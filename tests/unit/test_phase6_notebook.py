from __future__ import annotations

import json
from pathlib import Path
from typing import Any, cast


def test_phase6_simulation_notebook_is_explicit_and_executes_in_order() -> None:
    notebook_path = (
        Path(__file__).resolve().parents[2]
        / "notebooks"
        / "python"
        / "10_draft_simulation.ipynb"
    )
    notebook = cast(dict[str, Any], json.loads(notebook_path.read_text(encoding="utf-8")))
    assert notebook["nbformat"] == 4
    cells = cast(list[dict[str, Any]], notebook["cells"])
    notebook_text = "".join(
        "".join(cast(list[str], cell["source"]))
        for cell in cells
    ).casefold()
    for boundary in (
        "synthetic",
        "canonical",
        "display name",
        "246 ffc",
        "0 reviewed",
        "uncalibrated",
        "championship probability",
    ):
        assert boundary in notebook_text

    namespace: dict[str, Any] = {"__name__": "__main__"}
    for index, cell in enumerate(cells):
        if cell["cell_type"] != "code":
            continue
        source = "".join(cast(list[str], cell["source"]))
        exec(compile(source, f"{notebook_path.name}:cell-{index}", "exec"), namespace)
