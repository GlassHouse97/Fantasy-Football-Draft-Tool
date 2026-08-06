from __future__ import annotations

import hashlib
import json
from datetime import UTC, datetime
from pathlib import Path
from types import SimpleNamespace
from typing import Any

import duckdb
import pytest

from fantasy_draft_ai.config import (
    AppConfig,
    NetworkSection,
    PathSection,
    ProjectSection,
    TrainingSection,
)
from fantasy_draft_ai.data.warehouse import Warehouse
from fantasy_draft_ai.models.player_projection import repository
from fantasy_draft_ai.models.player_projection import train as training
from fantasy_draft_ai.models.player_projection.reporting import write_evaluation_report


def _config(tmp_path: Path) -> AppConfig:
    return AppConfig(
        project=ProjectSection(name="test", prediction_season=2026, random_seed=42),
        paths=PathSection(
            data_dir=Path("data"),
            raw_dir=Path("data/raw"),
            processed_dir=Path("data/processed"),
            warehouse=Path("data/warehouse.duckdb"),
            manifests=Path("data/manifests"),
        ),
        network=NetworkSection(timeout_seconds=30, user_agent="tests"),
        training=TrainingSection(start_season=2016, end_season=2025),
        project_root=tmp_path,
    )


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def test_registered_text_hash_is_stable_across_git_line_endings(tmp_path: Path) -> None:
    card = tmp_path / "model-card.md"
    card.write_bytes(b"# Model\r\n\r\nValidated text.\r\n")
    expected = hashlib.sha256(b"# Model\n\nValidated text.\n").hexdigest()

    text_issues: list[str] = []
    repository._audit_registered_file(
        tmp_path,
        card.name,
        expected,
        None,
        "model card",
        text_issues,
    )
    assert text_issues == []

    binary_issues: list[str] = []
    repository._audit_registered_file(
        tmp_path,
        card.name,
        expected,
        None,
        "artifact",
        binary_issues,
    )
    assert binary_issues == [f"A registered Phase 4 artifact hash does not match: {card.name}."]


_PHASE4_TABLES = (
    "player_projection_runs",
    "player_projection_models",
    "player_projection_predictions",
    "player_projection_champions",
    "player_projection_evaluation_metadata",
    "player_projection_board",
)


