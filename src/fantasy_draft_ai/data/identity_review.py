"""Build and resolve an auditable cross-source player identity review queue."""

from __future__ import annotations

import hashlib
import json
import re
import unicodedata
from collections import Counter
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import duckdb
import pandas as pd

from fantasy_draft_ai.config import AppConfig
from fantasy_draft_ai.data.manifests import RawArchive, SourceManifest, sha256_file
from fantasy_draft_ai.data.warehouse import Warehouse
from fantasy_draft_ai.schemas.identity import (
    IdentityResolution,
    IdentityReviewStatus,
    MappingConfidence,
)
from fantasy_draft_ai.schemas.quality import QualityIssue, QualityReport, Severity

REVIEW_WORKSHEET_COLUMNS = [
    "review_id",
    "source",
    "source_player_id",
    "source_display_name",
    "source_position",
    "source_nfl_team",
    "candidate_player_id",
    "candidate_display_name",
    "candidate_position",
    "candidate_nfl_team",
    "reason",
    "mapping_confidence",
    "status",
    "resolution",
    "player_id",
    "canonical_display_name",
    "reviewed_at",
    "reviewer",
    "notes",
]

REQUIRED_OVERRIDE_COLUMNS = frozenset(REVIEW_WORKSHEET_COLUMNS)
SUFFIXES = frozenset({"jr", "sr", "ii", "iii", "iv", "v"})
TEAM_ALIASES = {
    "ARZ": "ARI",
    "AZ": "ARI",
    "JAX": "JAC",
    "LA": "LAR",
    "OAK": "LV",
    "SD": "LAC",
    "STL": "LAR",
    "WSH": "WAS",
}
POSITION_ALIASES = {"PK": "K", "D/ST": "DEF", "DST": "DEF"}


@dataclass(frozen=True)
class CanonicalPlayer:
    player_id: str
    display_name: str
    position: str | None
    nfl_team: str | None
    gsis_id: str | None
    espn_id: str | None


@dataclass(frozen=True)
class SourceObservation:
    issue_type: str
    source: str
    source_player_id: str
    display_name: str
    position: str | None
    nfl_team: str | None
    dataset_id: str
    observed_at: datetime
    evidence: dict[str, Any]
    forced_candidate_id: str | None = None
    forced_reason: str | None = None
    excluded: bool = False


@dataclass(frozen=True)
class IdentityReviewResult:
    quality: QualityReport
    output_path: Path | None
    total_current: int
    pending: int
    resolved: int
    dismissed: int
    excluded: int
    exact: int
    high: int
    medium: int
    low: int
    committed: bool

    def render(self) -> str:
        lines = [
            self.quality.render(),
            "",
            f"Queue refresh: {'COMMITTED' if self.committed else 'NOT COMMITTED'}",
            f"Current review rows: {self.total_current}",
            f"  pending: {self.pending}",
            f"  resolved: {self.resolved}",
            f"  dismissed: {self.dismissed}",
            f"  excluded: {self.excluded}",
            "Candidate confidence:",
            f"  exact: {self.exact}",
            f"  high: {self.high}",
            f"  medium: {self.medium}",
            f"  low: {self.low}",
        ]
        if self.output_path is not None:
            lines.append(f"Review worksheet: {self.output_path}")
        return "\n".join(lines)


@dataclass(frozen=True)
class IdentityOverrideResult:
    quality: QualityReport
    committed: bool
    applied_rows: int
    matched_existing_rows: int
    skipped_pending_rows: int
    raw_path: Path | None = None
    manifest: SourceManifest | None = None
    manifest_path: Path | None = None

    def render(self) -> str:
        lines = [
            self.quality.render(),
            "",
            f"Override transaction: {'COMMITTED' if self.committed else 'NOT COMMITTED'}",
            f"  applied: {self.applied_rows}",
            f"  matched existing: {self.matched_existing_rows}",
            f"  pending rows skipped: {self.skipped_pending_rows}",
        ]
        if self.raw_path is not None:
            lines.append(f"Raw override archive: {self.raw_path}")
        if self.manifest_path is not None:
            lines.append(f"Override manifest: {self.manifest_path}")
        return "\n".join(lines)


@dataclass(frozen=True)
class _Capture:
    manifest: SourceManifest
    manifest_path: Path
    raw_paths: tuple[Path, ...]


def normalize_identity_name(value: str) -> str:
    """Fold accents and punctuation without treating names as authoritative IDs."""

    folded = unicodedata.normalize("NFKD", value)
    ascii_text = "".join(char for char in folded if not unicodedata.combining(char))
    return " ".join(re.findall(r"[a-z0-9]+", ascii_text.lower()))


def _suffixless_name(value: str) -> str:
    tokens = normalize_identity_name(value).split()
    if tokens and tokens[-1] in SUFFIXES:
        tokens = tokens[:-1]
    return " ".join(tokens)


def _normalize_team(value: str | None) -> str | None:
    if value is None or not value.strip():
        return None
    team = value.strip().upper()
    return TEAM_ALIASES.get(team, team)


def _normalize_position(value: str | None) -> str | None:
    if value is None or not value.strip():
        return None
    position = value.strip().upper()
    return POSITION_ALIASES.get(position, position)


def _clean_optional(value: Any) -> str | None:
    if value is None or pd.isna(value):
        return None
    text = str(value).strip()
    return text or None


