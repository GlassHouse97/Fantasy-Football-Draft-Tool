"""End-to-end, chronology-safe Phase 4 player projection training."""

from __future__ import annotations

import json
import math
import os
import tempfile
from collections import defaultdict
from dataclasses import dataclass
from datetime import UTC, datetime
from importlib.metadata import PackageNotFoundError, version
from pathlib import Path
from typing import Any, cast
from uuid import uuid4

import numpy as np
import pandas as pd

from fantasy_draft_ai.config import AppConfig
from fantasy_draft_ai.data.manifests import sha256_file
from fantasy_draft_ai.models.player_projection.artifacts import (
    ArtifactMetadata,
    persist_verified_model,
)
from fantasy_draft_ai.models.player_projection.bundle import ProjectionModelArtifact
from fantasy_draft_ai.models.player_projection.config import (
    HIST_GRADIENT_BOOSTING,
    RIDGE,
    ModelFamily,
    PlayerModelConfig,
    build_run_fingerprint,
    canonical_json,
)
from fantasy_draft_ai.models.player_projection.dataset import (
    ModelMatrix,
    PlayerModelDataset,
    prepare_model_dataset,
)
from fantasy_draft_ai.models.player_projection.evaluation import (
    assign_projection_tiers,
    interval_metrics,
    regression_metrics,
    segment_regression_metrics,
    select_champions,
)
from fantasy_draft_ai.models.player_projection.explanations import (
    explain_heuristic_fallback,
    explain_player_prediction,
    hist_gradient_boosting_permutation_importance,
    numeric_partial_dependence,
    ridge_coefficient_importance,
)
from fantasy_draft_ai.models.player_projection.repository import (
    FrozenProjectionContract,
    persist_projection_run,
    projection_integrity_issues,
    read_baseline_predictions,
    read_frozen_projection_contract,
)
from fantasy_draft_ai.models.player_projection.tuning import TuningResult, tune_model
from fantasy_draft_ai.models.player_projection.uncertainty import (
    ResidualCalibration,
    fit_residual_calibration,
)
from fantasy_draft_ai.rules.models import LeagueRules

MODEL_FAMILIES: tuple[ModelFamily, ...] = (RIDGE, HIST_GRADIENT_BOOSTING)
MODEL_CARD_DIRECTORY = Path("docs/model_cards/phase4")
DEFAULT_REPORT_MARKDOWN = Path("docs/PHASE_4_MODEL_EVALUATION.md")
DEFAULT_REPORT_JSON = Path("docs/PHASE_4_MODEL_EVALUATION.json")
DEFAULT_PLOT_DIRECTORY = Path("docs/images/phase4")
DEFAULT_ARTIFACT_ROOT = Path("models/artifacts")
AUTHORITATIVE_PUBLICATION_ROOT = Path("models/reports")
REGISTRY_MIRROR_PATH = Path("models/registry.json")


@dataclass(frozen=True)
class PublicationAttempt:
    """Unique filesystem namespace for one attempt at a deterministic model run."""

    run_id: str
    publication_id: str

    @property
    def relative_directory(self) -> Path:
        return Path(self.run_id) / self.publication_id

    @property
    def artifact_directory(self) -> Path:
        return self.relative_directory

    @property
    def model_card_directory(self) -> Path:
        return MODEL_CARD_DIRECTORY / self.relative_directory

    @property
    def plot_directory(self) -> Path:
        return DEFAULT_PLOT_DIRECTORY / self.relative_directory

    @property
    def report_directory(self) -> Path:
        return AUTHORITATIVE_PUBLICATION_ROOT / self.relative_directory


def _new_publication_attempt(run_id: str) -> PublicationAttempt:
    """Create a collision-resistant namespace without changing deterministic run identity."""

    normalized_run_id = run_id.strip()
    if not normalized_run_id or Path(normalized_run_id).name != normalized_run_id:
        raise ValueError("A publication attempt requires a safe, non-empty run ID.")
    return PublicationAttempt(
        run_id=normalized_run_id,
        publication_id=f"attempt-{uuid4().hex}",
    )


@dataclass(frozen=True)
class PlayerModelTrainingResult:
    """Outcome returned by the CLI after a complete or safely reused run."""

    committed: bool
    reused: bool
    run_id: str
    model_rows: int
    prediction_rows: int
    evaluated_rows: int
    live_prediction_rows: int
    champion_rows: int
    board_rows: int
    report_path: Path | None
    issues: tuple[str, ...]
    report: dict[str, Any]

    def render(self) -> str:
        succeeded = self.committed or self.reused
        status = (
            "PASSED WITH WARNINGS"
            if succeeded and self.issues
            else "PASSED"
            if succeeded
            else "FAILED"
        )
        transaction = (
            "REUSED" if self.reused else "COMMITTED" if self.committed else "NOT COMMITTED"
        )
        lines = [
            f"Phase 4 player-model training: {status}",
            f"Warehouse transaction: {transaction}",
            f"Run ID: {self.run_id or '<none>'}",
            f"Registered models: {self.model_rows}",
            f"Prediction rows: {self.prediction_rows}",
            f"Evaluated rows: {self.evaluated_rows}",
            f"Live prediction rows: {self.live_prediction_rows}",
            f"Champions: {self.champion_rows}",
            f"2026 board rows: {self.board_rows}",
        ]
        lines.extend(f"- {issue}" for issue in self.issues)
        if self.report_path is not None:
            lines.append(f"Evaluation report: {self.report_path}")
        return "\n".join(lines)


@dataclass
class FinalRoute:
    model_id: str
    family: str
    position: str
    target_name: str
    tuning: TuningResult
    calibration: ResidualCalibration
    training_matrix: ModelMatrix
    live_matrix: ModelMatrix
    artifact: ProjectionModelArtifact
    artifact_metadata: ArtifactMetadata
    global_importance: list[dict[str, Any]]
    feature_responses: list[dict[str, Any]]
    explanation_features: tuple[str, ...]
    position_reference: dict[str, Any]


def train_player_projection_models(
    config: AppConfig,
    rules: LeagueRules,
    *,
    model_config: PlayerModelConfig | None = None,
    validation_start_season: int = 2020,
    test_season: int = 2025,
    report_markdown_path: Path = DEFAULT_REPORT_MARKDOWN,
    report_json_path: Path = DEFAULT_REPORT_JSON,
    artifact_root: Path = DEFAULT_ARTIFACT_ROOT,
    force: bool = False,
) -> PlayerModelTrainingResult:
    """Train, compare, explain, persist, and report the Phase 4 model ladder."""

    try:
        resolved_model_config = model_config or PlayerModelConfig(
            random_seed=config.project.random_seed
        )
        contract = read_frozen_projection_contract(
            config,
            scoring_ruleset_fingerprint=rules.fingerprint(),
            validation_start_season=validation_start_season,
            test_season=test_season,
        )
        dataset = prepare_model_dataset(contract.rows, resolved_model_config)
        run_fingerprint = build_run_fingerprint(
            resolved_model_config,
            feature_data_fingerprint=contract.feature_data_fingerprint,
            target_data_fingerprint=contract.target_data_fingerprint,
            build_fingerprint=contract.build_fingerprint,
            scoring_ruleset_fingerprint=contract.scoring_ruleset_fingerprint,
            baseline_report_fingerprint=contract.baseline_report_fingerprint,
        )
        run_id = f"phase4-{run_fingerprint[:20]}"
        if not force:
            reused = _reuse_current_run(
                config,
                run_id,
                report_markdown_path,
                report_json_path,
            )
            if reused is not None:
                return reused
        baseline_predictions = read_baseline_predictions(config, contract)
        return _execute_training(
            config,
            contract,
            dataset,
            resolved_model_config,
            run_id=run_id,
            run_fingerprint=run_fingerprint,
            baseline_predictions=baseline_predictions,
            report_markdown_path=report_markdown_path,
            report_json_path=report_json_path,
            artifact_root=artifact_root,
        )
    except Exception as exc:
        return _failure(str(exc))


