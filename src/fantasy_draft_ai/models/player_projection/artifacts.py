"""Safe, verified persistence for fitted Phase 4 player models.

The modeling dependencies are deliberately imported inside public functions so
that data and status commands continue to work without the optional modeling
extra installed.
"""

from __future__ import annotations

import hashlib
import os
import tempfile
from dataclasses import dataclass
from pathlib import Path, PurePath
from typing import Any


class ArtifactPathError(ValueError):
    """Raised when an artifact path is not safely contained by its root."""


class ArtifactVerificationError(RuntimeError):
    """Raised when a serialized model does not reproduce its predictions."""


class ArtifactIntegrityError(RuntimeError):
    """Raised when a stored artifact no longer matches its recorded metadata."""


@dataclass(frozen=True)
class ArtifactMetadata:
    """Portable metadata persisted alongside a fitted model record."""

    relative_path: str
    sha256: str
    size_bytes: int

    @property
    def artifact_path(self) -> str:
        """Return the warehouse-facing artifact path."""

        return self.relative_path

    @property
    def artifact_sha256(self) -> str:
        """Return the warehouse-facing artifact digest."""

        return self.sha256

    @property
    def artifact_size_bytes(self) -> int:
        """Return the warehouse-facing artifact byte count."""

        return self.size_bytes

    def as_dict(self) -> dict[str, str | int]:
        """Return JSON-safe keys aligned with the warehouse schema."""

        return {
            "artifact_path": self.relative_path,
            "artifact_sha256": self.sha256,
            "artifact_size_bytes": self.size_bytes,
        }


def resolve_artifact_path(artifact_root: Path, relative_path: str | Path) -> Path:
    """Resolve a portable relative artifact path and reject path traversal.

    Only ``.joblib`` files below ``artifact_root`` are accepted. Absolute paths,
    drive-qualified paths, empty paths, and parent traversal are all rejected.
    Existing symlinked path components are resolved before containment is
    checked.
    """

    raw = str(relative_path).strip()
    if not raw:
        raise ArtifactPathError("Artifact path cannot be empty.")

    portable = raw.replace("\\", "/")
    path = Path(portable)
    pure = PurePath(portable)
    if path.is_absolute() or path.drive or pure.is_absolute() or ".." in pure.parts:
        raise ArtifactPathError("Artifact path must be relative and cannot traverse parents.")
    if pure.parts in {(), (".",)} or path.suffix.casefold() != ".joblib":
        raise ArtifactPathError("Artifact path must name a relative .joblib file.")

    root = artifact_root.resolve()
    candidate = (root / path).resolve()
    try:
        candidate.relative_to(root)
    except ValueError as exc:
        raise ArtifactPathError("Artifact path resolves outside the artifact root.") from exc
    if candidate == root:
        raise ArtifactPathError("Artifact path must name a file below the artifact root.")
    return candidate


def persist_verified_model(
    model: Any,
    artifact_root: Path,
    relative_path: str | Path,
    verification_features: Any,
    *,
    expected_predictions: Any | None = None,
    relative_tolerance: float = 1e-12,
    absolute_tolerance: float = 1e-12,
) -> ArtifactMetadata:
    """Atomically persist a model only after staged reload verification.

    Predictions are calculated before serialization (or supplied explicitly),
    the staged file is reloaded, and its predictions must match. The verified
    staged file then atomically replaces the destination, preventing a failed
    serialization from damaging a previously valid artifact.
    """

    import joblib  # type: ignore[import-untyped]
    import numpy as np

    if relative_tolerance < 0 or absolute_tolerance < 0:
        raise ValueError("Prediction comparison tolerances cannot be negative.")
    target = resolve_artifact_path(artifact_root, relative_path)
    target.parent.mkdir(parents=True, exist_ok=True)
    expected = (
        np.asarray(expected_predictions, dtype=float)
        if expected_predictions is not None
        else np.asarray(model.predict(verification_features), dtype=float)
    )
    if not np.all(np.isfinite(expected)):
        raise ArtifactVerificationError("Expected verification predictions must be finite.")

    descriptor, temporary_name = tempfile.mkstemp(
        prefix=f".{target.stem}-",
        suffix=".staged.joblib",
        dir=target.parent,
    )
    os.close(descriptor)
    staged = Path(temporary_name)
    try:
        joblib.dump(model, staged, compress=3, protocol=5)
        reloaded = joblib.load(staged)
        actual = np.asarray(reloaded.predict(verification_features), dtype=float)
        if expected.shape != actual.shape:
            raise ArtifactVerificationError(
                "Reloaded model predictions changed shape during artifact verification."
            )
        if not np.all(np.isfinite(actual)):
            raise ArtifactVerificationError(
                "Reloaded model produced non-finite verification predictions."
            )
        try:
            np.testing.assert_allclose(
                actual,
                expected,
                rtol=relative_tolerance,
                atol=absolute_tolerance,
                equal_nan=False,
            )
        except AssertionError as exc:
            raise ArtifactVerificationError(
                "Reloaded model predictions differ from the fitted model."
            ) from exc
        os.replace(staged, target)
    finally:
        staged.unlink(missing_ok=True)

    return _metadata_for_path(artifact_root, target)


def verify_artifact(
    artifact_root: Path,
    relative_path: str | Path,
    *,
    expected_sha256: str | None = None,
    expected_size_bytes: int | None = None,
) -> ArtifactMetadata:
    """Verify one artifact's location, size, and optional recorded digest."""

    path = resolve_artifact_path(artifact_root, relative_path)
    if not path.is_file():
        raise ArtifactIntegrityError(f"Model artifact is missing: {relative_path}.")
    metadata = _metadata_for_path(artifact_root, path)
    if expected_size_bytes is not None and metadata.size_bytes != expected_size_bytes:
        raise ArtifactIntegrityError(f"Model artifact size mismatch for {metadata.relative_path}.")
    if expected_sha256 is not None and metadata.sha256 != expected_sha256.casefold():
        raise ArtifactIntegrityError(
            f"Model artifact SHA-256 mismatch for {metadata.relative_path}."
        )
    return metadata


def load_verified_model(
    artifact_root: Path,
    relative_path: str | Path,
    *,
    expected_sha256: str | None = None,
    expected_size_bytes: int | None = None,
) -> Any:
    """Load a model only after its recorded file integrity has been verified."""

    import joblib

    verify_artifact(
        artifact_root,
        relative_path,
        expected_sha256=expected_sha256,
        expected_size_bytes=expected_size_bytes,
    )
    return joblib.load(resolve_artifact_path(artifact_root, relative_path))


def _metadata_for_path(artifact_root: Path, path: Path) -> ArtifactMetadata:
    root = artifact_root.resolve()
    resolved = path.resolve()
    try:
        relative = resolved.relative_to(root).as_posix()
    except ValueError as exc:
        raise ArtifactPathError("Artifact path resolves outside the artifact root.") from exc
    return ArtifactMetadata(
        relative_path=relative,
        sha256=_sha256(resolved),
        size_bytes=resolved.stat().st_size,
    )


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as artifact:
        for chunk in iter(lambda: artifact.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()
