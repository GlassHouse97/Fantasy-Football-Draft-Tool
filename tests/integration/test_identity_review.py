from __future__ import annotations

import json
from datetime import UTC, datetime, timedelta
from pathlib import Path
from typing import Any

import pandas as pd

from fantasy_draft_ai.config import (
    AppConfig,
    NetworkSection,
    PathSection,
    ProjectSection,
    TrainingSection,
)
from fantasy_draft_ai.data.audit import audit_project_data
from fantasy_draft_ai.data.identity_review import (
    apply_identity_overrides,
    refresh_identity_review_queue,
)
from fantasy_draft_ai.data.manifests import RawArchive, sha256_file
from fantasy_draft_ai.data.nflverse_loader import load_nflverse_to_warehouse
from fantasy_draft_ai.data.warehouse import Warehouse

ACQUIRED_AT = datetime(2026, 8, 5, 13, 20, 34, tzinfo=UTC)
REVIEWED_AT = "2026-08-05T15:00:00Z"


def _config(project_root: Path) -> AppConfig:
    return AppConfig(
        project=ProjectSection(name="Test Fantasy Football Draft AI", prediction_season=2026),
        paths=PathSection(
            data_dir=Path("data"),
            raw_dir=Path("data/raw"),
            processed_dir=Path("data/processed"),
            warehouse=Path("data/warehouse/test.duckdb"),
            manifests=Path("data/raw/manifests"),
        ),
        network=NetworkSection(timeout_seconds=5, user_agent="test"),
        training=TrainingSection(start_season=2025, end_season=2025),
        project_root=project_root,
    )


def _player(
    player_id: str,
    name: str,
    *,
    position: str = "WR",
    team: str = "BUF",
) -> dict[str, Any]:
    return {
        "gsis_id": player_id,
        "display_name": name,
        "pfr_id": f"pfr-{player_id}",
        "espn_id": f"espn-{player_id}",
        "birth_date": "2000-01-02",
        "position": position,
        "latest_team": team,
        "status": "ACT",
        "last_season": 2026,
        "years_of_experience": 3,
        "rookie_season": 2022,
        "draft_year": 2022,
        "draft_round": 2,
        "draft_pick": 45,
        "draft_team": team,
        "height": 73,
        "weight": 205,
    }


def _weekly_stat(player_id: str, name: str) -> dict[str, Any]:
    return {
        "player_id": player_id,
        "player_display_name": name,
        "position": "WR",
        "season": 2025,
        "week": 1,
        "season_type": "REG",
        "game_id": "2025_01_BUF_MIA",
        "team": "BUF",
        "opponent_team": "MIA",
        "completions": 0,
        "attempts": 0,
        "passing_yards": 0,
        "passing_tds": 0,
        "passing_interceptions": 0,
        "rushing_yards": 0,
        "rushing_tds": 0,
        "receiving_yards": 80,
        "receptions": 5,
        "receiving_tds": 1,
        "targets": 7,
        "carries": 0,
        "passing_2pt_conversions": 0,
        "rushing_2pt_conversions": 0,
        "receiving_2pt_conversions": 0,
        "fumbles_lost_total": 0,
        "special_teams_tds": 0,
        "fg_made": 0,
        "fg_att": 0,
        "pat_made": 0,
        "pat_att": 0,
    }


def _archive_nflverse_capture(
    config: AppConfig,
    *,
    acquired_at: datetime = ACQUIRED_AT,
    master_name: str = "Incorrect Master Name",
) -> Path:
    raw_dir = config.resolve(config.paths.raw_dir) / "nflverse"
    raw_dir.mkdir(parents=True, exist_ok=True)
    stamp = acquired_at.strftime("%Y%m%dT%H%M%S%fZ")
    player_path = raw_dir / f"nflverse_players__2025-2025__{stamp}.parquet"
    stats_path = raw_dir / f"nflverse_player_stats__weekly__2025-2025__{stamp}.parquet"
    players = [
        _player("p-conflict", master_name),
        _player("p-unique", "Unique Receiver"),
        _player("p-suffix", "José Núñez Jr.", position="RB", team="MIA"),
        _player("p-ambiguous-1", "Chris Smith"),
        _player("p-ambiguous-2", "Chris Smith"),
    ]
    pd.DataFrame(players).to_parquet(player_path, index=False)
    pd.DataFrame([_weekly_stat("p-conflict", "Correct Weekly Name")]).to_parquet(
        stats_path, index=False
    )
    archive = RawArchive(
        config.project_root,
        config.resolve(config.paths.raw_dir),
        config.resolve(config.paths.manifests),
    )
    _, manifest_path = archive.create_manifest(
        source="nflverse",
        acquisition_method="integration-test",
        acquired_at=acquired_at,
        raw_files=[player_path, stats_path],
        seasons=[2025],
    )
    return manifest_path


