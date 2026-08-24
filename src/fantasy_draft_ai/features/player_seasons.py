"""Build cutoff-safe player-season features and separately persisted targets."""

from __future__ import annotations

import hashlib
import json
import math
from collections import defaultdict
from collections.abc import Sequence
from dataclasses import asdict, dataclass
from datetime import UTC, date, datetime
from pathlib import Path
from typing import Any

import duckdb

from fantasy_draft_ai.config import AppConfig
from fantasy_draft_ai.data.warehouse import Warehouse, invalidate_player_projection_runs
from fantasy_draft_ai.rules.models import LeagueRules
from fantasy_draft_ai.schemas.quality import QualityIssue, Severity
from fantasy_draft_ai.scoring.engine import PlayerStatLine, score_player

FEATURE_VERSION = "phase3-v2"
CORE_POSITIONS = frozenset({"QB", "RB", "WR", "TE"})
HISTORY_WEIGHTS = (0.60, 0.30, 0.10)
POSITION_PRIOR_STRENGTH_GAMES = 8.0
CANDIDATE_HISTORY_SEASONS = 4
PRESEASON_CUTOFF_MONTH = 9
PRESEASON_CUTOFF_DAY = 1


@dataclass(frozen=True)
class FeatureQualityReport:
    """Deterministic row accounting and leakage checks for one feature build."""

    input_weekly_rows: int
    regular_weekly_rows: int
    postseason_weekly_rows: int
    unknown_season_type_rows: int
    input_participation_rows: int
    regular_participation_rows: int
    postseason_participation_rows: int
    feature_rows: int
    target_rows: int
    target_rows_missing_games_active: int
    live_rows_without_targets: int
    rookie_rows: int
    sparse_history_rows: int
    cutoff_safe_static_position_rows: int
    candidates_missing_cutoff_safe_position: int
    missing_age_rows: int
    missing_draft_capital_rows: int
    participation_coverage_failures: int
    target_scorers_without_features: int
    target_active_players_without_features: int
    source_dataset_ids: tuple[str, ...]
    issues: tuple[QualityIssue, ...] = ()

    @property
    def has_fatal_errors(self) -> bool:
        return any(issue.severity == Severity.FATAL for issue in self.issues)

    def render(self) -> str:
        status = "FAILED" if self.has_fatal_errors else "PASSED"
        lines = [
            f"Player-season feature quality: {status}",
            f"Weekly rows: {self.input_weekly_rows}",
            f"  regular used: {self.regular_weekly_rows}",
            f"  postseason excluded: {self.postseason_weekly_rows}",
            f"  unknown season type excluded: {self.unknown_season_type_rows}",
            f"Participation rows: {self.input_participation_rows}",
            f"  regular used: {self.regular_participation_rows}",
            f"  postseason excluded: {self.postseason_participation_rows}",
            f"Feature rows: {self.feature_rows}",
            f"Target rows: {self.target_rows}",
            f"Targets missing games active: {self.target_rows_missing_games_active}",
            f"Live rows without targets: {self.live_rows_without_targets}",
            f"Rookie fallback rows: {self.rookie_rows}",
            f"Sparse-history rows: {self.sparse_history_rows}",
            (
                "Rows using a cutoff-safe identity-snapshot position: "
                f"{self.cutoff_safe_static_position_rows}"
            ),
            (
                "Current-core candidates excluded without cutoff-safe position evidence: "
                f"{self.candidates_missing_cutoff_safe_position}"
            ),
            f"Missing age rows: {self.missing_age_rows}",
            f"Missing draft-capital rows: {self.missing_draft_capital_rows}",
            f"Participation coverage failures: {self.participation_coverage_failures}",
            f"Target scorers without feature rows: {self.target_scorers_without_features}",
            (
                "Active target players without feature rows: "
                f"{self.target_active_players_without_features}"
            ),
            f"Source datasets: {len(self.source_dataset_ids)}",
        ]
        lines.extend(
            f"- {issue.severity.value.upper()} {issue.code}: {issue.message} ({issue.count})"
            for issue in self.issues
        )
        return "\n".join(lines)


@dataclass(frozen=True)
class FeatureBuildResult:
    """Committed feature set plus reproducibility metadata."""

    quality: FeatureQualityReport
    feature_rows: int
    target_rows: int
    data_fingerprint: str
    target_fingerprint: str
    build_fingerprint: str
    scoring_ruleset_fingerprint: str
    report_path: Path | None
    committed: bool

    def render(self) -> str:
        lines = [
            self.quality.render(),
            "",
            f"Warehouse transaction: {'COMMITTED' if self.committed else 'NOT COMMITTED'}",
            f"Feature version: {FEATURE_VERSION}",
            f"Feature rows: {self.feature_rows}",
            f"Target rows: {self.target_rows}",
            f"Data fingerprint: {self.data_fingerprint or '<not built>'}",
            f"Target fingerprint: {self.target_fingerprint or '<not built>'}",
            f"Build fingerprint: {self.build_fingerprint or '<not built>'}",
            f"Scoring ruleset: {self.scoring_ruleset_fingerprint}",
        ]
        if self.report_path is not None:
            lines.append(f"Quality report: {self.report_path}")
        return "\n".join(lines)


@dataclass(frozen=True)
class StaticPlayer:
    player_id: str
    pfr_id: str | None
    position: str | None
    birth_date: date | None
    rookie_season: int | None
    draft_year: int | None
    draft_round: int | None
    draft_pick: int | None
    draft_team: str | None
    height_inches: int | None
    weight_lbs: int | None
    identity_source_dataset_id: str | None
    identity_source_as_of: datetime | None


@dataclass
class SeasonRecord:
    player_id: str
    season: int
    position: str | None = None
    nfl_team: str | None = None
    stat_games: int = 0
    games_active: int | None = None
    fantasy_points_total: float = 0.0
    completions: float = 0.0
    passing_attempts: float = 0.0
    passing_yards: float = 0.0
    passing_tds: float = 0.0
    interceptions: float = 0.0
    carries: float = 0.0
    rushing_yards: float = 0.0
    rushing_tds: float = 0.0
    targets: float = 0.0
    receptions: float = 0.0
    receiving_yards: float = 0.0
    receiving_tds: float = 0.0
    two_point_conversions: float = 0.0
    fumbles_lost: float = 0.0
    yardage_bonus_points: float = 0.0
    missing_participation_games: int = 0
    source_dataset_ids: set[str] | None = None
    source_max_as_of: datetime | None = None

    def __post_init__(self) -> None:
        if self.source_dataset_ids is None:
            self.source_dataset_ids = set()


@dataclass(frozen=True)
class FeatureRow:
    player_id: str
    feature_season: int
    prediction_season: int
    cutoff_date: date
    position: str
    feature_payload: str
    source: str
    source_dataset_ids: str
    source_max_stat_season: int | None
    source_max_as_of: datetime


@dataclass(frozen=True)
class TargetRow:
    player_id: str
    prediction_season: int
    position: str
    target_payload: str
    source: str
    source_dataset_ids: str
    source_max_as_of: datetime


