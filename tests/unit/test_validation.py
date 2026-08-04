import pandas as pd

from fantasy_draft_ai.data.validation import validate_tabular_import


def test_missing_headers_are_fatal() -> None:
    report = validate_tabular_import(
        pd.DataFrame({"name": ["Demo"]}),
        source="demo",
        required_columns=["name", "rank"],
        required_values=["name", "rank"],
        duplicate_key=["rank"],
    )
    assert report.has_fatal_errors
    assert report.required_field_failures == 1


def test_duplicates_and_blank_required_values_are_reported() -> None:
    frame = pd.DataFrame({"name": ["Demo", ""], "rank": [1, 1]})
    report = validate_tabular_import(
        frame,
        source="demo",
        required_columns=["name", "rank"],
        required_values=["name", "rank"],
        duplicate_key=["rank"],
    )
    assert report.required_field_failures == 1
    assert report.duplicate_keys == 2
    assert "FAILED" in report.render()
