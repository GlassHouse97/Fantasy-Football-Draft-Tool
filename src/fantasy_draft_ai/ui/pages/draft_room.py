"""Interactive event-sourced Draft Room page."""

from __future__ import annotations

import uuid
from typing import Any

import pandas as pd
import streamlit as st

from fantasy_draft_ai.draft.roster import RosterPlayer, assign_roster
from fantasy_draft_ai.draft.state import DraftStateError
from fantasy_draft_ai.recommendations.engine import recommend_for_session
from fantasy_draft_ai.recommendations.models import RecommendationResult
from fantasy_draft_ai.services.draft_board import DraftBoardRow, build_draft_board
from fantasy_draft_ai.services.draft_room import (
    DraftRoomSession,
    create_draft_session,
    load_draft_session,
    record_draft_pick,
    replace_draft_pick,
    undo_draft_pick,
)
from fantasy_draft_ai.services.league_setup import LeagueSetupRecord
from fantasy_draft_ai.ui.common import (
    render_lineage,
    render_method_legend,
    render_page_header,
    selected_league_setup,
)
from fantasy_draft_ai.ui.context import AppContext, load_app_context

_DRAFT_ERRORS = (OSError, KeyError, TypeError, ValueError, DraftStateError)


def _session_selector(context: AppContext) -> DraftRoomSession | None:
    try:
        sessions = context.draft_repository.list_sessions()
    except _DRAFT_ERRORS as exc:
        st.error(f"Draft persistence could not be opened: {exc}")
        return None
    if not sessions:
        st.info("No draft session exists yet. Create one above to freeze this ruleset and board.")
        return None
    session_ids = [session.session_id for session in sessions]
    selected_value = st.session_state.get("selected_draft_session")
    selected_id = selected_value if isinstance(selected_value, str) else None
    selected_id = st.selectbox(
        "Open draft session",
        session_ids,
        index=session_ids.index(selected_id) if selected_id in session_ids else 0,
        format_func=lambda value: next(
            f"{item.session_name} - v{item.current_version} - {item.status}"
            for item in sessions
            if item.session_id == value
        ),
        key="draft_session_selector",
    )
    st.session_state["selected_draft_session"] = selected_id
    try:
        return load_draft_session(context.draft_repository, selected_id)
    except _DRAFT_ERRORS as exc:
        st.error(f"Session replay failed: {exc}")
        return None


def _render_create_session(
    context: AppContext,
    setup: LeagueSetupRecord,
) -> None:
    preparation = context.prepare_draft(setup.rules)
    try:
        existing_sessions = context.draft_repository.list_sessions()
    except _DRAFT_ERRORS:
        existing_sessions = ()
    with st.expander("Create a new frozen session", expanded=not existing_sessions):
        st.info(preparation.readiness.state_message)
        if preparation.readiness.recommendation_ready:
            st.success(preparation.readiness.recommendation_message)
        else:
            st.warning(f"Recommendation gate: {preparation.readiness.recommendation_message}")
        one, two, three = st.columns(3)
        session_name = one.text_input(
            "Session name",
            value=f"My {setup.rules.season} draft",
            key="new_draft_session_name",
        )
        draft_slot = int(
            two.number_input(
                "Draft slot",
                1,
                setup.rules.teams,
                min(setup.draft_slot, setup.rules.teams),
                key="new_draft_slot",
            )
        )
        simulations = int(
            three.number_input(
                "Simulation paths",
                16,
                context.engine_config.maximum_simulations,
                context.engine_config.default_simulations,
                16,
                key="new_draft_simulations",
            )
        )
        st.caption(
            f"{setup.fingerprint_label}; recommendation coverage "
            f"{preparation.readiness.market_coverage:.1%} / "
            f"{preparation.readiness.required_market_coverage:.1%} required."
        )
        if st.button(
            "Create draft session",
            type="primary",
            disabled=not preparation.readiness.state_ready,
        ):
            try:
                created = create_draft_session(
                    context.draft_repository,
                    preparation,
                    session_name=session_name,
                    rules=setup.rules,
                    user_draft_slot=draft_slot,
                    engine_config=context.engine_config,
                    random_seed=context.config.project.random_seed,
                    simulation_count=simulations,
                    command_id=f"streamlit-create-{uuid.uuid4().hex}",
                )
                st.session_state["selected_draft_session"] = created.state.session_id
                st.rerun()
            except _DRAFT_ERRORS as exc:
                st.error(f"Session creation failed: {exc}")


