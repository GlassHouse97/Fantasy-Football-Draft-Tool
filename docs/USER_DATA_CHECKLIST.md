# User Data Checklist

## One-time setup

1. Install Python 3.11 and create the local `.venv` using the README commands.
2. Run `fantasy-draft data init-warehouse`.
3. Download a small completed nflverse season, then expand to 2015–2025 after the smoke test passes.
4. Copy your league rules into a YAML file modeled on `configs/example_ppr_12_team.yaml`.
5. Decide on pseudonymous IDs for league teams before importing personal history.
6. Optionally install R and Quarto for later companion analyses. They are not required.

## Repeat during draft season

1. Archive dated FFC ADP snapshots. Daily is sufficient because the source updates daily.
2. Export or manually prepare ESPN ADP using `data/templates/espn_adp_snapshot_template.csv`.
3. Review every unresolved or ambiguous player mapping.
4. Add current injury, suspension, and depth-chart adjustments using the manual template.
5. Confirm the exact scoring settings, team count, starting slots, FLEX/SUPERFLEX eligibility, bench, and draft position.

## Repeat each season

1. Add the newly completed nflverse season.
2. Import draft recap, rules, and team outcomes using the provided templates.
3. Retrain models only after validation and chronological evaluation.
4. Archive model cards and compare the new model against the simple baselines.

## Important boundaries

- Do not upload ESPN credentials, cookies, or private account data.
- Do not publish raw personal league files without reviewing identifiers.
- Do not fabricate missing ADP history, injuries, or league outcomes.
- Championship probabilities remain unavailable until enough real uploaded histories pass the future training gate.
