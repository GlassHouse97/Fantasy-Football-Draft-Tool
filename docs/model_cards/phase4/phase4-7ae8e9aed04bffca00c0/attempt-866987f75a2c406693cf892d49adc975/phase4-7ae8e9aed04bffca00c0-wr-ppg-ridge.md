# Model Card: phase4-7ae8e9aed04bffca00c0-wr-ppg-ridge

- Model ID: `phase4-7ae8e9aed04bffca00c0-wr-ppg-ridge`
- Trained at: 2026-08-05T20:58:13+00:00
- Target: `fantasy_points_per_game`
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
  "target_name": "fantasy_points_per_game",
  "test_mae": 2.132653544150065,
  "test_rows": 198,
  "test_season": 2025,
  "validation_mae": 2.5855815295906943,
  "validation_rows": 989,
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
    "candidate_mae": 2.367930773726267,
    "ci95_lower": -0.23545425147664406,
    "ci95_upper": -0.053987650009293967,
    "direction": "candidate_lower_mae",
    "mae_difference_candidate_minus_reference": -0.14159018367520027,
    "n_resamples": 2000,
    "reference_mae": 2.509520957401467,
    "rows": 989,
    "seed": 42
  },
  "decision_status": "learned_significant_improvement_selected",
  "learned_improvement_status": "statistically_clear",
  "reference_metrics": {
    "candidate_name": "age_position_adjusted",
    "candidate_source": "baseline",
    "position": "WR",
    "target_name": "fantasy_points_per_game",
    "test_mae": 2.2565557188552456,
    "test_rows": 198,
    "test_season": 2025,
    "validation_mae": 2.509520957401467,
    "validation_rows": 989,
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
      "empirical_coverage_p10_p90": 0.8939393939393939,
      "evaluation_scope": "test",
      "mean_interval_width_p10_p90": 7.824611270355044,
      "pinball_loss_p10": 0.4524867081874656,
      "pinball_loss_p50": 1.0663267720750325,
      "pinball_loss_p90": 0.5076506176198965,
      "position": "WR",
      "prediction_season": 2025,
      "projection_tier": "all",
      "rows": 198,
      "target_name": "fantasy_points_per_game"
    },
    {
      "candidate_name": "ridge",
      "empirical_coverage_p10_p90": 0.826530612244898,
      "evaluation_scope": "test",
      "mean_interval_width_p10_p90": 7.824611270355044,
      "pinball_loss_p10": 0.4508028493625019,
      "pinball_loss_p50": 1.278419039321923,
      "pinball_loss_p90": 0.6477208188257891,
      "position": "WR",
      "prediction_season": 2025,
      "projection_tier": "top",
      "rows": 98,
      "target_name": "fantasy_points_per_game"
    },
    {
      "candidate_name": "ridge",
      "empirical_coverage_p10_p90": 0.9487179487179487,
      "evaluation_scope": "test",
      "mean_interval_width_p10_p90": 7.824611270355042,
      "pinball_loss_p10": 0.4331016087681407,
      "pinball_loss_p50": 0.8268967896455957,
      "pinball_loss_p90": 0.403279496778322,
      "position": "WR",
      "prediction_season": 2025,
      "projection_tier": "middle",
      "rows": 78,
      "target_name": "fantasy_points_per_game"
    },
    {
      "candidate_name": "ridge",
      "empirical_coverage_p10_p90": 1.0,
      "evaluation_scope": "test",
      "mean_interval_width_p10_p90": 7.8246112703550414,
      "pinball_loss_p10": 0.5287165227126376,
      "pinball_loss_p50": 0.9704402465887043,
      "pinball_loss_p90": 0.2537446043228668,
      "position": "WR",
      "prediction_season": 2025,
      "projection_tier": "lower",
      "rows": 22,
      "target_name": "fantasy_points_per_game"
    },
    {
      "candidate_name": "ridge",
      "empirical_coverage_p10_p90": 0.9010416666666666,
      "evaluation_scope": "validation",
      "mean_interval_width_p10_p90": 11.207858132555272,
      "pinball_loss_p10": 0.5310832326643574,
      "pinball_loss_p50": 1.3777165905285278,
      "pinball_loss_p90": 0.7282241185498709,
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
      "mean_interval_width_p10_p90": 11.207858132555272,
      "pinball_loss_p10": 0.6701720018364249,
      "pinball_loss_p50": 1.5352449697234654,
      "pinball_loss_p90": 0.7123943017197972,
      "position": "WR",
      "prediction_season": 2020,
      "projection_tier": "top",
      "rows": 88,
      "target_name": "fantasy_points_per_game"
    },
    {
      "candidate_name": "ridge",
      "empirical_coverage_p10_p90": 0.9027777777777778,
      "evaluation_scope": "validation",
      "mean_interval_width_p10_p90": 11.207858132555272,
      "pinball_loss_p10": 0.3881288167804204,
      "pinball_loss_p50": 1.49773399964191,
      "pinball_loss_p90": 0.782093831775239,
      "position": "WR",
      "prediction_season": 2020,
      "projection_tier": "middle",
      "rows": 72,
      "target_name": "fantasy_points_per_game"
    },
    {
      "candidate_name": "ridge",
      "empirical_coverage_p10_p90": 1.0,
      "evaluation_scope": "validation",
      "mean_interval_width_p10_p90": 11.20785813255527,
      "pinball_loss_p10": 0.470236553180031,
      "pinball_loss_p50": 0.6744743772373392,
      "pinball_loss_p90": 0.6505492600754958,
      "position": "WR",
      "prediction_season": 2020,
      "projection_tier": "lower",
      "rows": 32,
      "target_name": "fantasy_points_per_game"
    },
    {
      "candidate_name": "ridge",
      "empirical_coverage_p10_p90": 0.8443396226415094,
      "evaluation_scope": "validation",
      "mean_interval_width_p10_p90": 10.378034898965797,
      "pinball_loss_p10": 0.6036639870470148,
      "pinball_loss_p50": 1.46630561216446,
      "pinball_loss_p90": 0.8960439091846434,
      "position": "WR",
      "prediction_season": 2021,
      "projection_tier": "all",
      "rows": 212,
      "target_name": "fantasy_points_per_game"
    },
    {
      "candidate_name": "ridge",
      "empirical_coverage_p10_p90": 0.7676767676767676,
      "evaluation_scope": "validation",
      "mean_interval_width_p10_p90": 10.378034898965796,
      "pinball_loss_p10": 0.7933792967392997,
      "pinball_loss_p50": 1.6259718608750795,
      "pinball_loss_p90": 0.8799813731799592,
      "position": "WR",
      "prediction_season": 2021,
      "projection_tier": "top",
      "rows": 99,
      "target_name": "fantasy_points_per_game"
    },
    {
      "candidate_name": "ridge",
      "empirical_coverage_p10_p90": 0.9010989010989011,
      "evaluation_scope": "validation",
      "mean_interval_width_p10_p90": 10.378034898965794,
      "pinball_loss_p10": 0.3922427647307187,
      "pinball_loss_p50": 1.2910899797479725,
      "pinball_loss_p90": 0.7151060360580278,
      "position": "WR",
      "prediction_season": 2021,
      "projection_tier": "middle",
      "rows": 91,
      "target_name": "fantasy_points_per_game"
    },
    {
      "candidate_name": "ridge",
      "empirical_coverage_p10_p90": 0.9545454545454546,
      "evaluation_scope": "validation",
      "mean_interval_width_p10_p90": 10.378034898965801,
      "pinball_loss_p10": 0.6244601493764137,
      "pinball_loss_p50": 1.4725630634166882,
      "pinball_loss_p90": 1.7167501600476305,
      "position": "WR",
      "prediction_season": 2021,
      "projection_tier": "lower",
      "rows": 22,
      "target_name": "fantasy_points_per_game"
    },
    {
      "candidate_name": "ridge",
      "empirical_coverage_p10_p90": 0.815,
      "evaluation_scope": "validation",
      "mean_interval_width_p10_p90": 8.333552649325355,
      "pinball_loss_p10": 0.5031005019330093,
      "pinball_loss_p50": 1.1975260817079572,
      "pinball_loss_p90": 0.5806544420166593,
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
      "mean_interval_width_p10_p90": 8.333552649325357,
      "pinball_loss_p10": 0.6064624383925796,
      "pinball_loss_p50": 1.3687737027645368,
      "pinball_loss_p90": 0.5719455850855214,
      "position": "WR",
      "prediction_season": 2022,
      "projection_tier": "top",
      "rows": 100,
      "target_name": "fantasy_points_per_game"
    },
    {
      "candidate_name": "ridge",
      "empirical_coverage_p10_p90": 0.8701298701298701,
      "evaluation_scope": "validation",
      "mean_interval_width_p10_p90": 8.333552649325357,
      "pinball_loss_p10": 0.3739287027733588,
      "pinball_loss_p50": 1.094340564946796,
      "pinball_loss_p90": 0.5844491656217765,
      "position": "WR",
      "prediction_season": 2022,
      "projection_tier": "middle",
      "rows": 77,
      "target_name": "fantasy_points_per_game"
    },
    {
      "candidate_name": "ridge",
      "empirical_coverage_p10_p90": 0.9130434782608695,
      "evaluation_scope": "validation",
      "mean_interval_width_p10_p90": 8.333552649325355,
      "pinball_loss_p10": 0.4861454971215341,
      "pinball_loss_p50": 0.7984183723580205,
      "pinball_loss_p90": 0.6058149626914319,
      "position": "WR",
      "prediction_season": 2022,
      "projection_tier": "lower",
      "rows": 23,
      "target_name": "fantasy_points_per_game"
    },
    {
      "candidate_name": "ridge",
      "empirical_coverage_p10_p90": 0.8324607329842932,
      "evaluation_scope": "validation",
      "mean_interval_width_p10_p90": 7.980678217288275,
      "pinball_loss_p10": 0.46398853282397257,
      "pinball_loss_p50": 1.0685507938341974,
      "pinball_loss_p90": 0.5837372283311871,
      "position": "WR",
      "prediction_season": 2023,
      "projection_tier": "all",
      "rows": 191,
      "target_name": "fantasy_points_per_game"
    },
    {
      "candidate_name": "ridge",
      "empirical_coverage_p10_p90": 0.7216494845360825,
      "evaluation_scope": "validation",
      "mean_interval_width_p10_p90": 7.980678217288275,
      "pinball_loss_p10": 0.5564898872727618,
      "pinball_loss_p50": 1.3641972822250965,
      "pinball_loss_p90": 0.6714465667824833,
      "position": "WR",
      "prediction_season": 2023,
      "projection_tier": "top",
      "rows": 97,
      "target_name": "fantasy_points_per_game"
    },
    {
      "candidate_name": "ridge",
      "empirical_coverage_p10_p90": 0.9459459459459459,
      "evaluation_scope": "validation",
      "mean_interval_width_p10_p90": 7.9806782172882755,
      "pinball_loss_p10": 0.3378053196774058,
      "pinball_loss_p50": 0.7733311257133467,
      "pinball_loss_p90": 0.5113948264951239,
      "position": "WR",
      "prediction_season": 2023,
      "projection_tier": "middle",
      "rows": 74,
      "target_name": "fantasy_points_per_game"
    },
    {
      "candidate_name": "ridge",
      "empirical_coverage_p10_p90": 0.95,
      "evaluation_scope": "validation",
      "mean_interval_width_p10_p90": 7.980678217288275,
      "pinball_loss_p10": 0.48223485238964237,
      "pinball_loss_p50": 0.7269780971854862,
      "pinball_loss_p90": 0.42601382363583473,
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
      "mean_interval_width_p10_p90": 7.525681273283739,
      "pinball_loss_p10": 0.5377239017738457,
      "pinball_loss_p50": 1.3381096559707848,
      "pinball_loss_p90": 0.6843079797174065,
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
      "mean_interval_width_p10_p90": 7.525681273283741,
      "pinball_loss_p10": 0.5531264411357962,
      "pinball_loss_p50": 1.5836305822082002,
      "pinball_loss_p90": 0.7998093798982302,
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
      "mean_interval_width_p10_p90": 7.525681273283743,
      "pinball_loss_p10": 0.5154120195206694,
      "pinball_loss_p50": 1.1134718561716996,
      "pinball_loss_p90": 0.6434260607029395,
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
      "mean_interval_width_p10_p90": 7.52568127328374,
      "pinball_loss_p10": 0.5690856675534532,
      "pinball_loss_p50": 1.133792504025728,
      "pinball_loss_p90": 0.23991524338043083,
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
      "absolute_importance": 1.650075924029596,
      "coefficient": 1.650075924029596,
      "direction": "positive",
      "feature": "numeric__lag1_fantasy_points_total",
      "rank": 1
    },
    {
      "absolute_importance": 1.4209322247622251,
      "coefficient": 1.4209322247622251,
      "direction": "positive",
      "feature": "numeric__weighted_3yr_receiving_yards_per_game",
      "rank": 2
    },
    {
      "absolute_importance": 1.164146259876699,
      "coefficient": -1.164146259876699,
      "direction": "negative",
      "feature": "categorical__previous_team_JAX",
      "rank": 3
    },
    {
      "absolute_importance": 1.031416441066438,
      "coefficient": 1.031416441066438,
      "direction": "positive",
      "feature": "numeric__weighted_3yr_fantasy_points_per_game",
      "rank": 4
    },
    {
      "absolute_importance": 1.015527927813902,
      "coefficient": 1.015527927813902,
      "direction": "positive",
      "feature": "numeric__weighted_3yr_receptions_per_game",
      "rank": 5
    },
    {
      "absolute_importance": 1.0025440566000665,
      "coefficient": 1.0025440566000665,
      "direction": "positive",
      "feature": "categorical__previous_team_DET",
      "rank": 6
    },
    {
      "absolute_importance": 0.9450047924657364,
      "coefficient": -0.9450047924657364,
      "direction": "negative",
      "feature": "categorical__previous_team_BAL",
      "rank": 7
    },
    {
      "absolute_importance": 0.7730681156919367,
      "coefficient": -0.7730681156919367,
      "direction": "negative",
      "feature": "categorical__previous_team_TEN",
      "rank": 8
    },
    {
      "absolute_importance": 0.745096114186044,
      "coefficient": -0.745096114186044,
      "direction": "negative",
      "feature": "categorical__previous_team_CAR",
      "rank": 9
    },
    {
      "absolute_importance": 0.7425949492584415,
      "coefficient": 0.7425949492584415,
      "direction": "positive",
      "feature": "categorical__previous_team_MIN",
      "rank": 10
    },
    {
      "absolute_importance": 0.7348485309982858,
      "coefficient": 0.7348485309982858,
      "direction": "positive",
      "feature": "categorical__previous_team_SF",
      "rank": 11
    },
    {
      "absolute_importance": 0.6394830761443837,
      "coefficient": -0.6394830761443837,
      "direction": "negative",
      "feature": "numeric__age_at_cutoff",
      "rank": 12
    },
    {
      "absolute_importance": 0.6109293925560858,
      "coefficient": -0.6109293925560858,
      "direction": "negative",
      "feature": "categorical__previous_team_NYJ",
      "rank": 13
    },
    {
      "absolute_importance": 0.55107715961266,
      "coefficient": -0.55107715961266,
      "direction": "negative",
      "feature": "numeric__draft_pick",
      "rank": 14
    },
    {
      "absolute_importance": 0.5145745279805188,
      "coefficient": 0.5145745279805188,
      "direction": "positive",
      "feature": "numeric__weighted_3yr_rushing_yards_per_game",
      "rank": 15
    },
    {
      "absolute_importance": 0.5100924131257106,
      "coefficient": 0.5100924131257106,
      "direction": "positive",
      "feature": "categorical__previous_team_SD",
      "rank": 16
    },
    {
      "absolute_importance": 0.4902777153822069,
      "coefficient": 0.4902777153822069,
      "direction": "positive",
      "feature": "categorical__previous_team_GB",
      "rank": 17
    },
    {
      "absolute_importance": 0.45138374849811275,
      "coefficient": 0.45138374849811275,
      "direction": "positive",
      "feature": "categorical__previous_team_TB",
      "rank": 18
    },
    {
      "absolute_importance": 0.45107269447525244,
      "coefficient": -0.45107269447525244,
      "direction": "negative",
      "feature": "categorical__previous_team_OAK",
      "rank": 19
    },
    {
      "absolute_importance": 0.4378839007016254,
      "coefficient": 0.4378839007016254,
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

- Project-relative path: `models/artifacts/phase4-7ae8e9aed04bffca00c0/attempt-866987f75a2c406693cf892d49adc975/WR/fantasy_points_per_game/ridge.joblib`
- SHA-256: `fef87df318cb6429f6728b2d19c85ff847ac4449ac3e6f75c695c4a02809ec65`

## Additional metadata

````json
{
  "publication_id": "attempt-866987f75a2c406693cf892d49adc975"
}
````
