"""Phase 8 structural draft features and drafted-only historical scoring."""

from __future__ import annotations

import hashlib
import json
from collections import Counter, defaultdict
from dataclasses import dataclass, replace
from datetime import UTC, datetime
from typing import Any

import duckdb

from fantasy_draft_ai.config import AppConfig
from fantasy_draft_ai.data.warehouse import Warehouse
from fantasy_draft_ai.draft.roster import RosterPlayer, assign_roster
from fantasy_draft_ai.rules.models import DraftSettings, FlexSlot, LeagueRules
from fantasy_draft_ai.scoring.engine import PlayerStatLine, ScoringRules, score_player

FEATURE_VERSION = "roster-construction-v1"
METRIC_VERSION = "draft-only-v1"
SUPPORTED_SCORING_POSITIONS = frozenset({"QB", "RB", "WR", "TE"})


@dataclass(frozen=True)
class HistoryBuildIssue:
    code: str
    message: str
    league_season_id: str | None = None
    team_id: str | None = None

    def as_dict(self) -> dict[str, object]:
        return dict(self.__dict__)


@dataclass(frozen=True)
class RosterHistoryBuildResult:
    committed: bool
    league_seasons: int
    feature_rows: int
    metric_rows: int
    ready_metric_rows: int
    build_fingerprint: str
    issues: tuple[HistoryBuildIssue, ...]

    def render(self) -> str:
        lines = [
            f"Roster-history build: {'COMMITTED' if self.committed else 'NOT COMMITTED'}",
            f"League-seasons: {self.league_seasons}",
            f"Roster feature rows: {self.feature_rows}",
            f"Draft-only metric rows: {self.metric_rows}",
            f"Ready metric rows: {self.ready_metric_rows}",
            f"Build fingerprint: {self.build_fingerprint or 'unavailable'}",
        ]
        lines.extend(f"- {issue.code}: {issue.message}" for issue in self.issues)
        return "\n".join(lines)


@dataclass(frozen=True)
class _LeagueRecord:
    league_season_id: str
    package_fingerprint: str
    season: int
    team_count: int
    ruleset_fingerprint: str
    rules: LeagueRules
    playoff_start_week: int | None


@dataclass(frozen=True)
class _Pick:
    overall_pick: int
    round: int
    draft_slot: int
    team_id: str
    player_id: str | None
    position: str


@dataclass(frozen=True)
class _MetricRow:
    league_season_id: str
    team_id: str
    package_fingerprint: str
    weekly_data_fingerprint: str
    scoring_fingerprint: str
    weeks_scored: int
    optimal_lineup_points: float | None
    best_ball_points: float | None
    drafted_starter_games: int | None
    starter_slot_weeks: int | None
    unfilled_starter_slot_weeks: int | None
    points_percentile: float | None
    mapping_coverage: float
    status: str
    metrics_payload: dict[str, Any]


@dataclass(frozen=True)
class _WeeklyEvidence:
    rows: tuple[tuple[Any, ...], ...]
    expected_weeks: tuple[int, ...]
    covered_weeks: tuple[int, ...]
    covered_player_ids: frozenset[str]

    @property
    def complete_weeks(self) -> bool:
        return self.expected_weeks == self.covered_weeks


