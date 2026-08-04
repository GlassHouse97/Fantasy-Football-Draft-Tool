"""Fantasy Football Calculator ADP snapshots."""

from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import httpx
import pandas as pd

from fantasy_draft_ai.config import AppConfig
from fantasy_draft_ai.data.manifests import RawArchive, SourceManifest

FFC_API_ROOT = "https://fantasyfootballcalculator.com/api/v1/adp"
SUPPORTED_FORMATS = {"standard", "half-ppr", "ppr", "2-qb", "dynasty", "rookie"}


@dataclass(frozen=True)
class SnapshotResult:
    raw_path: Path
    manifest: SourceManifest
    manifest_path: Path
    normalized: pd.DataFrame
    reused_offline: bool = False


def _archive(config: AppConfig) -> RawArchive:
    return RawArchive(
        project_root=config.project_root,
        raw_root=config.resolve(config.paths.raw_dir),
        manifest_root=config.resolve(config.paths.manifests),
    )


def normalize_ffc_payload(
    payload: dict[str, Any], *, season: int, scoring_format: str, teams: int
) -> pd.DataFrame:
    """Normalize the documented FFC ``players`` response without name-only IDs."""

    players = payload.get("players", [])
    if not isinstance(players, list):
        raise ValueError("FFC response did not contain a players list.")
    rows: list[dict[str, Any]] = []
    for index, player in enumerate(players):
        if not isinstance(player, dict):
            continue
        rows.append(
            {
                "source": "ffc",
                "season": season,
                "scoring_format": scoring_format,
                "team_count": teams,
                "player_id": None,
                "player_name": player.get("name") or player.get("player_name"),
                "position": player.get("position"),
                "nfl_team": player.get("team"),
                "average_pick": player.get("adp"),
                "median_pick": player.get("median"),
                "rank": player.get("overall_rank") or player.get("rank") or index + 1,
                "min_pick": player.get("high"),
                "max_pick": player.get("low"),
                "sample_size": player.get("times_drafted") or player.get("drafts"),
                "movement": player.get("change"),
                "raw_source_row_id": str(player.get("player_id") or index),
                "mapping_confidence": "unresolved",
            }
        )
    return pd.DataFrame(rows)


def snapshot_ffc_adp(
    config: AppConfig,
    *,
    season: int,
    scoring_format: str,
    teams: int,
    position: str | None = None,
    offline: bool = False,
) -> SnapshotResult:
    """Download and archive a never-overwritten FFC ADP snapshot."""

    if scoring_format not in SUPPORTED_FORMATS:
        raise ValueError(
            f"Unsupported format {scoring_format!r}; choose {sorted(SUPPORTED_FORMATS)}"
        )
    if not 4 <= teams <= 32:
        raise ValueError("Team count must be between 4 and 32.")
    position_label = position.lower() if position else "overall"
    stem = f"ffc_adp__{scoring_format}__{teams}_team__{season}__{position_label}"
    directory = config.resolve(config.paths.raw_dir) / "ffc_adp"

    if offline:
        matches = sorted(directory.glob(f"{stem}__*.json"))
        if not matches:
            raise FileNotFoundError(f"No cached FFC snapshot matches {stem}.")
        raw_path = matches[-1]
        payload = json.loads(raw_path.read_text(encoding="utf-8"))
        archive = _archive(config)
        existing = archive.find_manifest_for_files([raw_path])
        if existing is None:
            manifest, manifest_path = archive.create_manifest(
                source="ffc",
                acquisition_method="offline-cache",
                acquired_at=datetime.fromtimestamp(raw_path.stat().st_mtime, tz=UTC),
                raw_files=[raw_path],
                seasons=[season],
                notes="Reused existing immutable snapshot; no network request made.",
            )
        else:
            manifest, manifest_path = existing
        return SnapshotResult(
            raw_path,
            manifest,
            manifest_path,
            normalize_ffc_payload(
                payload, season=season, scoring_format=scoring_format, teams=teams
            ),
            True,
        )

    params: dict[str, str | int] = {"teams": teams, "year": season}
    if position:
        params["position"] = position.upper()
    headers = {"User-Agent": config.network.user_agent, "Accept": "application/json"}
    try:
        response = httpx.get(
            f"{FFC_API_ROOT}/{scoring_format}",
            params=params,
            headers=headers,
            timeout=config.network.timeout_seconds,
            follow_redirects=True,
        )
        response.raise_for_status()
    except httpx.HTTPError as exc:
        raise RuntimeError(
            f"FFC ADP download failed: {exc}. Retry later or add --offline to reuse a snapshot."
        ) from exc
    payload = response.json()
    if not isinstance(payload, dict):
        raise ValueError("FFC response was not a JSON object.")
    raw_bytes = json.dumps(payload, indent=2, sort_keys=True).encode("utf-8") + b"\n"
    raw_path, acquired_at = _archive(config).write_bytes("ffc_adp", stem, ".json", raw_bytes)
    manifest, manifest_path = _archive(config).create_manifest(
        source="ffc",
        acquisition_method="documented-rest-api",
        acquired_at=acquired_at,
        raw_files=[raw_path],
        seasons=[season],
        notes=f"format={scoring_format}; teams={teams}; position={position_label}",
    )
    return SnapshotResult(
        raw_path,
        manifest,
        manifest_path,
        normalize_ffc_payload(payload, season=season, scoring_format=scoring_format, teams=teams),
    )
