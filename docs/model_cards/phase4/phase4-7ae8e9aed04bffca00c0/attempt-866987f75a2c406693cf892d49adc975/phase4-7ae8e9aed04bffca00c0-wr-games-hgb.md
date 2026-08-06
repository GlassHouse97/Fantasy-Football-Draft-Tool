# Model Card: phase4-7ae8e9aed04bffca00c0-wr-games-hgb

- Model ID: `phase4-7ae8e9aed04bffca00c0-wr-games-hgb`
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
  "position": "WR",
  "target_name": "games_active",
  "test_mae": 2.811914056655338,
  "test_rows": 433,
  "test_season": 2025,
  "validation_mae": 2.9177447114825092,
  "validation_rows": 2101,
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
    "candidate_mae": 2.9177447114825092,
    "ci95_lower": -3.2568108709171186,
    "ci95_upper": -2.789372956939834,
    "direction": "candidate_lower_mae",
    "mae_difference_candidate_minus_reference": -3.0211359344260806,
    "n_resamples": 2000,
    "reference_mae": 5.93888064590859,
    "rows": 2101,
    "seed": 42
  },
  "decision_status": "learned_significant_improvement_selected",
  "learned_improvement_status": "statistically_clear",
  "reference_metrics": {
    "candidate_name": "age_position_adjusted",
    "candidate_source": "baseline",
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
      "empirical_coverage_p10_p90": 0.7944572748267898,
      "evaluation_scope": "test",
      "mean_interval_width_p10_p90": 7.94306229262854,
      "pinball_loss_p10": 0.5688424537549025,
      "pinball_loss_p50": 1.405957028327669,
      "pinball_loss_p90": 0.866126445716123,
      "position": "WR",
      "prediction_season": 2025,
      "projection_tier": "all",
      "rows": 433,
      "target_name": "games_active"
    },
    {
      "candidate_name": "hist_gradient_boosting",
      "empirical_coverage_p10_p90": 0.7614678899082569,
      "evaluation_scope": "test",
      "mean_interval_width_p10_p90": 9.37498611798127,
      "pinball_loss_p10": 1.1483899870709031,
      "pinball_loss_p50": 1.9151058161124985,
      "pinball_loss_p90": 0.5476239868853989,
      "position": "WR",
      "prediction_season": 2025,
      "projection_tier": "top",
      "rows": 109,
      "target_name": "games_active"
    },
    {
      "candidate_name": "hist_gradient_boosting",
      "empirical_coverage_p10_p90": 0.7162790697674418,
      "evaluation_scope": "test",
      "mean_interval_width_p10_p90": 8.363301688705336,
      "pinball_loss_p10": 0.548066390163462,
      "pinball_loss_p50": 1.7835544659570868,
      "pinball_loss_p90": 1.1403032705920562,
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
      "mean_interval_width_p10_p90": 5.682225897032593,
      "pinball_loss_p10": 0.030275229357798167,
      "pinball_loss_p50": 0.15200595531050312,
      "pinball_loss_p90": 0.6438214059383549,
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
      "empirical_coverage_p10_p90": 0.80622009569378,
      "evaluation_scope": "validation",
      "mean_interval_width_p10_p90": 8.531698246505039,
      "pinball_loss_p10": 0.6068523965731416,
      "pinball_loss_p50": 1.5685440542889468,
      "pinball_loss_p90": 0.9585001373820629,
      "position": "WR",
      "prediction_season": 2021,
      "projection_tier": "all",
      "rows": 418,
      "target_name": "games_active"
    },
    {
      "candidate_name": "hist_gradient_boosting",
      "empirical_coverage_p10_p90": 0.8095238095238095,
      "evaluation_scope": "validation",
      "mean_interval_width_p10_p90": 10.210216391967256,
      "pinball_loss_p10": 1.2496594779496581,
      "pinball_loss_p50": 2.140891698866232,
      "pinball_loss_p90": 0.5242804280439193,
      "position": "WR",
      "prediction_season": 2021,
      "projection_tier": "top",
      "rows": 105,
      "target_name": "games_active"
    },
    {
      "candidate_name": "hist_gradient_boosting",
      "empirical_coverage_p10_p90": 0.7211538461538461,
      "evaluation_scope": "validation",
      "mean_interval_width_p10_p90": 8.993493962581788,
      "pinball_loss_p10": 0.5680291181868224,
      "pinball_loss_p50": 1.9677744697661308,
      "pinball_loss_p90": 1.307086714379565,
      "position": "WR",
      "prediction_season": 2021,
      "projection_tier": "middle",
      "rows": 208,
      "target_name": "games_active"
    },
    {
      "candidate_name": "hist_gradient_boosting",
      "empirical_coverage_p10_p90": 0.9714285714285714,
      "evaluation_scope": "validation",
      "mean_interval_width_p10_p90": 5.938384777766982,
      "pinball_loss_p10": 0.04095238095238095,
      "pinball_loss_p50": 0.2053399676235258,
      "pinball_loss_p90": 0.702186437048964,
      "position": "WR",
      "prediction_season": 2021,
      "projection_tier": "lower",
      "rows": 105,
      "target_name": "games_active"
    },
    {
      "candidate_name": "hist_gradient_boosting",
      "empirical_coverage_p10_p90": 0.7953488372093023,
      "evaluation_scope": "validation",
      "mean_interval_width_p10_p90": 8.540705632204048,
      "pinball_loss_p10": 0.6422291266089325,
      "pinball_loss_p50": 1.510513691307224,
      "pinball_loss_p90": 0.8450800580367986,
      "position": "WR",
      "prediction_season": 2022,
      "projection_tier": "all",
      "rows": 430,
      "target_name": "games_active"
    },
    {
      "candidate_name": "hist_gradient_boosting",
      "empirical_coverage_p10_p90": 0.7592592592592593,
      "evaluation_scope": "validation",
      "mean_interval_width_p10_p90": 9.882072801494362,
      "pinball_loss_p10": 1.4042420902136667,
      "pinball_loss_p50": 2.195581206724621,
      "pinball_loss_p90": 0.5454836112612947,
      "position": "WR",
      "prediction_season": 2022,
      "projection_tier": "top",
      "rows": 108,
      "target_name": "games_active"
    },
    {
      "candidate_name": "hist_gradient_boosting",
      "empirical_coverage_p10_p90": 0.7162790697674418,
      "evaluation_scope": "validation",
      "mean_interval_width_p10_p90": 9.138313896923103,
      "pinball_loss_p10": 0.5748854823198372,
      "pinball_loss_p50": 1.8941716247486515,
      "pinball_loss_p90": 1.1093914763394883,
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
      "mean_interval_width_p10_p90": 5.9860006677372155,
      "pinball_loss_p10": 0.008411214953271028,
      "pinball_loss_p50": 0.04814222069987954,
      "pinball_loss_p90": 0.6163834348281645,
      "position": "WR",
      "prediction_season": 2022,
      "projection_tier": "lower",
      "rows": 107,
      "target_name": "games_active"
    },
    {
      "candidate_name": "hist_gradient_boosting",
      "empirical_coverage_p10_p90": 0.7961630695443646,
      "evaluation_scope": "validation",
      "mean_interval_width_p10_p90": 8.435716794830611,
      "pinball_loss_p10": 0.5455768419776195,
      "pinball_loss_p50": 1.4623445889588718,
      "pinball_loss_p90": 0.8468587042413687,
      "position": "WR",
      "prediction_season": 2023,
      "projection_tier": "all",
      "rows": 417,
      "target_name": "games_active"
    },
    {
      "candidate_name": "hist_gradient_boosting",
      "empirical_coverage_p10_p90": 0.819047619047619,
      "evaluation_scope": "validation",
      "mean_interval_width_p10_p90": 9.980083510312387,
      "pinball_loss_p10": 1.0443043101122533,
      "pinball_loss_p50": 1.902362516837494,
      "pinball_loss_p90": 0.4633453460897707,
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
      "mean_interval_width_p10_p90": 8.889542625149288,
      "pinball_loss_p10": 0.5526614929946188,
      "pinball_loss_p50": 1.8938478817411146,
      "pinball_loss_p90": 1.1653344514905304,
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
      "mean_interval_width_p10_p90": 5.968848738754928,
      "pinball_loss_p10": 0.02788461538461539,
      "pinball_loss_p50": 0.15508913390154616,
      "pinball_loss_p90": 0.5971081963384087,
      "position": "WR",
      "prediction_season": 2023,
      "projection_tier": "lower",
      "rows": 104,
      "target_name": "games_active"
    },
    {
      "candidate_name": "hist_gradient_boosting",
      "empirical_coverage_p10_p90": 0.8278301886792453,
      "evaluation_scope": "validation",
      "mean_interval_width_p10_p90": 8.27200042919025,
      "pinball_loss_p10": 0.5460469916802864,
      "pinball_loss_p50": 1.3521015674508616,
      "pinball_loss_p90": 0.7939942851387511,
      "position": "WR",
      "prediction_season": 2024,
      "projection_tier": "all",
      "rows": 424,
      "target_name": "games_active"
    },
    {
      "candidate_name": "hist_gradient_boosting",
      "empirical_coverage_p10_p90": 0.8301886792452831,
      "evaluation_scope": "validation",
      "mean_interval_width_p10_p90": 9.38283740065716,
      "pinball_loss_p10": 1.1282733396090978,
      "pinball_loss_p50": 1.859738596185435,
      "pinball_loss_p90": 0.45577236637837676,
      "position": "WR",
      "prediction_season": 2024,
      "projection_tier": "top",
      "rows": 106,
      "target_name": "games_active"
    },
    {
      "candidate_name": "hist_gradient_boosting",
      "empirical_coverage_p10_p90": 0.7405660377358491,
      "evaluation_scope": "validation",
      "mean_interval_width_p10_p90": 8.798894834893668,
      "pinball_loss_p10": 0.5227686343107409,
      "pinball_loss_p50": 1.7372258245640106,
      "pinball_loss_p90": 1.059922334017772,
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
      "mean_interval_width_p10_p90": 6.1073746463165035,
      "pinball_loss_p10": 0.010377358490566039,
      "pinball_loss_p50": 0.07421602448999012,
      "pinball_loss_p90": 0.6003601061410843,
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
          "average_prediction": 4.4789414565879335,
          "feature_value": 0.0
        },
        {
          "average_prediction": 4.699689368759872,
          "feature_value": 21.884090909090908
        },
        {
          "average_prediction": 5.261138968618732,
          "feature_value": 43.768181818181816
        },
        {
          "average_prediction": 8.524717631684306,
          "feature_value": 65.65227272727273
        },
        {
          "average_prediction": 8.56960425589658,
          "feature_value": 87.53636363636363
        },
        {
          "average_prediction": 9.091068815524642,
          "feature_value": 109.42045454545453
        },
        {
          "average_prediction": 9.28356771874555,
          "feature_value": 131.30454545454546
        },
        {
          "average_prediction": 9.285017933981994,
          "feature_value": 153.18863636363636
        },
        {
          "average_prediction": 9.920568117674728,
          "feature_value": 175.07272727272726
        },
        {
          "average_prediction": 10.31919485473674,
          "feature_value": 196.95681818181816
        },
        {
          "average_prediction": 10.31919485473674,
          "feature_value": 218.84090909090907
        },
        {
          "average_prediction": 10.31919485473674,
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
          "average_prediction": 6.46262489878047,
          "feature_value": 0.0
        },
        {
          "average_prediction": 3.950415236332024,
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
          "average_prediction": 3.9666405137074454,
          "feature_value": 1.4900000000000009
        },
        {
          "average_prediction": 3.995582895769027,
          "feature_value": 2.900000000000001
        },
        {
          "average_prediction": 4.01196835454022,
          "feature_value": 4.3100000000000005
        },
        {
          "average_prediction": 4.305375840821134,
          "feature_value": 5.720000000000001
        },
        {
          "average_prediction": 4.453337904405035,
          "feature_value": 7.130000000000001
        },
        {
          "average_prediction": 4.392400834897592,
          "feature_value": 8.540000000000001
        },
        {
          "average_prediction": 4.780644987165402,
          "feature_value": 9.95
        },
        {
          "average_prediction": 5.094512978397162,
          "feature_value": 11.36
        },
        {
          "average_prediction": 5.504744398144143,
          "feature_value": 12.77
        },
        {
          "average_prediction": 5.5388952154882665,
          "feature_value": 14.18
        },
        {
          "average_prediction": 5.80008051763822,
          "feature_value": 15.59
        },
        {
          "average_prediction": 6.648928782619419,
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
      "importance_mean": 1.117051606962098,
      "importance_std": 0.0790997136294715,
      "rank": 1
    },
    {
      "explanation_scope": "registered_final_artifact_descriptive_on_2025_training_rows",
      "feature": "missing_lag1",
      "importance_mean": 0.7600562689384168,
      "importance_std": 0.02507192950459701,
      "rank": 2
    },
    {
      "explanation_scope": "registered_final_artifact_descriptive_on_2025_training_rows",
      "feature": "weighted_3yr_games_active",
      "importance_mean": 0.3538329183474363,
      "importance_std": 0.0675603920749537,
      "rank": 3
    },
    {
      "explanation_scope": "registered_final_artifact_descriptive_on_2025_training_rows",
      "feature": "age_at_cutoff",
      "importance_mean": 0.32877634744021106,
      "importance_std": 0.0401003268191462,
      "rank": 4
    },
    {
      "explanation_scope": "registered_final_artifact_descriptive_on_2025_training_rows",
      "feature": "lag1_fantasy_points_per_game",
      "importance_mean": 0.3276385513176119,
      "importance_std": 0.03838490035252866,
      "rank": 5
    },
    {
      "explanation_scope": "registered_final_artifact_descriptive_on_2025_training_rows",
      "feature": "lag1_games_active",
      "importance_mean": 0.15839903091574667,
      "importance_std": 0.02498389250637577,
      "rank": 6
    },
    {
      "explanation_scope": "registered_final_artifact_descriptive_on_2025_training_rows",
      "feature": "weighted_3yr_receiving_tds_per_game",
      "importance_mean": 0.1273554891392094,
      "importance_std": 0.016132835303307967,
      "rank": 7
    },
    {
      "explanation_scope": "registered_final_artifact_descriptive_on_2025_training_rows",
      "feature": "weighted_3yr_targets_per_game",
      "importance_mean": 0.10556895373007205,
      "importance_std": 0.012433302420268463,
      "rank": 8
    },
    {
      "explanation_scope": "registered_final_artifact_descriptive_on_2025_training_rows",
      "feature": "weighted_3yr_receiving_yards_per_game",
      "importance_mean": 0.10002343974467606,
      "importance_std": 0.010569448280476056,
      "rank": 9
    },
    {
      "explanation_scope": "registered_final_artifact_descriptive_on_2025_training_rows",
      "feature": "weighted_3yr_rushing_yards_per_game",
      "importance_mean": 0.08924966305135155,
      "importance_std": 0.009639138390339051,
      "rank": 10
    },
    {
      "explanation_scope": "registered_final_artifact_descriptive_on_2025_training_rows",
      "feature": "previous_team",
      "importance_mean": 0.08743676852111237,
      "importance_std": 0.006513702796641499,
      "rank": 11
    },
    {
      "explanation_scope": "registered_final_artifact_descriptive_on_2025_training_rows",
      "feature": "weighted_3yr_fantasy_points_per_game",
      "importance_mean": 0.07310439294137225,
      "importance_std": 0.006588335613436123,
      "rank": 12
    },
    {
      "explanation_scope": "registered_final_artifact_descriptive_on_2025_training_rows",
      "feature": "draft_pick",
      "importance_mean": 0.04562745190857935,
      "importance_std": 0.010179196035840119,
      "rank": 13
    },
    {
      "explanation_scope": "registered_final_artifact_descriptive_on_2025_training_rows",
      "feature": "weighted_3yr_carries_per_game",
      "importance_mean": 0.03978244039328862,
      "importance_std": 0.005485115883908252,
      "rank": 14
    },
    {
      "explanation_scope": "registered_final_artifact_descriptive_on_2025_training_rows",
      "feature": "weighted_3yr_receptions_per_game",
      "importance_mean": 0.034959266643705966,
      "importance_std": 0.0017672220877960137,
      "rank": 15
    },
    {
      "explanation_scope": "registered_final_artifact_descriptive_on_2025_training_rows",
      "feature": "weighted_3yr_rushing_tds_per_game",
      "importance_mean": 0.026162134938048354,
      "importance_std": 0.0072696950661638145,
      "rank": 16
    },
    {
      "explanation_scope": "registered_final_artifact_descriptive_on_2025_training_rows",
      "feature": "height_inches",
      "importance_mean": 0.020606810186787693,
      "importance_std": 0.004404310637559419,
      "rank": 17
    },
    {
      "explanation_scope": "registered_final_artifact_descriptive_on_2025_training_rows",
      "feature": "weighted_3yr_passing_yards_per_game",
      "importance_mean": 0.018976801898001307,
      "importance_std": 0.007692476948513968,
      "rank": 18
    },
    {
      "explanation_scope": "registered_final_artifact_descriptive_on_2025_training_rows",
      "feature": "lag1_stat_games",
      "importance_mean": 0.017336628379595265,
      "importance_std": 0.003035526205859623,
      "rank": 19
    },
    {
      "explanation_scope": "registered_final_artifact_descriptive_on_2025_training_rows",
      "feature": "nfl_experience_years",
      "importance_mean": 0.0153582255110865,
      "importance_std": 0.003948424255290215,
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

- Project-relative path: `models/artifacts/phase4-7ae8e9aed04bffca00c0/attempt-866987f75a2c406693cf892d49adc975/WR/games_active/hist_gradient_boosting.joblib`
- SHA-256: `91c085399b4db831eae32f27b1dfb356fc2168cb262bfdab718c52dcacdad3ba`

## Additional metadata

````json
{
  "publication_id": "attempt-866987f75a2c406693cf892d49adc975"
}
````
