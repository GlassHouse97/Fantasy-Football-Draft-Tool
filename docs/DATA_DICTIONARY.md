# Data Dictionary

The DuckDB schema is created by `fantasy-draft data init-warehouse`. Types below are canonical targets; source adapters may expose additional fields in raw files.

## `players`

One row per internal player identity. For nflverse imports, the stable GSIS ID is also the internal `player_id`. Cross-platform IDs are nullable. `mapping_confidence` is `exact` for a consistent source-ID record, `high` for a stable-ID record with conflicting names, and `reviewed` when a human decision changes canonical identity metadata. Reviewed external-source confidence is stored on `player_source_mappings` rather than replacing an otherwise exact canonical GSIS identity. `mapping_source` includes either the nflverse manifest dataset ID or the immutable manual-review manifest ID so the evidence is traceable. `identity_source_dataset_id` and `identity_source_as_of` identify the player capture and acquisition time that supplied static feature evidence. `nfl_team`, experience, and active status describe the identity snapshot at acquisition time and must not be treated as historical features. `is_active` is true only for `ACT` players whose `last_season` reaches the configured prediction season, false for clearly historical or cut/released records, and null for ambiguous reserve, development, or suspension statuses.

| Canonical field | nflverse source |
|---|---|
| `player_id`, `gsis_id` | `gsis_id` |
| `pfr_id` | `pfr_id` |
| `espn_id` | `espn_id` |
| `display_name` | trimmed `display_name` |
| `canonical_position` | uppercase `position` |
| `nfl_team` | uppercase `latest_team` |
| `birth_date` | safely parsed `birth_date` |
| `experience` | `years_of_experience` |
| `rookie_season`, draft fields | `rookie_season`, `draft_year`, `draft_round`, `draft_pick`, `draft_team` |
| physical profile | parsed height and weight fields where available; weight remains identity-only until historical time semantics exist |
| `identity_source_dataset_id` | nflverse player manifest dataset ID |
| `identity_source_as_of` | nflverse player manifest acquisition timestamp; gates static-position fallback against the row cutoff |
| platform IDs | source value on insert; every existing non-null curated value wins on refresh |

## `player_source_mappings`

One durable, human-reviewed mapping per `(source, source_player_id)`. This registry is consulted before generating name-derived candidates, so approved decisions remain deterministic across queue refreshes and source reloads.

| Field | Meaning |
|---|---|
| `source`, `source_player_id` | Source-side identity and composite primary key |
| `player_id` | Approved canonical player |
| `mapping_confidence` | `reviewed` for a human decision |
| `mapping_source` | Manual-review provenance containing the override manifest ID |
| `review_id` | Queue record that the decision resolved |
| `reviewed_at`, `reviewer`, `notes` | Human review evidence |
| `source_dataset_id` | Immutable override manifest dataset ID |

## `identity_review_queue`

One auditable record per logical source observation. `review_id` is deterministic from issue type, source, and source player ID. A refresh updates `last_seen_at` and current evidence without overwriting a final human resolution; observations absent from the refreshed source are retained with `is_current = false`.

| Field group | Meaning |
|---|---|
| Source evidence | `source`, `source_player_id`, display name, position, team, `evidence_json`, dataset ID |
| Proposed match | Candidate player ID/name/context, reason, and confidence |
| Queue lifecycle | `pending`, `resolved`, `dismissed`, or `excluded`; `is_current` distinguishes current evidence |
| Human resolution | `confirmed`, `remapped`, or `dismissed`, plus resolved player, optional canonical-name override, reviewer, timestamp, note, and override dataset ID |

Exact platform-ID matches and previously reviewed registry mappings may be resolved without a new name decision. A match inferred from name, suffix, position, or team is only a candidate and remains `pending` until human approval. FFC `DEF`, `DST`, and `D/ST` observations normalize to `DEF` and are `excluded`; they are never forced into the player dimension.

## `player_week_stats`

