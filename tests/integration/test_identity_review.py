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
        "espn_id": f"espn-{player_id}",
        "birth_date": "2000-01-02",
        "position": position,
        "latest_team": team,
        "status": "ACT",
        "last_season": 2026,
        "years_of_experience": 3,
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
