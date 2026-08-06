"""Auditable, ruleset-aware post-draft analysis outside the UI.

The report is descriptive. It reuses the frozen session projections, exact roster
assignment, and transparent replacement heuristic; it does not estimate wins,
playoffs, or championships.
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from math import isclose
from typing import Any, Literal

import pandas as pd

from fantasy_draft_ai.draft.pool import FrozenDraftPlayer, player_pool_fingerprint
from fantasy_draft_ai.draft.roster import RosterAssignment, RosterPlayer, assign_roster
from fantasy_draft_ai.draft.state import DraftPick, DraftState, team_id_for_slot
from fantasy_draft_ai.rules.replacement import replacement_levels
from fantasy_draft_ai.services.draft_room import DraftRoomSession

REPORT_VERSION = "phase7-post-draft-v1"

LineupRole = Literal["starter", "bench"]
ReplacementRiskStatus = Literal[
    "floor_below_replacement",
    "floor_at_or_above_replacement",
    "uncertainty_unavailable",
    "replacement_unavailable",
]


class PostDraftReportError(ValueError):
    """Raised when state and its supposedly frozen player pool do not agree."""


@dataclass(frozen=True)
class ProjectionSummary:
    """Additive frozen projections with explicit uncertainty coverage."""

    player_count: int
    floor: float | None
    median: float
    ceiling: float | None
    interval_player_count: int
    interval_coverage: float

    def as_dict(self) -> dict[str, Any]:
        return {
            "player_count": self.player_count,
            "floor": self.floor,
            "median": self.median,
            "ceiling": self.ceiling,
            "interval_player_count": self.interval_player_count,
            "interval_coverage": self.interval_coverage,
        }


@dataclass(frozen=True)
class PostDraftPlayer:
    """One selected canonical player and every measured draft-value input."""

    player_id: str
    display_name: str
    position: str
    overall_pick: int
    round: int
    lineup_role: LineupRole
    lineup_slot: str
    p10: float | None
    p50: float
    p90: float | None
    projection_status: str
    projection_source: str
    projection_method: str
    outcome_interval_available: bool
    market_source: str | None
    market_snapshot_id: str | None
    market_captured_at: str | None
    mapping_confidence: str | None
    average_pick: float | None
    pick_value_vs_adp: float | None
    replacement_points: float | None
    p50_vorp: float | None
    floor_vorp: float | None
    replacement_risk_status: ReplacementRiskStatus

    def as_dict(self) -> dict[str, Any]:
        return {
            "player_id": self.player_id,
            "display_name": self.display_name,
            "position": self.position,
            "overall_pick": self.overall_pick,
            "round": self.round,
            "lineup_role": self.lineup_role,
            "lineup_slot": self.lineup_slot,
            "projection": {
                "p10": self.p10,
                "p50": self.p50,
                "p90": self.p90,
                "status": self.projection_status,
                "source": self.projection_source,
                "method": self.projection_method,
                "outcome_interval_available": self.outcome_interval_available,
            },
            "market_source": self.market_source,
            "market_snapshot_id": self.market_snapshot_id,
            "market_captured_at": self.market_captured_at,
            "mapping_confidence": self.mapping_confidence,
            "average_pick": self.average_pick,
            "pick_value_vs_adp": self.pick_value_vs_adp,
            "replacement_points": self.replacement_points,
            "p50_vorp": self.p50_vorp,
            "floor_vorp": self.floor_vorp,
            "replacement_risk_status": self.replacement_risk_status,
        }


@dataclass(frozen=True)
class LineupSummary:
    """Exact P50 lineup assignment and additive starter/bench projections."""

    starter_player_ids: tuple[str, ...]
    bench_player_ids: tuple[str, ...]
    starter_slots_filled: int
    starter_slot_count: int
    starter_coverage: float
    starters: ProjectionSummary
    bench: ProjectionSummary
    roster: ProjectionSummary

    def as_dict(self) -> dict[str, Any]:
        return {
            "starter_player_ids": list(self.starter_player_ids),
            "bench_player_ids": list(self.bench_player_ids),
            "starter_slots_filled": self.starter_slots_filled,
            "starter_slot_count": self.starter_slot_count,
            "starter_coverage": self.starter_coverage,
            "starters": self.starters.as_dict(),
            "bench": self.bench.as_dict(),
            "roster": self.roster.as_dict(),
        }


@dataclass(frozen=True)
class PositionDraftCapital:
    """Observed pick allocation by position without an opaque capital score."""

    position: str
    player_count: int
    starter_count: int
    bench_count: int
    overall_picks: tuple[int, ...]
    rounds: tuple[int, ...]
    earliest_overall_pick: int
    mean_overall_pick: float
    pick_share: float
    mapped_adp_count: int
    mean_pick_value_vs_adp: float | None
    replacement_points: float | None
    total_p50_vorp: float | None

    def as_dict(self) -> dict[str, Any]:
        return {
            "position": self.position,
            "player_count": self.player_count,
            "starter_count": self.starter_count,
            "bench_count": self.bench_count,
            "overall_picks": list(self.overall_picks),
            "rounds": list(self.rounds),
            "earliest_overall_pick": self.earliest_overall_pick,
            "mean_overall_pick": self.mean_overall_pick,
            "pick_share": self.pick_share,
            "mapped_adp_count": self.mapped_adp_count,
            "mean_pick_value_vs_adp": self.mean_pick_value_vs_adp,
            "replacement_points": self.replacement_points,
            "total_p50_vorp": self.total_p50_vorp,
        }


@dataclass(frozen=True)
class AdpValueSummary:
    """Draft-position minus ADP; positive values mean the team waited past ADP."""

    observed_players: int
    missing_players: int
    coverage: float
    total_pick_value_vs_adp: float | None
    mean_pick_value_vs_adp: float | None

    def as_dict(self) -> dict[str, Any]:
        return {
            "observed_players": self.observed_players,
            "missing_players": self.missing_players,
            "coverage": self.coverage,
            "total_pick_value_vs_adp": self.total_pick_value_vs_adp,
            "mean_pick_value_vs_adp": self.mean_pick_value_vs_adp,
            "positive_value_definition": "overall_pick - average_pick",
        }


@dataclass(frozen=True)
class ReplacementRiskSummary:
    """Floor-vs-replacement exposure counts, deliberately not a probability."""

    starter_players: int
    evaluated_starters: int
    starters_below_replacement_floor: int
    unknown_starter_floors: int
    floor_shortfall_points: float

    def as_dict(self) -> dict[str, Any]:
        return {
            "starter_players": self.starter_players,
            "evaluated_starters": self.evaluated_starters,
            "starters_below_replacement_floor": self.starters_below_replacement_floor,
            "unknown_starter_floors": self.unknown_starter_floors,
            "floor_shortfall_points": self.floor_shortfall_points,
            "interpretation": "descriptive floor shortfall, not an injury or outcome probability",
        }


@dataclass(frozen=True)
class BaselineSelection:
    overall_pick: int
    player_id: str

    def as_dict(self) -> dict[str, Any]:
        return {"overall_pick": self.overall_pick, "player_id": self.player_id}


@dataclass(frozen=True)
class StrategyComparison:
    """A deterministic counterfactual at the selected team's recorded pick numbers."""

    strategy_id: str
    label: str
    description: str
    available: bool
    selections: tuple[BaselineSelection, ...]
    starters: ProjectionSummary | None
    roster: ProjectionSummary | None
    starter_median_difference: float | None
    roster_median_difference: float | None
    unavailable_reason: str | None
    assumptions: tuple[str, ...]

    def as_dict(self) -> dict[str, Any]:
        return {
            "strategy_id": self.strategy_id,
            "label": self.label,
            "description": self.description,
            "available": self.available,
            "selections": [selection.as_dict() for selection in self.selections],
            "starters": None if self.starters is None else self.starters.as_dict(),
            "roster": None if self.roster is None else self.roster.as_dict(),
            "starter_median_difference": self.starter_median_difference,
            "roster_median_difference": self.roster_median_difference,
            "unavailable_reason": self.unavailable_reason,
            "assumptions": list(self.assumptions),
        }


