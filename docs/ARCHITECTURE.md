# Architecture

## Purpose

Fantasy Football Draft AI is a local, single-user system. It separates football projection, uncertainty, market timing, and roster optimization so each question can be tested independently.

```text
documented source or manual upload
    -> immutable timestamped raw file + SHA-256 manifest
    -> validation and identity resolution
    -> canonical DuckDB tables
    -> time-safe features and model artifacts
    -> ruleset-specific scoring and replacement value
    -> availability estimates and rest-of-draft simulation
    -> explained recommendation
```

## Layer boundaries

| Layer | Responsibility | Must not do |
|---|---|---|
| `data` | Acquire, archive, hash, validate, and load source data | Rank players or hide quality failures |
| `schemas` | Define stable canonical records and reports | Make network requests |
| `scoring` | Convert projected stat components into points | Predict the stat components |
| `rules` | Normalize league configuration, eligibility, demand, and replacement levels | Depend on Streamlit |
| `features` / `models` | Build cutoff-safe features and evaluated predictions | Use future information |
| `draft` / `simulation` | Replay draft events and compare possible futures | Invent learned probabilities |
| `services` | Orchestrate reusable application workflows | Contain UI rendering |
| `ui` / `app.py` | Present status, inputs, and outputs | Train models or encode business rules |

## Local storage

- `data/raw/` contains immutable source captures and manifests.
- `data/processed/` contains reproducible derived Parquet files.
- `data/warehouse/fantasy_football.duckdb` is the local analytical warehouse.
- `models/artifacts/<run_id>/<publication_id>/` contains serialized estimators, while `models/reports/<run_id>/<publication_id>/` contains the authoritative attempt-scoped evaluation and registry.
- `docs/PHASE_5_ADP_AVAILABILITY_EVALUATION.*` contains the reproducible Phase 5 evidence mirror; canonical snapshots, features, forecasts, parameters, and build metadata remain in DuckDB.
- DuckDB stores Phase 6 sessions, frozen player pools, append-only events, replay hashes, and recommendation-run payloads; local refreshes never make Streamlit session state authoritative.
- Generated data and models are ignored by Git; templates and test fixtures are not.

The warehouse uses explicit canonical tables even before every importer exists. This prevents early source-specific column names from becoming the application contract.

## nflverse warehouse loading

An nflverse load always selects the player and weekly-stat files from one source manifest. It never combines independently selected "latest" files. Before normalization, both raw files must exist inside the project and match their recorded SHA-256 hashes.

The player dimension uses GSIS IDs as internal IDs and never joins on display name. Weekly rows with no player ID are reported and excluded only when every mapped production field is zero; non-null IDs missing from the player capture and identifier-free rows with production are fatal. The loader stages both normalized tables, merges identity data without erasing later manual platform IDs or review metadata, key-upserts nflverse weekly rows, runs post-load invariants, and commits one DuckDB transaction. It never deletes keys absent from a capture because the current manifest does not prove that a file is a complete season replacement. Repeating the same manifest produces the same canonical rows and counts.

The nflverse player capture is a current global identity snapshot, not a table limited to the requested stat seasons. Historical feature code must use weekly team context and explicit cutoffs rather than treating current identity attributes as historical facts.

## Participation and historical player context

`fantasy-draft data download-nflverse-snap-counts` uses `nflreadpy.load_snap_counts` to archive Pro Football Reference game-level snap counts distributed by nflverse. The raw Parquet file is immutable and paired with a SHA-256 manifest. `fantasy-draft data load-nflverse-participation` verifies that capture, maps PFR IDs through canonical `players.pfr_id`, validates logical keys and season coverage, and atomically replaces nflverse participation rows in the manifest's complete season scope. Other seasons and sources survive; a repeat load of the same manifest produces the same rows.

Participation is evidence-based: a player has an active game only when offense, defense, or special-teams snaps sum to more than zero. A roster label or zero-snap record does not count. If a nonzero-stat/opportunity game lacks that evidence, the entire affected player-season denominator and points per game are left null instead of using a partial denominator. Postseason snap rows remain auditable but are excluded from season features.

The weekly-stat loader persists the position reported in each historical weekly row. Feature construction prefers weekly position and then participation position; historical team context also comes from time-indexed records. Static identity position is a fallback only when `identity_source_as_of` is on or before the row's September 1 cutoff. The August 2026 snapshot therefore supports live 2026 rows, but it is not backfilled into historical entry cohorts. Static facts used for age, rookie, draft-capital, and height features retain `identity_source_dataset_id` and acquisition time. Current weight, team, experience, and active status are never treated as historical features.

