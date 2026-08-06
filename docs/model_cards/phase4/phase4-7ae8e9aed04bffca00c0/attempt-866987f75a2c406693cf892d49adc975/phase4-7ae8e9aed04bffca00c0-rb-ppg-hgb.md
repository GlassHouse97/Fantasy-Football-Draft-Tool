# Model Card: phase4-7ae8e9aed04bffca00c0-rb-ppg-hgb

- Model ID: `phase4-7ae8e9aed04bffca00c0-rb-ppg-hgb`
- Trained at: 2026-08-05T20:58:13+00:00
- Target: `fantasy_points_per_game`
- Training seasons: 2016, 2017, 2018, 2019, 2020, 2021, 2022, 2023, 2024, 2025
- Data cutoff: September 1 before each prediction season

## Purpose

Project one future NFL season for draft-preparation comparison; this candidate is selected only if it lowers pooled future-season validation MAE and the paired-bootstrap comparison supports that improvement.

## Feature inputs

- prediction_season
- age_at_cutoff
- age_adjustment_factor
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
  "l2_regularization": 1.0,
  "learning_rate": 0.05,
  "max_iter": 120,
  "max_leaf_nodes": 15,
  "min_samples_leaf": 20
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
  "candidate_name": "hist_gradient_boosting",
  "candidate_source": "learned",
  "position": "RB",
  "target_name": "fantasy_points_per_game",
  "test_mae": 2.368541613719735,
  "test_rows": 128,
  "test_season": 2025,
  "validation_mae": 2.664872762103432,
  "validation_rows": 686,
  "validation_seasons": [
    2020,
    2021,
    2022,
    2023,
    2024
  ]
}
````

## Comparison with transparent baselines

````json
{
  "best_learned_vs_baseline_bootstrap": {
    "candidate_mae": 2.664872762103432,
    "ci95_lower": -0.11208713957810204,
    "ci95_upper": 0.1635642681013548,
    "direction": "uncertain",
    "mae_difference_candidate_minus_reference": 0.027918866645626927,
    "n_resamples": 2000,
    "reference_mae": 2.636953895457805,
    "rows": 686,
    "seed": 42
  },
  "decision_status": "learned_regression_baseline_retained",
  "learned_improvement_status": "regression",
  "reference_metrics": {
    "candidate_name": "age_position_adjusted",
    "candidate_source": "baseline",
    "position": "RB",
    "target_name": "fantasy_points_per_game",
    "test_mae": 2.2700883877685754,
    "test_rows": 128,
    "test_season": 2025,
    "validation_mae": 2.636953895457805,
    "validation_rows": 686,
    "validation_seasons": [
      2020,
      2021,
      2022,
      2023,
      2024
    ]
  },
  "selected_champion": "age_position_adjusted",
  "selected_source": "baseline",
  "selection_rule": "A learned candidate must lower pooled validation MAE and its paired bootstrap 95% interval for the MAE difference must remain below zero; otherwise the transparent baseline is retained.",
  "this_candidate_selected": false
}
````

## Uncertainty estimates

