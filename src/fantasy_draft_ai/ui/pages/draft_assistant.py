"""Recommendation-first redraft workflow for human draft-day use."""

from __future__ import annotations

import uuid
from collections import Counter
from collections.abc import Sequence
from math import isfinite
from typing import Any

import pandas as pd
import streamlit as st

from fantasy_draft_ai.draft.pool import FrozenDraftPlayer
from fantasy_draft_ai.draft.roster import RosterPlayer, assign_roster
from fantasy_draft_ai.draft.state import DraftStateError
from fantasy_draft_ai.recommendations.models import (
    ProjectionPickCandidate,
    ProjectionRecommendationResult,
)
from fantasy_draft_ai.recommendations.projection_baseline import (
    ProjectionRankingRow,
    build_projection_rankings,
    rank_best_available,
)
from fantasy_draft_ai.services.draft_auto_pick import simulate_opponents_to_user_turn
from fantasy_draft_ai.services.draft_room import (
    DraftRoomSession,
    create_draft_session,
    load_draft_session,
    record_draft_pick,
    undo_draft_pick,
)
from fantasy_draft_ai.ui.common import (
    position_cell_style,
    position_option_label,
    render_page_header,
    render_position_badge,
    render_section_header,
)
from fantasy_draft_ai.ui.context import AppContext, load_app_context
from fantasy_draft_ai.ui.redraft_presets import (
    DEFAULT_REDRAFT_PRESET_KEY,
    REDRAFT_ROSTER_PRESETS,
    redraft_preset,
    rules_for_redraft_preset,
)

_DRAFT_ERRORS = (OSError, KeyError, TypeError, ValueError, DraftStateError)
_QUICK_TEAM_COUNTS = (8, 10, 12, 14, 16)
_ROSTER_PRESET_KEYS = tuple(preset.key for preset in REDRAFT_ROSTER_PRESETS)
_EXTREME_RANK_GAP = 12


def _set_feedback(kind: str, message: str) -> None:
    st.session_state["assistant_feedback"] = (kind, message)


def _render_feedback() -> None:
    feedback = st.session_state.pop("assistant_feedback", None)
    if not isinstance(feedback, tuple) or len(feedback) != 2:
        return
    kind, message = feedback
    if kind == "success":
        st.toast(str(message), icon=":material/check_circle:")
    else:
        st.error(str(message))


def _team_display_name(team_id: str | None) -> str:
    """Turn internal team IDs into compact draft-room labels."""

    if team_id is None:
        return "Complete"
    suffix = team_id.removeprefix("team-")
    try:
        return f"Team {int(suffix)}"
    except ValueError:
        return team_id


def _load_sessions(context: AppContext) -> tuple[Any, ...]:
    try:
        return context.draft_repository.list_sessions()
    except _DRAFT_ERRORS as exc:
        st.error(f"Saved drafts could not be opened: {exc}")
        return ()


def _fallback_projection_count(players: Sequence[FrozenDraftPlayer]) -> int:
    return sum(
        "fallback_unvalidated" in player.prediction_status.strip().casefold()
        for player in players
    )


def _render_projection_confidence_warning(players: Sequence[FrozenDraftPlayer]) -> None:
    fallback_count = _fallback_projection_count(players)
    if fallback_count:
        projection_label = "projection" if fallback_count == 1 else "projections"
        use_verb = "uses" if fallback_count == 1 else "use"
        st.warning(
            f"{fallback_count:,} rookie {projection_label} {use_verb} an unvalidated point-only "
            "fallback. P10, P50, and P90 are identical, so risk is not estimated; treat "
            "those players as lower-confidence options."
        )


def _uses_unvalidated_fallback(
    session: DraftRoomSession,
    player_id: str,
) -> bool:
    return any(
        player.player_id == player_id
        and "fallback_unvalidated" in player.prediction_status.strip().casefold()
        for player in session.players
    )


