"""Deterministic, portable reporting outputs for Phase 4 player models.

The public functions accept JSON-safe mappings so training orchestration does
not need to depend on reporting-specific data classes. Matplotlib remains an
optional, lazy import: commands that do not create diagnostics can run without
the modeling extra installed.
"""

from __future__ import annotations

import hashlib
import importlib
import io
import json
import math
import os
import tempfile
from collections import defaultdict
from collections.abc import Iterable, Mapping, Sequence
from pathlib import Path
from typing import Any, Final, cast


class ReportingPathError(ValueError):
    """Raised when a generated report would escape the project directory."""


class ReportingPayloadError(ValueError):
    """Raised when a reporting payload is incomplete or is not JSON-safe."""


_FINGERPRINT_EXCLUDED_KEYS: Final = frozenset(
    {
        "report_fingerprint",
        "generated_at",
        "generated_at_utc",
        "created_at",
        "trained_at",
        "timestamp",
    }
)

_LINEAGE_KEYS: Final = (
    "feature_data_fingerprint",
    "target_data_fingerprint",
    "build_fingerprint",
    "scoring_ruleset_fingerprint",
    "baseline_report_fingerprint",
    "model_feature_fingerprint",
    "model_config_fingerprint",
)

_PLOT_FILES: Final = {
    "season_mae_comparison": "season_mae_comparison.svg",
    "test_predicted_vs_actual": "test_predicted_vs_actual.svg",
    "test_residuals": "test_residuals.svg",
    "segment_mae": "segment_mae.svg",
    "interval_coverage_width": "interval_coverage_width.svg",
    "ridge_coefficients": "ridge_coefficients.svg",
    "hgb_permutation_importance": "hgb_permutation_importance.svg",
    "feature_response": "feature_response.svg",
}

_PLOT_SIZES: Final = {
    "season_mae_comparison": (13.5, 4.8),
    "test_predicted_vs_actual": (13.5, 4.8),
    "test_residuals": (13.5, 4.8),
    "segment_mae": (13.5, 6.5),
    "interval_coverage_width": (13.5, 8.0),
    "ridge_coefficients": (13.5, 6.5),
    "hgb_permutation_importance": (13.5, 6.5),
    "feature_response": (14.0, 9.0),
}

_TARGET_ORDER: Final = (
    "fantasy_points_per_game",
    "games_active",
    "fantasy_points_total",
)
_TARGET_LABELS: Final = {
    "fantasy_points_per_game": "Fantasy points / game",
    "games_active": "Games active",
    "fantasy_points_total": "Season fantasy points",
}
_POSITION_ORDER: Final = ("QB", "RB", "WR", "TE")
_POSITION_COLORS: Final = {
    "QB": "#4C78A8",
    "RB": "#F58518",
    "WR": "#54A24B",
    "TE": "#E45756",
}
_MAX_SCATTER_POINTS_PER_ROUTE: Final = 200
_MAX_IMPORTANCE_BARS_PER_TARGET: Final = 10


def evaluation_report_fingerprint(report: Mapping[str, Any]) -> str:
    """Return a deterministic report digest independent of wall-clock metadata.

    Only top-level report-generation timestamps are excluded. Timestamps inside
    data-lineage records remain part of the fingerprint because they can identify
    materially different inputs.
    """

    normalized = _json_mapping(report, label="evaluation report")
    fingerprint_payload = {
        key: value for key, value in normalized.items() if key not in _FINGERPRINT_EXCLUDED_KEYS
    }
    return hashlib.sha256(_canonical_json(fingerprint_payload).encode("utf-8")).hexdigest()


def write_evaluation_report(
    project_root: Path,
    report: Mapping[str, Any],
    *,
    json_path: str | Path,
    markdown_path: str | Path,
) -> dict[str, Any]:
    """Atomically write matching JSON and Markdown Phase 4 evaluation reports.

    The caller controls both paths, but each must remain below ``project_root``.
    A supplied ``report_fingerprint`` is recalculated so stale values cannot be
    propagated. Returned paths use forward-slash, project-relative notation.
    """

    normalized = _json_mapping(report, label="evaluation report")
    fingerprint = evaluation_report_fingerprint(normalized)
    normalized["report_fingerprint"] = fingerprint
    json_output, json_relative = _resolve_project_output(project_root, json_path, ".json")
    markdown_output, markdown_relative = _resolve_project_output(project_root, markdown_path, ".md")
    if json_output == markdown_output:
        raise ReportingPathError("JSON and Markdown report paths must be different files.")

    json_bytes = (_canonical_json(normalized, indent=2) + "\n").encode("utf-8")
    markdown_bytes = _render_evaluation_markdown(normalized).encode("utf-8")
    _atomic_write(json_output, json_bytes)
    _atomic_write(markdown_output, markdown_bytes)
    return {
        "report_fingerprint": fingerprint,
        "json_path": json_relative,
        "json_sha256": _sha256_bytes(json_bytes),
        "markdown_path": markdown_relative,
        "markdown_sha256": _sha256_bytes(markdown_bytes),
    }


def write_model_card(
    project_root: Path,
    card: Mapping[str, Any],
    *,
    output_path: str | Path,
) -> dict[str, str]:
    """Write a complete tracked Markdown model card and return portable metadata.

    The payload must include model identity and timestamp, purpose, target,
    training seasons, cutoff, features and missing-value behavior,
    hyperparameters, chronological folds, metrics and baseline comparison,
    uncertainty, limitations, intended and out-of-scope uses, artifact path and
    SHA-256, data lineage, and global explanations. Common aliases documented in
    ``_validate_model_card`` are accepted to keep orchestration payloads simple.
    """

    normalized = _json_mapping(card, label="model card")
    fields = _validate_model_card(normalized)
    output, relative = _resolve_project_output(project_root, output_path, ".md")
    markdown_bytes = _render_model_card(normalized, fields).encode("utf-8")
    _atomic_write(output, markdown_bytes)
    return {
        "model_card_path": relative,
        "model_card_sha256": _sha256_bytes(markdown_bytes),
    }


