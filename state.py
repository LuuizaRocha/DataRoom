"""Session state for the workspace: one place that owns every mutation.

Views never write to ``st.session_state`` directly for dataset data; they call
the functions below so history, change log and activity stay consistent.
"""
from __future__ import annotations

from datetime import datetime

import pandas as pd
import streamlit as st

from config import MAX_ACTIVITY, MAX_HISTORY

_DEFAULTS = {
    "original_df": None,
    "working_df": None,
    "dataset_name": None,
    "source_type": None,
    "history": [],        # undoable steps: {"label", "before"}
    "change_log": [],     # applied cleaning labels, oldest first
    "filters": [],        # Data Explorer filters
    "activity": [],       # {"time", "message"}, newest first
    "flash": None,        # (message, icon) shown once on the next run
}


def init_state() -> None:
    for key, value in _DEFAULTS.items():
        if key not in st.session_state:
            st.session_state[key] = list(value) if isinstance(value, list) else value


def has_data() -> bool:
    return st.session_state.get("working_df") is not None


def log_activity(message: str) -> None:
    entry = {"time": datetime.now().strftime("%H:%M"), "message": message}
    st.session_state.activity.insert(0, entry)
    del st.session_state.activity[MAX_ACTIVITY:]


def flash(message: str, icon: str | None = None) -> None:
    """Queue a toast that survives ``st.rerun`` / ``st.switch_page``."""
    st.session_state.flash = (message, icon)


def show_flash() -> None:
    queued = st.session_state.get("flash")
    if queued:
        st.session_state.flash = None
        message, icon = queued
        st.toast(message, icon=icon)


def load_dataset(df: pd.DataFrame, name: str, source: str) -> None:
    """Make ``df`` the active dataset and reset everything derived from the previous one."""
    st.session_state.original_df = df.copy(deep=True)
    st.session_state.working_df = df
    st.session_state.dataset_name = name
    st.session_state.source_type = source
    st.session_state.history = []
    st.session_state.change_log = []
    st.session_state.filters = []
    log_activity(f"Loaded {name} · {len(df):,} rows")
    flash(f"Loaded {len(df):,} rows and {len(df.columns):,} columns.", ":material/check_circle:")


def load_sample_dataset() -> None:
    from core.importer import load_sample

    load_dataset(load_sample(), "sample_dataset.csv", "Sample")


def clear_dataset() -> None:
    for key in ("original_df", "working_df", "dataset_name", "source_type"):
        st.session_state[key] = None
    st.session_state.history = []
    st.session_state.change_log = []
    st.session_state.filters = []
    log_activity("Cleared the workspace")


def commit(new_df: pd.DataFrame, label: str) -> None:
    """Apply a cleaning step, keeping the previous frame so it can be undone."""
    st.session_state.history.append({"label": label, "before": st.session_state.working_df})
    del st.session_state.history[:-MAX_HISTORY]
    st.session_state.working_df = new_df
    st.session_state.change_log.append(label)
    st.session_state.filters = []
    log_activity(label)
    flash(f"Applied: {label}", ":material/check_circle:")


def undo() -> None:
    if not st.session_state.history:
        return
    step = st.session_state.history.pop()
    st.session_state.working_df = step["before"]
    if st.session_state.change_log:
        st.session_state.change_log.pop()
    st.session_state.filters = []
    log_activity(f"Undid: {step['label']}")
    flash(f"Undid: {step['label']}", ":material/undo:")


def restore_original() -> None:
    original = st.session_state.original_df
    if original is None:
        return
    st.session_state.working_df = original.copy(deep=True)
    st.session_state.history = []
    st.session_state.change_log = []
    st.session_state.filters = []
    log_activity("Restored the original dataset")
    flash("Restored the original dataset.", ":material/restore:")
