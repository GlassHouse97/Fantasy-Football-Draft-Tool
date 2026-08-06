import hashlib
import json
from dataclasses import replace
from datetime import UTC, datetime
from pathlib import Path

import duckdb
import pytest

from fantasy_draft_ai.draft.pool import FrozenDraftPlayer
from fantasy_draft_ai.draft.repository import DraftConcurrencyError, DraftRepository
from fantasy_draft_ai.draft.state import DraftStateError
from fantasy_draft_ai.rules.models import DraftSettings, LeagueRules
from fantasy_draft_ai.scoring.engine import ScoringRules

CAPTURED_AT = datetime(2026, 8, 4, 21, 3, tzinfo=UTC)


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
    positions = ("QB", "RB", "WR", "TE", "QB", "RB", "WR", "TE")
    return tuple(
        FrozenDraftPlayer(
            player_id=f"p{index}",
            display_name=f"Player {index}",
            position=position,
            p10=200.0 - index,
            p50=220.0 - index,
            p90=240.0 - index,
            prediction_status="validated",
            projection_source="learned",
            projection_method="test-model",
            market_source="ffc" if index <= 4 else None,
            market_snapshot_id="snapshot-test" if index <= 4 else None,
            market_captured_at=CAPTURED_AT if index <= 4 else None,
            average_pick=float(index) if index <= 4 else None,
            availability_scale=5.0 if index <= 4 else None,
            availability_evidence="source_stddev" if index <= 4 else None,
            mapping_confidence="reviewed" if index <= 4 else None,
        )
        for index, position in enumerate(positions, start=1)
    )


def _create_repository(tmp_path: Path) -> tuple[DraftRepository, tuple[FrozenDraftPlayer, ...]]:
    repository = DraftRepository(tmp_path / "warehouse.duckdb")
    players = _players()
    repository.create_session(
        session_id="draft-test",
        command_id="create-test",
        session_name="Integration draft",
        rules=_rules(),
        user_draft_slot=2,
        projection_run_id="phase4-test",
        adp_build_fingerprint="phase5-test",
        players=players,
        engine_config_fingerprint="engine-test",
        recommendation_status="available",
        recommendation_message="fixture inputs are complete",
        random_seed=42,
        simulation_count=100,
    )
    return repository, players


def test_commands_are_idempotent_and_reject_stale_versions_and_duplicate_players(
    tmp_path: Path,
) -> None:
    repository, _ = _create_repository(tmp_path)

    first = repository.record_pick(
        "draft-test", "p1", expected_version=0, command_id="pick-command-1"
    )
    repeated = repository.record_pick(
        "draft-test", "p1", expected_version=0, command_id="pick-command-1"
    )
    assert repeated == first
    assert repeated.version == 1
    assert [pick.player_id for pick in repeated.picks] == ["p1"]

    with pytest.raises(DraftConcurrencyError, match="expected 0, current 1"):
        repository.record_pick("draft-test", "p2", expected_version=0, command_id="stale-command")
    with pytest.raises(DraftStateError, match="already been selected"):
        repository.record_pick(
            "draft-test", "p1", expected_version=1, command_id="duplicate-command"
        )

    with duckdb.connect(str(repository.path), read_only=True) as connection:
        event_count = connection.execute(
            "SELECT count(*) FROM draft_events WHERE session_id = 'draft-test'"
        ).fetchone()
    assert event_count == (2,)
    assert repository.verify_session("draft-test") == first


def test_idempotency_key_is_bound_to_the_original_command_semantics(tmp_path: Path) -> None:
    repository, _ = _create_repository(tmp_path)

    first = repository.record_pick(
        "draft-test", "p1", expected_version=0, command_id="shared-command"
    )
    assert (
        repository.record_pick(
            "draft-test", "p1", expected_version=0, command_id="shared-command"
        )
        == first
    )
    second = repository.record_pick(
        "draft-test", "p2", expected_version=first.version, command_id="second-command"
    )
    assert (
        repository.record_pick(
            "draft-test", "p1", expected_version=0, command_id="shared-command"
        )
        == second
    )

    with pytest.raises(DraftStateError, match="already bound to a different draft command"):
        repository.record_pick(
            "draft-test", "p3", expected_version=0, command_id="shared-command"
        )
    with pytest.raises(DraftStateError, match="already bound to a different draft command"):
        repository.undo_last(
            "draft-test", expected_version=0, command_id="shared-command"
        )

    with duckdb.connect(str(repository.path), read_only=True) as connection:
        event_count = connection.execute(
            "SELECT count(*) FROM draft_events WHERE session_id = 'draft-test'"
        ).fetchone()
    assert event_count == (3,)


