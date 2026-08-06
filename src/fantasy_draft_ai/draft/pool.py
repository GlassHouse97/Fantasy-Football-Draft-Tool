"""Immutable player-pool rows frozen into each draft session."""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from datetime import datetime
from typing import Any


@dataclass(frozen=True)
class FrozenDraftPlayer:
    player_id: str
    display_name: str
    position: str
    p10: float
    p50: float
    p90: float
    prediction_status: str
    projection_source: str
    projection_method: str
    market_source: str | None = None
    market_snapshot_id: str | None = None
    market_captured_at: datetime | None = None
    average_pick: float | None = None
    availability_scale: float | None = None
    availability_evidence: str | None = None
    mapping_confidence: str | None = None

    def __post_init__(self) -> None:
        object.__setattr__(self, "position", self.position.strip().upper())
        object.__setattr__(self, "p10", float(self.p10))
        object.__setattr__(self, "p50", float(self.p50))
        object.__setattr__(self, "p90", float(self.p90))
        if self.average_pick is not None:
            object.__setattr__(self, "average_pick", float(self.average_pick))
        if self.availability_scale is not None:
            object.__setattr__(self, "availability_scale", float(self.availability_scale))
        if not self.player_id.strip() or not self.display_name.strip() or not self.position:
            raise ValueError("Frozen players require canonical ID, name, and position.")
        if not self.p10 <= self.p50 <= self.p90:
            raise ValueError("Frozen projection intervals must satisfy P10 <= P50 <= P90.")
        market_values = (self.average_pick, self.availability_scale)
        if any(value is not None for value in market_values) and not all(
            value is not None for value in market_values
        ):
            raise ValueError("Market location and scale must be frozen together.")
        if self.availability_scale is not None and self.availability_scale <= 0:
            raise ValueError("availability_scale must be positive.")

    @property
    def has_market_evidence(self) -> bool:
        return self.average_pick is not None and self.availability_scale is not None

    @property
    def has_outcome_interval(self) -> bool:
        return self.p10 < self.p90

    def as_dict(self) -> dict[str, Any]:
        return {
            "player_id": self.player_id,
            "display_name": self.display_name,
            "position": self.position,
            "p10": self.p10,
            "p50": self.p50,
            "p90": self.p90,
            "prediction_status": self.prediction_status,
            "projection_source": self.projection_source,
            "projection_method": self.projection_method,
            "market_source": self.market_source,
            "market_snapshot_id": self.market_snapshot_id,
            "market_captured_at": (
                None if self.market_captured_at is None else self.market_captured_at.isoformat()
            ),
            "average_pick": self.average_pick,
            "availability_scale": self.availability_scale,
            "availability_evidence": self.availability_evidence,
            "mapping_confidence": self.mapping_confidence,
        }


def player_pool_fingerprint(players: tuple[FrozenDraftPlayer, ...]) -> str:
    """Fingerprint stable canonical IDs and all frozen projection/market evidence."""

    if len({player.player_id for player in players}) != len(players):
        raise ValueError("A frozen draft pool cannot contain duplicate canonical player IDs.")
    payload = [player.as_dict() for player in sorted(players, key=lambda item: item.player_id)]
    encoded = json.dumps(
        payload,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=True,
        allow_nan=False,
    ).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()