One row per player, season, and week with historical position, passing, rushing, receiving, kicking, turnover, and opportunity components. `season_type` and `game_id` preserve regular/postseason and game context. `source`, `as_of`, and `source_dataset_id` preserve provenance. `games_played` and `games_active` remain null because the weekly stats capture does not directly establish either indicator; Phase 3 participation comes from snap counts instead.

Most stat names map directly. Important renamed or derived fields are:

| Canonical field | nflverse source |
|---|---|
| `position` | historical weekly `position` |
| `passing_attempts` | `attempts` |
| `interceptions` | `passing_interceptions` |
| `two_point_conversions` | passing + rushing + receiving two-point conversions |
| `fumbles_lost` | `fumbles_lost_total` |
| `field_goals_made`, `field_goals_attempted` | `fg_made`, `fg_att` |
| `extra_points_made`, `extra_points_attempted` | `pat_made`, `pat_att` |
| `as_of` | manifest acquisition timestamp |

Rows without player IDs are never assigned invented identities. Zero-stat placeholders are counted, reported, and excluded. A non-null weekly player ID absent from `players` is fatal and prevents the transaction from committing.

## `player_game_participation`

One row per mapped player and game from immutable PFR snap counts distributed by nflverse. `pfr_player_id` maps through `players.pfr_id`; `player_id` remains the canonical GSIS-oriented identity. `position`, team, and opponent are historical game context. `source`, `as_of`, and `source_dataset_id` retain capture provenance.

| Field group | Fields and meaning |
|---|---|
| Logical key | `game_id`, `player_id`, and source |
| Source identity | `pfr_game_id`, `pfr_player_id` |
| Historical context | season, week, game/season type, position, team, opponent |
| Participation | offense, defense, and special-teams snaps plus source percentages |
| Provenance | source `nflverse_pfr_snap_counts`, archive timestamp, dataset ID |

An active game is counted only when `offense_snaps + defense_snaps + special_teams_snaps > 0`. A new complete capture replaces only nflverse rows in its manifest season scope; other seasons and sources remain untouched. Postseason records are stored but excluded from regular-season feature aggregation.

## `player_season_features`

One row per player and prediction season, with unique logical key `(player_id, prediction_season)`. `feature_season = prediction_season - 1`. `cutoff_date` and `feature_available_at` are September 1 of the prediction season: a logical preseason cutoff, not the later local acquisition date. `source_max_as_of` separately records the newest 2026 archive timestamp used by the row.

`feature_payload` contains cutoff-safe lag-one and weighted three-year production, component rates, prior position means, rookie/sparse-history fallbacks, age, height, static draft fields, team-change context, transparent baseline inputs, candidate-selection evidence, and missingness flags. The candidate proxy uses four prior seasons plus current/prior rookie cohorts, while only three seasons enter weighted production. Historical weekly/participation position takes precedence. Static identity position is allowed only when `identity_source_as_of` is no later than the preseason cutoff; current team, weight, experience, and active status are excluded. `target_payload` is retained only as a nullable compatibility column and is not populated by the Phase 3 builder.

`feature_version`, scoring ruleset fingerprint, source dataset IDs, maximum contributing stat season, source timestamp, and data fingerprint make each build auditable. The validated set contains 11,171 rows, including 1,367 live 2026 rows without known outcomes. Of these, 309 use a cutoff-safe static identity position. Another 2,710 current-core historical entry-cohort candidates lacked a cutoff-safe position and were excluded rather than inheriting the current snapshot. That exclusion prevents later position conversions from leaking backward, but historical rookie baseline performance remains unavailable until a historical preseason-position archive exists.

## `player_season_targets`

One separately persisted outcome row per player and historical prediction season. `target_payload` contains next-season `fantasy_points_per_game`, `games_active`, and `fantasy_points_total`. The target table carries its own version, ruleset fingerprint, source dataset IDs, maximum archive timestamp, feature-data fingerprint, and target-only fingerprint. A nonzero-stat game without mapped positive-snap evidence makes that player-season's participation-dependent outcomes null instead of creating a partial denominator.

