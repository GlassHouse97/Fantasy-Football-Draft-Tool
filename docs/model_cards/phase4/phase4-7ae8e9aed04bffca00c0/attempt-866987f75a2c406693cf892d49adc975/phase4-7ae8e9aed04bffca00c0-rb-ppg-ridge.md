# Model Card: phase4-7ae8e9aed04bffca00c0-rb-ppg-ridge

- Model ID: `phase4-7ae8e9aed04bffca00c0-rb-ppg-ridge`
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
  "position": "RB",
  "target_name": "fantasy_points_per_game",
  "test_mae": 2.271980195817473,
  "test_rows": 128,
  "test_season": 2025,
  "validation_mae": 2.6680663845043413,
  "validation_rows": 686,
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
    "candidate_mae": 2.664872762103432,
    "ci95_lower": -0.11208713957810204,
    "ci95_upper": 0.1635642681013548,
    "direction": "uncertain",
    "mae_difference_candidate_minus_reference": 0.027918866645626927,
    "n_resamples": 2000,
    "reference_mae": 2.636953895457805,
    "rows": 686,
    "seed": 42
  },
  "decision_status": "learned_regression_baseline_retained",
  "learned_improvement_status": "regression",
  "reference_metrics": {
    "candidate_name": "age_position_adjusted",
    "candidate_source": "baseline",
    "position": "RB",
    "target_name": "fantasy_points_per_game",
    "test_mae": 2.2700883877685754,
    "test_rows": 128,
    "test_season": 2025,
    "validation_mae": 2.636953895457805,
    "validation_rows": 686,
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
      "empirical_coverage_p10_p90": 0.84375,
      "evaluation_scope": "test",
      "mean_interval_width_p10_p90": 8.832321800353544,
      "pinball_loss_p10": 0.5094717724935888,
      "pinball_loss_p50": 1.1359900979087365,
      "pinball_loss_p90": 0.6587897788013265,
      "position": "RB",
      "prediction_season": 2025,
      "projection_tier": "all",
      "rows": 128,
      "target_name": "fantasy_points_per_game"
    },
    {
      "candidate_name": "ridge",
      "empirical_coverage_p10_p90": 0.7230769230769231,
      "evaluation_scope": "test",
      "mean_interval_width_p10_p90": 8.832321800353544,
      "pinball_loss_p10": 0.637600858299632,
      "pinball_loss_p50": 1.36613627596178,
      "pinball_loss_p90": 0.7289089343195841,
      "position": "RB",
      "prediction_season": 2025,
      "projection_tier": "top",
      "rows": 65,
      "target_name": "fantasy_points_per_game"
    },
    {
      "candidate_name": "ridge",
      "empirical_coverage_p10_p90": 0.9545454545454546,
      "evaluation_scope": "test",
      "mean_interval_width_p10_p90": 8.832321800353547,
      "pinball_loss_p10": 0.3380184065158996,
      "pinball_loss_p50": 1.036696428860389,
      "pinball_loss_p90": 0.6604572895029269,
      "position": "RB",
      "prediction_season": 2025,
      "projection_tier": "middle",
      "rows": 44,
      "target_name": "fantasy_points_per_game"
    },
    {
      "candidate_name": "ridge",
      "empirical_coverage_p10_p90": 1.0,
      "evaluation_scope": "test",
      "mean_interval_width_p10_p90": 8.832321800353547,
      "pinball_loss_p10": 0.4681853264738787,
      "pinball_loss_p50": 0.578591143418181,
      "pinball_loss_p90": 0.4150468535614758,
      "position": "RB",
      "prediction_season": 2025,
      "projection_tier": "lower",
      "rows": 19,
      "target_name": "fantasy_points_per_game"
    },
    {
      "candidate_name": "ridge",
      "empirical_coverage_p10_p90": 0.8321167883211679,
      "evaluation_scope": "validation",
      "mean_interval_width_p10_p90": 10.159124504236498,
      "pinball_loss_p10": 0.6617270173141294,
      "pinball_loss_p50": 1.3846903705094027,
      "pinball_loss_p90": 0.72281319543012,
      "position": "RB",
      "prediction_season": 2020,
      "projection_tier": "all",
      "rows": 137,
      "target_name": "fantasy_points_per_game"
    },
    {
      "candidate_name": "ridge",
      "empirical_coverage_p10_p90": 0.7142857142857143,
      "evaluation_scope": "validation",
      "mean_interval_width_p10_p90": 10.159124504236498,
      "pinball_loss_p10": 0.8352157047798214,
      "pinball_loss_p50": 1.8452080346014197,
      "pinball_loss_p90": 0.7845286040855742,
      "position": "RB",
      "prediction_season": 2020,
      "projection_tier": "top",
      "rows": 70,
      "target_name": "fantasy_points_per_game"
    },
    {
      "candidate_name": "ridge",
      "empirical_coverage_p10_p90": 0.9473684210526315,
      "evaluation_scope": "validation",
      "mean_interval_width_p10_p90": 10.159124504236498,
      "pinball_loss_p10": 0.4718895278737277,
      "pinball_loss_p50": 0.9549859080442072,
      "pinball_loss_p90": 0.6884750865323774,
      "position": "RB",
      "prediction_season": 2020,
      "projection_tier": "middle",
      "rows": 57,
      "target_name": "fantasy_points_per_game"
    },
    {
      "candidate_name": "ridge",
      "empirical_coverage_p10_p90": 1.0,
      "evaluation_scope": "validation",
      "mean_interval_width_p10_p90": 10.159124504236498,
      "pinball_loss_p10": 0.5293798948645762,
      "pinball_loss_p50": 0.6103821579168952,
      "pinball_loss_p90": 0.4865325555590735,
      "position": "RB",
      "prediction_season": 2020,
      "projection_tier": "lower",
      "rows": 10,
      "target_name": "fantasy_points_per_game"
    },
    {
      "candidate_name": "ridge",
      "empirical_coverage_p10_p90": 0.8389261744966443,
      "evaluation_scope": "validation",
      "mean_interval_width_p10_p90": 9.827084218024588,
      "pinball_loss_p10": 0.6205232983711341,
      "pinball_loss_p50": 1.40017611750788,
      "pinball_loss_p90": 0.7048187907989935,
      "position": "RB",
      "prediction_season": 2021,
      "projection_tier": "all",
      "rows": 149,
      "target_name": "fantasy_points_per_game"
    },
    {
      "candidate_name": "ridge",
      "empirical_coverage_p10_p90": 0.782608695652174,
      "evaluation_scope": "validation",
      "mean_interval_width_p10_p90": 9.827084218024584,
      "pinball_loss_p10": 0.6288636139125028,
      "pinball_loss_p50": 1.5928461828111253,
      "pinball_loss_p90": 0.7371078217841205,
      "position": "RB",
      "prediction_season": 2021,
      "projection_tier": "top",
      "rows": 69,
      "target_name": "fantasy_points_per_game"
    },
    {
      "candidate_name": "ridge",
      "empirical_coverage_p10_p90": 0.8888888888888888,
      "evaluation_scope": "validation",
      "mean_interval_width_p10_p90": 9.827084218024583,
      "pinball_loss_p10": 0.5896435390920797,
      "pinball_loss_p50": 1.174495012171693,
      "pinball_loss_p90": 0.662645848034343,
      "position": "RB",
      "prediction_season": 2021,
      "projection_tier": "middle",
      "rows": 63,
      "target_name": "fantasy_points_per_game"
    },
    {
      "candidate_name": "ridge",
      "empirical_coverage_p10_p90": 0.8823529411764706,
      "evaluation_scope": "validation",
      "mean_interval_width_p10_p90": 9.82708421802459,
      "pinball_loss_p10": 0.701108184384428,
      "pinball_loss_p50": 1.4545099486994006,
      "pinball_loss_p90": 0.7300512764577708,
      "position": "RB",
      "prediction_season": 2021,
      "projection_tier": "lower",
      "rows": 17,
      "target_name": "fantasy_points_per_game"
    },
    {
      "candidate_name": "ridge",
      "empirical_coverage_p10_p90": 0.8201438848920863,
      "evaluation_scope": "validation",
      "mean_interval_width_p10_p90": 9.21648120440954,
      "pinball_loss_p10": 0.5441790587166149,
      "pinball_loss_p50": 1.2589041015268745,
      "pinball_loss_p90": 0.6916474035059471,
      "position": "RB",
      "prediction_season": 2022,
      "projection_tier": "all",
      "rows": 139,
      "target_name": "fantasy_points_per_game"
    },
    {
      "candidate_name": "ridge",
      "empirical_coverage_p10_p90": 0.6911764705882353,
      "evaluation_scope": "validation",
      "mean_interval_width_p10_p90": 9.21648120440954,
      "pinball_loss_p10": 0.6803931168476103,
      "pinball_loss_p50": 1.671572195642497,
      "pinball_loss_p90": 0.7606807815184337,
      "position": "RB",
      "prediction_season": 2022,
      "projection_tier": "top",
      "rows": 68,
      "target_name": "fantasy_points_per_game"
    },
    {
      "candidate_name": "ridge",
      "empirical_coverage_p10_p90": 0.9272727272727272,
      "evaluation_scope": "validation",
      "mean_interval_width_p10_p90": 9.216481204409542,
      "pinball_loss_p10": 0.3956940844372921,
      "pinball_loss_p50": 0.9870962973934848,
      "pinball_loss_p90": 0.6777692470716146,
      "position": "RB",
      "prediction_season": 2022,
      "projection_tier": "middle",
      "rows": 55,
      "target_name": "fantasy_points_per_game"
    },
    {
      "candidate_name": "ridge",
      "empirical_coverage_p10_p90": 1.0,
      "evaluation_scope": "validation",
      "mean_interval_width_p10_p90": 9.21648120440954,
      "pinball_loss_p10": 0.4756864107450568,
      "pinball_loss_p50": 0.43940402824400404,
      "pinball_loss_p90": 0.4459617096958971,
      "position": "RB",
      "prediction_season": 2022,
      "projection_tier": "lower",
      "rows": 16,
      "target_name": "fantasy_points_per_game"
    },
    {
      "candidate_name": "ridge",
      "empirical_coverage_p10_p90": 0.8283582089552238,
      "evaluation_scope": "validation",
      "mean_interval_width_p10_p90": 9.135742873548866,
      "pinball_loss_p10": 0.5912453526491279,
      "pinball_loss_p50": 1.3319349602332242,
      "pinball_loss_p90": 0.7579301143677615,
      "position": "RB",
      "prediction_season": 2023,
      "projection_tier": "all",
      "rows": 134,
      "target_name": "fantasy_points_per_game"
    },
    {
      "candidate_name": "ridge",
      "empirical_coverage_p10_p90": 0.6923076923076923,
      "evaluation_scope": "validation",
      "mean_interval_width_p10_p90": 9.135742873548864,
      "pinball_loss_p10": 0.7518116467442111,
      "pinball_loss_p50": 1.7513156655332875,
      "pinball_loss_p90": 0.7538199379316891,
      "position": "RB",
      "prediction_season": 2023,
      "projection_tier": "top",
      "rows": 65,
      "target_name": "fantasy_points_per_game"
    },
    {
      "candidate_name": "ridge",
      "empirical_coverage_p10_p90": 0.9433962264150944,
      "evaluation_scope": "validation",
      "mean_interval_width_p10_p90": 9.135742873548862,
      "pinball_loss_p10": 0.42507087042491587,
      "pinball_loss_p50": 1.064221006587444,
      "pinball_loss_p90": 0.863726695210018,
      "position": "RB",
      "prediction_season": 2023,
      "projection_tier": "middle",
      "rows": 53,
      "target_name": "fantasy_points_per_game"
    },
    {
      "candidate_name": "ridge",
      "empirical_coverage_p10_p90": 1.0,
      "evaluation_scope": "validation",
      "mean_interval_width_p10_p90": 9.135742873548864,
      "pinball_loss_p10": 0.48939775525555473,
      "pinball_loss_p50": 0.5150033164033637,
      "pinball_loss_p90": 0.42417653209933154,
      "position": "RB",
      "prediction_season": 2023,
      "projection_tier": "lower",
      "rows": 16,
      "target_name": "fantasy_points_per_game"
    },
    {
      "candidate_name": "ridge",
      "empirical_coverage_p10_p90": 0.8188976377952756,
      "evaluation_scope": "validation",
      "mean_interval_width_p10_p90": 8.975163285863495,
      "pinball_loss_p10": 0.5567055517710714,
      "pinball_loss_p50": 1.2862282900239315,
      "pinball_loss_p90": 0.6971402034609655,
      "position": "RB",
      "prediction_season": 2024,
      "projection_tier": "all",
      "rows": 127,
      "target_name": "fantasy_points_per_game"
    },
    {
      "candidate_name": "ridge",
      "empirical_coverage_p10_p90": 0.696969696969697,
      "evaluation_scope": "validation",
      "mean_interval_width_p10_p90": 8.97516328586349,
      "pinball_loss_p10": 0.6399862082238813,
      "pinball_loss_p50": 1.6506096751017154,
      "pinball_loss_p90": 0.8007709391999694,
      "position": "RB",
      "prediction_season": 2024,
      "projection_tier": "top",
      "rows": 66,
      "target_name": "fantasy_points_per_game"
    },
    {
      "candidate_name": "ridge",
      "empirical_coverage_p10_p90": 0.9375,
      "evaluation_scope": "validation",
      "mean_interval_width_p10_p90": 8.97516328586349,
      "pinball_loss_p10": 0.44861662513517625,
      "pinball_loss_p50": 0.9399727047591475,
      "pinball_loss_p90": 0.6447318522163245,
      "position": "RB",
      "prediction_season": 2024,
      "projection_tier": "middle",
      "rows": 48,
      "target_name": "fantasy_points_per_game"
    },
    {
      "candidate_name": "ridge",
      "empirical_coverage_p10_p90": 1.0,
      "evaluation_scope": "validation",
      "mean_interval_width_p10_p90": 8.97516328586349,
      "pinball_loss_p10": 0.5329936404354965,
      "pinball_loss_p50": 0.7147741882989955,
      "pinball_loss_p90": 0.3645226881508527,
      "position": "RB",
      "prediction_season": 2024,
      "projection_tier": "lower",
      "rows": 13,
      "target_name": "fantasy_points_per_game"
    }
  ],
  "empirical_not_guaranteed": true,
  "method": "training-only signed out-of-fold residual quantiles",
  "operational_center": "training_only_residual_adjusted_p50",
  "residual_rows": 389,
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
      "absolute_importance": 1.8351268376445038,
      "coefficient": 1.8351268376445038,
      "direction": "positive",
      "feature": "numeric__weighted_3yr_rushing_yards_per_game",
      "rank": 1
    },
    {
      "absolute_importance": 1.615701001018966,
      "coefficient": 1.615701001018966,
      "direction": "positive",
      "feature": "numeric__lag1_fantasy_points_total",
      "rank": 2
    },
    {
      "absolute_importance": 1.3454702537236833,
      "coefficient": -1.3454702537236833,
      "direction": "negative",
      "feature": "categorical__previous_team_NYJ",
      "rank": 3
    },
    {
      "absolute_importance": 0.8734774612142377,
      "coefficient": 0.8734774612142377,
      "direction": "positive",
      "feature": "numeric__weighted_3yr_fantasy_points_per_game",
      "rank": 4
    },
    {
      "absolute_importance": 0.825566282048469,
      "coefficient": -0.825566282048469,
      "direction": "negative",
      "feature": "numeric__weighted_3yr_carries_per_game",
      "rank": 5
    },
    {
      "absolute_importance": 0.7774737439967265,
      "coefficient": 0.7774737439967265,
      "direction": "positive",
      "feature": "categorical__previous_team_ARI",
      "rank": 6
    },
    {
      "absolute_importance": 0.740665207561108,
      "coefficient": 0.740665207561108,
      "direction": "positive",
      "feature": "categorical__previous_team_CAR",
      "rank": 7
    },
    {
      "absolute_importance": 0.729652599362691,
      "coefficient": -0.729652599362691,
      "direction": "negative",
      "feature": "categorical__previous_team_HOU",
      "rank": 8
    },
    {
      "absolute_importance": 0.7054573942452506,
      "coefficient": 0.7054573942452506,
      "direction": "positive",
      "feature": "categorical__previous_team_LA",
      "rank": 9
    },
    {
      "absolute_importance": 0.6748250414995458,
      "coefficient": 0.6748250414995458,
      "direction": "positive",
      "feature": "categorical__previous_team_GB",
      "rank": 10
    },
    {
      "absolute_importance": 0.6616393611250473,
      "coefficient": -0.6616393611250473,
      "direction": "negative",
      "feature": "categorical__previous_team_WAS",
      "rank": 11
    },
    {
      "absolute_importance": 0.6430312474105948,
      "coefficient": 0.6430312474105948,
      "direction": "positive",
      "feature": "categorical__previous_team_CIN",
      "rank": 12
    },
    {
      "absolute_importance": 0.6388172155744446,
      "coefficient": -0.6388172155744446,
      "direction": "negative",
      "feature": "categorical__previous_team_STL",
      "rank": 13
    },
    {
      "absolute_importance": 0.6306452366484859,
      "coefficient": -0.6306452366484859,
      "direction": "negative",
      "feature": "categorical__previous_team_DEN",
      "rank": 14
    },
    {
      "absolute_importance": 0.5796895589985829,
      "coefficient": -0.5796895589985829,
      "direction": "negative",
      "feature": "numeric__age_at_cutoff",
      "rank": 15
    },
    {
      "absolute_importance": 0.5275012374071936,
      "coefficient": -0.5275012374071936,
      "direction": "negative",
      "feature": "numeric__lag1_games_active",
      "rank": 16
    },
    {
      "absolute_importance": 0.5062993704054198,
      "coefficient": 0.5062993704054198,
      "direction": "positive",
      "feature": "categorical__previous_team_LAC",
      "rank": 17
    },
    {
      "absolute_importance": 0.4599459571519161,
      "coefficient": -0.4599459571519161,
      "direction": "negative",
      "feature": "numeric__draft_round",
      "rank": 18
    },
    {
      "absolute_importance": 0.39501217886509715,
      "coefficient": -0.39501217886509715,
      "direction": "negative",
      "feature": "categorical__previous_team_DET",
      "rank": 19
    },
    {
      "absolute_importance": 0.3914682524282667,
      "coefficient": -0.3914682524282667,
      "direction": "negative",
      "feature": "categorical__previous_team_JAX",
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

- Project-relative path: `models/artifacts/phase4-7ae8e9aed04bffca00c0/attempt-866987f75a2c406693cf892d49adc975/RB/fantasy_points_per_game/ridge.joblib`
- SHA-256: `dfbfe399c802996cc29386b92aea55a88e46e2909f0db1db047eb8085f1f47b1`

## Additional metadata

````json
{
  "publication_id": "attempt-866987f75a2c406693cf892d49adc975"
}
````
