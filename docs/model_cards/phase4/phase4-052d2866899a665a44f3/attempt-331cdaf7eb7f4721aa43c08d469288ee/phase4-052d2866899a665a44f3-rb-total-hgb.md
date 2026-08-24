# Model Card: phase4-052d2866899a665a44f3-rb-total-hgb

- Model ID: `phase4-052d2866899a665a44f3-rb-total-hgb`
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
  "draft_relevant_validation_mae": 77.39996641623142,
  "draft_relevant_validation_rows": 120,
  "draft_relevant_validation_signed_bias": -10.30255371991578,
  "position": "RB",
  "target_name": "fantasy_points_total",
  "test_mae": 22.379426556380587,
  "test_rows": 294,
  "test_season": 2025,
  "validation_mae": 23.20009823854864,
  "validation_rows": 1488,
  "validation_seasons": [
    2020,
    2021,
    2022,
    2023,
    2024
  ],
  "validation_top_n_capture_rate": 0.625
}
````

## Comparison with transparent baselines

````json
{
  "best_learned_vs_baseline_bootstrap": {
    "candidate_mae": 71.98658533498542,
    "ci95_lower": -9.06866373005735,
    "ci95_upper": 3.243812948760474,
    "direction": "uncertain",
    "mae_difference_candidate_minus_reference": -3.1023207068635656,
    "n_resamples": 2000,
    "reference_mae": 75.08890604184899,
    "rows": 120,
    "seed": 42
  },
  "decision_status": "learned_draft_relevant_improvement_inconclusive_baseline_retained",
  "learned_improvement_status": "inconclusive",
  "reference_metrics": {
    "candidate_name": "position_shrinkage",
    "candidate_source": "baseline",
    "draft_relevant_validation_mae": 75.08890604184899,
    "draft_relevant_validation_rows": 120,
    "draft_relevant_validation_signed_bias": 6.073505303971504,
    "position": "RB",
    "target_name": "fantasy_points_total",
    "test_mae": 46.48574953734089,
    "test_rows": 294,
    "test_season": 2025,
    "validation_mae": 45.68746765164051,
    "validation_rows": 1488,
    "validation_seasons": [
      2020,
      2021,
      2022,
      2023,
      2024
    ],
    "validation_top_n_capture_rate": 0.6
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
      "candidate_name": "hist_gradient_boosting",
      "empirical_coverage_p10_p90": 0.7993197278911565,
      "evaluation_scope": "test",
      "mean_interval_width_p10_p90": 73.93201754948254,
      "pinball_loss_p10": 7.4344541221293285,
      "pinball_loss_p50": 11.189713278190293,
      "pinball_loss_p90": 9.683709488200035,
      "position": "RB",
      "prediction_season": 2025,
      "projection_tier": "all",
      "rows": 294,
      "target_name": "fantasy_points_total"
    },
    {
      "candidate_name": "hist_gradient_boosting",
      "empirical_coverage_p10_p90": 0.3108108108108108,
      "evaluation_scope": "test",
      "mean_interval_width_p10_p90": 73.93201754948254,
      "pinball_loss_p10": 20.000922896730888,
      "pinball_loss_p50": 33.17811810815541,
      "pinball_loss_p90": 22.933121545682067,
      "position": "RB",
      "prediction_season": 2025,
      "projection_tier": "top",
      "rows": 74,
      "target_name": "fantasy_points_total"
    },
    {
      "candidate_name": "hist_gradient_boosting",
      "empirical_coverage_p10_p90": 0.9452054794520548,
      "evaluation_scope": "test",
      "mean_interval_width_p10_p90": 73.93201754948255,
      "pinball_loss_p10": 3.1122283939999598,
      "pinball_loss_p50": 5.117970305352058,
      "pinball_loss_p90": 5.850263954165138,
      "position": "RB",
      "prediction_season": 2025,
      "projection_tier": "middle",
      "rows": 146,
      "target_name": "fantasy_points_total"
    },
    {
      "candidate_name": "hist_gradient_boosting",
      "empirical_coverage_p10_p90": 1.0,
      "evaluation_scope": "test",
      "mean_interval_width_p10_p90": 73.93201754948254,
      "pinball_loss_p10": 3.395619892215444,
      "pinball_loss_p50": 1.1806932324735888,
      "pinball_loss_p90": 3.9975818627328095,
      "position": "RB",
      "prediction_season": 2025,
      "projection_tier": "lower",
      "rows": 74,
      "target_name": "fantasy_points_total"
    },
    {
      "candidate_name": "hist_gradient_boosting",
      "empirical_coverage_p10_p90": 0.8178807947019867,
      "evaluation_scope": "validation",
      "mean_interval_width_p10_p90": 90.57776381989065,
      "pinball_loss_p10": 9.563949729847991,
      "pinball_loss_p50": 12.884553617652273,
      "pinball_loss_p90": 9.307770950856927,
      "position": "RB",
      "prediction_season": 2020,
      "projection_tier": "all",
      "rows": 302,
      "target_name": "fantasy_points_total"
    },
    {
      "candidate_name": "hist_gradient_boosting",
      "empirical_coverage_p10_p90": 0.4473684210526316,
      "evaluation_scope": "validation",
      "mean_interval_width_p10_p90": 90.57776381989065,
      "pinball_loss_p10": 24.457720012212395,
      "pinball_loss_p50": 32.53606784911648,
      "pinball_loss_p90": 15.86676857795308,
      "position": "RB",
      "prediction_season": 2020,
      "projection_tier": "top",
      "rows": 76,
      "target_name": "fantasy_points_total"
    },
    {
      "candidate_name": "hist_gradient_boosting",
      "empirical_coverage_p10_p90": 0.9133333333333333,
      "evaluation_scope": "validation",
      "mean_interval_width_p10_p90": 90.57776381989065,
      "pinball_loss_p10": 4.636588538805637,
      "pinball_loss_p50": 8.046312850669397,
      "pinball_loss_p90": 8.338128179121965,
      "position": "RB",
      "prediction_season": 2020,
      "projection_tier": "middle",
      "rows": 150,
      "target_name": "fantasy_points_total"
    },
    {
      "candidate_name": "hist_gradient_boosting",
      "empirical_coverage_p10_p90": 1.0,
      "evaluation_scope": "validation",
      "mean_interval_width_p10_p90": 90.57776381989065,
      "pinball_loss_p10": 4.395234429804028,
      "pinball_loss_p50": 2.7821987947068996,
      "pinball_loss_p90": 4.6625419521850375,
      "position": "RB",
      "prediction_season": 2020,
      "projection_tier": "lower",
      "rows": 76,
      "target_name": "fantasy_points_total"
    },
    {
      "candidate_name": "hist_gradient_boosting",
      "empirical_coverage_p10_p90": 0.8079470198675497,
      "evaluation_scope": "validation",
      "mean_interval_width_p10_p90": 86.93164113898831,
      "pinball_loss_p10": 6.451522979003839,
      "pinball_loss_p50": 11.388440914741992,
      "pinball_loss_p90": 9.054517731213096,
      "position": "RB",
      "prediction_season": 2021,
      "projection_tier": "all",
      "rows": 302,
      "target_name": "fantasy_points_total"
    },
    {
      "candidate_name": "hist_gradient_boosting",
      "empirical_coverage_p10_p90": 0.39473684210526316,
      "evaluation_scope": "validation",
      "mean_interval_width_p10_p90": 86.93164113898834,
      "pinball_loss_p10": 12.602654812405286,
      "pinball_loss_p50": 27.055274535499308,
      "pinball_loss_p90": 16.203261862987205,
      "position": "RB",
      "prediction_season": 2021,
      "projection_tier": "top",
      "rows": 76,
      "target_name": "fantasy_points_total"
    },
    {
      "candidate_name": "hist_gradient_boosting",
      "empirical_coverage_p10_p90": 0.92,
      "evaluation_scope": "validation",
      "mean_interval_width_p10_p90": 86.93164113898833,
      "pinball_loss_p10": 4.44296834874288,
      "pinball_loss_p50": 8.312375069046745,
      "pinball_loss_p90": 7.776326014586278,
      "position": "RB",
      "prediction_season": 2021,
      "projection_tier": "middle",
      "rows": 150,
      "target_name": "fantasy_points_total"
    },
    {
      "candidate_name": "hist_gradient_boosting",
      "empirical_coverage_p10_p90": 1.0,
      "evaluation_scope": "validation",
      "mean_interval_width_p10_p90": 86.93164113898831,
      "pinball_loss_p10": 4.264643705327963,
      "pinball_loss_p50": 1.7927898841726653,
      "pinball_loss_p90": 4.428520408570871,
      "position": "RB",
      "prediction_season": 2021,
      "projection_tier": "lower",
      "rows": 76,
      "target_name": "fantasy_points_total"
    },
    {
      "candidate_name": "hist_gradient_boosting",
      "empirical_coverage_p10_p90": 0.8181818181818182,
      "evaluation_scope": "validation",
      "mean_interval_width_p10_p90": 81.98940233327914,
      "pinball_loss_p10": 6.511706537574937,
      "pinball_loss_p50": 11.546882820450831,
      "pinball_loss_p90": 9.920850254577974,
      "position": "RB",
      "prediction_season": 2022,
      "projection_tier": "all",
      "rows": 297,
      "target_name": "fantasy_points_total"
    },
    {
      "candidate_name": "hist_gradient_boosting",
      "empirical_coverage_p10_p90": 0.4594594594594595,
      "evaluation_scope": "validation",
      "mean_interval_width_p10_p90": 81.98940233327914,
      "pinball_loss_p10": 14.937665746224395,
      "pinball_loss_p50": 29.02818444437759,
      "pinball_loss_p90": 20.59713326112007,
      "position": "RB",
      "prediction_season": 2022,
      "projection_tier": "top",
      "rows": 74,
      "target_name": "fantasy_points_total"
    },
    {
      "candidate_name": "hist_gradient_boosting",
      "empirical_coverage_p10_p90": 0.9060402684563759,
      "evaluation_scope": "validation",
      "mean_interval_width_p10_p90": 81.98940233327914,
      "pinball_loss_p10": 3.683999853762499,
      "pinball_loss_p50": 8.256642771269,
      "pinball_loss_p90": 7.350716008382861,
      "position": "RB",
      "prediction_season": 2022,
      "projection_tier": "middle",
      "rows": 149,
      "target_name": "fantasy_points_total"
    },
    {
      "candidate_name": "hist_gradient_boosting",
      "empirical_coverage_p10_p90": 1.0,
      "evaluation_scope": "validation",
      "mean_interval_width_p10_p90": 81.98940233327914,
      "pinball_loss_p10": 3.7793729490343067,
      "pinball_loss_p50": 0.6905239982550573,
      "pinball_loss_p90": 4.419567284293607,
      "position": "RB",
      "prediction_season": 2022,
      "projection_tier": "lower",
      "rows": 74,
      "target_name": "fantasy_points_total"
    },
    {
      "candidate_name": "hist_gradient_boosting",
      "empirical_coverage_p10_p90": 0.7945205479452054,
      "evaluation_scope": "validation",
      "mean_interval_width_p10_p90": 76.51102101279038,
      "pinball_loss_p10": 6.800621350885161,
      "pinball_loss_p50": 11.58178088845418,
      "pinball_loss_p90": 10.149703505175232,
      "position": "RB",
      "prediction_season": 2023,
      "projection_tier": "all",
      "rows": 292,
      "target_name": "fantasy_points_total"
    },
    {
      "candidate_name": "hist_gradient_boosting",
      "empirical_coverage_p10_p90": 0.3013698630136986,
      "evaluation_scope": "validation",
      "mean_interval_width_p10_p90": 76.51102101279038,
      "pinball_loss_p10": 16.740155473328205,
      "pinball_loss_p50": 31.27397399524789,
      "pinball_loss_p90": 22.012032330533664,
      "position": "RB",
      "prediction_season": 2023,
      "projection_tier": "top",
      "rows": 73,
      "target_name": "fantasy_points_total"
    },
    {
      "candidate_name": "hist_gradient_boosting",
      "empirical_coverage_p10_p90": 0.9383561643835616,
      "evaluation_scope": "validation",
      "mean_interval_width_p10_p90": 76.51102101279038,
      "pinball_loss_p10": 3.462699158338544,
      "pinball_loss_p50": 7.248105854392101,
      "pinball_loss_p90": 7.236305601211792,
      "position": "RB",
      "prediction_season": 2023,
      "projection_tier": "middle",
      "rows": 146,
      "target_name": "fantasy_points_total"
    },
    {
      "candidate_name": "hist_gradient_boosting",
      "empirical_coverage_p10_p90": 1.0,
      "evaluation_scope": "validation",
      "mean_interval_width_p10_p90": 76.51102101279038,
      "pinball_loss_p10": 3.5369316135353537,
      "pinball_loss_p50": 0.5569378497846179,
      "pinball_loss_p90": 4.114170487743684,
      "position": "RB",
      "prediction_season": 2023,
      "projection_tier": "lower",
      "rows": 73,
      "target_name": "fantasy_points_total"
    },
    {
      "candidate_name": "hist_gradient_boosting",
      "empirical_coverage_p10_p90": 0.8338983050847457,
      "evaluation_scope": "validation",
      "mean_interval_width_p10_p90": 80.16311169537965,
      "pinball_loss_p10": 5.777302276714822,
      "pinball_loss_p50": 10.57330346981221,
      "pinball_loss_p90": 9.848609262932483,
      "position": "RB",
      "prediction_season": 2024,
      "projection_tier": "all",
      "rows": 295,
      "target_name": "fantasy_points_total"
    },
    {
      "candidate_name": "hist_gradient_boosting",
      "empirical_coverage_p10_p90": 0.43243243243243246,
      "evaluation_scope": "validation",
      "mean_interval_width_p10_p90": 80.16311169537965,
      "pinball_loss_p10": 12.20088909050377,
      "pinball_loss_p50": 29.49412134637088,
      "pinball_loss_p90": 23.13074383993347,
      "position": "RB",
      "prediction_season": 2024,
      "projection_tier": "top",
      "rows": 74,
      "target_name": "fantasy_points_total"
    },
    {
      "candidate_name": "hist_gradient_boosting",
      "empirical_coverage_p10_p90": 0.9523809523809523,
      "evaluation_scope": "validation",
      "mean_interval_width_p10_p90": 80.16311169537965,
      "pinball_loss_p10": 3.5778362596010305,
      "pinball_loss_p50": 6.050473038180553,
      "pinball_loss_p90": 5.958871500928149,
      "position": "RB",
      "prediction_season": 2024,
      "projection_tier": "middle",
      "rows": 147,
      "target_name": "fantasy_points_total"
    },
    {
      "candidate_name": "hist_gradient_boosting",
      "empirical_coverage_p10_p90": 1.0,
      "evaluation_scope": "validation",
      "mean_interval_width_p10_p90": 80.16311169537965,
      "pinball_loss_p10": 3.722924983408673,
      "pinball_loss_p50": 0.6370271263596714,
      "pinball_loss_p90": 4.29338618612929,
      "position": "RB",
      "prediction_season": 2024,
      "projection_tier": "lower",
      "rows": 74,
      "target_name": "fantasy_points_total"
    }
  ],
  "empirical_not_guaranteed": true,
  "method": "training-only signed out-of-fold residual quantiles",
  "operational_center": "training_only_residual_adjusted_p50",
  "residual_rows": 881,
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
      "feature": "age_at_cutoff",
      "interpretation": "This explanation is associative, not causal; changing a feature here does not establish that the feature causes the prediction to change.",
      "method": "one_way_average_partial_dependence",
      "points": [
        {
          "average_prediction": 53.6388271857782,
          "feature_value": 23.5765
        },
        {
          "average_prediction": 47.34781521933164,
          "feature_value": 24.477745454545452
        },
        {
          "average_prediction": 39.77953395008369,
          "feature_value": 25.37899090909091
        },
        {
          "average_prediction": 37.04234477509922,
          "feature_value": 26.280236363636362
        },
        {
          "average_prediction": 35.00267493325299,
          "feature_value": 27.18148181818182
        },
        {
          "average_prediction": 29.940857524282446,
          "feature_value": 28.082727272727272
        },
        {
          "average_prediction": 28.29790497720421,
          "feature_value": 28.98397272727273
        },
        {
          "average_prediction": 25.975839197215645,
          "feature_value": 29.885218181818182
        },
        {
          "average_prediction": 25.547300601379153,
          "feature_value": 30.78646363636364
        },
        {
          "average_prediction": 25.547300601379153,
          "feature_value": 31.68770909090909
        },
        {
          "average_prediction": 25.547300601379153,
          "feature_value": 32.58895454545455
        },
        {
          "average_prediction": 25.547300601379153,
          "feature_value": 33.4902
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
          "average_prediction": 21.101929318898144,
          "feature_value": 0.0
        },
        {
          "average_prediction": 21.19046044241549,
          "feature_value": 24.124545454545455
        },
        {
          "average_prediction": 41.45347627951487,
          "feature_value": 48.24909090909091
        },
        {
          "average_prediction": 41.24235747164455,
          "feature_value": 72.37363636363636
        },
        {
          "average_prediction": 62.40526779129965,
          "feature_value": 96.49818181818182
        },
        {
          "average_prediction": 76.63470177527766,
          "feature_value": 120.62272727272727
        },
        {
          "average_prediction": 82.84757912955301,
          "feature_value": 144.74727272727273
        },
        {
          "average_prediction": 92.36723916357103,
          "feature_value": 168.87181818181818
        },
        {
          "average_prediction": 95.6109045946797,
          "feature_value": 192.99636363636364
        },
        {
          "average_prediction": 95.14132091533885,
          "feature_value": 217.1209090909091
        },
        {
          "average_prediction": 94.2510138644441,
          "feature_value": 241.24545454545455
        },
        {
          "average_prediction": 93.57836208605087,
          "feature_value": 265.37
        }
      ],
      "response_status": "stable_numeric_grid"
    },
    {
      "explanation_scope": "registered_final_artifact_descriptive_on_2025_training_rows",
      "feature": "weighted_3yr_rushing_yards_per_game",
      "interpretation": "This explanation is associative, not causal; changing a feature here does not establish that the feature causes the prediction to change.",
      "method": "one_way_average_partial_dependence",
      "points": [
        {
          "average_prediction": 30.95238630138171,
          "feature_value": 0.0
        },
        {
          "average_prediction": 31.14891874805836,
          "feature_value": 5.859792780748664
        },
        {
          "average_prediction": 33.34176986328834,
          "feature_value": 11.719585561497327
        },
        {
          "average_prediction": 33.44545123694616,
          "feature_value": 17.57937834224599
        },
        {
          "average_prediction": 33.46903182013775,
          "feature_value": 23.439171122994654
        },
        {
          "average_prediction": 33.510900444501225,
          "feature_value": 29.298963903743317
        },
        {
          "average_prediction": 49.05171792545995,
          "feature_value": 35.15875668449198
        },
        {
          "average_prediction": 49.29262592116762,
          "feature_value": 41.018549465240646
        },
        {
          "average_prediction": 65.37172295020213,
          "feature_value": 46.87834224598931
        },
        {
          "average_prediction": 64.87802566787606,
          "feature_value": 52.73813502673797
        },
        {
          "average_prediction": 67.70908567589662,
          "feature_value": 58.597927807486634
        },
        {
          "average_prediction": 61.257060682510385,
          "feature_value": 64.4577205882353
        }
      ],
      "response_status": "stable_numeric_grid"
    }
  ],
  "importance": [
    {
      "explanation_scope": "registered_final_artifact_descriptive_on_2025_training_rows",
      "feature": "lag1_fantasy_points_total",
      "importance_mean": 15.200992171999022,
      "importance_std": 0.8456548635558938,
      "rank": 1
    },
    {
      "explanation_scope": "registered_final_artifact_descriptive_on_2025_training_rows",
      "feature": "weighted_3yr_rushing_yards_per_game",
      "importance_mean": 5.60701507652847,
      "importance_std": 0.327051405438768,
      "rank": 2
    },
    {
      "explanation_scope": "registered_final_artifact_descriptive_on_2025_training_rows",
      "feature": "age_at_cutoff",
      "importance_mean": 3.960944993368547,
      "importance_std": 0.8094653185192714,
      "rank": 3
    },
    {
      "explanation_scope": "registered_final_artifact_descriptive_on_2025_training_rows",
      "feature": "lag1_fantasy_points_per_game",
      "importance_mean": 3.056679794982197,
      "importance_std": 0.26831694154636004,
      "rank": 4
    },
    {
      "explanation_scope": "registered_final_artifact_descriptive_on_2025_training_rows",
      "feature": "weighted_3yr_fantasy_points_per_game",
      "importance_mean": 2.6450741712734236,
      "importance_std": 0.2696365646373728,
      "rank": 5
    },
    {
      "explanation_scope": "registered_final_artifact_descriptive_on_2025_training_rows",
      "feature": "weighted_3yr_targets_per_game",
      "importance_mean": 1.6805108441226302,
      "importance_std": 0.152994652382619,
      "rank": 6
    },
    {
      "explanation_scope": "registered_final_artifact_descriptive_on_2025_training_rows",
      "feature": "missing_lag1",
      "importance_mean": 1.575020158885308,
      "importance_std": 0.16716070526921165,
      "rank": 7
    },
    {
      "explanation_scope": "registered_final_artifact_descriptive_on_2025_training_rows",
      "feature": "weighted_3yr_fumbles_lost_per_game",
      "importance_mean": 1.265419584325987,
      "importance_std": 0.19576581660739326,
      "rank": 8
    },
    {
      "explanation_scope": "registered_final_artifact_descriptive_on_2025_training_rows",
      "feature": "weighted_3yr_carries_per_game",
      "importance_mean": 1.2067794066273478,
      "importance_std": 0.07095279850664352,
      "rank": 9
    },
    {
      "explanation_scope": "registered_final_artifact_descriptive_on_2025_training_rows",
      "feature": "lag1_stat_games",
      "importance_mean": 1.2050059775611053,
      "importance_std": 0.18236076554753283,
      "rank": 10
    },
    {
      "explanation_scope": "registered_final_artifact_descriptive_on_2025_training_rows",
      "feature": "draft_pick",
      "importance_mean": 0.9986877531929356,
      "importance_std": 0.15141686883986252,
      "rank": 11
    },
    {
      "explanation_scope": "registered_final_artifact_descriptive_on_2025_training_rows",
      "feature": "weighted_3yr_receiving_yards_per_game",
      "importance_mean": 0.9518990067180774,
      "importance_std": 0.1027441877982477,
      "rank": 12
    },
    {
      "explanation_scope": "registered_final_artifact_descriptive_on_2025_training_rows",
      "feature": "weighted_3yr_receiving_tds_per_game",
      "importance_mean": 0.8340357032515826,
      "importance_std": 0.06897780504282218,
      "rank": 13
    },
    {
      "explanation_scope": "registered_final_artifact_descriptive_on_2025_training_rows",
      "feature": "weighted_3yr_games_active",
      "importance_mean": 0.7301460984791941,
      "importance_std": 0.11510777344687838,
      "rank": 14
    },
    {
      "explanation_scope": "registered_final_artifact_descriptive_on_2025_training_rows",
      "feature": "weighted_3yr_rushing_tds_per_game",
      "importance_mean": 0.5109728651403372,
      "importance_std": 0.053596310274011606,
      "rank": 15
    },
    {
      "explanation_scope": "registered_final_artifact_descriptive_on_2025_training_rows",
      "feature": "weighted_3yr_passing_yards_per_game",
      "importance_mean": 0.5017153425100066,
      "importance_std": 0.09695479191404946,
      "rank": 16
    },
    {
      "explanation_scope": "registered_final_artifact_descriptive_on_2025_training_rows",
      "feature": "weighted_3yr_receptions_per_game",
      "importance_mean": 0.4770530448496107,
      "importance_std": 0.030672093076459767,
      "rank": 17
    },
    {
      "explanation_scope": "registered_final_artifact_descriptive_on_2025_training_rows",
      "feature": "previous_team",
      "importance_mean": 0.4675951391698064,
      "importance_std": 0.08231590002151323,
      "rank": 18
    },
    {
      "explanation_scope": "registered_final_artifact_descriptive_on_2025_training_rows",
      "feature": "draft_round",
      "importance_mean": 0.41617123507424764,
      "importance_std": 0.09566191263909075,
      "rank": 19
    },
    {
      "explanation_scope": "registered_final_artifact_descriptive_on_2025_training_rows",
      "feature": "nfl_experience_years",
      "importance_mean": 0.33805242401914626,
      "importance_std": 0.14734414378995014,
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

- Project-relative path: `models/artifacts/phase4-052d2866899a665a44f3/attempt-331cdaf7eb7f4721aa43c08d469288ee/RB/fantasy_points_total/hist_gradient_boosting.joblib`
- SHA-256: `5844b8fd216e24d2e57cf92f3db58b2c5c651024fcaba17649052b7c6580d2a2`

## Additional metadata

````json
{
  "publication_id": "attempt-331cdaf7eb7f4721aa43c08d469288ee"
}
````
