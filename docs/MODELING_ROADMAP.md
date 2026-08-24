# Modeling Roadmap

The project climbs a model ladder. A more complex model is adopted only when it beats a simpler baseline on future-season evaluation.

1. **Complete:** Build one cutoff-safe row per player and prediction season, with season `t` predicting `t+1`.
2. **Complete:** Persist next-season active games, points per active game, and total points separately from features.
3. **Complete:** Compare previous-season, weighted-history, age/position-adjusted, position-shrinkage, and weighted-component baselines.
4. **Complete:** Fit position-specific Ridge models as interpretable statistical candidates.
5. **Complete:** Fit position-specific histogram gradient-boosted models for nonlinear relationships.
6. **Complete:** Add training-only residual P10/P50/P90 estimates and evaluate coverage by season, position, and tier.
7. **Complete:** Compare learned candidates and all five baselines on fixed cutoff-safe draft-relevant cohorts, with paired-bootstrap evidence plus pooled-error and top-N ranking safeguards.
8. Project stat components where practical, then apply the ruleset scoring engine. Keep direct fantasy-point prediction as a benchmark.
9. **Complete foundation:** Archive immutable dated ADP snapshots and build honest movement features plus persistence, linear, and exponentially weighted baselines with explicit readiness status.
10. **Complete transparent baseline:** Estimate conditional next-pick availability from source spread with labeled fallback assumptions. Calibration and supervised ML remain unavailable until the sample is sufficient.
11. **Complete engine:** Build an event-sourced snake-draft state, exact lineup assignment, transparent ruleset-aware scoring, and seeded Monte Carlo rest-of-draft comparisons. Production activation remains gated by canonical market mappings.
12. **Complete:** Deliver the Phase 7 application plus Phase 8 Data Center intake, League History workspace, manual-data guides, descriptive roster construction, and draft-only reports.
13. **Locked:** Consider playoff or championship evaluation only after the documented real-history gate is met and an independently reviewed future modeling phase is authorized.

## Phase 3 evidence

The validated PPR feature set preserves separate feature and target tables, including explicit unavailable participation-dependent outcomes. Its current row counts and feature, target, and combined-build fingerprints are published by the generated Phase 3 evaluation so a rebuilt contract is never documented with an earlier fingerprint.

The five transparent baselines run on expanding validation seasons 2020-2024 plus the 2025 test. The evaluation separates positive-game accuracy, zero-game outcomes, and unavailable participation evidence. The age/position adjustment now uses a smooth position-specific performance curve; it does not estimate injury probability or games missed. See [the complete report](PHASE_3_BASELINE_EVALUATION.md) for current counts and metrics.

The current identity snapshot is cutoff-safe for live 2026 because its August 2026 acquisition predates September 1, so it provides 309 static-position fallbacks. It is not safe for historical entry cohorts: 2,710 current-core historical candidate rows without time-versioned position evidence are excluded and reported. Consequently, historical rookie baseline performance cannot be measured honestly until a historical preseason-position archive exists. Current ADP is likewise unavailable as a historical baseline because no cutoff-safe snapshot archive exists for those folds. Phase 4 preserves this frozen evidence rather than changing the Phase 3 contract.

## Phase 4 evidence

Phase 4 registers Ridge and histogram gradient boosting candidates for QB/RB/WR/TE across points per game, games active, and total points. The learned feature contract includes raw `age_at_cutoff` and excludes the deterministic `age_adjustment_factor`; configuration validation prevents both from entering together. Current run IDs, fingerprints, row counts, and champion decisions are published by the generated Phase 4 evaluation.

Selection freezes a cutoff-safe draft-relevant cohort for every validation season using the `weighted_components` total-points baseline: top 12 QB, 24 RB, 36 WR, and 12 TE. A learned candidate must beat the best transparent baseline on cohort MAE with a learned-minus-baseline paired-bootstrap 95% confidence-interval upper bound below zero. It must also stay within the configured pooled-MAE regression tolerance, and a total-points candidate must preserve top-N capture within the configured ranking tolerance. The 2025 test never selects.

Learned P10/P50/P90 values are signed-residual ranges calibrated from earlier out-of-fold training predictions and evaluated by season, position, and tier. Retained baselines are point-only. The 233 live rookies are also explicit point-only fallbacks—QB 21, RB 46, WR 114, TE 52—because historical rookie performance remains unavailable without preseason position snapshots.

