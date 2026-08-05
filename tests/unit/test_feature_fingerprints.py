from __future__ import annotations

from datetime import UTC, date, datetime, timedelta, timezone

from fantasy_draft_ai.features.player_seasons import FeatureRow, _feature_fingerprint


def test_feature_fingerprint_normalizes_same_instant_to_utc() -> None:
    utc_instant = datetime(2026, 8, 5, 16, 0, tzinfo=UTC)
    eastern_instant = utc_instant.astimezone(timezone(-timedelta(hours=4)))

    def row(source_max_as_of: datetime) -> FeatureRow:
        return FeatureRow(
            player_id="player-1",
            feature_season=2025,
            prediction_season=2026,
            cutoff_date=date(2026, 9, 1),
            position="WR",
            feature_payload='{"value":1}',
            source="nflverse",
            source_dataset_ids='["dataset-1"]',
            source_max_stat_season=2025,
            source_max_as_of=source_max_as_of,
        )

    assert _feature_fingerprint([row(utc_instant)], "rules") == _feature_fingerprint(
        [row(eastern_instant)], "rules"
    )
