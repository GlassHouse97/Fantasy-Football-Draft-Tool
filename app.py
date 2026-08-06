"""Streamlit application; reusable reads and validation remain in the package."""

import uuid
from typing import Any

import pandas as pd
import streamlit as st
import yaml

from fantasy_draft_ai.config import load_config
from fantasy_draft_ai.draft.repository import DraftRepository
from fantasy_draft_ai.draft.roster import RosterPlayer, assign_roster
from fantasy_draft_ai.draft.state import DraftStateError
from fantasy_draft_ai.recommendations.config import load_draft_engine_config
from fantasy_draft_ai.recommendations.engine import recommend_for_session
from fantasy_draft_ai.rules.models import LeagueRules
from fantasy_draft_ai.scoring.engine import PlayerStatLine, score_player
from fantasy_draft_ai.services.adp_market import load_adp_market_board
from fantasy_draft_ai.services.draft_room import (
    DraftRoomSession,
    create_draft_session,
    load_draft_session,
    prepare_draft_room,
    record_draft_pick,
    replace_draft_pick,
    undo_draft_pick,
)
from fantasy_draft_ai.services.projections import (
    PROJECTION_TARGETS,
    TARGET_LABELS,
    PlayerProjection,
    load_projection_board,
)
from fantasy_draft_ai.services.status import project_status


def _projection_display_frame(
    rows: list[PlayerProjection],
    target_name: str,
) -> pd.DataFrame:
    records: list[dict[str, Any]] = []
    for row in rows:
        interval = row.target(target_name)
        records.append(
            {
                "Player": row.display_name,
                "Pos": row.position,
                "P10": interval.p10,
                "P50": interval.p50,
                "P90": interval.p90,
                "Method type": interval.method_label(row.prediction_status),
                "Selected method": interval.selected_name,
                "Status": row.prediction_status,
            }
        )
    if not records:
        return pd.DataFrame(
            columns=[
                "Player",
                "Pos",
                "P10",
                "P50",
                "P90",
                "Method type",
                "Selected method",
                "Status",
            ]
        )
    return pd.DataFrame.from_records(records).sort_values(
        ["P50", "Player"], ascending=[False, True], kind="stable"
    )


st.set_page_config(page_title="Fantasy Football Draft AI", page_icon="🏈", layout="wide")
st.title("🏈 Fantasy Football Draft AI")
st.caption("Local-first projections, ruleset-aware value, and explanations you can audit.")

config = load_config()
projection_board = load_projection_board(config)
adp_market_board = load_adp_market_board(config)
rules_path = config.project_root / "configs" / "example_ppr_12_team.yaml"
with rules_path.open(encoding="utf-8") as handle:
    reference_rules = LeagueRules.model_validate(yaml.safe_load(handle))
draft_engine_config = load_draft_engine_config(
    config.project_root / "configs" / "draft_engine.yaml"
)
draft_preparation = prepare_draft_room(
    projection_board,
    adp_market_board,
    rules=reference_rules,
    projection_reference_rules=reference_rules,
    required_market_coverage=draft_engine_config.market_coverage_required,
)
draft_repository = DraftRepository(config.resolve(config.paths.warehouse))

tab_names = ["Project status"]
if projection_board.available:
    tab_names.append(f"{config.project.prediction_season} projections")
if adp_market_board.available:
    tab_names.append("ADP availability")
if draft_preparation.readiness.state_ready:
    tab_names.append("Draft room")
tab_names.extend(["Scoring sandbox", "Learning path"])
tabs = st.tabs(tab_names)
tab_by_name = dict(zip(tab_names, tabs, strict=True))

with tab_by_name["Project status"]:
    st.subheader("What is actually available")
    for item in project_status(
        config,
        phase4_status=projection_board.status,
        draft_readiness=draft_preparation.readiness,
    ):
        icon = "✅" if item.available else "⏳"
        st.write(f"{icon} **{item.name}:** {item.status}")
    if projection_board.available:
        st.success(
            "The Phase 4 projection run, upstream lineage, persisted counts, and registered "
            "artifacts passed the read-only availability checks."
        )
    else:
        st.info(
            "The learned projection view stays hidden until a complete, current Phase 4 run "
            f"passes validation. Current state: {projection_board.status.message}."
        )

