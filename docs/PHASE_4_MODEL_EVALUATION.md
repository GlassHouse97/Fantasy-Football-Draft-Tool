# Phase 4 Player Model Evaluation

Status: **PASSED**

Report fingerprint: `0ef23b61786f24b47c0c3a085be699647bd86a4a613453ce4d57beb95e20589c`

This report compares learned player models with transparent baselines using chronological validation. Test results are reported after selection.

## Data lineage

- baseline_report_fingerprint: `a8e805dc230a21154ff6375e232850f8736e70b103bc59ea573ecc4eba881aa3`
- build_fingerprint: `d4a02828f7ea38f180320b0c98458127a758bc167a377ea67faf86352e60870e`
- feature_data_fingerprint: `965c7775f8fc4a64b0040bb666ebecdbb962462d35dddecccf87121ce227a4f1`
- model_config_fingerprint: `cb3aebc7bcc75ebd6723886c5775fed9e4033c0648abde7463fb98bb608c2c02`
- model_feature_fingerprint: `9faa0a8ed38f8268fca5ea3a964ffb5645c8cdadbf9162d31021be93404cee68`
- scoring_ruleset_fingerprint: `9f660dd5c8db91e63a1c43a5db74a3848b0554b2acf94d0fd891fe58b4eb7871`
- target_data_fingerprint: `1dede9747fde400fe80ffd0302ab71ecf1231de7832f6006cf3482f6d733cfea`

## Run metadata

- Phase: Phase 4 - statistical and ML player models
- Run id: phase4-052d2866899a665a44f3
- Run fingerprint: 052d2866899a665a44f333b759abb2a0d6a5aa6c47d77eb051c8d9ce89bb5c2f
- Trained at: 2026-08-24T20:21:18+00:00
- Split strategy: expanding_prediction_seasons_with_nested_chronological_tuning

## Selection protocol

- Selection metric: draft_relevant_validation_mae_with_pooled_safety_gate
- Selection rule: Select on a fixed cutoff-safe draft-relevant cohort. A learned candidate must lower cohort MAE with a paired-bootstrap 95% CI below zero, remain within the configured pooled-MAE tolerance, and preserve total-points top-N capture.
- Validation seasons: 2020, 2021, 2022, 2023, 2024
- Test season: 2025
- Test excluded from selection: yes

## Row accounting

- Board rows: 1,367
- Evaluated rows: 32,024
- Feature rows: 11,171
- Live prediction rows: 6,804
- Live rookie fallback rows: 233
- Model rows: 24
- Prediction rows: 45,588
- Selection candidates: 84
- Target rows: 9,804

## Champions selected on validation

| Position | Target | Source | Champion | Decision | Draft-relevant validation MAE | Reference baseline | Draft-relevant baseline MAE | Best learned | Draft-relevant learned MAE | Draft-relevant MAE improvement | Bootstrap CI lower | Bootstrap CI upper | Test MAE |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| QB | fantasy_points_per_game | baseline | position_shrinkage | learned_draft_relevant_regression_baseline_retained | 3.1933 | position_shrinkage | 3.1933 | ridge | 3.37082 | -0.177523 | -0.18438 | 0.532156 | 4.69889 |
| QB | fantasy_points_total | baseline | previous_season | learned_draft_relevant_improvement_inconclusive_baseline_retained | 83.1627 | previous_season | 83.1627 | ridge | 78.3544 | 4.8083 | -19.4904 | 9.41817 | 68.4777 |
| QB | games_active | baseline | previous_season | learned_draft_relevant_regression_baseline_retained | 3.22467 | previous_season | 3.22467 | ridge | 3.29525 | -0.070576 | -0.538931 | 0.642201 | 5.33105 |
| RB | fantasy_points_per_game | baseline | position_shrinkage | learned_draft_relevant_improvement_inconclusive_baseline_retained | 3.60199 | position_shrinkage | 3.60199 | ridge | 3.35442 | 0.247574 | -0.583516 | 0.0858177 | 2.72047 |
| RB | fantasy_points_total | baseline | position_shrinkage | learned_draft_relevant_improvement_inconclusive_baseline_retained | 75.0889 | position_shrinkage | 75.0889 | ridge | 71.9866 | 3.10232 | -9.06866 | 3.24381 | 46.4857 |
| RB | games_active | baseline | position_shrinkage | learned_draft_relevant_regression_baseline_retained | 3.2505 | position_shrinkage | 3.2505 | hist_gradient_boosting | 3.67743 | -0.426929 | -0.0543247 | 0.912707 | 7.93044 |
| TE | fantasy_points_per_game | baseline | position_shrinkage | learned_draft_relevant_regression_baseline_retained | 2.23834 | position_shrinkage | 2.23834 | ridge | 2.40832 | -0.169982 | -0.229488 | 0.629689 | 1.88063 |
| TE | fantasy_points_total | baseline | position_shrinkage | learned_draft_relevant_regression_baseline_retained | 45.4905 | position_shrinkage | 45.4905 | ridge | 46.9051 | -1.41468 | -7.5091 | 9.70886 | 27.6593 |
| TE | games_active | baseline | position_shrinkage | learned_draft_relevant_regression_baseline_retained | 2.87495 | position_shrinkage | 2.87495 | hist_gradient_boosting | 3.52351 | -0.648565 | -0.172655 | 1.43699 | 7.24898 |
| WR | fantasy_points_per_game | baseline | age_position_adjusted | learned_draft_relevant_regression_baseline_retained | 2.63599 | age_position_adjusted | 2.63599 | hist_gradient_boosting | 2.66927 | -0.0332755 | -0.188774 | 0.253009 | 2.30394 |
| WR | fantasy_points_total | baseline | age_position_adjusted | learned_draft_relevant_regression_baseline_retained | 56.8968 | age_position_adjusted | 56.8968 | hist_gradient_boosting | 58.8157 | -1.91884 | -3.13054 | 7.37932 | 32.6617 |
| WR | games_active | baseline | age_position_adjusted | learned_draft_relevant_regression_baseline_retained | 2.57851 | age_position_adjusted | 2.57851 | ridge | 3.09821 | -0.519703 | 0.196916 | 0.825788 | 6.40931 |

## Required regression and ranking metrics

| Position | Target | Source | Candidate | Scope | Rows | MAE | RMSE | Median AE | Spearman | Top N | Mean annual top-N capture |
|---|---|---|---|---|---|---|---|---|---|---|---|
| QB | fantasy_points_per_game | baseline | age_position_adjusted | validation | 348 | 4.24031 | 5.78326 | 3.17282 | 0.658708 | 12 | 0.616667 |
| QB | fantasy_points_per_game | baseline | age_position_adjusted | test | 66 | 4.66078 | 6.11794 | 3.67293 | 0.616574 | 12 | 0.5 |
| QB | fantasy_points_per_game | baseline | position_shrinkage | validation | 348 | 4.38818 | 5.56297 | 3.72586 | 0.658148 | 12 | 0.583333 |
| QB | fantasy_points_per_game | baseline | position_shrinkage | test | 66 | 4.69889 | 5.74633 | 4.40898 | 0.651059 | 12 | 0.583333 |
| QB | fantasy_points_per_game | baseline | previous_season | validation | 348 | 4.80754 | 6.4316 | 3.47452 | 0.601379 | 12 | 0.583333 |
| QB | fantasy_points_per_game | baseline | previous_season | test | 66 | 5.24308 | 6.82662 | 4.07886 | 0.557857 | 12 | 0.416667 |
| QB | fantasy_points_per_game | baseline | weighted_components | validation | 348 | 4.26592 | 5.81023 | 3.125 | 0.657446 | 12 | 0.583333 |
| QB | fantasy_points_per_game | baseline | weighted_components | test | 66 | 4.6922 | 6.12048 | 3.7366 | 0.6086 | 12 | 0.5 |
| QB | fantasy_points_per_game | baseline | weighted_history | validation | 348 | 4.26592 | 5.81023 | 3.125 | 0.657446 | 12 | 0.583333 |
| QB | fantasy_points_per_game | baseline | weighted_history | test | 66 | 4.6922 | 6.12048 | 3.7366 | 0.6086 | 12 | 0.5 |
| QB | fantasy_points_per_game | learned | hist_gradient_boosting | validation | 348 | 4.23961 | 5.43806 | 3.47809 | 0.668473 | 12 | 0.583333 |
| QB | fantasy_points_per_game | learned | hist_gradient_boosting | test | 66 | 4.34153 | 5.37285 | 3.67576 | 0.673813 | 12 | 0.5 |
| QB | fantasy_points_per_game | learned | ridge | validation | 348 | 4.31211 | 5.5678 | 3.55093 | 0.667641 | 12 | 0.583333 |
| QB | fantasy_points_per_game | learned | ridge | test | 66 | 4.30708 | 5.22178 | 3.54834 | 0.702328 | 12 | 0.583333 |
| QB | fantasy_points_total | baseline | age_position_adjusted | validation | 618 | 51.6408 | 78.0347 | 31.9849 | 0.582894 | 12 | 0.533333 |
| QB | fantasy_points_total | baseline | age_position_adjusted | test | 124 | 51.7395 | 74.6448 | 29.2958 | 0.59705 | 12 | 0.666667 |
| QB | fantasy_points_total | baseline | position_shrinkage | validation | 618 | 65.6892 | 80.4599 | 56.3059 | 0.504769 | 12 | 0.516667 |
| QB | fantasy_points_total | baseline | position_shrinkage | test | 124 | 66.4154 | 77.6773 | 56.5642 | 0.546215 | 12 | 0.583333 |
| QB | fantasy_points_total | baseline | previous_season | validation | 618 | 64.7518 | 84.6305 | 75.8106 | 0.454912 | 12 | 0.6 |
| QB | fantasy_points_total | baseline | previous_season | test | 124 | 68.4777 | 86.8708 | 87.8333 | 0.499426 | 12 | 0.583333 |
| QB | fantasy_points_total | baseline | weighted_components | validation | 618 | 52.8707 | 80.5051 | 34.2094 | 0.575378 | 12 | 0.55 |
| QB | fantasy_points_total | baseline | weighted_components | test | 124 | 52.4134 | 75.9687 | 32.08 | 0.596092 | 12 | 0.583333 |
| QB | fantasy_points_total | baseline | weighted_history | validation | 618 | 52.8707 | 80.5051 | 34.2094 | 0.57545 | 12 | 0.55 |
| QB | fantasy_points_total | baseline | weighted_history | test | 124 | 52.4134 | 75.9687 | 32.08 | 0.596092 | 12 | 0.583333 |
| QB | fantasy_points_total | learned | hist_gradient_boosting | validation | 618 | 41.3552 | 68.986 | 16.9056 | 0.673307 | 12 | 0.516667 |
| QB | fantasy_points_total | learned | hist_gradient_boosting | test | 124 | 37.9816 | 63.6972 | 10.6212 | 0.757057 | 12 | 0.416667 |
| QB | fantasy_points_total | learned | ridge | validation | 618 | 45.3072 | 67.4165 | 26.0259 | 0.692038 | 12 | 0.55 |
| QB | fantasy_points_total | learned | ridge | test | 124 | 43.507 | 63.315 | 27.8793 | 0.761865 | 12 | 0.583333 |
| QB | games_active | baseline | age_position_adjusted | validation | 618 | 4.09064 | 5.33372 | 3 | 0.520637 | 12 | 0.433333 |
| QB | games_active | baseline | age_position_adjusted | test | 124 | 4.06355 | 5.22999 | 3 | 0.575338 | 12 | 0.5 |
| QB | games_active | baseline | position_shrinkage | validation | 618 | 5.22732 | 5.99484 | 5.53657 | 0.411571 | 12 | 0.483333 |
| QB | games_active | baseline | position_shrinkage | test | 124 | 5.3718 | 6.08722 | 5.96882 | 0.46983 | 12 | 0.416667 |
| QB | games_active | baseline | previous_season | validation | 618 | 5.05585 | 6.13245 | 5 | 0.367937 | 12 | 0.45 |
| QB | games_active | baseline | previous_season | test | 124 | 5.33105 | 6.32962 | 5 | 0.374086 | 12 | 0.583333 |
| QB | games_active | baseline | weighted_components | validation | 618 | 4.09064 | 5.33372 | 3 | 0.520637 | 12 | 0.433333 |
| QB | games_active | baseline | weighted_components | test | 124 | 4.06355 | 5.22999 | 3 | 0.575338 | 12 | 0.5 |
| QB | games_active | baseline | weighted_history | validation | 618 | 4.09064 | 5.33372 | 3 | 0.520637 | 12 | 0.433333 |
| QB | games_active | baseline | weighted_history | test | 124 | 4.06355 | 5.22999 | 3 | 0.575338 | 12 | 0.5 |
| QB | games_active | learned | hist_gradient_boosting | validation | 618 | 2.53429 | 3.75667 | 1.77396 | 0.738215 | 12 | 0.4 |
| QB | games_active | learned | hist_gradient_boosting | test | 124 | 2.27844 | 3.40994 | 1.40287 | 0.812381 | 12 | 0.416667 |
| QB | games_active | learned | ridge | validation | 618 | 2.44782 | 3.64491 | 1.52571 | 0.749562 | 12 | 0.45 |
| QB | games_active | learned | ridge | test | 124 | 2.30205 | 3.313 | 1.56783 | 0.820459 | 12 | 0.5 |
| RB | fantasy_points_per_game | baseline | age_position_adjusted | validation | 686 | 2.69753 | 3.80208 | 1.84259 | 0.760386 | 12 | 0.583333 |
| RB | fantasy_points_per_game | baseline | age_position_adjusted | test | 128 | 2.33592 | 3.12942 | 1.72465 | 0.785083 | 12 | 0.666667 |
| RB | fantasy_points_per_game | baseline | position_shrinkage | validation | 686 | 2.84192 | 3.68033 | 2.18097 | 0.759308 | 12 | 0.55 |
| RB | fantasy_points_per_game | baseline | position_shrinkage | test | 128 | 2.72047 | 3.39935 | 2.20823 | 0.75371 | 12 | 0.666667 |
| RB | fantasy_points_per_game | baseline | previous_season | validation | 686 | 2.8652 | 3.9235 | 2.11723 | 0.735766 | 12 | 0.6 |
| RB | fantasy_points_per_game | baseline | previous_season | test | 128 | 2.47996 | 3.45268 | 1.6421 | 0.781365 | 12 | 0.666667 |
| RB | fantasy_points_per_game | baseline | weighted_components | validation | 686 | 2.78325 | 3.91543 | 1.86965 | 0.75733 | 12 | 0.6 |
| RB | fantasy_points_per_game | baseline | weighted_components | test | 128 | 2.49616 | 3.31142 | 1.80687 | 0.781091 | 12 | 0.666667 |
| RB | fantasy_points_per_game | baseline | weighted_history | validation | 686 | 2.78325 | 3.91543 | 1.86965 | 0.757329 | 12 | 0.6 |
| RB | fantasy_points_per_game | baseline | weighted_history | test | 128 | 2.49616 | 3.31142 | 1.80687 | 0.781091 | 12 | 0.666667 |
| RB | fantasy_points_per_game | learned | hist_gradient_boosting | validation | 686 | 2.66504 | 3.66773 | 1.90016 | 0.755948 | 12 | 0.5 |
| RB | fantasy_points_per_game | learned | hist_gradient_boosting | test | 128 | 2.36122 | 3.27694 | 1.69338 | 0.764782 | 12 | 0.583333 |
| RB | fantasy_points_per_game | learned | ridge | validation | 686 | 2.666 | 3.62097 | 1.91048 | 0.762846 | 12 | 0.533333 |
| RB | fantasy_points_per_game | learned | ridge | test | 128 | 2.2728 | 3.12365 | 1.74554 | 0.789075 | 12 | 0.666667 |
| RB | fantasy_points_total | baseline | age_position_adjusted | validation | 1488 | 35.4954 | 52.8714 | 21.7389 | 0.534772 | 12 | 0.466667 |
| RB | fantasy_points_total | baseline | age_position_adjusted | test | 294 | 34.7254 | 51.3416 | 23.3024 | 0.480085 | 12 | 0.583333 |
| RB | fantasy_points_total | baseline | position_shrinkage | validation | 1488 | 45.6875 | 56.5191 | 39.7565 | 0.447759 | 12 | 0.466667 |
| RB | fantasy_points_total | baseline | position_shrinkage | test | 294 | 46.4857 | 57.4921 | 41.5497 | 0.421194 | 12 | 0.583333 |
| RB | fantasy_points_total | baseline | previous_season | validation | 1488 | 47.9314 | 61.587 | 57.4862 | 0.330087 | 12 | 0.466667 |
| RB | fantasy_points_total | baseline | previous_season | test | 294 | 48.1701 | 62.6209 | 62.3632 | 0.329258 | 12 | 0.75 |
| RB | fantasy_points_total | baseline | weighted_components | validation | 1488 | 37.8594 | 55.815 | 23.1603 | 0.517893 | 12 | 0.5 |
| RB | fantasy_points_total | baseline | weighted_components | test | 294 | 37.5788 | 55.0778 | 24.1827 | 0.467967 | 12 | 0.583333 |
| RB | fantasy_points_total | baseline | weighted_history | validation | 1488 | 37.8594 | 55.815 | 23.1603 | 0.517885 | 12 | 0.5 |
| RB | fantasy_points_total | baseline | weighted_history | test | 294 | 37.5788 | 55.0778 | 24.1827 | 0.467935 | 12 | 0.583333 |
| RB | fantasy_points_total | learned | hist_gradient_boosting | validation | 1488 | 23.2001 | 43.6552 | 6.45452 | 0.73861 | 12 | 0.433333 |
| RB | fantasy_points_total | learned | hist_gradient_boosting | test | 294 | 22.3794 | 46.1492 | 4.27117 | 0.728928 | 12 | 0.583333 |
| RB | fantasy_points_total | learned | ridge | validation | 1488 | 27.0683 | 43.9345 | 14.4918 | 0.714874 | 12 | 0.483333 |
| RB | fantasy_points_total | learned | ridge | test | 294 | 27.1653 | 44.4879 | 13.5183 | 0.664381 | 12 | 0.75 |
| RB | games_active | baseline | age_position_adjusted | validation | 1483 | 6.17816 | 7.67207 | 5 | 0.498444 | 12 | 0.133333 |
| RB | games_active | baseline | age_position_adjusted | test | 294 | 6.81933 | 8.3292 | 6 | 0.487127 | 12 | 0 |
| RB | games_active | baseline | position_shrinkage | validation | 1483 | 7.26169 | 8.3045 | 8.23485 | 0.468757 | 12 | 0.25 |
| RB | games_active | baseline | position_shrinkage | test | 294 | 7.93044 | 8.94974 | 8.99199 | 0.475517 | 12 | 0.166667 |
| RB | games_active | baseline | previous_season | validation | 1483 | 7.18794 | 8.48059 | 9 | 0.419213 | 12 | 0.4 |
| RB | games_active | baseline | previous_season | test | 294 | 7.84813 | 9.19628 | 11.4875 | 0.457982 | 12 | 0.416667 |
| RB | games_active | baseline | weighted_components | validation | 1483 | 6.17816 | 7.67207 | 5 | 0.498444 | 12 | 0.133333 |
| RB | games_active | baseline | weighted_components | test | 294 | 6.81933 | 8.3292 | 6 | 0.487127 | 12 | 0 |
| RB | games_active | baseline | weighted_history | validation | 1483 | 6.17816 | 7.67207 | 5 | 0.498444 | 12 | 0.133333 |
| RB | games_active | baseline | weighted_history | test | 294 | 6.81933 | 8.3292 | 6 | 0.487127 | 12 | 0 |
| RB | games_active | learned | hist_gradient_boosting | validation | 1483 | 3.00524 | 4.53586 | 1.90959 | 0.755951 | 12 | 0.116667 |
| RB | games_active | learned | hist_gradient_boosting | test | 294 | 2.67123 | 4.24331 | 1.24506 | 0.772643 | 12 | 0.0833333 |
| RB | games_active | learned | ridge | validation | 1483 | 3.12443 | 4.50769 | 2.0559 | 0.757945 | 12 | 0.05 |
| RB | games_active | learned | ridge | test | 294 | 3.02363 | 4.50107 | 1.67264 | 0.73892 | 12 | 0 |
| TE | fantasy_points_per_game | baseline | age_position_adjusted | validation | 565 | 1.78452 | 2.43854 | 1.36189 | 0.753236 | 12 | 0.616667 |
| TE | fantasy_points_per_game | baseline | age_position_adjusted | test | 122 | 1.65771 | 2.39922 | 1.1065 | 0.783267 | 12 | 0.5 |
| TE | fantasy_points_per_game | baseline | position_shrinkage | validation | 565 | 1.89745 | 2.42496 | 1.56603 | 0.716572 | 12 | 0.616667 |
| TE | fantasy_points_per_game | baseline | position_shrinkage | test | 122 | 1.88063 | 2.4863 | 1.41342 | 0.719511 | 12 | 0.5 |
| TE | fantasy_points_per_game | baseline | previous_season | validation | 565 | 1.90567 | 2.57141 | 1.4 | 0.714067 | 12 | 0.65 |
| TE | fantasy_points_per_game | baseline | previous_season | test | 122 | 1.90235 | 2.65904 | 1.24916 | 0.726307 | 12 | 0.5 |
| TE | fantasy_points_per_game | baseline | weighted_components | validation | 565 | 1.79923 | 2.45669 | 1.34853 | 0.751407 | 12 | 0.633333 |
| TE | fantasy_points_per_game | baseline | weighted_components | test | 122 | 1.6748 | 2.45766 | 1.1065 | 0.778681 | 12 | 0.5 |
| TE | fantasy_points_per_game | baseline | weighted_history | validation | 565 | 1.79923 | 2.45669 | 1.34853 | 0.751409 | 12 | 0.633333 |
| TE | fantasy_points_per_game | baseline | weighted_history | test | 122 | 1.6748 | 2.45766 | 1.1065 | 0.778681 | 12 | 0.5 |
| TE | fantasy_points_per_game | learned | hist_gradient_boosting | validation | 565 | 1.76886 | 2.37808 | 1.2903 | 0.746745 | 12 | 0.616667 |
| TE | fantasy_points_per_game | learned | hist_gradient_boosting | test | 122 | 1.5948 | 2.35665 | 0.854649 | 0.787423 | 12 | 0.5 |
| TE | fantasy_points_per_game | learned | ridge | validation | 565 | 1.91531 | 2.64466 | 1.41716 | 0.706346 | 12 | 0.666667 |
| TE | fantasy_points_per_game | learned | ridge | test | 122 | 1.76203 | 2.58434 | 1.09231 | 0.782964 | 12 | 0.583333 |
| TE | fantasy_points_total | baseline | age_position_adjusted | validation | 1160 | 23.9423 | 35.2516 | 16.646 | 0.541544 | 12 | 0.483333 |
| TE | fantasy_points_total | baseline | age_position_adjusted | test | 237 | 22.4411 | 32.8089 | 13.9383 | 0.554717 | 12 | 0.416667 |
| TE | fantasy_points_total | baseline | position_shrinkage | validation | 1160 | 29.4239 | 36.4369 | 24.6278 | 0.476327 | 12 | 0.483333 |
| TE | fantasy_points_total | baseline | position_shrinkage | test | 237 | 27.6593 | 34.3405 | 23.2146 | 0.457253 | 12 | 0.5 |
| TE | fantasy_points_total | baseline | previous_season | validation | 1160 | 30.7262 | 39.2747 | 35.9115 | 0.379127 | 12 | 0.483333 |
| TE | fantasy_points_total | baseline | previous_season | test | 237 | 31.3559 | 38.8978 | 40.181 | 0.32328 | 12 | 0.5 |
| TE | fantasy_points_total | baseline | weighted_components | validation | 1160 | 24.575 | 36.2864 | 17.0953 | 0.532213 | 12 | 0.45 |
| TE | fantasy_points_total | baseline | weighted_components | test | 237 | 23.0995 | 33.6422 | 14.1547 | 0.549805 | 12 | 0.416667 |
| TE | fantasy_points_total | baseline | weighted_history | validation | 1160 | 24.575 | 36.2864 | 17.0953 | 0.532204 | 12 | 0.45 |
| TE | fantasy_points_total | baseline | weighted_history | test | 237 | 23.0995 | 33.6422 | 14.1547 | 0.549819 | 12 | 0.416667 |
| TE | fantasy_points_total | learned | hist_gradient_boosting | validation | 1160 | 16.3807 | 29.8667 | 4.81349 | 0.753461 | 12 | 0.483333 |
| TE | fantasy_points_total | learned | hist_gradient_boosting | test | 237 | 13.3255 | 26.181 | 3.11438 | 0.822961 | 12 | 0.5 |
| TE | fantasy_points_total | learned | ridge | validation | 1160 | 19.1752 | 32.2944 | 10.144 | 0.716498 | 12 | 0.516667 |
| TE | fantasy_points_total | learned | ridge | test | 237 | 16.7748 | 28.7134 | 8.87204 | 0.78291 | 12 | 0.5 |
| TE | games_active | baseline | age_position_adjusted | validation | 1158 | 6.28561 | 7.89442 | 5 | 0.468542 | 12 | 0.2 |
| TE | games_active | baseline | age_position_adjusted | test | 235 | 6.16474 | 7.87191 | 4.42857 | 0.528364 | 12 | 0.0833333 |
| TE | games_active | baseline | position_shrinkage | validation | 1158 | 7.26705 | 8.45443 | 8.24548 | 0.444069 | 12 | 0.266667 |
| TE | games_active | baseline | position_shrinkage | test | 235 | 7.24898 | 8.5782 | 8.08325 | 0.490908 | 12 | 0.0833333 |
| TE | games_active | baseline | previous_season | validation | 1158 | 7.11719 | 8.59937 | 8 | 0.433652 | 12 | 0.4 |
| TE | games_active | baseline | previous_season | test | 235 | 7.37428 | 8.88295 | 8 | 0.432721 | 12 | 0.25 |
| TE | games_active | baseline | weighted_components | validation | 1158 | 6.28561 | 7.89442 | 5 | 0.468542 | 12 | 0.2 |
| TE | games_active | baseline | weighted_components | test | 235 | 6.16474 | 7.87191 | 4.42857 | 0.528364 | 12 | 0.0833333 |
| TE | games_active | baseline | weighted_history | validation | 1158 | 6.28561 | 7.89442 | 5 | 0.468542 | 12 | 0.2 |
| TE | games_active | baseline | weighted_history | test | 235 | 6.16474 | 7.87191 | 4.42857 | 0.528364 | 12 | 0.0833333 |
| TE | games_active | learned | hist_gradient_boosting | validation | 1158 | 3.25215 | 4.76257 | 2.25854 | 0.747934 | 12 | 0.0833333 |
| TE | games_active | learned | hist_gradient_boosting | test | 235 | 2.5701 | 3.96942 | 1.47615 | 0.806587 | 12 | 0 |
| TE | games_active | learned | ridge | validation | 1158 | 3.65206 | 5.0304 | 2.91424 | 0.710496 | 12 | 0.0666667 |
| TE | games_active | learned | ridge | test | 235 | 2.86741 | 4.07481 | 2.32653 | 0.798687 | 12 | 0 |
| WR | fantasy_points_per_game | baseline | age_position_adjusted | validation | 989 | 2.54439 | 3.33412 | 1.98676 | 0.75691 | 12 | 0.533333 |
| WR | fantasy_points_per_game | baseline | age_position_adjusted | test | 198 | 2.30394 | 2.98562 | 1.86212 | 0.810616 | 12 | 0.5 |
| WR | fantasy_points_per_game | baseline | position_shrinkage | validation | 989 | 2.77451 | 3.39377 | 2.45173 | 0.742016 | 12 | 0.516667 |
| WR | fantasy_points_per_game | baseline | position_shrinkage | test | 198 | 2.43741 | 3.04938 | 2.03722 | 0.790151 | 12 | 0.583333 |
| WR | fantasy_points_per_game | baseline | previous_season | validation | 989 | 2.76831 | 3.63967 | 2.21 | 0.730573 | 12 | 0.533333 |
| WR | fantasy_points_per_game | baseline | previous_season | test | 198 | 2.56141 | 3.36236 | 2.07793 | 0.785464 | 12 | 0.5 |
| WR | fantasy_points_per_game | baseline | weighted_components | validation | 989 | 2.63116 | 3.45256 | 2.05659 | 0.751856 | 12 | 0.55 |
| WR | fantasy_points_per_game | baseline | weighted_components | test | 198 | 2.41075 | 3.15466 | 1.86702 | 0.802269 | 12 | 0.583333 |
| WR | fantasy_points_per_game | baseline | weighted_history | validation | 989 | 2.63116 | 3.45256 | 2.05659 | 0.751859 | 12 | 0.55 |
| WR | fantasy_points_per_game | baseline | weighted_history | test | 198 | 2.41075 | 3.15466 | 1.86702 | 0.802266 | 12 | 0.583333 |
| WR | fantasy_points_per_game | learned | hist_gradient_boosting | validation | 989 | 2.36737 | 3.17099 | 1.69197 | 0.759968 | 12 | 0.5 |
| WR | fantasy_points_per_game | learned | hist_gradient_boosting | test | 198 | 2.1201 | 2.7802 | 1.64687 | 0.83098 | 12 | 0.5 |
| WR | fantasy_points_per_game | learned | ridge | validation | 989 | 2.57761 | 3.45271 | 2.05782 | 0.759948 | 12 | 0.566667 |
| WR | fantasy_points_per_game | learned | ridge | test | 198 | 2.12691 | 2.72144 | 1.66359 | 0.842133 | 12 | 0.583333 |
| WR | fantasy_points_total | baseline | age_position_adjusted | validation | 2109 | 33.4881 | 47.6241 | 23.9795 | 0.566953 | 12 | 0.566667 |
| WR | fantasy_points_total | baseline | age_position_adjusted | test | 434 | 32.6617 | 48.2429 | 19.858 | 0.566674 | 12 | 0.333333 |
| WR | fantasy_points_total | baseline | position_shrinkage | validation | 2109 | 43.5474 | 51.5039 | 39.3768 | 0.513722 | 12 | 0.533333 |
| WR | fantasy_points_total | baseline | position_shrinkage | test | 434 | 41.3842 | 50.0763 | 36.9847 | 0.511885 | 12 | 0.333333 |
| WR | fantasy_points_total | baseline | previous_season | validation | 2109 | 45.1961 | 56.0851 | 54.1649 | 0.408734 | 12 | 0.45 |
| WR | fantasy_points_total | baseline | previous_season | test | 434 | 44.8118 | 56.3973 | 59.2843 | 0.465414 | 12 | 0.333333 |
| WR | fantasy_points_total | baseline | weighted_components | validation | 2109 | 34.9655 | 49.7321 | 24.5 | 0.557175 | 12 | 0.55 |
| WR | fantasy_points_total | baseline | weighted_components | test | 434 | 34.1085 | 50.3687 | 20.6517 | 0.558377 | 12 | 0.333333 |
| WR | fantasy_points_total | baseline | weighted_history | validation | 2109 | 34.9655 | 49.7321 | 24.5 | 0.557178 | 12 | 0.55 |
| WR | fantasy_points_total | baseline | weighted_history | test | 434 | 34.1085 | 50.3687 | 20.6517 | 0.558362 | 12 | 0.333333 |
| WR | fantasy_points_total | learned | hist_gradient_boosting | validation | 2109 | 21.5237 | 39.2083 | 5.2245 | 0.749875 | 12 | 0.483333 |
| WR | fantasy_points_total | learned | hist_gradient_boosting | test | 434 | 19.031 | 37.019 | 4.17268 | 0.749512 | 12 | 0.333333 |
| WR | fantasy_points_total | learned | ridge | validation | 2109 | 27.881 | 43.2577 | 16.79 | 0.702068 | 12 | 0.483333 |
| WR | fantasy_points_total | learned | ridge | test | 434 | 22.7653 | 36.1024 | 12.7027 | 0.715594 | 12 | 0.333333 |
| WR | games_active | baseline | age_position_adjusted | validation | 2101 | 5.93888 | 7.40035 | 5 | 0.528502 | 12 | 0.1 |
| WR | games_active | baseline | age_position_adjusted | test | 433 | 6.40931 | 7.93854 | 5.5 | 0.451499 | 12 | 0.0833333 |
| WR | games_active | baseline | position_shrinkage | validation | 2101 | 7.10354 | 8.1117 | 8.08193 | 0.4938 | 12 | 0.15 |
| WR | games_active | baseline | position_shrinkage | test | 433 | 7.39689 | 8.46896 | 8.74731 | 0.437581 | 12 | 0.166667 |
| WR | games_active | baseline | previous_season | validation | 2101 | 7.04935 | 8.35514 | 9 | 0.432511 | 12 | 0.25 |
| WR | games_active | baseline | previous_season | test | 433 | 7.47264 | 8.75011 | 10 | 0.35395 | 12 | 0.166667 |
| WR | games_active | baseline | weighted_components | validation | 2101 | 5.93888 | 7.40035 | 5 | 0.528502 | 12 | 0.1 |
| WR | games_active | baseline | weighted_components | test | 433 | 6.40931 | 7.93854 | 5.5 | 0.451499 | 12 | 0.0833333 |
| WR | games_active | baseline | weighted_history | validation | 2101 | 5.93888 | 7.40035 | 5 | 0.528502 | 12 | 0.1 |
| WR | games_active | baseline | weighted_history | test | 433 | 6.40931 | 7.93854 | 5.5 | 0.451499 | 12 | 0.0833333 |
| WR | games_active | learned | hist_gradient_boosting | validation | 2101 | 2.91416 | 4.45503 | 1.81791 | 0.757169 | 12 | 0.0666667 |
| WR | games_active | learned | hist_gradient_boosting | test | 433 | 2.84212 | 4.4293 | 1.59535 | 0.730954 | 12 | 0.0833333 |
| WR | games_active | learned | ridge | validation | 2101 | 3.12805 | 4.41749 | 2.05794 | 0.75622 | 12 | 0.0833333 |
| WR | games_active | learned | ridge | test | 433 | 2.94836 | 4.40142 | 1.94303 | 0.731375 | 12 | 0.0833333 |