def build_roster_history(config: AppConfig) -> RosterHistoryBuildResult:
    """Build deterministic descriptive history without training an outcome model."""

    warehouse = Warehouse(config.resolve(config.paths.warehouse))
    warehouse.initialize()
    with warehouse.connect(read_only=True) as connection:
        leagues = _load_leagues(connection)
        picks_by_league = {
            league.league_season_id: _load_picks(connection, league.league_season_id)
            for league in leagues
        }

    feature_rows: list[tuple[str, str, str, str, str, dict[str, Any]]] = []
    metric_rows: list[_MetricRow] = []
    issues: list[HistoryBuildIssue] = []
    for league in leagues:
        picks = picks_by_league[league.league_season_id]
        team_picks = _group_team_picks(picks)
        for team_id, roster in sorted(team_picks.items()):
            try:
                payload = _feature_payload(league, roster)
            except ValueError as exc:
                issues.append(
                    HistoryBuildIssue(
                        code="roster_feature_unavailable",
                        message=str(exc),
                        league_season_id=league.league_season_id,
                        team_id=team_id,
                    )
                )
                continue
            feature_rows.append(
                (
                    league.league_season_id,
                    team_id,
                    FEATURE_VERSION,
                    league.package_fingerprint,
                    league.ruleset_fingerprint,
                    payload,
                )
            )
        league_metrics, league_issues = _draft_only_metrics(config, league, team_picks)
        metric_rows.extend(league_metrics)
        issues.extend(league_issues)

    metric_rows = _with_percentiles(metric_rows)
    fingerprint = _build_fingerprint(feature_rows, metric_rows)
    now = datetime.now(UTC)
    try:
        with warehouse.connect() as connection:
            connection.execute("BEGIN TRANSACTION")
            try:
                for feature_row in feature_rows:
                    _upsert_feature(connection, feature_row, now)
                for metric_row in metric_rows:
                    _upsert_metric(connection, metric_row, now)
                    if metric_row.status == "ready":
                        connection.execute(
                            """
                            UPDATE team_outcomes
                            SET draft_only_metrics = ?
                            WHERE league_season_id = ? AND team_id = ?
                            """,
                            [
                                _canonical_json(metric_row.metrics_payload),
                                metric_row.league_season_id,
                                metric_row.team_id,
                            ],
                        )
                    else:
                        connection.execute(
                            """
                            UPDATE team_outcomes
                            SET draft_only_metrics = NULL
                            WHERE league_season_id = ? AND team_id = ?
                            """,
                            [metric_row.league_season_id, metric_row.team_id],
                        )
                _verify_build_rows(connection, feature_rows, metric_rows)
                connection.execute("COMMIT")
            except Exception:
                connection.execute("ROLLBACK")
                raise
    except (duckdb.Error, OSError, TypeError, ValueError) as exc:
        return RosterHistoryBuildResult(
            committed=False,
            league_seasons=len(leagues),
            feature_rows=len(feature_rows),
            metric_rows=len(metric_rows),
            ready_metric_rows=sum(row.status == "ready" for row in metric_rows),
            build_fingerprint=fingerprint,
            issues=(*issues, HistoryBuildIssue("warehouse_transaction_failed", str(exc))),
        )
    return RosterHistoryBuildResult(
        committed=True,
        league_seasons=len(leagues),
        feature_rows=len(feature_rows),
        metric_rows=len(metric_rows),
        ready_metric_rows=sum(row.status == "ready" for row in metric_rows),
        build_fingerprint=fingerprint,
        issues=tuple(issues),
    )


def _load_leagues(connection: duckdb.DuckDBPyConnection) -> tuple[_LeagueRecord, ...]:
    rows = connection.execute(
        """
        SELECT history.league_season_id, history.package_fingerprint, history.season,
               history.team_count, history.ruleset_fingerprint,
               rules.draft_type, rules.rounds, rules.starter_slots_json,
               rules.flex_slots_json, rules.bench_slots, rules.ir_slots,
               rules.scoring_json, rules.playoff_settings_json
        FROM league_history_leagues AS history
        JOIN league_rules AS rules USING (league_season_id)
        ORDER BY history.season, history.league_season_id
        """
    ).fetchall()
    leagues: list[_LeagueRecord] = []
    for row in rows:
        starters = json.loads(str(row[7]))
        flex_payload = json.loads(str(row[8]))
        scoring = ScoringRules.model_validate(json.loads(str(row[11])))
        draft_type = str(row[5])
        if draft_type != "snake":
            raise ValueError(f"Unsupported historical draft type: {draft_type!r}.")
        rules = LeagueRules(
            season=int(row[2]),
            teams=int(row[3]),
            draft=DraftSettings(type="snake", rounds=int(row[6]), keepers=0),
            starters={str(key): int(value) for key, value in starters.items()},
            flex_slots=tuple(FlexSlot.model_validate(item) for item in flex_payload),
            bench=int(row[9]),
            ir=int(row[10]),
            scoring=scoring,
        )
        playoff = json.loads(str(row[12])) if row[12] is not None else {}
        leagues.append(
            _LeagueRecord(
                league_season_id=str(row[0]),
                package_fingerprint=str(row[1]),
                season=int(row[2]),
                team_count=int(row[3]),
                ruleset_fingerprint=str(row[4]),
                rules=rules,
                playoff_start_week=(
                    int(playoff["playoff_start_week"])
                    if playoff.get("playoff_start_week") is not None
                    else None
                ),
            )
        )
    return tuple(leagues)


