"""Reusable dataframe validation for manual CSV importers."""

from __future__ import annotations

from collections.abc import Sequence

import pandas as pd

from fantasy_draft_ai.schemas.quality import QualityIssue, QualityReport, Severity


def validate_tabular_import(
    frame: pd.DataFrame,
    *,
    source: str,
    required_columns: Sequence[str],
    required_values: Sequence[str],
    duplicate_key: Sequence[str],
) -> QualityReport:
    """Validate headers, required values, and duplicate business keys."""

    issues: list[QualityIssue] = []
    missing_columns = sorted(set(required_columns) - set(frame.columns))
    if missing_columns:
        issues.append(
            QualityIssue(
                code="missing_columns",
                message=f"Missing required columns: {', '.join(missing_columns)}",
                count=len(missing_columns),
                severity=Severity.FATAL,
            )
        )
        return QualityReport(
            source=source,
            row_count=len(frame),
            required_field_failures=len(missing_columns),
            issues=issues,
        )

    failures = 0
    for column in required_values:
        blank = frame[column].isna() | frame[column].astype(str).str.strip().eq("")
        failures += int(blank.sum())
    if failures:
        issues.append(
            QualityIssue(
                code="missing_required_values",
                message="Required fields contain blank values.",
                count=failures,
                severity=Severity.FATAL,
            )
        )

    duplicate_count = int(frame.duplicated(list(duplicate_key), keep=False).sum())
    if duplicate_count:
        issues.append(
            QualityIssue(
                code="duplicate_keys",
                message=f"Duplicate key rows for {', '.join(duplicate_key)}.",
                count=duplicate_count,
                severity=Severity.FATAL,
            )
        )

    return QualityReport(
        source=source,
        row_count=len(frame),
        required_field_failures=failures,
        duplicate_keys=duplicate_count,
        unresolved_players=0,
        issues=issues,
    )
