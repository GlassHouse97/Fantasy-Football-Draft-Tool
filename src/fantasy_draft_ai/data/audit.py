"""Verify manifests and summarize local warehouse state."""

from __future__ import annotations

import hashlib
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
            orphan_participation = connection.execute(
                "SELECT count(*) FROM player_game_participation g LEFT JOIN players p "
                "ON g.player_id = p.player_id WHERE p.player_id IS NULL"
            ).fetchone()
            orphan_features = connection.execute(
                "SELECT count(*) FROM player_season_features f LEFT JOIN players p "
                "ON f.player_id = p.player_id WHERE p.player_id IS NULL"
            ).fetchone()
            orphan_targets = connection.execute(
                "SELECT count(*) FROM player_season_targets t LEFT JOIN players p "
                "ON t.player_id = p.player_id WHERE p.player_id IS NULL"
            ).fetchone()
            feature_violations = connection.execute(
                "SELECT count(*) FROM player_season_features "
                "WHERE feature_season <> prediction_season - 1 "
                "OR source_max_stat_season > feature_season "
                "OR target_payload IS NOT NULL"
            ).fetchone()
            feature_duplicates = connection.execute(
                "SELECT count(*) FROM (SELECT player_id, prediction_season "
                "FROM player_season_features GROUP BY player_id, prediction_season "
                "HAVING count(*) > 1)"
            ).fetchone()
            orphan_baselines = connection.execute(
                "SELECT count(*) FROM baseline_predictions b LEFT JOIN players p "
                "ON b.player_id = p.player_id WHERE p.player_id IS NULL"
            ).fetchone()
            feature_build_integrity = connection.execute(
                """
                SELECT count(*)
                FROM feature_build_metadata AS metadata
                WHERE (SELECT count(*) FROM feature_build_metadata) = 1
                  AND metadata.data_fingerprint = (
                    SELECT min(data_fingerprint)
                    FROM player_season_features
                    WHERE source = 'nflverse'
                )
                  AND metadata.target_data_fingerprint IS NOT NULL
                  AND metadata.build_fingerprint IS NOT NULL
                  AND metadata.feature_rows = (
                    SELECT count(*)
                    FROM player_season_features
                    WHERE source = 'nflverse'
                  )
                  AND metadata.target_rows = (
                    SELECT count(*)
                    FROM player_season_targets
                    WHERE source = 'nflverse'
                  )
                  AND NOT EXISTS (
                    SELECT 1
                    FROM player_season_features AS feature
                    WHERE feature.source = 'nflverse'
                      AND (
                          feature.data_fingerprint IS DISTINCT FROM
                              metadata.data_fingerprint
                          OR feature.scoring_ruleset_fingerprint IS DISTINCT FROM
                              metadata.scoring_ruleset_fingerprint
                      )
                  )
                  AND NOT EXISTS (
                    SELECT 1
                    FROM player_season_targets AS target
                    WHERE target.source = 'nflverse'
                      AND (
                          target.data_fingerprint IS DISTINCT FROM
                             metadata.data_fingerprint
                          OR target.target_data_fingerprint IS DISTINCT FROM
                             metadata.target_data_fingerprint
                          OR target.scoring_ruleset_fingerprint IS DISTINCT FROM
                             metadata.scoring_ruleset_fingerprint
                      )
                  )
                """
            ).fetchone()
            active_feature_rows = connection.execute(
                "SELECT count(*) FROM player_season_features WHERE source = 'nflverse'"
            ).fetchone()
            feature_fingerprint_summary = connection.execute(
                """
                SELECT
                    count(DISTINCT data_fingerprint),
                    count(*) FILTER (WHERE data_fingerprint IS NULL),
                    min(data_fingerprint)
                FROM player_season_features
                WHERE source = 'nflverse'
                """
            ).fetchone()
            metadata_rows = connection.execute(
                """
                SELECT
                    data_fingerprint,
                    target_data_fingerprint,
                    build_fingerprint,
                    feature_version,
                    scoring_ruleset_fingerprint
                FROM feature_build_metadata
                ORDER BY data_fingerprint
                """
            ).fetchall()
            stale_baselines = connection.execute(
                """
                SELECT count(*)
                FROM baseline_predictions AS baseline
                WHERE NOT EXISTS (
                    SELECT 1
                    FROM feature_build_metadata AS metadata
                    WHERE (SELECT count(*) FROM feature_build_metadata) = 1
                      AND metadata.data_fingerprint = (
                          SELECT min(data_fingerprint)
                          FROM player_season_features
                          WHERE source = 'nflverse'
                      )
                      AND baseline.feature_data_fingerprint = metadata.data_fingerprint
                      AND baseline.target_data_fingerprint =
                          metadata.target_data_fingerprint
                      AND baseline.build_fingerprint = metadata.build_fingerprint
                )
                """
            ).fetchone()
            stale_evaluations = connection.execute(
                """
                SELECT count(*)
                FROM baseline_evaluation_metadata AS evaluation
                WHERE NOT EXISTS (
                    SELECT 1
                    FROM feature_build_metadata AS metadata
                    WHERE (SELECT count(*) FROM feature_build_metadata) = 1
                      AND metadata.data_fingerprint = (
                          SELECT min(data_fingerprint)
                          FROM player_season_features
                          WHERE source = 'nflverse'
                      )
                      AND evaluation.feature_data_fingerprint = metadata.data_fingerprint
                      AND evaluation.target_data_fingerprint =
                          metadata.target_data_fingerprint
                      AND evaluation.build_fingerprint = metadata.build_fingerprint
                )
                """
            ).fetchone()
            baseline_prediction_count = connection.execute(
                "SELECT count(*) FROM baseline_predictions"
            ).fetchone()
            evaluation_rows = connection.execute(
                """
                SELECT prediction_rows, evaluated_rows, report_payload
                FROM baseline_evaluation_metadata
                ORDER BY report_fingerprint
                """
            ).fetchall()
            if orphan_mappings is None or int(orphan_mappings[0]):
                failures.append("Canonical identity mappings contain orphan player IDs.")
            if orphan_candidates is None or int(orphan_candidates[0]):
                failures.append("Identity review candidates contain orphan player IDs.")
            if orphan_participation is None or int(orphan_participation[0]):
                failures.append("Game participation contains orphan player IDs.")
            if orphan_features is None or int(orphan_features[0]):
                failures.append("Player-season features contain orphan player IDs.")
            if orphan_targets is None or int(orphan_targets[0]):
                failures.append("Player-season targets contain orphan player IDs.")
            if feature_violations is None or int(feature_violations[0]):
                failures.append("Player-season features violate cutoff or target isolation.")
            if feature_duplicates is None or int(feature_duplicates[0]):
                failures.append("Player-season features contain duplicate logical keys.")
            if orphan_baselines is None or int(orphan_baselines[0]):
                failures.append("Baseline predictions contain orphan player IDs.")
            active_count = int(active_feature_rows[0]) if active_feature_rows is not None else 0
            if active_count:
                if (
                    feature_fingerprint_summary is None
                    or int(feature_fingerprint_summary[0]) != 1
                    or int(feature_fingerprint_summary[1]) != 0
                ):
                    failures.append(
                        "Player-season features do not have one complete active fingerprint."
                    )
                if len(metadata_rows) != 1:
                    failures.append("Exactly one active feature-build metadata row is required.")
                else:
                    metadata = metadata_rows[0]
                    expected_build = _expected_build_fingerprint(
                        str(metadata[0]),
                        str(metadata[1]),
                        str(metadata[3]),
                        str(metadata[4]),
                    )
                    if metadata[1] is None or str(metadata[2]) != expected_build:
                        failures.append("Feature-build metadata has an invalid build fingerprint.")
            elif metadata_rows:
                failures.append("Feature-build metadata exists without active feature rows.")
            if active_count and (
                feature_build_integrity is None or int(feature_build_integrity[0]) != 1
            ):
                failures.append("Feature and target tables do not match one active build.")
            if stale_baselines is None or int(stale_baselines[0]):
                failures.append("Baseline predictions are stale for the active feature build.")
            if stale_evaluations is None or int(stale_evaluations[0]):
                failures.append("Baseline evaluation metadata is stale for the active build.")
            prediction_count = (
                int(baseline_prediction_count[0]) if baseline_prediction_count is not None else -1
            )
            if prediction_count or evaluation_rows:
                if len(evaluation_rows) != 1:
                    failures.append("Exactly one active baseline evaluation is required.")
                else:
                    evaluation = evaluation_rows[0]
                    report = json.loads(str(evaluation[2]))
                    evaluation_metadata = metadata_rows[0] if len(metadata_rows) == 1 else None
                    if (
                        int(evaluation[0]) != prediction_count
                        or int(report.get("prediction_rows", -1)) != prediction_count
                        or int(evaluation[1]) != int(report.get("evaluated_rows", -1))
                        or evaluation_metadata is None
                        or report.get("feature_data_fingerprint") != evaluation_metadata[0]
                        or report.get("target_data_fingerprint") != evaluation_metadata[1]
                        or report.get("build_fingerprint") != evaluation_metadata[2]
                    ):
                        failures.append("Baseline evaluation row accounting is stale.")
            for column in (
                "gsis_id",
                "pfr_id",
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
    from fantasy_draft_ai.models.player_projection.repository import (
        projection_integrity_issues,
    )

    failures.extend(projection_integrity_issues(config))
    return AuditResult(len(manifest_paths), verified, tuple(failures), counts)


def _expected_build_fingerprint(
    feature_fingerprint: str,
    target_fingerprint: str,
    feature_version: str,
    scoring_fingerprint: str,
) -> str:
    payload = {
        "feature_data_fingerprint": feature_fingerprint,
        "target_data_fingerprint": target_fingerprint,
        "feature_version": feature_version,
        "scoring_ruleset_fingerprint": scoring_fingerprint,
    }
    encoded = json.dumps(
        payload,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=True,
        allow_nan=False,
    ).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()
