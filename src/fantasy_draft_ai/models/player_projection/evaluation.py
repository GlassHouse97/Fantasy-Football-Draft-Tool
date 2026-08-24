"""Pure, deterministic evaluation utilities for Phase 4 player models.

The functions in this module deliberately accept ordinary iterables as well as
NumPy arrays and pandas ``Series``/``DataFrame`` objects.  Returned mappings use
only JSON-safe Python scalars: unavailable metrics are represented by ``None``
rather than NaN.
"""

from __future__ import annotations

import math
from collections import defaultdict
from collections.abc import Iterable, Mapping, Sequence
from dataclasses import dataclass
from typing import Any, Final, cast

import numpy as np
from numpy.typing import NDArray

from fantasy_draft_ai.models.player_projection.config import (
    TARGET_FANTASY_POINTS_TOTAL,
    DraftRelevancePolicy,
)

DEFAULT_VALIDATION_SEASONS: Final = (2020, 2021, 2022, 2023, 2024)
DEFAULT_TEST_SEASON: Final = 2025
DEFAULT_BASELINES: Final = (
    "previous_season",
    "weighted_history",
    "age_position_adjusted",
    "position_shrinkage",
    "weighted_components",
)
DEFAULT_LEARNED_MODELS: Final = ("ridge", "hist_gradient_boosting")

FloatArray = NDArray[np.float64]


def regression_metrics(
    y_true: Iterable[object],
    y_pred: Iterable[object],
    *,
    top_n: int | None = 12,
    entity_ids: Iterable[object] | None = None,
) -> dict[str, int | float | None]:
    """Return core regression and ranking metrics for aligned observations.

    Rows with a missing/NaN actual are excluded. A non-finite prediction paired
    with an available actual is rejected. ``top_n_capture_rate`` is the share of
    the actual top N entities that also appear in the predicted top N. Both sets
    use ``min(N, rows)`` and ties are broken by entity ID, so the result is stable.
    """

    actual, predicted, valid_indexes, original_rows = _paired_values(y_true, y_pred)
    if top_n is not None and top_n < 1:
        raise ValueError("top_n must be positive when provided.")
    ids = (
        _filtered_entity_ids(entity_ids, original_rows, valid_indexes) if top_n is not None else []
    )
    row_count = int(actual.size)
    if row_count == 0:
        return {
            "rows": 0,
            "mae": None,
            "rmse": None,
            "median_absolute_error": None,
            "spearman_rank_correlation": None,
            "top_n": 0 if top_n is not None else None,
            "top_n_capture_rate": None,
        }

    errors = predicted - actual
    absolute_errors = np.abs(errors)
    capture = (
        _top_n_capture(actual, predicted, ids, top_n)
        if top_n is not None
        else {"top_n": None, "top_n_capture_rate": None}
    )
    return {
        "rows": row_count,
        "mae": float(np.mean(absolute_errors)),
        "rmse": float(np.sqrt(np.mean(np.square(errors)))),
        "median_absolute_error": float(np.median(absolute_errors)),
        "spearman_rank_correlation": _spearman(actual, predicted),
        **capture,
    }


def assign_projection_tiers(
    predicted_values: Iterable[object],
    *,
    entity_ids: Iterable[object] | None = None,
    edge_fraction: float = 0.25,
) -> list[str]:
    """Assign deterministic ``top``/``middle``/``lower`` projection tiers.

    Call this within a single season, position, target, and candidate slice.
    The top and bottom ``edge_fraction`` of the ordered projection list form the
    edge tiers; midpoint ranks make boundary behavior deterministic.
    """

    values = _float_array(predicted_values, "predicted_values")
    if not 0.0 < edge_fraction < 0.5:
        raise ValueError("edge_fraction must be between zero and one half.")
    if not bool(np.all(np.isfinite(values))):
        raise ValueError("predicted_values must all be finite.")
    indexes = np.arange(values.size, dtype=np.int64)
    ids = _filtered_entity_ids(entity_ids, int(values.size), indexes)
    order = _descending_order(values, ids)
    tiers = ["middle"] * int(values.size)
    row_count = int(values.size)
    for rank, original_index in enumerate(order):
        percentile = (rank + 0.5) / row_count
        if percentile <= edge_fraction:
            tiers[int(original_index)] = "top"
        elif percentile >= 1.0 - edge_fraction:
            tiers[int(original_index)] = "lower"
    return tiers