def _quick_start(context: AppContext, *, expanded: bool) -> None:
    reference = context.reference_rules
    with st.expander("Start a new redraft", expanded=expanded, icon=":material/add_circle:"):
        st.write(
            "Use the published 2026 full-PPR projection board now. Team count and draft "
            "position adjust the advice. Choose the closest common roster preset; season and "
            "scoring stay locked to the compatible published projections."
        )
        with st.container(horizontal=True, vertical_alignment="bottom"):
            draft_name = st.text_input(
                "Draft name",
                value=f"My {reference.season} redraft",
                key="assistant_new_draft_name",
            )
            preset_key = st.selectbox(
                "Roster preset",
                _ROSTER_PRESET_KEYS,
                index=_ROSTER_PRESET_KEYS.index(DEFAULT_REDRAFT_PRESET_KEY),
                format_func=lambda value: redraft_preset(str(value)).label,
                key="assistant_roster_preset",
            )
        with st.container(horizontal=True, vertical_alignment="bottom"):
            team_count = int(
                st.selectbox(
                    "League size",
                    _QUICK_TEAM_COUNTS,
                    index=_QUICK_TEAM_COUNTS.index(reference.teams),
                    format_func=lambda value: f"{value} teams",
                    key="assistant_team_count",
                )
            )
            draft_slot = int(
                st.number_input(
                    "Your draft position",
                    min_value=1,
                    max_value=team_count,
                    value=min(
                        int(st.session_state.get("assistant_draft_slot", 1)),
                        team_count,
                    ),
                    key="assistant_draft_slot",
                )
            )
        preset = redraft_preset(str(preset_key))
        rules = rules_for_redraft_preset(reference, team_count=team_count, preset=preset)
        preparation = context.prepare_draft(rules)
        st.caption(
            f"{reference.season} · {team_count}-team · Full PPR · Snake · "
            f"{rules.draft.rounds} rounds · {preset.summary}"
        )
        if not preparation.readiness.state_ready:
            st.error(preparation.readiness.state_message)
            return
        if st.button(
            "Start draft",
            type="primary",
            icon=":material/play_arrow:",
            key="assistant_start_draft",
        ):
            try:
                created = create_draft_session(
                    context.draft_repository,
                    preparation,
                    session_name=draft_name,
                    rules=rules,
                    user_draft_slot=draft_slot,
                    engine_config=context.engine_config,
                    random_seed=context.config.project.random_seed,
                    command_id=f"assistant-create-{uuid.uuid4().hex}",
                )
                st.session_state["assistant_draft_session"] = created.state.session_id
                _set_feedback("success", "Draft created. Track each pick as it happens.")
                st.rerun()
            except _DRAFT_ERRORS as exc:
                st.error(f"Draft could not be created: {exc}")


def _select_session(
    context: AppContext,
    sessions: tuple[Any, ...],
) -> DraftRoomSession | None:
    if not sessions:
        return None
    session_ids = [str(session.session_id) for session in sessions]
    selected = st.session_state.get("assistant_draft_session")
    selected_id = str(selected) if selected in session_ids else session_ids[0]
    if len(session_ids) > 1:
        selected_id = st.selectbox(
            "Open draft",
            session_ids,
            index=session_ids.index(selected_id),
            format_func=lambda value: next(
                f"{item.session_name} · {item.status.replace('_', ' ')}"
                for item in sessions
                if item.session_id == value
            ),
            key="assistant_session_selector",
        )
    st.session_state["assistant_draft_session"] = selected_id
    try:
        return load_draft_session(context.draft_repository, selected_id)
    except _DRAFT_ERRORS as exc:
        st.error(f"The selected draft could not be replayed: {exc}")
        return None


def _record_player(
    context: AppContext,
    session: DraftRoomSession,
    player_id: str,
    display_name: str,
) -> None:
    try:
        record_draft_pick(
            context.draft_repository,
            session.state.session_id,
            player_id,
            expected_version=session.state.version,
            command_id=f"assistant-pick-{uuid.uuid4().hex}",
        )
        st.session_state[f"assistant_search_{session.state.session_id}"] = ""
        _set_feedback("success", f"Recorded {display_name}.")
        st.rerun()
    except _DRAFT_ERRORS as exc:
        st.error(f"Pick could not be recorded: {exc}")


