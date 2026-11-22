import streamlit as st


def dataframe_view(df, height="auto", **kwargs):
    st.dataframe(df, width="stretch", height=height, hide_index=True, **kwargs)
