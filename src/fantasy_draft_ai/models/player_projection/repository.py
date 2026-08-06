"""Frozen Phase 3 inputs and transactional Phase 4 warehouse persistence."""

from __future__ import annotations

import hashlib
import json
from contextlib import AbstractContextManager, nullcontext
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import duckdb

from fantasy_draft_ai.config import AppConfig
from fantasy_draft_ai.data.manifests import sha256_file
from fantasy_draft_ai.data.warehouse import Warehouse
from fantasy_draft_ai.models.player_projection.config import canonical_json
from fantasy_draft_ai.models.player_projection.dataset import PlayerSeasonModelRow

_REQUIRED_BASELINES = {
    "previous_season",
    "weighted_history",
    "age_position_adjusted",
    "position_shrinkage",
    "weighted_components",
}
_REQUIRED_TARGETS = {
    "fantasy_points_per_game",
    "games_active",
    "fantasy_points_total",
}


@dataclass(frozen=True)
class FrozenProjectionContract:
    """Validated features, targets, baselines, and split labels for one run."""

    rows: tuple[PlayerSeasonModelRow, ...]
    feature_data_fingerprint: str
    target_data_fingerprint: str
    build_fingerprint: str
    scoring_ruleset_fingerprint: str
    baseline_report_fingerprint: str
    feature_rows: int
    target_rows: int
    folds: tuple[dict[str, Any], ...]
    baseline_report: dict[str, Any]

    @property
    def validation_seasons(self) -> tuple[int, ...]:
        return tuple(
            int(fold["evaluation_season"]) for fold in self.folds if fold["label"] == "validation"
        )

    @property
    def test_season(self) -> int:
        tests = [int(fold["evaluation_season"]) for fold in self.folds if fold["label"] == "test"]
        if len(tests) != 1:
            raise RuntimeError("The frozen comparison contract must contain exactly one test fold.")
        return tests[0]


RUN_COLUMNS = (
    "run_id",
    "feature_data_fingerprint",
    "target_data_fingerprint",
    "build_fingerprint",
    "scoring_ruleset_fingerprint",
    "baseline_report_fingerprint",
    "model_feature_fingerprint",
    "model_config_fingerprint",
    "split_seasons",
    "feature_rows",
    "target_rows",
    "training_rows",
    "prediction_rows",
    "evaluated_rows",
    "live_prediction_rows",
    "candidate_rows",
    "model_rows",
    "champion_rows",
    "status",
    "trained_at",
    "run_payload",
)
MODEL_COLUMNS = (
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
)
PREDICTION_COLUMNS = (
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
)
CHAMPION_COLUMNS = (
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
)
EVALUATION_COLUMNS = (
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
)
BOARD_COLUMNS = (
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
)


