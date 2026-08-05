# 🏈 Fantasy Football Draft AI

A local-first NFL redraft assistant that turns historical football data, exact league rules, and current draft-market information into transparent recommendations. The goal is useful software **and** a practical course in sports modeling. No LLM decides who you should draft.

## What works today

This first runnable foundation includes:

- a packaged Python CLI and local Streamlit status app;
- immutable raw-file archives with SHA-256 manifests;
- a DuckDB warehouse schema for the project’s canonical tables;
- current `nflreadpy` and Fantasy Football Calculator adapters with offline reuse;
- immutable nflverse/PFR snap-count captures and transactional participation loading;
- a validated manual ESPN ADP import path, without scraping or login automation;
- an auditable player-identity review queue and durable source-ID mapping registry;
- immutable, validated manual identity overrides that survive nflverse reloads;
- deterministic league-rule normalization and fingerprints;
- configurable fantasy scoring, explicit FLEX/SUPERFLEX eligibility, and two replacement-value definitions;
- cutoff-safe player-season features, separately persisted future targets, and source provenance;
- five transparent projection baselines evaluated on expanding 2020-2025 folds;
- tests for data integrity, leakage, chronological evaluation, scoring, rules, and replacement value.

Phase 3 is complete, but no statistical or machine-learning player model has been trained. The available projections are labeled transparent heuristics. Regularized and boosted models, uncertainty, availability modeling, draft simulation, and the full live draft room remain later phases; the app reports those boundaries instead of inventing results.

## Local setup (Windows PowerShell)

Python 3.11 is the recommended runtime for the current dependency set.

```powershell
py -3.11 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -e ".[dev]"
fantasy-draft data init-warehouse
fantasy-draft status
```

Run every quality gate:

```powershell
python -m ruff check .
python -m mypy
python -m pytest
```

Start the local UI:

```powershell
python -m streamlit run app.py
```

## First data commands

Start small while verifying your environment:

```powershell
fantasy-draft data download-nflverse --start-season 2025 --end-season 2025
fantasy-draft data load-nflverse
fantasy-draft data snapshot-ffc-adp --season 2026 --format ppr --teams 12
fantasy-draft data import-espn-adp data\templates\espn_adp_snapshot_template.csv
fantasy-draft data review-identities
fantasy-draft data audit
```

Network commands preserve timestamped raw files. Add `--offline` to reuse an existing matching download without making a request. `load-nflverse` verifies one manifest-paired capture and its raw hashes, excludes only reported non-player placeholders, preserves curated identity mappings, and upserts nflverse weekly keys in one transaction. Unmentioned rows are never deleted by a potentially partial capture, and repeating the same manifest leaves canonical rows and counts unchanged.

`review-identities` verifies the latest nflverse, FFC, and manual ESPN captures, refreshes the DuckDB review queue, and exports an editable worksheet to `data/processed/identity/identity_review_queue.csv`. Exact platform-ID evidence may resolve automatically. Name-based comparisons only propose candidates; they never create a confirmed mapping without human approval. FFC team-defense rows (`DEF`, `DST`, or `D/ST`) are explicitly excluded from player mapping.

To approve, remap, or dismiss pending rows, edit the exported worksheet and fill in `resolution`, `reviewed_at`, and `reviewer`. A remap or dismissal also requires `notes`. Then apply the decisions:

```powershell
fantasy-draft data apply-identity-overrides data\processed\identity\identity_review_queue.csv
fantasy-draft data review-identities
fantasy-draft data audit
```

The override command validates the complete worksheet before writing, archives the reviewed CSV unchanged with a SHA-256 manifest, and applies all decisions in one transaction. Reapplying an identical worksheet is a safe no-op. Confirmed source mappings are retained in `player_source_mappings` for later queue refreshes, and reviewed canonical identity state survives later nflverse loads.

## Reproduce the Phase 3 baseline build

The validated local build uses the existing immutable 2015-2025 archives. `--offline` selects those manifest-backed files without making a network request. Omit it only when intentionally acquiring a new timestamped capture, which will create new provenance and may change the feature fingerprint.

