from __future__ import annotations

from dataclasses import replace
from datetime import UTC, datetime

import pytest

from fantasy_draft_ai.draft.pool import FrozenDraftPlayer, player_pool_fingerprint
from fantasy_draft_ai.draft.state import (
    DraftPick,
    DraftState,
    draft_slot_for_pick,
    team_id_for_slot,
)
from fantasy_draft_ai.recommendations.config import DraftEngineConfig, load_draft_engine_config
from fantasy_draft_ai.recommendations.engine import generate_recommendations
from fantasy_draft_ai.rules.models import DraftSettings, FlexSlot, LeagueRules
from fantasy_draft_ai.scoring.engine import ScoringRules
from fantasy_draft_ai.simulation import monte_carlo


def _config(*, candidate_count: int = 4) -> DraftEngineConfig:
    return load_draft_engine_config().model_copy(
        update={
            "default_simulations": 16,
            "maximum_simulations": 16,
            "candidate_count": candidate_count,
            "opponent_candidate_window": 24,
            "work_budget": 10_000,
        }
    )


def _rules(*, wide_receivers: int = 2, flex_count: int = 1) -> LeagueRules:
    return LeagueRules(
        season=2026,
        teams=4,
        draft=DraftSettings(rounds=wide_receivers + flex_count),
        starters={"WR": wide_receivers},
        flex_slots=(
            FlexSlot(name="FLEX", count=flex_count, eligible=("RB", "WR")),
        ),
        bench=0,
        scoring=ScoringRules(reception=1),
    )


def _player(
    player_id: str,
    position: str,
    *,
    p50: float,
    average_pick: float,
    floor_spread: float,
    ceiling_spread: float,
) -> FrozenDraftPlayer:
    return FrozenDraftPlayer(
        player_id=player_id,
        display_name=f"Fixture {player_id}",
        position=position,
        p10=p50 - floor_spread,
        p50=p50,
        p90=p50 + ceiling_spread,
        prediction_status="learned_models_validated",
        projection_source="learned",
        projection_method="recommendation-test-fixture",
        market_source="ffc",
        market_snapshot_id="snapshot-2026-08-01",
        market_captured_at=datetime(2026, 8, 1, tzinfo=UTC),
        average_pick=average_pick,
        availability_scale=4.0,
        availability_evidence="source_reported_standard_deviation",
        mapping_confidence="reviewed",
    )


def _mapped_pool() -> tuple[FrozenDraftPlayer, ...]:
    players: list[FrozenDraftPlayer] = []
    for index in range(20):
        players.append(
            _player(
                f"WR-{index + 1:02d}",
                "WR",
                p50=310.0 - 6.0 * index,
                average_pick=float(index + 1),
                floor_spread=8.0 + 3.0 * (index % 4),
                ceiling_spread=12.0 + 4.0 * ((index + 1) % 5),
            )
        )
    for index in range(4):
        players.append(
            _player(
                f"RB-{index + 1:02d}",
                "RB",
                p50=180.0 - 5.0 * index,
                average_pick=float(index + 21),
                floor_spread=10.0 + 2.0 * (index % 3),
                ceiling_spread=14.0 + 3.0 * ((index + 1) % 4),
            )
        )
    return tuple(players)


def _state(
    players: tuple[FrozenDraftPlayer, ...],
    rules: LeagueRules,
    config: DraftEngineConfig,
) -> DraftState:
    return DraftState(
        session_id="recommendation-engine-test",
        rules=rules,
        user_draft_slot=1,
        projection_run_id="phase4-test",
        adp_build_fingerprint="phase5-test",
        player_pool_fingerprint=player_pool_fingerprint(players),
        engine_config_fingerprint=config.fingerprint(),
        random_seed=42,
        simulation_count=16,
    )


def _state_after_early_picks(
    players: tuple[FrozenDraftPlayer, ...],
    rules: LeagueRules,
    config: DraftEngineConfig,
) -> DraftState:
    opening = _state(players, rules, config)
    selected = sorted(players, key=lambda player: (-player.p50, player.player_id))[:7]
    picks = tuple(
        DraftPick(
            event_id=f"early-pick-{overall_pick}",
            overall_pick=overall_pick,
            round=(overall_pick - 1) // rules.teams + 1,
            draft_slot=draft_slot_for_pick(overall_pick, rules.teams),
            team_id=team_id_for_slot(draft_slot_for_pick(overall_pick, rules.teams)),
            player_id=player.player_id,
            player_name=player.display_name,
            position=player.position,
            projected_points=player.p50,
        )
        for overall_pick, player in enumerate(selected, start=1)
    )
    return replace(opening, picks=picks, version=len(picks))