````json
{
  "empirical_metrics_by_season": [
    {
      "candidate_name": "hist_gradient_boosting",
      "empirical_coverage_p10_p90": 0.8671875,
      "evaluation_scope": "test",
      "mean_interval_width_p10_p90": 9.177701297285866,
      "pinball_loss_p10": 0.5527280443453941,
      "pinball_loss_p50": 1.1842708068598675,
      "pinball_loss_p90": 0.675669044583981,
      "position": "RB",
      "prediction_season": 2025,
      "projection_tier": "all",
      "rows": 128,
      "target_name": "fantasy_points_per_game"
    },
    {
      "candidate_name": "hist_gradient_boosting",
      "empirical_coverage_p10_p90": 0.7666666666666667,
      "evaluation_scope": "test",
      "mean_interval_width_p10_p90": 9.17770129728587,
      "pinball_loss_p10": 0.6981889974023997,
      "pinball_loss_p50": 1.4927444476384244,
      "pinball_loss_p90": 0.748792294034086,
      "position": "RB",
      "prediction_season": 2025,
      "projection_tier": "top",
      "rows": 60,
      "target_name": "fantasy_points_per_game"
    },
    {
      "candidate_name": "hist_gradient_boosting",
      "empirical_coverage_p10_p90": 0.9565217391304348,
      "evaluation_scope": "test",
      "mean_interval_width_p10_p90": 9.177701297285866,
      "pinball_loss_p10": 0.3958034591566106,
      "pinball_loss_p50": 1.04883603230698,
      "pinball_loss_p90": 0.6602755875969174,
      "position": "RB",
      "prediction_season": 2025,
      "projection_tier": "middle",
      "rows": 46,
      "target_name": "fantasy_points_per_game"
    },
    {
      "candidate_name": "hist_gradient_boosting",
      "empirical_coverage_p10_p90": 0.9545454545454546,
      "evaluation_scope": "test",
      "mean_interval_width_p10_p90": 9.177701297285866,
      "pinball_loss_p10": 0.4841313959482896,
      "pinball_loss_p50": 0.6261608606198403,
      "pinball_loss_p90": 0.5084283197839189,
      "position": "RB",
      "prediction_season": 2025,
      "projection_tier": "lower",
      "rows": 22,
      "target_name": "fantasy_points_per_game"
    },
    {
      "candidate_name": "hist_gradient_boosting",
      "empirical_coverage_p10_p90": 0.7591240875912408,
      "evaluation_scope": "validation",
      "mean_interval_width_p10_p90": 9.540987802028777,
      "pinball_loss_p10": 0.6560280354138611,
      "pinball_loss_p50": 1.4034238782187325,
      "pinball_loss_p90": 0.7851689021406251,
      "position": "RB",
      "prediction_season": 2020,
      "projection_tier": "all",
      "rows": 137,
      "target_name": "fantasy_points_per_game"
    },
    {
      "candidate_name": "hist_gradient_boosting",
      "empirical_coverage_p10_p90": 0.6176470588235294,
      "evaluation_scope": "validation",
      "mean_interval_width_p10_p90": 9.540987802028775,
      "pinball_loss_p10": 0.8049984309129089,
      "pinball_loss_p50": 1.829890014978253,
      "pinball_loss_p90": 0.8826871163187856,
      "position": "RB",
      "prediction_season": 2020,
      "projection_tier": "top",
      "rows": 68,
      "target_name": "fantasy_points_per_game"
    },
    {
      "candidate_name": "hist_gradient_boosting",
      "empirical_coverage_p10_p90": 0.8541666666666666,
      "evaluation_scope": "validation",
      "mean_interval_width_p10_p90": 9.540987802028774,
      "pinball_loss_p10": 0.5349460273135799,
      "pinball_loss_p50": 1.2756398153041875,
      "pinball_loss_p90": 0.7701641570395227,
      "position": "RB",
      "prediction_season": 2020,
      "projection_tier": "middle",
      "rows": 48,
      "target_name": "fantasy_points_per_game"
    },
    {
      "candidate_name": "hist_gradient_boosting",
      "empirical_coverage_p10_p90": 1.0,
      "evaluation_scope": "validation",
      "mean_interval_width_p10_p90": 9.540987802028777,
      "pinball_loss_p10": 0.4504065827890156,
      "pinball_loss_p50": 0.3145637696592435,
      "pinball_loss_p90": 0.503692197413862,
      "position": "RB",
      "prediction_season": 2020,
      "projection_tier": "lower",
      "rows": 21,
      "target_name": "fantasy_points_per_game"
    },
    {
      "candidate_name": "hist_gradient_boosting",
      "empirical_coverage_p10_p90": 0.8389261744966443,
      "evaluation_scope": "validation",
      "mean_interval_width_p10_p90": 9.808807163501472,
      "pinball_loss_p10": 0.5754846113645434,
      "pinball_loss_p50": 1.325099032539861,
      "pinball_loss_p90": 0.6698985863466534,
      "position": "RB",
      "prediction_season": 2021,
      "projection_tier": "all",
      "rows": 149,
      "target_name": "fantasy_points_per_game"
    },
    {
      "candidate_name": "hist_gradient_boosting",
      "empirical_coverage_p10_p90": 0.7692307692307693,
      "evaluation_scope": "validation",
      "mean_interval_width_p10_p90": 9.808807163501474,
      "pinball_loss_p10": 0.6426549573700269,
      "pinball_loss_p50": 1.7171861341400012,
      "pinball_loss_p90": 0.7197780273452362,
      "position": "RB",
      "prediction_season": 2021,
      "projection_tier": "top",
      "rows": 65,
      "target_name": "fantasy_points_per_game"
    },
    {
      "candidate_name": "hist_gradient_boosting",
      "empirical_coverage_p10_p90": 0.8679245283018868,
      "evaluation_scope": "validation",
      "mean_interval_width_p10_p90": 9.80880716350147,
      "pinball_loss_p10": 0.5291005231662584,
      "pinball_loss_p50": 1.2716116918740332,
      "pinball_loss_p90": 0.6583343357019655,
      "position": "RB",
      "prediction_season": 2021,
      "projection_tier": "middle",
      "rows": 53,
      "target_name": "fantasy_points_per_game"
    },
    {
      "candidate_name": "hist_gradient_boosting",
      "empirical_coverage_p10_p90": 0.9354838709677419,
      "evaluation_scope": "validation",
      "mean_interval_width_p10_p90": 9.808807163501472,
      "pinball_loss_p10": 0.5139453914985013,
      "pinball_loss_p50": 0.5944270148392077,
      "pinball_loss_p90": 0.5850837998711882,
      "position": "RB",
      "prediction_season": 2021,
      "projection_tier": "lower",
      "rows": 31,
      "target_name": "fantasy_points_per_game"
    },
    {
      "candidate_name": "hist_gradient_boosting",
      "empirical_coverage_p10_p90": 0.8489208633093526,
      "evaluation_scope": "validation",
      "mean_interval_width_p10_p90": 9.666566239542597,
      "pinball_loss_p10": 0.5681011270763943,
      "pinball_loss_p50": 1.2712983464175276,
      "pinball_loss_p90": 0.7122976649502607,
      "position": "RB",
      "prediction_season": 2022,
      "projection_tier": "all",
      "rows": 139,
      "target_name": "fantasy_points_per_game"
    },
    {
      "candidate_name": "hist_gradient_boosting",
      "empirical_coverage_p10_p90": 0.7142857142857143,
      "evaluation_scope": "validation",
      "mean_interval_width_p10_p90": 9.666566239542597,
      "pinball_loss_p10": 0.762434696980921,
      "pinball_loss_p50": 1.720027493961658,
      "pinball_loss_p90": 0.8194306312565797,
      "position": "RB",
      "prediction_season": 2022,
      "projection_tier": "top",
      "rows": 63,
      "target_name": "fantasy_points_per_game"
    },
    {
      "candidate_name": "hist_gradient_boosting",
      "empirical_coverage_p10_p90": 0.9433962264150944,
      "evaluation_scope": "validation",
      "mean_interval_width_p10_p90": 9.666566239542597,
      "pinball_loss_p10": 0.39504099235085144,
      "pinball_loss_p50": 1.141812078040978,
      "pinball_loss_p90": 0.6631630465509323,
      "position": "RB",
      "prediction_season": 2022,
      "projection_tier": "middle",
      "rows": 53,
      "target_name": "fantasy_points_per_game"
    },
    {
      "candidate_name": "hist_gradient_boosting",
      "empirical_coverage_p10_p90": 1.0,
      "evaluation_scope": "validation",
      "mean_interval_width_p10_p90": 9.666566239542595,
      "pinball_loss_p10": 0.43458687648807165,
      "pinball_loss_p50": 0.3405520824469577,
      "pinball_loss_p90": 0.532069747466188,
      "position": "RB",
      "prediction_season": 2022,
      "projection_tier": "lower",
      "rows": 23,
      "target_name": "fantasy_points_per_game"
    },
    {
      "candidate_name": "hist_gradient_boosting",
      "empirical_coverage_p10_p90": 0.8208955223880597,
      "evaluation_scope": "validation",
      "mean_interval_width_p10_p90": 9.387212732396799,
      "pinball_loss_p10": 0.5668335697405993,
      "pinball_loss_p50": 1.4064967925146346,
      "pinball_loss_p90": 0.8247825181440056,
      "position": "RB",
      "prediction_season": 2023,
      "projection_tier": "all",
      "rows": 134,
      "target_name": "fantasy_points_per_game"
    },
    {
      "candidate_name": "hist_gradient_boosting",
      "empirical_coverage_p10_p90": 0.7142857142857143,
      "evaluation_scope": "validation",
      "mean_interval_width_p10_p90": 9.387212732396799,
      "pinball_loss_p10": 0.6993191279358851,
      "pinball_loss_p50": 1.7931482499975167,
      "pinball_loss_p90": 0.8349423677215952,
      "position": "RB",
      "prediction_season": 2023,
      "projection_tier": "top",
      "rows": 56,
      "target_name": "fantasy_points_per_game"
    },
    {
      "candidate_name": "hist_gradient_boosting",
      "empirical_coverage_p10_p90": 0.8679245283018868,
      "evaluation_scope": "validation",
      "mean_interval_width_p10_p90": 9.387212732396797,
      "pinball_loss_p10": 0.4575210258127924,
      "pinball_loss_p50": 1.3578886945720279,
      "pinball_loss_p90": 0.8730817822240228,
      "position": "RB",
      "prediction_season": 2023,
      "projection_tier": "middle",
      "rows": 53,
      "target_name": "fantasy_points_per_game"
    },
    {
      "candidate_name": "hist_gradient_boosting",
      "empirical_coverage_p10_p90": 0.96,
      "evaluation_scope": "validation",
      "mean_interval_width_p10_p90": 9.387212732396797,
      "pinball_loss_p10": 0.5018085125101094,
      "pinball_loss_p50": 0.643446695391305,
      "pinball_loss_p90": 0.6996300152405698,
      "position": "RB",
      "prediction_season": 2023,
      "projection_tier": "lower",
      "rows": 25,
      "target_name": "fantasy_points_per_game"
    },
    {
      "candidate_name": "hist_gradient_boosting",
      "empirical_coverage_p10_p90": 0.8188976377952756,
      "evaluation_scope": "validation",
      "mean_interval_width_p10_p90": 9.050711895239814,
      "pinball_loss_p10": 0.506814255616019,
      "pinball_loss_p50": 1.2532400778588515,
      "pinball_loss_p90": 0.7567419581150577,
      "position": "RB",
      "prediction_season": 2024,
      "projection_tier": "all",
      "rows": 127,
      "target_name": "fantasy_points_per_game"
    },
    {
      "candidate_name": "hist_gradient_boosting",
      "empirical_coverage_p10_p90": 0.6785714285714286,
      "evaluation_scope": "validation",
      "mean_interval_width_p10_p90": 9.050711895239813,
      "pinball_loss_p10": 0.6166022068625144,
      "pinball_loss_p50": 1.855824433528889,
      "pinball_loss_p90": 0.8957087625208234,
      "position": "RB",
      "prediction_season": 2024,
      "projection_tier": "top",
      "rows": 56,
      "target_name": "fantasy_points_per_game"
    },
    {
      "candidate_name": "hist_gradient_boosting",
      "empirical_coverage_p10_p90": 0.8958333333333334,
      "evaluation_scope": "validation",
      "mean_interval_width_p10_p90": 9.050711895239813,
      "pinball_loss_p10": 0.43018154229027816,
      "pinball_loss_p50": 0.9778505789623771,
      "pinball_loss_p90": 0.714934863945727,
      "position": "RB",
      "prediction_season": 2024,
      "projection_tier": "middle",
      "rows": 48,
      "target_name": "fantasy_points_per_game"
    },
    {
      "candidate_name": "hist_gradient_boosting",
      "empirical_coverage_p10_p90": 1.0,
      "evaluation_scope": "validation",
      "mean_interval_width_p10_p90": 9.050711895239807,
      "pinball_loss_p10": 0.3994336021304456,
      "pinball_loss_p50": 0.3608040791418373,
      "pinball_loss_p90": 0.5056375873935355,
      "position": "RB",
      "prediction_season": 2024,
      "projection_tier": "lower",
      "rows": 23,
      "target_name": "fantasy_points_per_game"
    }
  ],
  "empirical_not_guaranteed": true,
  "method": "training-only signed out-of-fold residual quantiles",
  "operational_center": "training_only_residual_adjusted_p50",
  "residual_rows": 389,
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
    "feature_response": "docs/images/phase4/phase4-7ae8e9aed04bffca00c0/attempt-866987f75a2c406693cf892d49adc975/feature_response.svg",
    "hgb_permutation_importance": "docs/images/phase4/phase4-7ae8e9aed04bffca00c0/attempt-866987f75a2c406693cf892d49adc975/hgb_permutation_importance.svg",
    "interval_coverage_width": "docs/images/phase4/phase4-7ae8e9aed04bffca00c0/attempt-866987f75a2c406693cf892d49adc975/interval_coverage_width.svg",
    "ridge_coefficients": "docs/images/phase4/phase4-7ae8e9aed04bffca00c0/attempt-866987f75a2c406693cf892d49adc975/ridge_coefficients.svg",
    "season_mae_comparison": "docs/images/phase4/phase4-7ae8e9aed04bffca00c0/attempt-866987f75a2c406693cf892d49adc975/season_mae_comparison.svg",
    "segment_mae": "docs/images/phase4/phase4-7ae8e9aed04bffca00c0/attempt-866987f75a2c406693cf892d49adc975/segment_mae.svg",
    "test_predicted_vs_actual": "docs/images/phase4/phase4-7ae8e9aed04bffca00c0/attempt-866987f75a2c406693cf892d49adc975/test_predicted_vs_actual.svg",
    "test_residuals": "docs/images/phase4/phase4-7ae8e9aed04bffca00c0/attempt-866987f75a2c406693cf892d49adc975/test_residuals.svg"
  },
  "feature_responses": [
    {
      "explanation_scope": "registered_final_artifact_descriptive_on_2025_training_rows",
      "feature": "lag1_fantasy_points_per_game",
      "interpretation": "This explanation is associative, not causal; changing a feature here does not establish that the feature causes the prediction to change.",
      "method": "one_way_average_partial_dependence",
      "points": [
        {
          "average_prediction": 4.90143024890511,
          "feature_value": 0.0
        },
        {
          "average_prediction": 4.843877502683194,
          "feature_value": 1.5897001527883878
        },
        {
          "average_prediction": 4.843877502683194,
          "feature_value": 3.1794003055767757
        },
        {
          "average_prediction": 4.858577891060759,
          "feature_value": 4.7691004583651635
        },
        {
          "average_prediction": 4.816267943161915,
          "feature_value": 6.358800611153551
        },
        {
          "average_prediction": 4.814115733824974,
          "feature_value": 7.948500763941939
        },
        {
          "average_prediction": 6.229121399341482,
          "feature_value": 9.538200916730327
        },
        {
          "average_prediction": 6.663135004722001,
          "feature_value": 11.127901069518714
        },
        {
          "average_prediction": 6.675798628609471,
          "feature_value": 12.717601222307103
        },
        {
          "average_prediction": 6.690661028756622,
          "feature_value": 14.307301375095491
        },
        {
          "average_prediction": 6.647687067907555,
          "feature_value": 15.897001527883878
        },
        {
          "average_prediction": 6.726940763098729,
          "feature_value": 17.486701680672265
        }
      ],
      "response_status": "stable_numeric_grid"
    },
    {
      "explanation_scope": "registered_final_artifact_descriptive_on_2025_training_rows",
      "feature": "lag1_fantasy_points_total",
      "interpretation": "This explanation is associative, not causal; changing a feature here does not establish that the feature causes the prediction to change.",
      "method": "one_way_average_partial_dependence",
      "points": [
        {
          "average_prediction": 4.906312315549724,
          "feature_value": 0.0
        },
        {
          "average_prediction": 4.905485997614399,
          "feature_value": 24.831818181818175
        },
        {
          "average_prediction": 4.998648641284884,
          "feature_value": 49.66363636363635
        },
        {
          "average_prediction": 4.946993853091255,
          "feature_value": 74.49545454545452
        },
        {
          "average_prediction": 5.6068800490845,
          "feature_value": 99.3272727272727
        },
        {
          "average_prediction": 6.903270845970326,
          "feature_value": 124.15909090909088
        },
        {
          "average_prediction": 6.925928288371197,
          "feature_value": 148.99090909090904
        },
        {
          "average_prediction": 7.157589691942641,
          "feature_value": 173.82272727272724
        },
        {
          "average_prediction": 7.222616322301189,
          "feature_value": 198.6545454545454
        },
        {
          "average_prediction": 7.219129972164007,
          "feature_value": 223.48636363636356
        },
        {
          "average_prediction": 7.344265269905224,
          "feature_value": 248.31818181818176
        },
        {
          "average_prediction": 7.344265269905224,
          "feature_value": 273.1499999999999
        }
      ],
      "response_status": "stable_numeric_grid"
    },
    {
      "explanation_scope": "registered_final_artifact_descriptive_on_2025_training_rows",
      "feature": "weighted_3yr_fantasy_points_per_game",
      "interpretation": "This explanation is associative, not causal; changing a feature here does not establish that the feature causes the prediction to change.",
      "method": "one_way_average_partial_dependence",
      "points": [
        {
          "average_prediction": 4.697174445705613,
          "feature_value": 0.047212121212121226
        },
        {
          "average_prediction": 4.687764288627802,
          "feature_value": 1.5688770286420355
        },
        {
          "average_prediction": 5.089628851107395,
          "feature_value": 3.0905419360719497
        },
        {
          "average_prediction": 5.336218902086725,
          "feature_value": 4.612206843501864
        },
        {
          "average_prediction": 5.32597502997069,
          "feature_value": 6.133871750931778
        },
        {
          "average_prediction": 5.351227698758291,
          "feature_value": 7.655536658361692
        },
        {
          "average_prediction": 5.357418131211243,
          "feature_value": 9.177201565791608
        },
        {
          "average_prediction": 5.42508681068652,
          "feature_value": 10.698866473221521
        },
        {
          "average_prediction": 6.438424069176282,
          "feature_value": 12.220531380651435
        },
        {
          "average_prediction": 6.6676826096549195,
          "feature_value": 13.742196288081349
        },
        {
          "average_prediction": 7.021681369741253,
          "feature_value": 15.263861195511263
        },
        {
          "average_prediction": 7.81539628689434,
          "feature_value": 16.785526102941176
        }
      ],
      "response_status": "stable_numeric_grid"
    }
  ],
  "importance": [
    {
      "explanation_scope": "registered_final_artifact_descriptive_on_2025_training_rows",
      "feature": "weighted_3yr_fantasy_points_per_game",
      "importance_mean": 0.6784250315019225,
      "importance_std": 0.06143556976549716,
      "rank": 1
    },
    {
      "explanation_scope": "registered_final_artifact_descriptive_on_2025_training_rows",
      "feature": "lag1_fantasy_points_total",
      "importance_mean": 0.6617237970112226,
      "importance_std": 0.08919104623240694,
      "rank": 2
    },
    {
      "explanation_scope": "registered_final_artifact_descriptive_on_2025_training_rows",
      "feature": "lag1_fantasy_points_per_game",
      "importance_mean": 0.6138349138884106,
      "importance_std": 0.09168864917274466,
      "rank": 3
    },
    {
      "explanation_scope": "registered_final_artifact_descriptive_on_2025_training_rows",
      "feature": "weighted_3yr_rushing_yards_per_game",
      "importance_mean": 0.5788429725442968,
      "importance_std": 0.034568489924526054,
      "rank": 4
    },
    {
      "explanation_scope": "registered_final_artifact_descriptive_on_2025_training_rows",
      "feature": "age_at_cutoff",
      "importance_mean": 0.4725154225084197,
      "importance_std": 0.07117808315171187,
      "rank": 5
    },
    {
      "explanation_scope": "registered_final_artifact_descriptive_on_2025_training_rows",
      "feature": "draft_pick",
      "importance_mean": 0.20141156526312143,
      "importance_std": 0.05120328219180875,
      "rank": 6
    },
    {
      "explanation_scope": "registered_final_artifact_descriptive_on_2025_training_rows",
      "feature": "weighted_3yr_targets_per_game",
      "importance_mean": 0.1368795559130874,
      "importance_std": 0.028977425197465396,
      "rank": 7
    },
    {
      "explanation_scope": "registered_final_artifact_descriptive_on_2025_training_rows",
      "feature": "draft_round",
      "importance_mean": 0.12251226516991749,
      "importance_std": 0.019270071037289945,
      "rank": 8
    },
    {
      "explanation_scope": "registered_final_artifact_descriptive_on_2025_training_rows",
      "feature": "weighted_3yr_receiving_yards_per_game",
      "importance_mean": 0.090465091099597,
      "importance_std": 0.015457449978234878,
      "rank": 9
    },
    {
      "explanation_scope": "registered_final_artifact_descriptive_on_2025_training_rows",
      "feature": "lag1_stat_games",
      "importance_mean": 0.08022984887443281,
      "importance_std": 0.022978159367069737,
      "rank": 10
    },
    {
      "explanation_scope": "registered_final_artifact_descriptive_on_2025_training_rows",
      "feature": "weighted_3yr_receptions_per_game",
      "importance_mean": 0.05356971949087756,
      "importance_std": 0.016050017466523032,
      "rank": 11
    },
    {
      "explanation_scope": "registered_final_artifact_descriptive_on_2025_training_rows",
      "feature": "weighted_3yr_fumbles_lost_per_game",
      "importance_mean": 0.050979102754445726,
      "importance_std": 0.010044540930003402,
      "rank": 12
    },
    {
      "explanation_scope": "registered_final_artifact_descriptive_on_2025_training_rows",
      "feature": "nfl_experience_years",
      "importance_mean": 0.042774574864507066,
      "importance_std": 0.016066516318014184,
      "rank": 13
    },
    {
      "explanation_scope": "registered_final_artifact_descriptive_on_2025_training_rows",
      "feature": "lag1_games_active",
      "importance_mean": 0.04040197332527411,
      "importance_std": 0.024206849582055035,
      "rank": 14
    },
    {
      "explanation_scope": "registered_final_artifact_descriptive_on_2025_training_rows",
      "feature": "weighted_3yr_rushing_tds_per_game",
      "importance_mean": 0.03597553017697237,
      "importance_std": 0.016064030735624162,
      "rank": 15
    },
    {
      "explanation_scope": "registered_final_artifact_descriptive_on_2025_training_rows",
      "feature": "weighted_3yr_passing_yards_per_game",
      "importance_mean": 0.03411541079106399,
      "importance_std": 0.018993312268790526,
      "rank": 16
    },
    {
      "explanation_scope": "registered_final_artifact_descriptive_on_2025_training_rows",
      "feature": "previous_team",
      "importance_mean": 0.033207349539766985,
      "importance_std": 0.004858561157938001,
      "rank": 17
    },
    {
      "explanation_scope": "registered_final_artifact_descriptive_on_2025_training_rows",
      "feature": "weighted_3yr_receiving_tds_per_game",
      "importance_mean": 0.0330781548621605,
      "importance_std": 0.011623179704525335,
      "rank": 18
    },
    {
      "explanation_scope": "registered_final_artifact_descriptive_on_2025_training_rows",
      "feature": "weighted_3yr_carries_per_game",
      "importance_mean": 0.02194790529264399,
      "importance_std": 0.013850461833402555,
      "rank": 19
    },
    {
      "explanation_scope": "registered_final_artifact_descriptive_on_2025_training_rows",
      "feature": "weighted_3yr_games_active",
      "importance_mean": 0.019177507024860763,
      "importance_std": 0.018598679957025684,
      "rank": 20
    }
  ],
  "method": "registered-artifact descriptive permutation importance and partial dependence on 2025 rows, computed only after champion selection"
}
````

