# Modeling Roadmap

The project climbs a model ladder. A more complex model is adopted only when it beats a simpler baseline on future-season evaluation.

1. **Complete:** Build one cutoff-safe row per player and prediction season, with season `t` predicting `t+1`.
2. **Complete:** Persist next-season active games, points per active game, and total points separately from features.
3. **Complete:** Compare previous-season, weighted-history, age/position-adjusted, position-shrinkage, and weighted-component baselines.
4. **Complete:** Fit position-specific Ridge models as interpretable statistical candidates.
5. **Complete:** Fit position-specific histogram gradient-boosted models for nonlinear relationships.
6. **Complete:** Add training-only residual P10/P50/P90 estimates and evaluate coverage by season, position, and tier.
7. **Complete:** Compare learned candidates and all five baselines using MAE, RMSE, median AE, rank correlation, top-N overlap, segment error, and a paired-bootstrap selection gate.
8. Project stat components where practical, then apply the ruleset scoring engine. Keep direct fantasy-point prediction as a benchmark.
9. **Complete foundation:** Archive immutable dated ADP snapshots and build honest movement features plus persistence, linear, and exponentially weighted baselines with explicit readiness status.
10. **Complete transparent baseline:** Estimate conditional next-pick availability from source spread with labeled fallback assumptions. Calibration and supervised ML remain unavailable until the sample is sufficient.
11. **Complete engine:** Build an event-sourced snake-draft state, exact lineup assignment, transparent ruleset-aware scoring, and seeded Monte Carlo rest-of-draft comparisons. Production activation remains gated by canonical market mappings.
12. **Next:** Polish the Phase 7 application, data-center, league-setup, post-draft, export, and learning workflows around the validated service boundaries.
13. Train playoff or championship outcomes only after a documented real-history sample gate is met.

## Phase 3 evidence

The validated PPR feature set has 11,171 rows, 9,804 historical targets, and 1,367 live 2026 rows. Fifteen participation coverage failures leave games active and points per game unavailable for 28 target rows. Its feature fingerprint is `d2bdda170fcbf88ccfe0b3f437615583a0684057eebe1fc12aa65463a47cf9cf`, target fingerprint is `dd759bbf87c146884e68425079b3a759d1d6d4bb434d5bccee6d9d91c98c56a9`, and combined build fingerprint is `f195dcb17a1a386b2f2003d87a06921550235cbec62aecd0f4eda419aa664cd7`.

The five transparent baselines produced 167,565 prediction rows and 80,060 evaluated rows on expanding validation seasons 2020-2024 plus the 2025 test. The 6,464 evaluation candidates comprise 3,102 positive-game, 3,344 zero-game, and 18 missing-games outcomes. Age/position adjustment produced the best aggregate fantasy-points-per-game MAE of 2.581 and total-points MAE of 33.324. See [the complete report](PHASE_3_BASELINE_EVALUATION.md).

The current identity snapshot is cutoff-safe for live 2026 because its August 2026 acquisition predates September 1, so it provides 309 static-position fallbacks. It is not safe for historical entry cohorts: 2,710 current-core historical candidate rows without time-versioned position evidence are excluded and reported. Consequently, historical rookie baseline performance cannot be measured honestly until a historical preseason-position archive exists. Current ADP is likewise unavailable as a historical baseline because no cutoff-safe snapshot archive exists for those folds. Phase 4 preserves this frozen evidence rather than changing the Phase 3 contract.

## Phase 4 evidence

Run `phase4-7ae8e9aed04bffca00c0` has fingerprint `7ae8e9aed04bffca00c04d05e623f8afd20877dcfa09ddf43a8c1a7e8c34db03` and the unchanged Phase 3 feature, target, and build fingerprints. It registers 24 models—Ridge and histogram gradient boosting for QB/RB/WR/TE across three targets—and persists 45,588 predictions, 32,024 evaluable rows, 6,804 live learned-candidate predictions, 84 selection candidates, 12 champion decisions, and a 1,367-row live board.

