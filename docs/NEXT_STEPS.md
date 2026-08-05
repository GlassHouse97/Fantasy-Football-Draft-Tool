# Next Steps

## Current milestone

Phases 0, 1, and 2 are complete. The manifest-backed 2015–2025 nflverse capture loads idempotently into canonical `players` and `player_week_stats`; scoring, rules, eligibility, replacement value, and the player-identity review workflow are implemented. Reviewed source mappings are durable, name-derived candidates require human approval, and FFC team-defense rows are explicitly excluded from player mapping.

No player model has been trained, and no learned draft recommendation is claimed yet.

## Operator identity review

Refresh the queue whenever nflverse, FFC, or ESPN identity evidence changes. The command exports the current worksheet to `data/processed/identity/identity_review_queue.csv`. Review pending rows, then fill `resolution`, `reviewed_at`, and `reviewer`; remapped or dismissed rows also require `notes`. Applying the worksheet archives it unchanged under `data/raw/identity_overrides/` with a SHA-256 manifest and updates the queue and source-mapping registry transactionally.

## Next implementation session

1. Define regular-season aggregation semantics, including postseason exclusion and availability denominators.
2. Preserve prediction-season cutoffs and source provenance explicitly.
3. Build the first idempotent `player_season_features` table with clear row accounting and missingness indicators.
4. Add deterministic leakage tests proving that no prediction-season or future information enters a feature row.
5. Validate the canonical feature table before enabling any baseline or model training.
6. After that gate passes, begin previous-season and weighted-history baselines with rolling evaluation.

## Exact next command

```powershell
.\.venv\Scripts\Activate.ps1
fantasy-draft data load-nflverse
fantasy-draft data review-identities
```

Review and edit `data\processed\identity\identity_review_queue.csv`, then run:

```powershell
fantasy-draft data apply-identity-overrides data\processed\identity\identity_review_queue.csv
fantasy-draft data review-identities
fantasy-draft data audit
```
