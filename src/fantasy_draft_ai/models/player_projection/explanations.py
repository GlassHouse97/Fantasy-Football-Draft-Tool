"""Deterministic, model-appropriate explanations for player projections.

This module intentionally does not import SHAP. Scikit-learn, pandas, and NumPy
are loaded only inside functions that need them, preserving the lightweight base
CLI when the optional modeling dependencies are absent.
"""

from __future__ import annotations

import math
from collections.abc import Iterable, Mapping, Sequence
from typing import Any

DEFAULT_RANDOM_SEED = 42
NON_CAUSAL_NOTICE = (
    "This explanation is associative, not causal; changing a feature here does not "
    "establish that the feature causes the prediction to change."
)


def ridge_coefficient_importance(
    model: Any,
    *,
    feature_names: Sequence[str] | None = None,
    top_n: int | None = None,
) -> list[dict[str, Any]]:
    """Return deterministic, JSON-safe Ridge coefficient importance.

    When ``model`` is a fitted scikit-learn Pipeline, transformed feature names
    are obtained from all steps before the final estimator. A bare fitted Ridge
    estimator can be used by supplying ``feature_names``.
    """

    import numpy as np

    estimator = _coefficient_estimator(model)
    coefficients = np.asarray(estimator.coef_, dtype=float).reshape(-1)
    names = _transformed_feature_names(model, feature_names)
    if not names:
        names = [f"feature_{index}" for index in range(coefficients.size)]
    if len(names) != coefficients.size:
        raise ValueError(
            "The number of Ridge coefficients does not match the transformed feature names."
        )
    limit = _validated_top_n(top_n)
    rows: list[dict[str, Any]] = [
        {
            "feature": str(name),
            "coefficient": _finite_float(coefficient, "Ridge coefficient"),
            "absolute_importance": _finite_float(abs(coefficient), "Ridge absolute coefficient"),
            "direction": (
                "positive" if coefficient > 0 else "negative" if coefficient < 0 else "zero"
            ),
        }
        for name, coefficient in zip(names, coefficients, strict=True)
    ]
    rows.sort(key=lambda row: (-float(row["absolute_importance"]), str(row["feature"])))
    if limit is not None:
        rows = rows[:limit]
    for rank, row in enumerate(rows, start=1):
        row["rank"] = rank
    return rows


def hist_gradient_boosting_permutation_importance(
    model: Any,
    features: Any,
    targets: Any,
    *,
    feature_names: Sequence[str] | None = None,
    scoring: str = "neg_mean_absolute_error",
    n_repeats: int = 10,
    random_seed: int = DEFAULT_RANDOM_SEED,
    top_n: int | None = None,
) -> list[dict[str, Any]]:
    """Calculate deterministic model-agnostic permutation importance for HGB.

    Importance is measured on the original columns supplied to the fitted
    pipeline, which keeps reports understandable after preprocessing.
    """

    import numpy as np
    from sklearn.inspection import permutation_importance  # type: ignore[import-untyped]

    if n_repeats < 1:
        raise ValueError("n_repeats must be at least one.")
    names = _input_feature_names(features, feature_names)
    result = permutation_importance(
        model,
        features,
        targets,
        scoring=scoring,
        n_repeats=n_repeats,
        random_state=random_seed,
        n_jobs=1,
    )
    means = np.asarray(result.importances_mean, dtype=float).reshape(-1)
    standard_deviations = np.asarray(result.importances_std, dtype=float).reshape(-1)
    if len(names) != means.size:
        raise ValueError("Permutation importance does not match the input feature columns.")
    limit = _validated_top_n(top_n)
    rows: list[dict[str, Any]] = [
        {
            "feature": str(name),
            "importance_mean": _finite_float(mean, "permutation importance"),
            "importance_std": _finite_float(std, "permutation importance deviation"),
        }
        for name, mean, std in zip(names, means, standard_deviations, strict=True)
    ]
    rows.sort(key=lambda row: (-float(row["importance_mean"]), str(row["feature"])))
    if limit is not None:
        rows = rows[:limit]
    for rank, row in enumerate(rows, start=1):
        row["rank"] = rank
    return rows


