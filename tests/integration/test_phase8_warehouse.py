from __future__ import annotations

from collections.abc import Callable
from datetime import UTC, datetime
from pathlib import Path

import duckdb

from fantasy_draft_ai.config import (
    AppConfig,
    NetworkSection,
    PathSection,
    ProjectSection,
    TrainingSection,
)
from fantasy_draft_ai.data.audit import audit_project_data
from fantasy_draft_ai.data.warehouse import Warehouse
from fantasy_draft_ai.draft.pool import FrozenDraftPlayer
from fantasy_draft_ai.draft.repository import DraftRepository
from fantasy_draft_ai.rules.models import LeagueRules


def _config(tmp_path: Path) -> AppConfig:
    return AppConfig(
        project=ProjectSection(name="test", prediction_season=2026, random_seed=42),
        paths=PathSection(
            data_dir=Path("data"),
            raw_dir=Path("data/raw"),
            processed_dir=Path("data/processed"),
            warehouse=Path("data/warehouse.duckdb"),
            manifests=Path("data/raw/manifests"),
        ),
        network=NetworkSection(timeout_seconds=30, user_agent="tests"),
        training=TrainingSection(start_season=2020, end_season=2025),
        project_root=tmp_path,
    )


def _phase6_snapshot(path: Path) -> dict[str, tuple[tuple[str, ...], list[tuple[object, ...]]]]:
    tables = (
        "draft_sessions",
        "draft_session_players",
        "draft_events",
        "draft_recommendation_runs",
    )
    snapshot: dict[str, tuple[tuple[str, ...], list[tuple[object, ...]]]] = {}
    with duckdb.connect(str(path), read_only=True) as connection:
        for table in tables:
            columns = tuple(
                str(row[1])
                for row in connection.execute(f"PRAGMA table_info('{table}')").fetchall()
            )
            rows = connection.execute(f"SELECT * FROM {table} ORDER BY ALL").fetchall()
            snapshot[table] = (columns, rows)
    return snapshot


def test_phase8_migration_preserves_phase6_schema_rows_and_replay(
    tmp_path: Path,
    rules_factory: Callable[..., LeagueRules],
) -> None:
    path = tmp_path / "warehouse.duckdb"
    repository = DraftRepository(path)
    rules = rules_factory(teams=4, qb=1, rb=0, wr=0, te=0, flex_count=0, bench=0)
    players = tuple(
        FrozenDraftPlayer(
            player_id=f"player-{index}",
            display_name=f"Player {index}",
            position="QB",
            p10=10.0,
            p50=20.0,
            p90=30.0,
            prediction_status="validated",
            projection_source="learned",
            projection_method="fixture",
        )
        for index in range(1, 5)
    )
    repository.create_session(
        session_id="phase6-preserved",
        command_id="create-phase6-preserved",
        session_name="Migration regression",
        rules=rules,
        user_draft_slot=1,
        projection_run_id="phase4-fixture",
        adp_build_fingerprint=None,
        players=players,
        engine_config_fingerprint="engine-fixture",
        recommendation_status="identity_mapping_required",
        recommendation_message="fixture has no market mappings",
        random_seed=42,
        simulation_count=10,
    )
    expected_state = repository.record_pick(
        "phase6-preserved",
        "player-1",
        expected_version=0,
        command_id="pick-player-1",
    )
    with duckdb.connect(str(path)) as connection:
        for table in (
            "league_history_imports",
            "league_history_leagues",
            "roster_construction_features",
            "draft_only_team_metrics",
        ):
            connection.execute(f"DROP TABLE {table}")
        for table, columns in (
            (
                "league_rules",
                ("draft_date", "source_dataset_id", "row_fingerprint", "loaded_at"),
            ),
            (
                "draft_picks",
                (
                    "position",
                    "source_platform",
                    "source_player_id",
                    "mapping_confidence",
                    "source_dataset_id",
                    "row_fingerprint",
                    "loaded_at",
                ),
            ),
            ("team_outcomes", ("source_dataset_id", "row_fingerprint", "loaded_at")),
        ):
            for column in columns:
                connection.execute(f"ALTER TABLE {table} DROP COLUMN {column}")
    before = _phase6_snapshot(path)

    warehouse = Warehouse(path)
    warehouse.initialize()
    warehouse.initialize()

    assert _phase6_snapshot(path) == before
    assert repository.verify_session("phase6-preserved") == expected_state
    assert before["draft_sessions"][0] == (
        "session_id",
        "session_name",
        "status",
        "ruleset_json",
        "ruleset_fingerprint",
        "scoring_fingerprint",
        "team_count",
        "rounds",
        "user_draft_slot",
        "projection_run_id",
        "adp_build_fingerprint",
        "player_pool_fingerprint",
        "engine_config_fingerprint",
        "player_pool_rows",
        "mapped_market_rows",
        "recommendation_status",
        "recommendation_message",
        "random_seed",
        "simulation_count",
        "current_version",
        "state_fingerprint",
        "created_at",
        "updated_at",
    )
    assert before["draft_events"][0] == (
        "session_id",
        "sequence",
        "event_id",
        "event_type",
        "occurred_at",
        "command_id",
        "payload",
        "prior_state_fingerprint",
        "resulting_state_fingerprint",
    )


