"""Read-only access to the validated Phase 4 player-projection board."""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from datetime import date, datetime
from pathlib import Path
from typing import Any

import duckdb
import pandas as pd

from fantasy_draft_ai.config import AppConfig

TARGET_FANTASY_POINTS_PER_GAME = "fantasy_points_per_game"
TARGET_GAMES_ACTIVE = "games_active"
TARGET_FANTASY_POINTS_TOTAL = "fantasy_points_total"
PROJECTION_TARGETS = (
    TARGET_FANTASY_POINTS_PER_GAME,
    TARGET_GAMES_ACTIVE,
    TARGET_FANTASY_POINTS_TOTAL,
)
TARGET_LABELS = {
    TARGET_FANTASY_POINTS_PER_GAME: "Fantasy points per game",
    TARGET_GAMES_ACTIVE: "Games active",
    TARGET_FANTASY_POINTS_TOTAL: "Season fantasy points",
}

_REQUIRED_TABLES = {
    "players",
    "player_season_features",
    "player_season_targets",
    "feature_build_metadata",
    "baseline_evaluation_metadata",
    "player_projection_runs",
    "player_projection_models",
    "player_projection_predictions",
    "player_projection_champions",
    "player_projection_evaluation_metadata",
    "player_projection_board",
}
_LINEAGE_FIELDS = (
    "feature_data_fingerprint",
    "target_data_fingerprint",
    "build_fingerprint",
    "scoring_ruleset_fingerprint",
    "baseline_report_fingerprint",
    "model_feature_fingerprint",
    "model_config_fingerprint",
)


@dataclass(frozen=True)
class ProjectionLineage:
    """Fingerprints that bind a projection run to its exact upstream inputs."""

    feature_data_fingerprint: str
    target_data_fingerprint: str
    build_fingerprint: str
    scoring_ruleset_fingerprint: str
    baseline_report_fingerprint: str
    model_feature_fingerprint: str
    model_config_fingerprint: str

    def as_dict(self) -> dict[str, str]:
        return {field: str(getattr(self, field)) for field in _LINEAGE_FIELDS}


@dataclass(frozen=True)
class ProjectionSelection:
    """The validation-only champion for one position and target."""

    position: str
    target_name: str
    selected_source: str
    selected_name: str
    model_id: str | None
    selection_metric: str
    selection_value: float
    reference_baseline_name: str
    reference_baseline_value: float
    improvement: float
    details: dict[str, Any]

    def as_dict(self) -> dict[str, Any]:
        return {
            "position": self.position,
            "target_name": self.target_name,
            "selected_source": self.selected_source,
            "selected_name": self.selected_name,
            "model_id": self.model_id,
            "selection_metric": self.selection_metric,
            "selection_value": self.selection_value,
            "reference_baseline_name": self.reference_baseline_name,
            "reference_baseline_value": self.reference_baseline_value,
            "improvement": self.improvement,
            "details": self.details,
        }


@dataclass(frozen=True)
class ProjectionRun:
    """Public metadata for the one validated Phase 4 run."""

    run_id: str
    status: str
    trained_at: str
    prediction_season: int
    lineage: ProjectionLineage
    split_seasons: Any
    feature_rows: int
    target_rows: int
    training_rows: int
    prediction_rows: int
    evaluated_rows: int
    live_prediction_rows: int
    candidate_rows: int
    model_rows: int
    champion_rows: int

    def as_dict(self) -> dict[str, Any]:
        return {
            "run_id": self.run_id,
            "status": self.status,
            "trained_at": self.trained_at,
            "prediction_season": self.prediction_season,
            "lineage": self.lineage.as_dict(),
            "split_seasons": self.split_seasons,
            "counts": {
                "feature_rows": self.feature_rows,
                "target_rows": self.target_rows,
                "training_rows": self.training_rows,
                "prediction_rows": self.prediction_rows,
                "evaluated_rows": self.evaluated_rows,
                "live_prediction_rows": self.live_prediction_rows,
                "candidate_rows": self.candidate_rows,
                "model_rows": self.model_rows,
                "champion_rows": self.champion_rows,
            },
        }


