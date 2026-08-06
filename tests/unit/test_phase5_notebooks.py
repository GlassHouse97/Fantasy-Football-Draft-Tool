from __future__ import annotations

import json
from pathlib import Path
from typing import Any, cast

import pytest

PROJECT_ROOT = Path(__file__).resolve().parents[2]
NOTEBOOKS = (
    PROJECT_ROOT / "notebooks" / "python" / "07_adp_snapshots_and_movement.ipynb",
    PROJECT_ROOT / "notebooks" / "python" / "08_player_availability.ipynb",
)


@pytest.mark.parametrize("notebook_path", NOTEBOOKS, ids=lambda path: path.stem)
def test_phase5_notebook_code_cells_execute_in_order(notebook_path: Path) -> None:
    notebook = cast(dict[str, Any], json.loads(notebook_path.read_text(encoding="utf-8")))
    assert notebook["nbformat"] == 4
    cells = cast(list[dict[str, Any]], notebook["cells"])
    declarations = "".join(
        "".join(cast(list[str], cell["source"]))
        for cell in cells[:2]
        if cell["cell_type"] == "markdown"
    ).casefold()
    for label in ("question", "data", "unit", "target", "cutoff", "validation"):
        assert label in declarations

    namespace: dict[str, Any] = {"__name__": "__main__"}
    for index, cell in enumerate(cells):
        if cell["cell_type"] != "code":
            continue
        source = "".join(cast(list[str], cell["source"]))
        exec(compile(source, f"{notebook_path.name}:cell-{index}", "exec"), namespace)
