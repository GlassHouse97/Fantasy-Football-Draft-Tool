from __future__ import annotations

from dataclasses import replace
from datetime import UTC, datetime

import pytest

from fantasy_draft_ai.draft.pool import FrozenDraftPlayer, player_pool_fingerprint
from fantasy_draft_ai.draft.roster import RosterPlayer, assign_roster
from fantasy_draft_ai.draft.state import DraftState, draft_slot_for_pick
from fantasy_draft_ai.recommendations.config import DraftEngineConfig, load_draft_engine_config
from fantasy_draft_ai.rules.models import DraftSettings, FlexSlot, LeagueRules
from fantasy_draft_ai.scoring.engine import ScoringRules
from fantasy_draft_ai.simulation import SimulationInputError, monte_carlo, simulate_rest_of_draft


def _rules(*, teams: int = 4, rounds: int = 3) -> LeagueRules:
    if rounds == 1:
        starters = {"WR": 1}
        bench = 0
    else:
        starters = {"QB": 1, "WR": 1}
        bench = rounds - 2
    return LeagueRules(
        season=2026,
        teams=teams,
        draft=DraftSettings(rounds=rounds),
        starters=starters,
        bench=bench,
        scoring=ScoringRules(reception=1),
    )


def _player(
    player_id: str,
    position: str,
    adp: float,
    p50: float,
    *,
    point_only: bool = False,
) -> FrozenDraftPlayer:
    spread = 0.0 if point_only else 10.0
    return FrozenDraftPlayer(
        player_id=player_id,
        display_name=f"Player {player_id}",
        position=position,
        p10=p50 - spread,
        p50=p50,
        p90=p50 + spread,
        prediction_status=(
            "rookie_heuristic_fallback_unvalidated" if point_only else "learned_models_validated"
        ),
        projection_source="baseline" if point_only else "learned",
        projection_method="fixture",
        market_source="ffc",
        market_snapshot_id="snapshot-1",
        market_captured_at=datetime(2026, 8, 1, tzinfo=UTC),
        average_pick=adp,
        availability_scale=3.0,
        availability_evidence="source_reported_standard_deviation",
        mapping_confidence="reviewed",
    )


def _three_round_pool() -> tuple[FrozenDraftPlayer, ...]:
    players: list[FrozenDraftPlayer] = []
    for index in range(8):
        players.append(_player(f"QB-{index + 1}", "QB", index + 1, 120 - index))
    for index in range(8):
        players.append(
            _player(
                f"WR-{index + 1}",
                "WR",
                index + 9,
                110 - index,
                point_only=index == 7,
            )
        )
    for index in range(8):
        players.append(_player(f"RB-{index + 1}", "RB", index + 17, 80 - index))
    return tuple(players)


def _state(
    players: tuple[FrozenDraftPlayer, ...],
    rules: LeagueRules,
    config: DraftEngineConfig,
    *,
    seed: int = 42,
    simulations: int = 16,
) -> DraftState:
    return DraftState(
        session_id="simulation-test",
        rules=rules,
        user_draft_slot=1,
        projection_run_id="phase4-test",
        adp_build_fingerprint="phase5-test",
        player_pool_fingerprint=player_pool_fingerprint(players),
        engine_config_fingerprint=config.fingerprint(),
        random_seed=seed,
        simulation_count=simulations,
    )


def test_simulation_is_seeded_order_independent_and_auditable() -> None:
    config = load_draft_engine_config()
    rules = _rules()
    players = _three_round_pool()
    state = _state(players, rules, config)

    first = simulate_rest_of_draft(state, players, "WR-1", config)
    repeated = simulate_rest_of_draft(state, list(reversed(players)), "WR-1", config)

    assert repeated == first
    assert first.fingerprint == repeated.fingerprint
    assert first.trace_fingerprint == repeated.trace_fingerprint
    assert first.market_coverage == 1.0
    assert first.mapped_player_count == len(players)
    assert first.point_only_player_count == 1
    assert first.total_simulated_picks == state.simulation_count * state.total_picks
    assert first.p10_final_roster_value <= first.p50_final_roster_value
    assert first.p50_final_roster_value <= first.p90_final_roster_value
    assert first.mean_starter_coverage == 1.0

    audit = first.audit_path
    assert [pick.overall_pick for pick in audit] == list(range(1, state.total_picks + 1))
    assert len({pick.player_id for pick in audit}) == len(audit)
    assert audit[0].actor == "candidate"
    assert audit[0].player_id == "WR-1"
    for pick in audit[1:]:
        expected_actor = (
            "user_policy"
            if draft_slot_for_pick(pick.overall_pick, rules.teams) == state.user_draft_slot
            else "opponent"
        )
        assert pick.actor == expected_actor


def test_seed_changes_trace_but_point_only_outcomes_remain_deterministic() -> None:
    config = load_draft_engine_config()
    rules = _rules()
    players = _three_round_pool()
    first_state = _state(players, rules, config, seed=42)
    second_state = _state(players, rules, config, seed=43)

    first = simulate_rest_of_draft(first_state, players, "WR-1", config)
    second = simulate_rest_of_draft(second_state, players, "WR-1", config)

    assert first.trace_fingerprint != second.trace_fingerprint
    point_player = next(player for player in players if player.player_id == "WR-8")
    assert (
        monte_carlo._sample_outcome(point_player, seed=42, simulation_index=0) == point_player.p50
    )
    assert (
        monte_carlo._sample_outcome(point_player, seed=999, simulation_index=99) == point_player.p50
    )