def _archive_ffc_capture(config: AppConfig) -> None:
    payload = {
        "status": "Success",
        "players": [
            {
                "player_id": "ffc-unique",
                "name": "Unique Receiver",
                "position": "WR",
                "team": "BUF",
                "rank": 1,
            },
            {
                "player_id": "ffc-suffix",
                "name": "Jose Nunez",
                "position": "RB",
                "team": "MIA",
                "rank": 2,
            },
            {
                "player_id": "ffc-defense",
                "name": "Buffalo Defense",
                "position": "DEF",
                "team": "BUF",
                "rank": 3,
            },
            {
                "player_id": "ffc-ambiguous",
                "name": "Chris Smith",
                "position": "WR",
                "team": "BUF",
                "rank": 4,
            },
        ],
    }
    archive = RawArchive(
        config.project_root,
        config.resolve(config.paths.raw_dir),
        config.resolve(config.paths.manifests),
    )
    raw_path, acquired_at = archive.write_bytes(
        "ffc_adp",
        "ffc_adp__ppr__12_team__2026__overall",
        ".json",
        (json.dumps(payload, sort_keys=True) + "\n").encode(),
        acquired_at=ACQUIRED_AT + timedelta(minutes=1),
    )
    archive.create_manifest(
        source="ffc",
        acquisition_method="integration-test",
        acquired_at=acquired_at,
        raw_files=[raw_path],
        seasons=[2026],
    )


def _scenario(config: AppConfig) -> Path:
    manifest_path = _archive_nflverse_capture(config)
    _archive_ffc_capture(config)
    loaded = load_nflverse_to_warehouse(config, manifest_path=manifest_path)
    assert loaded.committed
    return manifest_path


def _queue_rows(warehouse: Warehouse) -> list[tuple[Any, ...]]:
    with warehouse.connect(read_only=True) as connection:
        return connection.execute(
            "SELECT * FROM identity_review_queue ORDER BY review_id"
        ).fetchall()


def _decide_nflverse_conflict(worksheet_path: Path, override_path: Path) -> None:
    frame = pd.read_csv(worksheet_path, dtype="string", keep_default_na=False)
    selected = (frame["source"] == "nflverse") & (
        frame["source_player_id"] == "p-conflict"
    )
    assert int(selected.sum()) == 1
    frame.loc[selected, "resolution"] = "confirmed"
    frame.loc[selected, "player_id"] = "p-conflict"
    frame.loc[selected, "canonical_display_name"] = "Corrected Canonical Name"
    frame.loc[selected, "reviewed_at"] = REVIEWED_AT
    frame.loc[selected, "reviewer"] = "integration-test"
    frame.loc[selected, "notes"] = "Confirmed the stable GSIS ID after reviewing both names."
    frame.to_csv(override_path, index=False)


def _archive_platform_capture(
    config: AppConfig,
    source: str,
    rows: list[dict[str, Any]],
    *,
    acquired_at: datetime,
) -> None:
    archive = RawArchive(
        config.project_root,
        config.resolve(config.paths.raw_dir),
        config.resolve(config.paths.manifests),
    )
    if source == "sleeper":
        content = (json.dumps(rows, sort_keys=True) + "\n").encode()
        extension = ".json"
    else:
        content = pd.DataFrame(rows).to_csv(index=False).encode()
        extension = ".csv"
    raw_path, captured_at = archive.write_bytes(
        f"{source}_adp",
        f"{source}_adp__2026",
        extension,
        content,
        acquired_at=acquired_at,
    )
    archive.create_manifest(
        source=source,
        acquisition_method="integration-test",
        acquired_at=captured_at,
        raw_files=[raw_path],
        seasons=[2026],
    )


def _archive_ff_playerids(
    config: AppConfig,
    rows: list[dict[str, Any]],
    *,
    acquired_at: datetime,
) -> None:
    raw_dir = config.resolve(config.paths.raw_dir) / "nflverse"
    raw_dir.mkdir(parents=True, exist_ok=True)
    stamp = acquired_at.strftime("%Y%m%dT%H%M%S%fZ")
    raw_path = raw_dir / f"nflverse_ff_playerids__{stamp}.parquet"
    pd.DataFrame(rows).to_parquet(raw_path, index=False)
    archive = RawArchive(
        config.project_root,
        config.resolve(config.paths.raw_dir),
        config.resolve(config.paths.manifests),
    )
    archive.create_manifest(
        source="nflverse_ff_playerids",
        acquisition_method="integration-test",
        acquired_at=acquired_at,
        raw_files=[raw_path],
    )


