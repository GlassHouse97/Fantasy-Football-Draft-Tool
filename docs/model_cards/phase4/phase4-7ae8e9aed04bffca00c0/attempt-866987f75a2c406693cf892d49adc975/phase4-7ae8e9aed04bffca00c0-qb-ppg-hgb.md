# Model Card: phase4-7ae8e9aed04bffca00c0-qb-ppg-hgb

- Model ID: `phase4-7ae8e9aed04bffca00c0-qb-ppg-hgb`
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
  "position": "QB",
  "target_name": "fantasy_points_per_game",
  "test_mae": 4.341531857772311,
  "test_rows": 66,
  "test_season": 2025,
  "validation_mae": 4.24004050834275,
  "validation_rows": 348,
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
    "candidate_mae": 4.24004050834275,
    "ci95_lower": -0.2688073988829739,
    "ci95_upper": 0.28802816531906433,
    "direction": "uncertain",
    "mae_difference_candidate_minus_reference": 0.00995608765311129,
    "n_resamples": 2000,
    "reference_mae": 4.230084420689638,
    "rows": 348,
    "seed": 42
  },
  "decision_status": "learned_regression_baseline_retained",
  "learned_improvement_status": "regression",
  "reference_metrics": {
    "candidate_name": "age_position_adjusted",
    "candidate_source": "baseline",
    "position": "QB",
    "target_name": "fantasy_points_per_game",
    "test_mae": 4.63816089527217,
    "test_rows": 66,
    "test_season": 2025,
    "validation_mae": 4.230084420689638,
    "validation_rows": 348,
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
      "empirical_coverage_p10_p90": 0.7575757575757576,
      "evaluation_scope": "test",
      "mean_interval_width_p10_p90": 12.471010050241901,
      "pinball_loss_p10": 1.0067454349076634,
      "pinball_loss_p50": 2.1707659288861554,
      "pinball_loss_p90": 0.9092014299078769,
      "position": "QB",
      "prediction_season": 2025,
      "projection_tier": "all",
      "rows": 66,
      "target_name": "fantasy_points_per_game"
    },
    {
      "candidate_name": "hist_gradient_boosting",
      "empirical_coverage_p10_p90": 0.8148148148148148,
      "evaluation_scope": "test",
      "mean_interval_width_p10_p90": 12.471010050241897,
      "pinball_loss_p10": 1.14262117044235,
      "pinball_loss_p50": 1.7965571834499139,
      "pinball_loss_p90": 0.789492881626635,
      "position": "QB",
      "prediction_season": 2025,
      "projection_tier": "top",
      "rows": 27,
      "target_name": "fantasy_points_per_game"
    },
    {
      "candidate_name": "hist_gradient_boosting",
      "empirical_coverage_p10_p90": 0.6875,
      "evaluation_scope": "test",
      "mean_interval_width_p10_p90": 12.471010050241897,
      "pinball_loss_p10": 0.9680810376615753,
      "pinball_loss_p50": 2.6146128165139886,
      "pinball_loss_p90": 0.9470549550691223,
      "position": "QB",
      "prediction_season": 2025,
      "projection_tier": "middle",
      "rows": 32,
      "target_name": "fantasy_points_per_game"
    },
    {
      "candidate_name": "hist_gradient_boosting",
      "empirical_coverage_p10_p90": 0.8571428571428571,
      "evaluation_scope": "test",
      "mean_interval_width_p10_p90": 12.4710100502419,
      "pinball_loss_p10": 0.6594048423988477,
      "pinball_loss_p50": 1.585128174984421,
      "pinball_loss_p90": 1.197889715398402,
      "position": "QB",
      "prediction_season": 2025,
      "projection_tier": "lower",
      "rows": 7,
      "target_name": "fantasy_points_per_game"
    },
    {
      "candidate_name": "hist_gradient_boosting",
      "empirical_coverage_p10_p90": 0.7941176470588235,
      "evaluation_scope": "validation",
      "mean_interval_width_p10_p90": 14.523804574478973,
      "pinball_loss_p10": 1.0926305952464508,
      "pinball_loss_p50": 2.278492394711933,
      "pinball_loss_p90": 1.0033564791991452,
      "position": "QB",
      "prediction_season": 2020,
      "projection_tier": "all",
      "rows": 68,
      "target_name": "fantasy_points_per_game"
    },
    {
      "candidate_name": "hist_gradient_boosting",
      "empirical_coverage_p10_p90": 0.8620689655172413,
      "evaluation_scope": "validation",
      "mean_interval_width_p10_p90": 14.523804574478971,
      "pinball_loss_p10": 1.3293472705103548,
      "pinball_loss_p50": 2.330463450226229,
      "pinball_loss_p90": 0.788926752204491,
      "position": "QB",
      "prediction_season": 2020,
      "projection_tier": "top",
      "rows": 29,
      "target_name": "fantasy_points_per_game"
    },
    {
      "candidate_name": "hist_gradient_boosting",
      "empirical_coverage_p10_p90": 0.7,
      "evaluation_scope": "validation",
      "mean_interval_width_p10_p90": 14.52380457447897,
      "pinball_loss_p10": 0.9019640812410511,
      "pinball_loss_p50": 2.395864121208923,
      "pinball_loss_p90": 1.2846677647588503,
      "position": "QB",
      "prediction_season": 2020,
      "projection_tier": "middle",
      "rows": 30,
      "target_name": "fantasy_points_per_game"
    },
    {
      "candidate_name": "hist_gradient_boosting",
      "empirical_coverage_p10_p90": 0.8888888888888888,
      "evaluation_scope": "validation",
      "mean_interval_width_p10_p90": 14.523804574478978,
      "pinball_loss_p10": 0.9654319105252055,
      "pinball_loss_p50": 1.7197910163981225,
      "pinball_loss_p90": 0.7565924254273475,
      "position": "QB",
      "prediction_season": 2020,
      "projection_tier": "lower",
      "rows": 9,
      "target_name": "fantasy_points_per_game"
    },
    {
      "candidate_name": "hist_gradient_boosting",
      "empirical_coverage_p10_p90": 0.8088235294117647,
      "evaluation_scope": "validation",
      "mean_interval_width_p10_p90": 14.40206649373336,
      "pinball_loss_p10": 1.2011534176213918,
      "pinball_loss_p50": 2.16943791672095,
      "pinball_loss_p90": 1.0540749279938173,
      "position": "QB",
      "prediction_season": 2021,
      "projection_tier": "all",
      "rows": 68,
      "target_name": "fantasy_points_per_game"
    },
    {
      "candidate_name": "hist_gradient_boosting",
      "empirical_coverage_p10_p90": 0.8518518518518519,
      "evaluation_scope": "validation",
      "mean_interval_width_p10_p90": 14.402066493733356,
      "pinball_loss_p10": 1.4186488342489811,
      "pinball_loss_p50": 1.7825053473410803,
      "pinball_loss_p90": 1.0288454990569214,
      "position": "QB",
      "prediction_season": 2021,
      "projection_tier": "top",
      "rows": 27,
      "target_name": "fantasy_points_per_game"
    },
    {
      "candidate_name": "hist_gradient_boosting",
      "empirical_coverage_p10_p90": 0.7941176470588235,
      "evaluation_scope": "validation",
      "mean_interval_width_p10_p90": 14.402066493733358,
      "pinball_loss_p10": 1.0489262795697394,
      "pinball_loss_p50": 2.393424598764071,
      "pinball_loss_p90": 0.9408041981093687,
      "position": "QB",
      "prediction_season": 2021,
      "projection_tier": "middle",
      "rows": 34,
      "target_name": "fantasy_points_per_game"
    },
    {
      "candidate_name": "hist_gradient_boosting",
      "empirical_coverage_p10_p90": 0.7142857142857143,
      "evaluation_scope": "validation",
      "mean_interval_width_p10_p90": 14.402066493733358,
      "pinball_loss_p10": 1.1016314811658572,
      "pinball_loss_p50": 2.573956800119569,
      "pinball_loss_p90": 1.701560556189168,
      "position": "QB",
      "prediction_season": 2021,
      "projection_tier": "lower",
      "rows": 7,
      "target_name": "fantasy_points_per_game"
    },
    {
      "candidate_name": "hist_gradient_boosting",
      "empirical_coverage_p10_p90": 0.8918918918918919,
      "evaluation_scope": "validation",
      "mean_interval_width_p10_p90": 14.56506184021768,
      "pinball_loss_p10": 0.774119941303309,
      "pinball_loss_p50": 2.0062702904453764,
      "pinball_loss_p90": 0.9884634590982294,
      "position": "QB",
      "prediction_season": 2022,
      "projection_tier": "all",
      "rows": 74,
      "target_name": "fantasy_points_per_game"
    },
    {
      "candidate_name": "hist_gradient_boosting",
      "empirical_coverage_p10_p90": 0.9310344827586207,
      "evaluation_scope": "validation",
      "mean_interval_width_p10_p90": 14.56506184021769,
      "pinball_loss_p10": 0.6532742359078823,
      "pinball_loss_p50": 1.8744298154705121,
      "pinball_loss_p90": 0.8959222273012368,
      "position": "QB",
      "prediction_season": 2022,
      "projection_tier": "top",
      "rows": 29,
      "target_name": "fantasy_points_per_game"
    },
    {
      "candidate_name": "hist_gradient_boosting",
      "empirical_coverage_p10_p90": 0.8333333333333334,
      "evaluation_scope": "validation",
      "mean_interval_width_p10_p90": 14.56506184021769,
      "pinball_loss_p10": 0.8897309895402292,
      "pinball_loss_p50": 2.3558673933351026,
      "pinball_loss_p90": 1.126928480913724,
      "position": "QB",
      "prediction_season": 2022,
      "projection_tier": "middle",
      "rows": 30,
      "target_name": "fantasy_points_per_game"
    },
    {
      "candidate_name": "hist_gradient_boosting",
      "empirical_coverage_p10_p90": 0.9333333333333333,
      "evaluation_scope": "validation",
      "mean_interval_width_p10_p90": 14.565061840217682,
      "pinball_loss_p10": 0.7765328752606258,
      "pinball_loss_p50": 1.5619676696173277,
      "pinball_loss_p90": 0.8904464636080919,
      "position": "QB",
      "prediction_season": 2022,
      "projection_tier": "lower",
      "rows": 15,
      "target_name": "fantasy_points_per_game"
    },
    {
      "candidate_name": "hist_gradient_boosting",
      "empirical_coverage_p10_p90": 0.7428571428571429,
      "evaluation_scope": "validation",
      "mean_interval_width_p10_p90": 12.490614722712367,
      "pinball_loss_p10": 1.0704715246932086,
      "pinball_loss_p50": 2.0683037462182625,
      "pinball_loss_p90": 1.0470395873995815,
      "position": "QB",
      "prediction_season": 2023,
      "projection_tier": "all",
      "rows": 70,
      "target_name": "fantasy_points_per_game"
    },
    {
      "candidate_name": "hist_gradient_boosting",
      "empirical_coverage_p10_p90": 0.8148148148148148,
      "evaluation_scope": "validation",
      "mean_interval_width_p10_p90": 12.490614722712369,
      "pinball_loss_p10": 1.346779467367936,
      "pinball_loss_p50": 1.8640768847379576,
      "pinball_loss_p90": 0.8644380428418788,
      "position": "QB",
      "prediction_season": 2023,
      "projection_tier": "top",
      "rows": 27,
      "target_name": "fantasy_points_per_game"
    },
    {
      "candidate_name": "hist_gradient_boosting",
      "empirical_coverage_p10_p90": 0.6774193548387096,
      "evaluation_scope": "validation",
      "mean_interval_width_p10_p90": 12.490614722712372,
      "pinball_loss_p10": 0.8977140954990969,
      "pinball_loss_p50": 2.2288189065399306,
      "pinball_loss_p90": 0.9889461851203424,
      "position": "QB",
      "prediction_season": 2023,
      "projection_tier": "middle",
      "rows": 31,
      "target_name": "fantasy_points_per_game"
    },
    {
      "candidate_name": "hist_gradient_boosting",
      "empirical_coverage_p10_p90": 0.75,
      "evaluation_scope": "validation",
      "mean_interval_width_p10_p90": 12.490614722712365,
      "pinball_loss_p10": 0.8950686790931933,
      "pinball_loss_p50": 2.113150020384636,
      "pinball_loss_p90": 1.607967685209113,
      "position": "QB",
      "prediction_season": 2023,
      "projection_tier": "lower",
      "rows": 12,
      "target_name": "fantasy_points_per_game"
    },
    {
      "candidate_name": "hist_gradient_boosting",
      "empirical_coverage_p10_p90": 0.7941176470588235,
      "evaluation_scope": "validation",
      "mean_interval_width_p10_p90": 12.473271544720019,
      "pinball_loss_p10": 0.818612925008084,
      "pinball_loss_p50": 2.089154758028917,
      "pinball_loss_p90": 0.8677353125814711,
      "position": "QB",
      "prediction_season": 2024,
      "projection_tier": "all",
      "rows": 68,
      "target_name": "fantasy_points_per_game"
    },
    {
      "candidate_name": "hist_gradient_boosting",
      "empirical_coverage_p10_p90": 0.7777777777777778,
      "evaluation_scope": "validation",
      "mean_interval_width_p10_p90": 12.473271544720022,
      "pinball_loss_p10": 0.9694217654994302,
      "pinball_loss_p50": 1.990481250035768,
      "pinball_loss_p90": 0.8997548232972825,
      "position": "QB",
      "prediction_season": 2024,
      "projection_tier": "top",
      "rows": 27,
      "target_name": "fantasy_points_per_game"
    },
    {
      "candidate_name": "hist_gradient_boosting",
      "empirical_coverage_p10_p90": 0.7837837837837838,
      "evaluation_scope": "validation",
      "mean_interval_width_p10_p90": 12.473271544720024,
      "pinball_loss_p10": 0.7285784194591592,
      "pinball_loss_p50": 2.273077400753961,
      "pinball_loss_p90": 0.8718162735324755,
      "position": "QB",
      "prediction_season": 2024,
      "projection_tier": "middle",
      "rows": 37,
      "target_name": "fantasy_points_per_game"
    },
    {
      "candidate_name": "hist_gradient_boosting",
      "empirical_coverage_p10_p90": 1.0,
      "evaluation_scope": "validation",
      "mean_interval_width_p10_p90": 12.473271544720022,
      "pinball_loss_p10": 0.6334724280190505,
      "pinball_loss_p50": 1.053916491776016,
      "pinball_loss_p90": 0.6138547264529517,
      "position": "QB",
      "prediction_season": 2024,
      "projection_tier": "lower",
      "rows": 4,
      "target_name": "fantasy_points_per_game"
    }
  ],
  "empirical_not_guaranteed": true,
  "method": "training-only signed out-of-fold residual quantiles",
  "operational_center": "training_only_residual_adjusted_p50",
  "residual_rows": 204,
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
      "feature": "draft_pick",
      "interpretation": "This explanation is associative, not causal; changing a feature here does not establish that the feature causes the prediction to change.",
      "method": "one_way_average_partial_dependence",
      "points": [
        {
          "average_prediction": 11.355295382349457,
          "feature_value": 1.0
        },
        {
          "average_prediction": 10.809650276502367,
          "feature_value": 18.527272727272724
        },
        {
          "average_prediction": 9.878965576381523,
          "feature_value": 36.05454545454545
        },
        {
          "average_prediction": 9.612185980145146,
          "feature_value": 53.58181818181817
        },
        {
          "average_prediction": 9.679145322911724,
          "feature_value": 71.1090909090909
        },
        {
          "average_prediction": 9.391817852618736,
          "feature_value": 88.63636363636363
        },
        {
          "average_prediction": 9.27439249086381,
          "feature_value": 106.16363636363634
        },
        {
          "average_prediction": 9.288569288381373,
          "feature_value": 123.69090909090906
        },
        {
          "average_prediction": 9.290363994853198,
          "feature_value": 141.2181818181818
        },
        {
          "average_prediction": 9.290363994853198,
          "feature_value": 158.74545454545452
        },
        {
          "average_prediction": 9.12358661621567,
          "feature_value": 176.27272727272725
        },
        {
          "average_prediction": 8.993551430646988,
          "feature_value": 193.79999999999995
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
          "average_prediction": 7.998086653071238,
          "feature_value": 0.49999999999999994
        },
        {
          "average_prediction": 7.861899649567182,
          "feature_value": 33.61836363636363
        },
        {
          "average_prediction": 8.232157548946793,
          "feature_value": 66.73672727272726
        },
        {
          "average_prediction": 8.18605270039207,
          "feature_value": 99.8550909090909
        },
        {
          "average_prediction": 12.4488919163934,
          "feature_value": 132.97345454545453
        },
        {
          "average_prediction": 12.26344991305843,
          "feature_value": 166.09181818181816
        },
        {
          "average_prediction": 12.485269560994757,
          "feature_value": 199.2101818181818
        },
        {
          "average_prediction": 12.550902871485487,
          "feature_value": 232.32854545454543
        },
        {
          "average_prediction": 12.551246999486175,
          "feature_value": 265.44690909090906
        },
        {
          "average_prediction": 12.655903036070754,
          "feature_value": 298.5652727272727
        },
        {
          "average_prediction": 12.652992110106219,
          "feature_value": 331.6836363636363
        },
        {
          "average_prediction": 12.646353710199389,
          "feature_value": 364.80199999999996
        }
      ],
      "response_status": "stable_numeric_grid"
    },
    {
      "explanation_scope": "registered_final_artifact_descriptive_on_2025_training_rows",
      "feature": "weighted_3yr_interceptions_per_game",
      "interpretation": "This explanation is associative, not causal; changing a feature here does not establish that the feature causes the prediction to change.",
      "method": "one_way_average_partial_dependence",
      "points": [
        {
          "average_prediction": 11.783577142580938,
          "feature_value": 0.009375000000000003
        },
        {
          "average_prediction": 11.783577142580938,
          "feature_value": 0.09233058608058609
        },
        {
          "average_prediction": 11.656098189394811,
          "feature_value": 0.17528617216117215
        },
        {
          "average_prediction": 11.656098189394811,
          "feature_value": 0.25824175824175827
        },
        {
          "average_prediction": 9.691358410237031,
          "feature_value": 0.34119734432234433
        },
        {
          "average_prediction": 9.863560970798527,
          "feature_value": 0.4241529304029304
        },
        {
          "average_prediction": 9.612338359638242,
          "feature_value": 0.5071085164835165
        },
        {
          "average_prediction": 9.73576999307067,
          "feature_value": 0.5900641025641026
        },
        {
          "average_prediction": 9.657435674029516,
          "feature_value": 0.6730196886446886
        },
        {
          "average_prediction": 9.453446918406492,
          "feature_value": 0.7559752747252747
        },
        {
          "average_prediction": 9.319679329151159,
          "feature_value": 0.8389308608058608
        },
        {
          "average_prediction": 9.059518314143258,
          "feature_value": 0.9218864468864469
        }
      ],
      "response_status": "stable_numeric_grid"
    }
  ],
  "importance": [
    {
      "explanation_scope": "registered_final_artifact_descriptive_on_2025_training_rows",
      "feature": "lag1_fantasy_points_total",
      "importance_mean": 1.8914301898194392,
      "importance_std": 0.37636220410314103,
      "rank": 1
    },
    {
      "explanation_scope": "registered_final_artifact_descriptive_on_2025_training_rows",
      "feature": "draft_pick",
      "importance_mean": 0.6274866333587065,
      "importance_std": 0.09850813203451468,
      "rank": 2
    },
    {
      "explanation_scope": "registered_final_artifact_descriptive_on_2025_training_rows",
      "feature": "weighted_3yr_interceptions_per_game",
      "importance_mean": 0.6080552625555848,
      "importance_std": 0.09500244503474803,
      "rank": 3
    },
    {
      "explanation_scope": "registered_final_artifact_descriptive_on_2025_training_rows",
      "feature": "weighted_3yr_fantasy_points_per_game",
      "importance_mean": 0.5442452194481617,
      "importance_std": 0.06363248604562219,
      "rank": 4
    },
    {
      "explanation_scope": "registered_final_artifact_descriptive_on_2025_training_rows",
      "feature": "weighted_3yr_games_active",
      "importance_mean": 0.4715265714901289,
      "importance_std": 0.11755664456657092,
      "rank": 5
    },
    {
      "explanation_scope": "registered_final_artifact_descriptive_on_2025_training_rows",
      "feature": "weighted_3yr_carries_per_game",
      "importance_mean": 0.44346642379546086,
      "importance_std": 0.061380574393435736,
      "rank": 6
    },
    {
      "explanation_scope": "registered_final_artifact_descriptive_on_2025_training_rows",
      "feature": "weighted_3yr_rushing_yards_per_game",
      "importance_mean": 0.3508801832460568,
      "importance_std": 0.03815533243059281,
      "rank": 7
    },
    {
      "explanation_scope": "registered_final_artifact_descriptive_on_2025_training_rows",
      "feature": "lag1_fantasy_points_per_game",
      "importance_mean": 0.31227031234534514,
      "importance_std": 0.047779643361505156,
      "rank": 8
    },
    {
      "explanation_scope": "registered_final_artifact_descriptive_on_2025_training_rows",
      "feature": "weighted_3yr_passing_attempts_per_game",
      "importance_mean": 0.2979232435231155,
      "importance_std": 0.04315799804363811,
      "rank": 9
    },
    {
      "explanation_scope": "registered_final_artifact_descriptive_on_2025_training_rows",
      "feature": "weighted_3yr_passing_tds_per_game",
      "importance_mean": 0.25386035403504453,
      "importance_std": 0.03893268694763737,
      "rank": 10
    },
    {
      "explanation_scope": "registered_final_artifact_descriptive_on_2025_training_rows",
      "feature": "weighted_3yr_fumbles_lost_per_game",
      "importance_mean": 0.1990552035269845,
      "importance_std": 0.03408131318999951,
      "rank": 11
    },
    {
      "explanation_scope": "registered_final_artifact_descriptive_on_2025_training_rows",
      "feature": "age_at_cutoff",
      "importance_mean": 0.16005991476298828,
      "importance_std": 0.0644130249638276,
      "rank": 12
    },
    {
      "explanation_scope": "registered_final_artifact_descriptive_on_2025_training_rows",
      "feature": "weighted_3yr_receptions_per_game",
      "importance_mean": 0.14366000425683487,
      "importance_std": 0.025072810049110335,
      "rank": 13
    },
    {
      "explanation_scope": "registered_final_artifact_descriptive_on_2025_training_rows",
      "feature": "weighted_3yr_two_point_conversions_per_game",
      "importance_mean": 0.14241204258758838,
      "importance_std": 0.04628376041520469,
      "rank": 14
    },
    {
      "explanation_scope": "registered_final_artifact_descriptive_on_2025_training_rows",
      "feature": "weighted_3yr_receiving_yards_per_game",
      "importance_mean": 0.11444528333536694,
      "importance_std": 0.021975794759866194,
      "rank": 15
    },
    {
      "explanation_scope": "registered_final_artifact_descriptive_on_2025_training_rows",
      "feature": "weighted_3yr_passing_yards_per_game",
      "importance_mean": 0.11077588623650839,
      "importance_std": 0.010541151566852409,
      "rank": 16
    },
    {
      "explanation_scope": "registered_final_artifact_descriptive_on_2025_training_rows",
      "feature": "weighted_3yr_rushing_tds_per_game",
      "importance_mean": 0.10646345645941917,
      "importance_std": 0.053487524356628346,
      "rank": 17
    },
    {
      "explanation_scope": "registered_final_artifact_descriptive_on_2025_training_rows",
      "feature": "nfl_experience_years",
      "importance_mean": 0.05404628747316731,
      "importance_std": 0.011217483176429394,
      "rank": 18
    },
    {
      "explanation_scope": "registered_final_artifact_descriptive_on_2025_training_rows",
      "feature": "missing_draft_capital",
      "importance_mean": 0.036025936149606606,
      "importance_std": 0.024546626656001814,
      "rank": 19
    },
    {
      "explanation_scope": "registered_final_artifact_descriptive_on_2025_training_rows",
      "feature": "lag1_stat_games",
      "importance_mean": 0.03557235909667118,
      "importance_std": 0.012524744007174387,
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

- Project-relative path: `models/artifacts/phase4-7ae8e9aed04bffca00c0/attempt-866987f75a2c406693cf892d49adc975/QB/fantasy_points_per_game/hist_gradient_boosting.joblib`
- SHA-256: `56c53b99e49a9a24780ade4a8f7db2de6431f9c0c965affa5b5285b007be0486`

## Additional metadata

````json
{
  "publication_id": "attempt-866987f75a2c406693cf892d49adc975"
}
````
