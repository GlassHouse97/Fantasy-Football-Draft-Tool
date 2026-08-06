from __future__ import annotations

from pathlib import Path

import yaml
from typer.testing import CliRunner

from fantasy_draft_ai.cli import app
from fantasy_draft_ai.draft.pool import FrozenDraftPlayer
from fantasy_draft_ai.draft.repository import DraftRepository
from fantasy_draft_ai.recommendations.config import load_draft_engine_config
from fantasy_draft_ai.rules.models import DraftSettings, LeagueRules
from fantasy_draft_ai.scoring.engine import ScoringRules


def _configure_cli(tmp_path: Path, monkeypatch) -> Path:  # type: ignore[no-untyped-def]
    warehouse = tmp_path / "cli.duckdb"
    config_path = tmp_path / "config.yaml"
    config_path.write_text(
        yaml.safe_dump(
            {
                "project": {
                    "name": "test",
                    "prediction_season": 2026,
                    "random_seed": 42,
                },
                "paths": {
                    "data_dir": str(tmp_path),
                    "raw_dir": str(tmp_path / "raw"),
                    "processed_dir": str(tmp_path / "processed"),
                    "warehouse": str(warehouse),
                    "manifests": str(tmp_path / "manifests"),
                },
                "network": {"timeout_seconds": 30, "user_agent": "test"},
                "training": {"start_season": 2020, "end_season": 2025},
            }
        ),
        encoding="utf-8",
    )
    monkeypatch.setenv("FANTASY_DRAFT_CONFIG", str(config_path))
    return warehouse


def _seed_session(warehouse: Path) -> None:
    rules = LeagueRules(
        season=2026,
        teams=4,
        draft=DraftSettings(rounds=2),
        starters={"WR": 1},
        bench=1,
        scoring=ScoringRules(reception=1),
    )
    players = tuple(
        FrozenDraftPlayer(
            player_id=f"player-{index}",
            display_name=f"Player {index}",
            position="WR",
            p10=100 + index,
            p50=120 + index,
            p90=150 + index,
            prediction_status="validated",
            projection_source="learned",
            projection_method="fixture",
        )
        for index in range(8)
    )
    engine_config = load_draft_engine_config()
    DraftRepository(warehouse).create_session(
        session_name="CLI draft",
        rules=rules,
        user_draft_slot=1,
        projection_run_id="run-fixture",
        adp_build_fingerprint="adp-fixture",
        players=players,
        engine_config_fingerprint=engine_config.fingerprint(),
        recommendation_status="identity_mapping_required",
        recommendation_message="Canonical market identities are not mapped.",
        random_seed=42,
        simulation_count=engine_config.default_simulations,
        session_id="draft-cli",
    )


def test_draft_cli_pick_show_replace_undo_verify_and_blocked_recommendation(
    tmp_path: Path,
    monkeypatch,
) -> None:  # type: ignore[no-untyped-def]
    warehouse = _configure_cli(tmp_path, monkeypatch)
    _seed_session(warehouse)
    runner = CliRunner()

    listed = runner.invoke(app, ["draft", "list"])
    assert listed.exit_code == 0
    assert "draft-cli" in listed.stdout

    picked = runner.invoke(
        app,
        [
            "draft",
            "pick",
            "--session-id",
            "draft-cli",
            "--player-id",
            "player-0",
            "--expected-version",
            "0",
        ],
    )
    assert picked.exit_code == 0
    assert "version 1" in picked.stdout

    shown = runner.invoke(app, ["draft", "show", "--session-id", "draft-cli"])
    assert shown.exit_code == 0
    assert '"current_overall_pick": 2' in shown.stdout

    replaced = runner.invoke(
        app,
        [
            "draft",
            "replace",
            "--session-id",
            "draft-cli",
            "--overall-pick",
            "1",
            "--player-id",
            "player-1",
            "--expected-version",
            "1",
        ],
    )
    assert replaced.exit_code == 0
    assert "version 2" in replaced.stdout

    undone = runner.invoke(
        app,
        [
            "draft",
            "undo",
            "--session-id",
            "draft-cli",
            "--expected-version",
            "2",
        ],
    )
    assert undone.exit_code == 0
    assert "version 3" in undone.stdout

    verified = runner.invoke(app, ["draft", "verify", "--session-id", "draft-cli"])
    assert verified.exit_code == 0
    assert "PASSED" in verified.stdout

    recommendation = runner.invoke(
        app,
        ["draft", "recommend", "--session-id", "draft-cli"],
    )
    assert recommendation.exit_code == 2
    assert "identity_mapping_required" in recommendation.stdout
    assert '"championship_probability"' not in recommendation.stdout
