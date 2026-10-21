"""Smoke tests for the Streamlit interface using Streamlit's AppTest."""
import pytest
from streamlit.testing.v1 import AppTest


@pytest.mark.parametrize(
    "page",
    [
        "Overview",
        "Labour-market trends",
        "Data explorer",
        "Sources & methodology",
    ],
)
def test_each_dashboard_page_renders_without_uncaught_exception(page: str) -> None:
    """Every main navigation destination should render without an app exception."""
    app = AppTest.from_file("app.py", default_timeout=30)
    app.session_state["page"] = page
    app.run()
    assert not app.exception, f"App crashed on {page}: {app.exception}"
