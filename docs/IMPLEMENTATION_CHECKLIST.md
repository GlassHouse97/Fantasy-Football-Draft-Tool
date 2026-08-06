# Implementation Checklist

## Phase 0 — inspect and plan

- [x] Inspect the empty project directory and requested remote repository.
- [x] Record local Python, Git, GitHub CLI, R, Quarto, and dependency-manager availability.
- [x] Confirm current official nflreadpy, FFC ADP, and Sleeper interfaces.
- [x] Define architecture, assumptions, packaging, linting, typing, and tests.

## Phase 1 — project and data foundation

- [x] Scaffold the package, CLI, configuration, data layout, documentation, and UI shell.
- [x] Implement immutable raw archives, SHA-256 hashing, and source manifests.
- [x] Create the DuckDB warehouse and canonical empty tables.
- [x] Create required and optional manual import templates.
- [x] Implement nflverse player and weekly-stat downloads with offline reuse.
- [x] Normalize manifest-backed nflverse captures into canonical DuckDB tables.
- [x] Verify raw hashes and load both tables transactionally and idempotently.
- [x] Report excluded placeholder rows, unresolved IDs, duplicates, and identity conflicts.
- [x] Implement timestamped FFC ADP snapshots and normalization.
- [x] Implement validated manual ESPN ADP archiving.
- [x] Add small labeled fixtures and deterministic tests.
- [ ] Add optional Sleeper league import.
- [ ] Add league-history package import.

## Phase 2 — scoring, rules, and identity (complete)

- [x] Implement deterministic normalized rules and SHA-256 fingerprints.
- [x] Implement configurable component-based scoring.
- [x] Implement explicit FLEX and SUPERFLEX slot eligibility.
- [x] Implement starter-demand estimates and two replacement definitions.
- [x] Add a plain-English learning chapter and executable notebook.
- [x] Define identity records with mapping confidence and conflict rules.
- [x] Build a deterministic review queue from verified nflverse, FFC, and ESPN evidence.
- [x] Keep all name-derived candidates pending until explicit human approval.
- [x] Exclude FFC team-defense rows from the canonical player identity workflow.
- [x] Validate and immutably archive manual override worksheets.
- [x] Persist reviewed source mappings and preserve them across repeat imports and nflverse reloads.

## Phase 3 — projection baselines (complete)

- [x] Archive nflverse/PFR game-level snap counts immutably with hashes, manifests, and offline reuse.
- [x] Load mapped snap participation transactionally and idempotently.
- [x] Define an active game as positive offense, defense, or special-teams snaps.
- [x] Preserve historical weekly position and static-player source provenance, including the identity snapshot acquisition time.
- [x] Define regular-season aggregation, postseason exclusion, and September 1 cutoff semantics.
- [x] Build 11,171 `player_season_features` rows idempotently with explicit provenance and row accounting, including 1,367 live 2026 rows.
- [x] Persist 9,804 future outcomes separately in `player_season_targets`.
- [x] Add rookie/sparse-history fallbacks and explicit missingness indicators.
- [x] Allow static position only from an identity snapshot available by the preseason cutoff; use it for 309 rows in the validated build.
- [x] Exclude and report 2,710 historical entry-cohort candidates without cutoff-safe position evidence instead of leaking the current snapshot backward.
- [x] Keep 15 participation coverage failures and 28 affected target rows nullable instead of inventing games active or points per game.
- [x] Report 1,117 target scorers and 1,390 active target players outside the cutoff-safe candidate universe.
- [x] Prove `t -> t+1` isolation, target exclusion, source provenance, and chronological folds with deterministic tests.
- [x] Evaluate expanding 2020-2025 folds using previous-season, weighted-history, age/position-adjusted, position-shrinkage, and weighted-component baselines.
- [x] Produce 167,565 baseline prediction rows and evaluate 80,060 rows with MAE, RMSE, median AE, rank, top-N, and segment metrics.
- [x] Record the validated feature fingerprint `d2bdda170fcbf88ccfe0b3f437615583a0684057eebe1fc12aa65463a47cf9cf`, target fingerprint `dd759bbf87c146884e68425079b3a759d1d6d4bb434d5bccee6d9d91c98c56a9`, and build fingerprint `f195dcb17a1a386b2f2003d87a06921550235cbec62aecd0f4eda419aa664cd7`.
- [x] Publish the learning chapter, executable notebook, and Phase 3 evaluation report.
- [x] Keep historical ADP and historical rookie baseline performance marked unavailable where cutoff-safe archives do not exist.

