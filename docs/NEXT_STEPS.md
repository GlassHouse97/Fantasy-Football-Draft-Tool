# Next Steps

## Current milestone

Phases 0 through 7 are implemented locally. Phase 7 turns the validated data, model, market, and draft-engine contracts into a seven-route Streamlit application:

| Route | Current status |
|---|---|
| `/status` | Ready; shows build facts, capability status, blocker, and next action. |
| `/data-center` | Ready; archives allowlisted sources immutably and reports manifests, canonical tables, and audit quality. |
| `/model-lab` | Ready and read-only; it has no training or publication button. |
| `/league-setup` | Ready; persists normalized rules/draft slot and supports fingerprint-checked YAML backup/restore. |
| `/draft-room` | Manual state ready; live recommendation and simulation remain mapping-gated. |
| `/post-draft` | Ready for complete or incomplete persisted sessions with explicit limitations. |
| `/learning-center` | Ready; previews guide and notebook Markdown without executing code. |

Start the app from the repository root:

```powershell
.\.venv\Scripts\Activate.ps1
fantasy-draft app
```

The local app does not weaken prior quality boundaries. Data Center acquisition creates new timestamped raw files and SHA-256 manifests; canonical nflverse, participation, and ADP loads remain deliberate CLI handoffs. Model Lab reads only the validated publication. Draft Room persists through DuckDB and event replay, not browser state. Post-Draft reports use the session's frozen rules/player pool and never invent missing market evidence or uncertainty.

## Operator action required for live recommendations

Manual drafting is usable now with 1,367 canonical projection rows. Live recommendation and Monte Carlo actions remain correctly locked because 0 of 203 draftable PPR/12-team QB/RB/WR/TE ADP rows have reviewed canonical mappings. The 43 archived PK/DEF rows remain auditable outside this ruleset's projection and roster coverage. Display names are never used as fallback joins.

Refresh and review the identity worksheet, then rebuild the market publication:

```powershell
fantasy-draft data review-identities
fantasy-draft data apply-identity-overrides data\processed\identity\identity_review_queue.csv
fantasy-draft data review-identities
fantasy-draft data load-adp
fantasy-draft models build-adp-baselines --availability-config configs/adp_availability.yaml --output docs/PHASE_5_ADP_AVAILABILITY_EVALUATION.md
fantasy-draft data audit
fantasy-draft status
```

Only apply a worksheet after checking every decision, reviewer, timestamp, and required note. The override command validates the complete file before writing and archives it with immutable provenance. After the rebuilt Phase 5 status is ready, create a new draft session; existing state-only sessions intentionally retain their original frozen unresolved pool.

Continue capturing independent dated production ADP snapshots during draft season. Persistence is active, but linear and exponentially weighted movement methods need at least three dated observations per source player. Real linked draft outcomes are still required before availability calibration can be evaluated.

## Verified Phase 7 quality evidence

Phase 7's local publication gates are complete:

- Ruff passed.
- Strict mypy passed across 87 source files.
- All 38 focused service, repository, and UI tests passed during incremental validation.
- The final repository-wide pytest run passed 251 tests in 127.81 seconds.
- Streamlit AppTest loaded the default entry point and all seven pages with zero exceptions.
- The CLI data audit passed across eight manifests and 12 verified immutable raw files.
- Real browser QA navigated the local multipage app and successfully ran the live Data Center audit action.

To reproduce the final local gates:

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\test.ps1
fantasy-draft data audit
```

The complete evidence is recorded in [the Phase 7 evaluation](PHASE_7_STREAMLIT_EVALUATION.md).

## Phase 6 hosted-CI retry

Phase 6 PR #6 is merged, but its GitHub Actions evidence is not marked green. GitHub's runner outage canceled the pull-request and `main` workflows before any runner was assigned; `main` run `31119062454` completed zero steps with `runner_id=0`. An hourly reminder is active to:

1. check GitHub's Actions service status;
2. rerun the failed/canceled `main` workflow only after runners are accepting jobs;
3. watch the rerun to completion;
4. report the real result and disable the reminder after a green run; and
5. inspect an actual code failure before changing code if the rerun reaches a runner but fails.

The passing local Phase 6 gates remain useful evidence, but they are not a substitute for a completed hosted workflow.

## Phase 8 gate

Do not train league-outcome or championship models next. Sleeper import and league-history parsing/normalization are still unavailable. Phase 7 can only quarantine-archive a pseudonymized CSV, JSON, or ZIP package without inspecting or consuming it, so the repository still lacks validated linked histories for those claims.

The next development phase should begin with a versioned, privacy-safe league-history import contract and descriptive analysis only:

1. define a pseudonymized history package and validation report;
2. implement immutable archive and idempotent normalization;
3. add descriptive league/draft summaries without causal or probability claims;
4. measure seasons, teams, outcome completeness, and class balance; and
5. permit outcome modeling only if a written data-sufficiency gate passes.

Championship probability remains disabled throughout Phase 7 and until that future gate is genuinely satisfied.

## Frozen upstream contracts

Keep these validated publications unchanged unless their own phase is intentionally rebuilt:

- Phase 3: 11,171 cutoff-safe features, 9,804 historical targets, and 1,367 live 2026 rows. See [the Phase 3 evaluation](PHASE_3_BASELINE_EVALUATION.md).
- Phase 4: active run `phase4-7ae8e9aed04bffca00c0`, 24 registered models, 12 champion routes, and a complete 1,367-row projection board. See [the Phase 4 evaluation](PHASE_4_MODEL_EVALUATION.md).
- Phase 5: 246 production observations, 246 movement features, 738 baseline forecasts, and 246 availability parameter rows. See [the Phase 5 evaluation](PHASE_5_ADP_AVAILABILITY_EVALUATION.md).
- Phase 6: event-sourced state, exact lineup assignment, frozen pools, seeded simulation fixtures, and transparent recommendation roles. See [the Phase 6 evaluation](PHASE_6_DRAFT_ENGINE_EVALUATION.md).

No Phase 7 page retrains, silently reloads, or relabels those upstream contracts.
