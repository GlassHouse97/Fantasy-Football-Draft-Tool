from __future__ import annotations

import json
from pathlib import Path

import pytest

from fantasy_draft_ai.config import (
    AppConfig,
    NetworkSection,
    PathSection,
    ProjectSection,
    TrainingSection,
)
from fantasy_draft_ai.data.warehouse import Warehouse
from fantasy_draft_ai.services import model_lab
from fantasy_draft_ai.services.model_lab import (
    load_model_lab,
    load_player_model_explanation,
)
from fantasy_draft_ai.services.projections import (
    TARGET_FANTASY_POINTS_PER_GAME,
    TARGET_FANTASY_POINTS_TOTAL,
    TARGET_GAMES_ACTIVE,
    PlayerProjection,
    ProjectionBoard,
    ProjectionBoardStatus,
    ProjectionInterval,
    ProjectionLineage,
    ProjectionRun,
)


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


def _validated_board() -> ProjectionBoard:
    lineage = ProjectionLineage(
        feature_data_fingerprint="feature",
        target_data_fingerprint="target",
        build_fingerprint="build",
        scoring_ruleset_fingerprint="rules",
        baseline_report_fingerprint="baseline-report",
        model_feature_fingerprint="model-features",
        model_config_fingerprint="model-config",
    )
    run = ProjectionRun(
        run_id="run-validated",
        status="complete",
        trained_at="2026-08-06T00:00:00+00:00",
        prediction_season=2026,
        lineage=lineage,
        split_seasons=[2020, 2021, 2025],
        feature_rows=1,
        target_rows=1,
        training_rows=1,
        prediction_rows=1,
        evaluated_rows=1,
        live_prediction_rows=1,
        candidate_rows=1,
        model_rows=1,
        champion_rows=1,
    )
    targets = {
        TARGET_FANTASY_POINTS_PER_GAME: ProjectionInterval(10.0, 12.0, 14.0, "learned", "ridge"),
        TARGET_GAMES_ACTIVE: ProjectionInterval(14.0, 16.0, 17.0, "baseline", "weighted"),
        TARGET_FANTASY_POINTS_TOTAL: ProjectionInterval(
            150.0, 190.0, 220.0, "baseline", "weighted"
        ),
    }
    row = PlayerProjection(
        run_id=run.run_id,
        player_id="player-1",
        display_name="Example Receiver",
        prediction_season=2026,
        position="WR",
        prediction_status="learned_validated",
        targets=targets,
        explanation={
            TARGET_FANTASY_POINTS_PER_GAME: {
                "explanation_type": "local_position_reference_perturbation",
                "interpretation": "Associative, not causal.",
                "target_name": TARGET_FANTASY_POINTS_PER_GAME,
                "top_factors": [
                    {
                        "rank": 1,
                        "feature": "lag1_fantasy_points_per_game",
                        "direction": "increases_prediction",
                        "player_value": 13.0,
                        "position_reference_value": 8.0,
                        "prediction_delta": 1.5,
                    }
                ],
            }
        },
    )
    return ProjectionBoard(
        status=ProjectionBoardStatus(
            True,
            "available",
            "validated",
            run=run,
            row_count=1,
            learned_selection_rows=1,
        ),
        rows=(row,),
    )


