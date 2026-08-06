# Phase 4 model cards

Run `phase4-7ae8e9aed04bffca00c0` registered 24 learned candidates: Ridge and histogram gradient boosting for each QB/RB/WR/TE target route. The deterministic run ID identifies the model/data contract; the currently validated immutable publication is `attempt-866987f75a2c406693cf892d49adc975`. A card documents a candidate even when the transparent baseline or the other learned family won validation.

Champion decisions and the untouched 2025 test results are summarized in the [Phase 4 evaluation report](../../PHASE_4_MODEL_EVALUATION.md). Learned candidates were promoted only when they lowered pooled 2020-2024 validation MAE and the paired-bootstrap learned-minus-baseline 95% interval stayed below zero.

| Position | Target | Ridge | Histogram gradient boosting |
|---|---|---|---|
| QB | Points per active game | [Card](phase4-7ae8e9aed04bffca00c0/attempt-866987f75a2c406693cf892d49adc975/phase4-7ae8e9aed04bffca00c0-qb-ppg-ridge.md) | [Card](phase4-7ae8e9aed04bffca00c0/attempt-866987f75a2c406693cf892d49adc975/phase4-7ae8e9aed04bffca00c0-qb-ppg-hgb.md) |
| QB | Active games | [Card](phase4-7ae8e9aed04bffca00c0/attempt-866987f75a2c406693cf892d49adc975/phase4-7ae8e9aed04bffca00c0-qb-games-ridge.md) | [Card](phase4-7ae8e9aed04bffca00c0/attempt-866987f75a2c406693cf892d49adc975/phase4-7ae8e9aed04bffca00c0-qb-games-hgb.md) |
| QB | Total points | [Card](phase4-7ae8e9aed04bffca00c0/attempt-866987f75a2c406693cf892d49adc975/phase4-7ae8e9aed04bffca00c0-qb-total-ridge.md) | [Card](phase4-7ae8e9aed04bffca00c0/attempt-866987f75a2c406693cf892d49adc975/phase4-7ae8e9aed04bffca00c0-qb-total-hgb.md) |
| RB | Points per active game | [Card](phase4-7ae8e9aed04bffca00c0/attempt-866987f75a2c406693cf892d49adc975/phase4-7ae8e9aed04bffca00c0-rb-ppg-ridge.md) | [Card](phase4-7ae8e9aed04bffca00c0/attempt-866987f75a2c406693cf892d49adc975/phase4-7ae8e9aed04bffca00c0-rb-ppg-hgb.md) |
| RB | Active games | [Card](phase4-7ae8e9aed04bffca00c0/attempt-866987f75a2c406693cf892d49adc975/phase4-7ae8e9aed04bffca00c0-rb-games-ridge.md) | [Card](phase4-7ae8e9aed04bffca00c0/attempt-866987f75a2c406693cf892d49adc975/phase4-7ae8e9aed04bffca00c0-rb-games-hgb.md) |
| RB | Total points | [Card](phase4-7ae8e9aed04bffca00c0/attempt-866987f75a2c406693cf892d49adc975/phase4-7ae8e9aed04bffca00c0-rb-total-ridge.md) | [Card](phase4-7ae8e9aed04bffca00c0/attempt-866987f75a2c406693cf892d49adc975/phase4-7ae8e9aed04bffca00c0-rb-total-hgb.md) |
| WR | Points per active game | [Card](phase4-7ae8e9aed04bffca00c0/attempt-866987f75a2c406693cf892d49adc975/phase4-7ae8e9aed04bffca00c0-wr-ppg-ridge.md) | [Card](phase4-7ae8e9aed04bffca00c0/attempt-866987f75a2c406693cf892d49adc975/phase4-7ae8e9aed04bffca00c0-wr-ppg-hgb.md) |
| WR | Active games | [Card](phase4-7ae8e9aed04bffca00c0/attempt-866987f75a2c406693cf892d49adc975/phase4-7ae8e9aed04bffca00c0-wr-games-ridge.md) | [Card](phase4-7ae8e9aed04bffca00c0/attempt-866987f75a2c406693cf892d49adc975/phase4-7ae8e9aed04bffca00c0-wr-games-hgb.md) |
| WR | Total points | [Card](phase4-7ae8e9aed04bffca00c0/attempt-866987f75a2c406693cf892d49adc975/phase4-7ae8e9aed04bffca00c0-wr-total-ridge.md) | [Card](phase4-7ae8e9aed04bffca00c0/attempt-866987f75a2c406693cf892d49adc975/phase4-7ae8e9aed04bffca00c0-wr-total-hgb.md) |
| TE | Points per active game | [Card](phase4-7ae8e9aed04bffca00c0/attempt-866987f75a2c406693cf892d49adc975/phase4-7ae8e9aed04bffca00c0-te-ppg-ridge.md) | [Card](phase4-7ae8e9aed04bffca00c0/attempt-866987f75a2c406693cf892d49adc975/phase4-7ae8e9aed04bffca00c0-te-ppg-hgb.md) |
| TE | Active games | [Card](phase4-7ae8e9aed04bffca00c0/attempt-866987f75a2c406693cf892d49adc975/phase4-7ae8e9aed04bffca00c0-te-games-ridge.md) | [Card](phase4-7ae8e9aed04bffca00c0/attempt-866987f75a2c406693cf892d49adc975/phase4-7ae8e9aed04bffca00c0-te-games-hgb.md) |
| TE | Total points | [Card](phase4-7ae8e9aed04bffca00c0/attempt-866987f75a2c406693cf892d49adc975/phase4-7ae8e9aed04bffca00c0-te-total-ridge.md) | [Card](phase4-7ae8e9aed04bffca00c0/attempt-866987f75a2c406693cf892d49adc975/phase4-7ae8e9aed04bffca00c0-te-total-hgb.md) |

Each card records training seasons, cutoff and feature contracts, fold-local preprocessing, selected hyperparameters, baseline comparison, empirical learned-model uncertainty, global explanations, limitations, artifact path, and SHA-256 lineage.
