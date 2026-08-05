from __future__ import annotations

import json
from datetime import UTC, datetime
from pathlib import Path

import pytest

from fantasy_draft_ai.config import (
    AppConfig,
    NetworkSection,
    PathSection,
    ProjectSection,
    TrainingSection,
)
from fantasy_draft_ai.data.audit import audit_project_data
from fantasy_draft_ai.data.warehouse import Warehouse
from fantasy_draft_ai.features.player_seasons import build_player_season_features
from fantasy_draft_ai.models.baselines.evaluate import evaluate_baselines
from fantasy_draft_ai.rules.models import DraftSettings, LeagueRules
from fantasy_draft_ai.scoring.engine import ScoringRules
from fantasy_draft_ai.services.status import project_status

AS_OF = datetime(2026, 8, 5, 12, 0, tzinfo=UTC)
IDENTITY_AS_OF = datetime(2020, 8, 1, 12, 0, tzinfo=UTC)
STANDARD_RULES = LeagueRules(
    season=2025,
    teams=12,
    draft=DraftSettings(rounds=5),
    starters={"QB": 1, "RB": 1, "WR": 1, "TE": 1},
    bench=1,
    scoring=ScoringRules(),
)


def _config(project_root: Path) -> AppConfig:
    return AppConfig(
        project=ProjectSection(name="Baseline integration test", prediction_season=2025),
        paths=PathSection(
            data_dir=Path("data"),
            raw_dir=Path("data/raw"),
            processed_dir=Path("data/processed"),
            warehouse=Path("data/warehouse/test.duckdb"),
            manifests=Path("data/raw/manifests"),
        ),
        network=NetworkSection(timeout_seconds=5, user_agent="phase-3-test"),
        training=TrainingSection(start_season=2020, end_season=2024),
        project_root=project_root,
    )


def _seed_player(
    warehouse: Warehouse,
    player_id: str,
    position: str,
    *,
    rookie_season: int | None = None,
) -> None:
    with warehouse.connect() as connection:
        connection.execute(
            "INSERT INTO players "
            "(player_id, gsis_id, display_name, canonical_position, birth_date, rookie_season, "
            "mapping_confidence, mapping_source, identity_source_dataset_id, "
            "identity_source_as_of) VALUES (?, ?, ?, ?, DATE '2000-01-01', ?, "
            "'exact', 'phase-3-test', 'identity-test', ?)",
            [
                player_id,
                player_id,
                f"Player {player_id}",
                position,
                rookie_season,
                IDENTITY_AS_OF,
            ],
        )


def _seed_season(
    warehouse: Warehouse,
    *,
    player_id: str,
    position: str,
    season: int,
    fantasy_points: float,
) -> None:
    # Receiving yards are used only to make the expected fantasy totals exact and readable.
    # Position still comes from the time-indexed weekly/participation records.
    receiving_yards = fantasy_points * 10
    game_id = f"{season}_01_BUF_MIA"
    with warehouse.connect() as connection:
        connection.execute(
            """
            INSERT INTO player_week_stats (
                season, week, player_id, position, season_type, game_id, nfl_team, opponent,
                completions, passing_attempts, passing_yards, passing_tds, interceptions,
                rushing_yards, rushing_tds, receiving_yards, receptions, receiving_tds,
                targets, carries, two_point_conversions, fumbles_lost, special_teams_tds,
                source, as_of, source_dataset_id
            ) VALUES (
                ?, 1, ?, ?, 'REG', ?, 'BUF', 'MIA',
                0, 0, 0, 0, 0, 0, 0, ?, 0, 0, 0, 0, 0, 0, 0,
                'nflverse', ?, ?
            )
            """,
            [
                season,
                player_id,
                position,
                game_id,
                receiving_yards,
                AS_OF,
                f"weekly-{season}",
            ],
        )
        connection.execute(
            """
            INSERT INTO player_game_participation (
                season, week, game_id, player_id, pfr_game_id, pfr_player_id,
                game_type, season_type, position, nfl_team, opponent,
                offense_snaps, offense_snap_pct, defense_snaps, defense_snap_pct,
                special_teams_snaps, special_teams_snap_pct, source, as_of,
                source_dataset_id
            ) VALUES (
                ?, 1, ?, ?, ?, ?, 'REG', 'REG', ?, 'BUF', 'MIA',
                40, NULL, 0, NULL, 0, NULL, 'nflverse_pfr_snap_counts', ?, ?
            )
            """,
            [
                season,
                game_id,
                player_id,
                f"pfr-{game_id}",
                f"pfr-{player_id}",
                position,
                AS_OF,
                f"snaps-{season}",
            ],
        )


