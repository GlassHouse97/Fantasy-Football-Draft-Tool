"""Read-only discovery for Learning Center guides and notebooks."""

from __future__ import annotations

import json
import re
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Literal, cast

LearningResourceKind = Literal["guide", "notebook"]

_MAX_SUMMARY_LENGTH = 220
_HEADING_PATTERN = re.compile(r"^#{1,6}\s+(?P<title>.+?)\s*#*\s*$")
_QUESTION_PATTERN = re.compile(
    r"^\s*(?:[-*+]\s+)?(?:\*\*|__)?question(?:\*\*|__)?\s*:\s*"
    r"(?P<summary>.+?)\s*$",
    flags=re.IGNORECASE,
)
_MARKDOWN_LINK_PATTERN = re.compile(r"!?\[([^]]*)\]\([^)]*\)")
_INLINE_CODE_PATTERN = re.compile(r"`([^`]*)`")
_EMPHASIS_PATTERN = re.compile(r"[*_~]+")


@dataclass(frozen=True)
class LearningResource:
    """One locally discoverable Learning Center resource."""

    title: str
    summary: str
    relative_path: str
    kind: LearningResourceKind
    available: bool

    def as_dict(self) -> dict[str, object]:
        """Return a JSON-compatible representation for presentation layers."""

        return asdict(self)


@dataclass(frozen=True)
class LearningCenterCatalog:
    """Deterministic inventory of local learning material."""

    resources: tuple[LearningResource, ...]
    guides_directory_available: bool
    notebooks_directory_available: bool

    @property
    def available(self) -> bool:
        """Whether at least one resource can be previewed."""

        return any(resource.available for resource in self.resources)

    @property
    def guides(self) -> tuple[LearningResource, ...]:
        """Return guide records in catalog order."""

        return tuple(resource for resource in self.resources if resource.kind == "guide")

    @property
    def notebooks(self) -> tuple[LearningResource, ...]:
        """Return notebook records in catalog order."""

        return tuple(resource for resource in self.resources if resource.kind == "notebook")

    def as_dict(self) -> dict[str, object]:
        """Return a JSON-compatible representation for presentation layers."""

        return {
            "available": self.available,
            "guides_directory_available": self.guides_directory_available,
            "notebooks_directory_available": self.notebooks_directory_available,
            "resources": [resource.as_dict() for resource in self.resources],
        }


def load_learning_center(project_root: Path | str) -> LearningCenterCatalog:
    """Discover guides and notebooks below ``project_root`` without executing code.

    Markdown guides are read from ``docs/learning`` and notebooks are read from
    ``notebooks`` recursively. Missing directories produce an empty, unavailable
    section rather than an exception.
    """

    root = Path(project_root).resolve()
    guides_directory = root / "docs" / "learning"
    notebooks_directory = root / "notebooks"

    guides = _discover_resources(root, guides_directory, "*.md", "guide")
    notebooks = _discover_resources(root, notebooks_directory, "*.ipynb", "notebook")
    return LearningCenterCatalog(
        resources=guides + notebooks,
        guides_directory_available=guides_directory.is_dir(),
        notebooks_directory_available=notebooks_directory.is_dir(),
    )


def _discover_resources(
    root: Path,
    directory: Path,
    pattern: str,
    kind: LearningResourceKind,
) -> tuple[LearningResource, ...]:
    if not directory.is_dir():
        return ()

    paths = sorted(
        (path for path in directory.rglob(pattern) if path.is_file()),
        key=lambda path: path.relative_to(root).as_posix().casefold(),
    )
    return tuple(_load_resource(root, path, kind) for path in paths)