## Phase 4 — statistical and ML player models (complete)

- [x] Freeze the validated Phase 3 feature, target, build, scoring, baseline-report, and fold contract.
- [x] Build position-specific, fold-local preprocessing and nested chronological tuning.
- [x] Train Ridge and histogram gradient boosting for four positions and three targets; register 24 final estimators.
- [x] Persist 45,588 predictions, including 32,024 evaluable and 6,804 live learned-candidate rows.
- [x] Compare 84 learned/baseline candidates across 12 position/target routes.
- [x] Select champions using pooled 2020-2024 MAE plus a paired-bootstrap confidence gate; reserve 2025 as a selection-blind test.
- [x] Select learned models for all total-points and games-active routes plus histogram gradient boosting for WR points per game.
- [x] Retain `age_position_adjusted` for QB, RB, and TE points per game when learned candidates do not clear the gate.
- [x] Fit empirical P10/P50/P90 ranges from earlier out-of-fold training residuals and report coverage by season, position, and tier.
- [x] Keep retained baselines and rookie fallbacks honest point estimates with `P10=P50=P90`.
- [x] Publish a complete 1,367-row live board with explanations and explicit method/status labels.
- [x] Keep 233 rookies out of learned models and label point-only fallbacks: QB 21, RB 46, WR 114, and TE 52.
- [x] Write each forced attempt to immutable `<run_id>/<publication_id>/` report, registry, plot, model-card, and serialized-artifact paths with registered SHA-256 hashes.
- [x] Stage, audit, and promote all six Phase 4 tables inside one rollback-safe DuckDB transaction.
- [x] Require one complete current run with reconciled lineage, counts, chronology, board coverage, and file hashes before audit/status/app availability.
- [x] Record run ID `phase4-7ae8e9aed04bffca00c0` and run fingerprint `7ae8e9aed04bffca00c04d05e623f8afd20877dcfa09ddf43a8c1a7e8c34db03`.
- [x] Expose the validated board, filters, intervals, explanations, and lineage in the local Streamlit app.
- [x] At the Phase 4 publication boundary, keep ADP movement, next-pick availability, draft recommendations, and the draft engine explicitly unavailable.

## Phase 5 — ADP movement and next-pick availability (complete foundation)

- [x] Verify immutable FFC and manual ESPN captures against their SHA-256 manifests before normalization.
- [x] Define stable snapshot identity from source, season, scoring format, team count, position scope, capture time, and raw hash.
- [x] Collapse duplicate manifests that reference the same raw capture and make repeat loads idempotent.
- [x] Skip clearly labeled synthetic ESPN fixture data from production loads by default.
- [x] Normalize one production FFC snapshot into 246 canonical ADP observations.
- [x] Preserve all 246 unresolved identities with source keys and mapping confidence instead of joining by display name.
- [x] Build 246 chronological, cutoff-safe movement-feature rows.
- [x] Persist 738 forecast rows across persistence, linear-trend, and exponentially weighted methods with explicit readiness status.
- [x] Activate persistence for 246 rows and truthfully retain zero ready linear or exponentially weighted rows until at least three dated observations exist.
- [x] Persist 246 availability parameter rows using source standard deviation; record zero configured fallbacks in the validated build.
- [x] Expose conditional next-pick availability separately from player quality and market movement.
- [x] Mark availability uncalibrated because no linked real-draft outcomes are archived.
- [x] Keep supervised movement and availability unavailable because one independent production snapshot cannot support chronological training and validation.
- [x] Record build fingerprint `3446513dfe4b122079ba1ed89b6517821d35cac48821ff1631e25a77f6dd3b6b` and snapshot fingerprint `44624854b5c45f80fb0017e6ecdb52c972d4389236d35131b2dbfccb9a0447f2`.
- [x] Publish the Phase 5 evaluation report, learning chapter, app market view, audit/status checks, and integration/unit tests.
- [x] Keep draft recommendations, mutable draft state, and Monte Carlo simulation explicitly unavailable.

## Future phases

- [ ] Phase 6 (next): event-sourced snake draft and Monte Carlo optimization.
- [ ] Phase 7: full multipage Streamlit workflow.
- [ ] Phase 8: descriptive league-history analysis and gated outcome modeling.
