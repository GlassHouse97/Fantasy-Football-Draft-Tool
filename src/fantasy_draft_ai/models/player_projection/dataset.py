"""Strict extraction and target masking for Phase 4 model matrices."""

from __future__ import annotations

import hashlib
import json
import math
from collections.abc import Iterable, Mapping
from dataclasses import dataclass
from typing import Any

import pandas as pd

from fantasy_draft_ai.models.player_projection.config import (
    PlayerModelConfig,
    canonical_json,
)

_TARGET_PREFIX = "target__"
_KEY_COLUMNS = (
    "player_id",
    "prediction_season",
    "position",
    "is_rookie",
    "experience_group",
)


@dataclass(frozen=True)
class PlayerSeasonModelRow:
    """One validated Phase 3 row before strict predictor extraction."""

    player_id: str
    prediction_season: int
    position: str
    features: Mapping[str, Any]
    targets: Mapping[str, Any] | None = None

    @classmethod
    def from_json_payloads(
        cls,
        *,
        player_id: str,
        prediction_season: int,
        position: str,
        feature_payload: str,
        target_payload: str | None,
    ) -> PlayerSeasonModelRow:
        """Parse the JSON payloads returned by the canonical DuckDB join."""

        features = json.loads(feature_payload)
        targets = json.loads(target_payload) if target_payload is not None else None
        if not isinstance(features, dict):
            raise ValueError("feature_payload must decode to a JSON object.")
        if targets is not None and not isinstance(targets, dict):
            raise ValueError("target_payload must decode to a JSON object.")
        return cls(
            player_id=player_id,
            prediction_season=prediction_season,
            position=position,
            features=features,
            targets=targets,
        )


@dataclass(frozen=True)
class ModelMatrix:
    """A routed model matrix whose targets were never imputed."""

    X: pd.DataFrame
    keys: pd.DataFrame
    position: str
    target_name: str | None
    y: pd.Series | None

    @property
    def prediction_seasons(self) -> tuple[int, ...]:
        return tuple(sorted(int(value) for value in self.keys["prediction_season"].unique()))

    def __len__(self) -> int:
        return len(self.X)


@dataclass(frozen=True)
class PlayerModelDataset:
    """Deterministically sorted Phase 4 rows under one feature contract."""

    frame: pd.DataFrame
    feature_columns: tuple[str, ...]
    feature_fingerprint: str
    config: PlayerModelConfig

    def training_matrix(
        self,
        *,
        position: str,
        target_name: str,
        training_seasons: Iterable[int],
    ) -> ModelMatrix:
        """Return known targets for one position, always excluding rookies."""

        routed_position = self._validated_position(position)
        routed_target = self._validated_target(target_name)
        seasons = tuple(sorted(set(int(season) for season in training_seasons)))
        if not seasons:
            raise ValueError("At least one training season is required.")
        target_column = f"{_TARGET_PREFIX}{routed_target}"
        mask = (
            self.frame["position"].eq(routed_position)
            & self.frame["prediction_season"].isin(seasons)
            & ~self.frame["is_rookie"]
            & self.frame[target_column].notna()
        )
        selected = self.frame.loc[mask].copy()
        if selected.empty:
            raise ValueError(
                f"No non-rookie {routed_position} rows have target {routed_target!r} "
                f"in seasons {seasons}."
            )
        selected.sort_values(["prediction_season", "player_id"], kind="mergesort", inplace=True)
        selected.reset_index(drop=True, inplace=True)
        if bool(selected["is_rookie"].any()):
            raise RuntimeError("Rookie rows reached a training matrix.")
        y = selected[target_column].astype(float).rename(routed_target)
        if bool(y.isna().any()):
            raise RuntimeError("Target masking left a null outcome in the training matrix.")
        return ModelMatrix(
            X=selected.loc[:, self.feature_columns].copy(),
            keys=selected.loc[:, _KEY_COLUMNS].copy(),
            position=routed_position,
            target_name=routed_target,
            y=y,
        )

    def prediction_matrix(
        self,
        *,
        position: str,
        prediction_season: int,
        include_rookies: bool = False,
    ) -> ModelMatrix:
        """Return live-like predictors; rookies require an explicit fallback route."""

        routed_position = self._validated_position(position)
        mask = self.frame["position"].eq(routed_position) & self.frame["prediction_season"].eq(
            int(prediction_season)
        )
        if not include_rookies:
            mask &= ~self.frame["is_rookie"]
        selected = self.frame.loc[mask].copy()
        if selected.empty:
            raise ValueError(f"No {routed_position} prediction rows exist for {prediction_season}.")
        selected.sort_values(["player_id"], kind="mergesort", inplace=True)
        selected.reset_index(drop=True, inplace=True)
        return ModelMatrix(
            X=selected.loc[:, self.feature_columns].copy(),
            keys=selected.loc[:, _KEY_COLUMNS].copy(),
            position=routed_position,
            target_name=None,
            y=None,
        )

    def rookie_keys(self, *, position: str, prediction_season: int) -> pd.DataFrame:
        """Return rows that orchestration must send to the transparent fallback."""

        routed_position = self._validated_position(position)
        mask = (
            self.frame["position"].eq(routed_position)
            & self.frame["prediction_season"].eq(int(prediction_season))
            & self.frame["is_rookie"]
        )
        return (
            self.frame.loc[mask, _KEY_COLUMNS]
            .sort_values(["player_id"], kind="mergesort")
            .reset_index(drop=True)
        )

    def _validated_position(self, position: str) -> str:
        normalized = position.strip().upper()
        if normalized not in self.config.positions:
            raise ValueError(f"Unsupported model position: {position!r}.")
        return normalized

    def _validated_target(self, target_name: str) -> str:
        if target_name not in self.config.targets:
            raise ValueError(f"Unsupported model target: {target_name!r}.")
        return target_name


