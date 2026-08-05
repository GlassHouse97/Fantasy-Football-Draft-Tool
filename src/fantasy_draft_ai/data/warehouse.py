"""DuckDB warehouse schema and lightweight audit helpers."""

from __future__ import annotations

from collections.abc import Iterator
from contextlib import contextmanager
from pathlib import Path

import duckdb

SCHEMA_SQL = """
CREATE TABLE IF NOT EXISTS players (
    player_id VARCHAR PRIMARY KEY,
    gsis_id VARCHAR,
    pfr_id VARCHAR,
    espn_id VARCHAR,
    sleeper_id VARCHAR,
    yahoo_id VARCHAR,
    mfl_id VARCHAR,
    fleaflicker_id VARCHAR,
    fantasypros_id VARCHAR,
    display_name VARCHAR NOT NULL,
    canonical_position VARCHAR,
    nfl_team VARCHAR,
    birth_date DATE,
    age DOUBLE,
    experience INTEGER,
    rookie_season INTEGER,
    draft_year INTEGER,
    draft_round INTEGER,
    draft_pick INTEGER,
    draft_team VARCHAR,
    height_inches INTEGER,
    weight_lbs INTEGER,
    is_active BOOLEAN,
    mapping_confidence VARCHAR NOT NULL,
    mapping_source VARCHAR NOT NULL,
    identity_source_dataset_id VARCHAR,
    identity_source_as_of TIMESTAMPTZ
);

CREATE TABLE IF NOT EXISTS player_week_stats (
    season INTEGER NOT NULL,
    week INTEGER NOT NULL,
    player_id VARCHAR NOT NULL,
    position VARCHAR,
    season_type VARCHAR,
    game_id VARCHAR,
    nfl_team VARCHAR,
    opponent VARCHAR,
    completions DOUBLE,
    passing_attempts DOUBLE,
    passing_yards DOUBLE,
    passing_tds DOUBLE,
    interceptions DOUBLE,
    rushing_yards DOUBLE,
    rushing_tds DOUBLE,
    receiving_yards DOUBLE,
    receptions DOUBLE,
    receiving_tds DOUBLE,
    targets DOUBLE,
    carries DOUBLE,
    two_point_conversions DOUBLE,
    fumbles_lost DOUBLE,
    special_teams_tds DOUBLE,
    field_goals_made DOUBLE,
    field_goals_attempted DOUBLE,
    extra_points_made DOUBLE,
    extra_points_attempted DOUBLE,
    games_active DOUBLE,
    games_played DOUBLE,
    source VARCHAR NOT NULL,
    as_of TIMESTAMPTZ NOT NULL,
    source_dataset_id VARCHAR,
    PRIMARY KEY (season, week, player_id, source)
);

CREATE TABLE IF NOT EXISTS player_game_participation (
    season INTEGER NOT NULL,
    week INTEGER NOT NULL,
    game_id VARCHAR NOT NULL,
    player_id VARCHAR NOT NULL,
    pfr_game_id VARCHAR,
    pfr_player_id VARCHAR NOT NULL,
    game_type VARCHAR NOT NULL,
    season_type VARCHAR NOT NULL,
    position VARCHAR,
    nfl_team VARCHAR,
    opponent VARCHAR,
    offense_snaps DOUBLE NOT NULL,
    offense_snap_pct DOUBLE,
    defense_snaps DOUBLE NOT NULL,
    defense_snap_pct DOUBLE,
    special_teams_snaps DOUBLE NOT NULL,
    special_teams_snap_pct DOUBLE,
    source VARCHAR NOT NULL,
    as_of TIMESTAMPTZ NOT NULL,
    source_dataset_id VARCHAR NOT NULL,
    PRIMARY KEY (game_id, player_id, source)
);

CREATE TABLE IF NOT EXISTS player_source_mappings (
    source VARCHAR NOT NULL,
    source_player_id VARCHAR NOT NULL,
    player_id VARCHAR NOT NULL,
    mapping_confidence VARCHAR NOT NULL,
    mapping_source VARCHAR NOT NULL,
    review_id VARCHAR NOT NULL,
    reviewed_at TIMESTAMPTZ NOT NULL,
    reviewer VARCHAR NOT NULL,
    notes VARCHAR,
    source_dataset_id VARCHAR NOT NULL,
    PRIMARY KEY (source, source_player_id)
);

CREATE TABLE IF NOT EXISTS identity_review_queue (
    review_id VARCHAR PRIMARY KEY,
    issue_type VARCHAR NOT NULL,
    source VARCHAR NOT NULL,
    source_player_id VARCHAR NOT NULL,
    source_display_name VARCHAR NOT NULL,
    source_position VARCHAR,
    source_nfl_team VARCHAR,
    candidate_player_id VARCHAR,
    candidate_display_name VARCHAR,
    candidate_position VARCHAR,
    candidate_nfl_team VARCHAR,
    reason VARCHAR NOT NULL,
    mapping_confidence VARCHAR NOT NULL,
    status VARCHAR NOT NULL,
    evidence_json JSON NOT NULL,
    evidence_dataset_id VARCHAR NOT NULL,
    first_seen_at TIMESTAMPTZ NOT NULL,
    last_seen_at TIMESTAMPTZ NOT NULL,
    resolution VARCHAR,
    resolved_player_id VARCHAR,
    canonical_display_name_override VARCHAR,
    resolution_note VARCHAR,
    resolved_at TIMESTAMPTZ,
    reviewer VARCHAR,
    resolution_dataset_id VARCHAR,
    is_current BOOLEAN NOT NULL DEFAULT TRUE
);

CREATE TABLE IF NOT EXISTS player_season_features (
    player_id VARCHAR NOT NULL,
    feature_season INTEGER NOT NULL,
    prediction_season INTEGER NOT NULL,
    cutoff_date DATE NOT NULL,
    feature_available_at DATE,
    position VARCHAR NOT NULL,
    feature_payload JSON NOT NULL,
    target_payload JSON,
    source VARCHAR NOT NULL,
    is_synthetic BOOLEAN NOT NULL DEFAULT FALSE,
    feature_version VARCHAR,
    scoring_ruleset_fingerprint VARCHAR,
    source_dataset_ids JSON,
    source_max_stat_season INTEGER,
    source_max_as_of TIMESTAMPTZ,
    data_fingerprint VARCHAR,
    PRIMARY KEY (player_id, prediction_season, source)
);

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

CREATE TABLE IF NOT EXISTS baseline_predictions (
    player_id VARCHAR NOT NULL,
    prediction_season INTEGER NOT NULL,
    position VARCHAR NOT NULL,
    target_name VARCHAR NOT NULL,
    baseline_name VARCHAR NOT NULL,
    predicted_value DOUBLE NOT NULL,
    actual_value DOUBLE,
    experience_group VARCHAR NOT NULL,
    baseline_version VARCHAR NOT NULL,
    feature_data_fingerprint VARCHAR NOT NULL,
    target_data_fingerprint VARCHAR NOT NULL,
    build_fingerprint VARCHAR NOT NULL,
    scoring_ruleset_fingerprint VARCHAR NOT NULL,
    PRIMARY KEY (player_id, prediction_season, target_name, baseline_name)
);

CREATE TABLE IF NOT EXISTS baseline_evaluation_metadata (
    report_fingerprint VARCHAR PRIMARY KEY,
    baseline_version VARCHAR NOT NULL,
    feature_data_fingerprint VARCHAR NOT NULL,
    target_data_fingerprint VARCHAR NOT NULL,
    build_fingerprint VARCHAR NOT NULL,
    scoring_ruleset_fingerprint VARCHAR NOT NULL,
    prediction_rows INTEGER NOT NULL,
    evaluated_rows INTEGER NOT NULL,
    report_payload JSON NOT NULL
);

CREATE TABLE IF NOT EXISTS adp_snapshots (
    snapshot_id VARCHAR NOT NULL,
    source VARCHAR NOT NULL,
    captured_at TIMESTAMPTZ NOT NULL,
    season INTEGER NOT NULL,
    scoring_format VARCHAR NOT NULL,
    team_count INTEGER NOT NULL,
    player_id VARCHAR,
    player_name VARCHAR NOT NULL,
    position VARCHAR,
    nfl_team VARCHAR,
    average_pick DOUBLE,
    median_pick DOUBLE,
    rank INTEGER,
    min_pick DOUBLE,
    max_pick DOUBLE,
    sample_size INTEGER,
    movement DOUBLE,
    raw_source_row_id VARCHAR NOT NULL,
    mapping_confidence VARCHAR NOT NULL,
    PRIMARY KEY (snapshot_id, raw_source_row_id)
);

CREATE TABLE IF NOT EXISTS league_rules (
    league_season_id VARCHAR PRIMARY KEY,
    platform VARCHAR NOT NULL,
    season INTEGER NOT NULL,
    team_count INTEGER NOT NULL,
    draft_type VARCHAR NOT NULL,
    rounds INTEGER NOT NULL,
    starter_slots_json JSON NOT NULL,
    flex_slots_json JSON NOT NULL,
    bench_slots INTEGER NOT NULL,
    ir_slots INTEGER NOT NULL,
    scoring_json JSON NOT NULL,
    playoff_settings_json JSON,
    normalized_ruleset_json JSON NOT NULL,
    ruleset_fingerprint VARCHAR NOT NULL
);

CREATE TABLE IF NOT EXISTS draft_picks (
    league_season_id VARCHAR NOT NULL,
    overall_pick INTEGER NOT NULL,
    round INTEGER NOT NULL,
    draft_slot INTEGER NOT NULL,
    team_id VARCHAR NOT NULL,
    player_id VARCHAR,
    player_name VARCHAR,
    is_keeper BOOLEAN,
    is_autopick BOOLEAN,
    picked_at TIMESTAMPTZ,
    adp_snapshot_id VARCHAR,
    PRIMARY KEY (league_season_id, overall_pick)
);

CREATE TABLE IF NOT EXISTS team_outcomes (
    league_season_id VARCHAR NOT NULL,
    team_id VARCHAR NOT NULL,
    wins DOUBLE,
    losses DOUBLE,
    ties DOUBLE,
    points_for DOUBLE,
    points_against DOUBLE,
    all_play_percentile DOUBLE,
    points_percentile DOUBLE,
    seed INTEGER,
    made_playoffs BOOLEAN,
    final_place INTEGER,
    is_champion BOOLEAN,
    draft_only_metrics JSON,
    PRIMARY KEY (league_season_id, team_id)
);
"""

