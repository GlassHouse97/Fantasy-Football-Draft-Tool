"""Typed Phase 7 service boundary for local data inventory and safe actions.

The Streamlit Data Center consumes this module instead of reading manifests or
DuckDB directly. Inventory reads never modify raw files, and the action runner
allows only explicit read-only, idempotent-local, or immutable-archive operations.
"""

from __future__ import annotations

import json
from collections import defaultdict
from collections.abc import Mapping
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Literal, TypeAlias

import duckdb

from fantasy_draft_ai.config import AppConfig
from fantasy_draft_ai.data.audit import AuditResult, audit_project_data
from fantasy_draft_ai.data.manifests import SourceManifest, sha256_file
from fantasy_draft_ai.data.sources.espn import import_espn_adp
from fantasy_draft_ai.data.sources.ffc_adp import SUPPORTED_FORMATS, snapshot_ffc_adp
from fantasy_draft_ai.data.sources.league_history import (
    SUPPORTED_HISTORY_SUFFIXES,
    archive_league_history_package,
)
from fantasy_draft_ai.data.sources.nflverse import (
    download_nflverse,
    download_nflverse_snap_counts,
)
from fantasy_draft_ai.data.warehouse import Warehouse

ActionMode = Literal[
    "read_only",
    "idempotent_local",
    "immutable_archive",
    "cli_only",
    "unsupported",
]
ParameterValue: TypeAlias = str | int | float | bool | None


@dataclass(frozen=True)
class ManifestFileInventory:
    """One immutable raw file referenced by a source manifest."""

    relative_path: str
    expected_sha256: str
    actual_sha256: str | None
    exists: bool
    verified: bool
    size_bytes: int | None

    def as_dict(self) -> dict[str, object]:
        return {
            "relative_path": self.relative_path,
            "expected_sha256": self.expected_sha256,
            "actual_sha256": self.actual_sha256,
            "exists": self.exists,
            "verified": self.verified,
            "size_bytes": self.size_bytes,
        }


@dataclass(frozen=True)
class ManifestInventory:
    """Parsed provenance metadata and verification state for one manifest."""

    dataset_id: str
    source: str
    acquisition_method: str
    acquired_at: datetime | None
    seasons: tuple[int, ...]
    schema_version: str
    notes: str
    manifest_path: str
    files: tuple[ManifestFileInventory, ...]
    valid: bool
    issues: tuple[str, ...]

    @property
    def verified_files(self) -> int:
        return sum(file.verified for file in self.files)

    def as_dict(self) -> dict[str, object]:
        return {
            "dataset_id": self.dataset_id,
            "source": self.source,
            "acquisition_method": self.acquisition_method,
            "acquired_at": self.acquired_at.isoformat() if self.acquired_at else None,
            "seasons": list(self.seasons),
            "schema_version": self.schema_version,
            "notes": self.notes,
            "manifest_path": self.manifest_path,
            "files": [file.as_dict() for file in self.files],
            "valid": self.valid,
            "issues": list(self.issues),
        }


@dataclass(frozen=True)
class SourceInventory:
    """Aggregate immutable archive coverage for one named source."""

    source: str
    manifest_count: int
    valid_manifest_count: int
    file_count: int
    verified_file_count: int
    seasons: tuple[int, ...]
    latest_acquired_at: datetime | None

    @property
    def fully_verified(self) -> bool:
        return self.manifest_count > 0 and self.valid_manifest_count == self.manifest_count

    def as_dict(self) -> dict[str, object]:
        return {
            "source": self.source,
            "manifest_count": self.manifest_count,
            "valid_manifest_count": self.valid_manifest_count,
            "file_count": self.file_count,
            "verified_file_count": self.verified_file_count,
            "seasons": list(self.seasons),
            "latest_acquired_at": (
                self.latest_acquired_at.isoformat() if self.latest_acquired_at else None
            ),
            "fully_verified": self.fully_verified,
        }


@dataclass(frozen=True)
class WarehouseTableSummary:
    """Read-model row count for a canonical DuckDB table."""

    name: str
    row_count: int
    domain: str

    def as_dict(self) -> dict[str, object]:
        return {"name": self.name, "row_count": self.row_count, "domain": self.domain}


