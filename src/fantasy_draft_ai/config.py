"""Application configuration loaded from versioned YAML."""

from __future__ import annotations

import os
from pathlib import Path
from typing import Any

import yaml
from pydantic import BaseModel, ConfigDict, Field


class ProjectSection(BaseModel):
    """Stable project-level defaults."""

    model_config = ConfigDict(extra="forbid")

    name: str
    prediction_season: int = Field(ge=2000, le=2100)
    random_seed: int = 42


class PathSection(BaseModel):
    """Paths are relative to the project root unless absolute."""

    model_config = ConfigDict(extra="forbid")

    data_dir: Path
    raw_dir: Path
    processed_dir: Path
    warehouse: Path
    manifests: Path


class NetworkSection(BaseModel):
    """Shared behavior for documented HTTP sources."""

    model_config = ConfigDict(extra="forbid")

    timeout_seconds: float = Field(default=30, gt=0, le=300)
    user_agent: str


class TrainingSection(BaseModel):
    """Training boundaries that prevent accidental synthetic-data use."""

    model_config = ConfigDict(extra="forbid")

    start_season: int
    end_season: int
    include_synthetic: bool = False


class AppConfig(BaseModel):
    """Validated top-level configuration."""

    model_config = ConfigDict(extra="forbid")

    project: ProjectSection
    paths: PathSection
    network: NetworkSection
    training: TrainingSection
    project_root: Path = Field(exclude=True)

    def resolve(self, path: Path) -> Path:
        """Resolve a configured path against the project root."""

        return path if path.is_absolute() else self.project_root / path


def find_project_root(start: Path | None = None) -> Path:
    """Find the closest directory containing ``pyproject.toml``."""

    candidate = (start or Path.cwd()).resolve()
    for directory in (candidate, *candidate.parents):
        if (directory / "pyproject.toml").is_file():
            return directory
    raise FileNotFoundError("Could not find pyproject.toml; run this command inside the project.")


def load_config(path: Path | None = None) -> AppConfig:
    """Load and validate project YAML, honoring ``FANTASY_DRAFT_CONFIG``."""

    project_root = find_project_root()
    configured = path or Path(os.getenv("FANTASY_DRAFT_CONFIG", "configs/default.yaml"))
    config_path = configured if configured.is_absolute() else project_root / configured
    with config_path.open(encoding="utf-8") as handle:
        payload: dict[str, Any] = yaml.safe_load(handle) or {}
    payload["project_root"] = project_root
    return AppConfig.model_validate(payload)
