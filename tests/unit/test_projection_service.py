from __future__ import annotations

import hashlib
import json
from pathlib import Path

import duckdb
import pytest

from fantasy_draft_ai.config import (
    AppConfig,
    NetworkSection,
    PathSection,
    ProjectSection,
    TrainingSection,
)
from fantasy_draft_ai.data.audit import audit_project_data
from fantasy_draft_ai.data.warehouse import Warehouse
from fantasy_draft_ai.models.player_projection import train as training
from fantasy_draft_ai.models.player_projection.repository import projection_integrity_issues
from fantasy_draft_ai.services.projections import (
    TARGET_FANTASY_POINTS_PER_GAME,
    load_projection_board,
    projection_board_status,
)
from fantasy_draft_ai.services.status import project_status


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


def _insert_complete_board(config: AppConfig) -> None:
    warehouse = Warehouse(config.resolve(config.paths.warehouse))
    warehouse.initialize()
    artifact = config.project_root / "models" / "artifacts" / "test-model.joblib"
    card = config.project_root / "docs" / "model_cards" / "test-model.md"
    artifact.parent.mkdir(parents=True)
    card.parent.mkdir(parents=True)
    artifact.write_bytes(b"safe-test-artifact")
    card.write_text("# Test model card\n", encoding="utf-8")
    report_json = config.project_root / "docs" / "phase4.json"
    report_markdown = config.project_root / "docs" / "phase4.md"
    plot = config.project_root / "docs" / "images" / "phase4" / "test.svg"
    registry = config.project_root / "models" / "registry.json"
    plot.parent.mkdir(parents=True)
    report_json.write_text('{"status":"PASSED"}\n', encoding="utf-8")
    report_markdown.write_text("# Phase 4\n", encoding="utf-8")
    plot.write_text("<svg><!-- deterministic test plot --></svg>\n", encoding="utf-8")
    registry.write_text('{"active_run_id":"run-current"}\n', encoding="utf-8")
    run_payload = json.dumps(
        {
            "report_files": {
                "json_path": str(report_json.relative_to(config.project_root)),
                "json_sha256": _sha256(report_json),
                "markdown_path": str(report_markdown.relative_to(config.project_root)),
                "markdown_sha256": _sha256(report_markdown),
            },
            "registry": {
                "path": str(registry.relative_to(config.project_root)),
                "sha256": _sha256(registry),
            },
            "plot_files": {
                "test_plot": {
                    "path": str(plot.relative_to(config.project_root)),
                    "sha256": _sha256(plot),
                }
            },
        },
        sort_keys=True,
    )

    feature_fingerprint = "feature-current"
    target_fingerprint = "target-current"
    scoring_fingerprint = "rules-current"
    feature_version = "features-v1"
    build_payload = (
        '{"feature_data_fingerprint":"feature-current","feature_version":"features-v1",'
        '"scoring_ruleset_fingerprint":"rules-current",'
        '"target_data_fingerprint":"target-current"}'
    )
    build_fingerprint = hashlib.sha256(build_payload.encode()).hexdigest()
    baseline_fingerprint = "baseline-current"
    lineage = (
        feature_fingerprint,
        target_fingerprint,
        build_fingerprint,
        scoring_fingerprint,
        baseline_fingerprint,
        "model-features-current",
        "model-config-current",
    )

    with warehouse.connect() as connection:
        connection.execute(
            """
            INSERT INTO players (
                player_id, display_name, canonical_position, mapping_confidence, mapping_source
            ) VALUES ('player-1', 'Example Receiver', 'WR', 'high', 'test')
            """
        )
        connection.execute(
            """
            INSERT INTO player_season_features (
                player_id, feature_season, prediction_season, cutoff_date,
                feature_available_at, position, feature_payload, target_payload, source,
                feature_version, scoring_ruleset_fingerprint, source_dataset_ids,
                source_max_stat_season, source_max_as_of, data_fingerprint
            ) VALUES (
                'player-1', 2025, 2026, DATE '2026-03-01', DATE '2026-03-01', 'WR',
                '{"is_rookie":false}', NULL, 'nflverse', ?, ?, '[]', 2025,
                TIMESTAMPTZ '2026-03-01 00:00:00+00', ?
            )
            """,
            [feature_version, scoring_fingerprint, feature_fingerprint],
        )
        connection.execute(
            """
            INSERT INTO player_season_targets (
                player_id, prediction_season, position, target_payload, source,
                target_version, scoring_ruleset_fingerprint, source_dataset_ids,
                source_max_as_of, data_fingerprint, target_data_fingerprint
            ) VALUES (
                'player-1', 2026, 'WR', '{"fantasy_points_total":null}', 'nflverse',
                'targets-v1', ?, '[]', TIMESTAMPTZ '2026-03-01 00:00:00+00', ?, ?
            )
            """,
            [scoring_fingerprint, feature_fingerprint, target_fingerprint],
        )
        connection.execute(
            """
            INSERT INTO feature_build_metadata VALUES (
                ?, ?, ?, ?, ?, 2026, 2026, 1, 1, '[]',
                TIMESTAMPTZ '2026-03-01 00:00:00+00', '{"status":"PASSED"}'
            )
            """,
            [
                feature_fingerprint,
                target_fingerprint,
                build_fingerprint,
                feature_version,
                scoring_fingerprint,
            ],
        )
        connection.execute(
            """
            INSERT INTO baseline_predictions VALUES (
                'player-1', 2026, 'WR', 'fantasy_points_per_game', 'weighted_three_year',
                11.0, NULL, 'veteran', 'baseline-v1', ?, ?, ?, ?
            )
            """,
            [feature_fingerprint, target_fingerprint, build_fingerprint, scoring_fingerprint],
        )
        connection.execute(
            """
            INSERT INTO baseline_evaluation_metadata VALUES (
                ?, 'baseline-v1', ?, ?, ?, ?, 1, 0, '{"evaluated_rows":0}'
            )
            """,
            [
                baseline_fingerprint,
                feature_fingerprint,
                target_fingerprint,
                build_fingerprint,
                scoring_fingerprint,
            ],
        )
        connection.execute(
            """
            INSERT INTO player_projection_runs VALUES (
                'run-current', ?, ?, ?, ?, ?, ?, ?, '[2020,2021,2022,2023,2024,2025]',
                1, 1, 1, 2, 1, 1, 3, 1, 3, 'complete',
                TIMESTAMPTZ '2026-08-05 12:00:00+00', ?
            )
            """,
            [*lineage, run_payload],
        )
        connection.execute(
            """
            INSERT INTO player_projection_models VALUES (
                'model-1', 'run-current', 'ridge', 'fantasy_points_per_game', 'WR',
                '[2016,2017,2018,2019,2020,2021,2022,2023,2024,2025]', 1,
                '["lag1_ppg"]', '[]', '{"alpha":1.0}', 'oof_signed_residuals',
                ?, ?, ?, ?, ?, '{}'
            )
            """,
            [
                str(artifact.relative_to(config.project_root)),
                _sha256(artifact),
                artifact.stat().st_size,
                str(card.relative_to(config.project_root)),
                _sha256(card),
            ],
        )
        prediction_sql = """
            INSERT INTO player_projection_predictions VALUES (
                'run-current', 'player-1', ?, 'WR', 'fantasy_points_per_game', 'ridge',
                ?, ?, ?, 12.0, 9.0, 12.0, 15.0, ?, 16.0, 4, 'veteran',
                ?, ?, ?, ?, ?, ?, ?
            )
        """
        connection.execute(
            prediction_sql,
            [2025, "test", "test_2025", 2024, 10.0, *lineage],
        )
        connection.execute(
            prediction_sql,
            [2026, "live", None, 2025, None, *lineage],
        )
        for target_name, source, selected_name, model_id in (
            ("fantasy_points_per_game", "learned", "ridge", "model-1"),
            ("games_active", "baseline", "weighted_three_year", None),
            ("fantasy_points_total", "baseline", "weighted_three_year", None),
        ):
            connection.execute(
                """
                INSERT INTO player_projection_champions VALUES (
                    'run-current', ?, 'WR', ?, ?, ?, 'pooled_validation_mae',
                    1.0, 'weighted_three_year', 1.2, 0.2, '{"test_excluded":true}'
                )
                """,
                [target_name, source, selected_name, model_id],
            )
        connection.execute(
            """
            INSERT INTO player_projection_evaluation_metadata VALUES (
                'evaluation-current', 'run-current', ?, ?, ?, ?, ?, ?, ?,
                2, 1, 1, 3, 3, '{"status":"PASSED"}'
            )
            """,
            list(lineage),
        )
        connection.execute(
            """
            INSERT INTO player_projection_board VALUES (
                'run-current', 'player-1', 2026, 'WR',
                9.0, 12.0, 15.0, 'learned', 'ridge',
                15.0, 15.0, 15.0, 'baseline', 'weighted_three_year',
                180.0, 180.0, 180.0, 'baseline', 'weighted_three_year',
                'validated_champion_selection',
                '{"fantasy_points_per_game":{"top_factors":[{"feature":"lag1_ppg",'
                '"contribution":1.2}],"interpretation":"Associative, not causal."}}',
                ?, ?, ?, ?, ?, ?, ?, 'evaluation-current'
            )
            """,
            list(lineage),
        )


