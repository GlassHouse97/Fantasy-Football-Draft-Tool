"""Transactional DuckDB persistence for append-only draft event streams."""

from __future__ import annotations

import hashlib
import json
import uuid
from dataclasses import dataclass, replace
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import duckdb

from fantasy_draft_ai.data.warehouse import Warehouse
from fantasy_draft_ai.draft.pool import FrozenDraftPlayer, player_pool_fingerprint
from fantasy_draft_ai.draft.state import (
    DraftEvent,
    DraftState,
    DraftStateError,
    apply_event,
    replay_events,
)
from fantasy_draft_ai.rules.models import LeagueRules

_PLAYER_STORAGE_COLUMNS = """
    session_id, player_id, display_name, position, p10, p50, p90,
    prediction_status, projection_source, projection_method, market_source,
    market_snapshot_id, market_captured_at, average_pick, availability_scale,
    availability_evidence, mapping_confidence, player_payload
"""


class DraftConcurrencyError(DraftStateError):
    """Raised when a caller submits a command against a stale event version."""


@dataclass(frozen=True)
class DraftSessionInfo:
    session_id: str
    session_name: str
    status: str
    ruleset_fingerprint: str
    scoring_fingerprint: str
    user_draft_slot: int
    projection_run_id: str
    adp_build_fingerprint: str | None
    player_pool_fingerprint: str
    engine_config_fingerprint: str
    player_pool_rows: int
    mapped_market_rows: int
    recommendation_status: str
    recommendation_message: str
    random_seed: int
    simulation_count: int
    current_version: int
    state_fingerprint: str
    created_at: datetime
    updated_at: datetime


