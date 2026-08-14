"""Ruleset-aware pick guidance that remains usable without ADP evidence."""

from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass

import pandas as pd

from fantasy_draft_ai.draft.pool import FrozenDraftPlayer, player_pool_fingerprint
from fantasy_draft_ai.draft.repository import DraftRepository
from fantasy_draft_ai.draft.roster import RosterPlayer, assign_roster
from fantasy_draft_ai.draft.state import DraftState
from fantasy_draft_ai.models.adp.availability import conditional_normal_availability
from fantasy_draft_ai.recommendations.config import (
    DraftEngineConfig,
    ProjectionGuidanceConfig,
)
from fantasy_draft_ai.recommendations.models import (
    ProjectionPickCandidate,
    ProjectionRecommendationResult,
)
from fantasy_draft_ai.rules.models import LeagueRules
from fantasy_draft_ai.rules.replacement import replacement_levels


@dataclass(frozen=True)
class ProjectionRankingRow:
    """A pre-draft player rank based on league-specific replacement value."""

    player_id: str
    display_name: str
    position: str
    overall_rank: int
    position_rank: int
    tier: int
    p10: float
    p50: float
    p90: float
    replacement_points: float
    p50_vorp: float
    risk: str
    average_pick: float | None


@dataclass(frozen=True)
class _ScoredCandidate:
    player: FrozenDraftPlayer
    decision_score: float
    p50_vorp: float
    scarcity: float
    roster_fit: float
    fills_open_starter: bool
    improves_starting_lineup: bool
    starting_lineup_gain: float


def build_projection_rankings(
    rules: LeagueRules,
    players: Sequence[FrozenDraftPlayer],
) -> tuple[ProjectionRankingRow, ...]:
    """Rank draftable players by P50 value over a stable replacement line."""

    pool = _validated_pool(players)
    replacement = _replacement_by_position(pool, rules)
    draftable = [player for player in pool if replacement.get(player.position) is not None]
    position_order = {
        player.player_id: rank
        for position in sorted({player.position for player in draftable})
        for rank, player in enumerate(
            sorted(
                (item for item in draftable if item.position == position),
                key=lambda item: (-item.p50, item.player_id),
            ),
            start=1,
        )
    }
    ordered = sorted(
        draftable,
        key=lambda player: (
            -(player.p50 - replacement[player.position]),
            -player.p50,
            player.player_id,
        ),
    )
    return tuple(
        ProjectionRankingRow(
            player_id=player.player_id,
            display_name=player.display_name,
            position=player.position,
            overall_rank=overall_rank,
            position_rank=position_order[player.player_id],
            tier=(position_order[player.player_id] - 1) // rules.teams + 1,
            p10=player.p10,
            p50=player.p50,
            p90=player.p90,
            replacement_points=replacement[player.position],
            p50_vorp=player.p50 - replacement[player.position],
            risk=_risk_label(player),
            average_pick=(player.average_pick if player.has_mapped_market_evidence else None),
        )
        for overall_rank, player in enumerate(ordered, start=1)
    )


