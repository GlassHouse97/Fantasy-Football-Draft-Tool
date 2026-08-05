"""Official nflverse acquisition through the documented nflreadpy interface."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path

from fantasy_draft_ai.config import AppConfig
from fantasy_draft_ai.data.manifests import RawArchive, SourceManifest, utc_now


@dataclass(frozen=True)
class NflverseResult:
    player_path: Path
    stats_path: Path
    manifest: SourceManifest
    manifest_path: Path
    reused_offline: bool = False


@dataclass(frozen=True)
class NflverseSnapCountsResult:
    """One immutable Pro Football Reference snap-count capture."""

    snap_counts_path: Path
    manifest: SourceManifest
    manifest_path: Path
    reused_offline: bool = False


def _archive(config: AppConfig) -> RawArchive:
    return RawArchive(
        project_root=config.project_root,
        raw_root=config.resolve(config.paths.raw_dir),
        manifest_root=config.resolve(config.paths.manifests),
    )


def download_nflverse(
    config: AppConfig, *, start_season: int, end_season: int, offline: bool = False
) -> NflverseResult:
    """Archive player identities and weekly stats for completed seasons."""

    if start_season > end_season:
        raise ValueError("start_season must not be after end_season.")
    if start_season < 1999 or end_season > config.project.prediction_season:
        raise ValueError(
            f"Requested seasons must be between 1999 and {config.project.prediction_season}."
        )

    range_label = f"{start_season}-{end_season}"
    raw_dir = config.resolve(config.paths.raw_dir) / "nflverse"
    player_pattern = f"nflverse_players__{range_label}__*.parquet"
    stats_pattern = f"nflverse_player_stats__weekly__{range_label}__*.parquet"

    if offline:
        players = sorted(raw_dir.glob(player_pattern))
        stats = sorted(raw_dir.glob(stats_pattern))
        if not players or not stats:
            raise FileNotFoundError(
                f"Offline files not found for seasons {range_label}; run once without --offline."
            )
        player_path, stats_path = players[-1], stats[-1]
        acquired_at = datetime.fromtimestamp(
            max(player_path.stat().st_mtime, stats_path.stat().st_mtime), tz=UTC
        )
        archive = _archive(config)
        existing = archive.find_manifest_for_files([player_path, stats_path])
        if existing is None:
            manifest, manifest_path = archive.create_manifest(
                source="nflverse",
                acquisition_method="offline-cache",
                acquired_at=acquired_at,
                raw_files=[player_path, stats_path],
                seasons=list(range(start_season, end_season + 1)),
                notes="Reused existing immutable captures; no network request made.",
            )
        else:
            manifest, manifest_path = existing
        return NflverseResult(player_path, stats_path, manifest, manifest_path, reused_offline=True)

    try:
        import nflreadpy as nfl  # type: ignore[import-untyped]
    except ImportError as exc:  # pragma: no cover - packaging guards this for normal installs
        raise RuntimeError("nflreadpy is not installed; run pip install -e .") from exc

    seasons = list(range(start_season, end_season + 1))
    try:
        players_frame = nfl.load_players()
        stats_frame = nfl.load_player_stats(seasons=seasons, summary_level="week")
    except Exception as exc:  # nflreadpy may surface source-specific exceptions
        raise RuntimeError(
            f"nflverse download failed: {exc}. Retry later or add --offline to reuse captures."
        ) from exc

    acquired_at = utc_now()
    player_path, _ = _archive(config).new_path(
        "nflverse", f"nflverse_players__{range_label}", ".parquet", acquired_at
    )
    stats_path, _ = _archive(config).new_path(
        "nflverse",
        f"nflverse_player_stats__weekly__{range_label}",
        ".parquet",
        acquired_at,
    )
    players_frame.write_parquet(player_path)
    stats_frame.write_parquet(stats_path)
    manifest, manifest_path = _archive(config).create_manifest(
        source="nflverse",
        acquisition_method="nflreadpy",
        acquired_at=acquired_at,
        raw_files=[player_path, stats_path],
        seasons=seasons,
        notes="Players plus weekly player statistics; raw returned frames retained as Parquet.",
    )
    return NflverseResult(player_path, stats_path, manifest, manifest_path)


def download_nflverse_snap_counts(
    config: AppConfig, *, start_season: int, end_season: int, offline: bool = False
) -> NflverseSnapCountsResult:
    """Archive nflverse/PFR game-level snap counts without overwriting prior captures."""

    if start_season > end_season:
        raise ValueError("start_season must not be after end_season.")
    if start_season < 2012 or end_season > config.project.prediction_season:
        raise ValueError(
            f"Requested snap-count seasons must be between 2012 and "
            f"{config.project.prediction_season}."
        )

    range_label = f"{start_season}-{end_season}"
    raw_dir = config.resolve(config.paths.raw_dir) / "nflverse"
    pattern = f"nflverse_snap_counts__{range_label}__*.parquet"
    archive = _archive(config)

    if offline:
        snapshots = sorted(raw_dir.glob(pattern))
        if not snapshots:
            raise FileNotFoundError(
                f"Offline snap-count file not found for seasons {range_label}; "
                "run once without --offline."
            )
        snap_counts_path = snapshots[-1]
        acquired_at = datetime.fromtimestamp(snap_counts_path.stat().st_mtime, tz=UTC)
        existing = archive.find_manifest_for_files([snap_counts_path])
        if existing is None:
            manifest, manifest_path = archive.create_manifest(
                source="nflverse",
                acquisition_method="offline-cache",
                acquired_at=acquired_at,
                raw_files=[snap_counts_path],
                seasons=list(range(start_season, end_season + 1)),
                notes=(
                    "Reused existing immutable nflverse/PFR snap-count capture; "
                    "no network request made."
                ),
            )
        else:
            manifest, manifest_path = existing
        return NflverseSnapCountsResult(
            snap_counts_path,
            manifest,
            manifest_path,
            reused_offline=True,
        )

    try:
        import nflreadpy as nfl
    except ImportError as exc:  # pragma: no cover - packaging guards normal installs
        raise RuntimeError("nflreadpy is not installed; run pip install -e .") from exc

    seasons = list(range(start_season, end_season + 1))
    try:
        snap_counts_frame = nfl.load_snap_counts(seasons=seasons)
    except Exception as exc:  # nflreadpy may surface source-specific exceptions
        raise RuntimeError(
            f"nflverse snap-count download failed: {exc}. Retry later or use offline reuse."
        ) from exc

    acquired_at = utc_now()
    snap_counts_path, _ = archive.new_path(
        "nflverse",
        f"nflverse_snap_counts__{range_label}",
        ".parquet",
        acquired_at,
    )
    snap_counts_frame.write_parquet(snap_counts_path)
    manifest, manifest_path = archive.create_manifest(
        source="nflverse",
        acquisition_method="nflreadpy.load_snap_counts",
        acquired_at=acquired_at,
        raw_files=[snap_counts_path],
        seasons=seasons,
        notes=(
            "Pro Football Reference game-level snap counts distributed by nflverse; "
            "raw returned frame retained as Parquet."
        ),
    )
    return NflverseSnapCountsResult(snap_counts_path, manifest, manifest_path)
