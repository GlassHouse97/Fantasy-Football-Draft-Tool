from __future__ import annotations

import json
from datetime import UTC, date, datetime
from pathlib import Path
from typing import Any

from fantasy_draft_ai.config import (
    AppConfig,
    NetworkSection,
    PathSection,
    ProjectSection,
    TrainingSection,
)
from fantasy_draft_ai.data.warehouse import Warehouse
from fantasy_draft_ai.features.player_seasons import build_player_season_features
from fantasy_draft_ai.rules.models import DraftSettings, LeagueRules
from fantasy_draft_ai.scoring.engine import ScoringRules, YardageBonus

AS_OF = datetime(2026, 8, 5, 12, 0, tzinfo=UTC)
IDENTITY_AS_OF = datetime(2020, 8, 1, 12, 0, tzinfo=UTC)
LATE_IDENTITY_AS_OF = datetime(2026, 8, 30, 12, 0, tzinfo=UTC)
PPR_RULES = LeagueRules(
    season=2024,
    teams=12,
    draft=DraftSettings(rounds=5),
    starters={"QB": 1, "RB": 1, "WR": 1, "TE": 1},
    bench=1,
    scoring=ScoringRules(reception=1),
)


def _config(project_root: Path) -> AppConfig:
    return AppConfig(
        project=ProjectSection(name="Phase 3 integration test", prediction_season=2024),
        paths=PathSection(
            data_dir=Path("data"),
            raw_dir=Path("data/raw"),
            processed_dir=Path("data/processed"),
            warehouse=Path("data/warehouse/test.duckdb"),
            manifests=Path("data/raw/manifests"),
        ),
        network=NetworkSection(timeout_seconds=5, user_agent="phase-3-test"),
        training=TrainingSection(start_season=2020, end_season=2023),
        project_root=project_root,
    )


def _initialize(config: AppConfig, *player_ids: str) -> Warehouse:
    warehouse = Warehouse(config.resolve(config.paths.warehouse))
    warehouse.initialize()
    with warehouse.connect() as connection:
        connection.executemany(
            "INSERT INTO players "
            "(player_id, gsis_id, display_name, canonical_position, birth_date, "
            "mapping_confidence, mapping_source, identity_source_dataset_id, "
            "identity_source_as_of) VALUES (?, ?, ?, 'WR', DATE '2000-01-01', "
            "'exact', 'phase-3-test', 'identity-test', ?)",
            [
                (player_id, player_id, f"Player {player_id}", IDENTITY_AS_OF)
                for player_id in player_ids
            ],
        )
    return warehouse


def _insert_week(
    warehouse: Warehouse,
    *,
    player_id: str,
    season: int,
    week: int,
    position: str = "WR",
    season_type: str = "REG",
    game_id: str | None = None,
    receiving_yards: float | None = 0,
    receptions: float | None = 0,
    receiving_tds: float | None = 0,
    source_dataset_id: str = "dataset-a",
) -> None:
    scoring_values = (
        receiving_yards,
        receptions,
        receiving_tds,
    )
    null_scoring_row = all(value is None for value in scoring_values)
    default_value: float | None = None if null_scoring_row else 0
    with warehouse.connect() as connection:
        connection.execute(
            """
            INSERT INTO player_week_stats (
                season, week, player_id, position, season_type, game_id, nfl_team, opponent,
                completions, passing_attempts, passing_yards, passing_tds, interceptions,
                rushing_yards, rushing_tds, receiving_yards, receptions, receiving_tds,
                targets, carries, two_point_conversions, fumbles_lost, special_teams_tds,
                source, as_of, source_dataset_id
            ) VALUES (
                ?, ?, ?, ?, ?, ?, 'BUF', 'MIA',
                ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?,
                'nflverse', ?, ?
            )
            """,
            [
                season,
                week,
                player_id,
                position,
                season_type,
                game_id or f"{season}_{week:02d}_BUF_MIA",
                default_value,
                default_value,
                default_value,
                default_value,
                default_value,
                default_value,
                default_value,
                receiving_yards,
                receptions,
                receiving_tds,
                default_value,
                default_value,
                default_value,
                default_value,
                default_value,
                AS_OF,
                source_dataset_id,
            ],
        )