MIGRATION_SQL = """
ALTER TABLE players ADD COLUMN IF NOT EXISTS pfr_id VARCHAR;
ALTER TABLE players ADD COLUMN IF NOT EXISTS rookie_season INTEGER;
ALTER TABLE players ADD COLUMN IF NOT EXISTS draft_year INTEGER;
ALTER TABLE players ADD COLUMN IF NOT EXISTS draft_round INTEGER;
ALTER TABLE players ADD COLUMN IF NOT EXISTS draft_pick INTEGER;
ALTER TABLE players ADD COLUMN IF NOT EXISTS draft_team VARCHAR;
ALTER TABLE players ADD COLUMN IF NOT EXISTS height_inches INTEGER;
ALTER TABLE players ADD COLUMN IF NOT EXISTS weight_lbs INTEGER;
ALTER TABLE players ADD COLUMN IF NOT EXISTS identity_source_dataset_id VARCHAR;
ALTER TABLE players ADD COLUMN IF NOT EXISTS identity_source_as_of TIMESTAMPTZ;
ALTER TABLE player_week_stats ADD COLUMN IF NOT EXISTS position VARCHAR;
ALTER TABLE player_week_stats ADD COLUMN IF NOT EXISTS season_type VARCHAR;
ALTER TABLE player_week_stats ADD COLUMN IF NOT EXISTS game_id VARCHAR;
ALTER TABLE player_week_stats ADD COLUMN IF NOT EXISTS source_dataset_id VARCHAR;
ALTER TABLE player_week_stats ADD COLUMN IF NOT EXISTS completions DOUBLE;
ALTER TABLE player_week_stats ADD COLUMN IF NOT EXISTS passing_attempts DOUBLE;
ALTER TABLE player_week_stats ADD COLUMN IF NOT EXISTS special_teams_tds DOUBLE;
ALTER TABLE player_week_stats ADD COLUMN IF NOT EXISTS field_goals_made DOUBLE;
ALTER TABLE player_week_stats ADD COLUMN IF NOT EXISTS field_goals_attempted DOUBLE;
ALTER TABLE player_week_stats ADD COLUMN IF NOT EXISTS extra_points_made DOUBLE;
ALTER TABLE player_week_stats ADD COLUMN IF NOT EXISTS extra_points_attempted DOUBLE;
ALTER TABLE player_season_features ADD COLUMN IF NOT EXISTS feature_available_at DATE;
ALTER TABLE player_season_features ADD COLUMN IF NOT EXISTS feature_version VARCHAR;
ALTER TABLE player_season_features ADD COLUMN IF NOT EXISTS scoring_ruleset_fingerprint VARCHAR;
ALTER TABLE player_season_features ADD COLUMN IF NOT EXISTS source_dataset_ids JSON;
ALTER TABLE player_season_features ADD COLUMN IF NOT EXISTS source_max_stat_season INTEGER;
ALTER TABLE player_season_features ADD COLUMN IF NOT EXISTS source_max_as_of TIMESTAMPTZ;
ALTER TABLE player_season_features ADD COLUMN IF NOT EXISTS data_fingerprint VARCHAR;
ALTER TABLE player_season_targets ADD COLUMN IF NOT EXISTS target_data_fingerprint VARCHAR;
ALTER TABLE feature_build_metadata ADD COLUMN IF NOT EXISTS target_data_fingerprint VARCHAR;
ALTER TABLE feature_build_metadata ADD COLUMN IF NOT EXISTS build_fingerprint VARCHAR;
ALTER TABLE baseline_predictions ADD COLUMN IF NOT EXISTS target_data_fingerprint VARCHAR;
ALTER TABLE baseline_predictions ADD COLUMN IF NOT EXISTS build_fingerprint VARCHAR;
ALTER TABLE baseline_evaluation_metadata ADD COLUMN IF NOT EXISTS target_data_fingerprint VARCHAR;
ALTER TABLE baseline_evaluation_metadata ADD COLUMN IF NOT EXISTS build_fingerprint VARCHAR;
"""


