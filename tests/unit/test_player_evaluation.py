"""Player Evaluation market-comparison contract tests."""

from datetime import UTC, datetime, timedelta
from pathlib import Path
from types import SimpleNamespace

import duckdb

from fantasy_draft_ai.models.adp.movement import AdpIdentity
from fantasy_draft_ai.services.player_evaluation import (
    build_player_export_board,
    load_player_export_board,
)


def _market_row(
    *,
    source: str,
    player_id: str | None,
    average_pick: float,
    captured_at: datetime,
    confidence: str,
    raw_id: str,
    scoring_format: str = "overall",
    team_count: int = 12,
) -> SimpleNamespace:
    return SimpleNamespace(
        source=source,
        identity=AdpIdentity(source=source, raw_source_row_id=raw_id, player_id=player_id),
        average_pick=average_pick,
        captured_at=captured_at,
        mapping_confidence=confidence,
        snapshot_id=f"snapshot-{raw_id}",
        raw_source_row_id=raw_id,
        scoring_format=scoring_format,
        team_count=team_count,
    )


def _projection_board() -> SimpleNamespace:
    return SimpleNamespace(
        available=True,
        run=SimpleNamespace(prediction_season=2026),
        rows=(
            SimpleNamespace(player_id="player-a", display_name="Alpha Runner", position="RB"),
            SimpleNamespace(player_id="player-c", display_name="Gamma Passer", position="QB"),
        ),
    )


def _config(warehouse: Path) -> SimpleNamespace:
    return SimpleNamespace(
        project=SimpleNamespace(prediction_season=2026),
        paths=SimpleNamespace(warehouse=warehouse),
        resolve=lambda path: path,
    )


def _create_warehouse(connection: duckdb.DuckDBPyConnection) -> None:
    connection.execute(
        """
        CREATE TABLE players (
            player_id VARCHAR PRIMARY KEY,
            display_name VARCHAR NOT NULL,
            canonical_position VARCHAR
        );
        CREATE TABLE adp_snapshot_metadata (
            snapshot_id VARCHAR PRIMARY KEY,
            source VARCHAR NOT NULL,
            captured_at TIMESTAMPTZ NOT NULL,
            season INTEGER NOT NULL,
            scoring_format VARCHAR NOT NULL,
            team_count INTEGER NOT NULL,
            position_scope VARCHAR NOT NULL,
            row_count INTEGER NOT NULL,
            loaded_at TIMESTAMPTZ NOT NULL
        );
        CREATE TABLE adp_snapshots (
            snapshot_id VARCHAR NOT NULL,
            source VARCHAR NOT NULL,
            captured_at TIMESTAMPTZ NOT NULL,
            season INTEGER NOT NULL,
            scoring_format VARCHAR NOT NULL,
            team_count INTEGER NOT NULL,
            player_id VARCHAR,
            player_name VARCHAR NOT NULL,
            position VARCHAR,
            average_pick DOUBLE,
            raw_source_row_id VARCHAR NOT NULL,
            mapping_confidence VARCHAR NOT NULL
        );
        """
    )


