"""Truthful capability and local-data status reporting."""

from __future__ import annotations

from contextlib import suppress
from dataclasses import dataclass
from pathlib import Path

import duckdb
import yaml

from fantasy_draft_ai.config import AppConfig
from fantasy_draft_ai.draft.repository import DraftRepository
from fantasy_draft_ai.recommendations.config import load_draft_engine_config
from fantasy_draft_ai.rules.models import LeagueRules
from fantasy_draft_ai.services.adp_market import adp_market_status, load_adp_market_board
from fantasy_draft_ai.services.draft_room import DraftRoomReadiness, prepare_draft_room
from fantasy_draft_ai.services.projections import (
    ProjectionBoardStatus,
    load_projection_board,
    projection_board_status,
)


@dataclass(frozen=True)
class StatusItem:
    name: str
    status: str
    available: bool


def project_status(
    config: AppConfig,
    *,
    phase4_status: ProjectionBoardStatus | None = None,
    draft_readiness: DraftRoomReadiness | None = None,
) -> list[StatusItem]:
    raw_root = config.resolve(config.paths.raw_dir)
    ffc_files = sorted((raw_root / "ffc_adp").glob("*.json"))
    espn_files = sorted((raw_root / "espn_manual").glob("*.csv"))
    nfl_player_files = sorted((raw_root / "nflverse").glob("nflverse_players__*.parquet"))
    nfl_stat_files = sorted(
        (raw_root / "nflverse").glob("nflverse_player_stats__weekly__*.parquet")
    )
    snap_count_files = sorted((raw_root / "nflverse").glob("nflverse_snap_counts__*.parquet"))
    warehouse = config.resolve(config.paths.warehouse)

    def latest_label(files: list[Path]) -> str:
        return files[-1].name if files else "not available"

    identity_status = "not built; run fantasy-draft data review-identities"
    identity_available = False
    feature_status = "not built; run fantasy-draft features build-player-seasons"
    feature_available = False
    baseline_status = "not evaluated; run fantasy-draft models evaluate-baselines"
    baseline_available = False
    current_phase4_status = phase4_status or ProjectionBoardStatus(
        available=False,
        code="not_built",
        message="not built; train and validate Phase 4 first",
    )
    if warehouse.exists():
        counts = None
        feature_counts = None
        baseline_counts = None
        try:
            with duckdb.connect(str(warehouse), read_only=True) as connection:
                with suppress(duckdb.Error):
                    counts = connection.execute(
                        "SELECT count(*) FILTER (WHERE status = 'pending' AND is_current), "
                        "count(*) FILTER (WHERE status = 'resolved' AND is_current) "
                        "FROM identity_review_queue"
                    ).fetchone()
                with suppress(duckdb.Error):
                    feature_counts = connection.execute(
                        """
                        WITH feature_summary AS (
                            SELECT
                                count(*) AS feature_rows,
                                max(prediction_season) AS max_prediction_season,
                                count(DISTINCT data_fingerprint) AS fingerprint_count,
                                count(*) FILTER (
                                    WHERE data_fingerprint IS NULL
                                ) AS null_fingerprints,
                                min(data_fingerprint) AS active_fingerprint
                            FROM player_season_features
                            WHERE source = 'nflverse'
                        )
                        SELECT
                            summary.feature_rows,
                            summary.max_prediction_season,
                            summary.fingerprint_count,
                            summary.null_fingerprints,
                            (
                                SELECT count(*)
                                FROM feature_build_metadata AS metadata
                                WHERE (SELECT count(*) FROM feature_build_metadata) = 1
                                  AND metadata.data_fingerprint =
                                      summary.active_fingerprint
                                  AND metadata.target_data_fingerprint IS NOT NULL
                                  AND metadata.build_fingerprint IS NOT NULL
                                  AND metadata.build_fingerprint = sha256(
                                      '{"feature_data_fingerprint":"'
                                      || metadata.data_fingerprint
                                      || '","feature_version":"'
                                      || metadata.feature_version
                                      || '","scoring_ruleset_fingerprint":"'
                                      || metadata.scoring_ruleset_fingerprint
                                      || '","target_data_fingerprint":"'
                                      || metadata.target_data_fingerprint
                                      || '"}'
                                  )
                                  AND metadata.feature_rows = summary.feature_rows
                                  AND metadata.target_rows = (
                                      SELECT count(*)
                                      FROM player_season_targets
                                      WHERE source = 'nflverse'
                                  )
                                  AND NOT EXISTS (
                                      SELECT 1
                                      FROM player_season_targets AS target
                                      WHERE target.source = 'nflverse'
                                        AND (
                                            target.data_fingerprint IS DISTINCT FROM
                                                metadata.data_fingerprint
                                            OR target.target_data_fingerprint
                                                IS DISTINCT FROM
                                                metadata.target_data_fingerprint
                                        )
                                  )
                            ) AS valid_metadata_rows
                        FROM feature_summary AS summary
                        """
                    ).fetchone()
                with suppress(duckdb.Error):
                    baseline_counts = connection.execute(
                        """
                        WITH active_metadata AS (
                            SELECT metadata.*
                            FROM feature_build_metadata AS metadata
                            WHERE (SELECT count(*) FROM feature_build_metadata) = 1
                              AND metadata.data_fingerprint = (
                                  SELECT min(data_fingerprint)
                                  FROM player_season_features
                                  WHERE source = 'nflverse'
                              )
                              AND 1 = (
                                  SELECT count(DISTINCT data_fingerprint)
                                  FROM player_season_features
                                  WHERE source = 'nflverse'
                              )
                              AND 0 = (
                                  SELECT count(*)
                                  FROM player_season_features
                                  WHERE source = 'nflverse'
                                    AND data_fingerprint IS NULL
                              )
                        ),
                        current_predictions AS (
                            SELECT baseline.*
                            FROM baseline_predictions AS baseline
                            JOIN active_metadata AS metadata
                              ON baseline.build_fingerprint = metadata.build_fingerprint
                             AND baseline.feature_data_fingerprint =
                                 metadata.data_fingerprint
                             AND baseline.target_data_fingerprint =
                                 metadata.target_data_fingerprint
                        ),
                        current_evaluations AS (
                            SELECT evaluation.*
                            FROM baseline_evaluation_metadata AS evaluation
                            JOIN active_metadata AS metadata
                              ON evaluation.build_fingerprint = metadata.build_fingerprint
                             AND evaluation.feature_data_fingerprint =
                                 metadata.data_fingerprint
                             AND evaluation.target_data_fingerprint =
                                 metadata.target_data_fingerprint
                        )
                        SELECT
                            (
                                SELECT count(DISTINCT player_id)
                                FROM current_predictions
                                WHERE prediction_season = ?
                            ),
                            (SELECT count(*) FROM current_evaluations),
                            (SELECT count(*) FROM current_predictions),
                            (SELECT count(*) FROM baseline_predictions),
                            (SELECT count(*) FROM baseline_evaluation_metadata),
                            coalesce(
                                (SELECT max(prediction_rows) FROM current_evaluations), -1
                            ),
                            coalesce(
                                (SELECT max(evaluated_rows) FROM current_evaluations), -1
                            ),
                            coalesce(
                                (
                                    SELECT max(
                                        CAST(
                                            json_extract_string(
                                                report_payload, '$.evaluated_rows'
                                            ) AS INTEGER
                                        )
                                    )
                                    FROM current_evaluations
                                ),
                                -1
                            )
                        """,
                        [config.project.prediction_season],
                    ).fetchone()
            if counts is not None:
                identity_status = f"{int(counts[0])} pending; {int(counts[1])} resolved"
                identity_available = True
            if feature_counts is not None and int(feature_counts[0]):
                feature_status = (
                    f"{int(feature_counts[0])} rows through prediction season "
                    f"{int(feature_counts[1])}; {int(feature_counts[2])} active fingerprint"
                )
                feature_available = (
                    int(feature_counts[2]) == 1
                    and int(feature_counts[3]) == 0
                    and int(feature_counts[4]) == 1
                )
            if (
                baseline_counts is not None
                and feature_available
                and int(baseline_counts[0]) > 0
                and int(baseline_counts[1]) == 1
                and int(baseline_counts[2]) > 0
                and int(baseline_counts[2]) == int(baseline_counts[3])
                and int(baseline_counts[1]) == int(baseline_counts[4])
                and int(baseline_counts[2]) == int(baseline_counts[5])
                and int(baseline_counts[6]) == int(baseline_counts[7])
            ):
                baseline_status = (
                    f"{int(baseline_counts[0])} players projected for "
                    f"{config.project.prediction_season}; evaluation report available"
                )
                baseline_available = True
        except duckdb.Error:
            pass

    if warehouse.exists():
        current_phase4_status = phase4_status or projection_board_status(config)
        if current_phase4_status.available and not (feature_available and baseline_available):
            current_phase4_status = ProjectionBoardStatus(
                available=False,
                code="stale",
                message="Phase 4 exists, but its Phase 3 prerequisites no longer validate",
                run=current_phase4_status.run,
            )

    model_status = current_phase4_status.message
    board_status = current_phase4_status.message
    if current_phase4_status.available and current_phase4_status.run is not None:
        run = current_phase4_status.run
        model_status = (
            f"complete run {run.run_id[:12]}; {run.model_rows} registered models; "
            "active Phase 3 lineage verified"
        )
        board_status = current_phase4_status.message

    phase5_status = adp_market_status(config)
    movement_status = phase5_status.message
    availability_status = phase5_status.message
    supervised_status = phase5_status.supervised_status
    if phase5_status.available:
        movement_status = (
            f"persistence active for {phase5_status.persistence_ready_rows} rows; "
            f"linear/EW ready for {phase5_status.linear_ready_rows}/"
            f"{phase5_status.ew_ready_rows}"
        )
        availability_status = (
            f"distribution baseline active for {phase5_status.availability_rows} rows; "
            f"calibration {phase5_status.calibration_status}"
        )

    current_draft_readiness = draft_readiness
    if current_draft_readiness is None and current_phase4_status.available:
        try:
            reference_path = config.project_root / "configs" / "example_ppr_12_team.yaml"
            with reference_path.open(encoding="utf-8") as handle:
                reference_rules = LeagueRules.model_validate(yaml.safe_load(handle))
            engine_config = load_draft_engine_config(
                config.project_root / "configs" / "draft_engine.yaml"
            )
            current_draft_readiness = prepare_draft_room(
                load_projection_board(config),
                load_adp_market_board(config),
                rules=reference_rules,
                projection_reference_rules=reference_rules,
                required_market_coverage=engine_config.market_coverage_required,
            ).readiness
        except (OSError, ValueError, TypeError, duckdb.Error):
            current_draft_readiness = None

    draft_state_available = bool(
        current_draft_readiness is not None and current_draft_readiness.state_ready
    )
    draft_state_status = (
        current_draft_readiness.state_message
        if current_draft_readiness is not None
        else "unavailable until a compatible projection pool validates"
    )
    recommendation_available = bool(
        current_draft_readiness is not None and current_draft_readiness.recommendation_ready
    )
    recommendation_message = (
        current_draft_readiness.recommendation_message
        if current_draft_readiness is not None
        else "unavailable until draft inputs validate"
    )
    session_count = 0
    replay_issues: tuple[str, ...] = ()
    if warehouse.exists():
        try:
            repository = DraftRepository(warehouse)
            sessions = repository.list_sessions()
            session_count = len(sessions)
            replay_issues = repository.integrity_issues()
        except (OSError, ValueError, TypeError, duckdb.Error):
            replay_issues = ("Draft persistence could not be verified.",)
    replay_status = (
        "warehouse not initialized"
        if not warehouse.exists()
        else replay_issues[0]
        if replay_issues
        else "append-only replay checks passed"
    )

    return [
        StatusItem(
            "Warehouse",
            str(warehouse) if warehouse.exists() else "not initialized",
            warehouse.exists(),
        ),
        StatusItem(
            "nflverse player/week data",
            (
                f"{latest_label(nfl_player_files)} + {latest_label(nfl_stat_files)}"
                if nfl_player_files and nfl_stat_files
                else "not available"
            ),
            bool(nfl_player_files and nfl_stat_files),
        ),
        StatusItem(
            "nflverse/PFR snap counts",
            latest_label(snap_count_files),
            bool(snap_count_files),
        ),
        StatusItem("Raw FFC ADP capture", latest_label(ffc_files), bool(ffc_files)),
        StatusItem("Raw ESPN ADP upload", latest_label(espn_files), bool(espn_files)),
        StatusItem("Identity review queue", identity_status, identity_available),
        StatusItem("Scoring and rules engine", "available (configured logic)", True),
        StatusItem("Player-season features", feature_status, feature_available),
        StatusItem("Transparent projection baselines", baseline_status, baseline_available),
        StatusItem("Player projection model", model_status, current_phase4_status.available),
        StatusItem(
            "Learned 2026 projection board",
            board_status,
            current_phase4_status.available,
        ),
        StatusItem("Canonical ADP warehouse", phase5_status.message, phase5_status.available),
        StatusItem("ADP movement baselines", movement_status, phase5_status.available),
        StatusItem("Next-pick availability", availability_status, phase5_status.available),
        StatusItem("Supervised ADP model", supervised_status, False),
        StatusItem("Historical league outcome model", "insufficient uploaded histories", False),
        StatusItem("Draft state engine", draft_state_status, draft_state_available),
        StatusItem(
            "Active draft session",
            f"{session_count} persisted session(s)" if session_count else "no session created yet",
            bool(session_count),
        ),
        StatusItem(
            "Draft event replay integrity",
            replay_status,
            warehouse.exists() and not replay_issues,
        ),
        StatusItem(
            "Draft recommendation score",
            recommendation_message,
            recommendation_available,
        ),
        StatusItem(
            "Monte Carlo rest-of-draft simulation",
            recommendation_message,
            recommendation_available,
        ),
        StatusItem("Championship probabilities", "disabled", False),
    ]