@dataclass(frozen=True)
class RosterInsight:
    code: str
    title: str
    detail: str
    position: str | None = None
    metric_name: str | None = None
    metric_value: float | None = None

    def as_dict(self) -> dict[str, Any]:
        return {
            "code": self.code,
            "title": self.title,
            "detail": self.detail,
            "position": self.position,
            "metric_name": self.metric_name,
            "metric_value": self.metric_value,
        }


@dataclass(frozen=True)
class PostDraftReport:
    """Canonical post-draft payload suitable for UI display or export."""

    report_version: str
    session_id: str
    session_version: int
    state_fingerprint: str
    player_pool_fingerprint: str
    projection_run_id: str
    adp_build_fingerprint: str | None
    ruleset_fingerprint: str
    ruleset_canonical_json: str
    team_id: str
    draft_slot: int
    draft_complete: bool
    team_complete: bool
    picks_recorded: int
    total_picks: int
    team_picks_recorded: int
    expected_team_picks: int
    lineup: LineupSummary
    players: tuple[PostDraftPlayer, ...]
    positional_draft_capital: tuple[PositionDraftCapital, ...]
    value_vs_adp: AdpValueSummary
    replacement_risk: ReplacementRiskSummary
    strategy_comparisons: tuple[StrategyComparison, ...]
    strengths: tuple[RosterInsight, ...]
    weaknesses: tuple[RosterInsight, ...]
    limitations: tuple[str, ...]

    def as_dict(self) -> dict[str, Any]:
        return {
            "report_version": self.report_version,
            "session_id": self.session_id,
            "session_version": self.session_version,
            "state_fingerprint": self.state_fingerprint,
            "player_pool_fingerprint": self.player_pool_fingerprint,
            "projection_run_id": self.projection_run_id,
            "adp_build_fingerprint": self.adp_build_fingerprint,
            "ruleset_fingerprint": self.ruleset_fingerprint,
            "ruleset_canonical_json": self.ruleset_canonical_json,
            "team_id": self.team_id,
            "draft_slot": self.draft_slot,
            "draft_complete": self.draft_complete,
            "team_complete": self.team_complete,
            "picks_recorded": self.picks_recorded,
            "total_picks": self.total_picks,
            "team_picks_recorded": self.team_picks_recorded,
            "expected_team_picks": self.expected_team_picks,
            "lineup": self.lineup.as_dict(),
            "players": [player.as_dict() for player in self.players],
            "positional_draft_capital": [
                position.as_dict() for position in self.positional_draft_capital
            ],
            "value_vs_adp": self.value_vs_adp.as_dict(),
            "replacement_risk": self.replacement_risk.as_dict(),
            "strategy_comparisons": [
                comparison.as_dict() for comparison in self.strategy_comparisons
            ],
            "strengths": [insight.as_dict() for insight in self.strengths],
            "weaknesses": [insight.as_dict() for insight in self.weaknesses],
            "limitations": list(self.limitations),
        }

    def fingerprint(self) -> str:
        encoded = json.dumps(
            self.as_dict(),
            sort_keys=True,
            separators=(",", ":"),
            ensure_ascii=True,
            allow_nan=False,
        ).encode("utf-8")
        return hashlib.sha256(encoded).hexdigest()


