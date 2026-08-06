# Uncertainty and Prediction Intervals

## The plain-English idea

A point projection hides how often similar forecasts have missed. Two players can both project to 13 points per active game while one has a much wider range of plausible outcomes. Phase 4 therefore pairs eligible learned point estimates with empirical P10, P50, and P90 values derived from earlier out-of-fold residuals.

These are model-based uncertainty summaries, not promises. A nominal central 80% interval should contain about 80% of comparable future outcomes when it is calibrated, but coverage can drift by position, projection tier, era, or data quality. The report must show observed coverage and width rather than simply printing precise ranges.

Historical cutoff-safe rookie feature rows are not available in the current archive. Live rookies therefore use a clearly labeled transparent heuristic fallback. Their ranges must be labeled unvalidated and uncalibrated; a veteran residual distribution cannot be presented as validated rookie uncertainty.

## Formula and statistical idea

For a chronological out-of-fold prediction, define the signed residual:

\[
r_i = y_i - \hat y_i
\]

Using only residuals from seasons earlier than inference season \(s\), calculate their 10th, 50th, and 90th percentiles. Shift the current point prediction by those offsets:

\[
P10_s=\hat y_s+Q_{0.10}(r),\quad
P50_s=\hat y_s+Q_{0.50}(r),\quad
P90_s=\hat y_s+Q_{0.90}(r)
\]

Signed residuals allow a median correction when the model tends to under- or over-predict. They also preserve asymmetric historical misses.

For observed outcomes, central-80 coverage and average width are:

\[
\text{coverage}=\frac{1}{n}\sum_i I(P10_i\le y_i\le P90_i)
\]

\[
\text{average width}=\frac{1}{n}\sum_i(P90_i-P10_i)
\]

Coverage alone is not enough: an extremely wide interval can cover almost everything while being unhelpful. Pinball loss evaluates a quantile \(q\):

\[
L_q(y,\hat y_q)=
\begin{cases}
q(y-\hat y_q), & y\ge\hat y_q\\
(1-q)(\hat y_q-y), & y<\hat y_q
\end{cases}
\]

Lower pinball loss is better for the stated quantile.

## Where this is implemented

- `src/fantasy_draft_ai/models/player_projection/tuning.py` produces training-history-only out-of-fold predictions for selected hyperparameters.
- `src/fantasy_draft_ai/models/player_projection/uncertainty.py` fits signed residual quantiles, rejects inference-season and future residuals, enforces ordered intervals, and bounds only games-active predictions to the documented 0-to-18 range.
- `src/fantasy_draft_ai/models/player_projection/evaluation.py` calculates coverage, average width, and P10/P50/P90 pinball losses on evaluable rows.
- `src/fantasy_draft_ai/models/player_projection/explanations.py` labels rookie heuristic uncertainty as unvalidated and uncalibrated.
- `src/fantasy_draft_ai/models/player_projection/train.py` applies learned or baseline residual calibration to eligible live rows and uses a labeled point-only boundary for rookies.
- `src/fantasy_draft_ai/models/player_projection/reporting.py` creates the coverage-versus-width diagnostic without inventing points for an empty slice.
- `player_projection_predictions` stores candidate point estimates, intervals, fold labels, actual values when available, and the maximum training season used.
- `player_projection_board` stores the selected P10/P50/P90 fields and a prediction-status label for the live season. A rookie point fallback repeats its point in those fields but remains labeled unvalidated and uncalibrated.

Fantasy-points targets are not clipped to zero because legitimate negative seasonal outcomes exist under the scoring rules. Games active is bounded because it has a physical scale; the upper limit is 18 to accommodate legitimate source records for traded players across the current schedule structure.

## Concrete fantasy-football example

Suppose a WR point model forecasts 14.0 PPR points per active game. Earlier chronological residuals have P10, P50, and P90 offsets of -4.0, -0.5, and 5.0. The empirical interval becomes 10.0, 13.5, and 19.0.

The P50 being below the raw point estimate reveals a small historical over-prediction tendency in the calibration sample. It does not mean the player's true outcome has an 80% guaranteed probability of landing between 10 and 19. The honest interpretation is that the interval applies an earlier out-of-fold residual pattern, whose realized coverage must be checked on later seasons and within relevant segments.

## Common mistakes

- Calibrating a 2023 prediction with residuals from 2023, 2024, or 2025.
- Using in-sample residuals, which are usually too optimistic.
- Calling P10/P90 a guarantee or a complete probability distribution.
- Reporting coverage without width, or width without coverage.
- Assuming a nominal 80% interval has achieved 80% coverage without measuring it.
- Hiding poor calibration in one position behind an acceptable overall average.
- Sorting interval endpoints after a broken calculation instead of fixing the source invariant.
- Clipping fantasy points to zero and silently erasing legitimate negative outcomes.
- Giving rookies veteran-calibrated ranges without cutoff-safe historical rookie validation.
- Penalizing a wide interval as if it were a lower mean projection; risk preference belongs in a later decision layer.

## Exercise

Open `notebooks/python/06_uncertainty_and_calibration.ipynb`.

1. Verify that each displayed row satisfies `p10 <= p50 <= p90`.
2. Calculate coverage and average width for one position when evaluated rows exist.
3. Compare two groups with similar coverage but different widths.
4. Explain why 2025 residuals cannot calibrate a 2025 interval.
5. Find the rookie-status wording and describe what additional archive would be needed to validate it.
