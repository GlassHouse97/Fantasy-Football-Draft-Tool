"""Read-only Phase 8 workspace for validated historical league evidence."""

from __future__ import annotations

import json
from typing import Any

import streamlit as st

from fantasy_draft_ai.services.league_history import (
    GateCriterion,
    HistoryTeamSummary,
    LeagueHistorySnapshot,
    load_league_history_snapshot,
)
from fantasy_draft_ai.ui.common import records_frame, render_lineage, render_page_header
from fantasy_draft_ai.ui.context import load_app_context

_GUIDE_URL = (
    "https://github.com/GlassHouse97/Fantasy-Football-Draft-Tool/blob/main/"
    "docs/LEAGUE_HISTORY_IMPORT_GUIDE.md"
)
_TEMPLATE_URL = (
    "https://github.com/GlassHouse97/Fantasy-Football-Draft-Tool/tree/main/"
    "data/templates/league_history_v1"
)
_RATE_CRITERIA = frozenset({"complete_drafts", "complete_outcomes", "mapped_picks"})


def render() -> None:
    """Render history coverage, team descriptions, and outcome-model gates."""

    context = load_app_context()
    snapshot = load_league_history_snapshot(context.config)
    render_page_header(
        "League History",
        "Phase 8 · descriptive evidence only",
        "Inspect validated historical drafts, team outcomes, draft-only scoring, and the exact "
        "evidence still missing before any future league-outcome model could be considered.",
    )
    st.warning(
        "This workspace does not train a playoff or championship model and does not produce "
        "outcome probabilities. A satisfied count gate would permit independent review only."
    )
    if snapshot.issue:
        st.info(snapshot.issue)

    st.subheader("Recommended next action")
    st.info(snapshot.next_action)
    _render_manual_workflow(snapshot)
    _render_coverage(snapshot)

    teams_tab, construction_tab, packages_tab, gate_tab = st.tabs(
        ("Team results", "Roster construction", "Packages & quality", "Outcome-model gate")
    )
    with teams_tab:
        _render_team_results(snapshot)
    with construction_tab:
        _render_roster_construction(snapshot)
    with packages_tab:
        _render_packages(snapshot)
    with gate_tab:
        _render_gate(snapshot)


def _render_manual_workflow(snapshot: LeagueHistorySnapshot) -> None:
    with st.expander("How to prepare and upload league history", expanded=not snapshot.packages):
        st.markdown(
            """
            1. Copy the `league-history-v1` template bundle to a private working folder.
            2. Replace league, owner, and team names with stable pseudonymous IDs **before**
               selecting any file. Keep the private crosswalk outside this repository and any
               OneDrive or backup-synchronized folder.
            3. Fill the required rules, complete draft recap, and all-team outcomes for every
               completed season available. Weekly rosters, matchups, and transactions are
               optional enrichment.
            4. Put `package.json` and the CSV files at the root of one ZIP archive.
            5. Open [Data Center](/data-center), import the package, read its quality report,
               and review unresolved football player identities before using player-linked
               results.

            The app does not transmit selected files, but operating-system or cloud-backup
            software may still synchronize their containing folder. Never include credentials,
            cookies, usernames, email addresses, chat, or a private pseudonym crosswalk.
            """
        )
        st.markdown(
            f"Read the [League History Import Guide]({_GUIDE_URL}) for field definitions, "
            f"troubleshooting, and the [{snapshot.gate.status} evidence boundary]({_GUIDE_URL})."
        )
        one, two = st.columns(2)
        one.link_button("Open import guide", _GUIDE_URL, width="stretch")
        two.link_button("Open template bundle", _TEMPLATE_URL, width="stretch")


def _render_coverage(snapshot: LeagueHistorySnapshot) -> None:
    coverage = snapshot.coverage
    st.subheader("Historical evidence coverage")
    first = st.columns(4)
    first[0].metric("Packages", coverage.packages)
    first[1].metric("League-seasons", coverage.league_seasons)
    first[2].metric("Team-seasons", coverage.team_seasons)
    first[3].metric("Draft picks", coverage.draft_picks)
    second = st.columns(4)
    second[0].metric(
        "Complete drafts",
        _coverage_label(coverage.complete_drafts, coverage.league_seasons),
    )
    second[1].metric(
        "Complete outcomes",
        _coverage_label(coverage.complete_outcomes, coverage.league_seasons),
    )
    second[2].metric(
        "Reviewed pick IDs",
        _coverage_label(coverage.resolved_draft_picks, coverage.draft_picks),
    )
    second[3].metric("Descriptive-ready leagues", coverage.analysis_ready_leagues)
    st.caption(
        f"Coverage spans {coverage.distinct_seasons:,} completed season(s) and "
        f"{coverage.rulesets:,} distinct ruleset(s). The warehouse contains "
        f"{coverage.feature_rows:,} roster-feature row(s) and "
        f"{coverage.draft_metric_rows:,} ready drafted-only metric row(s)."
    )


