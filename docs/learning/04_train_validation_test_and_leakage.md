# Train, Validation, Test, and Leakage

## The plain-English idea

A football projection is useful only if it can predict a season it has not seen. The project therefore moves through history in the same direction as a real draft: learn from older seasons, make a prediction, and reveal that season's result afterward.

Three data roles must stay separate:

- **Training data** teaches the model's coefficients, tree splits, imputers, encoders, and other fitted values.
- **Validation data** compares hyperparameters and decides whether a learned model has earned the champion label.
- **Test data** is the final untouched check. It describes the selected approach; it does not get another vote in selection.

For Phase 4, prediction seasons 2020 through 2024 are expanding validation folds. Prediction season 2025 is the frozen test. A 2026 row is a live forecast whose target is not yet available.

## The statistical rule

For an evaluation season \(s\), every fitted operation must satisfy:

\[
\max(\text{training prediction seasons}) < s
\]

The outer evaluation sequence is:

```text
older seasons -> validate 2020
older seasons plus 2020 -> validate 2021
older seasons plus 2020-2021 -> validate 2022
older seasons plus 2020-2022 -> validate 2023
older seasons plus 2020-2023 -> validate 2024
older seasons plus 2020-2024 -> test 2025
all validated history through 2025 -> forecast 2026
```

Hyperparameter tuning is nested inside each outer training period. If the outer fold evaluates 2023, Ridge's penalty and boosting's tree settings are compared only with inner folds that end before 2023. The 2023 outcome cannot influence preprocessing, tuning, residual calibration, or feature selection.

The row itself also has a cutoff. A row with prediction season \(s\) uses a September 1 cutoff in feature season \(s-1\). In compact form:

\[
X_{p,s-1}^{\text{available by cutoff}} \longrightarrow y_{p,s}
\]

Acquisition time is provenance, not permission to use a future statistic.

## Where this is implemented

- `src/fantasy_draft_ai/features/player_seasons.py` builds the cutoff-safe player-season rows and keeps feature targets separate.
- `src/fantasy_draft_ai/models/evaluation/splits.py` creates deterministic expanding outer folds and labels the last fold as test.
- `src/fantasy_draft_ai/models/player_projection/dataset.py` enforces the reviewed feature allowlist, leaves unknown targets missing, and excludes rookies from learned-model training.
- `src/fantasy_draft_ai/models/player_projection/tuning.py` tunes each candidate on chronological inner folds and then refits on the complete outer training period.
- `src/fantasy_draft_ai/models/player_projection/uncertainty.py` rejects residuals from the inference season or any later season.
- `src/fantasy_draft_ai/models/player_projection/evaluation.py` selects champions with pooled 2020-2024 validation MAE plus a paired-bootstrap uncertainty gate. A learned candidate must lower MAE and keep the learned-minus-baseline 95% interval below zero; the 2025 test result is attached only after selection.
- `src/fantasy_draft_ai/models/player_projection/train.py` orchestrates the outer folds, final through-2025 refit, live 2026 forecast, and persisted lineage checks.

The frozen Phase 3 feature, target, ruleset, build, and baseline-report fingerprints are included in the Phase 4 run lineage. Rebuilding upstream data or changing the baseline comparison invalidates a stale model run.

## Concrete fantasy-football example

Imagine tuning a 2023 WR model. Its 2023 feature row contains information available through the 2022 cutoff, and its target is 2023 fantasy points per active game.

A safe inner comparison might train on prediction seasons through 2020 and validate on 2021, then train through 2021 and validate on 2022. It chooses the Ridge penalty before any 2023 result is examined. The selected pipeline then refits on all eligible pre-2023 rows and predicts 2023.

It would be leakage to calculate the WR median target volume using rows from 2023 before filling a missing 2023 input. The imputer must learn that median from the outer training rows only, which is why it lives inside the scikit-learn pipeline.

## Common mistakes

- Randomly splitting player-season rows, which lets later football seasons teach earlier ones.
- Scaling, imputing, encoding, or selecting features on the complete dataset before the split.
- Tuning hyperparameters on the 2025 test and still calling 2025 untouched.
- Letting a 2024 validation residual calibrate a 2023 interval.
- Joining a target-season statistic into a lag feature because of an off-by-one season key.
- Using today's team, status, depth chart, or ADP snapshot in a historical fold.
- Filling a missing target with zero. Missing participation evidence is not a zero-game outcome.
- Filtering the candidate population to players later known to have played, which creates survivorship bias.
- Reading the final test repeatedly and informally changing the model in response.

## Exercise

Open `notebooks/python/04_linear_player_model.ipynb` and inspect the fold audit.

1. Write down the maximum training season for each evaluation season.
2. Explain why `training_max_season >= prediction_season` is a failure.
3. Identify one preprocessing step that would leak if fitted before the split.
4. Pretend 2025 favors a different model than 2020-2024. State which model the selection rule must keep and why.
