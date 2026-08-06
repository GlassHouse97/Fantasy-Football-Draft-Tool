# Model Card: phase4-7ae8e9aed04bffca00c0-wr-games-ridge

- Model ID: `phase4-7ae8e9aed04bffca00c0-wr-games-ridge`
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
  "position": "WR",
  "target_name": "games_active",
  "test_mae": 2.9495711715939277,
  "test_rows": 433,
  "test_season": 2025,
  "validation_mae": 3.1387154767874796,
  "validation_rows": 2101,
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
    "candidate_mae": 2.9177447114825092,
    "ci95_lower": -3.2568108709171186,
    "ci95_upper": -2.789372956939834,
    "direction": "candidate_lower_mae",
    "mae_difference_candidate_minus_reference": -3.0211359344260806,
    "n_resamples": 2000,
    "reference_mae": 5.93888064590859,
    "rows": 2101,
    "seed": 42
  },
  "decision_status": "learned_significant_improvement_selected",
  "learned_improvement_status": "statistically_clear",
  "reference_metrics": {
    "candidate_name": "age_position_adjusted",
    "candidate_source": "baseline",
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
      "empirical_coverage_p10_p90": 0.8060046189376443,
      "evaluation_scope": "test",
      "mean_interval_width_p10_p90": 8.329946666641456,
      "pinball_loss_p10": 0.5653989737750037,
      "pinball_loss_p50": 1.4747855857969638,
      "pinball_loss_p90": 0.8279587024210043,
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
      "mean_interval_width_p10_p90": 10.234972787614366,
      "pinball_loss_p10": 1.1190698955053613,
      "pinball_loss_p50": 1.9803319534582644,
      "pinball_loss_p90": 0.5268339962788537,
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
      "mean_interval_width_p10_p90": 8.949093117669692,
      "pinball_loss_p10": 0.547158776904615,
      "pinball_loss_p50": 1.843023875454985,
      "pinball_loss_p90": 1.0353268959271213,
      "position": "WR",
      "prediction_season": 2025,
      "projection_tier": "middle",
      "rows": 215,
      "target_name": "games_active"
    },
    {
      "candidate_name": "ridge",
      "empirical_coverage_p10_p90": 0.9724770642201835,
      "evaluation_scope": "test",
      "mean_interval_width_p10_p90": 5.20366837162203,
      "pinball_loss_p10": 0.047706422018348627,
      "pinball_loss_p50": 0.24289763761754898,
      "pinball_loss_p90": 0.7200544030235668,
      "position": "WR",
      "prediction_season": 2025,
      "projection_tier": "lower",
      "rows": 109,
      "target_name": "games_active"
    },
    {
      "candidate_name": "ridge",
      "empirical_coverage_p10_p90": 0.8179611650485437,
      "evaluation_scope": "validation",
      "mean_interval_width_p10_p90": 9.557641817631126,
      "pinball_loss_p10": 0.6076266629635599,
      "pinball_loss_p50": 1.620761013200519,
      "pinball_loss_p90": 0.8506658434846179,
      "position": "WR",
      "prediction_season": 2020,
      "projection_tier": "all",
      "rows": 412,
      "target_name": "games_active"
    },
    {
      "candidate_name": "ridge",
      "empirical_coverage_p10_p90": 0.7980769230769231,
      "evaluation_scope": "validation",
      "mean_interval_width_p10_p90": 10.78337856729696,
      "pinball_loss_p10": 1.320893763095905,
      "pinball_loss_p50": 1.9688848603883284,
      "pinball_loss_p90": 0.5581946731636676,
      "position": "WR",
      "prediction_season": 2020,
      "projection_tier": "top",
      "rows": 104,
      "target_name": "games_active"
    },
    {
      "candidate_name": "ridge",
      "empirical_coverage_p10_p90": 0.7365853658536585,
      "evaluation_scope": "validation",
      "mean_interval_width_p10_p90": 10.426953032797034,
      "pinball_loss_p10": 0.5466791891659151,
      "pinball_loss_p50": 2.123508569035073,
      "pinball_loss_p90": 1.0997410384998363,
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
      "mean_interval_width_p10_p90": 6.589822195550943,
      "pinball_loss_p10": 0.008737864077669903,
      "pinball_loss_p50": 0.2686432553984244,
      "pinball_loss_p90": 0.6502443554774247,
      "position": "WR",
      "prediction_season": 2020,
      "projection_tier": "lower",
      "rows": 103,
      "target_name": "games_active"
    },
    {
      "candidate_name": "ridge",
      "empirical_coverage_p10_p90": 0.8229665071770335,
      "evaluation_scope": "validation",
      "mean_interval_width_p10_p90": 9.213987689652642,
      "pinball_loss_p10": 0.5740691323466526,
      "pinball_loss_p50": 1.6191285202826398,
      "pinball_loss_p90": 0.9082401751291584,
      "position": "WR",
      "prediction_season": 2021,
      "projection_tier": "all",
      "rows": 418,
      "target_name": "games_active"
    },
    {
      "candidate_name": "ridge",
      "empirical_coverage_p10_p90": 0.8095238095238095,
      "evaluation_scope": "validation",
      "mean_interval_width_p10_p90": 11.011679922784207,
      "pinball_loss_p10": 1.1052801546260196,
      "pinball_loss_p50": 2.1369055961535124,
      "pinball_loss_p90": 0.5127503328054516,
      "position": "WR",
      "prediction_season": 2021,
      "projection_tier": "top",
      "rows": 105,
      "target_name": "games_active"
    },
    {
      "candidate_name": "ridge",
      "empirical_coverage_p10_p90": 0.7548076923076923,
      "evaluation_scope": "validation",
      "mean_interval_width_p10_p90": 9.913204341299622,
      "pinball_loss_p10": 0.5707042359863881,
      "pinball_loss_p50": 2.015909163271659,
      "pinball_loss_p90": 1.166959729053818,
      "position": "WR",
      "prediction_season": 2021,
      "projection_tier": "middle",
      "rows": 208,
      "target_name": "games_active"
    },
    {
      "candidate_name": "ridge",
      "empirical_coverage_p10_p90": 0.9714285714285714,
      "evaluation_scope": "validation",
      "mean_interval_width_p10_p90": 6.031180565639438,
      "pinball_loss_p10": 0.04952380952380953,
      "pinball_loss_p50": 0.3153478849668511,
      "pinball_loss_p90": 0.7912189011068732,
      "position": "WR",
      "prediction_season": 2021,
      "projection_tier": "lower",
      "rows": 105,
      "target_name": "games_active"
    },
    {
      "candidate_name": "ridge",
      "empirical_coverage_p10_p90": 0.7953488372093023,
      "evaluation_scope": "validation",
      "mean_interval_width_p10_p90": 9.165987255274445,
      "pinball_loss_p10": 0.5662513467956657,
      "pinball_loss_p50": 1.5779237283495355,
      "pinball_loss_p90": 0.8323301098329119,
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
      "mean_interval_width_p10_p90": 10.524864613291284,
      "pinball_loss_p10": 1.1788693801438161,
      "pinball_loss_p50": 2.0614619245467267,
      "pinball_loss_p90": 0.5205535245584081,
      "position": "WR",
      "prediction_season": 2022,
      "projection_tier": "top",
      "rows": 108,
      "target_name": "games_active"
    },
    {
      "candidate_name": "ridge",
      "empirical_coverage_p10_p90": 0.7069767441860465,
      "evaluation_scope": "validation",
      "mean_interval_width_p10_p90": 10.018425408657166,
      "pinball_loss_p10": 0.5370706328679261,
      "pinball_loss_p50": 2.0537301021871177,
      "pinball_loss_p90": 1.1037646451568277,
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
      "mean_interval_width_p10_p90": 6.081567090385621,
      "pinball_loss_p10": 0.0065420560747663555,
      "pinball_loss_p50": 0.13380694737405138,
      "pinball_loss_p90": 0.6016146529637956,
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
      "mean_interval_width_p10_p90": 9.18409212057524,
      "pinball_loss_p10": 0.5589683643775304,
      "pinball_loss_p50": 1.5626661114366167,
      "pinball_loss_p90": 0.8118241761330632,
      "position": "WR",
      "prediction_season": 2023,
      "projection_tier": "all",
      "rows": 417,
      "target_name": "games_active"
    },
    {
      "candidate_name": "ridge",
      "empirical_coverage_p10_p90": 0.8761904761904762,
      "evaluation_scope": "validation",
      "mean_interval_width_p10_p90": 10.532831893809732,
      "pinball_loss_p10": 0.9694272125368517,
      "pinball_loss_p50": 1.841400423258264,
      "pinball_loss_p90": 0.4062571351849772,
      "position": "WR",
      "prediction_season": 2023,
      "projection_tier": "top",
      "rows": 105,
      "target_name": "games_active"
    },
    {
      "candidate_name": "ridge",
      "empirical_coverage_p10_p90": 0.7211538461538461,
      "evaluation_scope": "validation",
      "mean_interval_width_p10_p90": 9.99498879297853,
      "pinball_loss_p10": 0.6182689934089456,
      "pinball_loss_p50": 2.099295257317104,
      "pinball_loss_p90": 1.1237948106229416,
      "position": "WR",
      "prediction_season": 2023,
      "projection_tier": "middle",
      "rows": 208,
      "target_name": "games_active"
    },
    {
      "candidate_name": "ridge",
      "empirical_coverage_p10_p90": 0.9903846153846154,
      "evaluation_scope": "validation",
      "mean_interval_width_p10_p90": 6.200590350868448,
      "pinball_loss_p10": 0.025961538461538463,
      "pinball_loss_p50": 0.20799337024032444,
      "pinball_loss_p90": 0.5973496311874323,
      "position": "WR",
      "prediction_season": 2023,
      "projection_tier": "lower",
      "rows": 104,
      "target_name": "games_active"
    },
    {
      "candidate_name": "ridge",
      "empirical_coverage_p10_p90": 0.8183962264150944,
      "evaluation_scope": "validation",
      "mean_interval_width_p10_p90": 8.844474431377478,
      "pinball_loss_p10": 0.5526311278321279,
      "pinball_loss_p50": 1.4682367400686818,
      "pinball_loss_p90": 0.7784747197139217,
      "position": "WR",
      "prediction_season": 2024,
      "projection_tier": "all",
      "rows": 424,
      "target_name": "games_active"
    },
    {
      "candidate_name": "ridge",
      "empirical_coverage_p10_p90": 0.839622641509434,
      "evaluation_scope": "validation",
      "mean_interval_width_p10_p90": 9.89660662213684,
      "pinball_loss_p10": 1.0884774956807024,
      "pinball_loss_p50": 1.8845708305290922,
      "pinball_loss_p90": 0.4727424249459545,
      "position": "WR",
      "prediction_season": 2024,
      "projection_tier": "top",
      "rows": 106,
      "target_name": "games_active"
    },
    {
      "candidate_name": "ridge",
      "empirical_coverage_p10_p90": 0.7169811320754716,
      "evaluation_scope": "validation",
      "mean_interval_width_p10_p90": 9.662467034421573,
      "pinball_loss_p10": 0.555363130465414,
      "pinball_loss_p50": 1.922248095400335,
      "pinball_loss_p90": 1.0184207525868605,
      "position": "WR",
      "prediction_season": 2024,
      "projection_tier": "middle",
      "rows": 212,
      "target_name": "games_active"
    },
    {
      "candidate_name": "ridge",
      "empirical_coverage_p10_p90": 1.0,
      "evaluation_scope": "validation",
      "mean_interval_width_p10_p90": 6.156357034529926,
      "pinball_loss_p10": 0.011320754716981133,
      "pinball_loss_p50": 0.14387993894496443,
      "pinball_loss_p90": 0.6043149487360113,
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
      "absolute_importance": 1.7981146660215905,
      "coefficient": 1.7981146660215905,
      "direction": "positive",
      "feature": "numeric__lag1_fantasy_points_per_game",
      "rank": 1
    },
    {
      "absolute_importance": 1.7696397959406205,
      "coefficient": -1.7696397959406205,
      "direction": "negative",
      "feature": "categorical__previous_team_NYG",
      "rank": 2
    },
    {
      "absolute_importance": 1.534492476020923,
      "coefficient": 1.534492476020923,
      "direction": "positive",
      "feature": "categorical__previous_team_LA",
      "rank": 3
    },
    {
      "absolute_importance": 1.1669339783688883,
      "coefficient": 1.1669339783688883,
      "direction": "positive",
      "feature": "categorical__previous_team_CIN",
      "rank": 4
    },
    {
      "absolute_importance": 1.164904221384358,
      "coefficient": 1.164904221384358,
      "direction": "positive",
      "feature": "categorical__previous_team_NE",
      "rank": 5
    },
    {
      "absolute_importance": 1.1589068402902427,
      "coefficient": 1.1589068402902427,
      "direction": "positive",
      "feature": "numeric__weighted_3yr_interceptions_per_game",
      "rank": 6
    },
    {
      "absolute_importance": 1.114770817944013,
      "coefficient": 1.114770817944013,
      "direction": "positive",
      "feature": "categorical__previous_team_GB",
      "rank": 7
    },
    {
      "absolute_importance": 1.0822912447789974,
      "coefficient": 1.0822912447789974,
      "direction": "positive",
      "feature": "categorical__previous_team_DAL",
      "rank": 8
    },
    {
      "absolute_importance": 1.078151281329936,
      "coefficient": -1.078151281329936,
      "direction": "negative",
      "feature": "categorical__previous_team_NYJ",
      "rank": 9
    },
    {
      "absolute_importance": 1.0726084718671298,
      "coefficient": 1.0726084718671298,
      "direction": "positive",
      "feature": "categorical__previous_team_ATL",
      "rank": 10
    },
    {
      "absolute_importance": 1.011813141207502,
      "coefficient": -1.011813141207502,
      "direction": "negative",
      "feature": "numeric__lag1_fantasy_points_total",
      "rank": 11
    },
    {
      "absolute_importance": 1.011612803100217,
      "coefficient": -1.011612803100217,
      "direction": "negative",
      "feature": "numeric__weighted_3yr_passing_attempts_per_game",
      "rank": 12
    },
    {
      "absolute_importance": 0.9958707235422379,
      "coefficient": 0.9958707235422379,
      "direction": "positive",
      "feature": "categorical__previous_team_ARI",
      "rank": 13
    },
    {
      "absolute_importance": 0.9399573785532397,
      "coefficient": 0.9399573785532397,
      "direction": "positive",
      "feature": "numeric__lag1_stat_games",
      "rank": 14
    },
    {
      "absolute_importance": 0.9171704808948757,
      "coefficient": -0.9171704808948757,
      "direction": "negative",
      "feature": "categorical__previous_team_SD",
      "rank": 15
    },
    {
      "absolute_importance": 0.8858801929866886,
      "coefficient": -0.8858801929866886,
      "direction": "negative",
      "feature": "categorical__previous_team_SF",
      "rank": 16
    },
    {
      "absolute_importance": 0.8630846380471157,
      "coefficient": -0.8630846380471157,
      "direction": "negative",
      "feature": "categorical__previous_team_HOU",
      "rank": 17
    },
    {
      "absolute_importance": 0.8608353842839351,
      "coefficient": -0.8608353842839351,
      "direction": "negative",
      "feature": "categorical__previous_team_PHI",
      "rank": 18
    },
    {
      "absolute_importance": 0.8331800041158607,
      "coefficient": 0.8331800041158607,
      "direction": "positive",
      "feature": "numeric__lag1_games_active",
      "rank": 19
    },
    {
      "absolute_importance": 0.829168810671022,
      "coefficient": -0.829168810671022,
      "direction": "negative",
      "feature": "categorical__previous_team_NO",
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

- Project-relative path: `models/artifacts/phase4-7ae8e9aed04bffca00c0/attempt-866987f75a2c406693cf892d49adc975/WR/games_active/ridge.joblib`
- SHA-256: `1bb45fe2a96f61f01f5b60c98634244d57e7fb03f1c842f07cc27c36674c3c64`

## Additional metadata

````json
{
  "publication_id": "attempt-866987f75a2c406693cf892d49adc975"
}
````
