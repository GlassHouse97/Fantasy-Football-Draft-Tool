# Model Card: phase4-052d2866899a665a44f3-wr-total-hgb

- Model ID: `phase4-052d2866899a665a44f3-wr-total-hgb`
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
  "draft_relevant_validation_mae": 58.8156626037677,
  "draft_relevant_validation_rows": 180,
  "draft_relevant_validation_signed_bias": -4.634407682455668,
  "position": "WR",
  "target_name": "fantasy_points_total",
  "test_mae": 19.031035030694582,
  "test_rows": 434,
  "test_season": 2025,
  "validation_mae": 21.523708175125215,
  "validation_rows": 2109,
  "validation_seasons": [
    2020,
    2021,
    2022,
    2023,
    2024
  ],
  "validation_top_n_capture_rate": 0.6833333333333333
}
````

## Comparison with transparent baselines

````json
{
  "best_learned_vs_baseline_bootstrap": {
    "candidate_mae": 58.8156626037677,
    "ci95_lower": -3.130543470007716,
    "ci95_upper": 7.379321027205819,
    "direction": "uncertain",
    "mae_difference_candidate_minus_reference": 1.918842225695002,
    "n_resamples": 2000,
    "reference_mae": 56.8968203780727,
    "rows": 180,
    "seed": 42
  },
  "decision_status": "learned_draft_relevant_regression_baseline_retained",
  "learned_improvement_status": "regression",
  "reference_metrics": {
    "candidate_name": "age_position_adjusted",
    "candidate_source": "baseline",
    "draft_relevant_validation_mae": 56.8968203780727,
    "draft_relevant_validation_rows": 180,
    "draft_relevant_validation_signed_bias": 21.53161016093822,
    "position": "WR",
    "target_name": "fantasy_points_total",
    "test_mae": 32.661684199629065,
    "test_rows": 434,
    "test_season": 2025,
    "validation_mae": 33.488095587295305,
    "validation_rows": 2109,
    "validation_seasons": [
      2020,
      2021,
      2022,
      2023,
      2024
    ],
    "validation_top_n_capture_rate": 0.7277777777777777
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
      "empirical_coverage_p10_p90": 0.8502304147465438,
      "evaluation_scope": "test",
      "mean_interval_width_p10_p90": 75.90127528763593,
      "pinball_loss_p10": 7.584719372633743,
      "pinball_loss_p50": 9.515517515347291,
      "pinball_loss_p90": 7.021604273776035,
      "position": "WR",
      "prediction_season": 2025,
      "projection_tier": "all",
      "rows": 434,
      "target_name": "fantasy_points_total"
    },
    {
      "candidate_name": "hist_gradient_boosting",
      "empirical_coverage_p10_p90": 0.47706422018348627,
      "evaluation_scope": "test",
      "mean_interval_width_p10_p90": 75.90127528763593,
      "pinball_loss_p10": 19.213744612337532,
      "pinball_loss_p50": 27.426239772205815,
      "pinball_loss_p90": 14.913729874137054,
      "position": "WR",
      "prediction_season": 2025,
      "projection_tier": "top",
      "rows": 109,
      "target_name": "fantasy_points_total"
    },
    {
      "candidate_name": "hist_gradient_boosting",
      "empirical_coverage_p10_p90": 0.9675925925925926,
      "evaluation_scope": "test",
      "mean_interval_width_p10_p90": 75.90127528763593,
      "pinball_loss_p10": 3.6175881418772518,
      "pinball_loss_p50": 4.677254145623118,
      "pinball_loss_p90": 4.630439381813736,
      "position": "WR",
      "prediction_season": 2025,
      "projection_tier": "middle",
      "rows": 216,
      "target_name": "fantasy_points_total"
    },
    {
      "candidate_name": "hist_gradient_boosting",
      "empirical_coverage_p10_p90": 0.9908256880733946,
      "evaluation_scope": "test",
      "mean_interval_width_p10_p90": 75.90127528763593,
      "pinball_loss_p10": 3.8171651957134585,
      "pinball_loss_p50": 1.1925465232632781,
      "pinball_loss_p90": 3.8679338721659944,
      "position": "WR",
      "prediction_season": 2025,
      "projection_tier": "lower",
      "rows": 109,
      "target_name": "fantasy_points_total"
    },
    {
      "candidate_name": "hist_gradient_boosting",
      "empirical_coverage_p10_p90": 0.8067632850241546,
      "evaluation_scope": "validation",
      "mean_interval_width_p10_p90": 82.57833205622988,
      "pinball_loss_p10": 7.558131734284884,
      "pinball_loss_p50": 11.366297732394697,
      "pinball_loss_p90": 8.40209817196291,
      "position": "WR",
      "prediction_season": 2020,
      "projection_tier": "all",
      "rows": 414,
      "target_name": "fantasy_points_total"
    },
    {
      "candidate_name": "hist_gradient_boosting",
      "empirical_coverage_p10_p90": 0.40384615384615385,
      "evaluation_scope": "validation",
      "mean_interval_width_p10_p90": 82.57833205622991,
      "pinball_loss_p10": 18.75554480587816,
      "pinball_loss_p50": 29.67447198503003,
      "pinball_loss_p90": 15.37556673129608,
      "position": "WR",
      "prediction_season": 2020,
      "projection_tier": "top",
      "rows": 104,
      "target_name": "fantasy_points_total"
    },
    {
      "candidate_name": "hist_gradient_boosting",
      "empirical_coverage_p10_p90": 0.912621359223301,
      "evaluation_scope": "validation",
      "mean_interval_width_p10_p90": 82.5783320562299,
      "pinball_loss_p10": 3.874351039463099,
      "pinball_loss_p50": 6.875671469131038,
      "pinball_loss_p90": 6.8008185136226995,
      "position": "WR",
      "prediction_season": 2020,
      "projection_tier": "middle",
      "rows": 206,
      "target_name": "fantasy_points_total"
    },
    {
      "candidate_name": "hist_gradient_boosting",
      "empirical_coverage_p10_p90": 1.0,
      "evaluation_scope": "validation",
      "mean_interval_width_p10_p90": 82.57833205622991,
      "pinball_loss_p10": 3.657438115896298,
      "pinball_loss_p50": 1.9530178089162242,
      "pinball_loss_p90": 4.6003950897266925,
      "position": "WR",
      "prediction_season": 2020,
      "projection_tier": "lower",
      "rows": 104,
      "target_name": "fantasy_points_total"
    },
    {
      "candidate_name": "hist_gradient_boosting",
      "empirical_coverage_p10_p90": 0.7852028639618138,
      "evaluation_scope": "validation",
      "mean_interval_width_p10_p90": 81.31123774172298,
      "pinball_loss_p10": 8.268845505804986,
      "pinball_loss_p50": 12.105661365433805,
      "pinball_loss_p90": 9.07151486271293,
      "position": "WR",
      "prediction_season": 2021,
      "projection_tier": "all",
      "rows": 419,
      "target_name": "fantasy_points_total"
    },
    {
      "candidate_name": "hist_gradient_boosting",
      "empirical_coverage_p10_p90": 0.4,
      "evaluation_scope": "validation",
      "mean_interval_width_p10_p90": 81.31123774172298,
      "pinball_loss_p10": 20.707821635750065,
      "pinball_loss_p50": 30.408054440443845,
      "pinball_loss_p90": 16.37083955093956,
      "position": "WR",
      "prediction_season": 2021,
      "projection_tier": "top",
      "rows": 105,
      "target_name": "fantasy_points_total"
    },
    {
      "candidate_name": "hist_gradient_boosting",
      "empirical_coverage_p10_p90": 0.8851674641148325,
      "evaluation_scope": "validation",
      "mean_interval_width_p10_p90": 81.31123774172298,
      "pinball_loss_p10": 4.270168421843944,
      "pinball_loss_p50": 7.999471051490057,
      "pinball_loss_p90": 7.61763007666152,
      "position": "WR",
      "prediction_season": 2021,
      "projection_tier": "middle",
      "rows": 209,
      "target_name": "fantasy_points_total"
    },
    {
      "candidate_name": "hist_gradient_boosting",
      "empirical_coverage_p10_p90": 0.9714285714285714,
      "evaluation_scope": "validation",
      "mean_interval_width_p10_p90": 81.31123774172298,
      "pinball_loss_p10": 3.789140904887129,
      "pinball_loss_p50": 1.9765423438927479,
      "pinball_loss_p90": 4.666113224817207,
      "position": "WR",
      "prediction_season": 2021,
      "projection_tier": "lower",
      "rows": 105,
      "target_name": "fantasy_points_total"
    },
    {
      "candidate_name": "hist_gradient_boosting",
      "empirical_coverage_p10_p90": 0.8101851851851852,
      "evaluation_scope": "validation",
      "mean_interval_width_p10_p90": 83.09721951179448,
      "pinball_loss_p10": 6.941457661821585,
      "pinball_loss_p50": 10.741074096100029,
      "pinball_loss_p90": 8.011349286873282,
      "position": "WR",
      "prediction_season": 2022,
      "projection_tier": "all",
      "rows": 432,
      "target_name": "fantasy_points_total"
    },
    {
      "candidate_name": "hist_gradient_boosting",
      "empirical_coverage_p10_p90": 0.4074074074074074,
      "evaluation_scope": "validation",
      "mean_interval_width_p10_p90": 83.09721951179445,
      "pinball_loss_p10": 15.459294939224126,
      "pinball_loss_p50": 26.072663926027207,
      "pinball_loss_p90": 12.146549475536892,
      "position": "WR",
      "prediction_season": 2022,
      "projection_tier": "top",
      "rows": 108,
      "target_name": "fantasy_points_total"
    },
    {
      "candidate_name": "hist_gradient_boosting",
      "empirical_coverage_p10_p90": 0.9166666666666666,
      "evaluation_scope": "validation",
      "mean_interval_width_p10_p90": 83.09721951179448,
      "pinball_loss_p10": 4.144190179977424,
      "pinball_loss_p50": 8.049026262794722,
      "pinball_loss_p90": 7.803640534442075,
      "position": "WR",
      "prediction_season": 2022,
      "projection_tier": "middle",
      "rows": 216,
      "target_name": "fantasy_points_total"
    },
    {
      "candidate_name": "hist_gradient_boosting",
      "empirical_coverage_p10_p90": 1.0,
      "evaluation_scope": "validation",
      "mean_interval_width_p10_p90": 83.09721951179445,
      "pinball_loss_p10": 4.018155348107367,
      "pinball_loss_p50": 0.7935799327834596,
      "pinball_loss_p90": 4.291566603072078,
      "position": "WR",
      "prediction_season": 2022,
      "projection_tier": "lower",
      "rows": 108,
      "target_name": "fantasy_points_total"
    },
    {
      "candidate_name": "hist_gradient_boosting",
      "empirical_coverage_p10_p90": 0.8210023866348448,
      "evaluation_scope": "validation",
      "mean_interval_width_p10_p90": 82.50600187170883,
      "pinball_loss_p10": 5.7923455520183555,
      "pinball_loss_p50": 9.682753619392159,
      "pinball_loss_p90": 7.606946917004642,
      "position": "WR",
      "prediction_season": 2023,
      "projection_tier": "all",
      "rows": 419,
      "target_name": "fantasy_points_total"
    },
    {
      "candidate_name": "hist_gradient_boosting",
      "empirical_coverage_p10_p90": 0.41904761904761906,
      "evaluation_scope": "validation",
      "mean_interval_width_p10_p90": 82.50600187170883,
      "pinball_loss_p10": 11.791933761492919,
      "pinball_loss_p50": 25.01369865844843,
      "pinball_loss_p90": 13.912412230836933,
      "position": "WR",
      "prediction_season": 2023,
      "projection_tier": "top",
      "rows": 105,
      "target_name": "fantasy_points_total"
    },
    {
      "candidate_name": "hist_gradient_boosting",
      "empirical_coverage_p10_p90": 0.9330143540669856,
      "evaluation_scope": "validation",
      "mean_interval_width_p10_p90": 82.50600187170883,
      "pinball_loss_p10": 3.7510969866666706,
      "pinball_loss_p50": 6.462962635951587,
      "pinball_loss_p90": 6.052894380190071,
      "position": "WR",
      "prediction_season": 2023,
      "projection_tier": "middle",
      "rows": 209,
      "target_name": "fantasy_points_total"
    },
    {
      "candidate_name": "hist_gradient_boosting",
      "empirical_coverage_p10_p90": 1.0,
      "evaluation_scope": "validation",
      "mean_interval_width_p10_p90": 82.50600187170883,
      "pinball_loss_p10": 3.8558140107200054,
      "pinball_loss_p50": 0.760725871184256,
      "pinball_loss_p90": 4.39478617645088,
      "position": "WR",
      "prediction_season": 2023,
      "projection_tier": "lower",
      "rows": 105,
      "target_name": "fantasy_points_total"
    },
    {
      "candidate_name": "hist_gradient_boosting",
      "empirical_coverage_p10_p90": 0.8235294117647058,
      "evaluation_scope": "validation",
      "mean_interval_width_p10_p90": 79.60193182930745,
      "pinball_loss_p10": 6.630441525884044,
      "pinball_loss_p50": 9.933207344237275,
      "pinball_loss_p90": 8.32876805683912,
      "position": "WR",
      "prediction_season": 2024,
      "projection_tier": "all",
      "rows": 425,
      "target_name": "fantasy_points_total"
    },
    {
      "candidate_name": "hist_gradient_boosting",
      "empirical_coverage_p10_p90": 0.4339622641509434,
      "evaluation_scope": "validation",
      "mean_interval_width_p10_p90": 79.60193182930743,
      "pinball_loss_p10": 14.400304784379905,
      "pinball_loss_p50": 25.87670694239278,
      "pinball_loss_p90": 15.447254405148,
      "position": "WR",
      "prediction_season": 2024,
      "projection_tier": "top",
      "rows": 106,
      "target_name": "fantasy_points_total"
    },
    {
      "candidate_name": "hist_gradient_boosting",
      "empirical_coverage_p10_p90": 0.9295774647887324,
      "evaluation_scope": "validation",
      "mean_interval_width_p10_p90": 79.60193182930743,
      "pinball_loss_p10": 4.104553751502445,
      "pinball_loss_p50": 6.514373336013267,
      "pinball_loss_p90": 6.928508789233367,
      "position": "WR",
      "prediction_season": 2024,
      "projection_tier": "middle",
      "rows": 213,
      "target_name": "fantasy_points_total"
    },
    {
      "candidate_name": "hist_gradient_boosting",
      "empirical_coverage_p10_p90": 1.0,
      "evaluation_scope": "validation",
      "mean_interval_width_p10_p90": 79.60193182930743,
      "pinball_loss_p10": 3.9361829460983704,
      "pinball_loss_p50": 0.8596289135507702,
      "pinball_loss_p90": 4.024010236832372,
      "position": "WR",
      "prediction_season": 2024,
      "projection_tier": "lower",
      "rows": 106,
      "target_name": "fantasy_points_total"
    }
  ],
  "empirical_not_guaranteed": true,
  "method": "training-only signed out-of-fold residual quantiles",
  "operational_center": "training_only_residual_adjusted_p50",
  "residual_rows": 1278,
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
          "average_prediction": 50.96864027482327,
          "feature_value": 23.91855
        },
        {
          "average_prediction": 40.22486540494354,
          "feature_value": 24.790713636363638
        },
        {
          "average_prediction": 40.64299832619575,
          "feature_value": 25.662877272727272
        },
        {
          "average_prediction": 37.644111325545325,
          "feature_value": 26.53504090909091
        },
        {
          "average_prediction": 37.28277602018971,
          "feature_value": 27.407204545454544
        },
        {
          "average_prediction": 30.899165944169972,
          "feature_value": 28.27936818181818
        },
        {
          "average_prediction": 30.68360520458812,
          "feature_value": 29.151531818181816
        },
        {
          "average_prediction": 29.799229274424405,
          "feature_value": 30.023695454545454
        },
        {
          "average_prediction": 25.217199851613774,
          "feature_value": 30.895859090909088
        },
        {
          "average_prediction": 25.217199851613774,
          "feature_value": 31.768022727272726
        },
        {
          "average_prediction": 24.80466738366987,
          "feature_value": 32.64018636363636
        },
        {
          "average_prediction": 24.66372110550228,
          "feature_value": 33.51235
        }
      ],
      "response_status": "stable_numeric_grid"
    },
    {
      "explanation_scope": "registered_final_artifact_descriptive_on_2025_training_rows",
      "feature": "lag1_fantasy_points_per_game",
      "interpretation": "This explanation is associative, not causal; changing a feature here does not establish that the feature causes the prediction to change.",
      "method": "one_way_average_partial_dependence",
      "points": [
        {
          "average_prediction": 32.826036179499525,
          "feature_value": 0.0
        },
        {
          "average_prediction": 33.01989530039151,
          "feature_value": 1.5114705882352937
        },
        {
          "average_prediction": 33.54938483029802,
          "feature_value": 3.0229411764705874
        },
        {
          "average_prediction": 38.85019289377307,
          "feature_value": 4.534411764705881
        },
        {
          "average_prediction": 38.802260825010215,
          "feature_value": 6.045882352941175
        },
        {
          "average_prediction": 39.27756362513931,
          "feature_value": 7.557352941176468
        },
        {
          "average_prediction": 45.901640465715026,
          "feature_value": 9.068823529411763
        },
        {
          "average_prediction": 48.23205667133469,
          "feature_value": 10.580294117647055
        },
        {
          "average_prediction": 48.14060847999498,
          "feature_value": 12.09176470588235
        },
        {
          "average_prediction": 48.4534189774995,
          "feature_value": 13.603235294117644
        },
        {
          "average_prediction": 48.21786582059619,
          "feature_value": 15.114705882352936
        },
        {
          "average_prediction": 47.40892281580323,
          "feature_value": 16.62617647058823
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
          "average_prediction": 21.407675240893624,
          "feature_value": 0.0
        },
        {
          "average_prediction": 23.527004143901156,
          "feature_value": 21.88181818181818
        },
        {
          "average_prediction": 29.753094565050418,
          "feature_value": 43.76363636363636
        },
        {
          "average_prediction": 45.9042423335822,
          "feature_value": 65.64545454545454
        },
        {
          "average_prediction": 45.92813977401082,
          "feature_value": 87.52727272727272
        },
        {
          "average_prediction": 65.27281566202984,
          "feature_value": 109.40909090909089
        },
        {
          "average_prediction": 80.0286660651983,
          "feature_value": 131.29090909090908
        },
        {
          "average_prediction": 78.48239207573921,
          "feature_value": 153.17272727272726
        },
        {
          "average_prediction": 91.48680445008114,
          "feature_value": 175.05454545454543
        },
        {
          "average_prediction": 106.19408431678801,
          "feature_value": 196.9363636363636
        },
        {
          "average_prediction": 106.15078416864935,
          "feature_value": 218.81818181818178
        },
        {
          "average_prediction": 105.92215669218322,
          "feature_value": 240.7
        }
      ],
      "response_status": "stable_numeric_grid"
    }
  ],
  "importance": [
    {
      "explanation_scope": "registered_final_artifact_descriptive_on_2025_training_rows",
      "feature": "lag1_fantasy_points_total",
      "importance_mean": 15.062422011908211,
      "importance_std": 0.23420761154161868,
      "rank": 1
    },
    {
      "explanation_scope": "registered_final_artifact_descriptive_on_2025_training_rows",
      "feature": "age_at_cutoff",
      "importance_mean": 3.5783390053080937,
      "importance_std": 0.3790862640719249,
      "rank": 2
    },
    {
      "explanation_scope": "registered_final_artifact_descriptive_on_2025_training_rows",
      "feature": "lag1_fantasy_points_per_game",
      "importance_mean": 2.6782923962323997,
      "importance_std": 0.15461852546116012,
      "rank": 3
    },
    {
      "explanation_scope": "registered_final_artifact_descriptive_on_2025_training_rows",
      "feature": "weighted_3yr_receiving_yards_per_game",
      "importance_mean": 2.561062986929512,
      "importance_std": 0.30542659857538307,
      "rank": 4
    },
    {
      "explanation_scope": "registered_final_artifact_descriptive_on_2025_training_rows",
      "feature": "missing_lag1",
      "importance_mean": 1.962701483663857,
      "importance_std": 0.08744691763016858,
      "rank": 5
    },
    {
      "explanation_scope": "registered_final_artifact_descriptive_on_2025_training_rows",
      "feature": "weighted_3yr_targets_per_game",
      "importance_mean": 0.8948641881246541,
      "importance_std": 0.09813240193255039,
      "rank": 6
    },
    {
      "explanation_scope": "registered_final_artifact_descriptive_on_2025_training_rows",
      "feature": "weighted_3yr_receptions_per_game",
      "importance_mean": 0.8907900766661658,
      "importance_std": 0.1308977775433011,
      "rank": 7
    },
    {
      "explanation_scope": "registered_final_artifact_descriptive_on_2025_training_rows",
      "feature": "weighted_3yr_fantasy_points_per_game",
      "importance_mean": 0.8471969157130935,
      "importance_std": 0.18482331758708134,
      "rank": 8
    },
    {
      "explanation_scope": "registered_final_artifact_descriptive_on_2025_training_rows",
      "feature": "lag1_games_active",
      "importance_mean": 0.8198882857540284,
      "importance_std": 0.09462301740206142,
      "rank": 9
    },
    {
      "explanation_scope": "registered_final_artifact_descriptive_on_2025_training_rows",
      "feature": "weighted_3yr_games_active",
      "importance_mean": 0.7753180815805045,
      "importance_std": 0.16425522558422276,
      "rank": 10
    },
    {
      "explanation_scope": "registered_final_artifact_descriptive_on_2025_training_rows",
      "feature": "draft_pick",
      "importance_mean": 0.5689214028959231,
      "importance_std": 0.08516247783526315,
      "rank": 11
    },
    {
      "explanation_scope": "registered_final_artifact_descriptive_on_2025_training_rows",
      "feature": "weighted_3yr_rushing_yards_per_game",
      "importance_mean": 0.4520621411536851,
      "importance_std": 0.05737338396774555,
      "rank": 12
    },
    {
      "explanation_scope": "registered_final_artifact_descriptive_on_2025_training_rows",
      "feature": "weighted_3yr_carries_per_game",
      "importance_mean": 0.451230063714026,
      "importance_std": 0.06135287135657923,
      "rank": 13
    },
    {
      "explanation_scope": "registered_final_artifact_descriptive_on_2025_training_rows",
      "feature": "previous_team",
      "importance_mean": 0.43682302623760627,
      "importance_std": 0.08336972680097658,
      "rank": 14
    },
    {
      "explanation_scope": "registered_final_artifact_descriptive_on_2025_training_rows",
      "feature": "weighted_3yr_receiving_tds_per_game",
      "importance_mean": 0.4058984769856597,
      "importance_std": 0.1357796853272141,
      "rank": 15
    },
    {
      "explanation_scope": "registered_final_artifact_descriptive_on_2025_training_rows",
      "feature": "weighted_3yr_two_point_conversions_per_game",
      "importance_mean": 0.3034857532607834,
      "importance_std": 0.053162828121271107,
      "rank": 16
    },
    {
      "explanation_scope": "registered_final_artifact_descriptive_on_2025_training_rows",
      "feature": "nfl_experience_years",
      "importance_mean": 0.2371008939987675,
      "importance_std": 0.02039082082672071,
      "rank": 17
    },
    {
      "explanation_scope": "registered_final_artifact_descriptive_on_2025_training_rows",
      "feature": "weighted_3yr_fumbles_lost_per_game",
      "importance_mean": 0.21678885417151578,
      "importance_std": 0.0630066780350327,
      "rank": 18
    },
    {
      "explanation_scope": "registered_final_artifact_descriptive_on_2025_training_rows",
      "feature": "weighted_3yr_passing_yards_per_game",
      "importance_mean": 0.17286400665702714,
      "importance_std": 0.02045635885199276,
      "rank": 19
    },
    {
      "explanation_scope": "registered_final_artifact_descriptive_on_2025_training_rows",
      "feature": "height_inches",
      "importance_mean": 0.1389858085090335,
      "importance_std": 0.05677953188805042,
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

- Project-relative path: `models/artifacts/phase4-052d2866899a665a44f3/attempt-331cdaf7eb7f4721aa43c08d469288ee/WR/fantasy_points_total/hist_gradient_boosting.joblib`
- SHA-256: `1f37ee82669b526edfbc0ebed1e34512a3d172b92ced5f68331d9a5f8ac93c9b`

## Additional metadata

````json
{
  "publication_id": "attempt-331cdaf7eb7f4721aa43c08d469288ee"
}
````
