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
    is_active BOOLEAN,
    mapping_confidence VARCHAR NOT NULL,
    mapping_source VARCHAR NOT NULL
);

CREATE TABLE IF NOT EXISTS player_week_stats (
    season INTEGER NOT NULL,
    week INTEGER NOT NULL,
    player_id VARCHAR NOT NULL,
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
    position VARCHAR,
    feature_payload JSON NOT NULL,
    target_payload JSON,
    source VARCHAR NOT NULL,
    is_synthetic BOOLEAN NOT NULL DEFAULT FALSE,
    PRIMARY KEY (player_id, prediction_season, source)
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

    def table_counts(self) -> dict[str, int]:
        """Return row counts for every canonical table."""

        tables = [
            "players",
            "player_week_stats",
            "player_source_mappings",
            "identity_review_queue",
            "player_season_features",
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
