from __future__ import annotations

import io
import zipfile
from datetime import UTC, datetime
from pathlib import Path
from types import SimpleNamespace

import pandas as pd
import pytest

from fantasy_draft_ai.config import (
    AppConfig,
    NetworkSection,
    PathSection,
    ProjectSection,
    TrainingSection,
)
from fantasy_draft_ai.data.manifests import RawArchive
from fantasy_draft_ai.data.warehouse import Warehouse
from fantasy_draft_ai.services import data_center
from fantasy_draft_ai.services.data_center import (
    load_data_center,
    run_safe_data_action,
    validate_data_action_request,
)
from fantasy_draft_ai.ui.pages.data_center import _template_bundle_bytes


def _config(tmp_path: Path) -> AppConfig:
    return AppConfig(
        project=ProjectSection(name="test", prediction_season=2026, random_seed=42),
        paths=PathSection(
            data_dir=Path("data"),
            raw_dir=Path("data/raw"),
            processed_dir=Path("data/processed"),
            warehouse=Path("data/warehouse.duckdb"),
            manifests=Path("data/raw/manifests"),
        ),
        network=NetworkSection(timeout_seconds=30, user_agent="tests"),
        training=TrainingSection(start_season=2016, end_season=2025),
        project_root=tmp_path,
    )


def test_data_center_inventory_is_verified_and_truthful(tmp_path: Path) -> None:
    config = _config(tmp_path)
    warehouse = Warehouse(config.resolve(config.paths.warehouse))
    warehouse.initialize()
    with warehouse.connect() as connection:
        connection.execute(
            """
            INSERT INTO players (
                player_id, display_name, canonical_position,
                mapping_confidence, mapping_source
            ) VALUES ('player-1', 'Test Player', 'WR', 'high', 'test')
            """
        )
    archive = RawArchive(
        tmp_path,
        config.resolve(config.paths.raw_dir),
        config.resolve(config.paths.manifests),
    )
    raw_path, acquired = archive.write_bytes(
        "nflverse",
        "players",
        ".parquet",
        b"immutable-test",
        datetime(2026, 8, 6, 12, tzinfo=UTC),
    )
    archive.create_manifest(
        source="nflverse",
        acquisition_method="test",
        acquired_at=acquired,
        raw_files=[raw_path],
        seasons=[2025],
    )

    snapshot = load_data_center(config)

    assert snapshot.quality.passed
    assert snapshot.quality.verified_files == 1
    assert snapshot.manifests[0].valid
    assert snapshot.sources[0].fully_verified
    assert snapshot.sources[0].seasons == (2025,)
    assert snapshot.warehouse.table_count("players") == 1
    assert snapshot.warehouse.total_rows >= 1
    assert snapshot.action("audit") is not None
    assert snapshot.action("audit").safe_in_app  # type: ignore[union-attr]
    assert snapshot.action("sleeper_import") is not None
    assert not snapshot.action("sleeper_import").available  # type: ignore[union-attr]
    assert snapshot.action("league_history_import").safe_in_app  # type: ignore[union-attr]


def test_data_center_surfaces_invalid_manifest_without_fabricating_source(
    tmp_path: Path,
) -> None:
    config = _config(tmp_path)
    manifests = config.resolve(config.paths.manifests)
    manifests.mkdir(parents=True)
    (manifests / "broken.json").write_text("{not-json", encoding="utf-8")

    snapshot = load_data_center(config)

    assert not snapshot.quality.passed
    assert snapshot.manifests[0].source == "invalid_manifest"
    assert not snapshot.manifests[0].valid
    assert snapshot.manifests[0].issues
    assert not snapshot.warehouse.exists
    assert not snapshot.warehouse.readable


def test_data_center_does_not_pass_canonical_audit_without_warehouse(
    tmp_path: Path,
) -> None:
    config = _config(tmp_path)

    snapshot = load_data_center(config)
    request = validate_data_action_request(config, "audit")
    result = run_safe_data_action(config, request)

    assert not snapshot.quality.passed
    assert "not initialized" in snapshot.quality.failures[0]
    assert not result.succeeded


def test_data_action_validation_rejects_unsupported_and_unsafe_parameters(
    tmp_path: Path,
) -> None:
    config = _config(tmp_path)

    with pytest.raises(ValueError, match="unavailable"):
        validate_data_action_request(config, "sleeper_import")
    with pytest.raises(ValueError, match="ordered"):
        validate_data_action_request(
            config,
            "download_nflverse",
            {"start_season": 2025, "end_season": 2020},
        )
    with pytest.raises(ValueError, match="Unsupported FFC format"):
        validate_data_action_request(
            config,
            "snapshot_ffc_adp",
            {"season": 2026, "scoring_format": "made-up", "teams": 12},
        )


