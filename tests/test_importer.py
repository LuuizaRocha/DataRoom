from io import BytesIO

import pandas as pd
import pytest

from core.importer import list_excel_sheets, load_sample, read_uploaded_file, validate_dataframe


class Upload:
    def __init__(self, name, data):
        self.name, self.data = name, data

    def getvalue(self):
        return self.data


def test_read_csv():
    result = read_uploaded_file(Upload("data.csv", b"name,amount\nA,2\nB,3\n"))
    assert list(result.columns) == ["name", "amount"] and len(result) == 2


def test_semicolon_delimiter_and_decimal_comma():
    raw = "produto;preço\nCafé;1.234,50\nChá;3,20\n".encode("utf-8")
    result = read_uploaded_file(Upload("dados.csv", raw))
    assert list(result.columns) == ["produto", "preço"]
    assert result["preço"].tolist() == [1234.5, 3.2]


def test_latin1_encoding():
    raw = "nome;cidade\nJosé;São Paulo\n".encode("latin-1")
    assert read_uploaded_file(Upload("x.csv", raw))["cidade"].iloc[0] == "São Paulo"


def test_tab_delimiter():
    assert list(read_uploaded_file(Upload("x.tsv", b"a\tb\n1\t2\n")).columns) == ["a", "b"]


def test_ids_with_dots_are_not_turned_into_numbers():
    result = read_uploaded_file(Upload("x.csv", b"code,note\n1.234,a\n2.345,b\n"))
    assert result["code"].tolist() == [1.234, 2.345]


def test_excel_round_trip_and_sheets():
    buffer = BytesIO()
    with pd.ExcelWriter(buffer, engine="openpyxl") as writer:
        pd.DataFrame({"a": [1, 2]}).to_excel(writer, sheet_name="One", index=False)
        pd.DataFrame({"b": [3]}).to_excel(writer, sheet_name="Two", index=False)
    raw = buffer.getvalue()
    assert list_excel_sheets("w.xlsx", raw) == ["One", "Two"]
    assert list(read_uploaded_file(Upload("w.xlsx", raw), sheet="Two").columns) == ["b"]


def test_reject_unsupported_and_empty_files():
    with pytest.raises(ValueError):
        read_uploaded_file(Upload("data.json", b"{}"))
    with pytest.raises(ValueError):
        read_uploaded_file(Upload("data.csv", b""))


def test_corrupt_excel_gives_friendly_error():
    with pytest.raises(ValueError):
        read_uploaded_file(Upload("bad.xlsx", b"not an excel file"))


def test_validate_strips_and_dedupes_column_names():
    result = validate_dataframe(pd.DataFrame([[1, 2, 3]], columns=[" value ", "value", ""]))
    assert list(result.columns) == ["value", "value_2", "Column_3"]


def test_validate_drops_blank_rows_and_unnamed_columns():
    df = pd.DataFrame({"a": [1, None], "Unnamed: 1": [None, None]})
    result = validate_dataframe(df)
    assert list(result.columns) == ["a"] and len(result) == 1


def test_validate_rejects_empty_table():
    with pytest.raises(ValueError):
        validate_dataframe(pd.DataFrame({"a": []}))


def test_sample_dates_are_parsed():
    assert pd.api.types.is_datetime64_any_dtype(load_sample()["Order Date"])
