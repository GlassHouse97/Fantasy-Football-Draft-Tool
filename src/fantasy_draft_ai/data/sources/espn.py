"""Manual ESPN ADP upload validation and immutable archival."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import pandas as pd

from fantasy_draft_ai.config import AppConfig
from fantasy_draft_ai.data.manifests import RawArchive, SourceManifest
from fantasy_draft_ai.data.validation import validate_tabular_import
from fantasy_draft_ai.schemas.quality import QualityReport

ESPN_ADP_COLUMNS = [
    "captured_at",
    "season",
    "source",
    "scoring_format",
    "team_count",
    "player_name",
    "position",
    "nfl_team",
    "espn_player_id",
    "rank",
    "average_pick",
    "median_pick",
    "min_pick",
    "max_pick",
    "seven_day_change",
    "sample_size",
]


@dataclass(frozen=True)
class EspnImportResult:
    report: QualityReport
    raw_path: Path | None = None
    manifest: SourceManifest | None = None
    manifest_path: Path | None = None


def import_espn_adp(config: AppConfig, source_path: Path) -> EspnImportResult:
    """Validate a manual ESPN CSV and archive it only when fatal checks pass."""

    if not source_path.is_file():
        raise FileNotFoundError(source_path)
    try:
        frame = pd.read_csv(source_path, dtype={"espn_player_id": "string"})
    except Exception as exc:
        raise ValueError(f"Could not read ESPN ADP CSV: {exc}") from exc
    report = validate_tabular_import(
        frame,
        source="espn_manual",
        required_columns=ESPN_ADP_COLUMNS,
        required_values=[
            "captured_at",
            "season",
            "source",
            "scoring_format",
            "team_count",
            "player_name",
            "position",
            "rank",
            "average_pick",
        ],
        duplicate_key=["captured_at", "season", "scoring_format", "team_count", "rank"],
    )
    if report.has_fatal_errors:
        return EspnImportResult(report=report)

    season_values = pd.to_numeric(frame["season"], errors="coerce").dropna().astype(int).unique()
    seasons = sorted(int(value) for value in season_values)
    season_label = str(seasons[0]) if len(seasons) == 1 else "multi_season"
    content = source_path.read_bytes()
    archive = RawArchive(
        project_root=config.project_root,
        raw_root=config.resolve(config.paths.raw_dir),
        manifest_root=config.resolve(config.paths.manifests),
    )
    raw_path, acquired_at = archive.write_bytes(
        "espn_manual", f"espn_adp__manual__{season_label}", ".csv", content
    )
    manifest, manifest_path = archive.create_manifest(
        source="espn",
        acquisition_method="manual-csv-upload",
        acquired_at=acquired_at,
        raw_files=[raw_path],
        seasons=seasons,
        notes="Validated manual ADP upload; no ESPN scraping or authentication used.",
    )
    return EspnImportResult(report, raw_path, manifest, manifest_path)
