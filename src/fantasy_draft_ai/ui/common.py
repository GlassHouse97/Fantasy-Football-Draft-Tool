"""Reusable Streamlit presentation helpers."""

from __future__ import annotations

from collections.abc import Iterable, Mapping
from typing import Any

import duckdb
import pandas as pd
import streamlit as st

from fantasy_draft_ai.services.league_setup import (
    LeagueSetupIntegrityError,
    LeagueSetupRecord,
)
from fantasy_draft_ai.ui.context import AppContext


def render_page_header(title: str, eyebrow: str, description: str) -> None:
    """Render the consistent local-app page heading."""

    st.caption(eyebrow.upper())
    st.title(title)
    st.write(description)


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
