"""Small, scoring-compatible roster presets for the primary redraft UI."""

from __future__ import annotations

from dataclasses import dataclass

from fantasy_draft_ai.rules.models import DraftSettings, FlexSlot, LeagueRules


@dataclass(frozen=True)
class RedraftRosterPreset:
    """One beginner-friendly lineup shape that keeps the published scoring contract."""

    key: str
    label: str
    starters: tuple[tuple[str, int], ...]
    flex_count: int
    bench: int

    @property
    def rounds(self) -> int:
        return sum(count for _, count in self.starters) + self.flex_count + self.bench

    @property
    def summary(self) -> str:
        starter_summary = " · ".join(
            f"{count} {position}" for position, count in self.starters
        )
        return (
            f"{starter_summary} · {self.flex_count} FLEX · {self.bench} bench · "
            "no K/DST"
        )


REDRAFT_ROSTER_PRESETS = (
    RedraftRosterPreset(
        key="standard",
        label="Standard (2 WR, 1 FLEX)",
        starters=(("QB", 1), ("RB", 2), ("WR", 2), ("TE", 1)),
        flex_count=1,
        bench=7,
    ),
    RedraftRosterPreset(
        key="wr_flex_heavy",
        label="WR/FLEX-heavy (3 WR, 2 FLEX)",
        starters=(("QB", 1), ("RB", 2), ("WR", 3), ("TE", 1)),
        flex_count=2,
        bench=7,
    ),
)
DEFAULT_REDRAFT_PRESET_KEY = "standard"


def redraft_preset(key: str) -> RedraftRosterPreset:
    """Resolve a known preset without silently accepting an unknown UI value."""

    try:
        return next(preset for preset in REDRAFT_ROSTER_PRESETS if preset.key == key)
    except StopIteration as exc:
        raise ValueError(f"Unknown redraft roster preset: {key!r}.") from exc


def rules_for_redraft_preset(
    reference: LeagueRules,
    *,
    team_count: int,
    preset: RedraftRosterPreset,
) -> LeagueRules:
    """Change lineup demand while preserving the validated season and scoring inputs."""

    flex_slots = (
        FlexSlot(name="FLEX", count=preset.flex_count, eligible=("RB", "WR", "TE")),
    )
    return LeagueRules(
        season=reference.season,
        teams=team_count,
        draft=DraftSettings(type="snake", rounds=preset.rounds, keepers=0),
        starters=dict(preset.starters),
        flex_slots=flex_slots,
        bench=preset.bench,
        ir=reference.ir,
        scoring=reference.scoring,
    )