def read_frozen_projection_contract(
    config: AppConfig,
    *,
    scoring_ruleset_fingerprint: str,
    validation_start_season: int = 2020,
    test_season: int = 2025,
) -> FrozenProjectionContract:
    """Read and validate the exact Phase 3 contract without modifying raw data."""

    warehouse = Warehouse(config.resolve(config.paths.warehouse))
    if not warehouse.path.is_file():
        raise RuntimeError("The canonical warehouse does not exist.")
    warehouse.initialize()
    with warehouse.connect(read_only=True) as connection:
        metadata_rows = connection.execute(
            """
            SELECT data_fingerprint, target_data_fingerprint, build_fingerprint,
                   scoring_ruleset_fingerprint, feature_rows, target_rows
            FROM feature_build_metadata
            ORDER BY data_fingerprint
            """
        ).fetchall()
        if len(metadata_rows) != 1:
            raise RuntimeError("Exactly one validated Phase 3 feature build is required.")
        metadata = metadata_rows[0]
        feature_fingerprint = str(metadata[0])
        target_fingerprint = str(metadata[1])
        build_fingerprint = str(metadata[2])
        scoring_fingerprint = str(metadata[3])
        feature_rows = int(metadata[4])
        target_rows = int(metadata[5])
        if scoring_fingerprint != scoring_ruleset_fingerprint:
            raise RuntimeError("The requested scoring rules do not match the feature build.")
        actual_counts = connection.execute(
            """
            SELECT
                (SELECT count(*) FROM player_season_features WHERE source = 'nflverse'),
                (SELECT count(*) FROM player_season_targets WHERE source = 'nflverse'),
                (SELECT count(DISTINCT data_fingerprint)
                   FROM player_season_features WHERE source = 'nflverse'),
                (SELECT count(*) FROM player_season_features
                   WHERE source = 'nflverse' AND data_fingerprint IS NULL)
            """
        ).fetchone()
        if (
            actual_counts is None
            or int(actual_counts[0]) != feature_rows
            or int(actual_counts[1]) != target_rows
            or int(actual_counts[2]) != 1
            or int(actual_counts[3]) != 0
        ):
            raise RuntimeError("Phase 3 feature/target row accounting is stale.")
        baseline_rows = connection.execute(
            """
            SELECT report_fingerprint, feature_data_fingerprint,
                   target_data_fingerprint, build_fingerprint,
                   scoring_ruleset_fingerprint, prediction_rows, report_payload
            FROM baseline_evaluation_metadata
            ORDER BY report_fingerprint
            """
        ).fetchall()
        if len(baseline_rows) != 1:
            raise RuntimeError("Exactly one completed Phase 3 baseline evaluation is required.")
        baseline = baseline_rows[0]
        baseline_fingerprint = str(baseline[0])
        if tuple(str(value) for value in baseline[1:5]) != (
            feature_fingerprint,
            target_fingerprint,
            build_fingerprint,
            scoring_fingerprint,
        ):
            raise RuntimeError("The baseline evaluation is stale for the active feature build.")
        prediction_count = connection.execute(
            "SELECT count(*) FROM baseline_predictions"
        ).fetchone()
        if prediction_count is None or int(prediction_count[0]) != int(baseline[5]):
            raise RuntimeError("The baseline prediction row count is stale.")
        baseline_report = json.loads(str(baseline[6]))
        _validate_baseline_report(
            baseline_report,
            baseline_fingerprint=baseline_fingerprint,
            feature_fingerprint=feature_fingerprint,
            target_fingerprint=target_fingerprint,
            build_fingerprint=build_fingerprint,
            scoring_fingerprint=scoring_fingerprint,
            validation_start_season=validation_start_season,
            test_season=test_season,
        )
        feature_data = connection.execute(
            """
            SELECT feature.player_id, feature.prediction_season, feature.position,
                   feature.feature_payload, target.target_payload
            FROM player_season_features AS feature
            LEFT JOIN player_season_targets AS target
              ON feature.player_id = target.player_id
             AND feature.prediction_season = target.prediction_season
             AND target.data_fingerprint = ?
             AND target.target_data_fingerprint = ?
            WHERE feature.source = 'nflverse'
              AND feature.data_fingerprint = ?
              AND feature.scoring_ruleset_fingerprint = ?
              AND NOT feature.is_synthetic
            ORDER BY feature.prediction_season, feature.position, feature.player_id
            """,
            [
                feature_fingerprint,
                target_fingerprint,
                feature_fingerprint,
                scoring_fingerprint,
            ],
        ).fetchall()
    if len(feature_data) != feature_rows:
        raise RuntimeError("Synthetic or stale rows prevent a complete Phase 4 feature read.")
    rows = tuple(
        PlayerSeasonModelRow.from_json_payloads(
            player_id=str(row[0]),
            prediction_season=int(row[1]),
            position=str(row[2]),
            feature_payload=str(row[3]),
            target_payload=str(row[4]) if row[4] is not None else None,
        )
        for row in feature_data
    )
    return FrozenProjectionContract(
        rows=rows,
        feature_data_fingerprint=feature_fingerprint,
        target_data_fingerprint=target_fingerprint,
        build_fingerprint=build_fingerprint,
        scoring_ruleset_fingerprint=scoring_fingerprint,
        baseline_report_fingerprint=baseline_fingerprint,
        feature_rows=feature_rows,
        target_rows=target_rows,
        folds=tuple(dict(fold) for fold in baseline_report["folds"]),
        baseline_report=baseline_report,
    )