def _stable_review_id(issue_type: str, source: str, source_player_id: str) -> str:
    payload = json.dumps(
        [issue_type, source, source_player_id], ensure_ascii=True, separators=(",", ":")
    )
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def refresh_identity_review_queue(
    config: AppConfig, *, output_path: Path | None = None
) -> IdentityReviewResult:
    """Verify current captures, rebuild review evidence, and export a worksheet."""

    warehouse = Warehouse(config.resolve(config.paths.warehouse))
    warehouse.initialize()
    issues: list[QualityIssue] = []
    captures = _latest_captures(config, issues)
    with warehouse.connect(read_only=True) as connection:
        players = _load_players(connection)
        mappings = _load_source_mappings(connection)
        league_history_observations = _league_history_observations(connection)
    if not players:
        issues.append(
            QualityIssue(
                code="canonical_players_missing",
                message="Load nflverse players before building identity reviews.",
                severity=Severity.FATAL,
            )
        )

    observations: list[SourceObservation] = []
    if not any(issue.severity == Severity.FATAL for issue in issues):
        observations.extend(league_history_observations)
        for capture in captures:
            try:
                if capture.manifest.source == "nflverse":
                    observations.extend(_nflverse_conflicts(capture))
                elif capture.manifest.source == "ffc":
                    observations.extend(_ffc_observations(capture))
                elif capture.manifest.source == "espn":
                    observations.extend(_espn_observations(capture))
            except (OSError, ValueError, json.JSONDecodeError, duckdb.Error) as exc:
                issues.append(
                    QualityIssue(
                        code="invalid_identity_capture",
                        message=(
                            f"Could not read {capture.manifest.source} identity evidence: {exc}"
                        ),
                        severity=Severity.FATAL,
                    )
                )

    rows = _build_review_rows(observations, players, mappings)
    review_id_counts = Counter(str(row["review_id"]) for row in rows)
    duplicate_keys = sum(count - 1 for count in review_id_counts.values() if count > 1)
    if duplicate_keys:
        issues.append(
            QualityIssue(
                code="duplicate_source_identity_keys",
                message="Current source evidence repeats a stable source identity key.",
                count=duplicate_keys,
                severity=Severity.FATAL,
            )
        )
    pending = sum(row["status"] == IdentityReviewStatus.PENDING for row in rows)
    unresolved = sum(
        row["status"] == IdentityReviewStatus.PENDING and row["candidate_player_id"] is None
        for row in rows
    )
    excluded = sum(row["status"] == IdentityReviewStatus.EXCLUDED for row in rows)
    conflicts = sum(row["issue_type"] == "id_name_conflict" for row in rows)
    if pending:
        issues.append(
            QualityIssue(
                code="pending_identity_reviews",
                message="Name-derived candidates remain pending until a human reviews them.",
                count=pending,
            )
        )
    if unresolved:
        issues.append(
            QualityIssue(
                code="unresolved_source_players",
                message="Source rows have no unique canonical candidate.",
                count=unresolved,
            )
        )
    if excluded:
        issues.append(
            QualityIssue(
                code="excluded_non_player_rows",
                message="Team-defense rows are explicitly excluded from player identity mapping.",
                count=excluded,
            )
        )

    quality = QualityReport(
        source="identity_review",
        row_count=len(rows),
        duplicate_keys=duplicate_keys,
        unresolved_players=unresolved,
        excluded_rows=excluded,
        identity_conflicts=conflicts,
        issues=issues,
    )
    if quality.has_fatal_errors:
        return _review_result(quality, None, committed=False)

    _merge_review_rows(
        warehouse,
        rows,
        refreshed_sources={capture.manifest.source for capture in captures},
    )
    worksheet_path = output_path or (
        config.resolve(config.paths.processed_dir) / "identity" / "identity_review_queue.csv"
    )
    worksheet_path = worksheet_path.resolve()
    _export_review_worksheet(warehouse, worksheet_path)
    return _review_result(quality, worksheet_path, committed=True, warehouse=warehouse)


def _review_result(
    quality: QualityReport,
    output_path: Path | None,
    *,
    committed: bool,
    warehouse: Warehouse | None = None,
) -> IdentityReviewResult:
    counts = {
        "total": 0,
        "pending": 0,
        "resolved": 0,
        "dismissed": 0,
        "excluded": 0,
        "exact": 0,
        "high": 0,
        "medium": 0,
        "low": 0,
    }
    if warehouse is not None:
        with warehouse.connect(read_only=True) as connection:
            result = connection.execute(
                """
                SELECT
                    count(*) AS total,
                    count(*) FILTER (WHERE status = 'pending') AS pending,
                    count(*) FILTER (WHERE status = 'resolved') AS resolved,
                    count(*) FILTER (WHERE status = 'dismissed') AS dismissed,
                    count(*) FILTER (WHERE status = 'excluded') AS excluded,
                    count(*) FILTER (WHERE mapping_confidence = 'exact') AS exact,
                    count(*) FILTER (WHERE mapping_confidence = 'high') AS high,
                    count(*) FILTER (WHERE mapping_confidence = 'medium') AS medium,
                    count(*) FILTER (WHERE mapping_confidence = 'low') AS low
                FROM identity_review_queue
                WHERE is_current
                """
            ).fetchone()
        if result is not None:
            counts = dict(zip(counts, (int(value) for value in result), strict=True))
    return IdentityReviewResult(
        quality,
        output_path,
        counts["total"],
        counts["pending"],
        counts["resolved"],
        counts["dismissed"],
        counts["excluded"],
        counts["exact"],
        counts["high"],
        counts["medium"],
        counts["low"],
        committed,
    )


def _load_manifest_entries(config: AppConfig) -> list[tuple[SourceManifest, Path]]:
    root = config.resolve(config.paths.manifests)
    entries: list[tuple[SourceManifest, Path]] = []
    for path in sorted(root.glob("*.json")) if root.exists() else ():
        try:
            manifest = SourceManifest.model_validate_json(path.read_text(encoding="utf-8"))
        except (OSError, ValueError):
            continue
        entries.append((manifest, path))
    return entries


def _latest_captures(config: AppConfig, issues: list[QualityIssue]) -> list[_Capture]:
    entries = _load_manifest_entries(config)
    captures: list[_Capture] = []
    for source in ("nflverse", "ffc", "espn"):
        candidates = [entry for entry in entries if entry[0].source == source]
        if source == "nflverse":
            candidates = [
                entry
                for entry in candidates
                if any("nflverse_players__" in raw for raw in entry[0].raw_files)
                and any("nflverse_player_stats__weekly__" in raw for raw in entry[0].raw_files)
            ]
        if not candidates:
            issues.append(
                QualityIssue(
                    code=f"{source}_capture_unavailable",
                    message=f"No {source} capture is available for identity review.",
                )
            )
            continue
        manifest, manifest_path = max(
            candidates, key=lambda item: (item[0].acquired_at, item[0].dataset_id)
        )
        raw_paths = _verify_capture(config, manifest, issues)
        if raw_paths is not None:
            captures.append(_Capture(manifest, manifest_path, raw_paths))
    return captures


def _verify_capture(
    config: AppConfig, manifest: SourceManifest, issues: list[QualityIssue]
) -> tuple[Path, ...] | None:
    if len(manifest.raw_files) != len(manifest.sha256):
        issues.append(
            QualityIssue(
                code="manifest_file_hash_mismatch",
                message=f"Manifest {manifest.dataset_id} has mismatched file and hash counts.",
                severity=Severity.FATAL,
            )
        )
        return None
    project_root = config.project_root.resolve()
    paths: list[Path] = []
    for relative, expected_hash in zip(manifest.raw_files, manifest.sha256, strict=True):
        path = (project_root / relative).resolve()
        if not path.is_relative_to(project_root) or not path.is_file():
            issues.append(
                QualityIssue(
                    code="invalid_identity_source_path",
                    message=f"Identity source file is missing or unsafe: {relative}",
                    severity=Severity.FATAL,
                )
            )
            return None
        if sha256_file(path) != expected_hash:
            issues.append(
                QualityIssue(
                    code="identity_source_hash_mismatch",
                    message=f"Identity source hash mismatch: {relative}",
                    severity=Severity.FATAL,
                )
            )
            return None
        paths.append(path)
    return tuple(paths)


