from __future__ import annotations

from collections.abc import Callable
from datetime import UTC, datetime
from pathlib import Path

import pytest

from fantasy_draft_ai.draft.pool import player_pool_fingerprint
from fantasy_draft_ai.draft.repository import DraftRepository
from fantasy_draft_ai.draft.state import DraftState
from fantasy_draft_ai.models.adp.movement import AdpIdentity
from fantasy_draft_ai.recommendations.config import load_draft_engine_config
from fantasy_draft_ai.recommendations.engine import generate_recommendations
from fantasy_draft_ai.rules.models import LeagueRules
from fantasy_draft_ai.scoring.engine import ScoringRules
from fantasy_draft_ai.services.adp_market import (
    AdpMarketBoard,
    AdpMarketRow,
    AdpMarketStatus,
)
from fantasy_draft_ai.services.draft_room import (
    IDENTITY_MAPPING_REQUIRED,
    RECOMMENDATION_READY,
    DraftRoomServiceError,
    adp_scoring_format,
    create_draft_session,
    load_draft_session,
    prepare_draft_room,
    record_draft_pick,
    replace_draft_pick,
    undo_draft_pick,
)
from fantasy_draft_ai.services.projections import (
    TARGET_FANTASY_POINTS_TOTAL,
    PlayerProjection,
    ProjectionBoard,
    ProjectionBoardStatus,
    ProjectionInterval,
    ProjectionLineage,
    ProjectionRun,
)


def _projection_board(
    reference_rules: LeagueRules,
    *,
    rows: tuple[PlayerProjection, ...] | None = None,
) -> ProjectionBoard:
    projections = rows or (
        _projection("player-1", "Canonical Receiver", "WR", 180, 220, 260),
        _projection("player-2", "Canonical Runner", "RB", 160, 205, 245),
    )
    lineage = ProjectionLineage(
        feature_data_fingerprint="feature",
        target_data_fingerprint="target",
        build_fingerprint="build",
        scoring_ruleset_fingerprint=reference_rules.fingerprint(),
        baseline_report_fingerprint="baseline",
        model_feature_fingerprint="model-feature",
        model_config_fingerprint="model-config",
    )
    run = ProjectionRun(
        run_id="phase4-test-run",
        status="complete",
        trained_at="2026-08-01T00:00:00+00:00",
        prediction_season=reference_rules.season,
        lineage=lineage,
        split_seasons={},
        feature_rows=len(projections),
        target_rows=len(projections),
        training_rows=10,
        prediction_rows=len(projections),
        evaluated_rows=len(projections),
        live_prediction_rows=len(projections),
        candidate_rows=10,
        model_rows=1,
        champion_rows=1,
    )
    return ProjectionBoard(
        status=ProjectionBoardStatus(
            available=True,
            code="available",
            message="available",
            run=run,
            row_count=len(projections),
        ),
        rows=projections,
    )


def _projection(
    player_id: str,
    name: str,
    position: str,
    p10: float,
    p50: float,
    p90: float,
) -> PlayerProjection:
    return PlayerProjection(
        run_id="phase4-test-run",
        player_id=player_id,
        display_name=name,
        prediction_season=2026,
        position=position,
        prediction_status="learned",
        targets={
            TARGET_FANTASY_POINTS_TOTAL: ProjectionInterval(
                p10=p10,
                p50=p50,
                p90=p90,
                selected_source="learned",
                selected_name="histogram_gradient_boosting",
            )
        },
        explanation={},
    )


def _market_board(*rows: AdpMarketRow, available: bool = True) -> AdpMarketBoard:
    return AdpMarketBoard(
        status=AdpMarketStatus(
            available=available,
            code="available" if available else "not_built",
            message="available" if available else "not built",
            build_fingerprint="phase5-build" if available else None,
            snapshot_count=1 if available else 0,
            observation_rows=len(rows),
            persistence_ready_rows=len(rows),
            availability_rows=len(rows),
        ),
        rows=tuple(rows),
    )