def test_refresh_classifies_real_style_identity_evidence_idempotently(tmp_path: Path) -> None:
    config = _config(tmp_path)
    _scenario(config)

    first = refresh_identity_review_queue(config)

    assert first.committed
    assert first.total_current == 5
    assert first.pending == 4
    assert first.excluded == 1
    assert first.quality.identity_conflicts == 1
    assert first.quality.unresolved_players == 1
    assert first.quality.excluded_rows == 1
    assert first.output_path is not None and first.output_path.is_file()

    warehouse = Warehouse(config.resolve(config.paths.warehouse))
    with warehouse.connect(read_only=True) as connection:
        classified = {
            str(row[0]): row[1:]
            for row in connection.execute(
                "SELECT source_player_id, candidate_player_id, reason, "
                "mapping_confidence, status FROM identity_review_queue "
                "WHERE is_current ORDER BY source_player_id"
            ).fetchall()
        }

    assert classified["p-conflict"] == (
        "p-conflict",
        "stable_id_name_conflict",
        "high",
        "pending",
    )
    assert classified["ffc-unique"] == (
        "p-unique",
        "name_position_team_candidate",
        "high",
        "pending",
    )
    assert classified["ffc-suffix"] == (
        "p-suffix",
        "suffix_name_position_team_candidate",
        "medium",
        "pending",
    )
    assert classified["ffc-defense"] == (
        None,
        "unsupported_team_defense",
        "unresolved",
        "excluded",
    )
    assert classified["ffc-ambiguous"] == (
        None,
        "ambiguous_name_candidates",
        "unresolved",
        "pending",
    )

    before_repeat = _queue_rows(warehouse)
    second = refresh_identity_review_queue(config)
    after_repeat = _queue_rows(warehouse)

    assert second.committed
    assert second.total_current == first.total_current
    assert second.pending == first.pending
    assert before_repeat == after_repeat

    corrected_manifest = _archive_nflverse_capture(
        config,
        acquired_at=ACQUIRED_AT + timedelta(minutes=2),
        master_name="Correct Weekly Name",
    )
    assert load_nflverse_to_warehouse(config, manifest_path=corrected_manifest).committed
    without_conflict = refresh_identity_review_queue(config)
    assert without_conflict.total_current == 4
    with warehouse.connect(read_only=True) as connection:
        old_conflict = connection.execute(
            "SELECT is_current FROM identity_review_queue "
            "WHERE source = 'nflverse' AND source_player_id = 'p-conflict'"
        ).fetchone()
    assert old_conflict == (False,)


def test_confirmed_override_is_noop_on_repeat_and_survives_nflverse_reload(
    tmp_path: Path,
) -> None:
    config = _config(tmp_path)
    nflverse_manifest = _scenario(config)
    review = refresh_identity_review_queue(config)
    assert review.output_path is not None
    override_path = tmp_path / "reviewed_identity_overrides.csv"
    _decide_nflverse_conflict(review.output_path, override_path)
    override_hash = sha256_file(override_path)

    first = apply_identity_overrides(config, override_path)

    assert first.committed
    assert first.applied_rows == 1
    assert first.matched_existing_rows == 0
    assert first.raw_path is not None and first.raw_path.is_file()
    assert first.manifest is not None
    assert first.manifest.sha256 == [override_hash]
    assert sha256_file(first.raw_path) == override_hash
    assert sha256_file(override_path) == override_hash

    warehouse = Warehouse(config.resolve(config.paths.warehouse))
    with warehouse.connect(read_only=True) as connection:
        player = connection.execute(
            "SELECT display_name, mapping_confidence, mapping_source FROM players "
            "WHERE player_id = 'p-conflict'"
        ).fetchone()
        mapping = connection.execute(
            "SELECT player_id, mapping_confidence FROM player_source_mappings "
            "WHERE source = 'nflverse' AND source_player_id = 'p-conflict'"
        ).fetchone()
        queue = connection.execute(
            "SELECT status, resolution, resolved_player_id, "
            "canonical_display_name_override FROM identity_review_queue "
            "WHERE source = 'nflverse' AND source_player_id = 'p-conflict'"
        ).fetchone()

    assert player is not None
    assert player[0:2] == ("Corrected Canonical Name", "reviewed")
    assert str(player[2]).startswith("manual:identity-review:")
    assert mapping == ("p-conflict", "reviewed")
    assert queue == (
        "resolved",
        "confirmed",
        "p-conflict",
        "Corrected Canonical Name",
    )

    second = apply_identity_overrides(config, override_path)

    assert second.committed
    assert second.applied_rows == 0
    assert second.matched_existing_rows == 1
    assert second.raw_path == first.raw_path
    assert second.manifest_path == first.manifest_path
    assert sha256_file(override_path) == override_hash
    assert audit_project_data(config).passed

    reloaded = load_nflverse_to_warehouse(config, manifest_path=nflverse_manifest)
    assert reloaded.committed
    with warehouse.connect(read_only=True) as connection:
        preserved = connection.execute(
            "SELECT display_name, mapping_confidence, mapping_source FROM players "
            "WHERE player_id = 'p-conflict'"
        ).fetchone()
    assert preserved == player


