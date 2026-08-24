"""Pre-draft player rankings built from the active projection publication."""

from __future__ import annotations

from collections.abc import Sequence
from math import isfinite
from typing import Any

import pandas as pd
import streamlit as st

from fantasy_draft_ai.draft.pool import FrozenDraftPlayer
from fantasy_draft_ai.recommendations.projection_baseline import (
    ProjectionRankingRow,
    build_projection_rankings,
)
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
_EXTREME_RANK_GAP = 12


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
        "Your consensus-first redraft board",
        "Start with FantasyPros market consensus, then use the health-neutral model as a "
        "secondary comparison.",
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
    model_rankings = build_projection_rankings(rules, preparation.players)
    consensus_rankings = _consensus_rankings(model_rankings)
    rankings = tuple(
        sorted(
            model_rankings,
            key=lambda row: _consensus_sort_key(row, consensus_rankings),
        )
    )
    positions = sorted({row.position for row in model_rankings})
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
            "The earliest FantasyPros consensus values under your selected filters.",
            icon=":material/workspace_premium:",
        )
        with st.container(horizontal=True):
            for row in filtered[:3]:
                with st.container(border=True, width=320, height="stretch"):
                    with st.container(horizontal=True):
                        render_position_badge(row.position, f"{row.position}{row.position_rank}")
                        consensus_rank = consensus_rankings.get(row.player_id)
                        if consensus_rank is not None:
                            st.badge(f"Consensus #{consensus_rank}", color="green")
                        st.badge(f"Model #{row.overall_rank}", color="gray")
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
        "Consensus controls the default order. Sort any column to explore model differences.",
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
            "Consensus rank": consensus_rankings.get(row.player_id),
            "Player": row.display_name,
            "Pos": row.position,
            "Pos rank": row.position_rank,
            "Tier": row.tier,
            "Experimental model rank": row.overall_rank,
            "Model vs market": _rank_delta(
                consensus_rankings.get(row.player_id),
                row.overall_rank,
            ),
            "17-game projection": row.p50,
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
            "Consensus rank",
            "Player",
            "Pos",
            "Pos rank",
            "Tier",
            "Experimental model rank",
            "Model vs market",
            "17-game projection",
            "VORP",
            "Floor",
            "Ceiling",
            "ADP",
            "Risk",
        ),
    )
    market_available = not ranking_frame["ADP"].isna().all()
    if not market_available:
        ranking_frame = ranking_frame.drop(
            columns=["Consensus rank", "Model vs market", "ADP"]
        )
    ranking_column_config: dict[str, Any] = {
        "Consensus rank": st.column_config.NumberColumn(
            format="#%d",
            pinned=True,
            width="small",
            help="Primary rank derived from the reviewed FantasyPros composite ADP.",
        ),
        "Player": st.column_config.TextColumn(pinned=True, width="medium"),
        "Pos": st.column_config.TextColumn(width="small"),
        "Pos rank": st.column_config.NumberColumn(format="#%d", width="small"),
        "Tier": st.column_config.NumberColumn(format="%d", width="small"),
        "Experimental model rank": st.column_config.NumberColumn(
            format="#%d",
            width="small",
            help="Health-neutral PPG model rank under this league's replacement values.",
        ),
        "Model vs market": st.column_config.NumberColumn(
            format="%+d",
            width="small",
            help=(
                "Consensus rank minus model rank. Positive means the model likes the "
                "player more than the market."
            ),
        ),
        "17-game projection": st.column_config.NumberColumn(
            format="%.1f",
            help="Projected fantasy points per game multiplied by 17 for every player.",
        ),
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
                f"{extreme_count:,} shown players differ by at least {_EXTREME_RANK_GAP} "
                "ranks between consensus and the experimental model. Review those gaps; "
                "do not treat them as automatic sleepers or fades.",
                icon=":material/warning:",
            )
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
        "Every model projection assumes a full 17-game season; no injury probability changes "
        "the order."
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
            "The model deliberately assumes every player is healthy for 17 games. It does not "
            "predict injuries or include live suspension and depth-chart news, so check current "
            "player status before drafting."
        )
    with st.expander("How these rankings work", icon=":material/info:"):
        st.write(
            "Consensus rank is the primary board order and comes from FantasyPros AVG. The "
            "experimental model starts with projected points per game, multiplies every player "
            "by the same 17 games, and then compares points above the replacement player at each "
            "position."
        )
        st.write(
            "Floor and ceiling are model uncertainty bounds. Tiers are position-rank bands the "
            "size of one league, not learned player clusters."
        )


def _consensus_rankings(
    rows: Sequence[ProjectionRankingRow],
) -> dict[str, int]:
    """Create deterministic competition ranks from reviewed average-pick values."""

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
        if row.average_pick is None:  # narrowed above; retained for strict typing
            continue
        current_pick = row.average_pick
        if prior_pick is None or current_pick != prior_pick:
            prior_pick = current_pick
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
