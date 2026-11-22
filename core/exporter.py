"""Serialising DataFrames for download."""
from __future__ import annotations

import re
from io import BytesIO

import pandas as pd


def to_csv_bytes(df: pd.DataFrame) -> bytes:
    # utf-8-sig so Excel opens accented characters correctly.
    return df.to_csv(index=False).encode("utf-8-sig")


def _drop_timezones(df: pd.DataFrame) -> pd.DataFrame:
    out = df.copy()
    for col in out.columns:
        if isinstance(out[col].dtype, pd.DatetimeTZDtype):
            out[col] = out[col].dt.tz_localize(None)
    return out


def to_excel_bytes(df: pd.DataFrame, change_log: list[str] | None = None) -> bytes:
    buffer = BytesIO()
    with pd.ExcelWriter(buffer, engine="openpyxl") as writer:
        _drop_timezones(df).to_excel(writer, index=False, sheet_name="Cleaned Data")
        sheet = writer.sheets["Cleaned Data"]
        sheet.freeze_panes = "A2"
        for idx, col in enumerate(df.columns, start=1):
            sample = df[col].head(200).astype(str).str.len().max() if len(df) else 0
            width = min(max(len(str(col)), int(sample or 0)) + 2, 48)
            sheet.column_dimensions[sheet.cell(row=1, column=idx).column_letter].width = width
        if change_log is not None:
            log = pd.DataFrame({"Step": range(1, len(change_log) + 1), "Operation": change_log})
            if log.empty:
                log = pd.DataFrame({"Step": [], "Operation": []})
            log.to_excel(writer, index=False, sheet_name="Change Log")
            writer.sheets["Change Log"].column_dimensions["B"].width = 60
    return buffer.getvalue()


def safe_filename(name: str, default: str = "data_room_export") -> str:
    cleaned = re.sub(r"[^A-Za-z0-9._-]+", "_", name.strip()).strip("._")
    return cleaned or default