## Champion error by experience and projection tier

| Position | Target | Source | Champion | Scope | Segment type | Segment | Rows | MAE | RMSE | Median AE | Spearman |
|---|---|---|---|---|---|---|---|---|---|---|---|
| QB | fantasy_points_per_game | baseline | position_shrinkage | validation | experience_group | sparse | 62 | 5.22892 | 6.21577 | 4.72081 | 0.549811 |
| QB | fantasy_points_per_game | baseline | position_shrinkage | validation | experience_group | veteran | 286 | 4.20592 | 5.41107 | 3.47414 | 0.678712 |
| QB | fantasy_points_per_game | baseline | position_shrinkage | validation | projection_tier | lower | 84 | 4.52934 | 5.1576 | 4.50186 | 0.0869107 |
| QB | fantasy_points_per_game | baseline | position_shrinkage | validation | projection_tier | middle | 128 | 5.02515 | 6.10937 | 4.44853 | 0.264068 |
| QB | fantasy_points_per_game | baseline | position_shrinkage | validation | projection_tier | top | 136 | 3.70149 | 5.25624 | 2.65504 | 0.577115 |
| QB | fantasy_points_per_game | baseline | position_shrinkage | test | experience_group | sparse | 9 | 4.79727 | 5.56321 | 5.28388 | 0.55 |
| QB | fantasy_points_per_game | baseline | position_shrinkage | test | experience_group | veteran | 57 | 4.68336 | 5.77472 | 3.97176 | 0.654589 |
| QB | fantasy_points_per_game | baseline | position_shrinkage | test | projection_tier | lower | 15 | 4.92586 | 5.35233 | 5.83576 | -0.0571429 |
| QB | fantasy_points_per_game | baseline | position_shrinkage | test | projection_tier | middle | 22 | 5.39511 | 6.22607 | 5.62582 | -0.012987 |
| QB | fantasy_points_per_game | baseline | position_shrinkage | test | projection_tier | top | 29 | 4.05333 | 5.56103 | 3.13082 | 0.303448 |
| QB | fantasy_points_total | baseline | previous_season | validation | experience_group | sparse | 236 | 66.5488 | 75.1787 | 76.0458 | 0.162373 |
| QB | fantasy_points_total | baseline | previous_season | validation | experience_group | veteran | 382 | 63.6416 | 89.975 | 50.89 | 0.608618 |
| QB | fantasy_points_total | baseline | previous_season | validation | projection_tier | lower | 154 | 26.5373 | 62.7175 | 8.61 | 0.195986 |
| QB | fantasy_points_total | baseline | previous_season | validation | projection_tier | middle | 310 | 70.3021 | 76.2565 | 76.0458 | -0.108201 |
| QB | fantasy_points_total | baseline | previous_season | validation | projection_tier | top | 154 | 91.7936 | 114.469 | 77.86 | 0.50416 |
| QB | fantasy_points_total | baseline | previous_season | test | experience_group | sparse | 43 | 80.5038 | 89.8834 | 87.8333 | 0.0397342 |
| QB | fantasy_points_total | baseline | previous_season | test | experience_group | veteran | 81 | 62.0935 | 85.2282 | 49.44 | 0.63745 |
| QB | fantasy_points_total | baseline | previous_season | test | projection_tier | lower | 31 | 14.2845 | 22.1249 | 8.92 | 0.133024 |
| QB | fantasy_points_total | baseline | previous_season | test | projection_tier | middle | 62 | 84.3083 | 88.58 | 87.8333 | -0.206186 |
| QB | fantasy_points_total | baseline | previous_season | test | projection_tier | top | 31 | 91.0097 | 118.338 | 87.86 | 0.383506 |
| QB | games_active | baseline | previous_season | validation | experience_group | sparse | 236 | 6.31604 | 6.91751 | 7.73171 | 0.0561062 |
| QB | games_active | baseline | previous_season | validation | experience_group | veteran | 382 | 4.2773 | 5.59264 | 3.04819 | 0.51914 |
| QB | games_active | baseline | previous_season | validation | projection_tier | lower | 154 | 2.92857 | 4.31172 | 2 | 0.241399 |
| QB | games_active | baseline | previous_season | validation | projection_tier | middle | 310 | 6.61778 | 7.00324 | 7.73171 | -0.198588 |
| QB | games_active | baseline | previous_season | validation | projection_tier | top | 154 | 4.03896 | 5.79633 | 2.5 | 0.242113 |
| QB | games_active | baseline | previous_season | test | experience_group | sparse | 43 | 7.31763 | 7.80261 | 8.64557 | -0.0011777 |
| QB | games_active | baseline | previous_season | test | experience_group | veteran | 81 | 4.27645 | 5.3864 | 3 | 0.543719 |
| QB | games_active | baseline | previous_season | test | projection_tier | lower | 31 | 2.45161 | 2.91824 | 2 | 0.226416 |
| QB | games_active | baseline | previous_season | test | projection_tier | middle | 62 | 7.38791 | 7.74695 | 8.64557 | -0.195921 |
| QB | games_active | baseline | previous_season | test | projection_tier | top | 31 | 4.09677 | 5.63113 | 3 | 0.569309 |
| RB | fantasy_points_per_game | baseline | position_shrinkage | validation | experience_group | sparse | 154 | 3.01438 | 3.98481 | 2.31334 | 0.630068 |
| RB | fantasy_points_per_game | baseline | position_shrinkage | validation | experience_group | veteran | 532 | 2.792 | 3.58737 | 2.15457 | 0.784201 |
| RB | fantasy_points_per_game | baseline | position_shrinkage | validation | projection_tier | lower | 191 | 1.5458 | 1.94378 | 1.35386 | 0.401129 |
| RB | fantasy_points_per_game | baseline | position_shrinkage | validation | projection_tier | middle | 188 | 2.87837 | 3.74883 | 2.5298 | 0.218613 |
| RB | fantasy_points_per_game | baseline | position_shrinkage | validation | projection_tier | top | 307 | 3.62598 | 4.39424 | 3.24942 | 0.603512 |
| RB | fantasy_points_per_game | baseline | position_shrinkage | test | experience_group | sparse | 25 | 3.01022 | 3.38288 | 2.48427 | 0.018308 |
| RB | fantasy_points_per_game | baseline | position_shrinkage | test | experience_group | veteran | 103 | 2.65015 | 3.40333 | 2.06692 | 0.832753 |
| RB | fantasy_points_per_game | baseline | position_shrinkage | test | projection_tier | lower | 34 | 1.51077 | 1.73552 | 1.48829 | 0.315399 |
| RB | fantasy_points_per_game | baseline | position_shrinkage | test | projection_tier | middle | 39 | 2.80756 | 3.38297 | 2.83618 | -0.16087 |
| RB | fantasy_points_per_game | baseline | position_shrinkage | test | projection_tier | top | 55 | 3.40654 | 4.11288 | 2.96356 | 0.759091 |
| RB | fantasy_points_total | baseline | position_shrinkage | validation | experience_group | sparse | 650 | 49.1075 | 55.8202 | 47.9962 | 0.0829349 |
| RB | fantasy_points_total | baseline | position_shrinkage | validation | experience_group | veteran | 838 | 43.0347 | 57.0552 | 30.4684 | 0.648163 |
| RB | fantasy_points_total | baseline | position_shrinkage | validation | projection_tier | lower | 373 | 20.9216 | 24.7841 | 20.8432 | 0.0494198 |
| RB | fantasy_points_total | baseline | position_shrinkage | validation | projection_tier | middle | 742 | 46.5477 | 51.3919 | 47.1148 | -0.0908278 |
| RB | fantasy_points_total | baseline | position_shrinkage | validation | projection_tier | top | 373 | 68.7421 | 82.9166 | 65.9551 | 0.588301 |
| RB | fantasy_points_total | baseline | position_shrinkage | test | experience_group | sparse | 132 | 48.7987 | 51.4219 | 50.0402 | -0.137429 |
| RB | fantasy_points_total | baseline | position_shrinkage | test | experience_group | veteran | 162 | 44.6012 | 62.0003 | 31.3077 | 0.681464 |
| RB | fantasy_points_total | baseline | position_shrinkage | test | projection_tier | lower | 74 | 20.9584 | 23.0045 | 21.016 | 0.116866 |
| RB | fantasy_points_total | baseline | position_shrinkage | test | projection_tier | middle | 146 | 46.733 | 49.3615 | 49.0334 | -0.285628 |
| RB | fantasy_points_total | baseline | position_shrinkage | test | projection_tier | top | 74 | 71.5253 | 88.2924 | 63.1432 | 0.677478 |
| RB | games_active | baseline | position_shrinkage | validation | experience_group | sparse | 645 | 9.01884 | 9.56469 | 9.78431 | 0.266063 |
| RB | games_active | baseline | position_shrinkage | validation | experience_group | veteran | 838 | 5.90922 | 7.18558 | 5.85638 | 0.498986 |
| RB | games_active | baseline | position_shrinkage | validation | projection_tier | lower | 373 | 7.15146 | 7.46173 | 7.68627 | -0.010782 |
| RB | games_active | baseline | position_shrinkage | validation | projection_tier | middle | 737 | 8.14421 | 8.91583 | 9.67143 | 0.345146 |
| RB | games_active | baseline | position_shrinkage | validation | projection_tier | top | 373 | 5.62816 | 7.8391 | 2.84103 | 0.121328 |
| RB | games_active | baseline | position_shrinkage | test | experience_group | sparse | 132 | 9.85696 | 10.3158 | 10.3222 | 0.170895 |
| RB | games_active | baseline | position_shrinkage | test | experience_group | veteran | 162 | 6.36068 | 7.65858 | 6.59438 | 0.508326 |
| RB | games_active | baseline | position_shrinkage | test | projection_tier | lower | 74 | 7.22966 | 7.52847 | 7.64961 | 0.0577169 |
| RB | games_active | baseline | position_shrinkage | test | projection_tier | middle | 146 | 9.1378 | 9.78214 | 10.3222 | 0.445352 |
| RB | games_active | baseline | position_shrinkage | test | projection_tier | top | 74 | 6.24912 | 8.52963 | 2.71454 | 0.224749 |
| TE | fantasy_points_per_game | baseline | position_shrinkage | validation | experience_group | sparse | 129 | 1.86255 | 2.24985 | 1.71202 | 0.449701 |
| TE | fantasy_points_per_game | baseline | position_shrinkage | validation | experience_group | veteran | 436 | 1.90777 | 2.47439 | 1.50426 | 0.762819 |
| TE | fantasy_points_per_game | baseline | position_shrinkage | validation | projection_tier | lower | 134 | 1.04739 | 1.34968 | 1.04029 | 0.167736 |
| TE | fantasy_points_per_game | baseline | position_shrinkage | validation | projection_tier | middle | 203 | 1.86885 | 2.30521 | 1.75559 | 0.249605 |
| TE | fantasy_points_per_game | baseline | position_shrinkage | validation | projection_tier | top | 228 | 2.4225 | 2.96144 | 2.14213 | 0.649684 |
| TE | fantasy_points_per_game | baseline | position_shrinkage | test | experience_group | sparse | 20 | 1.87401 | 2.28434 | 1.6043 | 0.347172 |
| TE | fantasy_points_per_game | baseline | position_shrinkage | test | experience_group | veteran | 102 | 1.88192 | 2.524 | 1.34471 | 0.761975 |
| TE | fantasy_points_per_game | baseline | position_shrinkage | test | projection_tier | lower | 35 | 0.931028 | 1.26387 | 0.815699 | 0.217537 |
| TE | fantasy_points_per_game | baseline | position_shrinkage | test | projection_tier | middle | 41 | 1.64913 | 2.00954 | 1.59175 | 0.203642 |
| TE | fantasy_points_per_game | baseline | position_shrinkage | test | projection_tier | top | 46 | 2.80948 | 3.40296 | 2.80547 | 0.525254 |
| TE | fantasy_points_total | baseline | position_shrinkage | validation | experience_group | sparse | 487 | 30.6652 | 34.1068 | 29.7419 | 0.0448046 |
| TE | fantasy_points_total | baseline | position_shrinkage | validation | experience_group | veteran | 673 | 28.5256 | 38.0341 | 20.2794 | 0.667732 |
| TE | fantasy_points_total | baseline | position_shrinkage | validation | projection_tier | lower | 290 | 14.8209 | 17.9065 | 13.8599 | 0.085147 |
| TE | fantasy_points_total | baseline | position_shrinkage | validation | projection_tier | middle | 580 | 29.1213 | 32.2196 | 29.22 | -0.0284317 |
| TE | fantasy_points_total | baseline | position_shrinkage | validation | projection_tier | top | 290 | 44.6319 | 53.9791 | 43.2501 | 0.582001 |
| TE | fantasy_points_total | baseline | position_shrinkage | test | experience_group | sparse | 101 | 31.2454 | 33.7522 | 32.0736 | -0.0347603 |
| TE | fantasy_points_total | baseline | position_shrinkage | test | experience_group | veteran | 136 | 24.9961 | 34.7709 | 16.2241 | 0.737707 |
| TE | fantasy_points_total | baseline | position_shrinkage | test | projection_tier | lower | 59 | 13.1206 | 16.3435 | 11.911 | 0.0732561 |
| TE | fantasy_points_total | baseline | position_shrinkage | test | projection_tier | middle | 119 | 28.5913 | 30.6707 | 28.5751 | -0.274238 |
| TE | fantasy_points_total | baseline | position_shrinkage | test | projection_tier | top | 59 | 40.3184 | 50.7209 | 36.8455 | 0.633443 |
| TE | games_active | baseline | position_shrinkage | validation | experience_group | sparse | 485 | 9.06482 | 9.7501 | 10.078 | 0.0977101 |
| TE | games_active | baseline | position_shrinkage | validation | experience_group | veteran | 673 | 5.97148 | 7.38102 | 5.4854 | 0.493245 |
| TE | games_active | baseline | position_shrinkage | validation | projection_tier | lower | 290 | 7.21307 | 7.6039 | 7.98063 | 0.0216675 |
| TE | games_active | baseline | position_shrinkage | validation | projection_tier | middle | 578 | 8.51684 | 9.38201 | 10.4575 | 0.24514 |
| TE | games_active | baseline | position_shrinkage | validation | projection_tier | top | 290 | 4.83008 | 7.22221 | 2.07483 | 0.31633 |
| TE | games_active | baseline | position_shrinkage | test | experience_group | sparse | 99 | 10.3155 | 10.8027 | 11.4998 | -0.00633564 |
| TE | games_active | baseline | position_shrinkage | test | experience_group | veteran | 136 | 5.01674 | 6.49626 | 3.5297 | 0.565393 |
| TE | games_active | baseline | position_shrinkage | test | projection_tier | lower | 59 | 7.05853 | 7.56986 | 7.78309 | 0.159774 |
| TE | games_active | baseline | position_shrinkage | test | projection_tier | middle | 117 | 9.03531 | 9.98419 | 10.944 | 0.415784 |
| TE | games_active | baseline | position_shrinkage | test | projection_tier | top | 59 | 3.89706 | 6.17362 | 1.71614 | 0.170427 |
| WR | fantasy_points_per_game | baseline | age_position_adjusted | validation | experience_group | sparse | 224 | 2.23957 | 3.03568 | 1.61927 | 0.676764 |
| WR | fantasy_points_per_game | baseline | age_position_adjusted | validation | experience_group | veteran | 765 | 2.63365 | 3.41657 | 2.07878 | 0.775935 |
| WR | fantasy_points_per_game | baseline | age_position_adjusted | validation | projection_tier | lower | 159 | 1.53549 | 2.63091 | 0.675 | 0.073375 |
| WR | fantasy_points_per_game | baseline | age_position_adjusted | validation | projection_tier | middle | 387 | 2.26649 | 2.84687 | 1.79846 | 0.286839 |
| WR | fantasy_points_per_game | baseline | age_position_adjusted | validation | projection_tier | top | 443 | 3.14928 | 3.90549 | 2.81959 | 0.713489 |
| WR | fantasy_points_per_game | baseline | age_position_adjusted | test | experience_group | sparse | 47 | 2.2755 | 2.9701 | 1.86542 | 0.700013 |
| WR | fantasy_points_per_game | baseline | age_position_adjusted | test | experience_group | veteran | 151 | 2.3128 | 2.99044 | 1.81896 | 0.842961 |
| WR | fantasy_points_per_game | baseline | age_position_adjusted | test | projection_tier | lower | 35 | 1.17654 | 1.61158 | 0.812376 | -0.0211589 |
| WR | fantasy_points_per_game | baseline | age_position_adjusted | test | projection_tier | middle | 74 | 1.74476 | 2.1867 | 1.35904 | 0.478465 |
| WR | fantasy_points_per_game | baseline | age_position_adjusted | test | projection_tier | top | 89 | 3.21225 | 3.85148 | 2.96424 | 0.712734 |
| WR | fantasy_points_total | baseline | age_position_adjusted | validation | experience_group | sparse | 920 | 29.1747 | 40.8782 | 19.3601 | 0.236719 |
| WR | fantasy_points_total | baseline | age_position_adjusted | validation | experience_group | veteran | 1189 | 36.8256 | 52.2496 | 26.0288 | 0.696278 |
| WR | fantasy_points_total | baseline | age_position_adjusted | validation | projection_tier | lower | 528 | 4.6298 | 14.9478 | 1.32111 | 0.0816632 |
| WR | fantasy_points_total | baseline | age_position_adjusted | validation | projection_tier | middle | 1053 | 34.6198 | 41.6816 | 33 | 0.020319 |
| WR | fantasy_points_total | baseline | age_position_adjusted | validation | projection_tier | top | 528 | 60.0893 | 73.2876 | 57.8277 | 0.681212 |
| WR | fantasy_points_total | baseline | age_position_adjusted | test | experience_group | sparse | 201 | 30.0886 | 43.7643 | 17.7 | 0.179625 |
| WR | fantasy_points_total | baseline | age_position_adjusted | test | experience_group | veteran | 233 | 34.8814 | 51.7961 | 20.6222 | 0.733783 |
| WR | fantasy_points_total | baseline | age_position_adjusted | test | projection_tier | lower | 109 | 3.97061 | 9.67381 | 1.00656 | 0.089669 |
| WR | fantasy_points_total | baseline | age_position_adjusted | test | projection_tier | middle | 216 | 31.5113 | 38.0848 | 27.2148 | -0.0748649 |
| WR | fantasy_points_total | baseline | age_position_adjusted | test | projection_tier | top | 109 | 63.6323 | 79.3658 | 57.4219 | 0.569872 |
| WR | games_active | baseline | age_position_adjusted | validation | experience_group | sparse | 912 | 6.6177 | 8.05131 | 6 | 0.308418 |
| WR | games_active | baseline | age_position_adjusted | validation | experience_group | veteran | 1189 | 5.4182 | 6.85931 | 4.5 | 0.539467 |
| WR | games_active | baseline | age_position_adjusted | validation | projection_tier | lower | 528 | 3.22029 | 3.97021 | 3 | 0.108655 |
| WR | games_active | baseline | age_position_adjusted | validation | projection_tier | middle | 1045 | 7.67236 | 8.50764 | 8.25 | 0.249945 |
| WR | games_active | baseline | age_position_adjusted | validation | projection_tier | top | 528 | 5.22662 | 7.67499 | 2.15 | 0.239606 |
| WR | games_active | baseline | age_position_adjusted | test | experience_group | sparse | 200 | 7.36129 | 8.70791 | 8.5 | 0.0869547 |
| WR | games_active | baseline | age_position_adjusted | test | experience_group | veteran | 233 | 5.59215 | 7.21297 | 4.4 | 0.48778 |
| WR | games_active | baseline | age_position_adjusted | test | projection_tier | lower | 109 | 3.66938 | 4.72651 | 3 | 0.0821372 |
| WR | games_active | baseline | age_position_adjusted | test | projection_tier | middle | 215 | 8.08068 | 9.00007 | 9.9 | 0.16327 |
| WR | games_active | baseline | age_position_adjusted | test | projection_tier | top | 109 | 5.85249 | 8.26039 | 3 | 0.0493307 |