@dataclass(frozen=True)
class ProjectionInterval:
    """One target's central estimate, empirical interval, and selected method."""

    p10: float
    p50: float
    p90: float
    selected_source: str
    selected_name: str

    def method_label(self, prediction_status: str) -> str:
        """Return a truthful, user-facing method class."""

        status = prediction_status.casefold()
        source = self.selected_source.casefold()
        if "rookie" in status or "unvalidated" in status:
            return "Heuristic fallback (unvalidated / uncalibrated)"
        if source == "learned":
            return "Learned model"
        if source == "baseline":
            return "Transparent baseline (point estimate)"
        return "Heuristic fallback"

    def as_dict(self, *, prediction_status: str) -> dict[str, Any]:
        return {
            "p10": self.p10,
            "p50": self.p50,
            "p90": self.p90,
            "selected_source": self.selected_source,
            "selected_name": self.selected_name,
            "method_label": self.method_label(prediction_status),
        }


@dataclass(frozen=True)
class PlayerProjection:
    """One player's live projection row with all three Phase 4 targets."""

    run_id: str
    player_id: str
    display_name: str
    prediction_season: int
    position: str
    prediction_status: str
    targets: dict[str, ProjectionInterval]
    explanation: dict[str, Any]

    def target(self, target_name: str) -> ProjectionInterval:
        if target_name not in self.targets:
            raise ValueError(f"Unsupported projection target: {target_name}.")
        return self.targets[target_name]

    def explanation_for(self, target_name: str) -> dict[str, Any]:
        """Extract a target explanation while tolerating versioned payload envelopes."""

        if target_name not in PROJECTION_TARGETS:
            raise ValueError(f"Unsupported projection target: {target_name}.")
        direct = self.explanation.get(target_name)
        if isinstance(direct, dict):
            return direct
        nested = self.explanation.get("targets")
        nested_target = nested.get(target_name) if isinstance(nested, dict) else None
        if isinstance(nested_target, dict):
            return {str(key): value for key, value in nested_target.items()}
        return self.explanation

    def as_dict(self) -> dict[str, Any]:
        return {
            "run_id": self.run_id,
            "player_id": self.player_id,
            "display_name": self.display_name,
            "prediction_season": self.prediction_season,
            "position": self.position,
            "prediction_status": self.prediction_status,
            "targets": {
                name: interval.as_dict(prediction_status=self.prediction_status)
                for name, interval in self.targets.items()
            },
            "explanation": self.explanation,
        }

    def as_record(self, target_name: str) -> dict[str, Any]:
        """Return one flat record suitable for JSON, pandas, or Streamlit."""

        interval = self.target(target_name)
        return {
            "run_id": self.run_id,
            "player_id": self.player_id,
            "display_name": self.display_name,
            "prediction_season": self.prediction_season,
            "position": self.position,
            "target_name": target_name,
            "p10": interval.p10,
            "p50": interval.p50,
            "p90": interval.p90,
            "selected_source": interval.selected_source,
            "selected_name": interval.selected_name,
            "method_label": interval.method_label(self.prediction_status),
            "prediction_status": self.prediction_status,
            "explanation": self.explanation_for(target_name),
        }


@dataclass(frozen=True)
class ProjectionBoardStatus:
    """Availability result safe to show even when Phase 4 is absent or stale."""

    available: bool
    code: str
    message: str
    run: ProjectionRun | None = None
    row_count: int = 0
    learned_selection_rows: int = 0
    transparent_baseline_rows: int = 0
    rookie_fallback_rows: int = 0


