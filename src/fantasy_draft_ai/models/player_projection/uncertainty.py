"""Training-history-only residual intervals for Phase 4 player projections."""

from __future__ import annotations

import hashlib
import math
from collections.abc import Iterable
from dataclasses import dataclass
from typing import Protocol

import numpy as np

from fantasy_draft_ai.models.player_projection.config import (
    TARGET_GAMES_ACTIVE,
    PlayerModelConfig,
    canonical_json,
)


class ResidualLike(Protocol):
    """Structural input accepted from chronological tuning or outer-fold evaluation."""

    @property
    def prediction_season(self) -> int: ...

    @property
    def actual_value(self) -> float: ...

    @property
    def predicted_value(self) -> float: ...


@dataclass(frozen=True)
class ResidualObservation:
    prediction_season: int
    actual_value: float
    predicted_value: float


@dataclass(frozen=True)
class PredictionInterval:
    point_prediction: float
    p10: float
    p50: float
    p90: float


@dataclass(frozen=True)
class IntervalMetrics:
    rows: int
    central_80_coverage: float
    average_width: float


@dataclass(frozen=True)
class ResidualCalibration:
    """Signed residual quantiles that predate one inference season."""

    target_name: str
    prediction_season: int
    residual_count: int
    residual_seasons: tuple[int, ...]
    quantiles: tuple[float, float, float]
    residual_offsets: tuple[float, float, float]
    games_active_bounds: tuple[float, float]
    fingerprint: str

    def interval(self, point_prediction: float) -> PredictionInterval:
        """Shift one point estimate by calibrated signed residual quantiles."""

        point = float(point_prediction)
        if not math.isfinite(point):
            raise ValueError("Point predictions must be finite.")
        values = tuple(point + offset for offset in self.residual_offsets)
        if self.target_name == TARGET_GAMES_ACTIVE:
            lower, upper = self.games_active_bounds
            values = tuple(min(upper, max(lower, value)) for value in values)
            point = min(upper, max(lower, point))
        p10, p50, p90 = values
        # Clipping an ordered triple is monotonic, but keep the invariant explicit.
        p50 = min(p90, max(p10, p50))
        if not p10 <= p50 <= p90:
            raise RuntimeError("Residual interval quantiles are not ordered.")
        return PredictionInterval(
            point_prediction=point,
            p10=float(p10),
            p50=float(p50),
            p90=float(p90),
        )

    def intervals(self, point_predictions: Iterable[float]) -> tuple[PredictionInterval, ...]:
        return tuple(self.interval(value) for value in point_predictions)


def fit_residual_calibration(
    observations: Iterable[ResidualLike],
    *,
    target_name: str,
    prediction_season: int,
    config: PlayerModelConfig,
) -> ResidualCalibration:
    """Fit signed P10/P50/P90 offsets using only earlier out-of-fold errors."""

    if target_name not in config.targets:
        raise ValueError(f"Unsupported uncertainty target: {target_name!r}.")
    normalized: list[ResidualObservation] = []
    for observation in observations:
        actual = float(observation.actual_value)
        predicted = float(observation.predicted_value)
        season = int(observation.prediction_season)
        if not math.isfinite(actual) or not math.isfinite(predicted):
            raise ValueError("Residual observations must contain finite values.")
        if season >= prediction_season:
            raise ValueError(
                "Residual calibration cannot use the inference season or a future season."
            )
        normalized.append(ResidualObservation(season, actual, predicted))
    if not normalized:
        raise ValueError("At least one earlier out-of-fold residual is required.")
    normalized.sort(key=lambda row: (row.prediction_season, row.actual_value, row.predicted_value))
    residuals = np.asarray(
        [row.actual_value - row.predicted_value for row in normalized], dtype=float
    )
    offsets_array = np.quantile(
        residuals,
        np.asarray(config.interval_quantiles, dtype=float),
        method="linear",
    )
    offsets = tuple(float(value) for value in offsets_array)
    if len(offsets) != 3 or not offsets[0] <= offsets[1] <= offsets[2]:
        raise RuntimeError("Residual calibration did not produce ordered P10/P50/P90 offsets.")
    residual_seasons = tuple(sorted({row.prediction_season for row in normalized}))
    fingerprint_payload = {
        "target_name": target_name,
        "prediction_season": int(prediction_season),
        "quantiles": config.interval_quantiles,
        "games_active_bounds": config.games_active_bounds,
        "observations": [
            {
                "prediction_season": row.prediction_season,
                "actual_value": row.actual_value.hex(),
                "predicted_value": row.predicted_value.hex(),
            }
            for row in normalized
        ],
    }
    fingerprint = hashlib.sha256(canonical_json(fingerprint_payload).encode("utf-8")).hexdigest()
    return ResidualCalibration(
        target_name=target_name,
        prediction_season=int(prediction_season),
        residual_count=len(normalized),
        residual_seasons=residual_seasons,
        quantiles=config.interval_quantiles,
        residual_offsets=(offsets[0], offsets[1], offsets[2]),
        games_active_bounds=config.games_active_bounds,
        fingerprint=fingerprint,
    )


def evaluate_intervals(
    intervals: Iterable[PredictionInterval], actual_values: Iterable[float]
) -> IntervalMetrics:
    """Compute empirical central-80 coverage and average interval width."""

    paired = tuple(zip(intervals, actual_values, strict=True))
    if not paired:
        raise ValueError("At least one interval is required for evaluation.")
    covered = 0
    widths: list[float] = []
    for interval, actual_value in paired:
        actual = float(actual_value)
        if not math.isfinite(actual):
            raise ValueError("Interval outcomes must be finite.")
        covered += int(interval.p10 <= actual <= interval.p90)
        widths.append(interval.p90 - interval.p10)
    return IntervalMetrics(
        rows=len(paired),
        central_80_coverage=covered / len(paired),
        average_width=math.fsum(widths) / len(widths),
    )
