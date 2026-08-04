# Local data layout

- `raw/`: immutable downloads and manual uploads. Ignored by Git except placeholders.
- `interim/`: temporary reproducible transforms.
- `processed/`: canonical derived Parquet files.
- `warehouse/`: the local DuckDB database.
- `sample/`: small, public, clearly labeled demonstration data.
- `templates/`: versioned headers and examples for manual data.

Raw files are never overwritten. Each capture receives a timestamped filename and a SHA-256 source manifest under `data/raw/manifests/` at runtime.
