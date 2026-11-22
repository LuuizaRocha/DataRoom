"""Plotly charts. Fonts and colors are inherited from the active Streamlit theme."""
import plotly.express as px
import streamlit as st

_MARGIN = dict(l=10, r=10, t=48, b=10)


def _show(fig, title):
    fig.update_layout(title=dict(text=title, x=0), margin=_MARGIN)
    st.plotly_chart(fig, width="stretch")


def histogram(df, column):
    fig = px.histogram(df, x=column, marginal="box")
    fig.update_layout(bargap=0.04)
    _show(fig, f"Distribution of {column}")


def bar(series, title):
    data = series.rename_axis("Value").reset_index(name="Count")
    data["Value"] = data["Value"].astype(str)
    fig = px.bar(data, x="Count", y="Value", orientation="h")
    fig.update_yaxes(type="category", categoryorder="total ascending", title=None)
    _show(fig, title)


def heatmap(corr):
    fig = px.imshow(corr, text_auto=".2f", aspect="auto", zmin=-1, zmax=1,
                    color_continuous_scale="RdBu_r")
    _show(fig, "Correlation matrix")


def line(data, x, y, title):
    fig = px.line(data, x=x, y=y, markers=True)
    _show(fig, title)