def write_diagnostic_svgs(
    project_root: Path,
    records: Mapping[str, Sequence[Mapping[str, Any]]],
    *,
    output_directory: str | Path,
) -> dict[str, str]:
    """Write the eight required deterministic Phase 4 diagnostic SVGs.

    Expected record groups are ``season_metrics``, ``test_predictions``,
    ``segment_metrics``, ``interval_metrics``, ``ridge_coefficients``,
    ``hgb_permutation_importance``, and ``feature_responses``. ``residuals`` is
    optional and defaults to ``test_predictions``. Empty groups produce an
    explicitly labeled no-data figure rather than fabricated points.
    """

    normalized = _normalize_plot_records(records)
    output_dir, _ = _resolve_project_directory(project_root, output_directory)
    output_dir.mkdir(parents=True, exist_ok=True)

    matplotlib, pyplot = _load_matplotlib()
    plotters = {
        "season_mae_comparison": lambda figure: _plot_season_mae(
            figure, normalized["season_metrics"]
        ),
        "test_predicted_vs_actual": lambda figure: _plot_predicted_actual(
            figure, normalized["test_predictions"]
        ),
        "test_residuals": lambda figure: _plot_residuals(
            figure, normalized["residuals"] or normalized["test_predictions"]
        ),
        "segment_mae": lambda figure: _plot_segment_mae(figure, normalized["segment_metrics"]),
        "interval_coverage_width": lambda figure: _plot_intervals(
            figure, normalized["interval_metrics"]
        ),
        "ridge_coefficients": lambda figure: _plot_importance(
            figure,
            normalized["ridge_coefficients"],
            title="Ridge coefficient importance",
            value_keys=("coefficient", "value"),
            x_label="Standardized coefficient",
            signed=True,
        ),
        "hgb_permutation_importance": lambda figure: _plot_importance(
            figure,
            normalized["hgb_permutation_importance"],
            title="HGB permutation importance",
            value_keys=("importance_mean", "importance", "value"),
            x_label="MAE increase",
            signed=False,
        ),
        "feature_response": lambda figure: _plot_feature_response(
            figure, normalized["feature_responses"]
        ),
    }

    outputs: dict[str, str] = {}
    for plot_name, file_name in _PLOT_FILES.items():
        destination, relative = _resolve_project_output(
            project_root, output_dir / file_name, ".svg"
        )
        with matplotlib.rc_context(
            {
                "svg.hashsalt": "fantasy-draft-ai-phase4",
                "font.family": "DejaVu Sans",
            }
        ):
            figure = pyplot.figure(
                figsize=_PLOT_SIZES[plot_name],
                constrained_layout=True,
            )
            try:
                plotters[plot_name](figure)
                svg_bytes = _figure_svg_bytes(figure)
            finally:
                pyplot.close(figure)
        _atomic_write(destination, svg_bytes)
        outputs[plot_name] = relative
    return outputs


