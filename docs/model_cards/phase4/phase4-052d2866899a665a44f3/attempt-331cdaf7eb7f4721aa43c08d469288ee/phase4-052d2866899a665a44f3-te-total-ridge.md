# Model Card: phase4-052d2866899a665a44f3-te-total-ridge

- Model ID: `phase4-052d2866899a665a44f3-te-total-ridge`
- Trained at: 2026-08-24T20:21:18+00:00
- Target: `fantasy_points_total`
- Training seasons: 2016, 2017, 2018, 2019, 2020, 2021, 2022, 2023, 2024, 2025
- Data cutoff: September 1 before each prediction season

## Purpose

Project one future NFL season for draft-preparation comparison; this candidate is selected only if it improves fixed cutoff-safe draft-relevant validation rows and clears paired-bootstrap, pooled-MAE, and ranking safeguards.

## Feature inputs

- prediction_season
- age_at_cutoff
- draft_pick
- draft_round
- height_inches
- history_seasons
- lag1_fantasy_points_per_game
- lag1_fantasy_points_total
- lag1_games_active
- lag1_stat_games
- missing_age
- missing_draft_capital
- missing_history
- missing_lag1
- missing_lag1_participation
- nfl_experience_years
- position_prior_fantasy_points_per_game
- position_prior_games_active
- team_changed_last_feature_season
- weighted_3yr_fantasy_points_per_game
- weighted_3yr_games_active
- weighted_3yr_passing_attempts_per_game
- weighted_3yr_passing_yards_per_game
- weighted_3yr_passing_tds_per_game
- weighted_3yr_interceptions_per_game
- weighted_3yr_carries_per_game
- weighted_3yr_rushing_yards_per_game
- weighted_3yr_rushing_tds_per_game
- weighted_3yr_targets_per_game
- weighted_3yr_receptions_per_game
- weighted_3yr_receiving_yards_per_game
- weighted_3yr_receiving_tds_per_game
- weighted_3yr_two_point_conversions_per_game
- weighted_3yr_fumbles_lost_per_game
- previous_team

## Missing-value behavior

Numeric medians and explicit missing indicators are fitted inside each training fold; categorical gaps use an explicit missing token. Targets are never imputed.

## Hyperparameters

````json
{
  "alpha": 10.0
}
````

## Chronological folds

````json
[
  {
    "evaluation_season": 2020,
    "label": "validation",
    "training_seasons": [
      2016,
      2017,
      2018,
      2019
    ]
  },
  {
    "evaluation_season": 2021,
    "label": "validation",
    "training_seasons": [
      2016,
      2017,
      2018,
      2019,
      2020
    ]
  },
  {
    "evaluation_season": 2022,
    "label": "validation",
    "training_seasons": [
      2016,
      2017,
      2018,
      2019,
      2020,
      2021
    ]
  },
  {
    "evaluation_season": 2023,
    "label": "validation",
    "training_seasons": [
      2016,
      2017,
      2018,
      2019,
      2020,
      2021,
      2022
    ]
  },
  {
    "evaluation_season": 2024,
    "label": "validation",
    "training_seasons": [
      2016,
      2017,
      2018,
      2019,
      2020,
      2021,
      2022,
      2023
    ]
  },
  {
    "evaluation_season": 2025,
    "label": "test",
    "training_seasons": [
      2016,
      2017,
      2018,
      2019,
      2020,
      2021,
      2022,
      2023,
      2024
    ]
  }
]
````

## Evaluation metrics

````json
{
  "candidate_name": "ridge",
  "candidate_source": "learned",
  "draft_relevant_validation_mae": 46.90514606867475,
  "draft_relevant_validation_rows": 60,
  "draft_relevant_validation_signed_bias": -13.889053644479379,
  "position": "TE",
  "target_name": "fantasy_points_total",
  "test_mae": 16.774759590646713,
  "test_rows": 237,
  "test_season": 2025,
  "validation_mae": 19.175243049282127,
  "validation_rows": 1160,
  "validation_seasons": [
    2020,
    2021,
    2022,
    2023,
    2024
  ],
  "validation_top_n_capture_rate": 0.5166666666666667
}
````

