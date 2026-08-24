"""Deterministic configuration for Phase 4 player projection models."""

from __future__ import annotations

import hashlib
import json
from dataclasses import asdict, dataclass
from typing import Any, Final, Literal

PLAYER_MODEL_VERSION: Final = "phase4-player-models-v3"
FEATURE_CONTRACT_VERSION: Final = "phase4-player-features-v2"

RIDGE: Final = "ridge"
HIST_GRADIENT_BOOSTING: Final = "hist_gradient_boosting"
ModelFamily = Literal["ridge", "hist_gradient_boosting"]

TARGET_FANTASY_POINTS_PER_GAME: Final = "fantasy_points_per_game"
TARGET_GAMES_ACTIVE: Final = "games_active"
TARGET_FANTASY_POINTS_TOTAL: Final = "fantasy_points_total"

DEFAULT_POSITIONS: Final = ("QB", "RB", "WR", "TE")
DEFAULT_TARGETS: Final = (
    TARGET_FANTASY_POINTS_PER_GAME,
    TARGET_GAMES_ACTIVE,
    TARGET_FANTASY_POINTS_TOTAL,
)

# This is deliberately an allowlist. New Phase 3 payload fields cannot enter a
# learned model until they are reviewed and this contract version is changed.
DEFAULT_NUMERIC_FEATURES: Final = (
    "prediction_season",
    "age_at_cutoff",
    "draft_pick",
    "draft_round",
    "height_inches",
    "history_seasons",
    "lag1_fantasy_points_per_game",
    "lag1_fantasy_points_total",
    "lag1_games_active",
    "lag1_stat_games",
    "missing_age",
    "missing_draft_capital",
    "missing_history",
    "missing_lag1",
    "missing_lag1_participation",
    "nfl_experience_years",
    "position_prior_fantasy_points_per_game",
    "position_prior_games_active",
    "team_changed_last_feature_season",
    "weighted_3yr_fantasy_points_per_game",
    "weighted_3yr_games_active",
    "weighted_3yr_passing_attempts_per_game",
    "weighted_3yr_passing_yards_per_game",
    "weighted_3yr_passing_tds_per_game",
    "weighted_3yr_interceptions_per_game",
    "weighted_3yr_carries_per_game",
    "weighted_3yr_rushing_yards_per_game",
    "weighted_3yr_rushing_tds_per_game",
    "weighted_3yr_targets_per_game",
    "weighted_3yr_receptions_per_game",
    "weighted_3yr_receiving_yards_per_game",
    "weighted_3yr_receiving_tds_per_game",
    "weighted_3yr_two_point_conversions_per_game",
    "weighted_3yr_fumbles_lost_per_game",
)
DEFAULT_CATEGORICAL_FEATURES: Final = ("previous_team",)
DEFAULT_DRAFT_RELEVANCE_TOP_N: Final = (
    ("QB", 12),
    ("RB", 24),
    ("WR", 36),
    ("TE", 12),
)

_BLOCKED_METADATA_FEATURES: Final = frozenset(
    {
        "candidate_evidence_seasons",
        "candidate_history_lookback_seasons",
        "candidate_selection_reason",
        "cutoff_date",
        "data_fingerprint",
        "feature_available_at",
        "feature_season",
        "feature_version",
        "is_rookie",
        "player_id",
        "position",
        "scoring_ruleset_fingerprint",
        "source_dataset_ids",
        "source_max_as_of",
        "source_max_stat_season",
        "target_payload",
    }
)


@dataclass(frozen=True)
class HistGradientBoostingGridPoint:
    """One deliberately compact, deterministic HGB tuning candidate."""

    learning_rate: float
    max_iter: int
    max_leaf_nodes: int
    min_samples_leaf: int
    l2_regularization: float

    def __post_init__(self) -> None:
        if self.learning_rate <= 0:
            raise ValueError("HGB learning_rate must be positive.")
        if self.max_iter < 1 or self.max_leaf_nodes < 2 or self.min_samples_leaf < 1:
            raise ValueError("HGB iteration, leaf, and sample settings must be positive.")
        if self.l2_regularization < 0:
            raise ValueError("HGB l2_regularization cannot be negative.")


DEFAULT_HGB_GRID: Final = (
    HistGradientBoostingGridPoint(
        learning_rate=0.05,
        max_iter=120,
        max_leaf_nodes=15,
        min_samples_leaf=20,
        l2_regularization=1.0,
    ),
    HistGradientBoostingGridPoint(
        learning_rate=0.08,
        max_iter=160,
        max_leaf_nodes=31,
        min_samples_leaf=20,
        l2_regularization=2.0,
    ),
)


