"""Ruleset-aware starter demand and transparent replacement values."""

from __future__ import annotations

from dataclasses import dataclass
from math import ceil

import pandas as pd

from fantasy_draft_ai.rules.models import LeagueRules


@dataclass(frozen=True)
class PositionDemand:
    position: str
    direct_starters: int
    flex_eligible_slots: int


@dataclass(frozen=True)
class ReplacementLevel:
    position: str
    estimated_starters: int
    estimated_benched: int
    last_starter_points: float | None
    waiver_percentile_points: float | None


def position_demand(rules: LeagueRules, position: str) -> PositionDemand:
    """Report certain direct demand and potential flexible demand separately."""

    normalized = position.upper()
    direct = rules.starters.get(normalized, 0) * rules.teams
    flexible = sum(
        slot.count * rules.teams for slot in rules.flex_slots if normalized in slot.eligible
    )
    return PositionDemand(normalized, direct, flexible)


def _validate_projection_frame(projections: pd.DataFrame) -> pd.DataFrame:
    required = {"player_id", "position", "projected_points"}
    missing = required - set(projections.columns)
    if missing:
        raise ValueError(f"Projection frame is missing: {', '.join(sorted(missing))}")
    frame = projections.loc[:, ["player_id", "position", "projected_points"]].copy()
    frame["position"] = frame["position"].astype(str).str.upper()
    frame["projected_points"] = pd.to_numeric(frame["projected_points"], errors="raise")
    if frame["player_id"].duplicated().any():
        raise ValueError("Projection frame contains duplicate player_id values.")
    return frame.sort_values("projected_points", ascending=False, kind="stable").reset_index(
        drop=True
    )


def _take_best_available(
    frame: pd.DataFrame,
    selected: set[str],
    eligible: tuple[str, ...],
    count: int,
) -> list[tuple[str, str]]:
    candidates = frame[
        frame["position"].isin(eligible) & ~frame["player_id"].astype(str).isin(selected)
    ]
    taken: list[tuple[str, str]] = []
    for row in candidates.head(count).itertuples(index=False):
        player_id = str(row.player_id)
        selected.add(player_id)
        taken.append((player_id, str(row.position)))
    return taken


def replacement_levels(
    projections: pd.DataFrame,
    rules: LeagueRules,
    *,
    waiver_percentile: float = 0.75,
) -> dict[str, ReplacementLevel]:
    """Estimate last-starter and post-bench waiver thresholds.

    Direct starters are filled first. FLEX/SUPERFLEX and bench slots are then filled
    greedily by the highest projected remaining eligible player. This is a transparent
    roster-demand heuristic, not a learned draft-behavior model.
    """

    if not 0 <= waiver_percentile <= 1:
        raise ValueError("waiver_percentile must be between 0 and 1.")
    frame = _validate_projection_frame(projections)
    selected: set[str] = set()
    starter_counts: dict[str, int] = {}

    for position, count_per_team in rules.starters.items():
        taken = _take_best_available(frame, selected, (position,), count_per_team * rules.teams)
        starter_counts[position] = len(taken)

    for flex in rules.flex_slots:
        taken = _take_best_available(frame, selected, flex.eligible, flex.count * rules.teams)
        for _, position in taken:
            starter_counts[position] = starter_counts.get(position, 0) + 1

    starter_ids = selected.copy()
    bench_taken = _take_best_available(
        frame,
        selected,
        tuple(sorted(set(frame["position"]))),
        rules.bench * rules.teams,
    )
    bench_counts: dict[str, int] = {}
    for _, position in bench_taken:
        bench_counts[position] = bench_counts.get(position, 0) + 1

    results: dict[str, ReplacementLevel] = {}
    for position in sorted(set(frame["position"]) | set(starter_counts)):
        position_frame = frame[frame["position"] == position]
        starter_rows = position_frame[position_frame["player_id"].astype(str).isin(starter_ids)]
        last_starter = (
            float(starter_rows["projected_points"].min()) if not starter_rows.empty else None
        )
        remaining = position_frame[~position_frame["player_id"].astype(str).isin(selected)]
        waiver_value: float | None = None
        if not remaining.empty:
            rank = min(ceil(waiver_percentile * len(remaining)) - 1, len(remaining) - 1)
            rank = max(rank, 0)
            waiver_value = float(
                remaining.sort_values("projected_points")["projected_points"].iloc[rank]
            )
        results[position] = ReplacementLevel(
            position=position,
            estimated_starters=starter_counts.get(position, 0),
            estimated_benched=bench_counts.get(position, 0),
            last_starter_points=last_starter,
            waiver_percentile_points=waiver_value,
        )
    return results


def value_over_replacement(projected_points: float, replacement_points: float | None) -> float:
    """Calculate VORP while requiring an explicit replacement baseline."""

    if replacement_points is None:
        raise ValueError("Replacement points are unavailable for this position.")
    return projected_points - replacement_points
