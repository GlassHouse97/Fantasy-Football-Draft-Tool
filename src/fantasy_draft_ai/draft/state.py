"""Pure event reducer for deterministic snake-draft sessions."""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass, replace
from datetime import datetime
from typing import Any

from fantasy_draft_ai.draft.roster import RosterPlayer, assign_roster
from fantasy_draft_ai.rules.models import LeagueRules


class DraftStateError(ValueError):
    """Raised when an event would make the draft stream invalid."""


@dataclass(frozen=True)
class DraftEvent:
    session_id: str
    sequence: int
    event_id: str
    event_type: str
    occurred_at: datetime
    payload: dict[str, Any]
    command_id: str
    prior_state_fingerprint: str | None = None
    resulting_state_fingerprint: str | None = None


@dataclass(frozen=True)
class DraftPick:
    event_id: str
    overall_pick: int
    round: int
    draft_slot: int
    team_id: str
    player_id: str
    player_name: str
    position: str
    projected_points: float

    def as_dict(self) -> dict[str, Any]:
        return {
            "event_id": self.event_id,
            "overall_pick": self.overall_pick,
            "round": self.round,
            "draft_slot": self.draft_slot,
            "team_id": self.team_id,
            "player_id": self.player_id,
            "player_name": self.player_name,
            "position": self.position,
            "projected_points": self.projected_points,
        }


@dataclass(frozen=True)
class DraftHistoryEntry:
    sequence: int
    event_id: str
    event_type: str
    target_event_id: str | None

    def as_dict(self) -> dict[str, Any]:
        return {
            "sequence": self.sequence,
            "event_id": self.event_id,
            "event_type": self.event_type,
            "target_event_id": self.target_event_id,
        }


@dataclass(frozen=True)
class DraftState:
    session_id: str
    rules: LeagueRules
    user_draft_slot: int
    projection_run_id: str
    adp_build_fingerprint: str | None
    player_pool_fingerprint: str
    engine_config_fingerprint: str
    random_seed: int
    simulation_count: int
    picks: tuple[DraftPick, ...] = ()
    history: tuple[DraftHistoryEntry, ...] = ()
    version: int = 0

    @property
    def total_picks(self) -> int:
        return self.rules.teams * self.rules.draft.rounds

    @property
    def complete(self) -> bool:
        return len(self.picks) == self.total_picks

    @property
    def current_overall_pick(self) -> int | None:
        next_pick = len(self.picks) + 1
        return None if next_pick > self.total_picks else next_pick

    @property
    def current_draft_slot(self) -> int | None:
        if self.current_overall_pick is None:
            return None
        return draft_slot_for_pick(self.current_overall_pick, self.rules.teams)

    @property
    def current_team_id(self) -> str | None:
        slot = self.current_draft_slot
        return None if slot is None else team_id_for_slot(slot)

    @property
    def user_team_id(self) -> str:
        return team_id_for_slot(self.user_draft_slot)

    @property
    def is_user_turn(self) -> bool:
        return self.current_draft_slot == self.user_draft_slot

    @property
    def selected_player_ids(self) -> frozenset[str]:
        return frozenset(pick.player_id for pick in self.picks)

    def next_user_pick(self, *, include_current: bool = True) -> int | None:
        current = self.current_overall_pick
        if current is None:
            return None
        start = current if include_current else current + 1
        for overall_pick in range(start, self.total_picks + 1):
            if draft_slot_for_pick(overall_pick, self.rules.teams) == self.user_draft_slot:
                return overall_pick
        return None

    def roster(self, draft_slot: int) -> tuple[DraftPick, ...]:
        return tuple(pick for pick in self.picks if pick.draft_slot == draft_slot)

    def as_dict(self) -> dict[str, Any]:
        return {
            "session_id": self.session_id,
            "ruleset_fingerprint": self.rules.fingerprint(),
            "user_draft_slot": self.user_draft_slot,
            "projection_run_id": self.projection_run_id,
            "adp_build_fingerprint": self.adp_build_fingerprint,
            "player_pool_fingerprint": self.player_pool_fingerprint,
            "engine_config_fingerprint": self.engine_config_fingerprint,
            "random_seed": self.random_seed,
            "simulation_count": self.simulation_count,
            "version": self.version,
            "total_picks": self.total_picks,
            "current_overall_pick": self.current_overall_pick,
            "current_draft_slot": self.current_draft_slot,
            "picks": [pick.as_dict() for pick in self.picks],
            "history": [entry.as_dict() for entry in self.history],
        }

    def fingerprint(self) -> str:
        encoded = json.dumps(
            self.as_dict(),
            sort_keys=True,
            separators=(",", ":"),
            ensure_ascii=True,
            allow_nan=False,
        ).encode("utf-8")
        return hashlib.sha256(encoded).hexdigest()


