"""Validate and load immutable nflverse captures into canonical DuckDB tables."""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path

import duckdb

from fantasy_draft_ai.config import AppConfig
from fantasy_draft_ai.data.manifests import SourceManifest, sha256_file
from fantasy_draft_ai.data.warehouse import Warehouse
from fantasy_draft_ai.schemas.quality import QualityIssue, QualityReport, Severity

PLAYER_REQUIRED_COLUMNS = frozenset(
    {
        "gsis_id",
        "display_name",
        "pfr_id",
        "espn_id",
        "birth_date",
        "position",
        "latest_team",
        "status",
        "last_season",
        "years_of_experience",
        "rookie_season",
        "draft_year",
        "draft_round",
        "draft_pick",
        "draft_team",
        "height",
        "weight",
    }
)

WEEKLY_STATS_REQUIRED_COLUMNS = frozenset(
    {
        "player_id",
        "player_display_name",
        "position",
        "season",
        "week",
        "season_type",
        "game_id",
        "team",
        "opponent_team",
        "completions",
        "attempts",
        "passing_yards",
        "passing_tds",
        "passing_interceptions",
        "rushing_yards",
        "rushing_tds",
        "receiving_yards",
        "receptions",
        "receiving_tds",
        "targets",
        "carries",
        "passing_2pt_conversions",
        "rushing_2pt_conversions",
        "receiving_2pt_conversions",
        "fumbles_lost_total",
        "special_teams_tds",
        "fg_made",
        "fg_att",
        "pat_made",
        "pat_att",
    }
)


@dataclass(frozen=True)
class TableLoadSummary:
    """Row accounting for one canonical table."""

    source_rows: int
    normalized_rows: int
    excluded_rows: int
    inserted_rows: int
    matched_existing_rows: int
    final_table_rows: int


@dataclass(frozen=True)
class NflverseLoadResult:
    """Quality findings and committed warehouse row accounting."""

    manifest: SourceManifest
    manifest_path: Path
    quality: QualityReport
    players: TableLoadSummary
    weekly_stats: TableLoadSummary
    exact_mappings: int
    high_confidence_mappings: int
    committed: bool
    regular_season_rows: int = 0
    postseason_rows: int = 0

    def render(self) -> str:
        lines = [
            self.quality.render(),
            "",
            f"Manifest dataset: {self.manifest.dataset_id}",
            f"Manifest file: {self.manifest_path}",
            f"Warehouse transaction: {'COMMITTED' if self.committed else 'NOT COMMITTED'}",
            "Player mappings:",
            f"  exact: {self.exact_mappings}",
            f"  high (ID match with name conflict): {self.high_confidence_mappings}",
            f"  unresolved: {self.quality.unresolved_players}",
            "Weekly season types:",
            f"  regular season: {self.regular_season_rows}",
            f"  postseason: {self.postseason_rows}",
            "players row accounting:",
            _render_table_summary(self.players),
            "player_week_stats row accounting:",
            _render_table_summary(self.weekly_stats),
        ]
        return "\n".join(lines)


def _render_table_summary(summary: TableLoadSummary) -> str:
    return (
        f"  source={summary.source_rows}, normalized={summary.normalized_rows}, "
        f"excluded={summary.excluded_rows}, inserted={summary.inserted_rows}, "
        f"matched_existing={summary.matched_existing_rows}, "
        f"final_table={summary.final_table_rows}"
    )


def find_latest_nflverse_manifest(config: AppConfig) -> Path:
    """Return the newest valid nflverse manifest containing both required captures."""

    manifest_root = config.resolve(config.paths.manifests)
    candidates: list[tuple[SourceManifest, Path]] = []
    for path in manifest_root.glob("*.json") if manifest_root.exists() else ():
        try:
            payload = json.loads(path.read_text(encoding="utf-8"))
            manifest = SourceManifest.model_validate(payload)
        except (OSError, ValueError, json.JSONDecodeError):
            continue
        names = {Path(raw_file).name for raw_file in manifest.raw_files}
        has_players = any(name.startswith("nflverse_players__") for name in names)
        has_weekly = any(name.startswith("nflverse_player_stats__weekly__") for name in names)
        if manifest.source == "nflverse" and has_players and has_weekly:
            candidates.append((manifest, path))
    if not candidates:
        raise FileNotFoundError(
            "No nflverse manifest with player and weekly-stat captures was found. "
            "Run fantasy-draft data download-nflverse first."
        )
    return max(candidates, key=lambda item: item[0].acquired_at)[1]


