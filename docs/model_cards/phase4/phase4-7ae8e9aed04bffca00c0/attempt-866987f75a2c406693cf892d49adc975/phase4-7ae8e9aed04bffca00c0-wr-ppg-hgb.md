# Model Card: phase4-7ae8e9aed04bffca00c0-wr-ppg-hgb

- Model ID: `phase4-7ae8e9aed04bffca00c0-wr-ppg-hgb`
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
  "position": "WR",
  "target_name": "fantasy_points_per_game",
  "test_mae": 2.1200974110419506,
  "test_rows": 198,
  "test_season": 2025,
  "validation_mae": 2.367930773726267,
  "validation_rows": 989,
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
    "candidate_mae": 2.367930773726267,
    "ci95_lower": -0.23545425147664406,
    "ci95_upper": -0.053987650009293967,
    "direction": "candidate_lower_mae",
    "mae_difference_candidate_minus_reference": -0.14159018367520027,
    "n_resamples": 2000,
    "reference_mae": 2.509520957401467,
    "rows": 989,
    "seed": 42
  },
  "decision_status": "learned_significant_improvement_selected",
  "learned_improvement_status": "statistically_clear",
  "reference_metrics": {
    "candidate_name": "age_position_adjusted",
    "candidate_source": "baseline",
    "position": "WR",
    "target_name": "fantasy_points_per_game",
    "test_mae": 2.2565557188552456,
    "test_rows": 198,
    "test_season": 2025,
    "validation_mae": 2.509520957401467,
    "validation_rows": 989,
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
      "empirical_coverage_p10_p90": 0.8383838383838383,
      "evaluation_scope": "test",
      "mean_interval_width_p10_p90": 7.765283374010036,
      "pinball_loss_p10": 0.4881681151225607,
      "pinball_loss_p50": 1.0600487055209753,
      "pinball_loss_p90": 0.5106079697801522,
      "position": "WR",
      "prediction_season": 2025,
      "projection_tier": "all",
      "rows": 198,
      "target_name": "fantasy_points_per_game"
    },
    {
      "candidate_name": "hist_gradient_boosting",
      "empirical_coverage_p10_p90": 0.6813186813186813,
      "evaluation_scope": "test",
      "mean_interval_width_p10_p90": 7.7652833740100355,
      "pinball_loss_p10": 0.5864735647514625,
      "pinball_loss_p50": 1.4421485300422603,
      "pinball_loss_p90": 0.6625994767650181,
      "position": "WR",
      "prediction_season": 2025,
      "projection_tier": "top",
      "rows": 91,
      "target_name": "fantasy_points_per_game"
    },
    {
      "candidate_name": "hist_gradient_boosting",
      "empirical_coverage_p10_p90": 0.9571428571428572,
      "evaluation_scope": "test",
      "mean_interval_width_p10_p90": 7.765283374010035,
      "pinball_loss_p10": 0.3919295284608281,
      "pinball_loss_p50": 0.80538615211327,
      "pinball_loss_p90": 0.39893432223774755,
      "position": "WR",
      "prediction_season": 2025,
      "projection_tier": "middle",
      "rows": 70,
      "target_name": "fantasy_points_per_game"
    },
    {
      "candidate_name": "hist_gradient_boosting",
      "empirical_coverage_p10_p90": 1.0,
      "evaluation_scope": "test",
      "mean_interval_width_p10_p90": 7.765283374010037,
      "pinball_loss_p10": 0.42846284890881015,
      "pinball_loss_p50": 0.602083697604825,
      "pinball_loss_p90": 0.3480654884921935,
      "position": "WR",
      "prediction_season": 2025,
      "projection_tier": "lower",
      "rows": 37,
      "target_name": "fantasy_points_per_game"
    },
    {
      "candidate_name": "hist_gradient_boosting",
      "empirical_coverage_p10_p90": 0.8385416666666666,
      "evaluation_scope": "validation",
      "mean_interval_width_p10_p90": 9.101960343013152,
      "pinball_loss_p10": 0.5303764009475659,
      "pinball_loss_p50": 1.2348416397626099,
      "pinball_loss_p90": 0.6147212576845338,
      "position": "WR",
      "prediction_season": 2020,
      "projection_tier": "all",
      "rows": 192,
      "target_name": "fantasy_points_per_game"
    },
    {
      "candidate_name": "hist_gradient_boosting",
      "empirical_coverage_p10_p90": 0.7608695652173914,
      "evaluation_scope": "validation",
      "mean_interval_width_p10_p90": 9.10196034301315,
      "pinball_loss_p10": 0.6336705059185699,
      "pinball_loss_p50": 1.478702051363993,
      "pinball_loss_p90": 0.6545318359651935,
      "position": "WR",
      "prediction_season": 2020,
      "projection_tier": "top",
      "rows": 92,
      "target_name": "fantasy_points_per_game"
    },
    {
      "candidate_name": "hist_gradient_boosting",
      "empirical_coverage_p10_p90": 0.8857142857142857,
      "evaluation_scope": "validation",
      "mean_interval_width_p10_p90": 9.101960343013152,
      "pinball_loss_p10": 0.41830041831719744,
      "pinball_loss_p50": 1.104850118841381,
      "pinball_loss_p90": 0.6058948644753721,
      "position": "WR",
      "prediction_season": 2020,
      "projection_tier": "middle",
      "rows": 70,
      "target_name": "fantasy_points_per_game"
    },
    {
      "candidate_name": "hist_gradient_boosting",
      "empirical_coverage_p10_p90": 0.9666666666666667,
      "evaluation_scope": "validation",
      "mean_interval_width_p10_p90": 9.101960343013154,
      "pinball_loss_p10": 0.4751184385073468,
      "pinball_loss_p50": 0.7903165930012369,
      "pinball_loss_p90": 0.5132304017785544,
      "position": "WR",
      "prediction_season": 2020,
      "projection_tier": "lower",
      "rows": 30,
      "target_name": "fantasy_points_per_game"
    },
    {
      "candidate_name": "hist_gradient_boosting",
      "empirical_coverage_p10_p90": 0.8349056603773585,
      "evaluation_scope": "validation",
      "mean_interval_width_p10_p90": 8.666003481919804,
      "pinball_loss_p10": 0.5628054824837168,
      "pinball_loss_p50": 1.1963031060204703,
      "pinball_loss_p90": 0.6583415038312003,
      "position": "WR",
      "prediction_season": 2021,
      "projection_tier": "all",
      "rows": 212,
      "target_name": "fantasy_points_per_game"
    },
    {
      "candidate_name": "hist_gradient_boosting",
      "empirical_coverage_p10_p90": 0.7640449438202247,
      "evaluation_scope": "validation",
      "mean_interval_width_p10_p90": 8.666003481919804,
      "pinball_loss_p10": 0.7629786597896617,
      "pinball_loss_p50": 1.4348560135817083,
      "pinball_loss_p90": 0.7365719438537837,
      "position": "WR",
      "prediction_season": 2021,
      "projection_tier": "top",
      "rows": 89,
      "target_name": "fantasy_points_per_game"
    },
    {
      "candidate_name": "hist_gradient_boosting",
      "empirical_coverage_p10_p90": 0.8804347826086957,
      "evaluation_scope": "validation",
      "mean_interval_width_p10_p90": 8.666003481919804,
      "pinball_loss_p10": 0.3919924935385896,
      "pinball_loss_p50": 1.0596423498603778,
      "pinball_loss_p90": 0.6159378252188661,
      "position": "WR",
      "prediction_season": 2021,
      "projection_tier": "middle",
      "rows": 92,
      "target_name": "fantasy_points_per_game"
    },
    {
      "candidate_name": "hist_gradient_boosting",
      "empirical_coverage_p10_p90": 0.9032258064516129,
      "evaluation_scope": "validation",
      "mean_interval_width_p10_p90": 8.666003481919805,
      "pinball_loss_p10": 0.49504361805541364,
      "pinball_loss_p50": 0.9169992606584794,
      "pinball_loss_p90": 0.5595876093255508,
      "position": "WR",
      "prediction_season": 2021,
      "projection_tier": "lower",
      "rows": 31,
      "target_name": "fantasy_points_per_game"
    },
    {
      "candidate_name": "hist_gradient_boosting",
      "empirical_coverage_p10_p90": 0.81,
      "evaluation_scope": "validation",
      "mean_interval_width_p10_p90": 8.262177203232978,
      "pinball_loss_p10": 0.5117184643669951,
      "pinball_loss_p50": 1.1874983692951517,
      "pinball_loss_p90": 0.5874572252513498,
      "position": "WR",
      "prediction_season": 2022,
      "projection_tier": "all",
      "rows": 200,
      "target_name": "fantasy_points_per_game"
    },
    {
      "candidate_name": "hist_gradient_boosting",
      "empirical_coverage_p10_p90": 0.7368421052631579,
      "evaluation_scope": "validation",
      "mean_interval_width_p10_p90": 8.262177203232982,
      "pinball_loss_p10": 0.6045594371992425,
      "pinball_loss_p50": 1.422315719552126,
      "pinball_loss_p90": 0.5793603295765608,
      "position": "WR",
      "prediction_season": 2022,
      "projection_tier": "top",
      "rows": 95,
      "target_name": "fantasy_points_per_game"
    },
    {
      "candidate_name": "hist_gradient_boosting",
      "empirical_coverage_p10_p90": 0.8607594936708861,
      "evaluation_scope": "validation",
      "mean_interval_width_p10_p90": 8.262177203232982,
      "pinball_loss_p10": 0.4219933016022386,
      "pinball_loss_p50": 1.0827979696452623,
      "pinball_loss_p90": 0.6008119853032148,
      "position": "WR",
      "prediction_season": 2022,
      "projection_tier": "middle",
      "rows": 79,
      "target_name": "fantasy_points_per_game"
    },
    {
      "candidate_name": "hist_gradient_boosting",
      "empirical_coverage_p10_p90": 0.9230769230769231,
      "evaluation_scope": "validation",
      "mean_interval_width_p10_p90": 8.262177203232977,
      "pinball_loss_p10": 0.44511828895746663,
      "pinball_loss_p50": 0.6476400346000989,
      "pinball_loss_p90": 0.5764641115977965,
      "position": "WR",
      "prediction_season": 2022,
      "projection_tier": "lower",
      "rows": 26,
      "target_name": "fantasy_points_per_game"
    },
    {
      "candidate_name": "hist_gradient_boosting",
      "empirical_coverage_p10_p90": 0.8429319371727748,
      "evaluation_scope": "validation",
      "mean_interval_width_p10_p90": 8.060949837947067,
      "pinball_loss_p10": 0.46041314695285224,
      "pinball_loss_p50": 1.061566625401432,
      "pinball_loss_p90": 0.6098186018726233,
      "position": "WR",
      "prediction_season": 2023,
      "projection_tier": "all",
      "rows": 191,
      "target_name": "fantasy_points_per_game"
    },
    {
      "candidate_name": "hist_gradient_boosting",
      "empirical_coverage_p10_p90": 0.7422680412371134,
      "evaluation_scope": "validation",
      "mean_interval_width_p10_p90": 8.060949837947069,
      "pinball_loss_p10": 0.5906447145528793,
      "pinball_loss_p50": 1.3823182944146082,
      "pinball_loss_p90": 0.6676150130665607,
      "position": "WR",
      "prediction_season": 2023,
      "projection_tier": "top",
      "rows": 97,
      "target_name": "fantasy_points_per_game"
    },
    {
      "candidate_name": "hist_gradient_boosting",
      "empirical_coverage_p10_p90": 0.9428571428571428,
      "evaluation_scope": "validation",
      "mean_interval_width_p10_p90": 8.060949837947069,
      "pinball_loss_p10": 0.31706132135655324,
      "pinball_loss_p50": 0.8131299054278006,
      "pinball_loss_p90": 0.5703965228312403,
      "position": "WR",
      "prediction_season": 2023,
      "projection_tier": "middle",
      "rows": 70,
      "target_name": "fantasy_points_per_game"
    },
    {
      "candidate_name": "hist_gradient_boosting",
      "empirical_coverage_p10_p90": 0.9583333333333334,
      "evaluation_scope": "validation",
      "mean_interval_width_p10_p90": 8.060949837947069,
      "pinball_loss_p10": 0.35217005255861494,
      "pinball_loss_p50": 0.48980239639626905,
      "pinball_loss_p90": 0.49120583716782723,
      "position": "WR",
      "prediction_season": 2023,
      "projection_tier": "lower",
      "rows": 24,
      "target_name": "fantasy_points_per_game"
    },
    {
      "candidate_name": "hist_gradient_boosting",
      "empirical_coverage_p10_p90": 0.7525773195876289,
      "evaluation_scope": "validation",
      "mean_interval_width_p10_p90": 7.492373282087854,
      "pinball_loss_p10": 0.501773752029542,
      "pinball_loss_p50": 1.2369949226091461,
      "pinball_loss_p90": 0.67347791886914,
      "position": "WR",
      "prediction_season": 2024,
      "projection_tier": "all",
      "rows": 194,
      "target_name": "fantasy_points_per_game"
    },
    {
      "candidate_name": "hist_gradient_boosting",
      "empirical_coverage_p10_p90": 0.6421052631578947,
      "evaluation_scope": "validation",
      "mean_interval_width_p10_p90": 7.492373282087856,
      "pinball_loss_p10": 0.5568251555311294,
      "pinball_loss_p50": 1.5176054765747835,
      "pinball_loss_p90": 0.7260863414161333,
      "position": "WR",
      "prediction_season": 2024,
      "projection_tier": "top",
      "rows": 95,
      "target_name": "fantasy_points_per_game"
    },
    {
      "candidate_name": "hist_gradient_boosting",
      "empirical_coverage_p10_p90": 0.8289473684210527,
      "evaluation_scope": "validation",
      "mean_interval_width_p10_p90": 7.492373282087855,
      "pinball_loss_p10": 0.445795548300053,
      "pinball_loss_p50": 1.0252328419435388,
      "pinball_loss_p90": 0.6255422534289365,
      "position": "WR",
      "prediction_season": 2024,
      "projection_tier": "middle",
      "rows": 76,
      "target_name": "fantasy_points_per_game"
    },
    {
      "candidate_name": "hist_gradient_boosting",
      "empirical_coverage_p10_p90": 0.9565217391304348,
      "evaluation_scope": "validation",
      "mean_interval_width_p10_p90": 7.49237328208785,
      "pinball_loss_p10": 0.4593589759769488,
      "pinball_loss_p50": 0.7776869010374324,
      "pinball_loss_p90": 0.6145783724122308,
      "position": "WR",
      "prediction_season": 2024,
      "projection_tier": "lower",
      "rows": 23,
      "target_name": "fantasy_points_per_game"
    }
  ],
  "empirical_not_guaranteed": true,
  "method": "training-only signed out-of-fold residual quantiles",
  "operational_center": "training_only_residual_adjusted_p50",
  "residual_rows": 583,
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
      "feature": "age_at_cutoff",
      "interpretation": "This explanation is associative, not causal; changing a feature here does not establish that the feature causes the prediction to change.",
      "method": "one_way_average_partial_dependence",
      "points": [
        {
          "average_prediction": 6.912346831940021,
          "feature_value": 23.45
        },
        {
          "average_prediction": 6.1415189852939,
          "feature_value": 24.232545454545452
        },
        {
          "average_prediction": 6.072869978147956,
          "feature_value": 25.015090909090908
        },
        {
          "average_prediction": 5.952409182447582,
          "feature_value": 25.79763636363636
        },
        {
          "average_prediction": 5.6150439798457255,
          "feature_value": 26.580181818181813
        },
        {
          "average_prediction": 5.514182587735881,
          "feature_value": 27.36272727272727
        },
        {
          "average_prediction": 5.068622090210181,
          "feature_value": 28.145272727272722
        },
        {
          "average_prediction": 5.033632906047727,
          "feature_value": 28.927818181818175
        },
        {
          "average_prediction": 4.910013289578419,
          "feature_value": 29.71036363636363
        },
        {
          "average_prediction": 4.577585248233657,
          "feature_value": 30.492909090909087
        },
        {
          "average_prediction": 4.698186296139247,
          "feature_value": 31.27545454545454
        },
        {
          "average_prediction": 4.381428265083833,
          "feature_value": 32.05799999999999
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
          "average_prediction": 4.880465283528189,
          "feature_value": 0.0
        },
        {
          "average_prediction": 4.861061511123727,
          "feature_value": 1.5244997899159665
        },
        {
          "average_prediction": 5.119237826595727,
          "feature_value": 3.048999579831933
        },
        {
          "average_prediction": 5.066281372691967,
          "feature_value": 4.5734993697479
        },
        {
          "average_prediction": 5.1177400063718625,
          "feature_value": 6.097999159663866
        },
        {
          "average_prediction": 5.501116536815691,
          "feature_value": 7.622498949579832
        },
        {
          "average_prediction": 5.456530190980932,
          "feature_value": 9.1469987394958
        },
        {
          "average_prediction": 6.566893729313105,
          "feature_value": 10.671498529411766
        },
        {
          "average_prediction": 6.714199342195683,
          "feature_value": 12.195998319327732
        },
        {
          "average_prediction": 7.3285002602020874,
          "feature_value": 13.720498109243698
        },
        {
          "average_prediction": 7.9997708964984175,
          "feature_value": 15.244997899159664
        },
        {
          "average_prediction": 8.165930474733427,
          "feature_value": 16.76949768907563
        }
      ],
      "response_status": "stable_numeric_grid"
    },
    {
      "explanation_scope": "registered_final_artifact_descriptive_on_2025_training_rows",
      "feature": "weighted_3yr_receiving_yards_per_game",
      "interpretation": "This explanation is associative, not causal; changing a feature here does not establish that the feature causes the prediction to change.",
      "method": "one_way_average_partial_dependence",
      "points": [
        {
          "average_prediction": 4.415909809369826,
          "feature_value": 0.0
        },
        {
          "average_prediction": 4.415909809369826,
          "feature_value": 6.797757830404888
        },
        {
          "average_prediction": 4.41029874922531,
          "feature_value": 13.595515660809776
        },
        {
          "average_prediction": 4.826560886019671,
          "feature_value": 20.393273491214664
        },
        {
          "average_prediction": 4.840731870131097,
          "feature_value": 27.19103132161955
        },
        {
          "average_prediction": 4.865203935072016,
          "feature_value": 33.98878915202444
        },
        {
          "average_prediction": 5.792675959590152,
          "feature_value": 40.78654698242933
        },
        {
          "average_prediction": 6.454316852744918,
          "feature_value": 47.58430481283421
        },
        {
          "average_prediction": 8.912683304571805,
          "feature_value": 54.3820626432391
        },
        {
          "average_prediction": 8.960318407867742,
          "feature_value": 61.17982047364399
        },
        {
          "average_prediction": 9.003017391402361,
          "feature_value": 67.97757830404888
        },
        {
          "average_prediction": 8.792694723154229,
          "feature_value": 74.77533613445377
        }
      ],
      "response_status": "stable_numeric_grid"
    }
  ],
  "importance": [
    {
      "explanation_scope": "registered_final_artifact_descriptive_on_2025_training_rows",
      "feature": "weighted_3yr_receiving_yards_per_game",
      "importance_mean": 0.7230763369890149,
      "importance_std": 0.10149577484633424,
      "rank": 1
    },
    {
      "explanation_scope": "registered_final_artifact_descriptive_on_2025_training_rows",
      "feature": "weighted_3yr_fantasy_points_per_game",
      "importance_mean": 0.4430854200661714,
      "importance_std": 0.04714000607623596,
      "rank": 2
    },
    {
      "explanation_scope": "registered_final_artifact_descriptive_on_2025_training_rows",
      "feature": "age_at_cutoff",
      "importance_mean": 0.38755330601987253,
      "importance_std": 0.060919943499693825,
      "rank": 3
    },
    {
      "explanation_scope": "registered_final_artifact_descriptive_on_2025_training_rows",
      "feature": "lag1_fantasy_points_total",
      "importance_mean": 0.2849068193037951,
      "importance_std": 0.0428823598745186,
      "rank": 4
    },
    {
      "explanation_scope": "registered_final_artifact_descriptive_on_2025_training_rows",
      "feature": "weighted_3yr_targets_per_game",
      "importance_mean": 0.20078077191523308,
      "importance_std": 0.03151952626887777,
      "rank": 5
    },
    {
      "explanation_scope": "registered_final_artifact_descriptive_on_2025_training_rows",
      "feature": "weighted_3yr_receptions_per_game",
      "importance_mean": 0.09676480452947182,
      "importance_std": 0.030217013686142248,
      "rank": 6
    },
    {
      "explanation_scope": "registered_final_artifact_descriptive_on_2025_training_rows",
      "feature": "weighted_3yr_receiving_tds_per_game",
      "importance_mean": 0.07428572145315204,
      "importance_std": 0.01586970181757477,
      "rank": 7
    },
    {
      "explanation_scope": "registered_final_artifact_descriptive_on_2025_training_rows",
      "feature": "lag1_fantasy_points_per_game",
      "importance_mean": 0.06586908063616939,
      "importance_std": 0.019767573084337776,
      "rank": 8
    },
    {
      "explanation_scope": "registered_final_artifact_descriptive_on_2025_training_rows",
      "feature": "draft_pick",
      "importance_mean": 0.06322988202999102,
      "importance_std": 0.007573325321285517,
      "rank": 9
    },
    {
      "explanation_scope": "registered_final_artifact_descriptive_on_2025_training_rows",
      "feature": "previous_team",
      "importance_mean": 0.05862019950099686,
      "importance_std": 0.015360175235456984,
      "rank": 10
    },
    {
      "explanation_scope": "registered_final_artifact_descriptive_on_2025_training_rows",
      "feature": "weighted_3yr_games_active",
      "importance_mean": 0.05339807425131386,
      "importance_std": 0.012810310662101514,
      "rank": 11
    },
    {
      "explanation_scope": "registered_final_artifact_descriptive_on_2025_training_rows",
      "feature": "weighted_3yr_two_point_conversions_per_game",
      "importance_mean": 0.05259012867217918,
      "importance_std": 0.010535816809941255,
      "rank": 12
    },
    {
      "explanation_scope": "registered_final_artifact_descriptive_on_2025_training_rows",
      "feature": "weighted_3yr_rushing_yards_per_game",
      "importance_mean": 0.03589891473940354,
      "importance_std": 0.00886093803147859,
      "rank": 13
    },
    {
      "explanation_scope": "registered_final_artifact_descriptive_on_2025_training_rows",
      "feature": "height_inches",
      "importance_mean": 0.031105066090073664,
      "importance_std": 0.007881719882292457,
      "rank": 14
    },
    {
      "explanation_scope": "registered_final_artifact_descriptive_on_2025_training_rows",
      "feature": "weighted_3yr_carries_per_game",
      "importance_mean": 0.030382820553844603,
      "importance_std": 0.0069273711663249945,
      "rank": 15
    },
    {
      "explanation_scope": "registered_final_artifact_descriptive_on_2025_training_rows",
      "feature": "nfl_experience_years",
      "importance_mean": 0.014151092326797298,
      "importance_std": 0.00339106108609504,
      "rank": 16
    },
    {
      "explanation_scope": "registered_final_artifact_descriptive_on_2025_training_rows",
      "feature": "weighted_3yr_fumbles_lost_per_game",
      "importance_mean": 0.01301525269307624,
      "importance_std": 0.0037684168850324086,
      "rank": 17
    },
    {
      "explanation_scope": "registered_final_artifact_descriptive_on_2025_training_rows",
      "feature": "weighted_3yr_passing_attempts_per_game",
      "importance_mean": 0.011420577904322915,
      "importance_std": 0.005074455292647731,
      "rank": 18
    },
    {
      "explanation_scope": "registered_final_artifact_descriptive_on_2025_training_rows",
      "feature": "missing_lag1",
      "importance_mean": 0.010978828692585152,
      "importance_std": 0.00454585089669435,
      "rank": 19
    },
    {
      "explanation_scope": "registered_final_artifact_descriptive_on_2025_training_rows",
      "feature": "team_changed_last_feature_season",
      "importance_mean": 0.008539118608659413,
      "importance_std": 0.0013277491619683732,
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

- Project-relative path: `models/artifacts/phase4-7ae8e9aed04bffca00c0/attempt-866987f75a2c406693cf892d49adc975/WR/fantasy_points_per_game/hist_gradient_boosting.joblib`
- SHA-256: `4f6387ad354d7823d5a26d2ec278f32f5877c76fb85ab0beb64be96870802529`

## Additional metadata

````json
{
  "publication_id": "attempt-866987f75a2c406693cf892d49adc975"
}
````