class DraftRepository:
    """Use short transactions and replay as the authority for every mutation."""

    def __init__(self, warehouse_path: Path) -> None:
        self.path = warehouse_path

    def initialize(self) -> None:
        Warehouse(self.path).initialize()

    def create_session(
        self,
        *,
        session_name: str,
        rules: LeagueRules,
        user_draft_slot: int,
        projection_run_id: str,
        adp_build_fingerprint: str | None,
        players: tuple[FrozenDraftPlayer, ...],
        engine_config_fingerprint: str,
        recommendation_status: str,
        recommendation_message: str,
        random_seed: int,
        simulation_count: int,
        session_id: str | None = None,
        command_id: str | None = None,
    ) -> DraftState:
        self.initialize()
        normalized_name = session_name.strip()
        if not normalized_name:
            raise ValueError("session_name cannot be blank.")
        pool_fingerprint = player_pool_fingerprint(players)
        if not players:
            raise ValueError("A draft session requires at least one frozen player.")
        actual_session_id = session_id or f"draft-{uuid.uuid4().hex[:16]}"
        now = datetime.now(UTC)
        start_event = DraftEvent(
            session_id=actual_session_id,
            sequence=0,
            event_id=f"event-{uuid.uuid4().hex}",
            event_type="session_started",
            occurred_at=now,
            command_id=command_id or f"command-{uuid.uuid4().hex}",
            payload={
                "rules": rules.model_dump(mode="json"),
                "ruleset_fingerprint": rules.fingerprint(),
                "user_draft_slot": user_draft_slot,
                "projection_run_id": projection_run_id,
                "adp_build_fingerprint": adp_build_fingerprint,
                "player_pool_fingerprint": pool_fingerprint,
                "engine_config_fingerprint": engine_config_fingerprint,
                "random_seed": random_seed,
                "simulation_count": simulation_count,
            },
            prior_state_fingerprint=None,
        )
        state = apply_event(None, start_event)
        start_event = replace(start_event, resulting_state_fingerprint=state.fingerprint())
        with duckdb.connect(str(self.path)) as connection:
            connection.execute("BEGIN TRANSACTION")
            try:
                connection.execute(
                    """
                    INSERT INTO draft_sessions VALUES (
                        ?, ?, 'active', ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?
                    )
                    """,
                    [
                        actual_session_id,
                        normalized_name,
                        rules.canonical_json(),
                        rules.fingerprint(),
                        rules.scoring_fingerprint(),
                        rules.teams,
                        rules.draft.rounds,
                        user_draft_slot,
                        projection_run_id,
                        adp_build_fingerprint,
                        pool_fingerprint,
                        engine_config_fingerprint,
                        len(players),
                        sum(player.has_market_evidence for player in players),
                        recommendation_status,
                        recommendation_message,
                        random_seed,
                        simulation_count,
                        state.version,
                        state.fingerprint(),
                        now,
                        now,
                    ],
                )
                self._insert_players(connection, actual_session_id, players)
                self._insert_event(connection, start_event)
                connection.execute("COMMIT")
            except Exception:
                connection.execute("ROLLBACK")
                raise
        return state

    def list_sessions(self) -> tuple[DraftSessionInfo, ...]:
        self.initialize()
        with duckdb.connect(str(self.path), read_only=True) as connection:
            rows = connection.execute(
                "SELECT * FROM draft_sessions ORDER BY updated_at DESC, session_id"
            ).fetchall()
            columns = [str(item[0]) for item in connection.description]
        return tuple(self._session_info(dict(zip(columns, row, strict=True))) for row in rows)

    def session_info(self, session_id: str) -> DraftSessionInfo:
        self.initialize()
        with duckdb.connect(str(self.path), read_only=True) as connection:
            return self._session_info_from_connection(connection, session_id)

    def load_state(self, session_id: str) -> DraftState:
        self.initialize()
        with duckdb.connect(str(self.path), read_only=True) as connection:
            return self._load_state(connection, session_id)

    def load_players(self, session_id: str) -> tuple[FrozenDraftPlayer, ...]:
        self.initialize()
        with duckdb.connect(str(self.path), read_only=True) as connection:
            return self._load_players(connection, session_id)

    def record_pick(
        self,
        session_id: str,
        player_id: str,
        *,
        expected_version: int,
        command_id: str | None = None,
    ) -> DraftState:
        def payload(state: DraftState, player: FrozenDraftPlayer) -> dict[str, Any]:
            current = state.current_overall_pick
            if current is None or state.current_team_id is None:
                raise DraftStateError("The draft is complete.")
            return {
                "overall_pick": current,
                "team_id": state.current_team_id,
                "player_id": player.player_id,
                "player_name": player.display_name,
                "position": player.position,
                "projected_points": player.p50,
            }

        return self._append_player_event(
            session_id,
            player_id,
            event_type="pick_made",
            expected_version=expected_version,
            command_id=command_id,
            command_semantics={"player_id": player_id},
            payload_builder=payload,
        )

    def undo_last(
        self,
        session_id: str,
        *,
        expected_version: int,
        command_id: str | None = None,
    ) -> DraftState:
        self.initialize()
        with duckdb.connect(str(self.path)) as connection:
            connection.execute("BEGIN TRANSACTION")
            try:
                existing = self._idempotent_state(
                    connection,
                    session_id,
                    command_id,
                    expected_version=expected_version,
                    event_type="pick_undone",
                    command_semantics={},
                )
                if existing is not None:
                    connection.execute("COMMIT")
                    return existing
                state = self._load_state(connection, session_id)
                self._require_version(state, expected_version)
                if not state.picks:
                    raise DraftStateError("There is no pick to undo.")
                event = self._build_event(
                    state,
                    "pick_undone",
                    {"target_event_id": state.picks[-1].event_id},
                    command_id,
                )
                result = apply_event(state, event)
                event = replace(event, resulting_state_fingerprint=result.fingerprint())
                self._commit_event(connection, event, result)
                connection.execute("COMMIT")
                return result
            except Exception:
                connection.execute("ROLLBACK")
                raise

    def replace_pick(
        self,
        session_id: str,
        overall_pick: int,
        player_id: str,
        *,
        expected_version: int,
        command_id: str | None = None,
    ) -> DraftState:
        def payload(state: DraftState, player: FrozenDraftPlayer) -> dict[str, Any]:
            if not 1 <= overall_pick <= len(state.picks):
                raise DraftStateError("overall_pick does not identify an active pick.")
            prior = state.picks[overall_pick - 1]
            return {
                "overall_pick": overall_pick,
                "target_event_id": prior.event_id,
                "team_id": prior.team_id,
                "player_id": player.player_id,
                "player_name": player.display_name,
                "position": player.position,
                "projected_points": player.p50,
            }

        return self._append_player_event(
            session_id,
            player_id,
            event_type="pick_replaced",
            expected_version=expected_version,
            command_id=command_id,
            command_semantics={"player_id": player_id, "overall_pick": overall_pick},
            payload_builder=payload,
        )

    def verify_session(self, session_id: str) -> DraftState:
        self.initialize()
        with duckdb.connect(str(self.path), read_only=True) as connection:
            state = self._load_state(connection, session_id)
            info = self._session_info_from_connection(connection, session_id)
            players = self._load_players(connection, session_id)
            if info.current_version != state.version:
                raise DraftStateError("Session metadata version does not match event replay.")
            if info.state_fingerprint != state.fingerprint():
                raise DraftStateError("Session metadata fingerprint does not match event replay.")
            if info.player_pool_fingerprint != player_pool_fingerprint(players):
                raise DraftStateError("Frozen session player pool fingerprint is invalid.")
            if info.player_pool_rows != len(players):
                raise DraftStateError("Frozen session player count does not reconcile.")
            if info.mapped_market_rows != sum(player.has_market_evidence for player in players):
                raise DraftStateError("Frozen mapped-market count does not reconcile.")
            return state

    def integrity_issues(self) -> tuple[str, ...]:
        self.initialize()
        issues: list[str] = []
        with duckdb.connect(str(self.path), read_only=True) as connection:
            orphan_counts = connection.execute(
                """
                SELECT
                    (SELECT count(*) FROM draft_session_players AS player
                     LEFT JOIN draft_sessions AS session USING (session_id)
                     WHERE session.session_id IS NULL),
                    (SELECT count(*) FROM draft_events AS event
                     LEFT JOIN draft_sessions AS session USING (session_id)
                     WHERE session.session_id IS NULL),
                    (SELECT count(*) FROM draft_recommendation_runs AS result
                     LEFT JOIN draft_sessions AS session USING (session_id)
                     WHERE session.session_id IS NULL)
                """
            ).fetchone()
            if orphan_counts is None or any(int(value) for value in orphan_counts):
                issues.append("Draft persistence contains orphan session-dependent rows.")
            recommendation_rows = connection.execute(
                """
                SELECT recommendation_run_id, result_fingerprint, result_payload,
                       session_version, state_fingerprint, engine_config_fingerprint,
                       session_id, random_seed, simulation_count, status
                FROM draft_recommendation_runs
                """
            ).fetchall()
            for row in recommendation_rows:
                payload = _json_object(row[2])
                if str(row[1]) != _fingerprint_payload(payload):
                    issues.append(
                        f"Draft recommendation {row[0]} has an invalid result fingerprint."
                    )
                session_row = connection.execute(
                    """
                    SELECT current_version, state_fingerprint, engine_config_fingerprint,
                           projection_run_id, adp_build_fingerprint,
                           player_pool_fingerprint, random_seed, simulation_count
                    FROM draft_sessions WHERE session_id = ?
                    """,
                    [row[6]],
                ).fetchone()
                historical_event = connection.execute(
                    """
                    SELECT resulting_state_fingerprint
                    FROM draft_events
                    WHERE session_id = ? AND sequence = ?
                    """,
                    [row[6], row[3]],
                ).fetchone()
                session_lineage_valid = session_row is not None and (
                    0 <= int(row[3]) <= int(session_row[0])
                    and str(row[5]) == str(session_row[2])
                    and historical_event is not None
                    and str(row[4]) == str(historical_event[0])
                )
                if not session_lineage_valid:
                    issues.append(
                        f"Draft recommendation {row[0]} has invalid session/config lineage."
                    )
                    continue
                assert session_row is not None
                expected_payload_lineage = {
                    "session_id": str(row[6]),
                    "session_version": int(row[3]),
                    "state_fingerprint": str(row[4]),
                    "projection_run_id": str(session_row[3]),
                    "adp_build_fingerprint": (
                        None if session_row[4] is None else str(session_row[4])
                    ),
                    "player_pool_fingerprint": str(session_row[5]),
                    "engine_config_fingerprint": str(row[5]),
                    "random_seed": int(row[7]),
                    "simulation_count": int(row[8]),
                    "code": str(row[9]),
                }
                if any(
                    key not in payload or payload[key] != expected
                    for key, expected in expected_payload_lineage.items()
                ):
                    issues.append(
                        f"Draft recommendation {row[0]} has invalid result-payload lineage."
                    )
        for session in self.list_sessions():
            try:
                self.verify_session(session.session_id)
            except (DraftStateError, ValueError, TypeError, json.JSONDecodeError) as exc:
                issues.append(f"Draft session {session.session_id} failed replay integrity: {exc}")
        return tuple(issues)

    def save_recommendation(
        self,
        *,
        recommendation_run_id: str,
        session_id: str,
        state: DraftState,
        engine_config_fingerprint: str,
        random_seed: int,
        simulation_count: int,
        status: str,
        result_fingerprint: str,
        result_payload: dict[str, Any],
    ) -> None:
        self.initialize()
        with duckdb.connect(str(self.path)) as connection:
            connection.execute(
                """
                INSERT INTO draft_recommendation_runs VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT (recommendation_run_id) DO NOTHING
                """,
                [
                    recommendation_run_id,
                    session_id,
                    state.version,
                    state.fingerprint(),
                    engine_config_fingerprint,
                    random_seed,
                    simulation_count,
                    status,
                    result_fingerprint,
                    _canonical_json(result_payload),
                    datetime.now(UTC),
                ],
            )

    def _append_player_event(
        self,
        session_id: str,
        player_id: str,
        *,
        event_type: str,
        expected_version: int,
        command_id: str | None,
        command_semantics: dict[str, Any],
        payload_builder: Any,
    ) -> DraftState:
        self.initialize()
        with duckdb.connect(str(self.path)) as connection:
            connection.execute("BEGIN TRANSACTION")
            try:
                existing = self._idempotent_state(
                    connection,
                    session_id,
                    command_id,
                    expected_version=expected_version,
                    event_type=event_type,
                    command_semantics=command_semantics,
                )
                if existing is not None:
                    connection.execute("COMMIT")
                    return existing
                state = self._load_state(connection, session_id)
                self._require_version(state, expected_version)
                player = self._load_player(connection, session_id, player_id)
                event = self._build_event(
                    state,
                    event_type,
                    payload_builder(state, player),
                    command_id,
                )
                result = apply_event(state, event)
                event = replace(event, resulting_state_fingerprint=result.fingerprint())
                self._commit_event(connection, event, result)
                connection.execute("COMMIT")
                return result
            except Exception:
                connection.execute("ROLLBACK")
                raise

    def _idempotent_state(
        self,
        connection: duckdb.DuckDBPyConnection,
        session_id: str,
        command_id: str | None,
        *,
        expected_version: int,
        event_type: str,
        command_semantics: dict[str, Any],
    ) -> DraftState | None:
        if command_id is None:
            return None
        row = connection.execute(
            "SELECT sequence, event_type, payload FROM draft_events "
            "WHERE session_id = ? AND command_id = ?",
            [session_id, command_id],
        ).fetchone()
        if row is None:
            return None
        payload = _json_object(row[2])
        same_command = (
            int(row[0]) == expected_version + 1
            and str(row[1]) == event_type
            and all(payload.get(key) == value for key, value in command_semantics.items())
        )
        if not same_command:
            raise DraftStateError(
                f"command_id {command_id!r} is already bound to a different draft command."
            )
        return self._load_state(connection, session_id)

    @staticmethod
    def _require_version(state: DraftState, expected_version: int) -> None:
        if state.version != expected_version:
            raise DraftConcurrencyError(
                f"Draft version changed: expected {expected_version}, current {state.version}."
            )

    @staticmethod
    def _build_event(
        state: DraftState,
        event_type: str,
        payload: dict[str, Any],
        command_id: str | None,
    ) -> DraftEvent:
        return DraftEvent(
            session_id=state.session_id,
            sequence=state.version + 1,
            event_id=f"event-{uuid.uuid4().hex}",
            event_type=event_type,
            occurred_at=datetime.now(UTC),
            command_id=command_id or f"command-{uuid.uuid4().hex}",
            payload=payload,
            prior_state_fingerprint=state.fingerprint(),
        )

    def _commit_event(
        self,
        connection: duckdb.DuckDBPyConnection,
        event: DraftEvent,
        state: DraftState,
    ) -> None:
        self._insert_event(connection, event)
        status = "complete" if state.complete else "active"
        connection.execute(
            """
            UPDATE draft_sessions
            SET status = ?, current_version = ?, state_fingerprint = ?, updated_at = ?
            WHERE session_id = ?
            """,
            [
                status,
                state.version,
                state.fingerprint(),
                datetime.now(UTC),
                state.session_id,
            ],
        )

    @staticmethod
    def _insert_event(connection: duckdb.DuckDBPyConnection, event: DraftEvent) -> None:
        if event.resulting_state_fingerprint is None:
            raise ValueError("A persisted event requires its resulting state fingerprint.")
        connection.execute(
            "INSERT INTO draft_events VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
            [
                event.session_id,
                event.sequence,
                event.event_id,
                event.event_type,
                event.occurred_at,
                event.command_id,
                _canonical_json(event.payload),
                event.prior_state_fingerprint,
                event.resulting_state_fingerprint,
            ],
        )

    @staticmethod
    def _insert_players(
        connection: duckdb.DuckDBPyConnection,
        session_id: str,
        players: tuple[FrozenDraftPlayer, ...],
    ) -> None:
        connection.executemany(
            "INSERT INTO draft_session_players VALUES "
            "(?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
            [
                [
                    session_id,
                    player.player_id,
                    player.display_name,
                    player.position,
                    player.p10,
                    player.p50,
                    player.p90,
                    player.prediction_status,
                    player.projection_source,
                    player.projection_method,
                    player.market_source,
                    player.market_snapshot_id,
                    player.market_captured_at,
                    player.average_pick,
                    player.availability_scale,
                    player.availability_evidence,
                    player.mapping_confidence,
                    _canonical_json(player.as_dict()),
                ]
                for player in players
            ],
        )

    def _load_state(
        self,
        connection: duckdb.DuckDBPyConnection,
        session_id: str,
    ) -> DraftState:
        rows = connection.execute(
            """
            SELECT session_id, sequence, event_id, event_type, occurred_at, payload,
                   command_id, prior_state_fingerprint, resulting_state_fingerprint
            FROM draft_events WHERE session_id = ? ORDER BY sequence
            """,
            [session_id],
        ).fetchall()
        if not rows:
            raise KeyError(f"Unknown draft session: {session_id}")
        events = tuple(
            DraftEvent(
                session_id=str(row[0]),
                sequence=int(row[1]),
                event_id=str(row[2]),
                event_type=str(row[3]),
                occurred_at=_datetime(row[4]),
                payload=_json_object(row[5]),
                command_id=str(row[6]),
                prior_state_fingerprint=None if row[7] is None else str(row[7]),
                resulting_state_fingerprint=None if row[8] is None else str(row[8]),
            )
            for row in rows
        )
        return replay_events(session_id, events)

    def _load_players(
        self,
        connection: duckdb.DuckDBPyConnection,
        session_id: str,
    ) -> tuple[FrozenDraftPlayer, ...]:
        rows = connection.execute(
            f"SELECT {_PLAYER_STORAGE_COLUMNS} FROM draft_session_players "
            "WHERE session_id = ? ORDER BY player_id",
            [session_id],
        ).fetchall()
        return tuple(_player_from_storage_row(row, session_id) for row in rows)

    def _load_player(
        self,
        connection: duckdb.DuckDBPyConnection,
        session_id: str,
        player_id: str,
    ) -> FrozenDraftPlayer:
        row = connection.execute(
            f"SELECT {_PLAYER_STORAGE_COLUMNS} FROM draft_session_players "
            "WHERE session_id = ? AND player_id = ?",
            [session_id, player_id],
        ).fetchone()
        if row is None:
            raise KeyError(f"Player {player_id} is not in frozen session {session_id}.")
        return _player_from_storage_row(row, session_id)

    def _session_info_from_connection(
        self,
        connection: duckdb.DuckDBPyConnection,
        session_id: str,
    ) -> DraftSessionInfo:
        cursor = connection.execute(
            "SELECT * FROM draft_sessions WHERE session_id = ?", [session_id]
        )
        row = cursor.fetchone()
        if row is None:
            raise KeyError(f"Unknown draft session: {session_id}")
        columns = [str(item[0]) for item in cursor.description]
        return self._session_info(dict(zip(columns, row, strict=True)))

    @staticmethod
    def _session_info(row: dict[str, Any]) -> DraftSessionInfo:
        return DraftSessionInfo(
            session_id=str(row["session_id"]),
            session_name=str(row["session_name"]),
            status=str(row["status"]),
            ruleset_fingerprint=str(row["ruleset_fingerprint"]),
            scoring_fingerprint=str(row["scoring_fingerprint"]),
            user_draft_slot=int(row["user_draft_slot"]),
            projection_run_id=str(row["projection_run_id"]),
            adp_build_fingerprint=(
                None
                if row["adp_build_fingerprint"] is None
                else str(row["adp_build_fingerprint"])
            ),
            player_pool_fingerprint=str(row["player_pool_fingerprint"]),
            engine_config_fingerprint=str(row["engine_config_fingerprint"]),
            player_pool_rows=int(row["player_pool_rows"]),
            mapped_market_rows=int(row["mapped_market_rows"]),
            recommendation_status=str(row["recommendation_status"]),
            recommendation_message=str(row["recommendation_message"]),
            random_seed=int(row["random_seed"]),
            simulation_count=int(row["simulation_count"]),
            current_version=int(row["current_version"]),
            state_fingerprint=str(row["state_fingerprint"]),
            created_at=_datetime(row["created_at"]),
            updated_at=_datetime(row["updated_at"]),
        )


