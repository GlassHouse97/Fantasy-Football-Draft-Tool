# Next Steps

## Current milestone

Phases 0 through 3 are complete. The immutable 2015-2025 nflverse player/weekly capture and PFR snap-count capture load idempotently into canonical weekly and participation tables. Phase 3 then builds 11,171 cutoff-safe features, 9,804 separately persisted historical targets, and 1,367 live 2026 rows. Fifteen participation coverage failures leave games active and points per game unavailable for 28 targets. The feature fingerprint is `d2bdda170fcbf88ccfe0b3f437615583a0684057eebe1fc12aa65463a47cf9cf`, target fingerprint is `dd759bbf87c146884e68425079b3a759d1d6d4bb434d5bccee6d9d91c98c56a9`, and combined build fingerprint is `f195dcb17a1a386b2f2003d87a06921550235cbec62aecd0f4eda419aa664cd7`.

Five transparent heuristics generated 167,565 prediction rows and 80,060 evaluated rows across expanding 2020-2025 folds. The 6,464 evaluation candidates comprise 3,102 positive-game, 3,344 zero-game, and 18 missing-games outcomes. The age/position-adjusted baseline produced the best aggregate points-per-game MAE of 2.581 and total-points MAE of 33.324.

The August 2026 identity snapshot predates the September 1 live cutoff and safely supplies static position for 309 live rows. It is not backfilled into prior seasons: 2,710 current-core historical entry-cohort candidates without cutoff-safe position evidence are excluded and reported. This prevents later position conversions from leaking backward, but it also means historical rookie baseline performance cannot yet be measured honestly without a historical preseason-position archive. The quality report separately counts 1,117 target scorers and 1,390 active target players outside the candidate universe. Historical ADP remains unavailable for the same snapshot-timing reason.

No statistical or machine-learning player model has been trained, and no learned draft recommendation is claimed yet. See [the evaluation report](PHASE_3_BASELINE_EVALUATION.md) and [learning chapter](learning/03_baselines_and_why_they_matter.md).

## Operator identity review

Refresh the queue whenever nflverse, FFC, or ESPN identity evidence changes. The command exports the current worksheet to `data/processed/identity/identity_review_queue.csv`. Review pending rows, then fill `resolution`, `reviewed_at`, and `reviewer`; remapped or dismissed rows also require `notes`. Applying the worksheet archives it unchanged under `data/raw/identity_overrides/` with a SHA-256 manifest and updates the queue and source-mapping registry transactionally.

## Phase 4 — statistical and ML player models

1. Use the Phase 3 feature, target, and combined build fingerprints plus the expanding folds as the frozen comparison contract.
2. Fit position-specific Ridge and/or Elastic Net pipelines with fold-local imputation, encoding, scaling, and tuning.
3. Fit a supported nonlinear tabular model without allowing future-season leakage.
4. Add P10/P50/P90 or residual-based uncertainty and calibration reporting.
5. Compare every candidate against all five transparent baselines on future-season folds.
6. Select a champion only when it earns the title on out-of-time evidence.
7. Add global and player-level explanations plus model cards.

Phase 4 must not silently convert the transparent baseline evaluation into a claim that an ML model already exists.

## Reproduce the validated Phase 3 build

```powershell
.\.venv\Scripts\Activate.ps1
fantasy-draft data download-nflverse --start-season 2015 --end-season 2025 --offline
fantasy-draft data load-nflverse
fantasy-draft data download-nflverse-snap-counts --start-season 2015 --end-season 2025 --offline
fantasy-draft data load-nflverse-participation
fantasy-draft features build-player-seasons --prediction-season 2026 --rules configs/example_ppr_12_team.yaml
fantasy-draft models evaluate-baselines --rules configs/example_ppr_12_team.yaml --first-evaluation-season 2020 --last-evaluation-season 2025 --output docs/PHASE_3_BASELINE_EVALUATION.md
fantasy-draft data audit
fantasy-draft status
```

`--offline` reuses the validated immutable captures. Omit it only to intentionally acquire a new archive; new source provenance may produce a new feature fingerprint.

## Exact next development gate

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\test.ps1
```

Keep the current Phase 3 report as the baseline contract while Phase 4 model code is added. No statistical or machine-learning training has begun yet; that is the next milestone.
