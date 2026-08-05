"""Manual chronological inner tuning with no random or future-season folds."""

from __future__ import annotations

import math
from collections.abc import Iterable, Mapping
from dataclasses import dataclass
from typing import Any

import numpy as np
from sklearn.pipeline import Pipeline  # type: ignore[import-untyped]

from fantasy_draft_ai.models.player_projection.config import (
    ModelFamily,
    PlayerModelConfig,
    canonical_json,
)
from fantasy_draft_ai.models.player_projection.dataset import ModelMatrix
from fantasy_draft_ai.models.player_projection.pipelines import (
    build_pipeline,
    candidate_parameters,
)


@dataclass(frozen=True)
class InnerFold:
    """One validation season with strictly earlier training seasons."""

    training_seasons: tuple[int, ...]
    validation_season: int


@dataclass(frozen=True)
class FoldScore:
    training_seasons: tuple[int, ...]
    validation_season: int
    rows: int
    mean_absolute_error: float


@dataclass(frozen=True)
class OutOfFoldPrediction:
    """A training-history-only prediction suitable for residual calibration."""

    player_id: str
    position: str
    target_name: str
    prediction_season: int
    training_seasons: tuple[int, ...]
    actual_value: float
    predicted_value: float


@dataclass(frozen=True)
class CandidateEvaluation:
    parameters: Mapping[str, Any]
    fold_scores: tuple[FoldScore, ...]
    mean_absolute_error: float
    out_of_fold_predictions: tuple[OutOfFoldPrediction, ...]


@dataclass(frozen=True)
class TuningResult:
    """Selected inner-CV parameters and a refit pipeline for the outer training set."""

    family: ModelFamily
    position: str
    target_name: str
    training_seasons: tuple[int, ...]
    best_parameters: Mapping[str, Any]
    best_mean_absolute_error: float
    candidate_evaluations: tuple[CandidateEvaluation, ...]
    out_of_fold_predictions: tuple[OutOfFoldPrediction, ...]
    pipeline: Pipeline


def chronological_inner_folds(
    seasons: Iterable[int],
    *,
    min_training_seasons: int = 2,
    max_validation_seasons: int | None = 3,
) -> tuple[InnerFold, ...]:
    """Create deterministic expanding folds and optionally retain the newest validations."""

    ordered = tuple(sorted(set(int(season) for season in seasons)))
    if min_training_seasons < 1:
        raise ValueError("min_training_seasons must be at least one.")
    if max_validation_seasons is not None and max_validation_seasons < 1:
        raise ValueError("max_validation_seasons must be positive when set.")
    if len(ordered) <= min_training_seasons:
        raise ValueError("Not enough seasons for chronological inner tuning.")
    folds = tuple(
        InnerFold(training_seasons=ordered[:index], validation_season=season)
        for index, season in enumerate(ordered)
        if index >= min_training_seasons
    )
    if max_validation_seasons is not None:
        folds = folds[-max_validation_seasons:]
    if not folds:
        raise ValueError("No chronological inner folds are available.")
    for fold in folds:
        if not fold.training_seasons or max(fold.training_seasons) >= fold.validation_season:
            raise RuntimeError("Chronological inner fold construction leaked a future season.")
    return folds


def tune_model(
    matrix: ModelMatrix,
    *,
    family: ModelFamily,
    config: PlayerModelConfig,
) -> TuningResult:
    """Tune manually on inner seasons, then refit on the complete outer-training matrix."""

    _validate_training_matrix(matrix, config)
    assert matrix.y is not None
    folds = chronological_inner_folds(
        matrix.prediction_seasons,
        min_training_seasons=config.min_inner_training_seasons,
        max_validation_seasons=config.max_inner_validation_seasons,
    )
    evaluations = tuple(
        _evaluate_candidate(matrix, family, config, parameters, folds)
        for parameters in candidate_parameters(family, config)
    )
    selected = min(
        evaluations,
        key=lambda candidate: (
            candidate.mean_absolute_error,
            canonical_json(candidate.parameters),
        ),
    )
    pipeline = build_pipeline(family, config, selected.parameters)
    pipeline.fit(matrix.X, matrix.y)
    return TuningResult(
        family=family,
        position=matrix.position,
        target_name=str(matrix.target_name),
        training_seasons=matrix.prediction_seasons,
        best_parameters=dict(selected.parameters),
        best_mean_absolute_error=selected.mean_absolute_error,
        candidate_evaluations=evaluations,
        out_of_fold_predictions=selected.out_of_fold_predictions,
        pipeline=pipeline,
    )


