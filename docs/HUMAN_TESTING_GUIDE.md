# Human Testing Guide

This guide is the hands-on walkthrough for the finished local application. It separates three different jobs that are easy to confuse:

1. **Use the app for a draft** with rules, projections, a persistent draft board, and descriptive post-draft reporting.
2. **Maintain public NFL and ADP evidence** used by the player and draft-market components.
3. **Optionally import personal league history** for roster-construction and draft-only historical descriptions.

Personal league history is not required to open the app, create a league setup, or record a manual draft. It is required only for the Phase 8 historical workspace, and much more independent history would be required before a league-outcome model could be considered.

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

Project Status includes a collapsed **Local testing controls** section with a **Restore app defaults** button. The confirmation dialog shows the exact saved-setup, practice-draft, and pick counts and requires the phrase `RESTORE DEFAULTS` before it can run.

The restore removes only saved local league setups, practice draft sessions, their picks/events, and browser-session widget state. It does **not** remove immutable raw archives, manifests, canonical players or weekly stats, ADP evidence, reviewed identity mappings, model artifacts, or imported league-history evidence. If another browser tab changes local state after the dialog opens, the transaction stops before deletion and requires a fresh confirmation. After restoration, League Setup again prefills the checked-in 12-team PPR reference rules without inserting a replacement database row.

Download a setup YAML first if you may want to reuse custom rules. The restore cannot recover deleted practice-draft state.

## What to test first

### 1. Project Status

Confirm that the page clearly distinguishes:

- an available capability from a pending one;
- a learned model from a baseline or heuristic;
- a descriptive league-history report from an outcome model; and
- a local passing result from hosted GitHub Actions evidence.

Nothing on this page should imply that playoff or championship probabilities exist.

Open **Local testing controls** and confirm the restore dialog explains what it removes and preserves. Cancel it during a normal walkthrough. Use the final restore only when you intentionally want a clean test run.

### 2. Data Center

Run the read-only audit. Inspect source manifests and canonical table counts. Do not acquire new network data merely to test a button unless you intentionally want a new immutable snapshot.

For the league-history workflow, download a fresh template bundle before creating a private working copy. The upload must be a ZIP that follows `league-history-v1`. A rejected file should still be archived for evidence but must not change canonical history tables.

### 3. Model Lab

Inspect the selected player-projection methods, chronological evaluation evidence, intervals, diagnostics, and model lineage. This page is read-only. It should not offer a training or model-promotion button.

### 4. League Setup

Create a clearly named test setup. Verify team count, roster slots, FLEX/SUPERFLEX eligibility, scoring rules, playoff settings, and your draft slot before saving. Export the YAML backup, then import it again and confirm that the fingerprint check succeeds.

### 5. Draft Room

Create a new test session from the saved setup. Record several picks, refresh the browser, and confirm that the picks remain. Test undo and replacement, then inspect each roster and the event-replay status.

The manual state workflow can be usable even when recommendations are locked. A locked recommendation should state the exact missing evidence—such as reviewed ADP-to-player mappings—instead of returning a made-up ranking or probability.

### 6. Post-Draft

Open the report before and after completing a test draft. An incomplete report should identify itself as provisional. Check positional capital, lineup or roster coverage, market-value evidence, risk labels, and missing-data limitations. Missing ADP or uncertainty must remain unavailable rather than silently becoming zero.

### 7. League History

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
