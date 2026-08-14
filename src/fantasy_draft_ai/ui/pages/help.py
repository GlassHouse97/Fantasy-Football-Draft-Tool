"""Plain-language help for the core redraft workflow."""

from __future__ import annotations

import streamlit as st

from fantasy_draft_ai.ui.common import render_page_header


def render() -> None:
    """Explain how to operate the assistant without requiring project knowledge."""

    render_page_header(
        "How to use the app",
        "Draft-day walkthrough",
        "You only need Draft Assistant and Player rankings for a normal practice or live draft.",
    )
    st.subheader("Start in under a minute")
    steps = st.columns(3)
    with steps[0].container(border=True):
        st.caption("STEP 1")
        st.subheader("Set the draft")
        st.write("Choose your league size, draft position, and a recognizable draft name.")
    with steps[1].container(border=True):
        st.caption("STEP 2")
        st.subheader("Track every supported pick")
        st.write("Record each QB, RB, WR, and TE selection in the exact draft order.")
    with steps[2].container(border=True):
        st.caption("STEP 3")
        st.subheader("Use Best pick now")
        st.write("When the app says **You** are on the clock, compare the top recommendation.")

    st.subheader("During the draft")
    st.markdown(
        """
        1. Look at **On the clock** before recording a player.
        2. Search the available-player table or use its position filters.
        3. Select **Record my pick** or **Record taken** on the player who was selected.
        4. The player disappears and the snake draft advances automatically.
        5. At your turn, use the main recommendation or one of its alternatives.
        6. If you enter the wrong player, select **Undo last pick** immediately.
        """
    )
    st.info(
        "The app is a manual tracker today. It does not yet sync a live Sleeper or ESPN room, "
        "so skipping supported opponents' picks makes its available-player list incorrect. "
        "Quick Start cannot record K/DST selections and is not yet an exact live tracker for "
        "leagues that draft those positions."
    )

    st.subheader("How to read the recommendation")
    st.dataframe(
        [
            {
                "Label": "Projected points",
                "Meaning": "The model's median full-season fantasy-point estimate.",
            },
            {
                "Label": "Value over replacement",
                "Meaning": "Points above the league-specific fallback at that position.",
            },
            {
                "Label": "Position rank",
                "Meaning": "Rank among players at the same position.",
            },
            {
                "Label": "Floor / ceiling",
                "Meaning": "The model's lower and upper uncertainty estimates.",
            },
            {
                "Label": "Chance available next pick",
                "Meaning": "Optional reviewed market timing; blank means it is unavailable.",
            },
        ],
        hide_index=True,
        width="stretch",
    )
    st.write(
        "**Best pick now** combines projected value, the drop to the next player at that "
        "position, and fit with your current roster. It is a decision aid, not a guarantee."
    )

    st.subheader("Current supported quick start")
    st.write(
        "The current projection publication targets **2026 full PPR**. Quick start supports "
        "8, 10, 12, 14, or 16 teams. Choose either a standard 2-WR/1-FLEX roster or a deeper "
        "3-WR/2-FLEX roster; both use seven bench spots. Kicker and team defense are not "
        "projected or recordable, so use Quick Start for no-K/DST leagues or skill-position "
        "practice. Advanced scoring changes remain separate because a different scoring system "
        "requires compatible projections."
    )
    st.warning(
        "The model does not yet include live injury, suspension, or depth-chart news. Check a "
        "current news source before making a real pick."
    )
    st.warning(
        "Some rookies without enough historical evidence use an explicitly unvalidated "
        "point-only fallback. Their P10, P50, and P90 values are identical, so risk is not "
        "estimated; treat those projections as lower-confidence estimates."
    )

    with st.expander("Why is ADP blank?", icon=":material/help:"):
        st.write(
            "The player projections and league-adjusted ranking are available now. ADP timing "
            "requires reviewed links between the market feed and canonical player IDs. Until "
            "those links are verified, the app leaves ADP and next-pick probability blank rather "
            "than guessing by name."
        )
    with st.expander("Why do I have to enter opponents' picks?", icon=":material/help:"):
        st.write(
            "A recommendation is only correct for the players still available. Recording each "
            "league pick also lets the app follow snake order and know exactly when your team is "
            "on the clock."
        )
    with st.expander("Where did all the technical pages go?", icon=":material/help:"):
        st.write(
            "They are under **Advanced**. Data, model, history, and replay evidence remain "
            "available, but they are not required to use the drafting product."
        )
