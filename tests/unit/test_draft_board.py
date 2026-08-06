from __future__ import annotations

from collections.abc import Callable
from datetime import UTC, datetime

from fantasy_draft_ai.draft.pool import FrozenDraftPlayer
from fantasy_draft_ai.draft.state import DraftEvent, DraftState, apply_event
from fantasy_draft_ai.recommendations.config import load_draft_engine_config
from fantasy_draft_ai.rules.models import LeagueRules
from fantasy_draft_ai.services.draft_board import build_draft_board


def _player(
    player_id: str,
    position: str,
    p10: float,
    p50: float,
    p90: float,
    *,
    average_pick: float | None = None,
    scale: float | None = None,
    status: str = "learned",
    source: str = "learned",
) -> FrozenDraftPlayer:
    return FrozenDraftPlayer(
        player_id=player_id,
        display_name=player_id,
        position=position,
        p10=p10,
        p50=p50,
        p90=p90,
        prediction_status=status,
        projection_source=source,
        projection_method="test-method",
        average_pick=average_pick,
        availability_scale=scale,
        mapping_confidence="reviewed" if average_pick is not None else None,
    )


def _state(rules: LeagueRules) -> DraftState:
    event = DraftEvent(
        session_id="draft-board-test",
        sequence=0,
        event_id="start",
        event_type="session_started",
        occurred_at=datetime.now(UTC),
        command_id="start-command",
        payload={
            "rules": rules.model_dump(mode="json"),
            "ruleset_fingerprint": rules.fingerprint(),
            "user_draft_slot": 1,
            "projection_run_id": "projection-run",
            "adp_build_fingerprint": "adp-build",
            "player_pool_fingerprint": "pool",
            "engine_config_fingerprint": load_draft_engine_config().fingerprint(),
            "random_seed": 42,
            "simulation_count": 16,
        },
    )
    return apply_event(None, event)


def test_board_adds_deterministic_ranks_tiers_risk_and_method_labels(
    rules_factory: Callable[..., LeagueRules],
) -> None:
    rules = rules_factory(teams=4, wr=1, rb=0, qb=0, te=0, bench=0)
    players = [
        _player("wr-5", "WR", 50, 60, 70, status="rookie_fallback", source="baseline"),
        _player("wr-1", "WR", 90, 100, 110),
        _player("wr-2", "WR", 80, 95, 110),
        _player("wr-3", "WR", 60, 90, 120),
        _player("wr-4", "WR", 80, 80, 80, status="baseline", source="baseline"),
    ]

    rows = build_draft_board(_state(rules), players)

    assert [row.player_id for row in rows] == ["wr-1", "wr-2", "wr-3", "wr-4", "wr-5"]
    assert [row.tier for row in rows] == [1, 1, 1, 1, 2]
    assert rows[0].risk == "low"
    assert rows[2].risk == "high"
    assert rows[3].risk == "not_estimated"
    assert rows[3].method_kind == "transparent_baseline"
    assert rows[4].method_kind == "heuristic"


def test_board_probability_and_adp_value_are_missing_data_safe(
    rules_factory: Callable[..., LeagueRules],
) -> None:
    rules = rules_factory(teams=4, wr=1, rb=0, qb=0, te=0, bench=0)
    rows = build_draft_board(
        _state(rules),
        [
            _player("mapped", "WR", 80, 100, 120, average_pick=2, scale=1),
            _player("projection-only", "WR", 80, 90, 100),
        ],
    )

    mapped, projection_only = rows
    assert mapped.adp_value_at_current_pick == -1
    assert mapped.probability_gone_before_user_pick is not None
    assert 0 <= mapped.probability_gone_before_user_pick <= 1
    assert projection_only.average_pick is None
    assert projection_only.probability_gone_before_user_pick is None
