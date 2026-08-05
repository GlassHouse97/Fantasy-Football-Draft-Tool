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
from fantasy_draft_ai.data.nflverse_participation import (
    load_nflverse_participation_to_warehouse,
)
from fantasy_draft_ai.data.sources.nflverse import download_nflverse_snap_counts
from fantasy_draft_ai.data.warehouse import Warehouse

ACQUIRED_AT = datetime(2026, 8, 5, 16, 0, tzinfo=UTC)


def _config(project_root: Path) -> AppConfig:
    return AppConfig(
        project=ProjectSection(name="Participation test", prediction_season=2026),
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


def _snap(
    pfr_player_id: str,
    player: str,
    *,
    week: int,
    season: int = 2025,
    game_type: str = "REG",
    offense_snaps: float = 42,
    defense_snaps: float = 0,
    special_teams_snaps: float = 3,
) -> dict[str, Any]:
    return {
        "game_id": f"{season}_{week:02d}_BUF_MIA",
        "pfr_game_id": f"{season}09{week:02d}buf",
        "season": season,
        "game_type": game_type,
        "week": week,
        "player": player,
        "pfr_player_id": pfr_player_id,
        "position": "WR",
        "team": "BUF",
        "opponent": "MIA",
        "offense_snaps": offense_snaps,
        "offense_pct": 0.7 if offense_snaps else 0.0,
        "defense_snaps": defense_snaps,
        "defense_pct": 0.0,
        "st_snaps": special_teams_snaps,
        "st_pct": 0.1 if special_teams_snaps else 0.0,
    }


def _capture(
    config: AppConfig,
    rows: list[dict[str, Any]],
    *,
    acquired_at: datetime = ACQUIRED_AT,
) -> tuple[Path, Path]:
    raw_dir = config.resolve(config.paths.raw_dir) / "nflverse"
    raw_dir.mkdir(parents=True, exist_ok=True)
    stamp = acquired_at.strftime("%Y-%m-%dT%H%M%S%fZ")
    seasons = sorted({int(row["season"]) for row in rows})
    path = raw_dir / (f"nflverse_snap_counts__{seasons[0]}-{seasons[-1]}__{stamp}.parquet")
    pd.DataFrame(rows).to_parquet(path, index=False)
    archive = RawArchive(
        config.project_root,
        config.resolve(config.paths.raw_dir),
        config.resolve(config.paths.manifests),
    )
    _, manifest_path = archive.create_manifest(
        source="nflverse",
        acquisition_method="integration-test",
        acquired_at=acquired_at,
        raw_files=[path],
        seasons=seasons,
    )
    return path, manifest_path


def _players(config: AppConfig) -> Warehouse:
    warehouse = Warehouse(config.resolve(config.paths.warehouse))
    warehouse.initialize()
    with warehouse.connect() as connection:
        connection.executemany(
            "INSERT INTO players (player_id, gsis_id, pfr_id, display_name, "
            "mapping_confidence, mapping_source) VALUES (?, ?, ?, ?, 'exact', 'test')",
            [
                ("p1", "p1", "PfrOne00", "Player One"),
                ("p2", "p2", "PfrTwo00", "Player Two"),
            ],
        )
    return warehouse


def test_participation_load_maps_reports_and_is_idempotent(tmp_path: Path) -> None:
    config = _config(tmp_path)
    warehouse = _players(config)
    raw_path, manifest_path = _capture(
        config,
        [
            _snap("PfrOne00", "Player One", week=1),
            _snap(
                "PfrTwo00",
                "Player Two",
                week=2,
                offense_snaps=0,
                special_teams_snaps=0,
            ),
            _snap("PfrOne00", "Player One", week=19, game_type="WC"),
            _snap("Missing00", "Unmapped Player", week=3),
        ],
    )
    raw_hash = sha256_file(raw_path)

    first = load_nflverse_participation_to_warehouse(config, manifest_path=manifest_path)

    assert first.committed
    assert not first.quality.has_fatal_errors
    assert first.quality.row_count == 4
    assert first.quality.unresolved_players == 1
    assert first.quality.excluded_rows == 1
    assert first.regular_season_rows == 3
    assert first.postseason_rows == 1
    assert first.participation.normalized_rows == 3
    assert first.participation.inserted_rows == 3
    assert "unresolved_pfr_players" in first.render()
    assert sha256_file(raw_path) == raw_hash

    with warehouse.connect(read_only=True) as connection:
        before = connection.execute(
            "SELECT season, week, game_id, player_id, season_type, position, nfl_team, "
            "opponent, offense_snaps, defense_snaps, special_teams_snaps, source, "
            "source_dataset_id FROM player_game_participation "
            "ORDER BY season, week, player_id"
        ).fetchall()
        active_games = connection.execute(
            "SELECT count(*) FROM player_game_participation WHERE "
            "offense_snaps + defense_snaps + special_teams_snaps > 0"
        ).fetchone()
    second = load_nflverse_participation_to_warehouse(config, manifest_path=manifest_path)
    with warehouse.connect(read_only=True) as connection:
        after = connection.execute(
            "SELECT season, week, game_id, player_id, season_type, position, nfl_team, "
            "opponent, offense_snaps, defense_snaps, special_teams_snaps, source, "
            "source_dataset_id FROM player_game_participation "
            "ORDER BY season, week, player_id"
        ).fetchall()

    assert before == after
    assert active_games == (2,)
    assert before[0][4:12] == (
        "REG",
        "WR",
        "BUF",
        "MIA",
        42,
        0,
        3,
        "nflverse_pfr_snap_counts",
    )
    assert second.participation.inserted_rows == 0
    assert second.participation.matched_existing_rows == 3
    assert sha256_file(raw_path) == raw_hash


def test_duplicate_snap_keys_are_fatal_and_preserve_existing_rows(tmp_path: Path) -> None:
    config = _config(tmp_path)
    warehouse = _players(config)
    _, valid_manifest = _capture(config, [_snap("PfrOne00", "Player One", week=1)])
    assert load_nflverse_participation_to_warehouse(config, manifest_path=valid_manifest).committed
    duplicate = _snap("PfrOne00", "Player One", week=2)
    whitespace_duplicate = {
        **duplicate,
        "game_id": f" {duplicate['game_id']} ",
        "pfr_player_id": " PfrOne00 ",
    }
    _, duplicate_manifest = _capture(
        config,
        [
            duplicate,
            whitespace_duplicate,
        ],
        acquired_at=ACQUIRED_AT + timedelta(days=1),
    )

    result = load_nflverse_participation_to_warehouse(config, manifest_path=duplicate_manifest)

    assert not result.committed
    assert result.quality.has_fatal_errors
    assert result.quality.duplicate_keys == 1
    assert warehouse.table_counts()["player_game_participation"] == 1


def test_new_capture_replaces_manifest_seasons_without_touching_other_rows(
    tmp_path: Path,
) -> None:
    config = _config(tmp_path)
    warehouse = _players(config)
    first_raw, first_manifest = _capture(
        config,
        [
            _snap("PfrOne00", "Player One", season=2024, week=1),
            _snap("PfrOne00", "Player One", week=1),
            _snap("PfrTwo00", "Player Two", week=2),
        ],
    )
    first_hash = sha256_file(first_raw)
    first_result = load_nflverse_participation_to_warehouse(config, manifest_path=first_manifest)
    assert first_result.committed

    with warehouse.connect() as connection:
        connection.execute(
            """
            INSERT INTO player_game_participation (
                season, week, game_id, player_id, pfr_game_id, pfr_player_id,
                game_type, season_type, position, nfl_team, opponent,
                offense_snaps, offense_snap_pct, defense_snaps, defense_snap_pct,
                special_teams_snaps, special_teams_snap_pct, source, as_of,
                source_dataset_id
            )
            SELECT
                season, week, game_id, player_id, pfr_game_id, pfr_player_id,
                game_type, season_type, position, nfl_team, opponent,
                offense_snaps, offense_snap_pct, defense_snaps, defense_snap_pct,
                special_teams_snaps, special_teams_snap_pct,
                'other_participation_source', as_of, 'other-dataset'
            FROM player_game_participation
            WHERE season = 2025
              AND player_id = 'p2'
              AND source = 'nflverse_pfr_snap_counts'
            """
        )

    second_raw, second_manifest = _capture(
        config,
        [_snap("PfrOne00", "Player One", week=1, offense_snaps=55)],
        acquired_at=ACQUIRED_AT + timedelta(days=1),
    )
    second_hash = sha256_file(second_raw)

    result = load_nflverse_participation_to_warehouse(config, manifest_path=second_manifest)

    assert result.committed
    assert result.participation.normalized_rows == 1
    assert result.participation.inserted_rows == 0
    assert result.participation.matched_existing_rows == 1
    assert result.participation.deleted_rows == 1
    assert result.participation.final_table_rows == 3
    with warehouse.connect(read_only=True) as connection:
        rows = connection.execute(
            "SELECT season, player_id, source, source_dataset_id, offense_snaps "
            "FROM player_game_participation "
            "ORDER BY season, source, player_id"
        ).fetchall()
    assert rows == [
        (
            2024,
            "p1",
            "nflverse_pfr_snap_counts",
            first_result.manifest.dataset_id,
            42,
        ),
        (2025, "p1", "nflverse_pfr_snap_counts", result.manifest.dataset_id, 55),
        (2025, "p2", "other_participation_source", "other-dataset", 42),
    ]
    assert sha256_file(first_raw) == first_hash
    assert sha256_file(second_raw) == second_hash

    repeated = load_nflverse_participation_to_warehouse(config, manifest_path=second_manifest)
    assert repeated.committed
    assert repeated.participation.inserted_rows == 0
    assert repeated.participation.matched_existing_rows == 1
    assert repeated.participation.deleted_rows == 0
    assert repeated.participation.final_table_rows == 3


def test_offline_snap_archive_reuses_file_and_manifest(tmp_path: Path) -> None:
    config = _config(tmp_path)
    raw_dir = config.resolve(config.paths.raw_dir) / "nflverse"
    raw_dir.mkdir(parents=True, exist_ok=True)
    raw_path = raw_dir / "nflverse_snap_counts__2025-2025__cached.parquet"
    pd.DataFrame([_snap("PfrOne00", "Player One", week=1)]).to_parquet(raw_path, index=False)
    raw_hash = sha256_file(raw_path)

    first = download_nflverse_snap_counts(config, start_season=2025, end_season=2025, offline=True)
    second = download_nflverse_snap_counts(config, start_season=2025, end_season=2025, offline=True)

    assert first.reused_offline and second.reused_offline
    assert first.snap_counts_path == raw_path
    assert first.manifest.dataset_id == second.manifest.dataset_id
    assert first.manifest_path == second.manifest_path
    assert sha256_file(raw_path) == raw_hash
