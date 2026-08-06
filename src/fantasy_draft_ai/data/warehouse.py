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

CREATE TABLE IF NOT EXISTS player_projection_runs (
    run_id VARCHAR PRIMARY KEY,
    feature_data_fingerprint VARCHAR NOT NULL,
    target_data_fingerprint VARCHAR NOT NULL,
    build_fingerprint VARCHAR NOT NULL,
    scoring_ruleset_fingerprint VARCHAR NOT NULL,
    baseline_report_fingerprint VARCHAR NOT NULL,
    model_feature_fingerprint VARCHAR NOT NULL,
    model_config_fingerprint VARCHAR NOT NULL,
    split_seasons JSON NOT NULL,
    feature_rows INTEGER NOT NULL,
    target_rows INTEGER NOT NULL,
    training_rows INTEGER NOT NULL,
    prediction_rows INTEGER NOT NULL,
    evaluated_rows INTEGER NOT NULL,
    live_prediction_rows INTEGER NOT NULL,
    candidate_rows INTEGER NOT NULL,
    model_rows INTEGER NOT NULL,
    champion_rows INTEGER NOT NULL,
    status VARCHAR NOT NULL,
    trained_at TIMESTAMPTZ NOT NULL,
    run_payload JSON NOT NULL
);

CREATE TABLE IF NOT EXISTS player_projection_models (
    model_id VARCHAR PRIMARY KEY,
    run_id VARCHAR NOT NULL,
    model_family VARCHAR NOT NULL,
    target_name VARCHAR NOT NULL,
    position VARCHAR NOT NULL,
    training_seasons JSON NOT NULL,
    training_rows INTEGER NOT NULL,
    feature_names JSON NOT NULL,
    categorical_feature_names JSON NOT NULL,
    hyperparameters JSON NOT NULL,
    uncertainty_method VARCHAR NOT NULL,
    artifact_path VARCHAR NOT NULL,
    artifact_sha256 VARCHAR NOT NULL,
    artifact_size_bytes BIGINT NOT NULL,
    model_card_path VARCHAR NOT NULL,
    model_card_sha256 VARCHAR NOT NULL,
    package_versions JSON NOT NULL,
    UNIQUE (run_id, model_family, target_name, position)
);

CREATE TABLE IF NOT EXISTS player_projection_predictions (
    run_id VARCHAR NOT NULL,
    player_id VARCHAR NOT NULL,
    prediction_season INTEGER NOT NULL,
    position VARCHAR NOT NULL,
    target_name VARCHAR NOT NULL,
    model_family VARCHAR NOT NULL,
    prediction_scope VARCHAR NOT NULL,
    fold_label VARCHAR,
    training_max_season INTEGER NOT NULL,
    predicted_value DOUBLE NOT NULL,
    p10 DOUBLE NOT NULL,
    p50 DOUBLE NOT NULL,
    p90 DOUBLE NOT NULL,
    actual_value DOUBLE,
    actual_games_active DOUBLE,
    experience INTEGER,
    experience_group VARCHAR NOT NULL,
    feature_data_fingerprint VARCHAR NOT NULL,
    target_data_fingerprint VARCHAR NOT NULL,
    build_fingerprint VARCHAR NOT NULL,
    scoring_ruleset_fingerprint VARCHAR NOT NULL,
    baseline_report_fingerprint VARCHAR NOT NULL,
    model_feature_fingerprint VARCHAR NOT NULL,
    model_config_fingerprint VARCHAR NOT NULL,
    PRIMARY KEY (run_id, player_id, prediction_season, target_name, model_family)
);

CREATE TABLE IF NOT EXISTS player_projection_champions (
    run_id VARCHAR NOT NULL,
    target_name VARCHAR NOT NULL,
    position VARCHAR NOT NULL,
    selected_source VARCHAR NOT NULL,
    selected_name VARCHAR NOT NULL,
    model_id VARCHAR,
    selection_metric VARCHAR NOT NULL,
    selection_value DOUBLE NOT NULL,
    reference_baseline_name VARCHAR NOT NULL,
    reference_baseline_value DOUBLE NOT NULL,
    improvement DOUBLE NOT NULL,
    selection_payload JSON NOT NULL,
    PRIMARY KEY (run_id, target_name, position)
);

