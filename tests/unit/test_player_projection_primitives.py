from __future__ import annotations

from dataclasses import replace

import pytest

from fantasy_draft_ai.models.player_projection.config import (
    DEFAULT_NUMERIC_FEATURES,
    FEATURE_CONTRACT_VERSION,
    HIST_GRADIENT_BOOSTING,
    PLAYER_MODEL_VERSION,
    RIDGE,
    DraftRelevancePolicy,
    HistGradientBoostingGridPoint,
    PlayerModelConfig,
    build_run_fingerprint,
)
from fantasy_draft_ai.models.player_projection.dataset import (
    PlayerSeasonModelRow,
    prepare_model_dataset,
)
from fantasy_draft_ai.models.player_projection.pipelines import build_pipeline
from fantasy_draft_ai.models.player_projection.tuning import (
    InnerFold,
    chronological_inner_folds,
    tune_model,
)
from fantasy_draft_ai.models.player_projection.uncertainty import (
    ResidualObservation,
    evaluate_intervals,
    fit_residual_calibration,
)


def _compact_config() -> PlayerModelConfig:
    return PlayerModelConfig(
        ridge_alphas=(1.0,),
        hgb_grid=(
            HistGradientBoostingGridPoint(
                learning_rate=0.1,
                max_iter=10,
                max_leaf_nodes=7,
                min_samples_leaf=2,
                l2_regularization=1.0,
            ),
        ),
        max_inner_validation_seasons=None,
    )


def _features(
    config: PlayerModelConfig,
    value: float,
    *,
    rookie: bool = False,
    team: str | None = "BUF",
) -> dict[str, object]:
    payload: dict[str, object] = {
        feature: value + (index / 1000)
        for index, feature in enumerate(config.numeric_features)
        if feature != "prediction_season"
    }
    payload.update(
        {
            "history_seasons": 0 if rookie else 3,
            "is_rookie": rookie,
            "previous_team": team,
            # These tempting fields must never enter the extracted matrix.
            "baseline_previous_fantasy_points_per_game": 99999,
            "candidate_selection_reason": "future_metadata",
            "candidate_evidence_seasons": [2099],
        }
    )
    return payload


def _row(
    config: PlayerModelConfig,
    *,
    player_id: str,
    season: int,
    position: str = "WR",
    value: float = 1.0,
    rookie: bool = False,
    team: str | None = "BUF",
    ppg: float | None = 10.0,
    games: float | None = 5.0,
    total: float | None = 50.0,
) -> PlayerSeasonModelRow:
    return PlayerSeasonModelRow(
        player_id=player_id,
        prediction_season=season,
        position=position,
        features=_features(config, value, rookie=rookie, team=team),
        targets={
            "fantasy_points_per_game": ppg,
            "games_active": games,
            "fantasy_points_total": total,
        },
    )


def test_config_and_run_fingerprints_are_deterministic_and_reject_unsafe_features() -> None:
    config = _compact_config()
    kwargs = {
        "feature_data_fingerprint": "feature",
        "target_data_fingerprint": "target",
        "build_fingerprint": "build",
        "scoring_ruleset_fingerprint": "rules",
        "baseline_report_fingerprint": "baselines",
    }

    assert config.fingerprint() == _compact_config().fingerprint()
    assert config.feature_contract_fingerprint() == _compact_config().feature_contract_fingerprint()
    assert PLAYER_MODEL_VERSION == "phase4-player-models-v3"
    assert FEATURE_CONTRACT_VERSION == "phase4-player-features-v2"
    assert "age_at_cutoff" in config.numeric_features
    assert "age_adjustment_factor" not in config.numeric_features
    assert build_run_fingerprint(config, **kwargs) == build_run_fingerprint(config, **kwargs)
    assert build_run_fingerprint(config, **kwargs) != build_run_fingerprint(
        config, **(kwargs | {"baseline_report_fingerprint": "new-baselines"})
    )
    with pytest.raises(ValueError, match="cannot be empty"):
        build_run_fingerprint(config, **(kwargs | {"baseline_report_fingerprint": ""}))
    with pytest.raises(ValueError, match="forbidden"):
        PlayerModelConfig(
            numeric_features=(*DEFAULT_NUMERIC_FEATURES, "baseline_weighted_games_active")
        )
    with pytest.raises(ValueError, match="forbidden"):
        PlayerModelConfig(
            numeric_features=(*DEFAULT_NUMERIC_FEATURES, "candidate_selection_reason")
        )
    with pytest.raises(ValueError, match="both raw age and the derived age adjustment"):
        PlayerModelConfig(
            numeric_features=(*DEFAULT_NUMERIC_FEATURES, "age_adjustment_factor")
        )
    with pytest.raises(ValueError, match=r"exactly .*P10/P50/P90"):
        PlayerModelConfig(interval_quantiles=(0.05, 0.50, 0.95))


