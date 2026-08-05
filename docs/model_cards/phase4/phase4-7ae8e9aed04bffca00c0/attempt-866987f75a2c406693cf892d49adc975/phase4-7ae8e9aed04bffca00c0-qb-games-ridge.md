# Model Card: phase4-7ae8e9aed04bffca00c0-qb-games-ridge

- Model ID: `phase4-7ae8e9aed04bffca00c0-qb-games-ridge`
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
  "position": "QB",
  "target_name": "games_active",
  "test_mae": 2.3013753926040037,
  "test_rows": 124,
  "test_season": 2025,
  "validation_mae": 2.4652391334952553,
  "validation_rows": 618,
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
    "candidate_mae": 2.4652391334952553,
    "ci95_lower": -1.899658718397371,
    "ci95_upper": -1.3580031455871684,
    "direction": "candidate_lower_mae",
    "mae_difference_candidate_minus_reference": -1.6253974299508505,
    "n_resamples": 2000,
    "reference_mae": 4.090636563446106,
    "rows": 618,
    "seed": 42
  },
  "decision_status": "learned_significant_improvement_selected",
  "learned_improvement_status": "statistically_clear",
  "reference_metrics": {
    "candidate_name": "age_position_adjusted",
    "candidate_source": "baseline",
    "position": "QB",
    "target_name": "games_active",
    "test_mae": 4.063549748196543,
    "test_rows": 124,
    "test_season": 2025,
    "validation_mae": 4.090636563446106,
    "validation_rows": 618,
    "validation_seasons": [
      2020,
      2021,
      2022,
      2023,
      2024
    ]
  },
  "selected_champion": "ridge",
  "selected_source": "learned",
  "selection_rule": "A learned candidate must lower pooled validation MAE and its paired bootstrap 95% interval for the MAE difference must remain below zero; otherwise the transparent baseline is retained.",
  "this_candidate_selected": true
}
````

## Uncertainty estimates

