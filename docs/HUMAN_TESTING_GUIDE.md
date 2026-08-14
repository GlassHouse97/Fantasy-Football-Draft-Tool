# Human Testing Guide

This guide is the hands-on walkthrough for the local redraft assistant. It separates three different jobs that are easy to confuse:

1. **Use the app for a draft** with rules, projections, a persistent draft board, and descriptive post-draft reporting.
2. **Maintain public NFL and ADP evidence** used by the player and draft-market components.
3. **Optionally import personal league history** for roster-construction and draft-only historical descriptions.

Personal league history is not required to open the app, see player rankings, get projection-based pick advice, or run a manual draft. It is required only for the historical workspace, and much more independent history would be required before a league-outcome model could be considered.

## Start the app

From `PS C:\Users\Chris D>`:

```powershell
cd "C:\Users\Chris D\OneDrive - Musco Food Corporation\Desktop\Portfolio Data\Fantasy Football AI"
.\.venv\Scripts\Activate.ps1
fantasy-draft app
```

Keep that PowerShell window open while testing. Streamlit prints the local URL, normally `http://localhost:8501`. Stop the app with `Ctrl+C` when finished.

If the command is not recognized, use the module entry point from the activated environment:

```powershell
python -m streamlit run app.py
```

## Restore a clean testing baseline

Open **Advanced → System status**. Its collapsed **Local testing controls** section includes a **Restore app defaults** button. The confirmation dialog shows the exact saved-setup, practice-draft, and pick counts and requires the phrase `RESTORE DEFAULTS` before it can run.

The restore removes only saved local league setups, practice draft sessions, their picks/events, and the current app session's widget state. It does **not** remove immutable raw archives, manifests, canonical players or weekly stats, ADP evidence, reviewed identity mappings, model artifacts, or imported league-history evidence. Other open browser tabs have separate session state and may briefly retain stale widget values until they rerun. If another browser tab changes local database state after the dialog opens, the transaction stops before deletion and requires a fresh confirmation. After restoration, League Setup again prefills the checked-in 12-team PPR reference rules without inserting a replacement database row.

Download a setup YAML first if you may want to reuse custom rules. The restore cannot recover deleted practice-draft state.

## Your first useful draft test

### 1. Start in Draft Assistant

The app now opens directly to **Draft Assistant**. Expand **Start a new redraft** and use:

- Draft name: any recognizable practice name;
- League size: your real league size, or 12 teams for the first test; and
- Your draft position: your slot in the snake draft.

Quick Start keeps the checked-in **2026 full-PPR** scoring and lets you choose **Standard (2 WR, 1 FLEX)** or **WR/FLEX-heavy (3 WR, 2 FLEX)**; both use 1 QB, 2 RB, 1 TE, and 7 bench spots. It does not use a setup saved under Advanced. This is currently a no-K/DST workflow: kicker and team defense are not projected and cannot be entered as placeholder picks, so use Quick Start only for a draft that does not select those positions.

The active publication contains 1,367 projection rows, including 233 live rookies that use an **unvalidated point-only heuristic fallback** because an honest historical preseason rookie-position cohort is unavailable. For those rows, `P10=P50=P90`, and risk is not estimated. They can appear in rankings and recommendations, but they do not have validated uncertainty intervals.

Select **Start draft** for this first walkthrough. For a full-PPR QB/RB/WR/TE/FLEX/SUPERFLEX/bench roster outside those two presets, save the rules in **Advanced → League settings** and create the session in **Advanced → Technical draft room**. Half-PPR, standard, other scoring changes, a different season, and keeper formats cannot use the active projection publication.

### 2. Use the recommendation when you are on the clock

At your pick, the top of the page should answer three questions without another screen:

1. Who is the best projected pick now?
2. Why is that player above the alternatives?
3. Is next-pick market timing available, or is it honestly missing?

The main recommendation combines the model's season projection, value above the league-specific replacement player, the drop to the next available player at that position, and fit with your current roster. It works without ADP. In the current production build, 0 of 203 compatible QB/RB/WR/TE market identities are reviewed, so ADP and the estimated chance that a player lasts to your next turn are unavailable for every compatible player. If reviewed linkage is added later, the app may show that timing; missing timing is never displayed as zero.

Use the main **Draft Player Name** button or any row's **Draft** button to record the pick.

### 3. Record every league pick

This is a manual live tracker for the supported no-K/DST preset. **Record every QB/RB/WR/TE selection in draft order, including opponents' picks—not only your picks.** The app determines the team on the clock from snake order. Each recorded player should immediately disappear from the available table. When the draft reaches your slot again, the recommendation must recalculate from the remaining players and your roster. Do not use this workflow for a league that drafts kicker, team defense, or another unsupported position, because those selections cannot currently be recorded or skipped honestly.

