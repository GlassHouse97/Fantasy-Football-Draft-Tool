from __future__ import annotations

import hashlib
import json
import warnings
from pathlib import Path
from typing import Any

import pytest

from fantasy_draft_ai.models.player_projection.reporting import (
    ReportingPathError,
    ReportingPayloadError,
    evaluation_report_fingerprint,
    write_diagnostic_svgs,
    write_evaluation_report,
    write_model_card,
)


def _evaluation_payload() -> dict[str, Any]:
    return {
        "title": "Phase 4 Evaluation",
        "status": "passed",
        "generated_at": "2026-08-05T18:00:00Z",
        "feature_data_fingerprint": "feature-123",
        "target_data_fingerprint": "target-123",
        "build_fingerprint": "build-123",
        "baseline_report_fingerprint": "baseline-123",
        "selection_metric": "pooled_validation_mae",
        "selection_rule": "Validation only; ties retain the transparent baseline.",
        "validation_seasons": [2020, 2021, 2022, 2023, 2024],
        "test_season": 2025,
        "test_excluded_from_selection": True,
        "prediction_rows": 100,
        "evaluated_rows": 80,
        "candidate_metrics": [
            {
                "position": "WR",
                "target_name": "fantasy_points_per_game",
                "candidate_source": "learned",
                "candidate_name": "ridge",
                "validation_rows": 70,
                "validation_mae": 2.5,
                "test_rows": 10,
                "test_mae": 2.75,
            }
        ],
        "champions": [
            {
                "position": "WR",
                "target_name": "fantasy_points_per_game",
                "selected_source": "learned",
                "selected_name": "ridge",
                "decision_status": "learned_significant_improvement_selected",
                "selection_value": 2.5,
                "reference_baseline_name": "weighted_history",
                "reference_baseline_value": 2.8,
                "best_learned_name": "ridge",
                "best_learned_value": 2.5,
                "best_learned_mae_improvement": 0.3,
                "best_learned_vs_baseline_bootstrap": {
                    "ci95_lower": -0.5,
                    "ci95_upper": -0.1,
                },
                "test_mae": 2.75,
            }
        ],
        "detailed_metrics": [
            {
                "position": "WR",
                "target_name": "fantasy_points_per_game",
                "candidate_source": "learned",
                "candidate_name": "ridge",
                "evaluation_scope": "validation",
                "rows": 70,
                "mae": 2.5,
                "rmse": 3.2,
                "median_absolute_error": 1.8,
                "spearman_rank_correlation": 0.72,
                "top_n": 12,
                "top_n_capture_rate": 0.75,
                "segments": [
                    {
                        "segment_dimension": "projection_tier",
                        "segment": "top",
                        "rows": 18,
                        "mae": 2.1,
                        "rmse": 2.8,
                        "median_absolute_error": 1.5,
                        "spearman_rank_correlation": 0.7,
                    }
                ],
            }
        ],
        "interval_metrics": [
            {
                "position": "WR",
                "target_name": "fantasy_points_per_game",
                "candidate_name": "ridge",
                "rows": 10,
                "empirical_coverage_p10_p90": 0.8,
                "mean_interval_width_p10_p90": 8.0,
                "pinball_loss_p10": 0.5,
                "pinball_loss_p50": 1.25,
                "pinball_loss_p90": 0.6,
            }
        ],
        "rookie_boundary": [
            "Historical rookie rows are unavailable; live rookies use an unvalidated heuristic."
        ],
        "limitations": ["Intervals are empirical and are not guarantees."],
    }


def _model_card_payload() -> dict[str, Any]:
    return {
        "model_id": "WR-fantasy_points_per_game-ridge",
        "trained_at": "2026-08-05T18:00:00Z",
        "purpose": "Estimate cutoff-safe preseason player production.",
        "target_name": "fantasy_points_per_game",
        "training_seasons": [2016, 2017, 2018, 2019, 2020, 2021, 2022, 2023, 2024, 2025],
        "data_cutoff": "September 1 before each prediction season",
        "feature_names": ["lag1_fantasy_points_per_game", "age_at_cutoff"],
        "missing_value_behavior": "Median imputation learned on each training fold.",
        "hyperparameters": {"alpha": 1.0},
        "folds": [
            {
                "training_seasons": [2016, 2017, 2018, 2019],
                "evaluation_season": 2020,
            }
        ],
        "metrics": {"validation_mae": 2.5, "test_2025_mae": 2.75},
        "baseline_comparison": {
            "reference": "weighted_history",
            "validation_mae_improvement": 0.2,
        },
        "uncertainty": {
            "method": "training-only chronological signed residual quantiles",
            "empirical_coverage_p10_p90": 0.8,
        },
        "limitations": ["No historically validated rookie feature rows are available."],
        "intended_uses": ["Pre-draft ranking support"],
        "out_of_scope_uses": ["Guaranteed outcomes", "Causal claims"],
        "artifact_path": "models/artifacts/run-1/WR/ppg/ridge.joblib",
        "artifact_sha256": "a" * 64,
        "data_lineage": {
            "feature_data_fingerprint": "feature-123",
            "baseline_report_fingerprint": "baseline-123",
        },
        "global_explanations": {
            "method": "standardized Ridge coefficients",
            "top_features": [{"feature": "lag1_fantasy_points_per_game", "coefficient": 0.6}],
            "interpretation": "Associative, not causal.",
        },
    }