def _load_players(connection: duckdb.DuckDBPyConnection) -> list[CanonicalPlayer]:
    rows = connection.execute(
        "SELECT player_id, display_name, canonical_position, nfl_team, gsis_id, espn_id "
        "FROM players"
    ).fetchall()
    return [
        CanonicalPlayer(
            str(row[0]),
            str(row[1]),
            _clean_optional(row[2]),
            _clean_optional(row[3]),
            _clean_optional(row[4]),
            _clean_optional(row[5]),
        )
        for row in rows
    ]


def _load_source_mappings(
    connection: duckdb.DuckDBPyConnection,
) -> dict[tuple[str, str], str]:
    rows = connection.execute(
        "SELECT source, source_player_id, player_id FROM player_source_mappings"
    ).fetchall()
    return {(str(row[0]), str(row[1])): str(row[2]) for row in rows}


def _league_history_observations(
    connection: duckdb.DuckDBPyConnection,
) -> list[SourceObservation]:
    """Return one auditable observation per unresolved historical source identity."""

    table_exists = connection.execute(
        "SELECT count(*) FROM information_schema.tables "
        "WHERE table_schema = 'main' AND table_name = 'draft_picks'"
    ).fetchone()
    if table_exists is None or not int(table_exists[0]):
        return []
    rows = connection.execute(
        """
        SELECT
            pick.source_platform,
            pick.source_player_id,
            pick.player_name,
            pick.position,
            pick.league_season_id,
            pick.overall_pick,
            pick.source_dataset_id,
            coalesce(pick.loaded_at, package.imported_at) AS observed_at
        FROM draft_picks AS pick
        LEFT JOIN league_history_leagues AS history
            USING (league_season_id)
        LEFT JOIN league_history_imports AS package
            USING (package_fingerprint)
        WHERE pick.player_id IS NULL
          AND nullif(trim(pick.source_platform), '') IS NOT NULL
          AND nullif(trim(pick.source_player_id), '') IS NOT NULL
        ORDER BY
            lower(pick.source_platform),
            pick.source_player_id,
            observed_at DESC NULLS LAST,
            pick.league_season_id,
            pick.overall_pick
        """
    ).fetchall()
    grouped: dict[tuple[str, str], list[tuple[Any, ...]]] = {}
    for row in rows:
        source = str(row[0]).strip().lower()
        source_player_id = str(row[1]).strip()
        grouped.setdefault((source, source_player_id), []).append(row)

    observations: list[SourceObservation] = []
    fallback_time = datetime(1970, 1, 1, tzinfo=UTC)
    for (source, source_player_id), source_rows in grouped.items():
        names = sorted(
            {value for row in source_rows if (value := _clean_optional(row[2])) is not None}
        )
        positions = sorted(
            {value for row in source_rows if (value := _clean_optional(row[3])) is not None}
        )
        league_seasons = sorted({str(row[4]) for row in source_rows})
        dataset_ids = sorted(
            {value for row in source_rows if (value := _clean_optional(row[6])) is not None}
        )
        latest_name = next(
            (value for row in source_rows if (value := _clean_optional(row[2])) is not None),
            None,
        )
        latest_dataset_id = next(
            (value for row in source_rows if (value := _clean_optional(row[6])) is not None),
            None,
        )
        observed_times = [row[7] for row in source_rows if isinstance(row[7], datetime)]
        observations.append(
            SourceObservation(
                issue_type="league_history_source_mapping",
                source=source,
                source_player_id=source_player_id,
                display_name=latest_name or "<missing name>",
                position=positions[0] if len(positions) == 1 else None,
                nfl_team=None,
                dataset_id=latest_dataset_id or "league-history:unknown",
                observed_at=max(observed_times, default=fallback_time),
                evidence={
                    "origin": "canonical_draft_picks",
                    "unresolved_pick_count": len(source_rows),
                    "league_season_ids": league_seasons,
                    "source_dataset_ids": dataset_ids,
                    "observed_names": names,
                    "observed_positions": positions,
                },
            )
        )
    return observations


def _nflverse_conflicts(capture: _Capture) -> list[SourceObservation]:
    player_paths = [
        path for path in capture.raw_paths if path.name.startswith("nflverse_players__")
    ]
    stat_paths = [
        path
        for path in capture.raw_paths
        if path.name.startswith("nflverse_player_stats__weekly__")
    ]
    if len(player_paths) != 1 or len(stat_paths) != 1:
        raise ValueError("The selected nflverse capture does not contain one player/stat pair.")
    with duckdb.connect() as connection:
        rows = connection.execute(
            """
            SELECT
                p.gsis_id,
                p.display_name,
                p.position,
                p.latest_team,
                list_sort(list_distinct(list(trim(s.player_display_name)))) AS weekly_names
            FROM read_parquet(?) AS s
            JOIN read_parquet(?) AS p ON s.player_id = p.gsis_id
            WHERE regexp_replace(lower(s.player_display_name), '[^a-z0-9]', '', 'g')
                  <> regexp_replace(lower(p.display_name), '[^a-z0-9]', '', 'g')
            GROUP BY p.gsis_id, p.display_name, p.position, p.latest_team
            """,
            [str(stat_paths[0]), str(player_paths[0])],
        ).fetchall()
    observations: list[SourceObservation] = []
    for row in rows:
        weekly_names = sorted(str(value) for value in row[4])
        observations.append(
            SourceObservation(
                issue_type="id_name_conflict",
                source="nflverse",
                source_player_id=str(row[0]),
                display_name=" / ".join(weekly_names),
                position=_clean_optional(row[2]),
                nfl_team=_clean_optional(row[3]),
                dataset_id=capture.manifest.dataset_id,
                observed_at=capture.manifest.acquired_at,
                evidence={
                    "gsis_id": str(row[0]),
                    "player_capture_name": str(row[1]),
                    "weekly_names": weekly_names,
                    "raw_sha256": list(capture.manifest.sha256),
                },
                forced_candidate_id=str(row[0]),
                forced_reason="stable_id_name_conflict",
            )
        )
    return observations


