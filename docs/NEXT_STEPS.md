# Next Steps

## Current product milestone

Phases 0 through 8 from the master specification are complete. The active follow-up milestone refocuses the technical foundation into the product the user originally requested: a redraft assistant that answers **who should I pick now?** from the players still available.

The main workflow is now:

1. Open **Draft Assistant**.
2. Choose a built-in roster preset, league size, and draft position for supported 2026 full-PPR, no-K/DST play.
3. Record every supported QB/RB/WR/TE pick in order, including opponents' selections.
4. When your team is on the clock, use **Best pick now** and compare its alternatives.
5. Check **Player rankings** for the searchable league-adjusted board; choose a quick top-N view or **All players**.
6. Use **Undo last pick** if the live board was entered incorrectly.

Start the app from `PS C:\Users\Chris D>`:

```powershell
cd "C:\Users\Chris D\OneDrive - Musco Food Corporation\Desktop\Portfolio Data\Fantasy Football AI"
.\.venv\Scripts\Activate.ps1
fantasy-draft app
```

The detailed walkthrough is in [Human Testing Guide](HUMAN_TESTING_GUIDE.md).

## What works now

- The default page is **Draft Assistant**, not a project-status dashboard.
- Quick start creates a persistent 2026 full-PPR snake draft from a roster preset, league size, draft position, and a name.
- The app records supported QB/RB/WR/TE picks, removes drafted players, follows snake order, persists on refresh, and supports one-click undo.
- A recommendation appears whenever the user's team is on the clock.
- The recommendation works from the published player projections even with no linked ADP rows.
- The recommendation considers P50 value over replacement, same-position drop-off, current roster fit, and exact league roster demand.
- The native dark Draft Night theme uses Inter body text, Outfit headings, stronger borders, and consistent QB/RB/WR/TE colors.
- The compact turn card, dominant best-pick card, smaller alternatives, and roster summary create a clear live-draft hierarchy.
- User turns show recommendation and roster first; opponent turns move the available-player table first so **Record taken** is immediately accessible.
- The available-player table supports search, position pills, a row-level action, and pinned action/rank/player columns while limiting the live view to essential fields.
- **Draft activity** now defaults to a real round-by-team snake board with position-colored cells, a highlighted user column, current-pick status, and an alternate chronological pick log.
- **Player rankings** works before creating a session, offers quick Top 50/100/200/300 and complete all-player views, pins rank/player, and ranks across positions by value over replacement rather than raw fantasy points.
- Honest rookie, ADP, and live-news notes remain visible through compact badges and expandable details instead of dominating the primary action area.
- Technical data, model, history, and rules tools remain available under **Advanced**.

Quick Start currently covers QB/RB/WR/TE/FLEX only. Kicker and team defense are not in the projection publication and cannot be recorded as placeholder picks, so Quick Start is not a complete live tracker for leagues that draft those positions. It offers Standard (2 WR, 1 FLEX) and WR/FLEX-heavy (3 WR, 2 FLEX) built-in no-K/DST presets; saved Advanced settings do not alter them. Another full-PPR QB/RB/WR/TE/FLEX/SUPERFLEX/bench roster must be saved in **League settings** and opened through **Technical draft room**. Other scoring systems, seasons, and keeper formats require a compatible projection publication or further implementation.

The current production foundation remains:

- 25,037 canonical players;
- 199,629 weekly-stat rows;
- 11,171 cutoff-safe player-season features and 9,804 historical targets;
- one validated Phase 4 publication with 24 registered models and a 1,367-player 2026 projection board; and
- 246 production ADP observations with transparent persistence and availability baselines.

## Two recommendation layers

The app now keeps two distinct contracts instead of blocking all advice behind market data.

### Projection-first guidance — usable now

This is the primary **Best pick now** experience. It uses only evidence already validated for the draft session:

- player P10/P50/P90 season projections;
- league-specific replacement levels;
- positional drop-off among available players;
- exact starter/FLEX/bench rules; and
- the user's current roster.

Its score is a transparent, uncalibrated decision baseline. It is not a championship, playoff, or calibrated win probability.

The board includes 233 live rookies whose rows are explicitly `rookie_heuristic_fallback_unvalidated`. They are point-only transparent heuristics with `P10=P50=P90` and unavailable risk estimates. They may appear in rankings or recommendations and must not be interpreted as validated uncertainty forecasts.

### Market-enhanced simulation — still gated

