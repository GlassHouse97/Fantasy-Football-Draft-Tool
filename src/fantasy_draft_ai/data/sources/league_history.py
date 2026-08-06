"""Immutable quarantine archive for user-supplied league-history packages."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from fantasy_draft_ai.config import AppConfig
from fantasy_draft_ai.data.manifests import RawArchive, SourceManifest

SUPPORTED_HISTORY_SUFFIXES = frozenset({".csv", ".json", ".zip"})
MAX_HISTORY_PACKAGE_BYTES = 100 * 1024 * 1024


@dataclass(frozen=True)
class LeagueHistoryArchiveResult:
    """One archived package that has not been parsed or modeled."""

    raw_path: Path
    manifest: SourceManifest
    manifest_path: Path
    size_bytes: int


def archive_league_history_package(
    config: AppConfig,
    source_path: Path,
) -> LeagueHistoryArchiveResult:
    """Hash and archive a manual history package without inspecting its contents."""

    source = source_path.expanduser().resolve()
    if not source.is_file():
        raise FileNotFoundError(source)
    suffix = source.suffix.casefold()
    if suffix not in SUPPORTED_HISTORY_SUFFIXES:
        raise ValueError(
            "League-history packages must be CSV, JSON, or ZIP files; "
            "archives are not unpacked in Phase 7."
        )
    size_bytes = source.stat().st_size
    if size_bytes < 1:
        raise ValueError("League-history packages cannot be empty.")
    if size_bytes > MAX_HISTORY_PACKAGE_BYTES:
        raise ValueError("League-history packages cannot exceed 100 MB.")

    archive = RawArchive(
        project_root=config.project_root,
        raw_root=config.resolve(config.paths.raw_dir),
        manifest_root=config.resolve(config.paths.manifests),
    )
    raw_path, acquired_at = archive.write_bytes(
        "league_history_manual",
        "league_history_package",
        suffix,
        source.read_bytes(),
    )
    manifest, manifest_path = archive.create_manifest(
        source="league_history",
        acquisition_method="manual-package-upload",
        acquired_at=acquired_at,
        raw_files=[raw_path],
        notes=(
            "Phase 7 archive-only intake. Contents are not unpacked, normalized, or used for "
            "training. Review personal identifiers and use pseudonymous team IDs before upload."
        ),
    )
    return LeagueHistoryArchiveResult(raw_path, manifest, manifest_path, size_bytes)
