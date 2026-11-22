"""Sidebar content rendered below the navigation menu."""
import html

import streamlit as st

import state
from config import APP_TAGLINE, APP_VERSION


def render_sidebar_footer():
    with st.sidebar:
        st.divider()
        df = st.session_state.get("working_df")
        if df is not None:
            st.markdown("<div class='dr-eyebrow'>Active dataset</div>", unsafe_allow_html=True)
            name = html.escape(st.session_state.get("dataset_name") or "Untitled dataset")
            st.markdown(f"<div class='dr-dataset'>{name}</div>", unsafe_allow_html=True)
            st.caption(f"{len(df):,} rows · {len(df.columns):,} columns")
            steps = len(st.session_state.change_log)
            if steps:
                st.caption(f"{steps} cleaning step{'s' if steps != 1 else ''} applied")
            if st.button("Close dataset", width="stretch", icon=":material/close:", key="sidebar_close"):
                state.clear_dataset()
                st.rerun()
        else:
            st.caption("No dataset loaded")
        st.caption(f"{APP_TAGLINE} · v{APP_VERSION}")