@dataclass(frozen=True)
class ProjectionBoard:
    """Validated projection rows plus run lineage and champion selections."""

    status: ProjectionBoardStatus
    rows: tuple[PlayerProjection, ...] = ()
    selections: tuple[ProjectionSelection, ...] = ()

    @property
    def available(self) -> bool:
        return self.status.available

    @property
    def run(self) -> ProjectionRun | None:
        return self.status.run

    def records(self, target_name: str) -> list[dict[str, Any]]:
        if target_name not in PROJECTION_TARGETS:
            raise ValueError(f"Unsupported projection target: {target_name}.")
        return [row.as_record(target_name) for row in self.rows]

    def to_frame(self, target_name: str) -> pd.DataFrame:
        """Return a flat, predictably ordered pandas frame for one target."""

        frame = pd.DataFrame.from_records(self.records(target_name))
        if frame.empty:
            return frame
        return frame.sort_values(
            ["position", "p50", "display_name", "player_id"],
            ascending=[True, False, True, True],
            kind="stable",
        ).reset_index(drop=True)

    def as_dict(self) -> dict[str, Any]:
        return {
            "status": {
                "available": self.status.available,
                "code": self.status.code,
                "message": self.status.message,
                "row_count": self.status.row_count,
                "learned_selection_rows": self.status.learned_selection_rows,
                "transparent_baseline_rows": self.status.transparent_baseline_rows,
                "rookie_fallback_rows": self.status.rookie_fallback_rows,
            },
            "run": self.run.as_dict() if self.run is not None else None,
            "selections": [selection.as_dict() for selection in self.selections],
            "players": [row.as_dict() for row in self.rows],
        }


def projection_board_status(config: AppConfig) -> ProjectionBoardStatus:
    """Validate Phase 4 availability without loading player-level board rows."""

    warehouse = config.resolve(config.paths.warehouse)
    if not warehouse.is_file():
        return _unavailable("not_built", "not built; train and validate Phase 4 first")
    try:
        with duckdb.connect(str(warehouse), read_only=True) as connection:
            return _inspect_projection_board(connection, config)
    except (
        duckdb.Error,
        OSError,
        RuntimeError,
        TypeError,
        ValueError,
        json.JSONDecodeError,
    ):
        return _unavailable("unreadable", "Phase 4 data could not be read safely")


def load_projection_board(config: AppConfig) -> ProjectionBoard:
    """Load the board only after its run, lineage, counts, and files validate."""

    warehouse = config.resolve(config.paths.warehouse)
    if not warehouse.is_file():
        return ProjectionBoard(
            status=_unavailable("not_built", "not built; train and validate Phase 4 first")
        )
    try:
        with duckdb.connect(str(warehouse), read_only=True) as connection:
            status = _inspect_projection_board(connection, config)
            if not status.available or status.run is None:
                return ProjectionBoard(status=status)
            selections = _load_selections(connection, status.run.run_id)
            rows = _load_rows(connection, status.run.run_id, status.run.prediction_season)
            if len(rows) != status.row_count:
                return ProjectionBoard(
                    status=_unavailable(
                        "changed_during_read",
                        "Phase 4 changed while it was being read; reload after training finishes",
                        run=status.run,
                    )
                )
            return ProjectionBoard(status=status, rows=rows, selections=selections)
    except (
        duckdb.Error,
        OSError,
        RuntimeError,
        TypeError,
        ValueError,
        json.JSONDecodeError,
    ):
        return ProjectionBoard(
            status=_unavailable("unreadable", "Phase 4 data could not be read safely")
        )