def _market_row(
    raw_id: str,
    name: str,
    position: str,
    *,
    player_id: str | None,
    mapping_confidence: str,
    season: int = 2026,
    team_count: int = 12,
    scoring_format: str = "ppr",
    average_pick: float = 20,
) -> AdpMarketRow:
    return AdpMarketRow(
        snapshot_id="snapshot-1",
        raw_source_row_id=raw_id,
        identity=AdpIdentity("ffc", raw_id, player_id),
        player_name=name,
        position=position,
        nfl_team="TEST",
        source="ffc",
        captured_at=datetime(2026, 8, 1, tzinfo=UTC),
        season=season,
        scoring_format=scoring_format,
        team_count=team_count,
        average_pick=average_pick,
        min_pick=10,
        max_pick=30,
        source_standard_deviation=5,
        sample_size=100,
        mapping_confidence=mapping_confidence,
        prior_average_pick=None,
        change_7d=None,
        velocity_per_day=None,
        source_spread=None,
        observation_count=1,
        persistence_prediction=average_pick,
        linear_prediction=None,
        linear_status="insufficient_history",
        exponentially_weighted_prediction=None,
        exponentially_weighted_status="insufficient_history",
        availability_scale=5,
        availability_evidence_method="observed_source_stddev",
        availability_fallback_group=None,
    )


def test_unresolved_market_rows_require_identity_mapping_but_allow_state_only_pool(
    rules_factory: Callable[..., LeagueRules],
) -> None:
    rules = rules_factory()
    projections = _projection_board(rules)
    market = _market_board(
        _market_row(
            "ffc-1",
            "Canonical Receiver",
            "WR",
            player_id=None,
            mapping_confidence="unresolved",
        ),
        _market_row(
            "ffc-2",
            "Canonical Runner",
            "RB",
            player_id=None,
            mapping_confidence="unresolved",
        ),
    )

    prepared = prepare_draft_room(
        projections,
        market,
        rules=rules,
        projection_reference_rules=rules,
    )

    assert prepared.readiness.state_ready is True
    assert prepared.readiness.recommendation_ready is False
    assert prepared.readiness.recommendation_status == IDENTITY_MAPPING_REQUIRED
    assert prepared.readiness.compatible_market_rows == 2
    assert prepared.readiness.mapped_market_rows == 0
    assert prepared.readiness.unresolved_market_rows == 2
    assert prepared.readiness.market_coverage == 0
    assert len(prepared.players) == 2
    assert not any(player.has_market_evidence for player in prepared.players)


def test_pool_joins_only_by_canonical_id_and_allows_roster_variants(
    rules_factory: Callable[..., LeagueRules],
) -> None:
    reference = rules_factory(wr=2, flex_count=1)
    roster_variant = rules_factory(wr=3, flex_count=2, bench=4)
    projections = _projection_board(reference)
    market = _market_board(
        _market_row(
            "ffc-1",
            "A Totally Different Display Name",
            "WR",
            player_id="player-1",
            mapping_confidence="reviewed",
        ),
        _market_row(
            "ffc-2",
            "Another Different Name",
            "RB",
            player_id="player-2",
            mapping_confidence="reviewed",
            average_pick=30,
        ),
        _market_row(
            "wrong-scope",
            "Canonical Receiver",
            "WR",
            player_id="player-1",
            mapping_confidence="reviewed",
            team_count=10,
        ),
    )

    prepared = prepare_draft_room(
        projections,
        market,
        rules=roster_variant,
        projection_reference_rules=reference,
    )

    assert reference.fingerprint() != roster_variant.fingerprint()
    assert reference.scoring_fingerprint() == roster_variant.scoring_fingerprint()
    assert prepared.readiness.recommendation_status == RECOMMENDATION_READY
    assert prepared.readiness.market_coverage == 1
    assert prepared.readiness.compatible_market_rows == 2
    receiver = next(player for player in prepared.players if player.player_id == "player-1")
    assert receiver.display_name == "Canonical Receiver"
    assert receiver.p50 == 220
    assert receiver.average_pick == 20
    assert receiver.market_source == "ffc"