def _load_picks(
    connection: duckdb.DuckDBPyConnection,
    league_season_id: str,
) -> tuple[_Pick, ...]:
    rows = connection.execute(
        """
        SELECT overall_pick, round, draft_slot, team_id, player_id, position
        FROM draft_picks
        WHERE league_season_id = ?
        ORDER BY overall_pick
        """,
        [league_season_id],
    ).fetchall()
    return tuple(
        _Pick(
            overall_pick=int(row[0]),
            round=int(row[1]),
            draft_slot=int(row[2]),
            team_id=str(row[3]),
            player_id=None if row[4] is None else str(row[4]),
            position=_position(str(row[5] or "UNKNOWN")),
        )
        for row in rows
    )


def _group_team_picks(picks: tuple[_Pick, ...]) -> dict[str, tuple[_Pick, ...]]:
    grouped: dict[str, list[_Pick]] = defaultdict(list)
    for pick in picks:
        grouped[pick.team_id].append(pick)
    return {team: tuple(rows) for team, rows in grouped.items()}


def _feature_payload(league: _LeagueRecord, picks: tuple[_Pick, ...]) -> dict[str, Any]:
    position_counts = Counter(pick.position for pick in picks)
    by_round: dict[str, dict[str, int]] = defaultdict(dict)
    for round_number in sorted({pick.round for pick in picks}):
        counts = Counter(pick.position for pick in picks if pick.round == round_number)
        by_round[str(round_number)] = dict(sorted(counts.items()))
    total_picks = league.team_count * league.rules.draft.rounds
    draft_capital: dict[str, int] = defaultdict(int)
    for pick in picks:
        draft_capital[pick.position] += total_picks + 1 - pick.overall_pick
    first_round = {
        position: min(
            (pick.round for pick in picks if pick.position == position),
            default=None,
        )
        for position in ("QB", "RB", "WR", "TE")
    }
    counts_through_round = {
        str(cutoff): {
            position: sum(
                pick.position == position and pick.round <= cutoff for pick in picks
            )
            for position in ("RB", "WR")
        }
        for cutoff in (3, 5, 8, 10)
    }
    roster = [
        RosterPlayer(
            player_id=pick.player_id or f"pick:{pick.overall_pick}",
            position=pick.position,
            projected_points=0.0,
        )
        for pick in picks
    ]
    assignment = assign_roster(roster, league.rules)
    bench_depth = Counter(player.position for player in assignment.bench)
    direct_demand = dict(league.rules.starters)
    flex_demand = {
        slot.name: {"count": slot.count, "eligible": list(slot.eligible)}
        for slot in league.rules.flex_slots
    }
    return {
        "feature_version": FEATURE_VERSION,
        "position_picks_by_round": dict(sorted(by_round.items(), key=lambda item: int(item[0]))),
        "position_pick_counts": dict(sorted(position_counts.items())),
        "cumulative_draft_capital": dict(sorted(draft_capital.items())),
        "first_position_round": first_round,
        "rb_wr_counts_through_round": counts_through_round,
        "starter_coverage": assignment.starter_coverage,
        "starter_slots_filled": len(assignment.starters),
        "starter_slot_count": assignment.starter_slot_count,
        "bench_depth": dict(sorted(bench_depth.items())),
        "unassigned_roster_rows": len(assignment.unassigned),
        "ruleset_starter_demand": {
            "direct": direct_demand,
            "flex": flex_demand,
        },
        "value_vs_source_adp": {"status": "unavailable", "reason": "no_cutoff_safe_adp_link"},
        "projected_vorp": {
            "status": "unavailable",
            "reason": "no_rules_compatible_historical_projection",
        },
        "roster_volatility_upside": {
            "status": "unavailable",
            "reason": "no_cutoff_safe_historical_intervals",
        },
        "bye_week_concentration": {
            "status": "unavailable",
            "reason": "no_time_valid_historical_bye_source",
        },
    }


