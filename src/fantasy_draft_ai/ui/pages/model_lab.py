"""Read-only Model Lab page for Phase 3 and Phase 4 evidence."""

from __future__ import annotations

from urllib.parse import quote

import pandas as pd
import streamlit as st

from fantasy_draft_ai.services.model_lab import (
    ModelLabSnapshot,
    load_model_lab,
    load_player_model_explanation,
)
from fantasy_draft_ai.services.projections import TARGET_LABELS
from fantasy_draft_ai.ui.common import render_method_legend, render_page_header
from fantasy_draft_ai.ui.context import AppContext, load_app_context


def _render_contract(snapshot: ModelLabSnapshot) -> None:
    st.subheader("Prediction contract")
    target_tab, feature_tab, split_tab = st.tabs(("Targets", "Features", "Splits"))
    with target_tab:
        st.dataframe(
            [target.as_dict() for target in snapshot.targets],
            hide_index=True,
            width="stretch",
        )
        st.info(
            "What this means: each target is evaluated separately. A model can win for season "
            "points while a transparent baseline remains better for games played."
        )
    with feature_tab:
        st.dataframe(
            [feature.as_dict() for feature in snapshot.features],
            hide_index=True,
            width="stretch",
        )
        st.info(
            "What this means: lagged values are built from seasons available before the "
            "prediction year; the feature contract is fingerprinted with the run."
        )
    with split_tab:
        st.dataframe(
            [fold.as_dict() for fold in snapshot.folds],
            hide_index=True,
            width="stretch",
        )
        st.info(
            "What this means: every training season precedes its evaluation season. The 2025 "
            "test season was not used to select champions."
        )


def _render_champions(snapshot: ModelLabSnapshot) -> None:
    st.subheader("Model versus transparent baseline")
    rows = [
        {
            "Position": item.position,
            "Target": TARGET_LABELS.get(item.target_name, item.target_name),
            "Selected source": item.selected_source,
            "Selected method": item.selected_name,
            "Selected MAE": item.selection_value,
            "Reference baseline": item.reference_baseline_name,
            "Baseline MAE": item.reference_baseline_value,
            "MAE improvement": item.improvement,
            "Decision": item.decision_status,
        }
        for item in snapshot.selections
    ]
    st.dataframe(
        rows,
        hide_index=True,
        width="stretch",
        column_config={
            "Selected MAE": st.column_config.NumberColumn(format="%.3f"),
            "Baseline MAE": st.column_config.NumberColumn(format="%.3f"),
            "MAE improvement": st.column_config.NumberColumn(format="%+.3f"),
        },
    )
    chart = pd.DataFrame.from_records(rows)
    if not chart.empty:
        chart["Position / target"] = chart["Position"] + " / " + chart["Target"]
        st.bar_chart(chart, x="Position / target", y="MAE improvement", horizontal=True)
    st.info(
        "What this means: learned models are used only where their validation improvement "
        "survived the configured selection gate. Otherwise the simpler baseline wins."
    )


def _render_metrics(snapshot: ModelLabSnapshot) -> None:
    with st.expander("Explore evaluation metrics"):
        target_names = tuple(target.name for target in snapshot.targets)
        one, two, three = st.columns(3)
        target = one.selectbox(
            "Metric target",
            target_names,
            format_func=lambda value: TARGET_LABELS.get(value, value),
        )
        position = two.selectbox("Position", ("QB", "RB", "WR", "TE"))
        scope = three.selectbox("Evaluation scope", ("validation", "test"))
        records = []
        for item in (*snapshot.baseline_metrics, *snapshot.model_metrics):
            baseline_position_match = item.phase == "phase3" and item.segment in {
                position,
                "all",
            }
            model_position_match = item.phase == "phase4" and item.position == position
            if (
                item.target_name == target
                and item.evaluation_scope == scope
                and (baseline_position_match or model_position_match)
            ):
                records.append(item.as_dict())
        st.dataframe(records, hide_index=True, width="stretch")
        st.caption(
            "MAE and RMSE are lower-is-better error measures. Rank correlation and top-N "
            "capture describe ordering, not probability or causality."
        )