CREATE TABLE IF NOT EXISTS player_projection_evaluation_metadata (
    report_fingerprint VARCHAR PRIMARY KEY,
    run_id VARCHAR NOT NULL UNIQUE,
    feature_data_fingerprint VARCHAR NOT NULL,
    target_data_fingerprint VARCHAR NOT NULL,
    build_fingerprint VARCHAR NOT NULL,
    scoring_ruleset_fingerprint VARCHAR NOT NULL,
    baseline_report_fingerprint VARCHAR NOT NULL,
    model_feature_fingerprint VARCHAR NOT NULL,
    model_config_fingerprint VARCHAR NOT NULL,
    prediction_rows INTEGER NOT NULL,
    evaluated_rows INTEGER NOT NULL,
    live_prediction_rows INTEGER NOT NULL,
    candidate_rows INTEGER NOT NULL,
    champion_rows INTEGER NOT NULL,
    report_payload JSON NOT NULL
);

CREATE TABLE IF NOT EXISTS player_projection_board (
    run_id VARCHAR NOT NULL,
    player_id VARCHAR NOT NULL,
    prediction_season INTEGER NOT NULL,
    position VARCHAR NOT NULL,
    fantasy_points_per_game_p10 DOUBLE NOT NULL,
    fantasy_points_per_game_p50 DOUBLE NOT NULL,
    fantasy_points_per_game_p90 DOUBLE NOT NULL,
    fantasy_points_per_game_selected_source VARCHAR NOT NULL,
    fantasy_points_per_game_selected_name VARCHAR NOT NULL,
    games_active_p10 DOUBLE NOT NULL,
    games_active_p50 DOUBLE NOT NULL,
    games_active_p90 DOUBLE NOT NULL,
    games_active_selected_source VARCHAR NOT NULL,
    games_active_selected_name VARCHAR NOT NULL,
    fantasy_points_total_p10 DOUBLE NOT NULL,
    fantasy_points_total_p50 DOUBLE NOT NULL,
    fantasy_points_total_p90 DOUBLE NOT NULL,
    fantasy_points_total_selected_source VARCHAR NOT NULL,
    fantasy_points_total_selected_name VARCHAR NOT NULL,
    prediction_status VARCHAR NOT NULL,
    explanation_payload JSON NOT NULL,
    feature_data_fingerprint VARCHAR NOT NULL,
    target_data_fingerprint VARCHAR NOT NULL,
    build_fingerprint VARCHAR NOT NULL,
    scoring_ruleset_fingerprint VARCHAR NOT NULL,
    baseline_report_fingerprint VARCHAR NOT NULL,
    model_feature_fingerprint VARCHAR NOT NULL,
    model_config_fingerprint VARCHAR NOT NULL,
    evaluation_report_fingerprint VARCHAR NOT NULL,
    PRIMARY KEY (run_id, player_id, prediction_season)
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
    source_stddev DOUBLE,
    source_movement_horizon VARCHAR,
    raw_source_row_id VARCHAR NOT NULL,
    mapping_confidence VARCHAR NOT NULL,
    PRIMARY KEY (snapshot_id, raw_source_row_id)
);

CREATE TABLE IF NOT EXISTS adp_snapshot_metadata (
    snapshot_id VARCHAR PRIMARY KEY,
    source VARCHAR NOT NULL,
    captured_at TIMESTAMPTZ NOT NULL,
    season INTEGER NOT NULL,
    scoring_format VARCHAR NOT NULL,
    team_count INTEGER NOT NULL,
    position_scope VARCHAR NOT NULL,
    raw_sha256 VARCHAR NOT NULL,
    raw_relative_path VARCHAR NOT NULL,
    source_dataset_ids JSON NOT NULL,
    row_count INTEGER NOT NULL,
    loaded_at TIMESTAMPTZ NOT NULL
);

CREATE TABLE IF NOT EXISTS adp_movement_features (
    snapshot_id VARCHAR NOT NULL,
    raw_source_row_id VARCHAR NOT NULL,
    entity_key VARCHAR NOT NULL,
    player_id VARCHAR,
    source VARCHAR NOT NULL,
    captured_at TIMESTAMPTZ NOT NULL,
    season INTEGER NOT NULL,
    scoring_format VARCHAR NOT NULL,
    team_count INTEGER NOT NULL,
    average_pick DOUBLE,
    prior_snapshot_id VARCHAR,
    prior_observed_at TIMESTAMPTZ,
    prior_average_pick DOUBLE,
    elapsed_days DOUBLE,
    change_1d DOUBLE,
    change_3d DOUBLE,
    change_7d DOUBLE,
    change_14d DOUBLE,
    velocity_per_day DOUBLE,
    acceleration_per_day2 DOUBLE,
    rolling_volatility_14d DOUBLE,
    source_spread DOUBLE,
    observation_count INTEGER,
    source_count INTEGER,
    identity_observation_count INTEGER,
    feature_version VARCHAR NOT NULL,
    data_fingerprint VARCHAR NOT NULL,
    PRIMARY KEY (snapshot_id, raw_source_row_id)
);