def _ffc_observations(capture: _Capture) -> list[SourceObservation]:
    json_paths = [path for path in capture.raw_paths if path.suffix.lower() == ".json"]
    if len(json_paths) != 1:
        raise ValueError("The selected FFC manifest must contain one JSON capture.")
    payload = json.loads(json_paths[0].read_text(encoding="utf-8"))
    source_rows = payload.get("players", [])
    if not isinstance(source_rows, list):
        raise ValueError("FFC capture does not contain a players list.")
    observations: list[SourceObservation] = []
    raw_hash = capture.manifest.sha256[0]
    for index, raw in enumerate(source_rows):
        if not isinstance(raw, dict):
            continue
        source_id = _clean_optional(raw.get("player_id")) or (
            f"{capture.manifest.dataset_id}:row:{index}"
        )
        name = _clean_optional(raw.get("name") or raw.get("player_name")) or "<missing name>"
        position = _clean_optional(raw.get("position"))
        team = _clean_optional(raw.get("team"))
        excluded = _normalize_position(position) == "DEF"
        observations.append(
            SourceObservation(
                issue_type="unsupported_team_defense" if excluded else "source_mapping",
                source="ffc",
                source_player_id=source_id,
                display_name=name,
                position=position,
                nfl_team=team,
                dataset_id=capture.manifest.dataset_id,
                observed_at=capture.manifest.acquired_at,
                evidence={
                    "raw_source_row_id": source_id,
                    "raw_sha256": raw_hash,
                    "rank": raw.get("overall_rank") or raw.get("rank") or index + 1,
                },
                excluded=excluded,
            )
        )
    return observations


def _espn_observations(capture: _Capture) -> list[SourceObservation]:
    csv_paths = [path for path in capture.raw_paths if path.suffix.lower() == ".csv"]
    if len(csv_paths) != 1:
        raise ValueError("The selected ESPN manifest must contain one CSV capture.")
    frame = pd.read_csv(csv_paths[0], dtype="string", keep_default_na=False)
    observations: list[SourceObservation] = []
    raw_hash = capture.manifest.sha256[0]
    for index, row in frame.iterrows():
        espn_id = _clean_optional(row.get("espn_player_id"))
        source_id = espn_id or f"{capture.manifest.dataset_id}:row:{index}"
        observations.append(
            SourceObservation(
                issue_type="source_mapping",
                source="espn",
                source_player_id=source_id,
                display_name=_clean_optional(row.get("player_name")) or "<missing name>",
                position=_clean_optional(row.get("position")),
                nfl_team=_clean_optional(row.get("nfl_team")),
                dataset_id=capture.manifest.dataset_id,
                observed_at=capture.manifest.acquired_at,
                evidence={
                    "espn_player_id": espn_id,
                    "raw_sha256": raw_hash,
                    "rank": _clean_optional(row.get("rank")),
                },
            )
        )
    return observations


def _build_review_rows(
    observations: list[SourceObservation],
    players: list[CanonicalPlayer],
    mappings: dict[tuple[str, str], str],
) -> list[dict[str, Any]]:
    players_by_id = {player.player_id: player for player in players}
    espn_ids = {player.espn_id: player for player in players if player.espn_id is not None}
    strict_names: dict[str, list[CanonicalPlayer]] = {}
    suffix_names: dict[str, list[CanonicalPlayer]] = {}
    for player in players:
        strict_names.setdefault(normalize_identity_name(player.display_name), []).append(player)
        suffix_names.setdefault(_suffixless_name(player.display_name), []).append(player)

    rows: list[dict[str, Any]] = []
    for observation in observations:
        candidate: CanonicalPlayer | None = None
        confidence = MappingConfidence.UNRESOLVED
        status = IdentityReviewStatus.PENDING
        reason = "no_canonical_candidate"
        if observation.excluded:
            status = IdentityReviewStatus.EXCLUDED
            reason = "unsupported_team_defense"
        elif mapped_id := mappings.get((observation.source, observation.source_player_id)):
            candidate = players_by_id.get(mapped_id)
            confidence = MappingConfidence.REVIEWED
            status = IdentityReviewStatus.RESOLVED
            reason = "reviewed_source_mapping"
        elif observation.forced_candidate_id is not None:
            candidate = players_by_id.get(observation.forced_candidate_id)
            confidence = MappingConfidence.HIGH
            reason = observation.forced_reason or "stable_id_conflict"
        elif observation.source == "espn" and observation.source_player_id in espn_ids:
            candidate = espn_ids[observation.source_player_id]
            confidence = MappingConfidence.EXACT
            status = IdentityReviewStatus.RESOLVED
            reason = "exact_platform_id"
        else:
            candidate, confidence, reason = _name_candidate(observation, strict_names, suffix_names)

        rows.append(
            {
                "review_id": _stable_review_id(
                    observation.issue_type, observation.source, observation.source_player_id
                ),
                "issue_type": observation.issue_type,
                "source": observation.source,
                "source_player_id": observation.source_player_id,
                "source_display_name": observation.display_name,
                "source_position": _normalize_position(observation.position),
                "source_nfl_team": _normalize_team(observation.nfl_team),
                "candidate_player_id": candidate.player_id if candidate else None,
                "candidate_display_name": candidate.display_name if candidate else None,
                "candidate_position": candidate.position if candidate else None,
                "candidate_nfl_team": candidate.nfl_team if candidate else None,
                "reason": reason,
                "mapping_confidence": confidence.value,
                "status": status.value,
                "evidence_json": json.dumps(observation.evidence, sort_keys=True),
                "evidence_dataset_id": observation.dataset_id,
                "first_seen_at": observation.observed_at,
                "last_seen_at": observation.observed_at,
                "is_current": True,
            }
        )
    return rows


def _name_candidate(
    observation: SourceObservation,
    strict_names: dict[str, list[CanonicalPlayer]],
    suffix_names: dict[str, list[CanonicalPlayer]],
) -> tuple[CanonicalPlayer | None, MappingConfidence, str]:
    strict_key = normalize_identity_name(observation.display_name)
    suffix_key = _suffixless_name(observation.display_name)
    position = _normalize_position(observation.position)
    team = _normalize_team(observation.nfl_team)

    strict = strict_names.get(strict_key, [])
    exact_context = _context_matches(strict, position, team)
    if len(exact_context) == 1:
        return exact_context[0], MappingConfidence.HIGH, "name_position_team_candidate"

    suffix = suffix_names.get(suffix_key, [])
    suffix_context = _context_matches(suffix, position, team)
    if len(suffix_context) == 1:
        return suffix_context[0], MappingConfidence.MEDIUM, "suffix_name_position_team_candidate"

    name_and_team = [
        player for player in strict if team is not None and _normalize_team(player.nfl_team) == team
    ]
    if len(name_and_team) == 1:
        return name_and_team[0], MappingConfidence.LOW, "name_team_position_conflict"

    name_and_position = [
        player
        for player in strict
        if position is not None and _normalize_position(player.position) == position
    ]
    if len(name_and_position) == 1:
        return name_and_position[0], MappingConfidence.LOW, "name_position_team_mismatch"

    if len(strict) == 1:
        return strict[0], MappingConfidence.LOW, "unique_name_only_candidate"
    if strict or suffix:
        return None, MappingConfidence.UNRESOLVED, "ambiguous_name_candidates"
    return None, MappingConfidence.UNRESOLVED, "no_canonical_candidate"


