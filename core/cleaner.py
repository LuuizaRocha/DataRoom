"""Pure DataFrame transformations used by the Data Cleaning view."""
from __future__ import annotations

import re

import pandas as pd

MISSING_STRATEGIES = ["Drop rows", "Fill with mean", "Fill with median", "Fill with mode", "Fill with constant"]
NUMERIC_ONLY_STRATEGIES = {"Fill with mean", "Fill with median"}
TEXT_FORMATS = ["lowercase", "UPPERCASE", "Title Case"]
TARGET_TYPES = ["Text", "Numeric", "Integer", "Datetime", "Boolean"]

_WORD = re.compile(r"[^\W\d_]+(?:'[^\W\d_]+)*")
_BOOL_MAP = {"true": True, "false": False, "1": True, "0": False, "yes": True, "no": False,
             "sim": True, "não": False, "nao": False, "s": True, "n": False, "y": True}


def is_text_column(s: pd.Series) -> bool:
    return pd.api.types.is_object_dtype(s) or isinstance(s.dtype, pd.StringDtype)


def text_columns(df: pd.DataFrame) -> list[str]:
    return [c for c in df.columns if is_text_column(df[c])]


def incompatible_columns(df: pd.DataFrame, columns, strategy: str) -> list[str]:
    """Columns the chosen missing-value strategy cannot be applied to."""
    if strategy in NUMERIC_ONLY_STRATEGIES:
        return [c for c in columns if c in df.columns and not pd.api.types.is_numeric_dtype(df[c])]
    return []


def clean_missing(df: pd.DataFrame, columns, strategy: str, custom_value=None) -> pd.DataFrame:
    out = df.copy(deep=True)
    columns = [c for c in columns if c in out.columns]
    if strategy == "Drop rows":
        return out.dropna(subset=columns).reset_index(drop=True)
    for col in columns:
        s = out[col]
        if strategy in NUMERIC_ONLY_STRATEGIES:
            if not pd.api.types.is_numeric_dtype(s) or not s.notna().any():
                continue
            fill = s.mean() if strategy == "Fill with mean" else s.median()
            if pd.api.types.is_integer_dtype(s):
                fill = round(fill)
            out[col] = s.fillna(fill)
        elif strategy == "Fill with mode":
            modes = s.mode(dropna=True)
            if len(modes):
                out[col] = s.fillna(modes.iloc[0])
        elif strategy == "Fill with constant":
            if custom_value is None or custom_value == "":
                continue
            value = custom_value
            try:
                if pd.api.types.is_numeric_dtype(s):
                    value = pd.to_numeric(custom_value)
                elif pd.api.types.is_datetime64_any_dtype(s):
                    value = pd.to_datetime(custom_value)
            except (ValueError, TypeError):
                continue  # constant is not compatible with this column's type
            out[col] = s.fillna(value)
    return out


def remove_duplicates(df: pd.DataFrame, subset=None, keep="first") -> pd.DataFrame:
    return df.drop_duplicates(subset=subset or None, keep=keep).reset_index(drop=True)


def trim_whitespace(df: pd.DataFrame, columns) -> pd.DataFrame:
    out = df.copy(deep=True)
    for col in columns:
        if col in out.columns and is_text_column(out[col]):
            out[col] = out[col].map(lambda x: x.strip() if isinstance(x, str) else x)
    return out


def _title_case(text: str) -> str:
    return _WORD.sub(lambda m: m.group(0).capitalize(), text)


def standardize_text(df: pd.DataFrame, columns, case="lowercase") -> pd.DataFrame:
    converters = {"lowercase": str.lower, "UPPERCASE": str.upper, "Title Case": _title_case}
    convert = converters.get(case)
    out = df.copy(deep=True)
    if convert is None:
        return out
    for col in columns:
        if col in out.columns and is_text_column(out[col]):
            out[col] = out[col].map(lambda x: convert(x) if isinstance(x, str) else x)
    return out


def _decimal_comma_to_float(s: pd.Series) -> pd.Series:
    cleaned = s.astype("string").str.strip().str.replace(".", "", regex=False).str.replace(",", ".", regex=False)
    return pd.to_numeric(cleaned, errors="coerce")


def convert_type(df: pd.DataFrame, column: str, target: str, dayfirst: bool = False,
                 decimal_comma: bool = False) -> pd.DataFrame:
    out = df.copy(deep=True)
    if column not in out.columns:
        raise ValueError("Selected column does not exist.")
    s = out[column]
    if target in ("Numeric", "Integer"):
        numbers = _decimal_comma_to_float(s) if decimal_comma else pd.to_numeric(s, errors="coerce")
        out[column] = numbers if target == "Numeric" else numbers.round().astype("Int64")
    elif target == "Datetime":
        out[column] = pd.to_datetime(s, errors="coerce", dayfirst=dayfirst)
    elif target == "Text":
        out[column] = s.astype("string")
    elif target == "Boolean":
        out[column] = s.astype("string").str.strip().str.lower().map(_BOOL_MAP).astype("boolean")
    else:
        raise ValueError(f"Unknown target type: {target}")
    return out


def apply_operation(df: pd.DataFrame, operation: str, **kwargs) -> pd.DataFrame:
    operations = {
        "Remove duplicate rows": remove_duplicates,
        "Trim whitespace": trim_whitespace,
        "Standardize text": standardize_text,
        "Handle missing values": clean_missing,
        "Convert column type": convert_type,
    }
    if operation not in operations:
        raise ValueError("Unknown cleaning operation.")
    return operations[operation](df, **kwargs)
