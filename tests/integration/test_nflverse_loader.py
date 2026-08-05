from __future__ import annotations

from datetime import UTC, datetime, timedelta
from pathlib import Path
from typing import Any

import pandas as pd

from fantasy_draft_ai.config import (
    AppConfig,
    NetworkSection,
    PathSection,
    ProjectSection,
    TrainingSection,
)
from fantasy_draft_ai.data.manifests import RawArchive, sha256_file
from fantasy_draft_ai.data.nflverse_loader import load_nflverse_to_warehouse
from fantasy_draft_ai.data.warehouse import Warehouse

ACQUIRED_AT = datetime(2026, 8, 5, 13, 20, 34, tzinfo=UTC)


def _config(project_root: Path) -> AppConfig:
    return AppConfig(
        project=ProjectSection(name="Test Fantasy Football Draft AI", prediction_season=2026),
        paths=PathSection(
            data_dir=Path("data"),
            raw_dir=Path("data/raw"),
            processed_dir=Path("data/processed"),
            warehouse=Path("data/warehouse/test.duckdb"),
            manifests=Path("data/raw/manifests"),
        ),
        network=NetworkSection(timeout_seconds=5, user_agent="test"),
        training=TrainingSection(start_season=2025, end_season=2025),
        project_root=project_root,
    )


def _player(
    player_id: str,
    name: str,
    *,
    position: str = "WR",
    status: str = "ACT",
    last_season: int = 2026,
) -> dict[str, Any]:
    return {
        "gsis_id": player_id,
        "display_name": name,
        "espn_id": f"espn-{player_id}",
        "birth_date": "2000-01-02",
        "position": position,
        "latest_team": "BUF",
        "status": status,
        "last_season": last_season,
        "years_of_experience": 3,
    }


def _weekly_stat(
    player_id: str | None,
    name: str | None,
    *,
    week: int = 1,
    passing_yards: int = 0,
    receiving_yards: int = 80,
) -> dict[str, Any]:
    return {
        "player_id": player_id,
        "player_display_name": name,
        "position": "WR" if player_id else None,
        "season": 2025,
        "week": week,
        "season_type": "REG",
        "game_id": f"2025_{week:02d}_BUF_MIA",
        "team": "BUF",
        "opponent_team": "MIA",
        "completions": 2,
        "attempts": 3,
        "passing_yards": passing_yards,
        "passing_tds": 1,
        "passing_interceptions": 2,
        "rushing_yards": 12,
        "rushing_tds": 1,
        "receiving_yards": receiving_yards,
        "receptions": 5,
        "receiving_tds": 1,
        "targets": 7,
        "carries": 3,
        "passing_2pt_conversions": 1,
        "rushing_2pt_conversions": 1,
        "receiving_2pt_conversions": 1,
        "fumbles_lost_total": 3,
        "special_teams_tds": 1,
        "fg_made": 2,
        "fg_att": 3,
        "pat_made": 4,
        "pat_att": 5,
    }


def _zero_placeholder() -> dict[str, Any]:
    row = _weekly_stat(None, None, receiving_yards=0)
    for column in (
        "completions",
        "attempts",
        "passing_tds",
        "passing_interceptions",
        "rushing_yards",
        "rushing_tds",
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
    ):
        row[column] = 0
    return row


def _capture(
    config: AppConfig,
    players: list[dict[str, Any]],
    stats: list[dict[str, Any]],
    *,
    acquired_at: datetime = ACQUIRED_AT,
) -> tuple[Path, Path, Path]:
    raw_dir = config.resolve(config.paths.raw_dir) / "nflverse"
    raw_dir.mkdir(parents=True, exist_ok=True)
    stamp = acquired_at.strftime("%Y%m%dT%H%M%S%fZ")
    player_path = raw_dir / f"nflverse_players__2025-2025__{stamp}.parquet"
    stats_path = raw_dir / f"nflverse_player_stats__weekly__2025-2025__{stamp}.parquet"
    pd.DataFrame(players).to_parquet(player_path, index=False)
    pd.DataFrame(stats).to_parquet(stats_path, index=False)
    archive = RawArchive(
        config.project_root,
        config.resolve(config.paths.raw_dir),
        config.resolve(config.paths.manifests),
    )
    _, manifest_path = archive.create_manifest(
        source="nflverse",
        acquisition_method="integration-test",
        acquired_at=acquired_at,
        raw_files=[player_path, stats_path],
        seasons=[2025],
    )
    return player_path, stats_path, manifest_path


