import streamlit as st


def metric_row(items):
    """items: (label, value) or (label, value, delta) or (label, value, delta, help)."""
    cols = st.columns(len(items))
    for col, item in zip(cols, items):
        label, value, *rest = item
        delta = rest[0] if len(rest) > 0 else None
        help_text = rest[1] if len(rest) > 1 else None
        col.metric(label, value, delta, help=help_text, border=True)
