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
- DuckDB also stores Phase 7 league setups in `league_rules`; a saved draft slot and optional playoff settings accompany the already canonical normalized rules and fingerprint.
- Phase 7 post-draft reports are deterministic read models generated from a verified session and its frozen player pool. JSON downloads are exports, not a second source of truth.
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

- `player_season_features` contains lagged and weighted history, component rates, raw age, the transparent-baseline age factor, draft/rookie context, position priors, and explicit missingness flags;
- `player_season_targets` contains next-season points per active game, active games, and total points;
- `feature_build_metadata` binds row counts, ruleset fingerprint, source dataset IDs, validation report, a feature-only fingerprint, a target-only fingerprint, and their combined build fingerprint.

The builder stages and atomically replaces the active logical set, enforces one row per player/prediction season, excludes synthetic rows by default, and validates cutoffs, targets, provenance, duplicates, candidate coverage, position availability, and participation coverage before commit. The cutoff-safe candidate proxy uses evidence from the prior four seasons plus current and prior rookie cohorts; three seasons feed weighted production, and all four years of selection evidence remain in lineage. The validated build contains 11,171 features and 9,804 historical targets, including 1,367 live 2026 rows. It reports 2,710 current-core historical entry-cohort candidates excluded for missing cutoff-safe position evidence and 309 rows that use a cutoff-safe identity-snapshot fallback. Because the project does not yet archive historical preseason positions, historical rookie baseline performance is deliberately not claimed. A changed combined build fingerprint invalidates dependent baseline outputs.

Five transparent baselines—previous season, weighted history, age/position adjusted, position shrinkage, and weighted components—are evaluated on expanding folds for 2020-2025. The age/position-adjusted baseline applies a smooth, position-specific deterministic performance curve rather than an injury probability. No cutoff-safe historical ADP snapshots exist, so current 2026 ADP remains explicitly unavailable as a historical comparison. Current row counts and metrics are recorded in the generated Phase 3 evaluation.

These are deterministic heuristics rather than trained models. Their frozen fingerprints and chronological folds are the Phase 4 comparison contract. See [the Phase 3 evaluation report](PHASE_3_BASELINE_EVALUATION.md) and [learning chapter](learning/03_baselines_and_why_they_matter.md).

## Phase 4 player models and projection publication

Phase 4 is complete. `fantasy-draft models train-player-models` fits both Ridge and histogram gradient boosting for each combination of QB/RB/WR/TE and `fantasy_points_per_game`, `games_active`, and `fantasy_points_total`. Preprocessing, tuning, and signed-residual interval fitting remain inside chronological training data. Learned estimators receive raw `age_at_cutoff`; the deterministic `age_adjustment_factor` remains available to transparent baselines but is excluded from the learned feature allowlist. A configuration invariant rejects any learned feature contract containing both, preventing a hand-authored age penalty from being learned a second time.

Champion selection compares the learned families and all five transparent baselines on one cohort that is fixed before any candidate is evaluated. For each 2020-2024 validation season, the cutoff-safe `weighted_components` total-points baseline selects the top 12 QBs, 24 RBs, 36 WRs, and 12 TEs. A learned route must lower MAE on that shared draft-relevant cohort with a paired-bootstrap 95% confidence-interval upper bound below zero. It must also remain within the configured pooled-MAE regression tolerance, and a total-points route must preserve top-N capture within the configured ranking tolerance. Otherwise the transparent baseline remains champion. The 2025 test is evaluated only after selection and never chooses a champion.

The generated Phase 4 evaluation records the current run identity, fingerprints, candidate counts, champion decisions, and live-board coverage. Learned selections use empirical training-only residual P10/P50/P90 ranges evaluated by season, position, and projection tier. Transparent selections remain point estimates with `P10=P50=P90`.

Historical preseason position evidence contains no valid rookie training cohort, so live rookies never receive a learned result. The board labels 233 point-only heuristic fallbacks: 21 QB, 46 RB, 114 WR, and 52 TE. This boundary is enforced in both persistence and presentation.

