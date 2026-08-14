"""Deterministic Monte Carlo rest-of-draft simulation for Phase 6."""

from __future__ import annotations

import hashlib
import json
import math
from dataclasses import dataclass
from typing import Any, Literal, Protocol

import pandas as pd

from fantasy_draft_ai.draft.pool import FrozenDraftPlayer, player_pool_fingerprint
from fantasy_draft_ai.draft.roster import RosterAssignment, RosterPlayer, assign_roster
from fantasy_draft_ai.draft.state import DraftState, draft_slot_for_pick, team_id_for_slot
from fantasy_draft_ai.recommendations.config import DraftEngineConfig
from fantasy_draft_ai.rules.models import LeagueRules
from fantasy_draft_ai.rules.replacement import replacement_levels

ALGORITHM_VERSION = "phase6-monte-carlo-v1"
_NORMAL_90_Z = 1.2815515655446004
_SQRT_TWO = math.sqrt(2.0)
_LOG_SQRT_TWO_PI = 0.5 * math.log(2.0 * math.pi)

PickActor = Literal["candidate", "opponent", "user_policy"]


class SimulationInputError(ValueError):
    """Raised when a frozen draft cannot support an honest simulation."""


@dataclass(frozen=True)
class SimulatedPick:
    """One auditable selection from the first deterministic simulation path."""

    overall_pick: int
    draft_slot: int
    team_id: str
    player_id: str
    position: str
    actor: PickActor

    def as_dict(self) -> dict[str, Any]:
        return {
            "overall_pick": self.overall_pick,
            "draft_slot": self.draft_slot,
            "team_id": self.team_id,
            "player_id": self.player_id,
            "position": self.position,
            "actor": self.actor,
        }


@dataclass(frozen=True)
class DraftSimulationResult:
    """Deterministic summary and lineage for one candidate's draft paths."""

    candidate_id: str
    simulation_count: int
    random_seed: int
    work_units: int
    input_player_count: int
    market_universe_player_count: int
    mapped_player_count: int
    market_coverage: float
    point_only_player_count: int
    mean_final_roster_value: float
    p10_final_roster_value: float
    p50_final_roster_value: float
    p90_final_roster_value: float
    mean_starter_coverage: float
    mean_outcome_interval_coverage: float
    mean_point_only_roster_players: float
    total_simulated_picks: int
    state_fingerprint: str
    player_pool_fingerprint: str
    config_fingerprint: str
    trace_fingerprint: str
    audit_path: tuple[SimulatedPick, ...]
    fingerprint: str

    def as_dict(self) -> dict[str, Any]:
        return {
            "algorithm_version": ALGORITHM_VERSION,
            "candidate_id": self.candidate_id,
            "simulation_count": self.simulation_count,
            "random_seed": self.random_seed,
            "work_units": self.work_units,
            "input_player_count": self.input_player_count,
            "market_universe_player_count": self.market_universe_player_count,
            "mapped_player_count": self.mapped_player_count,
            "market_coverage": self.market_coverage,
            "point_only_player_count": self.point_only_player_count,
            "mean_final_roster_value": self.mean_final_roster_value,
            "p10_final_roster_value": self.p10_final_roster_value,
            "p50_final_roster_value": self.p50_final_roster_value,
            "p90_final_roster_value": self.p90_final_roster_value,
            "mean_starter_coverage": self.mean_starter_coverage,
            "mean_outcome_interval_coverage": self.mean_outcome_interval_coverage,
            "mean_point_only_roster_players": self.mean_point_only_roster_players,
            "total_simulated_picks": self.total_simulated_picks,
            "state_fingerprint": self.state_fingerprint,
            "player_pool_fingerprint": self.player_pool_fingerprint,
            "config_fingerprint": self.config_fingerprint,
            "trace_fingerprint": self.trace_fingerprint,
            "audit_path": [pick.as_dict() for pick in self.audit_path],
            "fingerprint": self.fingerprint,
        }


@dataclass(frozen=True)
class _PreparedSimulation:
    players: tuple[FrozenDraftPlayer, ...]
    by_id: dict[str, FrozenDraftPlayer]
    market_universe_available: tuple[FrozenDraftPlayer, ...]
    mapped_available: tuple[FrozenDraftPlayer, ...]
    market_order: tuple[FrozenDraftPlayer, ...]
    candidate: FrozenDraftPlayer
    simulation_count: int
    work_units: int
    market_coverage: float
    pool_fingerprint: str
    state_fingerprint: str
    config_fingerprint: str
    replacement_points: dict[str, float]


