from __future__ import annotations

from datetime import UTC, datetime, timedelta

import pytest

from fantasy_draft_ai.models.adp.movement import (
    AdpIdentity,
    AdpObservation,
    movement_baselines_as_of,
    movement_features_as_of,
)

BASE = datetime(2026, 7, 1, 12, tzinfo=UTC)


def _observation(
    day: int,
    adp: float,
    *,
    source: str = "ffc",
    source_row: str = "source-7",
    player_id: str | None = "canonical-7",
) -> AdpObservation:
    return AdpObservation(
        identity=AdpIdentity(
            source=source,
            raw_source_row_id=source_row,
            player_id=player_id,
        ),
        captured_at=BASE + timedelta(days=day),
        average_pick=adp,
    )


def test_identity_never_depends_on_display_name_and_unresolved_rows_stay_source_scoped() -> None:
    canonical = AdpIdentity("FFC", "row-a", "player-1")
    same_player_other_source = AdpIdentity("espn", "row-b", "player-1")
    unresolved = AdpIdentity("FFC", "row-a")

    assert canonical.key == same_player_other_source.key == "player:player-1"
    assert unresolved.key == "source:ffc:row-a"
    assert not hasattr(canonical, "player_name")
    with pytest.raises(ValueError, match="raw_source_row_id"):
        AdpIdentity("ffc", "")


def test_cutoff_safe_features_include_lags_rates_volatility_counts_and_source_spread() -> None:
    ffc = [
        _observation(0, 30),
        _observation(1, 28),
        _observation(3, 25),
        _observation(7, 20),
        _observation(14, 18),
    ]
    espn = _observation(13, 22, source="espn", source_row="espn-7")
    future = _observation(15, 999)

    features = movement_features_as_of([*ffc, espn, future], cutoff_at=BASE + timedelta(days=14))
    ffc_features = next(row for row in features if row.identity.source == "ffc")

    assert ffc_features.current_adp == 18
    assert ffc_features.prior_observed_at == BASE + timedelta(days=7)
    assert ffc_features.prior_adp == 20
    assert ffc_features.elapsed_days == 7
    assert ffc_features.change_1d == -2
    assert ffc_features.change_3d == -2
    assert ffc_features.change_7d == -2
    assert ffc_features.change_14d == -12
    assert ffc_features.velocity_picks_per_day == pytest.approx(-2 / 7)
    assert ffc_features.acceleration_picks_per_day_squared == pytest.approx(27 / 154)
    assert ffc_features.rolling_volatility_14d == pytest.approx(4.578209256903839)
    assert ffc_features.source_spread == 4
    assert ffc_features.source_count == 2
    assert ffc_features.observation_count == 5
    assert ffc_features.identity_observation_count == 6
    assert all(row.current_adp != 999 for row in features)


def test_unresolved_source_rows_are_not_joined_for_source_spread() -> None:
    observations = [
        _observation(0, 30, source="ffc", source_row="same-name", player_id=None),
        _observation(0, 40, source="espn", source_row="same-name", player_id=None),
    ]

    features = movement_features_as_of(observations, cutoff_at=BASE)

    assert len(features) == 2
    assert all(row.source_count == 1 for row in features)
    assert all(row.source_spread is None for row in features)


def test_persistence_is_active_with_one_point_and_trends_are_explicitly_unavailable() -> None:
    forecasts = movement_baselines_as_of(
        [_observation(0, 30)],
        cutoff_at=BASE,
        horizon_days=7,
    )

    assert [row.method for row in forecasts] == [
        "persistence",
        "linear_trend",
        "exponentially_weighted_trend",
    ]
    assert forecasts[0].status == "available"
    assert forecasts[0].predicted_adp == 30
    assert all(row.status == "unavailable" for row in forecasts[1:])
    assert all(row.predicted_adp is None for row in forecasts[1:])
    assert all("requires_at_least_3" in row.reason for row in forecasts[1:])


def test_trend_baselines_use_only_cutoff_safe_dated_history() -> None:
    history = [_observation(0, 30), _observation(1, 28), _observation(2, 26)]
    cutoff = BASE + timedelta(days=2)
    baseline = movement_baselines_as_of(history, cutoff_at=cutoff, horizon_days=2)
    with_future = movement_baselines_as_of(
        [*history, _observation(3, 1000)],
        cutoff_at=cutoff,
        horizon_days=2,
    )

    assert baseline == with_future
    by_method = {row.method: row for row in baseline}
    assert by_method["linear_trend"].status == "available"
    assert by_method["linear_trend"].predicted_adp == pytest.approx(22)
    assert by_method["exponentially_weighted_trend"].predicted_adp == pytest.approx(22)


def test_movement_inputs_reject_ambiguous_time_and_conflicting_duplicate_rows() -> None:
    with pytest.raises(ValueError, match="timezone-aware"):
        AdpObservation(
            identity=AdpIdentity("ffc", "row"),
            captured_at=datetime(2026, 1, 1),
            average_pick=10,
        )
    duplicates = [_observation(0, 10), _observation(0, 11)]
    with pytest.raises(ValueError, match="conflicting"):
        movement_features_as_of(duplicates, cutoff_at=BASE)