Publication uses one atomic integrity boundary. All six `player_projection_*` tables are staged with status `validating`, audited against the same open DuckDB connection, and promoted to `complete` before that transaction commits. The audit reconciles Phase 3 lineage, row counts, chronology, intervals, board coverage, artifacts, model cards, evaluation files, registry, and diagnostic plot hashes. Any integrity or promotion failure rolls the transaction back, preserving the prior complete publication.

The deterministic `run_id` names a model/data contract, while a unique `publication_id` names each immutable forced training attempt. DuckDB and the registered hashes are authoritative. Generated evaluation and registry files live under `models/reports/<run_id>/<publication_id>/`; artifact, card, and plot paths use the same attempt scope and are hashed. `docs/PHASE_4_MODEL_EVALUATION.*` and `models/registry.json` are convenience mirrors refreshed only after the verified transaction commits. Audit, status, and the projection service require exactly one current complete run and refuse stale, partial, orphaned, or tampered outputs. A changed Phase 3 feature/build or baseline-report fingerprint invalidates the dependent Phase 4 publication.

The Streamlit app reads this contract through a read-only service. When integrity passes, it exposes the 2026 board, position/search/target filters, selected method, intervals, explanations, and run lineage. Draft-facing services consume the selected points-per-game interval and multiply P10/P50/P90 by 17. They deliberately ignore predicted games active and direct season-total projections when ranking players, so the interface assumes full health and does not claim to predict injuries. Phase 4 itself remains player-outcome-only; Phase 5 supplies market movement and availability through a separate service. See [the Phase 4 evaluation report](PHASE_4_MODEL_EVALUATION.md).

## Phase 5 ADP movement and availability

Phase 5 is a validated transparent foundation, not a supervised model. `fantasy-draft data load-adp`
discovers FFC, direct Sleeper, and authorized manual aggregate manifests, verifies project-relative
raw files and SHA-256 hashes, rejects conflicting snapshot scope, and collapses duplicate manifests
that identify the same raw capture. An accepted FantasyPros Overall ADP export contributes four
immutable overall snapshots with sources `yahoo`, `sleeper`, `rtsports`, and `fantasypros`.
Synthetic fixture manifests are skipped unless explicitly requested. A stable snapshot identity
binds source, season, scoring format, team count, position scope, capture time, and raw hash.
Snapshot metadata and rows are upserted transactionally, so identical repeated loads preserve
counts and fingerprints.

Identity remains evidence-aware. Reviewed `player_source_mappings` win, exact ESPN/Yahoo/Sleeper
IDs may bridge through canonical fields or an immutable nflverse crosswalk, and one unique current
name + position + team match may receive `high` confidence. Ambiguous or unmatched rows retain a
nullable `player_id`, recorded mapping confidence, and stable source identity. Display name alone is
never a confirmed join key.

`fantasy-draft models build-adp-baselines` reads only verified production snapshots and builds three separate contracts:

- `adp_movement_features` contains as-of features such as prior ADP, elapsed days, fixed-horizon changes, velocity, acceleration, volatility, source spread, and observation counts. Every row is calculated using observations at or before its capture cutoff.
- `adp_movement_forecasts` records one-day persistence, linear-trend, and exponentially weighted trend results, including explicit unavailable status and reason. Persistence works with one observation; both trend methods require at least three dated observations for the same source identity.
- `adp_availability_parameters` stores the location and scale used by a continuity-corrected normal pick distribution. Source standard deviation wins, min/max-derived scale is second, and the versioned configuration fallback is used only when neither source measure exists.

`adp_phase5_builds` binds these tables to the snapshot-data and availability-configuration
fingerprints, counts, capability statuses, and a quality report. The current deterministic build
contains six snapshots, 2,795 observations/movement features/availability parameters, and 8,385
forecast rows. Its four FantasyPros-derived snapshots contain Yahoo 222 rows (185 mapped), Sleeper
302 (244 mapped), RTSports 328 (280 mapped), and FantasyPros composite 370 (299 mapped). The
post-build audit passes across 15 manifests and 19 verified immutable files.