def _load_resource(
    root: Path,
    path: Path,
    kind: LearningResourceKind,
) -> LearningResource:
    relative_path = path.relative_to(root).as_posix()
    fallback_title = _title_from_filename(path)
    try:
        raw_text = path.read_text(encoding="utf-8")
        markdown = raw_text if kind == "guide" else _notebook_markdown(raw_text)
        title = _markdown_title(markdown) or fallback_title
        summary = _markdown_summary(markdown)
        if not summary:
            summary = "Open this resource for the full worked explanation."
        return LearningResource(
            title=title,
            summary=summary,
            relative_path=relative_path,
            kind=kind,
            available=True,
        )
    except (OSError, UnicodeError, ValueError, TypeError, json.JSONDecodeError):
        return LearningResource(
            title=fallback_title,
            summary="Preview unavailable because this local resource could not be read.",
            relative_path=relative_path,
            kind=kind,
            available=False,
        )


def _notebook_markdown(raw_text: str) -> str:
    payload = cast(object, json.loads(raw_text))
    if not isinstance(payload, dict):
        raise ValueError("Notebook root must be an object.")
    notebook = cast(dict[object, object], payload)
    raw_cells = notebook.get("cells")
    if not isinstance(raw_cells, list):
        raise ValueError("Notebook cells must be a list.")

    markdown_cells: list[str] = []
    for raw_cell in raw_cells:
        if not isinstance(raw_cell, dict):
            continue
        cell = cast(dict[object, object], raw_cell)
        if cell.get("cell_type") != "markdown":
            continue
        source = cell.get("source")
        if isinstance(source, str):
            markdown_cells.append(source)
        elif isinstance(source, list) and all(isinstance(line, str) for line in source):
            markdown_cells.append("".join(cast(list[str], source)))
        else:
            raise ValueError("Markdown cell source must contain text.")
    return "\n\n".join(markdown_cells)


def _markdown_title(markdown: str) -> str:
    for line in markdown.splitlines():
        match = _HEADING_PATTERN.match(line.strip())
        if match and line.lstrip().startswith("# "):
            return _clean_inline_markdown(match.group("title"))
    return ""


def _markdown_summary(markdown: str) -> str:
    lines = markdown.splitlines()
    for index, line in enumerate(lines):
        match = _QUESTION_PATTERN.match(line)
        if match:
            question_parts = [match.group("summary")]
            for continuation in lines[index + 1 :]:
                stripped = continuation.strip()
                if not stripped or _is_structural_markdown(stripped):
                    break
                question_parts.append(stripped)
            return _concise(_clean_inline_markdown(" ".join(question_parts)))

    paragraphs: list[list[str]] = []
    current: list[str] = []
    in_fence = False
    for raw_line in lines:
        line = raw_line.strip()
        if line.startswith("```"):
            in_fence = not in_fence
            continue
        if in_fence:
            continue
        if not line:
            if current:
                paragraphs.append(current)
                current = []
            continue
        if _is_structural_markdown(line):
            if current:
                paragraphs.append(current)
                current = []
            continue
        current.append(line)
    if current:
        paragraphs.append(current)

    for paragraph in paragraphs:
        summary = _clean_inline_markdown(" ".join(paragraph))
        if summary:
            return _concise(summary)
    return ""


def _is_structural_markdown(line: str) -> bool:
    return bool(
        _HEADING_PATTERN.match(line)
        or line.startswith((">", "- ", "* ", "+ ", "|", "![", "<"))
        or re.match(r"^\d+[.)]\s", line)
        or re.fullmatch(r"[-:| ]{3,}", line)
    )


def _clean_inline_markdown(value: str) -> str:
    cleaned = _MARKDOWN_LINK_PATTERN.sub(r"\1", value)
    cleaned = _INLINE_CODE_PATTERN.sub(r"\1", cleaned)
    cleaned = _EMPHASIS_PATTERN.sub("", cleaned)
    return " ".join(cleaned.split()).strip()


def _concise(value: str) -> str:
    if len(value) <= _MAX_SUMMARY_LENGTH:
        return value
    shortened = value[: _MAX_SUMMARY_LENGTH - 3].rsplit(" ", 1)[0].rstrip(" ,;:-")
    return f"{shortened}..."


def _title_from_filename(path: Path) -> str:
    words = re.sub(r"^\d+[_-]*", "", path.stem).replace("_", " ").replace("-", " ")
    return " ".join(words.split()).title() or "Untitled resource"
