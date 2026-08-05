# Model Card: phase4-7ae8e9aed04bffca00c0-te-games-ridge

- Model ID: `phase4-7ae8e9aed04bffca00c0-te-games-ridge`
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
  "position": "TE",
  "target_name": "games_active",
  "test_mae": 2.874199214991195,
  "test_rows": 235,
  "test_season": 2025,
  "validation_mae": 3.6435709405526,
  "validation_rows": 1158,
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
    "candidate_mae": 3.252152007104269,
    "ci95_lower": -3.3900043141986305,
    "ci95_upper": -2.6881702109533583,
    "direction": "candidate_lower_mae",
    "mae_difference_candidate_minus_reference": -3.033460583473347,
    "n_resamples": 2000,
    "reference_mae": 6.285612590577616,
    "rows": 1158,
    "seed": 42
  },
  "decision_status": "learned_significant_improvement_selected",
  "learned_improvement_status": "statistically_clear",
  "reference_metrics": {
    "candidate_name": "age_position_adjusted",
    "candidate_source": "baseline",
    "position": "TE",
    "target_name": "games_active",
    "test_mae": 6.164744921388118,
    "test_rows": 235,
    "test_season": 2025,
    "validation_mae": 6.285612590577616,
    "validation_rows": 1158,
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
      "empirical_coverage_p10_p90": 0.8595744680851064,
      "evaluation_scope": "test",
      "mean_interval_width_p10_p90": 8.991162487144264,
      "pinball_loss_p10": 0.5299475215438627,
      "pinball_loss_p50": 1.4370996074955975,
      "pinball_loss_p90": 0.7405489950614117,
      "position": "TE",
      "prediction_season": 2025,
      "projection_tier": "all",
      "rows": 235,
      "target_name": "games_active"
    },
    {
      "candidate_name": "ridge",
      "empirical_coverage_p10_p90": 0.9152542372881356,
      "evaluation_scope": "test",
      "mean_interval_width_p10_p90": 10.251432968411528,
      "pinball_loss_p10": 0.8883894777822442,
      "pinball_loss_p50": 1.62007691615851,
      "pinball_loss_p90": 0.38783980887070146,
      "position": "TE",
      "prediction_season": 2025,
      "projection_tier": "top",
      "rows": 59,
      "target_name": "games_active"
    },
    {
      "candidate_name": "ridge",
      "empirical_coverage_p10_p90": 0.7606837606837606,
      "evaluation_scope": "test",
      "mean_interval_width_p10_p90": 9.990740705420434,
      "pinball_loss_p10": 0.6121597296893616,
      "pinball_loss_p50": 2.0118051853955157,
      "pinball_loss_p90": 1.0062330550018566,
      "position": "TE",
      "prediction_season": 2025,
      "projection_tier": "middle",
      "rows": 117,
      "target_name": "games_active"
    },
    {
      "candidate_name": "ridge",
      "empirical_coverage_p10_p90": 1.0,
      "evaluation_scope": "test",
      "mean_interval_width_p10_p90": 5.7486775730242625,
      "pinball_loss_p10": 0.00847457627118644,
      "pinball_loss_p50": 0.1144519155396267,
      "pinball_loss_p90": 0.5663931810312396,
      "position": "TE",
      "prediction_season": 2025,
      "projection_tier": "lower",
      "rows": 59,
      "target_name": "games_active"
    },
    {
      "candidate_name": "ridge",
      "empirical_coverage_p10_p90": 0.7946428571428571,
      "evaluation_scope": "validation",
      "mean_interval_width_p10_p90": 11.96323076481996,
      "pinball_loss_p10": 0.7984350167118562,
      "pinball_loss_p50": 2.517426370962015,
      "pinball_loss_p90": 0.9762594445964446,
      "position": "TE",
      "prediction_season": 2020,
      "projection_tier": "all",
      "rows": 224,
      "target_name": "games_active"
    },
    {
      "candidate_name": "ridge",
      "empirical_coverage_p10_p90": 0.875,
      "evaluation_scope": "validation",
      "mean_interval_width_p10_p90": 8.676613063362122,
      "pinball_loss_p10": 1.0569663720107918,
      "pinball_loss_p50": 1.636674062512382,
      "pinball_loss_p90": 0.45535714285714274,
      "position": "TE",
      "prediction_season": 2020,
      "projection_tier": "top",
      "rows": 56,
      "target_name": "games_active"
    },
    {
      "candidate_name": "ridge",
      "empirical_coverage_p10_p90": 0.6548672566371682,
      "evaluation_scope": "validation",
      "mean_interval_width_p10_p90": 13.6537402597338,
      "pinball_loss_p10": 1.0394630700075351,
      "pinball_loss_p50": 3.114906715141978,
      "pinball_loss_p90": 1.1529384473226219,
      "position": "TE",
      "prediction_season": 2020,
      "projection_tier": "middle",
      "rows": 113,
      "target_name": "games_active"
    },
    {
      "candidate_name": "ridge",
      "empirical_coverage_p10_p90": 1.0,
      "evaluation_scope": "validation",
      "mean_interval_width_p10_p90": 11.836376553117693,
      "pinball_loss_p10": 0.04,
      "pinball_loss_p50": 2.1866418324318992,
      "pinball_loss_p90": 1.143637655311769,
      "position": "TE",
      "prediction_season": 2020,
      "projection_tier": "lower",
      "rows": 55,
      "target_name": "games_active"
    },
    {
      "candidate_name": "ridge",
      "empirical_coverage_p10_p90": 0.8122270742358079,
      "evaluation_scope": "validation",
      "mean_interval_width_p10_p90": 10.08059989671118,
      "pinball_loss_p10": 0.5940900776175229,
      "pinball_loss_p50": 1.7510643281473723,
      "pinball_loss_p90": 0.9190023567875427,
      "position": "TE",
      "prediction_season": 2021,
      "projection_tier": "all",
      "rows": 229,
      "target_name": "games_active"
    },
    {
      "candidate_name": "ridge",
      "empirical_coverage_p10_p90": 0.8245614035087719,
      "evaluation_scope": "validation",
      "mean_interval_width_p10_p90": 13.565665547884857,
      "pinball_loss_p10": 1.1959459423276162,
      "pinball_loss_p50": 2.3859056722785525,
      "pinball_loss_p90": 0.5055865120569891,
      "position": "TE",
      "prediction_season": 2021,
      "projection_tier": "top",
      "rows": 57,
      "target_name": "games_active"
    },
    {
      "candidate_name": "ridge",
      "empirical_coverage_p10_p90": 0.7217391304347827,
      "evaluation_scope": "validation",
      "mean_interval_width_p10_p90": 10.442211715546994,
      "pinball_loss_p10": 0.5798061657542487,
      "pinball_loss_p50": 2.2521487637032243,
      "pinball_loss_p90": 1.1947573846447568,
      "position": "TE",
      "prediction_season": 2021,
      "projection_tier": "middle",
      "rows": 115,
      "target_name": "games_active"
    },
    {
      "candidate_name": "ridge",
      "empirical_coverage_p10_p90": 0.9824561403508771,
      "evaluation_scope": "validation",
      "mean_interval_width_p10_p90": 5.865966540868753,
      "pinball_loss_p10": 0.02105263157894737,
      "pinball_loss_p50": 0.10526315789473684,
      "pinball_loss_p90": 0.7760703382974016,
      "position": "TE",
      "prediction_season": 2021,
      "projection_tier": "lower",
      "rows": 57,
      "target_name": "games_active"
    },
    {
      "candidate_name": "ridge",
      "empirical_coverage_p10_p90": 0.7991452991452992,
      "evaluation_scope": "validation",
      "mean_interval_width_p10_p90": 9.904047995918381,
      "pinball_loss_p10": 0.5782605940856369,
      "pinball_loss_p50": 1.68364107112407,
      "pinball_loss_p90": 0.804136671019881,
      "position": "TE",
      "prediction_season": 2022,
      "projection_tier": "all",
      "rows": 234,
      "target_name": "games_active"
    },
    {
      "candidate_name": "ridge",
      "empirical_coverage_p10_p90": 0.847457627118644,
      "evaluation_scope": "validation",
      "mean_interval_width_p10_p90": 12.731371339653233,
      "pinball_loss_p10": 1.136849392056624,
      "pinball_loss_p50": 2.1655237486259806,
      "pinball_loss_p90": 0.43270324986343545,
      "position": "TE",
      "prediction_season": 2022,
      "projection_tier": "top",
      "rows": 59,
      "target_name": "games_active"
    },
    {
      "candidate_name": "ridge",
      "empirical_coverage_p10_p90": 0.6724137931034483,
      "evaluation_scope": "validation",
      "mean_interval_width_p10_p90": 10.772244445971634,
      "pinball_loss_p10": 0.5882660765922261,
      "pinball_loss_p50": 2.2948802540870648,
      "pinball_loss_p90": 1.1289387297365885,
      "position": "TE",
      "prediction_season": 2022,
      "projection_tier": "middle",
      "rows": 116,
      "target_name": "games_active"
    },
    {
      "candidate_name": "ridge",
      "empirical_coverage_p10_p90": 1.0,
      "evaluation_scope": "validation",
      "mean_interval_width_p10_p90": 5.369762140214437,
      "pinball_loss_p10": 0.0,
      "pinball_loss_p50": 0.0,
      "pinball_loss_p90": 0.5369762140214436,
      "position": "TE",
      "prediction_season": 2022,
      "projection_tier": "lower",
      "rows": 59,
      "target_name": "games_active"
    },
    {
      "candidate_name": "ridge",
      "empirical_coverage_p10_p90": 0.8340425531914893,
      "evaluation_scope": "validation",
      "mean_interval_width_p10_p90": 9.348284010464953,
      "pinball_loss_p10": 0.5675974803941626,
      "pinball_loss_p50": 1.5146863580361167,
      "pinball_loss_p90": 0.752863617163471,
      "position": "TE",
      "prediction_season": 2023,
      "projection_tier": "all",
      "rows": 235,
      "target_name": "games_active"
    },
    {
      "candidate_name": "ridge",
      "empirical_coverage_p10_p90": 0.8135593220338984,
      "evaluation_scope": "validation",
      "mean_interval_width_p10_p90": 12.576264807499728,
      "pinball_loss_p10": 1.2349391454904215,
      "pinball_loss_p50": 2.2180956012506416,
      "pinball_loss_p90": 0.4274518646200476,
      "position": "TE",
      "prediction_season": 2023,
      "projection_tier": "top",
      "rows": 59,
      "target_name": "games_active"
    },
    {
      "candidate_name": "ridge",
      "empirical_coverage_p10_p90": 0.7606837606837606,
      "evaluation_scope": "validation",
      "mean_interval_width_p10_p90": 9.698512071257143,
      "pinball_loss_p10": 0.5061880197324218,
      "pinball_loss_p50": 1.8682363561085433,
      "pinball_loss_p90": 1.0341125587424227,
      "position": "TE",
      "prediction_season": 2023,
      "projection_tier": "middle",
      "rows": 117,
      "target_name": "games_active"
    },
    {
      "candidate_name": "ridge",
      "empirical_coverage_p10_p90": 1.0,
      "evaluation_scope": "validation",
      "mean_interval_width_p10_p90": 5.4257831606727915,
      "pinball_loss_p10": 0.02203389830508475,
      "pinball_loss_p50": 0.11016949152542373,
      "pinball_loss_p90": 0.5205444177621944,
      "position": "TE",
      "prediction_season": 2023,
      "projection_tier": "lower",
      "rows": 59,
      "target_name": "games_active"
    },
    {
      "candidate_name": "ridge",
      "empirical_coverage_p10_p90": 0.8008474576271186,
      "evaluation_scope": "validation",
      "mean_interval_width_p10_p90": 8.956796424911506,
      "pinball_loss_p10": 0.6746320693201828,
      "pinball_loss_p50": 1.672911150666084,
      "pinball_loss_p90": 0.8383351040758228,
      "position": "TE",
      "prediction_season": 2024,
      "projection_tier": "all",
      "rows": 236,
      "target_name": "games_active"
    },
    {
      "candidate_name": "ridge",
      "empirical_coverage_p10_p90": 0.8813559322033898,
      "evaluation_scope": "validation",
      "mean_interval_width_p10_p90": 9.939953699267098,
      "pinball_loss_p10": 1.1802118791284197,
      "pinball_loss_p50": 2.0064353184896118,
      "pinball_loss_p90": 0.396906183576517,
      "position": "TE",
      "prediction_season": 2024,
      "projection_tier": "top",
      "rows": 59,
      "target_name": "games_active"
    },
    {
      "candidate_name": "ridge",
      "empirical_coverage_p10_p90": 0.6694915254237288,
      "evaluation_scope": "validation",
      "mean_interval_width_p10_p90": 9.868752068932135,
      "pinball_loss_p10": 0.7532259956863255,
      "pinball_loss_p50": 2.2423593145279277,
      "pinball_loss_p90": 1.174118497053205,
      "position": "TE",
      "prediction_season": 2024,
      "projection_tier": "middle",
      "rows": 118,
      "target_name": "games_active"
    },
    {
      "candidate_name": "ridge",
      "empirical_coverage_p10_p90": 0.9830508474576272,
      "evaluation_scope": "validation",
      "mean_interval_width_p10_p90": 6.1497278625146645,
      "pinball_loss_p10": 0.011864406779661017,
      "pinball_loss_p50": 0.2004906551188691,
      "pinball_loss_p90": 0.6081972386203635,
      "position": "TE",
      "prediction_season": 2024,
      "projection_tier": "lower",
      "rows": 59,
      "target_name": "games_active"
    }
  ],
  "empirical_not_guaranteed": true,
  "method": "training-only signed out-of-fold residual quantiles",
  "operational_center": "training_only_residual_adjusted_p50",
  "residual_rows": 706,
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
      "absolute_importance": 1.6574277430965263,
      "coefficient": 1.6574277430965263,
      "direction": "positive",
      "feature": "categorical__previous_team_SF",
      "rank": 1
    },
    {
      "absolute_importance": 1.6122460897138746,
      "coefficient": 1.6122460897138746,
      "direction": "positive",
      "feature": "numeric__weighted_3yr_receptions_per_game",
      "rank": 2
    },
    {
      "absolute_importance": 1.4010770481815478,
      "coefficient": -1.4010770481815478,
      "direction": "negative",
      "feature": "categorical__previous_team_NYG",
      "rank": 3
    },
    {
      "absolute_importance": 1.371027453026704,
      "coefficient": -1.371027453026704,
      "direction": "negative",
      "feature": "numeric__weighted_3yr_targets_per_game",
      "rank": 4
    },
    {
      "absolute_importance": 1.3167531921554083,
      "coefficient": -1.3167531921554083,
      "direction": "negative",
      "feature": "categorical__previous_team_NE",
      "rank": 5
    },
    {
      "absolute_importance": 1.3119712215737749,
      "coefficient": 1.3119712215737749,
      "direction": "positive",
      "feature": "categorical__previous_team_CAR",
      "rank": 6
    },
    {
      "absolute_importance": 1.303184005421523,
      "coefficient": 1.303184005421523,
      "direction": "positive",
      "feature": "numeric__lag1_stat_games",
      "rank": 7
    },
    {
      "absolute_importance": 1.2347513017115077,
      "coefficient": 1.2347513017115077,
      "direction": "positive",
      "feature": "categorical__previous_team_SD",
      "rank": 8
    },
    {
      "absolute_importance": 1.2327010607346016,
      "coefficient": -1.2327010607346016,
      "direction": "negative",
      "feature": "numeric__lag1_fantasy_points_total",
      "rank": 9
    },
    {
      "absolute_importance": 1.1755629344311385,
      "coefficient": 1.1755629344311385,
      "direction": "positive",
      "feature": "categorical__previous_team_KC",
      "rank": 10
    },
    {
      "absolute_importance": 1.1353636015983608,
      "coefficient": -1.1353636015983608,
      "direction": "negative",
      "feature": "categorical__previous_team_LV",
      "rank": 11
    },
    {
      "absolute_importance": 1.1272004093584922,
      "coefficient": 1.1272004093584922,
      "direction": "positive",
      "feature": "categorical__previous_team_GB",
      "rank": 12
    },
    {
      "absolute_importance": 1.1202956412307636,
      "coefficient": 1.1202956412307636,
      "direction": "positive",
      "feature": "categorical__previous_team_TEN",
      "rank": 13
    },
    {
      "absolute_importance": 1.1159942731631722,
      "coefficient": 1.1159942731631722,
      "direction": "positive",
      "feature": "numeric__lag1_games_active",
      "rank": 14
    },
    {
      "absolute_importance": 1.043339178513228,
      "coefficient": -1.043339178513228,
      "direction": "negative",
      "feature": "numeric__draft_round",
      "rank": 15
    },
    {
      "absolute_importance": 0.9671565031226519,
      "coefficient": 0.9671565031226519,
      "direction": "positive",
      "feature": "categorical__previous_team_LA",
      "rank": 16
    },
    {
      "absolute_importance": 0.9401784341385158,
      "coefficient": 0.9401784341385158,
      "direction": "positive",
      "feature": "numeric__lag1_fantasy_points_per_game",
      "rank": 17
    },
    {
      "absolute_importance": 0.9256500885370554,
      "coefficient": 0.9256500885370554,
      "direction": "positive",
      "feature": "categorical__previous_team_OAK",
      "rank": 18
    },
    {
      "absolute_importance": 0.8010530214556989,
      "coefficient": 0.8010530214556989,
      "direction": "positive",
      "feature": "numeric__draft_pick",
      "rank": 19
    },
    {
      "absolute_importance": 0.7305561003253158,
      "coefficient": -0.7305561003253158,
      "direction": "negative",
      "feature": "categorical__previous_team_WAS",
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

- Project-relative path: `models/artifacts/phase4-7ae8e9aed04bffca00c0/attempt-866987f75a2c406693cf892d49adc975/TE/games_active/ridge.joblib`
- SHA-256: `a3bb6e5d68f20ee741388aaabb6c6a282353b93596129545fa5794e877b5da98`

## Additional metadata

````json
{
  "publication_id": "attempt-866987f75a2c406693cf892d49adc975"
}
````