def _undo_latest(context: AppContext, session: DraftRoomSession) -> None:
    latest = session.state.picks[-1] if session.state.picks else None
    try:
        undo_draft_pick(
            context.draft_repository,
            session.state.session_id,
            expected_version=session.state.version,
            command_id=f"assistant-undo-{uuid.uuid4().hex}",
        )
        label = "latest pick" if latest is None else latest.player_name
        _set_feedback("success", f"Undid {label}.")
        st.rerun()
    except _DRAFT_ERRORS as exc:
        st.error(f"The latest pick could not be undone: {exc}")


def _simulate_to_user_turn(context: AppContext, session: DraftRoomSession) -> None:
    try:
        result = simulate_opponents_to_user_turn(
            context.draft_repository,
            session.state.session_id,
            expected_version=session.state.version,
            engine_config=context.engine_config,
            command_id=f"assistant-sim-{uuid.uuid4().hex}",
        )
        count = len(result.simulated_picks)
        if count == 0:
            message = "No opponent picks needed—your team is already on the clock."
        elif result.session.state.complete:
            message = f"Simulated {count} opponent picks and completed the draft."
        else:
            noun = "pick" if count == 1 else "picks"
            message = f"Simulated {count} opponent {noun}. You're on the clock."
        _set_feedback("success", message)
        st.rerun()
    except _DRAFT_ERRORS as exc:
        st.error(f"Opponent picks could not be simulated: {exc}")


def _picks_until_user_turn(session: DraftRoomSession) -> int:
    state = session.state
    current = state.current_overall_pick
    if current is None or state.is_user_turn:
        return 0
    next_user = state.next_user_pick()
    if next_user is None:
        return state.total_picks - current + 1
    return next_user - current


def _render_turn_bar(context: AppContext, session: DraftRoomSession) -> None:
    state = session.state
    round_number = (
        None
        if state.current_overall_pick is None
        else (state.current_overall_pick - 1) // state.rules.teams + 1
    )
    with st.container(border=True):
        with st.container(horizontal=True, vertical_alignment="center"):
            if state.complete:
                st.badge("Draft complete", icon=":material/check_circle:", color="green")
            elif state.is_user_turn:
                st.badge("Your pick", icon=":material/timer:", color="green")
            else:
                st.badge("Opponent pick", icon=":material/schedule:", color="blue")
            st.caption(
                f"{session.info.session_name} · {state.rules.teams}-team snake · "
                f"slot {state.user_draft_slot}"
            )
        with st.container(horizontal=True, vertical_alignment="center"):
            st.metric(
                "Overall pick",
                state.current_overall_pick or "Complete",
                icon=":material/tag:",
                border=True,
                width=150,
            )
            st.metric(
                "Round",
                round_number or "Complete",
                icon=":material/replay:",
                border=True,
                width=150,
            )
            st.metric(
                "On the clock",
                "You"
                if state.is_user_turn
                else _team_display_name(state.current_team_id),
                icon=":material/person:",
                border=True,
                width=150,
            )
            undo_clicked = st.button(
                "Undo last pick",
                icon=":material/undo:",
                disabled=not state.picks,
                width=150,
                key=f"assistant_undo_{state.session_id}_{state.version}",
            )
            picks_to_simulate = _picks_until_user_turn(session)
            sim_clicked = st.button(
                "Sim to my pick",
                icon=":material/fast_forward:",
                type="primary" if picks_to_simulate else "secondary",
                disabled=picks_to_simulate == 0,
                help=(
                    f"Auto-draft {picks_to_simulate} opponent "
                    f"{'pick' if picks_to_simulate == 1 else 'picks'} using projection value "
                    "and roster needs."
                    if picks_to_simulate
                    else (
                        "Make your pick first; simulation stops whenever your team is "
                        "on the clock."
                    )
                ),
                width=150,
                key=f"assistant_sim_{state.session_id}_{state.version}",
            )
        if undo_clicked:
            _undo_latest(context, session)
        if sim_clicked:
            _simulate_to_user_turn(context, session)