def test_point_only_candidate_is_not_given_fabricated_outcome_variance() -> None:
    config = load_draft_engine_config()
    rules = _rules(rounds=1)
    players = tuple(
        _player(f"WR-{index}", "WR", float(index), 101.0 - index, point_only=True)
        for index in range(1, 5)
    )
    state = _state(players, rules, config)

    result = simulate_rest_of_draft(state, players, "WR-1", config)

    assert result.p10_final_roster_value == 100.0
    assert result.p50_final_roster_value == 100.0
    assert result.p90_final_roster_value == 100.0
    assert result.mean_outcome_interval_coverage == 0.0
    assert result.mean_point_only_roster_players == 1.0


def test_unresolved_market_rows_and_pool_mismatches_are_rejected() -> None:
    config = load_draft_engine_config()
    rules = _rules()
    players = _three_round_pool()
    unresolved = replace(
        players[-1],
        market_source=None,
        market_snapshot_id=None,
        market_captured_at=None,
        average_pick=None,
        availability_scale=None,
        availability_evidence=None,
        mapping_confidence="unresolved",
    )
    partial_pool = (*players[:-1], unresolved)
    partial_state = _state(partial_pool, rules, config)

    with pytest.raises(SimulationInputError, match="coverage is insufficient"):
        simulate_rest_of_draft(partial_state, partial_pool, "WR-1", config)
    with pytest.raises(SimulationInputError, match="frozen player pool"):
        simulate_rest_of_draft(_state(players, rules, config), players[:-1], "WR-1", config)


def test_203_mapped_core_players_cover_a_192_pick_draft_with_projection_only_rows() -> None:
    config = load_draft_engine_config()
    rules = LeagueRules(
        season=2026,
        teams=12,
        draft=DraftSettings(rounds=16),
        starters={"QB": 1, "RB": 2, "WR": 3, "TE": 1},
        flex_slots=(FlexSlot(name="FLEX", count=2, eligible=("RB", "WR", "TE")),),
        bench=7,
        scoring=ScoringRules(reception=1),
    )
    mapped: list[FrozenDraftPlayer] = []
    next_adp = 1
    for position, count in (("QB", 30), ("RB", 60), ("WR", 80), ("TE", 33)):
        for index in range(1, count + 1):
            mapped.append(
                _player(
                    f"{position}-{index:03d}",
                    position,
                    float(next_adp),
                    400.0 - next_adp,
                )
            )
            next_adp += 1
    projection_only = tuple(
        replace(
            _player(f"MANUAL-{index:04d}", "RB", 500.0 + index, 50.0 - index / 100),
            market_source=None,
            market_snapshot_id=None,
            market_captured_at=None,
            average_pick=None,
            availability_scale=None,
            availability_evidence=None,
            mapping_confidence=None,
        )
        for index in range(1, 1_165)
    )
    players = (*mapped, *projection_only)
    state = _state(players, rules, config, simulations=1)

    result = simulate_rest_of_draft(state, players, "WR-001", config)

    assert state.total_picks == 192
    assert result.input_player_count == 1_367
    assert result.market_universe_player_count == 203
    assert result.mapped_player_count == 203
    assert result.market_coverage == 1.0
    assert result.total_simulated_picks == 192


def test_work_budget_is_enforced_before_expensive_paths() -> None:
    config = load_draft_engine_config().model_copy(
        update={"candidate_count": 30, "work_budget": 10_000}
    )
    rules = LeagueRules(
        season=2026,
        teams=32,
        draft=DraftSettings(rounds=31),
        starters={"WR": 1},
        bench=30,
        scoring=ScoringRules(),
    )
    players = (_player("WR-1", "WR", 1.0, 100.0),)
    state = _state(players, rules, config, simulations=1000)

    with pytest.raises(SimulationInputError, match="work budget exceeded"):
        simulate_rest_of_draft(state, players, "WR-1", config)


def test_opponent_need_and_run_adjustments_are_bounded_and_ruleset_aware() -> None:
    config = load_draft_engine_config()
    rules = _rules(rounds=1)
    empty = assign_roster([], rules)
    after_wr = assign_roster([RosterPlayer("WR-1", "WR", 100.0)], rules)
    filled = assign_roster([RosterPlayer("WR-2", "WR", 99.0)], rules)
    filled_after = assign_roster(
        [RosterPlayer("WR-2", "WR", 99.0), RosterPlayer("WR-3", "WR", 98.0)],
        rules,
    )

    assert monte_carlo._opponent_need_factor(empty, after_wr, config) > 1.0
    assert monte_carlo._opponent_need_factor(filled, filled_after, config) == 1.0
    assert monte_carlo._positional_run_factor("WR", ("WR", "WR", "WR"), config) == 1.25
    assert monte_carlo._positional_run_factor("QB", ("WR", "WR", "WR"), config) == 1.0
    near = monte_carlo._selection_hazard(10, average_pick=10.0, scale=3.0)
    far = monte_carlo._selection_hazard(1, average_pick=10.0, scale=3.0)
    assert 0.0 < far < near < 1.0