def _execute_training(
    app_config: AppConfig,
    contract: FrozenProjectionContract,
    dataset: PlayerModelDataset,
    model_config: PlayerModelConfig,
    *,
    run_id: str,
    run_fingerprint: str,
    baseline_predictions: list[dict[str, Any]],
    report_markdown_path: Path,
    report_json_path: Path,
    artifact_root: Path,
) -> PlayerModelTrainingResult:
    publication = _new_publication_attempt(run_id)
    learned_predictions: list[dict[str, Any]] = []
    test_routes: dict[tuple[str, str, str], tuple[TuningResult, ModelMatrix]] = {}
    folds = tuple(contract.folds)
    for fold in folds:
        evaluation_season = int(fold["evaluation_season"])
        training_seasons = tuple(int(value) for value in fold["training_seasons"])
        for position in model_config.positions:
            evaluation_matrix = dataset.prediction_matrix(
                position=position,
                prediction_season=evaluation_season,
            )
            for target_name in model_config.targets:
                training_matrix = dataset.training_matrix(
                    position=position,
                    target_name=target_name,
                    training_seasons=training_seasons,
                )
                for family in MODEL_FAMILIES:
                    tuning = tune_model(
                        training_matrix,
                        family=family,
                        config=model_config,
                    )
                    calibration = fit_residual_calibration(
                        tuning.out_of_fold_predictions,
                        target_name=target_name,
                        prediction_season=evaluation_season,
                        config=model_config,
                    )
                    point_predictions = np.asarray(
                        tuning.pipeline.predict(evaluation_matrix.X), dtype=float
                    )
                    learned_predictions.extend(
                        _prediction_records(
                            dataset,
                            contract,
                            model_config,
                            run_id=run_id,
                            matrix=evaluation_matrix,
                            target_name=target_name,
                            family=family,
                            point_predictions=point_predictions,
                            calibration=calibration,
                            scope=str(fold["label"]),
                            fold_label=str(fold["label"]),
                            training_max_season=max(training_seasons),
                        )
                    )
                    if str(fold["label"]) == "test":
                        test_routes[position, target_name, family] = (
                            tuning,
                            evaluation_matrix,
                        )

    final_routes: dict[tuple[str, str, str], FinalRoute] = {}
    artifact_root_absolute = _resolve_project_path(app_config.project_root, artifact_root)
    final_training_seasons = tuple(
        sorted(
            int(value)
            for value in dataset.frame.loc[
                dataset.frame["prediction_season"].le(contract.test_season),
                "prediction_season",
            ].unique()
        )
    )
    for position in model_config.positions:
        live_matrix = dataset.prediction_matrix(
            position=position,
            prediction_season=app_config.project.prediction_season,
        )
        for target_name in model_config.targets:
            training_matrix = dataset.training_matrix(
                position=position,
                target_name=target_name,
                training_seasons=final_training_seasons,
            )
            for family in MODEL_FAMILIES:
                tuning = tune_model(training_matrix, family=family, config=model_config)
                calibration = fit_residual_calibration(
                    tuning.out_of_fold_predictions,
                    target_name=target_name,
                    prediction_season=app_config.project.prediction_season,
                    config=model_config,
                )
                point_predictions = np.asarray(tuning.pipeline.predict(live_matrix.X), dtype=float)
                learned_predictions.extend(
                    _prediction_records(
                        dataset,
                        contract,
                        model_config,
                        run_id=run_id,
                        matrix=live_matrix,
                        target_name=target_name,
                        family=family,
                        point_predictions=point_predictions,
                        calibration=calibration,
                        scope="live",
                        fold_label=None,
                        training_max_season=max(final_training_seasons),
                    )
                )
                model_id = _model_id(run_id, position, target_name, family)
                lineage = _lineage(contract, model_config)
                bundle = ProjectionModelArtifact(
                    pipeline=tuning.pipeline,
                    calibration=calibration,
                    model_id=model_id,
                    run_id=run_id,
                    family=family,
                    position=position,
                    target_name=target_name,
                    feature_names=dataset.feature_columns,
                    training_seasons=final_training_seasons,
                    lineage=lineage,
                )
                artifact_relative = (
                    publication.artifact_directory / position / target_name / f"{family}.joblib"
                )
                verification_rows = live_matrix.X.iloc[: min(25, len(live_matrix.X))]
                artifact_metadata = persist_verified_model(
                    bundle,
                    artifact_root_absolute,
                    artifact_relative,
                    verification_rows,
                )
                final_routes[position, target_name, family] = FinalRoute(
                    model_id=model_id,
                    family=family,
                    position=position,
                    target_name=target_name,
                    tuning=tuning,
                    calibration=calibration,
                    training_matrix=training_matrix,
                    live_matrix=live_matrix,
                    artifact=bundle,
                    artifact_metadata=artifact_metadata,
                    global_importance=[],
                    feature_responses=[],
                    explanation_features=(),
                    position_reference=_position_reference(training_matrix.X),
                )

    comparison_records = _comparison_records(
        baseline_predictions,
        learned_predictions,
        evaluation_seasons={int(fold["evaluation_season"]) for fold in folds},
    )
    selection = select_champions(
        comparison_records,
        validation_seasons=contract.validation_seasons,
        test_season=contract.test_season,
        n_bootstrap=2_000,
        seed=model_config.random_seed,
        draft_relevance_policy=model_config.draft_relevance_policy,
    )
    # Explanations are deliberately computed only after validation has fixed the
    # champions. They cannot influence selection or expose the test outcome early.
    for route_key in sorted(final_routes):
        route = final_routes[route_key]
        _, test_matrix = test_routes[route_key]
        importance, responses, explanation_features = _global_explanations(
            route.family,
            route.tuning,
            test_matrix,
            dataset,
            route.target_name,
            model_config,
        )
        route.global_importance = importance
        route.feature_responses = responses
        route.explanation_features = explanation_features
    detailed_metrics, interval_metric_records = _detailed_metrics(
        comparison_records,
        learned_predictions,
        contract,
    )
    champion_lookup = {
        (str(row["position"]), str(row["target_name"])): row for row in selection["champions"]
    }
    board = _build_live_board(
        dataset,
        contract,
        model_config,
        app_config,
        run_id=run_id,
        learned_predictions=learned_predictions,
        baseline_predictions=baseline_predictions,
        champions=champion_lookup,
        final_routes=final_routes,
    )
    trained_at = datetime.now(UTC).replace(microsecond=0)
    diagnostics = _diagnostic_records(
        detailed_metrics,
        interval_metric_records,
        comparison_records,
        learned_predictions,
        final_routes,
        contract,
    )

    from fantasy_draft_ai.models.player_projection.reporting import (
        write_diagnostic_svgs,
        write_evaluation_report,
        write_model_card,
    )

    plot_paths = write_diagnostic_svgs(
        app_config.project_root,
        diagnostics,
        output_directory=publication.plot_directory,
    )
    plot_files = {
        name: {
            "path": path,
            "sha256": sha256_file(_resolve_project_path(app_config.project_root, Path(path))),
        }
        for name, path in sorted(plot_paths.items())
    }
    package_versions = _package_versions()
    model_records: list[dict[str, Any]] = []
    candidate_metric_lookup = {
        (
            str(row["position"]),
            str(row["target_name"]),
            str(row["candidate_source"]),
            str(row["candidate_name"]),
        ): row
        for row in selection["candidate_metrics"]
    }
    for route_key in sorted(final_routes):
        route = final_routes[route_key]
        candidate_metrics = candidate_metric_lookup[
            route.position,
            route.target_name,
            "learned",
            route.family,
        ]
        best_baseline = champion_lookup[route.position, route.target_name][
            "reference_baseline_name"
        ]
        baseline_metrics = candidate_metric_lookup[
            route.position,
            route.target_name,
            "baseline",
            best_baseline,
        ]
        route_champion = champion_lookup[route.position, route.target_name]
        route_interval_metrics = [
            row
            for row in interval_metric_records
            if row["position"] == route.position
            and row["target_name"] == route.target_name
            and row["candidate_name"] == route.family
        ]
        artifact_project_path = (
            artifact_root / Path(route.artifact_metadata.relative_path)
        ).as_posix()
        card_payload = _model_card_payload(
            route,
            contract,
            model_config,
            trained_at,
            publication.publication_id,
            candidate_metrics,
            baseline_metrics,
            route_champion,
            route_interval_metrics,
            artifact_project_path,
            plot_paths,
        )
        card_result = write_model_card(
            app_config.project_root,
            card_payload,
            output_path=publication.model_card_directory / f"{route.model_id}.md",
        )
        model_records.append(
            {
                "model_id": route.model_id,
                "run_id": run_id,
                "model_family": route.family,
                "target_name": route.target_name,
                "position": route.position,
                "training_seasons": canonical_json(list(route.tuning.training_seasons)),
                "training_rows": len(route.training_matrix),
                "feature_names": canonical_json(list(dataset.feature_columns)),
                "categorical_feature_names": canonical_json(
                    list(model_config.categorical_features)
                ),
                "hyperparameters": canonical_json(dict(route.tuning.best_parameters)),
                "uncertainty_method": "training_only_signed_oof_residual_quantiles",
                "artifact_path": artifact_project_path,
                "artifact_sha256": route.artifact_metadata.sha256,
                "artifact_size_bytes": route.artifact_metadata.size_bytes,
                "model_card_path": card_result["model_card_path"],
                "model_card_sha256": card_result["model_card_sha256"],
                "package_versions": canonical_json(package_versions),
            }
        )

    champion_records = _champion_records(
        selection["champions"],
        final_routes,
        run_id,
    )
    report = _report_payload(
        contract,
        dataset,
        model_config,
        run_id,
        publication.publication_id,
        run_fingerprint,
        trained_at,
        learned_predictions,
        model_records,
        board,
        selection,
        detailed_metrics,
        interval_metric_records,
        final_routes,
        plot_paths,
    )
    publication_directory = publication.report_directory
    report_files = write_evaluation_report(
        app_config.project_root,
        report,
        json_path=publication_directory / "evaluation.json",
        markdown_path=publication_directory / "evaluation.md",
    )
    report_fingerprint = str(report_files["report_fingerprint"])
    report["report_fingerprint"] = report_fingerprint
    for row in board:
        row["evaluation_report_fingerprint"] = report_fingerprint
    registry_metadata = _write_model_registry(
        app_config.project_root,
        run_id=run_id,
        publication_id=publication.publication_id,
        report_fingerprint=report_fingerprint,
        models=model_records,
        champions=champion_records,
        output_path=publication_directory / "registry.json",
    )
    evaluated_rows = sum(row["actual_value"] is not None for row in learned_predictions)
    live_prediction_rows = sum(row["prediction_scope"] == "live" for row in learned_predictions)
    candidate_rows = len(selection["candidate_metrics"])
    lineage = _lineage(contract, model_config)
    run_record = {
        "run_id": run_id,
        **lineage,
        "split_seasons": canonical_json(list(folds)),
        "feature_rows": contract.feature_rows,
        "target_rows": contract.target_rows,
        "training_rows": sum(row["training_rows"] for row in model_records),
        "prediction_rows": len(learned_predictions),
        "evaluated_rows": evaluated_rows,
        "live_prediction_rows": live_prediction_rows,
        "candidate_rows": candidate_rows,
        "model_rows": len(model_records),
        "champion_rows": len(champion_records),
        "status": "validating",
        "trained_at": trained_at,
        "run_payload": canonical_json(
            {
                "schema_version": "1.0",
                "publication_id": publication.publication_id,
                "run_fingerprint": run_fingerprint,
                "selected_feature_data_fingerprint": dataset.feature_fingerprint,
                "report_fingerprint": report_fingerprint,
                "report_files": report_files,
                "registry": registry_metadata,
                "plot_paths": plot_paths,
                "plot_files": plot_files,
                "rookie_policy": "transparent_heuristic_fallback_unvalidated",
            }
        ),
    }
    evaluation_record = {
        "report_fingerprint": report_fingerprint,
        "run_id": run_id,
        **lineage,
        "prediction_rows": len(learned_predictions),
        "evaluated_rows": evaluated_rows,
        "live_prediction_rows": live_prediction_rows,
        "candidate_rows": candidate_rows,
        "champion_rows": len(champion_records),
        "report_payload": canonical_json(report),
    }
    persist_projection_run(
        app_config,
        run=run_record,
        models=model_records,
        predictions=learned_predictions,
        champions=champion_records,
        evaluation=evaluation_record,
        board=board,
    )
    registered_outputs = json.loads(str(run_record["run_payload"]))
    return _committed_training_result(
        app_config,
        run_id=run_id,
        model_rows=len(model_records),
        prediction_rows=len(learned_predictions),
        evaluated_rows=evaluated_rows,
        live_prediction_rows=live_prediction_rows,
        champion_rows=len(champion_records),
        board_rows=len(board),
        report=report,
        registered_outputs=registered_outputs,
        report_markdown_path=report_markdown_path,
        report_json_path=report_json_path,
    )