def _render_candidate_card(
    context: AppContext,
    session: DraftRoomSession,
    candidate: ProjectionPickCandidate,
    *,
    primary: bool,
) -> None:
    with st.container(border=True):
        if primary:
            st.badge(
                "Best pick now",
                icon=":material/auto_awesome:",
                color="green",
            )
        else:
            st.badge("Strong alternative", icon=":material/compare_arrows:", color="blue")
        st.subheader(candidate.display_name)
        with st.container(horizontal=True, vertical_alignment="center"):
            render_position_badge(
                candidate.position,
                f"{candidate.position}{candidate.position_rank}",
            )
            st.badge(f"Experimental model #{candidate.overall_rank}", color="gray")
            if candidate.current_adp is not None:
                st.badge(f"Consensus ADP {candidate.current_adp:.1f}", color="green")
            st.badge(f"Tier {candidate.tier}", color="violet")
            if _uses_unvalidated_fallback(session, candidate.player_id):
                st.badge(
                    "Lower-confidence rookie estimate",
                    icon=":material/warning:",
                    color="orange",
                )
        if _uses_unvalidated_fallback(session, candidate.player_id):
            st.caption(
                "Point estimate only; downside, upside, and risk are not estimated for "
                "this player."
            )
        if st.button(
            f"Draft {candidate.display_name}",
            type="primary" if primary else "secondary",
            icon=":material/add:",
            width="stretch",
            key=(
                f"assistant_candidate_{session.state.session_id}_"
                f"{session.state.version}_{candidate.player_id}"
            ),
        ):
            _record_player(context, session, candidate.player_id, candidate.display_name)
        with st.container(horizontal=True):
            st.metric(
                "17-game projection",
                f"{candidate.p50:.1f}",
                icon=":material/query_stats:",
                border=True,
                width=150,
            )
            st.metric(
                "Value over replacement",
                f"+{candidate.p50_vorp:.1f}",
                icon=":material/trending_up:",
                border=True,
                width=150,
            )
            st.metric(
                "Floor — ceiling",
                f"{candidate.p10:.0f} — {candidate.p90:.0f}",
                icon=":material/height:",
                border=True,
                width=150,
            )
        if primary:
            st.markdown("**Why this recommendation is competitive**")
            for reason in candidate.reasons[:3]:
                st.markdown(f"- :material/check_circle: {reason}")
        else:
            st.caption(candidate.reasons[0])
        if candidate.probability_available_next_pick is None:
            st.caption("Next-pick market timing is not available yet.")
        else:
            st.caption(
                f"Chance available at your next pick: "
                f"{candidate.probability_available_next_pick:.0%}"
            )


def _render_recommendations(
    context: AppContext,
    session: DraftRoomSession,
    advice: ProjectionRecommendationResult,
) -> None:
    state = session.state
    if state.complete:
        st.success(
            "Draft complete. Open Draft report to review your roster.",
            icon=":material/check_circle:",
        )
        return
    if not state.is_user_turn:
        with st.container(border=True):
            st.badge("Waiting for your turn", icon=":material/schedule:", color="blue")
            st.subheader(f"{_team_display_name(state.current_team_id)} is on the clock")
            st.caption(
                "Record the selected player below. Your recommendation returns at "
                f"pick {state.next_user_pick()}."
            )
        return
    if not advice.available or not advice.candidates:
        st.warning(advice.message)
        return
    top = advice.candidates[0]
    if len(advice.candidates) > 1:
        gap = top.decision_score - advice.candidates[1].decision_score
        if gap < 5:
            st.info(
                "This is a close decision. Compare the alternatives before making the pick.",
                icon=":material/balance:",
            )
    _render_candidate_card(context, session, top, primary=True)
    alternatives = advice.candidates[1:4]
    if alternatives:
        render_section_header(
            "Other strong choices",
            "Use these when roster construction or personal preference breaks a close tie.",
            icon=":material/compare_arrows:",
        )
        for candidate in alternatives:
            _render_candidate_card(context, session, candidate, primary=False)
    st.caption(
        "Check current injury, suspension, and depth-chart news before drafting; those live "
        "updates are not yet included in the model."
    )


