from fantasy_draft_ai.data.sources.ffc_adp import normalize_ffc_payload


def test_ffc_payload_normalization_preserves_source_id_without_claiming_identity() -> None:
    payload = {
        "players": [
            {
                "player_id": 5672,
                "name": "Demo Back",
                "position": "RB",
                "team": "DET",
                "adp": 1.6,
                "times_drafted": 765,
                "high": 1,
                "low": 4,
                "stdev": 0.7,
            }
        ]
    }
    frame = normalize_ffc_payload(payload, season=2026, scoring_format="ppr", teams=12)
    assert frame.loc[0, "raw_source_row_id"] == "5672"
    assert frame.loc[0, "player_id"] is None
    assert frame.loc[0, "mapping_confidence"] == "unresolved"
    assert frame.loc[0, "average_pick"] == 1.6
    assert frame.loc[0, "source_stddev"] == 0.7
    assert frame.loc[0, "source_movement_horizon"] is None