def _context_matches(
    players: list[CanonicalPlayer], position: str | None, team: str | None
) -> list[CanonicalPlayer]:
    return [
        player
        for player in players
        if (position is None or _normalize_position(player.position) == position)
        and (team is None or _normalize_team(player.nfl_team) == team)
    ]


def _merge_review_rows(
    warehouse: Warehouse,
    rows: list[dict[str, Any]],
    *,
    refreshed_sources: set[str],
) -> None:
    frame = pd.DataFrame(rows)
    with warehouse.connect() as connection:
        try:
            connection.execute("BEGIN TRANSACTION")
            connection.execute(
                "UPDATE identity_review_queue SET is_current = FALSE "
                "WHERE issue_type = 'league_history_source_mapping'"
            )
            for source in sorted(refreshed_sources):
                connection.execute(
                    "UPDATE identity_review_queue SET is_current = FALSE WHERE source = ?",
                    [source],
                )
            if rows:
                connection.register("review_rows_frame", frame)
                connection.execute(
                    "CREATE OR REPLACE TEMP TABLE staged_identity_reviews AS "
                    "SELECT * FROM review_rows_frame"
                )
                connection.execute(REVIEW_QUEUE_MERGE_SQL)
                connection.unregister("review_rows_frame")
            duplicate_count = connection.execute(
                "SELECT count(*) FROM (SELECT review_id FROM identity_review_queue "
                "GROUP BY review_id HAVING count(*) > 1)"
            ).fetchone()
            orphan_count = connection.execute(
                "SELECT count(*) FROM identity_review_queue q LEFT JOIN players p "
                "ON q.candidate_player_id = p.player_id "
                "WHERE q.candidate_player_id IS NOT NULL AND p.player_id IS NULL"
            ).fetchone()
            if duplicate_count is None or int(duplicate_count[0]):
                raise RuntimeError("Identity queue contains duplicate review IDs.")
            if orphan_count is None or int(orphan_count[0]):
                raise RuntimeError("Identity queue contains orphan candidate players.")
            connection.execute("COMMIT")
        except Exception:
            connection.execute("ROLLBACK")
            raise


REVIEW_QUEUE_MERGE_SQL = """
MERGE INTO identity_review_queue AS target
USING staged_identity_reviews AS source
ON target.review_id = source.review_id
WHEN MATCHED THEN UPDATE SET
    issue_type = source.issue_type,
    source = source.source,
    source_player_id = source.source_player_id,
    source_display_name = source.source_display_name,
    source_position = source.source_position,
    source_nfl_team = source.source_nfl_team,
    candidate_player_id = source.candidate_player_id,
    candidate_display_name = source.candidate_display_name,
    candidate_position = source.candidate_position,
    candidate_nfl_team = source.candidate_nfl_team,
    reason = source.reason,
    mapping_confidence = CASE
        WHEN target.status IN ('resolved', 'dismissed') THEN target.mapping_confidence
        ELSE source.mapping_confidence
    END,
    status = CASE
        WHEN target.status IN ('resolved', 'dismissed') THEN target.status
        ELSE source.status
    END,
    evidence_json = source.evidence_json,
    evidence_dataset_id = source.evidence_dataset_id,
    last_seen_at = source.last_seen_at,
    is_current = TRUE
WHEN NOT MATCHED THEN INSERT (
    review_id, issue_type, source, source_player_id, source_display_name,
    source_position, source_nfl_team, candidate_player_id, candidate_display_name,
    candidate_position, candidate_nfl_team, reason, mapping_confidence, status,
    evidence_json, evidence_dataset_id, first_seen_at, last_seen_at, is_current
) VALUES (
    source.review_id, source.issue_type, source.source, source.source_player_id,
    source.source_display_name, source.source_position, source.source_nfl_team,
    source.candidate_player_id, source.candidate_display_name,
    source.candidate_position, source.candidate_nfl_team, source.reason,
    source.mapping_confidence, source.status, source.evidence_json,
    source.evidence_dataset_id, source.first_seen_at, source.last_seen_at, TRUE
)
"""


def _export_review_worksheet(warehouse: Warehouse, output_path: Path) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with warehouse.connect(read_only=True) as connection:
        frame = connection.execute(
            """
            SELECT
                review_id,
                source,
                source_player_id,
                source_display_name,
                source_position,
                source_nfl_team,
                candidate_player_id,
                candidate_display_name,
                candidate_position,
                candidate_nfl_team,
                reason,
                mapping_confidence,
                status,
                coalesce(resolution, '') AS resolution,
                coalesce(resolved_player_id, candidate_player_id, '') AS player_id,
                coalesce(canonical_display_name_override, '') AS canonical_display_name,
                coalesce(cast(resolved_at AS VARCHAR), '') AS reviewed_at,
                coalesce(reviewer, '') AS reviewer,
                coalesce(resolution_note, '') AS notes
            FROM identity_review_queue
            WHERE is_current
            ORDER BY
                CASE status WHEN 'pending' THEN 0 WHEN 'resolved' THEN 1
                    WHEN 'dismissed' THEN 2 ELSE 3 END,
                source,
                source_display_name,
                source_player_id
            """
        ).fetchdf()
    frame.to_csv(output_path, index=False, columns=REVIEW_WORKSHEET_COLUMNS)


