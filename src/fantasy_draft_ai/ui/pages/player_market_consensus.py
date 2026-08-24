"""Player-first creator consensus workspace and evidence gate."""

from __future__ import annotations

import streamlit as st

from fantasy_draft_ai.ui.common import render_page_header, render_section_header
from fantasy_draft_ai.ui.context import load_app_context

_CHANNEL_NAME = "Fantasy Football Advice"
_CHANNEL_URL = "https://www.youtube.com/@FantasyFootballAdviceFFA/videos"


def render() -> None:
    """Show the planned player-first view without inventing transcript conclusions."""

    context = load_app_context()
    render_page_header(
        "Player Market Consensus",
        "Creator opinions, organized by player",
        "Search one player and compare each creator's overall stance across the current-year "
        "video corpus—not a stack of per-video summaries.",
    )

    if not context.projection_board.available:
        st.error(
            "The active player publication is unavailable, so player lookup cannot be built.",
            icon=":material/error:",
        )
        return

    player_options = sorted(
        context.projection_board.rows,
        key=lambda row: (row.display_name.casefold(), row.player_id),
    )
    selected_player = st.selectbox(
        "Find a player",
        player_options,
        format_func=lambda player: f"{player.display_name} · {player.position}",
        key="market_consensus_player",
        width="stretch",
    )
    if selected_player is None:
        st.info("Choose a player to inspect creator coverage.")
        return

    render_section_header(
        selected_player.display_name,
        f"{selected_player.position} · 2026 creator-consensus evidence",
        icon=":material/person_search:",
    )
    with st.container(border=True):
        with st.container(horizontal=True, vertical_alignment="center"):
            st.subheader(_CHANNEL_NAME)
            st.link_button(
                "Open channel",
                _CHANNEL_URL,
                icon=":material/open_in_new:",
            )
        st.badge("Transcript corpus not built", color="orange", icon=":material/pending:")
        st.write(
            "No stance is shown yet because this channel's 2026 video inventory, caption "
            "coverage, player mentions, and nickname matches have not been archived and "
            "validated."
        )
        st.caption(
            "Future output: overall stance, confidence, summary, videos mentioning the "
            "player, total mentions, latest evidence date, and links back to the evidence."
        )

    st.info(
        "This page is the Milestone 2 evidence gate. The next build will create the channel "
        "inventory and transcript pipeline before generating any vibes-based conclusions.",
        icon=":material/verified_user:",
    )
    with st.expander("How the consensus will be built", icon=":material/schema:"):
        st.markdown(
            """
1. Inventory every in-scope 2026 video and preserve its URL, publication date, and title.
2. Acquire available transcripts with provenance and report videos with no usable captions.
3. Resolve player mentions through canonical IDs plus reviewed aliases such as **JSN**.
4. Aggregate evidence across the whole channel-year into one player/creator stance.
5. Show coverage, confidence, evidence dates, and source links alongside the summary.
6. Human-review a sample of mentions and summaries before treating the result as useful.
"""
        )
        st.warning(
            "No mention means no conclusion. Sparse or contradictory evidence will be labeled "
            "insufficient or mixed instead of being forced into a positive/negative rating."
        )