def load_nflverse_to_warehouse(
    config: AppConfig, *, manifest_path: Path | None = None
) -> NflverseLoadResult:
    """Validate, normalize, and transactionally upsert one nflverse capture pair."""

    selected_manifest_path = (manifest_path or find_latest_nflverse_manifest(config)).resolve()
    manifest = SourceManifest.model_validate_json(
        selected_manifest_path.read_text(encoding="utf-8")
    )
    issues: list[QualityIssue] = []
    resolved_files = _resolve_and_verify_manifest_files(config, manifest, issues)
    player_path = _select_capture(resolved_files, "nflverse_players__", issues, "players")
    stats_path = _select_capture(
        resolved_files, "nflverse_player_stats__weekly__", issues, "weekly stats"
    )

    empty_summary = TableLoadSummary(0, 0, 0, 0, 0, 0)
    if (
        player_path is None
        or stats_path is None
        or any(issue.severity == Severity.FATAL for issue in issues)
    ):
        quality = QualityReport(source="nflverse", row_count=0, issues=issues)
        return NflverseLoadResult(
            manifest,
            selected_manifest_path,
            quality,
            empty_summary,
            empty_summary,
            0,
            0,
            False,
        )

    with duckdb.connect() as validation_connection:
        player_columns = _parquet_columns(validation_connection, player_path)
        stats_columns = _parquet_columns(validation_connection, stats_path)
        missing_player_columns = sorted(PLAYER_REQUIRED_COLUMNS - player_columns)
        missing_stats_columns = sorted(WEEKLY_STATS_REQUIRED_COLUMNS - stats_columns)
        if missing_player_columns:
            issues.append(
                QualityIssue(
                    code="missing_player_columns",
                    message=f"Missing player columns: {', '.join(missing_player_columns)}",
                    count=len(missing_player_columns),
                    severity=Severity.FATAL,
                )
            )
        if missing_stats_columns:
            issues.append(
                QualityIssue(
                    code="missing_weekly_stat_columns",
                    message=f"Missing weekly-stat columns: {', '.join(missing_stats_columns)}",
                    count=len(missing_stats_columns),
                    severity=Severity.FATAL,
                )
            )
        if missing_player_columns or missing_stats_columns:
            quality = QualityReport(source="nflverse", row_count=0, issues=issues)
            return NflverseLoadResult(
                manifest,
                selected_manifest_path,
                quality,
                empty_summary,
                empty_summary,
                0,
                0,
                False,
            )

        metrics = _collect_quality_metrics(validation_connection, player_path, stats_path)
        issues.extend(_quality_issues(metrics))
        observed_seasons = _observed_seasons(validation_connection, stats_path)
        expected_seasons = set(manifest.seasons)
        if not expected_seasons or observed_seasons != expected_seasons:
            issues.append(
                QualityIssue(
                    code="manifest_season_mismatch",
                    message=(
                        f"Manifest seasons {sorted(expected_seasons)} do not match "
                        f"weekly-stat seasons {sorted(observed_seasons)}."
                    ),
                    severity=Severity.FATAL,
                )
            )

    quality = QualityReport(
        source="nflverse",
        row_count=metrics["player_rows"] + metrics["stats_rows"],
        required_field_failures=(
            metrics["players_missing_id"]
            + metrics["players_missing_name"]
            + metrics["stats_missing_id"]
            + metrics["stats_missing_season_or_week"]
        ),
        duplicate_keys=metrics["duplicate_player_ids"] + metrics["duplicate_stat_keys"],
        unresolved_players=metrics["unmatched_player_ids"],
        excluded_rows=metrics["stats_missing_id"],
        identity_conflicts=metrics["identity_conflicts"],
        issues=issues,
    )
    players_normalized = metrics["player_rows"] - metrics["players_missing_id"]
    stats_normalized = metrics["stats_rows"] - metrics["stats_missing_id"]
    preflight_players = TableLoadSummary(
        metrics["player_rows"], players_normalized, metrics["players_missing_id"], 0, 0, 0
    )
    preflight_stats = TableLoadSummary(
        metrics["stats_rows"], stats_normalized, metrics["stats_missing_id"], 0, 0, 0
    )
    if quality.has_fatal_errors:
        return NflverseLoadResult(
            manifest,
            selected_manifest_path,
            quality,
            preflight_players,
            preflight_stats,
            max(players_normalized - metrics["identity_conflicts"], 0),
            metrics["identity_conflicts"],
            False,
        )

    warehouse = Warehouse(config.resolve(config.paths.warehouse))
    warehouse.initialize()
    players_summary, stats_summary = _commit_load(
        warehouse,
        manifest,
        player_path,
        stats_path,
        metrics,
        prediction_season=config.project.prediction_season,
    )
    return NflverseLoadResult(
        manifest,
        selected_manifest_path,
        quality,
        players_summary,
        stats_summary,
        players_normalized - metrics["identity_conflicts"],
        metrics["identity_conflicts"],
        True,
        regular_season_rows=metrics["regular_season_rows"],
        postseason_rows=metrics["postseason_rows"],
    )