def read_baseline_predictions(
    config: AppConfig, contract: FrozenProjectionContract
) -> list[dict[str, Any]]:
    """Return deterministic Phase 3 predictions for comparison and fallbacks."""

    warehouse = Warehouse(config.resolve(config.paths.warehouse))
    with warehouse.connect(read_only=True) as connection:
        summary = connection.execute(
            """
            SELECT count(*), count(DISTINCT baseline_version),
                   count(*) FILTER (
                       WHERE feature_data_fingerprint <> ?
                          OR target_data_fingerprint <> ?
                          OR build_fingerprint <> ?
                          OR scoring_ruleset_fingerprint <> ?
                   )
            FROM baseline_predictions
            """,
            [
                contract.feature_data_fingerprint,
                contract.target_data_fingerprint,
                contract.build_fingerprint,
                contract.scoring_ruleset_fingerprint,
            ],
        ).fetchone()
        names = {
            str(row[0])
            for row in connection.execute(
                "SELECT DISTINCT baseline_name FROM baseline_predictions"
            ).fetchall()
        }
        targets = {
            str(row[0])
            for row in connection.execute(
                "SELECT DISTINCT target_name FROM baseline_predictions"
            ).fetchall()
        }
        versions = {
            str(row[0])
            for row in connection.execute(
                "SELECT DISTINCT baseline_version FROM baseline_predictions"
            ).fetchall()
        }
        expected_rows = contract.feature_rows * len(_REQUIRED_BASELINES) * len(_REQUIRED_TARGETS)
        expected_version = str(contract.baseline_report["baseline_version"])
        if (
            summary is None
            or int(summary[0]) != expected_rows
            or int(summary[1]) != 1
            or int(summary[2]) != 0
            or names != _REQUIRED_BASELINES
            or targets != _REQUIRED_TARGETS
            or versions != {expected_version}
        ):
            raise RuntimeError(
                "Baseline predictions do not exactly match the frozen Phase 3 contract."
            )
        rows = connection.execute(
            """
            SELECT player_id, prediction_season, position, target_name, baseline_name,
                   predicted_value, actual_value, experience_group
            FROM baseline_predictions
            WHERE feature_data_fingerprint = ?
              AND target_data_fingerprint = ?
              AND build_fingerprint = ?
              AND scoring_ruleset_fingerprint = ?
            ORDER BY prediction_season, position, player_id, target_name, baseline_name
            """,
            [
                contract.feature_data_fingerprint,
                contract.target_data_fingerprint,
                contract.build_fingerprint,
                contract.scoring_ruleset_fingerprint,
            ],
        ).fetchall()
    column_names = (
        "player_id",
        "prediction_season",
        "position",
        "target_name",
        "baseline_name",
        "predicted_value",
        "actual_value",
        "experience_group",
    )
    return [dict(zip(column_names, row, strict=True)) for row in rows]


