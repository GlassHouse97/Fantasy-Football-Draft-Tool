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
from fantasy_draft_ai.data.adp_upload import (
    MAX_ADP_UPLOAD_BYTES,
    MAX_ADP_UPLOAD_DATA_ROWS,
    AdpUploadColumnMapping,
    AdpUploadValidationError,
    commit_adp_upload,
    detect_adp_upload_columns,
    inspect_adp_upload_csv,
    preview_adp_upload,
)
from fantasy_draft_ai.data.warehouse import Warehouse

CAPTURED_AT = datetime(2026, 8, 24, 16, 30, tzinfo=UTC)


def _config(project_root: Path) -> AppConfig:
    return AppConfig(
        project=ProjectSection(name="ADP upload unit test", prediction_season=2026),
        paths=PathSection(
            data_dir=Path("data"),
            raw_dir=Path("data/raw"),
            processed_dir=Path("data/processed"),
            warehouse=Path("data/warehouse/test.duckdb"),
            manifests=Path("data/raw/manifests"),
        ),
        network=NetworkSection(timeout_seconds=5, user_agent="adp-upload-test"),
        training=TrainingSection(start_season=2025, end_season=2025),
        project_root=project_root,
    )


def _initialize_players(
    config: AppConfig,
    rows: list[tuple[str, str, str, str, str | None]],
) -> None:
    warehouse = Warehouse(config.resolve(config.paths.warehouse))
    warehouse.initialize()
    with warehouse.connect() as connection:
        connection.executemany(
            """
            INSERT INTO players (
                player_id, display_name, canonical_position, nfl_team, espn_id,
                is_active, mapping_confidence, mapping_source
            ) VALUES (?, ?, ?, ?, ?, true, 'exact', 'test')
            """,
            rows,
        )


def test_inspection_and_conservative_column_detection() -> None:
    content = (
        b"PLAYER,AVG PICK,POS,TEAM,ESPN ID,Overall Rank,Notes\n"
        b"Bijan Robinson,1.2,RB,ATL,100,1,first\n"
    )

    inspection = inspect_adp_upload_csv(content)
    detection = detect_adp_upload_columns(content)

    assert inspection.columns == (
        "PLAYER",
        "AVG PICK",
        "POS",
        "TEAM",
        "ESPN ID",
        "Overall Rank",
        "Notes",
    )
    assert inspection.data_rows == 1
    assert inspection.sample_rows[0]["PLAYER"] == "Bijan Robinson"
    assert detection.ready
    assert detection.to_column_mapping() == AdpUploadColumnMapping(
        player_name="PLAYER",
        average_pick="AVG PICK",
        position="POS",
        nfl_team="TEAM",
        source_player_id="ESPN ID",
        rank="Overall Rank",
    )


def test_preview_normalizes_resolves_and_collapses_duplicate_identity(tmp_path: Path) -> None:
    config = _config(tmp_path)
    _initialize_players(
        config,
        [("canonical-bijan", "Bijan Robinson", "RB", "ATL", "100")],
    )
    content = (
        "Name,ADP,Position,Team,ID,Rank\n"
        "Biján Robinson Jr.,1.2,RB,Atlanta Falcons,100.0,1\n"
        "Bijan Robinson,1.2,,,100,2\n"
    ).encode()

    preview = preview_adp_upload(
        config,
        content,
        file_name="espn.csv",
        source="ESPN",
        columns=AdpUploadColumnMapping(
            player_name="Name",
            average_pick="ADP",
            position="Position",
            nfl_team="Team",
            source_player_id="ID",
            rank="Rank",
        ),
        captured_at=CAPTURED_AT,
    )

    assert preview.scope.source == "espn"
    assert preview.scope.season == 2026
    assert preview.scope.scoring_format == "ppr"
    assert preview.scope.team_count == 12
    assert preview.input_rows == 2
    assert preview.accepted_rows == 1
    assert preview.duplicates_collapsed == 1
    assert len(preview.upload_fingerprint) == 64
    assert preview.mapping_confidence_counts == (("exact", 1),)
    assert preview.rows[0].source_row_numbers == (2, 3)
    assert preview.rows[0].source_player_id == "100"
    assert preview.rows[0].player_name == "Bijan Robinson"
    assert preview.rows[0].position == "RB"
    assert preview.rows[0].nfl_team == "ATL"
    assert preview.rows[0].canonical_player_id == "canonical-bijan"
    assert not config.resolve(config.paths.raw_dir).exists()


def test_name_only_never_becomes_high_confidence_without_position_or_exact_id(
    tmp_path: Path,
) -> None:
    config = _config(tmp_path)
    _initialize_players(
        config,
        [("canonical-bijan", "Bijan Robinson", "RB", "ATL", "100")],
    )

    with pytest.raises(AdpUploadValidationError, match="has no position"):
        preview_adp_upload(
            config,
            b"Player,ADP\nBijan Robinson,1.2\n",
            file_name="espn.csv",
            source="espn",
            columns=AdpUploadColumnMapping("Player", "ADP"),
            captured_at=CAPTURED_AT,
        )

    exact = preview_adp_upload(
        config,
        b"Player,ADP,ID\nBijan Robinson,1.2,100\n",
        file_name="espn.csv",
        source="espn",
        columns=AdpUploadColumnMapping("Player", "ADP", source_player_id="ID"),
        captured_at=CAPTURED_AT,
    )
    unresolved = preview_adp_upload(
        config,
        b"Player,ADP,Pos\nUnknown Prospect,200,WR\n",
        file_name="espn.csv",
        source="espn",
        columns=AdpUploadColumnMapping("Player", "ADP", position="Pos"),
        captured_at=CAPTURED_AT,
    )

    assert exact.rows[0].position == "RB"
    assert exact.rows[0].mapping_confidence == "exact"
    assert unresolved.rows[0].position == "WR"
    assert unresolved.rows[0].canonical_player_id is None
    assert unresolved.rows[0].mapping_confidence == "unresolved"