## Player identity review and overrides

`fantasy-draft data review-identities` reads the latest verified nflverse, FFC, and manual ESPN captures and compares their source identities with canonical `players`. Each logical observation receives a deterministic `review_id` based on its issue type, source, and source player ID. Refreshing the same evidence updates that queue record instead of manufacturing another review. Records that disappear from the latest source evidence remain available for audit with `is_current = false`.

The queue separates evidence from decisions:

- `identity_review_queue` stores source evidence, a proposed canonical candidate, confidence, current status, and any human resolution.
- `player_source_mappings` is the durable registry of reviewed `(source, source_player_id) -> player_id` decisions, including reviewer, timestamp, notes, and manifest provenance.
- the exported CSV under `data/processed/identity/` is an editable working copy, not an authoritative automatic mapping.

Stable source IDs are authoritative evidence when they already agree with the canonical registry. Normalized name, suffix, position, and team comparisons can produce `high`, `medium`, or `low` candidates, but every name-derived candidate remains `pending` until a human confirms or remaps it. Display name alone is never a join key. Ambiguous or missing candidates remain unresolved. FFC team-defense observations normalized to `DEF` are marked `excluded` because the canonical player dimension models people, not defense units.

`fantasy-draft data apply-identity-overrides PATH` accepts only decisions tied to an existing review ID. It validates source evidence, canonical targets, timestamps, reviewers, collisions, and resolution rules before archiving the submitted CSV unchanged. Approved decisions update the queue, mapping registry, and relevant canonical identity fields in one DuckDB transaction. Any failure rolls back the entire operation. Identical decisions are matched as no-ops, conflicting final decisions are rejected, and a stable nflverse GSIS ID cannot be remapped by name. The nflverse loader reapplies reviewed identity evidence after source refreshes so a later load cannot silently erase a human decision.

Phase 2 ends at this validated identity boundary.

## Phase 3 player-season features and baselines

Phase 3 is complete. A feature row with feature season `t` predicts season `t+1` and uses regular-season information only through `t`. September 1 of the prediction season is the logical preseason cutoff recorded in `cutoff_date` and `feature_available_at`. The later 2026 archive acquisition timestamp is retained in `source_max_as_of` as reproducibility evidence; it is not claimed to be the historical cutoff.

Feature construction separates predictors and outcomes physically:

- `player_season_features` contains lagged and weighted history, component rates, age/draft/rookie context, position priors, and explicit missingness flags;
- `player_season_targets` contains next-season points per active game, active games, and total points;
- `feature_build_metadata` binds row counts, ruleset fingerprint, source dataset IDs, validation report, a feature-only fingerprint, a target-only fingerprint, and their combined build fingerprint.

The builder stages and atomically replaces the active logical set, enforces one row per player/prediction season, excludes synthetic rows by default, and validates cutoffs, targets, provenance, duplicates, candidate coverage, position availability, and participation coverage before commit. The cutoff-safe candidate proxy uses evidence from the prior four seasons plus current and prior rookie cohorts; three seasons feed weighted production, and all four years of selection evidence remain in lineage. The validated build contains 11,171 features and 9,804 historical targets, including 1,367 live 2026 rows. It reports 2,710 current-core historical entry-cohort candidates excluded for missing cutoff-safe position evidence and 309 rows that use a cutoff-safe identity-snapshot fallback. Because the project does not yet archive historical preseason positions, historical rookie baseline performance is deliberately not claimed. A changed combined build fingerprint invalidates dependent baseline outputs.

Five transparent baselines—previous season, weighted history, age/position adjusted, position shrinkage, and weighted components—are evaluated on expanding folds for 2020-2025. They produced 167,565 prediction rows and 80,060 evaluated rows from 6,464 evaluation candidates (3,102 positive-game, 3,344 zero-game, and 18 with unavailable games-active outcomes). The age/position-adjusted baseline achieved the best aggregate points-per-game MAE of 2.581 and total-points MAE of 33.324. No cutoff-safe historical ADP snapshots exist, so the current 2026 ADP snapshot is explicitly unavailable as a historical comparison.

These are deterministic heuristics rather than trained models. Their frozen fingerprints and chronological folds are the Phase 4 comparison contract. See [the Phase 3 evaluation report](PHASE_3_BASELINE_EVALUATION.md) and [learning chapter](learning/03_baselines_and_why_they_matter.md).

## Phase 4 player models and projection publication

