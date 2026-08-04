"""Player identity records preserve mapping evidence and ambiguity."""

from __future__ import annotations

from enum import StrEnum

from pydantic import BaseModel, ConfigDict, Field, model_validator


class MappingConfidence(StrEnum):
    EXACT = "exact"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    UNRESOLVED = "unresolved"


class PlayerIdentity(BaseModel):
    """Canonical player identity with nullable platform IDs."""

    model_config = ConfigDict(extra="forbid")

    player_id: str = Field(min_length=1)
    display_name: str = Field(min_length=1)
    position: str | None = None
    nfl_team: str | None = None
    gsis_id: str | None = None
    espn_id: str | None = None
    sleeper_id: str | None = None
    yahoo_id: str | None = None
    mfl_id: str | None = None
    fleaflicker_id: str | None = None
    fantasypros_id: str | None = None
    mapping_confidence: MappingConfidence
    mapping_source: str = Field(min_length=1)

    @model_validator(mode="after")
    def unresolved_when_no_evidence(self) -> PlayerIdentity:
        """Forbid claiming an exact mapping without any platform identifier."""

        identifiers = (
            self.gsis_id,
            self.espn_id,
            self.sleeper_id,
            self.yahoo_id,
            self.mfl_id,
            self.fleaflicker_id,
            self.fantasypros_id,
        )
        if not any(identifiers) and self.mapping_confidence == MappingConfidence.EXACT:
            raise ValueError("Exact identity mapping requires at least one source identifier.")
        return self
