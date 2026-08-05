"""Evaluate transparent heuristics on expanding out-of-season folds."""

from __future__ import annotations

import hashlib
import json
import math
from collections import defaultdict
from dataclasses import dataclass
from pathlib import Path
from statistics import median
from typing import Any

import duckdb

from fantasy_draft_ai.config import AppConfig
from fantasy_draft_ai.data.warehouse import Warehouse
from fantasy_draft_ai.features.player_seasons import FEATURE_VERSION
from fantasy_draft_ai.models.evaluation.splits import expanding_season_splits
from fantasy_draft_ai.rules.models import LeagueRules

BASELINE_VERSION = "phase3-baselines-v1"
TARGETS = (
    "fantasy_points_per_game",
    "games_active",
    "fantasy_points_total",
)
BASELINES = (
    "previous_season",
    "weighted_history",
    "age_position_adjusted",
    "position_shrinkage",
    "weighted_components",
)


@dataclass(frozen=True)
class BaselineEvaluationResult:
    """Persisted predictions and their deterministic evaluation report."""

    committed: bool
    data_fingerprint: str
    prediction_rows: int
    evaluated_rows: int
    report_path: Path | None
    report: dict[str, Any]

    def render(self) -> str:
        status = "COMMITTED" if self.committed else "NOT COMMITTED"
        lines = [
            f"Phase 3 baseline evaluation: {self.report.get('status', 'FAILED')}",
            f"Warehouse transaction: {status}",
            f"Feature data fingerprint: {self.data_fingerprint or '<missing>'}",
            f"Prediction rows: {self.prediction_rows}",
            f"Evaluated rows: {self.evaluated_rows}",
        ]
        for issue in self.report.get("issues", []):
            lines.append(f"- {issue}")
        if self.report_path is not None:
            lines.append(f"Evaluation report: {self.report_path}")
        return "\n".join(lines)


@dataclass(frozen=True)
class JoinedRow:
    player_id: str
    prediction_season: int
    position: str
    features: dict[str, Any]
    targets: dict[str, Any] | None
    data_fingerprint: str
    target_fingerprint: str
    build_fingerprint: str
    scoring_fingerprint: str


@dataclass(frozen=True)
class PredictionRow:
    player_id: str
    prediction_season: int
    position: str
    target_name: str
    baseline_name: str
    predicted_value: float
    actual_value: float | None
    actual_games_active: float | None
    experience_group: str


