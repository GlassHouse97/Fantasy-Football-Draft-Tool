"""Validate and normalize privacy-safe ``league-history-v1`` ZIP packages.

The loader treats an uploaded archive as untrusted input.  It is archived first,
then inspected without extracting to disk, normalized from exact source fields,
and committed atomically.  Player display names are retained as source evidence
but are never used as identity joins.
"""

from __future__ import annotations

import csv
import hashlib
import io
import json
import math
import re
import stat
import zipfile
from contextlib import suppress
from dataclasses import dataclass, replace
from datetime import UTC, date, datetime
from pathlib import Path, PurePosixPath, PureWindowsPath
from typing import Literal, cast

import duckdb
from pydantic import BaseModel, ConfigDict, Field

from fantasy_draft_ai.config import AppConfig
from fantasy_draft_ai.data.manifests import sha256_file, utc_now
from fantasy_draft_ai.data.sources.league_history import LeagueHistoryArchiveResult
from fantasy_draft_ai.data.sources.league_history import (
    archive_league_history_package as archive_package,
)
from fantasy_draft_ai.data.warehouse import Warehouse
from fantasy_draft_ai.rules.models import DraftSettings, FlexSlot, LeagueRules
from fantasy_draft_ai.schemas.quality import QualityIssue, QualityReport, Severity
from fantasy_draft_ai.scoring.engine import ScoringRules

SCHEMA_VERSION = "league-history-v1"
MAX_ARCHIVE_ENTRIES = 16
MAX_EXPANDED_BYTES = 100 * 1024 * 1024
MAX_COMPRESSION_RATIO = 100.0

PACKAGE_FILE = "package.json"
REQUIRED_CSV_HEADERS: dict[str, tuple[str, ...]] = {
    "league_rules.csv": (
        "league_season_id",
        "platform",
        "season",
        "team_count",
        "draft_type",
        "draft_date",
        "rounds",
        "bench_slots",
        "ir_slots",
        "playoff_teams",
        "playoff_start_week",
        "championship_week",
        "scoring_json",
        "starter_slots_json",
    ),
    "draft_picks.csv": (
        "league_season_id",
        "overall_pick",
        "round",
        "draft_slot",
        "team_id",
        "player_name",
        "position",
        "source_player_id",
        "is_keeper",
        "is_autopick",
        "picked_at",
    ),
    "team_outcomes.csv": (
        "league_season_id",
        "team_id",
        "wins",
        "losses",
        "ties",
        "points_for",
        "points_against",
        "seed",
        "made_playoffs",
        "final_place",
        "is_champion",
    ),
}
OPTIONAL_CSV_HEADERS: dict[str, tuple[str, ...]] = {
    "weekly_rosters.csv": (
        "league_season_id",
        "week",
        "team_id",
        "player_name",
        "position",
        "source_player_id",
        "roster_slot",
        "is_starter",
    ),
    "matchups.csv": (
        "league_season_id",
        "week",
        "team_id",
        "opponent_team_id",
        "points_for",
        "points_against",
        "is_playoff",
    ),
    "transactions.csv": (
        "league_season_id",
        "transaction_id",
        "occurred_at",
        "team_id",
        "transaction_type",
        "player_name",
        "position",
        "source_player_id",
    ),
}
ALLOWED_FILES = frozenset(
    {PACKAGE_FILE, *REQUIRED_CSV_HEADERS.keys(), *OPTIONAL_CSV_HEADERS.keys()}
)
REQUIRED_FILES = frozenset({PACKAGE_FILE, *REQUIRED_CSV_HEADERS.keys()})
SUPPORTED_PLAYER_POSITIONS = frozenset({"QB", "RB", "WR", "TE"})
OPAQUE_ID_PATTERN = re.compile(r"^[A-Za-z0-9][A-Za-z0-9_-]{0,127}$")