CREATE TABLE IF NOT EXISTS adp_movement_forecasts (
    snapshot_id VARCHAR NOT NULL,
    raw_source_row_id VARCHAR NOT NULL,
    baseline_name VARCHAR NOT NULL,
    forecast_horizon_days INTEGER NOT NULL,
    target_at TIMESTAMPTZ NOT NULL,
    predicted_average_pick DOUBLE,
    predicted_change DOUBLE,
    history_count INTEGER,
    status VARCHAR NOT NULL,
    reason VARCHAR NOT NULL,
    model_version VARCHAR NOT NULL,
    data_fingerprint VARCHAR NOT NULL,
    PRIMARY KEY (
        snapshot_id, raw_source_row_id, baseline_name, forecast_horizon_days
    )
);

CREATE TABLE IF NOT EXISTS adp_availability_parameters (
    snapshot_id VARCHAR NOT NULL,
    raw_source_row_id VARCHAR NOT NULL,
    entity_key VARCHAR NOT NULL,
    player_id VARCHAR,
    source VARCHAR NOT NULL,
    captured_at TIMESTAMPTZ NOT NULL,
    average_pick DOUBLE,
    scale DOUBLE,
    evidence_method VARCHAR NOT NULL,
    fallback_group VARCHAR,
    source_sample_size INTEGER,
    min_pick DOUBLE,
    max_pick DOUBLE,
    mapping_confidence VARCHAR NOT NULL,
    method_version VARCHAR NOT NULL,
    data_fingerprint VARCHAR NOT NULL,
    PRIMARY KEY (snapshot_id, raw_source_row_id)
);

CREATE TABLE IF NOT EXISTS adp_phase5_builds (
    build_fingerprint VARCHAR PRIMARY KEY,
    snapshot_data_fingerprint VARCHAR NOT NULL,
    availability_config_fingerprint VARCHAR NOT NULL,
    snapshot_count INTEGER NOT NULL,
    observation_rows INTEGER NOT NULL,
    movement_feature_rows INTEGER NOT NULL,
    movement_forecast_rows INTEGER NOT NULL,
    availability_parameter_rows INTEGER NOT NULL,
    persistence_ready_rows INTEGER NOT NULL,
    linear_ready_rows INTEGER NOT NULL,
    ew_ready_rows INTEGER NOT NULL,
    calibration_status VARCHAR NOT NULL,
    supervised_status VARCHAR NOT NULL,
    built_at TIMESTAMPTZ NOT NULL,
    report_payload JSON NOT NULL
);

