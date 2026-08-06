"""Cutoff-safe ADP movement features and transparent trend baselines."""

from __future__ import annotations

import math
from collections import defaultdict
from collections.abc import Iterable, Sequence
from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
from itertools import pairwise
from typing import Literal

SECONDS_PER_DAY = 86_400.0
LAG_DAYS = (1, 3, 7, 14)

ForecastMethod = Literal["persistence", "linear_trend", "exponentially_weighted_trend"]
ForecastStatus = Literal["available", "unavailable"]


@dataclass(frozen=True)
class AdpIdentity:
    """Canonical identity when mapped, otherwise explicit source-row lineage."""

    source: str
    raw_source_row_id: str
    player_id: str | None = None

    def __post_init__(self) -> None:
        source = self.source.strip().lower()
        raw_source_row_id = self.raw_source_row_id.strip()
        player_id = self.player_id.strip() if self.player_id is not None else None
        if not source:
            raise ValueError("ADP identity source cannot be empty.")
        if not raw_source_row_id:
            raise ValueError("ADP identity raw_source_row_id cannot be empty.")
        if player_id == "":
            raise ValueError("ADP identity player_id cannot be blank when provided.")
        object.__setattr__(self, "source", source)
        object.__setattr__(self, "raw_source_row_id", raw_source_row_id)
        object.__setattr__(self, "player_id", player_id)

    @property
    def key(self) -> str:
        """Stable, name-free grouping key."""

        if self.player_id is not None:
            return f"player:{self.player_id}"
        return f"source:{self.source}:{self.raw_source_row_id}"


@dataclass(frozen=True)
class AdpObservation:
    """One immutable ADP observation with its lineage identity."""

    identity: AdpIdentity
    captured_at: datetime
    average_pick: float

    def __post_init__(self) -> None:
        if self.captured_at.tzinfo is None or self.captured_at.utcoffset() is None:
            raise ValueError("captured_at must be timezone-aware.")
        average_pick = float(self.average_pick)
        if not math.isfinite(average_pick) or average_pick < 1.0:
            raise ValueError("average_pick must be finite and at least one.")
        object.__setattr__(self, "captured_at", self.captured_at.astimezone(UTC))
        object.__setattr__(self, "average_pick", average_pick)


@dataclass(frozen=True)
class MovementFeatures:
    """Movement signals available for one source series at an explicit cutoff."""

    identity: AdpIdentity
    cutoff_at: datetime
    observed_at: datetime
    current_adp: float
    prior_observed_at: datetime | None
    prior_adp: float | None
    elapsed_days: float | None
    change_1d: float | None
    change_3d: float | None
    change_7d: float | None
    change_14d: float | None
    velocity_picks_per_day: float | None
    acceleration_picks_per_day_squared: float | None
    rolling_volatility_14d: float | None
    source_spread: float | None
    source_count: int
    observation_count: int
    identity_observation_count: int


@dataclass(frozen=True)
class MovementForecast:
    """One explicit movement baseline result, including unavailable methods."""

    identity: AdpIdentity
    method: ForecastMethod
    status: ForecastStatus
    reason: str
    cutoff_at: datetime
    target_at: datetime
    last_observed_at: datetime
    horizon_days: float
    training_observation_count: int
    predicted_adp: float | None


def movement_features_as_of(
    observations: Iterable[AdpObservation],
    *,
    cutoff_at: datetime,
    rolling_window_days: int = 14,
) -> tuple[MovementFeatures, ...]:
    """Build latest per-source movement features using no rows after ``cutoff_at``.

    Lag values use the most recent observation at or before the requested lag
    boundary. Velocity and acceleration are based on actual elapsed time.
    Source spread compares the latest available value from each source sharing
    a canonical identity; unresolved source rows remain isolated by construction.
    """

    cutoff = _utc_datetime(cutoff_at, "cutoff_at")
    if rolling_window_days < 1:
        raise ValueError("rolling_window_days must be positive.")
    eligible = tuple(
        observation for observation in observations if observation.captured_at <= cutoff
    )
    identity_groups: dict[str, list[AdpObservation]] = defaultdict(list)
    for observation in eligible:
        identity_groups[observation.identity.key].append(observation)

    output: list[MovementFeatures] = []
    for identity_key in sorted(identity_groups):
        identity_rows = identity_groups[identity_key]
        source_groups: dict[str, list[AdpObservation]] = defaultdict(list)
        for observation in identity_rows:
            source_groups[observation.identity.source].append(observation)
        latest_by_source = {
            source: _deduplicate_series(rows)[-1] for source, rows in source_groups.items()
        }
        latest_values = [observation.average_pick for observation in latest_by_source.values()]
        source_spread = max(latest_values) - min(latest_values) if len(latest_values) >= 2 else None
        identity_observation_count = sum(
            len(_deduplicate_series(rows)) for rows in source_groups.values()
        )
        for source in sorted(source_groups):
            series = _deduplicate_series(source_groups[source])
            current = series[-1]
            prior = series[-2] if len(series) >= 2 else None
            changes = {
                days: _change_at_lag(series, current=current, lag_days=days) for days in LAG_DAYS
            }
            output.append(
                MovementFeatures(
                    identity=current.identity,
                    cutoff_at=cutoff,
                    observed_at=current.captured_at,
                    current_adp=current.average_pick,
                    prior_observed_at=prior.captured_at if prior is not None else None,
                    prior_adp=prior.average_pick if prior is not None else None,
                    elapsed_days=(
                        _elapsed_days(prior.captured_at, current.captured_at)
                        if prior is not None
                        else None
                    ),
                    change_1d=changes[1],
                    change_3d=changes[3],
                    change_7d=changes[7],
                    change_14d=changes[14],
                    velocity_picks_per_day=_latest_velocity(series),
                    acceleration_picks_per_day_squared=_latest_acceleration(series),
                    rolling_volatility_14d=_rolling_volatility(
                        series,
                        current=current,
                        window_days=rolling_window_days,
                    ),
                    source_spread=source_spread,
                    source_count=len(latest_by_source),
                    observation_count=len(series),
                    identity_observation_count=identity_observation_count,
                )
            )
    return tuple(output)