def apply_identity_overrides(config: AppConfig, source_path: Path) -> IdentityOverrideResult:
    """Validate, archive, and transactionally apply reviewed identity decisions."""

    if not source_path.is_file():
        raise FileNotFoundError(source_path)
    try:
        frame = pd.read_csv(source_path, dtype="string", keep_default_na=False)
    except Exception as exc:
        raise ValueError(f"Could not read identity override CSV: {exc}") from exc
    issues: list[QualityIssue] = []
    missing_columns = sorted(REQUIRED_OVERRIDE_COLUMNS - set(frame.columns))
    if missing_columns:
        issues.append(
            QualityIssue(
                code="missing_override_columns",
                message=f"Missing identity override columns: {', '.join(missing_columns)}",
                count=len(missing_columns),
                severity=Severity.FATAL,
            )
        )
    if missing_columns:
        quality = QualityReport(
            source="identity_overrides",
            row_count=len(frame),
            required_field_failures=len(missing_columns),
            issues=issues,
        )
        return IdentityOverrideResult(quality, False, 0, 0, 0)

    frame = frame.loc[:, REVIEW_WORKSHEET_COLUMNS].copy()
    frame = frame.apply(lambda column: column.str.strip())
    duplicate_ids = int(frame["review_id"].duplicated(keep=False).sum())
    if duplicate_ids:
        issues.append(
            QualityIssue(
                code="duplicate_override_review_ids",
                message="The override worksheet repeats review IDs.",
                count=duplicate_ids,
                severity=Severity.FATAL,
            )
        )
    missing_review_ids = int((frame["review_id"] == "").sum())
    if missing_review_ids:
        issues.append(
            QualityIssue(
                code="missing_override_review_ids",
                message="Override rows are missing review IDs.",
                count=missing_review_ids,
                severity=Severity.FATAL,
            )
        )

    decided = frame[frame["resolution"] != ""].copy()
    skipped = len(frame) - len(decided)
    allowed = {resolution.value for resolution in IdentityResolution}
    invalid_resolution = int((~decided["resolution"].isin(allowed)).sum())
    if invalid_resolution:
        issues.append(
            QualityIssue(
                code="invalid_identity_resolution",
                message=f"Resolution must be one of {sorted(allowed)}.",
                count=invalid_resolution,
                severity=Severity.FATAL,
            )
        )
    required_decision_values = (decided["reviewed_at"] == "") | (decided["reviewer"] == "")
    missing_decision_values = int(required_decision_values.sum())
    if missing_decision_values:
        issues.append(
            QualityIssue(
                code="missing_review_evidence",
                message="Decided rows require reviewed_at and reviewer.",
                count=missing_decision_values,
                severity=Severity.FATAL,
            )
        )
    reviewed_at = pd.to_datetime(decided["reviewed_at"], errors="coerce", utc=True)
    invalid_timestamps = int(reviewed_at.isna().sum())
    if invalid_timestamps:
        issues.append(
            QualityIssue(
                code="invalid_review_timestamp",
                message="reviewed_at values must be valid timestamps.",
                count=invalid_timestamps,
                severity=Severity.FATAL,
            )
        )
    decided["parsed_reviewed_at"] = reviewed_at
    if skipped:
        issues.append(
            QualityIssue(
                code="pending_override_rows_skipped",
                message="Rows without a resolution remain pending and were not applied.",
                count=skipped,
            )
        )

    warehouse = Warehouse(config.resolve(config.paths.warehouse))
    warehouse.initialize()
    validation = _validate_override_targets(warehouse, decided)
    issues.extend(validation)
    quality = QualityReport(
        source="identity_overrides",
        row_count=len(frame),
        required_field_failures=missing_decision_values + missing_review_ids,
        duplicate_keys=duplicate_ids,
        unresolved_players=sum(issue.code == "unknown_override_player" for issue in issues),
        excluded_rows=skipped,
        issues=issues,
    )
    if quality.has_fatal_errors or decided.empty:
        return IdentityOverrideResult(quality, False, 0, 0, skipped)

    raw_path, manifest, manifest_path = _archive_override_worksheet(config, source_path)
    applied, matched = _commit_overrides(warehouse, decided, manifest)
    return IdentityOverrideResult(
        quality,
        True,
        applied,
        matched,
        skipped,
        raw_path,
        manifest,
        manifest_path,
    )


def _validate_override_targets(warehouse: Warehouse, decided: pd.DataFrame) -> list[QualityIssue]:
    issues: list[QualityIssue] = []
    with warehouse.connect(read_only=True) as connection:
        queue_rows = connection.execute(
            "SELECT review_id, source, source_player_id, candidate_player_id, status, "
            "resolution, resolved_player_id, canonical_display_name_override, resolved_at, "
            "reviewer, resolution_note, is_current FROM identity_review_queue"
        ).fetchall()
        player_ids = {
            str(row[0]) for row in connection.execute("SELECT player_id FROM players").fetchall()
        }
        mappings = {
            (str(row[0]), str(row[1])): str(row[2])
            for row in connection.execute(
                "SELECT source, source_player_id, player_id FROM player_source_mappings"
            ).fetchall()
        }
        espn_owners = {
            str(row[0]): str(row[1])
            for row in connection.execute(
                "SELECT espn_id, player_id FROM players WHERE espn_id IS NOT NULL"
            ).fetchall()
        }
    queue = {str(row[0]): row for row in queue_rows}
    for _, row in decided.iterrows():
        review_id = str(row["review_id"])
        queued = queue.get(review_id)
        if queued is None:
            issues.append(
                QualityIssue(
                    code="unknown_identity_review",
                    message=f"Review ID is not present in the queue: {review_id}",
                    severity=Severity.FATAL,
                )
            )
            continue
        source = str(queued[1])
        source_player_id = str(queued[2])
        if not bool(queued[11]):
            issues.append(
                QualityIssue(
                    code="stale_identity_review",
                    message=f"Review {review_id} is not current; refresh the worksheet.",
                    severity=Severity.FATAL,
                )
            )
        if str(queued[4]) == IdentityReviewStatus.EXCLUDED.value:
            issues.append(
                QualityIssue(
                    code="excluded_identity_review",
                    message=f"Excluded non-player review {review_id} cannot be resolved or mapped.",
                    severity=Severity.FATAL,
                )
            )
        if str(row["source"]) != source or str(row["source_player_id"]) != source_player_id:
            issues.append(
                QualityIssue(
                    code="override_source_evidence_mismatch",
                    message=f"Source evidence does not match queued review {review_id}.",
                    severity=Severity.FATAL,
                )
            )
        resolution = str(row["resolution"])
        player_id = str(row["player_id"])
        candidate_id = _clean_optional(queued[3])
        if resolution == IdentityResolution.DISMISSED:
            if player_id or str(row["canonical_display_name"]):
                issues.append(
                    QualityIssue(
                        code="dismissed_review_has_player",
                        message=(
                            "Dismissed reviews must not supply a player or display-name override."
                        ),
                        severity=Severity.FATAL,
                    )
                )
            if not str(row["notes"]):
                issues.append(
                    QualityIssue(
                        code="dismissed_review_missing_note",
                        message="Dismissed reviews require a note.",
                        severity=Severity.FATAL,
                    )
                )
        else:
            if not player_id or player_id not in player_ids:
                issues.append(
                    QualityIssue(
                        code="unknown_override_player",
                        message=(
                            f"Canonical player does not exist for review {review_id}: {player_id}"
                        ),
                        severity=Severity.FATAL,
                    )
                )
            if resolution == IdentityResolution.CONFIRMED and player_id != candidate_id:
                issues.append(
                    QualityIssue(
                        code="confirmed_candidate_mismatch",
                        message=f"Confirmed review {review_id} must use its proposed candidate.",
                        severity=Severity.FATAL,
                    )
                )
            if resolution == IdentityResolution.REMAPPED and not str(row["notes"]):
                issues.append(
                    QualityIssue(
                        code="remapped_review_missing_note",
                        message="Remapped reviews require a note.",
                        severity=Severity.FATAL,
                    )
                )
            if source == "nflverse" and player_id != source_player_id:
                issues.append(
                    QualityIssue(
                        code="gsis_remap_forbidden",
                        message="A stable nflverse GSIS ID cannot be remapped by display name.",
                        severity=Severity.FATAL,
                    )
                )
            mapped = mappings.get((source, source_player_id))
            if mapped is not None and mapped != player_id:
                issues.append(
                    QualityIssue(
                        code="conflicting_source_mapping",
                        message=f"{source}:{source_player_id} is already mapped to {mapped}.",
                        severity=Severity.FATAL,
                    )
                )
            if source == "espn":
                owner = espn_owners.get(source_player_id)
                if owner is not None and owner != player_id:
                    issues.append(
                        QualityIssue(
                            code="platform_id_collision",
                            message=f"ESPN ID {source_player_id} already belongs to {owner}.",
                            severity=Severity.FATAL,
                        )
                    )
        if str(queued[4]) in {"resolved", "dismissed"} and not _same_resolution(queued, row):
            issues.append(
                QualityIssue(
                    code="conflicting_review_resolution",
                    message=f"Review {review_id} already has a different final resolution.",
                    severity=Severity.FATAL,
                )
            )
    return issues