Every registered model card states training seasons, target, features, leakage controls, baseline comparison, uncertainty behavior, limitations, intended use, artifact path, artifact hash, and data lineage. DuckDB and registered attempt-scoped hashes are authoritative: deterministic run contracts may have multiple immutable publication attempts, and the six Phase 4 tables are audited and promoted in one rollback-safe transaction. Top-level reports and registry files are convenience mirrors. Draft-facing ranks use the selected points-per-game interval multiplied by 17 healthy games; predicted games active and direct total points remain evaluation targets but do not impose injury assumptions on the draft board. See [the Phase 4 evaluation report](PHASE_4_MODEL_EVALUATION.md).

## Phase 5 evidence

The current Phase 5 build has fingerprint
`7f856f948a77b720aff785ddf09921e8b54b3c6a6418ecd29d06453c9163da16` and snapshot-data fingerprint
`9040796e6913f516b0f9fa116b76df5b46a4326f15801e8567d02cd4b1c3067f`. It verifies and
idempotently normalizes immutable FFC and Sleeper snapshots with 1,573 observations. Duplicate
manifests collapse, the labeled synthetic ESPN fixture is skipped, 1,129 identities have accepted
evidence, and 444 unresolved identities remain source-keyed rather than joined by display name.

The build persists 1,573 cutoff-safe movement features and 4,719 baseline forecast rows.
Persistence is ready for all 1,573 observations. Linear and exponentially weighted forecasts have
zero ready rows because each source/player series has only one dated observation and those methods
require at least three. No later capture is allowed into an earlier feature or forecast.

The 246 FFC availability parameters use observed source spread; the 1,327 Sleeper rows use a
labeled versioned fallback because that response does not report a distribution spread. The
continuity-corrected pick distribution is conditional on the player still being available at the
current pick. It remains explicitly uncalibrated because no linked real-draft outcomes are archived.
A supervised movement or availability model remains unavailable until repeated dated captures can
support chronological evaluation. See [the Phase 5 evaluation report](PHASE_5_ADP_AVAILABILITY_EVALUATION.md).

For current-player comparison, an accepted FantasyPros `AVG` composite is the primary consensus
ordering when present. The health-neutral rules-aware ranking is shown separately as **Experimental
Model Rank**, together with Consensus Rank minus Experimental Model Rank so large disagreements can
be reviewed instead of hidden.

## Phase 6 evidence

Phase 6 now freezes canonical health-neutral PPG-times-17 projections, reviewed market evidence, rules, scoring compatibility, upstream lineage, engine configuration, seed, and simulation count into each local draft session. Picks, undo, and replacement are append-only events protected by idempotent command IDs, optimistic versions, and linked replay hashes. Exact lineup assignment supports overlapping flexible eligibility without a greedy slot-order dependency.

The versioned `phase6-baseline-v1` configuration has fingerprint `17e0337939917fcfcb08ec764d88b43a7001e4c3c776c3ac8597390cb54ad9c9`, defaults to 64 simulation paths, evaluates six candidates, and requires 100% mapping across the compatible market scope. Seeded fixtures prove order-independent simulation, bounded opponent roster/run adjustments, deterministic point-only rows, and recomputable balanced/safe-floor/high-upside scores. A controlled 2-WR/1-FLEX versus 3-WR/2-FLEX comparison changes the replacement boundary without hard-coding a preferred player.

This is engine validation, not a claim that current enhanced production simulation is active. The
live pool has 1,367 canonical projection rows; 877 of 1,278 compatible FFC/Sleeper source
observations are mapped to active projection players (68.6%, below the 100% gate). Multi-source
evidence selects one newest compatible row per canonical player with stable provenance. Market-only
IDs and position-mismatched rows remain archived outside recommendation coverage, while true
same-source/snapshot duplicates still fail closed. Manual state creation, projection-first picks,
undo, replacement, rosters, and replay are available; strict Monte Carlo remains
`identity_mapping_required`. Display names are never used as an unqualified bridge.

No recommendation payload contains or implies a championship probability. See [the Phase 6 evaluation](PHASE_6_DRAFT_ENGINE_EVALUATION.md). The Phase 7 application and Phase 8 history framework are now implemented, while identity review remains the operator prerequisite for live Phase 6 activation.
