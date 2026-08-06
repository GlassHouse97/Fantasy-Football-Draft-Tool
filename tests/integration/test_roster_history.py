from __future__ import annotations

import json
from datetime import UTC, datetime
from pathlib import Path

from fantasy_draft_ai.config import (
    AppConfig,
    NetworkSection,
    PathSection,
    ProjectSection,
    TrainingSection,
)
from fantasy_draft_ai.data.warehouse import Warehouse
from fantasy_draft_ai.features.roster_construction import build_roster_history
from fantasy_draft_ai.rules.models import DraftSettings, LeagueRules
from fantasy_draft_ai.scoring.engine import ScoringRules


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
        training=TrainingSection(start_season=2016, end_season=2025),
        project_root=tmp_path,
    )


def _seed_history(config: AppConfig, *, unresolved: bool = False) -> None:
    rules = LeagueRules(
        season=2024,
        teams=4,
        draft=DraftSettings(rounds=2),
        starters={"QB": 1, "RB": 1},
        scoring=ScoringRules(),
    )
    warehouse = Warehouse(config.resolve(config.paths.warehouse))
    warehouse.initialize()
    loaded_at = datetime(2026, 8, 6, 12, tzinfo=UTC)
    player_rows = [
        (f"player-{number}", f"Player {number}", "QB" if number <= 4 else "RB")
        for number in range(1, 9)
    ]
    picks = [
        (1, 1, 1, "team-1", "player-1", "QB"),
        (2, 1, 2, "team-2", "player-2", "QB"),
        (3, 1, 3, "team-3", "player-3", "QB"),
        (4, 1, 4, "team-4", "player-4", "QB"),
        (5, 2, 4, "team-4", "player-8", "RB"),
        (6, 2, 3, "team-3", "player-7", "RB"),
        (7, 2, 2, "team-2", "player-6", "RB"),
        (8, 2, 1, "team-1", None if unresolved else "player-5", "RB"),
    ]
    with warehouse.connect() as connection:
        connection.executemany(
            """
            INSERT INTO players (
                player_id, display_name, canonical_position,
                mapping_confidence, mapping_source
            ) VALUES (?, ?, ?, 'high', 'test')
            """,
            player_rows,
        )
        connection.execute(
            """
            INSERT INTO league_rules (
                league_season_id, platform, season, team_count, draft_type, rounds,
                starter_slots_json, flex_slots_json, bench_slots, ir_slots,
                scoring_json, playoff_settings_json, normalized_ruleset_json,
                ruleset_fingerprint, source_dataset_id, row_fingerprint, loaded_at
            ) VALUES (?, 'test', 2024, 4, 'snake', 2, ?, '[]', 0, 0, ?, ?, ?, ?,
                      'history-dataset', 'rules-fingerprint', ?)
            """,
            [
                "league-alpha-2024",
                json.dumps(rules.starters),
                json.dumps(rules.scoring.model_dump(mode="json")),
                json.dumps({"playoff_start_week": 3}),
                rules.canonical_json(),
                rules.fingerprint(),
                loaded_at,
            ],
        )
        connection.execute(
            """
            INSERT INTO league_history_leagues VALUES (
                'league-alpha-2024', 'package-fingerprint', 2024, 4, ?,
                8, 8, 4, ?, true, true, ?
            )
            """,
            [rules.fingerprint(), 7 if unresolved else 8, not unresolved],
        )
        connection.executemany(
            """
            INSERT INTO draft_picks (
                league_season_id, overall_pick, round, draft_slot, team_id,
                player_id, player_name, position, source_platform, source_player_id,
                mapping_confidence, source_dataset_id, row_fingerprint, loaded_at
            ) VALUES ('league-alpha-2024', ?, ?, ?, ?, ?, ?, ?, 'test', ?, ?,
                      'history-dataset', ?, ?)
            """,
            [
                (
                    overall,
                    round_number,
                    slot,
                    team,
                    player_id,
                    f"Player {overall}",
                    position,
                    f"source-{overall}",
                    "unresolved" if player_id is None else "high",
                    f"pick-{overall}",
                    loaded_at,
                )
                for overall, round_number, slot, team, player_id, position in picks
            ],
        )
        connection.executemany(
            """
            INSERT INTO team_outcomes (
                league_season_id, team_id, wins, losses, made_playoffs,
                final_place, is_champion, source_dataset_id, row_fingerprint, loaded_at
            ) VALUES ('league-alpha-2024', ?, ?, ?, ?, ?, ?,
                      'history-dataset', ?, ?)
            """,
            [
                (f"team-{number}", 10 - number, number, number <= 2, number, number == 1,
                 f"outcome-{number}", loaded_at)
                for number in range(1, 5)
            ],
        )
        weekly_rows = []
        for week in (1, 2):
            for number, player_id, position in (
                (number, f"player-{number}", "QB" if number <= 4 else "RB")
                for number in range(1, 9)
            ):
                weekly_rows.append(
                    (
                        2024,
                        week,
                        player_id,
                        position,
                        250.0 - number * 5 if position == "QB" else 0.0,
                        2.0 if position == "QB" else 0.0,
                        80.0 - number if position == "RB" else 0.0,
                        1.0 if position == "RB" else 0.0,
                        loaded_at,
                    )
                )
        connection.executemany(
            """
            INSERT INTO player_week_stats (
                season, week, player_id, position, season_type,
                passing_yards, passing_tds, rushing_yards, rushing_tds,
                games_active, games_played, source, as_of, source_dataset_id
            ) VALUES (?, ?, ?, ?, 'REG', ?, ?, ?, ?, 1, 1, 'nflverse', ?, 'weekly-test')
            """,
            weekly_rows,
        )


