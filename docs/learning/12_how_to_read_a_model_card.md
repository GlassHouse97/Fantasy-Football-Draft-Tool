# How to Read a Model Card

## The plain-English idea

A saved model file is not self-explanatory. A model card is the short, auditable record that says what the model predicts, what taught it, how it was tested, where it should be used, and where it should not be trusted.

Read the card before reading the leaderboard. A low error number is meaningful only when the target, population, cutoff, comparison sample, and validation period match the decision you are making.

Phase 4 produces one candidate card for each fitted position, target, and model family. A card describes a candidate whether or not that candidate becomes champion. Champion selection is a separate validation decision.

## The statistical idea

The card compares a candidate's pooled validation mean absolute error with the best transparent baseline on exactly the same player-season rows:

\[
\text{MAE}=\frac{1}{n}\sum_i |y_i-\hat y_i|
\]

The reported improvement convention is:

\[
\text{improvement}=\text{baseline MAE}-\text{candidate MAE}
\]

A positive value favors the candidate. Phase 4 promotes a learned candidate only when its validation MAE is strictly lower than the best baseline **and** the paired-bootstrap 95% interval for learned-minus-baseline MAE stays entirely below zero. A tie retains the baseline, and a lower learned MAE whose interval crosses zero is reported as inconclusive rather than promoted. The 2025 test result is attached after selection and cannot change the winner.

This performance evidence is distinct from artifact integrity. A SHA-256 digest can prove that a local artifact matches the bytes that were registered. It cannot prove that the model is accurate, fair, calibrated, or appropriate for a new population.

## How to read a Phase 4 card

1. **Identity and purpose:** Confirm model ID, family, position, target, timestamp, and intended forecast season.
2. **Data lineage:** Confirm the feature, target, build, scoring-ruleset, baseline-report, feature-contract, and model-configuration fingerprints. A mismatch means the card and current warehouse do not describe the same run.
3. **Training and cutoff:** Confirm every training prediction season precedes the evaluation season and that each feature row stops before its target season.
4. **Features and missingness:** Check the explicit feature list, categorical handling, imputation behavior, missing indicators, and the fact that targets are never imputed.
5. **Tuning and evaluation:** Check the inner folds, 2020-2024 selection period, matched baseline comparison, frozen 2025 test, and sample counts. Cross-check the overall evaluation report for segmented errors.
6. **Uncertainty:** Check the residual seasons, empirical coverage, interval width, pinball loss, and calibration caveats.
7. **Explanations:** Treat coefficients, permutation importance, partial dependence, and player factors as associations, not causes.
8. **Limitations and uses:** Pay special attention to sparse data, historical coverage, rookie routing, and what the model was not designed to answer.
9. **Artifact evidence:** Confirm the portable artifact path, SHA-256 digest, and data fingerprint. The registered warehouse metadata also records the artifact byte size, and the overall report records the reload-verification quality check.

## Where this is implemented

- Generated candidate cards live under `docs/model_cards/phase4/` and the Phase 4 report links back to them.
- `src/fantasy_draft_ai/models/player_projection/train.py` assembles the exact target, folds, metrics, baseline comparison, limitations, artifact evidence, lineage, and explanation payload for every candidate.
- `src/fantasy_draft_ai/models/player_projection/reporting.py` validates required card fields and writes the Markdown card and its SHA-256 atomically.
- `src/fantasy_draft_ai/models/player_projection/config.py` fingerprints the semantic model and feature contracts.
- `src/fantasy_draft_ai/models/player_projection/evaluation.py` owns metrics, paired comparison uncertainty, and validation-only champion selection.
- `src/fantasy_draft_ai/models/player_projection/uncertainty.py` records the empirical residual-calibration method and constraints.
- `src/fantasy_draft_ai/models/player_projection/explanations.py` produces global and player-level associative explanations.
- `src/fantasy_draft_ai/models/player_projection/artifacts.py` writes artifacts atomically, reload-checks predictions, and verifies path, size, and SHA-256.
- `src/fantasy_draft_ai/models/player_projection/repository.py` validates and persists model-card paths and hashes alongside the run, model, prediction, champion, evaluation, and live-board records.

## Concrete fantasy-football example

Suppose a WR Ridge card says it predicts next-season PPR points per active game for non-rookies, was selected from 2020-2024 validation, and reports a 2025 test result. It also says historical rookies were unavailable under the cutoff-safe position policy.

That card can support a 2026 veteran WR projection under the matching ruleset and feature contract. It cannot justify calling a rookie projection learned, cannot estimate when the draft room will select the player, and cannot decide whether roster construction makes that WR the best pick. Those are different modeling questions.

If the card's artifact hash matches but its lineage fingerprint differs from the current feature build, the artifact is intact but stale. Retraining is required before presenting it as current.

## Common mistakes

- Looking only at aggregate MAE and ignoring target definition, sample size, or position.
- Treating validation and test as interchangeable.
- Choosing a model because its 2025 test result is best after the winner was supposed to be frozen.
- Comparing a model and baseline evaluated on different player-season samples.
- Treating a model artifact hash as proof of predictive quality.
- Treating a coefficient, feature importance, or player factor as a causal explanation.
- Applying veteran evaluation evidence to rookies or other out-of-distribution rows.
- Assuming a points-per-game model also predicts availability.
- Assuming a player projection also estimates ADP movement, next-pick availability, replacement value, or optimal roster construction.
- Ignoring a stale lineage or missing model-card hash because the predictions still look reasonable.

## Exercise

Choose one card under `docs/model_cards/phase4/` after a Phase 4 run exists.

1. State the model's position, target, eligible population, and training seasons.
2. Trace its feature and baseline-report fingerprints to the Phase 4 evaluation report.
3. Identify the validation metric used for selection and the separate test metric.
4. Find one limitation that changes how you would use its 2026 projection.
5. Verify the artifact path and SHA-256 metadata without interpreting the hash as an accuracy score.
6. Write one appropriate use and one inappropriate use in your own words.
