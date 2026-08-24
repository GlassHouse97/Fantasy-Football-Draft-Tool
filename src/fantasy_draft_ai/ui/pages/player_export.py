"""Simple player-first multi-platform ADP export."""

from __future__ import annotations

from collections.abc import Iterable, Mapping
from math import isfinite
from typing import Any

import duckdb
import pandas as pd
import streamlit as st

from fantasy_draft_ai.config import AppConfig
from fantasy_draft_ai.data.fantasypros_upload import (
    FantasyProsUploadValidationError,
    import_fantasypros_adp_upload,
)
from fantasy_draft_ai.recommendations.projection_baseline import build_projection_rankings
from fantasy_draft_ai.rules.models import LeagueRules
from fantasy_draft_ai.services.player_evaluation import (
    PlayerAdpComparison,
    PlayerExportBoard,
    load_player_export_board,
)
from fantasy_draft_ai.services.projections import ProjectionBoard
from fantasy_draft_ai.ui.common import (
    position_cell_style,
    render_page_header,
    render_section_header,
)
from fantasy_draft_ai.ui.context import AppContext, load_app_context
from fantasy_draft_ai.ui.redraft_presets import (
    DEFAULT_REDRAFT_PRESET_KEY,
    redraft_preset,
    rules_for_redraft_preset,
)

EXTREME_RANK_DISAGREEMENT_THRESHOLD = 12


def render() -> None:
    """Render the downloadable FantasyPros market comparison."""

    context = load_app_context()
    warehouse_path = context.config.resolve(context.config.paths.warehouse)
    try:
        warehouse_stat = warehouse_path.stat()
        warehouse_version = (warehouse_stat.st_mtime_ns, warehouse_stat.st_size)
    except OSError:
        warehouse_version = (0, 0)
    board = _cached_player_export_board(
        str(warehouse_path),
        *warehouse_version,
        context.config.project.prediction_season,
        _config=context.config,
        _projection_board=context.projection_board,
    )
    render_page_header(
        "Player Export List",
        "Compare the draft market",
        "Use FantasyPros AVG as the primary consensus order, then compare Yahoo, "
        "Sleeper, RT Sports, and the experimental model in one player-first table.",
    )

    if not board.available:
        st.error(board.message, icon=":material/error:")
        _render_fantasypros_upload(context.config)
        return

    metric_columns = st.columns(4)
    metric_columns[0].metric("Players", f"{len(board.rows):,}")
    metric_columns[1].metric("With market data", f"{board.players_with_market_data:,}")
    metric_columns[2].metric("Platform observations", f"{board.platform_observations:,}")
    metric_columns[3].metric("Complete 4-source rows", f"{board.complete_comparisons:,}")

    all_platforms_loaded = all(item.available for item in board.coverage)
    if board.players_with_market_data and all_platforms_loaded:
        st.success(board.message, icon=":material/check_circle:")
    elif board.players_with_market_data:
        st.warning(board.message, icon=":material/database_off:")
    else:
        st.warning(board.message, icon=":material/database_off:")

    with (
        st.container(border=True),
        st.container(
            horizontal=True,
            vertical_alignment="bottom",
        ),
    ):
        search = st.text_input(
            "Search players",
            placeholder="Type a player name",
            icon=":material/search:",
            key="player_export_search",
            width="stretch",
        )
        all_positions = sorted({row.position for row in board.rows})
        selected_positions = st.multiselect(
            "Positions",
            all_positions,
            default=all_positions,
            key="player_export_positions",
            width=320,
        )

    normalized_search = search.strip().casefold()
    experimental_model_rankings = _experimental_model_rankings(
        context,
        warehouse_path=str(warehouse_path),
        warehouse_mtime_ns=warehouse_version[0],
        warehouse_size=warehouse_version[1],
    )
    filtered_rows = [
        row
        for row in board.rows
        if row.position in selected_positions and normalized_search in row.display_name.casefold()
    ]
    frame = _player_export_frame(
        filtered_rows,
        experimental_model_rankings,
        consensus_rankings=_consensus_rankings(board.rows),
    )
    extreme_disagreements = _extreme_rank_disagreements(frame)

    render_section_header(
        "Market comparison",
        "Consensus Rank comes from FantasyPros AVG and controls the default order. "
        "Experimental Model Rank uses a health-neutral 17-game PPG projection and remains "
        "experimental. Model vs Market Delta equals consensus rank minus model rank, so a "
        "positive number means the model likes the player more. Missing values stay blank—"
        "never zero.",
        icon=":material/compare_arrows:",
    )
    if extreme_disagreements:
        st.warning(
            f"{len(extreme_disagreements):,} players in the current table differ by at "
            f"least {EXTREME_RANK_DISAGREEMENT_THRESHOLD} ranks between market consensus "
            "and the experimental model. Treat these as review flags, not automatic reasons "
            "to ignore the market.",
            icon=":material/warning:",
        )
    if frame.empty:
        st.info(
            "No players match those filters. Clear the search or select another position.",
            icon=":material/search_off:",
        )
    else:
        display_frame = frame.drop(columns=["Player ID"])
        st.dataframe(
            display_frame.style.map(position_cell_style, subset=["Position"]),
            hide_index=True,
            width="stretch",
            height=650,
            row_height=40,
            column_config=_column_config(),
        )

    st.download_button(
        "Download player ADP CSV",
        data=frame.to_csv(index=False).encode("utf-8"),
        file_name=f"player_adp_comparison_{board.season}.csv",
        mime="text/csv",
        icon=":material/download:",
        disabled=frame.empty,
        width="content",
    )
    st.caption(
        f"Player universe: {board.projection_player_count:,} players from the {board.season} "
        f"validated projection board plus {board.market_only_player_count:,} additional "
        "canonical players mapped in current-season ADP. Historical players with neither "
        "signal are excluded. FantasyPros AVG is the composite supplied in the uploaded "
        "FantasyPros export; it is not recalculated by this app. Consensus Rank is derived "
        "by sorting that AVG from earliest to latest, with tied AVG values sharing a rank. "
        "The Experimental Model Rank assumes every player is available for 17 games, scales "
        "its predicted PPG to a season total, and applies the default 12-team full-PPR "
        "replacement-value rules. It is a secondary experimental signal, not the consensus."
    )

    with st.expander("Platform coverage and format notes", icon=":material/info:"):
        coverage_records = [
            {
                "Platform": item.label,
                "Status": "Loaded" if item.available else "Not loaded",
                "Draft format": item.format_label,
                "Warehouse scope": item.scope_label,
                "Archived rows": item.source_rows,
                "Accepted mapped players": item.player_count,
                "Identity coverage": item.mapping_coverage,
                "Latest capture": (
                    item.latest_capture.isoformat() if item.latest_capture is not None else "—"
                ),
                "Note": item.availability_message,
            }
            for item in board.coverage
        ]
        st.dataframe(
            coverage_records,
            hide_index=True,
            width="stretch",
            column_config={
                "Identity coverage": st.column_config.NumberColumn(format="percent"),
                "Archived rows": st.column_config.NumberColumn(format="%d"),
                "Accepted mapped players": st.column_config.NumberColumn(format="%d"),
            },
        )
        st.warning(
            "This is a broad overall-draft market view, not a scoring-normalized "
            "comparison. Platform settings and league defaults can still differ."
        )
        st.write(
            "A platform value appears only after a current exact-scope snapshot is archived "
            "and linked to the canonical player with exact, high-confidence, or reviewed "
            "identity evidence. Display-name matching alone never fills a value. This page "
            "only reads local DuckDB snapshots; it never makes network calls during reruns."
        )

    _render_fantasypros_upload(context.config)


