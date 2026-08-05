from pathlib import Path

from fantasy_draft_ai.data.warehouse import Warehouse


def test_warehouse_initialization_is_idempotent(tmp_path: Path) -> None:
    warehouse = Warehouse(tmp_path / "fantasy.duckdb")
    warehouse.initialize()
    warehouse.initialize()
    assert warehouse.path.is_file()
    assert warehouse.table_counts() == {
        "players": 0,
        "player_week_stats": 0,
        "player_source_mappings": 0,
        "identity_review_queue": 0,
        "player_season_features": 0,
        "adp_snapshots": 0,
        "league_rules": 0,
        "draft_picks": 0,
        "team_outcomes": 0,
    }
    with warehouse.connect(read_only=True) as connection:
        columns = {
            row[1]
            for row in connection.execute("PRAGMA table_info('player_week_stats')").fetchall()
        }
    assert {
        "season_type",
        "game_id",
        "source_dataset_id",
        "field_goals_made",
        "field_goals_attempted",
        "extra_points_made",
        "extra_points_attempted",
    } <= columns
    with warehouse.connect(read_only=True) as connection:
        review_columns = {
            row[1]
            for row in connection.execute("PRAGMA table_info('identity_review_queue')").fetchall()
        }
    assert {
        "review_id",
        "source_player_id",
        "candidate_player_id",
        "mapping_confidence",
        "status",
        "resolution",
        "is_current",
    } <= review_columns
