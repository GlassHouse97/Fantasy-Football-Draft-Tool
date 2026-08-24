"""Immutable current-platform ADP captures and fantasy-ID crosswalk snapshots.

Sleeper currently exposes PPR ADP inside a public projections response.  That
endpoint is intentionally labelled unsupported here because it is not included
in Sleeper's official public API documentation.  ESPN, Yahoo, and Underdog are
therefore accepted only as standardized CSV files obtained from an official or
otherwise authorized platform export; this module does not scrape those sites.
"""

from __future__ import annotations

import csv
import io
import json
import math
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Any, Final, Literal

import httpx
import pandas as pd

from fantasy_draft_ai.config import AppConfig
from fantasy_draft_ai.data.manifests import RawArchive, SourceManifest, utc_now

SLEEPER_PROJECTIONS_ROOT: Final = "https://api.sleeper.com/projections/nfl"
SLEEPER_POSITIONS: Final = ("QB", "RB", "WR", "TE")
MINIMUM_SLEEPER_ADP_ROWS: Final = 100
MANUAL_PLATFORM_ADP_COLUMNS: Final = (
    "captured_at",
    "season",
    "source",
    "scoring_format",
    "team_count",
    "source_player_id",
    "player_name",
    "position",
    "nfl_team",
    "average_pick",
    "rank",
)

ManualPlatformSource = Literal["espn", "yahoo", "underdog"]

_MANUAL_PROVENANCE: Final[dict[str, tuple[str, str]]] = {
    "espn": (
        "manual-official-espn-csv",
        "Official/authorized ESPN ADP CSV supplied manually; no ESPN scraping or "
        "authentication was performed by this application.",
    ),
    "yahoo": (
        "manual-official-yahoo-csv",
        "Official/authorized Yahoo ADP CSV supplied manually; no Yahoo scraping or "
        "authentication was performed by this application.",
    ),
    "underdog": (
        "manual-official-underdog-csv",
        "Official/authorized Underdog ADP CSV supplied manually; no Underdog scraping or "
        "authentication was performed by this application.",
    ),
}


@dataclass(frozen=True)
class SleeperAdpSnapshotResult:
    """One validated, immutable Sleeper PPR response capture."""

    raw_path: Path
    manifest: SourceManifest
    manifest_path: Path
    captured_at: datetime
    usable_count: int
    reused_offline: bool = False


@dataclass(frozen=True)
class ManualPlatformAdpImportResult:
    """One validated, byte-preserving official platform CSV import."""

    source: str
    raw_path: Path
    manifest: SourceManifest
    manifest_path: Path
    captured_at: datetime
    season: int
    scoring_format: str
    team_count: int
    usable_count: int


@dataclass(frozen=True)
class NflversePlayerIdsSnapshotResult:
    """One immutable nflverse fantasy-platform identifier crosswalk."""

    raw_path: Path
    manifest: SourceManifest
    manifest_path: Path
    captured_at: datetime
    row_count: int
    reused_offline: bool = False


def _archive(config: AppConfig) -> RawArchive:
    return RawArchive(
        project_root=config.project_root,
        raw_root=config.resolve(config.paths.raw_dir),
        manifest_root=config.resolve(config.paths.manifests),
    )


