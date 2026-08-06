# Model Card: phase4-7ae8e9aed04bffca00c0-rb-games-hgb

- Model ID: `phase4-7ae8e9aed04bffca00c0-rb-games-hgb`
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
  "position": "RB",
  "target_name": "games_active",
  "test_mae": 2.6712250004053235,
  "test_rows": 294,
  "test_season": 2025,
  "validation_mae": 3.0062002539299355,
  "validation_rows": 1483,
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
    "candidate_mae": 3.0062002539299355,
    "ci95_lower": -3.4529938711513335,
    "ci95_upper": -2.8897258240890045,
    "direction": "candidate_lower_mae",
    "mae_difference_candidate_minus_reference": -3.171957461928544,
    "n_resamples": 2000,
    "reference_mae": 6.17815771585848,
    "rows": 1483,
    "seed": 42
  },
  "decision_status": "learned_significant_improvement_selected",
  "learned_improvement_status": "statistically_clear",
  "reference_metrics": {
    "candidate_name": "age_position_adjusted",
    "candidate_source": "baseline",
    "position": "RB",
    "target_name": "games_active",
    "test_mae": 6.819331065759639,
    "test_rows": 294,
    "test_season": 2025,
    "validation_mae": 6.17815771585848,
    "validation_rows": 1483,
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
      "empirical_coverage_p10_p90": 0.8333333333333334,
      "evaluation_scope": "test",
      "mean_interval_width_p10_p90": 8.306459293134875,
      "pinball_loss_p10": 0.5631149781539669,
      "pinball_loss_p50": 1.3356125002026618,
      "pinball_loss_p90": 0.7930216882241746,
      "position": "RB",
      "prediction_season": 2025,
      "projection_tier": "all",
      "rows": 294,
      "target_name": "games_active"
    },
    {
      "candidate_name": "hist_gradient_boosting",
      "empirical_coverage_p10_p90": 0.7567567567567568,
      "evaluation_scope": "test",
      "mean_interval_width_p10_p90": 10.490409665098259,
      "pinball_loss_p10": 1.3771133602690704,
      "pinball_loss_p50": 2.1928352279301677,
      "pinball_loss_p90": 0.5459548164760354,
      "position": "RB",
      "prediction_season": 2025,
      "projection_tier": "top",
      "rows": 74,
      "target_name": "games_active"
    },
    {
      "candidate_name": "hist_gradient_boosting",
      "empirical_coverage_p10_p90": 0.7876712328767124,
      "evaluation_scope": "test",
      "mean_interval_width_p10_p90": 8.487052417520545,
      "pinball_loss_p10": 0.4339001021736649,
      "pinball_loss_p50": 1.567791263925568,
      "pinball_loss_p90": 1.0299850240961812,
      "position": "RB",
      "prediction_season": 2025,
      "projection_tier": "middle",
      "rows": 146,
      "target_name": "games_active"
    },
    {
      "candidate_name": "hist_gradient_boosting",
      "empirical_coverage_p10_p90": 1.0,
      "evaluation_scope": "test",
      "mean_interval_width_p10_p90": 5.76620356765382,
      "pinball_loss_p10": 0.004054054054054054,
      "pinball_loss_p50": 0.020307346751583105,
      "pinball_loss_p90": 0.5725663027113278,
      "position": "RB",
      "prediction_season": 2025,
      "projection_tier": "lower",
      "rows": 74,
      "target_name": "games_active"
    },
    {
      "candidate_name": "hist_gradient_boosting",
      "empirical_coverage_p10_p90": 0.7807308970099668,
      "evaluation_scope": "validation",
      "mean_interval_width_p10_p90": 8.783009666147064,
      "pinball_loss_p10": 0.5787497859532837,
      "pinball_loss_p50": 1.4556702752157669,
      "pinball_loss_p90": 0.8787342334087305,
      "position": "RB",
      "prediction_season": 2020,
      "projection_tier": "all",
      "rows": 301,
      "target_name": "games_active"
    },
    {
      "candidate_name": "hist_gradient_boosting",
      "empirical_coverage_p10_p90": 0.7105263157894737,
      "evaluation_scope": "validation",
      "mean_interval_width_p10_p90": 11.489734115400244,
      "pinball_loss_p10": 1.2726403165125835,
      "pinball_loss_p50": 2.2495329181763695,
      "pinball_loss_p90": 0.6329499970705325,
      "position": "RB",
      "prediction_season": 2020,
      "projection_tier": "top",
      "rows": 76,
      "target_name": "games_active"
    },
    {
      "candidate_name": "hist_gradient_boosting",
      "empirical_coverage_p10_p90": 0.7066666666666667,
      "evaluation_scope": "validation",
      "mean_interval_width_p10_p90": 8.91496806168739,
      "pinball_loss_p10": 0.5145534767798805,
      "pinball_loss_p50": 1.7712816737236123,
      "pinball_loss_p90": 1.15581809153329,
      "position": "RB",
      "prediction_season": 2020,
      "projection_tier": "middle",
      "rows": 150,
      "target_name": "games_active"
    },
    {
      "candidate_name": "hist_gradient_boosting",
      "empirical_coverage_p10_p90": 1.0,
      "evaluation_scope": "validation",
      "mean_interval_width_p10_p90": 5.776278766489858,
      "pinball_loss_p10": 0.004000000000000001,
      "pinball_loss_p50": 0.02,
      "pinball_loss_p90": 0.5736278766489855,
      "position": "RB",
      "prediction_season": 2020,
      "projection_tier": "lower",
      "rows": 75,
      "target_name": "games_active"
    },
    {
      "candidate_name": "hist_gradient_boosting",
      "empirical_coverage_p10_p90": 0.8272425249169435,
      "evaluation_scope": "validation",
      "mean_interval_width_p10_p90": 9.41783066196148,
      "pinball_loss_p10": 0.5292712864200222,
      "pinball_loss_p50": 1.4830787997062953,
      "pinball_loss_p90": 0.8627922309471396,
      "position": "RB",
      "prediction_season": 2021,
      "projection_tier": "all",
      "rows": 301,
      "target_name": "games_active"
    },
    {
      "candidate_name": "hist_gradient_boosting",
      "empirical_coverage_p10_p90": 0.7763157894736842,
      "evaluation_scope": "validation",
      "mean_interval_width_p10_p90": 11.690454054834857,
      "pinball_loss_p10": 1.0862304202201378,
      "pinball_loss_p50": 2.2139131052017187,
      "pinball_loss_p90": 0.6084756943277989,
      "position": "RB",
      "prediction_season": 2021,
      "projection_tier": "top",
      "rows": 76,
      "target_name": "games_active"
    },
    {
      "candidate_name": "hist_gradient_boosting",
      "empirical_coverage_p10_p90": 0.78,
      "evaluation_scope": "validation",
      "mean_interval_width_p10_p90": 9.854400595715001,
      "pinball_loss_p10": 0.49371430183797477,
      "pinball_loss_p50": 1.764328818108429,
      "pinball_loss_p90": 1.0378197535814147,
      "position": "RB",
      "prediction_season": 2021,
      "projection_tier": "middle",
      "rows": 150,
      "target_name": "games_active"
    },
    {
      "candidate_name": "hist_gradient_boosting",
      "empirical_coverage_p10_p90": 0.9733333333333334,
      "evaluation_scope": "validation",
      "mean_interval_width_p10_p90": 6.241765756342744,
      "pinball_loss_p10": 0.036000000000000004,
      "pinball_loss_p50": 0.18,
      "pinball_loss_p90": 0.7704446094528553,
      "position": "RB",
      "prediction_season": 2021,
      "projection_tier": "lower",
      "rows": 75,
      "target_name": "games_active"
    },
    {
      "candidate_name": "hist_gradient_boosting",
      "empirical_coverage_p10_p90": 0.793918918918919,
      "evaluation_scope": "validation",
      "mean_interval_width_p10_p90": 9.353679597483296,
      "pinball_loss_p10": 0.6428905926142129,
      "pinball_loss_p50": 1.5853373181012707,
      "pinball_loss_p90": 0.8111973584551236,
      "position": "RB",
      "prediction_season": 2022,
      "projection_tier": "all",
      "rows": 296,
      "target_name": "games_active"
    },
    {
      "candidate_name": "hist_gradient_boosting",
      "empirical_coverage_p10_p90": 0.7297297297297297,
      "evaluation_scope": "validation",
      "mean_interval_width_p10_p90": 11.12579569933382,
      "pinball_loss_p10": 1.2976841950489928,
      "pinball_loss_p50": 2.308230439176395,
      "pinball_loss_p90": 0.5347665266852186,
      "position": "RB",
      "prediction_season": 2022,
      "projection_tier": "top",
      "rows": 74,
      "target_name": "games_active"
    },
    {
      "candidate_name": "hist_gradient_boosting",
      "empirical_coverage_p10_p90": 0.722972972972973,
      "evaluation_scope": "validation",
      "mean_interval_width_p10_p90": 9.940586619766554,
      "pinball_loss_p10": 0.6369390877039294,
      "pinball_loss_p50": 2.010527584332675,
      "pinball_loss_p90": 1.0346239810143252,
      "position": "RB",
      "prediction_season": 2022,
      "projection_tier": "middle",
      "rows": 148,
      "target_name": "games_active"
    },
    {
      "candidate_name": "hist_gradient_boosting",
      "empirical_coverage_p10_p90": 1.0,
      "evaluation_scope": "validation",
      "mean_interval_width_p10_p90": 6.4077494510662545,
      "pinball_loss_p10": 0.0,
      "pinball_loss_p50": 0.012063664563337727,
      "pinball_loss_p90": 0.6407749451066254,
      "position": "RB",
      "prediction_season": 2022,
      "projection_tier": "lower",
      "rows": 74,
      "target_name": "games_active"
    },
    {
      "candidate_name": "hist_gradient_boosting",
      "empirical_coverage_p10_p90": 0.8006872852233677,
      "evaluation_scope": "validation",
      "mean_interval_width_p10_p90": 9.039177013553537,
      "pinball_loss_p10": 0.6562824984430685,
      "pinball_loss_p50": 1.55492340537709,
      "pinball_loss_p90": 0.8347192811394172,
      "position": "RB",
      "prediction_season": 2023,
      "projection_tier": "all",
      "rows": 291,
      "target_name": "games_active"
    },
    {
      "candidate_name": "hist_gradient_boosting",
      "empirical_coverage_p10_p90": 0.7671232876712328,
      "evaluation_scope": "validation",
      "mean_interval_width_p10_p90": 10.961463091783337,
      "pinball_loss_p10": 1.4434712444266344,
      "pinball_loss_p50": 2.341889758341201,
      "pinball_loss_p90": 0.5298510328389556,
      "position": "RB",
      "prediction_season": 2023,
      "projection_tier": "top",
      "rows": 73,
      "target_name": "games_active"
    },
    {
      "candidate_name": "hist_gradient_boosting",
      "empirical_coverage_p10_p90": 0.7241379310344828,
      "evaluation_scope": "validation",
      "mean_interval_width_p10_p90": 9.500403999110924,
      "pinball_loss_p10": 0.5752055600261285,
      "pinball_loss_p50": 1.859586147658394,
      "pinball_loss_p90": 1.0451663278053365,
      "position": "RB",
      "prediction_season": 2023,
      "projection_tier": "middle",
      "rows": 145,
      "target_name": "games_active"
    },
    {
      "candidate_name": "hist_gradient_boosting",
      "empirical_coverage_p10_p90": 0.9863013698630136,
      "evaluation_scope": "validation",
      "mean_interval_width_p10_p90": 6.2007551420933185,
      "pinball_loss_p10": 0.030136986301369864,
      "pinball_loss_p50": 0.16280503007340286,
      "pinball_loss_p90": 0.7215762723637376,
      "position": "RB",
      "prediction_season": 2023,
      "projection_tier": "lower",
      "rows": 73,
      "target_name": "games_active"
    },
    {
      "candidate_name": "hist_gradient_boosting",
      "empirical_coverage_p10_p90": 0.8333333333333334,
      "evaluation_scope": "validation",
      "mean_interval_width_p10_p90": 8.738920105683992,
      "pinball_loss_p10": 0.5520809839130522,
      "pinball_loss_p50": 1.4380661891659765,
      "pinball_loss_p90": 0.9000127875539943,
      "position": "RB",
      "prediction_season": 2024,
      "projection_tier": "all",
      "rows": 294,
      "target_name": "games_active"
    },
    {
      "candidate_name": "hist_gradient_boosting",
      "empirical_coverage_p10_p90": 0.8513513513513513,
      "evaluation_scope": "validation",
      "mean_interval_width_p10_p90": 11.044549815722954,
      "pinball_loss_p10": 1.163804170618285,
      "pinball_loss_p50": 1.9533363381102087,
      "pinball_loss_p90": 0.452290014554171,
      "position": "RB",
      "prediction_season": 2024,
      "projection_tier": "top",
      "rows": 74,
      "target_name": "games_active"
    },
    {
      "candidate_name": "hist_gradient_boosting",
      "empirical_coverage_p10_p90": 0.7414965986394558,
      "evaluation_scope": "validation",
      "mean_interval_width_p10_p90": 8.937439600763565,
      "pinball_loss_p10": 0.5114986438413895,
      "pinball_loss_p50": 1.8559298108688904,
      "pinball_loss_p90": 1.2810889668321805,
      "position": "RB",
      "prediction_season": 2024,
      "projection_tier": "middle",
      "rows": 147,
      "target_name": "games_active"
    },
    {
      "candidate_name": "hist_gradient_boosting",
      "empirical_coverage_p10_p90": 1.0,
      "evaluation_scope": "validation",
      "mean_interval_width_p10_p90": 6.001947991717143,
      "pinball_loss_p10": 0.0136986301369863,
      "pinball_loss_p50": 0.07428614242348924,
      "pinball_loss_p90": 0.5864961690347279,
      "position": "RB",
      "prediction_season": 2024,
      "projection_tier": "lower",
      "rows": 73,
      "target_name": "games_active"
    }
  ],
  "empirical_not_guaranteed": true,
  "method": "training-only signed out-of-fold residual quantiles",
  "operational_center": "training_only_residual_adjusted_p50",
  "residual_rows": 879,
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
          "average_prediction": 4.124442424515198,
          "feature_value": 0.0
        },
        {
          "average_prediction": 4.218906106663415,
          "feature_value": 24.124545454545455
        },
        {
          "average_prediction": 5.35675646685789,
          "feature_value": 48.24909090909091
        },
        {
          "average_prediction": 5.374812797453149,
          "feature_value": 72.37363636363636
        },
        {
          "average_prediction": 6.3358408173782665,
          "feature_value": 96.49818181818182
        },
        {
          "average_prediction": 6.311664719916666,
          "feature_value": 120.62272727272727
        },
        {
          "average_prediction": 6.311539921880669,
          "feature_value": 144.74727272727273
        },
        {
          "average_prediction": 6.387529347215327,
          "feature_value": 168.87181818181818
        },
        {
          "average_prediction": 6.505109370851956,
          "feature_value": 192.99636363636364
        },
        {
          "average_prediction": 6.505109370851956,
          "feature_value": 217.1209090909091
        },
        {
          "average_prediction": 6.496572204922909,
          "feature_value": 241.24545454545455
        },
        {
          "average_prediction": 6.496572204922909,
          "feature_value": 265.37
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
          "average_prediction": 6.848478595957353,
          "feature_value": 0.0
        },
        {
          "average_prediction": 1.4585424200980686,
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
          "average_prediction": 3.917923900050187,
          "feature_value": 1.0
        },
        {
          "average_prediction": 3.9297552634705126,
          "feature_value": 2.4545454545454546
        },
        {
          "average_prediction": 4.006564723045418,
          "feature_value": 3.909090909090909
        },
        {
          "average_prediction": 4.123161821824237,
          "feature_value": 5.363636363636363
        },
        {
          "average_prediction": 4.184114250440519,
          "feature_value": 6.818181818181818
        },
        {
          "average_prediction": 4.470254871242715,
          "feature_value": 8.272727272727273
        },
        {
          "average_prediction": 4.496588095981209,
          "feature_value": 9.727272727272727
        },
        {
          "average_prediction": 4.934630853232564,
          "feature_value": 11.181818181818182
        },
        {
          "average_prediction": 5.088986578451399,
          "feature_value": 12.636363636363637
        },
        {
          "average_prediction": 5.518369220513151,
          "feature_value": 14.090909090909092
        },
        {
          "average_prediction": 5.531340238803418,
          "feature_value": 15.545454545454547
        },
        {
          "average_prediction": 5.919031239318696,
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
      "importance_mean": 1.8300233114717777,
      "importance_std": 0.06499297980062023,
      "rank": 1
    },
    {
      "explanation_scope": "registered_final_artifact_descriptive_on_2025_training_rows",
      "feature": "lag1_fantasy_points_total",
      "importance_mean": 0.5529122754600998,
      "importance_std": 0.03327339233173291,
      "rank": 2
    },
    {
      "explanation_scope": "registered_final_artifact_descriptive_on_2025_training_rows",
      "feature": "weighted_3yr_games_active",
      "importance_mean": 0.46402945617330743,
      "importance_std": 0.039789476501204166,
      "rank": 3
    },
    {
      "explanation_scope": "registered_final_artifact_descriptive_on_2025_training_rows",
      "feature": "age_at_cutoff",
      "importance_mean": 0.33190854013769744,
      "importance_std": 0.03047349280042177,
      "rank": 4
    },
    {
      "explanation_scope": "registered_final_artifact_descriptive_on_2025_training_rows",
      "feature": "lag1_games_active",
      "importance_mean": 0.2887538693075668,
      "importance_std": 0.028081614917263308,
      "rank": 5
    },
    {
      "explanation_scope": "registered_final_artifact_descriptive_on_2025_training_rows",
      "feature": "weighted_3yr_carries_per_game",
      "importance_mean": 0.18758521093598227,
      "importance_std": 0.035970150758259115,
      "rank": 6
    },
    {
      "explanation_scope": "registered_final_artifact_descriptive_on_2025_training_rows",
      "feature": "weighted_3yr_receiving_yards_per_game",
      "importance_mean": 0.17053967526172267,
      "importance_std": 0.02918104749897663,
      "rank": 7
    },
    {
      "explanation_scope": "registered_final_artifact_descriptive_on_2025_training_rows",
      "feature": "nfl_experience_years",
      "importance_mean": 0.16508840872325728,
      "importance_std": 0.014553481470028566,
      "rank": 8
    },
    {
      "explanation_scope": "registered_final_artifact_descriptive_on_2025_training_rows",
      "feature": "lag1_stat_games",
      "importance_mean": 0.16368062890854418,
      "importance_std": 0.020769142499063833,
      "rank": 9
    },
    {
      "explanation_scope": "registered_final_artifact_descriptive_on_2025_training_rows",
      "feature": "weighted_3yr_rushing_yards_per_game",
      "importance_mean": 0.1340289944545015,
      "importance_std": 0.010502819453746788,
      "rank": 10
    },
    {
      "explanation_scope": "registered_final_artifact_descriptive_on_2025_training_rows",
      "feature": "draft_pick",
      "importance_mean": 0.12212661777914961,
      "importance_std": 0.01600796959709063,
      "rank": 11
    },
    {
      "explanation_scope": "registered_final_artifact_descriptive_on_2025_training_rows",
      "feature": "lag1_fantasy_points_per_game",
      "importance_mean": 0.1217670744330019,
      "importance_std": 0.017584476252336195,
      "rank": 12
    },
    {
      "explanation_scope": "registered_final_artifact_descriptive_on_2025_training_rows",
      "feature": "weighted_3yr_fantasy_points_per_game",
      "importance_mean": 0.11700564928757747,
      "importance_std": 0.01463316628050765,
      "rank": 13
    },
    {
      "explanation_scope": "registered_final_artifact_descriptive_on_2025_training_rows",
      "feature": "weighted_3yr_targets_per_game",
      "importance_mean": 0.09226225512522097,
      "importance_std": 0.012498223785854209,
      "rank": 14
    },
    {
      "explanation_scope": "registered_final_artifact_descriptive_on_2025_training_rows",
      "feature": "weighted_3yr_receptions_per_game",
      "importance_mean": 0.06990349310113206,
      "importance_std": 0.011030513704889437,
      "rank": 15
    },
    {
      "explanation_scope": "registered_final_artifact_descriptive_on_2025_training_rows",
      "feature": "weighted_3yr_fumbles_lost_per_game",
      "importance_mean": 0.056342017193516905,
      "importance_std": 0.005732033020308937,
      "rank": 16
    },
    {
      "explanation_scope": "registered_final_artifact_descriptive_on_2025_training_rows",
      "feature": "previous_team",
      "importance_mean": 0.04066515588100117,
      "importance_std": 0.02450512761318803,
      "rank": 17
    },
    {
      "explanation_scope": "registered_final_artifact_descriptive_on_2025_training_rows",
      "feature": "height_inches",
      "importance_mean": 0.03510856636585728,
      "importance_std": 0.004868170744241724,
      "rank": 18
    },
    {
      "explanation_scope": "registered_final_artifact_descriptive_on_2025_training_rows",
      "feature": "history_seasons",
      "importance_mean": 0.03431090591762072,
      "importance_std": 0.006432388732667464,
      "rank": 19
    },
    {
      "explanation_scope": "registered_final_artifact_descriptive_on_2025_training_rows",
      "feature": "weighted_3yr_two_point_conversions_per_game",
      "importance_mean": 0.03133977531210395,
      "importance_std": 0.00858652350851926,
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

- Project-relative path: `models/artifacts/phase4-7ae8e9aed04bffca00c0/attempt-866987f75a2c406693cf892d49adc975/RB/games_active/hist_gradient_boosting.joblib`
- SHA-256: `51610cb907de21b59954c1ed3302a4c6ec815b78f7c557392fb93ffbcffe0267`

## Additional metadata

````json
{
  "publication_id": "attempt-866987f75a2c406693cf892d49adc975"
}
````
