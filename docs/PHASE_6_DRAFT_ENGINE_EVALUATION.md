# Phase 6 Draft Engine Evaluation

Engine status: **PASSED**
Production recommendation status: **GATED — CANONICAL IDENTITY MAPPING REQUIRED**

## Validated engine foundation

- Event-sourced snake state with deterministic odd/even ownership and next-user-pick calculation.
- Append-only session, pick, undo, and replacement events.
- Idempotent command IDs, optimistic event versions, and linked prior/result state fingerprints.
- Frozen session player pools with exact Phase 4/5, rules, scoring, configuration, seed, and simulation lineage.
- Exact direct-starter, FLEX/SUPERFLEX, and bench assignment without greedy slot-order dependence.
- Canonical-ID-only projection/market joins with explicit duplicate, scope, mapping, and position-conflict gates.
- Runnable Streamlit session creation, manual picks, undo, replacement, roster grid, restore, and replay status.
- Runnable CLI create/list/show/pick/undo/replace/verify workflow.
- Seeded rest-of-draft simulator and transparent balanced, safe-floor, and high-upside recommendation baseline.

## Versioned configuration

- Version: `phase6-baseline-v1`
- Reference rules fingerprint: `9f660dd5c8db91e63a1c43a5db74a3848b0554b2acf94d0fd891fe58b4eb7871`
- Scoring-only fingerprint: `984854f3468e902beaab0381e735d7b2d1ac331e9335097bfbae6da59e5f43e8`
- Configuration fingerprint: `17e0337939917fcfcb08ec764d88b43a7001e4c3c776c3ac8597390cb54ad9c9`
- Default simulation paths: 64
- Maximum simulation paths: 1,000
- Evaluated candidate count: 6
- Required compatible-market coverage: 100%
- Work budget: 1,000,000 candidate/path/pick units

All component weights, opponent roster-need behavior, positional-run adjustment, bench credit, candidate window, work cap, and coverage requirement are versioned assumptions. They are not learned or calibrated opponent behavior.

## Controlled fixture evidence

The Phase 6 fixture gates verify:

- snake order, turn picks, current/next user pick, duplicate prevention, undo, and replacement;
- replay equality, event/state hash tamper detection, idempotent commands, and stale-version rejection;
- frozen-pool persistence after a caller changes its local source objects;
- exact lineup assignment for overlapping FLEX/SUPERFLEX eligibility;
- seeded and input-order-independent rest-of-draft paths;
- bounded opponent roster-need and positional-run adjustments;
- deterministic outcomes for point-only projections;
- work-budget and incomplete-market rejection before expensive simulation;
- three distinct, recomputable balanced/safe-floor/high-upside recommendation roles;
- ruleset-sensitive replacement behavior between shallow and deeper WR/FLEX requirements;
- graceful unavailability when canonical market evidence or role uncertainty is insufficient;
- no championship-probability key or claim in recommendation output.

These controlled mapped fixtures prove that the engine path works. They do **not** prove that the current live production pool is recommendation-ready or calibrated.

## Current production readiness

- Canonical 2026 projection rows available to manual state: 1,367
- Draftable current QB/RB/WR/TE ADP rows in the coverage denominator: 203
- Archived PK/DEF rows outside the active ruleset and projection scope: 43
- Reviewed canonical ADP mappings: 0
- Market coverage: 0.0%
- Required coverage: 100.0%
- State status: `state_ready`
- Recommendation status: `identity_mapping_required`
- Monte Carlo status: `identity_mapping_required`
- Championship probabilities: `disabled`

The service never joins by display name. It therefore freezes a valid projection-only pool for manual drafting and withholds production recommendation/simulation output until reviewed mappings connect the compatible market rows to canonical projection IDs.

## Runnable commands

```powershell
fantasy-draft draft create --rules configs/example_ppr_12_team.yaml --draft-slot 1 --name "My draft" --simulations 64 --seed 42
fantasy-draft draft list
fantasy-draft draft show --session-id SESSION_ID
fantasy-draft draft pick --session-id SESSION_ID --player-id PLAYER_ID --expected-version VERSION
fantasy-draft draft undo --session-id SESSION_ID --expected-version VERSION
fantasy-draft draft replace --session-id SESSION_ID --overall-pick PICK --player-id PLAYER_ID --expected-version VERSION
fantasy-draft draft verify --session-id SESSION_ID
fantasy-draft draft recommend --session-id SESSION_ID
fantasy-draft app
```

The manual state commands are active. With current production data, `draft recommend` exits unavailable and explains the canonical mapping gate.

## Operator activation gate

```powershell
fantasy-draft data review-identities
fantasy-draft data apply-identity-overrides data\processed\identity\identity_review_queue.csv
fantasy-draft data review-identities
fantasy-draft data load-adp
fantasy-draft models build-adp-baselines --availability-config configs/adp_availability.yaml --output docs/PHASE_5_ADP_AVAILABILITY_EVALUATION.md
fantasy-draft data audit
fantasy-draft status
```

After the required compatible rows are reviewed and Phase 5 validates, create a new session so its frozen pool contains that reviewed market evidence. Existing state-only sessions intentionally remain unchanged.

## Quality-gate note

The following repository-level evidence has been recorded:

- strict mypy passed across 69 source files;
- the full pytest suite collected and passed 210 tests in 77.23 seconds;
- Streamlit AppTest completed with zero exceptions across `Project status`, `2026 projections`, `ADP availability`, `Draft room`, `Scoring sandbox`, and `Learning path`;
- `fantasy-draft data audit` passed with eight manifests and 12 verified immutable raw files; and
- before any user session is created, `draft_sessions`, `draft_session_players`, `draft_events`, and `draft_recommendation_runs` are initialized and correctly contain zero rows.

Ruff and the final one-command quality-gate wrapper also passed.

## Phase boundary

Phase 6 is complete as an engine and runnable manual draft room. Live recommendation and Monte Carlo activation is a data-readiness gate, not missing engine code. Phase 7 is next for Data Center, Model Lab, League Setup, multipage Draft Room, Post-Draft Report, export, and Learning Center polish. No championship probability is produced.