def test_baseline_evaluation_is_chronological_reports_metrics_and_uses_rookie_fallback(
    tmp_path: Path,
) -> None:
    config = _config(tmp_path)
    warehouse = Warehouse(config.resolve(config.paths.warehouse))
    warehouse.initialize()
    _seed_player(warehouse, "qb-a", "QB")
    _seed_player(warehouse, "qb-b", "QB")
    _seed_player(warehouse, "wr-vet", "WR")
    _seed_player(warehouse, "rookie", "WR", rookie_season=2023)
    for season, points in zip(range(2020, 2025), (0, 10, 20, 30, 40), strict=True):
        _seed_season(
            warehouse,
            player_id="qb-a",
            position="QB",
            season=season,
            fantasy_points=points,
        )
    for season, points in zip(range(2020, 2025), (10, 20, 30, 40, 50), strict=True):
        _seed_season(
            warehouse,
            player_id="qb-b",
            position="QB",
            season=season,
            fantasy_points=points,
        )
    for season, points in zip(range(2020, 2025), (15, 25, 35, 45, 55), strict=True):
        _seed_season(
            warehouse,
            player_id="wr-vet",
            position="WR",
            season=season,
            fantasy_points=points,
        )
    # This player has a 2023 outcome but no 2022 feature history. Evaluation must use an
    # explicit position fallback instead of silently predicting zero or dropping the row.
    _seed_season(
        warehouse,
        player_id="rookie",
        position="WR",
        season=2023,
        fantasy_points=35,
    )
    _seed_season(
        warehouse,
        player_id="rookie",
        position="WR",
        season=2024,
        fantasy_points=45,
    )
    feature_result = build_player_season_features(config, STANDARD_RULES, prediction_season=2025)
    assert feature_result.committed, feature_result.render()
    assert not feature_result.quality.has_fatal_errors

    first_report = tmp_path / "baseline-evaluation.md"
    first = evaluate_baselines(
        config,
        STANDARD_RULES,
        first_evaluation_season=2023,
        last_evaluation_season=2024,
        output_path=first_report,
    )
    second = evaluate_baselines(
        config,
        STANDARD_RULES,
        first_evaluation_season=2023,
        last_evaluation_season=2024,
        output_path=tmp_path / "baseline-evaluation-repeat.md",
    )

    first_records = first.report["metrics"]
    second_records = second.report["metrics"]
    assert first.committed and second.committed
    assert first_report.is_file()
    assert first_records
    assert first_records == second_records
    assert first.report["target_data_fingerprint"] == feature_result.target_fingerprint
    assert first.report["build_fingerprint"] == feature_result.build_fingerprint
    assert any(
        row["scope"] == "active_only" and row["segment"] == "positive_games"
        for row in first_records
    )
    assert any(
        row["fold_label"] == "aggregate" and row["position"] == "ALL"
        for row in first.report["candidate_outcomes"]
    )
    assert first.report["folds"] == [
        {
            "training_seasons": [2021, 2022],
            "evaluation_season": 2023,
            "label": "validation",
        },
        {
            "training_seasons": [2021, 2022, 2023],
            "evaluation_season": 2024,
            "label": "test",
        },
    ]

    prior_qb_2023 = [
        record
        for record in first_records
        if record["baseline"] == "previous_season"
        and record.get("evaluation_season") == 2023
        and record["scope"] == "position"
        and record["segment"] == "QB"
        and record["target"] == "fantasy_points_total"
    ]
    assert prior_qb_2023, first.report
    metrics = prior_qb_2023[0]
    assert float(metrics["mae"]) == pytest.approx(10)
    assert float(metrics["rmse"]) == pytest.approx(10)
    median_key = "median_absolute_error" if "median_absolute_error" in metrics else "median_ae"
    assert float(metrics[median_key]) == pytest.approx(10)
    weighted_qb_2023 = [
        record
        for record in first_records
        if record["baseline"] == "weighted_history"
        and record.get("evaluation_season") == 2023
        and record["scope"] == "position"
        and record["segment"] == "QB"
        and record["target"] == "fantasy_points_total"
    ]
    assert len(weighted_qb_2023) == 1
    assert float(weighted_qb_2023[0]["mae"]) == pytest.approx(15)
    with warehouse.connect(read_only=True) as connection:
        qb_a_features = connection.execute(
            "SELECT feature_payload FROM player_season_features "
            "WHERE player_id = 'qb-a' AND prediction_season = 2023"
        ).fetchone()
        rookie_fallback = connection.execute(
            "SELECT predicted_value, actual_value, experience_group "
            "FROM baseline_predictions WHERE player_id = 'rookie' "
            "AND prediction_season = 2023 AND target_name = 'fantasy_points_total' "
            "AND baseline_name = 'previous_season'"
        ).fetchone()
        evaluation_metadata = connection.execute(
            "SELECT count(*), min(evaluated_rows), max(evaluated_rows) "
            "FROM baseline_evaluation_metadata"
        ).fetchone()
    assert qb_a_features is not None
    feature_payload = json.loads(qb_a_features[0])
    assert float(feature_payload["weighted_3yr_fantasy_points_per_game"]) == pytest.approx(15)
    assert rookie_fallback is not None
    assert float(rookie_fallback[0]) > 0
    assert float(rookie_fallback[1]) == 35
    assert rookie_fallback[2] == "rookie"
    assert evaluation_metadata == (
        1,
        int(second.report["evaluated_rows"]),
        int(second.report["evaluated_rows"]),
    )

    rendered = first_report.read_text(encoding="utf-8").lower()
    assert "previous" in rendered
    assert "weighted" in rendered
    assert feature_result.data_fingerprint.lower() in rendered

    with warehouse.connect() as connection:
        connection.execute(
            "UPDATE player_week_stats SET receiving_yards = receiving_yards + 10 "
            "WHERE player_id = 'qb-a' AND season = 2024"
        )
    rebuilt = build_player_season_features(config, STANDARD_RULES, prediction_season=2025)
    assert rebuilt.committed
    assert rebuilt.build_fingerprint != feature_result.build_fingerprint
    with warehouse.connect(read_only=True) as connection:
        invalidated = connection.execute(
            "SELECT (SELECT count(*) FROM baseline_predictions), "
            "(SELECT count(*) FROM baseline_evaluation_metadata)"
        ).fetchone()
    assert invalidated == (0, 0)
    baseline_status = next(
        item for item in project_status(config) if item.name == "Transparent projection baselines"
    )
    assert not baseline_status.available
    assert audit_project_data(config).passed

    refreshed = evaluate_baselines(
        config,
        STANDARD_RULES,
        first_evaluation_season=2023,
        last_evaluation_season=2024,
        output_path=tmp_path / "baseline-evaluation-refreshed.md",
    )
    assert refreshed.committed
    assert refreshed.report["build_fingerprint"] == rebuilt.build_fingerprint
    baseline_status = next(
        item for item in project_status(config) if item.name == "Transparent projection baselines"
    )
    assert baseline_status.available
    assert audit_project_data(config).passed

    with warehouse.connect() as connection:
        connection.execute(
            """
            INSERT INTO feature_build_metadata
            SELECT
                'legacy-feature', 'legacy-target', 'legacy-build', feature_version,
                scoring_ruleset_fingerprint, start_prediction_season,
                end_prediction_season, feature_rows, target_rows, source_dataset_ids,
                source_max_as_of, quality_payload
            FROM feature_build_metadata
            """
        )
    stale_status = next(
        item for item in project_status(config) if item.name == "Transparent projection baselines"
    )
    assert not stale_status.available
    assert not audit_project_data(config).passed

    with warehouse.connect() as connection:
        connection.execute(
            "DELETE FROM feature_build_metadata WHERE data_fingerprint = 'legacy-feature'"
        )
    assert audit_project_data(config).passed
    with warehouse.connect() as connection:
        connection.execute("DELETE FROM baseline_predictions")
    empty_status = next(
        item for item in project_status(config) if item.name == "Transparent projection baselines"
    )
    assert not empty_status.available
    assert not audit_project_data(config).passed


def test_evaluation_is_blocked_without_a_validated_feature_build(tmp_path: Path) -> None:
    config = _config(tmp_path)
    Warehouse(config.resolve(config.paths.warehouse)).initialize()
    output_path = tmp_path / "must-not-exist.md"

    result = evaluate_baselines(
        config,
        STANDARD_RULES,
        first_evaluation_season=2023,
        last_evaluation_season=2024,
        output_path=output_path,
    )

    assert not result.committed
    assert result.report["status"] == "FAILED"
    assert any(
        "valid" in issue.lower() and "feature" in issue.lower() for issue in result.report["issues"]
    )
    assert not output_path.exists()
