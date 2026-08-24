# Model Card: phase4-052d2866899a665a44f3-wr-games-hgb

- Model ID: `phase4-052d2866899a665a44f3-wr-games-hgb`
- Trained at: 2026-08-24T20:21:18+00:00
- Target: `games_active`
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
  "draft_relevant_validation_mae": 3.1912641476381407,
  "draft_relevant_validation_rows": 180,
  "draft_relevant_validation_signed_bias": -0.769470957423737,
  "position": "WR",
  "target_name": "games_active",
  "test_mae": 2.8421168749604724,
  "test_rows": 433,
  "test_season": 2025,
  "validation_mae": 2.9141609593376714,
  "validation_rows": 2101,
  "validation_seasons": [
    2020,
    2021,
    2022,
    2023,
    2024
  ],
  "validation_top_n_capture_rate": null
}
````

## Comparison with transparent baselines

````json
{
  "best_learned_vs_baseline_bootstrap": {
    "candidate_mae": 3.098208196136572,
    "ci95_lower": 0.19691558722738153,
    "ci95_upper": 0.8257878990843412,
    "direction": "reference_lower_mae",
    "mae_difference_candidate_minus_reference": 0.5197029051312807,
    "n_resamples": 2000,
    "reference_mae": 2.5785052910052912,
    "rows": 180,
    "seed": 42
  },
  "decision_status": "learned_draft_relevant_regression_baseline_retained",
  "learned_improvement_status": "regression",
  "reference_metrics": {
    "candidate_name": "age_position_adjusted",
    "candidate_source": "baseline",
    "draft_relevant_validation_mae": 2.5785052910052912,
    "draft_relevant_validation_rows": 180,
    "draft_relevant_validation_signed_bias": 1.1674206349206362,
    "position": "WR",
    "target_name": "games_active",
    "test_mae": 6.409305988654868,
    "test_rows": 433,
    "test_season": 2025,
    "validation_mae": 5.93888064590859,
    "validation_rows": 2101,
    "validation_seasons": [
      2020,
      2021,
      2022,
      2023,
      2024
    ],
    "validation_top_n_capture_rate": null
  },
  "selected_champion": "age_position_adjusted",
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
      "candidate_name": "hist_gradient_boosting",
      "empirical_coverage_p10_p90": 0.789838337182448,
      "evaluation_scope": "test",
      "mean_interval_width_p10_p90": 7.890950245417076,
      "pinball_loss_p10": 0.5760674796567485,
      "pinball_loss_p50": 1.4210584374802362,
      "pinball_loss_p90": 0.8661293461983057,
      "position": "WR",
      "prediction_season": 2025,
      "projection_tier": "all",
      "rows": 433,
      "target_name": "games_active"
    },
    {
      "candidate_name": "hist_gradient_boosting",
      "empirical_coverage_p10_p90": 0.7339449541284404,
      "evaluation_scope": "test",
      "mean_interval_width_p10_p90": 9.3454397259825,
      "pinball_loss_p10": 1.168479524553265,
      "pinball_loss_p50": 1.9532475535675253,
      "pinball_loss_p90": 0.558658537621754,
      "position": "WR",
      "prediction_season": 2025,
      "projection_tier": "top",
      "rows": 109,
      "target_name": "games_active"
    },
    {
      "candidate_name": "hist_gradient_boosting",
      "empirical_coverage_p10_p90": 0.7209302325581395,
      "evaluation_scope": "test",
      "mean_interval_width_p10_p90": 8.30573892492133,
      "pinball_loss_p10": 0.5524323279770521,
      "pinball_loss_p50": 1.7947023561994906,
      "pinball_loss_p90": 1.1364558203385957,
      "position": "WR",
      "prediction_season": 2025,
      "projection_tier": "middle",
      "rows": 215,
      "target_name": "games_active"
    },
    {
      "candidate_name": "hist_gradient_boosting",
      "empirical_coverage_p10_p90": 0.981651376146789,
      "evaluation_scope": "test",
      "mean_interval_width_p10_p90": 5.618299608031333,
      "pinball_loss_p10": 0.030275229357798167,
      "pinball_loss_p50": 0.1518652615338663,
      "pinball_loss_p90": 0.6403873846816249,
      "position": "WR",
      "prediction_season": 2025,
      "projection_tier": "lower",
      "rows": 109,
      "target_name": "games_active"
    },
    {
      "candidate_name": "hist_gradient_boosting",
      "empirical_coverage_p10_p90": 0.8325242718446602,
      "evaluation_scope": "validation",
      "mean_interval_width_p10_p90": 8.693583654911773,
      "pinball_loss_p10": 0.5476648163945832,
      "pinball_loss_p50": 1.4000722312196,
      "pinball_loss_p90": 0.8988427197995561,
      "position": "WR",
      "prediction_season": 2020,
      "projection_tier": "all",
      "rows": 412,
      "target_name": "games_active"
    },
    {
      "candidate_name": "hist_gradient_boosting",
      "empirical_coverage_p10_p90": 0.8076923076923077,
      "evaluation_scope": "validation",
      "mean_interval_width_p10_p90": 10.74649658914478,
      "pinball_loss_p10": 1.21097584691453,
      "pinball_loss_p50": 1.9571233747216341,
      "pinball_loss_p90": 0.5791720233562363,
      "position": "WR",
      "prediction_season": 2020,
      "projection_tier": "top",
      "rows": 104,
      "target_name": "games_active"
    },
    {
      "candidate_name": "hist_gradient_boosting",
      "empirical_coverage_p10_p90": 0.7658536585365854,
      "evaluation_scope": "validation",
      "mean_interval_width_p10_p90": 8.997602368948458,
      "pinball_loss_p10": 0.4741288598802788,
      "pinball_loss_p50": 1.7599459916654885,
      "pinball_loss_p90": 1.1786205480855698,
      "position": "WR",
      "prediction_season": 2020,
      "projection_tier": "middle",
      "rows": 205,
      "target_name": "games_active"
    },
    {
      "candidate_name": "hist_gradient_boosting",
      "empirical_coverage_p10_p90": 0.9902912621359223,
      "evaluation_scope": "validation",
      "mean_interval_width_p10_p90": 6.015653737069514,
      "pinball_loss_p10": 0.024271844660194174,
      "pinball_loss_p50": 0.12135922330097088,
      "pinball_loss_p90": 0.6647776482604536,
      "position": "WR",
      "prediction_season": 2020,
      "projection_tier": "lower",
      "rows": 103,
      "target_name": "games_active"
    },
    {
      "candidate_name": "hist_gradient_boosting",
      "empirical_coverage_p10_p90": 0.8038277511961722,
      "evaluation_scope": "validation",
      "mean_interval_width_p10_p90": 8.542406191659465,
      "pinball_loss_p10": 0.6007965026579558,
      "pinball_loss_p50": 1.5634226096717878,
      "pinball_loss_p90": 0.9646490969309852,
      "position": "WR",
      "prediction_season": 2021,
      "projection_tier": "all",
      "rows": 418,
      "target_name": "games_active"
    },
    {
      "candidate_name": "hist_gradient_boosting",
      "empirical_coverage_p10_p90": 0.8,
      "evaluation_scope": "validation",
      "mean_interval_width_p10_p90": 10.259841437857668,
      "pinball_loss_p10": 1.2197842911840526,
      "pinball_loss_p50": 2.132310168457574,
      "pinball_loss_p90": 0.50838368468741,
      "position": "WR",
      "prediction_season": 2021,
      "projection_tier": "top",
      "rows": 105,
      "target_name": "games_active"
    },
    {
      "candidate_name": "hist_gradient_boosting",
      "empirical_coverage_p10_p90": 0.7163461538461539,
      "evaluation_scope": "validation",
      "mean_interval_width_p10_p90": 8.985445476203003,
      "pinball_loss_p10": 0.57911340161875,
      "pinball_loss_p50": 2.0028589702911717,
      "pinball_loss_p90": 1.3455197467267537,
      "position": "WR",
      "prediction_season": 2021,
      "projection_tier": "middle",
      "rows": 208,
      "target_name": "games_active"
    },
    {
      "candidate_name": "hist_gradient_boosting",
      "empirical_coverage_p10_p90": 0.9809523809523809,
      "evaluation_scope": "validation",
      "mean_interval_width_p10_p90": 5.947331219889306,
      "pinball_loss_p10": 0.024761904761904766,
      "pinball_loss_p50": 0.12403254603998487,
      "pinball_loss_p90": 0.6664278886267525,
      "position": "WR",
      "prediction_season": 2021,
      "projection_tier": "lower",
      "rows": 105,
      "target_name": "games_active"
    },
    {
      "candidate_name": "hist_gradient_boosting",
      "empirical_coverage_p10_p90": 0.8,
      "evaluation_scope": "validation",
      "mean_interval_width_p10_p90": 8.587194165555522,
      "pinball_loss_p10": 0.6428874306294245,
      "pinball_loss_p50": 1.5103075159159114,
      "pinball_loss_p90": 0.8448926841876906,
      "position": "WR",
      "prediction_season": 2022,
      "projection_tier": "all",
      "rows": 430,
      "target_name": "games_active"
    },
    {
      "candidate_name": "hist_gradient_boosting",
      "empirical_coverage_p10_p90": 0.7685185185185185,
      "evaluation_scope": "validation",
      "mean_interval_width_p10_p90": 9.895131361869277,
      "pinball_loss_p10": 1.4052735904799454,
      "pinball_loss_p50": 2.195884732899483,
      "pinball_loss_p90": 0.5462661619958675,
      "position": "WR",
      "prediction_season": 2022,
      "projection_tier": "top",
      "rows": 108,
      "target_name": "games_active"
    },
    {
      "candidate_name": "hist_gradient_boosting",
      "empirical_coverage_p10_p90": 0.7209302325581395,
      "evaluation_scope": "validation",
      "mean_interval_width_p10_p90": 9.194857692804526,
      "pinball_loss_p10": 0.5756839413898531,
      "pinball_loss_p50": 1.8937318104344514,
      "pinball_loss_p90": 1.10591546392759,
      "position": "WR",
      "prediction_season": 2022,
      "projection_tier": "middle",
      "rows": 215,
      "target_name": "games_active"
    },
    {
      "candidate_name": "hist_gradient_boosting",
      "empirical_coverage_p10_p90": 0.9906542056074766,
      "evaluation_scope": "validation",
      "mean_interval_width_p10_p90": 6.046027104243174,
      "pinball_loss_p10": 0.008411214953271028,
      "pinball_loss_p50": 0.047891041563464874,
      "pinball_loss_p90": 0.6218250837450598,
      "position": "WR",
      "prediction_season": 2022,
      "projection_tier": "lower",
      "rows": 107,
      "target_name": "games_active"
    },
    {
      "candidate_name": "hist_gradient_boosting",
      "empirical_coverage_p10_p90": 0.7985611510791367,
      "evaluation_scope": "validation",
      "mean_interval_width_p10_p90": 8.493065552164921,
      "pinball_loss_p10": 0.5477581039106345,
      "pinball_loss_p50": 1.4614762911678183,
      "pinball_loss_p90": 0.8448208754458242,
      "position": "WR",
      "prediction_season": 2023,
      "projection_tier": "all",
      "rows": 417,
      "target_name": "games_active"
    },
    {
      "candidate_name": "hist_gradient_boosting",
      "empirical_coverage_p10_p90": 0.8285714285714286,
      "evaluation_scope": "validation",
      "mean_interval_width_p10_p90": 9.973701581774952,
      "pinball_loss_p10": 1.044100000537665,
      "pinball_loss_p50": 1.9039449156687307,
      "pinball_loss_p90": 0.46015934495629923,
      "position": "WR",
      "prediction_season": 2023,
      "projection_tier": "top",
      "rows": 105,
      "target_name": "games_active"
    },
    {
      "candidate_name": "hist_gradient_boosting",
      "empirical_coverage_p10_p90": 0.6971153846153846,
      "evaluation_scope": "validation",
      "mean_interval_width_p10_p90": 8.963319873276271,
      "pinball_loss_p10": 0.5571376407417298,
      "pinball_loss_p50": 1.8920343737250667,
      "pinball_loss_p90": 1.1596968294321714,
      "position": "WR",
      "prediction_season": 2023,
      "projection_tier": "middle",
      "rows": 208,
      "target_name": "games_active"
    },
    {
      "candidate_name": "hist_gradient_boosting",
      "empirical_coverage_p10_p90": 0.9711538461538461,
      "evaluation_scope": "validation",
      "mean_interval_width_p10_p90": 6.057683995432097,
      "pinball_loss_p10": 0.02788461538461539,
      "pinball_loss_p50": 0.15363699554759308,
      "pinball_loss_p90": 0.6034291665250535,
      "position": "WR",
      "prediction_season": 2023,
      "projection_tier": "lower",
      "rows": 104,
      "target_name": "games_active"
    },
    {
      "candidate_name": "hist_gradient_boosting",
      "empirical_coverage_p10_p90": 0.8349056603773585,
      "evaluation_scope": "validation",
      "mean_interval_width_p10_p90": 8.352485826984235,
      "pinball_loss_p10": 0.5551148562398286,
      "pinball_loss_p50": 1.3493345104200936,
      "pinball_loss_p90": 0.7955638706368318,
      "position": "WR",
      "prediction_season": 2024,
      "projection_tier": "all",
      "rows": 424,
      "target_name": "games_active"
    },
    {
      "candidate_name": "hist_gradient_boosting",
      "empirical_coverage_p10_p90": 0.8207547169811321,
      "evaluation_scope": "validation",
      "mean_interval_width_p10_p90": 9.265027830624692,
      "pinball_loss_p10": 1.1649246214504683,
      "pinball_loss_p50": 1.8797032058268426,
      "pinball_loss_p90": 0.4622856381179868,
      "position": "WR",
      "prediction_season": 2024,
      "projection_tier": "top",
      "rows": 106,
      "target_name": "games_active"
    },
    {
      "candidate_name": "hist_gradient_boosting",
      "empirical_coverage_p10_p90": 0.7594339622641509,
      "evaluation_scope": "validation",
      "mean_interval_width_p10_p90": 8.941167358475864,
      "pinball_loss_p10": 0.5263523074148003,
      "pinball_loss_p50": 1.7417617546262856,
      "pinball_loss_p90": 1.048270978536267,
      "position": "WR",
      "prediction_season": 2024,
      "projection_tier": "middle",
      "rows": 212,
      "target_name": "games_active"
    },
    {
      "candidate_name": "hist_gradient_boosting",
      "empirical_coverage_p10_p90": 1.0,
      "evaluation_scope": "validation",
      "mean_interval_width_p10_p90": 6.2625807603605175,
      "pinball_loss_p10": 0.0028301886792452833,
      "pinball_loss_p50": 0.03411132660096012,
      "pinball_loss_p90": 0.6234278873568063,
      "position": "WR",
      "prediction_season": 2024,
      "projection_tier": "lower",
      "rows": 106,
      "target_name": "games_active"
    }
  ],
  "empirical_not_guaranteed": true,
  "method": "training-only signed out-of-fold residual quantiles",
  "operational_center": "training_only_residual_adjusted_p50",
  "residual_rows": 1274,
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
  "feature_responses": [
    {
      "explanation_scope": "registered_final_artifact_descriptive_on_2025_training_rows",
      "feature": "lag1_fantasy_points_total",
      "interpretation": "This explanation is associative, not causal; changing a feature here does not establish that the feature causes the prediction to change.",
      "method": "one_way_average_partial_dependence",
      "points": [
        {
          "average_prediction": 4.535947847258177,
          "feature_value": 0.0
        },
        {
          "average_prediction": 4.68407164478234,
          "feature_value": 21.884090909090908
        },
        {
          "average_prediction": 5.28764220375193,
          "feature_value": 43.768181818181816
        },
        {
          "average_prediction": 8.504295167100507,
          "feature_value": 65.65227272727273
        },
        {
          "average_prediction": 8.567110978602255,
          "feature_value": 87.53636363636363
        },
        {
          "average_prediction": 9.084798293411133,
          "feature_value": 109.42045454545453
        },
        {
          "average_prediction": 9.275045200965023,
          "feature_value": 131.30454545454546
        },
        {
          "average_prediction": 9.275045200965023,
          "feature_value": 153.18863636363636
        },
        {
          "average_prediction": 9.904619479663323,
          "feature_value": 175.07272727272726
        },
        {
          "average_prediction": 10.303246216725334,
          "feature_value": 196.95681818181816
        },
        {
          "average_prediction": 10.303246216725334,
          "feature_value": 218.84090909090907
        },
        {
          "average_prediction": 10.303246216725334,
          "feature_value": 240.725
        }
      ],
      "response_status": "stable_numeric_grid"
    },
    {
      "explanation_scope": "registered_final_artifact_descriptive_on_2025_training_rows",
      "feature": "missing_lag1",
      "interpretation": "This explanation is associative, not causal; changing a feature here does not establish that the feature causes the prediction to change.",
      "method": "one_way_average_partial_dependence",
      "points": [
        {
          "average_prediction": 6.464264774340257,
          "feature_value": 0.0
        },
        {
          "average_prediction": 3.960395914794438,
          "feature_value": 1.0
        }
      ],
      "response_status": "stable_numeric_grid"
    },
    {
      "explanation_scope": "registered_final_artifact_descriptive_on_2025_training_rows",
      "feature": "weighted_3yr_games_active",
      "interpretation": "This explanation is associative, not causal; changing a feature here does not establish that the feature causes the prediction to change.",
      "method": "one_way_average_partial_dependence",
      "points": [
        {
          "average_prediction": 4.007967896829139,
          "feature_value": 1.4900000000000009
        },
        {
          "average_prediction": 4.046900263620595,
          "feature_value": 2.900000000000001
        },
        {
          "average_prediction": 4.063285722391787,
          "feature_value": 4.3100000000000005
        },
        {
          "average_prediction": 4.366985973075142,
          "feature_value": 5.720000000000001
        },
        {
          "average_prediction": 4.482192039494436,
          "feature_value": 7.130000000000001
        },
        {
          "average_prediction": 4.483294921276275,
          "feature_value": 8.540000000000001
        },
        {
          "average_prediction": 4.824526048770265,
          "feature_value": 9.95
        },
        {
          "average_prediction": 5.120863702507761,
          "feature_value": 11.36
        },
        {
          "average_prediction": 5.530152678968893,
          "feature_value": 12.77
        },
        {
          "average_prediction": 5.552257970665299,
          "feature_value": 14.18
        },
        {
          "average_prediction": 5.822475298197912,
          "feature_value": 15.59
        },
        {
          "average_prediction": 6.469469065843294,
          "feature_value": 17.0
        }
      ],
      "response_status": "stable_numeric_grid"
    }
  ],
  "importance": [
    {
      "explanation_scope": "registered_final_artifact_descriptive_on_2025_training_rows",
      "feature": "lag1_fantasy_points_total",
      "importance_mean": 1.1051335304821746,
      "importance_std": 0.07978528425665439,
      "rank": 1
    },
    {
      "explanation_scope": "registered_final_artifact_descriptive_on_2025_training_rows",
      "feature": "missing_lag1",
      "importance_mean": 0.7564122890912494,
      "importance_std": 0.025480862466430623,
      "rank": 2
    },
    {
      "explanation_scope": "registered_final_artifact_descriptive_on_2025_training_rows",
      "feature": "weighted_3yr_games_active",
      "importance_mean": 0.3283602868539548,
      "importance_std": 0.06846946697846983,
      "rank": 3
    },
    {
      "explanation_scope": "registered_final_artifact_descriptive_on_2025_training_rows",
      "feature": "lag1_fantasy_points_per_game",
      "importance_mean": 0.32743715492799835,
      "importance_std": 0.03623983149847494,
      "rank": 4
    },
    {
      "explanation_scope": "registered_final_artifact_descriptive_on_2025_training_rows",
      "feature": "age_at_cutoff",
      "importance_mean": 0.3262166544028517,
      "importance_std": 0.03500960137306333,
      "rank": 5
    },
    {
      "explanation_scope": "registered_final_artifact_descriptive_on_2025_training_rows",
      "feature": "lag1_games_active",
      "importance_mean": 0.14805780183145406,
      "importance_std": 0.024855700512588785,
      "rank": 6
    },
    {
      "explanation_scope": "registered_final_artifact_descriptive_on_2025_training_rows",
      "feature": "weighted_3yr_receiving_tds_per_game",
      "importance_mean": 0.12472175016959568,
      "importance_std": 0.013791973228221309,
      "rank": 7
    },
    {
      "explanation_scope": "registered_final_artifact_descriptive_on_2025_training_rows",
      "feature": "weighted_3yr_receiving_yards_per_game",
      "importance_mean": 0.10533386590276814,
      "importance_std": 0.014002645440152839,
      "rank": 8
    },
    {
      "explanation_scope": "registered_final_artifact_descriptive_on_2025_training_rows",
      "feature": "previous_team",
      "importance_mean": 0.08808516473222187,
      "importance_std": 0.008215771329671318,
      "rank": 9
    },
    {
      "explanation_scope": "registered_final_artifact_descriptive_on_2025_training_rows",
      "feature": "weighted_3yr_targets_per_game",
      "importance_mean": 0.08762119579245464,
      "importance_std": 0.012836997522643398,
      "rank": 10
    },
    {
      "explanation_scope": "registered_final_artifact_descriptive_on_2025_training_rows",
      "feature": "weighted_3yr_rushing_yards_per_game",
      "importance_mean": 0.08552082891478205,
      "importance_std": 0.007316574266703739,
      "rank": 11
    },
    {
      "explanation_scope": "registered_final_artifact_descriptive_on_2025_training_rows",
      "feature": "weighted_3yr_fantasy_points_per_game",
      "importance_mean": 0.06519125148634633,
      "importance_std": 0.008486202081726901,
      "rank": 12
    },
    {
      "explanation_scope": "registered_final_artifact_descriptive_on_2025_training_rows",
      "feature": "draft_pick",
      "importance_mean": 0.04560820431510706,
      "importance_std": 0.008337651526353879,
      "rank": 13
    },
    {
      "explanation_scope": "registered_final_artifact_descriptive_on_2025_training_rows",
      "feature": "weighted_3yr_carries_per_game",
      "importance_mean": 0.04081783811411412,
      "importance_std": 0.005260267586878021,
      "rank": 14
    },
    {
      "explanation_scope": "registered_final_artifact_descriptive_on_2025_training_rows",
      "feature": "weighted_3yr_receptions_per_game",
      "importance_mean": 0.03859721365192037,
      "importance_std": 0.002003822248513165,
      "rank": 15
    },
    {
      "explanation_scope": "registered_final_artifact_descriptive_on_2025_training_rows",
      "feature": "height_inches",
      "importance_mean": 0.02545785922721553,
      "importance_std": 0.002944597848970673,
      "rank": 16
    },
    {
      "explanation_scope": "registered_final_artifact_descriptive_on_2025_training_rows",
      "feature": "weighted_3yr_rushing_tds_per_game",
      "importance_mean": 0.022894221010200156,
      "importance_std": 0.006910008462120224,
      "rank": 17
    },
    {
      "explanation_scope": "registered_final_artifact_descriptive_on_2025_training_rows",
      "feature": "weighted_3yr_passing_yards_per_game",
      "importance_mean": 0.018073550402948956,
      "importance_std": 0.008148490879093008,
      "rank": 18
    },
    {
      "explanation_scope": "registered_final_artifact_descriptive_on_2025_training_rows",
      "feature": "weighted_3yr_fumbles_lost_per_game",
      "importance_mean": 0.015119886611977051,
      "importance_std": 0.00246438372508136,
      "rank": 19
    },
    {
      "explanation_scope": "registered_final_artifact_descriptive_on_2025_training_rows",
      "feature": "nfl_experience_years",
      "importance_mean": 0.01479159373643819,
      "importance_std": 0.0054646443371209755,
      "rank": 20
    }
  ],
  "method": "registered-artifact descriptive permutation importance and partial dependence on 2025 rows, computed only after champion selection"
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

- Project-relative path: `models/artifacts/phase4-052d2866899a665a44f3/attempt-331cdaf7eb7f4721aa43c08d469288ee/WR/games_active/hist_gradient_boosting.joblib`
- SHA-256: `6fbc895481d8b6f7272dc26f94bbb9076e7e4c2de854ac1223b399ce12b122f9`

## Additional metadata

````json
{
  "publication_id": "attempt-331cdaf7eb7f4721aa43c08d469288ee"
}
````