def test_confirmed_ffc_mapping_populates_registry_and_resolves_future_reviews(
    tmp_path: Path,
) -> None:
    config = _config(tmp_path)
    _scenario(config)
    review = refresh_identity_review_queue(config)
    assert review.output_path is not None
    frame = pd.read_csv(review.output_path, dtype="string", keep_default_na=False)
    selected = frame["source_player_id"] == "ffc-unique"
    assert int(selected.sum()) == 1
    frame.loc[selected, "resolution"] = "confirmed"
    frame.loc[selected, "player_id"] = "p-unique"
    frame.loc[selected, "reviewed_at"] = REVIEWED_AT
    frame.loc[selected, "reviewer"] = "integration-test"
    frame.loc[selected, "notes"] = "Reviewed the unique candidate against position and team."
    override_path = tmp_path / "reviewed_ffc_mapping.csv"
    frame.to_csv(override_path, index=False)

    applied = apply_identity_overrides(config, override_path)
    refreshed = refresh_identity_review_queue(config)

    assert applied.committed
    assert applied.applied_rows == 1
    assert refreshed.resolved == 1
    warehouse = Warehouse(config.resolve(config.paths.warehouse))
    with warehouse.connect(read_only=True) as connection:
        mapping = connection.execute(
            "SELECT player_id, mapping_confidence, review_id "
            "FROM player_source_mappings "
            "WHERE source = 'ffc' AND source_player_id = 'ffc-unique'"
        ).fetchone()
        queue = connection.execute(
            "SELECT status, mapping_confidence, resolved_player_id "
            "FROM identity_review_queue "
            "WHERE source = 'ffc' AND source_player_id = 'ffc-unique'"
        ).fetchone()
        canonical_confidence = connection.execute(
            "SELECT mapping_confidence FROM players WHERE player_id = 'p-unique'"
        ).fetchone()
    assert mapping is not None
    assert mapping[0:2] == ("p-unique", "reviewed")
    assert queue == ("resolved", "reviewed", "p-unique")
    assert canonical_confidence == ("exact",)


