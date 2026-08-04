from collections.abc import Callable

from fantasy_draft_ai.rules.models import LeagueRules


def test_flex_eligibility_is_explicit_and_normalized(
    rules_factory: Callable[..., LeagueRules],
) -> None:
    rules = rules_factory(flex_eligible=("wr", "TE", "rb", "WR"))
    assert rules.slot_eligibility()["FLEX"] == ("RB", "TE", "WR")
    assert rules.eligible_slots("TE") == ("FLEX", "TE")
    assert rules.eligible_slots("QB") == ("QB",)


def test_superflex_and_multiple_flex_slots(rules_factory: Callable[..., LeagueRules]) -> None:
    rules = rules_factory(flex_count=2, flex_eligible=("QB", "RB", "WR", "TE"))
    assert rules.flex_slots[0].count == 2
    assert "FLEX" in rules.eligible_slots("QB")


def test_fingerprint_is_deterministic_for_equivalent_input(
    rules_factory: Callable[..., LeagueRules],
) -> None:
    first = rules_factory(flex_eligible=("RB", "WR", "TE"))
    payload = first.model_dump(mode="python")
    payload["starters"] = dict(reversed(list(payload["starters"].items())))
    payload["flex_slots"][0]["eligible"] = ("TE", "RB", "WR")
    second = LeagueRules.model_validate(payload)
    assert first.canonical_json() == second.canonical_json()
    assert first.fingerprint() == second.fingerprint()