def _render_residuals(snapshot: ModelLabSnapshot) -> None:
    st.subheader("Residual diagnostics")
    target_names = tuple(target.name for target in snapshot.targets)
    one, two = st.columns(2)
    target = one.selectbox(
        "Residual target",
        target_names,
        format_func=lambda value: TARGET_LABELS.get(value, value),
        key="residual_target",
    )
    position = two.selectbox("Residual position", ("QB", "RB", "WR", "TE"))
    records = [
        {
            "Model": item.model_family,
            "Scope": item.prediction_scope,
            "Season": item.prediction_season,
            "Rows": item.rows,
            "Mean actual - prediction": item.mean_actual_minus_prediction,
            "MAE": item.mae,
            "RMSE": item.rmse,
        }
        for item in snapshot.residuals
        if item.target_name == target and item.position == position
    ]
    st.dataframe(records, hide_index=True, width="stretch")
    if records:
        residual_frame = pd.DataFrame.from_records(records)
        st.line_chart(
            residual_frame,
            x="Season",
            y="Mean actual - prediction",
            color="Model",
        )
    st.info(
        "What this means: positive signed residuals indicate underprediction; negative values "
        "indicate overprediction. Averages can hide player-level misses."
    )


def _render_importance(snapshot: ModelLabSnapshot) -> None:
    st.subheader("Feature importance")
    one, two, three = st.columns(3)
    position = one.selectbox("Importance position", ("QB", "RB", "WR", "TE"))
    target = two.selectbox(
        "Importance target",
        tuple(target.name for target in snapshot.targets),
        format_func=lambda value: TARGET_LABELS.get(value, value),
    )
    families = sorted(
        {
            item.model_family
            for item in snapshot.feature_importance
            if item.position == position and item.target_name == target
        }
    )
    if not families:
        st.info("No registered importance artifact is available for this selection.")
        return
    family = three.selectbox("Model family", families)
    selected_importance = sorted(
        (
            item
            for item in snapshot.feature_importance
            if item.position == position
            and item.target_name == target
            and item.model_family == family
        ),
        key=lambda item: item.rank,
    )
    records = [
        {
            "Feature": item.feature,
            "Rank": item.rank,
            "Importance": item.importance_mean,
            "Std dev": item.importance_std,
            "Direction": item.direction or "Magnitude only",
            "Method": item.method,
            "Interpretation": item.interpretation,
        }
        for item in selected_importance
    ]
    st.dataframe(records, hide_index=True, width="stretch")
    if records:
        st.bar_chart(
            pd.DataFrame.from_records(records[:12]),
            x="Feature",
            y="Importance",
            horizontal=True,
        )
    st.warning(
        "What this means: importance is an associative diagnostic for the fitted model. It is "
        "not proof that changing a feature causes fantasy performance."
    )


