"""Persist cutoff-safe ADP movement and availability baseline artifacts."""

from __future__ import annotations

import hashlib
import json
from collections import defaultdict
from dataclasses import asdict, dataclass
from datetime import UTC, datetime
from itertools import pairwise
from pathlib import Path
from typing import Any, cast

import duckdb

from fantasy_draft_ai.config import AppConfig
from fantasy_draft_ai.data.warehouse import Warehouse
from fantasy_draft_ai.models.adp.availability import estimate_pick_spread
from fantasy_draft_ai.models.adp.config import AvailabilityConfig, load_availability_config
from fantasy_draft_ai.models.adp.movement import (
    AdpIdentity,
    AdpObservation,
    MovementFeatures,
    MovementForecast,
    movement_baselines_as_of,
    movement_features_as_of,
)

MOVEMENT_FEATURE_VERSION = "phase5-adp-movement-features-v1"
MOVEMENT_BASELINE_VERSION = "phase5-adp-movement-baselines-v1"
AVAILABILITY_METHOD_VERSION = "phase5-normal-pick-distribution-v1"
PHASE5_BUILD_VERSION = "phase5-adp-availability-v1"
FORECAST_HORIZON_DAYS = 1


@dataclass(frozen=True)
class AdpMarketBuildResult:
    """Outcome and evidence from one deterministic Phase 5 build."""

    committed: bool
    reused: bool
    build_fingerprint: str
    snapshot_count: int
    observation_rows: int
    movement_feature_rows: int
    movement_forecast_rows: int
    availability_parameter_rows: int
    report_path: Path | None
    report: dict[str, Any]

    def render(self) -> str:
        if self.reused:
            transaction = "REUSED"
        elif self.committed:
            transaction = "COMMITTED"
        else:
            transaction = "NOT COMMITTED"
        lines = [
            f"Phase 5 ADP market foundation: {self.report.get('status', 'FAILED')}",
            f"Warehouse transaction: {transaction}",
            f"Build fingerprint: {self.build_fingerprint or '<missing>'}",
            f"Production snapshots: {self.snapshot_count}",
            f"ADP observations: {self.observation_rows}",
            f"Movement feature rows: {self.movement_feature_rows}",
            f"Movement baseline rows: {self.movement_forecast_rows}",
            f"Availability parameter rows: {self.availability_parameter_rows}",
        ]
        for issue in self.report.get("issues", []):
            lines.append(f"- {issue}")
        if self.report_path is not None:
            lines.append(f"Evaluation report: {self.report_path}")
        return "\n".join(lines)


@dataclass(frozen=True)
class _SnapshotRow:
    snapshot_id: str
    source: str
    captured_at: datetime
    season: int
    scoring_format: str
    team_count: int
    position_scope: str
    player_id: str | None
    player_name: str
    position: str
    average_pick: float
    min_pick: float | None
    max_pick: float | None
    sample_size: int | None
    source_stddev: float | None
    raw_source_row_id: str
    mapping_confidence: str
    raw_sha256: str

    @property
    def identity(self) -> AdpIdentity:
        return AdpIdentity(
            source=self.source,
            raw_source_row_id=self.raw_source_row_id,
            player_id=self.player_id,
        )

    @property
    def scope_key(self) -> tuple[int, str, int, str]:
        return (self.season, self.scoring_format, self.team_count, self.position_scope)

    @property
    def observation(self) -> AdpObservation:
        return AdpObservation(
            identity=self.identity,
            captured_at=self.captured_at,
            average_pick=self.average_pick,
        )


@dataclass(frozen=True)
class _BuildRows:
    movement_features: tuple[tuple[Any, ...], ...]
    movement_forecasts: tuple[tuple[Any, ...], ...]
    availability_parameters: tuple[tuple[Any, ...], ...]
    persistence_ready: int
    linear_ready: int
    ew_ready: int
    fallback_rows: int