def _draft_only_metrics(
    config: AppConfig,
    league: _LeagueRecord,
    team_picks: dict[str, tuple[_Pick, ...]],
) -> tuple[list[_MetricRow], list[HistoryBuildIssue]]:
    issues: list[HistoryBuildIssue] = []
    all_picks = tuple(pick for picks in team_picks.values() for pick in picks)
    resolved = sum(pick.player_id is not None for pick in all_picks)
    mapping_rate = float(resolved / len(all_picks)) if all_picks else 0.0
    unsupported_slots = set(league.rules.starters) - SUPPORTED_SCORING_POSITIONS
    unsupported_picks = {pick.position for pick in all_picks} - SUPPORTED_SCORING_POSITIONS
    if unsupported_slots or unsupported_picks:
        status = "unsupported_positions"
        rows = [
            _empty_metric(league, team_id, picks, status)
            for team_id, picks in sorted(team_picks.items())
        ]
        issues.append(
            HistoryBuildIssue(
                code=status,
                message=(
                    "Draft-only scoring supports QB/RB/WR/TE only; found slots/picks "
                    f"{sorted(unsupported_slots | unsupported_picks)}."
                ),
                league_season_id=league.league_season_id,
            )
        )
        return rows, issues
    if mapping_rate < 1:
        rows = [
            _empty_metric(league, team_id, picks, "identity_mapping_required")
            for team_id, picks in sorted(team_picks.items())
        ]
        issues.append(
            HistoryBuildIssue(
                code="identity_mapping_required",
                message=(
                    f"Draft-only scoring requires reviewed IDs for every pick; coverage is "
                    f"{mapping_rate:.1%}."
                ),
                league_season_id=league.league_season_id,
            )
        )
        return rows, issues
    player_ids = sorted({str(pick.player_id) for pick in all_picks if pick.player_id})
    weekly = _load_weekly_stats(config, league, player_ids)
    if not weekly.rows:
        rows = [
            _empty_metric(league, team_id, picks, "weekly_data_unavailable")
            for team_id, picks in sorted(team_picks.items())
        ]
        issues.append(
            HistoryBuildIssue(
                code="weekly_data_unavailable",
                message=f"No regular-season weekly stats were found for {league.season}.",
                league_season_id=league.league_season_id,
            )
        )
        return rows, issues
    if not weekly.complete_weeks:
        rows = [
            _empty_metric(league, team_id, picks, "weekly_data_incomplete")
            for team_id, picks in sorted(team_picks.items())
        ]
        missing_weeks = sorted(set(weekly.expected_weeks) - set(weekly.covered_weeks))
        issues.append(
            HistoryBuildIssue(
                code="weekly_data_incomplete",
                message=(
                    "Draft-only scoring requires continuous regular-season source coverage; "
                    f"missing weeks are {missing_weeks}."
                ),
                league_season_id=league.league_season_id,
            )
        )
        return rows, issues
    missing_players = sorted(set(player_ids) - weekly.covered_player_ids)
    if missing_players:
        rows = [
            _empty_metric(league, team_id, picks, "weekly_player_coverage_incomplete")
            for team_id, picks in sorted(team_picks.items())
        ]
        issues.append(
            HistoryBuildIssue(
                code="weekly_player_coverage_incomplete",
                message=(
                    "Draft-only scoring cannot distinguish all-season zero production from "
                    f"missing evidence for {len(missing_players)} drafted player(s)."
                ),
                league_season_id=league.league_season_id,
            )
        )
        return rows, issues
    weeks = list(weekly.expected_weeks)
    stats_by_key = {(int(row[0]), str(row[1])): row for row in weekly.rows}
    weekly_fingerprint = _weekly_fingerprint(list(weekly.rows))
    results: list[_MetricRow] = []
    for team_id, picks in sorted(team_picks.items()):
        total = 0.0
        starter_games = 0
        starter_slot_weeks = 0
        unfilled = 0
        for week in weeks:
            roster: list[RosterPlayer] = []
            active_roster: list[RosterPlayer] = []
            for pick in picks:
                player_id = str(pick.player_id)
                row = stats_by_key.get((week, player_id))
                points = _score_week(row, pick.position, league.rules.scoring)
                player = RosterPlayer(player_id, pick.position, points)
                roster.append(player)
                if row is not None and _active(row):
                    active_roster.append(player)
            assignment = assign_roster(roster, league.rules)
            active_assignment = assign_roster(active_roster, league.rules)
            total += assignment.starter_value
            starter_slot_weeks += assignment.starter_slot_count
            unfilled += assignment.starter_slot_count - len(active_assignment.starters)
            active_ids = {item.player.player_id for item in active_assignment.starters}
            starter_games += sum(
                item.player.player_id in active_ids for item in assignment.starters
            )
        payload = {
            "metric_version": METRIC_VERSION,
            "definition": "original_drafted_players_only",
            "best_ball_definition": "sum_of_weekly_optimal_drafted_only_lineups",
            "weeks_scored": len(weeks),
            "optimal_lineup_points": total,
            "best_ball_points": total,
            "drafted_player_starter_games": starter_games,
            "starter_slot_weeks": starter_slot_weeks,
            "unfilled_starter_slot_weeks": unfilled,
            "replacement_burden_label": "unfilled drafted-only starter slots; cause unknown",
            "mapping_coverage": 1.0,
            "points_percentile": None,
        }
        results.append(
            _MetricRow(
                league_season_id=league.league_season_id,
                team_id=team_id,
                package_fingerprint=league.package_fingerprint,
                weekly_data_fingerprint=weekly_fingerprint,
                scoring_fingerprint=league.rules.scoring_fingerprint(),
                weeks_scored=len(weeks),
                optimal_lineup_points=total,
                best_ball_points=total,
                drafted_starter_games=starter_games,
                starter_slot_weeks=starter_slot_weeks,
                unfilled_starter_slot_weeks=unfilled,
                points_percentile=None,
                mapping_coverage=1.0,
                status="ready",
                metrics_payload=payload,
            )
        )
    return results, issues