## Candidate comparison

| Position | Target | Source | Candidate | Validation rows | Validation MAE | Test rows | Test MAE |
|---|---|---|---|---|---|---|---|
| QB | fantasy_points_per_game | baseline | age_position_adjusted | 348 | 4.24031 | 66 | 4.66078 |
| QB | fantasy_points_per_game | baseline | position_shrinkage | 348 | 4.38818 | 66 | 4.69889 |
| QB | fantasy_points_per_game | baseline | previous_season | 348 | 4.80754 | 66 | 5.24308 |
| QB | fantasy_points_per_game | baseline | weighted_components | 348 | 4.26592 | 66 | 4.6922 |
| QB | fantasy_points_per_game | baseline | weighted_history | 348 | 4.26592 | 66 | 4.6922 |
| QB | fantasy_points_per_game | learned | hist_gradient_boosting | 348 | 4.23961 | 66 | 4.34153 |
| QB | fantasy_points_per_game | learned | ridge | 348 | 4.31211 | 66 | 4.30708 |
| QB | fantasy_points_total | baseline | age_position_adjusted | 618 | 51.6408 | 124 | 51.7395 |
| QB | fantasy_points_total | baseline | position_shrinkage | 618 | 65.6892 | 124 | 66.4154 |
| QB | fantasy_points_total | baseline | previous_season | 618 | 64.7518 | 124 | 68.4777 |
| QB | fantasy_points_total | baseline | weighted_components | 618 | 52.8707 | 124 | 52.4134 |
| QB | fantasy_points_total | baseline | weighted_history | 618 | 52.8707 | 124 | 52.4134 |
| QB | fantasy_points_total | learned | hist_gradient_boosting | 618 | 41.3552 | 124 | 37.9816 |
| QB | fantasy_points_total | learned | ridge | 618 | 45.3072 | 124 | 43.507 |
| QB | games_active | baseline | age_position_adjusted | 618 | 4.09064 | 124 | 4.06355 |
| QB | games_active | baseline | position_shrinkage | 618 | 5.22732 | 124 | 5.3718 |
| QB | games_active | baseline | previous_season | 618 | 5.05585 | 124 | 5.33105 |
| QB | games_active | baseline | weighted_components | 618 | 4.09064 | 124 | 4.06355 |
| QB | games_active | baseline | weighted_history | 618 | 4.09064 | 124 | 4.06355 |
| QB | games_active | learned | hist_gradient_boosting | 618 | 2.53429 | 124 | 2.27844 |
| QB | games_active | learned | ridge | 618 | 2.44782 | 124 | 2.30205 |
| RB | fantasy_points_per_game | baseline | age_position_adjusted | 686 | 2.69753 | 128 | 2.33592 |
| RB | fantasy_points_per_game | baseline | position_shrinkage | 686 | 2.84192 | 128 | 2.72047 |
| RB | fantasy_points_per_game | baseline | previous_season | 686 | 2.8652 | 128 | 2.47996 |
| RB | fantasy_points_per_game | baseline | weighted_components | 686 | 2.78325 | 128 | 2.49616 |
| RB | fantasy_points_per_game | baseline | weighted_history | 686 | 2.78325 | 128 | 2.49616 |
| RB | fantasy_points_per_game | learned | hist_gradient_boosting | 686 | 2.66504 | 128 | 2.36122 |
| RB | fantasy_points_per_game | learned | ridge | 686 | 2.666 | 128 | 2.2728 |
| RB | fantasy_points_total | baseline | age_position_adjusted | 1488 | 35.4954 | 294 | 34.7254 |
| RB | fantasy_points_total | baseline | position_shrinkage | 1488 | 45.6875 | 294 | 46.4857 |
| RB | fantasy_points_total | baseline | previous_season | 1488 | 47.9314 | 294 | 48.1701 |
| RB | fantasy_points_total | baseline | weighted_components | 1488 | 37.8594 | 294 | 37.5788 |
| RB | fantasy_points_total | baseline | weighted_history | 1488 | 37.8594 | 294 | 37.5788 |
| RB | fantasy_points_total | learned | hist_gradient_boosting | 1488 | 23.2001 | 294 | 22.3794 |
| RB | fantasy_points_total | learned | ridge | 1488 | 27.0683 | 294 | 27.1653 |
| RB | games_active | baseline | age_position_adjusted | 1483 | 6.17816 | 294 | 6.81933 |
| RB | games_active | baseline | position_shrinkage | 1483 | 7.26169 | 294 | 7.93044 |
| RB | games_active | baseline | previous_season | 1483 | 7.18794 | 294 | 7.84813 |
| RB | games_active | baseline | weighted_components | 1483 | 6.17816 | 294 | 6.81933 |
| RB | games_active | baseline | weighted_history | 1483 | 6.17816 | 294 | 6.81933 |
| RB | games_active | learned | hist_gradient_boosting | 1483 | 3.00524 | 294 | 2.67123 |
| RB | games_active | learned | ridge | 1483 | 3.12443 | 294 | 3.02363 |
| TE | fantasy_points_per_game | baseline | age_position_adjusted | 565 | 1.78452 | 122 | 1.65771 |
| TE | fantasy_points_per_game | baseline | position_shrinkage | 565 | 1.89745 | 122 | 1.88063 |
| TE | fantasy_points_per_game | baseline | previous_season | 565 | 1.90567 | 122 | 1.90235 |
| TE | fantasy_points_per_game | baseline | weighted_components | 565 | 1.79923 | 122 | 1.6748 |
| TE | fantasy_points_per_game | baseline | weighted_history | 565 | 1.79923 | 122 | 1.6748 |
| TE | fantasy_points_per_game | learned | hist_gradient_boosting | 565 | 1.76886 | 122 | 1.5948 |
| TE | fantasy_points_per_game | learned | ridge | 565 | 1.91531 | 122 | 1.76203 |
| TE | fantasy_points_total | baseline | age_position_adjusted | 1160 | 23.9423 | 237 | 22.4411 |
| TE | fantasy_points_total | baseline | position_shrinkage | 1160 | 29.4239 | 237 | 27.6593 |
| TE | fantasy_points_total | baseline | previous_season | 1160 | 30.7262 | 237 | 31.3559 |
| TE | fantasy_points_total | baseline | weighted_components | 1160 | 24.575 | 237 | 23.0995 |
| TE | fantasy_points_total | baseline | weighted_history | 1160 | 24.575 | 237 | 23.0995 |
| TE | fantasy_points_total | learned | hist_gradient_boosting | 1160 | 16.3807 | 237 | 13.3255 |
| TE | fantasy_points_total | learned | ridge | 1160 | 19.1752 | 237 | 16.7748 |
| TE | games_active | baseline | age_position_adjusted | 1158 | 6.28561 | 235 | 6.16474 |
| TE | games_active | baseline | position_shrinkage | 1158 | 7.26705 | 235 | 7.24898 |
| TE | games_active | baseline | previous_season | 1158 | 7.11719 | 235 | 7.37428 |
| TE | games_active | baseline | weighted_components | 1158 | 6.28561 | 235 | 6.16474 |
| TE | games_active | baseline | weighted_history | 1158 | 6.28561 | 235 | 6.16474 |
| TE | games_active | learned | hist_gradient_boosting | 1158 | 3.25215 | 235 | 2.5701 |
| TE | games_active | learned | ridge | 1158 | 3.65206 | 235 | 2.86741 |
| WR | fantasy_points_per_game | baseline | age_position_adjusted | 989 | 2.54439 | 198 | 2.30394 |
| WR | fantasy_points_per_game | baseline | position_shrinkage | 989 | 2.77451 | 198 | 2.43741 |
| WR | fantasy_points_per_game | baseline | previous_season | 989 | 2.76831 | 198 | 2.56141 |
| WR | fantasy_points_per_game | baseline | weighted_components | 989 | 2.63116 | 198 | 2.41075 |
| WR | fantasy_points_per_game | baseline | weighted_history | 989 | 2.63116 | 198 | 2.41075 |
| WR | fantasy_points_per_game | learned | hist_gradient_boosting | 989 | 2.36737 | 198 | 2.1201 |
| WR | fantasy_points_per_game | learned | ridge | 989 | 2.57761 | 198 | 2.12691 |
| WR | fantasy_points_total | baseline | age_position_adjusted | 2109 | 33.4881 | 434 | 32.6617 |
| WR | fantasy_points_total | baseline | position_shrinkage | 2109 | 43.5474 | 434 | 41.3842 |
| WR | fantasy_points_total | baseline | previous_season | 2109 | 45.1961 | 434 | 44.8118 |
| WR | fantasy_points_total | baseline | weighted_components | 2109 | 34.9655 | 434 | 34.1085 |
| WR | fantasy_points_total | baseline | weighted_history | 2109 | 34.9655 | 434 | 34.1085 |
| WR | fantasy_points_total | learned | hist_gradient_boosting | 2109 | 21.5237 | 434 | 19.031 |
| WR | fantasy_points_total | learned | ridge | 2109 | 27.881 | 434 | 22.7653 |
| WR | games_active | baseline | age_position_adjusted | 2101 | 5.93888 | 433 | 6.40931 |
| WR | games_active | baseline | position_shrinkage | 2101 | 7.10354 | 433 | 7.39689 |
| WR | games_active | baseline | previous_season | 2101 | 7.04935 | 433 | 7.47264 |
| WR | games_active | baseline | weighted_components | 2101 | 5.93888 | 433 | 6.40931 |
| WR | games_active | baseline | weighted_history | 2101 | 5.93888 | 433 | 6.40931 |
| WR | games_active | learned | hist_gradient_boosting | 2101 | 2.91416 | 433 | 2.84212 |
| WR | games_active | learned | ridge | 2101 | 3.12805 | 433 | 2.94836 |