def build_adp_market_baselines(
    config: AppConfig,
    *,
    availability_config_path: Path | None = None,
    output_path: Path | None = None,
) -> AdpMarketBuildResult:
    """Build deterministic market features without claiming unavailable supervision."""

    warehouse = Warehouse(config.resolve(config.paths.warehouse))
    if not warehouse.path.exists():
        return _failure("The canonical warehouse does not exist.")
    warehouse.initialize()
    configured_path = availability_config_path or (
        config.project_root / "configs" / "adp_availability.yaml"
    )
    try:
        availability_config = load_availability_config(configured_path)
        availability_config_fingerprint = _file_sha256(configured_path)
        with warehouse.connect(read_only=True) as connection:
            rows = _read_snapshot_rows(connection)
    except (OSError, ValueError, duckdb.Error) as exc:
        return _failure(f"Could not read validated ADP inputs: {exc}")
    if not rows:
        return _failure("No production ADP snapshots are loaded; run fantasy-draft data load-adp.")

    snapshot_fingerprint = _snapshot_data_fingerprint(rows)
    build_fingerprint = _fingerprint(
        {
            "build_version": PHASE5_BUILD_VERSION,
            "snapshot_data_fingerprint": snapshot_fingerprint,
            "availability_config_fingerprint": availability_config_fingerprint,
            "movement_feature_version": MOVEMENT_FEATURE_VERSION,
            "movement_baseline_version": MOVEMENT_BASELINE_VERSION,
            "availability_method_version": AVAILABILITY_METHOD_VERSION,
            "forecast_horizon_days": FORECAST_HORIZON_DAYS,
        }
    )
    try:
        with warehouse.connect(read_only=True) as connection:
            reused_report = _reusable_report(connection, build_fingerprint)
        if reused_report is not None:
            report_path = _write_report(config, output_path, reused_report)
            return _result_from_report(
                report=reused_report,
                report_path=report_path,
                committed=False,
                reused=True,
            )
        built = _build_rows(rows, availability_config, snapshot_fingerprint)
        report = _build_report(
            rows,
            built,
            snapshot_fingerprint=snapshot_fingerprint,
            availability_config_fingerprint=availability_config_fingerprint,
            build_fingerprint=build_fingerprint,
        )
        _persist_build(
            warehouse,
            built,
            report,
            snapshot_fingerprint=snapshot_fingerprint,
            availability_config_fingerprint=availability_config_fingerprint,
            build_fingerprint=build_fingerprint,
        )
        report_path = _write_report(config, output_path, report)
    except (OSError, ValueError, duckdb.Error) as exc:
        return _failure(f"Phase 5 build failed: {exc}")
    return _result_from_report(
        report=report,
        report_path=report_path,
        committed=True,
        reused=False,
    )


