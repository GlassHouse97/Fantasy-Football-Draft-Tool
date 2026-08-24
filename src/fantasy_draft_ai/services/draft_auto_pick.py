"""Deterministic opponent picks for the recommendation-first draft assistant."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime

from fantasy_draft_ai.draft.repository import DraftRepository
from fantasy_draft_ai.draft.roster import RosterPlayer, assign_roster
from fantasy_draft_ai.draft.state import DraftEvent, DraftPick, apply_event
from fantasy_draft_ai.recommendations.config import DraftEngineConfig
from fantasy_draft_ai.recommendations.projection_baseline import build_projection_rankings
from fantasy_draft_ai.services.draft_room import (
    DraftRoomServiceError,
    DraftRoomSession,
    load_draft_session,
)


@dataclass(frozen=True)
class AutoPickResult:
    """The verified session and opponent picks created by one sim-to-turn action."""

    session: DraftRoomSession
    simulated_picks: tuple[DraftPick, ...]


def simulate_opponents_to_user_turn(
    repository: DraftRepository,
    session_id: str,
    *,
    expected_version: int,
    engine_config: DraftEngineConfig,
    command_id: str,
) -> AutoPickResult:
    """Persist projection-guided opponent picks until the user is on the clock.

    Each CPU team takes the highest league-specific projection ranking that keeps its
    roster legal. Picks remain ordinary append-only draft events, so replay, rosters,
    the draft board, and single-pick undo continue to use one source of truth.
    """

    session = load_draft_session(repository, session_id)
    if session.state.version != expected_version:
        raise DraftRoomServiceError(
            "The draft changed before opponent picks could be simulated. Refresh and try again."
        )
    if session.state.engine_config_fingerprint != engine_config.fingerprint():
        raise DraftRoomServiceError(
            "This draft was created with a different recommendation configuration."
        )

    planned_player_ids: list[str] = []
    players_by_id = {player.player_id: player for player in session.players}
    rankings = build_projection_rankings(session.state.rules, session.players)
    preview_state = session.state
    while not preview_state.complete and not preview_state.is_user_turn:
        current_slot = preview_state.current_draft_slot
        current_pick = preview_state.current_overall_pick
        if current_slot is None or current_pick is None:
            break

        opponent_roster = tuple(
            RosterPlayer(pick.player_id, pick.position, pick.projected_points)
            for pick in preview_state.roster(current_slot)
        )
        player = next(
            (
                players_by_id[row.player_id]
                for row in rankings
                if row.player_id not in preview_state.selected_player_ids
                and assign_roster(
                    (
                        *opponent_roster,
                        RosterPlayer(row.player_id, row.position, row.p50),
                    ),
                    preview_state.rules,
                ).legal
            ),
            None,
        )
        if player is None:
            raise DraftRoomServiceError(
                f"Opponent pick {current_pick} could not be simulated because no legal "
                "projected player remains."
            )

        planned_player_ids.append(player.player_id)
        preview_event = DraftEvent(
            session_id=session_id,
            sequence=preview_state.version + 1,
            event_id=f"preview-{command_id}-{current_pick}",
            event_type="pick_made",
            occurred_at=datetime.now(UTC),
            command_id=f"preview-{command_id}-{current_pick}",
            payload={
                "overall_pick": current_pick,
                "team_id": preview_state.current_team_id,
                "player_id": player.player_id,
                "player_name": player.display_name,
                "position": player.position,
                "projected_points": player.p50,
            },
            prior_state_fingerprint=preview_state.fingerprint(),
        )
        preview_state = apply_event(preview_state, preview_event)

    if not planned_player_ids:
        return AutoPickResult(session=session, simulated_picks=())

    start_pick_count = len(session.state.picks)
    repository.record_pick_batch(
        session_id,
        tuple(planned_player_ids),
        expected_version=expected_version,
        command_id=command_id,
    )
    session = load_draft_session(repository, session_id)

    return AutoPickResult(
        session=session,
        simulated_picks=session.state.picks[start_pick_count:],
    )