The Phase 6 Monte Carlo engine additionally models opponent selections and whether players may survive to the user's next pick. That contract correctly remains unavailable because 0 of 203 compatible QB/RB/WR/TE ADP rows currently have reviewed canonical mappings. Current ADP and next-pick timing are therefore unavailable for every compatible player. The configuration requires 100% compatible canonical market coverage, so all 203 rows must be reviewed correctly before this layer can become ready. The 43 archived PK/DEF rows remain outside the projected draftable-position scope.

To unlock that optional layer, review identities carefully and rebuild Phase 5:

```powershell
fantasy-draft data review-identities
fantasy-draft data apply-identity-overrides data\processed\identity\identity_review_queue.csv
fantasy-draft data review-identities
fantasy-draft data load-adp
fantasy-draft models build-adp-baselines --availability-config configs/adp_availability.yaml --output docs/PHASE_5_ADP_AVAILABILITY_EVALUATION.md
fantasy-draft data audit
fantasy-draft status
```

Do not apply the generated worksheet without verifying every player ID, decision, reviewer, timestamp, and required note. Name matching is not an accepted shortcut.

## Immediate human-test priorities

Use the app like a fantasy-football player rather than like its developer. Record:

- whether a new draft starts in under 30 seconds;
- whether the next action is obvious at every turn;
- whether entering an opponent pick is fast enough for a live draft;
- whether **Best pick now** explains the choice in useful football language;
- whether close alternatives are easy to compare;
- whether the turn card and user/opponent render order make the next action obvious;
- whether the position-colored snake board is fast to scan by round and team;
- whether pinned player columns remain useful while scrolling wide tables;
- whether drafted players disappear immediately;
- whether undo and browser refresh behave exactly as expected;
- which terms still feel technical;
- which details should be collapsed or removed; and
- which missing features would materially improve the next real draft.

The most important known limitation is live context: injury, suspension, and depth-chart updates are not wired into the model or UI. Check current player news before acting on any recommendation.

## Likely next product increments

Prioritize these from actual human-test evidence:

1. Improve search/keyboard speed and live pick entry.
2. Add optional favorites, fades, personal tiers, and projection overrides.
3. Add bye-week and team-stack context to the existing roster panel.
4. Add a supported live or import-based Sleeper/ESPN draft sync, with explicit authorization and failure handling.
5. Wire a reviewed current-news/injury input with provenance and timestamps.
6. Correctly review all 203 compatible ADP identities required to enable next-pick availability forecasts.
7. Add cheat-sheet export after the on-screen rankings flow is validated.

Do not start outcome/championship modeling automatically. That remains evidence-gated.

## Optional personal-history workflow

Personal history is not needed for draft recommendations. It supports only the separate descriptive League history workspace today.

Start with one complete, pseudonymized historical season outside the repository and preferably outside OneDrive:

1. Download the `league-history-v1` template from **Advanced → Data center**.
2. Fill every league rule, every original draft pick, and every team outcome.
3. Put `package.json` and the declared CSV files directly at the ZIP root.
4. Import the ZIP and read its quality report.
5. Review public player identities before applying mappings.
6. Build roster-history features and inspect **Advanced → League history**.

See [League History Import Guide](LEAGUE_HISTORY_IMPORT_GUIDE.md) and [User Data Checklist](USER_DATA_CHECKLIST.md).

## Outcome-model boundary

The existing documented minimum remains 100 analysis-ready league-seasons, 1,000 team-seasons, five seasons, chronological validation/test coverage, at least 95% completeness/mapping, and usable target balance. Those counts are necessary rather than sufficient. A future authorized modeling phase would still require leakage review, representative sampling, ruleset diversity, calibration, and cohort reliability.

## Publication status

Phase 8 PR #8 was merged to `main` at commit `f321c325e0620cb43cae48edc098c3084a040dca`. After the GitHub Actions service outage recovered, Phase 6 pull-request run `31118319345`, the Phase 7 pull-request rerun and `main` retrigger, and the Phase 8 pull-request and resulting `main` runs all received real hosted runners and completed green. On August 14, 2026, the affected Phase 6 `main` run `31119062454` was safely canceled and rerun; attempt 2 received hosted job `94857281821` and completed green in 1 minute 49 seconds with Ruff, mypy, and pytest passing. Later green descendant `main` runs also include the Phase 6 code.

The recommendation-first milestone passes Ruff, strict mypy across 97 source files, all 299 repository tests, the production audit across eight manifests and 12 immutable raw files, and real browser QA of quick start, user/opponent table picks, search reset, persistence, rankings, help, and undo. Its temporary browser-test draft was removed and all local-state counters returned to zero. Hosted pull-request and resulting `main` evidence remain the publication gate; GitHub Actions is the live source of truth.
