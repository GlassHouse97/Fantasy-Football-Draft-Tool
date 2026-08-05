# Model Card: phase4-7ae8e9aed04bffca00c0-rb-total-ridge

- Model ID: `phase4-7ae8e9aed04bffca00c0-rb-total-ridge`
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
  "position": "RB",
  "target_name": "fantasy_points_total",
  "test_mae": 26.890671592261857,
  "test_rows": 294,
  "test_season": 2025,
  "validation_mae": 27.112651056929135,
  "validation_rows": 1488,
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
    "candidate_mae": 23.216781530895723,
    "ci95_lower": -12.896672517899596,
    "ci95_upper": -9.889759363107192,
    "direction": "candidate_lower_mae",
    "mae_difference_candidate_minus_reference": -11.342119918481544,
    "n_resamples": 2000,
    "reference_mae": 34.55890144937727,
    "rows": 1488,
    "seed": 42
  },
  "decision_status": "learned_significant_improvement_selected",
  "learned_improvement_status": "statistically_clear",
  "reference_metrics": {
    "candidate_name": "age_position_adjusted",
    "candidate_source": "baseline",
    "position": "RB",
    "target_name": "fantasy_points_total",
    "test_mae": 33.385817059825676,
    "test_rows": 294,
    "test_season": 2025,
    "validation_mae": 34.55890144937727,
    "validation_rows": 1488,
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
      "empirical_coverage_p10_p90": 0.7687074829931972,
      "evaluation_scope": "test",
      "mean_interval_width_p10_p90": 77.46347685745489,
      "pinball_loss_p10": 7.301965862166065,
      "pinball_loss_p50": 13.445335796130928,
      "pinball_loss_p90": 9.103538335038527,
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
      "mean_interval_width_p10_p90": 77.46347685745489,
      "pinball_loss_p10": 18.418692427778826,
      "pinball_loss_p50": 31.96450955005816,
      "pinball_loss_p90": 19.958127673424567,
      "position": "RB",
      "prediction_season": 2025,
      "projection_tier": "top",
      "rows": 74,
      "target_name": "fantasy_points_total"
    },
    {
      "candidate_name": "ridge",
      "empirical_coverage_p10_p90": 0.8972602739726028,
      "evaluation_scope": "test",
      "mean_interval_width_p10_p90": 77.46347685745489,
      "pinball_loss_p10": 3.1156960731946013,
      "pinball_loss_p50": 9.006877562746377,
      "pinball_loss_p90": 6.529556931672884,
      "position": "RB",
      "prediction_season": 2025,
      "projection_tier": "middle",
      "rows": 146,
      "target_name": "fantasy_points_total"
    },
    {
      "candidate_name": "ridge",
      "empirical_coverage_p10_p90": 0.9864864864864865,
      "evaluation_scope": "test",
      "mean_interval_width_p10_p90": 77.4634768574549,
      "pinball_loss_p10": 4.444636447767275,
      "pinball_loss_p50": 3.6831201783407876,
      "pinball_loss_p90": 3.3273447384279473,
      "position": "RB",
      "prediction_season": 2025,
      "projection_tier": "lower",
      "rows": 74,
      "target_name": "fantasy_points_total"
    },
    {
      "candidate_name": "ridge",
      "empirical_coverage_p10_p90": 0.8245033112582781,
      "evaluation_scope": "validation",
      "mean_interval_width_p10_p90": 93.2914257204783,
      "pinball_loss_p10": 8.655493121487464,
      "pinball_loss_p50": 13.680796178909597,
      "pinball_loss_p90": 8.29477675505575,
      "position": "RB",
      "prediction_season": 2020,
      "projection_tier": "all",
      "rows": 302,
      "target_name": "fantasy_points_total"
    },
    {
      "candidate_name": "ridge",
      "empirical_coverage_p10_p90": 0.4342105263157895,
      "evaluation_scope": "validation",
      "mean_interval_width_p10_p90": 93.29142572047829,
      "pinball_loss_p10": 18.432457572917173,
      "pinball_loss_p50": 29.98678857871681,
      "pinball_loss_p90": 15.3762011565001,
      "position": "RB",
      "prediction_season": 2020,
      "projection_tier": "top",
      "rows": 76,
      "target_name": "fantasy_points_total"
    },
    {
      "candidate_name": "ridge",
      "empirical_coverage_p10_p90": 0.9466666666666667,
      "evaluation_scope": "validation",
      "mean_interval_width_p10_p90": 93.29142572047829,
      "pinball_loss_p10": 4.749462296301208,
      "pinball_loss_p50": 8.005855658454447,
      "pinball_loss_p90": 7.3829655093032365,
      "position": "RB",
      "prediction_season": 2020,
      "projection_tier": "middle",
      "rows": 150,
      "target_name": "fantasy_points_total"
    },
    {
      "candidate_name": "ridge",
      "empirical_coverage_p10_p90": 0.9736842105263158,
      "evaluation_scope": "validation",
      "mean_interval_width_p10_p90": 93.29142572047829,
      "pinball_loss_p10": 6.587800035556946,
      "pinball_loss_p50": 8.575344280000715,
      "pinball_loss_p90": 3.012979812333464,
      "position": "RB",
      "prediction_season": 2020,
      "projection_tier": "lower",
      "rows": 76,
      "target_name": "fantasy_points_total"
    },
    {
      "candidate_name": "ridge",
      "empirical_coverage_p10_p90": 0.8178807947019867,
      "evaluation_scope": "validation",
      "mean_interval_width_p10_p90": 90.9516092354991,
      "pinball_loss_p10": 6.934787486911755,
      "pinball_loss_p50": 14.225919407916376,
      "pinball_loss_p90": 9.403753753366033,
      "position": "RB",
      "prediction_season": 2021,
      "projection_tier": "all",
      "rows": 302,
      "target_name": "fantasy_points_total"
    },
    {
      "candidate_name": "ridge",
      "empirical_coverage_p10_p90": 0.4868421052631579,
      "evaluation_scope": "validation",
      "mean_interval_width_p10_p90": 90.9516092354991,
      "pinball_loss_p10": 11.611268177676072,
      "pinball_loss_p50": 28.465317888882822,
      "pinball_loss_p90": 18.396065639662357,
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
      "mean_interval_width_p10_p90": 90.9516092354991,
      "pinball_loss_p10": 4.741988774305864,
      "pinball_loss_p50": 9.462034144109998,
      "pinball_loss_p90": 7.260436866135316,
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
      "mean_interval_width_p10_p90": 90.9516092354991,
      "pinball_loss_p10": 6.586198992080118,
      "pinball_loss_p50": 9.388926052883562,
      "pinball_loss_p90": 4.641672565551382,
      "position": "RB",
      "prediction_season": 2021,
      "projection_tier": "lower",
      "rows": 76,
      "target_name": "fantasy_points_total"
    },
    {
      "candidate_name": "ridge",
      "empirical_coverage_p10_p90": 0.8215488215488216,
      "evaluation_scope": "validation",
      "mean_interval_width_p10_p90": 85.49354256512882,
      "pinball_loss_p10": 6.792013743757943,
      "pinball_loss_p50": 13.664753041689979,
      "pinball_loss_p90": 9.589124183334405,
      "position": "RB",
      "prediction_season": 2022,
      "projection_tier": "all",
      "rows": 297,
      "target_name": "fantasy_points_total"
    },
    {
      "candidate_name": "ridge",
      "empirical_coverage_p10_p90": 0.43243243243243246,
      "evaluation_scope": "validation",
      "mean_interval_width_p10_p90": 85.49354256512883,
      "pinball_loss_p10": 14.212558630141677,
      "pinball_loss_p50": 30.11870276794186,
      "pinball_loss_p90": 19.88992296697494,
      "position": "RB",
      "prediction_season": 2022,
      "projection_tier": "top",
      "rows": 74,
      "target_name": "fantasy_points_total"
    },
    {
      "candidate_name": "ridge",
      "empirical_coverage_p10_p90": 0.9261744966442953,
      "evaluation_scope": "validation",
      "mean_interval_width_p10_p90": 85.49354256512883,
      "pinball_loss_p10": 3.8296106292120795,
      "pinball_loss_p50": 9.749985799387346,
      "pinball_loss_p90": 7.639933741109021,
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
      "mean_interval_width_p10_p90": 85.49354256512883,
      "pinball_loss_p10": 5.336307560986824,
      "pinball_loss_p50": 5.093240060074478,
      "pinball_loss_p90": 3.2130466955260597,
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
      "mean_interval_width_p10_p90": 82.91417669651312,
      "pinball_loss_p10": 6.814973258882494,
      "pinball_loss_p50": 13.335457824163184,
      "pinball_loss_p90": 9.842813484743418,
      "position": "RB",
      "prediction_season": 2023,
      "projection_tier": "all",
      "rows": 292,
      "target_name": "fantasy_points_total"
    },
    {
      "candidate_name": "ridge",
      "empirical_coverage_p10_p90": 0.3287671232876712,
      "evaluation_scope": "validation",
      "mean_interval_width_p10_p90": 82.91417669651314,
      "pinball_loss_p10": 15.696400255136393,
      "pinball_loss_p50": 31.2675452712867,
      "pinball_loss_p90": 20.977350313111973,
      "position": "RB",
      "prediction_season": 2023,
      "projection_tier": "top",
      "rows": 73,
      "target_name": "fantasy_points_total"
    },
    {
      "candidate_name": "ridge",
      "empirical_coverage_p10_p90": 0.958904109589041,
      "evaluation_scope": "validation",
      "mean_interval_width_p10_p90": 82.91417669651312,
      "pinball_loss_p10": 3.3735490768324996,
      "pinball_loss_p50": 9.38277626172234,
      "pinball_loss_p90": 7.459440291469491,
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
      "mean_interval_width_p10_p90": 82.91417669651311,
      "pinball_loss_p10": 4.8163946267285915,
      "pinball_loss_p50": 3.3087335019213544,
      "pinball_loss_p90": 3.475023042922721,
      "position": "RB",
      "prediction_season": 2023,
      "projection_tier": "lower",
      "rows": 73,
      "target_name": "fantasy_points_total"
    },
    {
      "candidate_name": "ridge",
      "empirical_coverage_p10_p90": 0.8067796610169492,
      "evaluation_scope": "validation",
      "mean_interval_width_p10_p90": 80.47071276822183,
      "pinball_loss_p10": 6.456910675289417,
      "pinball_loss_p50": 12.852877766427993,
      "pinball_loss_p90": 9.919340720183259,
      "position": "RB",
      "prediction_season": 2024,
      "projection_tier": "all",
      "rows": 295,
      "target_name": "fantasy_points_total"
    },
    {
      "candidate_name": "ridge",
      "empirical_coverage_p10_p90": 0.36486486486486486,
      "evaluation_scope": "validation",
      "mean_interval_width_p10_p90": 80.47071276822183,
      "pinball_loss_p10": 13.046751622074522,
      "pinball_loss_p50": 30.82303172742861,
      "pinball_loss_p90": 23.683760171556365,
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
      "mean_interval_width_p10_p90": 80.47071276822183,
      "pinball_loss_p10": 3.687417437116983,
      "pinball_loss_p50": 6.916703584406242,
      "pinball_loss_p90": 6.147123835293908,
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
      "mean_interval_width_p10_p90": 80.47071276822183,
      "pinball_loss_p10": 5.368630620549553,
      "pinball_loss_p50": 6.674853599443557,
      "pinball_loss_p90": 3.648379134739,
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
      "absolute_importance": 23.68066249808821,
      "coefficient": 23.68066249808821,
      "direction": "positive",
      "feature": "numeric__lag1_fantasy_points_total",
      "rank": 1
    },
    {
      "absolute_importance": 18.84937426239564,
      "coefficient": 18.84937426239564,
      "direction": "positive",
      "feature": "numeric__weighted_3yr_rushing_yards_per_game",
      "rank": 2
    },
    {
      "absolute_importance": 16.178158344005862,
      "coefficient": -16.178158344005862,
      "direction": "negative",
      "feature": "categorical__previous_team_HOU",
      "rank": 3
    },
    {
      "absolute_importance": 15.601298212725897,
      "coefficient": -15.601298212725897,
      "direction": "negative",
      "feature": "categorical__previous_team_NYJ",
      "rank": 4
    },
    {
      "absolute_importance": 13.755612290275385,
      "coefficient": 13.755612290275385,
      "direction": "positive",
      "feature": "categorical__previous_team_CIN",
      "rank": 5
    },
    {
      "absolute_importance": 13.277816418524816,
      "coefficient": -13.277816418524816,
      "direction": "negative",
      "feature": "numeric__weighted_3yr_carries_per_game",
      "rank": 6
    },
    {
      "absolute_importance": 11.954214319750367,
      "coefficient": -11.954214319750367,
      "direction": "negative",
      "feature": "categorical__previous_team_BAL",
      "rank": 7
    },
    {
      "absolute_importance": 10.009909605517956,
      "coefficient": 10.009909605517956,
      "direction": "positive",
      "feature": "numeric__lag1_fantasy_points_per_game",
      "rank": 8
    },
    {
      "absolute_importance": 9.304238425533272,
      "coefficient": 9.304238425533272,
      "direction": "positive",
      "feature": "categorical__previous_team_LA",
      "rank": 9
    },
    {
      "absolute_importance": 7.834827692843784,
      "coefficient": 7.834827692843784,
      "direction": "positive",
      "feature": "categorical__previous_team_DAL",
      "rank": 10
    },
    {
      "absolute_importance": 7.538861653247618,
      "coefficient": -7.538861653247618,
      "direction": "negative",
      "feature": "categorical__previous_team_KC",
      "rank": 11
    },
    {
      "absolute_importance": 7.499526439536046,
      "coefficient": -7.499526439536046,
      "direction": "negative",
      "feature": "categorical__previous_team_WAS",
      "rank": 12
    },
    {
      "absolute_importance": 7.483625887531553,
      "coefficient": 7.483625887531553,
      "direction": "positive",
      "feature": "numeric__weighted_3yr_fantasy_points_per_game",
      "rank": 13
    },
    {
      "absolute_importance": 7.424219246805434,
      "coefficient": -7.424219246805434,
      "direction": "negative",
      "feature": "categorical__previous_team_SD",
      "rank": 14
    },
    {
      "absolute_importance": 7.166049361973521,
      "coefficient": 7.166049361973521,
      "direction": "positive",
      "feature": "categorical__previous_team_MIA",
      "rank": 15
    },
    {
      "absolute_importance": 6.973199772615465,
      "coefficient": -6.973199772615465,
      "direction": "negative",
      "feature": "categorical__previous_team_DEN",
      "rank": 16
    },
    {
      "absolute_importance": 6.753702698646668,
      "coefficient": -6.753702698646668,
      "direction": "negative",
      "feature": "numeric__draft_pick",
      "rank": 17
    },
    {
      "absolute_importance": 6.7490579756335976,
      "coefficient": 6.7490579756335976,
      "direction": "positive",
      "feature": "categorical__previous_team_CLE",
      "rank": 18
    },
    {
      "absolute_importance": 6.654893538954603,
      "coefficient": 6.654893538954603,
      "direction": "positive",
      "feature": "categorical__previous_team_NE",
      "rank": 19
    },
    {
      "absolute_importance": 6.030222087685565,
      "coefficient": 6.030222087685565,
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

- Project-relative path: `models/artifacts/phase4-7ae8e9aed04bffca00c0/attempt-866987f75a2c406693cf892d49adc975/RB/fantasy_points_total/ridge.joblib`
- SHA-256: `eede72f5482ca8c2b6ed9bd81c9f9d61fc6b6aaa21074cef934a165ce856e7b5`

## Additional metadata

````json
{
  "publication_id": "attempt-866987f75a2c406693cf892d49adc975"
}
````