def test_pick_undo_replace_replay_and_frozen_pool_are_persisted_exactly(tmp_path: Path) -> None:
    repository, players = _create_repository(tmp_path)

    state = repository.record_pick("draft-test", "p1", expected_version=0, command_id="pick-p1")
    state = repository.record_pick(
        "draft-test", "p2", expected_version=state.version, command_id="pick-p2"
    )
    state = repository.undo_last("draft-test", expected_version=state.version, command_id="undo-p2")
    state = repository.record_pick(
        "draft-test", "p3", expected_version=state.version, command_id="pick-p3"
    )
    state = repository.replace_pick(
        "draft-test",
        1,
        "p4",
        expected_version=state.version,
        command_id="replace-p1-with-p4",
    )

    assert state.version == 5
    assert [pick.player_id for pick in state.picks] == ["p4", "p3"]
    assert len(state.history) == 6
    assert repository.load_state("draft-test") == state
    assert repository.verify_session("draft-test") == state

    stored_players = repository.load_players("draft-test")
    assert stored_players == players
    changed_local_copy = replace(players[0], p10=998.0, p50=999.0, p90=1000.0)
    assert changed_local_copy.p50 == 999.0
    assert repository.load_players("draft-test")[0].p50 == players[0].p50

    info = repository.session_info("draft-test")
    assert info.current_version == state.version
    assert info.state_fingerprint == state.fingerprint()
    assert info.player_pool_rows == len(players)
    assert info.mapped_market_rows == 4


def test_event_fingerprint_tampering_is_detected_by_replay_and_integrity_audit(
    tmp_path: Path,
) -> None:
    repository, _ = _create_repository(tmp_path)
    repository.record_pick("draft-test", "p1", expected_version=0, command_id="pick-p1")

    with duckdb.connect(str(repository.path)) as connection:
        connection.execute(
            "UPDATE draft_events SET prior_state_fingerprint = 'tampered' "
            "WHERE session_id = 'draft-test' AND sequence = 1"
        )

    with pytest.raises(DraftStateError, match="invalid prior-state fingerprint"):
        repository.verify_session("draft-test")
    issues = repository.integrity_issues()
    assert len(issues) == 1
    assert "failed replay integrity" in issues[0]
    assert "invalid prior-state fingerprint" in issues[0]


def test_frozen_player_column_tampering_is_detected_against_canonical_payload(
    tmp_path: Path,
) -> None:
    repository, _ = _create_repository(tmp_path)

    with duckdb.connect(str(repository.path)) as connection:
        connection.execute(
            "UPDATE draft_session_players SET p50 = 999 "
            "WHERE session_id = 'draft-test' AND player_id = 'p1'"
        )

    with pytest.raises(DraftStateError, match="columns do not match player_payload"):
        repository.verify_session("draft-test")
    issues = repository.integrity_issues()
    assert any("failed replay integrity" in issue for issue in issues)
    assert any("columns do not match player_payload" in issue for issue in issues)


def test_recommendation_audit_binds_payload_to_historical_event_state(tmp_path: Path) -> None:
    repository, _ = _create_repository(tmp_path)
    state = repository.record_pick(
        "draft-test", "p1", expected_version=0, command_id="pick-p1"
    )
    payload = {
        "available": True,
        "code": "recommendation_ready",
        "message": "fixture",
        "session_id": state.session_id,
        "session_version": state.version,
        "state_fingerprint": state.fingerprint(),
        "projection_run_id": state.projection_run_id,
        "adp_build_fingerprint": state.adp_build_fingerprint,
        "player_pool_fingerprint": state.player_pool_fingerprint,
        "engine_config_fingerprint": state.engine_config_fingerprint,
        "random_seed": state.random_seed,
        "simulation_count": state.simulation_count,
        "candidates": [],
        "limitations": [],
    }

    def fingerprint(value: dict[str, object]) -> str:
        encoded = json.dumps(
            value,
            sort_keys=True,
            separators=(",", ":"),
            ensure_ascii=True,
            allow_nan=False,
        ).encode("utf-8")
        return hashlib.sha256(encoded).hexdigest()

    repository.save_recommendation(
        recommendation_run_id="recommendation-test",
        session_id=state.session_id,
        state=state,
        engine_config_fingerprint=state.engine_config_fingerprint,
        random_seed=state.random_seed,
        simulation_count=state.simulation_count,
        status="recommendation_ready",
        result_fingerprint=fingerprint(payload),
        result_payload=payload,
    )
    assert repository.integrity_issues() == ()

    with duckdb.connect(str(repository.path)) as connection:
        connection.execute(
            "UPDATE draft_recommendation_runs SET state_fingerprint = 'tampered' "
            "WHERE recommendation_run_id = 'recommendation-test'"
        )
    assert any(
        "invalid session/config lineage" in issue for issue in repository.integrity_issues()
    )

    altered_payload = dict(payload)
    altered_payload["state_fingerprint"] = "tampered-payload"
    with duckdb.connect(str(repository.path)) as connection:
        connection.execute(
            """
            UPDATE draft_recommendation_runs
            SET state_fingerprint = ?, result_payload = ?, result_fingerprint = ?
            WHERE recommendation_run_id = 'recommendation-test'
            """,
            [
                state.fingerprint(),
                json.dumps(altered_payload, sort_keys=True, separators=(",", ":")),
                fingerprint(altered_payload),
            ],
        )
    assert any(
        "invalid result-payload lineage" in issue for issue in repository.integrity_issues()
    )