The read-only market service calculates the probability that a still-available player is selected before the user's next pick. This distribution baseline is explicitly uncalibrated because no linked real-draft outcomes exist. Supervised movement and availability remain unavailable because one independent dated capture cannot support chronological training and validation. Phase 6 may consume this evidence only through reviewed canonical IDs; Phase 5 itself still makes no recommendation. See [the Phase 5 evaluation report](PHASE_5_ADP_AVAILABILITY_EVALUATION.md).

## Phase 6 event-sourced draft engine

Phase 6 is implemented as a deterministic decision engine around frozen upstream evidence. The draft-room service verifies the active Phase 4 rules reference, compares scoring-only fingerprints so compatible roster variants can share projections, selects only matching ADP season/team/scoring scopes, and joins market evidence strictly by reviewed canonical `player_id`. Display names are presentation fields and never fallback keys. A session can start in state-only mode when market mapping is incomplete.

Session creation freezes the canonical health-neutral projection rows derived from points per game times 17, any compatible reviewed market evidence, the Phase 4 and Phase 5 lineage, exact rules, engine-config fingerprint, seed, and simulation count. This pool is immutable for the life of the session. A later projection or ADP rebuild affects only newly created sessions.

The event stream is authoritative:

- `session_started`, `pick_made`, `pick_undone`, and `pick_replaced` records are appended, never rewritten;
- each mutation carries a unique command ID and expected version, preventing Streamlit reruns or stale callers from duplicating work;
- every event binds the prior and resulting state fingerprints;
- replay validates sequence, snake ownership, duplicate prevention, roster legality, pool fingerprint, metadata version, and final state hash;
- an undo targets only the latest active pick, while replacement retains the original event and pick ownership.

Roster assignment uses an exact legal allocation across direct starters, FLEX/SUPERFLEX slots, and bench rather than a greedy slot order. The same rules contract feeds replacement levels and simulation roster evaluation.

The `phase6-baseline-v1` configuration is versioned and fingerprinted as `17e0337939917fcfcb08ec764d88b43a7001e4c3c776c3ac8597390cb54ad9c9`. It defaults to 64 seeded rest-of-draft paths, evaluates six candidates, caps work, and requires 100% compatible market mapping. Simulation samples opponent choice from frozen ADP distributions, applies bounded roster-need and positional-run adjustments, and keeps point-only projections deterministic. The recommendation engine exposes balanced, safe-floor, and high-upside roles with recomputable component contributions. It returns a draft recommendation score, not a calibrated win or championship probability.

Controlled mapped fixtures validate simulation and recommendation behavior, including
ruleset-sensitive replacement value. Production remains deliberately gated: 877 of 1,278 compatible
FFC/Sleeper source observations map to active projection players (68.6%) while the engine requires
100%. When several sources map to one player, the newest compatible observation is selected with a
stable tie-break and its provenance is frozen. Market-only IDs and position-mismatched observations
are retained but excluded from the recommendation pool; true same-source/snapshot duplicates still
fail closed. The manual Streamlit room and CLI remain fully usable for session creation, picks,
undo, replacement, rosters, and replay verification; enhanced recommendation and Monte Carlo remain
unavailable until canonical identity review and a new frozen session. See
[the Phase 6 evaluation](PHASE_6_DRAFT_ENGINE_EVALUATION.md).

## Phase 7 multipage application and Phase 8 history workspace

Phase 7 replaced the monolithic Streamlit tabs with unique `st.navigation` routes. Phase 8 adds the eighth `/league-history` route without moving validation or warehouse logic into Streamlit. The root `app.py` is only an entry point; page modules render presentation, while typed services own inventory, validation, persistence, and report calculations.

| URL path | Page boundary |
|---|---|
| `/status` | Combines read-only project status, projection publication status, market readiness, and the recommended next action. |
| `/data-center` | Displays source/manifests, canonical table counts, and audit evidence; dispatches only allowlisted safe actions. |
| `/league-history` | Reads validated package quality, coverage, pseudonymous team outcomes, roster construction, drafted-only metrics, and the explicit outcome-model gate. |
| `/model-lab` | Reads the validated Phase 3/4 publication; it cannot train or promote models. |
| `/league-setup` | Validates and persists exact roster, scoring, draft-slot, and playoff inputs. |
| `/draft-room` | Reuses the Phase 6 repository and event stream for manual state and gated recommendations. |
| `/post-draft` | Builds a descriptive, fingerprinted report from a verified session and frozen pool. |
| `/learning-center` | Discovers Markdown guides and notebook Markdown without executing notebook code. |

