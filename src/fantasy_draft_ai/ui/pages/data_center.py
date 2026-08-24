"""Data Center page for immutable archives, inventory, and quality evidence."""

from __future__ import annotations

import io
import tempfile
import zipfile
from pathlib import Path

import streamlit as st

from fantasy_draft_ai.services.data_center import (
    DataCenterSnapshot,
    load_data_center,
    run_safe_data_action,
    validate_data_action_request,
)
from fantasy_draft_ai.ui.common import render_page_header
from fantasy_draft_ai.ui.context import AppContext, load_app_context


def _execute_action(
    context: AppContext,
    action_id: str,
    parameters: dict[str, object] | None = None,
) -> None:
    try:
        request = validate_data_action_request(
            context.config,
            action_id,
            parameters,
        )
        result = run_safe_data_action(context.config, request)
        st.session_state["data_center_feedback"] = {
            "succeeded": result.succeeded,
            "message": result.message,
            "paths": list(result.artifact_paths),
            "records": result.records,
            "reused_offline": result.reused_offline,
        }
    except (OSError, RuntimeError, TypeError, ValueError) as exc:
        st.session_state["data_center_feedback"] = {
            "succeeded": False,
            "message": str(exc),
            "paths": [],
            "records": None,
            "reused_offline": False,
        }
    st.rerun()


def _render_feedback() -> None:
    value = st.session_state.pop("data_center_feedback", None)
    if not isinstance(value, dict):
        return
    message = str(value.get("message", "Data action completed."))
    if value.get("succeeded") is True:
        st.success(message)
    else:
        st.error(message)
    records = value.get("records")
    if isinstance(records, int):
        st.caption(f"Validated rows: {records:,}")
    if value.get("reused_offline") is True:
        st.info("The exact existing immutable archive was reused in offline mode.")
    paths = value.get("paths")
    if isinstance(paths, list) and paths:
        with st.expander("Artifacts written"):
            for path in paths:
                st.code(str(path), language=None)


def _render_inventory(snapshot: DataCenterSnapshot) -> None:
    st.subheader("Source inventory")
    st.dataframe(
        [source.as_dict() for source in snapshot.sources],
        hide_index=True,
        width="stretch",
        column_config={
            "fully_verified": st.column_config.CheckboxColumn("Verified"),
            "latest_acquired_at": st.column_config.DatetimeColumn("Latest archive"),
        },
    )
    st.subheader("Canonical warehouse")
    if not snapshot.warehouse.readable:
        st.error(snapshot.warehouse.issue or "The warehouse is not readable.")
    st.dataframe(
        [table.as_dict() for table in snapshot.warehouse.tables],
        hide_index=True,
        width="stretch",
        column_config={"row_count": st.column_config.NumberColumn("Rows", format="%d")},
    )
    with st.expander("Immutable manifests and files"):
        st.dataframe(
            [
                {
                    "Dataset": manifest.dataset_id,
                    "Source": manifest.source,
                    "Seasons": ", ".join(str(year) for year in manifest.seasons),
                    "Acquired": manifest.acquired_at,
                    "Verified files": f"{manifest.verified_files}/{len(manifest.files)}",
                    "Valid": manifest.valid,
                    "Manifest": manifest.manifest_path,
                    "Issues": "; ".join(manifest.issues),
                }
                for manifest in snapshot.manifests
            ],
            hide_index=True,
            width="stretch",
        )
        file_rows = [
            {"Dataset": manifest.dataset_id, **file.as_dict()}
            for manifest in snapshot.manifests
            for file in manifest.files
        ]
        st.dataframe(file_rows, hide_index=True, width="stretch")


def _render_quality(context: AppContext, snapshot: DataCenterSnapshot) -> None:
    st.subheader("Quality report")
    quality = snapshot.quality
    one, two, three = st.columns(3)
    one.metric("Audit", quality.status.title())
    two.metric("Manifests", quality.manifest_count)
    three.metric("Verified raw files", quality.verified_files)
    if quality.passed:
        st.success("Manifest hashes and canonical warehouse checks pass.")
    elif quality.failures:
        for issue in quality.failures:
            st.error(issue)
    else:
        st.info("The quality audit is not available yet.")
    action_one, action_two = st.columns(2)
    if action_one.button("Run read-only audit", width="stretch"):
        _execute_action(context, "audit")
    if action_two.button("Initialize or migrate warehouse", width="stretch"):
        _execute_action(context, "initialize_warehouse")


def _render_nflverse_actions(context: AppContext) -> None:
    st.subheader("Archive nflverse data")
    st.caption(
        "Downloads create timestamped raw files and manifests. Existing raw archives are never "
        "overwritten. Loading canonical tables remains a deliberate CLI quality-gated step."
    )
    with st.form("archive_nflverse"):
        one, two, three = st.columns(3)
        start = int(
            one.number_input(
                "Start season",
                1999,
                context.config.project.prediction_season,
                context.config.training.start_season,
            )
        )
        end = int(
            two.number_input(
                "End season",
                start,
                context.config.project.prediction_season,
                context.config.training.end_season,
            )
        )
        offline = three.checkbox(
            "Offline reuse only",
            help="Require the exact archived request to exist; do not use the network.",
        )
        submitted = st.form_submit_button("Archive players and weekly stats", type="primary")
    if submitted:
        _execute_action(
            context,
            "download_nflverse",
            {"start_season": start, "end_season": end, "offline": offline},
        )
    with st.form("archive_snap_counts"):
        one, two, three = st.columns(3)
        snap_start = int(
            one.number_input(
                "Snap-count start",
                2012,
                context.config.project.prediction_season,
                max(2012, context.config.training.start_season),
            )
        )
        snap_end = int(
            two.number_input(
                "Snap-count end",
                snap_start,
                context.config.project.prediction_season,
                context.config.training.end_season,
            )
        )
        snap_offline = three.checkbox("Offline snap-count reuse only")
        snap_submitted = st.form_submit_button("Archive snap counts")
    if snap_submitted:
        _execute_action(
            context,
            "download_nflverse_snap_counts",
            {
                "start_season": snap_start,
                "end_season": snap_end,
                "offline": snap_offline,
            },
        )