def _inspect_projection_board(
    connection: duckdb.DuckDBPyConnection,
    config: AppConfig,
) -> ProjectionBoardStatus:
    tables = {
        str(row[0])
        for row in connection.execute(
            "SELECT table_name FROM information_schema.tables WHERE table_schema = 'main'"
        ).fetchall()
    }
    missing = sorted(_REQUIRED_TABLES - tables)
    if missing:
        return _unavailable("not_built", "Phase 4 warehouse tables are not initialized")

    run_count = _scalar_int(connection, "SELECT count(*) FROM player_projection_runs")
    dependent_count = _scalar_int(
        connection,
        """
        SELECT
            (SELECT count(*) FROM player_projection_models)
          + (SELECT count(*) FROM player_projection_predictions)
          + (SELECT count(*) FROM player_projection_champions)
          + (SELECT count(*) FROM player_projection_evaluation_metadata)
          + (SELECT count(*) FROM player_projection_board)
        """,
    )
    if run_count == 0:
        message = (
            "Phase 4 is partial: output rows exist without a registered run"
            if dependent_count
            else "not built; train and validate Phase 4 first"
        )
        return _unavailable("partial" if dependent_count else "not_built", message)
    if run_count != 1:
        return _unavailable("partial", "Phase 4 must have exactly one current run")

    run_row = _fetch_one_dict(connection, "SELECT * FROM player_projection_runs")
    if run_row is None:
        return _unavailable("partial", "The registered Phase 4 run could not be read")
    run = _build_run(run_row, config.project.prediction_season)
    if run.status != "complete":
        return _unavailable(
            "partial",
            f"Phase 4 run {run.run_id[:12]} is {run.status!r}, not complete",
            run=run,
        )

    positive_counts = (
        run.feature_rows,
        run.target_rows,
        run.training_rows,
        run.prediction_rows,
        run.evaluated_rows,
        run.live_prediction_rows,
        run.candidate_rows,
        run.model_rows,
        run.champion_rows,
    )
    if any(value <= 0 for value in positive_counts):
        return _unavailable("partial", "Phase 4 recorded counts are incomplete", run=run)

    active_contract = connection.execute(
        """
        SELECT metadata.data_fingerprint, metadata.target_data_fingerprint,
               metadata.build_fingerprint, metadata.scoring_ruleset_fingerprint,
               baseline.report_fingerprint, metadata.feature_rows, metadata.target_rows
        FROM feature_build_metadata AS metadata
        JOIN baseline_evaluation_metadata AS baseline
          ON baseline.feature_data_fingerprint = metadata.data_fingerprint
         AND baseline.target_data_fingerprint = metadata.target_data_fingerprint
         AND baseline.build_fingerprint = metadata.build_fingerprint
         AND baseline.scoring_ruleset_fingerprint = metadata.scoring_ruleset_fingerprint
        WHERE (SELECT count(*) FROM feature_build_metadata) = 1
          AND (SELECT count(*) FROM baseline_evaluation_metadata) = 1
        """
    ).fetchall()
    if len(active_contract) != 1:
        return _unavailable(
            "stale", "Phase 4 has no single active Phase 3 feature/baseline contract", run=run
        )
    contract = active_contract[0]
    if tuple(str(value) for value in contract[:5]) != (
        run.lineage.feature_data_fingerprint,
        run.lineage.target_data_fingerprint,
        run.lineage.build_fingerprint,
        run.lineage.scoring_ruleset_fingerprint,
        run.lineage.baseline_report_fingerprint,
    ):
        return _unavailable("stale", "Phase 4 lineage is stale", run=run)

    feature_summary = connection.execute(
        """
        SELECT count(*), count(DISTINCT data_fingerprint),
               count(*) FILTER (WHERE data_fingerprint IS NULL),
               count(*) FILTER (WHERE prediction_season = ?)
        FROM player_season_features
        WHERE source = 'nflverse'
        """,
        [config.project.prediction_season],
    ).fetchone()
    target_summary = connection.execute(
        """
        SELECT count(*), count(*) FILTER (
            WHERE data_fingerprint <> ? OR target_data_fingerprint <> ?
        )
        FROM player_season_targets
        WHERE source = 'nflverse'
        """,
        [run.lineage.feature_data_fingerprint, run.lineage.target_data_fingerprint],
    ).fetchone()
    if feature_summary is None or target_summary is None:
        return _unavailable("partial", "Phase 4 prerequisite counts could not be read", run=run)
    feature_rows = int(feature_summary[0])
    live_feature_rows = int(feature_summary[3])
    target_rows = int(target_summary[0])
    if (
        feature_rows != run.feature_rows
        or target_rows != run.target_rows
        or feature_rows != int(contract[5])
        or target_rows != int(contract[6])
        or int(feature_summary[1]) != 1
        or int(feature_summary[2]) != 0
        or int(target_summary[1]) != 0
        or live_feature_rows <= 0
    ):
        return _unavailable("stale", "Phase 4 prerequisite rows do not match its lineage", run=run)

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
            (SELECT count(*) FROM player_projection_evaluation_metadata WHERE run_id = ?),
            (SELECT count(*) FROM player_projection_board WHERE run_id = ?),
            (SELECT count(*) FROM player_projection_models WHERE run_id <> ?)
              + (SELECT count(*) FROM player_projection_predictions WHERE run_id <> ?)
              + (SELECT count(*) FROM player_projection_champions WHERE run_id <> ?)
              + (SELECT count(*) FROM player_projection_evaluation_metadata WHERE run_id <> ?)
              + (SELECT count(*) FROM player_projection_board WHERE run_id <> ?)
        """,
        [run.run_id] * 12,
    ).fetchone()
    if counts is None:
        return _unavailable("partial", "Phase 4 recorded counts could not be read", run=run)
    actual_counts = tuple(int(value) for value in counts[:5])
    expected_counts = (
        run.prediction_rows,
        run.evaluated_rows,
        run.live_prediction_rows,
        run.model_rows,
        run.champion_rows,
    )
    if (
        actual_counts != expected_counts
        or int(counts[5]) != 1
        or int(counts[6]) != live_feature_rows
        or int(counts[7]) != 0
    ):
        return _unavailable("partial", "Phase 4 recorded counts do not reconcile", run=run)

    evaluation = _fetch_one_dict(
        connection,
        "SELECT * FROM player_projection_evaluation_metadata WHERE run_id = ?",
        [run.run_id],
    )
    if evaluation is None:
        return _unavailable("partial", "Phase 4 evaluation metadata is missing", run=run)
    evaluation_lineage = tuple(str(evaluation[field]) for field in _LINEAGE_FIELDS)
    if evaluation_lineage != tuple(run.lineage.as_dict().values()):
        return _unavailable("stale", "Phase 4 evaluation lineage is stale", run=run)
    if (
        int(evaluation["prediction_rows"]) != run.prediction_rows
        or int(evaluation["evaluated_rows"]) != run.evaluated_rows
        or int(evaluation["live_prediction_rows"]) != run.live_prediction_rows
        or int(evaluation["candidate_rows"]) != run.candidate_rows
        or int(evaluation["champion_rows"]) != run.champion_rows
    ):
        return _unavailable("partial", "Phase 4 evaluation counts do not reconcile", run=run)

    invalid_predictions = _scalar_int(
        connection,
        """
        SELECT count(*)
        FROM player_projection_predictions AS prediction
        LEFT JOIN players AS player ON prediction.player_id = player.player_id
        WHERE prediction.run_id = ? AND (
            player.player_id IS NULL
            OR NOT isfinite(prediction.predicted_value) OR NOT isfinite(prediction.p10)
            OR NOT isfinite(prediction.p50) OR NOT isfinite(prediction.p90)
            OR prediction.p10 > prediction.p50 OR prediction.p50 > prediction.p90
            OR abs(prediction.predicted_value - prediction.p50) > 1e-9
            OR prediction.training_max_season >= prediction.prediction_season
            OR (
                prediction.prediction_scope = 'live'
                AND prediction.actual_value IS NOT NULL
            )
            OR prediction.prediction_scope NOT IN ('validation', 'test', 'live')
        )
        """,
        [run.run_id],
    )
    invalid_board = _scalar_int(
        connection,
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
            OR (
                board.fantasy_points_per_game_selected_source = 'baseline'
                AND (
                    abs(board.fantasy_points_per_game_p10
                        - board.fantasy_points_per_game_p50) > 1e-9
                    OR abs(board.fantasy_points_per_game_p50
                        - board.fantasy_points_per_game_p90) > 1e-9
                )
            )
            OR (
                board.games_active_selected_source = 'baseline'
                AND (
                    abs(board.games_active_p10 - board.games_active_p50) > 1e-9
                    OR abs(board.games_active_p50 - board.games_active_p90) > 1e-9
                )
            )
            OR (
                board.fantasy_points_total_selected_source = 'baseline'
                AND (
                    abs(board.fantasy_points_total_p10
                        - board.fantasy_points_total_p50) > 1e-9
                    OR abs(board.fantasy_points_total_p50
                        - board.fantasy_points_total_p90) > 1e-9
                )
            )
            OR json_type(board.explanation_payload) IS DISTINCT FROM 'OBJECT'
        )
        """,
        [run.run_id, config.project.prediction_season],
    )
    if invalid_predictions or invalid_board:
        return _unavailable("partial", "Phase 4 contains invalid prediction rows", run=run)

    evaluation_fingerprints = connection.execute(
        """
        SELECT DISTINCT evaluation_report_fingerprint
        FROM player_projection_board WHERE run_id = ?
        """,
        [run.run_id],
    ).fetchall()
    if evaluation_fingerprints != [(str(evaluation["report_fingerprint"]),)]:
        return _unavailable("stale", "The Phase 4 board has stale evaluation lineage", run=run)

    lineage_sql = ", ".join(_LINEAGE_FIELDS)
    for table in (
        "player_projection_predictions",
        "player_projection_evaluation_metadata",
        "player_projection_board",
    ):
        rows = connection.execute(
            f"SELECT DISTINCT {lineage_sql} FROM {table} WHERE run_id = ?",
            [run.run_id],
        ).fetchall()
        if len(rows) != 1 or tuple(str(value) for value in rows[0]) != tuple(
            run.lineage.as_dict().values()
        ):
            return _unavailable("stale", f"{table} has stale Phase 4 lineage", run=run)

    expected_champions = _scalar_int(
        connection,
        "SELECT count(DISTINCT position) * 3 FROM player_projection_board WHERE run_id = ?",
        [run.run_id],
    )
    bad_champions = _scalar_int(
        connection,
        """
        SELECT count(*)
        FROM player_projection_champions AS champion
        LEFT JOIN player_projection_models AS model
          ON champion.model_id = model.model_id AND champion.run_id = model.run_id
        WHERE champion.run_id = ? AND (
            champion.target_name NOT IN (
                'fantasy_points_per_game', 'games_active', 'fantasy_points_total'
            )
            OR trim(champion.selected_source) = '' OR trim(champion.selected_name) = ''
            OR (champion.selected_source = 'learned' AND model.model_id IS NULL)
        )
        """,
        [run.run_id],
    )
    if run.champion_rows != expected_champions or bad_champions:
        return _unavailable("partial", "Phase 4 champion selections are incomplete", run=run)

    files = connection.execute(
        """
        SELECT artifact_path, artifact_sha256, artifact_size_bytes,
               model_card_path, model_card_sha256
        FROM player_projection_models WHERE run_id = ? ORDER BY model_id
        """,
        [run.run_id],
    ).fetchall()
    if any(not _registered_files_match(config.project_root, row) for row in files):
        return _unavailable(
            "partial", "Phase 4 model artifacts or model cards do not verify", run=run
        )
    run_payload = _parse_json_object(run_row["run_payload"])
    if not _registered_output_files_match(config.project_root, run_payload):
        return _unavailable("partial", "Phase 4 reports or model registry do not verify", run=run)

    method_counts = connection.execute(
        """
        SELECT
            count(*) FILTER (WHERE
                fantasy_points_per_game_selected_source = 'learned'
                OR games_active_selected_source = 'learned'
                OR fantasy_points_total_selected_source = 'learned'
            ),
            count(*) FILTER (WHERE
                fantasy_points_per_game_selected_source = 'baseline'
                OR games_active_selected_source = 'baseline'
                OR fantasy_points_total_selected_source = 'baseline'
            ),
            count(*) FILTER (WHERE lower(prediction_status) LIKE '%rookie%')
        FROM player_projection_board WHERE run_id = ?
        """,
        [run.run_id],
    ).fetchone()
    if method_counts is None:
        return _unavailable("partial", "Phase 4 board methods could not be summarized", run=run)
    learned_rows, baseline_rows, rookie_rows = (int(value) for value in method_counts)
    message = (
        f"{live_feature_rows} validated {run.prediction_season} board rows; "
        f"{learned_rows} include learned selections"
    )
    if rookie_rows:
        message += f"; {rookie_rows} rookie heuristic fallbacks are unvalidated/uncalibrated"
    return ProjectionBoardStatus(
        available=True,
        code="available",
        message=message,
        run=run,
        row_count=live_feature_rows,
        learned_selection_rows=learned_rows,
        transparent_baseline_rows=baseline_rows,
        rookie_fallback_rows=rookie_rows,
    )


