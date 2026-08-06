# Local data layout

- `raw/`: immutable downloads and manual uploads, including nflverse weekly/player data, nflverse/PFR snap counts, and reviewed identity worksheets under `raw/identity_overrides/`. Ignored by Git except placeholders.
- `interim/`: temporary reproducible transforms.
- `processed/`: reproducible derived files, including the editable identity-review worksheet under `processed/identity/`.
- `warehouse/`: the local DuckDB database, including identity, participation, feature, target, baseline-evaluation, and Phase 4 model-publication tables.
- `sample/`: small, public, clearly labeled demonstration data.
- `templates/`: versioned headers and examples for manual data.

Raw files are never overwritten. Each capture receives a timestamped filename and a SHA-256 source manifest under `data/raw/manifests/` at runtime. Reapplying identical identity-review content reuses its existing immutable archive and manifest.

`fantasy-draft data review-identities` refreshes `identity_review_queue` from verified source evidence and exports a working CSV. Name-derived matches remain candidates only. `fantasy-draft data apply-identity-overrides PATH` validates decided rows, archives the submitted file unchanged, and writes the final decision plus its provenance to DuckDB in one transaction. `player_source_mappings` is the durable registry used on future refreshes; the editable CSV is not an automatic source of truth. FFC team-defense rows are retained as excluded queue evidence and never mapped into `players`.

## Phase 3 participation and feature data

`fantasy-draft data download-nflverse-snap-counts` archives Pro Football Reference game-level snap counts distributed by nflverse as timestamped Parquet plus a SHA-256 manifest. `fantasy-draft data load-nflverse-participation` verifies that immutable capture, maps PFR player IDs to canonical player IDs, and transactionally replaces nflverse rows for the manifest's complete season scope. Other seasons and sources are preserved, replacement deletions are reported, and repeating the same manifest is idempotent.

An active game means:

```text
offense_snaps + defense_snaps + special_teams_snaps > 0
```

Roster status and the presence of a weekly stat row are not substituted for participation. If a game with nonzero stats or opportunities lacks mapped positive-snap evidence, that player-season's active-game denominator and points per game remain null. Historical position and team come from weekly statistics or snap-count evidence. Static player facts such as birth date and draft capital retain their identity-source dataset ID and acquisition timestamp; current team, current weight, current experience, and current active status are not historical features.

`fantasy-draft features build-player-seasons` uses regular-season data only and writes:

- `player_season_features`: one cutoff-safe feature row for season `t` predicting `t+1`;
- `player_season_targets`: separately persisted future outcomes;
- `feature_build_metadata`: feature version, ruleset, source datasets, separate feature/target fingerprints, their combined build fingerprint, and the quality report.

September 1 of the prediction season is the logical preseason cutoff. The 2026 archive acquisition time is retained separately as provenance and is not presented as the historical availability date. Generated feature quality is written to `processed/features/player_season_features_quality.json`.

The validated build contains 11,171 features, 9,804 targets, and 1,367 live 2026 rows. Fifteen player-seasons have an incomplete mapped participation denominator, and 28 target rows therefore retain total points while leaving games active and points per game null. Reproducibility is bound by feature fingerprint `d2bdda170fcbf88ccfe0b3f437615583a0684057eebe1fc12aa65463a47cf9cf`, target fingerprint `dd759bbf87c146884e68425079b3a759d1d6d4bb434d5bccee6d9d91c98c56a9`, and combined build fingerprint `f195dcb17a1a386b2f2003d87a06921550235cbec62aecd0f4eda419aa664cd7`.

The cutoff-safe candidate proxy includes players with evidence in the prior four seasons plus the current and prior rookie cohorts. Only three seasons enter weighted production; fourth-year evidence affects candidate inclusion and remains in row lineage. Completed-season scorers outside this proxy are reported without using their outcomes to select candidates: 1,117 scorers and 1,390 active players in the validated historical build.

Historical entry-cohort rows require a weekly or participation position known before the cutoff. The current nflverse identity snapshot is not backfilled into those seasons, so 2,710 current-core historical candidate rows without cutoff-safe position evidence are excluded and reported. The August 2026 identity snapshot does predate the September 1, 2026 cutoff and safely supplies position for 309 live rows. Until a historical preseason-position archive is added, historical rookie model performance cannot be measured honestly.

`baseline_predictions` contains deterministic heuristic outputs, not a trained ML model. `baseline_evaluation_metadata` records the expanding-fold report and combined build fingerprint. A changed feature or target fingerprint invalidates dependent baseline rows until evaluation is rerun.

## Phase 4 model data and publication

`fantasy-draft models train-player-models` reads the frozen Phase 3 feature, target, baseline, scoring, and fold contract. It trains Ridge and histogram gradient-boosting candidates for four positions and three targets, writes chronological validation/test/live predictions, selects one champion per route using validation only, and builds the live board. The validated run contains:

- 24 registered models: two families across QB/RB/WR/TE and three targets;
- 45,588 prediction rows, including 32,024 evaluable and 6,804 live learned-candidate predictions;
- 84 validation selection candidates and 12 champion decisions;
- 1,367 live 2026 board rows;
- 233 point-only rookie fallbacks: QB 21, RB 46, WR 114, and TE 52.

Run `phase4-7ae8e9aed04bffca00c0` is bound to fingerprint `7ae8e9aed04bffca00c04d05e623f8afd20877dcfa09ddf43a8c1a7e8c34db03` and the unchanged Phase 3 fingerprints. Pooled 2020-2024 validation MAE and a paired-bootstrap gate select champions; the 2025 test is report-only. Learned models won 9 of 12 routes: all total-points and games-active routes plus histogram gradient boosting for WR points per game. QB, RB, and TE points per game retain `age_position_adjusted`.

Learned intervals are P10/P50/P90 signed-residual ranges calibrated only from earlier out-of-fold training predictions and evaluated by season, position, and tier. Transparent-baseline selections and rookie fallbacks remain point-only with `P10=P50=P90`; the project does not imply calibrated uncertainty where none was validated.

The six `player_projection_*` tables hold the active run, model registrations, candidate predictions, champion decisions, evaluation metadata, and live board. The deterministic `run_id` identifies the model/data contract; a unique `publication_id` identifies each immutable training attempt. DuckDB plus registered hashes are authoritative for `models/reports/<run_id>/<publication_id>/`, serialized artifacts, model cards, and diagnostic plots. All six tables are staged, audited, and promoted to `complete` in one DuckDB transaction; an integrity or promotion failure rolls back without displacing the prior complete publication. `docs/PHASE_4_MODEL_EVALUATION.*` and `models/registry.json` are reproducible convenience mirrors refreshed after commit. A changed Phase 3 build or baseline contract invalidates the learned publication.
