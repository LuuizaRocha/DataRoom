"""Shared page scaffolding."""
from __future__ import annotations

import html
import re

import streamlit as st

import state

_MD_SPECIAL = re.compile(r"([\\`*_{}\[\]()#+\-.!|<>~$])")


def escape_md(text: str) -> str:
    """Escape user-provided text (file names, labels) before putting it in markdown."""
    return _MD_SPECIAL.sub(r"\\\1", str(text))


def eyebrow(text: str) -> None:
    st.markdown(f"<div class='dr-eyebrow'>{html.escape(text)}</div>", unsafe_allow_html=True)


def page_header(kicker: str, title: str, subtitle: str) -> None:
    eyebrow(kicker)
    st.title(title)
    st.caption(subtitle)


def require_dataset(message: str):
    """Return the working DataFrame, or render an empty state and return None."""
    df = st.session_state.get("working_df")
    if df is not None:
        return df
    with st.container(border=True):
        st.markdown("#### No dataset loaded")
        st.write(message)
        c1, c2, _ = st.columns([1.2, 1.2, 2])
        if c1.button("Load sample dataset", type="primary", width="stretch", key="empty_sample",
                     icon=":material/science:"):
            state.load_sample_dataset()
            st.rerun()
        if c2.button("Import a file", width="stretch", key="empty_import", icon=":material/upload_file:"):
            st.switch_page("views/import_data.py")
        st.caption("The sample contains realistic retail transactions and is safe to explore.")
    return None
