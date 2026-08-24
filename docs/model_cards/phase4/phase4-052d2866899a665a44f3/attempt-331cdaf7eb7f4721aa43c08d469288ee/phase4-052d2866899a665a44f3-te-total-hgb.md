# Model Card: phase4-052d2866899a665a44f3-te-total-hgb

- Model ID: `phase4-052d2866899a665a44f3-te-total-hgb`
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
  "draft_relevant_validation_mae": 51.52220992607089,
  "draft_relevant_validation_rows": 60,
  "draft_relevant_validation_signed_bias": -6.518849852099317,
  "position": "TE",
  "target_name": "fantasy_points_total",
  "test_mae": 13.325465648230487,
  "test_rows": 237,
  "test_season": 2025,
  "validation_mae": 16.380721931110866,
  "validation_rows": 1160,
  "validation_seasons": [
    2020,
    2021,
    2022,
    2023,
    2024
  ],
  "validation_top_n_capture_rate": 0.4833333333333334
}
````

## Comparison with transparent baselines

````json
{
  "best_learned_vs_baseline_bootstrap": {
    "candidate_mae": 46.90514606867475,
    "ci95_lower": -7.509098433930528,
    "ci95_upper": 9.708858637307124,
    "direction": "uncertain",
    "mae_difference_candidate_minus_reference": 1.41468133783939,
    "n_resamples": 2000,
    "reference_mae": 45.49046473083536,
    "rows": 60,
    "seed": 42
  },
  "decision_status": "learned_draft_relevant_regression_baseline_retained",
  "learned_improvement_status": "regression",
  "reference_metrics": {
    "candidate_name": "position_shrinkage",
    "candidate_source": "baseline",
    "draft_relevant_validation_mae": 45.49046473083536,
    "draft_relevant_validation_rows": 60,
    "draft_relevant_validation_signed_bias": 6.520829240626062,
    "position": "TE",
    "target_name": "fantasy_points_total",
    "test_mae": 27.65932959579542,
    "test_rows": 237,
    "test_season": 2025,
    "validation_mae": 29.423851137143856,
    "validation_rows": 1160,
    "validation_seasons": [
      2020,
      2021,
      2022,
      2023,
      2024
    ],
    "validation_top_n_capture_rate": 0.4833333333333333
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
      "empirical_coverage_p10_p90": 0.8438818565400844,
      "evaluation_scope": "test",
      "mean_interval_width_p10_p90": 54.299669078740436,
      "pinball_loss_p10": 4.235192487094951,
      "pinball_loss_p50": 6.662732824115244,
      "pinball_loss_p90": 5.992812463072365,
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
      "mean_interval_width_p10_p90": 54.29966907874046,
      "pinball_loss_p10": 8.835318653102226,
      "pinball_loss_p50": 18.271419402201406,
      "pinball_loss_p90": 12.956995385101651,
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
      "mean_interval_width_p10_p90": 54.299669078740436,
      "pinball_loss_p10": 2.742582318564687,
      "pinball_loss_p50": 3.9817609046379747,
      "pinball_loss_p90": 4.130716819007213,
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
      "mean_interval_width_p10_p90": 54.29966907874046,
      "pinball_loss_p10": 2.645585135580917,
      "pinball_loss_p50": 0.4614302870086614,
      "pinball_loss_p90": 2.7843817722931283,
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
      "empirical_coverage_p10_p90": 0.8270042194092827,
      "evaluation_scope": "validation",
      "mean_interval_width_p10_p90": 58.37340188241706,
      "pinball_loss_p10": 4.476746131801646,
      "pinball_loss_p50": 7.496695560392812,
      "pinball_loss_p90": 6.617145726869151,
      "position": "TE",
      "prediction_season": 2024,
      "projection_tier": "all",
      "rows": 237,
      "target_name": "fantasy_points_total"
    },
    {
      "candidate_name": "hist_gradient_boosting",
      "empirical_coverage_p10_p90": 0.4406779661016949,
      "evaluation_scope": "validation",
      "mean_interval_width_p10_p90": 58.37340188241707,
      "pinball_loss_p10": 9.77825379721749,
      "pinball_loss_p50": 20.47291866849065,
      "pinball_loss_p90": 14.2574393625863,
      "position": "TE",
      "prediction_season": 2024,
      "projection_tier": "top",
      "rows": 59,
      "target_name": "fantasy_points_total"
    },
    {
      "candidate_name": "hist_gradient_boosting",
      "empirical_coverage_p10_p90": 0.9327731092436975,
      "evaluation_scope": "validation",
      "mean_interval_width_p10_p90": 58.37340188241706,
      "pinball_loss_p10": 2.75218495539127,
      "pinball_loss_p50": 4.512186491080065,
      "pinball_loss_p90": 4.531373052762464,
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
      "pinball_loss_p10": 2.6535906696541898,
      "pinball_loss_p50": 0.5400754904003394,
      "pinball_loss_p90": 3.183749518587517,
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
      "feature": "lag1_fantasy_points_per_game",
      "interpretation": "This explanation is associative, not causal; changing a feature here does not establish that the feature causes the prediction to change.",
      "method": "one_way_average_partial_dependence",
      "points": [
        {
          "average_prediction": 21.40218897197841,
          "feature_value": 0.0
        },
        {
          "average_prediction": 21.40218897197841,
          "feature_value": 1.019685828877005
        },
        {
          "average_prediction": 21.19518034690361,
          "feature_value": 2.03937165775401
        },
        {
          "average_prediction": 22.59255634808137,
          "feature_value": 3.0590574866310147
        },
        {
          "average_prediction": 29.543282601250603,
          "feature_value": 4.07874331550802
        },
        {
          "average_prediction": 27.985133844815596,
          "feature_value": 5.098429144385025
        },
        {
          "average_prediction": 27.489668232634017,
          "feature_value": 6.1181149732620295
        },
        {
          "average_prediction": 38.57790691521224,
          "feature_value": 7.137800802139035
        },
        {
          "average_prediction": 35.55647288669158,
          "feature_value": 8.15748663101604
        },
        {
          "average_prediction": 34.902259914150214,
          "feature_value": 9.177172459893045
        },
        {
          "average_prediction": 53.45642388348895,
          "feature_value": 10.19685828877005
        },
        {
          "average_prediction": 51.059870360825116,
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
          "average_prediction": 16.472638434495984,
          "feature_value": 0.0
        },
        {
          "average_prediction": 17.98175146269302,
          "feature_value": 15.872727272727275
        },
        {
          "average_prediction": 22.635924065816344,
          "feature_value": 31.74545454545455
        },
        {
          "average_prediction": 37.48074021381331,
          "feature_value": 47.618181818181824
        },
        {
          "average_prediction": 36.80654630680615,
          "feature_value": 63.4909090909091
        },
        {
          "average_prediction": 48.24628165872143,
          "feature_value": 79.36363636363637
        },
        {
          "average_prediction": 49.11311653424605,
          "feature_value": 95.23636363636365
        },
        {
          "average_prediction": 49.26641505139688,
          "feature_value": 111.10909090909092
        },
        {
          "average_prediction": 54.55679814297546,
          "feature_value": 126.9818181818182
        },
        {
          "average_prediction": 54.596464721045606,
          "feature_value": 142.85454545454547
        },
        {
          "average_prediction": 54.08827176672929,
          "feature_value": 158.72727272727275
        },
        {
          "average_prediction": 52.87714322924351,
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
          "average_prediction": 21.97272060163832,
          "feature_value": 0.0
        },
        {
          "average_prediction": 21.97272060163832,
          "feature_value": 4.124194890077242
        },
        {
          "average_prediction": 22.920281948797758,
          "feature_value": 8.248389780154485
        },
        {
          "average_prediction": 22.886552356086685,
          "feature_value": 12.372584670231728
        },
        {
          "average_prediction": 31.691021440629306,
          "feature_value": 16.49677956030897
        },
        {
          "average_prediction": 23.439883556055946,
          "feature_value": 20.62097445038621
        },
        {
          "average_prediction": 25.923034306214504,
          "feature_value": 24.745169340463455
        },
        {
          "average_prediction": 26.20857263192807,
          "feature_value": 28.869364230540697
        },
        {
          "average_prediction": 32.11427448049717,
          "feature_value": 32.99355912061794
        },
        {
          "average_prediction": 40.34265507418406,
          "feature_value": 37.11775401069518
        },
        {
          "average_prediction": 38.76882636806682,
          "feature_value": 41.24194890077242
        },
        {
          "average_prediction": 33.45732097776743,
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
      "importance_mean": 9.336043548001147,
      "importance_std": 0.892430142402104,
      "rank": 1
    },
    {
      "explanation_scope": "registered_final_artifact_descriptive_on_2025_training_rows",
      "feature": "lag1_fantasy_points_per_game",
      "importance_mean": 4.494620033308344,
      "importance_std": 0.45836581937885523,
      "rank": 2
    },
    {
      "explanation_scope": "registered_final_artifact_descriptive_on_2025_training_rows",
      "feature": "weighted_3yr_receiving_yards_per_game",
      "importance_mean": 2.5949169885414434,
      "importance_std": 0.21671608551400834,
      "rank": 3
    },
    {
      "explanation_scope": "registered_final_artifact_descriptive_on_2025_training_rows",
      "feature": "age_at_cutoff",
      "importance_mean": 2.3925518785223945,
      "importance_std": 0.21022493255987243,
      "rank": 4
    },
    {
      "explanation_scope": "registered_final_artifact_descriptive_on_2025_training_rows",
      "feature": "missing_lag1",
      "importance_mean": 1.3545253519890164,
      "importance_std": 0.06479878877292813,
      "rank": 5
    },
    {
      "explanation_scope": "registered_final_artifact_descriptive_on_2025_training_rows",
      "feature": "weighted_3yr_games_active",
      "importance_mean": 1.1417519128821838,
      "importance_std": 0.12294896140084702,
      "rank": 6
    },
    {
      "explanation_scope": "registered_final_artifact_descriptive_on_2025_training_rows",
      "feature": "weighted_3yr_fantasy_points_per_game",
      "importance_mean": 1.0327962038702636,
      "importance_std": 0.19699438967926422,
      "rank": 7
    },
    {
      "explanation_scope": "registered_final_artifact_descriptive_on_2025_training_rows",
      "feature": "lag1_stat_games",
      "importance_mean": 0.9042758753787521,
      "importance_std": 0.1059636704404487,
      "rank": 8
    },
    {
      "explanation_scope": "registered_final_artifact_descriptive_on_2025_training_rows",
      "feature": "draft_pick",
      "importance_mean": 0.7677746725267507,
      "importance_std": 0.09345311535037436,
      "rank": 9
    },
    {
      "explanation_scope": "registered_final_artifact_descriptive_on_2025_training_rows",
      "feature": "weighted_3yr_receiving_tds_per_game",
      "importance_mean": 0.6394540410436622,
      "importance_std": 0.065384848098994,
      "rank": 10
    },
    {
      "explanation_scope": "registered_final_artifact_descriptive_on_2025_training_rows",
      "feature": "weighted_3yr_receptions_per_game",
      "importance_mean": 0.5920873858784776,
      "importance_std": 0.09396409571231583,
      "rank": 11
    },
    {
      "explanation_scope": "registered_final_artifact_descriptive_on_2025_training_rows",
      "feature": "weighted_3yr_targets_per_game",
      "importance_mean": 0.504798806490357,
      "importance_std": 0.051659661753725813,
      "rank": 12
    },
    {
      "explanation_scope": "registered_final_artifact_descriptive_on_2025_training_rows",
      "feature": "nfl_experience_years",
      "importance_mean": 0.497082466026508,
      "importance_std": 0.14697708535383316,
      "rank": 13
    },
    {
      "explanation_scope": "registered_final_artifact_descriptive_on_2025_training_rows",
      "feature": "weighted_3yr_rushing_yards_per_game",
      "importance_mean": 0.49017714328031303,
      "importance_std": 0.043105101914345946,
      "rank": 14
    },
    {
      "explanation_scope": "registered_final_artifact_descriptive_on_2025_training_rows",
      "feature": "weighted_3yr_two_point_conversions_per_game",
      "importance_mean": 0.48613555392611935,
      "importance_std": 0.13851547184931445,
      "rank": 15
    },
    {
      "explanation_scope": "registered_final_artifact_descriptive_on_2025_training_rows",
      "feature": "height_inches",
      "importance_mean": 0.39726760352595286,
      "importance_std": 0.07971602119535591,
      "rank": 16
    },
    {
      "explanation_scope": "registered_final_artifact_descriptive_on_2025_training_rows",
      "feature": "lag1_games_active",
      "importance_mean": 0.3146060816267561,
      "importance_std": 0.05370904085097234,
      "rank": 17
    },
    {
      "explanation_scope": "registered_final_artifact_descriptive_on_2025_training_rows",
      "feature": "weighted_3yr_carries_per_game",
      "importance_mean": 0.19529431900169456,
      "importance_std": 0.057816447081559266,
      "rank": 18
    },
    {
      "explanation_scope": "registered_final_artifact_descriptive_on_2025_training_rows",
      "feature": "previous_team",
      "importance_mean": 0.1758576750319129,
      "importance_std": 0.07742515763378177,
      "rank": 19
    },
    {
      "explanation_scope": "registered_final_artifact_descriptive_on_2025_training_rows",
      "feature": "draft_round",
      "importance_mean": 0.15600992891576232,
      "importance_std": 0.03375205868444326,
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

- Project-relative path: `models/artifacts/phase4-052d2866899a665a44f3/attempt-331cdaf7eb7f4721aa43c08d469288ee/TE/fantasy_points_total/hist_gradient_boosting.joblib`
- SHA-256: `90616951ef8f8a1f5072b05d83b3a490f0c1a5960f628dd593cb20c1f284d1ea`

## Additional metadata

````json
{
  "publication_id": "attempt-331cdaf7eb7f4721aa43c08d469288ee"
}
````