def _build_run(row: dict[str, Any], prediction_season: int) -> ProjectionRun:
    lineage = ProjectionLineage(**{field: str(row[field]) for field in _LINEAGE_FIELDS})
    return ProjectionRun(
        run_id=str(row["run_id"]),
        status=str(row["status"]),
        trained_at=_json_datetime(row["trained_at"]),
        prediction_season=prediction_season,
        lineage=lineage,
        split_seasons=_parse_json_value(row["split_seasons"]),
        feature_rows=int(row["feature_rows"]),
        target_rows=int(row["target_rows"]),
        training_rows=int(row["training_rows"]),
        prediction_rows=int(row["prediction_rows"]),
        evaluated_rows=int(row["evaluated_rows"]),
        live_prediction_rows=int(row["live_prediction_rows"]),
        candidate_rows=int(row["candidate_rows"]),
        model_rows=int(row["model_rows"]),
        champion_rows=int(row["champion_rows"]),
    )


def _load_selections(
    connection: duckdb.DuckDBPyConnection, run_id: str
) -> tuple[ProjectionSelection, ...]:
    cursor = connection.execute(
        """
        SELECT position, target_name, selected_source, selected_name, model_id,
               selection_metric, selection_value, reference_baseline_name,
               reference_baseline_value, improvement, selection_payload
        FROM player_projection_champions
        WHERE run_id = ? ORDER BY position, target_name
        """,
        [run_id],
    )
    return tuple(
        ProjectionSelection(
            position=str(row[0]),
            target_name=str(row[1]),
            selected_source=str(row[2]),
            selected_name=str(row[3]),
            model_id=str(row[4]) if row[4] is not None else None,
            selection_metric=str(row[5]),
            selection_value=float(row[6]),
            reference_baseline_name=str(row[7]),
            reference_baseline_value=float(row[8]),
            improvement=float(row[9]),
            details=_parse_json_object(row[10]),
        )
        for row in cursor.fetchall()
    )