def _canonical_json(value: Any) -> str:
    return json.dumps(
        value,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=True,
        allow_nan=False,
    )


def _fingerprint_payload(value: Any) -> str:
    return hashlib.sha256(_canonical_json(value).encode("utf-8")).hexdigest()


def _json_object(value: Any) -> dict[str, Any]:
    parsed = json.loads(value) if isinstance(value, str) else value
    if not isinstance(parsed, dict):
        raise ValueError("Expected a JSON object.")
    return {str(key): item for key, item in parsed.items()}


def _datetime(value: Any) -> datetime:
    if not isinstance(value, datetime):
        raise TypeError("Expected a persisted timestamp.")
    return value


def _player_from_payload(payload: dict[str, Any]) -> FrozenDraftPlayer:
    captured = payload.get("market_captured_at")
    return FrozenDraftPlayer(
        player_id=str(payload["player_id"]),
        display_name=str(payload["display_name"]),
        position=str(payload["position"]),
        p10=float(payload["p10"]),
        p50=float(payload["p50"]),
        p90=float(payload["p90"]),
        prediction_status=str(payload["prediction_status"]),
        projection_source=str(payload["projection_source"]),
        projection_method=str(payload["projection_method"]),
        market_source=(
            None if payload.get("market_source") is None else str(payload["market_source"])
        ),
        market_snapshot_id=(
            None
            if payload.get("market_snapshot_id") is None
            else str(payload["market_snapshot_id"])
        ),
        market_captured_at=None if captured is None else datetime.fromisoformat(str(captured)),
        average_pick=(
            None if payload.get("average_pick") is None else float(payload["average_pick"])
        ),
        availability_scale=(
            None
            if payload.get("availability_scale") is None
            else float(payload["availability_scale"])
        ),
        availability_evidence=(
            None
            if payload.get("availability_evidence") is None
            else str(payload["availability_evidence"])
        ),
        mapping_confidence=(
            None
            if payload.get("mapping_confidence") is None
            else str(payload["mapping_confidence"])
        ),
    )


