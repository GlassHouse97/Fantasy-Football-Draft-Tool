# Data Dictionary

The DuckDB schema is created by `fantasy-draft data init-warehouse`. Types below are canonical targets; source adapters may expose additional fields in raw files.

## `players`

One row per internal player identity. For nflverse imports, the stable GSIS ID is also the internal `player_id`. Cross-platform IDs are nullable. `mapping_confidence` is `exact` for a consistent source-ID record, `high` for a stable-ID record with conflicting names, and `reviewed` when a human decision changes canonical identity metadata. Reviewed external-source confidence is stored on `player_source_mappings` rather than replacing an otherwise exact canonical GSIS identity. `mapping_source` includes either the nflverse manifest dataset ID or the immutable manual-review manifest ID so the evidence is traceable. `nfl_team`, experience, and active status describe the identity snapshot at acquisition time and must not be treated as historical features. `is_active` is true only for `ACT` players whose `last_season` reaches the configured prediction season, false for clearly historical or cut/released records, and null for ambiguous reserve, development, or suspension statuses.

| Canonical field | nflverse source |
|---|---|
| `player_id`, `gsis_id` | `gsis_id` |
| `espn_id` | `espn_id` |
| `display_name` | trimmed `display_name` |
| `canonical_position` | uppercase `position` |
| `nfl_team` | uppercase `latest_team` |
| `birth_date` | safely parsed `birth_date` |
| `experience` | `years_of_experience` |
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

One row per player, season, and week with passing, rushing, receiving, kicking, turnover, and opportunity components. `season_type` and `game_id` preserve regular/postseason and game context. `source`, `as_of`, and `source_dataset_id` preserve provenance. `games_played` and `games_active` remain null because the weekly stats capture does not directly establish either indicator.

Most stat names map directly. Important renamed or derived fields are:

| Canonical field | nflverse source |
|---|---|
| `passing_attempts` | `attempts` |
| `interceptions` | `passing_interceptions` |
| `two_point_conversions` | passing + rushing + receiving two-point conversions |
| `fumbles_lost` | `fumbles_lost_total` |
| `field_goals_made`, `field_goals_attempted` | `fg_made`, `fg_att` |
| `extra_points_made`, `extra_points_attempted` | `pat_made`, `pat_att` |
| `as_of` | manifest acquisition timestamp |

Rows without player IDs are never assigned invented identities. Zero-stat placeholders are counted, reported, and excluded. A non-null weekly player ID absent from `players` is fatal and prevents the transaction from committing.

## `player_season_features`

One row per player and feature season. `cutoff_date` proves when the features were considered available. Future targets are stored separately from feature selection logic. This table is a Phase 3 target and must not be used for model training until its regular-season rules, provenance, row accounting, and leakage tests are validated.

## `adp_snapshots`

One row per player within a timestamped source snapshot and league configuration. `raw_source_row_id` makes normalization auditable.

## `league_rules`

One row per league-season configuration. `normalized_ruleset_json` is key-sorted canonical JSON; `ruleset_fingerprint` is its SHA-256 digest.

## `draft_picks`

One row per overall pick. Team identifiers are pseudonymous. The ADP snapshot is nullable when it is unknown.

## `team_outcomes`

One row per pseudonymous team and season. Outcome fields remain nullable when the uploaded history does not contain them. No championship probability is inferred from this table until a later training gate is satisfied.