def _load_rows(
    connection: duckdb.DuckDBPyConnection,
    run_id: str,
    prediction_season: int,
) -> tuple[PlayerProjection, ...]:
    rows = connection.execute(
        """
        SELECT board.run_id, board.player_id, player.display_name,
               board.prediction_season, board.position,
               board.fantasy_points_per_game_p10,
               board.fantasy_points_per_game_p50,
               board.fantasy_points_per_game_p90,
               board.fantasy_points_per_game_selected_source,
               board.fantasy_points_per_game_selected_name,
               board.games_active_p10, board.games_active_p50, board.games_active_p90,
               board.games_active_selected_source, board.games_active_selected_name,
               board.fantasy_points_total_p10, board.fantasy_points_total_p50,
               board.fantasy_points_total_p90,
               board.fantasy_points_total_selected_source,
               board.fantasy_points_total_selected_name,
               board.prediction_status, board.explanation_payload
        FROM player_projection_board AS board
        JOIN players AS player ON board.player_id = player.player_id
        WHERE board.run_id = ? AND board.prediction_season = ?
        ORDER BY board.position, board.fantasy_points_per_game_p50 DESC,
                 player.display_name, board.player_id
        """,
        [run_id, prediction_season],
    ).fetchall()
    return tuple(
        PlayerProjection(
            run_id=str(row[0]),
            player_id=str(row[1]),
            display_name=str(row[2]),
            prediction_season=int(row[3]),
            position=str(row[4]),
            targets={
                TARGET_FANTASY_POINTS_PER_GAME: ProjectionInterval(
                    p10=float(row[5]),
                    p50=float(row[6]),
                    p90=float(row[7]),
                    selected_source=str(row[8]),
                    selected_name=str(row[9]),
                ),
                TARGET_GAMES_ACTIVE: ProjectionInterval(
                    p10=float(row[10]),
                    p50=float(row[11]),
                    p90=float(row[12]),
                    selected_source=str(row[13]),
                    selected_name=str(row[14]),
                ),
                TARGET_FANTASY_POINTS_TOTAL: ProjectionInterval(
                    p10=float(row[15]),
                    p50=float(row[16]),
                    p90=float(row[17]),
                    selected_source=str(row[18]),
                    selected_name=str(row[19]),
                ),
            },
            prediction_status=str(row[20]),
            explanation=_parse_json_object(row[21]),
        )
        for row in rows
    )


