# Modeling Roadmap

The project climbs a model ladder. A more complex model is adopted only when it beats a simpler baseline on future-season evaluation.

1. **Complete:** Build one cutoff-safe row per player and prediction season, with season `t` predicting `t+1`.
2. **Complete:** Persist next-season active games, points per active game, and total points separately from features.
3. **Complete:** Compare previous-season, weighted-history, age/position-adjusted, position-shrinkage, and weighted-component baselines.
4. **Next:** Fit a regularized linear model for an interpretable statistical benchmark.
5. Fit a histogram gradient-boosted model for nonlinear relationships.
6. Add uncertainty estimates and evaluate interval calibration.
7. Compare MAE, RMSE, median AE, rank correlation, top-N overlap, and segment error on expanding chronological folds.
8. Project stat components where practical, then apply the ruleset scoring engine. Keep direct fantasy-point prediction as a benchmark.
9. Archive dated ADP snapshots before claiming a movement model exists.
10. Estimate availability, then simulate rest-of-draft roster construction separately from player projection.
11. Train playoff or championship outcomes only after a documented real-history sample gate is met.

## Phase 3 evidence

The validated PPR feature set has 11,171 rows, 9,804 historical targets, and 1,367 live 2026 rows. Fifteen participation coverage failures leave games active and points per game unavailable for 28 target rows. Its feature fingerprint is `d2bdda170fcbf88ccfe0b3f437615583a0684057eebe1fc12aa65463a47cf9cf`, target fingerprint is `dd759bbf87c146884e68425079b3a759d1d6d4bb434d5bccee6d9d91c98c56a9`, and combined build fingerprint is `f195dcb17a1a386b2f2003d87a06921550235cbec62aecd0f4eda419aa664cd7`.

The five transparent baselines produced 167,565 prediction rows and 80,060 evaluated rows on expanding validation seasons 2020-2024 plus the 2025 test. The 6,464 evaluation candidates comprise 3,102 positive-game, 3,344 zero-game, and 18 missing-games outcomes. Age/position adjustment produced the best aggregate fantasy-points-per-game MAE of 2.581 and total-points MAE of 33.324. See [the complete report](PHASE_3_BASELINE_EVALUATION.md).

The current identity snapshot is cutoff-safe for live 2026 because its August 2026 acquisition predates September 1, so it provides 309 static-position fallbacks. It is not safe for historical entry cohorts: 2,710 current-core historical candidate rows without time-versioned position evidence are excluded and reported. Consequently, historical rookie baseline performance cannot be measured honestly until a historical preseason-position archive exists. Current ADP is likewise unavailable as a historical baseline because no cutoff-safe snapshot archive exists for those folds. No statistical or machine-learning model has been trained yet; Phase 4 starts that work.

Every model card will state training seasons, target, features, leakage controls, baseline comparison, uncertainty behavior, limitations, and intended use.