def _resolve_and_verify_manifest_files(
    config: AppConfig, manifest: SourceManifest, issues: list[QualityIssue]
) -> list[Path]:
    if manifest.source != "nflverse":
        issues.append(
            QualityIssue(
                code="wrong_manifest_source",
                message=f"Expected nflverse manifest, received {manifest.source!r}.",
                severity=Severity.FATAL,
            )
        )
    if len(manifest.raw_files) != len(manifest.sha256):
        issues.append(
            QualityIssue(
                code="manifest_file_hash_mismatch",
                message="Manifest raw_files and sha256 lists have different lengths.",
                severity=Severity.FATAL,
            )
        )
        return []

    project_root = config.project_root.resolve()
    resolved: list[Path] = []
    for relative, expected_hash in zip(manifest.raw_files, manifest.sha256, strict=True):
        path = (project_root / relative).resolve()
        if not path.is_relative_to(project_root):
            issues.append(
                QualityIssue(
                    code="raw_path_outside_project",
                    message=f"Manifest path leaves the project root: {relative}",
                    severity=Severity.FATAL,
                )
            )
            continue
        if not path.is_file():
            issues.append(
                QualityIssue(
                    code="missing_raw_file",
                    message=f"Raw file is missing: {relative}",
                    severity=Severity.FATAL,
                )
            )
            continue
        if sha256_file(path) != expected_hash:
            issues.append(
                QualityIssue(
                    code="raw_hash_mismatch",
                    message=f"Raw file hash does not match its manifest: {relative}",
                    severity=Severity.FATAL,
                )
            )
            continue
        resolved.append(path)
    return resolved


def _select_capture(
    paths: list[Path], prefix: str, issues: list[QualityIssue], label: str
) -> Path | None:
    matches = [path for path in paths if path.name.startswith(prefix)]
    if len(matches) != 1:
        issues.append(
            QualityIssue(
                code="invalid_capture_count",
                message=f"Expected one {label} capture, found {len(matches)}.",
                count=len(matches),
                severity=Severity.FATAL,
            )
        )
        return None
    return matches[0]


def _parquet_columns(connection: duckdb.DuckDBPyConnection, path: Path) -> set[str]:
    rows = connection.execute("DESCRIBE SELECT * FROM read_parquet(?)", [str(path)]).fetchall()
    return {str(row[0]) for row in rows}