def build_post_draft_report(
    session: DraftRoomSession,
    *,
    team_id: str | None = None,
) -> PostDraftReport:
    """Analyze an already verified repository-backed draft-room session."""

    return analyze_draft_state(session.state, session.players, team_id=team_id)


def analyze_draft_state(
    state: DraftState,
    players: tuple[FrozenDraftPlayer, ...] | list[FrozenDraftPlayer],
    *,
    team_id: str | None = None,
) -> PostDraftReport:
    """Analyze a verified state and its exact frozen player pool.

    ``team_id`` defaults to the configured user team. The lower-level API verifies
    pool lineage and active picks so callers cannot accidentally combine unrelated
    state and projection snapshots.
    """

    pool = tuple(sorted(players, key=lambda player: player.player_id))
    by_id = _validate_inputs(state, pool)
    selected_team = state.user_team_id if team_id is None else team_id.strip()
    team_to_slot = {team_id_for_slot(slot): slot for slot in range(1, state.rules.teams + 1)}
    if selected_team not in team_to_slot:
        raise PostDraftReportError(f"team_id must be one of: {', '.join(sorted(team_to_slot))}.")
    draft_slot = team_to_slot[selected_team]
    team_picks = tuple(sorted(state.roster(draft_slot), key=lambda pick: pick.overall_pick))
    team_players = tuple(by_id[pick.player_id] for pick in team_picks)
    assignment = _assign(team_players, state)
    if not assignment.legal:
        raise PostDraftReportError("The selected team exceeds its ruleset roster capacity.")

    replacement = _replacement_by_position(pool, state)
    analyzed_players = _analyze_players(team_picks, by_id, assignment, replacement)
    lineup = _lineup_summary(team_players, assignment)
    capital = _position_capital(analyzed_players, replacement)
    adp_summary = _adp_summary(analyzed_players)
    risk_summary = _replacement_risk(analyzed_players)
    comparisons = _strategy_comparisons(
        state,
        pool,
        team_picks,
        replacement,
        lineup,
    )
    strengths, weaknesses = _ruleset_insights(
        state,
        analyzed_players,
        assignment,
        capital,
        adp_summary,
        risk_summary,
    )
    team_complete = len(team_picks) == state.rules.draft.rounds
    return PostDraftReport(
        report_version=REPORT_VERSION,
        session_id=state.session_id,
        session_version=state.version,
        state_fingerprint=state.fingerprint(),
        player_pool_fingerprint=state.player_pool_fingerprint,
        projection_run_id=state.projection_run_id,
        adp_build_fingerprint=state.adp_build_fingerprint,
        ruleset_fingerprint=state.rules.fingerprint(),
        ruleset_canonical_json=state.rules.canonical_json(),
        team_id=selected_team,
        draft_slot=draft_slot,
        draft_complete=state.complete,
        team_complete=team_complete,
        picks_recorded=len(state.picks),
        total_picks=state.total_picks,
        team_picks_recorded=len(team_picks),
        expected_team_picks=state.rules.draft.rounds,
        lineup=lineup,
        players=analyzed_players,
        positional_draft_capital=capital,
        value_vs_adp=adp_summary,
        replacement_risk=risk_summary,
        strategy_comparisons=comparisons,
        strengths=strengths,
        weaknesses=weaknesses,
        limitations=_limitations(
            state,
            team_complete,
            analyzed_players,
            comparisons,
        ),
    )


