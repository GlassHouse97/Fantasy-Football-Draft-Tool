from __future__ import annotations

import csv
import io
import json
import zipfile
from pathlib import Path
from typing import Any

from fantasy_draft_ai.config import (
    AppConfig,
    NetworkSection,
    PathSection,
    ProjectSection,
    TrainingSection,
)
from fantasy_draft_ai.data.audit import audit_project_data
from fantasy_draft_ai.data.league_history_loader import import_league_history_package
from fantasy_draft_ai.data.manifests import sha256_file
from fantasy_draft_ai.data.warehouse import Warehouse
from fantasy_draft_ai.services.league_history import load_league_history_snapshot


def _config(project_root: Path) -> AppConfig:
    return AppConfig(
        project=ProjectSection(name="League history test", prediction_season=2026),
        paths=PathSection(
            data_dir=Path("data"),
            raw_dir=Path("data/raw"),
            processed_dir=Path("data/processed"),
            warehouse=Path("data/warehouse/test.duckdb"),
            manifests=Path("data/raw/manifests"),
        ),
        network=NetworkSection(timeout_seconds=5, user_agent="test"),
        training=TrainingSection(start_season=2024, end_season=2025),
        project_root=project_root,
    )


def _manifest() -> dict[str, Any]:
    return {
        "schema_version": "league-history-v1",
        "package_id": "league_alpha_2025_v1",
        "created_at": "2026-01-10T12:00:00Z",
        "source_platform": "espn_manual",
        "contains_personal_identifiers": False,
        "files": [
            {
                "kind": "league_rules",
                "path": "league_rules.csv",
                "required": True,
                "included": True,
            },
            {
                "kind": "draft_picks",
                "path": "draft_picks.csv",
                "required": True,
                "included": True,
            },
            {
                "kind": "team_outcomes",
                "path": "team_outcomes.csv",
                "required": True,
                "included": True,
            },
            {
                "kind": "weekly_rosters",
                "path": "weekly_rosters.csv",
                "required": False,
                "included": False,
            },
            {
                "kind": "matchups",
                "path": "matchups.csv",
                "required": False,
                "included": False,
            },
            {
                "kind": "transactions",
                "path": "transactions.csv",
                "required": False,
                "included": False,
            },
        ],
    }


def _csv_text(header: tuple[str, ...], rows: list[dict[str, object]]) -> str:
    stream = io.StringIO(newline="")
    writer = csv.DictWriter(stream, fieldnames=header, lineterminator="\n")
    writer.writeheader()
    writer.writerows(rows)
    return stream.getvalue()


RULE_HEADER = (
    "league_season_id",
    "platform",
    "season",
    "team_count",
    "draft_type",
    "draft_date",
    "rounds",
    "bench_slots",
    "ir_slots",
    "playoff_teams",
    "playoff_start_week",
    "championship_week",
    "scoring_json",
    "starter_slots_json",
)
PICK_HEADER = (
    "league_season_id",
    "overall_pick",
    "round",
    "draft_slot",
    "team_id",
    "player_name",
    "position",
    "source_player_id",
    "is_keeper",
    "is_autopick",
    "picked_at",
)
OUTCOME_HEADER = (
    "league_season_id",
    "team_id",
    "wins",
    "losses",
    "ties",
    "points_for",
    "points_against",
    "seed",
    "made_playoffs",
    "final_place",
    "is_champion",
)


def _package_files(
    *,
    source_ids: tuple[str, ...] = ("espn-1", "espn-2", "espn-3", "espn-4"),
    player_names: tuple[str, ...] = ("One", "Two", "Three", "Four"),
    nested_starters: bool = False,
) -> dict[str, str]:
    starter_payload: object = (
        {"starters": {"QB": 1}, "flex_slots": []} if nested_starters else {"QB": 1}
    )
    rules = [
        {
            "league_season_id": "league_alpha_2025",
            "platform": "espn_manual",
            "season": 2025,
            "team_count": 4,
            "draft_type": "snake",
            "draft_date": "2025-08-25T20:00:00Z",
            "rounds": 1,
            "bench_slots": 0,
            "ir_slots": 0,
            "playoff_teams": 2,
            "playoff_start_week": 15,
            "championship_week": 17,
            "scoring_json": json.dumps({"reception": 1}),
            "starter_slots_json": json.dumps(starter_payload),
        }
    ]
    picks = [
        {
            "league_season_id": "league_alpha_2025",
            "overall_pick": index,
            "round": 1,
            "draft_slot": index,
            "team_id": f"team_{index:02d}",
            "player_name": player_names[index - 1],
            "position": "QB",
            "source_player_id": source_ids[index - 1],
            "is_keeper": "false",
            "is_autopick": "false",
            "picked_at": f"2025-08-25T20:0{index}:00Z",
        }
        for index in range(1, 5)
    ]
    outcomes = [
        {
            "league_season_id": "league_alpha_2025",
            "team_id": f"team_{index:02d}",
            "wins": 12 - index,
            "losses": index + 1,
            "ties": 0,
            "points_for": 1500 - index * 50,
            "points_against": 1300 + index * 20,
            "seed": index,
            "made_playoffs": "true" if index <= 2 else "false",
            "final_place": index,
            "is_champion": "true" if index == 1 else "false",
        }
        for index in range(1, 5)
    ]
    return {
        "package.json": json.dumps(_manifest()),
        "league_rules.csv": _csv_text(RULE_HEADER, rules),
        "draft_picks.csv": _csv_text(PICK_HEADER, picks),
        "team_outcomes.csv": _csv_text(OUTCOME_HEADER, outcomes),
    }


