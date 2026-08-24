"""Archive and normalize one FantasyPros multi-source ADP CSV export.

FantasyPros exports one licensed spreadsheet containing provider columns plus its
own composite average.  This importer retains those exact uploaded bytes once,
derives four provenance-linked canonical CSV snapshots, and submits all four to
the ADP warehouse in one transaction.  The deliberately neutral ``overall``
scoring scope keeps this market-consensus data out of scoring-specific draft
model inputs.
"""

from __future__ import annotations

import csv
import hashlib
import io
import json
import math
import re
from collections import Counter
from dataclasses import dataclass, field
from datetime import UTC, datetime
from pathlib import Path
from typing import Final

from fantasy_draft_ai.config import AppConfig
from fantasy_draft_ai.data.adp_loader import AdpLoadResult, load_adp_to_warehouse
from fantasy_draft_ai.data.manifests import RawArchive, SourceManifest, sha256_file, utc_now

FANTASYPROS_REQUIRED_HEADERS: Final = (
    "Rank",
    "Player (Bye)",
    "POS",
    "Yahoo",
    "Sleeper",
    "RTSports",
    "AVG",
)
FANTASYPROS_SOURCES: Final = ("yahoo", "sleeper", "rtsports", "fantasypros")
_SOURCE_COLUMNS: Final = {
    "yahoo": "Yahoo",
    "sleeper": "Sleeper",
    "rtsports": "RTSports",
    "fantasypros": "AVG",
}
_NORMALIZED_COLUMNS: Final = (
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
_SUPPORTED_POSITIONS: Final = frozenset({"QB", "RB", "WR", "TE", "K", "DST"})
_NFL_TEAMS: Final = frozenset(
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
        "JAC",
        "KC",
        "LAC",
        "LAR",
        "LV",
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
_POSITION_RE: Final = re.compile(r"^(QB|RB|WR|TE|K|DST)\d+$", flags=re.IGNORECASE)
_PLAYER_BYE_RE: Final = re.compile(
    r"^(?P<name>.+?)\s{2,}(?:(?P<team>[A-Z]{2,3})\s+)?\((?P<bye>\d{1,2})\)$"
)
_ORIGINAL_SOURCE: Final = "fantasypros_aggregate_upload"
_ORIGINAL_ACQUISITION: Final = "user-uploaded-fantasypros-aggregate-csv-v1"
_NORMALIZED_ACQUISITION: Final = "normalized-fantasypros-aggregate-source-v1"
_ORIGINAL_SCHEMA: Final = "fantasypros_aggregate_upload_v1"
_NORMALIZED_SCHEMA: Final = "fantasypros_aggregate_normalized_v1"
_MAX_UPLOAD_BYTES: Final = 10 * 1024 * 1024
_MAX_DATA_ROWS: Final = 10_000


class FantasyProsUploadValidationError(ValueError):
    """A fail-closed FantasyPros upload error safe for the UI to display."""


@dataclass(frozen=True)
class FantasyProsAggregateRow:
    """One conservatively parsed FantasyPros aggregate record."""

    source_row_number: int
    overall_rank: int
    player_name: str
    normalized_name: str
    position: str
    nfl_team: str | None
    bye_week: int | None
    source_adps: tuple[tuple[str, float], ...]

    def adp_for(self, source: str) -> float | None:
        """Return this row's ADP for one supported source."""

        return dict(self.source_adps).get(source)


@dataclass(frozen=True)
class FantasyProsAggregatePreview:
    """Validated write-free preview of one multi-source export."""

    file_name: str
    raw_sha256: str
    captured_at: datetime
    season: int
    team_count: int
    input_rows: int
    rows: tuple[FantasyProsAggregateRow, ...]
    source_row_counts: tuple[tuple[str, int], ...]
    upload_fingerprint: str
    raw_bytes: bytes = field(repr=False)


@dataclass(frozen=True)
class FantasyProsNormalizedArtifact:
    """One standardized provider/composite snapshot linked to the original upload."""

    source: str
    raw_path: Path
    manifest: SourceManifest
    manifest_path: Path


@dataclass(frozen=True)
class FantasyProsSourceImportSummary:
    """Committed identity mapping counts for one derived source."""

    source: str
    rows: int
    mapped: int
    unresolved: int
    snapshot_id: str


@dataclass(frozen=True)
class FantasyProsAggregateImportResult:
    """Immutable archive provenance plus the transactional warehouse result."""

    preview: FantasyProsAggregatePreview
    original_raw_path: Path
    original_manifest: SourceManifest
    original_manifest_path: Path
    normalized_artifacts: tuple[FantasyProsNormalizedArtifact, ...]
    load: AdpLoadResult
    source_summaries: tuple[FantasyProsSourceImportSummary, ...]
    reused_archive: bool

    @property
    def committed(self) -> bool:
        """Return whether all derived snapshots committed to DuckDB."""

        return self.load.committed


def preview_fantasypros_adp_upload(
    config: AppConfig,
    content: bytes,
    *,
    file_name: str,
    captured_at: datetime | None = None,
    season: int | None = None,
    team_count: int = 12,
) -> FantasyProsAggregatePreview:
    """Validate and parse a FantasyPros aggregate CSV without writing files."""

    effective_season = season or config.project.prediction_season
    if not 2000 <= effective_season <= 2100:
        raise FantasyProsUploadValidationError("Season must be between 2000 and 2100.")
    if not 4 <= team_count <= 32:
        raise FantasyProsUploadValidationError("Team count must be between 4 and 32.")
    effective_captured_at = _as_utc(captured_at or utc_now())
    raw_rows = _read_fantasypros_csv(content)

    parsed: list[FantasyProsAggregateRow] = []
    seen_ranks: set[int] = set()
    seen_players: dict[tuple[str, str], int] = {}
    for row_number, raw in enumerate(raw_rows, start=2):
        row = _parse_row(raw, row_number=row_number)
        if row.overall_rank in seen_ranks:
            raise FantasyProsUploadValidationError(
                f"CSV row {row_number} repeats overall Rank {row.overall_rank}."
            )
        seen_ranks.add(row.overall_rank)
        identity_key = (row.normalized_name, row.position)
        prior_row = seen_players.get(identity_key)
        if prior_row is not None:
            raise FantasyProsUploadValidationError(
                f"CSV rows {prior_row} and {row_number} normalize to the same player and "
                "position. Resolve the duplicate before uploading."
            )
        seen_players[identity_key] = row_number
        parsed.append(row)
    if not parsed:
        raise FantasyProsUploadValidationError(
            "The FantasyPros CSV has no nonblank player rows."
        )

    rows = tuple(sorted(parsed, key=lambda item: item.overall_rank))
    source_counts = tuple(
        (source, sum(row.adp_for(source) is not None for row in rows))
        for source in FANTASYPROS_SOURCES
    )
    if dict(source_counts)["fantasypros"] != len(rows):
        raise FantasyProsUploadValidationError(
            "Every FantasyPros row must contain a composite AVG value."
        )
    raw_sha256 = hashlib.sha256(content).hexdigest()
    fingerprint_payload = {
        "captured_at": effective_captured_at.isoformat(),
        "raw_sha256": raw_sha256,
        "schema": _ORIGINAL_SCHEMA,
        "season": effective_season,
        "team_count": team_count,
    }
    upload_fingerprint = hashlib.sha256(
        _canonical_json(fingerprint_payload).encode("utf-8")
    ).hexdigest()
    return FantasyProsAggregatePreview(
        file_name=Path(file_name).name or "fantasypros-adp.csv",
        raw_sha256=raw_sha256,
        captured_at=effective_captured_at,
        season=effective_season,
        team_count=team_count,
        input_rows=len(rows),
        rows=rows,
        source_row_counts=source_counts,
        upload_fingerprint=upload_fingerprint,
        raw_bytes=content,
    )


def commit_fantasypros_adp_upload(
    config: AppConfig,
    preview: FantasyProsAggregatePreview,
) -> FantasyProsAggregateImportResult:
    """Archive and load all four derived snapshots in one warehouse transaction."""

    actual_hash = hashlib.sha256(preview.raw_bytes).hexdigest()
    if actual_hash != preview.raw_sha256:
        raise FantasyProsUploadValidationError(
            "The uploaded bytes changed after preview; upload the file again."
        )
    verified = preview_fantasypros_adp_upload(
        config,
        preview.raw_bytes,
        file_name=preview.file_name,
        captured_at=preview.captured_at,
        season=preview.season,
        team_count=preview.team_count,
    )
    if verified.upload_fingerprint != preview.upload_fingerprint or verified.rows != preview.rows:
        raise FantasyProsUploadValidationError(
            "The FantasyPros preview is stale or its normalized rows changed."
        )

    existing = _find_existing_bundle(config, preview.raw_sha256)
    if existing is None:
        archive_bundle = _archive_bundle(config, preview)
        reused_archive = False
    else:
        archive_bundle = existing
        reused_archive = True
    original_raw_path, original_manifest, original_manifest_path, artifacts = archive_bundle

    load = load_adp_to_warehouse(
        config,
        manifest_paths=[artifact.manifest_path for artifact in artifacts],
    )
    source_summaries = tuple(
        FantasyProsSourceImportSummary(
            source=summary.source,
            rows=summary.source_rows,
            mapped=summary.source_rows - summary.unresolved_players,
            unresolved=summary.unresolved_players,
            snapshot_id=summary.snapshot_id,
        )
        for summary in sorted(
            load.snapshots,
            key=lambda item: FANTASYPROS_SOURCES.index(item.source),
        )
    )
    return FantasyProsAggregateImportResult(
        preview=preview,
        original_raw_path=original_raw_path,
        original_manifest=original_manifest,
        original_manifest_path=original_manifest_path,
        normalized_artifacts=artifacts,
        load=load,
        source_summaries=source_summaries,
        reused_archive=reused_archive,
    )


def import_fantasypros_adp_upload(
    config: AppConfig,
    content: bytes,
    *,
    file_name: str,
    captured_at: datetime | None = None,
    season: int | None = None,
    team_count: int = 12,
) -> FantasyProsAggregateImportResult:
    """Preview and immediately commit a trusted FantasyPros aggregate export."""

    preview = preview_fantasypros_adp_upload(
        config,
        content,
        file_name=file_name,
        captured_at=captured_at,
        season=season,
        team_count=team_count,
    )
    return commit_fantasypros_adp_upload(config, preview)


def _read_fantasypros_csv(content: bytes) -> list[dict[str, str | None]]:
    if not content:
        raise FantasyProsUploadValidationError("The uploaded CSV is empty.")
    if len(content) > _MAX_UPLOAD_BYTES:
        raise FantasyProsUploadValidationError("The uploaded CSV exceeds 10 MB.")
    try:
        text = content.decode("utf-8-sig")
    except UnicodeDecodeError as exc:
        raise FantasyProsUploadValidationError(
            "The FantasyPros CSV must be UTF-8 encoded."
        ) from exc
    try:
        reader = csv.DictReader(io.StringIO(text, newline=""))
        headers = tuple(reader.fieldnames or ())
        duplicates = sorted(header for header, count in Counter(headers).items() if count > 1)
        if duplicates:
            raise FantasyProsUploadValidationError(
                "The CSV contains duplicate headers: " + ", ".join(duplicates) + "."
            )
        missing = [header for header in FANTASYPROS_REQUIRED_HEADERS if header not in headers]
        if missing:
            raise FantasyProsUploadValidationError(
                "This is not the expected FantasyPros Overall ADP export. Missing headers: "
                + ", ".join(missing)
                + "."
            )
        rows: list[dict[str, str | None]] = []
        for data_row_number, row in enumerate(reader, start=1):
            if data_row_number > _MAX_DATA_ROWS:
                raise FantasyProsUploadValidationError(
                    "The uploaded CSV exceeds the 10,000-row safety limit."
                )
            if None in row:
                raise FantasyProsUploadValidationError(
                    f"CSV row {data_row_number + 1} contains more values than headers."
                )
            if any(_optional_text(value) for value in row.values()):
                rows.append(row)
    except csv.Error as exc:
        raise FantasyProsUploadValidationError(
            f"The uploaded file is not valid CSV: {exc}"
        ) from exc
    return rows


def _parse_row(raw: dict[str, str | None], *, row_number: int) -> FantasyProsAggregateRow:
    overall_rank = _parse_positive_integer(raw.get("Rank"), "Rank", row_number)
    player_name, nfl_team, bye_week = _parse_player_bye(raw.get("Player (Bye)"), row_number)
    position_text = _required_text(raw.get("POS"), "POS", row_number).upper()
    position_match = _POSITION_RE.fullmatch(position_text)
    if position_match is None:
        raise FantasyProsUploadValidationError(
            f"CSV row {row_number} has invalid FantasyPros POS {position_text!r}."
        )
    position = position_match.group(1).upper()
    if position not in _SUPPORTED_POSITIONS:
        raise FantasyProsUploadValidationError(
            f"CSV row {row_number} has unsupported position {position!r}."
        )

    source_adps: list[tuple[str, float]] = []
    for source in FANTASYPROS_SOURCES:
        column = _SOURCE_COLUMNS[source]
        raw_value = _optional_text(raw.get(column))
        if raw_value is None:
            if source == "fantasypros":
                raise FantasyProsUploadValidationError(
                    f"CSV row {row_number} has a blank AVG value."
                )
            continue
        source_adps.append((source, _parse_adp(raw_value, column, row_number)))
    normalized_name = _normalize_name(player_name)
    if not normalized_name:
        raise FantasyProsUploadValidationError(
            f"CSV row {row_number} has an invalid player name."
        )
    return FantasyProsAggregateRow(
        source_row_number=row_number,
        overall_rank=overall_rank,
        player_name=player_name,
        normalized_name=normalized_name,
        position=position,
        nfl_team=nfl_team,
        bye_week=bye_week,
        source_adps=tuple(source_adps),
    )


def _parse_player_bye(value: object, row_number: int) -> tuple[str, str | None, int | None]:
    text = _required_text(value, "Player (Bye)", row_number)
    compact = " ".join(text.split())
    if "(" not in text and ")" not in text:
        return compact, None, None
    match = _PLAYER_BYE_RE.fullmatch(text.strip())
    if match is None:
        raise FantasyProsUploadValidationError(
            f"CSV row {row_number} has an unrecognized Player (Bye) value {text!r}."
        )
    player_name = " ".join(match.group("name").split())
    team = match.group("team")
    if team is not None and team not in _NFL_TEAMS:
        raise FantasyProsUploadValidationError(
            f"CSV row {row_number} has unknown NFL team abbreviation {team!r}."
        )
    bye_week = int(match.group("bye"))
    if not 1 <= bye_week <= 18:
        raise FantasyProsUploadValidationError(
            f"CSV row {row_number} has invalid bye week {bye_week}."
        )
    return player_name, team, bye_week


def _archive_bundle(
    config: AppConfig,
    preview: FantasyProsAggregatePreview,
) -> tuple[
    Path,
    SourceManifest,
    Path,
    tuple[FantasyProsNormalizedArtifact, ...],
]:
    archive = RawArchive(
        project_root=config.project_root,
        raw_root=config.resolve(config.paths.raw_dir),
        manifest_root=config.resolve(config.paths.manifests),
    )
    file_stem = re.sub(r"[^A-Za-z0-9_-]+", "_", Path(preview.file_name).stem).strip("_")
    original_path, archived_at = archive.write_bytes(
        "fantasypros_aggregate",
        f"fantasypros_aggregate__{file_stem or 'upload'}",
        ".csv",
        preview.raw_bytes,
    )
    original_notes = _canonical_json(
        {
            "captured_at": preview.captured_at.isoformat(),
            "file_name": preview.file_name,
            "headers": list(FANTASYPROS_REQUIRED_HEADERS),
            "raw_sha256": preview.raw_sha256,
            "schema": _ORIGINAL_SCHEMA,
            "season": preview.season,
            "source_row_counts": dict(preview.source_row_counts),
            "team_count": preview.team_count,
            "upload_fingerprint": preview.upload_fingerprint,
        }
    )
    original_manifest, original_manifest_path = archive.create_manifest(
        source=_ORIGINAL_SOURCE,
        acquisition_method=_ORIGINAL_ACQUISITION,
        acquired_at=archived_at,
        raw_files=[original_path],
        seasons=[preview.season],
        notes=original_notes,
    )

    artifacts: list[FantasyProsNormalizedArtifact] = []
    for source in FANTASYPROS_SOURCES:
        normalized_path, normalized_at = archive.write_bytes(
            f"{source}_adp",
            f"{source}_adp__fantasypros_aggregate__overall__{preview.team_count}_team__"
            f"{preview.season}",
            ".csv",
            _normalized_csv_bytes(preview, source),
            acquired_at=archived_at,
        )
        normalized_notes = _canonical_json(
            {
                "original_dataset_id": original_manifest.dataset_id,
                "original_raw_sha256": preview.raw_sha256,
                "schema": _NORMALIZED_SCHEMA,
                "scope": {
                    "captured_at": preview.captured_at.isoformat(),
                    "position_scope": "overall",
                    "scoring_format": "overall",
                    "season": preview.season,
                    "source": source,
                    "team_count": preview.team_count,
                },
                "source_column": _SOURCE_COLUMNS[source],
                "source_rows": dict(preview.source_row_counts)[source],
            }
        )
        manifest, manifest_path = archive.create_manifest(
            source=source,
            acquisition_method=_NORMALIZED_ACQUISITION,
            acquired_at=normalized_at,
            raw_files=[normalized_path],
            seasons=[preview.season],
            notes=normalized_notes,
        )
        artifacts.append(
            FantasyProsNormalizedArtifact(
                source=source,
                raw_path=normalized_path,
                manifest=manifest,
                manifest_path=manifest_path,
            )
        )
    return original_path, original_manifest, original_manifest_path, tuple(artifacts)


def _find_existing_bundle(
    config: AppConfig,
    raw_sha256: str,
) -> tuple[
    Path,
    SourceManifest,
    Path,
    tuple[FantasyProsNormalizedArtifact, ...],
] | None:
    manifest_root = config.resolve(config.paths.manifests)
    if not manifest_root.exists():
        return None
    catalog: list[tuple[SourceManifest, Path, dict[str, object]]] = []
    for path in sorted(manifest_root.glob("*.json")):
        try:
            manifest = SourceManifest.model_validate_json(path.read_text(encoding="utf-8"))
        except (OSError, ValueError):
            continue
        catalog.append((manifest, path, _json_notes(manifest.notes)))
    originals = [
        (manifest, path)
        for manifest, path, notes in catalog
        if manifest.source.casefold() == _ORIGINAL_SOURCE
        and manifest.acquisition_method == _ORIGINAL_ACQUISITION
        and notes.get("raw_sha256") == raw_sha256
    ]
    if not originals:
        return None
    if len(originals) != 1:
        raise FantasyProsUploadValidationError(
            "Multiple original manifests claim the same FantasyPros upload bytes."
        )
    original_manifest, original_manifest_path = originals[0]
    original_path = _verified_single_raw_path(config, original_manifest)
    if original_manifest.sha256 != [raw_sha256]:
        raise FantasyProsUploadValidationError(
            "The existing FantasyPros original manifest does not match its recorded hash."
        )

    artifacts: list[FantasyProsNormalizedArtifact] = []
    for source in FANTASYPROS_SOURCES:
        matches = [
            (manifest, path)
            for manifest, path, notes in catalog
            if manifest.source.casefold() == source
            and manifest.acquisition_method == _NORMALIZED_ACQUISITION
            and notes.get("original_dataset_id") == original_manifest.dataset_id
            and notes.get("original_raw_sha256") == raw_sha256
        ]
        if len(matches) != 1:
            raise FantasyProsUploadValidationError(
                "An existing FantasyPros upload has missing or duplicate normalized "
                f"{source} provenance."
            )
        manifest, manifest_path = matches[0]
        artifacts.append(
            FantasyProsNormalizedArtifact(
                source=source,
                raw_path=_verified_single_raw_path(config, manifest),
                manifest=manifest,
                manifest_path=manifest_path,
            )
        )
    return original_path, original_manifest, original_manifest_path, tuple(artifacts)


def _verified_single_raw_path(config: AppConfig, manifest: SourceManifest) -> Path:
    if len(manifest.raw_files) != 1 or len(manifest.sha256) != 1:
        raise FantasyProsUploadValidationError(
            f"Manifest {manifest.dataset_id} must identify exactly one archived file."
        )
    project_root = config.project_root.resolve()
    path = (project_root / manifest.raw_files[0]).resolve()
    if not path.is_relative_to(project_root) or not path.is_file():
        raise FantasyProsUploadValidationError(
            f"Archived FantasyPros file is missing or outside the project: "
            f"{manifest.raw_files[0]}"
        )
    if sha256_file(path) != manifest.sha256[0]:
        raise FantasyProsUploadValidationError(
            f"Archived FantasyPros hash verification failed: {manifest.raw_files[0]}"
        )
    return path


def _normalized_csv_bytes(preview: FantasyProsAggregatePreview, source: str) -> bytes:
    ranked_rows = sorted(
        (row for row in preview.rows if row.adp_for(source) is not None),
        key=lambda row: (row.adp_for(source) or math.inf, row.overall_rank),
    )
    output = io.StringIO(newline="")
    writer = csv.DictWriter(output, fieldnames=_NORMALIZED_COLUMNS, lineterminator="\n")
    writer.writeheader()
    captured_at = preview.captured_at.isoformat().replace("+00:00", "Z")
    for source_rank, row in enumerate(ranked_rows, start=1):
        writer.writerow(
            {
                "captured_at": captured_at,
                "season": preview.season,
                "source": source,
                "scoring_format": "overall",
                "team_count": preview.team_count,
                "source_player_id": _generated_source_id(source, row),
                "player_name": row.player_name,
                "position": row.position,
                "nfl_team": row.nfl_team or "",
                "average_pick": format(row.adp_for(source) or 0.0, ".12g"),
                "rank": source_rank,
            }
        )
    return output.getvalue().encode("utf-8")


def _generated_source_id(source: str, row: FantasyProsAggregateRow) -> str:
    payload = f"{source}|{row.normalized_name}|{row.position}|{row.nfl_team or ''}"
    digest = hashlib.sha256(payload.encode("utf-8")).hexdigest()[:24]
    return f"fantasypros-aggregate:{source}:{digest}"


def _parse_adp(value: object, column: str, row_number: int) -> float:
    text = _required_text(value, column, row_number)
    try:
        number = float(text)
    except ValueError as exc:
        raise FantasyProsUploadValidationError(
            f"CSV row {row_number} has invalid {column} ADP {text!r}."
        ) from exc
    if not math.isfinite(number) or not 1.0 <= number < 900.0:
        raise FantasyProsUploadValidationError(
            f"CSV row {row_number} {column} ADP must be at least 1 and below 900."
        )
    return number


def _parse_positive_integer(value: object, field_name: str, row_number: int) -> int:
    text = _required_text(value, field_name, row_number)
    try:
        number = float(text)
    except ValueError as exc:
        raise FantasyProsUploadValidationError(
            f"CSV row {row_number} has invalid {field_name} {text!r}."
        ) from exc
    if not math.isfinite(number) or not number.is_integer() or number < 1:
        raise FantasyProsUploadValidationError(
            f"CSV row {row_number} {field_name} must be a positive integer."
        )
    return int(number)


def _required_text(value: object, field_name: str, row_number: int) -> str:
    text = _optional_text(value)
    if text is None:
        raise FantasyProsUploadValidationError(
            f"CSV row {row_number} has a blank {field_name} value."
        )
    return text


def _optional_text(value: object) -> str | None:
    if value is None:
        return None
    text = str(value).strip()
    return text or None


def _normalize_name(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", "", value.casefold())


def _as_utc(value: datetime) -> datetime:
    if value.tzinfo is None:
        raise FantasyProsUploadValidationError("Capture time must include a timezone.")
    return value.astimezone(UTC)


def _canonical_json(value: object) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"))


def _json_notes(notes: str) -> dict[str, object]:
    try:
        value = json.loads(notes)
    except (TypeError, json.JSONDecodeError):
        return {}
    return value if isinstance(value, dict) else {}