@dataclass(frozen=True)
class WarehouseSummary:
    """Truthful warehouse availability and row-count summary."""

    path: Path
    exists: bool
    readable: bool
    tables: tuple[WarehouseTableSummary, ...]
    issue: str | None = None

    @property
    def total_rows(self) -> int:
        return sum(table.row_count for table in self.tables)

    def table_count(self, name: str) -> int | None:
        return next((table.row_count for table in self.tables if table.name == name), None)

    def as_dict(self) -> dict[str, object]:
        return {
            "path": str(self.path),
            "exists": self.exists,
            "readable": self.readable,
            "total_rows": self.total_rows,
            "tables": [table.as_dict() for table in self.tables],
            "issue": self.issue,
        }


@dataclass(frozen=True)
class QualitySummary:
    """Reconciled manifest and warehouse audit result."""

    completed: bool
    passed: bool
    manifest_count: int
    verified_files: int
    failures: tuple[str, ...]

    @property
    def status(self) -> str:
        if not self.completed:
            return "unavailable"
        return "passed" if self.passed else "failed"

    def as_dict(self) -> dict[str, object]:
        return {
            "completed": self.completed,
            "passed": self.passed,
            "status": self.status,
            "manifest_count": self.manifest_count,
            "verified_files": self.verified_files,
            "failures": list(self.failures),
        }


@dataclass(frozen=True)
class DataActionCapability:
    """One backend action and whether Phase 7 may execute it in-app."""

    action_id: str
    label: str
    available: bool
    mode: ActionMode
    status: str
    message: str
    required_parameters: tuple[str, ...] = ()
    optional_parameters: tuple[str, ...] = ()
    command_hint: str | None = None

    @property
    def safe_in_app(self) -> bool:
        return self.available and self.mode in {
            "read_only",
            "idempotent_local",
            "immutable_archive",
        }

    def as_dict(self) -> dict[str, object]:
        return {
            "action_id": self.action_id,
            "label": self.label,
            "available": self.available,
            "mode": self.mode,
            "status": self.status,
            "message": self.message,
            "required_parameters": list(self.required_parameters),
            "optional_parameters": list(self.optional_parameters),
            "command_hint": self.command_hint,
            "safe_in_app": self.safe_in_app,
        }


@dataclass(frozen=True)
class DataActionRequest:
    """Validated, immutable action request created outside the Streamlit UI."""

    action_id: str
    parameters: tuple[tuple[str, ParameterValue], ...]
    safe_in_app: bool

    def parameter_map(self) -> dict[str, ParameterValue]:
        return dict(self.parameters)


@dataclass(frozen=True)
class DataActionResult:
    """Result of one allowlisted Data Center action."""

    action_id: str
    succeeded: bool
    message: str
    quality: QualitySummary | None = None
    artifact_paths: tuple[str, ...] = ()
    records: int | None = None
    reused_offline: bool = False


@dataclass(frozen=True)
class DataCenterSnapshot:
    """Complete immutable read model for the Phase 7 Data Center page."""

    manifests: tuple[ManifestInventory, ...]
    sources: tuple[SourceInventory, ...]
    warehouse: WarehouseSummary
    quality: QualitySummary
    actions: tuple[DataActionCapability, ...]

    def action(self, action_id: str) -> DataActionCapability | None:
        return next((action for action in self.actions if action.action_id == action_id), None)

    def as_dict(self) -> dict[str, object]:
        return {
            "manifests": [manifest.as_dict() for manifest in self.manifests],
            "sources": [source.as_dict() for source in self.sources],
            "warehouse": self.warehouse.as_dict(),
            "quality": self.quality.as_dict(),
            "actions": [action.as_dict() for action in self.actions],
        }


