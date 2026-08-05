from __future__ import annotations

from pathlib import Path
from types import SimpleNamespace
from typing import Any

import numpy as np
import pytest

from fantasy_draft_ai.config import (
    AppConfig,
    NetworkSection,
    PathSection,
    ProjectSection,
    TrainingSection,
)
from fantasy_draft_ai.models.player_projection.config import PlayerModelConfig
from fantasy_draft_ai.models.player_projection.dataset import (
    PlayerSeasonModelRow,
    prepare_model_dataset,
)
from fantasy_draft_ai.models.player_projection.repository import FrozenProjectionContract
from fantasy_draft_ai.models.player_projection.train import (
    _build_live_board,
    _detailed_metrics,
    _prediction_records,
)
from fantasy_draft_ai.models.player_projection.uncertainty import ResidualCalibration


class _ConstantPredictor:
    def __init__(self, value: float) -> None:
        self.value = value

    def predict(self, features: Any) -> np.ndarray[Any, np.dtype[np.float64]]:
        return np.full(len(features), self.value, dtype=float)


def _model_config() -> PlayerModelConfig:
    return PlayerModelConfig(
        positions=("WR",),
        numeric_features=(
            "prediction_season",
            "history_seasons",
            "nfl_experience_years",
            "position_prior_fantasy_points_per_game",
            "position_prior_games_active",
        ),
        categorical_features=("previous_team",),
    )


def _row(*, player_id: str, rookie: bool) -> PlayerSeasonModelRow:
    return PlayerSeasonModelRow(
        player_id=player_id,
        prediction_season=2026,
        position="WR",
        features={
            "is_rookie": rookie,
            "history_seasons": 0 if rookie else 3,
            "nfl_experience_years": 0 if rookie else 4,
            "position_prior_fantasy_points_per_game": 8.0,
            "position_prior_games_active": 12.0,
            "previous_team": None if rookie else "BUF",
        },
        targets=None,
    )


def _contract(rows: tuple[PlayerSeasonModelRow, ...]) -> FrozenProjectionContract:
    return FrozenProjectionContract(
        rows=rows,
        feature_data_fingerprint="feature",
        target_data_fingerprint="target",
        build_fingerprint="build",
        scoring_ruleset_fingerprint="rules",
        baseline_report_fingerprint="baseline-report",
        feature_rows=len(rows),
        target_rows=0,
        folds=(
            {
                "training_seasons": [2020, 2021, 2022, 2023],
                "evaluation_season": 2024,
                "label": "validation",
            },
            {
                "training_seasons": [2020, 2021, 2022, 2023, 2024],
                "evaluation_season": 2025,
                "label": "test",
            },
        ),
        baseline_report={"status": "PASSED"},
    )


def _calibration(target_name: str, offsets: tuple[float, float, float]) -> ResidualCalibration:
    return ResidualCalibration(
        target_name=target_name,
        prediction_season=2026,
        residual_count=3,
        residual_seasons=(2022, 2023, 2024),
        quantiles=(0.1, 0.5, 0.9),
        residual_offsets=offsets,
        games_active_bounds=(0.0, 18.0),
        fingerprint=f"calibration-{target_name}",
    )


def _app_config(tmp_path: Path) -> AppConfig:
    return AppConfig(
        project=ProjectSection(name="test", prediction_season=2026, random_seed=42),
        paths=PathSection(
            data_dir=Path("data"),
            raw_dir=Path("data/raw"),
            processed_dir=Path("data/processed"),
            warehouse=Path("data/warehouse.duckdb"),
            manifests=Path("data/manifests"),
        ),
        network=NetworkSection(timeout_seconds=30, user_agent="tests"),
        training=TrainingSection(start_season=2016, end_season=2025),
        project_root=tmp_path,
    )


def test_prediction_records_persist_the_residual_adjusted_p50_as_the_scored_center() -> None:
    config = _model_config()
    rows = (_row(player_id="veteran", rookie=False),)
    contract = _contract(rows)
    dataset = prepare_model_dataset(rows, config)
    matrix = dataset.prediction_matrix(position="WR", prediction_season=2026)

    records = _prediction_records(
        dataset,
        contract,
        config,
        run_id="run",
        matrix=matrix,
        target_name="fantasy_points_per_game",
        family="ridge",
        point_predictions=np.asarray([10.0]),
        calibration=_calibration("fantasy_points_per_game", (-2.0, 1.5, 4.0)),
        scope="live",
        fold_label=None,
        training_max_season=2025,
    )

    assert records[0]["predicted_value"] == pytest.approx(11.5)
    assert records[0]["predicted_value"] == records[0]["p50"]
    assert (records[0]["p10"], records[0]["p50"], records[0]["p90"]) == pytest.approx(
        (8.0, 11.5, 14.0)
    )


