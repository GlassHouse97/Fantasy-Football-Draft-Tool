# 🏈 Fantasy Football Draft AI

[![Quality gates](https://github.com/GlassHouse97/Fantasy-Football-Draft-Tool/actions/workflows/quality.yml/badge.svg)](https://github.com/GlassHouse97/Fantasy-Football-Draft-Tool/actions/workflows/quality.yml)

A local-first NFL redraft assistant that turns historical football data, exact league rules, and optional verified draft-market information into transparent recommendations. The goal is useful software **and** a practical course in sports modeling. No LLM decides who you should draft.

## What works today

The runnable local foundation includes:

- a packaged Python CLI and recommendation-first local Streamlit application;
- immutable raw-file archives with SHA-256 manifests;
- a DuckDB warehouse schema for the project’s canonical tables;
- current `nflreadpy`, Fantasy Football Calculator, and explicit Sleeper ADP adapters with offline reuse;
- immutable nflverse/PFR snap-count captures and transactional participation loading;
- a validated in-app FantasyPros Overall ADP CSV upload path that preserves the supplied export and publishes Yahoo, Sleeper, RTSports, and FantasyPros composite snapshots without login automation;
- an auditable player-identity review queue and durable source-ID mapping registry;
- immutable, validated manual identity overrides that survive nflverse reloads;
- deterministic league-rule normalization and fingerprints;
- configurable fantasy scoring, explicit FLEX/SUPERFLEX eligibility, and two replacement-value definitions;
- cutoff-safe player-season features, separately persisted future targets, and source provenance;
- five transparent projection baselines evaluated on expanding 2020-2025 folds;
- position-specific Ridge and histogram gradient-boosting models with cutoff-safe, draft-relevance-aware validation gates;
- a validated 2026 projection publication with P10/P50/P90 displays, player explanations, and explicit labels for unvalidated rookie fallbacks;
- consensus-first current-player tables that prefer FantasyPros composite ADP when it is present and keep the health-neutral model rank visibly experimental;
- idempotent, hash-verified normalization of immutable FFC, Sleeper, and authorized FantasyPros aggregate ADP captures;
- cutoff-safe ADP movement features with persistence, linear-trend, and exponentially weighted baselines;
- a transparent next-pick availability distribution with source-reported spread evidence and labeled fallbacks;
- an event-sourced snake-draft engine with immutable session pools, append-only picks, undo, replacement, and replay hashes;
- exact ruleset-aware lineup assignment plus a seeded Monte Carlo and transparent recommendation baseline;
- a quick-start redraft assistant with one-click picks, immediate projection-based advice, and a deterministic draft CLI;
- a professional native dark Draft Night interface with Inter body text, Outfit headings, compact turn and recommendation cards, and position-aware color cues;
- a round-by-team snake draft board plus streamlined, pinned available-player and rankings tables for faster live use;
- league-adjusted player rankings based on value over replacement rather than raw cross-position points;
- normalized, fingerprinted league setup persistence with YAML backup and restore;
- an auditable Data Center and read-only Model Lab that preserve the data and model publication gates;
- descriptive post-draft lineup, draft-capital, ADP-value, replacement-risk, and strategy reports;
- a Learning Center that previews local guides and notebook Markdown without executing code;
- a privacy-gated `league-history-v1` template, safe ZIP validator, immutable archive, and idempotent canonical loader;
- reviewed historical player mappings, roster-construction features, drafted-only descriptions, and an explicit outcome-model evidence gate;
- tests for data integrity, leakage, chronological evaluation, model selection, publication integrity, ADP idempotency, availability bounds, scoring, rules, and replacement value.

Phases 0 through 8 from the master specification are implemented. The current product milestone refocuses that foundation on the actual draft-day job: start a supported 2026 full-PPR snake draft, record each QB/RB/WR/TE selection, and see the best available players when your team is on the clock. Accepted FantasyPros composite ADP is the primary default ordering when it is present; the separately labeled **Experimental Model Rank** adds rules-aware replacement value and positional context. Draft-facing model projections assume every player is healthy and available for all 17 regular-season games by scaling the served points-per-game projection. They do not estimate injuries or games missed. Live rookies remain explicitly unvalidated point-only heuristic fallbacks with no estimated risk range. Quick Start offers two built-in no-K/DST roster presets and cannot record kicker or team-defense selections, so it is not yet a complete live tracker for leagues that draft those positions. The stricter market-simulation layer remains separately gated by canonical mapping coverage. No championship probability is produced.

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
fantasy-draft data snapshot-platform-player-ids
fantasy-draft data snapshot-sleeper-adp --season 2026
fantasy-draft data snapshot-ffc-adp --season 2026 --format ppr --teams 12
fantasy-draft data import-espn-adp data\templates\espn_adp_snapshot_template.csv
fantasy-draft data load-adp
fantasy-draft data review-identities
fantasy-draft data audit
```

Network commands preserve timestamped raw files. Add `--offline` to reuse an existing matching download without making a request. `load-nflverse` verifies one manifest-paired capture and its raw hashes, excludes only reported non-player placeholders, preserves curated identity mappings, and upserts nflverse weekly keys in one transaction. Unmentioned rows are never deleted by a potentially partial capture, and repeating the same manifest leaves canonical rows and counts unchanged.

`review-identities` verifies the latest nflverse, FFC, and supported platform captures,
refreshes the DuckDB review queue, and exports an editable worksheet to
`data/processed/identity/identity_review_queue.csv`. Exact ESPN/Yahoo/Sleeper IDs resolve through
canonical fields or the archived nflverse crosswalk. Name-based comparisons only propose
candidates; they never create a confirmed mapping without human approval. Platform-ID ambiguity
for an observed source row fails closed, while unrelated historical crosswalk collisions do not
block another platform's review. FFC team-defense rows (`DEF`, `DST`, or `D/ST`) are explicitly
excluded from player mapping.

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

Reproducibility uses separate feature, target, and combined-build hashes. Rebuilding identical inputs must reproduce all three, while any feature or target change invalidates dependent baseline rows until evaluation is rerun. The current values are published by the generated Phase 3 evaluation rather than duplicated here.

Five deterministic baselines are evaluated on chronological 2020-2025 folds. The report separates the all-candidate attrition view from positive-game accuracy, preserves missing participation-dependent outcomes as unavailable, and does not backfill current ADP into historical folds. These Phase 3 fingerprints and folds remain the comparison contract for Phase 4; current row counts and metrics live in the generated Phase 3 evaluation.

## Reproduce the Phase 4 model run

Phase 4 trains one Ridge and one histogram gradient-boosting model for each QB/RB/WR/TE and points-per-game/games-active/total-points route. Learned models receive raw `age_at_cutoff`; they do not also receive the deterministic `age_adjustment_factor` used by transparent baselines. This prevents the model from learning age on top of a second hand-authored age penalty.

```powershell
fantasy-draft models train-player-models --rules configs/example_ppr_12_team.yaml --validation-start-season 2020 --test-season 2025 --output docs/PHASE_4_MODEL_EVALUATION.md
fantasy-draft data audit
fantasy-draft status
fantasy-draft app
```

Model selection freezes one cutoff-safe draft-relevant cohort per validation season from the transparent weighted-components total-points baseline: the top 12 QBs, 24 RBs, 36 WRs, and 12 TEs. A learned candidate must improve MAE on that same cohort with a paired-bootstrap 95% confidence interval below zero. It must also remain within the configured pooled-MAE tolerance, and total-points candidates must preserve top-N capture within the configured ranking tolerance. The 2025 test is evaluated only after selection and never chooses a champion. Current run IDs, fingerprints, winner counts, and metrics live in the generated Phase 4 evaluation.

Learned P10/P50/P90 ranges use signed residuals from training-only, earlier out-of-fold predictions and are evaluated by season, position, and projection tier. A retained baseline remains an honest point estimate with `P10=P50=P90`. The 233 live rookies also use point-only transparent fallbacks because Phase 3 has no historical preseason rookie-position cohort: QB 21, RB 46, WR 114, and TE 52.

DuckDB is authoritative for the one active deterministic run. Every training attempt receives an immutable `publication_id`, and its reports, registry, diagnostic plots, model cards, and serialized artifacts live beneath `<run_id>/<publication_id>/` paths verified by registered SHA-256 hashes. All six Phase 4 tables are staged, audited, and promoted in one DuckDB transaction, so a failed forced retry rolls back to the previously complete publication. The top-level Phase 4 report and `models/registry.json` are convenience mirrors refreshed only after commit. Audit, status, and the app reject partial, stale, orphaned, count-mismatched, or hash-mismatched publication state.

## Reproduce the Phase 5 ADP foundation

Phase 5 verifies every archived FFC, direct Sleeper, or authorized manual aggregate capture against
its manifest, including the Yahoo/Sleeper/RTSports/FantasyPros snapshots produced from an accepted
FantasyPros Overall ADP export. It collapses duplicate manifests that point to the same immutable
raw payload and loads each production snapshot idempotently. Clearly labeled synthetic captures are
skipped by default.

```powershell
fantasy-draft data load-adp
fantasy-draft models build-adp-baselines --availability-config configs/adp_availability.yaml --output docs/PHASE_5_ADP_AVAILABILITY_EVALUATION.md
fantasy-draft data audit
fantasy-draft status
fantasy-draft app
```

The deterministic August 24 rebuild contains six production snapshots, 2,795 observations, 2,795
movement features, 8,385 forecast rows, and 2,795 availability parameters. Four snapshots come
from the authenticated FantasyPros Overall export: Yahoo 222 rows (185 mapped), Sleeper 302 (244
mapped), RTSports 328 (280 mapped), and FantasyPros composite 370 (299 mapped). Unresolved rows
remain source-keyed rather than being forced onto a player. The labeled ESPN fixture remains
excluded from the production build.

The availability distributions remain explicitly uncalibrated because no linked real-draft
outcomes are archived, and no supervised movement or availability model is claimed. See the
[dated market quality report](docs/ADP_MARKET_QUALITY_REPORT_2026-08-24.md).

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

The versioned `phase6-baseline-v1` configuration uses 64 default simulation paths, evaluates six candidates, and requires 100% canonical market coverage. Controlled mapped fixtures prove seeded rest-of-draft simulation, distinct balanced/safe-floor/high-upside outputs, configurable component weights, ruleset-sensitive replacement value, and the absence of championship-probability claims. That enhanced engine remains distinct from the app's projection-first guidance.

Current enhanced-simulation status remains `identity_mapping_required`, but the market foundation is
now partially linked: 877 of 1,278 compatible FFC/Sleeper source observations are mapped to active
projection players (68.6%; the versioned engine requires 100%). Cross-source rows for one player are
resolved deterministically to the newest capture. Another 295 rows are safely outside the frozen
recommendation pool, including 245 mapped market-only players and seven position-mismatched rows;
they remain archived and reported. Names are never used as an unqualified fallback join. The main
Draft Assistant still recommends from projections and league rules; the CLI `draft recommend`
command remains the stricter market-simulation action and stays unavailable until the residual
identity queue is reviewed and Phase 5 is rebuilt:

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

After the GitHub Actions outage recovered, Phase 6 pull-request run `31118319345` completed on a hosted runner with every quality step green. On August 14, 2026, the affected Phase 6 `main` run `31119062454` was safely canceled and rerun; attempt 2 received real hosted job `94857281821` and completed green in 1 minute 49 seconds with Ruff, mypy, and pytest passing. Later green descendant `main` runs also include the Phase 6 code.

## Use the local application

Start the app from the repository root:

```powershell
fantasy-draft app
```

Streamlit exposes one stable route for each workflow:

| Route | Purpose |
|---|---|
| `/` | Default quick start, best pick now, alternatives, one-click pick tracking, compact roster, and round-by-team snake board |
| `/rankings` | Searchable consensus-first rankings with FantasyPros market rank, Experimental Model Rank, rank delta, projections, tiers, and value over replacement |
| `/draft-report` | Descriptive lineup, positional capital, value, risk, strategy, and limitation report |
| `/player-export` | Downloadable consensus-first comparison with Experimental Model Rank, model-versus-market delta, and one bottom-of-page FantasyPros Overall ADP CSV upload |
| `/player-market-consensus` | Player-first creator-opinion lookup with an explicit transcript-corpus evidence gate |
| `/help` | Plain-language quick start, live-pick instructions, and recommendation glossary |
| `/league-settings` | Advanced roster/scoring/playoff rules, draft slot, fingerprint, and YAML backup/restore |
| `/technical-draft-room` | Advanced frozen-board, replay, and market-simulation diagnostics |
| `/system-status` | Project readiness, data/model facts, blockers, and local reset controls |
| `/data-center` | Immutable source archives, manifests, warehouse inventory, and quality audit |
| `/league-history` | Historical-package quality, roster construction, drafted-only results, and outcome-model gate |
| `/model-details` | Read-only model contract, chronological evidence, diagnostics, and player explanations |
| `/learning-center` | Advanced guides and notebook previews for the underlying data science |

The current local interface uses Streamlit's native dark theme rather than fragile page-level CSS. Inter keeps controls and tables readable, while Outfit gives headings the same clean geometric direction as the public DraftIQ redraft interface. Turn status, the primary recommendation, alternatives, and roster information are grouped into distinct bordered cards. On the user's turn, recommendation and roster context appear before the player pool; on an opponent's turn, the available-player table moves up so **Record taken** is the immediate action. Available-player and rankings tables default to FantasyPros consensus rank when it is present, keep player identity pinned, and expose Experimental Model Rank plus the market delta alongside it. Large rank disagreements are warnings to investigate, not proof that either source is correct. **Draft activity** defaults to a position-colored, round-by-team snake board with the user's column and current pick called out; a chronological pick log remains available as the alternate view. Projection, market, and live-news limitations remain accessible in compact badges and disclosure sections without dominating the main drafting workflow.

**Player Evaluation** is the active follow-up direction. Player Export List unions the validated
2026 projection board with accepted current-season market-only players and reads latest exact-scope
platform snapshots directly from DuckDB. The bottom of the page accepts one manually downloaded
FantasyPros **Overall ADP** CSV with the required columns `Rank`, `Player (Bye)`, `POS`, `Yahoo`,
`Sleeper`, `RTSports`, and `AVG`; the optional `Real-Time` column is ignored. Selecting a valid file
automatically preserves its exact original bytes and
loads four immutable overall snapshots: `yahoo`, `sleeper`, `rtsports`, and `fantasypros`. The `AVG`
field is displayed as the FantasyPros composite; it is not recomputed from the other three columns.
Identity mapping remains conservative, so ambiguous players stay unresolved instead of being
joined by name alone. The verified board now has 1,368 players, 276 with market data, 927 platform
observations, and 165 complete four-source comparisons. FantasyPros `AVG` produces the primary
**Consensus Rank** when present. **Experimental Model Rank** is secondary and uses the same
replacement-value ranking contract as Draft Assistant under the default 12-team full-PPR Standard
roster (1 QB, 2 RB, 2 WR, 1 TE, 1 FLEX, and 7 bench spots; no K/DST). Its draft-facing projection
is points per game multiplied by 17 healthy games; neither predicted games active nor direct
season-total predictions can lower a player because of an injury assumption. The displayed delta
is Consensus Rank minus Experimental Model Rank, so a positive value means the model is more
optimistic than the market. Market-only players without a supported projection can remain blank.
Player Market Consensus registers Fantasy Football Advice as its first 2026 source
but intentionally displays no stance until a complete video inventory, transcript coverage report,
alias-aware mention index, and reviewed aggregation exist. See
[Player Evaluation Milestones](docs/PLAYER_EVALUATION_PLAN.md).

The Data Center may run read-only audits, idempotent warehouse initialization, immutable
nflverse/snap-count/FFC/Sleeper/authorized platform archive actions, and the archive-first
`league-history-v1` ZIP workflow. A history ZIP is preserved before in-memory validation and
changes canonical tables only through one successful transaction. Standalone history CSV/JSON
remains archive-only. Existing nflverse, participation, and ADP canonical loads remain explicit
CLI handoffs (`load-nflverse`, `load-nflverse-participation`, and `load-adp`). Sleeper ADP acquisition
is archive-first through its explicit CLI command. The FantasyPros aggregate path supports a CSV
that the user downloads after signing into FantasyPros in their own browser. Selecting the file
starts local validation and import immediately; there is no preview or confirmation step. The app
does not store FantasyPros credentials or cookies, automate the login, or acquire that export
during a Streamlit rerun.

Model Lab never trains or promotes a model. It reads the validated Phase 3/4 publication and shows target/feature definitions, chronological folds, learned-versus-baseline decisions, metrics, residuals, feature importance, model cards, and served player explanations. Use the CLI training command only when intentionally creating a new model publication.

Draft Assistant quick start keeps the checked-in 2026 full-PPR scoring contract and offers two no-K/DST roster presets: Standard (2 WR, 1 FLEX) and WR/FLEX-heavy (3 WR, 2 FLEX), both with seven bench spots. The user chooses the preset, league size, draft position, and name. Saved **League settings** do not alter Quick Start. To use another full-PPR QB/RB/WR/TE/FLEX/SUPERFLEX/bench roster, save it in **League settings** and create the session in **Technical draft room**; scoring must still match the active projection publication. Each session freezes its exact rules, health-neutral PPG-times-17 projections, and optional market lineage. FantasyPros consensus is the primary board reference when present, while personalized recommendation components remain separately labeled. Draft reports may be generated for incomplete drafts, but those values are labeled provisional; missing ADP and uncertainty remain missing rather than being imputed. Rookie heuristic rows remain the explicit exception: they are unvalidated point estimates with `P10=P50=P90` and risk marked unavailable.

The production audit is green across 15 manifests and 19 verified immutable raw files after the
deterministic Phase 5 rebuild. Local Player Export verification covers its 1,368-player universe,
276 players with market data, 927 platform observations, 165 complete comparisons, search reset,
and QB/RB/WR/TE-only position filter. Hosted pull-request and resulting `main` workflows remain the
publication gate; GitHub Actions is the live source of truth for that evidence.

Phase 7 validation passed Ruff, strict mypy across 87 source files, 251 pytest tests in 127.81 seconds, AppTest with zero exceptions across all seven pages, and the CLI data audit across eight manifests and 12 verified immutable files. Real browser QA navigated the multipage app and successfully triggered the live Data Center audit action. See [the Phase 7 evaluation](docs/PHASE_7_STREAMLIT_EVALUATION.md).

After service recovery, the Phase 7 pull-request rerun and a no-functional-change `main` retrigger both completed on hosted runners with every quality step green.

## Use the Phase 8 history framework

Download the header-only template from Data Center or copy `data/templates/league_history_v1` to a private working location. Pseudonymize league/team/owner information before selecting a file. The app does not transmit the upload, but this checkout is inside OneDrive, so OneDrive, Windows backup, or other software may synchronize the raw local archive.

The safe command-line sequence is:

```powershell
fantasy-draft data import-league-history C:\path\to\pseudonymized-history.zip
fantasy-draft data review-identities
# Inspect and edit the generated worksheet before applying any decisions.
fantasy-draft data apply-identity-overrides data\processed\identity\identity_review_queue.csv
fantasy-draft data review-identities
fantasy-draft features build-roster-history
fantasy-draft data audit
fantasy-draft status
```

The importer rejects unsafe ZIP structures, contract/header errors, inconsistent drafts/outcomes, privacy assertions that are not `false`, and conflicting existing source facts. Exact public platform IDs or reviewed mappings are the only accepted player joins. Re-importing identical bytes or equivalent normalized content does not duplicate canonical rows. A rejected ZIP retains its immutable archive and quality report but writes no rules, picks, or outcomes.

Roster construction and drafted-only optimal-lineup reports are descriptive. Missing player mappings, incomplete weekly evidence, or unsupported positions leave numeric results null with an explicit status. The configured model gate remains locked with the current 0 real histories, and the application exposes no playoff/championship training button even if future counts reach the review threshold.

Start the guided human test with [the Human Testing Guide](docs/HUMAN_TESTING_GUIDE.md), then use [the League History Import Guide](docs/LEAGUE_HISTORY_IMPORT_GUIDE.md) for the manual historical-data workflow.

Phase 8 validation passed Ruff, strict mypy across 92 source files, all 281 repository tests in 139.01 seconds, AppTest with zero exceptions across all eight pages, the production data audit across eight manifests and 12 verified immutable files, and real browser checks of the history, Data Center, and protected local-reset workflows. PR #8 and its resulting `main` run later completed on hosted runners with every quality step green. See [the Phase 8 evaluation](docs/PHASE_8_LEAGUE_HISTORY_EVALUATION.md).

## Learn the system

- [Architecture](docs/ARCHITECTURE.md)
- [Assumptions](docs/ASSUMPTIONS.md)
- [Implementation checklist](docs/IMPLEMENTATION_CHECKLIST.md)
- [User data checklist](docs/USER_DATA_CHECKLIST.md)
- [Human testing guide](docs/HUMAN_TESTING_GUIDE.md)
- [League history import guide](docs/LEAGUE_HISTORY_IMPORT_GUIDE.md)
- [League history and roster construction](docs/learning/11_league_history_and_roster_construction.md)
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
- [Phase 8 league-history evaluation](docs/PHASE_8_LEAGUE_HISTORY_EVALUATION.md)
- [Next steps](docs/NEXT_STEPS.md)

## Data boundaries

Downloaded data, generated review worksheets, manual uploads, DuckDB files, serialized estimators, and authoritative attempt-scoped reports are ignored by Git. Publication-safe evaluation mirrors, model cards, and diagnostic figures may be versioned with their registered hashes; small templates and clearly labeled fixtures are also versioned. Never commit league exports or completed identity-review worksheets containing private or identifying information without reviewing and pseudonymizing them first.

## Attribution

Historical NFL data is accessed through [nflreadpy and nflverse](https://nflreadpy.nflverse.com/). Draft-market snapshots use the documented [Fantasy Football Calculator ADP API](https://help.fantasyfootballcalculator.com/article/42-adp-rest-api) and should retain source attribution.

## License

MIT. Third-party data remains subject to its source terms.
