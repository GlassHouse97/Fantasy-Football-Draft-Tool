from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pytest

from fantasy_draft_ai.models.player_projection.artifacts import (
    ArtifactIntegrityError,
    ArtifactPathError,
    ArtifactVerificationError,
    load_verified_model,
    persist_verified_model,
    resolve_artifact_path,
    verify_artifact,
)
from fantasy_draft_ai.models.player_projection.explanations import (
    NON_CAUSAL_NOTICE,
    explain_heuristic_fallback,
    explain_player_prediction,
    hist_gradient_boosting_permutation_importance,
    numeric_partial_dependence,
    ridge_coefficient_importance,
)


class LinearTestModel:
    def __init__(self, factor: float = 2.0) -> None:
        self.factor = factor

    def predict(self, rows: Any) -> list[float]:
        return [self.factor * float(row[0]) for row in rows]


class ChangesWhenReloadedModel(LinearTestModel):
    def __getstate__(self) -> dict[str, float]:
        return {"factor": self.factor + 1.0}


class TabularLinearModel:
    def predict(self, rows: Any) -> list[float]:
        return [
            float(row["age"]) + 2.0 * float(row["weighted_history"]) for _, row in rows.iterrows()
        ]


class MissingAwareTabularModel:
    def predict(self, rows: Any) -> list[float]:
        predictions: list[float] = []
        for _, row in rows.iterrows():
            age = float(row["age"])
            safe_age = 0.0 if age != age else age
            team_value = row["previous_team"]
            team_effect = 0.0 if team_value != team_value else 1.0
            predictions.append(safe_age + team_effect)
        return predictions


class CoefficientModel:
    coef_ = (0.5, -2.0, 2.0)


def test_persist_verified_model_is_relative_atomic_and_reloadable(tmp_path: Path) -> None:
    features = [[1.0], [2.5], [-1.0]]

    metadata = persist_verified_model(
        LinearTestModel(),
        tmp_path,
        "QB/points/ridge.joblib",
        features,
    )

    assert metadata.relative_path == "QB/points/ridge.joblib"
    assert len(metadata.sha256) == 64
    assert metadata.size_bytes > 0
    assert metadata.as_dict() == {
        "artifact_path": "QB/points/ridge.joblib",
        "artifact_sha256": metadata.sha256,
        "artifact_size_bytes": metadata.size_bytes,
    }
    loaded = load_verified_model(
        tmp_path,
        metadata.relative_path,
        expected_sha256=metadata.sha256,
        expected_size_bytes=metadata.size_bytes,
    )
    assert loaded.predict(features) == [2.0, 5.0, -2.0]
    assert not list(tmp_path.rglob("*.staged.joblib"))


@pytest.mark.parametrize(
    "unsafe_path",
    ["../outside.joblib", "nested/../../outside.joblib", "C:/outside.joblib", "/outside.joblib"],
)
def test_artifact_path_rejects_traversal_and_absolute_paths(
    tmp_path: Path, unsafe_path: str
) -> None:
    with pytest.raises(ArtifactPathError):
        resolve_artifact_path(tmp_path, unsafe_path)


def test_failed_reload_verification_preserves_existing_artifact(tmp_path: Path) -> None:
    target = tmp_path / "WR" / "points" / "ridge.joblib"
    target.parent.mkdir(parents=True)
    target.write_bytes(b"previous-good-artifact")

    with pytest.raises(ArtifactVerificationError, match="differ"):
        persist_verified_model(
            ChangesWhenReloadedModel(),
            tmp_path,
            "WR/points/ridge.joblib",
            [[1.0], [2.0]],
        )

    assert target.read_bytes() == b"previous-good-artifact"
    assert not list(tmp_path.rglob("*.staged.joblib"))


def test_verify_artifact_detects_tampering(tmp_path: Path) -> None:
    metadata = persist_verified_model(LinearTestModel(), tmp_path, "TE/games/ridge.joblib", [[1.0]])
    path = tmp_path / metadata.relative_path
    path.write_bytes(path.read_bytes() + b"tampered")

    with pytest.raises(ArtifactIntegrityError, match="size mismatch"):
        verify_artifact(
            tmp_path,
            metadata.relative_path,
            expected_sha256=metadata.sha256,
            expected_size_bytes=metadata.size_bytes,
        )


def test_ridge_importance_is_deterministic_and_json_safe() -> None:
    first = ridge_coefficient_importance(CoefficientModel(), feature_names=["age", "lag", "volume"])
    second = ridge_coefficient_importance(
        CoefficientModel(), feature_names=["age", "lag", "volume"]
    )

    assert first == second
    assert [row["feature"] for row in first] == ["lag", "volume", "age"]
    assert [row["rank"] for row in first] == [1, 2, 3]
    assert json.loads(json.dumps(first, allow_nan=False)) == first