def _render_evaluation_markdown(report: Mapping[str, Any]) -> str:
    title = str(report.get("title", "Phase 4 Player Model Evaluation"))
    lines = [f"# {title}", ""]
    status = report.get("status")
    if status is not None:
        lines.extend([f"Status: **{_inline(status)}**", ""])
    lines.extend(
        [
            f"Report fingerprint: `{report['report_fingerprint']}`",
            "",
            (
                "This report compares learned player models with transparent baselines "
                "using chronological validation. Test results are reported after selection."
            ),
            "",
        ]
    )

    lineage = _combined_lineage(report)
    if lineage:
        lines.extend(["## Data lineage", ""])
        lines.extend(f"- {key}: `{_inline(value)}`" for key, value in lineage.items())
        lines.append("")

    run_values = {
        key: report[key]
        for key in (
            "phase",
            "run_id",
            "run_fingerprint",
            "trained_at",
            "split_strategy",
        )
        if key in report
    }
    if run_values:
        lines.extend(["## Run metadata", ""])
        lines.extend(f"- {_humanize(key)}: {_inline(value)}" for key, value in run_values.items())
        lines.append("")

    split_values = {
        key: report[key]
        for key in (
            "selection_metric",
            "selection_rule",
            "validation_seasons",
            "test_season",
            "test_excluded_from_selection",
        )
        if key in report
    }
    if split_values:
        lines.extend(["## Selection protocol", ""])
        lines.extend(f"- {_humanize(key)}: {_inline(value)}" for key, value in split_values.items())
        lines.append("")

    row_counts: dict[str, Any] = {
        key: value for key, value in report.items() if key.endswith("_rows") and _is_scalar(value)
    }
    nested_row_counts = report.get("row_counts")
    if isinstance(nested_row_counts, Mapping):
        row_counts.update(
            {str(key): value for key, value in nested_row_counts.items() if _is_scalar(value)}
        )
    if row_counts:
        lines.extend(["## Row accounting", ""])
        lines.extend(
            f"- {_humanize(key)}: {_format_number(value)}"
            for key, value in sorted(row_counts.items())
        )
        lines.append("")

    raw_champions = _mapping_rows(report.get("champions"))
    selection_metric = str(report.get("selection_metric") or "")
    draft_relevant_selection = selection_metric.startswith("draft_relevant_")
    selection_value_label = (
        "Draft-relevant validation MAE"
        if draft_relevant_selection
        else "Validation MAE"
    )
    baseline_value_label = (
        "Draft-relevant baseline MAE" if draft_relevant_selection else "Baseline MAE"
    )
    learned_value_label = (
        "Draft-relevant learned MAE" if draft_relevant_selection else "Learned MAE"
    )
    improvement_label = (
        "Draft-relevant MAE improvement"
        if draft_relevant_selection
        else "Learned MAE improvement"
    )
    champions: list[dict[str, Any]] = []
    for row in raw_champions:
        comparison = row.get("best_learned_vs_baseline_bootstrap")
        comparison_values = comparison if isinstance(comparison, Mapping) else {}
        champions.append(
            {
                **row,
                "bootstrap_ci95_lower": comparison_values.get("ci95_lower"),
                "bootstrap_ci95_upper": comparison_values.get("ci95_upper"),
            }
        )
    if champions:
        lines.extend(
            _markdown_table(
                "## Champions selected on validation",
                champions,
                (
                    ("position", "Position"),
                    ("target_name", "Target"),
                    ("selected_source", "Source"),
                    ("selected_name", "Champion"),
                    ("decision_status", "Decision"),
                    ("selection_value", selection_value_label),
                    ("reference_baseline_name", "Reference baseline"),
                    ("reference_baseline_value", baseline_value_label),
                    ("best_learned_name", "Best learned"),
                    ("best_learned_value", learned_value_label),
                    ("best_learned_mae_improvement", improvement_label),
                    ("bootstrap_ci95_lower", "Bootstrap CI lower"),
                    ("bootstrap_ci95_upper", "Bootstrap CI upper"),
                    ("test_mae", "Test MAE"),
                ),
            )
        )

    detailed_metrics = _mapping_rows(report.get("detailed_metrics"))
    if detailed_metrics:
        lines.extend(
            _markdown_table(
                "## Required regression and ranking metrics",
                detailed_metrics,
                (
                    ("position", "Position"),
                    ("target_name", "Target"),
                    ("candidate_source", "Source"),
                    ("candidate_name", "Candidate"),
                    ("evaluation_scope", "Scope"),
                    ("rows", "Rows"),
                    ("mae", "MAE"),
                    ("rmse", "RMSE"),
                    ("median_absolute_error", "Median AE"),
                    ("spearman_rank_correlation", "Spearman"),
                    ("top_n", "Top N"),
                    ("top_n_capture_rate", "Mean annual top-N capture"),
                ),
            )
        )

        champion_lookup = {
            (str(row.get("position")), str(row.get("target_name"))): (
                str(row.get("selected_source")),
                str(row.get("selected_name")),
            )
            for row in champions
        }
        champion_segments: list[dict[str, Any]] = []
        for metric in detailed_metrics:
            route = (str(metric.get("position")), str(metric.get("target_name")))
            selected = champion_lookup.get(route)
            if selected != (
                str(metric.get("candidate_source")),
                str(metric.get("candidate_name")),
            ):
                continue
            for segment in _mapping_rows(metric.get("segments")):
                champion_segments.append(
                    {
                        "position": metric.get("position"),
                        "target_name": metric.get("target_name"),
                        "selected_source": metric.get("candidate_source"),
                        "selected_name": metric.get("candidate_name"),
                        "evaluation_scope": metric.get("evaluation_scope"),
                        **segment,
                    }
                )
        if champion_segments:
            lines.extend(
                _markdown_table(
                    "## Champion error by experience and projection tier",
                    champion_segments,
                    (
                        ("position", "Position"),
                        ("target_name", "Target"),
                        ("selected_source", "Source"),
                        ("selected_name", "Champion"),
                        ("evaluation_scope", "Scope"),
                        ("segment_dimension", "Segment type"),
                        ("segment", "Segment"),
                        ("rows", "Rows"),
                        ("mae", "MAE"),
                        ("rmse", "RMSE"),
                        ("median_absolute_error", "Median AE"),
                        ("spearman_rank_correlation", "Spearman"),
                    ),
                )
            )

    candidates = _mapping_rows(report.get("candidate_metrics"))
    if candidates:
        lines.extend(
            _markdown_table(
                "## Candidate comparison",
                candidates,
                (
                    ("position", "Position"),
                    ("target_name", "Target"),
                    ("candidate_source", "Source"),
                    ("candidate_name", "Candidate"),
                    ("validation_rows", "Validation rows"),
                    ("validation_mae", "Validation MAE"),
                    ("test_rows", "Test rows"),
                    ("test_mae", "Test MAE"),
                ),
            )
        )

    interval_rows = _mapping_rows(report.get("interval_metrics", report.get("uncertainty_metrics")))
    if interval_rows:
        lines.extend(
            _markdown_table(
                "## Empirical uncertainty diagnostics",
                interval_rows,
                (
                    ("position", "Position"),
                    ("target_name", "Target"),
                    ("candidate_name", "Candidate"),
                    ("evaluation_scope", "Scope"),
                    ("prediction_season", "Season"),
                    ("projection_tier", "Projection tier"),
                    ("rows", "Rows"),
                    ("empirical_coverage_p10_p90", "P10-P90 coverage"),
                    ("mean_interval_width_p10_p90", "Mean width"),
                    ("pinball_loss_p10", "P10 pinball"),
                    ("pinball_loss_p50", "P50 pinball"),
                    ("pinball_loss_p90", "P90 pinball"),
                ),
            )
        )

    for key, heading in (
        ("prediction_center_semantics", "## Prediction center contract"),
        ("uncertainty_interpretation", "## Uncertainty interpretation"),
        ("rookie_policy", "## Rookie policy"),
        ("rookie_boundary", "## Rookie boundary"),
        ("quality_checks", "## Quality checks"),
        ("limitations", "## Limitations"),
        ("diagnostics", "## Diagnostic artifacts"),
    ):
        if key in report and report[key] not in (None, [], {}):
            lines.extend([heading, "", *_markdown_value(report[key]), ""])

    rendered_keys = {
        "title",
        "status",
        "report_fingerprint",
        "schema_version",
        *run_values,
        "lineage",
        *_LINEAGE_KEYS,
        *split_values,
        *row_counts,
        "row_counts",
        "feature_contract",
        "folds",
        "champions",
        "candidate_metrics",
        "selection",
        "detailed_metrics",
        "interval_metrics",
        "uncertainty_metrics",
        "models",
        "global_explanations",
        "prediction_center_semantics",
        "uncertainty_interpretation",
        "rookie_policy",
        "rookie_boundary",
        "quality_checks",
        "limitations",
        "diagnostics",
        "diagnostic_plots",
    }
    additional = {key: value for key, value in report.items() if key not in rendered_keys}
    if additional:
        lines.extend(["## Additional validated details", "", *_markdown_value(additional), ""])
    lines.extend(
        [
            "## Machine-readable detail",
            "",
            (
                "Per-segment metrics, model inventory, feature contract, and global "
                "explanations are retained in the matching JSON report."
            ),
            "",
        ]
    )
    return "\n".join(lines).rstrip() + "\n"


