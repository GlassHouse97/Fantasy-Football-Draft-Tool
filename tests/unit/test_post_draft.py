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
from fantasy_draft_ai.rules.models import DraftSettings, FlexSlot, LeagueRules
from fantasy_draft_ai.scoring.engine import ScoringRules
from fantasy_draft_ai.services.post_draft import (
    PostDraftReportError,
    analyze_draft_state,
)


def _rules(*, teams: int = 4) -> LeagueRules:
    return LeagueRules(
        season=2026,
        teams=teams,
        draft=DraftSettings(rounds=2),
        starters={"WR": 1},
        bench=1,
        scoring=ScoringRules(reception=1),
    )


def _player(
    player_id: str,
    position: str,
    p50: float,
    *,
    average_pick: float | None,
    spread: float = 10.0,
) -> FrozenDraftPlayer:
    return FrozenDraftPlayer(
        player_id=player_id,
        display_name=f"Fixture {player_id}",
        position=position,
        p10=p50 - spread,
        p50=p50,
        p90=p50 + spread,
        prediction_status="learned_models_validated" if spread else "point_only",
        projection_source="learned" if spread else "baseline",
        projection_method="post-draft-test-fixture",
        market_source=None if average_pick is None else "ffc",
        market_snapshot_id=None if average_pick is None else "snapshot-2026-08-01",
        market_captured_at=(None if average_pick is None else datetime(2026, 8, 1, tzinfo=UTC)),
        average_pick=average_pick,
        availability_scale=None if average_pick is None else 4.0,
        availability_evidence=(
            None if average_pick is None else "source_reported_standard_deviation"
        ),
        mapping_confidence=None if average_pick is None else "reviewed",
    )


def _wr_pool(count: int = 12, *, market: bool = True) -> tuple[FrozenDraftPlayer, ...]:
    return tuple(
        _player(
            f"WR-{index:02d}",
            "WR",
            310.0 - 10.0 * (index - 1),
            average_pick=float(index) if market else None,
        )
        for index in range(1, count + 1)
    )


def _state(
    rules: LeagueRules,
    pool: tuple[FrozenDraftPlayer, ...],
    selected_ids: tuple[str, ...],
    *,
    user_draft_slot: int = 1,
) -> DraftState:
    by_id = {player.player_id: player for player in pool}
    picks = tuple(
        DraftPick(
            event_id=f"event-{overall_pick}",
            overall_pick=overall_pick,
            round=(overall_pick - 1) // rules.teams + 1,
            draft_slot=(slot := draft_slot_for_pick(overall_pick, rules.teams)),
            team_id=team_id_for_slot(slot),
            player_id=player_id,
            player_name=by_id[player_id].display_name,
            position=by_id[player_id].position,
            projected_points=by_id[player_id].p50,
        )
        for overall_pick, player_id in enumerate(selected_ids, start=1)
    )
    return DraftState(
        session_id="post-draft-test",
        rules=rules,
        user_draft_slot=user_draft_slot,
        projection_run_id="phase4-test",
        adp_build_fingerprint="phase5-test",
        player_pool_fingerprint=player_pool_fingerprint(pool),
        engine_config_fingerprint="phase6-test",
        random_seed=42,
        simulation_count=16,
        picks=picks,
        version=len(picks),
    )


def test_complete_report_is_auditable_and_deterministic() -> None:
    pool = _wr_pool()
    state = _state(
        _rules(),
        pool,
        tuple(f"WR-{index:02d}" for index in range(1, 9)),
    )

    report = analyze_draft_state(state, pool)
    reordered = analyze_draft_state(state, list(reversed(pool)))

    assert report.draft_complete
    assert report.team_complete
    assert report.team_id == "team-01"
    assert report.team_picks_recorded == 2
    assert report.lineup.starter_player_ids == ("WR-01",)
    assert report.lineup.bench_player_ids == ("WR-08",)
    assert report.lineup.starters.median == 310.0
    assert report.lineup.bench.median == 240.0
    assert report.lineup.roster.floor == 530.0
    assert report.value_vs_adp.observed_players == 2
    assert report.value_vs_adp.mean_pick_value_vs_adp == pytest.approx(0.0)
    assert report.positional_draft_capital[0].overall_picks == (1, 8)
    assert report.replacement_risk.starters_below_replacement_floor == 0
    assert all(comparison.available for comparison in report.strategy_comparisons)
    assert report.fingerprint() == reordered.fingerprint()
    assert report.as_dict()["value_vs_adp"]["positive_value_definition"] == (
        "overall_pick - average_pick"
    )
    assert "championship probability" in report.limitations[0]


