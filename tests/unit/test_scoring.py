from fantasy_draft_ai.scoring.engine import (
    PlayerStatLine,
    ScoringRules,
    YardageBonus,
    score_player,
)


def test_ppr_and_half_ppr_differ_only_by_reception_value() -> None:
    stats = PlayerStatLine(position="WR", receptions=8, receiving_yards=100, receiving_tds=1)
    ppr = score_player(stats, ScoringRules(reception=1))
    half = score_player(stats, ScoringRules(reception=0.5))
    assert ppr == 24
    assert half == 20


def test_four_and_six_point_passing_touchdowns() -> None:
    stats = PlayerStatLine(position="QB", passing_yards=250, passing_tds=3)
    four = score_player(stats, ScoringRules(passing_td=4))
    six = score_player(stats, ScoringRules(passing_td=6))
    assert four == 22
    assert six == 28


def test_turnovers_two_point_bonuses_and_te_premium() -> None:
    stats = PlayerStatLine(
        position="TE",
        receptions=5,
        receiving_yards=105,
        receiving_tds=1,
        two_point_conversions=1,
        fumbles_lost=1,
    )
    rules = ScoringRules(
        reception=1,
        position_reception_bonus={"te": 0.5},
        yardage_bonuses=(YardageBonus(category="receiving_yards", threshold=100, points=3),),
    )
    assert score_player(stats, rules) == 27