def _registered_files_match(project_root: Path, row: tuple[Any, ...]) -> bool:
    artifact_path, artifact_hash, artifact_size, card_path, card_hash = row
    return _registered_file_matches(
        project_root,
        str(artifact_path),
        str(artifact_hash),
        int(artifact_size),
    ) and _registered_file_matches(
        project_root,
        str(card_path),
        str(card_hash),
        None,
        canonical_text=True,
    )


def _registered_output_files_match(project_root: Path, run_payload: dict[str, Any]) -> bool:
    report_files = run_payload.get("report_files")
    registry = run_payload.get("registry")
    plot_files = run_payload.get("plot_files")
    if (
        not isinstance(report_files, dict)
        or not isinstance(registry, dict)
        or not isinstance(plot_files, dict)
        or not plot_files
    ):
        return False
    required = (
        (report_files.get("json_path"), report_files.get("json_sha256"), False),
        (report_files.get("markdown_path"), report_files.get("markdown_sha256"), True),
        (registry.get("path"), registry.get("sha256"), False),
    )
    required_files_match = all(
        path is not None
        and digest is not None
        and _registered_file_matches(
            project_root,
            str(path),
            str(digest),
            None,
            canonical_text=canonical_text,
        )
        for path, digest, canonical_text in required
    )
    plots_match = all(
        isinstance(metadata, dict)
        and metadata.get("path") is not None
        and metadata.get("sha256") is not None
        and _registered_file_matches(
            project_root,
            str(metadata["path"]),
            str(metadata["sha256"]),
            None,
        )
        for metadata in plot_files.values()
    )
    return required_files_match and plots_match


