"""Regression tests for transparent, health-neutral age adjustments."""

import pytest

from fantasy_draft_ai.features.player_seasons import _age_adjustment


def test_running_back_age_adjustment_is_smooth_and_bounded() -> None:
    before_boundary = _age_adjustment("RB", 27.999)
    after_boundary = _age_adjustment("RB", 28.001)

    assert before_boundary == pytest.approx(0.94003)
    assert after_boundary == pytest.approx(0.93997)
    assert abs(before_boundary - after_boundary) < 0.001
    assert _age_adjustment("RB", 40.0) == 0.82


def test_running_back_age_adjustment_does_not_encode_missed_games() -> None:
    jonathan_taylor_factor = _age_adjustment("RB", 27.617)
    christian_mccaffrey_factor = _age_adjustment("RB", 30.235)

    assert jonathan_taylor_factor == pytest.approx(0.95149)
    assert christian_mccaffrey_factor == pytest.approx(0.87295)
    assert jonathan_taylor_factor > christian_mccaffrey_factor


@pytest.mark.parametrize("position", ("QB", "RB", "WR", "TE"))
def test_missing_age_is_neutral(position: str) -> None:
    assert _age_adjustment(position, None) == 1.0