def _render_upload_feedback() -> None:
    feedback = st.session_state.pop("player_export_upload_feedback", None)
    if not isinstance(feedback, dict):
        return
    message = str(feedback.get("message") or "ADP upload finished.")
    if feedback.get("succeeded") is True:
        st.success(message, icon=":material/check_circle:")
    else:
        st.error(message, icon=":material/error:")
    details = feedback.get("details")
    if isinstance(details, str) and details:
        st.caption(details)


def _render_fantasypros_upload(config: AppConfig) -> None:
    generation = int(st.session_state.get("player_export_upload_generation", 0))
    with st.container(border=True):
        render_section_header(
            "Update market data",
            "Upload the FantasyPros Overall ADP CSV exported from your account. The app "
            "recognizes the columns automatically.",
            icon=":material/upload_file:",
        )
        _render_upload_feedback()

        uploaded = st.file_uploader(
            "Upload FantasyPros ADP CSV",
            type=("csv",),
            key=f"player_export_fantasypros_file_{generation}",
            max_upload_size=10,
            help=(
                "Expected FantasyPros columns: Rank, Player (Bye), POS, Yahoo, Sleeper, "
                "RTSports, and AVG. Real-Time may also be present and is ignored."
            ),
        )
        if uploaded is None:
            st.caption(
                "Expected columns: Rank, Player (Bye), POS, Yahoo, Sleeper, RTSports, and "
                "AVG. Real-Time may also be present and is ignored. Your original export "
                "is archived unchanged."
            )
            return

        content = uploaded.getvalue()
        try:
            with st.spinner("Validating and loading FantasyPros ADP…"):
                result = import_fantasypros_adp_upload(
                    config,
                    content,
                    file_name=uploaded.name,
                )
            if not result.committed:
                raise FantasyProsUploadValidationError(
                    "The warehouse rejected one or more FantasyPros platform snapshots."
                )
        except (
            FantasyProsUploadValidationError,
            duckdb.Error,
            OSError,
            RuntimeError,
            ValueError,
        ) as exc:
            st.error("The FantasyPros export was not loaded.", icon=":material/error:")
            st.caption(str(exc))
            return
        else:
            source_counts = ", ".join(
                f"{_SOURCE_LABELS[summary.source]}: {summary.rows:,}"
                for summary in result.source_summaries
            )
            mapped = sum(summary.mapped for summary in result.source_summaries)
            unresolved = sum(summary.unresolved for summary in result.source_summaries)
            reuse_note = (
                " The existing immutable archive was reused."
                if result.reused_archive
                else ""
            )
            st.session_state["player_export_upload_feedback"] = {
                "succeeded": True,
                "message": "FantasyPros market data loaded successfully.",
                "details": (
                    f"{source_counts}. {mapped:,} source rows mapped; "
                    f"{unresolved:,} remain unresolved."
                    f"{reuse_note}"
                ),
            }
            st.session_state["player_export_upload_generation"] = generation + 1
            _cached_player_export_board.clear()
        st.rerun()