def _roster_records(session: DraftRoomSession) -> list[dict[str, Any]]:
    state = session.state
    roster = state.roster(state.user_draft_slot)
    assignment = assign_roster(
        [RosterPlayer(pick.player_id, pick.position, pick.projected_points) for pick in roster],
        state.rules,
    )
    return [
        {
            "Pick": pick.overall_pick,
            "Player": pick.player_name,
            "Pos": pick.position,
            "Slot": assignment.slot_for_player(pick.player_id),
            "Projection": pick.projected_points,
        }
        for pick in roster
    ]


def _render_roster(session: DraftRoomSession) -> None:
    with st.container(border=True):
        render_section_header(
            "My roster",
            f"Draft slot {session.state.user_draft_slot}",
            icon=":material/groups:",
        )
        records = _roster_records(session)
        counts = Counter(record["Pos"] for record in records)
        with st.container(horizontal=True):
            for position in ("QB", "RB", "WR", "TE"):
                render_position_badge(position, f"{position} {counts[position]}")
        if not records:
            st.caption("Your drafted players will appear here as you build the roster.")
            return
        roster_frame = pd.DataFrame.from_records(records)
        styled_roster = roster_frame.style.map(position_cell_style, subset=["Pos"])
        st.dataframe(
            styled_roster,
            hide_index=True,
            width="stretch",
            row_height=38,
            column_config={
                "Player": st.column_config.TextColumn(pinned=True, width="medium"),
                "Projection": st.column_config.NumberColumn(format="%.1f"),
            },
        )


def _record_table_pick(
    context: AppContext,
    session_id: str,
    session_version: int,
    filtered: tuple[ProjectionRankingRow, ...],
    click_key: str,
    search_key: str,
) -> None:
    """Record a ButtonColumn selection against the exact rendered session version."""

    click = st.session_state.get(click_key)
    if click is None:
        return
    row_value = click.get("row")
    if not isinstance(row_value, int) or isinstance(row_value, bool):
        _set_feedback("error", "The selected player row is invalid.")
        return
    if not 0 <= row_value < len(filtered):
        _set_feedback("error", "The selected player row is no longer available.")
        return
    player = filtered[row_value]
    try:
        record_draft_pick(
            context.draft_repository,
            session_id,
            player.player_id,
            expected_version=session_version,
            command_id=f"assistant-table-pick-{uuid.uuid4().hex}",
        )
        st.session_state[search_key] = ""
        _set_feedback("success", f"Recorded {player.display_name}.")
    except _DRAFT_ERRORS as exc:
        _set_feedback("error", f"Pick could not be recorded: {exc}")


