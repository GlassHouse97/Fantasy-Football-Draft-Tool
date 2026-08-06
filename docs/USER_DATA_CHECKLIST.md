# User Data Checklist

This checklist separates the data the application can archive automatically from the historical league data only you can supply. The detailed package instructions are in [League History Import Guide](LEAGUE_HISTORY_IMPORT_GUIDE.md).

## Privacy check before personal history

- [ ] Work from a copy of `data/templates/league_history_v1/`, not the tracked template files.
- [ ] Put the working copy outside this repository and, preferably, outside OneDrive or another synchronized folder.
- [ ] Replace league names, owner names, usernames, email addresses, and team names with stable pseudonymous IDs.
- [ ] Keep the private name-to-ID crosswalk outside both the repository and the synchronized folder.
- [ ] Remove credentials, cookies, profile URLs, avatars, chat, screenshots, and unrelated exports.
- [ ] Confirm `contains_personal_identifiers` is `false` in `package.json` only after completing that review.

The application does not transmit the package, but Windows, OneDrive, or backup software may synchronize its containing folder. Git ignore rules prevent accidental Git commits; they do not disable cloud sync.

## One-time project setup

1. Install Python 3.11 and create the local `.venv` using the README commands.
2. Run `fantasy-draft data init-warehouse`.
3. Download one small completed nflverse season as a smoke test, then expand to the configured completed-season range.
4. Run `fantasy-draft data load-nflverse` and `fantasy-draft data review-identities`.
5. Review `data/processed/identity/identity_review_queue.csv`. Use `confirmed`, `remapped`, or `dismissed`; add `reviewed_at` and `reviewer`. Remaps and dismissals require a note.
6. Apply decisions with `fantasy-draft data apply-identity-overrides data\processed\identity\identity_review_queue.csv`, refresh the queue, and run `fantasy-draft data audit`.
7. Normalize existing production ADP archives with `fantasy-draft data load-adp`.
8. Build the transparent market baselines, then run the data audit and project status commands.
9. Optionally install R and Quarto for companion analyses. They are not required by the Python application.

The identity worksheet is generated data and should not be committed. Its applied copy is archived unchanged under `data/raw/identity_overrides/` with a SHA-256 manifest. Reapplying the same decisions is idempotent.

## Historical league package: what to collect

Collect every team from every completed season available. Do not submit only your roster, playoff teams, champions, or successful seasons.

| Dataset | Required? | What you must collect |
|---|---|---|
| League rules | Yes | One row per league-season: platform, season, team count, draft format/date/rounds, roster slots, scoring, and playoff settings. |
| Draft picks | Yes | The complete original draft recap for every team and every overall pick. |
| Team outcomes | Yes | Every team's final regular-season record, points, seed, playoff qualification, final place, and champion flag. |
| Weekly rosters | Optional | Each team's roster and starter/bench status for each week. |
| Matchups | Optional | Each team's weekly opponent, score, and playoff indicator. |
| Transactions | Optional | Waiver, free-agent, drop, and trade events when available. |

For each completed season:

1. Select the season in ESPN league history or the equivalent source page.
2. Transcribe league and scoring settings into `league_rules.csv`.
3. Transcribe every row of the draft recap into `draft_picks.csv`.
4. Transcribe final standings and playoff results for every team into `team_outcomes.csv`.
5. Add optional weekly data only when it is available without inventing values.
6. Verify that `league_season_id` and pseudonymous `team_id` values match across files.
7. Prefer a public platform player ID. A display name is review evidence, not an automatically approved mapping.
8. ZIP `package.json` and the CSV files at the root of the archive, then use the Data Center history workflow.
9. Download and keep the package quality report. Correct fatal errors in a new package rather than editing archived raw evidence.
10. Review unresolved players before relying on canonical draft-only reports.

## Repeat during draft season

1. Archive dated FFC ADP snapshots. Daily is sufficient because the source updates daily; never overwrite an earlier capture.
2. Export or manually prepare ESPN ADP using `data/templates/espn_adp_snapshot_template.csv`.
3. Run `fantasy-draft data load-adp`; it verifies raw hashes, collapses duplicate manifests, skips labeled fixtures by default, and loads new production snapshots idempotently.
4. Refresh the identity queue after new FFC or ESPN captures and review every unresolved or ambiguous player mapping. A suggested name match is not an approved mapping.
5. Rebuild the market baselines, then run `fantasy-draft data audit` and `fantasy-draft status`.
6. Add current injury, suspension, and depth-chart adjustments with the manual template.
7. Confirm exact scoring, team count, starting slots, FLEX/SUPERFLEX eligibility, bench, and draft position before creating a frozen draft session.

## Repeat after each completed season

1. Add the newly completed nflverse season.
2. Add the full league rules, original draft recap, and all-team outcomes to a new immutable history package.
3. Add optional rosters, matchups, and transactions when available.
4. Validate, review player identities, normalize idempotently, and rebuild descriptive reports.
5. Retrain existing player models only after their own chronological and leakage gates pass.
6. Do not train a league-outcome model merely because another season was added.

## Proposed conservative league-outcome training gate

Playoff and championship training remains locked. A future implementation may consider unlocking an evaluation workflow only after all of these minimums are satisfied:

- at least 100 independent league-seasons;
- at least 1,000 team-season rows;
- at least five completed seasons supporting a chronological holdout;
- at least 20 league-seasons in the validation season and 20 in the untouched test season;
- at least 95% completeness for required inputs and canonical player mappings; and
- for each binary target, at least 100 positive and 100 negative examples.

These are proposed necessary minimums, not proof that a model is valid. Ruleset diversity, leakage checks, cohort reliability, calibration, and performance against transparent baselines must still pass. A nonlinear boosted model has a deliberately stricter proposed threshold of 500 league-seasons, 5,000 team-seasons, and 500 examples in every target class. There is no training control in the Phase 8 history workflow.

## Important boundaries

- Do not upload ESPN credentials, cookies, browser storage, or private account data.
- Do not publish raw personal league files or a private pseudonym crosswalk.
- Do not map a player by display name alone. Confirm the canonical ID through the review workflow.
- Leave FFC team-defense rows excluded; `DEF`, `DST`, and `D/ST` are team units, not canonical players.
- Never fabricate missing ADP history, injuries, rules, picks, weekly activity, or league outcomes.
- Do not treat many players from one snapshot as independent time observations.
- Treat next-pick availability as an uncalibrated distribution baseline until linked real outcomes support calibration.
- Treat historical roster-construction charts as descriptive association, not causal evidence.
- Draft-only outcomes intentionally exclude waiver, trade, and start/sit management effects.
- Championship probabilities remain unavailable until a later model passes the written sufficiency, validation, chronological evaluation, and calibration gates.
