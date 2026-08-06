"""Headless smoke coverage for every Streamlit workspace."""

from pathlib import Path

import pytest
from streamlit.testing.v1 import AppTest

PROJECT_ROOT = Path(__file__).resolve().parents[2]
PAGE_CASES = (
    ("fantasy_draft_ai.ui.pages.home", "Project Status"),
    ("fantasy_draft_ai.ui.pages.data_center", "Data Center"),
    ("fantasy_draft_ai.ui.pages.league_history", "League History"),
    ("fantasy_draft_ai.ui.pages.model_lab", "Model Lab"),
    ("fantasy_draft_ai.ui.pages.league_setup", "League Setup"),
    ("fantasy_draft_ai.ui.pages.draft_room", "Draft Room"),
    ("fantasy_draft_ai.ui.pages.post_draft", "Post-Draft Report"),
    ("fantasy_draft_ai.ui.pages.learning_center", "Learning Center"),
)


def test_multipage_entrypoint_loads_default_route() -> None:
    app = AppTest.from_file(str(PROJECT_ROOT / "app.py"), default_timeout=45).run()

    assert len(app.exception) == 0
    assert [title.value for title in app.title] == ["Project Status"]


@pytest.mark.parametrize(("module", "expected_title"), PAGE_CASES)
def test_page_has_no_headless_exception(module: str, expected_title: str) -> None:
    script = f"from {module} import render\nrender()\n"
    app = AppTest.from_string(script, default_timeout=60).run()

    assert len(app.exception) == 0
    assert expected_title in [title.value for title in app.title]


def test_league_history_page_renders_descriptions_and_a_locked_gate() -> None:
    script = """
from datetime import UTC, datetime
from types import SimpleNamespace
from unittest.mock import patch

from fantasy_draft_ai.services.league_history import (
    GateCriterion,
    HistoryPackageSummary,
    HistoryTeamSummary,
    LeagueHistoryCoverage,
    LeagueHistorySnapshot,
    LeagueHistoryTrainingGate,
)
from fantasy_draft_ai.ui.pages.league_history import render

criterion = GateCriterion(
    code="league_seasons",
    label="Complete league-seasons",
    actual=1.0,
    required=100.0,
    passed=False,
    explanation="Complete league-seasons: 1/100.",
)
snapshot = LeagueHistorySnapshot(
    available=True,
    issue=None,
    packages=(HistoryPackageSummary(
        package_fingerprint="a" * 64,
        schema_version="league-history-v1",
        status="loaded",
        league_count=1,
        rules_rows=1,
        pick_rows=4,
        outcome_rows=4,
        unresolved_player_rows=1,
        imported_at=datetime(2026, 8, 6, tzinfo=UTC),
        quality_report={"passed": True, "warnings": ["One mapping requires review."]},
    ),),
    teams=(HistoryTeamSummary(
        league_season_id="league_alpha_2025",
        season=2025,
        team_id="team_01",
        wins=10.0,
        losses=4.0,
        points_for=1500.0,
        made_playoffs=True,
        final_place=2,
        is_champion=False,
        draft_metric_status="ready",
        drafted_only_points=1200.0,
        drafted_only_percentile=0.75,
        mapping_coverage=0.95,
        feature_payload={
            "starter_coverage": 1.0,
            "first_position_round": {"QB": 5, "RB": 1, "WR": 2, "TE": 7},
            "rb_wr_counts_through_round": {"3": {"RB": 2, "WR": 1}},
            "position_pick_counts": {"QB": 1, "RB": 5, "WR": 6, "TE": 2},
            "bench_depth": {"RB": 2, "WR": 3},
        },
    ),),
    coverage=LeagueHistoryCoverage(
        packages=1,
        loaded_packages=1,
        league_seasons=1,
        distinct_seasons=1,
        rulesets=1,
        team_seasons=4,
        draft_picks=4,
        resolved_draft_picks=3,
        complete_drafts=1,
        complete_outcomes=1,
        analysis_ready_leagues=1,
        feature_rows=4,
        draft_metric_rows=4,
    ),
    gate=LeagueHistoryTrainingGate(
        config_fingerprint="b" * 64,
        criteria=(criterion,),
        points_percentile_ready=False,
        playoff_ready=False,
        championship_ready=False,
        gradient_boosting_ready=False,
    ),
    next_action="Review 1 unresolved historical player identity.",
)

with (
    patch(
        "fantasy_draft_ai.ui.pages.league_history.load_app_context",
        return_value=SimpleNamespace(config=object()),
    ),
    patch(
        "fantasy_draft_ai.ui.pages.league_history.load_league_history_snapshot",
        return_value=snapshot,
    ),
):
    render()
"""
    app = AppTest.from_string(script, default_timeout=60).run()

    assert len(app.exception) == 0
    assert [title.value for title in app.title] == ["League History"]
    assert any("Training remains locked" in warning.value for warning in app.warning)
    assert any("Team" in frame.value.columns for frame in app.dataframe)
    assert any("Criterion" in frame.value.columns for frame in app.dataframe)
    assert all("train" not in button.label.casefold() for button in app.button)
