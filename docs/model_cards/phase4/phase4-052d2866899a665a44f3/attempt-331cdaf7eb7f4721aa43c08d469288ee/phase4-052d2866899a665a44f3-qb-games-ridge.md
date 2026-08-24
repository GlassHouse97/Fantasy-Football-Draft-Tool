# Model Card: phase4-052d2866899a665a44f3-qb-games-ridge

- Model ID: `phase4-052d2866899a665a44f3-qb-games-ridge`
- Trained at: 2026-08-24T20:21:18+00:00
- Target: `games_active`
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
  "draft_relevant_validation_mae": 3.2952458850450657,
  "draft_relevant_validation_rows": 60,
  "draft_relevant_validation_signed_bias": 0.6092600626048575,
  "position": "QB",
  "target_name": "games_active",
  "test_mae": 2.3020450399858463,
  "test_rows": 124,
  "test_season": 2025,
  "validation_mae": 2.4478198187561544,
  "validation_rows": 618,
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
    "candidate_mae": 3.2952458850450657,
    "ci95_lower": -0.5389312026360755,
    "ci95_upper": 0.6422013665597243,
    "direction": "uncertain",
    "mae_difference_candidate_minus_reference": 0.07057599954098936,
    "n_resamples": 2000,
    "reference_mae": 3.2246698855040763,
    "rows": 60,
    "seed": 42
  },
  "decision_status": "learned_draft_relevant_regression_baseline_retained",
  "learned_improvement_status": "regression",
  "reference_metrics": {
    "candidate_name": "previous_season",
    "candidate_source": "baseline",
    "draft_relevant_validation_mae": 3.2246698855040763,
    "draft_relevant_validation_rows": 60,
    "draft_relevant_validation_signed_bias": 2.324669885504076,
    "position": "QB",
    "target_name": "games_active",
    "test_mae": 5.331053491220906,
    "test_rows": 124,
    "test_season": 2025,
    "validation_mae": 5.055845042910461,
    "validation_rows": 618,
    "validation_seasons": [
      2020,
      2021,
      2022,
      2023,
      2024
    ],
    "validation_top_n_capture_rate": null
  },
  "selected_champion": "previous_season",
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
      "empirical_coverage_p10_p90": 0.8225806451612904,
      "evaluation_scope": "test",
      "mean_interval_width_p10_p90": 6.790829897541497,
      "pinball_loss_p10": 0.4751120497085659,
      "pinball_loss_p50": 1.1510225199929232,
      "pinball_loss_p90": 0.6157836091143911,
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
      "mean_interval_width_p10_p90": 8.28430833662065,
      "pinball_loss_p10": 1.2553538456121918,
      "pinball_loss_p50": 2.2226585164978383,
      "pinball_loss_p90": 0.7213690522878082,
      "position": "QB",
      "prediction_season": 2025,
      "projection_tier": "top",
      "rows": 31,
      "target_name": "games_active"
    },
    {
      "candidate_name": "ridge",
      "empirical_coverage_p10_p90": 0.8709677419354839,
      "evaluation_scope": "test",
      "mean_interval_width_p10_p90": 7.432899543004612,
      "pinball_loss_p10": 0.3160955637078102,
      "pinball_loss_p50": 1.1521577617251297,
      "pinball_loss_p90": 0.6766736966112988,
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
      "mean_interval_width_p10_p90": 4.013212167536107,
      "pinball_loss_p10": 0.012903225806451613,
      "pinball_loss_p50": 0.07711604002359589,
      "pinball_loss_p90": 0.38841799094715906,
      "position": "QB",
      "prediction_season": 2025,
      "projection_tier": "lower",
      "rows": 31,
      "target_name": "games_active"
    },
    {
      "candidate_name": "ridge",
      "empirical_coverage_p10_p90": 0.8067226890756303,
      "evaluation_scope": "validation",
      "mean_interval_width_p10_p90": 5.911726379059946,
      "pinball_loss_p10": 0.40254453246465044,
      "pinball_loss_p50": 1.1310400255369342,
      "pinball_loss_p90": 0.6301580650935406,
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
      "mean_interval_width_p10_p90": 8.8463795300857,
      "pinball_loss_p10": 1.004171478322767,
      "pinball_loss_p50": 1.8574236283372192,
      "pinball_loss_p90": 0.5649047626000974,
      "position": "QB",
      "prediction_season": 2020,
      "projection_tier": "top",
      "rows": 30,
      "target_name": "games_active"
    },
    {
      "candidate_name": "ridge",
      "empirical_coverage_p10_p90": 0.7627118644067796,
      "evaluation_scope": "validation",
      "mean_interval_width_p10_p90": 5.8307541519291295,
      "pinball_loss_p10": 0.2894517798917017,
      "pinball_loss_p50": 1.277475494725061,
      "pinball_loss_p90": 0.83614764481278,
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
      "mean_interval_width_p10_p90": 3.1363186080581347,
      "pinball_loss_p10": 0.02333333333333333,
      "pinball_loss_p50": 0.11666666666666667,
      "pinball_loss_p90": 0.2902985274724801,
      "position": "QB",
      "prediction_season": 2020,
      "projection_tier": "lower",
      "rows": 30,
      "target_name": "games_active"
    },
    {
      "candidate_name": "ridge",
      "empirical_coverage_p10_p90": 0.8,
      "evaluation_scope": "validation",
      "mean_interval_width_p10_p90": 6.427499653660741,
      "pinball_loss_p10": 0.518346046419476,
      "pinball_loss_p50": 1.2322641153386278,
      "pinball_loss_p90": 0.6226257132959764,
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
      "mean_interval_width_p10_p90": 7.856155687632118,
      "pinball_loss_p10": 1.2594459826955056,
      "pinball_loss_p50": 1.913150146085535,
      "pinball_loss_p90": 0.537838563761737,
      "position": "QB",
      "prediction_season": 2021,
      "projection_tier": "top",
      "rows": 31,
      "target_name": "games_active"
    },
    {
      "candidate_name": "ridge",
      "empirical_coverage_p10_p90": 0.8095238095238095,
      "evaluation_scope": "validation",
      "mean_interval_width_p10_p90": 7.052177752942145,
      "pinball_loss_p10": 0.38651476728371165,
      "pinball_loss_p50": 1.3884920223152886,
      "pinball_loss_p90": 0.7510992013253791,
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
      "mean_interval_width_p10_p90": 3.729336514698119,
      "pinball_loss_p10": 0.04516129032258065,
      "pinball_loss_p50": 0.23388266073592617,
      "pinball_loss_p90": 0.44632158070594674,
      "position": "QB",
      "prediction_season": 2021,
      "projection_tier": "lower",
      "rows": 31,
      "target_name": "games_active"
    },
    {
      "candidate_name": "ridge",
      "empirical_coverage_p10_p90": 0.8,
      "evaluation_scope": "validation",
      "mean_interval_width_p10_p90": 6.677420561872804,
      "pinball_loss_p10": 0.41537027169605045,
      "pinball_loss_p50": 1.158942337919882,
      "pinball_loss_p90": 0.6843688337555797,
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
      "mean_interval_width_p10_p90": 8.098975144406293,
      "pinball_loss_p10": 0.807528376003205,
      "pinball_loss_p50": 1.5666418803217204,
      "pinball_loss_p90": 0.6052861814719303,
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
      "mean_interval_width_p10_p90": 7.243312800308256,
      "pinball_loss_p10": 0.4077445127921737,
      "pinball_loss_p50": 1.3658439323006035,
      "pinball_loss_p90": 0.8223086480328825,
      "position": "QB",
      "prediction_season": 2022,
      "projection_tier": "middle",
      "rows": 63,
      "target_name": "games_active"
    },
    {
      "candidate_name": "ridge",
      "empirical_coverage_p10_p90": 0.9354838709677419,
      "evaluation_scope": "validation",
      "mean_interval_width_p10_p90": 4.105826914131794,
      "pinball_loss_p10": 0.03870967741935485,
      "pinball_loss_p50": 0.3307653617765776,
      "pinball_loss_p90": 0.4831221860563231,
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
      "mean_interval_width_p10_p90": 6.750358100658893,
      "pinball_loss_p10": 0.512639707079697,
      "pinball_loss_p50": 1.355460982578195,
      "pinball_loss_p90": 0.8087771774027914,
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
      "mean_interval_width_p10_p90": 8.042555371285339,
      "pinball_loss_p10": 1.251484473399763,
      "pinball_loss_p50": 2.099337523707306,
      "pinball_loss_p90": 0.7199576002343716,
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
      "mean_interval_width_p10_p90": 7.3560872956941115,
      "pinball_loss_p10": 0.37373072584660927,
      "pinball_loss_p50": 1.508466419692759,
      "pinball_loss_p90": 1.0394516130975513,
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
      "mean_interval_width_p10_p90": 4.246702439962018,
      "pinball_loss_p10": 0.05161290322580645,
      "pinball_loss_p50": 0.3055735672199561,
      "pinball_loss_p90": 0.4362478831816921,
      "position": "QB",
      "prediction_season": 2023,
      "projection_tier": "lower",
      "rows": 31,
      "target_name": "games_active"
    },
    {
      "candidate_name": "ridge",
      "empirical_coverage_p10_p90": 0.792,
      "evaluation_scope": "validation",
      "mean_interval_width_p10_p90": 6.7586687048236085,
      "pinball_loss_p10": 0.5062059582218601,
      "pinball_loss_p50": 1.2384367396779736,
      "pinball_loss_p90": 0.7205683449926894,
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
      "mean_interval_width_p10_p90": 8.282581967738158,
      "pinball_loss_p10": 1.0004465737215775,
      "pinball_loss_p50": 1.8172686096287882,
      "pinball_loss_p90": 0.6320965003112876,
      "position": "QB",
      "prediction_season": 2024,
      "projection_tier": "top",
      "rows": 31,
      "target_name": "games_active"
    },
    {
      "candidate_name": "ridge",
      "empirical_coverage_p10_p90": 0.7777777777777778,
      "evaluation_scope": "validation",
      "mean_interval_width_p10_p90": 7.296817873896787,
      "pinball_loss_p10": 0.4962206506724381,
      "pinball_loss_p50": 1.480096732516244,
      "pinball_loss_p90": 0.90792340660962,
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
      "mean_interval_width_p10_p90": 4.14109745314744,
      "pinball_loss_p10": 0.03225806451612904,
      "pinball_loss_p50": 0.16848940041067537,
      "pinball_loss_p90": 0.42828635477516774,
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
      "absolute_importance": 1.4493047550850724,
      "coefficient": -1.4493047550850724,
      "direction": "negative",
      "feature": "numeric__weighted_3yr_passing_attempts_per_game",
      "rank": 1
    },
    {
      "absolute_importance": 1.4437315482932702,
      "coefficient": -1.4437315482932702,
      "direction": "negative",
      "feature": "categorical__previous_team_IND",
      "rank": 2
    },
    {
      "absolute_importance": 1.4275096900912922,
      "coefficient": 1.4275096900912922,
      "direction": "positive",
      "feature": "categorical__previous_team_NE",
      "rank": 3
    },
    {
      "absolute_importance": 1.3657164696397275,
      "coefficient": 1.3657164696397275,
      "direction": "positive",
      "feature": "categorical__previous_team_SD",
      "rank": 4
    },
    {
      "absolute_importance": 1.3342412286198249,
      "coefficient": 1.3342412286198249,
      "direction": "positive",
      "feature": "numeric__weighted_3yr_passing_yards_per_game",
      "rank": 5
    },
    {
      "absolute_importance": 1.1586888603078835,
      "coefficient": 1.1586888603078835,
      "direction": "positive",
      "feature": "categorical__previous_team_LA",
      "rank": 6
    },
    {
      "absolute_importance": 1.1274870958296195,
      "coefficient": -1.1274870958296195,
      "direction": "negative",
      "feature": "categorical__previous_team_ARI",
      "rank": 7
    },
    {
      "absolute_importance": 1.098408060105568,
      "coefficient": -1.098408060105568,
      "direction": "negative",
      "feature": "numeric__age_at_cutoff",
      "rank": 8
    },
    {
      "absolute_importance": 1.089019631545298,
      "coefficient": -1.089019631545298,
      "direction": "negative",
      "feature": "categorical__previous_team_MIA",
      "rank": 9
    },
    {
      "absolute_importance": 0.9969382469946304,
      "coefficient": 0.9969382469946304,
      "direction": "positive",
      "feature": "categorical__previous_team_SEA",
      "rank": 10
    },
    {
      "absolute_importance": 0.9818468642765332,
      "coefficient": -0.9818468642765332,
      "direction": "negative",
      "feature": "categorical__previous_team_CLE",
      "rank": 11
    },
    {
      "absolute_importance": 0.8738241243481969,
      "coefficient": 0.8738241243481969,
      "direction": "positive",
      "feature": "numeric__lag1_fantasy_points_per_game",
      "rank": 12
    },
    {
      "absolute_importance": 0.8715033670613589,
      "coefficient": -0.8715033670613589,
      "direction": "negative",
      "feature": "categorical__previous_team_WAS",
      "rank": 13
    },
    {
      "absolute_importance": 0.8507346936416225,
      "coefficient": 0.8507346936416225,
      "direction": "positive",
      "feature": "categorical__previous_team_CAR",
      "rank": 14
    },
    {
      "absolute_importance": 0.8465519827042941,
      "coefficient": 0.8465519827042941,
      "direction": "positive",
      "feature": "numeric__lag1_games_active",
      "rank": 15
    },
    {
      "absolute_importance": 0.807794290554613,
      "coefficient": -0.807794290554613,
      "direction": "negative",
      "feature": "categorical__previous_team_SF",
      "rank": 16
    },
    {
      "absolute_importance": 0.7975642297980841,
      "coefficient": 0.7975642297980841,
      "direction": "positive",
      "feature": "numeric__weighted_3yr_fantasy_points_per_game",
      "rank": 17
    },
    {
      "absolute_importance": 0.7400786147854636,
      "coefficient": 0.7400786147854636,
      "direction": "positive",
      "feature": "numeric__weighted_3yr_games_active",
      "rank": 18
    },
    {
      "absolute_importance": 0.7289201193466176,
      "coefficient": 0.7289201193466176,
      "direction": "positive",
      "feature": "categorical__previous_team_PHI",
      "rank": 19
    },
    {
      "absolute_importance": 0.7169626626244392,
      "coefficient": -0.7169626626244392,
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

- Project-relative path: `models/artifacts/phase4-052d2866899a665a44f3/attempt-331cdaf7eb7f4721aa43c08d469288ee/QB/games_active/ridge.joblib`
- SHA-256: `6d9564bad778a90391641773b6a65566420a505bb3559adde9dbf953d03516d2`

## Additional metadata

````json
{
  "publication_id": "attempt-331cdaf7eb7f4721aa43c08d469288ee"
}
````
