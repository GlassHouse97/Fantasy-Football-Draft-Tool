# Phase 4 Player Model Evaluation

Status: **PASSED**

Report fingerprint: `00ffb3d0c6bf51c4bed9a9556dec479749a0b7abcf829deab1e2e14a565978a5`

This report compares learned player models with transparent baselines using chronological validation. Test results are reported after selection.

## Data lineage

- baseline_report_fingerprint: `72043c4baf8f0e5b1b63d68af77b92b9f5f497483cdaa279155e586127944965`
- build_fingerprint: `f195dcb17a1a386b2f2003d87a06921550235cbec62aecd0f4eda419aa664cd7`
- feature_data_fingerprint: `d2bdda170fcbf88ccfe0b3f437615583a0684057eebe1fc12aa65463a47cf9cf`
- model_config_fingerprint: `1330e36662458945cc117f0b56daade21e7cb1c4bc91779b7a9d2c96e0d1d3f8`
- model_feature_fingerprint: `9b7be095acc27d5b3bb86a028d3e321cd8fd354914fef1aa8a2843a3ee5666e8`
- scoring_ruleset_fingerprint: `9f660dd5c8db91e63a1c43a5db74a3848b0554b2acf94d0fd891fe58b4eb7871`
- target_data_fingerprint: `dd759bbf87c146884e68425079b3a759d1d6d4bb434d5bccee6d9d91c98c56a9`

## Run metadata

- Phase: Phase 4 - statistical and ML player models
- Run id: phase4-7ae8e9aed04bffca00c0
- Run fingerprint: 7ae8e9aed04bffca00c04d05e623f8afd20877dcfa09ddf43a8c1a7e8c34db03
- Trained at: 2026-08-05T20:58:13+00:00
- Split strategy: expanding_prediction_seasons_with_nested_chronological_tuning

## Selection protocol

- Selection metric: pooled_validation_mae
- Selection rule: Select on pooled validation MAE with a paired-bootstrap uncertainty gate; learned must be strictly lower than the best transparent baseline and its learned-minus-baseline 95% CI upper bound must be below zero. Ties and inconclusive improvements retain the baseline.
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

| Position | Target | Source | Champion | Decision | Validation MAE | Reference baseline | Baseline MAE | Best learned | Learned MAE | Learned MAE improvement | Bootstrap CI lower | Bootstrap CI upper | Test MAE |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| QB | fantasy_points_per_game | baseline | age_position_adjusted | learned_regression_baseline_retained | 4.23008 | age_position_adjusted | 4.23008 | hist_gradient_boosting | 4.24004 | -0.00995609 | -0.268807 | 0.288028 | 4.63816 |
| QB | fantasy_points_total | learned | hist_gradient_boosting | learned_significant_improvement_selected | 41.2086 | age_position_adjusted | 51.3388 | hist_gradient_boosting | 41.2086 | 10.1302 | -13.815 | -6.36567 | 37.9816 |
| QB | games_active | learned | ridge | learned_significant_improvement_selected | 2.46524 | age_position_adjusted | 4.09064 | ridge | 2.46524 | 1.6254 | -1.89966 | -1.358 | 2.30138 |
| RB | fantasy_points_per_game | baseline | age_position_adjusted | learned_regression_baseline_retained | 2.63695 | age_position_adjusted | 2.63695 | hist_gradient_boosting | 2.66487 | -0.0279189 | -0.112087 | 0.163564 | 2.27009 |
| RB | fantasy_points_total | learned | hist_gradient_boosting | learned_significant_improvement_selected | 23.2168 | age_position_adjusted | 34.5589 | hist_gradient_boosting | 23.2168 | 11.3421 | -12.8967 | -9.88976 | 22.3794 |
| RB | games_active | learned | hist_gradient_boosting | learned_significant_improvement_selected | 3.0062 | age_position_adjusted | 6.17816 | hist_gradient_boosting | 3.0062 | 3.17196 | -3.45299 | -2.88973 | 2.67123 |
| TE | fantasy_points_per_game | baseline | age_position_adjusted | learned_regression_baseline_retained | 1.76878 | age_position_adjusted | 1.76878 | hist_gradient_boosting | 1.76897 | -0.00018966 | -0.0885413 | 0.0943808 | 1.63116 |
| TE | fantasy_points_total | learned | hist_gradient_boosting | learned_significant_improvement_selected | 16.3984 | age_position_adjusted | 23.6861 | hist_gradient_boosting | 16.3984 | 7.28776 | -8.48855 | -6.02837 | 13.3161 |
| TE | games_active | learned | hist_gradient_boosting | learned_significant_improvement_selected | 3.25215 | age_position_adjusted | 6.28561 | hist_gradient_boosting | 3.25215 | 3.03346 | -3.39 | -2.68817 | 2.5701 |
| WR | fantasy_points_per_game | learned | hist_gradient_boosting | learned_significant_improvement_selected | 2.36793 | age_position_adjusted | 2.50952 | hist_gradient_boosting | 2.36793 | 0.14159 | -0.235454 | -0.0539877 | 2.1201 |
| WR | fantasy_points_total | learned | hist_gradient_boosting | learned_significant_improvement_selected | 21.5237 | age_position_adjusted | 32.9322 | hist_gradient_boosting | 21.5237 | 11.4085 | -12.6187 | -10.2115 | 19.031 |
| WR | games_active | learned | hist_gradient_boosting | learned_significant_improvement_selected | 2.91774 | age_position_adjusted | 5.93888 | hist_gradient_boosting | 2.91774 | 3.02114 | -3.25681 | -2.78937 | 2.81191 |

## Required regression and ranking metrics

| Position | Target | Source | Candidate | Scope | Rows | MAE | RMSE | Median AE | Spearman | Top N | Mean annual top-N capture |
|---|---|---|---|---|---|---|---|---|---|---|---|
| QB | fantasy_points_per_game | baseline | age_position_adjusted | validation | 348 | 4.23008 | 5.76969 | 3.19275 | 0.657915 | 12 | 0.616667 |
| QB | fantasy_points_per_game | baseline | age_position_adjusted | test | 66 | 4.63816 | 6.11245 | 3.26384 | 0.616825 | 12 | 0.5 |
| QB | fantasy_points_per_game | baseline | position_shrinkage | validation | 348 | 4.38818 | 5.56297 | 3.72586 | 0.658148 | 12 | 0.583333 |
| QB | fantasy_points_per_game | baseline | position_shrinkage | test | 66 | 4.69889 | 5.74633 | 4.40898 | 0.651059 | 12 | 0.583333 |
| QB | fantasy_points_per_game | baseline | previous_season | validation | 348 | 4.80754 | 6.4316 | 3.47452 | 0.601379 | 12 | 0.583333 |
| QB | fantasy_points_per_game | baseline | previous_season | test | 66 | 5.24308 | 6.82662 | 4.07886 | 0.557857 | 12 | 0.416667 |
| QB | fantasy_points_per_game | baseline | weighted_components | validation | 348 | 4.26592 | 5.81023 | 3.125 | 0.657446 | 12 | 0.583333 |
| QB | fantasy_points_per_game | baseline | weighted_components | test | 66 | 4.6922 | 6.12048 | 3.7366 | 0.6086 | 12 | 0.5 |
| QB | fantasy_points_per_game | baseline | weighted_history | validation | 348 | 4.26592 | 5.81023 | 3.125 | 0.657446 | 12 | 0.583333 |
| QB | fantasy_points_per_game | baseline | weighted_history | test | 66 | 4.6922 | 6.12048 | 3.7366 | 0.6086 | 12 | 0.5 |
| QB | fantasy_points_per_game | learned | hist_gradient_boosting | validation | 348 | 4.24004 | 5.4385 | 3.47809 | 0.668433 | 12 | 0.583333 |
| QB | fantasy_points_per_game | learned | hist_gradient_boosting | test | 66 | 4.34153 | 5.37285 | 3.67576 | 0.673813 | 12 | 0.5 |
| QB | fantasy_points_per_game | learned | ridge | validation | 348 | 4.32295 | 5.57297 | 3.51201 | 0.667727 | 12 | 0.583333 |
| QB | fantasy_points_per_game | learned | ridge | test | 66 | 4.31238 | 5.22439 | 3.48741 | 0.703246 | 12 | 0.583333 |
| QB | fantasy_points_total | baseline | age_position_adjusted | validation | 618 | 51.3388 | 77.5431 | 32.1673 | 0.583915 | 12 | 0.533333 |
| QB | fantasy_points_total | baseline | age_position_adjusted | test | 124 | 51.3816 | 74.3122 | 28.7994 | 0.599392 | 12 | 0.666667 |
| QB | fantasy_points_total | baseline | position_shrinkage | validation | 618 | 65.6892 | 80.4599 | 56.3059 | 0.504769 | 12 | 0.516667 |
| QB | fantasy_points_total | baseline | position_shrinkage | test | 124 | 66.4154 | 77.6773 | 56.5642 | 0.546215 | 12 | 0.583333 |
| QB | fantasy_points_total | baseline | previous_season | validation | 618 | 64.7518 | 84.6305 | 75.8106 | 0.454912 | 12 | 0.6 |
| QB | fantasy_points_total | baseline | previous_season | test | 124 | 68.4777 | 86.8708 | 87.8333 | 0.499426 | 12 | 0.583333 |
| QB | fantasy_points_total | baseline | weighted_components | validation | 618 | 52.8707 | 80.5051 | 34.2094 | 0.575378 | 12 | 0.55 |
| QB | fantasy_points_total | baseline | weighted_components | test | 124 | 52.4134 | 75.9687 | 32.08 | 0.596092 | 12 | 0.583333 |
| QB | fantasy_points_total | baseline | weighted_history | validation | 618 | 52.8707 | 80.5051 | 34.2094 | 0.57545 | 12 | 0.55 |
| QB | fantasy_points_total | baseline | weighted_history | test | 124 | 52.4134 | 75.9687 | 32.08 | 0.596092 | 12 | 0.583333 |
| QB | fantasy_points_total | learned | hist_gradient_boosting | validation | 618 | 41.2086 | 68.7205 | 17.1186 | 0.672801 | 12 | 0.516667 |
| QB | fantasy_points_total | learned | hist_gradient_boosting | test | 124 | 37.9816 | 63.6972 | 10.6212 | 0.757057 | 12 | 0.416667 |
| QB | fantasy_points_total | learned | ridge | validation | 618 | 45.5782 | 67.532 | 26.4099 | 0.691402 | 12 | 0.533333 |
| QB | fantasy_points_total | learned | ridge | test | 124 | 43.394 | 63.3183 | 27.1789 | 0.760819 | 12 | 0.583333 |
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
| QB | games_active | learned | hist_gradient_boosting | validation | 618 | 2.54197 | 3.76154 | 1.75613 | 0.73361 | 12 | 0.4 |
| QB | games_active | learned | hist_gradient_boosting | test | 124 | 2.29573 | 3.40259 | 1.4017 | 0.816327 | 12 | 0.416667 |
| QB | games_active | learned | ridge | validation | 618 | 2.46524 | 3.65018 | 1.61036 | 0.747915 | 12 | 0.45 |
| QB | games_active | learned | ridge | test | 124 | 2.30138 | 3.31152 | 1.61162 | 0.821795 | 12 | 0.5 |
| RB | fantasy_points_per_game | baseline | age_position_adjusted | validation | 686 | 2.63695 | 3.72848 | 1.78273 | 0.761773 | 12 | 0.566667 |
| RB | fantasy_points_per_game | baseline | age_position_adjusted | test | 128 | 2.27009 | 3.0633 | 1.72458 | 0.78868 | 12 | 0.583333 |
| RB | fantasy_points_per_game | baseline | position_shrinkage | validation | 686 | 2.84192 | 3.68033 | 2.18097 | 0.759308 | 12 | 0.55 |
| RB | fantasy_points_per_game | baseline | position_shrinkage | test | 128 | 2.72047 | 3.39935 | 2.20823 | 0.75371 | 12 | 0.666667 |
| RB | fantasy_points_per_game | baseline | previous_season | validation | 686 | 2.8652 | 3.9235 | 2.11723 | 0.735766 | 12 | 0.6 |
| RB | fantasy_points_per_game | baseline | previous_season | test | 128 | 2.47996 | 3.45268 | 1.6421 | 0.781365 | 12 | 0.666667 |
| RB | fantasy_points_per_game | baseline | weighted_components | validation | 686 | 2.78325 | 3.91543 | 1.86965 | 0.75733 | 12 | 0.6 |
| RB | fantasy_points_per_game | baseline | weighted_components | test | 128 | 2.49616 | 3.31142 | 1.80687 | 0.781091 | 12 | 0.666667 |
| RB | fantasy_points_per_game | baseline | weighted_history | validation | 686 | 2.78325 | 3.91543 | 1.86965 | 0.757329 | 12 | 0.6 |
| RB | fantasy_points_per_game | baseline | weighted_history | test | 128 | 2.49616 | 3.31142 | 1.80687 | 0.781091 | 12 | 0.666667 |
| RB | fantasy_points_per_game | learned | hist_gradient_boosting | validation | 686 | 2.66487 | 3.66748 | 1.90016 | 0.755997 | 12 | 0.5 |
| RB | fantasy_points_per_game | learned | hist_gradient_boosting | test | 128 | 2.36854 | 3.26984 | 1.70073 | 0.762027 | 12 | 0.583333 |
| RB | fantasy_points_per_game | learned | ridge | validation | 686 | 2.66807 | 3.6181 | 1.93124 | 0.76271 | 12 | 0.55 |
| RB | fantasy_points_per_game | learned | ridge | test | 128 | 2.27198 | 3.1268 | 1.71602 | 0.793285 | 12 | 0.666667 |
| RB | fantasy_points_total | baseline | age_position_adjusted | validation | 1488 | 34.5589 | 51.5179 | 21.5836 | 0.537301 | 12 | 0.466667 |
| RB | fantasy_points_total | baseline | age_position_adjusted | test | 294 | 33.3858 | 49.7028 | 22.4561 | 0.483116 | 12 | 0.583333 |
| RB | fantasy_points_total | baseline | position_shrinkage | validation | 1488 | 45.6875 | 56.5191 | 39.7565 | 0.447759 | 12 | 0.466667 |
| RB | fantasy_points_total | baseline | position_shrinkage | test | 294 | 46.4857 | 57.4921 | 41.5497 | 0.421194 | 12 | 0.583333 |
| RB | fantasy_points_total | baseline | previous_season | validation | 1488 | 47.9314 | 61.587 | 57.4862 | 0.330087 | 12 | 0.466667 |
| RB | fantasy_points_total | baseline | previous_season | test | 294 | 48.1701 | 62.6209 | 62.3632 | 0.329258 | 12 | 0.75 |
| RB | fantasy_points_total | baseline | weighted_components | validation | 1488 | 37.8594 | 55.815 | 23.1603 | 0.517893 | 12 | 0.5 |
| RB | fantasy_points_total | baseline | weighted_components | test | 294 | 37.5788 | 55.0778 | 24.1827 | 0.467967 | 12 | 0.583333 |
| RB | fantasy_points_total | baseline | weighted_history | validation | 1488 | 37.8594 | 55.815 | 23.1603 | 0.517885 | 12 | 0.5 |
| RB | fantasy_points_total | baseline | weighted_history | test | 294 | 37.5788 | 55.0778 | 24.1827 | 0.467935 | 12 | 0.583333 |
| RB | fantasy_points_total | learned | hist_gradient_boosting | validation | 1488 | 23.2168 | 43.6585 | 6.50917 | 0.737958 | 12 | 0.433333 |
| RB | fantasy_points_total | learned | hist_gradient_boosting | test | 294 | 22.3794 | 46.1492 | 4.27117 | 0.728928 | 12 | 0.583333 |
| RB | fantasy_points_total | learned | ridge | validation | 1488 | 27.1127 | 43.8767 | 14.6567 | 0.714959 | 12 | 0.483333 |
| RB | fantasy_points_total | learned | ridge | test | 294 | 26.8907 | 44.329 | 13.2157 | 0.666323 | 12 | 0.75 |
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
| RB | games_active | learned | hist_gradient_boosting | validation | 1483 | 3.0062 | 4.53501 | 1.90491 | 0.756415 | 12 | 0.116667 |
| RB | games_active | learned | hist_gradient_boosting | test | 294 | 2.67123 | 4.24331 | 1.24506 | 0.772643 | 12 | 0.0833333 |
| RB | games_active | learned | ridge | validation | 1483 | 3.12784 | 4.51084 | 2.05078 | 0.756809 | 12 | 0.05 |
| RB | games_active | learned | ridge | test | 294 | 2.99421 | 4.49017 | 1.62017 | 0.744185 | 12 | 0 |
| TE | fantasy_points_per_game | baseline | age_position_adjusted | validation | 565 | 1.76878 | 2.42216 | 1.34131 | 0.753998 | 12 | 0.616667 |
| TE | fantasy_points_per_game | baseline | age_position_adjusted | test | 122 | 1.63116 | 2.35215 | 1.0886 | 0.784101 | 12 | 0.5 |
| TE | fantasy_points_per_game | baseline | position_shrinkage | validation | 565 | 1.89745 | 2.42496 | 1.56603 | 0.716572 | 12 | 0.616667 |
| TE | fantasy_points_per_game | baseline | position_shrinkage | test | 122 | 1.88063 | 2.4863 | 1.41342 | 0.719511 | 12 | 0.5 |
| TE | fantasy_points_per_game | baseline | previous_season | validation | 565 | 1.90567 | 2.57141 | 1.4 | 0.714067 | 12 | 0.65 |
| TE | fantasy_points_per_game | baseline | previous_season | test | 122 | 1.90235 | 2.65904 | 1.24916 | 0.726307 | 12 | 0.5 |
| TE | fantasy_points_per_game | baseline | weighted_components | validation | 565 | 1.79923 | 2.45669 | 1.34853 | 0.751407 | 12 | 0.633333 |
| TE | fantasy_points_per_game | baseline | weighted_components | test | 122 | 1.6748 | 2.45766 | 1.1065 | 0.778681 | 12 | 0.5 |
| TE | fantasy_points_per_game | baseline | weighted_history | validation | 565 | 1.79923 | 2.45669 | 1.34853 | 0.751409 | 12 | 0.633333 |
| TE | fantasy_points_per_game | baseline | weighted_history | test | 122 | 1.6748 | 2.45766 | 1.1065 | 0.778681 | 12 | 0.5 |
| TE | fantasy_points_per_game | learned | hist_gradient_boosting | validation | 565 | 1.76897 | 2.37818 | 1.2903 | 0.746705 | 12 | 0.616667 |
| TE | fantasy_points_per_game | learned | hist_gradient_boosting | test | 122 | 1.5948 | 2.35665 | 0.854649 | 0.787423 | 12 | 0.5 |
| TE | fantasy_points_per_game | learned | ridge | validation | 565 | 1.94436 | 2.68389 | 1.44475 | 0.70143 | 12 | 0.65 |
| TE | fantasy_points_per_game | learned | ridge | test | 122 | 1.73482 | 2.57308 | 0.999517 | 0.783424 | 12 | 0.583333 |
| TE | fantasy_points_total | baseline | age_position_adjusted | validation | 1160 | 23.6861 | 34.9046 | 16.6181 | 0.543015 | 12 | 0.483333 |
| TE | fantasy_points_total | baseline | age_position_adjusted | test | 237 | 22.0405 | 32.2427 | 13.9383 | 0.554076 | 12 | 0.416667 |
| TE | fantasy_points_total | baseline | position_shrinkage | validation | 1160 | 29.4239 | 36.4369 | 24.6278 | 0.476327 | 12 | 0.483333 |
| TE | fantasy_points_total | baseline | position_shrinkage | test | 237 | 27.6593 | 34.3405 | 23.2146 | 0.457253 | 12 | 0.5 |
| TE | fantasy_points_total | baseline | previous_season | validation | 1160 | 30.7262 | 39.2747 | 35.9115 | 0.379127 | 12 | 0.483333 |
| TE | fantasy_points_total | baseline | previous_season | test | 237 | 31.3559 | 38.8978 | 40.181 | 0.32328 | 12 | 0.5 |
| TE | fantasy_points_total | baseline | weighted_components | validation | 1160 | 24.575 | 36.2864 | 17.0953 | 0.532213 | 12 | 0.45 |
| TE | fantasy_points_total | baseline | weighted_components | test | 237 | 23.0995 | 33.6422 | 14.1547 | 0.549805 | 12 | 0.416667 |
| TE | fantasy_points_total | baseline | weighted_history | validation | 1160 | 24.575 | 36.2864 | 17.0953 | 0.532204 | 12 | 0.45 |
| TE | fantasy_points_total | baseline | weighted_history | test | 237 | 23.0995 | 33.6422 | 14.1547 | 0.549819 | 12 | 0.416667 |
| TE | fantasy_points_total | learned | hist_gradient_boosting | validation | 1160 | 16.3984 | 29.9007 | 4.79298 | 0.753824 | 12 | 0.483333 |
| TE | fantasy_points_total | learned | hist_gradient_boosting | test | 237 | 13.3161 | 26.1771 | 3.05994 | 0.822961 | 12 | 0.5 |
| TE | fantasy_points_total | learned | ridge | validation | 1160 | 19.3157 | 32.3939 | 10.3753 | 0.712927 | 12 | 0.516667 |
| TE | fantasy_points_total | learned | ridge | test | 237 | 16.779 | 28.789 | 8.68132 | 0.78152 | 12 | 0.5 |
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
| TE | games_active | learned | ridge | validation | 1158 | 3.64357 | 5.02217 | 2.94807 | 0.711439 | 12 | 0.0333333 |
| TE | games_active | learned | ridge | test | 235 | 2.8742 | 4.08006 | 2.3312 | 0.798954 | 12 | 0 |
| WR | fantasy_points_per_game | baseline | age_position_adjusted | validation | 989 | 2.50952 | 3.28889 | 1.9525 | 0.758449 | 12 | 0.516667 |
| WR | fantasy_points_per_game | baseline | age_position_adjusted | test | 198 | 2.25656 | 2.9202 | 1.79706 | 0.813023 | 12 | 0.583333 |
| WR | fantasy_points_per_game | baseline | position_shrinkage | validation | 989 | 2.77451 | 3.39377 | 2.45173 | 0.742016 | 12 | 0.516667 |
| WR | fantasy_points_per_game | baseline | position_shrinkage | test | 198 | 2.43741 | 3.04938 | 2.03722 | 0.790151 | 12 | 0.583333 |
| WR | fantasy_points_per_game | baseline | previous_season | validation | 989 | 2.76831 | 3.63967 | 2.21 | 0.730573 | 12 | 0.533333 |
| WR | fantasy_points_per_game | baseline | previous_season | test | 198 | 2.56141 | 3.36236 | 2.07793 | 0.785464 | 12 | 0.5 |
| WR | fantasy_points_per_game | baseline | weighted_components | validation | 989 | 2.63116 | 3.45256 | 2.05659 | 0.751856 | 12 | 0.55 |
| WR | fantasy_points_per_game | baseline | weighted_components | test | 198 | 2.41075 | 3.15466 | 1.86702 | 0.802269 | 12 | 0.583333 |
| WR | fantasy_points_per_game | baseline | weighted_history | validation | 989 | 2.63116 | 3.45256 | 2.05659 | 0.751859 | 12 | 0.55 |
| WR | fantasy_points_per_game | baseline | weighted_history | test | 198 | 2.41075 | 3.15466 | 1.86702 | 0.802266 | 12 | 0.583333 |
| WR | fantasy_points_per_game | learned | hist_gradient_boosting | validation | 989 | 2.36793 | 3.17204 | 1.71416 | 0.759998 | 12 | 0.5 |
| WR | fantasy_points_per_game | learned | hist_gradient_boosting | test | 198 | 2.1201 | 2.7802 | 1.64687 | 0.83098 | 12 | 0.5 |
| WR | fantasy_points_per_game | learned | ridge | validation | 989 | 2.58558 | 3.46265 | 2.03102 | 0.758744 | 12 | 0.566667 |
| WR | fantasy_points_per_game | learned | ridge | test | 198 | 2.13265 | 2.73362 | 1.68293 | 0.841083 | 12 | 0.583333 |
| WR | fantasy_points_total | baseline | age_position_adjusted | validation | 2109 | 32.9322 | 46.8563 | 23.5529 | 0.568835 | 12 | 0.55 |
| WR | fantasy_points_total | baseline | age_position_adjusted | test | 434 | 32.0677 | 47.2908 | 19.722 | 0.567753 | 12 | 0.25 |
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
| WR | fantasy_points_total | learned | ridge | validation | 2109 | 27.9471 | 43.1835 | 16.9704 | 0.7021 | 12 | 0.483333 |
| WR | fantasy_points_total | learned | ridge | test | 434 | 22.8137 | 36.0592 | 12.7766 | 0.716527 | 12 | 0.333333 |
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
| WR | games_active | learned | hist_gradient_boosting | validation | 2101 | 2.91774 | 4.45276 | 1.81956 | 0.755432 | 12 | 0.0833333 |
| WR | games_active | learned | hist_gradient_boosting | test | 433 | 2.81191 | 4.40217 | 1.42482 | 0.733446 | 12 | 0 |
| WR | games_active | learned | ridge | validation | 2101 | 3.13872 | 4.4167 | 2.08933 | 0.756228 | 12 | 0.1 |
| WR | games_active | learned | ridge | test | 433 | 2.94957 | 4.39303 | 1.9549 | 0.732695 | 12 | 0.0833333 |