def build_player_season_features(
    config: AppConfig,
    rules: LeagueRules,
    prediction_season: int | None = None,
    output_dir: Path | None = None,
) -> FeatureBuildResult:
    """Build all historical and live feature rows, then atomically replace the active set.

    Features for prediction season ``t`` use regular-season information through
    ``t-1`` only. Targets are constructed in a separate pass and table.
    """

    final_prediction_season = prediction_season or config.project.prediction_season
    scoring_fingerprint = rules.fingerprint()
    warehouse = Warehouse(config.resolve(config.paths.warehouse))
    empty_quality = _empty_quality()
    if not warehouse.path.exists():
        quality = _with_issue(
            empty_quality,
            QualityIssue(
                code="warehouse_missing",
                message="Initialize and load the canonical warehouse before building features.",
                severity=Severity.FATAL,
            ),
        )
        return FeatureBuildResult(
            quality,
            0,
            0,
            "",
            "",
            "",
            scoring_fingerprint,
            None,
            False,
        )

    warehouse.initialize()
    try:
        with warehouse.connect(read_only=True) as connection:
            counts = _source_counts(connection)
            schema_issues = _validate_input_schema(connection)
            if any(issue.severity == Severity.FATAL for issue in schema_issues):
                quality = _quality_from_counts(counts, issues=tuple(schema_issues))
                return FeatureBuildResult(
                    quality,
                    0,
                    0,
                    "",
                    "",
                    "",
                    scoring_fingerprint,
                    None,
                    False,
                )
            static_players = _read_static_players(connection)
            records, season_lineage = _read_season_records(connection, rules)
    except duckdb.Error as exc:
        quality = _with_issue(
            empty_quality,
            QualityIssue(
                code="warehouse_read_failed",
                message=str(exc),
                severity=Severity.FATAL,
            ),
        )
        return FeatureBuildResult(
            quality,
            0,
            0,
            "",
            "",
            "",
            scoring_fingerprint,
            None,
            False,
        )

    feature_rows, target_rows, build_metrics = _construct_rows(
        records=records,
        static_players=static_players,
        season_lineage=season_lineage,
        start_season=config.training.start_season,
        last_completed_season=config.training.end_season,
        final_prediction_season=final_prediction_season,
        rules=rules,
    )
    issues = list(schema_issues)
    issues.extend(_validate_built_rows(feature_rows, target_rows, build_metrics))
    quality = _quality_from_counts(
        counts,
        feature_rows=len(feature_rows),
        target_rows=len(target_rows),
        target_rows_missing_games_active=build_metrics["target_rows_missing_games_active"],
        live_rows_without_targets=build_metrics["live_rows_without_targets"],
        rookie_rows=build_metrics["rookie_rows"],
        sparse_history_rows=build_metrics["sparse_history_rows"],
        cutoff_safe_static_position_rows=build_metrics["cutoff_safe_static_position_rows"],
        candidates_missing_cutoff_safe_position=build_metrics[
            "candidates_missing_cutoff_safe_position"
        ],
        missing_age_rows=build_metrics["missing_age_rows"],
        missing_draft_capital_rows=build_metrics["missing_draft_capital_rows"],
        participation_coverage_failures=build_metrics["participation_coverage_failures"],
        target_scorers_without_features=build_metrics["target_scorers_without_features"],
        target_active_players_without_features=build_metrics[
            "target_active_players_without_features"
        ],
        source_dataset_ids=tuple(sorted(build_metrics["source_dataset_ids"])),
        issues=tuple(issues),
    )
    if quality.has_fatal_errors:
        return FeatureBuildResult(
            quality,
            0,
            0,
            "",
            "",
            "",
            scoring_fingerprint,
            None,
            False,
        )

    data_fingerprint = _feature_fingerprint(feature_rows, scoring_fingerprint)
    target_fingerprint = _target_fingerprint(target_rows, scoring_fingerprint)
    build_fingerprint = _build_fingerprint(
        data_fingerprint, target_fingerprint, scoring_fingerprint
    )
    _commit_feature_rows(
        warehouse,
        feature_rows,
        target_rows,
        data_fingerprint,
        target_fingerprint,
        build_fingerprint,
        scoring_fingerprint,
        quality,
    )
    report_path = _write_quality_report(
        config,
        output_dir,
        quality,
        data_fingerprint,
        target_fingerprint,
        build_fingerprint,
        scoring_fingerprint,
    )
    return FeatureBuildResult(
        quality,
        len(feature_rows),
        len(target_rows),
        data_fingerprint,
        target_fingerprint,
        build_fingerprint,
        scoring_fingerprint,
        report_path,
        True,
    )


def _empty_quality() -> FeatureQualityReport:
    return FeatureQualityReport(
        input_weekly_rows=0,
        regular_weekly_rows=0,
        postseason_weekly_rows=0,
        unknown_season_type_rows=0,
        input_participation_rows=0,
        regular_participation_rows=0,
        postseason_participation_rows=0,
        feature_rows=0,
        target_rows=0,
        target_rows_missing_games_active=0,
        live_rows_without_targets=0,
        rookie_rows=0,
        sparse_history_rows=0,
        cutoff_safe_static_position_rows=0,
        candidates_missing_cutoff_safe_position=0,
        missing_age_rows=0,
        missing_draft_capital_rows=0,
        participation_coverage_failures=0,
        target_scorers_without_features=0,
        target_active_players_without_features=0,
        source_dataset_ids=(),
    )


def _with_issue(quality: FeatureQualityReport, issue: QualityIssue) -> FeatureQualityReport:
    payload = asdict(quality)
    payload["issues"] = (*quality.issues, issue)
    return FeatureQualityReport(**payload)


def _source_counts(connection: duckdb.DuckDBPyConnection) -> dict[str, int]:
    weekly = connection.execute(
        """
        SELECT
            count(*),
            count(*) FILTER (WHERE season_type = 'REG'),
            count(*) FILTER (WHERE season_type = 'POST'),
            count(*) FILTER (WHERE season_type NOT IN ('REG', 'POST') OR season_type IS NULL)
        FROM player_week_stats
        WHERE source = 'nflverse'
        """
    ).fetchone()
    participation_exists = connection.execute(
        "SELECT count(*) FROM information_schema.tables "
        "WHERE table_name = 'player_game_participation'"
    ).fetchone()
    participation = (0, 0, 0)
    if participation_exists is not None and int(participation_exists[0]):
        row = connection.execute(
            """
            SELECT
                count(*),
                count(*) FILTER (WHERE season_type = 'REG'),
                count(*) FILTER (WHERE season_type = 'POST')
            FROM player_game_participation
            WHERE source = 'nflverse_pfr_snap_counts'
            """
        ).fetchone()
        if row is not None:
            participation = (int(row[0]), int(row[1]), int(row[2]))
    if weekly is None:
        weekly = (0, 0, 0, 0)
    return {
        "input_weekly_rows": int(weekly[0]),
        "regular_weekly_rows": int(weekly[1]),
        "postseason_weekly_rows": int(weekly[2]),
        "unknown_season_type_rows": int(weekly[3]),
        "input_participation_rows": participation[0],
        "regular_participation_rows": participation[1],
        "postseason_participation_rows": participation[2],
    }


def _quality_from_counts(
    counts: dict[str, int],
    *,
    feature_rows: int = 0,
    target_rows: int = 0,
    target_rows_missing_games_active: int = 0,
    live_rows_without_targets: int = 0,
    rookie_rows: int = 0,
    sparse_history_rows: int = 0,
    cutoff_safe_static_position_rows: int = 0,
    candidates_missing_cutoff_safe_position: int = 0,
    missing_age_rows: int = 0,
    missing_draft_capital_rows: int = 0,
    participation_coverage_failures: int = 0,
    target_scorers_without_features: int = 0,
    target_active_players_without_features: int = 0,
    source_dataset_ids: tuple[str, ...] = (),
    issues: tuple[QualityIssue, ...] = (),
) -> FeatureQualityReport:
    return FeatureQualityReport(
        input_weekly_rows=counts["input_weekly_rows"],
        regular_weekly_rows=counts["regular_weekly_rows"],
        postseason_weekly_rows=counts["postseason_weekly_rows"],
        unknown_season_type_rows=counts["unknown_season_type_rows"],
        input_participation_rows=counts["input_participation_rows"],
        regular_participation_rows=counts["regular_participation_rows"],
        postseason_participation_rows=counts["postseason_participation_rows"],
        feature_rows=feature_rows,
        target_rows=target_rows,
        target_rows_missing_games_active=target_rows_missing_games_active,
        live_rows_without_targets=live_rows_without_targets,
        rookie_rows=rookie_rows,
        sparse_history_rows=sparse_history_rows,
        cutoff_safe_static_position_rows=cutoff_safe_static_position_rows,
        candidates_missing_cutoff_safe_position=candidates_missing_cutoff_safe_position,
        missing_age_rows=missing_age_rows,
        missing_draft_capital_rows=missing_draft_capital_rows,
        participation_coverage_failures=participation_coverage_failures,
        target_scorers_without_features=target_scorers_without_features,
        target_active_players_without_features=target_active_players_without_features,
        source_dataset_ids=source_dataset_ids,
        issues=issues,
    )


