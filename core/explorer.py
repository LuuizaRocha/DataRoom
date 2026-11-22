"""Search and column filters for the Data Explorer."""
from __future__ import annotations

import pandas as pd

FILTER_MODES = ["Contains", "Equals", "Greater than", "Less than", "Is missing", "Is not missing"]
NO_VALUE_MODES = {"Is missing", "Is not missing"}


def search_dataframe(df: pd.DataFrame, query: str) -> pd.DataFrame:
    query = (query or "").strip()
    if not query:
        return df
    mask = pd.Series(False, index=df.index)
    for col in df.columns:
        mask |= df[col].astype("string").str.contains(query, case=False, na=False, regex=False)
    return df[mask]


def _comparable(s: pd.Series, value):
    """Return (series, value) converted so that > and < make sense for the column type."""
    if pd.api.types.is_datetime64_any_dtype(s):
        return s, pd.to_datetime(value)
    return pd.to_numeric(s, errors="coerce"), float(str(value).replace(",", "."))


def validate_filter(df: pd.DataFrame, column: str, mode: str, value) -> str | None:
    """Return a user-facing error message, or None when the filter is valid."""
    if column not in df.columns:
        return "Select a column."
    if mode in NO_VALUE_MODES:
        return None
    if value is None or str(value).strip() == "":
        return "Enter a value for this condition."
    if mode in ("Greater than", "Less than"):
        try:
            _comparable(df[column], value)
        except (ValueError, TypeError):
            kind = "date" if pd.api.types.is_datetime64_any_dtype(df[column]) else "number"
            return f"“{value}” is not a valid {kind} for this column."
    return None


def filter_dataframe(df: pd.DataFrame, column: str, mode: str, value) -> pd.DataFrame:
    if column not in df.columns:
        return df
    s = df[column]
    if mode == "Contains":
        return df[s.astype("string").str.contains(str(value), case=False, na=False, regex=False)]
    if mode == "Equals":
        return df[s.astype("string").str.strip().str.lower() == str(value).strip().lower()]
    if mode == "Is missing":
        return df[s.isna()]
    if mode == "Is not missing":
        return df[s.notna()]
    if mode in ("Greater than", "Less than"):
        series, target = _comparable(s, value)
        return df[series > target] if mode == "Greater than" else df[series < target]
    return df


def apply_filters(df: pd.DataFrame, filters: list[dict]) -> pd.DataFrame:
    for f in filters:
        df = filter_dataframe(df, f["column"], f["mode"], f.get("value"))
    return df


def describe_filter(f: dict) -> str:
    if f["mode"] in NO_VALUE_MODES:
        return f"{f['column']} · {f['mode'].lower()}"
    return f"{f['column']} · {f['mode'].lower()} “{f['value']}”"