def _validate_model_card(card: Mapping[str, Any]) -> dict[str, Any]:
    aliases: dict[str, tuple[str, ...]] = {
        "model_id": ("model_id",),
        "trained_at": ("trained_at", "timestamp"),
        "purpose": ("purpose",),
        "target": ("target_name", "target"),
        "training_seasons": ("training_seasons",),
        "data_cutoff": ("data_cutoff", "cutoff", "feature_cutoff"),
        "features": ("feature_names", "features"),
        "missing_value_behavior": ("missing_value_behavior",),
        "hyperparameters": ("hyperparameters",),
        "folds": ("folds", "split_folds"),
        "metrics": ("metrics",),
        "baseline_comparison": ("baseline_comparison", "metrics_vs_baselines"),
        "uncertainty": ("uncertainty",),
        "limitations": ("limitations",),
        "intended_uses": ("intended_uses", "uses"),
        "out_of_scope_uses": ("out_of_scope_uses", "inappropriate_uses"),
        "data_lineage": ("data_lineage", "lineage"),
        "global_explanations": ("global_explanations", "global_explanation"),
    }
    output: dict[str, Any] = {}
    missing: list[str] = []
    for canonical, choices in aliases.items():
        selected = next((choice for choice in choices if choice in card), None)
        if selected is None:
            missing.append(canonical)
        else:
            output[canonical] = card[selected]

    artifact = card.get("artifact")
    artifact_mapping = artifact if isinstance(artifact, Mapping) else {}
    artifact_path = card.get("artifact_path", artifact_mapping.get("path"))
    artifact_sha256 = card.get("artifact_sha256", artifact_mapping.get("sha256"))
    if artifact_path is None:
        missing.append("artifact_path")
    else:
        output["artifact_path"] = artifact_path
    if artifact_sha256 is None:
        missing.append("artifact_sha256")
    else:
        output["artifact_sha256"] = artifact_sha256
    if missing:
        raise ReportingPayloadError(
            "Model card is missing required fields: " + ", ".join(sorted(missing)) + "."
        )
    if not str(output["model_id"]).strip():
        raise ReportingPayloadError("Model card model_id cannot be empty.")
    digest = str(output["artifact_sha256"]).casefold()
    if len(digest) != 64 or any(character not in "0123456789abcdef" for character in digest):
        raise ReportingPayloadError("Model card artifact_sha256 must be a 64-character hex digest.")
    output["artifact_sha256"] = digest
    return output


def _render_model_card(card: Mapping[str, Any], fields: Mapping[str, Any]) -> str:
    model_id = _inline(fields["model_id"])
    lines = [
        f"# Model Card: {model_id}",
        "",
        f"- Model ID: `{model_id}`",
        f"- Trained at: {_inline(fields['trained_at'])}",
        f"- Target: `{_inline(fields['target'])}`",
        f"- Training seasons: {_inline(fields['training_seasons'])}",
        f"- Data cutoff: {_inline(fields['data_cutoff'])}",
        "",
    ]
    sections = (
        ("Purpose", "purpose"),
        ("Feature inputs", "features"),
        ("Missing-value behavior", "missing_value_behavior"),
        ("Hyperparameters", "hyperparameters"),
        ("Chronological folds", "folds"),
        ("Evaluation metrics", "metrics"),
        ("Comparison with transparent baselines", "baseline_comparison"),
        ("Uncertainty estimates", "uncertainty"),
        ("Global explanations", "global_explanations"),
        ("Data lineage", "data_lineage"),
        ("Limitations", "limitations"),
        ("Intended uses", "intended_uses"),
        ("Out-of-scope uses", "out_of_scope_uses"),
    )
    for heading, field in sections:
        lines.extend([f"## {heading}", "", *_markdown_value(fields[field]), ""])

    lines.extend(
        [
            "## Serialized artifact",
            "",
            f"- Project-relative path: `{_inline(fields['artifact_path'])}`",
            f"- SHA-256: `{fields['artifact_sha256']}`",
            "",
        ]
    )
    recognized = {
        "model_id",
        "trained_at",
        "timestamp",
        "purpose",
        "target_name",
        "target",
        "training_seasons",
        "data_cutoff",
        "cutoff",
        "feature_cutoff",
        "feature_names",
        "features",
        "missing_value_behavior",
        "hyperparameters",
        "folds",
        "split_folds",
        "metrics",
        "baseline_comparison",
        "metrics_vs_baselines",
        "uncertainty",
        "limitations",
        "intended_uses",
        "uses",
        "out_of_scope_uses",
        "inappropriate_uses",
        "artifact",
        "artifact_path",
        "artifact_sha256",
        "data_lineage",
        "lineage",
        "global_explanations",
        "global_explanation",
    }
    additional = {key: value for key, value in card.items() if key not in recognized}
    if additional:
        lines.extend(["## Additional metadata", "", *_markdown_value(additional), ""])
    return "\n".join(lines).rstrip() + "\n"


def _plot_season_mae(figure: Any, records: Sequence[Mapping[str, Any]]) -> None:
    groups: dict[tuple[str, str, float], list[tuple[float, float]]] = defaultdict(list)
    for row in records:
        season = _first_number(row, ("prediction_season", "evaluation_season", "season"))
        mae = _first_number(row, ("mae", "validation_mae", "test_mae"))
        if season is not None and mae is not None:
            target = _target_name(row)
            weight = _first_number(row, ("rows", "row_count", "n")) or 1.0
            groups[target, _candidate_family_label(row), season].append((mae, weight))
    if not groups:
        axis = figure.subplots()
        _no_data(axis, "Season MAE comparison")
        return
    targets = _ordered_targets(target for target, _, _ in groups)
    axes = _facet_row(figure, targets)
    for axis, target in zip(axes, targets, strict=True):
        series: dict[str, list[tuple[float, float]]] = defaultdict(list)
        for (row_target, candidate, season), values in sorted(groups.items()):
            if row_target == target:
                series[candidate].append((season, _weighted_mean(values)))
        for label, points in sorted(series.items()):
            ordered = sorted(points)
            axis.plot(
                [point[0] for point in ordered],
                [point[1] for point in ordered],
                marker="o",
                linewidth=1.4,
                markersize=4,
                label=label,
            )
        axis.set_title(_target_label(target))
        axis.set_xlabel("Prediction season")
        axis.set_ylabel("MAE")
        axis.grid(alpha=0.25)
        seasons = sorted({point[0] for points in series.values() for point in points})
        axis.set_xticks(seasons)
    figure.suptitle("Chronological MAE (pooled across positions)")
    _add_shared_legend(figure, axes, max_columns=4)


def _plot_predicted_actual(figure: Any, records: Sequence[Mapping[str, Any]]) -> None:
    _plot_prediction_facets(figure, records, residuals=False)


def _plot_residuals(figure: Any, records: Sequence[Mapping[str, Any]]) -> None:
    _plot_prediction_facets(figure, records, residuals=True)


