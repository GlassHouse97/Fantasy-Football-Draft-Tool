"""Immutable raw-file naming, hashing, and provenance manifests."""

from __future__ import annotations

import hashlib
import json
from datetime import UTC, datetime
from pathlib import Path
from uuid import uuid4

from pydantic import BaseModel, ConfigDict, Field


def sha256_file(path: Path, chunk_size: int = 1024 * 1024) -> str:
    """Return a file's SHA-256 digest without loading it all into memory."""

    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(chunk_size), b""):
            digest.update(chunk)
    return digest.hexdigest()


def utc_now() -> datetime:
    return datetime.now(UTC)


def file_timestamp(moment: datetime) -> str:
    return moment.astimezone(UTC).strftime("%Y-%m-%dT%H%M%S%fZ")


class SourceManifest(BaseModel):
    """Small reproducibility record stored next to the raw archive tree."""

    model_config = ConfigDict(extra="forbid")

    dataset_id: str
    source: str
    acquisition_method: str
    acquired_at: datetime
    seasons: list[int] = Field(default_factory=list)
    raw_files: list[str]
    sha256: list[str]
    schema_version: str = "1.0"
    notes: str = ""


class RawArchive:
    """Create timestamped raw paths and manifests without overwriting captures."""

    def __init__(self, project_root: Path, raw_root: Path, manifest_root: Path) -> None:
        self.project_root = project_root.resolve()
        self.raw_root = raw_root.resolve()
        self.manifest_root = manifest_root.resolve()

    def new_path(
        self,
        source_directory: str,
        filename_stem: str,
        suffix: str,
        acquired_at: datetime | None = None,
    ) -> tuple[Path, datetime]:
        moment = acquired_at or utc_now()
        directory = self.raw_root / source_directory
        directory.mkdir(parents=True, exist_ok=True)
        path = directory / f"{filename_stem}__{file_timestamp(moment)}{suffix}"
        if path.exists():
            raise FileExistsError(f"Refusing to overwrite immutable raw file: {path}")
        return path, moment

    def write_bytes(
        self,
        source_directory: str,
        filename_stem: str,
        suffix: str,
        content: bytes,
        acquired_at: datetime | None = None,
    ) -> tuple[Path, datetime]:
        path, moment = self.new_path(
            source_directory, filename_stem, suffix, acquired_at=acquired_at
        )
        path.write_bytes(content)
        return path, moment

    def create_manifest(
        self,
        *,
        source: str,
        acquisition_method: str,
        acquired_at: datetime,
        raw_files: list[Path],
        seasons: list[int] | None = None,
        notes: str = "",
    ) -> tuple[SourceManifest, Path]:
        for path in raw_files:
            if not path.is_file():
                raise FileNotFoundError(path)
        manifest = SourceManifest(
            dataset_id=str(uuid4()),
            source=source,
            acquisition_method=acquisition_method,
            acquired_at=acquired_at,
            seasons=seasons or [],
            raw_files=[
                path.resolve().relative_to(self.project_root).as_posix() for path in raw_files
            ],
            sha256=[sha256_file(path) for path in raw_files],
            notes=notes,
        )
        self.manifest_root.mkdir(parents=True, exist_ok=True)
        manifest_path = self.manifest_root / f"{manifest.dataset_id}.json"
        manifest_path.write_text(
            json.dumps(manifest.model_dump(mode="json"), indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )
        return manifest, manifest_path

    def find_manifest_for_files(
        self, raw_files: list[Path]
    ) -> tuple[SourceManifest, Path] | None:
        """Find an existing manifest for an identical raw-file set.

        Offline replay uses this to remain idempotent instead of manufacturing a
        second provenance record for files that were already archived.
        """

        expected = {
            path.resolve().relative_to(self.project_root).as_posix() for path in raw_files
        }
        if not self.manifest_root.exists():
            return None
        for manifest_path in sorted(self.manifest_root.glob("*.json")):
            try:
                payload = json.loads(manifest_path.read_text(encoding="utf-8"))
                manifest = SourceManifest.model_validate(payload)
            except (OSError, ValueError, json.JSONDecodeError):
                continue
            if set(manifest.raw_files) == expected:
                return manifest, manifest_path
        return None
