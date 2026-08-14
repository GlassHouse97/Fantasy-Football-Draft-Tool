from __future__ import annotations

import tomllib
from pathlib import Path
from types import SimpleNamespace

from fantasy_draft_ai.ui.common import position_cell_style, position_option_label
from fantasy_draft_ai.ui.pages.draft_assistant import (
    _draft_board_frames,
    _style_draft_board,
)

PROJECT_ROOT = Path(__file__).resolve().parents[2]


def _relative_luminance(hex_color: str) -> float:
    channels = [
        int(hex_color[index : index + 2], 16) / 255
        for index in (1, 3, 5)
    ]
    linear = [
        channel / 12.92
        if channel <= 0.04045
        else ((channel + 0.055) / 1.055) ** 2.4
        for channel in channels
    ]
    return 0.2126 * linear[0] + 0.7152 * linear[1] + 0.0722 * linear[2]


def _contrast_ratio(first: str, second: str) -> float:
    first_luminance = _relative_luminance(first)
    second_luminance = _relative_luminance(second)
    lighter = max(first_luminance, second_luminance)
    darker = min(first_luminance, second_luminance)
    return (lighter + 0.05) / (darker + 0.05)


def test_draft_night_theme_has_accessible_contrast_and_explicit_fonts() -> None:
    config = tomllib.loads(
        (PROJECT_ROOT / ".streamlit" / "config.toml").read_text(encoding="utf-8")
    )
    theme = config["theme"]

    assert _contrast_ratio(theme["primaryColor"], "#FFFFFF") >= 4.5
    assert _contrast_ratio(theme["textColor"], theme["backgroundColor"]) >= 4.5
    assert _contrast_ratio(theme["borderColor"], theme["backgroundColor"]) >= 3.0
    assert (
        _contrast_ratio(theme["dataframeBorderColor"], theme["secondaryBackgroundColor"])
        >= 2.5
    )
    assert "Inter" in theme["font"]
    assert "Outfit" in theme["headingFont"]
    assert "family=Outfit" in theme["headingFont"]
    assert theme["showWidgetBorder"] is True


def test_position_visual_language_is_labeled_and_not_color_only() -> None:
    assert "RB" in position_option_label("rb")
    assert ":green[" in position_option_label("rb")
    assert "background-color" in position_cell_style("RB")
    assert "font-weight" in position_cell_style("RB")


def test_snake_board_groups_picks_by_round_and_marks_current_slot() -> None:
    picks = (
        SimpleNamespace(
            round=1,
            draft_slot=1,
            overall_pick=1,
            player_name="Runner One",
            position="RB",
        ),
        SimpleNamespace(
            round=1,
            draft_slot=2,
            overall_pick=2,
            player_name="Wideout Two",
            position="WR",
        ),
    )
    state = SimpleNamespace(
        user_draft_slot=2,
        rules=SimpleNamespace(teams=4, draft=SimpleNamespace(rounds=3)),
        picks=picks,
        current_overall_pick=3,
        current_draft_slot=3,
        is_user_turn=False,
    )
    session = SimpleNamespace(state=state)

    board, positions, user_column = _draft_board_frames(session)

    assert list(board.columns) == ["Round", "T1", "You · 2", "T3", "T4"]
    assert board.at[0, "T1"] == "01 · Runner One · RB"
    assert board.at[0, "You · 2"] == "02 · Wideout Two · WR"
    assert board.at[0, "T3"] == "ON THE CLOCK"
    assert positions.at[0, "T1"] == "RB"
    assert positions.at[0, "T3"] == "CURRENT"
    assert user_column == "You · 2"

    styled_html = _style_draft_board(board, positions, user_column).to_html()
    assert "#15803D" in styled_html
    assert "#1E3A8A" in styled_html
    assert "#713F12" in styled_html
    assert "box-shadow" not in styled_html
