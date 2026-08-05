"""Truthful capability and local-data status reporting."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import duckdb

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

    identity_status = "not built; run fantasy-draft data review-identities"
    identity_available = False
    if warehouse.exists():
        try:
            with duckdb.connect(str(warehouse), read_only=True) as connection:
                counts = connection.execute(
                    "SELECT count(*) FILTER (WHERE status = 'pending' AND is_current), "
                    "count(*) FILTER (WHERE status = 'resolved' AND is_current) "
                    "FROM identity_review_queue"
                ).fetchone()
            if counts is not None:
                identity_status = f"{int(counts[0])} pending; {int(counts[1])} resolved"
                identity_available = True
        except duckdb.CatalogException:
            pass

    return [
        StatusItem(
            "Warehouse",
            str(warehouse) if warehouse.exists() else "not initialized",
            warehouse.exists(),
        ),
        StatusItem("nflverse raw data", latest_label(nfl_files), bool(nfl_files)),
        StatusItem("FFC ADP snapshot", latest_label(ffc_files), bool(ffc_files)),
        StatusItem("ESPN ADP", latest_label(espn_files), bool(espn_files)),
        StatusItem("Identity review queue", identity_status, identity_available),
        StatusItem("Scoring and rules engine", "available (configured logic)", True),
        StatusItem("Player projection model", "not trained", False),
        StatusItem("2026 projection board", "not built", False),
        StatusItem("ADP movement model", "insufficient dated snapshots", False),
        StatusItem("Historical league outcome model", "insufficient uploaded histories", False),
        StatusItem("Championship probabilities", "disabled", False),
        StatusItem("Draft recommendation score", "not implemented", False),
    ]
