"""Validated local league setup records with idempotent DuckDB persistence."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Literal, cast

import duckdb
import yaml
from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

from fantasy_draft_ai.config import find_project_root
from fantasy_draft_ai.data.warehouse import Warehouse
from fantasy_draft_ai.rules.models import LeagueRules

SETUP_SCHEMA_VERSION: Literal["league-setup-v1"] = "league-setup-v1"
DEFAULT_REFERENCE_RULES_PATH = Path("configs/example_ppr_12_team.yaml")


class LeagueSetupIntegrityError(RuntimeError):
    """Raised when a stored setup no longer matches its normalized rules."""


class PlayoffSettings(BaseModel):
    """Optional playoff fields supported by the Phase 7 league setup page."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    playoff_teams: int = Field(ge=2, le=32)
    playoff_start_week: int = Field(ge=1, le=22)
    championship_week: int = Field(ge=1, le=22)

    @model_validator(mode="after")
    def validate_week_order(self) -> PlayoffSettings:
        if self.championship_week < self.playoff_start_week:
            raise ValueError("Championship week cannot be before the playoff start week.")
        return self


class LeagueSetupRecord(BaseModel):
    """One user's exact rules, draft position, and optional playoff context."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    league_season_id: str = Field(min_length=1, max_length=120)
    platform: str = Field(default="local", min_length=1, max_length=80)
    rules: LeagueRules
    draft_slot: int = Field(ge=1, le=32)
    playoff_settings: PlayoffSettings | None = None

    @field_validator("league_season_id", "platform")
    @classmethod
    def normalize_text(cls, value: str) -> str:
        normalized = value.strip()
        if not normalized:
            raise ValueError("Setup identifiers and platform names cannot be blank.")
        return normalized

    @model_validator(mode="after")
    def validate_team_dependent_fields(self) -> LeagueSetupRecord:
        if self.draft_slot > self.rules.teams:
            raise ValueError("Draft slot must be between 1 and the configured team count.")
        if (
            self.playoff_settings is not None
            and self.playoff_settings.playoff_teams > self.rules.teams
        ):
            raise ValueError("Playoff teams cannot exceed the configured team count.")
        return self

    def canonical_json(self) -> str:
        """Return a stable representation suitable for backup and replay."""

        return _canonical_json(self.model_dump(mode="json"))

    @property
    def fingerprint_label(self) -> str:
        """Return the readable label for the exact normalized rules fingerprint."""

        return human_ruleset_label(self.rules)


class _LeagueSetupEnvelope(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    schema_version: Literal["league-setup-v1"]
    ruleset_fingerprint: str = Field(pattern=r"^sha256:[0-9a-f]{64}$")
    setup: LeagueSetupRecord

    @model_validator(mode="after")
    def validate_fingerprint(self) -> _LeagueSetupEnvelope:
        if self.ruleset_fingerprint != f"sha256:{self.setup.rules.fingerprint()}":
            raise ValueError("The setup payload does not match its ruleset fingerprint.")
        return self


def human_ruleset_label(rules: LeagueRules) -> str:
    """Build a deterministic, readable label without changing the canonical fingerprint."""

    reception_points = rules.scoring.reception
    if reception_points == 0:
        scoring_label = "Standard"
    elif reception_points == 0.5:
        scoring_label = "Half-PPR"
    elif reception_points == 1:
        scoring_label = "PPR"
    else:
        scoring_label = f"{reception_points:g}-PPR"
    return (
        f"{rules.season} | {rules.teams}-team {scoring_label} "
        f"{rules.draft.type} | {rules.fingerprint()[:10]}"
    )


def load_reference_rules(path: Path | None = None) -> LeagueRules:
    """Load the checked-in, validated 12-team PPR rules as the setup default."""

    actual_path = path or find_project_root() / DEFAULT_REFERENCE_RULES_PATH
    with actual_path.open(encoding="utf-8") as handle:
        payload = yaml.safe_load(handle)
    return LeagueRules.model_validate(payload)


def export_setup_yaml(setup: LeagueSetupRecord) -> str:
    """Export a safe, deterministic payload that detects ruleset tampering on import."""

    envelope = _LeagueSetupEnvelope(
        schema_version=SETUP_SCHEMA_VERSION,
        ruleset_fingerprint=f"sha256:{setup.rules.fingerprint()}",
        setup=setup,
    )
    return yaml.safe_dump(
        envelope.model_dump(mode="json"),
        allow_unicode=False,
        sort_keys=True,
    )


def import_setup_yaml(payload: str) -> LeagueSetupRecord:
    """Safely validate and normalize a setup exported by :func:`export_setup_yaml`."""

    parsed = yaml.safe_load(payload)
    envelope = _LeagueSetupEnvelope.model_validate(parsed)
    return envelope.setup


class LeagueSetupRepository:
    """Persist local setups in the canonical ``league_rules`` warehouse table."""

    def __init__(self, warehouse_path: Path) -> None:
        self.path = warehouse_path.resolve()

    def initialize(self) -> None:
        Warehouse(self.path).initialize()

    def upsert(self, setup: LeagueSetupRecord) -> LeagueSetupRecord:
        """Insert or replace one setup without creating duplicate rows."""

        self.initialize()
        setup = LeagueSetupRecord.model_validate(setup.model_dump(mode="python"))
        rules = setup.rules
        playoff_json = (
            _canonical_json(setup.playoff_settings.model_dump(mode="json"))
            if setup.playoff_settings is not None
            else None
        )
        with duckdb.connect(str(self.path)) as connection:
            connection.execute("BEGIN TRANSACTION")
            try:
                existing = connection.execute(
                    "SELECT user_draft_slot FROM league_rules WHERE league_season_id = ?",
                    [setup.league_season_id],
                ).fetchone()
                if existing is not None and existing[0] is None:
                    raise LeagueSetupIntegrityError(
                        "The setup name collides with an imported historical league-season. "
                        "Choose a distinct local setup name."
                    )
                connection.execute(
                    """
                    INSERT INTO league_rules (
                        league_season_id, platform, season, team_count, user_draft_slot,
                        draft_type, rounds, starter_slots_json, flex_slots_json,
                        bench_slots, ir_slots, scoring_json, playoff_settings_json,
                        normalized_ruleset_json, ruleset_fingerprint
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    ON CONFLICT (league_season_id) DO UPDATE SET
                        platform = excluded.platform,
                        season = excluded.season,
                        team_count = excluded.team_count,
                        user_draft_slot = excluded.user_draft_slot,
                        draft_type = excluded.draft_type,
                        rounds = excluded.rounds,
                        starter_slots_json = excluded.starter_slots_json,
                        flex_slots_json = excluded.flex_slots_json,
                        bench_slots = excluded.bench_slots,
                        ir_slots = excluded.ir_slots,
                        scoring_json = excluded.scoring_json,
                        playoff_settings_json = excluded.playoff_settings_json,
                        normalized_ruleset_json = excluded.normalized_ruleset_json,
                        ruleset_fingerprint = excluded.ruleset_fingerprint
                    """,
                    [
                        setup.league_season_id,
                        setup.platform,
                        rules.season,
                        rules.teams,
                        setup.draft_slot,
                        rules.draft.type,
                        rules.draft.rounds,
                        _canonical_json(rules.starters),
                        _canonical_json(
                            [slot.model_dump(mode="json") for slot in rules.flex_slots]
                        ),
                        rules.bench,
                        rules.ir,
                        _canonical_json(rules.scoring.model_dump(mode="json")),
                        playoff_json,
                        rules.canonical_json(),
                        rules.fingerprint(),
                    ],
                )
                connection.execute("COMMIT")
            except Exception:
                connection.execute("ROLLBACK")
                raise
        persisted = self.load(setup.league_season_id)
        if persisted is None:  # pragma: no cover - defensive database invariant
            raise LeagueSetupIntegrityError("The saved league setup could not be reloaded.")
        return persisted

    def load(self, league_season_id: str) -> LeagueSetupRecord | None:
        """Load one local setup, excluding unrelated historical rules rows."""

        if not self.path.is_file():
            return None
        self.initialize()
        normalized_id = _normalized_id(league_season_id)
        with duckdb.connect(str(self.path), read_only=True) as connection:
            row = connection.execute(
                f"{_SELECT_SETUP_SQL} WHERE league_season_id = ? AND user_draft_slot IS NOT NULL",
                [normalized_id],
            ).fetchone()
        return None if row is None else _record_from_row(row)

    def list(self) -> tuple[LeagueSetupRecord, ...]:
        """List persisted local setups in stable season/identifier order."""

        if not self.path.is_file():
            return ()
        self.initialize()
        with duckdb.connect(str(self.path), read_only=True) as connection:
            rows = connection.execute(
                f"{_SELECT_SETUP_SQL} WHERE user_draft_slot IS NOT NULL "
                "ORDER BY season DESC, league_season_id"
            ).fetchall()
        return tuple(_record_from_row(row) for row in rows)

    def delete(self, league_season_id: str) -> bool:
        """Delete one local setup idempotently without touching historical-only rows."""

        if not self.path.is_file():
            return False
        self.initialize()
        normalized_id = _normalized_id(league_season_id)
        with duckdb.connect(str(self.path)) as connection:
            existing = connection.execute(
                "SELECT count(*) FROM league_rules "
                "WHERE league_season_id = ? AND user_draft_slot IS NOT NULL",
                [normalized_id],
            ).fetchone()
            connection.execute(
                "DELETE FROM league_rules "
                "WHERE league_season_id = ? AND user_draft_slot IS NOT NULL",
                [normalized_id],
            )
        return existing is not None and int(existing[0]) == 1


_SELECT_SETUP_SQL = """
SELECT league_season_id, platform, season, team_count, user_draft_slot,
       draft_type, rounds, starter_slots_json, flex_slots_json, bench_slots,
       ir_slots, scoring_json, playoff_settings_json, normalized_ruleset_json,
       ruleset_fingerprint
FROM league_rules
"""


def _record_from_row(row: tuple[Any, ...]) -> LeagueSetupRecord:
    rules = LeagueRules.model_validate(_parse_json(row[13], "normalized_ruleset_json"))
    expected_values = (
        rules.season,
        rules.teams,
        rules.draft.type,
        rules.draft.rounds,
        rules.bench,
        rules.ir,
        rules.fingerprint(),
    )
    stored_values = (
        int(row[2]),
        int(row[3]),
        str(row[5]),
        int(row[6]),
        int(row[9]),
        int(row[10]),
        str(row[14]),
    )
    if stored_values != expected_values:
        raise LeagueSetupIntegrityError(
            f"Stored setup {row[0]!s} does not match its normalized rules."
        )
    decomposed_json = (
        (_parse_json(row[7], "starter_slots_json"), rules.starters),
        (
            _parse_json(row[8], "flex_slots_json"),
            [slot.model_dump(mode="json") for slot in rules.flex_slots],
        ),
        (_parse_json(row[11], "scoring_json"), rules.scoring.model_dump(mode="json")),
    )
    if any(
        _canonical_json(stored) != _canonical_json(expected) for stored, expected in decomposed_json
    ):
        raise LeagueSetupIntegrityError(
            f"Stored setup {row[0]!s} has inconsistent decomposed rules fields."
        )
    playoff = (
        None
        if row[12] is None
        else PlayoffSettings.model_validate(_parse_json(row[12], "playoff_settings_json"))
    )
    return LeagueSetupRecord(
        league_season_id=str(row[0]),
        platform=str(row[1]),
        rules=rules,
        draft_slot=int(row[4]),
        playoff_settings=playoff,
    )


def _parse_json(value: object, field_name: str) -> object:
    if not isinstance(value, str):
        raise LeagueSetupIntegrityError(f"Stored {field_name} is not valid JSON text.")
    try:
        return cast(object, json.loads(value))
    except json.JSONDecodeError as exc:
        raise LeagueSetupIntegrityError(f"Stored {field_name} is not valid JSON.") from exc


def _canonical_json(value: object) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True)


def _normalized_id(value: str) -> str:
    normalized = value.strip()
    if not normalized:
        raise ValueError("league_season_id cannot be blank.")
    return normalized