## Comparison with transparent baselines

````json
{
  "best_learned_vs_baseline_bootstrap": {
    "candidate_mae": 46.90514606867475,
    "ci95_lower": -7.509098433930528,
    "ci95_upper": 9.708858637307124,
    "direction": "uncertain",
    "mae_difference_candidate_minus_reference": 1.41468133783939,
    "n_resamples": 2000,
    "reference_mae": 45.49046473083536,
    "rows": 60,
    "seed": 42
  },
  "decision_status": "learned_draft_relevant_regression_baseline_retained",
  "learned_improvement_status": "regression",
  "reference_metrics": {
    "candidate_name": "position_shrinkage",
    "candidate_source": "baseline",
    "draft_relevant_validation_mae": 45.49046473083536,
    "draft_relevant_validation_rows": 60,
    "draft_relevant_validation_signed_bias": 6.520829240626062,
    "position": "TE",
    "target_name": "fantasy_points_total",
    "test_mae": 27.65932959579542,
    "test_rows": 237,
    "test_season": 2025,
    "validation_mae": 29.423851137143856,
    "validation_rows": 1160,
    "validation_seasons": [
      2020,
      2021,
      2022,
      2023,
      2024
    ],
    "validation_top_n_capture_rate": 0.4833333333333333
  },
  "selected_champion": "position_shrinkage",
  "selected_source": "baseline",
  "selection_rule": "A learned candidate must lower fixed-cohort draft-relevant validation MAE, its paired-bootstrap 95% interval must remain below zero, pooled MAE must stay within tolerance, and total-points top-N capture must be preserved; otherwise the transparent baseline is retained.",
  "this_candidate_selected": false
}
````

## Uncertainty estimates