def _validate_inputs(
    state: DraftState,
    players: tuple[FrozenDraftPlayer, ...],
) -> dict[str, FrozenDraftPlayer]:
    if not players:
        raise PostDraftReportError("A post-draft report requires the frozen player pool.")
    try:
        actual_fingerprint = player_pool_fingerprint(players)
    except ValueError as exc:
        raise PostDraftReportError(str(exc)) from exc
    if actual_fingerprint != state.player_pool_fingerprint:
        raise PostDraftReportError("The frozen player pool does not match draft-state lineage.")
    by_id = {player.player_id: player for player in players}
    if len({pick.player_id for pick in state.picks}) != len(state.picks):
        raise PostDraftReportError("Active draft picks contain a duplicate canonical player ID.")
    for expected_pick, pick in enumerate(state.picks, start=1):
        player = by_id.get(pick.player_id)
        if player is None:
            raise PostDraftReportError(
                f"Selected player {pick.player_id} is absent from the frozen player pool."
            )
        if pick.overall_pick != expected_pick:
            raise PostDraftReportError("Active picks are not in contiguous overall-pick order.")
        if pick.position != player.position:
            raise PostDraftReportError(
                f"Selected player {pick.player_id} has conflicting frozen position evidence."
            )
        if not isclose(pick.projected_points, player.p50, rel_tol=0.0, abs_tol=1e-9):
            raise PostDraftReportError(
                f"Selected player {pick.player_id} does not use the frozen P50 projection."
            )
    return by_id


def _assign(
    players: tuple[FrozenDraftPlayer, ...],
    state: DraftState,
) -> RosterAssignment:
    return assign_roster(
        tuple(RosterPlayer(player.player_id, player.position, player.p50) for player in players),
        state.rules,
    )


def _replacement_by_position(
    players: tuple[FrozenDraftPlayer, ...],
    state: DraftState,
) -> dict[str, float]:
    draftable = _draftable_positions(state)
    frame = pd.DataFrame.from_records(
        {
            "player_id": player.player_id,
            "position": player.position,
            "projected_points": player.p50,
        }
        for player in players
        if player.position in draftable
    )
    if frame.empty:
        return {}
    levels = replacement_levels(frame, state.rules)
    return {
        position: float(level.last_starter_points)
        for position, level in levels.items()
        if level.last_starter_points is not None
    }