def test_league_history_picks_require_review_and_apply_mapping_only(tmp_path: Path) -> None:
    config = _config(tmp_path)
    _scenario(config)
    warehouse = Warehouse(config.resolve(config.paths.warehouse))
    package_fingerprint = "a" * 64
    normalized_fingerprint = "b" * 64
    ruleset_fingerprint = "c" * 64
    history_dataset_id = "history-dataset"
    initial_quality_report = json.dumps(
        {
            "quality": {
                "source": "league_history",
                "row_count": 5,
                "required_field_failures": 0,
                "duplicate_keys": 0,
                "unresolved_players": 2,
                "excluded_rows": 0,
                "identity_conflicts": 0,
                "impossible_picks_or_rounds": 0,
                "unsupported_lineup_slots": 0,
                "invalid_json_settings": 0,
                "issues": [
                    {
                        "code": "unresolved_player_mappings",
                        "message": (
                            "Draft picks without a canonical/source-ID or reviewed mapping were "
                            "retained with player_id null; display names were not joined."
                        ),
                        "count": 2,
                        "severity": "warning",
                    }
                ],
            },
            "readiness": {
                "schema_version": "league-history-v1",
                "archived": True,
                "normalized": True,
                "league_count": 1,
                "draft_complete_leagues": 1,
                "outcomes_complete_leagues": 1,
                "analysis_ready_leagues": 0,
                "championship_model_status": "disabled",
                "reasons": [
                    (
                        "Championship modeling remains disabled until the separate "
                        "data-sufficiency gate passes."
                    ),
                    (
                        "No league has a complete draft, complete outcomes, and 100% resolved "
                        "draft picks."
                    ),
                ],
            },
        },
        sort_keys=True,
        separators=(",", ":"),
    )
    with warehouse.connect() as connection:
        connection.execute(
            """
            INSERT INTO league_rules (
                league_season_id, platform, season, team_count, user_draft_slot,
                draft_date, draft_type, rounds, starter_slots_json, flex_slots_json,
                bench_slots, ir_slots, scoring_json, playoff_settings_json,
                normalized_ruleset_json, ruleset_fingerprint, source_dataset_id,
                row_fingerprint, loaded_at
            ) VALUES (
                'league-a-2025', 'sleeper', 2025, 2, NULL, NULL, 'snake', 1,
                '{"QB":1}', '{}', 0, 0, '{}', '{}', '{}', ?, ?, ?, ?
            )
            """,
            [ruleset_fingerprint, history_dataset_id, "d" * 64, ACQUIRED_AT],
        )
        connection.executemany(
            """
            INSERT INTO draft_picks (
                league_season_id, overall_pick, round, draft_slot, team_id,
                player_id, player_name, position, source_platform, source_player_id,
                mapping_confidence, is_keeper, is_autopick, picked_at,
                adp_snapshot_id, source_dataset_id, row_fingerprint, loaded_at
            ) VALUES (?, ?, ?, ?, ?, NULL, ?, ?, ?, ?, 'unresolved', ?, ?, ?, ?, ?, ?, ?)
            """,
            [
                (
                    "league-a-2025",
                    1,
                    1,
                    1,
                    "team-a",
                    "Unique Receiver",
                    "WR",
                    "Sleeper",
                    "sleeper-unique",
                    False,
                    False,
                    ACQUIRED_AT,
                    "adp-a",
                    history_dataset_id,
                    "e" * 64,
                    ACQUIRED_AT,
                ),
                (
                    "league-a-2025",
                    2,
                    1,
                    2,
                    "team-b",
                    "Unique Receiver",
                    "WR",
                    "sleeper",
                    "sleeper-unique",
                    True,
                    False,
                    ACQUIRED_AT + timedelta(minutes=5),
                    "adp-b",
                    history_dataset_id,
                    "f" * 64,
                    ACQUIRED_AT + timedelta(minutes=5),
                ),
            ],
        )
        connection.executemany(
            """
            INSERT INTO team_outcomes (
                league_season_id, team_id, wins, losses, ties, points_for,
                points_against, all_play_percentile, points_percentile, seed,
                made_playoffs, final_place, is_champion, draft_only_metrics,
                source_dataset_id, row_fingerprint, loaded_at
            ) VALUES ('league-a-2025', ?, ?, ?, 0, ?, ?, ?, ?, ?, ?, ?, ?, NULL, ?, ?, ?)
            """,
            [
                (
                    "team-a",
                    9,
                    5,
                    1400,
                    1300,
                    0.75,
                    0.75,
                    1,
                    True,
                    1,
                    True,
                    history_dataset_id,
                    "1" * 64,
                    ACQUIRED_AT,
                ),
                (
                    "team-b",
                    5,
                    9,
                    1300,
                    1400,
                    0.25,
                    0.25,
                    2,
                    False,
                    2,
                    False,
                    history_dataset_id,
                    "2" * 64,
                    ACQUIRED_AT,
                ),
            ],
        )
        connection.execute(
            """
            INSERT INTO league_history_imports (
                package_fingerprint, schema_version, manifest_dataset_id, raw_path,
                raw_sha256, normalized_fingerprint, status, league_count, rules_rows,
                pick_rows, outcome_rows, unresolved_player_rows, quality_report, imported_at
            ) VALUES (?, 'league-history-v1', ?, 'data/raw/test-history.zip', ?, ?,
                      'imported', 1, 1, 2, 2, 2, ?, ?)
            """,
            [
                package_fingerprint,
                history_dataset_id,
                package_fingerprint,
                normalized_fingerprint,
                initial_quality_report,
                ACQUIRED_AT,
            ],
        )
        connection.execute(
            """
            INSERT INTO league_history_leagues VALUES (
                'league-a-2025', ?, 2025, 2, ?, 2, 2, 2, 0, TRUE, TRUE, FALSE
            )
            """,
            [package_fingerprint, ruleset_fingerprint],
        )
        draft_facts_before = connection.execute(
            """
            SELECT
                league_season_id, overall_pick, round, draft_slot, team_id,
                player_name, position, source_platform, source_player_id,
                is_keeper, is_autopick, picked_at, adp_snapshot_id,
                source_dataset_id, row_fingerprint, loaded_at
            FROM draft_picks
            ORDER BY league_season_id, overall_pick
            """
        ).fetchall()

    review = refresh_identity_review_queue(config)

    assert review.committed
    assert review.output_path is not None
    with warehouse.connect(read_only=True) as connection:
        historical_review = connection.execute(
            """
            SELECT
                candidate_player_id, mapping_confidence, status,
                evidence_dataset_id, evidence_json
            FROM identity_review_queue
            WHERE issue_type = 'league_history_source_mapping'
              AND source = 'sleeper'
              AND source_player_id = 'sleeper-unique'
              AND is_current
            """
        ).fetchone()
        unresolved_picks = connection.execute(
            "SELECT count(*) FROM draft_picks WHERE player_id IS NULL"
        ).fetchone()
    assert historical_review is not None
    assert historical_review[0:3] == ("p-unique", "high", "pending")
    assert historical_review[3] == history_dataset_id
    evidence = json.loads(str(historical_review[4]))
    assert evidence["unresolved_pick_count"] == 2
    assert evidence["source_dataset_ids"] == [history_dataset_id]
    assert unresolved_picks == (2,)

    frame = pd.read_csv(review.output_path, dtype="string", keep_default_na=False)
    selected = (frame["source"] == "sleeper") & (
        frame["source_player_id"] == "sleeper-unique"
    )
    assert int(selected.sum()) == 1
    frame = frame.loc[selected].copy()
    frame.loc[:, "resolution"] = "confirmed"
    frame.loc[:, "player_id"] = "p-unique"
    frame.loc[:, "reviewed_at"] = REVIEWED_AT
    frame.loc[:, "reviewer"] = "integration-test"
    frame.loc[:, "notes"] = "Confirmed against the source platform player identifier."
    override_path = tmp_path / "reviewed_history_mapping.csv"
    frame.to_csv(override_path, index=False)

    first = apply_identity_overrides(config, override_path)

    assert first.committed and first.applied_rows == 1
    with warehouse.connect(read_only=True) as connection:
        metadata_after_first = connection.execute(
            """
            SELECT unresolved_player_rows, quality_report
            FROM league_history_imports WHERE package_fingerprint = ?
            """,
            [package_fingerprint],
        ).fetchone()
    second = apply_identity_overrides(config, override_path)

    assert second.committed and second.applied_rows == 0
    assert second.matched_existing_rows == 1
    with warehouse.connect(read_only=True) as connection:
        mapped_picks = connection.execute(
            """
            SELECT player_id, mapping_confidence
            FROM draft_picks
            ORDER BY league_season_id, overall_pick
            """
        ).fetchall()
        draft_facts_after = connection.execute(
            """
            SELECT
                league_season_id, overall_pick, round, draft_slot, team_id,
                player_name, position, source_platform, source_player_id,
                is_keeper, is_autopick, picked_at, adp_snapshot_id,
                source_dataset_id, row_fingerprint, loaded_at
            FROM draft_picks
            ORDER BY league_season_id, overall_pick
            """
        ).fetchall()
        registry_mapping = connection.execute(
            """
            SELECT player_id, mapping_confidence, mapping_source
            FROM player_source_mappings
            WHERE source = 'sleeper' AND source_player_id = 'sleeper-unique'
            """
        ).fetchone()
        league_readiness = connection.execute(
            """
            SELECT resolved_pick_rows, actual_pick_rows, analysis_ready
            FROM league_history_leagues WHERE league_season_id = 'league-a-2025'
            """
        ).fetchone()
        metadata_after_second = connection.execute(
            """
            SELECT unresolved_player_rows, quality_report
            FROM league_history_imports WHERE package_fingerprint = ?
            """,
            [package_fingerprint],
        ).fetchone()
    assert mapped_picks == [("p-unique", "reviewed"), ("p-unique", "reviewed")]
    assert draft_facts_after == draft_facts_before
    assert registry_mapping is not None
    assert registry_mapping[0:2] == ("p-unique", "reviewed")
    assert str(registry_mapping[2]).startswith("manual:identity-review:")
    assert league_readiness == (2, 2, True)
    assert metadata_after_first == metadata_after_second
    assert metadata_after_second is not None and metadata_after_second[0] == 0
    stored_report = json.loads(str(metadata_after_second[1]))
    assert stored_report["quality"]["unresolved_players"] == 0
    assert not any(
        issue["code"] == "unresolved_player_mappings"
        for issue in stored_report["quality"]["issues"]
    )
    assert stored_report["readiness"]["analysis_ready_leagues"] == 1
    assert stored_report["readiness"]["reasons"] == [
        "Championship modeling remains disabled until the separate data-sufficiency gate passes."
    ]
    assert audit_project_data(config).passed

    refreshed = refresh_identity_review_queue(config)
    assert refreshed.committed
    with warehouse.connect(read_only=True) as connection:
        retired = connection.execute(
            """
            SELECT is_current FROM identity_review_queue
            WHERE issue_type = 'league_history_source_mapping'
              AND source = 'sleeper'
              AND source_player_id = 'sleeper-unique'
            """
        ).fetchone()
    assert retired == (False,)