def _render_available_players(context: AppContext, session: DraftRoomSession) -> None:
    state = session.state
    if state.complete:
        st.caption("All draft selections are complete; no additional player can be recorded.")
        return
    model_rankings = build_projection_rankings(state.rules, session.players)
    consensus_rankings = _consensus_rankings(model_rankings)
    rankings = tuple(
        sorted(
            model_rankings,
            key=lambda row: _consensus_sort_key(row, consensus_rankings),
        )
    )
    available = [row for row in rankings if row.player_id not in state.selected_player_ids]
    render_section_header(
        "Available players",
        "FantasyPros consensus controls the default order; the health-neutral model is a "
        "secondary comparison.",
        icon=":material/format_list_numbered:",
    )
    owner = "your roster" if state.is_user_turn else state.current_team_id
    owner_label = "your roster" if state.is_user_turn else _team_display_name(owner)
    st.badge(
        f"Pick {state.current_overall_pick} · {owner_label}",
        icon=":material/touch_app:",
        color="green" if state.is_user_turn else "blue",
    )
    search_key = f"assistant_search_{state.session_id}"
    positions = sorted({row.position for row in available})
    with st.container(border=True):
        search = st.text_input(
            "Search players",
            placeholder="Type a player name",
            key=search_key,
            icon=":material/search:",
        )
        selected_position_value = st.pills(
            "Positions",
            positions,
            selection_mode="multi",
            default=positions,
            format_func=position_option_label,
            key=f"assistant_positions_{state.session_id}",
            width="stretch",
        )
    selected_positions = list(selected_position_value or ())
    normalized_search = search.strip().casefold()
    filtered = [
        row
        for row in available
        if row.position in selected_positions
        and normalized_search in row.display_name.casefold()
    ][:250]
    action_label = "Record my pick" if state.is_user_turn else "Record taken"
    records = [
        {
            "Action": action_label,
            "Consensus rank": consensus_rankings.get(row.player_id),
            "Player": row.display_name,
            "Pos": row.position,
            "Pos rank": row.position_rank,
            "Experimental model rank": row.overall_rank,
            "Model vs market": _rank_delta(
                consensus_rankings.get(row.player_id),
                row.overall_rank,
            ),
            "ADP": row.average_pick,
            "17-game projection": row.p50,
            "VORP": row.p50_vorp,
        }
        for row in filtered
    ]
    click_key = f"assistant_table_click_{state.session_id}_{state.version}"
    if records:
        player_frame = pd.DataFrame.from_records(records)
        styled_players = player_frame.style.map(position_cell_style, subset=["Pos"])
        st.dataframe(
            styled_players,
            hide_index=True,
            width="stretch",
            height=520,
            row_height=40,
            column_config={
                "Action": st.column_config.ButtonColumn(
                    "Record selection",
                    type="secondary",
                    pinned=True,
                    width="medium",
                    on_click=_record_table_pick,
                    args=(
                        context,
                        state.session_id,
                        state.version,
                        tuple(filtered),
                        click_key,
                        search_key,
                    ),
                    key=click_key,
                ),
                "Consensus rank": st.column_config.NumberColumn(
                    format="#%d",
                    pinned=True,
                    width="small",
                    help="Primary board rank derived from the FantasyPros composite ADP.",
                ),
                "Player": st.column_config.TextColumn(pinned=True, width="medium"),
                "Pos": st.column_config.TextColumn(width="small"),
                "Pos rank": st.column_config.NumberColumn(format="#%d", width="small"),
                "Experimental model rank": st.column_config.NumberColumn(
                    format="#%d",
                    width="small",
                ),
                "Model vs market": st.column_config.NumberColumn(
                    format="%+d",
                    width="small",
                    help="Positive means the health-neutral model ranks the player higher.",
                ),
                "ADP": st.column_config.NumberColumn(format="%.1f"),
                "17-game projection": st.column_config.NumberColumn(format="%.1f"),
                "VORP": st.column_config.NumberColumn(
                    "VORP",
                    format="%+.1f",
                    help="Projected points above the league-specific replacement player.",
                ),
            },
        )
    else:
        st.info("No available player matches those filters.", icon=":material/search_off:")
    extreme_count = sum(
        abs(delta) >= _EXTREME_RANK_GAP
        for row in filtered
        if (
            delta := _rank_delta(
                consensus_rankings.get(row.player_id),
                row.overall_rank,
            )
        )
        is not None
    )
    if extreme_count:
        st.warning(
            f"{extreme_count:,} shown players have a market/model gap of at least "
            f"{_EXTREME_RANK_GAP} ranks. Treat the model as a review flag, not permission "
            "to ignore consensus.",
            icon=":material/warning:",
        )
    st.caption(
        f"Showing {len(filtered):,} of {len(available):,} remaining players. The live board "
        "shows at most 250 matches, assumes 17 healthy games for every player, and uses your "
        "league size and roster demand."
    )


def _consensus_rankings(rows: Sequence[ProjectionRankingRow]) -> dict[str, int]:
    """Create deterministic competition ranks from reviewed consensus ADP."""

    usable = sorted(
        (
            row
            for row in rows
            if row.average_pick is not None
            and isfinite(row.average_pick)
            and row.average_pick > 0
        ),
        key=lambda row: (
            row.average_pick if row.average_pick is not None else float("inf"),
            row.display_name.casefold(),
            row.player_id,
        ),
    )
    output: dict[str, int] = {}
    prior_pick: float | None = None
    prior_rank = 0
    for ordinal, row in enumerate(usable, start=1):
        if row.average_pick is None:
            continue
        if prior_pick is None or row.average_pick != prior_pick:
            prior_pick = row.average_pick
            prior_rank = ordinal
        output[row.player_id] = prior_rank
    return output


