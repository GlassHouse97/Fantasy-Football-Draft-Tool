"""Headless smoke coverage for every Streamlit workspace."""

from pathlib import Path

import pytest
from streamlit.testing.v1 import AppTest

PROJECT_ROOT = Path(__file__).resolve().parents[2]
PAGE_CASES = (
    ("fantasy_draft_ai.ui.pages.draft_assistant", "Draft Assistant"),
    ("fantasy_draft_ai.ui.pages.rankings", "Player rankings"),
    ("fantasy_draft_ai.ui.pages.help", "How to use the app"),
    ("fantasy_draft_ai.ui.pages.home", "Project Status"),
    ("fantasy_draft_ai.ui.pages.data_center", "Data Center"),
    ("fantasy_draft_ai.ui.pages.league_history", "League History"),
    ("fantasy_draft_ai.ui.pages.model_lab", "Model Lab"),
    ("fantasy_draft_ai.ui.pages.league_setup", "League Setup"),
    ("fantasy_draft_ai.ui.pages.draft_room", "Draft Room"),
    ("fantasy_draft_ai.ui.pages.post_draft", "Post-Draft Report"),
    ("fantasy_draft_ai.ui.pages.learning_center", "Learning Center"),
    ("fantasy_draft_ai.ui.pages.player_export", "Player Export List"),
    (
        "fantasy_draft_ai.ui.pages.player_market_consensus",
        "Player Market Consensus",
    ),
)


def test_multipage_entrypoint_loads_default_route() -> None:
    app = AppTest.from_file(str(PROJECT_ROOT / "app.py"), default_timeout=45).run()

    assert len(app.exception) == 0
    assert [title.value for title in app.title] == ["Draft Assistant"]


@pytest.mark.parametrize(("module", "expected_title"), PAGE_CASES)
def test_page_has_no_headless_exception(module: str, expected_title: str) -> None:
    script = f"from {module} import render\nrender()\n"
    app = AppTest.from_string(script, default_timeout=60).run()

    assert len(app.exception) == 0
    assert expected_title in [title.value for title in app.title]


def test_player_export_upload_imports_fantasypros_aggregate_without_mapping_steps() -> None:
    script = """
from types import SimpleNamespace
from unittest.mock import patch

from fantasy_draft_ai.ui.pages.player_export import _render_fantasypros_upload

result = SimpleNamespace(
    committed=True,
    reused_archive=False,
    source_summaries=tuple(
        SimpleNamespace(source=source, rows=rows, mapped=rows, unresolved=0)
        for source, rows in (
            ("yahoo", 2),
            ("sleeper", 2),
            ("rtsports", 2),
            ("fantasypros", 2),
        )
    ),
)

with patch(
    "fantasy_draft_ai.ui.pages.player_export.import_fantasypros_adp_upload",
    return_value=result,
):
    _render_fantasypros_upload(SimpleNamespace())
"""
    app = AppTest.from_string(script, default_timeout=60).run()
    app = app.file_uploader[0].set_value(
        (
            "FantasyPros.csv",
            b"Rank,Player (Bye),POS,Yahoo,Sleeper,RTSports,AVG,Real-Time\n"
            b"1,Jahmyr Gibbs   DET (6),RB1,1,1,1,1.0,1\n",
            "text/csv",
        )
    ).run()

    assert len(app.exception) == 0
    assert len(app.file_uploader) == 1
    assert len(app.selectbox) == 0
    assert len(app.checkbox) == 0
    assert any("loaded successfully" in success.value for success in app.success)


def test_player_export_upload_reports_duckdb_import_errors_without_stack_trace() -> None:
    script = """
from types import SimpleNamespace
from unittest.mock import patch

import duckdb

from fantasy_draft_ai.ui.pages.player_export import _render_fantasypros_upload

with patch(
    "fantasy_draft_ai.ui.pages.player_export.import_fantasypros_adp_upload",
    side_effect=duckdb.IOException("warehouse is locked"),
):
    _render_fantasypros_upload(SimpleNamespace())
"""
    app = AppTest.from_string(script, default_timeout=60).run()
    app = app.file_uploader[0].set_value(
        (
            "FantasyPros.csv",
            b"Rank,Player (Bye),POS,Yahoo,Sleeper,RTSports,AVG,Real-Time\n"
            b"1,Jahmyr Gibbs   DET (6),RB1,1,1,1,1.0,1\n",
            "text/csv",
        )
    ).run()

    assert len(app.exception) == 0
    assert any("was not loaded" in error.value for error in app.error)
    assert any("warehouse is locked" in caption.value for caption in app.caption)