def _prediction_records(
    dataset: PlayerModelDataset,
    contract: FrozenProjectionContract,
    model_config: PlayerModelConfig,
    *,
    run_id: str,
    matrix: ModelMatrix,
    target_name: str,
    family: str,
    point_predictions: np.ndarray[Any, np.dtype[np.float64]],
    calibration: ResidualCalibration,
    scope: str,
    fold_label: str | None,
    training_max_season: int,
) -> list[dict[str, Any]]:
    if len(point_predictions) != len(matrix):
        raise RuntimeError("A fitted model returned the wrong number of predictions.")
    if not bool(np.isfinite(point_predictions).all()):
        raise RuntimeError("A fitted model produced a non-finite prediction.")
    lookup = dataset.frame.set_index(["player_id", "prediction_season"], drop=False)
    lineage = _lineage(contract, model_config)
    records: list[dict[str, Any]] = []
    for offset, (_, key) in enumerate(matrix.keys.iterrows()):
        player_id = str(key["player_id"])
        prediction_season = int(key["prediction_season"])
        source = cast(pd.Series, lookup.loc[(player_id, prediction_season)])
        interval = calibration.interval(float(point_predictions[offset]))
        actual = _optional_float(source[f"target__{target_name}"])
        actual_games = _optional_float(source["target__games_active"])
        experience = _optional_int(source["nfl_experience_years"])
        records.append(
            {
                "run_id": run_id,
                "player_id": player_id,
                "prediction_season": prediction_season,
                "position": str(key["position"]),
                "target_name": target_name,
                "model_family": family,
                "prediction_scope": scope,
                "fold_label": fold_label,
                "training_max_season": training_max_season,
                # This is the residual-adjusted central estimate shown to users.
                # Keeping it equal to P50 makes champion scoring and operational
                # projections evaluate the same quantity.
                "predicted_value": interval.p50,
                "p10": interval.p10,
                "p50": interval.p50,
                "p90": interval.p90,
                "actual_value": actual,
                "actual_games_active": actual_games,
                "experience": experience,
                "experience_group": str(key["experience_group"]),
                **lineage,
            }
        )
    return records


def _global_explanations(
    family: str,
    final_tuning: TuningResult,
    test_matrix: ModelMatrix,
    dataset: PlayerModelDataset,
    target_name: str,
    config: PlayerModelConfig,
) -> tuple[list[dict[str, Any]], list[dict[str, Any]], tuple[str, ...]]:
    if family == RIDGE:
        importance = ridge_coefficient_importance(final_tuning.pipeline, top_n=20)
        explanation_features = _ridge_input_features(importance, dataset.feature_columns)
        return importance, [], explanation_features[:8]
    target_lookup = dataset.frame.set_index(["player_id", "prediction_season"])[
        f"target__{target_name}"
    ]
    actual = np.asarray(
        [
            target_lookup.loc[str(row["player_id"]), int(row["prediction_season"])]
            for _, row in test_matrix.keys.iterrows()
        ],
        dtype=float,
    )
    valid = np.isfinite(actual)
    if not bool(valid.any()):
        raise RuntimeError("The HGB test fold has no evaluable outcomes for explanation.")
    importance = hist_gradient_boosting_permutation_importance(
        final_tuning.pipeline,
        test_matrix.X.loc[valid],
        actual[valid],
        n_repeats=5,
        random_seed=config.random_seed,
        top_n=20,
    )
    explanation_scope = (
        "registered_final_artifact_descriptive_on_"
        f"{max(test_matrix.prediction_seasons)}_training_rows"
    )
    for row in importance:
        row["explanation_scope"] = explanation_scope
    explanation_features = tuple(str(row["feature"]) for row in importance[:8])
    response_features = [
        str(row["feature"]) for row in importance if str(row["feature"]) in config.numeric_features
    ][:3]
    responses: list[dict[str, Any]] = []
    if response_features:
        try:
            responses = numeric_partial_dependence(
                final_tuning.pipeline,
                test_matrix.X.loc[valid],
                response_features,
                grid_resolution=12,
            )
        except ValueError:
            responses = []
    for response in responses:
        response["explanation_scope"] = explanation_scope
    return importance, responses, explanation_features


