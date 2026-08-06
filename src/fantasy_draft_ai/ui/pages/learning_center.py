"""Learning Center page backed by read-only repository discovery."""

from __future__ import annotations

from collections.abc import Sequence
from urllib.parse import quote

import streamlit as st

from fantasy_draft_ai.services.learning_center import LearningResource, load_learning_center
from fantasy_draft_ai.ui.common import records_frame, render_page_header
from fantasy_draft_ai.ui.context import load_app_context

_LEARNING_PATH: tuple[tuple[str, str, tuple[str, ...]], ...] = (
    (
        "1. Learn the draft math",
        "Start with scoring rules and replacement value before comparing players.",
        (
            "docs/learning/SCORING_AND_REPLACEMENT_VALUE.md",
            "notebooks/python/01_scoring_and_replacement_value.ipynb",
        ),
    ),
    (
        "2. Learn how projections earn trust",
        "Move from transparent baselines through chronological validation, learned models, "
        "and calibrated uncertainty.",
        (
            "docs/learning/03_baselines_and_why_they_matter.md",
            "docs/learning/04_train_validation_test_and_leakage.md",
            "docs/learning/05_linear_models_and_regularization.md",
            "docs/learning/06_gradient_boosted_trees.md",
            "docs/learning/07_uncertainty_and_prediction_intervals.md",
            "docs/learning/12_how_to_read_a_model_card.md",
        ),
    ),
    (
        "3. Connect projections to the draft room",
        "Finish with ADP movement, next-pick availability, league rules, and simulation.",
        (
            "docs/learning/08_adp_movement_and_availability.md",
            "docs/learning/09_replacement_value_and_rulesets.md",
            "docs/learning/10_monte_carlo_draft_simulation.md",
            "notebooks/python/10_draft_simulation.ipynb",
        ),
    ),
)


def render() -> None:
    """Render the discovered learning library and a suggested reading order."""

    context = load_app_context()
    catalog = load_learning_center(context.config.project_root)
    render_page_header(
        "Learning Center",
        "Understand every layer",
        "Follow the project from scoring arithmetic to model validation and draft simulation. "
        "These previews read documentation and notebook markdown only; notebook code is never "
        "executed here.",
    )

    metric_columns = st.columns(3)
    metric_columns[0].metric("Learning guides", len(catalog.guides))
    metric_columns[1].metric("Worked notebooks", len(catalog.notebooks))
    metric_columns[2].metric(
        "Readable resources",
        sum(resource.available for resource in catalog.resources),
    )

    if not catalog.resources:
        st.info(
            "No local learning resources were found. Add Markdown guides under "
            "`docs/learning/` or notebooks under `notebooks/`, then refresh this page."
        )
        return

    st.subheader("Suggested learning path")
    available_paths = {
        resource.relative_path for resource in catalog.resources if resource.available
    }
    for title, description, paths in _LEARNING_PATH:
        ready_count = sum(path in available_paths for path in paths)
        with st.container(border=True):
            st.markdown(f"#### {title}")
            st.write(description)
            st.caption(f"{ready_count} of {len(paths)} suggested resources available locally")
            for path in paths:
                st.markdown(f"- [{path}]({_github_url(path)})")

    st.subheader("Browse the local library")
    guide_tab, notebook_tab = st.tabs(["Guides", "Notebooks"])
    with guide_tab:
        _render_resource_table(catalog.guides, empty_label="No learning guides were discovered.")
    with notebook_tab:
        st.caption("Notebook descriptions come from markdown cells; code cells remain untouched.")
        _render_resource_table(
            catalog.notebooks,
            empty_label="No notebooks were discovered.",
        )

    unavailable = [resource for resource in catalog.resources if not resource.available]
    if unavailable:
        st.warning(
            f"{len(unavailable)} resource(s) could not be previewed. Their paths remain visible "
            "so the local files can be repaired."
        )


def _render_resource_table(
    resources: Sequence[LearningResource],
    *,
    empty_label: str,
) -> None:
    if not resources:
        st.info(empty_label)
        return

    records = [
        {
            "Title": resource.title,
            "What it covers": resource.summary,
            "Repository path": resource.relative_path,
            "Open": _github_url(resource.relative_path),
            "Status": "Ready" if resource.available else "Preview unavailable",
        }
        for resource in resources
    ]
    st.dataframe(
        records_frame(records),
        hide_index=True,
        width="stretch",
        column_config={
            "Title": st.column_config.TextColumn(width="medium"),
            "What it covers": st.column_config.TextColumn(width="large"),
            "Repository path": st.column_config.TextColumn(width="large"),
            "Open": st.column_config.LinkColumn(display_text="Open on GitHub"),
            "Status": st.column_config.TextColumn(width="small"),
        },
    )


def _github_url(relative_path: str) -> str:
    normalized = relative_path.replace("\\", "/")
    return (
        "https://github.com/GlassHouse97/Fantasy-Football-Draft-Tool/blob/main/"
        f"{quote(normalized, safe='/')}"
    )
