from __future__ import annotations

import json
import math
from typing import Any, cast

import pandas as pd
import pytest

from fantasy_draft_ai.models.player_projection.config import DraftRelevancePolicy
from fantasy_draft_ai.models.player_projection.evaluation import (
    assign_projection_tiers,
    interval_metrics,
    paired_bootstrap_mae_difference,
    regression_metrics,
    segment_regression_metrics,
    select_champions,
)


def test_regression_metrics_are_json_safe_and_define_top_n_capture() -> None:
    metrics = regression_metrics(
        [1.0, 2.0, 3.0, 4.0, None],
        [1.0, 3.0, 2.0, 4.0, 999.0],
        top_n=2,
        entity_ids=["a", "b", "c", "d", "missing"],
    )

    assert metrics == {
        "rows": 4,
        "mae": 0.5,
        "rmse": pytest.approx(math.sqrt(0.5)),
        "median_absolute_error": 0.5,
        "spearman_rank_correlation": pytest.approx(0.8),
        "top_n": 2,
        "top_n_capture_rate": 0.5,
    }
    json.dumps(metrics, allow_nan=False)


def test_regression_metrics_return_none_instead_of_nan_when_unavailable() -> None:
    empty = regression_metrics([None, float("nan")], [1.0, 2.0])
    constant = regression_metrics([1.0, 1.0], [2.0, 3.0], entity_ids=["a", "b"])

    assert empty["rows"] == 0
    assert empty["mae"] is None
    assert empty["spearman_rank_correlation"] is None
    assert constant["spearman_rank_correlation"] is None
    json.dumps({"empty": empty, "constant": constant}, allow_nan=False)


def test_projection_tiers_and_dataframe_segments_are_deterministic() -> None:
    tiers = assign_projection_tiers([40.0, 30.0, 20.0, 10.0], entity_ids=["a", "b", "c", "d"])
    assert tiers == ["top", "middle", "middle", "lower"]

    frame = pd.DataFrame(
        [
            {
                "player_id": "a",
                "position": "QB",
                "experience_group": "rookie",
                "projection_tier": "top",
                "actual_value": 1.0,
                "predicted_value": 2.0,
            },
            {
                "player_id": "b",
                "position": "QB",
                "experience_group": "veteran",
                "projection_tier": "middle",
                "actual_value": 2.0,
                "predicted_value": 2.0,
            },
            {
                "player_id": "c",
                "position": "RB",
                "experience_group": "veteran",
                "projection_tier": "lower",
                "actual_value": 3.0,
                "predicted_value": 1.0,
            },
        ]
    )

    first = segment_regression_metrics(frame)
    second = segment_regression_metrics(frame)

    assert first == second
    assert {(row["segment_dimension"], row["segment"]) for row in first} == {
        ("position", "QB"),
        ("position", "RB"),
        ("experience_group", "rookie"),
        ("experience_group", "veteran"),
        ("projection_tier", "top"),
        ("projection_tier", "middle"),
        ("projection_tier", "lower"),
    }
    veteran = next(
        row
        for row in first
        if row["segment_dimension"] == "experience_group" and row["segment"] == "veteran"
    )
    assert veteran["rows"] == 2
    assert veteran["mae"] == 1.0
    json.dumps(first, allow_nan=False)


def test_projection_tiers_are_symmetric_at_exact_midpoint_boundaries() -> None:
    tiers = assign_projection_tiers(
        [60.0, 50.0, 40.0, 30.0, 20.0, 10.0],
        entity_ids=["a", "b", "c", "d", "e", "f"],
    )

    assert tiers == ["top", "top", "middle", "middle", "lower", "lower"]
    assert tiers.count("top") == tiers.count("lower")


def test_interval_metrics_report_coverage_width_and_three_pinball_losses() -> None:
    metrics = interval_metrics(
        [0.0, 10.0, None],
        [-1.0, 8.0, -100.0],
        [0.0, 9.0, 0.0],
        [1.0, 12.0, 100.0],
    )

    assert metrics == {
        "rows": 2,
        "empirical_coverage_p10_p90": 1.0,
        "mean_interval_width_p10_p90": 3.0,
        "pinball_loss_p10": pytest.approx(0.15),
        "pinball_loss_p50": pytest.approx(0.25),
        "pinball_loss_p90": pytest.approx(0.15),
    }
    json.dumps(metrics, allow_nan=False)


def test_interval_metrics_reject_crossed_quantiles() -> None:
    with pytest.raises(ValueError, match="P10 <= P50 <= P90"):
        interval_metrics([10.0], [11.0], [10.0], [12.0])


