from __future__ import annotations

from dataclasses import replace
from datetime import UTC, datetime

from fantasy_draft_ai.draft.pool import FrozenDraftPlayer, player_pool_fingerprint
from fantasy_draft_ai.draft.state import (
    DraftPick,
    DraftState,
    draft_slot_for_pick,
    team_id_for_slot,
)
from fantasy_draft_ai.recommendations.config import (
    ProjectionGuidanceConfig,
    load_draft_engine_config,
    load_projection_guidance_config,
)
from fantasy_draft_ai.recommendations.projection_baseline import (
    build_projection_rankings,
    rank_best_available,
)
from fantasy_draft_ai.rules.models import DraftSettings, LeagueRules
from fantasy_draft_ai.scoring.engine import ScoringRules


def _rules() -> LeagueRules:
    return LeagueRules(
        season=2026,
        teams=4,
        draft=DraftSettings(rounds=2),
        starters={"QB": 1, "WR": 1},
        bench=0,
        scoring=ScoringRules(reception=1),
    )


def _player(player_id: str, position: str, p50: float) -> FrozenDraftPlayer:
    return FrozenDraftPlayer(
        player_id=player_id,
        display_name=f"Player {player_id}",
        position=position,
        p10=p50 - 20,
        p50=p50,
        p90=p50 + 20,
        prediction_status="learned_models_validated",
        projection_source="learned",
        projection_method="projection-guidance-test",
    )


def _pool() -> tuple[FrozenDraftPlayer, ...]:
    return (
        *(
            _player("QB-1", "QB", 300),
            _player("QB-2", "QB", 290),
            _player("QB-3", "QB", 280),
            _player("QB-4", "QB", 275),
            _player("QB-5", "QB", 260),
        ),
        *(
            _player("WR-1", "WR", 240),
            _player("WR-2", "WR", 180),
            _player("WR-3", "WR", 170),
            _player("WR-4", "WR", 160),
            _player("WR-5", "WR", 150),
        ),
    )


def _state(
    players: tuple[FrozenDraftPlayer, ...],
    *,
    user_draft_slot: int = 1,
    picks: tuple[DraftPick, ...] = (),
    rules: LeagueRules | None = None,
) -> DraftState:
    config = load_draft_engine_config()
    active_rules = rules or _rules()
    return DraftState(
        session_id="projection-guidance-test",
        rules=active_rules,
        user_draft_slot=user_draft_slot,
        projection_run_id="projection-run",
        adp_build_fingerprint=None,
        player_pool_fingerprint=player_pool_fingerprint(players),
        engine_config_fingerprint=config.fingerprint(),
        random_seed=42,
        simulation_count=16,
        picks=picks,
        version=len(picks),
    )


def _pick(overall_pick: int, player: FrozenDraftPlayer, *, teams: int = 4) -> DraftPick:
    slot = draft_slot_for_pick(overall_pick, teams)
    return DraftPick(
        event_id=f"pick-{overall_pick}",
        overall_pick=overall_pick,
        round=(overall_pick - 1) // teams + 1,
        draft_slot=slot,
        team_id=team_id_for_slot(slot),
        player_id=player.player_id,
        player_name=player.display_name,
        position=player.position,
        projected_points=player.p50,
    )


def _guidance_config() -> ProjectionGuidanceConfig:
    return load_projection_guidance_config()


def _with_market(
    player: FrozenDraftPlayer,
    *,
    average_pick: float,
    confidence: str = "reviewed",
    evidence: str | None = "observed_source_stddev",
) -> FrozenDraftPlayer:
    return replace(
        player,
        market_source="ffc",
        market_snapshot_id="snapshot-1",
        market_captured_at=datetime(2026, 8, 1, tzinfo=UTC),
        average_pick=average_pick,
        availability_scale=4.0,
        availability_evidence=evidence,
        mapping_confidence=confidence,
    )


def test_projection_rankings_use_replacement_value_across_positions() -> None:
    players = _pool()

    rankings = build_projection_rankings(_rules(), players)

    assert max(players, key=lambda player: player.p50).player_id == "QB-1"
    assert rankings[0].player_id == "WR-1"
    assert rankings[0].p50_vorp == 80
    assert rankings[0].position_rank == 1


