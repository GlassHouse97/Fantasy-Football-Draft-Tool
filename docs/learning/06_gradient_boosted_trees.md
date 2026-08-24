# Gradient-Boosted Trees

## The plain-English idea

A linear model applies one straight-line effect at a time. Football development is often less tidy: workload may matter differently for young and older players, an efficiency value may be informative only above a reasonable opportunity level, and a team change may interact with experience.

Gradient boosting builds a sequence of small decision trees. Each new tree concentrates on patterns the current ensemble still misses. The final estimate adds their contributions together. Phase 4 uses histogram gradient boosting as the nonlinear rung of the model ladder because it works well with tabular data, represents thresholds and interactions, and does not require a neural network.

The boosted candidate is not automatically promoted. It must cover the same validation
player-seasons as its competitors and lower MAE on a fixed, cutoff-safe draft-relevant cohort. Its
paired-bootstrap 95% interval for learned-minus-baseline cohort MAE must remain below zero, its
pooled MAE must stay within the configured safety tolerance, and total-points top-N capture cannot
regress beyond the ranking guard. Ties, inconclusive improvements, or failures of either safety
guard retain the transparent baseline.

## Formula and statistical idea

Boosting starts with a simple prediction \(F_0(x)\) and adds trees one at a time:

\[
F_M(x)=F_0(x)+\eta\sum_{m=1}^{M}h_m(x)
\]

Here \(h_m\) is the tree added at step \(m\), \(M\) is the number of boosting iterations, and \(\eta\) is the learning rate. With squared-error loss, each new tree is fitted to reduce the current residual errors.

Histogram boosting first groups continuous values into bins. Candidate splits operate on those bins rather than every unique raw value, which makes training efficient. Tree depth and leaf size control how detailed the learned interactions can become. L2 regularization discourages overly aggressive leaf values.

## Where this is implemented

- `src/fantasy_draft_ai/models/player_projection/config.py` defines the compact, deterministic grid for learning rate, iterations, leaf count, minimum leaf size, and L2 regularization.
- `src/fantasy_draft_ai/models/player_projection/pipelines.py` builds `HistGradientBoostingRegressor` behind the same reviewed preprocessing contract used by Ridge. It fixes the random seed and disables estimator-internal early stopping so an internal random validation split cannot replace the project's chronological split.
- `src/fantasy_draft_ai/models/player_projection/tuning.py` evaluates each grid point on expanding inner-season folds and refits the chosen settings on the complete outer training period.
- `src/fantasy_draft_ai/models/player_projection/explanations.py` calculates deterministic permutation importance and one-way average partial-dependence curves. Optional SHAP can extend the report, but it is not required for a valid run.
- `src/fantasy_draft_ai/models/player_projection/evaluation.py` compares the boosted model, Ridge, and all required baselines on matched samples.
- `src/fantasy_draft_ai/models/player_projection/reporting.py` renders the held-out importance and feature-response records into tracked diagnostic SVGs.

The model artifacts are saved and hash-verified through `src/fantasy_draft_ai/models/player_projection/artifacts.py`. Reloaded predictions must match before an artifact is registered.

## Concrete fantasy-football example

Consider two RBs with the same weighted rushing yards per game. One has high targets, is early in his career, and has multiple seasons of stable workload. The other has very low targets, sparse history, and a recent team change.

A single rushing-yards coefficient gives both players the same contribution from that field. A tree ensemble can split on receiving work, history, or experience before interpreting the rushing workload. That flexibility may improve future-season predictions, but it can also fit historical quirks. Only chronological validation can tell whether the added flexibility generalizes.

Permutation importance answers a narrow question: how much does held-out prediction quality worsen when one input column is shuffled? Partial dependence shows the model's average response as one feature varies over an observed range. Neither proves that manipulating the feature would cause the predicted football outcome.

## Common mistakes

- Declaring boosting the champion because its training error is smallest.
- Using a random internal early-stopping or tuning split on player-season rows.
- Searching a huge hyperparameter grid until validation noise looks like improvement.
- Comparing candidates on different player samples.
- Treating built-in or permutation importance as causal influence.
- Computing permutation importance on training rows and presenting it as generalization evidence.
- Extrapolating a partial-dependence curve far beyond the observed feature range.
- Assuming a nonlinear model solves missing historical rookie coverage. It does not create cutoff-safe rookie examples.
- Adding complexity when Ridge or a transparent baseline performs just as well.

## Exercise

Open `notebooks/python/05_gradient_boosting_player_model.ipynb`.

1. List the hyperparameters that change across the compact grid.
2. Sketch one interaction that a tree can represent more naturally than a single linear coefficient.
3. When real Phase 4 rows are present, compare validation MAE with test MAE without using the test to change the winner.
4. Choose one importance result and rewrite it as an association rather than a causal statement.
5. Explain why a baseline tie must not be described as a boosting win.