````json
{
  "empirical_metrics_by_season": [
    {
      "candidate_name": "ridge",
      "empirical_coverage_p10_p90": 0.810126582278481,
      "evaluation_scope": "test",
      "mean_interval_width_p10_p90": 52.195651093317444,
      "pinball_loss_p10": 4.638797126402854,
      "pinball_loss_p50": 8.387379795323357,
      "pinball_loss_p90": 6.013788680983884,
      "position": "TE",
      "prediction_season": 2025,
      "projection_tier": "all",
      "rows": 237,
      "target_name": "fantasy_points_total"
    },
    {
      "candidate_name": "ridge",
      "empirical_coverage_p10_p90": 0.423728813559322,
      "evaluation_scope": "test",
      "mean_interval_width_p10_p90": 52.19565109331742,
      "pinball_loss_p10": 10.465797666815238,
      "pinball_loss_p50": 20.129968737696988,
      "pinball_loss_p90": 14.01992033615557,
      "position": "TE",
      "prediction_season": 2025,
      "projection_tier": "top",
      "rows": 59,
      "target_name": "fantasy_points_total"
    },
    {
      "candidate_name": "ridge",
      "empirical_coverage_p10_p90": 0.907563025210084,
      "evaluation_scope": "test",
      "mean_interval_width_p10_p90": 52.195651093317466,
      "pinball_loss_p10": 2.4218370167287078,
      "pinball_loss_p50": 4.980557233217375,
      "pinball_loss_p90": 4.065987628017566,
      "position": "TE",
      "prediction_season": 2025,
      "projection_tier": "middle",
      "rows": 119,
      "target_name": "fantasy_points_total"
    },
    {
      "candidate_name": "ridge",
      "empirical_coverage_p10_p90": 1.0,
      "evaluation_scope": "test",
      "mean_interval_width_p10_p90": 52.19565109331743,
      "pinball_loss_p10": 3.283292400417987,
      "pinball_loss_p50": 3.516178732451617,
      "pinball_loss_p90": 1.9362727089137555,
      "position": "TE",
      "prediction_season": 2025,
      "projection_tier": "lower",
      "rows": 59,
      "target_name": "fantasy_points_total"
    },
    {
      "candidate_name": "ridge",
      "empirical_coverage_p10_p90": 0.8177777777777778,
      "evaluation_scope": "validation",
      "mean_interval_width_p10_p90": 68.8353347710781,
      "pinball_loss_p10": 5.625093999394456,
      "pinball_loss_p50": 11.483355794118333,
      "pinball_loss_p90": 8.237623730345055,
      "position": "TE",
      "prediction_season": 2020,
      "projection_tier": "all",
      "rows": 225,
      "target_name": "fantasy_points_total"
    },
    {
      "candidate_name": "ridge",
      "empirical_coverage_p10_p90": 0.6071428571428571,
      "evaluation_scope": "validation",
      "mean_interval_width_p10_p90": 68.83533477107808,
      "pinball_loss_p10": 7.163166262083363,
      "pinball_loss_p50": 18.90168433072055,
      "pinball_loss_p90": 14.878187247011498,
      "position": "TE",
      "prediction_season": 2020,
      "projection_tier": "top",
      "rows": 56,
      "target_name": "fantasy_points_total"
    },
    {
      "candidate_name": "ridge",
      "empirical_coverage_p10_p90": 0.8584070796460177,
      "evaluation_scope": "validation",
      "mean_interval_width_p10_p90": 68.8353347710781,
      "pinball_loss_p10": 4.979285732872511,
      "pinball_loss_p50": 9.157978391261642,
      "pinball_loss_p90": 8.184460040515505,
      "position": "TE",
      "prediction_season": 2020,
      "projection_tier": "middle",
      "rows": 113,
      "target_name": "fantasy_points_total"
    },
    {
      "candidate_name": "ridge",
      "empirical_coverage_p10_p90": 0.9464285714285714,
      "evaluation_scope": "validation",
      "mean_interval_width_p10_p90": 68.83533477107807,
      "pinball_loss_p10": 5.390170560223041,
      "pinball_loss_p50": 8.757306659709073,
      "pinball_loss_p90": 1.704336944941808,
      "position": "TE",
      "prediction_season": 2020,
      "projection_tier": "lower",
      "rows": 56,
      "target_name": "fantasy_points_total"
    },
    {
      "candidate_name": "ridge",
      "empirical_coverage_p10_p90": 0.8296943231441049,
      "evaluation_scope": "validation",
      "mean_interval_width_p10_p90": 69.90822204512526,
      "pinball_loss_p10": 4.811506398615646,
      "pinball_loss_p50": 9.570981893037926,
      "pinball_loss_p90": 6.776150634459249,
      "position": "TE",
      "prediction_season": 2021,
      "projection_tier": "all",
      "rows": 229,
      "target_name": "fantasy_points_total"
    },
    {
      "candidate_name": "ridge",
      "empirical_coverage_p10_p90": 0.45614035087719296,
      "evaluation_scope": "validation",
      "mean_interval_width_p10_p90": 69.90822204512521,
      "pinball_loss_p10": 7.443631035954762,
      "pinball_loss_p50": 21.4184369220018,
      "pinball_loss_p90": 14.568526201964609,
      "position": "TE",
      "prediction_season": 2021,
      "projection_tier": "top",
      "rows": 57,
      "target_name": "fantasy_points_total"
    },
    {
      "candidate_name": "ridge",
      "empirical_coverage_p10_p90": 0.9304347826086956,
      "evaluation_scope": "validation",
      "mean_interval_width_p10_p90": 69.90822204512526,
      "pinball_loss_p10": 3.6686985308471023,
      "pinball_loss_p50": 5.831143501369692,
      "pinball_loss_p90": 5.030463489635794,
      "position": "TE",
      "prediction_season": 2021,
      "projection_tier": "middle",
      "rows": 115,
      "target_name": "fantasy_points_total"
    },
    {
      "candidate_name": "ridge",
      "empirical_coverage_p10_p90": 1.0,
      "evaluation_scope": "validation",
      "mean_interval_width_p10_p90": 69.90822204512523,
      "pinball_loss_p10": 4.485046757651658,
      "pinball_loss_p50": 5.268814847264353,
      "pinball_loss_p90": 2.5057754468608637,
      "position": "TE",
      "prediction_season": 2021,
      "projection_tier": "lower",
      "rows": 57,
      "target_name": "fantasy_points_total"
    },
    {
      "candidate_name": "ridge",
      "empirical_coverage_p10_p90": 0.8461538461538461,
      "evaluation_scope": "validation",
      "mean_interval_width_p10_p90": 65.39241689134258,
      "pinball_loss_p10": 6.045907386379322,
      "pinball_loss_p50": 9.176797636716522,
      "pinball_loss_p90": 5.773950032491337,
      "position": "TE",
      "prediction_season": 2022,
      "projection_tier": "all",
      "rows": 234,
      "target_name": "fantasy_points_total"
    },
    {
      "candidate_name": "ridge",
      "empirical_coverage_p10_p90": 0.5254237288135594,
      "evaluation_scope": "validation",
      "mean_interval_width_p10_p90": 65.39241689134258,
      "pinball_loss_p10": 16.12960790943226,
      "pinball_loss_p50": 21.52816978513824,
      "pinball_loss_p90": 9.889218676358896,
      "position": "TE",
      "prediction_season": 2022,
      "projection_tier": "top",
      "rows": 59,
      "target_name": "fantasy_points_total"
    },
    {
      "candidate_name": "ridge",
      "empirical_coverage_p10_p90": 0.9310344827586207,
      "evaluation_scope": "validation",
      "mean_interval_width_p10_p90": 65.39241689134258,
      "pinball_loss_p10": 2.3194889341218063,
      "pinball_loss_p50": 6.1544426532731515,
      "pinball_loss_p90": 4.9643094089397,
      "position": "TE",
      "prediction_season": 2022,
      "projection_tier": "middle",
      "rows": 116,
      "target_name": "fantasy_points_total"
    },
    {
      "candidate_name": "ridge",
      "empirical_coverage_p10_p90": 1.0,
      "evaluation_scope": "validation",
      "mean_interval_width_p10_p90": 65.39241689134258,
      "pinball_loss_p10": 3.2887244982733663,
      "pinball_loss_p50": 2.7676827438783804,
      "pinball_loss_p90": 3.2505171908608923,
      "position": "TE",
      "prediction_season": 2022,
      "projection_tier": "lower",
      "rows": 59,
      "target_name": "fantasy_points_total"
    },
    {
      "candidate_name": "ridge",
      "empirical_coverage_p10_p90": 0.8085106382978723,
      "evaluation_scope": "validation",
      "mean_interval_width_p10_p90": 57.1613693129061,
      "pinball_loss_p10": 4.386625249293794,
      "pinball_loss_p50": 8.743410211785498,
      "pinball_loss_p90": 5.977523384952018,
      "position": "TE",
      "prediction_season": 2023,
      "projection_tier": "all",
      "rows": 235,
      "target_name": "fantasy_points_total"
    },
    {
      "candidate_name": "ridge",
      "empirical_coverage_p10_p90": 0.3898305084745763,
      "evaluation_scope": "validation",
      "mean_interval_width_p10_p90": 57.1613693129061,
      "pinball_loss_p10": 8.98412868502531,
      "pinball_loss_p50": 19.3248316742805,
      "pinball_loss_p90": 13.509043771128113,
      "position": "TE",
      "prediction_season": 2023,
      "projection_tier": "top",
      "rows": 59,
      "target_name": "fantasy_points_total"
    },
    {
      "candidate_name": "ridge",
      "empirical_coverage_p10_p90": 0.9230769230769231,
      "evaluation_scope": "validation",
      "mean_interval_width_p10_p90": 57.16136931290609,
      "pinball_loss_p10": 2.5223729347570107,
      "pinball_loss_p50": 5.429679650430629,
      "pinball_loss_p90": 4.069299502752118,
      "position": "TE",
      "prediction_season": 2023,
      "projection_tier": "middle",
      "rows": 117,
      "target_name": "fantasy_points_total"
    },
    {
      "candidate_name": "ridge",
      "empirical_coverage_p10_p90": 1.0,
      "evaluation_scope": "validation",
      "mean_interval_width_p10_p90": 57.16136931290611,
      "pinball_loss_p10": 3.4860289457792915,
      "pinball_loss_p50": 4.7332849472315095,
      "pinball_loss_p90": 2.2301079855113186,
      "position": "TE",
      "prediction_season": 2023,
      "projection_tier": "lower",
      "rows": 59,
      "target_name": "fantasy_points_total"
    },
    {
      "candidate_name": "ridge",
      "empirical_coverage_p10_p90": 0.8059071729957806,
      "evaluation_scope": "validation",
      "mean_interval_width_p10_p90": 54.22874660595639,
      "pinball_loss_p10": 5.029875216136523,
      "pinball_loss_p50": 9.046662509029808,
      "pinball_loss_p90": 6.637783915191373,
      "position": "TE",
      "prediction_season": 2024,
      "projection_tier": "all",
      "rows": 237,
      "target_name": "fantasy_points_total"
    },
    {
      "candidate_name": "ridge",
      "empirical_coverage_p10_p90": 0.423728813559322,
      "evaluation_scope": "validation",
      "mean_interval_width_p10_p90": 54.22874660595639,
      "pinball_loss_p10": 11.883544045286971,
      "pinball_loss_p50": 22.016625923819394,
      "pinball_loss_p90": 16.34921848189143,
      "position": "TE",
      "prediction_season": 2024,
      "projection_tier": "top",
      "rows": 59,
      "target_name": "fantasy_points_total"
    },
    {
      "candidate_name": "ridge",
      "empirical_coverage_p10_p90": 0.907563025210084,
      "evaluation_scope": "validation",
      "mean_interval_width_p10_p90": 54.22874660595637,
      "pinball_loss_p10": 2.4112640519989412,
      "pinball_loss_p50": 5.070748710953453,
      "pinball_loss_p90": 3.9515294422466467,
      "position": "TE",
      "prediction_season": 2024,
      "projection_tier": "middle",
      "rows": 119,
      "target_name": "fantasy_points_total"
    },
    {
      "candidate_name": "ridge",
      "empirical_coverage_p10_p90": 0.9830508474576272,
      "evaluation_scope": "validation",
      "mean_interval_width_p10_p90": 54.22874660595638,
      "pinball_loss_p10": 3.457811955331368,
      "pinball_loss_p50": 4.095915059851861,
      "pinball_loss_p90": 2.3443880312103427,
      "position": "TE",
      "prediction_season": 2024,
      "projection_tier": "lower",
      "rows": 59,
      "target_name": "fantasy_points_total"
    }
  ],
  "empirical_not_guaranteed": true,
  "method": "training-only signed out-of-fold residual quantiles",
  "operational_center": "training_only_residual_adjusted_p50",
  "residual_rows": 709,
  "residual_seasons": [
    2023,
    2024,
    2025
  ]
}
````

