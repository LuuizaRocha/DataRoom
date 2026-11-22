import pandas as pd

from core.cleaner import (clean_missing, convert_type, incompatible_columns, remove_duplicates,
                          standardize_text, text_columns, trim_whitespace)


def test_remove_duplicates():
    assert len(remove_duplicates(pd.DataFrame({"a": [1, 1, 2]}))) == 2


def test_trim_whitespace():
    result = trim_whitespace(pd.DataFrame({"name": [" Ana ", "Bob "]}), ["name"])
    assert result["name"].tolist() == ["Ana", "Bob"]


def test_trim_works_on_string_dtype():
    df = pd.DataFrame({"name": pd.array([" Ana "], dtype="string")})
    assert text_columns(df) == ["name"]
    assert trim_whitespace(df, ["name"])["name"].iloc[0] == "Ana"


def test_fill_missing_with_mean():
    result = clean_missing(pd.DataFrame({"value": [2.0, None, 4.0]}), ["value"], "Fill with mean")
    assert result["value"].iloc[1] == 3.0


def test_fill_mean_on_nullable_integer_does_not_crash():
    df = pd.DataFrame({"n": pd.array([1, None, 2], dtype="Int64")})
    assert clean_missing(df, ["n"], "Fill with mean")["n"].isna().sum() == 0


def test_numeric_strategy_skips_text_columns():
    df = pd.DataFrame({"t": ["a", None]})
    assert incompatible_columns(df, ["t"], "Fill with mean") == ["t"]
    assert clean_missing(df, ["t"], "Fill with mean")["t"].isna().sum() == 1


def test_constant_fill_ignores_incompatible_or_empty_value():
    df = pd.DataFrame({"n": [1.0, None]})
    assert clean_missing(df, ["n"], "Fill with constant", "Unknown")["n"].isna().sum() == 1
    assert clean_missing(df, ["n"], "Fill with constant", None)["n"].isna().sum() == 1
    assert clean_missing(df, ["n"], "Fill with constant", "7")["n"].iloc[1] == 7


def test_drop_rows():
    df = pd.DataFrame({"a": [1, None, 3]})
    assert len(clean_missing(df, ["a"], "Drop rows")) == 2


def test_title_case_handles_apostrophes():
    out = standardize_text(pd.DataFrame({"n": ["mcdonald's ana-maria"]}), ["n"], "Title Case")
    assert out["n"].iloc[0] == "Mcdonald's Ana-Maria"


def test_convert_numeric_marks_invalid_as_missing():
    result = convert_type(pd.DataFrame({"v": ["1", "2", "bad"]}), "v", "Numeric")
    assert result["v"].iloc[0] == 1 and result["v"].isna().sum() == 1


def test_convert_decimal_comma():
    result = convert_type(pd.DataFrame({"v": ["1.234,56", "0,5"]}), "v", "Numeric", decimal_comma=True)
    assert result["v"].tolist() == [1234.56, 0.5]


def test_convert_datetime_dayfirst():
    df = pd.DataFrame({"d": ["03/04/2025"]})
    assert convert_type(df, "d", "Datetime", dayfirst=True)["d"].iloc[0].month == 4
    assert convert_type(df, "d", "Datetime", dayfirst=False)["d"].iloc[0].month == 3


def test_convert_boolean_portuguese():
    out = convert_type(pd.DataFrame({"b": ["Sim", "não", "x"]}), "b", "Boolean")
    assert out["b"].tolist()[:2] == [True, False] and out["b"].isna().sum() == 1