def _filtered_board(rows: tuple[DraftBoardRow, ...]) -> list[DraftBoardRow]:
    available = [row for row in rows if row.available]
    positions = sorted({row.position for row in available})
    tiers = sorted({row.tier for row in available})
    risks = ["low", "medium", "high", "not_estimated"]
    filter_one, filter_two, filter_three = st.columns([2, 1, 1])
    search = filter_one.text_input("Search available players", key="draft_board_search")
    selected_positions = filter_two.multiselect(
        "Position",
        positions,
        default=positions,
        key="draft_board_positions",
    )
    selected_tiers = filter_three.multiselect(
        "Tier",
        tiers,
        default=tiers,
        key="draft_board_tiers",
    )
    filter_four, filter_five = st.columns(2)
    selected_risks = filter_four.multiselect(
        "Projection risk",
        risks,
        default=risks,
        key="draft_board_risks",
    )
    adp_limit = float(
        filter_five.number_input(
            "Latest ADP at or before",
            min_value=1.0,
            max_value=500.0,
            value=500.0,
            help="Rows without reviewed ADP stay visible so missing evidence is explicit.",
        )
    )
    normalized_search = search.strip().casefold()
    return [
        row
        for row in available
        if row.position in selected_positions
        and row.tier in selected_tiers
        and row.risk in selected_risks
        and (row.average_pick is None or row.average_pick <= adp_limit)
        and normalized_search in row.display_name.casefold()
    ]


def _render_board(session: DraftRoomSession) -> list[DraftBoardRow]:
    rows = build_draft_board(session.state, session.players)
    filtered = _filtered_board(rows)
    st.dataframe(
        pd.DataFrame.from_records(
            {
                "Rank": row.overall_rank,
                "Player": row.display_name,
                "Pos": row.position,
                "Pos rank": row.position_rank,
                "Tier": row.tier,
                "Risk": row.risk.replace("_", " ").title(),
                "Method": row.method_kind.replace("_", " ").title(),
                "P10": row.p10,
                "P50": row.p50,
                "P90": row.p90,
                "ADP": row.average_pick,
                "ADP value": row.adp_value_at_current_pick,
                "Likely gone": row.probability_gone_before_user_pick,
                "Mapping": row.mapping_confidence or "Missing",
            }
            for row in filtered[:200]
        ),
        hide_index=True,
        width="stretch",
        column_config={
            "P10": st.column_config.NumberColumn(format="%.1f"),
            "P50": st.column_config.NumberColumn(format="%.1f"),
            "P90": st.column_config.NumberColumn(format="%.1f"),
            "ADP": st.column_config.NumberColumn(format="%.1f"),
            "ADP value": st.column_config.NumberColumn(format="%+.1f"),
            "Likely gone": st.column_config.ProgressColumn(
                min_value=0.0,
                max_value=1.0,
                format="percent",
            ),
        },
    )
    st.caption(
        f"{sum(row.available for row in rows):,} players remain; "
        f"showing {min(len(filtered), 200):,} filtered rows. "
        "Tiers are transparent position-rank bands, not learned clusters."
    )
    return filtered


