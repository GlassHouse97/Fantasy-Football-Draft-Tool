# Model Card: phase4-052d2866899a665a44f3-wr-ppg-ridge

- Model ID: `phase4-052d2866899a665a44f3-wr-ppg-ridge`
- Trained at: 2026-08-24T20:21:18+00:00
- Target: `fantasy_points_per_game`
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
  "draft_relevant_validation_mae": 2.7248510644935893,
  "draft_relevant_validation_rows": 180,
  "draft_relevant_validation_signed_bias": -0.6763419994008577,
  "position": "WR",
  "target_name": "fantasy_points_per_game",
  "test_mae": 2.126908266125579,
  "test_rows": 198,
  "test_season": 2025,
  "validation_mae": 2.5776107025708757,
  "validation_rows": 989,
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
    "candidate_mae": 2.669270110634892,
    "ci95_lower": -0.18877376687210246,
    "ci95_upper": 0.25300939694794305,
    "direction": "uncertain",
    "mae_difference_candidate_minus_reference": 0.03327545983173241,
    "n_resamples": 2000,
    "reference_mae": 2.6359946508031595,
    "rows": 180,
    "seed": 42
  },
  "decision_status": "learned_draft_relevant_regression_baseline_retained",
  "learned_improvement_status": "regression",
  "reference_metrics": {
    "candidate_name": "age_position_adjusted",
    "candidate_source": "baseline",
    "draft_relevant_validation_mae": 2.6359946508031595,
    "draft_relevant_validation_rows": 180,
    "draft_relevant_validation_signed_bias": 0.5666536341219881,
    "position": "WR",
    "target_name": "fantasy_points_per_game",
    "test_mae": 2.3039447474264443,
    "test_rows": 198,
    "test_season": 2025,
    "validation_mae": 2.544393075816068,
    "validation_rows": 989,
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
      "empirical_coverage_p10_p90": 0.8939393939393939,
      "evaluation_scope": "test",
      "mean_interval_width_p10_p90": 7.7950825929057865,
      "pinball_loss_p10": 0.4505540203185689,
      "pinball_loss_p50": 1.0634541330627896,
      "pinball_loss_p90": 0.5077747951714765,
      "position": "WR",
      "prediction_season": 2025,
      "projection_tier": "all",
      "rows": 198,
      "target_name": "fantasy_points_per_game"
    },
    {
      "candidate_name": "ridge",
      "empirical_coverage_p10_p90": 0.8367346938775511,
      "evaluation_scope": "test",
      "mean_interval_width_p10_p90": 7.7950825929057865,
      "pinball_loss_p10": 0.4485082461827365,
      "pinball_loss_p50": 1.2775760714740356,
      "pinball_loss_p90": 0.6478600126637516,
      "position": "WR",
      "prediction_season": 2025,
      "projection_tier": "top",
      "rows": 98,
      "target_name": "fantasy_points_per_game"
    },
    {
      "candidate_name": "ridge",
      "empirical_coverage_p10_p90": 0.9367088607594937,
      "evaluation_scope": "test",
      "mean_interval_width_p10_p90": 7.795082592905788,
      "pinball_loss_p10": 0.4317848624809191,
      "pinball_loss_p50": 0.8222450502506352,
      "pinball_loss_p90": 0.4028397280883343,
      "position": "WR",
      "prediction_season": 2025,
      "projection_tier": "middle",
      "rows": 79,
      "target_name": "fantasy_points_per_game"
    },
    {
      "candidate_name": "ridge",
      "empirical_coverage_p10_p90": 1.0,
      "evaluation_scope": "test",
      "mean_interval_width_p10_p90": 7.795082592905781,
      "pinball_loss_p10": 0.5307087505321846,
      "pinball_loss_p50": 0.9716240177226997,
      "pinball_loss_p90": 0.24879950875839368,
      "position": "WR",
      "prediction_season": 2025,
      "projection_tier": "lower",
      "rows": 21,
      "target_name": "fantasy_points_per_game"
    },
    {
      "candidate_name": "ridge",
      "empirical_coverage_p10_p90": 0.9010416666666666,
      "evaluation_scope": "validation",
      "mean_interval_width_p10_p90": 11.190311240083373,
      "pinball_loss_p10": 0.53009927202885,
      "pinball_loss_p50": 1.3642090582139759,
      "pinball_loss_p90": 0.7297482038870798,
      "position": "WR",
      "prediction_season": 2020,
      "projection_tier": "all",
      "rows": 192,
      "target_name": "fantasy_points_per_game"
    },
    {
      "candidate_name": "ridge",
      "empirical_coverage_p10_p90": 0.8636363636363636,
      "evaluation_scope": "validation",
      "mean_interval_width_p10_p90": 11.190311240083373,
      "pinball_loss_p10": 0.6746218347874269,
      "pinball_loss_p50": 1.5016714845375694,
      "pinball_loss_p90": 0.7063518339014027,
      "position": "WR",
      "prediction_season": 2020,
      "projection_tier": "top",
      "rows": 88,
      "target_name": "fantasy_points_per_game"
    },
    {
      "candidate_name": "ridge",
      "empirical_coverage_p10_p90": 0.9041095890410958,
      "evaluation_scope": "validation",
      "mean_interval_width_p10_p90": 11.190311240083373,
      "pinball_loss_p10": 0.3824081455154048,
      "pinball_loss_p50": 1.493343353546068,
      "pinball_loss_p90": 0.7912229186898425,
      "position": "WR",
      "prediction_season": 2020,
      "projection_tier": "middle",
      "rows": 73,
      "target_name": "fantasy_points_per_game"
    },
    {
      "candidate_name": "ridge",
      "empirical_coverage_p10_p90": 1.0,
      "evaluation_scope": "validation",
      "mean_interval_width_p10_p90": 11.190311240083368,
      "pinball_loss_p10": 0.4676304563103577,
      "pinball_loss_p50": 0.6699027009327204,
      "pinball_loss_p90": 0.6514006676979796,
      "position": "WR",
      "prediction_season": 2020,
      "projection_tier": "lower",
      "rows": 31,
      "target_name": "fantasy_points_per_game"
    },
    {
      "candidate_name": "ridge",
      "empirical_coverage_p10_p90": 0.839622641509434,
      "evaluation_scope": "validation",
      "mean_interval_width_p10_p90": 10.298314817838541,
      "pinball_loss_p10": 0.6053535214907905,
      "pinball_loss_p50": 1.4552935520029542,
      "pinball_loss_p90": 0.8953479079673653,
      "position": "WR",
      "prediction_season": 2021,
      "projection_tier": "all",
      "rows": 212,
      "target_name": "fantasy_points_per_game"
    },
    {
      "candidate_name": "ridge",
      "empirical_coverage_p10_p90": 0.7575757575757576,
      "evaluation_scope": "validation",
      "mean_interval_width_p10_p90": 10.298314817838545,
      "pinball_loss_p10": 0.8026150954295226,
      "pinball_loss_p50": 1.608281982718384,
      "pinball_loss_p90": 0.8784050241646512,
      "position": "WR",
      "prediction_season": 2021,
      "projection_tier": "top",
      "rows": 99,
      "target_name": "fantasy_points_per_game"
    },
    {
      "candidate_name": "ridge",
      "empirical_coverage_p10_p90": 0.9021739130434783,
      "evaluation_scope": "validation",
      "mean_interval_width_p10_p90": 10.298314817838545,
      "pinball_loss_p10": 0.38862806249081283,
      "pinball_loss_p50": 1.274990567248498,
      "pinball_loss_p90": 0.7164540956708116,
      "position": "WR",
      "prediction_season": 2021,
      "projection_tier": "middle",
      "rows": 92,
      "target_name": "fantasy_points_per_game"
    },
    {
      "candidate_name": "ridge",
      "empirical_coverage_p10_p90": 0.9523809523809523,
      "evaluation_scope": "validation",
      "mean_interval_width_p10_p90": 10.29831481783854,
      "pinball_loss_p10": 0.6248700171128602,
      "pinball_loss_p50": 1.5239611689830672,
      "pinball_loss_p90": 1.7589467759555373,
      "position": "WR",
      "prediction_season": 2021,
      "projection_tier": "lower",
      "rows": 21,
      "target_name": "fantasy_points_per_game"
    },
    {
      "candidate_name": "ridge",
      "empirical_coverage_p10_p90": 0.815,
      "evaluation_scope": "validation",
      "mean_interval_width_p10_p90": 8.312566471772762,
      "pinball_loss_p10": 0.502637416195506,
      "pinball_loss_p50": 1.2005472452991903,
      "pinball_loss_p90": 0.5789625925217854,
      "position": "WR",
      "prediction_season": 2022,
      "projection_tier": "all",
      "rows": 200,
      "target_name": "fantasy_points_per_game"
    },
    {
      "candidate_name": "ridge",
      "empirical_coverage_p10_p90": 0.75,
      "evaluation_scope": "validation",
      "mean_interval_width_p10_p90": 8.312566471772763,
      "pinball_loss_p10": 0.6048634134360877,
      "pinball_loss_p50": 1.3698383976829454,
      "pinball_loss_p90": 0.5692439744616734,
      "position": "WR",
      "prediction_season": 2022,
      "projection_tier": "top",
      "rows": 100,
      "target_name": "fantasy_points_per_game"
    },
    {
      "candidate_name": "ridge",
      "empirical_coverage_p10_p90": 0.8717948717948718,
      "evaluation_scope": "validation",
      "mean_interval_width_p10_p90": 8.312566471772765,
      "pinball_loss_p10": 0.37337591321342006,
      "pinball_loss_p50": 1.0890435125976632,
      "pinball_loss_p90": 0.5819220127351347,
      "position": "WR",
      "prediction_season": 2022,
      "projection_tier": "middle",
      "rows": 78,
      "target_name": "fantasy_points_per_game"
    },
    {
      "candidate_name": "ridge",
      "empirical_coverage_p10_p90": 0.9090909090909091,
      "evaluation_scope": "validation",
      "mean_interval_width_p10_p90": 8.31256647177276,
      "pinball_loss_p10": 0.49626457567480226,
      "pinball_loss_p50": 0.8263734231329884,
      "pinball_loss_p90": 0.6126456393113286,
      "position": "WR",
      "prediction_season": 2022,
      "projection_tier": "lower",
      "rows": 22,
      "target_name": "fantasy_points_per_game"
    },
    {
      "candidate_name": "ridge",
      "empirical_coverage_p10_p90": 0.837696335078534,
      "evaluation_scope": "validation",
      "mean_interval_width_p10_p90": 8.033784555246939,
      "pinball_loss_p10": 0.46505460889841155,
      "pinball_loss_p50": 1.0690871022876647,
      "pinball_loss_p90": 0.5836566327043656,
      "position": "WR",
      "prediction_season": 2023,
      "projection_tier": "all",
      "rows": 191,
      "target_name": "fantasy_points_per_game"
    },
    {
      "candidate_name": "ridge",
      "empirical_coverage_p10_p90": 0.7142857142857143,
      "evaluation_scope": "validation",
      "mean_interval_width_p10_p90": 8.033784555246939,
      "pinball_loss_p10": 0.5498693714499552,
      "pinball_loss_p50": 1.36907465722452,
      "pinball_loss_p90": 0.6740384306787487,
      "position": "WR",
      "prediction_season": 2023,
      "projection_tier": "top",
      "rows": 98,
      "target_name": "fantasy_points_per_game"
    },
    {
      "candidate_name": "ridge",
      "empirical_coverage_p10_p90": 0.9726027397260274,
      "evaluation_scope": "validation",
      "mean_interval_width_p10_p90": 8.033784555246939,
      "pinball_loss_p10": 0.3444282172487608,
      "pinball_loss_p50": 0.7595132884493477,
      "pinball_loss_p90": 0.5063354340793359,
      "position": "WR",
      "prediction_season": 2023,
      "projection_tier": "middle",
      "rows": 73,
      "target_name": "fantasy_points_per_game"
    },
    {
      "candidate_name": "ridge",
      "empirical_coverage_p10_p90": 0.95,
      "evaluation_scope": "validation",
      "mean_interval_width_p10_p90": 8.033784555246939,
      "pinball_loss_p10": 0.48974860191707253,
      "pinball_loss_p50": 0.7290925036069307,
      "pinball_loss_p90": 0.4230081976112471,
      "position": "WR",
      "prediction_season": 2023,
      "projection_tier": "lower",
      "rows": 20,
      "target_name": "fantasy_points_per_game"
    },
    {
      "candidate_name": "ridge",
      "empirical_coverage_p10_p90": 0.7680412371134021,
      "evaluation_scope": "validation",
      "mean_interval_width_p10_p90": 7.546281519936241,
      "pinball_loss_p10": 0.5378112686412759,
      "pinball_loss_p50": 1.3395517248598263,
      "pinball_loss_p90": 0.682645874067104,
      "position": "WR",
      "prediction_season": 2024,
      "projection_tier": "all",
      "rows": 194,
      "target_name": "fantasy_points_per_game"
    },
    {
      "candidate_name": "ridge",
      "empirical_coverage_p10_p90": 0.6847826086956522,
      "evaluation_scope": "validation",
      "mean_interval_width_p10_p90": 7.5462815199362385,
      "pinball_loss_p10": 0.5533900967743043,
      "pinball_loss_p50": 1.5854440249466375,
      "pinball_loss_p90": 0.7981450203673173,
      "position": "WR",
      "prediction_season": 2024,
      "projection_tier": "top",
      "rows": 92,
      "target_name": "fantasy_points_per_game"
    },
    {
      "candidate_name": "ridge",
      "empirical_coverage_p10_p90": 0.8255813953488372,
      "evaluation_scope": "validation",
      "mean_interval_width_p10_p90": 7.5462815199362385,
      "pinball_loss_p10": 0.5154027413070119,
      "pinball_loss_p50": 1.11432376015052,
      "pinball_loss_p90": 0.6413106663233948,
      "position": "WR",
      "prediction_season": 2024,
      "projection_tier": "middle",
      "rows": 86,
      "target_name": "fantasy_points_per_game"
    },
    {
      "candidate_name": "ridge",
      "empirical_coverage_p10_p90": 0.9375,
      "evaluation_scope": "validation",
      "mean_interval_width_p10_p90": 7.54628151993624,
      "pinball_loss_p10": 0.5686788412980317,
      "pinball_loss_p50": 1.1362713096731865,
      "pinball_loss_p90": 0.24070252446331594,
      "position": "WR",
      "prediction_season": 2024,
      "projection_tier": "lower",
      "rows": 16,
      "target_name": "fantasy_points_per_game"
    }
  ],
  "empirical_not_guaranteed": true,
  "method": "training-only signed out-of-fold residual quantiles",
  "operational_center": "training_only_residual_adjusted_p50",
  "residual_rows": 583,
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
      "absolute_importance": 1.6520286014120837,
      "coefficient": 1.6520286014120837,
      "direction": "positive",
      "feature": "numeric__lag1_fantasy_points_total",
      "rank": 1
    },
    {
      "absolute_importance": 1.4227417239955018,
      "coefficient": 1.4227417239955018,
      "direction": "positive",
      "feature": "numeric__weighted_3yr_receiving_yards_per_game",
      "rank": 2
    },
    {
      "absolute_importance": 1.159394061024008,
      "coefficient": -1.159394061024008,
      "direction": "negative",
      "feature": "categorical__previous_team_JAX",
      "rank": 3
    },
    {
      "absolute_importance": 1.0306566937202195,
      "coefficient": 1.0306566937202195,
      "direction": "positive",
      "feature": "numeric__weighted_3yr_fantasy_points_per_game",
      "rank": 4
    },
    {
      "absolute_importance": 1.0125583768716258,
      "coefficient": 1.0125583768716258,
      "direction": "positive",
      "feature": "numeric__weighted_3yr_receptions_per_game",
      "rank": 5
    },
    {
      "absolute_importance": 0.9975792564220343,
      "coefficient": 0.9975792564220343,
      "direction": "positive",
      "feature": "categorical__previous_team_DET",
      "rank": 6
    },
    {
      "absolute_importance": 0.9427361254182152,
      "coefficient": -0.9427361254182152,
      "direction": "negative",
      "feature": "categorical__previous_team_BAL",
      "rank": 7
    },
    {
      "absolute_importance": 0.7710683819013034,
      "coefficient": -0.7710683819013034,
      "direction": "negative",
      "feature": "categorical__previous_team_TEN",
      "rank": 8
    },
    {
      "absolute_importance": 0.7457605476374789,
      "coefficient": -0.7457605476374789,
      "direction": "negative",
      "feature": "categorical__previous_team_CAR",
      "rank": 9
    },
    {
      "absolute_importance": 0.7420962974047615,
      "coefficient": 0.7420962974047615,
      "direction": "positive",
      "feature": "categorical__previous_team_MIN",
      "rank": 10
    },
    {
      "absolute_importance": 0.7360621525210332,
      "coefficient": 0.7360621525210332,
      "direction": "positive",
      "feature": "categorical__previous_team_SF",
      "rank": 11
    },
    {
      "absolute_importance": 0.6950329769385298,
      "coefficient": -0.6950329769385298,
      "direction": "negative",
      "feature": "numeric__age_at_cutoff",
      "rank": 12
    },
    {
      "absolute_importance": 0.6150379995494737,
      "coefficient": -0.6150379995494737,
      "direction": "negative",
      "feature": "categorical__previous_team_NYJ",
      "rank": 13
    },
    {
      "absolute_importance": 0.5481027954041592,
      "coefficient": -0.5481027954041592,
      "direction": "negative",
      "feature": "numeric__draft_pick",
      "rank": 14
    },
    {
      "absolute_importance": 0.5160109488512241,
      "coefficient": 0.5160109488512241,
      "direction": "positive",
      "feature": "numeric__weighted_3yr_rushing_yards_per_game",
      "rank": 15
    },
    {
      "absolute_importance": 0.510426041128649,
      "coefficient": 0.510426041128649,
      "direction": "positive",
      "feature": "categorical__previous_team_SD",
      "rank": 16
    },
    {
      "absolute_importance": 0.4925670692347119,
      "coefficient": 0.4925670692347119,
      "direction": "positive",
      "feature": "categorical__previous_team_GB",
      "rank": 17
    },
    {
      "absolute_importance": 0.4542913179921976,
      "coefficient": 0.4542913179921976,
      "direction": "positive",
      "feature": "categorical__previous_team_TB",
      "rank": 18
    },
    {
      "absolute_importance": 0.4534651940165676,
      "coefficient": -0.4534651940165676,
      "direction": "negative",
      "feature": "categorical__previous_team_OAK",
      "rank": 19
    },
    {
      "absolute_importance": 0.43593448771443455,
      "coefficient": 0.43593448771443455,
      "direction": "positive",
      "feature": "categorical__previous_team_DAL",
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

- Project-relative path: `models/artifacts/phase4-052d2866899a665a44f3/attempt-331cdaf7eb7f4721aa43c08d469288ee/WR/fantasy_points_per_game/ridge.joblib`
- SHA-256: `666c550ee2cbdacc562219a0bba56772165f4e311b75f03bd3a831492ffbe60b`

## Additional metadata

````json
{
  "publication_id": "attempt-331cdaf7eb7f4721aa43c08d469288ee"
}
````