def evaluate_baselines(
    config: AppConfig,
    rules: LeagueRules,
    *,
    first_evaluation_season: int | None = None,
    last_evaluation_season: int | None = None,
    output_path: Path | None = None,
    top_n: int = 12,
) -> BaselineEvaluationResult:
    """Evaluate baseline projections only after canonical features validate."""

    warehouse = Warehouse(config.resolve(config.paths.warehouse))
    if not warehouse.path.exists():
        return _failure("The canonical warehouse does not exist.")
    warehouse.initialize()
    try:
        with warehouse.connect(read_only=True) as connection:
            input_issues = _validate_feature_gate(connection, rules.fingerprint())
            if input_issues:
                return _failure(*input_issues)
            rows = _read_joined_rows(connection)
            feature_quality_warnings = _read_feature_quality_warnings(connection)
    except duckdb.Error as exc:
        return _failure(f"Could not read validated features: {exc}")
    if not rows:
        return _failure("No validated player-season feature rows are available.")

    data_fingerprint = rows[0].data_fingerprint
    target_fingerprint = rows[0].target_fingerprint
    build_fingerprint = rows[0].build_fingerprint
    target_seasons = sorted({row.prediction_season for row in rows if row.targets is not None})
    if len(target_seasons) < 2:
        return _failure("At least two completed target seasons are required.")
    default_first = max(config.training.start_season + 5, target_seasons[1])
    first = first_evaluation_season or default_first
    last = last_evaluation_season or min(config.training.end_season, target_seasons[-1])
    try:
        folds = expanding_season_splits(
            target_seasons,
            first_evaluation_season=first,
            last_evaluation_season=last,
            min_training_seasons=1,
        )
    except ValueError as exc:
        return _failure(str(exc))

    predictions = _make_predictions(rows)
    evaluation_seasons = {fold.evaluation_season for fold in folds}
    evaluation_candidates = [
        row for row in predictions if row.prediction_season in evaluation_seasons
    ]
    evaluated = [row for row in evaluation_candidates if row.actual_value is not None]
    metrics = _evaluate_metrics(evaluation_candidates, folds, top_n)
    evaluated_feature_keys = {
        (row.player_id, row.prediction_season)
        for row in rows
        if row.prediction_season in evaluation_seasons
    }
    fallback_feature_keys = {
        (row.player_id, row.prediction_season)
        for row in rows
        if row.prediction_season in evaluation_seasons
        and _experience_group(row.features) != "veteran"
    }
    report: dict[str, Any] = {
        "schema_version": "1.0",
        "status": "PASSED",
        "baseline_version": BASELINE_VERSION,
        "feature_version": FEATURE_VERSION,
        "feature_data_fingerprint": data_fingerprint,
        "target_data_fingerprint": target_fingerprint,
        "build_fingerprint": build_fingerprint,
        "scoring_ruleset_fingerprint": rules.fingerprint(),
        "split_strategy": "expanding_prediction_seasons",
        "folds": [
            {
                "training_seasons": list(fold.training_seasons),
                "evaluation_season": fold.evaluation_season,
                "label": fold.label,
            }
            for fold in folds
        ],
        "targets": list(TARGETS),
        "baselines": list(BASELINES),
        "prediction_rows": len(predictions),
        "evaluation_candidate_rows": len(evaluation_candidates),
        "evaluated_rows": len(evaluated),
        "excluded_missing_actual_rows": len(evaluation_candidates) - len(evaluated),
        "evaluated_player_seasons": len(evaluated_feature_keys),
        "fallback_player_seasons": len(fallback_feature_keys),
        "candidate_outcomes": _candidate_outcome_counts(evaluation_candidates, folds),
        "metrics": metrics,
        "unavailable_baselines": [
            {
                "name": "current_adp",
                "reason": (
                    "No cutoff-safe historical ADP archive exists for the expanding folds; "
                    "the current 2026 snapshot is not backfilled into the past."
                ),
            }
        ],
        "limitations": [
            "These are transparent heuristics, not a trained statistical or ML model.",
            "Games active use mapped positive snap-count participation, not roster status.",
            "Historical archive acquisition timestamps are provenance, not claimed cutoffs.",
            (
                "Rookies and players without history receive an explicit position prior "
                "only when their position is available before the prediction cutoff."
            ),
            (
                "The August 2026 identity snapshot predates the live 2026 cutoff; it is "
                "never backfilled into historical entry-cohort rows. Historical candidates "
                "without time-versioned preseason position evidence are excluded and counted."
            ),
            (
                "The four-year-history plus two-entry-cohort candidate universe is a "
                "cutoff-safe preseason proxy, not a historical roster or ADP list."
            ),
            (
                "All-candidate games-active metrics measure attrition; active-only "
                "segments describe projection error after a player records a game."
            ),
        ],
        "feature_quality_warnings": feature_quality_warnings,
        "issues": [
            (
                f"Upstream feature warning {warning['code']}: "
                f"{warning['message']} ({warning['count']})"
            )
            for warning in feature_quality_warnings
        ],
    }
    report_fingerprint = hashlib.sha256(_canonical_json(report).encode("utf-8")).hexdigest()
    report["report_fingerprint"] = report_fingerprint
    _commit_predictions(
        warehouse,
        predictions,
        data_fingerprint,
        target_fingerprint,
        build_fingerprint,
        rules.fingerprint(),
        report_fingerprint,
        report,
    )
    resolved_path = _write_report(config, output_path, report)
    return BaselineEvaluationResult(
        committed=True,
        data_fingerprint=data_fingerprint,
        prediction_rows=len(predictions),
        evaluated_rows=len(evaluated),
        report_path=resolved_path,
        report=report,
    )


def _failure(*issues: str) -> BaselineEvaluationResult:
    report: dict[str, Any] = {
        "schema_version": "1.0",
        "status": "FAILED",
        "issues": list(issues),
    }
    return BaselineEvaluationResult(False, "", 0, 0, None, report)


