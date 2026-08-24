# Phase 5 ADP Movement and Availability Evaluation

Status: **PASSED**

## Validated foundation

- Build fingerprint: `a845725d5bd5dedd27302ab926c91a88aaaa42ef7e91d463a867fe1df11c439e`
- Snapshot-data fingerprint: `2afe3ef5fc249bfadfcd87bef010d391641b54f6c80ed0955c183647ba43d31a`
- Production snapshots: 6
- Independent capture timestamps: 3
- Canonical ADP observations: 2795
- Mapped / unresolved / excluded identity rows: 2137 / 658 / 0
- Movement feature rows: 2795
- Movement baseline rows: 8385
- Availability parameter rows: 2795

## Honest capability status

- Persistence forecasts ready: 2795
- Linear-trend forecasts ready: 0
- Exponentially weighted forecasts ready: 0
- Movement: `persistence_active_trends_insufficient_history`
- Availability: `distribution_baseline_active_uncalibrated`
- Supervised model: `unavailable_insufficient_dated_snapshots`
- Calibration: `unavailable_no_linked_draft_outcomes`

## Availability evidence

- Source standard-deviation or min/max rows: 246
- Configured fallback rows: 2549

Probabilities use a continuity-corrected normal pick distribution. Source-reported standard deviation wins, then a min/max-derived scale, then a labeled versioned fallback. The result is conditional on the player still being available at the current pick.

## Quality notes

- 658 player rows remain unresolved; availability is keyed to source IDs and is not joined by display name.
- Availability probabilities are distribution-based and uncalibrated because real draft outcomes are not yet archived.

## Phase boundary

No draft recommendation, draft state, Monte Carlo simulation, or supervised availability model is produced in Phase 5.