class LeagueHistoryReadiness(BaseModel):
    """Durable capability result derived from normalized package evidence."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    schema_version: str | None = None
    archived: bool = True
    normalized: bool = False
    league_count: int = Field(default=0, ge=0)
    draft_complete_leagues: int = Field(default=0, ge=0)
    outcomes_complete_leagues: int = Field(default=0, ge=0)
    analysis_ready_leagues: int = Field(default=0, ge=0)
    championship_model_status: Literal["disabled"] = "disabled"
    reasons: tuple[str, ...] = ()

    @property
    def analysis_ready(self) -> bool:
        return self.analysis_ready_leagues > 0

    def as_dict(self) -> dict[str, object]:
        return cast(dict[str, object], self.model_dump(mode="json"))

    def render(self) -> str:
        lines = [
            "League-history readiness:",
            f"  schema: {self.schema_version or 'unavailable'}",
            f"  archived: {self.archived}",
            f"  normalized: {self.normalized}",
            f"  leagues: {self.league_count}",
            f"  complete drafts: {self.draft_complete_leagues}",
            f"  complete outcomes: {self.outcomes_complete_leagues}",
            f"  analysis ready: {self.analysis_ready_leagues}",
            "  championship model: disabled",
        ]
        lines.extend(f"  - {reason}" for reason in self.reasons)
        return "\n".join(lines)


class LeagueHistoryLoadResult(BaseModel):
    """Archive, validation, normalization, and readiness evidence for one upload."""

    model_config = ConfigDict(extra="forbid", frozen=True, arbitrary_types_allowed=True)

    raw_path: Path
    manifest_path: Path
    manifest_dataset_id: str
    raw_sha256: str
    package_fingerprint: str
    normalized_fingerprint: str | None = None
    status: Literal["archive_only", "validation_failed", "imported", "already_loaded"]
    committed: bool = False
    idempotent_reuse: bool = False
    optional_files: tuple[str, ...] = ()
    quality: QualityReport
    readiness: LeagueHistoryReadiness

    def as_dict(self) -> dict[str, object]:
        """Return a JSON-serializable result suitable for CLI/UI persistence."""

        return cast(dict[str, object], self.model_dump(mode="json"))

    def render(self) -> str:
        return "\n".join(
            (
                self.quality.render(),
                "",
                f"Raw archive: {self.raw_path}",
                f"Manifest: {self.manifest_path}",
                f"Package fingerprint: {self.package_fingerprint}",
                f"Normalized fingerprint: {self.normalized_fingerprint or 'unavailable'}",
                f"Warehouse status: {self.status}",
                "",
                self.readiness.render(),
            )
        )


@dataclass
class _Metrics:
    raw_rows: int = 0
    required_field_failures: int = 0
    duplicate_keys: int = 0
    unresolved_players: int = 0
    identity_conflicts: int = 0
    impossible_picks_or_rounds: int = 0
    unsupported_lineup_slots: int = 0
    invalid_json_settings: int = 0


@dataclass(frozen=True)
class _PackageDeclaration:
    schema_version: str
    package_id: str
    created_at: datetime
    source_platform: str
    included_files: frozenset[str]


@dataclass(frozen=True)
class _RuleRow:
    league_season_id: str
    platform: str
    season: int
    team_count: int
    draft_date: datetime
    rounds: int
    bench_slots: int
    ir_slots: int
    playoff_teams: int
    playoff_start_week: int
    championship_week: int
    rules: LeagueRules
    row_fingerprint: str


@dataclass(frozen=True)
class _PickRow:
    league_season_id: str
    overall_pick: int
    round: int
    draft_slot: int
    team_id: str
    player_name: str
    position: str
    source_player_id: str | None
    is_keeper: bool | None
    is_autopick: bool | None
    picked_at: datetime | None
    row_fingerprint: str
    player_id: str | None = None
    mapping_confidence: str = "unresolved"


@dataclass(frozen=True)
class _OutcomeRow:
    league_season_id: str
    team_id: str
    wins: float | None
    losses: float | None
    ties: float | None
    points_for: float | None
    points_against: float | None
    seed: int | None
    made_playoffs: bool | None
    final_place: int | None
    is_champion: bool | None
    row_fingerprint: str


@dataclass(frozen=True)
class _NormalizedPackage:
    declaration: _PackageDeclaration
    rules: tuple[_RuleRow, ...]
    picks: tuple[_PickRow, ...]
    outcomes: tuple[_OutcomeRow, ...]
    optional_files: tuple[str, ...]
    normalized_fingerprint: str


@dataclass(frozen=True)
class _LeagueReadinessRow:
    league_season_id: str
    season: int
    team_count: int
    ruleset_fingerprint: str
    expected_pick_rows: int
    actual_pick_rows: int
    outcome_rows: int
    resolved_pick_rows: int
    draft_complete: bool
    outcomes_complete: bool
    analysis_ready: bool


class _RowValueError(ValueError):
    pass


def import_league_history_package(
    config: AppConfig,
    source_path: Path,
) -> LeagueHistoryLoadResult:
    """Archive one upload, then normalize it only when it is a valid v1 ZIP."""

    archive = archive_package(config, source_path)
    return load_archived_league_history_package(config, archive)


def load_league_history_package(
    config: AppConfig,
    source_path: Path,
) -> LeagueHistoryLoadResult:
    """Compatibility-friendly public name for archive-then-import behavior."""

    return import_league_history_package(config, source_path)


def load_archived_league_history_package(
    config: AppConfig,
    archive: LeagueHistoryArchiveResult,
) -> LeagueHistoryLoadResult:
    """Validate and normalize an already immutable league-history archive."""

    raw_sha256 = sha256_file(archive.raw_path)
    if not archive.manifest.sha256 or archive.manifest.sha256[0] != raw_sha256:
        quality = _quality(
            _Metrics(),
            [
                QualityIssue(
                    code="raw_archive_hash_mismatch",
                    message="The archived package no longer matches its SHA-256 manifest.",
                    severity=Severity.FATAL,
                )
            ],
        )
        return _rejected_result(
            config,
            archive,
            raw_sha256,
            quality=quality,
            readiness=_blocked_readiness(None, "Raw archive integrity verification failed."),
        )

    if archive.raw_path.suffix.casefold() != ".zip":
        quality = _quality(
            _Metrics(),
            [
                QualityIssue(
                    code="archive_only_source_format",
                    message=(
                        "Standalone CSV and JSON history files remain immutable archive-only "
                        "evidence; league-history-v1 normalization requires a ZIP package."
                    ),
                )
            ],
        )
        return _result(
            archive,
            raw_sha256,
            status="archive_only",
            quality=quality,
            readiness=_blocked_readiness(
                None, "Only a validated league-history-v1 ZIP can be normalized."
            ),
        )

    metrics = _Metrics()
    issues: list[QualityIssue] = []
    normalized = _read_and_normalize_zip(config, archive.raw_path, metrics, issues)
    quality = _quality(metrics, issues)
    if normalized is None or quality.has_fatal_errors:
        schema_version = normalized.declaration.schema_version if normalized else None
        return _rejected_result(
            config,
            archive,
            raw_sha256,
            quality=quality,
            readiness=_blocked_readiness(schema_version, "Package validation failed."),
            optional_files=normalized.optional_files if normalized else (),
            normalized_fingerprint=normalized.normalized_fingerprint if normalized else None,
        )

    return _commit_package(config, archive, raw_sha256, normalized, metrics, issues)


def _result(
    archive: LeagueHistoryArchiveResult,
    raw_sha256: str,
    *,
    status: Literal["archive_only", "validation_failed", "imported", "already_loaded"],
    quality: QualityReport,
    readiness: LeagueHistoryReadiness,
    optional_files: tuple[str, ...] = (),
    normalized_fingerprint: str | None = None,
    committed: bool = False,
    idempotent_reuse: bool = False,
) -> LeagueHistoryLoadResult:
    return LeagueHistoryLoadResult(
        raw_path=archive.raw_path,
        manifest_path=archive.manifest_path,
        manifest_dataset_id=archive.manifest.dataset_id,
        raw_sha256=raw_sha256,
        package_fingerprint=raw_sha256,
        normalized_fingerprint=normalized_fingerprint,
        status=status,
        committed=committed,
        idempotent_reuse=idempotent_reuse,
        optional_files=optional_files,
        quality=quality,
        readiness=readiness,
    )


def _rejected_result(
    config: AppConfig,
    archive: LeagueHistoryArchiveResult,
    raw_sha256: str,
    *,
    quality: QualityReport,
    readiness: LeagueHistoryReadiness,
    optional_files: tuple[str, ...] = (),
    normalized_fingerprint: str | None = None,
) -> LeagueHistoryLoadResult:
    """Persist a rejected ZIP report without changing canonical source tables."""

    result = _result(
        archive,
        raw_sha256,
        status="validation_failed",
        quality=quality,
        readiness=readiness,
        optional_files=optional_files,
        normalized_fingerprint=normalized_fingerprint,
    )
    reused = _persist_rejected_package(config, archive, result)
    return result.model_copy(update={"idempotent_reuse": reused})


def _persist_rejected_package(
    config: AppConfig,
    archive: LeagueHistoryArchiveResult,
    result: LeagueHistoryLoadResult,
) -> bool:
    warehouse = Warehouse(config.resolve(config.paths.warehouse))
    try:
        warehouse.initialize()
        with warehouse.connect() as connection:
            existing = connection.execute(
                "SELECT 1 FROM league_history_imports WHERE package_fingerprint = ?",
                [result.package_fingerprint],
            ).fetchone()
            if existing is not None:
                return True
            _insert_rejected_import(connection, archive, result)
    except duckdb.Error:
        return False
    return False


def _insert_rejected_import(
    connection: duckdb.DuckDBPyConnection,
    archive: LeagueHistoryArchiveResult,
    result: LeagueHistoryLoadResult,
) -> None:
    quality_payload = _canonical_json(
        {
            "quality": result.quality.model_dump(mode="json"),
            "readiness": result.readiness.as_dict(),
        }
    )
    connection.execute(
        """
        INSERT INTO league_history_imports (
            package_fingerprint, schema_version, manifest_dataset_id, raw_path,
            raw_sha256, normalized_fingerprint, status, league_count, rules_rows,
            pick_rows, outcome_rows, unresolved_player_rows, quality_report, imported_at
        ) VALUES (?, ?, ?, ?, ?, ?, 'rejected', ?, 0, 0, 0, ?, ?, ?)
        """,
        [
            result.package_fingerprint,
            result.readiness.schema_version or "unrecognized",
            archive.manifest.dataset_id,
            archive.manifest.raw_files[0],
            result.raw_sha256,
            result.normalized_fingerprint or result.raw_sha256,
            result.readiness.league_count,
            result.quality.unresolved_players,
            quality_payload,
            utc_now(),
        ],
    )


def _blocked_readiness(schema_version: str | None, reason: str) -> LeagueHistoryReadiness:
    return LeagueHistoryReadiness(schema_version=schema_version, reasons=(reason,))


def _quality(metrics: _Metrics, issues: list[QualityIssue]) -> QualityReport:
    return QualityReport(
        source="league_history",
        row_count=metrics.raw_rows,
        required_field_failures=metrics.required_field_failures,
        duplicate_keys=metrics.duplicate_keys,
        unresolved_players=metrics.unresolved_players,
        identity_conflicts=metrics.identity_conflicts,
        impossible_picks_or_rounds=metrics.impossible_picks_or_rounds,
        unsupported_lineup_slots=metrics.unsupported_lineup_slots,
        invalid_json_settings=metrics.invalid_json_settings,
        issues=issues,
    )


def _read_and_normalize_zip(
    config: AppConfig,
    raw_path: Path,
    metrics: _Metrics,
    issues: list[QualityIssue],
) -> _NormalizedPackage | None:
    try:
        with zipfile.ZipFile(raw_path) as package:
            members = _validate_zip_members(package, issues)
            if _has_fatal(issues):
                return None
            contents = {name: package.read(info) for name, info in members.items()}
    except (OSError, RuntimeError, zipfile.BadZipFile, zipfile.LargeZipFile) as exc:
        _fatal(issues, "invalid_zip_package", f"Unable to read ZIP package: {exc}")
        return None

    declaration = _parse_package_declaration(contents.get(PACKAGE_FILE), issues)
    if declaration is None:
        return None
    _validate_declared_files(declaration, set(contents), issues)
    if _has_fatal(issues):
        return None

    csv_rows: dict[str, list[dict[str, str]]] = {}
    for name, expected_header in REQUIRED_CSV_HEADERS.items():
        rows = _parse_csv(contents[name], name, expected_header, metrics, issues)
        csv_rows[name] = rows
        if not rows:
            metrics.required_field_failures += 1
            _fatal(issues, "empty_required_file", f"{name} must contain at least one data row.")

    optional_files: list[str] = []
    for name, expected_header in OPTIONAL_CSV_HEADERS.items():
        if name not in contents:
            continue
        optional_files.append(name)
        rows = _parse_csv(contents[name], name, expected_header, metrics, issues)
        declared_included = name in declaration.included_files
        if rows and not declared_included:
            _fatal(
                issues,
                "optional_file_flag_mismatch",
                f"{name} has data rows but package.json declares included=false.",
            )
        elif rows:
            issues.append(
                QualityIssue(
                    code="optional_file_archived_only",
                    message=(
                        f"{name} passed header validation and remains archived-only in the "
                        "initial Phase 8 normalization."
                    ),
                    count=len(rows),
                )
            )

    if _has_fatal(issues):
        return None

    rules = _normalize_rules(config, csv_rows["league_rules.csv"], metrics, issues)
    picks = _normalize_picks(csv_rows["draft_picks.csv"], metrics, issues)
    outcomes = _normalize_outcomes(csv_rows["team_outcomes.csv"], metrics, issues)
    _validate_cross_table(rules, picks, outcomes, metrics, issues)
    if _has_fatal(issues):
        return None

    normalized_fingerprint = _fingerprint(
        {
            "schema_version": declaration.schema_version,
            "rules": [_rule_source_payload(row) for row in sorted(rules, key=_rule_sort_key)],
            "picks": [_pick_source_payload(row) for row in sorted(picks, key=_pick_sort_key)],
            "outcomes": [
                _outcome_source_payload(row) for row in sorted(outcomes, key=_outcome_sort_key)
            ],
        }
    )
    return _NormalizedPackage(
        declaration=declaration,
        rules=tuple(rules),
        picks=tuple(picks),
        outcomes=tuple(outcomes),
        optional_files=tuple(sorted(optional_files)),
        normalized_fingerprint=normalized_fingerprint,
    )


def _validate_zip_members(
    package: zipfile.ZipFile,
    issues: list[QualityIssue],
) -> dict[str, zipfile.ZipInfo]:
    infos = package.infolist()
    if len(infos) > MAX_ARCHIVE_ENTRIES:
        _fatal(
            issues,
            "excess_archive_entries",
            f"ZIP contains {len(infos)} entries; maximum is {MAX_ARCHIVE_ENTRIES}.",
        )
        return {}

    members: dict[str, zipfile.ZipInfo] = {}
    folded_names: set[str] = set()
    expanded_bytes = 0
    for info in infos:
        name = info.filename
        posix = PurePosixPath(name)
        windows = PureWindowsPath(name)
        unsafe_path = (
            not name
            or info.is_dir()
            or posix.is_absolute()
            or windows.is_absolute()
            or windows.drive != ""
            or len(posix.parts) != 1
            or any(part in {"", ".", ".."} for part in posix.parts)
        )
        if unsafe_path:
            _fatal(issues, "unsafe_archive_path", f"ZIP entry has an unsafe path: {name!r}.")
            continue
        unix_mode = info.external_attr >> 16
        if stat.S_ISLNK(unix_mode):
            _fatal(issues, "archive_symlink", f"ZIP entry cannot be a symbolic link: {name!r}.")
        if info.flag_bits & 0x1:
            _fatal(issues, "encrypted_archive_entry", f"ZIP entry is encrypted: {name!r}.")
        if name.casefold() in folded_names:
            _fatal(
                issues,
                "archive_name_collision",
                f"ZIP contains a duplicate or case-colliding entry: {name!r}.",
            )
        folded_names.add(name.casefold())
        if name not in ALLOWED_FILES:
            _fatal(issues, "unexpected_archive_file", f"Unexpected ZIP entry: {name!r}.")
        if Path(name).suffix.casefold() in {".zip", ".tar", ".gz", ".7z", ".rar"}:
            _fatal(issues, "nested_archive", f"Nested archives are not allowed: {name!r}.")
        expanded_bytes += info.file_size
        if info.file_size > 0:
            if info.compress_size <= 0:
                _fatal(
                    issues,
                    "suspicious_compression",
                    f"ZIP entry has a zero compressed size: {name!r}.",
                )
            elif info.file_size / info.compress_size > MAX_COMPRESSION_RATIO:
                _fatal(
                    issues,
                    "suspicious_compression",
                    (
                        f"ZIP entry exceeds the {MAX_COMPRESSION_RATIO:g}:1 compression "
                        f"limit: {name!r}."
                    ),
                )
        members[name] = info

    if expanded_bytes > MAX_EXPANDED_BYTES:
        _fatal(
            issues,
            "expanded_package_too_large",
            f"Expanded ZIP size exceeds {MAX_EXPANDED_BYTES // (1024 * 1024)} MB.",
        )
    missing = sorted(REQUIRED_FILES - set(members))
    if missing:
        _fatal(
            issues,
            "missing_required_package_files",
            f"Missing required root files: {', '.join(missing)}.",
            count=len(missing),
        )
    return members


def _parse_package_declaration(
    content: bytes | None,
    issues: list[QualityIssue],
) -> _PackageDeclaration | None:
    if content is None:
        return None
    try:
        payload = json.loads(content.decode("utf-8-sig"))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        _fatal(issues, "invalid_package_json", f"package.json is invalid UTF-8 JSON: {exc}")
        return None
    if not isinstance(payload, dict):
        _fatal(issues, "invalid_package_json", "package.json must contain one JSON object.")
        return None

    expected = {
        "schema_version",
        "package_id",
        "created_at",
        "source_platform",
        "contains_personal_identifiers",
        "files",
    }
    extras = sorted(set(payload) - expected)
    missing = sorted(expected - set(payload))
    if extras or missing:
        _fatal(
            issues,
            "invalid_package_fields",
            f"package.json missing={missing} unexpected={extras}.",
        )
        return None
    if payload["schema_version"] != SCHEMA_VERSION:
        _fatal(
            issues,
            "unsupported_package_schema",
            f"schema_version must be exactly {SCHEMA_VERSION!r}.",
        )
    if payload["contains_personal_identifiers"] is not False:
        _fatal(
            issues,
            "personal_identifiers_not_cleared",
            "contains_personal_identifiers must be the JSON boolean false before import.",
        )

    try:
        package_id = _opaque_id(payload["package_id"], "package_id")
        source_platform = _opaque_id(payload["source_platform"], "source_platform").casefold()
        created_at = _datetime_value(payload["created_at"], "created_at", required=True)
        if created_at is None:
            raise _RowValueError("created_at is required")
        included_files = _parse_file_declarations(payload["files"])
    except _RowValueError as exc:
        _fatal(issues, "invalid_package_fields", str(exc))
        return None
    if _has_fatal(issues):
        return None
    return _PackageDeclaration(
        schema_version=SCHEMA_VERSION,
        package_id=package_id,
        created_at=created_at,
        source_platform=source_platform,
        included_files=included_files,
    )


def _parse_file_declarations(value: object) -> frozenset[str]:
    if not isinstance(value, list):
        raise _RowValueError("package.json files must be an array")
    seen_kinds: set[str] = set()
    seen_paths: set[str] = set()
    included: set[str] = set()
    expected_by_kind = {
        Path(name).stem: (name, name in REQUIRED_CSV_HEADERS)
        for name in (*REQUIRED_CSV_HEADERS, *OPTIONAL_CSV_HEADERS)
    }
    for index, item in enumerate(value, start=1):
        if not isinstance(item, dict) or set(item) != {"kind", "path", "required", "included"}:
            raise _RowValueError(
                f"package.json files entry {index} must contain kind/path/required/included"
            )
        kind = item["kind"]
        path = item["path"]
        if not isinstance(kind, str) or kind not in expected_by_kind:
            raise _RowValueError(f"package.json files entry {index} has an unknown kind")
        expected_path, expected_required = expected_by_kind[kind]
        if path != expected_path:
            raise _RowValueError(
                f"package.json kind {kind!r} must use path {expected_path!r}"
            )
        if item["required"] is not expected_required:
            raise _RowValueError(
                f"package.json kind {kind!r} has an incorrect required flag"
            )
        if not isinstance(item["included"], bool):
            raise _RowValueError(
                f"package.json kind {kind!r} included must be a JSON boolean"
            )
        if expected_required and item["included"] is not True:
            raise _RowValueError(
                f"package.json required kind {kind!r} must declare included=true"
            )
        if kind in seen_kinds or expected_path.casefold() in seen_paths:
            raise _RowValueError(f"package.json declares {kind!r} more than once")
        seen_kinds.add(kind)
        seen_paths.add(expected_path.casefold())
        if item["included"]:
            included.add(expected_path)
    missing_kinds = sorted(set(expected_by_kind) - seen_kinds)
    if missing_kinds:
        raise _RowValueError(
            f"package.json files is missing declarations: {', '.join(missing_kinds)}"
        )
    return frozenset(included)


def _validate_declared_files(
    declaration: _PackageDeclaration,
    actual_files: set[str],
    issues: list[QualityIssue],
) -> None:
    for name in REQUIRED_CSV_HEADERS:
        if name not in declaration.included_files:
            _fatal(issues, "required_file_not_included", f"{name} must declare included=true.")
    for name in declaration.included_files:
        if name not in actual_files:
            _fatal(
                issues,
                "declared_file_missing",
                f"package.json declares {name} included, but it is absent from the ZIP.",
            )


def _parse_csv(
    content: bytes,
    name: str,
    expected_header: tuple[str, ...],
    metrics: _Metrics,
    issues: list[QualityIssue],
) -> list[dict[str, str]]:
    try:
        text = content.decode("utf-8-sig")
    except UnicodeDecodeError as exc:
        _fatal(issues, "invalid_csv_encoding", f"{name} is not valid UTF-8: {exc}")
        return []
    if "\x00" in text:
        _fatal(issues, "invalid_csv_content", f"{name} contains a NUL byte.")
        return []
    try:
        reader = csv.DictReader(io.StringIO(text, newline=""), strict=True)
        actual_header = tuple(reader.fieldnames or ())
        if actual_header != expected_header:
            _fatal(
                issues,
                "invalid_csv_header",
                f"{name} header must be exactly {','.join(expected_header)}.",
            )
            return []
        rows: list[dict[str, str]] = []
        for source_row in reader:
            if None in source_row:
                _fatal(issues, "invalid_csv_row", f"{name} contains an over-wide CSV row.")
                continue
            normalized = {key: (value or "").strip() for key, value in source_row.items()}
            if not any(normalized.values()):
                continue
            rows.append(normalized)
        metrics.raw_rows += len(rows)
        return rows
    except csv.Error as exc:
        _fatal(issues, "invalid_csv_content", f"{name} cannot be parsed: {exc}")
        return []


def _normalize_rules(
    config: AppConfig,
    source_rows: list[dict[str, str]],
    metrics: _Metrics,
    issues: list[QualityIssue],
) -> list[_RuleRow]:
    rows: list[_RuleRow] = []
    seen: set[str] = set()
    for index, source in enumerate(source_rows, start=2):
        try:
            league_id = _opaque_id(source["league_season_id"], "league_season_id")
            platform = _opaque_id(source["platform"], "platform").casefold()
            season = _integer(source["season"], "season", minimum=2000, maximum=2100)
            if season >= config.project.prediction_season:
                raise _RowValueError(
                    f"season must be completed and earlier than {config.project.prediction_season}"
                )
            team_count = _integer(source["team_count"], "team_count", minimum=4, maximum=32)
            draft_type = _required(source["draft_type"], "draft_type").casefold()
            if draft_type != "snake":
                raise _RowValueError("draft_type must be snake")
            draft_date = _datetime_value(source["draft_date"], "draft_date", required=True)
            if draft_date is None:
                raise _RowValueError("draft_date is required")
            rounds = _integer(source["rounds"], "rounds", minimum=1, maximum=40)
            bench_slots = _integer(source["bench_slots"], "bench_slots", minimum=0, maximum=30)
            ir_slots = _integer(source["ir_slots"], "ir_slots", minimum=0, maximum=20)
            playoff_teams = _integer(
                source["playoff_teams"], "playoff_teams", minimum=2, maximum=team_count
            )
            playoff_start = _integer(
                source["playoff_start_week"], "playoff_start_week", minimum=1, maximum=22
            )
            championship = _integer(
                source["championship_week"],
                "championship_week",
                minimum=playoff_start,
                maximum=22,
            )
            scoring = _parse_scoring_json(source["scoring_json"])
            starters, flex_slots = _parse_starter_slots(source["starter_slots_json"])
            unsupported = _unsupported_positions(starters, flex_slots)
            if unsupported:
                metrics.unsupported_lineup_slots += len(unsupported)
                issues.append(
                    QualityIssue(
                        code="unsupported_lineup_slots",
                        message=(
                            f"{league_id} uses positions outside draft-only scoring coverage: "
                            f"{', '.join(unsupported)}. Source facts remain importable."
                        ),
                        count=len(unsupported),
                    )
                )
            rules = LeagueRules(
                season=season,
                teams=team_count,
                draft=DraftSettings(type="snake", rounds=rounds, keepers=0),
                starters=starters,
                flex_slots=tuple(flex_slots),
                bench=bench_slots,
                ir=ir_slots,
                scoring=scoring,
            )
            row_payload = {
                "league_season_id": league_id,
                "platform": platform,
                "draft_date": _iso(draft_date),
                "playoff_teams": playoff_teams,
                "playoff_start_week": playoff_start,
                "championship_week": championship,
                "rules": json.loads(rules.canonical_json()),
            }
            row = _RuleRow(
                league_season_id=league_id,
                platform=platform,
                season=season,
                team_count=team_count,
                draft_date=draft_date,
                rounds=rounds,
                bench_slots=bench_slots,
                ir_slots=ir_slots,
                playoff_teams=playoff_teams,
                playoff_start_week=playoff_start,
                championship_week=championship,
                rules=rules,
                row_fingerprint=_fingerprint(row_payload),
            )
        except (ValueError, TypeError, json.JSONDecodeError) as exc:
            metrics.required_field_failures += 1
            if "JSON" in str(exc) or "json" in str(exc):
                metrics.invalid_json_settings += 1
            _fatal(
                issues,
                "invalid_league_rules_row",
                f"league_rules.csv row {index}: {exc}",
            )
            continue
        if league_id in seen:
            metrics.duplicate_keys += 1
            _fatal(
                issues,
                "duplicate_league_rules_key",
                f"league_rules.csv repeats league_season_id {league_id!r}.",
            )
            continue
        seen.add(league_id)
        rows.append(row)
    return rows


def _normalize_picks(
    source_rows: list[dict[str, str]],
    metrics: _Metrics,
    issues: list[QualityIssue],
) -> list[_PickRow]:
    rows: list[_PickRow] = []
    seen: set[tuple[str, int]] = set()
    for index, source in enumerate(source_rows, start=2):
        try:
            league_id = _opaque_id(source["league_season_id"], "league_season_id")
            overall = _integer(source["overall_pick"], "overall_pick", minimum=1)
            round_number = _integer(source["round"], "round", minimum=1)
            slot = _integer(source["draft_slot"], "draft_slot", minimum=1)
            team_id = _opaque_id(source["team_id"], "team_id")
            player_name = _required(source["player_name"], "player_name")
            position = _required(source["position"], "position").upper()
            source_player_id = source["source_player_id"] or None
            keeper = _boolean(source["is_keeper"], "is_keeper", required=False)
            autopick = _boolean(source["is_autopick"], "is_autopick", required=False)
            picked_at = _datetime_value(source["picked_at"], "picked_at", required=False)
            payload = {
                "league_season_id": league_id,
                "overall_pick": overall,
                "round": round_number,
                "draft_slot": slot,
                "team_id": team_id,
                "player_name": player_name,
                "position": position,
                "source_player_id": source_player_id,
                "is_keeper": keeper,
                "is_autopick": autopick,
                "picked_at": _iso(picked_at),
            }
            row = _PickRow(
                league_season_id=league_id,
                overall_pick=overall,
                round=round_number,
                draft_slot=slot,
                team_id=team_id,
                player_name=player_name,
                position=position,
                source_player_id=source_player_id,
                is_keeper=keeper,
                is_autopick=autopick,
                picked_at=picked_at,
                row_fingerprint=_fingerprint(payload),
            )
        except (ValueError, TypeError) as exc:
            metrics.required_field_failures += 1
            _fatal(issues, "invalid_draft_pick_row", f"draft_picks.csv row {index}: {exc}")
            continue
        key = (league_id, overall)
        if key in seen:
            metrics.duplicate_keys += 1
            _fatal(issues, "duplicate_draft_pick_key", f"Duplicate draft pick key {key!r}.")
            continue
        seen.add(key)
        rows.append(row)
    return rows


def _normalize_outcomes(
    source_rows: list[dict[str, str]],
    metrics: _Metrics,
    issues: list[QualityIssue],
) -> list[_OutcomeRow]:
    rows: list[_OutcomeRow] = []
    seen: set[tuple[str, str]] = set()
    for index, source in enumerate(source_rows, start=2):
        try:
            league_id = _opaque_id(source["league_season_id"], "league_season_id")
            team_id = _opaque_id(source["team_id"], "team_id")
            wins = _number(source["wins"], "wins", minimum=0)
            losses = _number(source["losses"], "losses", minimum=0)
            ties = _number(source["ties"], "ties", minimum=0)
            points_for = _number(source["points_for"], "points_for", minimum=0)
            points_against = _number(source["points_against"], "points_against", minimum=0)
            seed = _integer_optional(source["seed"], "seed", minimum=1)
            playoffs = _boolean(source["made_playoffs"], "made_playoffs", required=False)
            final_place = _integer_optional(source["final_place"], "final_place", minimum=1)
            champion = _boolean(source["is_champion"], "is_champion", required=False)
            if champion is True and final_place not in {None, 1}:
                raise _RowValueError("a champion must have final_place 1 when supplied")
            if champion is True and playoffs is False:
                raise _RowValueError("a champion cannot have made_playoffs=false")
            payload = {
                "league_season_id": league_id,
                "team_id": team_id,
                "wins": wins,
                "losses": losses,
                "ties": ties,
                "points_for": points_for,
                "points_against": points_against,
                "seed": seed,
                "made_playoffs": playoffs,
                "final_place": final_place,
                "is_champion": champion,
            }
            row = _OutcomeRow(
                league_season_id=league_id,
                team_id=team_id,
                wins=wins,
                losses=losses,
                ties=ties,
                points_for=points_for,
                points_against=points_against,
                seed=seed,
                made_playoffs=playoffs,
                final_place=final_place,
                is_champion=champion,
                row_fingerprint=_fingerprint(payload),
            )
        except (ValueError, TypeError) as exc:
            metrics.required_field_failures += 1
            _fatal(
                issues,
                "invalid_team_outcome_row",
                f"team_outcomes.csv row {index}: {exc}",
            )
            continue
        key = (league_id, team_id)
        if key in seen:
            metrics.duplicate_keys += 1
            _fatal(issues, "duplicate_team_outcome_key", f"Duplicate team outcome key {key!r}.")
            continue
        seen.add(key)
        rows.append(row)
    return rows


def _validate_cross_table(
    rules: list[_RuleRow],
    picks: list[_PickRow],
    outcomes: list[_OutcomeRow],
    metrics: _Metrics,
    issues: list[QualityIssue],
) -> None:
    rules_by_league = {row.league_season_id: row for row in rules}
    unknown_pick_leagues = sorted(
        {row.league_season_id for row in picks} - set(rules_by_league)
    )
    unknown_outcome_leagues = sorted(
        {row.league_season_id for row in outcomes} - set(rules_by_league)
    )
    if unknown_pick_leagues:
        _fatal(
            issues,
            "draft_pick_without_rules",
            f"Draft picks reference unknown leagues: {', '.join(unknown_pick_leagues)}.",
            count=len(unknown_pick_leagues),
        )
    if unknown_outcome_leagues:
        _fatal(
            issues,
            "outcome_without_rules",
            f"Outcomes reference unknown leagues: {', '.join(unknown_outcome_leagues)}.",
            count=len(unknown_outcome_leagues),
        )

    for league_id, rule in rules_by_league.items():
        league_picks = [row for row in picks if row.league_season_id == league_id]
        league_outcomes = [row for row in outcomes if row.league_season_id == league_id]
        slot_owners: dict[int, str] = {}
        team_slots: dict[str, int] = {}
        expected_rows = rule.team_count * rule.rounds
        for row in league_picks:
            expected_round = (row.overall_pick - 1) // rule.team_count + 1
            within_round = (row.overall_pick - 1) % rule.team_count + 1
            expected_slot = (
                within_round if expected_round % 2 == 1 else rule.team_count - within_round + 1
            )
            if (
                row.overall_pick > expected_rows
                or row.round != expected_round
                or row.draft_slot != expected_slot
                or row.draft_slot > rule.team_count
            ):
                metrics.impossible_picks_or_rounds += 1
                _fatal(
                    issues,
                    "impossible_pick_or_round",
                    f"{league_id} overall pick {row.overall_pick} disagrees with snake order.",
                )
            prior_team = slot_owners.setdefault(row.draft_slot, row.team_id)
            prior_slot = team_slots.setdefault(row.team_id, row.draft_slot)
            if prior_team != row.team_id or prior_slot != row.draft_slot:
                metrics.impossible_picks_or_rounds += 1
                _fatal(
                    issues,
                    "inconsistent_draft_slot_owner",
                    f"{league_id} does not have a stable team-to-draft-slot mapping.",
                )

        outcome_team_ids = {row.team_id for row in league_outcomes}
        pick_team_ids = {row.team_id for row in league_picks}
        if len(league_picks) == expected_rows and pick_team_ids != outcome_team_ids:
            _fatal(
                issues,
                "team_set_mismatch",
                f"{league_id} complete draft and outcome team IDs do not match.",
            )
        for outcome_row in league_outcomes:
            if outcome_row.seed is not None and outcome_row.seed > rule.team_count:
                _fatal(issues, "invalid_seed", f"{league_id} seed exceeds team_count.")
            if outcome_row.final_place is not None and outcome_row.final_place > rule.team_count:
                _fatal(
                    issues,
                    "invalid_final_place",
                    f"{league_id} final_place exceeds team_count.",
                )
        champions = [row for row in league_outcomes if row.is_champion is True]
        if len(champions) > 1:
            _fatal(
                issues,
                "multiple_champions",
                f"{league_id} contains more than one champion.",
                count=len(champions),
            )
        if len(league_outcomes) == rule.team_count:
            if len(champions) != 1:
                _fatal(
                    issues,
                    "complete_outcomes_require_champion",
                    f"{league_id} has complete team rows but does not have exactly one champion.",
                )
            playoff_values = [row.made_playoffs for row in league_outcomes]
            if all(value is not None for value in playoff_values):
                playoff_count = sum(value is True for value in playoff_values)
                if playoff_count != rule.playoff_teams:
                    _fatal(
                        issues,
                        "playoff_count_mismatch",
                        f"{league_id} playoff flags do not match playoff_teams.",
                    )


def _commit_package(
    config: AppConfig,
    archive: LeagueHistoryArchiveResult,
    raw_sha256: str,
    normalized: _NormalizedPackage,
    metrics: _Metrics,
    issues: list[QualityIssue],
) -> LeagueHistoryLoadResult:
    warehouse = Warehouse(config.resolve(config.paths.warehouse))
    warehouse.initialize()
    with warehouse.connect() as connection:
        existing = connection.execute(
            """
            SELECT status, quality_report, normalized_fingerprint
            FROM league_history_imports WHERE package_fingerprint = ?
            """,
            [raw_sha256],
        ).fetchone()
        if existing is not None:
            payload = json.loads(str(existing[1]))
            stored_quality = QualityReport.model_validate(payload["quality"])
            stored_readiness = LeagueHistoryReadiness.model_validate(payload["readiness"])
            if str(existing[0]) != "imported":
                return _result(
                    archive,
                    raw_sha256,
                    status="validation_failed",
                    quality=stored_quality,
                    readiness=stored_readiness,
                    optional_files=normalized.optional_files,
                    normalized_fingerprint=str(existing[2]),
                    idempotent_reuse=True,
                )
            return _result(
                archive,
                raw_sha256,
                status="already_loaded",
                quality=stored_quality,
                readiness=stored_readiness,
                optional_files=normalized.optional_files,
                normalized_fingerprint=normalized.normalized_fingerprint,
                committed=True,
                idempotent_reuse=True,
            )

        normalized_existing = connection.execute(
            """
            SELECT quality_report
            FROM league_history_imports
            WHERE normalized_fingerprint = ? AND status = 'imported'
            ORDER BY imported_at, package_fingerprint
            LIMIT 1
            """,
            [normalized.normalized_fingerprint],
        ).fetchone()
        if normalized_existing is not None:
            payload = json.loads(str(normalized_existing[0]))
            stored_quality = QualityReport.model_validate(payload["quality"])
            stored_readiness = LeagueHistoryReadiness.model_validate(payload["readiness"])
            return _result(
                archive,
                raw_sha256,
                status="already_loaded",
                quality=stored_quality,
                readiness=stored_readiness,
                optional_files=normalized.optional_files,
                normalized_fingerprint=normalized.normalized_fingerprint,
                committed=True,
                idempotent_reuse=True,
            )

        connection.execute("BEGIN TRANSACTION")
        try:
            resolved_picks = _resolve_player_ids(connection, normalized, metrics, issues)
            league_rows = _league_readiness_rows(normalized, resolved_picks)
            _validate_warehouse_conflicts(
                connection, normalized, resolved_picks, league_rows, issues
            )
            if _has_fatal(issues):
                connection.execute("ROLLBACK")
                quality = _quality(metrics, issues)
                rejected = _result(
                    archive,
                    raw_sha256,
                    status="validation_failed",
                    quality=quality,
                    readiness=_blocked_readiness(
                        normalized.declaration.schema_version,
                        "Canonical source facts conflict with existing warehouse rows.",
                    ),
                    optional_files=normalized.optional_files,
                    normalized_fingerprint=normalized.normalized_fingerprint,
                )
                _insert_rejected_import(connection, archive, rejected)
                return rejected

            if metrics.unresolved_players:
                issues.append(
                    QualityIssue(
                        code="unresolved_player_mappings",
                        message=(
                            "Draft picks without a canonical/source-ID or reviewed mapping were "
                            "retained with player_id null; display names were not joined."
                        ),
                        count=metrics.unresolved_players,
                    )
                )
            readiness = _readiness(normalized.declaration.schema_version, league_rows)
            quality = _quality(metrics, issues)
            imported_at = utc_now()
            _insert_rules(
                connection, normalized, archive.manifest.dataset_id, imported_at
            )
            _insert_picks(
                connection,
                normalized,
                resolved_picks,
                archive.manifest.dataset_id,
                imported_at,
            )
            _insert_outcomes(
                connection, normalized, archive.manifest.dataset_id, imported_at
            )
            _insert_league_readiness(connection, raw_sha256, league_rows)
            quality_payload = _canonical_json(
                {"quality": quality.model_dump(mode="json"), "readiness": readiness.as_dict()}
            )
            connection.execute(
                """
                INSERT INTO league_history_imports (
                    package_fingerprint, schema_version, manifest_dataset_id, raw_path,
                    raw_sha256, normalized_fingerprint, status, league_count, rules_rows,
                    pick_rows, outcome_rows, unresolved_player_rows, quality_report, imported_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                [
                    raw_sha256,
                    normalized.declaration.schema_version,
                    archive.manifest.dataset_id,
                    archive.manifest.raw_files[0],
                    raw_sha256,
                    normalized.normalized_fingerprint,
                    "imported",
                    len(normalized.rules),
                    len(normalized.rules),
                    len(resolved_picks),
                    len(normalized.outcomes),
                    metrics.unresolved_players,
                    quality_payload,
                    imported_at,
                ],
            )
            connection.execute("COMMIT")
        except (duckdb.Error, ValueError, TypeError) as exc:
            connection.execute("ROLLBACK")
            _fatal(issues, "warehouse_import_failed", f"Warehouse import rolled back: {exc}")
            quality = _quality(metrics, issues)
            rejected = _result(
                archive,
                raw_sha256,
                status="validation_failed",
                quality=quality,
                readiness=_blocked_readiness(
                    normalized.declaration.schema_version,
                    "The canonical warehouse transaction rolled back.",
                ),
                optional_files=normalized.optional_files,
                normalized_fingerprint=normalized.normalized_fingerprint,
            )
            with suppress(duckdb.Error):
                _insert_rejected_import(connection, archive, rejected)
            return rejected

    return _result(
        archive,
        raw_sha256,
        status="imported",
        quality=quality,
        readiness=readiness,
        optional_files=normalized.optional_files,
        normalized_fingerprint=normalized.normalized_fingerprint,
        committed=True,
    )