def _diagnostic_records() -> dict[str, list[dict[str, Any]]]:
    test_predictions = [
        {
            "prediction_season": 2025,
            "position": "WR",
            "target_name": "fantasy_points_per_game",
            "candidate_name": "ridge",
            "actual_value": 8.0,
            "predicted_value": 7.5,
        },
        {
            "prediction_season": 2025,
            "position": "WR",
            "target_name": "fantasy_points_per_game",
            "candidate_name": "ridge",
            "actual_value": 12.0,
            "predicted_value": 11.0,
        },
    ]
    return {
        "season_metrics": [
            {"prediction_season": 2024, "candidate_name": "ridge", "mae": 2.8},
            {"prediction_season": 2025, "candidate_name": "ridge", "mae": 2.7},
            {"prediction_season": 2024, "candidate_name": "hgb", "mae": 2.6},
            {"prediction_season": 2025, "candidate_name": "hgb", "mae": 2.5},
        ],
        "test_predictions": test_predictions,
        "segment_metrics": [
            {
                "segment_dimension": "experience_group",
                "segment": "veteran",
                "candidate_name": "ridge",
                "mae": 2.1,
            }
        ],
        "interval_metrics": [
            {
                "prediction_season": 2024,
                "candidate_name": "ridge",
                "empirical_coverage_p10_p90": 0.78,
                "mean_interval_width_p10_p90": 7.5,
            },
            {
                "prediction_season": 2025,
                "candidate_name": "ridge",
                "empirical_coverage_p10_p90": 0.8,
                "mean_interval_width_p10_p90": 7.8,
            },
        ],
        "ridge_coefficients": [
            {"feature": "lag1_ppg", "coefficient": 0.7},
            {"feature": "age", "coefficient": -0.2},
        ],
        "hgb_permutation_importance": [
            {"feature": "lag1_ppg", "importance_mean": 1.2},
            {"feature": "age", "importance_mean": 0.1},
        ],
        "feature_responses": [
            {
                "feature": "lag1_ppg",
                "points": [
                    {"feature_value": 2.0, "average_prediction": 4.0},
                    {"feature_value": 8.0, "average_prediction": 9.0},
                ],
            }
        ],
    }