def numeric_partial_dependence(
    model: Any,
    features: Any,
    numeric_features: Iterable[str],
    *,
    grid_resolution: int = 20,
    percentiles: tuple[float, float] = (0.05, 0.95),
) -> list[dict[str, Any]]:
    """Return one-way average feature-response curves without requiring SHAP.

    The grid is calculated from finite observed values before replacing that
    feature across the full evaluation frame. This matters for cutoff-safe NFL
    predictors, where a legitimate missing value is common: scikit-learn's
    default grid calculation can otherwise return an all-NaN grid even though
    the fitted pipeline can impute and score the feature correctly.
    """

    import numpy as np

    if grid_resolution < 2:
        raise ValueError("grid_resolution must be at least two.")
    if not 0 <= percentiles[0] < percentiles[1] <= 1:
        raise ValueError("percentiles must be ordered within [0, 1].")
    available_names = _input_feature_names(features, None)
    requested = sorted(set(str(feature) for feature in numeric_features))
    missing = sorted(set(requested) - set(available_names))
    if missing:
        raise ValueError(f"Partial-dependence features are missing: {missing}.")

    curves: list[dict[str, Any]] = []
    for feature in requested:
        feature_index = available_names.index(feature)
        source_column = (
            features[feature]
            if hasattr(features, "columns")
            else np.asarray(features)[:, feature_index]
        )
        try:
            numeric_values = np.asarray(source_column, dtype=float).reshape(-1)
        except (TypeError, ValueError) as exc:
            raise ValueError(f"Partial-dependence feature {feature!r} is not numeric.") from exc
        finite_values = numeric_values[np.isfinite(numeric_values)]
        unique_values = np.unique(finite_values)
        if unique_values.size < 2:
            curves.append(
                {
                    "feature": feature,
                    "method": "one_way_average_partial_dependence",
                    "response_status": "no_stable_numeric_grid",
                    "reason": "Fewer than two finite observed feature values are available.",
                    "points": [],
                    "interpretation": NON_CAUSAL_NOTICE,
                }
            )
            continue
        if unique_values.size <= grid_resolution:
            grid_values = unique_values
        else:
            lower, upper = np.quantile(finite_values, percentiles)
            grid_values = np.linspace(float(lower), float(upper), grid_resolution)
        averages: list[float] = []
        for grid_value in grid_values:
            evaluation_rows = features.copy()
            if hasattr(evaluation_rows, "loc"):
                evaluation_rows.loc[:, feature] = float(grid_value)
            else:
                evaluation_rows[:, feature_index] = float(grid_value)
            predictions = np.asarray(model.predict(evaluation_rows), dtype=float).reshape(-1)
            if predictions.size != numeric_values.size or not bool(np.isfinite(predictions).all()):
                raise ValueError(f"Partial-dependence predictions are malformed for {feature}.")
            averages.append(float(np.mean(predictions)))
        points = [
            {
                "feature_value": _json_scalar(value, f"{feature} grid value"),
                "average_prediction": _finite_float(average, f"{feature} response"),
            }
            for value, average in zip(grid_values, averages, strict=True)
        ]
        curves.append(
            {
                "feature": feature,
                "method": "one_way_average_partial_dependence",
                "response_status": "stable_numeric_grid",
                "points": points,
                "interpretation": NON_CAUSAL_NOTICE,
            }
        )
    return curves


