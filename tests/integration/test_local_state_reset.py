from __future__ import annotations

from datetime import UTC, datetime
from pathlib import Path

import duckdb
import pytest

from fantasy_draft_ai.draft.pool import FrozenDraftPlayer
from fantasy_draft_ai.draft.repository import DraftRepository
from fantasy_draft_ai.rules.models import DraftSettings, LeagueRules
from fantasy_draft_ai.scoring.engine import ScoringRules
from fantasy_draft_ai.services.league_setup import (
    LeagueSetupRecord,
    LeagueSetupRepository,
)
from fantasy_draft_ai.services.local_state import (
    LocalStateResetError,
    preview_local_state,
    restore_phase8_defaults,
)

NOW = datetime(2026, 8, 6, 20, 30, tzinfo=UTC)


def _rules() -> LeagueRules:
    return LeagueRules(
        season=2026,
        teams=4,
        draft=DraftSettings(rounds=3),
        starters={"QB": 1},
        bench=2,
        scoring=ScoringRules(reception=1),
    )


def _players() -> tuple[FrozenDraftPlayer, ...]:
    return tuple(
        FrozenDraftPlayer(
            player_id=f"player-{index}",
            display_name=f"Player {index}",
            position=position,
            p10=190.0 - index,
            p50=210.0 - index,
            p90=230.0 - index,
            prediction_status="validated",
            projection_source="test",
            projection_method="test",
        )
        for index, position in enumerate(("QB", "RB", "WR", "TE"), start=1)
    )


def _table_counts(path: Path) -> dict[str, int]:
    with duckdb.connect(str(path), read_only=True) as connection:
        tables = [str(row[0]) for row in connection.execute("SHOW TABLES").fetchall()]
        counts: dict[str, int] = {}
        for table in tables:
            row = connection.execute(f'SELECT count(*) FROM "{table}"').fetchone()
            assert row is not None
            counts[table] = int(row[0])
        return counts


def _seed_history_evidence(path: Path, rules: LeagueRules) -> None:
    setup_repository = LeagueSetupRepository(path)
    setup_repository.upsert(
        LeagueSetupRecord(
            league_season_id="history-2025",
            platform="espn",
            rules=rules.model_copy(update={"season": 2025}),
            draft_slot=1,
        )
    )
    with duckdb.connect(str(path)) as connection:
        connection.execute(
            """
            UPDATE league_rules
            SET user_draft_slot = NULL,
                source_dataset_id = 'history-dataset',
                row_fingerprint = 'history-rules',
                loaded_at = ?
            WHERE league_season_id = 'history-2025'
            """,
            [NOW],
        )
        connection.execute(
            """
            INSERT INTO league_history_imports VALUES (
                'history-package', 'league-history-v1', 'history-dataset',
                'data/raw/history.zip', 'raw-hash', 'normalized-hash', 'loaded',
                1, 1, 1, 1, 0, '{}', ?
            )
            """,
            [NOW],
        )
        connection.execute(
            """
            INSERT INTO league_history_leagues VALUES (
                'history-2025', 'history-package', 2025, 4, ?,
                1, 1, 1, 1, true, true, true
            )
            """,
            [rules.model_copy(update={"season": 2025}).fingerprint()],
        )
        connection.execute(
            """
            INSERT INTO draft_picks (
                league_season_id, overall_pick, round, draft_slot, team_id,
                player_name, position, source_platform, source_player_id,
                mapping_confidence, is_keeper, is_autopick, source_dataset_id,
                row_fingerprint, loaded_at
            ) VALUES (
                'history-2025', 1, 1, 1, 'team-1', 'Historical Player', 'QB',
                'espn', 'espn-1', 'unresolved', false, false,
                'history-dataset', 'history-pick', ?
            )
            """,
            [NOW],
        )
        connection.execute(
            """
            INSERT INTO team_outcomes (
                league_season_id, team_id, wins, losses, ties, points_for,
                points_against, made_playoffs, final_place, is_champion,
                source_dataset_id, row_fingerprint, loaded_at
            ) VALUES (
                'history-2025', 'team-1', 10, 4, 0, 1500, 1400,
                true, 2, false, 'history-dataset', 'history-outcome', ?
            )
            """,
            [NOW],
        )