def prepare_model_dataset(
    rows: Iterable[PlayerSeasonModelRow],
    config: PlayerModelConfig | None = None,
) -> PlayerModelDataset:
    """Extract only reviewed predictors and calculate a target-independent hash."""

    resolved = config or PlayerModelConfig()
    feature_columns = (*resolved.numeric_features, *resolved.categorical_features)
    normalized_rows: list[dict[str, Any]] = []
    seen_keys: set[tuple[str, int]] = set()
    for row in rows:
        player_id = row.player_id.strip()
        if not player_id:
            raise ValueError("player_id cannot be empty.")
        key = (player_id, int(row.prediction_season))
        if key in seen_keys:
            raise ValueError(f"Duplicate player-season model key: {key}.")
        seen_keys.add(key)
        position = row.position.strip().upper()
        if position not in resolved.positions:
            raise ValueError(f"Unsupported model position: {row.position!r}.")
        if "is_rookie" not in row.features:
            raise ValueError(f"Feature row {key} does not declare is_rookie.")
        is_rookie = _boolean_value(row.features["is_rookie"], "is_rookie")
        history_seasons = _numeric_value(row.features.get("history_seasons"), "history_seasons")
        experience_group = (
            "rookie"
            if is_rookie
            else "sparse"
            if math.isnan(history_seasons) or history_seasons < 2
            else "veteran"
        )
        normalized: dict[str, Any] = {
            "player_id": player_id,
            "prediction_season": int(row.prediction_season),
            "position": position,
            "is_rookie": is_rookie,
            "experience_group": experience_group,
        }
        for feature in resolved.numeric_features:
            normalized[feature] = (
                float(row.prediction_season)
                if feature == "prediction_season"
                else _numeric_value(row.features.get(feature), feature)
            )
        for feature in resolved.categorical_features:
            normalized[feature] = _categorical_value(row.features.get(feature))
        targets = row.targets or {}
        for target in resolved.targets:
            normalized[f"{_TARGET_PREFIX}{target}"] = _optional_target(targets.get(target), target)
        normalized_rows.append(normalized)
    if not normalized_rows:
        raise ValueError("No player-season rows were supplied.")
    frame = pd.DataFrame(normalized_rows)
    frame.sort_values(
        ["prediction_season", "position", "player_id"], kind="mergesort", inplace=True
    )
    frame.reset_index(drop=True, inplace=True)
    feature_fingerprint = _selected_feature_fingerprint(frame, resolved, feature_columns)
    return PlayerModelDataset(
        frame=frame,
        feature_columns=feature_columns,
        feature_fingerprint=feature_fingerprint,
        config=resolved,
    )


def _selected_feature_fingerprint(
    frame: pd.DataFrame,
    config: PlayerModelConfig,
    feature_columns: tuple[str, ...],
) -> str:
    records: list[dict[str, Any]] = []
    for row in frame.loc[:, ["player_id", "position", "is_rookie", *feature_columns]].to_dict(
        orient="records"
    ):
        records.append({str(name): _json_value(value) for name, value in row.items()})
    payload = {
        "model_feature_fingerprint": config.feature_contract_fingerprint(),
        "rows": records,
    }
    return hashlib.sha256(canonical_json(payload).encode("utf-8")).hexdigest()


def _numeric_value(value: Any, field: str) -> float:
    if value is None:
        return math.nan
    if isinstance(value, bool):
        return float(value)
    try:
        number = float(value)
    except (TypeError, ValueError) as exc:
        raise ValueError(f"Feature {field!r} must be numeric or null.") from exc
    if not math.isfinite(number):
        raise ValueError(f"Feature {field!r} must be finite when present.")
    return number


def _boolean_value(value: Any, field: str) -> bool:
    if isinstance(value, bool):
        return value
    if value in (0, 1):
        return bool(value)
    raise ValueError(f"Feature {field!r} must be a boolean.")


def _categorical_value(value: Any) -> str | float:
    if value is None:
        return math.nan
    normalized = str(value).strip().upper()
    return normalized if normalized else math.nan


def _optional_target(value: Any, target: str) -> float:
    if value is None:
        return math.nan
    if isinstance(value, bool):
        raise ValueError(f"Target {target!r} cannot be boolean.")
    try:
        number = float(value)
    except (TypeError, ValueError) as exc:
        raise ValueError(f"Target {target!r} must be numeric or null.") from exc
    if not math.isfinite(number):
        raise ValueError(f"Target {target!r} must be finite when present.")
    return number


def _json_value(value: Any) -> Any:
    if pd.isna(value):
        return None
    if hasattr(value, "item"):
        return value.item()
    return value