def adp_market_integrity_issues(config: AppConfig) -> list[str]:
    """Return warehouse-level Phase 5 lineage and count failures."""

    warehouse = Warehouse(config.resolve(config.paths.warehouse))
    if not warehouse.path.exists():
        return []
    try:
        with warehouse.connect(read_only=True) as connection:
            table_names = {
                str(row[0])
                for row in connection.execute(
                    "SELECT table_name FROM information_schema.tables WHERE table_schema='main'"
                ).fetchall()
            }
            required = {
                "adp_snapshots",
                "adp_snapshot_metadata",
                "adp_movement_features",
                "adp_movement_forecasts",
                "adp_availability_parameters",
                "adp_phase5_builds",
            }
            if not required.issubset(table_names):
                return []
            issues: list[str] = []
            orphan_players = connection.execute(
                """
                SELECT count(*)
                FROM adp_snapshots AS snapshot
                LEFT JOIN players AS player ON player.player_id = snapshot.player_id
                WHERE snapshot.player_id IS NOT NULL AND player.player_id IS NULL
                """
            ).fetchone()
            metadata_mismatch = connection.execute(
                """
                SELECT count(*)
                FROM adp_snapshot_metadata AS metadata
                WHERE metadata.row_count != (
                    SELECT count(*) FROM adp_snapshots AS snapshot
                    WHERE snapshot.snapshot_id = metadata.snapshot_id
                )
                """
            ).fetchone()
            missing_metadata = connection.execute(
                """
                SELECT count(DISTINCT snapshot.snapshot_id)
                FROM adp_snapshots AS snapshot
                LEFT JOIN adp_snapshot_metadata AS metadata USING (snapshot_id)
                WHERE metadata.snapshot_id IS NULL
                """
            ).fetchone()
            build_rows = connection.execute(
                """
                SELECT build_fingerprint, snapshot_data_fingerprint,
                       movement_feature_rows, movement_forecast_rows,
                       availability_parameter_rows, persistence_ready_rows,
                       linear_ready_rows, ew_ready_rows, report_payload
                FROM adp_phase5_builds
                """
            ).fetchall()
            if orphan_players is None or int(orphan_players[0]):
                issues.append("ADP snapshots contain orphan canonical player IDs.")
            if metadata_mismatch is None or int(metadata_mismatch[0]):
                issues.append("ADP snapshot metadata row counts do not reconcile.")
            if missing_metadata is None or int(missing_metadata[0]):
                issues.append("ADP snapshot rows are missing snapshot-level provenance.")
            if len(build_rows) > 1:
                issues.append("Exactly one active Phase 5 build is allowed.")
            elif len(build_rows) == 1:
                row = build_rows[0]
                report = cast(dict[str, Any], json.loads(str(row[8])))
                active_rows = _read_snapshot_rows(connection)
                active_snapshot_fingerprint = _snapshot_data_fingerprint(active_rows)
                actual_counts = connection.execute(
                    """
                    SELECT
                        (SELECT count(*) FROM adp_movement_features),
                        (SELECT count(*) FROM adp_movement_forecasts),
                        (SELECT count(*) FROM adp_availability_parameters),
                        (SELECT count(*) FROM adp_movement_forecasts
                         WHERE baseline_name = 'persistence' AND status = 'available'),
                        (SELECT count(*) FROM adp_movement_forecasts
                         WHERE baseline_name = 'linear_trend' AND status = 'available'),
                        (SELECT count(*) FROM adp_movement_forecasts
                         WHERE baseline_name = 'exponentially_weighted_trend'
                           AND status = 'available')
                    """
                ).fetchone()
                expected = tuple(int(value) for value in row[2:8])
                actual = tuple(int(value) for value in actual_counts) if actual_counts else ()
                if expected != actual:
                    issues.append("Phase 5 derived-table counts are stale or incomplete.")
                if (
                    str(row[1]) != active_snapshot_fingerprint
                    or int(report.get("observation_rows", -1)) != len(active_rows)
                    or int(report.get("snapshot_count", -1))
                    != len({snapshot.snapshot_id for snapshot in active_rows})
                ):
                    issues.append("Phase 5 derived rows are stale for the canonical ADP inputs.")
                if (
                    report.get("build_fingerprint") != row[0]
                    or report.get("snapshot_data_fingerprint") != row[1]
                    or report.get("status") != "PASSED"
                ):
                    issues.append("Phase 5 report lineage is stale or invalid.")
                feature_fingerprints = connection.execute(
                    """
                    SELECT count(DISTINCT data_fingerprint)
                    FROM (
                        SELECT data_fingerprint FROM adp_movement_features
                        UNION ALL
                        SELECT data_fingerprint FROM adp_movement_forecasts
                        UNION ALL
                        SELECT data_fingerprint FROM adp_availability_parameters
                    )
                    """
                ).fetchone()
                if feature_fingerprints is None or int(feature_fingerprints[0]) != 1:
                    issues.append("Phase 5 derived rows do not share one input fingerprint.")
            return issues
    except (duckdb.Error, json.JSONDecodeError, ValueError) as exc:
        return [f"Could not validate the Phase 5 ADP build: {exc}"]


