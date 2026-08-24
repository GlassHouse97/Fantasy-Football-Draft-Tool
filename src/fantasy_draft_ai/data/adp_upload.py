"""Preview, archive, and load user-supplied platform ADP CSV snapshots.

The upload is intentionally a two-step operation. ``preview_adp_upload`` parses
and validates bytes without writing anything. ``commit_adp_upload`` accepts that
immutable preview, archives the exact original bytes, writes a linked normalized
representation, and delegates the transactional warehouse work to the canonical
ADP loader.
"""

from __future__ import annotations

import csv
import hashlib
import io
import json
import math
import re
import unicodedata
from collections import Counter
from collections.abc import Iterable
from dataclasses import dataclass, field, replace
from datetime import UTC, datetime
from pathlib import Path
from typing import Final, Literal

from fantasy_draft_ai.config import AppConfig
from fantasy_draft_ai.data.adp_loader import AdpLoadResult, load_adp_to_warehouse
from fantasy_draft_ai.data.manifests import RawArchive, SourceManifest, sha256_file, utc_now
from fantasy_draft_ai.data.warehouse import Warehouse

AdpUploadSource = Literal["espn", "yahoo", "sleeper", "underdog"]

ADP_UPLOAD_SOURCES: Final = frozenset({"espn", "yahoo", "sleeper", "underdog"})
DEFAULT_SCORING_FORMAT: Final = {
    "espn": "ppr",
    "yahoo": "half_ppr",
    "sleeper": "ppr",
    "underdog": "half_ppr",
}
UPLOAD_ACQUISITION_METHOD: Final = "user-uploaded-source-of-truth-csv-v1"
NORMALIZED_ACQUISITION_METHOD: Final = "normalized-user-upload-source-of-truth-v1"
UPLOAD_NOTES_SCHEMA: Final = "adp_upload_source_v1"
NORMALIZED_NOTES_SCHEMA: Final = "adp_upload_normalized_v1"
NORMALIZED_COLUMNS: Final = (
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
SUPPORTED_POSITIONS: Final = frozenset({"QB", "RB", "WR", "TE", "K", "DST"})
MAX_ADP_UPLOAD_BYTES: Final = 10 * 1024 * 1024
MAX_ADP_UPLOAD_DATA_ROWS: Final = 10_000


class AdpUploadValidationError(ValueError):
    """A fail-closed validation error safe for the upload UI to display."""


@dataclass(frozen=True)
class AdpUploadColumnMapping:
    """Explicit semantic-to-source CSV column selection."""

    player_name: str
    average_pick: str
    position: str | None = None
    nfl_team: str | None = None
    source_player_id: str | None = None
    rank: str | None = None

    def as_dict(self) -> dict[str, str | None]:
        """Return a stable JSON-serializable representation."""

        return {
            "player_name": self.player_name,
            "average_pick": self.average_pick,
            "position": self.position,
            "nfl_team": self.nfl_team,
            "source_player_id": self.source_player_id,
            "rank": self.rank,
        }


@dataclass(frozen=True)
class AdpUploadCsvInspection:
    """Header and bounded sample information used to build mapping controls."""

    columns: tuple[str, ...]
    data_rows: int
    sample_rows: tuple[dict[str, str], ...]


@dataclass(frozen=True)
class AdpUploadColumnDetection:
    """Conservative header suggestions; ambiguous fields remain unselected."""

    player_name: str | None
    average_pick: str | None
    position: str | None
    nfl_team: str | None
    source_player_id: str | None
    rank: str | None
    ambiguous_fields: tuple[tuple[str, tuple[str, ...]], ...] = ()

    @property
    def ready(self) -> bool:
        """Return whether both required fields were detected unambiguously."""

        return self.player_name is not None and self.average_pick is not None

    def to_column_mapping(self) -> AdpUploadColumnMapping:
        """Build explicit input for preview, failing when required guesses are absent."""

        if not self.ready:
            raise AdpUploadValidationError(
                "Player-name and ADP columns must be selected explicitly before preview."
            )
        return AdpUploadColumnMapping(
            player_name=self.player_name or "",
            average_pick=self.average_pick or "",
            position=self.position,
            nfl_team=self.nfl_team,
            source_player_id=self.source_player_id,
            rank=self.rank,
        )


@dataclass(frozen=True)
class AdpUploadScope:
    """The exact market scope that determines latest-snapshot display behavior."""

    source: str
    captured_at: datetime
    season: int
    scoring_format: str
    team_count: int
    position_scope: str = "overall"


@dataclass(frozen=True)
class AdpUploadPreviewRow:
    """One normalized, deduplicated row shown before archive/load."""

    source_row_numbers: tuple[int, ...]
    source_player_id: str
    player_name: str
    normalized_name: str
    position: str
    nfl_team: str | None
    average_pick: float
    rank: int
    canonical_player_id: str | None
    mapping_confidence: str


@dataclass(frozen=True)
class AdpUploadPreview:
    """Validated write-free preview that can be committed without reparsing."""

    file_name: str
    raw_sha256: str
    scope: AdpUploadScope
    columns: AdpUploadColumnMapping
    input_rows: int
    accepted_rows: int
    duplicates_collapsed: int
    rows: tuple[AdpUploadPreviewRow, ...]
    mapping_confidence_counts: tuple[tuple[str, int], ...]
    upload_fingerprint: str
    raw_bytes: bytes = field(repr=False)


@dataclass(frozen=True)
class AdpUploadImportResult:
    """Immutable archive provenance plus the actual canonical load result."""

    preview: AdpUploadPreview
    original_raw_path: Path
    original_manifest: SourceManifest
    original_manifest_path: Path
    normalized_raw_path: Path
    normalized_manifest: SourceManifest
    normalized_manifest_path: Path
    load: AdpLoadResult
    mapping_confidence_counts: tuple[tuple[str, int], ...]
    reused_archive: bool

    @property
    def committed(self) -> bool:
        """Return whether the canonical ADP warehouse transaction committed."""

        return self.load.committed


@dataclass(frozen=True)
class _CanonicalPlayer:
    player_id: str
    display_name: str
    normalized_name: str
    position: str | None
    nfl_team: str | None


@dataclass(frozen=True)
class _IdentityLookup:
    by_name: dict[str, tuple[_CanonicalPlayer, ...]]
    direct: dict[tuple[str, str], _CanonicalPlayer]
    ambiguous_direct: frozenset[tuple[str, str]]
    reviewed: dict[tuple[str, str], _CanonicalPlayer]


@dataclass(frozen=True)
class _ParsedRow:
    source_row_numbers: tuple[int, ...]
    player_name: str
    normalized_name: str
    average_pick: float
    position: str | None
    nfl_team: str | None
    source_player_id: str | None
    rank: int | None
    canonical_player: _CanonicalPlayer | None
    mapping_confidence: str


def inspect_adp_upload_csv(content: bytes, *, sample_size: int = 5) -> AdpUploadCsvInspection:
    """Inspect an uploaded CSV without writing it or guessing semantic columns."""

    if sample_size < 0 or sample_size > 25:
        raise ValueError("sample_size must be between 0 and 25.")
    columns, rows = _read_csv(content)
    samples = tuple(
        {column: str(row.get(column) or "") for column in columns}
        for row in rows[:sample_size]
    )
    return AdpUploadCsvInspection(columns=columns, data_rows=len(rows), sample_rows=samples)


def detect_adp_upload_columns(content: bytes) -> AdpUploadColumnDetection:
    """Suggest common ADP headers while leaving every choice editable by the UI."""

    headers, _ = _read_csv(content)
    aliases = {
        "player_name": (
            "playername",
            "player",
            "fullname",
            "name",
            "athletename",
        ),
        "average_pick": (
            "averagepick",
            "avgpick",
            "overalladp",
            "adp",
            "average",
        ),
        "position": ("position", "pos", "playerposition"),
        "nfl_team": ("nflteam", "team", "tm", "proteam"),
        "source_player_id": (
            "sourceplayerid",
            "playerid",
            "espnplayerid",
            "espnid",
            "yahooplayerid",
            "yahooid",
            "sleeperplayerid",
            "sleeperid",
            "underdogplayerid",
            "underdogid",
            "id",
        ),
        "rank": ("overallrank", "adprank", "rank", "rk"),
    }
    normalized_headers: dict[str, list[str]] = {}
    for header in headers:
        normalized_headers.setdefault(_normalize_header(header), []).append(header)
    detected: dict[str, str | None] = {}
    ambiguous: list[tuple[str, tuple[str, ...]]] = []
    for field_name, field_aliases in aliases.items():
        matches: list[str] = []
        for alias in field_aliases:
            matches.extend(normalized_headers.get(alias, ()))
        unique_matches = tuple(dict.fromkeys(matches))
        if len(unique_matches) == 1:
            detected[field_name] = unique_matches[0]
        else:
            detected[field_name] = None
            if len(unique_matches) > 1:
                ambiguous.append((field_name, unique_matches))
    return AdpUploadColumnDetection(
        player_name=detected["player_name"],
        average_pick=detected["average_pick"],
        position=detected["position"],
        nfl_team=detected["nfl_team"],
        source_player_id=detected["source_player_id"],
        rank=detected["rank"],
        ambiguous_fields=tuple(ambiguous),
    )


def preview_adp_upload(
    config: AppConfig,
    content: bytes,
    *,
    file_name: str,
    source: AdpUploadSource | str,
    columns: AdpUploadColumnMapping,
    captured_at: datetime | None = None,
    season: int | None = None,
    scoring_format: str | None = None,
    team_count: int = 12,
) -> AdpUploadPreview:
    """Validate, normalize, resolve, and deduplicate one CSV without writing files."""

    normalized_source = _validate_source(source)
    scope = _validate_scope(
        source=normalized_source,
        captured_at=captured_at or utc_now(),
        season=season or config.project.prediction_season,
        scoring_format=scoring_format or DEFAULT_SCORING_FORMAT[normalized_source],
        team_count=team_count,
    )
    headers, raw_rows = _read_csv(content)
    _validate_column_mapping(columns, headers)
    identity_lookup = _load_identity_lookup(config, normalized_source)

    parsed_rows: list[_ParsedRow] = []
    for row_number, raw in enumerate(raw_rows, start=2):
        if not any(_optional_text(value) for value in raw.values()):
            continue
        parsed_rows.append(
            _parse_upload_row(
                raw,
                row_number=row_number,
                columns=columns,
                source=normalized_source,
                identities=identity_lookup,
            )
        )
    if not parsed_rows:
        raise AdpUploadValidationError("The uploaded CSV has no nonblank ADP data rows.")

    _validate_source_id_collisions(parsed_rows)
    deduplicated = _deduplicate_rows(parsed_rows)
    ordered = sorted(
        deduplicated,
        key=lambda row: (row.average_pick, row.normalized_name, row.source_player_id or ""),
    )
    preview_rows = tuple(
        _to_preview_row(row, derived_rank=index)
        for index, row in enumerate(ordered, start=1)
    )
    confidence_counts = _count_confidences(row.mapping_confidence for row in preview_rows)
    raw_sha256 = hashlib.sha256(content).hexdigest()
    fingerprint_payload = {
        "columns": columns.as_dict(),
        "raw_sha256": raw_sha256,
        "scope": _scope_payload(scope),
        "schema": UPLOAD_NOTES_SCHEMA,
    }
    upload_fingerprint = hashlib.sha256(_canonical_json(fingerprint_payload).encode()).hexdigest()
    return AdpUploadPreview(
        file_name=Path(file_name).name or "uploaded-adp.csv",
        raw_sha256=raw_sha256,
        scope=scope,
        columns=columns,
        input_rows=len(parsed_rows),
        accepted_rows=len(preview_rows),
        duplicates_collapsed=len(parsed_rows) - len(preview_rows),
        rows=preview_rows,
        mapping_confidence_counts=confidence_counts,
        upload_fingerprint=upload_fingerprint,
        raw_bytes=content,
    )


def commit_adp_upload(config: AppConfig, preview: AdpUploadPreview) -> AdpUploadImportResult:
    """Archive an exact preview and idempotently load its normalized snapshot."""

    actual_hash = hashlib.sha256(preview.raw_bytes).hexdigest()
    if actual_hash != preview.raw_sha256:
        raise AdpUploadValidationError(
            "The preview bytes changed before commit; create a new preview and try again."
        )
    verified_preview = preview_adp_upload(
        config,
        preview.raw_bytes,
        file_name=preview.file_name,
        source=preview.scope.source,
        columns=preview.columns,
        captured_at=preview.scope.captured_at,
        season=preview.scope.season,
        scoring_format=preview.scope.scoring_format,
        team_count=preview.scope.team_count,
    )
    if (
        verified_preview.upload_fingerprint != preview.upload_fingerprint
        or verified_preview.rows != preview.rows
    ):
        raise AdpUploadValidationError(
            "The upload preview is stale or its normalized rows changed; preview it again "
            "before applying."
        )

    existing = _find_existing_archive(config, preview)
    if existing is None:
        archive_bundle = _archive_upload(config, preview)
        reused_archive = False
    else:
        archive_bundle = existing
        reused_archive = True
    (
        original_raw_path,
        original_manifest,
        original_manifest_path,
        normalized_raw_path,
        normalized_manifest,
        normalized_manifest_path,
    ) = archive_bundle

    load = load_adp_to_warehouse(config, manifest_paths=[normalized_manifest_path])
    if not load.committed or len(load.snapshots) != 1:
        return AdpUploadImportResult(
            preview=preview,
            original_raw_path=original_raw_path,
            original_manifest=original_manifest,
            original_manifest_path=original_manifest_path,
            normalized_raw_path=normalized_raw_path,
            normalized_manifest=normalized_manifest,
            normalized_manifest_path=normalized_manifest_path,
            load=load,
            mapping_confidence_counts=(),
            reused_archive=reused_archive,
        )
    confidence_counts = _warehouse_confidence_counts(config, load.snapshots[0].snapshot_id)
    return AdpUploadImportResult(
        preview=preview,
        original_raw_path=original_raw_path,
        original_manifest=original_manifest,
        original_manifest_path=original_manifest_path,
        normalized_raw_path=normalized_raw_path,
        normalized_manifest=normalized_manifest,
        normalized_manifest_path=normalized_manifest_path,
        load=load,
        mapping_confidence_counts=confidence_counts,
        reused_archive=reused_archive,
    )


def import_adp_upload(
    config: AppConfig,
    content: bytes,
    *,
    file_name: str,
    source: AdpUploadSource | str,
    columns: AdpUploadColumnMapping,
    captured_at: datetime | None = None,
    season: int | None = None,
    scoring_format: str | None = None,
    team_count: int = 12,
) -> AdpUploadImportResult:
    """Convenience wrapper for callers that do not need a separate confirmation step."""

    preview = preview_adp_upload(
        config,
        content,
        file_name=file_name,
        source=source,
        columns=columns,
        captured_at=captured_at,
        season=season,
        scoring_format=scoring_format,
        team_count=team_count,
    )
    return commit_adp_upload(config, preview)


def _read_csv(content: bytes) -> tuple[tuple[str, ...], list[dict[str, str | None]]]:
    if not content:
        raise AdpUploadValidationError("The uploaded CSV is empty.")
    if len(content) > MAX_ADP_UPLOAD_BYTES:
        raise AdpUploadValidationError(
            "The uploaded CSV exceeds the 10 MB backend safety limit."
        )
    try:
        text = content.decode("utf-8-sig")
    except UnicodeDecodeError as exc:
        raise AdpUploadValidationError("The uploaded CSV must be UTF-8 encoded.") from exc
    try:
        reader = csv.DictReader(io.StringIO(text, newline=""))
        columns = tuple(reader.fieldnames or ())
        rows: list[dict[str, str | None]] = []
        for data_row_number, row in enumerate(reader, start=1):
            if data_row_number > MAX_ADP_UPLOAD_DATA_ROWS:
                raise AdpUploadValidationError(
                    "The uploaded CSV exceeds the 10,000 data-row backend safety limit."
                )
            rows.append(row)
    except csv.Error as exc:
        raise AdpUploadValidationError(f"The uploaded file is not valid CSV: {exc}") from exc
    if not columns:
        raise AdpUploadValidationError("The uploaded CSV does not contain a header row.")
    if any(not _optional_text(column) for column in columns):
        raise AdpUploadValidationError("The uploaded CSV contains a blank column header.")
    duplicate_headers = sorted(column for column, count in Counter(columns).items() if count > 1)
    if duplicate_headers:
        raise AdpUploadValidationError(
            "The uploaded CSV contains duplicate headers: " + ", ".join(duplicate_headers) + "."
        )
    return columns, rows


def _validate_column_mapping(
    columns: AdpUploadColumnMapping,
    headers: tuple[str, ...],
) -> None:
    mapping = columns.as_dict()
    for required in ("player_name", "average_pick"):
        if not _optional_text(mapping[required]):
            raise AdpUploadValidationError(f"A {required} column must be selected.")
    selected = [value for value in mapping.values() if value is not None and value.strip()]
    missing = sorted(set(selected) - set(headers))
    if missing:
        raise AdpUploadValidationError(
            "Selected columns are absent from the CSV: " + ", ".join(missing) + "."
        )
    duplicates = sorted(value for value, count in Counter(selected).items() if count > 1)
    if duplicates:
        raise AdpUploadValidationError(
            "Each source column may map to only one field; repeated selections: "
            + ", ".join(duplicates)
            + "."
        )


def _parse_upload_row(
    raw: dict[str, str | None],
    *,
    row_number: int,
    columns: AdpUploadColumnMapping,
    source: str,
    identities: _IdentityLookup,
) -> _ParsedRow:
    player_name = _required_text(raw.get(columns.player_name), "player name", row_number)
    normalized_name = _normalize_name(player_name)
    if not normalized_name:
        raise AdpUploadValidationError(f"CSV row {row_number} has an invalid player name.")
    average_pick = _parse_adp(raw.get(columns.average_pick), row_number)
    position = _normalize_position(_mapped_value(raw, columns.position))
    team = _normalize_team(_mapped_value(raw, columns.nfl_team))
    source_player_id = _normalize_identifier(_mapped_value(raw, columns.source_player_id))
    rank = _parse_optional_rank(_mapped_value(raw, columns.rank), row_number)
    canonical, confidence = _resolve_identity(
        source=source,
        source_player_id=source_player_id,
        normalized_name=normalized_name,
        position=position,
        nfl_team=team,
        identities=identities,
        row_number=row_number,
    )
    if canonical is not None:
        player_name = canonical.display_name
        normalized_name = canonical.normalized_name
        position = position or canonical.position
        team = team or canonical.nfl_team
    if position is None:
        raise AdpUploadValidationError(
            f"CSV row {row_number} has no position and {player_name!r} could not be "
            "resolved uniquely to a canonical player with a position."
        )
    if position not in SUPPORTED_POSITIONS:
        raise AdpUploadValidationError(
            f"CSV row {row_number} has unsupported position {position!r}."
        )
    return _ParsedRow(
        source_row_numbers=(row_number,),
        player_name=_normalize_display_name(player_name),
        normalized_name=normalized_name,
        average_pick=average_pick,
        position=position,
        nfl_team=team,
        source_player_id=source_player_id,
        rank=rank,
        canonical_player=canonical,
        mapping_confidence=confidence,
    )


def _resolve_identity(
    *,
    source: str,
    source_player_id: str | None,
    normalized_name: str,
    position: str | None,
    nfl_team: str | None,
    identities: _IdentityLookup,
    row_number: int,
) -> tuple[_CanonicalPlayer | None, str]:
    direct: _CanonicalPlayer | None = None
    confidence = "unresolved"
    if source_player_id is not None:
        key = (source, source_player_id)
        if key in identities.ambiguous_direct:
            raise AdpUploadValidationError(
                f"CSV row {row_number} source ID {source_player_id!r} maps to multiple "
                "canonical players. The upload was not archived."
            )
        direct = identities.reviewed.get(key)
        if direct is not None:
            confidence = "reviewed"
        else:
            direct = identities.direct.get(key)
            if direct is not None:
                confidence = "exact"

    candidates: list[_CanonicalPlayer] = []
    if position is not None:
        candidates = [
            candidate
            for candidate in identities.by_name.get(normalized_name, ())
            if candidate.position == position
        ]
        if nfl_team is not None:
            candidates = [
                candidate
                for candidate in candidates
                if candidate.nfl_team is None or candidate.nfl_team == nfl_team
            ]
    if len(candidates) > 1 and direct is None:
        candidate_ids = ", ".join(candidate.player_id for candidate in candidates[:5])
        raise AdpUploadValidationError(
            f"CSV row {row_number} player {normalized_name!r} is ambiguous across canonical "
            f"players ({candidate_ids}). Add position/team/source ID evidence."
        )
    if direct is not None and len(candidates) > 1:
        named = next(
            (candidate for candidate in candidates if candidate.player_id == direct.player_id),
            None,
        )
    else:
        named = candidates[0] if len(candidates) == 1 else None
    if direct is not None and named is not None and direct.player_id != named.player_id:
        raise AdpUploadValidationError(
            f"CSV row {row_number} source ID and name/position/team identify different "
            "canonical players. The upload was not archived."
        )
    chosen = direct or named
    if chosen is not None:
        if position is not None and chosen.position is not None and position != chosen.position:
            raise AdpUploadValidationError(
                f"CSV row {row_number} position conflicts with canonical identity "
                f"{chosen.player_id}."
            )
        if nfl_team is not None and chosen.nfl_team is not None and nfl_team != chosen.nfl_team:
            raise AdpUploadValidationError(
                f"CSV row {row_number} team conflicts with canonical identity "
                f"{chosen.player_id}."
            )
        if direct is None:
            confidence = "high"
    return chosen, confidence


def _deduplicate_rows(rows: list[_ParsedRow]) -> list[_ParsedRow]:
    deduplicated: dict[tuple[str, ...], _ParsedRow] = {}
    for row in rows:
        key = ("normalized", row.normalized_name, row.position or "")
        prior = deduplicated.get(key)
        if prior is None:
            deduplicated[key] = row
            continue
        if (
            prior.canonical_player is not None
            and row.canonical_player is not None
            and prior.canonical_player.player_id != row.canonical_player.player_id
        ):
            raise AdpUploadValidationError(
                f"CSV rows {prior.source_row_numbers[0]} and {row.source_row_numbers[0]} "
                "normalize to the same name and position but identify different canonical "
                "players. The upload was not archived."
            )
        if not math.isclose(prior.average_pick, row.average_pick, rel_tol=0.0, abs_tol=1e-9):
            raise AdpUploadValidationError(
                f"CSV rows {prior.source_row_numbers[0]} and {row.source_row_numbers[0]} "
                "normalize to the same "
                f"player but contain conflicting ADPs ({prior.average_pick} and "
                f"{row.average_pick}). The upload was not archived."
            )
        if (
            prior.source_player_id is not None
            and row.source_player_id is not None
            and prior.source_player_id != row.source_player_id
        ):
            raise AdpUploadValidationError(
                f"CSV rows {prior.source_row_numbers[0]} and {row.source_row_numbers[0]} "
                "normalize to the same "
                "player but contain different source player IDs."
            )
        if (
            prior.nfl_team is not None
            and row.nfl_team is not None
            and prior.nfl_team != row.nfl_team
        ):
            raise AdpUploadValidationError(
                f"CSV rows {prior.source_row_numbers[0]} and {row.source_row_numbers[0]} "
                "normalize to the same player but contain conflicting teams "
                f"({prior.nfl_team} and {row.nfl_team}). The upload was not archived."
            )
        selected_source_id = prior.source_player_id or row.source_player_id
        selected_team = prior.nfl_team or row.nfl_team
        selected_canonical = prior.canonical_player or row.canonical_player
        selected_player_name = (
            selected_canonical.display_name
            if selected_canonical is not None
            else prior.player_name
        )
        selected_rank = min(
            value for value in (prior.rank, row.rank) if value is not None
        ) if prior.rank is not None or row.rank is not None else None
        confidence = _stronger_confidence(prior.mapping_confidence, row.mapping_confidence)
        deduplicated[key] = replace(
            prior,
            source_row_numbers=prior.source_row_numbers + row.source_row_numbers,
            source_player_id=selected_source_id,
            nfl_team=selected_team,
            player_name=selected_player_name,
            canonical_player=selected_canonical,
            rank=selected_rank,
            mapping_confidence=confidence,
        )
    return list(deduplicated.values())


def _validate_source_id_collisions(rows: list[_ParsedRow]) -> None:
    seen: dict[str, _ParsedRow] = {}
    for row in rows:
        if row.source_player_id is None:
            continue
        prior = seen.get(row.source_player_id)
        if prior is None:
            seen[row.source_player_id] = row
            continue
        if not _compatible_identity(prior, row):
            raise AdpUploadValidationError(
                f"CSV rows {prior.source_row_numbers[0]} and {row.source_row_numbers[0]} "
                "reuse source player ID "
                f"{row.source_player_id!r} for different normalized identities."
            )


def _compatible_identity(left: _ParsedRow, right: _ParsedRow) -> bool:
    if left.canonical_player is not None and right.canonical_player is not None:
        return left.canonical_player.player_id == right.canonical_player.player_id
    if left.normalized_name != right.normalized_name or left.position != right.position:
        return False
    return (
        left.nfl_team is None
        or right.nfl_team is None
        or left.nfl_team == right.nfl_team
    )


def _load_identity_lookup(config: AppConfig, source: str) -> _IdentityLookup:
    warehouse = Warehouse(config.resolve(config.paths.warehouse))
    if not warehouse.path.is_file():
        return _IdentityLookup(
            by_name={}, direct={}, ambiguous_direct=frozenset(), reviewed={}
        )
    with warehouse.connect(read_only=True) as connection:
        raw_players = connection.execute(
            """
            SELECT player.player_id, player.display_name, player.canonical_position,
                   player.nfl_team, player.espn_id, player.yahoo_id, player.sleeper_id
            FROM players AS player
            WHERE coalesce(player.is_active, false)
               OR EXISTS (
                    SELECT 1 FROM player_projection_board AS board
                    WHERE board.player_id = player.player_id
                      AND board.prediction_season = ?
               )
            """,
            [config.project.prediction_season],
        ).fetchall()
        reviewed_rows = connection.execute(
            """
            SELECT mapping.source_player_id, player.player_id, player.display_name,
                   player.canonical_position, player.nfl_team
            FROM player_source_mappings AS mapping
            JOIN players AS player ON player.player_id = mapping.player_id
            WHERE lower(trim(mapping.source)) = ?
              AND mapping.mapping_confidence = 'reviewed'
            """,
            [source],
        ).fetchall()

    players_by_id: dict[str, _CanonicalPlayer] = {}
    by_name_lists: dict[str, list[_CanonicalPlayer]] = {}
    direct_lists: dict[tuple[str, str], list[_CanonicalPlayer]] = {}
    source_column_index = {"espn": 4, "yahoo": 5, "sleeper": 6}.get(source)
    for raw in raw_players:
        player = _CanonicalPlayer(
            player_id=str(raw[0]),
            display_name=_normalize_display_name(str(raw[1])),
            normalized_name=_normalize_name(str(raw[1])),
            position=_normalize_position(_optional_text(raw[2])),
            nfl_team=_normalize_team(_optional_text(raw[3])),
        )
        players_by_id[player.player_id] = player
        by_name_lists.setdefault(player.normalized_name, []).append(player)
        if source_column_index is not None:
            source_id = _normalize_identifier(raw[source_column_index])
            if source_id is not None:
                direct_lists.setdefault((source, source_id), []).append(player)

    ambiguous_direct = frozenset(key for key, values in direct_lists.items() if len(values) != 1)
    direct = {key: values[0] for key, values in direct_lists.items() if len(values) == 1}
    reviewed: dict[tuple[str, str], _CanonicalPlayer] = {}
    for raw in reviewed_rows:
        source_id = _normalize_identifier(raw[0])
        if source_id is None:
            continue
        player = players_by_id.get(str(raw[1])) or _CanonicalPlayer(
            player_id=str(raw[1]),
            display_name=_normalize_display_name(str(raw[2])),
            normalized_name=_normalize_name(str(raw[2])),
            position=_normalize_position(_optional_text(raw[3])),
            nfl_team=_normalize_team(_optional_text(raw[4])),
        )
        reviewed[(source, source_id)] = player
    return _IdentityLookup(
        by_name={
            key: tuple(sorted(values, key=lambda player: player.player_id))
            for key, values in by_name_lists.items()
        },
        direct=direct,
        ambiguous_direct=ambiguous_direct,
        reviewed=reviewed,
    )


def _archive_upload(
    config: AppConfig,
    preview: AdpUploadPreview,
) -> tuple[Path, SourceManifest, Path, Path, SourceManifest, Path]:
    archive = RawArchive(
        project_root=config.project_root,
        raw_root=config.resolve(config.paths.raw_dir),
        manifest_root=config.resolve(config.paths.manifests),
    )
    file_stem = _safe_file_stem(preview.file_name)
    original_raw_path, archived_at = archive.write_bytes(
        "user_uploaded_adp",
        f"{preview.scope.source}_adp_upload__{file_stem}",
        ".csv",
        preview.raw_bytes,
    )
    original_notes = _canonical_json(
        {
            "column_mapping": preview.columns.as_dict(),
            "file_name": preview.file_name,
            "raw_sha256": preview.raw_sha256,
            "schema": UPLOAD_NOTES_SCHEMA,
            "scope": _scope_payload(preview.scope),
            "upload_fingerprint": preview.upload_fingerprint,
        }
    )
    original_manifest, original_manifest_path = archive.create_manifest(
        source="user_uploaded_adp",
        acquisition_method=UPLOAD_ACQUISITION_METHOD,
        acquired_at=archived_at,
        raw_files=[original_raw_path],
        seasons=[preview.scope.season],
        notes=original_notes,
    )

    normalized_bytes = _normalized_csv_bytes(preview)
    normalized_raw_path, normalized_at = archive.write_bytes(
        f"{preview.scope.source}_adp",
        (
            f"{preview.scope.source}_adp__upload_normalized__"
            f"{preview.scope.scoring_format}__{preview.scope.team_count}_team__"
            f"{preview.scope.season}"
        ),
        ".csv",
        normalized_bytes,
    )
    normalized_notes = _canonical_json(
        {
            "original_dataset_id": original_manifest.dataset_id,
            "original_raw_sha256": preview.raw_sha256,
            "schema": NORMALIZED_NOTES_SCHEMA,
            "scope": _scope_payload(preview.scope),
            "upload_fingerprint": preview.upload_fingerprint,
        }
    )
    normalized_manifest, normalized_manifest_path = archive.create_manifest(
        source=preview.scope.source,
        acquisition_method=NORMALIZED_ACQUISITION_METHOD,
        acquired_at=normalized_at,
        raw_files=[normalized_raw_path],
        seasons=[preview.scope.season],
        notes=normalized_notes,
    )
    return (
        original_raw_path,
        original_manifest,
        original_manifest_path,
        normalized_raw_path,
        normalized_manifest,
        normalized_manifest_path,
    )


def _find_existing_archive(
    config: AppConfig,
    preview: AdpUploadPreview,
) -> tuple[Path, SourceManifest, Path, Path, SourceManifest, Path] | None:
    manifest_root = config.resolve(config.paths.manifests)
    if not manifest_root.exists():
        return None
    manifests: dict[str, tuple[SourceManifest, Path]] = {}
    normalized_match: tuple[SourceManifest, Path, dict[str, object]] | None = None
    for path in sorted(manifest_root.glob("*.json")):
        try:
            manifest = SourceManifest.model_validate_json(path.read_text(encoding="utf-8"))
        except (OSError, ValueError):
            continue
        manifests[manifest.dataset_id] = (manifest, path)
        if (
            manifest.source.casefold() != preview.scope.source
            or manifest.acquisition_method != NORMALIZED_ACQUISITION_METHOD
        ):
            continue
        notes = _json_notes(manifest.notes)
        if notes.get("upload_fingerprint") == preview.upload_fingerprint:
            normalized_match = (manifest, path, notes)
    if normalized_match is None:
        return None
    normalized_manifest, normalized_manifest_path, normalized_notes = normalized_match
    original_id = str(normalized_notes.get("original_dataset_id") or "")
    original_pair = manifests.get(original_id)
    if original_pair is None:
        raise AdpUploadValidationError(
            "An existing normalized upload is missing its original-byte provenance manifest."
        )
    original_manifest, original_manifest_path = original_pair
    original_raw_path = _verified_single_raw_path(config, original_manifest)
    normalized_raw_path = _verified_single_raw_path(config, normalized_manifest)
    if original_manifest.sha256[0] != preview.raw_sha256:
        raise AdpUploadValidationError(
            "An existing upload fingerprint points to different original bytes."
        )
    return (
        original_raw_path,
        original_manifest,
        original_manifest_path,
        normalized_raw_path,
        normalized_manifest,
        normalized_manifest_path,
    )


def _verified_single_raw_path(config: AppConfig, manifest: SourceManifest) -> Path:
    if len(manifest.raw_files) != 1 or len(manifest.sha256) != 1:
        raise AdpUploadValidationError(
            f"Upload manifest {manifest.dataset_id} must contain exactly one raw file."
        )
    project_root = config.project_root.resolve()
    path = (project_root / manifest.raw_files[0]).resolve()
    if not path.is_relative_to(project_root) or not path.is_file():
        raise AdpUploadValidationError(
            f"Archived upload file is missing or outside the project: {manifest.raw_files[0]}"
        )
    if sha256_file(path) != manifest.sha256[0]:
        raise AdpUploadValidationError(
            f"Archived upload hash verification failed: {manifest.raw_files[0]}"
        )
    return path


def _normalized_csv_bytes(preview: AdpUploadPreview) -> bytes:
    output = io.StringIO(newline="")
    writer = csv.DictWriter(output, fieldnames=NORMALIZED_COLUMNS, lineterminator="\n")
    writer.writeheader()
    for row in preview.rows:
        writer.writerow(
            {
                "captured_at": preview.scope.captured_at.isoformat().replace("+00:00", "Z"),
                "season": preview.scope.season,
                "source": preview.scope.source,
                "scoring_format": preview.scope.scoring_format,
                "team_count": preview.scope.team_count,
                "source_player_id": row.source_player_id,
                "player_name": row.player_name,
                "position": row.position,
                "nfl_team": row.nfl_team or "",
                "average_pick": format(row.average_pick, ".12g"),
                "rank": row.rank,
            }
        )
    return output.getvalue().encode("utf-8")


def _warehouse_confidence_counts(
    config: AppConfig,
    snapshot_id: str,
) -> tuple[tuple[str, int], ...]:
    warehouse = Warehouse(config.resolve(config.paths.warehouse))
    with warehouse.connect(read_only=True) as connection:
        rows = connection.execute(
            """
            SELECT mapping_confidence, count(*)
            FROM adp_snapshots
            WHERE snapshot_id = ?
            GROUP BY mapping_confidence
            ORDER BY mapping_confidence
            """,
            [snapshot_id],
        ).fetchall()
    return tuple((str(confidence), int(count)) for confidence, count in rows)


def _to_preview_row(row: _ParsedRow, *, derived_rank: int) -> AdpUploadPreviewRow:
    source_player_id = row.source_player_id or _generated_source_id(row)
    return AdpUploadPreviewRow(
        source_row_numbers=row.source_row_numbers,
        source_player_id=source_player_id,
        player_name=row.player_name,
        normalized_name=row.normalized_name,
        position=row.position or "",
        nfl_team=row.nfl_team,
        average_pick=row.average_pick,
        rank=row.rank or derived_rank,
        canonical_player_id=(
            row.canonical_player.player_id if row.canonical_player is not None else None
        ),
        mapping_confidence=row.mapping_confidence,
    )


def _validate_source(source: str) -> str:
    normalized = source.strip().casefold()
    if normalized not in ADP_UPLOAD_SOURCES:
        raise AdpUploadValidationError(
            "ADP upload source must be one of: espn, yahoo, sleeper, underdog."
        )
    return normalized


def _validate_scope(
    *,
    source: str,
    captured_at: datetime,
    season: int,
    scoring_format: str,
    team_count: int,
) -> AdpUploadScope:
    if captured_at.tzinfo is None:
        raise AdpUploadValidationError("ADP capture time must include a timezone.")
    if not 2000 <= season <= 2100:
        raise AdpUploadValidationError("ADP season must be between 2000 and 2100.")
    if not 4 <= team_count <= 32:
        raise AdpUploadValidationError("ADP team count must be between 4 and 32.")
    normalized_format = re.sub(
        r"[^a-z0-9]+", "_", scoring_format.strip().casefold()
    ).strip("_")
    if not normalized_format:
        raise AdpUploadValidationError("ADP scoring format cannot be blank.")
    return AdpUploadScope(
        source=source,
        captured_at=captured_at.astimezone(UTC),
        season=season,
        scoring_format=normalized_format,
        team_count=team_count,
    )


def _scope_payload(scope: AdpUploadScope) -> dict[str, object]:
    return {
        "captured_at": scope.captured_at.isoformat(),
        "position_scope": scope.position_scope,
        "scoring_format": scope.scoring_format,
        "season": scope.season,
        "source": scope.source,
        "team_count": scope.team_count,
    }


def _mapped_value(raw: dict[str, str | None], column: str | None) -> str | None:
    return raw.get(column) if column is not None else None


def _parse_adp(value: object, row_number: int) -> float:
    text = _optional_text(value)
    if text is None:
        raise AdpUploadValidationError(f"CSV row {row_number} has a blank ADP.")
    normalized = text.replace(",", "").strip()
    try:
        result = float(normalized)
    except ValueError as exc:
        raise AdpUploadValidationError(
            f"CSV row {row_number} ADP {text!r} is not numeric."
        ) from exc
    if not math.isfinite(result) or not 1.0 <= result < 900.0:
        raise AdpUploadValidationError(
            f"CSV row {row_number} ADP must be at least 1 and below 900."
        )
    return result


def _parse_optional_rank(value: object, row_number: int) -> int | None:
    text = _optional_text(value)
    if text is None:
        return None
    normalized = text.replace(",", "").strip()
    try:
        number = float(normalized)
    except ValueError as exc:
        raise AdpUploadValidationError(
            f"CSV row {row_number} rank {text!r} is not numeric."
        ) from exc
    if not math.isfinite(number) or not number.is_integer() or number < 1:
        raise AdpUploadValidationError(
            f"CSV row {row_number} rank must be a positive whole number."
        )
    return int(number)


def _normalize_identifier(value: object) -> str | None:
    text = _optional_text(value)
    if text is None or text.casefold() in {"nan", "none", "null"}:
        return None
    numeric = re.fullmatch(r"([+-]?\d+)\.0+", text)
    return numeric.group(1) if numeric is not None else text


def _normalize_name(value: str) -> str:
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


def _normalize_display_name(value: str) -> str:
    return " ".join(value.strip().split())


def _normalize_position(value: str | None) -> str | None:
    text = _optional_text(value)
    if text is None:
        return None
    compact = re.sub(r"[^A-Z]", "", text.upper())
    aliases = {"PK": "K", "D": "DST", "DEF": "DST", "DEFENSE": "DST"}
    return aliases.get(compact, compact) or None


def _normalize_team(value: str | None) -> str | None:
    text = _optional_text(value)
    if text is None:
        return None
    compact = re.sub(r"[^A-Z0-9]", "", text.upper())
    if compact in {"", "FA", "FREEAGENT", "NONE", "NA", "NAN"}:
        return None
    aliases = {
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
        "SANDIEGOCHARGERS": "LAC",
        "SD": "LAC",
        "LOSANGELESRAMS": "LAR",
        "STLOUISRAMS": "LAR",
        "STL": "LAR",
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
    return aliases.get(compact, compact)


def _generated_source_id(row: _ParsedRow) -> str:
    payload = "|".join((row.normalized_name, row.position or "", row.nfl_team or ""))
    digest = hashlib.sha256(payload.encode()).hexdigest()[:24]
    return f"upload-name:{digest}"


def _required_text(value: object, field_name: str, row_number: int) -> str:
    text = _optional_text(value)
    if text is None:
        raise AdpUploadValidationError(f"CSV row {row_number} has a blank {field_name}.")
    return text


def _optional_text(value: object) -> str | None:
    if value is None:
        return None
    text = str(value).strip()
    return text or None


def _count_confidences(values: Iterable[str]) -> tuple[tuple[str, int], ...]:
    counts = Counter(values)
    return tuple(sorted(counts.items()))


def _stronger_confidence(left: str, right: str) -> str:
    order = {"unresolved": 0, "high": 1, "exact": 2, "reviewed": 3}
    return max((left, right), key=lambda value: order.get(value, -1))


def _safe_file_stem(file_name: str) -> str:
    stem = Path(file_name).stem
    safe = re.sub(r"[^a-zA-Z0-9_-]+", "_", stem).strip("_")
    return safe[:80] or "uploaded_adp"


def _normalize_header(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", "", value.strip().casefold())


def _canonical_json(value: object) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"))


def _json_notes(value: str) -> dict[str, object]:
    try:
        parsed = json.loads(value)
    except json.JSONDecodeError:
        return {}
    return parsed if isinstance(parsed, dict) else {}