def _publication_records(
    run_id: str,
    marker: str,
    *,
    status: str,
    with_dependents: bool,
) -> dict[str, Any]:
    lineage = {
        "feature_data_fingerprint": f"{marker}-feature",
        "target_data_fingerprint": f"{marker}-target",
        "build_fingerprint": f"{marker}-build",
        "scoring_ruleset_fingerprint": f"{marker}-rules",
        "baseline_report_fingerprint": f"{marker}-baseline",
        "model_feature_fingerprint": f"{marker}-model-features",
        "model_config_fingerprint": f"{marker}-model-config",
    }
    model_id = f"{run_id}-{marker}-model"
    report_fingerprint = f"{marker}-report"
    models = (
        [
            {
                "model_id": model_id,
                "run_id": run_id,
                "model_family": "ridge",
                "target_name": "fantasy_points_total",
                "position": "WR",
                "training_seasons": "[2024]",
                "training_rows": 1,
                "feature_names": "[]",
                "categorical_feature_names": "[]",
                "hyperparameters": "{}",
                "uncertainty_method": "test",
                "artifact_path": f"models/artifacts/{marker}.joblib",
                "artifact_sha256": marker,
                "artifact_size_bytes": 1,
                "model_card_path": f"docs/model_cards/{marker}.md",
                "model_card_sha256": marker,
                "package_versions": "{}",
            }
        ]
        if with_dependents
        else []
    )
    predictions = (
        [
            {
                "run_id": run_id,
                "player_id": f"{marker}-player",
                "prediction_season": 2025,
                "position": "WR",
                "target_name": "fantasy_points_total",
                "model_family": "ridge",
                "prediction_scope": "validation",
                "fold_label": "validation",
                "training_max_season": 2024,
                "predicted_value": 10.0,
                "p10": 8.0,
                "p50": 10.0,
                "p90": 12.0,
                "actual_value": 11.0,
                "actual_games_active": 1.0,
                "experience": 1,
                "experience_group": "veteran",
                **lineage,
            }
        ]
        if with_dependents
        else []
    )
    champions = (
        [
            {
                "run_id": run_id,
                "target_name": "fantasy_points_total",
                "position": "WR",
                "selected_source": "learned",
                "selected_name": "ridge",
                "model_id": model_id,
                "selection_metric": "mae",
                "selection_value": 1.0,
                "reference_baseline_name": "weighted_history",
                "reference_baseline_value": 2.0,
                "improvement": 1.0,
                "selection_payload": json.dumps({"marker": marker}),
            }
        ]
        if with_dependents
        else []
    )
    board = (
        [
            {
                "run_id": run_id,
                "player_id": f"{marker}-player",
                "prediction_season": 2026,
                "position": "WR",
                "fantasy_points_per_game_p10": 1.0,
                "fantasy_points_per_game_p50": 2.0,
                "fantasy_points_per_game_p90": 3.0,
                "fantasy_points_per_game_selected_source": "learned",
                "fantasy_points_per_game_selected_name": "ridge",
                "games_active_p10": 1.0,
                "games_active_p50": 2.0,
                "games_active_p90": 3.0,
                "games_active_selected_source": "learned",
                "games_active_selected_name": "ridge",
                "fantasy_points_total_p10": 1.0,
                "fantasy_points_total_p50": 2.0,
                "fantasy_points_total_p90": 3.0,
                "fantasy_points_total_selected_source": "learned",
                "fantasy_points_total_selected_name": "ridge",
                "prediction_status": "learned_models_validated",
                "explanation_payload": json.dumps({"marker": marker}),
                **lineage,
                "evaluation_report_fingerprint": report_fingerprint,
            }
        ]
        if with_dependents
        else []
    )
    run = {
        "run_id": run_id,
        **lineage,
        "split_seasons": "[]",
        "feature_rows": int(with_dependents),
        "target_rows": int(with_dependents),
        "training_rows": int(with_dependents),
        "prediction_rows": len(predictions),
        "evaluated_rows": len(predictions),
        "live_prediction_rows": 0,
        "candidate_rows": int(with_dependents),
        "model_rows": len(models),
        "champion_rows": len(champions),
        "status": status,
        "trained_at": datetime(2026, 8, 5, 12, tzinfo=UTC),
        "run_payload": json.dumps({"marker": marker}),
    }
    evaluation = {
        "report_fingerprint": report_fingerprint,
        "run_id": run_id,
        **lineage,
        "prediction_rows": len(predictions),
        "evaluated_rows": len(predictions),
        "live_prediction_rows": 0,
        "candidate_rows": int(with_dependents),
        "champion_rows": len(champions),
        "report_payload": json.dumps({"marker": marker}),
    }
    return {
        "run": run,
        "models": models,
        "predictions": predictions,
        "champions": champions,
        "evaluation": evaluation,
        "board": board,
    }


def _insert_publication(config: AppConfig, records: dict[str, Any]) -> None:
    warehouse = Warehouse(config.resolve(config.paths.warehouse))
    warehouse.initialize()
    table_records = (
        ("player_projection_runs", repository.RUN_COLUMNS, [records["run"]]),
        ("player_projection_models", repository.MODEL_COLUMNS, records["models"]),
        ("player_projection_predictions", repository.PREDICTION_COLUMNS, records["predictions"]),
        ("player_projection_champions", repository.CHAMPION_COLUMNS, records["champions"]),
        (
            "player_projection_evaluation_metadata",
            repository.EVALUATION_COLUMNS,
            [records["evaluation"]],
        ),
        ("player_projection_board", repository.BOARD_COLUMNS, records["board"]),
    )
    with warehouse.connect() as connection:
        for table, columns, rows in table_records:
            if not rows:
                continue
            placeholders = ", ".join("?" for _ in columns)
            connection.executemany(
                f"INSERT INTO {table} ({', '.join(columns)}) VALUES ({placeholders})",
                [tuple(row[column] for column in columns) for row in rows],
            )