def _plot_segment_mae(figure: Any, records: Sequence[Mapping[str, Any]]) -> None:
    preferred_scope = (
        "validation"
        if any(str(row.get("evaluation_scope", "")) == "validation" for row in records)
        else None
    )
    groups: dict[tuple[str, str, str], list[tuple[float, float]]] = defaultdict(list)
    for row in records:
        if preferred_scope and str(row.get("evaluation_scope", "")) != preferred_scope:
            continue
        value = _first_number(row, ("mae", "mean_absolute_error"))
        if value is None:
            continue
        dimension = str(row.get("segment_dimension", row.get("scope", "segment")))
        segment = str(row.get("segment", row.get("segment_value", "unknown")))
        weight = _first_number(row, ("rows", "row_count", "n")) or 1.0
        groups[
            _target_name(row),
            _candidate_family_label(row),
            f"{_humanize(dimension)}: {segment}",
        ].append((value, weight))
    if not groups:
        axis = figure.subplots()
        _no_data(axis, "Segment MAE")
        return
    aggregated = {key: _weighted_mean(values) for key, values in groups.items()}
    targets = _ordered_targets(target for target, _, _ in aggregated)
    axes = _facet_row(figure, targets)
    candidates = sorted({candidate for _, candidate, _ in aggregated})
    for axis, target in zip(axes, targets, strict=True):
        segment_scores: dict[str, float] = defaultdict(float)
        for (row_target, _, segment), value in aggregated.items():
            if row_target == target:
                segment_scores[segment] = max(segment_scores[segment], value)
        segments = [
            name
            for name, _ in sorted(segment_scores.items(), key=lambda item: (-item[1], item[0]))[:8]
        ]
        y_positions = list(range(len(segments)))
        bar_height = 0.8 / max(1, len(candidates))
        for candidate_index, candidate in enumerate(candidates):
            plotted_y: list[float] = []
            values: list[float] = []
            for segment_index, segment in enumerate(segments):
                value = aggregated.get((target, candidate, segment))
                if value is not None:
                    plotted_y.append(
                        segment_index - 0.4 + bar_height / 2 + candidate_index * bar_height
                    )
                    values.append(value)
            if values:
                axis.barh(
                    plotted_y,
                    values,
                    height=bar_height,
                    label=candidate,
                )
        axis.set_yticks(y_positions, labels=segments, fontsize=8)
        axis.invert_yaxis()
        axis.set_title(_target_label(target))
        axis.set_xlabel("MAE")
        axis.grid(axis="x", alpha=0.2)
    scope_label = "validation" if preferred_scope else "available"
    figure.suptitle(f"{scope_label.title()} segment MAE (pooled across positions)")
    _add_shared_legend(figure, axes, max_columns=4)


def _plot_intervals(figure: Any, records: Sequence[Mapping[str, Any]]) -> None:
    coverage_groups: dict[tuple[str, str], list[tuple[float, float]]] = defaultdict(list)
    width_groups: dict[tuple[str, str], list[tuple[float, float]]] = defaultdict(list)
    for index, row in enumerate(records):
        season = _first_number(row, ("prediction_season", "evaluation_season", "season"))
        x_value = float(index) if season is None else season
        coverage = _first_number(
            row, ("empirical_coverage_p10_p90", "coverage", "interval_coverage")
        )
        width = _first_number(row, ("mean_interval_width_p10_p90", "mean_width", "interval_width"))
        target = _target_name(row)
        label = _position_candidate_label(row)
        if coverage is not None:
            coverage_groups[target, label].append((x_value, coverage))
        if width is not None:
            width_groups[target, label].append((x_value, width))
    if not coverage_groups and not width_groups:
        axis = figure.subplots()
        _no_data(axis, "Interval coverage and width")
        return
    targets = _ordered_targets(target for target, _ in {*coverage_groups, *width_groups})
    axes_array = figure.subplots(2, len(targets), squeeze=False, sharex="col")
    all_axes = [axis for row in axes_array for axis in row]
    for target_index, target in enumerate(targets):
        coverage_axis = axes_array[0][target_index]
        width_axis = axes_array[1][target_index]
        for (row_target, label), points in sorted(coverage_groups.items()):
            if row_target == target:
                ordered = sorted(points)
                coverage_axis.plot(
                    *zip(*ordered, strict=True),
                    label=label,
                    **_route_style(label, for_line=True),
                )
        for (row_target, label), points in sorted(width_groups.items()):
            if row_target == target:
                ordered = sorted(points)
                width_axis.plot(
                    *zip(*ordered, strict=True),
                    label=label,
                    **_route_style(label, for_line=True),
                )
        coverage_axis.axhline(0.8, linestyle="--", color="#555555", linewidth=1.0)
        coverage_axis.text(
            0.98,
            0.82,
            "80% nominal",
            fontsize=7,
            color="#555555",
            horizontalalignment="right",
            transform=coverage_axis.transAxes,
        )
        coverage_axis.set_title(_target_label(target))
        coverage_axis.set_ylim(0.0, 1.02)
        coverage_axis.set_ylabel("Coverage")
        width_axis.set_xlabel("Prediction season")
        width_axis.set_ylabel("Mean width")
        seasons = sorted(
            {
                point[0]
                for (row_target, _), points in {
                    **coverage_groups,
                    **width_groups,
                }.items()
                if row_target == target
                for point in points
            }
        )
        width_axis.set_xticks(seasons)
    for axis in all_axes:
        axis.grid(alpha=0.2)
    figure.suptitle("P10-P90 interval calibration by target and learned route")
    _add_shared_legend(figure, all_axes, max_columns=4)


def _plot_importance(
    figure: Any,
    records: Sequence[Mapping[str, Any]],
    *,
    title: str,
    value_keys: Sequence[str],
    x_label: str,
    signed: bool,
) -> None:
    rows: list[tuple[str, str, float]] = []
    for row in records:
        value = _first_number(row, value_keys)
        feature = row.get("feature")
        if value is not None and feature is not None:
            route = " / ".join(
                (
                    str(row.get("position", "route")),
                    _target_abbreviation(_target_name(row)),
                    _compact_feature_name(str(feature)),
                )
            )
            rows.append((_target_name(row), route, value))
    if not rows:
        axis = figure.subplots()
        _no_data(axis, title)
        return
    targets = _ordered_targets(row[0] for row in rows)
    axes = _facet_row(figure, targets)
    for axis, target in zip(axes, targets, strict=True):
        selected = sorted(
            (row for row in rows if row[0] == target),
            key=lambda item: (-abs(item[2]), item[1]),
        )[:_MAX_IMPORTANCE_BARS_PER_TARGET]
        selected.reverse()
        values = [row[2] for row in selected]
        colors = (
            ["#3274A1" if value >= 0.0 else "#C44E52" for value in values] if signed else "#3274A1"
        )
        axis.barh([row[1] for row in selected], values, color=colors)
        if signed:
            axis.axvline(0.0, color="#555555", linewidth=0.8)
        axis.set_title(_target_label(target))
        axis.set_xlabel(x_label)
        axis.tick_params(axis="y", labelsize=7)
        axis.grid(axis="x", alpha=0.2)
    figure.suptitle(
        f"{title} (top {_MAX_IMPORTANCE_BARS_PER_TARGET} route-feature pairs per target)"
    )