def test_empty_phase8_history_does_not_fail_project_audit(tmp_path: Path) -> None:
    config = _config(tmp_path)
    Warehouse(config.resolve(config.paths.warehouse)).initialize()

    result = audit_project_data(config)

    assert result.passed
    assert result.table_counts["league_history_imports"] == 0
    assert result.table_counts["league_history_leagues"] == 0


def test_phase8_history_audit_reconciles_counts_fingerprints_and_lineage(
    tmp_path: Path,
    rules_factory: Callable[..., LeagueRules],
) -> None:
    config = _config(tmp_path)
    warehouse = Warehouse(config.resolve(config.paths.warehouse))
    warehouse.initialize()
    rules = rules_factory(teams=4, qb=1, rb=0, wr=0, te=0, flex_count=0, bench=0)
    package_fingerprint = "a" * 64
    raw_sha256 = "b" * 64
    normalized_fingerprint = "c" * 64
    row_fingerprint = "d" * 64
    dataset_id = "history-dataset"
    loaded_at = datetime(2026, 8, 6, 19, tzinfo=UTC)
    player_rows = [
        (f"player-{index}", f"Player {index}", "QB", "exact", "fixture")
        for index in range(1, 5)
    ]
    with warehouse.connect() as connection:
        connection.executemany(
            """
            INSERT INTO players (
                player_id, display_name, canonical_position,
                mapping_confidence, mapping_source
            ) VALUES (?, ?, ?, ?, ?)
            """,
            player_rows,
        )
        connection.execute(
            """
            INSERT INTO league_rules (
                league_season_id, platform, season, team_count, user_draft_slot,
                draft_date, draft_type, rounds, starter_slots_json, flex_slots_json,
                bench_slots, ir_slots, scoring_json, playoff_settings_json,
                normalized_ruleset_json, ruleset_fingerprint, source_dataset_id,
                row_fingerprint, loaded_at
            ) VALUES (?, 'espn', ?, ?, NULL, ?, 'snake', ?, ?, '[]', 0, 0, ?, NULL,
                      ?, ?, ?, ?, ?)
            """,
            [
                "league-2025",
                rules.season,
                rules.teams,
                loaded_at,
                rules.draft.rounds,
                rules.model_dump_json(),
                rules.scoring.model_dump_json(),
                rules.canonical_json(),
                rules.fingerprint(),
                dataset_id,
                row_fingerprint,
                loaded_at,
            ],
        )
        connection.executemany(
            """
            INSERT INTO draft_picks (
                league_season_id, overall_pick, round, draft_slot, team_id,
                player_id, player_name, position, source_platform, source_player_id,
                mapping_confidence, is_keeper, is_autopick, picked_at, adp_snapshot_id,
                source_dataset_id, row_fingerprint, loaded_at
            ) VALUES ('league-2025', ?, 1, ?, ?, ?, ?, 'QB', 'espn', ?, 'exact',
                      FALSE, FALSE, NULL, NULL, ?, ?, ?)
            """,
            [
                (
                    index,
                    index,
                    f"team-{index}",
                    f"player-{index}",
                    f"Player {index}",
                    f"espn-{index}",
                    dataset_id,
                    row_fingerprint,
                    loaded_at,
                )
                for index in range(1, 5)
            ],
        )
        connection.executemany(
            """
            INSERT INTO team_outcomes (
                league_season_id, team_id, wins, losses, ties, points_for,
                points_against, all_play_percentile, points_percentile, seed,
                made_playoffs, final_place, is_champion, draft_only_metrics,
                source_dataset_id, row_fingerprint, loaded_at
            ) VALUES ('league-2025', ?, 1, 1, 0, 100, 90, NULL, NULL, ?,
                      TRUE, ?, ?, NULL, ?, ?, ?)
            """,
            [
                (
                    f"team-{index}",
                    index,
                    index,
                    index == 1,
                    dataset_id,
                    row_fingerprint,
                    loaded_at,
                )
                for index in range(1, 5)
            ],
        )
        connection.execute(
            """
            INSERT INTO league_history_imports VALUES (
                ?, 'league-history-v1', ?, 'data/raw/history.zip', ?, ?, 'complete',
                1, 1, 4, 4, 0, '{}', ?
            )
            """,
            [
                package_fingerprint,
                dataset_id,
                raw_sha256,
                normalized_fingerprint,
                loaded_at,
            ],
        )
        connection.execute(
            """
            INSERT INTO league_history_leagues VALUES (
                'league-2025', ?, ?, ?, ?, 4, 4, 4, 4, TRUE, TRUE, TRUE
            )
            """,
            [package_fingerprint, rules.season, rules.teams, rules.fingerprint()],
        )

    valid = audit_project_data(config)
    assert valid.passed

    with warehouse.connect() as connection:
        connection.execute(
            "UPDATE league_history_leagues SET actual_pick_rows = 3 "
            "WHERE league_season_id = 'league-2025'"
        )
    invalid = audit_project_data(config)
    assert not invalid.passed
    assert "League-history league row accounting or readiness is inconsistent." in invalid.failures
