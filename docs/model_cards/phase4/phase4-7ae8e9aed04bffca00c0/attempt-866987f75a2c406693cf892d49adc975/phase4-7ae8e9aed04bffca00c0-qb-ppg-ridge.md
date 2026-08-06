# Model Card: phase4-7ae8e9aed04bffca00c0-qb-ppg-ridge

- Model ID: `phase4-7ae8e9aed04bffca00c0-qb-ppg-ridge`
- Trained at: 2026-08-05T20:58:13+00:00
- Target: `fantasy_points_per_game`
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
  "position": "QB",
  "target_name": "fantasy_points_per_game",
  "test_mae": 4.312378134300151,
  "test_rows": 66,
  "test_season": 2025,
  "validation_mae": 4.322953671842711,
  "validation_rows": 348,
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
    "candidate_mae": 4.24004050834275,
    "ci95_lower": -0.2688073988829739,
    "ci95_upper": 0.28802816531906433,
    "direction": "uncertain",
    "mae_difference_candidate_minus_reference": 0.00995608765311129,
    "n_resamples": 2000,
    "reference_mae": 4.230084420689638,
    "rows": 348,
    "seed": 42
  },
  "decision_status": "learned_regression_baseline_retained",
  "learned_improvement_status": "regression",
  "reference_metrics": {
    "candidate_name": "age_position_adjusted",
    "candidate_source": "baseline",
    "position": "QB",
    "target_name": "fantasy_points_per_game",
    "test_mae": 4.63816089527217,
    "test_rows": 66,
    "test_season": 2025,
    "validation_mae": 4.230084420689638,
    "validation_rows": 348,
    "validation_seasons": [
      2020,
      2021,
      2022,
      2023,
      2024
    ]
  },
  "selected_champion": "age_position_adjusted",
  "selected_source": "baseline",
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
      "empirical_coverage_p10_p90": 0.7121212121212122,
      "evaluation_scope": "test",
      "mean_interval_width_p10_p90": 12.566326910662735,
      "pinball_loss_p10": 0.8812583400359145,
      "pinball_loss_p50": 2.1561890671500756,
      "pinball_loss_p90": 0.9420423981458009,
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
      "mean_interval_width_p10_p90": 12.566326910662731,
      "pinball_loss_p10": 1.0117156666071119,
      "pinball_loss_p50": 1.9993662352485773,
      "pinball_loss_p90": 0.8865549598963256,
      "position": "QB",
      "prediction_season": 2025,
      "projection_tier": "top",
      "rows": 30,
      "target_name": "fantasy_points_per_game"
    },
    {
      "candidate_name": "ridge",
      "empirical_coverage_p10_p90": 0.6363636363636364,
      "evaluation_scope": "test",
      "mean_interval_width_p10_p90": 12.566326910662735,
      "pinball_loss_p10": 0.7814626809806542,
      "pinball_loss_p50": 2.4426805212017406,
      "pinball_loss_p90": 1.0251988902827185,
      "position": "QB",
      "prediction_season": 2025,
      "projection_tier": "middle",
      "rows": 33,
      "target_name": "fantasy_points_per_game"
    },
    {
      "candidate_name": "ridge",
      "empirical_coverage_p10_p90": 1.0,
      "evaluation_scope": "test",
      "mean_interval_width_p10_p90": 12.566326910662733,
      "pinball_loss_p10": 0.6744373239318079,
      "pinball_loss_p50": 0.5730113915967564,
      "pinball_loss_p90": 0.5821953671344654,
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
      "mean_interval_width_p10_p90": 13.689582765431696,
      "pinball_loss_p10": 1.2222627560647903,
      "pinball_loss_p50": 2.414200885630084,
      "pinball_loss_p90": 1.134276005762924,
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
      "mean_interval_width_p10_p90": 13.689582765431693,
      "pinball_loss_p10": 1.5631758083151044,
      "pinball_loss_p50": 2.331960443500112,
      "pinball_loss_p90": 0.8234514090894867,
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
      "mean_interval_width_p10_p90": 13.689582765431691,
      "pinball_loss_p10": 0.8933768844880912,
      "pinball_loss_p50": 2.253152434117934,
      "pinball_loss_p90": 1.2068013691203237,
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
      "mean_interval_width_p10_p90": 13.689582765431693,
      "pinball_loss_p10": 1.2608856940171094,
      "pinball_loss_p50": 3.336385237960822,
      "pinball_loss_p90": 1.9799793856942127,
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
      "mean_interval_width_p10_p90": 14.035942809919261,
      "pinball_loss_p10": 1.1105128878563786,
      "pinball_loss_p50": 2.311148055727434,
      "pinball_loss_p90": 1.0720415761251332,
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
      "mean_interval_width_p10_p90": 14.035942809919264,
      "pinball_loss_p10": 1.0570655852333855,
      "pinball_loss_p50": 1.9872120246957081,
      "pinball_loss_p90": 1.0432317378535172,
      "position": "QB",
      "prediction_season": 2021,
      "projection_tier": "top",
      "rows": 27,
      "target_name": "fantasy_points_per_game"
    },
    {
      "candidate_name": "ridge",
      "empirical_coverage_p10_p90": 0.7428571428571429,
      "evaluation_scope": "validation",
      "mean_interval_width_p10_p90": 14.035942809919264,
      "pinball_loss_p10": 1.1603960409414333,
      "pinball_loss_p50": 2.4075983921271065,
      "pinball_loss_p90": 0.9212884222654402,
      "position": "QB",
      "prediction_season": 2021,
      "projection_tier": "middle",
      "rows": 35,
      "target_name": "fantasy_points_per_game"
    },
    {
      "candidate_name": "ridge",
      "empirical_coverage_p10_p90": 0.6666666666666666,
      "evaluation_scope": "validation",
      "mean_interval_width_p10_p90": 14.035942809919263,
      "pinball_loss_p10": 1.060040689997029,
      "pinball_loss_p50": 3.206233233038778,
      "pinball_loss_p90": 2.081079245862281,
      "position": "QB",
      "prediction_season": 2021,
      "projection_tier": "lower",
      "rows": 6,
      "target_name": "fantasy_points_per_game"
    },
    {
      "candidate_name": "ridge",
      "empirical_coverage_p10_p90": 0.8648648648648649,
      "evaluation_scope": "validation",
      "mean_interval_width_p10_p90": 14.244481214737704,
      "pinball_loss_p10": 0.8140078769870034,
      "pinball_loss_p50": 1.9756158206949315,
      "pinball_loss_p90": 0.9230735178499887,
      "position": "QB",
      "prediction_season": 2022,
      "projection_tier": "all",
      "rows": 74,
      "target_name": "fantasy_points_per_game"
    },
    {
      "candidate_name": "ridge",
      "empirical_coverage_p10_p90": 0.9,
      "evaluation_scope": "validation",
      "mean_interval_width_p10_p90": 14.244481214737695,
      "pinball_loss_p10": 0.8092244560693971,
      "pinball_loss_p50": 1.835496248200085,
      "pinball_loss_p90": 0.9065271295556221,
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
      "mean_interval_width_p10_p90": 14.244481214737698,
      "pinball_loss_p10": 0.7920797924706748,
      "pinball_loss_p50": 2.1186432901165055,
      "pinball_loss_p90": 1.023651078975381,
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
      "mean_interval_width_p10_p90": 14.2444812147377,
      "pinball_loss_p10": 0.9152284976091912,
      "pinball_loss_p50": 1.8864631257049638,
      "pinball_loss_p90": 0.5870931855657948,
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
      "mean_interval_width_p10_p90": 13.788685474756747,
      "pinball_loss_p10": 0.9422340650563539,
      "pinball_loss_p50": 2.182313215700028,
      "pinball_loss_p90": 1.0203832491378944,
      "position": "QB",
      "prediction_season": 2023,
      "projection_tier": "all",
      "rows": 70,
      "target_name": "fantasy_points_per_game"
    },
    {
      "candidate_name": "ridge",
      "empirical_coverage_p10_p90": 0.8666666666666667,
      "evaluation_scope": "validation",
      "mean_interval_width_p10_p90": 13.78868547475674,
      "pinball_loss_p10": 0.9802505349244367,
      "pinball_loss_p50": 1.894928515828742,
      "pinball_loss_p90": 0.8784218741344199,
      "position": "QB",
      "prediction_season": 2023,
      "projection_tier": "top",
      "rows": 30,
      "target_name": "fantasy_points_per_game"
    },
    {
      "candidate_name": "ridge",
      "empirical_coverage_p10_p90": 0.6666666666666666,
      "evaluation_scope": "validation",
      "mean_interval_width_p10_p90": 13.788685474756742,
      "pinball_loss_p10": 0.9421718927620536,
      "pinball_loss_p50": 2.673584535683737,
      "pinball_loss_p90": 1.2387662857077024,
      "position": "QB",
      "prediction_season": 2023,
      "projection_tier": "middle",
      "rows": 33,
      "target_name": "fantasy_points_per_game"
    },
    {
      "candidate_name": "ridge",
      "empirical_coverage_p10_p90": 1.0,
      "evaluation_scope": "validation",
      "mean_interval_width_p10_p90": 13.788685474756743,
      "pinball_loss_p10": 0.7795994350091286,
      "pinball_loss_p50": 1.0979685637966197,
      "pinball_loss_p90": 0.5992691124665452,
      "position": "QB",
      "prediction_season": 2023,
      "projection_tier": "lower",
      "rows": 7,
      "target_name": "fantasy_points_per_game"
    },
    {
      "candidate_name": "ridge",
      "empirical_coverage_p10_p90": 0.8382352941176471,
      "evaluation_scope": "validation",
      "mean_interval_width_p10_p90": 13.843421865118962,
      "pinball_loss_p10": 0.8501130434185168,
      "pinball_loss_p50": 1.9398928684984384,
      "pinball_loss_p90": 0.9061737862307893,
      "position": "QB",
      "prediction_season": 2024,
      "projection_tier": "all",
      "rows": 68,
      "target_name": "fantasy_points_per_game"
    },
    {
      "candidate_name": "ridge",
      "empirical_coverage_p10_p90": 0.896551724137931,
      "evaluation_scope": "validation",
      "mean_interval_width_p10_p90": 13.84342186511896,
      "pinball_loss_p10": 0.983349348267648,
      "pinball_loss_p50": 1.6456620127624662,
      "pinball_loss_p90": 0.7559649541220871,
      "position": "QB",
      "prediction_season": 2024,
      "projection_tier": "top",
      "rows": 29,
      "target_name": "fantasy_points_per_game"
    },
    {
      "candidate_name": "ridge",
      "empirical_coverage_p10_p90": 0.7894736842105263,
      "evaluation_scope": "validation",
      "mean_interval_width_p10_p90": 13.843421865118964,
      "pinball_loss_p10": 0.7391940058878168,
      "pinball_loss_p50": 2.1425996285560776,
      "pinball_loss_p90": 1.039833558857936,
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
      "mean_interval_width_p10_p90": 13.843421865118962,
      "pinball_loss_p10": 1.2011836289603128,
      "pinball_loss_p50": 2.7697308026513556,
      "pinball_loss_p90": 0.18315855755158342,
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
      "absolute_importance": 1.9960006450605903,
      "coefficient": 1.9960006450605903,
      "direction": "positive",
      "feature": "numeric__lag1_fantasy_points_total",
      "rank": 1
    },
    {
      "absolute_importance": 1.485796585906758,
      "coefficient": 1.485796585906758,
      "direction": "positive",
      "feature": "numeric__lag1_stat_games",
      "rank": 2
    },
    {
      "absolute_importance": 1.2469456451770902,
      "coefficient": 1.2469456451770902,
      "direction": "positive",
      "feature": "numeric__weighted_3yr_passing_yards_per_game",
      "rank": 3
    },
    {
      "absolute_importance": 1.2089508831563676,
      "coefficient": 1.2089508831563676,
      "direction": "positive",
      "feature": "numeric__weighted_3yr_carries_per_game",
      "rank": 4
    },
    {
      "absolute_importance": 1.1792333307245912,
      "coefficient": -1.1792333307245912,
      "direction": "negative",
      "feature": "numeric__age_at_cutoff",
      "rank": 5
    },
    {
      "absolute_importance": 1.0781404271813881,
      "coefficient": 1.0781404271813881,
      "direction": "positive",
      "feature": "categorical__previous_team_NO",
      "rank": 6
    },
    {
      "absolute_importance": 1.0421835486720614,
      "coefficient": 1.0421835486720614,
      "direction": "positive",
      "feature": "numeric__nfl_experience_years",
      "rank": 7
    },
    {
      "absolute_importance": 0.9984860889795102,
      "coefficient": -0.9984860889795102,
      "direction": "negative",
      "feature": "numeric__lag1_games_active",
      "rank": 8
    },
    {
      "absolute_importance": 0.9805625520520475,
      "coefficient": 0.9805625520520475,
      "direction": "positive",
      "feature": "numeric__weighted_3yr_fantasy_points_per_game",
      "rank": 9
    },
    {
      "absolute_importance": 0.9583830718114569,
      "coefficient": -0.9583830718114569,
      "direction": "negative",
      "feature": "categorical__previous_team_JAX",
      "rank": 10
    },
    {
      "absolute_importance": 0.9190704554177177,
      "coefficient": -0.9190704554177177,
      "direction": "negative",
      "feature": "numeric__weighted_3yr_interceptions_per_game",
      "rank": 11
    },
    {
      "absolute_importance": 0.8250894981850524,
      "coefficient": -0.8250894981850524,
      "direction": "negative",
      "feature": "numeric__lag1_fantasy_points_per_game",
      "rank": 12
    },
    {
      "absolute_importance": 0.8006483892041797,
      "coefficient": 0.8006483892041797,
      "direction": "positive",
      "feature": "categorical__previous_team_PHI",
      "rank": 13
    },
    {
      "absolute_importance": 0.7436173543995919,
      "coefficient": -0.7436173543995919,
      "direction": "negative",
      "feature": "categorical__previous_team_ATL",
      "rank": 14
    },
    {
      "absolute_importance": 0.738789197077718,
      "coefficient": -0.738789197077718,
      "direction": "negative",
      "feature": "numeric__draft_round",
      "rank": 15
    },
    {
      "absolute_importance": 0.737834814875486,
      "coefficient": 0.737834814875486,
      "direction": "positive",
      "feature": "categorical__previous_team_SEA",
      "rank": 16
    },
    {
      "absolute_importance": 0.7237425822608893,
      "coefficient": 0.7237425822608893,
      "direction": "positive",
      "feature": "categorical__previous_team_SF",
      "rank": 17
    },
    {
      "absolute_importance": 0.7182039505580208,
      "coefficient": 0.7182039505580208,
      "direction": "positive",
      "feature": "numeric__weighted_3yr_passing_tds_per_game",
      "rank": 18
    },
    {
      "absolute_importance": 0.6509337178658723,
      "coefficient": -0.6509337178658723,
      "direction": "negative",
      "feature": "categorical__previous_team_IND",
      "rank": 19
    },
    {
      "absolute_importance": 0.6074174047982156,
      "coefficient": 0.6074174047982156,
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

- Project-relative path: `models/artifacts/phase4-7ae8e9aed04bffca00c0/attempt-866987f75a2c406693cf892d49adc975/QB/fantasy_points_per_game/ridge.joblib`
- SHA-256: `5aa07ce66ea3f00eddc152dba3e691573bc37523962c69e8199f6c11f4f01176`

## Additional metadata

````json
{
  "publication_id": "attempt-866987f75a2c406693cf892d49adc975"
}
````