def persist_projection_run(
    config: AppConfig,
    *,
    run: dict[str, Any],
    models: list[dict[str, Any]],
    predictions: list[dict[str, Any]],
    champions: list[dict[str, Any]],
    evaluation: dict[str, Any],
    board: list[dict[str, Any]],
) -> None:
    """Validate and atomically replace the complete active Phase 4 publication."""

    _validate_record_keys(run, RUN_COLUMNS, "run")
    _validate_record_keys(evaluation, EVALUATION_COLUMNS, "evaluation")
    if str(run["status"]) != "validating":
        raise ValueError("A new Phase 4 run must be persisted with validating status.")
    for name, records, columns in (
        ("model", models, MODEL_COLUMNS),
        ("prediction", predictions, PREDICTION_COLUMNS),
        ("champion", champions, CHAMPION_COLUMNS),
        ("board", board, BOARD_COLUMNS),
    ):
        for record in records:
            _validate_record_keys(record, columns, name)
    run_id = str(run["run_id"])
    dependent_records = [*models, *predictions, *champions, *board]
    if any(str(record["run_id"]) != run_id for record in dependent_records):
        raise ValueError("Every Phase 4 record must use the same run_id.")
    if str(evaluation["run_id"]) != run_id:
        raise ValueError("Evaluation metadata must use the active run_id.")
    expected_counts = {
        "prediction_rows": len(predictions),
        "evaluated_rows": sum(row["actual_value"] is not None for row in predictions),
        "live_prediction_rows": sum(row["prediction_scope"] == "live" for row in predictions),
        "model_rows": len(models),
        "champion_rows": len(champions),
    }
    for field, expected in expected_counts.items():
        if int(run[field]) != expected:
            raise ValueError(f"Run {field}={run[field]} does not match {expected} records.")
    warehouse = Warehouse(config.resolve(config.paths.warehouse))
    warehouse.initialize()
    with warehouse.connect() as connection:
        connection.execute("BEGIN TRANSACTION")
        try:
            for table in (
                "player_projection_board",
                "player_projection_evaluation_metadata",
                "player_projection_champions",
                "player_projection_predictions",
                "player_projection_models",
                "player_projection_runs",
            ):
                connection.execute(f"DELETE FROM {table}")
            _insert_records(connection, "player_projection_runs", RUN_COLUMNS, [run])
            _insert_records(connection, "player_projection_models", MODEL_COLUMNS, models)
            _insert_records(
                connection,
                "player_projection_predictions",
                PREDICTION_COLUMNS,
                predictions,
            )
            _insert_records(
                connection,
                "player_projection_champions",
                CHAMPION_COLUMNS,
                champions,
            )
            _insert_records(
                connection,
                "player_projection_evaluation_metadata",
                EVALUATION_COLUMNS,
                [evaluation],
            )
            _insert_records(connection, "player_projection_board", BOARD_COLUMNS, board)
            counts = connection.execute(
                """
                SELECT
                    (SELECT count(*) FROM player_projection_models WHERE run_id = ?),
                    (SELECT count(*) FROM player_projection_predictions WHERE run_id = ?),
                    (SELECT count(*) FROM player_projection_champions WHERE run_id = ?),
                    (SELECT count(*) FROM player_projection_board WHERE run_id = ?)
                """,
                [run_id, run_id, run_id, run_id],
            ).fetchone()
            if counts is None or tuple(int(value) for value in counts) != (
                len(models),
                len(predictions),
                len(champions),
                len(board),
            ):
                raise RuntimeError("Phase 4 warehouse row accounting failed.")
            integrity_issues = projection_integrity_issues(
                config,
                expected_status="validating",
                connection=connection,
            )
            if integrity_issues:
                raise RuntimeError("; ".join(integrity_issues))
            _promote_projection_run(connection, run_id)
            connection.execute("COMMIT")
        except Exception:
            connection.execute("ROLLBACK")
            raise


def _promote_projection_run(connection: duckdb.DuckDBPyConnection, run_id: str) -> None:
    """Promote the staged run on the caller's still-open publication transaction."""

    rows = connection.execute(
        "SELECT run_id, status FROM player_projection_runs",
    ).fetchall()
    if rows != [(run_id, "validating")]:
        raise RuntimeError("Phase 4 completion requires exactly one matching validating run.")
    connection.execute(
        "UPDATE player_projection_runs SET status = 'complete' WHERE run_id = ?",
        [run_id],
    )
    completed = connection.execute(
        "SELECT count(*) FROM player_projection_runs WHERE run_id = ? AND status = 'complete'",
        [run_id],
    ).fetchone()
    if completed is None or int(completed[0]) != 1:
        raise RuntimeError("The Phase 4 run status transition did not persist.")