def _plot_feature_response(figure: Any, records: Sequence[Mapping[str, Any]]) -> None:
    no_records = not records
    groups: dict[tuple[str, str, str], list[tuple[float, float]]] = defaultdict(list)
    ranks: dict[tuple[str, str, str], float] = {}
    for row in records:
        feature = str(row.get("feature", "feature"))
        key = (_target_name(row), str(row.get("position", "route")), feature)
        rank = _first_number(row, ("response_rank", "rank")) or math.inf
        ranks[key] = min(rank, ranks.get(key, math.inf))
        points = row.get("points")
        if isinstance(points, Sequence) and not isinstance(points, (str, bytes)):
            for point in points:
                if not isinstance(point, Mapping):
                    continue
                x_value = _first_number(point, ("feature_value", "value", "x"))
                y_value = _first_number(
                    point, ("average_prediction", "predicted_response", "response", "y")
                )
                if x_value is not None and y_value is not None:
                    groups[key].append((x_value, y_value))
            continue
        x_value = _first_number(row, ("feature_value", "value", "x"))
        y_value = _first_number(row, ("average_prediction", "predicted_response", "response", "y"))
        if x_value is not None and y_value is not None:
            groups[key].append((x_value, y_value))
    # Each target-position route owns one axis. Different feature units are
    # therefore never overlaid, and a failed/unstable response cannot silently
    # remove a production route from the tracked figure.
    route_choices: dict[tuple[str, str], tuple[str, str, str]] = {}
    for key in sorted(
        groups,
        key=lambda item: (
            _target_sort_key(item[0]),
            _position_sort_key(item[1]),
            ranks[item],
            item[2],
        ),
    ):
        route_choices.setdefault((key[0], key[1]), key)
    axes_array = figure.subplots(
        len(_TARGET_ORDER),
        len(_POSITION_ORDER),
        squeeze=False,
    )
    for target_index, target in enumerate(_TARGET_ORDER):
        for position_index, position in enumerate(_POSITION_ORDER):
            axis = axes_array[target_index][position_index]
            axis.set_title(f"{position} / {_target_abbreviation(target)}", fontsize=9)
            selected_key = route_choices.get((target, position))
            if selected_key is None:
                axis.text(
                    0.5,
                    0.5,
                    "No stable numeric response",
                    fontsize=8,
                    color="#555555",
                    horizontalalignment="center",
                    verticalalignment="center",
                    wrap=True,
                    transform=axis.transAxes,
                )
                axis.set_xticks([])
                axis.set_yticks([])
                continue
            _, _, feature = selected_key
            ordered = sorted(groups[selected_key])
            axis.plot(
                [point[0] for point in ordered],
                [point[1] for point in ordered],
                marker="o",
                markersize=3,
                linewidth=1.5,
                color="#3274A1",
            )
            axis.set_xlabel(_compact_feature_name(feature), fontsize=8)
            axis.set_ylabel("Average prediction", fontsize=8)
            axis.tick_params(labelsize=7)
            axis.grid(alpha=0.2)
    title = "Leading one-way feature response by route (associative, not causal)"
    figure.suptitle(f"{title} — No records supplied" if no_records else title)


def _normalize_plot_records(
    records: Mapping[str, Sequence[Mapping[str, Any]]],
) -> dict[str, list[dict[str, Any]]]:
    if not isinstance(records, Mapping):
        raise ReportingPayloadError("Diagnostic records must be a mapping of record groups.")
    expected = {
        "season_metrics",
        "test_predictions",
        "residuals",
        "segment_metrics",
        "interval_metrics",
        "ridge_coefficients",
        "hgb_permutation_importance",
        "feature_responses",
    }
    unknown = sorted(set(records) - expected)
    if unknown:
        raise ReportingPayloadError(f"Unknown diagnostic record groups: {unknown}.")
    output: dict[str, list[dict[str, Any]]] = {}
    for name in sorted(expected):
        rows = records.get(name, ())
        if isinstance(rows, (str, bytes)) or not isinstance(rows, Sequence):
            raise ReportingPayloadError(f"Diagnostic group {name!r} must be a record sequence.")
        normalized_rows: list[dict[str, Any]] = []
        for index, row in enumerate(rows):
            if not isinstance(row, Mapping):
                raise ReportingPayloadError(
                    f"Diagnostic group {name!r} row {index} is not a mapping."
                )
            normalized_rows.append(_json_mapping(row, label=f"{name} row {index}"))
        output[name] = normalized_rows
    return output


