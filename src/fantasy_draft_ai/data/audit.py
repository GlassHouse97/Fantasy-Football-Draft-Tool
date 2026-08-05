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
    warehouse = Warehouse(config.resolve(config.paths.warehouse))
    counts = warehouse.table_counts()
    if warehouse.path.exists():
        with warehouse.connect(read_only=True) as connection:
            orphan_mappings = connection.execute(
                "SELECT count(*) FROM player_source_mappings m LEFT JOIN players p "
                "ON m.player_id = p.player_id WHERE p.player_id IS NULL"
            ).fetchone()
            orphan_candidates = connection.execute(
                "SELECT count(*) FROM identity_review_queue q LEFT JOIN players p "
                "ON q.candidate_player_id = p.player_id "
                "WHERE q.candidate_player_id IS NOT NULL AND p.player_id IS NULL"
            ).fetchone()
            if orphan_mappings is None or int(orphan_mappings[0]):
                failures.append("Canonical identity mappings contain orphan player IDs.")
            if orphan_candidates is None or int(orphan_candidates[0]):
                failures.append("Identity review candidates contain orphan player IDs.")
            for column in (
                "gsis_id",
                "espn_id",
                "sleeper_id",
                "yahoo_id",
                "mfl_id",
                "fleaflicker_id",
                "fantasypros_id",
            ):
                duplicate = connection.execute(
                    f"SELECT count(*) FROM (SELECT {column} FROM players "
                    f"WHERE {column} IS NOT NULL GROUP BY {column} HAVING count(*) > 1)"
                ).fetchone()
                if duplicate is None or int(duplicate[0]):
                    failures.append(f"Players contain duplicate non-null {column} values.")
    return AuditResult(len(manifest_paths), verified, tuple(failures), counts)