def test_player_export_uses_published_fantasypros_values_without_recomputing_avg() -> None:
    now = datetime(2026, 8, 24, 12, tzinfo=UTC)
    projections = SimpleNamespace(
        available=True,
        run=SimpleNamespace(prediction_season=2026),
        rows=(
            SimpleNamespace(player_id="player-a", display_name="Alpha Runner", position="RB"),
            SimpleNamespace(player_id="player-b", display_name="Beta Catcher", position="WR"),
        ),
    )
    market = SimpleNamespace(
        rows=(
            _market_row(
                source="yahoo",
                player_id="player-a",
                average_pick=20.0,
                captured_at=now - timedelta(days=1),
                confidence="reviewed",
                raw_id="yahoo-old",
            ),
            _market_row(
                source="yahoo",
                player_id="player-a",
                average_pick=18.0,
                captured_at=now,
                confidence="reviewed",
                raw_id="yahoo-new",
            ),
            _market_row(
                source="sleeper",
                player_id="player-a",
                average_pick=20.0,
                captured_at=now,
                confidence="exact",
                raw_id="sleeper-overall",
            ),
            _market_row(
                source="sleeper",
                player_id="player-a",
                average_pick=4.0,
                captured_at=now + timedelta(days=1),
                confidence="exact",
                raw_id="sleeper-newer-direct-ppr",
                scoring_format="ppr",
            ),
            _market_row(
                source="rtsports",
                player_id="player-a",
                average_pick=22.0,
                captured_at=now,
                confidence="high",
                raw_id="rtsports-a",
            ),
            _market_row(
                source="fantasypros",
                player_id="player-a",
                average_pick=19.7,
                captured_at=now,
                confidence="high",
                raw_id="fantasypros-a",
            ),
            _market_row(
                source="yahoo",
                player_id="player-b",
                average_pick=30.0,
                captured_at=now,
                confidence="exact",
                raw_id="yahoo-b",
            ),
            _market_row(
                source="fantasypros",
                player_id="player-b",
                average_pick=15.0,
                captured_at=now,
                confidence="low",
                raw_id="fantasypros-low-confidence",
            ),
            _market_row(
                source="espn",
                player_id="player-b",
                average_pick=25.0,
                captured_at=now,
                confidence="reviewed",
                raw_id="unsupported-espn",
            ),
        )
    )

    board = build_player_export_board(projections, market)

    assert board.available is True
    assert board.season == 2026
    assert len(board.rows) == 2
    alpha = next(row for row in board.rows if row.player_id == "player-a")
    beta = next(row for row in board.rows if row.player_id == "player-b")
    assert (alpha.yahoo_adp, alpha.sleeper_adp, alpha.rtsports_adp) == (18.0, 20.0, 22.0)
    assert alpha.fantasypros_avg == 19.7
    assert alpha.source_count == 4
    assert beta.yahoo_adp == 30.0
    assert beta.fantasypros_avg is None
    assert beta.source_count == 1
    assert alpha.as_record() == {
        "Player ID": "player-a",
        "Player": "Alpha Runner",
        "Position": "RB",
        "Yahoo ADP": 18.0,
        "Sleeper ADP": 20.0,
        "RTSports ADP": 22.0,
        "FantasyPros AVG": 19.7,
    }
    assert board.players_with_market_data == 2
    assert board.platform_observations == 5
    assert board.complete_comparisons == 1
    coverage = {row.key: row for row in board.coverage}
    assert set(coverage) == {"yahoo", "sleeper", "rtsports", "fantasypros"}
    assert coverage["yahoo"].latest_capture == now
    assert coverage["sleeper"].scope_label == "overall / 12-team / overall"
    assert coverage["fantasypros"].label == "FantasyPros AVG"


def test_player_export_stays_unavailable_without_projection_publication() -> None:
    projections = SimpleNamespace(available=False, run=None, rows=())
    market = SimpleNamespace(rows=())

    board = build_player_export_board(projections, market)

    assert board.available is False
    assert board.season is None
    assert board.rows == ()
    assert "projection publication is unavailable" in board.message