def _empty_metric(
    league: _LeagueRecord,
    team_id: str,
    picks: tuple[_Pick, ...],
    status: str,
) -> _MetricRow:
    coverage = (
        sum(pick.player_id is not None for pick in picks) / len(picks) if picks else 0.0
    )
    payload = {
        "metric_version": METRIC_VERSION,
        "status": status,
        "mapping_coverage": coverage,
        "best_ball_definition": "sum_of_weekly_optimal_drafted_only_lineups",
    }
    return _MetricRow(
        league_season_id=league.league_season_id,
        team_id=team_id,
        package_fingerprint=league.package_fingerprint,
        weekly_data_fingerprint="unavailable",
        scoring_fingerprint=league.rules.scoring_fingerprint(),
        weeks_scored=0,
        optimal_lineup_points=None,
        best_ball_points=None,
        drafted_starter_games=None,
        starter_slot_weeks=None,
        unfilled_starter_slot_weeks=None,
        points_percentile=None,
        mapping_coverage=coverage,
        status=status,
        metrics_payload=payload,
    )


def _load_weekly_stats(
    config: AppConfig,
    league: _LeagueRecord,
    player_ids: list[str],
) -> _WeeklyEvidence:
    if not player_ids:
        return _WeeklyEvidence((), (), (), frozenset())
    placeholders = ",".join("?" for _ in player_ids)
    cutoff = league.playoff_start_week
    predicate = "AND week < ?" if cutoff is not None else ""
    selected_parameters: list[object] = [league.season, *player_ids]
    season_parameters: list[object] = [league.season]
    if cutoff is not None:
        selected_parameters.append(cutoff)
        season_parameters.append(cutoff)
    warehouse = config.resolve(config.paths.warehouse)
    with duckdb.connect(str(warehouse), read_only=True) as connection:
        stat_rows = connection.execute(
            f"""
            SELECT week, player_id, position, games_active, games_played,
                   passing_yards, passing_tds, interceptions,
                   rushing_yards, rushing_tds, receiving_yards, receptions,
                   receiving_tds, two_point_conversions, fumbles_lost
            FROM player_week_stats
            WHERE season = ? AND player_id IN ({placeholders})
              AND coalesce(season_type, 'REG') = 'REG'
              AND source = 'nflverse'
              {predicate}
            ORDER BY week, player_id
            """,
            selected_parameters,
        ).fetchall()
        participation_rows = connection.execute(
            f"""
            SELECT week, player_id, any_value(position),
                   max(
                       CASE WHEN coalesce(offense_snaps, 0)
                                      + coalesce(defense_snaps, 0)
                                      + coalesce(special_teams_snaps, 0) > 0
                            THEN 1 ELSE 0 END
                   ) AS games_active
            FROM player_game_participation
            WHERE season = ? AND player_id IN ({placeholders})
              AND coalesce(season_type, game_type, 'REG') = 'REG'
              AND source = 'nflverse'
              {predicate}
            GROUP BY week, player_id
            ORDER BY week, player_id
            """,
            selected_parameters,
        ).fetchall()
        covered_stat_weeks = connection.execute(
            f"""
            SELECT DISTINCT week
            FROM player_week_stats
            WHERE season = ? AND coalesce(season_type, 'REG') = 'REG'
              AND source = 'nflverse' {predicate}
            """,
            season_parameters,
        ).fetchall()
        covered_participation_weeks = connection.execute(
            f"""
            SELECT DISTINCT week
            FROM player_game_participation
            WHERE season = ? AND coalesce(season_type, game_type, 'REG') = 'REG'
              AND source = 'nflverse' {predicate}
            """,
            season_parameters,
        ).fetchall()

    combined: dict[tuple[int, str], list[Any]] = {
        (int(row[0]), str(row[1])): list(row) for row in stat_rows
    }
    for stat_values in combined.values():
        stat_values[3] = max(_number(stat_values[3]), _number(stat_values[4]))
    for row in participation_rows:
        key = (int(row[0]), str(row[1]))
        participation_active = _number(row[3])
        existing = combined.get(key)
        if existing is None:
            combined[key] = [
                key[0],
                key[1],
                row[2],
                participation_active,
                None,
                0.0,
                0.0,
                0.0,
                0.0,
                0.0,
                0.0,
                0.0,
                0.0,
                0.0,
                0.0,
            ]
            continue
        existing[3] = max(_number(existing[3]), _number(existing[4]), participation_active)

    covered_weeks = tuple(
        sorted(
            {
                int(row[0])
                for row in (*covered_stat_weeks, *covered_participation_weeks)
            }
        )
    )
    if cutoff is not None:
        expected_weeks = tuple(range(1, cutoff))
    elif covered_weeks:
        expected_weeks = tuple(range(1, max(covered_weeks) + 1))
    else:
        expected_weeks = ()
    rows = tuple(tuple(row) for _, row in sorted(combined.items()))
    return _WeeklyEvidence(
        rows=rows,
        expected_weeks=expected_weeks,
        covered_weeks=covered_weeks,
        covered_player_ids=frozenset(key[1] for key in combined),
    )


