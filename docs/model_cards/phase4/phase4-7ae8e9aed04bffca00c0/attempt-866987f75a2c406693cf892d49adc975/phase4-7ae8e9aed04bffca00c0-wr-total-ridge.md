# Model Card: phase4-7ae8e9aed04bffca00c0-wr-total-ridge

- Model ID: `phase4-7ae8e9aed04bffca00c0-wr-total-ridge`
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
  "position": "WR",
  "target_name": "fantasy_points_total",
  "test_mae": 22.81365285219276,
  "test_rows": 434,
  "test_season": 2025,
  "validation_mae": 27.94708190030799,
  "validation_rows": 2109,
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
    "candidate_mae": 21.523708175125215,
    "ci95_lower": -12.618731302160686,
    "ci95_upper": -10.211485247785019,
    "direction": "candidate_lower_mae",
    "mae_difference_candidate_minus_reference": -11.408538925578036,
    "n_resamples": 2000,
    "reference_mae": 32.93224710070325,
    "rows": 2109,
    "seed": 42
  },
  "decision_status": "learned_significant_improvement_selected",
  "learned_improvement_status": "statistically_clear",
  "reference_metrics": {
    "candidate_name": "age_position_adjusted",
    "candidate_source": "baseline",
    "position": "WR",
    "target_name": "fantasy_points_total",
    "test_mae": 32.06773123690993,
    "test_rows": 434,
    "test_season": 2025,
    "validation_mae": 32.93224710070325,
    "validation_rows": 2109,
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
  "this_candidate_selected": false
}
````

## Uncertainty estimates

