"""Streamlit presentation for the auditable post-draft report service."""

from __future__ import annotations

import json

import duckdb
import streamlit as st

from fantasy_draft_ai.draft.repository import DraftSessionInfo
from fantasy_draft_ai.draft.state import DraftStateError, team_id_for_slot
from fantasy_draft_ai.services.draft_room import DraftRoomSession, load_draft_session
from fantasy_draft_ai.services.post_draft import (
    PostDraftPlayer,
    PostDraftReport,
    PostDraftReportError,
    ProjectionSummary,
    RosterInsight,
    StrategyComparison,
    build_post_draft_report,
)
from fantasy_draft_ai.ui.common import (
    records_frame,
    render_lineage,
    render_method_legend,
    render_page_header,
)
from fantasy_draft_ai.ui.context import load_app_context

_POST_DRAFT_UI_ERRORS = (
    duckdb.Error,
    OSError,
    KeyError,
    TypeError,
    ValueError,
    DraftStateError,
)


def render() -> None:
    """Render a report for any team in a verified persisted draft session."""

    render_page_header(
        "Post-Draft Report",
        "Phase 7 · descriptive roster analysis",
        (
            "Inspect roster construction under the session's exact rules. Values come from "
            "the frozen draft inputs; missing market or uncertainty evidence stays missing."
        ),
    )
    try:
        context = load_app_context()
        sessions = context.draft_repository.list_sessions()
    except _POST_DRAFT_UI_ERRORS as exc:
        st.error(f"The local draft warehouse could not be opened: {exc}")
        return
    if not sessions:
        st.info(
            "No persisted draft session exists yet. Create or restore a session in Draft "
            "Room, record at least one pick, and return here."
        )
        st.code("fantasy-draft draft list", language="powershell")
        return

    info_by_label = {_session_label(info): info for info in sessions}
    selected_label = st.selectbox(
        "Draft session",
        tuple(info_by_label),
        help="Reports always reload and verify the persisted event stream.",
    )
    if selected_label is None:
        return
    selected_info = info_by_label[selected_label]
    try:
        session = load_draft_session(context.draft_repository, selected_info.session_id)
    except _POST_DRAFT_UI_ERRORS as exc:
        st.error(f"The selected draft session failed replay verification: {exc}")
        return

    team_by_label = {
        _team_label(session, slot): team_id_for_slot(slot)
        for slot in range(1, session.state.rules.teams + 1)
    }
    default_team_label = next(
        label for label, team_id in team_by_label.items() if team_id == session.state.user_team_id
    )
    team_labels = tuple(team_by_label)
    selected_team_label = st.selectbox(
        "Team",
        team_labels,
        index=team_labels.index(default_team_label),
        help="The configured user team is selected first; every league team is reportable.",
    )
    if selected_team_label is None:
        return
    try:
        report = build_post_draft_report(
            session,
            team_id=team_by_label[selected_team_label],
        )
    except PostDraftReportError as exc:
        st.error(f"The post-draft report could not verify its inputs: {exc}")
        return

    _render_status(report, selected_info.session_name)
    roster_tab, strategy_tab, audit_tab = st.tabs(
        ("Roster analysis", "Strategy baselines", "Audit & limitations")
    )
    with roster_tab:
        _render_roster(report)
    with strategy_tab:
        _render_strategies(report)
    with audit_tab:
        _render_audit(report, session)


def _session_label(info: DraftSessionInfo) -> str:
    return f"{info.session_name} · {info.session_id[:12]} · v{info.current_version} · {info.status}"


def _team_label(session: DraftRoomSession, draft_slot: int) -> str:
    team_id = team_id_for_slot(draft_slot)
    pick_count = len(session.state.roster(draft_slot))
    user_marker = " · My team" if draft_slot == session.state.user_draft_slot else ""
    return f"Slot {draft_slot} · {team_id} · {pick_count} picks{user_marker}"


def _render_status(report: PostDraftReport, session_name: str) -> None:
    if not report.draft_complete or not report.team_complete:
        st.warning(
            "This is a provisional report: the draft or selected roster is incomplete. "
            "The report will update from the persisted event stream as picks are recorded."
        )
    columns = st.columns(4)
    columns[0].metric("Session", session_name)
    columns[1].metric(
        "Draft progress",
        f"{report.picks_recorded}/{report.total_picks}",
    )
    columns[2].metric(
        "Team roster",
        f"{report.team_picks_recorded}/{report.expected_team_picks}",
    )
    columns[3].metric(
        "Starter coverage",
        f"{report.lineup.starter_coverage:.0%}",
    )


