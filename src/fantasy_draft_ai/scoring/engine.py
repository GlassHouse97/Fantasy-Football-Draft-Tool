"""Convert projected football stat components into configurable fantasy points."""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator

BonusCategory = Literal["passing_yards", "rushing_yards", "receiving_yards"]


class YardageBonus(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    category: BonusCategory
    threshold: float
    points: float


class ScoringRules(BaseModel):
    """Supported stat-component values for a league."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    passing_yards_per_point: float = Field(default=25, gt=0)
    passing_td: float = 4
    interception: float = -2
    rushing_yards_per_point: float = Field(default=10, gt=0)
    rushing_td: float = 6
    receiving_yards_per_point: float = Field(default=10, gt=0)
    reception: float = 0
    receiving_td: float = 6
    two_point_conversion: float = 2
    fumble_lost: float = -2
    position_reception_bonus: dict[str, float] = Field(default_factory=dict)
    yardage_bonuses: tuple[YardageBonus, ...] = ()

    @field_validator("position_reception_bonus")
    @classmethod
    def normalize_position_bonus(cls, value: dict[str, float]) -> dict[str, float]:
        return {position.upper(): bonus for position, bonus in sorted(value.items())}


class PlayerStatLine(BaseModel):
    """A projected or observed stat line. Yardage may be negative."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    position: str
    passing_yards: float = 0
    passing_tds: float = 0
    interceptions: float = 0
    rushing_yards: float = 0
    rushing_tds: float = 0
    receiving_yards: float = 0
    receptions: float = 0
    receiving_tds: float = 0
    two_point_conversions: float = 0
    fumbles_lost: float = 0


def score_player(stats: PlayerStatLine, rules: ScoringRules) -> float:
    """Calculate fantasy points using only explicit stat components and rules."""

    points = (
        stats.passing_yards / rules.passing_yards_per_point
        + stats.passing_tds * rules.passing_td
        + stats.interceptions * rules.interception
        + stats.rushing_yards / rules.rushing_yards_per_point
        + stats.rushing_tds * rules.rushing_td
        + stats.receiving_yards / rules.receiving_yards_per_point
        + stats.receptions * rules.reception
        + stats.receiving_tds * rules.receiving_td
        + stats.two_point_conversions * rules.two_point_conversion
        + stats.fumbles_lost * rules.fumble_lost
    )
    points += stats.receptions * rules.position_reception_bonus.get(stats.position.upper(), 0)
    for bonus in rules.yardage_bonuses:
        if getattr(stats, bonus.category) >= bonus.threshold:
            points += bonus.points
    return float(points)