def projection_integrity_issues(
    config: AppConfig,
    *,
    expected_status: str = "complete",
    connection: duckdb.DuckDBPyConnection | None = None,
) -> tuple[str, ...]:
    """Audit the registered current Phase 4 run, including local file hashes."""

    if expected_status not in {"validating", "complete"}:
        raise ValueError("Phase 4 integrity status must be validating or complete.")

    connection_context: AbstractContextManager[duckdb.DuckDBPyConnection]
    if connection is None:
        warehouse = Warehouse(config.resolve(config.paths.warehouse))
        if not warehouse.path.is_file():
            return ()
        warehouse.initialize()
        connection_context = warehouse.connect(read_only=True)
    else:
        connection_context = nullcontext(connection)
    issues: list[str] = []
    with connection_context as connection:
        run_count_row = connection.execute("SELECT count(*) FROM player_projection_runs").fetchone()
        run_count = int(run_count_row[0]) if run_count_row is not None else 0
        dependent_count = connection.execute(
            """
            SELECT
                (SELECT count(*) FROM player_projection_models)
              + (SELECT count(*) FROM player_projection_predictions)
              + (SELECT count(*) FROM player_projection_champions)
              + (SELECT count(*) FROM player_projection_evaluation_metadata)
              + (SELECT count(*) FROM player_projection_board)
            """
        ).fetchone()
        dependents = int(dependent_count[0]) if dependent_count is not None else 0
        if run_count == 0:
            if dependents:
                issues.append("Phase 4 tables contain orphan rows without a registered run.")
            return tuple(issues)
        if run_count != 1:
            return ("Exactly one active Phase 4 player-projection run is required.",)
        run = connection.execute(
            """
            SELECT run_id, feature_data_fingerprint, target_data_fingerprint,
                   build_fingerprint, scoring_ruleset_fingerprint,
                   baseline_report_fingerprint, model_feature_fingerprint,
                   model_config_fingerprint, prediction_rows, evaluated_rows,
                   live_prediction_rows, model_rows, champion_rows, status,
                   run_payload
            FROM player_projection_runs
            """
        ).fetchone()
        if run is None:
            return ("The Phase 4 run could not be read.",)
        run_id = str(run[0])
        if str(run[13]) != expected_status:
            issues.append(f"The active Phase 4 run is not marked {expected_status}.")
        current = connection.execute(
            """
            SELECT metadata.data_fingerprint, metadata.target_data_fingerprint,
                   metadata.build_fingerprint, metadata.scoring_ruleset_fingerprint,
                   baseline.report_fingerprint
            FROM feature_build_metadata AS metadata
            JOIN baseline_evaluation_metadata AS baseline
              ON baseline.feature_data_fingerprint = metadata.data_fingerprint
             AND baseline.target_data_fingerprint = metadata.target_data_fingerprint
             AND baseline.build_fingerprint = metadata.build_fingerprint
             AND baseline.scoring_ruleset_fingerprint = metadata.scoring_ruleset_fingerprint
            """
        ).fetchall()
        if len(current) != 1 or tuple(str(value) for value in run[1:6]) != tuple(
            str(value) for value in current[0]
        ):
            issues.append("The Phase 4 run is stale for the active feature/baseline contract.")
        counts = connection.execute(
            """
            SELECT
                (SELECT count(*) FROM player_projection_predictions WHERE run_id = ?),
                (SELECT count(*) FROM player_projection_predictions
                   WHERE run_id = ? AND actual_value IS NOT NULL),
                (SELECT count(*) FROM player_projection_predictions
                   WHERE run_id = ? AND prediction_scope = 'live'),
                (SELECT count(*) FROM player_projection_models WHERE run_id = ?),
                (SELECT count(*) FROM player_projection_champions WHERE run_id = ?),
                (SELECT count(*) FROM player_projection_evaluation_metadata WHERE run_id = ?)
            """,
            [run_id] * 6,
        ).fetchone()
        expected = tuple(int(value) for value in run[8:13])
        if counts is None or tuple(int(value) for value in counts[:5]) != expected:
            issues.append("Phase 4 run metadata does not reconcile to persisted row counts.")
        if counts is None or int(counts[5]) != 1:
            issues.append("Exactly one evaluation report must belong to the active Phase 4 run.")
        invalid_predictions = connection.execute(
            """
            SELECT count(*)
            FROM player_projection_predictions
            WHERE run_id = ? AND (
                NOT isfinite(predicted_value) OR NOT isfinite(p10)
                OR NOT isfinite(p50) OR NOT isfinite(p90)
                OR p10 > p50 OR p50 > p90
                OR abs(predicted_value - p50) > 1e-9
                OR training_max_season >= prediction_season
                OR (prediction_scope = 'live' AND actual_value IS NOT NULL)
                OR prediction_scope NOT IN ('validation', 'test', 'live')
            )
            """,
            [run_id],
        ).fetchone()
        if invalid_predictions is None or int(invalid_predictions[0]):
            issues.append("Phase 4 predictions contain invalid values, intervals, or chronology.")
        invalid_board = connection.execute(
            """
            SELECT count(*)
            FROM player_projection_board AS board
            LEFT JOIN players AS player ON board.player_id = player.player_id
            WHERE board.run_id = ? AND (
                player.player_id IS NULL OR trim(player.display_name) = ''
                OR board.prediction_season <> ?
                OR trim(board.position) = '' OR trim(board.prediction_status) = ''
                OR NOT isfinite(board.fantasy_points_per_game_p10)
                OR NOT isfinite(board.fantasy_points_per_game_p50)
                OR NOT isfinite(board.fantasy_points_per_game_p90)
                OR board.fantasy_points_per_game_p10 > board.fantasy_points_per_game_p50
                OR board.fantasy_points_per_game_p50 > board.fantasy_points_per_game_p90
                OR NOT isfinite(board.games_active_p10)
                OR NOT isfinite(board.games_active_p50)
                OR NOT isfinite(board.games_active_p90)
                OR board.games_active_p10 > board.games_active_p50
                OR board.games_active_p50 > board.games_active_p90
                OR board.games_active_p10 < 0 OR board.games_active_p90 > 18
                OR NOT isfinite(board.fantasy_points_total_p10)
                OR NOT isfinite(board.fantasy_points_total_p50)
                OR NOT isfinite(board.fantasy_points_total_p90)
                OR board.fantasy_points_total_p10 > board.fantasy_points_total_p50
                OR board.fantasy_points_total_p50 > board.fantasy_points_total_p90
                OR trim(board.fantasy_points_per_game_selected_source) = ''
                OR trim(board.fantasy_points_per_game_selected_name) = ''
                OR trim(board.games_active_selected_source) = ''
                OR trim(board.games_active_selected_name) = ''
                OR trim(board.fantasy_points_total_selected_source) = ''
                OR trim(board.fantasy_points_total_selected_name) = ''
                OR json_type(board.explanation_payload) IS DISTINCT FROM 'OBJECT'
            )
            """,
            [run_id, config.project.prediction_season],
        ).fetchone()
        if invalid_board is None or int(invalid_board[0]):
            issues.append(
                "Phase 4 projection board contains invalid values, identities, intervals, "
                "or labels."
            )
        invalid_baseline_intervals = connection.execute(
            """
            SELECT count(*)
            FROM player_projection_board
            WHERE run_id = ? AND (
                (
                    fantasy_points_per_game_selected_source = 'baseline'
                    AND (
                        abs(fantasy_points_per_game_p10 - fantasy_points_per_game_p50) > 1e-9
                        OR abs(fantasy_points_per_game_p50 - fantasy_points_per_game_p90) > 1e-9
                    )
                )
                OR (
                    games_active_selected_source = 'baseline'
                    AND (
                        abs(games_active_p10 - games_active_p50) > 1e-9
                        OR abs(games_active_p50 - games_active_p90) > 1e-9
                    )
                )
                OR (
                    fantasy_points_total_selected_source = 'baseline'
                    AND (
                        abs(fantasy_points_total_p10 - fantasy_points_total_p50) > 1e-9
                        OR abs(fantasy_points_total_p50 - fantasy_points_total_p90) > 1e-9
                    )
                )
            )
            """,
            [run_id],
        ).fetchone()
        if invalid_baseline_intervals is None or int(invalid_baseline_intervals[0]):
            issues.append("Phase 4 transparent baseline board selections must remain point-only.")
        orphan_predictions = connection.execute(
            """
            SELECT count(*)
            FROM player_projection_predictions AS prediction
            LEFT JOIN players AS player ON prediction.player_id = player.player_id
            WHERE prediction.run_id = ? AND player.player_id IS NULL
            """,
            [run_id],
        ).fetchone()
        if orphan_predictions is None or int(orphan_predictions[0]):
            issues.append("Phase 4 predictions contain orphan player IDs.")
        live_features = connection.execute(
            "SELECT count(*) FROM player_season_features WHERE prediction_season = ?"
            " AND source = 'nflverse'",
            [config.project.prediction_season],
        ).fetchone()
        board_rows = connection.execute(
            "SELECT count(*) FROM player_projection_board WHERE run_id = ?",
            [run_id],
        ).fetchone()
        if (
            live_features is None
            or board_rows is None
            or int(live_features[0]) != int(board_rows[0])
        ):
            issues.append("The learned projection board does not cover every live feature row.")
        lineage_columns = (
            "feature_data_fingerprint",
            "target_data_fingerprint",
            "build_fingerprint",
            "scoring_ruleset_fingerprint",
            "baseline_report_fingerprint",
            "model_feature_fingerprint",
            "model_config_fingerprint",
        )
        lineage_expected = tuple(str(value) for value in run[1:8])
        for table in (
            "player_projection_predictions",
            "player_projection_evaluation_metadata",
            "player_projection_board",
        ):
            summary = connection.execute(
                f"SELECT DISTINCT {', '.join(lineage_columns)} FROM {table} WHERE run_id = ?",
                [run_id],
            ).fetchall()
            if len(summary) != 1 or tuple(str(value) for value in summary[0]) != lineage_expected:
                issues.append(f"{table} does not share the active run lineage.")
        registered_files = connection.execute(
            """
            SELECT artifact_path, artifact_sha256, artifact_size_bytes,
                   model_card_path, model_card_sha256
            FROM player_projection_models
            WHERE run_id = ?
            ORDER BY model_id
            """,
            [run_id],
        ).fetchall()
        try:
            registered_outputs = json.loads(str(run[14]))
        except (TypeError, ValueError):
            registered_outputs = {}
            issues.append("The active Phase 4 run payload is not valid JSON.")
    for artifact_path, artifact_hash, artifact_size, card_path, card_hash in registered_files:
        _audit_registered_file(
            config.project_root,
            str(artifact_path),
            str(artifact_hash),
            int(artifact_size),
            "artifact",
            issues,
        )
        _audit_registered_file(
            config.project_root,
            str(card_path),
            str(card_hash),
            None,
            "model card",
            issues,
        )
    report_files = registered_outputs.get("report_files", {})
    registry = registered_outputs.get("registry", {})
    plot_files = registered_outputs.get("plot_files", {})
    for path_key, hash_key, label in (
        ("json_path", "json_sha256", "JSON evaluation report"),
        ("markdown_path", "markdown_sha256", "Markdown evaluation report"),
    ):
        if not isinstance(report_files, dict) or not report_files.get(path_key):
            issues.append(f"The active Phase 4 run does not register its {label}.")
        else:
            _audit_registered_file(
                config.project_root,
                str(report_files[path_key]),
                str(report_files.get(hash_key, "")),
                None,
                label,
                issues,
            )
    if not isinstance(registry, dict) or not registry.get("path"):
        issues.append("The active Phase 4 run does not register its authoritative registry.")
    else:
        _audit_registered_file(
            config.project_root,
            str(registry["path"]),
            str(registry.get("sha256", "")),
            None,
            "model registry",
            issues,
        )
    if not isinstance(plot_files, dict) or not plot_files:
        issues.append("The active Phase 4 run does not register its diagnostic plots.")
    else:
        for plot_name, metadata in sorted(plot_files.items()):
            if not isinstance(metadata, dict) or not metadata.get("path"):
                issues.append(f"The active Phase 4 run has invalid {plot_name} plot metadata.")
                continue
            _audit_registered_file(
                config.project_root,
                str(metadata["path"]),
                str(metadata.get("sha256", "")),
                None,
                f"{plot_name} diagnostic plot",
                issues,
            )
    return tuple(issues)


