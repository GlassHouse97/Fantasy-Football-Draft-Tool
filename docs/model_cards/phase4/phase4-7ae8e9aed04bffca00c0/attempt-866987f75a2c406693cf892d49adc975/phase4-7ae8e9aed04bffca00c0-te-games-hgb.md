# Model Card: phase4-7ae8e9aed04bffca00c0-te-games-hgb

- Model ID: `phase4-7ae8e9aed04bffca00c0-te-games-hgb`
- Trained at: 2026-08-05T20:58:13+00:00
- Target: `games_active`
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
  "position": "TE",
  "target_name": "games_active",
  "test_mae": 2.5701022249145264,
  "test_rows": 235,
  "test_season": 2025,
  "validation_mae": 3.252152007104269,
  "validation_rows": 1158,
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
    "candidate_mae": 3.252152007104269,
    "ci95_lower": -3.3900043141986305,
    "ci95_upper": -2.6881702109533583,
    "direction": "candidate_lower_mae",
    "mae_difference_candidate_minus_reference": -3.033460583473347,
    "n_resamples": 2000,
    "reference_mae": 6.285612590577616,
    "rows": 1158,
    "seed": 42
  },
  "decision_status": "learned_significant_improvement_selected",
  "learned_improvement_status": "statistically_clear",
  "reference_metrics": {
    "candidate_name": "age_position_adjusted",
    "candidate_source": "baseline",
    "position": "TE",
    "target_name": "games_active",
    "test_mae": 6.164744921388118,
    "test_rows": 235,
    "test_season": 2025,
    "validation_mae": 6.285612590577616,
    "validation_rows": 1158,
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
      "empirical_coverage_p10_p90": 0.8425531914893617,
      "evaluation_scope": "test",
      "mean_interval_width_p10_p90": 8.361448159497723,
      "pinball_loss_p10": 0.5194392580325328,
      "pinball_loss_p50": 1.2850511124572632,
      "pinball_loss_p90": 0.7332782280004438,
      "position": "TE",
      "prediction_season": 2025,
      "projection_tier": "all",
      "rows": 235,
      "target_name": "games_active"
    },
    {
      "candidate_name": "hist_gradient_boosting",
      "empirical_coverage_p10_p90": 0.8983050847457628,
      "evaluation_scope": "test",
      "mean_interval_width_p10_p90": 9.308936028518998,
      "pinball_loss_p10": 0.8585528179956868,
      "pinball_loss_p50": 1.459668084450813,
      "pinball_loss_p90": 0.3971931340575378,
      "position": "TE",
      "prediction_season": 2025,
      "projection_tier": "top",
      "rows": 59,
      "target_name": "games_active"
    },
    {
      "candidate_name": "hist_gradient_boosting",
      "empirical_coverage_p10_p90": 0.7350427350427351,
      "evaluation_scope": "test",
      "mean_interval_width_p10_p90": 9.199614633585123,
      "pinball_loss_p10": 0.60609922543504,
      "pinball_loss_p50": 1.8203641797376882,
      "pinball_loss_p90": 0.9867535957582995,
      "position": "TE",
      "prediction_season": 2025,
      "projection_tier": "middle",
      "rows": 117,
      "target_name": "games_active"
    },
    {
      "candidate_name": "hist_gradient_boosting",
      "empirical_coverage_p10_p90": 1.0,
      "evaluation_scope": "test",
      "mean_interval_width_p10_p90": 5.7518335537268666,
      "pinball_loss_p10": 0.00847457627118644,
      "pinball_loss_p50": 0.04888110873812529,
      "pinball_loss_p90": 0.5667087791015003,
      "position": "TE",
      "prediction_season": 2025,
      "projection_tier": "lower",
      "rows": 59,
      "target_name": "games_active"
    },
    {
      "candidate_name": "hist_gradient_boosting",
      "empirical_coverage_p10_p90": 0.8526785714285714,
      "evaluation_scope": "validation",
      "mean_interval_width_p10_p90": 10.95271425763657,
      "pinball_loss_p10": 0.6342346638065701,
      "pinball_loss_p50": 1.7398676242218898,
      "pinball_loss_p90": 0.856142254384789,
      "position": "TE",
      "prediction_season": 2020,
      "projection_tier": "all",
      "rows": 224,
      "target_name": "games_active"
    },
    {
      "candidate_name": "hist_gradient_boosting",
      "empirical_coverage_p10_p90": 0.8392857142857143,
      "evaluation_scope": "validation",
      "mean_interval_width_p10_p90": 12.969204376254977,
      "pinball_loss_p10": 1.329887444444801,
      "pinball_loss_p50": 2.2117969237231767,
      "pinball_loss_p90": 0.6058076279498393,
      "position": "TE",
      "prediction_season": 2020,
      "projection_tier": "top",
      "rows": 56,
      "target_name": "games_active"
    },
    {
      "candidate_name": "hist_gradient_boosting",
      "empirical_coverage_p10_p90": 0.8035714285714286,
      "evaluation_scope": "validation",
      "mean_interval_width_p10_p90": 11.69892705428873,
      "pinball_loss_p10": 0.5794184625335969,
      "pinball_loss_p50": 2.2331755196289573,
      "pinball_loss_p90": 1.0382257977335207,
      "position": "TE",
      "prediction_season": 2020,
      "projection_tier": "middle",
      "rows": 112,
      "target_name": "games_active"
    },
    {
      "candidate_name": "hist_gradient_boosting",
      "empirical_coverage_p10_p90": 0.9642857142857143,
      "evaluation_scope": "validation",
      "mean_interval_width_p10_p90": 7.443798545713845,
      "pinball_loss_p10": 0.048214285714285716,
      "pinball_loss_p50": 0.28132253390646733,
      "pinball_loss_p90": 0.742309794122275,
      "position": "TE",
      "prediction_season": 2020,
      "projection_tier": "lower",
      "rows": 56,
      "target_name": "games_active"
    },
    {
      "candidate_name": "hist_gradient_boosting",
      "empirical_coverage_p10_p90": 0.8165938864628821,
      "evaluation_scope": "validation",
      "mean_interval_width_p10_p90": 10.391578801931198,
      "pinball_loss_p10": 0.6504961367148511,
      "pinball_loss_p50": 1.7255761259157207,
      "pinball_loss_p90": 0.9496623971517442,
      "position": "TE",
      "prediction_season": 2021,
      "projection_tier": "all",
      "rows": 229,
      "target_name": "games_active"
    },
    {
      "candidate_name": "hist_gradient_boosting",
      "empirical_coverage_p10_p90": 0.9298245614035088,
      "evaluation_scope": "validation",
      "mean_interval_width_p10_p90": 11.802475141371724,
      "pinball_loss_p10": 1.119638416300561,
      "pinball_loss_p50": 1.901207065862149,
      "pinball_loss_p90": 0.5017543859649122,
      "position": "TE",
      "prediction_season": 2021,
      "projection_tier": "top",
      "rows": 57,
      "target_name": "games_active"
    },
    {
      "candidate_name": "hist_gradient_boosting",
      "empirical_coverage_p10_p90": 0.6695652173913044,
      "evaluation_scope": "validation",
      "mean_interval_width_p10_p90": 11.299143018640523,
      "pinball_loss_p10": 0.7377758745962515,
      "pinball_loss_p50": 2.475169309592239,
      "pinball_loss_p90": 1.2906068469887815,
      "position": "TE",
      "prediction_season": 2021,
      "projection_tier": "middle",
      "rows": 115,
      "target_name": "games_active"
    },
    {
      "candidate_name": "hist_gradient_boosting",
      "empirical_coverage_p10_p90": 1.0,
      "evaluation_scope": "validation",
      "mean_interval_width_p10_p90": 7.1496318498315095,
      "pinball_loss_p10": 0.005263157894736843,
      "pinball_loss_p50": 0.03760806100789775,
      "pinball_loss_p90": 0.709700027088414,
      "position": "TE",
      "prediction_season": 2021,
      "projection_tier": "lower",
      "rows": 57,
      "target_name": "games_active"
    },
    {
      "candidate_name": "hist_gradient_boosting",
      "empirical_coverage_p10_p90": 0.8034188034188035,
      "evaluation_scope": "validation",
      "mean_interval_width_p10_p90": 10.012648144223158,
      "pinball_loss_p10": 0.6853768999139414,
      "pinball_loss_p50": 1.6713470542406101,
      "pinball_loss_p90": 0.8041516481955187,
      "position": "TE",
      "prediction_season": 2022,
      "projection_tier": "all",
      "rows": 234,
      "target_name": "games_active"
    },
    {
      "candidate_name": "hist_gradient_boosting",
      "empirical_coverage_p10_p90": 0.8813559322033898,
      "evaluation_scope": "validation",
      "mean_interval_width_p10_p90": 11.004959170368528,
      "pinball_loss_p10": 1.2150056302263859,
      "pinball_loss_p50": 1.9735305470338937,
      "pinball_loss_p90": 0.46924745219493863,
      "position": "TE",
      "prediction_season": 2022,
      "projection_tier": "top",
      "rows": 59,
      "target_name": "games_active"
    },
    {
      "candidate_name": "hist_gradient_boosting",
      "empirical_coverage_p10_p90": 0.6637931034482759,
      "evaluation_scope": "validation",
      "mean_interval_width_p10_p90": 11.122581361853248,
      "pinball_loss_p10": 0.7620074344526336,
      "pinball_loss_p50": 2.3524556729789685,
      "pinball_loss_p90": 1.0382855372939666,
      "position": "TE",
      "prediction_season": 2022,
      "projection_tier": "middle",
      "rows": 116,
      "target_name": "games_active"
    },
    {
      "candidate_name": "hist_gradient_boosting",
      "empirical_coverage_p10_p90": 1.0,
      "evaluation_scope": "validation",
      "mean_interval_width_p10_p90": 6.838095537652527,
      "pinball_loss_p10": 0.005084745762711865,
      "pinball_loss_p50": 0.03003475172445139,
      "pinball_loss_p90": 0.6787248080025406,
      "position": "TE",
      "prediction_season": 2022,
      "projection_tier": "lower",
      "rows": 59,
      "target_name": "games_active"
    },
    {
      "candidate_name": "hist_gradient_boosting",
      "empirical_coverage_p10_p90": 0.8468085106382979,
      "evaluation_scope": "validation",
      "mean_interval_width_p10_p90": 9.543789117932375,
      "pinball_loss_p10": 0.5509845665878361,
      "pinball_loss_p50": 1.5010106290856535,
      "pinball_loss_p90": 0.7997783424553905,
      "position": "TE",
      "prediction_season": 2023,
      "projection_tier": "all",
      "rows": 235,
      "target_name": "games_active"
    },
    {
      "candidate_name": "hist_gradient_boosting",
      "empirical_coverage_p10_p90": 0.8813559322033898,
      "evaluation_scope": "validation",
      "mean_interval_width_p10_p90": 10.94327340597452,
      "pinball_loss_p10": 1.1164858463297351,
      "pinball_loss_p50": 1.9802978153377377,
      "pinball_loss_p90": 0.38438185041004624,
      "position": "TE",
      "prediction_season": 2023,
      "projection_tier": "top",
      "rows": 59,
      "target_name": "games_active"
    },
    {
      "candidate_name": "hist_gradient_boosting",
      "empirical_coverage_p10_p90": 0.7606837606837606,
      "evaluation_scope": "validation",
      "mean_interval_width_p10_p90": 10.34137884293771,
      "pinball_loss_p10": 0.5257154548263858,
      "pinball_loss_p50": 1.9258004720969868,
      "pinball_loss_p90": 1.033482596373085,
      "position": "TE",
      "prediction_season": 2023,
      "projection_tier": "middle",
      "rows": 117,
      "target_name": "games_active"
    },
    {
      "candidate_name": "hist_gradient_boosting",
      "empirical_coverage_p10_p90": 0.9830508474576272,
      "evaluation_scope": "validation",
      "mean_interval_width_p10_p90": 6.562643849794907,
      "pinball_loss_p10": 0.03559322033898305,
      "pinball_loss_p50": 0.1793435846585539,
      "pinball_loss_p90": 0.7517274157147988,
      "position": "TE",
      "prediction_season": 2023,
      "projection_tier": "lower",
      "rows": 59,
      "target_name": "games_active"
    },
    {
      "candidate_name": "hist_gradient_boosting",
      "empirical_coverage_p10_p90": 0.8559322033898306,
      "evaluation_scope": "validation",
      "mean_interval_width_p10_p90": 8.936799086604024,
      "pinball_loss_p10": 0.5647025109022815,
      "pinball_loss_p50": 1.5011695886675303,
      "pinball_loss_p90": 0.8697493146757893,
      "position": "TE",
      "prediction_season": 2024,
      "projection_tier": "all",
      "rows": 236,
      "target_name": "games_active"
    },
    {
      "candidate_name": "hist_gradient_boosting",
      "empirical_coverage_p10_p90": 0.9152542372881356,
      "evaluation_scope": "validation",
      "mean_interval_width_p10_p90": 10.262035904245637,
      "pinball_loss_p10": 1.015783824274789,
      "pinball_loss_p50": 1.869446336385838,
      "pinball_loss_p90": 0.3520105217731897,
      "position": "TE",
      "prediction_season": 2024,
      "projection_tier": "top",
      "rows": 59,
      "target_name": "games_active"
    },
    {
      "candidate_name": "hist_gradient_boosting",
      "empirical_coverage_p10_p90": 0.7627118644067796,
      "evaluation_scope": "validation",
      "mean_interval_width_p10_p90": 9.634969782438306,
      "pinball_loss_p10": 0.6113436181417446,
      "pinball_loss_p50": 2.0153995946674836,
      "pinball_loss_p90": 1.2158288387254708,
      "position": "TE",
      "prediction_season": 2024,
      "projection_tier": "middle",
      "rows": 118,
      "target_name": "games_active"
    },
    {
      "candidate_name": "hist_gradient_boosting",
      "empirical_coverage_p10_p90": 0.9830508474576272,
      "evaluation_scope": "validation",
      "mean_interval_width_p10_p90": 6.215220877293858,
      "pinball_loss_p10": 0.02033898305084746,
      "pinball_loss_p50": 0.10443282894931633,
      "pinball_loss_p90": 0.6953290594790257,
      "position": "TE",
      "prediction_season": 2024,
      "projection_tier": "lower",
      "rows": 59,
      "target_name": "games_active"
    }
  ],
  "empirical_not_guaranteed": true,
  "method": "training-only signed out-of-fold residual quantiles",
  "operational_center": "training_only_residual_adjusted_p50",
  "residual_rows": 706,
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
      "feature": "lag1_fantasy_points_total",
      "interpretation": "This explanation is associative, not causal; changing a feature here does not establish that the feature causes the prediction to change.",
      "method": "one_way_average_partial_dependence",
      "points": [
        {
          "average_prediction": 5.541511109130166,
          "feature_value": 0.0
        },
        {
          "average_prediction": 5.490591433694304,
          "feature_value": 15.898181818181818
        },
        {
          "average_prediction": 5.822719229829313,
          "feature_value": 31.796363636363637
        },
        {
          "average_prediction": 7.447495618240489,
          "feature_value": 47.694545454545455
        },
        {
          "average_prediction": 7.425876876490814,
          "feature_value": 63.592727272727274
        },
        {
          "average_prediction": 7.467357037946967,
          "feature_value": 79.4909090909091
        },
        {
          "average_prediction": 7.420531041509574,
          "feature_value": 95.38909090909091
        },
        {
          "average_prediction": 7.414313970666796,
          "feature_value": 111.28727272727272
        },
        {
          "average_prediction": 7.399078572909301,
          "feature_value": 127.18545454545455
        },
        {
          "average_prediction": 7.451873451061978,
          "feature_value": 143.08363636363637
        },
        {
          "average_prediction": 7.451873451061978,
          "feature_value": 158.9818181818182
        },
        {
          "average_prediction": 7.219979977105847,
          "feature_value": 174.88
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
          "average_prediction": 8.475586133738904,
          "feature_value": 0.0
        },
        {
          "average_prediction": 2.188945430678011,
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
          "average_prediction": 4.2537176863996455,
          "feature_value": 1.0
        },
        {
          "average_prediction": 4.41331894895488,
          "feature_value": 2.4545454545454546
        },
        {
          "average_prediction": 4.641300313516211,
          "feature_value": 3.909090909090909
        },
        {
          "average_prediction": 4.8075297253613085,
          "feature_value": 5.363636363636363
        },
        {
          "average_prediction": 4.892860165645975,
          "feature_value": 6.818181818181818
        },
        {
          "average_prediction": 4.954524666352203,
          "feature_value": 8.272727272727273
        },
        {
          "average_prediction": 4.957325559801008,
          "feature_value": 9.727272727272727
        },
        {
          "average_prediction": 6.027404766320773,
          "feature_value": 11.181818181818182
        },
        {
          "average_prediction": 6.576150847528488,
          "feature_value": 12.636363636363637
        },
        {
          "average_prediction": 6.608002532505128,
          "feature_value": 14.090909090909092
        },
        {
          "average_prediction": 6.919959646725418,
          "feature_value": 15.545454545454547
        },
        {
          "average_prediction": 7.98679325791908,
          "feature_value": 17.0
        }
      ],
      "response_status": "stable_numeric_grid"
    }
  ],
  "importance": [
    {
      "explanation_scope": "registered_final_artifact_descriptive_on_2025_training_rows",
      "feature": "missing_lag1",
      "importance_mean": 2.259048979824246,
      "importance_std": 0.1370590121235884,
      "rank": 1
    },
    {
      "explanation_scope": "registered_final_artifact_descriptive_on_2025_training_rows",
      "feature": "weighted_3yr_games_active",
      "importance_mean": 0.7049559401776706,
      "importance_std": 0.06220149551316099,
      "rank": 2
    },
    {
      "explanation_scope": "registered_final_artifact_descriptive_on_2025_training_rows",
      "feature": "lag1_fantasy_points_total",
      "importance_mean": 0.6100413664281699,
      "importance_std": 0.03197238710647892,
      "rank": 3
    },
    {
      "explanation_scope": "registered_final_artifact_descriptive_on_2025_training_rows",
      "feature": "age_at_cutoff",
      "importance_mean": 0.4139538673080031,
      "importance_std": 0.04364125903107814,
      "rank": 4
    },
    {
      "explanation_scope": "registered_final_artifact_descriptive_on_2025_training_rows",
      "feature": "lag1_games_active",
      "importance_mean": 0.3593861944225134,
      "importance_std": 0.021142788237689784,
      "rank": 5
    },
    {
      "explanation_scope": "registered_final_artifact_descriptive_on_2025_training_rows",
      "feature": "lag1_stat_games",
      "importance_mean": 0.20436109264275829,
      "importance_std": 0.015253668391744713,
      "rank": 6
    },
    {
      "explanation_scope": "registered_final_artifact_descriptive_on_2025_training_rows",
      "feature": "nfl_experience_years",
      "importance_mean": 0.20168385504045344,
      "importance_std": 0.02501393164240384,
      "rank": 7
    },
    {
      "explanation_scope": "registered_final_artifact_descriptive_on_2025_training_rows",
      "feature": "weighted_3yr_receptions_per_game",
      "importance_mean": 0.12930800843332096,
      "importance_std": 0.02373826449692577,
      "rank": 8
    },
    {
      "explanation_scope": "registered_final_artifact_descriptive_on_2025_training_rows",
      "feature": "weighted_3yr_fantasy_points_per_game",
      "importance_mean": 0.1054252593473283,
      "importance_std": 0.024135770266600864,
      "rank": 9
    },
    {
      "explanation_scope": "registered_final_artifact_descriptive_on_2025_training_rows",
      "feature": "team_changed_last_feature_season",
      "importance_mean": 0.0950095392314834,
      "importance_std": 0.00940761466324742,
      "rank": 10
    },
    {
      "explanation_scope": "registered_final_artifact_descriptive_on_2025_training_rows",
      "feature": "lag1_fantasy_points_per_game",
      "importance_mean": 0.07359965076436029,
      "importance_std": 0.021931829098821392,
      "rank": 11
    },
    {
      "explanation_scope": "registered_final_artifact_descriptive_on_2025_training_rows",
      "feature": "draft_pick",
      "importance_mean": 0.07293756795123932,
      "importance_std": 0.013348051032600774,
      "rank": 12
    },
    {
      "explanation_scope": "registered_final_artifact_descriptive_on_2025_training_rows",
      "feature": "height_inches",
      "importance_mean": 0.06543450471366627,
      "importance_std": 0.030326708557988837,
      "rank": 13
    },
    {
      "explanation_scope": "registered_final_artifact_descriptive_on_2025_training_rows",
      "feature": "weighted_3yr_receiving_yards_per_game",
      "importance_mean": 0.06446376509031645,
      "importance_std": 0.01235199495615387,
      "rank": 14
    },
    {
      "explanation_scope": "registered_final_artifact_descriptive_on_2025_training_rows",
      "feature": "weighted_3yr_fumbles_lost_per_game",
      "importance_mean": 0.06424253289540945,
      "importance_std": 0.02212429975412516,
      "rank": 15
    },
    {
      "explanation_scope": "registered_final_artifact_descriptive_on_2025_training_rows",
      "feature": "weighted_3yr_carries_per_game",
      "importance_mean": 0.06055132908144865,
      "importance_std": 0.01085645430088292,
      "rank": 16
    },
    {
      "explanation_scope": "registered_final_artifact_descriptive_on_2025_training_rows",
      "feature": "history_seasons",
      "importance_mean": 0.05183762305249262,
      "importance_std": 0.006518699116012974,
      "rank": 17
    },
    {
      "explanation_scope": "registered_final_artifact_descriptive_on_2025_training_rows",
      "feature": "weighted_3yr_receiving_tds_per_game",
      "importance_mean": 0.04869168642737361,
      "importance_std": 0.005996272975820154,
      "rank": 18
    },
    {
      "explanation_scope": "registered_final_artifact_descriptive_on_2025_training_rows",
      "feature": "previous_team",
      "importance_mean": 0.03844510874307705,
      "importance_std": 0.013420420338460805,
      "rank": 19
    },
    {
      "explanation_scope": "registered_final_artifact_descriptive_on_2025_training_rows",
      "feature": "weighted_3yr_targets_per_game",
      "importance_mean": 0.026476166213127338,
      "importance_std": 0.011813718538967467,
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

- Project-relative path: `models/artifacts/phase4-7ae8e9aed04bffca00c0/attempt-866987f75a2c406693cf892d49adc975/TE/games_active/hist_gradient_boosting.joblib`
- SHA-256: `9d9572eae316b768a170b077f5fd884f0b565815a78f5b24af48f582d9f071fc`

## Additional metadata

````json
{
  "publication_id": "attempt-866987f75a2c406693cf892d49adc975"
}
````