def load_data_center(config: AppConfig) -> DataCenterSnapshot:
    """Build a truthful Data Center read model without changing raw archives."""

    manifests = _load_manifest_inventory(config)
    sources = _summarize_sources(manifests)
    warehouse_path = config.resolve(config.paths.warehouse)
    audit, audit_issue = _run_audit(config)
    warehouse = _warehouse_summary(warehouse_path, audit, audit_issue)
    quality = _quality_summary(audit, audit_issue)
    snapshot = DataCenterSnapshot(
        manifests=manifests,
        sources=sources,
        warehouse=warehouse,
        quality=quality,
        actions=(),
    )
    return DataCenterSnapshot(
        manifests=manifests,
        sources=sources,
        warehouse=warehouse,
        quality=quality,
        actions=data_action_capabilities(config, snapshot=snapshot),
    )


def data_action_capabilities(
    config: AppConfig,
    *,
    snapshot: DataCenterSnapshot | None = None,
) -> tuple[DataActionCapability, ...]:
    """Return static backend support plus local readiness for each data action."""

    manifests = snapshot.manifests if snapshot is not None else _load_manifest_inventory(config)
    sources = snapshot.sources if snapshot is not None else _summarize_sources(manifests)
    warehouse_exists = (
        snapshot.warehouse.exists
        if snapshot is not None
        else config.resolve(config.paths.warehouse).is_file()
    )
    has_nflverse = any(source.source == "nflverse" for source in sources)
    has_snap_counts = any(
        "snap_counts" in file.relative_path.casefold()
        for manifest in manifests
        for file in manifest.files
    )
    has_adp = any(
        source.source in {"ffc", "fantasyfootballcalculator", "espn", "espn_manual"}
        for source in sources
    )
    return (
        DataActionCapability(
            "audit",
            "Verify data integrity",
            True,
            "read_only",
            "ready",
            "Verify manifest hashes and canonical warehouse quality gates.",
            command_hint="fantasy-draft data audit",
        ),
        DataActionCapability(
            "initialize_warehouse",
            "Initialize warehouse",
            True,
            "idempotent_local",
            "ready" if not warehouse_exists else "already_initialized",
            "Create or migrate canonical DuckDB tables without deleting rows.",
            command_hint="fantasy-draft data init-warehouse",
        ),
        DataActionCapability(
            "download_nflverse",
            "Archive nflverse players and weekly stats",
            True,
            "immutable_archive",
            "ready",
            "Download documented nflverse data into never-overwritten raw files.",
            required_parameters=("start_season", "end_season"),
            optional_parameters=("offline",),
            command_hint=(
                "fantasy-draft data download-nflverse --start-season <year> --end-season <year>"
            ),
        ),
        DataActionCapability(
            "download_nflverse_snap_counts",
            "Archive nflverse snap counts",
            True,
            "immutable_archive",
            "ready",
            "Download documented nflverse/PFR snap counts into an immutable raw archive.",
            required_parameters=("start_season", "end_season"),
            optional_parameters=("offline",),
            command_hint=(
                "fantasy-draft data download-nflverse-snap-counts --start-season <year> "
                "--end-season <year>"
            ),
        ),
        DataActionCapability(
            "snapshot_ffc_adp",
            "Archive FFC ADP",
            True,
            "immutable_archive",
            "ready",
            "Capture the documented FFC endpoint into a never-overwritten JSON archive.",
            required_parameters=("season", "scoring_format", "teams"),
            optional_parameters=("position", "offline"),
            command_hint=(
                "fantasy-draft data snapshot-ffc-adp --season <year> --format ppr --teams 12"
            ),
        ),
        DataActionCapability(
            "load_archived_nflverse",
            "Load archived nflverse data",
            has_nflverse,
            "cli_only",
            "ready" if has_nflverse else "archive_required",
            "Validated loader exists; run it deliberately from the CLI.",
            command_hint="fantasy-draft data load-nflverse",
        ),
        DataActionCapability(
            "load_archived_snap_counts",
            "Load archived snap counts",
            has_snap_counts,
            "cli_only",
            "ready" if has_snap_counts else "archive_required",
            "Validated participation loader exists; run it deliberately from the CLI.",
            command_hint="fantasy-draft data load-nflverse-participation",
        ),
        DataActionCapability(
            "load_archived_adp",
            "Load archived ADP",
            has_adp,
            "cli_only",
            "ready" if has_adp else "archive_required",
            "Validated FFC/ESPN loader exists; run it deliberately from the CLI.",
            command_hint="fantasy-draft data load-adp",
        ),
        DataActionCapability(
            "import_espn_csv",
            "Import ESPN ADP CSV",
            True,
            "immutable_archive",
            "file_required",
            "A user-selected CSV is validated before it is copied to the immutable archive.",
            required_parameters=("path",),
            command_hint="fantasy-draft data import-espn-adp <path>",
        ),
        DataActionCapability(
            "sleeper_import",
            "Import Sleeper league",
            False,
            "unsupported",
            "not_implemented",
            "Sleeper authentication and league import are not implemented; no data is simulated.",
        ),
        DataActionCapability(
            "league_history_import",
            "Archive league-history package",
            True,
            "immutable_archive",
            "archive_only",
            "Hash and archive a user package without parsing it or making outcome claims.",
            required_parameters=("path",),
        ),
    )


