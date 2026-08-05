from __future__ import annotations

import pytest

from fantasy_draft_ai.models.evaluation.splits import expanding_season_splits


def test_expanding_season_splits_are_ordered_disjoint_and_deterministic() -> None:
    kwargs = {
        "seasons": [2024, 2020, 2022, 2021, 2023, 2022],
        "first_evaluation_season": 2022,
        "last_evaluation_season": 2024,
    }

    first = expanding_season_splits(**kwargs)
    second = expanding_season_splits(**kwargs)

    assert first == second
    assert [split.evaluation_season for split in first] == [2022, 2023, 2024]
    assert [tuple(split.training_seasons) for split in first] == [
        (2020, 2021),
        (2020, 2021, 2022),
        (2020, 2021, 2022, 2023),
    ]
    for split in first:
        assert split.evaluation_season not in split.training_seasons
        assert max(split.training_seasons) < split.evaluation_season


def test_expanding_season_splits_use_available_seasons_without_inventing_gaps() -> None:
    splits = expanding_season_splits(
        seasons=[2018, 2020, 2023],
        first_evaluation_season=2020,
        last_evaluation_season=2023,
    )

    assert [split.evaluation_season for split in splits] == [2020, 2023]
    assert [tuple(split.training_seasons) for split in splits] == [
        (2018,),
        (2018, 2020),
    ]


@pytest.mark.parametrize(
    ("available_seasons", "first_season", "last_season"),
    [
        ([2022], 2022, 2022),
        ([2020, 2021, 2022], 2023, 2022),
        ([], 2022, 2023),
    ],
)
def test_expanding_season_splits_reject_invalid_or_unusable_ranges(
    available_seasons: list[int], first_season: int, last_season: int
) -> None:
    with pytest.raises(ValueError):
        expanding_season_splits(
            seasons=available_seasons,
            first_evaluation_season=first_season,
            last_evaluation_season=last_season,
        )