def test_home_restore_defaults_previews_scoped_state_without_real_reset() -> None:
    script = """
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

import streamlit as st

from fantasy_draft_ai.services.local_state import LocalStateSummary
from fantasy_draft_ai.ui.pages.home import render

summary = LocalStateSummary(
    saved_league_setups=1,
    practice_drafts=1,
    recorded_picks=3,
    draft_events=4,
    frozen_player_rows=120,
    recommendation_runs=2,
)
config = SimpleNamespace(
    training=SimpleNamespace(start_season=2015, end_season=2025),
    project=SimpleNamespace(prediction_season=2026),
    paths=SimpleNamespace(warehouse=Path("ignored.duckdb")),
    resolve=lambda path: Path("ignored.duckdb"),
)
context = SimpleNamespace(
    config=config,
    reference_rules=object(),
    prepare_draft=lambda rules: SimpleNamespace(
        readiness=SimpleNamespace(
            unresolved_market_rows=0,
            recommendation_ready=True,
        )
    ),
    projection_board=SimpleNamespace(
        available=True,
        rows=(object(),),
        run=None,
        status=SimpleNamespace(message="Ready"),
    ),
    adp_market_board=SimpleNamespace(
        status=SimpleNamespace(observation_rows=120, snapshot_count=1)
    ),
    setup_repository=SimpleNamespace(list=lambda: (object(),)),
)
if not st.session_state.get("home_feedback_seeded"):
    st.session_state["app_reset_feedback"] = summary
    st.session_state["home_feedback_seeded"] = True

with (
    patch(
        "fantasy_draft_ai.ui.pages.home.load_app_context",
        return_value=context,
    ),
    patch("fantasy_draft_ai.ui.pages.home.project_status", return_value=()),
    patch(
        "fantasy_draft_ai.ui.pages.home.preview_local_state",
        return_value=summary,
    ),
    patch(
        "fantasy_draft_ai.ui.pages.home.restore_phase8_defaults",
        return_value=summary,
    ),
):
    render()
"""
    app = AppTest.from_string(script, default_timeout=60).run()

    assert len(app.exception) == 0
    assert any(expander.label == "Local testing controls" for expander in app.expander)
    assert any("1 saved league setup" in info.value for info in app.info)
    assert any("App defaults restored" in success.value for success in app.success)

    open_button = next(button for button in app.button if button.label == "Restore app defaults")
    app = open_button.click().run()

    assert len(app.exception) == 0
    assert any("Raw source archives" in markdown.value for markdown in app.markdown)
    confirm_button = next(
        button for button in app.button if button.label == "Restore app defaults now"
    )
    assert confirm_button.disabled is True


def test_home_restore_defaults_requires_exact_confirmation_and_uses_mocked_reset() -> None:
    script = """
from pathlib import Path
from unittest.mock import patch

from fantasy_draft_ai.services.local_state import LocalStateSummary
from fantasy_draft_ai.ui.pages.home import _confirm_restore_defaults

summary = LocalStateSummary(
    saved_league_setups=1,
    practice_drafts=1,
    recorded_picks=3,
    draft_events=4,
    frozen_player_rows=120,
    recommendation_runs=2,
)

with patch(
    "fantasy_draft_ai.ui.pages.home.restore_phase8_defaults",
    return_value=summary,
):
    _confirm_restore_defaults(Path("ignored.duckdb"), summary)
"""
    app = AppTest.from_string(script, default_timeout=60).run()

    confirmation = next(
        widget for widget in app.text_input if widget.label == "Type RESTORE DEFAULTS to continue"
    )
    app = confirmation.set_value("restore defaults").run()
    confirm_button = next(
        button for button in app.button if button.label == "Restore app defaults now"
    )
    assert confirm_button.disabled is True

    confirmation = next(
        widget for widget in app.text_input if widget.label == "Type RESTORE DEFAULTS to continue"
    )
    app = confirmation.set_value("RESTORE DEFAULTS").run()
    confirm_button = next(
        button for button in app.button if button.label == "Restore app defaults now"
    )
    assert confirm_button.disabled is False

    app = confirm_button.click().run()

    assert len(app.exception) == 0
    feedback = app.session_state["app_reset_feedback"]
    assert (
        feedback.saved_league_setups,
        feedback.practice_drafts,
        feedback.recorded_picks,
        feedback.draft_events,
        feedback.frozen_player_rows,
        feedback.recommendation_runs,
    ) == (
        1,
        1,
        3,
        4,
        120,
        2,
    )


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
