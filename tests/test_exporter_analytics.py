from io import BytesIO

import pandas as pd

from core.analytics import categorical_columns, correlation_matrix, datetime_columns, time_series
from core.exporter import safe_filename, to_csv_bytes, to_excel_bytes
from core.importer import load_sample


def test_csv_has_bom_and_no_index():
    data = to_csv_bytes(pd.DataFrame({"a": ["é"]}))
    assert data.startswith(b"\xef\xbb\xbf") and b"a\n" in data


def test_excel_contains_data_and_change_log():
    raw = to_excel_bytes(pd.DataFrame({"a": [1, 2]}), ["Removed duplicate rows"])
    sheets = pd.read_excel(BytesIO(raw), sheet_name=None)
    assert set(sheets) == {"Cleaned Data", "Change Log"}
    assert sheets["Change Log"]["Operation"].iloc[0] == "Removed duplicate rows"


def test_excel_handles_timezone_aware_dates():
    df = pd.DataFrame({"t": pd.to_datetime(["2025-01-01"]).tz_localize("UTC")})
    assert to_excel_bytes(df)


def test_safe_filename():
    assert safe_filename("../my file?.csv") == "my_file_.csv"
    assert safe_filename("???") == "???".replace("?", "") or safe_filename("???") == "data_room_export"


def test_column_kinds_on_sample():
    df = load_sample()
    assert datetime_columns(df) == ["Order Date"]
    assert "Order Date" not in categorical_columns(df)
    assert correlation_matrix(df) is not None


def test_time_series_monthly_sum():
    out = time_series(load_sample(), "Order Date", "Revenue", "Sum", "Month")
    assert len(out) == 1 and round(out["Revenue"].iloc[0], 2) == round(load_sample()["Revenue"].sum(), 2)