def _collect_quality_metrics(
    connection: duckdb.DuckDBPyConnection, player_path: Path, stats_path: Path
) -> dict[str, int]:
    player_file = str(player_path)
    stats_file = str(stats_path)
    metrics = {
        "player_rows": _scalar(connection, "SELECT count(*) FROM read_parquet(?)", [player_file]),
        "stats_rows": _scalar(connection, "SELECT count(*) FROM read_parquet(?)", [stats_file]),
        "regular_season_rows": _scalar(
            connection,
            "SELECT count(*) FROM read_parquet(?) WHERE player_id IS NOT NULL "
            "AND upper(season_type) = 'REG'",
            [stats_file],
        ),
        "postseason_rows": _scalar(
            connection,
            "SELECT count(*) FROM read_parquet(?) WHERE player_id IS NOT NULL "
            "AND upper(season_type) = 'POST'",
            [stats_file],
        ),
        "players_missing_id": _scalar(
            connection,
            "SELECT count(*) FROM read_parquet(?) WHERE gsis_id IS NULL OR trim(gsis_id) = ''",
            [player_file],
        ),
        "players_missing_name": _scalar(
            connection,
            "SELECT count(*) FROM read_parquet(?) "
            "WHERE display_name IS NULL OR trim(display_name) = ''",
            [player_file],
        ),
        "duplicate_player_ids": _scalar(
            connection,
            "SELECT coalesce(sum(n - 1), 0) FROM ("
            "SELECT gsis_id, count(*) AS n FROM read_parquet(?) "
            "WHERE gsis_id IS NOT NULL AND trim(gsis_id) <> '' "
            "GROUP BY gsis_id HAVING count(*) > 1)",
            [player_file],
        ),
        "stats_missing_id": _scalar(
            connection,
            "SELECT count(*) FROM read_parquet(?) WHERE player_id IS NULL OR trim(player_id) = ''",
            [stats_file],
        ),
        "missing_id_rows_with_stats": _scalar(
            connection,
            "SELECT count(*) FROM read_parquet(?) WHERE "
            "(player_id IS NULL OR trim(player_id) = '') AND ("
            "coalesce(completions, 0) <> 0 OR coalesce(attempts, 0) <> 0 OR "
            "coalesce(passing_yards, 0) <> 0 OR coalesce(passing_tds, 0) <> 0 OR "
            "coalesce(passing_interceptions, 0) <> 0 OR "
            "coalesce(rushing_yards, 0) <> 0 OR coalesce(rushing_tds, 0) <> 0 OR "
            "coalesce(receiving_yards, 0) <> 0 OR coalesce(receptions, 0) <> 0 OR "
            "coalesce(receiving_tds, 0) <> 0 OR coalesce(targets, 0) <> 0 OR "
            "coalesce(carries, 0) <> 0 OR "
            "coalesce(passing_2pt_conversions, 0) <> 0 OR "
            "coalesce(rushing_2pt_conversions, 0) <> 0 OR "
            "coalesce(receiving_2pt_conversions, 0) <> 0 OR "
            "coalesce(fumbles_lost_total, 0) <> 0 OR "
            "coalesce(special_teams_tds, 0) <> 0 OR coalesce(fg_made, 0) <> 0 OR "
            "coalesce(fg_att, 0) <> 0 OR coalesce(pat_made, 0) <> 0 OR "
            "coalesce(pat_att, 0) <> 0)",
            [stats_file],
        ),
        "stats_missing_season_or_week": _scalar(
            connection,
            "SELECT count(*) FROM read_parquet(?) WHERE player_id IS NOT NULL "
            "AND (season IS NULL OR week IS NULL)",
            [stats_file],
        ),
        "duplicate_stat_keys": _scalar(
            connection,
            "SELECT coalesce(sum(n - 1), 0) FROM ("
            "SELECT season, week, player_id, count(*) AS n FROM read_parquet(?) "
            "WHERE player_id IS NOT NULL GROUP BY season, week, player_id "
            "HAVING count(*) > 1)",
            [stats_file],
        ),
        "unmatched_player_ids": _scalar(
            connection,
            "SELECT count(DISTINCT s.player_id) FROM read_parquet(?) s "
            "LEFT JOIN read_parquet(?) p ON s.player_id = p.gsis_id "
            "WHERE s.player_id IS NOT NULL AND p.gsis_id IS NULL",
            [stats_file, player_file],
        ),
        "identity_conflicts": _scalar(
            connection,
            "SELECT count(DISTINCT s.player_id) FROM read_parquet(?) s "
            "JOIN read_parquet(?) p ON s.player_id = p.gsis_id "
            "WHERE regexp_replace(lower(s.player_display_name), '[^a-z0-9]', '', 'g') "
            "<> regexp_replace(lower(p.display_name), '[^a-z0-9]', '', 'g')",
            [stats_file, player_file],
        ),
        "missing_context_fields": _scalar(
            connection,
            "SELECT count(*) FROM read_parquet(?) WHERE player_id IS NOT NULL AND ("
            "team IS NULL OR trim(team) = '' OR opponent_team IS NULL "
            "OR trim(opponent_team) = '' OR position IS NULL OR trim(position) = '')",
            [stats_file],
        ),
        "invalid_birth_dates": _scalar(
            connection,
            "SELECT count(*) FROM read_parquet(?) WHERE birth_date IS NOT NULL "
            "AND try_cast(birth_date AS DATE) IS NULL",
            [player_file],
        ),
        "missing_birth_dates": _scalar(
            connection,
            "SELECT count(*) FROM read_parquet(?) WHERE birth_date IS NULL",
            [player_file],
        ),
        "duplicate_display_name_rows": _scalar(
            connection,
            "SELECT coalesce(sum(n), 0) FROM ("
            "SELECT regexp_replace(lower(display_name), '[^a-z0-9]', '', 'g') AS name_key, "
            "count(*) AS n FROM read_parquet(?) GROUP BY name_key HAVING count(*) > 1)",
            [player_file],
        ),
    }
    return metrics