def _write_package(path: Path, files: dict[str, str]) -> None:
    with zipfile.ZipFile(path, "w", compression=zipfile.ZIP_DEFLATED) as package:
        for name, content in files.items():
            package.writestr(name, content)


def _seed_players(config: AppConfig, *, reviewed_source_id: str | None = None) -> None:
    warehouse = Warehouse(config.resolve(config.paths.warehouse))
    warehouse.initialize()
    names = ("One", "Two", "Three", "Four")
    with warehouse.connect() as connection:
        for index in range(1, 5):
            connection.execute(
                """
                INSERT INTO players (
                    player_id, gsis_id, espn_id, display_name, canonical_position,
                    mapping_confidence, mapping_source
                ) VALUES (?, ?, ?, ?, 'QB', 'exact', 'test')
                """,
                [f"p{index}", f"g{index}", f"espn-{index}", names[index - 1]],
            )
        if reviewed_source_id is not None:
            connection.execute(
                """
                INSERT INTO player_source_mappings (
                    source, source_player_id, player_id, mapping_confidence, mapping_source,
                    review_id, reviewed_at, reviewer, notes, source_dataset_id
                ) VALUES (
                    'espn', ?, 'p1', 'reviewed', 'manual-review',
                    'review-1', '2026-01-01T00:00:00Z', 'tester', NULL, 'review-dataset'
                )
                """,
                [reviewed_source_id],
            )


def test_import_commits_provenance_and_reuses_identical_content(tmp_path: Path) -> None:
    config = _config(tmp_path)
    _seed_players(config)
    source = tmp_path / "league-history.zip"
    _write_package(source, _package_files())
    source_hash = sha256_file(source)

    first = import_league_history_package(config, source)
    second = import_league_history_package(config, source)

    assert first.committed
    assert first.status == "imported"
    assert not first.quality.has_fatal_errors
    assert first.readiness.analysis_ready_leagues == 1
    assert first.readiness.championship_model_status == "disabled"
    assert json.loads(json.dumps(first.as_dict()))["status"] == "imported"
    assert second.committed
    assert second.status == "already_loaded"
    assert second.idempotent_reuse
    assert source_hash == sha256_file(source)

    snapshot = load_league_history_snapshot(
        config,
        gate_path=Path("configs/league_history_gate.yaml").resolve(),
    )
    assert snapshot.available
    assert snapshot.coverage.loaded_packages == 1
    assert len(snapshot.teams) == 4

    warehouse = Warehouse(config.resolve(config.paths.warehouse))
    with warehouse.connect(read_only=True) as connection:
        counts = connection.execute(
            """
            SELECT
                (SELECT count(*) FROM league_history_imports),
                (SELECT count(*) FROM league_history_leagues),
                (SELECT count(*) FROM league_rules),
                (SELECT count(*) FROM draft_picks),
                (SELECT count(*) FROM team_outcomes)
            """
        ).fetchone()
        rule = connection.execute(
            """
            SELECT user_draft_slot, source_dataset_id, row_fingerprint
            FROM league_rules WHERE league_season_id = 'league_alpha_2025'
            """
        ).fetchone()
        readiness = connection.execute(
            """
            SELECT expected_pick_rows, actual_pick_rows, outcome_rows, resolved_pick_rows,
                   draft_complete, outcomes_complete, analysis_ready
            FROM league_history_leagues WHERE league_season_id = 'league_alpha_2025'
            """
        ).fetchone()
    assert counts == (1, 1, 1, 4, 4)
    assert rule is not None and rule[0] is None and rule[1] == first.manifest_dataset_id
    assert len(str(rule[2])) == 64
    assert readiness == (4, 4, 4, 4, True, True, True)


