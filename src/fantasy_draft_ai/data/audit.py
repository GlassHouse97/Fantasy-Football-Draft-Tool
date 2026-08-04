"""Verify manifests and summarize local warehouse state."""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path

from fantasy_draft_ai.config import AppConfig
from fantasy_draft_ai.data.manifests import SourceManifest, sha256_file
from fantasy_draft_ai.data.warehouse import Warehouse


@dataclass(frozen=True)
class AuditResult:
    manifest_count: int
    verified_files: int
    failures: tuple[str, ...]
    table_counts: dict[str, int]

    @property
    def passed(self) -> bool:
        return not self.failures


def audit_project_data(config: AppConfig) -> AuditResult:
    manifest_dir = config.resolve(config.paths.manifests)
    failures: list[str] = []
    verified = 0
    manifest_paths = sorted(manifest_dir.glob("*.json")) if manifest_dir.exists() else []
    for manifest_path in manifest_paths:
        try:
            payload = json.loads(manifest_path.read_text(encoding="utf-8"))
            manifest = SourceManifest.model_validate(payload)
        except Exception as exc:
            failures.append(f"Invalid manifest {manifest_path.name}: {exc}")
            continue
        if len(manifest.raw_files) != len(manifest.sha256):
            failures.append(f"Manifest {manifest.dataset_id} has mismatched file/hash counts.")
            continue
        for relative, expected in zip(manifest.raw_files, manifest.sha256, strict=True):
            path = config.project_root / Path(relative)
            if not path.is_file():
                failures.append(f"Missing raw file: {relative}")
            elif sha256_file(path) != expected:
                failures.append(f"Hash mismatch: {relative}")
            else:
                verified += 1
    counts = Warehouse(config.resolve(config.paths.warehouse)).table_counts()
    return AuditResult(len(manifest_paths), verified, tuple(failures), counts)