def _plot_prediction_facets(
    figure: Any,
    records: Sequence[Mapping[str, Any]],
    *,
    residuals: bool,
) -> None:
    available_seasons = [
        season
        for row in records
        if (season := _first_number(row, ("prediction_season", "evaluation_season", "season")))
        is not None
    ]
    latest_season = max(available_seasons) if available_seasons else None
    groups: dict[tuple[str, str], list[tuple[float, float, str]]] = defaultdict(list)
    for row_index, row in enumerate(records):
        season = _first_number(row, ("prediction_season", "evaluation_season", "season"))
        if latest_season is not None and season != latest_season:
            continue
        actual = _first_number(row, ("actual_value", "actual", "y_true"))
        predicted = _first_number(row, ("predicted_value", "prediction", "y_pred", "p50"))
        if actual is None or predicted is None:
            continue
        entity_id = str(row.get("player_id", row.get("entity_id", row_index)))
        groups[_target_name(row), _position_candidate_label(row)].append(
            (actual, predicted, entity_id)
        )
    if not groups:
        axis = figure.subplots()
        _no_data(axis, "Test residuals" if residuals else "Test predicted vs. actual")
        return
    targets = _ordered_targets(target for target, _ in groups)
    axes = _facet_row(figure, targets)
    for axis, target in zip(axes, targets, strict=True):
        plotted_points: list[tuple[float, float]] = []
        for (row_target, label), points in sorted(groups.items()):
            if row_target != target:
                continue
            sampled = _sample_prediction_points(points, limit=_MAX_SCATTER_POINTS_PER_ROUTE)
            actual_values = [point[0] for point in sampled]
            predicted_values = [point[1] for point in sampled]
            x_values = predicted_values if residuals else actual_values
            y_values = (
                [
                    actual_value - prediction
                    for actual_value, prediction in zip(
                        actual_values, predicted_values, strict=True
                    )
                ]
                if residuals
                else predicted_values
            )
            axis.scatter(
                x_values,
                y_values,
                s=14,
                alpha=0.45,
                label=label,
                **_route_style(label, for_line=False),
            )
            plotted_points.extend(zip(actual_values, predicted_values, strict=True))
        if residuals:
            axis.axhline(0.0, linestyle="--", color="#555555", linewidth=1.0)
            axis.set_xlabel("Predicted")
            axis.set_ylabel("Residual (actual - predicted)")
        elif plotted_points:
            values = [value for point in plotted_points for value in point]
            lower = min(values)
            upper = max(values)
            axis.plot(
                [lower, upper],
                [lower, upper],
                linestyle="--",
                color="#555555",
                linewidth=1.0,
            )
            axis.set_xlabel("Actual")
            axis.set_ylabel("Predicted")
        axis.set_title(_target_label(target))
        axis.grid(alpha=0.2)
    plot_name = "Test residuals" if residuals else "Test predicted vs. actual"
    season_label = "" if latest_season is None else f" ({int(latest_season)})"
    figure.suptitle(
        f"{plot_name}{season_label}; up to {_MAX_SCATTER_POINTS_PER_ROUTE} points per route"
    )
    _add_shared_legend(figure, axes, max_columns=4)


def _sample_prediction_points(
    points: Sequence[tuple[float, float, str]], *, limit: int
) -> list[tuple[float, float, str]]:
    ordered = sorted(points, key=lambda point: (point[0], point[1], point[2]))
    if len(ordered) <= limit:
        return ordered
    indices = [round(index * (len(ordered) - 1) / (limit - 1)) for index in range(limit)]
    return [ordered[index] for index in indices]


def _facet_row(figure: Any, targets: Sequence[str]) -> list[Any]:
    axes = figure.subplots(1, len(targets), squeeze=False)
    return list(axes[0])


def _add_shared_legend(figure: Any, axes: Sequence[Any], *, max_columns: int) -> None:
    entries: dict[str, Any] = {}
    for axis in axes:
        handles, labels = axis.get_legend_handles_labels()
        for handle, label in zip(handles, labels, strict=True):
            if label and not label.startswith("_"):
                entries.setdefault(label, handle)
    if not entries:
        return
    labels = sorted(entries)
    figure.legend(
        [entries[label] for label in labels],
        labels,
        loc="outside lower center",
        ncol=min(max_columns, len(labels)),
        fontsize="x-small",
        frameon=False,
    )


def _weighted_mean(values: Sequence[tuple[float, float]]) -> float:
    positive = [(value, weight) for value, weight in values if weight > 0.0]
    if positive:
        return sum(value * weight for value, weight in positive) / sum(
            weight for _, weight in positive
        )
    return sum(value for value, _ in values) / len(values)


def _target_name(row: Mapping[str, Any]) -> str:
    value = row.get("target_name", row.get("target", "all_targets"))
    return str(value) if value not in (None, "") else "all_targets"


def _ordered_targets(targets: Iterable[str]) -> list[str]:
    return sorted(set(str(target) for target in targets), key=_target_sort_key)


def _target_sort_key(target: str) -> tuple[int, str]:
    try:
        return (_TARGET_ORDER.index(target), target)
    except ValueError:
        return (len(_TARGET_ORDER), target)


def _position_sort_key(position: str) -> tuple[int, str]:
    try:
        return (_POSITION_ORDER.index(position), position)
    except ValueError:
        return (len(_POSITION_ORDER), position)


def _target_label(target: str) -> str:
    if target == "all_targets":
        return "All targets"
    return _TARGET_LABELS.get(target, _humanize(target))


def _target_abbreviation(target: str) -> str:
    return {
        "fantasy_points_per_game": "PPG",
        "games_active": "Games",
        "fantasy_points_total": "Total",
        "all_targets": "All",
    }.get(target, _humanize(target))


def _candidate_name(row: Mapping[str, Any]) -> str:
    value = next(
        (
            row[key]
            for key in (
                "candidate_name",
                "candidate",
                "model_name",
                "model_family",
                "baseline_name",
                "name",
            )
            if key in row and row[key] not in (None, "")
        ),
        "candidate",
    )
    text = str(value)
    if ":" in text and text.split(":", 1)[0] in {"learned", "baseline"}:
        text = text.split(":", 1)[1]
    return text


def _display_candidate(name: str) -> str:
    return {
        "ridge": "Ridge",
        "hist_gradient_boosting": "HGB",
        "hgb": "HGB",
    }.get(name, _humanize(name))


def _candidate_family_label(row: Mapping[str, Any]) -> str:
    candidate = _display_candidate(_candidate_name(row))
    source = str(row.get("candidate_source", "")).strip()
    return f"{source.title()} · {candidate}" if source else candidate


def _position_candidate_label(row: Mapping[str, Any]) -> str:
    position = str(row.get("position", "route"))
    return f"{position} · {_display_candidate(_candidate_name(row))}"


def _route_style(label: str, *, for_line: bool) -> dict[str, Any]:
    position, _, candidate = label.partition(" · ")
    color = _POSITION_COLORS.get(position, "#3274A1")
    hgb = candidate.casefold() == "hgb" or "gradient" in candidate.casefold()
    if for_line:
        return {
            "color": color,
            "linestyle": "--" if hgb else "-",
            "marker": "^" if hgb else "o",
        }
    return {"color": color, "marker": "^" if hgb else "o"}


def _compact_feature_name(feature: str) -> str:
    compact = feature.removeprefix("numeric__").removeprefix("categorical__")
    compact = compact.replace("_", " ")
    return compact if len(compact) <= 32 else compact[:29].rstrip() + "..."


