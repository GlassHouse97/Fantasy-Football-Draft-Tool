"""Pre-draft player rankings built from the active projection publication."""

from __future__ import annotations

from collections.abc import Sequence
from typing import Any

import pandas as pd
import streamlit as st

from fantasy_draft_ai.draft.pool import FrozenDraftPlayer
from fantasy_draft_ai.recommendations.projection_baseline import build_projection_rankings
from fantasy_draft_ai.ui.common import (
    position_cell_style,
    position_option_label,
    render_page_header,
    render_position_badge,
    render_section_header,
)
from fantasy_draft_ai.ui.context import load_app_context
from fantasy_draft_ai.ui.redraft_presets import (
    DEFAULT_REDRAFT_PRESET_KEY,
    REDRAFT_ROSTER_PRESETS,
    redraft_preset,
    rules_for_redraft_preset,
)

_TEAM_COUNTS = (8, 10, 12, 14, 16)
_ROSTER_PRESET_KEYS = tuple(preset.key for preset in REDRAFT_ROSTER_PRESETS)
_SHOW_OPTIONS = ("Top 50", "Top 100", "Top 200", "Top 300", "All players")


def _fallback_projection_count(players: Sequence[FrozenDraftPlayer]) -> int:
    return sum(
        "fallback_unvalidated" in player.prediction_status.strip().casefold()
        for player in players
    )