Phase 4 is complete. `fantasy-draft models train-player-models` fits both Ridge and histogram gradient boosting for each combination of QB/RB/WR/TE and `fantasy_points_per_game`, `games_active`, and `fantasy_points_total`: 24 final registered estimators. Preprocessing, tuning, and signed-residual interval fitting remain inside chronological training data. Expanding 2020-2024 folds form the validation pool; the 2025 test is evaluated only after selection and never chooses a champion.

Champion selection compares two learned families and all five transparent baselines for each of 12 position/target routes, producing 84 candidates. A learned route must have lower pooled validation MAE than the best baseline and a paired-bootstrap 95% confidence interval whose learned-minus-baseline upper bound is below zero. Otherwise the transparent baseline remains champion. Learned candidates passed for all eight total-points and games-active routes and histogram gradient boosting passed for WR points per game. QB, RB, and TE points per game retain `age_position_adjusted`.

The validated run `phase4-7ae8e9aed04bffca00c0` has fingerprint `7ae8e9aed04bffca00c04d05e623f8afd20877dcfa09ddf43a8c1a7e8c34db03`. It persists 45,588 candidate prediction rows, 32,024 evaluable predictions, 6,804 live learned-candidate predictions, 12 champions, and a complete 1,367-player live board. Learned selections use empirical training-only residual P10/P50/P90 ranges evaluated by season, position, and projection tier. Transparent selections remain point estimates with `P10=P50=P90`.

Historical preseason position evidence contains no valid rookie training cohort, so live rookies never receive a learned result. The board labels 233 point-only heuristic fallbacks: 21 QB, 46 RB, 114 WR, and 52 TE. This boundary is enforced in both persistence and presentation.

Publication uses one atomic integrity boundary. All six `player_projection_*` tables are staged with status `validating`, audited against the same open DuckDB connection, and promoted to `complete` before that transaction commits. The audit reconciles Phase 3 lineage, row counts, chronology, intervals, board coverage, artifacts, model cards, evaluation files, registry, and diagnostic plot hashes. Any integrity or promotion failure rolls the transaction back, preserving the prior complete publication.

The deterministic `run_id` names a model/data contract, while a unique `publication_id` names each immutable forced training attempt. DuckDB and the registered hashes are authoritative. Generated evaluation and registry files live under `models/reports/<run_id>/<publication_id>/`; artifact, card, and plot paths use the same attempt scope and are hashed. `docs/PHASE_4_MODEL_EVALUATION.*` and `models/registry.json` are convenience mirrors refreshed only after the verified transaction commits. Audit, status, and the projection service require exactly one current complete run and refuse stale, partial, orphaned, or tampered outputs. A changed Phase 3 feature/build or baseline-report fingerprint invalidates the dependent Phase 4 publication.

The Streamlit app reads this contract through a read-only service. When integrity passes, it exposes the 2026 board, position/search/target filters, selected method, intervals, explanations, and run lineage. Phase 4 itself remains player-outcome-only; Phase 5 supplies market movement and availability through a separate service and tab. Phase 6 consumes those outputs through a separately validated frozen-pool boundary. See [the Phase 4 evaluation report](PHASE_4_MODEL_EVALUATION.md).

## Phase 5 ADP movement and availability

Phase 5 is a validated transparent foundation, not a supervised model. `fantasy-draft data load-adp` discovers FFC and manual ESPN manifests, verifies project-relative raw files and SHA-256 hashes, rejects conflicting snapshot scope, and collapses duplicate manifests that identify the same raw capture. Synthetic fixture manifests are skipped unless explicitly requested. A stable snapshot identity binds source, season, scoring format, team count, position scope, capture time, and raw hash. Snapshot metadata and rows are upserted transactionally, so identical repeated loads preserve counts and fingerprints.

Identity remains evidence-aware. A reviewed `player_source_mappings` record may supply a canonical player ID; otherwise the row keeps a nullable `player_id`, recorded mapping confidence, and stable source identity. The validated FFC capture therefore retains 246 unresolved rows without joining on display name. Market calculations operate on the source identity until an auditable player mapping exists.

`fantasy-draft models build-adp-baselines` reads only verified production snapshots and builds three separate contracts:

- `adp_movement_features` contains as-of features such as prior ADP, elapsed days, fixed-horizon changes, velocity, acceleration, volatility, source spread, and observation counts. Every row is calculated using observations at or before its capture cutoff.
- `adp_movement_forecasts` records one-day persistence, linear-trend, and exponentially weighted trend results, including explicit unavailable status and reason. Persistence works with one observation; both trend methods require at least three dated observations for the same source identity.
- `adp_availability_parameters` stores the location and scale used by a continuity-corrected normal pick distribution. Source standard deviation wins, min/max-derived scale is second, and the versioned configuration fallback is used only when neither source measure exists.

