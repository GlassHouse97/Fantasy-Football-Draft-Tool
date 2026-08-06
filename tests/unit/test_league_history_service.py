from __future__ import annotations

from pathlib import Path

from fantasy_draft_ai.config import (
    AppConfig,
    NetworkSection,
    PathSection,
    ProjectSection,
    TrainingSection,
)
from fantasy_draft_ai.services.league_history import (
    LeagueHistoryCoverage,
    LeagueHistoryGateConfig,
    evaluate_league_history_gate,
    load_league_history_snapshot,
)


def _gate() -> LeagueHistoryGateConfig:
    return LeagueHistoryGateConfig(
        schema_version="league-history-gate-v1",
        minimum_league_seasons=100,
        minimum_team_seasons=1000,
        minimum_distinct_seasons=5,
        minimum_validation_league_seasons=20,
        minimum_test_league_seasons=20,
        minimum_positive_examples=100,
        minimum_negative_examples=100,
        minimum_complete_draft_rate=0.95,
        minimum_complete_outcome_rate=0.95,
        minimum_mapped_pick_rate=0.95,
        gradient_boosting_minimum_league_seasons=500,
        gradient_boosting_minimum_team_seasons=5000,
        gradient_boosting_minimum_class_examples=500,
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


def test_empty_history_keeps_every_outcome_model_locked() -> None:
    gate = evaluate_league_history_gate(LeagueHistoryCoverage(), _gate())

    assert gate.status == "locked_insufficient_data"
    assert not gate.points_percentile_ready
    assert not gate.playoff_ready
    assert not gate.championship_ready
    assert not gate.gradient_boosting_ready
    assert gate.blockers


def test_conservative_gate_requires_volume_completeness_and_class_balance() -> None:
    coverage = LeagueHistoryCoverage(
        packages=10,
        loaded_packages=10,
        league_seasons=100,
        distinct_seasons=5,
        rulesets=4,
        team_seasons=1200,
        draft_picks=16_000,
        resolved_draft_picks=15_500,
        complete_drafts=100,
        complete_outcomes=100,
        analysis_ready_leagues=100,
        feature_rows=1200,
        points_target_rows=1200,
        playoff_positive=400,
        playoff_negative=800,
        champion_positive=100,
        champion_negative=1100,
        validation_league_seasons=20,
        test_league_seasons=20,
    )

    gate = evaluate_league_history_gate(coverage, _gate())

    assert gate.status == "eligible_not_trained"
    assert gate.points_percentile_ready
    assert gate.playoff_ready
    assert gate.championship_ready
    assert not gate.gradient_boosting_ready
    assert not gate.blockers


def test_nonlinear_gate_cannot_bypass_common_or_target_evidence() -> None:
    coverage = LeagueHistoryCoverage(
        league_seasons=600,
        analysis_ready_leagues=600,
        distinct_seasons=5,
        team_seasons=6000,
        draft_picks=10_000,
        resolved_draft_picks=10_000,
        complete_drafts=600,
        complete_outcomes=600,
        feature_rows=0,
        points_target_rows=0,
        playoff_positive=600,
        playoff_negative=5400,
        champion_positive=600,
        champion_negative=5400,
        validation_league_seasons=20,
        test_league_seasons=20,
    )

    gate = evaluate_league_history_gate(coverage, _gate())

    assert not gate.points_percentile_ready
    assert not gate.playoff_ready
    assert not gate.championship_ready
    assert not gate.gradient_boosting_ready
    assert any(item.code == "roster_features" and not item.passed for item in gate.criteria)
    assert any(item.code == "points_targets" and not item.passed for item in gate.criteria)


def test_snapshot_without_warehouse_gives_a_specific_first_action(tmp_path: Path) -> None:
    gate_path = Path(__file__).parents[2] / "configs" / "league_history_gate.yaml"

    snapshot = load_league_history_snapshot(_config(tmp_path), gate_path=gate_path)

    assert not snapshot.available
    assert snapshot.issue == "Canonical warehouse is not initialized."
    assert "Initialize the warehouse" in snapshot.next_action
    assert snapshot.gate.status == "locked_insufficient_data"
