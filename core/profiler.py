"""Dataset and column profiling."""
from __future__ import annotations

import pandas as pd


def _safe_nunique(s: pd.Series) -> int:
    try:
        return int(s.nunique(dropna=True))
    except TypeError:  # unhashable values such as lists
        return int(s.astype(str).nunique())


def profile_dataframe(df: pd.DataFrame) -> dict:
    rows, cols = df.shape
    missing = int(df.isna().sum().sum())
    cells = max(rows * cols, 1)
    duplicate_rows = int(df.duplicated().sum()) if rows else 0
    completeness = 100 * (1 - missing / cells)
    uniqueness = 100 * (1 - duplicate_rows / max(rows, 1))
    score = max(0.0, min(100.0, 0.8 * completeness + 0.2 * uniqueness))
    column_rows = []
    for col in df.columns:
        s = df[col]
        non_null = s.dropna()
        column_rows.append({
            "Column": str(col),
            "Data type": str(s.dtype),
            "Non-null": int(s.notna().sum()),
            "Missing": int(s.isna().sum()),
            "Missing %": round(100 * s.isna().mean(), 2) if rows else 0.0,
            "Unique": _safe_nunique(s),
            "Sample": str(non_null.iloc[0])[:60] if len(non_null) else "—",
        })
    return {
        "rows": rows, "columns": cols, "missing": missing,
        "duplicate_rows": duplicate_rows, "completeness": round(completeness, 2),
        "uniqueness": round(uniqueness, 2),
        "score": round(score, 1), "column_profile": pd.DataFrame(column_rows),
    }


def column_summary(series: pd.Series) -> dict:
    s = series.dropna()
    result = {"dtype": str(series.dtype), "count": int(series.count()),
              "missing": int(series.isna().sum()), "unique": _safe_nunique(series)}
    if pd.api.types.is_bool_dtype(series):
        result["top_values"] = s.astype(str).value_counts().head(5).to_dict()
    elif pd.api.types.is_numeric_dtype(series):
        if len(s):
            result.update({"mean": float(s.mean()), "median": float(s.median()),
                           "min": float(s.min()), "max": float(s.max()),
                           "std": float(s.std()) if len(s) > 1 else 0.0})
    elif pd.api.types.is_datetime64_any_dtype(series):
        if len(s):
            result.update({"earliest": str(s.min())[:19], "latest": str(s.max())[:19]})
    else:
        result["top_values"] = s.astype(str).value_counts().head(5).to_dict()
    return result
