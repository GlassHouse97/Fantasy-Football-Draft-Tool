# Model Card: phase4-052d2866899a665a44f3-te-games-ridge

- Model ID: `phase4-052d2866899a665a44f3-te-games-ridge`
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
  "draft_relevant_validation_mae": 3.691576366682398,
  "draft_relevant_validation_rows": 60,
  "draft_relevant_validation_signed_bias": -0.7749403751978583,
  "position": "TE",
  "target_name": "games_active",
  "test_mae": 2.867405003563206,
  "test_rows": 235,
  "test_season": 2025,
  "validation_mae": 3.65206192705303,
  "validation_rows": 1158,
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
    "candidate_mae": 3.523514327909002,
    "ci95_lower": -0.17265503626353662,
    "ci95_upper": 1.4369851500407562,
    "direction": "uncertain",
    "mae_difference_candidate_minus_reference": 0.6485645187455078,
    "n_resamples": 2000,
    "reference_mae": 2.8749498091634944,
    "rows": 60,
    "seed": 42
  },
  "decision_status": "learned_draft_relevant_regression_baseline_retained",
  "learned_improvement_status": "regression",
  "reference_metrics": {
    "candidate_name": "position_shrinkage",
    "candidate_source": "baseline",
    "draft_relevant_validation_mae": 2.8749498091634944,
    "draft_relevant_validation_rows": 60,
    "draft_relevant_validation_signed_bias": 0.8226574852812342,
    "position": "TE",
    "target_name": "games_active",
    "test_mae": 7.248982728945333,
    "test_rows": 235,
    "test_season": 2025,
    "validation_mae": 7.267050655228297,
    "validation_rows": 1158,
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
      "empirical_coverage_p10_p90": 0.8638297872340426,
      "evaluation_scope": "test",
      "mean_interval_width_p10_p90": 9.051428987328716,
      "pinball_loss_p10": 0.529333384294681,
      "pinball_loss_p50": 1.433702501781603,
      "pinball_loss_p90": 0.7385223680870071,
      "position": "TE",
      "prediction_season": 2025,
      "projection_tier": "all",
      "rows": 235,
      "target_name": "games_active"
    },
    {
      "candidate_name": "ridge",
      "empirical_coverage_p10_p90": 0.9152542372881356,
      "evaluation_scope": "test",
      "mean_interval_width_p10_p90": 10.24525233009678,
      "pinball_loss_p10": 0.8932583326054634,
      "pinball_loss_p50": 1.6708792189904564,
      "pinball_loss_p90": 0.38137253041037744,
      "position": "TE",
      "prediction_season": 2025,
      "projection_tier": "top",
      "rows": 59,
      "target_name": "games_active"
    },
    {
      "candidate_name": "ridge",
      "empirical_coverage_p10_p90": 0.7692307692307693,
      "evaluation_scope": "test",
      "mean_interval_width_p10_p90": 10.06530893372274,
      "pinball_loss_p10": 0.608470971671177,
      "pinball_loss_p50": 1.9797505033856386,
      "pinball_loss_p90": 1.0004640963772362,
      "position": "TE",
      "prediction_season": 2025,
      "projection_tier": "middle",
      "rows": 117,
      "target_name": "games_active"
    },
    {
      "candidate_name": "ridge",
      "empirical_coverage_p10_p90": 1.0,
      "evaluation_scope": "test",
      "mean_interval_width_p10_p90": 5.847030157643691,
      "pinball_loss_p10": 0.00847457627118644,
      "pinball_loss_p50": 0.11368483223932238,
      "pinball_loss_p90": 0.5762284394931825,
      "position": "TE",
      "prediction_season": 2025,
      "projection_tier": "lower",
      "rows": 59,
      "target_name": "games_active"
    },
    {
      "candidate_name": "ridge",
      "empirical_coverage_p10_p90": 0.8035714285714286,
      "evaluation_scope": "validation",
      "mean_interval_width_p10_p90": 11.962397327578616,
      "pinball_loss_p10": 0.7968464669760594,
      "pinball_loss_p50": 2.5468492717729156,
      "pinball_loss_p90": 0.9776178228395681,
      "position": "TE",
      "prediction_season": 2020,
      "projection_tier": "all",
      "rows": 224,
      "target_name": "games_active"
    },
    {
      "candidate_name": "ridge",
      "empirical_coverage_p10_p90": 0.8928571428571429,
      "evaluation_scope": "validation",
      "mean_interval_width_p10_p90": 8.5820734266372,
      "pinball_loss_p10": 0.9414251838926628,
      "pinball_loss_p50": 1.5634816708905146,
      "pinball_loss_p90": 0.4410714285714285,
      "position": "TE",
      "prediction_season": 2020,
      "projection_tier": "top",
      "rows": 56,
      "target_name": "games_active"
    },
    {
      "candidate_name": "ridge",
      "empirical_coverage_p10_p90": 0.6637168141592921,
      "evaluation_scope": "validation",
      "mean_interval_width_p10_p90": 13.66348839376151,
      "pinball_loss_p10": 1.1024229938464443,
      "pinball_loss_p50": 3.177833050690122,
      "pinball_loss_p90": 1.150316125813944,
      "position": "TE",
      "prediction_season": 2020,
      "projection_tier": "middle",
      "rows": 113,
      "target_name": "games_active"
    },
    {
      "candidate_name": "ridge",
      "empirical_coverage_p10_p90": 1.0,
      "evaluation_scope": "validation",
      "mean_interval_width_p10_p90": 11.909212745288656,
      "pinball_loss_p10": 0.02181818181818182,
      "pinball_loss_p50": 2.2517114287141906,
      "pinball_loss_p90": 1.1691030927106834,
      "position": "TE",
      "prediction_season": 2020,
      "projection_tier": "lower",
      "rows": 55,
      "target_name": "games_active"
    },
    {
      "candidate_name": "ridge",
      "empirical_coverage_p10_p90": 0.8122270742358079,
      "evaluation_scope": "validation",
      "mean_interval_width_p10_p90": 10.021055286674045,
      "pinball_loss_p10": 0.5989107502517432,
      "pinball_loss_p50": 1.746544367371027,
      "pinball_loss_p90": 0.9190011339417674,
      "position": "TE",
      "prediction_season": 2021,
      "projection_tier": "all",
      "rows": 229,
      "target_name": "games_active"
    },
    {
      "candidate_name": "ridge",
      "empirical_coverage_p10_p90": 0.8771929824561403,
      "evaluation_scope": "validation",
      "mean_interval_width_p10_p90": 13.379186074455534,
      "pinball_loss_p10": 1.1841724764187935,
      "pinball_loss_p50": 2.3234069666683226,
      "pinball_loss_p90": 0.4686441913982647,
      "position": "TE",
      "prediction_season": 2021,
      "projection_tier": "top",
      "rows": 57,
      "target_name": "games_active"
    },
    {
      "candidate_name": "ridge",
      "empirical_coverage_p10_p90": 0.6956521739130435,
      "evaluation_scope": "validation",
      "mean_interval_width_p10_p90": 10.412262503242545,
      "pinball_loss_p10": 0.5952411361024171,
      "pinball_loss_p50": 2.2741257654597455,
      "pinball_loss_p90": 1.2126848183462076,
      "position": "TE",
      "prediction_season": 2021,
      "projection_tier": "middle",
      "rows": 115,
      "target_name": "games_active"
    },
    {
      "candidate_name": "ridge",
      "empirical_coverage_p10_p90": 0.9824561403508771,
      "evaluation_scope": "validation",
      "mean_interval_width_p10_p90": 5.873646781254347,
      "pinball_loss_p10": 0.02105263157894737,
      "pinball_loss_p50": 0.10526315789473684,
      "pinball_loss_p90": 0.7768383623359609,
      "position": "TE",
      "prediction_season": 2021,
      "projection_tier": "lower",
      "rows": 57,
      "target_name": "games_active"
    },
    {
      "candidate_name": "ridge",
      "empirical_coverage_p10_p90": 0.7991452991452992,
      "evaluation_scope": "validation",
      "mean_interval_width_p10_p90": 9.937780746229299,
      "pinball_loss_p10": 0.5792141006517104,
      "pinball_loss_p50": 1.6837579638090914,
      "pinball_loss_p90": 0.8027714421489797,
      "position": "TE",
      "prediction_season": 2022,
      "projection_tier": "all",
      "rows": 234,
      "target_name": "games_active"
    },
    {
      "candidate_name": "ridge",
      "empirical_coverage_p10_p90": 0.8813559322033898,
      "evaluation_scope": "validation",
      "mean_interval_width_p10_p90": 12.686102037487473,
      "pinball_loss_p10": 1.128142688711611,
      "pinball_loss_p50": 2.126576917353373,
      "pinball_loss_p90": 0.4151913910505771,
      "position": "TE",
      "prediction_season": 2022,
      "projection_tier": "top",
      "rows": 59,
      "target_name": "games_active"
    },
    {
      "candidate_name": "ridge",
      "empirical_coverage_p10_p90": 0.6551724137931034,
      "evaluation_scope": "validation",
      "mean_interval_width_p10_p90": 10.870119638219377,
      "pinball_loss_p10": 0.5946179389527173,
      "pinball_loss_p50": 2.3149041953809943,
      "pinball_loss_p90": 1.1357719461520046,
      "position": "TE",
      "prediction_season": 2022,
      "projection_tier": "middle",
      "rows": 116,
      "target_name": "games_active"
    },
    {
      "candidate_name": "ridge",
      "empirical_coverage_p10_p90": 1.0,
      "evaluation_scope": "validation",
      "mean_interval_width_p10_p90": 5.356386379194017,
      "pinball_loss_p10": 0.0,
      "pinball_loss_p50": 4.133463191674796e-05,
      "pinball_loss_p90": 0.5356386379194016,
      "position": "TE",
      "prediction_season": 2022,
      "projection_tier": "lower",
      "rows": 59,
      "target_name": "games_active"
    },
    {
      "candidate_name": "ridge",
      "empirical_coverage_p10_p90": 0.825531914893617,
      "evaluation_scope": "validation",
      "mean_interval_width_p10_p90": 9.324876053920176,
      "pinball_loss_p10": 0.5674634793433294,
      "pinball_loss_p50": 1.5148461097070027,
      "pinball_loss_p90": 0.7540290811273919,
      "position": "TE",
      "prediction_season": 2023,
      "projection_tier": "all",
      "rows": 235,
      "target_name": "games_active"
    },
    {
      "candidate_name": "ridge",
      "empirical_coverage_p10_p90": 0.8135593220338984,
      "evaluation_scope": "validation",
      "mean_interval_width_p10_p90": 12.457661044731205,
      "pinball_loss_p10": 1.2281993707075507,
      "pinball_loss_p50": 2.2236910875197946,
      "pinball_loss_p90": 0.42191399139371366,
      "position": "TE",
      "prediction_season": 2023,
      "projection_tier": "top",
      "rows": 59,
      "target_name": "games_active"
    },
    {
      "candidate_name": "ridge",
      "empirical_coverage_p10_p90": 0.7435897435897436,
      "evaluation_scope": "validation",
      "mean_interval_width_p10_p90": 9.670221592831677,
      "pinball_loss_p10": 0.5093175621704009,
      "pinball_loss_p50": 1.8657355693801516,
      "pinball_loss_p90": 1.0351377273985354,
      "position": "TE",
      "prediction_season": 2023,
      "projection_tier": "middle",
      "rows": 117,
      "target_name": "games_active"
    },
    {
      "candidate_name": "ridge",
      "empirical_coverage_p10_p90": 1.0,
      "evaluation_scope": "validation",
      "mean_interval_width_p10_p90": 5.507253299504976,
      "pinball_loss_p10": 0.02203389830508475,
      "pinball_loss_p50": 0.11016949152542373,
      "pinball_loss_p90": 0.5286914316454129,
      "position": "TE",
      "prediction_season": 2023,
      "projection_tier": "lower",
      "rows": 59,
      "target_name": "games_active"
    },
    {
      "candidate_name": "ridge",
      "empirical_coverage_p10_p90": 0.8050847457627118,
      "evaluation_scope": "validation",
      "mean_interval_width_p10_p90": 9.003961339133088,
      "pinball_loss_p10": 0.6652395541842364,
      "pinball_loss_p50": 1.6699269468056483,
      "pinball_loss_p90": 0.8334682697457724,
      "position": "TE",
      "prediction_season": 2024,
      "projection_tier": "all",
      "rows": 236,
      "target_name": "games_active"
    },
    {
      "candidate_name": "ridge",
      "empirical_coverage_p10_p90": 0.864406779661017,
      "evaluation_scope": "validation",
      "mean_interval_width_p10_p90": 10.060352261840851,
      "pinball_loss_p10": 1.1742886008378357,
      "pinball_loss_p50": 2.0131150893017087,
      "pinball_loss_p90": 0.39727524821115723,
      "position": "TE",
      "prediction_season": 2024,
      "projection_tier": "top",
      "rows": 59,
      "target_name": "games_active"
    },
    {
      "candidate_name": "ridge",
      "empirical_coverage_p10_p90": 0.6864406779661016,
      "evaluation_scope": "validation",
      "mean_interval_width_p10_p90": 9.90965619862852,
      "pinball_loss_p10": 0.7357076893054869,
      "pinball_loss_p50": 2.2338412111119728,
      "pinball_loss_p90": 1.1686682697218724,
      "position": "TE",
      "prediction_season": 2024,
      "projection_tier": "middle",
      "rows": 118,
      "target_name": "games_active"
    },
    {
      "candidate_name": "ridge",
      "empirical_coverage_p10_p90": 0.9830508474576272,
      "evaluation_scope": "validation",
      "mean_interval_width_p10_p90": 6.136180697434463,
      "pinball_loss_p10": 0.015254237288135596,
      "pinball_loss_p50": 0.1989102756969397,
      "pinball_loss_p90": 0.5992612913281877,
      "position": "TE",
      "prediction_season": 2024,
      "projection_tier": "lower",
      "rows": 59,
      "target_name": "games_active"
    }
  ],
  "empirical_not_guaranteed": true,
  "method": "training-only signed out-of-fold residual quantiles",
  "operational_center": "training_only_residual_adjusted_p50",
  "residual_rows": 706,
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
      "absolute_importance": 1.6493388464270708,
      "coefficient": 1.6493388464270708,
      "direction": "positive",
      "feature": "categorical__previous_team_SF",
      "rank": 1
    },
    {
      "absolute_importance": 1.6113512704254145,
      "coefficient": 1.6113512704254145,
      "direction": "positive",
      "feature": "numeric__weighted_3yr_receptions_per_game",
      "rank": 2
    },
    {
      "absolute_importance": 1.394097455652017,
      "coefficient": -1.394097455652017,
      "direction": "negative",
      "feature": "categorical__previous_team_NYG",
      "rank": 3
    },
    {
      "absolute_importance": 1.378445410763955,
      "coefficient": -1.378445410763955,
      "direction": "negative",
      "feature": "numeric__weighted_3yr_targets_per_game",
      "rank": 4
    },
    {
      "absolute_importance": 1.3188651095487918,
      "coefficient": -1.3188651095487918,
      "direction": "negative",
      "feature": "categorical__previous_team_NE",
      "rank": 5
    },
    {
      "absolute_importance": 1.306301728125142,
      "coefficient": 1.306301728125142,
      "direction": "positive",
      "feature": "categorical__previous_team_CAR",
      "rank": 6
    },
    {
      "absolute_importance": 1.3019206223151187,
      "coefficient": 1.3019206223151187,
      "direction": "positive",
      "feature": "numeric__lag1_stat_games",
      "rank": 7
    },
    {
      "absolute_importance": 1.2350429843108464,
      "coefficient": -1.2350429843108464,
      "direction": "negative",
      "feature": "numeric__lag1_fantasy_points_total",
      "rank": 8
    },
    {
      "absolute_importance": 1.226777619510401,
      "coefficient": 1.226777619510401,
      "direction": "positive",
      "feature": "categorical__previous_team_SD",
      "rank": 9
    },
    {
      "absolute_importance": 1.1768330118544599,
      "coefficient": 1.1768330118544599,
      "direction": "positive",
      "feature": "categorical__previous_team_KC",
      "rank": 10
    },
    {
      "absolute_importance": 1.1359404221277116,
      "coefficient": -1.1359404221277116,
      "direction": "negative",
      "feature": "categorical__previous_team_LV",
      "rank": 11
    },
    {
      "absolute_importance": 1.134955624881707,
      "coefficient": 1.134955624881707,
      "direction": "positive",
      "feature": "categorical__previous_team_GB",
      "rank": 12
    },
    {
      "absolute_importance": 1.1253414577657916,
      "coefficient": 1.1253414577657916,
      "direction": "positive",
      "feature": "categorical__previous_team_TEN",
      "rank": 13
    },
    {
      "absolute_importance": 1.116615383821745,
      "coefficient": 1.116615383821745,
      "direction": "positive",
      "feature": "numeric__lag1_games_active",
      "rank": 14
    },
    {
      "absolute_importance": 1.0548064898789737,
      "coefficient": -1.0548064898789737,
      "direction": "negative",
      "feature": "numeric__draft_round",
      "rank": 15
    },
    {
      "absolute_importance": 0.9763953955947825,
      "coefficient": 0.9763953955947825,
      "direction": "positive",
      "feature": "categorical__previous_team_LA",
      "rank": 16
    },
    {
      "absolute_importance": 0.9334641510138156,
      "coefficient": 0.9334641510138156,
      "direction": "positive",
      "feature": "numeric__lag1_fantasy_points_per_game",
      "rank": 17
    },
    {
      "absolute_importance": 0.9218624854641946,
      "coefficient": 0.9218624854641946,
      "direction": "positive",
      "feature": "categorical__previous_team_OAK",
      "rank": 18
    },
    {
      "absolute_importance": 0.8073011889229471,
      "coefficient": 0.8073011889229471,
      "direction": "positive",
      "feature": "numeric__draft_pick",
      "rank": 19
    },
    {
      "absolute_importance": 0.7303484628030096,
      "coefficient": -0.7303484628030096,
      "direction": "negative",
      "feature": "categorical__previous_team_WAS",
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

- Project-relative path: `models/artifacts/phase4-052d2866899a665a44f3/attempt-331cdaf7eb7f4721aa43c08d469288ee/TE/games_active/ridge.joblib`
- SHA-256: `4d117532b9989c7eb16cb4d746d43abba772b87b81c46de0e7e2c770c48a264d`

## Additional metadata

````json
{
  "publication_id": "attempt-331cdaf7eb7f4721aa43c08d469288ee"
}
````