def _publication_snapshot(config: AppConfig) -> dict[str, list[tuple[Any, ...]]]:
    warehouse = Warehouse(config.resolve(config.paths.warehouse))
    with warehouse.connect(read_only=True) as connection:
        return {
            table: connection.execute(f"SELECT * FROM {table} ORDER BY ALL").fetchall()
            for table in _PHASE4_TABLES
        }


def _insert_reusable_run(
    config: AppConfig,
    *,
    run_id: str,
    report: dict[str, Any],
    registered_outputs: dict[str, Any],
) -> None:
    warehouse_path = config.resolve(config.paths.warehouse)
    warehouse_path.parent.mkdir(parents=True, exist_ok=True)
    with duckdb.connect(str(warehouse_path)) as connection:
        connection.execute(
            """
            CREATE TABLE player_projection_runs (
                run_id VARCHAR,
                model_rows INTEGER,
                prediction_rows INTEGER,
                evaluated_rows INTEGER,
                live_prediction_rows INTEGER,
                champion_rows INTEGER,
                status VARCHAR,
                run_payload JSON
            )
            """
        )
        connection.execute(
            """
            CREATE TABLE player_projection_evaluation_metadata (
                run_id VARCHAR,
                report_payload JSON
            )
            """
        )
        connection.execute("CREATE TABLE player_projection_board (run_id VARCHAR)")
        connection.execute(
            "INSERT INTO player_projection_runs VALUES (?, 0, 0, 0, 0, 0, 'complete', ?)",
            [run_id, json.dumps(registered_outputs)],
        )
        connection.execute(
            "INSERT INTO player_projection_evaluation_metadata VALUES (?, ?)",
            [run_id, json.dumps(report)],
        )


