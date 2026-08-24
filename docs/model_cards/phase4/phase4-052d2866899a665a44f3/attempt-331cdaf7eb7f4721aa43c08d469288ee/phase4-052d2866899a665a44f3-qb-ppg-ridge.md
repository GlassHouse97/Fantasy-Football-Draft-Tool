# Model Card: phase4-052d2866899a665a44f3-qb-ppg-ridge

- Model ID: `phase4-052d2866899a665a44f3-qb-ppg-ridge`
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
  "draft_relevant_validation_mae": 3.3708183024137184,
  "draft_relevant_validation_rows": 55,
  "draft_relevant_validation_signed_bias": -0.35568912109263934,
  "position": "QB",
  "target_name": "fantasy_points_per_game",
  "test_mae": 4.307081627500359,
  "test_rows": 66,
  "test_season": 2025,
  "validation_mae": 4.312111249899847,
  "validation_rows": 348,
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
    "candidate_mae": 3.3708183024137184,
    "ci95_lower": -0.18437954522344538,
    "ci95_upper": 0.5321559165899932,
    "direction": "uncertain",
    "mae_difference_candidate_minus_reference": 0.1775231359926006,
    "n_resamples": 2000,
    "reference_mae": 3.1932951664211178,
    "rows": 55,
    "seed": 42
  },
  "decision_status": "learned_draft_relevant_regression_baseline_retained",
  "learned_improvement_status": "regression",
  "reference_metrics": {
    "candidate_name": "position_shrinkage",
    "candidate_source": "baseline",
    "draft_relevant_validation_mae": 3.1932951664211178,
    "draft_relevant_validation_rows": 55,
    "draft_relevant_validation_signed_bias": -0.5149281608010328,
    "position": "QB",
    "target_name": "fantasy_points_per_game",
    "test_mae": 4.698891239129586,
    "test_rows": 66,
    "test_season": 2025,
    "validation_mae": 4.3881796198403045,
    "validation_rows": 348,
    "validation_seasons": [
      2020,
      2021,
      2022,
      2023,
      2024
    ],
    "validation_top_n_capture_rate": null
  },
  "selected_champion": "position_shrinkage",
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
      "empirical_coverage_p10_p90": 0.7121212121212122,
      "evaluation_scope": "test",
      "mean_interval_width_p10_p90": 12.543464432479805,
      "pinball_loss_p10": 0.8829788287256338,
      "pinball_loss_p50": 2.1535408137501797,
      "pinball_loss_p90": 0.9368919608797733,
      "position": "QB",
      "prediction_season": 2025,
      "projection_tier": "all",
      "rows": 66,
      "target_name": "fantasy_points_per_game"
    },
    {
      "candidate_name": "ridge",
      "empirical_coverage_p10_p90": 0.7666666666666667,
      "evaluation_scope": "test",
      "mean_interval_width_p10_p90": 12.543464432479807,
      "pinball_loss_p10": 1.0130412489184621,
      "pinball_loss_p50": 2.0012020357401075,
      "pinball_loss_p90": 0.8810819200178575,
      "position": "QB",
      "prediction_season": 2025,
      "projection_tier": "top",
      "rows": 30,
      "target_name": "fantasy_points_per_game"
    },
    {
      "candidate_name": "ridge",
      "empirical_coverage_p10_p90": 0.6666666666666666,
      "evaluation_scope": "test",
      "mean_interval_width_p10_p90": 12.543464432479805,
      "pinball_loss_p10": 0.7662046797395701,
      "pinball_loss_p50": 2.345617982090945,
      "pinball_loss_p90": 0.9785577040776111,
      "position": "QB",
      "prediction_season": 2025,
      "projection_tier": "middle",
      "rows": 33,
      "target_name": "fantasy_points_per_game"
    },
    {
      "candidate_name": "ridge",
      "empirical_coverage_p10_p90": 0.6666666666666666,
      "evaluation_scope": "test",
      "mean_interval_width_p10_p90": 12.543464432479803,
      "pinball_loss_p10": 0.8668702656440516,
      "pinball_loss_p50": 1.564079742102482,
      "pinball_loss_p90": 1.0366691943227158,
      "position": "QB",
      "prediction_season": 2025,
      "projection_tier": "lower",
      "rows": 3,
      "target_name": "fantasy_points_per_game"
    },
    {
      "candidate_name": "ridge",
      "empirical_coverage_p10_p90": 0.7647058823529411,
      "evaluation_scope": "validation",
      "mean_interval_width_p10_p90": 13.733010559862798,
      "pinball_loss_p10": 1.22932698361643,
      "pinball_loss_p50": 2.4105784620238198,
      "pinball_loss_p90": 1.137892882472991,
      "position": "QB",
      "prediction_season": 2020,
      "projection_tier": "all",
      "rows": 68,
      "target_name": "fantasy_points_per_game"
    },
    {
      "candidate_name": "ridge",
      "empirical_coverage_p10_p90": 0.8275862068965517,
      "evaluation_scope": "validation",
      "mean_interval_width_p10_p90": 13.733010559862798,
      "pinball_loss_p10": 1.573404938459533,
      "pinball_loss_p50": 2.3288456117364484,
      "pinball_loss_p90": 0.8286155999857453,
      "position": "QB",
      "prediction_season": 2020,
      "projection_tier": "top",
      "rows": 29,
      "target_name": "fantasy_points_per_game"
    },
    {
      "candidate_name": "ridge",
      "empirical_coverage_p10_p90": 0.7419354838709677,
      "evaluation_scope": "validation",
      "mean_interval_width_p10_p90": 13.7330105598628,
      "pinball_loss_p10": 0.8968585060590951,
      "pinball_loss_p50": 2.2479336838604866,
      "pinball_loss_p90": 1.20811054195225,
      "position": "QB",
      "prediction_season": 2020,
      "projection_tier": "middle",
      "rows": 31,
      "target_name": "fantasy_points_per_game"
    },
    {
      "candidate_name": "ridge",
      "empirical_coverage_p10_p90": 0.625,
      "evaluation_scope": "validation",
      "mean_interval_width_p10_p90": 13.733010559862798,
      "pinball_loss_p10": 1.2703597478448552,
      "pinball_loss_p50": 3.337108559698465,
      "pinball_loss_p90": 1.9869296010071267,
      "position": "QB",
      "prediction_season": 2020,
      "projection_tier": "lower",
      "rows": 8,
      "target_name": "fantasy_points_per_game"
    },
    {
      "candidate_name": "ridge",
      "empirical_coverage_p10_p90": 0.7794117647058824,
      "evaluation_scope": "validation",
      "mean_interval_width_p10_p90": 14.104012610672843,
      "pinball_loss_p10": 1.1137996183998802,
      "pinball_loss_p50": 2.3218031404073174,
      "pinball_loss_p90": 1.077990135179844,
      "position": "QB",
      "prediction_season": 2021,
      "projection_tier": "all",
      "rows": 68,
      "target_name": "fantasy_points_per_game"
    },
    {
      "candidate_name": "ridge",
      "empirical_coverage_p10_p90": 0.8518518518518519,
      "evaluation_scope": "validation",
      "mean_interval_width_p10_p90": 14.104012610672843,
      "pinball_loss_p10": 1.0643174006586809,
      "pinball_loss_p50": 1.9861215952206734,
      "pinball_loss_p90": 1.0471464013310194,
      "position": "QB",
      "prediction_season": 2021,
      "projection_tier": "top",
      "rows": 27,
      "target_name": "fantasy_points_per_game"
    },
    {
      "candidate_name": "ridge",
      "empirical_coverage_p10_p90": 0.75,
      "evaluation_scope": "validation",
      "mean_interval_width_p10_p90": 14.104012610672847,
      "pinball_loss_p10": 1.140549440188205,
      "pinball_loss_p50": 2.392051960302943,
      "pinball_loss_p90": 0.9299287494298348,
      "position": "QB",
      "prediction_season": 2021,
      "projection_tier": "middle",
      "rows": 36,
      "target_name": "fantasy_points_per_game"
    },
    {
      "candidate_name": "ridge",
      "empirical_coverage_p10_p90": 0.6,
      "evaluation_scope": "validation",
      "mean_interval_width_p10_p90": 14.104012610672845,
      "pinball_loss_p10": 1.1884048773264209,
      "pinball_loss_p50": 3.628691981166692,
      "pinball_loss_p90": 2.310588275363563,
      "position": "QB",
      "prediction_season": 2021,
      "projection_tier": "lower",
      "rows": 5,
      "target_name": "fantasy_points_per_game"
    },
    {
      "candidate_name": "ridge",
      "empirical_coverage_p10_p90": 0.8513513513513513,
      "evaluation_scope": "validation",
      "mean_interval_width_p10_p90": 14.31042646725456,
      "pinball_loss_p10": 0.8113325423816228,
      "pinball_loss_p50": 1.9409170424247082,
      "pinball_loss_p90": 0.9314100320415095,
      "position": "QB",
      "prediction_season": 2022,
      "projection_tier": "all",
      "rows": 74,
      "target_name": "fantasy_points_per_game"
    },
    {
      "candidate_name": "ridge",
      "empirical_coverage_p10_p90": 0.8666666666666667,
      "evaluation_scope": "validation",
      "mean_interval_width_p10_p90": 14.310426467254562,
      "pinball_loss_p10": 0.8000816827105574,
      "pinball_loss_p50": 1.8070959687201908,
      "pinball_loss_p90": 0.9162806156955372,
      "position": "QB",
      "prediction_season": 2022,
      "projection_tier": "top",
      "rows": 30,
      "target_name": "fantasy_points_per_game"
    },
    {
      "candidate_name": "ridge",
      "empirical_coverage_p10_p90": 0.8285714285714286,
      "evaluation_scope": "validation",
      "mean_interval_width_p10_p90": 14.310426467254562,
      "pinball_loss_p10": 0.7960608021544979,
      "pinball_loss_p50": 2.0836623728223227,
      "pinball_loss_p90": 1.0389965723917818,
      "position": "QB",
      "prediction_season": 2022,
      "projection_tier": "middle",
      "rows": 35,
      "target_name": "fantasy_points_per_game"
    },
    {
      "candidate_name": "ridge",
      "empirical_coverage_p10_p90": 0.8888888888888888,
      "evaluation_scope": "validation",
      "mean_interval_width_p10_p90": 14.310426467254562,
      "pinball_loss_p10": 0.9082255088351041,
      "pinball_loss_p50": 1.8318665587823793,
      "pinball_loss_p90": 0.563449318499248,
      "position": "QB",
      "prediction_season": 2022,
      "projection_tier": "lower",
      "rows": 9,
      "target_name": "fantasy_points_per_game"
    },
    {
      "candidate_name": "ridge",
      "empirical_coverage_p10_p90": 0.7857142857142857,
      "evaluation_scope": "validation",
      "mean_interval_width_p10_p90": 13.907872491786406,
      "pinball_loss_p10": 0.9397289382303744,
      "pinball_loss_p50": 2.1789705914613666,
      "pinball_loss_p90": 1.0178944107502659,
      "position": "QB",
      "prediction_season": 2023,
      "projection_tier": "all",
      "rows": 70,
      "target_name": "fantasy_points_per_game"
    },
    {
      "candidate_name": "ridge",
      "empirical_coverage_p10_p90": 0.8620689655172413,
      "evaluation_scope": "validation",
      "mean_interval_width_p10_p90": 13.907872491786406,
      "pinball_loss_p10": 0.9814542836728997,
      "pinball_loss_p50": 1.8807285810316183,
      "pinball_loss_p90": 0.9101505458677339,
      "position": "QB",
      "prediction_season": 2023,
      "projection_tier": "top",
      "rows": 29,
      "target_name": "fantasy_points_per_game"
    },
    {
      "candidate_name": "ridge",
      "empirical_coverage_p10_p90": 0.6764705882352942,
      "evaluation_scope": "validation",
      "mean_interval_width_p10_p90": 13.907872491786406,
      "pinball_loss_p10": 0.9382937763998325,
      "pinball_loss_p50": 2.656236375097337,
      "pinball_loss_p90": 1.1923410361800486,
      "position": "QB",
      "prediction_season": 2023,
      "projection_tier": "middle",
      "rows": 34,
      "target_name": "fantasy_points_per_game"
    },
    {
      "candidate_name": "ridge",
      "empirical_coverage_p10_p90": 1.0,
      "evaluation_scope": "validation",
      "mean_interval_width_p10_p90": 13.907872491786406,
      "pinball_loss_p10": 0.7738375788596896,
      "pinball_loss_p50": 1.0963965427241753,
      "pinball_loss_p90": 0.6169496703189511,
      "position": "QB",
      "prediction_season": 2023,
      "projection_tier": "lower",
      "rows": 7,
      "target_name": "fantasy_points_per_game"
    },
    {
      "candidate_name": "ridge",
      "empirical_coverage_p10_p90": 0.8088235294117647,
      "evaluation_scope": "validation",
      "mean_interval_width_p10_p90": 13.663782558079296,
      "pinball_loss_p10": 0.847612172932085,
      "pinball_loss_p50": 1.9463177349342933,
      "pinball_loss_p90": 0.9047544399736719,
      "position": "QB",
      "prediction_season": 2024,
      "projection_tier": "all",
      "rows": 68,
      "target_name": "fantasy_points_per_game"
    },
    {
      "candidate_name": "ridge",
      "empirical_coverage_p10_p90": 0.8620689655172413,
      "evaluation_scope": "validation",
      "mean_interval_width_p10_p90": 13.663782558079292,
      "pinball_loss_p10": 0.9812677897535825,
      "pinball_loss_p50": 1.6661291671733303,
      "pinball_loss_p90": 0.7529285092809664,
      "position": "QB",
      "prediction_season": 2024,
      "projection_tier": "top",
      "rows": 29,
      "target_name": "fantasy_points_per_game"
    },
    {
      "candidate_name": "ridge",
      "empirical_coverage_p10_p90": 0.7631578947368421,
      "evaluation_scope": "validation",
      "mean_interval_width_p10_p90": 13.663782558079294,
      "pinball_loss_p10": 0.736598395475203,
      "pinball_loss_p50": 2.137040632935373,
      "pinball_loss_p90": 1.0397926242558924,
      "position": "QB",
      "prediction_season": 2024,
      "projection_tier": "middle",
      "rows": 38,
      "target_name": "fantasy_points_per_game"
    },
    {
      "candidate_name": "ridge",
      "empirical_coverage_p10_p90": 1.0,
      "evaluation_scope": "validation",
      "mean_interval_width_p10_p90": 13.663782558079296,
      "pinball_loss_p10": 1.1901228284701715,
      "pinball_loss_p50": 2.824316075961213,
      "pinball_loss_p90": 0.17625542733775812,
      "position": "QB",
      "prediction_season": 2024,
      "projection_tier": "lower",
      "rows": 1,
      "target_name": "fantasy_points_per_game"
    }
  ],
  "empirical_not_guaranteed": true,
  "method": "training-only signed out-of-fold residual quantiles",
  "operational_center": "training_only_residual_adjusted_p50",
  "residual_rows": 204,
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
      "absolute_importance": 1.9909000334731541,
      "coefficient": 1.9909000334731541,
      "direction": "positive",
      "feature": "numeric__lag1_fantasy_points_total",
      "rank": 1
    },
    {
      "absolute_importance": 1.4872439659467414,
      "coefficient": 1.4872439659467414,
      "direction": "positive",
      "feature": "numeric__lag1_stat_games",
      "rank": 2
    },
    {
      "absolute_importance": 1.2451701984722257,
      "coefficient": 1.2451701984722257,
      "direction": "positive",
      "feature": "numeric__weighted_3yr_passing_yards_per_game",
      "rank": 3
    },
    {
      "absolute_importance": 1.2125130256923498,
      "coefficient": 1.2125130256923498,
      "direction": "positive",
      "feature": "numeric__weighted_3yr_carries_per_game",
      "rank": 4
    },
    {
      "absolute_importance": 1.2012529262192417,
      "coefficient": -1.2012529262192417,
      "direction": "negative",
      "feature": "numeric__age_at_cutoff",
      "rank": 5
    },
    {
      "absolute_importance": 1.0735030904831977,
      "coefficient": 1.0735030904831977,
      "direction": "positive",
      "feature": "categorical__previous_team_NO",
      "rank": 6
    },
    {
      "absolute_importance": 1.0289812613402534,
      "coefficient": 1.0289812613402534,
      "direction": "positive",
      "feature": "numeric__nfl_experience_years",
      "rank": 7
    },
    {
      "absolute_importance": 0.9987690407229739,
      "coefficient": -0.9987690407229739,
      "direction": "negative",
      "feature": "numeric__lag1_games_active",
      "rank": 8
    },
    {
      "absolute_importance": 0.9787835453880973,
      "coefficient": 0.9787835453880973,
      "direction": "positive",
      "feature": "numeric__weighted_3yr_fantasy_points_per_game",
      "rank": 9
    },
    {
      "absolute_importance": 0.9560049366989264,
      "coefficient": -0.9560049366989264,
      "direction": "negative",
      "feature": "categorical__previous_team_JAX",
      "rank": 10
    },
    {
      "absolute_importance": 0.9188368223711573,
      "coefficient": -0.9188368223711573,
      "direction": "negative",
      "feature": "numeric__weighted_3yr_interceptions_per_game",
      "rank": 11
    },
    {
      "absolute_importance": 0.8188253115314225,
      "coefficient": -0.8188253115314225,
      "direction": "negative",
      "feature": "numeric__lag1_fantasy_points_per_game",
      "rank": 12
    },
    {
      "absolute_importance": 0.7995203519114411,
      "coefficient": 0.7995203519114411,
      "direction": "positive",
      "feature": "categorical__previous_team_PHI",
      "rank": 13
    },
    {
      "absolute_importance": 0.7497601971443519,
      "coefficient": 0.7497601971443519,
      "direction": "positive",
      "feature": "categorical__previous_team_SEA",
      "rank": 14
    },
    {
      "absolute_importance": 0.7478521520899593,
      "coefficient": -0.7478521520899593,
      "direction": "negative",
      "feature": "categorical__previous_team_ATL",
      "rank": 15
    },
    {
      "absolute_importance": 0.7371253989582145,
      "coefficient": -0.7371253989582145,
      "direction": "negative",
      "feature": "numeric__draft_round",
      "rank": 16
    },
    {
      "absolute_importance": 0.72610955716909,
      "coefficient": 0.72610955716909,
      "direction": "positive",
      "feature": "categorical__previous_team_SF",
      "rank": 17
    },
    {
      "absolute_importance": 0.7177729428512136,
      "coefficient": 0.7177729428512136,
      "direction": "positive",
      "feature": "numeric__weighted_3yr_passing_tds_per_game",
      "rank": 18
    },
    {
      "absolute_importance": 0.6552060251218593,
      "coefficient": -0.6552060251218593,
      "direction": "negative",
      "feature": "categorical__previous_team_IND",
      "rank": 19
    },
    {
      "absolute_importance": 0.612496107573531,
      "coefficient": 0.612496107573531,
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

- Project-relative path: `models/artifacts/phase4-052d2866899a665a44f3/attempt-331cdaf7eb7f4721aa43c08d469288ee/QB/fantasy_points_per_game/ridge.joblib`
- SHA-256: `a5cb111358c4e0bf21b6af17f3aa3110b74c40e0c011948d45008779f11f0d5a`

## Additional metadata

````json
{
  "publication_id": "attempt-331cdaf7eb7f4721aa43c08d469288ee"
}
````
