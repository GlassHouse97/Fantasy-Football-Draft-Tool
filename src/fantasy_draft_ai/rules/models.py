"""Validated league rules with canonical JSON and deterministic fingerprints."""

from __future__ import annotations

import hashlib
import json
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

from fantasy_draft_ai.scoring.engine import ScoringRules


class DraftSettings(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    type: Literal["snake"] = "snake"
    rounds: int = Field(ge=1, le=40)
    keepers: int = Field(default=0, ge=0)


class FlexSlot(BaseModel):
    """A repeated roster slot with an explicit eligibility set."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    name: str = Field(min_length=1)
    count: int = Field(ge=1, le=10)
    eligible: tuple[str, ...]

    @field_validator("name")
    @classmethod
    def uppercase_name(cls, value: str) -> str:
        return value.strip().upper()

    @field_validator("eligible")
    @classmethod
    def normalize_eligible(cls, value: tuple[str, ...]) -> tuple[str, ...]:
        normalized = tuple(sorted({position.strip().upper() for position in value if position}))
        if not normalized:
            raise ValueError("A flex slot needs at least one eligible position.")
        return normalized


class LeagueRules(BaseModel):
    """Complete draft, roster, and scoring settings used by recommendation logic."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    season: int = Field(ge=2000, le=2100)
    teams: int = Field(ge=4, le=32)
    draft: DraftSettings
    starters: dict[str, int]
    flex_slots: tuple[FlexSlot, ...] = ()
    bench: int = Field(default=0, ge=0, le=30)
    ir: int = Field(default=0, ge=0, le=20)
    scoring: ScoringRules

    @field_validator("starters")
    @classmethod
    def normalize_starters(cls, value: dict[str, int]) -> dict[str, int]:
        normalized = {position.strip().upper(): count for position, count in value.items()}
        if any(count < 0 for count in normalized.values()):
            raise ValueError("Starter counts cannot be negative.")
        return dict(sorted((position, count) for position, count in normalized.items() if count))

    @model_validator(mode="after")
    def rounds_cover_roster(self) -> LeagueRules:
        roster_size = (
            sum(self.starters.values()) + sum(slot.count for slot in self.flex_slots) + self.bench
        )
        if self.draft.rounds < roster_size - self.draft.keepers:
            raise ValueError("Draft rounds do not cover starters, flex slots, bench, and keepers.")
        return self

    def canonical_json(self) -> str:
        """Return a stable JSON representation with sorted keys and eligible positions."""

        payload = self.model_dump(mode="json")
        return json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=True)

    def fingerprint(self) -> str:
        return hashlib.sha256(self.canonical_json().encode("utf-8")).hexdigest()

    def slot_eligibility(self) -> dict[str, tuple[str, ...]]:
        """Return each concrete slot name and its valid positions."""

        slots: dict[str, tuple[str, ...]] = {position: (position,) for position in self.starters}
        slots.update({slot.name: slot.eligible for slot in self.flex_slots})
        return dict(sorted(slots.items()))

    def eligible_slots(self, position: str) -> tuple[str, ...]:
        normalized = position.upper()
        return tuple(
            slot for slot, eligible in self.slot_eligibility().items() if normalized in eligible
        )