def _validate_baseline_report(
    report: dict[str, Any],
    *,
    baseline_fingerprint: str,
    feature_fingerprint: str,
    target_fingerprint: str,
    build_fingerprint: str,
    scoring_fingerprint: str,
    validation_start_season: int,
    test_season: int,
) -> None:
    if report.get("status") != "PASSED":
        raise RuntimeError("The Phase 3 baseline report did not pass its quality gate.")
    lineage = (
        report.get("feature_data_fingerprint"),
        report.get("target_data_fingerprint"),
        report.get("build_fingerprint"),
        report.get("scoring_ruleset_fingerprint"),
    )
    if tuple(str(value) for value in lineage) != (
        feature_fingerprint,
        target_fingerprint,
        build_fingerprint,
        scoring_fingerprint,
    ):
        raise RuntimeError("The baseline report payload has stale lineage.")
    embedded_fingerprint = report.get("report_fingerprint")
    fingerprint_payload = dict(report)
    fingerprint_payload.pop("report_fingerprint", None)
    calculated = hashlib.sha256(canonical_json(fingerprint_payload).encode("utf-8")).hexdigest()
    if embedded_fingerprint != baseline_fingerprint or calculated != baseline_fingerprint:
        raise RuntimeError("The baseline report fingerprint does not verify.")
    folds = report.get("folds")
    if not isinstance(folds, list) or not folds:
        raise RuntimeError("The baseline report has no chronological folds.")
    evaluation_seasons = [int(fold["evaluation_season"]) for fold in folds]
    labels = [str(fold["label"]) for fold in folds]
    if evaluation_seasons != list(range(validation_start_season, test_season + 1)):
        raise RuntimeError("The baseline folds do not match the requested Phase 4 seasons.")
    if labels != ["validation"] * (len(labels) - 1) + ["test"]:
        raise RuntimeError("The baseline folds must reserve only the final season as test.")
    for fold in folds:
        training = tuple(int(value) for value in fold["training_seasons"])
        evaluation = int(fold["evaluation_season"])
        if not training or max(training) >= evaluation:
            raise RuntimeError("A baseline fold violates chronological isolation.")