def test_duplicate_blank_and_populated_team_collapses_to_populated_team(
    tmp_path: Path,
) -> None:
    config = _config(tmp_path)
    content = (
        b"Player,ADP,Pos,Team,ID\n"
        b"Jaxon Smith-Njigba,12.0,WR,,jsn\n"
        b"Jaxon Smith Njigba,12.0,WR,SEA,jsn\n"
    )

    preview = preview_adp_upload(
        config,
        content,
        file_name="espn.csv",
        source="espn",
        columns=AdpUploadColumnMapping(
            "Player",
            "ADP",
            position="Pos",
            nfl_team="Team",
            source_player_id="ID",
        ),
        captured_at=CAPTURED_AT,
    )

    assert preview.accepted_rows == 1
    assert preview.duplicates_collapsed == 1
    assert preview.rows[0].source_row_numbers == (2, 3)
    assert preview.rows[0].nfl_team == "SEA"


def test_duplicate_conflicting_teams_fail_closed(tmp_path: Path) -> None:
    config = _config(tmp_path)
    content = (
        b"Player,ADP,Pos,Team\n"
        b"Shared Player,25.0,WR,SEA\n"
        b"Shared Player,25.0,WR,MIA\n"
    )

    with pytest.raises(AdpUploadValidationError, match="conflicting teams"):
        preview_adp_upload(
            config,
            content,
            file_name="yahoo.csv",
            source="yahoo",
            columns=AdpUploadColumnMapping(
                "Player", "ADP", position="Pos", nfl_team="Team"
            ),
            captured_at=CAPTURED_AT,
        )


def test_csv_backend_limits_bytes_and_data_rows(tmp_path: Path) -> None:
    config = _config(tmp_path)
    oversized = b"Player,ADP,Pos\n" + b"x" * MAX_ADP_UPLOAD_BYTES
    too_many_rows = b"Player,ADP,Pos\n" + b"Unknown,25,WR\n" * (
        MAX_ADP_UPLOAD_DATA_ROWS + 1
    )

    with pytest.raises(AdpUploadValidationError, match="10 MB backend safety limit"):
        inspect_adp_upload_csv(oversized)
    with pytest.raises(AdpUploadValidationError, match="10,000 data-row"):
        preview_adp_upload(
            config,
            too_many_rows,
            file_name="espn.csv",
            source="espn",
            columns=AdpUploadColumnMapping("Player", "ADP", position="Pos"),
            captured_at=CAPTURED_AT,
        )


def test_preview_fails_closed_on_conflicting_duplicate_adp(tmp_path: Path) -> None:
    config = _config(tmp_path)
    content = (
        b"Player,ADP,Pos\n"
        b"Jaxon Smith-Njigba,12.0,WR\n"
        b"Jaxon Smith Njigba,14.0,WR\n"
    )

    with pytest.raises(AdpUploadValidationError, match="conflicting ADPs"):
        preview_adp_upload(
            config,
            content,
            file_name="espn.csv",
            source="espn",
            columns=AdpUploadColumnMapping("Player", "ADP", position="Pos"),
            captured_at=CAPTURED_AT,
        )

    assert not config.resolve(config.paths.raw_dir).exists()


def test_preview_fails_closed_on_ambiguous_canonical_identity(tmp_path: Path) -> None:
    config = _config(tmp_path)
    _initialize_players(
        config,
        [
            ("canonical-one", "Shared Player", "WR", "BUF", None),
            ("canonical-two", "Shared Player", "WR", "MIA", None),
        ],
    )
    content = b"Player,ADP,Pos\nShared Player,22.0,WR\n"

    with pytest.raises(AdpUploadValidationError, match="ambiguous"):
        preview_adp_upload(
            config,
            content,
            file_name="yahoo.csv",
            source="yahoo",
            columns=AdpUploadColumnMapping("Player", "ADP", position="Pos"),
            captured_at=CAPTURED_AT,
        )


def test_preview_rejects_unknown_source_or_reused_column(tmp_path: Path) -> None:
    config = _config(tmp_path)
    content = b"Player,ADP,Pos\nUnknown Player,25,WR\n"

    with pytest.raises(AdpUploadValidationError, match="one of"):
        preview_adp_upload(
            config,
            content,
            file_name="other.csv",
            source="other",
            columns=AdpUploadColumnMapping("Player", "ADP", position="Pos"),
            captured_at=CAPTURED_AT,
        )
    with pytest.raises(AdpUploadValidationError, match="only one field"):
        preview_adp_upload(
            config,
            content,
            file_name="espn.csv",
            source="espn",
            columns=AdpUploadColumnMapping("Player", "ADP", position="ADP"),
            captured_at=CAPTURED_AT,
        )


def test_commit_rejects_a_preview_with_a_changed_apply_fingerprint(tmp_path: Path) -> None:
    config = _config(tmp_path)
    preview = preview_adp_upload(
        config,
        b"Player,ADP,Pos\nUnknown Player,25,WR\n",
        file_name="espn.csv",
        source="espn",
        columns=AdpUploadColumnMapping("Player", "ADP", position="Pos"),
        captured_at=CAPTURED_AT,
    )

    with pytest.raises(AdpUploadValidationError, match="stale"):
        commit_adp_upload(
            config,
            replace(preview, upload_fingerprint="0" * 64),
        )

    assert not config.resolve(config.paths.raw_dir).exists()