def _experimental_model_rankings(
    context: AppContext,
    *,
    warehouse_path: str,
    warehouse_mtime_ns: int,
    warehouse_size: int,
) -> dict[str, int]:
    """Return the cached experimental pre-draft ordering used by Draft Assistant."""

    rules = _default_draft_helper_rules(context.reference_rules)
    return _cached_experimental_model_rankings(
        warehouse_path,
        warehouse_mtime_ns,
        warehouse_size,
        rules.fingerprint(),
        _context=context,
        _rules=rules,
    )


def _default_draft_helper_rules(reference_rules: LeagueRules) -> LeagueRules:
    """Apply the same standard roster preset used by Draft Assistant quick start."""

    return rules_for_redraft_preset(
        reference_rules,
        team_count=reference_rules.teams,
        preset=redraft_preset(DEFAULT_REDRAFT_PRESET_KEY),
    )


@st.cache_data(max_entries=8, show_spinner=False)
def _cached_experimental_model_rankings(
    warehouse_path: str,
    warehouse_mtime_ns: int,
    warehouse_size: int,
    rules_fingerprint: str,
    *,
    _context: AppContext,
    _rules: LeagueRules,
) -> dict[str, int]:
    """Cache one model rank map until its warehouse or league rules change."""

    del warehouse_path, warehouse_mtime_ns, warehouse_size, rules_fingerprint
    preparation = _context.prepare_draft(_rules)
    if not preparation.readiness.state_ready:
        return {}
    return {
        row.player_id: row.overall_rank
        for row in build_projection_rankings(_rules, preparation.players)
    }


def _player_export_frame(
    rows: Iterable[PlayerAdpComparison],
    experimental_model_rankings: Mapping[str, int],
    *,
    consensus_rankings: Mapping[str, int] | None = None,
) -> pd.DataFrame:
    """Build the consensus-first export with nullable model comparisons."""

    materialized_rows = tuple(rows)
    effective_consensus_rankings = (
        _consensus_rankings(materialized_rows)
        if consensus_rankings is None
        else consensus_rankings
    )
    ordered_rows = sorted(materialized_rows, key=_consensus_sort_key)
    records = [
        {
            **row.as_record(),
            "Consensus Rank": effective_consensus_rankings.get(row.player_id),
            "Experimental Model Rank": experimental_model_rankings.get(row.player_id),
            "Model vs Market Delta": _model_vs_market_delta(
                effective_consensus_rankings.get(row.player_id),
                experimental_model_rankings.get(row.player_id),
            ),
        }
        for row in ordered_rows
    ]
    frame = pd.DataFrame.from_records(records, columns=_EXPORT_COLUMNS)
    frame["Consensus Rank"] = pd.array(
        [effective_consensus_rankings.get(row.player_id) for row in ordered_rows],
        dtype="Int64",
    )
    frame["Experimental Model Rank"] = pd.array(
        [experimental_model_rankings.get(row.player_id) for row in ordered_rows],
        dtype="Int64",
    )
    frame["Model vs Market Delta"] = pd.array(
        [
            _model_vs_market_delta(
                effective_consensus_rankings.get(row.player_id),
                experimental_model_rankings.get(row.player_id),
            )
            for row in ordered_rows
        ],
        dtype="Int64",
    )
    return frame


