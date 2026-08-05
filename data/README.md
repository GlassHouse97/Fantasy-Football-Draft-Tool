# Local data layout

- `raw/`: immutable downloads and manual uploads, including reviewed identity worksheets under `raw/identity_overrides/`. Ignored by Git except placeholders.
- `interim/`: temporary reproducible transforms.
- `processed/`: reproducible derived files, including the editable identity-review worksheet under `processed/identity/`.
- `warehouse/`: the local DuckDB database, including the identity queue and reviewed source-mapping registry.
- `sample/`: small, public, clearly labeled demonstration data.
- `templates/`: versioned headers and examples for manual data.

Raw files are never overwritten. Each capture receives a timestamped filename and a SHA-256 source manifest under `data/raw/manifests/` at runtime. Reapplying identical identity-review content reuses its existing immutable archive and manifest.

`fantasy-draft data review-identities` refreshes `identity_review_queue` from verified source evidence and exports a working CSV. Name-derived matches remain candidates only. `fantasy-draft data apply-identity-overrides PATH` validates decided rows, archives the submitted file unchanged, and writes the final decision plus its provenance to DuckDB in one transaction. `player_source_mappings` is the durable registry used on future refreshes; the editable CSV is not an automatic source of truth. FFC team-defense rows are retained as excluded queue evidence and never mapped into `players`.