def _same_resolution(queued: tuple[Any, ...], row: pd.Series[Any]) -> bool:
    resolved_at = pd.Timestamp(queued[8]) if queued[8] is not None else None
    incoming_at = row["parsed_reviewed_at"]
    same_time = resolved_at is not None and resolved_at == incoming_at
    return (
        _clean_optional(queued[5]) == str(row["resolution"])
        and (_clean_optional(queued[6]) or "") == str(row["player_id"])
        and (_clean_optional(queued[7]) or "") == str(row["canonical_display_name"])
        and same_time
        and (_clean_optional(queued[9]) or "") == str(row["reviewer"])
        and (_clean_optional(queued[10]) or "") == str(row["notes"])
    )


def _archive_override_worksheet(
    config: AppConfig, source_path: Path
) -> tuple[Path, SourceManifest, Path]:
    content_hash = sha256_file(source_path)
    for manifest, manifest_path in _load_manifest_entries(config):
        if (
            manifest.source == "identity_overrides"
            and len(manifest.raw_files) == 1
            and manifest.sha256 == [content_hash]
        ):
            raw_path = (config.project_root / manifest.raw_files[0]).resolve()
            if raw_path.is_file() and sha256_file(raw_path) == content_hash:
                return raw_path, manifest, manifest_path
    archive = RawArchive(
        config.project_root,
        config.resolve(config.paths.raw_dir),
        config.resolve(config.paths.manifests),
    )
    raw_path, acquired_at = archive.write_bytes(
        "identity_overrides",
        "player_identity_overrides",
        ".csv",
        source_path.read_bytes(),
    )
    manifest, manifest_path = archive.create_manifest(
        source="identity_overrides",
        acquisition_method="reviewed-csv-upload",
        acquired_at=acquired_at,
        raw_files=[raw_path],
        notes="Human-reviewed player identity decisions; raw upload retained unchanged.",
    )
    return raw_path, manifest, manifest_path


def _commit_overrides(
    warehouse: Warehouse, decided: pd.DataFrame, manifest: SourceManifest
) -> tuple[int, int]:
    applied = 0
    matched = 0
    with warehouse.connect() as connection:
        try:
            connection.execute("BEGIN TRANSACTION")
            queue_rows = {
                str(row[0]): row
                for row in connection.execute(
                    "SELECT review_id, source, source_player_id, status, resolution, "
                    "resolved_player_id, canonical_display_name_override, resolved_at, "
                    "reviewer, resolution_note, is_current FROM identity_review_queue"
                ).fetchall()
            }
            for _, row in decided.iterrows():
                review_id = str(row["review_id"])
                queued = queue_rows[review_id]
                if not bool(queued[10]) or str(queued[3]) == IdentityReviewStatus.EXCLUDED.value:
                    raise RuntimeError(
                        f"Review {review_id} is stale or excluded and cannot be resolved."
                    )
                if str(queued[3]) in {"resolved", "dismissed"}:
                    matched += 1
                    continue
                source = str(queued[1])
                source_player_id = str(queued[2])
                resolution = str(row["resolution"])
                player_id = str(row["player_id"]) or None
                canonical_name = str(row["canonical_display_name"]) or None
                reviewed_at = row["parsed_reviewed_at"].to_pydatetime()
                reviewer = str(row["reviewer"])
                notes = str(row["notes"]) or None
                status = (
                    IdentityReviewStatus.DISMISSED.value
                    if resolution == IdentityResolution.DISMISSED
                    else IdentityReviewStatus.RESOLVED.value
                )
                connection.execute(
                    """
                    UPDATE identity_review_queue SET
                        status = ?,
                        mapping_confidence = ?,
                        resolution = ?,
                        resolved_player_id = ?,
                        canonical_display_name_override = ?,
                        resolution_note = ?,
                        resolved_at = ?,
                        reviewer = ?,
                        resolution_dataset_id = ?
                    WHERE review_id = ?
                    """,
                    [
                        status,
                        MappingConfidence.REVIEWED.value
                        if player_id is not None
                        else MappingConfidence.UNRESOLVED.value,
                        resolution,
                        player_id,
                        canonical_name,
                        notes,
                        reviewed_at,
                        reviewer,
                        manifest.dataset_id,
                        review_id,
                    ],
                )
                if player_id is not None:
                    mapping_source = f"manual:identity-review:{manifest.dataset_id}"
                    connection.execute(
                        """
                        INSERT INTO player_source_mappings (
                            source, source_player_id, player_id, mapping_confidence,
                            mapping_source, review_id, reviewed_at, reviewer, notes,
                            source_dataset_id
                        ) VALUES (?, ?, ?, 'reviewed', ?, ?, ?, ?, ?, ?)
                        """,
                        [
                            source,
                            source_player_id,
                            player_id,
                            mapping_source,
                            review_id,
                            reviewed_at,
                            reviewer,
                            notes,
                            manifest.dataset_id,
                        ],
                    )
                    _apply_player_resolution(
                        connection,
                        source,
                        source_player_id,
                        player_id,
                        canonical_name,
                        mapping_source,
                    )
                applied += 1

            _refresh_league_history_mapping_metadata(connection)

            orphan_count = connection.execute(
                "SELECT count(*) FROM player_source_mappings m LEFT JOIN players p "
                "ON m.player_id = p.player_id WHERE p.player_id IS NULL"
            ).fetchone()
            duplicate_espn = connection.execute(
                "SELECT count(*) FROM (SELECT espn_id FROM players WHERE espn_id IS NOT NULL "
                "GROUP BY espn_id HAVING count(*) > 1)"
            ).fetchone()
            if orphan_count is None or int(orphan_count[0]):
                raise RuntimeError("Identity override created an orphan player mapping.")
            if duplicate_espn is None or int(duplicate_espn[0]):
                raise RuntimeError("Identity override created a duplicate ESPN ID.")
            connection.execute("COMMIT")
        except Exception:
            connection.execute("ROLLBACK")
            raise
    return applied, matched


