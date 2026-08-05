from pathlib import Path

import duckdb
import pytest

from fantasy_draft_ai.data.warehouse import Warehouse


def test_warehouse_initialization_is_idempotent(tmp_path: Path) -> None:
    warehouse = Warehouse(tmp_path / "fantasy.duckdb")
    warehouse.initialize()
    warehouse.initialize()
    assert warehouse.path.is_file()
    assert warehouse.table_counts() == {
        "players": 0,
        "player_week_stats": 0,
        "player_game_participation": 0,
        "player_source_mappings": 0,
        "identity_review_queue": 0,
        "player_season_features": 0,
        "player_season_targets": 0,
        "feature_build_metadata": 0,
        "baseline_predictions": 0,
        "baseline_evaluation_metadata": 0,
        "adp_snapshots": 0,
        "league_rules": 0,
        "draft_picks": 0,
        "team_outcomes": 0,
    }
    with warehouse.connect(read_only=True) as connection:
        columns = {
            row[1]
            for row in connection.execute("PRAGMA table_info('player_week_stats')").fetchall()
        }
    assert {
        "position",
        "season_type",
        "game_id",
        "source_dataset_id",
        "field_goals_made",
        "field_goals_attempted",
        "extra_points_made",
        "extra_points_attempted",
    } <= columns
    with warehouse.connect(read_only=True) as connection:
        player_columns = {
            row[1] for row in connection.execute("PRAGMA table_info('players')").fetchall()
        }
        participation_columns = {
            row[1]
            for row in connection.execute(
                "PRAGMA table_info('player_game_participation')"
            ).fetchall()
        }
    assert {
        "pfr_id",
        "rookie_season",
        "draft_year",
        "draft_round",
        "draft_pick",
        "draft_team",
        "height_inches",
        "weight_lbs",
        "identity_source_dataset_id",
        "identity_source_as_of",
    } <= player_columns
    assert {
        "season",
        "week",
        "game_id",
        "player_id",
        "season_type",
        "position",
        "nfl_team",
        "opponent",
        "offense_snaps",
        "defense_snaps",
        "special_teams_snaps",
        "source",
        "as_of",
        "source_dataset_id",
    } <= participation_columns
    with warehouse.connect(read_only=True) as connection:
        review_columns = {
            row[1]
            for row in connection.execute("PRAGMA table_info('identity_review_queue')").fetchall()
        }
    assert {
        "review_id",
        "source_player_id",
        "candidate_player_id",
        "mapping_confidence",
        "status",
        "resolution",
        "is_current",
    } <= review_columns


def test_legacy_duplicate_feature_keys_fail_with_actionable_migration_error(
    tmp_path: Path,
) -> None:
    path = tmp_path / "legacy.duckdb"
    with duckdb.connect(str(path)) as connection:
        connection.execute(
            "CREATE TABLE player_season_features "
            "(player_id VARCHAR, prediction_season INTEGER, source VARCHAR)"
        )
        connection.executemany(
            "INSERT INTO player_season_features VALUES ('p1', 2025, ?)",
            [("legacy-a",), ("legacy-b",)],
        )

    with pytest.raises(RuntimeError, match="duplicate player/prediction-season"):
        Warehouse(path).initialize()