def _scalar(connection: duckdb.DuckDBPyConnection, query: str, parameters: list[str]) -> int:
    row = connection.execute(query, parameters).fetchone()
    if row is None:
        raise RuntimeError("DuckDB quality query returned no row.")
    return int(row[0])


def _quality_issues(metrics: dict[str, int]) -> list[QualityIssue]:
    issues: list[QualityIssue] = []

    def add(code: str, message: str, metric: str, severity: Severity) -> None:
        count = metrics[metric]
        if count:
            issues.append(QualityIssue(code=code, message=message, count=count, severity=severity))

    add(
        "missing_player_ids",
        "Player identity rows are missing GSIS IDs.",
        "players_missing_id",
        Severity.FATAL,
    )
    add(
        "missing_player_names",
        "Player identity rows are missing display names.",
        "players_missing_name",
        Severity.FATAL,
    )
    add(
        "duplicate_player_ids",
        "Player identity rows contain duplicate GSIS IDs.",
        "duplicate_player_ids",
        Severity.FATAL,
    )
    add(
        "excluded_missing_player_id",
        "Weekly zero-stat placeholder rows lack a player ID and will be excluded.",
        "stats_missing_id",
        Severity.WARNING,
    )
    add(
        "missing_id_with_stats",
        "Weekly rows without player IDs contain non-zero mapped statistics.",
        "missing_id_rows_with_stats",
        Severity.FATAL,
    )
    add(
        "missing_stat_keys",
        "Weekly player rows are missing season or week keys.",
        "stats_missing_season_or_week",
        Severity.FATAL,
    )
    add(
        "duplicate_weekly_keys",
        "Weekly rows duplicate the canonical season/week/player key.",
        "duplicate_stat_keys",
        Severity.FATAL,
    )
    add(
        "unmatched_player_ids",
        "Weekly rows contain non-null player IDs absent from the player capture.",
        "unmatched_player_ids",
        Severity.FATAL,
    )
    add(
        "duplicate_display_names",
        "Multiple GSIS IDs share a normalized display name; IDs remain separate and "
        "names are not used as join keys.",
        "duplicate_display_name_rows",
        Severity.WARNING,
    )
    add(
        "identity_name_conflicts",
        "GSIS IDs match, but weekly and player-capture display names disagree; "
        "mapping confidence is reduced to high.",
        "identity_conflicts",
        Severity.WARNING,
    )
    add(
        "missing_weekly_context",
        "Weekly rows are missing team, opponent, or position context.",
        "missing_context_fields",
        Severity.WARNING,
    )
    add(
        "missing_birth_dates",
        "Player birth dates are unavailable and will remain null.",
        "missing_birth_dates",
        Severity.WARNING,
    )
    add(
        "invalid_birth_dates",
        "Player birth dates could not be parsed and will be stored as null.",
        "invalid_birth_dates",
        Severity.WARNING,
    )
    return issues


def _observed_seasons(connection: duckdb.DuckDBPyConnection, stats_path: Path) -> set[int]:
    rows = connection.execute(
        "SELECT DISTINCT season FROM read_parquet(?) WHERE season IS NOT NULL",
        [str(stats_path)],
    ).fetchall()
    return {int(row[0]) for row in rows}


