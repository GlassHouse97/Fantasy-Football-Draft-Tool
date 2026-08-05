# Model Card: phase4-7ae8e9aed04bffca00c0-te-total-hgb

- Model ID: `phase4-7ae8e9aed04bffca00c0-te-total-hgb`
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
  "position": "TE",
  "target_name": "fantasy_points_total",
  "test_mae": 13.316090749223283,
  "test_rows": 237,
  "test_season": 2025,
  "validation_mae": 16.398392683579086,
  "validation_rows": 1160,
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
    "candidate_mae": 16.398392683579086,
    "ci95_lower": -8.488550161377646,
    "ci95_upper": -6.028367519894714,
    "direction": "candidate_lower_mae",
    "mae_difference_candidate_minus_reference": -7.287755124346365,
    "n_resamples": 2000,
    "reference_mae": 23.68614780792545,
    "rows": 1160,
    "seed": 42
  },
  "decision_status": "learned_significant_improvement_selected",
  "learned_improvement_status": "statistically_clear",
  "reference_metrics": {
    "candidate_name": "age_position_adjusted",
    "candidate_source": "baseline",
    "position": "TE",
    "target_name": "fantasy_points_total",
    "test_mae": 22.04052262824578,
    "test_rows": 237,
    "test_season": 2025,
    "validation_mae": 23.68614780792545,
    "validation_rows": 1160,
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
      "empirical_coverage_p10_p90": 0.8438818565400844,
      "evaluation_scope": "test",
      "mean_interval_width_p10_p90": 54.488018457273746,
      "pinball_loss_p10": 4.234602769789839,
      "pinball_loss_p50": 6.658045374611642,
      "pinball_loss_p90": 5.997033919847159,
      "position": "TE",
      "prediction_season": 2025,
      "projection_tier": "all",
      "rows": 237,
      "target_name": "fantasy_points_total"
    },
    {
      "candidate_name": "hist_gradient_boosting",
      "empirical_coverage_p10_p90": 0.4745762711864407,
      "evaluation_scope": "test",
      "mean_interval_width_p10_p90": 54.48801845727377,
      "pinball_loss_p10": 8.840347295135736,
      "pinball_loss_p50": 18.2746487378718,
      "pinball_loss_p90": 12.931378921650703,
      "position": "TE",
      "prediction_season": 2025,
      "projection_tier": "top",
      "rows": 59,
      "target_name": "fantasy_points_total"
    },
    {
      "candidate_name": "hist_gradient_boosting",
      "empirical_coverage_p10_p90": 0.9495798319327731,
      "evaluation_scope": "test",
      "mean_interval_width_p10_p90": 54.48801845727375,
      "pinball_loss_p10": 2.7401303360855374,
      "pinball_loss_p50": 3.9843192757187644,
      "pinball_loss_p90": 4.141270838331718,
      "position": "TE",
      "prediction_season": 2025,
      "projection_tier": "middle",
      "rows": 119,
      "target_name": "fantasy_points_total"
    },
    {
      "candidate_name": "hist_gradient_boosting",
      "empirical_coverage_p10_p90": 1.0,
      "evaluation_scope": "test",
      "mean_interval_width_p10_p90": 54.48801845727377,
      "pinball_loss_p10": 2.6431331531017688,
      "pinball_loss_p50": 0.43421160064389586,
      "pinball_loss_p90": 2.8056686926256065,
      "position": "TE",
      "prediction_season": 2025,
      "projection_tier": "lower",
      "rows": 59,
      "target_name": "fantasy_points_total"
    },
    {
      "candidate_name": "hist_gradient_boosting",
      "empirical_coverage_p10_p90": 0.8311111111111111,
      "evaluation_scope": "validation",
      "mean_interval_width_p10_p90": 62.61530712051264,
      "pinball_loss_p10": 4.79914361219474,
      "pinball_loss_p50": 8.948031408129307,
      "pinball_loss_p90": 7.733010064264353,
      "position": "TE",
      "prediction_season": 2020,
      "projection_tier": "all",
      "rows": 225,
      "target_name": "fantasy_points_total"
    },
    {
      "candidate_name": "hist_gradient_boosting",
      "empirical_coverage_p10_p90": 0.5178571428571429,
      "evaluation_scope": "validation",
      "mean_interval_width_p10_p90": 62.61530712051264,
      "pinball_loss_p10": 9.855176614041378,
      "pinball_loss_p50": 20.267400319236447,
      "pinball_loss_p90": 14.150663189379012,
      "position": "TE",
      "prediction_season": 2020,
      "projection_tier": "top",
      "rows": 56,
      "target_name": "fantasy_points_total"
    },
    {
      "candidate_name": "hist_gradient_boosting",
      "empirical_coverage_p10_p90": 0.9026548672566371,
      "evaluation_scope": "validation",
      "mean_interval_width_p10_p90": 62.61530712051263,
      "pinball_loss_p10": 3.174580409372754,
      "pinball_loss_p50": 6.959239531807704,
      "pinball_loss_p90": 6.779064089183735,
      "position": "TE",
      "prediction_season": 2020,
      "projection_tier": "middle",
      "rows": 113,
      "target_name": "fantasy_points_total"
    },
    {
      "candidate_name": "hist_gradient_boosting",
      "empirical_coverage_p10_p90": 1.0,
      "evaluation_scope": "validation",
      "mean_interval_width_p10_p90": 62.61530712051264,
      "pinball_loss_p10": 3.0212470731853247,
      "pinball_loss_p50": 1.6417603903139744,
      "pinball_loss_p90": 3.2402836388659395,
      "position": "TE",
      "prediction_season": 2020,
      "projection_tier": "lower",
      "rows": 56,
      "target_name": "fantasy_points_total"
    },
    {
      "candidate_name": "hist_gradient_boosting",
      "empirical_coverage_p10_p90": 0.7991266375545851,
      "evaluation_scope": "validation",
      "mean_interval_width_p10_p90": 59.60779988044251,
      "pinball_loss_p10": 4.691714481954102,
      "pinball_loss_p50": 9.115287062776414,
      "pinball_loss_p90": 7.374000232964289,
      "position": "TE",
      "prediction_season": 2021,
      "projection_tier": "all",
      "rows": 229,
      "target_name": "fantasy_points_total"
    },
    {
      "candidate_name": "hist_gradient_boosting",
      "empirical_coverage_p10_p90": 0.42105263157894735,
      "evaluation_scope": "validation",
      "mean_interval_width_p10_p90": 59.607799880442535,
      "pinball_loss_p10": 10.847596321869272,
      "pinball_loss_p50": 21.69690889140862,
      "pinball_loss_p90": 14.901891158459893,
      "position": "TE",
      "prediction_season": 2021,
      "projection_tier": "top",
      "rows": 57,
      "target_name": "fantasy_points_total"
    },
    {
      "candidate_name": "hist_gradient_boosting",
      "empirical_coverage_p10_p90": 0.8869565217391304,
      "evaluation_scope": "validation",
      "mean_interval_width_p10_p90": 59.607799880442506,
      "pinball_loss_p10": 2.666205412346192,
      "pinball_loss_p50": 6.801160273344976,
      "pinball_loss_p90": 5.643041753036648,
      "position": "TE",
      "prediction_season": 2021,
      "projection_tier": "middle",
      "rows": 115,
      "target_name": "fantasy_points_total"
    },
    {
      "candidate_name": "hist_gradient_boosting",
      "empirical_coverage_p10_p90": 1.0,
      "evaluation_scope": "validation",
      "mean_interval_width_p10_p90": 59.607799880442535,
      "pinball_loss_p10": 2.6223860280899727,
      "pinball_loss_p50": 1.202517528611133,
      "pinball_loss_p90": 3.3383939599542796,
      "position": "TE",
      "prediction_season": 2021,
      "projection_tier": "lower",
      "rows": 57,
      "target_name": "fantasy_points_total"
    },
    {
      "candidate_name": "hist_gradient_boosting",
      "empirical_coverage_p10_p90": 0.7948717948717948,
      "evaluation_scope": "validation",
      "mean_interval_width_p10_p90": 63.63127372483896,
      "pinball_loss_p10": 4.802579853037262,
      "pinball_loss_p50": 7.789459200409271,
      "pinball_loss_p90": 5.678040448875486,
      "position": "TE",
      "prediction_season": 2022,
      "projection_tier": "all",
      "rows": 234,
      "target_name": "fantasy_points_total"
    },
    {
      "candidate_name": "hist_gradient_boosting",
      "empirical_coverage_p10_p90": 0.3050847457627119,
      "evaluation_scope": "validation",
      "mean_interval_width_p10_p90": 63.631273724838984,
      "pinball_loss_p10": 11.965765322232599,
      "pinball_loss_p50": 19.930984020700546,
      "pinball_loss_p90": 9.892321673741801,
      "position": "TE",
      "prediction_season": 2022,
      "projection_tier": "top",
      "rows": 59,
      "target_name": "fantasy_points_total"
    },
    {
      "candidate_name": "hist_gradient_boosting",
      "empirical_coverage_p10_p90": 0.9396551724137931,
      "evaluation_scope": "validation",
      "mean_interval_width_p10_p90": 63.63127372483897,
      "pinball_loss_p10": 2.3655345471173304,
      "pinball_loss_p50": 4.915407380193264,
      "pinball_loss_p90": 4.422512891749422,
      "position": "TE",
      "prediction_season": 2022,
      "projection_tier": "middle",
      "rows": 116,
      "target_name": "fantasy_points_total"
    },
    {
      "candidate_name": "hist_gradient_boosting",
      "empirical_coverage_p10_p90": 1.0,
      "evaluation_scope": "validation",
      "mean_interval_width_p10_p90": 63.631273724838984,
      "pinball_loss_p10": 2.4308732903963617,
      "pinball_loss_p50": 1.298612535118957,
      "pinball_loss_p90": 3.932254082087536,
      "position": "TE",
      "prediction_season": 2022,
      "projection_tier": "lower",
      "rows": 59,
      "target_name": "fantasy_points_total"
    },
    {
      "candidate_name": "hist_gradient_boosting",
      "empirical_coverage_p10_p90": 0.8085106382978723,
      "evaluation_scope": "validation",
      "mean_interval_width_p10_p90": 58.41147286891376,
      "pinball_loss_p10": 4.8239896640416315,
      "pinball_loss_p50": 7.662385596300192,
      "pinball_loss_p90": 6.276284675410588,
      "position": "TE",
      "prediction_season": 2023,
      "projection_tier": "all",
      "rows": 235,
      "target_name": "fantasy_points_total"
    },
    {
      "candidate_name": "hist_gradient_boosting",
      "empirical_coverage_p10_p90": 0.4067796610169492,
      "evaluation_scope": "validation",
      "mean_interval_width_p10_p90": 58.41147286891378,
      "pinball_loss_p10": 11.773984205391487,
      "pinball_loss_p50": 20.317033165701933,
      "pinball_loss_p90": 12.308082431448671,
      "position": "TE",
      "prediction_season": 2023,
      "projection_tier": "top",
      "rows": 59,
      "target_name": "fantasy_points_total"
    },
    {
      "candidate_name": "hist_gradient_boosting",
      "empirical_coverage_p10_p90": 0.9230769230769231,
      "evaluation_scope": "validation",
      "mean_interval_width_p10_p90": 58.41147286891376,
      "pinball_loss_p10": 2.4210405882131085,
      "pinball_loss_p50": 4.4249579451789325,
      "pinball_loss_p90": 4.755200163404163,
      "position": "TE",
      "prediction_season": 2023,
      "projection_tier": "middle",
      "rows": 117,
      "target_name": "fantasy_points_total"
    },
    {
      "candidate_name": "hist_gradient_boosting",
      "empirical_coverage_p10_p90": 0.9830508474576272,
      "evaluation_scope": "validation",
      "mean_interval_width_p10_p90": 58.41147286891377,
      "pinball_loss_p10": 2.639165323911051,
      "pinball_loss_p50": 1.4277216740372143,
      "pinball_loss_p90": 3.2608748499615205,
      "position": "TE",
      "prediction_season": 2023,
      "projection_tier": "lower",
      "rows": 59,
      "target_name": "fantasy_points_total"
    },
    {
      "candidate_name": "hist_gradient_boosting",
      "empirical_coverage_p10_p90": 0.8354430379746836,
      "evaluation_scope": "validation",
      "mean_interval_width_p10_p90": 58.37340188241706,
      "pinball_loss_p10": 4.546149643109817,
      "pinball_loss_p50": 7.5399404398509,
      "pinball_loss_p90": 6.590956164111538,
      "position": "TE",
      "prediction_season": 2024,
      "projection_tier": "all",
      "rows": 237,
      "target_name": "fantasy_points_total"
    },
    {
      "candidate_name": "hist_gradient_boosting",
      "empirical_coverage_p10_p90": 0.4576271186440678,
      "evaluation_scope": "validation",
      "mean_interval_width_p10_p90": 58.37340188241707,
      "pinball_loss_p10": 10.152757455822357,
      "pinball_loss_p50": 21.043792735890705,
      "pinball_loss_p90": 14.859565701818568,
      "position": "TE",
      "prediction_season": 2024,
      "projection_tier": "top",
      "rows": 59,
      "target_name": "fantasy_points_total"
    },
    {
      "candidate_name": "hist_gradient_boosting",
      "empirical_coverage_p10_p90": 0.9411764705882353,
      "evaluation_scope": "validation",
      "mean_interval_width_p10_p90": 58.37340188241706,
      "pinball_loss_p10": 2.6945437158263066,
      "pinball_loss_p50": 4.264340670089036,
      "pinball_loss_p90": 4.190867535471046,
      "position": "TE",
      "prediction_season": 2024,
      "projection_tier": "middle",
      "rows": 119,
      "target_name": "fantasy_points_total"
    },
    {
      "candidate_name": "hist_gradient_boosting",
      "empirical_coverage_p10_p90": 1.0,
      "evaluation_scope": "validation",
      "mean_interval_width_p10_p90": 58.37340188241707,
      "pinball_loss_p10": 2.6741368362741773,
      "pinball_loss_p50": 0.642806323500278,
      "pinball_loss_p90": 3.1632033519675296,
      "position": "TE",
      "prediction_season": 2024,
      "projection_tier": "lower",
      "rows": 59,
      "target_name": "fantasy_points_total"
    }
  ],
  "empirical_not_guaranteed": true,
  "method": "training-only signed out-of-fold residual quantiles",
  "operational_center": "training_only_residual_adjusted_p50",
  "residual_rows": 709,
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
      "feature": "lag1_fantasy_points_per_game",
      "interpretation": "This explanation is associative, not causal; changing a feature here does not establish that the feature causes the prediction to change.",
      "method": "one_way_average_partial_dependence",
      "points": [
        {
          "average_prediction": 21.58134753995825,
          "feature_value": 0.0
        },
        {
          "average_prediction": 21.58134753995825,
          "feature_value": 1.019685828877005
        },
        {
          "average_prediction": 21.58134753995825,
          "feature_value": 2.03937165775401
        },
        {
          "average_prediction": 22.703531171170848,
          "feature_value": 3.0590574866310147
        },
        {
          "average_prediction": 28.36366695152982,
          "feature_value": 4.07874331550802
        },
        {
          "average_prediction": 27.380081283551217,
          "feature_value": 5.098429144385025
        },
        {
          "average_prediction": 26.984178575283472,
          "feature_value": 6.1181149732620295
        },
        {
          "average_prediction": 39.40250398993963,
          "feature_value": 7.137800802139035
        },
        {
          "average_prediction": 36.17379877422488,
          "feature_value": 8.15748663101604
        },
        {
          "average_prediction": 35.487635271676275,
          "feature_value": 9.177172459893045
        },
        {
          "average_prediction": 49.64803959531808,
          "feature_value": 10.19685828877005
        },
        {
          "average_prediction": 49.31190375278303,
          "feature_value": 11.216544117647056
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
          "average_prediction": 16.258966129665197,
          "feature_value": 0.0
        },
        {
          "average_prediction": 17.768079157862235,
          "feature_value": 15.872727272727275
        },
        {
          "average_prediction": 22.45234821465061,
          "feature_value": 31.74545454545455
        },
        {
          "average_prediction": 37.3398368502331,
          "feature_value": 47.618181818181824
        },
        {
          "average_prediction": 35.70018103757595,
          "feature_value": 63.4909090909091
        },
        {
          "average_prediction": 47.147005609503445,
          "feature_value": 79.36363636363637
        },
        {
          "average_prediction": 48.28369762986095,
          "feature_value": 95.23636363636365
        },
        {
          "average_prediction": 48.68897679553518,
          "feature_value": 111.10909090909092
        },
        {
          "average_prediction": 52.540889920732894,
          "feature_value": 126.9818181818182
        },
        {
          "average_prediction": 52.075847819320494,
          "feature_value": 142.85454545454547
        },
        {
          "average_prediction": 52.81681123502198,
          "feature_value": 158.72727272727275
        },
        {
          "average_prediction": 52.04038896964911,
          "feature_value": 174.60000000000002
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
          "average_prediction": 21.90249269245783,
          "feature_value": 0.0
        },
        {
          "average_prediction": 21.90249269245783,
          "feature_value": 4.124194890077242
        },
        {
          "average_prediction": 23.183649012599034,
          "feature_value": 8.248389780154485
        },
        {
          "average_prediction": 23.183649012599034,
          "feature_value": 12.372584670231728
        },
        {
          "average_prediction": 33.13050464119738,
          "feature_value": 16.49677956030897
        },
        {
          "average_prediction": 23.998728170510955,
          "feature_value": 20.62097445038621
        },
        {
          "average_prediction": 27.01612636008618,
          "feature_value": 24.745169340463455
        },
        {
          "average_prediction": 27.120410394224873,
          "feature_value": 28.869364230540697
        },
        {
          "average_prediction": 32.34209422744504,
          "feature_value": 32.99355912061794
        },
        {
          "average_prediction": 40.44274812918735,
          "feature_value": 37.11775401069518
        },
        {
          "average_prediction": 39.366321652290964,
          "feature_value": 41.24194890077242
        },
        {
          "average_prediction": 37.70860788360834,
          "feature_value": 45.36614379084966
        }
      ],
      "response_status": "stable_numeric_grid"
    }
  ],
  "importance": [
    {
      "explanation_scope": "registered_final_artifact_descriptive_on_2025_training_rows",
      "feature": "lag1_fantasy_points_total",
      "importance_mean": 9.269869493401666,
      "importance_std": 0.9218632300834078,
      "rank": 1
    },
    {
      "explanation_scope": "registered_final_artifact_descriptive_on_2025_training_rows",
      "feature": "lag1_fantasy_points_per_game",
      "importance_mean": 4.237208163135723,
      "importance_std": 0.43607097243574783,
      "rank": 2
    },
    {
      "explanation_scope": "registered_final_artifact_descriptive_on_2025_training_rows",
      "feature": "weighted_3yr_receiving_yards_per_game",
      "importance_mean": 3.0318806939248177,
      "importance_std": 0.3279040960653606,
      "rank": 3
    },
    {
      "explanation_scope": "registered_final_artifact_descriptive_on_2025_training_rows",
      "feature": "age_at_cutoff",
      "importance_mean": 2.4733592805512514,
      "importance_std": 0.29336461601205416,
      "rank": 4
    },
    {
      "explanation_scope": "registered_final_artifact_descriptive_on_2025_training_rows",
      "feature": "missing_lag1",
      "importance_mean": 1.2975171163699226,
      "importance_std": 0.07117348809301474,
      "rank": 5
    },
    {
      "explanation_scope": "registered_final_artifact_descriptive_on_2025_training_rows",
      "feature": "weighted_3yr_games_active",
      "importance_mean": 1.288565463940693,
      "importance_std": 0.15693189122328136,
      "rank": 6
    },
    {
      "explanation_scope": "registered_final_artifact_descriptive_on_2025_training_rows",
      "feature": "draft_pick",
      "importance_mean": 0.8925426695195423,
      "importance_std": 0.0658170517012858,
      "rank": 7
    },
    {
      "explanation_scope": "registered_final_artifact_descriptive_on_2025_training_rows",
      "feature": "weighted_3yr_fantasy_points_per_game",
      "importance_mean": 0.8472740314516933,
      "importance_std": 0.18462625811370853,
      "rank": 8
    },
    {
      "explanation_scope": "registered_final_artifact_descriptive_on_2025_training_rows",
      "feature": "lag1_stat_games",
      "importance_mean": 0.8375626427909605,
      "importance_std": 0.09669453249093897,
      "rank": 9
    },
    {
      "explanation_scope": "registered_final_artifact_descriptive_on_2025_training_rows",
      "feature": "weighted_3yr_receiving_tds_per_game",
      "importance_mean": 0.732268339631889,
      "importance_std": 0.08083439345182104,
      "rank": 10
    },
    {
      "explanation_scope": "registered_final_artifact_descriptive_on_2025_training_rows",
      "feature": "weighted_3yr_receptions_per_game",
      "importance_mean": 0.6076117999639183,
      "importance_std": 0.08590501154892007,
      "rank": 11
    },
    {
      "explanation_scope": "registered_final_artifact_descriptive_on_2025_training_rows",
      "feature": "height_inches",
      "importance_mean": 0.5644935735950473,
      "importance_std": 0.1130454188752024,
      "rank": 12
    },
    {
      "explanation_scope": "registered_final_artifact_descriptive_on_2025_training_rows",
      "feature": "weighted_3yr_two_point_conversions_per_game",
      "importance_mean": 0.5033723416711535,
      "importance_std": 0.14776738805315412,
      "rank": 13
    },
    {
      "explanation_scope": "registered_final_artifact_descriptive_on_2025_training_rows",
      "feature": "lag1_games_active",
      "importance_mean": 0.4928829268445032,
      "importance_std": 0.0520076141163523,
      "rank": 14
    },
    {
      "explanation_scope": "registered_final_artifact_descriptive_on_2025_training_rows",
      "feature": "weighted_3yr_rushing_yards_per_game",
      "importance_mean": 0.4760630881251792,
      "importance_std": 0.05047430479099036,
      "rank": 15
    },
    {
      "explanation_scope": "registered_final_artifact_descriptive_on_2025_training_rows",
      "feature": "nfl_experience_years",
      "importance_mean": 0.4473098190594545,
      "importance_std": 0.19157130515743648,
      "rank": 16
    },
    {
      "explanation_scope": "registered_final_artifact_descriptive_on_2025_training_rows",
      "feature": "weighted_3yr_targets_per_game",
      "importance_mean": 0.40057490855380246,
      "importance_std": 0.034865902059254765,
      "rank": 17
    },
    {
      "explanation_scope": "registered_final_artifact_descriptive_on_2025_training_rows",
      "feature": "previous_team",
      "importance_mean": 0.18150174899003807,
      "importance_std": 0.09155975392897399,
      "rank": 18
    },
    {
      "explanation_scope": "registered_final_artifact_descriptive_on_2025_training_rows",
      "feature": "weighted_3yr_carries_per_game",
      "importance_mean": 0.17838534419334984,
      "importance_std": 0.065288061020122,
      "rank": 19
    },
    {
      "explanation_scope": "registered_final_artifact_descriptive_on_2025_training_rows",
      "feature": "weighted_3yr_fumbles_lost_per_game",
      "importance_mean": 0.17681806789062904,
      "importance_std": 0.10659885387673468,
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

- Project-relative path: `models/artifacts/phase4-7ae8e9aed04bffca00c0/attempt-866987f75a2c406693cf892d49adc975/TE/fantasy_points_total/hist_gradient_boosting.joblib`
- SHA-256: `1600f9f998ecb07e2648c126c9206faa952022aaa6e2582200d64961bf934510`

## Additional metadata

````json
{
  "publication_id": "attempt-866987f75a2c406693cf892d49adc975"
}
````