````json
{
  "empirical_metrics_by_season": [
    {
      "candidate_name": "ridge",
      "empirical_coverage_p10_p90": 0.836405529953917,
      "evaluation_scope": "test",
      "mean_interval_width_p10_p90": 75.82978623796987,
      "pinball_loss_p10": 6.788341849280851,
      "pinball_loss_p50": 11.40682642609638,
      "pinball_loss_p90": 6.82716244447291,
      "position": "WR",
      "prediction_season": 2025,
      "projection_tier": "all",
      "rows": 434,
      "target_name": "fantasy_points_total"
    },
    {
      "candidate_name": "ridge",
      "empirical_coverage_p10_p90": 0.43119266055045874,
      "evaluation_scope": "test",
      "mean_interval_width_p10_p90": 75.82978623796986,
      "pinball_loss_p10": 14.385715341573414,
      "pinball_loss_p50": 26.039293842825348,
      "pinball_loss_p90": 15.767734376456202,
      "position": "WR",
      "prediction_season": 2025,
      "projection_tier": "top",
      "rows": 109,
      "target_name": "fantasy_points_total"
    },
    {
      "candidate_name": "ridge",
      "empirical_coverage_p10_p90": 0.9675925925925926,
      "evaluation_scope": "test",
      "mean_interval_width_p10_p90": 75.82978623796987,
      "pinball_loss_p10": 3.6709941319009882,
      "pinball_loss_p50": 5.742823035587329,
      "pinball_loss_p90": 4.449067213697272,
      "position": "WR",
      "prediction_season": 2025,
      "projection_tier": "middle",
      "rows": 216,
      "target_name": "fantasy_points_total"
    },
    {
      "candidate_name": "ridge",
      "empirical_coverage_p10_p90": 0.981651376146789,
      "evaluation_scope": "test",
      "mean_interval_width_p10_p90": 75.82978623796986,
      "pinball_loss_p10": 5.368464751062144,
      "pinball_loss_p50": 7.998439122669752,
      "pinball_loss_p90": 2.599146199164278,
      "position": "WR",
      "prediction_season": 2025,
      "projection_tier": "lower",
      "rows": 109,
      "target_name": "fantasy_points_total"
    },
    {
      "candidate_name": "ridge",
      "empirical_coverage_p10_p90": 0.8526570048309179,
      "evaluation_scope": "validation",
      "mean_interval_width_p10_p90": 131.80561606457533,
      "pinball_loss_p10": 7.3531847286537415,
      "pinball_loss_p50": 18.494917277733364,
      "pinball_loss_p90": 10.080168686575854,
      "position": "WR",
      "prediction_season": 2020,
      "projection_tier": "all",
      "rows": 414,
      "target_name": "fantasy_points_total"
    },
    {
      "candidate_name": "ridge",
      "empirical_coverage_p10_p90": 0.5769230769230769,
      "evaluation_scope": "validation",
      "mean_interval_width_p10_p90": 131.80561606457533,
      "pinball_loss_p10": 15.911130561122606,
      "pinball_loss_p50": 31.08103202609256,
      "pinball_loss_p90": 12.883126945733183,
      "position": "WR",
      "prediction_season": 2020,
      "projection_tier": "top",
      "rows": 104,
      "target_name": "fantasy_points_total"
    },
    {
      "candidate_name": "ridge",
      "empirical_coverage_p10_p90": 0.9174757281553398,
      "evaluation_scope": "validation",
      "mean_interval_width_p10_p90": 131.80561606457533,
      "pinball_loss_p10": 3.976105175663247,
      "pinball_loss_p50": 18.38566412026134,
      "pinball_loss_p90": 9.868686698707954,
      "position": "WR",
      "prediction_season": 2020,
      "projection_tier": "middle",
      "rows": 206,
      "target_name": "fantasy_points_total"
    },
    {
      "candidate_name": "ridge",
      "empirical_coverage_p10_p90": 1.0,
      "evaluation_scope": "validation",
      "mean_interval_width_p10_p90": 131.80561606457533,
      "pinball_loss_p10": 5.484454164608357,
      "pinball_loss_p50": 6.125207822059139,
      "pinball_loss_p90": 7.696107441849175,
      "position": "WR",
      "prediction_season": 2020,
      "projection_tier": "lower",
      "rows": 104,
      "target_name": "fantasy_points_total"
    },
    {
      "candidate_name": "ridge",
      "empirical_coverage_p10_p90": 0.8448687350835322,
      "evaluation_scope": "validation",
      "mean_interval_width_p10_p90": 125.86576077104148,
      "pinball_loss_p10": 8.032687035697021,
      "pinball_loss_p50": 14.951217492160753,
      "pinball_loss_p90": 11.093819717818947,
      "position": "WR",
      "prediction_season": 2021,
      "projection_tier": "all",
      "rows": 419,
      "target_name": "fantasy_points_total"
    },
    {
      "candidate_name": "ridge",
      "empirical_coverage_p10_p90": 0.5904761904761905,
      "evaluation_scope": "validation",
      "mean_interval_width_p10_p90": 125.86576077104148,
      "pinball_loss_p10": 16.72076366687701,
      "pinball_loss_p50": 29.169509878083563,
      "pinball_loss_p90": 13.950219862269787,
      "position": "WR",
      "prediction_season": 2021,
      "projection_tier": "top",
      "rows": 105,
      "target_name": "fantasy_points_total"
    },
    {
      "candidate_name": "ridge",
      "empirical_coverage_p10_p90": 0.9043062200956937,
      "evaluation_scope": "validation",
      "mean_interval_width_p10_p90": 125.86576077104148,
      "pinball_loss_p10": 4.5626072215319216,
      "pinball_loss_p50": 11.680239894022002,
      "pinball_loss_p90": 9.423743927967074,
      "position": "WR",
      "prediction_season": 2021,
      "projection_tier": "middle",
      "rows": 209,
      "target_name": "fantasy_points_total"
    },
    {
      "candidate_name": "ridge",
      "empirical_coverage_p10_p90": 0.9809523809523809,
      "evaluation_scope": "validation",
      "mean_interval_width_p10_p90": 125.86576077104148,
      "pinball_loss_p10": 6.251721653664708,
      "pinball_loss_p50": 7.243728134914127,
      "pinball_loss_p90": 11.561665669358984,
      "position": "WR",
      "prediction_season": 2021,
      "projection_tier": "lower",
      "rows": 105,
      "target_name": "fantasy_points_total"
    },
    {
      "candidate_name": "ridge",
      "empirical_coverage_p10_p90": 0.8310185185185185,
      "evaluation_scope": "validation",
      "mean_interval_width_p10_p90": 91.83355261184816,
      "pinball_loss_p10": 6.774438718011061,
      "pinball_loss_p50": 12.85030856331717,
      "pinball_loss_p90": 8.041257837978662,
      "position": "WR",
      "prediction_season": 2022,
      "projection_tier": "all",
      "rows": 432,
      "target_name": "fantasy_points_total"
    },
    {
      "candidate_name": "ridge",
      "empirical_coverage_p10_p90": 0.5,
      "evaluation_scope": "validation",
      "mean_interval_width_p10_p90": 91.83355261184816,
      "pinball_loss_p10": 14.367360396524365,
      "pinball_loss_p50": 26.17725559679971,
      "pinball_loss_p90": 12.021748694014176,
      "position": "WR",
      "prediction_season": 2022,
      "projection_tier": "top",
      "rows": 108,
      "target_name": "fantasy_points_total"
    },
    {
      "candidate_name": "ridge",
      "empirical_coverage_p10_p90": 0.9120370370370371,
      "evaluation_scope": "validation",
      "mean_interval_width_p10_p90": 91.83355261184816,
      "pinball_loss_p10": 3.848648354322221,
      "pinball_loss_p50": 10.892300075060437,
      "pinball_loss_p90": 7.996512581795549,
      "position": "WR",
      "prediction_season": 2022,
      "projection_tier": "middle",
      "rows": 216,
      "target_name": "fantasy_points_total"
    },
    {
      "candidate_name": "ridge",
      "empirical_coverage_p10_p90": 1.0,
      "evaluation_scope": "validation",
      "mean_interval_width_p10_p90": 91.83355261184815,
      "pinball_loss_p10": 5.033097766875437,
      "pinball_loss_p50": 3.439378506348101,
      "pinball_loss_p90": 4.150257494309378,
      "position": "WR",
      "prediction_season": 2022,
      "projection_tier": "lower",
      "rows": 108,
      "target_name": "fantasy_points_total"
    },
    {
      "candidate_name": "ridge",
      "empirical_coverage_p10_p90": 0.8424821002386634,
      "evaluation_scope": "validation",
      "mean_interval_width_p10_p90": 87.73004604978495,
      "pinball_loss_p10": 6.024234096879822,
      "pinball_loss_p50": 11.49937940595497,
      "pinball_loss_p90": 7.554913744338659,
      "position": "WR",
      "prediction_season": 2023,
      "projection_tier": "all",
      "rows": 419,
      "target_name": "fantasy_points_total"
    },
    {
      "candidate_name": "ridge",
      "empirical_coverage_p10_p90": 0.4666666666666667,
      "evaluation_scope": "validation",
      "mean_interval_width_p10_p90": 87.73004604978496,
      "pinball_loss_p10": 11.606121905282736,
      "pinball_loss_p50": 25.12069420429962,
      "pinball_loss_p90": 13.86937828836503,
      "position": "WR",
      "prediction_season": 2023,
      "projection_tier": "top",
      "rows": 105,
      "target_name": "fantasy_points_total"
    },
    {
      "candidate_name": "ridge",
      "empirical_coverage_p10_p90": 0.9569377990430622,
      "evaluation_scope": "validation",
      "mean_interval_width_p10_p90": 87.73004604978496,
      "pinball_loss_p10": 3.5810304416054133,
      "pinball_loss_p50": 7.31086918135258,
      "pinball_loss_p90": 6.358776493936052,
      "position": "WR",
      "prediction_season": 2023,
      "projection_tier": "middle",
      "rows": 209,
      "target_name": "fantasy_points_total"
    },
    {
      "candidate_name": "ridge",
      "empirical_coverage_p10_p90": 0.9904761904761905,
      "evaluation_scope": "validation",
      "mean_interval_width_p10_p90": 87.73004604978496,
      "pinball_loss_p10": 5.305484992785019,
      "pinball_loss_p50": 6.215194483247461,
      "pinball_loss_p90": 3.6213319177803305,
      "position": "WR",
      "prediction_season": 2023,
      "projection_tier": "lower",
      "rows": 105,
      "target_name": "fantasy_points_total"
    },
    {
      "candidate_name": "ridge",
      "empirical_coverage_p10_p90": 0.8,
      "evaluation_scope": "validation",
      "mean_interval_width_p10_p90": 80.6741358742481,
      "pinball_loss_p10": 6.573679001093363,
      "pinball_loss_p50": 12.18627932054036,
      "pinball_loss_p90": 8.114110130851214,
      "position": "WR",
      "prediction_season": 2024,
      "projection_tier": "all",
      "rows": 425,
      "target_name": "fantasy_points_total"
    },
    {
      "candidate_name": "ridge",
      "empirical_coverage_p10_p90": 0.36792452830188677,
      "evaluation_scope": "validation",
      "mean_interval_width_p10_p90": 80.6741358742481,
      "pinball_loss_p10": 12.850725147796755,
      "pinball_loss_p50": 26.07378796563042,
      "pinball_loss_p90": 15.77876628189165,
      "position": "WR",
      "prediction_season": 2024,
      "projection_tier": "top",
      "rows": 106,
      "target_name": "fantasy_points_total"
    },
    {
      "candidate_name": "ridge",
      "empirical_coverage_p10_p90": 0.9154929577464789,
      "evaluation_scope": "validation",
      "mean_interval_width_p10_p90": 80.6741358742481,
      "pinball_loss_p10": 4.08281506813638,
      "pinball_loss_p50": 7.573843053752062,
      "pinball_loss_p90": 6.961496900231903,
      "position": "WR",
      "prediction_season": 2024,
      "projection_tier": "middle",
      "rows": 213,
      "target_name": "fantasy_points_total"
    },
    {
      "candidate_name": "ridge",
      "empirical_coverage_p10_p90": 1.0,
      "evaluation_scope": "validation",
      "mean_interval_width_p10_p90": 80.6741358742481,
      "pinball_loss_p10": 5.301859436652583,
      "pinball_loss_p50": 7.5671567587135815,
      "pinball_loss_p90": 2.7655541507722257,
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
    "feature_response": "docs/images/phase4/phase4-7ae8e9aed04bffca00c0/attempt-866987f75a2c406693cf892d49adc975/feature_response.svg",
    "hgb_permutation_importance": "docs/images/phase4/phase4-7ae8e9aed04bffca00c0/attempt-866987f75a2c406693cf892d49adc975/hgb_permutation_importance.svg",
    "interval_coverage_width": "docs/images/phase4/phase4-7ae8e9aed04bffca00c0/attempt-866987f75a2c406693cf892d49adc975/interval_coverage_width.svg",
    "ridge_coefficients": "docs/images/phase4/phase4-7ae8e9aed04bffca00c0/attempt-866987f75a2c406693cf892d49adc975/ridge_coefficients.svg",
    "season_mae_comparison": "docs/images/phase4/phase4-7ae8e9aed04bffca00c0/attempt-866987f75a2c406693cf892d49adc975/season_mae_comparison.svg",
    "segment_mae": "docs/images/phase4/phase4-7ae8e9aed04bffca00c0/attempt-866987f75a2c406693cf892d49adc975/segment_mae.svg",
    "test_predicted_vs_actual": "docs/images/phase4/phase4-7ae8e9aed04bffca00c0/attempt-866987f75a2c406693cf892d49adc975/test_predicted_vs_actual.svg",
    "test_residuals": "docs/images/phase4/phase4-7ae8e9aed04bffca00c0/attempt-866987f75a2c406693cf892d49adc975/test_residuals.svg"
  },
  "feature_responses": [],
  "importance": [
    {
      "absolute_importance": 31.913528181807187,
      "coefficient": 31.913528181807187,
      "direction": "positive",
      "feature": "numeric__lag1_fantasy_points_total",
      "rank": 1
    },
    {
      "absolute_importance": 16.290730753045068,
      "coefficient": 16.290730753045068,
      "direction": "positive",
      "feature": "categorical__previous_team_MIN",
      "rank": 2
    },
    {
      "absolute_importance": 11.562470972515488,
      "coefficient": -11.562470972515488,
      "direction": "negative",
      "feature": "categorical__previous_team_NYG",
      "rank": 3
    },
    {
      "absolute_importance": 11.557398950573484,
      "coefficient": -11.557398950573484,
      "direction": "negative",
      "feature": "categorical__previous_team_JAX",
      "rank": 4
    },
    {
      "absolute_importance": 10.598827679522513,
      "coefficient": -10.598827679522513,
      "direction": "negative",
      "feature": "categorical__previous_team_NYJ",
      "rank": 5
    },
    {
      "absolute_importance": 10.249585943581916,
      "coefficient": 10.249585943581916,
      "direction": "positive",
      "feature": "categorical__previous_team_DAL",
      "rank": 6
    },
    {
      "absolute_importance": 9.924671432195053,
      "coefficient": -9.924671432195053,
      "direction": "negative",
      "feature": "categorical__previous_team_BAL",
      "rank": 7
    },
    {
      "absolute_importance": 9.720151383932386,
      "coefficient": 9.720151383932386,
      "direction": "positive",
      "feature": "numeric__weighted_3yr_receiving_yards_per_game",
      "rank": 8
    },
    {
      "absolute_importance": 8.039939836476604,
      "coefficient": 8.039939836476604,
      "direction": "positive",
      "feature": "numeric__lag1_fantasy_points_per_game",
      "rank": 9
    },
    {
      "absolute_importance": 7.900405526862853,
      "coefficient": 7.900405526862853,
      "direction": "positive",
      "feature": "categorical__previous_team_SEA",
      "rank": 10
    },
    {
      "absolute_importance": 7.792193154192434,
      "coefficient": 7.792193154192434,
      "direction": "positive",
      "feature": "categorical__previous_team_GB",
      "rank": 11
    },
    {
      "absolute_importance": 7.622852565847712,
      "coefficient": -7.622852565847712,
      "direction": "negative",
      "feature": "numeric__draft_pick",
      "rank": 12
    },
    {
      "absolute_importance": 7.439535825598526,
      "coefficient": -7.439535825598526,
      "direction": "negative",
      "feature": "categorical__previous_team_TEN",
      "rank": 13
    },
    {
      "absolute_importance": 7.339010196441981,
      "coefficient": -7.339010196441981,
      "direction": "negative",
      "feature": "categorical__previous_team_CLE",
      "rank": 14
    },
    {
      "absolute_importance": 7.1945500173259465,
      "coefficient": 7.1945500173259465,
      "direction": "positive",
      "feature": "categorical__previous_team_DET",
      "rank": 15
    },
    {
      "absolute_importance": 6.107289787087878,
      "coefficient": -6.107289787087878,
      "direction": "negative",
      "feature": "numeric__age_at_cutoff",
      "rank": 16
    },
    {
      "absolute_importance": 6.008609876487174,
      "coefficient": 6.008609876487174,
      "direction": "positive",
      "feature": "categorical__previous_team_STL",
      "rank": 17
    },
    {
      "absolute_importance": 5.956870000880809,
      "coefficient": 5.956870000880809,
      "direction": "positive",
      "feature": "categorical__previous_team_LA",
      "rank": 18
    },
    {
      "absolute_importance": 5.799191349702404,
      "coefficient": -5.799191349702404,
      "direction": "negative",
      "feature": "categorical__previous_team_NO",
      "rank": 19
    },
    {
      "absolute_importance": 5.395885272864394,
      "coefficient": 5.395885272864394,
      "direction": "positive",
      "feature": "numeric__weighted_3yr_fantasy_points_per_game",
      "rank": 20
    }
  ],
  "method": "standardized coefficients"
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

- Project-relative path: `models/artifacts/phase4-7ae8e9aed04bffca00c0/attempt-866987f75a2c406693cf892d49adc975/WR/fantasy_points_total/ridge.joblib`
- SHA-256: `2804b639c6d6930b0a2025febd1320583943d2e32f38f53720d57aedfdda0ef1`

## Additional metadata

````json
{
  "publication_id": "attempt-866987f75a2c406693cf892d49adc975"
}
````