def _insert_participation(
    warehouse: Warehouse,
    *,
    player_id: str,
    season: int,
    week: int,
    season_type: str = "REG",
    game_id: str | None = None,
    offense_snaps: float = 1,
    defense_snaps: float = 0,
    special_teams_snaps: float = 0,
    source_dataset_id: str = "snap-dataset-a",
) -> None:
    resolved_game_id = game_id or f"{season}_{week:02d}_BUF_MIA"
    with warehouse.connect() as connection:
        connection.execute(
            """
            INSERT INTO player_game_participation (
                season, week, game_id, player_id, pfr_game_id, pfr_player_id,
                game_type, season_type, position, nfl_team, opponent,
                offense_snaps, offense_snap_pct, defense_snaps, defense_snap_pct,
                special_teams_snaps, special_teams_snap_pct, source, as_of,
                source_dataset_id
            ) VALUES (
                ?, ?, ?, ?, ?, ?, ?, ?, 'WR', 'BUF', 'MIA',
                ?, NULL, ?, NULL, ?, NULL, 'nflverse_pfr_snap_counts', ?, ?
            )
            """,
            [
                season,
                week,
                resolved_game_id,
                player_id,
                f"pfr-{resolved_game_id}",
                f"pfr-{player_id}",
                season_type,
                season_type,
                offense_snaps,
                defense_snaps,
                special_teams_snaps,
                AS_OF,
                source_dataset_id,
            ],
        )


def _decode_json(value: Any) -> dict[str, Any] | None:
    if value is None:
        return None
    decoded = json.loads(value) if isinstance(value, str) else value
    assert isinstance(decoded, dict)
    return decoded


def _feature_row(
    warehouse: Warehouse, player_id: str, prediction_season: int
) -> tuple[int, date, dict[str, Any], dict[str, Any] | None, str, tuple[str, ...]]:
    with warehouse.connect(read_only=True) as connection:
        row = connection.execute(
            "SELECT feature_season, cutoff_date, feature_payload, source, "
            "source_dataset_ids "
            "FROM player_season_features WHERE player_id = ? AND prediction_season = ?",
            [player_id, prediction_season],
        ).fetchone()
        target_row = connection.execute(
            "SELECT target_payload FROM player_season_targets "
            "WHERE player_id = ? AND prediction_season = ?",
            [player_id, prediction_season],
        ).fetchone()
    assert row is not None
    feature_payload = _decode_json(row[2])
    assert feature_payload is not None
    source_ids = json.loads(row[4]) if isinstance(row[4], str) else row[4]
    assert isinstance(source_ids, list)
    target_payload = _decode_json(target_row[0]) if target_row is not None else None
    return (
        int(row[0]),
        row[1],
        feature_payload,
        target_payload,
        str(row[3]),
        tuple(str(value) for value in source_ids),
    )


def _table_snapshot(warehouse: Warehouse, maximum_prediction_season: int) -> list[tuple[Any, ...]]:
    with warehouse.connect(read_only=True) as connection:
        features = connection.execute(
            "SELECT player_id, feature_season, prediction_season, cutoff_date, position, "
            "feature_payload::VARCHAR, source_dataset_ids::VARCHAR, source, is_synthetic "
            "FROM player_season_features WHERE prediction_season <= ? "
            "ORDER BY player_id, prediction_season, source",
            [maximum_prediction_season],
        ).fetchall()
        targets = connection.execute(
            "SELECT player_id, prediction_season, position, target_payload::VARCHAR, "
            "source_dataset_ids::VARCHAR, source, is_synthetic "
            "FROM player_season_targets WHERE prediction_season <= ? "
            "ORDER BY player_id, prediction_season, source",
            [maximum_prediction_season],
        ).fetchall()
    return [
        *(tuple(["feature", *row]) for row in features),
        *(tuple(["target", *row]) for row in targets),
    ]


def _find_key(payload: Any, names: set[str]) -> tuple[bool, Any]:
    if isinstance(payload, dict):
        for key, value in payload.items():
            if key in names:
                return True, value
        for value in payload.values():
            found, match = _find_key(value, names)
            if found:
                return True, match
    elif isinstance(payload, list):
        for value in payload:
            found, match = _find_key(value, names)
            if found:
                return True, match
    return False, None


def _metric(payload: dict[str, Any], *names: str) -> float:
    found, value = _find_key(payload, set(names))
    assert found, f"Expected one of {names!r} in payload: {payload!r}"
    assert isinstance(value, int | float) and not isinstance(value, bool)
    return float(value)