def _ridge_input_features(
    importance: list[dict[str, Any]], feature_columns: tuple[str, ...]
) -> tuple[str, ...]:
    selected: list[str] = []
    for row in importance:
        transformed = str(row["feature"])
        for feature in feature_columns:
            if transformed == feature or transformed.startswith(
                (f"numeric__{feature}", f"categorical__{feature}_")
            ):
                if feature not in selected:
                    selected.append(feature)
                break
    return tuple(selected)


def _position_reference(frame: pd.DataFrame) -> dict[str, Any]:
    reference: dict[str, Any] = {}
    for column in frame.columns:
        series = frame[column]
        if pd.api.types.is_numeric_dtype(series):
            finite = pd.to_numeric(series, errors="coerce").dropna()
            reference[str(column)] = float(finite.median()) if not finite.empty else math.nan
        else:
            modes = series.dropna().mode()
            reference[str(column)] = str(modes.iloc[0]) if not modes.empty else math.nan
    return reference


def _comparison_records(
    baseline_predictions: list[dict[str, Any]],
    learned_predictions: list[dict[str, Any]],
    *,
    evaluation_seasons: set[int],
) -> list[dict[str, Any]]:
    records = [
        {
            **row,
            "candidate_source": "baseline",
            "candidate_name": str(row["baseline_name"]),
        }
        for row in baseline_predictions
        if int(row["prediction_season"]) in evaluation_seasons
    ]
    records.extend(
        {
            **row,
            "candidate_source": "learned",
            "candidate_name": str(row["model_family"]),
        }
        for row in learned_predictions
        if int(row["prediction_season"]) in evaluation_seasons
    )
    return records


