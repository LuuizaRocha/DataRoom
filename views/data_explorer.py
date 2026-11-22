import pandas as pd
import streamlit as st

from components.layout import escape_md, page_header, require_dataset
from components.tables import dataframe_view
from config import MAX_EXPLORER_ROWS
from core.exporter import safe_filename, to_csv_bytes
from core.explorer import FILTER_MODES, NO_VALUE_MODES, apply_filters, describe_filter, search_dataframe, validate_filter
from core.profiler import column_summary

page_header("Inspect & understand", "Data Explorer", "Search records, combine filters and inspect individual columns.")

df = require_dataset("Import a dataset to start exploring.")
if df is None:
    st.stop()

filters = st.session_state.filters
query = st.text_input("Search across all columns", placeholder="Type a value to search for…", icon=":material/search:")

with st.expander(f"Filters ({len(filters)} active)" if filters else "Filters", expanded=bool(filters)):
    c1, c2, c3, c4 = st.columns([2, 2, 2, 1], vertical_alignment="bottom")
    column = c1.selectbox("Column", list(df.columns), key="flt_col")
    mode = c2.selectbox("Condition", FILTER_MODES, key="flt_mode")
    value = c3.text_input("Value", disabled=mode in NO_VALUE_MODES, key="flt_val")
    if c4.button("Add filter", width="stretch", icon=":material/add:"):
        error = validate_filter(df, column, mode, value)
        if error:
            st.error(error)
        else:
            filters.append({"column": column, "mode": mode, "value": None if mode in NO_VALUE_MODES else value})
            st.rerun()
    for i, f in enumerate(filters):
        a, b = st.columns([6, 1], vertical_alignment="center")
        a.markdown(f"**{i + 1}.** {escape_md(describe_filter(f))}")
        if b.button("Remove", key=f"rm_filter_{i}", width="stretch", icon=":material/close:"):
            filters.pop(i)
            st.rerun()
    if filters and st.button("Clear all filters", key="clear_filters"):
        filters.clear()
        st.rerun()

try:
    view = apply_filters(search_dataframe(df, query), filters)
except Exception as exc:  # defensive: never let a bad filter crash the page
    st.error(f"Could not apply the current filters: {exc}")
    view = df

shown = min(len(view), MAX_EXPLORER_ROWS)
left, right = st.columns([3, 1], vertical_alignment="center")
note = f" (first {MAX_EXPLORER_ROWS:,} displayed)" if len(view) > MAX_EXPLORER_ROWS else ""
left.caption(f"Showing {len(view):,} of {len(df):,} rows{note}")
right.download_button("Download this view (CSV)", lambda: to_csv_bytes(view), width="stretch",
                      file_name=f"{safe_filename((st.session_state.dataset_name or 'data').rsplit('.', 1)[0])}_view.csv",
                      mime="text/csv", on_click="ignore", icon=":material/download:")
if view.empty:
    st.info("No rows match the current search and filters.")
else:
    dataframe_view(view.head(shown), height=480)

st.markdown("#### Column details")
selected = st.selectbox("Select a column", list(df.columns), key="detail_col")
summary = column_summary(df[selected])
a, b, c = st.columns(3)
a.metric("Data type", summary["dtype"], border=True)
b.metric("Non-null values", f"{summary['count']:,}", border=True)
c.metric("Unique values", f"{summary['unique']:,}", border=True)
if "mean" in summary:
    a, b, c = st.columns(3)
    a.metric("Mean", f"{summary['mean']:,.3f}", border=True)
    b.metric("Median", f"{summary['median']:,.3f}", border=True)
    c.metric("Range", f"{summary['min']:,.3f} – {summary['max']:,.3f}", border=True)
elif "earliest" in summary:
    a, b, _ = st.columns(3)
    a.metric("Earliest", summary["earliest"], border=True)
    b.metric("Latest", summary["latest"], border=True)
elif summary.get("top_values"):
    st.markdown("**Top values**")
    dataframe_view(pd.DataFrame(summary["top_values"].items(), columns=["Value", "Count"]))
