# Model Card: phase4-052d2866899a665a44f3-qb-total-ridge

- Model ID: `phase4-052d2866899a665a44f3-qb-total-ridge`
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
  "draft_relevant_validation_mae": 78.35438168370483,
  "draft_relevant_validation_rows": 60,
  "draft_relevant_validation_signed_bias": 0.6214016043880705,
  "position": "QB",
  "target_name": "fantasy_points_total",
  "test_mae": 43.50698855862558,
  "test_rows": 124,
  "test_season": 2025,
  "validation_mae": 45.30720637828314,
  "validation_rows": 618,
  "validation_seasons": [
    2020,
    2021,
    2022,
    2023,
    2024
  ],
  "validation_top_n_capture_rate": 0.55
}
````

## Comparison with transparent baselines

````json
{
  "best_learned_vs_baseline_bootstrap": {
    "candidate_mae": 78.35438168370483,
    "ci95_lower": -19.49038732738462,
    "ci95_upper": 9.418170216787768,
    "direction": "uncertain",
    "mae_difference_candidate_minus_reference": -4.808300526609287,
    "n_resamples": 2000,
    "reference_mae": 83.16268221031412,
    "rows": 60,
    "seed": 42
  },
  "decision_status": "learned_draft_relevant_improvement_inconclusive_baseline_retained",
  "learned_improvement_status": "inconclusive",
  "reference_metrics": {
    "candidate_name": "previous_season",
    "candidate_source": "baseline",
    "draft_relevant_validation_mae": 83.16268221031412,
    "draft_relevant_validation_rows": 60,
    "draft_relevant_validation_signed_bias": 49.59354330977318,
    "position": "QB",
    "target_name": "fantasy_points_total",
    "test_mae": 68.47771658869458,
    "test_rows": 124,
    "test_season": 2025,
    "validation_mae": 64.75177486415684,
    "validation_rows": 618,
    "validation_seasons": [
      2020,
      2021,
      2022,
      2023,
      2024
    ],
    "validation_top_n_capture_rate": 0.6
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
      "mean_interval_width_p10_p90": 145.97139728688146,
      "pinball_loss_p10": 11.7162943211777,
      "pinball_loss_p50": 21.75349427931279,
      "pinball_loss_p90": 12.686474967995432,
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
      "mean_interval_width_p10_p90": 145.9713972868814,
      "pinball_loss_p10": 22.850483572949006,
      "pinball_loss_p50": 42.983868955713014,
      "pinball_loss_p90": 23.798034709871562,
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
      "mean_interval_width_p10_p90": 145.97139728688143,
      "pinball_loss_p10": 7.383266747259417,
      "pinball_loss_p50": 16.37752175382594,
      "pinball_loss_p90": 10.799442825332491,
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
      "mean_interval_width_p10_p90": 145.9713972868814,
      "pinball_loss_p10": 9.248160217242964,
      "pinball_loss_p50": 11.275064653886268,
      "pinball_loss_p90": 5.348979511445178,
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
      "mean_interval_width_p10_p90": 155.440227930882,
      "pinball_loss_p10": 11.998857402042413,
      "pinball_loss_p50": 23.291571729565295,
      "pinball_loss_p90": 13.516340629552806,
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
      "mean_interval_width_p10_p90": 155.44022793088212,
      "pinball_loss_p10": 23.691481064516566,
      "pinball_loss_p50": 43.2029429490195,
      "pinball_loss_p90": 20.029969421449696,
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
      "mean_interval_width_p10_p90": 155.4402279308821,
      "pinball_loss_p10": 7.272637232842675,
      "pinball_loss_p50": 18.938772336075353,
      "pinball_loss_p90": 14.05523340085558,
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
      "mean_interval_width_p10_p90": 155.44022793088212,
      "pinball_loss_p10": 9.601133405661074,
      "pinball_loss_p50": 11.94070598397468,
      "pinball_loss_p90": 5.942889387427134,
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
      "mean_interval_width_p10_p90": 155.88871887993716,
      "pinball_loss_p10": 14.28089106148407,
      "pinball_loss_p50": 23.600627253118695,
      "pinball_loss_p90": 13.029844232738364,
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
      "mean_interval_width_p10_p90": 155.88871887993713,
      "pinball_loss_p10": 33.39084745372285,
      "pinball_loss_p50": 41.91158882968344,
      "pinball_loss_p90": 14.926687836034285,
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
      "mean_interval_width_p10_p90": 155.888718879937,
      "pinball_loss_p10": 7.992082426923707,
      "pinball_loss_p50": 22.57795116457455,
      "pinball_loss_p90": 14.401514967660143,
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
      "mean_interval_width_p10_p90": 155.88871887993713,
      "pinball_loss_p10": 7.95141673302925,
      "pinball_loss_p50": 7.368007404885604,
      "pinball_loss_p90": 8.345411716536887,
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
      "mean_interval_width_p10_p90": 149.4905750701458,
      "pinball_loss_p10": 10.375645199811041,
      "pinball_loss_p50": 20.83343523844539,
      "pinball_loss_p90": 12.909195253952628,
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
      "mean_interval_width_p10_p90": 149.4905750701457,
      "pinball_loss_p10": 15.37232492830544,
      "pinball_loss_p50": 34.63832670212988,
      "pinball_loss_p90": 14.684345769541375,
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
      "mean_interval_width_p10_p90": 149.4905750701457,
      "pinball_loss_p10": 8.959364790111989,
      "pinball_loss_p50": 20.942626531262988,
      "pinball_loss_p90": 15.09503969194762,
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
      "mean_interval_width_p10_p90": 149.49057507014567,
      "pinball_loss_p10": 8.257212755543748,
      "pinball_loss_p50": 6.806638889357383,
      "pinball_loss_p90": 6.691844751470825,
      "position": "QB",
      "prediction_season": 2022,
      "projection_tier": "lower",
      "rows": 31,
      "target_name": "fantasy_points_total"
    },
    {
      "candidate_name": "ridge",
      "empirical_coverage_p10_p90": 0.8064516129032258,
      "evaluation_scope": "validation",
      "mean_interval_width_p10_p90": 150.01276517182765,
      "pinball_loss_p10": 12.175491601897782,
      "pinball_loss_p50": 23.862837895413186,
      "pinball_loss_p90": 14.169306132071764,
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
      "mean_interval_width_p10_p90": 150.01276517182762,
      "pinball_loss_p10": 24.36715071368872,
      "pinball_loss_p50": 43.80711579016308,
      "pinball_loss_p90": 21.284275053986274,
      "position": "QB",
      "prediction_season": 2023,
      "projection_tier": "top",
      "rows": 31,
      "target_name": "fantasy_points_total"
    },
    {
      "candidate_name": "ridge",
      "empirical_coverage_p10_p90": 0.8870967741935484,
      "evaluation_scope": "validation",
      "mean_interval_width_p10_p90": 150.0127651718277,
      "pinball_loss_p10": 7.292470956209457,
      "pinball_loss_p50": 18.666327445018716,
      "pinball_loss_p90": 15.070773369300753,
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
      "mean_interval_width_p10_p90": 150.01276517182765,
      "pinball_loss_p10": 9.749873781483503,
      "pinball_loss_p50": 14.311580901452224,
      "pinball_loss_p90": 5.251402735699259,
      "position": "QB",
      "prediction_season": 2023,
      "projection_tier": "lower",
      "rows": 31,
      "target_name": "fantasy_points_total"
    },
    {
      "candidate_name": "ridge",
      "empirical_coverage_p10_p90": 0.792,
      "evaluation_scope": "validation",
      "mean_interval_width_p10_p90": 141.7160359773991,
      "pinball_loss_p10": 11.52458949824036,
      "pinball_loss_p50": 21.71984019675579,
      "pinball_loss_p90": 14.354153529876134,
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
      "mean_interval_width_p10_p90": 141.71603597739903,
      "pinball_loss_p10": 20.8672772200392,
      "pinball_loss_p50": 38.232739728299045,
      "pinball_loss_p90": 22.133565209618574,
      "position": "QB",
      "prediction_season": 2024,
      "projection_tier": "top",
      "rows": 31,
      "target_name": "fantasy_points_total"
    },
    {
      "candidate_name": "ridge",
      "empirical_coverage_p10_p90": 0.8412698412698413,
      "evaluation_scope": "validation",
      "mean_interval_width_p10_p90": 141.71603597739906,
      "pinball_loss_p10": 7.723825827056837,
      "pinball_loss_p50": 16.583788870905202,
      "pinball_loss_p90": 12.184273409472176,
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
      "mean_interval_width_p10_p90": 141.71603597739903,
      "pinball_loss_p10": 9.906034398524179,
      "pinball_loss_p50": 15.64472239194114,
      "pinball_loss_p90": 10.98449822385788,
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
      "absolute_importance": 46.328333035369276,
      "coefficient": 46.328333035369276,
      "direction": "positive",
      "feature": "numeric__lag1_fantasy_points_total",
      "rank": 1
    },
    {
      "absolute_importance": 28.278132376986644,
      "coefficient": -28.278132376986644,
      "direction": "negative",
      "feature": "categorical__previous_team_IND",
      "rank": 2
    },
    {
      "absolute_importance": 22.989903537832177,
      "coefficient": -22.989903537832177,
      "direction": "negative",
      "feature": "numeric__weighted_3yr_passing_attempts_per_game",
      "rank": 3
    },
    {
      "absolute_importance": 22.549345693105906,
      "coefficient": 22.549345693105906,
      "direction": "positive",
      "feature": "categorical__previous_team_SEA",
      "rank": 4
    },
    {
      "absolute_importance": 21.515330766424768,
      "coefficient": 21.515330766424768,
      "direction": "positive",
      "feature": "categorical__previous_team_PHI",
      "rank": 5
    },
    {
      "absolute_importance": 21.486632993261257,
      "coefficient": 21.486632993261257,
      "direction": "positive",
      "feature": "numeric__weighted_3yr_passing_yards_per_game",
      "rank": 6
    },
    {
      "absolute_importance": 21.2147723263395,
      "coefficient": -21.2147723263395,
      "direction": "negative",
      "feature": "categorical__previous_team_CLE",
      "rank": 7
    },
    {
      "absolute_importance": 19.461153544335502,
      "coefficient": 19.461153544335502,
      "direction": "positive",
      "feature": "categorical__previous_team_NE",
      "rank": 8
    },
    {
      "absolute_importance": 19.40807062820399,
      "coefficient": 19.40807062820399,
      "direction": "positive",
      "feature": "categorical__previous_team_LA",
      "rank": 9
    },
    {
      "absolute_importance": 18.638716601962088,
      "coefficient": 18.638716601962088,
      "direction": "positive",
      "feature": "categorical__previous_team_KC",
      "rank": 10
    },
    {
      "absolute_importance": 18.276306836395865,
      "coefficient": -18.276306836395865,
      "direction": "negative",
      "feature": "numeric__age_at_cutoff",
      "rank": 11
    },
    {
      "absolute_importance": 16.86922059161593,
      "coefficient": 16.86922059161593,
      "direction": "positive",
      "feature": "categorical__previous_team_DET",
      "rank": 12
    },
    {
      "absolute_importance": 15.706158652729108,
      "coefficient": -15.706158652729108,
      "direction": "negative",
      "feature": "categorical__previous_team_ARI",
      "rank": 13
    },
    {
      "absolute_importance": 14.916004590637508,
      "coefficient": -14.916004590637508,
      "direction": "negative",
      "feature": "categorical__previous_team_PIT",
      "rank": 14
    },
    {
      "absolute_importance": 13.28859334472297,
      "coefficient": -13.28859334472297,
      "direction": "negative",
      "feature": "categorical__previous_team_WAS",
      "rank": 15
    },
    {
      "absolute_importance": 13.266663106692835,
      "coefficient": 13.266663106692835,
      "direction": "positive",
      "feature": "categorical__previous_team_LAC",
      "rank": 16
    },
    {
      "absolute_importance": 13.017701234875986,
      "coefficient": 13.017701234875986,
      "direction": "positive",
      "feature": "numeric__weighted_3yr_fantasy_points_per_game",
      "rank": 17
    },
    {
      "absolute_importance": 12.49631194503302,
      "coefficient": 12.49631194503302,
      "direction": "positive",
      "feature": "categorical__previous_team_BUF",
      "rank": 18
    },
    {
      "absolute_importance": 12.34424800356771,
      "coefficient": -12.34424800356771,
      "direction": "negative",
      "feature": "categorical__previous_team_HOU",
      "rank": 19
    },
    {
      "absolute_importance": 11.894403822944277,
      "coefficient": -11.894403822944277,
      "direction": "negative",
      "feature": "categorical__previous_team_MIA",
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

- Project-relative path: `models/artifacts/phase4-052d2866899a665a44f3/attempt-331cdaf7eb7f4721aa43c08d469288ee/QB/fantasy_points_total/ridge.joblib`
- SHA-256: `7d0b4928c6934aa9ff59f679d64c7970b999d2f7ea4de2f4cf0cf88b7a010787`

## Additional metadata

````json
{
  "publication_id": "attempt-331cdaf7eb7f4721aa43c08d469288ee"
}
````