def test_paired_bootstrap_mae_difference_is_reproducible_and_directional() -> None:
    first = paired_bootstrap_mae_difference(
        [0.0, 10.0, 20.0, 30.0],
        [0.0, 10.0, 20.0, 30.0],
        [5.0, 15.0, 25.0, 35.0],
        n_resamples=500,
    )
    second = paired_bootstrap_mae_difference(
        [0.0, 10.0, 20.0, 30.0],
        [0.0, 10.0, 20.0, 30.0],
        [5.0, 15.0, 25.0, 35.0],
        n_resamples=500,
    )

    assert first == second
    assert first["mae_difference_candidate_minus_reference"] == -5.0
    assert first["ci95_lower"] == -5.0
    assert first["ci95_upper"] == -5.0
    assert first["direction"] == "candidate_lower_mae"
    assert first["seed"] == 42
    json.dumps(first, allow_nan=False)


def test_champion_selection_uses_pooled_validation_only_and_retains_baseline_ties() -> None:
    predictions = _champion_fixture()

    result = select_champions(
        predictions,
        required_baselines=("baseline_a", "baseline_b"),
        required_learned_models=("ridge", "hist_gradient_boosting"),
        n_bootstrap=200,
    )

    champions = {(row["position"], row["target_name"]): row for row in result["champions"]}
    quarterback = champions["QB", "fantasy_points_per_game"]
    running_back = champions["RB", "fantasy_points_per_game"]
    assert quarterback["selected_source"] == "baseline"
    assert quarterback["selected_name"] == "baseline_a"
    assert quarterback["selection_value"] == 1.0
    assert quarterback["decision_status"] == "mae_tie_baseline_retained"
    assert quarterback["learned_improvement_status"] == "tie"
    # Ridge is perfect in the 2025 QB test rows, but that cannot change selection.
    assert quarterback["test_mae"] == 100.0
    assert (
        quarterback["best_learned_vs_baseline_bootstrap"][
            "mae_difference_candidate_minus_reference"
        ]
        == 0.0
    )
    assert running_back["selected_source"] == "learned"
    assert running_back["selected_name"] == "ridge"
    assert running_back["selection_value"] == 0.5
    assert running_back["mae_improvement_over_best_baseline"] == 0.5
    assert running_back["decision_status"] == "learned_significant_improvement_selected"
    assert running_back["bootstrap_ci_supports_learned"] is True
    # Ridge is intentionally awful in 2025; validation still owns the decision.
    assert running_back["test_mae"] == 100.0
    assert result["validation_seasons"] == [2020, 2021, 2022, 2023, 2024]
    assert result["test_season"] == 2025
    assert result["test_excluded_from_selection"] is True
    assert all(row["validation_rows"] == 10 for row in result["candidate_metrics"])
    json.dumps(result, allow_nan=False)


def test_champion_selection_promotes_a_bootstrap_supported_improvement() -> None:
    champion = _single_candidate_champion([0.5] * 10)

    assert champion["selected_source"] == "learned"
    assert champion["selected_name"] == "ridge"
    assert champion["decision_status"] == "learned_significant_improvement_selected"
    assert champion["learned_improvement_status"] == "statistically_clear"
    assert champion["learned_has_lower_validation_mae"] is True
    assert champion["bootstrap_ci_supports_learned"] is True
    assert champion["best_learned_vs_baseline_bootstrap"]["ci95_upper"] < 0.0


def test_champion_selection_retains_baseline_for_inconclusive_small_improvement() -> None:
    # Paired error differences are -1 for six rows and +1 for four. The pooled
    # learned MAE is lower, but its bootstrap interval still crosses zero.
    champion = _single_candidate_champion([0.0] * 6 + [2.0] * 4)

    assert champion["selected_source"] == "baseline"
    assert champion["selected_name"] == "baseline"
    assert champion["selection_value"] == 1.0
    assert champion["best_learned_value"] == pytest.approx(0.8)
    assert champion["best_learned_mae_improvement"] == pytest.approx(0.2)
    assert champion["decision_status"] == ("learned_improvement_inconclusive_baseline_retained")
    assert champion["learned_improvement_status"] == "inconclusive"
    assert champion["learned_has_lower_validation_mae"] is True
    assert champion["bootstrap_ci_supports_learned"] is False
    comparison = champion["best_learned_vs_baseline_bootstrap"]
    assert comparison["mae_difference_candidate_minus_reference"] == pytest.approx(-0.2)
    assert comparison["ci95_upper"] >= 0.0
    assert comparison["direction"] == "uncertain"


def test_champion_selection_retains_baseline_for_mae_tie() -> None:
    champion = _single_candidate_champion([1.0] * 10)

    assert champion["selected_source"] == "baseline"
    assert champion["decision_status"] == "mae_tie_baseline_retained"
    assert champion["learned_improvement_status"] == "tie"
    assert champion["learned_has_lower_validation_mae"] is False
    assert champion["bootstrap_ci_supports_learned"] is False


