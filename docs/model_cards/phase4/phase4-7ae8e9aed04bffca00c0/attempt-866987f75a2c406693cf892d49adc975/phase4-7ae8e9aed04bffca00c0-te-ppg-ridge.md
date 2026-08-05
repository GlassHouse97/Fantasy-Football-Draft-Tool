# Model Card: phase4-7ae8e9aed04bffca00c0-te-ppg-ridge

- Model ID: `phase4-7ae8e9aed04bffca00c0-te-ppg-ridge`
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
  "position": "TE",
  "target_name": "fantasy_points_per_game",
  "test_mae": 1.7348182573965845,
  "test_rows": 122,
  "test_season": 2025,
  "validation_mae": 1.9443608838171238,
  "validation_rows": 565,
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
    "candidate_mae": 1.7689720600061385,
    "ci95_lower": -0.0885412541767426,
    "ci95_upper": 0.09438080776593463,
    "direction": "uncertain",
    "mae_difference_candidate_minus_reference": 0.000189659891028926,
    "n_resamples": 2000,
    "reference_mae": 1.7687824001151096,
    "rows": 565,
    "seed": 42
  },
  "decision_status": "learned_regression_baseline_retained",
  "learned_improvement_status": "regression",
  "reference_metrics": {
    "candidate_name": "age_position_adjusted",
    "candidate_source": "baseline",
    "position": "TE",
    "target_name": "fantasy_points_per_game",
    "test_mae": 1.6311634954600387,
    "test_rows": 122,
    "test_season": 2025,
    "validation_mae": 1.7687824001151096,
    "validation_rows": 565,
    "validation_seasons": [
      2020,
      2021,
      2022,
      2023,
      2024
    ]
  },
  "selected_champion": "age_position_adjusted",
  "selected_source": "baseline",
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
      "empirical_coverage_p10_p90": 0.7704918032786885,
      "evaluation_scope": "test",
      "mean_interval_width_p10_p90": 4.992733765754863,
      "pinball_loss_p10": 0.4133283274854506,
      "pinball_loss_p50": 0.8674091286982922,
      "pinball_loss_p90": 0.5452930977958205,
      "position": "TE",
      "prediction_season": 2025,
      "projection_tier": "all",
      "rows": 122,
      "target_name": "fantasy_points_per_game"
    },
    {
      "candidate_name": "ridge",
      "empirical_coverage_p10_p90": 0.5636363636363636,
      "evaluation_scope": "test",
      "mean_interval_width_p10_p90": 4.992733765754861,
      "pinball_loss_p10": 0.5517689253814092,
      "pinball_loss_p50": 1.2403524967965036,
      "pinball_loss_p90": 0.7430337888399068,
      "position": "TE",
      "prediction_season": 2025,
      "projection_tier": "top",
      "rows": 55,
      "target_name": "fantasy_points_per_game"
    },
    {
      "candidate_name": "ridge",
      "empirical_coverage_p10_p90": 0.9423076923076923,
      "evaluation_scope": "test",
      "mean_interval_width_p10_p90": 4.992733765754862,
      "pinball_loss_p10": 0.28433261222628275,
      "pinball_loss_p50": 0.5332967909943558,
      "pinball_loss_p90": 0.44516393613175076,
      "position": "TE",
      "prediction_season": 2025,
      "projection_tier": "middle",
      "rows": 52,
      "target_name": "fantasy_points_per_game"
    },
    {
      "candidate_name": "ridge",
      "empirical_coverage_p10_p90": 0.9333333333333333,
      "evaluation_scope": "test",
      "mean_interval_width_p10_p90": 4.9927337657548625,
      "pinball_loss_p10": 0.35289794809871816,
      "pinball_loss_p50": 0.6582062163784986,
      "pinball_loss_p90": 0.16735832440294673,
      "position": "TE",
      "prediction_season": 2025,
      "projection_tier": "lower",
      "rows": 15,
      "target_name": "fantasy_points_per_game"
    },
    {
      "candidate_name": "ridge",
      "empirical_coverage_p10_p90": 0.7387387387387387,
      "evaluation_scope": "validation",
      "mean_interval_width_p10_p90": 6.345530476271847,
      "pinball_loss_p10": 0.5474483414026593,
      "pinball_loss_p50": 1.347196447532311,
      "pinball_loss_p90": 0.6654961470355313,
      "position": "TE",
      "prediction_season": 2020,
      "projection_tier": "all",
      "rows": 111,
      "target_name": "fantasy_points_per_game"
    },
    {
      "candidate_name": "ridge",
      "empirical_coverage_p10_p90": 0.6521739130434783,
      "evaluation_scope": "validation",
      "mean_interval_width_p10_p90": 6.345530476271847,
      "pinball_loss_p10": 0.6264466472620479,
      "pinball_loss_p50": 1.5028223420942672,
      "pinball_loss_p90": 0.7408553415496903,
      "position": "TE",
      "prediction_season": 2020,
      "projection_tier": "top",
      "rows": 46,
      "target_name": "fantasy_points_per_game"
    },
    {
      "candidate_name": "ridge",
      "empirical_coverage_p10_p90": 0.7692307692307693,
      "evaluation_scope": "validation",
      "mean_interval_width_p10_p90": 6.345530476271847,
      "pinball_loss_p10": 0.493654393871331,
      "pinball_loss_p50": 1.2760506429221066,
      "pinball_loss_p90": 0.7186230611840764,
      "position": "TE",
      "prediction_season": 2020,
      "projection_tier": "middle",
      "rows": 52,
      "target_name": "fantasy_points_per_game"
    },
    {
      "candidate_name": "ridge",
      "empirical_coverage_p10_p90": 0.9230769230769231,
      "evaluation_scope": "validation",
      "mean_interval_width_p10_p90": 6.345530476271847,
      "pinball_loss_p10": 0.4830916646409054,
      "pinball_loss_p50": 1.0811034236769739,
      "pinball_loss_p90": 0.18633287908355856,
      "position": "TE",
      "prediction_season": 2020,
      "projection_tier": "lower",
      "rows": 13,
      "target_name": "fantasy_points_per_game"
    },
    {
      "candidate_name": "ridge",
      "empirical_coverage_p10_p90": 0.8050847457627118,
      "evaluation_scope": "validation",
      "mean_interval_width_p10_p90": 6.608664854060017,
      "pinball_loss_p10": 0.41739779147012895,
      "pinball_loss_p50": 0.9100217213733549,
      "pinball_loss_p90": 0.5165541548322041,
      "position": "TE",
      "prediction_season": 2021,
      "projection_tier": "all",
      "rows": 118,
      "target_name": "fantasy_points_per_game"
    },
    {
      "candidate_name": "ridge",
      "empirical_coverage_p10_p90": 0.6538461538461539,
      "evaluation_scope": "validation",
      "mean_interval_width_p10_p90": 6.608664854060014,
      "pinball_loss_p10": 0.5931510147117729,
      "pinball_loss_p50": 1.2320699490379154,
      "pinball_loss_p90": 0.6071196623688867,
      "position": "TE",
      "prediction_season": 2021,
      "projection_tier": "top",
      "rows": 52,
      "target_name": "fantasy_points_per_game"
    },
    {
      "candidate_name": "ridge",
      "empirical_coverage_p10_p90": 0.9,
      "evaluation_scope": "validation",
      "mean_interval_width_p10_p90": 6.608664854060014,
      "pinball_loss_p10": 0.27269183389123414,
      "pinball_loss_p50": 0.7802696200319567,
      "pinball_loss_p90": 0.47167597988846494,
      "position": "TE",
      "prediction_season": 2021,
      "projection_tier": "middle",
      "rows": 50,
      "target_name": "fantasy_points_per_game"
    },
    {
      "candidate_name": "ridge",
      "empirical_coverage_p10_p90": 1.0,
      "evaluation_scope": "validation",
      "mean_interval_width_p10_p90": 6.608664854060015,
      "pinball_loss_p10": 0.2984059333688316,
      "pinball_loss_p50": 0.2688402981554042,
      "pinball_loss_p90": 0.36246055203716976,
      "position": "TE",
      "prediction_season": 2021,
      "projection_tier": "lower",
      "rows": 16,
      "target_name": "fantasy_points_per_game"
    },
    {
      "candidate_name": "ridge",
      "empirical_coverage_p10_p90": 0.8727272727272727,
      "evaluation_scope": "validation",
      "mean_interval_width_p10_p90": 6.600830984079338,
      "pinball_loss_p10": 0.4874760370188199,
      "pinball_loss_p50": 0.948445421051548,
      "pinball_loss_p90": 0.4700557153642139,
      "position": "TE",
      "prediction_season": 2022,
      "projection_tier": "all",
      "rows": 110,
      "target_name": "fantasy_points_per_game"
    },
    {
      "candidate_name": "ridge",
      "empirical_coverage_p10_p90": 0.7450980392156863,
      "evaluation_scope": "validation",
      "mean_interval_width_p10_p90": 6.600830984079335,
      "pinball_loss_p10": 0.7687931317347133,
      "pinball_loss_p50": 1.2490242728361498,
      "pinball_loss_p90": 0.4988653802562244,
      "position": "TE",
      "prediction_season": 2022,
      "projection_tier": "top",
      "rows": 51,
      "target_name": "fantasy_points_per_game"
    },
    {
      "candidate_name": "ridge",
      "empirical_coverage_p10_p90": 0.9772727272727273,
      "evaluation_scope": "validation",
      "mean_interval_width_p10_p90": 6.600830984079334,
      "pinball_loss_p10": 0.21534708893975793,
      "pinball_loss_p50": 0.7549102745316415,
      "pinball_loss_p90": 0.48412250593471734,
      "position": "TE",
      "prediction_season": 2022,
      "projection_tier": "middle",
      "rows": 44,
      "target_name": "fantasy_points_per_game"
    },
    {
      "candidate_name": "ridge",
      "empirical_coverage_p10_p90": 1.0,
      "evaluation_scope": "validation",
      "mean_interval_width_p10_p90": 6.6008309840793356,
      "pinball_loss_p10": 0.3292428293500315,
      "pinball_loss_p50": 0.49418042144229385,
      "pinball_loss_p90": 0.33084026905790187,
      "position": "TE",
      "prediction_season": 2022,
      "projection_tier": "lower",
      "rows": 15,
      "target_name": "fantasy_points_per_game"
    },
    {
      "candidate_name": "ridge",
      "empirical_coverage_p10_p90": 0.8303571428571429,
      "evaluation_scope": "validation",
      "mean_interval_width_p10_p90": 6.189862153323423,
      "pinball_loss_p10": 0.3603616681318923,
      "pinball_loss_p50": 0.8484364644448055,
      "pinball_loss_p90": 0.486539152226064,
      "position": "TE",
      "prediction_season": 2023,
      "projection_tier": "all",
      "rows": 112,
      "target_name": "fantasy_points_per_game"
    },
    {
      "candidate_name": "ridge",
      "empirical_coverage_p10_p90": 0.6923076923076923,
      "evaluation_scope": "validation",
      "mean_interval_width_p10_p90": 6.189862153323423,
      "pinball_loss_p10": 0.49716656729223724,
      "pinball_loss_p50": 1.1575583481813372,
      "pinball_loss_p90": 0.5431399439932245,
      "position": "TE",
      "prediction_season": 2023,
      "projection_tier": "top",
      "rows": 52,
      "target_name": "fantasy_points_per_game"
    },
    {
      "candidate_name": "ridge",
      "empirical_coverage_p10_p90": 0.9591836734693877,
      "evaluation_scope": "validation",
      "mean_interval_width_p10_p90": 6.189862153323424,
      "pinball_loss_p10": 0.20867379324381033,
      "pinball_loss_p50": 0.5849145288983252,
      "pinball_loss_p90": 0.42201015792131713,
      "position": "TE",
      "prediction_season": 2023,
      "projection_tier": "middle",
      "rows": 49,
      "target_name": "fantasy_points_per_game"
    },
    {
      "candidate_name": "ridge",
      "empirical_coverage_p10_p90": 0.9090909090909091,
      "evaluation_scope": "validation",
      "mean_interval_width_p10_p90": 6.189862153323423,
      "pinball_loss_p10": 0.38934813296626347,
      "pinball_loss_p50": 0.5610034542155232,
      "pinball_loss_p90": 0.5064191112297235,
      "position": "TE",
      "prediction_season": 2023,
      "projection_tier": "lower",
      "rows": 11,
      "target_name": "fantasy_points_per_game"
    },
    {
      "candidate_name": "ridge",
      "empirical_coverage_p10_p90": 0.8157894736842105,
      "evaluation_scope": "validation",
      "mean_interval_width_p10_p90": 5.2203229500736175,
      "pinball_loss_p10": 0.37441765803965676,
      "pinball_loss_p50": 0.8158482504097072,
      "pinball_loss_p90": 0.46379075226665584,
      "position": "TE",
      "prediction_season": 2024,
      "projection_tier": "all",
      "rows": 114,
      "target_name": "fantasy_points_per_game"
    },
    {
      "candidate_name": "ridge",
      "empirical_coverage_p10_p90": 0.6730769230769231,
      "evaluation_scope": "validation",
      "mean_interval_width_p10_p90": 5.2203229500736175,
      "pinball_loss_p10": 0.4745243576432374,
      "pinball_loss_p50": 1.209014968043433,
      "pinball_loss_p90": 0.7041133211607596,
      "position": "TE",
      "prediction_season": 2024,
      "projection_tier": "top",
      "rows": 52,
      "target_name": "fantasy_points_per_game"
    },
    {
      "candidate_name": "ridge",
      "empirical_coverage_p10_p90": 0.9230769230769231,
      "evaluation_scope": "validation",
      "mean_interval_width_p10_p90": 5.2203229500736175,
      "pinball_loss_p10": 0.2804003607537624,
      "pinball_loss_p50": 0.48167188078488327,
      "pinball_loss_p90": 0.27818188015081785,
      "position": "TE",
      "prediction_season": 2024,
      "projection_tier": "middle",
      "rows": 52,
      "target_name": "fantasy_points_per_game"
    },
    {
      "candidate_name": "ridge",
      "empirical_coverage_p10_p90": 1.0,
      "evaluation_scope": "validation",
      "mean_interval_width_p10_p90": 5.2203229500736175,
      "pinball_loss_p10": 0.3427527659876878,
      "pinball_loss_p50": 0.50909844076342,
      "pinball_loss_p90": 0.179279529019674,
      "position": "TE",
      "prediction_season": 2024,
      "projection_tier": "lower",
      "rows": 10,
      "target_name": "fantasy_points_per_game"
    }
  ],
  "empirical_not_guaranteed": true,
  "method": "training-only signed out-of-fold residual quantiles",
  "operational_center": "training_only_residual_adjusted_p50",
  "residual_rows": 348,
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
      "absolute_importance": 1.808531174572918,
      "coefficient": 1.808531174572918,
      "direction": "positive",
      "feature": "numeric__weighted_3yr_receiving_yards_per_game",
      "rank": 1
    },
    {
      "absolute_importance": 1.1833896358096962,
      "coefficient": 1.1833896358096962,
      "direction": "positive",
      "feature": "numeric__lag1_fantasy_points_total",
      "rank": 2
    },
    {
      "absolute_importance": 0.7329714414309897,
      "coefficient": -0.7329714414309897,
      "direction": "negative",
      "feature": "numeric__weighted_3yr_rushing_tds_per_game",
      "rank": 3
    },
    {
      "absolute_importance": 0.7308034501450917,
      "coefficient": -0.7308034501450917,
      "direction": "negative",
      "feature": "categorical__previous_team_NYJ",
      "rank": 4
    },
    {
      "absolute_importance": 0.6938572072610668,
      "coefficient": 0.6938572072610668,
      "direction": "positive",
      "feature": "numeric__weighted_3yr_fantasy_points_per_game",
      "rank": 5
    },
    {
      "absolute_importance": 0.6180529933703169,
      "coefficient": 0.6180529933703169,
      "direction": "positive",
      "feature": "numeric__weighted_3yr_rushing_yards_per_game",
      "rank": 6
    },
    {
      "absolute_importance": 0.6142336783016972,
      "coefficient": 0.6142336783016972,
      "direction": "positive",
      "feature": "categorical__previous_team_KC",
      "rank": 7
    },
    {
      "absolute_importance": 0.5379090364657985,
      "coefficient": 0.5379090364657985,
      "direction": "positive",
      "feature": "categorical__previous_team_NO",
      "rank": 8
    },
    {
      "absolute_importance": 0.47482171060574774,
      "coefficient": 0.47482171060574774,
      "direction": "positive",
      "feature": "categorical__previous_team_DET",
      "rank": 9
    },
    {
      "absolute_importance": 0.4586563833023753,
      "coefficient": 0.4586563833023753,
      "direction": "positive",
      "feature": "categorical__previous_team_LA",
      "rank": 10
    },
    {
      "absolute_importance": 0.44857104751669075,
      "coefficient": -0.44857104751669075,
      "direction": "negative",
      "feature": "categorical__previous_team_CAR",
      "rank": 11
    },
    {
      "absolute_importance": 0.43000712831772997,
      "coefficient": 0.43000712831772997,
      "direction": "positive",
      "feature": "numeric__weighted_3yr_carries_per_game",
      "rank": 12
    },
    {
      "absolute_importance": 0.4238560549129143,
      "coefficient": -0.4238560549129143,
      "direction": "negative",
      "feature": "categorical__previous_team_CHI",
      "rank": 13
    },
    {
      "absolute_importance": 0.41942948791692775,
      "coefficient": 0.41942948791692775,
      "direction": "positive",
      "feature": "categorical__previous_team_ARI",
      "rank": 14
    },
    {
      "absolute_importance": 0.4178081523910563,
      "coefficient": -0.4178081523910563,
      "direction": "negative",
      "feature": "numeric__weighted_3yr_passing_tds_per_game",
      "rank": 15
    },
    {
      "absolute_importance": 0.4093022176565884,
      "coefficient": -0.4093022176565884,
      "direction": "negative",
      "feature": "categorical__previous_team_PIT",
      "rank": 16
    },
    {
      "absolute_importance": 0.37967313914486234,
      "coefficient": 0.37967313914486234,
      "direction": "positive",
      "feature": "categorical__previous_team_DAL",
      "rank": 17
    },
    {
      "absolute_importance": 0.3689620928135471,
      "coefficient": -0.3689620928135471,
      "direction": "negative",
      "feature": "numeric__draft_pick",
      "rank": 18
    },
    {
      "absolute_importance": 0.36282900621859654,
      "coefficient": 0.36282900621859654,
      "direction": "positive",
      "feature": "numeric__weighted_3yr_passing_yards_per_game",
      "rank": 19
    },
    {
      "absolute_importance": 0.3603532130207114,
      "coefficient": -0.3603532130207114,
      "direction": "negative",
      "feature": "numeric__lag1_fantasy_points_per_game",
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

- Project-relative path: `models/artifacts/phase4-7ae8e9aed04bffca00c0/attempt-866987f75a2c406693cf892d49adc975/TE/fantasy_points_per_game/ridge.joblib`
- SHA-256: `4f9af8f15299d0698ce35fd7ced04cda78115739c5e1fa4ec1d2a650ba24191b`

## Additional metadata

````json
{
  "publication_id": "attempt-866987f75a2c406693cf892d49adc975"
}
````