def _render_roster(report: PostDraftReport) -> None:
    st.subheader("Projected roster value")
    starter, bench, roster = st.columns(3)
    starter.metric("Starter P50", _points(report.lineup.starters.median))
    bench.metric("Bench P50", _points(report.lineup.bench.median))
    roster.metric("Full-roster P50", _points(report.lineup.roster.median))

    st.caption(
        "P10/P90 totals are shown only when every player in that group has measured "
        "uncertainty. They sum marginal intervals and are not calibrated team quantiles."
    )
    range_columns = st.columns(3)
    range_columns[0].metric("Roster P10", _optional_points(report.lineup.roster.floor))
    range_columns[1].metric("Roster P50", _points(report.lineup.roster.median))
    range_columns[2].metric("Roster P90", _optional_points(report.lineup.roster.ceiling))
    st.progress(
        report.lineup.roster.interval_coverage,
        text=(
            "Uncertainty coverage: "
            f"{report.lineup.roster.interval_player_count}/"
            f"{report.lineup.roster.player_count} selected players"
        ),
    )

    st.subheader("Exact lineup assignment")
    if not report.players:
        st.info("This team has no recorded picks yet.")
    else:
        starter_players = tuple(
            player for player in report.players if player.lineup_role == "starter"
        )
        bench_players = tuple(player for player in report.players if player.lineup_role == "bench")
        starters_tab, bench_tab = st.tabs(
            (f"Starters ({len(starter_players)})", f"Bench ({len(bench_players)})")
        )
        with starters_tab:
            _render_player_table(starter_players)
        with bench_tab:
            _render_player_table(bench_players)

    st.subheader("Positional draft capital")
    if report.positional_draft_capital:
        st.dataframe(
            records_frame(
                {
                    "Position": item.position,
                    "Players": item.player_count,
                    "Starters": item.starter_count,
                    "Bench": item.bench_count,
                    "Overall picks": ", ".join(str(pick) for pick in item.overall_picks),
                    "Pick share": item.pick_share,
                    "Mean overall pick": item.mean_overall_pick,
                    "Mapped ADP": f"{item.mapped_adp_count}/{item.player_count}",
                    "Mean value vs ADP": item.mean_pick_value_vs_adp,
                    "Replacement P50": item.replacement_points,
                    "Total P50 VORP": item.total_p50_vorp,
                }
                for item in report.positional_draft_capital
            ),
            hide_index=True,
            width="stretch",
            column_config={
                "Pick share": st.column_config.ProgressColumn(
                    "Pick share",
                    min_value=0.0,
                    max_value=1.0,
                    format="percent",
                ),
                "Mean value vs ADP": st.column_config.NumberColumn(format="%.1f"),
                "Replacement P50": st.column_config.NumberColumn(format="%.1f"),
                "Total P50 VORP": st.column_config.NumberColumn(format="%.1f"),
            },
        )
    else:
        st.caption("Positional capital appears after this team records a pick.")

    adp_column, risk_column = st.columns(2)
    with adp_column:
        st.markdown("#### Value versus ADP")
        st.metric(
            "Mean pick-minus-ADP",
            _optional_number(report.value_vs_adp.mean_pick_value_vs_adp),
        )
        st.caption(
            f"Coverage: {report.value_vs_adp.observed_players}/"
            f"{report.team_picks_recorded}. Positive means selected later than ADP; "
            "missing values are not imputed."
        )
    with risk_column:
        st.markdown("#### Replacement-value exposure")
        st.metric(
            "Starter floors below replacement",
            str(report.replacement_risk.starters_below_replacement_floor),
        )
        st.caption(
            f"Evaluated {report.replacement_risk.evaluated_starters}/"
            f"{report.replacement_risk.starter_players} starter floors; descriptive "
            "shortfall is not an outcome probability."
        )

    _render_insights(report.strengths, report.weaknesses)
    render_method_legend()


def _render_player_table(players: tuple[PostDraftPlayer, ...]) -> None:
    if not players:
        st.caption("No players are assigned here yet.")
        return
    st.dataframe(
        records_frame(
            {
                "Slot": player.lineup_slot,
                "Round": player.round,
                "Pick": player.overall_pick,
                "Player": player.display_name,
                "Pos": player.position,
                "P10": player.p10,
                "P50": player.p50,
                "P90": player.p90,
                "ADP": player.average_pick,
                "Value vs ADP": player.pick_value_vs_adp,
                "Replacement": player.replacement_points,
                "P50 VORP": player.p50_vorp,
                "Floor risk": _risk_label(player.replacement_risk_status),
                "Method": player.projection_method,
            }
            for player in players
        ),
        hide_index=True,
        width="stretch",
        column_config={
            name: st.column_config.NumberColumn(format="%.1f")
            for name in (
                "P10",
                "P50",
                "P90",
                "ADP",
                "Value vs ADP",
                "Replacement",
                "P50 VORP",
            )
        },
    )