def _read_snapshot_rows(connection: duckdb.DuckDBPyConnection) -> tuple[_SnapshotRow, ...]:
    raw_rows = connection.execute(
        """
        SELECT snapshot.snapshot_id, snapshot.source, snapshot.captured_at,
               snapshot.season, snapshot.scoring_format, snapshot.team_count,
               metadata.position_scope, snapshot.player_id, snapshot.player_name,
               coalesce(snapshot.position, ''), snapshot.average_pick,
               snapshot.min_pick, snapshot.max_pick, snapshot.sample_size,
               snapshot.source_stddev, snapshot.raw_source_row_id,
               snapshot.mapping_confidence, metadata.raw_sha256
        FROM adp_snapshots AS snapshot
        JOIN adp_snapshot_metadata AS metadata USING (snapshot_id)
        WHERE snapshot.average_pick IS NOT NULL
        ORDER BY snapshot.season, snapshot.scoring_format, snapshot.team_count,
                 metadata.position_scope, snapshot.captured_at, snapshot.source,
                 snapshot.raw_source_row_id
        """
    ).fetchall()
    rows: list[_SnapshotRow] = []
    for raw in raw_rows:
        captured = raw[2]
        if not isinstance(captured, datetime):
            raise ValueError("ADP captured_at must be a timestamp.")
        rows.append(
            _SnapshotRow(
                snapshot_id=str(raw[0]),
                source=str(raw[1]),
                captured_at=captured.astimezone(UTC),
                season=int(raw[3]),
                scoring_format=str(raw[4]),
                team_count=int(raw[5]),
                position_scope=str(raw[6]),
                player_id=None if raw[7] is None else str(raw[7]),
                player_name=str(raw[8]),
                position=str(raw[9]),
                average_pick=float(raw[10]),
                min_pick=None if raw[11] is None else float(raw[11]),
                max_pick=None if raw[12] is None else float(raw[12]),
                sample_size=None if raw[13] is None else int(raw[13]),
                source_stddev=None if raw[14] is None else float(raw[14]),
                raw_source_row_id=str(raw[15]),
                mapping_confidence=str(raw[16]),
                raw_sha256=str(raw[17]),
            )
        )
    return tuple(rows)