def test_load_normalizes_reports_and_is_idempotent(tmp_path: Path) -> None:
    config = _config(tmp_path)
    player_path, stats_path, manifest_path = _capture(
        config,
        [
            _player("p1", "Exact Player"),
            _player("p2", "Master Name", status="RES"),
            _player("p3", "Exact Player", last_season=2025),
        ],
        [
            _weekly_stat("p1", "Exact Player"),
            _weekly_stat("p2", "Weekly Name", week=2),
            _weekly_stat("p3", "Exact Player", week=3),
            _zero_placeholder(),
        ],
    )
    raw_hashes = (sha256_file(player_path), sha256_file(stats_path))

    first = load_nflverse_to_warehouse(config, manifest_path=manifest_path)

    assert first.committed
    assert not first.quality.has_fatal_errors
    assert first.quality.required_field_failures == 1
    assert first.quality.excluded_rows == 1
    assert first.quality.identity_conflicts == 1
    assert first.exact_mappings == 2
    assert first.high_confidence_mappings == 1
    assert first.regular_season_rows == 3
    assert first.postseason_rows == 0
    assert first.players.inserted_rows == 3
    assert first.weekly_stats.inserted_rows == 3
    assert "excluded_missing_player_id" in first.render()
    assert "duplicate_display_names" in first.render()
    assert raw_hashes == (sha256_file(player_path), sha256_file(stats_path))

    warehouse = Warehouse(config.resolve(config.paths.warehouse))
    with warehouse.connect() as connection:
        players = connection.execute(
            "SELECT player_id, mapping_confidence, is_active, mapping_source "
            "FROM players ORDER BY player_id"
        ).fetchall()
        stat = connection.execute(
            "SELECT season_type, game_id, completions, passing_attempts, "
            "interceptions, two_point_conversions, fumbles_lost, special_teams_tds, "
            "field_goals_made, field_goals_attempted, extra_points_made, "
            "extra_points_attempted, games_active, games_played, as_of, "
            "source_dataset_id FROM player_week_stats WHERE player_id = 'p1'"
        ).fetchone()
        connection.execute(
            "UPDATE players SET espn_id = 'manual-espn-p1', sleeper_id = 'sleeper-p1', "
            "mapping_confidence = 'reviewed', mapping_source = 'manual:identity-review' "
            "WHERE player_id = 'p1'"
        )

    assert players[0][0:3] == ("p1", "exact", True)
    assert players[1][0:3] == ("p2", "high", None)
    assert players[2][0:3] == ("p3", "exact", False)
    assert first.manifest.dataset_id in players[0][3]
    assert stat is not None
    assert stat[0:12] == ("REG", "2025_01_BUF_MIA", 2, 3, 2, 3, 3, 1, 2, 3, 4, 5)
    assert stat[12] is None
    assert stat[13] is None
    assert stat[14] == ACQUIRED_AT
    assert stat[15] == first.manifest.dataset_id

    with warehouse.connect(read_only=True) as connection:
        before_repeat = connection.execute(
            "SELECT * FROM player_week_stats ORDER BY season, week, player_id, source"
        ).fetchall()
    second = load_nflverse_to_warehouse(config, manifest_path=manifest_path)
    with warehouse.connect(read_only=True) as connection:
        after_repeat = connection.execute(
            "SELECT * FROM player_week_stats ORDER BY season, week, player_id, source"
        ).fetchall()
        curated_identity = connection.execute(
            "SELECT espn_id, sleeper_id, mapping_confidence, mapping_source "
            "FROM players WHERE player_id = 'p1'"
        ).fetchone()

    assert second.committed
    assert second.players.inserted_rows == 0
    assert second.players.matched_existing_rows == 3
    assert second.weekly_stats.inserted_rows == 0
    assert second.weekly_stats.matched_existing_rows == 3
    assert before_repeat == after_repeat
    assert curated_identity == (
        "manual-espn-p1",
        "sleeper-p1",
        "reviewed",
        "manual:identity-review",
    )
    assert raw_hashes == (sha256_file(player_path), sha256_file(stats_path))


