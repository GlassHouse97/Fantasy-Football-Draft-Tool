"""Validated configuration for the transparent ADP availability fallback."""

from __future__ import annotations

import math
from dataclasses import dataclass, field
from itertools import pairwise
from pathlib import Path
from typing import Any, cast

import yaml

from fantasy_draft_ai.config import find_project_root

DEFAULT_CONFIG_PATH = Path("configs/adp_availability.yaml")


@dataclass(frozen=True)
class FallbackBand:
    """One configured draft-range assumption for an ADP standard deviation."""

    min_pick: float
    max_pick: float | None
    standard_deviation: float

    def __post_init__(self) -> None:
        values = (self.min_pick, self.standard_deviation)
        if not all(math.isfinite(value) for value in values):
            raise ValueError("Fallback-band values must be finite.")
        if self.min_pick < 1.0:
            raise ValueError("Fallback-band min_pick must be at least one.")
        if self.max_pick is not None:
            if not math.isfinite(self.max_pick):
                raise ValueError("Fallback-band max_pick must be finite when provided.")
            if self.max_pick <= self.min_pick:
                raise ValueError("Fallback-band max_pick must be greater than min_pick.")
        if self.standard_deviation <= 0.0:
            raise ValueError("Fallback standard deviations must be positive.")

    def contains(self, average_pick: float) -> bool:
        """Return whether an ADP belongs to this left-inclusive range."""

        return self.min_pick <= average_pick and (
            self.max_pick is None or average_pick < self.max_pick
        )


def _default_fallback_bands() -> dict[str, tuple[FallbackBand, ...]]:
    return {
        "DEFAULT": (
            FallbackBand(1.0, 60.0, 8.0),
            FallbackBand(60.0, 120.0, 12.0),
            FallbackBand(120.0, None, 18.0),
        )
    }


@dataclass(frozen=True)
class AvailabilityConfig:
    """Rules for deriving a pick-distribution scale without hiding assumptions."""

    range_sigma_divisor: float = 4.0
    minimum_standard_deviation: float = 1.0
    fallback_assumption_label: str = "configured_position_draft_range_assumption"
    fallback_bands: dict[str, tuple[FallbackBand, ...]] = field(
        default_factory=_default_fallback_bands
    )

    def __post_init__(self) -> None:
        if not math.isfinite(self.range_sigma_divisor) or self.range_sigma_divisor <= 0.0:
            raise ValueError("range_sigma_divisor must be finite and positive.")
        if (
            not math.isfinite(self.minimum_standard_deviation)
            or self.minimum_standard_deviation <= 0.0
        ):
            raise ValueError("minimum_standard_deviation must be finite and positive.")
        if not self.fallback_assumption_label.strip():
            raise ValueError("fallback_assumption_label cannot be empty.")
        normalized: dict[str, tuple[FallbackBand, ...]] = {}
        for position, bands in self.fallback_bands.items():
            key = position.strip().upper()
            if not key:
                raise ValueError("Fallback positions cannot be empty.")
            if not bands:
                raise ValueError(f"Fallback position {key!r} must contain at least one band.")
            ordered = tuple(sorted(bands, key=lambda band: band.min_pick))
            for previous, current in pairwise(ordered):
                if previous.max_pick is None or current.min_pick < previous.max_pick:
                    raise ValueError(f"Fallback bands overlap for position {key!r}.")
            normalized[key] = ordered
        if "DEFAULT" not in normalized:
            raise ValueError("Fallback configuration must include a DEFAULT position.")
        object.__setattr__(self, "fallback_bands", normalized)

    def fallback_for(self, *, position: str, average_pick: float) -> FallbackBand:
        """Select the position-specific band, falling back to DEFAULT bands."""

        if not math.isfinite(average_pick) or average_pick < 1.0:
            raise ValueError("average_pick must be finite and at least one.")
        position_key = position.strip().upper()
        bands = self.fallback_bands.get(position_key, self.fallback_bands["DEFAULT"])
        for band in bands:
            if band.contains(average_pick):
                return band
        default_bands = self.fallback_bands["DEFAULT"]
        if bands is not default_bands:
            for band in default_bands:
                if band.contains(average_pick):
                    return band
        raise ValueError(
            f"No configured availability fallback covers position={position_key!r}, "
            f"average_pick={average_pick}."
        )


def load_availability_config(path: Path | None = None) -> AvailabilityConfig:
    """Load the versioned availability assumptions from YAML."""

    configured = path or (find_project_root() / DEFAULT_CONFIG_PATH)
    config_path = configured if configured.is_absolute() else find_project_root() / configured
    with config_path.open(encoding="utf-8") as handle:
        payload = cast(dict[str, Any], yaml.safe_load(handle) or {})
    availability = payload.get("availability")
    if not isinstance(availability, dict):
        raise ValueError("Availability config must contain an 'availability' mapping.")
    raw_bands = availability.get("fallback_bands")
    if not isinstance(raw_bands, dict):
        raise ValueError("Availability config must contain a 'fallback_bands' mapping.")
    fallback_bands: dict[str, tuple[FallbackBand, ...]] = {}
    for position, value in raw_bands.items():
        if not isinstance(position, str) or not isinstance(value, list):
            raise ValueError("Each fallback position must map to a list of bands.")
        bands: list[FallbackBand] = []
        for raw_band in value:
            if not isinstance(raw_band, dict):
                raise ValueError("Each fallback band must be a mapping.")
            try:
                min_pick = float(raw_band["min_pick"])
                maximum = raw_band.get("max_pick")
                standard_deviation = float(raw_band["standard_deviation"])
            except (KeyError, TypeError, ValueError) as exc:
                raise ValueError("Fallback bands require numeric pick bounds and scale.") from exc
            bands.append(
                FallbackBand(
                    min_pick=min_pick,
                    max_pick=None if maximum is None else float(maximum),
                    standard_deviation=standard_deviation,
                )
            )
        fallback_bands[position] = tuple(bands)
    try:
        return AvailabilityConfig(
            range_sigma_divisor=float(availability["range_sigma_divisor"]),
            minimum_standard_deviation=float(availability["minimum_standard_deviation"]),
            fallback_assumption_label=str(availability["fallback_assumption_label"]),
            fallback_bands=fallback_bands,
        )
    except (KeyError, TypeError, ValueError) as exc:
        raise ValueError("Availability configuration is invalid.") from exc
