# Next Steps

## Current milestone

Phase 0 and the Phase 1 data foundation are complete. The newest manifest-backed 2015–2025 nflverse capture is validated and loaded idempotently into canonical `players` and `player_week_stats` tables. The core Phase 2 rules/scoring slice is also implemented. No trained player model or learned draft recommendation is claimed yet.

## Next implementation session

1. Add a player identity review queue for cross-platform/manual mappings.
2. Define regular-season aggregation semantics and preserve feature cutoffs explicitly.
3. Build the first cutoff-safe `player_season_features` table.
4. Implement previous-season and weighted-history baselines with rolling evaluation.
5. Add leakage tests before accepting any trained model.
6. Expand the Streamlit shell into Data Center and League Setup pages.

## Exact next command

```powershell
.\.venv\Scripts\Activate.ps1
fantasy-draft data load-nflverse
fantasy-draft data audit
```
