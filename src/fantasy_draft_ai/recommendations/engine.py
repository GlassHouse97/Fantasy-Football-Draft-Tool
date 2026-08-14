"""Ruleset-aware candidate comparison over deterministic rest-of-draft paths."""

from __future__ import annotations

from dataclasses import dataclass
from math import isclose

import pandas as pd

from fantasy_draft_ai.draft.pool import FrozenDraftPlayer
from fantasy_draft_ai.draft.repository import DraftRepository
from fantasy_draft_ai.draft.roster import RosterAssignment, RosterPlayer, assign_roster
from fantasy_draft_ai.draft.state import DraftState
from fantasy_draft_ai.models.adp.availability import normal_survival
from fantasy_draft_ai.recommendations.config import DraftEngineConfig, RoleWeights
from fantasy_draft_ai.recommendations.models import (
    RecommendationComponent,
    RecommendationResult,
    RecommendationRole,
    RecommendedPlayer,
)
from fantasy_draft_ai.rules.replacement import replacement_levels
from fantasy_draft_ai.simulation import (
    DraftSimulationResult,
    SimulationInputError,
    simulate_rest_of_draft,
)


@dataclass(frozen=True)
class _CandidateMetrics:
    player: FrozenDraftPlayer
    replacement_points: float
    p50_vorp: float
    floor_vorp: float | None
    ceiling_vorp: float | None
    scarcity: float
    gone_probability: float
    roster_fit: float
    risk_penalty: float | None
    simulation: DraftSimulationResult

    def raw_components(self) -> dict[str, float | None]:
        return {
            "p50_vorp": self.p50_vorp,
            "floor_vorp": self.floor_vorp,
            "ceiling_vorp": self.ceiling_vorp,
            "scarcity": self.scarcity,
            "gone_probability": self.gone_probability,
            "roster_fit": self.roster_fit,
            "simulation_mean": self.simulation.mean_final_roster_value,
            "simulation_floor": self.simulation.p10_final_roster_value,
            "simulation_ceiling": self.simulation.p90_final_roster_value,
            "risk_penalty": self.risk_penalty,
        }


def recommend_for_session(
    repository: DraftRepository,
    session_id: str,
    config: DraftEngineConfig,
) -> RecommendationResult:
    """Verify frozen inputs, generate a result, and persist its deterministic payload."""

    state = repository.verify_session(session_id)
    info = repository.session_info(session_id)
    players = repository.load_players(session_id)
    if info.recommendation_status != "recommendation_ready":
        return _unavailable(
            state,
            code=info.recommendation_status,
            message=info.recommendation_message,
        )
    result = generate_recommendations(state, players, config)
    if result.available:
        fingerprint = result.fingerprint()
        repository.save_recommendation(
            recommendation_run_id=f"recommendation-{fingerprint[:20]}",
            session_id=session_id,
            state=state,
            engine_config_fingerprint=config.fingerprint(),
            random_seed=state.random_seed,
            simulation_count=state.simulation_count,
            status=result.code,
            result_fingerprint=fingerprint,
            result_payload=result.as_dict(),
        )
    return result