Selection uses pooled validation MAE across 2020-2024 plus a paired-bootstrap uncertainty gate. A learned candidate must beat the best transparent baseline and have a learned-minus-baseline 95% confidence-interval upper bound below zero. The 2025 test never selects. Learned models clear the gate for 9 of 12 routes: all total-points and games-active routes plus histogram gradient boosting for WR points per game. QB, RB, and TE points per game retain `age_position_adjusted`.

Learned P10/P50/P90 values are signed-residual ranges calibrated from earlier out-of-fold training predictions and evaluated by season, position, and tier. Retained baselines are point-only. The 233 live rookies are also explicit point-only fallbacks—QB 21, RB 46, WR 114, TE 52—because historical rookie performance remains unavailable without preseason position snapshots.

Every registered model card states training seasons, target, features, leakage controls, baseline comparison, uncertainty behavior, limitations, intended use, artifact path, artifact hash, and data lineage. DuckDB and registered attempt-scoped hashes are authoritative: deterministic run contracts may have multiple immutable publication attempts, and the six Phase 4 tables are audited and promoted in one rollback-safe transaction. Top-level reports and registry files are convenience mirrors. See [the Phase 4 evaluation report](PHASE_4_MODEL_EVALUATION.md).

## Phase 5 evidence

The validated Phase 5 build has fingerprint `3446513dfe4b122079ba1ed89b6517821d35cac48821ff1631e25a77f6dd3b6b` and snapshot-data fingerprint `44624854b5c45f80fb0017e6ecdb52c972d4389236d35131b2dbfccb9a0447f2`. It verifies and idempotently normalizes one immutable production FFC snapshot with 246 observations. Duplicate manifests collapse, the labeled synthetic ESPN fixture is skipped, and all 246 unresolved identities remain source-keyed with recorded confidence rather than joined by display name.

The build persists 246 cutoff-safe movement features and 738 baseline forecast rows. Persistence is ready for all 246 observations. Linear and exponentially weighted forecasts have zero ready rows because each source player has only one dated observation and those methods require at least three. No later capture is allowed into an earlier feature or forecast.

All 246 availability parameter rows derive their scale from source-reported standard deviation, so zero configured fallbacks are active in this build. The continuity-corrected pick distribution is conditional on the player still being available at the current pick. It is explicitly uncalibrated because no linked real-draft outcomes are archived. A supervised movement or availability model remains unavailable because one independent capture cannot support chronological train/validation/test evaluation. See [the Phase 5 evaluation report](PHASE_5_ADP_AVAILABILITY_EVALUATION.md).

## Phase 6 evidence

Phase 6 now freezes canonical total-points projections, reviewed market evidence, rules, scoring compatibility, upstream lineage, engine configuration, seed, and simulation count into each local draft session. Picks, undo, and replacement are append-only events protected by idempotent command IDs, optimistic versions, and linked replay hashes. Exact lineup assignment supports overlapping flexible eligibility without a greedy slot-order dependency.

The versioned `phase6-baseline-v1` configuration has fingerprint `17e0337939917fcfcb08ec764d88b43a7001e4c3c776c3ac8597390cb54ad9c9`, defaults to 64 simulation paths, evaluates six candidates, and requires 100% mapping across the compatible market scope. Seeded fixtures prove order-independent simulation, bounded opponent roster/run adjustments, deterministic point-only rows, and recomputable balanced/safe-floor/high-upside scores. A controlled 2-WR/1-FLEX versus 3-WR/2-FLEX comparison changes the replacement boundary without hard-coding a preferred player.

This is engine validation, not a claim that current production recommendations are active. The live pool has 1,367 canonical projection rows and 203 draftable QB/RB/WR/TE ADP rows, but none of those market rows currently have a reviewed canonical player ID. The 43 remaining PK/DEF rows stay in the Phase 5 archive outside this ruleset's recommendation coverage. Manual state creation, picks, undo, replacement, rosters, and replay are available; recommendations and Monte Carlo return `identity_mapping_required`. Display names are never used to bridge the gap.

No recommendation payload contains or implies a championship probability. See [the Phase 6 evaluation](PHASE_6_DRAFT_ENGINE_EVALUATION.md). Phase 7 is next for application/data-center/post-draft polish, while identity review is the operator prerequisite for live Phase 6 activation.