def _commit_load(
    warehouse: Warehouse,
    manifest: SourceManifest,
    player_path: Path,
    stats_path: Path,
    metrics: dict[str, int],
    *,
    prediction_season: int,
) -> tuple[TableLoadSummary, TableLoadSummary]:
    with warehouse.connect() as connection:
        try:
            connection.execute("BEGIN TRANSACTION")
            _create_normalized_tables(
                connection,
                manifest,
                player_path,
                stats_path,
                prediction_season=prediction_season,
            )
            players_existing = _scalar(
                connection,
                "SELECT count(*) FROM normalized_players s JOIN players t USING (player_id)",
                [],
            )
            stats_existing = _scalar(
                connection,
                "SELECT count(*) FROM normalized_weekly_stats s JOIN player_week_stats t "
                "ON s.season = t.season AND s.week = t.week "
                "AND s.player_id = t.player_id AND s.source = t.source",
                [],
            )
            connection.execute(PLAYER_MERGE_SQL)
            connection.execute(APPLY_REVIEWED_NFLVERSE_IDENTITIES_SQL)
            connection.execute(WEEKLY_STATS_MERGE_SQL)
            loaded_stats = _scalar(
                connection,
                "SELECT count(*) FROM player_week_stats "
                "WHERE source = 'nflverse' AND source_dataset_id = ?",
                [manifest.dataset_id],
            )
            if loaded_stats != metrics["stats_rows"] - metrics["stats_missing_id"]:
                raise RuntimeError(
                    "Post-load weekly-stat row count does not match the normalized capture."
                )
            orphan_count = _scalar(
                connection,
                "SELECT count(*) FROM player_week_stats s "
                "LEFT JOIN players p ON s.player_id = p.player_id "
                "WHERE s.source = 'nflverse' AND p.player_id IS NULL",
                [],
            )
            if orphan_count:
                raise RuntimeError(f"Post-load validation found {orphan_count} orphan rows.")
            players_after = _table_count(connection, "players")
            stats_after = _table_count(connection, "player_week_stats")
            connection.execute("COMMIT")
        except Exception:
            connection.execute("ROLLBACK")
            raise

    players_normalized = metrics["player_rows"] - metrics["players_missing_id"]
    stats_normalized = metrics["stats_rows"] - metrics["stats_missing_id"]
    players_inserted = players_normalized - players_existing
    stats_inserted = stats_normalized - stats_existing
    return (
        TableLoadSummary(
            metrics["player_rows"],
            players_normalized,
            metrics["players_missing_id"],
            players_inserted,
            players_existing,
            players_after,
        ),
        TableLoadSummary(
            metrics["stats_rows"],
            stats_normalized,
            metrics["stats_missing_id"],
            stats_inserted,
            stats_existing,
            stats_after,
        ),
    )


def _table_count(connection: duckdb.DuckDBPyConnection, table: str) -> int:
    row = connection.execute(f"SELECT count(*) FROM {table}").fetchone()
    if row is None:
        raise RuntimeError(f"DuckDB returned no count for {table}.")
    return int(row[0])


def _create_normalized_tables(
    connection: duckdb.DuckDBPyConnection,
    manifest: SourceManifest,
    player_path: Path,
    stats_path: Path,
    *,
    prediction_season: int,
) -> None:
    connection.execute(
        NORMALIZE_PLAYERS_SQL,
        [
            str(stats_path),
            str(player_path),
            prediction_season,
            manifest.dataset_id,
            manifest.dataset_id,
            manifest.dataset_id,
            manifest.acquired_at,
            str(player_path),
        ],
    )
    connection.execute(
        NORMALIZE_WEEKLY_STATS_SQL,
        [manifest.acquired_at, manifest.dataset_id, str(stats_path)],
    )


NORMALIZE_PLAYERS_SQL = """
CREATE OR REPLACE TEMP TABLE normalized_players AS
WITH conflict_ids AS (
    SELECT DISTINCT s.player_id
    FROM read_parquet(?) s
    JOIN read_parquet(?) p ON s.player_id = p.gsis_id
    WHERE regexp_replace(lower(s.player_display_name), '[^a-z0-9]', '', 'g')
          <> regexp_replace(lower(p.display_name), '[^a-z0-9]', '', 'g')
)
SELECT
    p.gsis_id AS player_id,
    p.gsis_id,
    nullif(trim(p.pfr_id), '') AS pfr_id,
    nullif(trim(p.espn_id), '') AS espn_id,
    NULL::VARCHAR AS sleeper_id,
    NULL::VARCHAR AS yahoo_id,
    NULL::VARCHAR AS mfl_id,
    NULL::VARCHAR AS fleaflicker_id,
    NULL::VARCHAR AS fantasypros_id,
    trim(p.display_name) AS display_name,
    upper(nullif(trim(p.position), '')) AS canonical_position,
    upper(nullif(trim(p.latest_team), '')) AS nfl_team,
    try_cast(p.birth_date AS DATE) AS birth_date,
    NULL::DOUBLE AS age,
    p.years_of_experience AS experience,
    p.rookie_season,
    p.draft_year,
    p.draft_round,
    p.draft_pick,
    upper(nullif(trim(p.draft_team), '')) AS draft_team,
    p.height AS height_inches,
    p.weight AS weight_lbs,
    CASE
        WHEN p.last_season < ? THEN FALSE
        WHEN p.status = 'ACT' THEN TRUE
        WHEN p.status IN ('CUT', 'RET', 'RLS') THEN FALSE
        ELSE NULL
    END AS is_active,
    CASE WHEN c.player_id IS NULL THEN 'exact' ELSE 'high' END AS mapping_confidence,
    CASE
        WHEN c.player_id IS NULL THEN 'nflverse:gsis_id:' || ?
        ELSE 'nflverse:gsis_id_with_name_conflict:' || ?
    END AS mapping_source,
    ?::VARCHAR AS identity_source_dataset_id,
    ?::TIMESTAMPTZ AS identity_source_as_of
FROM read_parquet(?) p
LEFT JOIN conflict_ids c ON p.gsis_id = c.player_id
WHERE p.gsis_id IS NOT NULL AND trim(p.gsis_id) <> ''
"""