def test_unknown_player_and_duplicate_override_rows_write_nothing(tmp_path: Path) -> None:
    config = _config(tmp_path)
    _scenario(config)
    review = refresh_identity_review_queue(config)
    assert review.output_path is not None
    warehouse = Warehouse(config.resolve(config.paths.warehouse))
    before_queue = _queue_rows(warehouse)

    frame = pd.read_csv(review.output_path, dtype="string", keep_default_na=False)
    row = frame.loc[frame["source_player_id"] == "ffc-unique"].copy()
    assert len(row) == 1
    row.loc[:, "resolution"] = "confirmed"
    row.loc[:, "player_id"] = "missing-canonical-player"
    row.loc[:, "reviewed_at"] = REVIEWED_AT
    row.loc[:, "reviewer"] = "integration-test"
    invalid = pd.concat([row, row], ignore_index=True)
    invalid_path = tmp_path / "invalid_duplicate_overrides.csv"
    invalid.to_csv(invalid_path, index=False)
    invalid_hash = sha256_file(invalid_path)

    result = apply_identity_overrides(config, invalid_path)

    assert not result.committed
    assert result.quality.has_fatal_errors
    assert result.quality.duplicate_keys == 2
    assert any(issue.code == "unknown_override_player" for issue in result.quality.issues)
    assert result.raw_path is None
    assert sha256_file(invalid_path) == invalid_hash
    assert _queue_rows(warehouse) == before_queue
    with warehouse.connect(read_only=True) as connection:
        mapping_count = connection.execute(
            "SELECT count(*) FROM player_source_mappings"
        ).fetchone()
    assert mapping_count == (0,)
    manifest_dir = config.resolve(config.paths.manifests)
    override_manifests = [
        path
        for path in manifest_dir.glob("*.json")
        if json.loads(path.read_text(encoding="utf-8"))["source"] == "identity_overrides"
    ]
    assert override_manifests == []


