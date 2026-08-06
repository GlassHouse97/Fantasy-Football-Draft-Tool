from __future__ import annotations

from pathlib import Path

from fantasy_draft_ai.config import (
    AppConfig,
    NetworkSection,
    PathSection,
    ProjectSection,
    TrainingSection,
)
from fantasy_draft_ai.services.data_center import (
    load_data_center,
    run_safe_data_action,
    validate_data_action_request,
)


def _config(tmp_path: Path) -> AppConfig:
    return AppConfig(
        project=ProjectSection(name="test", prediction_season=2026, random_seed=42),
        paths=PathSection(
            data_dir=Path("data"),
            raw_dir=Path("data/raw"),
            processed_dir=Path("data/processed"),
            warehouse=Path("data/warehouse.duckdb"),
            manifests=Path("data/raw/manifests"),
        ),
        network=NetworkSection(timeout_seconds=30, user_agent="tests"),
        training=TrainingSection(start_season=2016, end_season=2025),
        project_root=tmp_path,
    )


def test_data_center_archives_valid_espn_file_immutably(tmp_path: Path) -> None:
    config = _config(tmp_path)
    source = Path(__file__).parents[1] / "fixtures" / "espn_adp_valid.csv"
    original = source.read_bytes()
    request = validate_data_action_request(config, "import_espn_csv", {"path": source})

    first = run_safe_data_action(config, request)
    second = run_safe_data_action(config, request)
    snapshot = load_data_center(config)

    assert first.succeeded and second.succeeded
    assert first.artifact_paths[0] != second.artifact_paths[0]
    assert Path(first.artifact_paths[0]).read_bytes() == original
    assert source.read_bytes() == original
    assert not snapshot.quality.passed
    assert snapshot.quality.failures == ("Canonical warehouse is not initialized.",)
    assert snapshot.quality.manifest_count == 2
    assert snapshot.quality.verified_files == 2
    espn = next(item for item in snapshot.sources if item.source == "espn")
    assert espn.fully_verified


def test_data_center_initialization_and_audit_round_trip(tmp_path: Path) -> None:
    config = _config(tmp_path)
    init_request = validate_data_action_request(config, "initialize_warehouse")
    init_result = run_safe_data_action(config, init_request)
    audit_request = validate_data_action_request(config, "audit")
    audit_result = run_safe_data_action(config, audit_request)
    snapshot = load_data_center(config)

    assert init_result.succeeded
    assert audit_result.succeeded
    assert audit_result.quality is not None
    assert audit_result.quality.passed
    assert snapshot.warehouse.exists
    assert snapshot.warehouse.readable
    assert snapshot.warehouse.table_count("players") == 0