def rank_best_available(
    state: DraftState,
    players: Sequence[FrozenDraftPlayer],
    config: DraftEngineConfig,
    guidance_config: ProjectionGuidanceConfig,
    *,
    limit: int = 10,
) -> ProjectionRecommendationResult:
    """Return deterministic best-pick guidance from projections and current roster state.

    ADP can enrich the displayed timing context, but it never changes this baseline's
    ordering. The stricter simulation-backed recommendation engine remains a separate API.
    """

    if limit < 1:
        raise ValueError("limit must be positive.")
    if state.engine_config_fingerprint != config.fingerprint():
        return _unavailable(
            state,
            guidance_config,
            code="engine_config_mismatch",
            message="This draft was created with a different recommendation configuration.",
        )
    if state.current_overall_pick is None:
        return _unavailable(
            state,
            guidance_config,
            code="draft_complete",
            message="The draft is complete.",
        )
    if not state.is_user_turn:
        return _unavailable(
            state,
            guidance_config,
            code="not_user_turn",
            message="Record picks until your team is on the clock to see the best pick now.",
        )
    try:
        pool = _validated_pool(players)
        supplied_pool_fingerprint = player_pool_fingerprint(pool)
    except ValueError as exc:
        return _unavailable(
            state,
            guidance_config,
            code="invalid_player_pool",
            message=str(exc),
        )
    if supplied_pool_fingerprint != state.player_pool_fingerprint:
        return _unavailable(
            state,
            guidance_config,
            code="player_pool_mismatch",
            message="The supplied player pool does not match this frozen draft session.",
        )

    rankings = build_projection_rankings(state.rules, pool)
    ranking_by_id = {row.player_id: row for row in rankings}
    replacement = _replacement_by_position(pool, state.rules)
    available = tuple(
        player for player in pool if player.player_id not in state.selected_player_ids
    )
    user_roster = tuple(
        RosterPlayer(pick.player_id, pick.position, pick.projected_points)
        for pick in state.roster(state.user_draft_slot)
    )
    current_assignment = assign_roster(user_roster, state.rules)
    next_user_pick = state.next_user_pick(include_current=False)
    scored: list[_ScoredCandidate] = []
    for player in available:
        baseline = replacement.get(player.position)
        ranking = ranking_by_id.get(player.player_id)
        if baseline is None or ranking is None:
            continue
        after = assign_roster(
            (*user_roster, RosterPlayer(player.player_id, player.position, player.p50)),
            state.rules,
        )
        if not after.legal:
            continue
        prior_coverage = current_assignment.starter_coverage
        coverage_gain = max(0.0, float(after.starter_coverage) - prior_coverage)
        starts_after_pick = after.slot_for_player(player.player_id) not in {None, "BENCH"}
        fills_open_starter = starts_after_pick and coverage_gain > 0.0
        starter_value_gain = max(
            0.0,
            float(after.starter_value) - float(current_assignment.starter_value),
        )
        improves_starting_lineup = (
            starts_after_pick
            and not fills_open_starter
            and starter_value_gain > 1e-9
        )
        starting_lineup_gain = starter_value_gain if improves_starting_lineup else 0.0
        starter_fit_bonus = guidance_config.open_starter_bonus if fills_open_starter else 0.0
        roster_fit = coverage_gain + starter_fit_bonus
        scarcity = _scarcity_after(player, available)
        vorp = player.p50 - baseline
        # Replacement value is the primary cross-position signal. Scarcity is a
        # conservative tier-drop adjustment because, without linked ADP, the next
        # same-position player is not guaranteed to be the user's next alternative.
        decision_score = (
            vorp
            + guidance_config.scarcity_weight * scarcity
            + guidance_config.roster_fit_weight * roster_fit
            + guidance_config.lineup_improvement_weight * starting_lineup_gain
        )
        scored.append(
            _ScoredCandidate(
                player=player,
                decision_score=decision_score,
                p50_vorp=vorp,
                scarcity=scarcity,
                roster_fit=roster_fit,
                fills_open_starter=fills_open_starter,
                improves_starting_lineup=improves_starting_lineup,
                starting_lineup_gain=starting_lineup_gain,
            )
        )
    scored.sort(
        key=lambda item: (
            -item.decision_score,
            -item.p50_vorp,
            -item.player.p50,
            item.player.player_id,
        )
    )

    candidates: list[ProjectionPickCandidate] = []
    for scored_candidate in scored[:limit]:
        player = scored_candidate.player
        ranking = ranking_by_id[player.player_id]
        probability = _probability_available_next_pick(
            player,
            current_pick=state.current_overall_pick,
            next_user_pick=next_user_pick,
        )
        reasons = [
            f"Projects {scored_candidate.p50_vorp:.1f} points above the "
            f"{player.position} replacement level.",
        ]
        if scored_candidate.fills_open_starter:
            reasons.append("Fits an open starter or flex spot on your roster.")
        elif scored_candidate.improves_starting_lineup:
            reasons.append("Projects to improve one of your current starting spots.")
        if scored_candidate.scarcity > 0:
            reasons.append(
                f"The next available {player.position} projects "
                f"{scored_candidate.scarcity:.1f} points lower."
            )
        if probability is not None:
            reasons.append(
                f"Market data estimates a {probability:.0%} chance of lasting to your next pick."
            )
        candidates.append(
            ProjectionPickCandidate(
                player_id=player.player_id,
                display_name=player.display_name,
                position=player.position,
                overall_rank=ranking.overall_rank,
                position_rank=ranking.position_rank,
                tier=ranking.tier,
                p10=player.p10,
                p50=player.p50,
                p90=player.p90,
                replacement_points=ranking.replacement_points,
                p50_vorp=scored_candidate.p50_vorp,
                scarcity=scored_candidate.scarcity,
                roster_fit=scored_candidate.roster_fit,
                fills_open_starter=scored_candidate.fills_open_starter,
                improves_starting_lineup=scored_candidate.improves_starting_lineup,
                starting_lineup_gain=scored_candidate.starting_lineup_gain,
                decision_score=scored_candidate.decision_score,
                risk=ranking.risk,
                reasons=tuple(reasons),
                current_adp=(
                    player.average_pick if player.has_mapped_market_evidence else None
                ),
                probability_available_next_pick=probability,
                market_source=(
                    player.market_source if player.has_mapped_market_evidence else None
                ),
                market_captured_at=(
                    player.market_captured_at.isoformat()
                    if player.has_mapped_market_evidence
                    and player.market_captured_at is not None
                    else None
                ),
            )
        )
    if not candidates:
        return _unavailable(
            state,
            guidance_config,
            code="no_legal_candidates",
            message="No legal projected player is available for your remaining roster space.",
        )
    return ProjectionRecommendationResult(
        available=True,
        code="projection_guidance_ready",
        message=(
            "Best-pick guidance is ready from league-adjusted projections, replacement value, "
            "positional drop-off, and your roster needs."
        ),
        session_id=state.session_id,
        session_version=state.version,
        state_fingerprint=state.fingerprint(),
        projection_run_id=state.projection_run_id,
        player_pool_fingerprint=state.player_pool_fingerprint,
        engine_config_fingerprint=state.engine_config_fingerprint,
        guidance_version=guidance_config.version,
        guidance_config_fingerprint=guidance_config.fingerprint(),
        candidates=tuple(candidates),
        limitations=(
            f"{guidance_config.version} is a transparent uncalibrated baseline, not a win "
            "probability.",
            "Market timing is shown only for canonically linked ADP rows and never changes the "
            "projection-only order.",
            "Current projections do not include live injury, suspension, or depth-chart news.",
        ),
    )