## Empirical uncertainty diagnostics

| Position | Target | Candidate | Scope | Season | Projection tier | Rows | P10-P90 coverage | Mean width | P10 pinball | P50 pinball | P90 pinball |
|---|---|---|---|---|---|---|---|---|---|---|---|
| QB | fantasy_points_per_game | hist_gradient_boosting | test | 2025 | all | 66 | 0.757576 | 12.471 | 1.00675 | 2.17077 | 0.909201 |
| QB | fantasy_points_per_game | hist_gradient_boosting | test | 2025 | top | 27 | 0.814815 | 12.471 | 1.14262 | 1.79656 | 0.789493 |
| QB | fantasy_points_per_game | hist_gradient_boosting | test | 2025 | middle | 32 | 0.6875 | 12.471 | 0.968081 | 2.61461 | 0.947055 |
| QB | fantasy_points_per_game | hist_gradient_boosting | test | 2025 | lower | 7 | 0.857143 | 12.471 | 0.659405 | 1.58513 | 1.19789 |
| QB | fantasy_points_per_game | hist_gradient_boosting | validation | 2020 | all | 68 | 0.794118 | 14.5238 | 1.09263 | 2.27849 | 1.00336 |
| QB | fantasy_points_per_game | hist_gradient_boosting | validation | 2020 | top | 29 | 0.862069 | 14.5238 | 1.32935 | 2.33046 | 0.788927 |
| QB | fantasy_points_per_game | hist_gradient_boosting | validation | 2020 | middle | 30 | 0.7 | 14.5238 | 0.901964 | 2.39586 | 1.28467 |
| QB | fantasy_points_per_game | hist_gradient_boosting | validation | 2020 | lower | 9 | 0.888889 | 14.5238 | 0.965432 | 1.71979 | 0.756592 |
| QB | fantasy_points_per_game | hist_gradient_boosting | validation | 2021 | all | 68 | 0.808824 | 14.4021 | 1.20115 | 2.16944 | 1.05407 |
| QB | fantasy_points_per_game | hist_gradient_boosting | validation | 2021 | top | 27 | 0.851852 | 14.4021 | 1.41865 | 1.78251 | 1.02885 |
| QB | fantasy_points_per_game | hist_gradient_boosting | validation | 2021 | middle | 34 | 0.794118 | 14.4021 | 1.04893 | 2.39342 | 0.940804 |
| QB | fantasy_points_per_game | hist_gradient_boosting | validation | 2021 | lower | 7 | 0.714286 | 14.4021 | 1.10163 | 2.57396 | 1.70156 |
| QB | fantasy_points_per_game | hist_gradient_boosting | validation | 2022 | all | 74 | 0.891892 | 14.5651 | 0.77412 | 2.00627 | 0.988463 |
| QB | fantasy_points_per_game | hist_gradient_boosting | validation | 2022 | top | 29 | 0.931034 | 14.5651 | 0.653274 | 1.87443 | 0.895922 |
| QB | fantasy_points_per_game | hist_gradient_boosting | validation | 2022 | middle | 30 | 0.833333 | 14.5651 | 0.889731 | 2.35587 | 1.12693 |
| QB | fantasy_points_per_game | hist_gradient_boosting | validation | 2022 | lower | 15 | 0.933333 | 14.5651 | 0.776533 | 1.56197 | 0.890446 |
| QB | fantasy_points_per_game | hist_gradient_boosting | validation | 2023 | all | 70 | 0.742857 | 12.4906 | 1.06857 | 2.06725 | 1.04683 |
| QB | fantasy_points_per_game | hist_gradient_boosting | validation | 2023 | top | 27 | 0.814815 | 12.4906 | 1.34678 | 1.86408 | 0.864438 |
| QB | fantasy_points_per_game | hist_gradient_boosting | validation | 2023 | middle | 31 | 0.677419 | 12.4906 | 0.893411 | 2.22643 | 0.988468 |
| QB | fantasy_points_per_game | hist_gradient_boosting | validation | 2023 | lower | 12 | 0.75 | 12.4906 | 0.895069 | 2.11315 | 1.60797 |
| QB | fantasy_points_per_game | hist_gradient_boosting | validation | 2024 | all | 68 | 0.794118 | 12.4733 | 0.818613 | 2.08915 | 0.867735 |
| QB | fantasy_points_per_game | hist_gradient_boosting | validation | 2024 | top | 27 | 0.777778 | 12.4733 | 0.969422 | 1.99048 | 0.899755 |
| QB | fantasy_points_per_game | hist_gradient_boosting | validation | 2024 | middle | 37 | 0.783784 | 12.4733 | 0.728578 | 2.27308 | 0.871816 |
| QB | fantasy_points_per_game | hist_gradient_boosting | validation | 2024 | lower | 4 | 1 | 12.4733 | 0.633472 | 1.05392 | 0.613855 |
| QB | fantasy_points_per_game | ridge | test | 2025 | all | 66 | 0.712121 | 12.5435 | 0.882979 | 2.15354 | 0.936892 |
| QB | fantasy_points_per_game | ridge | test | 2025 | top | 30 | 0.766667 | 12.5435 | 1.01304 | 2.0012 | 0.881082 |
| QB | fantasy_points_per_game | ridge | test | 2025 | middle | 33 | 0.666667 | 12.5435 | 0.766205 | 2.34562 | 0.978558 |
| QB | fantasy_points_per_game | ridge | test | 2025 | lower | 3 | 0.666667 | 12.5435 | 0.86687 | 1.56408 | 1.03667 |
| QB | fantasy_points_per_game | ridge | validation | 2020 | all | 68 | 0.764706 | 13.733 | 1.22933 | 2.41058 | 1.13789 |
| QB | fantasy_points_per_game | ridge | validation | 2020 | top | 29 | 0.827586 | 13.733 | 1.5734 | 2.32885 | 0.828616 |
| QB | fantasy_points_per_game | ridge | validation | 2020 | middle | 31 | 0.741935 | 13.733 | 0.896859 | 2.24793 | 1.20811 |
| QB | fantasy_points_per_game | ridge | validation | 2020 | lower | 8 | 0.625 | 13.733 | 1.27036 | 3.33711 | 1.98693 |
| QB | fantasy_points_per_game | ridge | validation | 2021 | all | 68 | 0.779412 | 14.104 | 1.1138 | 2.3218 | 1.07799 |
| QB | fantasy_points_per_game | ridge | validation | 2021 | top | 27 | 0.851852 | 14.104 | 1.06432 | 1.98612 | 1.04715 |
| QB | fantasy_points_per_game | ridge | validation | 2021 | middle | 36 | 0.75 | 14.104 | 1.14055 | 2.39205 | 0.929929 |
| QB | fantasy_points_per_game | ridge | validation | 2021 | lower | 5 | 0.6 | 14.104 | 1.1884 | 3.62869 | 2.31059 |
| QB | fantasy_points_per_game | ridge | validation | 2022 | all | 74 | 0.851351 | 14.3104 | 0.811333 | 1.94092 | 0.93141 |
| QB | fantasy_points_per_game | ridge | validation | 2022 | top | 30 | 0.866667 | 14.3104 | 0.800082 | 1.8071 | 0.916281 |
| QB | fantasy_points_per_game | ridge | validation | 2022 | middle | 35 | 0.828571 | 14.3104 | 0.796061 | 2.08366 | 1.039 |
| QB | fantasy_points_per_game | ridge | validation | 2022 | lower | 9 | 0.888889 | 14.3104 | 0.908226 | 1.83187 | 0.563449 |
| QB | fantasy_points_per_game | ridge | validation | 2023 | all | 70 | 0.785714 | 13.9079 | 0.939729 | 2.17897 | 1.01789 |
| QB | fantasy_points_per_game | ridge | validation | 2023 | top | 29 | 0.862069 | 13.9079 | 0.981454 | 1.88073 | 0.910151 |
| QB | fantasy_points_per_game | ridge | validation | 2023 | middle | 34 | 0.676471 | 13.9079 | 0.938294 | 2.65624 | 1.19234 |
| QB | fantasy_points_per_game | ridge | validation | 2023 | lower | 7 | 1 | 13.9079 | 0.773838 | 1.0964 | 0.61695 |
| QB | fantasy_points_per_game | ridge | validation | 2024 | all | 68 | 0.808824 | 13.6638 | 0.847612 | 1.94632 | 0.904754 |
| QB | fantasy_points_per_game | ridge | validation | 2024 | top | 29 | 0.862069 | 13.6638 | 0.981268 | 1.66613 | 0.752929 |
| QB | fantasy_points_per_game | ridge | validation | 2024 | middle | 38 | 0.763158 | 13.6638 | 0.736598 | 2.13704 | 1.03979 |
| QB | fantasy_points_per_game | ridge | validation | 2024 | lower | 1 | 1 | 13.6638 | 1.19012 | 2.82432 | 0.176255 |
| QB | fantasy_points_total | hist_gradient_boosting | test | 2025 | all | 124 | 0.814516 | 142.6 | 10.3542 | 18.9908 | 14.2238 |
| QB | fantasy_points_total | hist_gradient_boosting | test | 2025 | top | 31 | 0.483871 | 142.6 | 21.6139 | 44.4237 | 26.2226 |
| QB | fantasy_points_total | hist_gradient_boosting | test | 2025 | middle | 62 | 0.887097 | 142.6 | 6.53886 | 14.6729 | 11.5689 |
| QB | fantasy_points_total | hist_gradient_boosting | test | 2025 | lower | 31 | 1 | 142.6 | 6.72521 | 2.19375 | 7.53479 |
| QB | fantasy_points_total | hist_gradient_boosting | validation | 2020 | all | 119 | 0.806723 | 148.185 | 10.9658 | 20.2945 | 14.1561 |
| QB | fantasy_points_total | hist_gradient_boosting | validation | 2020 | top | 30 | 0.5 | 148.185 | 21.4218 | 42.2562 | 19.8172 |
| QB | fantasy_points_total | hist_gradient_boosting | validation | 2020 | middle | 59 | 0.864407 | 148.185 | 7.31799 | 16.7968 | 14.8478 |
| QB | fantasy_points_total | hist_gradient_boosting | validation | 2020 | lower | 30 | 1 | 148.185 | 7.6839 | 5.21165 | 7.13463 |
| QB | fantasy_points_total | hist_gradient_boosting | validation | 2021 | all | 125 | 0.832 | 151.562 | 14.9932 | 20.8875 | 13.1927 |
| QB | fantasy_points_total | hist_gradient_boosting | validation | 2021 | top | 31 | 0.516129 | 151.562 | 40.1479 | 48.8823 | 16.4656 |
| QB | fantasy_points_total | hist_gradient_boosting | validation | 2021 | middle | 63 | 0.904762 | 151.562 | 6.55377 | 14.8693 | 14.0554 |
| QB | fantasy_points_total | hist_gradient_boosting | validation | 2021 | lower | 31 | 1 | 151.562 | 6.98944 | 5.12316 | 8.16679 |
| QB | fantasy_points_total | hist_gradient_boosting | validation | 2022 | all | 125 | 0.808 | 141.823 | 9.91844 | 18.3791 | 14.4688 |
| QB | fantasy_points_total | hist_gradient_boosting | validation | 2022 | top | 31 | 0.451613 | 141.823 | 19.9821 | 39.5104 | 21.906 |
| QB | fantasy_points_total | hist_gradient_boosting | validation | 2022 | middle | 63 | 0.904762 | 141.823 | 6.18573 | 13.7116 | 13.1582 |
| QB | fantasy_points_total | hist_gradient_boosting | validation | 2022 | lower | 31 | 0.967742 | 141.823 | 7.44061 | 6.73317 | 9.69521 |
| QB | fantasy_points_total | hist_gradient_boosting | validation | 2023 | all | 124 | 0.717742 | 135.143 | 15.4263 | 25.0078 | 17.0153 |
| QB | fantasy_points_total | hist_gradient_boosting | validation | 2023 | top | 31 | 0.193548 | 135.143 | 40.6864 | 54.631 | 24.853 |
| QB | fantasy_points_total | hist_gradient_boosting | validation | 2023 | middle | 62 | 0.854839 | 135.143 | 7.11067 | 19.0309 | 16.1837 |
| QB | fantasy_points_total | hist_gradient_boosting | validation | 2023 | lower | 31 | 0.967742 | 135.143 | 6.79733 | 7.33859 | 10.841 |
| QB | fantasy_points_total | hist_gradient_boosting | validation | 2024 | all | 125 | 0.816 | 149.084 | 10.7895 | 18.8354 | 13.8721 |
| QB | fantasy_points_total | hist_gradient_boosting | validation | 2024 | top | 31 | 0.516129 | 149.084 | 22.1666 | 41.2893 | 23.2277 |
| QB | fantasy_points_total | hist_gradient_boosting | validation | 2024 | middle | 63 | 0.873016 | 149.084 | 6.99703 | 15.9381 | 12.262 |
| QB | fantasy_points_total | hist_gradient_boosting | validation | 2024 | lower | 31 | 1 | 149.084 | 7.11983 | 2.26925 | 7.78858 |
| QB | fantasy_points_total | ridge | test | 2025 | all | 124 | 0.822581 | 145.971 | 11.7163 | 21.7535 | 12.6865 |
| QB | fantasy_points_total | ridge | test | 2025 | top | 31 | 0.516129 | 145.971 | 22.8505 | 42.9839 | 23.798 |
| QB | fantasy_points_total | ridge | test | 2025 | middle | 62 | 0.887097 | 145.971 | 7.38327 | 16.3775 | 10.7994 |
| QB | fantasy_points_total | ridge | test | 2025 | lower | 31 | 1 | 145.971 | 9.24816 | 11.2751 | 5.34898 |
| QB | fantasy_points_total | ridge | validation | 2020 | all | 119 | 0.798319 | 155.44 | 11.9989 | 23.2916 | 13.5163 |
| QB | fantasy_points_total | ridge | validation | 2020 | top | 30 | 0.5 | 155.44 | 23.6915 | 43.2029 | 20.03 |
| QB | fantasy_points_total | ridge | validation | 2020 | middle | 59 | 0.847458 | 155.44 | 7.27264 | 18.9388 | 14.0552 |
| QB | fantasy_points_total | ridge | validation | 2020 | lower | 30 | 1 | 155.44 | 9.60113 | 11.9407 | 5.94289 |
| QB | fantasy_points_total | ridge | validation | 2021 | all | 125 | 0.816 | 155.889 | 14.2809 | 23.6006 | 13.0298 |
| QB | fantasy_points_total | ridge | validation | 2021 | top | 31 | 0.645161 | 155.889 | 33.3908 | 41.9116 | 14.9267 |
| QB | fantasy_points_total | ridge | validation | 2021 | middle | 63 | 0.825397 | 155.889 | 7.99208 | 22.578 | 14.4015 |
| QB | fantasy_points_total | ridge | validation | 2021 | lower | 31 | 0.967742 | 155.889 | 7.95142 | 7.36801 | 8.34541 |
| QB | fantasy_points_total | ridge | validation | 2022 | all | 125 | 0.792 | 149.491 | 10.3756 | 20.8334 | 12.9092 |
| QB | fantasy_points_total | ridge | validation | 2022 | top | 31 | 0.580645 | 149.491 | 15.3723 | 34.6383 | 14.6843 |
| QB | fantasy_points_total | ridge | validation | 2022 | middle | 63 | 0.793651 | 149.491 | 8.95936 | 20.9426 | 15.095 |
| QB | fantasy_points_total | ridge | validation | 2022 | lower | 31 | 1 | 149.491 | 8.25721 | 6.80664 | 6.69184 |
| QB | fantasy_points_total | ridge | validation | 2023 | all | 124 | 0.806452 | 150.013 | 12.1755 | 23.8628 | 14.1693 |
| QB | fantasy_points_total | ridge | validation | 2023 | top | 31 | 0.451613 | 150.013 | 24.3672 | 43.8071 | 21.2843 |
| QB | fantasy_points_total | ridge | validation | 2023 | middle | 62 | 0.887097 | 150.013 | 7.29247 | 18.6663 | 15.0708 |
| QB | fantasy_points_total | ridge | validation | 2023 | lower | 31 | 1 | 150.013 | 9.74987 | 14.3116 | 5.2514 |
| QB | fantasy_points_total | ridge | validation | 2024 | all | 125 | 0.792 | 141.716 | 11.5246 | 21.7198 | 14.3542 |
| QB | fantasy_points_total | ridge | validation | 2024 | top | 31 | 0.548387 | 141.716 | 20.8673 | 38.2327 | 22.1336 |
| QB | fantasy_points_total | ridge | validation | 2024 | middle | 63 | 0.84127 | 141.716 | 7.72383 | 16.5838 | 12.1843 |
| QB | fantasy_points_total | ridge | validation | 2024 | lower | 31 | 0.935484 | 141.716 | 9.90603 | 15.6447 | 10.9845 |
| QB | games_active | hist_gradient_boosting | test | 2025 | all | 124 | 0.782258 | 6.8787 | 0.447755 | 1.13922 | 0.693021 |
| QB | games_active | hist_gradient_boosting | test | 2025 | top | 31 | 0.516129 | 8.11777 | 1.08727 | 2.14602 | 0.906186 |
| QB | games_active | hist_gradient_boosting | test | 2025 | middle | 62 | 0.806452 | 7.35508 | 0.351875 | 1.1948 | 0.698605 |
| QB | games_active | hist_gradient_boosting | test | 2025 | lower | 31 | 1 | 4.68686 | 0 | 0.0212545 | 0.468686 |
| QB | games_active | hist_gradient_boosting | validation | 2020 | all | 119 | 0.840336 | 6.87181 | 0.404731 | 1.22003 | 0.690392 |
| QB | games_active | hist_gradient_boosting | validation | 2020 | top | 30 | 0.766667 | 9.1925 | 0.897638 | 1.64968 | 0.65754 |
| QB | games_active | hist_gradient_boosting | validation | 2020 | middle | 59 | 0.813559 | 7.02904 | 0.331082 | 1.47785 | 0.850803 |
| QB | games_active | hist_gradient_boosting | validation | 2020 | lower | 30 | 0.966667 | 4.24189 | 0.0566667 | 0.283333 | 0.40777 |
| QB | games_active | hist_gradient_boosting | validation | 2021 | all | 125 | 0.808 | 6.68517 | 0.561987 | 1.19609 | 0.628551 |
| QB | games_active | hist_gradient_boosting | validation | 2021 | top | 31 | 0.548387 | 8.53038 | 1.64873 | 2.30246 | 0.712599 |
| QB | games_active | hist_gradient_boosting | validation | 2021 | middle | 63 | 0.873016 | 6.9073 | 0.27679 | 1.10482 | 0.676868 |
| QB | games_active | hist_gradient_boosting | validation | 2021 | lower | 31 | 0.935484 | 4.38853 | 0.0548387 | 0.275205 | 0.446312 |
| QB | games_active | hist_gradient_boosting | validation | 2022 | all | 125 | 0.84 | 6.91501 | 0.373143 | 1.1201 | 0.65469 |
| QB | games_active | hist_gradient_boosting | validation | 2022 | top | 31 | 0.677419 | 8.30301 | 0.753538 | 1.71687 | 0.502956 |
| QB | games_active | hist_gradient_boosting | validation | 2022 | middle | 63 | 0.857143 | 7.3342 | 0.350528 | 1.26303 | 0.836898 |
| QB | games_active | hist_gradient_boosting | validation | 2022 | lower | 31 | 0.967742 | 4.67512 | 0.0387097 | 0.23287 | 0.436131 |
| QB | games_active | hist_gradient_boosting | validation | 2023 | all | 124 | 0.741935 | 6.62728 | 0.666984 | 1.51803 | 0.90295 |
| QB | games_active | hist_gradient_boosting | validation | 2023 | top | 31 | 0.580645 | 7.633 | 1.74922 | 2.36237 | 0.76703 |
| QB | games_active | hist_gradient_boosting | validation | 2023 | middle | 62 | 0.709677 | 7.10749 | 0.440002 | 1.73337 | 1.20847 |
| QB | games_active | hist_gradient_boosting | validation | 2023 | lower | 31 | 0.967742 | 4.66115 | 0.0387097 | 0.243014 | 0.427827 |
| QB | games_active | hist_gradient_boosting | validation | 2024 | all | 125 | 0.784 | 6.83902 | 0.557692 | 1.28121 | 0.694771 |
| QB | games_active | hist_gradient_boosting | validation | 2024 | top | 31 | 0.580645 | 7.75847 | 1.36257 | 2.11881 | 0.626999 |
| QB | games_active | hist_gradient_boosting | validation | 2024 | middle | 63 | 0.793651 | 7.32792 | 0.415424 | 1.37935 | 0.838818 |
| QB | games_active | hist_gradient_boosting | validation | 2024 | lower | 31 | 0.967742 | 4.92603 | 0.0419355 | 0.244143 | 0.469803 |
| QB | games_active | ridge | test | 2025 | all | 124 | 0.822581 | 6.79083 | 0.475112 | 1.15102 | 0.615784 |
| QB | games_active | ridge | test | 2025 | top | 31 | 0.548387 | 8.28431 | 1.25535 | 2.22266 | 0.721369 |
| QB | games_active | ridge | test | 2025 | middle | 62 | 0.870968 | 7.4329 | 0.316096 | 1.15216 | 0.676674 |
| QB | games_active | ridge | test | 2025 | lower | 31 | 1 | 4.01321 | 0.0129032 | 0.077116 | 0.388418 |
| QB | games_active | ridge | validation | 2020 | all | 119 | 0.806723 | 5.91173 | 0.402545 | 1.13104 | 0.630158 |
| QB | games_active | ridge | validation | 2020 | top | 30 | 0.7 | 8.84638 | 1.00417 | 1.85742 | 0.564905 |
| QB | games_active | ridge | validation | 2020 | middle | 59 | 0.762712 | 5.83075 | 0.289452 | 1.27748 | 0.836148 |
| QB | games_active | ridge | validation | 2020 | lower | 30 | 1 | 3.13632 | 0.0233333 | 0.116667 | 0.290299 |
| QB | games_active | ridge | validation | 2021 | all | 125 | 0.8 | 6.4275 | 0.518346 | 1.23226 | 0.622626 |
| QB | games_active | ridge | validation | 2021 | top | 31 | 0.645161 | 7.85616 | 1.25945 | 1.91315 | 0.537839 |
| QB | games_active | ridge | validation | 2021 | middle | 63 | 0.809524 | 7.05218 | 0.386515 | 1.38849 | 0.751099 |
| QB | games_active | ridge | validation | 2021 | lower | 31 | 0.935484 | 3.72934 | 0.0451613 | 0.233883 | 0.446322 |
| QB | games_active | ridge | validation | 2022 | all | 125 | 0.8 | 6.67742 | 0.41537 | 1.15894 | 0.684369 |
| QB | games_active | ridge | validation | 2022 | top | 31 | 0.677419 | 8.09898 | 0.807528 | 1.56664 | 0.605286 |
| QB | games_active | ridge | validation | 2022 | middle | 63 | 0.793651 | 7.24331 | 0.407745 | 1.36584 | 0.822309 |
| QB | games_active | ridge | validation | 2022 | lower | 31 | 0.935484 | 4.10583 | 0.0387097 | 0.330765 | 0.483122 |
| QB | games_active | ridge | validation | 2023 | all | 124 | 0.782258 | 6.75036 | 0.51264 | 1.35546 | 0.808777 |
| QB | games_active | ridge | validation | 2023 | top | 31 | 0.516129 | 8.04256 | 1.25148 | 2.09934 | 0.719958 |
| QB | games_active | ridge | validation | 2023 | middle | 62 | 0.822581 | 7.35609 | 0.373731 | 1.50847 | 1.03945 |
| QB | games_active | ridge | validation | 2023 | lower | 31 | 0.967742 | 4.2467 | 0.0516129 | 0.305574 | 0.436248 |
| QB | games_active | ridge | validation | 2024 | all | 125 | 0.792 | 6.75867 | 0.506206 | 1.23844 | 0.720568 |
| QB | games_active | ridge | validation | 2024 | top | 31 | 0.645161 | 8.28258 | 1.00045 | 1.81727 | 0.632097 |
| QB | games_active | ridge | validation | 2024 | middle | 63 | 0.777778 | 7.29682 | 0.496221 | 1.4801 | 0.907923 |
| QB | games_active | ridge | validation | 2024 | lower | 31 | 0.967742 | 4.1411 | 0.0322581 | 0.168489 | 0.428286 |
| RB | fantasy_points_per_game | hist_gradient_boosting | test | 2025 | all | 128 | 0.875 | 9.1777 | 0.558527 | 1.18061 | 0.674069 |
| RB | fantasy_points_per_game | hist_gradient_boosting | test | 2025 | top | 60 | 0.783333 | 9.1777 | 0.706646 | 1.46981 | 0.759995 |
| RB | fantasy_points_per_game | hist_gradient_boosting | test | 2025 | middle | 49 | 0.938776 | 9.1777 | 0.404821 | 1.07038 | 0.663264 |
| RB | fantasy_points_per_game | hist_gradient_boosting | test | 2025 | lower | 19 | 1 | 9.1777 | 0.487182 | 0.551622 | 0.430588 |
| RB | fantasy_points_per_game | hist_gradient_boosting | validation | 2020 | all | 137 | 0.759124 | 9.54099 | 0.656028 | 1.40342 | 0.785169 |
| RB | fantasy_points_per_game | hist_gradient_boosting | validation | 2020 | top | 68 | 0.617647 | 9.54099 | 0.804998 | 1.82989 | 0.882687 |
| RB | fantasy_points_per_game | hist_gradient_boosting | validation | 2020 | middle | 48 | 0.854167 | 9.54099 | 0.534946 | 1.27564 | 0.770164 |
| RB | fantasy_points_per_game | hist_gradient_boosting | validation | 2020 | lower | 21 | 1 | 9.54099 | 0.450407 | 0.314564 | 0.503692 |
| RB | fantasy_points_per_game | hist_gradient_boosting | validation | 2021 | all | 149 | 0.838926 | 9.80881 | 0.576161 | 1.32547 | 0.669974 |
| RB | fantasy_points_per_game | hist_gradient_boosting | validation | 2021 | top | 65 | 0.769231 | 9.80881 | 0.644205 | 1.71805 | 0.71995 |
| RB | fantasy_points_per_game | hist_gradient_boosting | validation | 2021 | middle | 53 | 0.867925 | 9.80881 | 0.529101 | 1.27161 | 0.658334 |
| RB | fantasy_points_per_game | hist_gradient_boosting | validation | 2021 | lower | 31 | 0.935484 | 9.80881 | 0.513945 | 0.594427 | 0.585084 |
| RB | fantasy_points_per_game | hist_gradient_boosting | validation | 2022 | all | 139 | 0.848921 | 9.66657 | 0.568101 | 1.2713 | 0.712298 |
| RB | fantasy_points_per_game | hist_gradient_boosting | validation | 2022 | top | 63 | 0.714286 | 9.66657 | 0.762435 | 1.72003 | 0.819431 |
| RB | fantasy_points_per_game | hist_gradient_boosting | validation | 2022 | middle | 53 | 0.943396 | 9.66657 | 0.395041 | 1.14181 | 0.663163 |
| RB | fantasy_points_per_game | hist_gradient_boosting | validation | 2022 | lower | 23 | 1 | 9.66657 | 0.434587 | 0.340552 | 0.53207 |
| RB | fantasy_points_per_game | hist_gradient_boosting | validation | 2023 | all | 134 | 0.820896 | 9.38721 | 0.566834 | 1.4065 | 0.824783 |
| RB | fantasy_points_per_game | hist_gradient_boosting | validation | 2023 | top | 56 | 0.714286 | 9.38721 | 0.699319 | 1.79315 | 0.834942 |
| RB | fantasy_points_per_game | hist_gradient_boosting | validation | 2023 | middle | 53 | 0.867925 | 9.38721 | 0.457521 | 1.35789 | 0.873082 |
| RB | fantasy_points_per_game | hist_gradient_boosting | validation | 2023 | lower | 25 | 0.96 | 9.38721 | 0.501809 | 0.643447 | 0.69963 |
| RB | fantasy_points_per_game | hist_gradient_boosting | validation | 2024 | all | 127 | 0.818898 | 9.05071 | 0.506814 | 1.25324 | 0.756742 |
| RB | fantasy_points_per_game | hist_gradient_boosting | validation | 2024 | top | 56 | 0.678571 | 9.05071 | 0.616602 | 1.85582 | 0.895709 |
| RB | fantasy_points_per_game | hist_gradient_boosting | validation | 2024 | middle | 48 | 0.895833 | 9.05071 | 0.430182 | 0.977851 | 0.714935 |
| RB | fantasy_points_per_game | hist_gradient_boosting | validation | 2024 | lower | 23 | 1 | 9.05071 | 0.399434 | 0.360804 | 0.505638 |
| RB | fantasy_points_per_game | ridge | test | 2025 | all | 128 | 0.84375 | 8.74688 | 0.50668 | 1.1364 | 0.660078 |
| RB | fantasy_points_per_game | ridge | test | 2025 | top | 64 | 0.71875 | 8.74688 | 0.646986 | 1.37842 | 0.731773 |
| RB | fantasy_points_per_game | ridge | test | 2025 | middle | 45 | 0.955556 | 8.74688 | 0.329123 | 1.03592 | 0.65944 |
| RB | fantasy_points_per_game | ridge | test | 2025 | lower | 19 | 1 | 8.74688 | 0.454601 | 0.559149 | 0.420087 |
| RB | fantasy_points_per_game | ridge | validation | 2020 | all | 137 | 0.846715 | 10.3827 | 0.670225 | 1.38571 | 0.719969 |
| RB | fantasy_points_per_game | ridge | validation | 2020 | top | 71 | 0.732394 | 10.3827 | 0.832233 | 1.86231 | 0.772662 |
| RB | fantasy_points_per_game | ridge | validation | 2020 | middle | 56 | 0.964286 | 10.3827 | 0.486319 | 0.920051 | 0.69451 |
| RB | fantasy_points_per_game | ridge | validation | 2020 | lower | 10 | 1 | 10.3827 | 0.549845 | 0.60954 | 0.488421 |
| RB | fantasy_points_per_game | ridge | validation | 2021 | all | 149 | 0.838926 | 9.72135 | 0.615693 | 1.40474 | 0.708208 |
| RB | fantasy_points_per_game | ridge | validation | 2021 | top | 69 | 0.782609 | 9.72135 | 0.619028 | 1.58575 | 0.745752 |
| RB | fantasy_points_per_game | ridge | validation | 2021 | middle | 63 | 0.888889 | 9.72135 | 0.591233 | 1.19577 | 0.659024 |
| RB | fantasy_points_per_game | ridge | validation | 2021 | lower | 17 | 0.882353 | 9.72135 | 0.692802 | 1.44449 | 0.738095 |
| RB | fantasy_points_per_game | ridge | validation | 2022 | all | 139 | 0.81295 | 9.17823 | 0.54476 | 1.25005 | 0.69131 |
| RB | fantasy_points_per_game | ridge | validation | 2022 | top | 68 | 0.691176 | 9.17823 | 0.67986 | 1.6687 | 0.760666 |
| RB | fantasy_points_per_game | ridge | validation | 2022 | middle | 55 | 0.909091 | 9.17823 | 0.39774 | 0.971051 | 0.67813 |
| RB | fantasy_points_per_game | ridge | validation | 2022 | lower | 16 | 1 | 9.17823 | 0.47597 | 0.429823 | 0.441854 |
| RB | fantasy_points_per_game | ridge | validation | 2023 | all | 134 | 0.828358 | 9.0594 | 0.593139 | 1.33787 | 0.755699 |
| RB | fantasy_points_per_game | ridge | validation | 2023 | top | 66 | 0.69697 | 9.0594 | 0.77542 | 1.84489 | 0.907621 |
| RB | fantasy_points_per_game | ridge | validation | 2023 | middle | 52 | 0.942308 | 9.0594 | 0.394 | 0.949799 | 0.666934 |
| RB | fantasy_points_per_game | ridge | validation | 2023 | lower | 16 | 1 | 9.0594 | 0.488431 | 0.507619 | 0.417509 |
| RB | fantasy_points_per_game | ridge | validation | 2024 | all | 127 | 0.795276 | 8.80126 | 0.559004 | 1.27761 | 0.702287 |
| RB | fantasy_points_per_game | ridge | validation | 2024 | top | 66 | 0.666667 | 8.80126 | 0.646737 | 1.64634 | 0.813065 |
| RB | fantasy_points_per_game | ridge | validation | 2024 | middle | 49 | 0.918367 | 8.80126 | 0.447457 | 0.918292 | 0.639798 |
| RB | fantasy_points_per_game | ridge | validation | 2024 | lower | 12 | 1 | 8.80126 | 0.531949 | 0.716826 | 0.348176 |
| RB | fantasy_points_total | hist_gradient_boosting | test | 2025 | all | 294 | 0.79932 | 73.932 | 7.43445 | 11.1897 | 9.68371 |
| RB | fantasy_points_total | hist_gradient_boosting | test | 2025 | top | 74 | 0.310811 | 73.932 | 20.0009 | 33.1781 | 22.9331 |
| RB | fantasy_points_total | hist_gradient_boosting | test | 2025 | middle | 146 | 0.945205 | 73.932 | 3.11223 | 5.11797 | 5.85026 |
| RB | fantasy_points_total | hist_gradient_boosting | test | 2025 | lower | 74 | 1 | 73.932 | 3.39562 | 1.18069 | 3.99758 |
| RB | fantasy_points_total | hist_gradient_boosting | validation | 2020 | all | 302 | 0.817881 | 90.5778 | 9.56395 | 12.8846 | 9.30777 |
| RB | fantasy_points_total | hist_gradient_boosting | validation | 2020 | top | 76 | 0.447368 | 90.5778 | 24.4577 | 32.5361 | 15.8668 |
| RB | fantasy_points_total | hist_gradient_boosting | validation | 2020 | middle | 150 | 0.913333 | 90.5778 | 4.63659 | 8.04631 | 8.33813 |
| RB | fantasy_points_total | hist_gradient_boosting | validation | 2020 | lower | 76 | 1 | 90.5778 | 4.39523 | 2.7822 | 4.66254 |
| RB | fantasy_points_total | hist_gradient_boosting | validation | 2021 | all | 302 | 0.807947 | 86.9316 | 6.45152 | 11.3884 | 9.05452 |
| RB | fantasy_points_total | hist_gradient_boosting | validation | 2021 | top | 76 | 0.394737 | 86.9316 | 12.6027 | 27.0553 | 16.2033 |
| RB | fantasy_points_total | hist_gradient_boosting | validation | 2021 | middle | 150 | 0.92 | 86.9316 | 4.44297 | 8.31238 | 7.77633 |
| RB | fantasy_points_total | hist_gradient_boosting | validation | 2021 | lower | 76 | 1 | 86.9316 | 4.26464 | 1.79279 | 4.42852 |
| RB | fantasy_points_total | hist_gradient_boosting | validation | 2022 | all | 297 | 0.818182 | 81.9894 | 6.51171 | 11.5469 | 9.92085 |
| RB | fantasy_points_total | hist_gradient_boosting | validation | 2022 | top | 74 | 0.459459 | 81.9894 | 14.9377 | 29.0282 | 20.5971 |
| RB | fantasy_points_total | hist_gradient_boosting | validation | 2022 | middle | 149 | 0.90604 | 81.9894 | 3.684 | 8.25664 | 7.35072 |
| RB | fantasy_points_total | hist_gradient_boosting | validation | 2022 | lower | 74 | 1 | 81.9894 | 3.77937 | 0.690524 | 4.41957 |
| RB | fantasy_points_total | hist_gradient_boosting | validation | 2023 | all | 292 | 0.794521 | 76.511 | 6.80062 | 11.5818 | 10.1497 |
| RB | fantasy_points_total | hist_gradient_boosting | validation | 2023 | top | 73 | 0.30137 | 76.511 | 16.7402 | 31.274 | 22.012 |
| RB | fantasy_points_total | hist_gradient_boosting | validation | 2023 | middle | 146 | 0.938356 | 76.511 | 3.4627 | 7.24811 | 7.23631 |
| RB | fantasy_points_total | hist_gradient_boosting | validation | 2023 | lower | 73 | 1 | 76.511 | 3.53693 | 0.556938 | 4.11417 |
| RB | fantasy_points_total | hist_gradient_boosting | validation | 2024 | all | 295 | 0.833898 | 80.1631 | 5.7773 | 10.5733 | 9.84861 |
| RB | fantasy_points_total | hist_gradient_boosting | validation | 2024 | top | 74 | 0.432432 | 80.1631 | 12.2009 | 29.4941 | 23.1307 |
| RB | fantasy_points_total | hist_gradient_boosting | validation | 2024 | middle | 147 | 0.952381 | 80.1631 | 3.57784 | 6.05047 | 5.95887 |
| RB | fantasy_points_total | hist_gradient_boosting | validation | 2024 | lower | 74 | 1 | 80.1631 | 3.72292 | 0.637027 | 4.29339 |
| RB | fantasy_points_total | ridge | test | 2025 | all | 294 | 0.768707 | 77.5171 | 7.33513 | 13.5827 | 9.15553 |
| RB | fantasy_points_total | ridge | test | 2025 | top | 74 | 0.297297 | 77.5171 | 18.7181 | 31.9289 | 19.7273 |
| RB | fantasy_points_total | ridge | test | 2025 | middle | 146 | 0.890411 | 77.5171 | 3.08525 | 9.27819 | 6.707 |
| RB | fantasy_points_total | ridge | test | 2025 | lower | 74 | 1 | 77.5171 | 4.3371 | 3.72909 | 3.41461 |
| RB | fantasy_points_total | ridge | validation | 2020 | all | 302 | 0.821192 | 93.3159 | 8.66729 | 13.7383 | 8.31747 |
| RB | fantasy_points_total | ridge | validation | 2020 | top | 76 | 0.421053 | 93.3159 | 18.6779 | 30.2875 | 15.6354 |
| RB | fantasy_points_total | ridge | validation | 2020 | middle | 150 | 0.953333 | 93.3159 | 4.64365 | 7.93217 | 7.28576 |
| RB | fantasy_points_total | ridge | validation | 2020 | lower | 76 | 0.960526 | 93.3159 | 6.5981 | 8.64857 | 3.03581 |
| RB | fantasy_points_total | ridge | validation | 2021 | all | 302 | 0.807947 | 91.0489 | 6.90902 | 14.1452 | 9.40865 |
| RB | fantasy_points_total | ridge | validation | 2021 | top | 76 | 0.447368 | 91.0489 | 11.5994 | 28.2307 | 18.3626 |
| RB | fantasy_points_total | ridge | validation | 2021 | middle | 150 | 0.913333 | 91.0489 | 4.69358 | 9.37814 | 7.29857 |
| RB | fantasy_points_total | ridge | validation | 2021 | lower | 76 | 0.960526 | 91.0489 | 6.59122 | 9.46827 | 4.61938 |
| RB | fantasy_points_total | ridge | validation | 2022 | all | 297 | 0.83165 | 86.8362 | 6.80612 | 13.6037 | 9.63084 |
| RB | fantasy_points_total | ridge | validation | 2022 | top | 74 | 0.459459 | 86.8362 | 14.1529 | 29.9861 | 19.8182 |
| RB | fantasy_points_total | ridge | validation | 2022 | middle | 149 | 0.932886 | 86.8362 | 3.86852 | 9.48519 | 7.71085 |
| RB | fantasy_points_total | ridge | validation | 2022 | lower | 74 | 1 | 86.8362 | 5.37423 | 5.51413 | 3.30938 |
| RB | fantasy_points_total | ridge | validation | 2023 | all | 292 | 0.811644 | 82.4302 | 6.86511 | 13.3325 | 9.84864 |
| RB | fantasy_points_total | ridge | validation | 2023 | top | 73 | 0.356164 | 82.4302 | 16.0795 | 31.1804 | 20.8755 |
| RB | fantasy_points_total | ridge | validation | 2023 | middle | 146 | 0.945205 | 82.4302 | 3.3148 | 9.33236 | 7.51371 |
| RB | fantasy_points_total | ridge | validation | 2023 | lower | 73 | 1 | 82.4302 | 4.75137 | 3.48499 | 3.49164 |
| RB | fantasy_points_total | ridge | validation | 2024 | all | 295 | 0.80339 | 79.0388 | 6.43508 | 12.8291 | 9.90329 |
| RB | fantasy_points_total | ridge | validation | 2024 | top | 74 | 0.351351 | 79.0388 | 13.415 | 31.0706 | 24.1364 |
| RB | fantasy_points_total | ridge | validation | 2024 | middle | 147 | 0.952381 | 79.0388 | 3.51178 | 6.75855 | 5.9199 |
| RB | fantasy_points_total | ridge | validation | 2024 | lower | 74 | 0.959459 | 79.0388 | 5.26232 | 6.64651 | 3.58313 |
| RB | games_active | hist_gradient_boosting | test | 2025 | all | 294 | 0.833333 | 8.30646 | 0.563115 | 1.33561 | 0.793022 |
| RB | games_active | hist_gradient_boosting | test | 2025 | top | 74 | 0.756757 | 10.4904 | 1.37711 | 2.19284 | 0.545955 |
| RB | games_active | hist_gradient_boosting | test | 2025 | middle | 146 | 0.787671 | 8.48705 | 0.4339 | 1.56779 | 1.02999 |
| RB | games_active | hist_gradient_boosting | test | 2025 | lower | 74 | 1 | 5.7662 | 0.00405405 | 0.0203073 | 0.572566 |
| RB | games_active | hist_gradient_boosting | validation | 2020 | all | 301 | 0.797342 | 8.91813 | 0.582983 | 1.45039 | 0.866766 |
| RB | games_active | hist_gradient_boosting | validation | 2020 | top | 76 | 0.736842 | 11.6314 | 1.25745 | 2.17463 | 0.612796 |
| RB | games_active | hist_gradient_boosting | validation | 2020 | middle | 150 | 0.726667 | 9.04372 | 0.530747 | 1.79863 | 1.13495 |
| RB | games_active | hist_gradient_boosting | validation | 2020 | lower | 75 | 1 | 5.91751 | 0.004 | 0.02 | 0.587751 |
| RB | games_active | hist_gradient_boosting | validation | 2021 | all | 301 | 0.817276 | 9.26359 | 0.529953 | 1.48409 | 0.864429 |
| RB | games_active | hist_gradient_boosting | validation | 2021 | top | 76 | 0.736842 | 11.5781 | 1.08718 | 2.21166 | 0.613884 |
| RB | games_active | hist_gradient_boosting | validation | 2021 | middle | 150 | 0.78 | 9.68472 | 0.494603 | 1.76745 | 1.04448 |
| RB | games_active | hist_gradient_boosting | validation | 2021 | lower | 75 | 0.973333 | 6.07593 | 0.036 | 0.180098 | 0.758209 |
| RB | games_active | hist_gradient_boosting | validation | 2022 | all | 296 | 0.790541 | 9.24964 | 0.638613 | 1.58653 | 0.81083 |
| RB | games_active | hist_gradient_boosting | validation | 2022 | top | 74 | 0.72973 | 11.1097 | 1.29183 | 2.30578 | 0.537571 |
| RB | games_active | hist_gradient_boosting | validation | 2022 | middle | 148 | 0.716216 | 9.81546 | 0.631312 | 2.01307 | 1.03998 |
| RB | games_active | hist_gradient_boosting | validation | 2022 | lower | 74 | 1 | 6.25796 | 0 | 0.0141984 | 0.625796 |
| RB | games_active | hist_gradient_boosting | validation | 2023 | all | 291 | 0.797251 | 9.01316 | 0.655482 | 1.55569 | 0.83506 |
| RB | games_active | hist_gradient_boosting | validation | 2023 | top | 73 | 0.767123 | 10.9599 | 1.44272 | 2.34063 | 0.530832 |
| RB | games_active | hist_gradient_boosting | validation | 2023 | middle | 145 | 0.717241 | 9.46797 | 0.573981 | 1.86135 | 1.04699 |
| RB | games_active | hist_gradient_boosting | validation | 2023 | lower | 73 | 0.986301 | 6.16307 | 0.030137 | 0.163633 | 0.718324 |
| RB | games_active | hist_gradient_boosting | validation | 2024 | all | 294 | 0.833333 | 8.73892 | 0.552081 | 1.43807 | 0.900013 |
| RB | games_active | hist_gradient_boosting | validation | 2024 | top | 74 | 0.851351 | 11.0445 | 1.1638 | 1.95334 | 0.45229 |
| RB | games_active | hist_gradient_boosting | validation | 2024 | middle | 147 | 0.741497 | 8.93744 | 0.511499 | 1.85593 | 1.28109 |
| RB | games_active | hist_gradient_boosting | validation | 2024 | lower | 73 | 1 | 6.00195 | 0.0136986 | 0.0742861 | 0.586496 |
| RB | games_active | ridge | test | 2025 | all | 294 | 0.778912 | 8.50782 | 0.604759 | 1.51181 | 0.806236 |
| RB | games_active | ridge | test | 2025 | top | 74 | 0.689189 | 11.1098 | 1.37858 | 2.44292 | 0.558045 |
| RB | games_active | ridge | test | 2025 | middle | 146 | 0.726027 | 8.75201 | 0.502631 | 1.71468 | 1.03901 |
| RB | games_active | ridge | test | 2025 | lower | 74 | 0.972973 | 5.42401 | 0.0324324 | 0.180463 | 0.595179 |
| RB | games_active | ridge | validation | 2020 | all | 301 | 0.803987 | 8.72836 | 0.522698 | 1.42519 | 0.800218 |
| RB | games_active | ridge | validation | 2020 | top | 76 | 0.763158 | 12.1668 | 1.12672 | 2.23607 | 0.532012 |
| RB | games_active | ridge | validation | 2020 | middle | 150 | 0.733333 | 8.54534 | 0.464679 | 1.66027 | 1.00498 |
| RB | games_active | ridge | validation | 2020 | lower | 75 | 0.986667 | 5.61009 | 0.0266667 | 0.133333 | 0.662466 |
| RB | games_active | ridge | validation | 2021 | all | 301 | 0.82392 | 9.6273 | 0.606236 | 1.61697 | 0.821177 |
| RB | games_active | ridge | validation | 2021 | top | 76 | 0.828947 | 11.5893 | 1.25988 | 2.17851 | 0.58166 |
| RB | games_active | ridge | validation | 2021 | middle | 149 | 0.744966 | 10.4334 | 0.559237 | 1.97161 | 0.938136 |
| RB | games_active | ridge | validation | 2021 | lower | 76 | 0.973684 | 6.08495 | 0.0447368 | 0.360169 | 0.831393 |
| RB | games_active | ridge | validation | 2022 | all | 296 | 0.793919 | 9.60217 | 0.58185 | 1.68338 | 0.804616 |
| RB | games_active | ridge | validation | 2022 | top | 74 | 0.824324 | 11.3343 | 0.993724 | 1.93471 | 0.452643 |
| RB | games_active | ridge | validation | 2022 | middle | 148 | 0.675676 | 10.4949 | 0.665487 | 2.29775 | 1.08004 |
| RB | games_active | ridge | validation | 2022 | lower | 74 | 1 | 6.08444 | 0.0027027 | 0.203307 | 0.605742 |
| RB | games_active | ridge | validation | 2023 | all | 291 | 0.800687 | 9.16786 | 0.615473 | 1.62225 | 0.818183 |
| RB | games_active | ridge | validation | 2023 | top | 73 | 0.739726 | 11.4666 | 1.37263 | 2.38687 | 0.541233 |
| RB | games_active | ridge | validation | 2023 | middle | 145 | 0.731034 | 9.81975 | 0.542071 | 2.01737 | 1.09096 |
| RB | games_active | ridge | validation | 2023 | lower | 73 | 1 | 5.57425 | 0.00410959 | 0.0727793 | 0.553316 |
| RB | games_active | ridge | validation | 2024 | all | 294 | 0.809524 | 8.53722 | 0.534868 | 1.46504 | 0.878554 |
| RB | games_active | ridge | validation | 2024 | top | 74 | 0.810811 | 11.2651 | 1.12394 | 2.10713 | 0.406057 |
| RB | games_active | ridge | validation | 2024 | middle | 146 | 0.719178 | 8.8821 | 0.500545 | 1.8479 | 1.30313 |
| RB | games_active | ridge | validation | 2024 | lower | 74 | 0.986486 | 5.12895 | 0.0135135 | 0.0675676 | 0.513366 |
| TE | fantasy_points_per_game | hist_gradient_boosting | test | 2025 | all | 122 | 0.762295 | 5.06232 | 0.388803 | 0.7974 | 0.484414 |
| TE | fantasy_points_per_game | hist_gradient_boosting | test | 2025 | top | 56 | 0.553571 | 5.06232 | 0.514553 | 1.19108 | 0.590951 |
| TE | fantasy_points_per_game | hist_gradient_boosting | test | 2025 | middle | 55 | 0.945455 | 5.06232 | 0.272857 | 0.43843 | 0.331609 |
| TE | fantasy_points_per_game | hist_gradient_boosting | test | 2025 | lower | 11 | 0.909091 | 5.06232 | 0.32835 | 0.588074 | 0.706074 |
| TE | fantasy_points_per_game | hist_gradient_boosting | validation | 2020 | all | 111 | 0.72973 | 6.32692 | 0.49691 | 1.06627 | 0.582311 |
| TE | fantasy_points_per_game | hist_gradient_boosting | validation | 2020 | top | 44 | 0.545455 | 6.32692 | 0.730953 | 1.39326 | 0.652409 |
| TE | fantasy_points_per_game | hist_gradient_boosting | validation | 2020 | middle | 55 | 0.836364 | 6.32692 | 0.35436 | 0.943656 | 0.5704 |
| TE | fantasy_points_per_game | hist_gradient_boosting | validation | 2020 | lower | 12 | 0.916667 | 6.32692 | 0.292108 | 0.429312 | 0.379874 |
| TE | fantasy_points_per_game | hist_gradient_boosting | validation | 2021 | all | 118 | 0.830508 | 6.74921 | 0.367365 | 0.883345 | 0.509101 |
| TE | fantasy_points_per_game | hist_gradient_boosting | validation | 2021 | top | 47 | 0.638298 | 6.74921 | 0.515669 | 1.22699 | 0.634554 |
| TE | fantasy_points_per_game | hist_gradient_boosting | validation | 2021 | middle | 51 | 0.941176 | 6.74921 | 0.265679 | 0.789875 | 0.437538 |
| TE | fantasy_points_per_game | hist_gradient_boosting | validation | 2021 | lower | 20 | 1 | 6.74921 | 0.27815 | 0.314115 | 0.396771 |
| TE | fantasy_points_per_game | hist_gradient_boosting | validation | 2022 | all | 110 | 0.890909 | 6.60973 | 0.376883 | 0.831574 | 0.439351 |
| TE | fantasy_points_per_game | hist_gradient_boosting | validation | 2022 | top | 47 | 0.765957 | 6.60973 | 0.49778 | 1.12786 | 0.483635 |
| TE | fantasy_points_per_game | hist_gradient_boosting | validation | 2022 | middle | 50 | 0.98 | 6.60973 | 0.274479 | 0.651752 | 0.426853 |
| TE | fantasy_points_per_game | hist_gradient_boosting | validation | 2022 | lower | 13 | 1 | 6.60973 | 0.333656 | 0.451988 | 0.327317 |
| TE | fantasy_points_per_game | hist_gradient_boosting | validation | 2023 | all | 112 | 0.839286 | 5.82504 | 0.353522 | 0.793345 | 0.485205 |
| TE | fantasy_points_per_game | hist_gradient_boosting | validation | 2023 | top | 51 | 0.72549 | 5.82504 | 0.467679 | 1.03658 | 0.535045 |
| TE | fantasy_points_per_game | hist_gradient_boosting | validation | 2023 | middle | 49 | 0.918367 | 5.82504 | 0.251876 | 0.675979 | 0.478909 |
| TE | fantasy_points_per_game | hist_gradient_boosting | validation | 2023 | lower | 12 | 1 | 5.82504 | 0.283407 | 0.238847 | 0.299097 |
| TE | fantasy_points_per_game | hist_gradient_boosting | validation | 2024 | all | 114 | 0.763158 | 5.09649 | 0.382152 | 0.84899 | 0.472038 |
| TE | fantasy_points_per_game | hist_gradient_boosting | validation | 2024 | top | 50 | 0.56 | 5.09649 | 0.504857 | 1.25783 | 0.655186 |
| TE | fantasy_points_per_game | hist_gradient_boosting | validation | 2024 | middle | 52 | 0.903846 | 5.09649 | 0.293427 | 0.603979 | 0.346183 |
| TE | fantasy_points_per_game | hist_gradient_boosting | validation | 2024 | lower | 12 | 1 | 5.09649 | 0.255356 | 0.207197 | 0.254293 |
| TE | fantasy_points_per_game | ridge | test | 2025 | all | 122 | 0.754098 | 4.91029 | 0.414355 | 0.881017 | 0.552108 |
| TE | fantasy_points_per_game | ridge | test | 2025 | top | 55 | 0.545455 | 4.91029 | 0.548886 | 1.25348 | 0.765582 |
| TE | fantasy_points_per_game | ridge | test | 2025 | middle | 53 | 0.924528 | 4.91029 | 0.28877 | 0.542709 | 0.437148 |
| TE | fantasy_points_per_game | ridge | test | 2025 | lower | 14 | 0.928571 | 4.91029 | 0.361271 | 0.698487 | 0.148659 |
| TE | fantasy_points_per_game | ridge | validation | 2020 | all | 111 | 0.72973 | 6.08693 | 0.524724 | 1.30047 | 0.665311 |
| TE | fantasy_points_per_game | ridge | validation | 2020 | top | 46 | 0.630435 | 6.08693 | 0.611487 | 1.4587 | 0.748624 |
| TE | fantasy_points_per_game | ridge | validation | 2020 | middle | 50 | 0.76 | 6.08693 | 0.463189 | 1.22905 | 0.737134 |
| TE | fantasy_points_per_game | ridge | validation | 2020 | lower | 15 | 0.933333 | 6.08693 | 0.463765 | 1.05326 | 0.170411 |
| TE | fantasy_points_per_game | ridge | validation | 2021 | all | 118 | 0.830508 | 6.82289 | 0.40321 | 0.899719 | 0.526052 |
| TE | fantasy_points_per_game | ridge | validation | 2021 | top | 52 | 0.711538 | 6.82289 | 0.571857 | 1.18166 | 0.598425 |
| TE | fantasy_points_per_game | ridge | validation | 2021 | middle | 47 | 0.893617 | 6.82289 | 0.271186 | 0.84384 | 0.491255 |
| TE | fantasy_points_per_game | ridge | validation | 2021 | lower | 19 | 1 | 6.82289 | 0.268235 | 0.266305 | 0.414054 |
| TE | fantasy_points_per_game | ridge | validation | 2022 | all | 110 | 0.854545 | 6.44684 | 0.48299 | 0.939063 | 0.468841 |
| TE | fantasy_points_per_game | ridge | validation | 2022 | top | 51 | 0.705882 | 6.44684 | 0.776444 | 1.23498 | 0.497241 |
| TE | fantasy_points_per_game | ridge | validation | 2022 | middle | 45 | 0.977778 | 6.44684 | 0.199892 | 0.746249 | 0.48273 |
| TE | fantasy_points_per_game | ridge | validation | 2022 | lower | 14 | 1 | 6.44684 | 0.323939 | 0.480844 | 0.320745 |
| TE | fantasy_points_per_game | ridge | validation | 2023 | all | 112 | 0.830357 | 6.00649 | 0.362934 | 0.847623 | 0.484916 |
| TE | fantasy_points_per_game | ridge | validation | 2023 | top | 52 | 0.692308 | 6.00649 | 0.509902 | 1.16124 | 0.546483 |
| TE | fantasy_points_per_game | ridge | validation | 2023 | middle | 48 | 0.958333 | 6.00649 | 0.201743 | 0.58109 | 0.414227 |
| TE | fantasy_points_per_game | ridge | validation | 2023 | lower | 12 | 0.916667 | 6.00649 | 0.370836 | 0.554747 | 0.500878 |
| TE | fantasy_points_per_game | ridge | validation | 2024 | all | 114 | 0.789474 | 5.10803 | 0.374139 | 0.809886 | 0.46501 |
| TE | fantasy_points_per_game | ridge | validation | 2024 | top | 52 | 0.615385 | 5.10803 | 0.47978 | 1.2122 | 0.711892 |
| TE | fantasy_points_per_game | ridge | validation | 2024 | middle | 55 | 0.927273 | 5.10803 | 0.277868 | 0.462215 | 0.269777 |
| TE | fantasy_points_per_game | ridge | validation | 2024 | lower | 7 | 1 | 5.10803 | 0.345794 | 0.552937 | 0.165009 |
| TE | fantasy_points_total | hist_gradient_boosting | test | 2025 | all | 237 | 0.843882 | 54.2997 | 4.23519 | 6.66273 | 5.99281 |
| TE | fantasy_points_total | hist_gradient_boosting | test | 2025 | top | 59 | 0.474576 | 54.2997 | 8.83532 | 18.2714 | 12.957 |
| TE | fantasy_points_total | hist_gradient_boosting | test | 2025 | middle | 119 | 0.94958 | 54.2997 | 2.74258 | 3.98176 | 4.13072 |
| TE | fantasy_points_total | hist_gradient_boosting | test | 2025 | lower | 59 | 1 | 54.2997 | 2.64559 | 0.46143 | 2.78438 |
| TE | fantasy_points_total | hist_gradient_boosting | validation | 2020 | all | 225 | 0.831111 | 62.6153 | 4.79914 | 8.94803 | 7.73301 |
| TE | fantasy_points_total | hist_gradient_boosting | validation | 2020 | top | 56 | 0.517857 | 62.6153 | 9.85518 | 20.2674 | 14.1507 |
| TE | fantasy_points_total | hist_gradient_boosting | validation | 2020 | middle | 113 | 0.902655 | 62.6153 | 3.17458 | 6.95924 | 6.77906 |
| TE | fantasy_points_total | hist_gradient_boosting | validation | 2020 | lower | 56 | 1 | 62.6153 | 3.02125 | 1.64176 | 3.24028 |
| TE | fantasy_points_total | hist_gradient_boosting | validation | 2021 | all | 229 | 0.799127 | 59.6078 | 4.69171 | 9.11529 | 7.374 |
| TE | fantasy_points_total | hist_gradient_boosting | validation | 2021 | top | 57 | 0.421053 | 59.6078 | 10.8476 | 21.6969 | 14.9019 |
| TE | fantasy_points_total | hist_gradient_boosting | validation | 2021 | middle | 115 | 0.886957 | 59.6078 | 2.66621 | 6.80116 | 5.64304 |
| TE | fantasy_points_total | hist_gradient_boosting | validation | 2021 | lower | 57 | 1 | 59.6078 | 2.62239 | 1.20252 | 3.33839 |
| TE | fantasy_points_total | hist_gradient_boosting | validation | 2022 | all | 234 | 0.794872 | 63.6313 | 4.80258 | 7.78946 | 5.67804 |
| TE | fantasy_points_total | hist_gradient_boosting | validation | 2022 | top | 59 | 0.305085 | 63.6313 | 11.9658 | 19.931 | 9.89232 |
| TE | fantasy_points_total | hist_gradient_boosting | validation | 2022 | middle | 116 | 0.939655 | 63.6313 | 2.36553 | 4.91541 | 4.42251 |
| TE | fantasy_points_total | hist_gradient_boosting | validation | 2022 | lower | 59 | 1 | 63.6313 | 2.43087 | 1.29861 | 3.93225 |
| TE | fantasy_points_total | hist_gradient_boosting | validation | 2023 | all | 235 | 0.808511 | 58.4115 | 4.82399 | 7.66239 | 6.27628 |
| TE | fantasy_points_total | hist_gradient_boosting | validation | 2023 | top | 59 | 0.40678 | 58.4115 | 11.774 | 20.317 | 12.3081 |
| TE | fantasy_points_total | hist_gradient_boosting | validation | 2023 | middle | 117 | 0.923077 | 58.4115 | 2.42104 | 4.42496 | 4.7552 |
| TE | fantasy_points_total | hist_gradient_boosting | validation | 2023 | lower | 59 | 0.983051 | 58.4115 | 2.63917 | 1.42772 | 3.26087 |
| TE | fantasy_points_total | hist_gradient_boosting | validation | 2024 | all | 237 | 0.827004 | 58.3734 | 4.47675 | 7.4967 | 6.61715 |
| TE | fantasy_points_total | hist_gradient_boosting | validation | 2024 | top | 59 | 0.440678 | 58.3734 | 9.77825 | 20.4729 | 14.2574 |
| TE | fantasy_points_total | hist_gradient_boosting | validation | 2024 | middle | 119 | 0.932773 | 58.3734 | 2.75218 | 4.51219 | 4.53137 |
| TE | fantasy_points_total | hist_gradient_boosting | validation | 2024 | lower | 59 | 1 | 58.3734 | 2.65359 | 0.540075 | 3.18375 |
| TE | fantasy_points_total | ridge | test | 2025 | all | 237 | 0.810127 | 52.1957 | 4.6388 | 8.38738 | 6.01379 |
| TE | fantasy_points_total | ridge | test | 2025 | top | 59 | 0.423729 | 52.1957 | 10.4658 | 20.13 | 14.0199 |
| TE | fantasy_points_total | ridge | test | 2025 | middle | 119 | 0.907563 | 52.1957 | 2.42184 | 4.98056 | 4.06599 |
| TE | fantasy_points_total | ridge | test | 2025 | lower | 59 | 1 | 52.1957 | 3.28329 | 3.51618 | 1.93627 |
| TE | fantasy_points_total | ridge | validation | 2020 | all | 225 | 0.817778 | 68.8353 | 5.62509 | 11.4834 | 8.23762 |
| TE | fantasy_points_total | ridge | validation | 2020 | top | 56 | 0.607143 | 68.8353 | 7.16317 | 18.9017 | 14.8782 |
| TE | fantasy_points_total | ridge | validation | 2020 | middle | 113 | 0.858407 | 68.8353 | 4.97929 | 9.15798 | 8.18446 |
| TE | fantasy_points_total | ridge | validation | 2020 | lower | 56 | 0.946429 | 68.8353 | 5.39017 | 8.75731 | 1.70434 |
| TE | fantasy_points_total | ridge | validation | 2021 | all | 229 | 0.829694 | 69.9082 | 4.81151 | 9.57098 | 6.77615 |
| TE | fantasy_points_total | ridge | validation | 2021 | top | 57 | 0.45614 | 69.9082 | 7.44363 | 21.4184 | 14.5685 |
| TE | fantasy_points_total | ridge | validation | 2021 | middle | 115 | 0.930435 | 69.9082 | 3.6687 | 5.83114 | 5.03046 |
| TE | fantasy_points_total | ridge | validation | 2021 | lower | 57 | 1 | 69.9082 | 4.48505 | 5.26881 | 2.50578 |
| TE | fantasy_points_total | ridge | validation | 2022 | all | 234 | 0.846154 | 65.3924 | 6.04591 | 9.1768 | 5.77395 |
| TE | fantasy_points_total | ridge | validation | 2022 | top | 59 | 0.525424 | 65.3924 | 16.1296 | 21.5282 | 9.88922 |
| TE | fantasy_points_total | ridge | validation | 2022 | middle | 116 | 0.931034 | 65.3924 | 2.31949 | 6.15444 | 4.96431 |
| TE | fantasy_points_total | ridge | validation | 2022 | lower | 59 | 1 | 65.3924 | 3.28872 | 2.76768 | 3.25052 |
| TE | fantasy_points_total | ridge | validation | 2023 | all | 235 | 0.808511 | 57.1614 | 4.38663 | 8.74341 | 5.97752 |
| TE | fantasy_points_total | ridge | validation | 2023 | top | 59 | 0.389831 | 57.1614 | 8.98413 | 19.3248 | 13.509 |
| TE | fantasy_points_total | ridge | validation | 2023 | middle | 117 | 0.923077 | 57.1614 | 2.52237 | 5.42968 | 4.0693 |
| TE | fantasy_points_total | ridge | validation | 2023 | lower | 59 | 1 | 57.1614 | 3.48603 | 4.73328 | 2.23011 |
| TE | fantasy_points_total | ridge | validation | 2024 | all | 237 | 0.805907 | 54.2287 | 5.02988 | 9.04666 | 6.63778 |
| TE | fantasy_points_total | ridge | validation | 2024 | top | 59 | 0.423729 | 54.2287 | 11.8835 | 22.0166 | 16.3492 |
| TE | fantasy_points_total | ridge | validation | 2024 | middle | 119 | 0.907563 | 54.2287 | 2.41126 | 5.07075 | 3.95153 |
| TE | fantasy_points_total | ridge | validation | 2024 | lower | 59 | 0.983051 | 54.2287 | 3.45781 | 4.09592 | 2.34439 |
| TE | games_active | hist_gradient_boosting | test | 2025 | all | 235 | 0.842553 | 8.36145 | 0.519439 | 1.28505 | 0.733278 |
| TE | games_active | hist_gradient_boosting | test | 2025 | top | 59 | 0.898305 | 9.30894 | 0.858553 | 1.45967 | 0.397193 |
| TE | games_active | hist_gradient_boosting | test | 2025 | middle | 117 | 0.735043 | 9.19961 | 0.606099 | 1.82036 | 0.986754 |
| TE | games_active | hist_gradient_boosting | test | 2025 | lower | 59 | 1 | 5.75183 | 0.00847458 | 0.0488811 | 0.566709 |
| TE | games_active | hist_gradient_boosting | validation | 2020 | all | 224 | 0.852679 | 10.9527 | 0.634235 | 1.73987 | 0.856142 |
| TE | games_active | hist_gradient_boosting | validation | 2020 | top | 56 | 0.839286 | 12.9692 | 1.32989 | 2.2118 | 0.605808 |
| TE | games_active | hist_gradient_boosting | validation | 2020 | middle | 112 | 0.803571 | 11.6989 | 0.579418 | 2.23318 | 1.03823 |
| TE | games_active | hist_gradient_boosting | validation | 2020 | lower | 56 | 0.964286 | 7.4438 | 0.0482143 | 0.281323 | 0.74231 |
| TE | games_active | hist_gradient_boosting | validation | 2021 | all | 229 | 0.816594 | 10.3916 | 0.650496 | 1.72558 | 0.949662 |
| TE | games_active | hist_gradient_boosting | validation | 2021 | top | 57 | 0.929825 | 11.8025 | 1.11964 | 1.90121 | 0.501754 |
| TE | games_active | hist_gradient_boosting | validation | 2021 | middle | 115 | 0.669565 | 11.2991 | 0.737776 | 2.47517 | 1.29061 |
| TE | games_active | hist_gradient_boosting | validation | 2021 | lower | 57 | 1 | 7.14963 | 0.00526316 | 0.0376081 | 0.7097 |
| TE | games_active | hist_gradient_boosting | validation | 2022 | all | 234 | 0.803419 | 10.0126 | 0.685377 | 1.67135 | 0.804152 |
| TE | games_active | hist_gradient_boosting | validation | 2022 | top | 59 | 0.881356 | 11.005 | 1.21501 | 1.97353 | 0.469247 |
| TE | games_active | hist_gradient_boosting | validation | 2022 | middle | 116 | 0.663793 | 11.1226 | 0.762007 | 2.35246 | 1.03829 |
| TE | games_active | hist_gradient_boosting | validation | 2022 | lower | 59 | 1 | 6.8381 | 0.00508475 | 0.0300348 | 0.678725 |
| TE | games_active | hist_gradient_boosting | validation | 2023 | all | 235 | 0.846809 | 9.54379 | 0.550985 | 1.50101 | 0.799778 |
| TE | games_active | hist_gradient_boosting | validation | 2023 | top | 59 | 0.881356 | 10.9433 | 1.11649 | 1.9803 | 0.384382 |
| TE | games_active | hist_gradient_boosting | validation | 2023 | middle | 117 | 0.760684 | 10.3414 | 0.525715 | 1.9258 | 1.03348 |
| TE | games_active | hist_gradient_boosting | validation | 2023 | lower | 59 | 0.983051 | 6.56264 | 0.0355932 | 0.179344 | 0.751727 |
| TE | games_active | hist_gradient_boosting | validation | 2024 | all | 236 | 0.855932 | 8.9368 | 0.564703 | 1.50117 | 0.869749 |
| TE | games_active | hist_gradient_boosting | validation | 2024 | top | 59 | 0.915254 | 10.262 | 1.01578 | 1.86945 | 0.352011 |
| TE | games_active | hist_gradient_boosting | validation | 2024 | middle | 118 | 0.762712 | 9.63497 | 0.611344 | 2.0154 | 1.21583 |
| TE | games_active | hist_gradient_boosting | validation | 2024 | lower | 59 | 0.983051 | 6.21522 | 0.020339 | 0.104433 | 0.695329 |
| TE | games_active | ridge | test | 2025 | all | 235 | 0.86383 | 9.05143 | 0.529333 | 1.4337 | 0.738522 |
| TE | games_active | ridge | test | 2025 | top | 59 | 0.915254 | 10.2453 | 0.893258 | 1.67088 | 0.381373 |
| TE | games_active | ridge | test | 2025 | middle | 117 | 0.769231 | 10.0653 | 0.608471 | 1.97975 | 1.00046 |
| TE | games_active | ridge | test | 2025 | lower | 59 | 1 | 5.84703 | 0.00847458 | 0.113685 | 0.576228 |
| TE | games_active | ridge | validation | 2020 | all | 224 | 0.803571 | 11.9624 | 0.796846 | 2.54685 | 0.977618 |
| TE | games_active | ridge | validation | 2020 | top | 56 | 0.892857 | 8.58207 | 0.941425 | 1.56348 | 0.441071 |
| TE | games_active | ridge | validation | 2020 | middle | 113 | 0.663717 | 13.6635 | 1.10242 | 3.17783 | 1.15032 |
| TE | games_active | ridge | validation | 2020 | lower | 55 | 1 | 11.9092 | 0.0218182 | 2.25171 | 1.1691 |
| TE | games_active | ridge | validation | 2021 | all | 229 | 0.812227 | 10.0211 | 0.598911 | 1.74654 | 0.919001 |
| TE | games_active | ridge | validation | 2021 | top | 57 | 0.877193 | 13.3792 | 1.18417 | 2.32341 | 0.468644 |
| TE | games_active | ridge | validation | 2021 | middle | 115 | 0.695652 | 10.4123 | 0.595241 | 2.27413 | 1.21268 |
| TE | games_active | ridge | validation | 2021 | lower | 57 | 0.982456 | 5.87365 | 0.0210526 | 0.105263 | 0.776838 |
| TE | games_active | ridge | validation | 2022 | all | 234 | 0.799145 | 9.93778 | 0.579214 | 1.68376 | 0.802771 |
| TE | games_active | ridge | validation | 2022 | top | 59 | 0.881356 | 12.6861 | 1.12814 | 2.12658 | 0.415191 |
| TE | games_active | ridge | validation | 2022 | middle | 116 | 0.655172 | 10.8701 | 0.594618 | 2.3149 | 1.13577 |
| TE | games_active | ridge | validation | 2022 | lower | 59 | 1 | 5.35639 | 0 | 4.13346e-05 | 0.535639 |
| TE | games_active | ridge | validation | 2023 | all | 235 | 0.825532 | 9.32488 | 0.567463 | 1.51485 | 0.754029 |
| TE | games_active | ridge | validation | 2023 | top | 59 | 0.813559 | 12.4577 | 1.2282 | 2.22369 | 0.421914 |
| TE | games_active | ridge | validation | 2023 | middle | 117 | 0.74359 | 9.67022 | 0.509318 | 1.86574 | 1.03514 |
| TE | games_active | ridge | validation | 2023 | lower | 59 | 1 | 5.50725 | 0.0220339 | 0.110169 | 0.528691 |
| TE | games_active | ridge | validation | 2024 | all | 236 | 0.805085 | 9.00396 | 0.66524 | 1.66993 | 0.833468 |
| TE | games_active | ridge | validation | 2024 | top | 59 | 0.864407 | 10.0604 | 1.17429 | 2.01312 | 0.397275 |
| TE | games_active | ridge | validation | 2024 | middle | 118 | 0.686441 | 9.90966 | 0.735708 | 2.23384 | 1.16867 |
| TE | games_active | ridge | validation | 2024 | lower | 59 | 0.983051 | 6.13618 | 0.0152542 | 0.19891 | 0.599261 |
| WR | fantasy_points_per_game | hist_gradient_boosting | test | 2025 | all | 198 | 0.838384 | 7.76528 | 0.488168 | 1.06005 | 0.510608 |
| WR | fantasy_points_per_game | hist_gradient_boosting | test | 2025 | top | 91 | 0.681319 | 7.76528 | 0.586474 | 1.44215 | 0.662599 |
| WR | fantasy_points_per_game | hist_gradient_boosting | test | 2025 | middle | 70 | 0.957143 | 7.76528 | 0.39193 | 0.805386 | 0.398934 |
| WR | fantasy_points_per_game | hist_gradient_boosting | test | 2025 | lower | 37 | 1 | 7.76528 | 0.428463 | 0.602084 | 0.348065 |
| WR | fantasy_points_per_game | hist_gradient_boosting | validation | 2020 | all | 192 | 0.838542 | 8.98188 | 0.529513 | 1.23104 | 0.616468 |
| WR | fantasy_points_per_game | hist_gradient_boosting | validation | 2020 | top | 93 | 0.763441 | 8.98188 | 0.645786 | 1.47445 | 0.647624 |
| WR | fantasy_points_per_game | hist_gradient_boosting | validation | 2020 | middle | 68 | 0.882353 | 8.98188 | 0.407227 | 1.10297 | 0.617201 |
| WR | fantasy_points_per_game | hist_gradient_boosting | validation | 2020 | lower | 31 | 0.967742 | 8.98188 | 0.448934 | 0.781725 | 0.521391 |
| WR | fantasy_points_per_game | hist_gradient_boosting | validation | 2021 | all | 212 | 0.839623 | 8.50819 | 0.561622 | 1.19581 | 0.659979 |
| WR | fantasy_points_per_game | hist_gradient_boosting | validation | 2021 | top | 89 | 0.775281 | 8.50819 | 0.779652 | 1.43464 | 0.739151 |
| WR | fantasy_points_per_game | hist_gradient_boosting | validation | 2021 | middle | 92 | 0.880435 | 8.50819 | 0.38018 | 1.05809 | 0.617162 |
| WR | fantasy_points_per_game | hist_gradient_boosting | validation | 2021 | lower | 31 | 0.903226 | 8.50819 | 0.474144 | 0.918888 | 0.559753 |
| WR | fantasy_points_per_game | hist_gradient_boosting | validation | 2022 | all | 200 | 0.81 | 8.27374 | 0.511506 | 1.18938 | 0.587457 |
| WR | fantasy_points_per_game | hist_gradient_boosting | validation | 2022 | top | 95 | 0.736842 | 8.27374 | 0.60624 | 1.42535 | 0.579879 |
| WR | fantasy_points_per_game | hist_gradient_boosting | validation | 2022 | middle | 79 | 0.860759 | 8.27374 | 0.420134 | 1.08533 | 0.599939 |
| WR | fantasy_points_per_game | hist_gradient_boosting | validation | 2022 | lower | 26 | 0.923077 | 8.27374 | 0.44299 | 0.643329 | 0.577222 |
| WR | fantasy_points_per_game | hist_gradient_boosting | validation | 2023 | all | 191 | 0.842932 | 8.07872 | 0.460413 | 1.0625 | 0.610572 |
| WR | fantasy_points_per_game | hist_gradient_boosting | validation | 2023 | top | 97 | 0.742268 | 8.07872 | 0.590645 | 1.38274 | 0.667926 |
| WR | fantasy_points_per_game | hist_gradient_boosting | validation | 2023 | middle | 70 | 0.942857 | 8.07872 | 0.317061 | 0.814782 | 0.571666 |
| WR | fantasy_points_per_game | hist_gradient_boosting | validation | 2023 | lower | 24 | 0.958333 | 8.07872 | 0.35217 | 0.490766 | 0.492242 |
| WR | fantasy_points_per_game | hist_gradient_boosting | validation | 2024 | all | 194 | 0.752577 | 7.49237 | 0.501774 | 1.23699 | 0.673478 |
| WR | fantasy_points_per_game | hist_gradient_boosting | validation | 2024 | top | 95 | 0.642105 | 7.49237 | 0.556825 | 1.51761 | 0.726086 |
| WR | fantasy_points_per_game | hist_gradient_boosting | validation | 2024 | middle | 76 | 0.828947 | 7.49237 | 0.445796 | 1.02523 | 0.625542 |
| WR | fantasy_points_per_game | hist_gradient_boosting | validation | 2024 | lower | 23 | 0.956522 | 7.49237 | 0.459359 | 0.777687 | 0.614578 |
| WR | fantasy_points_per_game | ridge | test | 2025 | all | 198 | 0.893939 | 7.79508 | 0.450554 | 1.06345 | 0.507775 |
| WR | fantasy_points_per_game | ridge | test | 2025 | top | 98 | 0.836735 | 7.79508 | 0.448508 | 1.27758 | 0.64786 |
| WR | fantasy_points_per_game | ridge | test | 2025 | middle | 79 | 0.936709 | 7.79508 | 0.431785 | 0.822245 | 0.40284 |
| WR | fantasy_points_per_game | ridge | test | 2025 | lower | 21 | 1 | 7.79508 | 0.530709 | 0.971624 | 0.2488 |
| WR | fantasy_points_per_game | ridge | validation | 2020 | all | 192 | 0.901042 | 11.1903 | 0.530099 | 1.36421 | 0.729748 |
| WR | fantasy_points_per_game | ridge | validation | 2020 | top | 88 | 0.863636 | 11.1903 | 0.674622 | 1.50167 | 0.706352 |
| WR | fantasy_points_per_game | ridge | validation | 2020 | middle | 73 | 0.90411 | 11.1903 | 0.382408 | 1.49334 | 0.791223 |
| WR | fantasy_points_per_game | ridge | validation | 2020 | lower | 31 | 1 | 11.1903 | 0.46763 | 0.669903 | 0.651401 |
| WR | fantasy_points_per_game | ridge | validation | 2021 | all | 212 | 0.839623 | 10.2983 | 0.605354 | 1.45529 | 0.895348 |
| WR | fantasy_points_per_game | ridge | validation | 2021 | top | 99 | 0.757576 | 10.2983 | 0.802615 | 1.60828 | 0.878405 |
| WR | fantasy_points_per_game | ridge | validation | 2021 | middle | 92 | 0.902174 | 10.2983 | 0.388628 | 1.27499 | 0.716454 |
| WR | fantasy_points_per_game | ridge | validation | 2021 | lower | 21 | 0.952381 | 10.2983 | 0.62487 | 1.52396 | 1.75895 |
| WR | fantasy_points_per_game | ridge | validation | 2022 | all | 200 | 0.815 | 8.31257 | 0.502637 | 1.20055 | 0.578963 |
| WR | fantasy_points_per_game | ridge | validation | 2022 | top | 100 | 0.75 | 8.31257 | 0.604863 | 1.36984 | 0.569244 |
| WR | fantasy_points_per_game | ridge | validation | 2022 | middle | 78 | 0.871795 | 8.31257 | 0.373376 | 1.08904 | 0.581922 |
| WR | fantasy_points_per_game | ridge | validation | 2022 | lower | 22 | 0.909091 | 8.31257 | 0.496265 | 0.826373 | 0.612646 |
| WR | fantasy_points_per_game | ridge | validation | 2023 | all | 191 | 0.837696 | 8.03378 | 0.465055 | 1.06909 | 0.583657 |
| WR | fantasy_points_per_game | ridge | validation | 2023 | top | 98 | 0.714286 | 8.03378 | 0.549869 | 1.36907 | 0.674038 |
| WR | fantasy_points_per_game | ridge | validation | 2023 | middle | 73 | 0.972603 | 8.03378 | 0.344428 | 0.759513 | 0.506335 |
| WR | fantasy_points_per_game | ridge | validation | 2023 | lower | 20 | 0.95 | 8.03378 | 0.489749 | 0.729093 | 0.423008 |
| WR | fantasy_points_per_game | ridge | validation | 2024 | all | 194 | 0.768041 | 7.54628 | 0.537811 | 1.33955 | 0.682646 |
| WR | fantasy_points_per_game | ridge | validation | 2024 | top | 92 | 0.684783 | 7.54628 | 0.55339 | 1.58544 | 0.798145 |
| WR | fantasy_points_per_game | ridge | validation | 2024 | middle | 86 | 0.825581 | 7.54628 | 0.515403 | 1.11432 | 0.641311 |
| WR | fantasy_points_per_game | ridge | validation | 2024 | lower | 16 | 0.9375 | 7.54628 | 0.568679 | 1.13627 | 0.240703 |
| WR | fantasy_points_total | hist_gradient_boosting | test | 2025 | all | 434 | 0.85023 | 75.9013 | 7.58472 | 9.51552 | 7.0216 |
| WR | fantasy_points_total | hist_gradient_boosting | test | 2025 | top | 109 | 0.477064 | 75.9013 | 19.2137 | 27.4262 | 14.9137 |
| WR | fantasy_points_total | hist_gradient_boosting | test | 2025 | middle | 216 | 0.967593 | 75.9013 | 3.61759 | 4.67725 | 4.63044 |
| WR | fantasy_points_total | hist_gradient_boosting | test | 2025 | lower | 109 | 0.990826 | 75.9013 | 3.81717 | 1.19255 | 3.86793 |
| WR | fantasy_points_total | hist_gradient_boosting | validation | 2020 | all | 414 | 0.806763 | 82.5783 | 7.55813 | 11.3663 | 8.4021 |
| WR | fantasy_points_total | hist_gradient_boosting | validation | 2020 | top | 104 | 0.403846 | 82.5783 | 18.7555 | 29.6745 | 15.3756 |
| WR | fantasy_points_total | hist_gradient_boosting | validation | 2020 | middle | 206 | 0.912621 | 82.5783 | 3.87435 | 6.87567 | 6.80082 |
| WR | fantasy_points_total | hist_gradient_boosting | validation | 2020 | lower | 104 | 1 | 82.5783 | 3.65744 | 1.95302 | 4.6004 |
| WR | fantasy_points_total | hist_gradient_boosting | validation | 2021 | all | 419 | 0.785203 | 81.3112 | 8.26885 | 12.1057 | 9.07151 |
| WR | fantasy_points_total | hist_gradient_boosting | validation | 2021 | top | 105 | 0.4 | 81.3112 | 20.7078 | 30.4081 | 16.3708 |
| WR | fantasy_points_total | hist_gradient_boosting | validation | 2021 | middle | 209 | 0.885167 | 81.3112 | 4.27017 | 7.99947 | 7.61763 |
| WR | fantasy_points_total | hist_gradient_boosting | validation | 2021 | lower | 105 | 0.971429 | 81.3112 | 3.78914 | 1.97654 | 4.66611 |
| WR | fantasy_points_total | hist_gradient_boosting | validation | 2022 | all | 432 | 0.810185 | 83.0972 | 6.94146 | 10.7411 | 8.01135 |
| WR | fantasy_points_total | hist_gradient_boosting | validation | 2022 | top | 108 | 0.407407 | 83.0972 | 15.4593 | 26.0727 | 12.1465 |
| WR | fantasy_points_total | hist_gradient_boosting | validation | 2022 | middle | 216 | 0.916667 | 83.0972 | 4.14419 | 8.04903 | 7.80364 |
| WR | fantasy_points_total | hist_gradient_boosting | validation | 2022 | lower | 108 | 1 | 83.0972 | 4.01816 | 0.79358 | 4.29157 |
| WR | fantasy_points_total | hist_gradient_boosting | validation | 2023 | all | 419 | 0.821002 | 82.506 | 5.79235 | 9.68275 | 7.60695 |
| WR | fantasy_points_total | hist_gradient_boosting | validation | 2023 | top | 105 | 0.419048 | 82.506 | 11.7919 | 25.0137 | 13.9124 |
| WR | fantasy_points_total | hist_gradient_boosting | validation | 2023 | middle | 209 | 0.933014 | 82.506 | 3.7511 | 6.46296 | 6.05289 |
| WR | fantasy_points_total | hist_gradient_boosting | validation | 2023 | lower | 105 | 1 | 82.506 | 3.85581 | 0.760726 | 4.39479 |
| WR | fantasy_points_total | hist_gradient_boosting | validation | 2024 | all | 425 | 0.823529 | 79.6019 | 6.63044 | 9.93321 | 8.32877 |
| WR | fantasy_points_total | hist_gradient_boosting | validation | 2024 | top | 106 | 0.433962 | 79.6019 | 14.4003 | 25.8767 | 15.4473 |
| WR | fantasy_points_total | hist_gradient_boosting | validation | 2024 | middle | 213 | 0.929577 | 79.6019 | 4.10455 | 6.51437 | 6.92851 |
| WR | fantasy_points_total | hist_gradient_boosting | validation | 2024 | lower | 106 | 1 | 79.6019 | 3.93618 | 0.859629 | 4.02401 |
| WR | fantasy_points_total | ridge | test | 2025 | all | 434 | 0.827189 | 74.8583 | 6.78573 | 11.3826 | 6.81614 |
| WR | fantasy_points_total | ridge | test | 2025 | top | 109 | 0.422018 | 74.8583 | 14.5006 | 26.2755 | 15.8592 |
| WR | fantasy_points_total | ridge | test | 2025 | middle | 216 | 0.958333 | 74.8583 | 3.63029 | 5.60157 | 4.4139 |
| WR | fantasy_points_total | ridge | test | 2025 | lower | 109 | 0.972477 | 74.8583 | 5.32383 | 7.9458 | 2.53344 |
| WR | fantasy_points_total | ridge | validation | 2020 | all | 414 | 0.850242 | 132.098 | 7.32981 | 18.4016 | 10.1037 |
| WR | fantasy_points_total | ridge | validation | 2020 | top | 104 | 0.567308 | 132.098 | 15.9474 | 31.0238 | 12.8658 |
| WR | fantasy_points_total | ridge | validation | 2020 | middle | 206 | 0.917476 | 132.098 | 3.90191 | 18.306 | 9.91884 |
| WR | fantasy_points_total | ridge | validation | 2020 | lower | 104 | 1 | 132.098 | 5.50211 | 5.96892 | 7.7077 |
| WR | fantasy_points_total | ridge | validation | 2021 | all | 419 | 0.847255 | 125.856 | 8.011 | 14.8947 | 11.1306 |
| WR | fantasy_points_total | ridge | validation | 2021 | top | 105 | 0.590476 | 125.856 | 16.6982 | 29.0751 | 13.9912 |
| WR | fantasy_points_total | ridge | validation | 2021 | middle | 209 | 0.909091 | 125.856 | 4.5574 | 11.5997 | 9.37142 |
| WR | fantasy_points_total | ridge | validation | 2021 | lower | 105 | 0.980952 | 125.856 | 6.19808 | 7.27314 | 11.7718 |
| WR | fantasy_points_total | ridge | validation | 2022 | all | 432 | 0.826389 | 91.5888 | 6.7788 | 12.9357 | 8.08556 |
| WR | fantasy_points_total | ridge | validation | 2022 | top | 108 | 0.490741 | 91.5888 | 14.464 | 26.1363 | 12.0997 |
| WR | fantasy_points_total | ridge | validation | 2022 | middle | 216 | 0.907407 | 91.5888 | 3.81678 | 11.0877 | 8.05069 |
| WR | fantasy_points_total | ridge | validation | 2022 | lower | 108 | 1 | 91.5888 | 5.01767 | 3.43113 | 4.14121 |
| WR | fantasy_points_total | ridge | validation | 2023 | all | 419 | 0.835322 | 87.422 | 6.01774 | 11.3885 | 7.52518 |
| WR | fantasy_points_total | ridge | validation | 2023 | top | 105 | 0.457143 | 87.422 | 11.5366 | 25.0123 | 13.8677 |
| WR | fantasy_points_total | ridge | validation | 2023 | middle | 209 | 0.947368 | 87.422 | 3.61303 | 7.0307 | 6.31233 |
| WR | fantasy_points_total | ridge | validation | 2023 | lower | 105 | 0.990476 | 87.422 | 5.28542 | 6.43873 | 3.59686 |
| WR | fantasy_points_total | ridge | validation | 2024 | all | 425 | 0.802353 | 81.4425 | 6.6076 | 12.1915 | 8.09892 |
| WR | fantasy_points_total | ridge | validation | 2024 | top | 106 | 0.386792 | 81.4425 | 12.9456 | 26.1694 | 15.7022 |
| WR | fantasy_points_total | ridge | validation | 2024 | middle | 213 | 0.910798 | 81.4425 | 4.09982 | 7.51827 | 6.93452 |
| WR | fantasy_points_total | ridge | validation | 2024 | lower | 106 | 1 | 81.4425 | 5.30881 | 7.60402 | 2.83543 |
| WR | games_active | hist_gradient_boosting | test | 2025 | all | 433 | 0.789838 | 7.89095 | 0.576067 | 1.42106 | 0.866129 |
| WR | games_active | hist_gradient_boosting | test | 2025 | top | 109 | 0.733945 | 9.34544 | 1.16848 | 1.95325 | 0.558659 |
| WR | games_active | hist_gradient_boosting | test | 2025 | middle | 215 | 0.72093 | 8.30574 | 0.552432 | 1.7947 | 1.13646 |
| WR | games_active | hist_gradient_boosting | test | 2025 | lower | 109 | 0.981651 | 5.6183 | 0.0302752 | 0.151865 | 0.640387 |
| WR | games_active | hist_gradient_boosting | validation | 2020 | all | 412 | 0.832524 | 8.69358 | 0.547665 | 1.40007 | 0.898843 |
| WR | games_active | hist_gradient_boosting | validation | 2020 | top | 104 | 0.807692 | 10.7465 | 1.21098 | 1.95712 | 0.579172 |
| WR | games_active | hist_gradient_boosting | validation | 2020 | middle | 205 | 0.765854 | 8.9976 | 0.474129 | 1.75995 | 1.17862 |
| WR | games_active | hist_gradient_boosting | validation | 2020 | lower | 103 | 0.990291 | 6.01565 | 0.0242718 | 0.121359 | 0.664778 |
| WR | games_active | hist_gradient_boosting | validation | 2021 | all | 418 | 0.803828 | 8.54241 | 0.600797 | 1.56342 | 0.964649 |
| WR | games_active | hist_gradient_boosting | validation | 2021 | top | 105 | 0.8 | 10.2598 | 1.21978 | 2.13231 | 0.508384 |
| WR | games_active | hist_gradient_boosting | validation | 2021 | middle | 208 | 0.716346 | 8.98545 | 0.579113 | 2.00286 | 1.34552 |
| WR | games_active | hist_gradient_boosting | validation | 2021 | lower | 105 | 0.980952 | 5.94733 | 0.0247619 | 0.124033 | 0.666428 |
| WR | games_active | hist_gradient_boosting | validation | 2022 | all | 430 | 0.8 | 8.58719 | 0.642887 | 1.51031 | 0.844893 |
| WR | games_active | hist_gradient_boosting | validation | 2022 | top | 108 | 0.768519 | 9.89513 | 1.40527 | 2.19588 | 0.546266 |
| WR | games_active | hist_gradient_boosting | validation | 2022 | middle | 215 | 0.72093 | 9.19486 | 0.575684 | 1.89373 | 1.10592 |
| WR | games_active | hist_gradient_boosting | validation | 2022 | lower | 107 | 0.990654 | 6.04603 | 0.00841121 | 0.047891 | 0.621825 |
| WR | games_active | hist_gradient_boosting | validation | 2023 | all | 417 | 0.798561 | 8.49307 | 0.547758 | 1.46148 | 0.844821 |
| WR | games_active | hist_gradient_boosting | validation | 2023 | top | 105 | 0.828571 | 9.9737 | 1.0441 | 1.90394 | 0.460159 |
| WR | games_active | hist_gradient_boosting | validation | 2023 | middle | 208 | 0.697115 | 8.96332 | 0.557138 | 1.89203 | 1.1597 |
| WR | games_active | hist_gradient_boosting | validation | 2023 | lower | 104 | 0.971154 | 6.05768 | 0.0278846 | 0.153637 | 0.603429 |
| WR | games_active | hist_gradient_boosting | validation | 2024 | all | 424 | 0.834906 | 8.35249 | 0.555115 | 1.34933 | 0.795564 |
| WR | games_active | hist_gradient_boosting | validation | 2024 | top | 106 | 0.820755 | 9.26503 | 1.16492 | 1.8797 | 0.462286 |
| WR | games_active | hist_gradient_boosting | validation | 2024 | middle | 212 | 0.759434 | 8.94117 | 0.526352 | 1.74176 | 1.04827 |
| WR | games_active | hist_gradient_boosting | validation | 2024 | lower | 106 | 1 | 6.26258 | 0.00283019 | 0.0341113 | 0.623428 |
| WR | games_active | ridge | test | 2025 | all | 433 | 0.808314 | 8.36482 | 0.568619 | 1.47418 | 0.826149 |
| WR | games_active | ridge | test | 2025 | top | 109 | 0.816514 | 10.2593 | 1.12654 | 1.99422 | 0.521662 |
| WR | games_active | ridge | test | 2025 | middle | 215 | 0.716279 | 8.98467 | 0.551252 | 1.84347 | 1.04959 |
| WR | games_active | ridge | test | 2025 | lower | 109 | 0.981651 | 5.24774 | 0.0449541 | 0.225739 | 0.68991 |
| WR | games_active | ridge | validation | 2020 | all | 412 | 0.820388 | 9.5645 | 0.608189 | 1.64538 | 0.853821 |
| WR | games_active | ridge | validation | 2020 | top | 104 | 0.817308 | 10.8185 | 1.28898 | 1.92471 | 0.546851 |
| WR | games_active | ridge | validation | 2020 | middle | 205 | 0.731707 | 10.4149 | 0.563999 | 2.16473 | 1.11103 |
| WR | games_active | ridge | validation | 2020 | lower | 103 | 1 | 6.60579 | 0.00873786 | 0.329666 | 0.651841 |
| WR | games_active | ridge | validation | 2021 | all | 418 | 0.815789 | 9.22265 | 0.570461 | 1.62299 | 0.908651 |
| WR | games_active | ridge | validation | 2021 | top | 105 | 0.8 | 10.9883 | 1.10518 | 2.16234 | 0.516263 |
| WR | games_active | ridge | validation | 2021 | middle | 208 | 0.740385 | 9.88671 | 0.570237 | 2.029 | 1.17812 |
| WR | games_active | ridge | validation | 2021 | lower | 105 | 0.980952 | 6.14159 | 0.0361905 | 0.279376 | 0.767229 |
| WR | games_active | ridge | validation | 2022 | all | 430 | 0.793023 | 9.17175 | 0.574617 | 1.57424 | 0.83892 |
| WR | games_active | ridge | validation | 2022 | top | 108 | 0.768519 | 10.491 | 1.16424 | 2.04309 | 0.52192 |
| WR | games_active | ridge | validation | 2022 | middle | 215 | 0.702326 | 10.0152 | 0.561153 | 2.05729 | 1.11308 |
| WR | games_active | ridge | validation | 2022 | lower | 107 | 1 | 6.14551 | 0.00654206 | 0.130399 | 0.608009 |
| WR | games_active | ridge | validation | 2023 | all | 417 | 0.827338 | 9.18959 | 0.557527 | 1.53988 | 0.809148 |
| WR | games_active | ridge | validation | 2023 | top | 105 | 0.885714 | 10.641 | 0.941553 | 1.85394 | 0.390342 |
| WR | games_active | ridge | validation | 2023 | middle | 208 | 0.725962 | 9.96291 | 0.628008 | 2.05167 | 1.12792 |
| WR | games_active | ridge | validation | 2023 | lower | 104 | 0.971154 | 6.17764 | 0.0288462 | 0.199227 | 0.594431 |
| WR | games_active | ridge | validation | 2024 | all | 424 | 0.820755 | 8.85816 | 0.544965 | 1.44021 | 0.773471 |
| WR | games_active | ridge | validation | 2024 | top | 106 | 0.867925 | 9.97961 | 1.03708 | 1.86344 | 0.460667 |
| WR | games_active | ridge | validation | 2024 | middle | 212 | 0.712264 | 9.6515 | 0.565728 | 1.89172 | 1.01471 |
| WR | games_active | ridge | validation | 2024 | lower | 106 | 0.990566 | 6.15002 | 0.0113208 | 0.113973 | 0.603789 |

