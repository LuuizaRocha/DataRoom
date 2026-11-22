"""Minimal, theme-neutral CSS.

Colors, fonts and radii come from ``.streamlit/config.toml`` so every element
(widgets, tables, charts) stays consistent in both Light and Dark mode. This
stylesheet only adds spacing and a few typographic details, and never sets a
font-family or a hard-coded color.
"""
import streamlit as st

_CSS = """
<style>
.block-container { max-width: 1240px; padding-top: 2.4rem; padding-bottom: 4rem; }
h1 { letter-spacing: -0.02em; margin-bottom: 0.15rem; }
h3, h4 { letter-spacing: -0.01em; }
[data-testid="stMetricValue"] { font-variant-numeric: tabular-nums; }
.dr-eyebrow { font-size: 0.72rem; font-weight: 600; letter-spacing: 0.14em;
              text-transform: uppercase; opacity: 0.6; margin-bottom: 0.2rem; }
.dr-dataset { font-weight: 600; word-break: break-word; line-height: 1.3; }
.dr-muted { opacity: 0.65; font-size: 0.875rem; }
</style>
"""


def inject_css() -> None:
    st.markdown(_CSS, unsafe_allow_html=True)
