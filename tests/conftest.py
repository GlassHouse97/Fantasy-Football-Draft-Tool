from __future__ import annotations

from collections.abc import Callable

import pytest

from fantasy_draft_ai.rules.models import DraftSettings, FlexSlot, LeagueRules
from fantasy_draft_ai.scoring.engine import ScoringRules


@pytest.fixture
def rules_factory() -> Callable[..., LeagueRules]:
    def build(
        *,
        teams: int = 12,
        qb: int = 1,
        rb: int = 2,
        wr: int = 2,
        te: int = 1,
        flex_count: int = 1,
        flex_eligible: tuple[str, ...] = ("RB", "WR", "TE"),
        bench: int = 6,
    ) -> LeagueRules:
        roster_size = qb + rb + wr + te + flex_count + bench
        return LeagueRules(
            season=2026,
            teams=teams,
            draft=DraftSettings(rounds=roster_size),
            starters={"QB": qb, "RB": rb, "WR": wr, "TE": te},
            flex_slots=(FlexSlot(name="FLEX", count=flex_count, eligible=flex_eligible),)
            if flex_count
            else (),
            bench=bench,
            scoring=ScoringRules(reception=1),
        )

    return build
