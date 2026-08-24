# Model Card: phase4-052d2866899a665a44f3-rb-games-ridge

- Model ID: `phase4-052d2866899a665a44f3-rb-games-ridge`
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
  "alpha": 10.0
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
  "candidate_name": "ridge",
  "candidate_source": "learned",
  "draft_relevant_validation_mae": 3.7731762328412057,
  "draft_relevant_validation_rows": 120,
  "draft_relevant_validation_signed_bias": -0.9164826390263676,
  "position": "RB",
  "target_name": "games_active",
  "test_mae": 3.0236268932768344,
  "test_rows": 294,
  "test_season": 2025,
  "validation_mae": 3.1244306339317602,
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
      "candidate_name": "ridge",
      "empirical_coverage_p10_p90": 0.7789115646258503,
      "evaluation_scope": "test",
      "mean_interval_width_p10_p90": 8.507815669261085,
      "pinball_loss_p10": 0.6047585183003367,
      "pinball_loss_p50": 1.5118134466384172,
      "pinball_loss_p90": 0.8062359603683087,
      "position": "RB",
      "prediction_season": 2025,
      "projection_tier": "all",
      "rows": 294,
      "target_name": "games_active"
    },
    {
      "candidate_name": "ridge",
      "empirical_coverage_p10_p90": 0.6891891891891891,
      "evaluation_scope": "test",
      "mean_interval_width_p10_p90": 11.109837321995967,
      "pinball_loss_p10": 1.378580162854261,
      "pinball_loss_p50": 2.4429196898499552,
      "pinball_loss_p90": 0.5580446491441329,
      "position": "RB",
      "prediction_season": 2025,
      "projection_tier": "top",
      "rows": 74,
      "target_name": "games_active"
    },
    {
      "candidate_name": "ridge",
      "empirical_coverage_p10_p90": 0.726027397260274,
      "evaluation_scope": "test",
      "mean_interval_width_p10_p90": 8.752008553633402,
      "pinball_loss_p10": 0.502630632390984,
      "pinball_loss_p50": 1.714676765356592,
      "pinball_loss_p90": 1.039005386723822,
      "position": "RB",
      "prediction_season": 2025,
      "projection_tier": "middle",
      "rows": 146,
      "target_name": "games_active"
    },
    {
      "candidate_name": "ridge",
      "empirical_coverage_p10_p90": 0.972972972972973,
      "evaluation_scope": "test",
      "mean_interval_width_p10_p90": 5.424008055467304,
      "pinball_loss_p10": 0.032432432432432434,
      "pinball_loss_p50": 0.180463358388318,
      "pinball_loss_p90": 0.5951794844586339,
      "position": "RB",
      "prediction_season": 2025,
      "projection_tier": "lower",
      "rows": 74,
      "target_name": "games_active"
    },
    {
      "candidate_name": "ridge",
      "empirical_coverage_p10_p90": 0.8039867109634552,
      "evaluation_scope": "validation",
      "mean_interval_width_p10_p90": 8.728355326292279,
      "pinball_loss_p10": 0.522698384433822,
      "pinball_loss_p50": 1.4251885901048722,
      "pinball_loss_p90": 0.8002175369466281,
      "position": "RB",
      "prediction_season": 2020,
      "projection_tier": "all",
      "rows": 301,
      "target_name": "games_active"
    },
    {
      "candidate_name": "ridge",
      "empirical_coverage_p10_p90": 0.7631578947368421,
      "evaluation_scope": "validation",
      "mean_interval_width_p10_p90": 12.166795725382341,
      "pinball_loss_p10": 1.126716241646318,
      "pinball_loss_p50": 2.236074547319634,
      "pinball_loss_p90": 0.5320123000772731,
      "position": "RB",
      "prediction_season": 2020,
      "projection_tier": "top",
      "rows": 76,
      "target_name": "games_active"
    },
    {
      "candidate_name": "ridge",
      "empirical_coverage_p10_p90": 0.7333333333333333,
      "evaluation_scope": "validation",
      "mean_interval_width_p10_p90": 8.545344631535814,
      "pinball_loss_p10": 0.46467852899640166,
      "pinball_loss_p50": 1.6602673335018294,
      "pinball_loss_p90": 1.0049839109207281,
      "position": "RB",
      "prediction_season": 2020,
      "projection_tier": "middle",
      "rows": 150,
      "target_name": "games_active"
    },
    {
      "candidate_name": "ridge",
      "empirical_coverage_p10_p90": 0.9866666666666667,
      "evaluation_scope": "validation",
      "mean_interval_width_p10_p90": 5.610090444727271,
      "pinball_loss_p10": 0.02666666666666667,
      "pinball_loss_p50": 0.13333333333333333,
      "pinball_loss_p90": 0.6624660956927076,
      "position": "RB",
      "prediction_season": 2020,
      "projection_tier": "lower",
      "rows": 75,
      "target_name": "games_active"
    },
    {
      "candidate_name": "ridge",
      "empirical_coverage_p10_p90": 0.8239202657807309,
      "evaluation_scope": "validation",
      "mean_interval_width_p10_p90": 9.627300443926496,
      "pinball_loss_p10": 0.6062356703075975,
      "pinball_loss_p50": 1.6169745358259227,
      "pinball_loss_p90": 0.8211770659785631,
      "position": "RB",
      "prediction_season": 2021,
      "projection_tier": "all",
      "rows": 301,
      "target_name": "games_active"
    },
    {
      "candidate_name": "ridge",
      "empirical_coverage_p10_p90": 0.8289473684210527,
      "evaluation_scope": "validation",
      "mean_interval_width_p10_p90": 11.589303566570138,
      "pinball_loss_p10": 1.2598774271321542,
      "pinball_loss_p50": 2.1785102908531493,
      "pinball_loss_p90": 0.5816599408603341,
      "position": "RB",
      "prediction_season": 2021,
      "projection_tier": "top",
      "rows": 76,
      "target_name": "games_active"
    },
    {
      "candidate_name": "ridge",
      "empirical_coverage_p10_p90": 0.7449664429530202,
      "evaluation_scope": "validation",
      "mean_interval_width_p10_p90": 10.433381779249924,
      "pinball_loss_p10": 0.559236592621095,
      "pinball_loss_p50": 1.9716089567493884,
      "pinball_loss_p90": 0.9381359090349658,
      "position": "RB",
      "prediction_season": 2021,
      "projection_tier": "middle",
      "rows": 149,
      "target_name": "games_active"
    },
    {
      "candidate_name": "ridge",
      "empirical_coverage_p10_p90": 0.9736842105263158,
      "evaluation_scope": "validation",
      "mean_interval_width_p10_p90": 6.084953650714559,
      "pinball_loss_p10": 0.044736842105263165,
      "pinball_loss_p50": 0.3601686660934805,
      "pinball_loss_p90": 0.8313933014204237,
      "position": "RB",
      "prediction_season": 2021,
      "projection_tier": "lower",
      "rows": 76,
      "target_name": "games_active"
    },
    {
      "candidate_name": "ridge",
      "empirical_coverage_p10_p90": 0.793918918918919,
      "evaluation_scope": "validation",
      "mean_interval_width_p10_p90": 9.602168722732792,
      "pinball_loss_p10": 0.5818501230967886,
      "pinball_loss_p50": 1.683379024153075,
      "pinball_loss_p90": 0.8046162030209498,
      "position": "RB",
      "prediction_season": 2022,
      "projection_tier": "all",
      "rows": 296,
      "target_name": "games_active"
    },
    {
      "candidate_name": "ridge",
      "empirical_coverage_p10_p90": 0.8243243243243243,
      "evaluation_scope": "validation",
      "mean_interval_width_p10_p90": 11.334345442822173,
      "pinball_loss_p10": 0.9937244298685028,
      "pinball_loss_p50": 1.9347084615021017,
      "pinball_loss_p90": 0.4526432206202154,
      "position": "RB",
      "prediction_season": 2022,
      "projection_tier": "top",
      "rows": 74,
      "target_name": "games_active"
    },
    {
      "candidate_name": "ridge",
      "empirical_coverage_p10_p90": 0.6756756756756757,
      "evaluation_scope": "validation",
      "mean_interval_width_p10_p90": 10.494942539247718,
      "pinball_loss_p10": 0.6654866799079744,
      "pinball_loss_p50": 2.2977501743068167,
      "pinball_loss_p90": 1.0800399286024656,
      "position": "RB",
      "prediction_season": 2022,
      "projection_tier": "middle",
      "rows": 148,
      "target_name": "games_active"
    },
    {
      "candidate_name": "ridge",
      "empirical_coverage_p10_p90": 1.0,
      "evaluation_scope": "validation",
      "mean_interval_width_p10_p90": 6.084444369613558,
      "pinball_loss_p10": 0.002702702702702703,
      "pinball_loss_p50": 0.2033072864965651,
      "pinball_loss_p90": 0.6057417342586529,
      "position": "RB",
      "prediction_season": 2022,
      "projection_tier": "lower",
      "rows": 74,
      "target_name": "games_active"
    },
    {
      "candidate_name": "ridge",
      "empirical_coverage_p10_p90": 0.8006872852233677,
      "evaluation_scope": "validation",
      "mean_interval_width_p10_p90": 9.167862714525231,
      "pinball_loss_p10": 0.6154725854507308,
      "pinball_loss_p50": 1.6222460101066905,
      "pinball_loss_p90": 0.8181832269499506,
      "position": "RB",
      "prediction_season": 2023,
      "projection_tier": "all",
      "rows": 291,
      "target_name": "games_active"
    },
    {
      "candidate_name": "ridge",
      "empirical_coverage_p10_p90": 0.7397260273972602,
      "evaluation_scope": "validation",
      "mean_interval_width_p10_p90": 11.466617606796884,
      "pinball_loss_p10": 1.3726336542235558,
      "pinball_loss_p50": 2.3868681303564783,
      "pinball_loss_p90": 0.5412330686145272,
      "position": "RB",
      "prediction_season": 2023,
      "projection_tier": "top",
      "rows": 73,
      "target_name": "games_active"
    },
    {
      "candidate_name": "ridge",
      "empirical_coverage_p10_p90": 0.7310344827586207,
      "evaluation_scope": "validation",
      "mean_interval_width_p10_p90": 9.819754463774876,
      "pinball_loss_p10": 0.5420707972954695,
      "pinball_loss_p50": 2.017374671479849,
      "pinball_loss_p90": 1.0909603330706472,
      "position": "RB",
      "prediction_season": 2023,
      "projection_tier": "middle",
      "rows": 145,
      "target_name": "games_active"
    },
    {
      "candidate_name": "ridge",
      "empirical_coverage_p10_p90": 1.0,
      "evaluation_scope": "validation",
      "mean_interval_width_p10_p90": 5.574254347716615,
      "pinball_loss_p10": 0.004109589041095891,
      "pinball_loss_p50": 0.07277928849925959,
      "pinball_loss_p90": 0.5533158457305656,
      "position": "RB",
      "prediction_season": 2023,
      "projection_tier": "lower",
      "rows": 73,
      "target_name": "games_active"
    },
    {
      "candidate_name": "ridge",
      "empirical_coverage_p10_p90": 0.8095238095238095,
      "evaluation_scope": "validation",
      "mean_interval_width_p10_p90": 8.537221121850472,
      "pinball_loss_p10": 0.5348681065084631,
      "pinball_loss_p50": 1.4650354900165776,
      "pinball_loss_p90": 0.8785543705202603,
      "position": "RB",
      "prediction_season": 2024,
      "projection_tier": "all",
      "rows": 294,
      "target_name": "games_active"
    },
    {
      "candidate_name": "ridge",
      "empirical_coverage_p10_p90": 0.8108108108108109,
      "evaluation_scope": "validation",
      "mean_interval_width_p10_p90": 11.265061767659533,
      "pinball_loss_p10": 1.1239406686228597,
      "pinball_loss_p50": 2.107128764746579,
      "pinball_loss_p90": 0.40605707362261995,
      "position": "RB",
      "prediction_season": 2024,
      "projection_tier": "top",
      "rows": 74,
      "target_name": "games_active"
    },
    {
      "candidate_name": "ridge",
      "empirical_coverage_p10_p90": 0.7191780821917808,
      "evaluation_scope": "validation",
      "mean_interval_width_p10_p90": 8.882098729800981,
      "pinball_loss_p10": 0.5005453002424421,
      "pinball_loss_p50": 1.8478966128330612,
      "pinball_loss_p90": 1.3031349905453824,
      "position": "RB",
      "prediction_season": 2024,
      "projection_tier": "middle",
      "rows": 146,
      "target_name": "games_active"
    },
    {
      "candidate_name": "ridge",
      "empirical_coverage_p10_p90": 0.9864864864864865,
      "evaluation_scope": "validation",
      "mean_interval_width_p10_p90": 5.128946276571484,
      "pinball_loss_p10": 0.013513513513513514,
      "pinball_loss_p50": 0.06756756756756757,
      "pinball_loss_p90": 0.513365579260228,
      "position": "RB",
      "prediction_season": 2024,
      "projection_tier": "lower",
      "rows": 74,
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
  "feature_responses": [],
  "importance": [
    {
      "absolute_importance": 1.9072119294778602,
      "coefficient": 1.9072119294778602,
      "direction": "positive",
      "feature": "numeric__lag1_games_active",
      "rank": 1
    },
    {
      "absolute_importance": 1.7785884920632717,
      "coefficient": 1.7785884920632717,
      "direction": "positive",
      "feature": "categorical__previous_team_NE",
      "rank": 2
    },
    {
      "absolute_importance": 1.7394813708505044,
      "coefficient": 1.7394813708505044,
      "direction": "positive",
      "feature": "categorical__previous_team_MIN",
      "rank": 3
    },
    {
      "absolute_importance": 1.7227153171323601,
      "coefficient": -1.7227153171323601,
      "direction": "negative",
      "feature": "categorical__previous_team_NYJ",
      "rank": 4
    },
    {
      "absolute_importance": 1.2920831882806634,
      "coefficient": -1.2920831882806634,
      "direction": "negative",
      "feature": "categorical__previous_team_NYG",
      "rank": 5
    },
    {
      "absolute_importance": 1.274864668602354,
      "coefficient": -1.274864668602354,
      "direction": "negative",
      "feature": "categorical__previous_team_SD",
      "rank": 6
    },
    {
      "absolute_importance": 1.266533682543533,
      "coefficient": 1.266533682543533,
      "direction": "positive",
      "feature": "numeric__weighted_3yr_rushing_yards_per_game",
      "rank": 7
    },
    {
      "absolute_importance": 1.1454212213498651,
      "coefficient": 1.1454212213498651,
      "direction": "positive",
      "feature": "numeric__lag1_fantasy_points_per_game",
      "rank": 8
    },
    {
      "absolute_importance": 1.0503673414107653,
      "coefficient": -1.0503673414107653,
      "direction": "negative",
      "feature": "numeric__weighted_3yr_carries_per_game",
      "rank": 9
    },
    {
      "absolute_importance": 0.9662951074281093,
      "coefficient": 0.9662951074281093,
      "direction": "positive",
      "feature": "categorical__previous_team_PHI",
      "rank": 10
    },
    {
      "absolute_importance": 0.9612357545030162,
      "coefficient": 0.9612357545030162,
      "direction": "positive",
      "feature": "categorical__previous_team_STL",
      "rank": 11
    },
    {
      "absolute_importance": 0.9485228284757801,
      "coefficient": -0.9485228284757801,
      "direction": "negative",
      "feature": "numeric__lag1_fantasy_points_total",
      "rank": 12
    },
    {
      "absolute_importance": 0.6865546337101507,
      "coefficient": 0.6865546337101507,
      "direction": "positive",
      "feature": "categorical__previous_team_SF",
      "rank": 13
    },
    {
      "absolute_importance": 0.6690638841661807,
      "coefficient": -0.6690638841661807,
      "direction": "negative",
      "feature": "numeric__missing_lag1",
      "rank": 14
    },
    {
      "absolute_importance": 0.6690638841661807,
      "coefficient": -0.6690638841661807,
      "direction": "negative",
      "feature": "numeric__missingindicator_lag1_fantasy_points_per_game",
      "rank": 15
    },
    {
      "absolute_importance": 0.6690638841661807,
      "coefficient": -0.6690638841661807,
      "direction": "negative",
      "feature": "numeric__missingindicator_lag1_fantasy_points_total",
      "rank": 16
    },
    {
      "absolute_importance": 0.6690638841661807,
      "coefficient": -0.6690638841661807,
      "direction": "negative",
      "feature": "numeric__missingindicator_lag1_games_active",
      "rank": 17
    },
    {
      "absolute_importance": 0.6690638841661807,
      "coefficient": -0.6690638841661807,
      "direction": "negative",
      "feature": "numeric__missingindicator_lag1_stat_games",
      "rank": 18
    },
    {
      "absolute_importance": 0.6658511734379995,
      "coefficient": -0.6658511734379995,
      "direction": "negative",
      "feature": "categorical__previous_team_WAS",
      "rank": 19
    },
    {
      "absolute_importance": 0.6432020311516933,
      "coefficient": 0.6432020311516933,
      "direction": "positive",
      "feature": "categorical__previous_team_CIN",
      "rank": 20
    }
  ],
  "method": "standardized coefficients"
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

- Project-relative path: `models/artifacts/phase4-052d2866899a665a44f3/attempt-331cdaf7eb7f4721aa43c08d469288ee/RB/games_active/ridge.joblib`
- SHA-256: `c1f982e2386558f6e7624b9ed3797377b2cc972a6b9582ef5ddc6ace65492233`

## Additional metadata

````json
{
  "publication_id": "attempt-331cdaf7eb7f4721aa43c08d469288ee"
}
````
