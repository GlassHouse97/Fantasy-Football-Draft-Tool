"""Phase 6 draft-room readiness, frozen player pools, and repository commands.

The service joins projections to market evidence only through a reviewed canonical
``player_id``. Display names are deliberately never considered identity evidence.
"""

from __future__ import annotations

from collections import Counter
from dataclasses import dataclass
from math import isclose

from fantasy_draft_ai.draft.pool import FrozenDraftPlayer
from fantasy_draft_ai.draft.repository import (
    DraftRepository,
    DraftSessionInfo,
)
from fantasy_draft_ai.draft.state import DraftState
from fantasy_draft_ai.recommendations.config import DraftEngineConfig
from fantasy_draft_ai.rules.models import LeagueRules
from fantasy_draft_ai.services.adp_market import AdpMarketBoard, AdpMarketRow
from fantasy_draft_ai.services.projections import (
    TARGET_FANTASY_POINTS_TOTAL,
    PlayerProjection,
    ProjectionBoard,
)

STATE_READY = "state_ready"
IDENTITY_MAPPING_REQUIRED = "identity_mapping_required"
RECOMMENDATION_READY = "recommendation_ready"


class DraftRoomServiceError(ValueError):
    """Raised when a requested session operation is outside the validated boundary."""


@dataclass(frozen=True)
class DraftRoomReadiness:
    """Separate manual-state readiness from recommendation-data readiness."""

    state_ready: bool
    recommendation_ready: bool
    state_status: str
    recommendation_status: str
    state_message: str
    recommendation_message: str
    projection_rows: int
    compatible_market_rows: int
    excluded_market_rows: int
    mapped_market_rows: int
    matched_market_rows: int
    unresolved_market_rows: int
    market_coverage: float
    required_market_coverage: float
    scoring_format: str | None
    duplicate_mapped_player_ids: tuple[str, ...] = ()
    unmatched_mapped_player_ids: tuple[str, ...] = ()
    conflicting_position_player_ids: tuple[str, ...] = ()
    excluded_market_positions: tuple[str, ...] = ()


@dataclass(frozen=True)
class DraftRoomPreparation:
    """The immutable pool and lineage that may be persisted as a draft session."""

    readiness: DraftRoomReadiness
    players: tuple[FrozenDraftPlayer, ...]
    projection_run_id: str | None
    adp_build_fingerprint: str | None
    ruleset_fingerprint: str | None


@dataclass(frozen=True)
class DraftRoomSession:
    """One verified persisted session with its frozen player pool."""

    info: DraftSessionInfo
    state: DraftState
    players: tuple[FrozenDraftPlayer, ...]