def _validate_input_schema(connection: duckdb.DuckDBPyConnection) -> list[QualityIssue]:
    issues: list[QualityIssue] = []
    required_tables = {"players", "player_week_stats", "player_game_participation"}
    present = {
        str(row[0])
        for row in connection.execute(
            "SELECT table_name FROM information_schema.tables WHERE table_schema = 'main'"
        ).fetchall()
    }
    missing = required_tables - present
    if missing:
        issues.append(
            QualityIssue(
                code="missing_canonical_tables",
                message=f"Missing canonical tables: {', '.join(sorted(missing))}.",
                count=len(missing),
                severity=Severity.FATAL,
            )
        )
        return issues
    weekly_columns = {
        str(row[1])
        for row in connection.execute("PRAGMA table_info('player_week_stats')").fetchall()
    }
    player_columns = {
        str(row[1]) for row in connection.execute("PRAGMA table_info('players')").fetchall()
    }
    required_weekly = {"position", "source_dataset_id", "as_of", "season_type"}
    required_players = {
        "pfr_id",
        "birth_date",
        "rookie_season",
        "draft_year",
        "draft_round",
        "draft_pick",
        "draft_team",
        "height_inches",
        "weight_lbs",
        "identity_source_dataset_id",
        "identity_source_as_of",
    }
    missing_columns = sorted(
        {f"player_week_stats.{column}" for column in required_weekly - weekly_columns}
        | {f"players.{column}" for column in required_players - player_columns}
    )
    if missing_columns:
        issues.append(
            QualityIssue(
                code="missing_feature_source_columns",
                message=f"Missing source columns: {', '.join(missing_columns)}.",
                count=len(missing_columns),
                severity=Severity.FATAL,
            )
        )
    participation_count = connection.execute(
        "SELECT count(*) FROM player_game_participation "
        "WHERE source = 'nflverse_pfr_snap_counts' AND season_type = 'REG'"
    ).fetchone()
    if participation_count is None or int(participation_count[0]) == 0:
        issues.append(
            QualityIssue(
                code="participation_data_missing",
                message=(
                    "Verified snap-count participation is required before games-active "
                    "or points-per-game targets can be built."
                ),
                severity=Severity.FATAL,
            )
        )
    return issues


def _read_static_players(
    connection: duckdb.DuckDBPyConnection,
) -> dict[str, StaticPlayer]:
    rows = connection.execute(
        """
        SELECT
            player_id,
            pfr_id,
            canonical_position,
            birth_date,
            rookie_season,
            draft_year,
            draft_round,
            draft_pick,
            draft_team,
            height_inches,
            weight_lbs,
            identity_source_dataset_id,
            identity_source_as_of
        FROM players
        """
    ).fetchall()
    players: dict[str, StaticPlayer] = {}
    for row in rows:
        player_id = str(row[0])
        players[player_id] = StaticPlayer(
            player_id=player_id,
            pfr_id=_optional_str(row[1]),
            position=_normalize_position(row[2]),
            birth_date=row[3] if isinstance(row[3], date) else None,
            rookie_season=_optional_int(row[4]),
            draft_year=_optional_int(row[5]),
            draft_round=_optional_int(row[6]),
            draft_pick=_optional_int(row[7]),
            draft_team=_optional_str(row[8]),
            height_inches=_optional_int(row[9]),
            weight_lbs=_optional_int(row[10]),
            identity_source_dataset_id=_optional_str(row[11]),
            identity_source_as_of=row[12] if isinstance(row[12], datetime) else None,
        )
    return players


def _read_season_records(
    connection: duckdb.DuckDBPyConnection, rules: LeagueRules
) -> tuple[dict[tuple[str, int], SeasonRecord], dict[int, tuple[set[str], datetime]]]:
    records: dict[tuple[str, int], SeasonRecord] = {}
    score_sql = _weekly_score_sql(rules)
    yardage_bonus_sql = _weekly_yardage_bonus_sql(rules)
    stat_rows = connection.execute(
        f"""
        SELECT
            player_id,
            season,
            arg_max(position, week) FILTER (WHERE position IS NOT NULL) AS position,
            arg_max(nfl_team, week) FILTER (WHERE nfl_team IS NOT NULL) AS nfl_team,
            count(DISTINCT game_id) AS stat_games,
            sum({score_sql}) AS fantasy_points_total,
            sum(coalesce(completions, 0)),
            sum(coalesce(passing_attempts, 0)),
            sum(coalesce(passing_yards, 0)),
            sum(coalesce(passing_tds, 0)),
            sum(coalesce(interceptions, 0)),
            sum(coalesce(carries, 0)),
            sum(coalesce(rushing_yards, 0)),
            sum(coalesce(rushing_tds, 0)),
            sum(coalesce(targets, 0)),
            sum(coalesce(receptions, 0)),
            sum(coalesce(receiving_yards, 0)),
            sum(coalesce(receiving_tds, 0)),
            sum(coalesce(two_point_conversions, 0)),
            sum(coalesce(fumbles_lost, 0)),
            sum({yardage_bonus_sql}) AS yardage_bonus_points,
            list_sort(list_distinct(list(source_dataset_id))),
            max(as_of)
        FROM player_week_stats
        WHERE source = 'nflverse' AND season_type = 'REG'
        GROUP BY player_id, season
        ORDER BY season, player_id
        """
    ).fetchall()
    for row in stat_rows:
        player_id = str(row[0])
        season = int(row[1])
        record = SeasonRecord(
            player_id=player_id,
            season=season,
            position=_normalize_position(row[2]),
            nfl_team=_optional_str(row[3]),
            stat_games=int(row[4]),
            fantasy_points_total=float(row[5] or 0.0),
            completions=float(row[6] or 0.0),
            passing_attempts=float(row[7] or 0.0),
            passing_yards=float(row[8] or 0.0),
            passing_tds=float(row[9] or 0.0),
            interceptions=float(row[10] or 0.0),
            carries=float(row[11] or 0.0),
            rushing_yards=float(row[12] or 0.0),
            rushing_tds=float(row[13] or 0.0),
            targets=float(row[14] or 0.0),
            receptions=float(row[15] or 0.0),
            receiving_yards=float(row[16] or 0.0),
            receiving_tds=float(row[17] or 0.0),
            two_point_conversions=float(row[18] or 0.0),
            fumbles_lost=float(row[19] or 0.0),
            yardage_bonus_points=float(row[20] or 0.0),
            source_dataset_ids={str(value) for value in (row[21] or []) if value},
            source_max_as_of=row[22] if isinstance(row[22], datetime) else None,
        )
        records[(player_id, season)] = record

    participation_rows = connection.execute(
        """
        SELECT
            player_id,
            season,
            arg_max(position, week) FILTER (WHERE position IS NOT NULL) AS position,
            arg_max(nfl_team, week) FILTER (WHERE nfl_team IS NOT NULL) AS nfl_team,
            count(DISTINCT game_id) FILTER (
                WHERE coalesce(offense_snaps, 0)
                    + coalesce(defense_snaps, 0)
                    + coalesce(special_teams_snaps, 0) > 0
            ) AS games_active,
            list_sort(list_distinct(list(source_dataset_id))),
            max(as_of)
        FROM player_game_participation
        WHERE source = 'nflverse_pfr_snap_counts' AND season_type = 'REG'
        GROUP BY player_id, season
        ORDER BY season, player_id
        """
    ).fetchall()
    for row in participation_rows:
        key = (str(row[0]), int(row[1]))
        record = records.setdefault(key, SeasonRecord(key[0], key[1]))
        record.position = record.position or _normalize_position(row[2])
        record.nfl_team = _optional_str(row[3]) or record.nfl_team
        record.games_active = int(row[4])
        assert record.source_dataset_ids is not None
        record.source_dataset_ids.update(str(value) for value in (row[5] or []) if value)
        if isinstance(row[6], datetime):
            record.source_max_as_of = _max_datetime(record.source_max_as_of, row[6])

    coverage_rows = connection.execute(
        """
        SELECT
            weekly.player_id,
            weekly.season,
            count(*) FILTER (WHERE participation.player_id IS NULL) AS missing_games
        FROM player_week_stats AS weekly
        LEFT JOIN player_game_participation AS participation
          ON weekly.player_id = participation.player_id
         AND weekly.game_id = participation.game_id
         AND participation.source = 'nflverse_pfr_snap_counts'
         AND participation.season_type = 'REG'
         AND coalesce(participation.offense_snaps, 0)
             + coalesce(participation.defense_snaps, 0)
             + coalesce(participation.special_teams_snaps, 0) > 0
        WHERE weekly.source = 'nflverse'
          AND weekly.season_type = 'REG'
          AND abs(coalesce(weekly.completions, 0))
              + abs(coalesce(weekly.passing_attempts, 0))
              + abs(coalesce(weekly.passing_yards, 0))
              + abs(coalesce(weekly.passing_tds, 0))
              + abs(coalesce(weekly.interceptions, 0))
              + abs(coalesce(weekly.carries, 0))
              + abs(coalesce(weekly.rushing_yards, 0))
              + abs(coalesce(weekly.rushing_tds, 0))
              + abs(coalesce(weekly.targets, 0))
              + abs(coalesce(weekly.receptions, 0))
              + abs(coalesce(weekly.receiving_yards, 0))
              + abs(coalesce(weekly.receiving_tds, 0))
              + abs(coalesce(weekly.two_point_conversions, 0))
              + abs(coalesce(weekly.fumbles_lost, 0)) > 0
        GROUP BY weekly.player_id, weekly.season
        HAVING count(*) FILTER (WHERE participation.player_id IS NULL) > 0
        ORDER BY weekly.season, weekly.player_id
        """
    ).fetchall()
    for row in coverage_rows:
        key = (str(row[0]), int(row[1]))
        covered_record = records.get(key)
        if covered_record is not None:
            covered_record.missing_participation_games = int(row[2])
            covered_record.games_active = None

    lineage: dict[int, tuple[set[str], datetime]] = {}
    by_season_ids: dict[int, set[str]] = defaultdict(set)
    by_season_as_of: dict[int, datetime] = {}
    for record in records.values():
        assert record.source_dataset_ids is not None
        by_season_ids[record.season].update(record.source_dataset_ids)
        if record.source_max_as_of is not None:
            prior = by_season_as_of.get(record.season)
            by_season_as_of[record.season] = _max_datetime(prior, record.source_max_as_of)
    for season, dataset_ids in by_season_ids.items():
        if season in by_season_as_of:
            lineage[season] = (dataset_ids, by_season_as_of[season])
    return records, lineage