## Champion error by experience and projection tier

| Position | Target | Source | Champion | Scope | Segment type | Segment | Rows | MAE | RMSE | Median AE | Spearman |
|---|---|---|---|---|---|---|---|---|---|---|---|
| QB | fantasy_points_per_game | baseline | age_position_adjusted | validation | experience_group | sparse | 62 | 4.51745 | 6.55387 | 2.93 | 0.491161 |
| QB | fantasy_points_per_game | baseline | age_position_adjusted | validation | experience_group | veteran | 286 | 4.16779 | 5.58519 | 3.22052 | 0.68199 |
| QB | fantasy_points_per_game | baseline | age_position_adjusted | validation | projection_tier | lower | 55 | 4.38003 | 6.45294 | 2.58545 | 0.0511581 |
| QB | fantasy_points_per_game | baseline | age_position_adjusted | validation | projection_tier | middle | 152 | 4.47366 | 5.65466 | 3.655 | 0.399667 |
| QB | fantasy_points_per_game | baseline | age_position_adjusted | validation | projection_tier | top | 141 | 3.90902 | 5.6079 | 2.40348 | 0.606715 |
| QB | fantasy_points_per_game | baseline | age_position_adjusted | test | experience_group | sparse | 9 | 5.82737 | 7.55338 | 4.54444 | 0.0833333 |
| QB | fantasy_points_per_game | baseline | age_position_adjusted | test | experience_group | veteran | 57 | 4.45039 | 5.8526 | 2.95753 | 0.648691 |
| QB | fantasy_points_per_game | baseline | age_position_adjusted | test | projection_tier | lower | 7 | 2.16158 | 2.5637 | 1.29729 | -0.642857 |
| QB | fantasy_points_per_game | baseline | age_position_adjusted | test | projection_tier | middle | 32 | 4.77326 | 5.66622 | 4.59533 | 0.336877 |
| QB | fantasy_points_per_game | baseline | age_position_adjusted | test | projection_tier | top | 27 | 5.12012 | 7.18151 | 2.95753 | 0.310745 |
| QB | fantasy_points_total | learned | hist_gradient_boosting | validation | experience_group | sparse | 236 | 19.619 | 38.5956 | 6.55118 | 0.493477 |
| QB | fantasy_points_total | learned | hist_gradient_boosting | validation | experience_group | veteran | 382 | 54.5467 | 81.9742 | 30.7113 | 0.652151 |
| QB | fantasy_points_total | learned | hist_gradient_boosting | validation | projection_tier | lower | 154 | 11.7571 | 29.8203 | 5.17082 | -0.00685559 |
| QB | fantasy_points_total | learned | hist_gradient_boosting | validation | projection_tier | middle | 310 | 31.2061 | 53.4557 | 16.3276 | 0.414121 |
| QB | fantasy_points_total | learned | hist_gradient_boosting | validation | projection_tier | top | 154 | 90.795 | 110.95 | 83.724 | 0.414046 |
| QB | fantasy_points_total | learned | hist_gradient_boosting | test | experience_group | sparse | 43 | 21.9428 | 45.5608 | 4.32957 | 0.664968 |
| QB | fantasy_points_total | learned | hist_gradient_boosting | test | experience_group | veteran | 81 | 46.496 | 71.4791 | 30.142 | 0.748582 |
| QB | fantasy_points_total | learned | hist_gradient_boosting | test | projection_tier | lower | 31 | 4.38749 | 6.55701 | 3.75026 | 0.0142019 |
| QB | fantasy_points_total | learned | hist_gradient_boosting | test | projection_tier | middle | 62 | 29.3457 | 46.851 | 11.6154 | 0.439028 |
| QB | fantasy_points_total | learned | hist_gradient_boosting | test | projection_tier | top | 31 | 88.8474 | 108.611 | 74.6239 | 0.2875 |
| QB | games_active | learned | ridge | validation | experience_group | sparse | 236 | 1.35134 | 2.3411 | 0.600553 | 0.607101 |
| QB | games_active | learned | ridge | validation | experience_group | veteran | 382 | 3.15341 | 4.26254 | 2.54595 | 0.690639 |
| QB | games_active | learned | ridge | validation | projection_tier | lower | 154 | 0.51088 | 1.28862 | 0 | -0.0845188 |
| QB | games_active | learned | ridge | validation | projection_tier | middle | 310 | 2.82183 | 3.86006 | 2.12985 | 0.457446 |
| QB | games_active | learned | ridge | validation | projection_tier | top | 154 | 3.70178 | 4.67054 | 3.11568 | 0.406019 |
| QB | games_active | learned | ridge | test | experience_group | sparse | 43 | 1.30663 | 2.28868 | 0.385439 | 0.734292 |
| QB | games_active | learned | ridge | test | experience_group | veteran | 81 | 2.82945 | 3.7426 | 2.2744 | 0.764296 |
| QB | games_active | learned | ridge | test | projection_tier | lower | 31 | 0.147086 | 0.531576 | 0 | 0.342201 |
| QB | games_active | learned | ridge | test | projection_tier | middle | 62 | 2.2875 | 2.99217 | 1.69771 | 0.653606 |
| QB | games_active | learned | ridge | test | projection_tier | top | 31 | 4.48341 | 5.06715 | 4.15365 | 0.379365 |
| RB | fantasy_points_per_game | baseline | age_position_adjusted | validation | experience_group | sparse | 154 | 2.66453 | 4.18978 | 1.51529 | 0.659473 |
| RB | fantasy_points_per_game | baseline | age_position_adjusted | validation | experience_group | veteran | 532 | 2.62897 | 3.58388 | 1.86996 | 0.787055 |
| RB | fantasy_points_per_game | baseline | age_position_adjusted | validation | projection_tier | lower | 122 | 1.02542 | 2.01827 | 0.393557 | 0.113084 |
| RB | fantasy_points_per_game | baseline | age_position_adjusted | validation | projection_tier | middle | 256 | 2.23758 | 3.29013 | 1.4777 | 0.360808 |
| RB | fantasy_points_per_game | baseline | age_position_adjusted | validation | projection_tier | top | 308 | 3.60723 | 4.51128 | 3.33266 | 0.610866 |
| RB | fantasy_points_per_game | baseline | age_position_adjusted | test | experience_group | sparse | 25 | 2.05425 | 2.77692 | 1.33712 | 0.47278 |
| RB | fantasy_points_per_game | baseline | age_position_adjusted | test | experience_group | veteran | 103 | 2.32248 | 3.12886 | 1.78417 | 0.834116 |
| RB | fantasy_points_per_game | baseline | age_position_adjusted | test | projection_tier | lower | 27 | 0.83447 | 1.33359 | 0.469886 | 0.204403 |
| RB | fantasy_points_per_game | baseline | age_position_adjusted | test | projection_tier | middle | 44 | 2.13742 | 2.7842 | 1.77739 | 0.41575 |
| RB | fantasy_points_per_game | baseline | age_position_adjusted | test | projection_tier | top | 57 | 3.05252 | 3.77441 | 2.82576 | 0.810604 |
| RB | fantasy_points_total | learned | hist_gradient_boosting | validation | experience_group | sparse | 650 | 12.8315 | 30.8408 | 3.26804 | 0.609505 |
| RB | fantasy_points_total | learned | hist_gradient_boosting | validation | experience_group | veteran | 838 | 31.2722 | 51.4465 | 13.4065 | 0.732547 |
| RB | fantasy_points_total | learned | hist_gradient_boosting | validation | projection_tier | lower | 373 | 2.67757 | 4.22395 | 1.33281 | -0.0272249 |
| RB | fantasy_points_total | learned | hist_gradient_boosting | validation | projection_tier | middle | 742 | 15.1855 | 29.2639 | 6.60698 | 0.404799 |
| RB | fantasy_points_total | learned | hist_gradient_boosting | validation | projection_tier | top | 373 | 59.7324 | 76.6969 | 48.8935 | 0.601535 |
| RB | fantasy_points_total | learned | hist_gradient_boosting | test | experience_group | sparse | 132 | 7.63217 | 18.4047 | 1.20347 | 0.473809 |
| RB | fantasy_points_total | learned | hist_gradient_boosting | test | experience_group | veteran | 162 | 34.3957 | 59.9091 | 14.1632 | 0.752354 |
| RB | fantasy_points_total | learned | hist_gradient_boosting | test | projection_tier | lower | 74 | 2.36139 | 5.4959 | 1.37217 | 0.13812 |
| RB | fantasy_points_total | learned | hist_gradient_boosting | test | projection_tier | middle | 146 | 10.2359 | 21.8276 | 4.27117 | 0.490533 |
| RB | fantasy_points_total | learned | hist_gradient_boosting | test | projection_tier | top | 74 | 66.3562 | 86.5519 | 53.5207 | 0.585356 |
| RB | games_active | learned | hist_gradient_boosting | validation | experience_group | sparse | 645 | 1.67244 | 3.39392 | 0.153156 | 0.695762 |
| RB | games_active | learned | hist_gradient_boosting | validation | experience_group | veteran | 838 | 4.03278 | 5.24692 | 3.32462 | 0.659989 |
| RB | games_active | learned | hist_gradient_boosting | validation | projection_tier | lower | 370 | 0.179461 | 1.3813 | 0 | 0.0705207 |
| RB | games_active | learned | hist_gradient_boosting | validation | projection_tier | middle | 740 | 3.70368 | 5.10009 | 2.62804 | 0.600373 |
| RB | games_active | learned | hist_gradient_boosting | validation | projection_tier | top | 373 | 4.42647 | 5.31723 | 3.87609 | 0.172997 |
| RB | games_active | learned | hist_gradient_boosting | test | experience_group | sparse | 132 | 1.20353 | 2.63366 | 0.0691239 | 0.616831 |
| RB | games_active | learned | hist_gradient_boosting | test | experience_group | veteran | 162 | 3.86712 | 5.19859 | 3.24798 | 0.692662 |
| RB | games_active | learned | hist_gradient_boosting | test | projection_tier | lower | 74 | 0.0406147 | 0.348743 | 0 | -0.0136986 |
| RB | games_active | learned | hist_gradient_boosting | test | projection_tier | middle | 146 | 3.13558 | 4.60893 | 1.9198 | 0.586383 |
| RB | games_active | learned | hist_gradient_boosting | test | projection_tier | top | 74 | 4.38567 | 5.43177 | 3.82624 | 0.234725 |
| TE | fantasy_points_per_game | baseline | age_position_adjusted | validation | experience_group | sparse | 129 | 1.5183 | 2.18673 | 1.15894 | 0.62224 |
| TE | fantasy_points_per_game | baseline | age_position_adjusted | validation | experience_group | veteran | 436 | 1.84289 | 2.48755 | 1.4003 | 0.774025 |
| TE | fantasy_points_per_game | baseline | age_position_adjusted | validation | projection_tier | lower | 98 | 0.620506 | 1.06325 | 0.351576 | 0.0978488 |
| TE | fantasy_points_per_game | baseline | age_position_adjusted | validation | projection_tier | middle | 237 | 1.5057 | 2.0781 | 1.17976 | 0.315451 |
| TE | fantasy_points_per_game | baseline | age_position_adjusted | validation | projection_tier | top | 230 | 2.52913 | 3.07903 | 2.27386 | 0.635551 |
| TE | fantasy_points_per_game | baseline | age_position_adjusted | test | experience_group | sparse | 20 | 1.04092 | 1.64496 | 0.529202 | 0.695823 |
| TE | fantasy_points_per_game | baseline | age_position_adjusted | test | experience_group | veteran | 102 | 1.7469 | 2.46716 | 1.14636 | 0.780688 |
| TE | fantasy_points_per_game | baseline | age_position_adjusted | test | projection_tier | lower | 20 | 0.673267 | 1.41882 | 0.0769716 | 0.4482 |
| TE | fantasy_points_per_game | baseline | age_position_adjusted | test | projection_tier | middle | 56 | 1.10442 | 1.64815 | 0.872221 | 0.378671 |
| TE | fantasy_points_per_game | baseline | age_position_adjusted | test | projection_tier | top | 46 | 2.68889 | 3.23903 | 2.63055 | 0.563861 |
| TE | fantasy_points_total | learned | hist_gradient_boosting | validation | experience_group | sparse | 487 | 7.34999 | 16.737 | 2.33906 | 0.600087 |
| TE | fantasy_points_total | learned | hist_gradient_boosting | validation | experience_group | veteran | 673 | 22.946 | 36.5828 | 11.6289 | 0.755907 |
| TE | fantasy_points_total | learned | hist_gradient_boosting | validation | projection_tier | lower | 290 | 2.47766 | 3.91754 | 1.98428 | -0.0425545 |
| TE | fantasy_points_total | learned | hist_gradient_boosting | validation | projection_tier | middle | 580 | 10.91 | 20.0044 | 5.0873 | 0.491417 |
| TE | fantasy_points_total | learned | hist_gradient_boosting | validation | projection_tier | top | 290 | 41.296 | 52.5406 | 34.2528 | 0.583524 |
| TE | fantasy_points_total | learned | hist_gradient_boosting | test | experience_group | sparse | 101 | 4.14395 | 11.7539 | 0.70338 | 0.586137 |
| TE | fantasy_points_total | learned | hist_gradient_boosting | test | experience_group | veteran | 136 | 20.1278 | 33.0383 | 8.86832 | 0.827756 |
| TE | fantasy_points_total | learned | hist_gradient_boosting | test | projection_tier | lower | 59 | 0.868423 | 1.39184 | 0.70338 | 0.2211 |
| TE | fantasy_points_total | learned | hist_gradient_boosting | test | projection_tier | middle | 119 | 7.96864 | 15.816 | 3.60518 | 0.625209 |
| TE | fantasy_points_total | learned | hist_gradient_boosting | test | projection_tier | top | 59 | 36.5493 | 47.3931 | 27.0995 | 0.704658 |
| TE | games_active | learned | hist_gradient_boosting | validation | experience_group | sparse | 485 | 1.81305 | 3.40397 | 0.259798 | 0.687239 |
| TE | games_active | learned | hist_gradient_boosting | validation | experience_group | veteran | 673 | 4.28925 | 5.53876 | 3.77058 | 0.640081 |
| TE | games_active | learned | hist_gradient_boosting | validation | projection_tier | lower | 290 | 0.251121 | 1.39321 | 0 | 0.100918 |
| TE | games_active | learned | hist_gradient_boosting | validation | projection_tier | middle | 578 | 4.39717 | 5.69905 | 3.75078 | 0.535088 |
| TE | games_active | learned | hist_gradient_boosting | validation | projection_tier | top | 290 | 3.97105 | 4.88841 | 3.56922 | 0.201305 |
| TE | games_active | learned | hist_gradient_boosting | test | experience_group | sparse | 99 | 1.48424 | 3.28598 | 0.116429 | 0.625707 |
| TE | games_active | learned | hist_gradient_boosting | test | experience_group | veteran | 136 | 3.36055 | 4.40066 | 2.87157 | 0.704072 |
| TE | games_active | learned | hist_gradient_boosting | test | projection_tier | lower | 59 | 0.0977622 | 0.460662 | 0 | 0.129762 |
| TE | games_active | learned | hist_gradient_boosting | test | projection_tier | middle | 117 | 3.64073 | 4.9351 | 3.06122 | 0.682316 |
| TE | games_active | learned | hist_gradient_boosting | test | projection_tier | top | 59 | 2.91934 | 3.77469 | 2.39372 | 0.148714 |
| WR | fantasy_points_per_game | learned | hist_gradient_boosting | validation | experience_group | sparse | 224 | 2.09297 | 2.76736 | 1.53971 | 0.713359 |
| WR | fantasy_points_per_game | learned | hist_gradient_boosting | validation | experience_group | veteran | 765 | 2.44844 | 3.2811 | 1.74311 | 0.767549 |
| WR | fantasy_points_per_game | learned | hist_gradient_boosting | validation | projection_tier | lower | 134 | 1.4719 | 2.45123 | 0.768837 | 0.192933 |
| WR | fantasy_points_per_game | learned | hist_gradient_boosting | validation | projection_tier | middle | 387 | 2.0424 | 2.76531 | 1.46916 | 0.275831 |
| WR | fantasy_points_per_game | learned | hist_gradient_boosting | validation | projection_tier | top | 468 | 2.89368 | 3.63584 | 2.49949 | 0.748291 |
| WR | fantasy_points_per_game | learned | hist_gradient_boosting | test | experience_group | sparse | 47 | 1.88697 | 2.40189 | 1.77984 | 0.702165 |
| WR | fantasy_points_per_game | learned | hist_gradient_boosting | test | experience_group | veteran | 151 | 2.19266 | 2.88785 | 1.64208 | 0.849663 |
| WR | fantasy_points_per_game | learned | hist_gradient_boosting | test | projection_tier | lower | 37 | 1.20417 | 1.66568 | 0.678496 | 0.00119141 |
| WR | fantasy_points_per_game | learned | hist_gradient_boosting | test | projection_tier | middle | 70 | 1.61077 | 2.10053 | 1.16852 | 0.423964 |
| WR | fantasy_points_per_game | learned | hist_gradient_boosting | test | projection_tier | top | 91 | 2.8843 | 3.50655 | 2.19885 | 0.706753 |
| WR | fantasy_points_total | learned | hist_gradient_boosting | validation | experience_group | sparse | 920 | 10.5198 | 24.1922 | 1.95597 | 0.611244 |
| WR | fantasy_points_total | learned | hist_gradient_boosting | validation | experience_group | veteran | 1189 | 30.0381 | 47.6858 | 13.3842 | 0.751937 |
| WR | fantasy_points_total | learned | hist_gradient_boosting | validation | projection_tier | lower | 528 | 2.52786 | 5.54172 | 1.6755 | -0.0237062 |
| WR | fantasy_points_total | learned | hist_gradient_boosting | validation | projection_tier | middle | 1053 | 14.3688 | 27.7614 | 5.22964 | 0.452118 |
| WR | fantasy_points_total | learned | hist_gradient_boosting | validation | projection_tier | top | 528 | 54.7887 | 67.6219 | 48.939 | 0.645575 |
| WR | fantasy_points_total | learned | hist_gradient_boosting | test | experience_group | sparse | 201 | 9.12101 | 25.5286 | 1.36661 | 0.605259 |
| WR | fantasy_points_total | learned | hist_gradient_boosting | test | experience_group | veteran | 233 | 27.58 | 44.6139 | 11.2552 | 0.785756 |
| WR | fantasy_points_total | learned | hist_gradient_boosting | test | projection_tier | lower | 109 | 2.38509 | 6.36951 | 1.36661 | -0.0416981 |
| WR | fantasy_points_total | learned | hist_gradient_boosting | test | projection_tier | middle | 216 | 9.35451 | 16.003 | 4.44065 | 0.412274 |
| WR | fantasy_points_total | learned | hist_gradient_boosting | test | projection_tier | top | 109 | 54.8525 | 70.0602 | 51.7391 | 0.570137 |
| WR | games_active | learned | hist_gradient_boosting | validation | experience_group | sparse | 912 | 1.53164 | 3.0207 | 0.175717 | 0.683058 |
| WR | games_active | learned | hist_gradient_boosting | validation | experience_group | veteran | 1189 | 3.98093 | 5.29492 | 3.10623 | 0.65632 |
| WR | games_active | learned | hist_gradient_boosting | validation | projection_tier | lower | 525 | 0.240793 | 1.38061 | 0 | 0.0513316 |
| WR | games_active | learned | hist_gradient_boosting | validation | projection_tier | middle | 1048 | 3.70142 | 5.13168 | 2.52481 | 0.559873 |
| WR | games_active | learned | hist_gradient_boosting | validation | projection_tier | top | 528 | 4.02401 | 4.97301 | 3.351 | 0.169309 |
| WR | games_active | learned | hist_gradient_boosting | test | experience_group | sparse | 200 | 1.80176 | 3.72073 | 0.081523 | 0.630439 |
| WR | games_active | learned | hist_gradient_boosting | test | experience_group | veteran | 233 | 3.679 | 4.91227 | 2.80175 | 0.680263 |
| WR | games_active | learned | hist_gradient_boosting | test | projection_tier | lower | 109 | 0.304012 | 1.81988 | 0 | -0.0678287 |
| WR | games_active | learned | hist_gradient_boosting | test | projection_tier | middle | 215 | 3.56711 | 5.04041 | 2.45345 | 0.490843 |
| WR | games_active | learned | hist_gradient_boosting | test | projection_tier | top | 109 | 3.83021 | 4.85375 | 2.89171 | 0.0833217 |