@dataclass(frozen=True)
class _PathResult:
    final_roster_value: float
    starter_coverage: float
    outcome_interval_coverage: float
    point_only_roster_players: int
    picks: tuple[SimulatedPick, ...]


class _CoverageState(Protocol):
    @property
    def starter_coverage(self) -> float: ...

    @property
    def starter_slot_count(self) -> int: ...


@dataclass(frozen=True)
class _RosterShape:
    legal: bool
    starter_coverage: float
    starter_slot_count: int


def simulate_rest_of_draft(
    state: DraftState,
    players: tuple[FrozenDraftPlayer, ...] | list[FrozenDraftPlayer],
    candidate_id: str,
    config: DraftEngineConfig,
    *,
    simulation_count: int | None = None,
) -> DraftSimulationResult:
    """Compare one candidate through reproducible, market-aware draft paths.

    Only confirmed canonical market mappings may enter a simulated selection.
    Opponents use a conditional ADP hazard adjusted for open legal starter slots
    and a capped positional-run effect. Later user turns use a transparent,
    deterministic need-adjusted VORP rule. The function never mutates draft state.
    """

    prepared = _prepare_simulation(
        state,
        tuple(players),
        candidate_id,
        config,
        simulation_count=simulation_count,
    )
    final_values: list[float] = []
    starter_coverages: list[float] = []
    interval_coverages: list[float] = []
    point_only_counts: list[int] = []
    audit_path: tuple[SimulatedPick, ...] = ()
    trace_hasher = hashlib.sha256()
    shape_cache: dict[tuple[str, ...], _RosterShape] = {}
    for simulation_index in range(prepared.simulation_count):
        path = _simulate_path(
            state,
            prepared,
            config,
            simulation_index=simulation_index,
            shape_cache=shape_cache,
        )
        final_values.append(path.final_roster_value)
        starter_coverages.append(path.starter_coverage)
        interval_coverages.append(path.outcome_interval_coverage)
        point_only_counts.append(path.point_only_roster_players)
        if simulation_index == 0:
            audit_path = path.picks
        trace_hasher.update(
            _canonical_bytes(
                {
                    "simulation_index": simulation_index,
                    "picks": [pick.as_dict() for pick in path.picks],
                    "final_roster_value": _rounded(path.final_roster_value),
                    "starter_coverage": _rounded(path.starter_coverage),
                }
            )
        )
        trace_hasher.update(b"\n")

    trace_fingerprint = trace_hasher.hexdigest()
    summary: dict[str, Any] = {
        "algorithm_version": ALGORITHM_VERSION,
        "candidate_id": prepared.candidate.player_id,
        "simulation_count": prepared.simulation_count,
        "random_seed": state.random_seed,
        "work_units": prepared.work_units,
        "input_player_count": len(prepared.players),
        "market_universe_player_count": len(prepared.market_universe_available),
        "mapped_player_count": len(prepared.mapped_available),
        "market_coverage": _rounded(prepared.market_coverage),
        "point_only_player_count": sum(
            not player.has_outcome_interval for player in prepared.players
        ),
        "mean_final_roster_value": _rounded(_mean(final_values)),
        "p10_final_roster_value": _rounded(_percentile(final_values, 0.10)),
        "p50_final_roster_value": _rounded(_percentile(final_values, 0.50)),
        "p90_final_roster_value": _rounded(_percentile(final_values, 0.90)),
        "mean_starter_coverage": _rounded(_mean(starter_coverages)),
        "mean_outcome_interval_coverage": _rounded(_mean(interval_coverages)),
        "mean_point_only_roster_players": _rounded(_mean(point_only_counts)),
        "total_simulated_picks": prepared.simulation_count * (state.total_picks - len(state.picks)),
        "state_fingerprint": prepared.state_fingerprint,
        "player_pool_fingerprint": prepared.pool_fingerprint,
        "config_fingerprint": prepared.config_fingerprint,
        "trace_fingerprint": trace_fingerprint,
    }
    fingerprint = _fingerprint(summary)
    return DraftSimulationResult(
        candidate_id=str(summary["candidate_id"]),
        simulation_count=int(summary["simulation_count"]),
        random_seed=int(summary["random_seed"]),
        work_units=int(summary["work_units"]),
        input_player_count=int(summary["input_player_count"]),
        market_universe_player_count=int(summary["market_universe_player_count"]),
        mapped_player_count=int(summary["mapped_player_count"]),
        market_coverage=float(summary["market_coverage"]),
        point_only_player_count=int(summary["point_only_player_count"]),
        mean_final_roster_value=float(summary["mean_final_roster_value"]),
        p10_final_roster_value=float(summary["p10_final_roster_value"]),
        p50_final_roster_value=float(summary["p50_final_roster_value"]),
        p90_final_roster_value=float(summary["p90_final_roster_value"]),
        mean_starter_coverage=float(summary["mean_starter_coverage"]),
        mean_outcome_interval_coverage=float(summary["mean_outcome_interval_coverage"]),
        mean_point_only_roster_players=float(summary["mean_point_only_roster_players"]),
        total_simulated_picks=int(summary["total_simulated_picks"]),
        state_fingerprint=str(summary["state_fingerprint"]),
        player_pool_fingerprint=str(summary["player_pool_fingerprint"]),
        config_fingerprint=str(summary["config_fingerprint"]),
        trace_fingerprint=trace_fingerprint,
        audit_path=audit_path,
        fingerprint=fingerprint,
    )