### Data Center action boundary

`DataCenterSnapshot` is a read model over immutable manifests, source inventory, the canonical warehouse, and the audit result. User-triggered actions pass through a closed capability catalog and parameter validator. The app may:

- run the read-only audit;
- initialize or migrate DuckDB idempotently;
- archive nflverse players/weekly statistics and PFR snap counts in timestamped, hashed files;
- archive FFC ADP from its documented API;
- archive the explicit Sleeper ADP and nflverse platform-ID captures through CLI workflows;
- automatically validate, immutably archive, normalize, and transactionally load one selected
  FantasyPros Overall ADP CSV with `Rank`, `Player (Bye)`, `POS`, `Yahoo`, `Sleeper`, `RTSports`,
  and `AVG` (an optional `Real-Time` column is retained only in the original archive);
  and
- archive every user-selected league-history upload first, then validate and transactionally normalize only a versioned `league-history-v1` ZIP.

The existing nflverse, participation, and ADP canonical loads remain deliberate CLI-only handoffs:
`fantasy-draft data load-nflverse`, `fantasy-draft data load-nflverse-participation`, and
`fantasy-draft data load-adp`. League-history ZIP intake is the narrow exception because its
archive-first loader validates the complete user-selected contract and commits all canonical rows
in one transaction. Standalone history CSV/JSON files remain archive-only. Streamlit page reruns
never acquire ADP over the network. The Player Export upload path is the second narrow exception:
selecting a structurally valid file in the bottom-of-page control immediately preserves the exact
original FantasyPros CSV bytes and transactionally publishes four immutable overall snapshots.
There is no separate preview or confirmation action. Yahoo, Sleeper, and RTSports retain their named CSV values;
FantasyPros uses `AVG` as its displayed composite without recomputing it. Player resolution remains
conservative, so ambiguous display names stay unresolved rather than becoming canonical joins.
Re-selecting the identical file resolves to the existing verified archive rather than duplicating
raw evidence.

### Model Lab read boundary

`ModelLabSnapshot` reconstructs target and feature definitions, chronological folds, baseline/model metrics, champion decisions, residual summaries, feature importance, model-card and diagnostic references, and available live players from the validated warehouse publication. Player explanations come from the served projection payload; no estimator is loaded for inference or retraining. Nonchronological, missing, stale, or unreadable evidence makes the page unavailable. There is intentionally no training button.

### League setup and draft continuity

`LeagueSetupRecord` adds the user's draft slot and optional playoff context around `LeagueRules` without changing the existing canonical rules fingerprint. `LeagueSetupRepository` upserts one row per local setup in `league_rules`, rejects IDs already owned by historical-only rows, validates the decomposed columns against `normalized_ruleset_json` on reload, and excludes unrelated historical-only rules rows. YAML backup uses a versioned envelope plus `sha256:<ruleset fingerprint>` and rejects unknown fields or a mismatched digest. Deleting a setup does not delete draft sessions that already froze those rules.

The Draft Room builds its searchable board from the selected persisted setup and a verified
event-sourced session. When an accepted FantasyPros composite observation exists, it is the primary
market row and controls the default consensus ordering; a deterministic latest-source fallback is
used only when FantasyPros is absent. The separately labeled **Experimental Model Rank** uses the
health-neutral PPG-times-17 projection, rules-aware replacement value, and positional tiering. The
displayed model-versus-market delta makes disagreement auditable, and large gaps are presented as
warnings rather than silent overrides. Risk comes from the served interval width, while learned,
transparent-baseline, heuristic, and unavailable methods remain distinct. Enhanced
recommendation/simulation retains its separate canonical-coverage gate.

### Post-draft and learning reports