def test_stale_and_excluded_reviews_cannot_be_mapped(tmp_path: Path) -> None:
    config = _config(tmp_path)
    _scenario(config)
    review = refresh_identity_review_queue(config)
    assert review.output_path is not None
    original = pd.read_csv(review.output_path, dtype="string", keep_default_na=False)

    defense = original.loc[original["source_player_id"] == "ffc-defense"].copy()
    assert len(defense) == 1
    defense.loc[:, "resolution"] = "remapped"
    defense.loc[:, "player_id"] = "p-unique"
    defense.loc[:, "reviewed_at"] = REVIEWED_AT
    defense.loc[:, "reviewer"] = "integration-test"
    defense.loc[:, "notes"] = "This deliberately invalid decision must be rejected."
    defense_path = tmp_path / "invalid_defense_override.csv"
    defense.to_csv(defense_path, index=False)

    excluded_result = apply_identity_overrides(config, defense_path)

    assert not excluded_result.committed
    assert any(
        issue.code == "excluded_identity_review" for issue in excluded_result.quality.issues
    )

    corrected_manifest = _archive_nflverse_capture(
        config,
        acquired_at=ACQUIRED_AT + timedelta(minutes=2),
        master_name="Correct Weekly Name",
    )
    assert load_nflverse_to_warehouse(config, manifest_path=corrected_manifest).committed
    assert refresh_identity_review_queue(config).committed
    stale = original.loc[original["source_player_id"] == "p-conflict"].copy()
    assert len(stale) == 1
    stale.loc[:, "resolution"] = "confirmed"
    stale.loc[:, "player_id"] = "p-conflict"
    stale.loc[:, "reviewed_at"] = REVIEWED_AT
    stale.loc[:, "reviewer"] = "integration-test"
    stale.loc[:, "notes"] = "This stale decision must be rejected."
    stale_path = tmp_path / "stale_identity_override.csv"
    stale.to_csv(stale_path, index=False)

    stale_result = apply_identity_overrides(config, stale_path)

    assert not stale_result.committed
    assert any(issue.code == "stale_identity_review" for issue in stale_result.quality.issues)
    warehouse = Warehouse(config.resolve(config.paths.warehouse))
    with warehouse.connect(read_only=True) as connection:
        mapping_count = connection.execute(
            "SELECT count(*) FROM player_source_mappings"
        ).fetchone()
    assert mapping_count == (0,)


