from pathlib import Path

import duckdb
import pytest

from fantasy_draft_ai.data.warehouse import Warehouse, invalidate_player_projection_runs


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
        "player_projection_runs": 0,
        "player_projection_models": 0,
        "player_projection_predictions": 0,
        "player_projection_champions": 0,
        "player_projection_evaluation_metadata": 0,
        "player_projection_board": 0,
        "adp_snapshots": 0,
        "adp_snapshot_metadata": 0,
        "adp_movement_features": 0,
        "adp_movement_forecasts": 0,
        "adp_availability_parameters": 0,
        "adp_phase5_builds": 0,
        "league_rules": 0,
        "draft_picks": 0,
        "draft_sessions": 0,
        "draft_session_players": 0,
        "draft_events": 0,
        "draft_recommendation_runs": 0,
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

    expected_projection_columns = {
        "player_projection_runs": {
            "run_id",
            "feature_data_fingerprint",
            "target_data_fingerprint",
            "build_fingerprint",
            "scoring_ruleset_fingerprint",
            "baseline_report_fingerprint",
            "model_feature_fingerprint",
            "model_config_fingerprint",
            "split_seasons",
            "training_rows",
            "status",
            "trained_at",
            "run_payload",
        },
        "player_projection_models": {
            "model_id",
            "run_id",
            "model_family",
            "target_name",
            "position",
            "training_seasons",
            "training_rows",
            "feature_names",
            "categorical_feature_names",
            "hyperparameters",
            "uncertainty_method",
            "artifact_path",
            "artifact_sha256",
            "artifact_size_bytes",
            "model_card_path",
            "model_card_sha256",
            "package_versions",
        },
        "player_projection_predictions": {
            "run_id",
            "player_id",
            "prediction_season",
            "position",
            "target_name",
            "model_family",
            "prediction_scope",
            "fold_label",
            "training_max_season",
            "predicted_value",
            "p10",
            "p50",
            "p90",
            "actual_value",
            "actual_games_active",
            "experience",
            "experience_group",
            "feature_data_fingerprint",
            "target_data_fingerprint",
            "build_fingerprint",
            "scoring_ruleset_fingerprint",
            "baseline_report_fingerprint",
            "model_feature_fingerprint",
            "model_config_fingerprint",
        },
        "player_projection_champions": {
            "run_id",
            "target_name",
            "position",
            "selected_source",
            "selected_name",
            "model_id",
            "selection_metric",
            "selection_value",
            "reference_baseline_name",
            "reference_baseline_value",
            "improvement",
            "selection_payload",
        },
        "player_projection_evaluation_metadata": {
            "report_fingerprint",
            "run_id",
            "feature_data_fingerprint",
            "target_data_fingerprint",
            "build_fingerprint",
            "scoring_ruleset_fingerprint",
            "baseline_report_fingerprint",
            "model_feature_fingerprint",
            "model_config_fingerprint",
            "prediction_rows",
            "evaluated_rows",
            "live_prediction_rows",
            "candidate_rows",
            "champion_rows",
            "report_payload",
        },
        "player_projection_board": {
            "run_id",
            "player_id",
            "prediction_season",
            "position",
            "fantasy_points_per_game_p10",
            "fantasy_points_per_game_p50",
            "fantasy_points_per_game_p90",
            "fantasy_points_per_game_selected_source",
            "fantasy_points_per_game_selected_name",
            "games_active_p10",
            "games_active_p50",
            "games_active_p90",
            "games_active_selected_source",
            "games_active_selected_name",
            "fantasy_points_total_p10",
            "fantasy_points_total_p50",
            "fantasy_points_total_p90",
            "fantasy_points_total_selected_source",
            "fantasy_points_total_selected_name",
            "prediction_status",
            "explanation_payload",
            "feature_data_fingerprint",
            "target_data_fingerprint",
            "build_fingerprint",
            "scoring_ruleset_fingerprint",
            "baseline_report_fingerprint",
            "model_feature_fingerprint",
            "model_config_fingerprint",
            "evaluation_report_fingerprint",
        },
    }
    with warehouse.connect(read_only=True) as connection:
        for table, expected_columns in expected_projection_columns.items():
            actual_columns = {
                row[1] for row in connection.execute(f"PRAGMA table_info('{table}')").fetchall()
            }
            assert expected_columns <= actual_columns


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


def test_player_projection_invalidation_preserves_only_the_current_contract(
    tmp_path: Path,
) -> None:
    warehouse = Warehouse(tmp_path / "projection-invalidation.duckdb")
    warehouse.initialize()
    with warehouse.connect() as connection:
        for run_id, build, baseline in (
            ("current", "build-current", "baseline-current"),
            ("stale-build", "build-old", "baseline-current"),
            ("stale-baseline", "build-current", "baseline-old"),
        ):
            connection.execute(
                """
                INSERT INTO player_projection_runs VALUES (
                    ?, 'feature', 'target', ?, 'scoring', ?, 'model-feature',
                    'model-config', '[]', 1, 1, 1, 0, 0, 0, 0, 0, 0,
                    'complete', current_timestamp, '{}'
                )
                """,
                [run_id, build, baseline],
            )

        removed = invalidate_player_projection_runs(
            connection,
            build_fingerprint="build-current",
            baseline_report_fingerprint="baseline-current",
        )

        assert removed == 2
        assert connection.execute("SELECT run_id FROM player_projection_runs").fetchall() == [
            ("current",)
        ]
