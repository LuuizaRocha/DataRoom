"""Reading CSV / Excel uploads into validated DataFrames."""
from __future__ import annotations

import csv
import re
from io import BytesIO
from pathlib import Path

import pandas as pd

from config import MAX_ROWS

CSV_EXTENSIONS = (".csv", ".tsv")
EXCEL_EXTENSIONS = (".xlsx", ".xls")
SUPPORTED_EXTENSIONS = CSV_EXTENSIONS + EXCEL_EXTENSIONS

_ENCODINGS = ("utf-8-sig", "cp1252", "latin-1")
_DELIMITERS = (",", ";", "\t", "|")
# 1234,56 · 1.234,56 · -0,5  (Brazilian / European decimal comma)
_DECIMAL_COMMA = re.compile(r"^\s*-?(\d+|\d{1,3}(\.\d{3})+)(,\d+)?\s*$")


def _detect_encoding(raw: bytes) -> str:
    for encoding in _ENCODINGS[:-1]:
        try:
            raw.decode(encoding)
            return encoding
        except UnicodeDecodeError:
            continue
    return _ENCODINGS[-1]


def _detect_delimiter(text: str) -> str:
    lines = [ln for ln in text[:65_536].splitlines()[:-1] or text.splitlines() if ln.strip()][:25]
    sample = "\n".join(lines)
    try:
        return csv.Sniffer().sniff(sample, delimiters="".join(_DELIMITERS)).delimiter
    except csv.Error:
        pass
    best, best_count = ",", 0
    for delimiter in _DELIMITERS:
        counts = {ln.count(delimiter) for ln in lines}
        if len(counts) == 1 and min(counts) > best_count:
            best, best_count = delimiter, min(counts)
    return best


def _coerce_decimal_comma(df: pd.DataFrame) -> pd.DataFrame:
    """Turn text columns such as '1.234,56' into numbers (only when every value fits)."""
    for col in df.columns:
        s = df[col]
        if not (pd.api.types.is_object_dtype(s) or isinstance(s.dtype, pd.StringDtype)):
            continue
        values = s.dropna().astype(str)
        if values.empty or not values.str.contains(",", regex=False).any():
            continue
        if values.map(lambda v: bool(_DECIMAL_COMMA.match(v))).all():
            cleaned = s.astype("string").str.strip().str.replace(".", "", regex=False).str.replace(",", ".", regex=False)
            df[col] = pd.to_numeric(cleaned, errors="coerce")
    return df


def _read_csv(raw: bytes) -> pd.DataFrame:
    encoding = _detect_encoding(raw)
    delimiter = _detect_delimiter(raw[:65_536].decode(encoding, errors="replace"))
    try:
        df = pd.read_csv(BytesIO(raw), encoding=encoding, sep=delimiter, low_memory=False)
    except pd.errors.EmptyDataError as exc:
        raise ValueError("The file has no data.") from exc
    except (pd.errors.ParserError, UnicodeDecodeError) as exc:
        raise ValueError(f"Could not parse this CSV. Check its delimiter and encoding. ({exc})") from exc
    return _coerce_decimal_comma(df)


def _excel_engine(name: str) -> str:
    return "openpyxl" if name.lower().endswith(".xlsx") else "xlrd"


def list_excel_sheets(name: str, raw: bytes) -> list[str]:
    try:
        with pd.ExcelFile(BytesIO(raw), engine=_excel_engine(name)) as workbook:
            return list(workbook.sheet_names)
    except Exception as exc:
        raise ValueError(f"Unable to read the workbook. It may be corrupted or password-protected. ({exc})") from exc


def read_file(name: str, raw: bytes, sheet: str | None = None) -> pd.DataFrame:
    """Read raw bytes of a CSV/TSV/Excel file. ``sheet`` selects the worksheet for Excel."""
    lowered = name.lower()
    if not raw:
        raise ValueError("The uploaded file is empty.")
    if lowered.endswith(CSV_EXTENSIONS):
        return _read_csv(raw)
    if lowered.endswith(EXCEL_EXTENSIONS):
        try:
            return pd.read_excel(BytesIO(raw), engine=_excel_engine(name), sheet_name=sheet or 0)
        except Exception as exc:
            raise ValueError(f"Unable to read the file: {exc}") from exc
    raise ValueError("Unsupported file type. Please upload a CSV or Excel file.")


def read_uploaded_file(uploaded_file, sheet: str | None = None) -> pd.DataFrame:
    """Convenience wrapper for Streamlit's UploadedFile (anything with ``name`` and ``getvalue``)."""
    return read_file(uploaded_file.name, uploaded_file.getvalue(), sheet)


def _unique_names(columns) -> list[str]:
    seen: dict[str, int] = {}
    names = []
    for i, col in enumerate(columns):
        base = str(col).strip() or f"Column_{i + 1}"
        seen[base] = seen.get(base, 0) + 1
        names.append(base if seen[base] == 1 else f"{base}_{seen[base]}")
    return names


def validate_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    if not isinstance(df, pd.DataFrame):
        raise ValueError("The uploaded content is not a valid table.")
    if len(df.columns) == 0:
        raise ValueError("No columns were found in this file.")
    out = df.copy()
    # Excel exports often carry empty "Unnamed: n" columns and blank rows.
    blank_unnamed = [c for c in out.columns if str(c).startswith("Unnamed:") and out[c].isna().all()]
    out = out.drop(columns=blank_unnamed).dropna(how="all").reset_index(drop=True)
    if out.shape[1] == 0 or out.empty:
        raise ValueError("This file has no data rows.")
    if len(out) > MAX_ROWS:
        raise ValueError(f"This version supports up to {MAX_ROWS:,} rows per dataset.")
    out.columns = _unique_names(out.columns)
    return out


def load_sample() -> pd.DataFrame:
    path = Path(__file__).resolve().parents[1] / "data" / "sample_dataset.csv"
    return pd.read_csv(path, parse_dates=["Order Date"])
