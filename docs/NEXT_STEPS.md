# Next Steps

## Current milestone

Phases 0 through 6 are complete. The validated Phase 3 contract remains unchanged: 11,171 cutoff-safe features, 9,804 historical targets, 1,367 live 2026 rows, and feature/target/build fingerprints `d2bdda170fcbf88ccfe0b3f437615583a0684057eebe1fc12aa65463a47cf9cf`, `dd759bbf87c146884e68425079b3a759d1d6d4bb434d5bccee6d9d91c98c56a9`, and `f195dcb17a1a386b2f2003d87a06921550235cbec62aecd0f4eda419aa664cd7`. See [the Phase 3 report](PHASE_3_BASELINE_EVALUATION.md) for its full participation, candidate-universe, and historical-position limitations.

Phase 4 run `phase4-7ae8e9aed04bffca00c0` has fingerprint `7ae8e9aed04bffca00c04d05e623f8afd20877dcfa09ddf43a8c1a7e8c34db03`. Its validated immutable publication is `attempt-866987f75a2c406693cf892d49adc975`, with evaluation-report fingerprint `00ffb3d0c6bf51c4bed9a9556dec479749a0b7abcf829deab1e2e14a565978a5`. It registered 24 Ridge/HGB models, persisted 45,588 predictions (32,024 evaluable and 6,804 live learned-candidate predictions), compared 84 candidates, recorded 12 champions, and built a complete 1,367-row projection board.

The validation/bootstrap gate selected learned models for 9 of 12 routes: every total-points and games-active route plus histogram gradient boosting for WR points per game. QB, RB, and TE points per game retain `age_position_adjusted`. Selection uses pooled 2020-2024 MAE and requires the learned-minus-baseline paired-bootstrap 95% confidence-interval upper bound to be below zero; the 2025 test never selects.

Learned intervals use earlier out-of-fold training residuals and are evaluated by season, position, and projection tier. Retained baselines and 233 rookie fallbacks remain honest point estimates with `P10=P50=P90`. Rookie counts are QB 21, RB 46, WR 114, and TE 52. See [the Phase 4 report](PHASE_4_MODEL_EVALUATION.md) and the active run in [the model registry](../models/registry.json).

Phase 5 build `3446513dfe4b122079ba1ed89b6517821d35cac48821ff1631e25a77f6dd3b6b` is bound to snapshot fingerprint `44624854b5c45f80fb0017e6ecdb52c972d4389236d35131b2dbfccb9a0447f2`. One production FFC capture produced 246 canonical observations, 246 movement features, 738 baseline forecasts, and 246 availability parameters. Duplicate manifests collapse to one snapshot, and the labeled ESPN fixture is skipped. All 246 identities remain unresolved and source-keyed; no display-name join was used.

Persistence is active for all 246 rows. Linear and exponentially weighted trends have zero ready rows because each requires at least three dated observations. All 246 availability scales use source standard deviation, with zero configured fallbacks. Availability remains uncalibrated, and supervised ADP movement and availability remain unavailable until enough independent dated snapshots and linked real-draft outcomes exist. See [the Phase 5 report](PHASE_5_ADP_AVAILABILITY_EVALUATION.md).

Phase 6 adds an append-only, event-sourced snake-draft state machine, exact lineup assignment, frozen player pools, optimistic versions, replay/state hashes, seeded rest-of-draft simulation, and a transparent ruleset-aware recommendation baseline. Its `phase6-baseline-v1` configuration defaults to 64 paths, evaluates six candidates, and requires complete compatible-market coverage. Fixture tests exercise mapped simulation and three distinct recommendation roles without producing championship probabilities. See [the Phase 6 evaluation](PHASE_6_DRAFT_ENGINE_EVALUATION.md).

The local app and CLI now provide runnable session creation, manual picks, undo, replacement, roster views, persistence, and replay verification. Production recommendation and Monte Carlo actions remain correctly gated: 0 of 203 draftable PPR/12-team QB/RB/WR/TE ADP rows currently have reviewed canonical mappings. The 43 archived PK/DEF rows remain auditable outside this ruleset's coverage denominator. The system never substitutes a display-name join. Fixture success proves the engine path, not live production readiness.

## Operator identity review

Refresh the queue whenever nflverse, FFC, or ESPN identity evidence changes. The command exports the current worksheet to `data/processed/identity/identity_review_queue.csv`. Review pending rows, then fill `resolution`, `reviewed_at`, and `reviewer`; remapped or dismissed rows also require `notes`. Applying the worksheet archives it unchanged under `data/raw/identity_overrides/` with a SHA-256 manifest and updates the queue and source-mapping registry transactionally.

## Phase 5 — complete foundation and ongoing data collection

- Stable source/scope/capture snapshot identity, immutable hash verification, duplicate-manifest collapse, synthetic-data exclusion, and idempotent normalization are implemented.
- Unresolved identities remain source-keyed with recorded confidence; display name is never the canonical join key.
- Movement features and persistence, linear, and exponentially weighted forecast rows are built with explicit cutoff semantics and unavailable statuses.
- Availability uses a continuity-corrected pick distribution with source standard deviation first, min/max-derived spread second, and a labeled versioned fallback only when necessary.
- Player quality, market movement, and draft availability remain separate signals.

