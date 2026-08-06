from fantasy_draft_ai.draft.roster import RosterPlayer, assign_roster
from fantasy_draft_ai.rules.models import DraftSettings, FlexSlot, LeagueRules
from fantasy_draft_ai.scoring.engine import ScoringRules


def _rules(
    *,
    starters: dict[str, int],
    flex_slots: tuple[FlexSlot, ...] = (),
    bench: int = 0,
) -> LeagueRules:
    roster_size = sum(starters.values()) + sum(slot.count for slot in flex_slots) + bench
    return LeagueRules(
        season=2026,
        teams=12,
        draft=DraftSettings(rounds=roster_size),
        starters=starters,
        flex_slots=flex_slots,
        bench=bench,
        scoring=ScoringRules(reception=1),
    )


def test_direct_and_flex_slots_use_exact_assignment_instead_of_greedy_slot_order() -> None:
    rules = _rules(
        starters={"RB": 1},
        flex_slots=(FlexSlot(name="FLEX", count=1, eligible=("RB", "WR")),),
    )
    assignment = assign_roster(
        [
            RosterPlayer("rb", "RB", 100.0),
            RosterPlayer("wr", "WR", 90.0),
        ],
        rules,
    )

    assert assignment.legal
    assert assignment.starter_coverage == 1.0
    assert assignment.starter_value == 190.0
    assert assignment.slot_for_player("rb") == "RB:1"
    assert assignment.slot_for_player("wr") == "FLEX:1"


def test_superflex_and_overlapping_flex_choose_the_maximum_value_legal_lineup() -> None:
    rules = _rules(
        starters={"QB": 1, "RB": 1, "WR": 1},
        flex_slots=(
            FlexSlot(name="FLEX", count=1, eligible=("RB", "WR", "TE")),
            FlexSlot(name="SUPERFLEX", count=1, eligible=("QB", "RB", "WR", "TE")),
        ),
        bench=1,
    )
    assignment = assign_roster(
        [
            RosterPlayer("qb1", "QB", 30.0),
            RosterPlayer("qb2", "QB", 25.0),
            RosterPlayer("rb1", "RB", 24.0),
            RosterPlayer("rb2", "RB", 10.0),
            RosterPlayer("wr1", "WR", 23.0),
            RosterPlayer("wr2", "WR", 22.0),
            RosterPlayer("te1", "TE", 21.0),
        ],
        rules,
    )

    assert {item.player.player_id for item in assignment.starters} == {
        "qb1",
        "qb2",
        "rb1",
        "wr1",
        "wr2",
    }
    assert assignment.starter_value == 124.0
    assert {assignment.slot_for_player("qb1"), assignment.slot_for_player("qb2")} == {
        "QB:1",
        "SUPERFLEX:1",
    }
    assert [player.player_id for player in assignment.bench] == ["te1"]
    assert [player.player_id for player in assignment.unassigned] == ["rb2"]
    assert not assignment.legal


def test_multiple_flex_slots_are_concrete_and_can_both_be_filled() -> None:
    rules = _rules(
        starters={"RB": 1, "WR": 1},
        flex_slots=(FlexSlot(name="FLEX", count=2, eligible=("RB", "WR", "TE")),),
    )
    assignment = assign_roster(
        [
            RosterPlayer("rb", "RB", 10.0),
            RosterPlayer("wr", "WR", 9.0),
            RosterPlayer("te1", "TE", 12.0),
            RosterPlayer("te2", "TE", 11.0),
        ],
        rules,
    )

    assert assignment.legal
    assert assignment.starter_coverage == 1.0
    assert assignment.slot_for_player("rb") == "RB:1"
    assert assignment.slot_for_player("wr") == "WR:1"
    assert {assignment.slot_for_player("te1"), assignment.slot_for_player("te2")} == {
        "FLEX:1",
        "FLEX:2",
    }


def test_bench_capacity_is_universal_and_overflow_is_explicitly_illegal() -> None:
    rules = _rules(starters={"QB": 1}, bench=1)
    assignment = assign_roster(
        [
            RosterPlayer("qb1", "QB", 30.0),
            RosterPlayer("qb2", "QB", 20.0),
            RosterPlayer("qb3", "QB", 10.0),
        ],
        rules,
    )

    assert assignment.slot_for_player("qb1") == "QB:1"
    assert assignment.slot_for_player("qb2") == "BENCH"
    assert assignment.slot_for_player("qb3") is None
    assert [player.player_id for player in assignment.unassigned] == ["qb3"]
    assert not assignment.legal