The validated set contains 9,804 rows. Fifteen player-seasons have a nonzero-stat game without complete mapped snap participation; 28 target rows therefore retain total points while participation-dependent games-active and points-per-game values are null. Targets never enter the feature payload.

## `feature_build_metadata`

One active record binds the feature-only fingerprint, target-only fingerprint, combined build fingerprint, feature version, prediction-season range, row counts, ruleset, source dataset IDs, maximum acquisition timestamp, and full quality payload. Target-only changes preserve feature identity but change the combined build and invalidate downstream baseline outputs.

## `baseline_predictions`

One row per player, prediction season, target, and transparent baseline. It stores predicted value, nullable actual value, position, experience group, baseline version, feature fingerprint, target fingerprint, combined build fingerprint, and scoring-ruleset fingerprint. The five baselines are previous season, weighted history, age/position adjusted, position shrinkage, and weighted components.

## `baseline_evaluation_metadata`

One active record per combined feature/target build. It binds the report and baseline versions to feature, target, build, and scoring fingerprints plus prediction/evaluated row counts, chronological folds, upstream quality warnings, candidate outcome counts, metrics, limitations, and unavailable comparisons. Metrics include the all-candidate attrition view and separately labeled positive-game diagnostics. These records describe transparent heuristics, not a trained ML model.

The validated Phase 3 build uses feature fingerprint `d2bdda170fcbf88ccfe0b3f437615583a0684057eebe1fc12aa65463a47cf9cf`, target fingerprint `dd759bbf87c146884e68425079b3a759d1d6d4bb434d5bccee6d9d91c98c56a9`, and combined build fingerprint `f195dcb17a1a386b2f2003d87a06921550235cbec62aecd0f4eda419aa664cd7`.

## `player_projection_runs`

The single authoritative Phase 4 run header. It binds the deterministic `run_id` to the frozen Phase 3 feature, target, build, scoring, and baseline-report fingerprints; model-feature and model-configuration fingerprints; chronological split definitions; persisted row counts; training timestamp; run status; and the registered publication payload, including the unique immutable-attempt `publication_id`. The six Phase 4 tables are staged as `validating`, audited, and promoted to `complete` inside one transaction; failure rolls back to the prior complete publication.

The active run is `phase4-7ae8e9aed04bffca00c0`, with run fingerprint `7ae8e9aed04bffca00c04d05e623f8afd20877dcfa09ddf43a8c1a7e8c34db03`. Its Phase 3 fingerprints are unchanged from the validated baseline build.

## `player_projection_models`

One registered final estimator per `(run_id, model_family, target_name, position)`. Fields record chronological training seasons and row count, feature/categorical-feature names, selected hyperparameters, uncertainty method, package versions, and project-relative artifact/model-card paths with SHA-256 hashes and artifact byte size.

The validated run registers 24 models: Ridge and histogram gradient boosting for four core positions and three targets. Registration does not make every model a champion; all final candidates remain auditable.

## `player_projection_predictions`

One candidate prediction per run, player, prediction season, target, and model family. `prediction_scope` distinguishes validation, test, and live rows; `fold_label` and `training_max_season` enforce chronology. `predicted_value` equals the residual-adjusted `p50`, while `p10` and `p90` carry empirical signed-residual bounds. Historical rows may have nullable actual values; live rows must not have actuals. Seven lineage fingerprints bind every row to its exact upstream data, rules, baselines, selected model feature set, and model configuration.

The validated run stores 45,588 rows: 32,024 have evaluable historical actuals and 6,804 are live learned-candidate predictions. Learned intervals use earlier out-of-fold training residuals only.

## `player_projection_champions`

One decision per `(run_id, target_name, position)`, for 12 total routes. It records whether the selected source is `learned` or `baseline`, the selected model/baseline name, validation metric and value, reference baseline, improvement, and a payload containing the bootstrap decision evidence. The 2025 test does not participate in selection.