def _consensus_sort_key(
    row: ProjectionRankingRow,
    consensus_rankings: dict[str, int],
) -> tuple[int, int, int, str]:
    consensus_rank = consensus_rankings.get(row.player_id)
    return (
        1 if consensus_rank is None else 0,
        consensus_rank if consensus_rank is not None else 10**9,
        row.overall_rank,
        row.player_id,
    )


def _rank_delta(consensus_rank: int | None, model_rank: int) -> int | None:
    return None if consensus_rank is None else consensus_rank - model_rank


def _draft_board_frames(session: DraftRoomSession) -> tuple[pd.DataFrame, pd.DataFrame, str]:
    """Build a round-by-slot snake board and its position styling metadata."""

    state = session.state
    slot_labels = [
        f"You · {slot}" if slot == state.user_draft_slot else f"T{slot}"
        for slot in range(1, state.rules.teams + 1)
    ]
    user_column = slot_labels[state.user_draft_slot - 1]
    rows: list[dict[str, Any]] = []
    positions: list[dict[str, Any]] = []
    picks_by_location = {(pick.round, pick.draft_slot): pick for pick in state.picks}
    current_round = (
        None
        if state.current_overall_pick is None
        else (state.current_overall_pick - 1) // state.rules.teams + 1
    )
    for round_number in range(1, state.rules.draft.rounds + 1):
        row: dict[str, Any] = {"Round": round_number}
        position_row: dict[str, Any] = {"Round": ""}
        for slot, column in enumerate(slot_labels, start=1):
            pick = picks_by_location.get((round_number, slot))
            if pick is not None:
                row[column] = f"{pick.overall_pick:02d} · {pick.player_name} · {pick.position}"
                position_row[column] = pick.position
            elif round_number == current_round and slot == state.current_draft_slot:
                row[column] = "YOUR PICK" if state.is_user_turn else "ON THE CLOCK"
                position_row[column] = "CURRENT_USER" if state.is_user_turn else "CURRENT"
            else:
                row[column] = ""
                position_row[column] = ""
        rows.append(row)
        positions.append(position_row)
    return (
        pd.DataFrame.from_records(rows),
        pd.DataFrame.from_records(positions),
        user_column,
    )


def _style_draft_board(
    board: pd.DataFrame,
    positions: pd.DataFrame,
    user_column: str,
) -> Any:
    """Apply stable position and user-column colors without changing board values."""

    def board_styles(_: pd.DataFrame) -> pd.DataFrame:
        styles = pd.DataFrame("", index=board.index, columns=board.columns)
        for row_index in board.index:
            for column in board.columns:
                marker = str(positions.at[row_index, column])
                if marker == "CURRENT_USER":
                    style = "background-color: #14532D; color: #F8FAFC; font-weight: 800;"
                elif column == user_column:
                    style = "background-color: #713F12; color: #F8FAFC; font-weight: 800;"
                elif marker == "CURRENT":
                    style = "background-color: #1E3A8A; color: #F8FAFC; font-weight: 800;"
                else:
                    style = position_cell_style(marker)
                styles.at[row_index, column] = style
        return styles

    return board.style.apply(board_styles, axis=None)