## Data lineage

````json
{
  "baseline_report_fingerprint": "72043c4baf8f0e5b1b63d68af77b92b9f5f497483cdaa279155e586127944965",
  "build_fingerprint": "f195dcb17a1a386b2f2003d87a06921550235cbec62aecd0f4eda419aa664cd7",
  "feature_data_fingerprint": "d2bdda170fcbf88ccfe0b3f437615583a0684057eebe1fc12aa65463a47cf9cf",
  "model_config_fingerprint": "1330e36662458945cc117f0b56daade21e7cb1c4bc91779b7a9d2c96e0d1d3f8",
  "model_feature_fingerprint": "9b7be095acc27d5b3bb86a028d3e321cd8fd354914fef1aa8a2843a3ee5666e8",
  "scoring_ruleset_fingerprint": "9f660dd5c8db91e63a1c43a5db74a3848b0554b2acf94d0fd891fe58b4eb7871",
  "target_data_fingerprint": "dd759bbf87c146884e68425079b3a759d1d6d4bb434d5bccee6d9d91c98c56a9"
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

- Project-relative path: `models/artifacts/phase4-7ae8e9aed04bffca00c0/attempt-866987f75a2c406693cf892d49adc975/RB/fantasy_points_per_game/hist_gradient_boosting.joblib`
- SHA-256: `c27fe57b015ecb6c09955ea4f034a09dd4d74f0ec1073bf8fb041599f5adcb0a`

## Additional metadata

````json
{
  "publication_id": "attempt-866987f75a2c406693cf892d49adc975"
}
````
