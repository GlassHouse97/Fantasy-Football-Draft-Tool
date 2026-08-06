# Phase 8 League-History Evaluation

Implementation status: **PASSED**

Local publication gate: **PASSED**

Hosted CI: **PENDING — PR #8 OPEN AS DRAFT; NO WORKFLOW REGISTERED**

## Validated framework

Phase 8 completes the final phase in the master specification without fabricating a personal-history dataset or outcome model. It provides:

- a versioned, header-only `league-history-v1` package;
- archive-first intake with SHA-256 manifests;
- strict in-memory ZIP and package validation;
- transactional, idempotent canonical rules/picks/outcome loading;
- persistent rejected-package quality evidence with no canonical fact writes;
- exact/reviewed player identity mapping and historical review-queue reconciliation;
- versioned roster-construction and drafted-only descriptive reports;
- the `/league-history` Streamlit workspace; and
- an explicit, read-only outcome-model evidence gate with no training action.

## Import safety and integrity

Every selected file is archived before inspection. A canonical import requires a root-level ZIP with the exact declared contract. Validation rejects traversal, absolute or nested paths, case collisions, links, encryption, nested archives, undeclared files, excessive entries, expanded size, compression ratio, invalid privacy assertions, header/type/JSON errors, cross-file key conflicts, impossible snake-draft structure, and inconsistent outcomes.

The importer reads ZIP members in memory and does not extract them to disk. Fatal package errors preserve the raw archive and rejected quality report while rules, picks, and outcomes remain unchanged. Conflicting logical source facts roll back. Identical bytes and differently packaged but equivalent normalized content reuse existing canonical evidence rather than duplicating it.

## Identity boundary

Player names are retained only as review evidence. Canonical resolution uses the declared public platform namespace or the reviewed `player_source_mappings` registry. Platform IDs never fall through to the canonical-player namespace.

Unresolved picks retain null `player_id`, source ID, name, position, and confidence. The existing review workflow aggregates historical observations. Applying a verified mapping changes mapping fields only, recomputes league/package readiness and stored quality in the same transaction, and leaves draft facts and raw archives untouched. The data audit verifies reconciliation after the change.

## Descriptive boundary

`roster-construction-v1` describes positional allocation, draft capital, first position rounds, RB/WR counts at fixed round cutoffs, exact starter coverage, bench depth, and ruleset demand. Historical ADP/VORP/uncertainty/bye features remain unavailable without time-valid evidence.

`draft-only-v1` calculates optimal lineups made only from original picks under recorded rules. It requires complete reviewed mapping, supported positions, continuous regular-season source weeks, and evidence for every drafted player. Missing evidence creates a named blocked status and nullable metrics. A blocked rebuild also clears a stale formerly-ready outcome payload.

These outputs are associations and reconstructions, not causal strategy claims or manager-grade estimates.

## Outcome-model gate

The versioned gate requires analysis-ready leagues, team outcomes, roster-feature rows, points target evidence, five seasons, chronological validation/test coverage, 95% input/mapping coverage, and sufficient positive/negative playoff/champion labels. The nonlinear floor is higher and cannot bypass common completeness or split criteria.

Passing the counts would mean eligible for independent review only. Phase 8 does not train, approve, calibrate, publish, or serve a league-outcome model. It produces no playoff or championship probability.

## Current production evidence

The production warehouse currently contains:

| Evidence | Rows |
|---|---:|
| League-history packages | 0 |
| League-seasons | 0 |
| Historical draft picks | 0 |
| Team outcomes | 0 |
| Roster-construction features | 0 |
| Ready drafted-only metrics | 0 |

This is the expected truthful empty state. No personal history or synthetic production substitute is committed.

The additive warehouse migration preserves the Phase 6 persistence schemas and data. The production data audit passes with eight manifests and 12 verified immutable raw files.

## Quality evidence

Focused Phase 8 validation currently records:

- Ruff: **passed**;
- strict mypy: **passed**;
- integrated importer, identity, warehouse, descriptive, service, Data Center, and AppTest suite: **46 passed**; and
- CLI warehouse migration, empty descriptive build, data audit, and project status: **passed**.

The final local publication evidence is:

- repository-wide Ruff: **passed**;
- repository-wide strict mypy: **passed across 91 source files**;
- repository-wide pytest: **276 passed in 123.86 seconds**;
- Streamlit AppTest: **zero exceptions across the entry point and all eight pages**;
- CLI data audit: **passed across eight manifests and 12 verified immutable raw files**; and
- real browser QA: **passed** for the new navigation, League History empty state, exact 0/14 locked gate, absence of training controls, Data Center history template/ZIP controls, privacy warning, and live passed audit.

Local evidence is not presented as hosted GitHub Actions success.

Phase 8 commit `d593fe4` is pushed on `codex/phase-8-league-history`, and draft PR #8 targets `main`. At the publication check, GitHub Status reported an Actions major outage and the PR had no registered workflow. The PR remains unmerged until a hosted runner executes the quality gates successfully or a separate explicit outage decision is documented.

## Human handoff

The app is ready for a human usability pass without personal history. Use [the Human Testing Guide](HUMAN_TESTING_GUIDE.md). Personal history is optional and begins with [the League History Import Guide](LEAGUE_HISTORY_IMPORT_GUIDE.md) plus the Data Center template download.

There is no Phase 9 in the current master specification. Follow-up work should be driven by observed usability issues, reviewed ADP mappings, live draft rehearsals, and genuine history-package quality results.