def test_direct_player_export_reads_fantasypros_aggregate_exact_scopes(
    tmp_path: Path,
) -> None:
    warehouse = tmp_path / "market.duckdb"
    now = datetime(2026, 8, 24, 12, tzinfo=UTC)
    with duckdb.connect(str(warehouse)) as connection:
        _create_warehouse(connection)
        connection.executemany(
            "INSERT INTO players VALUES (?, ?, ?)",
            (
                ("player-a", "Alpha Runner", "CB"),
                ("player-b", "Beta Catcher", "DB"),
                ("player-low", "Low Confidence", "TE"),
                ("player-fb", "Fullback Leakage", "FB"),
                ("player-lb", "Linebacker Leakage", "LB"),
            ),
        )
        metadata = (
            (
                "yahoo-old",
                "yahoo",
                now - timedelta(days=2),
                2026,
                "overall",
                12,
                "overall",
                1,
                now - timedelta(days=2),
            ),
            ("yahoo-new", "yahoo", now, 2026, "overall", 12, "overall", 5, now),
            (
                "yahoo-wrong-scope",
                "yahoo",
                now + timedelta(days=1),
                2026,
                "overall",
                10,
                "overall",
                1,
                now + timedelta(days=1),
            ),
            ("sleeper-overall", "sleeper", now, 2026, "overall", 12, "overall", 1, now),
            (
                "sleeper-newer-ppr",
                "sleeper",
                now + timedelta(days=1),
                2026,
                "ppr",
                12,
                "overall",
                1,
                now + timedelta(days=1),
            ),
            ("rtsports-new", "rtsports", now, 2026, "overall", 12, "overall", 1, now),
            (
                "fantasypros-new",
                "fantasypros",
                now,
                2026,
                "overall",
                12,
                "overall",
                2,
                now,
            ),
        )
        connection.executemany(
            "INSERT INTO adp_snapshot_metadata VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
            metadata,
        )
        snapshots = (
            (
                "yahoo-old",
                "yahoo",
                now - timedelta(days=2),
                2026,
                "overall",
                12,
                "player-a",
                "Alpha Runner",
                "RB",
                25.0,
                "yahoo-a-old",
                "exact",
            ),
            (
                "yahoo-new",
                "yahoo",
                now,
                2026,
                "overall",
                12,
                "player-a",
                "Alpha Runner",
                "WR",
                18.0,
                "yahoo-a-new",
                "exact",
            ),
            (
                "yahoo-new",
                "yahoo",
                now,
                2026,
                "overall",
                12,
                "player-b",
                "Beta Catcher",
                "WR",
                30.0,
                "yahoo-b",
                "high",
            ),
            (
                "yahoo-new",
                "yahoo",
                now,
                2026,
                "overall",
                12,
                "player-low",
                "Low Confidence",
                "TE",
                40.0,
                "yahoo-low",
                "low",
            ),
            (
                "yahoo-new",
                "yahoo",
                now,
                2026,
                "overall",
                12,
                "player-fb",
                "Fullback Leakage",
                "FB",
                41.0,
                "yahoo-fb",
                "exact",
            ),
            (
                "yahoo-new",
                "yahoo",
                now,
                2026,
                "overall",
                12,
                "player-lb",
                "Linebacker Leakage",
                "LB",
                42.0,
                "yahoo-lb",
                "exact",
            ),
            (
                "yahoo-wrong-scope",
                "yahoo",
                now + timedelta(days=1),
                2026,
                "overall",
                10,
                "player-a",
                "Alpha Runner",
                "RB",
                5.0,
                "yahoo-wrong",
                "exact",
            ),
            (
                "sleeper-overall",
                "sleeper",
                now,
                2026,
                "overall",
                12,
                "player-a",
                "Alpha Runner",
                "RB",
                20.0,
                "sleeper-a-overall",
                "reviewed",
            ),
            (
                "sleeper-newer-ppr",
                "sleeper",
                now + timedelta(days=1),
                2026,
                "ppr",
                12,
                "player-a",
                "Alpha Runner",
                "RB",
                4.0,
                "sleeper-a-ppr",
                "reviewed",
            ),
            (
                "rtsports-new",
                "rtsports",
                now,
                2026,
                "overall",
                12,
                "player-a",
                "Alpha Runner",
                "RB",
                22.0,
                "rtsports-a",
                "exact",
            ),
            (
                "fantasypros-new",
                "fantasypros",
                now,
                2026,
                "overall",
                12,
                "player-a",
                "Alpha Runner",
                "RB",
                19.7,
                "fantasypros-a",
                "exact",
            ),
            (
                "fantasypros-new",
                "fantasypros",
                now,
                2026,
                "overall",
                12,
                "player-b",
                "Beta Catcher",
                "WR",
                31.0,
                "fantasypros-b",
                "exact",
            ),
        )
        connection.executemany(
            "INSERT INTO adp_snapshots VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
            snapshots,
        )

    board = load_player_export_board(_config(warehouse), _projection_board())

    assert board.available is True
    assert board.projection_player_count == 2
    assert board.market_only_player_count == 1
    assert {row.player_id for row in board.rows} == {"player-a", "player-b", "player-c"}
    alpha = next(row for row in board.rows if row.player_id == "player-a")
    beta = next(row for row in board.rows if row.player_id == "player-b")
    gamma = next(row for row in board.rows if row.player_id == "player-c")
    assert (
        alpha.yahoo_adp,
        alpha.sleeper_adp,
        alpha.rtsports_adp,
        alpha.fantasypros_avg,
    ) == (18.0, 20.0, 22.0, 19.7)
    assert (beta.yahoo_adp, beta.fantasypros_avg) == (30.0, 31.0)
    assert alpha.position == "RB"
    assert beta.position == "WR"
    assert gamma.fantasypros_avg is None
    assert all(row.player_id != "player-low" for row in board.rows)
    assert {row.position for row in board.rows} <= {"QB", "RB", "TE", "WR"}
    coverage = {item.key: item for item in board.coverage}
    assert coverage["yahoo"].latest_capture == now
    assert coverage["yahoo"].source_rows == 5
    assert coverage["yahoo"].player_count == 2
    assert coverage["yahoo"].mapping_coverage == 2 / 5
    assert coverage["sleeper"].scope_label == "overall / 12-team / overall"
    assert coverage["rtsports"].available is True
    assert coverage["fantasypros"].available is True
    assert "Not loaded" not in board.message


