import streamlit as st

import state
from components.layout import escape_md, page_header, require_dataset
from components.tables import dataframe_view
from config import MAX_HISTORY
from core.cleaner import (MISSING_STRATEGIES, TARGET_TYPES, TEXT_FORMATS, clean_missing, convert_type,
                          incompatible_columns, remove_duplicates, standardize_text, text_columns, trim_whitespace)
from core.profiler import profile_dataframe

page_header("Improve data quality", "Data Cleaning",
            "Preview every transformation before applying it. Your original import is always preserved.")

df = require_dataset("Import a dataset to start cleaning.")
if df is None:
    st.stop()

p = profile_dataframe(df)
c1, c2, c3 = st.columns(3)
c1.metric("Missing values", f"{p['missing']:,}", border=True)
c2.metric("Duplicate rows", f"{p['duplicate_rows']:,}", border=True)
c3.metric("Quality score", f"{p['score']:.1f}%", border=True)

u, r, _ = st.columns([1, 1.3, 3])
if u.button("Undo last change", disabled=not st.session_state.history, width="stretch", icon=":material/undo:"):
    state.undo()
    st.rerun()
with r.popover("Restore original", icon=":material/restore:", width="stretch"):
    st.write("Discard every cleaning step and return to the dataset as it was imported.")
    if st.button("Yes, restore original", type="primary", key="confirm_restore"):
        state.restore_original()
        st.rerun()

st.divider()
operation = st.selectbox("Cleaning operation", ["Handle missing values", "Remove duplicate rows", "Trim whitespace",
                                                "Standardize text", "Convert column type"])
cols = list(df.columns)
texts = text_columns(df)
ready, preview, label = True, df, ""

if operation == "Handle missing values":
    selected = st.multiselect("Columns", cols, default=[c for c in cols if df[c].isna().any()])
    strategy = st.selectbox("Strategy", MISSING_STRATEGIES)
    constant = st.text_input("Replacement value", "Unknown") if strategy == "Fill with constant" else None
    skipped = incompatible_columns(df, selected, strategy)
    if skipped:
        st.warning(f"{strategy} only works on numeric columns. These will be left unchanged: {', '.join(skipped)}.")
    ready = bool(selected)
    preview = clean_missing(df, selected, strategy, constant)
    label = f"Missing values: {strategy} ({len(selected)} column{'s' if len(selected) != 1 else ''})"
elif operation == "Remove duplicate rows":
    mode = st.radio("Compare", ["All columns", "Selected columns"], horizontal=True)
    subset = st.multiselect("Columns to compare", cols, default=cols, disabled=mode == "All columns")
    keep = st.selectbox("Keep", ["first", "last"])
    ready = mode == "All columns" or bool(subset)
    preview = remove_duplicates(df, subset=None if mode == "All columns" else subset, keep=keep)
    label = "Removed duplicate rows"
elif operation == "Trim whitespace":
    selected = st.multiselect("Text columns", texts, default=texts)
    ready = bool(selected)
    preview = trim_whitespace(df, selected)
    label = f"Trimmed whitespace ({len(selected)} column{'s' if len(selected) != 1 else ''})"
elif operation == "Standardize text":
    selected = st.multiselect("Text columns", texts)
    case = st.selectbox("Format", TEXT_FORMATS)
    ready = bool(selected)
    preview = standardize_text(df, selected, case)
    label = f"Standardized text: {case} ({len(selected)} column{'s' if len(selected) != 1 else ''})"
else:
    column = st.selectbox("Column", cols)
    target = st.selectbox("Target type", TARGET_TYPES)
    dayfirst = decimal_comma = False
    if target == "Datetime":
        dayfirst = st.checkbox("Day first (DD/MM/YYYY)", help="Tick this for Brazilian / European dates such as 03/04/2025 = 3 April.")
    if target in ("Numeric", "Integer"):
        decimal_comma = st.checkbox("Decimal comma (1.234,56)", help="Tick this for Brazilian / European numbers.")
    try:
        preview = convert_type(df, column, target, dayfirst=dayfirst, decimal_comma=decimal_comma)
        lost = int(preview[column].isna().sum() - df[column].isna().sum())
        if lost > 0:
            st.warning(f"{lost:,} value{'s' if lost != 1 else ''} could not be converted and will become missing.")
    except Exception as exc:
        st.error(str(exc))
        ready, preview = False, df
    label = f"Converted {column} to {target}"

st.markdown("#### Preview")
before_missing, after_missing = int(df.isna().sum().sum()), int(preview.isna().sum().sum())
m1, m2, m3 = st.columns(3)
m1.metric("Rows after", f"{len(preview):,}", f"{len(preview) - len(df):+,}", delta_color="off", border=True)
m2.metric("Missing values after", f"{after_missing:,}", f"{after_missing - before_missing:+,}", delta_color="inverse", border=True)
m3.metric("Columns", f"{len(preview.columns):,}", border=True)
changed = ready and not preview.equals(df)
dataframe_view(preview.head(15))
if ready and not changed:
    st.caption("This operation would not change the dataset.")
if st.button("Apply transformation", type="primary", disabled=not changed, icon=":material/check:"):
    state.commit(preview, label)
    st.rerun()

st.divider()
st.markdown("#### Before & after")
original = st.session_state.original_df
if original is not None:
    x, y = st.columns(2)
    x.metric("Original rows", f"{len(original):,}", border=True)
    y.metric("Current rows", f"{len(df):,}", f"{len(df) - len(original):+,}", delta_color="off", border=True)
    with st.expander("View original data"):
        dataframe_view(original.head(20))
with st.expander(f"Cleaning history ({len(st.session_state.change_log)})"):
    if st.session_state.change_log:
        for i, item in enumerate(st.session_state.change_log, 1):
            st.markdown(f"{i}. {escape_md(item)}")
        st.caption(f"The last {MAX_HISTORY} steps can be undone.")
    else:
        st.caption("No transformations applied yet.")