def _player_from_storage_row(
    row: tuple[Any, ...],
    expected_session_id: str,
) -> FrozenDraftPlayer:
    if len(row) != 18:
        raise DraftStateError("Frozen session player storage has an unexpected column count.")
    payload = _json_object(row[17])
    player = _player_from_payload(payload)
    actual = (
        str(row[0]),
        str(row[1]),
        str(row[2]),
        str(row[3]),
        float(row[4]),
        float(row[5]),
        float(row[6]),
        str(row[7]),
        str(row[8]),
        str(row[9]),
        None if row[10] is None else str(row[10]),
        None if row[11] is None else str(row[11]),
        None if row[12] is None else _datetime(row[12]),
        None if row[13] is None else float(row[13]),
        None if row[14] is None else float(row[14]),
        None if row[15] is None else str(row[15]),
        None if row[16] is None else str(row[16]),
    )
    expected = (
        expected_session_id,
        player.player_id,
        player.display_name,
        player.position,
        player.p10,
        player.p50,
        player.p90,
        player.prediction_status,
        player.projection_source,
        player.projection_method,
        player.market_source,
        player.market_snapshot_id,
        player.market_captured_at,
        player.average_pick,
        player.availability_scale,
        player.availability_evidence,
        player.mapping_confidence,
    )
    if actual != expected or _canonical_json(payload) != _canonical_json(player.as_dict()):
        raise DraftStateError(
            "Frozen session player columns do not match player_payload for "
            f"{player.player_id}."
        )
    return player