def test_direct_player_export_uses_sleeper_ppr_only_as_missing_aggregate_fallback(
    tmp_path: Path,
) -> None:
    warehouse = tmp_path / "sleeper-fallback.duckdb"
    now = datetime(2026, 8, 24, 12, tzinfo=UTC)
    with duckdb.connect(str(warehouse)) as connection:
        _create_warehouse(connection)
        connection.execute("INSERT INTO players VALUES ('player-a', 'Alpha Runner', 'RB')")
        connection.execute(
            """
            INSERT INTO adp_snapshot_metadata VALUES
            ('sleeper-ppr', 'sleeper', ?, 2026, 'ppr', 12, 'overall', 1, ?)
            """,
            [now, now],
        )
        connection.execute(
            """
            INSERT INTO adp_snapshots VALUES
            ('sleeper-ppr', 'sleeper', ?, 2026, 'ppr', 12, 'player-a',
             'Alpha Runner', 'RB', 21.0, 'sleeper-a', 'exact')
            """,
            [now],
        )

    board = load_player_export_board(_config(warehouse), _projection_board())

    alpha = next(row for row in board.rows if row.player_id == "player-a")
    assert alpha.sleeper_adp == 21.0
    sleeper = next(item for item in board.coverage if item.key == "sleeper")
    assert sleeper.available is True
    assert sleeper.format_label == "Direct Sleeper full-PPR fallback (12-team)"
    assert sleeper.scope_label == "ppr / 12-team / overall"
    assert "fallback" in sleeper.availability_message


def test_direct_player_export_keeps_projection_rows_when_warehouse_is_missing(
    tmp_path: Path,
) -> None:
    warehouse = tmp_path / "missing.duckdb"

    board = load_player_export_board(_config(warehouse), _projection_board())

    assert board.available is True
    assert len(board.rows) == 2
    assert board.rows[0].fantasypros_avg is None
    assert all(not item.available for item in board.coverage)
    assert "ADP warehouse is not built" in board.message