```powershell
fantasy-draft data download-nflverse --start-season 2015 --end-season 2025 --offline
fantasy-draft data load-nflverse
fantasy-draft data download-nflverse-snap-counts --start-season 2015 --end-season 2025 --offline
fantasy-draft data load-nflverse-participation
fantasy-draft features build-player-seasons --prediction-season 2026 --rules configs/example_ppr_12_team.yaml
fantasy-draft models evaluate-baselines --rules configs/example_ppr_12_team.yaml --first-evaluation-season 2020 --last-evaluation-season 2025 --output docs/PHASE_3_BASELINE_EVALUATION.md
fantasy-draft data audit
fantasy-draft status
```

The feature builder treats a game as active only when mapped PFR participation has positive offense, defense, or special-teams snaps. It creates a feature row from season `t` to predict `t+1`, assigns September 1 of the prediction season as the logical preseason cutoff, and retains archive acquisition timestamps separately as provenance. Targets live in `player_season_targets`, not inside the feature payload used by an evaluator. The cutoff-safe candidate proxy uses the prior four seasons plus current/prior rookie cohorts; selection gaps are measured without consulting future outcomes.

Position evidence follows the same time boundary. Historical weekly or participation position is preferred. A static identity position is used only when that identity snapshot was acquired on or before the row's September 1 cutoff. The August 2026 identity snapshot therefore safely supports 309 live 2026 fallbacks. It is never backfilled into earlier seasons: 2,710 current-core historical entry-cohort candidates without cutoff-safe position evidence are excluded and reported. This protects the evaluation from later position conversions, but it also means historical rookie baseline performance cannot yet be measured honestly without a historical preseason-position archive.

The validated PPR build produced 11,171 feature rows, 9,804 historical target rows, and 1,367 live 2026 rows without targets. Fifteen player-seasons contain a nonzero-stat game without complete mapped participation, and 28 historical target rows have unavailable active-game denominators; total points remain available while unsupported games-active and points-per-game values stay null. The quality report also discloses 1,117 scorers and 1,390 active players outside the preseason candidate proxy.

Reproducibility uses three hashes: feature `d2bdda170fcbf88ccfe0b3f437615583a0684057eebe1fc12aa65463a47cf9cf`, target `dd759bbf87c146884e68425079b3a759d1d6d4bb434d5bccee6d9d91c98c56a9`, and combined build `f195dcb17a1a386b2f2003d87a06921550235cbec62aecd0f4eda419aa664cd7`. Rebuilding identical inputs reproduced all three. A feature or target change invalidates dependent baseline rows until evaluation is rerun.

Five deterministic baselines generated 167,565 prediction rows, of which 80,060 had an evaluable historical target across the 2020-2025 folds. The age- and position-adjusted baseline had the best aggregate points-per-game MAE at 2.581 and total-points MAE at 33.324. The report separates the all-candidate attrition view from positive-game accuracy and counts 6,464 evaluation candidates: 3,102 with positive games, 3,344 with zero games, and 18 with unavailable active-game outcomes. Current ADP was not backfilled into historical folds because no cutoff-safe historical archive exists. No statistical or machine-learning model training has begun; Phase 4 starts that work.

## Learn the system

- [Architecture](docs/ARCHITECTURE.md)
- [Assumptions](docs/ASSUMPTIONS.md)
- [Implementation checklist](docs/IMPLEMENTATION_CHECKLIST.md)
- [User data checklist](docs/USER_DATA_CHECKLIST.md)
- [Scoring and replacement value](docs/learning/SCORING_AND_REPLACEMENT_VALUE.md)
- [Projection baselines and why they matter](docs/learning/03_baselines_and_why_they_matter.md)
- [Projection baseline notebook](notebooks/python/03_projection_baselines.ipynb)
- [Phase 3 baseline evaluation](docs/PHASE_3_BASELINE_EVALUATION.md)
- [Next steps](docs/NEXT_STEPS.md)

## Data boundaries

Downloaded data, generated review worksheets, manual uploads, DuckDB files, and trained artifacts are ignored by Git. Small templates and clearly labeled fixtures are versioned. Never commit league exports or completed identity-review worksheets containing private or identifying information without reviewing and pseudonymizing them first.

## Attribution

Historical NFL data is accessed through [nflreadpy and nflverse](https://nflreadpy.nflverse.com/). Draft-market snapshots use the documented [Fantasy Football Calculator ADP API](https://help.fantasyfootballcalculator.com/article/42-adp-rest-api) and should retain source attribution.

## License

MIT. Third-party data remains subject to its source terms.
