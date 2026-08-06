# 🏈 Fantasy Football Draft AI

[![Quality gates](https://github.com/GlassHouse97/Fantasy-Football-Draft-Tool/actions/workflows/quality.yml/badge.svg)](https://github.com/GlassHouse97/Fantasy-Football-Draft-Tool/actions/workflows/quality.yml)

A local-first NFL redraft assistant that turns historical football data, exact league rules, and current draft-market information into transparent recommendations. The goal is useful software **and** a practical course in sports modeling. No LLM decides who you should draft.

## What works today

The runnable local foundation includes:

- a packaged Python CLI and seven-route local Streamlit application;
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
- position-specific Ridge and histogram gradient-boosting models with validation-gated champions;
- a validated 2026 projection board with P10/P50/P90 displays and player explanations;
- idempotent, hash-verified normalization of immutable FFC and manual ESPN ADP captures;
- cutoff-safe ADP movement features with persistence, linear-trend, and exponentially weighted baselines;
- a transparent next-pick availability distribution with source-reported spread evidence and labeled fallbacks;
- an event-sourced snake-draft engine with immutable session pools, append-only picks, undo, replacement, and replay hashes;
- exact ruleset-aware lineup assignment plus a seeded Monte Carlo and transparent recommendation baseline;
- a runnable manual Streamlit draft room and deterministic draft CLI;
- normalized, fingerprinted league setup persistence with YAML backup and restore;
- an auditable Data Center and read-only Model Lab that preserve the data and model publication gates;
- descriptive post-draft lineup, draft-capital, ADP-value, replacement-risk, and strategy reports;
- a Learning Center that previews local guides and notebook Markdown without executing code;
- tests for data integrity, leakage, chronological evaluation, model selection, publication integrity, ADP idempotency, availability bounds, scoring, rules, and replacement value.

Phases 0 through 7 are complete locally. Phase 7 organizes the existing contracts into Project Status, Data Center, Model Lab, League Setup, Draft Room, Post-Draft, and Learning Center routes. The draft engine, seeded simulator, and configurable recommendation baseline pass controlled fixture tests, but live production recommendations remain locked: all 203 draftable QB/RB/WR/TE ADP rows currently lack reviewed canonical player mappings. The other 43 PK/DEF rows remain archived and auditable outside this ruleset's recommendation coverage. Manual picks, undo, replacement, rosters, replay verification, and descriptive post-draft reporting remain available. No championship probability is produced.

## Local setup (Windows PowerShell)

Python 3.11 is the recommended runtime for the current dependency set.

```powershell
py -3.11 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -e ".[modeling,dev]"
fantasy-draft data init-warehouse
fantasy-draft status
```

To run the educational notebooks, install the notebook tooling alongside the modeling and
development dependencies:

```powershell
python -m pip install -e ".[modeling,notebooks,dev]"
```

Run every quality gate:

```powershell
python -m ruff check .
python -m mypy
python -m pytest
```

Start the local UI:

```powershell
fantasy-draft app
```

## First data commands

Start small while verifying your environment:

```powershell
fantasy-draft data download-nflverse --start-season 2025 --end-season 2025
fantasy-draft data load-nflverse
fantasy-draft data snapshot-ffc-adp --season 2026 --format ppr --teams 12
fantasy-draft data import-espn-adp data\templates\espn_adp_snapshot_template.csv
fantasy-draft data load-adp
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

Five deterministic baselines generated 167,565 prediction rows, of which 80,060 had an evaluable historical target across the 2020-2025 folds. The age- and position-adjusted baseline had the best aggregate points-per-game MAE at 2.581 and total-points MAE at 33.324. The report separates the all-candidate attrition view from positive-game accuracy and counts 6,464 evaluation candidates: 3,102 with positive games, 3,344 with zero games, and 18 with unavailable active-game outcomes. Current ADP was not backfilled into historical folds because no cutoff-safe historical archive exists. These frozen Phase 3 fingerprints and folds remain the comparison contract for Phase 4.

## Reproduce the Phase 4 model run

Phase 4 trains one Ridge and one histogram gradient-boosting model for each QB/RB/WR/TE and points-per-game/games-active/total-points route. It uses pooled 2020-2024 validation for selection and reserves 2025 as a final test that never selects a champion.

```powershell
fantasy-draft models train-player-models --rules configs/example_ppr_12_team.yaml --validation-start-season 2020 --test-season 2025 --output docs/PHASE_4_MODEL_EVALUATION.md
fantasy-draft data audit
fantasy-draft status
fantasy-draft app
```

The validated run is `phase4-7ae8e9aed04bffca00c0`, with run fingerprint `7ae8e9aed04bffca00c04d05e623f8afd20877dcfa09ddf43a8c1a7e8c34db03`. It registered 24 models, persisted 45,588 predictions (32,024 evaluable and 6,804 live learned-candidate predictions), compared 84 selection candidates, selected 12 position/target champions, and materialized 1,367 live board rows.

A learned candidate is selected only when its pooled validation MAE is below the best transparent baseline and the paired-bootstrap 95% confidence interval for learned-minus-baseline MAE has an upper bound below zero. That gate selected learned models for 9 of 12 routes: every total-points and games-active route plus histogram gradient boosting for WR points per game. QB, RB, and TE points per game retain the age/position-adjusted baseline.

Learned P10/P50/P90 ranges use signed residuals from training-only, earlier out-of-fold predictions and are evaluated by season, position, and projection tier. A retained baseline remains an honest point estimate with `P10=P50=P90`. The 233 live rookies also use point-only transparent fallbacks because Phase 3 has no historical preseason rookie-position cohort: QB 21, RB 46, WR 114, and TE 52.

DuckDB is authoritative for the one active deterministic run. Every training attempt receives an immutable `publication_id`, and its reports, registry, diagnostic plots, model cards, and serialized artifacts live beneath `<run_id>/<publication_id>/` paths verified by registered SHA-256 hashes. All six Phase 4 tables are staged, audited, and promoted in one DuckDB transaction, so a failed forced retry rolls back to the previously complete publication. The top-level Phase 4 report and `models/registry.json` are convenience mirrors refreshed only after commit. Audit, status, and the app reject partial, stale, orphaned, count-mismatched, or hash-mismatched publication state.

## Reproduce the Phase 5 ADP foundation

Phase 5 verifies every archived FFC or manual ESPN capture against its manifest, collapses duplicate manifests that point to the same immutable raw payload, and loads each production snapshot idempotently. Clearly labeled synthetic captures are skipped by default.

```powershell
fantasy-draft data load-adp
fantasy-draft models build-adp-baselines --availability-config configs/adp_availability.yaml --output docs/PHASE_5_ADP_AVAILABILITY_EVALUATION.md
fantasy-draft data audit
fantasy-draft status
fantasy-draft app
```

The validated build has fingerprint `3446513dfe4b122079ba1ed89b6517821d35cac48821ff1631e25a77f6dd3b6b` and snapshot fingerprint `44624854b5c45f80fb0017e6ecdb52c972d4389236d35131b2dbfccb9a0447f2`. One production FFC snapshot produced 246 canonical observations, 246 movement-feature rows, 738 baseline rows, and 246 availability-parameter rows. All 246 identities remain unresolved and are safely keyed by source identity instead of display name. The labeled ESPN fixture is excluded from the production build.

Persistence is ready for all 246 observations. Linear and exponentially weighted trends require at least three dated observations per source player, so neither is active yet. Every availability scale came from source-reported standard deviation; no configured fallback was needed. These probabilities are explicitly uncalibrated because no linked real-draft outcomes are archived, and no supervised movement or availability model is claimed.

## Run the Phase 6 draft room

The Streamlit room can create and restore a local session, record the on-clock team's pick, undo the latest pick, replace an earlier pick without deleting history, show all team rosters, and verify the replayed state after a refresh:

```powershell
fantasy-draft app
```

The same state workflow is available through the CLI:

```powershell
fantasy-draft draft create --rules configs/example_ppr_12_team.yaml --draft-slot 1 --name "My draft" --simulations 64 --seed 42
fantasy-draft draft list
fantasy-draft draft show --session-id SESSION_ID
fantasy-draft draft pick --session-id SESSION_ID --player-id PLAYER_ID --expected-version 0
# Choose undo or replace using the current version printed by draft show.
fantasy-draft draft undo --session-id SESSION_ID --expected-version 1
fantasy-draft draft replace --session-id SESSION_ID --overall-pick 1 --player-id PLAYER_ID --expected-version 1
fantasy-draft draft verify --session-id SESSION_ID
fantasy-draft draft recommend --session-id SESSION_ID
```

Use the current version printed by `draft show` for each mutation. Every command appends an idempotent event and checks optimistic concurrency. The session freezes all 1,367 canonical projection rows and their exact lineage, so a later upstream refresh cannot rewrite an in-progress draft.

The versioned `phase6-baseline-v1` configuration uses 64 default simulation paths, evaluates six candidates, and requires 100% canonical market coverage. Controlled mapped fixtures prove seeded rest-of-draft simulation, distinct balanced/safe-floor/high-upside outputs, configurable component weights, ruleset-sensitive replacement value, and the absence of championship-probability claims. Those fixtures validate the engine; they do not make the current live data recommendation-ready.

Current production status is `identity_mapping_required`: 0 of 203 draftable PPR/12-team QB/RB/WR/TE ADP rows map to canonical projection IDs. The 43 archived PK/DEF rows are outside the configured roster and projection scope, so they do not create an impossible coverage requirement. Names are never used as a fallback join. The manual room is runnable, but `draft recommend` exits unavailable until the operator reviews identities and rebuilds Phase 5:

```powershell
fantasy-draft data review-identities
fantasy-draft data apply-identity-overrides data\processed\identity\identity_review_queue.csv
fantasy-draft data review-identities
fantasy-draft data load-adp
fantasy-draft models build-adp-baselines --availability-config configs/adp_availability.yaml --output docs/PHASE_5_ADP_AVAILABILITY_EVALUATION.md
fantasy-draft data audit
fantasy-draft status
```

The verified Phase 6 implementation gates include Ruff, strict mypy across 69 source files, 210 passing pytest tests in 77.23 seconds, a Streamlit AppTest run with zero exceptions across all six tabs, a passing data audit covering eight manifests and 12 verified immutable raw files, and the passing one-command quality-gate wrapper.

The Phase 6 GitHub Actions workflow is not recorded as green. GitHub's runner outage canceled the pull-request and `main` workflows before a runner was assigned, so an hourly reminder is active to retry and verify the `main` run when hosted runners recover. The local Phase 6 evidence above remains valid; it is not a substitute for a completed hosted workflow.

## Use the Phase 7 local application

Start the app from the repository root:

```powershell
fantasy-draft app
```

Streamlit exposes one stable route for each workflow:

| Route | Purpose |
|---|---|
| `/status` | Project readiness, current data/model facts, blockers, and next action |
| `/data-center` | Immutable source archives, manifests, warehouse inventory, and quality audit |
| `/model-lab` | Read-only model contract, chronological evidence, diagnostics, and player explanations |
| `/league-setup` | Exact roster/scoring/playoff rules, draft slot, fingerprint, and YAML backup/restore |
| `/draft-room` | Persistent manual picks, undo/replace, board filters, rosters, and gated recommendations |
| `/post-draft` | Descriptive lineup, positional capital, value, risk, strategy, and limitation report |
| `/learning-center` | Read-only previews and links for guides and notebooks |

The Data Center may run read-only audits, idempotent warehouse initialization, immutable nflverse/snap-count/FFC/manual ESPN archive actions, and an archive-only quarantine intake for CSV/JSON/ZIP league-history packages. Canonical warehouse loads remain explicit CLI handoffs (`load-nflverse`, `load-nflverse-participation`, and `load-adp`) so archiving evidence cannot silently change downstream tables. Sleeper league import and league-history parsing, normalization, analysis, and modeling remain visibly unavailable until their real contracts exist.

Model Lab never trains or promotes a model. It reads the validated Phase 3/4 publication and shows target/feature definitions, chronological folds, learned-versus-baseline decisions, metrics, residuals, feature importance, model cards, and served player explanations. Use the CLI training command only when intentionally creating a new model publication.

League Setup persists normalized rules and the user's draft slot in DuckDB. Deterministic YAML exports include the ruleset fingerprint and reject tampering on import. Draft Room freezes the selected ruleset and projection/market lineage into each new session. Post-Draft reports may be generated for incomplete drafts, but those values are labeled provisional; missing ADP and uncertainty remain missing rather than being imputed.

Phase 7 validation passed Ruff, strict mypy across 87 source files, 251 pytest tests in 127.81 seconds, AppTest with zero exceptions across all seven pages, and the CLI data audit across eight manifests and 12 verified immutable files. Real browser QA navigated the multipage app and successfully triggered the live Data Center audit action. See [the Phase 7 evaluation](docs/PHASE_7_STREAMLIT_EVALUATION.md).

Hosted Phase 7 CI is not recorded as green. GitHub Actions was in a reported major outage when PR #7 was opened, and no workflow run registered for the branch. The existing hourly recovery reminder now tracks both the Phase 6 canceled run and the missing Phase 7 run; local validation is not presented as hosted-CI success.

## Learn the system

- [Architecture](docs/ARCHITECTURE.md)
- [Assumptions](docs/ASSUMPTIONS.md)
- [Implementation checklist](docs/IMPLEMENTATION_CHECKLIST.md)
- [User data checklist](docs/USER_DATA_CHECKLIST.md)
- [Scoring and replacement value](docs/learning/SCORING_AND_REPLACEMENT_VALUE.md)
- [Projection baselines and why they matter](docs/learning/03_baselines_and_why_they_matter.md)
- [Projection baseline notebook](notebooks/python/03_projection_baselines.ipynb)
- [Phase 3 baseline evaluation](docs/PHASE_3_BASELINE_EVALUATION.md)
- [Phase 4 model evaluation](docs/PHASE_4_MODEL_EVALUATION.md)
- [Active Phase 4 model registry](models/registry.json)
- [How to read a model card](docs/learning/12_how_to_read_a_model_card.md)
- [ADP movement and availability](docs/learning/08_adp_movement_and_availability.md)
- [Phase 5 ADP and availability evaluation](docs/PHASE_5_ADP_AVAILABILITY_EVALUATION.md)
- [Phase 6 draft-engine evaluation](docs/PHASE_6_DRAFT_ENGINE_EVALUATION.md)
- [Phase 7 Streamlit evaluation](docs/PHASE_7_STREAMLIT_EVALUATION.md)
- [Next steps](docs/NEXT_STEPS.md)

## Data boundaries

Downloaded data, generated review worksheets, manual uploads, DuckDB files, serialized estimators, and authoritative attempt-scoped reports are ignored by Git. Publication-safe evaluation mirrors, model cards, and diagnostic figures may be versioned with their registered hashes; small templates and clearly labeled fixtures are also versioned. Never commit league exports or completed identity-review worksheets containing private or identifying information without reviewing and pseudonymizing them first.

## Attribution

Historical NFL data is accessed through [nflreadpy and nflverse](https://nflreadpy.nflverse.com/). Draft-market snapshots use the documented [Fantasy Football Calculator ADP API](https://help.fantasyfootballcalculator.com/article/42-adp-rest-api) and should retain source attribution.

## License

MIT. Third-party data remains subject to its source terms.
