# Projection Baselines and Why They Matter

## The question

Before accepting a machine-learning model, we need to know whether it improves on a simple, honest forecast. A projection baseline answers a deliberately modest question:

> Given only information that existed before an NFL season began, what would a transparent rule have predicted for each player in that season?

If a complicated model cannot beat a careful historical average on future seasons, the extra complexity has not earned a place in the draft tool.

## One row looks backward and predicts forward

The unit of observation is one player and one prediction season. For a row labeled feature season `t` and prediction season `t + 1`:

- regular-season statistics through season `t` may become features;
- statistics from season `t + 1` are targets used only after a prediction is made;
- postseason statistics are excluded;
- every lag and rolling value must stop at `t`.

For example, a 2025 feature row may use a receiver's 2023, 2024, and 2025 regular seasons to predict 2026. It must not use a 2026 game, a late-2026 injury result, or a depth-chart label created after the 2026 draft.

This relationship is written as:

\[
X_{p,t} \longrightarrow y_{p,t+1}
\]

where `p` is the player, `X` is the information available through season `t`, and `y` is the next-season outcome.

## Cutoff time is not acquisition time

Three dates answer different questions:

1. **Football event time** says when a game or season occurred.
2. **Feature cutoff** says the latest event information allowed in a prediction row.
3. **Acquisition time** says when this project downloaded its immutable copy of the source.

A file downloaded in 2026 may contain 2019 statistics. Its 2026 acquisition timestamp is essential provenance, but it does not turn those 2019 statistics into 2026 performance. Conversely, a historical capture can contain later corrections, so the source manifest and dataset ID must remain attached to the derived table.

The Phase 3 builder therefore needs both a visible cutoff and traceable source provenance. It must enforce season and cutoff rules from the data itself rather than infer historical truth from today's `players` snapshot. Current team, experience, and active-status fields are not valid historical features.

### Position identity also needs a cutoff

Position is not timeless. A player can be relabeled later in his career, so today's canonical position cannot be projected backward into a historical rookie or other entry cohort. Phase 3 first looks for position evidence that existed by the row's September 1 feature cutoff. If a historical entry-cohort candidate has no cutoff-safe, time-versioned position evidence, the builder excludes that candidate and reports the exclusion in its quality output instead of borrowing a later label.

The live 2026 build has one deliberately narrow fallback. Its player-identity snapshot was acquired in August 2026, before the September 1, 2026 cutoff, so the static position in that snapshot is valid for a live 2026 candidate when no earlier record-level position is available. The same snapshot is after every historical cutoff and therefore cannot supply a historical position.

This policy has an honest evaluation consequence: historical rookie-baseline performance cannot be measured comprehensively from the current sources. Doing that requires a historical preseason-position archive captured before each season's cutoff. Excluded historical entry-cohort rows remain visible in the quality report rather than being converted into a deceptively complete metric.

## Regular-season aggregation and participation denominators

Season totals are sums of regular-season component statistics such as attempts, carries, targets, receptions, yards, touchdowns, interceptions, and fumbles lost. Per-game rates require more care.

An observed weekly stat row is not automatically proof that the player was active or played a game. A zero-opportunity row may describe an active player who received no work, an inactive roster record, or a source convention. Therefore:

- `lag1_stat_games` means exactly "distinct games represented by weekly stat rows";
- `games_active` or `games_played` should be used only when a trusted source establishes that meaning;
- a points-per-game target should remain unavailable, or be labeled as an explicit proxy, when its denominator is not supported;
- missing participation evidence is data, not zero, and needs a missingness indicator.

Phase 3 adds separately archived nflverse/PFR snap counts. `games_active` counts a game only when mapped offense, defense, or special-teams snaps are positive. Calling an uncertain stat-row count "games played" would make the evaluation look precise while changing the target being modeled.

## Five transparent baselines

Let `y[p,t]` be a player's observed points per game in season `t`.

### 1. Previous-season baseline

\[
\hat{y}_{p,t+1} = y_{p,t}
\]

This is the clearest persistence assumption: next season looks like last season. It is strong for stable veterans and weak for role changes, rookies, injuries, and aging curves.

### 2. Weighted-history baseline

\[
\hat{y}_{p,t+1} =
\frac{w_0 y_{p,t} + w_1 y_{p,t-1} + w_2 y_{p,t-2}}
     {w_0 + w_1 + w_2}
\]

Recent seasons receive more weight, for example 60%, 30%, and 10%. If a player has less history, use only available seasons and renormalize the weights. Do not fill an absent rookie season with zero.

### 3. Age- and position-adjusted history

Players do not age at the same rate across positions. This first transparent baseline multiplies weighted history by a small, documented position-and-age bucket factor:

\[
\hat{y}_{p,t+1} = \hat{y}^{weighted}_{p,t+1}
                  \times f(position, age\ bucket)
\]

The current factors are fixed heuristic assumptions, not learned values. Phase 4's Ridge and gradient-boosted candidates can learn associations involving age, but each validation fold learns them only from older seasons. Calculating them with a validation player's future result would be leakage.

### 4. Position-average shrinkage

Small samples produce noisy rates. Shrink a player's rate toward a prior position mean:

