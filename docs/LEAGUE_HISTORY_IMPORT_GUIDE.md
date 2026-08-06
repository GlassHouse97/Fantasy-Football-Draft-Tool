# League History Import Guide

Phase 8 turns completed personal league histories into validated canonical rows and descriptive draft reports. It does not train a playoff or championship model. Start with the header-only [league-history-v1 template bundle](../data/templates/league_history_v1/README.md).

## The safe workflow

```text
private source pages
    -> pseudonymized working copy outside the repository
    -> immutable local archive and SHA-256 manifest
    -> package validation and quality report
    -> reviewed player identities
    -> idempotent canonical load
    -> descriptive roster-construction and draft-only reports
    -> read-only future-model readiness gate
```

A fatal package error must leave canonical warehouse tables unchanged. Re-uploading identical bytes must not duplicate canonical rows. Corrected contents create a new immutable archive; conflicting logical keys require review instead of silent replacement.

## Required and optional evidence

| File | Status | Enables |
|---|---|---|
| `package.json` | Required | Versioned contract, source metadata, privacy assertion, and file declarations. |
| `league_rules.csv` | Required | Ruleset normalization, exact scoring, roster demand, and pick-count validation. |
| `draft_picks.csv` | Required | Draft-capital, positional construction, identity review, and draft-only scoring. |
| `team_outcomes.csv` | Required | Descriptive standings, playoff, placement, and champion comparisons. |
| `weekly_rosters.csv` | Optional | Actual weekly starter and roster-management descriptions. |
| `matchups.csv` | Optional | Weekly scoring and opponent context. |
| `transactions.csv` | Optional | Waiver, free-agent, drop, and trade context. |

The first draft-only report does not require transactions or actual weekly rosters. It reconstructs what the originally drafted players could have produced under the recorded rules. Actual manager decisions and post-draft acquisitions are separate evidence.

## Privacy and pseudonymization

The app does not send a package to an external service. This repository currently sits in a OneDrive path, however, so local files may still be synchronized by OneDrive, Windows backup, or corporate tooling. Pseudonymize before selecting a file in the app.

Use IDs such as:

- `league_alpha_2024` for one league-season;
- `team_01` through `team_12` for teams; and
- `league_alpha_history_2021_2025_v1` for a package.

Stable team pseudonyms across seasons are useful when the same franchise returns. Store the private mapping from real names to these IDs outside the repository and outside synchronized storage. The application neither needs nor should receive that mapping.

Remove owner names, team names, usernames, email addresses, avatars, profile URLs, chat, credentials, cookies, browser storage, and unrelated screenshots. Public football player IDs are permitted in `source_player_id`; personal account or owner IDs are not.

## Manual collection walkthrough

ESPN and other platforms may change menu names. Use visible completed-season league-history pages and documented export or print controls when available. Do not use login automation or undocumented endpoints.

### 1. League rules

For each completed season, record:

- source platform and season;
- team count, draft type, date, and rounds;
- direct starters, FLEX/SUPERFLEX eligibility, bench, and IR;
- scoring values; and
- playoff teams and schedule.

Use the scoring field names from `configs/example_ppr_12_team.yaml`. A conceptual `starter_slots_json` value is:

```json
{
  "QB": 1,
  "RB": 2,
  "WR": 3,
  "TE": 1,
  "FLEX": {"count": 2, "eligible": ["RB", "WR", "TE"]}
}
```

CSV requires the whole JSON value to be quoted and each inner quote doubled. Do not simplify FLEX or SUPERFLEX eligibility to a single position.

### 2. Complete draft recap

Open draft results and capture every overall pick. Do not collect only your team. Preserve pick number, round, draft slot, pseudonymous team ID, player evidence, keeper/autopick status, and timestamp when known.

Before continuing, reconcile the row count with the recorded team count and rounds. Keepers may affect the relationship, so record them explicitly rather than forcing missing draft rows to look complete.

### 3. Every team outcome

Use final standings and the playoff bracket to record every team's wins, losses, ties, points for/against, seed, playoff qualification, final place, and champion flag. Include non-playoff teams. Keep truly unavailable fields blank; zero is a real value and must not mean “unknown.”