def _render_team_results(snapshot: LeagueHistorySnapshot) -> None:
    st.subheader("Pseudonymous team results")
    st.caption(
        "These are imported historical labels and drafted-player descriptions, not predictions. "
        "Drafted-only optimal points exclude waivers, trades, and manager start/sit decisions."
    )
    teams = _filtered_teams(snapshot.teams, key_prefix="history_results")
    if not teams:
        st.info(
            "No normalized team outcomes match the current filters. Import complete rules, "
            "draft picks, and all-team outcomes through Data Center first."
        )
        return
    st.dataframe(
        records_frame(
            {
                "Season": team.season,
                "League": team.league_season_id,
                "Team": team.team_id,
                "Record": _record(team),
                "Points for": team.points_for,
                "Made playoffs": _boolean_label(team.made_playoffs),
                "Final place": team.final_place,
                "Champion": _boolean_label(team.is_champion),
                "Draft-only status": team.draft_metric_status or "Unavailable",
                "Drafted-only optimal points": team.drafted_only_points,
                "Drafted-only percentile": team.drafted_only_percentile,
                "Reviewed pick coverage": team.mapping_coverage,
            }
            for team in teams
        ),
        hide_index=True,
        width="stretch",
        column_config={
            "Points for": st.column_config.NumberColumn(format="%.1f"),
            "Drafted-only optimal points": st.column_config.NumberColumn(format="%.1f"),
            "Drafted-only percentile": st.column_config.ProgressColumn(
                min_value=0.0,
                max_value=1.0,
                format="percent",
            ),
            "Reviewed pick coverage": st.column_config.ProgressColumn(
                min_value=0.0,
                max_value=1.0,
                format="percent",
            ),
        },
    )


def _render_roster_construction(snapshot: LeagueHistorySnapshot) -> None:
    st.subheader("Original-draft roster construction")
    st.caption(
        "These fields describe how each original draft allocated picks. Any association with "
        "standings is non-causal and must be interpreted with its team-season count."
    )
    teams = _filtered_teams(snapshot.teams, key_prefix="history_construction")
    records: list[dict[str, object]] = []
    for team in teams:
        payload = team.feature_payload
        if payload is None:
            continue
        first_round = _object_dict(payload.get("first_position_round"))
        through_round = _object_dict(payload.get("rb_wr_counts_through_round"))
        round_three = _object_dict(through_round.get("3"))
        round_five = _object_dict(through_round.get("5"))
        round_eight = _object_dict(through_round.get("8"))
        round_ten = _object_dict(through_round.get("10"))
        records.append(
            {
                "Season": team.season,
                "League": team.league_season_id,
                "Team": team.team_id,
                "Starter coverage": _optional_float(payload.get("starter_coverage")),
                "First QB round": first_round.get("QB"),
                "First RB round": first_round.get("RB"),
                "First WR round": first_round.get("WR"),
                "First TE round": first_round.get("TE"),
                "RB/WR through R3": _position_pair(round_three),
                "RB/WR through R5": _position_pair(round_five),
                "RB/WR through R8": _position_pair(round_eight),
                "RB/WR through R10": _position_pair(round_ten),
                "Position pick counts": _compact_json(payload.get("position_pick_counts")),
                "Bench depth": _compact_json(payload.get("bench_depth")),
            }
        )
    if not records:
        st.info(
            "Roster-construction features are not available for the selected teams. Validated "
            "history must be normalized and the descriptive Phase 8 build must complete first."
        )
        return
    st.dataframe(
        records_frame(records),
        hide_index=True,
        width="stretch",
        column_config={
            "Starter coverage": st.column_config.ProgressColumn(
                min_value=0.0,
                max_value=1.0,
                format="percent",
            )
        },
    )
    st.info(
        "Historical value-versus-ADP, VORP, uncertainty, and bye-week features remain unavailable "
        "unless time-valid historical sources exist. The app does not backfill them from current "
        "data."
    )


def _render_packages(snapshot: LeagueHistorySnapshot) -> None:
    st.subheader("Import packages and quality evidence")
    if not snapshot.packages:
        st.info(
            "No league-history package has been recorded. Use the v1 template and Data Center "
            "workflow described above."
        )
        return
    st.dataframe(
        records_frame(
            {
                "Imported": package.imported_at,
                "Status": package.status,
                "Schema": package.schema_version,
                "Package fingerprint": package.package_fingerprint,
                "League-seasons": package.league_count,
                "Rules rows": package.rules_rows,
                "Pick rows": package.pick_rows,
                "Outcome rows": package.outcome_rows,
                "Unresolved players": package.unresolved_player_rows,
            }
            for package in snapshot.packages
        ),
        hide_index=True,
        width="stretch",
    )
    for package in snapshot.packages:
        label = (
            f"{package.imported_at.isoformat()} · {package.status} · "
            f"{package.package_fingerprint[:16]}..."
        )
        with st.expander(label):
            render_lineage("Package", package.package_fingerprint)
            st.json(package.quality_report)
            st.download_button(
                "Download quality report JSON",
                data=json.dumps(package.quality_report, indent=2, sort_keys=True),
                file_name=f"{package.package_fingerprint[:16]}-quality-report.json",
                mime="application/json",
                key=f"history_quality_{package.package_fingerprint}",
                width="stretch",
            )