## Prediction center contract

````json
{
  "learned": "training_only_residual_adjusted_p50",
  "selection_matches_served_center": true,
  "transparent_baseline": "phase3_transparent_point"
}
````

## Uncertainty interpretation

Learned-candidate P10/P50/P90 values are empirical signed-residual intervals fitted only on earlier out-of-fold predictions; their coverage is measured, not guaranteed. A selected transparent baseline is served honestly as its validated Phase 3 point with P10=P50=P90, not as a calibrated interval.

## Rookie policy

````json
{
  "fallback": "transparent Phase 3 heuristic",
  "historical_training_rows": 0,
  "interval_status": "unvalidated_uncalibrated_point_only",
  "learned_models_used": false,
  "live_rookie_rows": 233,
  "reason": "A historical preseason-position archive is required before rookie model performance can be evaluated honestly."
}
````

## Rookie boundary

- 233 live rookies use transparent point fallbacks.
- No historical rookie ML metric is reported without a preseason-position archive.

## Quality checks

- All preprocessing and tuning are fold-local.
- [2020, 2021, 2022, 2023, 2024] cutoff-safe draft-relevant cohort MAE plus paired-bootstrap, pooled-MAE, and ranking safeguards select champions; 2025 never selects.
- Every learned candidate is compared against all five Phase 3 baselines.
- Interval coverage, width, and pinball loss are reported by position and tier.
- Artifacts are reloaded and must reproduce fitted predictions before registration.
- All registered artifacts and cards have SHA-256 hashes.
- The 2026 board covers every live feature row; rookies are labeled fallbacks.