def _all_keys(payload: Any) -> set[str]:
    keys: set[str] = set()
    if isinstance(payload, dict):
        for key, value in payload.items():
            keys.add(key)
            keys.update(_all_keys(value))
    elif isinstance(payload, list):
        for value in payload:
            keys.update(_all_keys(value))
    return keys


def _all_strings(payload: Any) -> set[str]:
    values: set[str] = set()
    if isinstance(payload, str):
        values.add(payload)
    elif isinstance(payload, dict):
        for value in payload.values():
            values.update(_all_strings(value))
    elif isinstance(payload, list):
        for value in payload:
            values.update(_all_strings(value))
    return values


def test_build_uses_regular_season_stat_rows_and_keeps_targets_separate(
    tmp_path: Path,
) -> None:
    config = _config(tmp_path)
    warehouse = _initialize(config, "p1")
    _insert_week(
        warehouse,
        player_id="p1",
        season=2022,
        week=1,
        receiving_yards=100,
        receptions=5,
        receiving_tds=1,
        source_dataset_id="dataset-b",
    )
    _insert_participation(
        warehouse,
        player_id="p1",
        season=2022,
        week=1,
        offense_snaps=42,
        source_dataset_id="snap-dataset-b",
    )
    _insert_week(
        warehouse,
        player_id="p1",
        season=2022,
        week=2,
        receiving_yards=50,
        receptions=2,
        source_dataset_id="dataset-a",
    )
    _insert_participation(
        warehouse,
        player_id="p1",
        season=2022,
        week=2,
        offense_snaps=37,
        source_dataset_id="snap-dataset-a",
    )
    _insert_week(
        warehouse,
        player_id="p1",
        season=2022,
        week=19,
        season_type="POST",
        receiving_yards=10_000,
        receptions=1_000,
        receiving_tds=100,
        source_dataset_id="postseason-dataset",
    )
    _insert_participation(
        warehouse,
        player_id="p1",
        season=2022,
        week=19,
        season_type="POST",
        offense_snaps=50,
        source_dataset_id="postseason-snap-dataset",
    )
    _insert_week(
        warehouse,
        player_id="p1",
        season=2023,
        week=1,
        receiving_yards=200,
        receptions=5,
        source_dataset_id="target-dataset",
    )
    _insert_participation(
        warehouse,
        player_id="p1",
        season=2023,
        week=1,
        offense_snaps=45,
        source_dataset_id="target-snap-dataset",
    )

    result = build_player_season_features(config, PPR_RULES, prediction_season=2024)

    assert result.committed
    assert not result.quality.has_fatal_errors
    assert result.feature_rows == 2
    assert result.target_rows == 1
    assert result.quality.input_weekly_rows == 4
    assert result.quality.regular_weekly_rows == 3
    assert result.quality.postseason_weekly_rows == 1
    assert result.quality.input_participation_rows == 4
    assert result.quality.regular_participation_rows == 3
    assert result.quality.postseason_participation_rows == 1
    assert result.quality.live_rows_without_targets == 1
    assert result.data_fingerprint
    assert "PASSED" in result.render()

    feature_season, cutoff, features, target, _, source_ids = _feature_row(warehouse, "p1", 2023)
    assert feature_season == 2022
    assert feature_season < cutoff.year <= 2023
    assert _metric(features, "lag1_games_active") == 2
    assert _metric(features, "lag1_stat_games") == 2
    assert _metric(features, "lag1_fantasy_points_total") == 28
    assert _metric(features, "lag1_fantasy_points_per_game") == 14

    assert target is not None
    assert _metric(target, "fantasy_points_total") == 25
    assert _metric(target, "games_active") == 1
    assert _metric(target, "fantasy_points_per_game") == 25
    assert not any(key.startswith("target") or "next_season" in key for key in _all_keys(features))
    with warehouse.connect(read_only=True) as connection:
        legacy_target_payload = connection.execute(
            "SELECT target_payload FROM player_season_features "
            "WHERE player_id = 'p1' AND prediction_season = 2023"
        ).fetchone()
    assert legacy_target_payload == (None,)

    # Row-level lineage must identify every regular-season feature input, not an arbitrary
    # MIN/MAX manifest. The postseason and target manifests are not feature provenance.
    assert {"dataset-a", "dataset-b", "snap-dataset-a", "snap-dataset-b"} <= set(source_ids)
    assert "postseason-dataset" not in source_ids
    assert "postseason-snap-dataset" not in source_ids
    assert "target-dataset" not in source_ids
    assert "target-snap-dataset" not in source_ids


