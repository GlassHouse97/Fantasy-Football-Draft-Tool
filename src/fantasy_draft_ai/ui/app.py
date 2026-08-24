"""Multipage Streamlit application entry point."""

from __future__ import annotations

import streamlit as st

from fantasy_draft_ai.ui.pages.data_center import render as render_data_center
from fantasy_draft_ai.ui.pages.draft_assistant import render as render_draft_assistant
from fantasy_draft_ai.ui.pages.draft_room import render as render_draft_room
from fantasy_draft_ai.ui.pages.help import render as render_help
from fantasy_draft_ai.ui.pages.home import render as render_home
from fantasy_draft_ai.ui.pages.league_history import render as render_league_history
from fantasy_draft_ai.ui.pages.league_setup import render as render_league_setup
from fantasy_draft_ai.ui.pages.learning_center import render as render_learning_center
from fantasy_draft_ai.ui.pages.model_lab import render as render_model_lab
from fantasy_draft_ai.ui.pages.player_export import render as render_player_export
from fantasy_draft_ai.ui.pages.player_market_consensus import (
    render as render_player_market_consensus,
)
from fantasy_draft_ai.ui.pages.post_draft import render as render_post_draft
from fantasy_draft_ai.ui.pages.rankings import render as render_rankings


def run_app() -> None:
    """Configure and run the recommendation-first local application."""

    st.set_page_config(
        page_title="Fantasy Football Draft AI",
        page_icon=":material/sports_football:",
        layout="wide",
        initial_sidebar_state="collapsed",
    )
    pages = {
        "Draft": [
            st.Page(
                render_draft_assistant,
                title="Draft Assistant",
                icon=":material/sports_football:",
                default=True,
            ),
            st.Page(
                render_rankings,
                title="Player rankings",
                icon=":material/leaderboard:",
                url_path="rankings",
            ),
            st.Page(
                render_post_draft,
                title="Draft report",
                icon=":material/analytics:",
                url_path="draft-report",
            ),
        ],
        "Player Evaluation": [
            st.Page(
                render_player_export,
                title="Player Export List",
                icon=":material/table_view:",
                url_path="player-export",
            ),
            st.Page(
                render_player_market_consensus,
                title="Player Market Consensus",
                icon=":material/forum:",
                url_path="player-market-consensus",
            ),
        ],
        "Help": [
            st.Page(
                render_help,
                title="How to use the app",
                icon=":material/help:",
                url_path="help",
            )
        ],
        "Advanced": [
            st.Page(
                render_league_setup,
                title="League settings",
                icon=":material/tune:",
                url_path="league-settings",
            ),
            st.Page(
                render_draft_room,
                title="Technical draft room",
                icon=":material/science:",
                url_path="technical-draft-room",
            ),
            st.Page(
                render_home,
                title="System status",
                icon=":material/monitor_heart:",
                url_path="system-status",
            ),
            st.Page(
                render_data_center,
                title="Data center",
                icon=":material/database:",
                url_path="data-center",
            ),
            st.Page(
                render_league_history,
                title="League history",
                icon=":material/history:",
                url_path="league-history",
            ),
            st.Page(
                render_model_lab,
                title="Model details",
                icon=":material/science:",
                url_path="model-details",
            ),
            st.Page(
                render_learning_center,
                title="Learning center",
                icon=":material/school:",
                url_path="learning-center",
            ),
        ],
    }
    navigation = st.navigation(pages, position="top", expanded=False)
    navigation.run()
