import streamlit as st

from components.layout import eyebrow, escape_md, page_header, require_dataset
from components.metrics import metric_row
from components.tables import dataframe_view
from core.profiler import profile_dataframe

page_header("Your data workspace", "Overview", "A clear view of your dataset's health, activity and structure.")

df = require_dataset("Import a CSV or Excel file, or load the sample dataset to explore the workspace.")
if df is None:
    st.stop()

p = profile_dataframe(df)
metric_row([
    ("Rows", f"{p['rows']:,}"),
    ("Columns", f"{p['columns']:,}"),
    ("Data quality", f"{p['score']:.1f}%", None, "80% completeness + 20% row uniqueness."),
    ("Duplicate rows", f"{p['duplicate_rows']:,}"),
])

left, right = st.columns([1.6, 1], gap="large")
with left:
    with st.container(border=True):
        eyebrow("Active dataset")
        st.markdown(f"### {escape_md(st.session_state.dataset_name or 'Untitled dataset')}")
        st.caption(f"{p['rows']:,} records · {p['columns']:,} fields · source: {st.session_state.source_type or '—'}")
    st.markdown("#### Data preview")
    dataframe_view(df.head(8))

with right:
    st.markdown("#### Quality indicators")
    st.progress(min(max(p["completeness"] / 100, 0.0), 1.0), text=f"Completeness · {p['completeness']:.1f}%")
    st.progress(min(max(p["uniqueness"] / 100, 0.0), 1.0), text=f"Uniqueness · {p['uniqueness']:.1f}%")
    st.metric("Missing values", f"{p['missing']:,}", border=True)
    st.markdown("#### Recent activity")
    activity = st.session_state.activity[:6]
    if activity:
        for item in activity:
            st.caption(f"{item['time']} · {escape_md(item['message'])}")
    else:
        st.caption("No activity yet.")

st.markdown("#### Column profile")
dataframe_view(
    p["column_profile"],
    column_config={
        "Missing %": st.column_config.ProgressColumn("Missing %", min_value=0, max_value=100, format="%.1f%%"),
        "Non-null": st.column_config.NumberColumn(format="%d"),
        "Missing": st.column_config.NumberColumn(format="%d"),
        "Unique": st.column_config.NumberColumn(format="%d"),
    },
)
