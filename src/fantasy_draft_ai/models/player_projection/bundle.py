"""Serializable fitted-model bundle with its empirical interval calibration."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from fantasy_draft_ai.models.player_projection.uncertainty import (
    PredictionInterval,
    ResidualCalibration,
)


@dataclass(frozen=True)
class ProjectionModelArtifact:
    """One production estimator and the metadata needed to reproduce its output."""

    pipeline: Any
    calibration: ResidualCalibration
    model_id: str
    run_id: str
    family: str
    position: str
    target_name: str
    feature_names: tuple[str, ...]
    training_seasons: tuple[int, ...]
    lineage: dict[str, str]

    def predict(self, features: Any) -> Any:
        """Delegate point prediction to the fitted scikit-learn pipeline."""

        return self.pipeline.predict(features)

    def interval(self, point_prediction: float) -> PredictionInterval:
        """Apply the persisted signed-residual calibration."""

        return self.calibration.interval(point_prediction)