def test_missing_rookie_history_is_distinct_from_observed_zero(tmp_path: Path) -> None:
    config = _config(tmp_path).model_copy(
        update={"training": TrainingSection(start_season=2020, end_season=2022)}
    )
    warehouse = _initialize(config, "missing", "zero")
    with warehouse.connect() as connection:
        connection.execute("UPDATE players SET rookie_season = 2023 WHERE player_id = 'missing'")
    _insert_week(
        warehouse,
        player_id="zero",
        season=2022,
        week=1,
        receiving_yards=0,
        receptions=0,
        receiving_tds=0,
    )
    _insert_participation(
        warehouse,
        player_id="zero",
        season=2022,
        week=1,
        offense_snaps=20,
    )

    result = build_player_season_features(config, PPR_RULES, prediction_season=2023)

    assert result.committed
    _, _, missing_features, _, _, _ = _feature_row(warehouse, "missing", 2023)
    _, _, zero_features, _, _, _ = _feature_row(warehouse, "zero", 2023)
    found_missing, missing_points = _find_key(missing_features, {"lag1_fantasy_points_total"})
    assert found_missing
    assert missing_points is None
    assert _metric(zero_features, "lag1_fantasy_points_total") == 0
    assert missing_features["is_rookie"] is True
    assert missing_features["missing_history"] is True
    assert missing_features["missing_lag1"] is True
    assert zero_features["missing_lag1"] is False
    assert missing_features != zero_features


def test_component_baseline_averages_weekly_yardage_bonus_points(
    tmp_path: Path,
) -> None:
    config = _config(tmp_path).model_copy(
        update={"training": TrainingSection(start_season=2020, end_season=2022)}
    )
    warehouse = _initialize(config, "threshold")
    for week, receiving_yards in [(1, 99.0), (2, 101.0)]:
        _insert_week(
            warehouse,
            player_id="threshold",
            season=2022,
            week=week,
            receiving_yards=receiving_yards,
        )
        _insert_participation(
            warehouse,
            player_id="threshold",
            season=2022,
            week=week,
            offense_snaps=40,
        )

    no_bonus_rules = PPR_RULES.model_copy(update={"scoring": ScoringRules(reception=0)})
    no_bonus_result = build_player_season_features(config, no_bonus_rules, prediction_season=2023)
    _, _, no_bonus_features, _, _, _ = _feature_row(warehouse, "threshold", 2023)

    bonus_rules = PPR_RULES.model_copy(
        update={
            "scoring": ScoringRules(
                reception=0,
                yardage_bonuses=(
                    YardageBonus(category="receiving_yards", threshold=100, points=3),
                ),
            )
        }
    )
    bonus_result = build_player_season_features(config, bonus_rules, prediction_season=2023)
    _, _, bonus_features, _, _, _ = _feature_row(warehouse, "threshold", 2023)

    assert no_bonus_result.committed and bonus_result.committed
    assert _metric(no_bonus_features, "baseline_components_fantasy_points_per_game") == 10
    assert _metric(bonus_features, "weighted_3yr_yardage_bonus_points_per_game") == 1.5
    assert _metric(bonus_features, "baseline_components_fantasy_points_per_game") == 11.5
    assert _metric(bonus_features, "lag1_fantasy_points_total") == 23
    assert _metric(bonus_features, "lag1_fantasy_points_per_game") == 11.5