Test this sequence:

1. Draft the recommended player at your first pick.
2. Record several opponent picks using search and the row button.
3. Confirm drafted players disappear everywhere.
4. Use **Undo last pick** and confirm the player returns.
5. Refresh the browser and confirm the session and picks remain.
6. Continue until your next turn and compare the changed recommendation.

The app does not yet synchronize Sleeper or ESPN drafts. It also does not ingest live injury, suspension, or depth-chart news, so check a current news source before acting on a recommendation.

### 4. Check Player rankings

Open **Player rankings** before or during the practice draft. Change league size, search for players, and filter positions. Use a quick Top 50/100/200/300 view during normal comparison or choose **All players** when you need the complete filtered board. Overall rank should use value over replacement, not raw points across positions. That prevents a quarterback from automatically outranking every running back or receiver merely because quarterback scoring totals are larger.

Confirm each row clearly shows projection, position rank, tier, floor, ceiling, and replacement value. ADP is blank for all currently compatible players because reviewed market mappings are 0/203; the projection ranking should still work. For the 233 rookie heuristic rows, floor and ceiling equal the point estimate and the risk label is **Not estimated**—that equality is a limitation, not evidence of certainty.

### 5. Open Draft report

Open the report before and after completing a test draft. An incomplete report should identify itself as provisional. Check positional capital, lineup or roster coverage, market-value evidence, risk labels, and missing-data limitations. Missing ADP or uncertainty must remain unavailable rather than silently becoming zero.

### 6. Use Advanced only when you need it

The normal draft path should not require these pages:

- **League settings** retains the complete roster/scoring editor and YAML backup/restore.
- **Technical draft room** retains frozen-board, replay, and enhanced market-simulation diagnostics.
- **System status** shows capability gates and the protected local reset.
- **Data center** audits source files and handles optional history packages.
- **Model details** exposes chronological model evidence and player-level explanations.
- **League history** handles optional personal historical data.

If the core Draft Assistant forces you into one of these pages to answer “who should I pick?”, record that as a usability bug.

### 7. Optional League history test

Before importing personal evidence, confirm that the empty state explains:

- which files are required;
- how to pseudonymize league and team identifiers;
- that the app does not transmit the upload but OneDrive, Windows backup, or other software may synchronize local files;
- the difference between archived, validated, normalized, descriptive-ready, and outcome-model-ready; and
- why training remains locked.

After importing a valid package, inspect its row counts, validation report, unresolved player identities, completeness, team outcomes, roster-construction features, and drafted-only metric status. Re-importing the exact same ZIP must not duplicate canonical rows.

## Historical data you must collect manually

Start with one completed season to learn the workflow, but collect every accessible season and every team rather than only your roster or winning years.

The required files are:

- `league_rules.csv`: one row per league-season with team count, draft, roster, scoring, and playoff rules;
- `draft_picks.csv`: every original draft pick for every team; and
- `team_outcomes.csv`: every team's final regular-season and playoff outcome.

Optional weekly rosters, matchups, and transactions add management context but are not needed for the first draft-only report. They should remain absent or explicitly not included when the source is incomplete.

Use the header-only files under `data/templates/league_history_v1` only as a source template. Copy them to a private location that is preferably outside OneDrive. Replace league names, team names, owners, usernames, and account identifiers with stable pseudonymous IDs before import. Keep the private crosswalk outside this repository and outside synchronized storage.

For a detailed field-by-field workflow, use [League History Import Guide](LEAGUE_HISTORY_IMPORT_GUIDE.md) and [User Data Checklist](USER_DATA_CHECKLIST.md).

## What one personal history can and cannot do

A complete personal history can support useful descriptive questions such as:

- Which positions did each team prioritize by round?
- How much draft capital went to each position?
- How completely did the original draft cover the recorded starting lineup?
- What could the originally drafted players have scored in weekly optimal lineups under those rules?
- How did that drafted-only total rank inside that league-season?

It cannot by itself establish that a strategy caused wins or produce a calibrated playoff or championship probability. Waivers, trades, weekly decisions, injuries, opponents, and league-specific behavior all matter. Phase 8 therefore exposes a written evidence gate and no outcome-training button.

## Suggested acceptance-test notes

For each page, record:

- what you expected to happen;
- what actually happened;
- any label or instruction that was confusing;
- whether you knew the next safe action;
- whether an unavailable feature explained why it was unavailable; and
- the exact error text and action that produced it.

Also mark every place where the interface assumes technical knowledge. In particular, note jargon that needs plain-language copy, advanced evidence that could move behind an expander, unclear first actions, and screens where one recommended next step would be more useful than several equal-looking controls.

Screenshots are useful for UI feedback, but do not include personal league data, local credentials, or a completed private crosswalk. These notes will drive the first usability iteration after Phase 8.