````json
{
  "empirical_metrics_by_season": [
    {
      "candidate_name": "ridge",
      "empirical_coverage_p10_p90": 0.8145161290322581,
      "evaluation_scope": "test",
      "mean_interval_width_p10_p90": 6.738498452534926,
      "pinball_loss_p10": 0.47366535642495766,
      "pinball_loss_p50": 1.1506876963020019,
      "pinball_loss_p90": 0.6161644069224479,
      "position": "QB",
      "prediction_season": 2025,
      "projection_tier": "all",
      "rows": 124,
      "target_name": "games_active"
    },
    {
      "candidate_name": "ridge",
      "empirical_coverage_p10_p90": 0.5483870967741935,
      "evaluation_scope": "test",
      "mean_interval_width_p10_p90": 8.233854861620708,
      "pinball_loss_p10": 1.244909889618767,
      "pinball_loss_p50": 2.241707086218729,
      "pinball_loss_p90": 0.7348268343456812,
      "position": "QB",
      "prediction_season": 2025,
      "projection_tier": "top",
      "rows": 31,
      "target_name": "games_active"
    },
    {
      "candidate_name": "ridge",
      "empirical_coverage_p10_p90": 0.8548387096774194,
      "evaluation_scope": "test",
      "mean_interval_width_p10_p90": 7.36897895020381,
      "pinball_loss_p10": 0.3184241551373059,
      "pinball_loss_p50": 1.1437502817994127,
      "pinball_loss_p90": 0.6722579571697125,
      "position": "QB",
      "prediction_season": 2025,
      "projection_tier": "middle",
      "rows": 62,
      "target_name": "games_active"
    },
    {
      "candidate_name": "ridge",
      "empirical_coverage_p10_p90": 1.0,
      "evaluation_scope": "test",
      "mean_interval_width_p10_p90": 3.9821810481113706,
      "pinball_loss_p10": 0.012903225806451613,
      "pinball_loss_p50": 0.07354313539045357,
      "pinball_loss_p90": 0.38531487900468536,
      "position": "QB",
      "prediction_season": 2025,
      "projection_tier": "lower",
      "rows": 31,
      "target_name": "games_active"
    },
    {
      "candidate_name": "ridge",
      "empirical_coverage_p10_p90": 0.8151260504201681,
      "evaluation_scope": "validation",
      "mean_interval_width_p10_p90": 5.903933888899281,
      "pinball_loss_p10": 0.40390079390414246,
      "pinball_loss_p50": 1.1227121565615157,
      "pinball_loss_p90": 0.6281065015989108,
      "position": "QB",
      "prediction_season": 2020,
      "projection_tier": "all",
      "rows": 119,
      "target_name": "games_active"
    },
    {
      "candidate_name": "ridge",
      "empirical_coverage_p10_p90": 0.7,
      "evaluation_scope": "validation",
      "mean_interval_width_p10_p90": 8.824026319547093,
      "pinball_loss_p10": 1.0095991089235274,
      "pinball_loss_p50": 1.8383955898972673,
      "pinball_loss_p90": 0.5614752292544505,
      "position": "QB",
      "prediction_season": 2020,
      "projection_tier": "top",
      "rows": 30,
      "target_name": "games_active"
    },
    {
      "candidate_name": "ridge",
      "empirical_coverage_p10_p90": 0.7796610169491526,
      "evaluation_scope": "validation",
      "mean_interval_width_p10_p90": 5.815755810462882,
      "pinball_loss_p10": 0.28942747808283265,
      "pinball_loss_p50": 1.2703538802356331,
      "pinball_loss_p90": 0.8326888436458936,
      "position": "QB",
      "prediction_season": 2020,
      "projection_tier": "middle",
      "rows": 59,
      "target_name": "games_active"
    },
    {
      "candidate_name": "ridge",
      "empirical_coverage_p10_p90": 1.0,
      "evaluation_scope": "validation",
      "mean_interval_width_p10_p90": 3.157258345843057,
      "pinball_loss_p10": 0.02333333333333333,
      "pinball_loss_p50": 0.11666666666666667,
      "pinball_loss_p90": 0.2923925012509724,
      "position": "QB",
      "prediction_season": 2020,
      "projection_tier": "lower",
      "rows": 30,
      "target_name": "games_active"
    },
    {
      "candidate_name": "ridge",
      "empirical_coverage_p10_p90": 0.792,
      "evaluation_scope": "validation",
      "mean_interval_width_p10_p90": 6.430378430221334,
      "pinball_loss_p10": 0.5092731419962806,
      "pinball_loss_p50": 1.227001685634716,
      "pinball_loss_p90": 0.6195485001852563,
      "position": "QB",
      "prediction_season": 2021,
      "projection_tier": "all",
      "rows": 125,
      "target_name": "games_active"
    },
    {
      "candidate_name": "ridge",
      "empirical_coverage_p10_p90": 0.6451612903225806,
      "evaluation_scope": "validation",
      "mean_interval_width_p10_p90": 7.839990259654346,
      "pinball_loss_p10": 1.2389772652910183,
      "pinball_loss_p50": 1.8780963219474525,
      "pinball_loss_p90": 0.5381782947099558,
      "position": "QB",
      "prediction_season": 2021,
      "projection_tier": "top",
      "rows": 31,
      "target_name": "games_active"
    },
    {
      "candidate_name": "ridge",
      "empirical_coverage_p10_p90": 0.7936507936507936,
      "evaluation_scope": "validation",
      "mean_interval_width_p10_p90": 7.055229023378701,
      "pinball_loss_p10": 0.38017218294465877,
      "pinball_loss_p50": 1.37912662516202,
      "pinball_loss_p90": 0.7440429752771007,
      "position": "QB",
      "prediction_season": 2021,
      "projection_tier": "middle",
      "rows": 63,
      "target_name": "games_active"
    },
    {
      "candidate_name": "ridge",
      "empirical_coverage_p10_p90": 0.9354838709677419,
      "evaluation_scope": "validation",
      "mean_interval_width_p10_p90": 3.750908943726577,
      "pinball_loss_p10": 0.04193548387096775,
      "pinball_loss_p50": 0.266749914153587,
      "pinball_loss_p90": 0.44791380466745423,
      "position": "QB",
      "prediction_season": 2021,
      "projection_tier": "lower",
      "rows": 31,
      "target_name": "games_active"
    },
    {
      "candidate_name": "ridge",
      "empirical_coverage_p10_p90": 0.808,
      "evaluation_scope": "validation",
      "mean_interval_width_p10_p90": 6.5758467741292534,
      "pinball_loss_p10": 0.42742706170968103,
      "pinball_loss_p50": 1.2023988808850476,
      "pinball_loss_p90": 0.689181387663722,
      "position": "QB",
      "prediction_season": 2022,
      "projection_tier": "all",
      "rows": 125,
      "target_name": "games_active"
    },
    {
      "candidate_name": "ridge",
      "empirical_coverage_p10_p90": 0.6774193548387096,
      "evaluation_scope": "validation",
      "mean_interval_width_p10_p90": 7.970834723520559,
      "pinball_loss_p10": 0.9200128740763973,
      "pinball_loss_p50": 1.6206620260419395,
      "pinball_loss_p90": 0.6370344758704716,
      "position": "QB",
      "prediction_season": 2022,
      "projection_tier": "top",
      "rows": 31,
      "target_name": "games_active"
    },
    {
      "candidate_name": "ridge",
      "empirical_coverage_p10_p90": 0.7936507936507936,
      "evaluation_scope": "validation",
      "mean_interval_width_p10_p90": 7.123376733572627,
      "pinball_loss_p10": 0.37631720027526694,
      "pinball_loss_p50": 1.39362250604856,
      "pinball_loss_p90": 0.8172601461425991,
      "position": "QB",
      "prediction_season": 2022,
      "projection_tier": "middle",
      "rows": 63,
      "target_name": "games_active"
    },
    {
      "candidate_name": "ridge",
      "empirical_coverage_p10_p90": 0.967741935483871,
      "evaluation_scope": "validation",
      "mean_interval_width_p10_p90": 4.068136649094959,
      "pinball_loss_p10": 0.03870967741935485,
      "pinball_loss_p50": 0.3955199813635969,
      "pinball_loss_p90": 0.48103920964505975,
      "position": "QB",
      "prediction_season": 2022,
      "projection_tier": "lower",
      "rows": 31,
      "target_name": "games_active"
    },
    {
      "candidate_name": "ridge",
      "empirical_coverage_p10_p90": 0.782258064516129,
      "evaluation_scope": "validation",
      "mean_interval_width_p10_p90": 6.753401990842393,
      "pinball_loss_p10": 0.5007807106613625,
      "pinball_loss_p50": 1.3655466922311168,
      "pinball_loss_p90": 0.8104035634537881,
      "position": "QB",
      "prediction_season": 2023,
      "projection_tier": "all",
      "rows": 124,
      "target_name": "games_active"
    },
    {
      "candidate_name": "ridge",
      "empirical_coverage_p10_p90": 0.5161290322580645,
      "evaluation_scope": "validation",
      "mean_interval_width_p10_p90": 8.136457270888322,
      "pinball_loss_p10": 1.2272266674845522,
      "pinball_loss_p50": 2.0919499871516196,
      "pinball_loss_p90": 0.7237875308235047,
      "position": "QB",
      "prediction_season": 2023,
      "projection_tier": "top",
      "rows": 31,
      "target_name": "games_active"
    },
    {
      "candidate_name": "ridge",
      "empirical_coverage_p10_p90": 0.8225806451612904,
      "evaluation_scope": "validation",
      "mean_interval_width_p10_p90": 7.324927486225964,
      "pinball_loss_p10": 0.36214163596754595,
      "pinball_loss_p50": 1.5140600940109787,
      "pinball_loss_p90": 1.0384669686731682,
      "position": "QB",
      "prediction_season": 2023,
      "projection_tier": "middle",
      "rows": 62,
      "target_name": "games_active"
    },
    {
      "candidate_name": "ridge",
      "empirical_coverage_p10_p90": 0.967741935483871,
      "evaluation_scope": "validation",
      "mean_interval_width_p10_p90": 4.227295720029324,
      "pinball_loss_p10": 0.05161290322580645,
      "pinball_loss_p50": 0.34211659375088993,
      "pinball_loss_p90": 0.44089278564531015,
      "position": "QB",
      "prediction_season": 2023,
      "projection_tier": "lower",
      "rows": 31,
      "target_name": "games_active"
    },
    {
      "candidate_name": "ridge",
      "empirical_coverage_p10_p90": 0.8,
      "evaluation_scope": "validation",
      "mean_interval_width_p10_p90": 6.77558346233884,
      "pinball_loss_p10": 0.5045440120949001,
      "pinball_loss_p50": 1.2412262797406775,
      "pinball_loss_p90": 0.7217213901492086,
      "position": "QB",
      "prediction_season": 2024,
      "projection_tier": "all",
      "rows": 125,
      "target_name": "games_active"
    },
    {
      "candidate_name": "ridge",
      "empirical_coverage_p10_p90": 0.6451612903225806,
      "evaluation_scope": "validation",
      "mean_interval_width_p10_p90": 8.368517593424396,
      "pinball_loss_p10": 0.9944020799130838,
      "pinball_loss_p50": 1.824948276358605,
      "pinball_loss_p90": 0.6321713797386386,
      "position": "QB",
      "prediction_season": 2024,
      "projection_tier": "top",
      "rows": 31,
      "target_name": "games_active"
    },
    {
      "candidate_name": "ridge",
      "empirical_coverage_p10_p90": 0.7936507936507936,
      "evaluation_scope": "validation",
      "mean_interval_width_p10_p90": 7.320456543621419,
      "pinball_loss_p10": 0.4974847148342367,
      "pinball_loss_p50": 1.4901291855368775,
      "pinball_loss_p90": 0.904474093392034,
      "position": "QB",
      "prediction_season": 2024,
      "projection_tier": "middle",
      "rows": 63,
      "target_name": "games_active"
    },
    {
      "candidate_name": "ridge",
      "empirical_coverage_p10_p90": 0.967741935483871,
      "evaluation_scope": "validation",
      "mean_interval_width_p10_p90": 4.075326617679012,
      "pinball_loss_p10": 0.029032258064516134,
      "pinball_loss_p50": 0.1516693455369243,
      "pinball_loss_p90": 0.43987074558242384,
      "position": "QB",
      "prediction_season": 2024,
      "projection_tier": "lower",
      "rows": 31,
      "target_name": "games_active"
    }
  ],
  "empirical_not_guaranteed": true,
  "method": "training-only signed out-of-fold residual quantiles",
  "operational_center": "training_only_residual_adjusted_p50",
  "residual_rows": 373,
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
      "absolute_importance": 1.4642897094088074,
      "coefficient": -1.4642897094088074,
      "direction": "negative",
      "feature": "numeric__weighted_3yr_passing_attempts_per_game",
      "rank": 1
    },
    {
      "absolute_importance": 1.4401483743806185,
      "coefficient": 1.4401483743806185,
      "direction": "positive",
      "feature": "categorical__previous_team_NE",
      "rank": 2
    },
    {
      "absolute_importance": 1.4022968242258278,
      "coefficient": -1.4022968242258278,
      "direction": "negative",
      "feature": "categorical__previous_team_IND",
      "rank": 3
    },
    {
      "absolute_importance": 1.3603964550148762,
      "coefficient": 1.3603964550148762,
      "direction": "positive",
      "feature": "numeric__weighted_3yr_passing_yards_per_game",
      "rank": 4
    },
    {
      "absolute_importance": 1.3412038642042432,
      "coefficient": 1.3412038642042432,
      "direction": "positive",
      "feature": "categorical__previous_team_SD",
      "rank": 5
    },
    {
      "absolute_importance": 1.178762045948165,
      "coefficient": 1.178762045948165,
      "direction": "positive",
      "feature": "categorical__previous_team_LA",
      "rank": 6
    },
    {
      "absolute_importance": 1.1119391215431063,
      "coefficient": -1.1119391215431063,
      "direction": "negative",
      "feature": "categorical__previous_team_ARI",
      "rank": 7
    },
    {
      "absolute_importance": 1.077308748406833,
      "coefficient": -1.077308748406833,
      "direction": "negative",
      "feature": "categorical__previous_team_MIA",
      "rank": 8
    },
    {
      "absolute_importance": 0.9579499714168407,
      "coefficient": -0.9579499714168407,
      "direction": "negative",
      "feature": "categorical__previous_team_CLE",
      "rank": 9
    },
    {
      "absolute_importance": 0.9331981286804666,
      "coefficient": -0.9331981286804666,
      "direction": "negative",
      "feature": "numeric__age_at_cutoff",
      "rank": 10
    },
    {
      "absolute_importance": 0.9197901023245151,
      "coefficient": -0.9197901023245151,
      "direction": "negative",
      "feature": "categorical__previous_team_WAS",
      "rank": 11
    },
    {
      "absolute_importance": 0.9159567913654694,
      "coefficient": 0.9159567913654694,
      "direction": "positive",
      "feature": "categorical__previous_team_SEA",
      "rank": 12
    },
    {
      "absolute_importance": 0.8687696553095637,
      "coefficient": 0.8687696553095637,
      "direction": "positive",
      "feature": "numeric__lag1_fantasy_points_per_game",
      "rank": 13
    },
    {
      "absolute_importance": 0.8448818498884799,
      "coefficient": 0.8448818498884799,
      "direction": "positive",
      "feature": "categorical__previous_team_CAR",
      "rank": 14
    },
    {
      "absolute_importance": 0.8224981916813634,
      "coefficient": 0.8224981916813634,
      "direction": "positive",
      "feature": "numeric__lag1_games_active",
      "rank": 15
    },
    {
      "absolute_importance": 0.8071365737440478,
      "coefficient": -0.8071365737440478,
      "direction": "negative",
      "feature": "categorical__previous_team_SF",
      "rank": 16
    },
    {
      "absolute_importance": 0.8023626002713277,
      "coefficient": 0.8023626002713277,
      "direction": "positive",
      "feature": "numeric__weighted_3yr_fantasy_points_per_game",
      "rank": 17
    },
    {
      "absolute_importance": 0.7550147586679978,
      "coefficient": 0.7550147586679978,
      "direction": "positive",
      "feature": "numeric__weighted_3yr_games_active",
      "rank": 18
    },
    {
      "absolute_importance": 0.7528733626477545,
      "coefficient": 0.7528733626477545,
      "direction": "positive",
      "feature": "categorical__previous_team_PHI",
      "rank": 19
    },
    {
      "absolute_importance": 0.7305313163642073,
      "coefficient": -0.7305313163642073,
      "direction": "negative",
      "feature": "categorical__previous_team_HOU",
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

- Project-relative path: `models/artifacts/phase4-7ae8e9aed04bffca00c0/attempt-866987f75a2c406693cf892d49adc975/QB/games_active/ridge.joblib`
- SHA-256: `fcaf395770d7cadb92327ac97666640d1ca3deccb3a80b5a491ee2a635a3ae00`

## Additional metadata

````json
{
  "publication_id": "attempt-866987f75a2c406693cf892d49adc975"
}
````