def test_reuse_rewrites_both_requested_reports_and_registry_from_authoritative_run(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    config = _config(tmp_path)
    run_id = "phase4-reusable"
    report: dict[str, Any] = {
        "title": "Reusable Phase 4 report",
        "status": "PASSED",
        "run_id": run_id,
    }
    report_files = write_evaluation_report(
        tmp_path,
        report,
        json_path=f"models/reports/{run_id}/evaluation.json",
        markdown_path=f"models/reports/{run_id}/evaluation.md",
    )
    report["report_fingerprint"] = report_files["report_fingerprint"]
    registry_source = tmp_path / "models" / "reports" / run_id / "registry.json"
    registry_source.write_text(
        json.dumps({"active_run_id": run_id}, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    registered_outputs = {
        "report_files": report_files,
        "registry": {
            "path": registry_source.relative_to(tmp_path).as_posix(),
            "sha256": _sha256(registry_source),
        },
    }
    _insert_reusable_run(
        config,
        run_id=run_id,
        report=report,
        registered_outputs=registered_outputs,
    )
    monkeypatch.setattr(training, "projection_integrity_issues", lambda _config: ())
    requested_markdown = tmp_path / "docs" / "requested.md"
    requested_json = tmp_path / "docs" / "requested.json"
    requested_markdown.parent.mkdir(parents=True)
    requested_markdown.write_text("unrelated markdown\n", encoding="utf-8")
    requested_json.write_text('{"unrelated":true}\n', encoding="utf-8")

    result = training._reuse_current_run(
        config,
        run_id,
        Path("docs/requested.md"),
        Path("docs/requested.json"),
    )

    assert result is not None and result.reused
    assert result.report_path == requested_markdown.resolve()
    assert (
        requested_markdown.read_bytes()
        == (tmp_path / str(report_files["markdown_path"])).read_bytes()
    )
    assert requested_json.read_bytes() == (tmp_path / str(report_files["json_path"])).read_bytes()
    assert (tmp_path / "models" / "registry.json").read_bytes() == registry_source.read_bytes()


def test_integrity_failure_rolls_back_all_six_prior_publication_tables(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    config = _config(tmp_path)
    run_id = "phase4-force-run"
    prior = _publication_records(
        run_id,
        "prior",
        status="complete",
        with_dependents=True,
    )
    attempted = _publication_records(
        run_id,
        "attempted",
        status="validating",
        with_dependents=False,
    )
    _insert_publication(config, prior)
    before = _publication_snapshot(config)
    assert all(before.values())

    def fail_integrity(
        _config: AppConfig,
        *,
        expected_status: str = "complete",
        connection: duckdb.DuckDBPyConnection | None = None,
    ) -> tuple[str, ...]:
        assert expected_status == "validating"
        assert connection is not None
        assert connection.execute("SELECT status FROM player_projection_runs").fetchone() == (
            "validating",
        )
        assert connection.execute("SELECT count(*) FROM player_projection_models").fetchone() == (
            0,
        )
        return ("injected integrity failure",)

    monkeypatch.setattr(repository, "projection_integrity_issues", fail_integrity)

    with pytest.raises(RuntimeError, match="injected integrity failure"):
        repository.persist_projection_run(config, **attempted)

    after = _publication_snapshot(config)
    assert after == before
    assert after["player_projection_runs"][0][18] == "complete"


def test_promotion_failure_rolls_back_all_six_prior_publication_tables(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    config = _config(tmp_path)
    run_id = "phase4-force-run"
    prior = _publication_records(
        run_id,
        "prior",
        status="complete",
        with_dependents=True,
    )
    attempted = _publication_records(
        run_id,
        "attempted",
        status="validating",
        with_dependents=False,
    )
    _insert_publication(config, prior)
    before = _publication_snapshot(config)
    assert all(before.values())

    def pass_integrity(
        _config: AppConfig,
        *,
        expected_status: str = "complete",
        connection: duckdb.DuckDBPyConnection | None = None,
    ) -> tuple[str, ...]:
        assert expected_status == "validating"
        assert connection is not None
        return ()

    def fail_promotion(connection: duckdb.DuckDBPyConnection, staged_run_id: str) -> None:
        assert staged_run_id == run_id
        assert connection.execute("SELECT status FROM player_projection_runs").fetchone() == (
            "validating",
        )
        raise RuntimeError("injected status transition failure")

    monkeypatch.setattr(repository, "projection_integrity_issues", pass_integrity)
    monkeypatch.setattr(repository, "_promote_projection_run", fail_promotion)

    with pytest.raises(RuntimeError, match="injected status transition failure"):
        repository.persist_projection_run(config, **attempted)

    after = _publication_snapshot(config)
    assert after == before
    assert after["player_projection_runs"][0][18] == "complete"


def test_persist_projection_run_commits_only_the_complete_status(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    config = _config(tmp_path)
    attempted = _publication_records(
        "phase4-run",
        "attempted",
        status="validating",
        with_dependents=False,
    )
    monkeypatch.setattr(repository, "projection_integrity_issues", lambda *_args, **_kwargs: ())

    repository.persist_projection_run(config, **attempted)

    warehouse = Warehouse(config.resolve(config.paths.warehouse))
    with warehouse.connect(read_only=True) as connection:
        status = connection.execute(
            "SELECT status FROM player_projection_runs WHERE run_id = 'phase4-run'"
        ).fetchone()
    assert status == ("complete",)


def test_post_commit_verification_failure_preserves_committed_result(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    config = _config(tmp_path)
    authoritative_report = (
        tmp_path / "models" / "reports" / "phase4-run" / "attempt-test" / "evaluation.md"
    )
    authoritative_report.parent.mkdir(parents=True)
    authoritative_report.write_text("authoritative\n", encoding="utf-8")
    registered_outputs = {
        "report_files": {
            "markdown_path": authoritative_report.relative_to(tmp_path).as_posix(),
        }
    }
    monkeypatch.setattr(
        training,
        "projection_integrity_issues",
        lambda *_args, **_kwargs: ("injected post-commit verification failure",),
    )

    result = training._committed_training_result(
        config,
        run_id="phase4-run",
        model_rows=24,
        prediction_rows=100,
        evaluated_rows=75,
        live_prediction_rows=25,
        champion_rows=12,
        board_rows=25,
        report={"status": "PASSED"},
        registered_outputs=registered_outputs,
        report_markdown_path=Path("docs/PHASE_4_MODEL_EVALUATION.md"),
        report_json_path=Path("docs/PHASE_4_MODEL_EVALUATION.json"),
    )

    assert result.committed
    assert not result.reused
    assert result.run_id == "phase4-run"
    assert result.model_rows == 24
    assert result.prediction_rows == 100
    assert result.evaluated_rows == 75
    assert result.live_prediction_rows == 25
    assert result.champion_rows == 12
    assert result.board_rows == 25
    assert result.report_path == authoritative_report.resolve()
    assert "injected post-commit verification failure" in result.issues[0]
    rendered = result.render()
    assert "Phase 4 player-model training: PASSED WITH WARNINGS" in rendered
    assert "Warehouse transaction: COMMITTED" in rendered
    assert "Run ID: phase4-run" in rendered


def test_publication_attempts_use_disjoint_authoritative_paths(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    tokens = iter(("a" * 32, "b" * 32))
    monkeypatch.setattr(training, "uuid4", lambda: SimpleNamespace(hex=next(tokens)))

    prior = training._new_publication_attempt("phase4-run")
    retry = training._new_publication_attempt("phase4-run")

    assert prior.run_id == retry.run_id == "phase4-run"
    assert prior.publication_id != retry.publication_id
    assert prior.artifact_directory != retry.artifact_directory
    assert prior.model_card_directory != retry.model_card_directory
    assert prior.plot_directory != retry.plot_directory
    assert prior.report_directory != retry.report_directory

    prior_files = {
        "artifact": tmp_path / "models" / "artifacts" / prior.artifact_directory / "model.joblib",
        "card": prior.model_card_directory / "model.md",
        "plot": prior.plot_directory / "diagnostic.svg",
        "report": prior.report_directory / "evaluation.json",
        "registry": prior.report_directory / "registry.json",
    }
    retry_files = {
        "artifact": tmp_path / "models" / "artifacts" / retry.artifact_directory / "model.joblib",
        "card": retry.model_card_directory / "model.md",
        "plot": retry.plot_directory / "diagnostic.svg",
        "report": retry.report_directory / "evaluation.json",
        "registry": retry.report_directory / "registry.json",
    }
    # Project-relative card/plot/report paths need the same root as real publication.
    for key in ("card", "plot", "report", "registry"):
        prior_files[key] = tmp_path / prior_files[key]
        retry_files[key] = tmp_path / retry_files[key]

    for path in prior_files.values():
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(b"prior-complete-publication")
    for path in retry_files.values():
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(b"failed-retry-staging")

    assert set(prior_files.values()).isdisjoint(retry_files.values())
    assert all(path.read_bytes() == b"prior-complete-publication" for path in prior_files.values())


def test_registry_exposes_champion_decision_statuses(tmp_path: Path) -> None:
    champion = {
        "position": "WR",
        "target_name": "fantasy_points_per_game",
        "selected_source": "baseline",
        "selected_name": "weighted_history",
        "selection_metric": "pooled_validation_mae",
        "selection_value": 2.5,
        "reference_baseline_name": "weighted_history",
        "reference_baseline_value": 2.5,
        "selection_payload": json.dumps(
            {
                "decision_status": "learned_improvement_inconclusive_baseline_retained",
                "learned_improvement_status": "inconclusive",
            }
        ),
    }

    metadata = training._write_model_registry(
        tmp_path,
        run_id="phase4-run",
        publication_id="attempt-registry-test",
        report_fingerprint="report",
        models=[],
        champions=[champion],
        output_path=Path("models/reports/phase4-run/registry.json"),
    )

    registry = json.loads((tmp_path / metadata["path"]).read_text(encoding="utf-8"))
    decision = registry["champions"][0]
    assert registry["publication_id"] == "attempt-registry-test"
    assert decision["decision_status"] == ("learned_improvement_inconclusive_baseline_retained")
    assert decision["learned_improvement_status"] == "inconclusive"