def movement_baselines_as_of(
    observations: Iterable[AdpObservation],
    *,
    cutoff_at: datetime,
    horizon_days: float,
    minimum_trend_observations: int = 3,
    exponential_alpha: float = 0.5,
) -> tuple[MovementForecast, ...]:
    """Forecast each identity/source series with honest transparent baselines.

    Persistence activates with one cutoff-safe point. Linear and exponentially
    weighted trends remain explicitly unavailable until enough dated points exist.
    """

    cutoff = _utc_datetime(cutoff_at, "cutoff_at")
    if not math.isfinite(horizon_days) or horizon_days <= 0.0:
        raise ValueError("horizon_days must be finite and positive.")
    if minimum_trend_observations < 3:
        raise ValueError("minimum_trend_observations must be at least three.")
    if not math.isfinite(exponential_alpha) or not 0.0 < exponential_alpha <= 1.0:
        raise ValueError("exponential_alpha must be in (0, 1].")
    target_at = cutoff + timedelta(days=horizon_days)
    groups: dict[tuple[str, str], list[AdpObservation]] = defaultdict(list)
    for observation in observations:
        if observation.captured_at <= cutoff:
            groups[observation.identity.key, observation.identity.source].append(observation)

    output: list[MovementForecast] = []
    for group_key in sorted(groups):
        series = _deduplicate_series(groups[group_key])
        current = series[-1]
        count = len(series)
        output.append(
            _forecast(
                current=current,
                method="persistence",
                status="available",
                reason="one_or_more_cutoff_safe_observations",
                cutoff=cutoff,
                target_at=target_at,
                horizon_days=horizon_days,
                count=count,
                prediction=current.average_pick,
            )
        )
        if count < minimum_trend_observations:
            reason = f"requires_at_least_{minimum_trend_observations}_dated_observations"
            for method in ("linear_trend", "exponentially_weighted_trend"):
                output.append(
                    _forecast(
                        current=current,
                        method=method,
                        status="unavailable",
                        reason=reason,
                        cutoff=cutoff,
                        target_at=target_at,
                        horizon_days=horizon_days,
                        count=count,
                        prediction=None,
                    )
                )
            continue
        linear_prediction = _linear_prediction(series, target_at=target_at)
        ew_prediction = _exponentially_weighted_prediction(
            series,
            target_at=target_at,
            alpha=exponential_alpha,
        )
        output.extend(
            (
                _forecast(
                    current=current,
                    method="linear_trend",
                    status="available",
                    reason="cutoff_safe_linear_least_squares",
                    cutoff=cutoff,
                    target_at=target_at,
                    horizon_days=horizon_days,
                    count=count,
                    prediction=linear_prediction,
                ),
                _forecast(
                    current=current,
                    method="exponentially_weighted_trend",
                    status="available",
                    reason="cutoff_safe_exponentially_weighted_interval_velocity",
                    cutoff=cutoff,
                    target_at=target_at,
                    horizon_days=horizon_days,
                    count=count,
                    prediction=ew_prediction,
                ),
            )
        )
    return tuple(output)


def _utc_datetime(value: datetime, name: str) -> datetime:
    if value.tzinfo is None or value.utcoffset() is None:
        raise ValueError(f"{name} must be timezone-aware.")
    return value.astimezone(UTC)