def _render_insights(
    strengths: tuple[RosterInsight, ...],
    weaknesses: tuple[RosterInsight, ...],
) -> None:
    st.subheader("Ruleset-specific readout")
    strength_column, weakness_column = st.columns(2)
    with strength_column:
        st.markdown("#### Strengths")
        if not strengths:
            st.caption("No measured strength is labeled yet.")
        for insight in strengths:
            st.success(f"**{insight.title}**\n\n{insight.detail}")
    with weakness_column:
        st.markdown("#### Weaknesses")
        if not weaknesses:
            st.caption("No measured weakness is labeled yet.")
        for insight in weaknesses:
            st.warning(f"**{insight.title}**\n\n{insight.detail}")


def _render_strategies(report: PostDraftReport) -> None:
    st.subheader("Transparent strategy comparisons")
    st.write(
        "Each counterfactual uses this team's recorded pick numbers, exact roster legality, "
        "and the recorded opponent board. Positive differences mean the actual team has the "
        "higher P50 value."
    )
    for comparison in report.strategy_comparisons:
        _render_strategy(comparison)


def _render_strategy(comparison: StrategyComparison) -> None:
    with st.container(border=True):
        st.markdown(f"#### {comparison.label}")
        st.caption(comparison.description)
        if not comparison.available:
            st.warning(comparison.unavailable_reason or "Required baseline inputs are unavailable.")
        else:
            columns = st.columns(3)
            columns[0].metric(
                "Baseline starter P50",
                _optional_summary_points(comparison.starters),
            )
            columns[1].metric(
                "Actual minus baseline starters",
                _optional_number(comparison.starter_median_difference),
            )
            columns[2].metric(
                "Actual minus baseline roster",
                _optional_number(comparison.roster_median_difference),
            )
            st.dataframe(
                records_frame(
                    {
                        "Overall pick": selection.overall_pick,
                        "Selected player ID": selection.player_id,
                    }
                    for selection in comparison.selections
                ),
                hide_index=True,
                width="stretch",
            )
        with st.expander("Assumptions"):
            for assumption in comparison.assumptions:
                st.markdown(f"- {assumption}")


def _render_audit(report: PostDraftReport, session: DraftRoomSession) -> None:
    st.subheader("Lineage and reproducibility")
    render_lineage("Report", report.fingerprint())
    render_lineage("Draft state", report.state_fingerprint)
    render_lineage("Frozen player pool", report.player_pool_fingerprint)
    render_lineage("Projection run", report.projection_run_id)
    render_lineage("ADP build", report.adp_build_fingerprint)
    render_lineage("Ruleset", report.ruleset_fingerprint)
    render_lineage("Draft engine config", session.info.engine_config_fingerprint)
    st.caption(
        f"Report contract: `{report.report_version}` · session version: "
        f"`{report.session_version}` · selected team: `{report.team_id}`"
    )
    with st.expander("Canonical league rules"):
        st.json(json.loads(report.ruleset_canonical_json))

    st.subheader("Limitations")
    for limitation in report.limitations:
        st.markdown(f"- {limitation}")
    st.download_button(
        "Download report JSON",
        data=json.dumps(report.as_dict(), indent=2, sort_keys=True),
        file_name=f"{report.session_id}-{report.team_id}-post-draft.json",
        mime="application/json",
        width="stretch",
    )


def _points(value: float) -> str:
    return f"{value:,.1f} pts"


def _optional_points(value: float | None) -> str:
    return "Unavailable" if value is None else _points(value)


def _optional_number(value: float | None) -> str:
    return "Unavailable" if value is None else f"{value:+,.1f}"


def _optional_summary_points(summary: ProjectionSummary | None) -> str:
    return "Unavailable" if summary is None else _points(summary.median)


def _risk_label(status: str) -> str:
    return {
        "floor_below_replacement": "Floor below replacement",
        "floor_at_or_above_replacement": "Floor at/above replacement",
        "uncertainty_unavailable": "Uncertainty unavailable",
        "replacement_unavailable": "Replacement unavailable",
    }.get(status, status)
