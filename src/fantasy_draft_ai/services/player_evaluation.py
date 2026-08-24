"""Player-first market comparison contracts for the Player Evaluation workspace."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from math import isfinite

import duckdb

from fantasy_draft_ai.config import AppConfig
from fantasy_draft_ai.draft.pool import is_mapped_market_confidence
from fantasy_draft_ai.services.adp_market import AdpMarketBoard, AdpMarketRow
from fantasy_draft_ai.services.projections import ProjectionBoard


@dataclass(frozen=True)
class PlatformAdpSpec:
    """One intentionally labeled draft market shown in the comparison export."""

    key: str
    label: str
    format_label: str
    aliases: frozenset[str]
    scoring_formats: tuple[str, ...]
    team_count: int
    position_scope: str
    fallback_scoring_formats: tuple[str, ...] = ()
    fallback_format_label: str | None = None

    @property
    def scope_label(self) -> str:
        """Return the preferred exact warehouse scope used for this market value."""

        return self.scope_label_for(self.scoring_formats[0])

    def scope_label_for(self, scoring_format: str) -> str:
        """Return a truthful label for a selected preferred or fallback scope."""

        return (
            f"{scoring_format.replace('_', '-')} / "
            f"{self.team_count}-team / {self.position_scope}"
        )


PLATFORM_ADP_SPECS = (
    PlatformAdpSpec(
        "yahoo",
        "Yahoo",
        "FantasyPros overall ADP export",
        frozenset({"yahoo"}),
        ("overall",),
        12,
        "overall",
    ),
    PlatformAdpSpec(
        "sleeper",
        "Sleeper",
        "FantasyPros overall ADP export",
        frozenset({"sleeper"}),
        ("overall",),
        12,
        "overall",
        fallback_scoring_formats=("ppr",),
        fallback_format_label="Direct Sleeper full-PPR fallback (12-team)",
    ),
    PlatformAdpSpec(
        "rtsports",
        "RTSports",
        "FantasyPros overall ADP export",
        frozenset({"rtsports"}),
        ("overall",),
        12,
        "overall",
    ),
    PlatformAdpSpec(
        "fantasypros",
        "FantasyPros AVG",
        "FantasyPros published multi-site average",
        frozenset({"fantasypros"}),
        ("overall",),
        12,
        "overall",
    ),
)

_OFFENSIVE_ADP_POSITIONS = frozenset({"QB", "RB", "TE", "WR"})


@dataclass(frozen=True)
class PlatformCoverage:
    """Observed, canonical coverage for one configured platform."""

    key: str
    label: str
    format_label: str
    player_count: int
    latest_capture: datetime | None
    source_rows: int = 0
    snapshot_id: str | None = None
    scope_label: str = ""
    availability_message: str = ""

    @property
    def mapping_coverage(self) -> float | None:
        """Return accepted unique-player coverage of the archived source rows."""

        if self.source_rows <= 0:
            return None
        return self.player_count / self.source_rows

    @property
    def available(self) -> bool:
        """Return whether an exact-scope snapshot was found."""

        return self.snapshot_id is not None


@dataclass(frozen=True)
class PlayerAdpComparison:
    """One canonical current player and the available platform observations."""

    player_id: str
    display_name: str
    position: str
    yahoo_adp: float | None
    sleeper_adp: float | None
    rtsports_adp: float | None
    fantasypros_avg: float | None
    source_count: int

    def as_record(self) -> dict[str, object]:
        """Return stable user-facing CSV column names."""

        return {
            "Player ID": self.player_id,
            "Player": self.display_name,
            "Position": self.position,
            "Yahoo ADP": self.yahoo_adp,
            "Sleeper ADP": self.sleeper_adp,
            "RTSports ADP": self.rtsports_adp,
            "FantasyPros AVG": self.fantasypros_avg,
        }


@dataclass(frozen=True)
class PlayerExportBoard:
    """Current player universe plus truthful direct-snapshot market coverage."""

    available: bool
    message: str
    season: int | None
    rows: tuple[PlayerAdpComparison, ...] = ()
    coverage: tuple[PlatformCoverage, ...] = ()
    projection_player_count: int = 0
    market_only_player_count: int = 0

    @property
    def players_with_market_data(self) -> int:
        return sum(row.source_count > 0 for row in self.rows)

    @property
    def complete_comparisons(self) -> int:
        return sum(row.source_count == len(PLATFORM_ADP_SPECS) for row in self.rows)

    @property
    def platform_observations(self) -> int:
        return sum(row.source_count for row in self.rows)

    def records(self) -> list[dict[str, object]]:
        return [row.as_record() for row in self.rows]


@dataclass(frozen=True)
class _PlatformObservation:
    average_pick: float
    captured_at: datetime
    snapshot_id: str
    raw_source_row_id: str
    scoring_format: str


def load_player_export_board(
    config: AppConfig,
    projection_board: ProjectionBoard,
) -> PlayerExportBoard:
    """Read the latest exact-scope platform snapshots directly from DuckDB.

    This deliberately bypasses the Phase 5 derived publication. Snapshot acquisition and
    normalization happen outside Streamlit, so a page rerun performs no network requests.
    """

    season = config.project.prediction_season
    projection_players = _projection_players(projection_board, season)
    warehouse = config.resolve(config.paths.warehouse)
    if not warehouse.is_file():
        return _board_without_market(
            season,
            projection_players,
            "The ADP warehouse is not built yet.",
        )

    try:
        with duckdb.connect(str(warehouse), read_only=True) as connection:
            tables = {
                str(row[0])
                for row in connection.execute(
                    """
                    SELECT table_name
                    FROM information_schema.tables
                    WHERE table_schema = 'main'
                    """
                ).fetchall()
            }
            required = {"players", "adp_snapshots", "adp_snapshot_metadata"}
            if not required.issubset(tables):
                return _board_without_market(
                    season,
                    projection_players,
                    "The canonical ADP warehouse tables are not initialized yet.",
                )
            platform_rows, market_players, coverage = _read_latest_platform_snapshots(
                connection,
                season,
            )
    except (duckdb.Error, OSError, TypeError, ValueError) as exc:
        return _board_without_market(
            season,
            projection_players,
            f"The archived ADP snapshots could not be read safely: {exc}",
        )

    players = dict(projection_players)
    for player_id, player in market_players.items():
        players.setdefault(player_id, player)
    return _assemble_board(
        season=season,
        players=players,
        platform_rows=platform_rows,
        coverage=coverage,
        projection_player_count=len(projection_players),
        market_only_player_count=len(set(market_players) - set(projection_players)),
    )


def build_player_export_board(
    projection_board: ProjectionBoard,
    market_board: AdpMarketBoard,
) -> PlayerExportBoard:
    """Build from Phase 5 objects for backward-compatible callers and tests.

    The Streamlit Player Export page uses :func:`load_player_export_board` so newly loaded
    immutable snapshots appear before a Phase 5 baseline rebuild.
    """

    if not projection_board.available or projection_board.run is None:
        return PlayerExportBoard(
            available=False,
            message=(
                "The active projection publication is unavailable, so a current player "
                "universe cannot be built safely."
            ),
            season=None,
        )

    season = projection_board.run.prediction_season
    players = _projection_players(projection_board, season)
    platform_rows = _latest_platform_rows(market_board.rows)
    coverage = tuple(
        PlatformCoverage(
            key=spec.key,
            label=spec.label,
            format_label=_compatibility_format_label(spec, platform_rows[spec.key]),
            player_count=len(platform_rows[spec.key]),
            latest_capture=max(
                (row.captured_at for row in platform_rows[spec.key].values()),
                default=None,
            ),
            source_rows=len(platform_rows[spec.key]),
            snapshot_id=(
                max(
                    platform_rows[spec.key].values(),
                    key=_observation_order,
                ).snapshot_id
                if platform_rows[spec.key]
                else None
            ),
            scope_label=_compatibility_scope_label(spec, platform_rows[spec.key]),
            availability_message=(
                "Loaded from the Phase 5 compatibility board."
                if platform_rows[spec.key]
                else f"No {spec.scope_label} snapshot is available."
            ),
        )
        for spec in PLATFORM_ADP_SPECS
    )
    return _assemble_board(
        season=season,
        players=players,
        platform_rows=platform_rows,
        coverage=coverage,
        projection_player_count=len(players),
        market_only_player_count=0,
    )


def _projection_players(
    projection_board: ProjectionBoard,
    season: int,
) -> dict[str, tuple[str, str]]:
    if (
        not projection_board.available
        or projection_board.run is None
        or projection_board.run.prediction_season != season
    ):
        return {}
    return {
        player.player_id: (player.display_name, player.position or "UNK")
        for player in projection_board.rows
    }


def _read_latest_platform_snapshots(
    connection: duckdb.DuckDBPyConnection,
    season: int,
) -> tuple[
    dict[str, dict[str, _PlatformObservation]],
    dict[str, tuple[str, str]],
    tuple[PlatformCoverage, ...],
]:
    by_platform: dict[str, dict[str, _PlatformObservation]] = {
        spec.key: {} for spec in PLATFORM_ADP_SPECS
    }
    market_players: dict[str, tuple[str, str]] = {}
    coverage: list[PlatformCoverage] = []
    for spec in PLATFORM_ADP_SPECS:
        metadata = _latest_metadata(connection, season, spec)
        if metadata is None:
            coverage.append(_missing_coverage(spec))
            continue
        snapshot_id, captured_at, source_rows, scoring_format = metadata
        raw_rows = connection.execute(
            """
            SELECT snapshot.player_id, player.display_name,
                   coalesce(nullif(trim(snapshot.position), ''),
                            nullif(trim(player.canonical_position), ''), 'UNK'),
                   snapshot.average_pick, snapshot.mapping_confidence,
                   snapshot.captured_at, snapshot.raw_source_row_id
            FROM adp_snapshots AS snapshot
            JOIN players AS player ON player.player_id = snapshot.player_id
            WHERE snapshot.snapshot_id = ?
              AND snapshot.player_id IS NOT NULL
              AND snapshot.average_pick IS NOT NULL
            ORDER BY snapshot.player_id, snapshot.raw_source_row_id
            """,
            [snapshot_id],
        ).fetchall()
        for raw in raw_rows:
            average_pick = float(raw[3])
            confidence = str(raw[4])
            observed_at = raw[5]
            source_position = str(raw[2]).strip().upper()
            if (
                not is_mapped_market_confidence(confidence)
                or not isfinite(average_pick)
                or average_pick <= 0
                or not isinstance(observed_at, datetime)
                or source_position not in _OFFENSIVE_ADP_POSITIONS
            ):
                continue
            player_id = str(raw[0])
            observation = _PlatformObservation(
                average_pick=average_pick,
                captured_at=observed_at,
                snapshot_id=snapshot_id,
                raw_source_row_id=str(raw[6]),
                scoring_format=scoring_format,
            )
            prior = by_platform[spec.key].get(player_id)
            if prior is None or _observation_order(observation) > _observation_order(prior):
                by_platform[spec.key][player_id] = observation
            market_players.setdefault(player_id, (str(raw[1]), source_position))
        accepted_players = len(by_platform[spec.key])
        used_fallback = scoring_format in spec.fallback_scoring_formats
        coverage.append(
            PlatformCoverage(
                key=spec.key,
                label=spec.label,
                format_label=(
                    spec.fallback_format_label
                    if used_fallback and spec.fallback_format_label is not None
                    else spec.format_label
                ),
                player_count=accepted_players,
                latest_capture=captured_at,
                source_rows=source_rows,
                snapshot_id=snapshot_id,
                scope_label=spec.scope_label_for(scoring_format),
                availability_message=(
                    f"Loaded {accepted_players:,} canonical players from the latest "
                    + (
                        "direct Sleeper full-PPR fallback because no FantasyPros "
                        "overall Sleeper snapshot is loaded."
                        if used_fallback
                        else "exact-scope FantasyPros aggregate snapshot."
                    )
                ),
            )
        )
    return by_platform, market_players, tuple(coverage)


def _latest_metadata(
    connection: duckdb.DuckDBPyConnection,
    season: int,
    spec: PlatformAdpSpec,
) -> tuple[str, datetime, int, str] | None:
    preferred = _latest_metadata_for_formats(
        connection,
        season,
        spec,
        spec.scoring_formats,
    )
    if preferred is not None or not spec.fallback_scoring_formats:
        return preferred
    return _latest_metadata_for_formats(
        connection,
        season,
        spec,
        spec.fallback_scoring_formats,
    )


def _latest_metadata_for_formats(
    connection: duckdb.DuckDBPyConnection,
    season: int,
    spec: PlatformAdpSpec,
    scoring_formats: tuple[str, ...],
) -> tuple[str, datetime, int, str] | None:
    source_placeholders = ", ".join("?" for _ in spec.aliases)
    format_placeholders = ", ".join("?" for _ in scoring_formats)
    parameters: list[object] = [
        season,
        spec.team_count,
        spec.position_scope,
        *sorted(spec.aliases),
        *scoring_formats,
    ]
    row = connection.execute(
        f"""
        SELECT snapshot_id, captured_at, row_count, lower(trim(scoring_format))
        FROM adp_snapshot_metadata
        WHERE season = ?
          AND team_count = ?
          AND lower(trim(position_scope)) = ?
          AND lower(trim(source)) IN ({source_placeholders})
          AND lower(trim(scoring_format)) IN ({format_placeholders})
        ORDER BY captured_at DESC, loaded_at DESC, snapshot_id DESC
        LIMIT 1
        """,
        parameters,
    ).fetchone()
    if row is None:
        return None
    captured_at = row[1]
    if not isinstance(captured_at, datetime):
        raise ValueError(f"{spec.label} captured_at is not a timestamp.")
    return str(row[0]), captured_at, int(row[2]), str(row[3])


def _missing_coverage(spec: PlatformAdpSpec) -> PlatformCoverage:
    return PlatformCoverage(
        key=spec.key,
        label=spec.label,
        format_label=spec.format_label,
        player_count=0,
        latest_capture=None,
        source_rows=0,
        snapshot_id=None,
        scope_label=spec.scope_label,
        availability_message=f"No {spec.scope_label} snapshot is loaded for this season.",
    )


def _board_without_market(
    season: int,
    projection_players: dict[str, tuple[str, str]],
    reason: str,
) -> PlayerExportBoard:
    coverage = tuple(_missing_coverage(spec) for spec in PLATFORM_ADP_SPECS)
    if not projection_players:
        return PlayerExportBoard(
            available=False,
            message=(
                f"{reason} The current projection publication is also unavailable, so "
                "there is no safe current-player universe to show."
            ),
            season=season,
            coverage=coverage,
        )
    return _assemble_board(
        season=season,
        players=projection_players,
        platform_rows={spec.key: {} for spec in PLATFORM_ADP_SPECS},
        coverage=coverage,
        projection_player_count=len(projection_players),
        market_only_player_count=0,
        market_issue=reason,
    )


def _assemble_board(
    *,
    season: int,
    players: dict[str, tuple[str, str]],
    platform_rows: dict[str, dict[str, _PlatformObservation]],
    coverage: tuple[PlatformCoverage, ...],
    projection_player_count: int,
    market_only_player_count: int,
    market_issue: str | None = None,
) -> PlayerExportBoard:
    comparisons = tuple(
        _comparison_for_player(player_id, display_name, position, platform_rows)
        for player_id, (display_name, position) in players.items()
    )
    ordered = tuple(
        sorted(
            comparisons,
            key=lambda row: (
                row.fantasypros_avg is None,
                row.fantasypros_avg if row.fantasypros_avg is not None else float("inf"),
                row.display_name.casefold(),
                row.player_id,
            ),
        )
    )
    market_count = sum(row.source_count > 0 for row in ordered)
    missing = [item.label for item in coverage if not item.available]
    if market_issue is not None:
        message = (
            f"{market_issue} All {len(ordered):,} current player rows remain visible, and "
            "market values remain blank."
        )
    elif market_count:
        message = (
            f"{market_count:,} of {len(ordered):,} current players have at least one "
            "accepted platform ADP from the latest archived exact-scope snapshots."
        )
        if missing:
            message += f" Not loaded: {', '.join(missing)}."
    else:
        message = (
            "No accepted Yahoo, Sleeper, RTSports, or FantasyPros AVG observations are "
            "loaded for the configured scopes. Current player rows remain visible and "
            "market values remain blank."
        )
    return PlayerExportBoard(
        available=bool(ordered),
        message=message,
        season=season,
        rows=ordered,
        coverage=coverage,
        projection_player_count=projection_player_count,
        market_only_player_count=market_only_player_count,
    )


def _latest_platform_rows(
    rows: tuple[AdpMarketRow, ...],
) -> dict[str, dict[str, _PlatformObservation]]:
    preferred: dict[str, dict[str, _PlatformObservation]] = {
        spec.key: {} for spec in PLATFORM_ADP_SPECS
    }
    fallback: dict[str, dict[str, _PlatformObservation]] = {
        spec.key: {} for spec in PLATFORM_ADP_SPECS
    }
    alias_to_spec = {
        alias.casefold(): spec for spec in PLATFORM_ADP_SPECS for alias in spec.aliases
    }
    for row in rows:
        spec = alias_to_spec.get(row.source.strip().casefold())
        player_id = row.identity.player_id
        scope_kind = _market_row_scope_kind(row, spec) if spec is not None else None
        if (
            spec is None
            or player_id is None
            or not is_mapped_market_confidence(row.mapping_confidence)
            or scope_kind is None
        ):
            continue
        scoring_format = str(getattr(row, "scoring_format", spec.scoring_formats[0])).casefold()
        observation = _PlatformObservation(
            average_pick=row.average_pick,
            captured_at=row.captured_at,
            snapshot_id=row.snapshot_id,
            raw_source_row_id=row.raw_source_row_id,
            scoring_format=scoring_format,
        )
        destination = preferred if scope_kind == "preferred" else fallback
        prior = destination[spec.key].get(player_id)
        if prior is None or _observation_order(observation) > _observation_order(prior):
            destination[spec.key][player_id] = observation
    return {
        spec.key: preferred[spec.key] or fallback[spec.key] for spec in PLATFORM_ADP_SPECS
    }


def _market_row_scope_kind(
    row: AdpMarketRow,
    spec: PlatformAdpSpec,
) -> str | None:
    scoring_format = getattr(row, "scoring_format", None)
    team_count = getattr(row, "team_count", None)
    if team_count is not None and int(team_count) != spec.team_count:
        return None
    if scoring_format is None or str(scoring_format).casefold() in spec.scoring_formats:
        return "preferred"
    if str(scoring_format).casefold() in spec.fallback_scoring_formats:
        return "fallback"
    return None


def _compatibility_format_label(
    spec: PlatformAdpSpec,
    rows: dict[str, _PlatformObservation],
) -> str:
    if rows and next(iter(rows.values())).scoring_format in spec.fallback_scoring_formats:
        return spec.fallback_format_label or spec.format_label
    return spec.format_label


def _compatibility_scope_label(
    spec: PlatformAdpSpec,
    rows: dict[str, _PlatformObservation],
) -> str:
    scoring_format = (
        next(iter(rows.values())).scoring_format if rows else spec.scoring_formats[0]
    )
    return spec.scope_label_for(scoring_format)


def _observation_order(row: _PlatformObservation) -> tuple[datetime, str, str]:
    return row.captured_at, row.snapshot_id, row.raw_source_row_id


def _comparison_for_player(
    player_id: str,
    display_name: str,
    position: str,
    platform_rows: dict[str, dict[str, _PlatformObservation]],
) -> PlayerAdpComparison:
    values = {
        spec.key: (
            platform_rows[spec.key][player_id].average_pick
            if player_id in platform_rows[spec.key]
            else None
        )
        for spec in PLATFORM_ADP_SPECS
    }
    observed = [value for value in values.values() if value is not None]
    return PlayerAdpComparison(
        player_id=player_id,
        display_name=display_name,
        position=position,
        yahoo_adp=values["yahoo"],
        sleeper_adp=values["sleeper"],
        rtsports_adp=values["rtsports"],
        fantasypros_avg=values["fantasypros"],
        source_count=len(observed),
    )