def test_build_is_idempotent_and_isolated_from_future_postseason_and_targets(
    tmp_path: Path,
) -> None:
    config = _config(tmp_path)
    warehouse = _initialize(config, "p1")
    _insert_week(
        warehouse,
        player_id="p1",
        season=2022,
        week=1,
        receiving_yards=100,
        source_dataset_id="feature-dataset",
    )
    _insert_participation(
        warehouse,
        player_id="p1",
        season=2022,
        week=1,
        offense_snaps=40,
        source_dataset_id="feature-snap-dataset",
    )
    _insert_week(
        warehouse,
        player_id="p1",
        season=2023,
        week=1,
        receiving_yards=200,
        source_dataset_id="target-dataset",
    )
    _insert_participation(
        warehouse,
        player_id="p1",
        season=2023,
        week=1,
        offense_snaps=40,
        source_dataset_id="target-snap-dataset",
    )
    _insert_week(
        warehouse,
        player_id="p1",
        season=2023,
        week=19,
        season_type="POST",
        receiving_yards=30_000,
        source_dataset_id="postseason-dataset",
    )
    _insert_participation(
        warehouse,
        player_id="p1",
        season=2023,
        week=19,
        season_type="POST",
        offense_snaps=40,
        source_dataset_id="postseason-snap-dataset",
    )

    first = build_player_season_features(config, PPR_RULES, prediction_season=2024)
    first_snapshot = _table_snapshot(warehouse, 2024)
    first_row = _feature_row(warehouse, "p1", 2023)
    assert first.report_path is not None
    first_report = first.report_path.read_bytes()
    second = build_player_season_features(config, PPR_RULES, prediction_season=2024)

    assert first.committed and second.committed
    assert first_snapshot == _table_snapshot(warehouse, 2024)
    assert first.data_fingerprint == second.data_fingerprint
    assert second.report_path is not None
    assert second.report_path.read_bytes() == first_report

    with warehouse.connect() as connection:
        connection.execute(
            "UPDATE player_week_stats SET receiving_yards = 999999 "
            "WHERE player_id = 'p1' AND season_type = 'POST'"
        )
    _insert_week(
        warehouse,
        player_id="p1",
        season=2025,
        week=1,
        receiving_yards=999_999,
        source_dataset_id="future-dataset",
    )
    _insert_participation(
        warehouse,
        player_id="p1",
        season=2025,
        week=1,
        offense_snaps=40,
        source_dataset_id="future-snap-dataset",
    )
    after_irrelevant_mutation = build_player_season_features(
        config, PPR_RULES, prediction_season=2024
    )

    assert first_snapshot == _table_snapshot(warehouse, 2024)
    assert first.data_fingerprint == after_irrelevant_mutation.data_fingerprint

    with warehouse.connect() as connection:
        connection.execute(
            "UPDATE player_week_stats SET receiving_yards = 300 "
            "WHERE player_id = 'p1' AND season = 2023 AND season_type = 'REG'"
        )
    after_target_mutation = build_player_season_features(config, PPR_RULES, prediction_season=2024)
    changed_row = _feature_row(warehouse, "p1", 2023)

    assert after_target_mutation.committed
    assert changed_row[2] == first_row[2]
    assert changed_row[3] != first_row[3]


def test_target_only_change_preserves_feature_fingerprint_and_changes_build(
    tmp_path: Path,
) -> None:
    config = _config(tmp_path)
    warehouse = _initialize(config, "p1")
    _insert_week(
        warehouse,
        player_id="p1",
        season=2022,
        week=1,
        receiving_yards=100,
    )
    _insert_participation(warehouse, player_id="p1", season=2022, week=1, offense_snaps=40)
    _insert_week(
        warehouse,
        player_id="p1",
        season=2023,
        week=1,
        receiving_yards=200,
    )
    _insert_participation(warehouse, player_id="p1", season=2023, week=1, offense_snaps=40)

    first = build_player_season_features(config, PPR_RULES, prediction_season=2023)
    with warehouse.connect() as connection:
        connection.execute(
            "UPDATE player_week_stats SET receiving_yards = 300 "
            "WHERE player_id = 'p1' AND season = 2023 AND season_type = 'REG'"
        )
    second = build_player_season_features(config, PPR_RULES, prediction_season=2023)

    assert first.committed and second.committed
    assert first.data_fingerprint == second.data_fingerprint
    assert first.target_fingerprint != second.target_fingerprint
    assert first.build_fingerprint != second.build_fingerprint
    with warehouse.connect(read_only=True) as connection:
        fingerprints = connection.execute(
            """
            SELECT
                feature.data_fingerprint,
                target.target_data_fingerprint,
                metadata.build_fingerprint
            FROM player_season_features AS feature
            JOIN player_season_targets AS target USING (player_id, prediction_season)
            JOIN feature_build_metadata AS metadata
              ON feature.data_fingerprint = metadata.data_fingerprint
            WHERE feature.player_id = 'p1' AND feature.prediction_season = 2023
            """
        ).fetchone()
    assert fingerprints == (
        second.data_fingerprint,
        second.target_fingerprint,
        second.build_fingerprint,
    )


