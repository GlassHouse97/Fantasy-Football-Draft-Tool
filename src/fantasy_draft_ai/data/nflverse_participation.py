"""Validate and load immutable nflverse/PFR snap-count captures."""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path

import duckdb

from fantasy_draft_ai.config import AppConfig
from fantasy_draft_ai.data.manifests import SourceManifest, sha256_file
from fantasy_draft_ai.data.warehouse import Warehouse
from fantasy_draft_ai.schemas.quality import QualityIssue, QualityReport, Severity

SNAP_COUNT_REQUIRED_COLUMNS = frozenset(
    {
        "game_id",
        "pfr_game_id",
        "season",
        "game_type",
        "week",
        "player",
        "pfr_player_id",
        "position",
        "team",
        "opponent",
        "offense_snaps",
        "offense_pct",
        "defense_snaps",
        "defense_pct",
        "st_snaps",
        "st_pct",
    }
)


@dataclass(frozen=True)
class ParticipationLoadSummary:
    """Row accounting for one snap-count capture."""

    source_rows: int
    normalized_rows: int
    excluded_rows: int
    inserted_rows: int
    matched_existing_rows: int
    deleted_rows: int
    final_table_rows: int


@dataclass(frozen=True)
class NflverseParticipationLoadResult:
    """Quality findings and committed participation row accounting."""

    manifest: SourceManifest
    manifest_path: Path
    quality: QualityReport
    participation: ParticipationLoadSummary
    regular_season_rows: int
    postseason_rows: int
    committed: bool

    def render(self) -> str:
        summary = self.participation
        return "\n".join(
            [
                self.quality.render(),
                "",
                f"Manifest dataset: {self.manifest.dataset_id}",
                f"Manifest file: {self.manifest_path}",
                f"Warehouse transaction: {'COMMITTED' if self.committed else 'NOT COMMITTED'}",
                "Snap-count season types:",
                f"  regular season: {self.regular_season_rows}",
                f"  postseason: {self.postseason_rows}",
                "player_game_participation row accounting:",
                (
                    f"  source={summary.source_rows}, normalized={summary.normalized_rows}, "
                    f"excluded={summary.excluded_rows}, inserted={summary.inserted_rows}, "
                    f"matched_existing={summary.matched_existing_rows}, "
                    f"deleted={summary.deleted_rows}, "
                    f"final_table={summary.final_table_rows}"
                ),
            ]
        )


def find_latest_nflverse_snap_counts_manifest(config: AppConfig) -> Path:
    """Return the newest valid manifest containing one snap-count capture."""

    manifest_root = config.resolve(config.paths.manifests)
    candidates: list[tuple[SourceManifest, Path]] = []
    for path in manifest_root.glob("*.json") if manifest_root.exists() else ():
        try:
            manifest = SourceManifest.model_validate_json(path.read_text(encoding="utf-8"))
        except (OSError, ValueError, json.JSONDecodeError):
            continue
        has_snap_counts = any(
            Path(raw_file).name.startswith("nflverse_snap_counts__")
            for raw_file in manifest.raw_files
        )
        if manifest.source == "nflverse" and has_snap_counts:
            candidates.append((manifest, path))
    if not candidates:
        raise FileNotFoundError(
            "No nflverse snap-count manifest was found. "
            "Archive snap counts with download_nflverse_snap_counts first."
        )
    return max(candidates, key=lambda item: item[0].acquired_at)[1]