def _registered_file_matches(
    project_root: Path,
    registered_path: str,
    expected_hash: str,
    expected_size: int | None,
    *,
    canonical_text: bool = False,
) -> bool:
    candidate = Path(registered_path)
    if candidate.is_absolute():
        return False
    root = project_root.resolve()
    resolved = (root / candidate).resolve()
    try:
        resolved.relative_to(root)
    except ValueError:
        return False
    if not resolved.is_file():
        return False
    if expected_size is not None and resolved.stat().st_size != expected_size:
        return False
    digest = hashlib.sha256()
    if canonical_text:
        digest.update(resolved.read_bytes().replace(b"\r\n", b"\n").replace(b"\r", b"\n"))
    else:
        with resolved.open("rb") as handle:
            for chunk in iter(lambda: handle.read(1024 * 1024), b""):
                digest.update(chunk)
    return digest.hexdigest() == expected_hash


def _fetch_one_dict(
    connection: duckdb.DuckDBPyConnection,
    query: str,
    parameters: list[Any] | None = None,
) -> dict[str, Any] | None:
    cursor = connection.execute(query, parameters or [])
    row = cursor.fetchone()
    if row is None:
        return None
    columns = [str(column[0]) for column in cursor.description]
    return dict(zip(columns, row, strict=True))


def _scalar_int(
    connection: duckdb.DuckDBPyConnection,
    query: str,
    parameters: list[Any] | None = None,
) -> int:
    row = connection.execute(query, parameters or []).fetchone()
    if row is None:
        raise RuntimeError("DuckDB did not return the requested count.")
    return int(row[0])


def _parse_json_value(value: Any) -> Any:
    if isinstance(value, str):
        return json.loads(value)
    return value


def _parse_json_object(value: Any) -> dict[str, Any]:
    parsed = _parse_json_value(value)
    if not isinstance(parsed, dict):
        raise TypeError("The stored JSON payload must be an object.")
    return {str(key): item for key, item in parsed.items()}


def _json_datetime(value: Any) -> str:
    if isinstance(value, (date, datetime)):
        return value.isoformat()
    return str(value)


def _unavailable(
    code: str,
    message: str,
    *,
    run: ProjectionRun | None = None,
) -> ProjectionBoardStatus:
    return ProjectionBoardStatus(available=False, code=code, message=message, run=run)