def test_incomplete_report_remains_useful_and_can_select_another_team() -> None:
    pool = _wr_pool()
    state = _state(_rules(), pool, ("WR-01", "WR-02", "WR-03"))

    user_report = analyze_draft_state(state, pool)
    empty_team_report = analyze_draft_state(state, pool, team_id="team-04")

    assert not user_report.draft_complete
    assert not user_report.team_complete
    assert user_report.lineup.starter_coverage == 1.0
    assert all(len(item.selections) == 1 for item in user_report.strategy_comparisons)
    assert any("provisional" in item for item in user_report.limitations)
    assert empty_team_report.team_picks_recorded == 0
    assert empty_team_report.lineup.roster.median == 0.0
    assert empty_team_report.lineup.roster.floor is None
    assert empty_team_report.lineup.roster.interval_coverage == 0.0
    assert any("no recorded picks" in item for item in empty_team_report.limitations)


def test_ruleset_changes_replacement_value_and_lineup_interpretation() -> None:
    pool = tuple(
        [
            _player(
                f"WR-{index:02d}",
                "WR",
                320.0 - 8.0 * index,
                average_pick=float(index),
            )
            for index in range(1, 13)
        ]
        + [
            _player(
                f"RB-{index:02d}",
                "RB",
                200.0 - 3.0 * index,
                average_pick=float(index + 12),
            )
            for index in range(1, 13)
        ]
    )
    shallow_wr_rules = LeagueRules(
        season=2026,
        teams=4,
        draft=DraftSettings(rounds=2),
        starters={"RB": 1},
        flex_slots=(FlexSlot(name="FLEX", count=1, eligible=("RB", "WR")),),
        bench=0,
        scoring=ScoringRules(reception=1),
    )
    deep_wr_rules = LeagueRules(
        season=2026,
        teams=4,
        draft=DraftSettings(rounds=2),
        starters={"WR": 2},
        bench=0,
        scoring=ScoringRules(reception=1),
    )
    shallow = analyze_draft_state(_state(shallow_wr_rules, pool, ("WR-01",)), pool)
    deep = analyze_draft_state(_state(deep_wr_rules, pool, ("WR-01",)), pool)

    shallow_wr = next(row for row in shallow.positional_draft_capital if row.position == "WR")
    deep_wr = next(row for row in deep.positional_draft_capital if row.position == "WR")
    assert shallow.ruleset_fingerprint != deep.ruleset_fingerprint
    assert shallow_wr.replacement_points is not None
    assert deep_wr.replacement_points is not None
    assert deep_wr.replacement_points < shallow_wr.replacement_points
    assert deep_wr.total_p50_vorp is not None
    assert shallow_wr.total_p50_vorp is not None
    assert deep_wr.total_p50_vorp > shallow_wr.total_p50_vorp
    assert any(insight.position == "RB" for insight in shallow.weaknesses)
    assert any(insight.position == "WR" for insight in deep.weaknesses)


def test_missing_adp_and_point_only_projection_are_never_invented() -> None:
    pool_list = list(_wr_pool(count=8, market=False))
    pool_list[0] = _player("WR-01", "WR", 300.0, average_pick=None, spread=0.0)
    pool = tuple(pool_list)
    rules = LeagueRules(
        season=2026,
        teams=4,
        draft=DraftSettings(rounds=1),
        starters={"WR": 1},
        bench=0,
        scoring=ScoringRules(reception=1),
    )
    report = analyze_draft_state(_state(rules, pool, ("WR-01",)), pool)
    selected = report.players[0]
    market = next(
        item for item in report.strategy_comparisons if item.strategy_id == "market_consensus"
    )

    assert selected.p10 is None
    assert selected.p90 is None
    assert selected.pick_value_vs_adp is None
    assert selected.floor_vorp is None
    assert selected.replacement_risk_status == "uncertainty_unavailable"
    assert report.lineup.starters.floor is None
    assert report.lineup.starters.ceiling is None
    assert report.value_vs_adp.coverage == 0.0
    assert report.value_vs_adp.mean_pick_value_vs_adp is None
    assert not market.available
    assert market.starters is None
    assert any("not imputed" in item for item in report.limitations)
    assert any("zero spread is not treated as low risk" in item for item in report.limitations)


def test_state_and_pool_lineage_must_match() -> None:
    pool = _wr_pool()
    state = _state(_rules(), pool, ("WR-01",))
    changed_pool = (replace(pool[0], p10=pool[0].p10 - 1.0), *pool[1:])

    with pytest.raises(PostDraftReportError, match="does not match draft-state lineage"):
        analyze_draft_state(state, changed_pool)