def _analyze_players(
    picks: tuple[DraftPick, ...],
    by_id: dict[str, FrozenDraftPlayer],
    assignment: RosterAssignment,
    replacement: dict[str, float],
) -> tuple[PostDraftPlayer, ...]:
    results: list[PostDraftPlayer] = []
    for pick in picks:
        player = by_id[pick.player_id]
        slot = assignment.slot_for_player(player.player_id)
        if slot is None:
            raise PostDraftReportError(f"Player {player.player_id} has no legal roster slot.")
        role: LineupRole = "bench" if slot == "BENCH" else "starter"
        line = replacement.get(player.position)
        has_interval = player.has_outcome_interval
        floor = player.p10 if has_interval else None
        ceiling = player.p90 if has_interval else None
        floor_vorp = None if line is None or floor is None else floor - line
        if line is None:
            risk: ReplacementRiskStatus = "replacement_unavailable"
        elif floor is None:
            risk = "uncertainty_unavailable"
        elif floor < line:
            risk = "floor_below_replacement"
        else:
            risk = "floor_at_or_above_replacement"
        results.append(
            PostDraftPlayer(
                player_id=player.player_id,
                display_name=player.display_name,
                position=player.position,
                overall_pick=pick.overall_pick,
                round=pick.round,
                lineup_role=role,
                lineup_slot=slot,
                p10=floor,
                p50=player.p50,
                p90=ceiling,
                projection_status=player.prediction_status,
                projection_source=player.projection_source,
                projection_method=player.projection_method,
                outcome_interval_available=has_interval,
                market_source=player.market_source,
                market_snapshot_id=player.market_snapshot_id,
                market_captured_at=(
                    None
                    if player.market_captured_at is None
                    else player.market_captured_at.isoformat()
                ),
                mapping_confidence=player.mapping_confidence,
                average_pick=player.average_pick,
                pick_value_vs_adp=(
                    None
                    if player.average_pick is None
                    else float(pick.overall_pick) - player.average_pick
                ),
                replacement_points=line,
                p50_vorp=None if line is None else player.p50 - line,
                floor_vorp=floor_vorp,
                replacement_risk_status=risk,
            )
        )
    return tuple(results)


def _projection_summary(players: tuple[FrozenDraftPlayer, ...]) -> ProjectionSummary:
    count = len(players)
    interval_count = sum(player.has_outcome_interval for player in players)
    coverage = interval_count / count if count else 0.0
    fully_measured = count > 0 and interval_count == count
    return ProjectionSummary(
        player_count=count,
        floor=float(sum(player.p10 for player in players)) if fully_measured else None,
        median=float(sum(player.p50 for player in players)),
        ceiling=float(sum(player.p90 for player in players)) if fully_measured else None,
        interval_player_count=interval_count,
        interval_coverage=coverage,
    )


def _lineup_summary(
    players: tuple[FrozenDraftPlayer, ...],
    assignment: RosterAssignment,
) -> LineupSummary:
    by_id = {player.player_id: player for player in players}
    starter_ids = tuple(item.player.player_id for item in assignment.starters)
    bench_ids = tuple(player.player_id for player in assignment.bench)
    starters = tuple(by_id[player_id] for player_id in starter_ids)
    bench = tuple(by_id[player_id] for player_id in bench_ids)
    return LineupSummary(
        starter_player_ids=starter_ids,
        bench_player_ids=bench_ids,
        starter_slots_filled=len(starter_ids),
        starter_slot_count=assignment.starter_slot_count,
        starter_coverage=assignment.starter_coverage,
        starters=_projection_summary(starters),
        bench=_projection_summary(bench),
        roster=_projection_summary(players),
    )


def _position_capital(
    players: tuple[PostDraftPlayer, ...],
    replacement: dict[str, float],
) -> tuple[PositionDraftCapital, ...]:
    results: list[PositionDraftCapital] = []
    total_count = len(players)
    for position in sorted({player.position for player in players}):
        position_players = tuple(player for player in players if player.position == position)
        overall_picks = tuple(player.overall_pick for player in position_players)
        rounds = tuple(player.round for player in position_players)
        adp_values = tuple(
            player.pick_value_vs_adp
            for player in position_players
            if player.pick_value_vs_adp is not None
        )
        line = replacement.get(position)
        results.append(
            PositionDraftCapital(
                position=position,
                player_count=len(position_players),
                starter_count=sum(player.lineup_role == "starter" for player in position_players),
                bench_count=sum(player.lineup_role == "bench" for player in position_players),
                overall_picks=overall_picks,
                rounds=rounds,
                earliest_overall_pick=min(overall_picks),
                mean_overall_pick=sum(overall_picks) / len(overall_picks),
                pick_share=len(position_players) / total_count,
                mapped_adp_count=len(adp_values),
                mean_pick_value_vs_adp=(
                    None if not adp_values else float(sum(adp_values) / len(adp_values))
                ),
                replacement_points=line,
                total_p50_vorp=(
                    None
                    if line is None
                    else float(sum(player.p50 - line for player in position_players))
                ),
            )
        )
    return tuple(results)