def _render_gate(snapshot: LeagueHistorySnapshot) -> None:
    gate = snapshot.gate
    st.subheader("Read-only outcome-model evidence gate")
    passed = sum(criterion.passed for criterion in gate.criteria)
    if gate.ready:
        st.info(
            "Every configured count and completeness threshold is met. This means eligible for "
            "independent data and modeling review—not trained, approved, calibrated, or available "
            "for use. This page intentionally has no training control."
        )
    else:
        st.warning(
            f"Training remains locked: {passed}/{len(gate.criteria)} configured criteria pass. "
            "No playoff or championship probability is produced."
        )

    summaries = st.columns(4)
    summaries[0].metric(
        "Points-percentile evidence",
        _gate_label(gate.points_percentile_ready),
    )
    summaries[1].metric("Playoff-label evidence", _gate_label(gate.playoff_ready))
    summaries[2].metric(
        "Championship-label evidence",
        _gate_label(gate.championship_ready),
    )
    summaries[3].metric(
        "Nonlinear-model evidence",
        _gate_label(gate.gradient_boosting_ready),
    )
    st.dataframe(
        records_frame(_criterion_record(criterion) for criterion in gate.criteria),
        hide_index=True,
        width="stretch",
        column_order=("State", "Criterion", "Actual", "Required", "Gap", "Evidence"),
    )
    render_lineage("Gate configuration", gate.config_fingerprint)
    st.caption(
        "Thresholds are necessary minimum evidence only. Representative sampling, leakage "
        "review, chronological evaluation, baseline comparisons, calibration, and cohort "
        "reliability would still be required in a later modeling phase."
    )


def _filtered_teams(
    teams: tuple[HistoryTeamSummary, ...],
    *,
    key_prefix: str,
) -> tuple[HistoryTeamSummary, ...]:
    if not teams:
        return ()
    seasons = tuple(sorted({team.season for team in teams}, reverse=True))
    selected_seasons = st.multiselect(
        "Seasons",
        seasons,
        default=seasons,
        key=f"{key_prefix}_seasons",
    )
    season_set = set(selected_seasons)
    league_options = tuple(
        sorted({team.league_season_id for team in teams if team.season in season_set})
    )
    selected_leagues = st.multiselect(
        "League-seasons",
        league_options,
        default=league_options,
        key=f"{key_prefix}_leagues",
    )
    league_set = set(selected_leagues)
    return tuple(
        team
        for team in teams
        if team.season in season_set and team.league_season_id in league_set
    )


def _criterion_record(criterion: GateCriterion) -> dict[str, object]:
    is_rate = criterion.code in _RATE_CRITERIA
    gap = max(0.0, criterion.required - criterion.actual)
    return {
        "State": "Threshold met" if criterion.passed else "Locked",
        "Criterion": criterion.label,
        "Actual": _criterion_value(criterion.actual, is_rate),
        "Required": _criterion_value(criterion.required, is_rate),
        "Gap": _criterion_value(gap, is_rate),
        "Evidence": criterion.explanation,
    }


def _criterion_value(value: float, is_rate: bool) -> str:
    return f"{value:.1%}" if is_rate else f"{int(value):,}"


def _coverage_label(numerator: int, denominator: int) -> str:
    if denominator == 0:
        return "Unavailable"
    return f"{numerator:,}/{denominator:,} ({numerator / denominator:.1%})"


def _gate_label(passed: bool) -> str:
    return "Count gate met" if passed else "Locked"


def _record(team: HistoryTeamSummary) -> str:
    if team.wins is None or team.losses is None:
        return "Unavailable"
    return f"{team.wins:g}-{team.losses:g}"


def _boolean_label(value: bool | None) -> str:
    return "Unavailable" if value is None else "Yes" if value else "No"


def _object_dict(value: object) -> dict[str, Any]:
    if not isinstance(value, dict):
        return {}
    return {str(key): item for key, item in value.items()}


def _optional_float(value: object) -> float | None:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        return None
    return float(value)


def _position_pair(value: dict[str, Any]) -> str:
    rb = value.get("RB")
    wr = value.get("WR")
    return f"RB {rb if isinstance(rb, int) else '—'} · WR {wr if isinstance(wr, int) else '—'}"


def _compact_json(value: object) -> str:
    return "Unavailable" if value is None else json.dumps(value, sort_keys=True)
