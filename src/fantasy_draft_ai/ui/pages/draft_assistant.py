"""Recommendation-first redraft workflow for human draft-day use."""

from __future__ import annotations

import uuid
from collections.abc import Sequence
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
from fantasy_draft_ai.services.draft_room import (
    DraftRoomSession,
    create_draft_session,
    load_draft_session,
    record_draft_pick,
    undo_draft_pick,
)
from fantasy_draft_ai.ui.common import render_page_header
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


def _set_feedback(kind: str, message: str) -> None:
    st.session_state["assistant_feedback"] = (kind, message)


def _render_feedback() -> None:
    feedback = st.session_state.pop("assistant_feedback", None)
    if not isinstance(feedback, tuple) or len(feedback) != 2:
        return
    kind, message = feedback
    if kind == "success":
        st.success(str(message))
    else:
        st.error(str(message))


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
                f"{item.session_name} · {item.current_version} picks/events · {item.status}"
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


def _render_turn_bar(context: AppContext, session: DraftRoomSession) -> None:
    state = session.state
    round_number = (
        None
        if state.current_overall_pick is None
        else (state.current_overall_pick - 1) // state.rules.teams + 1
    )
    metric_one, metric_two, metric_three, action = st.columns([1, 1, 1.4, 1.1])
    metric_one.metric("Pick", state.current_overall_pick or "Complete")
    metric_two.metric("Round", round_number or "Complete")
    if state.complete:
        metric_three.metric("Status", "Draft complete")
    elif state.is_user_turn:
        metric_three.metric("On the clock", "You")
    else:
        metric_three.metric("On the clock", state.current_team_id or "Complete")
    if action.button(
        "Undo last pick",
        icon=":material/undo:",
        disabled=not state.picks,
        width="stretch",
        key=f"assistant_undo_{state.session_id}_{state.version}",
    ):
        _undo_latest(context, session)