def _build_rows(
    rows: tuple[_SnapshotRow, ...],
    availability_config: AvailabilityConfig,
    snapshot_fingerprint: str,
) -> _BuildRows:
    scope_groups: dict[tuple[int, str, int, str], list[_SnapshotRow]] = defaultdict(list)
    for row in rows:
        scope_groups[row.scope_key].append(row)
    feature_records: list[tuple[Any, ...]] = []
    forecast_records: list[tuple[Any, ...]] = []
    availability_records: list[tuple[Any, ...]] = []
    persistence_ready = 0
    linear_ready = 0
    ew_ready = 0
    fallback_rows = 0
    for scope_rows in scope_groups.values():
        observations = tuple(row.observation for row in scope_rows)
        cutoffs = sorted({row.captured_at for row in scope_rows})
        previous_rows = _previous_row_lookup(scope_rows)
        rows_by_cutoff: dict[datetime, list[_SnapshotRow]] = defaultdict(list)
        for row in scope_rows:
            rows_by_cutoff[row.captured_at].append(row)
        for cutoff in cutoffs:
            current_rows = rows_by_cutoff[cutoff]
            features = movement_features_as_of(observations, cutoff_at=cutoff)
            forecasts = movement_baselines_as_of(
                observations,
                cutoff_at=cutoff,
                horizon_days=FORECAST_HORIZON_DAYS,
            )
            feature_index = {
                (feature.identity.source, feature.identity.raw_source_row_id): feature
                for feature in features
                if feature.observed_at == cutoff
            }
            forecast_index = {
                (forecast.identity.source, forecast.identity.raw_source_row_id, forecast.method): (
                    forecast
                )
                for forecast in forecasts
                if forecast.last_observed_at == cutoff
            }
            for row in current_rows:
                key = (row.source, row.raw_source_row_id)
                feature = feature_index.get(key)
                if feature is None:
                    raise ValueError(f"Missing movement feature for {row.snapshot_id}/{key[1]}.")
                previous = previous_rows.get((row.snapshot_id, row.raw_source_row_id))
                feature_records.append(
                    _movement_feature_record(
                        row,
                        feature,
                        previous,
                        snapshot_fingerprint,
                    )
                )
                for method in (
                    "persistence",
                    "linear_trend",
                    "exponentially_weighted_trend",
                ):
                    forecast = forecast_index.get((row.source, row.raw_source_row_id, method))
                    if forecast is None:
                        raise ValueError(
                            f"Missing {method} forecast for {row.snapshot_id}/{key[1]}."
                        )
                    forecast_records.append(
                        _movement_forecast_record(row, forecast, snapshot_fingerprint)
                    )
                    if forecast.status == "available":
                        if method == "persistence":
                            persistence_ready += 1
                        elif method == "linear_trend":
                            linear_ready += 1
                        else:
                            ew_ready += 1
                spread = estimate_pick_spread(
                    position=row.position,
                    average_pick=row.average_pick,
                    observed_standard_deviation=row.source_stddev,
                    minimum_pick=row.min_pick,
                    maximum_pick=row.max_pick,
                    sample_size=row.sample_size,
                    config=availability_config,
                )
                fallback_group = None
                if spread.fallback_used:
                    fallback_rows += 1
                    band = availability_config.fallback_for(
                        position=row.position,
                        average_pick=row.average_pick,
                    )
                    upper = "open" if band.max_pick is None else f"{band.max_pick:g}"
                    fallback_group = (
                        f"{row.position.upper() or 'DEFAULT'}:{band.min_pick:g}-{upper}"
                    )
                availability_records.append(
                    (
                        row.snapshot_id,
                        row.raw_source_row_id,
                        row.identity.key,
                        row.player_id,
                        row.source,
                        row.captured_at,
                        row.average_pick,
                        spread.standard_deviation,
                        spread.method,
                        fallback_group,
                        spread.sample_size,
                        row.min_pick,
                        row.max_pick,
                        row.mapping_confidence,
                        AVAILABILITY_METHOD_VERSION,
                        snapshot_fingerprint,
                    )
                )
    return _BuildRows(
        movement_features=tuple(feature_records),
        movement_forecasts=tuple(forecast_records),
        availability_parameters=tuple(availability_records),
        persistence_ready=persistence_ready,
        linear_ready=linear_ready,
        ew_ready=ew_ready,
        fallback_rows=fallback_rows,
    )


def _previous_row_lookup(
    rows: list[_SnapshotRow],
) -> dict[tuple[str, str], _SnapshotRow]:
    groups: dict[tuple[str, str], list[_SnapshotRow]] = defaultdict(list)
    for row in rows:
        groups[(row.source, row.raw_source_row_id)].append(row)
    output: dict[tuple[str, str], _SnapshotRow] = {}
    for series in groups.values():
        ordered = sorted(series, key=lambda row: (row.captured_at, row.snapshot_id))
        for previous, current in pairwise(ordered):
            output[(current.snapshot_id, current.raw_source_row_id)] = previous
    return output


def _movement_feature_record(
    row: _SnapshotRow,
    feature: MovementFeatures,
    previous: _SnapshotRow | None,
    snapshot_fingerprint: str,
) -> tuple[Any, ...]:
    return (
        row.snapshot_id,
        row.raw_source_row_id,
        row.identity.key,
        row.player_id,
        row.source,
        row.captured_at,
        row.season,
        row.scoring_format,
        row.team_count,
        row.average_pick,
        None if previous is None else previous.snapshot_id,
        feature.prior_observed_at,
        feature.prior_adp,
        feature.elapsed_days,
        feature.change_1d,
        feature.change_3d,
        feature.change_7d,
        feature.change_14d,
        feature.velocity_picks_per_day,
        feature.acceleration_picks_per_day_squared,
        feature.rolling_volatility_14d,
        feature.source_spread,
        feature.observation_count,
        feature.source_count,
        feature.identity_observation_count,
        MOVEMENT_FEATURE_VERSION,
        snapshot_fingerprint,
    )