def _construct_rows(
    *,
    records: dict[tuple[str, int], SeasonRecord],
    static_players: dict[str, StaticPlayer],
    season_lineage: dict[int, tuple[set[str], datetime]],
    start_season: int,
    last_completed_season: int,
    final_prediction_season: int,
    rules: LeagueRules,
) -> tuple[list[FeatureRow], list[TargetRow], dict[str, Any]]:
    feature_rows: list[FeatureRow] = []
    target_rows: list[TargetRow] = []
    metrics: dict[str, Any] = {
        "live_rows_without_targets": 0,
        "target_rows_missing_games_active": 0,
        "rookie_rows": 0,
        "sparse_history_rows": 0,
        "cutoff_safe_static_position_rows": 0,
        "candidates_missing_cutoff_safe_position": 0,
        "missing_age_rows": 0,
        "missing_draft_capital_rows": 0,
        "participation_coverage_failures": 0,
        "missing_target_lineage": 0,
        "target_scorers_without_features": 0,
        "target_active_players_without_features": 0,
        "source_dataset_ids": set(),
    }
    players_by_recent_season: dict[int, set[str]] = defaultdict(set)
    for (player_id, season), record in records.items():
        if _record_position(record) in CORE_POSITIONS:
            players_by_recent_season[season].add(player_id)
        if (
            record.stat_games > 0
            and record.missing_participation_games > 0
            and _record_position(record) in CORE_POSITIONS
        ):
            metrics["participation_coverage_failures"] += 1

    rookies_by_season: dict[int, set[str]] = defaultdict(set)
    for player in static_players.values():
        if player.rookie_season is not None:
            rookies_by_season[player.rookie_season].add(player.player_id)

    for prediction_year in range(start_season + 1, final_prediction_season + 1):
        feature_year = prediction_year - 1
        candidate_ids = set(rookies_by_season.get(prediction_year, set()))
        candidate_ids.update(rookies_by_season.get(prediction_year - 1, set()))
        for offset in range(1, CANDIDATE_HISTORY_SEASONS + 1):
            candidate_ids.update(players_by_recent_season.get(prediction_year - offset, set()))
        priors = _position_priors(records, feature_year)
        for player_id in sorted(candidate_ids):
            static = static_players.get(player_id)
            cutoff = date(prediction_year, PRESEASON_CUTOFF_MONTH, PRESEASON_CUTOFF_DAY)
            history = [records.get((player_id, feature_year - offset)) for offset in range(3)]
            candidate_evidence_records: list[SeasonRecord] = []
            for offset in range(CANDIDATE_HISTORY_SEASONS):
                evidence_record = records.get((player_id, feature_year - offset))
                if evidence_record is not None:
                    candidate_evidence_records.append(evidence_record)
            evidence_position = _choose_position(
                candidate_evidence_records,
                static=None,
                allow_static=False,
            )
            allow_static_position = _static_position_available_at_cutoff(static, cutoff)
            position = _choose_position(
                candidate_evidence_records,
                static,
                allow_static=allow_static_position,
            )
            if (
                evidence_position not in CORE_POSITIONS
                and static is not None
                and static.position in CORE_POSITIONS
                and not allow_static_position
            ):
                metrics["candidates_missing_cutoff_safe_position"] += 1
            if position not in CORE_POSITIONS or position not in priors:
                continue
            if evidence_position not in CORE_POSITIONS:
                metrics["cutoff_safe_static_position_rows"] += 1
            payload = _feature_payload(
                history=history,
                static=static,
                position=position,
                prediction_season=prediction_year,
                cutoff=cutoff,
                position_prior=priors[position],
                rules=rules,
            )
            payload["candidate_evidence_seasons"] = sorted(
                record.season for record in candidate_evidence_records
            )
            payload["candidate_history_lookback_seasons"] = CANDIDATE_HISTORY_SEASONS
            payload["candidate_selection_reason"] = _candidate_selection_reason(
                static, prediction_year, candidate_evidence_records
            )
            history_records = candidate_evidence_records
            dataset_ids = {
                dataset_id
                for record in history_records
                for dataset_id in (record.source_dataset_ids or set())
            }
            if static is not None and static.identity_source_dataset_id:
                dataset_ids.add(static.identity_source_dataset_id)
            source_as_of = [
                record.source_max_as_of
                for record in history_records
                if record.source_max_as_of is not None
            ]
            if static is not None and static.identity_source_as_of is not None:
                source_as_of.append(static.identity_source_as_of)
            for year in range(
                max(start_season, feature_year - CANDIDATE_HISTORY_SEASONS + 1),
                feature_year + 1,
            ):
                if year in season_lineage:
                    year_ids, year_as_of = season_lineage[year]
                    dataset_ids.update(year_ids)
                    source_as_of.append(year_as_of)
            if not dataset_ids or not source_as_of:
                continue
            metrics["source_dataset_ids"].update(dataset_ids)
            metrics["rookie_rows"] += int(bool(payload["is_rookie"]))
            metrics["sparse_history_rows"] += int(payload["history_seasons"] < 2)
            metrics["missing_age_rows"] += int(bool(payload["missing_age"]))
            metrics["missing_draft_capital_rows"] += int(bool(payload["missing_draft_capital"]))
            feature_rows.append(
                FeatureRow(
                    player_id=player_id,
                    feature_season=feature_year,
                    prediction_season=prediction_year,
                    cutoff_date=cutoff,
                    position=position,
                    feature_payload=_canonical_json(payload),
                    source="nflverse",
                    source_dataset_ids=_canonical_json(sorted(dataset_ids)),
                    source_max_stat_season=feature_year,
                    source_max_as_of=max(source_as_of),
                )
            )
            if prediction_year <= last_completed_season:
                if prediction_year in season_lineage:
                    target_rows.append(
                        _target_row(
                            player_id,
                            prediction_year,
                            position,
                            records.get((player_id, prediction_year)),
                            static,
                            season_lineage[prediction_year],
                        )
                    )
                else:
                    metrics["missing_target_lineage"] += 1
            else:
                metrics["live_rows_without_targets"] += 1
    feature_keys = {(row.player_id, row.prediction_season) for row in feature_rows}
    metrics["target_scorers_without_features"] = sum(
        1
        for (player_id, season), record in records.items()
        if start_season < season <= min(last_completed_season, final_prediction_season)
        and abs(record.fantasy_points_total) > 1e-12
        and _record_position(record) in CORE_POSITIONS
        and (player_id, season) not in feature_keys
    )
    metrics["target_active_players_without_features"] = sum(
        1
        for (player_id, season), record in records.items()
        if start_season < season <= min(last_completed_season, final_prediction_season)
        and record.games_active is not None
        and record.games_active > 0
        and _record_position(record) in CORE_POSITIONS
        and (player_id, season) not in feature_keys
    )
    metrics["target_rows_missing_games_active"] = sum(
        json.loads(row.target_payload).get("games_active") is None for row in target_rows
    )
    return feature_rows, target_rows, metrics


def _position_priors(
    records: dict[tuple[str, int], SeasonRecord],
    feature_season: int,
) -> dict[str, dict[str, float]]:
    by_position: dict[str, list[SeasonRecord]] = defaultdict(list)
    for (_, season), record in records.items():
        if season != feature_season or record.games_active is None or record.games_active <= 0:
            continue
        position = _record_position(record)
        if position in CORE_POSITIONS:
            by_position[position].append(record)
    priors: dict[str, dict[str, float]] = {}
    for position in sorted(CORE_POSITIONS):
        group = by_position.get(position, [])
        if not group:
            continue
        priors[position] = {
            "fantasy_points_per_game": _mean(
                [
                    record.fantasy_points_total / record.games_active
                    for record in group
                    if record.games_active is not None
                ]
            ),
            "games_active": _mean(
                [float(record.games_active) for record in group if record.games_active is not None]
            ),
            "yardage_bonus_points_per_game": _mean(
                [
                    record.yardage_bonus_points / record.games_active
                    for record in group
                    if record.games_active is not None
                ]
            ),
        }
        for field in _component_fields():
            priors[position][field] = _mean(
                [
                    float(getattr(record, field)) / record.games_active
                    for record in group
                    if record.games_active is not None
                ]
            )
    return priors