NORMALIZE_WEEKLY_STATS_SQL = """
CREATE OR REPLACE TEMP TABLE normalized_weekly_stats AS
SELECT
    season,
    week,
    player_id,
    upper(nullif(trim(position), '')) AS position,
    upper(nullif(trim(season_type), '')) AS season_type,
    nullif(trim(game_id), '') AS game_id,
    upper(nullif(trim(team), '')) AS nfl_team,
    upper(nullif(trim(opponent_team), '')) AS opponent,
    completions::DOUBLE AS completions,
    attempts::DOUBLE AS passing_attempts,
    passing_yards::DOUBLE AS passing_yards,
    passing_tds::DOUBLE AS passing_tds,
    passing_interceptions::DOUBLE AS interceptions,
    rushing_yards::DOUBLE AS rushing_yards,
    rushing_tds::DOUBLE AS rushing_tds,
    receiving_yards::DOUBLE AS receiving_yards,
    receptions::DOUBLE AS receptions,
    receiving_tds::DOUBLE AS receiving_tds,
    targets::DOUBLE AS targets,
    carries::DOUBLE AS carries,
    (
        coalesce(passing_2pt_conversions, 0)
        + coalesce(rushing_2pt_conversions, 0)
        + coalesce(receiving_2pt_conversions, 0)
    )::DOUBLE AS two_point_conversions,
    fumbles_lost_total::DOUBLE AS fumbles_lost,
    special_teams_tds::DOUBLE AS special_teams_tds,
    fg_made::DOUBLE AS field_goals_made,
    fg_att::DOUBLE AS field_goals_attempted,
    pat_made::DOUBLE AS extra_points_made,
    pat_att::DOUBLE AS extra_points_attempted,
    NULL::DOUBLE AS games_active,
    NULL::DOUBLE AS games_played,
    'nflverse'::VARCHAR AS source,
    ?::TIMESTAMPTZ AS as_of,
    ?::VARCHAR AS source_dataset_id
FROM read_parquet(?)
WHERE player_id IS NOT NULL AND trim(player_id) <> ''
"""

PLAYER_MERGE_SQL = """
MERGE INTO players AS target
USING normalized_players AS source
ON target.player_id = source.player_id
WHEN MATCHED THEN UPDATE SET
    gsis_id = source.gsis_id,
    pfr_id = coalesce(target.pfr_id, source.pfr_id),
    espn_id = coalesce(target.espn_id, source.espn_id),
    sleeper_id = coalesce(target.sleeper_id, source.sleeper_id),
    yahoo_id = coalesce(target.yahoo_id, source.yahoo_id),
    mfl_id = coalesce(target.mfl_id, source.mfl_id),
    fleaflicker_id = coalesce(target.fleaflicker_id, source.fleaflicker_id),
    fantasypros_id = coalesce(target.fantasypros_id, source.fantasypros_id),
    display_name = source.display_name,
    canonical_position = source.canonical_position,
    nfl_team = source.nfl_team,
    birth_date = source.birth_date,
    age = source.age,
    experience = source.experience,
    rookie_season = source.rookie_season,
    draft_year = source.draft_year,
    draft_round = source.draft_round,
    draft_pick = source.draft_pick,
    draft_team = source.draft_team,
    height_inches = source.height_inches,
    weight_lbs = source.weight_lbs,
    is_active = source.is_active,
    mapping_confidence = CASE
        WHEN target.mapping_source NOT LIKE 'nflverse:%' THEN target.mapping_confidence
        ELSE source.mapping_confidence
    END,
    mapping_source = CASE
        WHEN target.mapping_source NOT LIKE 'nflverse:%' THEN target.mapping_source
        ELSE source.mapping_source
    END,
    identity_source_dataset_id = source.identity_source_dataset_id,
    identity_source_as_of = source.identity_source_as_of
WHEN NOT MATCHED THEN INSERT (
    player_id, gsis_id, pfr_id, espn_id, sleeper_id, yahoo_id, mfl_id, fleaflicker_id,
    fantasypros_id, display_name, canonical_position, nfl_team, birth_date, age,
    experience, rookie_season, draft_year, draft_round, draft_pick, draft_team,
    height_inches, weight_lbs, is_active, mapping_confidence, mapping_source,
    identity_source_dataset_id, identity_source_as_of
) VALUES (
    source.player_id, source.gsis_id, source.pfr_id, source.espn_id, source.sleeper_id,
    source.yahoo_id, source.mfl_id, source.fleaflicker_id, source.fantasypros_id,
    source.display_name, source.canonical_position, source.nfl_team,
    source.birth_date, source.age, source.experience, source.rookie_season,
    source.draft_year, source.draft_round, source.draft_pick, source.draft_team,
    source.height_inches, source.weight_lbs, source.is_active,
    source.mapping_confidence, source.mapping_source, source.identity_source_dataset_id,
    source.identity_source_as_of
)
"""

