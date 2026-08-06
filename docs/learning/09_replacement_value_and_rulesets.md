# Replacement Value and Exact League Rules

## The question

How much more projected value does a player provide than the replacement option implied by this
league's exact scoring, starter slots, FLEX/SUPERFLEX eligibility, team count, and bench depth?

The answer is ruleset-specific. A player can have the same football projection in two leagues and
still have a different draft value because the leagues require different numbers of starters at
each position.

## Scoring and roster shape are separate inputs

Scoring converts football production into fantasy points. Roster shape determines how many of
those fantasy-point producers a league can start. Phase 6 preserves both facts:

- `scoring_fingerprint()` identifies the scoring payload alone;
- `fingerprint()` identifies scoring plus teams, rounds, starters, FLEX slots, and bench depth.

The current Phase 4 board predicts fantasy-point totals under one validated PPR scoring payload.
A league with the same scoring but a different roster shape can reuse those player values and
recalculate replacement demand. A change from PPR to standard, a passing-touchdown change, or a
TE premium is different: direct fantasy-point predictions must be rebuilt under matching scoring
until component-level projections can be rescored safely.

## FLEX and SUPERFLEX are assignment problems

It is not enough to count positions independently. A running back can fill RB or FLEX, a wide
receiver can fill WR or FLEX, and a quarterback may fill QB or SUPERFLEX. Assigning a flexible
player too early can block a better legal lineup later.

The roster code expands the rules into concrete slots such as:

```text
QB:1       -> QB
RB:1       -> RB
WR:1       -> WR
TE:1       -> TE
FLEX:1     -> RB, WR, TE
SUPERFLEX:1 -> QB, RB, WR, TE
```

It then finds a deterministic maximum-value match between players and eligible slots. The
implementation uses augmenting-path matching and adds players in projected-value order. The sets
of players that can be matched to slots form a transversal matroid, so this weighted greedy
selection produces the maximum-value legal starter set. Stable player IDs break ties.

Bench capacity is universal after starters are assigned. Players beyond the legal starter and
bench capacity are returned as `unassigned`; the draft state rejects a pick that would create
that overflow. This is stricter and safer than hiding an illegal roster in a UI table.

## Replacement level

For player (i) at position (p), the basic value-over-replacement calculation is:

$$
VORP_i = Projection_i - Replacement_p.
$$

The project reports two transparent replacement definitions:

1. **Last starter:** fill direct starters, then flexible starters, using the best remaining legal
   projections. The lowest projected starter at a position becomes its starter replacement line.
2. **Waiver percentile:** after estimated league starters and benches are allocated, take a
   configured percentile of the remaining position pool.

Neither line is a universal fact. The last-starter definition is useful for draft scarcity; the
waiver definition is useful for estimating what may remain after the draft. Phase 6 uses the
last-starter line for its initial recommendation components and displays the raw threshold.

## Why a deeper WR league changes the answer

Compare two 12-team leagues with identical PPR scoring:

```text
League A: 2 WR + 1 FLEX
League B: 3 WR + 2 FLEX
```

League A has 24 direct WR starters and 12 flexible slots that WRs may fill. League B has 36
direct WR starters and 24 flexible slots. When the same projection pool is assigned under League
B, more WR/RB players are consumed as starters, the replacement threshold usually moves down,
and an elite WR's VORP increases. The recommendation order is allowed to change because the
league demand changed; no named player is hard-coded as universally correct.

SUPERFLEX creates the same kind of effect for quarterbacks. A one-QB projection ranking cannot
be treated as a SUPERFLEX value ranking without recomputing slot demand.

## Static replacement versus simulated scarcity

Replacement value and next-turn scarcity answer related but different questions:

- ruleset VORP compares a player with a league-wide replacement threshold;
- scarcity compares the player with the next option at that position;
- next-pick availability estimates whether the market selects the player before the user's next
  turn;
- simulation measures how the candidate affects a completed legal roster across many draft
  paths.

Keeping these as separate displayed components prevents one assumption from masquerading as the
whole recommendation.

## Tests that protect the contract

The controlled tests verify that:

- FLEX and SUPERFLEX assignments are legal and maximum-value;
- duplicate players and roster overflow are rejected;
- equivalent scoring payloads have the same scoring fingerprint even when roster shape differs;
- 3-WR/2-FLEX demand lowers the WR replacement line relative to 2-WR/1-FLEX;
- a changed scoring payload is not silently treated as compatible;
- VORP always exposes the replacement value used in the subtraction.

## Interpretation boundary

VORP is a transparent decision feature, not a prediction that the player will win a league. It
does not know who opponents will draft, how outcomes will correlate, or whether an ADP estimate
is calibrated. Those questions enter the separately versioned simulation baseline described in
[Monte Carlo Draft Simulation](10_monte_carlo_draft_simulation.md).
