from __future__ import annotations

from pathlib import Path

from streamlit.testing.v1 import AppTest

from fantasy_draft_ai.draft.repository import DraftRepository
from fantasy_draft_ai.services.draft_room import record_draft_pick


def test_quick_start_recommend_pick_and_undo_with_unmapped_market(tmp_path: Path) -> None:
    warehouse = tmp_path / "draft-assistant.duckdb"
    script = f'''
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

from fantasy_draft_ai.draft.repository import DraftRepository
from fantasy_draft_ai.recommendations.config import (
    load_draft_engine_config,
    load_projection_guidance_config,
)
from fantasy_draft_ai.rules.models import DraftSettings, FlexSlot, LeagueRules
from fantasy_draft_ai.scoring.engine import ScoringRules
from fantasy_draft_ai.services.adp_market import AdpMarketBoard, AdpMarketStatus
from fantasy_draft_ai.services.league_setup import LeagueSetupRepository
from fantasy_draft_ai.services.projections import (
    TARGET_FANTASY_POINTS_TOTAL,
    PlayerProjection,
    ProjectionBoard,
    ProjectionBoardStatus,
    ProjectionInterval,
    ProjectionLineage,
    ProjectionRun,
)
from fantasy_draft_ai.ui.context import AppContext
from fantasy_draft_ai.ui.pages.draft_assistant import render

warehouse = Path(r"{warehouse}")
rules = LeagueRules(
    season=2026,
    teams=12,
    draft=DraftSettings(rounds=16),
    starters={{"QB": 1, "RB": 2, "WR": 3, "TE": 1}},
    flex_slots=(FlexSlot(name="FLEX", count=2, eligible=("RB", "WR", "TE")),),
    bench=7,
    scoring=ScoringRules(reception=1),
)
lineage = ProjectionLineage(
    feature_data_fingerprint="feature",
    target_data_fingerprint="target",
    build_fingerprint="build",
    scoring_ruleset_fingerprint=rules.fingerprint(),
    baseline_report_fingerprint="baseline",
    model_feature_fingerprint="model-feature",
    model_config_fingerprint="model-config",
)
players = []
for position, base in (("QB", 330), ("RB", 300), ("WR", 295), ("TE", 230)):
    for index in range(1, 41):
        p50 = float(base - index * 3)
        players.append(
            PlayerProjection(
                run_id="projection-run",
                player_id=f"{{position}}-{{index:02d}}",
                display_name=f"{{position}} Player {{index:02d}}",
                prediction_season=2026,
                position=position,
                prediction_status=(
                    "rookie_heuristic_fallback_unvalidated"
                    if position == "WR" and index == 1
                    else "mixed_learned_and_heuristic_validated"
                    if position == "QB" and index == 1
                    else "learned_models_validated"
                ),
                targets={{
                    TARGET_FANTASY_POINTS_TOTAL: ProjectionInterval(
                        p10=p50 - 20,
                        p50=p50,
                        p90=p50 + 20,
                        selected_source="learned",
                        selected_name="test-model",
                    )
                }},
                explanation={{}},
            )
        )
run = ProjectionRun(
    run_id="projection-run",
    status="published",
    trained_at="2026-08-01T00:00:00Z",
    prediction_season=2026,
    lineage=lineage,
    split_seasons={{}},
    feature_rows=160,
    target_rows=160,
    training_rows=160,
    prediction_rows=160,
    evaluated_rows=160,
    live_prediction_rows=160,
    candidate_rows=160,
    model_rows=4,
    champion_rows=4,
)
board = ProjectionBoard(
    status=ProjectionBoardStatus(
        available=True,
        code="available",
        message="available",
        run=run,
        row_count=len(players),
    ),
    rows=tuple(players),
)
market = AdpMarketBoard(
    status=AdpMarketStatus(
        available=False,
        code="not_built",
        message="No reviewed ADP mapping is available.",
    )
)
context = AppContext(
    config=SimpleNamespace(project=SimpleNamespace(random_seed=42)),
    projection_board=board,
    adp_market_board=market,
    reference_rules=rules,
    engine_config=load_draft_engine_config(),
    guidance_config=load_projection_guidance_config(),
    draft_repository=DraftRepository(warehouse),
    setup_repository=LeagueSetupRepository(warehouse),
)
with patch(
    "fantasy_draft_ai.ui.pages.draft_assistant.load_app_context",
    return_value=context,
):
    render()
'''
    app = AppTest.from_string(script, default_timeout=60).run()

    assert len(app.exception) == 0
    assert [title.value for title in app.title] == ["Draft Assistant"]
    assert any(button.label == "Start draft" for button in app.button)
    roster_preset = next(widget for widget in app.selectbox if widget.label == "Roster preset")
    assert roster_preset.value == "standard"

    app = next(button for button in app.button if button.label == "Start draft").click().run()

    assert len(app.exception) == 0
    assert any("Best pick now" in markdown.value for markdown in app.markdown)
    assert any(
        "Lower-confidence rookie estimate" in markdown.value for markdown in app.markdown
    )
    fallback_warning = next(
        warning.value for warning in app.warning if "point-only fallback" in warning.value
    )
    assert fallback_warning.startswith("1 rookie projection uses")
    assert "P10, P50, and P90 are identical" in fallback_warning
    best_pick_button = next(
        button
        for button in app.button
        if button.label.startswith("Draft ")
    )
    drafted_name = best_pick_button.label.removeprefix("Draft ")
    app = best_pick_button.click().run()

    repository = DraftRepository(warehouse)
    session_id = repository.list_sessions()[0].session_id
    after_pick = repository.verify_session(session_id)
    assert len(after_pick.picks) == 1
    assert after_pick.rules.starters["WR"] == 2
    assert after_pick.rules.flex_slots[0].count == 1
    assert after_pick.rules.draft.rounds == 14
    assert after_pick.picks[0].player_name == drafted_name
    assert repository.session_info(session_id).recommendation_status != "recommendation_ready"
    assert len(app.exception) == 0
    assert any("Opponent pick" in markdown.value for markdown in app.markdown)
    assert any(header.value.endswith("Available players") for header in app.header)

    app = next(button for button in app.button if button.label == "Undo last pick").click().run()

    assert len(app.exception) == 0
    assert repository.verify_session(session_id).picks == ()
    assert any("Best pick now" in markdown.value for markdown in app.markdown)

    best_pick_button = next(
        button for button in app.button if button.label.startswith("Draft ")
    )
    app = best_pick_button.click().run()
    state = repository.verify_session(session_id)
    assert len(state.picks) == 1
    assert state.current_overall_pick == 2

    callback_script = f'''
from pathlib import Path
from types import SimpleNamespace

import streamlit as st

from fantasy_draft_ai.draft.repository import DraftRepository
from fantasy_draft_ai.ui.pages.draft_assistant import _record_table_pick

repository = DraftRepository(Path(r"{warehouse}"))
state = repository.verify_session("{session_id}")
available = tuple(
    player
    for player in repository.load_players("{session_id}")
    if player.player_id not in state.selected_player_ids
)
click_key = f"assistant_table_click_{{state.session_id}}_{{state.version}}"
search_key = f"assistant_search_{{state.session_id}}"
st.session_state[click_key] = {{"row": 0, "label": "Record taken"}}
st.session_state[search_key] = "stale player search"
_record_table_pick(
    SimpleNamespace(draft_repository=repository),
    state.session_id,
    state.version,
    available[:1],
    click_key,
    search_key,
)
st.write(st.session_state[search_key])
'''
    callback_app = AppTest.from_string(callback_script, default_timeout=60).run()

    assert len(callback_app.exception) == 0
    assert callback_app.session_state[f"assistant_search_{session_id}"] == ""
    assert callback_app.session_state["assistant_feedback"][0] == "success"
    state = repository.verify_session(session_id)
    assert len(state.picks) == 2
    assert state.current_overall_pick == 3

    app = app.run()
    assert any("Pick 3 · Team 3" in markdown.value for markdown in app.markdown)
    while not (state := repository.verify_session(session_id)).is_user_turn:
        next_player = next(
            player
            for player in repository.load_players(session_id)
            if player.player_id not in state.selected_player_ids
        )
        record_draft_pick(
            repository,
            session_id,
            next_player.player_id,
            expected_version=state.version,
            command_id=f"integration-opponent-{state.version}",
        )

    assert state.current_overall_pick == 24
    app = app.run()
    assert any("Best pick now" in markdown.value for markdown in app.markdown)

    for expected_pick in (24, 25):
        pick_button = next(
            button for button in app.button if button.label.startswith("Draft ")
        )
        app = pick_button.click().run()
        assert repository.verify_session(session_id).picks[-1].overall_pick == expected_pick

    resumed = AppTest.from_string(script, default_timeout=60).run()
    assert len(resumed.exception) == 0
    assert any("Pick 26 · Team 2" in markdown.value for markdown in resumed.markdown)
    assert repository.verify_session(session_id).current_overall_pick == 26


