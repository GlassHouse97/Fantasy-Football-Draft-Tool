from __future__ import annotations

import pytest

from fantasy_draft_ai.models.adp.availability import (
    conditional_normal_availability,
    estimate_availability,
    estimate_pick_spread,
    normal_survival,
)
from fantasy_draft_ai.models.adp.config import (
    AvailabilityConfig,
    FallbackBand,
    load_availability_config,
)
from fantasy_draft_ai.models.adp.movement import AdpIdentity


def _config() -> AvailabilityConfig:
    return AvailabilityConfig(
        range_sigma_divisor=4.0,
        minimum_standard_deviation=1.0,
        fallback_assumption_label="test_fallback_assumption",
        fallback_bands={
            "DEFAULT": (FallbackBand(1, None, 15),),
            "WR": (
                FallbackBand(1, 60, 7),
                FallbackBand(60, None, 12),
            ),
        },
    )


def _estimate(next_pick: float, **overrides: object):  # type: ignore[no-untyped-def]
    values = {
        "identity": AdpIdentity("ffc", "source-1", "player-1"),
        "position": "WR",
        "average_pick": 30.0,
        "current_pick": 20.0,
        "next_pick": next_pick,
        "observed_standard_deviation": 6.0,
        "minimum_pick": 10.0,
        "maximum_pick": 50.0,
        "sample_size": 100,
        "config": _config(),
    }
    values.update(overrides)
    return estimate_availability(**values)  # type: ignore[arg-type]


def test_spread_evidence_priority_is_observed_then_range_then_labeled_fallback() -> None:
    config = _config()
    observed = estimate_pick_spread(
        position="WR",
        average_pick=30,
        observed_standard_deviation=6,
        minimum_pick=10,
        maximum_pick=50,
        sample_size=100,
        config=config,
    )
    ranged = estimate_pick_spread(
        position="WR",
        average_pick=30,
        observed_standard_deviation=None,
        minimum_pick=10,
        maximum_pick=50,
        sample_size=50,
        config=config,
    )
    fallback = estimate_pick_spread(
        position="WR",
        average_pick=70,
        observed_standard_deviation=None,
        minimum_pick=None,
        maximum_pick=None,
        sample_size=None,
        config=config,
    )

    assert observed.method == "observed_source_stddev"
    assert observed.standard_deviation == 6
    assert observed.fallback_used is False
    assert ranged.method == "min_max_derived"
    assert ranged.standard_deviation == 10
    assert ranged.evidence_label == "source_min_max_range_divided_by_4"
    assert fallback.method == "configured_fallback"
    assert fallback.standard_deviation == 12
    assert fallback.evidence_label == "test_fallback_assumption"
    assert fallback.fallback_used is True


def test_availability_probabilities_are_bounded_complementary_and_monotonic() -> None:
    near = _estimate(25)
    far = _estimate(35)

    for estimate in (near, far):
        assert 0 <= estimate.probability_selected_before_next_pick <= 1
        assert 0 <= estimate.probability_available_at_next_pick <= 1
        assert (
            estimate.probability_selected_before_next_pick
            + estimate.probability_available_at_next_pick
        ) == pytest.approx(1.0)
        assert estimate.spread_method == "observed_source_stddev"
        assert estimate.sample_size == 100
    assert far.probability_selected_before_next_pick > near.probability_selected_before_next_pick
    assert far.probability_available_at_next_pick < near.probability_available_at_next_pick


def test_consecutive_picks_have_no_intervening_selection_and_extreme_tails_are_stable() -> None:
    consecutive = _estimate(21)
    tail = _estimate(
        202,
        average_pick=1.0,
        current_pick=200.0,
        observed_standard_deviation=1.0,
    )

    assert consecutive.probability_selected_before_next_pick == 0
    assert consecutive.probability_available_at_next_pick == 1
    assert 0 <= tail.probability_available_at_next_pick <= 1
    assert 0 <= tail.probability_selected_before_next_pick <= 1
    assert (
        tail.probability_available_at_next_pick + tail.probability_selected_before_next_pick
    ) == pytest.approx(1)
    assert conditional_normal_availability(
        average_pick=30,
        current_pick=20,
        next_pick=21,
        standard_deviation=6,
    ) == pytest.approx(1)
    assert 0 <= conditional_normal_availability(
        average_pick=1,
        current_pick=200,
        next_pick=202,
        standard_deviation=1,
    ) <= 1


def test_normal_survival_does_not_require_scipy_and_validates_scale() -> None:
    assert normal_survival(0, mean=0, standard_deviation=1) == pytest.approx(0.5)
    assert normal_survival(-10, mean=0, standard_deviation=1) > 0.999
    assert normal_survival(10, mean=0, standard_deviation=1) < 1e-20
    with pytest.raises(ValueError, match="standard_deviation"):
        normal_survival(1, mean=0, standard_deviation=0)


def test_versioned_fallback_config_loads_and_invalid_pick_order_is_rejected() -> None:
    loaded = load_availability_config()

    assert loaded.fallback_for(position="RB", average_pick=30).standard_deviation == 7
    assert loaded.fallback_for(position="UNKNOWN", average_pick=150).standard_deviation == 18
    with pytest.raises(ValueError, match="greater than current_pick"):
        _estimate(20)