def team_id_for_slot(draft_slot: int) -> str:
    if draft_slot < 1:
        raise ValueError("draft_slot must be positive.")
    return f"team-{draft_slot:02d}"


def draft_slot_for_pick(overall_pick: int, team_count: int) -> int:
    """Return one-based snake slot, reversing every even round."""

    if overall_pick < 1:
        raise ValueError("overall_pick must be positive.")
    if team_count < 2:
        raise ValueError("team_count must be at least two.")
    round_number = (overall_pick - 1) // team_count + 1
    within_round = (overall_pick - 1) % team_count + 1
    return within_round if round_number % 2 else team_count - within_round + 1


def _new_pick(state: DraftState, event: DraftEvent) -> DraftPick:
    expected = state.current_overall_pick
    if expected is None:
        raise DraftStateError("The draft is complete; no additional pick is legal.")
    overall_pick = int(event.payload.get("overall_pick", -1))
    if overall_pick != expected:
        raise DraftStateError(f"Expected overall pick {expected}, received {overall_pick}.")
    draft_slot = draft_slot_for_pick(overall_pick, state.rules.teams)
    expected_team = team_id_for_slot(draft_slot)
    if str(event.payload.get("team_id")) != expected_team:
        raise DraftStateError(f"Overall pick {overall_pick} belongs to {expected_team}.")
    player_id = str(event.payload.get("player_id", "")).strip()
    player_name = str(event.payload.get("player_name", "")).strip()
    position = str(event.payload.get("position", "")).strip().upper()
    if not player_id or not player_name or not position:
        raise DraftStateError("A pick requires player_id, player_name, and position.")
    if player_id in state.selected_player_ids:
        raise DraftStateError(f"Player {player_id} has already been selected.")
    return DraftPick(
        event_id=event.event_id,
        overall_pick=overall_pick,
        round=(overall_pick - 1) // state.rules.teams + 1,
        draft_slot=draft_slot,
        team_id=expected_team,
        player_id=player_id,
        player_name=player_name,
        position=position,
        projected_points=float(event.payload.get("projected_points", 0.0)),
    )


def _validate_team_roster(state: DraftState, picks: tuple[DraftPick, ...], draft_slot: int) -> None:
    roster = [
        RosterPlayer(pick.player_id, pick.position, pick.projected_points)
        for pick in picks
        if pick.draft_slot == draft_slot
    ]
    assignment = assign_roster(roster, state.rules)
    if not assignment.legal:
        raise DraftStateError(
            "The pick would exceed legal starter/bench capacity for "
            f"{team_id_for_slot(draft_slot)}."
        )


def _start_state(event: DraftEvent) -> DraftState:
    if event.sequence != 0 or event.event_type != "session_started":
        raise DraftStateError("A draft stream must begin with sequence 0 session_started.")
    rules = LeagueRules.model_validate(event.payload.get("rules"))
    ruleset_fingerprint = str(event.payload.get("ruleset_fingerprint", ""))
    if rules.fingerprint() != ruleset_fingerprint:
        raise DraftStateError("The session ruleset fingerprint does not match its rules payload.")
    user_draft_slot = int(event.payload.get("user_draft_slot", 0))
    if not 1 <= user_draft_slot <= rules.teams:
        raise DraftStateError("user_draft_slot must be within the league team count.")
    if rules.draft.keepers:
        raise DraftStateError("Phase 6 sessions do not yet support keeper placement.")
    projection_run_id = str(event.payload.get("projection_run_id", "")).strip()
    if not projection_run_id:
        raise DraftStateError("A session must freeze a projection_run_id.")
    player_pool_fingerprint = str(event.payload.get("player_pool_fingerprint", "")).strip()
    engine_config_fingerprint = str(event.payload.get("engine_config_fingerprint", "")).strip()
    if not player_pool_fingerprint or not engine_config_fingerprint:
        raise DraftStateError("A session must freeze player-pool and engine-config fingerprints.")
    simulation_count = int(event.payload.get("simulation_count", 0))
    if simulation_count < 1:
        raise DraftStateError("simulation_count must be positive.")
    return DraftState(
        session_id=event.session_id,
        rules=rules,
        user_draft_slot=user_draft_slot,
        projection_run_id=projection_run_id,
        adp_build_fingerprint=(
            None
            if event.payload.get("adp_build_fingerprint") is None
            else str(event.payload["adp_build_fingerprint"])
        ),
        player_pool_fingerprint=player_pool_fingerprint,
        engine_config_fingerprint=engine_config_fingerprint,
        random_seed=int(event.payload.get("random_seed", 0)),
        simulation_count=simulation_count,
        history=(DraftHistoryEntry(0, event.event_id, event.event_type, None),),
        version=0,
    )