def _prepare_simulation(
    state: DraftState,
    players: tuple[FrozenDraftPlayer, ...],
    candidate_id: str,
    config: DraftEngineConfig,
    *,
    simulation_count: int | None,
) -> _PreparedSimulation:
    ordered = tuple(sorted(players, key=lambda player: player.player_id))
    if len({player.player_id for player in ordered}) != len(ordered):
        raise SimulationInputError("The simulation pool contains duplicate canonical player IDs.")
    if state.current_overall_pick is None:
        raise SimulationInputError("The draft is complete; there is nothing left to simulate.")
    if not state.is_user_turn:
        raise SimulationInputError("Candidate simulation requires the current user pick.")
    count = state.simulation_count if simulation_count is None else simulation_count
    if count != state.simulation_count:
        raise SimulationInputError("simulation_count must match the value frozen in draft state.")
    if count < 1 or count > config.maximum_simulations:
        raise SimulationInputError(
            f"simulation_count must be between 1 and {config.maximum_simulations}."
        )
    config_fingerprint = config.fingerprint()
    if state.engine_config_fingerprint != config_fingerprint:
        raise SimulationInputError("Draft state does not match the supplied engine configuration.")
    pool_fingerprint = player_pool_fingerprint(ordered)
    if state.player_pool_fingerprint != pool_fingerprint:
        raise SimulationInputError("Draft state does not match the supplied frozen player pool.")
    if state.adp_build_fingerprint is None:
        raise SimulationInputError("Mapped ADP evidence is required for rest-of-draft simulation.")
    remaining_selection_count = state.total_picks - len(state.picks)
    work_units = count * config.candidate_count * remaining_selection_count
    if work_units > config.work_budget:
        raise SimulationInputError(
            f"Simulation work budget exceeded: {work_units} > {config.work_budget}."
        )
    by_id = {player.player_id: player for player in ordered}
    unknown_selected = sorted(state.selected_player_ids - set(by_id))
    if unknown_selected:
        raise SimulationInputError(
            "Draft state references players outside the frozen pool: " + ", ".join(unknown_selected)
        )
    for pick in state.picks:
        frozen = by_id[pick.player_id]
        if not math.isclose(pick.projected_points, frozen.p50, rel_tol=0.0, abs_tol=1e-9):
            raise SimulationInputError(
                f"Draft pick {pick.overall_pick} does not match frozen projection evidence."
            )
    candidate = by_id.get(candidate_id)
    if candidate is None:
        raise SimulationInputError(f"Candidate {candidate_id!r} is not in the frozen pool.")
    if candidate.player_id in state.selected_player_ids:
        raise SimulationInputError(f"Candidate {candidate_id!r} has already been selected.")
    available = tuple(
        player for player in ordered if player.player_id not in state.selected_player_ids
    )
    market_universe_available = tuple(
        player for player in available if _has_market_universe_evidence(player)
    )
    mapped_available = tuple(
        player for player in market_universe_available if _has_mapped_market_evidence(player)
    )
    market_coverage = (
        len(mapped_available) / len(market_universe_available)
        if market_universe_available
        else 0.0
    )
    if not _has_mapped_market_evidence(candidate):
        raise SimulationInputError("The candidate lacks confirmed canonical market evidence.")
    if market_coverage + 1e-12 < config.market_coverage_required:
        raise SimulationInputError(
            "Mapped market coverage is insufficient for the configured simulation gate: "
            f"{market_coverage:.3f} < {config.market_coverage_required:.3f}."
        )
    if len(mapped_available) < remaining_selection_count:
        raise SimulationInputError(
            "The mapped market pool cannot fill every remaining draft selection."
        )
    user_roster_ids = [
        pick.player_id for pick in state.picks if pick.draft_slot == state.user_draft_slot
    ]
    candidate_assignment = _assignment(
        (*user_roster_ids, candidate.player_id),
        by_id,
        state.rules,
    )
    if not candidate_assignment.legal:
        raise SimulationInputError("The candidate cannot fit the user's remaining legal roster.")
    return _PreparedSimulation(
        players=ordered,
        by_id=by_id,
        market_universe_available=market_universe_available,
        mapped_available=mapped_available,
        market_order=tuple(
            sorted(
                mapped_available,
                key=lambda player: (
                    math.inf if player.average_pick is None else player.average_pick,
                    player.player_id,
                ),
            )
        ),
        candidate=candidate,
        simulation_count=count,
        work_units=work_units,
        market_coverage=market_coverage,
        pool_fingerprint=pool_fingerprint,
        state_fingerprint=state.fingerprint(),
        config_fingerprint=config_fingerprint,
        replacement_points=_replacement_points(ordered, state.rules),
    )