def rank_best_available_for_session(
    repository: DraftRepository,
    session_id: str,
    config: DraftEngineConfig,
    guidance_config: ProjectionGuidanceConfig,
    *,
    limit: int = 10,
) -> ProjectionRecommendationResult:
    """Verify a frozen session and return projection-first guidance without persisting it."""

    state = repository.verify_session(session_id)
    players = repository.load_players(session_id)
    return rank_best_available(state, players, config, guidance_config, limit=limit)


def _validated_pool(players: Sequence[FrozenDraftPlayer]) -> tuple[FrozenDraftPlayer, ...]:
    pool = tuple(sorted(players, key=lambda player: player.player_id))
    if len({player.player_id for player in pool}) != len(pool):
        raise ValueError("The frozen player pool contains duplicate canonical IDs.")
    return pool


def _replacement_by_position(
    players: tuple[FrozenDraftPlayer, ...],
    rules: LeagueRules,
) -> dict[str, float]:
    frame = pd.DataFrame.from_records(
        {
            "player_id": player.player_id,
            "position": player.position,
            "projected_points": player.p50,
        }
        for player in players
    )
    if frame.empty:
        return {}
    return {
        position: float(level.last_starter_points)
        for position, level in replacement_levels(frame, rules).items()
        if level.last_starter_points is not None
    }


def _scarcity_after(
    candidate: FrozenDraftPlayer,
    available: tuple[FrozenDraftPlayer, ...],
) -> float:
    position_players = sorted(
        (player for player in available if player.position == candidate.position),
        key=lambda player: (-player.p50, player.player_id),
    )
    index = next(
        (
            offset
            for offset, player in enumerate(position_players)
            if player.player_id == candidate.player_id
        ),
        None,
    )
    if index is None or index + 1 >= len(position_players):
        return 0.0
    return max(0.0, candidate.p50 - position_players[index + 1].p50)


def _risk_label(player: FrozenDraftPlayer) -> str:
    if not player.has_outcome_interval:
        return "not estimated"
    relative_width = (player.p90 - player.p10) / max(abs(player.p50), 1.0)
    if relative_width >= 0.5:
        return "high"
    if relative_width >= 0.25:
        return "medium"
    return "low"


def _probability_available_next_pick(
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
    return conditional_normal_availability(
        average_pick=player.average_pick,
        current_pick=float(current_pick),
        next_pick=float(next_user_pick),
        standard_deviation=player.availability_scale,
    )


def _unavailable(
    state: DraftState,
    guidance_config: ProjectionGuidanceConfig,
    *,
    code: str,
    message: str,
) -> ProjectionRecommendationResult:
    return ProjectionRecommendationResult(
        available=False,
        code=code,
        message=message,
        session_id=state.session_id,
        session_version=state.version,
        state_fingerprint=state.fingerprint(),
        projection_run_id=state.projection_run_id,
        player_pool_fingerprint=state.player_pool_fingerprint,
        engine_config_fingerprint=state.engine_config_fingerprint,
        guidance_version=guidance_config.version,
        guidance_config_fingerprint=guidance_config.fingerprint(),
        limitations=(
            "No market availability, simulation, or win probability is invented.",
        ),
    )
