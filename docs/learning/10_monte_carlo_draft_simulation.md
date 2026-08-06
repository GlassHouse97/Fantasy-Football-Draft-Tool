# Monte Carlo Draft Simulation

## Modeling declaration

- **Question:** If the user selects candidate (c) now, what legal roster value results across
  many plausible rest-of-draft paths?
- **Data:** A frozen canonical player pool, validated P10/P50/P90 player projections, confirmed
  canonical ADP mappings, exact league rules, the event-sourced draft state, and versioned engine
  assumptions.
- **Unit:** One candidate and one simulated remainder of the draft.
- **Target:** The initial baseline summarizes final legal starter value plus a small configured
  bench-depth credit. It does not target wins, playoffs, or championships.
- **Cutoff:** The session freezes the projection run, ADP build and capture, player pool, rules,
  engine configuration, seed, and simulation count when it starts.
- **Validation:** Deterministic replay, controlled ruleset fixtures, seed-repeatability tests, and
  later comparison with real linked draft outcomes. Current opponent and availability assumptions
  are uncalibrated.

## Event sourcing makes the draft state reproducible

A draft session is an append-only stream. The first event freezes the exact inputs. Later events
record a pick, undo the most recent pick, or replace an earlier active pick. Replaying the stream
reconstructs the same:

- current overall pick and snake-draft owner;
- selected player IDs and all team rosters;
- undo/replace history;
- model, market, rules, pool, and configuration lineage.

Every event stores the prior and resulting state fingerprints. A sequence gap, stale undo target,
duplicate player, wrong team for a pick, or fingerprint mismatch makes replay fail instead of
guessing what happened.

## Canonical identity is a hard gate

Player quality uses canonical nflverse player IDs. Phase 5 market rows may still be source-keyed.
The two sources can be combined only after a reviewed canonical mapping exists. Display name is
never a join key.

At the current validated checkpoint, the live FFC board contains 246 rows. Of those, 203 are
draftable QB/RB/WR/TE rows for the active ruleset, and **0 of 203** have a reviewed canonical
mapping. The other 43 PK/DEF rows remain archived and auditable but are outside this ruleset's
coverage denominator. The production recommendation service therefore returns an identity review
action instead of running a misleading simulation. The simulator and recommendation contract are
tested with small, explicitly synthetic fixtures whose mappings are complete. This is graceful
degradation: the app remains usable for review and draft-state work without fabricating market
evidence.

## What one simulation path does

For a candidate on the user's turn:

1. add the candidate to the user's roster;
2. walk every remaining overall pick in exact snake order;
3. sample opponent selections from the mapped market pool;
4. use a fixed, transparent VORP/roster-need policy at later user turns;
5. sample player outcomes when interval evidence exists;
6. assign the user's maximum-value legal final lineup;
7. record starter value, configured bench credit, and coverage diagnostics.

The process repeats for the configured number of paths. Candidate comparisons use the same keyed
random inputs where possible so differences are driven by the candidate and the resulting draft
path rather than unrelated random noise.

## Deterministic SHA-256 random numbers

The simulator never uses Python's salted `hash()` and never touches a global random-number
generator. Each uniform value is derived from SHA-256 over stable inputs such as:

```text
(seed, purpose, simulation_index, overall_pick, player_id)
```

Two keyed uniforms feed a Box-Muller transform for normal outcome draws. Inputs are sorted by
canonical player ID, and stable IDs break ties. The same state, pool, configuration, seed, and
simulation count therefore produce the same audit path, trace fingerprint, summary, and result
fingerprint even if the caller supplies the rows in another order.

## Opponent-pick assumptions

Let (S(x)) be the survival function of a player's Phase 5 normal draft-pick distribution. For
overall pick (p), the conditional probability mass around that pick is:

$$
h_p = 1 - \frac{S(p + 0.5)}{S(p - 0.5)}.
$$

The simulator uses this one-pick hazard as the base categorical weight. Two explicit heuristics
then modify it:

- **Roster need:** a player receives a multiplier when adding that position fills an open legal
  starter, FLEX, or SUPERFLEX slot. Until starters are covered, legal starter-improving options
  take priority over bench accumulation.
- **Positional run:** recent selections at the same position add a modest configured multiplier,
  capped at 25 percent.

A small configured floor prevents every weight from becoming numerical zero in the tails. These
need and run effects are rules, not learned opponent behavior, and their values are visible in
`configs/draft_engine.yaml`.

## Player outcome intervals and point-only rows

For a validated interval, the simulator draws a standard-normal value around P50. The scale below
the median is anchored so P10 is reached at the standard-normal 10th percentile; the scale above
the median is anchored to P90. This allows asymmetric downside and upside:

$$
\sigma_{down} = \frac{P50-P10}{1.28155}, \qquad
\sigma_{up} = \frac{P90-P50}{1.28155}.
$$

Some transparent baselines and all current rookie fallbacks are point-only, with
`P10 = P50 = P90`. They remain deterministic at P50. Zero width is missing uncertainty evidence,
not proof that the player is safe. The safe-floor and high-upside recommendation roles require
measured interval evidence, and every result reports interval coverage.

The MVP samples players independently. Team, game, injury, and shared-offense correlations remain
a documented limitation.

## A visible work budget

Simulation cost grows with candidates, paths, and remaining picks. The deterministic guard is:

```text
work units = candidate_count * simulation_count * remaining_selections
```

The tracked interactive baseline uses 6 shortlisted candidates and 64 paths, caps a request at
1,000 paths, and rejects work above 1,000,000 units. It also considers only a configured imminent
market window at each opponent pick and caches roster-shape legality. This protects the local app
from an accidental multi-minute request while keeping tests fast at 16 paths.

## The recommendation score is transparent

Before a trained roster-outcome model exists, Phase 6 returns a configured score rather than a
fake probability. Raw components include:

- P50, floor, and ceiling VORP;
- same-position scarcity;
- probability the player is gone before the next user turn;
- legal roster fit;
- simulated final-roster mean, floor, and ceiling;
- interval-width risk penalty.

Each component exposes its raw value, direction, normalized value, configured weight, and weighted
contribution. The displayed score can be recomputed by summing those contributions. The weights
are versioned starting assumptions, not learned truths.

Three distinct roles use different visible weight profiles:

1. **Balanced:** emphasizes P50 VORP, roster fit, scarcity, and simulated mean.
2. **Safer floor:** emphasizes P10 VORP, downside width, and simulated P10.
3. **Higher upside:** emphasizes P90 VORP, scarcity, gone probability, and simulated P90.

Point-only candidates cannot silently win the safer-floor role merely because their interval
width is zero.

## Why there is no championship probability

The simulation completes a draft under transparent market and outcome assumptions. It does not
model waivers, trades, start/sit choices, weekly matchups, opponent outcome correlation, playoffs,
or a calibrated relationship between roster value and titles. Calling its score a championship
probability would be false precision.

A future championship model requires enough uploaded league histories, league-grouped
season-forward validation, and probability calibration. Until then the output is named exactly
what it is: a **draft recommendation score** with a simulated roster-value distribution.

## Failure and leakage tests

The quality gates verify that:

- replay is identical and rejects altered event links;
- snake order reverses every even round for every supported team count;
- selected players never reappear and each simulated path has no duplicates;
- input row order cannot change a seeded result;
- unresolved market rows never join by display name;
- altered pool, configuration, state, and scoring fingerprints are rejected;
- FLEX/SUPERFLEX legality and the ruleset-sensitivity fixture behave as expected;
- point-only rows stay deterministic and are not labeled safe;
- work above the configured budget stops before expensive paths begin;
- no recommendation payload contains a championship-probability field.

## Try the executable fixture

Open `notebooks/python/10_draft_simulation.ipynb`. It uses a small, fully mapped synthetic player
pool, replays an event stream, verifies exact flexible-slot assignment, runs low-path deterministic
recommendations, and recomputes the displayed component scores. It reads the live mapping count
only to show the separate production gate; no live player is joined or simulated by name.
