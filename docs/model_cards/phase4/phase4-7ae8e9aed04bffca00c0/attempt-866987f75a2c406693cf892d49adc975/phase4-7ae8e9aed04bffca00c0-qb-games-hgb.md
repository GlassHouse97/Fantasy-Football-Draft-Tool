# Model Card: phase4-7ae8e9aed04bffca00c0-qb-games-hgb

- Model ID: `phase4-7ae8e9aed04bffca00c0-qb-games-hgb`
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
  "position": "QB",
  "target_name": "games_active",
  "test_mae": 2.2957293502981004,
  "test_rows": 124,
  "test_season": 2025,
  "validation_mae": 2.541974044856945,
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
    "candidate_mae": 2.4652391334952553,
    "ci95_lower": -1.899658718397371,
    "ci95_upper": -1.3580031455871684,
    "direction": "candidate_lower_mae",
    "mae_difference_candidate_minus_reference": -1.6253974299508505,
    "n_resamples": 2000,
    "reference_mae": 4.090636563446106,
    "rows": 618,
    "seed": 42
  },
  "decision_status": "learned_significant_improvement_selected",
  "learned_improvement_status": "statistically_clear",
  "reference_metrics": {
    "candidate_name": "age_position_adjusted",
    "candidate_source": "baseline",
    "position": "QB",
    "target_name": "games_active",
    "test_mae": 4.063549748196543,
    "test_rows": 124,
    "test_season": 2025,
    "validation_mae": 4.090636563446106,
    "validation_rows": 618,
    "validation_seasons": [
      2020,
      2021,
      2022,
      2023,
      2024
    ]
  },
  "selected_champion": "ridge",
  "selected_source": "learned",
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
      "empirical_coverage_p10_p90": 0.782258064516129,
      "evaluation_scope": "test",
      "mean_interval_width_p10_p90": 6.875816188253565,
      "pinball_loss_p10": 0.46723831658352,
      "pinball_loss_p50": 1.1478646751490502,
      "pinball_loss_p90": 0.6757310046066713,
      "position": "QB",
      "prediction_season": 2025,
      "projection_tier": "all",
      "rows": 124,
      "target_name": "games_active"
    },
    {
      "candidate_name": "hist_gradient_boosting",
      "empirical_coverage_p10_p90": 0.5161290322580645,
      "evaluation_scope": "test",
      "mean_interval_width_p10_p90": 8.09301413588014,
      "pinball_loss_p10": 1.128361319138409,
      "pinball_loss_p50": 2.1575696039265435,
      "pinball_loss_p90": 0.8583763058904045,
      "position": "QB",
      "prediction_season": 2025,
      "projection_tier": "top",
      "rows": 31,
      "target_name": "games_active"
    },
    {
      "candidate_name": "hist_gradient_boosting",
      "empirical_coverage_p10_p90": 0.8064516129032258,
      "evaluation_scope": "test",
      "mean_interval_width_p10_p90": 7.3621723641098535,
      "pinball_loss_p10": 0.36868307037202896,
      "pinball_loss_p50": 1.2011313908720769,
      "pinball_loss_p90": 0.6895914650482267,
      "position": "QB",
      "prediction_season": 2025,
      "projection_tier": "middle",
      "rows": 62,
      "target_name": "games_active"
    },
    {
      "candidate_name": "hist_gradient_boosting",
      "empirical_coverage_p10_p90": 1.0,
      "evaluation_scope": "test",
      "mean_interval_width_p10_p90": 4.685905888914408,
      "pinball_loss_p10": 0.0032258064516129032,
      "pinball_loss_p50": 0.03162631492550399,
      "pinball_loss_p90": 0.4653647824398278,
      "position": "QB",
      "prediction_season": 2025,
      "projection_tier": "lower",
      "rows": 31,
      "target_name": "games_active"
    },
    {
      "candidate_name": "hist_gradient_boosting",
      "empirical_coverage_p10_p90": 0.8403361344537815,
      "evaluation_scope": "validation",
      "mean_interval_width_p10_p90": 6.871805589136354,
      "pinball_loss_p10": 0.40473068982109783,
      "pinball_loss_p50": 1.2200282727078327,
      "pinball_loss_p90": 0.6903922895729098,
      "position": "QB",
      "prediction_season": 2020,
      "projection_tier": "all",
      "rows": 119,
      "target_name": "games_active"
    },
    {
      "candidate_name": "hist_gradient_boosting",
      "empirical_coverage_p10_p90": 0.7666666666666667,
      "evaluation_scope": "validation",
      "mean_interval_width_p10_p90": 9.192501728859495,
      "pinball_loss_p10": 0.8976380370276638,
      "pinball_loss_p50": 1.6496762866981773,
      "pinball_loss_p90": 0.6575401456632157,
      "position": "QB",
      "prediction_season": 2020,
      "projection_tier": "top",
      "rows": 30,
      "target_name": "games_active"
    },
    {
      "candidate_name": "hist_gradient_boosting",
      "empirical_coverage_p10_p90": 0.8135593220338984,
      "evaluation_scope": "validation",
      "mean_interval_width_p10_p90": 7.029037617913954,
      "pinball_loss_p10": 0.33108154199797873,
      "pinball_loss_p50": 1.4778487432421485,
      "pinball_loss_p90": 0.8508028303951011,
      "position": "QB",
      "prediction_season": 2020,
      "projection_tier": "middle",
      "rows": 59,
      "target_name": "games_active"
    },
    {
      "candidate_name": "hist_gradient_boosting",
      "empirical_coverage_p10_p90": 0.9666666666666667,
      "evaluation_scope": "validation",
      "mean_interval_width_p10_p90": 4.24188645948393,
      "pinball_loss_p10": 0.05666666666666667,
      "pinball_loss_p50": 0.2833333333333333,
      "pinball_loss_p90": 0.4077703698656278,
      "position": "QB",
      "prediction_season": 2020,
      "projection_tier": "lower",
      "rows": 30,
      "target_name": "games_active"
    },
    {
      "candidate_name": "hist_gradient_boosting",
      "empirical_coverage_p10_p90": 0.808,
      "evaluation_scope": "validation",
      "mean_interval_width_p10_p90": 6.685168718305998,
      "pinball_loss_p10": 0.5619869631833296,
      "pinball_loss_p50": 1.196092651428148,
      "pinball_loss_p90": 0.6285512186281356,
      "position": "QB",
      "prediction_season": 2021,
      "projection_tier": "all",
      "rows": 125,
      "target_name": "games_active"
    },
    {
      "candidate_name": "hist_gradient_boosting",
      "empirical_coverage_p10_p90": 0.5483870967741935,
      "evaluation_scope": "validation",
      "mean_interval_width_p10_p90": 8.530377587112039,
      "pinball_loss_p10": 1.6487300511490521,
      "pinball_loss_p50": 2.302461084855513,
      "pinball_loss_p90": 0.7125986537731575,
      "position": "QB",
      "prediction_season": 2021,
      "projection_tier": "top",
      "rows": 31,
      "target_name": "games_active"
    },
    {
      "candidate_name": "hist_gradient_boosting",
      "empirical_coverage_p10_p90": 0.873015873015873,
      "evaluation_scope": "validation",
      "mean_interval_width_p10_p90": 6.9072988310001,
      "pinball_loss_p10": 0.276789504957073,
      "pinball_loss_p50": 1.1048240960110014,
      "pinball_loss_p90": 0.6768678038781661,
      "position": "QB",
      "prediction_season": 2021,
      "projection_tier": "middle",
      "rows": 63,
      "target_name": "games_active"
    },
    {
      "candidate_name": "hist_gradient_boosting",
      "empirical_coverage_p10_p90": 0.9354838709677419,
      "evaluation_scope": "validation",
      "mean_interval_width_p10_p90": 4.388534136605497,
      "pinball_loss_p10": 0.05483870967741936,
      "pinball_loss_p50": 0.2752054757840179,
      "pinball_loss_p90": 0.446312013458858,
      "position": "QB",
      "prediction_season": 2021,
      "projection_tier": "lower",
      "rows": 31,
      "target_name": "games_active"
    },
    {
      "candidate_name": "hist_gradient_boosting",
      "empirical_coverage_p10_p90": 0.84,
      "evaluation_scope": "validation",
      "mean_interval_width_p10_p90": 6.915010296008263,
      "pinball_loss_p10": 0.37314328836479166,
      "pinball_loss_p50": 1.120104221392106,
      "pinball_loss_p90": 0.654690110823182,
      "position": "QB",
      "prediction_season": 2022,
      "projection_tier": "all",
      "rows": 125,
      "target_name": "games_active"
    },
    {
      "candidate_name": "hist_gradient_boosting",
      "empirical_coverage_p10_p90": 0.6774193548387096,
      "evaluation_scope": "validation",
      "mean_interval_width_p10_p90": 8.303006665447336,
      "pinball_loss_p10": 0.7535376282290925,
      "pinball_loss_p50": 1.7168685918595397,
      "pinball_loss_p90": 0.5029562743807668,
      "position": "QB",
      "prediction_season": 2022,
      "projection_tier": "top",
      "rows": 31,
      "target_name": "games_active"
    },
    {
      "candidate_name": "hist_gradient_boosting",
      "empirical_coverage_p10_p90": 0.8571428571428571,
      "evaluation_scope": "validation",
      "mean_interval_width_p10_p90": 7.334196921110865,
      "pinball_loss_p10": 0.35052769159519176,
      "pinball_loss_p50": 1.26303405254627,
      "pinball_loss_p90": 0.8368975522904529,
      "position": "QB",
      "prediction_season": 2022,
      "projection_tier": "middle",
      "rows": 63,
      "target_name": "games_active"
    },
    {
      "candidate_name": "hist_gradient_boosting",
      "empirical_coverage_p10_p90": 0.967741935483871,
      "evaluation_scope": "validation",
      "mean_interval_width_p10_p90": 4.67511852716714,
      "pinball_loss_p10": 0.03870967741935485,
      "pinball_loss_p50": 0.2328695489016923,
      "pinball_loss_p90": 0.4361314049288844,
      "position": "QB",
      "prediction_season": 2022,
      "projection_tier": "lower",
      "rows": 31,
      "target_name": "games_active"
    },
    {
      "candidate_name": "hist_gradient_boosting",
      "empirical_coverage_p10_p90": 0.7096774193548387,
      "evaluation_scope": "validation",
      "mean_interval_width_p10_p90": 6.596241688293825,
      "pinball_loss_p10": 0.7117153915820119,
      "pinball_loss_p50": 1.537188387247063,
      "pinball_loss_p90": 0.9050693411289966,
      "position": "QB",
      "prediction_season": 2023,
      "projection_tier": "all",
      "rows": 124,
      "target_name": "games_active"
    },
    {
      "candidate_name": "hist_gradient_boosting",
      "empirical_coverage_p10_p90": 0.5161290322580645,
      "evaluation_scope": "validation",
      "mean_interval_width_p10_p90": 7.466413208643343,
      "pinball_loss_p10": 1.918121572215624,
      "pinball_loss_p50": 2.618097906800601,
      "pinball_loss_p90": 0.9500439878141997,
      "position": "QB",
      "prediction_season": 2023,
      "projection_tier": "top",
      "rows": 31,
      "target_name": "games_active"
    },
    {
      "candidate_name": "hist_gradient_boosting",
      "empirical_coverage_p10_p90": 0.6935483870967742,
      "evaluation_scope": "validation",
      "mean_interval_width_p10_p90": 7.1629969669638145,
      "pinball_loss_p10": 0.4288861260884703,
      "pinball_loss_p50": 1.5667921713962676,
      "pinball_loss_p90": 1.1012778741916294,
      "position": "QB",
      "prediction_season": 2023,
      "projection_tier": "middle",
      "rows": 62,
      "target_name": "games_active"
    },
    {
      "candidate_name": "hist_gradient_boosting",
      "empirical_coverage_p10_p90": 0.9354838709677419,
      "evaluation_scope": "validation",
      "mean_interval_width_p10_p90": 4.592559610604328,
      "pinball_loss_p10": 0.07096774193548387,
      "pinball_loss_p50": 0.3970712993951155,
      "pinball_loss_p90": 0.46767762831852827,
      "position": "QB",
      "prediction_season": 2023,
      "projection_tier": "lower",
      "rows": 31,
      "target_name": "games_active"
    },
    {
      "candidate_name": "hist_gradient_boosting",
      "empirical_coverage_p10_p90": 0.784,
      "evaluation_scope": "validation",
      "mean_interval_width_p10_p90": 6.8390242670833805,
      "pinball_loss_p10": 0.5576918118866011,
      "pinball_loss_p50": 1.2812051702991716,
      "pinball_loss_p90": 0.6947712414698322,
      "position": "QB",
      "prediction_season": 2024,
      "projection_tier": "all",
      "rows": 125,
      "target_name": "games_active"
    },
    {
      "candidate_name": "hist_gradient_boosting",
      "empirical_coverage_p10_p90": 0.5806451612903226,
      "evaluation_scope": "validation",
      "mean_interval_width_p10_p90": 7.758469299056417,
      "pinball_loss_p10": 1.3625725581390165,
      "pinball_loss_p50": 2.1188105440282974,
      "pinball_loss_p90": 0.6269989239793079,
      "position": "QB",
      "prediction_season": 2024,
      "projection_tier": "top",
      "rows": 31,
      "target_name": "games_active"
    },
    {
      "candidate_name": "hist_gradient_boosting",
      "empirical_coverage_p10_p90": 0.7936507936507936,
      "evaluation_scope": "validation",
      "mean_interval_width_p10_p90": 7.327915185329653,
      "pinball_loss_p10": 0.4154242410081844,
      "pinball_loss_p50": 1.3793505221706002,
      "pinball_loss_p90": 0.8388182638054122,
      "position": "QB",
      "prediction_season": 2024,
      "projection_tier": "middle",
      "rows": 63,
      "target_name": "games_active"
    },
    {
      "candidate_name": "hist_gradient_boosting",
      "empirical_coverage_p10_p90": 0.967741935483871,
      "evaluation_scope": "validation",
      "mean_interval_width_p10_p90": 4.9260267238356565,
      "pinball_loss_p10": 0.041935483870967745,
      "pinball_loss_p50": 0.2441431137345622,
      "pinball_loss_p90": 0.4698028361493388,
      "position": "QB",
      "prediction_season": 2024,
      "projection_tier": "lower",
      "rows": 31,
      "target_name": "games_active"
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
      "feature": "lag1_fantasy_points_total",
      "interpretation": "This explanation is associative, not causal; changing a feature here does not establish that the feature causes the prediction to change.",
      "method": "one_way_average_partial_dependence",
      "points": [
        {
          "average_prediction": 3.875663591600949,
          "feature_value": -0.2
        },
        {
          "average_prediction": 3.743871224306823,
          "feature_value": 32.25618181818181
        },
        {
          "average_prediction": 3.6155589861914796,
          "feature_value": 64.71236363636362
        },
        {
          "average_prediction": 5.533319900650784,
          "feature_value": 97.16854545454542
        },
        {
          "average_prediction": 6.376466724311928,
          "feature_value": 129.62472727272726
        },
        {
          "average_prediction": 6.485052487985231,
          "feature_value": 162.08090909090907
        },
        {
          "average_prediction": 6.4978042725200265,
          "feature_value": 194.53709090909086
        },
        {
          "average_prediction": 8.426812102400659,
          "feature_value": 226.99327272727268
        },
        {
          "average_prediction": 8.578967672471107,
          "feature_value": 259.4494545454545
        },
        {
          "average_prediction": 8.553872947165027,
          "feature_value": 291.9056363636363
        },
        {
          "average_prediction": 8.553872947165027,
          "feature_value": 324.36181818181814
        },
        {
          "average_prediction": 8.553872947165027,
          "feature_value": 356.8179999999999
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
          "average_prediction": 5.19150713854616,
          "feature_value": 0.0
        },
        {
          "average_prediction": 3.9088063357024594,
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
          "average_prediction": 4.057680082279656,
          "feature_value": 1.3300000000000005
        },
        {
          "average_prediction": 4.057680082279656,
          "feature_value": 2.725454545454546
        },
        {
          "average_prediction": 4.113871279167657,
          "feature_value": 4.120909090909091
        },
        {
          "average_prediction": 4.205918015598535,
          "feature_value": 5.5163636363636375
        },
        {
          "average_prediction": 4.250921538045875,
          "feature_value": 6.911818181818182
        },
        {
          "average_prediction": 4.618059611461116,
          "feature_value": 8.307272727272728
        },
        {
          "average_prediction": 4.587640995475473,
          "feature_value": 9.702727272727273
        },
        {
          "average_prediction": 5.13696203323354,
          "feature_value": 11.09818181818182
        },
        {
          "average_prediction": 6.159931519385617,
          "feature_value": 12.493636363636364
        },
        {
          "average_prediction": 5.883948600344147,
          "feature_value": 13.889090909090909
        },
        {
          "average_prediction": 6.336262920592938,
          "feature_value": 15.284545454545455
        },
        {
          "average_prediction": 6.390964279158236,
          "feature_value": 16.68
        }
      ],
      "response_status": "stable_numeric_grid"
    }
  ],
  "importance": [
    {
      "explanation_scope": "registered_final_artifact_descriptive_on_2025_training_rows",
      "feature": "lag1_fantasy_points_total",
      "importance_mean": 1.2106141476831254,
      "importance_std": 0.15471458587316406,
      "rank": 1
    },
    {
      "explanation_scope": "registered_final_artifact_descriptive_on_2025_training_rows",
      "feature": "weighted_3yr_games_active",
      "importance_mean": 0.5264613383273187,
      "importance_std": 0.12778293087369147,
      "rank": 2
    },
    {
      "explanation_scope": "registered_final_artifact_descriptive_on_2025_training_rows",
      "feature": "missing_lag1",
      "importance_mean": 0.38218515227443134,
      "importance_std": 0.046477560962948784,
      "rank": 3
    },
    {
      "explanation_scope": "registered_final_artifact_descriptive_on_2025_training_rows",
      "feature": "weighted_3yr_fantasy_points_per_game",
      "importance_mean": 0.25806360240946163,
      "importance_std": 0.08643395088033644,
      "rank": 4
    },
    {
      "explanation_scope": "registered_final_artifact_descriptive_on_2025_training_rows",
      "feature": "draft_pick",
      "importance_mean": 0.2522200758008014,
      "importance_std": 0.04111667868128297,
      "rank": 5
    },
    {
      "explanation_scope": "registered_final_artifact_descriptive_on_2025_training_rows",
      "feature": "lag1_fantasy_points_per_game",
      "importance_mean": 0.23654997039002965,
      "importance_std": 0.05118701936906078,
      "rank": 6
    },
    {
      "explanation_scope": "registered_final_artifact_descriptive_on_2025_training_rows",
      "feature": "age_at_cutoff",
      "importance_mean": 0.20763542411982194,
      "importance_std": 0.016230926439395867,
      "rank": 7
    },
    {
      "explanation_scope": "registered_final_artifact_descriptive_on_2025_training_rows",
      "feature": "weighted_3yr_interceptions_per_game",
      "importance_mean": 0.20348248815672268,
      "importance_std": 0.02466086353271879,
      "rank": 8
    },
    {
      "explanation_scope": "registered_final_artifact_descriptive_on_2025_training_rows",
      "feature": "weighted_3yr_two_point_conversions_per_game",
      "importance_mean": 0.1718728536631673,
      "importance_std": 0.010120050033304386,
      "rank": 9
    },
    {
      "explanation_scope": "registered_final_artifact_descriptive_on_2025_training_rows",
      "feature": "weighted_3yr_passing_tds_per_game",
      "importance_mean": 0.16871143485781145,
      "importance_std": 0.03280740594786716,
      "rank": 10
    },
    {
      "explanation_scope": "registered_final_artifact_descriptive_on_2025_training_rows",
      "feature": "weighted_3yr_passing_yards_per_game",
      "importance_mean": 0.14778314394565384,
      "importance_std": 0.008110210300357096,
      "rank": 11
    },
    {
      "explanation_scope": "registered_final_artifact_descriptive_on_2025_training_rows",
      "feature": "weighted_3yr_passing_attempts_per_game",
      "importance_mean": 0.14523823773352956,
      "importance_std": 0.014334712756685195,
      "rank": 12
    },
    {
      "explanation_scope": "registered_final_artifact_descriptive_on_2025_training_rows",
      "feature": "nfl_experience_years",
      "importance_mean": 0.09345684670851573,
      "importance_std": 0.027422069099062155,
      "rank": 13
    },
    {
      "explanation_scope": "registered_final_artifact_descriptive_on_2025_training_rows",
      "feature": "weighted_3yr_rushing_tds_per_game",
      "importance_mean": 0.09176619700629707,
      "importance_std": 0.011721263362810303,
      "rank": 14
    },
    {
      "explanation_scope": "registered_final_artifact_descriptive_on_2025_training_rows",
      "feature": "history_seasons",
      "importance_mean": 0.08110952047100159,
      "importance_std": 0.015144995970356703,
      "rank": 15
    },
    {
      "explanation_scope": "registered_final_artifact_descriptive_on_2025_training_rows",
      "feature": "weighted_3yr_fumbles_lost_per_game",
      "importance_mean": 0.0702760789828174,
      "importance_std": 0.006488478771290924,
      "rank": 16
    },
    {
      "explanation_scope": "registered_final_artifact_descriptive_on_2025_training_rows",
      "feature": "previous_team",
      "importance_mean": 0.06918422293732043,
      "importance_std": 0.011414806756962742,
      "rank": 17
    },
    {
      "explanation_scope": "registered_final_artifact_descriptive_on_2025_training_rows",
      "feature": "weighted_3yr_carries_per_game",
      "importance_mean": 0.0675444222926191,
      "importance_std": 0.01601460292355449,
      "rank": 18
    },
    {
      "explanation_scope": "registered_final_artifact_descriptive_on_2025_training_rows",
      "feature": "lag1_stat_games",
      "importance_mean": 0.06388542948580515,
      "importance_std": 0.026660991568346604,
      "rank": 19
    },
    {
      "explanation_scope": "registered_final_artifact_descriptive_on_2025_training_rows",
      "feature": "height_inches",
      "importance_mean": 0.02830613218264455,
      "importance_std": 0.008511588030491344,
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

- Project-relative path: `models/artifacts/phase4-7ae8e9aed04bffca00c0/attempt-866987f75a2c406693cf892d49adc975/QB/games_active/hist_gradient_boosting.joblib`
- SHA-256: `d623bc75fb3a6b411f2476c1756af9f0c8a0531b45ae95e702eef7f141610da7`

## Additional metadata

````json
{
  "publication_id": "attempt-866987f75a2c406693cf892d49adc975"
}
````