def test_unmapped_pool_produces_deterministic_best_pick_guidance() -> None:
    players = _pool()
    state = _state(players)
    config = load_draft_engine_config()

    guidance_config = _guidance_config()
    first = rank_best_available(state, players, config, guidance_config, limit=5)
    reversed_input = rank_best_available(
        state,
        tuple(reversed(players)),
        config,
        guidance_config,
        limit=5,
    )

    assert first.available
    assert first == reversed_input
    assert first.guidance_mode == "projection_baseline"
    assert first.guidance_version == guidance_config.version
    assert first.guidance_config_fingerprint == guidance_config.fingerprint()
    assert first.candidates[0].player_id == "WR-1"
    assert first.candidates[0].fills_open_starter is True
    assert first.candidates[0].improves_starting_lineup is False
    assert first.candidates[0].starting_lineup_gain == 0.0
    assert first.candidates[0].roster_fit == 0.5 + guidance_config.open_starter_bonus
    assert all(candidate.current_adp is None for candidate in first.candidates)
    assert all(
        candidate.probability_available_next_pick is None for candidate in first.candidates
    )


def test_drafted_players_are_removed_before_guidance_is_recomputed() -> None:
    players = _pool()
    drafted = tuple(_pick(index, player) for index, player in enumerate(players[:7], start=1))
    state = _state(players, picks=drafted)

    result = rank_best_available(
        state,
        players,
        load_draft_engine_config(),
        _guidance_config(),
    )

    assert result.available
    recommended_ids = {candidate.player_id for candidate in result.candidates}
    assert not (recommended_ids & state.selected_player_ids)


def test_mapped_market_data_enriches_but_does_not_reorder_projection_guidance() -> None:
    players = _pool()
    market_players = tuple(
        _with_market(player, average_pick=float(index + 1), confidence=" high ")
        for index, player in enumerate(reversed(players))
    )
    config = load_draft_engine_config()
    guidance_config = _guidance_config()
    baseline = rank_best_available(_state(players), players, config, guidance_config)
    enriched = rank_best_available(
        _state(market_players), market_players, config, guidance_config
    )

    assert [candidate.player_id for candidate in enriched.candidates] == [
        candidate.player_id for candidate in baseline.candidates
    ]
    assert all(candidate.current_adp is not None for candidate in enriched.candidates)
    assert all(
        candidate.probability_available_next_pick is not None
        for candidate in enriched.candidates
    )


def test_partial_market_evidence_is_ignored_without_disabling_projection_guidance() -> None:
    players = _pool()
    incomplete = tuple(
        _with_market(player, average_pick=-1.0)
        if index == 0
        else player
        for index, player in enumerate(players)
    )

    result = rank_best_available(
        _state(incomplete),
        incomplete,
        load_draft_engine_config(),
        _guidance_config(),
    )

    assert result.available
    candidate = next(
        item for item in result.candidates if item.player_id == incomplete[0].player_id
    )
    assert candidate.current_adp is None
    assert candidate.probability_available_next_pick is None


def test_shared_market_predicate_normalizes_confidence_and_rejects_partial_rows() -> None:
    player = _player("WR-market", "WR", 200)

    assert _with_market(player, average_pick=10, confidence=" HIGH ").has_mapped_market_evidence
    assert not _with_market(player, average_pick=10, evidence=None).has_mapped_market_evidence
    assert not _with_market(player, average_pick=-1).has_mapped_market_evidence
    assert not _with_market(player, average_pick=10, confidence="medium").has_mapped_market_evidence


def test_consecutive_snake_turn_reports_certain_next_pick_availability() -> None:
    players = tuple(
        _with_market(player, average_pick=float(index + 1), confidence="exact")
        for index, player in enumerate(_pool())
    )
    picks = tuple(_pick(index, player) for index, player in enumerate(players[:3], start=1))
    state = _state(players, user_draft_slot=4, picks=picks)

    result = rank_best_available(
        state,
        players,
        load_draft_engine_config(),
        _guidance_config(),
    )

    assert state.current_overall_pick == 4
    assert state.next_user_pick(include_current=False) == 5
    assert result.available
    assert all(item.probability_available_next_pick == 1.0 for item in result.candidates)


