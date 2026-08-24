"""Normalize immutable ADP captures into canonical, provenance-bound snapshots."""

from __future__ import annotations

import csv
import hashlib
import json
import math
import re
import unicodedata
from collections.abc import Sequence
from dataclasses import dataclass, field, replace
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import duckdb

from fantasy_draft_ai.config import AppConfig
from fantasy_draft_ai.data.manifests import SourceManifest, sha256_file
from fantasy_draft_ai.data.warehouse import Warehouse
from fantasy_draft_ai.schemas.quality import QualityIssue, QualityReport, Severity

ADP_SOURCES = frozenset(
    {"espn", "fantasypros", "ffc", "rtsports", "sleeper", "underdog", "yahoo"}
)
ESPN_REQUIRED_COLUMNS = frozenset(
    {
        "captured_at",
        "season",
        "source",
        "scoring_format",
        "team_count",
        "player_name",
        "position",
        "espn_player_id",
        "rank",
        "average_pick",
    }
)
PLATFORM_REQUIRED_COLUMNS = frozenset(
    {
        "captured_at",
        "season",
        "source",
        "scoring_format",
        "team_count",
        "source_player_id",
        "player_name",
        "position",
        "average_pick",
        "rank",
    }
)


@dataclass(frozen=True)
class AdpSnapshotLoadSummary:
    """Committed row accounting for one immutable ADP snapshot."""

    snapshot_id: str
    source: str
    captured_at: datetime
    season: int
    scoring_format: str
    team_count: int
    position_scope: str
    source_rows: int
    inserted_rows: int
    matched_existing_rows: int
    unresolved_players: int


@dataclass(frozen=True)
class AdpLoadResult:
    """Quality findings and committed warehouse accounting for ADP captures."""

    quality: QualityReport
    snapshots: tuple[AdpSnapshotLoadSummary, ...]
    committed: bool
    skipped_synthetic_rows: int
    manifest_paths: tuple[Path, ...]

    @property
    def inserted_rows(self) -> int:
        return sum(snapshot.inserted_rows for snapshot in self.snapshots)

    @property
    def matched_existing_rows(self) -> int:
        return sum(snapshot.matched_existing_rows for snapshot in self.snapshots)

    @property
    def unresolved_players(self) -> int:
        return sum(snapshot.unresolved_players for snapshot in self.snapshots)

    def render(self) -> str:
        lines = [
            self.quality.render(),
            "",
            f"Warehouse transaction: {'COMMITTED' if self.committed else 'NOT COMMITTED'}",
            f"Canonical snapshots: {len(self.snapshots)}",
            f"Inserted observations: {self.inserted_rows}",
            f"Matched existing observations: {self.matched_existing_rows}",
            f"Unresolved player observations: {self.unresolved_players}",
            f"Skipped synthetic observations: {self.skipped_synthetic_rows}",
        ]
        for snapshot in self.snapshots:
            lines.append(
                f"- {snapshot.source} {snapshot.captured_at.isoformat()} "
                f"{snapshot.scoring_format}/{snapshot.team_count}-team/"
                f"{snapshot.position_scope}: rows={snapshot.source_rows}, "
                f"inserted={snapshot.inserted_rows}, "
                f"matched={snapshot.matched_existing_rows}, "
                f"unresolved={snapshot.unresolved_players}"
            )
        return "\n".join(lines)


@dataclass
class _RawCapture:
    source: str
    raw_relative_path: str
    raw_path: Path
    raw_sha256: str
    acquired_at: datetime
    source_dataset_ids: set[str] = field(default_factory=set)
    manifest_seasons: set[int] = field(default_factory=set)


@dataclass(frozen=True)
class _AdpRow:
    raw_source_row_id: str
    player_name: str
    position: str | None
    nfl_team: str | None
    average_pick: float | None
    median_pick: float | None
    rank: int | None
    min_pick: float | None
    max_pick: float | None
    sample_size: int | None
    movement: float | None
    source_stddev: float | None
    source_movement_horizon: str | None
    player_id: str | None = None
    mapping_confidence: str = "unresolved"


@dataclass(frozen=True)
class _NormalizedSnapshot:
    snapshot_id: str
    source: str
    captured_at: datetime
    season: int
    scoring_format: str
    team_count: int
    position_scope: str
    raw_sha256: str
    raw_relative_path: str
    source_dataset_ids: tuple[str, ...]
    rows: tuple[_AdpRow, ...]


@dataclass
class _LoadMetrics:
    raw_rows: int = 0
    excluded_rows: int = 0
    skipped_synthetic_rows: int = 0
    required_field_failures: int = 0
    duplicate_keys: int = 0
    impossible_picks_or_rounds: int = 0


@dataclass(frozen=True)
class _CanonicalIdentity:
    player_id: str
    display_name: str
    position: str
    nfl_team: str | None
    current: bool


@dataclass(frozen=True)
class _IdentityIndex:
    direct: dict[tuple[str, str], str]
    by_name_position: dict[tuple[str, str], tuple[_CanonicalIdentity, ...]]


def find_adp_manifest_paths(config: AppConfig) -> tuple[Path, ...]:
    """Return every valid archived supported ADP manifest, including duplicates."""

    root = config.resolve(config.paths.manifests)
    matches: list[Path] = []
    for path in sorted(root.glob("*.json")) if root.exists() else ():
        try:
            manifest = SourceManifest.model_validate_json(path.read_text(encoding="utf-8"))
        except (OSError, ValueError):
            continue
        if manifest.source.casefold() in ADP_SOURCES:
            matches.append(path.resolve())
    if not matches:
        raise FileNotFoundError(
            "No archived supported ADP manifests were found. Archive a snapshot first."
        )
    return tuple(matches)


