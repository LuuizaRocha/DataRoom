import streamlit as st

import state
from components.layout import page_header
from components.metrics import metric_row
from components.tables import dataframe_view
from config import MAX_PREVIEW_ROWS
from core.importer import EXCEL_EXTENSIONS, SUPPORTED_EXTENSIONS, list_excel_sheets, read_file, validate_dataframe


@st.cache_data(show_spinner="Reading file…", max_entries=3)
def _parse(name: str, raw: bytes, sheet: str | None):
    return validate_dataframe(read_file(name, raw, sheet))


@st.cache_data(show_spinner=False, max_entries=3)
def _sheets(name: str, raw: bytes):
    return list_excel_sheets(name, raw)


page_header("Data ingestion", "Import Data", "Bring a dataset into your workspace. Your original file is never modified.")

uploaded = st.file_uploader(
    "Upload a CSV, TSV or Excel file",
    type=[ext.lstrip(".") for ext in SUPPORTED_EXTENSIONS],
    help="Delimiter and encoding are detected automatically. Files are processed in your active session.",
)

if uploaded is not None:
    raw, name = uploaded.getvalue(), uploaded.name
    sheet = None
    try:
        if name.lower().endswith(EXCEL_EXTENSIONS):
            sheets = _sheets(name, raw)
            if len(sheets) > 1:
                sheet = st.selectbox("Worksheet", sheets)
        df = _parse(name, raw, sheet)
    except ValueError as exc:
        st.error(str(exc))
    else:
        st.markdown("#### Import preview")
        metric_row([("Rows", f"{len(df):,}"), ("Columns", f"{len(df.columns):,}"),
                    ("File size", f"{len(raw) / 1024:,.1f} KB")])
        dataframe_view(df.head(min(12, MAX_PREVIEW_ROWS)))
        if st.session_state.working_df is not None:
            st.caption("Loading this file replaces the current dataset and clears its cleaning history.")
        if st.button("Use this dataset", type="primary", icon=":material/check:"):
            state.load_dataset(df, name, "Upload")
            st.switch_page("views/overview.py")

st.divider()
st.markdown("#### Prefer to explore first?")
st.write("Load the built-in retail transactions dataset: dates, categories, regions, quantities and revenue.")
if st.button("Load sample dataset", icon=":material/science:"):
    state.load_sample_dataset()
    st.switch_page("views/overview.py")

st.info("Privacy: uploaded data is processed in memory by this app. On Streamlit Community Cloud, files are "
        "sent to the hosted app while the session is active. Do not upload confidential or regulated data.",
        icon=":material/lock:")