def snapshot_sleeper_adp(
    config: AppConfig,
    *,
    season: int = 2026,
    offline: bool = False,
) -> SleeperAdpSnapshotResult:
    """Archive Sleeper's current full-PPR ADP response without rewriting it.

    The projections route is public and unauthenticated at the time of writing,
    but it is not part of Sleeper's documented public API.  It is used only for
    this personal, noncommercial research project and may stop working without
    notice.  Offline mode never makes a network request.
    """

    if not 2000 <= season <= 2100:
        raise ValueError("Sleeper ADP season must be between 2000 and 2100.")
    stem = f"sleeper_adp__ppr__12_team__{season}"
    raw_directory = config.resolve(config.paths.raw_dir) / "sleeper_adp"
    archive = _archive(config)

    if offline:
        matches = sorted(raw_directory.glob(f"{stem}__*.json"))
        if not matches:
            raise FileNotFoundError(
                f"No cached Sleeper PPR ADP snapshot matches season {season}; "
                "run once without offline mode."
            )
        raw_path = matches[-1]
        usable_count = _validate_sleeper_payload(raw_path.read_bytes())
        existing = archive.find_manifest_for_files([raw_path])
        if existing is None:
            acquired_at = datetime.fromtimestamp(raw_path.stat().st_mtime, tz=UTC)
            manifest, manifest_path = archive.create_manifest(
                source="sleeper",
                acquisition_method="offline-cache",
                acquired_at=acquired_at,
                raw_files=[raw_path],
                seasons=[season],
                notes=(
                    "Reused an immutable Sleeper capture; no network request was made. "
                    "The originating projections endpoint is unsupported/undocumented."
                ),
            )
        else:
            manifest, manifest_path = existing
            acquired_at = _as_utc(manifest.acquired_at)
        return SleeperAdpSnapshotResult(
            raw_path=raw_path,
            manifest=manifest,
            manifest_path=manifest_path,
            captured_at=acquired_at,
            usable_count=usable_count,
            reused_offline=True,
        )

    params = httpx.QueryParams(
        [
            ("season_type", "regular"),
            *(("position[]", position) for position in SLEEPER_POSITIONS),
            ("order_by", "adp_ppr"),
        ]
    )
    headers = {"User-Agent": config.network.user_agent, "Accept": "application/json"}
    try:
        response = httpx.get(
            f"{SLEEPER_PROJECTIONS_ROOT}/{season}",
            params=params,
            headers=headers,
            timeout=config.network.timeout_seconds,
            follow_redirects=True,
        )
        response.raise_for_status()
    except httpx.HTTPError as exc:
        raise RuntimeError(
            "Sleeper ADP download failed through its unsupported public projections "
            f"endpoint: {exc}. Retry later or use offline mode to reuse a capture."
        ) from exc

    raw_bytes = response.content
    usable_count = _validate_sleeper_payload(raw_bytes)
    raw_path, acquired_at = archive.write_bytes("sleeper_adp", stem, ".json", raw_bytes)
    manifest, manifest_path = archive.create_manifest(
        source="sleeper",
        acquisition_method="unsupported-public-projections-endpoint",
        acquired_at=acquired_at,
        raw_files=[raw_path],
        seasons=[season],
        notes=(
            "Full-PPR adp_ppr values from Sleeper's public, unauthenticated projections "
            "endpoint. The endpoint is unsupported/undocumented by Sleeper and may change; "
            "captured for personal noncommercial research. Exact HTTP response-body bytes "
            f"were retained unchanged; usable_rows={usable_count}; assumed_team_count=12."
        ),
    )
    return SleeperAdpSnapshotResult(
        raw_path=raw_path,
        manifest=manifest,
        manifest_path=manifest_path,
        captured_at=acquired_at,
        usable_count=usable_count,
    )


def import_manual_platform_adp(
    config: AppConfig,
    source_path: Path,
    *,
    source: ManualPlatformSource | str,
) -> ManualPlatformAdpImportResult:
    """Validate and byte-for-byte archive an official platform ADP CSV."""

    normalized_source = source.strip().casefold()
    provenance = _MANUAL_PROVENANCE.get(normalized_source)
    if provenance is None:
        raise ValueError("Manual ADP source must be one of: espn, yahoo, underdog.")
    if not source_path.is_file():
        raise FileNotFoundError(source_path)

    content = source_path.read_bytes()
    scope, usable_count = _validate_manual_platform_csv(content, normalized_source)
    captured_at, season, scoring_format, team_count = scope
    archive = _archive(config)
    stem = f"{normalized_source}_adp__manual__{scoring_format}__{team_count}_team__{season}"
    raw_path, archived_at = archive.write_bytes(f"{normalized_source}_adp", stem, ".csv", content)
    acquisition_method, source_notes = provenance
    manifest, manifest_path = archive.create_manifest(
        source=normalized_source,
        acquisition_method=acquisition_method,
        acquired_at=archived_at,
        raw_files=[raw_path],
        seasons=[season],
        notes=(
            f"{source_notes} Source capture timestamp={captured_at.isoformat()}; "
            f"scoring_format={scoring_format}; team_count={team_count}; rows={usable_count}. "
            "CSV bytes were retained unchanged."
        ),
    )
    return ManualPlatformAdpImportResult(
        source=normalized_source,
        raw_path=raw_path,
        manifest=manifest,
        manifest_path=manifest_path,
        captured_at=captured_at,
        season=season,
        scoring_format=scoring_format,
        team_count=team_count,
        usable_count=usable_count,
    )


