"""End-to-end checks that drive the real Streamlit app headlessly."""
import re
from pathlib import Path

import pytest
from streamlit.testing.v1 import AppTest

APP = str(Path(__file__).resolve().parents[1] / "app.py")
PAGES = ["views/overview.py", "views/import_data.py", "views/data_explorer.py",
         "views/data_cleaning.py", "views/analytics.py", "views/export_center.py"]


def new_app():
    return AppTest.from_file(APP, default_timeout=60).run()


def with_sample():
    at = new_app()
    next(b for b in at.button if b.label == "Load sample dataset").click().run()
    assert at.session_state.working_df is not None
    return at


@pytest.mark.parametrize("page", PAGES)
def test_every_page_renders_without_data(page):
    at = new_app()
    at.switch_page(page).run()
    assert not at.exception


@pytest.mark.parametrize("page", PAGES)
def test_every_page_renders_with_sample(page):
    at = with_sample()
    at.switch_page(page).run()
    assert not at.exception


def test_filters_persist_when_other_widgets_change():
    at = with_sample().switch_page("views/data_explorer.py").run()
    at.selectbox(key="flt_col").set_value("Region")
    at.selectbox(key="flt_mode").set_value("Equals").run()
    at.text_input(key="flt_val").set_value("North").run()
    next(b for b in at.button if b.label == "Add filter").click().run()
    assert len(at.session_state.filters) == 1
    at.text_input[0].set_value("zzz").run()          # touch another widget
    assert len(at.session_state.filters) == 1        # filter survives
    assert not at.exception


def test_invalid_numeric_filter_shows_error_not_crash():
    at = with_sample().switch_page("views/data_explorer.py").run()
    at.selectbox(key="flt_mode").set_value("Greater than").run()
    at.text_input(key="flt_val").set_value("abc").run()
    next(b for b in at.button if b.label == "Add filter").click().run()
    assert at.error and not at.exception and not at.session_state.filters


def test_clean_apply_undo_restore():
    at = with_sample().switch_page("views/data_cleaning.py").run()
    at.selectbox[0].set_value("Standardize text").run()
    at.multiselect[0].set_value(["Region"]).run()
    next(b for b in at.button if b.label == "Apply transformation").click().run()
    assert at.session_state.working_df["Region"].iloc[0] == "north"
    assert at.session_state.original_df["Region"].iloc[0] == "North"   # original untouched
    assert len(at.session_state.change_log) == 1
    next(b for b in at.button if b.label == "Undo last change").click().run()
    assert at.session_state.working_df["Region"].iloc[0] == "North"
    assert not at.exception


def test_security_filename_is_escaped_in_html():
    at = with_sample()
    at.session_state.dataset_name = "<img src=x onerror=alert(1)>.csv"
    at.run()
    html = " ".join(m.value for m in at.markdown)
    assert not re.search(r"(?<!\\)<img", html)   # only escaped forms (\\< or &lt;) may appear
