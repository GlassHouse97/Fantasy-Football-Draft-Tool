"""Read-only Phase 5 ADP movement and next-pick availability service."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime

import duckdb

from fantasy_draft_ai.config import AppConfig
from fantasy_draft_ai.models.adp.availability import AvailabilityEstimate, estimate_availability
from fantasy_draft_ai.models.adp.build import adp_market_integrity_issues
from fantasy_draft_ai.models.adp.config import AvailabilityConfig, load_availability_config
from fantasy_draft_ai.models.adp.movement import AdpIdentity


@dataclass(frozen=True)
class AdpMarketStatus:
    """Truthful read-only availability state for the Phase 5 publication."""

    available: bool
    code: str
    message: str
    build_fingerprint: str | None = None
    snapshot_count: int = 0
    observation_rows: int = 0
    persistence_ready_rows: int = 0
    linear_ready_rows: int = 0
    ew_ready_rows: int = 0
    availability_rows: int = 0
    calibration_status: str = "unavailable"
    supervised_status: str = "unavailable"


@dataclass(frozen=True)
class AdpMarketRow:
    """One latest source observation with separate movement and availability evidence."""

    snapshot_id: str
    raw_source_row_id: str
    identity: AdpIdentity
    player_name: str
    position: str
    nfl_team: str | None
    source: str
    captured_at: datetime
    season: int
    scoring_format: str
    team_count: int
    average_pick: float
    min_pick: float | None
    max_pick: float | None
    source_standard_deviation: float | None
    sample_size: int | None
    mapping_confidence: str
    prior_average_pick: float | None
    change_7d: float | None
    velocity_per_day: float | None
    source_spread: float | None
    observation_count: int
    persistence_prediction: float | None
    linear_prediction: float | None
    linear_status: str
    exponentially_weighted_prediction: float | None
    exponentially_weighted_status: str
    availability_scale: float
    availability_evidence_method: str
    availability_fallback_group: str | None

    def estimate_availability(
        self,
        *,
        current_pick: float,
        next_pick: float,
        config: AvailabilityConfig,
    ) -> AvailabilityEstimate:
        """Condition the versioned spread rule on the player being available now."""

        return estimate_availability(
            identity=self.identity,
            position=self.position,
            average_pick=self.average_pick,
            current_pick=current_pick,
            next_pick=next_pick,
            observed_standard_deviation=self.source_standard_deviation,
            minimum_pick=self.min_pick,
            maximum_pick=self.max_pick,
            sample_size=self.sample_size,
            config=config,
        )


@dataclass(frozen=True)
class AdpMarketBoard:
    """Validated latest market rows and the assumptions used to query them."""

    status: AdpMarketStatus
    rows: tuple[AdpMarketRow, ...] = ()
    availability_config: AvailabilityConfig | None = None

    @property
    def available(self) -> bool:
        return self.status.available


def adp_market_status(config: AppConfig) -> AdpMarketStatus:
    """Inspect the persisted Phase 5 build without loading player-level rows."""

    warehouse_path = config.resolve(config.paths.warehouse)
    if not warehouse_path.exists():
        return _unavailable("not_built", "not built; load dated ADP snapshots first")
    issues = adp_market_integrity_issues(config)
    if issues:
        return _unavailable("invalid", issues[0])
    try:
        with duckdb.connect(str(warehouse_path), read_only=True) as connection:
            row = connection.execute(
                """
                SELECT build_fingerprint, snapshot_count, observation_rows,
                       persistence_ready_rows, linear_ready_rows, ew_ready_rows,
                       availability_parameter_rows, calibration_status, supervised_status
                FROM adp_phase5_builds
                """
            ).fetchone()
    except duckdb.Error as exc:
        return _unavailable("unreadable", f"Phase 5 data could not be read safely: {exc}")
    if row is None:
        return _unavailable(
            "not_built",
            "not built; run fantasy-draft models build-adp-baselines",
        )
    snapshots = int(row[1])
    observations = int(row[2])
    persistence = int(row[3])
    linear = int(row[4])
    ew = int(row[5])
    availability = int(row[6])
    if not snapshots or persistence != observations or availability != observations:
        return _unavailable("invalid", "Phase 5 publication counts do not reconcile")
    trend_message = (
        f"linear/EW trends ready for {linear}/{ew} rows"
        if linear or ew
        else "linear/EW trends unavailable: insufficient dated history"
    )
    return AdpMarketStatus(
        available=True,
        code="available",
        message=(
            f"{snapshots} production snapshot(s), {observations} rows; persistence active; "
            f"{trend_message}; availability baseline active and uncalibrated"
        ),
        build_fingerprint=str(row[0]),
        snapshot_count=snapshots,
        observation_rows=observations,
        persistence_ready_rows=persistence,
        linear_ready_rows=linear,
        ew_ready_rows=ew,
        availability_rows=availability,
        calibration_status=str(row[7]),
        supervised_status=str(row[8]),
    )


def load_adp_market_board(config: AppConfig) -> AdpMarketBoard:
    """Load only latest validated source/scope rows for the prediction season."""

    status = adp_market_status(config)
    if not status.available:
        return AdpMarketBoard(status=status)
    warehouse_path = config.resolve(config.paths.warehouse)
    try:
        availability_config = load_availability_config(
            config.project_root / "configs" / "adp_availability.yaml"
        )
        with duckdb.connect(str(warehouse_path), read_only=True) as connection:
            raw_rows = connection.execute(
                """
                WITH latest_scopes AS (
                    SELECT source, season, scoring_format, team_count, position_scope,
                           max(captured_at) AS captured_at
                    FROM adp_snapshot_metadata
                    WHERE season = ?
                    GROUP BY source, season, scoring_format, team_count, position_scope
                )
                SELECT snapshot.snapshot_id, snapshot.raw_source_row_id,
                       snapshot.player_id, snapshot.player_name,
                       coalesce(snapshot.position, ''), snapshot.nfl_team,
                       snapshot.source, snapshot.captured_at, snapshot.season,
                       snapshot.scoring_format, snapshot.team_count,
                       snapshot.average_pick, snapshot.min_pick, snapshot.max_pick,
                       snapshot.source_stddev, snapshot.sample_size,
                       snapshot.mapping_confidence, movement.prior_average_pick,
                       movement.change_7d, movement.velocity_per_day,
                       movement.source_spread, movement.observation_count,
                       persistence.predicted_average_pick,
                       linear.predicted_average_pick, linear.status,
                       weighted.predicted_average_pick, weighted.status,
                       availability.scale, availability.evidence_method,
                       availability.fallback_group
                FROM adp_snapshots AS snapshot
                JOIN adp_snapshot_metadata AS metadata USING (snapshot_id)
                JOIN latest_scopes AS latest
                  ON latest.source = metadata.source
                 AND latest.season = metadata.season
                 AND latest.scoring_format = metadata.scoring_format
                 AND latest.team_count = metadata.team_count
                 AND latest.position_scope = metadata.position_scope
                 AND latest.captured_at = metadata.captured_at
                JOIN adp_movement_features AS movement
                  ON movement.snapshot_id = snapshot.snapshot_id
                 AND movement.raw_source_row_id = snapshot.raw_source_row_id
                JOIN adp_availability_parameters AS availability
                  ON availability.snapshot_id = snapshot.snapshot_id
                 AND availability.raw_source_row_id = snapshot.raw_source_row_id
                JOIN adp_movement_forecasts AS persistence
                  ON persistence.snapshot_id = snapshot.snapshot_id
                 AND persistence.raw_source_row_id = snapshot.raw_source_row_id
                 AND persistence.baseline_name = 'persistence'
                JOIN adp_movement_forecasts AS linear
                  ON linear.snapshot_id = snapshot.snapshot_id
                 AND linear.raw_source_row_id = snapshot.raw_source_row_id
                 AND linear.baseline_name = 'linear_trend'
                JOIN adp_movement_forecasts AS weighted
                  ON weighted.snapshot_id = snapshot.snapshot_id
                 AND weighted.raw_source_row_id = snapshot.raw_source_row_id
                 AND weighted.baseline_name = 'exponentially_weighted_trend'
                ORDER BY snapshot.average_pick, snapshot.source, snapshot.player_name
                """,
                [config.project.prediction_season],
            ).fetchall()
    except (OSError, ValueError, duckdb.Error) as exc:
        return AdpMarketBoard(
            status=_unavailable("unreadable", f"Phase 5 data could not be loaded safely: {exc}")
        )
    rows = tuple(_row_from_query(row) for row in raw_rows)
    if not rows:
        return AdpMarketBoard(
            status=_unavailable(
                "no_live_rows",
                f"no validated ADP rows for {config.project.prediction_season}",
            )
        )
    return AdpMarketBoard(status=status, rows=rows, availability_config=availability_config)


def _row_from_query(row: tuple[object, ...]) -> AdpMarketRow:
    captured_at = row[7]
    if not isinstance(captured_at, datetime):
        raise ValueError("ADP market captured_at must be a timestamp.")
    player_id = None if row[2] is None else str(row[2])
    source = str(row[6])
    raw_source_row_id = str(row[1])
    return AdpMarketRow(
        snapshot_id=str(row[0]),
        raw_source_row_id=raw_source_row_id,
        identity=AdpIdentity(
            source=source,
            raw_source_row_id=raw_source_row_id,
            player_id=player_id,
        ),
        player_name=str(row[3]),
        position=str(row[4]),
        nfl_team=None if row[5] is None else str(row[5]),
        source=source,
        captured_at=captured_at,
        season=int(str(row[8])),
        scoring_format=str(row[9]),
        team_count=int(str(row[10])),
        average_pick=float(str(row[11])),
        min_pick=None if row[12] is None else float(str(row[12])),
        max_pick=None if row[13] is None else float(str(row[13])),
        source_standard_deviation=None if row[14] is None else float(str(row[14])),
        sample_size=None if row[15] is None else int(str(row[15])),
        mapping_confidence=str(row[16]),
        prior_average_pick=None if row[17] is None else float(str(row[17])),
        change_7d=None if row[18] is None else float(str(row[18])),
        velocity_per_day=None if row[19] is None else float(str(row[19])),
        source_spread=None if row[20] is None else float(str(row[20])),
        observation_count=int(str(row[21])),
        persistence_prediction=None if row[22] is None else float(str(row[22])),
        linear_prediction=None if row[23] is None else float(str(row[23])),
        linear_status=str(row[24]),
        exponentially_weighted_prediction=None if row[25] is None else float(str(row[25])),
        exponentially_weighted_status=str(row[26]),
        availability_scale=float(str(row[27])),
        availability_evidence_method=str(row[28]),
        availability_fallback_group=None if row[29] is None else str(row[29]),
    )


def _unavailable(code: str, message: str) -> AdpMarketStatus:
    return AdpMarketStatus(available=False, code=code, message=message)
