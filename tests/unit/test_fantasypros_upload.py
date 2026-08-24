from __future__ import annotations

from dataclasses import replace
from datetime import UTC, datetime
from pathlib import Path

import pytest

from fantasy_draft_ai.config import (
    AppConfig,
    NetworkSection,
    PathSection,
    ProjectSection,
    TrainingSection,
)
from fantasy_draft_ai.data.fantasypros_upload import (
    FantasyProsUploadValidationError,
    commit_fantasypros_adp_upload,
    preview_fantasypros_adp_upload,
)

CAPTURED_AT = datetime(2026, 8, 24, 18, 30, tzinfo=UTC)


def _config(project_root: Path) -> AppConfig:
    return AppConfig(
        project=ProjectSection(name="FantasyPros upload unit test", prediction_season=2026),
        paths=PathSection(
            data_dir=Path("data"),
            raw_dir=Path("data/raw"),
            processed_dir=Path("data/processed"),
            warehouse=Path("data/warehouse/test.duckdb"),
            manifests=Path("data/raw/manifests"),
        ),
        network=NetworkSection(timeout_seconds=5, user_agent="fantasypros-upload-test"),
        training=TrainingSection(start_season=2025, end_season=2025),
        project_root=project_root,
    )


def test_preview_recognizes_export_and_parses_identity_conservatively(tmp_path: Path) -> None:
    content = (
        b"Rank,Player (Bye),POS,Yahoo,Sleeper,RTSports,AVG,Real-Time\r\n"
        b"1,Jahmyr Gibbs   DET (6),RB1,1,1,1,1.0,1\r\n"
        b"2,Denver Broncos DST   (12),DST1,2,,3,2.5,2\r\n"
        b"3,Tyreek Hill,WR2,,4,,4.0,3\r\n"
    )

    preview = preview_fantasypros_adp_upload(
        _config(tmp_path),
        content,
        file_name="FantasyPros_2026_Overall_ADP_Rankings.csv",
        captured_at=CAPTURED_AT,
    )

    assert preview.input_rows == 3
    assert preview.source_row_counts == (
        ("yahoo", 2),
        ("sleeper", 2),
        ("rtsports", 2),
        ("fantasypros", 3),
    )
    assert preview.rows[0].player_name == "Jahmyr Gibbs"
    assert preview.rows[0].position == "RB"
    assert preview.rows[0].nfl_team == "DET"
    assert preview.rows[0].bye_week == 6
    assert preview.rows[1].player_name == "Denver Broncos DST"
    assert preview.rows[1].position == "DST"
    assert preview.rows[1].nfl_team is None
    assert preview.rows[1].bye_week == 12
    assert preview.rows[2].player_name == "Tyreek Hill"
    assert preview.rows[2].nfl_team is None
    assert preview.rows[2].bye_week is None
    assert not tmp_path.joinpath("data").exists()


def test_preview_requires_exact_fantasypros_headers(tmp_path: Path) -> None:
    content = b"Rank,Player,POS,Yahoo,Sleeper,RTSports,AVG\n1,A Player,RB1,1,1,1,1\n"

    with pytest.raises(FantasyProsUploadValidationError, match=r"Player \(Bye\)"):
        preview_fantasypros_adp_upload(
            _config(tmp_path),
            content,
            file_name="not-the-export.csv",
            captured_at=CAPTURED_AT,
        )


@pytest.mark.parametrize(
    ("player_value", "position", "message"),
    [
        ("Jahmyr Gibbs DET (6)", "RB1", "unrecognized Player"),
        ("Jahmyr Gibbs   DET (6)", "FLEX1", "invalid FantasyPros POS"),
        ("Jahmyr Gibbs   XYZ (6)", "RB1", "unknown NFL team"),
    ],
)
def test_preview_rejects_ambiguous_identity_fields(
    tmp_path: Path,
    player_value: str,
    position: str,
    message: str,
) -> None:
    content = (
        "Rank,Player (Bye),POS,Yahoo,Sleeper,RTSports,AVG\n"
        f"1,{player_value},{position},1,1,1,1\n"
    ).encode()

    with pytest.raises(FantasyProsUploadValidationError, match=message):
        preview_fantasypros_adp_upload(
            _config(tmp_path),
            content,
            file_name="fantasypros.csv",
            captured_at=CAPTURED_AT,
        )


def test_commit_rejects_changed_preview_fingerprint(tmp_path: Path) -> None:
    content = (
        b"Rank,Player (Bye),POS,Yahoo,Sleeper,RTSports,AVG\n"
        b"1,Jahmyr Gibbs   DET (6),RB1,1,1,1,1\n"
    )
    preview = preview_fantasypros_adp_upload(
        _config(tmp_path),
        content,
        file_name="fantasypros.csv",
        captured_at=CAPTURED_AT,
    )

    with pytest.raises(FantasyProsUploadValidationError, match="stale"):
        commit_fantasypros_adp_upload(
            _config(tmp_path),
            replace(preview, upload_fingerprint="0" * 64),
        )

    assert not tmp_path.joinpath("data").exists()