def _feature_payload(
    *,
    history: list[SeasonRecord | None],
    static: StaticPlayer | None,
    position: str,
    prediction_season: int,
    cutoff: date,
    position_prior: dict[str, float],
    rules: LeagueRules,
) -> dict[str, Any]:
    lag1 = history[0]
    usable = [
        (record, HISTORY_WEIGHTS[index])
        for index, record in enumerate(history)
        if record is not None and record.games_active is not None and record.games_active > 0
    ]
    weighted_ppg = _weighted_metric(
        usable,
        lambda record: record.fantasy_points_total / record.games_active,
    )
    weighted_games = _weighted_metric(usable, lambda record: float(record.games_active))
    weighted_components = {
        field: _weighted_metric(
            usable,
            lambda record, component=field: float(getattr(record, component)) / record.games_active,
        )
        for field in _component_fields()
    }
    weighted_yardage_bonus_points = _weighted_metric(
        usable,
        lambda record: record.yardage_bonus_points / record.games_active,
    )
    prior_ppg = position_prior["fantasy_points_per_game"]
    previous_ppg = (
        lag1.fantasy_points_total / lag1.games_active
        if lag1 is not None and lag1.games_active is not None and lag1.games_active > 0
        else prior_ppg
    )
    base_weighted_ppg = weighted_ppg if weighted_ppg is not None else prior_ppg
    total_history_games = sum(
        record.games_active for record, _ in usable if record.games_active is not None
    )
    shrinkage_ppg = (
        base_weighted_ppg * total_history_games + prior_ppg * POSITION_PRIOR_STRENGTH_GAMES
    ) / (total_history_games + POSITION_PRIOR_STRENGTH_GAMES)
    age = _age_on(static.birth_date, cutoff) if static is not None else None
    age_factor = _age_adjustment(position, age)
    component_values: dict[str, float] = {}
    for field in _component_fields():
        weighted_component = weighted_components[field]
        component_values[field] = (
            weighted_component if weighted_component is not None else position_prior[field]
        )
    component_scoring = rules.scoring.model_copy(update={"yardage_bonuses": ()})
    component_ppg = score_player(
        PlayerStatLine(
            position=position,
            passing_yards=component_values["passing_yards"],
            passing_tds=component_values["passing_tds"],
            interceptions=component_values["interceptions"],
            rushing_yards=component_values["rushing_yards"],
            rushing_tds=component_values["rushing_tds"],
            receiving_yards=component_values["receiving_yards"],
            receptions=component_values["receptions"],
            receiving_tds=component_values["receiving_tds"],
            two_point_conversions=component_values["two_point_conversions"],
            fumbles_lost=component_values["fumbles_lost"],
        ),
        component_scoring,
    ) + (
        weighted_yardage_bonus_points
        if weighted_yardage_bonus_points is not None
        else position_prior["yardage_bonus_points_per_game"]
    )
    prior_games = position_prior["games_active"]
    projected_games = weighted_games if weighted_games is not None else prior_games
    payload: dict[str, Any] = {
        "age_at_cutoff": age,
        "age_adjustment_factor": age_factor,
        "draft_pick": static.draft_pick if static is not None else None,
        "draft_round": static.draft_round if static is not None else None,
        "draft_year": static.draft_year if static is not None else None,
        "height_inches": static.height_inches if static is not None else None,
        "history_seasons": len(usable),
        "is_rookie": bool(static and static.rookie_season == prediction_season),
        "lag1_fantasy_points_per_game": (
            lag1.fantasy_points_total / lag1.games_active
            if lag1 is not None and lag1.games_active is not None and lag1.games_active > 0
            else None
        ),
        "lag1_fantasy_points_total": (lag1.fantasy_points_total if lag1 is not None else None),
        "lag1_games_active": lag1.games_active if lag1 is not None else None,
        "lag1_stat_games": lag1.stat_games if lag1 is not None else None,
        "missing_age": age is None,
        "missing_draft_capital": not (static and static.draft_pick is not None),
        "missing_history": not usable,
        "missing_lag1": (lag1 is None or lag1.games_active is None or lag1.games_active == 0),
        "missing_lag1_participation": lag1 is not None and lag1.games_active is None,
        "nfl_experience_years": (
            max(0, prediction_season - static.rookie_season)
            if static is not None and static.rookie_season is not None
            else None
        ),
        "position_prior_fantasy_points_per_game": prior_ppg,
        "position_prior_games_active": prior_games,
        "previous_team": lag1.nfl_team if lag1 is not None else None,
        "team_changed_last_feature_season": _team_changed(history),
        "weighted_3yr_fantasy_points_per_game": weighted_ppg,
        "weighted_3yr_games_active": weighted_games,
        "baseline_previous_fantasy_points_per_game": previous_ppg,
        "baseline_weighted_fantasy_points_per_game": base_weighted_ppg,
        "baseline_age_adjusted_fantasy_points_per_game": base_weighted_ppg * age_factor,
        "baseline_shrinkage_fantasy_points_per_game": shrinkage_ppg,
        "baseline_components_fantasy_points_per_game": component_ppg,
        "baseline_previous_games_active": (
            float(lag1.games_active)
            if lag1 is not None and lag1.games_active is not None
            else prior_games
        ),
        "baseline_weighted_games_active": projected_games,
        "baseline_shrinkage_games_active": (
            projected_games * total_history_games + prior_games * POSITION_PRIOR_STRENGTH_GAMES
        )
        / (total_history_games + POSITION_PRIOR_STRENGTH_GAMES),
    }
    for field in _component_fields():
        payload[f"weighted_3yr_{field}_per_game"] = weighted_components[field]
    if rules.scoring.yardage_bonuses:
        payload["weighted_3yr_yardage_bonus_points_per_game"] = weighted_yardage_bonus_points
    return payload


def _target_row(
    player_id: str,
    prediction_season: int,
    position: str,
    record: SeasonRecord | None,
    static: StaticPlayer | None,
    lineage: tuple[set[str], datetime],
) -> TargetRow:
    games_active = (
        record.games_active
        if record is not None
        else (0 if static is not None and static.pfr_id is not None else None)
    )
    points = record.fantasy_points_total if record is not None else 0.0
    payload = {
        "fantasy_points_per_game": points / games_active if games_active else None,
        "fantasy_points_total": points,
        "games_active": games_active,
    }
    dataset_ids, source_max_as_of = lineage
    return TargetRow(
        player_id=player_id,
        prediction_season=prediction_season,
        position=position,
        target_payload=_canonical_json(payload),
        source="nflverse",
        source_dataset_ids=_canonical_json(sorted(dataset_ids)),
        source_max_as_of=source_max_as_of,
    )


