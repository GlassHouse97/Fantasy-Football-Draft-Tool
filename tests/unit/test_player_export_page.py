"""Focused contracts for the Player Export presentation merge."""

import math
from pathlib import Path

import pandas as pd
import pytest

from fantasy_draft_ai.services.league_setup import load_reference_rules
from fantasy_draft_ai.services.player_evaluation import PlayerAdpComparison
from fantasy_draft_ai.ui.pages.player_export import (
    EXTREME_RANK_DISAGREEMENT_THRESHOLD,
    _consensus_rankings,
    _default_draft_helper_rules,
    _extreme_rank_disagreements,
    _model_vs_market_delta,
    _player_export_frame,
)

PROJECT_ROOT = Path(__file__).resolve().parents[2]


def _row(
    player_id: str,
    name: str,
    *,
    fantasypros_avg: float | None = 2.0,
) -> PlayerAdpComparison:
    return PlayerAdpComparison(
        player_id=player_id,
        display_name=name,
        position="RB",
        yahoo_adp=1.0,
        sleeper_adp=2.0,
        rtsports_adp=3.0,
        fantasypros_avg=fantasypros_avg,
        source_count=4,
    )


def test_player_export_is_consensus_first_with_nullable_integer_comparisons() -> None:
    frame = _player_export_frame(
        (
            _row("market-only", "Market Player", fantasypros_avg=4.0),
            _row("projected", "Projected Player", fantasypros_avg=2.0),
            _row("missing-market", "No Consensus", fantasypros_avg=None),
        ),
        {"projected": 7},
    )

    assert frame["Player"].tolist() == [
        "Projected Player",
        "Market Player",
        "No Consensus",
    ]
    assert frame.columns[:6].tolist() == [
        "Player ID",
        "Consensus Rank",
        "Player",
        "Position",
        "Experimental Model Rank",
        "Model vs Market Delta",
    ]
    assert str(frame["Consensus Rank"].dtype) == "Int64"
    assert str(frame["Experimental Model Rank"].dtype) == "Int64"
    assert str(frame["Model vs Market Delta"].dtype) == "Int64"
    assert frame.loc[0, "Consensus Rank"] == 1
    assert frame.loc[0, "Experimental Model Rank"] == 7
    assert frame.loc[0, "Model vs Market Delta"] == -6
    assert pd.isna(frame.loc[1, "Experimental Model Rank"])
    assert pd.isna(frame.loc[1, "Model vs Market Delta"])
    assert pd.isna(frame.loc[2, "Consensus Rank"])
    assert pd.isna(frame.loc[2, "Model vs Market Delta"])
    csv_text = frame.to_csv(index=False)
    assert "No Consensus" in csv_text
    assert ",0," not in csv_text


def test_consensus_rank_is_derived_from_avg_with_shared_ties_and_blank_invalids() -> None:
    rows = (
        _row("later", "Later", fantasypros_avg=8.5),
        _row("tie-b", "Zulu Tie", fantasypros_avg=3.0),
        _row("none", "Missing", fantasypros_avg=None),
        _row("tie-a", "Alpha Tie", fantasypros_avg=3.0),
        _row("zero", "Zero", fantasypros_avg=0.0),
        _row("nan", "NaN", fantasypros_avg=math.nan),
    )

    rankings = _consensus_rankings(rows)
    frame = _player_export_frame(rows, {})

    assert rankings == {"tie-a": 1, "tie-b": 1, "later": 3}
    assert frame["Player"].tolist() == [
        "Alpha Tie",
        "Zulu Tie",
        "Later",
        "Missing",
        "NaN",
        "Zero",
    ]
    assert frame["Consensus Rank"].tolist()[:3] == [1, 1, 3]
    assert frame["Consensus Rank"].isna().sum() == 3


def test_filtered_export_preserves_full_board_consensus_rank() -> None:
    full_board = (
        _row("first", "First", fantasypros_avg=1.0),
        _row("second", "Second", fantasypros_avg=2.0),
        _row("third", "Third", fantasypros_avg=3.0),
    )

    frame = _player_export_frame(
        (full_board[2],),
        {"third": 2},
        consensus_rankings=_consensus_rankings(full_board),
    )

    assert frame.loc[0, "Player"] == "Third"
    assert frame.loc[0, "Consensus Rank"] == 3
    assert frame.loc[0, "Model vs Market Delta"] == 1


@pytest.mark.parametrize(
    ("consensus_rank", "model_rank", "expected"),
    [
        (20, 5, 15),
        (5, 20, -15),
        (8, 8, 0),
        (None, 8, None),
        (8, None, None),
    ],
)
def test_model_vs_market_delta_has_plain_directional_semantics(
    consensus_rank: int | None,
    model_rank: int | None,
    expected: int | None,
) -> None:
    assert _model_vs_market_delta(consensus_rank, model_rank) == expected


def test_extreme_disagreements_include_threshold_and_sort_deterministically() -> None:
    frame = pd.DataFrame(
        {
            "Player": ["At Threshold", "Largest", "Below", "Same Gap Alpha", "Blank"],
            "Model vs Market Delta": pd.array([12, -30, 11, 30, None], dtype="Int64"),
        }
    )

    flags = _extreme_rank_disagreements(
        frame,
        threshold=EXTREME_RANK_DISAGREEMENT_THRESHOLD,
    )

    assert flags == (
        ("Largest", -30),
        ("Same Gap Alpha", 30),
        ("At Threshold", 12),
    )


def test_extreme_disagreements_reject_nonpositive_threshold() -> None:
    with pytest.raises(ValueError, match="must be positive"):
        _extreme_rank_disagreements(pd.DataFrame(), threshold=0)


def test_draft_helper_rank_uses_the_quick_start_standard_roster() -> None:
    reference = load_reference_rules(PROJECT_ROOT / "configs" / "example_ppr_12_team.yaml")

    rules = _default_draft_helper_rules(reference)

    assert rules.teams == 12
    assert rules.starters["WR"] == 2
    assert len(rules.flex_slots) == 1
    assert rules.scoring.reception == 1.0
