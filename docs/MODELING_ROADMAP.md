# Modeling Roadmap

The project will climb a model ladder. A more complex model is adopted only when it beats a simpler baseline on future-season evaluation.

1. Build one row per player-season with a visible information cutoff.
2. Predict next-season games played, points per game, and total points by position.
3. Compare prior-year, weighted-history, age-adjusted, and shrinkage baselines.
4. Fit a regularized linear model for an interpretable statistical benchmark.
5. Fit a histogram gradient-boosted model for nonlinear relationships.
6. Evaluate MAE, RMSE, rank correlation, top-k recall, calibration/coverage, and positional error on rolling chronological splits.
7. Project stat components where practical, then apply the ruleset scoring engine. Keep direct fantasy-point prediction as a benchmark.
8. Archive dated ADP snapshots before claiming a movement model exists.
9. Estimate availability, then simulate rest-of-draft roster construction separately from player projection.
10. Train playoff or championship outcomes only after a documented real-history sample gate is met.

Every model card will state training seasons, target, features, leakage controls, baseline comparison, uncertainty behavior, limitations, and intended use.