def _validate_built_rows(
    feature_rows: list[FeatureRow],
    target_rows: list[TargetRow],
    metrics: dict[str, Any],
) -> list[QualityIssue]:
    issues: list[QualityIssue] = []
    feature_keys = [(row.player_id, row.prediction_season) for row in feature_rows]
    target_keys = [(row.player_id, row.prediction_season) for row in target_rows]
    duplicate_features = len(feature_keys) - len(set(feature_keys))
    duplicate_targets = len(target_keys) - len(set(target_keys))
    if duplicate_features or duplicate_targets:
        issues.append(
            QualityIssue(
                code="duplicate_player_seasons",
                message="Feature or target player-season keys are not unique.",
                count=duplicate_features + duplicate_targets,
                severity=Severity.FATAL,
            )
        )
    cutoff_violations = sum(
        row.feature_season != row.prediction_season - 1
        or (
            row.source_max_stat_season is not None
            and row.source_max_stat_season > row.feature_season
        )
        for row in feature_rows
    )
    if cutoff_violations:
        issues.append(
            QualityIssue(
                code="feature_cutoff_violation",
                message="Feature rows include an invalid season relationship.",
                count=cutoff_violations,
                severity=Severity.FATAL,
            )
        )
    forbidden_payloads = 0
    for row in feature_rows:
        keys = json.loads(row.feature_payload)
        forbidden_payloads += int(any(str(key).startswith(("target_", "actual_")) for key in keys))
    if forbidden_payloads:
        issues.append(
            QualityIssue(
                code="target_in_feature_payload",
                message="Target-derived fields entered the feature payload.",
                count=forbidden_payloads,
                severity=Severity.FATAL,
            )
        )
    if not feature_rows:
        issues.append(
            QualityIssue(
                code="no_feature_rows",
                message="No cutoff-safe core-position player-season rows were constructed.",
                severity=Severity.FATAL,
            )
        )
    coverage_failures = int(metrics["participation_coverage_failures"])
    if coverage_failures:
        issues.append(
            QualityIssue(
                code="missing_participation_for_scoring_rows",
                message=(
                    "Core-position games with nonzero stats or opportunities lack "
                    "complete mapped positive-snap participation. Their total points are "
                    "retained, while games-active and PPG are null for the affected "
                    "player-season."
                ),
                count=coverage_failures,
                severity=Severity.WARNING,
            )
        )
    missing_target_games = int(metrics["target_rows_missing_games_active"])
    if missing_target_games:
        issues.append(
            QualityIssue(
                code="target_games_active_unavailable",
                message=(
                    "Historical candidate outcomes lack complete positive-snap evidence. "
                    "Total points remain available, but games active and points per game "
                    "are null rather than inferred as zero."
                ),
                count=missing_target_games,
                severity=Severity.WARNING,
            )
        )
    missing_target_lineage = int(metrics["missing_target_lineage"])
    if missing_target_lineage:
        issues.append(
            QualityIssue(
                code="missing_completed_target_lineage",
                message=(
                    "A configured completed prediction season has no verified season-wide "
                    "target lineage; zero outcomes were not invented."
                ),
                count=missing_target_lineage,
                severity=Severity.FATAL,
            )
        )
    missing_scorers = int(metrics["target_scorers_without_features"])
    if missing_scorers:
        issues.append(
            QualityIssue(
                code="target_scorers_outside_candidate_universe",
                message=(
                    "Completed-season scorers lacked cutoff-safe candidate evidence under "
                    "the four-year history plus two-cohort entry policy; they are counted "
                    "but were not selected from future outcomes."
                ),
                count=missing_scorers,
                severity=Severity.WARNING,
            )
        )
    missing_active = int(metrics["target_active_players_without_features"])
    if missing_active:
        issues.append(
            QualityIssue(
                code="target_active_players_outside_candidate_universe",
                message=(
                    "Completed-season active players lacked cutoff-safe candidate "
                    "evidence under the four-year history plus two-cohort entry policy; "
                    "they are counted without using target activity for selection."
                ),
                count=missing_active,
                severity=Severity.WARNING,
            )
        )
    missing_cutoff_position = int(metrics["candidates_missing_cutoff_safe_position"])
    if missing_cutoff_position:
        issues.append(
            QualityIssue(
                code="candidate_position_unavailable_at_cutoff",
                message=(
                    "Current-core entry-cohort candidates had no historical position "
                    "evidence available before the preseason cutoff. The latest player "
                    "snapshot was not backfilled into those historical rows."
                ),
                count=missing_cutoff_position,
                severity=Severity.WARNING,
            )
        )
    return issues


def _commit_feature_rows(
    warehouse: Warehouse,
    feature_rows: list[FeatureRow],
    target_rows: list[TargetRow],
    data_fingerprint: str,
    target_fingerprint: str,
    build_fingerprint: str,
    scoring_fingerprint: str,
    quality: FeatureQualityReport,
) -> None:
    with warehouse.connect() as connection:
        _ensure_feature_schema(connection)
        _stage_feature_rows(
            connection,
            feature_rows,
            target_rows,
            data_fingerprint,
            target_fingerprint,
            scoring_fingerprint,
        )
        connection.execute("BEGIN TRANSACTION")
        try:
            connection.execute(
                """
                MERGE INTO player_season_features AS target
                USING staged_player_season_features AS source
                ON target.player_id = source.player_id
                   AND target.prediction_season = source.prediction_season
                WHEN MATCHED THEN UPDATE SET
                    feature_season = source.feature_season,
                    cutoff_date = source.cutoff_date,
                    feature_available_at = source.feature_available_at,
                    position = source.position,
                    feature_payload = source.feature_payload,
                    target_payload = NULL,
                    source = source.source,
                    is_synthetic = source.is_synthetic,
                    feature_version = source.feature_version,
                    scoring_ruleset_fingerprint = source.scoring_ruleset_fingerprint,
                    source_dataset_ids = source.source_dataset_ids,
                    source_max_stat_season = source.source_max_stat_season,
                    source_max_as_of = source.source_max_as_of,
                    data_fingerprint = source.data_fingerprint
                WHEN NOT MATCHED THEN INSERT BY NAME
                """
            )
            connection.execute(
                """
                DELETE FROM player_season_features AS target
                WHERE target.source = 'nflverse'
                  AND NOT EXISTS (
                      SELECT 1 FROM staged_player_season_features AS source
                      WHERE source.player_id = target.player_id
                        AND source.prediction_season = target.prediction_season
                  )
                """
            )
            connection.execute(
                """
                MERGE INTO player_season_targets AS target
                USING staged_player_season_targets AS source
                ON target.player_id = source.player_id
                   AND target.prediction_season = source.prediction_season
                WHEN MATCHED THEN UPDATE SET
                    position = source.position,
                    target_payload = source.target_payload,
                    source = source.source,
                    is_synthetic = source.is_synthetic,
                    target_version = source.target_version,
                    scoring_ruleset_fingerprint = source.scoring_ruleset_fingerprint,
                    source_dataset_ids = source.source_dataset_ids,
                    source_max_as_of = source.source_max_as_of,
                    data_fingerprint = source.data_fingerprint,
                    target_data_fingerprint = source.target_data_fingerprint
                WHEN NOT MATCHED THEN INSERT BY NAME
                """
            )
            connection.execute(
                """
                DELETE FROM player_season_targets AS target
                WHERE target.source = 'nflverse'
                  AND NOT EXISTS (
                      SELECT 1 FROM staged_player_season_targets AS source
                      WHERE source.player_id = target.player_id
                        AND source.prediction_season = target.prediction_season
                  )
                """
            )
            source_max_as_of = max(row.source_max_as_of for row in feature_rows)
            connection.execute(
                """
                INSERT INTO feature_build_metadata (
                    data_fingerprint, target_data_fingerprint, build_fingerprint,
                    feature_version, scoring_ruleset_fingerprint, start_prediction_season,
                    end_prediction_season, feature_rows, target_rows, source_dataset_ids,
                    source_max_as_of, quality_payload
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT (data_fingerprint) DO UPDATE SET
                    target_data_fingerprint = excluded.target_data_fingerprint,
                    build_fingerprint = excluded.build_fingerprint,
                    feature_version = excluded.feature_version,
                    scoring_ruleset_fingerprint = excluded.scoring_ruleset_fingerprint,
                    start_prediction_season = excluded.start_prediction_season,
                    end_prediction_season = excluded.end_prediction_season,
                    feature_rows = excluded.feature_rows,
                    target_rows = excluded.target_rows,
                    source_dataset_ids = excluded.source_dataset_ids,
                    source_max_as_of = excluded.source_max_as_of,
                    quality_payload = excluded.quality_payload
                """,
                [
                    data_fingerprint,
                    target_fingerprint,
                    build_fingerprint,
                    FEATURE_VERSION,
                    scoring_fingerprint,
                    min(row.prediction_season for row in feature_rows),
                    max(row.prediction_season for row in feature_rows),
                    len(feature_rows),
                    len(target_rows),
                    _canonical_json(list(quality.source_dataset_ids)),
                    source_max_as_of,
                    _canonical_json(_quality_json_payload(quality)),
                ],
            )
            connection.execute(
                "DELETE FROM feature_build_metadata WHERE data_fingerprint <> ?",
                [data_fingerprint],
            )
            connection.execute(
                "DELETE FROM baseline_predictions "
                "WHERE build_fingerprint IS NULL OR build_fingerprint <> ?",
                [build_fingerprint],
            )
            connection.execute(
                "DELETE FROM baseline_evaluation_metadata "
                "WHERE build_fingerprint IS NULL OR build_fingerprint <> ?",
                [build_fingerprint],
            )
            invalidate_player_projection_runs(
                connection,
                build_fingerprint=build_fingerprint,
            )
            _validate_committed_feature_set(
                connection,
                len(feature_rows),
                len(target_rows),
                data_fingerprint,
                target_fingerprint,
                build_fingerprint,
            )
            connection.execute("COMMIT")
        except Exception:
            connection.execute("ROLLBACK")
            raise