def snapshot_nflverse_ff_playerids(
    config: AppConfig,
    *,
    offline: bool = False,
) -> NflversePlayerIdsSnapshotResult:
    """Archive nflverse's exact fantasy-platform-to-GSIS identifier crosswalk."""

    archive = _archive(config)
    raw_directory = config.resolve(config.paths.raw_dir) / "nflverse"
    pattern = "nflverse_ff_playerids__*.parquet"

    if offline:
        matches = sorted(raw_directory.glob(pattern))
        if not matches:
            raise FileNotFoundError(
                "No cached nflverse fantasy-ID crosswalk exists; run once without offline mode."
            )
        raw_path = matches[-1]
        frame = pd.read_parquet(raw_path)
        row_count = _validate_ff_playerids_frame(frame)
        existing = archive.find_manifest_for_files([raw_path])
        if existing is None:
            acquired_at = datetime.fromtimestamp(raw_path.stat().st_mtime, tz=UTC)
            manifest, manifest_path = archive.create_manifest(
                source="nflverse_ff_playerids",
                acquisition_method="offline-cache",
                acquired_at=acquired_at,
                raw_files=[raw_path],
                notes=(
                    "Reused an immutable nflverse fantasy-ID crosswalk; no network "
                    "request was made."
                ),
            )
        else:
            manifest, manifest_path = existing
            acquired_at = _as_utc(manifest.acquired_at)
        return NflversePlayerIdsSnapshotResult(
            raw_path=raw_path,
            manifest=manifest,
            manifest_path=manifest_path,
            captured_at=acquired_at,
            row_count=row_count,
            reused_offline=True,
        )

    try:
        import nflreadpy as nfl  # type: ignore[import-untyped]
    except ImportError as exc:  # pragma: no cover - required project dependency
        raise RuntimeError("nflreadpy is not installed; run pip install -e .") from exc
    try:
        frame = nfl.load_ff_playerids()
    except Exception as exc:  # nflreadpy surfaces upstream-specific failures
        raise RuntimeError(
            f"nflverse fantasy-ID crosswalk download failed: {exc}. Retry later or "
            "use offline mode."
        ) from exc

    row_count = _validate_ff_playerids_frame(frame)
    acquired_at = utc_now()
    raw_path, _ = archive.new_path("nflverse", "nflverse_ff_playerids", ".parquet", acquired_at)
    if isinstance(frame, pd.DataFrame):
        frame.to_parquet(raw_path, index=False)
    else:
        frame.write_parquet(raw_path)
    manifest, manifest_path = archive.create_manifest(
        source="nflverse_ff_playerids",
        acquisition_method="nflreadpy.load_ff_playerids",
        acquired_at=acquired_at,
        raw_files=[raw_path],
        notes=(
            "Fantasy-platform identifier crosswalk returned by "
            "nflreadpy.load_ff_playerids(); exact returned frame retained as Parquet."
        ),
    )
    return NflversePlayerIdsSnapshotResult(
        raw_path=raw_path,
        manifest=manifest,
        manifest_path=manifest_path,
        captured_at=acquired_at,
        row_count=row_count,
    )


def _validate_sleeper_payload(content: bytes) -> int:
    try:
        payload: Any = json.loads(content)
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise ValueError(f"Sleeper response was not valid JSON: {exc}") from exc
    if not isinstance(payload, list):
        raise ValueError("Sleeper response must be a JSON list.")

    source_ids: set[str] = set()
    usable_count = 0
    for value in payload:
        if not isinstance(value, dict):
            continue
        player = value.get("player")
        stats = value.get("stats")
        if not isinstance(player, dict) or not isinstance(stats, dict):
            continue
        source_player_id = _required_optional_text(value.get("player_id"))
        position = _required_optional_text(player.get("position"))
        adp = _finite_float(stats.get("adp_ppr"))
        if (
            source_player_id is None
            or position is None
            or position.upper() not in SLEEPER_POSITIONS
            or adp is None
            or not 1.0 <= adp < 900.0
        ):
            continue
        if source_player_id in source_ids:
            raise ValueError(
                f"Sleeper response contains duplicate stable player_id {source_player_id!r}."
            )
        source_ids.add(source_player_id)
        usable_count += 1

    if usable_count < MINIMUM_SLEEPER_ADP_ROWS:
        raise ValueError(
            "Sleeper response produced only "
            f"{usable_count} usable QB/RB/WR/TE rows; expected at least "
            f"{MINIMUM_SLEEPER_ADP_ROWS}."
        )
    return usable_count


