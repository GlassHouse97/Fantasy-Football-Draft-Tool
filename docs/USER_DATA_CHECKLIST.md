# User Data Checklist

## One-time setup

1. Install Python 3.11 and create the local `.venv` using the README commands.
2. Run `fantasy-draft data init-warehouse`.
3. Download a small completed nflverse season, then expand to 2015–2025 after the smoke test passes.
4. Run `fantasy-draft data load-nflverse` and then `fantasy-draft data review-identities`.
5. Review `data/processed/identity/identity_review_queue.csv`. For each decision, use `confirmed`, `remapped`, or `dismissed`, and enter `reviewed_at` plus `reviewer`. Remaps and dismissals require a note.
6. Apply decisions with `fantasy-draft data apply-identity-overrides data\processed\identity\identity_review_queue.csv`, then refresh the queue and run `fantasy-draft data audit`.
7. Copy your league rules into a YAML file modeled on `configs/example_ppr_12_team.yaml`.
8. Normalize existing production ADP archives with `fantasy-draft data load-adp`.
9. Build transparent market baselines with `fantasy-draft models build-adp-baselines --availability-config configs/adp_availability.yaml --output docs/PHASE_5_ADP_AVAILABILITY_EVALUATION.md`.
10. Decide on pseudonymous IDs for league teams before importing personal history.
11. Optionally install R and Quarto for later companion analyses. They are not required.

The review worksheet is generated data and should not be committed. Its applied copy is archived unchanged under `data/raw/identity_overrides/` with a SHA-256 manifest. Reapplying the same decisions is idempotent.

## Repeat during draft season

1. Archive dated FFC ADP snapshots. Daily is sufficient because the source updates daily; never overwrite an earlier capture.
2. Export or manually prepare ESPN ADP using `data/templates/espn_adp_snapshot_template.csv`.
3. Run `fantasy-draft data load-adp`; it verifies raw hashes, collapses duplicate manifests, skips labeled fixtures by default, and loads new production snapshots idempotently.
4. Refresh the identity queue after adding new FFC or ESPN captures and review every unresolved or ambiguous player mapping. A suggested name match is not an approved mapping.
5. Run `fantasy-draft models build-adp-baselines --availability-config configs/adp_availability.yaml --output docs/PHASE_5_ADP_AVAILABILITY_EVALUATION.md`, then run `fantasy-draft data audit` and `fantasy-draft status`.
6. Add current injury, suspension, and depth-chart adjustments using the manual template.
7. Confirm the exact scoring settings, team count, starting slots, FLEX/SUPERFLEX eligibility, bench, and draft position.

## Repeat each season

1. Add the newly completed nflverse season.
2. Import draft recap, rules, and team outcomes using the provided templates.
3. Retrain models only after validation and chronological evaluation.
4. Archive model cards and compare the new model against the simple baselines.

## Important boundaries

- Do not upload ESPN credentials, cookies, or private account data.
- Do not publish raw personal league files without reviewing identifiers.
- Do not map a player by display name alone. Confirm the canonical ID and use a reviewed queue decision.
- Leave FFC team-defense rows excluded; `DEF`, `DST`, and `D/ST` represent team units, not canonical players.
- Do not fabricate missing ADP history, injuries, or league outcomes.
- Do not treat 246 rows from one ADP capture as 246 independent time observations. The current build supports persistence, not a trained trend model.
- Treat next-pick availability as an uncalibrated distribution baseline until linked real draft outcomes support calibration testing.
- Do not present the Phase 5 market view as a player recommendation or draft simulation.
- Do not train a player model until the Phase 3 feature table passes cutoff, provenance, row-accounting, and leakage validation.
- Championship probabilities remain unavailable until enough real uploaded histories pass the future training gate.