def test_champion_selection_retains_baseline_for_learned_regression() -> None:
    champion = _single_candidate_champion([1.5] * 10)

    assert champion["selected_source"] == "baseline"
    assert champion["decision_status"] == "learned_regression_baseline_retained"
    assert champion["learned_improvement_status"] == "regression"
    assert champion["learned_has_lower_validation_mae"] is False
    assert champion["best_learned_mae_improvement"] == -0.5
    comparison = champion["best_learned_vs_baseline_bootstrap"]
    assert comparison["ci95_lower"] > 0.0
    assert comparison["direction"] == "reference_lower_mae"


def test_champion_selection_rejects_unmatched_validation_samples() -> None:
    predictions = _champion_fixture()
    predictions = [
        row
        for row in predictions
        if not (
            row["position"] == "QB"
            and row["candidate_name"] == "ridge"
            and row["prediction_season"] == 2022
            and row["player_id"] == "QB-0"
        )
    ]

    with pytest.raises(ValueError, match="sample mismatch"):
        select_champions(
            predictions,
            required_baselines=("baseline_a", "baseline_b"),
            required_learned_models=("ridge", "hist_gradient_boosting"),
            n_bootstrap=20,
        )


def test_draft_relevant_selection_rejects_a_pooled_mae_winner_on_the_fixed_cohort() -> None:
    result = _select_draft_relevant_champion(
        baseline_predictions=(99.0, 80.0, 20.0),
        learned_predictions=(90.0, 90.0, 0.0),
    )

    champion = cast(dict[str, Any], result["champions"][0])
    assert champion["selected_source"] == "baseline"
    assert champion["decision_status"] == (
        "learned_draft_relevant_regression_baseline_retained"
    )
    assert champion["learned_has_lower_validation_mae"] is True
    assert champion["learned_has_lower_draft_relevant_mae"] is False
    assert champion["selection_metric"] == (
        "draft_relevant_validation_mae_with_pooled_safety_gate"
    )
    assert champion["reference_baseline_value"] == 1.0
    assert champion["best_learned_value"] == 10.0


def test_draft_relevant_selection_enforces_the_pooled_mae_safety_gate() -> None:
    result = _select_draft_relevant_champion(
        baseline_predictions=(91.0, 90.0, 0.0),
        learned_predictions=(99.0, 40.0, 50.0),
    )

    champion = cast(dict[str, Any], result["champions"][0])
    assert champion["selected_source"] == "baseline"
    assert champion["learned_has_lower_draft_relevant_mae"] is True
    assert champion["bootstrap_ci_supports_learned"] is True
    assert champion["pooled_mae_safety_gate_passed"] is False
    assert champion["decision_status"] == (
        "learned_pooled_mae_safety_gate_failed_baseline_retained"
    )


def test_draft_relevant_total_selection_enforces_the_top_n_capture_guard() -> None:
    result = _select_draft_relevant_champion(
        baseline_predictions=(80.0, 70.0, 0.0),
        learned_predictions=(90.0, 95.0, 0.0),
    )

    champion = cast(dict[str, Any], result["champions"][0])
    assert champion["selected_source"] == "baseline"
    assert champion["learned_has_lower_draft_relevant_mae"] is True
    assert champion["pooled_mae_safety_gate_passed"] is True
    assert champion["reference_baseline_top_n_capture_rate"] == 1.0
    assert champion["best_learned_top_n_capture_rate"] == 0.0
    assert champion["total_top_n_capture_guard_passed"] is False
    assert champion["decision_status"] == (
        "learned_total_capture_guard_failed_baseline_retained"
    )


def test_draft_relevant_selection_promotes_a_candidate_that_clears_every_gate() -> None:
    result = _select_draft_relevant_champion(
        baseline_predictions=(90.0, 70.0, 0.0),
        learned_predictions=(98.0, 80.0, 0.0),
    )

    champion = cast(dict[str, Any], result["champions"][0])
    assert champion["selected_source"] == "learned"
    assert champion["decision_status"] == "learned_draft_relevant_improvement_selected"
    assert champion["bootstrap_ci_supports_learned"] is True
    assert champion["pooled_mae_safety_gate_passed"] is True
    assert champion["total_top_n_capture_guard_passed"] is True
    assert result["draft_relevance_policy"] == {
        "anchor_target": "fantasy_points_total",
        "anchor_baseline": "weighted_components",
        "top_n_by_position": {"RB": 1},
        "pooled_mae_regression_tolerance": 0.05,
        "max_total_top_n_capture_regression": 0.05,
    }


def test_draft_relevant_selection_fails_closed_without_the_anchor_baseline() -> None:
    rows = _draft_relevance_fixture(
        baseline_predictions=(90.0, 70.0, 0.0),
        learned_predictions=(98.0, 80.0, 0.0),
    )
    for row in rows:
        if row["candidate_source"] == "baseline":
            row["candidate_name"] = "other_baseline"

    with pytest.raises(ValueError, match="requires the cutoff-safe anchor"):
        select_champions(
            rows,
            required_baselines=("other_baseline",),
            required_learned_models=("ridge",),
            n_bootstrap=50,
            draft_relevance_policy=_draft_relevance_policy(),
        )


