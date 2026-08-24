# Model Card: phase4-052d2866899a665a44f3-wr-games-ridge

- Model ID: `phase4-052d2866899a665a44f3-wr-games-ridge`
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
  "draft_relevant_validation_mae": 3.098208196136572,
  "draft_relevant_validation_rows": 180,
  "draft_relevant_validation_signed_bias": -0.2257280785710975,
  "position": "WR",
  "target_name": "games_active",
  "test_mae": 2.9483636394202253,
  "test_rows": 433,
  "test_season": 2025,
  "validation_mae": 3.128045277136161,
  "validation_rows": 2101,
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
    "candidate_mae": 3.098208196136572,
    "ci95_lower": 0.19691558722738153,
    "ci95_upper": 0.8257878990843412,
    "direction": "reference_lower_mae",
    "mae_difference_candidate_minus_reference": 0.5197029051312807,
    "n_resamples": 2000,
    "reference_mae": 2.5785052910052912,
    "rows": 180,
    "seed": 42
  },
  "decision_status": "learned_draft_relevant_regression_baseline_retained",
  "learned_improvement_status": "regression",
  "reference_metrics": {
    "candidate_name": "age_position_adjusted",
    "candidate_source": "baseline",
    "draft_relevant_validation_mae": 2.5785052910052912,
    "draft_relevant_validation_rows": 180,
    "draft_relevant_validation_signed_bias": 1.1674206349206362,
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
    ],
    "validation_top_n_capture_rate": null
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
      "candidate_name": "ridge",
      "empirical_coverage_p10_p90": 0.8083140877598153,
      "evaluation_scope": "test",
      "mean_interval_width_p10_p90": 8.364818727398994,
      "pinball_loss_p10": 0.5686192210100943,
      "pinball_loss_p50": 1.4741818197101126,
      "pinball_loss_p90": 0.8261486598454972,
      "position": "WR",
      "prediction_season": 2025,
      "projection_tier": "all",
      "rows": 433,
      "target_name": "games_active"
    },
    {
      "candidate_name": "ridge",
      "empirical_coverage_p10_p90": 0.8165137614678899,
      "evaluation_scope": "test",
      "mean_interval_width_p10_p90": 10.259260394383418,
      "pinball_loss_p10": 1.1265403608227536,
      "pinball_loss_p50": 1.9942160606104855,
      "pinball_loss_p90": 0.5216615493439882,
      "position": "WR",
      "prediction_season": 2025,
      "projection_tier": "top",
      "rows": 109,
      "target_name": "games_active"
    },
    {
      "candidate_name": "ridge",
      "empirical_coverage_p10_p90": 0.7162790697674418,
      "evaluation_scope": "test",
      "mean_interval_width_p10_p90": 8.984666868793497,
      "pinball_loss_p10": 0.5512522017101891,
      "pinball_loss_p50": 1.8434678540643687,
      "pinball_loss_p90": 1.0495863909217635,
      "position": "WR",
      "prediction_season": 2025,
      "projection_tier": "middle",
      "rows": 215,
      "target_name": "games_active"
    },
    {
      "candidate_name": "ridge",
      "empirical_coverage_p10_p90": 0.981651376146789,
      "evaluation_scope": "test",
      "mean_interval_width_p10_p90": 5.247740818214413,
      "pinball_loss_p10": 0.044954128440366975,
      "pinball_loss_p50": 0.22573934590914252,
      "pinball_loss_p90": 0.6899099705176744,
      "position": "WR",
      "prediction_season": 2025,
      "projection_tier": "lower",
      "rows": 109,
      "target_name": "games_active"
    },
    {
      "candidate_name": "ridge",
      "empirical_coverage_p10_p90": 0.8203883495145631,
      "evaluation_scope": "validation",
      "mean_interval_width_p10_p90": 9.564495856258947,
      "pinball_loss_p10": 0.6081892564156753,
      "pinball_loss_p50": 1.6453759510474273,
      "pinball_loss_p90": 0.8538209316713428,
      "position": "WR",
      "prediction_season": 2020,
      "projection_tier": "all",
      "rows": 412,
      "target_name": "games_active"
    },
    {
      "candidate_name": "ridge",
      "empirical_coverage_p10_p90": 0.8173076923076923,
      "evaluation_scope": "validation",
      "mean_interval_width_p10_p90": 10.818459062831067,
      "pinball_loss_p10": 1.2889818267891,
      "pinball_loss_p50": 1.9247080961869947,
      "pinball_loss_p90": 0.5468514662687372,
      "position": "WR",
      "prediction_season": 2020,
      "projection_tier": "top",
      "rows": 104,
      "target_name": "games_active"
    },
    {
      "candidate_name": "ridge",
      "empirical_coverage_p10_p90": 0.7317073170731707,
      "evaluation_scope": "validation",
      "mean_interval_width_p10_p90": 10.414910102310799,
      "pinball_loss_p10": 0.5639993349131309,
      "pinball_loss_p50": 2.164729896781061,
      "pinball_loss_p90": 1.1110345045345875,
      "position": "WR",
      "prediction_season": 2020,
      "projection_tier": "middle",
      "rows": 205,
      "target_name": "games_active"
    },
    {
      "candidate_name": "ridge",
      "empirical_coverage_p10_p90": 1.0,
      "evaluation_scope": "validation",
      "mean_interval_width_p10_p90": 6.605786206510108,
      "pinball_loss_p10": 0.008737864077669903,
      "pinball_loss_p50": 0.3296662231842242,
      "pinball_loss_p90": 0.6518407565733411,
      "position": "WR",
      "prediction_season": 2020,
      "projection_tier": "lower",
      "rows": 103,
      "target_name": "games_active"
    },
    {
      "candidate_name": "ridge",
      "empirical_coverage_p10_p90": 0.8157894736842105,
      "evaluation_scope": "validation",
      "mean_interval_width_p10_p90": 9.22265132512588,
      "pinball_loss_p10": 0.5704612806267103,
      "pinball_loss_p50": 1.6229935245888119,
      "pinball_loss_p90": 0.9086508445056141,
      "position": "WR",
      "prediction_season": 2021,
      "projection_tier": "all",
      "rows": 418,
      "target_name": "games_active"
    },
    {
      "candidate_name": "ridge",
      "empirical_coverage_p10_p90": 0.8,
      "evaluation_scope": "validation",
      "mean_interval_width_p10_p90": 10.988250791324747,
      "pinball_loss_p10": 1.1051765463118277,
      "pinball_loss_p50": 2.1623409897892065,
      "pinball_loss_p90": 0.5162626752071829,
      "position": "WR",
      "prediction_season": 2021,
      "projection_tier": "top",
      "rows": 105,
      "target_name": "games_active"
    },
    {
      "candidate_name": "ridge",
      "empirical_coverage_p10_p90": 0.7403846153846154,
      "evaluation_scope": "validation",
      "mean_interval_width_p10_p90": 9.886705502713435,
      "pinball_loss_p10": 0.5702369131693416,
      "pinball_loss_p50": 2.0289952792816175,
      "pinball_loss_p90": 1.178122069324954,
      "position": "WR",
      "prediction_season": 2021,
      "projection_tier": "middle",
      "rows": 208,
      "target_name": "games_active"
    },
    {
      "candidate_name": "ridge",
      "empirical_coverage_p10_p90": 0.9809523809523809,
      "evaluation_scope": "validation",
      "mean_interval_width_p10_p90": 6.141592154753582,
      "pinball_loss_p10": 0.03619047619047619,
      "pinball_loss_p50": 0.2793759167588599,
      "pinball_loss_p90": 0.7672293494000195,
      "position": "WR",
      "prediction_season": 2021,
      "projection_tier": "lower",
      "rows": 105,
      "target_name": "games_active"
    },
    {
      "candidate_name": "ridge",
      "empirical_coverage_p10_p90": 0.7930232558139535,
      "evaluation_scope": "validation",
      "mean_interval_width_p10_p90": 9.171748344080259,
      "pinball_loss_p10": 0.5746170842149972,
      "pinball_loss_p50": 1.5742418128805742,
      "pinball_loss_p90": 0.8389200205546832,
      "position": "WR",
      "prediction_season": 2022,
      "projection_tier": "all",
      "rows": 430,
      "target_name": "games_active"
    },
    {
      "candidate_name": "ridge",
      "empirical_coverage_p10_p90": 0.7685185185185185,
      "evaluation_scope": "validation",
      "mean_interval_width_p10_p90": 10.490952133427404,
      "pinball_loss_p10": 1.1642361563697452,
      "pinball_loss_p50": 2.0430857259582846,
      "pinball_loss_p90": 0.5219196040431905,
      "position": "WR",
      "prediction_season": 2022,
      "projection_tier": "top",
      "rows": 108,
      "target_name": "games_active"
    },
    {
      "candidate_name": "ridge",
      "empirical_coverage_p10_p90": 0.7023255813953488,
      "evaluation_scope": "validation",
      "mean_interval_width_p10_p90": 10.015160580027231,
      "pinball_loss_p10": 0.5611527503465876,
      "pinball_loss_p50": 2.05729309457562,
      "pinball_loss_p90": 1.11307603868837,
      "position": "WR",
      "prediction_season": 2022,
      "projection_tier": "middle",
      "rows": 215,
      "target_name": "games_active"
    },
    {
      "candidate_name": "ridge",
      "empirical_coverage_p10_p90": 1.0,
      "evaluation_scope": "validation",
      "mean_interval_width_p10_p90": 6.145508718116795,
      "pinball_loss_p10": 0.0065420560747663555,
      "pinball_loss_p50": 0.13039911963919645,
      "pinball_loss_p90": 0.6080088157369129,
      "position": "WR",
      "prediction_season": 2022,
      "projection_tier": "lower",
      "rows": 107,
      "target_name": "games_active"
    },
    {
      "candidate_name": "ridge",
      "empirical_coverage_p10_p90": 0.8273381294964028,
      "evaluation_scope": "validation",
      "mean_interval_width_p10_p90": 9.189594963314432,
      "pinball_loss_p10": 0.5575270984797269,
      "pinball_loss_p50": 1.5398824657608143,
      "pinball_loss_p90": 0.809147908786912,
      "position": "WR",
      "prediction_season": 2023,
      "projection_tier": "all",
      "rows": 417,
      "target_name": "games_active"
    },
    {
      "candidate_name": "ridge",
      "empirical_coverage_p10_p90": 0.8857142857142857,
      "evaluation_scope": "validation",
      "mean_interval_width_p10_p90": 10.64096268210046,
      "pinball_loss_p10": 0.9415528410397749,
      "pinball_loss_p50": 1.8539441127328218,
      "pinball_loss_p90": 0.3903420815955832,
      "position": "WR",
      "prediction_season": 2023,
      "projection_tier": "top",
      "rows": 105,
      "target_name": "games_active"
    },
    {
      "candidate_name": "ridge",
      "empirical_coverage_p10_p90": 0.7259615384615384,
      "evaluation_scope": "validation",
      "mean_interval_width_p10_p90": 9.96291287482269,
      "pinball_loss_p10": 0.6280084219080275,
      "pinball_loss_p50": 2.0516692176135995,
      "pinball_loss_p90": 1.1279226784381022,
      "position": "WR",
      "prediction_season": 2023,
      "projection_tier": "middle",
      "rows": 208,
      "target_name": "games_active"
    },
    {
      "candidate_name": "ridge",
      "empirical_coverage_p10_p90": 0.9711538461538461,
      "evaluation_scope": "validation",
      "mean_interval_width_p10_p90": 6.1776359626774076,
      "pinball_loss_p10": 0.028846153846153848,
      "pinball_loss_p50": 0.19922749155465994,
      "pinball_loss_p90": 0.5944311757834694,
      "position": "WR",
      "prediction_season": 2023,
      "projection_tier": "lower",
      "rows": 104,
      "target_name": "games_active"
    },
    {
      "candidate_name": "ridge",
      "empirical_coverage_p10_p90": 0.8207547169811321,
      "evaluation_scope": "validation",
      "mean_interval_width_p10_p90": 8.858155029356135,
      "pinball_loss_p10": 0.544965113927247,
      "pinball_loss_p50": 1.440213232926808,
      "pinball_loss_p90": 0.7734711166294128,
      "position": "WR",
      "prediction_season": 2024,
      "projection_tier": "all",
      "rows": 424,
      "target_name": "games_active"
    },
    {
      "candidate_name": "ridge",
      "empirical_coverage_p10_p90": 0.8679245283018868,
      "evaluation_scope": "validation",
      "mean_interval_width_p10_p90": 9.979609269438189,
      "pinball_loss_p10": 1.0370845136617517,
      "pinball_loss_p50": 1.863439284875982,
      "pinball_loss_p90": 0.4606673497280376,
      "position": "WR",
      "prediction_season": 2024,
      "projection_tier": "top",
      "rows": 106,
      "target_name": "games_active"
    },
    {
      "candidate_name": "ridge",
      "empirical_coverage_p10_p90": 0.7122641509433962,
      "evaluation_scope": "validation",
      "mean_interval_width_p10_p90": 9.651495937436245,
      "pinball_loss_p10": 0.5657275936651276,
      "pinball_loss_p50": 1.89172013644274,
      "pinball_loss_p90": 1.0147138278724952,
      "position": "WR",
      "prediction_season": 2024,
      "projection_tier": "middle",
      "rows": 212,
      "target_name": "games_active"
    },
    {
      "candidate_name": "ridge",
      "empirical_coverage_p10_p90": 0.9905660377358491,
      "evaluation_scope": "validation",
      "mean_interval_width_p10_p90": 6.150018973113869,
      "pinball_loss_p10": 0.011320754716981133,
      "pinball_loss_p50": 0.11397337394577024,
      "pinball_loss_p90": 0.6037894610446229,
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
      "absolute_importance": 1.7750887076907307,
      "coefficient": 1.7750887076907307,
      "direction": "positive",
      "feature": "numeric__lag1_fantasy_points_per_game",
      "rank": 1
    },
    {
      "absolute_importance": 1.7676313100882661,
      "coefficient": -1.7676313100882661,
      "direction": "negative",
      "feature": "categorical__previous_team_NYG",
      "rank": 2
    },
    {
      "absolute_importance": 1.5352397040360601,
      "coefficient": 1.5352397040360601,
      "direction": "positive",
      "feature": "categorical__previous_team_LA",
      "rank": 3
    },
    {
      "absolute_importance": 1.1688966946207762,
      "coefficient": 1.1688966946207762,
      "direction": "positive",
      "feature": "categorical__previous_team_CIN",
      "rank": 4
    },
    {
      "absolute_importance": 1.1558448017619307,
      "coefficient": 1.1558448017619307,
      "direction": "positive",
      "feature": "categorical__previous_team_NE",
      "rank": 5
    },
    {
      "absolute_importance": 1.1351682566086225,
      "coefficient": 1.1351682566086225,
      "direction": "positive",
      "feature": "categorical__previous_team_GB",
      "rank": 6
    },
    {
      "absolute_importance": 1.1266269082256297,
      "coefficient": 1.1266269082256297,
      "direction": "positive",
      "feature": "numeric__weighted_3yr_interceptions_per_game",
      "rank": 7
    },
    {
      "absolute_importance": 1.0793633204961515,
      "coefficient": -1.0793633204961515,
      "direction": "negative",
      "feature": "categorical__previous_team_NYJ",
      "rank": 8
    },
    {
      "absolute_importance": 1.0680904841753063,
      "coefficient": 1.0680904841753063,
      "direction": "positive",
      "feature": "categorical__previous_team_DAL",
      "rank": 9
    },
    {
      "absolute_importance": 1.0573809137118642,
      "coefficient": 1.0573809137118642,
      "direction": "positive",
      "feature": "categorical__previous_team_ATL",
      "rank": 10
    },
    {
      "absolute_importance": 1.0069531197808632,
      "coefficient": 1.0069531197808632,
      "direction": "positive",
      "feature": "categorical__previous_team_ARI",
      "rank": 11
    },
    {
      "absolute_importance": 0.9930916459858756,
      "coefficient": -0.9930916459858756,
      "direction": "negative",
      "feature": "numeric__lag1_fantasy_points_total",
      "rank": 12
    },
    {
      "absolute_importance": 0.9860761442875714,
      "coefficient": -0.9860761442875714,
      "direction": "negative",
      "feature": "numeric__weighted_3yr_passing_attempts_per_game",
      "rank": 13
    },
    {
      "absolute_importance": 0.9397271778419489,
      "coefficient": 0.9397271778419489,
      "direction": "positive",
      "feature": "numeric__lag1_stat_games",
      "rank": 14
    },
    {
      "absolute_importance": 0.9195773203114891,
      "coefficient": -0.9195773203114891,
      "direction": "negative",
      "feature": "categorical__previous_team_SD",
      "rank": 15
    },
    {
      "absolute_importance": 0.9052316186263477,
      "coefficient": -0.9052316186263477,
      "direction": "negative",
      "feature": "categorical__previous_team_SF",
      "rank": 16
    },
    {
      "absolute_importance": 0.8739562550717583,
      "coefficient": -0.8739562550717583,
      "direction": "negative",
      "feature": "categorical__previous_team_HOU",
      "rank": 17
    },
    {
      "absolute_importance": 0.868826138011178,
      "coefficient": -0.868826138011178,
      "direction": "negative",
      "feature": "categorical__previous_team_PHI",
      "rank": 18
    },
    {
      "absolute_importance": 0.8442884153991635,
      "coefficient": -0.8442884153991635,
      "direction": "negative",
      "feature": "numeric__age_at_cutoff",
      "rank": 19
    },
    {
      "absolute_importance": 0.8304933181382607,
      "coefficient": 0.8304933181382607,
      "direction": "positive",
      "feature": "numeric__lag1_games_active",
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

- Project-relative path: `models/artifacts/phase4-052d2866899a665a44f3/attempt-331cdaf7eb7f4721aa43c08d469288ee/WR/games_active/ridge.joblib`
- SHA-256: `5a3af842ecfe7fc48a7bcdd134f151ad1a103c099ac0cee454db71897d28c943`

## Additional metadata

````json
{
  "publication_id": "attempt-331cdaf7eb7f4721aa43c08d469288ee"
}
````
