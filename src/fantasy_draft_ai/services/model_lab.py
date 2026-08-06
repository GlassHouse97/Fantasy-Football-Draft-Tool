"""Read-only Phase 7 service boundary for validated model-learning artifacts."""

from __future__ import annotations

import json
import math
from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from pathlib import Path
from typing import Any, TypeAlias

import duckdb

from fantasy_draft_ai.config import AppConfig
from fantasy_draft_ai.models.player_projection.config import (
    DEFAULT_CATEGORICAL_FEATURES,
    DEFAULT_NUMERIC_FEATURES,
)
from fantasy_draft_ai.services.projections import (
    PROJECTION_TARGETS,
    TARGET_FANTASY_POINTS_PER_GAME,
    TARGET_FANTASY_POINTS_TOTAL,
    TARGET_GAMES_ACTIVE,
    ProjectionBoard,
    load_projection_board,
)

JsonScalar: TypeAlias = str | int | float | bool | None

_TARGET_DEFINITIONS = {
    TARGET_FANTASY_POINTS_PER_GAME: (
        "Fantasy points per game",
        "points per active game",
        "Scoring-rules fantasy points divided by games active in the prediction season.",
    ),
    TARGET_GAMES_ACTIVE: (
        "Games active",
        "games",
        "Regular-season games in which the player was active.",
    ),
    TARGET_FANTASY_POINTS_TOTAL: (
        "Season fantasy points",
        "points",
        "Total scoring-rules fantasy points in the prediction season.",
    ),
}


@dataclass(frozen=True)
class ModelLabStatus:
    available: bool
    code: str
    message: str


@dataclass(frozen=True)
class TargetDefinition:
    name: str
    label: str
    unit: str
    description: str

    def as_dict(self) -> dict[str, object]:
        return {
            "name": self.name,
            "label": self.label,
            "unit": self.unit,
            "description": self.description,
        }


@dataclass(frozen=True)
class FeatureDefinition:
    name: str
    label: str
    feature_type: str
    history_window: str
    description: str

    def as_dict(self) -> dict[str, object]:
        return {
            "name": self.name,
            "label": self.label,
            "feature_type": self.feature_type,
            "history_window": self.history_window,
            "description": self.description,
        }


@dataclass(frozen=True)
class ChronologicalFoldSummary:
    label: str
    evaluation_season: int
    training_seasons: tuple[int, ...]

    @property
    def training_max_season(self) -> int | None:
        return max(self.training_seasons) if self.training_seasons else None

    @property
    def leakage_safe(self) -> bool:
        return bool(
            self.training_seasons
            and self.training_max_season is not None
            and self.training_max_season < self.evaluation_season
        )

    def as_dict(self) -> dict[str, object]:
        return {
            "label": self.label,
            "evaluation_season": self.evaluation_season,
            "training_seasons": list(self.training_seasons),
            "training_max_season": self.training_max_season,
            "leakage_safe": self.leakage_safe,
        }


@dataclass(frozen=True)
class MetricSummary:
    phase: str
    candidate_name: str
    candidate_source: str
    target_name: str
    position: str
    evaluation_scope: str
    evaluation_seasons: tuple[int, ...]
    segment: str
    rows: int
    mae: float | None
    rmse: float | None
    median_absolute_error: float | None
    spearman_rank_correlation: float | None
    top_n_capture_rate: float | None

    def as_dict(self) -> dict[str, object]:
        return {
            "phase": self.phase,
            "candidate_name": self.candidate_name,
            "candidate_source": self.candidate_source,
            "target_name": self.target_name,
            "position": self.position,
            "evaluation_scope": self.evaluation_scope,
            "evaluation_seasons": list(self.evaluation_seasons),
            "segment": self.segment,
            "rows": self.rows,
            "mae": self.mae,
            "rmse": self.rmse,
            "median_absolute_error": self.median_absolute_error,
            "spearman_rank_correlation": self.spearman_rank_correlation,
            "top_n_capture_rate": self.top_n_capture_rate,
        }


@dataclass(frozen=True)
class ChampionSelectionSummary:
    position: str
    target_name: str
    selected_source: str
    selected_name: str
    selection_metric: str
    selection_value: float
    reference_baseline_name: str
    reference_baseline_value: float
    improvement: float
    decision_status: str


