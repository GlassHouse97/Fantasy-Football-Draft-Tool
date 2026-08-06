"""Streamlit application; reusable reads and validation remain in the package."""

from typing import Any

import pandas as pd
import streamlit as st
import yaml

from fantasy_draft_ai.config import load_config
from fantasy_draft_ai.rules.models import LeagueRules
from fantasy_draft_ai.scoring.engine import PlayerStatLine, score_player
from fantasy_draft_ai.services.adp_market import load_adp_market_board
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

tab_names = ["Project status"]
if projection_board.available:
    tab_names.append(f"{config.project.prediction_season} projections")
if adp_market_board.available:
    tab_names.append("ADP availability")
tab_names.extend(["Scoring sandbox", "Learning path"])
tabs = st.tabs(tab_names)
tab_by_name = dict(zip(tab_names, tabs, strict=True))

with tab_by_name["Project status"]:
    st.subheader("What is actually available")
    for item in project_status(config, phase4_status=projection_board.status):
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

with tab_by_name["Scoring sandbox"]:
    rules_path = config.project_root / "configs" / "example_ppr_12_team.yaml"
    with rules_path.open(encoding="utf-8") as handle:
        rules = LeagueRules.model_validate(yaml.safe_load(handle))
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
