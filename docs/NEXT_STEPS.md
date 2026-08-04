# Next Steps

## Current milestone

Phase 0 and the runnable Phase 1 foundation are complete. The core Phase 2 rules/scoring slice is implemented. Live and offline smoke tests passed for 2026 FFC ADP and 2025 nflverse data. No trained player model or learned draft recommendation is claimed yet.

## Next implementation session

1. Download the full 2015–2025 completed-season range.
2. Map source columns into `players` and `player_week_stats`, preserving unmapped fields in processed Parquet.
3. Add a player identity review queue and tests for same-name conflicts.
4. Build the first cutoff-safe `player_season_features` table.
5. Implement previous-season and weighted-history baselines with rolling evaluation.
6. Expand the Streamlit shell into Data Center and League Setup pages.

## Exact next command

```powershell
.\.venv\Scripts\Activate.ps1
fantasy-draft data download-nflverse --start-season 2015 --end-season 2025
```