def validate_data_action_request(
    config: AppConfig,
    action_id: str,
    parameters: Mapping[str, object] | None = None,
) -> DataActionRequest:
    """Validate an action identifier and JSON-scalar parameters before dispatch."""

    capability = next(
        (item for item in data_action_capabilities(config) if item.action_id == action_id),
        None,
    )
    if capability is None:
        raise ValueError(f"Unknown Data Center action: {action_id!r}.")
    if not capability.available:
        raise ValueError(f"Data Center action {action_id!r} is unavailable: {capability.message}")
    supplied = parameters or {}
    missing = sorted(set(capability.required_parameters) - set(supplied))
    if missing:
        raise ValueError(f"Data Center action {action_id!r} requires parameters: {missing}.")
    allowed = set(capability.required_parameters) | set(capability.optional_parameters)
    unexpected = sorted(set(supplied) - allowed)
    if unexpected:
        raise ValueError(
            f"Unexpected parameters for Data Center action {action_id!r}: {unexpected}."
        )
    normalized = _normalize_action_parameters(config, action_id, supplied)
    return DataActionRequest(
        action_id=action_id,
        parameters=normalized,
        safe_in_app=capability.safe_in_app,
    )


def run_safe_data_action(config: AppConfig, request: DataActionRequest) -> DataActionResult:
    """Execute one validated action from the explicit in-app allowlist."""

    validated = validate_data_action_request(config, request.action_id, request.parameter_map())
    if not validated.safe_in_app:
        raise ValueError(
            f"Data Center action {validated.action_id!r} is not allowlisted for in-app execution."
        )
    parameters = validated.parameter_map()
    try:
        if validated.action_id == "audit":
            audit, issue = _run_audit(config)
            quality = _quality_summary(audit, issue)
            return DataActionResult(
                action_id="audit",
                succeeded=quality.completed and quality.passed,
                message=(
                    "Data audit passed."
                    if quality.passed
                    else quality.failures[0]
                    if quality.failures
                    else "Data audit could not be completed."
                ),
                quality=quality,
            )
        if validated.action_id == "initialize_warehouse":
            path = config.resolve(config.paths.warehouse)
            Warehouse(path).initialize()
            return DataActionResult(
                action_id="initialize_warehouse",
                succeeded=True,
                message=f"Initialized canonical warehouse at {path}.",
                artifact_paths=(str(path),),
            )
        if validated.action_id == "download_nflverse":
            nflverse_result = download_nflverse(
                config,
                start_season=_request_int(parameters, "start_season"),
                end_season=_request_int(parameters, "end_season"),
                offline=_request_bool(parameters, "offline", False),
            )
            return DataActionResult(
                action_id=validated.action_id,
                succeeded=True,
                message="Archived nflverse players and weekly statistics.",
                artifact_paths=(
                    str(nflverse_result.player_path),
                    str(nflverse_result.stats_path),
                    str(nflverse_result.manifest_path),
                ),
                reused_offline=nflverse_result.reused_offline,
            )
        if validated.action_id == "download_nflverse_snap_counts":
            snap_result = download_nflverse_snap_counts(
                config,
                start_season=_request_int(parameters, "start_season"),
                end_season=_request_int(parameters, "end_season"),
                offline=_request_bool(parameters, "offline", False),
            )
            return DataActionResult(
                action_id=validated.action_id,
                succeeded=True,
                message="Archived nflverse/PFR snap counts.",
                artifact_paths=(
                    str(snap_result.snap_counts_path),
                    str(snap_result.manifest_path),
                ),
                reused_offline=snap_result.reused_offline,
            )
        if validated.action_id == "snapshot_ffc_adp":
            ffc_result = snapshot_ffc_adp(
                config,
                season=_request_int(parameters, "season"),
                scoring_format=_request_string(parameters, "scoring_format"),
                teams=_request_int(parameters, "teams"),
                position=_request_optional_string(parameters, "position"),
                offline=_request_bool(parameters, "offline", False),
            )
            return DataActionResult(
                action_id=validated.action_id,
                succeeded=True,
                message=f"Archived {len(ffc_result.normalized)} FFC ADP rows.",
                artifact_paths=(str(ffc_result.raw_path), str(ffc_result.manifest_path)),
                records=len(ffc_result.normalized),
                reused_offline=ffc_result.reused_offline,
            )
        if validated.action_id == "import_espn_csv":
            espn_result = import_espn_adp(
                config,
                Path(_request_string(parameters, "path")),
            )
            paths = tuple(
                str(path)
                for path in (espn_result.raw_path, espn_result.manifest_path)
                if path is not None
            )
            return DataActionResult(
                action_id=validated.action_id,
                succeeded=not espn_result.report.has_fatal_errors,
                message=espn_result.report.render(),
                artifact_paths=paths,
                records=espn_result.report.row_count,
            )
        if validated.action_id == "league_history_import":
            history_result = archive_league_history_package(
                config,
                Path(_request_string(parameters, "path")),
            )
            return DataActionResult(
                action_id=validated.action_id,
                succeeded=True,
                message=(
                    "Archived the league-history package without parsing or modeling it. "
                    "Phase 8 normalization remains unavailable."
                ),
                artifact_paths=(
                    str(history_result.raw_path),
                    str(history_result.manifest_path),
                ),
            )
    except (OSError, RuntimeError, TypeError, ValueError) as exc:
        return DataActionResult(
            action_id=validated.action_id,
            succeeded=False,
            message=str(exc),
        )
    raise RuntimeError(f"No safe action handler exists for {validated.action_id!r}.")


