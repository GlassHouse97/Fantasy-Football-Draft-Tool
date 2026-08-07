"""Read-only Phase 8 league-history coverage, reports, and training gates."""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any

import duckdb
import yaml
from pydantic import BaseModel, ConfigDict, Field

from fantasy_draft_ai.config import AppConfig

DEFAULT_GATE_PATH = Path("configs/league_history_gate.yaml")


class LeagueHistoryGateConfig(BaseModel):
    """Conservative, versioned minimum evidence for outcome-model eligibility."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    schema_version: str = Field(pattern=r"^league-history-gate-v\d+$")
    minimum_league_seasons: int = Field(ge=1)
    minimum_team_seasons: int = Field(ge=1)
    minimum_distinct_seasons: int = Field(ge=3)
    minimum_validation_league_seasons: int = Field(ge=1)
    minimum_test_league_seasons: int = Field(ge=1)
    minimum_positive_examples: int = Field(ge=1)
    minimum_negative_examples: int = Field(ge=1)
    minimum_complete_draft_rate: float = Field(ge=0, le=1)
    minimum_complete_outcome_rate: float = Field(ge=0, le=1)
    minimum_mapped_pick_rate: float = Field(ge=0, le=1)
    gradient_boosting_minimum_league_seasons: int = Field(ge=1)
    gradient_boosting_minimum_team_seasons: int = Field(ge=1)
    gradient_boosting_minimum_class_examples: int = Field(ge=1)

    def fingerprint(self) -> str:
        payload = json.dumps(
            self.model_dump(mode="json"),
            sort_keys=True,
            separators=(",", ":"),
            ensure_ascii=True,
        )
        return hashlib.sha256(payload.encode("utf-8")).hexdigest()


@dataclass(frozen=True)
class HistoryPackageSummary:
    package_fingerprint: str
    schema_version: str
    status: str
    league_count: int
    rules_rows: int
    pick_rows: int
    outcome_rows: int
    unresolved_player_rows: int
    imported_at: datetime
    quality_report: dict[str, Any]

    def as_dict(self) -> dict[str, object]:
        return {
            "package_fingerprint": self.package_fingerprint,
            "schema_version": self.schema_version,
            "status": self.status,
            "league_count": self.league_count,
            "rules_rows": self.rules_rows,
            "pick_rows": self.pick_rows,
            "outcome_rows": self.outcome_rows,
            "unresolved_player_rows": self.unresolved_player_rows,
            "imported_at": self.imported_at.isoformat(),
            "quality_report": self.quality_report,
        }


@dataclass(frozen=True)
class LeagueHistoryCoverage:
    packages: int = 0
    loaded_packages: int = 0
    rejected_packages: int = 0
    league_seasons: int = 0
    distinct_seasons: int = 0
    rulesets: int = 0
    team_seasons: int = 0
    draft_picks: int = 0
    resolved_draft_picks: int = 0
    complete_drafts: int = 0
    complete_outcomes: int = 0
    analysis_ready_leagues: int = 0
    feature_rows: int = 0
    draft_metric_rows: int = 0
    points_target_rows: int = 0
    playoff_positive: int = 0
    playoff_negative: int = 0
    champion_positive: int = 0
    champion_negative: int = 0
    validation_league_seasons: int = 0
    test_league_seasons: int = 0

    @property
    def mapped_pick_rate(self) -> float:
        return _rate(self.resolved_draft_picks, self.draft_picks)

    @property
    def complete_draft_rate(self) -> float:
        return _rate(self.complete_drafts, self.league_seasons)

    @property
    def complete_outcome_rate(self) -> float:
        return _rate(self.complete_outcomes, self.league_seasons)

    def as_dict(self) -> dict[str, object]:
        payload = dict(self.__dict__)
        payload.update(
            {
                "mapped_pick_rate": self.mapped_pick_rate,
                "complete_draft_rate": self.complete_draft_rate,
                "complete_outcome_rate": self.complete_outcome_rate,
            }
        )
        return payload


@dataclass(frozen=True)
class GateCriterion:
    code: str
    label: str
    actual: float
    required: float
    passed: bool
    explanation: str

    def as_dict(self) -> dict[str, object]:
        return dict(self.__dict__)


@dataclass(frozen=True)
class LeagueHistoryTrainingGate:
    config_fingerprint: str
    criteria: tuple[GateCriterion, ...]
    points_percentile_ready: bool
    playoff_ready: bool
    championship_ready: bool
    gradient_boosting_ready: bool

    @property
    def ready(self) -> bool:
        return self.points_percentile_ready and self.playoff_ready and self.championship_ready

    @property
    def status(self) -> str:
        return "eligible_not_trained" if self.ready else "locked_insufficient_data"

    @property
    def blockers(self) -> tuple[str, ...]:
        return tuple(item.explanation for item in self.criteria if not item.passed)

    def as_dict(self) -> dict[str, object]:
        return {
            "config_fingerprint": self.config_fingerprint,
            "status": self.status,
            "ready": self.ready,
            "points_percentile_ready": self.points_percentile_ready,
            "playoff_ready": self.playoff_ready,
            "championship_ready": self.championship_ready,
            "gradient_boosting_ready": self.gradient_boosting_ready,
            "blockers": list(self.blockers),
            "criteria": [item.as_dict() for item in self.criteria],
        }


@dataclass(frozen=True)
class HistoryTeamSummary:
    league_season_id: str
    season: int
    team_id: str
    wins: float | None
    losses: float | None
    points_for: float | None
    made_playoffs: bool | None
    final_place: int | None
    is_champion: bool | None
    draft_metric_status: str | None
    drafted_only_points: float | None
    drafted_only_percentile: float | None
    mapping_coverage: float | None
    feature_payload: dict[str, Any] | None

    def as_dict(self) -> dict[str, object]:
        return {
            "league_season_id": self.league_season_id,
            "season": self.season,
            "team_id": self.team_id,
            "wins": self.wins,
            "losses": self.losses,
            "points_for": self.points_for,
            "made_playoffs": self.made_playoffs,
            "final_place": self.final_place,
            "is_champion": self.is_champion,
            "draft_metric_status": self.draft_metric_status,
            "drafted_only_points": self.drafted_only_points,
            "drafted_only_percentile": self.drafted_only_percentile,
            "mapping_coverage": self.mapping_coverage,
            "feature_payload": self.feature_payload,
        }


@dataclass(frozen=True)
class LeagueHistorySnapshot:
    available: bool
    issue: str | None
    packages: tuple[HistoryPackageSummary, ...]
    teams: tuple[HistoryTeamSummary, ...]
    coverage: LeagueHistoryCoverage
    gate: LeagueHistoryTrainingGate
    next_action: str

    def as_dict(self) -> dict[str, object]:
        return {
            "available": self.available,
            "issue": self.issue,
            "packages": [item.as_dict() for item in self.packages],
            "teams": [item.as_dict() for item in self.teams],
            "coverage": self.coverage.as_dict(),
            "gate": self.gate.as_dict(),
            "next_action": self.next_action,
        }


def load_league_history_gate_config(
    config: AppConfig,
    path: Path | None = None,
) -> LeagueHistoryGateConfig:
    actual = path or config.project_root / DEFAULT_GATE_PATH
    with actual.open(encoding="utf-8") as handle:
        payload = yaml.safe_load(handle) or {}
    return LeagueHistoryGateConfig.model_validate(payload)


def evaluate_league_history_gate(
    coverage: LeagueHistoryCoverage,
    gate_config: LeagueHistoryGateConfig,
) -> LeagueHistoryTrainingGate:
    common = (
        _criterion(
            "league_seasons",
            "Analysis-ready league-seasons",
            coverage.analysis_ready_leagues,
            gate_config.minimum_league_seasons,
        ),
        _criterion(
            "team_seasons",
            "Team-seasons with outcomes",
            coverage.team_seasons,
            gate_config.minimum_team_seasons,
        ),
        _criterion(
            "distinct_seasons",
            "Distinct completed seasons",
            coverage.distinct_seasons,
            gate_config.minimum_distinct_seasons,
        ),
        _criterion(
            "validation_leagues",
            "League-seasons in the validation season",
            coverage.validation_league_seasons,
            gate_config.minimum_validation_league_seasons,
        ),
        _criterion(
            "test_leagues",
            "League-seasons in the untouched test season",
            coverage.test_league_seasons,
            gate_config.minimum_test_league_seasons,
        ),
        _rate_criterion(
            "complete_drafts",
            "Complete-draft coverage",
            coverage.complete_draft_rate,
            gate_config.minimum_complete_draft_rate,
        ),
        _rate_criterion(
            "complete_outcomes",
            "Complete-outcome coverage",
            coverage.complete_outcome_rate,
            gate_config.minimum_complete_outcome_rate,
        ),
        _rate_criterion(
            "mapped_picks",
            "Reviewed player-ID coverage",
            coverage.mapped_pick_rate,
            gate_config.minimum_mapped_pick_rate,
        ),
        _criterion(
            "roster_features",
            "Team-seasons with roster-construction features",
            coverage.feature_rows,
            gate_config.minimum_team_seasons,
        ),
    )
    points = (
        _criterion(
            "points_targets",
            "Team-seasons with points-for target evidence",
            coverage.points_target_rows,
            gate_config.minimum_team_seasons,
        ),
    )
    playoff = (
        _criterion(
            "playoff_positive",
            "Playoff positive examples",
            coverage.playoff_positive,
            gate_config.minimum_positive_examples,
        ),
        _criterion(
            "playoff_negative",
            "Playoff negative examples",
            coverage.playoff_negative,
            gate_config.minimum_negative_examples,
        ),
    )
    champion = (
        _criterion(
            "champion_positive",
            "Champion positive examples",
            coverage.champion_positive,
            gate_config.minimum_positive_examples,
        ),
        _criterion(
            "champion_negative",
            "Champion negative examples",
            coverage.champion_negative,
            gate_config.minimum_negative_examples,
        ),
    )
    common_ready = all(item.passed for item in common)
    points_ready = common_ready and all(item.passed for item in points)
    playoff_ready = common_ready and all(item.passed for item in playoff)
    championship_ready = common_ready and all(item.passed for item in champion)
    gradient_ready = (
        common_ready
        and all(item.passed for item in (*playoff, *champion))
        and coverage.analysis_ready_leagues
        >= gate_config.gradient_boosting_minimum_league_seasons
        and coverage.team_seasons >= gate_config.gradient_boosting_minimum_team_seasons
        and coverage.feature_rows >= gate_config.gradient_boosting_minimum_team_seasons
        and min(
            coverage.playoff_positive,
            coverage.playoff_negative,
            coverage.champion_positive,
            coverage.champion_negative,
        )
        >= gate_config.gradient_boosting_minimum_class_examples
    )
    return LeagueHistoryTrainingGate(
        config_fingerprint=gate_config.fingerprint(),
        criteria=(*common, *points, *playoff, *champion),
        points_percentile_ready=points_ready,
        playoff_ready=playoff_ready,
        championship_ready=championship_ready,
        gradient_boosting_ready=gradient_ready,
    )


def load_league_history_snapshot(
    config: AppConfig,
    *,
    gate_path: Path | None = None,
) -> LeagueHistorySnapshot:
    """Read validated history and return truthful availability without training."""

    gate_config = load_league_history_gate_config(config, gate_path)
    warehouse = config.resolve(config.paths.warehouse)
    empty = LeagueHistoryCoverage()
    if not warehouse.is_file():
        gate = evaluate_league_history_gate(empty, gate_config)
        return LeagueHistorySnapshot(
            available=False,
            issue="Canonical warehouse is not initialized.",
            packages=(),
            teams=(),
            coverage=empty,
            gate=gate,
            next_action="Initialize the warehouse, then download the league-history template.",
        )
    try:
        with duckdb.connect(str(warehouse), read_only=True) as connection:
            if not _table_exists(connection, "league_history_imports"):
                gate = evaluate_league_history_gate(empty, gate_config)
                return LeagueHistorySnapshot(
                    available=False,
                    issue="Phase 8 warehouse tables have not been initialized.",
                    packages=(),
                    teams=(),
                    coverage=empty,
                    gate=gate,
                    next_action="Run `fantasy-draft data init-warehouse` before importing history.",
                )
            packages = _load_packages(connection)
            coverage = _load_coverage(connection, packages)
            teams = _load_teams(connection)
    except (duckdb.Error, OSError, TypeError, ValueError, json.JSONDecodeError) as exc:
        gate = evaluate_league_history_gate(empty, gate_config)
        return LeagueHistorySnapshot(
            available=False,
            issue=f"League-history evidence could not be read safely: {exc}",
            packages=(),
            teams=(),
            coverage=empty,
            gate=gate,
            next_action="Run the data audit and inspect the league-history quality report.",
        )
    gate = evaluate_league_history_gate(coverage, gate_config)
    return LeagueHistorySnapshot(
        available=bool(coverage.loaded_packages),
        issue=None,
        packages=packages,
        teams=teams,
        coverage=coverage,
        gate=gate,
        next_action=_next_action(coverage, gate),
    )


def _load_packages(
    connection: duckdb.DuckDBPyConnection,
) -> tuple[HistoryPackageSummary, ...]:
    rows = connection.execute(
        """
        SELECT package_fingerprint, schema_version, status, league_count,
               rules_rows, pick_rows, outcome_rows, unresolved_player_rows,
               imported_at, quality_report
        FROM league_history_imports
        ORDER BY imported_at DESC, package_fingerprint
        """
    ).fetchall()
    return tuple(
        HistoryPackageSummary(
            package_fingerprint=str(row[0]),
            schema_version=str(row[1]),
            status=str(row[2]),
            league_count=int(row[3]),
            rules_rows=int(row[4]),
            pick_rows=int(row[5]),
            outcome_rows=int(row[6]),
            unresolved_player_rows=int(row[7]),
            imported_at=row[8],
            quality_report=json.loads(str(row[9])),
        )
        for row in rows
    )


def _load_coverage(
    connection: duckdb.DuckDBPyConnection,
    packages: tuple[HistoryPackageSummary, ...],
) -> LeagueHistoryCoverage:
    league = connection.execute(
        """
        SELECT count(*), count(DISTINCT season), count(DISTINCT ruleset_fingerprint),
               count(*) FILTER (WHERE draft_complete),
               count(*) FILTER (WHERE outcomes_complete),
               count(*) FILTER (WHERE analysis_ready)
        FROM league_history_leagues
        """
    ).fetchone()
    picks = connection.execute(
        """
        SELECT count(*), count(*) FILTER (WHERE player_id IS NOT NULL)
        FROM draft_picks
        WHERE source_dataset_id IS NOT NULL
        """
    ).fetchone()
    outcomes = connection.execute(
        """
        SELECT count(*),
               count(*) FILTER (WHERE points_for IS NOT NULL),
               count(*) FILTER (WHERE made_playoffs),
               count(*) FILTER (WHERE made_playoffs = false),
               count(*) FILTER (WHERE is_champion),
               count(*) FILTER (WHERE is_champion = false)
        FROM team_outcomes
        WHERE source_dataset_id IS NOT NULL
        """
    ).fetchone()
    feature_rows = _count_rows(connection, "roster_construction_features")
    metric_rows = _count_rows(connection, "draft_only_team_metrics", "status = 'ready'")
    season_counts = connection.execute(
        """
        SELECT season, count(*)
        FROM league_history_leagues
        GROUP BY season
        ORDER BY season DESC
        LIMIT 2
        """
    ).fetchall()
    test_leagues = int(season_counts[0][1]) if season_counts else 0
    validation_leagues = int(season_counts[1][1]) if len(season_counts) > 1 else 0
    return LeagueHistoryCoverage(
        packages=len(packages),
        loaded_packages=sum(
            item.status in {"imported", "loaded", "already_loaded"} for item in packages
        ),
        rejected_packages=sum(item.status == "rejected" for item in packages),
        league_seasons=int(league[0]) if league else 0,
        distinct_seasons=int(league[1]) if league else 0,
        rulesets=int(league[2]) if league else 0,
        team_seasons=int(outcomes[0]) if outcomes else 0,
        draft_picks=int(picks[0]) if picks else 0,
        resolved_draft_picks=int(picks[1]) if picks else 0,
        complete_drafts=int(league[3]) if league else 0,
        complete_outcomes=int(league[4]) if league else 0,
        analysis_ready_leagues=int(league[5]) if league else 0,
        feature_rows=feature_rows,
        draft_metric_rows=metric_rows,
        points_target_rows=int(outcomes[1]) if outcomes else 0,
        playoff_positive=int(outcomes[2]) if outcomes else 0,
        playoff_negative=int(outcomes[3]) if outcomes else 0,
        champion_positive=int(outcomes[4]) if outcomes else 0,
        champion_negative=int(outcomes[5]) if outcomes else 0,
        validation_league_seasons=validation_leagues,
        test_league_seasons=test_leagues,
    )


def _load_teams(
    connection: duckdb.DuckDBPyConnection,
) -> tuple[HistoryTeamSummary, ...]:
    rows = connection.execute(
        """
        SELECT history.season, outcomes.league_season_id, outcomes.team_id,
               outcomes.wins, outcomes.losses, outcomes.points_for,
               outcomes.made_playoffs, outcomes.final_place, outcomes.is_champion,
               metrics.status, metrics.optimal_lineup_points, metrics.points_percentile,
               metrics.mapping_coverage, features.feature_payload
        FROM team_outcomes AS outcomes
        JOIN league_history_leagues AS history USING (league_season_id)
        LEFT JOIN draft_only_team_metrics AS metrics
          ON metrics.league_season_id = outcomes.league_season_id
         AND metrics.team_id = outcomes.team_id
         AND metrics.metric_version = 'draft-only-v1'
        LEFT JOIN roster_construction_features AS features
          ON features.league_season_id = outcomes.league_season_id
         AND features.team_id = outcomes.team_id
         AND features.feature_version = 'roster-construction-v1'
        WHERE outcomes.source_dataset_id IS NOT NULL
        ORDER BY history.season DESC, outcomes.league_season_id, outcomes.team_id
        """
    ).fetchall()
    return tuple(
        HistoryTeamSummary(
            season=int(row[0]),
            league_season_id=str(row[1]),
            team_id=str(row[2]),
            wins=None if row[3] is None else float(row[3]),
            losses=None if row[4] is None else float(row[4]),
            points_for=None if row[5] is None else float(row[5]),
            made_playoffs=None if row[6] is None else bool(row[6]),
            final_place=None if row[7] is None else int(row[7]),
            is_champion=None if row[8] is None else bool(row[8]),
            draft_metric_status=None if row[9] is None else str(row[9]),
            drafted_only_points=None if row[10] is None else float(row[10]),
            drafted_only_percentile=None if row[11] is None else float(row[11]),
            mapping_coverage=None if row[12] is None else float(row[12]),
            feature_payload=None if row[13] is None else json.loads(str(row[13])),
        )
        for row in rows
    )


def _criterion(
    code: str,
    label: str,
    actual: int,
    required: int,
) -> GateCriterion:
    passed = actual >= required
    return GateCriterion(
        code=code,
        label=label,
        actual=float(actual),
        required=float(required),
        passed=passed,
        explanation=(
            f"{label}: {actual:,}/{required:,}."
            if not passed
            else f"{label}: threshold met ({actual:,}/{required:,})."
        ),
    )


def _rate_criterion(
    code: str,
    label: str,
    actual: float,
    required: float,
) -> GateCriterion:
    passed = actual >= required
    return GateCriterion(
        code=code,
        label=label,
        actual=actual,
        required=required,
        passed=passed,
        explanation=(
            f"{label}: {actual:.1%}/{required:.1%}."
            if not passed
            else f"{label}: threshold met ({actual:.1%}/{required:.1%})."
        ),
    )


def _rate(numerator: int, denominator: int) -> float:
    return float(numerator / denominator) if denominator else 0.0


def _table_exists(connection: duckdb.DuckDBPyConnection, table: str) -> bool:
    row = connection.execute(
        "SELECT count(*) FROM information_schema.tables WHERE table_name = ?",
        [table],
    ).fetchone()
    return bool(row and int(row[0]))


def _count_rows(
    connection: duckdb.DuckDBPyConnection,
    table: str,
    predicate: str | None = None,
) -> int:
    if not _table_exists(connection, table):
        return 0
    query = f"SELECT count(*) FROM {table}"
    if predicate:
        query += f" WHERE {predicate}"
    row = connection.execute(query).fetchone()
    return int(row[0]) if row else 0


def _next_action(
    coverage: LeagueHistoryCoverage,
    gate: LeagueHistoryTrainingGate,
) -> str:
    if not coverage.packages:
        return "Download the v1 template, pseudonymize it, and import one complete season."
    if coverage.rejected_packages:
        return "Open the newest package report and fix its fatal validation errors."
    if coverage.draft_picks and coverage.mapped_pick_rate < 1:
        unresolved = coverage.draft_picks - coverage.resolved_draft_picks
        return f"Review {unresolved:,} unresolved historical player identities."
    if coverage.analysis_ready_leagues and not coverage.feature_rows:
        return "Build the idempotent roster-construction and draft-only reports."
    if not gate.ready:
        return "Keep collecting complete, unbiased league-seasons; outcome training stays locked."
    return "The written data gate passes; independently review evidence before any training work."