def _deduplicate_series(observations: Sequence[AdpObservation]) -> tuple[AdpObservation, ...]:
    by_timestamp: dict[datetime, AdpObservation] = {}
    for observation in observations:
        existing = by_timestamp.get(observation.captured_at)
        if existing is not None and not math.isclose(
            existing.average_pick,
            observation.average_pick,
            rel_tol=0.0,
            abs_tol=1e-12,
        ):
            raise ValueError(
                "One identity/source series has conflicting ADP values at the same timestamp."
            )
        by_timestamp[observation.captured_at] = observation
    return tuple(by_timestamp[timestamp] for timestamp in sorted(by_timestamp))


def _change_at_lag(
    series: Sequence[AdpObservation],
    *,
    current: AdpObservation,
    lag_days: int,
) -> float | None:
    boundary = current.captured_at - timedelta(days=lag_days)
    candidates = [observation for observation in series if observation.captured_at <= boundary]
    if not candidates:
        return None
    return current.average_pick - candidates[-1].average_pick


def _elapsed_days(first: datetime, second: datetime) -> float:
    return (second - first).total_seconds() / SECONDS_PER_DAY


def _latest_velocity(series: Sequence[AdpObservation]) -> float | None:
    if len(series) < 2:
        return None
    previous, current = series[-2:]
    return (current.average_pick - previous.average_pick) / _elapsed_days(
        previous.captured_at, current.captured_at
    )


def _latest_acceleration(series: Sequence[AdpObservation]) -> float | None:
    if len(series) < 3:
        return None
    first, second, third = series[-3:]
    first_velocity = (second.average_pick - first.average_pick) / _elapsed_days(
        first.captured_at, second.captured_at
    )
    second_velocity = (third.average_pick - second.average_pick) / _elapsed_days(
        second.captured_at, third.captured_at
    )
    first_midpoint = first.captured_at + (second.captured_at - first.captured_at) / 2
    second_midpoint = second.captured_at + (third.captured_at - second.captured_at) / 2
    return (second_velocity - first_velocity) / _elapsed_days(first_midpoint, second_midpoint)


def _rolling_volatility(
    series: Sequence[AdpObservation],
    *,
    current: AdpObservation,
    window_days: int,
) -> float | None:
    boundary = current.captured_at - timedelta(days=window_days)
    values = [
        observation.average_pick
        for observation in series
        if boundary <= observation.captured_at <= current.captured_at
    ]
    if len(values) < 2:
        return None
    mean = math.fsum(values) / len(values)
    variance = math.fsum((value - mean) ** 2 for value in values) / len(values)
    return math.sqrt(variance)


def _linear_prediction(
    series: Sequence[AdpObservation],
    *,
    target_at: datetime,
) -> float:
    first_timestamp = series[0].captured_at
    x_values = [_elapsed_days(first_timestamp, row.captured_at) for row in series]
    y_values = [row.average_pick for row in series]
    x_mean = math.fsum(x_values) / len(x_values)
    y_mean = math.fsum(y_values) / len(y_values)
    denominator = math.fsum((value - x_mean) ** 2 for value in x_values)
    if denominator <= 0.0:
        raise ValueError("Linear ADP trend requires distinct dated observations.")
    slope = (
        math.fsum(
            (x_value - x_mean) * (y_value - y_mean)
            for x_value, y_value in zip(x_values, y_values, strict=True)
        )
        / denominator
    )
    target_x = _elapsed_days(first_timestamp, target_at)
    return max(1.0, y_mean + slope * (target_x - x_mean))


def _exponentially_weighted_prediction(
    series: Sequence[AdpObservation],
    *,
    target_at: datetime,
    alpha: float,
) -> float:
    velocities = [
        (current.average_pick - previous.average_pick)
        / _elapsed_days(previous.captured_at, current.captured_at)
        for previous, current in pairwise(series)
    ]
    weighted_velocity = velocities[0]
    for velocity in velocities[1:]:
        weighted_velocity = alpha * velocity + (1.0 - alpha) * weighted_velocity
    current = series[-1]
    target_elapsed_days = _elapsed_days(current.captured_at, target_at)
    return max(1.0, current.average_pick + weighted_velocity * target_elapsed_days)


def _forecast(
    *,
    current: AdpObservation,
    method: ForecastMethod,
    status: ForecastStatus,
    reason: str,
    cutoff: datetime,
    target_at: datetime,
    horizon_days: float,
    count: int,
    prediction: float | None,
) -> MovementForecast:
    return MovementForecast(
        identity=current.identity,
        method=method,
        status=status,
        reason=reason,
        cutoff_at=cutoff,
        target_at=target_at,
        last_observed_at=current.captured_at,
        horizon_days=horizon_days,
        training_observation_count=count,
        predicted_adp=prediction,
    )