def _first_number(row: Mapping[str, Any], keys: Sequence[str]) -> float | None:
    for key in keys:
        if key not in row or row[key] is None:
            continue
        value = row[key]
        if isinstance(value, bool):
            continue
        try:
            numeric = float(cast(Any, value))
        except (TypeError, ValueError):
            continue
        if math.isfinite(numeric):
            return numeric
    return None


def _no_data(axis: Any, title: str) -> None:
    axis.set_title(title)
    axis.text(
        0.5,
        0.5,
        "No records supplied",
        horizontalalignment="center",
        verticalalignment="center",
        transform=axis.transAxes,
    )
    axis.set_axis_off()


def _figure_svg_bytes(figure: Any) -> bytes:
    buffer = io.BytesIO()
    figure.savefig(
        buffer,
        format="svg",
        metadata={"Date": None, "Creator": "fantasy-football-draft-ai"},
    )
    return buffer.getvalue()


def _load_matplotlib() -> tuple[Any, Any]:
    try:
        matplotlib = importlib.import_module("matplotlib")
        matplotlib.use("Agg", force=True)
        pyplot = importlib.import_module("matplotlib.pyplot")
    except ImportError as exc:
        raise RuntimeError(
            "SVG diagnostics require the optional modeling dependencies. "
            'Install them with: pip install -e ".[modeling]"'
        ) from exc
    return matplotlib, pyplot


def _resolve_project_output(
    project_root: Path, output_path: str | Path, expected_suffix: str
) -> tuple[Path, str]:
    raw = str(output_path).strip()
    if not raw:
        raise ReportingPathError("Output path cannot be empty.")
    root = project_root.resolve()
    supplied = Path(raw)
    candidate = (supplied if supplied.is_absolute() else root / supplied).resolve()
    try:
        relative = candidate.relative_to(root)
    except ValueError as exc:
        raise ReportingPathError("Output path resolves outside the project directory.") from exc
    if candidate == root or candidate.suffix.casefold() != expected_suffix.casefold():
        raise ReportingPathError(f"Output path must name a {expected_suffix} file in the project.")
    return candidate, relative.as_posix()


def _resolve_project_directory(project_root: Path, directory: str | Path) -> tuple[Path, str]:
    raw = str(directory).strip()
    if not raw:
        raise ReportingPathError("Output directory cannot be empty.")
    root = project_root.resolve()
    supplied = Path(raw)
    candidate = (supplied if supplied.is_absolute() else root / supplied).resolve()
    try:
        relative = candidate.relative_to(root)
    except ValueError as exc:
        raise ReportingPathError("Output directory resolves outside the project.") from exc
    if candidate == root:
        raise ReportingPathError("Diagnostic output directory must be below the project root.")
    return candidate, relative.as_posix()


def _atomic_write(path: Path, content: bytes) -> None:
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


def _json_mapping(value: Mapping[str, Any], *, label: str) -> dict[str, Any]:
    if not isinstance(value, Mapping):
        raise ReportingPayloadError(f"{label.capitalize()} must be a mapping.")
    try:
        normalized = json.loads(_canonical_json(dict(value)))
    except (TypeError, ValueError) as exc:
        raise ReportingPayloadError(f"{label.capitalize()} must contain JSON-safe values.") from exc
    if not isinstance(normalized, dict):
        raise ReportingPayloadError(f"{label.capitalize()} must normalize to an object.")
    return {str(key): item for key, item in normalized.items()}


def _combined_lineage(report: Mapping[str, Any]) -> dict[str, Any]:
    output: dict[str, Any] = {}
    supplied = report.get("lineage")
    if isinstance(supplied, Mapping):
        output.update({str(key): value for key, value in supplied.items()})
    for key in _LINEAGE_KEYS:
        if key in report:
            output[key] = report[key]
    return dict(sorted(output.items()))


def _mapping_rows(value: Any) -> list[dict[str, Any]]:
    if not isinstance(value, Sequence) or isinstance(value, (str, bytes)):
        return []
    return [dict(row) for row in value if isinstance(row, Mapping)]


def _markdown_table(
    heading: str,
    rows: Sequence[Mapping[str, Any]],
    columns: Sequence[tuple[str, str]],
) -> list[str]:
    visible = [(key, label) for key, label in columns if any(key in row for row in rows)]
    if not visible:
        return []
    lines = [heading, "", "| " + " | ".join(label for _, label in visible) + " |"]
    lines.append("|" + "|".join("---" for _ in visible) + "|")
    for row in rows:
        lines.append("| " + " | ".join(_table_value(row.get(key)) for key, _ in visible) + " |")
    lines.append("")
    return lines


def _markdown_value(value: Any) -> list[str]:
    if isinstance(value, Sequence) and not isinstance(value, (str, bytes)):
        if not value:
            return ["None reported."]
        if all(_is_scalar(item) for item in value):
            return [f"- {_inline(item)}" for item in value]
    if _is_scalar(value):
        return [_inline(value)]
    return ["````json", _canonical_json(value, indent=2), "````"]


def _inline(value: Any) -> str:
    if value is None:
        return "n/a"
    if isinstance(value, bool):
        return "yes" if value else "no"
    if isinstance(value, float):
        return _format_number(value)
    if isinstance(value, Sequence) and not isinstance(value, (str, bytes)):
        return ", ".join(_inline(item) for item in value)
    return str(value).replace("\r", " ").replace("\n", " ")


def _table_value(value: Any) -> str:
    return _inline(value).replace("|", "\\|")


def _format_number(value: Any) -> str:
    if isinstance(value, bool):
        return str(value)
    if isinstance(value, int):
        return f"{value:,}"
    if isinstance(value, float):
        return f"{value:.6g}"
    return str(value)


def _humanize(key: str) -> str:
    return key.replace("_", " ").capitalize()


def _is_scalar(value: Any) -> bool:
    return value is None or isinstance(value, (str, int, float, bool))


def _canonical_json(value: object, *, indent: int | None = None) -> str:
    return json.dumps(
        value,
        sort_keys=True,
        separators=(",", ":") if indent is None else None,
        ensure_ascii=True,
        allow_nan=False,
        indent=indent,
    )


def _sha256_bytes(content: bytes) -> str:
    return hashlib.sha256(content).hexdigest()