def test_draft_relevance_policy_changes_the_model_run_fingerprint() -> None:
    config = _compact_config()
    changed = PlayerModelConfig(
        ridge_alphas=config.ridge_alphas,
        hgb_grid=config.hgb_grid,
        max_inner_validation_seasons=config.max_inner_validation_seasons,
        draft_relevance_policy=DraftRelevancePolicy(
            pooled_mae_regression_tolerance=0.10
        ),
    )
    kwargs = {
        "feature_data_fingerprint": "feature",
        "target_data_fingerprint": "target",
        "build_fingerprint": "build",
        "scoring_ruleset_fingerprint": "rules",
        "baseline_report_fingerprint": "baselines",
    }

    assert config.feature_contract_fingerprint() == changed.feature_contract_fingerprint()
    assert config.fingerprint() != changed.fingerprint()
    assert build_run_fingerprint(config, **kwargs) != build_run_fingerprint(changed, **kwargs)


def test_dataset_uses_allowlist_routes_position_masks_targets_and_never_trains_rookies() -> None:
    config = _compact_config()
    rows = [
        _row(config, player_id="active", season=2020, ppg=12, games=5, total=60),
        _row(config, player_id="zero", season=2020, ppg=None, games=0, total=0),
        _row(
            config,
            player_id="rookie",
            season=2020,
            rookie=True,
            ppg=20,
            games=10,
            total=200,
        ),
        _row(
            config,
            player_id="running-back",
            season=2020,
            position="RB",
            ppg=8,
            games=4,
            total=32,
        ),
    ]
    dataset = prepare_model_dataset(rows, config)

    assert "baseline_previous_fantasy_points_per_game" not in dataset.feature_columns
    assert "candidate_selection_reason" not in dataset.feature_columns
    assert dataset.feature_columns == (*config.numeric_features, *config.categorical_features)
    ppg = dataset.training_matrix(
        position="WR",
        target_name="fantasy_points_per_game",
        training_seasons=[2020],
    )
    games = dataset.training_matrix(
        position="WR", target_name="games_active", training_seasons=[2020]
    )
    total = dataset.training_matrix(
        position="WR", target_name="fantasy_points_total", training_seasons=[2020]
    )

    assert ppg.keys["player_id"].tolist() == ["active"]
    assert games.keys["player_id"].tolist() == ["active", "zero"]
    assert games.y is not None and games.y.tolist() == [5.0, 0.0]
    assert total.keys["player_id"].tolist() == ["active", "zero"]
    assert not bool(total.keys["is_rookie"].any())
    assert dataset.rookie_keys(position="WR", prediction_season=2020)["player_id"].tolist() == [
        "rookie"
    ]
    assert dataset.prediction_matrix(position="WR", prediction_season=2020).keys[
        "player_id"
    ].tolist() == ["active", "zero"]


def test_selected_feature_fingerprint_ignores_input_order_and_target_changes() -> None:
    config = _compact_config()
    first = _row(config, player_id="a", season=2020, value=1, total=10)
    second = _row(config, player_id="b", season=2021, value=2, total=20)
    changed_target = replace(first, targets={**(first.targets or {}), "fantasy_points_total": 999})

    original = prepare_model_dataset([first, second], config)
    reordered = prepare_model_dataset([second, first], config)
    outcome_changed = prepare_model_dataset([changed_target, second], config)

    assert original.feature_fingerprint == reordered.feature_fingerprint
    assert original.feature_fingerprint == outcome_changed.feature_fingerprint