def load_adp_to_warehouse(
    config: AppConfig,
    *,
    manifest_paths: Sequence[Path] | None = None,
    include_synthetic: bool = False,
) -> AdpLoadResult:
    """Verify, normalize, and transactionally load archived ADP captures.

    Snapshot identifiers are content-derived and deliberately exclude manifest dataset
    UUIDs. Multiple manifests that document the same raw capture therefore contribute
    provenance without duplicating canonical rows.
    """

    selected_paths = tuple(
        path.resolve() for path in (manifest_paths or find_adp_manifest_paths(config))
    )
    issues: list[QualityIssue] = []
    metrics = _LoadMetrics()
    captures = _resolve_captures(config, selected_paths, issues)
    snapshots: list[_NormalizedSnapshot] = []
    if not _has_fatal(issues):
        for capture in sorted(captures, key=lambda item: item.raw_relative_path):
            if capture.source == "ffc":
                snapshots.extend(_normalize_ffc(capture, metrics, issues))
            elif capture.source == "espn":
                if _is_generic_platform_csv(capture.raw_path):
                    snapshots.extend(_normalize_platform_csv(capture, metrics, issues))
                else:
                    snapshots.extend(
                        _normalize_espn(
                            capture,
                            metrics,
                            issues,
                            include_synthetic=include_synthetic,
                        )
                    )
            elif capture.source == "sleeper":
                if _is_generic_platform_csv(capture.raw_path):
                    snapshots.extend(_normalize_platform_csv(capture, metrics, issues))
                else:
                    snapshots.extend(_normalize_sleeper(capture, metrics, issues))
            elif capture.source in {"fantasypros", "rtsports", "underdog", "yahoo"}:
                snapshots.extend(_normalize_platform_csv(capture, metrics, issues))

    if metrics.required_field_failures:
        issues.append(
            QualityIssue(
                code="invalid_required_adp_fields",
                message="ADP rows are missing required identity or snapshot-scope values.",
                count=metrics.required_field_failures,
                severity=Severity.FATAL,
            )
        )
    if metrics.skipped_synthetic_rows:
        issues.append(
            QualityIssue(
                code="synthetic_adp_rows_skipped",
                message="Fixture-labeled ESPN rows were excluded by the production load.",
                count=metrics.skipped_synthetic_rows,
            )
        )

    _validate_snapshot_keys(snapshots, metrics, issues)
    if _has_fatal(issues):
        return AdpLoadResult(
            quality=_quality_report(metrics, issues, unresolved_players=0),
            snapshots=(),
            committed=False,
            skipped_synthetic_rows=metrics.skipped_synthetic_rows,
            manifest_paths=selected_paths,
        )

    identity_index = _load_identity_index(
        config,
        issues,
        sources=frozenset(snapshot.source for snapshot in snapshots),
    )
    if _has_fatal(issues):
        return AdpLoadResult(
            quality=_quality_report(metrics, issues, unresolved_players=0),
            snapshots=(),
            committed=False,
            skipped_synthetic_rows=metrics.skipped_synthetic_rows,
            manifest_paths=selected_paths,
        )

    warehouse = Warehouse(config.resolve(config.paths.warehouse))
    warehouse.initialize()
    summaries, unresolved = _commit_snapshots(
        warehouse,
        snapshots,
        identity_index,
        issues,
    )
    if _has_fatal(issues):
        return AdpLoadResult(
            quality=_quality_report(metrics, issues, unresolved_players=0),
            snapshots=(),
            committed=False,
            skipped_synthetic_rows=metrics.skipped_synthetic_rows,
            manifest_paths=selected_paths,
        )
    if unresolved:
        issues.append(
            QualityIssue(
                code="unresolved_player_mappings",
                message=(
                    "ADP observations without exact platform-ID evidence, a reviewed mapping, "
                    "or one unique current name/position/team match were retained with a null "
                    "canonical player_id."
                ),
                count=unresolved,
            )
        )
    return AdpLoadResult(
        quality=_quality_report(metrics, issues, unresolved_players=unresolved),
        snapshots=summaries,
        committed=True,
        skipped_synthetic_rows=metrics.skipped_synthetic_rows,
        manifest_paths=selected_paths,
    )


def _quality_report(
    metrics: _LoadMetrics,
    issues: list[QualityIssue],
    *,
    unresolved_players: int,
) -> QualityReport:
    return QualityReport(
        source="adp_archives",
        row_count=metrics.raw_rows,
        required_field_failures=metrics.required_field_failures,
        duplicate_keys=metrics.duplicate_keys,
        unresolved_players=unresolved_players,
        excluded_rows=metrics.excluded_rows,
        impossible_picks_or_rounds=metrics.impossible_picks_or_rounds,
        issues=issues,
    )


def _resolve_captures(
    config: AppConfig,
    manifest_paths: tuple[Path, ...],
    issues: list[QualityIssue],
) -> list[_RawCapture]:
    project_root = config.project_root.resolve()
    captures: dict[tuple[str, str], _RawCapture] = {}
    source_by_archived_file: dict[tuple[Path, str], str] = {}
    for manifest_path in manifest_paths:
        try:
            manifest = SourceManifest.model_validate_json(manifest_path.read_text(encoding="utf-8"))
        except (OSError, ValueError) as exc:
            issues.append(
                QualityIssue(
                    code="invalid_adp_manifest",
                    message=f"Could not validate {manifest_path}: {exc}",
                    severity=Severity.FATAL,
                )
            )
            continue
        source = manifest.source.casefold()
        if source not in ADP_SOURCES:
            issues.append(
                QualityIssue(
                    code="wrong_adp_manifest_source",
                    message=(
                        "Expected a supported ADP manifest source, received "
                        f"{manifest.source!r}."
                    ),
                    severity=Severity.FATAL,
                )
            )
            continue
        if len(manifest.raw_files) != len(manifest.sha256):
            issues.append(
                QualityIssue(
                    code="adp_manifest_file_hash_mismatch",
                    message=(
                        f"Manifest {manifest.dataset_id} has different raw-file and hash counts."
                    ),
                    severity=Severity.FATAL,
                )
            )
            continue
        for relative, expected_hash in zip(manifest.raw_files, manifest.sha256, strict=True):
            raw_path = (project_root / relative).resolve()
            if not raw_path.is_relative_to(project_root):
                issues.append(
                    QualityIssue(
                        code="adp_raw_path_outside_project",
                        message=f"Manifest path leaves the project root: {relative}",
                        severity=Severity.FATAL,
                    )
                )
                continue
            if not raw_path.is_file():
                issues.append(
                    QualityIssue(
                        code="missing_adp_raw_file",
                        message=f"Raw ADP file is missing: {relative}",
                        severity=Severity.FATAL,
                    )
                )
                continue
            actual_hash = sha256_file(raw_path)
            if actual_hash != expected_hash:
                issues.append(
                    QualityIssue(
                        code="adp_raw_hash_mismatch",
                        message=f"Raw ADP hash does not match its manifest: {relative}",
                        severity=Severity.FATAL,
                    )
                )
                continue
            archived_file_key = (raw_path, actual_hash)
            prior_source = source_by_archived_file.get(archived_file_key)
            if prior_source is not None and prior_source != source:
                issues.append(
                    QualityIssue(
                        code="conflicting_adp_provenance",
                        message=f"Raw file {relative} is attributed to multiple ADP sources.",
                        severity=Severity.FATAL,
                    )
                )
                continue
            source_by_archived_file[archived_file_key] = source

            key = (source, actual_hash)
            capture = captures.get(key)
            if capture is None:
                capture = _RawCapture(
                    source=source,
                    raw_relative_path=Path(relative).as_posix(),
                    raw_path=raw_path,
                    raw_sha256=actual_hash,
                    acquired_at=_as_utc(manifest.acquired_at),
                )
                captures[key] = capture
            elif Path(relative).as_posix() < capture.raw_relative_path:
                # Identical bytes archived under different immutable paths represent one
                # capture. Keep a deterministic representative path while merging every
                # manifest dataset ID into the canonical snapshot provenance.
                capture.raw_relative_path = Path(relative).as_posix()
                capture.raw_path = raw_path
            capture.acquired_at = min(capture.acquired_at, _as_utc(manifest.acquired_at))
            capture.source_dataset_ids.add(manifest.dataset_id)
            capture.manifest_seasons.update(manifest.seasons)
    return list(captures.values())