def generate_recommendations(
    state: DraftState,
    players: tuple[FrozenDraftPlayer, ...] | list[FrozenDraftPlayer],
    config: DraftEngineConfig,
) -> RecommendationResult:
    """Return balanced, floor, and upside baseline recommendations.

    This is an optimization baseline over upstream model outputs and explicit simulation
    assumptions. It is never described as a championship or calibrated win probability.
    """

    pool = tuple(sorted(players, key=lambda player: player.player_id))
    if state.engine_config_fingerprint != config.fingerprint():
        return _unavailable(
            state,
            code="engine_config_mismatch",
            message="The session does not match the supplied recommendation configuration.",
        )
    if not state.is_user_turn:
        return _unavailable(
            state,
            code="not_user_turn",
            message="Recommendations are available only while the user's team is on the clock.",
        )
    if state.current_overall_pick is None:
        return _unavailable(state, code="draft_complete", message="The draft is complete.")
    if len({player.player_id for player in pool}) != len(pool):
        return _unavailable(
            state,
            code="duplicate_player_ids",
            message="The frozen player pool contains duplicate canonical IDs.",
        )

    replacement = _replacement_by_position(pool, state)
    available = tuple(
        player for player in pool if player.player_id not in state.selected_player_ids
    )
    user_roster = [
        pick for pick in state.picks if pick.draft_slot == state.user_draft_slot
    ]
    current_assignment = assign_roster(
        [
            RosterPlayer(pick.player_id, pick.position, pick.projected_points)
            for pick in user_roster
        ],
        state.rules,
    )
    next_user_pick = state.next_user_pick(include_current=False)
    premetrics: list[tuple[float, FrozenDraftPlayer, float, float, float, float]] = []
    for player in available:
        baseline = replacement.get(player.position)
        if baseline is None or not player.has_mapped_market_evidence:
            continue
        after = assign_roster(
            [
                *(
                    RosterPlayer(pick.player_id, pick.position, pick.projected_points)
                    for pick in user_roster
                ),
                RosterPlayer(player.player_id, player.position, player.p50),
            ],
            state.rules,
        )
        if not after.legal:
            continue
        fit = _roster_fit(current_assignment.starter_coverage, after, player.player_id)
        scarcity = _scarcity_after(player, available)
        gone = _gone_probability(state, player, next_user_pick)
        vorp = player.p50 - baseline
        prescore = vorp + 0.5 * scarcity + 40.0 * gone + 25.0 * fit
        premetrics.append((prescore, player, baseline, scarcity, gone, fit))
    premetrics.sort(key=lambda item: (-item[0], item[1].player_id))
    shortlist = premetrics[: config.candidate_count]
    if len(shortlist) < 3:
        return _unavailable(
            state,
            code="insufficient_mapped_candidates",
            message="At least three legal, canonically mapped candidates are required.",
        )

    metrics: list[_CandidateMetrics] = []
    try:
        for _, player, baseline, scarcity, gone, fit in shortlist:
            simulation = simulate_rest_of_draft(state, pool, player.player_id, config)
            metrics.append(
                _CandidateMetrics(
                    player=player,
                    replacement_points=baseline,
                    p50_vorp=player.p50 - baseline,
                    floor_vorp=(player.p10 - baseline if player.has_outcome_interval else None),
                    ceiling_vorp=(player.p90 - baseline if player.has_outcome_interval else None),
                    scarcity=scarcity,
                    gone_probability=gone,
                    roster_fit=fit,
                    risk_penalty=(player.p90 - player.p10 if player.has_outcome_interval else None),
                    simulation=simulation,
                )
            )
    except SimulationInputError as exc:
        return _unavailable(
            state,
            code="market_simulation_unavailable",
            message=str(exc),
        )

    normalized = _normalize_components(metrics)
    role_specs: tuple[tuple[RecommendationRole, RoleWeights], ...] = (
        ("balanced", config.balanced),
        ("safe_floor", config.safe_floor),
        ("high_upside", config.high_upside),
    )
    selected: list[RecommendedPlayer] = []
    used_ids: set[str] = set()
    for role, weights in role_specs:
        ranked: list[tuple[float, _CandidateMetrics, tuple[RecommendationComponent, ...]]] = []
        for candidate in metrics:
            components = _weighted_components(candidate, normalized, weights)
            if components is None:
                continue
            score = max(
                0.0,
                min(100.0, 100.0 * sum(item.weighted_contribution for item in components)),
            )
            ranked.append((score, candidate, components))
        ranked.sort(key=lambda item: (-item[0], item[1].player.player_id))
        choice = next((item for item in ranked if item[1].player.player_id not in used_ids), None)
        if choice is None:
            return _unavailable(
                state,
                code="insufficient_role_evidence",
                message=(
                    "Three distinct candidates with measured floor, median, ceiling, and risk "
                    "evidence are required. Point-only rows are not treated as safe."
                ),
            )
        score, candidate, components = choice
        used_ids.add(candidate.player.player_id)
        selected.append(_recommended_player(role, candidate, components, score))

    return RecommendationResult(
        available=True,
        code="recommendation_ready",
        message=(
            "Three deterministic baseline recommendations are available; component weights "
            "and Monte Carlo assumptions are versioned and uncalibrated."
        ),
        session_id=state.session_id,
        session_version=state.version,
        state_fingerprint=state.fingerprint(),
        projection_run_id=state.projection_run_id,
        adp_build_fingerprint=state.adp_build_fingerprint,
        player_pool_fingerprint=state.player_pool_fingerprint,
        engine_config_fingerprint=state.engine_config_fingerprint,
        random_seed=state.random_seed,
        simulation_count=state.simulation_count,
        candidates=tuple(selected),
        limitations=(
            "The recommendation score is an arbitrary transparent baseline, not a learned "
            "team-outcome or championship probability.",
            "ADP availability and opponent-pick assumptions are not calibrated to linked drafts.",
            "Player outcomes are sampled independently; cross-player correlations are absent.",
            "Point-only projection rows remain deterministic and are not labeled low risk.",
        ),
    )


