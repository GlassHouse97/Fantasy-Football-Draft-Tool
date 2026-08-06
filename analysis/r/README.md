# Optional R/Quarto Companion

These Quarto documents are optional teaching and audit companions. Python remains the canonical build, training, artifact, and warehouse-write path. The R analyses open the same local `data/warehouse/fantasy_football.duckdb` file read-only; they do not download another dataset, rewrite canonical tables, select production champions, or save competing model artifacts.

## Documents

- `01_data_exploration.qmd` inspects Phase 3 row coverage and the Phase 4 table state.
- `02_regularized_regression.qmd` fits a small, explicitly educational Ridge example from canonical cutoff-safe rows.
- `03_rolling_resampling.qmd` audits expanding-season splits and stored training cutoffs.
- `04_model_comparison_and_calibration.qmd` independently summarizes stored validation/test predictions, champions, and empirical intervals.

`01_scoring_comparison.qmd` remains the earlier ruleset illustration.

## Optional setup

Install R and Quarto separately, then install the analysis packages in R:

```r
install.packages(c(
  "arrow", "broom", "DBI", "dplyr", "duckdb", "ggplot2", "glmnet",
  "jsonlite", "knitr", "parsnip", "purrr", "recipes", "rsample",
  "tibble", "tidymodels", "tidyr", "tune", "workflows", "yardstick"
))
```

From the repository root, render one document with:

```powershell
quarto render analysis/r/01_data_exploration.qmd
```

The documents find the repository root from the working directory and contain no user-specific machine paths. If the warehouse or Phase 4 outputs do not exist, they print an honest prerequisite message instead of fabricating a result.

## Validation status

R and Quarto are not installed in the current project environment, so these files are not part of the blocking Python quality gates and were not executed for Phase 4. Their SQL and assumptions mirror the canonical DuckDB contracts, but a rendered document must still be reviewed before publication.
