"""Serializable, recomputable outputs for transparent draft recommendations."""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from typing import Any, Literal

RecommendationRole = Literal["balanced", "safe_floor", "high_upside"]


@dataclass(frozen=True)
class RecommendationComponent:
    name: str
    raw_value: float
    normalized_value: float
    direction: Literal["higher_is_better", "lower_is_better"]
    weight: float
    weighted_contribution: float

    def as_dict(self) -> dict[str, Any]:
        return {
            "name": self.name,
            "raw_value": self.raw_value,
            "normalized_value": self.normalized_value,
            "direction": self.direction,
            "weight": self.weight,
            "weighted_contribution": self.weighted_contribution,
        }


@dataclass(frozen=True)
class RecommendedPlayer:
    role: RecommendationRole
    player_id: str
    display_name: str
    position: str
    p10: float
    p50: float
    p90: float
    projection_status: str
    projection_method: str
    current_adp: float
    probability_available_next_pick: float
    probability_gone_next_pick: float
    availability_evidence: str
    replacement_points: float
    p50_vorp: float
    roster_fit: float
    simulation: dict[str, Any]
    components: tuple[RecommendationComponent, ...]
    draft_recommendation_score: float
    explanation: str
    primary_risks: tuple[str, ...]
    market_source: str
    market_snapshot_id: str
    market_captured_at: str

    def as_dict(self) -> dict[str, Any]:
        return {
            "role": self.role,
            "player_id": self.player_id,
            "display_name": self.display_name,
            "position": self.position,
            "projection": {
                "p10": self.p10,
                "p50": self.p50,
                "p90": self.p90,
                "status": self.projection_status,
                "method": self.projection_method,
            },
            "current_adp": self.current_adp,
            "probability_available_next_pick": self.probability_available_next_pick,
            "probability_gone_next_pick": self.probability_gone_next_pick,
            "availability_evidence": self.availability_evidence,
            "replacement_points": self.replacement_points,
            "p50_vorp": self.p50_vorp,
            "roster_fit": self.roster_fit,
            "simulation": self.simulation,
            "components": [component.as_dict() for component in self.components],
            "draft_recommendation_score": self.draft_recommendation_score,
            "explanation": self.explanation,
            "primary_risks": list(self.primary_risks),
            "market_source": self.market_source,
            "market_snapshot_id": self.market_snapshot_id,
            "market_captured_at": self.market_captured_at,
        }


@dataclass(frozen=True)
class RecommendationResult:
    available: bool
    code: str
    message: str
    session_id: str
    session_version: int
    state_fingerprint: str
    projection_run_id: str
    adp_build_fingerprint: str | None
    player_pool_fingerprint: str
    engine_config_fingerprint: str
    random_seed: int
    simulation_count: int
    candidates: tuple[RecommendedPlayer, ...] = ()
    limitations: tuple[str, ...] = ()

    def as_dict(self) -> dict[str, Any]:
        return {
            "available": self.available,
            "code": self.code,
            "message": self.message,
            "session_id": self.session_id,
            "session_version": self.session_version,
            "state_fingerprint": self.state_fingerprint,
            "projection_run_id": self.projection_run_id,
            "adp_build_fingerprint": self.adp_build_fingerprint,
            "player_pool_fingerprint": self.player_pool_fingerprint,
            "engine_config_fingerprint": self.engine_config_fingerprint,
            "random_seed": self.random_seed,
            "simulation_count": self.simulation_count,
            "candidates": [candidate.as_dict() for candidate in self.candidates],
            "limitations": list(self.limitations),
        }

    def fingerprint(self) -> str:
        encoded = json.dumps(
            self.as_dict(),
            sort_keys=True,
            separators=(",", ":"),
            ensure_ascii=True,
            allow_nan=False,
        ).encode("utf-8")
        return hashlib.sha256(encoded).hexdigest()
