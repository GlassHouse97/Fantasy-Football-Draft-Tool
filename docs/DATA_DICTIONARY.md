# Data Dictionary

The DuckDB schema is created by `fantasy-draft data init-warehouse`. Types below are canonical targets; source adapters may expose additional fields in raw files.

## `players`

One row per internal player identity. Cross-platform IDs are nullable. `mapping_confidence` is one of `exact`, `high`, `medium`, `low`, or `unresolved`; `mapping_source` explains the evidence.

## `player_week_stats`

One row per player, season, and week with passing, rushing, receiving, turnover, and opportunity components. `source` and `as_of` preserve provenance.

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