def _normalize_action_parameters(
    config: AppConfig,
    action_id: str,
    supplied: Mapping[str, object],
) -> tuple[tuple[str, ParameterValue], ...]:
    values: dict[str, ParameterValue] = {}
    for key, value in supplied.items():
        if key == "path" and isinstance(value, Path):
            values[key] = str(value.resolve())
        elif isinstance(value, (str, int, float, bool)) or value is None:
            values[key] = value
        else:
            raise TypeError(f"Data Center parameter {key!r} must be a JSON scalar.")
    for key, value in values.items():
        if isinstance(value, str) and not value.strip():
            raise ValueError(f"Data Center parameter {key!r} cannot be blank.")

    if action_id in {"download_nflverse", "download_nflverse_snap_counts"}:
        start = _request_int(values, "start_season")
        end = _request_int(values, "end_season")
        minimum = 2012 if action_id == "download_nflverse_snap_counts" else 1999
        if start < minimum or end > config.project.prediction_season or start > end:
            raise ValueError(
                f"Requested seasons must be ordered between {minimum} and "
                f"{config.project.prediction_season}."
            )
        _request_bool(values, "offline", False)
    elif action_id == "snapshot_ffc_adp":
        season = _request_int(values, "season")
        if season < 2007 or season > config.project.prediction_season:
            raise ValueError(
                f"FFC season must be between 2007 and {config.project.prediction_season}."
            )
        teams = _request_int(values, "teams")
        if not 4 <= teams <= 32:
            raise ValueError("FFC team count must be between 4 and 32.")
        scoring_format = _request_string(values, "scoring_format").casefold()
        if scoring_format not in SUPPORTED_FORMATS:
            raise ValueError(
                f"Unsupported FFC format {scoring_format!r}; choose {sorted(SUPPORTED_FORMATS)}."
            )
        values["scoring_format"] = scoring_format
        if "position" in values and values["position"] is not None:
            position = _request_string(values, "position").upper()
            values["position"] = position
        _request_bool(values, "offline", False)
    elif action_id in {"import_espn_csv", "league_history_import"}:
        source = Path(_request_string(values, "path")).expanduser().resolve()
        if action_id == "import_espn_csv" and source.suffix.casefold() != ".csv":
            raise ValueError("ESPN manual imports must be CSV files.")
        if (
            action_id == "league_history_import"
            and source.suffix.casefold() not in SUPPORTED_HISTORY_SUFFIXES
        ):
            raise ValueError("League-history packages must be CSV, JSON, or ZIP files.")
        if not source.is_file():
            raise FileNotFoundError(source)
        values["path"] = str(source)

    return tuple(sorted(values.items()))