## Candidate comparison

| Position | Target | Source | Candidate | Validation rows | Validation MAE | Test rows | Test MAE |
|---|---|---|---|---|---|---|---|
| QB | fantasy_points_per_game | baseline | age_position_adjusted | 348 | 4.23008 | 66 | 4.63816 |
| QB | fantasy_points_per_game | baseline | position_shrinkage | 348 | 4.38818 | 66 | 4.69889 |
| QB | fantasy_points_per_game | baseline | previous_season | 348 | 4.80754 | 66 | 5.24308 |
| QB | fantasy_points_per_game | baseline | weighted_components | 348 | 4.26592 | 66 | 4.6922 |
| QB | fantasy_points_per_game | baseline | weighted_history | 348 | 4.26592 | 66 | 4.6922 |
| QB | fantasy_points_per_game | learned | hist_gradient_boosting | 348 | 4.24004 | 66 | 4.34153 |
| QB | fantasy_points_per_game | learned | ridge | 348 | 4.32295 | 66 | 4.31238 |
| QB | fantasy_points_total | baseline | age_position_adjusted | 618 | 51.3388 | 124 | 51.3816 |
| QB | fantasy_points_total | baseline | position_shrinkage | 618 | 65.6892 | 124 | 66.4154 |
| QB | fantasy_points_total | baseline | previous_season | 618 | 64.7518 | 124 | 68.4777 |
| QB | fantasy_points_total | baseline | weighted_components | 618 | 52.8707 | 124 | 52.4134 |
| QB | fantasy_points_total | baseline | weighted_history | 618 | 52.8707 | 124 | 52.4134 |
| QB | fantasy_points_total | learned | hist_gradient_boosting | 618 | 41.2086 | 124 | 37.9816 |
| QB | fantasy_points_total | learned | ridge | 618 | 45.5782 | 124 | 43.394 |
| QB | games_active | baseline | age_position_adjusted | 618 | 4.09064 | 124 | 4.06355 |
| QB | games_active | baseline | position_shrinkage | 618 | 5.22732 | 124 | 5.3718 |
| QB | games_active | baseline | previous_season | 618 | 5.05585 | 124 | 5.33105 |
| QB | games_active | baseline | weighted_components | 618 | 4.09064 | 124 | 4.06355 |
| QB | games_active | baseline | weighted_history | 618 | 4.09064 | 124 | 4.06355 |
| QB | games_active | learned | hist_gradient_boosting | 618 | 2.54197 | 124 | 2.29573 |
| QB | games_active | learned | ridge | 618 | 2.46524 | 124 | 2.30138 |
| RB | fantasy_points_per_game | baseline | age_position_adjusted | 686 | 2.63695 | 128 | 2.27009 |
| RB | fantasy_points_per_game | baseline | position_shrinkage | 686 | 2.84192 | 128 | 2.72047 |
| RB | fantasy_points_per_game | baseline | previous_season | 686 | 2.8652 | 128 | 2.47996 |
| RB | fantasy_points_per_game | baseline | weighted_components | 686 | 2.78325 | 128 | 2.49616 |
| RB | fantasy_points_per_game | baseline | weighted_history | 686 | 2.78325 | 128 | 2.49616 |
| RB | fantasy_points_per_game | learned | hist_gradient_boosting | 686 | 2.66487 | 128 | 2.36854 |
| RB | fantasy_points_per_game | learned | ridge | 686 | 2.66807 | 128 | 2.27198 |
| RB | fantasy_points_total | baseline | age_position_adjusted | 1488 | 34.5589 | 294 | 33.3858 |
| RB | fantasy_points_total | baseline | position_shrinkage | 1488 | 45.6875 | 294 | 46.4857 |
| RB | fantasy_points_total | baseline | previous_season | 1488 | 47.9314 | 294 | 48.1701 |
| RB | fantasy_points_total | baseline | weighted_components | 1488 | 37.8594 | 294 | 37.5788 |
| RB | fantasy_points_total | baseline | weighted_history | 1488 | 37.8594 | 294 | 37.5788 |
| RB | fantasy_points_total | learned | hist_gradient_boosting | 1488 | 23.2168 | 294 | 22.3794 |
| RB | fantasy_points_total | learned | ridge | 1488 | 27.1127 | 294 | 26.8907 |
| RB | games_active | baseline | age_position_adjusted | 1483 | 6.17816 | 294 | 6.81933 |
| RB | games_active | baseline | position_shrinkage | 1483 | 7.26169 | 294 | 7.93044 |
| RB | games_active | baseline | previous_season | 1483 | 7.18794 | 294 | 7.84813 |
| RB | games_active | baseline | weighted_components | 1483 | 6.17816 | 294 | 6.81933 |
| RB | games_active | baseline | weighted_history | 1483 | 6.17816 | 294 | 6.81933 |
| RB | games_active | learned | hist_gradient_boosting | 1483 | 3.0062 | 294 | 2.67123 |
| RB | games_active | learned | ridge | 1483 | 3.12784 | 294 | 2.99421 |
| TE | fantasy_points_per_game | baseline | age_position_adjusted | 565 | 1.76878 | 122 | 1.63116 |
| TE | fantasy_points_per_game | baseline | position_shrinkage | 565 | 1.89745 | 122 | 1.88063 |
| TE | fantasy_points_per_game | baseline | previous_season | 565 | 1.90567 | 122 | 1.90235 |
| TE | fantasy_points_per_game | baseline | weighted_components | 565 | 1.79923 | 122 | 1.6748 |
| TE | fantasy_points_per_game | baseline | weighted_history | 565 | 1.79923 | 122 | 1.6748 |
| TE | fantasy_points_per_game | learned | hist_gradient_boosting | 565 | 1.76897 | 122 | 1.5948 |
| TE | fantasy_points_per_game | learned | ridge | 565 | 1.94436 | 122 | 1.73482 |
| TE | fantasy_points_total | baseline | age_position_adjusted | 1160 | 23.6861 | 237 | 22.0405 |
| TE | fantasy_points_total | baseline | position_shrinkage | 1160 | 29.4239 | 237 | 27.6593 |
| TE | fantasy_points_total | baseline | previous_season | 1160 | 30.7262 | 237 | 31.3559 |
| TE | fantasy_points_total | baseline | weighted_components | 1160 | 24.575 | 237 | 23.0995 |
| TE | fantasy_points_total | baseline | weighted_history | 1160 | 24.575 | 237 | 23.0995 |
| TE | fantasy_points_total | learned | hist_gradient_boosting | 1160 | 16.3984 | 237 | 13.3161 |
| TE | fantasy_points_total | learned | ridge | 1160 | 19.3157 | 237 | 16.779 |
| TE | games_active | baseline | age_position_adjusted | 1158 | 6.28561 | 235 | 6.16474 |
| TE | games_active | baseline | position_shrinkage | 1158 | 7.26705 | 235 | 7.24898 |
| TE | games_active | baseline | previous_season | 1158 | 7.11719 | 235 | 7.37428 |
| TE | games_active | baseline | weighted_components | 1158 | 6.28561 | 235 | 6.16474 |
| TE | games_active | baseline | weighted_history | 1158 | 6.28561 | 235 | 6.16474 |
| TE | games_active | learned | hist_gradient_boosting | 1158 | 3.25215 | 235 | 2.5701 |
| TE | games_active | learned | ridge | 1158 | 3.64357 | 235 | 2.8742 |
| WR | fantasy_points_per_game | baseline | age_position_adjusted | 989 | 2.50952 | 198 | 2.25656 |
| WR | fantasy_points_per_game | baseline | position_shrinkage | 989 | 2.77451 | 198 | 2.43741 |
| WR | fantasy_points_per_game | baseline | previous_season | 989 | 2.76831 | 198 | 2.56141 |
| WR | fantasy_points_per_game | baseline | weighted_components | 989 | 2.63116 | 198 | 2.41075 |
| WR | fantasy_points_per_game | baseline | weighted_history | 989 | 2.63116 | 198 | 2.41075 |
| WR | fantasy_points_per_game | learned | hist_gradient_boosting | 989 | 2.36793 | 198 | 2.1201 |
| WR | fantasy_points_per_game | learned | ridge | 989 | 2.58558 | 198 | 2.13265 |
| WR | fantasy_points_total | baseline | age_position_adjusted | 2109 | 32.9322 | 434 | 32.0677 |
| WR | fantasy_points_total | baseline | position_shrinkage | 2109 | 43.5474 | 434 | 41.3842 |
| WR | fantasy_points_total | baseline | previous_season | 2109 | 45.1961 | 434 | 44.8118 |
| WR | fantasy_points_total | baseline | weighted_components | 2109 | 34.9655 | 434 | 34.1085 |
| WR | fantasy_points_total | baseline | weighted_history | 2109 | 34.9655 | 434 | 34.1085 |
| WR | fantasy_points_total | learned | hist_gradient_boosting | 2109 | 21.5237 | 434 | 19.031 |
| WR | fantasy_points_total | learned | ridge | 2109 | 27.9471 | 434 | 22.8137 |
| WR | games_active | baseline | age_position_adjusted | 2101 | 5.93888 | 433 | 6.40931 |
| WR | games_active | baseline | position_shrinkage | 2101 | 7.10354 | 433 | 7.39689 |
| WR | games_active | baseline | previous_season | 2101 | 7.04935 | 433 | 7.47264 |
| WR | games_active | baseline | weighted_components | 2101 | 5.93888 | 433 | 6.40931 |
| WR | games_active | baseline | weighted_history | 2101 | 5.93888 | 433 | 6.40931 |
| WR | games_active | learned | hist_gradient_boosting | 2101 | 2.91774 | 433 | 2.81191 |
| WR | games_active | learned | ridge | 2101 | 3.13872 | 433 | 2.94957 |

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
| QB | fantasy_points_per_game | hist_gradient_boosting | validation | 2023 | all | 70 | 0.742857 | 12.4906 | 1.07047 | 2.0683 | 1.04704 |
| QB | fantasy_points_per_game | hist_gradient_boosting | validation | 2023 | top | 27 | 0.814815 | 12.4906 | 1.34678 | 1.86408 | 0.864438 |
| QB | fantasy_points_per_game | hist_gradient_boosting | validation | 2023 | middle | 31 | 0.677419 | 12.4906 | 0.897714 | 2.22882 | 0.988946 |
| QB | fantasy_points_per_game | hist_gradient_boosting | validation | 2023 | lower | 12 | 0.75 | 12.4906 | 0.895069 | 2.11315 | 1.60797 |
| QB | fantasy_points_per_game | hist_gradient_boosting | validation | 2024 | all | 68 | 0.794118 | 12.4733 | 0.818613 | 2.08915 | 0.867735 |
| QB | fantasy_points_per_game | hist_gradient_boosting | validation | 2024 | top | 27 | 0.777778 | 12.4733 | 0.969422 | 1.99048 | 0.899755 |
| QB | fantasy_points_per_game | hist_gradient_boosting | validation | 2024 | middle | 37 | 0.783784 | 12.4733 | 0.728578 | 2.27308 | 0.871816 |
| QB | fantasy_points_per_game | hist_gradient_boosting | validation | 2024 | lower | 4 | 1 | 12.4733 | 0.633472 | 1.05392 | 0.613855 |
| QB | fantasy_points_per_game | ridge | test | 2025 | all | 66 | 0.712121 | 12.5663 | 0.881258 | 2.15619 | 0.942042 |
| QB | fantasy_points_per_game | ridge | test | 2025 | top | 30 | 0.766667 | 12.5663 | 1.01172 | 1.99937 | 0.886555 |
| QB | fantasy_points_per_game | ridge | test | 2025 | middle | 33 | 0.636364 | 12.5663 | 0.781463 | 2.44268 | 1.0252 |
| QB | fantasy_points_per_game | ridge | test | 2025 | lower | 3 | 1 | 12.5663 | 0.674437 | 0.573011 | 0.582195 |
| QB | fantasy_points_per_game | ridge | validation | 2020 | all | 68 | 0.764706 | 13.6896 | 1.22226 | 2.4142 | 1.13428 |
| QB | fantasy_points_per_game | ridge | validation | 2020 | top | 29 | 0.827586 | 13.6896 | 1.56318 | 2.33196 | 0.823451 |
| QB | fantasy_points_per_game | ridge | validation | 2020 | middle | 31 | 0.741935 | 13.6896 | 0.893377 | 2.25315 | 1.2068 |
| QB | fantasy_points_per_game | ridge | validation | 2020 | lower | 8 | 0.625 | 13.6896 | 1.26089 | 3.33639 | 1.97998 |
| QB | fantasy_points_per_game | ridge | validation | 2021 | all | 68 | 0.779412 | 14.0359 | 1.11051 | 2.31115 | 1.07204 |
| QB | fantasy_points_per_game | ridge | validation | 2021 | top | 27 | 0.851852 | 14.0359 | 1.05707 | 1.98721 | 1.04323 |
| QB | fantasy_points_per_game | ridge | validation | 2021 | middle | 35 | 0.742857 | 14.0359 | 1.1604 | 2.4076 | 0.921288 |
| QB | fantasy_points_per_game | ridge | validation | 2021 | lower | 6 | 0.666667 | 14.0359 | 1.06004 | 3.20623 | 2.08108 |
| QB | fantasy_points_per_game | ridge | validation | 2022 | all | 74 | 0.864865 | 14.2445 | 0.814008 | 1.97562 | 0.923074 |
| QB | fantasy_points_per_game | ridge | validation | 2022 | top | 30 | 0.9 | 14.2445 | 0.809224 | 1.8355 | 0.906527 |
| QB | fantasy_points_per_game | ridge | validation | 2022 | middle | 35 | 0.828571 | 14.2445 | 0.79208 | 2.11864 | 1.02365 |
| QB | fantasy_points_per_game | ridge | validation | 2022 | lower | 9 | 0.888889 | 14.2445 | 0.915228 | 1.88646 | 0.587093 |
| QB | fantasy_points_per_game | ridge | validation | 2023 | all | 70 | 0.785714 | 13.7887 | 0.942234 | 2.18231 | 1.02038 |
| QB | fantasy_points_per_game | ridge | validation | 2023 | top | 30 | 0.866667 | 13.7887 | 0.980251 | 1.89493 | 0.878422 |
| QB | fantasy_points_per_game | ridge | validation | 2023 | middle | 33 | 0.666667 | 13.7887 | 0.942172 | 2.67358 | 1.23877 |
| QB | fantasy_points_per_game | ridge | validation | 2023 | lower | 7 | 1 | 13.7887 | 0.779599 | 1.09797 | 0.599269 |
| QB | fantasy_points_per_game | ridge | validation | 2024 | all | 68 | 0.838235 | 13.8434 | 0.850113 | 1.93989 | 0.906174 |
| QB | fantasy_points_per_game | ridge | validation | 2024 | top | 29 | 0.896552 | 13.8434 | 0.983349 | 1.64566 | 0.755965 |
| QB | fantasy_points_per_game | ridge | validation | 2024 | middle | 38 | 0.789474 | 13.8434 | 0.739194 | 2.1426 | 1.03983 |
| QB | fantasy_points_per_game | ridge | validation | 2024 | lower | 1 | 1 | 13.8434 | 1.20118 | 2.76973 | 0.183159 |
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
| QB | fantasy_points_total | hist_gradient_boosting | validation | 2023 | all | 124 | 0.725806 | 135.105 | 14.9488 | 24.6145 | 16.7579 |
| QB | fantasy_points_total | hist_gradient_boosting | validation | 2023 | top | 31 | 0.193548 | 135.105 | 38.7813 | 54.9171 | 26.6565 |
| QB | fantasy_points_total | hist_gradient_boosting | validation | 2023 | middle | 62 | 0.887097 | 135.105 | 6.8399 | 16.734 | 13.1569 |
| QB | fantasy_points_total | hist_gradient_boosting | validation | 2023 | lower | 31 | 0.935484 | 135.105 | 7.33422 | 10.0727 | 14.0612 |
| QB | fantasy_points_total | hist_gradient_boosting | validation | 2024 | all | 125 | 0.808 | 145.48 | 10.7975 | 18.8632 | 13.8859 |
| QB | fantasy_points_total | hist_gradient_boosting | validation | 2024 | top | 31 | 0.516129 | 145.48 | 22.9174 | 41.3203 | 23.0836 |
| QB | fantasy_points_total | hist_gradient_boosting | validation | 2024 | middle | 63 | 0.857143 | 145.48 | 6.87723 | 15.9973 | 12.3039 |
| QB | fantasy_points_total | hist_gradient_boosting | validation | 2024 | lower | 31 | 1 | 145.48 | 6.64482 | 2.23042 | 7.90319 |
| QB | fantasy_points_total | ridge | test | 2025 | all | 124 | 0.822581 | 144.489 | 11.7091 | 21.697 | 12.6611 |
| QB | fantasy_points_total | ridge | test | 2025 | top | 31 | 0.516129 | 144.489 | 22.846 | 42.9374 | 24.0661 |
| QB | fantasy_points_total | ridge | test | 2025 | middle | 62 | 0.887097 | 144.489 | 7.37205 | 16.3376 | 10.6878 |
| QB | fantasy_points_total | ridge | test | 2025 | lower | 31 | 1 | 144.489 | 9.24632 | 11.1756 | 5.20257 |
| QB | fantasy_points_total | ridge | validation | 2020 | all | 119 | 0.798319 | 154.313 | 12.0047 | 23.2974 | 13.5262 |
| QB | fantasy_points_total | ridge | validation | 2020 | top | 30 | 0.5 | 154.313 | 23.6614 | 43.2152 | 20.3412 |
| QB | fantasy_points_total | ridge | validation | 2020 | middle | 59 | 0.847458 | 154.313 | 7.29004 | 18.8958 | 13.9839 |
| QB | fantasy_points_total | ridge | validation | 2020 | lower | 30 | 1 | 154.313 | 9.62024 | 12.0363 | 5.81111 |
| QB | fantasy_points_total | ridge | validation | 2021 | all | 125 | 0.816 | 154.77 | 14.2062 | 23.5269 | 12.9598 |
| QB | fantasy_points_total | ridge | validation | 2021 | top | 31 | 0.645161 | 154.77 | 33.205 | 41.7803 | 14.862 |
| QB | fantasy_points_total | ridge | validation | 2021 | middle | 63 | 0.825397 | 154.77 | 7.95559 | 22.4859 | 14.3358 |
| QB | fantasy_points_total | ridge | validation | 2021 | lower | 31 | 0.967742 | 154.77 | 7.91035 | 7.38917 | 8.26153 |
| QB | fantasy_points_total | ridge | validation | 2022 | all | 125 | 0.792 | 146.624 | 10.5795 | 21.1933 | 13.0011 |
| QB | fantasy_points_total | ridge | validation | 2022 | top | 31 | 0.580645 | 146.624 | 15.9901 | 34.8431 | 14.8497 |
| QB | fantasy_points_total | ridge | validation | 2022 | middle | 63 | 0.793651 | 146.624 | 9.29726 | 21.5734 | 15.0998 |
| QB | fantasy_points_total | ridge | validation | 2022 | lower | 31 | 1 | 146.624 | 7.77493 | 6.77082 | 6.88748 |
| QB | fantasy_points_total | ridge | validation | 2023 | all | 124 | 0.798387 | 149.561 | 12.1408 | 23.9257 | 14.1823 |
| QB | fantasy_points_total | ridge | validation | 2023 | top | 31 | 0.451613 | 149.561 | 24.4201 | 43.7412 | 21.3466 |
| QB | fantasy_points_total | ridge | validation | 2023 | middle | 62 | 0.870968 | 149.561 | 7.20862 | 18.5574 | 15.0763 |
| QB | fantasy_points_total | ridge | validation | 2023 | lower | 31 | 1 | 149.561 | 9.72602 | 14.8468 | 5.23007 |
| QB | fantasy_points_total | ridge | validation | 2024 | all | 125 | 0.8 | 141.819 | 11.51 | 22.0356 | 14.3276 |
| QB | fantasy_points_total | ridge | validation | 2024 | top | 31 | 0.548387 | 141.819 | 20.8208 | 38.315 | 22.1903 |
| QB | fantasy_points_total | ridge | validation | 2024 | middle | 63 | 0.857143 | 141.819 | 7.65547 | 16.6286 | 12.1297 |
| QB | fantasy_points_total | ridge | validation | 2024 | lower | 31 | 0.935484 | 141.819 | 10.0325 | 16.7446 | 10.9317 |
| QB | games_active | hist_gradient_boosting | test | 2025 | all | 124 | 0.782258 | 6.87582 | 0.467238 | 1.14786 | 0.675731 |
| QB | games_active | hist_gradient_boosting | test | 2025 | top | 31 | 0.516129 | 8.09301 | 1.12836 | 2.15757 | 0.858376 |
| QB | games_active | hist_gradient_boosting | test | 2025 | middle | 62 | 0.806452 | 7.36217 | 0.368683 | 1.20113 | 0.689591 |
| QB | games_active | hist_gradient_boosting | test | 2025 | lower | 31 | 1 | 4.68591 | 0.00322581 | 0.0316263 | 0.465365 |
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
| QB | games_active | hist_gradient_boosting | validation | 2023 | all | 124 | 0.709677 | 6.59624 | 0.711715 | 1.53719 | 0.905069 |
| QB | games_active | hist_gradient_boosting | validation | 2023 | top | 31 | 0.516129 | 7.46641 | 1.91812 | 2.6181 | 0.950044 |
| QB | games_active | hist_gradient_boosting | validation | 2023 | middle | 62 | 0.693548 | 7.163 | 0.428886 | 1.56679 | 1.10128 |
| QB | games_active | hist_gradient_boosting | validation | 2023 | lower | 31 | 0.935484 | 4.59256 | 0.0709677 | 0.397071 | 0.467678 |
| QB | games_active | hist_gradient_boosting | validation | 2024 | all | 125 | 0.784 | 6.83902 | 0.557692 | 1.28121 | 0.694771 |
| QB | games_active | hist_gradient_boosting | validation | 2024 | top | 31 | 0.580645 | 7.75847 | 1.36257 | 2.11881 | 0.626999 |
| QB | games_active | hist_gradient_boosting | validation | 2024 | middle | 63 | 0.793651 | 7.32792 | 0.415424 | 1.37935 | 0.838818 |
| QB | games_active | hist_gradient_boosting | validation | 2024 | lower | 31 | 0.967742 | 4.92603 | 0.0419355 | 0.244143 | 0.469803 |
| QB | games_active | ridge | test | 2025 | all | 124 | 0.814516 | 6.7385 | 0.473665 | 1.15069 | 0.616164 |
| QB | games_active | ridge | test | 2025 | top | 31 | 0.548387 | 8.23385 | 1.24491 | 2.24171 | 0.734827 |
| QB | games_active | ridge | test | 2025 | middle | 62 | 0.854839 | 7.36898 | 0.318424 | 1.14375 | 0.672258 |
| QB | games_active | ridge | test | 2025 | lower | 31 | 1 | 3.98218 | 0.0129032 | 0.0735431 | 0.385315 |
| QB | games_active | ridge | validation | 2020 | all | 119 | 0.815126 | 5.90393 | 0.403901 | 1.12271 | 0.628107 |
| QB | games_active | ridge | validation | 2020 | top | 30 | 0.7 | 8.82403 | 1.0096 | 1.8384 | 0.561475 |
| QB | games_active | ridge | validation | 2020 | middle | 59 | 0.779661 | 5.81576 | 0.289427 | 1.27035 | 0.832689 |
| QB | games_active | ridge | validation | 2020 | lower | 30 | 1 | 3.15726 | 0.0233333 | 0.116667 | 0.292393 |
| QB | games_active | ridge | validation | 2021 | all | 125 | 0.792 | 6.43038 | 0.509273 | 1.227 | 0.619549 |
| QB | games_active | ridge | validation | 2021 | top | 31 | 0.645161 | 7.83999 | 1.23898 | 1.8781 | 0.538178 |
| QB | games_active | ridge | validation | 2021 | middle | 63 | 0.793651 | 7.05523 | 0.380172 | 1.37913 | 0.744043 |
| QB | games_active | ridge | validation | 2021 | lower | 31 | 0.935484 | 3.75091 | 0.0419355 | 0.26675 | 0.447914 |
| QB | games_active | ridge | validation | 2022 | all | 125 | 0.808 | 6.57585 | 0.427427 | 1.2024 | 0.689181 |
| QB | games_active | ridge | validation | 2022 | top | 31 | 0.677419 | 7.97083 | 0.920013 | 1.62066 | 0.637034 |
| QB | games_active | ridge | validation | 2022 | middle | 63 | 0.793651 | 7.12338 | 0.376317 | 1.39362 | 0.81726 |
| QB | games_active | ridge | validation | 2022 | lower | 31 | 0.967742 | 4.06814 | 0.0387097 | 0.39552 | 0.481039 |
| QB | games_active | ridge | validation | 2023 | all | 124 | 0.782258 | 6.7534 | 0.500781 | 1.36555 | 0.810404 |
| QB | games_active | ridge | validation | 2023 | top | 31 | 0.516129 | 8.13646 | 1.22723 | 2.09195 | 0.723788 |
| QB | games_active | ridge | validation | 2023 | middle | 62 | 0.822581 | 7.32493 | 0.362142 | 1.51406 | 1.03847 |
| QB | games_active | ridge | validation | 2023 | lower | 31 | 0.967742 | 4.2273 | 0.0516129 | 0.342117 | 0.440893 |
| QB | games_active | ridge | validation | 2024 | all | 125 | 0.8 | 6.77558 | 0.504544 | 1.24123 | 0.721721 |
| QB | games_active | ridge | validation | 2024 | top | 31 | 0.645161 | 8.36852 | 0.994402 | 1.82495 | 0.632171 |
| QB | games_active | ridge | validation | 2024 | middle | 63 | 0.793651 | 7.32046 | 0.497485 | 1.49013 | 0.904474 |
| QB | games_active | ridge | validation | 2024 | lower | 31 | 0.967742 | 4.07533 | 0.0290323 | 0.151669 | 0.439871 |
| RB | fantasy_points_per_game | hist_gradient_boosting | test | 2025 | all | 128 | 0.867188 | 9.1777 | 0.552728 | 1.18427 | 0.675669 |
| RB | fantasy_points_per_game | hist_gradient_boosting | test | 2025 | top | 60 | 0.766667 | 9.1777 | 0.698189 | 1.49274 | 0.748792 |
| RB | fantasy_points_per_game | hist_gradient_boosting | test | 2025 | middle | 46 | 0.956522 | 9.1777 | 0.395803 | 1.04884 | 0.660276 |
| RB | fantasy_points_per_game | hist_gradient_boosting | test | 2025 | lower | 22 | 0.954545 | 9.1777 | 0.484131 | 0.626161 | 0.508428 |
| RB | fantasy_points_per_game | hist_gradient_boosting | validation | 2020 | all | 137 | 0.759124 | 9.54099 | 0.656028 | 1.40342 | 0.785169 |
| RB | fantasy_points_per_game | hist_gradient_boosting | validation | 2020 | top | 68 | 0.617647 | 9.54099 | 0.804998 | 1.82989 | 0.882687 |
| RB | fantasy_points_per_game | hist_gradient_boosting | validation | 2020 | middle | 48 | 0.854167 | 9.54099 | 0.534946 | 1.27564 | 0.770164 |
| RB | fantasy_points_per_game | hist_gradient_boosting | validation | 2020 | lower | 21 | 1 | 9.54099 | 0.450407 | 0.314564 | 0.503692 |
| RB | fantasy_points_per_game | hist_gradient_boosting | validation | 2021 | all | 149 | 0.838926 | 9.80881 | 0.575485 | 1.3251 | 0.669899 |
| RB | fantasy_points_per_game | hist_gradient_boosting | validation | 2021 | top | 65 | 0.769231 | 9.80881 | 0.642655 | 1.71719 | 0.719778 |
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
| RB | fantasy_points_per_game | ridge | test | 2025 | all | 128 | 0.84375 | 8.83232 | 0.509472 | 1.13599 | 0.65879 |
| RB | fantasy_points_per_game | ridge | test | 2025 | top | 65 | 0.723077 | 8.83232 | 0.637601 | 1.36614 | 0.728909 |
| RB | fantasy_points_per_game | ridge | test | 2025 | middle | 44 | 0.954545 | 8.83232 | 0.338018 | 1.0367 | 0.660457 |
| RB | fantasy_points_per_game | ridge | test | 2025 | lower | 19 | 1 | 8.83232 | 0.468185 | 0.578591 | 0.415047 |
| RB | fantasy_points_per_game | ridge | validation | 2020 | all | 137 | 0.832117 | 10.1591 | 0.661727 | 1.38469 | 0.722813 |
| RB | fantasy_points_per_game | ridge | validation | 2020 | top | 70 | 0.714286 | 10.1591 | 0.835216 | 1.84521 | 0.784529 |
| RB | fantasy_points_per_game | ridge | validation | 2020 | middle | 57 | 0.947368 | 10.1591 | 0.47189 | 0.954986 | 0.688475 |
| RB | fantasy_points_per_game | ridge | validation | 2020 | lower | 10 | 1 | 10.1591 | 0.52938 | 0.610382 | 0.486533 |
| RB | fantasy_points_per_game | ridge | validation | 2021 | all | 149 | 0.838926 | 9.82708 | 0.620523 | 1.40018 | 0.704819 |
| RB | fantasy_points_per_game | ridge | validation | 2021 | top | 69 | 0.782609 | 9.82708 | 0.628864 | 1.59285 | 0.737108 |
| RB | fantasy_points_per_game | ridge | validation | 2021 | middle | 63 | 0.888889 | 9.82708 | 0.589644 | 1.1745 | 0.662646 |
| RB | fantasy_points_per_game | ridge | validation | 2021 | lower | 17 | 0.882353 | 9.82708 | 0.701108 | 1.45451 | 0.730051 |
| RB | fantasy_points_per_game | ridge | validation | 2022 | all | 139 | 0.820144 | 9.21648 | 0.544179 | 1.2589 | 0.691647 |
| RB | fantasy_points_per_game | ridge | validation | 2022 | top | 68 | 0.691176 | 9.21648 | 0.680393 | 1.67157 | 0.760681 |
| RB | fantasy_points_per_game | ridge | validation | 2022 | middle | 55 | 0.927273 | 9.21648 | 0.395694 | 0.987096 | 0.677769 |
| RB | fantasy_points_per_game | ridge | validation | 2022 | lower | 16 | 1 | 9.21648 | 0.475686 | 0.439404 | 0.445962 |
| RB | fantasy_points_per_game | ridge | validation | 2023 | all | 134 | 0.828358 | 9.13574 | 0.591245 | 1.33193 | 0.75793 |
| RB | fantasy_points_per_game | ridge | validation | 2023 | top | 65 | 0.692308 | 9.13574 | 0.751812 | 1.75132 | 0.75382 |
| RB | fantasy_points_per_game | ridge | validation | 2023 | middle | 53 | 0.943396 | 9.13574 | 0.425071 | 1.06422 | 0.863727 |
| RB | fantasy_points_per_game | ridge | validation | 2023 | lower | 16 | 1 | 9.13574 | 0.489398 | 0.515003 | 0.424177 |
| RB | fantasy_points_per_game | ridge | validation | 2024 | all | 127 | 0.818898 | 8.97516 | 0.556706 | 1.28623 | 0.69714 |
| RB | fantasy_points_per_game | ridge | validation | 2024 | top | 66 | 0.69697 | 8.97516 | 0.639986 | 1.65061 | 0.800771 |
| RB | fantasy_points_per_game | ridge | validation | 2024 | middle | 48 | 0.9375 | 8.97516 | 0.448617 | 0.939973 | 0.644732 |
| RB | fantasy_points_per_game | ridge | validation | 2024 | lower | 13 | 1 | 8.97516 | 0.532994 | 0.714774 | 0.364523 |
| RB | fantasy_points_total | hist_gradient_boosting | test | 2025 | all | 294 | 0.79932 | 73.932 | 7.43445 | 11.1897 | 9.68371 |
| RB | fantasy_points_total | hist_gradient_boosting | test | 2025 | top | 74 | 0.310811 | 73.932 | 20.0009 | 33.1781 | 22.9331 |
| RB | fantasy_points_total | hist_gradient_boosting | test | 2025 | middle | 146 | 0.945205 | 73.932 | 3.11223 | 5.11797 | 5.85026 |
| RB | fantasy_points_total | hist_gradient_boosting | test | 2025 | lower | 74 | 1 | 73.932 | 3.39562 | 1.18069 | 3.99758 |
| RB | fantasy_points_total | hist_gradient_boosting | validation | 2020 | all | 302 | 0.81457 | 89.2099 | 9.56739 | 12.915 | 9.29301 |
| RB | fantasy_points_total | hist_gradient_boosting | validation | 2020 | top | 76 | 0.434211 | 89.2099 | 24.3293 | 32.5043 | 16.0413 |
| RB | fantasy_points_total | hist_gradient_boosting | validation | 2020 | middle | 150 | 0.913333 | 89.2099 | 4.68434 | 8.06247 | 8.31353 |
| RB | fantasy_points_total | hist_gradient_boosting | validation | 2020 | lower | 76 | 1 | 89.2099 | 4.44307 | 2.90313 | 4.47791 |
| RB | fantasy_points_total | hist_gradient_boosting | validation | 2021 | all | 302 | 0.811258 | 87.55 | 6.46311 | 11.3991 | 9.05452 |
| RB | fantasy_points_total | hist_gradient_boosting | validation | 2021 | top | 76 | 0.407895 | 87.55 | 12.4648 | 27.054 | 16.2033 |
| RB | fantasy_points_total | hist_gradient_boosting | validation | 2021 | middle | 150 | 0.92 | 87.55 | 4.50481 | 8.31059 | 7.77633 |
| RB | fantasy_points_total | hist_gradient_boosting | validation | 2021 | lower | 76 | 1 | 87.55 | 4.32648 | 1.83984 | 4.42852 |
| RB | fantasy_points_total | hist_gradient_boosting | validation | 2022 | all | 297 | 0.818182 | 81.9894 | 6.51171 | 11.5469 | 9.92085 |
| RB | fantasy_points_total | hist_gradient_boosting | validation | 2022 | top | 74 | 0.459459 | 81.9894 | 14.9377 | 29.0282 | 20.5971 |
| RB | fantasy_points_total | hist_gradient_boosting | validation | 2022 | middle | 149 | 0.90604 | 81.9894 | 3.684 | 8.25659 | 7.35072 |
| RB | fantasy_points_total | hist_gradient_boosting | validation | 2022 | lower | 74 | 1 | 81.9894 | 3.77937 | 0.690606 | 4.41957 |
| RB | fantasy_points_total | hist_gradient_boosting | validation | 2023 | all | 292 | 0.794521 | 76.5107 | 6.80062 | 11.5818 | 10.1497 |
| RB | fantasy_points_total | hist_gradient_boosting | validation | 2023 | top | 73 | 0.30137 | 76.5107 | 16.7403 | 31.274 | 22.012 |
| RB | fantasy_points_total | hist_gradient_boosting | validation | 2023 | middle | 146 | 0.938356 | 76.5107 | 3.46266 | 7.24811 | 7.23632 |
| RB | fantasy_points_total | hist_gradient_boosting | validation | 2023 | lower | 73 | 1 | 76.5107 | 3.53688 | 0.556938 | 4.11419 |
| RB | fantasy_points_total | hist_gradient_boosting | validation | 2024 | all | 295 | 0.833898 | 80.1631 | 5.7773 | 10.5733 | 9.84861 |
| RB | fantasy_points_total | hist_gradient_boosting | validation | 2024 | top | 74 | 0.432432 | 80.1631 | 12.2009 | 29.4941 | 23.1307 |
| RB | fantasy_points_total | hist_gradient_boosting | validation | 2024 | middle | 147 | 0.952381 | 80.1631 | 3.57784 | 6.05047 | 5.95887 |
| RB | fantasy_points_total | hist_gradient_boosting | validation | 2024 | lower | 74 | 1 | 80.1631 | 3.72292 | 0.637027 | 4.29339 |
| RB | fantasy_points_total | ridge | test | 2025 | all | 294 | 0.768707 | 77.4635 | 7.30197 | 13.4453 | 9.10354 |
| RB | fantasy_points_total | ridge | test | 2025 | top | 74 | 0.297297 | 77.4635 | 18.4187 | 31.9645 | 19.9581 |
| RB | fantasy_points_total | ridge | test | 2025 | middle | 146 | 0.89726 | 77.4635 | 3.1157 | 9.00688 | 6.52956 |
| RB | fantasy_points_total | ridge | test | 2025 | lower | 74 | 0.986486 | 77.4635 | 4.44464 | 3.68312 | 3.32734 |
| RB | fantasy_points_total | ridge | validation | 2020 | all | 302 | 0.824503 | 93.2914 | 8.65549 | 13.6808 | 8.29478 |
| RB | fantasy_points_total | ridge | validation | 2020 | top | 76 | 0.434211 | 93.2914 | 18.4325 | 29.9868 | 15.3762 |
| RB | fantasy_points_total | ridge | validation | 2020 | middle | 150 | 0.946667 | 93.2914 | 4.74946 | 8.00586 | 7.38297 |
| RB | fantasy_points_total | ridge | validation | 2020 | lower | 76 | 0.973684 | 93.2914 | 6.5878 | 8.57534 | 3.01298 |
| RB | fantasy_points_total | ridge | validation | 2021 | all | 302 | 0.817881 | 90.9516 | 6.93479 | 14.2259 | 9.40375 |
| RB | fantasy_points_total | ridge | validation | 2021 | top | 76 | 0.486842 | 90.9516 | 11.6113 | 28.4653 | 18.3961 |
| RB | fantasy_points_total | ridge | validation | 2021 | middle | 150 | 0.913333 | 90.9516 | 4.74199 | 9.46203 | 7.26044 |
| RB | fantasy_points_total | ridge | validation | 2021 | lower | 76 | 0.960526 | 90.9516 | 6.5862 | 9.38893 | 4.64167 |
| RB | fantasy_points_total | ridge | validation | 2022 | all | 297 | 0.821549 | 85.4935 | 6.79201 | 13.6648 | 9.58912 |
| RB | fantasy_points_total | ridge | validation | 2022 | top | 74 | 0.432432 | 85.4935 | 14.2126 | 30.1187 | 19.8899 |
| RB | fantasy_points_total | ridge | validation | 2022 | middle | 149 | 0.926174 | 85.4935 | 3.82961 | 9.74999 | 7.63993 |
| RB | fantasy_points_total | ridge | validation | 2022 | lower | 74 | 1 | 85.4935 | 5.33631 | 5.09324 | 3.21305 |
| RB | fantasy_points_total | ridge | validation | 2023 | all | 292 | 0.811644 | 82.9142 | 6.81497 | 13.3355 | 9.84281 |
| RB | fantasy_points_total | ridge | validation | 2023 | top | 73 | 0.328767 | 82.9142 | 15.6964 | 31.2675 | 20.9774 |
| RB | fantasy_points_total | ridge | validation | 2023 | middle | 146 | 0.958904 | 82.9142 | 3.37355 | 9.38278 | 7.45944 |
| RB | fantasy_points_total | ridge | validation | 2023 | lower | 73 | 1 | 82.9142 | 4.81639 | 3.30873 | 3.47502 |
| RB | fantasy_points_total | ridge | validation | 2024 | all | 295 | 0.80678 | 80.4707 | 6.45691 | 12.8529 | 9.91934 |
| RB | fantasy_points_total | ridge | validation | 2024 | top | 74 | 0.364865 | 80.4707 | 13.0468 | 30.823 | 23.6838 |
| RB | fantasy_points_total | ridge | validation | 2024 | middle | 147 | 0.952381 | 80.4707 | 3.68742 | 6.9167 | 6.14712 |
| RB | fantasy_points_total | ridge | validation | 2024 | lower | 74 | 0.959459 | 80.4707 | 5.36863 | 6.67485 | 3.64838 |
| RB | games_active | hist_gradient_boosting | test | 2025 | all | 294 | 0.833333 | 8.30646 | 0.563115 | 1.33561 | 0.793022 |
| RB | games_active | hist_gradient_boosting | test | 2025 | top | 74 | 0.756757 | 10.4904 | 1.37711 | 2.19284 | 0.545955 |
| RB | games_active | hist_gradient_boosting | test | 2025 | middle | 146 | 0.787671 | 8.48705 | 0.4339 | 1.56779 | 1.02999 |
| RB | games_active | hist_gradient_boosting | test | 2025 | lower | 74 | 1 | 5.7662 | 0.00405405 | 0.0203073 | 0.572566 |
| RB | games_active | hist_gradient_boosting | validation | 2020 | all | 301 | 0.780731 | 8.78301 | 0.57875 | 1.45567 | 0.878734 |
| RB | games_active | hist_gradient_boosting | validation | 2020 | top | 76 | 0.710526 | 11.4897 | 1.27264 | 2.24953 | 0.63295 |
| RB | games_active | hist_gradient_boosting | validation | 2020 | middle | 150 | 0.706667 | 8.91497 | 0.514553 | 1.77128 | 1.15582 |
| RB | games_active | hist_gradient_boosting | validation | 2020 | lower | 75 | 1 | 5.77628 | 0.004 | 0.02 | 0.573628 |
| RB | games_active | hist_gradient_boosting | validation | 2021 | all | 301 | 0.827243 | 9.41783 | 0.529271 | 1.48308 | 0.862792 |
| RB | games_active | hist_gradient_boosting | validation | 2021 | top | 76 | 0.776316 | 11.6905 | 1.08623 | 2.21391 | 0.608476 |
| RB | games_active | hist_gradient_boosting | validation | 2021 | middle | 150 | 0.78 | 9.8544 | 0.493714 | 1.76433 | 1.03782 |
| RB | games_active | hist_gradient_boosting | validation | 2021 | lower | 75 | 0.973333 | 6.24177 | 0.036 | 0.18 | 0.770445 |
| RB | games_active | hist_gradient_boosting | validation | 2022 | all | 296 | 0.793919 | 9.35368 | 0.642891 | 1.58534 | 0.811197 |
| RB | games_active | hist_gradient_boosting | validation | 2022 | top | 74 | 0.72973 | 11.1258 | 1.29768 | 2.30823 | 0.534767 |
| RB | games_active | hist_gradient_boosting | validation | 2022 | middle | 148 | 0.722973 | 9.94059 | 0.636939 | 2.01053 | 1.03462 |
| RB | games_active | hist_gradient_boosting | validation | 2022 | lower | 74 | 1 | 6.40775 | 0 | 0.0120637 | 0.640775 |
| RB | games_active | hist_gradient_boosting | validation | 2023 | all | 291 | 0.800687 | 9.03918 | 0.656282 | 1.55492 | 0.834719 |
| RB | games_active | hist_gradient_boosting | validation | 2023 | top | 73 | 0.767123 | 10.9615 | 1.44347 | 2.34189 | 0.529851 |
| RB | games_active | hist_gradient_boosting | validation | 2023 | middle | 145 | 0.724138 | 9.5004 | 0.575206 | 1.85959 | 1.04517 |
| RB | games_active | hist_gradient_boosting | validation | 2023 | lower | 73 | 0.986301 | 6.20076 | 0.030137 | 0.162805 | 0.721576 |
| RB | games_active | hist_gradient_boosting | validation | 2024 | all | 294 | 0.833333 | 8.73892 | 0.552081 | 1.43807 | 0.900013 |
| RB | games_active | hist_gradient_boosting | validation | 2024 | top | 74 | 0.851351 | 11.0445 | 1.1638 | 1.95334 | 0.45229 |
| RB | games_active | hist_gradient_boosting | validation | 2024 | middle | 147 | 0.741497 | 8.93744 | 0.511499 | 1.85593 | 1.28109 |
| RB | games_active | hist_gradient_boosting | validation | 2024 | lower | 73 | 1 | 6.00195 | 0.0136986 | 0.0742861 | 0.586496 |
| RB | games_active | ridge | test | 2025 | all | 294 | 0.778912 | 8.46807 | 0.600221 | 1.49711 | 0.806081 |
| RB | games_active | ridge | test | 2025 | top | 74 | 0.675676 | 11.1032 | 1.36664 | 2.42356 | 0.554807 |
| RB | games_active | ridge | test | 2025 | middle | 146 | 0.732877 | 8.70415 | 0.501602 | 1.71113 | 1.04116 |
| RB | games_active | ridge | test | 2025 | lower | 74 | 0.972973 | 5.36716 | 0.0283784 | 0.148385 | 0.59355 |
| RB | games_active | ridge | validation | 2020 | all | 301 | 0.810631 | 8.75156 | 0.520661 | 1.42286 | 0.80178 |
| RB | games_active | ridge | validation | 2020 | top | 76 | 0.763158 | 12.2867 | 1.13204 | 2.25321 | 0.538291 |
| RB | games_active | ridge | validation | 2020 | middle | 150 | 0.746667 | 8.56416 | 0.45389 | 1.62691 | 1.01252 |
| RB | games_active | ridge | validation | 2020 | lower | 75 | 0.986667 | 5.54406 | 0.0346667 | 0.173333 | 0.647307 |
| RB | games_active | ridge | validation | 2021 | all | 301 | 0.817276 | 9.5621 | 0.606865 | 1.61965 | 0.821088 |
| RB | games_active | ridge | validation | 2021 | top | 76 | 0.776316 | 11.5833 | 1.31621 | 2.25062 | 0.594315 |
| RB | games_active | ridge | validation | 2021 | middle | 149 | 0.751678 | 10.3583 | 0.543184 | 1.99512 | 0.990933 |
| RB | games_active | ridge | validation | 2021 | lower | 76 | 0.986842 | 5.9799 | 0.0223684 | 0.252562 | 0.714877 |
| RB | games_active | ridge | validation | 2022 | all | 296 | 0.790541 | 9.62548 | 0.577745 | 1.69012 | 0.805416 |
| RB | games_active | ridge | validation | 2022 | top | 74 | 0.837838 | 11.3342 | 0.996678 | 1.90554 | 0.453089 |
| RB | games_active | ridge | validation | 2022 | middle | 148 | 0.662162 | 10.5324 | 0.655799 | 2.32241 | 1.08049 |
| RB | games_active | ridge | validation | 2022 | lower | 74 | 1 | 6.10294 | 0.0027027 | 0.210123 | 0.607591 |
| RB | games_active | ridge | validation | 2023 | all | 291 | 0.804124 | 9.10987 | 0.613486 | 1.62483 | 0.82175 |
| RB | games_active | ridge | validation | 2023 | top | 73 | 0.739726 | 11.4742 | 1.37017 | 2.37377 | 0.554278 |
| RB | games_active | ridge | validation | 2023 | middle | 145 | 0.737931 | 9.73101 | 0.539323 | 2.02855 | 1.09469 |
| RB | games_active | ridge | validation | 2023 | lower | 73 | 1 | 5.51179 | 0.00410959 | 0.0739715 | 0.54707 |
| RB | games_active | ridge | validation | 2024 | all | 294 | 0.823129 | 8.61217 | 0.531595 | 1.46393 | 0.874773 |
| RB | games_active | ridge | validation | 2024 | top | 74 | 0.824324 | 11.3588 | 1.1091 | 2.12131 | 0.421048 |
| RB | games_active | ridge | validation | 2024 | middle | 146 | 0.739726 | 8.98274 | 0.501479 | 1.83848 | 1.28882 |
| RB | games_active | ridge | validation | 2024 | lower | 74 | 0.986486 | 5.13444 | 0.0135135 | 0.0675676 | 0.511591 |
| TE | fantasy_points_per_game | hist_gradient_boosting | test | 2025 | all | 122 | 0.762295 | 5.06232 | 0.388803 | 0.7974 | 0.484414 |
| TE | fantasy_points_per_game | hist_gradient_boosting | test | 2025 | top | 56 | 0.553571 | 5.06232 | 0.514553 | 1.19108 | 0.590951 |
| TE | fantasy_points_per_game | hist_gradient_boosting | test | 2025 | middle | 55 | 0.945455 | 5.06232 | 0.272857 | 0.43843 | 0.331609 |
| TE | fantasy_points_per_game | hist_gradient_boosting | test | 2025 | lower | 11 | 0.909091 | 5.06232 | 0.32835 | 0.588074 | 0.706074 |
| TE | fantasy_points_per_game | hist_gradient_boosting | validation | 2020 | all | 111 | 0.72973 | 6.32692 | 0.497133 | 1.06655 | 0.582366 |
| TE | fantasy_points_per_game | hist_gradient_boosting | validation | 2020 | top | 44 | 0.545455 | 6.32692 | 0.730953 | 1.39326 | 0.652409 |
| TE | fantasy_points_per_game | hist_gradient_boosting | validation | 2020 | middle | 55 | 0.836364 | 6.32692 | 0.35481 | 0.944218 | 0.570512 |
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
| TE | fantasy_points_per_game | ridge | test | 2025 | all | 122 | 0.770492 | 4.99273 | 0.413328 | 0.867409 | 0.545293 |
| TE | fantasy_points_per_game | ridge | test | 2025 | top | 55 | 0.563636 | 4.99273 | 0.551769 | 1.24035 | 0.743034 |
| TE | fantasy_points_per_game | ridge | test | 2025 | middle | 52 | 0.942308 | 4.99273 | 0.284333 | 0.533297 | 0.445164 |
| TE | fantasy_points_per_game | ridge | test | 2025 | lower | 15 | 0.933333 | 4.99273 | 0.352898 | 0.658206 | 0.167358 |
| TE | fantasy_points_per_game | ridge | validation | 2020 | all | 111 | 0.738739 | 6.34553 | 0.547448 | 1.3472 | 0.665496 |
| TE | fantasy_points_per_game | ridge | validation | 2020 | top | 46 | 0.652174 | 6.34553 | 0.626447 | 1.50282 | 0.740855 |
| TE | fantasy_points_per_game | ridge | validation | 2020 | middle | 52 | 0.769231 | 6.34553 | 0.493654 | 1.27605 | 0.718623 |
| TE | fantasy_points_per_game | ridge | validation | 2020 | lower | 13 | 0.923077 | 6.34553 | 0.483092 | 1.0811 | 0.186333 |
| TE | fantasy_points_per_game | ridge | validation | 2021 | all | 118 | 0.805085 | 6.60866 | 0.417398 | 0.910022 | 0.516554 |
| TE | fantasy_points_per_game | ridge | validation | 2021 | top | 52 | 0.653846 | 6.60866 | 0.593151 | 1.23207 | 0.60712 |
| TE | fantasy_points_per_game | ridge | validation | 2021 | middle | 50 | 0.9 | 6.60866 | 0.272692 | 0.78027 | 0.471676 |
| TE | fantasy_points_per_game | ridge | validation | 2021 | lower | 16 | 1 | 6.60866 | 0.298406 | 0.26884 | 0.362461 |
| TE | fantasy_points_per_game | ridge | validation | 2022 | all | 110 | 0.872727 | 6.60083 | 0.487476 | 0.948445 | 0.470056 |
| TE | fantasy_points_per_game | ridge | validation | 2022 | top | 51 | 0.745098 | 6.60083 | 0.768793 | 1.24902 | 0.498865 |
| TE | fantasy_points_per_game | ridge | validation | 2022 | middle | 44 | 0.977273 | 6.60083 | 0.215347 | 0.75491 | 0.484123 |
| TE | fantasy_points_per_game | ridge | validation | 2022 | lower | 15 | 1 | 6.60083 | 0.329243 | 0.49418 | 0.33084 |
| TE | fantasy_points_per_game | ridge | validation | 2023 | all | 112 | 0.830357 | 6.18986 | 0.360362 | 0.848436 | 0.486539 |
| TE | fantasy_points_per_game | ridge | validation | 2023 | top | 52 | 0.692308 | 6.18986 | 0.497167 | 1.15756 | 0.54314 |
| TE | fantasy_points_per_game | ridge | validation | 2023 | middle | 49 | 0.959184 | 6.18986 | 0.208674 | 0.584915 | 0.42201 |
| TE | fantasy_points_per_game | ridge | validation | 2023 | lower | 11 | 0.909091 | 6.18986 | 0.389348 | 0.561003 | 0.506419 |
| TE | fantasy_points_per_game | ridge | validation | 2024 | all | 114 | 0.815789 | 5.22032 | 0.374418 | 0.815848 | 0.463791 |
| TE | fantasy_points_per_game | ridge | validation | 2024 | top | 52 | 0.673077 | 5.22032 | 0.474524 | 1.20901 | 0.704113 |
| TE | fantasy_points_per_game | ridge | validation | 2024 | middle | 52 | 0.923077 | 5.22032 | 0.2804 | 0.481672 | 0.278182 |
| TE | fantasy_points_per_game | ridge | validation | 2024 | lower | 10 | 1 | 5.22032 | 0.342753 | 0.509098 | 0.17928 |
| TE | fantasy_points_total | hist_gradient_boosting | test | 2025 | all | 237 | 0.843882 | 54.488 | 4.2346 | 6.65805 | 5.99703 |
| TE | fantasy_points_total | hist_gradient_boosting | test | 2025 | top | 59 | 0.474576 | 54.488 | 8.84035 | 18.2746 | 12.9314 |
| TE | fantasy_points_total | hist_gradient_boosting | test | 2025 | middle | 119 | 0.94958 | 54.488 | 2.74013 | 3.98432 | 4.14127 |
| TE | fantasy_points_total | hist_gradient_boosting | test | 2025 | lower | 59 | 1 | 54.488 | 2.64313 | 0.434212 | 2.80567 |
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
| TE | fantasy_points_total | hist_gradient_boosting | validation | 2024 | all | 237 | 0.835443 | 58.3734 | 4.54615 | 7.53994 | 6.59096 |
| TE | fantasy_points_total | hist_gradient_boosting | validation | 2024 | top | 59 | 0.457627 | 58.3734 | 10.1528 | 21.0438 | 14.8596 |
| TE | fantasy_points_total | hist_gradient_boosting | validation | 2024 | middle | 119 | 0.941176 | 58.3734 | 2.69454 | 4.26434 | 4.19087 |
| TE | fantasy_points_total | hist_gradient_boosting | validation | 2024 | lower | 59 | 1 | 58.3734 | 2.67414 | 0.642806 | 3.1632 |
| TE | fantasy_points_total | ridge | test | 2025 | all | 237 | 0.810127 | 52.0147 | 4.65346 | 8.38948 | 6.00644 |
| TE | fantasy_points_total | ridge | test | 2025 | top | 59 | 0.423729 | 52.0147 | 10.5489 | 20.1384 | 13.9936 |
| TE | fantasy_points_total | ridge | test | 2025 | middle | 119 | 0.907563 | 52.0147 | 2.43805 | 5.14338 | 4.04515 |
| TE | fantasy_points_total | ridge | test | 2025 | lower | 59 | 1 | 52.0147 | 3.22637 | 3.18784 | 1.97509 |
| TE | fantasy_points_total | ridge | validation | 2020 | all | 225 | 0.822222 | 69.0083 | 5.64762 | 11.6719 | 8.27083 |
| TE | fantasy_points_total | ridge | validation | 2020 | top | 56 | 0.607143 | 69.0083 | 7.33344 | 19.2167 | 14.8093 |
| TE | fantasy_points_total | ridge | validation | 2020 | middle | 113 | 0.867257 | 69.0083 | 4.93827 | 9.19563 | 8.27853 |
| TE | fantasy_points_total | ridge | validation | 2020 | lower | 56 | 0.946429 | 69.0083 | 5.39315 | 9.12373 | 1.7168 |
| TE | fantasy_points_total | ridge | validation | 2021 | all | 229 | 0.829694 | 71.4764 | 4.80733 | 9.67711 | 6.77141 |
| TE | fantasy_points_total | ridge | validation | 2021 | top | 57 | 0.45614 | 71.4764 | 7.46653 | 21.5489 | 14.2662 |
| TE | fantasy_points_total | ridge | validation | 2021 | middle | 115 | 0.930435 | 71.4764 | 3.64843 | 5.86629 | 5.09375 |
| TE | fantasy_points_total | ridge | validation | 2021 | lower | 57 | 1 | 71.4764 | 4.48625 | 5.49376 | 2.66139 |
| TE | fantasy_points_total | ridge | validation | 2022 | all | 234 | 0.850427 | 65.1289 | 6.06095 | 9.21339 | 5.75727 |
| TE | fantasy_points_total | ridge | validation | 2022 | top | 59 | 0.542373 | 65.1289 | 16.0254 | 21.5419 | 9.99617 |
| TE | fantasy_points_total | ridge | validation | 2022 | middle | 116 | 0.931034 | 65.1289 | 2.36954 | 6.14829 | 4.92297 |
| TE | fantasy_points_total | ridge | validation | 2022 | lower | 59 | 1 | 65.1289 | 3.35422 | 2.91113 | 3.15867 |
| TE | fantasy_points_total | ridge | validation | 2023 | all | 235 | 0.804255 | 57.4323 | 4.39574 | 8.75515 | 5.95472 |
| TE | fantasy_points_total | ridge | validation | 2023 | top | 59 | 0.389831 | 57.4323 | 8.96629 | 19.3875 | 13.4319 |
| TE | fantasy_points_total | ridge | validation | 2023 | middle | 117 | 0.91453 | 57.4323 | 2.54078 | 5.46367 | 4.05762 |
| TE | fantasy_points_total | ridge | validation | 2023 | lower | 59 | 1 | 57.4323 | 3.50366 | 4.64996 | 2.23957 |
| TE | fantasy_points_total | ridge | validation | 2024 | all | 237 | 0.805907 | 54.5876 | 5.01272 | 9.06107 | 6.66531 |
| TE | fantasy_points_total | ridge | validation | 2024 | top | 59 | 0.423729 | 54.5876 | 11.7814 | 21.9279 | 16.3534 |
| TE | fantasy_points_total | ridge | validation | 2024 | middle | 119 | 0.915966 | 54.5876 | 2.39847 | 5.08903 | 3.99517 |
| TE | fantasy_points_total | ridge | validation | 2024 | lower | 59 | 0.966102 | 54.5876 | 3.51683 | 4.2057 | 2.36271 |
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
| TE | games_active | ridge | test | 2025 | all | 235 | 0.859574 | 8.99116 | 0.529948 | 1.4371 | 0.740549 |
| TE | games_active | ridge | test | 2025 | top | 59 | 0.915254 | 10.2514 | 0.888389 | 1.62008 | 0.38784 |
| TE | games_active | ridge | test | 2025 | middle | 117 | 0.760684 | 9.99074 | 0.61216 | 2.01181 | 1.00623 |
| TE | games_active | ridge | test | 2025 | lower | 59 | 1 | 5.74868 | 0.00847458 | 0.114452 | 0.566393 |
| TE | games_active | ridge | validation | 2020 | all | 224 | 0.794643 | 11.9632 | 0.798435 | 2.51743 | 0.976259 |
| TE | games_active | ridge | validation | 2020 | top | 56 | 0.875 | 8.67661 | 1.05697 | 1.63667 | 0.455357 |
| TE | games_active | ridge | validation | 2020 | middle | 113 | 0.654867 | 13.6537 | 1.03946 | 3.11491 | 1.15294 |
| TE | games_active | ridge | validation | 2020 | lower | 55 | 1 | 11.8364 | 0.04 | 2.18664 | 1.14364 |
| TE | games_active | ridge | validation | 2021 | all | 229 | 0.812227 | 10.0806 | 0.59409 | 1.75106 | 0.919002 |
| TE | games_active | ridge | validation | 2021 | top | 57 | 0.824561 | 13.5657 | 1.19595 | 2.38591 | 0.505587 |
| TE | games_active | ridge | validation | 2021 | middle | 115 | 0.721739 | 10.4422 | 0.579806 | 2.25215 | 1.19476 |
| TE | games_active | ridge | validation | 2021 | lower | 57 | 0.982456 | 5.86597 | 0.0210526 | 0.105263 | 0.77607 |
| TE | games_active | ridge | validation | 2022 | all | 234 | 0.799145 | 9.90405 | 0.578261 | 1.68364 | 0.804137 |
| TE | games_active | ridge | validation | 2022 | top | 59 | 0.847458 | 12.7314 | 1.13685 | 2.16552 | 0.432703 |
| TE | games_active | ridge | validation | 2022 | middle | 116 | 0.672414 | 10.7722 | 0.588266 | 2.29488 | 1.12894 |
| TE | games_active | ridge | validation | 2022 | lower | 59 | 1 | 5.36976 | 0 | 0 | 0.536976 |
| TE | games_active | ridge | validation | 2023 | all | 235 | 0.834043 | 9.34828 | 0.567597 | 1.51469 | 0.752864 |
| TE | games_active | ridge | validation | 2023 | top | 59 | 0.813559 | 12.5763 | 1.23494 | 2.2181 | 0.427452 |
| TE | games_active | ridge | validation | 2023 | middle | 117 | 0.760684 | 9.69851 | 0.506188 | 1.86824 | 1.03411 |
| TE | games_active | ridge | validation | 2023 | lower | 59 | 1 | 5.42578 | 0.0220339 | 0.110169 | 0.520544 |
| TE | games_active | ridge | validation | 2024 | all | 236 | 0.800847 | 8.9568 | 0.674632 | 1.67291 | 0.838335 |
| TE | games_active | ridge | validation | 2024 | top | 59 | 0.881356 | 9.93995 | 1.18021 | 2.00644 | 0.396906 |
| TE | games_active | ridge | validation | 2024 | middle | 118 | 0.669492 | 9.86875 | 0.753226 | 2.24236 | 1.17412 |
| TE | games_active | ridge | validation | 2024 | lower | 59 | 0.983051 | 6.14973 | 0.0118644 | 0.200491 | 0.608197 |
| WR | fantasy_points_per_game | hist_gradient_boosting | test | 2025 | all | 198 | 0.838384 | 7.76528 | 0.488168 | 1.06005 | 0.510608 |
| WR | fantasy_points_per_game | hist_gradient_boosting | test | 2025 | top | 91 | 0.681319 | 7.76528 | 0.586474 | 1.44215 | 0.662599 |
| WR | fantasy_points_per_game | hist_gradient_boosting | test | 2025 | middle | 70 | 0.957143 | 7.76528 | 0.39193 | 0.805386 | 0.398934 |
| WR | fantasy_points_per_game | hist_gradient_boosting | test | 2025 | lower | 37 | 1 | 7.76528 | 0.428463 | 0.602084 | 0.348065 |
| WR | fantasy_points_per_game | hist_gradient_boosting | validation | 2020 | all | 192 | 0.838542 | 9.10196 | 0.530376 | 1.23484 | 0.614721 |
| WR | fantasy_points_per_game | hist_gradient_boosting | validation | 2020 | top | 92 | 0.76087 | 9.10196 | 0.633671 | 1.4787 | 0.654532 |
| WR | fantasy_points_per_game | hist_gradient_boosting | validation | 2020 | middle | 70 | 0.885714 | 9.10196 | 0.4183 | 1.10485 | 0.605895 |
| WR | fantasy_points_per_game | hist_gradient_boosting | validation | 2020 | lower | 30 | 0.966667 | 9.10196 | 0.475118 | 0.790317 | 0.51323 |
| WR | fantasy_points_per_game | hist_gradient_boosting | validation | 2021 | all | 212 | 0.834906 | 8.666 | 0.562805 | 1.1963 | 0.658342 |
| WR | fantasy_points_per_game | hist_gradient_boosting | validation | 2021 | top | 89 | 0.764045 | 8.666 | 0.762979 | 1.43486 | 0.736572 |
| WR | fantasy_points_per_game | hist_gradient_boosting | validation | 2021 | middle | 92 | 0.880435 | 8.666 | 0.391992 | 1.05964 | 0.615938 |
| WR | fantasy_points_per_game | hist_gradient_boosting | validation | 2021 | lower | 31 | 0.903226 | 8.666 | 0.495044 | 0.916999 | 0.559588 |
| WR | fantasy_points_per_game | hist_gradient_boosting | validation | 2022 | all | 200 | 0.81 | 8.26218 | 0.511718 | 1.1875 | 0.587457 |
| WR | fantasy_points_per_game | hist_gradient_boosting | validation | 2022 | top | 95 | 0.736842 | 8.26218 | 0.604559 | 1.42232 | 0.57936 |
| WR | fantasy_points_per_game | hist_gradient_boosting | validation | 2022 | middle | 79 | 0.860759 | 8.26218 | 0.421993 | 1.0828 | 0.600812 |
| WR | fantasy_points_per_game | hist_gradient_boosting | validation | 2022 | lower | 26 | 0.923077 | 8.26218 | 0.445118 | 0.64764 | 0.576464 |
| WR | fantasy_points_per_game | hist_gradient_boosting | validation | 2023 | all | 191 | 0.842932 | 8.06095 | 0.460413 | 1.06157 | 0.609819 |
| WR | fantasy_points_per_game | hist_gradient_boosting | validation | 2023 | top | 97 | 0.742268 | 8.06095 | 0.590645 | 1.38232 | 0.667615 |
| WR | fantasy_points_per_game | hist_gradient_boosting | validation | 2023 | middle | 70 | 0.942857 | 8.06095 | 0.317061 | 0.81313 | 0.570397 |
| WR | fantasy_points_per_game | hist_gradient_boosting | validation | 2023 | lower | 24 | 0.958333 | 8.06095 | 0.35217 | 0.489802 | 0.491206 |
| WR | fantasy_points_per_game | hist_gradient_boosting | validation | 2024 | all | 194 | 0.752577 | 7.49237 | 0.501774 | 1.23699 | 0.673478 |
| WR | fantasy_points_per_game | hist_gradient_boosting | validation | 2024 | top | 95 | 0.642105 | 7.49237 | 0.556825 | 1.51761 | 0.726086 |
| WR | fantasy_points_per_game | hist_gradient_boosting | validation | 2024 | middle | 76 | 0.828947 | 7.49237 | 0.445796 | 1.02523 | 0.625542 |
| WR | fantasy_points_per_game | hist_gradient_boosting | validation | 2024 | lower | 23 | 0.956522 | 7.49237 | 0.459359 | 0.777687 | 0.614578 |
| WR | fantasy_points_per_game | ridge | test | 2025 | all | 198 | 0.893939 | 7.82461 | 0.452487 | 1.06633 | 0.507651 |
| WR | fantasy_points_per_game | ridge | test | 2025 | top | 98 | 0.826531 | 7.82461 | 0.450803 | 1.27842 | 0.647721 |
| WR | fantasy_points_per_game | ridge | test | 2025 | middle | 78 | 0.948718 | 7.82461 | 0.433102 | 0.826897 | 0.403279 |
| WR | fantasy_points_per_game | ridge | test | 2025 | lower | 22 | 1 | 7.82461 | 0.528717 | 0.97044 | 0.253745 |
| WR | fantasy_points_per_game | ridge | validation | 2020 | all | 192 | 0.901042 | 11.2079 | 0.531083 | 1.37772 | 0.728224 |
| WR | fantasy_points_per_game | ridge | validation | 2020 | top | 88 | 0.863636 | 11.2079 | 0.670172 | 1.53524 | 0.712394 |
| WR | fantasy_points_per_game | ridge | validation | 2020 | middle | 72 | 0.902778 | 11.2079 | 0.388129 | 1.49773 | 0.782094 |
| WR | fantasy_points_per_game | ridge | validation | 2020 | lower | 32 | 1 | 11.2079 | 0.470237 | 0.674474 | 0.650549 |
| WR | fantasy_points_per_game | ridge | validation | 2021 | all | 212 | 0.84434 | 10.378 | 0.603664 | 1.46631 | 0.896044 |
| WR | fantasy_points_per_game | ridge | validation | 2021 | top | 99 | 0.767677 | 10.378 | 0.793379 | 1.62597 | 0.879981 |
| WR | fantasy_points_per_game | ridge | validation | 2021 | middle | 91 | 0.901099 | 10.378 | 0.392243 | 1.29109 | 0.715106 |
| WR | fantasy_points_per_game | ridge | validation | 2021 | lower | 22 | 0.954545 | 10.378 | 0.62446 | 1.47256 | 1.71675 |
| WR | fantasy_points_per_game | ridge | validation | 2022 | all | 200 | 0.815 | 8.33355 | 0.503101 | 1.19753 | 0.580654 |
| WR | fantasy_points_per_game | ridge | validation | 2022 | top | 100 | 0.75 | 8.33355 | 0.606462 | 1.36877 | 0.571946 |
| WR | fantasy_points_per_game | ridge | validation | 2022 | middle | 77 | 0.87013 | 8.33355 | 0.373929 | 1.09434 | 0.584449 |
| WR | fantasy_points_per_game | ridge | validation | 2022 | lower | 23 | 0.913043 | 8.33355 | 0.486145 | 0.798418 | 0.605815 |
| WR | fantasy_points_per_game | ridge | validation | 2023 | all | 191 | 0.832461 | 7.98068 | 0.463989 | 1.06855 | 0.583737 |
| WR | fantasy_points_per_game | ridge | validation | 2023 | top | 97 | 0.721649 | 7.98068 | 0.55649 | 1.3642 | 0.671447 |
| WR | fantasy_points_per_game | ridge | validation | 2023 | middle | 74 | 0.945946 | 7.98068 | 0.337805 | 0.773331 | 0.511395 |
| WR | fantasy_points_per_game | ridge | validation | 2023 | lower | 20 | 0.95 | 7.98068 | 0.482235 | 0.726978 | 0.426014 |
| WR | fantasy_points_per_game | ridge | validation | 2024 | all | 194 | 0.768041 | 7.52568 | 0.537724 | 1.33811 | 0.684308 |
| WR | fantasy_points_per_game | ridge | validation | 2024 | top | 92 | 0.684783 | 7.52568 | 0.553126 | 1.58363 | 0.799809 |
| WR | fantasy_points_per_game | ridge | validation | 2024 | middle | 86 | 0.825581 | 7.52568 | 0.515412 | 1.11347 | 0.643426 |
| WR | fantasy_points_per_game | ridge | validation | 2024 | lower | 16 | 0.9375 | 7.52568 | 0.569086 | 1.13379 | 0.239915 |
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
| WR | fantasy_points_total | ridge | test | 2025 | all | 434 | 0.836406 | 75.8298 | 6.78834 | 11.4068 | 6.82716 |
| WR | fantasy_points_total | ridge | test | 2025 | top | 109 | 0.431193 | 75.8298 | 14.3857 | 26.0393 | 15.7677 |
| WR | fantasy_points_total | ridge | test | 2025 | middle | 216 | 0.967593 | 75.8298 | 3.67099 | 5.74282 | 4.44907 |
| WR | fantasy_points_total | ridge | test | 2025 | lower | 109 | 0.981651 | 75.8298 | 5.36846 | 7.99844 | 2.59915 |
| WR | fantasy_points_total | ridge | validation | 2020 | all | 414 | 0.852657 | 131.806 | 7.35318 | 18.4949 | 10.0802 |
| WR | fantasy_points_total | ridge | validation | 2020 | top | 104 | 0.576923 | 131.806 | 15.9111 | 31.081 | 12.8831 |
| WR | fantasy_points_total | ridge | validation | 2020 | middle | 206 | 0.917476 | 131.806 | 3.97611 | 18.3857 | 9.86869 |
| WR | fantasy_points_total | ridge | validation | 2020 | lower | 104 | 1 | 131.806 | 5.48445 | 6.12521 | 7.69611 |
| WR | fantasy_points_total | ridge | validation | 2021 | all | 419 | 0.844869 | 125.866 | 8.03269 | 14.9512 | 11.0938 |
| WR | fantasy_points_total | ridge | validation | 2021 | top | 105 | 0.590476 | 125.866 | 16.7208 | 29.1695 | 13.9502 |
| WR | fantasy_points_total | ridge | validation | 2021 | middle | 209 | 0.904306 | 125.866 | 4.56261 | 11.6802 | 9.42374 |
| WR | fantasy_points_total | ridge | validation | 2021 | lower | 105 | 0.980952 | 125.866 | 6.25172 | 7.24373 | 11.5617 |
| WR | fantasy_points_total | ridge | validation | 2022 | all | 432 | 0.831019 | 91.8336 | 6.77444 | 12.8503 | 8.04126 |
| WR | fantasy_points_total | ridge | validation | 2022 | top | 108 | 0.5 | 91.8336 | 14.3674 | 26.1773 | 12.0217 |
| WR | fantasy_points_total | ridge | validation | 2022 | middle | 216 | 0.912037 | 91.8336 | 3.84865 | 10.8923 | 7.99651 |
| WR | fantasy_points_total | ridge | validation | 2022 | lower | 108 | 1 | 91.8336 | 5.0331 | 3.43938 | 4.15026 |
| WR | fantasy_points_total | ridge | validation | 2023 | all | 419 | 0.842482 | 87.73 | 6.02423 | 11.4994 | 7.55491 |
| WR | fantasy_points_total | ridge | validation | 2023 | top | 105 | 0.466667 | 87.73 | 11.6061 | 25.1207 | 13.8694 |
| WR | fantasy_points_total | ridge | validation | 2023 | middle | 209 | 0.956938 | 87.73 | 3.58103 | 7.31087 | 6.35878 |
| WR | fantasy_points_total | ridge | validation | 2023 | lower | 105 | 0.990476 | 87.73 | 5.30548 | 6.21519 | 3.62133 |
| WR | fantasy_points_total | ridge | validation | 2024 | all | 425 | 0.8 | 80.6741 | 6.57368 | 12.1863 | 8.11411 |
| WR | fantasy_points_total | ridge | validation | 2024 | top | 106 | 0.367925 | 80.6741 | 12.8507 | 26.0738 | 15.7788 |
| WR | fantasy_points_total | ridge | validation | 2024 | middle | 213 | 0.915493 | 80.6741 | 4.08282 | 7.57384 | 6.9615 |
| WR | fantasy_points_total | ridge | validation | 2024 | lower | 106 | 1 | 80.6741 | 5.30186 | 7.56716 | 2.76555 |
| WR | games_active | hist_gradient_boosting | test | 2025 | all | 433 | 0.794457 | 7.94306 | 0.568842 | 1.40596 | 0.866126 |
| WR | games_active | hist_gradient_boosting | test | 2025 | top | 109 | 0.761468 | 9.37499 | 1.14839 | 1.91511 | 0.547624 |
| WR | games_active | hist_gradient_boosting | test | 2025 | middle | 215 | 0.716279 | 8.3633 | 0.548066 | 1.78355 | 1.1403 |
| WR | games_active | hist_gradient_boosting | test | 2025 | lower | 109 | 0.981651 | 5.68223 | 0.0302752 | 0.152006 | 0.643821 |
| WR | games_active | hist_gradient_boosting | validation | 2020 | all | 412 | 0.832524 | 8.69358 | 0.547665 | 1.40007 | 0.898843 |
| WR | games_active | hist_gradient_boosting | validation | 2020 | top | 104 | 0.807692 | 10.7465 | 1.21098 | 1.95712 | 0.579172 |
| WR | games_active | hist_gradient_boosting | validation | 2020 | middle | 205 | 0.765854 | 8.9976 | 0.474129 | 1.75995 | 1.17862 |
| WR | games_active | hist_gradient_boosting | validation | 2020 | lower | 103 | 0.990291 | 6.01565 | 0.0242718 | 0.121359 | 0.664778 |
| WR | games_active | hist_gradient_boosting | validation | 2021 | all | 418 | 0.80622 | 8.5317 | 0.606852 | 1.56854 | 0.9585 |
| WR | games_active | hist_gradient_boosting | validation | 2021 | top | 105 | 0.809524 | 10.2102 | 1.24966 | 2.14089 | 0.52428 |
| WR | games_active | hist_gradient_boosting | validation | 2021 | middle | 208 | 0.721154 | 8.99349 | 0.568029 | 1.96777 | 1.30709 |
| WR | games_active | hist_gradient_boosting | validation | 2021 | lower | 105 | 0.971429 | 5.93838 | 0.0409524 | 0.20534 | 0.702186 |
| WR | games_active | hist_gradient_boosting | validation | 2022 | all | 430 | 0.795349 | 8.54071 | 0.642229 | 1.51051 | 0.84508 |
| WR | games_active | hist_gradient_boosting | validation | 2022 | top | 108 | 0.759259 | 9.88207 | 1.40424 | 2.19558 | 0.545484 |
| WR | games_active | hist_gradient_boosting | validation | 2022 | middle | 215 | 0.716279 | 9.13831 | 0.574885 | 1.89417 | 1.10939 |
| WR | games_active | hist_gradient_boosting | validation | 2022 | lower | 107 | 0.990654 | 5.986 | 0.00841121 | 0.0481422 | 0.616383 |
| WR | games_active | hist_gradient_boosting | validation | 2023 | all | 417 | 0.796163 | 8.43572 | 0.545577 | 1.46234 | 0.846859 |
| WR | games_active | hist_gradient_boosting | validation | 2023 | top | 105 | 0.819048 | 9.98008 | 1.0443 | 1.90236 | 0.463345 |
| WR | games_active | hist_gradient_boosting | validation | 2023 | middle | 208 | 0.697115 | 8.88954 | 0.552661 | 1.89385 | 1.16533 |
| WR | games_active | hist_gradient_boosting | validation | 2023 | lower | 104 | 0.971154 | 5.96885 | 0.0278846 | 0.155089 | 0.597108 |
| WR | games_active | hist_gradient_boosting | validation | 2024 | all | 424 | 0.82783 | 8.272 | 0.546047 | 1.3521 | 0.793994 |
| WR | games_active | hist_gradient_boosting | validation | 2024 | top | 106 | 0.830189 | 9.38284 | 1.12827 | 1.85974 | 0.455772 |
| WR | games_active | hist_gradient_boosting | validation | 2024 | middle | 212 | 0.740566 | 8.79889 | 0.522769 | 1.73723 | 1.05992 |
| WR | games_active | hist_gradient_boosting | validation | 2024 | lower | 106 | 1 | 6.10737 | 0.0103774 | 0.074216 | 0.60036 |
| WR | games_active | ridge | test | 2025 | all | 433 | 0.806005 | 8.32995 | 0.565399 | 1.47479 | 0.827959 |
| WR | games_active | ridge | test | 2025 | top | 109 | 0.816514 | 10.235 | 1.11907 | 1.98033 | 0.526834 |
| WR | games_active | ridge | test | 2025 | middle | 215 | 0.716279 | 8.94909 | 0.547159 | 1.84302 | 1.03533 |
| WR | games_active | ridge | test | 2025 | lower | 109 | 0.972477 | 5.20367 | 0.0477064 | 0.242898 | 0.720054 |
| WR | games_active | ridge | validation | 2020 | all | 412 | 0.817961 | 9.55764 | 0.607627 | 1.62076 | 0.850666 |
| WR | games_active | ridge | validation | 2020 | top | 104 | 0.798077 | 10.7834 | 1.32089 | 1.96888 | 0.558195 |
| WR | games_active | ridge | validation | 2020 | middle | 205 | 0.736585 | 10.427 | 0.546679 | 2.12351 | 1.09974 |
| WR | games_active | ridge | validation | 2020 | lower | 103 | 1 | 6.58982 | 0.00873786 | 0.268643 | 0.650244 |
| WR | games_active | ridge | validation | 2021 | all | 418 | 0.822967 | 9.21399 | 0.574069 | 1.61913 | 0.90824 |
| WR | games_active | ridge | validation | 2021 | top | 105 | 0.809524 | 11.0117 | 1.10528 | 2.13691 | 0.51275 |
| WR | games_active | ridge | validation | 2021 | middle | 208 | 0.754808 | 9.9132 | 0.570704 | 2.01591 | 1.16696 |
| WR | games_active | ridge | validation | 2021 | lower | 105 | 0.971429 | 6.03118 | 0.0495238 | 0.315348 | 0.791219 |
| WR | games_active | ridge | validation | 2022 | all | 430 | 0.795349 | 9.16599 | 0.566251 | 1.57792 | 0.83233 |
| WR | games_active | ridge | validation | 2022 | top | 108 | 0.768519 | 10.5249 | 1.17887 | 2.06146 | 0.520554 |
| WR | games_active | ridge | validation | 2022 | middle | 215 | 0.706977 | 10.0184 | 0.537071 | 2.05373 | 1.10376 |
| WR | games_active | ridge | validation | 2022 | lower | 107 | 1 | 6.08157 | 0.00654206 | 0.133807 | 0.601615 |
| WR | games_active | ridge | validation | 2023 | all | 417 | 0.827338 | 9.18409 | 0.558968 | 1.56267 | 0.811824 |
| WR | games_active | ridge | validation | 2023 | top | 105 | 0.87619 | 10.5328 | 0.969427 | 1.8414 | 0.406257 |
| WR | games_active | ridge | validation | 2023 | middle | 208 | 0.721154 | 9.99499 | 0.618269 | 2.0993 | 1.12379 |
| WR | games_active | ridge | validation | 2023 | lower | 104 | 0.990385 | 6.20059 | 0.0259615 | 0.207993 | 0.59735 |
| WR | games_active | ridge | validation | 2024 | all | 424 | 0.818396 | 8.84447 | 0.552631 | 1.46824 | 0.778475 |
| WR | games_active | ridge | validation | 2024 | top | 106 | 0.839623 | 9.89661 | 1.08848 | 1.88457 | 0.472742 |
| WR | games_active | ridge | validation | 2024 | middle | 212 | 0.716981 | 9.66247 | 0.555363 | 1.92225 | 1.01842 |
| WR | games_active | ridge | validation | 2024 | lower | 106 | 1 | 6.15636 | 0.0113208 | 0.14388 | 0.604315 |

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
- [2020, 2021, 2022, 2023, 2024] pooled validation MAE plus a paired bootstrap confidence check select champions; 2025 never selects.
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
  "feature_response": "docs/images/phase4/phase4-7ae8e9aed04bffca00c0/attempt-866987f75a2c406693cf892d49adc975/feature_response.svg",
  "hgb_permutation_importance": "docs/images/phase4/phase4-7ae8e9aed04bffca00c0/attempt-866987f75a2c406693cf892d49adc975/hgb_permutation_importance.svg",
  "interval_coverage_width": "docs/images/phase4/phase4-7ae8e9aed04bffca00c0/attempt-866987f75a2c406693cf892d49adc975/interval_coverage_width.svg",
  "ridge_coefficients": "docs/images/phase4/phase4-7ae8e9aed04bffca00c0/attempt-866987f75a2c406693cf892d49adc975/ridge_coefficients.svg",
  "season_mae_comparison": "docs/images/phase4/phase4-7ae8e9aed04bffca00c0/attempt-866987f75a2c406693cf892d49adc975/season_mae_comparison.svg",
  "segment_mae": "docs/images/phase4/phase4-7ae8e9aed04bffca00c0/attempt-866987f75a2c406693cf892d49adc975/segment_mae.svg",
  "test_predicted_vs_actual": "docs/images/phase4/phase4-7ae8e9aed04bffca00c0/attempt-866987f75a2c406693cf892d49adc975/test_predicted_vs_actual.svg",
  "test_residuals": "docs/images/phase4/phase4-7ae8e9aed04bffca00c0/attempt-866987f75a2c406693cf892d49adc975/test_residuals.svg"
}
````

## Additional validated details

````json
{
  "publication_id": "attempt-866987f75a2c406693cf892d49adc975",
  "selected_feature_data_fingerprint": "99b0afd6334f3b476a93c28e3d5ed82240b72b2b1b5bb425900c2a3245f69ad4"
}
````

## Machine-readable detail

Per-segment metrics, model inventory, feature contract, and global explanations are retained in the matching JSON report.
