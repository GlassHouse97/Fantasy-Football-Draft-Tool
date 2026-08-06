# Phase 5 ADP Movement and Availability Evaluation

Status: **PASSED**

## Validated foundation

- Build fingerprint: `3446513dfe4b122079ba1ed89b6517821d35cac48821ff1631e25a77f6dd3b6b`
- Snapshot-data fingerprint: `44624854b5c45f80fb0017e6ecdb52c972d4389236d35131b2dbfccb9a0447f2`
- Production snapshots: 1
- Independent capture timestamps: 1
- Canonical ADP observations: 246
- Mapped / unresolved / excluded identity rows: 0 / 246 / 0
- Movement feature rows: 246
- Movement baseline rows: 738
- Availability parameter rows: 246

## Honest capability status

- Persistence forecasts ready: 246
- Linear-trend forecasts ready: 0
- Exponentially weighted forecasts ready: 0
- Movement: `persistence_active_trends_insufficient_history`
- Availability: `distribution_baseline_active_uncalibrated`
- Supervised model: `unavailable_insufficient_dated_snapshots`
- Calibration: `unavailable_no_linked_draft_outcomes`

## Availability evidence

- Source standard-deviation or min/max rows: 246
- Configured fallback rows: 0

Probabilities use a continuity-corrected normal pick distribution. Source-reported standard deviation wins, then a min/max-derived scale, then a labeled versioned fallback. The result is conditional on the player still being available at the current pick.

## Quality notes

- 246 player rows remain unresolved; availability is keyed to source IDs and is not joined by display name.
- Linear and exponentially weighted movement baselines require at least three dated observations per source player; persistence remains active.
- Availability probabilities are distribution-based and uncalibrated because real draft outcomes are not yet archived.

## Phase boundary

No draft recommendation, draft state, Monte Carlo simulation, or supervised availability model is produced in Phase 5.