def _validate_feature_gate(
    connection: duckdb.DuckDBPyConnection, scoring_fingerprint: str
) -> list[str]:
    tables = {
        str(row[0])
        for row in connection.execute(
            "SELECT table_name FROM information_schema.tables WHERE table_schema = 'main'"
        ).fetchall()
    }
    required = {"player_season_features", "player_season_targets", "feature_build_metadata"}
    if missing := required - tables:
        return [f"Missing validated Phase 3 tables: {', '.join(sorted(missing))}."]
    summary = connection.execute(
        """
        SELECT
            count(*),
            count(DISTINCT data_fingerprint),
            count(*) FILTER (WHERE data_fingerprint IS NULL),
            count(*) FILTER (WHERE feature_season <> prediction_season - 1),
            count(*) FILTER (WHERE source_max_stat_season > feature_season),
            count(*) FILTER (WHERE scoring_ruleset_fingerprint IS DISTINCT FROM ?)
        FROM player_season_features
        WHERE source = 'nflverse'
        """,
        [scoring_fingerprint],
    ).fetchone()
    if summary is None or int(summary[0]) == 0:
        return ["No validated Phase 3 feature rows are available."]
    issues: list[str] = []
    if int(summary[1]) != 1:
        issues.append("The active feature table contains multiple data fingerprints.")
    if int(summary[2]):
        issues.append("The active feature table contains missing data fingerprints.")
    if int(summary[3]) or int(summary[4]):
        issues.append("The active feature table violates chronological isolation.")
    if int(summary[5]):
        issues.append("The feature scoring fingerprint does not match the requested rules.")
    fingerprint = connection.execute(
        "SELECT min(data_fingerprint) FROM player_season_features WHERE source = 'nflverse'"
    ).fetchone()
    metadata_count = connection.execute("SELECT count(*) FROM feature_build_metadata").fetchone()
    if metadata_count is None or int(metadata_count[0]) != 1:
        issues.append("Exactly one active feature-build metadata row is required.")
    if fingerprint is None:
        issues.append("The active feature data fingerprint is missing.")
    else:
        metadata = connection.execute(
            """
            SELECT
                target_data_fingerprint,
                build_fingerprint,
                quality_payload,
                feature_rows,
                target_rows,
                scoring_ruleset_fingerprint
            FROM feature_build_metadata
            WHERE data_fingerprint = ?
            """,
            [fingerprint[0]],
        ).fetchone()
        if metadata is None:
            issues.append("No feature validation metadata matches the active fingerprint.")
        else:
            target_summary = connection.execute(
                """
                SELECT
                    count(*),
                    count(*) FILTER (
                        WHERE data_fingerprint IS DISTINCT FROM ?
                           OR target_data_fingerprint IS DISTINCT FROM ?
                           OR scoring_ruleset_fingerprint IS DISTINCT FROM ?
                    )
                FROM player_season_targets
                WHERE source = 'nflverse'
                """,
                [fingerprint[0], metadata[0], scoring_fingerprint],
            ).fetchone()
            expected_build_fingerprint = _build_fingerprint(
                str(fingerprint[0]), str(metadata[0]), scoring_fingerprint
            )
            if str(metadata[1]) != expected_build_fingerprint:
                issues.append("The active feature/target build fingerprint is inconsistent.")
            if str(metadata[5]) != scoring_fingerprint:
                issues.append("Feature metadata uses a different scoring ruleset.")
            if int(metadata[3]) != int(summary[0]):
                issues.append("Feature metadata row accounting is stale.")
            if (
                target_summary is None
                or int(target_summary[0]) != int(metadata[4])
                or int(target_summary[1])
            ):
                issues.append("Targets do not match the active validated feature build.")
            quality = json.loads(str(metadata[2]))
            fatal = [
                issue for issue in quality.get("issues", []) if issue.get("severity") == "fatal"
            ]
            if fatal:
                issues.append("The active feature validation metadata contains fatal issues.")
    return issues


def _read_feature_quality_warnings(
    connection: duckdb.DuckDBPyConnection,
) -> list[dict[str, Any]]:
    row = connection.execute(
        """
        SELECT quality_payload
        FROM feature_build_metadata
        ORDER BY source_max_as_of DESC, data_fingerprint
        LIMIT 1
        """
    ).fetchone()
    if row is None:
        return []
    quality = json.loads(str(row[0]))
    return [
        {
            "code": str(issue.get("code", "unknown")),
            "message": str(issue.get("message", "")),
            "count": int(issue.get("count", 0)),
            "severity": str(issue.get("severity", "warning")),
        }
        for issue in quality.get("issues", [])
        if issue.get("severity") == "warning"
    ]


