# Phase 7 Streamlit Evaluation

Implementation status: **PASSED**

Local publication gate: **PASSED**

Hosted Phase 6 CI recovery: **PENDING OUTAGE RETRY — NOT GREEN**

## Validated application foundation

Phase 7 organizes the existing project into seven stable local routes while keeping business rules outside Streamlit page modules:

| Route | Validated responsibility |
|---|---|
| `/status` | Project facts, data/model readiness, unresolved mappings, capability inventory, and one recommended next action. |
| `/data-center` | Immutable source/manifests, canonical warehouse inventory, live quality report, and allowlisted data actions. |
| `/model-lab` | Read-only target/feature/split definitions, baseline/model comparisons, metrics, residuals, importance, model cards, and player explanations. |
| `/league-setup` | Exact roster, FLEX/SUPERFLEX, bench/IR, scoring, draft-slot, and playoff settings with normalized persistence. |
| `/draft-room` | Persistent manual event-sourced drafting, searchable board, filters, likely-gone evidence, rosters, explanations, and gated recommendations. |
| `/post-draft` | Exact lineup and descriptive roster-value report with lineage, limitations, and JSON export. |
| `/learning-center` | Read-only discovery, previews, and repository links for guides and notebook Markdown. |

`app.py` delegates to `fantasy_draft_ai.ui.app`; page renderers consume typed services. Model training, data normalization, draft state, and post-draft calculations do not live in the page files.

## Data Center boundary

The page may execute only actions that the service labels safe for in-app use:

- read-only data audit;
- idempotent warehouse initialization/migration;
- immutable nflverse player and weekly-stat archive;
- immutable nflverse/PFR snap-count archive;
- immutable Fantasy Football Calculator ADP archive; and
- validated immutable ESPN CSV archive; and
- immutable quarantine archive for a user-selected CSV, JSON, or ZIP league-history package.

Every acquisition preserves timestamped raw evidence and a SHA-256 manifest. The Data Center does not silently load or rebuild downstream warehouse products. Its capability catalog provides explicit CLI handoffs for:

```powershell
fantasy-draft data load-nflverse
fantasy-draft data load-nflverse-participation
fantasy-draft data load-adp
```

Sleeper league import remains disabled with an explicit `not_implemented` status. League-history intake is explicitly `archive_only`: the bytes and manifest are preserved locally after a privacy warning, but the package is not unpacked, parsed, normalized, analyzed, or used for training. No synthetic league history is generated.

## Model Lab boundary

Model Lab reads the validated Phase 3/4 publication. It validates chronology before exposing claims, presents learned and transparent-baseline choices separately, and explains that importance is associative rather than causal. Served player explanations come from the stored projection payload. Point-only predictions remain point-only.

There is no training or model-promotion button. A missing, stale, unreadable, or nonchronological publication makes the page unavailable instead of training a replacement.

## League Setup boundary

`LeagueSetupRecord` wraps the existing normalized `LeagueRules` with a user draft slot, platform/identifier, and optional playoff settings. The DuckDB repository:

- upserts by local setup ID without creating duplicates and rejects IDs that belong to historical-only rules rows;
- persists `user_draft_slot` and playoff JSON in `league_rules`;
- revalidates normalized rules, decomposed fields, and the existing ruleset fingerprint on load;
- excludes unrelated historical-only rows without a user draft slot; and
- leaves already frozen draft sessions intact when a setup is edited or deleted.

YAML backup uses a deterministic `league-setup-v1` envelope with `sha256:<ruleset fingerprint>`. Import rejects unknown fields, invalid team-dependent settings, and fingerprint mismatches.

## Draft Room and live readiness

The Draft Room retains the Phase 6 append-only event and replay contract. It adds transparent overall/position ranks, team-count position tiers, interval-derived risk, method provenance, ADP value, and a conditional likely-gone indicator. Missing reviewed market evidence remains visible and does not remove a player from the manual board.

Current live production readiness remains:

- canonical manual-state players: **1,367**;
- compatible draftable QB/RB/WR/TE ADP rows: **203**;
- reviewed canonical mappings: **0**;
- live market coverage: **0.0%** of **100.0% required**;
- archived PK/DEF rows outside active roster/projection coverage: **43**;
- manual pick, undo, replacement, roster, persistence, and replay status: **available**;
- recommendation and Monte Carlo status: **`identity_mapping_required`**; and
- championship probability: **disabled**.

Controlled fixtures still validate the recommendation engine. They do not override the live mapping gate. A new recommendation-ready session may be created only after identity review and a validated Phase 5 rebuild.

## Post-Draft boundary

The post-draft service verifies the session/player-pool fingerprint before producing a deterministic report. It includes:

- exact starter, FLEX/SUPERFLEX, and bench assignment;
- starter, bench, and roster P10/P50/P90 summaries when supported;
- positional picks, draft capital, replacement estimates, and P50 VORP;
- pick value versus reviewed ADP;
- starter floor versus replacement risk;
- ruleset-specific strengths and weaknesses;
- transparent fixed-opponent strategy comparisons;
- session, pool, model, ADP, and rules lineage; and
- a canonical JSON export and report fingerprint.

The report is useful before draft completion but labels incomplete values provisional. It does not impute missing ADP, turn point estimates into uncertainty, treat summed marginal intervals as calibrated team quantiles, or simulate counterfactual opponent reactions. It is descriptive draft analysis and does not estimate wins, playoff odds, or championship probability.

## Learning Center boundary

Learning Center discovers Markdown below `docs/learning/` and notebooks below `notebooks/`. It extracts titles and concise summaries from guide text or notebook Markdown cells, keeps unreadable resources visible as unavailable, and links to the repository. Notebook code cells are never executed by the page.

## Quality evidence

The recorded Phase 7 evidence is:

- Ruff: **passed**;
- strict mypy: **passed across 87 source files**;
- focused service/repository/UI tests: **38 passed** during incremental validation;
- final repository-wide pytest: **251 passed in 127.81 seconds**;
- Streamlit AppTest: **zero exceptions across the default entry point and all seven pages**;
- CLI data audit: **passed across eight manifests and 12 verified immutable raw files**; and
- real browser QA: **passed multipage navigation and successfully ran the live Data Center audit action**.

These are local Phase 7 gates. The separate Phase 6 hosted-CI caveat below remains open because its canceled workflow never reached a runner.

## Hosted-CI caveat

Phase 6 PR #6 is merged, but its GitHub Actions workflows were canceled during a GitHub runner outage before a runner was assigned. The `main` workflow run `31119062454` completed zero steps with `runner_id=0`; it is **pending retry**, not green. An hourly reminder is active to wait for runner recovery, rerun the workflow, watch it to completion, report the real result, and disable itself after a green run. If a runner executes the workflow and finds a genuine code failure, that failure must be inspected before any code change.

Local validation evidence is not presented as hosted-CI success.

## Phase boundary

Phase 7 is complete as a runnable local application and passes its repository-wide local gates. It adds no outcome model and does not weaken data, publication, identity, or draft-replay integrity. The operator identity review remains the separate data action required to activate live recommendations. Phase 8 must begin with real, privacy-safe league-history ingestion and descriptive analysis; championship probability remains disabled.