def apply_event(state: DraftState | None, event: DraftEvent) -> DraftState:
    """Apply one immutable event, rejecting gaps, duplicates, and illegal rosters."""

    if state is None:
        return _start_state(event)
    if event.session_id != state.session_id:
        raise DraftStateError("Event session_id does not match the active state.")
    if event.sequence != state.version + 1:
        raise DraftStateError(
            f"Expected event sequence {state.version + 1}, received {event.sequence}."
        )
    if event.event_type == "pick_made":
        pick = _new_pick(state, event)
        picks = (*state.picks, pick)
        _validate_team_roster(state, picks, pick.draft_slot)
        target_event_id: str | None = None
    elif event.event_type == "pick_undone":
        if not state.picks:
            raise DraftStateError("There is no pick to undo.")
        target_event_id = str(event.payload.get("target_event_id", ""))
        if target_event_id != state.picks[-1].event_id:
            raise DraftStateError("Only the current draft's most recent pick can be undone.")
        picks = state.picks[:-1]
    elif event.event_type == "pick_replaced":
        overall_pick = int(event.payload.get("overall_pick", -1))
        if not 1 <= overall_pick <= len(state.picks):
            raise DraftStateError("Replacement overall_pick does not identify an active pick.")
        prior = state.picks[overall_pick - 1]
        target_event_id = str(event.payload.get("target_event_id", ""))
        if target_event_id != prior.event_id:
            raise DraftStateError("Replacement target_event_id is stale.")
        replacement_payload = dict(event.payload)
        replacement_payload["team_id"] = prior.team_id
        replacement_event = replace(event, payload=replacement_payload)
        without_prior = replace(state, picks=state.picks[: overall_pick - 1])
        replacement_pick = _new_pick(without_prior, replacement_event)
        if replacement_pick.overall_pick != prior.overall_pick:
            raise DraftStateError("A replacement cannot change pick ownership or order.")
        picks_list = list(state.picks)
        picks_list[overall_pick - 1] = replacement_pick
        picks = tuple(picks_list)
        if len({pick.player_id for pick in picks}) != len(picks):
            raise DraftStateError("Replacement would select a duplicate player.")
        _validate_team_roster(state, picks, prior.draft_slot)
    else:
        raise DraftStateError(f"Unsupported draft event type: {event.event_type}.")
    return replace(
        state,
        picks=picks,
        history=(
            *state.history,
            DraftHistoryEntry(
                event.sequence,
                event.event_id,
                event.event_type,
                target_event_id,
            ),
        ),
        version=event.sequence,
    )


def replay_events(session_id: str, events: tuple[DraftEvent, ...]) -> DraftState:
    """Replay an entire append-only stream and verify every stored fingerprint link."""

    if not events:
        raise DraftStateError(f"Draft session {session_id} has no events.")
    state: DraftState | None = None
    for event in events:
        if event.session_id != session_id:
            raise DraftStateError("Draft stream contains an event from another session.")
        prior = None if state is None else state.fingerprint()
        if event.prior_state_fingerprint != prior:
            raise DraftStateError(f"Event {event.sequence} has an invalid prior-state fingerprint.")
        state = apply_event(state, event)
        if event.resulting_state_fingerprint != state.fingerprint():
            raise DraftStateError(f"Event {event.sequence} has an invalid result fingerprint.")
    if state is None:
        raise DraftStateError(f"Draft session {session_id} could not be replayed.")
    return state