def test_restore_removes_only_local_setup_and_practice_draft_state(tmp_path: Path) -> None:
    path = tmp_path / "warehouse.duckdb"
    rules = _rules()
    setup_repository = LeagueSetupRepository(path)
    setup_repository.upsert(
        LeagueSetupRecord(
            league_season_id="local-setup",
            platform="local",
            rules=rules,
            draft_slot=2,
        )
    )
    draft_repository = DraftRepository(path)
    draft_repository.create_session(
        session_id="draft-test",
        command_id="create-test",
        session_name="Practice draft",
        rules=rules,
        user_draft_slot=2,
        projection_run_id="phase4-test",
        adp_build_fingerprint=None,
        players=_players(),
        engine_config_fingerprint="engine-test",
        recommendation_status="locked",
        recommendation_message="Test fixture",
        random_seed=42,
        simulation_count=16,
    )
    draft_repository.record_pick(
        "draft-test",
        "player-1",
        expected_version=0,
        command_id="pick-test",
    )
    with duckdb.connect(str(path)) as connection:
        connection.execute(
            """
            INSERT INTO draft_recommendation_runs VALUES (
                'recommendation-test', 'draft-test', 1, 'state-test',
                'engine-test', 42, 16, 'locked', 'result-test', '{}', ?
            )
            """,
            [NOW],
        )
    _seed_history_evidence(path, rules)

    before_counts = _table_counts(path)
    preview = preview_local_state(path)

    assert preview.saved_league_setups == 1
    assert preview.practice_drafts == 1
    assert preview.recorded_picks == 1
    assert preview.draft_events == 2
    assert preview.frozen_player_rows == 4
    assert preview.recommendation_runs == 1

    removed = restore_phase8_defaults(path, expected_summary=preview)
    after_counts = _table_counts(path)

    assert removed == preview
    assert preview_local_state(path).is_empty
    assert after_counts["league_rules"] == before_counts["league_rules"] - 1
    assert after_counts["draft_sessions"] == 0
    assert after_counts["draft_session_players"] == 0
    assert after_counts["draft_events"] == 0
    assert after_counts["draft_recommendation_runs"] == 0
    for table, count in before_counts.items():
        if table not in {
            "league_rules",
            "draft_sessions",
            "draft_session_players",
            "draft_events",
            "draft_recommendation_runs",
        }:
            assert after_counts[table] == count

    with duckdb.connect(str(path), read_only=True) as connection:
        assert connection.execute(
            "SELECT user_draft_slot, source_dataset_id FROM league_rules "
            "WHERE league_season_id = 'history-2025'"
        ).fetchone() == (None, "history-dataset")
        assert connection.execute("SELECT count(*) FROM draft_picks").fetchone() == (1,)
        assert connection.execute("SELECT count(*) FROM team_outcomes").fetchone() == (1,)
        assert connection.execute("SELECT count(*) FROM league_history_imports").fetchone() == (1,)


def test_restore_is_idempotent_when_local_state_is_already_empty(tmp_path: Path) -> None:
    path = tmp_path / "warehouse.duckdb"

    first_preview = preview_local_state(path)
    assert restore_phase8_defaults(path, expected_summary=first_preview).is_empty
    second_preview = preview_local_state(path)
    assert restore_phase8_defaults(path, expected_summary=second_preview).is_empty
    assert preview_local_state(path).is_empty


def test_restore_rejects_a_stale_confirmation_before_deleting_anything(
    tmp_path: Path,
) -> None:
    path = tmp_path / "warehouse.duckdb"
    rules = _rules()
    repository = LeagueSetupRepository(path)
    repository.upsert(
        LeagueSetupRecord(
            league_season_id="first-setup",
            platform="local",
            rules=rules,
            draft_slot=1,
        )
    )
    stale_preview = preview_local_state(path)
    repository.upsert(
        LeagueSetupRecord(
            league_season_id="second-setup",
            platform="local",
            rules=rules,
            draft_slot=2,
        )
    )

    with pytest.raises(LocalStateResetError, match="changed after the confirmation"):
        restore_phase8_defaults(path, expected_summary=stale_preview)

    current = preview_local_state(path)
    assert current.saved_league_setups == 2
    assert repository.load("first-setup") is not None
    assert repository.load("second-setup") is not None
