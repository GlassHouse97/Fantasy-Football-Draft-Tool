"""Verify manifests and summarize local warehouse state."""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from pathlib import Path

import duckdb

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
            failures.extend(_league_history_integrity_issues(connection))
    from fantasy_draft_ai.models.adp.build import adp_market_integrity_issues
    from fantasy_draft_ai.models.player_projection.repository import (
        projection_integrity_issues,
    )

    failures.extend(projection_integrity_issues(config))
    failures.extend(adp_market_integrity_issues(config))
    from fantasy_draft_ai.draft.repository import DraftRepository

    failures.extend(DraftRepository(config.resolve(config.paths.warehouse)).integrity_issues())
    return AuditResult(len(manifest_paths), verified, tuple(failures), counts)


def _league_history_integrity_issues(
    connection: duckdb.DuckDBPyConnection,
) -> tuple[str, ...]:
    """Reconcile Phase 8 provenance without requiring history to exist."""

    issues: list[str] = []
    checks = (
        (
            "League-history metadata references a missing import package.",
            """
            SELECT count(*)
            FROM league_history_leagues AS league
            LEFT JOIN league_history_imports AS package USING (package_fingerprint)
            WHERE package.package_fingerprint IS NULL
            """,
        ),
        (
            "League-history metadata does not match its canonical rules row.",
            """
            SELECT count(*)
            FROM league_history_leagues AS history
            LEFT JOIN league_rules AS rules USING (league_season_id)
            WHERE rules.league_season_id IS NULL
               OR rules.user_draft_slot IS NOT NULL
               OR rules.season <> history.season
               OR rules.team_count <> history.team_count
               OR rules.ruleset_fingerprint <> history.ruleset_fingerprint
            """,
        ),
        (
            "Historical draft picks contain orphan canonical player IDs.",
            """
            SELECT count(*)
            FROM draft_picks AS pick
            LEFT JOIN players AS player USING (player_id)
            WHERE pick.player_id IS NOT NULL AND player.player_id IS NULL
            """,
        ),
        (
            "Imported draft-pick rows are not linked to league-history metadata.",
            """
            SELECT count(*)
            FROM draft_picks AS pick
            LEFT JOIN league_history_leagues AS history USING (league_season_id)
            WHERE pick.source_dataset_id IS NOT NULL
              AND history.league_season_id IS NULL
            """,
        ),
        (
            "Imported team-outcome rows are not linked to league-history metadata.",
            """
            SELECT count(*)
            FROM team_outcomes AS outcome
            LEFT JOIN league_history_leagues AS history USING (league_season_id)
            WHERE outcome.source_dataset_id IS NOT NULL
              AND history.league_season_id IS NULL
            """,
        ),
        (
            "League-history canonical rows do not match their manifest dataset lineage.",
            """
            SELECT count(*) FROM (
                SELECT rules.source_dataset_id, package.manifest_dataset_id
                FROM league_history_leagues AS history
                JOIN league_history_imports AS package USING (package_fingerprint)
                JOIN league_rules AS rules USING (league_season_id)
                UNION ALL
                SELECT pick.source_dataset_id, package.manifest_dataset_id
                FROM league_history_leagues AS history
                JOIN league_history_imports AS package USING (package_fingerprint)
                JOIN draft_picks AS pick USING (league_season_id)
                UNION ALL
                SELECT outcome.source_dataset_id, package.manifest_dataset_id
                FROM league_history_leagues AS history
                JOIN league_history_imports AS package USING (package_fingerprint)
                JOIN team_outcomes AS outcome USING (league_season_id)
            ) AS lineage
            WHERE source_dataset_id IS DISTINCT FROM manifest_dataset_id
            """,
        ),
        (
            "Roster-construction features contain invalid league-history lineage.",
            """
            SELECT count(*)
            FROM roster_construction_features AS feature
            LEFT JOIN league_history_leagues AS history USING (league_season_id)
            WHERE history.league_season_id IS NULL
               OR feature.package_fingerprint <> history.package_fingerprint
               OR feature.ruleset_fingerprint <> history.ruleset_fingerprint
               OR NOT EXISTS (
                   SELECT 1 FROM draft_picks AS pick
                   WHERE pick.league_season_id = feature.league_season_id
                     AND pick.team_id = feature.team_id
               )
            """,
        ),
        (
            "Draft-only team metrics contain invalid league-history lineage.",
            """
            SELECT count(*)
            FROM draft_only_team_metrics AS metric
            LEFT JOIN league_history_leagues AS history USING (league_season_id)
            WHERE history.league_season_id IS NULL
               OR metric.package_fingerprint <> history.package_fingerprint
               OR NOT EXISTS (
                   SELECT 1 FROM draft_picks AS pick
                   WHERE pick.league_season_id = metric.league_season_id
                     AND pick.team_id = metric.team_id
               )
            """,
        ),
    )
    for message, query in checks:
        if _audit_count(connection, query):
            issues.append(message)

    malformed_fingerprints = _audit_count(
        connection,
        """
        SELECT count(*)
        FROM league_history_imports
        WHERE NOT regexp_matches(package_fingerprint, '^[0-9a-f]{64}$')
           OR NOT regexp_matches(raw_sha256, '^[0-9a-f]{64}$')
           OR NOT regexp_matches(normalized_fingerprint, '^[0-9a-f]{64}$')
        """,
    )
    malformed_fingerprints += _audit_count(
        connection,
        """
        SELECT count(*) FROM (
            SELECT source_dataset_id, row_fingerprint, loaded_at FROM league_rules
            UNION ALL
            SELECT source_dataset_id, row_fingerprint, loaded_at FROM draft_picks
            UNION ALL
            SELECT source_dataset_id, row_fingerprint, loaded_at FROM team_outcomes
        ) AS source_row
        WHERE source_dataset_id IS NOT NULL
          AND (
              row_fingerprint IS NULL
              OR NOT regexp_matches(row_fingerprint, '^[0-9a-f]{64}$')
              OR loaded_at IS NULL
          )
        """,
    )
    if malformed_fingerprints:
        issues.append("League-history provenance contains invalid SHA-256 or load metadata.")

    package_count_mismatches = _audit_count(
        connection,
        """
        SELECT count(*)
        FROM league_history_imports AS package
        WHERE package.league_count <> (
                  SELECT count(*) FROM league_history_leagues AS history
                  WHERE history.package_fingerprint = package.package_fingerprint
              )
           OR package.rules_rows <> (
                  SELECT count(*)
                  FROM league_history_leagues AS history
                  JOIN league_rules AS rules USING (league_season_id)
                  WHERE history.package_fingerprint = package.package_fingerprint
              )
           OR package.pick_rows <> (
                  SELECT count(*)
                  FROM league_history_leagues AS history
                  JOIN draft_picks AS pick USING (league_season_id)
                  WHERE history.package_fingerprint = package.package_fingerprint
              )
           OR package.outcome_rows <> (
                  SELECT count(*)
                  FROM league_history_leagues AS history
                  JOIN team_outcomes AS outcome USING (league_season_id)
                  WHERE history.package_fingerprint = package.package_fingerprint
              )
           OR package.unresolved_player_rows <> (
                  SELECT count(*)
                  FROM league_history_leagues AS history
                  JOIN draft_picks AS pick USING (league_season_id)
                  WHERE history.package_fingerprint = package.package_fingerprint
                    AND pick.player_id IS NULL
              )
        """,
    )
    if package_count_mismatches:
        issues.append("League-history import row accounting does not reconcile.")

    league_count_mismatches = _audit_count(
        connection,
        """
        SELECT count(*)
        FROM league_history_leagues AS history
        JOIN league_rules AS rules USING (league_season_id)
        WHERE history.expected_pick_rows <> history.team_count * rules.rounds
           OR history.actual_pick_rows <> (
                  SELECT count(*) FROM draft_picks AS pick
                  WHERE pick.league_season_id = history.league_season_id
              )
           OR history.outcome_rows <> (
                  SELECT count(*) FROM team_outcomes AS outcome
                  WHERE outcome.league_season_id = history.league_season_id
              )
           OR history.resolved_pick_rows <> (
                  SELECT count(*) FROM draft_picks AS pick
                  WHERE pick.league_season_id = history.league_season_id
                    AND pick.player_id IS NOT NULL
              )
           OR (history.draft_complete AND history.actual_pick_rows <> history.expected_pick_rows)
           OR (history.outcomes_complete AND history.outcome_rows <> history.team_count)
           OR (
               history.analysis_ready
               AND (
                   NOT history.draft_complete
                   OR NOT history.outcomes_complete
                   OR history.resolved_pick_rows <> history.actual_pick_rows
               )
           )
        """,
    )
    if league_count_mismatches:
        issues.append("League-history league row accounting or readiness is inconsistent.")

    invalid_metric_values = _audit_count(
        connection,
        """
        SELECT count(*)
        FROM draft_only_team_metrics
        WHERE weeks_scored < 0
           OR drafted_starter_games < 0
           OR starter_slot_weeks < 0
           OR unfilled_starter_slot_weeks < 0
           OR unfilled_starter_slot_weeks > starter_slot_weeks
           OR mapping_coverage < 0 OR mapping_coverage > 1
           OR (points_percentile IS NOT NULL AND (points_percentile < 0 OR points_percentile > 1))
        """,
    )
    if invalid_metric_values:
        issues.append("Draft-only team metrics contain invalid counts or proportions.")
    return tuple(issues)


def _audit_count(connection: duckdb.DuckDBPyConnection, query: str) -> int:
    row = connection.execute(query).fetchone()
    if row is None:
        raise RuntimeError("DuckDB did not return an integrity count.")
    return int(row[0])


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