def _load_identity_index(
    config: AppConfig,
    issues: list[QualityIssue],
    *,
    sources: frozenset[str],
) -> _IdentityIndex:
    """Build exact platform-ID and conservative composite identity evidence."""

    warehouse = Warehouse(config.resolve(config.paths.warehouse))
    warehouse.initialize()
    with warehouse.connect(read_only=True) as connection:
        raw_players = connection.execute(
            """
            SELECT player.player_id, player.gsis_id, player.espn_id,
                   player.sleeper_id, player.yahoo_id, player.display_name,
                   coalesce(player.canonical_position, ''), player.nfl_team,
                   coalesce(player.is_active, false)
                     OR EXISTS (
                         SELECT 1 FROM player_projection_board AS board
                         WHERE board.player_id = player.player_id
                           AND board.prediction_season = ?
                     ) AS current
            FROM players AS player
            """,
            [config.project.prediction_season],
        ).fetchall()

    direct: dict[tuple[str, str], str] = {}
    ambiguous_direct: set[tuple[str, str]] = set()
    canonical_by_gsis: dict[str, str] = {}
    by_name: dict[tuple[str, str], list[_CanonicalIdentity]] = {}
    for raw in raw_players:
        player_id = str(raw[0])
        gsis_id = _identifier_text(raw[1])
        if gsis_id is not None:
            prior_player_id = canonical_by_gsis.get(gsis_id)
            if prior_player_id is not None and prior_player_id != player_id:
                issues.append(
                    QualityIssue(
                        code="conflicting_gsis_identity",
                        message=(
                            f"GSIS identity {gsis_id} maps to both {prior_player_id} and "
                            f"{player_id}."
                        ),
                        severity=Severity.FATAL,
                    )
                )
            else:
                canonical_by_gsis[gsis_id] = player_id
        for source, value in (("espn", raw[2]), ("sleeper", raw[3]), ("yahoo", raw[4])):
            if source not in sources:
                continue
            source_id = _identifier_text(value)
            if source_id is not None:
                _add_direct_identity(
                    direct,
                    ambiguous_direct,
                    source,
                    source_id,
                    player_id,
                    issues,
                )
        display_name = _optional_text(raw[5])
        position = _normalize_position(_optional_text(raw[6]))
        if display_name is None or position is None:
            continue
        identity = _CanonicalIdentity(
            player_id=player_id,
            display_name=display_name,
            position=position,
            nfl_team=_normalize_team(_optional_text(raw[7])),
            current=bool(raw[8]),
        )
        by_name.setdefault((_normalize_name(display_name), position), []).append(identity)

    exact_crosswalk_sources = sources & {"espn", "sleeper", "yahoo"}
    crosswalk_path = (
        _latest_verified_ff_playerids_path(config, issues)
        if exact_crosswalk_sources
        else None
    )
    if crosswalk_path is not None and not _has_fatal(issues):
        try:
            with duckdb.connect() as connection:
                crosswalk_rows = connection.execute(
                    """
                    SELECT gsis_id, espn_id, sleeper_id, yahoo_id
                    FROM read_parquet(?)
                    WHERE gsis_id IS NOT NULL
                    """,
                    [str(crosswalk_path)],
                ).fetchall()
        except duckdb.Error as exc:
            issues.append(
                QualityIssue(
                    code="unreadable_ff_playerids_crosswalk",
                    message=f"Could not read the archived fantasy-ID crosswalk: {exc}",
                    severity=Severity.FATAL,
                )
            )
            crosswalk_rows = []
        for gsis_value, espn_value, sleeper_value, yahoo_value in crosswalk_rows:
            gsis_id = _identifier_text(gsis_value)
            crosswalk_player_id = canonical_by_gsis.get(gsis_id or "")
            if crosswalk_player_id is None:
                continue
            for source, value in (
                ("espn", espn_value),
                ("sleeper", sleeper_value),
                ("yahoo", yahoo_value),
            ):
                if source not in exact_crosswalk_sources:
                    continue
                source_id = _identifier_text(value)
                if source_id is not None:
                    _add_direct_identity(
                        direct,
                        ambiguous_direct,
                        source,
                        source_id,
                        crosswalk_player_id,
                        issues,
                    )

    return _IdentityIndex(
        direct=direct,
        by_name_position={
            key: tuple(sorted(values, key=lambda item: item.player_id))
            for key, values in by_name.items()
        },
    )


def _latest_verified_ff_playerids_path(
    config: AppConfig,
    issues: list[QualityIssue],
) -> Path | None:
    manifest_root = config.resolve(config.paths.manifests)
    candidates: list[tuple[datetime, SourceManifest]] = []
    for manifest_path in sorted(manifest_root.glob("*.json")) if manifest_root.exists() else ():
        try:
            manifest = SourceManifest.model_validate_json(
                manifest_path.read_text(encoding="utf-8")
            )
        except (OSError, ValueError):
            continue
        if manifest.source.casefold() == "nflverse_ff_playerids":
            candidates.append((_as_utc(manifest.acquired_at), manifest))
    if not candidates:
        issues.append(
            QualityIssue(
                code="missing_ff_playerids_crosswalk",
                message=(
                    "No archived nflverse fantasy-ID crosswalk was found; canonical mapping "
                    "will use existing IDs and conservative composite evidence only."
                ),
            )
        )
        return None
    manifest = max(candidates, key=lambda item: item[0])[1]
    if len(manifest.raw_files) != 1 or len(manifest.sha256) != 1:
        issues.append(
            QualityIssue(
                code="invalid_ff_playerids_manifest",
                message="The latest fantasy-ID crosswalk manifest must describe one raw file.",
                severity=Severity.FATAL,
            )
        )
        return None
    raw_path = (config.project_root / manifest.raw_files[0]).resolve()
    if (
        not raw_path.is_relative_to(config.project_root.resolve())
        or not raw_path.is_file()
        or sha256_file(raw_path) != manifest.sha256[0]
    ):
        issues.append(
            QualityIssue(
                code="invalid_ff_playerids_archive",
                message="The latest fantasy-ID crosswalk raw file is missing or hash-invalid.",
                severity=Severity.FATAL,
            )
        )
        return None
    return raw_path


def _add_direct_identity(
    direct: dict[tuple[str, str], str],
    ambiguous: set[tuple[str, str]],
    source: str,
    source_id: str,
    player_id: str,
    issues: list[QualityIssue],
) -> None:
    key = (source.casefold(), source_id)
    if key in ambiguous:
        return
    prior = direct.get(key)
    if prior is not None and prior != player_id:
        direct.pop(key)
        ambiguous.add(key)
        issues.append(
            QualityIssue(
                code="ambiguous_platform_identity",
                message=(
                    f"Platform identity {source}:{source_id} maps to both {prior} and "
                    f"{player_id}; exact mapping for this source ID was disabled."
                ),
            )
        )
        return
    direct[key] = player_id


