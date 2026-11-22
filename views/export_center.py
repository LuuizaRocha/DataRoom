import streamlit as st

from components.layout import page_header, require_dataset
from components.metrics import metric_row
from core.exporter import safe_filename, to_csv_bytes, to_excel_bytes

page_header("Deliver results", "Export Center", "Download your dataset as CSV or Excel.")

working = require_dataset("Import a dataset to export it.")
if working is None:
    st.stop()

original = st.session_state.original_df
log = st.session_state.change_log
metric_row([("Rows", f"{len(working):,}"), ("Columns", f"{len(working.columns):,}"), ("Cleaning steps applied", f"{len(log)}")])

st.markdown("#### Export options")
source = st.radio("Dataset", ["Working copy (with cleaning applied)", "Original import"], horizontal=True)
df = working if source.startswith("Working") else original
fmt = st.radio("Format", ["CSV (.csv)", "Excel (.xlsx)"], horizontal=True)

stem = safe_filename((st.session_state.dataset_name or "data").rsplit(".", 1)[0], "data")
suffix = "cleaned" if log and df is working else "export"
name = st.text_input("File name", value=f"{stem}_{suffix}", key=f"export_name_{stem}_{suffix}")
base = safe_filename(name)

if fmt.startswith("CSV"):
    st.download_button("Download CSV", lambda: to_csv_bytes(df), file_name=f"{base}.csv", mime="text/csv",
                       type="primary", on_click="ignore", icon=":material/download:")
    st.caption("UTF-8 with BOM, so accented characters open correctly in Excel.")
else:
    include_log = st.checkbox("Include a “Change Log” sheet listing the cleaning steps", value=True,
                              disabled=df is not working)
    st.download_button("Download Excel", lambda: to_excel_bytes(df, log if include_log and df is working else None),
                       file_name=f"{base}.xlsx",
                       mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                       type="primary", on_click="ignore", icon=":material/download:")
    st.caption("The header row is frozen and columns are sized automatically.")
st.caption("Your original import is never modified by exports or cleaning.")