Across 84 validation candidates, learned models won 9 routes: all total-points and games-active routes plus histogram gradient boosting for WR points per game. QB, RB, and TE points per game retain the `age_position_adjusted` baseline. A learned win requires lower pooled 2020-2024 MAE and a learned-minus-baseline 95% confidence-interval upper bound below zero.

## `player_projection_evaluation_metadata`

Exactly one evaluation record belongs to the active run. It binds the report fingerprint and all upstream/model fingerprints to prediction, evaluated, live, candidate, and champion row counts plus the complete report payload. It is the warehouse-side bridge between the authoritative attempt-scoped report and the selected board.

## `player_projection_board`

One served row per `(run_id, player_id, prediction_season)`. Each of the three targets stores P10/P50/P90, selected source, and selected name. `prediction_status` distinguishes learned, retained-baseline, and rookie-fallback behavior; `explanation_payload` contains target-level model factors or transparent fallback reasoning. The row repeats all lineage fingerprints, including the evaluation-report fingerprint, so the app cannot mix publications.

The validated 2026 board has 1,367 rows. Learned selections use training-only residual intervals evaluated by season, position, and projection tier. Every baseline selection is point-only with `P10=P50=P90`. The same point-only rule applies to 233 rookie fallbacks—QB 21, RB 46, WR 114, and TE 52—because no valid historical preseason rookie-position cohort exists.

## Phase 4 publication authority

DuckDB and the registered attempt-scoped hashes are authoritative. Generated evaluation/registry files under `models/reports/<run_id>/<publication_id>/`, serialized artifacts, model cards, and diagnostic plots must remain project-relative and match their registered SHA-256 metadata. A deterministic `run_id` can therefore be retrained safely without overwriting an earlier attempt. `docs/PHASE_4_MODEL_EVALUATION.*` and `models/registry.json` are convenience mirrors, not independent sources of truth. Audit, status, and the app require exactly one complete current run, reconciled table counts and lineage, full live-board coverage, valid chronology/intervals, and matching registered files.

## `adp_snapshots`

One source observation per `(snapshot_id, raw_source_row_id)`. The row preserves source, capture time, season, scoring format, team count, display context, average/median/rank/min/max picks, sample size, source movement, source standard deviation, and the source movement horizon. `player_id` is nullable; `mapping_confidence` records whether canonical identity evidence exists. Unresolved rows remain source-keyed and are never joined by display name.

## `adp_snapshot_metadata`

One row per immutable production snapshot. The stable `snapshot_id` binds source, capture time, season, scoring format, team count, position scope, and raw SHA-256 evidence. `raw_relative_path` remains project-relative, `source_dataset_ids` records every manifest collapsed into the snapshot, `row_count` reconciles canonical observations, and `loaded_at` records warehouse normalization time. Repeating the same raw capture preserves this row and its observation count.

## `adp_movement_features`

One cutoff-safe feature row per source observation. `entity_key` uses a canonical player ID only when mapping evidence exists and otherwise retains the stable source identity. Fields include current and prior ADP, prior snapshot/time, elapsed days, 1/3/7/14-day change, velocity, acceleration, 14-day rolling volatility, cross-source spread, and source/identity observation counts. `feature_version` and `data_fingerprint` bind the calculation contract. A feature row uses no observation after its own `captured_at` cutoff.

## `adp_movement_forecasts`

Three one-day baseline rows per source observation: `persistence`, `linear_trend`, and `exponentially_weighted_trend`. `predicted_average_pick` and `predicted_change` are nullable when the method lacks enough history; `status`, `reason`, and `history_count` make that boundary explicit. Persistence requires one observation. The two trend methods require at least three dated observations for the same source player. The validated one-snapshot build therefore contains 738 rows: 246 ready persistence forecasts and zero ready linear or exponentially weighted forecasts.

## `adp_availability_parameters`

One distribution parameter row per source observation. `average_pick` is the location and `scale` is selected from source standard deviation, then min/max-derived spread, then a versioned configured fallback. `evidence_method`, `fallback_group`, source sample/range fields, and `mapping_confidence` keep the estimate explainable. The app conditions the pick distribution on the player still being available at the current pick. The validated build has 246 rows, all using source standard deviation and none using configured fallback.