def _adp_summary(players: tuple[PostDraftPlayer, ...]) -> AdpValueSummary:
    values = tuple(
        player.pick_value_vs_adp for player in players if player.pick_value_vs_adp is not None
    )
    count = len(players)
    return AdpValueSummary(
        observed_players=len(values),
        missing_players=count - len(values),
        coverage=len(values) / count if count else 0.0,
        total_pick_value_vs_adp=None if not values else float(sum(values)),
        mean_pick_value_vs_adp=None if not values else float(sum(values) / len(values)),
    )


def _replacement_risk(players: tuple[PostDraftPlayer, ...]) -> ReplacementRiskSummary:
    starters = tuple(player for player in players if player.lineup_role == "starter")
    evaluated = tuple(
        player
        for player in starters
        if player.floor_vorp is not None and player.replacement_points is not None
    )
    return ReplacementRiskSummary(
        starter_players=len(starters),
        evaluated_starters=len(evaluated),
        starters_below_replacement_floor=sum(
            player.replacement_risk_status == "floor_below_replacement" for player in starters
        ),
        unknown_starter_floors=len(starters) - len(evaluated),
        floor_shortfall_points=float(
            sum(
                max(0.0, -player.floor_vorp)
                for player in evaluated
                if player.floor_vorp is not None
            )
        ),
    )


def _strategy_comparisons(
    state: DraftState,
    pool: tuple[FrozenDraftPlayer, ...],
    team_picks: tuple[DraftPick, ...],
    replacement: dict[str, float],
    actual_lineup: LineupSummary,
) -> tuple[StrategyComparison, ...]:
    common_assumptions = (
        "Uses the selected team's recorded pick numbers and holds recorded opponent picks fixed.",
        "Chooses only a player that keeps the counterfactual roster legal under exact assignment.",
        "It is a descriptive counterfactual, not a forecast of opponent reactions or "
        "team outcomes.",
    )
    specs = (
        (
            "projection_greedy",
            "Highest P50 available",
            "Selects the legal available player with the highest frozen median projection.",
        ),
        (
            "vorp_greedy",
            "Highest ruleset VORP available",
            "Selects the legal available player with the highest P50 minus replacement value.",
        ),
        (
            "market_consensus",
            "Earliest ADP available",
            "Selects the legal available player with the earliest reviewed market ADP.",
        ),
    )
    comparisons: list[StrategyComparison] = []
    draftable_pool = tuple(
        player for player in pool if player.position in _draftable_positions(state)
    )
    market_missing = sum(not player.has_market_evidence for player in draftable_pool)
    for strategy_id, label, description in specs:
        if strategy_id == "market_consensus" and market_missing:
            comparisons.append(
                StrategyComparison(
                    strategy_id=strategy_id,
                    label=label,
                    description=description,
                    available=False,
                    selections=(),
                    starters=None,
                    roster=None,
                    starter_median_difference=None,
                    roster_median_difference=None,
                    unavailable_reason=(
                        "A market-consensus baseline requires ADP for every draftable frozen "
                        f"player; {market_missing}/{len(draftable_pool)} are missing."
                    ),
                    assumptions=common_assumptions,
                )
            )
            continue
        selected = _run_strategy(
            strategy_id,
            state,
            draftable_pool,
            team_picks,
            replacement,
        )
        if selected is None:
            comparisons.append(
                StrategyComparison(
                    strategy_id=strategy_id,
                    label=label,
                    description=description,
                    available=False,
                    selections=(),
                    starters=None,
                    roster=None,
                    starter_median_difference=None,
                    roster_median_difference=None,
                    unavailable_reason="No legal candidate could be selected at every team pick.",
                    assumptions=common_assumptions,
                )
            )
            continue
        selected_players, selections = selected
        baseline_assignment = _assign(selected_players, state)
        baseline_lineup = _lineup_summary(selected_players, baseline_assignment)
        comparisons.append(
            StrategyComparison(
                strategy_id=strategy_id,
                label=label,
                description=description,
                available=True,
                selections=selections,
                starters=baseline_lineup.starters,
                roster=baseline_lineup.roster,
                starter_median_difference=(
                    actual_lineup.starters.median - baseline_lineup.starters.median
                ),
                roster_median_difference=(
                    actual_lineup.roster.median - baseline_lineup.roster.median
                ),
                unavailable_reason=None,
                assumptions=common_assumptions,
            )
        )
    return tuple(comparisons)