def _score_week(row: tuple[Any, ...] | None, position: str, rules: ScoringRules) -> float:
    if row is None:
        return 0.0
    stats = PlayerStatLine(
        position=_position(str(row[2] or position)),
        passing_yards=_number(row[5]),
        passing_tds=_number(row[6]),
        interceptions=_number(row[7]),
        rushing_yards=_number(row[8]),
        rushing_tds=_number(row[9]),
        receiving_yards=_number(row[10]),
        receptions=_number(row[11]),
        receiving_tds=_number(row[12]),
        two_point_conversions=_number(row[13]),
        fumbles_lost=_number(row[14]),
    )
    return score_player(stats, rules)


def _active(row: tuple[Any, ...]) -> bool:
    active = row[3] if row[3] is not None else row[4]
    return _number(active) > 0


def _with_percentiles(rows: list[_MetricRow]) -> list[_MetricRow]:
    grouped: dict[str, list[_MetricRow]] = defaultdict(list)
    for row in rows:
        grouped[row.league_season_id].append(row)
    output: list[_MetricRow] = []
    for league_rows in grouped.values():
        ready = [row for row in league_rows if row.optimal_lineup_points is not None]
        for row in league_rows:
            percentile = None
            if row.optimal_lineup_points is not None and ready:
                below = sum(
                    float(other.optimal_lineup_points) < row.optimal_lineup_points
                    for other in ready
                    if other.optimal_lineup_points is not None
                )
                equal = sum(
                    float(other.optimal_lineup_points) == row.optimal_lineup_points
                    for other in ready
                    if other.optimal_lineup_points is not None
                )
                percentile = (below + 0.5 * equal) / len(ready)
            payload = {**row.metrics_payload, "points_percentile": percentile}
            output.append(replace(row, points_percentile=percentile, metrics_payload=payload))
    return output