def _dense_diagnostic_records() -> dict[str, list[dict[str, Any]]]:
    targets = (
        "fantasy_points_per_game",
        "games_active",
        "fantasy_points_total",
    )
    positions = ("QB", "RB", "WR", "TE")
    families = ("ridge", "hist_gradient_boosting")
    records: dict[str, list[dict[str, Any]]] = {
        "season_metrics": [],
        "test_predictions": [],
        "residuals": [],
        "segment_metrics": [],
        "interval_metrics": [],
        "ridge_coefficients": [],
        "hgb_permutation_importance": [],
        "feature_responses": [],
    }
    for target_index, target in enumerate(targets):
        for position_index, position in enumerate(positions):
            for family_index, family in enumerate(families):
                for season in range(2020, 2026):
                    mae = 1.5 + target_index + position_index / 10 + family_index / 20
                    records["season_metrics"].append(
                        {
                            "prediction_season": season,
                            "position": position,
                            "target_name": target,
                            "candidate_source": "learned",
                            "candidate_name": family,
                            "rows": 25 + position_index,
                            "mae": mae,
                        }
                    )
                    records["interval_metrics"].append(
                        {
                            "prediction_season": season,
                            "position": position,
                            "target_name": target,
                            "candidate_name": family,
                            "empirical_coverage_p10_p90": 0.74
                            + position_index / 100
                            + family_index / 50,
                            "mean_interval_width_p10_p90": 4.0
                            + target_index * 5
                            + position_index / 2,
                        }
                    )
                for player_index in range(30):
                    actual = float(player_index + target_index * 10)
                    prediction = actual + (position_index - 1.5) / 4 + family_index / 5
                    prediction_row = {
                        "player_id": f"{position}-{family}-{player_index:03d}",
                        "prediction_season": 2025,
                        "position": position,
                        "target_name": target,
                        "candidate_source": "learned",
                        "candidate_name": family,
                        "actual_value": actual,
                        "predicted_value": prediction,
                    }
                    records["test_predictions"].append(prediction_row)
                    records["residuals"].append(prediction_row)
                for segment in ("top", "middle", "lower"):
                    records["segment_metrics"].append(
                        {
                            "position": position,
                            "target_name": target,
                            "candidate_source": "learned",
                            "candidate_name": family,
                            "evaluation_scope": "validation",
                            "segment_dimension": "projection_tier",
                            "segment": segment,
                            "rows": 20,
                            "mae": 2.0 + target_index + position_index / 10,
                        }
                    )
            for feature_index in range(15):
                feature = f"lag_{feature_index}_feature_value"
                records["ridge_coefficients"].append(
                    {
                        "position": position,
                        "target_name": target,
                        "feature": feature,
                        "coefficient": ((-1) ** feature_index) / (feature_index + 1),
                    }
                )
                records["hgb_permutation_importance"].append(
                    {
                        "position": position,
                        "target_name": target,
                        "feature": feature,
                        "importance_mean": 1 / (feature_index + 1),
                    }
                )
            for response_rank in (1, 2):
                for point_index in range(8):
                    records["feature_responses"].append(
                        {
                            "position": position,
                            "target_name": target,
                            "feature": f"response_feature_{response_rank}",
                            "response_rank": response_rank,
                            "feature_value": (
                                None
                                if target == "fantasy_points_total" and position == "QB"
                                else float(point_index)
                            ),
                            "average_prediction": float(
                                point_index + target_index + position_index
                            ),
                        }
                    )
    return records


def test_evaluation_report_is_deterministic_and_timestamp_independent(tmp_path: Path) -> None:
    payload = _evaluation_payload()
    first = write_evaluation_report(
        tmp_path,
        payload,
        json_path="docs/phase4.json",
        markdown_path="docs/phase4.md",
    )
    json_bytes = (tmp_path / first["json_path"]).read_bytes()
    markdown_bytes = (tmp_path / first["markdown_path"]).read_bytes()

    reordered = dict(reversed(list(payload.items())))
    reordered["report_fingerprint"] = "stale"
    second = write_evaluation_report(
        tmp_path,
        reordered,
        json_path="docs/phase4.json",
        markdown_path="docs/phase4.md",
    )

    assert first == second
    assert json_bytes == (tmp_path / second["json_path"]).read_bytes()
    assert markdown_bytes == (tmp_path / second["markdown_path"]).read_bytes()
    assert first["json_sha256"] == hashlib.sha256(json_bytes).hexdigest()
    assert first["markdown_sha256"] == hashlib.sha256(markdown_bytes).hexdigest()
    written = json.loads(json_bytes)
    assert written["report_fingerprint"] == first["report_fingerprint"]
    assert "## Champions selected on validation" in markdown_bytes.decode("utf-8")
    assert "## Required regression and ranking metrics" in markdown_bytes.decode("utf-8")
    assert "## Champion error by experience and projection tier" in markdown_bytes.decode("utf-8")
    assert "Bootstrap CI upper" in markdown_bytes.decode("utf-8")
    assert "## Empirical uncertainty diagnostics" in markdown_bytes.decode("utf-8")
    assert not list(tmp_path.rglob("*.tmp"))

    changed_timestamp = {**payload, "generated_at": "2030-01-01T00:00:00Z"}
    assert evaluation_report_fingerprint(changed_timestamp) == first["report_fingerprint"]


def test_report_payload_rejects_non_json_values_and_escaping_paths(tmp_path: Path) -> None:
    with pytest.raises(ReportingPayloadError, match="JSON-safe"):
        write_evaluation_report(
            tmp_path,
            {"bad": float("nan")},
            json_path="docs/report.json",
            markdown_path="docs/report.md",
        )
    with pytest.raises(ReportingPathError, match="outside"):
        write_evaluation_report(
            tmp_path,
            _evaluation_payload(),
            json_path="../outside.json",
            markdown_path="docs/report.md",
        )


