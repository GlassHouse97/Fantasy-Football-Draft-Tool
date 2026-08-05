"""Deterministic expanding-season validation splits."""

from __future__ import annotations

from collections.abc import Iterable
from dataclasses import dataclass


@dataclass(frozen=True)
class ChronologicalFold:
    """Training prediction seasons strictly preceding one evaluation season."""

    training_seasons: tuple[int, ...]
    evaluation_season: int
    label: str


def expanding_season_splits(
    seasons: Iterable[int],
    *,
    first_evaluation_season: int | None = None,
    last_evaluation_season: int | None = None,
    min_training_seasons: int = 1,
) -> tuple[ChronologicalFold, ...]:
    """Return ordered expanding folds without random or future rows.

    ``seasons`` are target/prediction seasons, not source-stat seasons. The final
    fold is labeled ``test`` and earlier folds are labeled ``validation``.
    """

    ordered = tuple(sorted(set(int(season) for season in seasons)))
    if min_training_seasons < 1:
        raise ValueError("min_training_seasons must be at least one.")
    if len(ordered) <= min_training_seasons:
        raise ValueError("Not enough seasons for the requested chronological split.")
    first = first_evaluation_season or ordered[min_training_seasons]
    last = last_evaluation_season or ordered[-1]
    if first > last:
        raise ValueError("The first evaluation season cannot follow the last.")
    evaluation_seasons = tuple(season for season in ordered if first <= season <= last)
    if not evaluation_seasons:
        raise ValueError("No available seasons fall inside the evaluation bounds.")
    folds: list[ChronologicalFold] = []
    for evaluation_season in evaluation_seasons:
        training = tuple(season for season in ordered if season < evaluation_season)
        if len(training) < min_training_seasons:
            continue
        folds.append(
            ChronologicalFold(
                training_seasons=training,
                evaluation_season=evaluation_season,
                label="validation",
            )
        )
    if not folds:
        raise ValueError("No fold has enough strictly earlier training seasons.")
    final = folds[-1]
    folds[-1] = ChronologicalFold(
        training_seasons=final.training_seasons,
        evaluation_season=final.evaluation_season,
        label="test",
    )
    return tuple(folds)
