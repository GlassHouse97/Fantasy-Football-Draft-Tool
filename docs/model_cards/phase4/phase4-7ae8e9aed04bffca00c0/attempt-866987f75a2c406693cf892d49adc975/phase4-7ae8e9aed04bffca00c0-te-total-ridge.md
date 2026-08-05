# Model Card: phase4-7ae8e9aed04bffca00c0-te-total-ridge

- Model ID: `phase4-7ae8e9aed04bffca00c0-te-total-ridge`
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
  "position": "TE",
  "target_name": "fantasy_points_total",
  "test_mae": 16.77896828082317,
  "test_rows": 237,
  "test_season": 2025,
  "validation_mae": 19.315675425987592,
  "validation_rows": 1160,
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
    "candidate_mae": 16.398392683579086,
    "ci95_lower": -8.488550161377646,
    "ci95_upper": -6.028367519894714,
    "direction": "candidate_lower_mae",
    "mae_difference_candidate_minus_reference": -7.287755124346365,
    "n_resamples": 2000,
    "reference_mae": 23.68614780792545,
    "rows": 1160,
    "seed": 42
  },
  "decision_status": "learned_significant_improvement_selected",
  "learned_improvement_status": "statistically_clear",
  "reference_metrics": {
    "candidate_name": "age_position_adjusted",
    "candidate_source": "baseline",
    "position": "TE",
    "target_name": "fantasy_points_total",
    "test_mae": 22.04052262824578,
    "test_rows": 237,
    "test_season": 2025,
    "validation_mae": 23.68614780792545,
    "validation_rows": 1160,
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
      "empirical_coverage_p10_p90": 0.810126582278481,
      "evaluation_scope": "test",
      "mean_interval_width_p10_p90": 52.01466318225574,
      "pinball_loss_p10": 4.6534591748032685,
      "pinball_loss_p50": 8.389484140411586,
      "pinball_loss_p90": 6.006438559896319,
      "position": "TE",
      "prediction_season": 2025,
      "projection_tier": "all",
      "rows": 237,
      "target_name": "fantasy_points_total"
    },
    {
      "candidate_name": "ridge",
      "empirical_coverage_p10_p90": 0.423728813559322,
      "evaluation_scope": "test",
      "mean_interval_width_p10_p90": 52.01466318225577,
      "pinball_loss_p10": 10.548903933182785,
      "pinball_loss_p50": 20.138358238106054,
      "pinball_loss_p90": 13.993597870890857,
      "position": "TE",
      "prediction_season": 2025,
      "projection_tier": "top",
      "rows": 59,
      "target_name": "fantasy_points_total"
    },
    {
      "candidate_name": "ridge",
      "empirical_coverage_p10_p90": 0.907563025210084,
      "evaluation_scope": "test",
      "mean_interval_width_p10_p90": 52.014663182255724,
      "pinball_loss_p10": 2.43805422551703,
      "pinball_loss_p50": 5.143378454352253,
      "pinball_loss_p90": 4.045152866148083,
      "position": "TE",
      "prediction_season": 2025,
      "projection_tier": "middle",
      "rows": 119,
      "target_name": "fantasy_points_total"
    },
    {
      "candidate_name": "ridge",
      "empirical_coverage_p10_p90": 1.0,
      "evaluation_scope": "test",
      "mean_interval_width_p10_p90": 52.01466318225575,
      "pinball_loss_p10": 3.226373551424811,
      "pinball_loss_p50": 3.1878401552774753,
      "pinball_loss_p90": 1.9750927668007647,
      "position": "TE",
      "prediction_season": 2025,
      "projection_tier": "lower",
      "rows": 59,
      "target_name": "fantasy_points_total"
    },
    {
      "candidate_name": "ridge",
      "empirical_coverage_p10_p90": 0.8222222222222222,
      "evaluation_scope": "validation",
      "mean_interval_width_p10_p90": 69.00831525264446,
      "pinball_loss_p10": 5.647618003661067,
      "pinball_loss_p50": 11.671857816248195,
      "pinball_loss_p90": 8.270834934403114,
      "position": "TE",
      "prediction_season": 2020,
      "projection_tier": "all",
      "rows": 225,
      "target_name": "fantasy_points_total"
    },
    {
      "candidate_name": "ridge",
      "empirical_coverage_p10_p90": 0.6071428571428571,
      "evaluation_scope": "validation",
      "mean_interval_width_p10_p90": 69.00831525264445,
      "pinball_loss_p10": 7.333439687935814,
      "pinball_loss_p50": 19.216670390016592,
      "pinball_loss_p90": 14.809330698132786,
      "position": "TE",
      "prediction_season": 2020,
      "projection_tier": "top",
      "rows": 56,
      "target_name": "fantasy_points_total"
    },
    {
      "candidate_name": "ridge",
      "empirical_coverage_p10_p90": 0.8672566371681416,
      "evaluation_scope": "validation",
      "mean_interval_width_p10_p90": 69.00831525264446,
      "pinball_loss_p10": 4.9382749084788875,
      "pinball_loss_p50": 9.19562505256483,
      "pinball_loss_p90": 8.278534251654715,
      "position": "TE",
      "prediction_season": 2020,
      "projection_tier": "middle",
      "rows": 113,
      "target_name": "fantasy_points_total"
    },
    {
      "candidate_name": "ridge",
      "empirical_coverage_p10_p90": 0.9464285714285714,
      "evaluation_scope": "validation",
      "mean_interval_width_p10_p90": 69.00831525264445,
      "pinball_loss_p10": 5.393149350736077,
      "pinball_loss_p50": 9.123729212055155,
      "pinball_loss_p90": 1.716803048362174,
      "position": "TE",
      "prediction_season": 2020,
      "projection_tier": "lower",
      "rows": 56,
      "target_name": "fantasy_points_total"
    },
    {
      "candidate_name": "ridge",
      "empirical_coverage_p10_p90": 0.8296943231441049,
      "evaluation_scope": "validation",
      "mean_interval_width_p10_p90": 71.47640926005693,
      "pinball_loss_p10": 4.8073263684595195,
      "pinball_loss_p50": 9.677106492462006,
      "pinball_loss_p90": 6.771405152481891,
      "position": "TE",
      "prediction_season": 2021,
      "projection_tier": "all",
      "rows": 229,
      "target_name": "fantasy_points_total"
    },
    {
      "candidate_name": "ridge",
      "empirical_coverage_p10_p90": 0.45614035087719296,
      "evaluation_scope": "validation",
      "mean_interval_width_p10_p90": 71.47640926005693,
      "pinball_loss_p10": 7.466530631341403,
      "pinball_loss_p50": 21.548949894227746,
      "pinball_loss_p90": 14.26615898554186,
      "position": "TE",
      "prediction_season": 2021,
      "projection_tier": "top",
      "rows": 57,
      "target_name": "fantasy_points_total"
    },
    {
      "candidate_name": "ridge",
      "empirical_coverage_p10_p90": 0.9304347826086956,
      "evaluation_scope": "validation",
      "mean_interval_width_p10_p90": 71.47640926005693,
      "pinball_loss_p10": 3.6484290891816302,
      "pinball_loss_p50": 5.866288257521067,
      "pinball_loss_p90": 5.093750713869782,
      "position": "TE",
      "prediction_season": 2021,
      "projection_tier": "middle",
      "rows": 115,
      "target_name": "fantasy_points_total"
    },
    {
      "candidate_name": "ridge",
      "empirical_coverage_p10_p90": 1.0,
      "evaluation_scope": "validation",
      "mean_interval_width_p10_p90": 71.47640926005694,
      "pinball_loss_p10": 4.486248195348813,
      "pinball_loss_p50": 5.493756020840272,
      "pinball_loss_p90": 2.66139273065688,
      "position": "TE",
      "prediction_season": 2021,
      "projection_tier": "lower",
      "rows": 57,
      "target_name": "fantasy_points_total"
    },
    {
      "candidate_name": "ridge",
      "empirical_coverage_p10_p90": 0.8504273504273504,
      "evaluation_scope": "validation",
      "mean_interval_width_p10_p90": 65.12892897495885,
      "pinball_loss_p10": 6.060954406502393,
      "pinball_loss_p50": 9.213385530601851,
      "pinball_loss_p90": 5.757268228963853,
      "position": "TE",
      "prediction_season": 2022,
      "projection_tier": "all",
      "rows": 234,
      "target_name": "fantasy_points_total"
    },
    {
      "candidate_name": "ridge",
      "empirical_coverage_p10_p90": 0.5423728813559322,
      "evaluation_scope": "validation",
      "mean_interval_width_p10_p90": 65.12892897495885,
      "pinball_loss_p10": 16.02538956927882,
      "pinball_loss_p50": 21.54192122304508,
      "pinball_loss_p90": 9.996168569572387,
      "position": "TE",
      "prediction_season": 2022,
      "projection_tier": "top",
      "rows": 59,
      "target_name": "fantasy_points_total"
    },
    {
      "candidate_name": "ridge",
      "empirical_coverage_p10_p90": 0.9310344827586207,
      "evaluation_scope": "validation",
      "mean_interval_width_p10_p90": 65.12892897495884,
      "pinball_loss_p10": 2.3695378691199274,
      "pinball_loss_p50": 6.148293217848688,
      "pinball_loss_p90": 4.922974937385447,
      "position": "TE",
      "prediction_season": 2022,
      "projection_tier": "middle",
      "rows": 116,
      "target_name": "fantasy_points_total"
    },
    {
      "candidate_name": "ridge",
      "empirical_coverage_p10_p90": 1.0,
      "evaluation_scope": "validation",
      "mean_interval_width_p10_p90": 65.12892897495885,
      "pinball_loss_p10": 3.354219554511834,
      "pinball_loss_p50": 2.911133029334329,
      "pinball_loss_p90": 3.1586733429840517,
      "position": "TE",
      "prediction_season": 2022,
      "projection_tier": "lower",
      "rows": 59,
      "target_name": "fantasy_points_total"
    },
    {
      "candidate_name": "ridge",
      "empirical_coverage_p10_p90": 0.8042553191489362,
      "evaluation_scope": "validation",
      "mean_interval_width_p10_p90": 57.43230209795209,
      "pinball_loss_p10": 4.395736574682693,
      "pinball_loss_p50": 8.755147311185867,
      "pinball_loss_p90": 5.95471735944993,
      "position": "TE",
      "prediction_season": 2023,
      "projection_tier": "all",
      "rows": 235,
      "target_name": "fantasy_points_total"
    },
    {
      "candidate_name": "ridge",
      "empirical_coverage_p10_p90": 0.3898305084745763,
      "evaluation_scope": "validation",
      "mean_interval_width_p10_p90": 57.43230209795212,
      "pinball_loss_p10": 8.966285458057477,
      "pinball_loss_p50": 19.387489350483616,
      "pinball_loss_p90": 13.431916874882663,
      "position": "TE",
      "prediction_season": 2023,
      "projection_tier": "top",
      "rows": 59,
      "target_name": "fantasy_points_total"
    },
    {
      "candidate_name": "ridge",
      "empirical_coverage_p10_p90": 0.9145299145299145,
      "evaluation_scope": "validation",
      "mean_interval_width_p10_p90": 57.43230209795208,
      "pinball_loss_p10": 2.5407782114594535,
      "pinball_loss_p50": 5.4636745446145945,
      "pinball_loss_p90": 4.057616271444654,
      "position": "TE",
      "prediction_season": 2023,
      "projection_tier": "middle",
      "rows": 117,
      "target_name": "fantasy_points_total"
    },
    {
      "candidate_name": "ridge",
      "empirical_coverage_p10_p90": 1.0,
      "evaluation_scope": "validation",
      "mean_interval_width_p10_p90": 57.432302097952125,
      "pinball_loss_p10": 3.503664445496365,
      "pinball_loss_p50": 4.649963131020984,
      "pinball_loss_p90": 2.2395657642988467,
      "position": "TE",
      "prediction_season": 2023,
      "projection_tier": "lower",
      "rows": 59,
      "target_name": "fantasy_points_total"
    },
    {
      "candidate_name": "ridge",
      "empirical_coverage_p10_p90": 0.8059071729957806,
      "evaluation_scope": "validation",
      "mean_interval_width_p10_p90": 54.587558246671264,
      "pinball_loss_p10": 5.012717238474025,
      "pinball_loss_p50": 9.061073921323413,
      "pinball_loss_p90": 6.665308224853212,
      "position": "TE",
      "prediction_season": 2024,
      "projection_tier": "all",
      "rows": 237,
      "target_name": "fantasy_points_total"
    },
    {
      "candidate_name": "ridge",
      "empirical_coverage_p10_p90": 0.423728813559322,
      "evaluation_scope": "validation",
      "mean_interval_width_p10_p90": 54.587558246671236,
      "pinball_loss_p10": 11.781403629101005,
      "pinball_loss_p50": 21.92786043061075,
      "pinball_loss_p90": 16.353443386140626,
      "position": "TE",
      "prediction_season": 2024,
      "projection_tier": "top",
      "rows": 59,
      "target_name": "fantasy_points_total"
    },
    {
      "candidate_name": "ridge",
      "empirical_coverage_p10_p90": 0.9159663865546218,
      "evaluation_scope": "validation",
      "mean_interval_width_p10_p90": 54.58755824667128,
      "pinball_loss_p10": 2.3984711728556807,
      "pinball_loss_p50": 5.089026568903679,
      "pinball_loss_p90": 3.9951665951449846,
      "position": "TE",
      "prediction_season": 2024,
      "projection_tier": "middle",
      "rows": 119,
      "target_name": "fantasy_points_total"
    },
    {
      "candidate_name": "ridge",
      "empirical_coverage_p10_p90": 0.9661016949152542,
      "evaluation_scope": "validation",
      "mean_interval_width_p10_p90": 54.58755824667125,
      "pinball_loss_p10": 3.516832234433195,
      "pinball_loss_p50": 4.205704953357232,
      "pinball_loss_p90": 2.362712960773913,
      "position": "TE",
      "prediction_season": 2024,
      "projection_tier": "lower",
      "rows": 59,
      "target_name": "fantasy_points_total"
    }
  ],
  "empirical_not_guaranteed": true,
  "method": "training-only signed out-of-fold residual quantiles",
  "operational_center": "training_only_residual_adjusted_p50",
  "residual_rows": 709,
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
      "absolute_importance": 21.30899630368599,
      "coefficient": 21.30899630368599,
      "direction": "positive",
      "feature": "numeric__lag1_fantasy_points_total",
      "rank": 1
    },
    {
      "absolute_importance": 14.850093244036596,
      "coefficient": 14.850093244036596,
      "direction": "positive",
      "feature": "categorical__previous_team_KC",
      "rank": 2
    },
    {
      "absolute_importance": 11.742265039620335,
      "coefficient": 11.742265039620335,
      "direction": "positive",
      "feature": "numeric__weighted_3yr_receiving_yards_per_game",
      "rank": 3
    },
    {
      "absolute_importance": 9.510940175888985,
      "coefficient": -9.510940175888985,
      "direction": "negative",
      "feature": "categorical__previous_team_WAS",
      "rank": 4
    },
    {
      "absolute_importance": 8.800873916610556,
      "coefficient": -8.800873916610556,
      "direction": "negative",
      "feature": "numeric__weighted_3yr_passing_tds_per_game",
      "rank": 5
    },
    {
      "absolute_importance": 8.540389693225814,
      "coefficient": 8.540389693225814,
      "direction": "positive",
      "feature": "categorical__previous_team_OAK",
      "rank": 6
    },
    {
      "absolute_importance": 7.901303323861442,
      "coefficient": -7.901303323861442,
      "direction": "negative",
      "feature": "categorical__previous_team_NYJ",
      "rank": 7
    },
    {
      "absolute_importance": 6.5058193938725335,
      "coefficient": 6.5058193938725335,
      "direction": "positive",
      "feature": "categorical__previous_team_LA",
      "rank": 8
    },
    {
      "absolute_importance": 6.478760946298971,
      "coefficient": -6.478760946298971,
      "direction": "negative",
      "feature": "categorical__previous_team_NYG",
      "rank": 9
    },
    {
      "absolute_importance": 6.342819040746689,
      "coefficient": -6.342819040746689,
      "direction": "negative",
      "feature": "categorical__previous_team_LAC",
      "rank": 10
    },
    {
      "absolute_importance": 6.147258200917489,
      "coefficient": 6.147258200917489,
      "direction": "positive",
      "feature": "numeric__weighted_3yr_rushing_yards_per_game",
      "rank": 11
    },
    {
      "absolute_importance": 6.057148881476831,
      "coefficient": 6.057148881476831,
      "direction": "positive",
      "feature": "categorical__previous_team_DET",
      "rank": 12
    },
    {
      "absolute_importance": 5.917635577593893,
      "coefficient": -5.917635577593893,
      "direction": "negative",
      "feature": "categorical__previous_team_CIN",
      "rank": 13
    },
    {
      "absolute_importance": 5.911661098575051,
      "coefficient": 5.911661098575051,
      "direction": "positive",
      "feature": "numeric__weighted_3yr_passing_yards_per_game",
      "rank": 14
    },
    {
      "absolute_importance": 5.77518405564964,
      "coefficient": -5.77518405564964,
      "direction": "negative",
      "feature": "categorical__previous_team_NE",
      "rank": 15
    },
    {
      "absolute_importance": 5.750654052671402,
      "coefficient": -5.750654052671402,
      "direction": "negative",
      "feature": "categorical__previous_team_MIA",
      "rank": 16
    },
    {
      "absolute_importance": 5.736288092099159,
      "coefficient": 5.736288092099159,
      "direction": "positive",
      "feature": "categorical__previous_team_SF",
      "rank": 17
    },
    {
      "absolute_importance": 5.515576967603814,
      "coefficient": 5.515576967603814,
      "direction": "positive",
      "feature": "categorical__previous_team_PHI",
      "rank": 18
    },
    {
      "absolute_importance": 5.3470270353635385,
      "coefficient": 5.3470270353635385,
      "direction": "positive",
      "feature": "categorical__previous_team_ARI",
      "rank": 19
    },
    {
      "absolute_importance": 4.761604816343898,
      "coefficient": -4.761604816343898,
      "direction": "negative",
      "feature": "categorical__previous_team_DEN",
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

- Project-relative path: `models/artifacts/phase4-7ae8e9aed04bffca00c0/attempt-866987f75a2c406693cf892d49adc975/TE/fantasy_points_total/ridge.joblib`
- SHA-256: `a9e3d988fb6e4eb0e25f86169dddae42a33bd2cb7fcce58a0a8dfef89ebccad2`

## Additional metadata

````json
{
  "publication_id": "attempt-866987f75a2c406693cf892d49adc975"
}
````