def test_partial_positive_stat_game_coverage_nulls_player_season_denominator(
    tmp_path: Path,
) -> None:
    config = _config(tmp_path).model_copy(
        update={"training": TrainingSection(start_season=2020, end_season=2022)}
    )
    warehouse = _initialize(config, "partial", "anchor")
    _insert_week(
        warehouse,
        player_id="anchor",
        season=2022,
        week=1,
        receiving_yards=80,
    )
    _insert_participation(warehouse, player_id="anchor", season=2022, week=1, offense_snaps=40)
    for week, yards in ((1, 100.0), (2, 50.0)):
        _insert_week(
            warehouse,
            player_id="partial",
            season=2022,
            week=week,
            receiving_yards=yards,
        )
    _insert_participation(warehouse, player_id="partial", season=2022, week=1, offense_snaps=40)

    result = build_player_season_features(config, PPR_RULES, prediction_season=2023)

    assert result.committed
    assert result.quality.participation_coverage_failures == 1
    assert any(
        issue.code == "missing_participation_for_scoring_rows" for issue in result.quality.issues
    )
    _, _, features, _, _, _ = _feature_row(warehouse, "partial", 2023)
    assert features["lag1_games_active"] is None
    assert features["lag1_fantasy_points_per_game"] is None
    assert features["missing_lag1_participation"] is True


def test_absent_target_record_distinguishes_mapped_zero_from_unresolved_identity(
    tmp_path: Path,
) -> None:
    config = _config(tmp_path)
    warehouse = _initialize(config, "mapped", "unmapped", "anchor")
    with warehouse.connect() as connection:
        connection.execute("UPDATE players SET pfr_id = 'Mapped00' WHERE player_id = 'mapped'")
    for player_id in ("mapped", "unmapped", "anchor"):
        _insert_week(
            warehouse,
            player_id=player_id,
            season=2022,
            week=1,
            receiving_yards=50,
        )
        _insert_participation(
            warehouse,
            player_id=player_id,
            season=2022,
            week=1,
            offense_snaps=40,
        )
    _insert_week(
        warehouse,
        player_id="anchor",
        season=2023,
        week=1,
        receiving_yards=60,
    )
    _insert_participation(warehouse, player_id="anchor", season=2023, week=1, offense_snaps=40)

    result = build_player_season_features(config, PPR_RULES, prediction_season=2023)

    assert result.committed
    assert result.quality.target_rows_missing_games_active == 1
    assert any(issue.code == "target_games_active_unavailable" for issue in result.quality.issues)
    _, _, _, mapped_target, _, _ = _feature_row(warehouse, "mapped", 2023)
    _, _, _, unmapped_target, _, _ = _feature_row(warehouse, "unmapped", 2023)
    assert mapped_target is not None and unmapped_target is not None
    assert mapped_target["games_active"] == 0
    assert mapped_target["fantasy_points_total"] == 0
    assert unmapped_target["games_active"] is None
    assert unmapped_target["fantasy_points_per_game"] is None
    assert unmapped_target["fantasy_points_total"] == 0


def test_candidate_policy_includes_returners_and_second_year_players_with_lineage(
    tmp_path: Path,
) -> None:
    config = _config(tmp_path).model_copy(
        update={"training": TrainingSection(start_season=2020, end_season=2022)}
    )
    warehouse = _initialize(config, "anchor", "returner", "redshirt")
    with warehouse.connect() as connection:
        connection.execute("UPDATE players SET rookie_season = 2022 WHERE player_id = 'redshirt'")
        connection.execute(
            "UPDATE players SET canonical_position = 'TE' WHERE player_id = 'returner'"
        )
    _insert_week(
        warehouse,
        player_id="anchor",
        season=2022,
        week=1,
        receiving_yards=80,
    )
    _insert_participation(warehouse, player_id="anchor", season=2022, week=1, offense_snaps=40)
    _insert_week(
        warehouse,
        player_id="returner",
        season=2019,
        week=1,
        position="WR",
        receiving_yards=70,
        source_dataset_id="returner-weekly-2019",
    )
    _insert_participation(
        warehouse,
        player_id="returner",
        season=2019,
        week=1,
        offense_snaps=40,
        source_dataset_id="returner-snaps-2019",
    )
    with warehouse.connect() as connection:
        connection.execute(
            "UPDATE player_game_participation SET position = 'CB/RB' "
            "WHERE player_id = 'returner' AND season = 2019"
        )

    result = build_player_season_features(config, PPR_RULES, prediction_season=2023)

    assert result.committed
    _, _, returner, _, _, returner_sources = _feature_row(warehouse, "returner", 2023)
    _, _, redshirt, _, _, _ = _feature_row(warehouse, "redshirt", 2023)
    assert returner["candidate_selection_reason"] == "prior_four_season_record"
    assert returner["candidate_evidence_seasons"] == [2019]
    assert returner["missing_history"] is True
    assert {"returner-weekly-2019", "returner-snaps-2019"} <= set(returner_sources)
    assert redshirt["candidate_selection_reason"] == "second_year_entry_cohort"
    with warehouse.connect(read_only=True) as connection:
        positions = connection.execute(
            "SELECT player_id, position, source_max_stat_season "
            "FROM player_season_features "
            "WHERE prediction_season = 2023 AND player_id IN ('returner', 'redshirt') "
            "ORDER BY player_id"
        ).fetchall()
    assert positions == [("redshirt", "WR", 2022), ("returner", "WR", 2022)]