def _resolve_player_ids(
    connection: duckdb.DuckDBPyConnection,
    normalized: _NormalizedPackage,
    metrics: _Metrics,
    issues: list[QualityIssue],
) -> tuple[_PickRow, ...]:
    players = connection.execute(
        """
        SELECT player_id, canonical_position, gsis_id, espn_id, sleeper_id, yahoo_id,
               mfl_id, fleaflicker_id, fantasypros_id
        FROM players
        """
    ).fetchall()
    canonical_positions = {
        str(player_record[0]): str(player_record[1] or "").upper()
        for player_record in players
    }
    by_source: dict[tuple[str, str], set[str]] = {}
    source_columns = ("nflverse", "espn", "sleeper", "yahoo", "mfl", "fleaflicker", "fantasypros")
    for player_record in players:
        player_id = str(player_record[0])
        by_source.setdefault(("canonical", player_id), set()).add(player_id)
        for source, source_id in zip(source_columns, player_record[2:], strict=True):
            if source_id is not None and str(source_id).strip():
                by_source.setdefault((source, str(source_id)), set()).add(player_id)

    reviewed: dict[tuple[str, str], str] = {
        (str(source).casefold(), str(source_id)): str(player_id)
        for source, source_id, player_id in connection.execute(
            """
            SELECT source, source_player_id, player_id
            FROM player_source_mappings
            WHERE mapping_confidence = 'reviewed'
            """
        ).fetchall()
    }
    rules_by_league = {row.league_season_id: row for row in normalized.rules}
    resolved: list[_PickRow] = []
    for pick_row in normalized.picks:
        source_id = pick_row.source_player_id
        if source_id is None:
            metrics.unresolved_players += 1
            resolved.append(pick_row)
            continue
        source = _identity_source(rules_by_league[pick_row.league_season_id].platform)
        candidates: set[str] = set()
        if source == "canonical":
            candidates.update(by_source.get(("canonical", source_id), set()))
        candidates.update(by_source.get((source, source_id), set()))
        if mapped := reviewed.get((source, source_id)):
            if mapped not in canonical_positions:
                metrics.identity_conflicts += 1
                _fatal(
                    issues,
                    "orphan_reviewed_player_mapping",
                    f"{source}:{source_id} maps to missing canonical player {mapped!r}.",
                )
            else:
                candidates.add(mapped)
        if len(candidates) > 1:
            metrics.identity_conflicts += 1
            _fatal(
                issues,
                "conflicting_player_identity",
                f"{source}:{source_id} resolves to multiple canonical player IDs.",
            )
            resolved.append(pick_row)
            continue
        if not candidates:
            metrics.unresolved_players += 1
            resolved.append(pick_row)
            continue
        player_id = next(iter(candidates))
        confidence = "reviewed" if (source, source_id) in reviewed else "exact"
        canonical_position = canonical_positions.get(player_id, "")
        if canonical_position and canonical_position != pick_row.position:
            metrics.identity_conflicts += 1
            issues.append(
                QualityIssue(
                    code="source_position_conflict",
                    message=(
                        f"{source}:{source_id} reports {pick_row.position}, while canonical player "
                        f"{player_id} reports {canonical_position}; exact ID mapping was retained."
                    ),
                )
            )
        resolved.append(replace(pick_row, player_id=player_id, mapping_confidence=confidence))
    return tuple(resolved)