def _validate_record_keys(record: dict[str, Any], columns: tuple[str, ...], name: str) -> None:
    if set(record) != set(columns):
        missing = sorted(set(columns) - set(record))
        extra = sorted(set(record) - set(columns))
        raise ValueError(f"Invalid {name} record keys; missing={missing}, extra={extra}.")


def _insert_records(
    connection: duckdb.DuckDBPyConnection,
    table: str,
    columns: tuple[str, ...],
    records: list[dict[str, Any]],
) -> None:
    if not records:
        return
    placeholders = ", ".join("?" for _ in columns)
    column_sql = ", ".join(columns)
    connection.executemany(
        f"INSERT INTO {table} ({column_sql}) VALUES ({placeholders})",
        [tuple(record[column] for column in columns) for record in records],
    )


def _audit_registered_file(
    project_root: Path,
    relative_path: str,
    expected_hash: str,
    expected_size: int | None,
    label: str,
    issues: list[str],
) -> None:
    candidate = Path(relative_path)
    if candidate.is_absolute():
        issues.append(f"A registered Phase 4 {label} path is absolute.")
        return
    resolved = (project_root / candidate).resolve()
    try:
        resolved.relative_to(project_root.resolve())
    except ValueError:
        issues.append(f"A registered Phase 4 {label} path escapes the project root.")
        return
    if not resolved.is_file():
        issues.append(f"A registered Phase 4 {label} is missing: {relative_path}.")
        return
    if expected_size is not None and resolved.stat().st_size != expected_size:
        issues.append(f"A registered Phase 4 {label} has the wrong size: {relative_path}.")
    actual_hash = (
        _canonical_text_sha256(resolved)
        if label in {"model card", "Markdown evaluation report"}
        else sha256_file(resolved)
    )
    if actual_hash != expected_hash:
        issues.append(f"A registered Phase 4 {label} hash does not match: {relative_path}.")


def _canonical_text_sha256(path: Path) -> str:
    """Hash UTF-8 publication text independently of Git checkout line endings."""

    canonical_bytes = path.read_bytes().replace(b"\r\n", b"\n").replace(b"\r", b"\n")
    return hashlib.sha256(canonical_bytes).hexdigest()