@dataclass(frozen=True)
class ResidualSummary:
    """Grouped signed residuals where positive values mean underprediction."""

    model_family: str
    position: str
    target_name: str
    prediction_scope: str
    prediction_season: int
    rows: int
    mean_actual_minus_prediction: float
    mae: float
    rmse: float


@dataclass(frozen=True)
class FeatureImportanceSummary:
    position: str
    target_name: str
    model_family: str
    feature: str
    rank: int
    importance_mean: float
    importance_std: float | None
    signed_value: float | None
    direction: str
    method: str
    scope: str
    interpretation: str


@dataclass(frozen=True)
class ModelCardReference:
    model_id: str
    model_family: str
    position: str
    target_name: str
    relative_path: str
    absolute_path: Path
    exists: bool


@dataclass(frozen=True)
class DiagnosticReference:
    name: str
    relative_path: str
    absolute_path: Path
    exists: bool


@dataclass(frozen=True)
class PlayerOption:
    player_id: str
    display_name: str
    position: str
    prediction_status: str


@dataclass(frozen=True)
class ExplanationFactor:
    rank: int
    feature: str
    direction: str
    player_value: JsonScalar
    reference_value: JsonScalar
    prediction_delta: float | None


@dataclass(frozen=True)
class ExplanationValue:
    name: str
    value: JsonScalar


@dataclass(frozen=True)
class PlayerModelExplanation:
    available: bool
    code: str
    message: str
    player_id: str
    display_name: str
    position: str
    target_name: str
    prediction_status: str
    method_label: str
    p10: float | None
    p50: float | None
    p90: float | None
    explanation_type: str
    interpretation: str
    reason: str
    learned_model_used: bool
    factors: tuple[ExplanationFactor, ...]
    supporting_values: tuple[ExplanationValue, ...]


@dataclass(frozen=True)
class ModelLabSnapshot:
    """Complete immutable read model for the Phase 7 Model Lab page."""

    status: ModelLabStatus
    run_id: str | None
    targets: tuple[TargetDefinition, ...]
    features: tuple[FeatureDefinition, ...]
    folds: tuple[ChronologicalFoldSummary, ...]
    baseline_metrics: tuple[MetricSummary, ...]
    model_metrics: tuple[MetricSummary, ...]
    selections: tuple[ChampionSelectionSummary, ...]
    residuals: tuple[ResidualSummary, ...]
    feature_importance: tuple[FeatureImportanceSummary, ...]
    model_cards: tuple[ModelCardReference, ...]
    diagnostics: tuple[DiagnosticReference, ...]
    players: tuple[PlayerOption, ...]
    limitations: tuple[str, ...]

    @property
    def available(self) -> bool:
        return self.status.available


