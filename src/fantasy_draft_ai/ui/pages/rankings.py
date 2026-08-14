"""Pre-draft player rankings built from the active projection publication."""

from __future__ import annotations

from collections.abc import Sequence

import pandas as pd
import streamlit as st

from fantasy_draft_ai.draft.pool import FrozenDraftPlayer
from fantasy_draft_ai.recommendations.projection_baseline import build_projection_rankings
from fantasy_draft_ai.ui.common import render_page_header
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
    with st.container(horizontal=True, vertical_alignment="bottom"):
        team_count = int(
            st.selectbox(
                "League size",
                _TEAM_COUNTS,
                index=_TEAM_COUNTS.index(context.reference_rules.teams),
                format_func=lambda value: f"{value} teams",
                key="rankings_team_count",
            )
        )
        preset_key = st.selectbox(
            "Roster preset",
            _ROSTER_PRESET_KEYS,
            index=_ROSTER_PRESET_KEYS.index(DEFAULT_REDRAFT_PRESET_KEY),
            format_func=lambda value: redraft_preset(str(value)).label,
            key="rankings_roster_preset",
        )
    with st.container(horizontal=True, vertical_alignment="bottom"):
        show = st.selectbox(
            "Show",
            _SHOW_OPTIONS,
            index=2,
            key="rankings_limit",
        )
        search = st.text_input(
            "Search",
            placeholder="Type a player name",
            key="rankings_search",
        )
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
    selected_positions = st.multiselect(
        "Positions",
        positions,
        default=positions,
        key="rankings_positions",
    )
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
        leaders = st.columns(min(4, len(filtered)))
        for column, row in zip(leaders, filtered[:4], strict=True):
            with column.container(border=True):
                st.caption(f"#{row.overall_rank} · {row.position}{row.position_rank}")
                st.subheader(row.display_name)
                st.metric("Projected points", f"{row.p50:.1f}")
                st.caption(f"+{row.p50_vorp:.1f} over replacement")
    st.dataframe(
        pd.DataFrame.from_records(
            {
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
        ),
        hide_index=True,
        width="stretch",
        height=650,
        column_config={
            "Rank": st.column_config.NumberColumn(format="#%d"),
            "Projection": st.column_config.NumberColumn(format="%.1f"),
            "Value": st.column_config.NumberColumn(
                "Value over replacement",
                format="%+.1f",
                help="Projected points above this league's replacement player.",
            ),
            "Floor": st.column_config.NumberColumn(format="%.1f"),
            "Ceiling": st.column_config.NumberColumn(format="%.1f"),
            "ADP": st.column_config.NumberColumn(format="%.1f"),
        },
    )
    st.caption(
        f"Showing {len(filtered):,} of {len(rankings):,} draftable projected players for a "
        f"{team_count}-team full-PPR league using the {preset.label} roster. Blank ADP means "
        "reviewed market linkage is not available; it does not remove the player from the "
        "model ranking."
    )
    fallback_count = _fallback_projection_count(preparation.players)
    if fallback_count:
        projection_label = "projection" if fallback_count == 1 else "projections"
        use_verb = "uses" if fallback_count == 1 else "use"
        st.warning(
            f"{fallback_count:,} rookie {projection_label} {use_verb} an unvalidated point-only "
            "fallback. P10, P50, and P90 are identical, so risk is not estimated; treat "
            "those rankings as lower-confidence estimates."
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