def test_roster_history_build_is_descriptive_scored_and_idempotent(tmp_path: Path) -> None:
    config = _config(tmp_path)
    _seed_history(config)

    first = build_roster_history(config)
    second = build_roster_history(config)

    assert first.committed and second.committed
    assert first.build_fingerprint == second.build_fingerprint
    assert first.feature_rows == first.metric_rows == first.ready_metric_rows == 4
    with Warehouse(config.resolve(config.paths.warehouse)).connect(read_only=True) as connection:
        count_row = connection.execute(
            """
            SELECT
              (SELECT count(*) FROM roster_construction_features),
              (SELECT count(*) FROM draft_only_team_metrics)
            """
        ).fetchone()
        assert count_row is not None
        feature_count, metric_count = count_row
        payload_row = connection.execute(
            """
            SELECT feature_payload, draft_only_metrics
            FROM roster_construction_features AS features
            JOIN team_outcomes AS outcomes USING (league_season_id, team_id)
            WHERE features.team_id = 'team-1'
            """
        ).fetchone()
        assert payload_row is not None
        payload, metric = payload_row
    assert (feature_count, metric_count) == (4, 4)
    assert json.loads(str(payload))["position_pick_counts"] == {"QB": 1, "RB": 1}
    assert json.loads(str(metric))["optimal_lineup_points"] > 0


def test_draft_only_metrics_fail_closed_until_every_pick_is_mapped(tmp_path: Path) -> None:
    config = _config(tmp_path)
    _seed_history(config, unresolved=True)

    result = build_roster_history(config)

    assert result.committed
    assert result.feature_rows == result.metric_rows == 4
    assert result.ready_metric_rows == 0
    assert any(issue.code == "identity_mapping_required" for issue in result.issues)
    with Warehouse(config.resolve(config.paths.warehouse)).connect(read_only=True) as connection:
        rows = connection.execute(
            """
            SELECT status, optimal_lineup_points, drafted_starter_games,
                   starter_slot_weeks, unfilled_starter_slot_weeks
            FROM draft_only_team_metrics
            ORDER BY team_id
            """
        ).fetchall()
        outcome_metrics = connection.execute(
            "SELECT count(*) FROM team_outcomes WHERE draft_only_metrics IS NOT NULL"
        ).fetchone()
    assert rows == [("identity_mapping_required", None, None, None, None)] * 4
    assert outcome_metrics == (0,)


def test_partial_weekly_evidence_blocks_metrics_and_clears_stale_ready_payload(
    tmp_path: Path,
) -> None:
    config = _config(tmp_path)
    _seed_history(config)
    ready = build_roster_history(config)
    assert ready.ready_metric_rows == 4
    warehouse = Warehouse(config.resolve(config.paths.warehouse))
    with warehouse.connect() as connection:
        connection.execute("DELETE FROM player_week_stats WHERE week = 2")

    blocked = build_roster_history(config)

    assert blocked.committed
    assert blocked.ready_metric_rows == 0
    assert any(issue.code == "weekly_data_incomplete" for issue in blocked.issues)
    with warehouse.connect(read_only=True) as connection:
        rows = connection.execute(
            """
            SELECT status, optimal_lineup_points, drafted_starter_games
            FROM draft_only_team_metrics ORDER BY team_id
            """
        ).fetchall()
        stale_outcomes = connection.execute(
            "SELECT count(*) FROM team_outcomes WHERE draft_only_metrics IS NOT NULL"
        ).fetchone()
    assert rows == [("weekly_data_incomplete", None, None)] * 4
    assert stale_outcomes == (0,)