def prepare_draft_room(
    projection_board: ProjectionBoard,
    adp_market_board: AdpMarketBoard,
    *,
    rules: LeagueRules,
    projection_reference_rules: LeagueRules,
    required_market_coverage: float = 1.0,
) -> DraftRoomPreparation:
    """Build a deterministic projection pool with canonical-ID-only market evidence.

    The supplied reference rules are the versioned rules that produced the active
    projection board. Their full fingerprint must match the board lineage. A session
    may change roster shape, team count, or draft slot, but its scoring inputs must
    remain identical to that verified reference.
    """

    if not 0 < required_market_coverage <= 1:
        raise ValueError("required_market_coverage must be greater than 0 and at most 1.")
    projection_run = projection_board.run
    if not projection_board.available or projection_run is None:
        return _unavailable_preparation(
            state_status="projection_board_unavailable",
            message=projection_board.status.message,
            required_market_coverage=required_market_coverage,
        )
    if (
        projection_run.lineage.scoring_ruleset_fingerprint
        != projection_reference_rules.fingerprint()
    ):
        return _unavailable_preparation(
            state_status="projection_reference_mismatch",
            message=(
                "The supplied projection reference rules do not match the active Phase 4 "
                "ruleset fingerprint."
            ),
            required_market_coverage=required_market_coverage,
            projection_run_id=projection_run.run_id,
        )
    if rules.scoring_fingerprint() != projection_reference_rules.scoring_fingerprint():
        return _unavailable_preparation(
            state_status="scoring_incompatible",
            message=(
                "The session scoring rules differ from the scoring used by the active player "
                "projections; rebuild the projection contract for this scoring format."
            ),
            required_market_coverage=required_market_coverage,
            projection_run_id=projection_run.run_id,
        )
    if rules.season != projection_run.prediction_season:
        return _unavailable_preparation(
            state_status="projection_season_mismatch",
            message=(
                f"Session season {rules.season} does not match projection season "
                f"{projection_run.prediction_season}."
            ),
            required_market_coverage=required_market_coverage,
            projection_run_id=projection_run.run_id,
        )
    if rules.draft.keepers:
        return _unavailable_preparation(
            state_status="keepers_not_supported",
            message="Phase 6 supports redraft sessions only; keeper placement is not implemented.",
            required_market_coverage=required_market_coverage,
            projection_run_id=projection_run.run_id,
        )

    projection_ids = [row.player_id.strip() for row in projection_board.rows]
    duplicate_projection_ids = tuple(
        sorted(player_id for player_id, count in Counter(projection_ids).items() if count > 1)
    )
    if duplicate_projection_ids:
        return _unavailable_preparation(
            state_status="duplicate_projection_player_ids",
            message=(
                "The projection board contains duplicate canonical player IDs: "
                f"{', '.join(duplicate_projection_ids)}."
            ),
            required_market_coverage=required_market_coverage,
            projection_run_id=projection_run.run_id,
        )
    if not projection_board.rows:
        return _unavailable_preparation(
            state_status="projection_pool_empty",
            message="The validated projection board contains no players.",
            required_market_coverage=required_market_coverage,
            projection_run_id=projection_run.run_id,
        )
    if any(row.prediction_season != rules.season for row in projection_board.rows):
        return _unavailable_preparation(
            state_status="projection_season_mismatch",
            message="At least one projection row is outside the session season.",
            required_market_coverage=required_market_coverage,
            projection_run_id=projection_run.run_id,
        )
    scoring_format = adp_scoring_format(rules)
    scoped_market = _compatible_market_rows(
        adp_market_board,
        season=rules.season,
        team_count=rules.teams,
        scoring_format=scoring_format,
    )
    projection_positions = {
        row.position.strip().upper() for row in projection_board.rows if row.position.strip()
    }
    rules_positions = set(rules.starters)
    rules_positions.update(
        position for slot in rules.flex_slots for position in slot.eligible
    )
    eligible_positions = projection_positions & rules_positions
    compatible_market = tuple(
        row for row in scoped_market if row.position.strip().upper() in eligible_positions
    )
    excluded_market = tuple(
        row for row in scoped_market if row.position.strip().upper() not in eligible_positions
    )
    mapped_rows = tuple(row for row in compatible_market if _canonical_market_id(row) is not None)
    mapped_ids = tuple(_required_canonical_market_id(row) for row in mapped_rows)
    duplicate_mapped_ids = tuple(
        sorted(player_id for player_id, count in Counter(mapped_ids).items() if count > 1)
    )
    projection_by_id = {row.player_id: row for row in projection_board.rows}
    unmatched_ids = tuple(sorted(set(mapped_ids) - set(projection_by_id)))
    conflicting_positions = tuple(
        sorted(
            {
                player_id
                for row in mapped_rows
                if (player_id := _required_canonical_market_id(row)) in projection_by_id
                and row.position.strip().upper()
                != projection_by_id[player_id].position.strip().upper()
            }
        )
    )

    unusable_ids = set(duplicate_mapped_ids) | set(unmatched_ids) | set(conflicting_positions)
    market_by_id = {
        _required_canonical_market_id(row): row
        for row in mapped_rows
        if _required_canonical_market_id(row) not in unusable_ids
    }
    players = tuple(
        _freeze_projection(row, market_by_id.get(row.player_id))
        for row in sorted(projection_board.rows, key=lambda item: item.player_id)
    )
    compatible_count = len(compatible_market)
    mapped_count = len(mapped_rows)
    readiness = _market_readiness(
        projection_rows=len(players),
        compatible_market_rows=compatible_count,
        excluded_market_rows=len(excluded_market),
        mapped_market_rows=mapped_count,
        matched_market_rows=sum(player.has_market_evidence for player in players),
        required_market_coverage=required_market_coverage,
        scoring_format=scoring_format,
        adp_market_board=adp_market_board,
        duplicate_mapped_ids=duplicate_mapped_ids,
        unmatched_ids=unmatched_ids,
        conflicting_positions=conflicting_positions,
        excluded_market_positions=tuple(
            sorted({row.position.strip().upper() for row in excluded_market})
        ),
    )
    return DraftRoomPreparation(
        readiness=readiness,
        players=players,
        projection_run_id=projection_run.run_id,
        adp_build_fingerprint=adp_market_board.status.build_fingerprint,
        ruleset_fingerprint=rules.fingerprint(),
    )