## `adp_phase5_builds`

One deterministic logical build record per `build_fingerprint`. It binds the snapshot-data fingerprint and availability-configuration fingerprint to snapshot, observation, feature, forecast, parameter, and ready-method counts. `calibration_status`, `supervised_status`, and `report_payload` preserve honest capability boundaries. The validated build fingerprint is `3446513dfe4b122079ba1ed89b6517821d35cac48821ff1631e25a77f6dd3b6b`; its snapshot fingerprint is `44624854b5c45f80fb0017e6ecdb52c972d4389236d35131b2dbfccb9a0447f2`.

## `league_rules`

One row per imported league-season configuration. `normalized_ruleset_json` is key-sorted canonical JSON; `ruleset_fingerprint` is its SHA-256 digest. A live Phase 6 session also freezes its exact rules JSON and full/scoring-only fingerprints in `draft_sessions`, so replay does not depend on a later configuration edit.

## `draft_picks`

One row per materialized imported or completed-draft pick. Team identifiers are pseudonymous. The ADP snapshot is nullable when it is unknown. This table is not the Phase 6 live-state authority because it cannot retain undo and replacement history; `draft_events` is authoritative for an active local session.

## `draft_sessions`

One row per local event-sourced session. It stores the session label/status, canonical rules JSON, full rules and scoring-only fingerprints, team count, rounds, user slot, frozen Phase 4 run ID, optional Phase 5 build fingerprint, player-pool and engine-config fingerprints, pool/mapped-market counts, recommendation readiness and message, random seed, simulation count, current event version, current state fingerprint, and timestamps.

The recommendation status may truthfully be `identity_mapping_required` while the manual state engine remains usable. The current production preparation freezes 1,367 canonical projections but has 0 mapped market rows from 203 draftable QB/RB/WR/TE ADP observations. Another 43 PK/DEF observations remain archived and auditable outside the active ruleset's coverage denominator.

## `draft_session_players`

One immutable player row per `(session_id, player_id)`. The row freezes canonical display/position, total-points P10/P50/P90, prediction status/source/method, and nullable reviewed market source, snapshot, capture time, ADP location, availability scale/evidence, and mapping confidence. `player_payload` is the canonical replay representation. The session pool fingerprint covers every frozen field in canonical player-ID order.

Market evidence joins only through reviewed canonical `player_id`. A name match is never accepted. Duplicate canonical market mappings, mapped players absent from the projection board, position conflicts, incompatible season/team/scoring scopes, and insufficient mapping coverage all prevent recommendation readiness.

## `draft_events`

Append-only events keyed by `(session_id, sequence)`. Each event has a unique event ID and idempotent command ID, event type, timestamp, canonical JSON payload, prior-state fingerprint, and resulting-state fingerprint. Supported Phase 6 events are session start, pick, undo latest pick, and replace an active pick. Stored events are never deleted or rewritten during normal operation.

Replay derives snake ownership, current pick, every roster, availability, history, and completion from this stream. It rejects sequence gaps, stale fingerprint links, duplicate players, incorrect team ownership, illegal roster capacity, and inconsistent session metadata.

## `draft_recommendation_runs`

One persisted result per deterministic recommendation attempt. It binds the session/event version and state fingerprint to the engine-config fingerprint, random seed, simulation count, availability status, result fingerprint, canonical result payload, and creation time. Candidate roles and their raw/normalized components, simulation summaries, explanations, risks, limitations, and upstream evidence live inside the hashed result payload.

The table does not imply production readiness. Controlled fixtures prove the engine, while current live recommendations remain unavailable until all required compatible ADP rows have reviewed canonical mappings. No championship-probability field is produced.

## `team_outcomes`

One row per pseudonymous team and season. Outcome fields remain nullable when the uploaded history does not contain them. No championship probability is inferred from this table until a later training gate is satisfied.