def test_live_board_serves_selected_centers_and_keeps_rookies_point_only(
    tmp_path: Path,
) -> None:
    config = _model_config()
    rows = (
        _row(player_id="veteran", rookie=False),
        _row(player_id="rookie", rookie=True),
    )
    contract = _contract(rows)
    dataset = prepare_model_dataset(rows, config)
    matrix = dataset.prediction_matrix(position="WR", prediction_season=2026)
    learned_predictions: list[dict[str, Any]] = []
    learned_centers = {
        "games_active": (8.0, _calibration("games_active", (-2.0, 1.0, 3.0))),
        "fantasy_points_total": (
            80.0,
            _calibration("fantasy_points_total", (-20.0, 10.0, 30.0)),
        ),
    }
    for target_name, (point, calibration) in learned_centers.items():
        learned_predictions.extend(
            _prediction_records(
                dataset,
                contract,
                config,
                run_id="run",
                matrix=matrix,
                target_name=target_name,
                family="ridge",
                point_predictions=np.asarray([point]),
                calibration=calibration,
                scope="live",
                fold_label=None,
                training_max_season=2025,
            )
        )

    baseline_points = {
        "veteran": {
            "fantasy_points_per_game": 11.0,
            "games_active": 7.0,
            "fantasy_points_total": 70.0,
        },
        "rookie": {
            "fantasy_points_per_game": 5.0,
            "games_active": 10.0,
            "fantasy_points_total": 50.0,
        },
    }
    baseline_predictions = [
        {
            "player_id": player_id,
            "prediction_season": 2026,
            "position": "WR",
            "target_name": target_name,
            "baseline_name": "position_prior",
            "predicted_value": point,
            "actual_value": None,
            "experience_group": "rookie" if player_id == "rookie" else "veteran",
        }
        for player_id, target_points in baseline_points.items()
        for target_name, point in target_points.items()
    ]
    champions = {
        ("WR", "fantasy_points_per_game"): {
            "selected_source": "baseline",
            "selected_name": "position_prior",
            "reference_baseline_name": "position_prior",
        },
        ("WR", "games_active"): {
            "selected_source": "learned",
            "selected_name": "ridge",
            "reference_baseline_name": "position_prior",
        },
        ("WR", "fantasy_points_total"): {
            "selected_source": "learned",
            "selected_name": "ridge",
            "reference_baseline_name": "position_prior",
        },
    }
    reference = {
        feature: 0.0 if feature != "previous_team" else "BUF" for feature in dataset.feature_columns
    }
    final_routes: Any = {
        ("WR", target_name, "ridge"): SimpleNamespace(
            tuning=SimpleNamespace(pipeline=_ConstantPredictor(point)),
            position_reference=reference,
            explanation_features=(),
        )
        for target_name, (point, _) in learned_centers.items()
    }
    board = _build_live_board(
        dataset,
        contract,
        config,
        _app_config(tmp_path),
        run_id="run",
        learned_predictions=learned_predictions,
        baseline_predictions=baseline_predictions,
        champions=champions,
        final_routes=final_routes,
    )
    by_player = {row["player_id"]: row for row in board}
    veteran = by_player["veteran"]
    rookie = by_player["rookie"]

    # The transparent baseline's frozen Phase 3 point remains its served center;
    # it is not relabeled as an unevaluated quantile interval.
    assert (
        veteran["fantasy_points_per_game_p50"]
        == baseline_points["veteran"]["fantasy_points_per_game"]
    )
    assert veteran["fantasy_points_per_game_p10"] == pytest.approx(11.0)
    assert veteran["fantasy_points_per_game_p90"] == pytest.approx(11.0)

    learned_by_target = {row["target_name"]: row for row in learned_predictions}
    for target_name in ("games_active", "fantasy_points_total"):
        assert veteran[f"{target_name}_p50"] == learned_by_target[target_name]["predicted_value"]
        assert veteran[f"{target_name}_p50"] == learned_by_target[target_name]["p50"]

    assert rookie["prediction_status"] == "rookie_heuristic_fallback_unvalidated"
    for target_name, point in baseline_points["rookie"].items():
        assert rookie[f"{target_name}_selected_source"] == "baseline"
        assert rookie[f"{target_name}_selected_name"] == "position_prior"
        assert (
            rookie[f"{target_name}_p10"],
            rookie[f"{target_name}_p50"],
            rookie[f"{target_name}_p90"],
        ) == pytest.approx((point, point, point))


def test_interval_diagnostics_are_sliced_by_prediction_season_and_projection_tier() -> None:
    learned_predictions: list[dict[str, Any]] = []
    for season, scope in ((2024, "validation"), (2025, "test")):
        for player_number in range(6):
            predicted = float(player_number + 1)
            learned_predictions.append(
                {
                    "player_id": f"player-{player_number}",
                    "prediction_season": season,
                    "position": "WR",
                    "target_name": "fantasy_points_per_game",
                    "model_family": "ridge",
                    "prediction_scope": scope,
                    "predicted_value": predicted,
                    "p10": predicted - 1.0,
                    "p50": predicted,
                    "p90": predicted + 1.0,
                    "actual_value": predicted + 0.5,
                    "experience_group": "veteran",
                }
            )
    comparison_records = [
        {
            **row,
            "candidate_source": "learned",
            "candidate_name": "ridge",
        }
        for row in learned_predictions
    ]

    _, intervals = _detailed_metrics(
        comparison_records,
        learned_predictions,
        _contract(()),
    )

    assert len(intervals) == 8
    assert {(row["prediction_season"], row["projection_tier"]) for row in intervals} == {
        (season, tier) for season in (2024, 2025) for tier in ("all", "top", "middle", "lower")
    }
    assert all(row["rows"] == (6 if row["projection_tier"] == "all" else 2) for row in intervals)