def test_historical_entry_cohort_never_uses_later_position_conversion(
    tmp_path: Path,
) -> None:
    config = _config(tmp_path).model_copy(
        update={"training": TrainingSection(start_season=2020, end_season=2022)}
    )
    warehouse = _initialize(config, "anchor", "converted")
    with warehouse.connect() as connection:
        connection.execute(
            "UPDATE players SET rookie_season = 2023, canonical_position = 'TE', "
            "identity_source_as_of = TIMESTAMPTZ '2026-08-01 12:00:00+00' "
            "WHERE player_id = 'converted'"
        )
    _insert_week(
        warehouse,
        player_id="anchor",
        season=2022,
        week=1,
        receiving_yards=80,
    )
    _insert_participation(warehouse, player_id="anchor", season=2022, week=1, offense_snaps=40)

    historical = build_player_season_features(config, PPR_RULES, prediction_season=2023)

    assert historical.committed
    assert historical.quality.candidates_missing_cutoff_safe_position == 1
    assert any(
        issue.code == "candidate_position_unavailable_at_cutoff"
        for issue in historical.quality.issues
    )
    with warehouse.connect(read_only=True) as connection:
        historical_row = connection.execute(
            "SELECT position FROM player_season_features "
            "WHERE player_id = 'converted' AND prediction_season = 2023"
        ).fetchone()
    assert historical_row is None

    with warehouse.connect() as connection:
        connection.execute(
            "UPDATE players SET rookie_season = 2026, identity_source_as_of = "
            "TIMESTAMPTZ '2026-08-01 12:00:00+00' WHERE player_id = 'converted'"
        )
    _insert_week(
        warehouse,
        player_id="anchor",
        season=2025,
        week=1,
        position="TE",
        receiving_yards=90,
    )
    _insert_participation(warehouse, player_id="anchor", season=2025, week=1, offense_snaps=40)
    live = build_player_season_features(config, PPR_RULES, prediction_season=2026)

    assert live.committed
    assert live.quality.cutoff_safe_static_position_rows >= 1
    with warehouse.connect(read_only=True) as connection:
        live_row = connection.execute(
            "SELECT position FROM player_season_features "
            "WHERE player_id = 'converted' AND prediction_season = 2026"
        ).fetchone()
    assert live_row == ("TE",)


def test_identity_snapshot_timestamp_is_included_in_feature_provenance(
    tmp_path: Path,
) -> None:
    config = _config(tmp_path)
    warehouse = _initialize(config, "p1")
    with warehouse.connect() as connection:
        connection.execute(
            "UPDATE players SET identity_source_dataset_id = 'identity-late', "
            "identity_source_as_of = ? WHERE player_id = 'p1'",
            [LATE_IDENTITY_AS_OF],
        )
    _insert_week(
        warehouse,
        player_id="p1",
        season=2025,
        week=1,
        receiving_yards=80,
        source_dataset_id="weekly-early",
    )
    _insert_participation(
        warehouse,
        player_id="p1",
        season=2025,
        week=1,
        offense_snaps=40,
        source_dataset_id="snaps-early",
    )

    result = build_player_season_features(config, PPR_RULES, prediction_season=2026)

    assert result.committed
    with warehouse.connect(read_only=True) as connection:
        row = connection.execute(
            "SELECT source_dataset_ids, source_max_as_of "
            "FROM player_season_features "
            "WHERE player_id = 'p1' AND prediction_season = 2026"
        ).fetchone()
    assert row is not None
    source_ids = json.loads(row[0]) if isinstance(row[0], str) else row[0]
    assert "identity-late" in source_ids
    assert row[1] == LATE_IDENTITY_AS_OF
