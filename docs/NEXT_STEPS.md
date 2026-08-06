# Next Steps

## Current milestone

Phases 0 through 4 are complete. The validated Phase 3 contract remains unchanged: 11,171 cutoff-safe features, 9,804 historical targets, 1,367 live 2026 rows, and feature/target/build fingerprints `d2bdda170fcbf88ccfe0b3f437615583a0684057eebe1fc12aa65463a47cf9cf`, `dd759bbf87c146884e68425079b3a759d1d6d4bb434d5bccee6d9d91c98c56a9`, and `f195dcb17a1a386b2f2003d87a06921550235cbec62aecd0f4eda419aa664cd7`. See [the Phase 3 report](PHASE_3_BASELINE_EVALUATION.md) for its full participation, candidate-universe, and historical-position limitations.

Phase 4 run `phase4-7ae8e9aed04bffca00c0` has fingerprint `7ae8e9aed04bffca00c04d05e623f8afd20877dcfa09ddf43a8c1a7e8c34db03`. Its validated immutable publication is `attempt-866987f75a2c406693cf892d49adc975`, with evaluation-report fingerprint `00ffb3d0c6bf51c4bed9a9556dec479749a0b7abcf829deab1e2e14a565978a5`. It registered 24 Ridge/HGB models, persisted 45,588 predictions (32,024 evaluable and 6,804 live learned-candidate predictions), compared 84 candidates, recorded 12 champions, and built a complete 1,367-row projection board.

The validation/bootstrap gate selected learned models for 9 of 12 routes: every total-points and games-active route plus histogram gradient boosting for WR points per game. QB, RB, and TE points per game retain `age_position_adjusted`. Selection uses pooled 2020-2024 MAE and requires the learned-minus-baseline paired-bootstrap 95% confidence-interval upper bound to be below zero; the 2025 test never selects.

Learned intervals use earlier out-of-fold training residuals and are evaluated by season, position, and projection tier. Retained baselines and 233 rookie fallbacks remain honest point estimates with `P10=P50=P90`. Rookie counts are QB 21, RB 46, WR 114, and TE 52. See [the Phase 4 report](PHASE_4_MODEL_EVALUATION.md) and the active run in [the model registry](../models/registry.json).

The local app now exposes the validated board, filters, uncertainty display, explanations, and run lineage. It does not yet provide ADP movement, empirical next-pick availability, draft recommendations, or a draft engine.

## Operator identity review

Refresh the queue whenever nflverse, FFC, or ESPN identity evidence changes. The command exports the current worksheet to `data/processed/identity/identity_review_queue.csv`. Review pending rows, then fill `resolution`, `reviewed_at`, and `reviewer`; remapped or dismissed rows also require `notes`. Applying the worksheet archives it unchanged under `data/raw/identity_overrides/` with a SHA-256 manifest and updates the queue and source-mapping registry transactionally.

## Phase 5 — ADP movement and next-pick availability

1. Define a stable snapshot key and scope for source, season, scoring format, team count, position filter, and capture time.
2. Archive every dated ADP response immutably with its raw hash and manifest; never overwrite a prior market observation.
3. Normalize snapshots idempotently and preserve unresolved player mappings rather than joining on display name.
4. Build cutoff-safe movement features such as current ADP, prior ADP, elapsed time, direction, velocity, and observation count.
5. Add transparent movement baselines before considering a learned trend model.
6. Estimate empirical next-pick availability by draft context, with sample counts and fallback behavior visible.
7. Evaluate chronologically so later snapshots never predict earlier market states.
8. Keep player quality, market movement, and draft availability as separate signals.
9. Do not claim supervised ADP or availability ML until the archive contains enough independent dated snapshots for honest train/validation/test splits.

Phase 5 does not authorize a draft recommendation or simulation engine; those begin only after availability is validated.

## Reproduce the validated Phase 3 and Phase 4 build

```powershell
.\.venv\Scripts\Activate.ps1
fantasy-draft data download-nflverse --start-season 2015 --end-season 2025 --offline
fantasy-draft data load-nflverse
fantasy-draft data download-nflverse-snap-counts --start-season 2015 --end-season 2025 --offline
fantasy-draft data load-nflverse-participation
fantasy-draft features build-player-seasons --prediction-season 2026 --rules configs/example_ppr_12_team.yaml
fantasy-draft models evaluate-baselines --rules configs/example_ppr_12_team.yaml --first-evaluation-season 2020 --last-evaluation-season 2025 --output docs/PHASE_3_BASELINE_EVALUATION.md
fantasy-draft models train-player-models --rules configs/example_ppr_12_team.yaml --validation-start-season 2020 --test-season 2025 --output docs/PHASE_4_MODEL_EVALUATION.md
fantasy-draft data audit
fantasy-draft status
fantasy-draft app
```

`--offline` reuses the validated immutable captures. Omit it only to intentionally acquire a new archive; new source provenance may change Phase 3 fingerprints and correctly invalidate the dependent Phase 4 run. Repeating the model command without `--force` safely reuses the current deterministic run when all registered outputs verify.

## Exact next development gate

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\test.ps1
```

The next development slice is the immutable dated ADP archive and idempotent warehouse normalization. It is complete only when raw captures remain immutable, manifest/hash checks pass, repeat loads preserve row counts, mapping gaps are reported, and time-order leakage tests cover movement features. Then add transparent empirical availability baselines. Keep the Phase 3 and Phase 4 reports frozen as upstream contracts while this work proceeds.