def create_draft_session(
    repository: DraftRepository,
    preparation: DraftRoomPreparation,
    *,
    session_name: str,
    rules: LeagueRules,
    user_draft_slot: int,
    engine_config: DraftEngineConfig,
    random_seed: int,
    simulation_count: int | None = None,
    session_id: str | None = None,
    command_id: str | None = None,
) -> DraftRoomSession:
    """Create a persisted session, including when only manual state is ready."""

    if not preparation.readiness.state_ready or preparation.projection_run_id is None:
        raise DraftRoomServiceError(preparation.readiness.state_message)
    if preparation.ruleset_fingerprint != rules.fingerprint():
        raise DraftRoomServiceError(
            "The session rules differ from the rules used to validate this draft-room preparation."
        )
    actual_simulations = (
        engine_config.default_simulations if simulation_count is None else simulation_count
    )
    if not 1 <= actual_simulations <= engine_config.maximum_simulations:
        raise DraftRoomServiceError(
            f"simulation_count must be between 1 and {engine_config.maximum_simulations}."
        )
    created_state = repository.create_session(
        session_name=session_name,
        rules=rules,
        user_draft_slot=user_draft_slot,
        projection_run_id=preparation.projection_run_id,
        adp_build_fingerprint=preparation.adp_build_fingerprint,
        players=preparation.players,
        engine_config_fingerprint=engine_config.fingerprint(),
        recommendation_status=preparation.readiness.recommendation_status,
        recommendation_message=preparation.readiness.recommendation_message,
        random_seed=random_seed,
        simulation_count=actual_simulations,
        session_id=session_id,
        command_id=command_id,
    )
    return load_draft_session(repository, created_state.session_id)


def load_draft_session(repository: DraftRepository, session_id: str) -> DraftRoomSession:
    """Replay and verify a persisted session before exposing it to a caller."""

    state = repository.verify_session(session_id)
    return DraftRoomSession(
        info=repository.session_info(session_id),
        state=state,
        players=repository.load_players(session_id),
    )


def record_draft_pick(
    repository: DraftRepository,
    session_id: str,
    player_id: str,
    *,
    expected_version: int,
    command_id: str | None = None,
) -> DraftRoomSession:
    """Append one canonical-player pick and return verified replayed state."""

    repository.record_pick(
        session_id,
        player_id,
        expected_version=expected_version,
        command_id=command_id,
    )
    return load_draft_session(repository, session_id)


def undo_draft_pick(
    repository: DraftRepository,
    session_id: str,
    *,
    expected_version: int,
    command_id: str | None = None,
) -> DraftRoomSession:
    """Append an undo for the latest active pick and return verified state."""

    repository.undo_last(
        session_id,
        expected_version=expected_version,
        command_id=command_id,
    )
    return load_draft_session(repository, session_id)


def replace_draft_pick(
    repository: DraftRepository,
    session_id: str,
    overall_pick: int,
    player_id: str,
    *,
    expected_version: int,
    command_id: str | None = None,
) -> DraftRoomSession:
    """Append a canonical-player replacement and return verified state."""

    repository.replace_pick(
        session_id,
        overall_pick,
        player_id,
        expected_version=expected_version,
        command_id=command_id,
    )
    return load_draft_session(repository, session_id)


def adp_scoring_format(rules: LeagueRules) -> str | None:
    """Return the documented FFC-style market scope for supported redraft rules."""

    if rules.starters.get("QB", 0) >= 2 or any("QB" in slot.eligible for slot in rules.flex_slots):
        return "2-qb"
    scoring = rules.scoring
    if scoring.position_reception_bonus or scoring.yardage_bonuses:
        return None
    reception = float(scoring.reception)
    if isclose(reception, 0.0, abs_tol=1e-9):
        return "standard"
    if isclose(reception, 0.5, abs_tol=1e-9):
        return "half-ppr"
    if isclose(reception, 1.0, abs_tol=1e-9):
        return "ppr"
    return None


def _freeze_projection(
    projection: PlayerProjection,
    market: AdpMarketRow | None,
) -> FrozenDraftPlayer:
    interval = projection.target(TARGET_FANTASY_POINTS_TOTAL)
    return FrozenDraftPlayer(
        player_id=projection.player_id,
        display_name=projection.display_name,
        position=projection.position,
        p10=interval.p10,
        p50=interval.p50,
        p90=interval.p90,
        prediction_status=projection.prediction_status,
        projection_source=interval.selected_source,
        projection_method=interval.selected_name,
        market_source=None if market is None else market.source,
        market_snapshot_id=None if market is None else market.snapshot_id,
        market_captured_at=None if market is None else market.captured_at,
        average_pick=None if market is None else market.average_pick,
        availability_scale=None if market is None else market.availability_scale,
        availability_evidence=(None if market is None else market.availability_evidence_method),
        mapping_confidence=None if market is None else market.mapping_confidence,
    )


def _compatible_market_rows(
    board: AdpMarketBoard,
    *,
    season: int,
    team_count: int,
    scoring_format: str | None,
) -> tuple[AdpMarketRow, ...]:
    if not board.available or scoring_format is None:
        return ()
    normalized_format = scoring_format.casefold()
    return tuple(
        row
        for row in board.rows
        if row.season == season
        and row.team_count == team_count
        and row.scoring_format.casefold() == normalized_format
    )


