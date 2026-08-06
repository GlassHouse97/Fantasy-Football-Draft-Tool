# Model Card: phase4-7ae8e9aed04bffca00c0-rb-games-ridge

- Model ID: `phase4-7ae8e9aed04bffca00c0-rb-games-ridge`
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
  "position": "RB",
  "target_name": "games_active",
  "test_mae": 2.9942114253182686,
  "test_rows": 294,
  "test_season": 2025,
  "validation_mae": 3.127836452504436,
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
      "mean_interval_width_p10_p90": 8.468071258231266,
      "pinball_loss_p10": 0.6002213948921938,
      "pinball_loss_p50": 1.4971057126591343,
      "pinball_loss_p90": 0.8060807273466155,
      "position": "RB",
      "prediction_season": 2025,
      "projection_tier": "all",
      "rows": 294,
      "target_name": "games_active"
    },
    {
      "candidate_name": "ridge",
      "empirical_coverage_p10_p90": 0.6756756756756757,
      "evaluation_scope": "test",
      "mean_interval_width_p10_p90": 11.103194143619504,
      "pinball_loss_p10": 1.3666375443585213,
      "pinball_loss_p50": 2.4235638564930198,
      "pinball_loss_p90": 0.5548073872910105,
      "position": "RB",
      "prediction_season": 2025,
      "projection_tier": "top",
      "rows": 74,
      "target_name": "games_active"
    },
    {
      "candidate_name": "ridge",
      "empirical_coverage_p10_p90": 0.7328767123287672,
      "evaluation_scope": "test",
      "mean_interval_width_p10_p90": 8.704153579935507,
      "pinball_loss_p10": 0.5016021357244822,
      "pinball_loss_p50": 1.7111292961523763,
      "pinball_loss_p90": 1.0411594548164032,
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
      "mean_interval_width_p10_p90": 5.367164332723853,
      "pinball_loss_p10": 0.028378378378378387,
      "pinball_loss_p50": 0.14838482301425815,
      "pinball_loss_p90": 0.5935500915834503,
      "position": "RB",
      "prediction_season": 2025,
      "projection_tier": "lower",
      "rows": 74,
      "target_name": "games_active"
    },
    {
      "candidate_name": "ridge",
      "empirical_coverage_p10_p90": 0.8106312292358804,
      "evaluation_scope": "validation",
      "mean_interval_width_p10_p90": 8.751559299887587,
      "pinball_loss_p10": 0.5206605437621973,
      "pinball_loss_p50": 1.4228587911764812,
      "pinball_loss_p90": 0.8017800462945834,
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
      "mean_interval_width_p10_p90": 12.286732427339459,
      "pinball_loss_p10": 1.132044643721851,
      "pinball_loss_p50": 2.2532085162931796,
      "pinball_loss_p90": 0.5382912857623142,
      "position": "RB",
      "prediction_season": 2020,
      "projection_tier": "top",
      "rows": 76,
      "target_name": "games_active"
    },
    {
      "candidate_name": "ridge",
      "empirical_coverage_p10_p90": 0.7466666666666667,
      "evaluation_scope": "validation",
      "mean_interval_width_p10_p90": 8.564156778410677,
      "pinball_loss_p10": 0.4538895383304049,
      "pinball_loss_p50": 1.6269109927055945,
      "pinball_loss_p90": 1.0125173793549043,
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
      "mean_interval_width_p10_p90": 5.544055573690174,
      "pinball_loss_p10": 0.034666666666666665,
      "pinball_loss_p50": 0.17333333333333334,
      "pinball_loss_p90": 0.6473073241799743,
      "position": "RB",
      "prediction_season": 2020,
      "projection_tier": "lower",
      "rows": 75,
      "target_name": "games_active"
    },
    {
      "candidate_name": "ridge",
      "empirical_coverage_p10_p90": 0.8172757475083057,
      "evaluation_scope": "validation",
      "mean_interval_width_p10_p90": 9.562102622176745,
      "pinball_loss_p10": 0.6068647363234361,
      "pinball_loss_p50": 1.6196505863854913,
      "pinball_loss_p90": 0.821088485644088,
      "position": "RB",
      "prediction_season": 2021,
      "projection_tier": "all",
      "rows": 301,
      "target_name": "games_active"
    },
    {
      "candidate_name": "ridge",
      "empirical_coverage_p10_p90": 0.7763157894736842,
      "evaluation_scope": "validation",
      "mean_interval_width_p10_p90": 11.583292130766067,
      "pinball_loss_p10": 1.3162084983653088,
      "pinball_loss_p50": 2.250622233156193,
      "pinball_loss_p90": 0.5943153486734293,
      "position": "RB",
      "prediction_season": 2021,
      "projection_tier": "top",
      "rows": 76,
      "target_name": "games_active"
    },
    {
      "candidate_name": "ridge",
      "empirical_coverage_p10_p90": 0.7516778523489933,
      "evaluation_scope": "validation",
      "mean_interval_width_p10_p90": 10.358321852826611,
      "pinball_loss_p10": 0.5431841594469177,
      "pinball_loss_p50": 1.9951195552554473,
      "pinball_loss_p90": 0.9909330990242896,
      "position": "RB",
      "prediction_season": 2021,
      "projection_tier": "middle",
      "rows": 149,
      "target_name": "games_active"
    },
    {
      "candidate_name": "ridge",
      "empirical_coverage_p10_p90": 0.9868421052631579,
      "evaluation_scope": "validation",
      "mean_interval_width_p10_p90": 5.979904358760713,
      "pinball_loss_p10": 0.022368421052631583,
      "pinball_loss_p50": 0.25256214538290184,
      "pinball_loss_p90": 0.7148767884877721,
      "position": "RB",
      "prediction_season": 2021,
      "projection_tier": "lower",
      "rows": 76,
      "target_name": "games_active"
    },
    {
      "candidate_name": "ridge",
      "empirical_coverage_p10_p90": 0.7905405405405406,
      "evaluation_scope": "validation",
      "mean_interval_width_p10_p90": 9.625484683110567,
      "pinball_loss_p10": 0.5777445420744035,
      "pinball_loss_p50": 1.6901183580707828,
      "pinball_loss_p90": 0.8054156486946553,
      "position": "RB",
      "prediction_season": 2022,
      "projection_tier": "all",
      "rows": 296,
      "target_name": "games_active"
    },
    {
      "candidate_name": "ridge",
      "empirical_coverage_p10_p90": 0.8378378378378378,
      "evaluation_scope": "validation",
      "mean_interval_width_p10_p90": 11.334238818286218,
      "pinball_loss_p10": 0.9966783369349638,
      "pinball_loss_p50": 1.9055398679436608,
      "pinball_loss_p90": 0.45308870741955504,
      "position": "RB",
      "prediction_season": 2022,
      "projection_tier": "top",
      "rows": 74,
      "target_name": "games_active"
    },
    {
      "candidate_name": "ridge",
      "empirical_coverage_p10_p90": 0.6621621621621622,
      "evaluation_scope": "validation",
      "mean_interval_width_p10_p90": 10.532381756514093,
      "pinball_loss_p10": 0.6557985643299739,
      "pinball_loss_p50": 2.3224055302891875,
      "pinball_loss_p90": 1.0804914749744916,
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
      "mean_interval_width_p10_p90": 6.10293640112786,
      "pinball_loss_p10": 0.002702702702702703,
      "pinball_loss_p50": 0.21012250376109487,
      "pinball_loss_p90": 0.6075909374100833,
      "position": "RB",
      "prediction_season": 2022,
      "projection_tier": "lower",
      "rows": 74,
      "target_name": "games_active"
    },
    {
      "candidate_name": "ridge",
      "empirical_coverage_p10_p90": 0.8041237113402062,
      "evaluation_scope": "validation",
      "mean_interval_width_p10_p90": 9.109866726003391,
      "pinball_loss_p10": 0.6134862407637706,
      "pinball_loss_p50": 1.6248281992573463,
      "pinball_loss_p90": 0.82174973838792,
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
      "mean_interval_width_p10_p90": 11.474158957788827,
      "pinball_loss_p10": 1.3701731507480863,
      "pinball_loss_p50": 2.373773466407415,
      "pinball_loss_p90": 0.5542783365411671,
      "position": "RB",
      "prediction_season": 2023,
      "projection_tier": "top",
      "rows": 73,
      "target_name": "games_active"
    },
    {
      "candidate_name": "ridge",
      "empirical_coverage_p10_p90": 0.7379310344827587,
      "evaluation_scope": "validation",
      "mean_interval_width_p10_p90": 9.731011498952606,
      "pinball_loss_p10": 0.5393231452251512,
      "pinball_loss_p50": 2.0285491192441505,
      "pinball_loss_p90": 1.094694901402428,
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
      "mean_interval_width_p10_p90": 5.51179378082568,
      "pinball_loss_p10": 0.004109589041095891,
      "pinball_loss_p50": 0.07397151569513152,
      "pinball_loss_p90": 0.547069789041472,
      "position": "RB",
      "prediction_season": 2023,
      "projection_tier": "lower",
      "rows": 73,
      "target_name": "games_active"
    },
    {
      "candidate_name": "ridge",
      "empirical_coverage_p10_p90": 0.8231292517006803,
      "evaluation_scope": "validation",
      "mean_interval_width_p10_p90": 8.612173601203061,
      "pinball_loss_p10": 0.5315951069766225,
      "pinball_loss_p50": 1.4639298194321293,
      "pinball_loss_p90": 0.874773120909758,
      "position": "RB",
      "prediction_season": 2024,
      "projection_tier": "all",
      "rows": 294,
      "target_name": "games_active"
    },
    {
      "candidate_name": "ridge",
      "empirical_coverage_p10_p90": 0.8243243243243243,
      "evaluation_scope": "validation",
      "mean_interval_width_p10_p90": 11.358777041052925,
      "pinball_loss_p10": 1.1090952799628577,
      "pinball_loss_p50": 2.1213147321081536,
      "pinball_loss_p90": 0.421048203087965,
      "position": "RB",
      "prediction_season": 2024,
      "projection_tier": "top",
      "rows": 74,
      "target_name": "games_active"
    },
    {
      "candidate_name": "ridge",
      "empirical_coverage_p10_p90": 0.7397260273972602,
      "evaluation_scope": "validation",
      "mean_interval_width_p10_p90": 8.982744570554896,
      "pinball_loss_p10": 0.5014788406429835,
      "pinball_loss_p50": 1.8384799776509773,
      "pinball_loss_p90": 1.2888216626031404,
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
      "mean_interval_width_p10_p90": 5.134443654253628,
      "pinball_loss_p10": 0.013513513513513514,
      "pinball_loss_p50": 0.06756756756756757,
      "pinball_loss_p90": 0.5115914564716348,
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
      "absolute_importance": 1.9117287260409679,
      "coefficient": 1.9117287260409679,
      "direction": "positive",
      "feature": "numeric__lag1_games_active",
      "rank": 1
    },
    {
      "absolute_importance": 1.8055564383653617,
      "coefficient": 1.8055564383653617,
      "direction": "positive",
      "feature": "categorical__previous_team_NE",
      "rank": 2
    },
    {
      "absolute_importance": 1.7644658430885503,
      "coefficient": 1.7644658430885503,
      "direction": "positive",
      "feature": "categorical__previous_team_MIN",
      "rank": 3
    },
    {
      "absolute_importance": 1.7296950240982751,
      "coefficient": -1.7296950240982751,
      "direction": "negative",
      "feature": "categorical__previous_team_NYJ",
      "rank": 4
    },
    {
      "absolute_importance": 1.3025001011400175,
      "coefficient": -1.3025001011400175,
      "direction": "negative",
      "feature": "categorical__previous_team_NYG",
      "rank": 5
    },
    {
      "absolute_importance": 1.2919230243297297,
      "coefficient": -1.2919230243297297,
      "direction": "negative",
      "feature": "categorical__previous_team_SD",
      "rank": 6
    },
    {
      "absolute_importance": 1.2832601031569197,
      "coefficient": 1.2832601031569197,
      "direction": "positive",
      "feature": "numeric__weighted_3yr_rushing_yards_per_game",
      "rank": 7
    },
    {
      "absolute_importance": 1.1558294640684794,
      "coefficient": 1.1558294640684794,
      "direction": "positive",
      "feature": "numeric__lag1_fantasy_points_per_game",
      "rank": 8
    },
    {
      "absolute_importance": 1.0733962337250578,
      "coefficient": -1.0733962337250578,
      "direction": "negative",
      "feature": "numeric__weighted_3yr_carries_per_game",
      "rank": 9
    },
    {
      "absolute_importance": 0.9814063745729755,
      "coefficient": 0.9814063745729755,
      "direction": "positive",
      "feature": "categorical__previous_team_STL",
      "rank": 10
    },
    {
      "absolute_importance": 0.9704861323849446,
      "coefficient": -0.9704861323849446,
      "direction": "negative",
      "feature": "numeric__lag1_fantasy_points_total",
      "rank": 11
    },
    {
      "absolute_importance": 0.9486161970269485,
      "coefficient": 0.9486161970269485,
      "direction": "positive",
      "feature": "categorical__previous_team_PHI",
      "rank": 12
    },
    {
      "absolute_importance": 0.7253172783116915,
      "coefficient": 0.7253172783116915,
      "direction": "positive",
      "feature": "categorical__previous_team_SF",
      "rank": 13
    },
    {
      "absolute_importance": 0.6611281600209736,
      "coefficient": -0.6611281600209736,
      "direction": "negative",
      "feature": "numeric__missing_lag1",
      "rank": 14
    },
    {
      "absolute_importance": 0.6611281600209736,
      "coefficient": -0.6611281600209736,
      "direction": "negative",
      "feature": "numeric__missingindicator_lag1_fantasy_points_per_game",
      "rank": 15
    },
    {
      "absolute_importance": 0.6611281600209736,
      "coefficient": -0.6611281600209736,
      "direction": "negative",
      "feature": "numeric__missingindicator_lag1_fantasy_points_total",
      "rank": 16
    },
    {
      "absolute_importance": 0.6611281600209736,
      "coefficient": -0.6611281600209736,
      "direction": "negative",
      "feature": "numeric__missingindicator_lag1_games_active",
      "rank": 17
    },
    {
      "absolute_importance": 0.6611281600209736,
      "coefficient": -0.6611281600209736,
      "direction": "negative",
      "feature": "numeric__missingindicator_lag1_stat_games",
      "rank": 18
    },
    {
      "absolute_importance": 0.6411570673917826,
      "coefficient": -0.6411570673917826,
      "direction": "negative",
      "feature": "categorical__previous_team_WAS",
      "rank": 19
    },
    {
      "absolute_importance": 0.6324075986912319,
      "coefficient": 0.6324075986912319,
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

- Project-relative path: `models/artifacts/phase4-7ae8e9aed04bffca00c0/attempt-866987f75a2c406693cf892d49adc975/RB/games_active/ridge.joblib`
- SHA-256: `c6886aca5df0ab08315d29a86184e8eab88545ddaf9370a355b4abfdb2f958e1`

## Additional metadata

````json
{
  "publication_id": "attempt-866987f75a2c406693cf892d49adc975"
}
````
