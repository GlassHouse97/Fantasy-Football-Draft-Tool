# Data Dictionary

The DuckDB schema is created by `fantasy-draft data init-warehouse`. Types below are canonical targets; source adapters may expose additional fields in raw files.

## `players`

One row per internal player identity. For nflverse imports, the stable GSIS ID is also the internal `player_id`. Cross-platform IDs are nullable. `mapping_confidence` is `exact` for a consistent GSIS-linked record and `high` when the GSIS ID matches but weekly and identity display names conflict. `mapping_source` includes the manifest dataset ID so the evidence is traceable. `nfl_team`, experience, and active status describe the identity snapshot at acquisition time and must not be treated as historical features. `is_active` is true only for `ACT` players whose `last_season` reaches the configured prediction season, false for clearly historical or cut/released records, and null for ambiguous reserve, development, or suspension statuses.

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

One row per player and feature season. `cutoff_date` proves when the features were considered available. Future targets are stored separately from feature selection logic.

## `adp_snapshots`

One row per player within a timestamped source snapshot and league configuration. `raw_source_row_id` makes normalization auditable.

## `league_rules`

One row per league-season configuration. `normalized_ruleset_json` is key-sorted canonical JSON; `ruleset_fingerprint` is its SHA-256 digest.

## `draft_picks`

One row per overall pick. Team identifiers are pseudonymous. The ADP snapshot is nullable when it is unknown.

## `team_outcomes`

One row per pseudonymous team and season. Outcome fields remain nullable when the uploaded history does not contain them. No championship probability is inferred from this table until a later training gate is satisfied.
