from dataclasses import replace
from datetime import UTC, datetime

import pytest

from fantasy_draft_ai.draft.state import (
    DraftEvent,
    DraftState,
    DraftStateError,
    apply_event,
    draft_slot_for_pick,
    team_id_for_slot,
)
from fantasy_draft_ai.rules.models import DraftSettings, LeagueRules
from fantasy_draft_ai.scoring.engine import ScoringRules

NOW = datetime(2026, 8, 6, 12, tzinfo=UTC)


def _rules(*, teams: int = 4, rounds: int = 4) -> LeagueRules:
    return LeagueRules(
        season=2026,
        teams=teams,
        draft=DraftSettings(rounds=rounds),
        starters={"QB": 1},
        bench=rounds - 1,
        scoring=ScoringRules(reception=1),
    )


def _start_event(*, user_draft_slot: int = 3, teams: int = 4) -> DraftEvent:
    rules = _rules(teams=teams)
    return DraftEvent(
        session_id="draft-test",
        sequence=0,
        event_id="event-start",
        event_type="session_started",
        occurred_at=NOW,
        command_id="command-start",
        payload={
            "rules": rules.model_dump(mode="json"),
            "ruleset_fingerprint": rules.fingerprint(),
            "user_draft_slot": user_draft_slot,
            "projection_run_id": "phase4-test",
            "adp_build_fingerprint": "phase5-test",
            "player_pool_fingerprint": "pool-test",
            "engine_config_fingerprint": "engine-test",
            "random_seed": 42,
            "simulation_count": 100,
        },
    )


def _pick_event(state: DraftState, player_id: str, *, event_id: str) -> DraftEvent:
    overall_pick = state.current_overall_pick
    team_id = state.current_team_id
    assert overall_pick is not None
    assert team_id is not None
    return DraftEvent(
        session_id=state.session_id,
        sequence=state.version + 1,
        event_id=event_id,
        event_type="pick_made",
        occurred_at=NOW,
        command_id=f"command-{event_id}",
        payload={
            "overall_pick": overall_pick,
            "team_id": team_id,
            "player_id": player_id,
            "player_name": f"Player {player_id}",
            "position": "QB",
            "projected_points": 300.0 - overall_pick,
        },
    )


@pytest.mark.parametrize("team_count", range(4, 33))
def test_snake_order_reverses_even_rounds_and_preserves_turn_boundaries(
    team_count: int,
) -> None:
    first_round = [draft_slot_for_pick(pick, team_count) for pick in range(1, team_count + 1)]
    second_round = [
        draft_slot_for_pick(pick, team_count) for pick in range(team_count + 1, 2 * team_count + 1)
    ]
    third_round = [
        draft_slot_for_pick(pick, team_count)
        for pick in range(2 * team_count + 1, 3 * team_count + 1)
    ]

    assert first_round == list(range(1, team_count + 1))
    assert second_round == list(range(team_count, 0, -1))
    assert third_round == first_round
    assert draft_slot_for_pick(team_count, team_count) == draft_slot_for_pick(
        team_count + 1, team_count
    )
    assert draft_slot_for_pick(2 * team_count, team_count) == draft_slot_for_pick(
        2 * team_count + 1, team_count
    )


def test_current_and_next_user_pick_are_unambiguous_before_and_after_user_turn() -> None:
    state = apply_event(None, _start_event(user_draft_slot=3))
    assert state.current_overall_pick == 1
    assert state.current_draft_slot == 1
    assert state.current_team_id == team_id_for_slot(1)
    assert state.next_user_pick() == 3
    assert not state.is_user_turn

    state = apply_event(state, _pick_event(state, "p1", event_id="event-p1"))
    state = apply_event(state, _pick_event(state, "p2", event_id="event-p2"))
    assert state.current_overall_pick == 3
    assert state.current_draft_slot == 3
    assert state.is_user_turn
    assert state.next_user_pick() == 3
    assert state.next_user_pick(include_current=False) == 6

    state = apply_event(state, _pick_event(state, "p3", event_id="event-p3"))
    assert state.current_overall_pick == 4
    assert state.next_user_pick() == 6


def test_pick_undo_repick_and_replace_preserve_order_and_history() -> None:
    state = apply_event(None, _start_event(user_draft_slot=1))
    first = _pick_event(state, "p1", event_id="event-p1")
    state = apply_event(state, first)
    second = _pick_event(state, "p2", event_id="event-p2")
    state = apply_event(state, second)

    undo = DraftEvent(
        session_id=state.session_id,
        sequence=state.version + 1,
        event_id="event-undo",
        event_type="pick_undone",
        occurred_at=NOW,
        command_id="command-undo",
        payload={"target_event_id": second.event_id},
    )
    state = apply_event(state, undo)
    assert [pick.player_id for pick in state.picks] == ["p1"]
    assert state.current_overall_pick == 2

    state = apply_event(state, _pick_event(state, "p3", event_id="event-p3"))
    replace_first = DraftEvent(
        session_id=state.session_id,
        sequence=state.version + 1,
        event_id="event-replace",
        event_type="pick_replaced",
        occurred_at=NOW,
        command_id="command-replace",
        payload={
            "overall_pick": 1,
            "target_event_id": first.event_id,
            "team_id": first.payload["team_id"],
            "player_id": "p4",
            "player_name": "Player p4",
            "position": "QB",
            "projected_points": 325.0,
        },
    )
    state = apply_event(state, replace_first)

    assert [pick.player_id for pick in state.picks] == ["p4", "p3"]
    assert [pick.overall_pick for pick in state.picks] == [1, 2]
    assert state.picks[0].draft_slot == 1
    assert state.current_overall_pick == 3
    assert state.version == 5
    assert state.history[-2].target_event_id is None
    assert state.history[-1].target_event_id == first.event_id


def test_duplicate_players_stale_targets_and_sequence_gaps_are_rejected() -> None:
    state = apply_event(None, _start_event())
    first = _pick_event(state, "p1", event_id="event-p1")
    state = apply_event(state, first)

    duplicate = _pick_event(state, "p1", event_id="event-duplicate")
    with pytest.raises(DraftStateError, match="already been selected"):
        apply_event(state, duplicate)

    stale_undo = DraftEvent(
        session_id=state.session_id,
        sequence=state.version + 1,
        event_id="event-stale-undo",
        event_type="pick_undone",
        occurred_at=NOW,
        command_id="command-stale-undo",
        payload={"target_event_id": "not-the-active-event"},
    )
    with pytest.raises(DraftStateError, match="most recent pick"):
        apply_event(state, stale_undo)

    stale_replace = DraftEvent(
        session_id=state.session_id,
        sequence=state.version + 1,
        event_id="event-stale-replace",
        event_type="pick_replaced",
        occurred_at=NOW,
        command_id="command-stale-replace",
        payload={
            "overall_pick": 1,
            "target_event_id": "not-the-active-event",
            "team_id": team_id_for_slot(1),
            "player_id": "p2",
            "player_name": "Player p2",
            "position": "QB",
            "projected_points": 250.0,
        },
    )
    with pytest.raises(DraftStateError, match="target_event_id is stale"):
        apply_event(state, stale_replace)

    with pytest.raises(DraftStateError, match="Expected event sequence"):
        apply_event(state, replace(_pick_event(state, "p2", event_id="event-gap"), sequence=3))