def _render_player_explanation(context: AppContext, snapshot: ModelLabSnapshot) -> None:
    st.subheader("Player explanation")
    if not snapshot.players:
        st.info("No validated live projection players are available.")
        return
    player_options = {player.player_id: player for player in snapshot.players}
    one, two = st.columns(2)
    player_id = one.selectbox(
        "Player",
        list(player_options),
        format_func=lambda value: (
            f"{player_options[value].display_name} ({player_options[value].position})"
        ),
    )
    target = two.selectbox(
        "Explanation target",
        tuple(target.name for target in snapshot.targets),
        format_func=lambda value: TARGET_LABELS.get(value, value),
    )
    explanation = load_player_model_explanation(context.config, player_id, target)
    if not explanation.available:
        st.warning(explanation.message)
        return
    metric_one, metric_two, metric_three = st.columns(3)
    metric_one.metric("P10", f"{explanation.p10:.2f}" if explanation.p10 is not None else "N/A")
    metric_two.metric("P50", f"{explanation.p50:.2f}" if explanation.p50 is not None else "N/A")
    metric_three.metric("P90", f"{explanation.p90:.2f}" if explanation.p90 is not None else "N/A")
    st.write(f"**Method:** {explanation.method_label}")
    if explanation.method_label.startswith("Transparent baseline"):
        st.write(
            "This player-target row uses the validated transparent baseline that won its "
            "chronological comparison."
        )
        if explanation.reason:
            st.caption(explanation.reason)
    else:
        st.write(explanation.interpretation or explanation.reason)
    if explanation.factors:
        st.dataframe(
            [
                {
                    "Rank": factor.rank,
                    "Feature": factor.feature,
                    "Direction": factor.direction,
                    "Player value": factor.player_value,
                    "Reference": factor.reference_value,
                    "Prediction delta": factor.prediction_delta,
                }
                for factor in explanation.factors
            ],
            hide_index=True,
            width="stretch",
        )
    if explanation.supporting_values:
        with st.expander("Supporting values"):
            st.dataframe(
                [
                    {"Name": value.name, "Value": value.value}
                    for value in explanation.supporting_values
                ],
                hide_index=True,
            )
    if not explanation.learned_model_used:
        st.info(
            "This player-target row was not served by a learned model. Repeated interval values "
            "are point estimates, not calibrated uncertainty."
        )


def _render_artifacts(snapshot: ModelLabSnapshot) -> None:
    st.subheader("Model cards and diagnostics")
    card_rows = [
        {
            "Position": card.position,
            "Target": TARGET_LABELS.get(card.target_name, card.target_name),
            "Family": card.model_family,
            "Path": card.relative_path,
            "GitHub": (
                "https://github.com/GlassHouse97/Fantasy-Football-Draft-Tool/blob/main/"
                f"{quote(card.relative_path.replace(chr(92), '/'), safe='/')}"
            ),
            "Verified": card.exists,
        }
        for card in snapshot.model_cards
    ]
    st.dataframe(
        card_rows,
        hide_index=True,
        width="stretch",
        column_config={"GitHub": st.column_config.LinkColumn(display_text="Open model card")},
    )
    available_diagnostics = [item for item in snapshot.diagnostics if item.exists]
    if available_diagnostics:
        selected_name = st.selectbox(
            "Diagnostic plot",
            [item.name for item in available_diagnostics],
        )
        diagnostic = next(item for item in available_diagnostics if item.name == selected_name)
        st.image(str(diagnostic.absolute_path), caption=diagnostic.relative_path)


def render() -> None:
    """Render model evidence and explanations without any training actions."""

    context = load_app_context()
    snapshot = load_model_lab(context.config)
    render_page_header(
        "Model Lab",
        "Evidence, not a training button",
        "Inspect targets, leakage-safe splits, comparisons, residuals, feature importance, and "
        "served player explanations from the validated Phase 4 publication.",
    )
    if not snapshot.available:
        st.error(snapshot.status.message)
        st.info("Validate Phase 3 and Phase 4 artifacts before this page exposes model claims.")
        return
    st.success(snapshot.status.message)
    if snapshot.run_id:
        st.caption(f"Active validated run: `{snapshot.run_id}`")
    _render_contract(snapshot)
    _render_champions(snapshot)
    _render_metrics(snapshot)
    _render_residuals(snapshot)
    _render_importance(snapshot)
    _render_player_explanation(context, snapshot)
    _render_artifacts(snapshot)
    render_method_legend()
    if snapshot.limitations:
        with st.expander("Registered limitations", expanded=True):
            for limitation in snapshot.limitations:
                st.write(f"- {limitation}")
    st.warning(
        "Model training is intentionally unavailable here. This page reads the validated "
        "publication and never promotes a new run."
    )