def explain_player_prediction(
    model: Any,
    player_features: Mapping[str, Any],
    position_reference: Mapping[str, Any],
    *,
    position: str,
    target_name: str,
    feature_names: Iterable[str] | None = None,
    prediction_value: float | None = None,
    top_n: int = 5,
    minimum_absolute_delta: float = 1e-12,
) -> dict[str, Any]:
    """Explain one player by replacing one feature at a time with a reference.

    The supplied reference must be calculated for the player's position using
    training-only data. Deltas are local sensitivity descriptions and are
    explicitly not presented as causal effects.
    """

    import pandas as pd

    if not position.strip() or not target_name.strip():
        raise ValueError("position and target_name cannot be empty.")
    if top_n < 1:
        raise ValueError("top_n must be at least one.")
    if minimum_absolute_delta < 0:
        raise ValueError("minimum_absolute_delta cannot be negative.")

    player = dict(player_features)
    if not player:
        raise ValueError("player_features cannot be empty.")
    selected = (
        sorted(set(str(name) for name in feature_names))
        if feature_names is not None
        else sorted(set(player) & set(position_reference))
    )
    missing_player = sorted(set(selected) - set(player))
    missing_reference = sorted(set(selected) - set(position_reference))
    if missing_player or missing_reference:
        raise ValueError(
            "Explanation features must exist in both player and position reference rows; "
            f"missing player={missing_player}, missing reference={missing_reference}."
        )

    raw_prediction = _single_prediction(model, pd.DataFrame([player]))
    displayed_prediction = (
        raw_prediction
        if prediction_value is None
        else _finite_float(prediction_value, "displayed prediction")
    )
    factors: list[dict[str, Any]] = []
    for feature in selected:
        observed = player[feature]
        reference = position_reference[feature]
        if _same_scalar(observed, reference):
            continue
        perturbed = dict(player)
        perturbed[feature] = reference
        reference_prediction = _single_prediction(model, pd.DataFrame([perturbed]))
        delta = raw_prediction - reference_prediction
        if abs(delta) <= minimum_absolute_delta:
            continue
        factors.append(
            {
                "feature": feature,
                "player_value": _json_scalar(observed, f"{feature} player value"),
                "position_reference_value": _json_scalar(
                    reference, f"{feature} position reference"
                ),
                "prediction_delta": _finite_float(delta, f"{feature} prediction delta"),
                "direction": "increases_prediction" if delta > 0 else "decreases_prediction",
                "reference_substitution_prediction": reference_prediction,
            }
        )
    factors.sort(key=lambda row: (-abs(float(row["prediction_delta"])), str(row["feature"])))
    factors = factors[:top_n]
    for rank, factor in enumerate(factors, start=1):
        factor["rank"] = rank

    return {
        "schema_version": "1.0",
        "explanation_type": "local_position_reference_perturbation",
        "method": "one_feature_at_a_time_position_reference_substitution",
        "position": position,
        "target_name": target_name,
        "prediction": displayed_prediction,
        "raw_model_prediction": raw_prediction,
        "top_factors": factors,
        "reference_requirement": (
            "The supplied position reference must be derived from training-only rows."
        ),
        "interpretation": NON_CAUSAL_NOTICE,
    }


