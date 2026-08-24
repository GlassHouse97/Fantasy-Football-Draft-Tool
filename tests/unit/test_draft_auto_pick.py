from __future__ import annotations

from pathlib import Path

from fantasy_draft_ai.draft.pool import FrozenDraftPlayer
from fantasy_draft_ai.draft.repository import DraftRepository
from fantasy_draft_ai.recommendations.config import load_draft_engine_config
from fantasy_draft_ai.rules.models import DraftSettings, LeagueRules
from fantasy_draft_ai.scoring.engine import ScoringRules
from fantasy_draft_ai.services.draft_auto_pick import simulate_opponents_to_user_turn


def _players() -> tuple[FrozenDraftPlayer, ...]:
    return tuple(
        FrozenDraftPlayer(
            player_id=f"{position}-{index:02d}",
            display_name=f"{position} Player {index:02d}",
            position=position,
            p10=float(base - index - 20),
            p50=float(base - index),
            p90=float(base - index + 20),
            prediction_status="validated",
            projection_source="learned",
            projection_method="test-model",
        )
        for position, base in (("QB", 320), ("RB", 290), ("WR", 285), ("TE", 230))
        for index in range(1, 13)
    )


def _repository(tmp_path: Path, *, user_draft_slot: int) -> DraftRepository:
    repository = DraftRepository(tmp_path / f"auto-pick-{user_draft_slot}.duckdb")
    engine_config = load_draft_engine_config()
    repository.create_session(
        session_id=f"auto-pick-{user_draft_slot}",
        command_id="create-auto-pick-test",
        session_name="Auto-pick test",
        rules=LeagueRules(
            season=2026,
            teams=4,
            draft=DraftSettings(rounds=3),
            starters={"QB": 1},
            bench=2,
            scoring=ScoringRules(reception=1),
        ),
        user_draft_slot=user_draft_slot,
        projection_run_id="projection-test",
        adp_build_fingerprint=None,
        players=_players(),
        engine_config_fingerprint=engine_config.fingerprint(),
        recommendation_status="identity_mapping_required",
        recommendation_message="Projection guidance is available.",
        random_seed=42,
        simulation_count=engine_config.default_simulations,
    )
    return repository


def test_simulated_opponents_stop_exactly_at_user_turn_and_persist_normal_picks(
    tmp_path: Path,
) -> None:
    repository = _repository(tmp_path, user_draft_slot=2)
    result = simulate_opponents_to_user_turn(
        repository,
        "auto-pick-2",
        expected_version=0,
        engine_config=load_draft_engine_config(),
        command_id="sim-first-turn",
    )

    assert len(result.simulated_picks) == 1
    assert result.simulated_picks[0].overall_pick == 1
    assert result.simulated_picks[0].draft_slot == 1
    assert result.session.state.current_overall_pick == 2
    assert result.session.state.is_user_turn
    assert repository.verify_session("auto-pick-2") == result.session.state

    user_pick = repository.record_pick(
        "auto-pick-2",
        next(
            player.player_id
            for player in repository.load_players("auto-pick-2")
            if player.player_id not in result.session.state.selected_player_ids
        ),
        expected_version=result.session.state.version,
        command_id="user-pick",
    )
    next_result = simulate_opponents_to_user_turn(
        repository,
        "auto-pick-2",
        expected_version=user_pick.version,
        engine_config=load_draft_engine_config(),
        command_id="sim-second-turn",
    )

    assert [pick.overall_pick for pick in next_result.simulated_picks] == [3, 4, 5, 6]
    assert all(pick.draft_slot != 2 for pick in next_result.simulated_picks)
    assert next_result.session.state.current_overall_pick == 7
    assert next_result.session.state.is_user_turn
    assert len(next_result.session.state.selected_player_ids) == len(
        next_result.session.state.picks
    )


def test_simulate_is_a_no_op_when_user_is_already_on_the_clock(tmp_path: Path) -> None:
    repository = _repository(tmp_path, user_draft_slot=1)

    result = simulate_opponents_to_user_turn(
        repository,
        "auto-pick-1",
        expected_version=0,
        engine_config=load_draft_engine_config(),
        command_id="sim-no-op",
    )

    assert result.simulated_picks == ()
    assert result.session.state.version == 0
    assert result.session.state.is_user_turn
