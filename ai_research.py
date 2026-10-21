"""Evidence-led AI research for Sri Lanka's economy and investment landscape.

Requires OPENAI_API_KEY (environment variable or Streamlit secret). Uses the
Responses API with web search so answers can cite current public sources.
"""
from __future__ import annotations

import os
from typing import Any

SYSTEM_INSTRUCTIONS = """
You are Sri Lanka Economic Intelligence, an evidence-led economic research analyst.
Answer the user's question using web search and primary sources wherever possible.
Prioritise official sources: Central Bank of Sri Lanka, Department of Census and
Statistics, Ministry of Finance, Board of Investment of Sri Lanka, Urban Development
Authority, Colombo Stock Exchange, Sri Lanka Tourism Development Authority, IMF,
World Bank, Asian Development Bank, Government of India, and official Sri Lankan
government sources.

Focus areas include macroeconomics, public finance, trade, investment, property and
real estate development, construction, tourism, infrastructure, renewable energy,
logistics, technology, and India-Sri Lanka cooperation. The current Sri Lankan
President is Anura Kumara Disanayaka and India's Prime Minister is Narendra Modi,
but verify current officeholders and all time-sensitive claims using search.

Separate verified facts from analysis, scenarios, and recommendations. Give dates,
currency and units. Link sources inline and include publication dates when available.
Never invent market prices, property returns, official statistics, project approvals,
or government commitments. Do not present speculative forecasts as facts. For real
estate, explain risks, planning/zoning, title diligence, financing, demand, FX exposure,
and environmental or infrastructure constraints when relevant. For bilateral
partnership analysis, assess commercial opportunities and risks neutrally, including
Sri Lanka's debt sustainability, sovereignty, procurement transparency, and regional
competition. If evidence is weak or sources disagree, say so clearly.
"""

def research_with_ai(question: str, api_key: str | None = None, model: str | None = None) -> str:
    """Search the web and synthesise a cited answer with the OpenAI Responses API."""
    cleaned = question.strip()
    if not cleaned:
        raise ValueError("Enter a research question first.")

    key = api_key or os.getenv("OPENAI_API_KEY")
    if not key:
        raise RuntimeError(
            "AI research is not connected yet. Add OPENAI_API_KEY to your "
            "Streamlit app secrets or deployment environment to enable it."
        )

    try:
        from openai import OpenAI
    except ImportError as exc:
        raise RuntimeError(
            "The OpenAI package is not installed. Install the project's requirements."
        ) from exc

    client = OpenAI(api_key=key)
    response: Any = client.responses.create(
        model=model or os.getenv("OPENAI_MODEL", "gpt-4.1-mini"),
        tools=[{"type": "web_search"}],
        instructions=SYSTEM_INSTRUCTIONS,
        input=(
            "Research this question about Sri Lanka using current web sources. "
            "Structure the answer with: Executive summary; Verified facts and dates; "
            "What it could mean for Sri Lankan businesses/investors; Risks and unknowns; "
            "Sources. Make clear what is evidence and what is analysis.\n\n"
            f"Research question: {cleaned}"
        ),
    )
    answer = getattr(response, "output_text", None)
    if not answer or not answer.strip():
        raise RuntimeError("The AI service returned no text. Please try a narrower question.")
    return answer.strip()