if projection_board.available:
    projection_tab_name = f"{config.project.prediction_season} projections"
    with tab_by_name[projection_tab_name]:
        st.subheader(f"{config.project.prediction_season} player projections")
        st.caption(
            "Learned-model P10-P90 ranges are empirical uncertainty intervals, not guarantees. "
            "Selected transparent baselines are honest point estimates (P10=P50=P90). All "
            "methods were compared on chronological validation seasons; rookie fallbacks remain "
            "explicitly unvalidated and uncalibrated."
        )

        positions = sorted({row.position for row in projection_board.rows})
        filter_col, search_col, target_col = st.columns([1, 2, 2])
        with filter_col:
            selected_positions = st.multiselect("Position", positions, default=positions)
        with search_col:
            search = st.text_input("Search player", placeholder="Type a player name")
        with target_col:
            target_name = st.selectbox(
                "Projection target",
                PROJECTION_TARGETS,
                format_func=lambda value: TARGET_LABELS[value],
            )

        filtered = [
            row
            for row in projection_board.rows
            if row.position in selected_positions
            and search.casefold() in row.display_name.casefold()
        ]
        display_frame = _projection_display_frame(filtered, target_name)
        st.dataframe(
            display_frame,
            hide_index=True,
            width="stretch",
            column_config={
                "P10": st.column_config.NumberColumn(format="%.2f"),
                "P50": st.column_config.NumberColumn(format="%.2f"),
                "P90": st.column_config.NumberColumn(format="%.2f"),
            },
        )
        st.caption(f"Showing {len(filtered):,} of {len(projection_board.rows):,} players.")

        if filtered:
            st.divider()
            st.subheader("Player explanation")
            options = {row.player_id: row for row in filtered}
            selected_player_id = st.selectbox(
                "Player",
                list(options),
                format_func=lambda player_id: (
                    f"{options[player_id].display_name} ({options[player_id].position})"
                ),
            )
            selected_player = options[selected_player_id]
            interval = selected_player.target(target_name)
            method_label = interval.method_label(selected_player.prediction_status)
            metric_one, metric_two, metric_three = st.columns(3)
            metric_one.metric("P50", f"{interval.p50:.2f}")
            metric_two.metric("P10", f"{interval.p10:.2f}")
            metric_three.metric("P90", f"{interval.p90:.2f}")
            st.write(
                f"**Method:** {method_label} — `{interval.selected_name}`  \n"
                f"**Status:** `{selected_player.prediction_status}`"
            )
            if "rookie" in selected_player.prediction_status.casefold():
                st.warning(
                    "This rookie row uses a transparent heuristic fallback. It is not a "
                    "validated learned-model prediction, and its interval is uncalibrated."
                )
            elif interval.selected_source.casefold() == "learned":
                st.info(
                    "This explanation describes model associations. It is not a causal claim "
                    "or a draft recommendation."
                )
            else:
                st.info(
                    "This selection uses a transparent baseline retained by the validation and "
                    "bootstrap gate. Its repeated P10/P50/P90 is a point estimate, not a "
                    "calibrated interval."
                )
            explanation = selected_player.explanation_for(target_name)
            top_factors = explanation.get("top_factors")
            if isinstance(top_factors, list) and top_factors:
                st.write("**Leading model factors**")
                st.dataframe(pd.DataFrame.from_records(top_factors), hide_index=True)
            with st.expander("Full explanation payload"):
                st.json(explanation)

        with st.expander("Run lineage and champion selection"):
            if projection_board.run is not None:
                st.json(projection_board.run.as_dict())
            st.json([selection.as_dict() for selection in projection_board.selections])

