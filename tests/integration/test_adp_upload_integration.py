from __future__ import annotations

import json
from datetime import UTC, datetime, timedelta
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
    AdpUploadColumnMapping,
    commit_adp_upload,
    preview_adp_upload,
)
from fantasy_draft_ai.data.warehouse import Warehouse

CAPTURED_AT = datetime(2026, 8, 24, 17, 0, tzinfo=UTC)


def _config(project_root: Path) -> AppConfig:
    return AppConfig(
        project=ProjectSection(name="ADP upload integration test", prediction_season=2026),
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


def _initialize_player(config: AppConfig) -> None:
    warehouse = Warehouse(config.resolve(config.paths.warehouse))
    warehouse.initialize()
    with warehouse.connect() as connection:
        connection.execute(
            """
            INSERT INTO players (
                player_id, display_name, canonical_position, nfl_team,
                espn_id, yahoo_id, sleeper_id, is_active,
                mapping_confidence, mapping_source
            ) VALUES (
                'canonical-bijan', 'Bijan Robinson', 'RB', 'ATL',
                'espn-1', 'yahoo-1', 'sleeper-1', true, 'exact', 'test'
            )
            """
        )


@pytest.mark.parametrize(
    ("source", "source_id", "expected_confidence", "expected_format"),
    [
        ("espn", "espn-1", "exact", "ppr"),
        ("yahoo", "yahoo-1", "exact", "half_ppr"),
        ("sleeper", "sleeper-1", "exact", "ppr"),
        ("underdog", "underdog-1", "high", "half_ppr"),
    ],
)
def test_upload_archives_original_and_loads_each_platform_idempotently(
    tmp_path: Path,
    source: str,
    source_id: str,
    expected_confidence: str,
    expected_format: str,
) -> None:
    config = _config(tmp_path)
    _initialize_player(config)
    content = (
        "PLAYER NAME,ADP,POS,TEAM,PLAYER ID\r\n"
        f"Bijan Robinson,1.5,RB,ATL,{source_id}\r\n"
    ).encode()
    preview = preview_adp_upload(
        config,
        content,
        file_name=f"{source}-export.csv",
        source=source,
        columns=AdpUploadColumnMapping(
            "PLAYER NAME",
            "ADP",
            position="POS",
            nfl_team="TEAM",
            source_player_id="PLAYER ID",
        ),
        captured_at=CAPTURED_AT,
    )

    first = commit_adp_upload(config, preview)
    second = commit_adp_upload(config, preview)

    assert first.committed
    assert not first.reused_archive
    assert first.original_raw_path.read_bytes() == content
    assert first.original_manifest.source == "user_uploaded_adp"
    assert first.original_manifest.acquisition_method == (
        "user-uploaded-source-of-truth-csv-v1"
    )
    assert first.original_manifest.sha256 == [preview.raw_sha256]
    assert first.normalized_manifest.source == source
    assert first.normalized_manifest.acquisition_method == (
        "normalized-user-upload-source-of-truth-v1"
    )
    normalized_notes = json.loads(first.normalized_manifest.notes)
    assert normalized_notes["original_dataset_id"] == first.original_manifest.dataset_id
    assert normalized_notes["original_raw_sha256"] == preview.raw_sha256
    assert first.load.inserted_rows == 1
    assert first.mapping_confidence_counts == ((expected_confidence, 1),)
    assert second.committed
    assert second.reused_archive
    assert second.original_raw_path == first.original_raw_path
    assert second.normalized_raw_path == first.normalized_raw_path
    assert second.load.inserted_rows == 0
    assert second.load.matched_existing_rows == 1
    assert len(list(config.resolve(config.paths.manifests).glob("*.json"))) == 2
    assert len(list(config.resolve(config.paths.raw_dir).rglob("*.csv"))) == 2

    warehouse = Warehouse(config.resolve(config.paths.warehouse))
    with warehouse.connect(read_only=True) as connection:
        row = connection.execute(
            """
            SELECT source, captured_at, season, scoring_format, team_count,
                   player_id, player_name, position, nfl_team, average_pick,
                   mapping_confidence
            FROM adp_snapshots
            """
        ).fetchone()
    assert row == (
        source,
        CAPTURED_AT,
        2026,
        expected_format,
        12,
        "canonical-bijan",
        "Bijan Robinson",
        "RB",
        "ATL",
        1.5,
        expected_confidence,
    )


def test_newest_uploaded_exact_scope_snapshot_is_available_for_display(tmp_path: Path) -> None:
    config = _config(tmp_path)
    _initialize_player(config)
    columns = AdpUploadColumnMapping(
        "Player", "ADP", position="Position", source_player_id="ID"
    )
    older = preview_adp_upload(
        config,
        b"Player,ADP,Position,ID\nBijan Robinson,2.5,RB,espn-1\n",
        file_name="espn-old.csv",
        source="espn",
        columns=columns,
        captured_at=CAPTURED_AT,
    )
    newer = preview_adp_upload(
        config,
        b"Player,ADP,Position,ID\nBijan Robinson,1.25,RB,espn-1\n",
        file_name="espn-new.csv",
        source="espn",
        columns=columns,
        captured_at=CAPTURED_AT + timedelta(days=1),
    )

    first = commit_adp_upload(config, older)
    second = commit_adp_upload(config, newer)

    assert first.committed and second.committed
    warehouse = Warehouse(config.resolve(config.paths.warehouse))
    with warehouse.connect(read_only=True) as connection:
        latest = connection.execute(
            """
            SELECT metadata.snapshot_id, metadata.captured_at, snapshot.average_pick
            FROM adp_snapshot_metadata AS metadata
            JOIN adp_snapshots AS snapshot USING (snapshot_id)
            WHERE metadata.source = 'espn'
              AND metadata.season = 2026
              AND metadata.scoring_format = 'ppr'
              AND metadata.team_count = 12
              AND metadata.position_scope = 'overall'
            ORDER BY metadata.captured_at DESC, metadata.loaded_at DESC
            LIMIT 1
            """
        ).fetchone()
        snapshot_count = connection.execute(
            "SELECT count(*) FROM adp_snapshot_metadata WHERE source = 'espn'"
        ).fetchone()
    assert latest == (
        second.load.snapshots[0].snapshot_id,
        CAPTURED_AT + timedelta(days=1),
        1.25,
    )
    assert snapshot_count == (2,)
