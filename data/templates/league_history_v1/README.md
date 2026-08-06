# League History v1 Template Bundle

This folder defines the manual `league-history-v1` package. The CSV files intentionally contain headers only. Do not enter personal data into this tracked template folder.

## Privacy stop

Before editing anything:

1. Copy this entire folder to a private working location outside the repository.
2. Prefer a location that is not synchronized by OneDrive, Dropbox, Google Drive, a corporate backup agent, or another cloud service.
3. Replace league names, owner names, usernames, email addresses, and team names with pseudonymous IDs before importing.
4. Keep any private name-to-ID crosswalk outside both the repository and the synchronized folder. The application does not need that crosswalk.

The application does not transmit an uploaded package. That does not prevent Windows, OneDrive, or backup software from synchronizing the folder that contains it. Git ignores generated raw and warehouse data, but `.gitignore` is not a cloud-sync control.

## Package contents

| File | Requirement | One row per | Purpose |
|---|---|---|---|
| `package.json` | Required | Package | Declares the contract version, package ID, source, privacy assertion, and included files. |
| `league_rules.csv` | Required | League-season | Exact draft, roster, scoring, and playoff settings. |
| `draft_picks.csv` | Required | Overall pick | Complete original draft recap for every team. |
| `team_outcomes.csv` | Required | Team and league-season | Final standings and outcome labels for every team. |
| `weekly_rosters.csv` | Optional | Team, week, and player | Actual weekly roster and starter evidence. |
| `matchups.csv` | Optional | Team and week | Weekly score and opponent evidence. |
| `transactions.csv` | Optional | Transaction | Waiver, free-agent, drop, and trade evidence when available. |

Keep the CSV headers exactly as supplied. Required files must contain data rows. Optional files may remain header-only; leave their `included` value as `false` in `package.json`. Set it to `true` only after adding rows.

## Edit `package.json`

- Keep `schema_version` exactly `league-history-v1`.
- Replace `package_id` with a stable pseudonymous value such as `league_alpha_history_2021_2025_v1`.
- Set `created_at` to the UTC time when the package was assembled.
- Use a short source label such as `espn_manual`.
- Keep `contains_personal_identifiers` set to `false`. This is an assertion that pseudonymization is complete, not an instruction for the importer to remove identifiers.
- Do not add credentials, cookies, profile URLs, owner names, avatars, chat, or private ID mappings.

## Stable identifiers

Use one `league_season_id` everywhere for the same league and completed season, for example `league_alpha_2024`. Use a different ID for another season. Use stable pseudonymous team IDs such as `team_01`; if the same franchise appears across seasons, reusing its pseudonymous ID makes longitudinal descriptions possible.

`source_player_id` should be a public platform player ID when one is available. Never place an owner or account ID in that field. A player name and position may be retained as review evidence, but the importer must not silently accept a display-name match as a canonical player mapping.

## Required data examples

The following snippets are illustrative documentation, not production rows and not a complete import package.

### League rules

`scoring_json` uses the scoring field names from `configs/example_ppr_12_team.yaml`. `starter_slots_json` stores direct starters plus explicit FLEX or SUPERFLEX eligibility. A conceptual value is:

```json
{
  "QB": 1,
  "RB": 2,
  "WR": 3,
  "TE": 1,
  "FLEX": {"count": 2, "eligible": ["RB", "WR", "TE"]}
}
```

For CSV, the JSON must occupy one quoted cell and its internal quotation marks must be doubled. For example:

```csv
"{ ""QB"": 1, ""RB"": 2, ""WR"": 3, ""TE"": 1, ""FLEX"": {""count"": 2, ""eligible"": [""RB"", ""WR"", ""TE""]} }"
```

Do not add commas outside the quoted JSON cell. Spreadsheet software normally performs this escaping when a workbook is saved as CSV, but reopen the CSV in a text editor to verify it.

### Draft picks

- Include every original pick from every team, not only your roster.
- `overall_pick` must be unique within a league-season and start at 1.
- `round` and `draft_slot` must agree with the league's draft order.
- Use `true` or `false` for keeper and autopick flags. Leave a value empty only when it is genuinely unknown.
- Use an ISO 8601 timestamp for `picked_at` when it is available; otherwise leave it empty.

### Team outcomes

- Include every team, not only playoff teams or the champion.
- Preserve the final regular-season record and points exactly as shown by the source.
- Use `true` or `false` for `made_playoffs` and `is_champion`.
- There should be exactly one champion for a completed conventional league-season unless the source explicitly records a different result.
- Leave unavailable values empty. Never invent standings, seeds, or points.

## Collecting from ESPN or another manual source

Platform labels and menus can change, so use the visible completed-season pages rather than login automation or undocumented endpoints:

1. Select one completed season in league history.
2. Record team count, draft type/date/rounds, roster slots, scoring settings, and playoff settings in `league_rules.csv`.
3. Open the draft recap or draft results and transcribe every pick into `draft_picks.csv`. Verify that the number of rows agrees with the league's completed draft.
4. Open final standings and the playoff bracket. Record every team's regular-season record, points, seed, playoff result, final place, and champion status in `team_outcomes.csv`.
5. Optionally collect weekly rosters, matchup scores, and transactions. These enrich management analysis but are not required for the first draft-only report.
6. Repeat for every completed season you can obtain. Do not select only winning seasons, your own teams, or memorable drafts.

Do not supply ESPN credentials, session cookies, browser storage, or private account exports. If a page offers a print or download option, save it only as a private reference and transcribe the documented fields into these templates.

## Final checks and ZIP layout

Before upload:

- confirm all team and league labels are pseudonymous;
- confirm the three required files contain all teams and all picks for each included season;
- confirm IDs match across every file;
- confirm JSON cells parse and CSV headers are unchanged;
- confirm optional `included` flags match the files containing rows; and
- retain missing data as blank rather than replacing it with zero.

Create a ZIP whose root contains `package.json` and the CSV files directly:

```text
league_history.zip
|-- package.json
|-- league_rules.csv
|-- draft_picks.csv
|-- team_outcomes.csv
|-- weekly_rosters.csv
|-- matchups.csv
`-- transactions.csv
```

Do not add nested ZIP files, executables, credentials, screenshots, private crosswalks, or unrelated exports.

## What happens after upload

The safe workflow is archive, validate, review, normalize, and then describe. A fatal validation result leaves canonical warehouse tables unchanged. An exact package re-upload is identified by its content hash and must not duplicate canonical rows. A corrected package is a new immutable archive. Conflicting logical keys must be reviewed rather than silently overwritten.

Uploaded history can support descriptive roster-construction and draft-only reports. It does not automatically authorize playoff or championship model training, and it never creates a calibrated championship probability by itself.
