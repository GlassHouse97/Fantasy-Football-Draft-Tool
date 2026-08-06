# Next Steps

## Current milestone

Phases 0 through 8 from the master specification are implemented locally. Phase 8 is the final planned phase, not the start of automatic championship modeling. It adds the safe league-history framework, descriptive reports, and the written evidence gate that prevents outcome training without enough real data.

The local app now has eight workspaces:

| Route | Current status |
|---|---|
| `/status` | Ready; reports actual capability, evidence, blockers, and next actions. |
| `/data-center` | Ready; inventories data, runs the audit, downloads the history template, and archive-first imports validated history ZIPs. |
| `/league-history` | Ready; currently shows the truthful empty state because no personal history has been imported. |
| `/model-lab` | Ready and read-only; player-model training/publication remains a deliberate CLI workflow. |
| `/league-setup` | Ready; saves exact rules and supports fingerprint-checked YAML backup/restore. |
| `/draft-room` | Manual state ready; recommendation/simulation remains ADP-identity-gated. |
| `/post-draft` | Ready for complete or incomplete persisted sessions with explicit limitations. |
| `/learning-center` | Ready; previews local guides and notebook Markdown without executing code. |

Start the app from `PS C:\Users\Chris D>`:

```powershell
cd "C:\Users\Chris D\OneDrive - Musco Food Corporation\Desktop\Portfolio Data\Fantasy Football AI"
.\.venv\Scripts\Activate.ps1
fantasy-draft app
```

Use [the Human Testing Guide](HUMAN_TESTING_GUIDE.md) for the first click-through. Record confusing labels, unexpected behavior, unavailable-feature explanations, and the exact action/error when something fails. That usability pass is the safest next iteration after Phase 8.

## What is already usable without personal history

You do not need a personal league-history package to open the app, inspect player models, save league rules, create a draft session, or manually record picks. The session is persisted in DuckDB and verified through event replay, so a browser refresh does not erase the draft.

The current public-data foundation remains intact:

- 25,037 canonical players and 199,629 weekly-stat rows;
- 11,171 cutoff-safe player-season features and 9,804 historical targets;
- one validated Phase 4 run with 24 registered routes and a 1,367-player 2026 board; and
- 246 production ADP observations with transparent persistence/availability baselines.

Live recommendation and Monte Carlo actions are still correctly locked because 0 of 203 compatible QB/RB/WR/TE ADP rows have reviewed canonical mappings. The 43 archived PK/DEF rows remain outside this ruleset's recommendation coverage. Manual drafting is a separate capability and remains usable.

To unlock reviewed market linkage, carefully complete the existing identity workflow and rebuild Phase 5 before creating a new frozen session:

```powershell
fantasy-draft data review-identities
fantasy-draft data apply-identity-overrides data\processed\identity\identity_review_queue.csv
fantasy-draft data review-identities
fantasy-draft data load-adp
fantasy-draft models build-adp-baselines --availability-config configs/adp_availability.yaml --output docs/PHASE_5_ADP_AVAILABILITY_EVALUATION.md
fantasy-draft data audit
fantasy-draft status
```

Do not apply the generated worksheet without checking every decision, canonical player ID, reviewer, timestamp, and required note.

## Optional personal-history workflow

Production currently contains 0 league-history packages, league-seasons, team outcomes, roster-construction rows, and drafted-only metrics. No real personal data is committed to the repository.

Start with one complete historical season to learn the workflow:

1. Download the `league-history-v1` template in Data Center.
2. Move the working copy outside the repository and preferably outside OneDrive.
3. Replace league, team, owner, username, and account identifiers with stable pseudonymous IDs.
4. Fill every league rule, every original draft pick, and every team outcome for that season.
5. Put `package.json` and the declared CSV files directly at the ZIP root.
6. Import the ZIP in Data Center and read/download its quality report.
7. Run `fantasy-draft data review-identities`; approve only verified public football-player IDs.
8. Apply reviewed decisions, refresh the queue, and run `fantasy-draft features build-roster-history`.
9. Run `fantasy-draft data audit` and inspect `/league-history`.
10. Repeat for all accessible completed seasons without selecting only your team, champions, or memorable drafts.

The full field walkthrough is in [League History Import Guide](LEAGUE_HISTORY_IMPORT_GUIDE.md) and the collection checklist is in [User Data Checklist](USER_DATA_CHECKLIST.md).

## Why outcome training remains locked

One personal league can be useful for descriptive learning but is not independent representative evidence for a calibrated playoff/championship model. Phase 8 requires, at minimum, 100 analysis-ready league-seasons, 1,000 team-seasons with roster features and target evidence, five seasons, chronological validation/test coverage, 95% completeness/mapping, and balanced target classes. A nonlinear model has a higher floor.

Those counts are necessary, not sufficient. A later authorized modeling phase would still need leakage review, representative sampling, ruleset diversity, chronological baseline comparison, calibration, and cohort reliability. Phase 8 has no outcome-training button and produces no playoff/championship probability.

## Quality and publication boundary

The current production warehouse has been migrated additively and the CLI data audit passes across eight manifests and 12 verified raw files. The focused Phase 8 integration suite covers unsafe ZIPs, privacy rejection, immutable archives, equivalent-package deduplication, canonical conflicts, identity review/reconciliation, additive migrations, partial-week fail-closed behavior, app pages, and model-gate locks. Final repository-wide and browser evidence is recorded in [the Phase 8 evaluation](PHASE_8_LEAGUE_HISTORY_EVALUATION.md).

GitHub Actions hosted evidence for Phases 6 and 7 is still pending due the reported Actions outage. Phase 8 commit `d593fe4` is pushed on `codex/phase-8-league-history`, and draft PR #8 is open against `main`. No Phase 8 workflow registered while GitHub Status reported an Actions major outage. The recovery reminder should track all three milestones and report only real hosted results. PR #8 remains unmerged until green hosted CI exists unless the outage persists and a separate explicit, documented decision is made.

## After Phase 8

There is no Phase 9 in the current master specification. The next work should be driven by evidence from:

- your human usability test;
- reviewed ADP identity mappings and live draft rehearsals;
- the first real pseudonymized history package and its quality report; and
- genuine data gaps uncovered by those workflows.

Likely follow-up work is usability polish, platform-specific documented import helpers, additional historical evidence coverage, and bug fixes. It is not automatic expansion into outcome modeling.