def _movement_forecast_record(
    row: _SnapshotRow,
    forecast: MovementForecast,
    snapshot_fingerprint: str,
) -> tuple[Any, ...]:
    predicted_change = (
        None if forecast.predicted_adp is None else forecast.predicted_adp - row.average_pick
    )
    return (
        row.snapshot_id,
        row.raw_source_row_id,
        forecast.method,
        FORECAST_HORIZON_DAYS,
        forecast.target_at,
        forecast.predicted_adp,
        predicted_change,
        forecast.training_observation_count,
        forecast.status,
        forecast.reason,
        MOVEMENT_BASELINE_VERSION,
        snapshot_fingerprint,
    )


def _snapshot_data_fingerprint(rows: tuple[_SnapshotRow, ...]) -> str:
    payload = [
        {
            **asdict(row),
            "captured_at": row.captured_at.isoformat(),
        }
        for row in rows
    ]
    return _fingerprint(payload)


def _build_report(
    rows: tuple[_SnapshotRow, ...],
    built: _BuildRows,
    *,
    snapshot_fingerprint: str,
    availability_config_fingerprint: str,
    build_fingerprint: str,
) -> dict[str, Any]:
    snapshots = {row.snapshot_id for row in rows}
    captures = sorted({row.captured_at for row in rows})
    mapped = sum(row.player_id is not None for row in rows)
    excluded = sum(row.mapping_confidence == "excluded" for row in rows)
    observed_spread = sum(
        record[8] != "configured_fallback" for record in built.availability_parameters
    )
    issues = [
        (
            f"{len(rows) - mapped - excluded} player rows remain unresolved; availability is "
            "keyed to source IDs and is not joined by display name."
        )
    ]
    if len(captures) < 3:
        issues.append(
            "Linear and exponentially weighted movement baselines require at least three dated "
            "observations per source player; persistence remains active."
        )
    issues.append(
        "Availability probabilities are distribution-based and uncalibrated because real draft "
        "outcomes are not yet archived."
    )
    return {
        "schema_version": "1.0",
        "status": "PASSED",
        "phase": 5,
        "build_version": PHASE5_BUILD_VERSION,
        "build_fingerprint": build_fingerprint,
        "snapshot_data_fingerprint": snapshot_fingerprint,
        "availability_config_fingerprint": availability_config_fingerprint,
        "movement_feature_version": MOVEMENT_FEATURE_VERSION,
        "movement_baseline_version": MOVEMENT_BASELINE_VERSION,
        "availability_method_version": AVAILABILITY_METHOD_VERSION,
        "snapshot_count": len(snapshots),
        "capture_timestamp_count": len(captures),
        "capture_start": captures[0].isoformat(),
        "capture_end": captures[-1].isoformat(),
        "sources": sorted({row.source for row in rows}),
        "observation_rows": len(rows),
        "mapped_rows": mapped,
        "unresolved_rows": len(rows) - mapped - excluded,
        "excluded_identity_rows": excluded,
        "movement_feature_rows": len(built.movement_features),
        "movement_forecast_rows": len(built.movement_forecasts),
        "persistence_ready_rows": built.persistence_ready,
        "linear_ready_rows": built.linear_ready,
        "exponentially_weighted_ready_rows": built.ew_ready,
        "availability_parameter_rows": len(built.availability_parameters),
        "availability_observed_spread_rows": observed_spread,
        "availability_fallback_rows": built.fallback_rows,
        "movement_status": (
            "persistence_active_trends_insufficient_history"
            if built.linear_ready == 0 and built.ew_ready == 0
            else "transparent_trends_active"
        ),
        "availability_status": "distribution_baseline_active_uncalibrated",
        "supervised_status": "unavailable_insufficient_dated_snapshots",
        "calibration_status": "unavailable_no_linked_draft_outcomes",
        "validation_strategy": "chronological_cutoff_only",
        "forecast_horizon_days": FORECAST_HORIZON_DAYS,
        "issues": issues,
        "phase_boundary": (
            "No draft recommendation, draft state, Monte Carlo simulation, or supervised "
            "availability model is produced in Phase 5."
        ),
    }


