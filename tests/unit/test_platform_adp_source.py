from __future__ import annotations

import json
import sys
from datetime import UTC, datetime
from pathlib import Path
from types import SimpleNamespace
from typing import Any

import httpx
import pandas as pd
import pytest

from fantasy_draft_ai.config import (
    AppConfig,
    NetworkSection,
    PathSection,
    ProjectSection,
    TrainingSection,
)
from fantasy_draft_ai.data.sources import platform_adp


def _config(project_root: Path) -> AppConfig:
    return AppConfig(
        project=ProjectSection(name="Platform ADP unit test", prediction_season=2026),
        paths=PathSection(
            data_dir=Path("data"),
            raw_dir=Path("data/raw"),
            processed_dir=Path("data/processed"),
            warehouse=Path("data/warehouse/test.duckdb"),
            manifests=Path("data/raw/manifests"),
        ),
        network=NetworkSection(timeout_seconds=5, user_agent="platform-adp-test"),
        training=TrainingSection(start_season=2025, end_season=2025),
        project_root=project_root,
    )


def _sleeper_payload(count: int = 100) -> bytes:
    rows = [
        {
            "player_id": str(10_000 + index),
            "player": {
                "first_name": f"Player{index}",
                "last_name": "Test",
                "position": ("QB", "RB", "WR", "TE")[index % 4],
                "team": "BUF",
            },
            "stats": {"adp_ppr": float(index + 1)},
        }
        for index in range(count)
    ]
    return json.dumps(rows, separators=(",", ":")).encode("utf-8")