def _render_adp_actions(context: AppContext) -> None:
    st.subheader("Archive market data")
    with st.form("archive_ffc"):
        one, two, three, four = st.columns(4)
        season = int(
            one.number_input(
                "FFC season",
                2007,
                context.config.project.prediction_season,
                context.config.project.prediction_season,
            )
        )
        scoring_format = two.selectbox("Scoring format", ("ppr", "half-ppr", "standard", "2-qb"))
        teams = int(three.number_input("Teams", 4, 32, 12))
        position = four.selectbox("Position", ("All", "QB", "RB", "WR", "TE", "PK", "DEF"))
        ffc_offline = st.checkbox("Offline FFC reuse only")
        submitted = st.form_submit_button("Archive FFC ADP", type="primary")
    if submitted:
        parameters: dict[str, object] = {
            "season": season,
            "scoring_format": scoring_format,
            "teams": teams,
            "offline": ffc_offline,
        }
        if position != "All":
            parameters["position"] = position
        _execute_action(context, "snapshot_ffc_adp", parameters)

    st.info(
        "To update Yahoo, Sleeper, RT Sports, and FantasyPros AVG, export the Overall ADP "
        "CSV from your FantasyPros account and open Player Evaluation → Player Export List. "
        "The single uploader at the bottom recognizes Rank, Player (Bye), POS, Yahoo, "
        "Sleeper, RTSports, and AVG, then validates and imports the file locally. The "
        "optional Real-Time column is ignored. FantasyPros credentials and cookies are "
        "never stored.",
        icon=":material/upload_file:",
    )


def _render_league_imports(context: AppContext, snapshot: DataCenterSnapshot) -> None:
    st.subheader("League imports")
    st.text_input(
        "Sleeper league ID",
        placeholder="Not connected yet",
        disabled=True,
        help="Sleeper import is explicitly unavailable; no league data is simulated.",
    )
    template_root = context.config.project_root / "data" / "templates" / "league_history_v1"
    if template_root.is_dir():
        st.download_button(
            "Download league-history-v1 template",
            data=_template_bundle_bytes(template_root),
            file_name="league-history-v1-template.zip",
            mime="application/zip",
            width="stretch",
        )
    history_package = st.file_uploader(
        "Manual league-history-v1 ZIP",
        type=("zip",),
        help=(
            "The original ZIP is archived first, then inspected in memory, validated, and "
            "loaded transactionally only if every fatal check passes. Remove personal "
            "identifiers before selecting it."
        ),
    )
    if st.button(
        "Archive, validate, and import history",
        type="primary",
        disabled=history_package is None,
    ):
        if history_package is None:
            return
        suffix = Path(history_package.name).suffix.casefold()
        temporary_path: Path | None = None
        try:
            with tempfile.NamedTemporaryFile(suffix=suffix, delete=False) as handle:
                handle.write(history_package.getvalue())
                temporary_path = Path(handle.name)
            _execute_action(context, "league_history_import", {"path": temporary_path})
        finally:
            if temporary_path is not None:
                temporary_path.unlink(missing_ok=True)
    st.warning(
        "Before importing personal history, replace league and team names with pseudonymous "
        "IDs. The app does not transmit this upload, but this project is inside OneDrive and "
        "Windows, OneDrive, or backup software may synchronize the archived local file."
    )
    sleeper = snapshot.action("sleeper_import")
    if sleeper is not None:
        st.info(f"**{sleeper.label}:** {sleeper.message}")
    history = snapshot.action("league_history_import")
    if history is not None:
        st.info(f"**{history.label}:** {history.message}")


def _template_bundle_bytes(template_root: Path) -> bytes:
    """Create a download-only ZIP without modifying the tracked template files."""

    output = io.BytesIO()
    with zipfile.ZipFile(output, mode="w", compression=zipfile.ZIP_DEFLATED) as package:
        for path in sorted(template_root.iterdir(), key=lambda item: item.name):
            if path.is_file() and (path.name == "package.json" or path.suffix == ".csv"):
                package.writestr(path.name, path.read_bytes())
    return output.getvalue()


def _render_action_catalog(snapshot: DataCenterSnapshot) -> None:
    with st.expander("All action capabilities and CLI handoffs"):
        st.dataframe(
            [action.as_dict() for action in snapshot.actions],
            hide_index=True,
            width="stretch",
        )
        for action in snapshot.actions:
            if action.command_hint:
                st.code(action.command_hint, language="powershell")


def render() -> None:
    """Render immutable data workflows and their quality evidence."""

    context = load_app_context()
    snapshot = load_data_center(context.config)
    render_page_header(
        "Data Center",
        "Raw stays raw",
        "Archive documented sources, inspect immutable manifests, and verify the canonical "
        "warehouse without silently overwriting evidence.",
    )
    _render_feedback()
    _render_quality(context, snapshot)
    _render_inventory(snapshot)
    st.divider()
    _render_nflverse_actions(context)
    st.divider()
    _render_adp_actions(context)
    st.divider()
    _render_league_imports(context, snapshot)
    _render_action_catalog(snapshot)
