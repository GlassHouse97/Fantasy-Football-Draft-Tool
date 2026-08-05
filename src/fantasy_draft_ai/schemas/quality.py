"""Human-readable data quality reports shared by importers."""

from __future__ import annotations

from enum import StrEnum

from pydantic import BaseModel, ConfigDict, Field


class Severity(StrEnum):
    WARNING = "warning"
    FATAL = "fatal"


class QualityIssue(BaseModel):
    model_config = ConfigDict(extra="forbid")

    code: str
    message: str
    count: int = Field(default=1, ge=0)
    severity: Severity = Severity.WARNING


class QualityReport(BaseModel):
    """A stable report that CLI and Streamlit can both render."""

    model_config = ConfigDict(extra="forbid")

    source: str
    row_count: int = Field(ge=0)
    required_field_failures: int = Field(default=0, ge=0)
    duplicate_keys: int = Field(default=0, ge=0)
    unresolved_players: int = Field(default=0, ge=0)
    excluded_rows: int = Field(default=0, ge=0)
    identity_conflicts: int = Field(default=0, ge=0)
    impossible_picks_or_rounds: int = Field(default=0, ge=0)
    unsupported_lineup_slots: int = Field(default=0, ge=0)
    invalid_json_settings: int = Field(default=0, ge=0)
    issues: list[QualityIssue] = Field(default_factory=list)

    @property
    def has_fatal_errors(self) -> bool:
        return any(issue.severity == Severity.FATAL for issue in self.issues)

    def render(self) -> str:
        status = "FAILED" if self.has_fatal_errors else "PASSED"
        lines = [
            f"Data quality report: {status}",
            f"Source: {self.source}",
            f"Rows: {self.row_count}",
            f"Required-field failures: {self.required_field_failures}",
            f"Duplicate keys: {self.duplicate_keys}",
            f"Unresolved players: {self.unresolved_players}",
            f"Excluded rows: {self.excluded_rows}",
            f"Identity conflicts: {self.identity_conflicts}",
            f"Impossible picks/rounds: {self.impossible_picks_or_rounds}",
            f"Unsupported lineup slots: {self.unsupported_lineup_slots}",
            f"Invalid JSON settings: {self.invalid_json_settings}",
        ]
        lines.extend(
            f"- {issue.severity.value.upper()} {issue.code}: {issue.message} ({issue.count})"
            for issue in self.issues
        )
        return "\n".join(lines)