def test_completed_session_hides_available_player_actions() -> None:
    script = '''
from types import SimpleNamespace

from fantasy_draft_ai.ui.pages.draft_assistant import _render_available_players

session = SimpleNamespace(state=SimpleNamespace(complete=True))
_render_available_players(SimpleNamespace(), session)
'''
    app = AppTest.from_string(script, default_timeout=30).run()

    assert len(app.exception) == 0
    assert any("no additional player" in caption.value for caption in app.caption)
    assert len(app.dataframe) == 0


def test_rankings_can_show_the_complete_projection_board() -> None:
    script = '''
from types import SimpleNamespace
from unittest.mock import patch

from fantasy_draft_ai.draft.pool import FrozenDraftPlayer
from fantasy_draft_ai.rules.models import DraftSettings, FlexSlot, LeagueRules
from fantasy_draft_ai.scoring.engine import ScoringRules
from fantasy_draft_ai.ui.pages.rankings import render

rules = LeagueRules(
    season=2026,
    teams=12,
    draft=DraftSettings(rounds=16),
    starters={"QB": 1, "RB": 2, "WR": 3, "TE": 1},
    flex_slots=(FlexSlot(name="FLEX", count=2, eligible=("RB", "WR", "TE")),),
    bench=7,
    scoring=ScoringRules(reception=1),
)
players = tuple(
    FrozenDraftPlayer(
        player_id=f"{position}-{index:03d}",
        display_name=f"{position} Player {index:03d}",
        position=position,
        p10=float(base - index - 20),
        p50=float(base - index),
        p90=float(base - index + 20),
        prediction_status=(
            "rookie_heuristic_fallback_unvalidated"
            if position == "WR" and index == 1
            else "mixed_learned_and_heuristic_validated"
            if position == "QB" and index == 1
            else "learned_models_validated"
        ),
        projection_source="test",
        projection_method="integration-test",
    )
    for position, base in (("QB", 400), ("RB", 350), ("WR", 340), ("TE", 300))
    for index in range(1, 81)
)
context = SimpleNamespace(
    reference_rules=rules,
    prepare_draft=lambda selected_rules: SimpleNamespace(
        readiness=SimpleNamespace(state_ready=True, state_message="Ready"),
        players=players,
    ),
)
with patch("fantasy_draft_ai.ui.pages.rankings.load_app_context", return_value=context):
    render()
'''
    app = AppTest.from_string(script, default_timeout=60).run()

    assert len(app.exception) == 0
    show = next(widget for widget in app.selectbox if widget.label == "Board size")
    assert "All players" in show.options
    app = show.set_value("All players").run()

    assert len(app.exception) == 0
    rankings_frame = next(
        frame for frame in app.dataframe if "Player" in frame.value.columns
    )
    assert len(rankings_frame.value) == 320
    assert "ADP" not in rankings_frame.value.columns
    assert any("ADP is hidden" in caption.value for caption in app.caption)
    fallback_warning = next(
        warning.value for warning in app.warning if "point-only fallback" in warning.value
    )
    assert fallback_warning.startswith("1 rookie projection uses")
    assert "P10, P50, and P90 are identical" in fallback_warning