## Global explanations

````json
{
  "diagnostic_plots": {
    "feature_response": "docs/images/phase4/phase4-052d2866899a665a44f3/attempt-331cdaf7eb7f4721aa43c08d469288ee/feature_response.svg",
    "hgb_permutation_importance": "docs/images/phase4/phase4-052d2866899a665a44f3/attempt-331cdaf7eb7f4721aa43c08d469288ee/hgb_permutation_importance.svg",
    "interval_coverage_width": "docs/images/phase4/phase4-052d2866899a665a44f3/attempt-331cdaf7eb7f4721aa43c08d469288ee/interval_coverage_width.svg",
    "ridge_coefficients": "docs/images/phase4/phase4-052d2866899a665a44f3/attempt-331cdaf7eb7f4721aa43c08d469288ee/ridge_coefficients.svg",
    "season_mae_comparison": "docs/images/phase4/phase4-052d2866899a665a44f3/attempt-331cdaf7eb7f4721aa43c08d469288ee/season_mae_comparison.svg",
    "segment_mae": "docs/images/phase4/phase4-052d2866899a665a44f3/attempt-331cdaf7eb7f4721aa43c08d469288ee/segment_mae.svg",
    "test_predicted_vs_actual": "docs/images/phase4/phase4-052d2866899a665a44f3/attempt-331cdaf7eb7f4721aa43c08d469288ee/test_predicted_vs_actual.svg",
    "test_residuals": "docs/images/phase4/phase4-052d2866899a665a44f3/attempt-331cdaf7eb7f4721aa43c08d469288ee/test_residuals.svg"
  },
  "feature_responses": [],
  "importance": [
    {
      "absolute_importance": 21.27032072960784,
      "coefficient": 21.27032072960784,
      "direction": "positive",
      "feature": "numeric__lag1_fantasy_points_total",
      "rank": 1
    },
    {
      "absolute_importance": 14.870768455399459,
      "coefficient": 14.870768455399459,
      "direction": "positive",
      "feature": "categorical__previous_team_KC",
      "rank": 2
    },
    {
      "absolute_importance": 11.89504023107531,
      "coefficient": 11.89504023107531,
      "direction": "positive",
      "feature": "numeric__weighted_3yr_receiving_yards_per_game",
      "rank": 3
    },
    {
      "absolute_importance": 9.507038604087182,
      "coefficient": -9.507038604087182,
      "direction": "negative",
      "feature": "categorical__previous_team_WAS",
      "rank": 4
    },
    {
      "absolute_importance": 8.541935757938102,
      "coefficient": -8.541935757938102,
      "direction": "negative",
      "feature": "numeric__weighted_3yr_passing_tds_per_game",
      "rank": 5
    },
    {
      "absolute_importance": 8.478591720814778,
      "coefficient": 8.478591720814778,
      "direction": "positive",
      "feature": "categorical__previous_team_OAK",
      "rank": 6
    },
    {
      "absolute_importance": 7.994365866224185,
      "coefficient": -7.994365866224185,
      "direction": "negative",
      "feature": "categorical__previous_team_NYJ",
      "rank": 7
    },
    {
      "absolute_importance": 6.655737081888937,
      "coefficient": 6.655737081888937,
      "direction": "positive",
      "feature": "categorical__previous_team_LA",
      "rank": 8
    },
    {
      "absolute_importance": 6.435772263216324,
      "coefficient": -6.435772263216324,
      "direction": "negative",
      "feature": "categorical__previous_team_LAC",
      "rank": 9
    },
    {
      "absolute_importance": 6.366148736465708,
      "coefficient": -6.366148736465708,
      "direction": "negative",
      "feature": "categorical__previous_team_NYG",
      "rank": 10
    },
    {
      "absolute_importance": 6.3484029931218835,
      "coefficient": 6.3484029931218835,
      "direction": "positive",
      "feature": "numeric__weighted_3yr_rushing_yards_per_game",
      "rank": 11
    },
    {
      "absolute_importance": 5.873413114650949,
      "coefficient": 5.873413114650949,
      "direction": "positive",
      "feature": "categorical__previous_team_DET",
      "rank": 12
    },
    {
      "absolute_importance": 5.858178134564879,
      "coefficient": -5.858178134564879,
      "direction": "negative",
      "feature": "categorical__previous_team_CIN",
      "rank": 13
    },
    {
      "absolute_importance": 5.809585302823341,
      "coefficient": -5.809585302823341,
      "direction": "negative",
      "feature": "categorical__previous_team_NE",
      "rank": 14
    },
    {
      "absolute_importance": 5.7138501608776195,
      "coefficient": 5.7138501608776195,
      "direction": "positive",
      "feature": "numeric__weighted_3yr_passing_yards_per_game",
      "rank": 15
    },
    {
      "absolute_importance": 5.654245526040622,
      "coefficient": -5.654245526040622,
      "direction": "negative",
      "feature": "categorical__previous_team_MIA",
      "rank": 16
    },
    {
      "absolute_importance": 5.601181640290404,
      "coefficient": 5.601181640290404,
      "direction": "positive",
      "feature": "categorical__previous_team_SF",
      "rank": 17
    },
    {
      "absolute_importance": 5.544681742644539,
      "coefficient": 5.544681742644539,
      "direction": "positive",
      "feature": "categorical__previous_team_PHI",
      "rank": 18
    },
    {
      "absolute_importance": 5.340716833747184,
      "coefficient": 5.340716833747184,
      "direction": "positive",
      "feature": "categorical__previous_team_ARI",
      "rank": 19
    },
    {
      "absolute_importance": 4.8158961351642695,
      "coefficient": -4.8158961351642695,
      "direction": "negative",
      "feature": "numeric__weighted_3yr_targets_per_game",
      "rank": 20
    }
  ],
  "method": "standardized coefficients"
}
````

