from collections.abc import Callable
from pathlib import Path

import duckdb
import pytest
from pydantic import ValidationError

from fantasy_draft_ai.rules.models import LeagueRules
from fantasy_draft_ai.services.league_setup import (
    LeagueSetupIntegrityError,
    LeagueSetupRecord,
    LeagueSetupRepository,
    PlayoffSettings,
)


def _setup(rules: LeagueRules, *, setup_id: str, draft_slot: int) -> LeagueSetupRecord:
    return LeagueSetupRecord(
        league_season_id=setup_id,
        platform="local",
        rules=rules,
        draft_slot=draft_slot,
        playoff_settings=PlayoffSettings(
            playoff_teams=6,
            playoff_start_week=15,
            championship_week=17,
        ),
    )


def test_repository_upsert_is_idempotent_and_replays_exact_rules(
    tmp_path: Path,
    rules_factory: Callable[..., LeagueRules],
) -> None:
    warehouse_path = tmp_path / "warehouse.duckdb"
    repository = LeagueSetupRepository(warehouse_path)
    setup = _setup(rules_factory(), setup_id="home-2026", draft_slot=7)

    assert repository.upsert(setup) == setup
    assert repository.upsert(setup) == setup

    with duckdb.connect(str(warehouse_path), read_only=True) as connection:
        row = connection.execute(
            """
            SELECT count(*), min(user_draft_slot), min(normalized_ruleset_json),
                   min(ruleset_fingerprint)
            FROM league_rules
            WHERE league_season_id = 'home-2026'
            """
        ).fetchone()
    assert row == (1, 7, setup.rules.canonical_json(), setup.rules.fingerprint())
    assert repository.load("  home-2026 ") == setup

    unchecked_copy = setup.model_copy(update={"draft_slot": 99})
    with pytest.raises(ValidationError, match="less than or equal to 32"):
        repository.upsert(unchecked_copy)


def test_repository_updates_lists_and_deletes_local_setups(
    tmp_path: Path,
    rules_factory: Callable[..., LeagueRules],
) -> None:
    repository = LeagueSetupRepository(tmp_path / "warehouse.duckdb")
    rules_2026 = rules_factory()
    rules_2025 = rules_2026.model_copy(update={"season": 2025})
    older = _setup(rules_2025, setup_id="older", draft_slot=1)
    original = _setup(rules_2026, setup_id="current", draft_slot=2)
    updated = original.model_copy(update={"draft_slot": 9, "playoff_settings": None})

    repository.upsert(older)
    repository.upsert(original)
    assert repository.upsert(updated) == updated

    assert repository.list() == (updated, older)
    assert repository.delete("current") is True
    assert repository.delete("current") is False
    assert repository.load("current") is None
    assert repository.list() == (older,)


def test_repository_detects_decomposed_rules_corruption(
    tmp_path: Path,
    rules_factory: Callable[..., LeagueRules],
) -> None:
    warehouse_path = tmp_path / "warehouse.duckdb"
    repository = LeagueSetupRepository(warehouse_path)
    repository.upsert(_setup(rules_factory(), setup_id="corrupt-me", draft_slot=3))
    with duckdb.connect(str(warehouse_path)) as connection:
        connection.execute(
            "UPDATE league_rules SET team_count = 10 WHERE league_season_id = 'corrupt-me'"
        )

    with pytest.raises(LeagueSetupIntegrityError, match="does not match"):
        repository.load("corrupt-me")


def test_repository_never_overwrites_historical_league_row(
    tmp_path: Path,
    rules_factory: Callable[..., LeagueRules],
) -> None:
    warehouse_path = tmp_path / "warehouse.duckdb"
    repository = LeagueSetupRepository(warehouse_path)
    repository.initialize()
    rules = rules_factory()
    with duckdb.connect(str(warehouse_path)) as connection:
        connection.execute(
            """
            INSERT INTO league_rules (
                league_season_id, platform, season, team_count, user_draft_slot,
                draft_type, rounds, starter_slots_json, flex_slots_json,
                bench_slots, ir_slots, scoring_json, playoff_settings_json,
                normalized_ruleset_json, ruleset_fingerprint
            ) VALUES (?, 'historical-import', ?, ?, NULL, 'snake', ?, ?, ?, ?, ?, ?, NULL, ?, ?)
            """,
            [
                "historical-2026",
                rules.season,
                rules.teams,
                rules.draft.rounds,
                "{}",
                "[]",
                rules.bench,
                rules.ir,
                rules.scoring.model_dump_json(),
                rules.canonical_json(),
                rules.fingerprint(),
            ],
        )

    with pytest.raises(LeagueSetupIntegrityError, match="historical"):
        repository.upsert(_setup(rules, setup_id="historical-2026", draft_slot=4))

    with duckdb.connect(str(warehouse_path), read_only=True) as connection:
        row = connection.execute(
            "SELECT platform, user_draft_slot FROM league_rules WHERE league_season_id = ?",
            ["historical-2026"],
        ).fetchone()
    assert row == ("historical-import", None)