def _run_strategy(
    strategy_id: str,
    state: DraftState,
    pool: tuple[FrozenDraftPlayer, ...],
    team_picks: tuple[DraftPick, ...],
    replacement: dict[str, float],
) -> tuple[tuple[FrozenDraftPlayer, ...], tuple[BaselineSelection, ...]] | None:
    by_id = {player.player_id: player for player in pool}
    selected: list[FrozenDraftPlayer] = []
    selections: list[BaselineSelection] = []
    selected_slot = team_picks[0].draft_slot if team_picks else state.user_draft_slot
    opponent_picks = tuple(pick for pick in state.picks if pick.draft_slot != selected_slot)
    for team_pick in team_picks:
        unavailable = {
            pick.player_id for pick in opponent_picks if pick.overall_pick < team_pick.overall_pick
        }
        unavailable.update(player.player_id for player in selected)
        candidates = tuple(player for player in pool if player.player_id not in unavailable)
        if strategy_id == "projection_greedy":
            ranked = sorted(candidates, key=lambda player: (-player.p50, player.player_id))
        elif strategy_id == "vorp_greedy":
            ranked = sorted(
                (player for player in candidates if player.position in replacement),
                key=lambda player: (
                    -(player.p50 - replacement[player.position]),
                    player.player_id,
                ),
            )
        elif strategy_id == "market_consensus":
            ranked = sorted(
                (player for player in candidates if player.average_pick is not None),
                key=lambda player: (
                    float(player.average_pick) if player.average_pick is not None else float("inf"),
                    -player.p50,
                    player.player_id,
                ),
            )
        else:
            raise ValueError(f"Unsupported strategy baseline: {strategy_id}.")
        choice = next(
            (player for player in ranked if _assign(tuple([*selected, player]), state).legal),
            None,
        )
        if choice is None:
            return None
        selected.append(by_id[choice.player_id])
        selections.append(BaselineSelection(team_pick.overall_pick, choice.player_id))
    return tuple(selected), tuple(selections)