`PostDraftReport` verifies state/pool lineage before computing exact starter/bench assignment, positional draft capital, value versus reviewed ADP, ruleset-sensitive replacement risk, P10/P50/P90 summaries, strengths/weaknesses, and fixed-opponent strategy baselines. It supports incomplete drafts, but labels results provisional. Missing ADP is not imputed, point-only projections do not gain synthetic ranges, summed player intervals are not presented as calibrated team quantiles, and the strategy comparisons do not model opponent reactions. The report is descriptive and never estimates wins, playoffs, or championship probability.

The Learning Center scans only `docs/learning/**/*.md` and `notebooks/**/*.ipynb`. It reads Markdown cells for titles and summaries, keeps unreadable resources visible as unavailable, links to repository files, and never executes notebook code.

See [the Phase 7 evaluation](PHASE_7_STREAMLIT_EVALUATION.md) for the repository-wide local validation evidence and current hosted-CI caveat.

## Phase 8 league-history framework

The manual contract is a root-level `league-history-v1` ZIP containing `package.json`, `league_rules.csv`, `draft_picks.csv`, and `team_outcomes.csv`. Weekly rosters, matchups, and transactions are optional archived evidence and are not consumed by the initial descriptive build. The package asserts that personal identifiers have already been removed. Public football player IDs may remain; account, owner, and private crosswalk IDs may not.

The importer follows one fail-closed sequence:

1. copy the original bytes into the immutable raw archive and write a SHA-256 manifest;
2. verify the archived hash;
3. inspect the ZIP in memory without extracting it to disk;
4. reject traversal, absolute paths, nested files/archives, case collisions, links, encrypted members, undeclared files, excessive entries, expanded size, or compression ratio;
5. validate exact headers, field types, JSON rules, cross-file IDs, picks, team counts, outcomes, and package privacy/version metadata;
6. resolve players only through canonical platform IDs or the reviewed mapping registry—never display names;
7. reject conflicting existing source facts and roll back the complete canonical transaction; and
8. upsert no derived descriptions during import. A separate idempotent feature build reads only committed canonical rows.

Unresolved player evidence is preserved on `draft_picks` with a null `player_id`, source ID, display name, position, and mapping confidence. The existing identity-review queue aggregates those observations for human review. Applying an approved mapping changes only mapping fields on matching picks and leaves original draft facts unchanged.

`roster-construction-v1` describes positional picks by round, positional draft capital, first positions selected, RB/WR counts through rounds 3/5/8/10, exact starter coverage, bench depth, and ruleset demand. Historical ADP value, projected VORP, uncertainty, and bye concentration remain explicitly unavailable when cutoff-safe historical evidence does not exist.

`draft-only-v1` scores weekly optimal lineups made only from the originally drafted players, under the recorded scoring and roster rules and before the recorded playoff start. It reports optimal/best-ball points, drafted starter games, league-season percentile, and unfilled drafted-only starter slots. Any unresolved pick, unsupported position, or missing weekly evidence produces a named unavailable status and nullable metrics rather than fabricated zero performance.

The read-only gate in `configs/league_history_gate.yaml` requires 100 league-seasons, 1,000 team-seasons, five completed seasons, chronological validation/test coverage, 95% completeness/mapping, and balanced target examples before outcome-model evaluation can even be considered. A nonlinear model has a higher evidence floor. Passing those counts means eligible for independent review, not trained, approved, calibrated, or deployed. Phase 8 contains no playoff/championship training action and produces no outcome probability.

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

No ESPN, Yahoo, RTSports, Underdog, or FantasyPros scraping is used. FantasyPros acquisition is a
manual authenticated export: the user signs in and downloads the Overall ADP CSV in their own
browser. The application accepts that local file but never stores FantasyPros credentials or
cookies and never automates login or export acquisition. The explicit Sleeper ADP adapter reads a
public projections endpoint that is not part of Sleeper's documented API contract; it is isolated
behind the archive-first CLI workflow, uses no authentication, and may stop working without notice.
Live Sleeper league/draft synchronization and league-history import are not implemented. Any future
league integration must use documented read-only league interfaces. Personal league identifiers and
exported league setups should be reviewed and pseudonymized before publication. Secrets belong in
`.env`, which is ignored.