def _insert_model_lab_artifacts(config: AppConfig) -> None:
    warehouse = Warehouse(config.resolve(config.paths.warehouse))
    warehouse.initialize()
    card = config.project_root / "docs/model_cards/test.md"
    plot = config.project_root / "docs/images/test.svg"
    card.parent.mkdir(parents=True)
    plot.parent.mkdir(parents=True)
    card.write_text("# Test model\n", encoding="utf-8")
    plot.write_text("<svg></svg>\n", encoding="utf-8")
    phase3 = {
        "metrics": [
            {
                "baseline": "previous_season",
                "target": TARGET_FANTASY_POINTS_PER_GAME,
                "fold_label": "validation",
                "evaluation_season": 2020,
                "segment": "all",
                "rows": 10,
                "mae": 3.0,
                "rmse": 4.0,
                "median_absolute_error": 2.5,
                "spearman_rank_correlation": 0.7,
            }
        ]
    }
    phase4 = {
        "feature_contract": {
            "numeric_features": ["prediction_season", "lag1_fantasy_points_per_game"],
            "categorical_features": ["previous_team"],
        },
        "folds": [
            {
                "label": "validation",
                "evaluation_season": 2020,
                "training_seasons": [2016, 2017, 2018, 2019],
            },
            {
                "label": "test",
                "evaluation_season": 2025,
                "training_seasons": [2016, 2017, 2018, 2019, 2020, 2021, 2022, 2023, 2024],
            },
        ],
        "detailed_metrics": [
            {
                "candidate_name": "ridge",
                "candidate_source": "learned",
                "target_name": TARGET_FANTASY_POINTS_PER_GAME,
                "position": "WR",
                "evaluation_scope": "test",
                "evaluation_seasons": [2025],
                "rows": 1,
                "mae": 2.0,
                "rmse": 2.0,
                "median_absolute_error": 2.0,
                "spearman_rank_correlation": 0.8,
                "top_n_capture_rate": 0.75,
            }
        ],
        "champions": [
            {
                "position": "WR",
                "target_name": TARGET_FANTASY_POINTS_PER_GAME,
                "selected_source": "learned",
                "selected_name": "ridge",
                "selection_metric": "pooled_validation_mae",
                "selection_value": 2.0,
                "reference_baseline_name": "previous_season",
                "reference_baseline_value": 3.0,
                "mae_improvement_over_best_baseline": 1.0,
                "decision_status": "learned_significant_improvement_selected",
            }
        ],
        "global_explanations": [
            {
                "position": "WR",
                "target_name": TARGET_FANTASY_POINTS_PER_GAME,
                "model_family": "ridge",
                "importance": [
                    {
                        "feature": "lag1_fantasy_points_per_game",
                        "rank": 1,
                        "importance_mean": 1.2,
                        "importance_std": 0.1,
                        "explanation_scope": "training rows",
                    }
                ],
            }
        ],
        "diagnostic_plots": {"test_residuals": "docs/images/test.svg"},
        "limitations": ["Associative explanations are not causal."],
    }
    with warehouse.connect() as connection:
        connection.execute(
            """
            INSERT INTO baseline_evaluation_metadata (
                report_fingerprint, baseline_version, feature_data_fingerprint,
                target_data_fingerprint, build_fingerprint,
                scoring_ruleset_fingerprint, prediction_rows, evaluated_rows,
                report_payload
            ) VALUES ('baseline-report', 'v1', 'feature', 'target', 'build',
                      'rules', 1, 1, ?)
            """,
            [json.dumps(phase3)],
        )
        connection.execute(
            """
            INSERT INTO player_projection_evaluation_metadata (
                report_fingerprint, run_id, feature_data_fingerprint,
                target_data_fingerprint, build_fingerprint,
                scoring_ruleset_fingerprint, baseline_report_fingerprint,
                model_feature_fingerprint, model_config_fingerprint,
                prediction_rows, evaluated_rows, live_prediction_rows,
                candidate_rows, champion_rows, report_payload
            ) VALUES ('phase4-report', 'run-validated', 'feature', 'target', 'build',
                      'rules', 'baseline-report', 'model-features', 'model-config',
                      1, 1, 1, 1, 1, ?)
            """,
            [json.dumps(phase4)],
        )
        connection.execute(
            """
            INSERT INTO player_projection_models (
                model_id, run_id, model_family, target_name, position,
                training_seasons, training_rows, feature_names,
                categorical_feature_names, hyperparameters, uncertainty_method,
                artifact_path, artifact_sha256, artifact_size_bytes,
                model_card_path, model_card_sha256, package_versions
            ) VALUES ('model-1', 'run-validated', 'ridge', ?, 'WR', '[2016,2017]',
                      10, '["prediction_season"]', '["previous_team"]', '{}',
                      'residuals', 'models/test.joblib', 'hash', 1,
                      'docs/model_cards/test.md', 'hash', '{}')
            """,
            [TARGET_FANTASY_POINTS_PER_GAME],
        )
        connection.execute(
            """
            INSERT INTO player_projection_predictions (
                run_id, player_id, prediction_season, position, target_name,
                model_family, prediction_scope, fold_label, training_max_season,
                predicted_value, p10, p50, p90, actual_value, actual_games_active,
                experience, experience_group, feature_data_fingerprint,
                target_data_fingerprint, build_fingerprint,
                scoring_ruleset_fingerprint, baseline_report_fingerprint,
                model_feature_fingerprint, model_config_fingerprint
            ) VALUES ('run-validated', 'player-1', 2025, 'WR', ?, 'ridge', 'test',
                      'test_2025', 2024, 12.0, 10.0, 12.0, 14.0, 10.0, 16.0,
                      3, 'veteran', 'feature', 'target', 'build', 'rules',
                      'baseline-report', 'model-features', 'model-config')
            """,
            [TARGET_FANTASY_POINTS_PER_GAME],
        )