def _consensus_rankings(rows: Iterable[PlayerAdpComparison]) -> dict[str, int]:
    """Rank usable FantasyPros AVG values, sharing ranks for exact ADP ties."""

    ranked_rows = sorted(
        (row for row in rows if _is_usable_adp(row.fantasypros_avg)),
        key=_consensus_sort_key,
    )
    rankings: dict[str, int] = {}
    prior_adp: float | None = None
    prior_rank = 0
    for ordinal, row in enumerate(ranked_rows, start=1):
        current_adp = row.fantasypros_avg
        if current_adp is None:  # defensive narrowing; filtered above
            continue
        if prior_adp is None or current_adp != prior_adp:
            prior_rank = ordinal
            prior_adp = current_adp
        rankings[row.player_id] = prior_rank
    return rankings


def _consensus_sort_key(row: PlayerAdpComparison) -> tuple[int, float, str, str]:
    """Put known FantasyPros AVG values first with deterministic tie ordering."""

    average_pick = row.fantasypros_avg
    if average_pick is None or not _is_usable_adp(average_pick):
        return (1, float("inf"), row.display_name.casefold(), row.player_id)
    return (0, average_pick, row.display_name.casefold(), row.player_id)


def _is_usable_adp(value: float | None) -> bool:
    """Return whether an ADP can truthfully produce a consensus rank."""

    return value is not None and isfinite(value) and value > 0


def _model_vs_market_delta(
    consensus_rank: int | None,
    experimental_model_rank: int | None,
) -> int | None:
    """Return consensus minus model rank; positive means the model is higher."""

    if consensus_rank is None or experimental_model_rank is None:
        return None
    return consensus_rank - experimental_model_rank


def _extreme_rank_disagreements(
    frame: pd.DataFrame,
    *,
    threshold: int = EXTREME_RANK_DISAGREEMENT_THRESHOLD,
) -> tuple[tuple[str, int], ...]:
    """Return deterministic player/delta flags at or beyond ``threshold`` ranks."""

    if threshold <= 0:
        raise ValueError("Rank-disagreement threshold must be positive.")
    if frame.empty:
        return ()

    flags = [
        (str(row["Player"]), int(row["Model vs Market Delta"]))
        for _, row in frame.iterrows()
        if not pd.isna(row["Model vs Market Delta"])
        and abs(int(row["Model vs Market Delta"])) >= threshold
    ]
    return tuple(sorted(flags, key=lambda item: (-abs(item[1]), item[0].casefold())))


_SOURCE_LABELS = {
    "yahoo": "Yahoo",
    "sleeper": "Sleeper",
    "rtsports": "RT Sports",
    "fantasypros": "FantasyPros AVG",
}


_EXPORT_COLUMNS = (
    "Player ID",
    "Consensus Rank",
    "Player",
    "Position",
    "Experimental Model Rank",
    "Model vs Market Delta",
    "Yahoo ADP",
    "Sleeper ADP",
    "RTSports ADP",
    "FantasyPros AVG",
)


def _column_config() -> dict[str, Any]:
    return {
        "Consensus Rank": st.column_config.NumberColumn(
            format="#%d",
            pinned=True,
            width="small",
            help=(
                "Primary market rank derived by sorting FantasyPros AVG from earliest to "
                "latest. Tied AVG values share a rank; missing AVG stays blank."
            ),
        ),
        "Player": st.column_config.TextColumn(pinned=True, width="medium"),
        "Position": st.column_config.TextColumn(width="small"),
        "Experimental Model Rank": st.column_config.NumberColumn(
            format="#%d",
            width="small",
            help=(
                "Secondary experimental rank from health-neutral predicted PPG scaled to "
                "17 games, then evaluated under default 12-team full-PPR replacement value."
            ),
        ),
        "Model vs Market Delta": st.column_config.NumberColumn(
            format="%+d",
            width="small",
            help=(
                "Consensus Rank minus Experimental Model Rank. Positive means the model "
                "likes the player more than the market; negative means it likes them less."
            ),
        ),
        "Yahoo ADP": st.column_config.NumberColumn(format="%.1f"),
        "Sleeper ADP": st.column_config.NumberColumn(format="%.1f"),
        "RTSports ADP": st.column_config.NumberColumn(format="%.1f"),
        "FantasyPros AVG": st.column_config.NumberColumn(format="%.1f"),
    }


@st.cache_data(max_entries=8, show_spinner=False)
def _cached_player_export_board(
    warehouse_path: str,
    warehouse_mtime_ns: int,
    warehouse_size: int,
    season: int,
    *,
    _config: AppConfig,
    _projection_board: ProjectionBoard,
) -> PlayerExportBoard:
    """Cache one local read until the warehouse file version changes."""

    del warehouse_path, warehouse_mtime_ns, warehouse_size, season
    return load_player_export_board(_config, _projection_board)