def _request_int(parameters: Mapping[str, ParameterValue], name: str) -> int:
    value = parameters.get(name)
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise TypeError(f"Data Center parameter {name!r} must be an integer.")
    number = float(value)
    if not number.is_integer():
        raise ValueError(f"Data Center parameter {name!r} must be an integer.")
    return int(number)


def _request_bool(parameters: Mapping[str, ParameterValue], name: str, default: bool) -> bool:
    value = parameters.get(name, default)
    if not isinstance(value, bool):
        raise TypeError(f"Data Center parameter {name!r} must be true or false.")
    return value


def _request_string(parameters: Mapping[str, ParameterValue], name: str) -> str:
    value = parameters.get(name)
    if not isinstance(value, str) or not value.strip():
        raise TypeError(f"Data Center parameter {name!r} must be non-blank text.")
    return value.strip()


def _request_optional_string(parameters: Mapping[str, ParameterValue], name: str) -> str | None:
    return None if parameters.get(name) is None else _request_string(parameters, name)


def _load_manifest_inventory(config: AppConfig) -> tuple[ManifestInventory, ...]:
    root = config.project_root.resolve()
    manifest_root = config.resolve(config.paths.manifests)
    paths = sorted(manifest_root.glob("*.json")) if manifest_root.is_dir() else []
    inventories: list[ManifestInventory] = []
    for path in paths:
        relative_manifest = _display_path(root, path)
        try:
            payload = json.loads(path.read_text(encoding="utf-8"))
            manifest = SourceManifest.model_validate(payload)
        except (OSError, ValueError, json.JSONDecodeError) as exc:
            inventories.append(
                ManifestInventory(
                    dataset_id=path.stem,
                    source="invalid_manifest",
                    acquisition_method="unknown",
                    acquired_at=None,
                    seasons=(),
                    schema_version="unknown",
                    notes="",
                    manifest_path=relative_manifest,
                    files=(),
                    valid=False,
                    issues=(f"Invalid manifest: {exc}",),
                )
            )
            continue
        files: list[ManifestFileInventory] = []
        issues: list[str] = []
        if len(manifest.raw_files) != len(manifest.sha256):
            issues.append("Manifest has mismatched raw-file and SHA-256 counts.")
        for index, relative in enumerate(manifest.raw_files):
            expected = manifest.sha256[index] if index < len(manifest.sha256) else ""
            raw_path = _safe_project_path(root, relative)
            if raw_path is None:
                issues.append(f"Raw path escapes the project root: {relative}")
                files.append(ManifestFileInventory(relative, expected, None, False, False, None))
                continue
            exists = raw_path.is_file()
            try:
                actual = sha256_file(raw_path) if exists else None
                size_bytes = raw_path.stat().st_size if exists else None
            except OSError as exc:
                actual = None
                size_bytes = None
                issues.append(f"Raw file could not be read: {relative}: {exc}")
            verified = bool(exists and expected and actual == expected)
            if not exists:
                issues.append(f"Missing raw file: {relative}")
            elif not verified:
                issues.append(f"Hash mismatch: {relative}")
            files.append(
                ManifestFileInventory(
                    relative_path=relative,
                    expected_sha256=expected,
                    actual_sha256=actual,
                    exists=exists,
                    verified=verified,
                    size_bytes=size_bytes,
                )
            )
        inventories.append(
            ManifestInventory(
                dataset_id=manifest.dataset_id,
                source=manifest.source,
                acquisition_method=manifest.acquisition_method,
                acquired_at=manifest.acquired_at,
                seasons=tuple(sorted(set(manifest.seasons))),
                schema_version=manifest.schema_version,
                notes=manifest.notes,
                manifest_path=relative_manifest,
                files=tuple(files),
                valid=not issues,
                issues=tuple(issues),
            )
        )
    return tuple(inventories)