def _draft_relevance_policy() -> DraftRelevancePolicy:
    return DraftRelevancePolicy(top_n_by_position=(("RB", 1),))


def _select_draft_relevant_champion(
    *,
    baseline_predictions: tuple[float, float, float],
    learned_predictions: tuple[float, float, float],
) -> dict[str, Any]:
    return select_champions(
        _draft_relevance_fixture(
            baseline_predictions=baseline_predictions,
            learned_predictions=learned_predictions,
        ),
        required_baselines=("weighted_components",),
        required_learned_models=("ridge",),
        n_bootstrap=200,
        draft_relevance_policy=_draft_relevance_policy(),
    )


def _draft_relevance_fixture(
    *,
    baseline_predictions: tuple[float, float, float],
    learned_predictions: tuple[float, float, float],
) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    players = (("star", 100.0), ("challenger", 90.0), ("depth", 0.0))
    for season in range(2020, 2026):
        for player_index, (player_id, actual) in enumerate(players):
            for source, candidate, predictions in (
                ("baseline", "weighted_components", baseline_predictions),
                ("learned", "ridge", learned_predictions),
            ):
                rows.append(
                    {
                        "prediction_season": season,
                        "position": "RB",
                        "target_name": "fantasy_points_total",
                        "candidate_source": source,
                        "candidate_name": candidate,
                        "player_id": player_id,
                        "actual_value": actual,
                        "predicted_value": predictions[player_index],
                    }
                )
    return rows


def _champion_fixture() -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    candidates = (
        ("baseline", "baseline_a"),
        ("baseline", "baseline_b"),
        ("learned", "ridge"),
        ("learned", "hist_gradient_boosting"),
    )
    validation_errors = {
        "QB": {
            "baseline_a": 1.0,
            "baseline_b": 2.0,
            "ridge": -1.0,
            "hist_gradient_boosting": 3.0,
        },
        "RB": {
            "baseline_a": 1.0,
            "baseline_b": 2.0,
            "ridge": 0.5,
            "hist_gradient_boosting": 0.75,
        },
    }
    test_errors = {
        "QB": {
            "baseline_a": 100.0,
            "baseline_b": 50.0,
            "ridge": 0.0,
            "hist_gradient_boosting": 0.0,
        },
        "RB": {
            "baseline_a": 0.0,
            "baseline_b": 0.0,
            "ridge": 100.0,
            "hist_gradient_boosting": 100.0,
        },
    }
    for position in ("QB", "RB"):
        for season in range(2020, 2026):
            for player_index in range(2):
                actual = float(10 + player_index + season - 2020)
                for source, candidate in candidates:
                    error = (
                        test_errors[position][candidate]
                        if season == 2025
                        else validation_errors[position][candidate]
                    )
                    rows.append(
                        {
                            "prediction_season": season,
                            "position": position,
                            "target_name": "fantasy_points_per_game",
                            "candidate_source": source,
                            "candidate_name": candidate,
                            "player_id": f"{position}-{player_index}",
                            "actual_value": actual,
                            "predicted_value": actual + error,
                        }
                    )
    return rows


def _single_candidate_champion(learned_absolute_errors: list[float]) -> dict[str, Any]:
    if len(learned_absolute_errors) != 10:
        raise ValueError("The focused champion fixture requires ten validation errors.")
    rows: list[dict[str, Any]] = []
    error_index = 0
    for season in range(2020, 2025):
        for player_index in range(2):
            actual = float(20 + player_index)
            for source, candidate, error in (
                ("baseline", "baseline", 1.0),
                ("learned", "ridge", learned_absolute_errors[error_index]),
            ):
                rows.append(
                    {
                        "prediction_season": season,
                        "position": "WR",
                        "target_name": "fantasy_points_total",
                        "candidate_source": source,
                        "candidate_name": candidate,
                        "player_id": f"WR-{player_index}",
                        "actual_value": actual,
                        "predicted_value": actual + error,
                    }
                )
            error_index += 1
    for source, candidate in (("baseline", "baseline"), ("learned", "ridge")):
        rows.append(
            {
                "prediction_season": 2025,
                "position": "WR",
                "target_name": "fantasy_points_total",
                "candidate_source": source,
                "candidate_name": candidate,
                "player_id": "WR-test",
                "actual_value": 20.0,
                "predicted_value": 20.0,
            }
        )
    result = select_champions(
        rows,
        required_baselines=("baseline",),
        required_learned_models=("ridge",),
        n_bootstrap=1_000,
    )
    return cast(dict[str, Any], result["champions"][0])