## Limitations

- The candidate universe is a cutoff-safe proxy, not a historical roster list.
- PPG is conditional on positive mapped snap participation; missing targets stay null.
- Games-active predictions are bounded 0-18 because traded players can exceed 17.
- Direct fantasy-point targets are benchmarks; component-first extensions remain.
- ADP, availability, and draft optimization are not part of Phase 4.
- SHAP remains optional and was not required for this run.

## Diagnostic artifacts

````json
{
  "feature_response": "docs/images/phase4/phase4-052d2866899a665a44f3/attempt-331cdaf7eb7f4721aa43c08d469288ee/feature_response.svg",
  "hgb_permutation_importance": "docs/images/phase4/phase4-052d2866899a665a44f3/attempt-331cdaf7eb7f4721aa43c08d469288ee/hgb_permutation_importance.svg",
  "interval_coverage_width": "docs/images/phase4/phase4-052d2866899a665a44f3/attempt-331cdaf7eb7f4721aa43c08d469288ee/interval_coverage_width.svg",
  "ridge_coefficients": "docs/images/phase4/phase4-052d2866899a665a44f3/attempt-331cdaf7eb7f4721aa43c08d469288ee/ridge_coefficients.svg",
  "season_mae_comparison": "docs/images/phase4/phase4-052d2866899a665a44f3/attempt-331cdaf7eb7f4721aa43c08d469288ee/season_mae_comparison.svg",
  "segment_mae": "docs/images/phase4/phase4-052d2866899a665a44f3/attempt-331cdaf7eb7f4721aa43c08d469288ee/segment_mae.svg",
  "test_predicted_vs_actual": "docs/images/phase4/phase4-052d2866899a665a44f3/attempt-331cdaf7eb7f4721aa43c08d469288ee/test_predicted_vs_actual.svg",
  "test_residuals": "docs/images/phase4/phase4-052d2866899a665a44f3/attempt-331cdaf7eb7f4721aa43c08d469288ee/test_residuals.svg"
}
````

## Additional validated details

````json
{
  "publication_id": "attempt-331cdaf7eb7f4721aa43c08d469288ee",
  "selected_feature_data_fingerprint": "f156d6d537092f8780568f9e466c980f9a261eee08b8a7dd0852471ad795b116"
}
````

## Machine-readable detail

Per-segment metrics, model inventory, feature contract, and global explanations are retained in the matching JSON report.