def _ruleset_insights(
    state: DraftState,
    players: tuple[PostDraftPlayer, ...],
    assignment: RosterAssignment,
    capital: tuple[PositionDraftCapital, ...],
    adp: AdpValueSummary,
    risk: ReplacementRiskSummary,
) -> tuple[tuple[RosterInsight, ...], tuple[RosterInsight, ...]]:
    strengths: list[RosterInsight] = []
    weaknesses: list[RosterInsight] = []
    if assignment.starter_coverage == 1.0:
        strengths.append(
            RosterInsight(
                code="starter_coverage_complete",
                title="Every ruleset starter slot is filled",
                detail="The exact eligibility matcher can fill every direct and flexible slot.",
                metric_name="starter_coverage",
                metric_value=1.0,
            )
        )
    else:
        weaknesses.append(
            RosterInsight(
                code="starter_slots_open",
                title="Starter slots remain open",
                detail=(
                    f"The current roster fills {len(assignment.starters)}/"
                    f"{assignment.starter_slot_count} ruleset starter slots."
                ),
                metric_name="starter_coverage",
                metric_value=assignment.starter_coverage,
            )
        )

    capital_by_position = {row.position: row for row in capital}
    required_positions = tuple(sorted(state.rules.starters))
    for position in required_positions:
        drafted = capital_by_position.get(position)
        direct_required = state.rules.starters[position]
        direct_filled = sum(
            player.lineup_role == "starter" and player.position == position for player in players
        )
        if direct_filled < direct_required:
            weaknesses.append(
                RosterInsight(
                    code="direct_position_shortfall",
                    title=f"{position} starter demand is not covered",
                    detail=(
                        f"This ruleset requires {direct_required} direct {position} slot(s); "
                        f"the current best lineup starts {direct_filled}."
                    ),
                    position=position,
                    metric_name="direct_starters_filled",
                    metric_value=float(direct_filled),
                )
            )
        if drafted is None or drafted.total_p50_vorp is None:
            continue
        if drafted.total_p50_vorp > 0:
            strengths.append(
                RosterInsight(
                    code="positive_position_vorp",
                    title=f"{position} adds value over the ruleset replacement line",
                    detail=(
                        f"Selected {position} players total {drafted.total_p50_vorp:.1f} "
                        "P50 points above the transparent replacement estimate."
                    ),
                    position=position,
                    metric_name="total_p50_vorp",
                    metric_value=drafted.total_p50_vorp,
                )
            )
        else:
            weaknesses.append(
                RosterInsight(
                    code="nonpositive_position_vorp",
                    title=f"{position} does not clear the ruleset replacement line",
                    detail=(
                        f"Selected {position} players total {drafted.total_p50_vorp:.1f} "
                        "P50 points versus replacement."
                    ),
                    position=position,
                    metric_name="total_p50_vorp",
                    metric_value=drafted.total_p50_vorp,
                )
            )

    if adp.mean_pick_value_vs_adp is not None:
        target = strengths if adp.mean_pick_value_vs_adp > 0 else weaknesses
        target.append(
            RosterInsight(
                code="adp_draft_value" if adp.mean_pick_value_vs_adp > 0 else "adp_reach",
                title=(
                    "Drafted later than reviewed ADP on average"
                    if adp.mean_pick_value_vs_adp > 0
                    else "Drafted earlier than reviewed ADP on average"
                ),
                detail=(
                    f"Across {adp.observed_players} mapped selections, the mean pick-minus-ADP "
                    f"difference is {adp.mean_pick_value_vs_adp:.1f}."
                ),
                metric_name="mean_pick_value_vs_adp",
                metric_value=adp.mean_pick_value_vs_adp,
            )
        )
    if risk.starters_below_replacement_floor:
        weaknesses.append(
            RosterInsight(
                code="replacement_floor_exposure",
                title="Starter floors cross the replacement line",
                detail=(
                    f"{risk.starters_below_replacement_floor} measured starter floor(s) fall "
                    "below their position's replacement estimate."
                ),
                metric_name="starters_below_replacement_floor",
                metric_value=float(risk.starters_below_replacement_floor),
            )
        )
    return tuple(strengths), tuple(weaknesses)


def _limitations(
    state: DraftState,
    team_complete: bool,
    players: tuple[PostDraftPlayer, ...],
    comparisons: tuple[StrategyComparison, ...],
) -> tuple[str, ...]:
    limitations = [
        "This is a descriptive draft-only report; it does not estimate wins, playoffs, "
        "or championship probability.",
        "Replacement levels are a transparent ruleset-demand heuristic, not a learned "
        "waiver-wire model.",
        "Strategy baselines hold recorded opponent selections fixed and do not model "
        "counterfactual opponent reactions.",
    ]
    if not state.complete or not team_complete:
        limitations.append(
            "The draft or selected roster is incomplete, so all roster values and insights "
            "are provisional."
        )
    if not players:
        limitations.append("The selected team has no recorded picks; projection totals are zero.")
    missing_adp = sum(player.average_pick is None for player in players)
    if missing_adp:
        limitations.append(
            f"Value versus ADP is unavailable for {missing_adp}/{len(players)} selected "
            "players; missing market data is not imputed."
        )
    point_only = sum(player.p10 is None or player.p90 is None for player in players)
    if point_only:
        limitations.append(
            f"Floor and ceiling are unavailable for {point_only}/{len(players)} selected "
            "point-only projections; zero spread is not treated as low risk."
        )
    elif players:
        limitations.append(
            "Reported floor and ceiling totals sum marginal player intervals; they are not "
            "calibrated team quantiles and omit player correlations."
        )
    unavailable = tuple(comparison.label for comparison in comparisons if not comparison.available)
    if unavailable:
        limitations.append(
            f"Unavailable strategy baselines: {', '.join(unavailable)}. Their missing "
            "inputs are not synthesized."
        )
    return tuple(limitations)


def _draftable_positions(state: DraftState) -> frozenset[str]:
    positions = set(state.rules.starters)
    positions.update(position for flex in state.rules.flex_slots for position in flex.eligible)
    return frozenset(positions)