def _nested_keys(value: object) -> set[str]:
    keys: set[str] = set()
    if isinstance(value, dict):
        for key, nested in value.items():
            keys.add(str(key))
            keys.update(_nested_keys(nested))
    elif isinstance(value, (list, tuple)):
        for nested in value:
            keys.update(_nested_keys(nested))
    return keys


def test_recommendations_are_deterministic_distinct_and_recomputable() -> None:
    config = _config()
    rules = _rules()
    players = _mapped_pool()
    state = _state(players, rules, config)

    first = generate_recommendations(state, players, config)
    repeated = generate_recommendations(state, tuple(reversed(players)), config)

    assert first.available
    assert first == repeated
    assert first.fingerprint() == repeated.fingerprint()
    assert [candidate.role for candidate in first.candidates] == [
        "balanced",
        "safe_floor",
        "high_upside",
    ]
    assert len({candidate.player_id for candidate in first.candidates}) == 3

    for candidate in first.candidates:
        displayed = candidate.as_dict()
        contribution_total = sum(
            component["weighted_contribution"] for component in displayed["components"]
        )
        recomputed = max(0.0, min(100.0, 100.0 * contribution_total))
        assert displayed["draft_recommendation_score"] == pytest.approx(recomputed)

    assert not any(
        "championship" in key.casefold() for key in _nested_keys(first.as_dict())
    )
    assert any("championship probability" in limitation for limitation in first.limitations)


def test_unmapped_production_pool_is_gracefully_unavailable() -> None:
    config = _config()
    rules = _rules()
    players = tuple(
        replace(
            player,
            market_source=None,
            market_snapshot_id=None,
            market_captured_at=None,
            average_pick=None,
            availability_scale=None,
            availability_evidence=None,
            mapping_confidence="unresolved",
        )
        for player in _mapped_pool()
    )

    result = generate_recommendations(_state(players, rules, config), players, config)

    assert not result.available
    assert result.code == "insufficient_mapped_candidates"
    assert result.candidates == ()
    assert "canonically mapped" in result.message


def test_point_only_shortlist_is_not_promoted_as_safe_evidence() -> None:
    config = _config(candidate_count=3)
    rules = _rules()
    players = list(_mapped_pool())
    leader = players[0]
    players[0] = replace(
        leader,
        p10=leader.p50,
        p90=leader.p50,
        prediction_status="point_projection_only",
        projection_source="baseline",
    )
    frozen_pool = tuple(players)

    result = generate_recommendations(
        _state(frozen_pool, rules, config),
        frozen_pool,
        config,
    )

    assert not result.available
    assert result.code == "insufficient_role_evidence"
    assert "Point-only rows are not treated as safe" in result.message
    assert result.candidates == ()


def test_increased_wr_demand_changes_replacement_without_named_player_expectations() -> None:
    config = _config()
    players = _mapped_pool()
    shallow_rules = _rules(wide_receivers=2, flex_count=1)
    deep_rules = _rules(wide_receivers=3, flex_count=2)

    shallow = generate_recommendations(
        _state(players, shallow_rules, config),
        players,
        config,
    )
    deep = generate_recommendations(
        _state(players, deep_rules, config),
        players,
        config,
    )

    assert shallow_rules.scoring_fingerprint() == deep_rules.scoring_fingerprint()
    assert shallow_rules.fingerprint() != deep_rules.fingerprint()
    assert shallow.available and deep.available
    assert {candidate.position for candidate in shallow.candidates} == {"WR"}
    assert {candidate.position for candidate in deep.candidates} == {"WR"}

    shallow_replacement = {candidate.replacement_points for candidate in shallow.candidates}
    deep_replacement = {candidate.replacement_points for candidate in deep.candidates}
    assert len(shallow_replacement) == 1
    assert len(deep_replacement) == 1
    assert deep_replacement.pop() < shallow_replacement.pop()


def test_replacement_baseline_stays_frozen_after_early_picks_and_matches_simulator() -> None:
    config = _config()
    rules = _rules()
    players = _mapped_pool()
    opening = generate_recommendations(_state(players, rules, config), players, config)
    after_early_picks = generate_recommendations(
        _state_after_early_picks(players, rules, config),
        players,
        config,
    )

    assert opening.available and after_early_picks.available
    opening_lines = {candidate.replacement_points for candidate in opening.candidates}
    later_lines = {
        candidate.replacement_points for candidate in after_early_picks.candidates
    }
    simulator_line = monte_carlo._replacement_points(players, rules)["WR"]

    assert opening_lines == later_lines == {simulator_line}
    players_by_id = {player.player_id: player for player in players}
    for candidate in after_early_picks.candidates:
        assert candidate.p50_vorp == pytest.approx(
            players_by_id[candidate.player_id].p50 - simulator_line
        )
