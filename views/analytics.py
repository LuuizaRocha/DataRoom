import streamlit as st

from components import charts
from components.layout import page_header, require_dataset
from components.tables import dataframe_view
from core.analytics import (AGGREGATIONS, FREQUENCIES, categorical_columns, correlation_matrix, datetime_columns,
                            numeric_columns, numeric_summary, time_series, value_counts)

page_header("Find the signal", "Analytics", "Understand distributions, trends, relationships and descriptive statistics.")

df = require_dataset("Import a dataset to unlock analytics.")
if df is None:
    st.stop()

numeric, dates, categorical = numeric_columns(df), datetime_columns(df), categorical_columns(df)

if numeric:
    st.markdown("#### Numeric overview")
    dataframe_view(numeric_summary(df))
    selected = st.selectbox("Explore a numeric distribution", numeric)
    charts.histogram(df, selected)
    corr = correlation_matrix(df)
    if corr is not None:
        charts.heatmap(corr)
else:
    st.info("No numeric columns detected. Convert a column to Numeric in Data Cleaning to unlock numeric analytics.",
            icon=":material/info:")

if dates:
    st.markdown("#### Trend over time")
    a, b, c, d = st.columns(4)
    date_col = a.selectbox("Date column", dates)
    value_col = b.selectbox("Measure", numeric or list(df.columns))
    agg = c.selectbox("Aggregation", list(AGGREGATIONS))
    freq = d.selectbox("Period", list(FREQUENCIES), index=2)
    try:
        trend = time_series(df, date_col, value_col, agg, freq)
        if trend.empty:
            st.info("There are no dated rows to chart.")
        else:
            charts.line(trend, "Period", value_col, f"{agg} of {value_col} by {freq.lower()}")
    except Exception as exc:
        st.error(f"Could not build this chart: {exc}")
else:
    st.caption("Tip: convert a date column to Datetime in Data Cleaning to unlock trend analysis.")

if categorical:
    st.markdown("#### Category distribution")
    cat = st.selectbox("Choose a categorical column", categorical)
    charts.bar(value_counts(df, cat), f"Top values · {cat}")