def segment_regression_metrics(
    records: object,
    *,
    actual_key: str = "actual_value",
    prediction_key: str = "predicted_value",
    entity_key: str = "player_id",
    dimensions: Sequence[str] = ("position", "experience_group", "projection_tier"),
    top_n: int | None = None,
) -> list[dict[str, Any]]:
    """Return error records by position, experience group, and projection tier.

    ``records`` should represent one candidate/target slice. It may be an
    iterable of mappings or a pandas DataFrame. Missing dimension columns are a
    hard error so reports cannot silently omit a required segment.
    """

    normalized = _as_records(records)
    if not dimensions:
        raise ValueError("At least one segment dimension is required.")
    for dimension in dimensions:
        if any(dimension not in row for row in normalized):
            raise KeyError(f"Missing required segment dimension: {dimension}.")

    grouped: dict[tuple[str, str], list[dict[str, Any]]] = defaultdict(list)
    for row in normalized:
        for dimension in dimensions:
            value = row[dimension]
            segment = "unknown" if value is None else str(value)
            grouped[dimension, segment].append(row)

    output: list[dict[str, Any]] = []
    for dimension in dimensions:
        dimension_groups = sorted(
            (
                (segment, rows)
                for (group_dimension, segment), rows in grouped.items()
                if group_dimension == dimension
            ),
            key=lambda item: item[0],
        )
        for segment, rows in dimension_groups:
            required_keys = [actual_key, prediction_key]
            if top_n is not None:
                required_keys.append(entity_key)
            for key in required_keys:
                if any(key not in row for row in rows):
                    raise KeyError(f"Missing required evaluation column: {key}.")
            metrics = regression_metrics(
                (row[actual_key] for row in rows),
                (row[prediction_key] for row in rows),
                top_n=top_n,
                entity_ids=(row[entity_key] for row in rows) if top_n is not None else None,
            )
            output.append(
                {
                    "segment_dimension": dimension,
                    "segment": segment,
                    "candidate_rows": len(rows),
                    **metrics,
                }
            )
    return output


def interval_metrics(
    y_true: Iterable[object],
    p10: Iterable[object],
    p50: Iterable[object],
    p90: Iterable[object],
) -> dict[str, int | float | None]:
    """Evaluate empirical P10/P50/P90 intervals and quantile calibration losses."""

    actual = _float_array(y_true, "y_true")
    lower = _float_array(p10, "p10")
    median = _float_array(p50, "p50")
    upper = _float_array(p90, "p90")
    _require_equal_lengths(actual, lower, median, upper)
    valid = np.isfinite(actual)
    if bool(np.any(valid & (~np.isfinite(lower) | ~np.isfinite(median) | ~np.isfinite(upper)))):
        raise ValueError("Every available actual must have finite P10/P50/P90 predictions.")
    actual = actual[valid]
    lower = lower[valid]
    median = median[valid]
    upper = upper[valid]
    if bool(np.any((lower > median) | (median > upper))):
        raise ValueError("Prediction intervals must satisfy P10 <= P50 <= P90.")
    if actual.size == 0:
        return {
            "rows": 0,
            "empirical_coverage_p10_p90": None,
            "mean_interval_width_p10_p90": None,
            "pinball_loss_p10": None,
            "pinball_loss_p50": None,
            "pinball_loss_p90": None,
        }
    return {
        "rows": int(actual.size),
        "empirical_coverage_p10_p90": float(np.mean((actual >= lower) & (actual <= upper))),
        "mean_interval_width_p10_p90": float(np.mean(upper - lower)),
        "pinball_loss_p10": _pinball_loss(actual, lower, 0.10),
        "pinball_loss_p50": _pinball_loss(actual, median, 0.50),
        "pinball_loss_p90": _pinball_loss(actual, upper, 0.90),
    }


def paired_bootstrap_mae_difference(
    y_true: Iterable[object],
    candidate_prediction: Iterable[object],
    reference_prediction: Iterable[object],
    *,
    n_resamples: int = 2_000,
    seed: int = 42,
) -> dict[str, int | float | str | None]:
    """Return a paired percentile 95% CI for candidate MAE minus reference MAE.

    Negative differences favor the candidate. Resampling rows as pairs preserves
    the fact that both candidates were evaluated on the same player-seasons.
    """

    if n_resamples < 1:
        raise ValueError("n_resamples must be positive.")
    if seed < 0:
        raise ValueError("seed cannot be negative.")
    actual = _float_array(y_true, "y_true")
    candidate = _float_array(candidate_prediction, "candidate_prediction")
    reference = _float_array(reference_prediction, "reference_prediction")
    _require_equal_lengths(actual, candidate, reference)
    valid = np.isfinite(actual)
    if bool(np.any(valid & (~np.isfinite(candidate) | ~np.isfinite(reference)))):
        raise ValueError("Every available actual must have two finite paired predictions.")
    actual = actual[valid]
    candidate = candidate[valid]
    reference = reference[valid]
    rows = int(actual.size)
    if rows == 0:
        return {
            "rows": 0,
            "candidate_mae": None,
            "reference_mae": None,
            "mae_difference_candidate_minus_reference": None,
            "ci95_lower": None,
            "ci95_upper": None,
            "n_resamples": n_resamples,
            "seed": seed,
            "direction": "unavailable",
        }

    candidate_errors = np.abs(candidate - actual)
    reference_errors = np.abs(reference - actual)
    observed = float(np.mean(candidate_errors) - np.mean(reference_errors))
    generator = np.random.default_rng(seed)
    bootstrapped = np.empty(n_resamples, dtype=np.float64)
    offset = 0
    chunk_size = 256
    while offset < n_resamples:
        batch_size = min(chunk_size, n_resamples - offset)
        indexes = generator.integers(0, rows, size=(batch_size, rows))
        bootstrapped[offset : offset + batch_size] = np.mean(
            candidate_errors[indexes] - reference_errors[indexes], axis=1
        )
        offset += batch_size
    bounds = np.quantile(bootstrapped, [0.025, 0.975], method="linear")
    lower = float(bounds[0])
    upper = float(bounds[1])
    if upper < 0.0:
        direction = "candidate_lower_mae"
    elif lower > 0.0:
        direction = "reference_lower_mae"
    else:
        direction = "uncertain"
    return {
        "rows": rows,
        "candidate_mae": float(np.mean(candidate_errors)),
        "reference_mae": float(np.mean(reference_errors)),
        "mae_difference_candidate_minus_reference": observed,
        "ci95_lower": lower,
        "ci95_upper": upper,
        "n_resamples": n_resamples,
        "seed": seed,
        "direction": direction,
    }