def _stage_feature_rows(
    connection: duckdb.DuckDBPyConnection,
    feature_rows: list[FeatureRow],
    target_rows: list[TargetRow],
    data_fingerprint: str,
    target_fingerprint: str,
    scoring_fingerprint: str,
) -> None:
    connection.execute(
        "CREATE OR REPLACE TEMP TABLE staged_player_season_features AS "
        "SELECT * FROM player_season_features WHERE FALSE"
    )
    connection.executemany(
        """
        INSERT INTO staged_player_season_features (
            player_id, feature_season, prediction_season, cutoff_date,
            feature_available_at, position, feature_payload, target_payload,
            source, is_synthetic, feature_version, scoring_ruleset_fingerprint,
            source_dataset_ids, source_max_stat_season, source_max_as_of,
            data_fingerprint
        ) VALUES (?, ?, ?, ?, ?, ?, ?, NULL, ?, FALSE, ?, ?, ?, ?, ?, ?)
        """,
        [
            (
                row.player_id,
                row.feature_season,
                row.prediction_season,
                row.cutoff_date,
                row.cutoff_date,
                row.position,
                row.feature_payload,
                row.source,
                FEATURE_VERSION,
                scoring_fingerprint,
                row.source_dataset_ids,
                row.source_max_stat_season,
                row.source_max_as_of,
                data_fingerprint,
            )
            for row in feature_rows
        ],
    )
    connection.execute(
        "CREATE OR REPLACE TEMP TABLE staged_player_season_targets AS "
        "SELECT * FROM player_season_targets WHERE FALSE"
    )
    if target_rows:
        connection.executemany(
            """
            INSERT INTO staged_player_season_targets (
                player_id, prediction_season, position, target_payload, source,
                is_synthetic, target_version, scoring_ruleset_fingerprint,
                source_dataset_ids, source_max_as_of, data_fingerprint,
                target_data_fingerprint
            ) VALUES (?, ?, ?, ?, ?, FALSE, ?, ?, ?, ?, ?, ?)
            """,
            [
                (
                    row.player_id,
                    row.prediction_season,
                    row.position,
                    row.target_payload,
                    row.source,
                    FEATURE_VERSION,
                    scoring_fingerprint,
                    row.source_dataset_ids,
                    row.source_max_as_of,
                    data_fingerprint,
                    target_fingerprint,
                )
                for row in target_rows
            ],
        )


def _ensure_feature_schema(connection: duckdb.DuckDBPyConnection) -> None:
    connection.execute(
        """
        ALTER TABLE player_season_features ADD COLUMN IF NOT EXISTS
            feature_available_at DATE;
        ALTER TABLE player_season_features ADD COLUMN IF NOT EXISTS
            feature_version VARCHAR;
        ALTER TABLE player_season_features ADD COLUMN IF NOT EXISTS
            scoring_ruleset_fingerprint VARCHAR;
        ALTER TABLE player_season_features ADD COLUMN IF NOT EXISTS
            source_dataset_ids JSON;
        ALTER TABLE player_season_features ADD COLUMN IF NOT EXISTS
            source_max_stat_season INTEGER;
        ALTER TABLE player_season_features ADD COLUMN IF NOT EXISTS
            source_max_as_of TIMESTAMPTZ;
        ALTER TABLE player_season_features ADD COLUMN IF NOT EXISTS
            data_fingerprint VARCHAR;
        ALTER TABLE player_season_targets ADD COLUMN IF NOT EXISTS
            target_data_fingerprint VARCHAR;
        ALTER TABLE feature_build_metadata ADD COLUMN IF NOT EXISTS
            target_data_fingerprint VARCHAR;
        ALTER TABLE feature_build_metadata ADD COLUMN IF NOT EXISTS
            build_fingerprint VARCHAR;
        ALTER TABLE baseline_predictions ADD COLUMN IF NOT EXISTS
            target_data_fingerprint VARCHAR;
        ALTER TABLE baseline_predictions ADD COLUMN IF NOT EXISTS
            build_fingerprint VARCHAR;
        ALTER TABLE baseline_evaluation_metadata ADD COLUMN IF NOT EXISTS
            target_data_fingerprint VARCHAR;
        ALTER TABLE baseline_evaluation_metadata ADD COLUMN IF NOT EXISTS
            build_fingerprint VARCHAR;

        CREATE TABLE IF NOT EXISTS player_season_targets (
            player_id VARCHAR NOT NULL,
            prediction_season INTEGER NOT NULL,
            position VARCHAR NOT NULL,
            target_payload JSON NOT NULL,
            source VARCHAR NOT NULL,
            is_synthetic BOOLEAN NOT NULL DEFAULT FALSE,
            target_version VARCHAR NOT NULL,
            scoring_ruleset_fingerprint VARCHAR NOT NULL,
            source_dataset_ids JSON NOT NULL,
            source_max_as_of TIMESTAMPTZ NOT NULL,
            data_fingerprint VARCHAR NOT NULL,
            target_data_fingerprint VARCHAR NOT NULL,
            PRIMARY KEY (player_id, prediction_season)
        );

        CREATE TABLE IF NOT EXISTS feature_build_metadata (
            data_fingerprint VARCHAR PRIMARY KEY,
            target_data_fingerprint VARCHAR NOT NULL,
            build_fingerprint VARCHAR NOT NULL,
            feature_version VARCHAR NOT NULL,
            scoring_ruleset_fingerprint VARCHAR NOT NULL,
            start_prediction_season INTEGER NOT NULL,
            end_prediction_season INTEGER NOT NULL,
            feature_rows INTEGER NOT NULL,
            target_rows INTEGER NOT NULL,
            source_dataset_ids JSON NOT NULL,
            source_max_as_of TIMESTAMPTZ NOT NULL,
            quality_payload JSON NOT NULL
        );
        """
    )


def _validate_committed_feature_set(
    connection: duckdb.DuckDBPyConnection,
    expected_features: int,
    expected_targets: int,
    data_fingerprint: str,
    target_fingerprint: str,
    build_fingerprint: str,
) -> None:
    actual = connection.execute(
        """
        SELECT
            count(*),
            count(DISTINCT (player_id, prediction_season)),
            count(*) FILTER (
                WHERE feature_season <> prediction_season - 1
                   OR source_max_stat_season > feature_season
                   OR data_fingerprint IS DISTINCT FROM ?
            )
        FROM player_season_features
        WHERE source = 'nflverse'
        """,
        [data_fingerprint],
    ).fetchone()
    targets = connection.execute(
        """
        SELECT
            count(*),
            count(*) FILTER (
                WHERE data_fingerprint IS DISTINCT FROM ?
                   OR target_data_fingerprint IS DISTINCT FROM ?
            )
        FROM player_season_targets
        WHERE source = 'nflverse'
        """,
        [data_fingerprint, target_fingerprint],
    ).fetchone()
    metadata = connection.execute(
        """
        SELECT count(*)
        FROM feature_build_metadata
        WHERE data_fingerprint = ?
          AND target_data_fingerprint = ?
          AND build_fingerprint = ?
        """,
        [data_fingerprint, target_fingerprint, build_fingerprint],
    ).fetchone()
    if (
        actual is None
        or targets is None
        or int(actual[0]) != expected_features
        or int(actual[1]) != expected_features
        or int(actual[2]) != 0
        or int(targets[0]) != expected_targets
        or int(targets[1]) != 0
        or metadata is None
        or int(metadata[0]) != 1
    ):
        raise RuntimeError("Post-load feature invariants failed; transaction was rolled back.")


def _write_quality_report(
    config: AppConfig,
    output_dir: Path | None,
    quality: FeatureQualityReport,
    data_fingerprint: str,
    target_fingerprint: str,
    build_fingerprint: str,
    scoring_fingerprint: str,
) -> Path:
    directory = output_dir or config.resolve(config.paths.processed_dir) / "features"
    if not directory.is_absolute():
        directory = config.project_root / directory
    directory.mkdir(parents=True, exist_ok=True)
    path = directory / "player_season_features_quality.json"
    payload = {
        "data_fingerprint": data_fingerprint,
        "target_data_fingerprint": target_fingerprint,
        "build_fingerprint": build_fingerprint,
        "feature_version": FEATURE_VERSION,
        "quality": _quality_json_payload(quality),
        "scoring_ruleset_fingerprint": scoring_fingerprint,
    }
    path.write_text(_canonical_json(payload, indent=2) + "\n", encoding="utf-8")
    return path.resolve()


def _quality_json_payload(quality: FeatureQualityReport) -> dict[str, Any]:
    payload = asdict(quality)
    payload["issues"] = [issue.model_dump(mode="json") for issue in quality.issues]
    return payload


