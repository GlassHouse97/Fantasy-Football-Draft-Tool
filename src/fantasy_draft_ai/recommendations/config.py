"""Versioned, fingerprinted assumptions for Phase 6 simulation and scoring."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

import yaml
from pydantic import BaseModel, ConfigDict, Field, model_validator


class RoleWeights(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    p50_vorp: float = Field(ge=0)
    floor_vorp: float = Field(ge=0)
    ceiling_vorp: float = Field(ge=0)
    scarcity: float = Field(ge=0)
    gone_probability: float = Field(ge=0)
    roster_fit: float = Field(ge=0)
    simulation_mean: float = Field(ge=0)
    simulation_floor: float = Field(ge=0)
    simulation_ceiling: float = Field(ge=0)
    risk_penalty: float = Field(ge=0)

    @model_validator(mode="after")
    def weights_sum_to_one(self) -> RoleWeights:
        total = sum(self.model_dump().values())
        if abs(total - 1.0) > 1e-9:
            raise ValueError(f"Recommendation role weights must sum to 1.0, received {total}.")
        return self


class DraftEngineConfig(BaseModel):
    """All arbitrary Phase 6 choices that must be visible and reproducible."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    version: str = Field(min_length=1)
    default_simulations: int = Field(ge=16, le=1000)
    maximum_simulations: int = Field(ge=16, le=1000)
    candidate_count: int = Field(ge=3, le=30)
    opponent_candidate_window: int = Field(ge=3, le=100)
    work_budget: int = Field(ge=10_000, le=5_000_000)
    position_need_multiplier: float = Field(ge=0, le=2)
    positional_run_multiplier: float = Field(ge=0, le=0.5)
    positional_run_window: int = Field(ge=1, le=8)
    minimum_pick_weight: float = Field(gt=0, le=1)
    bench_value_credit: float = Field(ge=0, le=0.5)
    market_coverage_required: float = Field(gt=0, le=1)
    balanced: RoleWeights
    safe_floor: RoleWeights
    high_upside: RoleWeights

    @model_validator(mode="after")
    def defaults_within_cap(self) -> DraftEngineConfig:
        if self.default_simulations > self.maximum_simulations:
            raise ValueError("default_simulations cannot exceed maximum_simulations.")
        return self

    def canonical_json(self) -> str:
        return json.dumps(
            self.model_dump(mode="json"),
            sort_keys=True,
            separators=(",", ":"),
            ensure_ascii=True,
        )

    def fingerprint(self) -> str:
        return hashlib.sha256(self.canonical_json().encode("utf-8")).hexdigest()


def load_draft_engine_config(path: Path | None = None) -> DraftEngineConfig:
    config_path = path or Path("configs/draft_engine.yaml")
    with config_path.open(encoding="utf-8") as handle:
        return DraftEngineConfig.model_validate(yaml.safe_load(handle))