def select_champions(
    predictions: object,
    *,
    validation_seasons: Sequence[int] = DEFAULT_VALIDATION_SEASONS,
    test_season: int = DEFAULT_TEST_SEASON,
    required_baselines: Sequence[str] = DEFAULT_BASELINES,
    required_learned_models: Sequence[str] = DEFAULT_LEARNED_MODELS,
    season_key: str = "prediction_season",
    position_key: str = "position",
    target_key: str = "target_name",
    source_key: str = "candidate_source",
    candidate_key: str = "candidate_name",
    entity_key: str = "player_id",
    actual_key: str = "actual_value",
    prediction_key: str = "predicted_value",
    n_bootstrap: int = 2_000,
    seed: int = 42,
    draft_relevance_policy: DraftRelevancePolicy | None = None,
) -> dict[str, Any]:
    """Select one champion per position and target using validation evidence only.

    Without a draft-relevance policy, validation errors retain the original pooled
    2020-2024 behavior. With a policy, one fixed cohort per season and position is
    selected from the cutoff-safe total-points anchor baseline. Candidate selection
    then uses cohort MAE with paired-bootstrap, pooled-MAE, and total-points capture
    safeguards. The 2025 test metric is attached only after selection. All
    candidates must cover the same validation player-seasons.

    Required standardized sources are ``baseline`` and ``learned``. The output
    contains JSON-safe candidate metrics and champion records suitable for a
    report or warehouse persistence layer.
    """

    selection_seasons = tuple(sorted(set(int(season) for season in validation_seasons)))
    if not selection_seasons:
        raise ValueError("At least one validation season is required.")
    if any(season >= test_season for season in selection_seasons):
        raise ValueError("Every validation season must strictly precede the test season.")
    normalized = _normalize_candidate_predictions(
        predictions,
        season_key=season_key,
        position_key=position_key,
        target_key=target_key,
        source_key=source_key,
        candidate_key=candidate_key,
        entity_key=entity_key,
        actual_key=actual_key,
        prediction_key=prediction_key,
    )
    candidate_groups: dict[tuple[str, str, str, str], list[_CandidatePrediction]] = defaultdict(
        list
    )
    seen_rows: set[tuple[str, str, str, str, int, str]] = set()
    for row in normalized:
        row_key = (
            row.position,
            row.target_name,
            row.candidate_source,
            row.candidate_name,
            row.prediction_season,
            row.entity_id,
        )
        if row_key in seen_rows:
            raise ValueError(f"Duplicate candidate prediction row: {row_key}.")
        seen_rows.add(row_key)
        candidate_groups[
            row.position, row.target_name, row.candidate_source, row.candidate_name
        ].append(row)
    if not candidate_groups:
        raise ValueError("No candidate predictions were provided.")

    draft_relevant_keys = (
        _draft_relevant_validation_keys(
            candidate_groups,
            selection_seasons,
            draft_relevance_policy,
        )
        if draft_relevance_policy is not None
        else {}
    )

    candidate_metrics: list[dict[str, Any]] = []
    metrics_lookup: dict[tuple[str, str, str, str], dict[str, Any]] = {}
    for candidate_group in sorted(candidate_groups):
        position, target_name, source, candidate_name = candidate_group
        rows = candidate_groups[candidate_group]
        validation_rows = [
            row
            for row in rows
            if row.prediction_season in selection_seasons and row.actual_value is not None
        ]
        seasons_present = {row.prediction_season for row in validation_rows}
        missing_seasons = sorted(set(selection_seasons) - seasons_present)
        if missing_seasons:
            raise ValueError(
                f"{position}/{target_name}/{source}/{candidate_name} has no evaluable "
                f"rows for validation seasons {missing_seasons}."
            )
        test_rows = [
            row
            for row in rows
            if row.prediction_season == test_season and row.actual_value is not None
        ]
        validation = regression_metrics(
            (row.actual_value for row in validation_rows),
            (row.predicted_value for row in validation_rows),
            top_n=None,
        )
        test = regression_metrics(
            (row.actual_value for row in test_rows),
            (row.predicted_value for row in test_rows),
            top_n=None,
        )
        relevant_rows = (
            [
                row
                for row in validation_rows
                if (row.prediction_season, row.entity_id) in draft_relevant_keys[position]
            ]
            if draft_relevance_policy is not None
            else validation_rows
        )
        relevant_seasons_present = {row.prediction_season for row in relevant_rows}
        missing_relevant_seasons = sorted(set(selection_seasons) - relevant_seasons_present)
        if missing_relevant_seasons:
            raise ValueError(
                f"{position}/{target_name}/{source}/{candidate_name} has no evaluable "
                "draft-relevant rows for validation seasons "
                f"{missing_relevant_seasons}."
            )
        draft_relevant = regression_metrics(
            (row.actual_value for row in relevant_rows),
            (row.predicted_value for row in relevant_rows),
            top_n=None,
        )
        total_capture = (
            _mean_annual_top_n_capture(
                validation_rows,
                selection_seasons,
                top_n=draft_relevance_policy.top_n_for(position),
            )
            if draft_relevance_policy is not None
            and target_name == TARGET_FANTASY_POINTS_TOTAL
            else None
        )
        metric_record = {
            "position": position,
            "target_name": target_name,
            "candidate_source": source,
            "candidate_name": candidate_name,
            "validation_seasons": list(selection_seasons),
            "validation_rows": validation["rows"],
            "validation_mae": validation["mae"],
            "draft_relevant_validation_rows": draft_relevant["rows"],
            "draft_relevant_validation_mae": draft_relevant["mae"],
            "draft_relevant_validation_signed_bias": _signed_bias(relevant_rows),
            "validation_top_n_capture_rate": total_capture,
            "test_season": test_season,
            "test_rows": test["rows"],
            "test_mae": test["mae"],
        }
        candidate_metrics.append(metric_record)
        metrics_lookup[candidate_group] = metric_record

    position_targets = sorted({(key[0], key[1]) for key in candidate_groups})
    champions: list[dict[str, Any]] = []
    for position, target_name in position_targets:
        group_keys = sorted(key for key in candidate_groups if key[:2] == (position, target_name))
        baseline_keys = [key for key in group_keys if key[2] == "baseline"]
        learned_keys = [key for key in group_keys if key[2] == "learned"]
        present_baselines = {key[3] for key in baseline_keys}
        present_learned = {key[3] for key in learned_keys}
        missing_baselines = sorted(set(required_baselines) - present_baselines)
        missing_learned = sorted(set(required_learned_models) - present_learned)
        if missing_baselines:
            raise ValueError(
                f"{position}/{target_name} is missing required baselines: {missing_baselines}."
            )
        if missing_learned:
            raise ValueError(
                f"{position}/{target_name} is missing required learned models: {missing_learned}."
            )
        if not baseline_keys:
            raise ValueError(f"{position}/{target_name} has no transparent baseline.")
        _require_matched_validation_samples(
            {key: candidate_groups[key] for key in group_keys}, selection_seasons
        )
        selection_metric_key = (
            "draft_relevant_validation_mae"
            if draft_relevance_policy is not None
            else "validation_mae"
        )
        best_baseline = min(
            baseline_keys,
            key=lambda key: (
                cast(float, metrics_lookup[key][selection_metric_key]),
                cast(float, metrics_lookup[key]["validation_mae"]),
                key[3],
            ),
        )
        best_learned = (
            min(
                learned_keys,
                key=lambda key: (
                    cast(float, metrics_lookup[key][selection_metric_key]),
                    cast(float, metrics_lookup[key]["validation_mae"]),
                    key[3],
                ),
            )
            if learned_keys
            else None
        )
        baseline_selection_mae = cast(
            float, metrics_lookup[best_baseline][selection_metric_key]
        )
        baseline_pooled_mae = cast(float, metrics_lookup[best_baseline]["validation_mae"])
        comparison = (
            _bootstrap_candidate_pair(
                candidate_groups[best_learned],
                candidate_groups[best_baseline],
                selection_seasons,
                included_keys=(
                    draft_relevant_keys[position]
                    if draft_relevance_policy is not None
                    else None
                ),
                n_resamples=n_bootstrap,
                seed=seed,
            )
            if best_learned is not None
            else None
        )
        learned_selection_mae = (
            cast(float, metrics_lookup[best_learned][selection_metric_key])
            if best_learned is not None
            else None
        )
        learned_pooled_mae = (
            cast(float, metrics_lookup[best_learned]["validation_mae"])
            if best_learned is not None
            else None
        )
        learned_has_lower_selection_mae = bool(
            learned_selection_mae is not None
            and learned_selection_mae < baseline_selection_mae
        )
        learned_has_lower_pooled_mae = bool(
            learned_pooled_mae is not None and learned_pooled_mae < baseline_pooled_mae
        )
        bootstrap_supports_learned = bool(
            comparison is not None
            and comparison["ci95_upper"] is not None
            and cast(float, comparison["ci95_upper"]) < 0.0
        )
        pooled_mae_safety_gate_passed = bool(
            learned_pooled_mae is not None
            and (
                draft_relevance_policy is None
                or learned_pooled_mae
                <= baseline_pooled_mae
                * (1.0 + draft_relevance_policy.pooled_mae_regression_tolerance)
            )
        )
        baseline_capture = metrics_lookup[best_baseline]["validation_top_n_capture_rate"]
        learned_capture = (
            metrics_lookup[best_learned]["validation_top_n_capture_rate"]
            if best_learned is not None
            else None
        )
        capture_guard_required = bool(
            draft_relevance_policy is not None
            and target_name == TARGET_FANTASY_POINTS_TOTAL
        )
        capture_regression_tolerance = (
            draft_relevance_policy.max_total_top_n_capture_regression
            if draft_relevance_policy is not None
            else 0.0
        )
        total_capture_guard_passed = bool(
            not capture_guard_required
            or (
                baseline_capture is not None
                and learned_capture is not None
                and cast(float, learned_capture)
                >= cast(float, baseline_capture)
                - capture_regression_tolerance
            )
        )
        learned_wins = (
            learned_has_lower_selection_mae
            and bootstrap_supports_learned
            and pooled_mae_safety_gate_passed
            and total_capture_guard_passed
        )
        if best_learned is None:
            decision_status = "no_learned_candidate_baseline_retained"
            learned_improvement_status = "unavailable"
        elif learned_selection_mae == baseline_selection_mae:
            decision_status = (
                "draft_relevant_mae_tie_baseline_retained"
                if draft_relevance_policy is not None
                else "mae_tie_baseline_retained"
            )
            learned_improvement_status = "tie"
        elif not learned_has_lower_selection_mae:
            decision_status = (
                "learned_draft_relevant_regression_baseline_retained"
                if draft_relevance_policy is not None
                else "learned_regression_baseline_retained"
            )
            learned_improvement_status = "regression"
        elif not bootstrap_supports_learned:
            decision_status = (
                "learned_draft_relevant_improvement_inconclusive_baseline_retained"
                if draft_relevance_policy is not None
                else "learned_improvement_inconclusive_baseline_retained"
            )
            learned_improvement_status = "inconclusive"
        elif not pooled_mae_safety_gate_passed:
            decision_status = "learned_pooled_mae_safety_gate_failed_baseline_retained"
            learned_improvement_status = "pooled_regression"
        elif not total_capture_guard_passed:
            decision_status = "learned_total_capture_guard_failed_baseline_retained"
            learned_improvement_status = "ranking_regression"
        else:
            decision_status = (
                "learned_draft_relevant_improvement_selected"
                if draft_relevance_policy is not None
                else "learned_significant_improvement_selected"
            )
            learned_improvement_status = "statistically_clear"
        selected = best_learned if learned_wins and best_learned is not None else best_baseline
        selected_metrics = metrics_lookup[selected]
        selected_mae = cast(float, selected_metrics[selection_metric_key])
        champions.append(
            {
                "position": position,
                "target_name": target_name,
                "selected_source": selected[2],
                "selected_name": selected[3],
                "selection_metric": (
                    "draft_relevant_validation_mae_with_pooled_safety_gate"
                    if draft_relevance_policy is not None
                    else "pooled_validation_mae"
                ),
                "selection_value": selected_mae,
                "validation_seasons": list(selection_seasons),
                "validation_rows": selected_metrics["validation_rows"],
                "draft_relevant_validation_rows": selected_metrics[
                    "draft_relevant_validation_rows"
                ],
                "pooled_validation_mae": selected_metrics["validation_mae"],
                "reference_baseline_name": best_baseline[3],
                "reference_baseline_value": baseline_selection_mae,
                "reference_baseline_pooled_validation_mae": baseline_pooled_mae,
                "mae_improvement_over_best_baseline": baseline_selection_mae - selected_mae,
                "decision_status": decision_status,
                "learned_improvement_status": learned_improvement_status,
                "learned_has_lower_validation_mae": learned_has_lower_pooled_mae,
                "learned_has_lower_draft_relevant_mae": learned_has_lower_selection_mae,
                "bootstrap_ci_supports_learned": bootstrap_supports_learned,
                "pooled_mae_safety_gate_passed": pooled_mae_safety_gate_passed,
                "total_top_n_capture_guard_passed": (
                    total_capture_guard_passed if capture_guard_required else None
                ),
                "reference_baseline_top_n_capture_rate": baseline_capture,
                "best_learned_top_n_capture_rate": learned_capture,
                "best_learned_name": best_learned[3] if best_learned is not None else None,
                "best_learned_value": (
                    metrics_lookup[best_learned][selection_metric_key]
                    if best_learned is not None
                    else None
                ),
                "best_learned_mae_improvement": (
                    baseline_selection_mae - learned_selection_mae
                    if learned_selection_mae is not None
                    else None
                ),
                "best_learned_vs_baseline_bootstrap": comparison,
                "test_season": test_season,
                "test_rows": selected_metrics["test_rows"],
                "test_mae": selected_metrics["test_mae"],
            }
        )

    return {
        "selection_metric": (
            "draft_relevant_validation_mae_with_pooled_safety_gate"
            if draft_relevance_policy is not None
            else "pooled_validation_mae"
        ),
        "selection_rule": (
            "Select on a fixed cutoff-safe draft-relevant cohort. A learned candidate must "
            "lower cohort MAE with a paired-bootstrap 95% CI below zero, remain within the "
            "configured pooled-MAE tolerance, and preserve total-points top-N capture."
            if draft_relevance_policy is not None
            else (
                "Select on pooled validation MAE with a paired-bootstrap uncertainty gate; "
                "learned must be strictly lower than the best transparent baseline and its "
                "learned-minus-baseline 95% CI upper bound must be below zero. Ties and "
                "inconclusive improvements retain the baseline."
            )
        ),
        "draft_relevance_policy": (
            {
                "anchor_target": TARGET_FANTASY_POINTS_TOTAL,
                "anchor_baseline": draft_relevance_policy.anchor_baseline,
                "top_n_by_position": dict(draft_relevance_policy.top_n_by_position),
                "pooled_mae_regression_tolerance": (
                    draft_relevance_policy.pooled_mae_regression_tolerance
                ),
                "max_total_top_n_capture_regression": (
                    draft_relevance_policy.max_total_top_n_capture_regression
                ),
            }
            if draft_relevance_policy is not None
            else None
        ),
        "validation_seasons": list(selection_seasons),
        "test_season": test_season,
        "test_excluded_from_selection": True,
        "candidate_metrics": candidate_metrics,
        "champions": champions,
    }