def test_new_capture_upserts_keys_without_erasing_unmentioned_rows(tmp_path: Path) -> None:
    config = _config(tmp_path)
    players = [_player("p1", "Player One")]
    _, _, first_manifest = _capture(
        config,
        players,
        [
            _weekly_stat("p1", "Player One", week=1, receiving_yards=40),
            _weekly_stat("p1", "Player One", week=2, receiving_yards=50),
        ],
    )
    first = load_nflverse_to_warehouse(config, manifest_path=first_manifest)
    assert first.committed

    warehouse = Warehouse(config.resolve(config.paths.warehouse))
    with warehouse.connect() as connection:
        connection.execute(
            "INSERT INTO player_week_stats "
            "(season, week, player_id, source, as_of) "
            "VALUES (2025, 99, 'manual-player', 'manual', ?)",
            [ACQUIRED_AT],
        )

    _, _, second_manifest = _capture(
        config,
        players,
        [_weekly_stat("p1", "Player One", week=1, receiving_yards=99)],
        acquired_at=ACQUIRED_AT + timedelta(days=1),
    )
    second = load_nflverse_to_warehouse(config, manifest_path=second_manifest)

    assert second.committed
    assert second.weekly_stats.normalized_rows == 1
    assert second.weekly_stats.matched_existing_rows == 1
    with warehouse.connect(read_only=True) as connection:
        nflverse_rows = connection.execute(
            "SELECT week, receiving_yards, source_dataset_id "
            "FROM player_week_stats WHERE source = 'nflverse' ORDER BY week"
        ).fetchall()
        manual_count = connection.execute(
            "SELECT count(*) FROM player_week_stats WHERE source = 'manual'"
        ).fetchone()
    assert nflverse_rows == [
        (1, 99.0, second.manifest.dataset_id),
        (2, 50.0, first.manifest.dataset_id),
    ]
    assert manual_count == (1,)


def test_missing_id_with_kicking_production_is_fatal(tmp_path: Path) -> None:
    config = _config(tmp_path)
    unresolved = _zero_placeholder()
    unresolved["fg_made"] = 1
    _, _, manifest_path = _capture(
        config,
        [_player("p1", "Player One")],
        [unresolved],
    )

    result = load_nflverse_to_warehouse(config, manifest_path=manifest_path)

    assert not result.committed
    assert result.quality.has_fatal_errors
    assert any(issue.code == "missing_id_with_stats" for issue in result.quality.issues)
    assert not config.resolve(config.paths.warehouse).exists()


def test_orphan_or_duplicate_source_rows_are_fatal_and_write_nothing(tmp_path: Path) -> None:
    config = _config(tmp_path)
    warehouse = Warehouse(config.resolve(config.paths.warehouse))
    warehouse.initialize()
    with warehouse.connect() as connection:
        connection.execute(
            "INSERT INTO players "
            "(player_id, display_name, mapping_confidence, mapping_source) "
            "VALUES ('manual-player', 'Manual Player', 'exact', 'manual')"
        )
    players = [_player("p1", "Player One")]
    duplicate = _weekly_stat("p1", "Player One")
    _, _, duplicate_manifest = _capture(config, players, [duplicate, duplicate.copy()])

    duplicate_result = load_nflverse_to_warehouse(config, manifest_path=duplicate_manifest)
    assert not duplicate_result.committed
    assert duplicate_result.quality.has_fatal_errors
    assert duplicate_result.quality.duplicate_keys == 1
    assert warehouse.table_counts()["players"] == 1

    _, _, orphan_manifest = _capture(
        config,
        players,
        [_weekly_stat("missing-player", "Unknown Player")],
        acquired_at=ACQUIRED_AT + timedelta(days=1),
    )
    orphan_result = load_nflverse_to_warehouse(config, manifest_path=orphan_manifest)
    assert not orphan_result.committed
    assert orphan_result.quality.unresolved_players == 1
    assert warehouse.table_counts()["players"] == 1
    with warehouse.connect(read_only=True) as connection:
        preserved = connection.execute(
            "SELECT display_name FROM players WHERE player_id = 'manual-player'"
        ).fetchone()
    assert preserved == ("Manual Player",)


def test_missing_required_source_column_is_fatal(tmp_path: Path) -> None:
    config = _config(tmp_path)
    incomplete_stat = _weekly_stat("p1", "Player One")
    del incomplete_stat["fumbles_lost_total"]
    _, _, manifest_path = _capture(config, [_player("p1", "Player One")], [incomplete_stat])

    result = load_nflverse_to_warehouse(config, manifest_path=manifest_path)

    assert not result.committed
    assert result.quality.has_fatal_errors
    assert any(issue.code == "missing_weekly_stat_columns" for issue in result.quality.issues)
    assert not config.resolve(config.paths.warehouse).exists()


def test_hash_mismatch_is_fatal_and_raw_file_is_not_loaded(tmp_path: Path) -> None:
    config = _config(tmp_path)
    player_path, _, manifest_path = _capture(
        config,
        [_player("p1", "Player One")],
        [_weekly_stat("p1", "Player One")],
    )
    pd.DataFrame([_player("p2", "Tampered Player")]).to_parquet(player_path, index=False)

    result = load_nflverse_to_warehouse(config, manifest_path=manifest_path)

    assert not result.committed
    assert result.quality.has_fatal_errors
    assert any(issue.code == "raw_hash_mismatch" for issue in result.quality.issues)
    assert not config.resolve(config.paths.warehouse).exists()
