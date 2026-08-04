"""Truthful capability and local-data status reporting."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from fantasy_draft_ai.config import AppConfig


@dataclass(frozen=True)
class StatusItem:
    name: str
    status: str
    available: bool


def project_status(config: AppConfig) -> list[StatusItem]:
    raw_root = config.resolve(config.paths.raw_dir)
    ffc_files = sorted((raw_root / "ffc_adp").glob("*.json"))
    espn_files = sorted((raw_root / "espn_manual").glob("*.csv"))
    nfl_files = sorted((raw_root / "nflverse").glob("*.parquet"))
    warehouse = config.resolve(config.paths.warehouse)

    def latest_label(files: list[Path]) -> str:
        return files[-1].name if files else "not available"

    return [
        StatusItem(
            "Warehouse",
            str(warehouse) if warehouse.exists() else "not initialized",
            warehouse.exists(),
        ),
        StatusItem("nflverse raw data", latest_label(nfl_files), bool(nfl_files)),
        StatusItem("FFC ADP snapshot", latest_label(ffc_files), bool(ffc_files)),
        StatusItem("ESPN ADP", latest_label(espn_files), bool(espn_files)),
        StatusItem("Scoring and rules engine", "available (configured logic)", True),
        StatusItem("Player projection model", "not trained", False),
        StatusItem("2026 projection board", "not built", False),
        StatusItem("ADP movement model", "insufficient dated snapshots", False),
        StatusItem("Historical league outcome model", "insufficient uploaded histories", False),
        StatusItem("Championship probabilities", "disabled", False),
        StatusItem("Draft recommendation score", "not implemented", False),
    ]