def _read_joined_rows(connection: duckdb.DuckDBPyConnection) -> list[JoinedRow]:
    rows = connection.execute(
        """
        SELECT
            feature.player_id,
            feature.prediction_season,
            feature.position,
            feature.feature_payload,
            target.target_payload,
            feature.data_fingerprint,
            metadata.target_data_fingerprint,
            metadata.build_fingerprint,
            feature.scoring_ruleset_fingerprint
        FROM player_season_features AS feature
        JOIN feature_build_metadata AS metadata
          ON feature.data_fingerprint = metadata.data_fingerprint
        LEFT JOIN player_season_targets AS target
          ON feature.player_id = target.player_id
         AND feature.prediction_season = target.prediction_season
         AND feature.data_fingerprint = target.data_fingerprint
         AND metadata.target_data_fingerprint = target.target_data_fingerprint
        WHERE feature.source = 'nflverse'
        ORDER BY feature.prediction_season, feature.position, feature.player_id
        """
    ).fetchall()
    return [
        JoinedRow(
            player_id=str(row[0]),
            prediction_season=int(row[1]),
            position=str(row[2]),
            features=json.loads(str(row[3])),
            targets=json.loads(str(row[4])) if row[4] is not None else None,
            data_fingerprint=str(row[5]),
            target_fingerprint=str(row[6]),
            build_fingerprint=str(row[7]),
            scoring_fingerprint=str(row[8]),
        )
        for row in rows
    ]


def _make_predictions(rows: list[JoinedRow]) -> list[PredictionRow]:
    predictions: list[PredictionRow] = []
    for row in rows:
        experience_group = _experience_group(row.features)
        actuals = row.targets or {}
        for baseline in BASELINES:
            ppg, games = _baseline_components(row.features, baseline)
            values = {
                "fantasy_points_per_game": ppg,
                "games_active": games,
                "fantasy_points_total": ppg * games,
            }
            for target_name, predicted in values.items():
                actual = actuals.get(target_name)
                predictions.append(
                    PredictionRow(
                        player_id=row.player_id,
                        prediction_season=row.prediction_season,
                        position=row.position,
                        target_name=target_name,
                        baseline_name=baseline,
                        predicted_value=float(predicted),
                        actual_value=float(actual) if actual is not None else None,
                        actual_games_active=(
                            float(actuals["games_active"])
                            if actuals.get("games_active") is not None
                            else None
                        ),
                        experience_group=experience_group,
                    )
                )
    return predictions


def _baseline_components(features: dict[str, Any], baseline: str) -> tuple[float, float]:
    ppg_keys = {
        "previous_season": "baseline_previous_fantasy_points_per_game",
        "weighted_history": "baseline_weighted_fantasy_points_per_game",
        "age_position_adjusted": "baseline_age_adjusted_fantasy_points_per_game",
        "position_shrinkage": "baseline_shrinkage_fantasy_points_per_game",
        "weighted_components": "baseline_components_fantasy_points_per_game",
    }
    games_keys = {
        "previous_season": "baseline_previous_games_active",
        "weighted_history": "baseline_weighted_games_active",
        "age_position_adjusted": "baseline_weighted_games_active",
        "position_shrinkage": "baseline_shrinkage_games_active",
        "weighted_components": "baseline_weighted_games_active",
    }
    return float(features[ppg_keys[baseline]]), float(features[games_keys[baseline]])


def _experience_group(features: dict[str, Any]) -> str:
    if bool(features.get("is_rookie")):
        return "rookie"
    return "sparse" if int(features.get("history_seasons", 0)) < 2 else "veteran"


def _evaluate_metrics(
    predictions: list[PredictionRow], folds: tuple[Any, ...], top_n: int
) -> list[dict[str, Any]]:
    metrics: list[dict[str, Any]] = []
    fold_lookup = {fold.evaluation_season: fold.label for fold in folds}
    for season in sorted(fold_lookup):
        fold_rows = [row for row in predictions if row.prediction_season == season]
        metrics.extend(_metric_groups(fold_rows, season, fold_lookup[season], top_n))
    metrics.extend(_metric_groups(predictions, None, "aggregate", top_n))
    return metrics