def test_projection_only_rows_do_not_dilute_fully_mapped_market_coverage(
    rules_factory: Callable[..., LeagueRules],
) -> None:
    rules = rules_factory(
        teams=4,
        qb=0,
        rb=0,
        wr=3,
        te=0,
        flex_count=0,
        bench=0,
    )
    market_projections = tuple(
        _projection(
            f"market-{index:02d}",
            f"Market Receiver {index:02d}",
            "WR",
            310.0 - 6.0 * index,
            330.0 - 5.0 * index,
            350.0 - 3.0 * index,
        )
        for index in range(1, 21)
    )
    projection_only = tuple(
        _projection(
            f"manual-{index:02d}",
            f"Projection Only {index:02d}",
            "RB",
            120.0 - index,
            140.0 - index,
            160.0 - index,
        )
        for index in range(1, 41)
    )
    market = _market_board(
        *(
            _market_row(
                f"ffc-{index:02d}",
                f"Source Receiver {index:02d}",
                "WR",
                player_id=f"market-{index:02d}",
                mapping_confidence="reviewed",
                team_count=4,
                average_pick=float(index),
            )
            for index in range(1, 21)
        ),
        _market_row(
            "ffc-kicker",
            "Archived Kicker",
            "PK",
            player_id="market-kicker",
            mapping_confidence="reviewed",
            team_count=4,
            average_pick=21.0,
        ),
        _market_row(
            "ffc-defense",
            "Archived Defense",
            "DEF",
            player_id="market-defense",
            mapping_confidence="reviewed",
            team_count=4,
            average_pick=22.0,
        ),
    )
    prepared = prepare_draft_room(
        _projection_board(rules, rows=(*market_projections, *projection_only)),
        market,
        rules=rules,
        projection_reference_rules=rules,
    )

    assert prepared.readiness.recommendation_ready
    assert prepared.readiness.market_coverage == 1.0
    assert prepared.readiness.mapped_market_rows == 20
    assert prepared.readiness.compatible_market_rows == 20
    assert prepared.readiness.excluded_market_rows == 2
    assert prepared.readiness.excluded_market_positions == ("DEF", "PK")
    assert "remain archived and auditable" in prepared.readiness.recommendation_message
    assert len(prepared.players) == 60
    assert sum(player.has_market_evidence for player in prepared.players) == 20

    config = load_draft_engine_config().model_copy(
        update={
            "default_simulations": 16,
            "maximum_simulations": 16,
            "candidate_count": 4,
            "work_budget": 10_000,
        }
    )
    state = DraftState(
        session_id="market-universe-coverage",
        rules=rules,
        user_draft_slot=1,
        projection_run_id="phase4-test-run",
        adp_build_fingerprint="phase5-build",
        player_pool_fingerprint=player_pool_fingerprint(prepared.players),
        engine_config_fingerprint=config.fingerprint(),
        random_seed=42,
        simulation_count=16,
    )
    result = generate_recommendations(state, prepared.players, config)

    assert result.available
    assert len(result.candidates) == 3
    for candidate in result.candidates:
        simulation = candidate.simulation
        assert simulation["input_player_count"] == 60
        assert simulation["market_universe_player_count"] == 20
        assert simulation["mapped_player_count"] == 20
        assert simulation["market_coverage"] == 1.0


def test_scoring_change_blocks_pool_even_when_roster_is_otherwise_compatible(
    rules_factory: Callable[..., LeagueRules],
) -> None:
    reference = rules_factory()
    changed_scoring = reference.model_copy(update={"scoring": ScoringRules(reception=0.5)})

    prepared = prepare_draft_room(
        _projection_board(reference),
        _market_board(),
        rules=changed_scoring,
        projection_reference_rules=reference,
    )

    assert prepared.readiness.state_ready is False
    assert prepared.readiness.state_status == "scoring_incompatible"
    assert prepared.players == ()


def test_duplicate_canonical_market_mapping_is_detected_without_choosing_by_name(
    rules_factory: Callable[..., LeagueRules],
) -> None:
    rules = rules_factory()
    market = _market_board(
        _market_row(
            "ffc-1",
            "First Source Name",
            "WR",
            player_id="player-1",
            mapping_confidence="reviewed",
        ),
        _market_row(
            "espn-1",
            "Second Source Name",
            "WR",
            player_id="player-1",
            mapping_confidence="reviewed",
        ),
    )

    prepared = prepare_draft_room(
        _projection_board(rules),
        market,
        rules=rules,
        projection_reference_rules=rules,
    )

    assert prepared.readiness.state_ready is True
    assert prepared.readiness.recommendation_ready is False
    assert prepared.readiness.recommendation_status == "duplicate_mapped_player_ids"
    assert prepared.readiness.duplicate_mapped_player_ids == ("player-1",)
    assert not next(
        player for player in prepared.players if player.player_id == "player-1"
    ).has_market_evidence