def test_unresolved_source_id_is_never_name_joined(tmp_path: Path) -> None:
    config = _config(tmp_path)
    _seed_players(config)
    source = tmp_path / "unresolved.zip"
    _write_package(
        source,
        _package_files(source_ids=("unknown", "espn-2", "espn-3", "espn-4")),
    )

    result = import_league_history_package(config, source)

    assert result.committed
    assert result.quality.unresolved_players == 1
    assert result.readiness.analysis_ready_leagues == 0
    warehouse = Warehouse(config.resolve(config.paths.warehouse))
    with warehouse.connect(read_only=True) as connection:
        first_pick = connection.execute(
            """
            SELECT player_id, player_name, source_player_id, mapping_confidence
            FROM draft_picks WHERE league_season_id = 'league_alpha_2025' AND overall_pick = 1
            """
        ).fetchone()
    assert first_pick == (None, "One", "unknown", "unresolved")


def test_platform_id_never_falls_through_to_canonical_namespace(tmp_path: Path) -> None:
    config = _config(tmp_path)
    _seed_players(config)
    source = tmp_path / "namespace-collision.zip"
    _write_package(
        source,
        _package_files(source_ids=("p1", "espn-2", "espn-3", "espn-4")),
    )

    result = import_league_history_package(config, source)

    assert result.committed
    assert result.quality.unresolved_players == 1
    warehouse = Warehouse(config.resolve(config.paths.warehouse))
    with warehouse.connect(read_only=True) as connection:
        first_pick = connection.execute(
            """
            SELECT player_id, source_platform, source_player_id, mapping_confidence
            FROM draft_picks WHERE league_season_id = 'league_alpha_2025' AND overall_pick = 1
            """
        ).fetchone()
    assert first_pick == (None, "espn", "p1", "unresolved")


def test_reviewed_source_mapping_is_used_without_name_join(tmp_path: Path) -> None:
    config = _config(tmp_path)
    _seed_players(config, reviewed_source_id="reviewed-external")
    warehouse = Warehouse(config.resolve(config.paths.warehouse))
    source = tmp_path / "reviewed.zip"
    _write_package(
        source,
        _package_files(
            source_ids=("reviewed-external", "espn-2", "espn-3", "espn-4"),
            player_names=("Not The Canonical Name", "Two", "Three", "Four"),
        ),
    )

    result = import_league_history_package(config, source)

    assert result.committed
    assert result.readiness.analysis_ready_leagues == 1
    with warehouse.connect(read_only=True) as connection:
        mapped = connection.execute(
            """
            SELECT player_id, player_name, mapping_confidence, source_platform FROM draft_picks
            WHERE league_season_id = 'league_alpha_2025' AND overall_pick = 1
            """
        ).fetchone()
    assert mapped == ("p1", "Not The Canonical Name", "reviewed", "espn")


def test_conflicting_source_facts_roll_back_without_overwrite(tmp_path: Path) -> None:
    config = _config(tmp_path)
    _seed_players(config)
    first_source = tmp_path / "first.zip"
    second_source = tmp_path / "corrected.zip"
    _write_package(first_source, _package_files())
    changed_names = ("Changed Name", "Two", "Three", "Four")
    _write_package(second_source, _package_files(player_names=changed_names))

    first = import_league_history_package(config, first_source)
    second = import_league_history_package(config, second_source)

    assert first.committed
    assert not second.committed
    assert second.status == "validation_failed"
    assert any(issue.code == "draft_pick_conflict" for issue in second.quality.issues)
    warehouse = Warehouse(config.resolve(config.paths.warehouse))
    with warehouse.connect(read_only=True) as connection:
        stored = connection.execute(
            "SELECT player_name FROM draft_picks WHERE league_season_id = ? AND overall_pick = 1",
            ["league_alpha_2025"],
        ).fetchone()
        import_statuses = connection.execute(
            "SELECT status FROM league_history_imports ORDER BY status"
        ).fetchall()
    assert stored == ("One",)
    assert import_statuses == [("imported",), ("rejected",)]


def test_flat_and_nested_starter_json_have_same_normalized_fingerprint(
    tmp_path: Path,
) -> None:
    config = _config(tmp_path)
    _seed_players(config)
    flat = tmp_path / "flat.zip"
    nested = tmp_path / "nested.zip"
    _write_package(flat, _package_files())
    _write_package(nested, _package_files(nested_starters=True))

    first = import_league_history_package(config, flat)
    second = import_league_history_package(config, nested)

    assert first.committed and second.committed
    assert second.status == "already_loaded"
    assert second.idempotent_reuse
    assert first.normalized_fingerprint == second.normalized_fingerprint
    warehouse = Warehouse(config.resolve(config.paths.warehouse))
    with warehouse.connect(read_only=True) as connection:
        assert connection.execute("SELECT count(*) FROM league_rules").fetchone() == (1,)
        assert connection.execute("SELECT count(*) FROM league_history_imports").fetchone() == (
            1,
        )
    audit = audit_project_data(config)
    assert audit.passed, audit.failures
