# Assumptions

1. Phase 3 was validated on August 5, 2026. The newest completed NFL season is treated as 2025 and the first live prediction season as 2026.
2. Python 3.11 is used locally because the installed Python 3.14 runtime is newer than the supported range selected for this data stack.
3. The first release is a local, single-user redraft tool. Cloud scale, authentication, and mobile clients are out of scope.
4. nflverse is the historical performance and identity backbone. Play-by-play is not required for the first model.
5. ESPN ADP and league history arrive through user-supplied files. The project will not scrape ESPN.
6. A display-name match is never treated as a confirmed player identity without a source identifier or recorded confidence.
7. No representative league-history dataset is assumed. Championship probabilities remain disabled until an evidence-based minimum sample policy is implemented and satisfied.
8. Synthetic data is allowed only in labeled tests/demos and is excluded from production training by default.
9. Network failures should preserve prior snapshots and give a useful offline-reuse instruction.
10. R and Quarto are optional. Neither is currently installed, so Python implementation is not blocked.
11. PFR game-level snap counts distributed by nflverse are the Phase 3 participation source. An active game requires positive offense, defense, or special-teams snaps; roster status and weekly-row presence are not substitutes.
12. A feature row from season `t` predicts `t+1`. September 1 of the prediction season is the logical preseason cutoff. The 2026 archive acquisition timestamp is retained as provenance, not represented as historical availability.
13. Historical weekly or snap-count position/team evidence takes precedence. Static identity position is eligible only when the identity snapshot was acquired on or before the row's September 1 cutoff. Static birth, rookie, draft, and height fields retain source-dataset provenance. Weight remains available in the identity table but is excluded from historical features until its time semantics are established; current team, current experience, and active status are also excluded.
14. The August 2026 identity snapshot predates the September 1, 2026 live cutoff, so it safely supports live 2026 static-position fallbacks. It is not backfilled into historical entry cohorts. Historical rookie baseline performance remains unavailable until the project has a historical preseason-position archive.
15. Phase 3 baselines are deterministic heuristics, not trained ML. Current 2026 ADP is not used in historical evaluation because no cutoff-safe historical snapshot archive exists. Statistical and machine-learning model training begins only in Phase 4.