def test_open_starter_and_lineup_improvement_are_distinct_scoring_components() -> None:
    rules = LeagueRules(
        season=2026,
        teams=4,
        draft=DraftSettings(rounds=3),
        starters={"QB": 1, "WR": 1},
        bench=1,
        scoring=ScoringRules(reception=1),
    )
    players = (
        _player("QB-current", "QB", 280),
        _player("QB-opp-1", "QB", 270),
        _player("WR-opp-1", "WR", 195),
        _player("QB-opp-2", "QB", 260),
        _player("WR-opp-2", "WR", 190),
        _player("QB-opp-3", "QB", 250),
        _player("WR-opp-3", "WR", 185),
        _player("WR-current", "WR", 200),
        _player("QB-upgrade", "QB", 285),
        _player("WR-bench", "WR", 170),
        _player("QB-bench", "QB", 240),
        _player("WR-bench-2", "WR", 160),
    )
    picks = tuple(_pick(index, player) for index, player in enumerate(players[:8], start=1))
    state = _state(players, picks=picks, rules=rules)
    guidance_config = _guidance_config()

    result = rank_best_available(
        state,
        players,
        load_draft_engine_config(),
        guidance_config,
    )

    assert result.available
    upgrade = next(item for item in result.candidates if item.player_id == "QB-upgrade")
    bench = next(item for item in result.candidates if item.player_id == "WR-bench")
    assert upgrade.fills_open_starter is False
    assert upgrade.improves_starting_lineup is True
    assert upgrade.starting_lineup_gain == 5.0
    assert upgrade.roster_fit == 0.0
    assert upgrade.decision_score == (
        upgrade.p50_vorp
        + guidance_config.scarcity_weight * upgrade.scarcity
        + guidance_config.lineup_improvement_weight * upgrade.starting_lineup_gain
    )
    assert "improve one of your current starting spots" in " ".join(upgrade.reasons)
    assert bench.fills_open_starter is False
    assert bench.improves_starting_lineup is False
    assert bench.starting_lineup_gain == 0.0


def test_player_pool_mismatch_fails_closed_with_frozen_provenance() -> None:
    players = _pool()
    state = _state(players)

    result = rank_best_available(
        state,
        players[:-1],
        load_draft_engine_config(),
        _guidance_config(),
    )

    assert (result.available, result.code) == (False, "player_pool_mismatch")
    assert result.player_pool_fingerprint == state.player_pool_fingerprint
    assert result.candidates == ()


def test_guidance_weights_are_versioned_and_fingerprinted() -> None:
    configured = _guidance_config()
    alternate = ProjectionGuidanceConfig(
        version="projection-baseline-test-v2",
        scarcity_weight=configured.scarcity_weight,
        roster_fit_weight=configured.roster_fit_weight,
        open_starter_bonus=configured.open_starter_bonus,
        lineup_improvement_weight=0.5,
    )

    assert configured.version == "projection-baseline-v1"
    assert configured.fingerprint() != alternate.fingerprint()


def test_guidance_fails_safely_off_turn_after_completion_and_on_config_mismatch() -> None:
    players = _pool()
    config = load_draft_engine_config()

    guidance_config = _guidance_config()
    off_turn = rank_best_available(
        _state(players, user_draft_slot=2), players, config, guidance_config
    )
    complete_picks = tuple(
        _pick(index, player) for index, player in enumerate(players[:8], start=1)
    )
    complete = rank_best_available(
        _state(players, picks=complete_picks), players, config, guidance_config
    )
    mismatched_state = replace(_state(players), engine_config_fingerprint="different")
    mismatched = rank_best_available(mismatched_state, players, config, guidance_config)

    assert (off_turn.available, off_turn.code) == (False, "not_user_turn")
    assert (complete.available, complete.code) == (False, "draft_complete")
    assert (mismatched.available, mismatched.code) == (False, "engine_config_mismatch")