def test_state_only_session_convenience_functions_replay_pick_replace_and_undo(
    tmp_path: Path,
    rules_factory: Callable[..., LeagueRules],
) -> None:
    rules = rules_factory()
    prepared = prepare_draft_room(
        _projection_board(rules),
        _market_board(
            _market_row(
                "ffc-1",
                "Canonical Receiver",
                "WR",
                player_id=None,
                mapping_confidence="unresolved",
            )
        ),
        rules=rules,
        projection_reference_rules=rules,
    )
    repository = DraftRepository(tmp_path / "draft-room.duckdb")

    created = create_draft_session(
        repository,
        prepared,
        session_name="State only",
        rules=rules,
        user_draft_slot=1,
        engine_config=load_draft_engine_config(),
        random_seed=42,
        session_id="draft-test",
        command_id="create-test",
    )
    picked = record_draft_pick(
        repository,
        "draft-test",
        "player-1",
        expected_version=created.state.version,
        command_id="pick-test",
    )
    replaced = replace_draft_pick(
        repository,
        "draft-test",
        1,
        "player-2",
        expected_version=picked.state.version,
        command_id="replace-test",
    )
    undone = undo_draft_pick(
        repository,
        "draft-test",
        expected_version=replaced.state.version,
        command_id="undo-test",
    )
    loaded = load_draft_session(repository, "draft-test")

    assert created.info.recommendation_status == IDENTITY_MAPPING_REQUIRED
    assert picked.state.picks[0].player_id == "player-1"
    assert replaced.state.picks[0].player_id == "player-2"
    assert undone.state.picks == ()
    assert loaded.state.fingerprint() == undone.state.fingerprint()
    assert loaded.state.version == 3


def test_session_creation_rejects_incompatible_scoring_and_simulation_over_cap(
    tmp_path: Path,
    rules_factory: Callable[..., LeagueRules],
) -> None:
    reference = rules_factory()
    changed_scoring = reference.model_copy(update={"scoring": ScoringRules(reception=0.5)})
    blocked = prepare_draft_room(
        _projection_board(reference),
        _market_board(),
        rules=changed_scoring,
        projection_reference_rules=reference,
    )
    repository = DraftRepository(tmp_path / "blocked.duckdb")
    engine_config = load_draft_engine_config()

    with pytest.raises(DraftRoomServiceError, match="session scoring rules differ"):
        create_draft_session(
            repository,
            blocked,
            session_name="Blocked",
            rules=changed_scoring,
            user_draft_slot=1,
            engine_config=engine_config,
            random_seed=42,
        )

    ready = prepare_draft_room(
        _projection_board(reference),
        _market_board(),
        rules=reference,
        projection_reference_rules=reference,
    )
    with pytest.raises(DraftRoomServiceError, match="simulation_count"):
        create_draft_session(
            repository,
            ready,
            session_name="Too many simulations",
            rules=reference,
            user_draft_slot=1,
            engine_config=engine_config,
            random_seed=42,
            simulation_count=engine_config.maximum_simulations + 1,
        )


def test_session_creation_rejects_rules_changed_after_preparation(
    tmp_path: Path,
    rules_factory: Callable[..., LeagueRules],
) -> None:
    prepared_rules = rules_factory()
    changed_rules = rules_factory(wr=3, flex_count=2, bench=4)
    prepared = prepare_draft_room(
        _projection_board(prepared_rules),
        _market_board(),
        rules=prepared_rules,
        projection_reference_rules=prepared_rules,
    )

    with pytest.raises(DraftRoomServiceError, match="rules differ"):
        create_draft_session(
            DraftRepository(tmp_path / "rules-mismatch.duckdb"),
            prepared,
            session_name="Mismatched rules",
            rules=changed_rules,
            user_draft_slot=1,
            engine_config=load_draft_engine_config(),
            random_seed=42,
        )


def test_adp_scoring_scope_is_explicit(
    rules_factory: Callable[..., LeagueRules],
) -> None:
    ppr = rules_factory()
    half = ppr.model_copy(update={"scoring": ScoringRules(reception=0.5)})
    standard = ppr.model_copy(update={"scoring": ScoringRules(reception=0)})
    superflex = rules_factory(flex_eligible=("QB", "RB", "WR", "TE"))

    assert adp_scoring_format(ppr) == "ppr"
    assert adp_scoring_format(half) == "half-ppr"
    assert adp_scoring_format(standard) == "standard"
    assert adp_scoring_format(superflex) == "2-qb"
