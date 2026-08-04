# Scoring and Replacement Value

## Why predict components first?

A football projection such as 95 receptions and 1,100 receiving yards can be reused in standard, half-PPR, PPR, and TE-premium leagues. A single hard-coded fantasy-point target cannot. The scoring engine therefore converts stat components into points after the football projection is made.

## Scoring is arithmetic, not machine learning

Passing yards, rushing touchdowns, receptions, turnovers, and two-point conversions each receive the configured value. Yardage settings use “yards per point,” so 250 passing yards at 25 yards per point creates 10 points. Position-specific reception bonuses are added only for the configured position.

## Roster slots create demand

A 12-team league with three starting WR spots has at least 36 directly required WR starters. Two FLEX spots add another 24 starter slots that may be filled by RB, WR, or TE. Because those flex spots are shared, the implementation reports both direct demand and eligible flexible demand rather than pretending every flex slot belongs to one position.

## Two replacement definitions

1. **Last starter:** Sort eligible projected players by points and use the player at the estimated starter-demand boundary. This is aggressive and useful for understanding positional scarcity.
2. **Waiver percentile:** Move beyond expected starters and bench depth, then take a configurable percentile of the remaining pool. This is a lower replacement threshold and often produces larger VORP values.

Neither definition is universal truth. Comparing them shows how assumptions about bench behavior change value-based drafting.

## What is learned versus configured?

- Scoring and eligibility are configured facts.
- Replacement level is a transparent heuristic derived from projections and league shape.
- Future player production will be learned by later models.
- Draft availability will be estimated separately from production.
- A future recommendation will combine these pieces and label each contribution.