Continue capturing dated production ADP snapshots during draft season and rerun `load-adp` plus `build-adp-baselines`. More independent dates will activate transparent trends; linked real draft outcomes are still required before calibration can be measured. Do not enable a supervised model merely because more rows from one capture exist.

## Phase 6 — complete engine; live activation requires identity review

- Session creation freezes the canonical projection pool, model lineage, ADP evidence, rules, scoring fingerprint, engine configuration, random seed, and simulation count.
- Picks, undo, and replacement are append-only events with idempotent command IDs, optimistic versions, and prior/result state fingerprints.
- Replaying persisted events is authoritative; refreshes and restarts reconstruct the same snake order, rosters, and available players.
- Exact lineup assignment handles direct starters, FLEX/SUPERFLEX eligibility, and bench capacity without relying on a greedy slot order.
- The recommendation baseline separates VORP, scarcity, next-pick risk, roster fit, uncertainty, and simulated roster value under visible role-specific weights.
- Seeded fixtures validate Monte Carlo behavior and balanced, safe-floor, and high-upside outputs. Point-only projections stay deterministic and are not promoted as calibrated uncertainty.

The operator prerequisite is now canonical identity review. Resolve the draftable FFC rows, apply the reviewed worksheet, reload ADP, rebuild the Phase 5 baseline, and confirm status. Create a new frozen session afterward; existing state-only sessions intentionally retain their original unresolved pool.

```powershell
fantasy-draft data review-identities
fantasy-draft data apply-identity-overrides data\processed\identity\identity_review_queue.csv
fantasy-draft data review-identities
fantasy-draft data load-adp
fantasy-draft models build-adp-baselines --availability-config configs/adp_availability.yaml --output docs/PHASE_5_ADP_AVAILABILITY_EVALUATION.md
fantasy-draft data audit
fantasy-draft status
```

## Phase 7 — application and report polish (next)

The next build phase should organize the existing capabilities into clearer Data Center, Model Lab, League Setup, Draft Room, Post-Draft Report, and Learning Center workflows. Add manifest/report browsing, rules editing with compatibility explanations, richer completed-draft summaries, and export/polish without weakening Phase 6 persistence or data gates. Phase 7 should not bypass the canonical identity prerequisite or relabel the baseline score as a championship probability.

## Verified Phase 6 quality evidence

- Strict mypy passed across 69 source files.
- The full pytest suite collected and passed 210 tests in 77.23 seconds.
- Streamlit AppTest completed with zero exceptions and exposed `Project status`, `2026 projections`, `ADP availability`, `Draft room`, `Scoring sandbox`, and `Learning path`.
- `fantasy-draft data audit` passed with eight manifests and 12 verified immutable raw files.
- With no user-created draft session, all four live Phase 6 persistence tables correctly contain zero rows: `draft_sessions`, `draft_session_players`, `draft_events`, and `draft_recommendation_runs`.
- Ruff and the final one-command quality-gate wrapper passed.

## Reproduce the validated Phase 3 through Phase 6 foundation

```powershell
.\.venv\Scripts\Activate.ps1
fantasy-draft data download-nflverse --start-season 2015 --end-season 2025 --offline
fantasy-draft data load-nflverse
fantasy-draft data download-nflverse-snap-counts --start-season 2015 --end-season 2025 --offline
fantasy-draft data load-nflverse-participation
fantasy-draft features build-player-seasons --prediction-season 2026 --rules configs/example_ppr_12_team.yaml
fantasy-draft models evaluate-baselines --rules configs/example_ppr_12_team.yaml --first-evaluation-season 2020 --last-evaluation-season 2025 --output docs/PHASE_3_BASELINE_EVALUATION.md
fantasy-draft models train-player-models --rules configs/example_ppr_12_team.yaml --validation-start-season 2020 --test-season 2025 --output docs/PHASE_4_MODEL_EVALUATION.md
fantasy-draft data load-adp
fantasy-draft models build-adp-baselines --availability-config configs/adp_availability.yaml --output docs/PHASE_5_ADP_AVAILABILITY_EVALUATION.md
fantasy-draft data audit
fantasy-draft status
fantasy-draft app
```

`--offline` reuses the validated immutable nflverse captures. Omit it only to intentionally acquire a new archive; new source provenance may change Phase 3 fingerprints and correctly invalidate the dependent Phase 4 run. Repeating the player-model command without `--force` safely reuses the current deterministic run when all registered outputs verify. Repeating the ADP load and baseline build preserves counts and fingerprints for identical inputs.

## Exact next development gate

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\test.ps1
```

Create and inspect a state-only Phase 6 session independently of the gated recommendation path:

```powershell
fantasy-draft draft create --rules configs/example_ppr_12_team.yaml --draft-slot 1 --name "My draft" --simulations 64 --seed 42
fantasy-draft draft list
fantasy-draft draft show --session-id SESSION_ID
fantasy-draft draft verify --session-id SESSION_ID
```

Phase 6's engine boundary is implemented and its controlled fixture paths validate state replay, exact roster assignment, seeded simulation, and recommendation explanations. The exact Ruff, mypy, pytest, AppTest, data-audit, and combined-wrapper evidence is recorded above. The next development slice is Phase 7 UI/data-center/post-draft polish, while canonical ADP review remains the operator action required to activate live recommendations. Keep the Phase 3 through Phase 6 reports frozen as upstream contracts and keep championship probabilities disabled.