class Warehouse:
    """Small explicit wrapper around the local DuckDB file."""

    def __init__(self, path: Path) -> None:
        self.path = path.resolve()

    @contextmanager
    def connect(self, *, read_only: bool = False) -> Iterator[duckdb.DuckDBPyConnection]:
        if not read_only:
            self.path.parent.mkdir(parents=True, exist_ok=True)
        connection = duckdb.connect(str(self.path), read_only=read_only)
        try:
            yield connection
        finally:
            connection.close()

    def initialize(self) -> None:
        with self.connect() as connection:
            connection.execute(SCHEMA_SQL)
            connection.execute(MIGRATION_SQL)
            _ensure_feature_key_uniqueness(connection)

    def table_counts(self) -> dict[str, int]:
        """Return row counts for every canonical table."""

        tables = [
            "players",
            "player_week_stats",
            "player_game_participation",
            "player_source_mappings",
            "identity_review_queue",
            "player_season_features",
            "player_season_targets",
            "feature_build_metadata",
            "baseline_predictions",
            "baseline_evaluation_metadata",
            "adp_snapshots",
            "league_rules",
            "draft_picks",
            "team_outcomes",
        ]
        if not self.path.exists():
            return {table: 0 for table in tables}
        self.initialize()
        with self.connect(read_only=True) as connection:
            counts: dict[str, int] = {}
            for table in tables:
                row = connection.execute(f"SELECT COUNT(*) FROM {table}").fetchone()
                if row is None:
                    raise RuntimeError(f"DuckDB did not return a count for {table}.")
                counts[table] = int(row[0])
            return counts


def _ensure_feature_key_uniqueness(
    connection: duckdb.DuckDBPyConnection,
) -> None:
    duplicate = connection.execute(
        """
        SELECT count(*)
        FROM (
            SELECT player_id, prediction_season
            FROM player_season_features
            GROUP BY player_id, prediction_season
            HAVING count(*) > 1
        )
        """
    ).fetchone()
    if duplicate is None or int(duplicate[0]):
        raise RuntimeError(
            "Cannot migrate player_season_features: duplicate player/prediction-season "
            "keys exist across legacy sources. Resolve them before initializing Phase 3."
        )
    connection.execute(
        "CREATE UNIQUE INDEX IF NOT EXISTS uq_player_season_features_logical "
        "ON player_season_features (player_id, prediction_season)"
    )