def render() -> None:
    """Render league-adjusted rankings without requiring a draft session."""

    context = load_app_context()
    render_page_header(
        "Player rankings",
        "Your redraft board",
        "Compare model projections and league-adjusted draft value before or during a draft.",
    )
    with st.container(border=True):
        st.caption("Tune the board to your league before comparing players.")
        team_count_value = st.segmented_control(
            "League size",
            _TEAM_COUNTS,
            default=context.reference_rules.teams,
            required=True,
            format_func=lambda value: f"{value} teams",
            key="rankings_team_count",
            width="stretch",
        )
        preset_key_value = st.segmented_control(
            "Roster preset",
            _ROSTER_PRESET_KEYS,
            default=DEFAULT_REDRAFT_PRESET_KEY,
            required=True,
            format_func=lambda value: redraft_preset(str(value)).label,
            key="rankings_roster_preset",
            width="stretch",
        )
        with st.container(horizontal=True, vertical_alignment="bottom"):
            show = st.selectbox(
                "Board size",
                _SHOW_OPTIONS,
                index=2,
                key="rankings_limit",
                width=180,
            )
            search = st.text_input(
                "Search players",
                placeholder="Type a player name",
                key="rankings_search",
                icon=":material/search:",
                width="stretch",
            )
    team_count = int(team_count_value)
    preset_key = str(preset_key_value)
    preset = redraft_preset(str(preset_key))
    rules = rules_for_redraft_preset(
        context.reference_rules,
        team_count=team_count,
        preset=preset,
    )
    preparation = context.prepare_draft(rules)
    if not preparation.readiness.state_ready:
        st.error(preparation.readiness.state_message)
        return
    rankings = build_projection_rankings(rules, preparation.players)
    positions = sorted({row.position for row in rankings})
    selected_position_value = st.pills(
        "Positions",
        positions,
        selection_mode="multi",
        default=positions,
        format_func=position_option_label,
        key="rankings_positions",
        width="stretch",
    )
    selected_positions = list(selected_position_value or ())
    normalized_search = search.strip().casefold()
    filtered = [
        row
        for row in rankings
        if row.position in selected_positions
        and normalized_search in row.display_name.casefold()
    ]
    if show != "All players":
        filtered = filtered[: int(str(show).removeprefix("Top "))]
    if filtered:
        render_section_header(
            "Top of the board",
            "The strongest league-adjusted values under the selected roster format.",
            icon=":material/workspace_premium:",
        )
        with st.container(horizontal=True):
            for row in filtered[:3]:
                with st.container(border=True, width=320, height="stretch"):
                    with st.container(horizontal=True):
                        render_position_badge(row.position, f"{row.position}{row.position_rank}")
                        st.badge(f"Overall #{row.overall_rank}", color="gray")
                        st.badge(f"Tier {row.tier}", color="violet")
                    st.subheader(row.display_name)
                    st.metric(
                        "Projected points",
                        f"{row.p50:.1f}",
                        icon=":material/query_stats:",
                        border=True,
                    )
                    st.caption(f"+{row.p50_vorp:.1f} points over replacement")
    else:
        st.info(
            "No players match those filters. Clear the search or select another position.",
            icon=":material/search_off:",
        )
    render_section_header(
        "Full player board",
        "Sort any column. Rank and player stay pinned while you scan projections.",
        icon=":material/leaderboard:",
    )
    fallback_count = _fallback_projection_count(preparation.players)
    if fallback_count:
        st.badge(
            f"{fallback_count:,} rookie estimates need extra caution",
            icon=":material/warning:",
            color="orange",
        )
    ranking_records = [
        {
            "Rank": row.overall_rank,
            "Player": row.display_name,
            "Pos": row.position,
            "Pos rank": row.position_rank,
            "Tier": row.tier,
            "Projection": row.p50,
            "VORP": row.p50_vorp,
            "Floor": row.p10,
            "Ceiling": row.p90,
            "ADP": row.average_pick if row.average_pick is not None else float("nan"),
            "Risk": row.risk.title(),
        }
        for row in filtered
    ]
    ranking_frame = pd.DataFrame.from_records(
        ranking_records,
        columns=(
            "Rank",
            "Player",
            "Pos",
            "Pos rank",
            "Tier",
            "Projection",
            "VORP",
            "Floor",
            "Ceiling",
            "ADP",
            "Risk",
        ),
    )
    market_available = not ranking_frame["ADP"].isna().all()
    if not market_available:
        ranking_frame = ranking_frame.drop(columns=["ADP"])
    ranking_column_config: dict[str, Any] = {
        "Rank": st.column_config.NumberColumn(format="#%d", pinned=True, width="small"),
        "Player": st.column_config.TextColumn(pinned=True, width="medium"),
        "Pos": st.column_config.TextColumn(width="small"),
        "Pos rank": st.column_config.NumberColumn(format="#%d", width="small"),
        "Tier": st.column_config.NumberColumn(format="%d", width="small"),
        "Projection": st.column_config.NumberColumn(format="%.1f"),
        "VORP": st.column_config.NumberColumn(
            "VORP",
            format="%+.1f",
            help="Projected points above this league's replacement player.",
        ),
        "Floor": st.column_config.NumberColumn(format="%.1f"),
        "Ceiling": st.column_config.NumberColumn(format="%.1f"),
    }
    if market_available:
        ranking_column_config["ADP"] = st.column_config.NumberColumn(format="%.1f")
    st.dataframe(
        ranking_frame.style.map(position_cell_style, subset=["Pos"]),
        hide_index=True,
        width="stretch",
        height=650,
        row_height=40,
        column_config=ranking_column_config,
    )
    market_note = (
        "ADP appears only where reviewed market linkage is available."
        if market_available
        else "ADP is hidden because reviewed market linkage is not available."
    )
    st.caption(
        f"Showing {len(filtered):,} of {len(rankings):,} draftable projected players for a "
        f"{team_count}-team full-PPR league using the {preset.label} roster. {market_note} "
        "This does not remove any player from the model ranking."
    )
    with st.expander("Data and confidence notes", icon=":material/info:"):
        if fallback_count:
            projection_label = "projection" if fallback_count == 1 else "projections"
            use_verb = "uses" if fallback_count == 1 else "use"
            st.warning(
                f"{fallback_count:,} rookie {projection_label} {use_verb} an unvalidated "
                "point-only fallback. P10, P50, and P90 are identical, so risk is not "
                "estimated; treat those rankings as lower-confidence estimates."
            )
        st.warning(
            "These rankings do not yet include live injury, suspension, or depth-chart news. "
            "Check current player news before your draft."
        )
    with st.expander("How these rankings work", icon=":material/info:"):
        st.write(
            "Overall rank uses projected season points above the replacement player for each "
            "position. Replacement changes with league size and roster demand, so a quarterback "
            "is not ranked above a receiver merely because quarterbacks score more raw points."
        )
        st.write(
            "Floor and ceiling are model uncertainty bounds. Tiers are position-rank bands the "
            "size of one league, not learned player clusters."
        )
