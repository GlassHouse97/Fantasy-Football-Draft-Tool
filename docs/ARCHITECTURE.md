# Architecture

## Purpose

Fantasy Football Draft AI is a local, single-user system. It separates football projection, uncertainty, market timing, and roster optimization so each question can be tested independently.

```text
documented source or manual upload
    -> immutable timestamped raw file + SHA-256 manifest
    -> validation and identity resolution
    -> canonical DuckDB tables
    -> time-safe features and model artifacts
    -> ruleset-specific scoring and replacement value
    -> availability estimates and rest-of-draft simulation
    -> explained recommendation
```

## Layer boundaries

| Layer | Responsibility | Must not do |
|---|---|---|
| `data` | Acquire, archive, hash, validate, and load source data | Rank players or hide quality failures |
| `schemas` | Define stable canonical records and reports | Make network requests |
| `scoring` | Convert projected stat components into points | Predict the stat components |
| `rules` | Normalize league configuration, eligibility, demand, and replacement levels | Depend on Streamlit |
| `features` / `models` | Build cutoff-safe features and evaluated predictions | Use future information |
| `draft` / `simulation` | Replay draft events and compare possible futures | Invent learned probabilities |
| `services` | Orchestrate reusable application workflows | Contain UI rendering |
| `ui` / `app.py` | Present status, inputs, and outputs | Train models or encode business rules |

## Local storage

- `data/raw/` contains immutable source captures and manifests.
- `data/processed/` contains reproducible derived Parquet files.
- `data/warehouse/fantasy_football.duckdb` is the local analytical warehouse.
- `models/artifacts/` and `models/reports/` contain generated model outputs.
- Generated data and models are ignored by Git; templates and test fixtures are not.

The warehouse uses explicit canonical tables even before every importer exists. This prevents early source-specific column names from becoming the application contract.

## nflverse warehouse loading

An nflverse load always selects the player and weekly-stat files from one source manifest. It never combines independently selected "latest" files. Before normalization, both raw files must exist inside the project and match their recorded SHA-256 hashes.

The player dimension uses GSIS IDs as internal IDs and never joins on display name. Weekly rows with no player ID are reported and excluded only when every mapped production field is zero; non-null IDs missing from the player capture and identifier-free rows with production are fatal. The loader stages both normalized tables, merges identity data without erasing later manual platform IDs or review metadata, key-upserts nflverse weekly rows, runs post-load invariants, and commits one DuckDB transaction. It never deletes keys absent from a capture because the current manifest does not prove that a file is a complete season replacement. Repeating the same manifest produces the same canonical rows and counts.

The nflverse player capture is a current global identity snapshot, not a table limited to the requested stat seasons. Historical feature code must use weekly team context and explicit cutoffs rather than treating current identity attributes as historical facts.

## Player identity review and overrides

`fantasy-draft data review-identities` reads the latest verified nflverse, FFC, and manual ESPN captures and compares their source identities with canonical `players`. Each logical observation receives a deterministic `review_id` based on its issue type, source, and source player ID. Refreshing the same evidence updates that queue record instead of manufacturing another review. Records that disappear from the latest source evidence remain available for audit with `is_current = false`.

The queue separates evidence from decisions:

- `identity_review_queue` stores source evidence, a proposed canonical candidate, confidence, current status, and any human resolution.
- `player_source_mappings` is the durable registry of reviewed `(source, source_player_id) -> player_id` decisions, including reviewer, timestamp, notes, and manifest provenance.
- the exported CSV under `data/processed/identity/` is an editable working copy, not an authoritative automatic mapping.

Stable source IDs are authoritative evidence when they already agree with the canonical registry. Normalized name, suffix, position, and team comparisons can produce `high`, `medium`, or `low` candidates, but every name-derived candidate remains `pending` until a human confirms or remaps it. Display name alone is never a join key. Ambiguous or missing candidates remain unresolved. FFC team-defense observations normalized to `DEF` are marked `excluded` because the canonical player dimension models people, not defense units.

`fantasy-draft data apply-identity-overrides PATH` accepts only decisions tied to an existing review ID. It validates source evidence, canonical targets, timestamps, reviewers, collisions, and resolution rules before archiving the submitted CSV unchanged. Approved decisions update the queue, mapping registry, and relevant canonical identity fields in one DuckDB transaction. Any failure rolls back the entire operation. Identical decisions are matched as no-ops, conflicting final decisions are rejected, and a stable nflverse GSIS ID cannot be remapped by name. The nflverse loader reapplies reviewed identity evidence after source refreshes so a later load cannot silently erase a human decision.

Phase 2 ends at this validated identity boundary. Phase 3 may build cutoff-safe player-season features, but model training remains disabled until feature row accounting, regular-season semantics, provenance, and leakage tests pass.

## Interfaces chosen in Phase 0

- Python 3.11 is the canonical runtime.
- `pyproject.toml` and a local `.venv` provide reproducible packaging.
- `nflreadpy` is the documented nflverse adapter and returns Polars dataframes.
- Pandas remains the approachable canonical tabular API inside this project.
- DuckDB is the embedded warehouse.
- Pydantic validates configuration and rules.
- Typer provides the CLI.
- Streamlit provides the first replaceable UI shell.

## Security and privacy

No ESPN scraping, authentication automation, cookies, or undocumented endpoints are used. Sleeper support will use only its documented read-only league interfaces. Personal league identifiers should be pseudonymized before publication. Secrets belong in `.env`, which is ignored.