def _persist_build(
    warehouse: Warehouse,
    built: _BuildRows,
    report: dict[str, Any],
    *,
    snapshot_fingerprint: str,
    availability_config_fingerprint: str,
    build_fingerprint: str,
) -> None:
    with warehouse.connect() as connection:
        connection.execute("BEGIN TRANSACTION")
        try:
            connection.execute("DELETE FROM adp_movement_features")
            connection.execute("DELETE FROM adp_movement_forecasts")
            connection.execute("DELETE FROM adp_availability_parameters")
            connection.execute("DELETE FROM adp_phase5_builds")
            connection.executemany(
                """
                INSERT INTO adp_movement_features VALUES (
                    ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?,
                    ?, ?, ?
                )
                """,
                built.movement_features,
            )
            connection.executemany(
                """
                INSERT INTO adp_movement_forecasts VALUES (
                    ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?
                )
                """,
                built.movement_forecasts,
            )
            connection.executemany(
                """
                INSERT INTO adp_availability_parameters VALUES (
                    ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?
                )
                """,
                built.availability_parameters,
            )
            connection.execute(
                """
                INSERT INTO adp_phase5_builds VALUES (
                    ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?
                )
                """,
                [
                    build_fingerprint,
                    snapshot_fingerprint,
                    availability_config_fingerprint,
                    int(report["snapshot_count"]),
                    int(report["observation_rows"]),
                    len(built.movement_features),
                    len(built.movement_forecasts),
                    len(built.availability_parameters),
                    built.persistence_ready,
                    built.linear_ready,
                    built.ew_ready,
                    str(report["calibration_status"]),
                    str(report["supervised_status"]),
                    datetime.now(UTC),
                    _canonical_json(report),
                ],
            )
            issues = _transaction_integrity_issues(connection, report)
            if issues:
                raise ValueError("; ".join(issues))
            connection.execute("COMMIT")
        except Exception:
            connection.execute("ROLLBACK")
            raise


def _transaction_integrity_issues(
    connection: duckdb.DuckDBPyConnection,
    report: dict[str, Any],
) -> list[str]:
    counts = connection.execute(
        """
        SELECT
            (SELECT count(*) FROM adp_movement_features),
            (SELECT count(*) FROM adp_movement_forecasts),
            (SELECT count(*) FROM adp_availability_parameters),
            (SELECT count(*) FROM adp_movement_forecasts
             WHERE baseline_name = 'persistence' AND status = 'available')
        """
    ).fetchone()
    if counts is None:
        return ["Could not reconcile Phase 5 derived row counts."]
    expected = (
        int(report["movement_feature_rows"]),
        int(report["movement_forecast_rows"]),
        int(report["availability_parameter_rows"]),
        int(report["persistence_ready_rows"]),
    )
    if tuple(int(value) for value in counts) != expected:
        return ["Phase 5 derived row counts do not match the evaluation report."]
    invalid_probability_parameters = connection.execute(
        "SELECT count(*) FROM adp_availability_parameters "
        "WHERE average_pick < 1 OR scale <= 0 OR evidence_method = ''"
    ).fetchone()
    if invalid_probability_parameters is None or int(invalid_probability_parameters[0]):
        return ["Phase 5 availability parameters contain invalid values."]
    return []


def _reusable_report(
    connection: duckdb.DuckDBPyConnection,
    build_fingerprint: str,
) -> dict[str, Any] | None:
    row = connection.execute(
        "SELECT report_payload FROM adp_phase5_builds WHERE build_fingerprint = ?",
        [build_fingerprint],
    ).fetchone()
    if row is None:
        return None
    report = cast(dict[str, Any], json.loads(str(row[0])))
    if _transaction_integrity_issues(connection, report):
        return None
    return report


def _result_from_report(
    *,
    report: dict[str, Any],
    report_path: Path | None,
    committed: bool,
    reused: bool,
) -> AdpMarketBuildResult:
    return AdpMarketBuildResult(
        committed=committed,
        reused=reused,
        build_fingerprint=str(report["build_fingerprint"]),
        snapshot_count=int(report["snapshot_count"]),
        observation_rows=int(report["observation_rows"]),
        movement_feature_rows=int(report["movement_feature_rows"]),
        movement_forecast_rows=int(report["movement_forecast_rows"]),
        availability_parameter_rows=int(report["availability_parameter_rows"]),
        report_path=report_path,
        report=report,
    )