def _candidate_outcome_counts(
    predictions: list[PredictionRow], folds: tuple[Any, ...]
) -> list[dict[str, Any]]:
    canonical_rows = [
        row
        for row in predictions
        if row.target_name == "games_active" and row.baseline_name == BASELINES[0]
    ]
    fold_lookup = {fold.evaluation_season: fold.label for fold in folds}
    groups: list[tuple[int | None, str, list[PredictionRow]]] = [
        (
            season,
            fold_lookup[season],
            [row for row in canonical_rows if row.prediction_season == season],
        )
        for season in sorted(fold_lookup)
    ]
    groups.append((None, "aggregate", canonical_rows))
    output: list[dict[str, Any]] = []
    for season, label, rows in groups:
        for position in ["ALL", *sorted({row.position for row in rows})]:
            segment = (
                rows if position == "ALL" else [row for row in rows if row.position == position]
            )
            output.append(
                {
                    "evaluation_season": season,
                    "fold_label": label,
                    "position": position,
                    "candidate_rows": len(segment),
                    "positive_game_rows": sum(
                        row.actual_games_active is not None and row.actual_games_active > 0
                        for row in segment
                    ),
                    "zero_game_rows": sum(row.actual_games_active == 0 for row in segment),
                    "missing_games_active_rows": sum(
                        row.actual_games_active is None for row in segment
                    ),
                }
            )
    return output


def _metric_groups(
    rows: list[PredictionRow],
    evaluation_season: int | None,
    fold_label: str,
    top_n: int,
) -> list[dict[str, Any]]:
    output: list[dict[str, Any]] = []
    for target in TARGETS:
        for baseline in BASELINES:
            base = [
                row
                for row in rows
                if row.target_name == target
                and row.baseline_name == baseline
                and row.actual_value is not None
            ]
            if not base:
                continue
            output.append(
                _metric_record(
                    base,
                    evaluation_season,
                    fold_label,
                    target,
                    baseline,
                    "overall",
                    "all",
                    top_n,
                )
            )
            active = [
                row
                for row in base
                if row.actual_games_active is not None and row.actual_games_active > 0
            ]
            if active:
                output.append(
                    _metric_record(
                        active,
                        evaluation_season,
                        fold_label,
                        target,
                        baseline,
                        "active_only",
                        "positive_games",
                        top_n,
                    )
                )
            for position in sorted({row.position for row in base}):
                group = [row for row in base if row.position == position]
                output.append(
                    _metric_record(
                        group,
                        evaluation_season,
                        fold_label,
                        target,
                        baseline,
                        "position",
                        position,
                        top_n,
                    )
                )
                active_position = [
                    row
                    for row in group
                    if row.actual_games_active is not None and row.actual_games_active > 0
                ]
                if active_position:
                    output.append(
                        _metric_record(
                            active_position,
                            evaluation_season,
                            fold_label,
                            target,
                            baseline,
                            "active_position",
                            position,
                            top_n,
                        )
                    )
            for experience in ("rookie", "sparse", "veteran"):
                group = [row for row in base if row.experience_group == experience]
                if group:
                    output.append(
                        _metric_record(
                            group,
                            evaluation_season,
                            fold_label,
                            target,
                            baseline,
                            "experience",
                            experience,
                            top_n,
                        )
                    )
            tiers = _projection_tiers(base)
            for tier in ("top", "middle", "lower"):
                group = [
                    row
                    for row in base
                    if tiers[row.player_id, row.position, row.prediction_season] == tier
                ]
                if group:
                    output.append(
                        _metric_record(
                            group,
                            evaluation_season,
                            fold_label,
                            target,
                            baseline,
                            "projection_tier",
                            tier,
                            top_n,
                        )
                    )
    return output


def _metric_record(
    rows: list[PredictionRow],
    evaluation_season: int | None,
    fold_label: str,
    target: str,
    baseline: str,
    scope: str,
    segment: str,
    top_n: int,
) -> dict[str, Any]:
    predicted = [row.predicted_value for row in rows]
    actual = [float(row.actual_value) for row in rows if row.actual_value is not None]
    errors = [prediction - outcome for prediction, outcome in zip(predicted, actual, strict=True)]
    absolute = [abs(error) for error in errors]
    overlap = _top_n_overlap(rows, top_n) if scope in {"position", "active_position"} else None
    return {
        "evaluation_season": evaluation_season,
        "fold_label": fold_label,
        "target": target,
        "baseline": baseline,
        "scope": scope,
        "segment": segment,
        "rows": len(rows),
        "mae": _round(sum(absolute) / len(absolute)),
        "rmse": _round(math.sqrt(sum(error * error for error in errors) / len(errors))),
        "median_absolute_error": _round(float(median(absolute))),
        "spearman_rank_correlation": _round_or_none(_spearman(predicted, actual)),
        "top_n_overlap": _round_or_none(overlap),
        "top_n": min(top_n, len(rows)) if scope == "position" else None,
    }


