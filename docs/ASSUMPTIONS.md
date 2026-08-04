# Assumptions

1. The current date is August 4, 2026. The newest completed NFL season is treated as 2025 and the first prediction season as 2026.
2. Python 3.11 is used locally because the installed Python 3.14 runtime is newer than the supported range selected for this data stack.
3. The first release is a local, single-user redraft tool. Cloud scale, authentication, and mobile clients are out of scope.
4. nflverse is the historical performance and identity backbone. Play-by-play is not required for the first model.
5. ESPN ADP and league history arrive through user-supplied files. The project will not scrape ESPN.
6. A display-name match is never treated as a confirmed player identity without a source identifier or recorded confidence.
7. No representative league-history dataset is assumed. Championship probabilities remain disabled until an evidence-based minimum sample policy is implemented and satisfied.
8. Synthetic data is allowed only in labeled tests/demos and is excluded from production training by default.
9. Network failures should preserve prior snapshots and give a useful offline-reuse instruction.
10. R and Quarto are optional. Neither is currently installed, so Python implementation is not blocked.