def test_model_lab_degrades_gracefully_when_phase4_is_missing(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    config = _config(tmp_path)
    monkeypatch.setattr(
        model_lab,
        "load_projection_board",
        lambda _config: ProjectionBoard(
            ProjectionBoardStatus(False, "not_built", "train and validate Phase 4 first")
        ),
    )

    snapshot = load_model_lab(config)

    assert not snapshot.available
    assert snapshot.status.code == "not_built"
    assert len(snapshot.targets) == 3
    assert snapshot.features
    assert not snapshot.model_metrics
    assert not snapshot.model_cards


def test_model_lab_reads_validated_reports_metrics_and_diagnostics(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    config = _config(tmp_path)
    board = _validated_board()
    _insert_model_lab_artifacts(config)
    monkeypatch.setattr(model_lab, "load_projection_board", lambda _config: board)

    snapshot = load_model_lab(config)

    assert snapshot.available
    assert snapshot.run_id == "run-validated"
    assert [fold.evaluation_season for fold in snapshot.folds] == [2020, 2025]
    assert all(fold.leakage_safe for fold in snapshot.folds)
    assert snapshot.baseline_metrics[0].candidate_name == "previous_season"
    assert snapshot.model_metrics[0].candidate_name == "ridge"
    assert snapshot.selections[0].improvement == 1.0
    assert snapshot.residuals[0].mean_actual_minus_prediction == -2.0
    assert snapshot.residuals[0].mae == 2.0
    assert snapshot.feature_importance[0].feature == "lag1_fantasy_points_per_game"
    assert snapshot.model_cards[0].exists
    assert snapshot.diagnostics[0].exists
    assert snapshot.players[0].player_id == "player-1"
    assert snapshot.limitations == ("Associative explanations are not causal.",)


def test_player_explanation_uses_served_board_payload_without_training(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    config = _config(tmp_path)
    board = _validated_board()
    monkeypatch.setattr(model_lab, "load_projection_board", lambda _config: board)

    explanation = load_player_model_explanation(
        config,
        "player-1",
        TARGET_FANTASY_POINTS_PER_GAME,
    )
    missing = load_player_model_explanation(
        config,
        "missing-player",
        TARGET_FANTASY_POINTS_PER_GAME,
    )

    assert explanation.available
    assert explanation.method_label == "Learned model"
    assert explanation.p50 == 12.0
    assert explanation.factors[0].feature == "lag1_fantasy_points_per_game"
    assert explanation.factors[0].prediction_delta == 1.5
    assert "not causal" in explanation.interpretation
    assert not missing.available
    assert missing.code == "player_not_found"


def test_model_lab_rejects_non_chronological_report(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    config = _config(tmp_path)
    board = _validated_board()
    _insert_model_lab_artifacts(config)
    warehouse = Warehouse(config.resolve(config.paths.warehouse))
    with warehouse.connect() as connection:
        payload = {
            "feature_contract": {"numeric_features": ["prediction_season"]},
            "folds": [
                {
                    "label": "test",
                    "evaluation_season": 2025,
                    "training_seasons": [2025],
                }
            ],
        }
        connection.execute(
            "UPDATE player_projection_evaluation_metadata SET report_payload = ?",
            [json.dumps(payload)],
        )
    monkeypatch.setattr(model_lab, "load_projection_board", lambda _config: board)

    snapshot = load_model_lab(config)

    assert not snapshot.available
    assert snapshot.status.code == "invalid_splits"