def _simulate_path(
    state: DraftState,
    prepared: _PreparedSimulation,
    config: DraftEngineConfig,
    *,
    simulation_index: int,
    shape_cache: dict[tuple[str, ...], _RosterShape],
) -> _PathResult:
    current_pick = state.current_overall_pick
    if current_pick is None:
        raise SimulationInputError("The draft completed before simulation began.")
    rosters: dict[int, list[str]] = {slot: [] for slot in range(1, state.rules.teams + 1)}
    for pick in state.picks:
        rosters[pick.draft_slot].append(pick.player_id)
    rosters[state.user_draft_slot].append(prepared.candidate.player_id)
    available = {
        player.player_id: player
        for player in prepared.mapped_available
        if player.player_id not in state.selected_player_ids
        and player.player_id != prepared.candidate.player_id
    }
    picks: list[SimulatedPick] = [
        SimulatedPick(
            overall_pick=current_pick,
            draft_slot=state.user_draft_slot,
            team_id=state.user_team_id,
            player_id=prepared.candidate.player_id,
            position=prepared.candidate.position,
            actor="candidate",
        )
    ]
    recent_positions = [pick.position for pick in state.picks]
    recent_positions.append(prepared.candidate.position)
    recent_positions = recent_positions[-config.positional_run_window :]

    for overall_pick in range(current_pick + 1, state.total_picks + 1):
        draft_slot = draft_slot_for_pick(overall_pick, state.rules.teams)
        roster_ids = rosters[draft_slot]
        if draft_slot == state.user_draft_slot:
            selected = _choose_user_player(
                tuple(available.values()),
                roster_ids,
                prepared.by_id,
                prepared.replacement_points,
                state.rules,
                config,
                shape_cache,
            )
            actor: PickActor = "user_policy"
        else:
            selected = _choose_opponent_player(
                prepared.market_order,
                available,
                roster_ids,
                prepared.by_id,
                state.rules,
                config,
                recent_positions=tuple(recent_positions),
                seed=state.random_seed,
                simulation_index=simulation_index,
                overall_pick=overall_pick,
                shape_cache=shape_cache,
            )
            actor = "opponent"
        if selected is None:
            raise SimulationInputError(
                f"No legal mapped player remains for overall pick {overall_pick}."
            )
        roster_ids.append(selected.player_id)
        del available[selected.player_id]
        recent_positions.append(selected.position)
        recent_positions = recent_positions[-config.positional_run_window :]
        picks.append(
            SimulatedPick(
                overall_pick=overall_pick,
                draft_slot=draft_slot,
                team_id=team_id_for_slot(draft_slot),
                player_id=selected.player_id,
                position=selected.position,
                actor=actor,
            )
        )

    selected_ids = [pick.player_id for pick in state.picks] + [pick.player_id for pick in picks]
    if len(selected_ids) != len(set(selected_ids)):
        raise RuntimeError("The simulator produced a duplicate player selection.")
    user_ids = tuple(rosters[state.user_draft_slot])
    sampled_points = {
        player_id: _sample_outcome(
            prepared.by_id[player_id],
            seed=state.random_seed,
            simulation_index=simulation_index,
        )
        for player_id in user_ids
    }
    final_assignment = _assignment(
        user_ids,
        prepared.by_id,
        state.rules,
        projected_points=sampled_points,
    )
    if not final_assignment.legal:
        raise RuntimeError("The simulated user roster is not legal.")
    bench_credit = config.bench_value_credit * math.fsum(
        max(0.0, player.projected_points) for player in final_assignment.bench
    )
    interval_count = sum(prepared.by_id[player_id].has_outcome_interval for player_id in user_ids)
    roster_size = len(user_ids)
    return _PathResult(
        final_roster_value=final_assignment.starter_value + bench_credit,
        starter_coverage=final_assignment.starter_coverage,
        outcome_interval_coverage=interval_count / roster_size if roster_size else 0.0,
        point_only_roster_players=roster_size - interval_count,
        picks=tuple(picks),
    )