def _feature_fingerprint(features: list[FeatureRow], scoring_fingerprint: str) -> str:
    payload = {
        "feature_version": FEATURE_VERSION,
        "scoring_ruleset_fingerprint": scoring_fingerprint,
        "features": [asdict(row) for row in features],
    }
    encoded = _canonical_json(payload).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def _target_fingerprint(targets: list[TargetRow], scoring_fingerprint: str) -> str:
    payload = {
        "target_version": FEATURE_VERSION,
        "scoring_ruleset_fingerprint": scoring_fingerprint,
        "targets": [asdict(row) for row in targets],
    }
    encoded = _canonical_json(payload).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def _build_fingerprint(
    feature_fingerprint: str,
    target_fingerprint: str,
    scoring_fingerprint: str,
) -> str:
    payload = {
        "feature_data_fingerprint": feature_fingerprint,
        "target_data_fingerprint": target_fingerprint,
        "feature_version": FEATURE_VERSION,
        "scoring_ruleset_fingerprint": scoring_fingerprint,
    }
    return hashlib.sha256(_canonical_json(payload).encode("utf-8")).hexdigest()


def _weekly_score_sql(rules: LeagueRules) -> str:
    scoring = rules.scoring
    position_bonus = "0.0"
    if scoring.position_reception_bonus:
        cases = " ".join(
            f"WHEN upper(position) = {_sql_string(position)} THEN {_sql_number(points)}"
            for position, points in scoring.position_reception_bonus.items()
        )
        position_bonus = f"CASE {cases} ELSE 0.0 END"
    terms = [
        f"coalesce(passing_yards, 0) / {_sql_number(scoring.passing_yards_per_point)}",
        f"coalesce(passing_tds, 0) * {_sql_number(scoring.passing_td)}",
        f"coalesce(interceptions, 0) * {_sql_number(scoring.interception)}",
        f"coalesce(rushing_yards, 0) / {_sql_number(scoring.rushing_yards_per_point)}",
        f"coalesce(rushing_tds, 0) * {_sql_number(scoring.rushing_td)}",
        f"coalesce(receiving_yards, 0) / {_sql_number(scoring.receiving_yards_per_point)}",
        f"coalesce(receptions, 0) * ({_sql_number(scoring.reception)} + {position_bonus})",
        f"coalesce(receiving_tds, 0) * {_sql_number(scoring.receiving_td)}",
        f"coalesce(two_point_conversions, 0) * {_sql_number(scoring.two_point_conversion)}",
        f"coalesce(fumbles_lost, 0) * {_sql_number(scoring.fumble_lost)}",
        _weekly_yardage_bonus_sql(rules),
    ]
    return " + ".join(terms)


def _weekly_yardage_bonus_sql(rules: LeagueRules) -> str:
    bonuses = [
        f"CASE WHEN coalesce({bonus.category}, 0) >= {_sql_number(bonus.threshold)} "
        f"THEN {_sql_number(bonus.points)} ELSE 0.0 END"
        for bonus in rules.scoring.yardage_bonuses
    ]
    return " + ".join(bonuses) if bonuses else "0.0"


def _sql_number(value: float) -> str:
    number = float(value)
    if not math.isfinite(number):
        raise ValueError("Scoring values must be finite.")
    return repr(number)


def _sql_string(value: str) -> str:
    return "'" + value.replace("'", "''") + "'"


def _component_fields() -> tuple[str, ...]:
    return (
        "passing_attempts",
        "passing_yards",
        "passing_tds",
        "interceptions",
        "carries",
        "rushing_yards",
        "rushing_tds",
        "targets",
        "receptions",
        "receiving_yards",
        "receiving_tds",
        "two_point_conversions",
        "fumbles_lost",
    )


def _weighted_metric(
    records: list[tuple[SeasonRecord, float]],
    value: Any,
) -> float | None:
    if not records:
        return None
    denominator = sum(weight for _, weight in records)
    return sum(float(value(record)) * weight for record, weight in records) / denominator


def _choose_position(
    history: Sequence[SeasonRecord | None],
    static: StaticPlayer | None,
    *,
    allow_static: bool,
) -> str | None:
    for record in history:
        if record is not None:
            position = _record_position(record)
            if position in CORE_POSITIONS:
                return position
    return static.position if allow_static and static is not None else None


def _record_position(record: SeasonRecord) -> str | None:
    return _normalize_position(record.position)


def _static_position_available_at_cutoff(
    static: StaticPlayer | None,
    cutoff: date,
) -> bool:
    return bool(
        static is not None
        and static.position in CORE_POSITIONS
        and static.identity_source_as_of is not None
        and static.identity_source_as_of.date() <= cutoff
    )


def _candidate_selection_reason(
    static: StaticPlayer | None,
    prediction_season: int,
    evidence: list[SeasonRecord],
) -> str:
    if static is not None and static.rookie_season == prediction_season:
        return "rookie_entry_cohort"
    if static is not None and static.rookie_season == prediction_season - 1:
        return "second_year_entry_cohort"
    if evidence:
        return "prior_four_season_record"
    return "position_prior_fallback"


def _normalize_position(value: object) -> str | None:
    if value is None:
        return None
    position = str(value).strip().upper()
    aliases = {"HB": "RB", "FB": "RB", "FL": "WR", "SE": "WR"}
    direct = aliases.get(position, position)
    if direct in CORE_POSITIONS:
        return direct
    tokens = {aliases.get(token, token) for token in position.replace("-", "/").split("/") if token}
    core_tokens = tokens & CORE_POSITIONS
    return next(iter(core_tokens)) if len(core_tokens) == 1 else direct or None


def _team_changed(history: list[SeasonRecord | None]) -> bool | None:
    if len(history) < 2 or history[0] is None or history[1] is None:
        return None
    current = history[0].nfl_team
    prior = history[1].nfl_team
    return bool(current and prior and current != prior) if current and prior else None


def _age_on(birth_date: date | None, cutoff: date) -> float | None:
    if birth_date is None or birth_date > cutoff:
        return None
    return round((cutoff - birth_date).days / 365.2425, 3)


def _age_adjustment(position: str, age: float | None) -> float:
    """Return a transparent, continuous age adjustment for baseline projections.

    Age is a performance input, not an injury forecast. Older versions used abrupt
    birthday cliffs (for example, an RB changed from 0.96 to 0.90 immediately after
    age 27). A smooth bounded decline avoids those artificial discontinuities while
    preserving a conservative veteran trend.
    """

    if age is None:
        return 1.0
    if position == "QB":
        if age < 25:
            return 1.03
        if age <= 34:
            return 1.0
        return _bounded_age_decline(age, start_age=34, annual_decline=0.02, floor=0.86)
    if position == "RB":
        if age < 24:
            return 1.03
        if age <= 26:
            return 1.0
        return _bounded_age_decline(age, start_age=26, annual_decline=0.03, floor=0.82)
    if position == "WR":
        if age < 24:
            return 1.04
        if age <= 27:
            return 1.0
        return _bounded_age_decline(age, start_age=27, annual_decline=0.02, floor=0.88)
    if age < 25:
        return 1.03
    if age <= 29:
        return 1.0
    return _bounded_age_decline(age, start_age=29, annual_decline=0.02, floor=0.92)


def _bounded_age_decline(
    age: float,
    *,
    start_age: float,
    annual_decline: float,
    floor: float,
) -> float:
    """Apply a continuous linear decline with an explicit lower bound."""

    decline_years = max(0.0, age - start_age)
    return round(max(floor, 1.0 - annual_decline * decline_years), 6)


def _mean(values: list[float]) -> float:
    return sum(values) / len(values)


def _max_datetime(left: datetime | None, right: datetime) -> datetime:
    return right if left is None or right > left else left


def _optional_int(value: object) -> int | None:
    return None if value is None else int(str(value))


def _optional_str(value: object) -> str | None:
    if value is None:
        return None
    normalized = str(value).strip()
    return normalized or None


def _canonical_json(value: object, *, indent: int | None = None) -> str:
    return json.dumps(
        value,
        sort_keys=True,
        separators=(",", ":") if indent is None else None,
        ensure_ascii=True,
        allow_nan=False,
        default=_json_default,
        indent=indent,
    )


def _json_default(value: object) -> str:
    if isinstance(value, datetime):
        if value.tzinfo is not None:
            return value.astimezone(UTC).isoformat()
        return value.isoformat()
    if isinstance(value, date):
        return value.isoformat()
    raise TypeError(f"Cannot serialize {type(value).__name__} to canonical JSON.")