@dataclass(frozen=True)
class _CandidatePrediction:
    prediction_season: int
    position: str
    target_name: str
    candidate_source: str
    candidate_name: str
    entity_id: str
    actual_value: float | None
    predicted_value: float


def _draft_relevant_validation_keys(
    candidate_groups: Mapping[
        tuple[str, str, str, str], list[_CandidatePrediction]
    ],
    validation_seasons: Sequence[int],
    policy: DraftRelevancePolicy,
) -> dict[str, set[tuple[int, str]]]:
    """Freeze one cutoff-safe cohort shared by every candidate and target."""

    positions = sorted({key[0] for key in candidate_groups})
    output: dict[str, set[tuple[int, str]]] = {}
    for position in positions:
        anchor_key = (
            position,
            TARGET_FANTASY_POINTS_TOTAL,
            "baseline",
            policy.anchor_baseline,
        )
        anchor_rows = candidate_groups.get(anchor_key)
        if anchor_rows is None:
            raise ValueError(
                "Draft-relevant selection requires the cutoff-safe anchor "
                f"{position}/{TARGET_FANTASY_POINTS_TOTAL}/baseline/"
                f"{policy.anchor_baseline}."
            )
        top_n = policy.top_n_for(position)
        selected: set[tuple[int, str]] = set()
        for season in validation_seasons:
            season_rows = [row for row in anchor_rows if row.prediction_season == season]
            if len(season_rows) < top_n:
                raise ValueError(
                    f"Draft-relevant anchor {position}/{season} has {len(season_rows)} "
                    f"rows; {top_n} are required."
                )
            ordered = sorted(
                season_rows,
                key=lambda row: (-row.predicted_value, row.entity_id),
            )
            selected.update((season, row.entity_id) for row in ordered[:top_n])
        output[position] = selected
    return output