def _choose_opponent_player(
    market_order: tuple[FrozenDraftPlayer, ...],
    available: dict[str, FrozenDraftPlayer],
    roster_ids: list[str],
    by_id: dict[str, FrozenDraftPlayer],
    rules: LeagueRules,
    config: DraftEngineConfig,
    *,
    recent_positions: tuple[str, ...],
    seed: int,
    simulation_index: int,
    overall_pick: int,
    shape_cache: dict[tuple[str, ...], _RosterShape],
) -> FrozenDraftPlayer | None:
    before = _roster_shape(tuple(roster_ids), by_id, rules, shape_cache)
    legal: list[tuple[FrozenDraftPlayer, _RosterShape]] = []
    starter_improving: list[tuple[FrozenDraftPlayer, _RosterShape]] = []
    for player in market_order:
        if player.player_id not in available:
            continue
        after = _roster_shape((*roster_ids, player.player_id), by_id, rules, shape_cache)
        if after.legal:
            legal.append((player, after))
            if after.starter_coverage > before.starter_coverage:
                starter_improving.append((player, after))
        enough_legal = len(legal) >= config.opponent_candidate_window
        enough_improving = len(starter_improving) >= config.opponent_candidate_window
        if enough_legal and (before.starter_coverage >= 1.0 or enough_improving):
            break
    candidates = starter_improving if before.starter_coverage < 1.0 else legal
    if not candidates:
        candidates = legal
    candidates = candidates[: config.opponent_candidate_window]
    if not candidates:
        return None
    weighted: list[tuple[FrozenDraftPlayer, float]] = []
    for player, after in candidates:
        average_pick = player.average_pick
        scale = player.availability_scale
        if average_pick is None or scale is None:
            raise RuntimeError("An unmapped player reached opponent selection.")
        market_weight = max(
            config.minimum_pick_weight,
            _selection_hazard(overall_pick, average_pick=average_pick, scale=scale),
        )
        need = _opponent_need_factor(before, after, config)
        run = _positional_run_factor(player.position, recent_positions, config)
        weighted.append((player, market_weight * need * run))
    weighted.sort(key=lambda item: item[0].player_id)
    total = math.fsum(weight for _, weight in weighted)
    if not math.isfinite(total) or total <= 0.0:
        raise RuntimeError("Opponent selection weights are invalid.")
    needle = (
        _stable_uniform(
            seed,
            "opponent-pick",
            simulation_index,
            overall_pick,
        )
        * total
    )
    cumulative = 0.0
    for player, weight in weighted:
        cumulative += weight
        if needle < cumulative:
            return player
    return weighted[-1][0]