def load_nflverse_participation_to_warehouse(
    config: AppConfig, *, manifest_path: Path | None = None
) -> NflverseParticipationLoadResult:
    """Validate, map by PFR ID, and transactionally upsert game participation."""

    selected_manifest_path = manifest_path or find_latest_nflverse_snap_counts_manifest(config)
    selected_manifest_path = selected_manifest_path.resolve()
    manifest = SourceManifest.model_validate_json(
        selected_manifest_path.read_text(encoding="utf-8")
    )
    issues: list[QualityIssue] = []
    snap_path = _resolve_snap_capture(config, manifest, issues)
    empty = ParticipationLoadSummary(0, 0, 0, 0, 0, 0, 0)
    if snap_path is None or _has_fatal(issues):
        return NflverseParticipationLoadResult(
            manifest,
            selected_manifest_path,
            QualityReport(source="nflverse_pfr_snap_counts", row_count=0, issues=issues),
            empty,
            0,
            0,
            False,
        )

    metrics = _capture_metrics(snap_path)
    issues.extend(_capture_issues(metrics))
    expected_seasons = set(manifest.seasons)
    observed_seasons = _observed_seasons(snap_path)
    if not expected_seasons or expected_seasons != observed_seasons:
        issues.append(
            QualityIssue(
                code="manifest_season_mismatch",
                message=(
                    f"Manifest seasons {sorted(expected_seasons)} do not match "
                    f"snap-count seasons {sorted(observed_seasons)}."
                ),
                severity=Severity.FATAL,
            )
        )

    warehouse = Warehouse(config.resolve(config.paths.warehouse))
    warehouse.initialize()
    mapping = _mapping_metrics(warehouse, snap_path)
    if mapping["duplicate_player_pfr_ids"]:
        issues.append(
            QualityIssue(
                code="duplicate_player_pfr_ids",
                message="Canonical players contain duplicate non-null PFR IDs.",
                count=mapping["duplicate_player_pfr_ids"],
                severity=Severity.FATAL,
            )
        )
    if mapping["unresolved_player_ids"]:
        issues.append(
            QualityIssue(
                code="unresolved_pfr_players",
                message=(
                    "Snap-count PFR IDs are absent from canonical players; their rows are "
                    "reported and excluded rather than name-matched."
                ),
                count=mapping["unresolved_player_ids"],
                severity=Severity.WARNING,
            )
        )
    if metrics["source_rows"] and not mapping["mapped_rows"]:
        issues.append(
            QualityIssue(
                code="no_mapped_participation_rows",
                message=(
                    "No snap-count rows map to canonical PFR IDs. Reload the nflverse "
                    "player dimension before loading participation."
                ),
                severity=Severity.FATAL,
            )
        )

    required_failures = metrics["missing_required_keys"] + metrics["missing_snap_values"]
    excluded_rows = mapping["unresolved_rows"]
    quality = QualityReport(
        source="nflverse_pfr_snap_counts",
        row_count=metrics["source_rows"],
        required_field_failures=required_failures,
        duplicate_keys=metrics["duplicate_keys"],
        unresolved_players=mapping["unresolved_player_ids"],
        excluded_rows=excluded_rows,
        issues=issues,
    )
    preflight = ParticipationLoadSummary(
        metrics["source_rows"],
        mapping["mapped_rows"],
        excluded_rows,
        0,
        0,
        0,
        0,
    )
    if quality.has_fatal_errors:
        return NflverseParticipationLoadResult(
            manifest,
            selected_manifest_path,
            quality,
            preflight,
            metrics["regular_season_rows"],
            metrics["postseason_rows"],
            False,
        )

    summary = _commit_load(warehouse, manifest, snap_path, metrics, mapping)
    return NflverseParticipationLoadResult(
        manifest,
        selected_manifest_path,
        quality,
        summary,
        metrics["regular_season_rows"],
        metrics["postseason_rows"],
        True,
    )


def _resolve_snap_capture(
    config: AppConfig, manifest: SourceManifest, issues: list[QualityIssue]
) -> Path | None:
    if manifest.source != "nflverse":
        issues.append(
            QualityIssue(
                code="wrong_manifest_source",
                message=f"Expected nflverse manifest, received {manifest.source!r}.",
                severity=Severity.FATAL,
            )
        )
    if len(manifest.raw_files) != 1 or len(manifest.sha256) != 1:
        issues.append(
            QualityIssue(
                code="invalid_capture_count",
                message="Expected exactly one snap-count raw file and SHA-256 digest.",
                count=len(manifest.raw_files),
                severity=Severity.FATAL,
            )
        )
        return None
    relative = Path(manifest.raw_files[0])
    if not relative.name.startswith("nflverse_snap_counts__"):
        issues.append(
            QualityIssue(
                code="invalid_snap_capture_name",
                message=f"Manifest file is not an nflverse snap-count capture: {relative}",
                severity=Severity.FATAL,
            )
        )
        return None
    project_root = config.project_root.resolve()
    path = (project_root / relative).resolve()
    if not path.is_relative_to(project_root):
        issues.append(
            QualityIssue(
                code="raw_path_outside_project",
                message=f"Manifest path leaves the project root: {relative}",
                severity=Severity.FATAL,
            )
        )
        return None
    if not path.is_file():
        issues.append(
            QualityIssue(
                code="missing_raw_file",
                message=f"Raw snap-count file is missing: {relative}",
                severity=Severity.FATAL,
            )
        )
        return None
    if sha256_file(path) != manifest.sha256[0]:
        issues.append(
            QualityIssue(
                code="raw_hash_mismatch",
                message=f"Raw snap-count hash does not match its manifest: {relative}",
                severity=Severity.FATAL,
            )
        )
        return None
    with duckdb.connect() as connection:
        columns = {
            str(row[0])
            for row in connection.execute(
                "DESCRIBE SELECT * FROM read_parquet(?)", [str(path)]
            ).fetchall()
        }
    missing = sorted(SNAP_COUNT_REQUIRED_COLUMNS - columns)
    if missing:
        issues.append(
            QualityIssue(
                code="missing_snap_count_columns",
                message=f"Missing snap-count columns: {', '.join(missing)}",
                count=len(missing),
                severity=Severity.FATAL,
            )
        )
        return None
    return path