def test_projection_board_is_unavailable_without_a_warehouse(tmp_path: Path) -> None:
    config = _config(tmp_path)

    status = projection_board_status(config)
    board = load_projection_board(config)

    assert status.available is False
    assert status.code == "not_built"
    assert board.available is False
    assert board.rows == ()


def test_complete_projection_board_loads_names_lineage_and_flat_records(tmp_path: Path) -> None:
    config = _config(tmp_path)
    _insert_complete_board(config)

    board = load_projection_board(config)

    assert board.available is True
    assert board.status.row_count == 1
    assert board.status.learned_selection_rows == 1
    assert board.status.transparent_baseline_rows == 1
    assert board.run is not None
    assert board.run.run_id == "run-current"
    assert board.run.lineage.baseline_report_fingerprint == "baseline-current"
    assert len(board.selections) == 3
    assert board.rows[0].display_name == "Example Receiver"
    record = board.rows[0].as_record(TARGET_FANTASY_POINTS_PER_GAME)
    assert record["p10"] == 9.0
    assert record["p50"] == 12.0
    assert record["p90"] == 15.0
    assert record["selected_source"] == "learned"
    assert record["method_label"] == "Learned model"
    assert record["explanation"]["top_factors"][0]["feature"] == "lag1_ppg"
    frame = board.to_frame(TARGET_FANTASY_POINTS_PER_GAME)
    assert frame.loc[0, "display_name"] == "Example Receiver"
    assert json.dumps(board.as_dict())