def explain_heuristic_fallback(
    *,
    heuristic_name: str,
    position: str,
    target_name: str,
    prediction_value: float,
    reason: str,
    is_rookie: bool = False,
    supporting_values: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    """Describe a transparent baseline fallback, including the rookie boundary."""

    required = {
        "heuristic_name": heuristic_name,
        "position": position,
        "target_name": target_name,
        "reason": reason,
    }
    empty = sorted(name for name, value in required.items() if not value.strip())
    if empty:
        raise ValueError(f"Fallback explanation fields cannot be empty: {empty}.")
    values = {
        str(key): _json_scalar(value, f"supporting value {key}")
        for key, value in sorted((supporting_values or {}).items())
    }
    rookie_note = (
        "No cutoff-safe historical rookie feature rows are available for learned-model "
        "validation, so this rookie uses a transparent heuristic fallback."
        if is_rookie
        else "This player uses a transparent heuristic fallback instead of a learned model."
    )
    return {
        "schema_version": "1.0",
        "explanation_type": "transparent_heuristic_fallback",
        "heuristic_name": heuristic_name,
        "position": position,
        "target_name": target_name,
        "prediction": _finite_float(prediction_value, "heuristic prediction"),
        "prediction_status": (
            "rookie_heuristic_fallback_unvalidated" if is_rookie else "heuristic_fallback"
        ),
        "validation_status": (
            "not_validated_for_rookies" if is_rookie else "baseline_validation_only"
        ),
        "uncertainty_status": "unvalidated_uncalibrated",
        "reason": reason,
        "supporting_values": values,
        "interpretation": rookie_note,
        "learned_model_used": False,
    }


def _coefficient_estimator(model: Any) -> Any:
    if hasattr(model, "coef_"):
        return model
    named_steps = getattr(model, "named_steps", None)
    if named_steps is not None:
        for estimator in reversed(tuple(named_steps.values())):
            if hasattr(estimator, "coef_"):
                return estimator
    raise ValueError("The supplied fitted model does not expose Ridge coefficients.")


def _transformed_feature_names(model: Any, feature_names: Sequence[str] | None) -> list[str]:
    named_steps = getattr(model, "named_steps", None)
    if named_steps is None:
        return [str(name) for name in feature_names] if feature_names is not None else []
    try:
        preprocessing = model[:-1]
        names = preprocessing.get_feature_names_out(
            None if feature_names is None else list(feature_names)
        )
    except (AttributeError, TypeError, ValueError):
        return [str(name) for name in feature_names] if feature_names is not None else []
    return [str(name) for name in names]


def _input_feature_names(features: Any, supplied: Sequence[str] | None) -> list[str]:
    if supplied is not None:
        names = [str(name) for name in supplied]
    elif hasattr(features, "columns"):
        names = [str(name) for name in features.columns]
    else:
        shape = getattr(features, "shape", None)
        if shape is None or len(shape) != 2:
            raise ValueError("feature_names are required for non-tabular features.")
        names = [f"feature_{index}" for index in range(int(shape[1]))]
    if len(set(names)) != len(names):
        raise ValueError("Feature names must be unique.")
    return names


def _single_prediction(model: Any, features: Any) -> float:
    import numpy as np

    predictions = np.asarray(model.predict(features), dtype=float).reshape(-1)
    if predictions.size != 1:
        raise ValueError("Local explanation requires exactly one model prediction.")
    return _finite_float(predictions[0], "model prediction")


def _same_scalar(left: Any, right: Any) -> bool:
    left_missing = _is_missing_scalar(left)
    right_missing = _is_missing_scalar(right)
    if left_missing or right_missing:
        return left_missing and right_missing
    try:
        result = left == right
        return bool(result)
    except (TypeError, ValueError):
        return False


def _json_scalar(value: Any, label: str) -> str | int | float | bool | None:
    if _is_missing_scalar(value):
        return None
    if isinstance(value, (str, bool, int)):
        return value
    if isinstance(value, float):
        return _finite_float(value, label)
    item = getattr(value, "item", None)
    if callable(item):
        return _json_scalar(item(), label)
    raise ValueError(f"{label} must be a JSON-safe scalar, not {type(value).__name__}.")


def _is_missing_scalar(value: Any) -> bool:
    if value is None:
        return True
    if isinstance(value, float):
        return math.isnan(value)
    item = getattr(value, "item", None)
    if callable(item):
        try:
            scalar = item()
        except (TypeError, ValueError):
            scalar = value
        if scalar is not value:
            return _is_missing_scalar(scalar)
    # pandas.NA and pandas.NaT deliberately refuse truth-value coercion.
    return type(value).__name__ in {"NAType", "NaTType"}


def _finite_float(value: Any, label: str) -> float:
    result = float(value)
    if not math.isfinite(result):
        raise ValueError(f"{label} must be finite.")
    return result


def _validated_top_n(top_n: int | None) -> int | None:
    if top_n is not None and top_n < 1:
        raise ValueError("top_n must be at least one when supplied.")
    return top_n
