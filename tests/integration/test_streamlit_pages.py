"""Headless smoke coverage for every Phase 7 Streamlit area."""

from pathlib import Path

import pytest
from streamlit.testing.v1 import AppTest

PROJECT_ROOT = Path(__file__).resolve().parents[2]
PAGE_CASES = (
    ("fantasy_draft_ai.ui.pages.home", "Project Status"),
    ("fantasy_draft_ai.ui.pages.data_center", "Data Center"),
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
def test_phase7_page_has_no_headless_exception(module: str, expected_title: str) -> None:
    script = f"from {module} import render\nrender()\n"
    app = AppTest.from_string(script, default_timeout=60).run()

    assert len(app.exception) == 0
    assert expected_title in [title.value for title in app.title]