def load_model_lab(config: AppConfig) -> ModelLabSnapshot:
    """Read validated Phase 3/4 reports and diagnostics without training models."""

    targets = _target_definitions()
    default_features = _feature_definitions(
        DEFAULT_NUMERIC_FEATURES,
        DEFAULT_CATEGORICAL_FEATURES,
    )
    board = load_projection_board(config)
    if not board.available or board.run is None:
        return _empty_snapshot(
            status=ModelLabStatus(False, board.status.code, board.status.message),
            targets=targets,
            features=default_features,
        )

    warehouse = config.resolve(config.paths.warehouse)
    try:
        with duckdb.connect(str(warehouse), read_only=True) as connection:
            phase3_value = connection.execute(
                "SELECT report_payload FROM baseline_evaluation_metadata "
                "WHERE report_fingerprint = ?",
                [board.run.lineage.baseline_report_fingerprint],
            ).fetchone()
            phase4_value = connection.execute(
                "SELECT report_payload FROM player_projection_evaluation_metadata WHERE run_id = ?",
                [board.run.run_id],
            ).fetchone()
            if phase3_value is None or phase4_value is None:
                return _empty_snapshot(
                    status=ModelLabStatus(
                        False,
                        "missing_report",
                        "Validated model metadata is missing a Phase 3 or Phase 4 report.",
                    ),
                    targets=targets,
                    features=default_features,
                )
            phase3 = _json_object(phase3_value[0])
            phase4 = _json_object(phase4_value[0])
            residuals = _load_residual_summaries(connection, board.run.run_id)
            cards = _load_model_cards(connection, config.project_root, board.run.run_id)
    except (duckdb.Error, OSError, TypeError, ValueError, json.JSONDecodeError) as exc:
        return _empty_snapshot(
            status=ModelLabStatus(
                False,
                "unreadable",
                f"Validated model artifacts could not be read safely: {exc}",
            ),
            targets=targets,
            features=default_features,
        )

    feature_contract = phase4.get("feature_contract")
    if isinstance(feature_contract, Mapping):
        numeric = _string_tuple(feature_contract.get("numeric_features"))
        categorical = _string_tuple(feature_contract.get("categorical_features"))
        features = _feature_definitions(numeric, categorical)
    else:
        features = default_features
    folds = _parse_folds(phase4.get("folds"))
    if not folds or not all(fold.leakage_safe for fold in folds):
        return _empty_snapshot(
            status=ModelLabStatus(
                False,
                "invalid_splits",
                "Chronological model splits are missing or fail the "
                "training-before-evaluation gate.",
            ),
            targets=targets,
            features=features,
        )

    return ModelLabSnapshot(
        status=ModelLabStatus(
            True,
            "available",
            f"Validated read-only model run {board.run.run_id[:12]} is available.",
        ),
        run_id=board.run.run_id,
        targets=targets,
        features=features,
        folds=folds,
        baseline_metrics=_parse_baseline_metrics(phase3.get("metrics")),
        model_metrics=_parse_model_metrics(phase4.get("detailed_metrics")),
        selections=_parse_selections(phase4.get("champions")),
        residuals=residuals,
        feature_importance=_parse_feature_importance(phase4.get("global_explanations")),
        model_cards=cards,
        diagnostics=_parse_diagnostics(
            config.project_root,
            phase4.get("diagnostic_plots", phase4.get("diagnostics")),
        ),
        players=tuple(
            PlayerOption(
                row.player_id,
                row.display_name,
                row.position,
                row.prediction_status,
            )
            for row in board.rows
        ),
        limitations=_string_tuple(phase4.get("limitations")),
    )


def load_player_model_explanation(
    config: AppConfig,
    player_id: str,
    target_name: str,
) -> PlayerModelExplanation:
    """Return one served prediction explanation without loading a model artifact."""

    normalized_id = player_id.strip()
    if not normalized_id:
        raise ValueError("player_id cannot be blank.")
    if target_name not in PROJECTION_TARGETS:
        raise ValueError(f"Unsupported projection target: {target_name}.")
    board = load_projection_board(config)
    if not board.available:
        return _unavailable_player_explanation(
            board,
            normalized_id,
            target_name,
            board.status.code,
            board.status.message,
        )
    player = next((row for row in board.rows if row.player_id == normalized_id), None)
    if player is None:
        return _unavailable_player_explanation(
            board,
            normalized_id,
            target_name,
            "player_not_found",
            "The canonical player ID is not present in the validated projection board.",
        )
    interval = player.target(target_name)
    payload = player.explanation_for(target_name)
    factors = _parse_player_factors(payload.get("top_factors"))
    supporting = _parse_supporting_values(payload.get("supporting_values"))
    interpretation = _optional_string(payload.get("interpretation"))
    reason = _optional_string(payload.get("reason"))
    return PlayerModelExplanation(
        available=True,
        code="available",
        message="Validated served explanation available.",
        player_id=player.player_id,
        display_name=player.display_name,
        position=player.position,
        target_name=target_name,
        prediction_status=player.prediction_status,
        method_label=interval.method_label(player.prediction_status),
        p10=interval.p10,
        p50=interval.p50,
        p90=interval.p90,
        explanation_type=_optional_string(payload.get("explanation_type")),
        interpretation=interpretation,
        reason=reason,
        learned_model_used=bool(payload.get("learned_model_used", factors)),
        factors=factors,
        supporting_values=supporting,
    )


def _target_definitions() -> tuple[TargetDefinition, ...]:
    return tuple(TargetDefinition(name, *_TARGET_DEFINITIONS[name]) for name in PROJECTION_TARGETS)


def _feature_definitions(
    numeric: Sequence[str], categorical: Sequence[str]
) -> tuple[FeatureDefinition, ...]:
    records = [
        FeatureDefinition(
            name=name,
            label=name.replace("_", " ").title(),
            feature_type="numeric",
            history_window=_feature_window(name),
            description=_feature_description(name),
        )
        for name in numeric
    ]
    records.extend(
        FeatureDefinition(
            name=name,
            label=name.replace("_", " ").title(),
            feature_type="categorical",
            history_window=_feature_window(name),
            description=_feature_description(name),
        )
        for name in categorical
    )
    return tuple(records)


