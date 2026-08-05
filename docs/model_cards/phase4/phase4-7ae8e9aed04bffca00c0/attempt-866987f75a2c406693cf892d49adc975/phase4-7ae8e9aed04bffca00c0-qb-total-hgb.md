# Model Card: phase4-7ae8e9aed04bffca00c0-qb-total-hgb

- Model ID: `phase4-7ae8e9aed04bffca00c0-qb-total-hgb`
- Trained at: 2026-08-05T20:58:13+00:00
- Target: `fantasy_points_total`
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
  "target_name": "fantasy_points_total",
  "test_mae": 37.981587321083445,
  "test_rows": 124,
  "test_season": 2025,
  "validation_mae": 41.20860389333247,
  "validation_rows": 618,
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
    "candidate_mae": 41.20860389333247,
    "ci95_lower": -13.815049499312021,
    "ci95_upper": -6.3656732283432875,
    "direction": "candidate_lower_mae",
    "mae_difference_candidate_minus_reference": -10.130237681520477,
    "n_resamples": 2000,
    "reference_mae": 51.33884157485295,
    "rows": 618,
    "seed": 42
  },
  "decision_status": "learned_significant_improvement_selected",
  "learned_improvement_status": "statistically_clear",
  "reference_metrics": {
    "candidate_name": "age_position_adjusted",
    "candidate_source": "baseline",
    "position": "QB",
    "target_name": "fantasy_points_total",
    "test_mae": 51.38160378623023,
    "test_rows": 124,
    "test_season": 2025,
    "validation_mae": 51.33884157485295,
    "validation_rows": 618,
    "validation_seasons": [
      2020,
      2021,
      2022,
      2023,
      2024
    ]
  },
  "selected_champion": "hist_gradient_boosting",
  "selected_source": "learned",
  "selection_rule": "A learned candidate must lower pooled validation MAE and its paired bootstrap 95% interval for the MAE difference must remain below zero; otherwise the transparent baseline is retained.",
  "this_candidate_selected": true
}
````

## Uncertainty estimates

