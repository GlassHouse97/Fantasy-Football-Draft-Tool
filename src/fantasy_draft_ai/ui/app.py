"""Multipage Streamlit application entry point."""

from __future__ import annotations

import streamlit as st

from fantasy_draft_ai.ui.pages.data_center import render as render_data_center
from fantasy_draft_ai.ui.pages.draft_room import render as render_draft_room
from fantasy_draft_ai.ui.pages.home import render as render_home
from fantasy_draft_ai.ui.pages.league_history import render as render_league_history
from fantasy_draft_ai.ui.pages.league_setup import render as render_league_setup
from fantasy_draft_ai.ui.pages.learning_center import render as render_learning_center
from fantasy_draft_ai.ui.pages.model_lab import render as render_model_lab
from fantasy_draft_ai.ui.pages.post_draft import render as render_post_draft


def run_app() -> None:
    """Configure and run the eight-area local application."""

    st.set_page_config(
        page_title="Fantasy Football Draft AI",
        page_icon=":material/sports_football:",
        layout="wide",
        initial_sidebar_state="expanded",
    )
    st.markdown(
        """
        <style>
        [data-testid="stSidebar"] { border-right: 1px solid #20324d; }
        [data-testid="stMetric"] {
            background: color-mix(in srgb, #1f6feb 9%, transparent);
            border: 1px solid color-mix(in srgb, #1f6feb 28%, transparent);
            border-radius: 0.75rem;
            padding: 0.75rem;
        }
        .block-container { padding-top: 2.2rem; padding-bottom: 4rem; }
        </style>
        """,
        unsafe_allow_html=True,
    )
    pages = {
        "Build & validate": [
            st.Page(
                render_home,
                title="Project Status",
                icon=":material/home:",
                url_path="status",
                default=True,
            ),
            st.Page(
                render_data_center,
                title="Data Center",
                icon=":material/database:",
                url_path="data-center",
            ),
            st.Page(
                render_league_history,
                title="League History",
                icon=":material/history:",
                url_path="league-history",
            ),
            st.Page(
                render_model_lab,
                title="Model Lab",
                icon=":material/science:",
                url_path="model-lab",
            ),
        ],
        "Draft": [
            st.Page(
                render_league_setup,
                title="League Setup",
                icon=":material/tune:",
                url_path="league-setup",
            ),
            st.Page(
                render_draft_room,
                title="Draft Room",
                icon=":material/sports_football:",
                url_path="draft-room",
            ),
            st.Page(
                render_post_draft,
                title="Post-Draft",
                icon=":material/analytics:",
                url_path="post-draft",
            ),
        ],
        "Learn": [
            st.Page(
                render_learning_center,
                title="Learning Center",
                icon=":material/school:",
                url_path="learning-center",
            )
        ],
    }
    with st.sidebar:
        st.subheader("Fantasy Draft AI")
        st.caption("Local-first. Auditable. No championship-probability theater.")
    navigation = st.navigation(pages, position="sidebar", expanded=True)
    navigation.run()
