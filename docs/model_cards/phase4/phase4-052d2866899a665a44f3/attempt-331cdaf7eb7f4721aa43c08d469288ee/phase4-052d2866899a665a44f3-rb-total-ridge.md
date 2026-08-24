# Model Card: phase4-052d2866899a665a44f3-rb-total-ridge

- Model ID: `phase4-052d2866899a665a44f3-rb-total-ridge`
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
  "draft_relevant_validation_mae": 71.98658533498542,
  "draft_relevant_validation_rows": 120,
  "draft_relevant_validation_signed_bias": -15.696207642686963,
  "position": "RB",
  "target_name": "fantasy_points_total",
  "test_mae": 27.16533265656641,
  "test_rows": 294,
  "test_season": 2025,
  "validation_mae": 27.06826062832246,
  "validation_rows": 1488,
  "validation_seasons": [
    2020,
    2021,
    2022,
    2023,
    2024
  ],
  "validation_top_n_capture_rate": 0.6416666666666667
}
````

## Comparison with transparent baselines

````json
{
  "best_learned_vs_baseline_bootstrap": {
    "candidate_mae": 71.98658533498542,
    "ci95_lower": -9.06866373005735,
    "ci95_upper": 3.243812948760474,
    "direction": "uncertain",
    "mae_difference_candidate_minus_reference": -3.1023207068635656,
    "n_resamples": 2000,
    "reference_mae": 75.08890604184899,
    "rows": 120,
    "seed": 42
  },
  "decision_status": "learned_draft_relevant_improvement_inconclusive_baseline_retained",
  "learned_improvement_status": "inconclusive",
  "reference_metrics": {
    "candidate_name": "position_shrinkage",
    "candidate_source": "baseline",
    "draft_relevant_validation_mae": 75.08890604184899,
    "draft_relevant_validation_rows": 120,
    "draft_relevant_validation_signed_bias": 6.073505303971504,
    "position": "RB",
    "target_name": "fantasy_points_total",
    "test_mae": 46.48574953734089,
    "test_rows": 294,
    "test_season": 2025,
    "validation_mae": 45.68746765164051,
    "validation_rows": 1488,
    "validation_seasons": [
      2020,
      2021,
      2022,
      2023,
      2024
    ],
    "validation_top_n_capture_rate": 0.6
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
      "empirical_coverage_p10_p90": 0.7687074829931972,
      "evaluation_scope": "test",
      "mean_interval_width_p10_p90": 77.51706770654918,
      "pinball_loss_p10": 7.335130043032719,
      "pinball_loss_p50": 13.582666328283205,
      "pinball_loss_p90": 9.155528346478967,
      "position": "RB",
      "prediction_season": 2025,
      "projection_tier": "all",
      "rows": 294,
      "target_name": "fantasy_points_total"
    },
    {
      "candidate_name": "ridge",
      "empirical_coverage_p10_p90": 0.2972972972972973,
      "evaluation_scope": "test",
      "mean_interval_width_p10_p90": 77.51706770654918,
      "pinball_loss_p10": 18.71806087605856,
      "pinball_loss_p50": 31.928865296673333,
      "pinball_loss_p90": 19.72734020562038,
      "position": "RB",
      "prediction_season": 2025,
      "projection_tier": "top",
      "rows": 74,
      "target_name": "fantasy_points_total"
    },
    {
      "candidate_name": "ridge",
      "empirical_coverage_p10_p90": 0.8904109589041096,
      "evaluation_scope": "test",
      "mean_interval_width_p10_p90": 77.51706770654918,
      "pinball_loss_p10": 3.0852487182117434,
      "pinball_loss_p50": 9.278187369242097,
      "pinball_loss_p90": 6.7069950177042195,
      "position": "RB",
      "prediction_season": 2025,
      "projection_tier": "middle",
      "rows": 146,
      "target_name": "fantasy_points_total"
    },
    {
      "candidate_name": "ridge",
      "empirical_coverage_p10_p90": 1.0,
      "evaluation_scope": "test",
      "mean_interval_width_p10_p90": 77.51706770654917,
      "pinball_loss_p10": 4.337100202221236,
      "pinball_loss_p50": 3.729088008812022,
      "pinball_loss_p90": 3.4146065684336824,
      "position": "RB",
      "prediction_season": 2025,
      "projection_tier": "lower",
      "rows": 74,
      "target_name": "fantasy_points_total"
    },
    {
      "candidate_name": "ridge",
      "empirical_coverage_p10_p90": 0.8211920529801324,
      "evaluation_scope": "validation",
      "mean_interval_width_p10_p90": 93.31589549661052,
      "pinball_loss_p10": 8.66728569662266,
      "pinball_loss_p50": 13.738291078760435,
      "pinball_loss_p90": 8.317472061024564,
      "position": "RB",
      "prediction_season": 2020,
      "projection_tier": "all",
      "rows": 302,
      "target_name": "fantasy_points_total"
    },
    {
      "candidate_name": "ridge",
      "empirical_coverage_p10_p90": 0.42105263157894735,
      "evaluation_scope": "validation",
      "mean_interval_width_p10_p90": 93.31589549661052,
      "pinball_loss_p10": 18.677864240205107,
      "pinball_loss_p50": 30.287460381650966,
      "pinball_loss_p90": 15.635407554171435,
      "position": "RB",
      "prediction_season": 2020,
      "projection_tier": "top",
      "rows": 76,
      "target_name": "fantasy_points_total"
    },
    {
      "candidate_name": "ridge",
      "empirical_coverage_p10_p90": 0.9533333333333334,
      "evaluation_scope": "validation",
      "mean_interval_width_p10_p90": 93.31589549661052,
      "pinball_loss_p10": 4.643648243895169,
      "pinball_loss_p50": 7.9321693017367005,
      "pinball_loss_p90": 7.285761615329354,
      "position": "RB",
      "prediction_season": 2020,
      "projection_tier": "middle",
      "rows": 150,
      "target_name": "fantasy_points_total"
    },
    {
      "candidate_name": "ridge",
      "empirical_coverage_p10_p90": 0.9605263157894737,
      "evaluation_scope": "validation",
      "mean_interval_width_p10_p90": 93.31589549661052,
      "pinball_loss_p10": 6.598096862370782,
      "pinball_loss_p50": 8.648572651574645,
      "pinball_loss_p90": 3.0358071843813947,
      "position": "RB",
      "prediction_season": 2020,
      "projection_tier": "lower",
      "rows": 76,
      "target_name": "fantasy_points_total"
    },
    {
      "candidate_name": "ridge",
      "empirical_coverage_p10_p90": 0.8079470198675497,
      "evaluation_scope": "validation",
      "mean_interval_width_p10_p90": 91.04886349967056,
      "pinball_loss_p10": 6.909018344419721,
      "pinball_loss_p50": 14.14517109129887,
      "pinball_loss_p90": 9.408649258256313,
      "position": "RB",
      "prediction_season": 2021,
      "projection_tier": "all",
      "rows": 302,
      "target_name": "fantasy_points_total"
    },
    {
      "candidate_name": "ridge",
      "empirical_coverage_p10_p90": 0.4473684210526316,
      "evaluation_scope": "validation",
      "mean_interval_width_p10_p90": 91.04886349967057,
      "pinball_loss_p10": 11.599390374799576,
      "pinball_loss_p50": 28.230677338633505,
      "pinball_loss_p90": 18.362558551656008,
      "position": "RB",
      "prediction_season": 2021,
      "projection_tier": "top",
      "rows": 76,
      "target_name": "fantasy_points_total"
    },
    {
      "candidate_name": "ridge",
      "empirical_coverage_p10_p90": 0.9133333333333333,
      "evaluation_scope": "validation",
      "mean_interval_width_p10_p90": 91.04886349967057,
      "pinball_loss_p10": 4.693581184735166,
      "pinball_loss_p50": 9.378144512022427,
      "pinball_loss_p90": 7.298565697547298,
      "position": "RB",
      "prediction_season": 2021,
      "projection_tier": "middle",
      "rows": 150,
      "target_name": "fantasy_points_total"
    },
    {
      "candidate_name": "ridge",
      "empirical_coverage_p10_p90": 0.9605263157894737,
      "evaluation_scope": "validation",
      "mean_interval_width_p10_p90": 91.04886349967057,
      "pinball_loss_p10": 6.5912196555225435,
      "pinball_loss_p50": 9.468269934641441,
      "pinball_loss_p90": 4.619378571519151,
      "position": "RB",
      "prediction_season": 2021,
      "projection_tier": "lower",
      "rows": 76,
      "target_name": "fantasy_points_total"
    },
    {
      "candidate_name": "ridge",
      "empirical_coverage_p10_p90": 0.8316498316498316,
      "evaluation_scope": "validation",
      "mean_interval_width_p10_p90": 86.8361691605466,
      "pinball_loss_p10": 6.80611684797363,
      "pinball_loss_p50": 13.603727745299432,
      "pinball_loss_p90": 9.630840572935812,
      "position": "RB",
      "prediction_season": 2022,
      "projection_tier": "all",
      "rows": 297,
      "target_name": "fantasy_points_total"
    },
    {
      "candidate_name": "ridge",
      "empirical_coverage_p10_p90": 0.4594594594594595,
      "evaluation_scope": "validation",
      "mean_interval_width_p10_p90": 86.83616916054659,
      "pinball_loss_p10": 14.152884222221418,
      "pinball_loss_p50": 29.986058153187262,
      "pinball_loss_p90": 19.81822395325867,
      "position": "RB",
      "prediction_season": 2022,
      "projection_tier": "top",
      "rows": 74,
      "target_name": "fantasy_points_total"
    },
    {
      "candidate_name": "ridge",
      "empirical_coverage_p10_p90": 0.9328859060402684,
      "evaluation_scope": "validation",
      "mean_interval_width_p10_p90": 86.83616916054662,
      "pinball_loss_p10": 3.868522955073837,
      "pinball_loss_p50": 9.485191465236491,
      "pinball_loss_p90": 7.710850851882756,
      "position": "RB",
      "prediction_season": 2022,
      "projection_tier": "middle",
      "rows": 149,
      "target_name": "fantasy_points_total"
    },
    {
      "candidate_name": "ridge",
      "empirical_coverage_p10_p90": 1.0,
      "evaluation_scope": "validation",
      "mean_interval_width_p10_p90": 86.83616916054662,
      "pinball_loss_p10": 5.374234474294341,
      "pinball_loss_p50": 5.514125793214016,
      "pinball_loss_p90": 3.3093824417603175,
      "position": "RB",
      "prediction_season": 2022,
      "projection_tier": "lower",
      "rows": 74,
      "target_name": "fantasy_points_total"
    },
    {
      "candidate_name": "ridge",
      "empirical_coverage_p10_p90": 0.8116438356164384,
      "evaluation_scope": "validation",
      "mean_interval_width_p10_p90": 82.43017837216645,
      "pinball_loss_p10": 6.865110332512386,
      "pinball_loss_p50": 13.332520955529267,
      "pinball_loss_p90": 9.848642654405806,
      "position": "RB",
      "prediction_season": 2023,
      "projection_tier": "all",
      "rows": 292,
      "target_name": "fantasy_points_total"
    },
    {
      "candidate_name": "ridge",
      "empirical_coverage_p10_p90": 0.3561643835616438,
      "evaluation_scope": "validation",
      "mean_interval_width_p10_p90": 82.43017837216647,
      "pinball_loss_p10": 16.079469879675294,
      "pinball_loss_p50": 31.180364691289732,
      "pinball_loss_p90": 20.8755159187004,
      "position": "RB",
      "prediction_season": 2023,
      "projection_tier": "top",
      "rows": 73,
      "target_name": "fantasy_points_total"
    },
    {
      "candidate_name": "ridge",
      "empirical_coverage_p10_p90": 0.9452054794520548,
      "evaluation_scope": "validation",
      "mean_interval_width_p10_p90": 82.43017837216645,
      "pinball_loss_p10": 3.314798805453588,
      "pinball_loss_p50": 9.332363892993584,
      "pinball_loss_p90": 7.513705350586624,
      "position": "RB",
      "prediction_season": 2023,
      "projection_tier": "middle",
      "rows": 146,
      "target_name": "fantasy_points_total"
    },
    {
      "candidate_name": "ridge",
      "empirical_coverage_p10_p90": 1.0,
      "evaluation_scope": "validation",
      "mean_interval_width_p10_p90": 82.43017837216645,
      "pinball_loss_p10": 4.751373839467075,
      "pinball_loss_p50": 3.484991344840164,
      "pinball_loss_p90": 3.491643997749572,
      "position": "RB",
      "prediction_season": 2023,
      "projection_tier": "lower",
      "rows": 73,
      "target_name": "fantasy_points_total"
    },
    {
      "candidate_name": "ridge",
      "empirical_coverage_p10_p90": 0.8033898305084746,
      "evaluation_scope": "validation",
      "mean_interval_width_p10_p90": 79.03878548898354,
      "pinball_loss_p10": 6.435083583438519,
      "pinball_loss_p50": 12.829074822866163,
      "pinball_loss_p90": 9.90329215567678,
      "position": "RB",
      "prediction_season": 2024,
      "projection_tier": "all",
      "rows": 295,
      "target_name": "fantasy_points_total"
    },
    {
      "candidate_name": "ridge",
      "empirical_coverage_p10_p90": 0.35135135135135137,
      "evaluation_scope": "validation",
      "mean_interval_width_p10_p90": 79.03878548898354,
      "pinball_loss_p10": 13.414950128054908,
      "pinball_loss_p50": 31.07064293868623,
      "pinball_loss_p90": 24.136404875007084,
      "position": "RB",
      "prediction_season": 2024,
      "projection_tier": "top",
      "rows": 74,
      "target_name": "fantasy_points_total"
    },
    {
      "candidate_name": "ridge",
      "empirical_coverage_p10_p90": 0.9523809523809523,
      "evaluation_scope": "validation",
      "mean_interval_width_p10_p90": 79.03878548898354,
      "pinball_loss_p10": 3.5117812104430612,
      "pinball_loss_p50": 6.75855487909269,
      "pinball_loss_p90": 5.919900746043414,
      "position": "RB",
      "prediction_season": 2024,
      "projection_tier": "middle",
      "rows": 147,
      "target_name": "fantasy_points_total"
    },
    {
      "candidate_name": "ridge",
      "empirical_coverage_p10_p90": 0.9594594594594594,
      "evaluation_scope": "validation",
      "mean_interval_width_p10_p90": 79.03878548898354,
      "pinball_loss_p10": 5.262317698691486,
      "pinball_loss_p50": 6.646512541298802,
      "pinball_loss_p90": 3.583132641969511,
      "position": "RB",
      "prediction_season": 2024,
      "projection_tier": "lower",
      "rows": 74,
      "target_name": "fantasy_points_total"
    }
  ],
  "empirical_not_guaranteed": true,
  "method": "training-only signed out-of-fold residual quantiles",
  "operational_center": "training_only_residual_adjusted_p50",
  "residual_rows": 881,
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
      "absolute_importance": 23.904128193953618,
      "coefficient": 23.904128193953618,
      "direction": "positive",
      "feature": "numeric__lag1_fantasy_points_total",
      "rank": 1
    },
    {
      "absolute_importance": 18.678955294537733,
      "coefficient": 18.678955294537733,
      "direction": "positive",
      "feature": "numeric__weighted_3yr_rushing_yards_per_game",
      "rank": 2
    },
    {
      "absolute_importance": 16.22754557603642,
      "coefficient": -16.22754557603642,
      "direction": "negative",
      "feature": "categorical__previous_team_HOU",
      "rank": 3
    },
    {
      "absolute_importance": 15.530168132725745,
      "coefficient": -15.530168132725745,
      "direction": "negative",
      "feature": "categorical__previous_team_NYJ",
      "rank": 4
    },
    {
      "absolute_importance": 13.865275679866977,
      "coefficient": 13.865275679866977,
      "direction": "positive",
      "feature": "categorical__previous_team_CIN",
      "rank": 5
    },
    {
      "absolute_importance": 13.043225500470196,
      "coefficient": -13.043225500470196,
      "direction": "negative",
      "feature": "numeric__weighted_3yr_carries_per_game",
      "rank": 6
    },
    {
      "absolute_importance": 12.005256732289695,
      "coefficient": -12.005256732289695,
      "direction": "negative",
      "feature": "categorical__previous_team_BAL",
      "rank": 7
    },
    {
      "absolute_importance": 9.903246008227429,
      "coefficient": 9.903246008227429,
      "direction": "positive",
      "feature": "numeric__lag1_fantasy_points_per_game",
      "rank": 8
    },
    {
      "absolute_importance": 9.237922043069682,
      "coefficient": 9.237922043069682,
      "direction": "positive",
      "feature": "categorical__previous_team_LA",
      "rank": 9
    },
    {
      "absolute_importance": 7.835677720031485,
      "coefficient": -7.835677720031485,
      "direction": "negative",
      "feature": "categorical__previous_team_KC",
      "rank": 10
    },
    {
      "absolute_importance": 7.83356893964729,
      "coefficient": 7.83356893964729,
      "direction": "positive",
      "feature": "categorical__previous_team_DAL",
      "rank": 11
    },
    {
      "absolute_importance": 7.751262533870352,
      "coefficient": -7.751262533870352,
      "direction": "negative",
      "feature": "categorical__previous_team_WAS",
      "rank": 12
    },
    {
      "absolute_importance": 7.448375147387127,
      "coefficient": 7.448375147387127,
      "direction": "positive",
      "feature": "numeric__weighted_3yr_fantasy_points_per_game",
      "rank": 13
    },
    {
      "absolute_importance": 7.279623578908902,
      "coefficient": 7.279623578908902,
      "direction": "positive",
      "feature": "categorical__previous_team_MIA",
      "rank": 14
    },
    {
      "absolute_importance": 7.250702549895668,
      "coefficient": -7.250702549895668,
      "direction": "negative",
      "feature": "categorical__previous_team_SD",
      "rank": 15
    },
    {
      "absolute_importance": 7.02615609367857,
      "coefficient": 7.02615609367857,
      "direction": "positive",
      "feature": "categorical__previous_team_CLE",
      "rank": 16
    },
    {
      "absolute_importance": 6.828892126546103,
      "coefficient": -6.828892126546103,
      "direction": "negative",
      "feature": "categorical__previous_team_DEN",
      "rank": 17
    },
    {
      "absolute_importance": 6.7339073051608285,
      "coefficient": -6.7339073051608285,
      "direction": "negative",
      "feature": "numeric__draft_pick",
      "rank": 18
    },
    {
      "absolute_importance": 6.562609799604833,
      "coefficient": 6.562609799604833,
      "direction": "positive",
      "feature": "categorical__previous_team_GB",
      "rank": 19
    },
    {
      "absolute_importance": 6.3800983393435,
      "coefficient": 6.3800983393435,
      "direction": "positive",
      "feature": "categorical__previous_team_NE",
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

- Project-relative path: `models/artifacts/phase4-052d2866899a665a44f3/attempt-331cdaf7eb7f4721aa43c08d469288ee/RB/fantasy_points_total/ridge.joblib`
- SHA-256: `3e32bca2aa6677a6c41b299a9d752ad9297322b1cd2c02817a2058d5e2bf995b`

## Additional metadata

````json
{
  "publication_id": "attempt-331cdaf7eb7f4721aa43c08d469288ee"
}
````