def _mean_annual_top_n_capture(
    rows: Sequence[_CandidatePrediction],
    validation_seasons: Sequence[int],
    *,
    top_n: int,
) -> float:
    """Measure mean annual actual/predicted top-N overlap without pooling seasons."""

    captures: list[float] = []
    for season in validation_seasons:
        season_rows = [
            row
            for row in rows
            if row.prediction_season == season and row.actual_value is not None
        ]
        if len(season_rows) < top_n:
            raise ValueError(
                f"Top-N capture for {season} has {len(season_rows)} evaluable rows; "
                f"{top_n} are required."
            )
        metrics = regression_metrics(
            (row.actual_value for row in season_rows),
            (row.predicted_value for row in season_rows),
            top_n=top_n,
            entity_ids=(row.entity_id for row in season_rows),
        )
        capture = metrics["top_n_capture_rate"]
        if capture is None:
            raise ValueError(f"Top-N capture is unavailable for validation season {season}.")
        captures.append(float(capture))
    return math.fsum(captures) / len(captures)


def _signed_bias(rows: Sequence[_CandidatePrediction]) -> float | None:
    errors = [
        row.predicted_value - row.actual_value
        for row in rows
        if row.actual_value is not None
    ]
    return math.fsum(errors) / len(errors) if errors else None


