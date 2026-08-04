from collections.abc import Callable

import pandas as pd

from fantasy_draft_ai.rules.models import LeagueRules
from fantasy_draft_ai.rules.replacement import (
    position_demand,
    replacement_levels,
    value_over_replacement,
)


def projection_fixture(players_per_position: int = 90) -> pd.DataFrame:
    rows = []
    for position, offset in (("QB", 60), ("RB", 30), ("WR", 25), ("TE", 0)):
        for rank in range(players_per_position):
            rows.append(
                {
                    "player_id": f"{position}_{rank:03d}",
                    "position": position,
                    "projected_points": 300 + offset - rank * 2,
                }
            )
    return pd.DataFrame(rows)


def test_position_demand_changes_with_teams_and_starters(
    rules_factory: Callable[..., LeagueRules],
) -> None:
    small = rules_factory(teams=10, wr=2, flex_count=1)
    large = rules_factory(teams=12, wr=3, flex_count=2)
    assert position_demand(small, "WR").direct_starters == 20
    assert position_demand(large, "WR").direct_starters == 36
    assert position_demand(small, "WR").flex_eligible_slots == 10
    assert position_demand(large, "WR").flex_eligible_slots == 24


def test_extra_wr_and_flex_demand_lowers_last_starter_threshold(
    rules_factory: Callable[..., LeagueRules],
) -> None:
    projections = projection_fixture()
    shallow = replacement_levels(projections, rules_factory(wr=2, flex_count=1, bench=0))
    deep = replacement_levels(projections, rules_factory(wr=3, flex_count=2, bench=0))
    assert deep["WR"].estimated_starters > shallow["WR"].estimated_starters
    assert deep["WR"].last_starter_points < shallow["WR"].last_starter_points
    assert deep["RB"].estimated_starters >= shallow["RB"].estimated_starters


def test_replacement_definitions_and_vorp_are_available(
    rules_factory: Callable[..., LeagueRules],
) -> None:
    levels = replacement_levels(projection_fixture(), rules_factory())
    wr = levels["WR"]
    assert wr.last_starter_points is not None
    assert wr.waiver_percentile_points is not None
    assert value_over_replacement(250, wr.last_starter_points) == 250 - wr.last_starter_points