def _canonical_market_id(row: AdpMarketRow) -> str | None:
    value = row.identity.player_id
    if value is None or not value.strip():
        return None
    if row.mapping_confidence.strip().casefold() in {"unresolved", "pending", "none"}:
        return None
    return value.strip()


def _required_canonical_market_id(row: AdpMarketRow) -> str:
    value = _canonical_market_id(row)
    if value is None:
        raise ValueError("A mapped market row requires reviewed canonical identity evidence.")
    return value


def _market_readiness(
    *,
    projection_rows: int,
    compatible_market_rows: int,
    excluded_market_rows: int,
    mapped_market_rows: int,
    matched_market_rows: int,
    required_market_coverage: float,
    scoring_format: str | None,
    adp_market_board: AdpMarketBoard,
    duplicate_mapped_ids: tuple[str, ...],
    unmatched_ids: tuple[str, ...],
    conflicting_positions: tuple[str, ...],
    excluded_market_positions: tuple[str, ...],
) -> DraftRoomReadiness:
    coverage = mapped_market_rows / compatible_market_rows if compatible_market_rows else 0.0
    status = RECOMMENDATION_READY
    message = (
        f"Canonical market evidence is ready for {matched_market_rows} projection players "
        f"({mapped_market_rows}/{compatible_market_rows} compatible rows mapped)."
    )
    if not adp_market_board.available:
        status = "adp_market_unavailable"
        message = adp_market_board.status.message
    elif scoring_format is None:
        status = "unsupported_adp_scoring_scope"
        message = "The session scoring has no supported redraft ADP scope."
    elif not compatible_market_rows:
        status = "compatible_adp_scope_required"
        message = "No ADP rows match the session season, team count, and scoring scope."
    elif duplicate_mapped_ids:
        status = "duplicate_mapped_player_ids"
        message = (
            "Multiple compatible market rows map to the same canonical player IDs: "
            f"{', '.join(duplicate_mapped_ids)}."
        )
    elif unmatched_ids:
        status = "mapped_projection_required"
        message = (
            "Mapped ADP identities are absent from the projection board: "
            f"{', '.join(unmatched_ids)}."
        )
    elif conflicting_positions:
        status = "mapped_position_conflict"
        message = (
            f"Mapped ADP and projection positions conflict for: {', '.join(conflicting_positions)}."
        )
    elif coverage < required_market_coverage:
        status = IDENTITY_MAPPING_REQUIRED
        message = (
            "Canonical ADP identity mapping is required: "
            f"{mapped_market_rows}/{compatible_market_rows} compatible rows are mapped "
            f"({coverage:.1%}; required {required_market_coverage:.1%})."
        )
    if excluded_market_rows:
        positions = ", ".join(excluded_market_positions)
        message += (
            f" {excluded_market_rows} source rows ({positions}) remain archived and auditable "
            "but are outside this ruleset's projected draftable-position coverage."
        )
    return DraftRoomReadiness(
        state_ready=True,
        recommendation_ready=status == RECOMMENDATION_READY,
        state_status=STATE_READY,
        recommendation_status=status,
        state_message=(
            f"Manual event-sourced draft state is ready with {projection_rows} canonical players."
        ),
        recommendation_message=message,
        projection_rows=projection_rows,
        compatible_market_rows=compatible_market_rows,
        excluded_market_rows=excluded_market_rows,
        mapped_market_rows=mapped_market_rows,
        matched_market_rows=matched_market_rows,
        unresolved_market_rows=compatible_market_rows - mapped_market_rows,
        market_coverage=coverage,
        required_market_coverage=required_market_coverage,
        scoring_format=scoring_format,
        duplicate_mapped_player_ids=duplicate_mapped_ids,
        unmatched_mapped_player_ids=unmatched_ids,
        conflicting_position_player_ids=conflicting_positions,
        excluded_market_positions=excluded_market_positions,
    )


def _unavailable_preparation(
    *,
    state_status: str,
    message: str,
    required_market_coverage: float,
    projection_run_id: str | None = None,
) -> DraftRoomPreparation:
    readiness = DraftRoomReadiness(
        state_ready=False,
        recommendation_ready=False,
        state_status=state_status,
        recommendation_status=state_status,
        state_message=message,
        recommendation_message=message,
        projection_rows=0,
        compatible_market_rows=0,
        excluded_market_rows=0,
        mapped_market_rows=0,
        matched_market_rows=0,
        unresolved_market_rows=0,
        market_coverage=0.0,
        required_market_coverage=required_market_coverage,
        scoring_format=None,
    )
    return DraftRoomPreparation(
        readiness=readiness,
        players=(),
        projection_run_id=projection_run_id,
        adp_build_fingerprint=None,
        ruleset_fingerprint=None,
    )