def test_hgb_permutation_importance_and_partial_dependence_are_repeatable() -> None:
    pd = pytest.importorskip("pandas")
    ensemble = pytest.importorskip("sklearn.ensemble")
    features = pd.DataFrame(
        {
            "signal": [float(value) for value in range(40)],
            "noise": [float(value % 3) for value in range(40)],
        }
    )
    targets = features["signal"] * 3.0
    model = ensemble.HistGradientBoostingRegressor(
        max_iter=30,
        min_samples_leaf=2,
        early_stopping=False,
        random_state=42,
    ).fit(features, targets)

    first = hist_gradient_boosting_permutation_importance(model, features, targets, n_repeats=3)
    second = hist_gradient_boosting_permutation_importance(model, features, targets, n_repeats=3)
    curves = numeric_partial_dependence(model, features, ["signal"], grid_resolution=5)

    assert first == second
    assert first[0]["feature"] == "signal"
    assert curves[0]["feature"] == "signal"
    assert len(curves[0]["points"]) == 5
    assert curves[0]["interpretation"] == NON_CAUSAL_NOTICE
    json.dumps({"importance": first, "curves": curves}, allow_nan=False)


def test_partial_dependence_uses_finite_grid_when_feature_contains_missing_values() -> None:
    pd = pytest.importorskip("pandas")
    ensemble = pytest.importorskip("sklearn.ensemble")
    features = pd.DataFrame(
        {
            "signal": [float("nan") if value % 7 == 0 else float(value) for value in range(40)],
            "noise": [float(value % 3) for value in range(40)],
        }
    )
    targets = pd.Series([float(value * 3) for value in range(40)])
    model = ensemble.HistGradientBoostingRegressor(
        max_iter=30,
        min_samples_leaf=2,
        early_stopping=False,
        random_state=42,
    ).fit(features, targets)

    curve = numeric_partial_dependence(
        model,
        features,
        ["signal"],
        grid_resolution=5,
    )[0]

    assert curve["response_status"] == "stable_numeric_grid"
    assert len(curve["points"]) == 5
    assert all(point["feature_value"] is not None for point in curve["points"])
    json.dumps(curve, allow_nan=False)


def test_partial_dependence_marks_feature_without_stable_numeric_grid() -> None:
    pd = pytest.importorskip("pandas")
    features = pd.DataFrame(
        {
            "age": [float("nan"), float("nan")],
            "previous_team": [float("nan"), float("nan")],
        }
    )

    curve = numeric_partial_dependence(
        MissingAwareTabularModel(),
        features,
        ["age"],
    )[0]

    assert curve["response_status"] == "no_stable_numeric_grid"
    assert curve["points"] == []
    assert "Fewer than two finite" in curve["reason"]
    json.dumps(curve, allow_nan=False)


def test_local_player_explanation_uses_signed_position_reference_deltas() -> None:
    explanation = explain_player_prediction(
        TabularLinearModel(),
        {"age": 25.0, "weighted_history": 10.0, "previous_team": "NYJ"},
        {"age": 27.0, "weighted_history": 7.0, "previous_team": "BUF"},
        position="WR",
        target_name="fantasy_points_per_game",
        top_n=2,
    )

    assert explanation["prediction"] == 45.0
    assert [factor["feature"] for factor in explanation["top_factors"]] == [
        "weighted_history",
        "age",
    ]
    assert [factor["prediction_delta"] for factor in explanation["top_factors"]] == [
        6.0,
        -2.0,
    ]
    assert "associative, not causal" in explanation["interpretation"]
    json.dumps(explanation, allow_nan=False)


def test_local_explanation_serializes_missing_values_and_perturbs_them() -> None:
    missing = float("nan")
    explanation = explain_player_prediction(
        MissingAwareTabularModel(),
        {"age": missing, "previous_team": missing},
        {"age": 28.0, "previous_team": missing},
        position="TE",
        target_name="games_active",
    )

    assert len(explanation["top_factors"]) == 1
    factor = explanation["top_factors"][0]
    assert factor["feature"] == "age"
    assert factor["player_value"] is None
    assert factor["position_reference_value"] == 28.0
    assert factor["prediction_delta"] == -28.0
    json.dumps(explanation, allow_nan=False)


def test_rookie_fallback_is_transparent_and_explicitly_unvalidated() -> None:
    explanation = explain_heuristic_fallback(
        heuristic_name="position_shrinkage",
        position="RB",
        target_name="fantasy_points_total",
        prediction_value=88.5,
        reason="No cutoff-safe historical features exist for this player.",
        is_rookie=True,
        supporting_values={"position_prior": 88.5},
    )

    assert explanation["prediction_status"] == "rookie_heuristic_fallback_unvalidated"
    assert explanation["validation_status"] == "not_validated_for_rookies"
    assert explanation["uncertainty_status"] == "unvalidated_uncalibrated"
    assert explanation["learned_model_used"] is False
    assert "historical rookie" in explanation["interpretation"]
    json.dumps(explanation, allow_nan=False)
