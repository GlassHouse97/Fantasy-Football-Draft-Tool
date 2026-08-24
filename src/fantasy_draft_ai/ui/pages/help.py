"""Plain-language help for the core redraft workflow."""

from __future__ import annotations

import streamlit as st

from fantasy_draft_ai.ui.common import render_page_header, render_section_header


def render() -> None:
    """Explain how to operate the assistant without requiring project knowledge."""

    render_page_header(
        "How to use the app",
        "Draft-day walkthrough",
        "You only need Draft Assistant and Player rankings for a normal practice or live draft.",
    )
    render_section_header(
        "Start in under a minute",
        "Three steps take you from league setup to a live recommendation.",
        icon=":material/rocket_launch:",
    )
    with st.container(horizontal=True):
        with st.container(border=True, width=310, height="stretch"):
            st.badge("Step 1", icon=":material/tune:", color="blue")
            st.subheader("Set the draft")
            st.caption("Choose your league size, draft position, and a recognizable name.")
        with st.container(border=True, width=310, height="stretch"):
            st.badge("Step 2", icon=":material/list_alt:", color="violet")
            st.subheader("Track or simulate picks")
            st.caption("Record real selections, or simulate opponents in a practice draft.")
        with st.container(border=True, width=310, height="stretch"):
            st.badge("Step 3", icon=":material/auto_awesome:", color="green")
            st.subheader("Use Best pick now")
            st.caption("When the clock says **You**, compare the top recommendation.")

    render_section_header(
        "During the draft",
        "The assistant updates immediately after every recorded selection.",
        icon=":material/sports_football:",
    )
    st.markdown(
        """
        1. Look at **On the clock** before recording a player.
        2. Search the available-player table or use its position filters.
        3. Select **Record my pick** or **Record taken** on the player who was selected.
        4. The player disappears and the snake draft advances automatically.
        5. In a practice draft, select **Sim to my pick** to auto-draft opponents until your turn.
        6. At your turn, use the main recommendation or one of its alternatives.
        7. If you enter the wrong player, select **Undo last pick** immediately.
        """
    )
    with st.container(border=True):
        st.badge("Live versus practice", icon=":material/touch_app:", color="blue")
        st.write(
            "For a real draft, record every supported opponent selection so the available-player "
            "board matches the room. For practice, **Sim to my pick** makes deterministic, "
            "roster-aware opponent selections from the frozen projections. The app does not yet "
            "sync a live Sleeper or ESPN room, and Quick Start cannot record K/DST selections."
        )

    render_section_header(
        "How to read the recommendation",
        "Projection estimates player output; draft value compares that output with alternatives.",
        icon=":material/query_stats:",
    )
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

    render_section_header(
        "Current supported quick start",
        "Use these boundaries for a trustworthy first test.",
        icon=":material/checklist:",
    )
    st.write(
        "The current projection publication targets **2026 full PPR**. Quick start supports "
        "8, 10, 12, 14, or 16 teams. Choose either a standard 2-WR/1-FLEX roster or a deeper "
        "3-WR/2-FLEX roster; both use seven bench spots. Kicker and team defense are not "
        "projected or recordable, so use Quick Start for no-K/DST leagues or skill-position "
        "practice. Advanced scoring changes remain separate because a different scoring system "
        "requires compatible projections."
    )
    with st.container(border=True):
        st.badge("Before draft day", icon=":material/warning:", color="orange")
        st.markdown(
            "- **Check current player news.** Injuries, suspensions, and depth-chart changes "
            "are not live in the model.\n"
            "- **Use extra caution with rookie estimates.** Some rookies use an unvalidated "
            "point estimate, so their downside and upside risk are not yet measured.\n"
            "- **Use a no-K/DST format for exact tracking.** Those positions are not on the "
            "current projection board."
        )

    with st.expander("Why is market timing unavailable?", icon=":material/help:"):
        st.write(
            "The player projections and league-adjusted ranking are available now. ADP timing "
            "requires reviewed links between the market feed and canonical player IDs. Until "
            "those links are verified, Rankings hides ADP and the assistant leaves next-pick "
            "probability unavailable rather than guessing by name."
        )
    with st.expander("Why do I have to enter opponents' picks?", icon=":material/help:"):
        st.write(
            "A recommendation is only correct for the players still available. Recording each "
            "league pick also lets the app follow snake order and know exactly when your team is "
            "on the clock. During a practice draft, **Sim to my pick** can do this automatically; "
            "during a real draft, enter the actual selections instead."
        )
    with st.expander("Where did all the technical pages go?", icon=":material/help:"):
        st.write(
            "They are under **Advanced**. Data, model, history, and replay evidence remain "
            "available, but they are not required to use the drafting product."
        )