@dataclass(frozen=True)
class DraftRelevancePolicy:
    """Cutoff-safe model-selection policy for a conventional 12-team draft pool."""

    anchor_baseline: str = "weighted_components"
    top_n_by_position: tuple[tuple[str, int], ...] = DEFAULT_DRAFT_RELEVANCE_TOP_N
    pooled_mae_regression_tolerance: float = 0.05
    max_total_top_n_capture_regression: float = 0.05

    def __post_init__(self) -> None:
        if not self.anchor_baseline.strip():
            raise ValueError("The draft-relevance anchor baseline cannot be blank.")
        positions = [position for position, _ in self.top_n_by_position]
        if len(set(positions)) != len(positions) or not positions:
            raise ValueError("Draft-relevance positions must be non-empty and unique.")
        if any(position not in DEFAULT_POSITIONS for position in positions):
            raise ValueError("Draft relevance supports only QB, RB, WR, and TE.")
        if any(top_n < 1 for _, top_n in self.top_n_by_position):
            raise ValueError("Every draft-relevance top-N value must be positive.")
        if not 0.0 <= self.pooled_mae_regression_tolerance <= 1.0:
            raise ValueError("The pooled-MAE regression tolerance must be within [0, 1].")
        if not 0.0 <= self.max_total_top_n_capture_regression <= 1.0:
            raise ValueError("The top-N capture regression tolerance must be within [0, 1].")

    def top_n_for(self, position: str) -> int:
        """Return the fixed draft-relevant cohort size for one position."""

        normalized = position.strip().upper()
        try:
            return dict(self.top_n_by_position)[normalized]
        except KeyError as exc:
            raise ValueError(
                f"No draft-relevance top-N value is configured for {normalized or position!r}."
            ) from exc


