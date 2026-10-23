"""Smoke tests for the Streamlit interface using Streamlit's AppTest."""
import pytest
from streamlit.testing.v1 import AppTest
from pathlib import Path


@pytest.mark.parametrize(
    "page",
    [
        "Overview",
        "Labour-market trends",
        "Data explorer",
        "AI research studio",
        "Sources & methodology",
    ],
)
def test_each_dashboard_page_renders_without_uncaught_exception(page: str) -> None:
    """Every main navigation destination should render without an app exception."""
    app = AppTest.from_file(Path(__file__).resolve().parents[1] / "app.py", default_timeout=30)
    app.session_state["page"] = page
    app.run()
    assert not app.exception, f"App crashed on {page}: {app.exception}"