def _league_readiness_rows(
    normalized: _NormalizedPackage,
    picks: tuple[_PickRow, ...],
) -> tuple[_LeagueReadinessRow, ...]:
    rows: list[_LeagueReadinessRow] = []
    for rule in sorted(normalized.rules, key=_rule_sort_key):
        league_picks = [row for row in picks if row.league_season_id == rule.league_season_id]
        league_outcomes = [
            row for row in normalized.outcomes if row.league_season_id == rule.league_season_id
        ]
        expected = rule.team_count * rule.rounds
        actual = len(league_picks)
        outcome_count = len(league_outcomes)
        resolved_count = sum(row.player_id is not None for row in league_picks)
        draft_complete = actual == expected
        outcomes_complete = outcome_count == rule.team_count
        analysis_ready = draft_complete and outcomes_complete and resolved_count == actual
        rows.append(
            _LeagueReadinessRow(
                league_season_id=rule.league_season_id,
                season=rule.season,
                team_count=rule.team_count,
                ruleset_fingerprint=rule.rules.fingerprint(),
                expected_pick_rows=expected,
                actual_pick_rows=actual,
                outcome_rows=outcome_count,
                resolved_pick_rows=resolved_count,
                draft_complete=draft_complete,
                outcomes_complete=outcomes_complete,
                analysis_ready=analysis_ready,
            )
        )
    return tuple(rows)