def _projection_tiers(
    rows: list[PredictionRow],
) -> dict[tuple[str, str, int], str]:
    groups: dict[tuple[int, str], list[PredictionRow]] = defaultdict(list)
    for row in rows:
        groups[row.prediction_season, row.position].append(row)
    tiers: dict[tuple[str, str, int], str] = {}
    for (prediction_season, position), group in groups.items():
        ordered = sorted(group, key=lambda row: (-row.predicted_value, row.player_id))
        for index, row in enumerate(ordered):
            percentile = (index + 0.5) / len(ordered)
            tier = "top" if percentile <= 0.25 else "lower" if percentile > 0.75 else "middle"
            tiers[row.player_id, position, prediction_season] = tier
    return tiers


def _top_n_overlap(rows: list[PredictionRow], top_n: int) -> float:
    count = min(top_n, len(rows))
    predicted = {
        row.player_id
        for row in sorted(rows, key=lambda item: (-item.predicted_value, item.player_id))[:count]
    }
    actual = {
        row.player_id
        for row in sorted(
            rows,
            key=lambda item: (
                -float(item.actual_value) if item.actual_value is not None else 0.0,
                item.player_id,
            ),
        )[:count]
    }
    return len(predicted & actual) / count if count else 0.0


def _spearman(predicted: list[float], actual: list[float]) -> float | None:
    if len(predicted) < 2:
        return None
    predicted_ranks = _average_ranks(predicted)
    actual_ranks = _average_ranks(actual)
    mean_predicted = sum(predicted_ranks) / len(predicted_ranks)
    mean_actual = sum(actual_ranks) / len(actual_ranks)
    numerator = sum(
        (left - mean_predicted) * (right - mean_actual)
        for left, right in zip(predicted_ranks, actual_ranks, strict=True)
    )
    left_scale = math.sqrt(sum((value - mean_predicted) ** 2 for value in predicted_ranks))
    right_scale = math.sqrt(sum((value - mean_actual) ** 2 for value in actual_ranks))
    if left_scale == 0 or right_scale == 0:
        return None
    return numerator / (left_scale * right_scale)


def _average_ranks(values: list[float]) -> list[float]:
    indexed = sorted(enumerate(values), key=lambda item: (item[1], item[0]))
    ranks = [0.0] * len(values)
    index = 0
    while index < len(indexed):
        end = index + 1
        while end < len(indexed) and indexed[end][1] == indexed[index][1]:
            end += 1
        average = (index + 1 + end) / 2
        for original, _ in indexed[index:end]:
            ranks[original] = average
        index = end
    return ranks


