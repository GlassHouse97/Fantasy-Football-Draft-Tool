# Implementation Checklist

## Phase 0 — inspect and plan

- [x] Inspect the empty project directory and requested remote repository.
- [x] Record local Python, Git, GitHub CLI, R, Quarto, and dependency-manager availability.
- [x] Confirm current official nflreadpy, FFC ADP, and Sleeper interfaces.
- [x] Define architecture, assumptions, packaging, linting, typing, and tests.

## Phase 1 — project and data foundation

- [x] Scaffold the package, CLI, configuration, data layout, documentation, and UI shell.
- [x] Implement immutable raw archives, SHA-256 hashing, and source manifests.
- [x] Create the DuckDB warehouse and canonical empty tables.
- [x] Create required and optional manual import templates.
- [x] Implement nflverse player and weekly-stat downloads with offline reuse.
- [x] Implement timestamped FFC ADP snapshots and normalization.
- [x] Implement validated manual ESPN ADP archiving.
- [x] Add small labeled fixtures and deterministic tests.
- [ ] Add optional Sleeper league import.
- [ ] Add league-history package import.

## Phase 2 — scoring, rules, and identity

- [x] Implement deterministic normalized rules and SHA-256 fingerprints.
- [x] Implement configurable component-based scoring.
- [x] Implement explicit FLEX and SUPERFLEX slot eligibility.
- [x] Implement starter-demand estimates and two replacement definitions.
- [x] Add a plain-English learning chapter and executable notebook.
- [x] Define identity records with mapping confidence and conflict rules.
- [ ] Build a review queue that resolves real source rows across platforms.

## Future phases

- [ ] Phase 3: cutoff-safe player-season features and transparent baselines.
- [ ] Phase 4: regularized linear and boosted models, uncertainty, explanations, and model cards.
- [ ] Phase 5: ADP movement archive and next-pick availability.
- [ ] Phase 6: event-sourced snake draft and Monte Carlo optimization.
- [ ] Phase 7: full multipage Streamlit workflow.
- [ ] Phase 8: descriptive league-history analysis and gated outcome modeling.
