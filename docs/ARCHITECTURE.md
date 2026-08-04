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