def _commit_predictions(
    warehouse: Warehouse,
    predictions: list[PredictionRow],
    data_fingerprint: str,
    target_fingerprint: str,
    build_fingerprint: str,
    scoring_fingerprint: str,
    report_fingerprint: str,
    report: dict[str, Any],
) -> None:
    with warehouse.connect() as connection:
        _ensure_baseline_schema(connection)
        connection.execute("BEGIN TRANSACTION")
        try:
            connection.execute("DELETE FROM baseline_predictions")
            connection.executemany(
                """
                INSERT INTO baseline_predictions (
                    player_id, prediction_season, position, target_name, baseline_name,
                    predicted_value, actual_value, experience_group, baseline_version,
                    feature_data_fingerprint, target_data_fingerprint,
                    build_fingerprint, scoring_ruleset_fingerprint
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                [
                    (
                        row.player_id,
                        row.prediction_season,
                        row.position,
                        row.target_name,
                        row.baseline_name,
                        row.predicted_value,
                        row.actual_value,
                        row.experience_group,
                        BASELINE_VERSION,
                        data_fingerprint,
                        target_fingerprint,
                        build_fingerprint,
                        scoring_fingerprint,
                    )
                    for row in predictions
                ],
            )
            connection.execute(
                """
                DELETE FROM baseline_evaluation_metadata
                WHERE report_fingerprint <> ?
                """,
                [
                    report_fingerprint,
                ],
            )
            connection.execute(
                """
                INSERT INTO baseline_evaluation_metadata (
                    report_fingerprint, baseline_version, feature_data_fingerprint,
                    target_data_fingerprint, build_fingerprint,
                    scoring_ruleset_fingerprint, prediction_rows, evaluated_rows,
                    report_payload
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT (report_fingerprint) DO UPDATE SET
                    prediction_rows = excluded.prediction_rows,
                    evaluated_rows = excluded.evaluated_rows,
                    report_payload = excluded.report_payload
                """,
                [
                    report_fingerprint,
                    BASELINE_VERSION,
                    data_fingerprint,
                    target_fingerprint,
                    build_fingerprint,
                    scoring_fingerprint,
                    len(predictions),
                    int(report["evaluated_rows"]),
                    _canonical_json(report),
                ],
            )
            actual = connection.execute("SELECT count(*) FROM baseline_predictions").fetchone()
            if actual is None or int(actual[0]) != len(predictions):
                raise RuntimeError("Baseline prediction row accounting failed.")
            connection.execute("COMMIT")
        except Exception:
            connection.execute("ROLLBACK")
            raise


def _ensure_baseline_schema(connection: duckdb.DuckDBPyConnection) -> None:
    connection.execute(
        """
        CREATE TABLE IF NOT EXISTS baseline_predictions (
            player_id VARCHAR NOT NULL,
            prediction_season INTEGER NOT NULL,
            position VARCHAR NOT NULL,
            target_name VARCHAR NOT NULL,
            baseline_name VARCHAR NOT NULL,
            predicted_value DOUBLE NOT NULL,
            actual_value DOUBLE,
            experience_group VARCHAR NOT NULL,
            baseline_version VARCHAR NOT NULL,
            feature_data_fingerprint VARCHAR NOT NULL,
            target_data_fingerprint VARCHAR NOT NULL,
            build_fingerprint VARCHAR NOT NULL,
            scoring_ruleset_fingerprint VARCHAR NOT NULL,
            PRIMARY KEY (player_id, prediction_season, target_name, baseline_name)
        );

        CREATE TABLE IF NOT EXISTS baseline_evaluation_metadata (
            report_fingerprint VARCHAR PRIMARY KEY,
            baseline_version VARCHAR NOT NULL,
            feature_data_fingerprint VARCHAR NOT NULL,
            target_data_fingerprint VARCHAR NOT NULL,
            build_fingerprint VARCHAR NOT NULL,
            scoring_ruleset_fingerprint VARCHAR NOT NULL,
            prediction_rows INTEGER NOT NULL,
            evaluated_rows INTEGER NOT NULL,
            report_payload JSON NOT NULL
        );

        ALTER TABLE baseline_predictions ADD COLUMN IF NOT EXISTS
            target_data_fingerprint VARCHAR;
        ALTER TABLE baseline_predictions ADD COLUMN IF NOT EXISTS
            build_fingerprint VARCHAR;
        ALTER TABLE baseline_evaluation_metadata ADD COLUMN IF NOT EXISTS
            target_data_fingerprint VARCHAR;
        ALTER TABLE baseline_evaluation_metadata ADD COLUMN IF NOT EXISTS
            build_fingerprint VARCHAR;
        """
    )


def _write_report(config: AppConfig, output_path: Path | None, report: dict[str, Any]) -> Path:
    path = output_path or config.project_root / "models/reports/phase3_baselines.json"
    if not path.is_absolute():
        path = config.project_root / path
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.suffix.lower() == ".md":
        path.write_text(_render_markdown(report), encoding="utf-8")
        json_path = path.with_suffix(".json")
        json_path.write_text(_canonical_json(report, indent=2) + "\n", encoding="utf-8")
    else:
        path.write_text(_canonical_json(report, indent=2) + "\n", encoding="utf-8")
        markdown_path = path.with_suffix(".md")
        markdown_path.write_text(_render_markdown(report), encoding="utf-8")
    return path.resolve()


def _render_markdown(report: dict[str, Any]) -> str:
    lines = [
        "# Phase 3 Transparent Baseline Evaluation",
        "",
        f"Status: **{report['status']}**",
        "",
        f"Feature fingerprint: `{report['feature_data_fingerprint']}`",
        "",
        f"Target fingerprint: `{report['target_data_fingerprint']}`",
        "",
        f"Build fingerprint: `{report['build_fingerprint']}`",
        "",
        f"Prediction rows: {report['prediction_rows']:,}",
        "",
        f"Evaluated rows: {report['evaluated_rows']:,}",
        "",
        f"Rows excluded for unavailable actuals: {report['excluded_missing_actual_rows']:,}",
        "",
        f"Sparse/entry fallback player-seasons: {report['fallback_player_seasons']:,}",
        "",
        "## Chronological folds",
        "",
        "| Label | Training prediction seasons | Evaluation season |",
        "|---|---|---|",
    ]
    for fold in report["folds"]:
        training = fold["training_seasons"]
        lines.append(
            f"| {fold['label']} | {training[0]}-{training[-1]} | {fold['evaluation_season']} |"
        )
    lines.extend(
        [
            "",
            "## Candidate outcome availability",
            "",
            "| Position | Candidates | Positive games | Zero games | Missing games |",
            "|---|---:|---:|---:|---:|",
        ]
    )
    for row in report["candidate_outcomes"]:
        if row["fold_label"] == "aggregate":
            lines.append(
                f"| {row['position']} | {row['candidate_rows']} | "
                f"{row['positive_game_rows']} | {row['zero_game_rows']} | "
                f"{row['missing_games_active_rows']} |"
            )
    lines.extend(
        [
            "",
            "## Aggregate metrics",
            "",
            "| Target | Baseline | Rows | MAE | RMSE | Median AE | Spearman |",
            "|---|---|---:|---:|---:|---:|---:|",
        ]
    )
    aggregate = [
        row
        for row in report["metrics"]
        if row["fold_label"] == "aggregate" and row["scope"] == "overall"
    ]
    for row in aggregate:
        spearman = row["spearman_rank_correlation"]
        lines.append(
            f"| {row['target']} | {row['baseline']} | {row['rows']} | "
            f"{row['mae']:.3f} | {row['rmse']:.3f} | "
            f"{row['median_absolute_error']:.3f} | "
            f"{spearman if spearman is not None else 'n/a'} |"
        )
    lines.extend(
        [
            "",
            "## Positive-game aggregate metrics",
            "",
            "This diagnostic conditions on recording at least one active game; "
            "candidate selection itself never uses the outcome.",
            "",
            "| Target | Baseline | Rows | MAE | RMSE | Median AE | Spearman |",
            "|---|---|---:|---:|---:|---:|---:|",
        ]
    )
    active_aggregate = [
        row
        for row in report["metrics"]
        if row["fold_label"] == "aggregate" and row["scope"] == "active_only"
    ]
    for row in active_aggregate:
        spearman = row["spearman_rank_correlation"]
        lines.append(
            f"| {row['target']} | {row['baseline']} | {row['rows']} | "
            f"{row['mae']:.3f} | {row['rmse']:.3f} | "
            f"{row['median_absolute_error']:.3f} | "
            f"{spearman if spearman is not None else 'n/a'} |"
        )
    lines.extend(["", "## Honest limitations", ""])
    lines.extend(f"- {limitation}" for limitation in report["limitations"])
    if report["feature_quality_warnings"]:
        lines.extend(["", "## Upstream feature-quality warnings", ""])
        lines.extend(
            f"- **{warning['code']}** ({warning['count']}): {warning['message']}"
            for warning in report["feature_quality_warnings"]
        )
    lines.extend(["", "## Unavailable comparison", ""])
    lines.extend(
        f"- **{item['name']}**: {item['reason']}" for item in report["unavailable_baselines"]
    )
    return "\n".join(lines) + "\n"


def _round(value: float) -> float:
    return round(value, 6)


def _round_or_none(value: float | None) -> float | None:
    return None if value is None else _round(value)


def _canonical_json(value: object, *, indent: int | None = None) -> str:
    return json.dumps(
        value,
        sort_keys=True,
        separators=(",", ":") if indent is None else None,
        ensure_ascii=True,
        allow_nan=False,
        indent=indent,
    )


def _build_fingerprint(
    feature_fingerprint: str,
    target_fingerprint: str,
    scoring_fingerprint: str,
) -> str:
    payload = {
        "feature_data_fingerprint": feature_fingerprint,
        "target_data_fingerprint": target_fingerprint,
        "feature_version": FEATURE_VERSION,
        "scoring_ruleset_fingerprint": scoring_fingerprint,
    }
    return hashlib.sha256(_canonical_json(payload).encode("utf-8")).hexdigest()