def test_model_card_covers_contract_and_returns_portable_hash(tmp_path: Path) -> None:
    output = write_model_card(
        tmp_path,
        _model_card_payload(),
        output_path="docs/model_cards/wr-ppg-ridge.md",
    )

    assert output["model_card_path"] == "docs/model_cards/wr-ppg-ridge.md"
    card_path = tmp_path / output["model_card_path"]
    content = card_path.read_text(encoding="utf-8")
    assert output["model_card_sha256"] == hashlib.sha256(card_path.read_bytes()).hexdigest()
    for heading in (
        "## Purpose",
        "## Feature inputs",
        "## Missing-value behavior",
        "## Chronological folds",
        "## Comparison with transparent baselines",
        "## Uncertainty estimates",
        "## Global explanations",
        "## Limitations",
        "## Intended uses",
        "## Out-of-scope uses",
        "## Serialized artifact",
    ):
        assert heading in content
    assert "models/artifacts/run-1/WR/ppg/ridge.joblib" in content
    assert "`" + "a" * 64 + "`" in content
    assert not list(tmp_path.rglob("*.tmp"))


def test_model_card_rejects_incomplete_payload_and_escape(tmp_path: Path) -> None:
    incomplete = _model_card_payload()
    del incomplete["uncertainty"]
    with pytest.raises(ReportingPayloadError, match="uncertainty"):
        write_model_card(tmp_path, incomplete, output_path="docs/model.md")

    with pytest.raises(ReportingPathError, match="outside"):
        write_model_card(
            tmp_path,
            _model_card_payload(),
            output_path="../escaped-card.md",
        )


def test_diagnostic_writer_emits_repeatable_portable_svgs(tmp_path: Path) -> None:
    pytest.importorskip("matplotlib")
    import matplotlib.pyplot as pyplot

    records = _diagnostic_records()
    first = write_diagnostic_svgs(
        tmp_path,
        records,
        output_directory="docs/images/phase4",
    )
    first_bytes = {name: (tmp_path / path).read_bytes() for name, path in first.items()}
    second = write_diagnostic_svgs(
        tmp_path,
        records,
        output_directory="docs/images/phase4",
    )

    assert first == second
    assert set(first) == {
        "season_mae_comparison",
        "test_predicted_vs_actual",
        "test_residuals",
        "segment_mae",
        "interval_coverage_width",
        "ridge_coefficients",
        "hgb_permutation_importance",
        "feature_response",
    }
    for name, relative_path in first.items():
        content = (tmp_path / relative_path).read_bytes()
        assert content == first_bytes[name]
        assert content.lstrip().startswith(b"<?xml")
        assert b"<svg" in content
        assert "\\" not in relative_path
    assert pyplot.get_fignums() == []
    assert not list(tmp_path.rglob("*.tmp"))


def test_empty_diagnostics_are_labeled_and_directory_cannot_escape(tmp_path: Path) -> None:
    pytest.importorskip("matplotlib")
    output = write_diagnostic_svgs(tmp_path, {}, output_directory="docs/images/empty")
    assert len(output) == 8
    assert all(
        b"No records supplied" in (tmp_path / relative_path).read_bytes()
        for relative_path in output.values()
    )

    with pytest.raises(ReportingPathError, match="outside"):
        write_diagnostic_svgs(tmp_path, {}, output_directory="../outside")


def test_dense_diagnostics_use_readable_facets_without_layout_warnings(
    tmp_path: Path,
) -> None:
    pytest.importorskip("matplotlib")
    with warnings.catch_warnings(record=True) as caught:
        warnings.simplefilter("always")
        output = write_diagnostic_svgs(
            tmp_path,
            _dense_diagnostic_records(),
            output_directory="docs/images/dense",
        )

    layout_warnings = [
        warning
        for warning in caught
        if "constrained_layout" in str(warning.message)
        or "layout not applied" in str(warning.message).casefold()
    ]
    assert not layout_warnings
    interval_svg = (tmp_path / output["interval_coverage_width"]).read_text(encoding="utf-8")
    importance_svg = (tmp_path / output["ridge_coefficients"]).read_text(encoding="utf-8")
    hgb_svg = (tmp_path / output["hgb_permutation_importance"]).read_text(encoding="utf-8")
    response_svg = (tmp_path / output["feature_response"]).read_text(encoding="utf-8")
    assert "QB · Ridge" in interval_svg
    assert "QB / PPG / lag 0 feature value" in importance_svg
    for target in ("PPG", "Games", "Total"):
        for position in ("QB", "RB", "WR", "TE"):
            assert f"{position} / {target}" in response_svg
    assert "No stable numeric response" in response_svg
    assert "MAE increase" in hgb_svg
    assert "Increase in error after permutation" not in hgb_svg