def _paired_values(
    y_true: Iterable[object], y_pred: Iterable[object]
) -> tuple[FloatArray, FloatArray, NDArray[np.int64], int]:
    actual = _float_array(y_true, "y_true")
    predicted = _float_array(y_pred, "y_pred")
    _require_equal_lengths(actual, predicted)
    valid = np.isfinite(actual)
    if bool(np.any(valid & ~np.isfinite(predicted))):
        raise ValueError("Every available actual must have a finite prediction.")
    indexes = np.flatnonzero(valid).astype(np.int64, copy=False)
    return actual[valid], predicted[valid], indexes, int(actual.size)


def _float_array(values: Iterable[object], label: str) -> FloatArray:
    raw = list(values)
    output = np.empty(len(raw), dtype=np.float64)
    for index, value in enumerate(raw):
        if value is None:
            output[index] = np.nan
            continue
        try:
            output[index] = float(cast(Any, value))
        except (TypeError, ValueError) as exc:
            raise ValueError(f"{label} contains a non-numeric value at row {index}.") from exc
    return output


def _require_equal_lengths(*arrays: FloatArray) -> None:
    lengths = {int(array.size) for array in arrays}
    if len(lengths) != 1:
        raise ValueError("Evaluation arrays must have equal lengths.")


def _filtered_entity_ids(
    entity_ids: Iterable[object] | None,
    original_rows: int,
    valid_indexes: NDArray[np.int64],
) -> list[str]:
    if entity_ids is None:
        return [str(int(index)) for index in valid_indexes]
    raw = list(entity_ids)
    if len(raw) != original_rows:
        raise ValueError("entity_ids must have the same length as the evaluation arrays.")
    filtered = [str(raw[int(index)]) for index in valid_indexes]
    if len(set(filtered)) != len(filtered):
        raise ValueError("entity_ids must be unique among evaluated rows.")
    return filtered


