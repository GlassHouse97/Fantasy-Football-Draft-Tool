from __future__ import annotations

import json
import stat
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
from fantasy_draft_ai.data.league_history_loader import import_league_history_package
from fantasy_draft_ai.data.warehouse import Warehouse


def _config(project_root: Path) -> AppConfig:
    return AppConfig(
        project=ProjectSection(name="League history unit test", prediction_season=2026),
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


def _manifest(*, contains_personal_identifiers: bool = False) -> dict[str, Any]:
    return {
        "schema_version": "league-history-v1",
        "package_id": "private_package_01",
        "created_at": "2026-01-10T12:00:00Z",
        "source_platform": "espn_manual",
        "contains_personal_identifiers": contains_personal_identifiers,
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


def _write_structural_package(
    path: Path,
    *,
    manifest: dict[str, Any] | None = None,
    extra_entries: tuple[tuple[str | zipfile.ZipInfo, str], ...] = (),
) -> None:
    with zipfile.ZipFile(path, "w", compression=zipfile.ZIP_DEFLATED) as package:
        package.writestr("package.json", json.dumps(manifest or _manifest()))
        package.writestr("league_rules.csv", "wrong_header\n")
        package.writestr("draft_picks.csv", "wrong_header\n")
        package.writestr("team_outcomes.csv", "wrong_header\n")
        for name, content in extra_entries:
            package.writestr(name, content)


def test_standalone_csv_is_preserved_as_archive_only(tmp_path: Path) -> None:
    config = _config(tmp_path)
    source = tmp_path / "history.csv"
    content = b"league_season_id,team_id\nleague_2025,team_01\n"
    source.write_bytes(content)

    result = import_league_history_package(config, source)

    assert result.status == "archive_only"
    assert not result.committed
    assert result.raw_path.read_bytes() == content
    assert result.manifest_path.is_file()
    assert not config.resolve(config.paths.warehouse).exists()
    assert "archive-only" in result.render()


def test_privacy_assertion_fails_after_raw_archive_is_preserved(tmp_path: Path) -> None:
    config = _config(tmp_path)
    source = tmp_path / "private.zip"
    _write_structural_package(source, manifest=_manifest(contains_personal_identifiers=True))

    result = import_league_history_package(config, source)
    repeated = import_league_history_package(config, source)

    assert result.status == "validation_failed"
    assert repeated.status == "validation_failed"
    assert repeated.idempotent_reuse
    assert result.raw_path.is_file()
    assert any(
        issue.code == "personal_identifiers_not_cleared" for issue in result.quality.issues
    )
    warehouse = Warehouse(config.resolve(config.paths.warehouse))
    with warehouse.connect(read_only=True) as connection:
        stored = connection.execute(
            "SELECT status, quality_report FROM league_history_imports"
        ).fetchone()
        stored_count = connection.execute(
            "SELECT count(*) FROM league_history_imports"
        ).fetchone()
    assert stored is not None and stored[0] == "rejected"
    assert "personal_identifiers_not_cleared" in str(stored[1])
    assert stored_count == (1,)


def test_zip_traversal_and_case_collisions_are_rejected(tmp_path: Path) -> None:
    config = _config(tmp_path)
    source = tmp_path / "unsafe.zip"
    _write_structural_package(
        source,
        extra_entries=(("../escape.txt", "no"), ("PACKAGE.JSON", "{}")),
    )

    result = import_league_history_package(config, source)

    codes = {issue.code for issue in result.quality.issues}
    assert result.status == "validation_failed"
    assert "unsafe_archive_path" in codes
    assert "archive_name_collision" in codes
    assert not (tmp_path / "escape.txt").exists()


def test_zip_symlink_is_rejected_without_extraction(tmp_path: Path) -> None:
    config = _config(tmp_path)
    source = tmp_path / "symlink.zip"
    link = zipfile.ZipInfo("weekly_rosters.csv")
    link.create_system = 3
    link.external_attr = (stat.S_IFLNK | 0o777) << 16
    _write_structural_package(source, extra_entries=((link, "target.csv"),))

    result = import_league_history_package(config, source)

    assert result.status == "validation_failed"
    assert any(issue.code == "archive_symlink" for issue in result.quality.issues)


def test_exact_csv_headers_are_required(tmp_path: Path) -> None:
    config = _config(tmp_path)
    source = tmp_path / "wrong-header.zip"
    _write_structural_package(source)

    result = import_league_history_package(config, source)

    assert result.status == "validation_failed"
    assert sum(issue.code == "invalid_csv_header" for issue in result.quality.issues) == 3