def _capture_metrics(path: Path) -> dict[str, int]:
    with duckdb.connect() as connection:
        source_file = str(path)
        return {
            "source_rows": _scalar(
                connection, "SELECT count(*) FROM read_parquet(?)", [source_file]
            ),
            "regular_season_rows": _scalar(
                connection,
                "SELECT count(*) FROM read_parquet(?) WHERE upper(game_type) = 'REG'",
                [source_file],
            ),
            "postseason_rows": _scalar(
                connection,
                "SELECT count(*) FROM read_parquet(?) WHERE upper(game_type) <> 'REG'",
                [source_file],
            ),
            "missing_required_keys": _scalar(
                connection,
                "SELECT count(*) FROM read_parquet(?) WHERE season IS NULL OR week IS NULL "
                "OR game_id IS NULL OR trim(game_id) = '' OR game_type IS NULL "
                "OR trim(game_type) = '' OR pfr_player_id IS NULL "
                "OR trim(pfr_player_id) = ''",
                [source_file],
            ),
            "missing_snap_values": _scalar(
                connection,
                "SELECT count(*) FROM read_parquet(?) WHERE offense_snaps IS NULL "
                "OR defense_snaps IS NULL OR st_snaps IS NULL",
                [source_file],
            ),
            "duplicate_keys": _scalar(
                connection,
                "SELECT coalesce(sum(n - 1), 0) FROM (SELECT trim(game_id) AS game_id, "
                "trim(pfr_player_id) AS pfr_player_id, count(*) AS n "
                "FROM read_parquet(?) GROUP BY trim(game_id), trim(pfr_player_id) "
                "HAVING count(*) > 1)",
                [source_file],
            ),
            "multi_game_week_rows": _scalar(
                connection,
                "SELECT coalesce(sum(n - 1), 0) FROM (SELECT season, week, "
                "pfr_player_id, count(*) AS n FROM read_parquet(?) "
                "GROUP BY season, week, pfr_player_id HAVING count(*) > 1)",
                [source_file],
            ),
            "invalid_snap_values": _scalar(
                connection,
                "SELECT count(*) FROM read_parquet(?) WHERE offense_snaps < 0 "
                "OR defense_snaps < 0 OR st_snaps < 0 OR offense_pct < 0 "
                "OR offense_pct > 1.01 OR defense_pct < 0 OR defense_pct > 1.01 "
                "OR st_pct < 0 OR st_pct > 1.01",
                [source_file],
            ),
            "rounded_percentage_rows": _scalar(
                connection,
                "SELECT count(*) FROM read_parquet(?) WHERE "
                "offense_pct > 1 OR defense_pct > 1 OR st_pct > 1",
                [source_file],
            ),
        }


def _capture_issues(metrics: dict[str, int]) -> list[QualityIssue]:
    issues: list[QualityIssue] = []
    if metrics["missing_required_keys"]:
        issues.append(
            QualityIssue(
                code="missing_snap_count_keys",
                message="Snap-count rows are missing a season, week, game, or PFR player ID.",
                count=metrics["missing_required_keys"],
                severity=Severity.FATAL,
            )
        )
    if metrics["missing_snap_values"]:
        issues.append(
            QualityIssue(
                code="missing_snap_values",
                message="Snap-count rows are missing offense, defense, or special-teams counts.",
                count=metrics["missing_snap_values"],
                severity=Severity.FATAL,
            )
        )
    if metrics["duplicate_keys"]:
        issues.append(
            QualityIssue(
                code="duplicate_snap_count_keys",
                message="Snap counts duplicate the canonical game/PFR-player key.",
                count=metrics["duplicate_keys"],
                severity=Severity.FATAL,
            )
        )
    if metrics["multi_game_week_rows"]:
        issues.append(
            QualityIssue(
                code="multiple_games_in_player_week",
                message=(
                    "A PFR player ID appears in multiple games in one week; game-level "
                    "keys preserve every source row."
                ),
                count=metrics["multi_game_week_rows"],
                severity=Severity.WARNING,
            )
        )
    if metrics["invalid_snap_values"]:
        issues.append(
            QualityIssue(
                code="invalid_snap_values",
                message=(
                    "Snap counts are negative or percentages fall outside the accepted "
                    "zero-to-1.01 source range."
                ),
                count=metrics["invalid_snap_values"],
                severity=Severity.FATAL,
            )
        )
    if metrics["rounded_percentage_rows"]:
        issues.append(
            QualityIssue(
                code="snap_percentage_rounding",
                message=(
                    "Source snap percentages exceed 1.00 by at most 0.01 because of "
                    "published rounding; raw values are retained."
                ),
                count=metrics["rounded_percentage_rows"],
                severity=Severity.WARNING,
            )
        )
    return issues