def _validate_manual_platform_csv(
    content: bytes,
    expected_source: str,
) -> tuple[tuple[datetime, int, str, int], int]:
    try:
        text = content.decode("utf-8-sig")
    except UnicodeDecodeError as exc:
        raise ValueError("Platform ADP CSV must be UTF-8 encoded.") from exc
    try:
        reader = csv.DictReader(io.StringIO(text, newline=""))
        columns = set(reader.fieldnames or ())
        missing = sorted(set(MANUAL_PLATFORM_ADP_COLUMNS) - columns)
        if missing:
            raise ValueError(f"Platform ADP CSV is missing columns: {', '.join(missing)}.")
        rows = list(reader)
    except csv.Error as exc:
        raise ValueError(f"Could not parse platform ADP CSV: {exc}") from exc
    if not rows:
        raise ValueError("Platform ADP CSV must contain at least one data row.")

    scopes: set[tuple[datetime, int, str, int]] = set()
    source_ids: set[str] = set()
    for row_number, row in enumerate(rows, start=2):
        captured_at = _parse_timestamp(row.get("captured_at"), row_number=row_number)
        season = _required_integer(row.get("season"), "season", row_number)
        source = _required_text(row.get("source"), "source", row_number).casefold()
        scoring_format = _required_text(
            row.get("scoring_format"), "scoring_format", row_number
        ).casefold()
        team_count = _required_integer(row.get("team_count"), "team_count", row_number)
        source_player_id = _required_text(
            row.get("source_player_id"), "source_player_id", row_number
        )
        _required_text(row.get("player_name"), "player_name", row_number)
        position = _required_text(row.get("position"), "position", row_number).upper()
        average_pick = _required_number(row.get("average_pick"), "average_pick", row_number)
        rank = _required_integer(row.get("rank"), "rank", row_number)

        if source != expected_source:
            raise ValueError(
                f"CSV row {row_number} source {source!r} does not match "
                f"requested source {expected_source!r}."
            )
        if not 2000 <= season <= 2100:
            raise ValueError(f"CSV row {row_number} season is outside 2000-2100.")
        if not 4 <= team_count <= 32:
            raise ValueError(f"CSV row {row_number} team_count must be between 4 and 32.")
        if position not in {"QB", "RB", "WR", "TE", "K", "DST", "DEF"}:
            raise ValueError(f"CSV row {row_number} has unsupported position {position!r}.")
        if not 1.0 <= average_pick < 900.0:
            raise ValueError(f"CSV row {row_number} average_pick must be at least 1 and below 900.")
        if rank < 1:
            raise ValueError(f"CSV row {row_number} rank must be positive.")
        if source_player_id in source_ids:
            raise ValueError(f"CSV contains duplicate source_player_id {source_player_id!r}.")
        source_ids.add(source_player_id)
        scopes.add((captured_at, season, scoring_format, team_count))

    if len(scopes) != 1:
        raise ValueError(
            "Platform ADP CSV must describe one captured_at/season/scoring_format/"
            "team_count snapshot."
        )
    return next(iter(scopes)), len(rows)


def _validate_ff_playerids_frame(frame: Any) -> int:
    required = {"gsis_id", "espn_id", "sleeper_id", "yahoo_id"}
    columns = {str(column) for column in frame.columns}
    missing = sorted(required - columns)
    if missing:
        raise ValueError(
            "nflverse fantasy-ID crosswalk is missing columns: " + ", ".join(missing) + "."
        )
    row_count = len(frame.index) if isinstance(frame, pd.DataFrame) else int(frame.height)
    if row_count < 100:
        raise ValueError(
            f"nflverse fantasy-ID crosswalk contains only {row_count} rows; expected at least 100."
        )
    return row_count


def _parse_timestamp(value: object, *, row_number: int) -> datetime:
    text = _required_text(value, "captured_at", row_number)
    try:
        parsed = datetime.fromisoformat(text.replace("Z", "+00:00"))
    except ValueError as exc:
        raise ValueError(f"CSV row {row_number} has an invalid captured_at timestamp.") from exc
    if parsed.tzinfo is None:
        raise ValueError(f"CSV row {row_number} captured_at must include a timezone.")
    return parsed.astimezone(UTC)


def _required_text(value: object, field: str, row_number: int) -> str:
    text = _required_optional_text(value)
    if text is None:
        raise ValueError(f"CSV row {row_number} has a blank {field} value.")
    return text


def _required_optional_text(value: object) -> str | None:
    if value is None:
        return None
    text = str(value).strip()
    return text or None


def _finite_float(value: object) -> float | None:
    if value is None or isinstance(value, bool):
        return None
    try:
        result = float(str(value))
    except (TypeError, ValueError):
        return None
    return result if math.isfinite(result) else None


def _required_number(value: object, field: str, row_number: int) -> float:
    result = _finite_float(value)
    if result is None:
        raise ValueError(f"CSV row {row_number} has an invalid {field} value.")
    return result


def _required_integer(value: object, field: str, row_number: int) -> int:
    result = _required_number(value, field, row_number)
    if not result.is_integer():
        raise ValueError(f"CSV row {row_number} {field} must be an integer.")
    return int(result)


def _as_utc(value: datetime) -> datetime:
    if value.tzinfo is None:
        return value.replace(tzinfo=UTC)
    return value.astimezone(UTC)