\[
\hat{y}_{p,t+1} =
\frac{n_p y_{p,t} + k \mu_{position,t}}{n_p + k}
\]

Here `n[p]` is a trusted participation or opportunity volume, `mu` is the position average from allowable history, and `k` controls the strength of the prior. A low-volume player moves more toward the position mean than a high-volume veteran.

### 5. Weighted component reconstruction

Instead of averaging already-scored fantasy points, independently weight the player's per-active-game passing, rushing, receiving, turnover, and opportunity components. Feed that reconstructed stat line through the configured league scoring engine. This makes the projection explainable in football units and lets one feature build respect different scoring rules.

Threshold yardage bonuses need special care. A bonus is earned by an observed weekly performance, not by an averaged stat line. Phase 3 therefore calculates bonus points for each historical week, weights those bonus points per active game separately, scores the averaged component line with threshold bonuses disabled, and adds the weighted weekly bonus contribution afterward. It never awards a 100-yard bonus merely because two sub/super-threshold games average to 100 yards.

A current ADP rank can later serve as a weak ranking baseline, but it cannot be inserted into a historical fold unless the snapshot was captured before that historical draft.

## Chronological evaluation

Player rows are related across seasons, so a random split would let future football inform the past. Use expanding folds whose labels are prediction seasons:

```text
Train through prediction season 2019 -> validate 2020
Train through prediction season 2020 -> validate 2021
Train through prediction season 2021 -> validate 2022
Train through prediction season 2022 -> validate 2023
Train through prediction season 2023 -> validate 2024
Train through prediction season 2024 -> test 2025
Features through 2025               -> forecast 2026 (target not yet known)
```

In the 2020 validation fold, every training target is from 2019 or earlier and every 2020 feature stops at 2019. Any age adjustment, shrinkage strength, tier boundary, or other fitted choice must be learned within the training side of that fold.

## How the baselines are scored

No single metric tells the whole story.

- **MAE** is the average absolute miss and is easy to explain in fantasy-point units.
- **RMSE** penalizes large misses more heavily.
- **Median absolute error** shows the typical miss without letting a few extreme seasons dominate.
- **Spearman rank correlation** asks whether the ordering is useful even when point estimates are imperfect.
- **Top-N overlap by position** compares the projected and actual top group at QB, RB, WR, and TE.
- **Segmented error** reveals whether results fail for a position, experience group, or projection tier.

Report the number of eligible and scored rows with every metric. Missing targets must not disappear silently.

## Common leakage traps

- Aggregating target-season weeks into a lag feature because of an off-by-one join.
- Computing a rolling average after sorting by player but forgetting to shift one season.
- Using today's team, experience, active status, or depth chart in an old fold.
- Using a current ADP snapshot to evaluate a historical draft.
- Defining tiers or age adjustments from the complete dataset before splitting.
- Selecting only players known to have played in the target season, creating survivorship bias.
- Treating missing rookie history as zero production.
- Leaving `target_payload` or another target-derived field in the feature matrix.

Automated tests should assert cutoff order, chronological folds, target exclusion, regular-season filtering, deterministic repeat builds, and source-manifest provenance.

## Where this lives in the project

The Phase 3 interfaces are organized around:

- `player_week_stats` as the canonical weekly input;
- `player_season_features` as the cutoff-safe player-season output;
- `src/fantasy_draft_ai/features/` for aggregation and row accounting;
- `src/fantasy_draft_ai/models/baselines/` for transparent forecasts;
- `src/fantasy_draft_ai/models/evaluation/` for chronological folds and metrics;
- `models/reports/` for generated evaluation reports.

The build and evaluation entry points are:

```powershell
fantasy-draft features build-player-seasons --prediction-season 2026 --rules configs/example_ppr_12_team.yaml
fantasy-draft models evaluate-baselines --rules configs/example_ppr_12_team.yaml
```

Run the warehouse audit and the repository quality gates before treating generated rows or baseline results as validated.

## Concrete fantasy-football example

Suppose a WR scored 12, 15, and 14 PPR points per game over three seasons. A 10%/30%/60% weighted baseline predicts:

\[
0.10(12) + 0.30(15) + 0.60(14) = 14.1
\]

If those 14 points came from only a few trustworthy games, a shrinkage baseline should pull the estimate toward the position average. An age adjustment might move it again, but only using historical WR aging evidence available before the prediction season.

## Limitations

Baselines do not know about a new coordinator, a rookie's college profile, an August injury, a depth-chart promotion, or a sudden team change unless those inputs are explicitly added with valid cutoffs. They are reference points, not final rankings. Their purpose is to set an honest performance bar for Phase 4 models.

Phase 4 machine-learning training is now complete. The validated baselines still matter: each learned candidate had to beat its route's transparent baseline on chronological validation and clear the paired-bootstrap confidence gate before it could become the champion.

## Exercise

Open `notebooks/python/03_projection_baselines.ipynb` and:

1. Change the weighted-history weights from 60/30/10 to 50/30/20.
2. Increase the shrinkage strength `k`.
3. Predict which players will move most before running the cells.
4. Compare MAE, RMSE, rank correlation, and top-N overlap.
5. Explain why the setting with the lowest RMSE might not produce the best draft ranking.