if adp_market_board.available:
    with tab_by_name["ADP availability"]:
        st.subheader("ADP movement and next-pick availability")
        st.caption(
            "This view estimates market survival, not player quality or a draft recommendation. "
            "Probabilities use source spread when available and remain uncalibrated until real "
            "draft outcomes are archived."
        )
        input_col, next_col = st.columns(2)
        with input_col:
            current_pick = int(
                st.number_input("Current overall pick", min_value=1, max_value=400, value=1)
            )
        with next_col:
            next_pick = int(
                st.number_input(
                    "Your next overall pick",
                    min_value=current_pick + 1,
                    max_value=500,
                    value=max(current_pick + 1, 24),
                )
            )

        positions = sorted({row.position for row in adp_market_board.rows})
        filter_col, search_col = st.columns([1, 2])
        with filter_col:
            selected_positions = st.multiselect("ADP position", positions, default=positions)
        with search_col:
            market_search = st.text_input(
                "Search ADP player",
                placeholder="Type a player or team",
            )
        probability_rows: list[dict[str, Any]] = []
        availability_config = adp_market_board.availability_config
        if availability_config is None:
            st.error("The versioned availability assumptions could not be loaded.")
        else:
            for row in adp_market_board.rows:
                if row.position not in selected_positions:
                    continue
                searchable = f"{row.player_name} {row.nfl_team or ''}".casefold()
                if market_search.casefold() not in searchable:
                    continue
                estimate = row.estimate_availability(
                    current_pick=current_pick,
                    next_pick=next_pick,
                    config=availability_config,
                )
                probability_rows.append(
                    {
                        "Player": row.player_name,
                        "Pos": row.position,
                        "Team": row.nfl_team,
                        "ADP": row.average_pick,
                        "P available": estimate.probability_available_at_next_pick,
                        "P selected first": estimate.probability_selected_before_next_pick,
                        "Spread method": estimate.spread_method,
                        "Sample": estimate.sample_size,
                        "7-day change": row.change_7d,
                        "History": row.observation_count,
                        "Trend status": row.linear_status,
                        "Mapping": row.mapping_confidence,
                        "Source": row.source,
                    }
                )
            probability_frame = pd.DataFrame.from_records(probability_rows)
            if not probability_frame.empty:
                probability_frame = probability_frame.sort_values(["ADP", "Player"], kind="stable")
            st.dataframe(
                probability_frame,
                hide_index=True,
                width="stretch",
                column_config={
                    "ADP": st.column_config.NumberColumn(format="%.1f"),
                    "P available": st.column_config.ProgressColumn(
                        min_value=0.0,
                        max_value=1.0,
                        format="percent",
                    ),
                    "P selected first": st.column_config.NumberColumn(format="percent"),
                    "7-day change": st.column_config.NumberColumn(format="%.2f"),
                },
            )
            st.caption(
                f"Showing {len(probability_rows):,} market rows. Positive ADP movement means "
                "the player moved later; missing history remains blank."
            )
            st.warning(
                "Linear and exponentially weighted movement remain unavailable for rows with "
                "fewer than three independent dated observations. No supervised availability "
                "or calibration claim is active."
            )