def test_chronological_tuning_is_deterministic_and_future_rows_do_not_change_prior_oof() -> None:
    config = _compact_config()
    base_rows: list[PlayerSeasonModelRow] = []
    for season in range(2018, 2022):
        for index in range(2):
            value = float((season - 2017) * 10 + index)
            base_rows.append(
                _row(
                    config,
                    player_id=f"p-{season}-{index}",
                    season=season,
                    value=value,
                    team="BUF" if index == 0 else "MIA",
                    total=(value * 2) + 3,
                )
            )
    base = prepare_model_dataset(base_rows, config).training_matrix(
        position="WR",
        target_name="fantasy_points_total",
        training_seasons=range(2018, 2022),
    )
    first = tune_model(base, family=RIDGE, config=config)
    second = tune_model(base, family=RIDGE, config=config)

    assert first.best_parameters == second.best_parameters == {"alpha": 1.0}
    assert first.best_mean_absolute_error == pytest.approx(second.best_mean_absolute_error)
    assert [row.predicted_value for row in first.out_of_fold_predictions] == pytest.approx(
        [row.predicted_value for row in second.out_of_fold_predictions]
    )
    assert chronological_inner_folds(range(2018, 2022), max_validation_seasons=None) == (
        InnerFold(training_seasons=(2018, 2019), validation_season=2020),
        InnerFold(training_seasons=(2018, 2019, 2020), validation_season=2021),
    )

    future_rows = [
        _row(
            config,
            player_id=f"future-{index}",
            season=2022,
            value=100000 + index,
            team="ZZZ",
            total=-100000,
        )
        for index in range(2)
    ]
    extended = prepare_model_dataset([*base_rows, *future_rows], config).training_matrix(
        position="WR",
        target_name="fantasy_points_total",
        training_seasons=range(2018, 2023),
    )
    with_future = tune_model(extended, family=RIDGE, config=config)
    prior = {
        (row.player_id, row.prediction_season): row.predicted_value
        for row in first.out_of_fold_predictions
    }
    extended_prior = {
        (row.player_id, row.prediction_season): row.predicted_value
        for row in with_future.out_of_fold_predictions
        if row.prediction_season <= 2021
    }
    assert prior == pytest.approx(extended_prior)


def test_hist_gradient_boosting_disables_internal_random_early_stopping() -> None:
    config = _compact_config()
    pipeline = build_pipeline(HIST_GRADIENT_BOOSTING, config)
    estimator = pipeline.named_steps["estimator"]

    assert estimator.early_stopping is False
    assert estimator.random_state == 42


def test_signed_residual_intervals_are_training_only_deterministic_ordered_and_bounded() -> None:
    config = _compact_config()
    observations = [
        ResidualObservation(2020, actual_value=0, predicted_value=2),
        ResidualObservation(2021, actual_value=5, predicted_value=5),
        ResidualObservation(2022, actual_value=10, predicted_value=8),
    ]
    calibration = fit_residual_calibration(
        observations,
        target_name="games_active",
        prediction_season=2026,
        config=config,
    )
    repeated = fit_residual_calibration(
        reversed(observations),
        target_name="games_active",
        prediction_season=2026,
        config=config,
    )

    assert calibration.fingerprint == repeated.fingerprint
    assert calibration.residual_seasons == (2020, 2021, 2022)
    interval = calibration.interval(17)
    assert 0 <= interval.p10 <= interval.p50 <= interval.p90 <= 18
    assert calibration.interval(-100).point_prediction == 0
    assert calibration.interval(100).point_prediction == 18
    metrics = evaluate_intervals([interval], [17])
    assert metrics.rows == 1
    assert metrics.central_80_coverage == 1
    assert metrics.average_width == pytest.approx(interval.p90 - interval.p10)

    with pytest.raises(ValueError, match="future season"):
        fit_residual_calibration(
            [*observations, ResidualObservation(2026, 4, 4)],
            target_name="games_active",
            prediction_season=2026,
            config=config,
        )
