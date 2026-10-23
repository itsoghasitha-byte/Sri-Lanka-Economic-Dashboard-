"""Tests for the AI research wrapper; no live API calls are made."""
import sys
from types import SimpleNamespace

import pytest

from ai_research import research_with_ai


def test_empty_question_is_rejected_before_api_key_check():
    with pytest.raises(ValueError, match="Enter a research question"):
        research_with_ai("   ", api_key="test-key")


def test_missing_api_key_gives_actionable_setup_message(monkeypatch):
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    with pytest.raises(RuntimeError, match="Add OPENAI_API_KEY"):
        research_with_ai("What do the latest reports say?", api_key=None)


def test_research_calls_responses_api_with_web_search(monkeypatch):
    calls = {}

    class FakeResponses:
        def create(self, **kwargs):
            calls.update(kwargs)
            return SimpleNamespace(output_text="Summary with source links.")

    class FakeClient:
        def __init__(self, api_key):
            calls["api_key"] = api_key
            self.responses = FakeResponses()

    monkeypatch.setitem(sys.modules, "openai", SimpleNamespace(OpenAI=FakeClient))
    result = research_with_ai("Assess Sri Lanka's property market.", api_key="test-key", model="test-model")

    assert result == "Summary with source links."
    assert calls["api_key"] == "test-key"
    assert calls["model"] == "test-model"
    assert {"type": "web_search"} in calls["tools"]
    assert "Sri Lanka's property market" in calls["input"]


def test_empty_ai_response_is_reported(monkeypatch):
    class FakeResponses:
        def create(self, **kwargs):
            return SimpleNamespace(output_text="")

    class FakeClient:
        def __init__(self, api_key):
            self.responses = FakeResponses()

    monkeypatch.setitem(sys.modules, "openai", SimpleNamespace(OpenAI=FakeClient))
    with pytest.raises(RuntimeError, match="returned no text"):
        research_with_ai("Search the latest official reports.", api_key="test-key")