def test_platform_captures_use_exact_ids_and_reviews_update_historical_adp(
    tmp_path: Path,
) -> None:
    config = _config(tmp_path)
    _scenario(config)
    _archive_ff_playerids(
        config,
        [
            {
                "gsis_id": "p-unique",
                "espn_id": "espn-p-unique",
                "sleeper_id": "sleeper-exact",
                "yahoo_id": "yahoo-exact",
            },
            {
                "gsis_id": "p-suffix",
                "espn_id": "espn-p-suffix",
                "sleeper_id": None,
                "yahoo_id": None,
            },
            {
                "gsis_id": "p-unique",
                "espn_id": "2582138",
                "sleeper_id": None,
                "yahoo_id": None,
            },
            {
                "gsis_id": "p-suffix",
                "espn_id": "2582138",
                "sleeper_id": None,
                "yahoo_id": None,
            },
        ],
        acquired_at=ACQUIRED_AT + timedelta(minutes=2),
    )
    _archive_platform_capture(
        config,
        "sleeper",
        [
            {
                "player_id": "sleeper-exact",
                "player": {
                    "first_name": "Wrong",
                    "last_name": "Display Name",
                    "position": "WR",
                    "team": "BUF",
                },
                "stats": {"adp_ppr": 10.5},
            },
            {
                "player_id": "sleeper-review",
                "player": {
                    "first_name": "Jose",
                    "last_name": "Nunez",
                    "position": "RB",
                    "team": "MIA",
                },
                "stats": {"adp_ppr": 28.0},
            },
        ],
        acquired_at=ACQUIRED_AT + timedelta(minutes=3),
    )
    common = {
        "captured_at": "2026-08-05T13:24:34Z",
        "season": 2026,
        "scoring_format": "ppr",
        "team_count": 12,
        "position": "WR",
        "nfl_team": "BUF",
        "average_pick": 12.5,
        "rank": 12,
    }
    _archive_platform_capture(
        config,
        "espn",
        [
            {
                **common,
                "source": "espn",
                "source_player_id": "espn-p-unique",
                "player_name": "Unique Receiver",
            }
        ],
        acquired_at=ACQUIRED_AT + timedelta(minutes=4),
    )
    _archive_platform_capture(
        config,
        "yahoo",
        [
            {
                **common,
                "source": "yahoo",
                "source_player_id": "yahoo-exact",
                "player_name": "Unique Receiver",
            }
        ],
        acquired_at=ACQUIRED_AT + timedelta(minutes=5),
    )
    _archive_platform_capture(
        config,
        "underdog",
        [
            {
                **common,
                "source": "underdog",
                "source_player_id": "underdog-review",
                "player_name": "Unique Receiver",
            }
        ],
        acquired_at=ACQUIRED_AT + timedelta(minutes=6),
    )
    warehouse = Warehouse(config.resolve(config.paths.warehouse))
    with warehouse.connect() as connection:
        connection.executemany(
            """
            INSERT INTO adp_snapshots (
                snapshot_id, source, captured_at, season, scoring_format, team_count,
                player_id, player_name, position, nfl_team, average_pick, rank,
                raw_source_row_id, mapping_confidence
            ) VALUES (?, 'sleeper', ?, 2026, 'ppr', 12, NULL, 'Jose Nunez', 'RB',
                      'MIA', 28.0, 28, 'sleeper-review', 'unresolved')
            """,
            [
                ("sleeper-history-a", ACQUIRED_AT),
                ("sleeper-history-b", ACQUIRED_AT + timedelta(minutes=1)),
            ],
        )

    review = refresh_identity_review_queue(config)

    assert review.committed
    with warehouse.connect(read_only=True) as connection:
        platform_rows = {
            (str(row[0]), str(row[1])): row[2:]
            for row in connection.execute(
                """
                SELECT source, source_player_id, candidate_player_id,
                       mapping_confidence, status, reason
                FROM identity_review_queue
                WHERE source IN ('espn', 'sleeper', 'yahoo', 'underdog') AND is_current
                ORDER BY source, source_player_id
                """
            ).fetchall()
        }
    assert platform_rows[("espn", "espn-p-unique")] == (
        "p-unique",
        "exact",
        "resolved",
        "exact_platform_id",
    )
    assert platform_rows[("sleeper", "sleeper-exact")] == (
        "p-unique",
        "exact",
        "resolved",
        "exact_platform_id",
    )
    assert platform_rows[("yahoo", "yahoo-exact")] == (
        "p-unique",
        "exact",
        "resolved",
        "exact_platform_id",
    )
    assert platform_rows[("sleeper", "sleeper-review")] == (
        "p-suffix",
        "medium",
        "pending",
        "suffix_name_position_team_candidate",
    )
    assert platform_rows[("underdog", "underdog-review")][0:3] == (
        "p-unique",
        "high",
        "pending",
    )

    assert review.output_path is not None
    frame = pd.read_csv(review.output_path, dtype="string", keep_default_na=False)
    selected = (frame["source"] == "sleeper") & (
        frame["source_player_id"] == "sleeper-review"
    )
    frame = frame.loc[selected].copy()
    frame.loc[:, "resolution"] = "confirmed"
    frame.loc[:, "player_id"] = "p-suffix"
    frame.loc[:, "reviewed_at"] = REVIEWED_AT
    frame.loc[:, "reviewer"] = "integration-test"
    frame.loc[:, "notes"] = "Confirmed against the platform profile."
    override_path = tmp_path / "reviewed_sleeper_mapping.csv"
    frame.to_csv(override_path, index=False)

    applied = apply_identity_overrides(config, override_path)

    assert applied.committed and applied.applied_rows == 1
    with warehouse.connect(read_only=True) as connection:
        historical_rows = connection.execute(
            """
            SELECT snapshot_id, player_id, mapping_confidence
            FROM adp_snapshots
            WHERE source = 'sleeper' AND raw_source_row_id = 'sleeper-review'
            ORDER BY snapshot_id
            """
        ).fetchall()
        sleeper_id = connection.execute(
            "SELECT sleeper_id FROM players WHERE player_id = 'p-suffix'"
        ).fetchone()
    assert historical_rows == [
        ("sleeper-history-a", "p-suffix", "reviewed"),
        ("sleeper-history-b", "p-suffix", "reviewed"),
    ]
    assert sleeper_id == ("sleeper-review",)


def test_crosswalk_platform_id_collision_fails_closed(tmp_path: Path) -> None:
    config = _config(tmp_path)
    _scenario(config)
    _archive_ff_playerids(
        config,
        [
            {
                "gsis_id": "p-unique",
                "espn_id": "espn-p-unique",
                "sleeper_id": "shared-sleeper-id",
                "yahoo_id": None,
            },
            {
                "gsis_id": "p-suffix",
                "espn_id": "espn-p-suffix",
                "sleeper_id": "shared-sleeper-id",
                "yahoo_id": None,
            },
        ],
        acquired_at=ACQUIRED_AT + timedelta(minutes=2),
    )
    _archive_platform_capture(
        config,
        "sleeper",
        [
            {
                "player_id": "shared-sleeper-id",
                "player": {
                    "first_name": "Unique",
                    "last_name": "Receiver",
                    "position": "WR",
                    "team": "BUF",
                },
                "stats": {"adp_ppr": 10.0},
            }
        ],
        acquired_at=ACQUIRED_AT + timedelta(minutes=3),
    )

    result = refresh_identity_review_queue(config)

    assert not result.committed
    assert result.quality.has_fatal_errors
    assert any(
        issue.code == "platform_identity_collision" for issue in result.quality.issues
    )
    warehouse = Warehouse(config.resolve(config.paths.warehouse))
    with warehouse.connect(read_only=True) as connection:
        queue_count = connection.execute("SELECT count(*) FROM identity_review_queue").fetchone()
    assert queue_count == (0,)
