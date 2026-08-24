from __future__ import annotations

import json
from datetime import UTC, datetime
from pathlib import Path

from fantasy_draft_ai.config import (
    AppConfig,
    NetworkSection,
    PathSection,
    ProjectSection,
    TrainingSection,
)
from fantasy_draft_ai.data.fantasypros_upload import import_fantasypros_adp_upload
from fantasy_draft_ai.data.warehouse import Warehouse

CAPTURED_AT = datetime(2026, 8, 24, 19, 0, tzinfo=UTC)


def _config(project_root: Path) -> AppConfig:
    return AppConfig(
        project=ProjectSection(
            name="FantasyPros upload integration test",
            prediction_season=2026,
        ),
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


def _initialize_players(config: AppConfig) -> None:
    warehouse = Warehouse(config.resolve(config.paths.warehouse))
    warehouse.initialize()
    with warehouse.connect() as connection:
        connection.executemany(
            """
            INSERT INTO players (
                player_id, display_name, canonical_position, nfl_team, is_active,
                mapping_confidence, mapping_source
            ) VALUES (?, ?, ?, ?, true, 'exact', 'test')
            """,
            [
                ("canonical-gibbs", "Jahmyr Gibbs", "RB", "DET"),
                ("canonical-denver", "Denver Broncos DST", "DST", None),
            ],
        )


def test_import_archives_once_and_loads_all_sources_transactionally(
    tmp_path: Path,
) -> None:
    config = _config(tmp_path)
    _initialize_players(config)
    content = (
        b"Rank,Player (Bye),POS,Yahoo,Sleeper,RTSports,AVG,Real-Time\r\n"
        b"1,Jahmyr Gibbs   DET (6),RB1,1,1,1,1.0,1\r\n"
        b"2,Denver Broncos DST   (12),DST1,2,,3,2.5,2\r\n"
        b"3,Mystery Prospect   SEA (8),WR1,,4,5,4.5,3\r\n"
    )

    first = import_fantasypros_adp_upload(
        config,
        content,
        file_name="FantasyPros_2026_Overall_ADP_Rankings.csv",
        captured_at=CAPTURED_AT,
    )
    second = import_fantasypros_adp_upload(
        config,
        content,
        file_name="FantasyPros_2026_Overall_ADP_Rankings.csv",
        captured_at=CAPTURED_AT,
    )

    assert first.committed
    assert not first.reused_archive
    assert first.original_raw_path.read_bytes() == content
    assert first.original_manifest.source == "fantasypros_aggregate_upload"
    assert first.original_manifest.sha256 == [first.preview.raw_sha256]
    assert [artifact.source for artifact in first.normalized_artifacts] == [
        "yahoo",
        "sleeper",
        "rtsports",
        "fantasypros",
    ]
    for artifact in first.normalized_artifacts:
        notes = json.loads(artifact.manifest.notes)
        assert artifact.manifest.source == artifact.source
        assert notes["original_dataset_id"] == first.original_manifest.dataset_id
        assert notes["original_raw_sha256"] == first.preview.raw_sha256
        assert notes["scope"]["scoring_format"] == "overall"
    summary_counts = [
        (summary.source, summary.rows, summary.mapped, summary.unresolved)
        for summary in first.source_summaries
    ]
    assert summary_counts == [
        ("yahoo", 2, 2, 0),
        ("sleeper", 2, 1, 1),
        ("rtsports", 3, 2, 1),
        ("fantasypros", 3, 2, 1),
    ]

    assert second.committed
    assert second.reused_archive
    assert second.original_raw_path == first.original_raw_path
    assert second.load.inserted_rows == 0
    assert second.load.matched_existing_rows == 10
    assert len(list(config.resolve(config.paths.manifests).glob("*.json"))) == 5
    assert len(list(config.resolve(config.paths.raw_dir).rglob("*.csv"))) == 5

    warehouse = Warehouse(config.resolve(config.paths.warehouse))
    with warehouse.connect(read_only=True) as connection:
        scopes = connection.execute(
            """
            SELECT source, scoring_format, team_count, position_scope, row_count
            FROM adp_snapshot_metadata
            ORDER BY source
            """
        ).fetchall()
        observation_count = connection.execute(
            "SELECT count(*) FROM adp_snapshots"
        ).fetchone()
    assert scopes == [
        ("fantasypros", "overall", 12, "overall", 3),
        ("rtsports", "overall", 12, "overall", 3),
        ("sleeper", "overall", 12, "overall", 2),
        ("yahoo", "overall", 12, "overall", 2),
    ]
    assert observation_count == (10,)