def _feature_window(name: str) -> str:
    if name.startswith("lag1_") or name in {"previous_team", "team_changed_last_feature_season"}:
        return "previous completed season"
    if name.startswith("weighted_3yr_"):
        return "up to three completed seasons"
    if name.startswith("position_prior_"):
        return "training-only position prior"
    if name == "prediction_season":
        return "prediction season identifier"
    return "known at preseason cutoff"


def _feature_description(name: str) -> str:
    label = name.replace("_", " ")
    if name.startswith("lag1_"):
        return f"Prior completed-season {label.removeprefix('lag1 ')} value."
    if name.startswith("weighted_3yr_"):
        return f"Recency-weighted {label.removeprefix('weighted 3yr ')} over up to three seasons."
    if name.startswith("missing_"):
        return f"Indicator that {label.removeprefix('missing ')} evidence is unavailable."
    if name.startswith("position_prior_"):
        return f"Training-only positional prior for {label.removeprefix('position prior ')}."
    special = {
        "prediction_season": "Season being predicted; used only with chronological splitting.",
        "previous_team": "Team from the most recent completed season.",
        "age_at_cutoff": "Player age at the documented preseason feature cutoff.",
        "age_adjustment_factor": "Transparent position-aware age adjustment available at cutoff.",
        "history_seasons": "Count of completed historical seasons available at cutoff.",
        "nfl_experience_years": "NFL experience known at the preseason cutoff.",
        "team_changed_last_feature_season": "Indicator of a team change in the latest evidence.",
    }
    return special.get(name, f"Cutoff-safe {label} predictor from the Phase 4 feature contract.")


def _parse_folds(value: object) -> tuple[ChronologicalFoldSummary, ...]:
    records: list[ChronologicalFoldSummary] = []
    for row in _record_sequence(value):
        season = _optional_int(row.get("evaluation_season"))
        if season is None:
            continue
        records.append(
            ChronologicalFoldSummary(
                label=_optional_string(row.get("label")),
                evaluation_season=season,
                training_seasons=_int_tuple(row.get("training_seasons")),
            )
        )
    return tuple(sorted(records, key=lambda row: row.evaluation_season))


def _parse_baseline_metrics(value: object) -> tuple[MetricSummary, ...]:
    metrics: list[MetricSummary] = []
    for row in _record_sequence(value):
        season = _optional_int(row.get("evaluation_season"))
        metrics.append(
            MetricSummary(
                phase="phase3",
                candidate_name=_optional_string(row.get("baseline")),
                candidate_source="baseline",
                target_name=_optional_string(row.get("target")),
                position="ALL",
                evaluation_scope=_optional_string(row.get("fold_label")),
                evaluation_seasons=(season,) if season is not None else (),
                segment=_optional_string(row.get("segment")) or "all",
                rows=_optional_int(row.get("rows")) or 0,
                mae=_optional_float(row.get("mae")),
                rmse=_optional_float(row.get("rmse")),
                median_absolute_error=_optional_float(row.get("median_absolute_error")),
                spearman_rank_correlation=_optional_float(row.get("spearman_rank_correlation")),
                top_n_capture_rate=_optional_float(row.get("top_n_overlap")),
            )
        )
    return tuple(metrics)


def _parse_model_metrics(value: object) -> tuple[MetricSummary, ...]:
    metrics: list[MetricSummary] = []
    for row in _record_sequence(value):
        metrics.append(
            MetricSummary(
                phase="phase4",
                candidate_name=_optional_string(row.get("candidate_name")),
                candidate_source=_optional_string(row.get("candidate_source")),
                target_name=_optional_string(row.get("target_name")),
                position=_optional_string(row.get("position")),
                evaluation_scope=_optional_string(row.get("evaluation_scope")),
                evaluation_seasons=_int_tuple(row.get("evaluation_seasons")),
                segment="all",
                rows=_optional_int(row.get("rows")) or 0,
                mae=_optional_float(row.get("mae")),
                rmse=_optional_float(row.get("rmse")),
                median_absolute_error=_optional_float(row.get("median_absolute_error")),
                spearman_rank_correlation=_optional_float(row.get("spearman_rank_correlation")),
                top_n_capture_rate=_optional_float(row.get("top_n_capture_rate")),
            )
        )
    return tuple(metrics)


