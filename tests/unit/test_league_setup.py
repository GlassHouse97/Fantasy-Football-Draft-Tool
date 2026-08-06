from collections.abc import Callable
from pathlib import Path

import pytest
from pydantic import ValidationError

from fantasy_draft_ai.rules.models import LeagueRules
from fantasy_draft_ai.services.league_setup import (
    LeagueSetupRecord,
    PlayoffSettings,
    export_setup_yaml,
    human_ruleset_label,
    import_setup_yaml,
    load_reference_rules,
)


def test_setup_validates_team_dependent_draft_and_playoff_fields(
    rules_factory: Callable[..., LeagueRules],
) -> None:
    rules = rules_factory(teams=10)

    with pytest.raises(ValidationError, match="Draft slot"):
        LeagueSetupRecord(
            league_season_id="test-2026",
            rules=rules,
            draft_slot=11,
        )
    with pytest.raises(ValidationError, match="Playoff teams"):
        LeagueSetupRecord(
            league_season_id="test-2026",
            rules=rules,
            draft_slot=5,
            playoff_settings=PlayoffSettings(
                playoff_teams=12,
                playoff_start_week=15,
                championship_week=17,
            ),
        )
    with pytest.raises(ValidationError, match="cannot be before"):
        PlayoffSettings(
            playoff_teams=6,
            playoff_start_week=17,
            championship_week=16,
        )


def test_setup_yaml_is_deterministic_replay_safe_and_strict(
    rules_factory: Callable[..., LeagueRules],
) -> None:
    setup = LeagueSetupRecord(
        league_season_id="  home-league-2026  ",
        platform="  local  ",
        rules=rules_factory(),
        draft_slot=4,
        playoff_settings=PlayoffSettings(
            playoff_teams=6,
            playoff_start_week=15,
            championship_week=17,
        ),
    )

    first = export_setup_yaml(setup)
    assert first == export_setup_yaml(setup)
    assert import_setup_yaml(first) == setup
    assert setup.league_season_id == "home-league-2026"
    assert setup.canonical_json() == import_setup_yaml(first).canonical_json()

    tampered = first.replace(setup.rules.fingerprint(), "0" * 64)
    with pytest.raises(ValidationError, match="does not match"):
        import_setup_yaml(tampered)

    with pytest.raises(ValidationError, match="Field required"):
        import_setup_yaml("schema_version: league-setup-v1\n")


def test_human_label_is_deterministic_and_contains_rules_fingerprint(
    rules_factory: Callable[..., LeagueRules],
) -> None:
    rules = rules_factory()

    label = human_ruleset_label(rules)

    assert label == f"2026 | 12-team PPR snake | {rules.fingerprint()[:10]}"
    assert (
        LeagueSetupRecord(
            league_season_id="label-test",
            rules=rules,
            draft_slot=1,
        ).fingerprint_label
        == label
    )


def test_checked_in_reference_rules_are_the_default(tmp_path: Path) -> None:
    default = load_reference_rules()
    copied = tmp_path / "reference.yaml"
    copied.write_text(
        """
season: 2026
teams: 4
draft: {type: snake, rounds: 5, keepers: 0}
starters: {QB: 1, RB: 1, WR: 1, TE: 1}
flex_slots: []
bench: 1
ir: 0
scoring: {reception: 0.5}
""".strip(),
        encoding="utf-8",
    )

    custom = load_reference_rules(copied)

    assert default.teams == 12
    assert default.scoring.reception == 1
    assert custom.teams == 4
    assert custom.scoring.reception == 0.5
