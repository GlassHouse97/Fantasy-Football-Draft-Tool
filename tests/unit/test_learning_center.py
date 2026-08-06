from __future__ import annotations

import json
from pathlib import Path

from fantasy_draft_ai.services.learning_center import load_learning_center


def test_catalog_discovers_guides_and_notebooks_without_executing_code(tmp_path: Path) -> None:
    guide_directory = tmp_path / "docs" / "learning"
    notebook_directory = tmp_path / "notebooks" / "python"
    guide_directory.mkdir(parents=True)
    notebook_directory.mkdir(parents=True)
    (guide_directory / "02_projection_baselines.md").write_text(
        "# Projection Baselines\n\n## Why\n\n"
        "A transparent baseline gives a learned model an honest opponent.\n",
        encoding="utf-8",
    )
    (notebook_directory / "01_draft_math.ipynb").write_text(
        json.dumps(
            {
                "cells": [
                    {
                        "cell_type": "markdown",
                        "source": [
                            "# Draft Math Lab\n",
                            "\n",
                            "- **Question:** How does draft position change\n",
                            "  replacement value?\n",
                        ],
                    },
                    {
                        "cell_type": "code",
                        "source": ["raise RuntimeError('this cell must never run')\n"],
                    },
                ],
                "nbformat": 4,
            }
        ),
        encoding="utf-8",
    )

    catalog = load_learning_center(tmp_path)

    assert catalog.available is True
    assert catalog.guides_directory_available is True
    assert catalog.notebooks_directory_available is True
    assert [resource.kind for resource in catalog.resources] == ["guide", "notebook"]
    assert catalog.guides[0].title == "Projection Baselines"
    assert catalog.guides[0].summary == (
        "A transparent baseline gives a learned model an honest opponent."
    )
    assert catalog.guides[0].relative_path == "docs/learning/02_projection_baselines.md"
    assert catalog.notebooks[0].title == "Draft Math Lab"
    assert catalog.notebooks[0].summary == ("How does draft position change replacement value?")
    assert catalog.notebooks[0].relative_path == "notebooks/python/01_draft_math.ipynb"
    assert all(resource.available for resource in catalog.resources)


def test_catalog_order_is_deterministic_and_summaries_are_concise(tmp_path: Path) -> None:
    guide_directory = tmp_path / "docs" / "learning"
    guide_directory.mkdir(parents=True)
    long_summary = " ".join(["explanation"] * 40)
    (guide_directory / "z_last.md").write_text(
        f"# Last Guide\n\n{long_summary}\n",
        encoding="utf-8",
    )
    (guide_directory / "A_first.md").write_text(
        "No heading here, but this is still useful.\n",
        encoding="utf-8",
    )

    catalog = load_learning_center(str(tmp_path))

    assert [guide.relative_path for guide in catalog.guides] == [
        "docs/learning/A_first.md",
        "docs/learning/z_last.md",
    ]
    assert catalog.guides[0].title == "A First"
    assert len(catalog.guides[1].summary) <= 220
    assert catalog.guides[1].summary.endswith("...")
    assert catalog.as_dict()["available"] is True


def test_invalid_notebook_is_visible_but_marked_unavailable(tmp_path: Path) -> None:
    notebook_directory = tmp_path / "notebooks"
    notebook_directory.mkdir()
    (notebook_directory / "04_broken_notebook.ipynb").write_text("{broken", encoding="utf-8")

    catalog = load_learning_center(tmp_path)

    assert catalog.available is False
    assert catalog.notebooks_directory_available is True
    assert catalog.notebooks[0].title == "Broken Notebook"
    assert catalog.notebooks[0].available is False
    assert "Preview unavailable" in catalog.notebooks[0].summary


def test_missing_learning_directories_return_an_empty_catalog(tmp_path: Path) -> None:
    catalog = load_learning_center(tmp_path)

    assert catalog.resources == ()
    assert catalog.guides == ()
    assert catalog.notebooks == ()
    assert catalog.available is False
    assert catalog.guides_directory_available is False
    assert catalog.notebooks_directory_available is False