def _readiness(
    schema_version: str,
    league_rows: tuple[_LeagueReadinessRow, ...],
) -> LeagueHistoryReadiness:
    analysis_ready = sum(row.analysis_ready for row in league_rows)
    reasons = [
        "Championship modeling remains disabled until the separate data-sufficiency gate passes."
    ]
    if not analysis_ready:
        reasons.append(
            "No league has a complete draft, complete outcomes, and 100% resolved draft picks."
        )
    return LeagueHistoryReadiness(
        schema_version=schema_version,
        normalized=True,
        league_count=len(league_rows),
        draft_complete_leagues=sum(row.draft_complete for row in league_rows),
        outcomes_complete_leagues=sum(row.outcomes_complete for row in league_rows),
        analysis_ready_leagues=analysis_ready,
        reasons=tuple(reasons),
    )


def _validate_warehouse_conflicts(
    connection: duckdb.DuckDBPyConnection,
    normalized: _NormalizedPackage,
    picks: tuple[_PickRow, ...],
    league_rows: tuple[_LeagueReadinessRow, ...],
    issues: list[QualityIssue],
) -> None:
    for rule_row in normalized.rules:
        existing = connection.execute(
            "SELECT user_draft_slot, row_fingerprint FROM league_rules WHERE league_season_id = ?",
            [rule_row.league_season_id],
        ).fetchone()
        if existing is not None:
            _fatal(
                issues,
                "league_rules_conflict",
                (
                    f"League {rule_row.league_season_id} is already owned by a local setup or "
                    "a different normalized package; existing rows were not changed."
                ),
            )
    for pick_row in picks:
        existing = connection.execute(
            "SELECT row_fingerprint FROM draft_picks "
            "WHERE league_season_id = ? AND overall_pick = ?",
            [pick_row.league_season_id, pick_row.overall_pick],
        ).fetchone()
        if existing is not None and str(existing[0] or "") != pick_row.row_fingerprint:
            _fatal(
                issues,
                "draft_pick_conflict",
                (
                    "Draft pick source facts conflict at "
                    f"{pick_row.league_season_id}:{pick_row.overall_pick}."
                ),
            )
    for outcome_row in normalized.outcomes:
        existing = connection.execute(
            "SELECT row_fingerprint FROM team_outcomes WHERE league_season_id = ? AND team_id = ?",
            [outcome_row.league_season_id, outcome_row.team_id],
        ).fetchone()
        if existing is not None and str(existing[0] or "") != outcome_row.row_fingerprint:
            _fatal(
                issues,
                "team_outcome_conflict",
                (
                    "Team outcome source facts conflict at "
                    f"{outcome_row.league_season_id}:{outcome_row.team_id}."
                ),
            )
    for readiness_row in league_rows:
        existing = connection.execute(
            """
            SELECT season, team_count, ruleset_fingerprint, expected_pick_rows,
                   actual_pick_rows, outcome_rows, resolved_pick_rows, draft_complete,
                   outcomes_complete, analysis_ready
            FROM league_history_leagues WHERE league_season_id = ?
            """,
            [readiness_row.league_season_id],
        ).fetchone()
        expected = (
            readiness_row.season,
            readiness_row.team_count,
            readiness_row.ruleset_fingerprint,
            readiness_row.expected_pick_rows,
            readiness_row.actual_pick_rows,
            readiness_row.outcome_rows,
            readiness_row.resolved_pick_rows,
            readiness_row.draft_complete,
            readiness_row.outcomes_complete,
            readiness_row.analysis_ready,
        )
        if existing is not None and tuple(existing) != expected:
            _fatal(
                issues,
                "league_readiness_conflict",
                f"Derived readiness conflicts for {readiness_row.league_season_id}.",
            )


