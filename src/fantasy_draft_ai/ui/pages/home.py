"""Project-status home page."""

from __future__ import annotations

import duckdb
import streamlit as st

from fantasy_draft_ai.services.league_setup import LeagueSetupIntegrityError
from fantasy_draft_ai.services.status import project_status
from fantasy_draft_ai.ui.common import render_method_legend, render_page_header
from fantasy_draft_ai.ui.context import load_app_context


def render() -> None:
    """Render a truthful summary of the local build and its next action."""

    context = load_app_context()
    preparation = context.prepare_draft(context.reference_rules)
    model_run = context.projection_board.run
    statuses = project_status(
        context.config,
        phase4_status=context.projection_board.status,
        draft_readiness=preparation.readiness,
    )
    try:
        has_saved_setup = bool(context.setup_repository.list())
        setup_issue: str | None = None
    except (duckdb.Error, OSError, TypeError, ValueError, LeagueSetupIntegrityError) as exc:
        has_saved_setup = False
        setup_issue = str(exc)

    render_page_header(
        "Project Status",
        "Phase 7 command center",
        "See what is ready, what is blocked, and the one most useful action to take next.",
    )

    metric_one, metric_two = st.columns(2)
    metric_one.metric(
        "Canonical projections",
        f"{len(context.projection_board.rows):,}",
        help="Validated live-board rows only; unavailable runs display zero.",
    )
    metric_two.metric(
        "ADP observations",
        f"{context.adp_market_board.status.observation_rows:,}",
        help="Rows in the validated Phase 5 publication.",
    )
    metric_three, metric_four = st.columns(2)
    metric_three.metric(
        "Unresolved draft mappings",
        f"{preparation.readiness.unresolved_market_rows:,}",
        help="Compatible ADP rows that still lack a reviewed canonical player ID.",
    )
    metric_four.metric(
        "Recommendation gate",
        "Ready" if preparation.readiness.recommendation_ready else "Locked",
    )

    st.subheader("Recommended next action")
    if not context.projection_board.available:
        st.error(
            "Validate the Phase 4 projection publication before using model outputs. "
            f"Current status: {context.projection_board.status.message}"
        )
    elif preparation.readiness.unresolved_market_rows:
        st.warning(
            "Review the remaining canonical ADP identities, rebuild Phase 5, then create a "
            "new frozen draft session. Manual draft tracking remains usable now."
        )
    elif setup_issue is not None:
        st.error(f"Repair the saved league setup before drafting: {setup_issue}")
    elif not has_saved_setup:
        st.info("Save your exact league rules and draft slot in League Setup.")
    else:
        st.success("Open Draft Room and create or resume a frozen draft session.")

    st.subheader("Build facts")
    fact_one, fact_two = st.columns(2)
    fact_one.metric(
        "Training seasons",
        f"{context.config.training.start_season}-{context.config.training.end_season}",
    )
    fact_two.metric("Prediction season", context.config.project.prediction_season)
    fact_three, fact_four = st.columns(2)
    fact_three.metric(
        "Model cutoff",
        str(context.config.training.end_season),
        help="No prediction-season outcomes are included in training.",
    )
    fact_four.metric(
        "Latest ADP snapshots",
        context.adp_market_board.status.snapshot_count,
    )
    if model_run is not None:
        st.caption(
            f"Active run `{model_run.run_id}` trained at {model_run.trained_at}; "
            f"{model_run.model_rows} registered models and {model_run.champion_rows} champions."
        )

    st.subheader("Capability inventory")
    status_filter = st.segmented_control(
        "Show",
        options=("All", "Ready", "Not ready"),
        default="All",
        key="home_status_filter",
    )
    filtered = [
        item
        for item in statuses
        if status_filter == "All"
        or (status_filter == "Ready" and item.available)
        or (status_filter == "Not ready" and not item.available)
    ]
    st.dataframe(
        [
            {
                "State": "Ready" if item.available else "Not ready",
                "Capability": item.name,
                "Evidence": item.status,
            }
            for item in filtered
        ],
        hide_index=True,
        width="stretch",
        column_order=("State", "Capability", "Evidence"),
    )
    render_method_legend()
    st.warning(
        "Championship probabilities are intentionally disabled. The repository does not have "
        "enough uploaded league histories to support that claim."
    )
