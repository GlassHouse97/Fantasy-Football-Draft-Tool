# Phase 3 Transparent Baseline Evaluation

Status: **PASSED**

Feature fingerprint: `d2bdda170fcbf88ccfe0b3f437615583a0684057eebe1fc12aa65463a47cf9cf`

Target fingerprint: `dd759bbf87c146884e68425079b3a759d1d6d4bb434d5bccee6d9d91c98c56a9`

Build fingerprint: `f195dcb17a1a386b2f2003d87a06921550235cbec62aecd0f4eda419aa664cd7`

Prediction rows: 167,565

Evaluated rows: 80,060

Rows excluded for unavailable actuals: 16,900

Sparse/entry fallback player-seasons: 2,770

## Chronological folds

| Label | Training prediction seasons | Evaluation season |
|---|---|---|
| validation | 2016-2019 | 2020 |
| validation | 2016-2020 | 2021 |
| validation | 2016-2021 | 2022 |
| validation | 2016-2022 | 2023 |
| validation | 2016-2023 | 2024 |
| test | 2016-2024 | 2025 |

## Candidate outcome availability

| Position | Candidates | Positive games | Zero games | Missing games |
|---|---:|---:|---:|---:|
| ALL | 6464 | 3102 | 3344 | 18 |
| QB | 742 | 414 | 328 | 0 |
| RB | 1782 | 814 | 963 | 5 |
| TE | 1397 | 687 | 706 | 4 |
| WR | 2543 | 1187 | 1347 | 9 |

## Aggregate metrics

| Target | Baseline | Rows | MAE | RMSE | Median AE | Spearman |
|---|---|---:|---:|---:|---:|---:|
| fantasy_points_per_game | previous_season | 3102 | 2.855 | 3.994 | 2.082 | 0.718329 |
| fantasy_points_per_game | weighted_history | 3102 | 2.683 | 3.768 | 1.869 | 0.749172 |
| fantasy_points_per_game | age_position_adjusted | 3102 | 2.581 | 3.643 | 1.784 | 0.753173 |
| fantasy_points_per_game | position_shrinkage | 3102 | 2.793 | 3.637 | 2.181 | 0.740834 |
| fantasy_points_per_game | weighted_components | 3102 | 2.683 | 3.768 | 1.869 | 0.749173 |
| games_active | previous_season | 6446 | 6.946 | 8.297 | 8.000 | 0.410308 |
| games_active | weighted_history | 6446 | 5.923 | 7.450 | 5.000 | 0.495209 |
| games_active | age_position_adjusted | 6446 | 5.923 | 7.450 | 5.000 | 0.495209 |
| games_active | position_shrinkage | 6446 | 7.019 | 8.091 | 7.606 | 0.456297 |
| games_active | weighted_components | 6446 | 5.923 | 7.450 | 5.000 | 0.495209 |
| fantasy_points_total | previous_season | 6464 | 45.147 | 58.763 | 42.500 | 0.378813 |
| fantasy_points_total | weighted_history | 6464 | 35.440 | 53.297 | 22.473 | 0.539006 |
| fantasy_points_total | age_position_adjusted | 6464 | 33.324 | 50.273 | 21.383 | 0.551965 |
| fantasy_points_total | position_shrinkage | 6464 | 43.467 | 54.182 | 37.245 | 0.479153 |
| fantasy_points_total | weighted_components | 6464 | 35.440 | 53.297 | 22.473 | 0.539011 |

## Positive-game aggregate metrics

This diagnostic conditions on recording at least one active game; candidate selection itself never uses the outcome.

| Target | Baseline | Rows | MAE | RMSE | Median AE | Spearman |
|---|---|---:|---:|---:|---:|---:|
| fantasy_points_per_game | previous_season | 3102 | 2.855 | 3.994 | 2.082 | 0.718329 |
| fantasy_points_per_game | weighted_history | 3102 | 2.683 | 3.768 | 1.869 | 0.749172 |
| fantasy_points_per_game | age_position_adjusted | 3102 | 2.581 | 3.643 | 1.784 | 0.753173 |
| fantasy_points_per_game | position_shrinkage | 3102 | 2.793 | 3.637 | 2.181 | 0.740834 |
| fantasy_points_per_game | weighted_components | 3102 | 2.683 | 3.768 | 1.869 | 0.749173 |
| games_active | previous_season | 3102 | 4.008 | 5.456 | 3.000 | 0.434938 |
| games_active | weighted_history | 3102 | 3.754 | 5.053 | 2.750 | 0.463431 |
| games_active | age_position_adjusted | 3102 | 3.754 | 5.053 | 2.750 | 0.463431 |
| games_active | position_shrinkage | 3102 | 3.818 | 4.825 | 3.035 | 0.454491 |
| games_active | weighted_components | 3102 | 3.754 | 5.053 | 2.750 | 0.463431 |
| fantasy_points_total | previous_season | 3102 | 43.760 | 63.806 | 30.000 | 0.704217 |
| fantasy_points_total | weighted_history | 3102 | 41.222 | 59.960 | 26.534 | 0.740475 |
| fantasy_points_total | age_position_adjusted | 3102 | 39.872 | 58.049 | 25.716 | 0.744669 |
| fantasy_points_total | position_shrinkage | 3102 | 42.861 | 58.198 | 30.809 | 0.724763 |
| fantasy_points_total | weighted_components | 3102 | 41.222 | 59.960 | 26.534 | 0.740477 |

## Honest limitations

- These are transparent heuristics, not a trained statistical or ML model.
- Games active use mapped positive snap-count participation, not roster status.
- Historical archive acquisition timestamps are provenance, not claimed cutoffs.
- Rookies and players without history receive an explicit position prior only when their position is available before the prediction cutoff.
- The August 2026 identity snapshot predates the live 2026 cutoff; it is never backfilled into historical entry-cohort rows. Historical candidates without time-versioned preseason position evidence are excluded and counted.
- The four-year-history plus two-entry-cohort candidate universe is a cutoff-safe preseason proxy, not a historical roster or ADP list.
- All-candidate games-active metrics measure attrition; active-only segments describe projection error after a player records a game.

## Upstream feature-quality warnings

- **missing_participation_for_scoring_rows** (15): Core-position games with nonzero stats or opportunities lack complete mapped positive-snap participation. Their total points are retained, while games-active and PPG are null for the affected player-season.
- **target_games_active_unavailable** (28): Historical candidate outcomes lack complete positive-snap evidence. Total points remain available, but games active and points per game are null rather than inferred as zero.
- **target_scorers_outside_candidate_universe** (1117): Completed-season scorers lacked cutoff-safe candidate evidence under the four-year history plus two-cohort entry policy; they are counted but were not selected from future outcomes.
- **target_active_players_outside_candidate_universe** (1390): Completed-season active players lacked cutoff-safe candidate evidence under the four-year history plus two-cohort entry policy; they are counted without using target activity for selection.
- **candidate_position_unavailable_at_cutoff** (2710): Current-core entry-cohort candidates had no historical position evidence available before the preseason cutoff. The latest player snapshot was not backfilled into those historical rows.

## Unavailable comparison

- **current_adp**: No cutoff-safe historical ADP archive exists for the expanding folds; the current 2026 snapshot is not backfilled into the past.