def test_rookie_fallback_is_labeled_unvalidated_and_uncalibrated(tmp_path: Path) -> None:
    config = _config(tmp_path)
    _insert_complete_board(config)
    with duckdb.connect(str(config.resolve(config.paths.warehouse))) as connection:
        connection.execute(
            """
            UPDATE player_projection_board
            SET prediction_status = 'rookie_heuristic_fallback_unvalidated',
                fantasy_points_per_game_selected_source = 'heuristic'
            """
        )

    board = load_projection_board(config)

    assert board.available is True
    assert board.status.rookie_fallback_rows == 1
    interval = board.rows[0].target(TARGET_FANTASY_POINTS_PER_GAME)
    assert interval.method_label(board.rows[0].prediction_status) == (
        "Heuristic fallback (unvalidated / uncalibrated)"
    )


def test_stale_or_partial_phase4_never_becomes_available(tmp_path: Path) -> None:
    config = _config(tmp_path)
    _insert_complete_board(config)
    warehouse_path = config.resolve(config.paths.warehouse)
    with duckdb.connect(str(warehouse_path)) as connection:
        connection.execute("UPDATE player_projection_runs SET build_fingerprint = 'stale-build'")
    stale = projection_board_status(config)
    assert stale.available is False
    assert stale.code == "stale"

    with duckdb.connect(str(warehouse_path)) as connection:
        connection.execute(
            "UPDATE player_projection_runs SET build_fingerprint = "
            "(SELECT build_fingerprint FROM feature_build_metadata)"
        )
        connection.execute(
            "DELETE FROM player_projection_champions WHERE target_name = 'games_active'"
        )
    partial = projection_board_status(config)
    assert partial.available is False
    assert partial.code == "partial"