def _render_pick_actions(
    context: AppContext,
    session: DraftRoomSession,
    filtered: list[DraftBoardRow],
) -> None:
    state = session.state
    if state.current_overall_pick is not None and filtered:
        options = {row.player_id: row for row in filtered}
        selected_player = st.selectbox(
            "Record player at the current pick",
            list(options),
            format_func=lambda value: (
                f"{options[value].display_name} ({options[value].position}) - "
                f"P50 {options[value].p50:.1f}"
            ),
            key="draft_pick_player",
        )
        if st.button("Record pick", type="primary"):
            try:
                record_draft_pick(
                    context.draft_repository,
                    state.session_id,
                    selected_player,
                    expected_version=state.version,
                    command_id=f"streamlit-pick-{uuid.uuid4().hex}",
                )
                st.rerun()
            except _DRAFT_ERRORS as exc:
                st.error(f"Pick failed: {exc}")
    action_one, action_two = st.columns(2)
    if action_one.button("Undo latest pick", disabled=not state.picks, width="stretch"):
        try:
            undo_draft_pick(
                context.draft_repository,
                state.session_id,
                expected_version=state.version,
                command_id=f"streamlit-undo-{uuid.uuid4().hex}",
            )
            st.rerun()
        except _DRAFT_ERRORS as exc:
            st.error(f"Undo failed: {exc}")
    action_two.caption("Undo and replacement append events; original history is retained.")
    if state.picks and filtered:
        with st.expander("Replace an earlier pick"):
            pick_number = st.selectbox(
                "Pick to replace",
                list(range(1, len(state.picks) + 1)),
                format_func=lambda value: (
                    f"{value}: {state.picks[value - 1].player_name} "
                    f"({state.picks[value - 1].team_id})"
                ),
            )
            replacements = {row.player_id: row for row in filtered}
            replacement = st.selectbox(
                "Replacement player",
                list(replacements),
                format_func=lambda value: (
                    f"{replacements[value].display_name} ({replacements[value].position})"
                ),
            )
            if st.button("Replace pick"):
                try:
                    replace_draft_pick(
                        context.draft_repository,
                        state.session_id,
                        pick_number,
                        replacement,
                        expected_version=state.version,
                        command_id=f"streamlit-replace-{uuid.uuid4().hex}",
                    )
                    st.rerun()
                except _DRAFT_ERRORS as exc:
                    st.error(f"Replacement failed: {exc}")


def _render_rosters(session: DraftRoomSession) -> None:
    state = session.state
    selected_team = st.selectbox(
        "Roster view",
        [f"team-{slot:02d}" for slot in range(1, state.rules.teams + 1)],
        index=state.user_draft_slot - 1,
    )
    records: list[dict[str, Any]] = []
    for draft_slot in range(1, state.rules.teams + 1):
        picks = state.roster(draft_slot)
        assignment = assign_roster(
            [RosterPlayer(pick.player_id, pick.position, pick.projected_points) for pick in picks],
            state.rules,
        )
        for pick in picks:
            if pick.team_id == selected_team:
                records.append(
                    {
                        "Overall": pick.overall_pick,
                        "Player": pick.player_name,
                        "Pos": pick.position,
                        "Assigned slot": assignment.slot_for_player(pick.player_id),
                        "P50": pick.projected_points,
                    }
                )
    st.dataframe(records, hide_index=True, width="stretch")
    with st.expander("All teams at a glance"):
        st.dataframe(
            [
                {
                    "Team": f"team-{slot:02d}",
                    "Players": len(state.roster(slot)),
                    "P50 total": sum(pick.projected_points for pick in state.roster(slot)),
                }
                for slot in range(1, state.rules.teams + 1)
            ],
            hide_index=True,
            width="stretch",
        )


