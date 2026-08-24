# Model Card: phase4-052d2866899a665a44f3-rb-ppg-ridge

- Model ID: `phase4-052d2866899a665a44f3-rb-ppg-ridge`
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
  "draft_relevant_validation_mae": 3.3544154406916347,
  "draft_relevant_validation_rows": 117,
  "draft_relevant_validation_signed_bias": -0.7999121356217198,
  "position": "RB",
  "target_name": "fantasy_points_per_game",
  "test_mae": 2.272795090337521,
  "test_rows": 128,
  "test_season": 2025,
  "validation_mae": 2.665996205720287,
  "validation_rows": 686,
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
    "candidate_mae": 3.3544154406916347,
    "ci95_lower": -0.5835155351276052,
    "ci95_upper": 0.085817698106291,
    "direction": "uncertain",
    "mae_difference_candidate_minus_reference": -0.2475744895149843,
    "n_resamples": 2000,
    "reference_mae": 3.601989930206619,
    "rows": 117,
    "seed": 42
  },
  "decision_status": "learned_draft_relevant_improvement_inconclusive_baseline_retained",
  "learned_improvement_status": "inconclusive",
  "reference_metrics": {
    "candidate_name": "position_shrinkage",
    "candidate_source": "baseline",
    "draft_relevant_validation_mae": 3.601989930206619,
    "draft_relevant_validation_rows": 117,
    "draft_relevant_validation_signed_bias": -0.043191251854455465,
    "position": "RB",
    "target_name": "fantasy_points_per_game",
    "test_mae": 2.720472586513103,
    "test_rows": 128,
    "test_season": 2025,
    "validation_mae": 2.8419226187686193,
    "validation_rows": 686,
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
      "empirical_coverage_p10_p90": 0.84375,
      "evaluation_scope": "test",
      "mean_interval_width_p10_p90": 8.746884086501954,
      "pinball_loss_p10": 0.5066802021869126,
      "pinball_loss_p50": 1.1363975451687605,
      "pinball_loss_p90": 0.6600777118210233,
      "position": "RB",
      "prediction_season": 2025,
      "projection_tier": "all",
      "rows": 128,
      "target_name": "fantasy_points_per_game"
    },
    {
      "candidate_name": "ridge",
      "empirical_coverage_p10_p90": 0.71875,
      "evaluation_scope": "test",
      "mean_interval_width_p10_p90": 8.746884086501957,
      "pinball_loss_p10": 0.6469860812305384,
      "pinball_loss_p50": 1.3784168776708001,
      "pinball_loss_p90": 0.7317729521134384,
      "position": "RB",
      "prediction_season": 2025,
      "projection_tier": "top",
      "rows": 64,
      "target_name": "fantasy_points_per_game"
    },
    {
      "candidate_name": "ridge",
      "empirical_coverage_p10_p90": 0.9555555555555556,
      "evaluation_scope": "test",
      "mean_interval_width_p10_p90": 8.746884086501957,
      "pinball_loss_p10": 0.3291230312446395,
      "pinball_loss_p50": 1.035919338831659,
      "pinball_loss_p90": 0.6594404153030838,
      "position": "RB",
      "prediction_season": 2025,
      "projection_tier": "middle",
      "rows": 45,
      "target_name": "fantasy_points_per_game"
    },
    {
      "candidate_name": "ridge",
      "empirical_coverage_p10_p90": 1.0,
      "evaluation_scope": "test",
      "mean_interval_width_p10_p90": 8.746884086501955,
      "pinball_loss_p10": 0.4546010671137667,
      "pinball_loss_p50": 0.5591492296444996,
      "pinball_loss_p90": 0.420087341536429,
      "position": "RB",
      "prediction_season": 2025,
      "projection_tier": "lower",
      "rows": 19,
      "target_name": "fantasy_points_per_game"
    },
    {
      "candidate_name": "ridge",
      "empirical_coverage_p10_p90": 0.8467153284671532,
      "evaluation_scope": "validation",
      "mean_interval_width_p10_p90": 10.382661433561218,
      "pinball_loss_p10": 0.6702252366895561,
      "pinball_loss_p50": 1.3857084048926491,
      "pinball_loss_p90": 0.7199689971582602,
      "position": "RB",
      "prediction_season": 2020,
      "projection_tier": "all",
      "rows": 137,
      "target_name": "fantasy_points_per_game"
    },
    {
      "candidate_name": "ridge",
      "empirical_coverage_p10_p90": 0.7323943661971831,
      "evaluation_scope": "validation",
      "mean_interval_width_p10_p90": 10.382661433561218,
      "pinball_loss_p10": 0.8322329632122089,
      "pinball_loss_p50": 1.8623070945826972,
      "pinball_loss_p90": 0.7726617138021771,
      "position": "RB",
      "prediction_season": 2020,
      "projection_tier": "top",
      "rows": 71,
      "target_name": "fantasy_points_per_game"
    },
    {
      "candidate_name": "ridge",
      "empirical_coverage_p10_p90": 0.9642857142857143,
      "evaluation_scope": "validation",
      "mean_interval_width_p10_p90": 10.382661433561221,
      "pinball_loss_p10": 0.4863189736636411,
      "pinball_loss_p50": 0.9200509032343896,
      "pinball_loss_p90": 0.6945100716143627,
      "position": "RB",
      "prediction_season": 2020,
      "projection_tier": "middle",
      "rows": 56,
      "target_name": "fantasy_points_per_game"
    },
    {
      "candidate_name": "ridge",
      "empirical_coverage_p10_p90": 1.0,
      "evaluation_scope": "validation",
      "mean_interval_width_p10_p90": 10.382661433561221,
      "pinball_loss_p10": 0.5498454513238462,
      "pinball_loss_p50": 0.6095397173795576,
      "pinball_loss_p90": 0.4884206920322757,
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
      "mean_interval_width_p10_p90": 9.721350612552838,
      "pinball_loss_p10": 0.6156929853000763,
      "pinball_loss_p50": 1.4047422283193804,
      "pinball_loss_p90": 0.7082081811984988,
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
      "mean_interval_width_p10_p90": 9.721350612552836,
      "pinball_loss_p10": 0.6190282679093767,
      "pinball_loss_p50": 1.5857460479405465,
      "pinball_loss_p90": 0.7457523885057128,
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
      "mean_interval_width_p10_p90": 9.721350612552833,
      "pinball_loss_p10": 0.5912329646930585,
      "pinball_loss_p50": 1.1957747493821855,
      "pinball_loss_p90": 0.6590236332966837,
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
      "mean_interval_width_p10_p90": 9.721350612552838,
      "pinball_loss_p10": 0.6928016204883352,
      "pinball_loss_p50": 1.4444885588595497,
      "pinball_loss_p90": 0.7380950172935931,
      "position": "RB",
      "prediction_season": 2021,
      "projection_tier": "lower",
      "rows": 17,
      "target_name": "fantasy_points_per_game"
    },
    {
      "candidate_name": "ridge",
      "empirical_coverage_p10_p90": 0.8129496402877698,
      "evaluation_scope": "validation",
      "mean_interval_width_p10_p90": 9.17823377663466,
      "pinball_loss_p10": 0.5447603229107321,
      "pinball_loss_p50": 1.2500486563746094,
      "pinball_loss_p90": 0.6913101283405155,
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
      "mean_interval_width_p10_p90": 9.17823377663466,
      "pinball_loss_p10": 0.6798602603690788,
      "pinball_loss_p50": 1.6687030276691326,
      "pinball_loss_p90": 0.7606662700120145,
      "position": "RB",
      "prediction_season": 2022,
      "projection_tier": "top",
      "rows": 68,
      "target_name": "fantasy_points_per_game"
    },
    {
      "candidate_name": "ridge",
      "empirical_coverage_p10_p90": 0.9090909090909091,
      "evaluation_scope": "validation",
      "mean_interval_width_p10_p90": 9.17823377663466,
      "pinball_loss_p10": 0.39773954306894266,
      "pinball_loss_p50": 0.9710508435685425,
      "pinball_loss_p90": 0.6781298135745772,
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
      "mean_interval_width_p10_p90": 9.17823377663466,
      "pinball_loss_p10": 0.47596951941890975,
      "pinball_loss_p50": 0.4298225598937413,
      "pinball_loss_p90": 0.4418538582445562,
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
      "mean_interval_width_p10_p90": 9.059403233659596,
      "pinball_loss_p10": 0.5931390626827573,
      "pinball_loss_p50": 1.3378694429611944,
      "pinball_loss_p90": 0.7556989393237626,
      "position": "RB",
      "prediction_season": 2023,
      "projection_tier": "all",
      "rows": 134,
      "target_name": "fantasy_points_per_game"
    },
    {
      "candidate_name": "ridge",
      "empirical_coverage_p10_p90": 0.696969696969697,
      "evaluation_scope": "validation",
      "mean_interval_width_p10_p90": 9.059403233659594,
      "pinball_loss_p10": 0.7754200480530282,
      "pinball_loss_p50": 1.8448947710541994,
      "pinball_loss_p90": 0.907620639918969,
      "position": "RB",
      "prediction_season": 2023,
      "projection_tier": "top",
      "rows": 66,
      "target_name": "fantasy_points_per_game"
    },
    {
      "candidate_name": "ridge",
      "empirical_coverage_p10_p90": 0.9423076923076923,
      "evaluation_scope": "validation",
      "mean_interval_width_p10_p90": 9.059403233659596,
      "pinball_loss_p10": 0.39400025952864914,
      "pinball_loss_p50": 0.949798961668318,
      "pinball_loss_p90": 0.6669336191033991,
      "position": "RB",
      "prediction_season": 2023,
      "projection_tier": "middle",
      "rows": 52,
      "target_name": "fantasy_points_per_game"
    },
    {
      "candidate_name": "ridge",
      "empirical_coverage_p10_p90": 1.0,
      "evaluation_scope": "validation",
      "mean_interval_width_p10_p90": 9.059403233659594,
      "pinball_loss_p10": 0.48843110828124137,
      "pinball_loss_p50": 0.5076190287793931,
      "pinball_loss_p90": 0.41750921508471794,
      "position": "RB",
      "prediction_season": 2023,
      "projection_tier": "lower",
      "rows": 16,
      "target_name": "fantasy_points_per_game"
    },
    {
      "candidate_name": "ridge",
      "empirical_coverage_p10_p90": 0.7952755905511811,
      "evaluation_scope": "validation",
      "mean_interval_width_p10_p90": 8.8012550898613,
      "pinball_loss_p10": 0.559003521642322,
      "pinball_loss_p50": 1.277612491963047,
      "pinball_loss_p90": 0.7022874621289181,
      "position": "RB",
      "prediction_season": 2024,
      "projection_tier": "all",
      "rows": 127,
      "target_name": "fantasy_points_per_game"
    },
    {
      "candidate_name": "ridge",
      "empirical_coverage_p10_p90": 0.6666666666666666,
      "evaluation_scope": "validation",
      "mean_interval_width_p10_p90": 8.801255089861298,
      "pinball_loss_p10": 0.6467371408859877,
      "pinball_loss_p50": 1.6463421601512724,
      "pinball_loss_p90": 0.8130648854755336,
      "position": "RB",
      "prediction_season": 2024,
      "projection_tier": "top",
      "rows": 66,
      "target_name": "fantasy_points_per_game"
    },
    {
      "candidate_name": "ridge",
      "empirical_coverage_p10_p90": 0.9183673469387755,
      "evaluation_scope": "validation",
      "mean_interval_width_p10_p90": 8.801255089861298,
      "pinball_loss_p10": 0.44745720643159437,
      "pinball_loss_p50": 0.9182917491511658,
      "pinball_loss_p90": 0.6397982035939873,
      "position": "RB",
      "prediction_season": 2024,
      "projection_tier": "middle",
      "rows": 49,
      "target_name": "fantasy_points_per_game"
    },
    {
      "candidate_name": "ridge",
      "empirical_coverage_p10_p90": 1.0,
      "evaluation_scope": "validation",
      "mean_interval_width_p10_p90": 8.801255089861298,
      "pinball_loss_p10": 0.53194940291263,
      "pinball_loss_p50": 0.7168256834096541,
      "pinball_loss_p90": 0.34817610607349936,
      "position": "RB",
      "prediction_season": 2024,
      "projection_tier": "lower",
      "rows": 12,
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
      "absolute_importance": 1.8272657206708147,
      "coefficient": 1.8272657206708147,
      "direction": "positive",
      "feature": "numeric__weighted_3yr_rushing_yards_per_game",
      "rank": 1
    },
    {
      "absolute_importance": 1.6253558459422557,
      "coefficient": 1.6253558459422557,
      "direction": "positive",
      "feature": "numeric__lag1_fantasy_points_total",
      "rank": 2
    },
    {
      "absolute_importance": 1.371682234680305,
      "coefficient": -1.371682234680305,
      "direction": "negative",
      "feature": "categorical__previous_team_NYJ",
      "rank": 3
    },
    {
      "absolute_importance": 0.8640926979447713,
      "coefficient": 0.8640926979447713,
      "direction": "positive",
      "feature": "numeric__weighted_3yr_fantasy_points_per_game",
      "rank": 4
    },
    {
      "absolute_importance": 0.8122808602724936,
      "coefficient": -0.8122808602724936,
      "direction": "negative",
      "feature": "numeric__weighted_3yr_carries_per_game",
      "rank": 5
    },
    {
      "absolute_importance": 0.8113024115609259,
      "coefficient": -0.8113024115609259,
      "direction": "negative",
      "feature": "numeric__age_at_cutoff",
      "rank": 6
    },
    {
      "absolute_importance": 0.7893067417924196,
      "coefficient": 0.7893067417924196,
      "direction": "positive",
      "feature": "categorical__previous_team_ARI",
      "rank": 7
    },
    {
      "absolute_importance": 0.7203531813812645,
      "coefficient": -0.7203531813812645,
      "direction": "negative",
      "feature": "categorical__previous_team_HOU",
      "rank": 8
    },
    {
      "absolute_importance": 0.7125829474156856,
      "coefficient": 0.7125829474156856,
      "direction": "positive",
      "feature": "categorical__previous_team_CAR",
      "rank": 9
    },
    {
      "absolute_importance": 0.6977623306210271,
      "coefficient": 0.6977623306210271,
      "direction": "positive",
      "feature": "categorical__previous_team_GB",
      "rank": 10
    },
    {
      "absolute_importance": 0.6897770585526065,
      "coefficient": 0.6897770585526065,
      "direction": "positive",
      "feature": "categorical__previous_team_LA",
      "rank": 11
    },
    {
      "absolute_importance": 0.6662036499372344,
      "coefficient": -0.6662036499372344,
      "direction": "negative",
      "feature": "categorical__previous_team_WAS",
      "rank": 12
    },
    {
      "absolute_importance": 0.6569988835942914,
      "coefficient": -0.6569988835942914,
      "direction": "negative",
      "feature": "categorical__previous_team_STL",
      "rank": 13
    },
    {
      "absolute_importance": 0.644051321283212,
      "coefficient": 0.644051321283212,
      "direction": "positive",
      "feature": "categorical__previous_team_CIN",
      "rank": 14
    },
    {
      "absolute_importance": 0.6307493539623886,
      "coefficient": -0.6307493539623886,
      "direction": "negative",
      "feature": "categorical__previous_team_DEN",
      "rank": 15
    },
    {
      "absolute_importance": 0.5352995216523111,
      "coefficient": 0.5352995216523111,
      "direction": "positive",
      "feature": "categorical__previous_team_LAC",
      "rank": 16
    },
    {
      "absolute_importance": 0.5144601596295845,
      "coefficient": -0.5144601596295845,
      "direction": "negative",
      "feature": "numeric__lag1_games_active",
      "rank": 17
    },
    {
      "absolute_importance": 0.4609327843230339,
      "coefficient": -0.4609327843230339,
      "direction": "negative",
      "feature": "numeric__draft_round",
      "rank": 18
    },
    {
      "absolute_importance": 0.40196939347943694,
      "coefficient": -0.40196939347943694,
      "direction": "negative",
      "feature": "categorical__previous_team_DET",
      "rank": 19
    },
    {
      "absolute_importance": 0.3966848095527881,
      "coefficient": 0.3966848095527881,
      "direction": "positive",
      "feature": "categorical__previous_team_SD",
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

- Project-relative path: `models/artifacts/phase4-052d2866899a665a44f3/attempt-331cdaf7eb7f4721aa43c08d469288ee/RB/fantasy_points_per_game/ridge.joblib`
- SHA-256: `2c19e4bf3a4287d8ceabbc3ab41f82cb77a43add6194973afb384afb32422d64`

## Additional metadata

````json
{
  "publication_id": "attempt-331cdaf7eb7f4721aa43c08d469288ee"
}
````