````json
{
  "empirical_metrics_by_season": [
    {
      "candidate_name": "hist_gradient_boosting",
      "empirical_coverage_p10_p90": 0.8145161290322581,
      "evaluation_scope": "test",
      "mean_interval_width_p10_p90": 142.59995626756736,
      "pinball_loss_p10": 10.35420870446644,
      "pinball_loss_p50": 18.990793660541723,
      "pinball_loss_p90": 14.223780182185326,
      "position": "QB",
      "prediction_season": 2025,
      "projection_tier": "all",
      "rows": 124,
      "target_name": "fantasy_points_total"
    },
    {
      "candidate_name": "hist_gradient_boosting",
      "empirical_coverage_p10_p90": 0.4838709677419355,
      "evaluation_scope": "test",
      "mean_interval_width_p10_p90": 142.5999562675673,
      "pinball_loss_p10": 21.613900906331505,
      "pinball_loss_p50": 44.42368476042442,
      "pinball_loss_p90": 26.22257445961321,
      "position": "QB",
      "prediction_season": 2025,
      "projection_tier": "top",
      "rows": 31,
      "target_name": "fantasy_points_total"
    },
    {
      "candidate_name": "hist_gradient_boosting",
      "empirical_coverage_p10_p90": 0.8870967741935484,
      "evaluation_scope": "test",
      "mean_interval_width_p10_p90": 142.59995626756736,
      "pinball_loss_p10": 6.53886285890623,
      "pinball_loss_p50": 14.672871615795865,
      "pinball_loss_p90": 11.568879418046581,
      "position": "QB",
      "prediction_season": 2025,
      "projection_tier": "middle",
      "rows": 62,
      "target_name": "fantasy_points_total"
    },
    {
      "candidate_name": "hist_gradient_boosting",
      "empirical_coverage_p10_p90": 1.0,
      "evaluation_scope": "test",
      "mean_interval_width_p10_p90": 142.5999562675673,
      "pinball_loss_p10": 6.7252081937218025,
      "pinball_loss_p50": 2.1937466501507417,
      "pinball_loss_p90": 7.534787433034929,
      "position": "QB",
      "prediction_season": 2025,
      "projection_tier": "lower",
      "rows": 31,
      "target_name": "fantasy_points_total"
    },
    {
      "candidate_name": "hist_gradient_boosting",
      "empirical_coverage_p10_p90": 0.8067226890756303,
      "evaluation_scope": "validation",
      "mean_interval_width_p10_p90": 148.18530549560077,
      "pinball_loss_p10": 10.965822995111008,
      "pinball_loss_p50": 20.29450758533938,
      "pinball_loss_p90": 14.15610703734929,
      "position": "QB",
      "prediction_season": 2020,
      "projection_tier": "all",
      "rows": 119,
      "target_name": "fantasy_points_total"
    },
    {
      "candidate_name": "hist_gradient_boosting",
      "empirical_coverage_p10_p90": 0.5,
      "evaluation_scope": "validation",
      "mean_interval_width_p10_p90": 148.1853054956008,
      "pinball_loss_p10": 21.421823613305886,
      "pinball_loss_p50": 42.25619933542571,
      "pinball_loss_p90": 19.817174569922443,
      "position": "QB",
      "prediction_season": 2020,
      "projection_tier": "top",
      "rows": 30,
      "target_name": "fantasy_points_total"
    },
    {
      "candidate_name": "hist_gradient_boosting",
      "empirical_coverage_p10_p90": 0.864406779661017,
      "evaluation_scope": "validation",
      "mean_interval_width_p10_p90": 148.1853054956008,
      "pinball_loss_p10": 7.317986514789199,
      "pinball_loss_p50": 16.796797078323383,
      "pinball_loss_p90": 14.847840805195945,
      "position": "QB",
      "prediction_season": 2020,
      "projection_tier": "middle",
      "rows": 59,
      "target_name": "fantasy_points_total"
    },
    {
      "candidate_name": "hist_gradient_boosting",
      "empirical_coverage_p10_p90": 1.0,
      "evaluation_scope": "validation",
      "mean_interval_width_p10_p90": 148.1853054956008,
      "pinball_loss_p10": 7.683900788215687,
      "pinball_loss_p50": 5.211646499051168,
      "pinball_loss_p90": 7.134629761344389,
      "position": "QB",
      "prediction_season": 2020,
      "projection_tier": "lower",
      "rows": 30,
      "target_name": "fantasy_points_total"
    },
    {
      "candidate_name": "hist_gradient_boosting",
      "empirical_coverage_p10_p90": 0.832,
      "evaluation_scope": "validation",
      "mean_interval_width_p10_p90": 151.56234396447454,
      "pinball_loss_p10": 14.993155929093067,
      "pinball_loss_p50": 20.88749319969211,
      "pinball_loss_p90": 13.192739973363526,
      "position": "QB",
      "prediction_season": 2021,
      "projection_tier": "all",
      "rows": 125,
      "target_name": "fantasy_points_total"
    },
    {
      "candidate_name": "hist_gradient_boosting",
      "empirical_coverage_p10_p90": 0.5161290322580645,
      "evaluation_scope": "validation",
      "mean_interval_width_p10_p90": 151.5623439644745,
      "pinball_loss_p10": 40.147884073940546,
      "pinball_loss_p50": 48.882256930946916,
      "pinball_loss_p90": 16.465624753608513,
      "position": "QB",
      "prediction_season": 2021,
      "projection_tier": "top",
      "rows": 31,
      "target_name": "fantasy_points_total"
    },
    {
      "candidate_name": "hist_gradient_boosting",
      "empirical_coverage_p10_p90": 0.9047619047619048,
      "evaluation_scope": "validation",
      "mean_interval_width_p10_p90": 151.56234396447462,
      "pinball_loss_p10": 6.553766848430869,
      "pinball_loss_p50": 14.869343500175715,
      "pinball_loss_p90": 14.055359308127578,
      "position": "QB",
      "prediction_season": 2021,
      "projection_tier": "middle",
      "rows": 63,
      "target_name": "fantasy_points_total"
    },
    {
      "candidate_name": "hist_gradient_boosting",
      "empirical_coverage_p10_p90": 1.0,
      "evaluation_scope": "validation",
      "mean_interval_width_p10_p90": 151.5623439644745,
      "pinball_loss_p10": 6.9894443030106945,
      "pinball_loss_p50": 5.123162728744805,
      "pinball_loss_p90": 8.16679009343676,
      "position": "QB",
      "prediction_season": 2021,
      "projection_tier": "lower",
      "rows": 31,
      "target_name": "fantasy_points_total"
    },
    {
      "candidate_name": "hist_gradient_boosting",
      "empirical_coverage_p10_p90": 0.808,
      "evaluation_scope": "validation",
      "mean_interval_width_p10_p90": 141.82268761563896,
      "pinball_loss_p10": 9.918436859810164,
      "pinball_loss_p50": 18.379053811107365,
      "pinball_loss_p90": 14.468838261744686,
      "position": "QB",
      "prediction_season": 2022,
      "projection_tier": "all",
      "rows": 125,
      "target_name": "fantasy_points_total"
    },
    {
      "candidate_name": "hist_gradient_boosting",
      "empirical_coverage_p10_p90": 0.45161290322580644,
      "evaluation_scope": "validation",
      "mean_interval_width_p10_p90": 141.8226876156389,
      "pinball_loss_p10": 19.98207839158738,
      "pinball_loss_p50": 39.51037488867895,
      "pinball_loss_p90": 21.906010126752697,
      "position": "QB",
      "prediction_season": 2022,
      "projection_tier": "top",
      "rows": 31,
      "target_name": "fantasy_points_total"
    },
    {
      "candidate_name": "hist_gradient_boosting",
      "empirical_coverage_p10_p90": 0.9047619047619048,
      "evaluation_scope": "validation",
      "mean_interval_width_p10_p90": 141.82268761563884,
      "pinball_loss_p10": 6.1857341193382736,
      "pinball_loss_p50": 13.71161883156984,
      "pinball_loss_p90": 13.158203396287679,
      "position": "QB",
      "prediction_season": 2022,
      "projection_tier": "middle",
      "rows": 63,
      "target_name": "fantasy_points_total"
    },
    {
      "candidate_name": "hist_gradient_boosting",
      "empirical_coverage_p10_p90": 0.967741935483871,
      "evaluation_scope": "validation",
      "mean_interval_width_p10_p90": 141.8226876156389,
      "pinball_loss_p10": 7.440610574798402,
      "pinball_loss_p50": 6.733165111305594,
      "pinball_loss_p90": 9.695214671697673,
      "position": "QB",
      "prediction_season": 2022,
      "projection_tier": "lower",
      "rows": 31,
      "target_name": "fantasy_points_total"
    },
    {
      "candidate_name": "hist_gradient_boosting",
      "empirical_coverage_p10_p90": 0.7258064516129032,
      "evaluation_scope": "validation",
      "mean_interval_width_p10_p90": 135.10494029216628,
      "pinball_loss_p10": 14.948839863064242,
      "pinball_loss_p50": 24.614452531331533,
      "pinball_loss_p90": 16.757869822298993,
      "position": "QB",
      "prediction_season": 2023,
      "projection_tier": "all",
      "rows": 124,
      "target_name": "fantasy_points_total"
    },
    {
      "candidate_name": "hist_gradient_boosting",
      "empirical_coverage_p10_p90": 0.1935483870967742,
      "evaluation_scope": "validation",
      "mean_interval_width_p10_p90": 135.10494029216625,
      "pinball_loss_p10": 38.781335442295486,
      "pinball_loss_p50": 54.91706262141587,
      "pinball_loss_p90": 26.656494121910907,
      "position": "QB",
      "prediction_season": 2023,
      "projection_tier": "top",
      "rows": 31,
      "target_name": "fantasy_points_total"
    },
    {
      "candidate_name": "hist_gradient_boosting",
      "empirical_coverage_p10_p90": 0.8870967741935484,
      "evaluation_scope": "validation",
      "mean_interval_width_p10_p90": 135.10494029216628,
      "pinball_loss_p10": 6.839901864521173,
      "pinball_loss_p50": 16.73400379148954,
      "pinball_loss_p90": 13.156895374377953,
      "position": "QB",
      "prediction_season": 2023,
      "projection_tier": "middle",
      "rows": 62,
      "target_name": "fantasy_points_total"
    },
    {
      "candidate_name": "hist_gradient_boosting",
      "empirical_coverage_p10_p90": 0.9354838709677419,
      "evaluation_scope": "validation",
      "mean_interval_width_p10_p90": 135.10494029216628,
      "pinball_loss_p10": 7.334220280919144,
      "pinball_loss_p50": 10.07273992093119,
      "pinball_loss_p90": 14.06119441852916,
      "position": "QB",
      "prediction_season": 2023,
      "projection_tier": "lower",
      "rows": 31,
      "target_name": "fantasy_points_total"
    },
    {
      "candidate_name": "hist_gradient_boosting",
      "empirical_coverage_p10_p90": 0.808,
      "evaluation_scope": "validation",
      "mean_interval_width_p10_p90": 145.48009736166634,
      "pinball_loss_p10": 10.797547774024572,
      "pinball_loss_p50": 18.86321368119443,
      "pinball_loss_p90": 13.885873054763756,
      "position": "QB",
      "prediction_season": 2024,
      "projection_tier": "all",
      "rows": 125,
      "target_name": "fantasy_points_total"
    },
    {
      "candidate_name": "hist_gradient_boosting",
      "empirical_coverage_p10_p90": 0.5161290322580645,
      "evaluation_scope": "validation",
      "mean_interval_width_p10_p90": 145.48009736166634,
      "pinball_loss_p10": 22.91737663373756,
      "pinball_loss_p50": 41.32026784121866,
      "pinball_loss_p90": 23.083564210201484,
      "position": "QB",
      "prediction_season": 2024,
      "projection_tier": "top",
      "rows": 31,
      "target_name": "fantasy_points_total"
    },
    {
      "candidate_name": "hist_gradient_boosting",
      "empirical_coverage_p10_p90": 0.8571428571428571,
      "evaluation_scope": "validation",
      "mean_interval_width_p10_p90": 145.48009736166628,
      "pinball_loss_p10": 6.877227485556096,
      "pinball_loss_p50": 15.997305523493992,
      "pinball_loss_p90": 12.303885778178286,
      "position": "QB",
      "prediction_season": 2024,
      "projection_tier": "middle",
      "rows": 63,
      "target_name": "fantasy_points_total"
    },
    {
      "candidate_name": "hist_gradient_boosting",
      "empirical_coverage_p10_p90": 1.0,
      "evaluation_scope": "validation",
      "mean_interval_width_p10_p90": 145.48009736166634,
      "pinball_loss_p10": 6.644821436037855,
      "pinball_loss_p50": 2.2304244868194796,
      "pinball_loss_p90": 7.903188300128778,
      "position": "QB",
      "prediction_season": 2024,
      "projection_tier": "lower",
      "rows": 31,
      "target_name": "fantasy_points_total"
    }
  ],
  "empirical_not_guaranteed": true,
  "method": "training-only signed out-of-fold residual quantiles",
  "operational_center": "training_only_residual_adjusted_p50",
  "residual_rows": 373,
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
          "average_prediction": 74.73039583671887,
          "feature_value": 1.0
        },
        {
          "average_prediction": 68.58264449074657,
          "feature_value": 22.504545454545443
        },
        {
          "average_prediction": 62.64599102362986,
          "feature_value": 44.00909090909089
        },
        {
          "average_prediction": 59.05721869648412,
          "feature_value": 65.51363636363632
        },
        {
          "average_prediction": 58.30329247284409,
          "feature_value": 87.01818181818177
        },
        {
          "average_prediction": 56.224408991253945,
          "feature_value": 108.52272727272722
        },
        {
          "average_prediction": 56.224408991253945,
          "feature_value": 130.02727272727265
        },
        {
          "average_prediction": 56.224408991253945,
          "feature_value": 151.5318181818181
        },
        {
          "average_prediction": 56.224408991253945,
          "feature_value": 173.03636363636355
        },
        {
          "average_prediction": 56.224408991253945,
          "feature_value": 194.540909090909
        },
        {
          "average_prediction": 56.224408991253945,
          "feature_value": 216.04545454545445
        },
        {
          "average_prediction": 56.224408991253945,
          "feature_value": 237.54999999999987
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
          "average_prediction": 37.54960468392537,
          "feature_value": -0.2
        },
        {
          "average_prediction": 37.853717379544086,
          "feature_value": 32.25618181818181
        },
        {
          "average_prediction": 37.53680532558526,
          "feature_value": 64.71236363636362
        },
        {
          "average_prediction": 52.154801544459744,
          "feature_value": 97.16854545454542
        },
        {
          "average_prediction": 92.8584173800215,
          "feature_value": 129.62472727272726
        },
        {
          "average_prediction": 91.19348712831922,
          "feature_value": 162.08090909090907
        },
        {
          "average_prediction": 91.34181803207537,
          "feature_value": 194.53709090909086
        },
        {
          "average_prediction": 122.21805389979825,
          "feature_value": 226.99327272727268
        },
        {
          "average_prediction": 123.9244931968183,
          "feature_value": 259.4494545454545
        },
        {
          "average_prediction": 124.93059448736028,
          "feature_value": 291.9056363636363
        },
        {
          "average_prediction": 123.98180675242801,
          "feature_value": 324.36181818181814
        },
        {
          "average_prediction": 122.12292146430883,
          "feature_value": 356.8179999999999
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
          "average_prediction": 58.503631833022595,
          "feature_value": 0.14507142857142857
        },
        {
          "average_prediction": 58.503631833022595,
          "feature_value": 1.9024524417494266
        },
        {
          "average_prediction": 58.6705818925024,
          "feature_value": 3.659833454927425
        },
        {
          "average_prediction": 59.05690933253836,
          "feature_value": 5.417214468105423
        },
        {
          "average_prediction": 62.79570017643536,
          "feature_value": 7.174595481283421
        },
        {
          "average_prediction": 72.2534149174565,
          "feature_value": 8.93197649446142
        },
        {
          "average_prediction": 73.93517482033661,
          "feature_value": 10.689357507639418
        },
        {
          "average_prediction": 74.85588353245959,
          "feature_value": 12.446738520817416
        },
        {
          "average_prediction": 74.29468012444055,
          "feature_value": 14.204119533995414
        },
        {
          "average_prediction": 68.87802585269003,
          "feature_value": 15.961500547173411
        },
        {
          "average_prediction": 76.96790638105593,
          "feature_value": 17.71888156035141
        },
        {
          "average_prediction": 79.59526741293008,
          "feature_value": 19.476262573529407
        }
      ],
      "response_status": "stable_numeric_grid"
    }
  ],
  "importance": [
    {
      "explanation_scope": "registered_final_artifact_descriptive_on_2025_training_rows",
      "feature": "lag1_fantasy_points_total",
      "importance_mean": 25.223684876548297,
      "importance_std": 3.5412620549860545,
      "rank": 1
    },
    {
      "explanation_scope": "registered_final_artifact_descriptive_on_2025_training_rows",
      "feature": "weighted_3yr_fantasy_points_per_game",
      "importance_mean": 5.825671937924656,
      "importance_std": 0.5359644086178136,
      "rank": 2
    },
    {
      "explanation_scope": "registered_final_artifact_descriptive_on_2025_training_rows",
      "feature": "draft_pick",
      "importance_mean": 5.569109277470888,
      "importance_std": 1.1264524667331903,
      "rank": 3
    },
    {
      "explanation_scope": "registered_final_artifact_descriptive_on_2025_training_rows",
      "feature": "weighted_3yr_games_active",
      "importance_mean": 4.9262762136635745,
      "importance_std": 1.1012668745290872,
      "rank": 4
    },
    {
      "explanation_scope": "registered_final_artifact_descriptive_on_2025_training_rows",
      "feature": "age_at_cutoff",
      "importance_mean": 4.386422843793712,
      "importance_std": 0.41449116344775744,
      "rank": 5
    },
    {
      "explanation_scope": "registered_final_artifact_descriptive_on_2025_training_rows",
      "feature": "weighted_3yr_interceptions_per_game",
      "importance_mean": 3.7761914430351773,
      "importance_std": 1.1105224136837535,
      "rank": 6
    },
    {
      "explanation_scope": "registered_final_artifact_descriptive_on_2025_training_rows",
      "feature": "weighted_3yr_two_point_conversions_per_game",
      "importance_mean": 3.732041832762441,
      "importance_std": 0.4309341958267238,
      "rank": 7
    },
    {
      "explanation_scope": "registered_final_artifact_descriptive_on_2025_training_rows",
      "feature": "weighted_3yr_passing_yards_per_game",
      "importance_mean": 3.243870844643623,
      "importance_std": 0.5792970873986,
      "rank": 8
    },
    {
      "explanation_scope": "registered_final_artifact_descriptive_on_2025_training_rows",
      "feature": "lag1_fantasy_points_per_game",
      "importance_mean": 3.1849664924960015,
      "importance_std": 0.5365506455432834,
      "rank": 9
    },
    {
      "explanation_scope": "registered_final_artifact_descriptive_on_2025_training_rows",
      "feature": "weighted_3yr_passing_tds_per_game",
      "importance_mean": 3.007256184874791,
      "importance_std": 0.42349484559747963,
      "rank": 10
    },
    {
      "explanation_scope": "registered_final_artifact_descriptive_on_2025_training_rows",
      "feature": "weighted_3yr_passing_attempts_per_game",
      "importance_mean": 2.737618905989379,
      "importance_std": 0.6121057304395017,
      "rank": 11
    },
    {
      "explanation_scope": "registered_final_artifact_descriptive_on_2025_training_rows",
      "feature": "lag1_stat_games",
      "importance_mean": 1.8950477044043943,
      "importance_std": 0.30958586956663325,
      "rank": 12
    },
    {
      "explanation_scope": "registered_final_artifact_descriptive_on_2025_training_rows",
      "feature": "nfl_experience_years",
      "importance_mean": 1.8314277434539386,
      "importance_std": 0.48362619313273775,
      "rank": 13
    },
    {
      "explanation_scope": "registered_final_artifact_descriptive_on_2025_training_rows",
      "feature": "weighted_3yr_rushing_tds_per_game",
      "importance_mean": 1.7363267370951754,
      "importance_std": 0.3506703248448419,
      "rank": 14
    },
    {
      "explanation_scope": "registered_final_artifact_descriptive_on_2025_training_rows",
      "feature": "missing_lag1",
      "importance_mean": 1.5472462889436058,
      "importance_std": 0.3441548264475563,
      "rank": 15
    },
    {
      "explanation_scope": "registered_final_artifact_descriptive_on_2025_training_rows",
      "feature": "weighted_3yr_fumbles_lost_per_game",
      "importance_mean": 1.5215536732162263,
      "importance_std": 0.25572432745576784,
      "rank": 16
    },
    {
      "explanation_scope": "registered_final_artifact_descriptive_on_2025_training_rows",
      "feature": "weighted_3yr_rushing_yards_per_game",
      "importance_mean": 1.141271544066526,
      "importance_std": 0.4050079597123555,
      "rank": 17
    },
    {
      "explanation_scope": "registered_final_artifact_descriptive_on_2025_training_rows",
      "feature": "previous_team",
      "importance_mean": 0.855060599099648,
      "importance_std": 0.15586392528088006,
      "rank": 18
    },
    {
      "explanation_scope": "registered_final_artifact_descriptive_on_2025_training_rows",
      "feature": "weighted_3yr_receiving_yards_per_game",
      "importance_mean": 0.7913464237929972,
      "importance_std": 0.26800304117927565,
      "rank": 19
    },
    {
      "explanation_scope": "registered_final_artifact_descriptive_on_2025_training_rows",
      "feature": "weighted_3yr_carries_per_game",
      "importance_mean": 0.7681068746453782,
      "importance_std": 0.1290407178443246,
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

- Project-relative path: `models/artifacts/phase4-7ae8e9aed04bffca00c0/attempt-866987f75a2c406693cf892d49adc975/QB/fantasy_points_total/hist_gradient_boosting.joblib`
- SHA-256: `4a7cd77bffc46de7956141c318b61b8e368f432edb39bbc35f74002a94fac8fc`

## Additional metadata

````json
{
  "publication_id": "attempt-866987f75a2c406693cf892d49adc975"
}
````