### 4. Optional weekly evidence

Weekly rosters, matchups, and transactions help distinguish original draft quality from lineup and waiver management. Collect them only when complete, understandable evidence is available. Partial optional data is still allowed, but its coverage must be reported and analyses that need it must remain unavailable.

### 5. Repeat without cherry-picking

Collect all accessible completed seasons and all teams. Selecting only your best seasons, champions, or currently active members creates selection bias. A single league's history is still useful for personal descriptive learning, but it is not representative training data.

## IDs and cross-file consistency

- `league_season_id` must identify exactly one league and season and must match across every CSV.
- `team_id` must be pseudonymous and must match draft, outcome, roster, matchup, and transaction rows.
- `overall_pick` must be unique within a league-season.
- `transaction_id` must be unique within a league-season.
- Prefer a stable public platform player ID. Player name and position support review but never authorize a silent name join.
- Use ISO 8601 dates and timestamps when the source provides them.
- Use lowercase `true` and `false` for Boolean fields.

## What validation should report

The importer produces a human-readable and downloadable quality report with:

- archive hash, package ID, contract version, and files discovered;
- row counts and required-field failures by file;
- duplicate logical keys and cross-file ID conflicts;
- invalid JSON, dates, Booleans, scoring fields, or lineup slots;
- impossible pick numbers, rounds, slots, team counts, and outcome combinations;
- unresolved or ambiguous football player identities;
- completeness for rules, draft picks, outcomes, and optional evidence;
- fatal errors versus warnings; and
- the exact file, row, field, issue code, explanation, and suggested correction.

Readiness is staged:

1. **Archived** means immutable bytes and a manifest exist.
2. **Validated** means the package contract and required data have no fatal errors.
3. **Normalized** means canonical rows were loaded idempotently.
4. **Descriptive-ready** means the required linked evidence exists for a named report.
5. **Outcome-model ready** remains false until the separate written gate passes.

An archived package is not automatically valid. A valid package can still require identity review before a player-linked report is ready.

## Troubleshooting

### The JSON column split into several CSV columns

Quote the entire JSON cell and double every internal quotation mark. Reopen the saved CSV in a text editor and verify the header and column count.

### Team or league IDs do not match

Use find/replace in the private working copy so the same pseudonym appears in every file. Do not solve the mismatch by introducing real names.

### Pick count does not equal teams multiplied by rounds

Check keepers, traded picks, skipped slots, and whether the source recap is complete. Preserve the real evidence and allow validation to explain the discrepancy; do not invent rows.

### A player cannot be mapped

Retain source player ID, name, position, and source evidence. Use the generated identity-review workflow. Never change the row to a different player merely to clear an error.

### Optional data is incomplete

Leave unavailable values blank and keep the quality warning. Analyses that require that evidence should display unavailable rather than zero.

### A corrected package conflicts with an earlier load

Do not edit the archived package. Create a corrected package with a new package ID/version and preserve the validation report. The loader must reject ambiguous conflicting authority rather than silently overwrite history.

## Descriptive use and model lock

Validated history may describe positional picks by round, draft capital, first position selected, starter coverage, bench depth, ADP value, projected replacement value, volatility, bye concentration, optimal drafted-player weekly lineups, best-ball points, drafted starter games, draft-only points percentile, and replacement burden.

These are descriptions and associations. They do not prove that a draft strategy causes wins. Draft-only outcomes intentionally omit waivers, trades, and manager start/sit decisions.

The proposed conservative minimum for even considering a future league-outcome evaluation is:

- 100 independent league-seasons;
- 1,000 team-seasons;
- five completed seasons with chronological holdout support;
- at least 20 league-seasons in the validation season and 20 in the untouched test season;
- at least 95% complete required inputs and canonical player mappings; and
- at least 100 positive and 100 negative examples for each binary target.

Passing those counts would be necessary, not sufficient. Ruleset diversity, leakage prevention, representative sampling, calibration, and improvement over simple baselines must also be demonstrated. A nonlinear boosted model has a stricter proposed floor of 500 league-seasons, 5,000 team-seasons, and 500 examples in every target class. Phase 8 exposes no playoff or championship training action and produces no predicted championship percentage.