def test_safe_archive_actions_dispatch_to_existing_package_apis(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    config = _config(tmp_path)
    artifacts = tmp_path / "artifacts"
    artifacts.mkdir()
    players = artifacts / "players.parquet"
    stats = artifacts / "stats.parquet"
    ffc = artifacts / "ffc.json"
    manifest = artifacts / "manifest.json"
    for path in (players, stats, ffc, manifest):
        path.write_text("test", encoding="utf-8")
    nfl_calls: list[tuple[int, int, bool]] = []
    ffc_calls: list[tuple[int, str, int, str | None, bool]] = []

    def fake_download(
        _config: AppConfig, *, start_season: int, end_season: int, offline: bool
    ) -> SimpleNamespace:
        nfl_calls.append((start_season, end_season, offline))
        return SimpleNamespace(
            player_path=players,
            stats_path=stats,
            manifest_path=manifest,
            reused_offline=offline,
        )

    def fake_snapshot(
        _config: AppConfig,
        *,
        season: int,
        scoring_format: str,
        teams: int,
        position: str | None,
        offline: bool,
    ) -> SimpleNamespace:
        ffc_calls.append((season, scoring_format, teams, position, offline))
        return SimpleNamespace(
            normalized=pd.DataFrame([{"player": "one"}]),
            raw_path=ffc,
            manifest_path=manifest,
            reused_offline=offline,
        )

    monkeypatch.setattr(data_center, "download_nflverse", fake_download)
    monkeypatch.setattr(data_center, "snapshot_ffc_adp", fake_snapshot)

    nfl_request = validate_data_action_request(
        config,
        "download_nflverse",
        {"start_season": 2020, "end_season": 2025, "offline": True},
    )
    nfl_result = run_safe_data_action(config, nfl_request)
    ffc_request = validate_data_action_request(
        config,
        "snapshot_ffc_adp",
        {
            "season": 2026,
            "scoring_format": "PPR",
            "teams": 12,
            "position": "wr",
            "offline": False,
        },
    )
    ffc_result = run_safe_data_action(config, ffc_request)

    assert nfl_result.succeeded
    assert nfl_result.reused_offline
    assert nfl_calls == [(2020, 2025, True)]
    assert ffc_result.succeeded
    assert ffc_result.records == 1
    assert ffc_calls == [(2026, "ppr", 12, "WR", False)]


def test_espn_action_validates_path_and_uses_import_service(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    config = _config(tmp_path)
    csv_path = tmp_path / "espn.csv"
    csv_path.write_text("header\nvalue\n", encoding="utf-8")
    archived = tmp_path / "archived.csv"
    manifest = tmp_path / "manifest.json"

    class FakeReport:
        has_fatal_errors = False
        row_count = 1

        @staticmethod
        def render() -> str:
            return "Data quality report: PASSED"

    def fake_import(_config: AppConfig, path: Path) -> SimpleNamespace:
        assert path == csv_path.resolve()
        return SimpleNamespace(
            report=FakeReport(),
            raw_path=archived,
            manifest_path=manifest,
        )

    monkeypatch.setattr(data_center, "import_espn_adp", fake_import)
    request = validate_data_action_request(config, "import_espn_csv", {"path": csv_path})
    result = run_safe_data_action(config, request)

    assert request.safe_in_app
    assert result.succeeded
    assert result.records == 1
    assert result.artifact_paths == (str(archived), str(manifest))


def test_initialize_warehouse_action_is_idempotent(tmp_path: Path) -> None:
    config = _config(tmp_path)
    request = validate_data_action_request(config, "initialize_warehouse")

    first = run_safe_data_action(config, request)
    second = run_safe_data_action(config, request)

    assert first.succeeded and second.succeeded
    assert config.resolve(config.paths.warehouse).is_file()


def test_invalid_league_history_zip_is_archived_but_not_normalized(tmp_path: Path) -> None:
    config = _config(tmp_path)
    source = tmp_path / "private-history.zip"
    content = b"not unpacked and not modeled"
    source.write_bytes(content)

    request = validate_data_action_request(
        config,
        "league_history_import",
        {"path": source},
    )
    result = run_safe_data_action(config, request)

    assert not result.succeeded
    assert "validation_failed" in result.message
    assert Path(result.artifact_paths[0]).read_bytes() == content
    assert source.read_bytes() == content
    snapshot = load_data_center(config)
    assert snapshot.quality.passed
    assert snapshot.warehouse.table_count("league_history_imports") == 1
    assert snapshot.warehouse.table_count("league_rules") == 0
    assert snapshot.warehouse.table_count("draft_picks") == 0
    assert snapshot.warehouse.table_count("team_outcomes") == 0
    history = next(item for item in snapshot.sources if item.source == "league_history")
    assert history.fully_verified


def test_history_template_download_contains_only_importable_root_files(tmp_path: Path) -> None:
    template = tmp_path / "template"
    template.mkdir()
    (template / "package.json").write_text("{}", encoding="utf-8")
    (template / "league_rules.csv").write_text("header\n", encoding="utf-8")
    (template / "README.md").write_text("instructions", encoding="utf-8")

    payload = _template_bundle_bytes(template)

    with zipfile.ZipFile(io.BytesIO(payload)) as package:
        assert package.namelist() == ["league_rules.csv", "package.json"]
