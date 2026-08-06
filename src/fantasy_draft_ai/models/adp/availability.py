"""Transparent empirical player-availability estimates around ADP."""

from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Literal

from fantasy_draft_ai.models.adp.config import AvailabilityConfig
from fantasy_draft_ai.models.adp.movement import AdpIdentity

SpreadMethod = Literal["observed_source_stddev", "min_max_derived", "configured_fallback"]

_SQRT_TWO = math.sqrt(2.0)
_LOG_SQRT_TWO_PI = 0.5 * math.log(2.0 * math.pi)


@dataclass(frozen=True)
class SpreadEstimate:
    """Distribution scale plus the evidence or assumption that produced it."""

    standard_deviation: float
    method: SpreadMethod
    evidence_label: str
    fallback_used: bool
    sample_size: int | None


@dataclass(frozen=True)
class AvailabilityEstimate:
    """Conditional next-pick probability for one name-free player identity."""

    identity: AdpIdentity
    position: str
    average_pick: float
    current_pick: float
    next_pick: float
    standard_deviation: float
    spread_method: SpreadMethod
    evidence_label: str
    fallback_used: bool
    sample_size: int | None
    probability_selected_before_next_pick: float
    probability_available_at_next_pick: float


def estimate_pick_spread(
    *,
    position: str,
    average_pick: float,
    observed_standard_deviation: float | None,
    minimum_pick: float | None,
    maximum_pick: float | None,
    sample_size: int | None,
    config: AvailabilityConfig,
) -> SpreadEstimate:
    """Choose observed spread, range-derived scale, then labeled fallback."""

    mean = _positive_pick(average_pick, "average_pick")
    normalized_sample_size = _sample_size(sample_size)
    if observed_standard_deviation is not None:
        observed = float(observed_standard_deviation)
        if math.isfinite(observed) and observed > 0.0:
            return SpreadEstimate(
                standard_deviation=max(config.minimum_standard_deviation, observed),
                method="observed_source_stddev",
                evidence_label="source_reported_standard_deviation",
                fallback_used=False,
                sample_size=normalized_sample_size,
            )
    if minimum_pick is not None and maximum_pick is not None:
        minimum = float(minimum_pick)
        maximum = float(maximum_pick)
        if (
            math.isfinite(minimum)
            and math.isfinite(maximum)
            and minimum >= 1.0
            and maximum > minimum
        ):
            derived = (maximum - minimum) / config.range_sigma_divisor
            return SpreadEstimate(
                standard_deviation=max(config.minimum_standard_deviation, derived),
                method="min_max_derived",
                evidence_label=(f"source_min_max_range_divided_by_{config.range_sigma_divisor:g}"),
                fallback_used=False,
                sample_size=normalized_sample_size,
            )
    band = config.fallback_for(position=position, average_pick=mean)
    return SpreadEstimate(
        standard_deviation=max(config.minimum_standard_deviation, band.standard_deviation),
        method="configured_fallback",
        evidence_label=config.fallback_assumption_label,
        fallback_used=True,
        sample_size=normalized_sample_size,
    )


def estimate_availability(
    *,
    identity: AdpIdentity,
    position: str,
    average_pick: float,
    current_pick: float,
    next_pick: float,
    observed_standard_deviation: float | None = None,
    minimum_pick: float | None = None,
    maximum_pick: float | None = None,
    sample_size: int | None = None,
    config: AvailabilityConfig,
) -> AvailabilityEstimate:
    """Estimate conditional availability under a normal draft-slot distribution.

    The player is known to be available immediately after ``current_pick``.
    Continuity-corrected pick boundaries make consecutive user picks contain no
    intervening opponent selection. The two returned probabilities are exact
    complements after numerical clamping.
    """

    mean = _positive_pick(average_pick, "average_pick")
    current = _positive_pick(current_pick, "current_pick")
    following = _positive_pick(next_pick, "next_pick")
    if following <= current:
        raise ValueError("next_pick must be greater than current_pick.")
    spread = estimate_pick_spread(
        position=position,
        average_pick=mean,
        observed_standard_deviation=observed_standard_deviation,
        minimum_pick=minimum_pick,
        maximum_pick=maximum_pick,
        sample_size=sample_size,
        config=config,
    )
    lower_boundary = current + 0.5
    upper_boundary = following - 0.5
    if upper_boundary <= lower_boundary:
        probability_available = 1.0
    else:
        lower_z = (lower_boundary - mean) / spread.standard_deviation
        upper_z = (upper_boundary - mean) / spread.standard_deviation
        log_lower_survival = _normal_log_survival(lower_z)
        log_upper_survival = _normal_log_survival(upper_z)
        probability_available = math.exp(min(0.0, log_upper_survival - log_lower_survival))
        probability_available = min(1.0, max(0.0, probability_available))
    probability_selected = 1.0 - probability_available
    return AvailabilityEstimate(
        identity=identity,
        position=position.strip().upper(),
        average_pick=mean,
        current_pick=current,
        next_pick=following,
        standard_deviation=spread.standard_deviation,
        spread_method=spread.method,
        evidence_label=spread.evidence_label,
        fallback_used=spread.fallback_used,
        sample_size=spread.sample_size,
        probability_selected_before_next_pick=probability_selected,
        probability_available_at_next_pick=probability_available,
    )


def normal_survival(value: float, *, mean: float, standard_deviation: float) -> float:
    """Return ``P(X > value)`` for a normal variable without SciPy."""

    numeric = float(value)
    location = float(mean)
    scale = float(standard_deviation)
    if not math.isfinite(numeric) or not math.isfinite(location):
        raise ValueError("Normal-distribution values must be finite.")
    if not math.isfinite(scale) or scale <= 0.0:
        raise ValueError("standard_deviation must be finite and positive.")
    log_probability = _normal_log_survival((numeric - location) / scale)
    if log_probability < math.log(float.fromhex("0x0.0000000000001p-1022")):
        return 0.0
    return min(1.0, max(0.0, math.exp(log_probability)))


def _normal_log_survival(z_value: float) -> float:
    """Stable standard-normal log survival, including extreme positive tails."""

    if z_value < 8.0:
        return math.log(0.5 * math.erfc(z_value / _SQRT_TWO))
    inverse_square = 1.0 / (z_value * z_value)
    correction = 1.0 + inverse_square * (
        -1.0 + inverse_square * (3.0 + inverse_square * (-15.0 + inverse_square * 105.0))
    )
    return -0.5 * z_value * z_value - math.log(z_value) - _LOG_SQRT_TWO_PI + math.log(correction)


def _positive_pick(value: float, name: str) -> float:
    numeric = float(value)
    if not math.isfinite(numeric) or numeric < 1.0:
        raise ValueError(f"{name} must be finite and at least one.")
    return numeric


def _sample_size(value: int | None) -> int | None:
    if value is None:
        return None
    if isinstance(value, bool) or value < 0:
        raise ValueError("sample_size cannot be negative.")
    return int(value)
