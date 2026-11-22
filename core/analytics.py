"""Descriptive statistics and aggregations for the Analytics view."""
from __future__ import annotations

import pandas as pd

FREQUENCIES = {"Day": "D", "Week": "W", "Month": "MS", "Quarter": "QS", "Year": "YS"}
AGGREGATIONS = {"Sum": "sum", "Average": "mean", "Median": "median", "Count": "count"}


def numeric_columns(df: pd.DataFrame) -> list[str]:
    return list(df.select_dtypes(include="number").columns)


def datetime_columns(df: pd.DataFrame) -> list[str]:
    return list(df.select_dtypes(include=["datetime", "datetimetz"]).columns)


def categorical_columns(df: pd.DataFrame) -> list[str]:
    return list(df.select_dtypes(exclude=["number", "datetime", "datetimetz"]).columns)


def numeric_summary(df: pd.DataFrame) -> pd.DataFrame:
    numeric = df.select_dtypes(include="number")
    if numeric.empty:
        return pd.DataFrame()
    return numeric.describe().T.reset_index(names="Column")


def categorical_summary(df: pd.DataFrame, top_n=10) -> dict:
    return {col: df[col].astype("string").value_counts(dropna=False).head(top_n)
            for col in categorical_columns(df)}


def value_counts(df: pd.DataFrame, column: str, top_n: int = 15) -> pd.Series:
    return df[column].astype("string").fillna("(Missing)").value_counts().head(top_n)


def correlation_matrix(df: pd.DataFrame):
    numeric = df.select_dtypes(include="number")
    if numeric.shape[1] < 2:
        return None
    return numeric.corr(numeric_only=True)


def time_series(df: pd.DataFrame, date_col: str, value_col: str,
                agg: str = "Sum", freq: str = "Month") -> pd.DataFrame:
    data = df[[date_col, value_col]].dropna(subset=[date_col])
    series = data.set_index(date_col)[value_col]
    out = series.resample(FREQUENCIES[freq]).agg(AGGREGATIONS[agg])
    return out.rename(value_col).reset_index().rename(columns={date_col: "Period"})
