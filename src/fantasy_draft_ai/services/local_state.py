"""Scoped restoration of user-controlled app state to checked-in defaults."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import duckdb

from fantasy_draft_ai.data.warehouse import Warehouse


class LocalStateResetError(RuntimeError):
    """Raised when a local-state reset cannot prove its requested scope is empty."""


@dataclass(frozen=True)
class LocalStateSummary:
    """Counts for local setup and practice-draft state eligible for reset."""

    saved_league_setups: int
    practice_drafts: int
    recorded_picks: int
    draft_events: int
    frozen_player_rows: int
    recommendation_runs: int

    @property
    def is_empty(self) -> bool:
        """Return whether there is no resettable local state."""

        return not any(
            (
                self.saved_league_setups,
                self.practice_drafts,
                self.recorded_picks,
                self.draft_events,
                self.frozen_player_rows,
                self.recommendation_runs,
            )
        )


_LOCAL_SETUP_PREDICATE = """
user_draft_slot IS NOT NULL
AND source_dataset_id IS NULL
AND NOT EXISTS (
    SELECT 1
    FROM league_history_leagues AS history
    WHERE history.league_season_id = league_rules.league_season_id
)
"""


def preview_local_state(warehouse_path: Path) -> LocalStateSummary:
    """Return the exact state that a restore operation would remove."""

    path = warehouse_path.resolve()
    Warehouse(path).initialize()
    with duckdb.connect(str(path), read_only=True) as connection:
        return _read_summary(connection)


def restore_phase8_defaults(
    warehouse_path: Path,
    *,
    expected_summary: LocalStateSummary,
) -> LocalStateSummary:
    """Delete only local setups and practice drafts in one transaction.

    Immutable archives, canonical football data, identity decisions, market data,
    model publications, and imported league-history evidence are intentionally
    outside this operation's scope.
    """

    path = warehouse_path.resolve()
    Warehouse(path).initialize()
    with duckdb.connect(str(path)) as connection:
        connection.execute("BEGIN TRANSACTION")
        try:
            removed = _read_summary(connection)
            if removed != expected_summary:
                raise LocalStateResetError(
                    "Local testing state changed after the confirmation dialog opened. "
                    "Close it, review the refreshed counts, and confirm again."
                )
            connection.execute("DELETE FROM draft_recommendation_runs")
            connection.execute("DELETE FROM draft_events")
            connection.execute("DELETE FROM draft_session_players")
            connection.execute("DELETE FROM draft_sessions")
            connection.execute(f"DELETE FROM league_rules WHERE {_LOCAL_SETUP_PREDICATE}")
            remaining = _read_summary(connection)
            if not remaining.is_empty:
                raise LocalStateResetError(
                    "The reset transaction left resettable local state behind."
                )
            connection.execute("COMMIT")
        except Exception:
            connection.execute("ROLLBACK")
            raise
    return removed


def _read_summary(connection: duckdb.DuckDBPyConnection) -> LocalStateSummary:
    row = connection.execute(
        f"""
        SELECT
            (SELECT count(*) FROM league_rules WHERE {_LOCAL_SETUP_PREDICATE}),
            (SELECT count(*) FROM draft_sessions),
            (SELECT count(*) FROM draft_events WHERE event_type = 'pick_made'),
            (SELECT count(*) FROM draft_events),
            (SELECT count(*) FROM draft_session_players),
            (SELECT count(*) FROM draft_recommendation_runs)
        """
    ).fetchone()
    if row is None:  # pragma: no cover - aggregate query always returns one row
        raise LocalStateResetError("Local-state counts could not be read.")
    return LocalStateSummary(*(int(value) for value in row))
