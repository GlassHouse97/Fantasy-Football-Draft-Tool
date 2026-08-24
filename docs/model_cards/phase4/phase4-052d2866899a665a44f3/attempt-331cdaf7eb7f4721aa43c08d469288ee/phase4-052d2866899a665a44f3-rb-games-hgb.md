# Model Card: phase4-052d2866899a665a44f3-rb-games-hgb

- Model ID: `phase4-052d2866899a665a44f3-rb-games-hgb`
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
  "draft_relevant_validation_mae": 3.6774342878393673,
  "draft_relevant_validation_rows": 120,
  "draft_relevant_validation_signed_bias": -1.017637141647351,
  "position": "RB",
  "target_name": "games_active",
  "test_mae": 2.6712250004053235,
  "test_rows": 294,
  "test_season": 2025,
  "validation_mae": 3.005243844162158,
  "validation_rows": 1483,
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
    "candidate_mae": 3.6774342878393673,
    "ci95_lower": -0.054324727078729255,
    "ci95_upper": 0.9127073383284123,
    "direction": "uncertain",
    "mae_difference_candidate_minus_reference": 0.4269294747641088,
    "n_resamples": 2000,
    "reference_mae": 3.2505048130752585,
    "rows": 120,
    "seed": 42
  },
  "decision_status": "learned_draft_relevant_regression_baseline_retained",
  "learned_improvement_status": "regression",
  "reference_metrics": {
    "candidate_name": "position_shrinkage",
    "candidate_source": "baseline",
    "draft_relevant_validation_mae": 3.2505048130752585,
    "draft_relevant_validation_rows": 120,
    "draft_relevant_validation_signed_bias": 1.0133315518536432,
    "position": "RB",
    "target_name": "games_active",
    "test_mae": 7.930435127876736,
    "test_rows": 294,
    "test_season": 2025,
    "validation_mae": 7.2616850855011,
    "validation_rows": 1483,
    "validation_seasons": [
      2020,
      2021,
      2022,
      2023,
      2024
    ],
    "validation_top_n_capture_rate": null
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
      "empirical_coverage_p10_p90": 0.7973421926910299,
      "evaluation_scope": "validation",
      "mean_interval_width_p10_p90": 8.918125928612316,
      "pinball_loss_p10": 0.5829831498169082,
      "pinball_loss_p50": 1.4503880412483927,
      "pinball_loss_p90": 0.8667663477365198,
      "position": "RB",
      "prediction_season": 2020,
      "projection_tier": "all",
      "rows": 301,
      "target_name": "games_active"
    },
    {
      "candidate_name": "hist_gradient_boosting",
      "empirical_coverage_p10_p90": 0.7368421052631579,
      "evaluation_scope": "validation",
      "mean_interval_width_p10_p90": 11.631375754057261,
      "pinball_loss_p10": 1.2574462264387436,
      "pinball_loss_p50": 2.1746316914535235,
      "pinball_loss_p90": 0.6127962141893086,
      "position": "RB",
      "prediction_season": 2020,
      "projection_tier": "top",
      "rows": 76,
      "target_name": "games_active"
    },
    {
      "candidate_name": "hist_gradient_boosting",
      "empirical_coverage_p10_p90": 0.7266666666666667,
      "evaluation_scope": "validation",
      "mean_interval_width_p10_p90": 9.04371899693095,
      "pinball_loss_p10": 0.5307467659036326,
      "pinball_loss_p50": 1.7986319457686561,
      "pinball_loss_p90": 1.1349520574924916,
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
      "mean_interval_width_p10_p90": 5.917513302190838,
      "pinball_loss_p10": 0.004000000000000001,
      "pinball_loss_p50": 0.02,
      "pinball_loss_p90": 0.5877513302190838,
      "position": "RB",
      "prediction_season": 2020,
      "projection_tier": "lower",
      "rows": 75,
      "target_name": "games_active"
    },
    {
      "candidate_name": "hist_gradient_boosting",
      "empirical_coverage_p10_p90": 0.8172757475083057,
      "evaluation_scope": "validation",
      "mean_interval_width_p10_p90": 9.263591173039176,
      "pinball_loss_p10": 0.5299530655960258,
      "pinball_loss_p50": 1.4840897261547799,
      "pinball_loss_p90": 0.864428715641337,
      "position": "RB",
      "prediction_season": 2021,
      "projection_tier": "all",
      "rows": 301,
      "target_name": "games_active"
    },
    {
      "candidate_name": "hist_gradient_boosting",
      "empirical_coverage_p10_p90": 0.7368421052631579,
      "evaluation_scope": "validation",
      "mean_interval_width_p10_p90": 11.578137573580806,
      "pinball_loss_p10": 1.087177212727741,
      "pinball_loss_p50": 2.2116637986993717,
      "pinball_loss_p90": 0.6138844328334185,
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
      "mean_interval_width_p10_p90": 9.684716925468052,
      "pinball_loss_p10": 0.4946026971806367,
      "pinball_loss_p50": 1.7674480512226152,
      "pinball_loss_p90": 1.0444810536197304,
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
      "mean_interval_width_p10_p90": 6.0759326489659,
      "pinball_loss_p10": 0.036000000000000004,
      "pinball_loss_p50": 0.18009801584059082,
      "pinball_loss_p90": 0.7582089129299081,
      "position": "RB",
      "prediction_season": 2021,
      "projection_tier": "lower",
      "rows": 75,
      "target_name": "games_active"
    },
    {
      "candidate_name": "hist_gradient_boosting",
      "empirical_coverage_p10_p90": 0.7905405405405406,
      "evaluation_scope": "validation",
      "mean_interval_width_p10_p90": 9.249636917667857,
      "pinball_loss_p10": 0.6386127120628832,
      "pinball_loss_p50": 1.5865294840886557,
      "pinball_loss_p90": 0.8108295544048437,
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
      "mean_interval_width_p10_p90": 11.109669643302967,
      "pinball_loss_p10": 1.291826196456181,
      "pinball_loss_p50": 2.3057846754144817,
      "pinball_loss_p90": 0.5375711429077636,
      "position": "RB",
      "prediction_season": 2022,
      "projection_tier": "top",
      "rows": 74,
      "target_name": "games_active"
    },
    {
      "candidate_name": "hist_gradient_boosting",
      "empirical_coverage_p10_p90": 0.7162162162162162,
      "evaluation_scope": "validation",
      "mean_interval_width_p10_p90": 9.815460151100549,
      "pinball_loss_p10": 0.6313123258976759,
      "pinball_loss_p50": 2.0130674159315847,
      "pinball_loss_p90": 1.0399756510974378,
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
      "mean_interval_width_p10_p90": 6.257957725167357,
      "pinball_loss_p10": 0.0,
      "pinball_loss_p50": 0.014198429076971652,
      "pinball_loss_p90": 0.6257957725167356,
      "position": "RB",
      "prediction_season": 2022,
      "projection_tier": "lower",
      "rows": 74,
      "target_name": "games_active"
    },
    {
      "candidate_name": "hist_gradient_boosting",
      "empirical_coverage_p10_p90": 0.7972508591065293,
      "evaluation_scope": "validation",
      "mean_interval_width_p10_p90": 9.013155954508266,
      "pinball_loss_p10": 0.6554824923931619,
      "pinball_loss_p50": 1.5556918060235279,
      "pinball_loss_p90": 0.83505997300515,
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
      "mean_interval_width_p10_p90": 10.959852044410587,
      "pinball_loss_p10": 1.4427152699711583,
      "pinball_loss_p50": 2.3406271078390404,
      "pinball_loss_p90": 0.5308319232460482,
      "position": "RB",
      "prediction_season": 2023,
      "projection_tier": "top",
      "rows": 73,
      "target_name": "games_active"
    },
    {
      "candidate_name": "hist_gradient_boosting",
      "empirical_coverage_p10_p90": 0.7172413793103448,
      "evaluation_scope": "validation",
      "mean_interval_width_p10_p90": 9.467966880068689,
      "pinball_loss_p10": 0.5739806246794178,
      "pinball_loss_p50": 1.8613470598687063,
      "pinball_loss_p90": 1.0469936618573212,
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
      "mean_interval_width_p10_p90": 6.163068300136608,
      "pinball_loss_p10": 0.030136986301369864,
      "pinball_loss_p50": 0.16363305478951065,
      "pinball_loss_p90": 0.7183238462770625,
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
          "average_prediction": 4.13279777659373,
          "feature_value": 0.0
        },
        {
          "average_prediction": 4.197927813620076,
          "feature_value": 24.124545454545455
        },
        {
          "average_prediction": 5.335786830016683,
          "feature_value": 48.24909090909091
        },
        {
          "average_prediction": 5.382387915079298,
          "feature_value": 72.37363636363636
        },
        {
          "average_prediction": 6.343415935004416,
          "feature_value": 96.49818181818182
        },
        {
          "average_prediction": 6.319217670016057,
          "feature_value": 120.62272727272727
        },
        {
          "average_prediction": 6.321501064612843,
          "feature_value": 144.74727272727273
        },
        {
          "average_prediction": 6.388966339723456,
          "feature_value": 168.87181818181818
        },
        {
          "average_prediction": 6.535840668174517,
          "feature_value": 192.99636363636364
        },
        {
          "average_prediction": 6.535840668174517,
          "feature_value": 217.1209090909091
        },
        {
          "average_prediction": 6.529244397889514,
          "feature_value": 241.24545454545455
        },
        {
          "average_prediction": 6.529244397889514,
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
          "average_prediction": 6.853430321627541,
          "feature_value": 0.0
        },
        {
          "average_prediction": 1.4579936924193888,
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
          "average_prediction": 3.924050282508261,
          "feature_value": 1.0
        },
        {
          "average_prediction": 3.9360121727756403,
          "feature_value": 2.4545454545454546
        },
        {
          "average_prediction": 4.012968116251323,
          "feature_value": 3.909090909090909
        },
        {
          "average_prediction": 4.129565215030142,
          "feature_value": 5.363636363636363
        },
        {
          "average_prediction": 4.188899689328071,
          "feature_value": 6.818181818181818
        },
        {
          "average_prediction": 4.47247826893534,
          "feature_value": 8.272727272727273
        },
        {
          "average_prediction": 4.497445942793026,
          "feature_value": 9.727272727272727
        },
        {
          "average_prediction": 4.929150891753851,
          "feature_value": 11.181818181818182
        },
        {
          "average_prediction": 5.080249345910769,
          "feature_value": 12.636363636363637
        },
        {
          "average_prediction": 5.512056136791339,
          "feature_value": 14.090909090909092
        },
        {
          "average_prediction": 5.5276184702971864,
          "feature_value": 15.545454545454547
        },
        {
          "average_prediction": 5.935437731288493,
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
      "importance_mean": 1.8327917112123147,
      "importance_std": 0.06440220377319318,
      "rank": 1
    },
    {
      "explanation_scope": "registered_final_artifact_descriptive_on_2025_training_rows",
      "feature": "lag1_fantasy_points_total",
      "importance_mean": 0.5546055337433886,
      "importance_std": 0.03276040366560515,
      "rank": 2
    },
    {
      "explanation_scope": "registered_final_artifact_descriptive_on_2025_training_rows",
      "feature": "weighted_3yr_games_active",
      "importance_mean": 0.46497198146485336,
      "importance_std": 0.03914257142234257,
      "rank": 3
    },
    {
      "explanation_scope": "registered_final_artifact_descriptive_on_2025_training_rows",
      "feature": "age_at_cutoff",
      "importance_mean": 0.33933436041234055,
      "importance_std": 0.0296229941124819,
      "rank": 4
    },
    {
      "explanation_scope": "registered_final_artifact_descriptive_on_2025_training_rows",
      "feature": "lag1_games_active",
      "importance_mean": 0.285618457411094,
      "importance_std": 0.028829827187327402,
      "rank": 5
    },
    {
      "explanation_scope": "registered_final_artifact_descriptive_on_2025_training_rows",
      "feature": "weighted_3yr_carries_per_game",
      "importance_mean": 0.18169784468070774,
      "importance_std": 0.03492291876481238,
      "rank": 6
    },
    {
      "explanation_scope": "registered_final_artifact_descriptive_on_2025_training_rows",
      "feature": "weighted_3yr_receiving_yards_per_game",
      "importance_mean": 0.16902939202909587,
      "importance_std": 0.02978640951932081,
      "rank": 7
    },
    {
      "explanation_scope": "registered_final_artifact_descriptive_on_2025_training_rows",
      "feature": "nfl_experience_years",
      "importance_mean": 0.16445331752497844,
      "importance_std": 0.015006074784027846,
      "rank": 8
    },
    {
      "explanation_scope": "registered_final_artifact_descriptive_on_2025_training_rows",
      "feature": "lag1_stat_games",
      "importance_mean": 0.16002341774267262,
      "importance_std": 0.01938550036822283,
      "rank": 9
    },
    {
      "explanation_scope": "registered_final_artifact_descriptive_on_2025_training_rows",
      "feature": "weighted_3yr_rushing_yards_per_game",
      "importance_mean": 0.14001335966248957,
      "importance_std": 0.01180585011035808,
      "rank": 10
    },
    {
      "explanation_scope": "registered_final_artifact_descriptive_on_2025_training_rows",
      "feature": "draft_pick",
      "importance_mean": 0.12402376150515462,
      "importance_std": 0.01515037791182969,
      "rank": 11
    },
    {
      "explanation_scope": "registered_final_artifact_descriptive_on_2025_training_rows",
      "feature": "lag1_fantasy_points_per_game",
      "importance_mean": 0.1160480815536749,
      "importance_std": 0.011997621622057192,
      "rank": 12
    },
    {
      "explanation_scope": "registered_final_artifact_descriptive_on_2025_training_rows",
      "feature": "weighted_3yr_fantasy_points_per_game",
      "importance_mean": 0.10991980895839264,
      "importance_std": 0.014271969821644144,
      "rank": 13
    },
    {
      "explanation_scope": "registered_final_artifact_descriptive_on_2025_training_rows",
      "feature": "weighted_3yr_targets_per_game",
      "importance_mean": 0.08868294710112065,
      "importance_std": 0.010826532595062959,
      "rank": 14
    },
    {
      "explanation_scope": "registered_final_artifact_descriptive_on_2025_training_rows",
      "feature": "weighted_3yr_receptions_per_game",
      "importance_mean": 0.07742566349671058,
      "importance_std": 0.010241566365018774,
      "rank": 15
    },
    {
      "explanation_scope": "registered_final_artifact_descriptive_on_2025_training_rows",
      "feature": "weighted_3yr_fumbles_lost_per_game",
      "importance_mean": 0.06834521961042661,
      "importance_std": 0.005734644101513817,
      "rank": 16
    },
    {
      "explanation_scope": "registered_final_artifact_descriptive_on_2025_training_rows",
      "feature": "previous_team",
      "importance_mean": 0.03744276418043384,
      "importance_std": 0.023077254229772352,
      "rank": 17
    },
    {
      "explanation_scope": "registered_final_artifact_descriptive_on_2025_training_rows",
      "feature": "height_inches",
      "importance_mean": 0.03473316904415533,
      "importance_std": 0.005294365564502326,
      "rank": 18
    },
    {
      "explanation_scope": "registered_final_artifact_descriptive_on_2025_training_rows",
      "feature": "weighted_3yr_two_point_conversions_per_game",
      "importance_mean": 0.03428549191948553,
      "importance_std": 0.008589640908274812,
      "rank": 19
    },
    {
      "explanation_scope": "registered_final_artifact_descriptive_on_2025_training_rows",
      "feature": "history_seasons",
      "importance_mean": 0.0319204139253265,
      "importance_std": 0.004712271937132002,
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

- Project-relative path: `models/artifacts/phase4-052d2866899a665a44f3/attempt-331cdaf7eb7f4721aa43c08d469288ee/RB/games_active/hist_gradient_boosting.joblib`
- SHA-256: `6306bbe6c34c95ef7d36828ad88ebaed35de5724796c98c46ce5206239f2166a`

## Additional metadata

````json
{
  "publication_id": "attempt-331cdaf7eb7f4721aa43c08d469288ee"
}
````