def test_project_status_requires_the_complete_phase4_contract(tmp_path: Path) -> None:
    config = _config(tmp_path)
    _insert_complete_board(config)

    items = {item.name: item for item in project_status(config)}

    assert items["Player projection model"].available is True
    assert "active Phase 3 lineage verified" in items["Player projection model"].status
    assert items["Learned 2026 projection board"].available is True
    assert "validated 2026 board rows" in items["Learned 2026 projection board"].status

    with duckdb.connect(str(config.resolve(config.paths.warehouse))) as connection:
        connection.execute("UPDATE player_projection_runs SET prediction_rows = 99")
    items = {item.name: item for item in project_status(config)}
    assert items["Player projection model"].available is False
    assert items["Learned 2026 projection board"].available is False


@pytest.mark.parametrize(
    "relative_path",
    (Path("docs/phase4.md"), Path("docs/images/phase4/test.svg")),
)
def test_registered_output_tampering_hides_the_board(tmp_path: Path, relative_path: Path) -> None:
    config = _config(tmp_path)
    _insert_complete_board(config)
    (config.project_root / relative_path).write_text("tampered\n", encoding="utf-8")

    status = projection_board_status(config)

    assert status.available is False
    assert status.code == "partial"


def test_prediction_center_mismatch_fails_repository_and_service_integrity(
    tmp_path: Path,
) -> None:
    config = _config(tmp_path)
    _insert_complete_board(config)
    with duckdb.connect(str(config.resolve(config.paths.warehouse))) as connection:
        connection.execute(
            """
            UPDATE player_projection_predictions
            SET predicted_value = p50 + 0.25
            WHERE prediction_scope = 'live'
            """
        )

    issues = projection_integrity_issues(config)
    status = projection_board_status(config)

    assert any("predictions contain invalid" in issue for issue in issues)
    assert status.available is False
    assert status.code == "partial"


def test_baseline_interval_mismatch_fails_repository_and_service_integrity(
    tmp_path: Path,
) -> None:
    config = _config(tmp_path)
    _insert_complete_board(config)
    with duckdb.connect(str(config.resolve(config.paths.warehouse))) as connection:
        connection.execute(
            """
            UPDATE player_projection_board
            SET games_active_p10 = games_active_p50 - 1.0
            WHERE games_active_selected_source = 'baseline'
            """
        )

    issues = projection_integrity_issues(config)
    status = projection_board_status(config)

    assert any("baseline board selections" in issue for issue in issues)
    assert status.available is False
    assert status.code == "partial"


def _assert_all_phase4_authorities_reject(
    config: AppConfig,
    *,
    issue_fragment: str,
) -> None:
    issues = projection_integrity_issues(config)
    status = projection_board_status(config)
    audit = audit_project_data(config)
    reused = training._reuse_current_run(
        config,
        "run-current",
        Path("docs/requested.md"),
        Path("docs/requested.json"),
    )

    assert any(issue_fragment in issue for issue in issues)
    assert any(issue_fragment in issue for issue in audit.failures)
    assert status.available is False
    assert status.code == "partial"
    assert reused is None


@pytest.mark.parametrize(
    "mutation",
    (
        "SET fantasy_points_per_game_p10 = CAST('NaN' AS DOUBLE)",
        "SET fantasy_points_per_game_p10 = fantasy_points_per_game_p50 + 1.0",
        "SET games_active_p90 = 19.0",
        "SET fantasy_points_total_p90 = fantasy_points_total_p50 - 1.0",
        "SET player_id = 'missing-board-player'",
        "SET prediction_status = ''",
        "SET fantasy_points_total_selected_name = ''",
        "SET explanation_payload = '[]'::JSON",
    ),
)
def test_invalid_board_contract_is_rejected_by_every_phase4_authority(
    tmp_path: Path,
    mutation: str,
) -> None:
    config = _config(tmp_path)
    _insert_complete_board(config)
    with duckdb.connect(str(config.resolve(config.paths.warehouse))) as connection:
        connection.execute(f"UPDATE player_projection_board {mutation}")

    _assert_all_phase4_authorities_reject(
        config,
        issue_fragment="projection board contains invalid",
    )


def test_orphan_candidate_prediction_is_rejected_by_every_phase4_authority(
    tmp_path: Path,
) -> None:
    config = _config(tmp_path)
    _insert_complete_board(config)
    with duckdb.connect(str(config.resolve(config.paths.warehouse))) as connection:
        connection.execute(
            "UPDATE player_projection_predictions SET player_id = 'missing-prediction-player'"
        )

    _assert_all_phase4_authorities_reject(
        config,
        issue_fragment="predictions contain orphan player IDs",
    )
