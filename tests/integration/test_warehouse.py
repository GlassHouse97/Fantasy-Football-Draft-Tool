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
        "player_season_features": 0,
        "adp_snapshots": 0,
        "league_rules": 0,
        "draft_picks": 0,
        "team_outcomes": 0,
    }