CREATE TABLE IF NOT EXISTS league_rules (
    league_season_id VARCHAR PRIMARY KEY,
    platform VARCHAR NOT NULL,
    season INTEGER NOT NULL,
    team_count INTEGER NOT NULL,
    user_draft_slot INTEGER,
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

CREATE TABLE IF NOT EXISTS draft_sessions (
    session_id VARCHAR PRIMARY KEY,
    session_name VARCHAR NOT NULL,
    status VARCHAR NOT NULL,
    ruleset_json JSON NOT NULL,
    ruleset_fingerprint VARCHAR NOT NULL,
    scoring_fingerprint VARCHAR NOT NULL,
    team_count INTEGER NOT NULL,
    rounds INTEGER NOT NULL,
    user_draft_slot INTEGER NOT NULL,
    projection_run_id VARCHAR NOT NULL,
    adp_build_fingerprint VARCHAR,
    player_pool_fingerprint VARCHAR NOT NULL,
    engine_config_fingerprint VARCHAR NOT NULL,
    player_pool_rows INTEGER NOT NULL,
    mapped_market_rows INTEGER NOT NULL,
    recommendation_status VARCHAR NOT NULL,
    recommendation_message VARCHAR NOT NULL,
    random_seed BIGINT NOT NULL,
    simulation_count INTEGER NOT NULL,
    current_version INTEGER NOT NULL,
    state_fingerprint VARCHAR NOT NULL,
    created_at TIMESTAMPTZ NOT NULL,
    updated_at TIMESTAMPTZ NOT NULL
);

CREATE TABLE IF NOT EXISTS draft_session_players (
    session_id VARCHAR NOT NULL,
    player_id VARCHAR NOT NULL,
    display_name VARCHAR NOT NULL,
    position VARCHAR NOT NULL,
    p10 DOUBLE NOT NULL,
    p50 DOUBLE NOT NULL,
    p90 DOUBLE NOT NULL,
    prediction_status VARCHAR NOT NULL,
    projection_source VARCHAR NOT NULL,
    projection_method VARCHAR NOT NULL,
    market_source VARCHAR,
    market_snapshot_id VARCHAR,
    market_captured_at TIMESTAMPTZ,
    average_pick DOUBLE,
    availability_scale DOUBLE,
    availability_evidence VARCHAR,
    mapping_confidence VARCHAR,
    player_payload JSON NOT NULL,
    PRIMARY KEY (session_id, player_id)
);

CREATE TABLE IF NOT EXISTS draft_events (
    session_id VARCHAR NOT NULL,
    sequence INTEGER NOT NULL,
    event_id VARCHAR NOT NULL,
    event_type VARCHAR NOT NULL,
    occurred_at TIMESTAMPTZ NOT NULL,
    command_id VARCHAR NOT NULL,
    payload JSON NOT NULL,
    prior_state_fingerprint VARCHAR,
    resulting_state_fingerprint VARCHAR NOT NULL,
    PRIMARY KEY (session_id, sequence),
    UNIQUE (session_id, event_id),
    UNIQUE (session_id, command_id)
);

CREATE TABLE IF NOT EXISTS draft_recommendation_runs (
    recommendation_run_id VARCHAR PRIMARY KEY,
    session_id VARCHAR NOT NULL,
    session_version INTEGER NOT NULL,
    state_fingerprint VARCHAR NOT NULL,
    engine_config_fingerprint VARCHAR NOT NULL,
    random_seed BIGINT NOT NULL,
    simulation_count INTEGER NOT NULL,
    status VARCHAR NOT NULL,
    result_fingerprint VARCHAR NOT NULL,
    result_payload JSON NOT NULL,
    created_at TIMESTAMPTZ NOT NULL
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
ALTER TABLE adp_snapshots ADD COLUMN IF NOT EXISTS source_stddev DOUBLE;
ALTER TABLE adp_snapshots ADD COLUMN IF NOT EXISTS source_movement_horizon VARCHAR;
ALTER TABLE league_rules ADD COLUMN IF NOT EXISTS user_draft_slot INTEGER;
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
            "player_projection_runs",
            "player_projection_models",
            "player_projection_predictions",
            "player_projection_champions",
            "player_projection_evaluation_metadata",
            "player_projection_board",
            "adp_snapshots",
            "adp_snapshot_metadata",
            "adp_movement_features",
            "adp_movement_forecasts",
            "adp_availability_parameters",
            "adp_phase5_builds",
            "league_rules",
            "draft_picks",
            "draft_sessions",
            "draft_session_players",
            "draft_events",
            "draft_recommendation_runs",
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


def invalidate_player_projection_runs(
    connection: duckdb.DuckDBPyConnection,
    *,
    build_fingerprint: str,
    baseline_report_fingerprint: str | None = None,
) -> int:
    """Remove learned outputs whose frozen Phase 3 contract is no longer current.

    Generated model files are immutable local artifacts and are intentionally not
    deleted here. Their database registrations are removed transactionally, which
    makes them harmless orphans that can be inspected or cleaned separately.
    """

    predicate = "build_fingerprint <> ?"
    parameters: list[str] = [build_fingerprint]
    if baseline_report_fingerprint is not None:
        predicate += " OR baseline_report_fingerprint <> ?"
        parameters.append(baseline_report_fingerprint)
    stale = connection.execute(
        f"SELECT count(*) FROM player_projection_runs WHERE {predicate}",
        parameters,
    ).fetchone()
    stale_count = int(stale[0]) if stale is not None else 0
    for table in (
        "player_projection_board",
        "player_projection_evaluation_metadata",
        "player_projection_champions",
        "player_projection_predictions",
        "player_projection_models",
    ):
        connection.execute(
            f"DELETE FROM {table} WHERE run_id IN "
            f"(SELECT run_id FROM player_projection_runs WHERE {predicate})",
            parameters,
        )
    connection.execute(
        f"DELETE FROM player_projection_runs WHERE {predicate}",
        parameters,
    )
    return stale_count


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
