# Model Card: phase4-052d2866899a665a44f3-te-ppg-ridge

- Model ID: `phase4-052d2866899a665a44f3-te-ppg-ridge`
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
  "draft_relevant_validation_mae": 2.40831830739868,
  "draft_relevant_validation_rows": 57,
  "draft_relevant_validation_signed_bias": -0.28588035932949496,
  "position": "TE",
  "target_name": "fantasy_points_per_game",
  "test_mae": 1.762033539403317,
  "test_rows": 122,
  "test_season": 2025,
  "validation_mae": 1.9153139957242427,
  "validation_rows": 565,
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
    "candidate_mae": 2.40831830739868,
    "ci95_lower": -0.22948778595683184,
    "ci95_upper": 0.6296893557089356,
    "direction": "uncertain",
    "mae_difference_candidate_minus_reference": 0.16998204626480184,
    "n_resamples": 2000,
    "reference_mae": 2.238336261133878,
    "rows": 57,
    "seed": 42
  },
  "decision_status": "learned_draft_relevant_regression_baseline_retained",
  "learned_improvement_status": "regression",
  "reference_metrics": {
    "candidate_name": "position_shrinkage",
    "candidate_source": "baseline",
    "draft_relevant_validation_mae": 2.238336261133878,
    "draft_relevant_validation_rows": 57,
    "draft_relevant_validation_signed_bias": -0.19274826615156876,
    "position": "TE",
    "target_name": "fantasy_points_per_game",
    "test_mae": 1.8806253978457534,
    "test_rows": 122,
    "test_season": 2025,
    "validation_mae": 1.897446004312275,
    "validation_rows": 565,
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
      "empirical_coverage_p10_p90": 0.7540983606557377,
      "evaluation_scope": "test",
      "mean_interval_width_p10_p90": 4.9102890573421005,
      "pinball_loss_p10": 0.4143550134581311,
      "pinball_loss_p50": 0.8810167697016585,
      "pinball_loss_p90": 0.5521075021715016,
      "position": "TE",
      "prediction_season": 2025,
      "projection_tier": "all",
      "rows": 122,
      "target_name": "fantasy_points_per_game"
    },
    {
      "candidate_name": "ridge",
      "empirical_coverage_p10_p90": 0.5454545454545454,
      "evaluation_scope": "test",
      "mean_interval_width_p10_p90": 4.910289057342101,
      "pinball_loss_p10": 0.5488858930134536,
      "pinball_loss_p50": 1.253484274665086,
      "pinball_loss_p90": 0.7655823317988832,
      "position": "TE",
      "prediction_season": 2025,
      "projection_tier": "top",
      "rows": 55,
      "target_name": "fantasy_points_per_game"
    },
    {
      "candidate_name": "ridge",
      "empirical_coverage_p10_p90": 0.9245283018867925,
      "evaluation_scope": "test",
      "mean_interval_width_p10_p90": 4.910289057342102,
      "pinball_loss_p10": 0.2887696513835895,
      "pinball_loss_p50": 0.5427092419445861,
      "pinball_loss_p90": 0.4371483997562279,
      "position": "TE",
      "prediction_season": 2025,
      "projection_tier": "middle",
      "rows": 53,
      "target_name": "fantasy_points_per_game"
    },
    {
      "candidate_name": "ridge",
      "empirical_coverage_p10_p90": 0.9285714285714286,
      "evaluation_scope": "test",
      "mean_interval_width_p10_p90": 4.9102890573421,
      "pinball_loss_p10": 0.3612711430586999,
      "pinball_loss_p50": 0.6984872124256791,
      "pinball_loss_p90": 0.14865870206460957,
      "position": "TE",
      "prediction_season": 2025,
      "projection_tier": "lower",
      "rows": 14,
      "target_name": "fantasy_points_per_game"
    },
    {
      "candidate_name": "ridge",
      "empirical_coverage_p10_p90": 0.7297297297297297,
      "evaluation_scope": "validation",
      "mean_interval_width_p10_p90": 6.086927443671152,
      "pinball_loss_p10": 0.5247237405595013,
      "pinball_loss_p50": 1.300465068477774,
      "pinball_loss_p90": 0.6653109865186779,
      "position": "TE",
      "prediction_season": 2020,
      "projection_tier": "all",
      "rows": 111,
      "target_name": "fantasy_points_per_game"
    },
    {
      "candidate_name": "ridge",
      "empirical_coverage_p10_p90": 0.6304347826086957,
      "evaluation_scope": "validation",
      "mean_interval_width_p10_p90": 6.086927443671152,
      "pinball_loss_p10": 0.6114871448758844,
      "pinball_loss_p50": 1.4587014577140778,
      "pinball_loss_p90": 0.7486235292066803,
      "position": "TE",
      "prediction_season": 2020,
      "projection_tier": "top",
      "rows": 46,
      "target_name": "fantasy_points_per_game"
    },
    {
      "candidate_name": "ridge",
      "empirical_coverage_p10_p90": 0.76,
      "evaluation_scope": "validation",
      "mean_interval_width_p10_p90": 6.0869274436711525,
      "pinball_loss_p10": 0.46318917338108906,
      "pinball_loss_p50": 1.2290482314898097,
      "pinball_loss_p90": 0.7371335644669569,
      "position": "TE",
      "prediction_season": 2020,
      "projection_tier": "middle",
      "rows": 50,
      "target_name": "fantasy_points_per_game"
    },
    {
      "candidate_name": "ridge",
      "empirical_coverage_p10_p90": 0.9333333333333333,
      "evaluation_scope": "validation",
      "mean_interval_width_p10_p90": 6.086927443671154,
      "pinball_loss_p10": 0.46376452458396733,
      "pinball_loss_p50": 1.053262931446325,
      "pinball_loss_p90": 0.17041059578120868,
      "position": "TE",
      "prediction_season": 2020,
      "projection_tier": "lower",
      "rows": 15,
      "target_name": "fantasy_points_per_game"
    },
    {
      "candidate_name": "ridge",
      "empirical_coverage_p10_p90": 0.8305084745762712,
      "evaluation_scope": "validation",
      "mean_interval_width_p10_p90": 6.822889452245716,
      "pinball_loss_p10": 0.4032097967054609,
      "pinball_loss_p50": 0.8997188570230218,
      "pinball_loss_p90": 0.5260515276600513,
      "position": "TE",
      "prediction_season": 2021,
      "projection_tier": "all",
      "rows": 118,
      "target_name": "fantasy_points_per_game"
    },
    {
      "candidate_name": "ridge",
      "empirical_coverage_p10_p90": 0.7115384615384616,
      "evaluation_scope": "validation",
      "mean_interval_width_p10_p90": 6.822889452245715,
      "pinball_loss_p10": 0.5718566267585682,
      "pinball_loss_p50": 1.1816646447075958,
      "pinball_loss_p90": 0.5984248503034783,
      "position": "TE",
      "prediction_season": 2021,
      "projection_tier": "top",
      "rows": 52,
      "target_name": "fantasy_points_per_game"
    },
    {
      "candidate_name": "ridge",
      "empirical_coverage_p10_p90": 0.8936170212765957,
      "evaluation_scope": "validation",
      "mean_interval_width_p10_p90": 6.822889452245714,
      "pinball_loss_p10": 0.27118595809855034,
      "pinball_loss_p50": 0.8438397705490431,
      "pinball_loss_p90": 0.49125466974479354,
      "position": "TE",
      "prediction_season": 2021,
      "projection_tier": "middle",
      "rows": 47,
      "target_name": "fantasy_points_per_game"
    },
    {
      "candidate_name": "ridge",
      "empirical_coverage_p10_p90": 1.0,
      "evaluation_scope": "validation",
      "mean_interval_width_p10_p90": 6.822889452245715,
      "pinball_loss_p10": 0.26823533627194623,
      "pinball_loss_p50": 0.2663049677956085,
      "pinball_loss_p90": 0.4140536089526253,
      "position": "TE",
      "prediction_season": 2021,
      "projection_tier": "lower",
      "rows": 19,
      "target_name": "fantasy_points_per_game"
    },
    {
      "candidate_name": "ridge",
      "empirical_coverage_p10_p90": 0.8545454545454545,
      "evaluation_scope": "validation",
      "mean_interval_width_p10_p90": 6.446838625958611,
      "pinball_loss_p10": 0.48299031009900645,
      "pinball_loss_p50": 0.9390634175126242,
      "pinball_loss_p90": 0.46884143254064875,
      "position": "TE",
      "prediction_season": 2022,
      "projection_tier": "all",
      "rows": 110,
      "target_name": "fantasy_points_per_game"
    },
    {
      "candidate_name": "ridge",
      "empirical_coverage_p10_p90": 0.7058823529411765,
      "evaluation_scope": "validation",
      "mean_interval_width_p10_p90": 6.446838625958608,
      "pinball_loss_p10": 0.776444364791827,
      "pinball_loss_p50": 1.2349793042753199,
      "pinball_loss_p90": 0.4972411690360891,
      "position": "TE",
      "prediction_season": 2022,
      "projection_tier": "top",
      "rows": 51,
      "target_name": "fantasy_points_per_game"
    },
    {
      "candidate_name": "ridge",
      "empirical_coverage_p10_p90": 0.9777777777777777,
      "evaluation_scope": "validation",
      "mean_interval_width_p10_p90": 6.446838625958608,
      "pinball_loss_p10": 0.1998917035059741,
      "pinball_loss_p50": 0.7462493834589855,
      "pinball_loss_p90": 0.4827295273561656,
      "position": "TE",
      "prediction_season": 2022,
      "projection_tier": "middle",
      "rows": 45,
      "target_name": "fantasy_points_per_game"
    },
    {
      "candidate_name": "ridge",
      "empirical_coverage_p10_p90": 1.0,
      "evaluation_scope": "validation",
      "mean_interval_width_p10_p90": 6.446838625958607,
      "pinball_loss_p10": 0.3239389177670496,
      "pinball_loss_p50": 0.4808435109066438,
      "pinball_loss_p90": 0.3207449448288113,
      "position": "TE",
      "prediction_season": 2022,
      "projection_tier": "lower",
      "rows": 14,
      "target_name": "fantasy_points_per_game"
    },
    {
      "candidate_name": "ridge",
      "empirical_coverage_p10_p90": 0.8303571428571429,
      "evaluation_scope": "validation",
      "mean_interval_width_p10_p90": 6.006492330136999,
      "pinball_loss_p10": 0.3629335540250938,
      "pinball_loss_p50": 0.8476233088547038,
      "pinball_loss_p90": 0.4849156294950992,
      "position": "TE",
      "prediction_season": 2023,
      "projection_tier": "all",
      "rows": 112,
      "target_name": "fantasy_points_per_game"
    },
    {
      "candidate_name": "ridge",
      "empirical_coverage_p10_p90": 0.6923076923076923,
      "evaluation_scope": "validation",
      "mean_interval_width_p10_p90": 6.006492330136999,
      "pinball_loss_p10": 0.5099015893502693,
      "pinball_loss_p50": 1.1612412957277878,
      "pinball_loss_p90": 0.5464834381723798,
      "position": "TE",
      "prediction_season": 2023,
      "projection_tier": "top",
      "rows": 52,
      "target_name": "fantasy_points_per_game"
    },
    {
      "candidate_name": "ridge",
      "empirical_coverage_p10_p90": 0.9583333333333334,
      "evaluation_scope": "validation",
      "mean_interval_width_p10_p90": 6.006492330136999,
      "pinball_loss_p10": 0.2017426839856095,
      "pinball_loss_p50": 0.5810895578818963,
      "pinball_loss_p90": 0.41422658933544687,
      "position": "TE",
      "prediction_season": 2023,
      "projection_tier": "middle",
      "rows": 48,
      "target_name": "fantasy_points_per_game"
    },
    {
      "candidate_name": "ridge",
      "empirical_coverage_p10_p90": 0.9166666666666666,
      "evaluation_scope": "validation",
      "mean_interval_width_p10_p90": 6.0064923301369975,
      "pinball_loss_p10": 0.37083554777393735,
      "pinball_loss_p50": 0.5547470362959032,
      "pinball_loss_p90": 0.5008779525321589,
      "position": "TE",
      "prediction_season": 2023,
      "projection_tier": "lower",
      "rows": 12,
      "target_name": "fantasy_points_per_game"
    },
    {
      "candidate_name": "ridge",
      "empirical_coverage_p10_p90": 0.7894736842105263,
      "evaluation_scope": "validation",
      "mean_interval_width_p10_p90": 5.108034966757714,
      "pinball_loss_p10": 0.3741391777387814,
      "pinball_loss_p50": 0.809885697756434,
      "pinball_loss_p90": 0.4650104153535043,
      "position": "TE",
      "prediction_season": 2024,
      "projection_tier": "all",
      "rows": 114,
      "target_name": "fantasy_points_per_game"
    },
    {
      "candidate_name": "ridge",
      "empirical_coverage_p10_p90": 0.6153846153846154,
      "evaluation_scope": "validation",
      "mean_interval_width_p10_p90": 5.108034966757715,
      "pinball_loss_p10": 0.47977969376734697,
      "pinball_loss_p50": 1.2122039920793595,
      "pinball_loss_p90": 0.7118920281374466,
      "position": "TE",
      "prediction_season": 2024,
      "projection_tier": "top",
      "rows": 52,
      "target_name": "fantasy_points_per_game"
    },
    {
      "candidate_name": "ridge",
      "empirical_coverage_p10_p90": 0.9272727272727272,
      "evaluation_scope": "validation",
      "mean_interval_width_p10_p90": 5.108034966757715,
      "pinball_loss_p10": 0.2778683962140584,
      "pinball_loss_p50": 0.46221453667107076,
      "pinball_loss_p90": 0.2697770509994125,
      "position": "TE",
      "prediction_season": 2024,
      "projection_tier": "middle",
      "rows": 55,
      "target_name": "fantasy_points_per_game"
    },
    {
      "candidate_name": "ridge",
      "empirical_coverage_p10_p90": 1.0,
      "evaluation_scope": "validation",
      "mean_interval_width_p10_p90": 5.108034966757715,
      "pinball_loss_p10": 0.34579434207797616,
      "pinball_loss_p50": 0.5529374913139852,
      "pinball_loss_p90": 0.16500915459779528,
      "position": "TE",
      "prediction_season": 2024,
      "projection_tier": "lower",
      "rows": 7,
      "target_name": "fantasy_points_per_game"
    }
  ],
  "empirical_not_guaranteed": true,
  "method": "training-only signed out-of-fold residual quantiles",
  "operational_center": "training_only_residual_adjusted_p50",
  "residual_rows": 348,
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
      "absolute_importance": 1.8236760473178044,
      "coefficient": 1.8236760473178044,
      "direction": "positive",
      "feature": "numeric__weighted_3yr_receiving_yards_per_game",
      "rank": 1
    },
    {
      "absolute_importance": 1.1842163405236827,
      "coefficient": 1.1842163405236827,
      "direction": "positive",
      "feature": "numeric__lag1_fantasy_points_total",
      "rank": 2
    },
    {
      "absolute_importance": 0.7434403352054295,
      "coefficient": -0.7434403352054295,
      "direction": "negative",
      "feature": "categorical__previous_team_NYJ",
      "rank": 3
    },
    {
      "absolute_importance": 0.7141527001450384,
      "coefficient": -0.7141527001450384,
      "direction": "negative",
      "feature": "numeric__weighted_3yr_rushing_tds_per_game",
      "rank": 4
    },
    {
      "absolute_importance": 0.7025811140408672,
      "coefficient": 0.7025811140408672,
      "direction": "positive",
      "feature": "numeric__weighted_3yr_fantasy_points_per_game",
      "rank": 5
    },
    {
      "absolute_importance": 0.6234653747253742,
      "coefficient": 0.6234653747253742,
      "direction": "positive",
      "feature": "numeric__weighted_3yr_rushing_yards_per_game",
      "rank": 6
    },
    {
      "absolute_importance": 0.6149765958303764,
      "coefficient": 0.6149765958303764,
      "direction": "positive",
      "feature": "categorical__previous_team_KC",
      "rank": 7
    },
    {
      "absolute_importance": 0.5495774260796311,
      "coefficient": 0.5495774260796311,
      "direction": "positive",
      "feature": "categorical__previous_team_NO",
      "rank": 8
    },
    {
      "absolute_importance": 0.4653456261575946,
      "coefficient": 0.4653456261575946,
      "direction": "positive",
      "feature": "categorical__previous_team_LA",
      "rank": 9
    },
    {
      "absolute_importance": 0.4647771280608386,
      "coefficient": -0.4647771280608386,
      "direction": "negative",
      "feature": "categorical__previous_team_CAR",
      "rank": 10
    },
    {
      "absolute_importance": 0.4622076263288409,
      "coefficient": 0.4622076263288409,
      "direction": "positive",
      "feature": "categorical__previous_team_DET",
      "rank": 11
    },
    {
      "absolute_importance": 0.4148755637389135,
      "coefficient": -0.4148755637389135,
      "direction": "negative",
      "feature": "categorical__previous_team_CHI",
      "rank": 12
    },
    {
      "absolute_importance": 0.4146114393812152,
      "coefficient": 0.4146114393812152,
      "direction": "positive",
      "feature": "categorical__previous_team_ARI",
      "rank": 13
    },
    {
      "absolute_importance": 0.4001969066435565,
      "coefficient": -0.4001969066435565,
      "direction": "negative",
      "feature": "categorical__previous_team_PIT",
      "rank": 14
    },
    {
      "absolute_importance": 0.3992211632590845,
      "coefficient": 0.3992211632590845,
      "direction": "positive",
      "feature": "numeric__weighted_3yr_carries_per_game",
      "rank": 15
    },
    {
      "absolute_importance": 0.3900734636985536,
      "coefficient": 0.3900734636985536,
      "direction": "positive",
      "feature": "categorical__previous_team_DAL",
      "rank": 16
    },
    {
      "absolute_importance": 0.376820575774109,
      "coefficient": -0.376820575774109,
      "direction": "negative",
      "feature": "numeric__weighted_3yr_passing_tds_per_game",
      "rank": 17
    },
    {
      "absolute_importance": 0.36607491428566313,
      "coefficient": -0.36607491428566313,
      "direction": "negative",
      "feature": "numeric__lag1_fantasy_points_per_game",
      "rank": 18
    },
    {
      "absolute_importance": 0.3612068036563794,
      "coefficient": -0.3612068036563794,
      "direction": "negative",
      "feature": "numeric__draft_pick",
      "rank": 19
    },
    {
      "absolute_importance": 0.34512391780363477,
      "coefficient": 0.34512391780363477,
      "direction": "positive",
      "feature": "numeric__weighted_3yr_games_active",
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

- Project-relative path: `models/artifacts/phase4-052d2866899a665a44f3/attempt-331cdaf7eb7f4721aa43c08d469288ee/TE/fantasy_points_per_game/ridge.joblib`
- SHA-256: `6d4c64153e10a9bebd5d1370fa23052aeb54609f61ac974267ff7b974f5f96df`

## Additional metadata

````json
{
  "publication_id": "attempt-331cdaf7eb7f4721aa43c08d469288ee"
}
````