@dataclass(frozen=True)
class PlayerModelConfig:
    """Versioned training behavior included in every model-run fingerprint."""

    version: str = PLAYER_MODEL_VERSION
    random_seed: int = 42
    positions: tuple[str, ...] = DEFAULT_POSITIONS
    targets: tuple[str, ...] = DEFAULT_TARGETS
    numeric_features: tuple[str, ...] = DEFAULT_NUMERIC_FEATURES
    categorical_features: tuple[str, ...] = DEFAULT_CATEGORICAL_FEATURES
    ridge_alphas: tuple[float, ...] = (0.1, 1.0, 10.0)
    hgb_grid: tuple[HistGradientBoostingGridPoint, ...] = DEFAULT_HGB_GRID
    min_inner_training_seasons: int = 2
    max_inner_validation_seasons: int | None = 3
    interval_quantiles: tuple[float, float, float] = (0.10, 0.50, 0.90)
    games_active_bounds: tuple[float, float] = (0.0, 18.0)
    learned_operational_center: str = "training_only_residual_adjusted_p50"
    baseline_operational_center: str = "phase3_transparent_point"
    draft_relevance_policy: DraftRelevancePolicy = DraftRelevancePolicy()

    def __post_init__(self) -> None:
        if not self.version.strip():
            raise ValueError("Model version cannot be empty.")
        if self.random_seed < 0:
            raise ValueError("random_seed cannot be negative.")
        if len(set(self.positions)) != len(self.positions) or not self.positions:
            raise ValueError("positions must be non-empty and unique.")
        if any(position not in DEFAULT_POSITIONS for position in self.positions):
            raise ValueError("Only QB, RB, WR, and TE model routes are supported.")
        if len(set(self.targets)) != len(self.targets) or not self.targets:
            raise ValueError("targets must be non-empty and unique.")
        if any(target not in DEFAULT_TARGETS for target in self.targets):
            raise ValueError("Unsupported player projection target.")
        feature_names = (*self.numeric_features, *self.categorical_features)
        if not feature_names or len(set(feature_names)) != len(feature_names):
            raise ValueError("Model features must be non-empty and unique.")
        unsafe = sorted(
            feature
            for feature in feature_names
            if feature.startswith("baseline_")
            or feature.startswith("target_")
            or feature in _BLOCKED_METADATA_FEATURES
        )
        if unsafe:
            raise ValueError(f"Unsafe or metadata model features are forbidden: {unsafe}.")
        if "prediction_season" not in self.numeric_features:
            raise ValueError("prediction_season must remain an explicit model feature.")
        if {"age_at_cutoff", "age_adjustment_factor"}.issubset(self.numeric_features):
            raise ValueError(
                "Learned models cannot include both raw age and the derived age adjustment."
            )
        if "previous_team" not in self.categorical_features:
            raise ValueError("previous_team must remain an explicit categorical feature.")
        configured_relevance_positions = {
            position for position, _ in self.draft_relevance_policy.top_n_by_position
        }
        missing_relevance_positions = sorted(set(self.positions) - configured_relevance_positions)
        if missing_relevance_positions:
            raise ValueError(
                "Draft relevance has no top-N value for positions: "
                f"{missing_relevance_positions}."
            )
        if not self.ridge_alphas or any(alpha <= 0 for alpha in self.ridge_alphas):
            raise ValueError("Every Ridge alpha must be positive.")
        if not self.hgb_grid:
            raise ValueError("At least one HGB grid point is required.")
        if self.min_inner_training_seasons < 1:
            raise ValueError("min_inner_training_seasons must be at least one.")
        if self.max_inner_validation_seasons is not None and self.max_inner_validation_seasons < 1:
            raise ValueError("max_inner_validation_seasons must be positive when set.")
        if tuple(sorted(self.interval_quantiles)) != self.interval_quantiles:
            raise ValueError("Interval quantiles must be ordered.")
        if any(quantile < 0 or quantile > 1 for quantile in self.interval_quantiles):
            raise ValueError("Interval quantiles must be within [0, 1].")
        if self.interval_quantiles != (0.10, 0.50, 0.90):
            raise ValueError(
                "Phase 4 interval quantiles must remain exactly (0.10, 0.50, 0.90) "
                "while the warehouse and evaluation schema use P10/P50/P90."
            )
        if self.games_active_bounds[0] >= self.games_active_bounds[1]:
            raise ValueError("games_active_bounds must be strictly increasing.")
        if self.learned_operational_center != "training_only_residual_adjusted_p50":
            raise ValueError("Phase 4 learned candidates must be scored and served from P50.")
        if self.baseline_operational_center != "phase3_transparent_point":
            raise ValueError("Phase 4 baselines must retain their evaluated transparent point.")

    def canonical_payload(self) -> dict[str, Any]:
        """Return the complete JSON-compatible semantic model configuration."""

        return asdict(self)

    def fingerprint(self) -> str:
        """Hash all behavior that can change model fitting or postprocessing."""

        return _fingerprint(self.canonical_payload())

    def feature_contract_fingerprint(self) -> str:
        """Hash only the ordered predictor contract and its extraction version."""

        return _fingerprint(
            {
                "feature_contract_version": FEATURE_CONTRACT_VERSION,
                "numeric_features": self.numeric_features,
                "categorical_features": self.categorical_features,
                "rookie_training_policy": "exclude_all_rookies",
            }
        )


def build_run_fingerprint(
    config: PlayerModelConfig,
    *,
    feature_data_fingerprint: str,
    target_data_fingerprint: str,
    build_fingerprint: str,
    scoring_ruleset_fingerprint: str,
    baseline_report_fingerprint: str,
) -> str:
    """Bind one deterministic model run to an exact validated Phase 3 build."""

    input_fingerprints = {
        "feature_data_fingerprint": feature_data_fingerprint,
        "target_data_fingerprint": target_data_fingerprint,
        "build_fingerprint": build_fingerprint,
        "scoring_ruleset_fingerprint": scoring_ruleset_fingerprint,
        "baseline_report_fingerprint": baseline_report_fingerprint,
    }
    empty = sorted(name for name, value in input_fingerprints.items() if not value.strip())
    if empty:
        raise ValueError(f"Run fingerprints cannot be empty: {empty}.")
    return _fingerprint(
        {
            "model_version": config.version,
            "model_config_fingerprint": config.fingerprint(),
            "model_feature_fingerprint": config.feature_contract_fingerprint(),
            **input_fingerprints,
        }
    )


def canonical_json(value: Any) -> str:
    """Serialize deterministic model metadata without NaN or platform formatting."""

    return json.dumps(
        value,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=True,
        allow_nan=False,
    )


def _fingerprint(value: Any) -> str:
    return hashlib.sha256(canonical_json(value).encode("utf-8")).hexdigest()
