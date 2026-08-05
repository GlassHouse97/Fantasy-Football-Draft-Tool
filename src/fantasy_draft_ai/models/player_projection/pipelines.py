"""Fold-local scikit-learn pipelines for Phase 4 player models."""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import asdict
from typing import Any

from sklearn.compose import ColumnTransformer  # type: ignore[import-untyped]
from sklearn.ensemble import HistGradientBoostingRegressor  # type: ignore[import-untyped]
from sklearn.impute import SimpleImputer  # type: ignore[import-untyped]
from sklearn.linear_model import Ridge  # type: ignore[import-untyped]
from sklearn.pipeline import Pipeline  # type: ignore[import-untyped]
from sklearn.preprocessing import (  # type: ignore[import-untyped]
    OneHotEncoder,
    StandardScaler,
)

from fantasy_draft_ai.models.player_projection.config import (
    HIST_GRADIENT_BOOSTING,
    RIDGE,
    ModelFamily,
    PlayerModelConfig,
)


def candidate_parameters(
    family: ModelFamily,
    config: PlayerModelConfig,
) -> tuple[dict[str, Any], ...]:
    """Return the complete compact tuning grid in deterministic order."""

    if family == RIDGE:
        return tuple({"alpha": float(alpha)} for alpha in config.ridge_alphas)
    if family == HIST_GRADIENT_BOOSTING:
        return tuple(asdict(point) for point in config.hgb_grid)
    raise ValueError(f"Unsupported model family: {family!r}.")


def build_pipeline(
    family: ModelFamily,
    config: PlayerModelConfig,
    parameters: Mapping[str, Any] | None = None,
) -> Pipeline:
    """Build an unfitted estimator with every learned transform inside the pipeline."""

    resolved_parameters = dict(parameters or candidate_parameters(family, config)[0])
    if family == RIDGE:
        _require_parameter_keys(resolved_parameters, {"alpha"}, family)
        estimator = Ridge(
            alpha=float(resolved_parameters["alpha"]),
            solver="lsqr",
            tol=1e-8,
        )
        numeric_steps: list[tuple[str, Any]] = [
            (
                "imputer",
                SimpleImputer(
                    strategy="median",
                    add_indicator=True,
                    keep_empty_features=True,
                ),
            ),
            ("scaler", StandardScaler()),
        ]
    elif family == HIST_GRADIENT_BOOSTING:
        expected = {
            "learning_rate",
            "max_iter",
            "max_leaf_nodes",
            "min_samples_leaf",
            "l2_regularization",
        }
        _require_parameter_keys(resolved_parameters, expected, family)
        estimator = HistGradientBoostingRegressor(
            loss="squared_error",
            learning_rate=float(resolved_parameters["learning_rate"]),
            max_iter=int(resolved_parameters["max_iter"]),
            max_leaf_nodes=int(resolved_parameters["max_leaf_nodes"]),
            min_samples_leaf=int(resolved_parameters["min_samples_leaf"]),
            l2_regularization=float(resolved_parameters["l2_regularization"]),
            early_stopping=False,
            random_state=config.random_seed,
        )
        numeric_steps = [
            (
                "imputer",
                SimpleImputer(
                    strategy="median",
                    add_indicator=True,
                    keep_empty_features=True,
                ),
            )
        ]
    else:
        raise ValueError(f"Unsupported model family: {family!r}.")

    categorical = Pipeline(
        steps=[
            (
                "imputer",
                SimpleImputer(strategy="constant", fill_value="__MISSING__"),
            ),
            (
                "one_hot",
                OneHotEncoder(handle_unknown="ignore", sparse_output=False),
            ),
        ]
    )
    preprocessor = ColumnTransformer(
        transformers=[
            ("numeric", Pipeline(steps=numeric_steps), list(config.numeric_features)),
            ("categorical", categorical, list(config.categorical_features)),
        ],
        remainder="drop",
        sparse_threshold=0.0,
        verbose_feature_names_out=True,
    )
    return Pipeline(steps=[("preprocessor", preprocessor), ("estimator", estimator)])


def transformed_feature_names(pipeline: Pipeline) -> tuple[str, ...]:
    """Return fitted transformed names for artifacts and explanations."""

    preprocessor = pipeline.named_steps.get("preprocessor")
    if not isinstance(preprocessor, ColumnTransformer):
        raise ValueError("Pipeline does not contain the expected fitted preprocessor.")
    return tuple(str(name) for name in preprocessor.get_feature_names_out())


def _require_parameter_keys(
    parameters: Mapping[str, Any], expected: set[str], family: ModelFamily
) -> None:
    actual = set(parameters)
    if actual != expected:
        raise ValueError(
            f"{family} parameters must be exactly {sorted(expected)}; got {sorted(actual)}."
        )