def _upsert_feature(
    connection: duckdb.DuckDBPyConnection,
    row: tuple[str, str, str, str, str, dict[str, Any]],
    built_at: datetime,
) -> None:
    payload = _canonical_json(row[5])
    existing = connection.execute(
        """
        SELECT package_fingerprint, ruleset_fingerprint, feature_payload
        FROM roster_construction_features
        WHERE league_season_id = ? AND team_id = ? AND feature_version = ?
        """,
        list(row[:3]),
    ).fetchone()
    values = [*row[:5], payload, built_at]
    if existing is None:
        connection.execute(
            "INSERT INTO roster_construction_features VALUES (?, ?, ?, ?, ?, ?, ?)",
            values,
        )
    elif (str(existing[0]), str(existing[1]), str(existing[2])) != (row[3], row[4], payload):
        connection.execute(
            """
            UPDATE roster_construction_features
            SET package_fingerprint = ?, ruleset_fingerprint = ?, feature_payload = ?,
                built_at = ?
            WHERE league_season_id = ? AND team_id = ? AND feature_version = ?
            """,
            [row[3], row[4], payload, built_at, *row[:3]],
        )


def _upsert_metric(
    connection: duckdb.DuckDBPyConnection,
    row: _MetricRow,
    built_at: datetime,
) -> None:
    values: list[object] = [
        row.league_season_id,
        row.team_id,
        METRIC_VERSION,
        row.package_fingerprint,
        row.weekly_data_fingerprint,
        row.scoring_fingerprint,
        row.weeks_scored,
        row.optimal_lineup_points,
        row.best_ball_points,
        row.drafted_starter_games,
        row.starter_slot_weeks,
        row.unfilled_starter_slot_weeks,
        row.points_percentile,
        row.mapping_coverage,
        row.status,
        _canonical_json(row.metrics_payload),
        built_at,
    ]
    existing = connection.execute(
        """
        SELECT package_fingerprint, weekly_data_fingerprint, scoring_fingerprint,
               weeks_scored, optimal_lineup_points, best_ball_points,
               drafted_starter_games, starter_slot_weeks, unfilled_starter_slot_weeks,
               points_percentile, mapping_coverage, status, metrics_payload
        FROM draft_only_team_metrics
        WHERE league_season_id = ? AND team_id = ? AND metric_version = ?
        """,
        values[:3],
    ).fetchone()
    comparable = tuple(values[3:16])
    if existing is None:
        connection.execute(
            "INSERT INTO draft_only_team_metrics VALUES "
            "(?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
            values,
        )
    elif tuple(existing) != comparable:
        connection.execute(
            """
            UPDATE draft_only_team_metrics SET
                package_fingerprint = ?, weekly_data_fingerprint = ?,
                scoring_fingerprint = ?, weeks_scored = ?, optimal_lineup_points = ?,
                best_ball_points = ?, drafted_starter_games = ?, starter_slot_weeks = ?,
                unfilled_starter_slot_weeks = ?, points_percentile = ?,
                mapping_coverage = ?, status = ?, metrics_payload = ?, built_at = ?
            WHERE league_season_id = ? AND team_id = ? AND metric_version = ?
            """,
            [*values[3:16], built_at, *values[:3]],
        )