def _summarize_sources(
    manifests: tuple[ManifestInventory, ...],
) -> tuple[SourceInventory, ...]:
    grouped: dict[str, list[ManifestInventory]] = defaultdict(list)
    for manifest in manifests:
        grouped[manifest.source].append(manifest)
    summaries: list[SourceInventory] = []
    for source, records in sorted(grouped.items()):
        acquired = [record.acquired_at for record in records if record.acquired_at is not None]
        summaries.append(
            SourceInventory(
                source=source,
                manifest_count=len(records),
                valid_manifest_count=sum(record.valid for record in records),
                file_count=sum(len(record.files) for record in records),
                verified_file_count=sum(record.verified_files for record in records),
                seasons=tuple(sorted({season for record in records for season in record.seasons})),
                latest_acquired_at=max(acquired) if acquired else None,
            )
        )
    return tuple(summaries)


def _run_audit(config: AppConfig) -> tuple[AuditResult | None, str | None]:
    warehouse = Warehouse(config.resolve(config.paths.warehouse))
    if not warehouse.path.is_file():
        manifests = _load_manifest_inventory(config)
        failures = (
            "Canonical warehouse is not initialized.",
            *(
                f"{manifest.manifest_path}: {issue}"
                for manifest in manifests
                for issue in manifest.issues
            ),
        )
        return (
            AuditResult(
                manifest_count=len(manifests),
                verified_files=sum(manifest.verified_files for manifest in manifests),
                failures=failures,
                table_counts=warehouse.table_counts(),
            ),
            None,
        )
    try:
        return audit_project_data(config), None
    except (duckdb.Error, OSError, RuntimeError, ValueError) as exc:
        return None, f"Data audit could not be completed safely: {exc}"


def _warehouse_summary(
    path: Path,
    audit: AuditResult | None,
    issue: str | None,
) -> WarehouseSummary:
    exists = path.is_file()
    if audit is None:
        return WarehouseSummary(path=path, exists=exists, readable=False, tables=(), issue=issue)
    tables = tuple(
        WarehouseTableSummary(name, count, _table_domain(name))
        for name, count in sorted(audit.table_counts.items())
    )
    return WarehouseSummary(
        path=path,
        exists=exists,
        readable=exists,
        tables=tables,
        issue=None if exists else "Warehouse has not been initialized.",
    )


def _quality_summary(audit: AuditResult | None, issue: str | None) -> QualitySummary:
    if audit is None:
        return QualitySummary(
            completed=False,
            passed=False,
            manifest_count=0,
            verified_files=0,
            failures=(issue or "Data audit is unavailable.",),
        )
    return QualitySummary(
        completed=True,
        passed=audit.passed,
        manifest_count=audit.manifest_count,
        verified_files=audit.verified_files,
        failures=audit.failures,
    )


def _table_domain(name: str) -> str:
    if name.startswith("draft_"):
        return "draft"
    if name.startswith("adp_"):
        return "market"
    if name.startswith(("player_projection_", "baseline_", "feature_")):
        return "modeling"
    if name in {"league_rules", "team_outcomes"}:
        return "league"
    return "canonical"


def _safe_project_path(root: Path, relative: str) -> Path | None:
    candidate = (root / Path(relative)).resolve()
    return candidate if candidate.is_relative_to(root) else None


def _display_path(root: Path, path: Path) -> str:
    resolved = path.resolve()
    return resolved.relative_to(root).as_posix() if resolved.is_relative_to(root) else str(resolved)
