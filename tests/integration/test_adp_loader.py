from __future__ import annotations

import json
from datetime import UTC, datetime, timedelta
from pathlib import Path

import duckdb
import pytest

from fantasy_draft_ai.config import (
    AppConfig,
    NetworkSection,
    PathSection,
    ProjectSection,
    TrainingSection,
)
from fantasy_draft_ai.data.adp_loader import load_adp_to_warehouse
from fantasy_draft_ai.data.manifests import RawArchive, SourceManifest
from fantasy_draft_ai.data.warehouse import Warehouse

CAPTURED_AT = datetime(2026, 8, 4, 21, 3, 26, tzinfo=UTC)


def _config(project_root: Path) -> AppConfig:
    return AppConfig(
        project=ProjectSection(name="ADP loader test", prediction_season=2026),
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


def _archive(config: AppConfig) -> RawArchive:
    return RawArchive(
        project_root=config.project_root,
        raw_root=config.resolve(config.paths.raw_dir),
        manifest_root=config.resolve(config.paths.manifests),
    )


def _archive_ffc(
    config: AppConfig,
    *,
    acquired_at: datetime = CAPTURED_AT,
    average_pick: float = 4.5,
    duplicate_manifest: bool = False,
) -> tuple[Path, tuple[Path, ...]]:
    payload = {
        "players": [
            {
                "player_id": 101,
                "name": "Mapped Runner",
                "position": "RB",
                "team": "BUF",
                "adp": average_pick,
                "high": 2,
                "low": 8,
                "stdev": 1.5,
                "times_drafted": 200,
            },
            {
                "player_id": 202,
                "name": "Same Name As Canonical",
                "position": "DEF",
                "team": "NYJ",
                "adp": 180.0,
                "high": 160,
                "low": 200,
                "stdev": 8.0,
                "times_drafted": 20,
            },
        ]
    }
    archive = _archive(config)
    raw_path, moment = archive.write_bytes(
        "ffc_adp",
        "ffc_adp__ppr__12_team__2026__overall",
        ".json",
        (json.dumps(payload) + "\n").encode(),
        acquired_at=acquired_at,
    )
    _, first_manifest = archive.create_manifest(
        source="ffc",
        acquisition_method="test-api",
        acquired_at=moment,
        raw_files=[raw_path],
        seasons=[2026],
    )
    manifests = [first_manifest]
    if duplicate_manifest:
        _, duplicate = archive.create_manifest(
            source="ffc",
            acquisition_method="offline-cache",
            acquired_at=moment,
            raw_files=[raw_path],
            seasons=[2026],
        )
        manifests.append(duplicate)
    return raw_path, tuple(manifests)


def _archive_espn(config: AppConfig) -> Path:
    csv_text = "\n".join(
        [
            "captured_at,season,source,scoring_format,team_count,player_name,position,"
            "nfl_team,espn_player_id,rank,average_pick,median_pick,min_pick,max_pick,"
            "seven_day_change,sample_size",
            "2026-08-04T18:15:00Z,2026,espn,ppr,12,Mapped Receiver,WR,BUF,303,1,1.5,1,1,4,-0.2,100",
            "2026-08-04T18:15:00Z,2026,espn,ppr,12,Fixture Receiver,WR,BUF,999,2,2.5,2,1,5,-0.1,50",
            "",
        ]
    )
    archive = _archive(config)
    raw_path, moment = archive.write_bytes(
        "espn_manual",
        "espn_adp__manual__2026",
        ".csv",
        csv_text.encode(),
        acquired_at=CAPTURED_AT,
    )
    _, manifest_path = archive.create_manifest(
        source="espn",
        acquisition_method="manual-csv-upload",
        acquired_at=moment,
        raw_files=[raw_path],
        seasons=[2026],
    )
    return manifest_path


def _reviewed_mappings(config: AppConfig) -> None:
    warehouse = Warehouse(config.resolve(config.paths.warehouse))
    warehouse.initialize()
    with warehouse.connect() as connection:
        connection.executemany(
            """
            INSERT INTO players (
                player_id, display_name, mapping_confidence, mapping_source
            ) VALUES (?, ?, 'exact', 'test')
            """,
            [
                ("canonical-rb", "Mapped Runner"),
                ("canonical-wr", "Mapped Receiver"),
                ("canonical-same-name", "Same Name As Canonical"),
            ],
        )
        connection.executemany(
            """
            INSERT INTO player_source_mappings (
                source, source_player_id, player_id, mapping_confidence,
                mapping_source, review_id, reviewed_at, reviewer, notes,
                source_dataset_id
            ) VALUES (?, ?, ?, 'reviewed', 'manual:test', ?, ?, 'tester', NULL, 'review')
            """,
            [
                ("ffc", "101", "canonical-rb", "review-ffc", CAPTURED_AT),
                ("espn", "303", "canonical-wr", "review-espn", CAPTURED_AT),
            ],
        )


def _archive_crosswalk(config: AppConfig) -> Path:
    archive = _archive(config)
    raw_path, moment = archive.new_path(
        "nflverse",
        "nflverse_ff_playerids",
        ".parquet",
        acquired_at=CAPTURED_AT,
    )
    with duckdb.connect() as connection:
        connection.execute(
            """
            CREATE TABLE crosswalk (
                gsis_id VARCHAR,
                espn_id VARCHAR,
                sleeper_id VARCHAR,
                yahoo_id VARCHAR
            )
            """
        )
        connection.execute(
            "INSERT INTO crosswalk VALUES ('gsis-crosswalk', NULL, 'sleeper-crosswalk', NULL)"
        )
        escaped_path = str(raw_path).replace("'", "''")
        connection.execute(f"COPY crosswalk TO '{escaped_path}' (FORMAT PARQUET)")
    _, manifest_path = archive.create_manifest(
        source="nflverse_ff_playerids",
        acquisition_method="test-crosswalk",
        acquired_at=moment,
        raw_files=[raw_path],
    )
    return manifest_path


def _sleeper_payload() -> list[dict[str, object]]:
    rows: list[dict[str, object]] = [
        {
            "player_id": "sleeper-direct",
            "player": {
                "full_name": "Direct Runner",
                "position": "RB",
                "team": "BUF",
            },
            "stats": {"adp_ppr": 1.0},
        },
        {
            "player_id": "sleeper-crosswalk",
            "player": {
                "full_name": "Crosswalk Receiver",
                "position": "WR",
                "team": "NYJ",
            },
            "stats": {"adp_ppr": 2.0},
        },
        {
            "player_id": "sleeper-composite",
            "player": {
                "full_name": "Dandre Swift",
                "position": "RB",
                "team": "Chicago Bears",
            },
            "stats": {"adp_ppr": 3.0},
        },
        {
            "player_id": "sleeper-ambiguous",
            "player": {"full_name": "Chris Smith", "position": "WR", "team": "BUF"},
            "stats": {"adp_ppr": 4.0},
        },
        {
            "player_id": "sleeper-team-mismatch",
            "player": {"full_name": "Team Mismatch", "position": "TE", "team": "BUF"},
            "stats": {"adp_ppr": 5.0},
        },
        {
            "player_id": "sleeper-inactive",
            "player": {"full_name": "Inactive Quarterback", "position": "QB", "team": "MIA"},
            "stats": {"adp_ppr": 6.0},
        },
    ]
    positions = ("QB", "RB", "WR", "TE")
    rows.extend(
        {
            "player_id": f"sleeper-unmatched-{index}",
            "player": {
                "full_name": f"Unmatched Player {index}",
                "position": positions[index % len(positions)],
                "team": "DAL",
            },
            "stats": {"adp_ppr": float(index + 1)},
        }
        for index in range(6, 100)
    )
    return rows


def _archive_sleeper(config: AppConfig, *, season: int = 2027) -> Path:
    archive = _archive(config)
    raw_path, moment = archive.write_bytes(
        "sleeper_adp",
        f"sleeper_adp__ppr__12_team__{season}__overall",
        ".json",
        (json.dumps(_sleeper_payload()) + "\n").encode(),
        acquired_at=CAPTURED_AT,
    )
    _, manifest_path = archive.create_manifest(
        source="sleeper",
        acquisition_method="test-api",
        acquired_at=moment,
        raw_files=[raw_path],
        seasons=[season],
    )
    return manifest_path


def _insert_platform_identities(config: AppConfig) -> None:
    warehouse = Warehouse(config.resolve(config.paths.warehouse))
    warehouse.initialize()
    with warehouse.connect() as connection:
        connection.executemany(
            """
            INSERT INTO players (
                player_id, gsis_id, espn_id, sleeper_id, yahoo_id, display_name,
                canonical_position, nfl_team, is_active, mapping_confidence,
                mapping_source
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, 'exact', 'test')
            """,
            [
                (
                    "canonical-direct",
                    "gsis-direct",
                    "espn-direct",
                    "sleeper-direct",
                    "yahoo-direct",
                    "Direct Runner",
                    "RB",
                    "BUF",
                    True,
                ),
                (
                    "canonical-crosswalk",
                    "gsis-crosswalk",
                    None,
                    None,
                    None,
                    "Crosswalk Receiver",
                    "WR",
                    "NYJ",
                    True,
                ),
                (
                    "canonical-composite",
                    "gsis-composite",
                    None,
                    None,
                    None,
                    "D'Andre Swift Jr.",
                    "RB",
                    "CHI",
                    True,
                ),
                (
                    "canonical-ambiguous-a",
                    "gsis-ambiguous-a",
                    None,
                    None,
                    None,
                    "Chris Smith",
                    "WR",
                    "BUF",
                    True,
                ),
                (
                    "canonical-ambiguous-b",
                    "gsis-ambiguous-b",
                    None,
                    None,
                    None,
                    "Chris Smith Jr.",
                    "WR",
                    "BUF",
                    True,
                ),
                (
                    "canonical-team-mismatch",
                    "gsis-team-mismatch",
                    None,
                    None,
                    None,
                    "Team Mismatch",
                    "TE",
                    "NYJ",
                    True,
                ),
                (
                    "canonical-inactive",
                    "gsis-inactive",
                    None,
                    None,
                    None,
                    "Inactive Quarterback",
                    "QB",
                    "MIA",
                    False,
                ),
            ],
        )


def _archive_generic_platform(
    config: AppConfig,
    source: str,
    *,
    acquired_at: datetime = CAPTURED_AT,
) -> Path:
    csv_text = "\n".join(
        [
            "captured_at,season,source,scoring_format,team_count,source_player_id,"
            "player_name,position,nfl_team,average_pick,rank",
            f"2026-08-24T19:30:00Z,2026,{source},Half-PPR,12,{source}-direct,"
            "Direct Runner,RB,Buffalo Bills,1.5,1",
            f"2026-08-24T19:30:00Z,2026,{source},Half-PPR,12,{source}-composite,"
            "Dandre Swift,RB,Chicago Bears,2.5,2",
            f"2026-08-24T19:30:00Z,2026,{source},Half-PPR,12,{source}-ambiguous,"
            "Chris Smith,WR,Buffalo Bills,3.5,3",
            "",
        ]
    )
    archive = _archive(config)
    raw_path, moment = archive.write_bytes(
        f"{source}_adp",
        f"{source}_adp__manual__2026",
        ".csv",
        csv_text.encode(),
        acquired_at=acquired_at,
    )
    _, manifest_path = archive.create_manifest(
        source=source,
        acquisition_method="manual-official-export",
        acquired_at=moment,
        raw_files=[raw_path],
        seasons=[2026],
    )
    return manifest_path


def test_adp_load_is_provenance_bound_idempotent_and_mapping_safe(tmp_path: Path) -> None:
    config = _config(tmp_path)
    _, ffc_manifests = _archive_ffc(config, duplicate_manifest=True)
    espn_manifest = _archive_espn(config)
    _reviewed_mappings(config)

    paths = (*ffc_manifests, espn_manifest)
    first = load_adp_to_warehouse(config, manifest_paths=paths)
    second = load_adp_to_warehouse(config, manifest_paths=tuple(reversed(paths)))

    assert first.committed
    assert first.quality.row_count == 4
    assert first.skipped_synthetic_rows == 1
    assert first.quality.excluded_rows == 1
    assert len(first.snapshots) == 2
    assert first.inserted_rows == 3
    assert first.unresolved_players == 1
    assert second.inserted_rows == 0
    assert second.matched_existing_rows == 3
    assert [item.snapshot_id for item in first.snapshots] == [
        item.snapshot_id for item in second.snapshots
    ]

    warehouse = Warehouse(config.resolve(config.paths.warehouse))
    with warehouse.connect(read_only=True) as connection:
        counts = connection.execute(
            "SELECT (SELECT count(*) FROM adp_snapshot_metadata), "
            "(SELECT count(*) FROM adp_snapshots)"
        ).fetchone()
        assert counts == (2, 3)
        ffc_metadata = connection.execute(
            "SELECT source_dataset_ids, row_count FROM adp_snapshot_metadata WHERE source = 'ffc'"
        ).fetchone()
        assert ffc_metadata is not None
        assert len(json.loads(str(ffc_metadata[0]))) == 2
        assert ffc_metadata[1] == 2
        observations = connection.execute(
            """
            SELECT source, raw_source_row_id, player_id, mapping_confidence,
                   source_stddev, source_movement_horizon
            FROM adp_snapshots
            ORDER BY source, raw_source_row_id
            """
        ).fetchall()
    assert observations == [
        ("espn", "303", "canonical-wr", "reviewed", None, "7_day"),
        ("ffc", "101", "canonical-rb", "reviewed", 1.5, None),
        ("ffc", "202", None, "unresolved", 8.0, None),
    ]


def test_loading_an_older_capture_after_a_newer_one_preserves_both(tmp_path: Path) -> None:
    config = _config(tmp_path)
    _, old_manifests = _archive_ffc(config, acquired_at=CAPTURED_AT, average_pick=5.0)
    _, new_manifests = _archive_ffc(
        config,
        acquired_at=CAPTURED_AT + timedelta(days=1),
        average_pick=3.0,
    )

    newer = load_adp_to_warehouse(config, manifest_paths=new_manifests)
    older = load_adp_to_warehouse(config, manifest_paths=old_manifests)

    assert newer.inserted_rows == 2
    assert older.inserted_rows == 2
    warehouse = Warehouse(config.resolve(config.paths.warehouse))
    with warehouse.connect(read_only=True) as connection:
        rows = connection.execute(
            "SELECT captured_at, average_pick FROM adp_snapshots "
            "WHERE raw_source_row_id = '101' ORDER BY captured_at"
        ).fetchall()
    assert len(rows) == 2
    assert [row[1] for row in rows] == [5.0, 3.0]


def test_hash_mismatch_blocks_the_transaction_without_replacing_raw_data(
    tmp_path: Path,
) -> None:
    config = _config(tmp_path)
    raw_path, manifests = _archive_ffc(config)
    raw_path.write_text('{"players": []}\n', encoding="utf-8")

    result = load_adp_to_warehouse(config, manifest_paths=manifests)

    assert not result.committed
    assert result.quality.has_fatal_errors
    assert any(issue.code == "adp_raw_hash_mismatch" for issue in result.quality.issues)
    assert not config.resolve(config.paths.warehouse).exists()


def test_impossible_adp_values_block_the_transaction(tmp_path: Path) -> None:
    config = _config(tmp_path)
    _, manifests = _archive_ffc(config, average_pick=0.0)

    result = load_adp_to_warehouse(config, manifest_paths=manifests)

    assert not result.committed
    assert result.quality.has_fatal_errors
    assert result.quality.impossible_picks_or_rounds == 1
    assert any(issue.code == "invalid_adp_pick_values" for issue in result.quality.issues)
    assert not config.resolve(config.paths.warehouse).exists()


def test_sleeper_load_uses_exact_and_conservative_composite_identity_evidence(
    tmp_path: Path,
) -> None:
    config = _config(tmp_path)
    _insert_platform_identities(config)
    _archive_crosswalk(config)
    sleeper_manifest = _archive_sleeper(config, season=2027)

    first = load_adp_to_warehouse(config, manifest_paths=[sleeper_manifest])
    second = load_adp_to_warehouse(config, manifest_paths=[sleeper_manifest])

    assert first.committed
    assert first.quality.row_count == 100
    assert first.inserted_rows == 100
    assert first.unresolved_players == 97
    assert first.snapshots[0].season == 2027
    assert first.snapshots[0].scoring_format == "ppr"
    assert second.committed
    assert second.inserted_rows == 0
    assert second.matched_existing_rows == 100

    warehouse = Warehouse(config.resolve(config.paths.warehouse))
    with warehouse.connect(read_only=True) as connection:
        observations = connection.execute(
            """
            SELECT raw_source_row_id, player_id, mapping_confidence
            FROM adp_snapshots
            WHERE raw_source_row_id IN (
                'sleeper-direct', 'sleeper-crosswalk', 'sleeper-composite',
                'sleeper-ambiguous', 'sleeper-team-mismatch', 'sleeper-inactive'
            )
            ORDER BY raw_source_row_id
            """
        ).fetchall()
    assert observations == [
        ("sleeper-ambiguous", None, "unresolved"),
        ("sleeper-composite", "canonical-composite", "high"),
        ("sleeper-crosswalk", "canonical-crosswalk", "exact"),
        ("sleeper-direct", "canonical-direct", "exact"),
        ("sleeper-inactive", None, "unresolved"),
        ("sleeper-team-mismatch", None, "unresolved"),
    ]


@pytest.mark.parametrize(
    ("source", "direct_confidence"),
    [("espn", "exact"), ("yahoo", "exact"), ("underdog", "high")],
)
def test_generic_platform_csv_supports_each_source_and_normalizes_scope(
    tmp_path: Path,
    source: str,
    direct_confidence: str,
) -> None:
    config = _config(tmp_path)
    _insert_platform_identities(config)
    manifest_path = _archive_generic_platform(config, source)

    result = load_adp_to_warehouse(config, manifest_paths=[manifest_path])

    assert result.committed
    assert result.inserted_rows == 3
    assert result.unresolved_players == 1
    assert result.snapshots[0].source == source
    assert result.snapshots[0].scoring_format == "half_ppr"
    warehouse = Warehouse(config.resolve(config.paths.warehouse))
    with warehouse.connect(read_only=True) as connection:
        observations = connection.execute(
            """
            SELECT raw_source_row_id, player_id, mapping_confidence
            FROM adp_snapshots
            ORDER BY raw_source_row_id
            """
        ).fetchall()
    assert observations == [
        (f"{source}-ambiguous", None, "unresolved"),
        (f"{source}-composite", "canonical-composite", "high"),
        (f"{source}-direct", "canonical-direct", direct_confidence),
    ]


def test_full_load_collapses_identical_source_content_across_archived_paths(
    tmp_path: Path,
) -> None:
    config = _config(tmp_path)
    _insert_platform_identities(config)
    first_manifest_path = _archive_generic_platform(
        config,
        "underdog",
        acquired_at=CAPTURED_AT,
    )
    second_manifest_path = _archive_generic_platform(
        config,
        "underdog",
        acquired_at=CAPTURED_AT + timedelta(minutes=1),
    )
    first_manifest = SourceManifest.model_validate_json(
        first_manifest_path.read_text(encoding="utf-8")
    )
    second_manifest = SourceManifest.model_validate_json(
        second_manifest_path.read_text(encoding="utf-8")
    )

    first = load_adp_to_warehouse(config)
    second = load_adp_to_warehouse(config)

    assert first.committed
    assert not first.quality.has_fatal_errors
    assert first.quality.row_count == 3
    assert len(first.snapshots) == 1
    assert first.inserted_rows == 3
    assert second.committed
    assert len(second.snapshots) == 1
    assert second.inserted_rows == 0
    assert second.matched_existing_rows == 3
    assert not any(issue.code == "duplicate_adp_snapshot" for issue in first.quality.issues)

    warehouse = Warehouse(config.resolve(config.paths.warehouse))
    with warehouse.connect(read_only=True) as connection:
        metadata = connection.execute(
            "SELECT source_dataset_ids, raw_relative_path, row_count "
            "FROM adp_snapshot_metadata WHERE source = 'underdog'"
        ).fetchone()
        counts = connection.execute(
            "SELECT (SELECT count(*) FROM adp_snapshot_metadata), "
            "(SELECT count(*) FROM adp_snapshots)"
        ).fetchone()
    assert metadata is not None
    assert set(json.loads(str(metadata[0]))) == {
        first_manifest.dataset_id,
        second_manifest.dataset_id,
    }
    assert str(metadata[1]) == min(
        first_manifest.raw_files[0],
        second_manifest.raw_files[0],
    )
    assert metadata[2] == 3
    assert counts == (1, 3)


def test_conflicting_reviewed_and_exact_platform_ids_fail_closed(tmp_path: Path) -> None:
    config = _config(tmp_path)
    _insert_platform_identities(config)
    sleeper_manifest = _archive_sleeper(config, season=2026)
    warehouse = Warehouse(config.resolve(config.paths.warehouse))
    with warehouse.connect() as connection:
        connection.execute(
            """
            INSERT INTO player_source_mappings (
                source, source_player_id, player_id, mapping_confidence,
                mapping_source, review_id, reviewed_at, reviewer, notes,
                source_dataset_id
            ) VALUES (
                'sleeper', 'sleeper-direct', 'canonical-composite', 'reviewed',
                'manual:test', 'conflict-review', ?, 'tester', NULL, 'review'
            )
            """,
            [CAPTURED_AT],
        )

    result = load_adp_to_warehouse(config, manifest_paths=[sleeper_manifest])

    assert not result.committed
    assert result.quality.has_fatal_errors
    assert any(
        issue.code == "conflicting_reviewed_platform_identity"
        for issue in result.quality.issues
    )
    with warehouse.connect(read_only=True) as connection:
        counts = connection.execute(
            "SELECT (SELECT count(*) FROM adp_snapshot_metadata), "
            "(SELECT count(*) FROM adp_snapshots)"
        ).fetchone()
    assert counts == (0, 0)
