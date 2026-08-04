from datetime import UTC, datetime
from pathlib import Path

import pytest

from fantasy_draft_ai.data.manifests import RawArchive, sha256_file


def test_file_hash_and_manifest_round_trip(tmp_path: Path) -> None:
    archive = RawArchive(tmp_path, tmp_path / "data/raw", tmp_path / "data/raw/manifests")
    moment = datetime(2026, 8, 4, 18, tzinfo=UTC)
    raw_path, acquired_at = archive.write_bytes("demo", "dataset", ".json", b"{}\n", moment)
    manifest, manifest_path = archive.create_manifest(
        source="demo",
        acquisition_method="test",
        acquired_at=acquired_at,
        raw_files=[raw_path],
        seasons=[2025],
    )
    assert sha256_file(raw_path) == manifest.sha256[0]
    assert manifest.raw_files == [raw_path.relative_to(tmp_path).as_posix()]
    assert manifest_path.is_file()
    found = archive.find_manifest_for_files([raw_path])
    assert found is not None
    assert found[0].dataset_id == manifest.dataset_id
    assert found[1] == manifest_path


def test_raw_archive_refuses_same_timestamp_overwrite(tmp_path: Path) -> None:
    archive = RawArchive(tmp_path, tmp_path / "data/raw", tmp_path / "data/raw/manifests")
    moment = datetime(2026, 8, 4, 18, tzinfo=UTC)
    archive.write_bytes("demo", "dataset", ".json", b"first", moment)
    with pytest.raises(FileExistsError, match="Refusing to overwrite"):
        archive.write_bytes("demo", "dataset", ".json", b"second", moment)
