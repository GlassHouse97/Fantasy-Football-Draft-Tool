# Model Card: phase4-052d2866899a665a44f3-wr-total-ridge

- Model ID: `phase4-052d2866899a665a44f3-wr-total-ridge`
- Trained at: 2026-08-24T20:21:18+00:00
- Target: `fantasy_points_total`
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
  "draft_relevant_validation_mae": 59.010869227177174,
  "draft_relevant_validation_rows": 180,
  "draft_relevant_validation_signed_bias": -13.654930255988411,
  "position": "WR",
  "target_name": "fantasy_points_total",
  "test_mae": 22.765254092883012,
  "test_rows": 434,
  "test_season": 2025,
  "validation_mae": 27.88103226455879,
  "validation_rows": 2109,
  "validation_seasons": [
    2020,
    2021,
    2022,
    2023,
    2024
  ],
  "validation_top_n_capture_rate": 0.6833333333333333
}
````

## Comparison with transparent baselines

````json
{
  "best_learned_vs_baseline_bootstrap": {
    "candidate_mae": 58.8156626037677,
    "ci95_lower": -3.130543470007716,
    "ci95_upper": 7.379321027205819,
    "direction": "uncertain",
    "mae_difference_candidate_minus_reference": 1.918842225695002,
    "n_resamples": 2000,
    "reference_mae": 56.8968203780727,
    "rows": 180,
    "seed": 42
  },
  "decision_status": "learned_draft_relevant_regression_baseline_retained",
  "learned_improvement_status": "regression",
  "reference_metrics": {
    "candidate_name": "age_position_adjusted",
    "candidate_source": "baseline",
    "draft_relevant_validation_mae": 56.8968203780727,
    "draft_relevant_validation_rows": 180,
    "draft_relevant_validation_signed_bias": 21.53161016093822,
    "position": "WR",
    "target_name": "fantasy_points_total",
    "test_mae": 32.661684199629065,
    "test_rows": 434,
    "test_season": 2025,
    "validation_mae": 33.488095587295305,
    "validation_rows": 2109,
    "validation_seasons": [
      2020,
      2021,
      2022,
      2023,
      2024
    ],
    "validation_top_n_capture_rate": 0.7277777777777777
  },
  "selected_champion": "age_position_adjusted",
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
      "empirical_coverage_p10_p90": 0.8271889400921659,
      "evaluation_scope": "test",
      "mean_interval_width_p10_p90": 74.85831446614834,
      "pinball_loss_p10": 6.785725028851077,
      "pinball_loss_p50": 11.382627046441506,
      "pinball_loss_p90": 6.8161407452611735,
      "position": "WR",
      "prediction_season": 2025,
      "projection_tier": "all",
      "rows": 434,
      "target_name": "fantasy_points_total"
    },
    {
      "candidate_name": "ridge",
      "empirical_coverage_p10_p90": 0.42201834862385323,
      "evaluation_scope": "test",
      "mean_interval_width_p10_p90": 74.85831446614833,
      "pinball_loss_p10": 14.500590428727643,
      "pinball_loss_p50": 26.275485790292613,
      "pinball_loss_p90": 15.85923961998342,
      "position": "WR",
      "prediction_season": 2025,
      "projection_tier": "top",
      "rows": 109,
      "target_name": "fantasy_points_total"
    },
    {
      "candidate_name": "ridge",
      "empirical_coverage_p10_p90": 0.9583333333333334,
      "evaluation_scope": "test",
      "mean_interval_width_p10_p90": 74.85831446614836,
      "pinball_loss_p10": 3.6302920617845014,
      "pinball_loss_p50": 5.601573547614192,
      "pinball_loss_p90": 4.413901149487359,
      "position": "WR",
      "prediction_season": 2025,
      "projection_tier": "middle",
      "rows": 216,
      "target_name": "fantasy_points_total"
    },
    {
      "candidate_name": "ridge",
      "empirical_coverage_p10_p90": 0.9724770642201835,
      "evaluation_scope": "test",
      "mean_interval_width_p10_p90": 74.85831446614833,
      "pinball_loss_p10": 5.323827710500943,
      "pinball_loss_p50": 7.945800924119762,
      "pinball_loss_p90": 2.5334432713384087,
      "position": "WR",
      "prediction_season": 2025,
      "projection_tier": "lower",
      "rows": 109,
      "target_name": "fantasy_points_total"
    },
    {
      "candidate_name": "ridge",
      "empirical_coverage_p10_p90": 0.8502415458937198,
      "evaluation_scope": "validation",
      "mean_interval_width_p10_p90": 132.09813484080382,
      "pinball_loss_p10": 7.329813235169453,
      "pinball_loss_p50": 18.40164921138302,
      "pinball_loss_p90": 10.103691587711078,
      "position": "WR",
      "prediction_season": 2020,
      "projection_tier": "all",
      "rows": 414,
      "target_name": "fantasy_points_total"
    },
    {
      "candidate_name": "ridge",
      "empirical_coverage_p10_p90": 0.5673076923076923,
      "evaluation_scope": "validation",
      "mean_interval_width_p10_p90": 132.09813484080382,
      "pinball_loss_p10": 15.947396491733175,
      "pinball_loss_p50": 31.02384082427358,
      "pinball_loss_p90": 12.86582536745138,
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
      "mean_interval_width_p10_p90": 132.09813484080382,
      "pinball_loss_p10": 3.9019101746986142,
      "pinball_loss_p50": 18.30599684457475,
      "pinball_loss_p90": 9.918843810607141,
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
      "mean_interval_width_p10_p90": 132.09813484080382,
      "pinball_loss_p10": 5.502114886846049,
      "pinball_loss_p50": 5.968922863516531,
      "pinball_loss_p90": 7.707698597234333,
      "position": "WR",
      "prediction_season": 2020,
      "projection_tier": "lower",
      "rows": 104,
      "target_name": "fantasy_points_total"
    },
    {
      "candidate_name": "ridge",
      "empirical_coverage_p10_p90": 0.847255369928401,
      "evaluation_scope": "validation",
      "mean_interval_width_p10_p90": 125.85585070848607,
      "pinball_loss_p10": 8.011003377338412,
      "pinball_loss_p50": 14.894743300847388,
      "pinball_loss_p90": 11.130646201029744,
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
      "mean_interval_width_p10_p90": 125.85585070848607,
      "pinball_loss_p10": 16.698237359446768,
      "pinball_loss_p50": 29.075089139318766,
      "pinball_loss_p90": 13.991207315221793,
      "position": "WR",
      "prediction_season": 2021,
      "projection_tier": "top",
      "rows": 105,
      "target_name": "fantasy_points_total"
    },
    {
      "candidate_name": "ridge",
      "empirical_coverage_p10_p90": 0.9090909090909091,
      "evaluation_scope": "validation",
      "mean_interval_width_p10_p90": 125.85585070848607,
      "pinball_loss_p10": 4.557400379852811,
      "pinball_loss_p50": 11.599678775011453,
      "pinball_loss_p90": 9.371424016546028,
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
      "mean_interval_width_p10_p90": 125.85585070848607,
      "pinball_loss_p10": 6.19808393308235,
      "pinball_loss_p50": 7.273144947135151,
      "pinball_loss_p90": 11.771774958810038,
      "position": "WR",
      "prediction_season": 2021,
      "projection_tier": "lower",
      "rows": 105,
      "target_name": "fantasy_points_total"
    },
    {
      "candidate_name": "ridge",
      "empirical_coverage_p10_p90": 0.8263888888888888,
      "evaluation_scope": "validation",
      "mean_interval_width_p10_p90": 91.58876350244108,
      "pinball_loss_p10": 6.77879502060257,
      "pinball_loss_p50": 12.935694340187151,
      "pinball_loss_p90": 8.085564114449298,
      "position": "WR",
      "prediction_season": 2022,
      "projection_tier": "all",
      "rows": 432,
      "target_name": "fantasy_points_total"
    },
    {
      "candidate_name": "ridge",
      "empirical_coverage_p10_p90": 0.49074074074074076,
      "evaluation_scope": "validation",
      "mean_interval_width_p10_p90": 91.5887635024411,
      "pinball_loss_p10": 14.46395803676373,
      "pinball_loss_p50": 26.13627808470629,
      "pinball_loss_p90": 12.09966398906968,
      "position": "WR",
      "prediction_season": 2022,
      "projection_tier": "top",
      "rows": 108,
      "target_name": "fantasy_points_total"
    },
    {
      "candidate_name": "ridge",
      "empirical_coverage_p10_p90": 0.9074074074074074,
      "evaluation_scope": "validation",
      "mean_interval_width_p10_p90": 91.58876350244108,
      "pinball_loss_p10": 3.816776888363139,
      "pinball_loss_p50": 11.087684602263742,
      "pinball_loss_p90": 8.050692193701838,
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
      "mean_interval_width_p10_p90": 91.58876350244108,
      "pinball_loss_p10": 5.017668268920273,
      "pinball_loss_p50": 3.4311300715148283,
      "pinball_loss_p90": 4.1412080813238346,
      "position": "WR",
      "prediction_season": 2022,
      "projection_tier": "lower",
      "rows": 108,
      "target_name": "fantasy_points_total"
    },
    {
      "candidate_name": "ridge",
      "empirical_coverage_p10_p90": 0.8353221957040573,
      "evaluation_scope": "validation",
      "mean_interval_width_p10_p90": 87.42200960933766,
      "pinball_loss_p10": 6.0177377350036245,
      "pinball_loss_p50": 11.388491708505175,
      "pinball_loss_p90": 7.525181747767744,
      "position": "WR",
      "prediction_season": 2023,
      "projection_tier": "all",
      "rows": 419,
      "target_name": "fantasy_points_total"
    },
    {
      "candidate_name": "ridge",
      "empirical_coverage_p10_p90": 0.45714285714285713,
      "evaluation_scope": "validation",
      "mean_interval_width_p10_p90": 87.42200960933766,
      "pinball_loss_p10": 11.536558909253829,
      "pinball_loss_p50": 25.01232273698267,
      "pinball_loss_p90": 13.867668587192565,
      "position": "WR",
      "prediction_season": 2023,
      "projection_tier": "top",
      "rows": 105,
      "target_name": "fantasy_points_total"
    },
    {
      "candidate_name": "ridge",
      "empirical_coverage_p10_p90": 0.9473684210526315,
      "evaluation_scope": "validation",
      "mean_interval_width_p10_p90": 87.42200960933766,
      "pinball_loss_p10": 3.6130348578273335,
      "pinball_loss_p50": 7.030704354693821,
      "pinball_loss_p90": 6.312325528948117,
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
      "mean_interval_width_p10_p90": 87.42200960933766,
      "pinball_loss_p10": 5.285420382942419,
      "pinball_loss_p50": 6.438732650947427,
      "pinball_loss_p90": 3.596856334374371,
      "position": "WR",
      "prediction_season": 2023,
      "projection_tier": "lower",
      "rows": 105,
      "target_name": "fantasy_points_total"
    },
    {
      "candidate_name": "ridge",
      "empirical_coverage_p10_p90": 0.8023529411764706,
      "evaluation_scope": "validation",
      "mean_interval_width_p10_p90": 81.44245198853653,
      "pinball_loss_p10": 6.607596104460648,
      "pinball_loss_p50": 12.191459589612005,
      "pinball_loss_p90": 8.098917457246957,
      "position": "WR",
      "prediction_season": 2024,
      "projection_tier": "all",
      "rows": 425,
      "target_name": "fantasy_points_total"
    },
    {
      "candidate_name": "ridge",
      "empirical_coverage_p10_p90": 0.3867924528301887,
      "evaluation_scope": "validation",
      "mean_interval_width_p10_p90": 81.44245198853653,
      "pinball_loss_p10": 12.945586976476429,
      "pinball_loss_p50": 26.169368472156858,
      "pinball_loss_p90": 15.702187961945938,
      "position": "WR",
      "prediction_season": 2024,
      "projection_tier": "top",
      "rows": 106,
      "target_name": "fantasy_points_total"
    },
    {
      "candidate_name": "ridge",
      "empirical_coverage_p10_p90": 0.9107981220657277,
      "evaluation_scope": "validation",
      "mean_interval_width_p10_p90": 81.44245198853653,
      "pinball_loss_p10": 4.099822147628631,
      "pinball_loss_p50": 7.5182697290083675,
      "pinball_loss_p90": 6.93451648699331,
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
      "mean_interval_width_p10_p90": 81.44245198853653,
      "pinball_loss_p10": 5.308811390984675,
      "pinball_loss_p50": 7.604017125072583,
      "pinball_loss_p90": 2.835433807868979,
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
      "absolute_importance": 32.06779315517168,
      "coefficient": 32.06779315517168,
      "direction": "positive",
      "feature": "numeric__lag1_fantasy_points_total",
      "rank": 1
    },
    {
      "absolute_importance": 16.284027537002572,
      "coefficient": 16.284027537002572,
      "direction": "positive",
      "feature": "categorical__previous_team_MIN",
      "rank": 2
    },
    {
      "absolute_importance": 11.545870684932142,
      "coefficient": -11.545870684932142,
      "direction": "negative",
      "feature": "categorical__previous_team_NYG",
      "rank": 3
    },
    {
      "absolute_importance": 11.404334573492827,
      "coefficient": -11.404334573492827,
      "direction": "negative",
      "feature": "categorical__previous_team_JAX",
      "rank": 4
    },
    {
      "absolute_importance": 10.608822144950866,
      "coefficient": -10.608822144950866,
      "direction": "negative",
      "feature": "categorical__previous_team_NYJ",
      "rank": 5
    },
    {
      "absolute_importance": 10.132430367478483,
      "coefficient": 10.132430367478483,
      "direction": "positive",
      "feature": "categorical__previous_team_DAL",
      "rank": 6
    },
    {
      "absolute_importance": 10.012042399522235,
      "coefficient": 10.012042399522235,
      "direction": "positive",
      "feature": "numeric__weighted_3yr_receiving_yards_per_game",
      "rank": 7
    },
    {
      "absolute_importance": 9.7586571860333,
      "coefficient": -9.7586571860333,
      "direction": "negative",
      "feature": "categorical__previous_team_BAL",
      "rank": 8
    },
    {
      "absolute_importance": 9.388006032497863,
      "coefficient": -9.388006032497863,
      "direction": "negative",
      "feature": "numeric__age_at_cutoff",
      "rank": 9
    },
    {
      "absolute_importance": 7.960898461127418,
      "coefficient": 7.960898461127418,
      "direction": "positive",
      "feature": "categorical__previous_team_GB",
      "rank": 10
    },
    {
      "absolute_importance": 7.916865333326184,
      "coefficient": 7.916865333326184,
      "direction": "positive",
      "feature": "categorical__previous_team_SEA",
      "rank": 11
    },
    {
      "absolute_importance": 7.849653194252537,
      "coefficient": 7.849653194252537,
      "direction": "positive",
      "feature": "numeric__lag1_fantasy_points_per_game",
      "rank": 12
    },
    {
      "absolute_importance": 7.462384162897707,
      "coefficient": -7.462384162897707,
      "direction": "negative",
      "feature": "categorical__previous_team_TEN",
      "rank": 13
    },
    {
      "absolute_importance": 7.281448656967361,
      "coefficient": -7.281448656967361,
      "direction": "negative",
      "feature": "categorical__previous_team_CLE",
      "rank": 14
    },
    {
      "absolute_importance": 7.214866977396519,
      "coefficient": -7.214866977396519,
      "direction": "negative",
      "feature": "numeric__draft_pick",
      "rank": 15
    },
    {
      "absolute_importance": 7.019415136559581,
      "coefficient": 7.019415136559581,
      "direction": "positive",
      "feature": "categorical__previous_team_DET",
      "rank": 16
    },
    {
      "absolute_importance": 6.178216100543554,
      "coefficient": 6.178216100543554,
      "direction": "positive",
      "feature": "categorical__previous_team_STL",
      "rank": 17
    },
    {
      "absolute_importance": 5.963463850382931,
      "coefficient": 5.963463850382931,
      "direction": "positive",
      "feature": "categorical__previous_team_LA",
      "rank": 18
    },
    {
      "absolute_importance": 5.79641054935111,
      "coefficient": -5.79641054935111,
      "direction": "negative",
      "feature": "categorical__previous_team_NO",
      "rank": 19
    },
    {
      "absolute_importance": 5.501070667289003,
      "coefficient": 5.501070667289003,
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

- Project-relative path: `models/artifacts/phase4-052d2866899a665a44f3/attempt-331cdaf7eb7f4721aa43c08d469288ee/WR/fantasy_points_total/ridge.joblib`
- SHA-256: `f7f4981cc07e67ce0b0ba12e99bbd6f8639a19e79a1798d594ca5c9057ee7fdf`

## Additional metadata

````json
{
  "publication_id": "attempt-331cdaf7eb7f4721aa43c08d469288ee"
}
````