def _replacement_by_position(
    players: tuple[FrozenDraftPlayer, ...],
    state: DraftState,
) -> dict[str, float]:
    """Freeze replacement levels to the session's complete player pool.

    Removing drafted players while retaining full-league starter demand would push the
    replacement line artificially deeper after every pick. Callers therefore supply the
    immutable session pool, matching the baseline used by rest-of-draft simulation.
    """

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
    levels = replacement_levels(frame, state.rules)
    return {
        position: float(level.last_starter_points)
        for position, level in levels.items()
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


def _roster_fit(
    prior_coverage: float,
    after: RosterAssignment,
    candidate_id: str,
) -> float:
    coverage_gain = max(0.0, float(after.starter_coverage) - prior_coverage)
    starter_bonus = 1.0 if after.slot_for_player(candidate_id) not in {None, "BENCH"} else 0.0
    return coverage_gain + 0.25 * starter_bonus


def _gone_probability(
    state: DraftState,
    player: FrozenDraftPlayer,
    next_user_pick: int | None,
) -> float:
    current = state.current_overall_pick
    if current is None or next_user_pick is None or next_user_pick <= current + 1:
        return 0.0
    if player.average_pick is None or player.availability_scale is None:
        raise ValueError("Mapped market evidence is required for next-pick availability.")
    lower = normal_survival(
        current + 0.5,
        mean=player.average_pick,
        standard_deviation=player.availability_scale,
    )
    upper = normal_survival(
        next_user_pick - 0.5,
        mean=player.average_pick,
        standard_deviation=player.availability_scale,
    )
    available = 0.0 if isclose(lower, 0.0, abs_tol=1e-300) else min(1.0, upper / lower)
    return min(1.0, max(0.0, 1.0 - available))


def _normalize_components(
    candidates: list[_CandidateMetrics],
) -> dict[str, dict[str, float]]:
    names = tuple(candidates[0].raw_components())
    normalized: dict[str, dict[str, float]] = {}
    for name in names:
        values = {
            candidate.player.player_id: value
            for candidate in candidates
            if (value := candidate.raw_components()[name]) is not None
        }
        if not values:
            normalized[name] = {}
            continue
        low = min(values.values())
        high = max(values.values())
        if isclose(low, high, rel_tol=0.0, abs_tol=1e-12):
            normalized[name] = {player_id: 0.5 for player_id in values}
        else:
            normalized[name] = {
                player_id: (value - low) / (high - low)
                for player_id, value in values.items()
            }
    return normalized


def _weighted_components(
    candidate: _CandidateMetrics,
    normalized: dict[str, dict[str, float]],
    weights: RoleWeights,
) -> tuple[RecommendationComponent, ...] | None:
    raw = candidate.raw_components()
    weight_values = weights.model_dump()
    components: list[RecommendationComponent] = []
    for name, weight in weight_values.items():
        if weight == 0:
            continue
        raw_value = raw[name]
        normalized_value = normalized[name].get(candidate.player.player_id)
        if raw_value is None or normalized_value is None:
            return None
        is_risk = name == "risk_penalty"
        contribution = weight * normalized_value * (-1.0 if is_risk else 1.0)
        components.append(
            RecommendationComponent(
                name=name,
                raw_value=raw_value,
                normalized_value=normalized_value,
                direction="lower_is_better" if is_risk else "higher_is_better",
                weight=weight,
                weighted_contribution=contribution,
            )
        )
    return tuple(components)


def _recommended_player(
    role: RecommendationRole,
    candidate: _CandidateMetrics,
    components: tuple[RecommendationComponent, ...],
    score: float,
) -> RecommendedPlayer:
    player = candidate.player
    if (
        player.average_pick is None
        or player.availability_evidence is None
        or player.market_source is None
        or player.market_snapshot_id is None
        or player.market_captured_at is None
    ):
        raise ValueError("A recommendation requires complete frozen market provenance.")
    leading = sorted(
        (component for component in components if component.weighted_contribution > 0),
        key=lambda component: (-component.weighted_contribution, component.name),
    )[:2]
    explanation = (
        f"{player.display_name} is the {role.replace('_', ' ')} baseline because its leading "
        f"weighted components are {', '.join(item.name for item in leading)}. "
        f"It adds {candidate.p50_vorp:.1f} P50 points over the ruleset replacement line."
    )
    risks = [
        "ADP availability and simulated opponent behavior are uncalibrated assumptions.",
        "The simulation does not model cross-player outcome correlation.",
    ]
    if candidate.simulation.mean_outcome_interval_coverage < 1.0:
        risks.append(
            "Some simulated roster rows have point-only uncertainty and remain deterministic."
        )
    return RecommendedPlayer(
        role=role,
        player_id=player.player_id,
        display_name=player.display_name,
        position=player.position,
        p10=player.p10,
        p50=player.p50,
        p90=player.p90,
        projection_status=player.prediction_status,
        projection_method=player.projection_method,
        current_adp=player.average_pick,
        probability_available_next_pick=1.0 - candidate.gone_probability,
        probability_gone_next_pick=candidate.gone_probability,
        availability_evidence=player.availability_evidence,
        replacement_points=candidate.replacement_points,
        p50_vorp=candidate.p50_vorp,
        roster_fit=candidate.roster_fit,
        simulation=candidate.simulation.as_dict(),
        components=components,
        draft_recommendation_score=score,
        explanation=explanation,
        primary_risks=tuple(risks),
        market_source=player.market_source,
        market_snapshot_id=player.market_snapshot_id,
        market_captured_at=player.market_captured_at.isoformat(),
    )


def _unavailable(
    state: DraftState,
    *,
    code: str,
    message: str,
) -> RecommendationResult:
    return RecommendationResult(
        available=False,
        code=code,
        message=message,
        session_id=state.session_id,
        session_version=state.version,
        state_fingerprint=state.fingerprint(),
        projection_run_id=state.projection_run_id,
        adp_build_fingerprint=state.adp_build_fingerprint,
        player_pool_fingerprint=state.player_pool_fingerprint,
        engine_config_fingerprint=state.engine_config_fingerprint,
        random_seed=state.random_seed,
        simulation_count=state.simulation_count,
        limitations=(
            "No championship probability is produced.",
            "Missing or unreviewed market identity evidence is never bridged by player name.",
        ),
    )