if draft_preparation.readiness.state_ready:
    with tab_by_name["Draft room"]:
        st.subheader("Event-sourced manual snake draft")
        st.caption(
            "Every pick, undo, and replacement is appended to DuckDB. The visible state is "
            "rebuilt from that event stream, and the session freezes its projection and market "
            "inputs so a later data refresh cannot rewrite the draft."
        )
        st.info(draft_preparation.readiness.state_message)
        if draft_preparation.readiness.recommendation_ready:
            st.success(draft_preparation.readiness.recommendation_message)
        else:
            st.warning(
                f"Recommendations are locked: "
                f"{draft_preparation.readiness.recommendation_message}"
            )

        try:
            existing_sessions = draft_repository.list_sessions()
        except (OSError, TypeError, ValueError, DraftStateError) as exc:
            existing_sessions = ()
            st.error(f"Draft persistence could not be opened: {exc}")

        with st.expander("Create a new draft session", expanded=not existing_sessions):
            setup_one, setup_two, setup_three = st.columns(3)
            with setup_one:
                session_name = st.text_input(
                    "Session name",
                    value="My 2026 draft",
                    key="draft_session_name",
                )
            with setup_two:
                user_slot = int(
                    st.number_input(
                        "Your draft slot",
                        min_value=1,
                        max_value=reference_rules.teams,
                        value=1,
                        step=1,
                        key="draft_user_slot",
                    )
                )
            with setup_three:
                simulation_count = int(
                    st.number_input(
                        "Simulation paths",
                        min_value=16,
                        max_value=draft_engine_config.maximum_simulations,
                        value=draft_engine_config.default_simulations,
                        step=16,
                        key="draft_simulation_count",
                    )
                )
            st.write(
                f"**Rules:** {reference_rules.teams} teams, "
                f"{reference_rules.draft.rounds} rounds, "
                f"fingerprint `{reference_rules.fingerprint()[:16]}...`"
            )
            if st.button("Create session", type="primary", key="create_draft_session"):
                try:
                    created = create_draft_session(
                        draft_repository,
                        draft_preparation,
                        session_name=session_name,
                        rules=reference_rules,
                        user_draft_slot=user_slot,
                        engine_config=draft_engine_config,
                        random_seed=config.project.random_seed,
                        simulation_count=simulation_count,
                        command_id=f"streamlit-create-{uuid.uuid4().hex}",
                    )
                    st.session_state["selected_draft_session"] = created.state.session_id
                    st.success(f"Created {created.state.session_id}.")
                    st.rerun()
                except (OSError, KeyError, TypeError, ValueError, DraftStateError) as exc:
                    st.error(f"Session creation failed: {exc}")

        if existing_sessions:
            session_ids = [session.session_id for session in existing_sessions]
            prior_selection = st.session_state.get("selected_draft_session")
            default_index = (
                session_ids.index(prior_selection) if prior_selection in session_ids else 0
            )
            selected_session_id = st.selectbox(
                "Open session",
                session_ids,
                index=default_index,
                format_func=lambda session_id: next(
                    f"{item.session_name} ({item.session_id}, v{item.current_version})"
                    for item in existing_sessions
                    if item.session_id == session_id
                ),
                key="draft_session_selector",
            )
            st.session_state["selected_draft_session"] = selected_session_id
            draft_session: DraftRoomSession | None
            try:
                draft_session = load_draft_session(draft_repository, selected_session_id)
            except (OSError, KeyError, TypeError, ValueError, DraftStateError) as exc:
                st.error(f"Session replay failed: {exc}")
                draft_session = None

            if draft_session is not None:
                state = draft_session.state
                current_round = (
                    None
                    if state.current_overall_pick is None
                    else (state.current_overall_pick - 1) // state.rules.teams + 1
                )
                header_one, header_two, header_three, header_four = st.columns(4)
                header_one.metric(
                    "Current pick",
                    (
                        "Complete"
                        if state.current_overall_pick is None
                        else state.current_overall_pick
                    ),
                )
                header_two.metric("Round", "Complete" if current_round is None else current_round)
                header_three.metric("On the clock", state.current_team_id or "Complete")
                header_four.metric(
                    "Your following pick",
                    state.next_user_pick(include_current=False) or "None",
                )
                st.caption(
                    f"Event version {state.version} · state hash `{state.fingerprint()[:20]}...` · "
                    f"your team `{state.user_team_id}`"
                )

                available_players = [
                    player
                    for player in draft_session.players
                    if player.player_id not in state.selected_player_ids
                ]
                available_positions = sorted({player.position for player in available_players})
                board_filter, board_search = st.columns([1, 2])
                with board_filter:
                    draft_positions = st.multiselect(
                        "Draft positions",
                        available_positions,
                        default=available_positions,
                        key="draft_position_filter",
                    )
                with board_search:
                    draft_search = st.text_input(
                        "Search available players",
                        key="draft_player_search",
                    )
                filtered_players = [
                    player
                    for player in available_players
                    if player.position in draft_positions
                    and draft_search.casefold() in player.display_name.casefold()
                ]
                filtered_players.sort(key=lambda player: (-player.p50, player.display_name))
                st.dataframe(
                    pd.DataFrame.from_records(
                        {
                            "Player": player.display_name,
                            "Pos": player.position,
                            "P10": player.p10,
                            "P50": player.p50,
                            "P90": player.p90,
                            "ADP": player.average_pick,
                            "Market mapping": player.mapping_confidence or "unresolved",
                            "Method": player.projection_method,
                        }
                        for player in filtered_players[:150]
                    ),
                    hide_index=True,
                    width="stretch",
                    column_config={
                        "P10": st.column_config.NumberColumn(format="%.1f"),
                        "P50": st.column_config.NumberColumn(format="%.1f"),
                        "P90": st.column_config.NumberColumn(format="%.1f"),
                        "ADP": st.column_config.NumberColumn(format="%.1f"),
                    },
                )
                st.caption(
                    f"{len(available_players):,} players remain; showing up to 150 filtered rows."
                )

                if state.current_overall_pick is not None and filtered_players:
                    pick_options = {player.player_id: player for player in filtered_players}
                    selected_pick_player = st.selectbox(
                        "Record player",
                        list(pick_options),
                        format_func=lambda player_id: (
                            f"{pick_options[player_id].display_name} "
                            f"({pick_options[player_id].position})"
                        ),
                        key="draft_pick_player",
                    )
                    if st.button("Record pick", type="primary", key="record_draft_pick"):
                        try:
                            record_draft_pick(
                                draft_repository,
                                state.session_id,
                                selected_pick_player,
                                expected_version=state.version,
                                command_id=f"streamlit-pick-{uuid.uuid4().hex}",
                            )
                            st.rerun()
                        except (OSError, KeyError, TypeError, ValueError, DraftStateError) as exc:
                            st.error(f"Pick failed: {exc}")

                action_one, action_two = st.columns(2)
                with action_one:
                    if st.button(
                        "Undo latest pick",
                        disabled=not state.picks,
                        key="undo_draft_pick",
                    ):
                        try:
                            undo_draft_pick(
                                draft_repository,
                                state.session_id,
                                expected_version=state.version,
                                command_id=f"streamlit-undo-{uuid.uuid4().hex}",
                            )
                            st.rerun()
                        except (
                            OSError,
                            KeyError,
                            TypeError,
                            ValueError,
                            DraftStateError,
                        ) as exc:
                            st.error(f"Undo failed: {exc}")
                with action_two:
                    st.write(
                        "Undo and replacement append history; original event rows are retained."
                    )

                if state.picks and available_players:
                    with st.expander("Replace an earlier pick"):
                        replacement_pick = st.selectbox(
                            "Pick to replace",
                            list(range(1, len(state.picks) + 1)),
                            format_func=lambda overall: (
                                f"{overall}: {state.picks[overall - 1].player_name} "
                                f"({state.picks[overall - 1].team_id})"
                            ),
                            key="replacement_pick",
                        )
                        replacement_options = {
                            player.player_id: player for player in available_players
                        }
                        replacement_player = st.selectbox(
                            "New player",
                            list(replacement_options),
                            format_func=lambda player_id: (
                                f"{replacement_options[player_id].display_name} "
                                f"({replacement_options[player_id].position})"
                            ),
                            key="replacement_player",
                        )
                        if st.button("Replace pick", key="replace_draft_pick"):
                            try:
                                replace_draft_pick(
                                    draft_repository,
                                    state.session_id,
                                    replacement_pick,
                                    replacement_player,
                                    expected_version=state.version,
                                    command_id=f"streamlit-replace-{uuid.uuid4().hex}",
                                )
                                st.rerun()
                            except (
                                OSError,
                                KeyError,
                                TypeError,
                                ValueError,
                                DraftStateError,
                            ) as exc:
                                st.error(f"Replacement failed: {exc}")

                st.divider()
                st.subheader("All team rosters")
                roster_records: list[dict[str, Any]] = []
                for draft_slot in range(1, state.rules.teams + 1):
                    roster_picks = state.roster(draft_slot)
                    assignment = assign_roster(
                        [
                            RosterPlayer(
                                pick.player_id,
                                pick.position,
                                pick.projected_points,
                            )
                            for pick in roster_picks
                        ],
                        state.rules,
                    )
                    for pick in roster_picks:
                        roster_records.append(
                            {
                                "Team": pick.team_id,
                                "Overall": pick.overall_pick,
                                "Player": pick.player_name,
                                "Pos": pick.position,
                                "Assigned slot": assignment.slot_for_player(pick.player_id),
                                "Projected P50": pick.projected_points,
                            }
                        )
                st.dataframe(
                    pd.DataFrame.from_records(roster_records),
                    hide_index=True,
                    width="stretch",
                )

                st.divider()
                st.subheader("Recommendation baseline")
                if draft_session.info.recommendation_status != "recommendation_ready":
                    st.warning(draft_session.info.recommendation_message)
                    st.caption(
                        "Manual drafting remains available. Review canonical ADP identities, "
                        "then create a new frozen session after rebuilding Phase 5."
                    )
                elif not state.is_user_turn:
                    st.info("Recommendations will be available when your team is on the clock.")
                elif st.button("Run recommendation simulation", key="run_recommendation"):
                    with st.spinner("Simulating reproducible rest-of-draft paths..."):
                        result = recommend_for_session(
                            draft_repository,
                            state.session_id,
                            draft_engine_config,
                        )
                    if not result.available:
                        st.warning(result.message)
                    else:
                        for candidate in result.candidates:
                            st.markdown(
                                f"**{candidate.role.replace('_', ' ').title()}: "
                                f"{candidate.display_name} ({candidate.position})**"
                            )
                            st.write(
                                f"Score {candidate.draft_recommendation_score:.1f} · "
                                f"P50 VORP {candidate.p50_vorp:.1f} · "
                                f"P(gone) {candidate.probability_gone_next_pick:.1%}"
                            )
                            st.write(candidate.explanation)
                            with st.expander("Components, simulation, and risks"):
                                st.dataframe(
                                    pd.DataFrame.from_records(
                                        item.as_dict() for item in candidate.components
                                    ),
                                    hide_index=True,
                                )
                                st.json(candidate.simulation)
                                for risk in candidate.primary_risks:
                                    st.write(f"- {risk}")