def _evaluate_candidate(
    matrix: ModelMatrix,
    family: ModelFamily,
    config: PlayerModelConfig,
    parameters: Mapping[str, Any],
    folds: tuple[InnerFold, ...],
) -> CandidateEvaluation:
    assert matrix.y is not None
    assert matrix.target_name is not None
    scores: list[FoldScore] = []
    predictions: list[OutOfFoldPrediction] = []
    absolute_errors: list[float] = []
    seasons = matrix.keys["prediction_season"]
    for fold in folds:
        training_mask = seasons.isin(fold.training_seasons)
        validation_mask = seasons.eq(fold.validation_season)
        if not bool(training_mask.any()) or not bool(validation_mask.any()):
            raise ValueError(
                f"Inner fold {fold.validation_season} has an empty training or validation set."
            )
        pipeline = build_pipeline(family, config, parameters)
        pipeline.fit(matrix.X.loc[training_mask], matrix.y.loc[training_mask])
        predicted = np.asarray(pipeline.predict(matrix.X.loc[validation_mask]), dtype=float)
        actual = matrix.y.loc[validation_mask].to_numpy(dtype=float)
        fold_errors = np.abs(predicted - actual)
        if not np.isfinite(predicted).all() or not np.isfinite(fold_errors).all():
            raise RuntimeError("A tuning candidate produced non-finite predictions.")
        absolute_errors.extend(float(value) for value in fold_errors)
        fold_mae = math.fsum(float(value) for value in fold_errors) / len(fold_errors)
        scores.append(
            FoldScore(
                training_seasons=fold.training_seasons,
                validation_season=fold.validation_season,
                rows=len(fold_errors),
                mean_absolute_error=fold_mae,
            )
        )
        validation_keys = matrix.keys.loc[validation_mask]
        for index, (_, key) in enumerate(validation_keys.iterrows()):
            predictions.append(
                OutOfFoldPrediction(
                    player_id=str(key["player_id"]),
                    position=matrix.position,
                    target_name=matrix.target_name,
                    prediction_season=int(key["prediction_season"]),
                    training_seasons=fold.training_seasons,
                    actual_value=float(actual[index]),
                    predicted_value=float(predicted[index]),
                )
            )
    if not absolute_errors:
        raise ValueError("No out-of-fold predictions were produced during tuning.")
    return CandidateEvaluation(
        parameters=dict(parameters),
        fold_scores=tuple(scores),
        mean_absolute_error=math.fsum(absolute_errors) / len(absolute_errors),
        out_of_fold_predictions=tuple(predictions),
    )


def _validate_training_matrix(matrix: ModelMatrix, config: PlayerModelConfig) -> None:
    if matrix.y is None or matrix.target_name is None:
        raise ValueError("Manual tuning requires a training matrix with outcomes.")
    if matrix.position not in config.positions or matrix.target_name not in config.targets:
        raise ValueError("Training matrix routing does not match the model configuration.")
    if tuple(str(column) for column in matrix.X.columns) != (
        *config.numeric_features,
        *config.categorical_features,
    ):
        raise ValueError("Training matrix columns do not match the locked feature contract.")
    if len(matrix.X) != len(matrix.y) or len(matrix.X) != len(matrix.keys):
        raise ValueError("Training matrix features, outcomes, and keys are misaligned.")
    if bool(matrix.keys["is_rookie"].any()):
        raise ValueError("Rookie rows cannot be used to fit Phase 4 models.")
    if bool(matrix.y.isna().any()):
        raise ValueError("Training outcomes cannot contain nulls.")