def _observed_seasons(path: Path) -> set[int]:
    with duckdb.connect() as connection:
        rows = connection.execute(
            "SELECT DISTINCT season FROM read_parquet(?) WHERE season IS NOT NULL",
            [str(path)],
        ).fetchall()
    return {int(row[0]) for row in rows}


def _mapping_metrics(warehouse: Warehouse, path: Path) -> dict[str, int]:
    source_file = str(path)
    with warehouse.connect(read_only=True) as connection:
        return {
            "duplicate_player_pfr_ids": _scalar(
                connection,
                "SELECT coalesce(sum(n - 1), 0) FROM (SELECT pfr_id, count(*) AS n "
                "FROM players WHERE pfr_id IS NOT NULL GROUP BY pfr_id HAVING count(*) > 1)",
                [],
            ),
            "unresolved_player_ids": _scalar(
                connection,
                "SELECT count(DISTINCT s.pfr_player_id) FROM read_parquet(?) s "
                "LEFT JOIN players p ON s.pfr_player_id = p.pfr_id "
                "WHERE s.pfr_player_id IS NOT NULL AND p.player_id IS NULL",
                [source_file],
            ),
            "unresolved_rows": _scalar(
                connection,
                "SELECT count(*) FROM read_parquet(?) s LEFT JOIN players p "
                "ON s.pfr_player_id = p.pfr_id WHERE p.player_id IS NULL",
                [source_file],
            ),
            "mapped_rows": _scalar(
                connection,
                "SELECT count(*) FROM read_parquet(?) s JOIN players p "
                "ON s.pfr_player_id = p.pfr_id",
                [source_file],
            ),
        }


def _commit_load(
    warehouse: Warehouse,
    manifest: SourceManifest,
    path: Path,
    metrics: dict[str, int],
    mapping: dict[str, int],
) -> ParticipationLoadSummary:
    with warehouse.connect() as connection:
        try:
            connection.execute("BEGIN TRANSACTION")
            connection.execute(
                NORMALIZE_PARTICIPATION_SQL,
                [manifest.acquired_at, manifest.dataset_id, str(path)],
            )
            existing = _scalar(
                connection,
                "SELECT count(*) FROM normalized_participation s "
                "JOIN player_game_participation t ON s.game_id = t.game_id "
                "AND s.player_id = t.player_id "
                "AND s.source = t.source",
                [],
            )
            connection.execute(
                "CREATE OR REPLACE TEMP TABLE participation_manifest_seasons "
                "(season INTEGER PRIMARY KEY)"
            )
            connection.executemany(
                "INSERT INTO participation_manifest_seasons VALUES (?)",
                [(season,) for season in sorted(set(manifest.seasons))],
            )
            before_prune = _scalar(
                connection,
                "SELECT count(*) FROM player_game_participation "
                "WHERE source = 'nflverse_pfr_snap_counts' "
                "AND season IN (SELECT season FROM participation_manifest_seasons)",
                [],
            )
            connection.execute(PARTICIPATION_PRUNE_SQL)
            after_prune = _scalar(
                connection,
                "SELECT count(*) FROM player_game_participation "
                "WHERE source = 'nflverse_pfr_snap_counts' "
                "AND season IN (SELECT season FROM participation_manifest_seasons)",
                [],
            )
            connection.execute(PARTICIPATION_MERGE_SQL)
            loaded = _scalar(
                connection,
                "SELECT count(*) FROM player_game_participation "
                "WHERE source = 'nflverse_pfr_snap_counts' AND source_dataset_id = ?",
                [manifest.dataset_id],
            )
            if loaded != mapping["mapped_rows"]:
                raise RuntimeError(
                    "Post-load participation count does not match mapped snap-count rows."
                )
            orphan_count = _scalar(
                connection,
                "SELECT count(*) FROM player_game_participation s LEFT JOIN players p "
                "ON s.player_id = p.player_id WHERE p.player_id IS NULL",
                [],
            )
            if orphan_count:
                raise RuntimeError(
                    f"Post-load validation found {orphan_count} orphan participation rows."
                )
            final_rows = _scalar(connection, "SELECT count(*) FROM player_game_participation", [])
            connection.execute("COMMIT")
        except Exception:
            connection.execute("ROLLBACK")
            raise
    normalized = mapping["mapped_rows"]
    return ParticipationLoadSummary(
        metrics["source_rows"],
        normalized,
        mapping["unresolved_rows"],
        normalized - existing,
        existing,
        before_prune - after_prune,
        final_rows,
    )