def _choose_user_player(
    available: tuple[FrozenDraftPlayer, ...],
    roster_ids: list[str],
    by_id: dict[str, FrozenDraftPlayer],
    replacement_points: dict[str, float],
    rules: LeagueRules,
    config: DraftEngineConfig,
    shape_cache: dict[tuple[str, ...], _RosterShape],
) -> FrozenDraftPlayer | None:
    before = _roster_shape(tuple(roster_ids), by_id, rules, shape_cache)
    ranked: list[tuple[float, float, float, str, FrozenDraftPlayer, bool]] = []
    for player in sorted(available, key=lambda item: item.player_id):
        after = _roster_shape((*roster_ids, player.player_id), by_id, rules, shape_cache)
        if not after.legal:
            continue
        replacement = replacement_points.get(player.position, 0.0)
        vorp = player.p50 - replacement
        starter_slots_gained = max(
            0.0,
            (after.starter_coverage - before.starter_coverage) * after.starter_slot_count,
        )
        need_bonus = (
            config.position_need_multiplier * starter_slots_gained * max(1.0, abs(replacement))
        )
        score = vorp + need_bonus
        ranked.append(
            (
                score,
                player.p50,
                -(player.average_pick if player.average_pick is not None else math.inf),
                player.player_id,
                player,
                after.starter_coverage > before.starter_coverage,
            )
        )
    if not ranked:
        return None
    if before.starter_coverage < 1.0:
        starter_improving = [item for item in ranked if item[5]]
        if starter_improving:
            ranked = starter_improving
    ranked.sort(key=lambda item: (-item[0], -item[1], -item[2], item[3]))
    return ranked[0][4]


def _opponent_need_factor(
    before: _CoverageState,
    after: _CoverageState,
    config: DraftEngineConfig,
) -> float:
    slots_gained = max(
        0.0,
        (after.starter_coverage - before.starter_coverage) * after.starter_slot_count,
    )
    return 1.0 + config.position_need_multiplier * slots_gained


def _positional_run_factor(
    position: str,
    recent_positions: tuple[str, ...] | list[str],
    config: DraftEngineConfig,
) -> float:
    same_position = sum(item.upper() == position.upper() for item in recent_positions)
    return 1.0 + min(0.25, config.positional_run_multiplier * same_position)


def _selection_hazard(overall_pick: int, *, average_pick: float, scale: float) -> float:
    if overall_pick < 1 or not math.isfinite(average_pick) or average_pick < 1.0:
        raise SimulationInputError("Market pick inputs must be finite and positive.")
    if not math.isfinite(scale) or scale <= 0.0:
        raise SimulationInputError("Market availability scale must be finite and positive.")
    lower_z = (overall_pick - 0.5 - average_pick) / scale
    upper_z = (overall_pick + 0.5 - average_pick) / scale
    log_ratio = min(0.0, _normal_log_survival(upper_z) - _normal_log_survival(lower_z))
    return min(1.0, max(0.0, -math.expm1(log_ratio)))


def _sample_outcome(
    player: FrozenDraftPlayer,
    *,
    seed: int,
    simulation_index: int,
) -> float:
    if not player.has_outcome_interval:
        return player.p50
    z_value = _stable_normal(seed, "player-outcome", simulation_index, player.player_id)
    if z_value < 0.0:
        scale = (player.p50 - player.p10) / _NORMAL_90_Z
    else:
        scale = (player.p90 - player.p50) / _NORMAL_90_Z
    return player.p50 + z_value * scale


def _stable_uniform(seed: int, *parts: object) -> float:
    """Return an order-independent uniform variate derived only from SHA-256."""

    digest = hashlib.sha256(_canonical_bytes([seed, *parts])).digest()
    mantissa = int.from_bytes(digest[:8], "big") >> 11
    return (mantissa + 0.5) / (1 << 53)


def _stable_normal(seed: int, *parts: object) -> float:
    first = _stable_uniform(seed, *parts, "box-muller-u1")
    second = _stable_uniform(seed, *parts, "box-muller-u2")
    return math.sqrt(-2.0 * math.log(first)) * math.cos(2.0 * math.pi * second)