APPLY_REVIEWED_NFLVERSE_IDENTITIES_SQL = """
UPDATE players AS player SET
    display_name = coalesce(review.canonical_display_name_override, player.display_name),
    mapping_confidence = 'reviewed',
    mapping_source = 'manual:identity-review:' || review.resolution_dataset_id
FROM (
    SELECT * EXCLUDE (review_order)
    FROM (
        SELECT
            queue.*,
            row_number() OVER (
                PARTITION BY queue.resolved_player_id
                ORDER BY queue.resolved_at DESC, queue.review_id DESC
            ) AS review_order
        FROM identity_review_queue AS queue
        WHERE queue.source = 'nflverse'
          AND queue.status = 'resolved'
          AND queue.resolved_player_id IS NOT NULL
          AND queue.resolution_dataset_id IS NOT NULL
    )
    WHERE review_order = 1
) AS review
WHERE player.player_id = review.resolved_player_id
"""

WEEKLY_STATS_MERGE_SQL = """
MERGE INTO player_week_stats AS target
USING normalized_weekly_stats AS source
ON target.season = source.season
   AND target.week = source.week
   AND target.player_id = source.player_id
   AND target.source = source.source
WHEN MATCHED THEN UPDATE SET
    position = source.position,
    season_type = source.season_type,
    game_id = source.game_id,
    nfl_team = source.nfl_team,
    opponent = source.opponent,
    completions = source.completions,
    passing_attempts = source.passing_attempts,
    passing_yards = source.passing_yards,
    passing_tds = source.passing_tds,
    interceptions = source.interceptions,
    rushing_yards = source.rushing_yards,
    rushing_tds = source.rushing_tds,
    receiving_yards = source.receiving_yards,
    receptions = source.receptions,
    receiving_tds = source.receiving_tds,
    targets = source.targets,
    carries = source.carries,
    two_point_conversions = source.two_point_conversions,
    fumbles_lost = source.fumbles_lost,
    special_teams_tds = source.special_teams_tds,
    field_goals_made = source.field_goals_made,
    field_goals_attempted = source.field_goals_attempted,
    extra_points_made = source.extra_points_made,
    extra_points_attempted = source.extra_points_attempted,
    games_active = source.games_active,
    games_played = source.games_played,
    as_of = source.as_of,
    source_dataset_id = source.source_dataset_id
WHEN NOT MATCHED THEN INSERT (
    season, week, player_id, position, season_type, game_id, nfl_team, opponent,
    completions, passing_attempts, passing_yards, passing_tds, interceptions,
    rushing_yards, rushing_tds, receiving_yards, receptions, receiving_tds,
    targets, carries, two_point_conversions, fumbles_lost, special_teams_tds,
    field_goals_made, field_goals_attempted, extra_points_made,
    extra_points_attempted, games_active, games_played, source, as_of,
    source_dataset_id
) VALUES (
    source.season, source.week, source.player_id, source.position, source.season_type,
    source.game_id, source.nfl_team, source.opponent, source.completions,
    source.passing_attempts, source.passing_yards, source.passing_tds,
    source.interceptions, source.rushing_yards, source.rushing_tds,
    source.receiving_yards, source.receptions, source.receiving_tds,
    source.targets, source.carries, source.two_point_conversions,
    source.fumbles_lost, source.special_teams_tds, source.field_goals_made,
    source.field_goals_attempted, source.extra_points_made,
    source.extra_points_attempted, source.games_active, source.games_played,
    source.source, source.as_of, source.source_dataset_id
)
"""
