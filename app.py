"""DATA ROOM — entry point. Sets up the page, theme helpers and navigation."""
import streamlit as st

from components.sidebar import render_sidebar_footer
from components.styles import inject_css
from config import APP_NAME
from state import init_state, show_flash

st.set_page_config(page_title=APP_NAME, page_icon=":material/database:", layout="wide",
                   initial_sidebar_state="expanded")

init_state()
inject_css()
st.logo("assets/logo.svg", icon_image="assets/logo_mark.svg", size="large")

navigation = st.navigation([
    st.Page("views/overview.py", title="Overview", icon=":material/dashboard:", default=True),
    st.Page("views/import_data.py", title="Import Data", icon=":material/upload_file:"),
    st.Page("views/data_explorer.py", title="Data Explorer", icon=":material/table_view:"),
    st.Page("views/data_cleaning.py", title="Data Cleaning", icon=":material/cleaning_services:"),
    st.Page("views/analytics.py", title="Analytics", icon=":material/monitoring:"),
    st.Page("views/export_center.py", title="Export Center", icon=":material/download:"),
])

render_sidebar_footer()
show_flash()
navigation.run()