def _normalize_ffc(
    capture: _RawCapture,
    metrics: _LoadMetrics,
    issues: list[QualityIssue],
) -> list[_NormalizedSnapshot]:
    parts = capture.raw_path.stem.split("__")
    if len(parts) != 6 or parts[0] != "ffc_adp" or not parts[2].endswith("_team"):
        issues.append(
            QualityIssue(
                code="invalid_ffc_capture_name",
                message=f"Could not derive the FFC snapshot scope from {capture.raw_path.name}.",
                severity=Severity.FATAL,
            )
        )
        return []
    try:
        scoring_format = parts[1].casefold()
        team_count = int(parts[2].removesuffix("_team"))
        season = int(parts[3])
        position_scope = parts[4].casefold()
    except ValueError:
        issues.append(
            QualityIssue(
                code="invalid_ffc_capture_scope",
                message=f"FFC capture scope is invalid: {capture.raw_path.name}.",
                severity=Severity.FATAL,
            )
        )
        return []
    captured_at = _timestamp_from_filename(parts[5]) or capture.acquired_at
    if capture.manifest_seasons and season not in capture.manifest_seasons:
        issues.append(
            QualityIssue(
                code="adp_manifest_season_mismatch",
                message=(
                    f"FFC filename season {season} is absent from manifest seasons "
                    f"{sorted(capture.manifest_seasons)}."
                ),
                severity=Severity.FATAL,
            )
        )
    try:
        payload: Any = json.loads(capture.raw_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        issues.append(
            QualityIssue(
                code="invalid_ffc_json",
                message=f"Could not read FFC JSON {capture.raw_path}: {exc}",
                severity=Severity.FATAL,
            )
        )
        return []
    if not isinstance(payload, dict) or not isinstance(payload.get("players"), list):
        issues.append(
            QualityIssue(
                code="missing_ffc_players",
                message="FFC JSON did not contain a players list.",
                severity=Severity.FATAL,
            )
        )
        return []
    raw_players: list[Any] = payload["players"]
    metrics.raw_rows += len(raw_players)
    rows: list[_AdpRow] = []
    for index, value in enumerate(raw_players):
        if not isinstance(value, dict):
            metrics.required_field_failures += 1
            metrics.excluded_rows += 1
            continue
        player_name = _optional_text(value.get("name") or value.get("player_name"))
        if player_name is None:
            metrics.required_field_failures += 1
            metrics.excluded_rows += 1
            continue
        source_id = _optional_text(value.get("player_id")) or f"row:{index}"
        rows.append(
            _AdpRow(
                raw_source_row_id=source_id,
                player_name=player_name,
                position=_optional_text(value.get("position")),
                nfl_team=_optional_text(value.get("team")),
                average_pick=_optional_float(value.get("adp")),
                median_pick=_optional_float(value.get("median")),
                rank=_optional_int(value.get("overall_rank") or value.get("rank") or index + 1),
                min_pick=_optional_float(value.get("high")),
                max_pick=_optional_float(value.get("low")),
                sample_size=_optional_int(value.get("times_drafted") or value.get("drafts")),
                movement=_optional_float(value.get("change")),
                source_stddev=_optional_float(value.get("stdev")),
                source_movement_horizon=(
                    "source_unspecified"
                    if _optional_float(value.get("change")) is not None
                    else None
                ),
            )
        )
    return [
        _make_snapshot(
            capture,
            captured_at=captured_at,
            season=season,
            scoring_format=scoring_format,
            team_count=team_count,
            position_scope=position_scope,
            rows=rows,
        )
    ]


def _normalize_espn(
    capture: _RawCapture,
    metrics: _LoadMetrics,
    issues: list[QualityIssue],
    *,
    include_synthetic: bool,
) -> list[_NormalizedSnapshot]:
    try:
        with capture.raw_path.open(encoding="utf-8-sig", newline="") as handle:
            reader = csv.DictReader(handle)
            columns = set(reader.fieldnames or ())
            missing = sorted(ESPN_REQUIRED_COLUMNS - columns)
            if missing:
                issues.append(
                    QualityIssue(
                        code="missing_espn_adp_columns",
                        message=f"Missing ESPN ADP columns: {', '.join(missing)}",
                        count=len(missing),
                        severity=Severity.FATAL,
                    )
                )
                return []
            raw_rows = list(reader)
    except (OSError, csv.Error) as exc:
        issues.append(
            QualityIssue(
                code="invalid_espn_csv",
                message=f"Could not read ESPN CSV {capture.raw_path}: {exc}",
                severity=Severity.FATAL,
            )
        )
        return []
    metrics.raw_rows += len(raw_rows)
    grouped: dict[tuple[datetime, int, str, int], list[_AdpRow]] = {}
    for index, value in enumerate(raw_rows):
        player_name = _optional_text(value.get("player_name"))
        if not include_synthetic and player_name is not None and _looks_synthetic(player_name):
            metrics.skipped_synthetic_rows += 1
            metrics.excluded_rows += 1
            continue
        try:
            captured_at = _parse_timestamp(value.get("captured_at"))
            season = _required_int(value.get("season"))
            scoring_format = _required_text(value.get("scoring_format")).casefold()
            team_count = _required_int(value.get("team_count"))
            player_name = _required_text(value.get("player_name"))
            source = _required_text(value.get("source")).casefold()
        except ValueError:
            metrics.required_field_failures += 1
            metrics.excluded_rows += 1
            continue
        if source != "espn":
            metrics.required_field_failures += 1
            metrics.excluded_rows += 1
            continue
        if capture.manifest_seasons and season not in capture.manifest_seasons:
            issues.append(
                QualityIssue(
                    code="adp_manifest_season_mismatch",
                    message=(
                        f"ESPN row season {season} is absent from manifest seasons "
                        f"{sorted(capture.manifest_seasons)}."
                    ),
                    severity=Severity.FATAL,
                )
            )
        source_id = _optional_text(value.get("espn_player_id")) or f"row:{index}"
        grouped.setdefault((captured_at, season, scoring_format, team_count), []).append(
            _AdpRow(
                raw_source_row_id=source_id,
                player_name=player_name,
                position=_optional_text(value.get("position")),
                nfl_team=_optional_text(value.get("nfl_team")),
                average_pick=_optional_float(value.get("average_pick")),
                median_pick=_optional_float(value.get("median_pick")),
                rank=_optional_int(value.get("rank")),
                min_pick=_optional_float(value.get("min_pick")),
                max_pick=_optional_float(value.get("max_pick")),
                sample_size=_optional_int(value.get("sample_size")),
                movement=_optional_float(value.get("seven_day_change")),
                source_stddev=None,
                source_movement_horizon=(
                    "7_day" if _optional_float(value.get("seven_day_change")) is not None else None
                ),
            )
        )
    return [
        _make_snapshot(
            capture,
            captured_at=scope[0],
            season=scope[1],
            scoring_format=scope[2],
            team_count=scope[3],
            position_scope="overall",
            rows=rows,
        )
        for scope, rows in sorted(grouped.items(), key=lambda item: item[0])
    ]


def _is_generic_platform_csv(path: Path) -> bool:
    if path.suffix.casefold() != ".csv":
        return False
    try:
        with path.open(encoding="utf-8-sig", newline="") as handle:
            columns = set(csv.DictReader(handle).fieldnames or ())
    except (OSError, csv.Error):
        return False
    return PLATFORM_REQUIRED_COLUMNS.issubset(columns)


def _normalize_platform_csv(
    capture: _RawCapture,
    metrics: _LoadMetrics,
    issues: list[QualityIssue],
) -> list[_NormalizedSnapshot]:
    """Normalize one validated standard official/licensed platform export."""

    try:
        with capture.raw_path.open(encoding="utf-8-sig", newline="") as handle:
            reader = csv.DictReader(handle)
            columns = set(reader.fieldnames or ())
            missing = sorted(PLATFORM_REQUIRED_COLUMNS - columns)
            if missing:
                issues.append(
                    QualityIssue(
                        code="missing_platform_adp_columns",
                        message=f"Missing platform ADP columns: {', '.join(missing)}",
                        count=len(missing),
                        severity=Severity.FATAL,
                    )
                )
                return []
            raw_rows = list(reader)
    except (OSError, csv.Error) as exc:
        issues.append(
            QualityIssue(
                code="invalid_platform_adp_csv",
                message=f"Could not read platform ADP CSV {capture.raw_path}: {exc}",
                severity=Severity.FATAL,
            )
        )
        return []
    metrics.raw_rows += len(raw_rows)
    grouped: dict[tuple[datetime, int, str, int], list[_AdpRow]] = {}
    for value in raw_rows:
        try:
            captured_at = _parse_timestamp(value.get("captured_at"))
            season = _required_int(value.get("season"))
            source = _required_text(value.get("source")).casefold()
            scoring_format = _normalize_scoring_format(
                _required_text(value.get("scoring_format"))
            )
            team_count = _required_int(value.get("team_count"))
            source_player_id = _required_identifier(value.get("source_player_id"))
            player_name = _required_text(value.get("player_name"))
            position = _normalize_position(_required_text(value.get("position")))
            if position is None:
                raise ValueError("Required position value is missing or invalid.")
            average_pick = _required_float(value.get("average_pick"))
            rank = _required_int(value.get("rank"))
        except ValueError:
            metrics.required_field_failures += 1
            metrics.excluded_rows += 1
            continue
        if source != capture.source:
            metrics.required_field_failures += 1
            metrics.excluded_rows += 1
            continue
        if capture.manifest_seasons and season not in capture.manifest_seasons:
            issues.append(
                QualityIssue(
                    code="adp_manifest_season_mismatch",
                    message=(
                        f"Platform row season {season} is absent from manifest seasons "
                        f"{sorted(capture.manifest_seasons)}."
                    ),
                    severity=Severity.FATAL,
                )
            )
        grouped.setdefault((captured_at, season, scoring_format, team_count), []).append(
            _AdpRow(
                raw_source_row_id=source_player_id,
                player_name=player_name,
                position=position,
                nfl_team=_optional_text(value.get("nfl_team")),
                average_pick=average_pick,
                median_pick=_optional_float(value.get("median_pick")),
                rank=rank,
                min_pick=_optional_float(value.get("min_pick")),
                max_pick=_optional_float(value.get("max_pick")),
                sample_size=_optional_int(value.get("sample_size")),
                movement=_optional_float(value.get("movement")),
                source_stddev=_optional_float(value.get("source_stddev")),
                source_movement_horizon=_optional_text(
                    value.get("source_movement_horizon")
                ),
            )
        )
    return [
        _make_snapshot(
            capture,
            captured_at=scope[0],
            season=scope[1],
            scoring_format=scope[2],
            team_count=scope[3],
            position_scope="overall",
            rows=rows,
        )
        for scope, rows in sorted(grouped.items(), key=lambda item: item[0])
    ]


def _normalize_sleeper(
    capture: _RawCapture,
    metrics: _LoadMetrics,
    issues: list[QualityIssue],
) -> list[_NormalizedSnapshot]:
    """Normalize Sleeper's current full-PPR projections/ADP response."""

    try:
        payload: Any = json.loads(capture.raw_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        issues.append(
            QualityIssue(
                code="invalid_sleeper_json",
                message=f"Could not read Sleeper JSON {capture.raw_path}: {exc}",
                severity=Severity.FATAL,
            )
        )
        return []
    if not isinstance(payload, list):
        issues.append(
            QualityIssue(
                code="invalid_sleeper_payload",
                message="Sleeper ADP JSON must be a list of player projection rows.",
                severity=Severity.FATAL,
            )
        )
        return []
    metrics.raw_rows += len(payload)
    candidates: list[_AdpRow] = []
    for value in payload:
        if not isinstance(value, dict):
            metrics.required_field_failures += 1
            metrics.excluded_rows += 1
            continue
        player = value.get("player")
        stats = value.get("stats")
        if not isinstance(player, dict) or not isinstance(stats, dict):
            metrics.excluded_rows += 1
            continue
        source_player_id = _optional_text(value.get("player_id"))
        position = _normalize_position(_optional_text(player.get("position")))
        average_pick = _optional_float(stats.get("adp_ppr"))
        if (
            source_player_id is None
            or position not in {"QB", "RB", "TE", "WR"}
            or average_pick is None
            or average_pick >= 900.0
        ):
            metrics.excluded_rows += 1
            continue
        player_name = _optional_text(player.get("full_name")) or " ".join(
            part
            for part in (
                _optional_text(player.get("first_name")),
                _optional_text(player.get("last_name")),
            )
            if part is not None
        ).strip()
        if not player_name:
            metrics.required_field_failures += 1
            metrics.excluded_rows += 1
            continue
        candidates.append(
            _AdpRow(
                raw_source_row_id=source_player_id,
                player_name=player_name,
                position=position,
                nfl_team=_optional_text(player.get("team") or value.get("team")),
                average_pick=average_pick,
                median_pick=None,
                rank=None,
                min_pick=None,
                max_pick=None,
                sample_size=None,
                movement=None,
                source_stddev=None,
                source_movement_horizon=None,
            )
        )
    ordered = sorted(
        candidates,
        key=lambda row: (
            row.average_pick if row.average_pick is not None else float("inf"),
            row.raw_source_row_id,
        ),
    )
    rows = [replace(row, rank=index) for index, row in enumerate(ordered, start=1)]
    if len(rows) < 100:
        issues.append(
            QualityIssue(
                code="insufficient_sleeper_adp_rows",
                message=f"Sleeper capture produced only {len(rows)} usable PPR ADP rows.",
                count=len(rows),
                severity=Severity.FATAL,
            )
        )
        return []
    if len(capture.manifest_seasons) != 1:
        issues.append(
            QualityIssue(
                code="invalid_sleeper_manifest_season",
                message=(
                    "Sleeper ADP manifests must identify exactly one season; found "
                    f"{sorted(capture.manifest_seasons)}."
                ),
                severity=Severity.FATAL,
            )
        )
        return []
    season = next(iter(capture.manifest_seasons))
    return [
        _make_snapshot(
            capture,
            captured_at=capture.acquired_at,
            season=season,
            scoring_format="ppr",
            team_count=12,
            position_scope="overall",
            rows=rows,
        )
    ]


def _make_snapshot(
    capture: _RawCapture,
    *,
    captured_at: datetime,
    season: int,
    scoring_format: str,
    team_count: int,
    position_scope: str,
    rows: list[_AdpRow],
) -> _NormalizedSnapshot:
    scope_payload = {
        "captured_at": _as_utc(captured_at).isoformat(),
        "position_scope": position_scope.casefold(),
        "raw_sha256": capture.raw_sha256,
        "scoring_format": scoring_format.casefold(),
        "season": season,
        "source": capture.source,
        "team_count": team_count,
    }
    digest = hashlib.sha256(
        json.dumps(scope_payload, sort_keys=True, separators=(",", ":")).encode("utf-8")
    ).hexdigest()
    return _NormalizedSnapshot(
        snapshot_id=f"adp-{digest}",
        source=capture.source,
        captured_at=_as_utc(captured_at),
        season=season,
        scoring_format=scoring_format.casefold(),
        team_count=team_count,
        position_scope=position_scope.casefold(),
        raw_sha256=capture.raw_sha256,
        raw_relative_path=capture.raw_relative_path,
        source_dataset_ids=tuple(sorted(capture.source_dataset_ids)),
        rows=tuple(rows),
    )


def _validate_snapshot_keys(
    snapshots: list[_NormalizedSnapshot],
    metrics: _LoadMetrics,
    issues: list[QualityIssue],
) -> None:
    snapshot_ids: set[str] = set()
    for snapshot in snapshots:
        if (
            snapshot.season < 2000
            or snapshot.season > 2100
            or snapshot.team_count < 4
            or snapshot.team_count > 32
            or not snapshot.scoring_format
            or not snapshot.position_scope
        ):
            issues.append(
                QualityIssue(
                    code="invalid_adp_snapshot_scope",
                    message=(
                        f"Snapshot {snapshot.snapshot_id} has an invalid season, scoring "
                        "format, team count, or position scope."
                    ),
                    severity=Severity.FATAL,
                )
            )
        if snapshot.snapshot_id in snapshot_ids:
            issues.append(
                QualityIssue(
                    code="duplicate_adp_snapshot",
                    message=f"Snapshot key was produced more than once: {snapshot.snapshot_id}",
                    severity=Severity.FATAL,
                )
            )
        invalid_values = sum(not _valid_adp_row(row) for row in snapshot.rows)
        if invalid_values:
            metrics.impossible_picks_or_rounds += invalid_values
            issues.append(
                QualityIssue(
                    code="invalid_adp_pick_values",
                    message=(
                        f"Snapshot {snapshot.snapshot_id} contains impossible ADP, rank, "
                        "range, sample-size, or spread values."
                    ),
                    count=invalid_values,
                    severity=Severity.FATAL,
                )
            )
        snapshot_ids.add(snapshot.snapshot_id)
        row_ids = [row.raw_source_row_id for row in snapshot.rows]
        duplicate_count = len(row_ids) - len(set(row_ids))
        if duplicate_count:
            metrics.duplicate_keys += duplicate_count
            issues.append(
                QualityIssue(
                    code="duplicate_adp_source_ids",
                    message=(
                        f"Snapshot {snapshot.snapshot_id} contains duplicate source player IDs."
                    ),
                    count=duplicate_count,
                    severity=Severity.FATAL,
                )
            )


def _valid_adp_row(row: _AdpRow) -> bool:
    if row.average_pick is None or row.average_pick < 1.0:
        return False
    if row.rank is not None and row.rank < 1:
        return False
    if row.sample_size is not None and row.sample_size < 0:
        return False
    if row.source_stddev is not None and row.source_stddev <= 0.0:
        return False
    ordered_picks = tuple(
        value
        for value in (row.min_pick, row.median_pick, row.average_pick, row.max_pick)
        if value is not None
    )
    if any(value < 1.0 for value in ordered_picks):
        return False
    if row.min_pick is not None:
        if row.average_pick < row.min_pick:
            return False
        if row.median_pick is not None and row.median_pick < row.min_pick:
            return False
    if row.max_pick is not None:
        if row.average_pick > row.max_pick:
            return False
        if row.median_pick is not None and row.median_pick > row.max_pick:
            return False
    return row.min_pick is None or row.max_pick is None or row.min_pick <= row.max_pick


def _commit_snapshots(
    warehouse: Warehouse,
    snapshots: list[_NormalizedSnapshot],
    identity_index: _IdentityIndex,
    issues: list[QualityIssue],
) -> tuple[tuple[AdpSnapshotLoadSummary, ...], int]:
    summaries: list[AdpSnapshotLoadSummary] = []
    with warehouse.connect() as connection:
        mappings = _reviewed_source_mappings(connection)
        conflicts = [
            (key, reviewed[0], identity_index.direct[key])
            for key, reviewed in mappings.items()
            if key in identity_index.direct and reviewed[0] != identity_index.direct[key]
        ]
        if conflicts:
            for (source, source_player_id), reviewed_player_id, exact_player_id in conflicts:
                issues.append(
                    QualityIssue(
                        code="conflicting_reviewed_platform_identity",
                        message=(
                            f"Reviewed mapping {source}:{source_player_id} points to "
                            f"{reviewed_player_id}, but exact platform-ID evidence points to "
                            f"{exact_player_id}. No ADP snapshots were committed."
                        ),
                        severity=Severity.FATAL,
                    )
                )
            return (), 0
        try:
            connection.execute("BEGIN TRANSACTION")
            resolved_snapshots = [
                replace(
                    snapshot,
                    rows=tuple(
                        _apply_mapping(snapshot.source, row, mappings, identity_index)
                        for row in snapshot.rows
                    ),
                )
                for snapshot in snapshots
            ]
            for snapshot in resolved_snapshots:
                existing = _snapshot_row_count(connection, snapshot.snapshot_id)
                _upsert_snapshot(connection, snapshot)
                final_count = _snapshot_row_count(connection, snapshot.snapshot_id)
                if final_count != len(snapshot.rows):
                    raise RuntimeError(
                        f"Post-load row count mismatch for snapshot {snapshot.snapshot_id}: "
                        f"expected {len(snapshot.rows)}, found {final_count}."
                    )
                unresolved = sum(row.player_id is None for row in snapshot.rows)
                summaries.append(
                    AdpSnapshotLoadSummary(
                        snapshot_id=snapshot.snapshot_id,
                        source=snapshot.source,
                        captured_at=snapshot.captured_at,
                        season=snapshot.season,
                        scoring_format=snapshot.scoring_format,
                        team_count=snapshot.team_count,
                        position_scope=snapshot.position_scope,
                        source_rows=len(snapshot.rows),
                        inserted_rows=max(len(snapshot.rows) - existing, 0),
                        matched_existing_rows=min(existing, len(snapshot.rows)),
                        unresolved_players=unresolved,
                    )
                )
            connection.execute("COMMIT")
        except Exception:
            connection.execute("ROLLBACK")
            raise
    return tuple(summaries), sum(summary.unresolved_players for summary in summaries)


def _reviewed_source_mappings(
    connection: duckdb.DuckDBPyConnection,
) -> dict[tuple[str, str], tuple[str, str]]:
    rows = connection.execute(
        """
        SELECT mapping.source, mapping.source_player_id, mapping.player_id,
               mapping.mapping_confidence
        FROM player_source_mappings AS mapping
        JOIN players AS player ON player.player_id = mapping.player_id
        WHERE mapping.mapping_confidence = 'reviewed'
        """
    ).fetchall()
    mappings: dict[tuple[str, str], tuple[str, str]] = {}
    for source, source_player_id, player_id, confidence in rows:
        normalized_source_id = _identifier_text(source_player_id)
        if normalized_source_id is None:
            continue
        mappings[(str(source).strip().casefold(), normalized_source_id)] = (
            str(player_id),
            str(confidence),
        )
    return mappings


def _apply_mapping(
    source: str,
    row: _AdpRow,
    mappings: dict[tuple[str, str], tuple[str, str]],
    identity_index: _IdentityIndex,
) -> _AdpRow:
    source_key = source.casefold()
    source_player_id = _identifier_text(row.raw_source_row_id)
    if source_player_id is None:
        return replace(row, player_id=None, mapping_confidence="unresolved")

    reviewed = mappings.get((source_key, source_player_id))
    if reviewed is not None:
        return replace(row, player_id=reviewed[0], mapping_confidence="reviewed")

    exact_player_id = identity_index.direct.get((source_key, source_player_id))
    if exact_player_id is not None:
        return replace(row, player_id=exact_player_id, mapping_confidence="exact")

    position = _normalize_position(row.position)
    normalized_name = _normalize_name(row.player_name)
    if not normalized_name or position is None:
        return replace(row, player_id=None, mapping_confidence="unresolved")
    candidates = [
        candidate
        for candidate in identity_index.by_name_position.get(
            (normalized_name, position),
            (),
        )
        if candidate.current
    ]
    source_team = _normalize_team(row.nfl_team)
    if source_team is not None:
        candidates = [candidate for candidate in candidates if candidate.nfl_team == source_team]
    if len(candidates) != 1:
        return replace(row, player_id=None, mapping_confidence="unresolved")
    return replace(row, player_id=candidates[0].player_id, mapping_confidence="high")


def _snapshot_row_count(
    connection: duckdb.DuckDBPyConnection,
    snapshot_id: str,
) -> int:
    row = connection.execute(
        "SELECT count(*) FROM adp_snapshots WHERE snapshot_id = ?", [snapshot_id]
    ).fetchone()
    if row is None:
        raise RuntimeError("DuckDB did not return an ADP snapshot count.")
    return int(row[0])


def _upsert_snapshot(
    connection: duckdb.DuckDBPyConnection,
    snapshot: _NormalizedSnapshot,
) -> None:
    connection.execute(
        """
        INSERT INTO adp_snapshot_metadata (
            snapshot_id, source, captured_at, season, scoring_format, team_count,
            position_scope, raw_sha256, raw_relative_path, source_dataset_ids,
            row_count, loaded_at
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, current_timestamp)
        ON CONFLICT (snapshot_id) DO UPDATE SET
            source_dataset_ids = excluded.source_dataset_ids,
            row_count = excluded.row_count
        """,
        [
            snapshot.snapshot_id,
            snapshot.source,
            snapshot.captured_at,
            snapshot.season,
            snapshot.scoring_format,
            snapshot.team_count,
            snapshot.position_scope,
            snapshot.raw_sha256,
            snapshot.raw_relative_path,
            json.dumps(snapshot.source_dataset_ids, separators=(",", ":")),
            len(snapshot.rows),
        ],
    )
    if snapshot.rows:
        connection.executemany(
            """
            INSERT INTO adp_snapshots (
                snapshot_id, source, captured_at, season, scoring_format, team_count,
                player_id, player_name, position, nfl_team, average_pick, median_pick,
                rank, min_pick, max_pick, sample_size, movement, source_stddev,
                source_movement_horizon, raw_source_row_id, mapping_confidence
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT (snapshot_id, raw_source_row_id) DO UPDATE SET
                source = excluded.source,
                captured_at = excluded.captured_at,
                season = excluded.season,
                scoring_format = excluded.scoring_format,
                team_count = excluded.team_count,
                player_id = excluded.player_id,
                player_name = excluded.player_name,
                position = excluded.position,
                nfl_team = excluded.nfl_team,
                average_pick = excluded.average_pick,
                median_pick = excluded.median_pick,
                rank = excluded.rank,
                min_pick = excluded.min_pick,
                max_pick = excluded.max_pick,
                sample_size = excluded.sample_size,
                movement = excluded.movement,
                source_stddev = excluded.source_stddev,
                source_movement_horizon = excluded.source_movement_horizon,
                mapping_confidence = excluded.mapping_confidence
            """,
            [
                (
                    snapshot.snapshot_id,
                    snapshot.source,
                    snapshot.captured_at,
                    snapshot.season,
                    snapshot.scoring_format,
                    snapshot.team_count,
                    row.player_id,
                    row.player_name,
                    row.position,
                    row.nfl_team,
                    row.average_pick,
                    row.median_pick,
                    row.rank,
                    row.min_pick,
                    row.max_pick,
                    row.sample_size,
                    row.movement,
                    row.source_stddev,
                    row.source_movement_horizon,
                    row.raw_source_row_id,
                    row.mapping_confidence,
                )
                for row in snapshot.rows
            ],
        )


def _has_fatal(issues: list[QualityIssue]) -> bool:
    return any(issue.severity == Severity.FATAL for issue in issues)


def _as_utc(value: datetime) -> datetime:
    if value.tzinfo is None:
        return value.replace(tzinfo=UTC)
    return value.astimezone(UTC)


def _parse_timestamp(value: object) -> datetime:
    text = _required_text(value)
    try:
        parsed = datetime.fromisoformat(text.replace("Z", "+00:00"))
    except ValueError as exc:
        raise ValueError(f"Invalid timestamp: {text}") from exc
    if parsed.tzinfo is None:
        raise ValueError(f"Timestamp must include a timezone: {text}")
    return parsed.astimezone(UTC)


def _timestamp_from_filename(value: str) -> datetime | None:
    try:
        return datetime.strptime(value, "%Y-%m-%dT%H%M%S%fZ").replace(tzinfo=UTC)
    except ValueError:
        return None


def _optional_text(value: object) -> str | None:
    if value is None:
        return None
    text = str(value).strip()
    return text or None


def _required_text(value: object) -> str:
    text = _optional_text(value)
    if text is None:
        raise ValueError("Required text value is missing.")
    return text


def _identifier_text(value: object) -> str | None:
    """Return a stable textual platform identifier without inventing an ID."""

    if value is None or isinstance(value, bool):
        return None
    if isinstance(value, int):
        return str(value)
    if isinstance(value, float):
        if not math.isfinite(value):
            return None
        return str(int(value)) if value.is_integer() else str(value)
    text = _optional_text(value)
    if text is None or text.casefold() in {"nan", "none", "null"}:
        return None
    numeric_float = re.fullmatch(r"([+-]?\d+)\.0+", text)
    return numeric_float.group(1) if numeric_float is not None else text


def _required_identifier(value: object) -> str:
    identifier = _identifier_text(value)
    if identifier is None:
        raise ValueError("Required platform identifier is missing or invalid.")
    return identifier


def _normalize_name(value: str) -> str:
    """Normalize a full player name for conservative composite matching only."""

    ascii_text = (
        unicodedata.normalize("NFKD", value)
        .encode("ascii", errors="ignore")
        .decode("ascii")
        .casefold()
    )
    tokens = re.findall(r"[a-z0-9]+", ascii_text)
    while tokens and tokens[-1] in {"jr", "sr", "ii", "iii", "iv", "v"}:
        tokens.pop()
    return "".join(tokens)


def _normalize_position(value: str | None) -> str | None:
    text = _optional_text(value)
    if text is None:
        return None
    compact = re.sub(r"[^A-Z]", "", text.upper())
    if compact in {"D", "DEF", "DEFENSE", "DST"}:
        return "DST"
    return compact or None


_NFL_TEAM_ALIASES = {
    "ARIZONACARDINALS": "ARI",
    "ARZ": "ARI",
    "ATLANTAFALCONS": "ATL",
    "BALTIMORERAVENS": "BAL",
    "BLT": "BAL",
    "BUFFALOBILLS": "BUF",
    "CAROLINAPANTHERS": "CAR",
    "CHICAGOBEARS": "CHI",
    "CINCINNATIBENGALS": "CIN",
    "CLEVELANDBROWNS": "CLE",
    "CLV": "CLE",
    "DALLASCOWBOYS": "DAL",
    "DENVERBRONCOS": "DEN",
    "DETROITLIONS": "DET",
    "GREENBAYPACKERS": "GB",
    "GNB": "GB",
    "HOUSTONTEXANS": "HOU",
    "HST": "HOU",
    "INDIANAPOLISCOLTS": "IND",
    "JACKSONVILLEJAGUARS": "JAX",
    "JAC": "JAX",
    "KANSASCITYCHIEFS": "KC",
    "KAN": "KC",
    "LASVEGASRAIDERS": "LV",
    "LVR": "LV",
    "OAK": "LV",
    "LOSANGELESCHARGERS": "LAC",
    "SD": "LAC",
    "SANDIEGOCHARGERS": "LAC",
    "LOSANGELESRAMS": "LAR",
    "STL": "LAR",
    "STLOUISRAMS": "LAR",
    "MIAMIDOLPHINS": "MIA",
    "MINNESOTAVIKINGS": "MIN",
    "NEWENGLANDPATRIOTS": "NE",
    "NWE": "NE",
    "NEWORLEANSSAINTS": "NO",
    "NOR": "NO",
    "NEWYORKGIANTS": "NYG",
    "NEWYORKJETS": "NYJ",
    "PHILADELPHIAEAGLES": "PHI",
    "PITTSBURGHSTEELERS": "PIT",
    "SEATTLESEAHAWKS": "SEA",
    "SANFRANCISCO49ERS": "SF",
    "SFO": "SF",
    "TAMPABAYBUCCANEERS": "TB",
    "TAM": "TB",
    "TENNESSEETITANS": "TEN",
    "WASHINGTONCOMMANDERS": "WAS",
    "WASHINGTONFOOTBALLTEAM": "WAS",
    "WASHINGTONREDSKINS": "WAS",
    "WSH": "WAS",
}
_NFL_TEAM_ABBREVIATIONS = frozenset(
    {
        "ARI",
        "ATL",
        "BAL",
        "BUF",
        "CAR",
        "CHI",
        "CIN",
        "CLE",
        "DAL",
        "DEN",
        "DET",
        "GB",
        "HOU",
        "IND",
        "JAX",
        "KC",
        "LV",
        "LAC",
        "LAR",
        "MIA",
        "MIN",
        "NE",
        "NO",
        "NYG",
        "NYJ",
        "PHI",
        "PIT",
        "SEA",
        "SF",
        "TB",
        "TEN",
        "WAS",
    }
)


def _normalize_team(value: str | None) -> str | None:
    text = _optional_text(value)
    if text is None:
        return None
    compact = re.sub(r"[^A-Z0-9]", "", text.upper())
    if compact in {"", "FA", "FREEAGENT", "NONE", "NA", "NAN"}:
        return None
    if compact in _NFL_TEAM_ABBREVIATIONS:
        return compact
    # Preserve an explicit unknown value so composite matching fails closed instead
    # of silently discarding contradictory team evidence.
    return _NFL_TEAM_ALIASES.get(compact, compact)


def _normalize_scoring_format(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", "_", value.strip().casefold()).strip("_")


def _optional_float(value: object) -> float | None:
    text = _optional_text(value)
    if text is None:
        return None
    try:
        number = float(text)
    except (TypeError, ValueError):
        return None
    return number if math.isfinite(number) else None


def _required_float(value: object) -> float:
    number = _optional_float(value)
    if number is None:
        raise ValueError("Required numeric value is missing or invalid.")
    return number


def _optional_int(value: object) -> int | None:
    number = _optional_float(value)
    if number is None or not number.is_integer():
        return None
    return int(number)


def _required_int(value: object) -> int:
    number = _optional_int(value)
    if number is None:
        raise ValueError("Required integer value is missing or invalid.")
    return number


def _looks_synthetic(player_name: str) -> bool:
    return player_name.casefold().startswith("fixture ")
