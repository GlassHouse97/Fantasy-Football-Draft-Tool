from __future__ import annotations

import shutil
from datetime import UTC, datetime
from pathlib import Path

import duckdb
import pytest

from fantasy_draft_ai.config import (
    AppConfig,
    NetworkSection,
    PathSection,
    ProjectSection,
    TrainingSection,
)
from fantasy_draft_ai.data.warehouse import Warehouse
from fantasy_draft_ai.models.adp.build import (
    adp_market_integrity_issues,
    build_adp_market_baselines,
)
from fantasy_draft_ai.services.adp_market import load_adp_market_board

PROJECT_ROOT = Path(__file__).resolve().parents[2]


def _config(tmp_path: Path) -> AppConfig:
    config_dir = tmp_path / "configs"
    config_dir.mkdir()
    shutil.copyfile(
        PROJECT_ROOT / "configs" / "adp_availability.yaml",
        config_dir / "adp_availability.yaml",
    )
    return AppConfig(
        project=ProjectSection(name="phase-5-test", prediction_season=2026),
        paths=PathSection(
            data_dir=Path("data"),
            raw_dir=Path("data/raw"),
            processed_dir=Path("data/processed"),
            warehouse=Path("data/warehouse/test.duckdb"),
            manifests=Path("data/raw/manifests"),
        ),
        network=NetworkSection(timeout_seconds=5, user_agent="phase-5-test"),
        training=TrainingSection(start_season=2020, end_season=2025),
        project_root=tmp_path,
    )


def _seed_market(config: AppConfig) -> None:
    warehouse = Warehouse(config.resolve(config.paths.warehouse))
    warehouse.initialize()
    captures = (
        ("snapshot-1", datetime(2026, 8, 1, tzinfo=UTC), 1),
        ("snapshot-2", datetime(2026, 8, 2, tzinfo=UTC), 1),
        ("snapshot-3", datetime(2026, 8, 4, tzinfo=UTC), 2),
    )
    with warehouse.connect() as connection:
        for index, (snapshot_id, captured_at, row_count) in enumerate(captures, start=1):
            connection.execute(
                """
                INSERT INTO adp_snapshot_metadata VALUES (
                    ?, 'ffc', ?, 2026, 'ppr', 12, 'overall', ?, ?, '["dataset"]', ?, ?
                )
                """,
                [
                    snapshot_id,
                    captured_at,
                    str(index) * 64,
                    f"data/raw/ffc/snapshot-{index}.json",
                    row_count,
                    captured_at,
                ],
            )
        for snapshot_id, captured_at, average_pick in (
            ("snapshot-1", captures[0][1], 10.0),
            ("snapshot-2", captures[1][1], 9.0),
            ("snapshot-3", captures[2][1], 7.0),
        ):
            connection.execute(
                """
                INSERT INTO adp_snapshots (
                    snapshot_id, source, captured_at, season, scoring_format, team_count,
                    player_id, player_name, position, nfl_team, average_pick, median_pick,
                    rank, min_pick, max_pick, sample_size, movement, source_stddev,
                    source_movement_horizon, raw_source_row_id, mapping_confidence
                ) VALUES (
                    ?, 'ffc', ?, 2026, 'ppr', 12, NULL, 'Cutoff Runner', 'RB', 'BUF',
                    ?, NULL, NULL, 5, 15, 100, NULL, 2, NULL, 'ffc-1', 'unresolved'
                )
                """,
                [snapshot_id, captured_at, average_pick],
            )
        connection.execute(
            """
            INSERT INTO adp_snapshots (
                snapshot_id, source, captured_at, season, scoring_format, team_count,
                player_id, player_name, position, nfl_team, average_pick, median_pick,
                rank, min_pick, max_pick, sample_size, movement, source_stddev,
                source_movement_horizon, raw_source_row_id, mapping_confidence
            ) VALUES (
                'snapshot-3', 'ffc', ?, 2026, 'ppr', 12, NULL, 'Fallback Receiver',
                'WR', 'MIA', 50, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL,
                'ffc-2', 'unresolved'
            )
            """,
            [captures[2][1]],
        )


def test_phase5_build_is_cutoff_safe_reusable_and_served_read_only(tmp_path: Path) -> None:
    config = _config(tmp_path)
    _seed_market(config)
    report_path = tmp_path / "docs" / "phase5.md"

    first = build_adp_market_baselines(
        config,
        availability_config_path=tmp_path / "configs" / "adp_availability.yaml",
        output_path=report_path,
    )
    second = build_adp_market_baselines(
        config,
        availability_config_path=tmp_path / "configs" / "adp_availability.yaml",
        output_path=report_path,
    )

    assert first.committed is True
    assert first.reused is False
    assert second.committed is False
    assert second.reused is True
    assert second.build_fingerprint == first.build_fingerprint
    assert first.snapshot_count == 3
    assert first.observation_rows == 4
    assert first.movement_feature_rows == 4
    assert first.movement_forecast_rows == 12
    assert first.availability_parameter_rows == 4
    assert first.report["persistence_ready_rows"] == 4
    assert first.report["linear_ready_rows"] == 1
    assert first.report["exponentially_weighted_ready_rows"] == 1
    assert first.report["availability_fallback_rows"] == 1
    assert report_path.is_file()
    assert report_path.with_suffix(".json").is_file()
    assert adp_market_integrity_issues(config) == []

    board = load_adp_market_board(config)
    assert board.available is True
    assert len(board.rows) == 2
    assert board.availability_config is not None
    runner = next(row for row in board.rows if row.player_name == "Cutoff Runner")
    assert runner.prior_average_pick == pytest.approx(9.0)
    assert runner.observation_count == 3
    assert runner.linear_status == "available"
    estimate = runner.estimate_availability(
        current_pick=1,
        next_pick=12,
        config=board.availability_config,
    )
    assert estimate.probability_available_at_next_pick == pytest.approx(
        1.0 - estimate.probability_selected_before_next_pick
    )
    fallback = next(row for row in board.rows if row.player_name == "Fallback Receiver")
    assert fallback.availability_evidence_method == "configured_fallback"
    assert fallback.availability_fallback_group == "WR:1-60"

    with duckdb.connect(str(config.resolve(config.paths.warehouse))) as connection:
        connection.execute(
            "UPDATE adp_snapshots SET average_pick = 51 WHERE raw_source_row_id = 'ffc-2'"
        )
    assert (
        "Phase 5 derived rows are stale for the canonical ADP inputs."
        in adp_market_integrity_issues(config)
    )
    with duckdb.connect(str(config.resolve(config.paths.warehouse))) as connection:
        connection.execute(
            "UPDATE adp_snapshots SET average_pick = 50 WHERE raw_source_row_id = 'ffc-2'"
        )
        connection.execute(
            "DELETE FROM adp_availability_parameters WHERE raw_source_row_id = 'ffc-2'"
        )
    assert "Phase 5 derived-table counts are stale or incomplete." in adp_market_integrity_issues(
        config
    )
