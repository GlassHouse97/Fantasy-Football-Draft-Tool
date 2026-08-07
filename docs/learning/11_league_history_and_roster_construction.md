# League History and Roster Construction

League history adds a different kind of evidence to the draft assistant. Player models ask how an individual may perform. League-history analysis asks how complete drafts were constructed and what those drafted players could produce under a particular ruleset. A future outcome model would ask whether those patterns generalize to playoffs or championships, but Phase 8 does not make that leap.

## The evidence ladder

```text
collect every team and completed season
    -> pseudonymize before import
    -> archive immutable source bytes
    -> validate structure and cross-file consistency
    -> review football player identities
    -> normalize canonical league rows
    -> calculate draft-only outcomes
    -> describe roster-construction patterns
    -> measure future-model readiness without training
```

Each step answers a different question. “Archived” means the bytes are preserved. It does not mean the package is correct. “Validated” means the contract passes, but unresolved player mappings may still block player-linked analysis. “Descriptive-ready” means a named report has enough evidence. None of those states means championship probabilities are available.

## Why all teams and all seasons matter

Collecting only your roster answers almost nothing about relative strategy. Collecting only champions makes successful patterns appear more common than they were. Collecting only memorable seasons creates the same bias.

A useful history package contains every team in every accessible completed season, including weak teams, missed playoffs, autopicks, and disappointing players. Missing evidence remains missing. It must not become zero, an average, or an invented row merely to make a chart complete.

Personal history can be valuable even when it is small. It can show how your league drafts, where positional runs occur, and how rules change starter demand. It should not be mistaken for a representative sample of all fantasy leagues.

## Privacy is part of data quality

Use stable labels such as `league_alpha_2024` and `team_01`. Keep the private crosswalk outside the repository and outside synchronized storage. The application does not transmit packages, but OneDrive or backup software may copy local files because this project is currently stored in a synchronized path.

Remove owner names, team names, usernames, email addresses, profile data, chat, credentials, cookies, and screenshots. A public football player ID is useful mapping evidence; a fantasy owner's account ID is not.

## Roster-construction features

The first descriptive framework can calculate:

- positional picks by round;
- cumulative draft capital spent by position;
- the first QB, RB, WR, and TE round;
- RB and WR counts after rounds 3, 5, 8, and 10;
- direct-starter and FLEX/SUPERFLEX coverage;
- bench depth;
- value versus source ADP when time-appropriate ADP exists;
- projected replacement value and starter demand under the recorded rules;
- roster volatility or upside when valid player intervals exist; and
- bye-week concentration when bye data is available.

Every chart needs its denominator. “Champions selected a quarterback early” is weak evidence if it describes two champions. Prefer language such as “In 24 team-seasons, teams with a QB by Round 5 had this distribution of draft-only points.” That is still association, not causation.

## Draft-only outcomes

Draft-only scoring isolates the original picks from later management. Using the recorded rules plus historical player-week results, it can calculate:

- optimal weekly lineup points from originally drafted players;
- best-ball points from originally drafted players;
- drafted-player starter games;
- draft-only points percentile within the league-season; and
- unfilled drafted-only starter-slot burden, without claiming why the slot was unfilled.

These metrics are useful because complete transaction histories are optional. They answer “What could this draft have produced?” They do not answer “How well did this manager handle waivers, trades, and lineup choices?”

The calculation fails closed unless every original pick has a reviewed canonical player ID, the recorded roster uses supported QB/RB/WR/TE positions, the regular-season source has continuous week coverage, and every drafted player has explicit season evidence. A missing player-week inside an otherwise complete source may represent zero/bye/inactive production; a missing week or player for the entire source is not assumed to be zero. Blocked metrics remain null with a named status.

Actual standings and champion flags remain separate outcomes. Comparing them with draft-only metrics can be descriptive, but it cannot prove that a draft strategy caused the final result.

## What the quality report teaches

A good import report names the file, row, field, severity, and suggested correction for every issue. Fatal problems prevent canonical writes. Warnings preserve honest partial coverage.

Common checks include:

- matching league and team pseudonyms across files;
- exact CSV headers and parseable JSON settings;
- team count, draft round, slot, and overall-pick consistency;
- one logical rules row and one team outcome row per expected key;
- plausible playoff, placement, and champion combinations;
- duplicate picks or transactions; and
- reviewed versus unresolved player mappings.

An exact package re-upload should reuse its content fingerprint rather than create duplicate history. A corrected package remains a new immutable artifact so the audit trail is preserved.

## Why training remains locked

Playoff and championship targets are difficult. They are imbalanced, affected by schedule luck and roster management, and highly dependent on league rules. A model can rank teams while still producing badly calibrated probabilities.

The proposed conservative gate requires at least 100 independent league-seasons, 1,000 team-seasons, five completed seasons, at least 20 league-seasons in both the validation season and untouched test season, 95% complete required inputs and mappings, and 100 positive plus 100 negative examples for each binary target. Those counts are only prerequisites. The dataset must also support chronological evaluation, ruleset cohorts, leakage checks, calibration, and fair comparison with simple baselines. A nonlinear boosted model has a stricter proposed floor of 500 league-seasons, 5,000 team-seasons, and 500 examples in every target class.

Phase 8 displays this gate as evidence, not as a training button. Until a later implementation passes every gate, playoff and championship probabilities remain disabled.

## Continue learning

- Follow the operational steps in [League History Import Guide](../LEAGUE_HISTORY_IMPORT_GUIDE.md).
- Start from the [league-history-v1 template bundle](../../data/templates/league_history_v1/README.md).
- Revisit [train, validation, test, and leakage](04_train_validation_test_and_leakage.md) before interpreting any future outcome evaluation.
- Use [model cards](12_how_to_read_a_model_card.md) to distinguish intended use from overclaiming.
