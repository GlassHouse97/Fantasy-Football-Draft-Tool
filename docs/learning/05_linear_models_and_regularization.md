# Linear Models and Regularization

## The plain-English idea

A linear model gives each reviewed input a weight and adds the weighted inputs together. It is a useful first learned model because the relationship is inspectable: after preprocessing, each coefficient has a direction and a size.

Football inputs overlap. Prior-year points, weighted history, targets, receptions, and yards often carry similar information. An unregularized model can respond with large, unstable coefficients that cancel one another. Ridge regression adds a penalty that gently pulls coefficients toward zero. It trades a little training fit for more stable future-season behavior.

Phase 4 fits separate pipelines for QB, RB, WR, and TE, and separately predicts next-season fantasy points per active game, games active, and total fantasy points. A target is used only when its value is known; targets are never imputed.

## Formula and statistical idea

The linear prediction is:

\[
\hat y_i = \beta_0 + \sum_{j=1}^{p}\beta_j x_{ij}
\]

Ridge chooses coefficients by minimizing squared error plus an L2 penalty:

\[
\underset{\beta}{\operatorname{argmin}}
\left[
\sum_i (y_i-\hat y_i)^2 + \alpha\sum_j \beta_j^2
\right]
\]

The tuning value \(\alpha\) controls shrinkage. With a small \(\alpha\), the model behaves more like ordinary least squares. With a larger \(\alpha\), coefficients are pulled closer to zero. The intercept is not the football meaning of a replacement player; it is simply the fitted constant after preprocessing.

Numeric features are standardized so one unit of age and one unit of passing yards do not receive penalties on incomparable scales. Categorical team values are one-hot encoded. Median imputation and missingness indicators preserve the distinction between an observed value and a filled value.

## Where this is implemented

- `src/fantasy_draft_ai/models/player_projection/config.py` locks the explicit numeric and categorical feature allowlist, Ridge penalties, targets, positions, and seed into a fingerprinted configuration.
- `src/fantasy_draft_ai/models/player_projection/dataset.py` extracts only allowed predictors, masks null targets, routes by position and target, and keeps rookies out of learned training.
- `src/fantasy_draft_ai/models/player_projection/pipelines.py` creates the median-imputation, missing-indicator, scaling, one-hot encoding, and Ridge pipeline.
- `src/fantasy_draft_ai/models/player_projection/tuning.py` compares Ridge penalties only inside chronological training folds.
- `src/fantasy_draft_ai/models/player_projection/explanations.py` reports transformed coefficient direction and magnitude and creates non-causal player-level reference substitutions.
- `src/fantasy_draft_ai/models/player_projection/evaluation.py` compares the linear candidate with every required transparent baseline and the nonlinear candidate.
- `src/fantasy_draft_ai/models/player_projection/train.py` fits each position-target route, produces the candidate cards and live rows, and hands diagnostics to the report writer.

The feature contract intentionally forbids `baseline_*`, `target_*`, identity metadata, candidate-selection metadata, and target payloads. Adding a predictor requires a reviewed contract change rather than silently inheriting a new JSON field.

## Concrete fantasy-football example

Suppose a WR's standardized weighted three-year targets per game is one unit above the training-set mean. If its fitted coefficient is positive, that feature contributes upward relative to an otherwise identical row. A negative coefficient on a team-change indicator could contribute downward.

That does **not** mean changing teams causes a lower fantasy score. Team changes can be associated with age, role, injury, or other unmeasured circumstances. The coefficient describes how the fitted model combines available predictors after holding its other encoded inputs fixed.

If targets, receptions, and receiving yards all describe a similar opportunity signal, Ridge can distribute weight across them without allowing one noisy coefficient to explode merely to improve the historical training fit.

## Common mistakes

- Reading a standardized coefficient as fantasy points per one raw unit.
- Comparing coefficient magnitude across a scaled numeric field and an encoded category without checking the transformed feature definition.
- Treating an association as a causal claim.
- Fitting the imputer, scaler, or encoder before creating the chronological fold.
- Tuning \(\alpha\) on the outer validation or 2025 test season.
- Passing every JSON field into the model and accidentally including a baseline or target-derived value.
- Replacing an unknown outcome with zero instead of excluding it from that target's fit.
- Assuming a sparse-history player and a rookie are the same case. Phase 4 can train on eligible sparse veteran history, while rookies use an explicit heuristic boundary until cutoff-safe historical rookie rows exist.
- Assuming interpretability makes the model accurate. Ridge must still beat the baseline out of time.

## Exercise

Open `notebooks/python/04_linear_player_model.ipynb`.

1. Compare the candidate Ridge penalties stored for one position and target.
2. Find the selected penalty without looking at the 2025 result.
3. Inspect the largest positive and negative coefficients when a fitted report is present.
4. Pick one coefficient and describe it with associative, non-causal language.
5. Explain why the best training error is not the selection criterion.