def _detailed_metrics(
    comparison_records: list[dict[str, Any]],
    learned_predictions: list[dict[str, Any]],
    contract: FrozenProjectionContract,
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    detailed: list[dict[str, Any]] = []
    interval_records: list[dict[str, Any]] = []
    grouped: dict[tuple[str, str, str, str], list[dict[str, Any]]] = defaultdict(list)
    for row in comparison_records:
        grouped[
            str(row["position"]),
            str(row["target_name"]),
            str(row["candidate_source"]),
            str(row["candidate_name"]),
        ].append(dict(row))
    for key in sorted(grouped):
        position, target_name, source, candidate_name = key
        rows = grouped[key]
        for season in sorted({int(row["prediction_season"]) for row in rows}):
            season_rows = [row for row in rows if int(row["prediction_season"]) == season]
            tiers = assign_projection_tiers(
                [row["predicted_value"] for row in season_rows],
                entity_ids=[row["player_id"] for row in season_rows],
            )
            for row, tier in zip(season_rows, tiers, strict=True):
                row["projection_tier"] = tier
        for scope, seasons in (
            ("validation", set(contract.validation_seasons)),
            ("test", {contract.test_season}),
        ):
            scope_rows = [row for row in rows if int(row["prediction_season"]) in seasons]
            metrics = regression_metrics(
                [row["actual_value"] for row in scope_rows],
                [row["predicted_value"] for row in scope_rows],
                top_n=None,
                entity_ids=[f"{row['prediction_season']}:{row['player_id']}" for row in scope_rows],
            )
            ranking = _season_ranking_metrics(scope_rows, top_n=12)
            detailed.append(
                {
                    "position": position,
                    "target_name": target_name,
                    "candidate_source": source,
                    "candidate_name": candidate_name,
                    "evaluation_scope": scope,
                    "evaluation_seasons": sorted(seasons),
                    **metrics,
                    **ranking,
                    "segments": segment_regression_metrics(
                        scope_rows,
                        dimensions=("experience_group", "projection_tier"),
                        top_n=None,
                    ),
                }
            )
    interval_grouped: dict[tuple[str, str, str, str], list[dict[str, Any]]] = defaultdict(list)
    for row in learned_predictions:
        if row["prediction_scope"] in {"validation", "test"}:
            interval_grouped[
                str(row["position"]),
                str(row["target_name"]),
                str(row["model_family"]),
                str(row["prediction_scope"]),
            ].append(row)
    for key in sorted(interval_grouped):
        position, target_name, family, scope = key
        rows = interval_grouped[key]
        for season in sorted({int(row["prediction_season"]) for row in rows}):
            season_rows = [row for row in rows if int(row["prediction_season"]) == season]
            tiers = assign_projection_tiers(
                [row["predicted_value"] for row in season_rows],
                entity_ids=[row["player_id"] for row in season_rows],
            )
            tiered_rows = [
                {**row, "projection_tier": tier}
                for row, tier in zip(season_rows, tiers, strict=True)
            ]
            for projection_tier, metric_rows in (
                ("all", tiered_rows),
                *(
                    (
                        tier,
                        [row for row in tiered_rows if row["projection_tier"] == tier],
                    )
                    for tier in ("top", "middle", "lower")
                ),
            ):
                interval_records.append(
                    {
                        "position": position,
                        "target_name": target_name,
                        "candidate_name": family,
                        "evaluation_scope": scope,
                        "prediction_season": season,
                        "projection_tier": projection_tier,
                        **interval_metrics(
                            [row["actual_value"] for row in metric_rows],
                            [row["p10"] for row in metric_rows],
                            [row["p50"] for row in metric_rows],
                            [row["p90"] for row in metric_rows],
                        ),
                    }
                )
    return detailed, interval_records


def _season_ranking_metrics(rows: list[dict[str, Any]], *, top_n: int) -> dict[str, Any]:
    season_metrics: list[dict[str, Any]] = []
    for season in sorted({int(row["prediction_season"]) for row in rows}):
        season_rows = [row for row in rows if int(row["prediction_season"]) == season]
        metrics = regression_metrics(
            [row["actual_value"] for row in season_rows],
            [row["predicted_value"] for row in season_rows],
            top_n=top_n,
            entity_ids=[row["player_id"] for row in season_rows],
        )
        season_metrics.append({"prediction_season": season, **metrics})
    captures = [
        float(row["top_n_capture_rate"])
        for row in season_metrics
        if row["top_n_capture_rate"] is not None
    ]
    correlations = [
        float(row["spearman_rank_correlation"])
        for row in season_metrics
        if row["spearman_rank_correlation"] is not None
    ]
    return {
        "top_n": top_n,
        "top_n_capture_rate": math.fsum(captures) / len(captures) if captures else None,
        "season_mean_spearman_rank_correlation": (
            math.fsum(correlations) / len(correlations) if correlations else None
        ),
        "season_ranking_metrics": season_metrics,
    }


def _build_live_board(
    dataset: PlayerModelDataset,
    contract: FrozenProjectionContract,
    model_config: PlayerModelConfig,
    app_config: AppConfig,
    *,
    run_id: str,
    learned_predictions: list[dict[str, Any]],
    baseline_predictions: list[dict[str, Any]],
    champions: dict[tuple[str, str], dict[str, Any]],
    final_routes: dict[tuple[str, str, str], FinalRoute],
) -> list[dict[str, Any]]:
    live_season = app_config.project.prediction_season
    learned_lookup = {
        (
            str(row["player_id"]),
            str(row["target_name"]),
            str(row["model_family"]),
        ): row
        for row in learned_predictions
        if row["prediction_scope"] == "live"
    }
    baseline_lookup = {
        (
            str(row["player_id"]),
            str(row["target_name"]),
            str(row["baseline_name"]),
        ): row
        for row in baseline_predictions
        if int(row["prediction_season"]) == live_season
    }
    live = dataset.frame.loc[dataset.frame["prediction_season"].eq(live_season)].copy()
    live.sort_values(["position", "player_id"], kind="mergesort", inplace=True)
    lineage = _lineage(contract, model_config)
    board: list[dict[str, Any]] = []
    for _, player in live.iterrows():
        player_id = str(player["player_id"])
        position = str(player["position"])
        is_rookie = bool(player["is_rookie"])
        target_values: dict[str, dict[str, Any]] = {}
        explanations: dict[str, Any] = {}
        for target_name in model_config.targets:
            champion = champions[position, target_name]
            selected_source = str(champion["selected_source"])
            selected_name = str(champion["selected_name"])
            if is_rookie:
                selected_source = "baseline"
                selected_name = str(champion["reference_baseline_name"])
            if selected_source == "learned":
                prediction = learned_lookup[player_id, target_name, selected_name]
                route = final_routes[position, target_name, selected_name]
                feature_values = {feature: player[feature] for feature in dataset.feature_columns}
                explanation = explain_player_prediction(
                    route.tuning.pipeline,
                    feature_values,
                    route.position_reference,
                    position=position,
                    target_name=target_name,
                    feature_names=route.explanation_features,
                    prediction_value=float(prediction["p50"]),
                    top_n=5,
                )
                values = {
                    "p10": float(prediction["p10"]),
                    "p50": float(prediction["p50"]),
                    "p90": float(prediction["p90"]),
                    "selected_source": selected_source,
                    "selected_name": selected_name,
                }
            else:
                baseline = baseline_lookup[player_id, target_name, selected_name]
                point = float(baseline["predicted_value"])
                lower = median = upper = point
                if is_rookie:
                    reason = (
                        "Historical preseason position evidence contains no validated rookie "
                        "cohort, so learned rookie output is disabled."
                    )
                else:
                    reason = (
                        "The transparent heuristic retained the title because the best "
                        "learned candidate did not clear the fixed draft-relevant cohort, "
                        "paired-bootstrap, pooled-MAE, and ranking safeguards."
                    )
                explanation = explain_heuristic_fallback(
                    heuristic_name=selected_name,
                    position=position,
                    target_name=target_name,
                    prediction_value=median,
                    reason=reason,
                    is_rookie=is_rookie,
                    supporting_values={
                        "position_prior_fantasy_points_per_game": player[
                            "position_prior_fantasy_points_per_game"
                        ],
                        "position_prior_games_active": player["position_prior_games_active"],
                    },
                )
                if not is_rookie:
                    explanation["uncertainty_status"] = "transparent_point_estimate_only"
                values = {
                    "p10": lower,
                    "p50": median,
                    "p90": upper,
                    "selected_source": selected_source,
                    "selected_name": selected_name,
                }
            target_values[target_name] = values
            explanations[target_name] = explanation
        selected_sources = {str(values["selected_source"]) for values in target_values.values()}
        if is_rookie:
            prediction_status = "rookie_heuristic_fallback_unvalidated"
        elif selected_sources == {"learned"}:
            prediction_status = "learned_models_validated"
        elif selected_sources == {"baseline"}:
            prediction_status = "transparent_baselines_validated"
        else:
            prediction_status = "mixed_learned_and_heuristic_validated"
        board.append(
            {
                "run_id": run_id,
                "player_id": player_id,
                "prediction_season": live_season,
                "position": position,
                **_target_board_columns(target_values),
                "prediction_status": prediction_status,
                "explanation_payload": canonical_json(
                    {
                        "schema_version": "1.0",
                        "player_id": player_id,
                        "position": position,
                        "is_rookie": is_rookie,
                        "targets": explanations,
                        "interpretation": (
                            "Model explanations describe associations and local sensitivity, "
                            "not causal effects."
                        ),
                    }
                ),
                **lineage,
                "evaluation_report_fingerprint": "pending",
            }
        )
    if len(board) != len(live):
        raise RuntimeError("The live board did not cover every Phase 3 feature row.")
    return board


def _target_board_columns(target_values: dict[str, dict[str, Any]]) -> dict[str, Any]:
    columns: dict[str, Any] = {}
    for target_name, values in target_values.items():
        for suffix in ("p10", "p50", "p90", "selected_source", "selected_name"):
            columns[f"{target_name}_{suffix}"] = values[suffix]
    return columns


def _champion_records(
    champions: list[dict[str, Any]],
    final_routes: dict[tuple[str, str, str], FinalRoute],
    run_id: str,
) -> list[dict[str, Any]]:
    records: list[dict[str, Any]] = []
    for champion in champions:
        position = str(champion["position"])
        target_name = str(champion["target_name"])
        selected_source = str(champion["selected_source"])
        selected_name = str(champion["selected_name"])
        model_id = (
            final_routes[position, target_name, selected_name].model_id
            if selected_source == "learned"
            else None
        )
        records.append(
            {
                "run_id": run_id,
                "target_name": target_name,
                "position": position,
                "selected_source": selected_source,
                "selected_name": selected_name,
                "model_id": model_id,
                "selection_metric": str(champion["selection_metric"]),
                "selection_value": float(champion["selection_value"]),
                "reference_baseline_name": str(champion["reference_baseline_name"]),
                "reference_baseline_value": float(champion["reference_baseline_value"]),
                "improvement": float(champion["mae_improvement_over_best_baseline"]),
                "selection_payload": canonical_json(champion),
            }
        )
    return records


def _diagnostic_records(
    detailed_metrics: list[dict[str, Any]],
    interval_metric_records: list[dict[str, Any]],
    comparison_records: list[dict[str, Any]],
    learned_predictions: list[dict[str, Any]],
    final_routes: dict[tuple[str, str, str], FinalRoute],
    contract: FrozenProjectionContract,
) -> dict[str, list[dict[str, Any]]]:
    season_metrics: list[dict[str, Any]] = []
    for key in sorted(
        {
            (
                str(row["position"]),
                str(row["target_name"]),
                str(row["candidate_source"]),
                str(row["candidate_name"]),
                int(row["prediction_season"]),
            )
            for row in comparison_records
        }
    ):
        position, target_name, source, name, season = key
        rows = [
            row
            for row in comparison_records
            if str(row["position"]) == position
            and str(row["target_name"]) == target_name
            and str(row["candidate_source"]) == source
            and str(row["candidate_name"]) == name
            and int(row["prediction_season"]) == season
        ]
        metrics = regression_metrics(
            [row["actual_value"] for row in rows],
            [row["predicted_value"] for row in rows],
            top_n=None,
        )
        season_metrics.append(
            {
                "season": season,
                "position": position,
                "target_name": target_name,
                "candidate_source": source,
                "candidate_name": name,
                "rows": metrics["rows"],
                "mae": metrics["mae"],
            }
        )
    test_predictions = [
        {
            "player_id": row["player_id"],
            "prediction_season": contract.test_season,
            "position": row["position"],
            "target_name": row["target_name"],
            "candidate_source": row["candidate_source"],
            "candidate_name": row["candidate_name"],
            "actual_value": row["actual_value"],
            "predicted_value": row["predicted_value"],
            "residual": (
                None
                if row["actual_value"] is None
                else float(row["actual_value"]) - float(row["predicted_value"])
            ),
        }
        for row in comparison_records
        if int(row["prediction_season"]) == contract.test_season
        and str(row["candidate_source"]) == "learned"
    ]
    segment_metrics = [
        {
            "position": metric["position"],
            "target_name": metric["target_name"],
            "candidate_source": metric["candidate_source"],
            "candidate_name": metric["candidate_name"],
            "evaluation_scope": metric["evaluation_scope"],
            "segment_dimension": segment["segment_dimension"],
            "segment": segment["segment"],
            "rows": segment["rows"],
            "mae": segment["mae"],
        }
        for metric in detailed_metrics
        if metric["candidate_source"] == "learned"
        for segment in metric["segments"]
    ]
    ridge_coefficients = [
        {
            "position": route.position,
            "target_name": route.target_name,
            "feature": row["feature"],
            "coefficient": row["coefficient"],
            "absolute_importance": row["absolute_importance"],
            "rank": row["rank"],
        }
        for route in final_routes.values()
        if route.family == RIDGE
        for row in route.global_importance
    ]
    hgb_importance = [
        {
            "position": route.position,
            "target_name": route.target_name,
            "feature": row["feature"],
            "importance_mean": row["importance_mean"],
            "rank": row["rank"],
        }
        for route in final_routes.values()
        if route.family == HIST_GRADIENT_BOOSTING
        for row in route.global_importance
    ]
    feature_responses = [
        {
            "position": route.position,
            "target_name": route.target_name,
            "feature": response["feature"],
            "response_rank": response_rank,
            "feature_value": point["feature_value"],
            "average_prediction": point["average_prediction"],
        }
        for route in final_routes.values()
        if route.family == HIST_GRADIENT_BOOSTING
        for response_rank, response in enumerate(route.feature_responses, start=1)
        for point in response["points"]
    ]
    return {
        "season_metrics": season_metrics,
        "test_predictions": test_predictions,
        "residuals": test_predictions,
        "segment_metrics": segment_metrics,
        "interval_metrics": [
            row for row in interval_metric_records if row["projection_tier"] == "all"
        ],
        "ridge_coefficients": ridge_coefficients,
        "hgb_permutation_importance": hgb_importance,
        "feature_responses": feature_responses,
    }


def _model_card_payload(
    route: FinalRoute,
    contract: FrozenProjectionContract,
    config: PlayerModelConfig,
    trained_at: datetime,
    publication_id: str,
    candidate_metrics: dict[str, Any],
    baseline_metrics: dict[str, Any],
    champion: dict[str, Any],
    route_interval_metrics: list[dict[str, Any]],
    artifact_path: str,
    plot_paths: dict[str, str],
) -> dict[str, Any]:
    return {
        "model_id": route.model_id,
        "publication_id": publication_id,
        "trained_at": trained_at.isoformat(),
        "purpose": (
            "Project one future NFL season for draft-preparation comparison; this candidate "
            "is selected only if it improves fixed cutoff-safe draft-relevant validation "
            "rows and clears paired-bootstrap, pooled-MAE, and ranking safeguards."
        ),
        "target_name": route.target_name,
        "training_seasons": list(route.tuning.training_seasons),
        "feature_cutoff": "September 1 before each prediction season",
        "feature_names": list(config.numeric_features + config.categorical_features),
        "missing_value_behavior": (
            "Numeric medians and explicit missing indicators are fitted inside each training "
            "fold; categorical gaps use an explicit missing token. Targets are never imputed."
        ),
        "hyperparameters": dict(route.tuning.best_parameters),
        "folds": list(contract.folds),
        "metrics": candidate_metrics,
        "baseline_comparison": {
            "reference_metrics": baseline_metrics,
            "selected_champion": champion["selected_name"],
            "selected_source": champion["selected_source"],
            "decision_status": champion["decision_status"],
            "learned_improvement_status": champion["learned_improvement_status"],
            "this_candidate_selected": (
                champion["selected_source"] == "learned"
                and champion["selected_name"] == route.family
            ),
            "best_learned_vs_baseline_bootstrap": champion["best_learned_vs_baseline_bootstrap"],
            "selection_rule": (
                "A learned candidate must lower fixed-cohort draft-relevant validation MAE, "
                "its paired-bootstrap 95% interval must remain below zero, pooled MAE must "
                "stay within tolerance, and total-points top-N capture must be preserved; "
                "otherwise the transparent baseline is retained."
            ),
        },
        "uncertainty": {
            "method": "training-only signed out-of-fold residual quantiles",
            "operational_center": config.learned_operational_center,
            "residual_rows": route.calibration.residual_count,
            "residual_seasons": list(route.calibration.residual_seasons),
            "empirical_metrics_by_season": route_interval_metrics,
            "empirical_not_guaranteed": True,
        },
        "limitations": [
            "No historical preseason-position archive exists for a validated rookie cohort.",
            "Intervals are empirical residual ranges, not guaranteed probability statements.",
            "Negative fantasy-point outcomes are legitimate and are not silently clamped.",
            "Player explanations describe associations and sensitivity, not causes.",
        ],
        "intended_uses": [
            "Compare transparent, linear, and nonlinear season projections.",
            "Supply an auditable 2026 projection input to later draft-value work.",
        ],
        "out_of_scope_uses": [
            "Weekly lineup decisions, wagering, injury diagnosis, or causal claims.",
            "Learned rookie projection claims until historical rookie evidence is added.",
            "ADP availability or draft recommendations, which begin in later phases.",
        ],
        "artifact_path": artifact_path,
        "artifact_sha256": route.artifact_metadata.sha256,
        "data_lineage": {
            "feature_data_fingerprint": contract.feature_data_fingerprint,
            "target_data_fingerprint": contract.target_data_fingerprint,
            "build_fingerprint": contract.build_fingerprint,
            "scoring_ruleset_fingerprint": contract.scoring_ruleset_fingerprint,
            "baseline_report_fingerprint": contract.baseline_report_fingerprint,
            "model_feature_fingerprint": config.feature_contract_fingerprint(),
            "model_config_fingerprint": config.fingerprint(),
        },
        "global_explanations": {
            "method": (
                "standardized coefficients"
                if route.family == RIDGE
                else (
                    "registered-artifact descriptive permutation importance and partial "
                    f"dependence on {contract.test_season} rows, computed only after "
                    "champion selection"
                )
            ),
            "importance": route.global_importance,
            "feature_responses": route.feature_responses,
            "diagnostic_plots": plot_paths,
        },
    }


def _report_payload(
    contract: FrozenProjectionContract,
    dataset: PlayerModelDataset,
    config: PlayerModelConfig,
    run_id: str,
    publication_id: str,
    run_fingerprint: str,
    trained_at: datetime,
    predictions: list[dict[str, Any]],
    models: list[dict[str, Any]],
    board: list[dict[str, Any]],
    selection: dict[str, Any],
    detailed_metrics: list[dict[str, Any]],
    interval_metric_records: list[dict[str, Any]],
    final_routes: dict[tuple[str, str, str], FinalRoute],
    plot_paths: dict[str, str],
) -> dict[str, Any]:
    rookie_rows = int(
        dataset.frame.loc[
            dataset.frame["prediction_season"].eq(
                max(int(row["prediction_season"]) for row in board)
            ),
            "is_rookie",
        ].sum()
    )
    return {
        "title": "Phase 4 Player Model Evaluation",
        "schema_version": "1.0",
        "status": "PASSED",
        "phase": "Phase 4 - statistical and ML player models",
        "run_id": run_id,
        "publication_id": publication_id,
        "run_fingerprint": run_fingerprint,
        "trained_at": trained_at.isoformat(),
        "feature_data_fingerprint": contract.feature_data_fingerprint,
        "target_data_fingerprint": contract.target_data_fingerprint,
        "build_fingerprint": contract.build_fingerprint,
        "scoring_ruleset_fingerprint": contract.scoring_ruleset_fingerprint,
        "baseline_report_fingerprint": contract.baseline_report_fingerprint,
        "model_feature_fingerprint": config.feature_contract_fingerprint(),
        "selected_feature_data_fingerprint": dataset.feature_fingerprint,
        "model_config_fingerprint": config.fingerprint(),
        "feature_contract": {
            "numeric_features": list(config.numeric_features),
            "categorical_features": list(config.categorical_features),
            "forbidden": "baseline outputs, target data, and candidate-selection metadata",
        },
        "prediction_center_semantics": {
            "learned": config.learned_operational_center,
            "transparent_baseline": config.baseline_operational_center,
            "selection_matches_served_center": True,
        },
        "split_strategy": "expanding_prediction_seasons_with_nested_chronological_tuning",
        "folds": list(contract.folds),
        "selection_metric": selection["selection_metric"],
        "selection_rule": selection["selection_rule"],
        "validation_seasons": selection["validation_seasons"],
        "test_season": selection["test_season"],
        "test_excluded_from_selection": selection["test_excluded_from_selection"],
        "candidate_metrics": selection["candidate_metrics"],
        "champions": selection["champions"],
        "selection": selection,
        "detailed_metrics": detailed_metrics,
        "interval_metrics": interval_metric_records,
        "uncertainty_metrics": interval_metric_records,
        "row_counts": {
            "feature_rows": contract.feature_rows,
            "target_rows": contract.target_rows,
            "model_rows": len(models),
            "prediction_rows": len(predictions),
            "evaluated_rows": sum(row["actual_value"] is not None for row in predictions),
            "live_prediction_rows": sum(row["prediction_scope"] == "live" for row in predictions),
            "board_rows": len(board),
            "live_rookie_fallback_rows": rookie_rows,
            "selection_candidates": len(selection["candidate_metrics"]),
        },
        "models": [
            {
                key: row[key]
                for key in (
                    "model_id",
                    "model_family",
                    "target_name",
                    "position",
                    "training_rows",
                    "hyperparameters",
                    "artifact_path",
                    "artifact_sha256",
                    "model_card_path",
                    "model_card_sha256",
                )
            }
            for row in models
        ],
        "global_explanations": [
            {
                "position": route.position,
                "target_name": route.target_name,
                "model_family": route.family,
                "importance": route.global_importance,
                "feature_responses": route.feature_responses,
            }
            for route in (final_routes[key] for key in sorted(final_routes))
        ],
        "diagnostic_plots": plot_paths,
        "uncertainty_interpretation": (
            "Learned-candidate P10/P50/P90 values are empirical signed-residual intervals "
            "fitted only on earlier out-of-fold predictions; their coverage is measured, "
            "not guaranteed. A selected transparent baseline is served honestly as its "
            "validated Phase 3 point with P10=P50=P90, not as a calibrated interval."
        ),
        "rookie_policy": {
            "historical_training_rows": 0,
            "live_rookie_rows": rookie_rows,
            "learned_models_used": False,
            "fallback": "transparent Phase 3 heuristic",
            "interval_status": "unvalidated_uncalibrated_point_only",
            "reason": (
                "A historical preseason-position archive is required before rookie model "
                "performance can be evaluated honestly."
            ),
        },
        "rookie_boundary": [
            f"{rookie_rows} live rookies use transparent point fallbacks.",
            "No historical rookie ML metric is reported without a preseason-position archive.",
        ],
        "quality_checks": [
            "All preprocessing and tuning are fold-local.",
            (
                f"{list(contract.validation_seasons)} cutoff-safe draft-relevant cohort MAE "
                "plus paired-bootstrap, pooled-MAE, and ranking safeguards select champions; "
                f"{contract.test_season} never selects."
            ),
            "Every learned candidate is compared against all five Phase 3 baselines.",
            "Interval coverage, width, and pinball loss are reported by position and tier.",
            "Artifacts are reloaded and must reproduce fitted predictions before registration.",
            "All registered artifacts and cards have SHA-256 hashes.",
            "The 2026 board covers every live feature row; rookies are labeled fallbacks.",
        ],
        "limitations": [
            "The candidate universe is a cutoff-safe proxy, not a historical roster list.",
            "PPG is conditional on positive mapped snap participation; missing targets stay null.",
            "Games-active predictions are bounded 0-18 because traded players can exceed 17.",
            "Direct fantasy-point targets are benchmarks; component-first extensions remain.",
            "ADP, availability, and draft optimization are not part of Phase 4.",
            "SHAP remains optional and was not required for this run.",
        ],
        "diagnostics": plot_paths,
    }


def _reuse_current_run(
    config: AppConfig,
    run_id: str,
    report_markdown_path: Path,
    report_json_path: Path,
) -> PlayerModelTrainingResult | None:
    warehouse_path = config.resolve(config.paths.warehouse)
    if not warehouse_path.is_file():
        return None
    import duckdb

    try:
        with duckdb.connect(str(warehouse_path), read_only=True) as connection:
            row = connection.execute(
                """
                SELECT run.run_id, run.model_rows, run.prediction_rows,
                       run.evaluated_rows, run.live_prediction_rows,
                       run.champion_rows, evaluation.report_payload, run.run_payload,
                       (SELECT count(*) FROM player_projection_board AS board
                         WHERE board.run_id = run.run_id)
                FROM player_projection_runs AS run
                JOIN player_projection_evaluation_metadata AS evaluation
                  ON run.run_id = evaluation.run_id
                WHERE run.run_id = ? AND run.status = 'complete'
                """,
                [run_id],
            ).fetchone()
    except duckdb.Error:
        return None
    if row is None or projection_integrity_issues(config):
        return None
    report = json.loads(str(row[6]))
    registered_outputs = json.loads(str(row[7]))
    report_path, publication_issues = _materialize_publication_mirrors_with_fallback(
        config,
        report=report,
        registered_outputs=registered_outputs,
        report_markdown_path=report_markdown_path,
        report_json_path=report_json_path,
    )
    return PlayerModelTrainingResult(
        committed=False,
        reused=True,
        run_id=str(row[0]),
        model_rows=int(row[1]),
        prediction_rows=int(row[2]),
        evaluated_rows=int(row[3]),
        live_prediction_rows=int(row[4]),
        champion_rows=int(row[5]),
        board_rows=int(row[8]),
        report_path=report_path,
        issues=publication_issues,
        report=report,
    )


def _finalize_projection_run(
    config: AppConfig,
    *,
    report: dict[str, Any],
    registered_outputs: dict[str, Any],
    report_markdown_path: Path,
    report_json_path: Path,
) -> tuple[Path, tuple[str, ...]]:
    integrity_issues = projection_integrity_issues(
        config,
        expected_status="complete",
    )
    if integrity_issues:
        raise RuntimeError("; ".join(integrity_issues))
    return _materialize_publication_mirrors_with_fallback(
        config,
        report=report,
        registered_outputs=registered_outputs,
        report_markdown_path=report_markdown_path,
        report_json_path=report_json_path,
    )


def _committed_training_result(
    config: AppConfig,
    *,
    run_id: str,
    model_rows: int,
    prediction_rows: int,
    evaluated_rows: int,
    live_prediction_rows: int,
    champion_rows: int,
    board_rows: int,
    report: dict[str, Any],
    registered_outputs: dict[str, Any],
    report_markdown_path: Path,
    report_json_path: Path,
) -> PlayerModelTrainingResult:
    """Preserve the real committed outcome across post-commit publication work."""

    report_path: Path | None
    try:
        report_path, publication_issues = _finalize_projection_run(
            config,
            report=report,
            registered_outputs=registered_outputs,
            report_markdown_path=report_markdown_path,
            report_json_path=report_json_path,
        )
    except Exception as exc:
        try:
            report_path = _registered_authoritative_report_path(
                config.project_root,
                registered_outputs,
            )
            path_issue = ""
        except Exception as path_exc:
            report_path = None
            path_issue = f"; the authoritative report path is also unavailable: {path_exc}"
        publication_issues = (
            "The Phase 4 warehouse transaction committed, but post-commit verification "
            f"or mirror refresh did not finish: {exc}{path_issue}",
        )
    return PlayerModelTrainingResult(
        committed=True,
        reused=False,
        run_id=run_id,
        model_rows=model_rows,
        prediction_rows=prediction_rows,
        evaluated_rows=evaluated_rows,
        live_prediction_rows=live_prediction_rows,
        champion_rows=champion_rows,
        board_rows=board_rows,
        report_path=report_path,
        issues=publication_issues,
        report=report,
    )


def _materialize_publication_mirrors_with_fallback(
    config: AppConfig,
    *,
    report: dict[str, Any],
    registered_outputs: dict[str, Any],
    report_markdown_path: Path,
    report_json_path: Path,
) -> tuple[Path, tuple[str, ...]]:
    authoritative_report = _registered_authoritative_report_path(
        config.project_root,
        registered_outputs,
    )
    try:
        mirror_path = _materialize_publication_mirrors(
            config,
            report=report,
            registered_outputs=registered_outputs,
            report_markdown_path=report_markdown_path,
            report_json_path=report_json_path,
        )
    except Exception as exc:
        return (
            authoritative_report,
            (
                "The authoritative Phase 4 run is valid, but its requested report or "
                f"registry mirror could not be refreshed: {exc}",
            ),
        )
    return mirror_path, ()


def _materialize_publication_mirrors(
    config: AppConfig,
    *,
    report: dict[str, Any],
    registered_outputs: dict[str, Any],
    report_markdown_path: Path,
    report_json_path: Path,
) -> Path:
    """Refresh non-authoritative convenience outputs from one validated run."""

    markdown_output = _resolve_publication_mirror_path(
        config.project_root,
        report_markdown_path,
    )
    _resolve_publication_mirror_path(config.project_root, report_json_path)
    from fantasy_draft_ai.models.player_projection.reporting import write_evaluation_report

    mirror_files = write_evaluation_report(
        config.project_root,
        report,
        json_path=report_json_path,
        markdown_path=report_markdown_path,
    )
    expected_files = registered_outputs.get("report_files")
    if not isinstance(expected_files, dict):
        raise RuntimeError("The active run does not register authoritative report files.")
    for key in (
        "report_fingerprint",
        "json_sha256",
        "markdown_sha256",
    ):
        if str(mirror_files.get(key, "")) != str(expected_files.get(key, "")):
            raise RuntimeError(f"The requested report mirror does not match registered {key}.")
    registry = registered_outputs.get("registry")
    if not isinstance(registry, dict):
        raise RuntimeError("The active run does not register an authoritative model registry.")
    _copy_registered_output(
        config.project_root,
        metadata=registry,
        destination=REGISTRY_MIRROR_PATH,
        label="model registry",
    )
    return markdown_output


def _registered_authoritative_report_path(
    project_root: Path,
    registered_outputs: dict[str, Any],
) -> Path:
    report_files = registered_outputs.get("report_files")
    if not isinstance(report_files, dict) or not report_files.get("markdown_path"):
        raise RuntimeError("The active run does not register an authoritative Markdown report.")
    path = _resolve_project_path(project_root, Path(str(report_files["markdown_path"])))
    _require_authoritative_publication_path(project_root, path)
    return path


def _resolve_publication_mirror_path(project_root: Path, path: Path) -> Path:
    resolved = _resolve_project_path(project_root, path)
    authoritative_root = (project_root / AUTHORITATIVE_PUBLICATION_ROOT).resolve()
    if resolved == authoritative_root or authoritative_root in resolved.parents:
        raise ValueError(
            "Requested report mirrors cannot overwrite immutable models/reports outputs."
        )
    return resolved


def _require_authoritative_publication_path(project_root: Path, path: Path) -> None:
    authoritative_root = (project_root / AUTHORITATIVE_PUBLICATION_ROOT).resolve()
    if path == authoritative_root or authoritative_root not in path.parents:
        raise RuntimeError("Registered Phase 4 publication files must be attempt-scoped.")


def _copy_registered_output(
    project_root: Path,
    *,
    metadata: dict[str, Any],
    destination: Path,
    label: str,
) -> None:
    if not metadata.get("path") or not metadata.get("sha256"):
        raise RuntimeError(f"The active run has incomplete {label} metadata.")
    source = _resolve_project_path(project_root, Path(str(metadata["path"])))
    _require_authoritative_publication_path(project_root, source)
    expected_hash = str(metadata["sha256"])
    if not source.is_file() or sha256_file(source) != expected_hash:
        raise RuntimeError(f"The authoritative {label} does not match its registered hash.")
    output = _resolve_publication_mirror_path(project_root, destination)
    _atomic_write_bytes(output, source.read_bytes())
    if sha256_file(output) != expected_hash:
        raise RuntimeError(f"The refreshed {label} mirror does not match its source.")


def _lineage(
    contract: FrozenProjectionContract,
    config: PlayerModelConfig,
) -> dict[str, str]:
    return {
        "feature_data_fingerprint": contract.feature_data_fingerprint,
        "target_data_fingerprint": contract.target_data_fingerprint,
        "build_fingerprint": contract.build_fingerprint,
        "scoring_ruleset_fingerprint": contract.scoring_ruleset_fingerprint,
        "baseline_report_fingerprint": contract.baseline_report_fingerprint,
        "model_feature_fingerprint": config.feature_contract_fingerprint(),
        "model_config_fingerprint": config.fingerprint(),
    }


def _model_id(run_id: str, position: str, target_name: str, family: str) -> str:
    target_label = {
        "fantasy_points_per_game": "ppg",
        "games_active": "games",
        "fantasy_points_total": "total",
    }[target_name]
    family_label = "ridge" if family == RIDGE else "hgb"
    return f"{run_id}-{position.lower()}-{target_label}-{family_label}"


def _resolve_project_path(project_root: Path, path: Path) -> Path:
    resolved = path.resolve() if path.is_absolute() else (project_root / path).resolve()
    try:
        resolved.relative_to(project_root.resolve())
    except ValueError as exc:
        raise ValueError("Phase 4 output paths must stay inside the project root.") from exc
    return resolved


def _package_versions() -> dict[str, str]:
    packages = (
        "fantasy-football-draft-ai",
        "duckdb",
        "joblib",
        "matplotlib",
        "numpy",
        "pandas",
        "scikit-learn",
        "scipy",
    )
    versions: dict[str, str] = {}
    for package in packages:
        try:
            versions[package] = version(package)
        except PackageNotFoundError:
            versions[package] = "unknown"
    return versions


def _write_model_registry(
    project_root: Path,
    *,
    run_id: str,
    publication_id: str,
    report_fingerprint: str,
    models: list[dict[str, Any]],
    champions: list[dict[str, Any]],
    output_path: Path,
) -> dict[str, str]:
    path = _resolve_project_path(project_root, output_path)
    _require_authoritative_publication_path(project_root, path)
    payload = {
        "schema_version": "1.0",
        "authority": (
            "DuckDB and the registered attempt-scoped hash are authoritative; "
            "unregistered copies are convenience mirrors."
        ),
        "active_run_id": run_id,
        "publication_id": publication_id,
        "evaluation_report_fingerprint": report_fingerprint,
        "models": [
            {
                key: row[key]
                for key in (
                    "model_id",
                    "model_family",
                    "position",
                    "target_name",
                    "artifact_path",
                    "artifact_sha256",
                    "model_card_path",
                    "model_card_sha256",
                )
            }
            for row in sorted(models, key=lambda value: str(value["model_id"]))
        ],
        "champions": [
            _registry_champion_metadata(row)
            for row in sorted(
                champions,
                key=lambda value: (str(value["position"]), str(value["target_name"])),
            )
        ],
    }
    content = (json.dumps(payload, indent=2, sort_keys=True, allow_nan=False) + "\n").encode(
        "utf-8"
    )
    _atomic_write_bytes(path, content)
    return {
        "path": path.relative_to(project_root.resolve()).as_posix(),
        "sha256": sha256_file(path),
    }


def _registry_champion_metadata(row: dict[str, Any]) -> dict[str, Any]:
    metadata = {
        key: row[key]
        for key in (
            "position",
            "target_name",
            "selected_source",
            "selected_name",
            "selection_metric",
            "selection_value",
            "reference_baseline_name",
            "reference_baseline_value",
        )
    }
    try:
        selection_payload = json.loads(str(row.get("selection_payload", "{}")))
    except (TypeError, ValueError):
        selection_payload = {}
    if not isinstance(selection_payload, dict):
        selection_payload = {}
    for key in ("decision_status", "learned_improvement_status"):
        value = row.get(key, selection_payload.get(key))
        if value is not None:
            metadata[key] = value
    return metadata


def _atomic_write_bytes(path: Path, content: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temporary_name = tempfile.mkstemp(
        prefix=f".{path.name}-", suffix=".tmp", dir=path.parent
    )
    temporary = Path(temporary_name)
    try:
        with os.fdopen(descriptor, "wb") as stream:
            stream.write(content)
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary, path)
    finally:
        temporary.unlink(missing_ok=True)


def _optional_float(value: Any) -> float | None:
    if value is None or bool(pd.isna(value)):
        return None
    number = float(value)
    if not math.isfinite(number):
        return None
    return number


def _optional_int(value: Any) -> int | None:
    number = _optional_float(value)
    return None if number is None else int(number)


def _failure(*issues: str) -> PlayerModelTrainingResult:
    return PlayerModelTrainingResult(
        committed=False,
        reused=False,
        run_id="",
        model_rows=0,
        prediction_rows=0,
        evaluated_rows=0,
        live_prediction_rows=0,
        champion_rows=0,
        board_rows=0,
        report_path=None,
        issues=tuple(issues),
        report={"schema_version": "1.0", "status": "FAILED", "issues": list(issues)},
    )
