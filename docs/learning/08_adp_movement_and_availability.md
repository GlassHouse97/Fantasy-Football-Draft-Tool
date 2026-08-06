# ADP Movement and Next-Pick Availability

## The two questions are different

Average draft position (ADP) is a market observation, not a player projection. Phase 5 asks two
separate questions:

1. **Movement:** where is a player's ADP likely to be after a stated time horizon?
2. **Availability:** given that the player is available now, what is the probability that the
   player is still available at a later pick?

Neither answer says whether the player is good, whether the roster needs the position, or whether
the user should draft the player. Player quality, market movement, and draft availability remain
separate signals until the draft engine can evaluate them together.

## Modeling declaration

- **Question:** How is an observed ADP changing, and will the player survive to a future pick?
- **Data:** Immutable, timestamped FFC or manually supplied ESPN ADP snapshots whose raw hashes
  match their manifests.
- **Unit:** One source player in one market snapshot, scoped by season, scoring format, team count,
  and optional position filter.
- **Movement target:** Future average pick at a stated forecast horizon. The current foundation
  does not have enough future observations to evaluate this target.
- **Availability target:** Whether a player is selected before a future overall pick. Until real
  draft outcomes are archived, Phase 5 estimates this from the source's observed draft-pick
  distribution rather than claiming a trained classifier.
- **Cutoff:** Only snapshots captured at or before the prediction timestamp may enter features or
  baselines.
- **Validation:** Chronological evaluation only. Later snapshots and later draft outcomes may
  score an earlier forecast, but may never help create it.

## Why immutable snapshots matter

An ADP website normally shows only its current state. If today's response overwrites yesterday's
file, there is no honest way to reconstruct what was knowable yesterday. Each acquisition is
therefore archived under a new timestamped path and bound to a SHA-256 manifest. A deterministic
snapshot identity uses the market scope, capture timestamp, and raw content hash; two manifests
that reference the same capture are one market observation, not two samples.

The canonical loader verifies the hash before parsing, retains source player IDs, and leaves
unresolved canonical player IDs null. Display names can produce review evidence, but they are
never used as an automatic join key.

## Cutoff-safe movement features

For a current observation at time $t$, useful transparent features include:

- current and previous ADP;
- elapsed days since the previous observation;
- changes over 1, 3, 7, and 14 days, when an observation exists before the relevant boundary;
- velocity, measured as ADP-pick change per day;
- acceleration, measured as the change in consecutive velocities per day;
- rolling volatility;
- cross-source spread for a confirmed canonical identity;
- the number of dated observations available at the cutoff.

The sign convention in this project is:

```text
ADP change = current average pick - prior average pick
```

A positive value means the player moved later in drafts; a negative value means the player became
more expensive. Missing history remains null. Zero is a real claim of no change and is not used as
a substitute for missing evidence.

## Transparent movement baselines

Phase 5 implements three deterministic baselines before any supervised model:

- **Persistence:** the next ADP equals the latest observed ADP.
- **Linear trend:** a least-squares line through the dated observations is projected to the stated
  horizon.
- **Exponentially weighted trend:** recent interval velocities receive more weight than older
  velocities.

Persistence needs one observation. Trend baselines need multiple independent timestamps. When
the archive is too short, their persisted status is `insufficient_history` and their prediction is
null. This is more informative than manufacturing a trend from one point.

## From an ADP distribution to availability

Let $X$ be the overall pick at which a player is selected. The first foundation models $X$ with a
normal distribution centered at the source ADP. Its scale is chosen in this order:

1. source-reported standard deviation;
2. a scale derived from the source's observed minimum and maximum picks;
3. a versioned fallback for the player's position and ADP range.

The result always exposes which evidence was used. A fallback is an assumption, not a measured
sample, and remains labeled as such in the warehouse, report, service, and app.

With a continuity correction, the unconditional probability of being available at overall pick
$n$ is approximately:

$$
P(X \ge n) = 1 - F(n - 0.5),
$$

where $F$ is the fitted cumulative distribution function. During a draft, we know that the player
is still available at the current pick $c$. The useful conditional probability is therefore:

$$
P(X \ge n \mid X \ge c)
= \frac{1 - F(n - 0.5)}{1 - F(c - 0.5)}.
$$

The probability of selection before the next pick is its complement. These probabilities must be
bounded from zero to one, sum to one, and availability must never increase as the requested future
pick moves later.

## Calibration is not optional evidence

A probability can be calculated before it can be calibrated. Calibration asks whether events
labeled 70% actually occur about 70% of the time. That requires real draft outcomes or archived
boards paired with the exact pre-draft snapshot. The current archive does not contain enough such
outcomes, so Phase 5 truthfully reports:

- persistence baseline: available;
- linear and exponentially weighted movement validation: insufficient dated history;
- distribution-based next-pick availability: available and uncalibrated;
- supervised movement or survival model: unavailable;
- calibration report: unavailable.

## Leakage traps to test

1. Selecting the newest snapshot today and using it for a draft that happened earlier.
2. Counting two manifests for the same raw capture as two observations.
3. Backfilling a confirmed identity mapping without retaining when and how it was reviewed.
4. Computing a seven-day change from an observation captured after the feature cutoff.
5. Tuning fallback spreads against outcomes that are later used as a final test.
6. Treating a source's current min/max range as a historically calibrated probability interval.

## What comes next

Continue acquiring real dated snapshots. Once the archive spans enough independent dates, evaluate
persistence and trend baselines on expanding chronological folds. Only then is a learned movement
model justified. Once real draft selections are linked to cutoff-safe snapshots, evaluate
availability with calibration curves and Brier scores before the probability can influence a
Phase 6 draft simulation.