def _scalar(connection: duckdb.DuckDBPyConnection, query: str, parameters: list[object]) -> int:
    row = connection.execute(query, parameters).fetchone()
    if row is None:
        raise RuntimeError("DuckDB participation query returned no row.")
    return int(row[0])


def _has_fatal(issues: list[QualityIssue]) -> bool:
    return any(issue.severity == Severity.FATAL for issue in issues)


NORMALIZE_PARTICIPATION_SQL = """
CREATE OR REPLACE TEMP TABLE normalized_participation AS
SELECT
    s.season,
    s.week,
    trim(s.game_id) AS game_id,
    p.player_id,
    nullif(trim(s.pfr_game_id), '') AS pfr_game_id,
    trim(s.pfr_player_id) AS pfr_player_id,
    upper(trim(s.game_type)) AS game_type,
    CASE WHEN upper(trim(s.game_type)) = 'REG' THEN 'REG' ELSE 'POST' END AS season_type,
    upper(nullif(trim(s.position), '')) AS position,
    upper(nullif(trim(s.team), '')) AS nfl_team,
    upper(nullif(trim(s.opponent), '')) AS opponent,
    s.offense_snaps::DOUBLE AS offense_snaps,
    s.offense_pct::DOUBLE AS offense_snap_pct,
    s.defense_snaps::DOUBLE AS defense_snaps,
    s.defense_pct::DOUBLE AS defense_snap_pct,
    s.st_snaps::DOUBLE AS special_teams_snaps,
    s.st_pct::DOUBLE AS special_teams_snap_pct,
    'nflverse_pfr_snap_counts'::VARCHAR AS source,
    ?::TIMESTAMPTZ AS as_of,
    ?::VARCHAR AS source_dataset_id
FROM read_parquet(?) s
JOIN players p ON s.pfr_player_id = p.pfr_id
"""


PARTICIPATION_PRUNE_SQL = """
DELETE FROM player_game_participation AS target
WHERE target.source = 'nflverse_pfr_snap_counts'
  AND target.season IN (
      SELECT season FROM participation_manifest_seasons
  )
  AND NOT EXISTS (
      SELECT 1
      FROM normalized_participation AS source
      WHERE source.season = target.season
        AND source.game_id = target.game_id
        AND source.player_id = target.player_id
        AND source.source = target.source
  )
"""


PARTICIPATION_MERGE_SQL = """
MERGE INTO player_game_participation AS target
USING normalized_participation AS source
ON target.season = source.season
   AND target.game_id = source.game_id
   AND target.player_id = source.player_id
   AND target.source = source.source
WHEN MATCHED THEN UPDATE SET
    game_id = source.game_id,
    pfr_game_id = source.pfr_game_id,
    pfr_player_id = source.pfr_player_id,
    game_type = source.game_type,
    season_type = source.season_type,
    position = source.position,
    nfl_team = source.nfl_team,
    opponent = source.opponent,
    offense_snaps = source.offense_snaps,
    offense_snap_pct = source.offense_snap_pct,
    defense_snaps = source.defense_snaps,
    defense_snap_pct = source.defense_snap_pct,
    special_teams_snaps = source.special_teams_snaps,
    special_teams_snap_pct = source.special_teams_snap_pct,
    as_of = source.as_of,
    source_dataset_id = source.source_dataset_id
WHEN NOT MATCHED THEN INSERT (
    season, week, game_id, player_id, pfr_game_id, pfr_player_id, game_type,
    season_type, position, nfl_team, opponent, offense_snaps, offense_snap_pct,
    defense_snaps, defense_snap_pct, special_teams_snaps, special_teams_snap_pct,
    source, as_of, source_dataset_id
) VALUES (
    source.season, source.week, source.game_id, source.player_id,
    source.pfr_game_id, source.pfr_player_id, source.game_type,
    source.season_type, source.position, source.nfl_team, source.opponent,
    source.offense_snaps, source.offense_snap_pct, source.defense_snaps,
    source.defense_snap_pct, source.special_teams_snaps,
    source.special_teams_snap_pct, source.source, source.as_of,
    source.source_dataset_id
)
"""