def _normal_log_survival(z_value: float) -> float:
    if z_value < 8.0:
        return math.log(0.5 * math.erfc(z_value / _SQRT_TWO))
    inverse_square = 1.0 / (z_value * z_value)
    correction = 1.0 + inverse_square * (
        -1.0 + inverse_square * (3.0 + inverse_square * (-15.0 + inverse_square * 105.0))
    )
    return -0.5 * z_value * z_value - math.log(z_value) - _LOG_SQRT_TWO_PI + math.log(correction)


def _has_mapped_market_evidence(player: FrozenDraftPlayer) -> bool:
    return player.has_mapped_market_evidence


def _has_market_universe_evidence(player: FrozenDraftPlayer) -> bool:
    """Distinguish ADP-universe rows from projection-only manual-draft rows.

    Any partial market lineage keeps a player in the denominator so incomplete or
    unresolved evidence cannot make coverage look better. Players with no market
    evidence at all remain usable by manual draft state without diluting the ADP gate.
    """

    return any(
        (
            player.average_pick is not None,
            player.availability_scale is not None,
            bool((player.market_source or "").strip()),
            bool((player.market_snapshot_id or "").strip()),
            player.market_captured_at is not None,
            bool((player.availability_evidence or "").strip()),
            bool((player.mapping_confidence or "").strip()),
        )
    )


def _assignment(
    player_ids: tuple[str, ...] | list[str],
    by_id: dict[str, FrozenDraftPlayer],
    rules: LeagueRules,
    *,
    projected_points: dict[str, float] | None = None,
) -> RosterAssignment:
    return assign_roster(
        [
            RosterPlayer(
                player_id=player_id,
                position=by_id[player_id].position,
                projected_points=(
                    by_id[player_id].p50
                    if projected_points is None
                    else projected_points[player_id]
                ),
            )
            for player_id in player_ids
        ],
        rules,
    )


def _roster_shape(
    player_ids: tuple[str, ...] | list[str],
    by_id: dict[str, FrozenDraftPlayer],
    rules: LeagueRules,
    cache: dict[tuple[str, ...], _RosterShape],
) -> _RosterShape:
    positions = tuple(sorted(by_id[player_id].position for player_id in player_ids))
    cached = cache.get(positions)
    if cached is not None:
        return cached
    assignment = assign_roster(
        [
            RosterPlayer(
                player_id=f"shape-{index:02d}-{position}",
                position=position,
                projected_points=0.0,
            )
            for index, position in enumerate(positions)
        ],
        rules,
    )
    result = _RosterShape(
        legal=assignment.legal,
        starter_coverage=assignment.starter_coverage,
        starter_slot_count=assignment.starter_slot_count,
    )
    cache[positions] = result
    return result


def _replacement_points(
    players: tuple[FrozenDraftPlayer, ...],
    rules: LeagueRules,
) -> dict[str, float]:
    frame = pd.DataFrame.from_records(
        [
            {
                "player_id": player.player_id,
                "position": player.position,
                "projected_points": player.p50,
            }
            for player in players
        ]
    )
    levels = replacement_levels(frame, rules)
    output: dict[str, float] = {}
    for position, level in levels.items():
        if level.last_starter_points is not None:
            output[position] = level.last_starter_points
        elif level.waiver_percentile_points is not None:
            output[position] = level.waiver_percentile_points
        else:
            output[position] = 0.0
    return output


def _mean(values: list[float] | list[int]) -> float:
    if not values:
        raise ValueError("Cannot summarize an empty simulation result.")
    return math.fsum(values) / len(values)


def _percentile(values: list[float], probability: float) -> float:
    if not values:
        raise ValueError("Cannot summarize an empty simulation result.")
    ordered = sorted(values)
    position = (len(ordered) - 1) * probability
    lower = math.floor(position)
    upper = math.ceil(position)
    if lower == upper:
        return ordered[lower]
    fraction = position - lower
    return ordered[lower] * (1.0 - fraction) + ordered[upper] * fraction


def _rounded(value: float) -> float:
    return round(float(value), 10)


def _canonical_bytes(payload: object) -> bytes:
    return json.dumps(
        payload,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=True,
        allow_nan=False,
    ).encode("utf-8")


def _fingerprint(payload: object) -> str:
    return hashlib.sha256(_canonical_bytes(payload)).hexdigest()