def _render_candidate_card(
    context: AppContext,
    session: DraftRoomSession,
    candidate: ProjectionPickCandidate,
    *,
    primary: bool,
) -> None:
    with st.container(border=True):
        label = "Best pick now" if primary else "Alternative"
        st.caption(label.upper())
        st.subheader(f"{candidate.display_name} · {candidate.position}{candidate.position_rank}")
        with st.container(horizontal=True):
            st.metric("Projected points", f"{candidate.p50:.1f}")
            st.metric("Value over replacement", f"+{candidate.p50_vorp:.1f}")
            st.metric("Overall rank", f"#{candidate.overall_rank}")
        if primary:
            for reason in candidate.reasons[:3]:
                st.write(f"- {reason}")
        else:
            st.caption(candidate.reasons[0])
        if candidate.probability_available_next_pick is None:
            st.caption("Next-pick market timing is not available yet.")
        else:
            st.caption(
                f"Chance available at your next pick: "
                f"{candidate.probability_available_next_pick:.0%}"
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


def _render_recommendations(
    context: AppContext,
    session: DraftRoomSession,
    advice: ProjectionRecommendationResult,
) -> None:
    state = session.state
    if state.complete:
        st.success("Draft complete. Open Draft report to review your roster.")
        return
    if not state.is_user_turn:
        st.info(
            f"{state.current_team_id} is picking now. Record that selection below; your "
            f"recommendation will appear at pick {state.next_user_pick()}."
        )
        return
    if not advice.available or not advice.candidates:
        st.warning(advice.message)
        return
    top = advice.candidates[0]
    if len(advice.candidates) > 1:
        gap = top.decision_score - advice.candidates[1].decision_score
        if gap < 5:
            st.info("This is a close decision. Compare the alternatives before making the pick.")
    _render_candidate_card(context, session, top, primary=True)
    alternatives = advice.candidates[1:4]
    if alternatives:
        st.subheader("Other strong choices")
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
    st.subheader("My roster")
    records = _roster_records(session)
    if not records:
        st.caption("Your drafted players will appear here.")
        return
    st.dataframe(
        records,
        hide_index=True,
        width="stretch",
        column_config={"Projection": st.column_config.NumberColumn(format="%.1f")},
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
    rankings = build_projection_rankings(state.rules, session.players)
    available = [row for row in rankings if row.player_id not in state.selected_player_ids]
    st.subheader("Available players")
    owner = "your roster" if state.is_user_turn else state.current_team_id
    st.caption(f"Recording pick {state.current_overall_pick} for {owner}.")
    search_col, position_col = st.columns([2, 1])
    search_key = f"assistant_search_{state.session_id}"
    search = search_col.text_input(
        "Search",
        placeholder="Type a player name",
        key=search_key,
    )
    positions = sorted({row.position for row in available})
    selected_positions = position_col.multiselect(
        "Position",
        positions,
        default=positions,
        key=f"assistant_positions_{state.session_id}",
    )
    normalized_search = search.strip().casefold()
    filtered = [
        row
        for row in available
        if row.position in selected_positions
        and normalized_search in row.display_name.casefold()
    ][:250]
    action_label = (
        ":material/add: Record my pick"
        if state.is_user_turn
        else ":material/check: Record taken"
    )
    records = [
        {
            "Action": action_label,
            "Rank": row.overall_rank,
            "Player": row.display_name,
            "Pos": row.position,
            "Pos rank": row.position_rank,
            "Tier": row.tier,
            "Projection": row.p50,
            "Value": row.p50_vorp,
            "Floor": row.p10,
            "Ceiling": row.p90,
            "ADP": row.average_pick if row.average_pick is not None else float("nan"),
            "Risk": row.risk.title(),
        }
        for row in filtered
    ]
    click_key = f"assistant_table_click_{state.session_id}_{state.version}"
    if records:
        st.dataframe(
            pd.DataFrame.from_records(records),
            hide_index=True,
            width="stretch",
            height=560,
            column_config={
                "Action": st.column_config.ButtonColumn(
                    "Record selection",
                    type="secondary",
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
                "Rank": st.column_config.NumberColumn(format="#%d"),
                "Projection": st.column_config.NumberColumn(format="%.1f"),
                "Value": st.column_config.NumberColumn(
                    "Value over replacement",
                    format="%+.1f",
                    help="Projected points above the league-specific replacement player.",
                ),
                "Floor": st.column_config.NumberColumn(format="%.1f"),
                "Ceiling": st.column_config.NumberColumn(format="%.1f"),
                "ADP": st.column_config.NumberColumn(format="%.1f"),
            },
        )
    else:
        st.info("No available player matches those filters.")
    st.caption(
        f"{len(available):,} players remain. Rankings use your league size and roster demand."
    )


def _render_history(session: DraftRoomSession) -> None:
    state = session.state
    with st.expander("Draft board and history", icon=":material/history:"):
        if not state.picks:
            st.caption("No picks have been recorded.")
            return
        st.dataframe(
            [
                {
                    "Overall": pick.overall_pick,
                    "Round": pick.round,
                    "Team": "You" if pick.draft_slot == state.user_draft_slot else pick.team_id,
                    "Player": pick.player_name,
                    "Pos": pick.position,
                }
                for pick in reversed(state.picks)
            ],
            hide_index=True,
            width="stretch",
        )


def _render_method_details(
    session: DraftRoomSession,
    advice: ProjectionRecommendationResult,
) -> None:
    with st.expander("How the recommendation works", icon=":material/info:"):
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
    render_page_header(
        "Draft Assistant",
        "Your next pick, made simpler",
        "Track every selection and get a fresh best-available recommendation when your team "
        "is on the clock.",
    )
    _render_feedback()
    sessions = _load_sessions(context)
    _quick_start(context, expanded=not sessions)
    session = _select_session(context, sessions)
    if session is None:
        st.info("Start a draft above. The assistant will immediately rank the best players.")
        return

    _render_turn_bar(context, session)
    state = session.state
    _render_projection_confidence_warning(session.players)
    advice = rank_best_available(
        state,
        session.players,
        context.engine_config,
        context.guidance_config,
        limit=8,
    )
    main, roster = st.columns([2.4, 1], gap="large")
    with main:
        _render_recommendations(context, session, advice)
    with roster:
        _render_roster(session)

    st.divider()
    _render_available_players(context, session)
    _render_history(session)
    _render_method_details(session, advice)