def _render_recommendations(context: AppContext, session: DraftRoomSession) -> None:
    state = session.state
    st.subheader("Top three recommendation roles")
    if session.info.recommendation_status != "recommendation_ready":
        st.warning(session.info.recommendation_message)
        st.caption(
            "Manual tracking remains available. Resolve canonical ADP mappings and create a "
            "new frozen session to activate simulation-backed recommendations."
        )
        return
    if not state.is_user_turn:
        st.info("Recommendations unlock when your team is on the clock.")
        return
    result: RecommendationResult | None = None
    if st.button("Run reproducible recommendation simulation", type="primary"):
        with st.spinner("Simulating the rest of the draft..."):
            result = recommend_for_session(
                context.draft_repository,
                state.session_id,
                context.engine_config,
            )
    if result is None:
        st.caption("The simulation runs only on demand and uses the session's frozen random seed.")
        return
    if not result.available:
        st.warning(result.message)
        return
    for candidate in result.candidates[:3]:
        with st.container(border=True):
            st.subheader(
                f"{candidate.role.replace('_', ' ').title()}: "
                f"{candidate.display_name} ({candidate.position})"
            )
            one, two, three = st.columns(3)
            one.metric("Recommendation score", f"{candidate.draft_recommendation_score:.1f}")
            two.metric("P50 VORP", f"{candidate.p50_vorp:.1f}")
            three.metric("Likely gone", f"{candidate.probability_gone_next_pick:.1%}")
            st.write(candidate.explanation)
            with st.expander("Why this recommendation"):
                st.dataframe(
                    [component.as_dict() for component in candidate.components],
                    hide_index=True,
                    width="stretch",
                )
                st.json(candidate.simulation)
                for risk in candidate.primary_risks:
                    st.write(f"- {risk}")


def _render_player_explanation(
    context: AppContext,
    filtered: list[DraftBoardRow],
) -> None:
    if not filtered:
        return
    with st.expander("Player explanation drawer"):
        options = {row.player_id: row for row in filtered}
        selected_id = st.selectbox(
            "Explain player",
            list(options),
            format_func=lambda value: f"{options[value].display_name} ({options[value].position})",
            key="draft_explanation_player",
        )
        row = options[selected_id]
        st.write(
            f"**{row.method_kind.replace('_', ' ').title()}** via `{row.projection_method}`; "
            f"risk `{row.risk}`; tier {row.tier}."
        )
        if row.probability_gone_before_user_pick is None:
            st.info(
                "Likely-gone probability is unavailable because reviewed market evidence "
                "is missing."
            )
        else:
            st.info(
                f"Estimated chance selected before your next pick: "
                f"{row.probability_gone_before_user_pick:.1%}. This is market pressure, "
                "not quality."
            )
        projection = next(
            (item for item in context.projection_board.rows if item.player_id == selected_id),
            None,
        )
        if projection is not None:
            st.json(projection.explanation_for("fantasy_points_total"))


def render() -> None:
    """Render manual drafting, board intelligence, rosters, and recommendations."""

    context = load_app_context()
    setup = selected_league_setup(context)
    if setup is None:
        setup = LeagueSetupRecord(
            league_season_id="checked-in-reference",
            rules=context.reference_rules,
            draft_slot=1,
        )
    render_page_header(
        "Draft Room",
        "Every pick has a paper trail",
        "Run a manual snake draft, inspect market pressure, and request recommendations only "
        "when their validated inputs are ready.",
    )
    _render_create_session(context, setup)
    session = _session_selector(context)
    if session is None:
        return
    state = session.state
    current_round = (
        None
        if state.current_overall_pick is None
        else (state.current_overall_pick - 1) // state.rules.teams + 1
    )
    one, two = st.columns(2)
    one.metric("Current pick", state.current_overall_pick or "Complete")
    two.metric("Round", current_round or "Complete")
    three, four = st.columns(2)
    three.metric("On the clock", state.current_team_id or "Complete")
    four.metric("Your next pick", state.next_user_pick() or "None")
    render_lineage("State hash", state.fingerprint())
    st.caption(
        f"Your team `{state.user_team_id}` - event version {state.version} - "
        f"{len(state.picks)}/{state.total_picks} picks recorded."
    )

    st.subheader("Available player board")
    filtered = _render_board(session)
    _render_pick_actions(context, session, filtered)
    _render_player_explanation(context, filtered)
    render_method_legend()

    st.divider()
    st.subheader("Rosters")
    _render_rosters(session)
    st.divider()
    _render_recommendations(context, session)