def _insert_rules(
    connection: duckdb.DuckDBPyConnection,
    normalized: _NormalizedPackage,
    source_dataset_id: str,
    imported_at: datetime,
) -> None:
    for row in normalized.rules:
        if connection.execute(
            "SELECT 1 FROM league_rules WHERE league_season_id = ?", [row.league_season_id]
        ).fetchone():
            continue
        connection.execute(
            """
            INSERT INTO league_rules (
                league_season_id, platform, season, team_count, user_draft_slot, draft_type,
                rounds, starter_slots_json, flex_slots_json, bench_slots, ir_slots,
                scoring_json, playoff_settings_json, normalized_ruleset_json,
                ruleset_fingerprint, draft_date, source_dataset_id, row_fingerprint, loaded_at
            ) VALUES (?, ?, ?, ?, NULL, 'snake', ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            [
                row.league_season_id,
                row.platform,
                row.season,
                row.team_count,
                row.rounds,
                _canonical_json(row.rules.starters),
                _canonical_json(
                    [slot.model_dump(mode="json") for slot in row.rules.flex_slots]
                ),
                row.bench_slots,
                row.ir_slots,
                _canonical_json(row.rules.scoring.model_dump(mode="json")),
                _canonical_json(
                    {
                        "playoff_teams": row.playoff_teams,
                        "playoff_start_week": row.playoff_start_week,
                        "championship_week": row.championship_week,
                    }
                ),
                row.rules.canonical_json(),
                row.rules.fingerprint(),
                row.draft_date,
                source_dataset_id,
                row.row_fingerprint,
                imported_at,
            ],
        )


def _insert_picks(
    connection: duckdb.DuckDBPyConnection,
    normalized: _NormalizedPackage,
    picks: tuple[_PickRow, ...],
    source_dataset_id: str,
    imported_at: datetime,
) -> None:
    platform_by_league = {row.league_season_id: row.platform for row in normalized.rules}
    for row in picks:
        existing = connection.execute(
            "SELECT row_fingerprint FROM draft_picks "
            "WHERE league_season_id = ? AND overall_pick = ?",
            [row.league_season_id, row.overall_pick],
        ).fetchone()
        if existing is not None:
            connection.execute(
                """
                UPDATE draft_picks
                SET player_id = ?, mapping_confidence = ?
                WHERE league_season_id = ? AND overall_pick = ? AND row_fingerprint = ?
                """,
                [
                    row.player_id,
                    row.mapping_confidence,
                    row.league_season_id,
                    row.overall_pick,
                    row.row_fingerprint,
                ],
            )
            continue
        connection.execute(
            """
            INSERT INTO draft_picks (
                league_season_id, overall_pick, round, draft_slot, team_id, player_id,
                player_name, is_keeper, is_autopick, picked_at, adp_snapshot_id, position,
                source_platform, source_player_id, mapping_confidence, source_dataset_id,
                row_fingerprint, loaded_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, NULL, ?, ?, ?, ?, ?, ?, ?)
            """,
            [
                row.league_season_id,
                row.overall_pick,
                row.round,
                row.draft_slot,
                row.team_id,
                row.player_id,
                row.player_name,
                row.is_keeper,
                row.is_autopick,
                row.picked_at,
                row.position,
                _identity_source(platform_by_league[row.league_season_id]),
                row.source_player_id,
                row.mapping_confidence,
                source_dataset_id,
                row.row_fingerprint,
                imported_at,
            ],
        )


def _insert_outcomes(
    connection: duckdb.DuckDBPyConnection,
    normalized: _NormalizedPackage,
    source_dataset_id: str,
    imported_at: datetime,
) -> None:
    for row in normalized.outcomes:
        if connection.execute(
            "SELECT 1 FROM team_outcomes WHERE league_season_id = ? AND team_id = ?",
            [row.league_season_id, row.team_id],
        ).fetchone():
            continue
        connection.execute(
            """
            INSERT INTO team_outcomes (
                league_season_id, team_id, wins, losses, ties, points_for, points_against,
                all_play_percentile, points_percentile, seed, made_playoffs, final_place,
                is_champion, draft_only_metrics, source_dataset_id, row_fingerprint, loaded_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, NULL, NULL, ?, ?, ?, ?, NULL, ?, ?, ?)
            """,
            [
                row.league_season_id,
                row.team_id,
                row.wins,
                row.losses,
                row.ties,
                row.points_for,
                row.points_against,
                row.seed,
                row.made_playoffs,
                row.final_place,
                row.is_champion,
                source_dataset_id,
                row.row_fingerprint,
                imported_at,
            ],
        )


def _insert_league_readiness(
    connection: duckdb.DuckDBPyConnection,
    package_fingerprint: str,
    rows: tuple[_LeagueReadinessRow, ...],
) -> None:
    for row in rows:
        if connection.execute(
            "SELECT 1 FROM league_history_leagues WHERE league_season_id = ?",
            [row.league_season_id],
        ).fetchone():
            continue
        connection.execute(
            """
            INSERT INTO league_history_leagues (
                league_season_id, package_fingerprint, season, team_count,
                ruleset_fingerprint, expected_pick_rows, actual_pick_rows, outcome_rows,
                resolved_pick_rows, draft_complete, outcomes_complete, analysis_ready
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            [
                row.league_season_id,
                package_fingerprint,
                row.season,
                row.team_count,
                row.ruleset_fingerprint,
                row.expected_pick_rows,
                row.actual_pick_rows,
                row.outcome_rows,
                row.resolved_pick_rows,
                row.draft_complete,
                row.outcomes_complete,
                row.analysis_ready,
            ],
        )


def _parse_scoring_json(value: str) -> ScoringRules:
    try:
        payload = json.loads(_required(value, "scoring_json"))
    except json.JSONDecodeError as exc:
        raise _RowValueError(f"scoring_json is invalid JSON: {exc}") from exc
    if not isinstance(payload, dict):
        raise _RowValueError("scoring_json must contain an object")
    try:
        return ScoringRules.model_validate(payload)
    except ValueError as exc:
        raise _RowValueError(f"scoring_json failed validation: {exc}") from exc


def _parse_starter_slots(value: str) -> tuple[dict[str, int], list[FlexSlot]]:
    try:
        payload = json.loads(_required(value, "starter_slots_json"))
    except json.JSONDecodeError as exc:
        raise _RowValueError(f"starter_slots_json is invalid JSON: {exc}") from exc
    if not isinstance(payload, dict):
        raise _RowValueError("starter_slots_json must contain an object")

    if set(payload) <= {"starters", "flex_slots"} and "starters" in payload:
        direct = payload["starters"]
        flex_payload = payload.get("flex_slots", [])
        if not isinstance(direct, dict) or not isinstance(flex_payload, list):
            raise _RowValueError(
                "nested starter_slots_json requires starters object and flex_slots array"
            )
        nested_starters = {
            str(position).upper(): _json_integer(count, f"starter {position}")
            for position, count in direct.items()
        }
        try:
            nested_flex_slots = [FlexSlot.model_validate(item) for item in flex_payload]
        except ValueError as exc:
            raise _RowValueError(f"flex_slots failed validation: {exc}") from exc
        if not any(nested_starters.values()) and not nested_flex_slots:
            raise _RowValueError("starter_slots_json must define at least one starting slot")
        return nested_starters, nested_flex_slots

    starters: dict[str, int] = {}
    flex_slots: list[FlexSlot] = []
    for slot_name, slot_value in payload.items():
        normalized_name = str(slot_name).strip().upper()
        if isinstance(slot_value, dict):
            if set(slot_value) != {"count", "eligible"}:
                raise _RowValueError(
                    f"flex slot {normalized_name} must contain count and eligible"
                )
            eligible = slot_value["eligible"]
            if not isinstance(eligible, list) or not all(
                isinstance(position, str) and position.strip() for position in eligible
            ):
                raise _RowValueError(
                    f"flex slot {normalized_name} eligible must be an array of positions"
                )
            try:
                flex_slots.append(
                    FlexSlot(
                        name=normalized_name,
                        count=_json_integer(slot_value["count"], f"{normalized_name} count"),
                        eligible=tuple(eligible),
                    )
                )
            except (TypeError, ValueError) as exc:
                raise _RowValueError(f"flex slot {normalized_name} is invalid: {exc}") from exc
        else:
            starters[normalized_name] = _json_integer(slot_value, f"starter {normalized_name}")
    if not any(starters.values()) and not flex_slots:
        raise _RowValueError("starter_slots_json must define at least one starting slot")
    return starters, flex_slots


def _unsupported_positions(starters: dict[str, int], flex_slots: list[FlexSlot]) -> list[str]:
    positions = set(starters)
    positions.update(position for slot in flex_slots for position in slot.eligible)
    return sorted(positions - SUPPORTED_PLAYER_POSITIONS)


def _identity_source(platform: str) -> str:
    """Map descriptive package platform labels to canonical identity namespaces."""

    normalized = platform.casefold()
    for source in ("espn", "sleeper", "yahoo", "mfl", "fleaflicker", "fantasypros"):
        if normalized == source or normalized.startswith(f"{source}_"):
            return source
    if normalized in {"nflverse", "gsis"}:
        return "nflverse"
    return normalized


def _required(value: object, name: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise _RowValueError(f"{name} is required")
    return value.strip()


def _opaque_id(value: object, name: str) -> str:
    normalized = _required(value, name)
    if not OPAQUE_ID_PATTERN.fullmatch(normalized):
        raise _RowValueError(
            f"{name} must be an opaque ID using only letters, digits, hyphens, and underscores"
        )
    return normalized


def _integer(
    value: object,
    name: str,
    *,
    minimum: int | None = None,
    maximum: int | None = None,
) -> int:
    text = _required(value, name)
    try:
        number = float(text)
    except ValueError as exc:
        raise _RowValueError(f"{name} must be an integer") from exc
    if not math.isfinite(number) or not number.is_integer():
        raise _RowValueError(f"{name} must be an integer")
    result = int(number)
    if minimum is not None and result < minimum:
        raise _RowValueError(f"{name} must be at least {minimum}")
    if maximum is not None and result > maximum:
        raise _RowValueError(f"{name} cannot exceed {maximum}")
    return result


def _integer_optional(
    value: object,
    name: str,
    *,
    minimum: int | None = None,
    maximum: int | None = None,
) -> int | None:
    if not isinstance(value, str) or not value.strip():
        return None
    return _integer(value, name, minimum=minimum, maximum=maximum)


def _number(value: object, name: str, *, minimum: float | None = None) -> float | None:
    if not isinstance(value, str) or not value.strip():
        return None
    try:
        result = float(value)
    except ValueError as exc:
        raise _RowValueError(f"{name} must be numeric") from exc
    if not math.isfinite(result):
        raise _RowValueError(f"{name} must be finite")
    if minimum is not None and result < minimum:
        raise _RowValueError(f"{name} must be at least {minimum:g}")
    return result


def _boolean(value: object, name: str, *, required: bool) -> bool | None:
    if not isinstance(value, str) or not value.strip():
        if required:
            raise _RowValueError(f"{name} is required")
        return None
    normalized = value.strip().casefold()
    if normalized == "true":
        return True
    if normalized == "false":
        return False
    raise _RowValueError(f"{name} must be true, false, or blank")


def _datetime_value(value: object, name: str, *, required: bool) -> datetime | None:
    if not isinstance(value, str) or not value.strip():
        if required:
            raise _RowValueError(f"{name} is required")
        return None
    text = value.strip()
    try:
        if len(text) == 10:
            parsed_date = date.fromisoformat(text)
            return datetime.combine(parsed_date, datetime.min.time(), tzinfo=UTC)
        parsed = datetime.fromisoformat(text.replace("Z", "+00:00"))
    except ValueError as exc:
        raise _RowValueError(f"{name} must be an ISO 8601 date or timestamp") from exc
    return parsed.replace(tzinfo=UTC) if parsed.tzinfo is None else parsed.astimezone(UTC)


def _json_integer(value: object, name: str) -> int:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise _RowValueError(f"{name} must be an integer")
    number = float(value)
    if not number.is_integer() or number < 0:
        raise _RowValueError(f"{name} must be a nonnegative integer")
    return int(number)


def _rule_source_payload(row: _RuleRow) -> dict[str, object]:
    return {
        "league_season_id": row.league_season_id,
        "platform": row.platform,
        "draft_date": _iso(row.draft_date),
        "playoff_teams": row.playoff_teams,
        "playoff_start_week": row.playoff_start_week,
        "championship_week": row.championship_week,
        "rules": json.loads(row.rules.canonical_json()),
    }


def _pick_source_payload(row: _PickRow) -> dict[str, object]:
    return {
        "league_season_id": row.league_season_id,
        "overall_pick": row.overall_pick,
        "round": row.round,
        "draft_slot": row.draft_slot,
        "team_id": row.team_id,
        "player_name": row.player_name,
        "position": row.position,
        "source_player_id": row.source_player_id,
        "is_keeper": row.is_keeper,
        "is_autopick": row.is_autopick,
        "picked_at": _iso(row.picked_at),
    }


def _outcome_source_payload(row: _OutcomeRow) -> dict[str, object]:
    return {
        "league_season_id": row.league_season_id,
        "team_id": row.team_id,
        "wins": row.wins,
        "losses": row.losses,
        "ties": row.ties,
        "points_for": row.points_for,
        "points_against": row.points_against,
        "seed": row.seed,
        "made_playoffs": row.made_playoffs,
        "final_place": row.final_place,
        "is_champion": row.is_champion,
    }


def _rule_sort_key(row: _RuleRow) -> str:
    return row.league_season_id


def _pick_sort_key(row: _PickRow) -> tuple[str, int]:
    return row.league_season_id, row.overall_pick


def _outcome_sort_key(row: _OutcomeRow) -> tuple[str, str]:
    return row.league_season_id, row.team_id


def _fingerprint(payload: object) -> str:
    return hashlib.sha256(_canonical_json(payload).encode("utf-8")).hexdigest()


def _canonical_json(payload: object) -> str:
    return json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=True)


def _iso(value: datetime | None) -> str | None:
    return value.astimezone(UTC).isoformat().replace("+00:00", "Z") if value else None


def _fatal(
    issues: list[QualityIssue],
    code: str,
    message: str,
    *,
    count: int = 1,
) -> None:
    issues.append(QualityIssue(code=code, message=message, count=count, severity=Severity.FATAL))


def _has_fatal(issues: list[QualityIssue]) -> bool:
    return any(issue.severity == Severity.FATAL for issue in issues)