def _refresh_league_history_mapping_metadata(
    connection: duckdb.DuckDBPyConnection,
) -> None:
    """Reconcile derived history readiness after transactional identity changes."""

    league_rows = connection.execute(
        """
        SELECT league_season_id, expected_pick_rows, team_count
        FROM league_history_leagues
        ORDER BY league_season_id
        """
    ).fetchall()
    for league_season_id, expected_pick_rows, team_count in league_rows:
        counts = connection.execute(
            """
            SELECT
                count(*) AS actual_pick_rows,
                count(*) FILTER (WHERE player_id IS NOT NULL) AS resolved_pick_rows
            FROM draft_picks
            WHERE league_season_id = ?
            """,
            [league_season_id],
        ).fetchone()
        outcome_count = connection.execute(
            "SELECT count(*) FROM team_outcomes WHERE league_season_id = ?",
            [league_season_id],
        ).fetchone()
        if counts is None or outcome_count is None:
            raise RuntimeError("Could not reconcile league-history mapping readiness.")
        actual = int(counts[0])
        resolved = int(counts[1])
        outcomes = int(outcome_count[0])
        draft_complete = actual == int(expected_pick_rows)
        outcomes_complete = outcomes == int(team_count)
        analysis_ready = draft_complete and outcomes_complete and resolved == actual
        connection.execute(
            """
            UPDATE league_history_leagues SET
                actual_pick_rows = ?,
                outcome_rows = ?,
                resolved_pick_rows = ?,
                draft_complete = ?,
                outcomes_complete = ?,
                analysis_ready = ?
            WHERE league_season_id = ?
            """,
            [
                actual,
                outcomes,
                resolved,
                draft_complete,
                outcomes_complete,
                analysis_ready,
                league_season_id,
            ],
        )

    package_rows = connection.execute(
        """
        SELECT package_fingerprint, schema_version, quality_report
        FROM league_history_imports
        WHERE status = 'imported'
        ORDER BY package_fingerprint
        """
    ).fetchall()
    for package_fingerprint, schema_version, stored_report in package_rows:
        summary = connection.execute(
            """
            SELECT
                count(*) AS league_count,
                count(*) FILTER (WHERE draft_complete) AS draft_complete_leagues,
                count(*) FILTER (WHERE outcomes_complete) AS outcomes_complete_leagues,
                count(*) FILTER (WHERE analysis_ready) AS analysis_ready_leagues
            FROM league_history_leagues
            WHERE package_fingerprint = ?
            """,
            [package_fingerprint],
        ).fetchone()
        unresolved_row = connection.execute(
            """
            SELECT count(*)
            FROM league_history_leagues AS history
            JOIN draft_picks AS pick USING (league_season_id)
            WHERE history.package_fingerprint = ? AND pick.player_id IS NULL
            """,
            [package_fingerprint],
        ).fetchone()
        if summary is None or unresolved_row is None:
            raise RuntimeError("Could not reconcile league-history package readiness.")
        unresolved = int(unresolved_row[0])
        payload = json.loads(str(stored_report))
        quality = QualityReport.model_validate(payload["quality"])
        issues = [
            issue for issue in quality.issues if issue.code != "unresolved_player_mappings"
        ]
        if unresolved:
            issues.append(
                QualityIssue(
                    code="unresolved_player_mappings",
                    message=(
                        "Draft picks without a canonical/source-ID or reviewed mapping were "
                        "retained with player_id null; display names were not joined."
                    ),
                    count=unresolved,
                )
            )
        current_quality = quality.model_copy(
            update={"unresolved_players": unresolved, "issues": issues}
        )
        analysis_ready_leagues = int(summary[3])
        reasons = [
            "Championship modeling remains disabled until the separate data-sufficiency gate "
            "passes."
        ]
        if not analysis_ready_leagues:
            reasons.append(
                "No league has a complete draft, complete outcomes, and 100% resolved draft "
                "picks."
            )
        readiness = {
            "schema_version": str(schema_version),
            "archived": True,
            "normalized": True,
            "league_count": int(summary[0]),
            "draft_complete_leagues": int(summary[1]),
            "outcomes_complete_leagues": int(summary[2]),
            "analysis_ready_leagues": analysis_ready_leagues,
            "championship_model_status": "disabled",
            "reasons": reasons,
        }
        quality_report = json.dumps(
            {
                "quality": current_quality.model_dump(mode="json"),
                "readiness": readiness,
            },
            sort_keys=True,
            separators=(",", ":"),
            ensure_ascii=True,
        )
        connection.execute(
            """
            UPDATE league_history_imports SET
                unresolved_player_rows = ?,
                quality_report = ?
            WHERE package_fingerprint = ?
            """,
            [unresolved, quality_report, package_fingerprint],
        )


def _apply_player_resolution(
    connection: duckdb.DuckDBPyConnection,
    source: str,
    source_player_id: str,
    player_id: str,
    canonical_name: str | None,
    mapping_source: str,
) -> None:
    if source == "espn":
        connection.execute(
            "UPDATE players SET espn_id = coalesce(espn_id, ?) WHERE player_id = ?",
            [source_player_id, player_id],
        )
    if source == "nflverse" or canonical_name is not None:
        connection.execute(
            """
            UPDATE players SET
                display_name = coalesce(?, display_name),
                mapping_confidence = 'reviewed',
                mapping_source = ?
            WHERE player_id = ?
            """,
            [canonical_name, mapping_source, player_id],
        )
    connection.execute(
        """
        UPDATE adp_snapshots SET player_id = ?, mapping_confidence = 'reviewed'
        WHERE source = ? AND raw_source_row_id = ?
        """,
        [player_id, source, source_player_id],
    )
    connection.execute(
        """
        UPDATE draft_picks SET
            player_id = ?,
            mapping_confidence = 'reviewed'
        WHERE lower(source_platform) = ?
          AND source_player_id = ?
          AND (player_id IS NULL OR player_id = ?)
        """,
        [player_id, source.lower(), source_player_id, player_id],
    )