def _verify_build_rows(
    connection: duckdb.DuckDBPyConnection,
    features: list[tuple[str, str, str, str, str, dict[str, Any]]],
    metrics: list[_MetricRow],
) -> None:
    feature_count = connection.execute(
        "SELECT count(*) FROM roster_construction_features WHERE feature_version = ?",
        [FEATURE_VERSION],
    ).fetchone()
    metric_count = connection.execute(
        "SELECT count(*) FROM draft_only_team_metrics WHERE metric_version = ?",
        [METRIC_VERSION],
    ).fetchone()
    if feature_count is None or int(feature_count[0]) < len(features):
        raise RuntimeError("Roster feature row reconciliation failed.")
    if metric_count is None or int(metric_count[0]) < len(metrics):
        raise RuntimeError("Draft-only metric row reconciliation failed.")


def _weekly_fingerprint(rows: list[tuple[Any, ...]]) -> str:
    payload = [[_json_scalar(value) for value in row] for row in rows]
    return hashlib.sha256(_canonical_json(payload).encode("utf-8")).hexdigest()


def _build_fingerprint(
    features: list[tuple[str, str, str, str, str, dict[str, Any]]],
    metrics: list[_MetricRow],
) -> str:
    payload = {
        "feature_version": FEATURE_VERSION,
        "metric_version": METRIC_VERSION,
        "features": [
            [*row[:5], row[5]] for row in sorted(features, key=lambda item: item[:3])
        ],
        "metrics": [
            {
                "league_season_id": row.league_season_id,
                "team_id": row.team_id,
                "status": row.status,
                "payload": row.metrics_payload,
            }
            for row in sorted(metrics, key=lambda item: (item.league_season_id, item.team_id))
        ],
    }
    return hashlib.sha256(_canonical_json(payload).encode("utf-8")).hexdigest()


def _position(value: str) -> str:
    position = value.strip().upper()
    return {"PK": "K", "D/ST": "DEF", "DST": "DEF"}.get(position, position)


def _number(value: object) -> float:
    if value is None:
        return 0.0
    if isinstance(value, (int, float)):
        return float(value)
    return float(str(value))


def _json_scalar(value: object) -> object:
    if isinstance(value, datetime):
        return value.isoformat()
    return value


def _canonical_json(value: object) -> str:
    return json.dumps(
        value,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=True,
        allow_nan=False,
    )