`adp_phase5_builds` binds these tables to the snapshot-data and availability-configuration fingerprints, counts, capability statuses, and a quality report. The validated build fingerprint is `3446513dfe4b122079ba1ed89b6517821d35cac48821ff1631e25a77f6dd3b6b`; its snapshot fingerprint is `44624854b5c45f80fb0017e6ecdb52c972d4389236d35131b2dbfccb9a0447f2`. It contains one independent FFC snapshot, 246 observations and movement features, 738 forecast rows, and 246 availability parameters. Persistence is ready for 246 rows; linear and exponentially weighted trends have zero ready rows. All availability scales use source standard deviation and zero use fallback assumptions.

The read-only market service calculates the probability that a still-available player is selected before the user's next pick. This distribution baseline is explicitly uncalibrated because no linked real-draft outcomes exist. Supervised movement and availability remain unavailable because one independent dated capture cannot support chronological training and validation. Phase 6 may consume this evidence only through reviewed canonical IDs; Phase 5 itself still makes no recommendation. See [the Phase 5 evaluation report](PHASE_5_ADP_AVAILABILITY_EVALUATION.md).

## Phase 6 event-sourced draft engine

Phase 6 is implemented as a deterministic decision engine around frozen upstream evidence. The draft-room service verifies the active Phase 4 rules reference, compares scoring-only fingerprints so compatible roster variants can share projections, selects only matching ADP season/team/scoring scopes, and joins market evidence strictly by reviewed canonical `player_id`. Display names are presentation fields and never fallback keys. A session can start in state-only mode when market mapping is incomplete.

Session creation freezes all 1,367 canonical total-points projection rows, any compatible reviewed market evidence, the Phase 4 and Phase 5 lineage, exact rules, engine-config fingerprint, seed, and simulation count. This pool is immutable for the life of the session. A later projection or ADP rebuild affects only newly created sessions.

The event stream is authoritative:

- `session_started`, `pick_made`, `pick_undone`, and `pick_replaced` records are appended, never rewritten;
- each mutation carries a unique command ID and expected version, preventing Streamlit reruns or stale callers from duplicating work;
- every event binds the prior and resulting state fingerprints;
- replay validates sequence, snake ownership, duplicate prevention, roster legality, pool fingerprint, metadata version, and final state hash;
- an undo targets only the latest active pick, while replacement retains the original event and pick ownership.

Roster assignment uses an exact legal allocation across direct starters, FLEX/SUPERFLEX slots, and bench rather than a greedy slot order. The same rules contract feeds replacement levels and simulation roster evaluation.

The `phase6-baseline-v1` configuration is versioned and fingerprinted as `17e0337939917fcfcb08ec764d88b43a7001e4c3c776c3ac8597390cb54ad9c9`. It defaults to 64 seeded rest-of-draft paths, evaluates six candidates, caps work, and requires 100% compatible market mapping. Simulation samples opponent choice from frozen ADP distributions, applies bounded roster-need and positional-run adjustments, and keeps point-only projections deterministic. The recommendation engine exposes balanced, safe-floor, and high-upside roles with recomputable component contributions. It returns a draft recommendation score, not a calibrated win or championship probability.

Controlled mapped fixtures validate simulation and recommendation behavior, including ruleset-sensitive replacement value. Production remains deliberately gated: the current PPR/12-team market has 0 reviewed mappings across 203 draftable QB/RB/WR/TE rows. The other 43 archived PK/DEF rows stay auditable but are excluded from this ruleset's coverage denominator because no corresponding roster slots or projections exist. The manual Streamlit room and CLI remain fully usable for session creation, picks, undo, replacement, rosters, and replay verification; recommendation and Monte Carlo commands remain unavailable until canonical identity review and a new frozen session. See [the Phase 6 evaluation](PHASE_6_DRAFT_ENGINE_EVALUATION.md).

## Interfaces chosen in Phase 0

- Python 3.11 is the canonical runtime.
- `pyproject.toml` and a local `.venv` provide reproducible packaging.
- `nflreadpy` is the documented nflverse adapter and returns Polars dataframes.
- Pandas remains the approachable canonical tabular API inside this project.
- DuckDB is the embedded warehouse.
- Pydantic validates configuration and rules.
- Typer provides the CLI.
- Streamlit provides the first replaceable UI shell.

## Security and privacy

No ESPN scraping, authentication automation, cookies, or undocumented endpoints are used. Sleeper support will use only its documented read-only league interfaces. Personal league identifiers should be pseudonymized before publication. Secrets belong in `.env`, which is ignored.