def _render_history(session: DraftRoomSession) -> None:
    state = session.state
    render_section_header(
        "Draft activity",
        "Follow the snake board by team or switch to the chronological pick log.",
        icon=":material/grid_view:",
    )
    with st.container(border=True):
        view = st.segmented_control(
            "Draft activity view",
            ("Draft board", "Pick log"),
            default="Draft board",
            required=True,
            label_visibility="collapsed",
            key=f"assistant_activity_view_{state.session_id}",
        )
        if view == "Draft board":
            board, positions, user_column = _draft_board_frames(session)
            board_config: dict[str, Any] = {
                "Round": st.column_config.NumberColumn(
                    "Round",
                    format="%d",
                    pinned=True,
                    width="small",
                )
            }
            for column in board.columns:
                if column != "Round":
                    board_config[column] = st.column_config.TextColumn(
                        column,
                        pinned=column == user_column,
                        width="medium",
                    )
            st.dataframe(
                _style_draft_board(board, positions, user_column),
                hide_index=True,
                width="stretch",
                height=min(620, 46 * (len(board) + 1)),
                row_height=44,
                column_config=board_config,
            )
            with st.container(horizontal=True):
                for position in ("QB", "RB", "WR", "TE"):
                    render_position_badge(position)
                st.badge("Your team column", color="yellow")
            return
        if not state.picks:
            st.caption("No picks have been recorded.")
            return
        pick_log = pd.DataFrame.from_records(
            [
                {
                    "Overall": pick.overall_pick,
                    "Round": pick.round,
                    "Team": "You"
                    if pick.draft_slot == state.user_draft_slot
                    else _team_display_name(pick.team_id),
                    "Player": pick.player_name,
                    "Pos": pick.position,
                }
                for pick in reversed(state.picks)
            ]
        )
        st.dataframe(
            pick_log.style.map(position_cell_style, subset=["Pos"]),
            hide_index=True,
            width="stretch",
            row_height=38,
            column_config={
                "Overall": st.column_config.NumberColumn(format="#%d"),
                "Player": st.column_config.TextColumn(pinned=True, width="medium"),
            },
        )


def _render_method_details(
    session: DraftRoomSession,
    advice: ProjectionRecommendationResult,
) -> None:
    with st.expander("Projection and recommendation notes", icon=":material/info:"):
        _render_projection_confidence_warning(session.players)
        st.write(
            "The assistant starts with the model's season projection, compares each player "
            "with the replacement option at that position, then adds current roster fit and "
            "the drop to the next available player at the same position."
        )
        if session.info.recommendation_status == "recommendation_ready":
            st.success("Reviewed market timing is available for the enhanced simulation.")
        else:
            st.caption(
                "ADP-based market timing is still unavailable. It is optional here, so the "
                "projection recommendation continues to work without inventing a probability."
            )
        for limitation in advice.limitations:
            st.write(f"- {limitation}")


def render() -> None:
    """Render the app's primary quick-start and live redraft experience."""

    context = load_app_context()
    sessions = _load_sessions(context)
    if sessions:
        with st.container(horizontal=True, vertical_alignment="center"):
            st.title("Draft Assistant", width="content")
            st.badge("Live redraft", icon=":material/sports_football:", color="green")
        st.caption("Track the room, see the best available value, and make the next pick.")
    else:
        render_page_header(
            "Draft Assistant",
            "Your next pick, made simpler",
            "Track every selection and get a fresh best-available recommendation when your "
            "team is on the clock.",
        )
    _render_feedback()
    if not sessions:
        _quick_start(context, expanded=True)
    session = _select_session(context, sessions)
    if session is None:
        if sessions:
            _quick_start(context, expanded=True)
            st.info(
                "Choose a saved draft above, or start a new one. The assistant will "
                "immediately rank the best players."
            )
        else:
            st.info(
                "Start a draft above. The assistant will immediately rank the best players."
            )
        return

    _render_turn_bar(context, session)
    state = session.state
    advice = rank_best_available(
        state,
        session.players,
        context.engine_config,
        context.guidance_config,
        limit=8,
    )
    if state.is_user_turn:
        with st.container(horizontal=True, vertical_alignment="top", gap="large"):
            with st.container(width=700):
                _render_recommendations(context, session, advice)
            with st.container(width=340):
                _render_roster(session)
        st.space("small")
        _render_available_players(context, session)
    elif state.complete:
        _render_recommendations(context, session, advice)
        _render_roster(session)
    else:
        _render_available_players(context, session)
        st.space("small")
        _render_roster(session)
    st.space("small")
    _render_history(session)
    _render_method_details(session, advice)
    _quick_start(context, expanded=False)