def _top_n_capture(
    actual: FloatArray,
    predicted: FloatArray,
    entity_ids: Sequence[str],
    requested_top_n: int,
) -> dict[str, int | float | None]:
    count = min(requested_top_n, int(actual.size))
    if count == 0:
        return {"top_n": 0, "top_n_capture_rate": None}
    actual_order = _descending_order(actual, entity_ids)
    predicted_order = _descending_order(predicted, entity_ids)
    actual_top = {entity_ids[int(index)] for index in actual_order[:count]}
    predicted_top = {entity_ids[int(index)] for index in predicted_order[:count]}
    return {
        "top_n": count,
        "top_n_capture_rate": len(actual_top & predicted_top) / count,
    }


def _descending_order(values: FloatArray, entity_ids: Sequence[str]) -> NDArray[np.int64]:
    ids = np.asarray(entity_ids, dtype=np.str_)
    return np.lexsort((ids, -values)).astype(np.int64, copy=False)


def _spearman(actual: FloatArray, predicted: FloatArray) -> float | None:
    if actual.size < 2:
        return None
    actual_ranks = _average_ranks(actual)
    predicted_ranks = _average_ranks(predicted)
    actual_centered = actual_ranks - np.mean(actual_ranks)
    predicted_centered = predicted_ranks - np.mean(predicted_ranks)
    denominator = float(
        np.sqrt(np.sum(np.square(actual_centered)) * np.sum(np.square(predicted_centered)))
    )
    if denominator == 0.0:
        return None
    return float(np.sum(actual_centered * predicted_centered) / denominator)


def _average_ranks(values: FloatArray) -> FloatArray:
    order = np.argsort(values, kind="stable")
    ranks = np.empty(values.size, dtype=np.float64)
    start = 0
    while start < values.size:
        end = start + 1
        while end < values.size and values[order[end]] == values[order[start]]:
            end += 1
        ranks[order[start:end]] = (start + 1 + end) / 2.0
        start = end
    return ranks


def _pinball_loss(actual: FloatArray, predicted_quantile: FloatArray, quantile: float) -> float:
    residual = actual - predicted_quantile
    return float(np.mean(np.maximum(quantile * residual, (quantile - 1.0) * residual)))


