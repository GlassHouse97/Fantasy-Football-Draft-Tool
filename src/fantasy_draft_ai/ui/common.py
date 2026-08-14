"""Reusable Streamlit presentation helpers."""

from __future__ import annotations

from collections.abc import Iterable, Mapping
from typing import Any, Literal, TypeAlias

import duckdb
import pandas as pd
import streamlit as st

from fantasy_draft_ai.services.league_setup import (
    LeagueSetupIntegrityError,
    LeagueSetupRecord,
)
from fantasy_draft_ai.ui.context import AppContext

BadgeColor: TypeAlias = Literal[
    "red",
    "orange",
    "yellow",
    "blue",
    "green",
    "violet",
    "gray",
    "grey",
    "primary",
]

_POSITION_BADGE_COLORS: dict[str, BadgeColor] = {
    "QB": "blue",
    "RB": "green",
    "WR": "violet",
    "TE": "orange",
    "K": "gray",
    "DST": "red",
    "DEF": "red",
}

_POSITION_CELL_STYLES = {
    "QB": "background-color: #1D4ED8; color: #F8FAFC; font-weight: 700;",
    "RB": "background-color: #15803D; color: #F8FAFC; font-weight: 700;",
    "WR": "background-color: #6D28D9; color: #F8FAFC; font-weight: 700;",
    "TE": "background-color: #C2410C; color: #F8FAFC; font-weight: 700;",
    "K": "background-color: #475569; color: #F8FAFC; font-weight: 700;",
    "DST": "background-color: #BE123C; color: #F8FAFC; font-weight: 700;",
    "DEF": "background-color: #BE123C; color: #F8FAFC; font-weight: 700;",
}

_POSITION_MARKDOWN_COLORS = {
    "QB": "blue",
    "RB": "green",
    "WR": "violet",
    "TE": "orange",
    "K": "gray",
    "DST": "red",
    "DEF": "red",
}


def render_page_header(title: str, eyebrow: str, description: str) -> None:
    """Render the consistent local-app page heading."""

    with st.container(border=True, gap="xsmall"):
        st.badge(eyebrow, color="blue")
        st.title(title)
        st.caption(description)


def render_section_header(
    title: str,
    description: str | None = None,
    *,
    icon: str | None = None,
) -> None:
    """Introduce one product section with a compact, repeatable hierarchy."""

    label = title if icon is None else f"{icon} {title}"
    st.header(label)
    if description:
        st.caption(description)


def render_position_badge(position: str, label: str | None = None) -> None:
    """Render one position using the shared draft-night color language."""

    normalized = position.strip().upper()
    color = _POSITION_BADGE_COLORS.get(normalized, "gray")
    st.badge(label or normalized, color=color)


def position_cell_style(position: object) -> str:
    """Return a readable dataframe cell style for a fantasy position."""

    normalized = str(position).strip().upper()
    return _POSITION_CELL_STYLES.get(normalized, "")


def position_option_label(position: object) -> str:
    """Format position filter options with readable semantic text colors."""

    normalized = str(position).strip().upper()
    color = _POSITION_MARKDOWN_COLORS.get(normalized, "gray")
    return f":{color}[**{normalized}**]"


def render_method_legend() -> None:
    """Keep prediction provenance visible wherever model outputs appear."""

    with st.expander("How to read prediction methods"):
        st.markdown(
            """
            - **Learned model:** selected on chronological validation data.
            - **Transparent baseline:** a validated simple method and point estimate.
            - **Heuristic fallback:** explicit unvalidated coverage, usually for rookies.
            - **Unavailable:** required data or validation is missing; no value is invented.
            """
        )


def records_frame(records: Iterable[Mapping[str, Any]]) -> pd.DataFrame:
    """Create a predictable dataframe, including for an empty record collection."""

    return pd.DataFrame.from_records(list(records))


def selected_league_setup(context: AppContext) -> LeagueSetupRecord | None:
    """Resolve the current setup selection, defaulting safely when none is saved."""

    try:
        setups = context.setup_repository.list()
    except (duckdb.Error, OSError, TypeError, ValueError, LeagueSetupIntegrityError) as exc:
        st.error(f"Saved league setups could not be verified: {exc}")
        return None
    if not setups:
        return None
    selected_value = st.session_state.get("selected_league_setup")
    selected_id = selected_value if isinstance(selected_value, str) else None
    selected = next(
        (item for item in setups if item.league_season_id == selected_id),
        setups[0],
    )
    st.session_state["selected_league_setup"] = selected.league_season_id
    return selected


def render_lineage(label: str, value: str | None) -> None:
    """Render a compact fingerprint without implying that a missing value exists."""

    if value:
        st.caption(f"{label}: `{value[:20]}...`")
    else:
        st.caption(f"{label}: unavailable")