def _parse_selections(value: object) -> tuple[ChampionSelectionSummary, ...]:
    selections: list[ChampionSelectionSummary] = []
    for row in _record_sequence(value):
        selection_value = _optional_float(row.get("selection_value"))
        reference_value = _optional_float(row.get("reference_baseline_value"))
        improvement = _optional_float(row.get("mae_improvement_over_best_baseline"))
        if selection_value is None or reference_value is None:
            continue
        selections.append(
            ChampionSelectionSummary(
                position=_optional_string(row.get("position")),
                target_name=_optional_string(row.get("target_name")),
                selected_source=_optional_string(row.get("selected_source")),
                selected_name=_optional_string(row.get("selected_name")),
                selection_metric=_optional_string(row.get("selection_metric")),
                selection_value=selection_value,
                reference_baseline_name=_optional_string(row.get("reference_baseline_name")),
                reference_baseline_value=reference_value,
                improvement=improvement or 0.0,
                decision_status=_optional_string(row.get("decision_status")),
            )
        )
    return tuple(selections)


def _load_residual_summaries(
    connection: duckdb.DuckDBPyConnection, run_id: str
) -> tuple[ResidualSummary, ...]:
    rows = connection.execute(
        """
        SELECT model_family, position, target_name, prediction_scope,
               prediction_season, count(*),
               avg(actual_value - predicted_value),
               avg(abs(actual_value - predicted_value)),
               sqrt(avg(pow(actual_value - predicted_value, 2)))
        FROM player_projection_predictions
        WHERE run_id = ? AND actual_value IS NOT NULL
        GROUP BY ALL
        ORDER BY position, target_name, model_family, prediction_scope, prediction_season
        """,
        [run_id],
    ).fetchall()
    return tuple(
        ResidualSummary(
            model_family=str(row[0]),
            position=str(row[1]),
            target_name=str(row[2]),
            prediction_scope=str(row[3]),
            prediction_season=int(row[4]),
            rows=int(row[5]),
            mean_actual_minus_prediction=float(row[6]),
            mae=float(row[7]),
            rmse=float(row[8]),
        )
        for row in rows
    )


def _parse_feature_importance(value: object) -> tuple[FeatureImportanceSummary, ...]:
    results: list[FeatureImportanceSummary] = []
    for group in _record_sequence(value):
        interpretation = "Associative model diagnostic; importance is not causal."
        for row in _record_sequence(group.get("importance")):
            mean = _optional_float(row.get("importance_mean"))
            method = "permutation_importance"
            signed_value = None
            if mean is None:
                mean = _optional_float(row.get("absolute_importance"))
                signed_value = _optional_float(row.get("coefficient"))
                method = "standardized_ridge_coefficient"
            rank = _optional_int(row.get("rank"))
            if mean is None or rank is None:
                continue
            results.append(
                FeatureImportanceSummary(
                    position=_optional_string(group.get("position")),
                    target_name=_optional_string(group.get("target_name")),
                    model_family=_optional_string(group.get("model_family")),
                    feature=_optional_string(row.get("feature")),
                    rank=rank,
                    importance_mean=mean,
                    importance_std=_optional_float(row.get("importance_std")),
                    signed_value=signed_value,
                    direction=_optional_string(row.get("direction")),
                    method=method,
                    scope=_optional_string(row.get("explanation_scope")),
                    interpretation=interpretation,
                )
            )
    return tuple(results)


def _load_model_cards(
    connection: duckdb.DuckDBPyConnection, project_root: Path, run_id: str
) -> tuple[ModelCardReference, ...]:
    rows = connection.execute(
        """
        SELECT model_id, model_family, position, target_name, model_card_path
        FROM player_projection_models WHERE run_id = ?
        ORDER BY position, target_name, model_family
        """,
        [run_id],
    ).fetchall()
    cards: list[ModelCardReference] = []
    for row in rows:
        relative = str(row[4])
        absolute = _safe_project_path(project_root, relative)
        if absolute is None:
            continue
        cards.append(
            ModelCardReference(
                model_id=str(row[0]),
                model_family=str(row[1]),
                position=str(row[2]),
                target_name=str(row[3]),
                relative_path=relative,
                absolute_path=absolute,
                exists=absolute.is_file(),
            )
        )
    return tuple(cards)