with tab_by_name["Scoring sandbox"]:
    rules = reference_rules
    st.write(f"Example ruleset fingerprint: `{rules.fingerprint()}`")
    position = st.selectbox("Position", ["QB", "RB", "WR", "TE"], index=2)
    receptions = st.number_input("Receptions", min_value=0.0, value=7.0, step=1.0)
    receiving_yards = st.number_input("Receiving yards", value=100.0, step=5.0)
    receiving_tds = st.number_input("Receiving touchdowns", min_value=0.0, value=1.0, step=1.0)
    line = PlayerStatLine(
        position=position,
        receptions=receptions,
        receiving_yards=receiving_yards,
        receiving_tds=receiving_tds,
    )
    st.metric("Fantasy points", f"{score_player(line, rules.scoring):.2f}")

with tab_by_name["Learning path"]:
    st.markdown(
        """
        1. Archive source data without overwriting it.
        2. Validate and map players with visible confidence.
        3. Build features using only information available before the prediction season.
        4. Beat transparent baselines before accepting a more complex model.
        5. Apply the exact league scoring and roster rules.
        6. Estimate draft availability separately from player performance.
        7. Simulate the rest of the draft and explain the recommendation.
        """
    )
    st.markdown("See `docs/learning/SCORING_AND_REPLACEMENT_VALUE.md` in the repository.")