def _as_records(records: object) -> list[dict[str, Any]]:
    to_dict = getattr(records, "to_dict", None)
    if callable(to_dict):
        raw_records = cast(Any, to_dict)(orient="records")
    else:
        if isinstance(records, Mapping):
            raise TypeError("records must be a row iterable, not one mapping.")
        try:
            raw_records = list(cast(Iterable[object], records))
        except TypeError as exc:
            raise TypeError("records must be an iterable of mappings or a DataFrame.") from exc
    if not isinstance(raw_records, list):
        raise TypeError("DataFrame-style to_dict must return a record list.")
    normalized: list[dict[str, Any]] = []
    for index, row in enumerate(raw_records):
        if not isinstance(row, Mapping):
            raise TypeError(f"Evaluation row {index} is not a mapping.")
        normalized.append({str(key): value for key, value in row.items()})
    return normalized


def _normalize_candidate_predictions(
    predictions: object,
    *,
    season_key: str,
    position_key: str,
    target_key: str,
    source_key: str,
    candidate_key: str,
    entity_key: str,
    actual_key: str,
    prediction_key: str,
) -> list[_CandidatePrediction]:
    records = _as_records(predictions)
    required = (
        season_key,
        position_key,
        target_key,
        source_key,
        candidate_key,
        entity_key,
        actual_key,
        prediction_key,
    )
    normalized: list[_CandidatePrediction] = []
    for index, record in enumerate(records):
        missing = [key for key in required if key not in record]
        if missing:
            raise KeyError(f"Candidate prediction row {index} is missing columns: {missing}.")
        source = str(record[source_key])
        if source not in {"baseline", "learned"}:
            raise ValueError(f"Candidate prediction row {index} has unsupported source {source!r}.")
        actual = _optional_actual(record[actual_key], index)
        predicted = _required_prediction(record[prediction_key], index)
        normalized.append(
            _CandidatePrediction(
                prediction_season=int(record[season_key]),
                position=str(record[position_key]),
                target_name=str(record[target_key]),
                candidate_source=source,
                candidate_name=str(record[candidate_key]),
                entity_id=str(record[entity_key]),
                actual_value=actual,
                predicted_value=predicted,
            )
        )
    return normalized


def _optional_actual(value: object, row_index: int) -> float | None:
    if value is None:
        return None
    try:
        numeric = float(cast(Any, value))
    except (TypeError, ValueError) as exc:
        raise ValueError(f"Actual value at row {row_index} is not numeric.") from exc
    if math.isnan(numeric):
        return None
    if not math.isfinite(numeric):
        raise ValueError(f"Actual value at row {row_index} must be finite or missing.")
    return numeric


def _required_prediction(value: object, row_index: int) -> float:
    try:
        numeric = float(cast(Any, value))
    except (TypeError, ValueError) as exc:
        raise ValueError(f"Prediction at row {row_index} is not numeric.") from exc
    if not math.isfinite(numeric):
        raise ValueError(f"Prediction at row {row_index} must be finite.")
    return numeric


def _require_matched_validation_samples(
    candidates: Mapping[tuple[str, str, str, str], list[_CandidatePrediction]],
    validation_seasons: Sequence[int],
) -> None:
    expected: dict[tuple[int, str], float] | None = None
    expected_name = ""
    for candidate_key in sorted(candidates):
        sample = {
            (row.prediction_season, row.entity_id): row.actual_value
            for row in candidates[candidate_key]
            if row.prediction_season in validation_seasons and row.actual_value is not None
        }
        if expected is None:
            expected = sample
            expected_name = candidate_key[3]
            continue
        if sample.keys() != expected.keys():
            raise ValueError(
                f"Validation sample mismatch between {expected_name} and {candidate_key[3]}."
            )
        if any(not math.isclose(sample[key], expected[key], abs_tol=1e-12) for key in sample):
            raise ValueError(
                f"Validation actual mismatch between {expected_name} and {candidate_key[3]}."
            )


def _bootstrap_candidate_pair(
    candidate_rows: Sequence[_CandidatePrediction],
    reference_rows: Sequence[_CandidatePrediction],
    validation_seasons: Sequence[int],
    *,
    included_keys: set[tuple[int, str]] | None = None,
    n_resamples: int,
    seed: int,
) -> dict[str, int | float | str | None]:
    candidate = {
        (row.prediction_season, row.entity_id): row
        for row in candidate_rows
        if row.prediction_season in validation_seasons and row.actual_value is not None
        and (
            included_keys is None
            or (row.prediction_season, row.entity_id) in included_keys
        )
    }
    reference = {
        (row.prediction_season, row.entity_id): row
        for row in reference_rows
        if row.prediction_season in validation_seasons and row.actual_value is not None
        and (
            included_keys is None
            or (row.prediction_season, row.entity_id) in included_keys
        )
    }
    keys = sorted(candidate)
    return paired_bootstrap_mae_difference(
        (reference[key].actual_value for key in keys),
        (candidate[key].predicted_value for key in keys),
        (reference[key].predicted_value for key in keys),
        n_resamples=n_resamples,
        seed=seed,
    )