def _failure(*issues: str) -> AdpMarketBuildResult:
    return AdpMarketBuildResult(
        committed=False,
        reused=False,
        build_fingerprint="",
        snapshot_count=0,
        observation_rows=0,
        movement_feature_rows=0,
        movement_forecast_rows=0,
        availability_parameter_rows=0,
        report_path=None,
        report={"schema_version": "1.0", "status": "FAILED", "issues": list(issues)},
    )


def _write_report(
    config: AppConfig,
    output_path: Path | None,
    report: dict[str, Any],
) -> Path | None:
    if output_path is None:
        return None
    path = output_path if output_path.is_absolute() else config.project_root / output_path
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.suffix.casefold() == ".md":
        path.write_text(_render_markdown(report), encoding="utf-8")
        path.with_suffix(".json").write_text(
            _canonical_json(report, indent=2) + "\n", encoding="utf-8"
        )
    else:
        path.write_text(_canonical_json(report, indent=2) + "\n", encoding="utf-8")
        path.with_suffix(".md").write_text(_render_markdown(report), encoding="utf-8")
    return path


def _render_markdown(report: dict[str, Any]) -> str:
    lines = [
        "# Phase 5 ADP Movement and Availability Evaluation",
        "",
        f"Status: **{report['status']}**",
        "",
        "## Validated foundation",
        "",
        f"- Build fingerprint: `{report['build_fingerprint']}`",
        f"- Snapshot-data fingerprint: `{report['snapshot_data_fingerprint']}`",
        f"- Production snapshots: {report['snapshot_count']}",
        f"- Independent capture timestamps: {report['capture_timestamp_count']}",
        f"- Canonical ADP observations: {report['observation_rows']}",
        f"- Mapped / unresolved / excluded identity rows: {report['mapped_rows']} / "
        f"{report['unresolved_rows']} / {report['excluded_identity_rows']}",
        f"- Movement feature rows: {report['movement_feature_rows']}",
        f"- Movement baseline rows: {report['movement_forecast_rows']}",
        f"- Availability parameter rows: {report['availability_parameter_rows']}",
        "",
        "## Honest capability status",
        "",
        f"- Persistence forecasts ready: {report['persistence_ready_rows']}",
        f"- Linear-trend forecasts ready: {report['linear_ready_rows']}",
        f"- Exponentially weighted forecasts ready: {report['exponentially_weighted_ready_rows']}",
        f"- Movement: `{report['movement_status']}`",
        f"- Availability: `{report['availability_status']}`",
        f"- Supervised model: `{report['supervised_status']}`",
        f"- Calibration: `{report['calibration_status']}`",
        "",
        "## Availability evidence",
        "",
        "- Source standard-deviation or min/max rows: "
        f"{report['availability_observed_spread_rows']}",
        f"- Configured fallback rows: {report['availability_fallback_rows']}",
        "",
        "Probabilities use a continuity-corrected normal pick distribution. Source-reported "
        "standard deviation wins, then a min/max-derived scale, then a labeled versioned "
        "fallback. The result is conditional on the player still being available at the current "
        "pick.",
        "",
        "## Quality notes",
        "",
    ]
    lines.extend(f"- {issue}" for issue in report.get("issues", []))
    lines.extend(
        [
            "",
            "## Phase boundary",
            "",
            str(report["phase_boundary"]),
            "",
        ]
    )
    return "\n".join(lines)


def _canonical_json(payload: Any, *, indent: int | None = None) -> str:
    return json.dumps(
        payload,
        sort_keys=True,
        separators=None if indent is not None else (",", ":"),
        ensure_ascii=True,
        allow_nan=False,
        indent=indent,
    )


def _fingerprint(payload: Any) -> str:
    return hashlib.sha256(_canonical_json(payload).encode("utf-8")).hexdigest()


def _file_sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()
