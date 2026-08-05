# Model Card: phase4-7ae8e9aed04bffca00c0-qb-total-ridge

- Model ID: `phase4-7ae8e9aed04bffca00c0-qb-total-ridge`
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
  "position": "QB",
  "target_name": "fantasy_points_total",
  "test_mae": 43.39403342796977,
  "test_rows": 124,
  "test_season": 2025,
  "validation_mae": 45.5781669821033,
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
    "candidate_mae": 41.20860389333247,
    "ci95_lower": -13.815049499312021,
    "ci95_upper": -6.3656732283432875,
    "direction": "candidate_lower_mae",
    "mae_difference_candidate_minus_reference": -10.130237681520477,
    "n_resamples": 2000,
    "reference_mae": 51.33884157485295,
    "rows": 618,
    "seed": 42
  },
  "decision_status": "learned_significant_improvement_selected",
  "learned_improvement_status": "statistically_clear",
  "reference_metrics": {
    "candidate_name": "age_position_adjusted",
    "candidate_source": "baseline",
    "position": "QB",
    "target_name": "fantasy_points_total",
    "test_mae": 51.38160378623023,
    "test_rows": 124,
    "test_season": 2025,
    "validation_mae": 51.33884157485295,
    "validation_rows": 618,
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
      "empirical_coverage_p10_p90": 0.8225806451612904,
      "evaluation_scope": "test",
      "mean_interval_width_p10_p90": 144.4888919021263,
      "pinball_loss_p10": 11.709112381748833,
      "pinball_loss_p50": 21.697016713984883,
      "pinball_loss_p90": 12.661075879390493,
      "position": "QB",
      "prediction_season": 2025,
      "projection_tier": "all",
      "rows": 124,
      "target_name": "fantasy_points_total"
    },
    {
      "candidate_name": "ridge",
      "empirical_coverage_p10_p90": 0.5161290322580645,
      "evaluation_scope": "test",
      "mean_interval_width_p10_p90": 144.4888919021263,
      "pinball_loss_p10": 22.846028179758683,
      "pinball_loss_p50": 42.937360419994235,
      "pinball_loss_p90": 24.066138664979018,
      "position": "QB",
      "prediction_season": 2025,
      "projection_tier": "top",
      "rows": 31,
      "target_name": "fantasy_points_total"
    },
    {
      "candidate_name": "ridge",
      "empirical_coverage_p10_p90": 0.8870967741935484,
      "evaluation_scope": "test",
      "mean_interval_width_p10_p90": 144.48889190212637,
      "pinball_loss_p10": 7.372051241186338,
      "pinball_loss_p50": 16.337562884930918,
      "pinball_loss_p90": 10.687797263617147,
      "position": "QB",
      "prediction_season": 2025,
      "projection_tier": "middle",
      "rows": 62,
      "target_name": "fantasy_points_total"
    },
    {
      "candidate_name": "ridge",
      "empirical_coverage_p10_p90": 1.0,
      "evaluation_scope": "test",
      "mean_interval_width_p10_p90": 144.4888919021263,
      "pinball_loss_p10": 9.246318864863971,
      "pinball_loss_p50": 11.175580666083471,
      "pinball_loss_p90": 5.20257032534866,
      "position": "QB",
      "prediction_season": 2025,
      "projection_tier": "lower",
      "rows": 31,
      "target_name": "fantasy_points_total"
    },
    {
      "candidate_name": "ridge",
      "empirical_coverage_p10_p90": 0.7983193277310925,
      "evaluation_scope": "validation",
      "mean_interval_width_p10_p90": 154.31349578508915,
      "pinball_loss_p10": 12.0047272630672,
      "pinball_loss_p50": 23.297437168493953,
      "pinball_loss_p90": 13.52621527190663,
      "position": "QB",
      "prediction_season": 2020,
      "projection_tier": "all",
      "rows": 119,
      "target_name": "fantasy_points_total"
    },
    {
      "candidate_name": "ridge",
      "empirical_coverage_p10_p90": 0.5,
      "evaluation_scope": "validation",
      "mean_interval_width_p10_p90": 154.31349578508917,
      "pinball_loss_p10": 23.66142498804194,
      "pinball_loss_p50": 43.215210714501715,
      "pinball_loss_p90": 20.3412482044685,
      "position": "QB",
      "prediction_season": 2020,
      "projection_tier": "top",
      "rows": 30,
      "target_name": "fantasy_points_total"
    },
    {
      "candidate_name": "ridge",
      "empirical_coverage_p10_p90": 0.847457627118644,
      "evaluation_scope": "validation",
      "mean_interval_width_p10_p90": 154.31349578508915,
      "pinball_loss_p10": 7.290042782255382,
      "pinball_loss_p50": 18.895776596929093,
      "pinball_loss_p90": 13.983880582681996,
      "position": "QB",
      "prediction_season": 2020,
      "projection_tier": "middle",
      "rows": 59,
      "target_name": "fantasy_points_total"
    },
    {
      "candidate_name": "ridge",
      "empirical_coverage_p10_p90": 1.0,
      "evaluation_scope": "validation",
      "mean_interval_width_p10_p90": 154.31349578508917,
      "pinball_loss_p10": 9.620242350355701,
      "pinball_loss_p50": 12.036262746563727,
      "pinball_loss_p90": 5.811107228153216,
      "position": "QB",
      "prediction_season": 2020,
      "projection_tier": "lower",
      "rows": 30,
      "target_name": "fantasy_points_total"
    },
    {
      "candidate_name": "ridge",
      "empirical_coverage_p10_p90": 0.816,
      "evaluation_scope": "validation",
      "mean_interval_width_p10_p90": 154.77028525720286,
      "pinball_loss_p10": 14.206228544737506,
      "pinball_loss_p50": 23.52693133365371,
      "pinball_loss_p90": 12.959846725346157,
      "position": "QB",
      "prediction_season": 2021,
      "projection_tier": "all",
      "rows": 125,
      "target_name": "fantasy_points_total"
    },
    {
      "candidate_name": "ridge",
      "empirical_coverage_p10_p90": 0.6451612903225806,
      "evaluation_scope": "validation",
      "mean_interval_width_p10_p90": 154.7702852572028,
      "pinball_loss_p10": 33.20501701560694,
      "pinball_loss_p50": 41.78031447005147,
      "pinball_loss_p90": 14.861952766946448,
      "position": "QB",
      "prediction_season": 2021,
      "projection_tier": "top",
      "rows": 31,
      "target_name": "fantasy_points_total"
    },
    {
      "candidate_name": "ridge",
      "empirical_coverage_p10_p90": 0.8253968253968254,
      "evaluation_scope": "validation",
      "mean_interval_width_p10_p90": 154.77028525720266,
      "pinball_loss_p10": 7.955589212874691,
      "pinball_loss_p50": 22.485911731703307,
      "pinball_loss_p90": 14.335760001416093,
      "position": "QB",
      "prediction_season": 2021,
      "projection_tier": "middle",
      "rows": 63,
      "target_name": "fantasy_points_total"
    },
    {
      "candidate_name": "ridge",
      "empirical_coverage_p10_p90": 0.967741935483871,
      "evaluation_scope": "validation",
      "mean_interval_width_p10_p90": 154.7702852572028,
      "pinball_loss_p10": 7.910352264427977,
      "pinball_loss_p50": 7.389168678639012,
      "pinball_loss_p90": 8.261529832377942,
      "position": "QB",
      "prediction_season": 2021,
      "projection_tier": "lower",
      "rows": 31,
      "target_name": "fantasy_points_total"
    },
    {
      "candidate_name": "ridge",
      "empirical_coverage_p10_p90": 0.792,
      "evaluation_scope": "validation",
      "mean_interval_width_p10_p90": 146.6240174037836,
      "pinball_loss_p10": 10.57954375313707,
      "pinball_loss_p50": 21.19326057861711,
      "pinball_loss_p90": 13.0011318769139,
      "position": "QB",
      "prediction_season": 2022,
      "projection_tier": "all",
      "rows": 125,
      "target_name": "fantasy_points_total"
    },
    {
      "candidate_name": "ridge",
      "empirical_coverage_p10_p90": 0.5806451612903226,
      "evaluation_scope": "validation",
      "mean_interval_width_p10_p90": 146.6240174037836,
      "pinball_loss_p10": 15.990082747641054,
      "pinball_loss_p50": 34.84314327432062,
      "pinball_loss_p90": 14.84969800836514,
      "position": "QB",
      "prediction_season": 2022,
      "projection_tier": "top",
      "rows": 31,
      "target_name": "fantasy_points_total"
    },
    {
      "candidate_name": "ridge",
      "empirical_coverage_p10_p90": 0.7936507936507936,
      "evaluation_scope": "validation",
      "mean_interval_width_p10_p90": 146.6240174037835,
      "pinball_loss_p10": 9.297264737467929,
      "pinball_loss_p50": 21.573406337779645,
      "pinball_loss_p90": 15.09982726838049,
      "position": "QB",
      "prediction_season": 2022,
      "projection_tier": "middle",
      "rows": 63,
      "target_name": "fantasy_points_total"
    },
    {
      "candidate_name": "ridge",
      "empirical_coverage_p10_p90": 1.0,
      "evaluation_scope": "validation",
      "mean_interval_width_p10_p90": 146.6240174037836,
      "pinball_loss_p10": 7.774926629186503,
      "pinball_loss_p50": 6.770823598163971,
      "pinball_loss_p90": 6.887475111191854,
      "position": "QB",
      "prediction_season": 2022,
      "projection_tier": "lower",
      "rows": 31,
      "target_name": "fantasy_points_total"
    },
    {
      "candidate_name": "ridge",
      "empirical_coverage_p10_p90": 0.7983870967741935,
      "evaluation_scope": "validation",
      "mean_interval_width_p10_p90": 149.56098946599272,
      "pinball_loss_p10": 12.140841548785156,
      "pinball_loss_p50": 23.925689995709984,
      "pinball_loss_p90": 14.182319406265158,
      "position": "QB",
      "prediction_season": 2023,
      "projection_tier": "all",
      "rows": 124,
      "target_name": "fantasy_points_total"
    },
    {
      "candidate_name": "ridge",
      "empirical_coverage_p10_p90": 0.45161290322580644,
      "evaluation_scope": "validation",
      "mean_interval_width_p10_p90": 149.56098946599275,
      "pinball_loss_p10": 24.420108032656117,
      "pinball_loss_p50": 43.74123717699558,
      "pinball_loss_p90": 21.3465892707895,
      "position": "QB",
      "prediction_season": 2023,
      "projection_tier": "top",
      "rows": 31,
      "target_name": "fantasy_points_total"
    },
    {
      "candidate_name": "ridge",
      "empirical_coverage_p10_p90": 0.8709677419354839,
      "evaluation_scope": "validation",
      "mean_interval_width_p10_p90": 149.5609894659926,
      "pinball_loss_p10": 7.208616944654482,
      "pinball_loss_p50": 18.55736975345189,
      "pinball_loss_p90": 15.076306840423694,
      "position": "QB",
      "prediction_season": 2023,
      "projection_tier": "middle",
      "rows": 62,
      "target_name": "fantasy_points_total"
    },
    {
      "candidate_name": "ridge",
      "empirical_coverage_p10_p90": 1.0,
      "evaluation_scope": "validation",
      "mean_interval_width_p10_p90": 149.56098946599272,
      "pinball_loss_p10": 9.72602427317553,
      "pinball_loss_p50": 14.846783298940592,
      "pinball_loss_p90": 5.230074673423739,
      "position": "QB",
      "prediction_season": 2023,
      "projection_tier": "lower",
      "rows": 31,
      "target_name": "fantasy_points_total"
    },
    {
      "candidate_name": "ridge",
      "empirical_coverage_p10_p90": 0.8,
      "evaluation_scope": "validation",
      "mean_interval_width_p10_p90": 141.8185132321827,
      "pinball_loss_p10": 11.509982748819741,
      "pinball_loss_p50": 22.03559220733798,
      "pinball_loss_p90": 14.327646507664374,
      "position": "QB",
      "prediction_season": 2024,
      "projection_tier": "all",
      "rows": 125,
      "target_name": "fantasy_points_total"
    },
    {
      "candidate_name": "ridge",
      "empirical_coverage_p10_p90": 0.5483870967741935,
      "evaluation_scope": "validation",
      "mean_interval_width_p10_p90": 141.8185132321827,
      "pinball_loss_p10": 20.820840525935093,
      "pinball_loss_p50": 38.315012787968236,
      "pinball_loss_p90": 22.19032950664977,
      "position": "QB",
      "prediction_season": 2024,
      "projection_tier": "top",
      "rows": 31,
      "target_name": "fantasy_points_total"
    },
    {
      "candidate_name": "ridge",
      "empirical_coverage_p10_p90": 0.8571428571428571,
      "evaluation_scope": "validation",
      "mean_interval_width_p10_p90": 141.8185132321828,
      "pinball_loss_p10": 7.655470586359922,
      "pinball_loss_p50": 16.62859893638145,
      "pinball_loss_p90": 12.129712213731402,
      "position": "QB",
      "prediction_season": 2024,
      "projection_tier": "middle",
      "rows": 63,
      "target_name": "fantasy_points_total"
    },
    {
      "candidate_name": "ridge",
      "empirical_coverage_p10_p90": 0.9354838709677419,
      "evaluation_scope": "validation",
      "mean_interval_width_p10_p90": 141.8185132321827,
      "pinball_loss_p10": 10.032488398638852,
      "pinball_loss_p50": 16.74457730639358,
      "pinball_loss_p90": 10.931733202800825,
      "position": "QB",
      "prediction_season": 2024,
      "projection_tier": "lower",
      "rows": 31,
      "target_name": "fantasy_points_total"
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
      "absolute_importance": 46.49012017747645,
      "coefficient": 46.49012017747645,
      "direction": "positive",
      "feature": "numeric__lag1_fantasy_points_total",
      "rank": 1
    },
    {
      "absolute_importance": 27.969087726072733,
      "coefficient": -27.969087726072733,
      "direction": "negative",
      "feature": "categorical__previous_team_IND",
      "rank": 2
    },
    {
      "absolute_importance": 23.101649056456665,
      "coefficient": -23.101649056456665,
      "direction": "negative",
      "feature": "numeric__weighted_3yr_passing_attempts_per_game",
      "rank": 3
    },
    {
      "absolute_importance": 21.945331477406064,
      "coefficient": 21.945331477406064,
      "direction": "positive",
      "feature": "categorical__previous_team_SEA",
      "rank": 4
    },
    {
      "absolute_importance": 21.693979962596956,
      "coefficient": 21.693979962596956,
      "direction": "positive",
      "feature": "categorical__previous_team_PHI",
      "rank": 5
    },
    {
      "absolute_importance": 21.681689555892234,
      "coefficient": 21.681689555892234,
      "direction": "positive",
      "feature": "numeric__weighted_3yr_passing_yards_per_game",
      "rank": 6
    },
    {
      "absolute_importance": 21.03649831236537,
      "coefficient": -21.03649831236537,
      "direction": "negative",
      "feature": "categorical__previous_team_CLE",
      "rank": 7
    },
    {
      "absolute_importance": 19.557783028606316,
      "coefficient": 19.557783028606316,
      "direction": "positive",
      "feature": "categorical__previous_team_LA",
      "rank": 8
    },
    {
      "absolute_importance": 19.55542010254284,
      "coefficient": 19.55542010254284,
      "direction": "positive",
      "feature": "categorical__previous_team_NE",
      "rank": 9
    },
    {
      "absolute_importance": 18.588424916764087,
      "coefficient": 18.588424916764087,
      "direction": "positive",
      "feature": "categorical__previous_team_KC",
      "rank": 10
    },
    {
      "absolute_importance": 17.044112960991708,
      "coefficient": -17.044112960991708,
      "direction": "negative",
      "feature": "numeric__age_at_cutoff",
      "rank": 11
    },
    {
      "absolute_importance": 16.617132199306937,
      "coefficient": 16.617132199306937,
      "direction": "positive",
      "feature": "categorical__previous_team_DET",
      "rank": 12
    },
    {
      "absolute_importance": 15.590217601261525,
      "coefficient": -15.590217601261525,
      "direction": "negative",
      "feature": "categorical__previous_team_ARI",
      "rank": 13
    },
    {
      "absolute_importance": 14.654557528873546,
      "coefficient": -14.654557528873546,
      "direction": "negative",
      "feature": "categorical__previous_team_PIT",
      "rank": 14
    },
    {
      "absolute_importance": 13.648748569498364,
      "coefficient": -13.648748569498364,
      "direction": "negative",
      "feature": "categorical__previous_team_WAS",
      "rank": 15
    },
    {
      "absolute_importance": 13.337728441419403,
      "coefficient": 13.337728441419403,
      "direction": "positive",
      "feature": "categorical__previous_team_LAC",
      "rank": 16
    },
    {
      "absolute_importance": 13.05348120913585,
      "coefficient": 13.05348120913585,
      "direction": "positive",
      "feature": "numeric__weighted_3yr_fantasy_points_per_game",
      "rank": 17
    },
    {
      "absolute_importance": 12.46268352060895,
      "coefficient": 12.46268352060895,
      "direction": "positive",
      "feature": "categorical__previous_team_BUF",
      "rank": 18
    },
    {
      "absolute_importance": 12.44545455249498,
      "coefficient": -12.44545455249498,
      "direction": "negative",
      "feature": "categorical__previous_team_HOU",
      "rank": 19
    },
    {
      "absolute_importance": 11.81460523874876,
      "coefficient": 11.81460523874876,
      "direction": "positive",
      "feature": "categorical__previous_team_GB",
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

- Project-relative path: `models/artifacts/phase4-7ae8e9aed04bffca00c0/attempt-866987f75a2c406693cf892d49adc975/QB/fantasy_points_total/ridge.joblib`
- SHA-256: `ae127e07ba4a343eb0d8d8497143879a44cd4023bc9fe8c30bdaca9a2260def0`

## Additional metadata

````json
{
  "publication_id": "attempt-866987f75a2c406693cf892d49adc975"
}
````