def _parse_diagnostics(project_root: Path, value: object) -> tuple[DiagnosticReference, ...]:
    if not isinstance(value, Mapping):
        return ()
    results: list[DiagnosticReference] = []
    for key, path_value in sorted(value.items(), key=lambda item: str(item[0])):
        if not isinstance(path_value, str):
            continue
        absolute = _safe_project_path(project_root, path_value)
        if absolute is None:
            continue
        results.append(
            DiagnosticReference(
                name=str(key),
                relative_path=path_value,
                absolute_path=absolute,
                exists=absolute.is_file(),
            )
        )
    return tuple(results)


def _parse_player_factors(value: object) -> tuple[ExplanationFactor, ...]:
    factors: list[ExplanationFactor] = []
    for row in _record_sequence(value):
        factors.append(
            ExplanationFactor(
                rank=_optional_int(row.get("rank")) or len(factors) + 1,
                feature=_optional_string(row.get("feature")),
                direction=_optional_string(row.get("direction")),
                player_value=_json_scalar(row.get("player_value")),
                reference_value=_json_scalar(row.get("position_reference_value")),
                prediction_delta=_optional_float(row.get("prediction_delta")),
            )
        )
    return tuple(factors)


def _parse_supporting_values(value: object) -> tuple[ExplanationValue, ...]:
    if not isinstance(value, Mapping):
        return ()
    return tuple(
        ExplanationValue(str(key), _json_scalar(item))
        for key, item in sorted(value.items(), key=lambda pair: str(pair[0]))
    )


def _unavailable_player_explanation(
    board: ProjectionBoard,
    player_id: str,
    target_name: str,
    code: str,
    message: str,
) -> PlayerModelExplanation:
    del board
    return PlayerModelExplanation(
        available=False,
        code=code,
        message=message,
        player_id=player_id,
        display_name="",
        position="",
        target_name=target_name,
        prediction_status="unavailable",
        method_label="Unavailable",
        p10=None,
        p50=None,
        p90=None,
        explanation_type="unavailable",
        interpretation="",
        reason=message,
        learned_model_used=False,
        factors=(),
        supporting_values=(),
    )


def _empty_snapshot(
    *,
    status: ModelLabStatus,
    targets: tuple[TargetDefinition, ...],
    features: tuple[FeatureDefinition, ...],
) -> ModelLabSnapshot:
    return ModelLabSnapshot(
        status=status,
        run_id=None,
        targets=targets,
        features=features,
        folds=(),
        baseline_metrics=(),
        model_metrics=(),
        selections=(),
        residuals=(),
        feature_importance=(),
        model_cards=(),
        diagnostics=(),
        players=(),
        limitations=(),
    )


def _json_object(value: object) -> dict[str, Any]:
    parsed = json.loads(value) if isinstance(value, str) else value
    if not isinstance(parsed, dict):
        raise ValueError("Model report payload must be a JSON object.")
    return {str(key): item for key, item in parsed.items()}


def _record_sequence(value: object) -> tuple[Mapping[str, object], ...]:
    if not isinstance(value, Sequence) or isinstance(value, (str, bytes)):
        return ()
    return tuple(item for item in value if isinstance(item, Mapping))


def _string_tuple(value: object) -> tuple[str, ...]:
    if not isinstance(value, Sequence) or isinstance(value, (str, bytes)):
        return ()
    return tuple(str(item) for item in value if isinstance(item, str))


def _int_tuple(value: object) -> tuple[int, ...]:
    if not isinstance(value, Sequence) or isinstance(value, (str, bytes)):
        return ()
    return tuple(number for item in value if (number := _optional_int(item)) is not None)


def _optional_string(value: object) -> str:
    return value if isinstance(value, str) else ""


def _optional_int(value: object) -> int | None:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        return None
    number = float(value)
    return int(number) if math.isfinite(number) and number.is_integer() else None


def _optional_float(value: object) -> float | None:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        return None
    number = float(value)
    return number if math.isfinite(number) else None


def _json_scalar(value: object) -> JsonScalar:
    if value is None or isinstance(value, (str, bool, int)):
        return value
    if isinstance(value, float) and math.isfinite(value):
        return value
    return str(value)


def _safe_project_path(project_root: Path, relative: str) -> Path | None:
    root = project_root.resolve()
    path = (root / Path(relative)).resolve()
    return path if path.is_relative_to(root) else None