def test_sleeper_snapshot_preserves_exact_response_and_reuses_offline(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    config = _config(tmp_path)
    content = _sleeper_payload()
    calls: list[dict[str, Any]] = []

    def fake_get(url: str, **kwargs: Any) -> httpx.Response:
        calls.append({"url": url, **kwargs})
        request = httpx.Request("GET", url)
        return httpx.Response(200, content=content, request=request)

    monkeypatch.setattr(platform_adp.httpx, "get", fake_get)
    result = platform_adp.snapshot_sleeper_adp(config, season=2026)

    assert result.raw_path.read_bytes() == content
    assert result.usable_count == 100
    assert not result.reused_offline
    assert result.manifest.source == "sleeper"
    assert result.manifest.acquisition_method == "unsupported-public-projections-endpoint"
    assert "personal noncommercial research" in result.manifest.notes
    assert result.manifest_path.is_file()
    assert calls[0]["url"].endswith("/2026")
    assert calls[0]["params"].get("order_by") == "adp_ppr"

    def fail_get(*_args: object, **_kwargs: object) -> httpx.Response:
        raise AssertionError("offline reuse must not make an HTTP request")

    monkeypatch.setattr(platform_adp.httpx, "get", fail_get)
    reused = platform_adp.snapshot_sleeper_adp(config, season=2026, offline=True)

    assert reused.raw_path == result.raw_path
    assert reused.raw_path.read_bytes() == content
    assert reused.manifest_path == result.manifest_path
    assert reused.captured_at == result.captured_at
    assert reused.usable_count == 100
    assert reused.reused_offline


def test_sleeper_rejects_wrong_shape_or_incomplete_adp_before_archiving(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    config = _config(tmp_path)
    responses = [b'{"players":[]}', _sleeper_payload(99)]

    def fake_get(url: str, **_kwargs: object) -> httpx.Response:
        request = httpx.Request("GET", url)
        return httpx.Response(200, content=responses.pop(0), request=request)

    monkeypatch.setattr(platform_adp.httpx, "get", fake_get)
    with pytest.raises(ValueError, match="JSON list"):
        platform_adp.snapshot_sleeper_adp(config)
    with pytest.raises(ValueError, match="only 99 usable"):
        platform_adp.snapshot_sleeper_adp(config)

    raw_root = config.resolve(config.paths.raw_dir)
    assert not list(raw_root.rglob("*.json"))


@pytest.mark.parametrize("source", ["espn", "yahoo", "underdog"])
def test_manual_platform_csv_is_validated_and_preserved_byte_for_byte(
    source: str, tmp_path: Path
) -> None:
    config = _config(tmp_path)
    source_path = tmp_path / f"{source}.csv"
    content = (
        "captured_at,season,source,scoring_format,team_count,source_player_id,"
        "player_name,position,nfl_team,average_pick,rank\r\n"
        f"2026-08-24T15:30:00-04:00,2026,{source},ppr,12,{source}-101,"
        "Example Player,WR,BUF,23.5,24\r\n"
    ).encode()
    source_path.write_bytes(content)

    result = platform_adp.import_manual_platform_adp(config, source_path, source=source)

    assert result.source == source
    assert result.raw_path.read_bytes() == content
    assert result.usable_count == 1
    assert result.captured_at == datetime(2026, 8, 24, 19, 30, tzinfo=UTC)
    assert result.manifest.source == source
    assert result.manifest.acquisition_method == f"manual-official-{source}-csv"
    assert "CSV bytes were retained unchanged" in result.manifest.notes
    assert result.manifest_path.is_file()


def test_manual_platform_csv_rejects_wrong_source_and_duplicate_stable_ids(
    tmp_path: Path,
) -> None:
    config = _config(tmp_path)
    source_path = tmp_path / "bad.csv"
    header = (
        "captured_at,season,source,scoring_format,team_count,source_player_id,"
        "player_name,position,nfl_team,average_pick,rank\n"
    )
    source_path.write_text(
        header + "2026-08-24T19:30:00Z,2026,yahoo,ppr,12,1,One Player,RB,BUF,1,1\n",
        encoding="utf-8",
    )
    with pytest.raises(ValueError, match="does not match"):
        platform_adp.import_manual_platform_adp(config, source_path, source="espn")

    source_path.write_text(
        header
        + "2026-08-24T19:30:00Z,2026,espn,ppr,12,1,One Player,RB,BUF,1,1\n"
        + "2026-08-24T19:30:00Z,2026,espn,ppr,12,1,Two Player,WR,BUF,2,2\n",
        encoding="utf-8",
    )
    with pytest.raises(ValueError, match="duplicate source_player_id"):
        platform_adp.import_manual_platform_adp(config, source_path, source="espn")

    assert not list(config.resolve(config.paths.raw_dir).rglob("*.csv"))


class _FakePolarsFrame:
    def __init__(self, frame: pd.DataFrame) -> None:
        self._frame = frame
        self.columns = list(frame.columns)
        self.height = len(frame)

    def write_parquet(self, path: Path) -> None:
        self._frame.to_parquet(path, index=False)


def test_nflverse_ff_playerids_snapshot_and_offline_reuse(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    config = _config(tmp_path)
    frame = pd.DataFrame(
        {
            "gsis_id": [f"gsis-{index}" for index in range(100)],
            "espn_id": [f"espn-{index}" for index in range(100)],
            "sleeper_id": [f"sleeper-{index}" for index in range(100)],
            "yahoo_id": [f"yahoo-{index}" for index in range(100)],
            "height": [72 for _ in range(100)],
        }
    )
    calls: list[str] = []

    def load_ff_playerids() -> _FakePolarsFrame:
        calls.append("called")
        return _FakePolarsFrame(frame)

    fake_module = SimpleNamespace(load_ff_playerids=load_ff_playerids)
    monkeypatch.setitem(sys.modules, "nflreadpy", fake_module)

    result = platform_adp.snapshot_nflverse_ff_playerids(config)

    assert result.raw_path.is_file()
    assert result.row_count == 100
    assert result.manifest.source == "nflverse_ff_playerids"
    assert result.manifest.acquisition_method == "nflreadpy.load_ff_playerids"
    assert result.manifest_path.is_file()
    assert calls == ["called"]

    def fail_load() -> _FakePolarsFrame:
        raise AssertionError("offline reuse must not call nflreadpy")

    monkeypatch.setitem(sys.modules, "nflreadpy", SimpleNamespace(load_ff_playerids=fail_load))
    reused = platform_adp.snapshot_nflverse_ff_playerids(config, offline=True)

    assert reused.raw_path == result.raw_path
    assert reused.manifest_path == result.manifest_path
    assert reused.captured_at == result.captured_at
    assert reused.row_count == 100
    assert reused.reused_offline
