import pandas as pd

from core.explorer import apply_filters, search_dataframe, validate_filter

DF = pd.DataFrame({"name": ["Ana", "Bob", None], "n": [1, 5, 10], "d": pd.to_datetime(["2025-01-01", "2025-02-01", None])})


def test_search_is_case_insensitive_across_columns():
    assert len(search_dataframe(DF, "ANA")) == 1
    assert len(search_dataframe(DF, "")) == 3


def test_filters_are_combined():
    filters = [{"column": "n", "mode": "Greater than", "value": "1"},
               {"column": "name", "mode": "Is not missing", "value": None}]
    assert apply_filters(DF, filters)["name"].tolist() == ["Bob"]


def test_date_comparison():
    out = apply_filters(DF, [{"column": "d", "mode": "Greater than", "value": "2025-01-15"}])
    assert out["name"].tolist() == ["Bob"]


def test_validation_messages():
    assert validate_filter(DF, "n", "Greater than", "abc")
    assert validate_filter(DF, "n", "Contains", "")
    assert validate_filter(DF, "n", "Is missing", "") is None
    assert validate_filter(DF, "n", "Greater than", "1,5") is None