## Data lineage

````json
{
  "baseline_report_fingerprint": "a8e805dc230a21154ff6375e232850f8736e70b103bc59ea573ecc4eba881aa3",
  "build_fingerprint": "d4a02828f7ea38f180320b0c98458127a758bc167a377ea67faf86352e60870e",
  "feature_data_fingerprint": "965c7775f8fc4a64b0040bb666ebecdbb962462d35dddecccf87121ce227a4f1",
  "model_config_fingerprint": "cb3aebc7bcc75ebd6723886c5775fed9e4033c0648abde7463fb98bb608c2c02",
  "model_feature_fingerprint": "9faa0a8ed38f8268fca5ea3a964ffb5645c8cdadbf9162d31021be93404cee68",
  "scoring_ruleset_fingerprint": "9f660dd5c8db91e63a1c43a5db74a3848b0554b2acf94d0fd891fe58b4eb7871",
  "target_data_fingerprint": "1dede9747fde400fe80ffd0302ab71ecf1231de7832f6006cf3482f6d733cfea"
}
````

## Limitations

- No historical preseason-position archive exists for a validated rookie cohort.
- Intervals are empirical residual ranges, not guaranteed probability statements.
- Negative fantasy-point outcomes are legitimate and are not silently clamped.
- Player explanations describe associations and sensitivity, not causes.

## Intended uses

- Compare transparent, linear, and nonlinear season projections.
- Supply an auditable 2026 projection input to later draft-value work.

## Out-of-scope uses

- Weekly lineup decisions, wagering, injury diagnosis, or causal claims.
- Learned rookie projection claims until historical rookie evidence is added.
- ADP availability or draft recommendations, which begin in later phases.

## Serialized artifact

- Project-relative path: `models/artifacts/phase4-052d2866899a665a44f3/attempt-331cdaf7eb7f4721aa43c08d469288ee/TE/fantasy_points_total/ridge.joblib`
- SHA-256: `b8e4e087cb8dd402c41b26950a646ddaaeb0dcf7e33762b9a2f884bb6db1ea15`

## Additional metadata

````json
{
  "publication_id": "attempt-331cdaf7eb7f4721aa43c08d469288ee"
}
````
