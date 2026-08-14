"""Presentation-ready draft-board rows derived from frozen Phase 6 state."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Literal

from fantasy_draft_ai.draft.pool import FrozenDraftPlayer
from fantasy_draft_ai.draft.state import DraftState
from fantasy_draft_ai.models.adp.availability import conditional_normal_availability

RiskLabel = Literal["low", "medium", "high", "not_estimated"]
MethodKind = Literal["learned", "transparent_baseline", "heuristic"]


@dataclass(frozen=True)
class DraftBoardRow:
    """One frozen player enriched with transparent UI-only board attributes."""

    player_id: str
    display_name: str
    position: str
    overall_rank: int
    position_rank: int
    tier: int
    risk: RiskLabel
    method_kind: MethodKind
    available: bool
    p10: float
    p50: float
    p90: float
    average_pick: float | None
    adp_value_at_current_pick: float | None
    probability_gone_before_user_pick: float | None
    mapping_confidence: str | None
    projection_status: str
    projection_method: str

    def as_dict(self) -> dict[str, Any]:
        return {
            "player_id": self.player_id,
            "display_name": self.display_name,
            "position": self.position,
            "overall_rank": self.overall_rank,
            "position_rank": self.position_rank,
            "tier": self.tier,
            "risk": self.risk,
            "method_kind": self.method_kind,
            "available": self.available,
            "p10": self.p10,
            "p50": self.p50,
            "p90": self.p90,
            "average_pick": self.average_pick,
            "adp_value_at_current_pick": self.adp_value_at_current_pick,
            "probability_gone_before_user_pick": self.probability_gone_before_user_pick,
            "mapping_confidence": self.mapping_confidence,
            "projection_status": self.projection_status,
            "projection_method": self.projection_method,
        }


def build_draft_board(
    state: DraftState,
    players: tuple[FrozenDraftPlayer, ...] | list[FrozenDraftPlayer],
) -> tuple[DraftBoardRow, ...]:
    """Return deterministic ranks, tiers, risk labels, and next-user-pick pressure.

    Tiers are ruleset-aware rank bands: one tier contains one league-wide team count
    at a position. This is a transparent navigation aid, not a learned clustering model.
    """

    pool = tuple(sorted(players, key=lambda player: (-player.p50, player.player_id)))
    if len({player.player_id for player in pool}) != len(pool):
        raise ValueError("Draft-board players must have unique canonical IDs.")
    position_ranks: dict[str, int] = {}
    next_user_pick = state.next_user_pick(include_current=not state.is_user_turn)
    current_pick = state.current_overall_pick
    rows: list[DraftBoardRow] = []
    for overall_rank, player in enumerate(pool, start=1):
        position_rank = position_ranks.get(player.position, 0) + 1
        position_ranks[player.position] = position_rank
        rows.append(
            DraftBoardRow(
                player_id=player.player_id,
                display_name=player.display_name,
                position=player.position,
                overall_rank=overall_rank,
                position_rank=position_rank,
                tier=(position_rank - 1) // state.rules.teams + 1,
                risk=_risk_label(player),
                method_kind=_method_kind(player),
                available=player.player_id not in state.selected_player_ids,
                p10=player.p10,
                p50=player.p50,
                p90=player.p90,
                average_pick=(
                    player.average_pick if player.has_mapped_market_evidence else None
                ),
                adp_value_at_current_pick=(
                    None
                    if current_pick is None
                    or not player.has_mapped_market_evidence
                    or player.average_pick is None
                    else float(current_pick) - player.average_pick
                ),
                probability_gone_before_user_pick=_probability_gone(
                    player,
                    current_pick=current_pick,
                    next_user_pick=next_user_pick,
                ),
                mapping_confidence=player.mapping_confidence,
                projection_status=player.prediction_status,
                projection_method=player.projection_method,
            )
        )
    return tuple(rows)


def _risk_label(player: FrozenDraftPlayer) -> RiskLabel:
    if not player.has_outcome_interval:
        return "not_estimated"
    relative_width = (player.p90 - player.p10) / max(abs(player.p50), 1.0)
    if relative_width >= 0.5:
        return "high"
    if relative_width >= 0.25:
        return "medium"
    return "low"


def _method_kind(player: FrozenDraftPlayer) -> MethodKind:
    status = player.prediction_status.casefold()
    source = player.projection_source.casefold()
    if "rookie" in status or "heuristic" in status or "fallback" in status:
        return "heuristic"
    if source == "learned" or "learned" in status:
        return "learned"
    return "transparent_baseline"


def _probability_gone(
    player: FrozenDraftPlayer,
    *,
    current_pick: int | None,
    next_user_pick: int | None,
) -> float | None:
    if (
        current_pick is None
        or next_user_pick is None
        or not player.has_mapped_market_evidence
        or player.average_pick is None
        or player.availability_scale is None
    ):
        return None
    if next_user_pick <= current_pick:
        return None
    probability_available = conditional_normal_availability(
        average_pick=player.average_pick,
        current_pick=float(current_pick),
        next_pick=float(next_user_pick),
        standard_deviation=player.availability_scale,
    )
    return 1.0 - probability_available
