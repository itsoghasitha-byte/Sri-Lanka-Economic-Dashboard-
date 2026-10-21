"""API backend for the Sri Lanka Economic Intelligence project.

Uses PostgreSQL when DATABASE_URL is set (recommended: free-tier Supabase Postgres).
Falls back to SQLite for local development. Never place database credentials in frontend code.
"""
from __future__ import annotations
import os
import sqlite3
import time
from collections import defaultdict, deque
from contextlib import contextmanager
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from fastapi import FastAPI, HTTPException, Query, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

ROOT = Path(__file__).resolve().parents[1]
DATABASE_URL = os.getenv("DATABASE_URL", "").strip()
SQLITE_PATH = Path(os.getenv("SQLITE_PATH", str(ROOT / "data" / "economic_intel.db")))
DEMO_ROWS = [
    ("2025", "participation_rate", "Labour-force participation", 49.4, "%", "labour", "Department of Census and Statistics", "https://www.statistics.gov.lk/LabourForce/StaticalInformation/Bulletins/", "bundled_sample"),
    ("2025", "unemployment_rate", "Unemployment rate", 3.9, "%", "labour", "Department of Census and Statistics", "https://www.statistics.gov.lk/LabourForce/StaticalInformation/Bulletins/", "bundled_sample"),
    ("2026 Q1", "participation_rate", "Labour-force participation", 49.2, "%", "labour", "Department of Census and Statistics", "https://www.statistics.gov.lk/LabourForce/StaticalInformation/QuarterlyReports/", "bundled_sample"),
    ("2026 Q1", "unemployment_rate", "Unemployment rate", 3.7, "%", "labour", "Department of Census and Statistics", "https://www.statistics.gov.lk/LabourForce/StaticalInformation/QuarterlyReports/", "bundled_sample"),
    ("2026 Q2", "participation_rate", "Labour-force participation", 50.0, "%", "labour", "Department of Census and Statistics", "https://www.statistics.gov.lk/LabourForce/StaticalInformation/QuarterlyReports/", "bundled_sample"),
    ("2026 Q2", "unemployment_rate", "Unemployment rate", 4.0, "%", "labour", "Department of Census and Statistics", "https://www.statistics.gov.lk/LabourForce/StaticalInformation/QuarterlyReports/", "bundled_sample"),
]

app = FastAPI(title="Lanka Intel API", version="1.0.0", description="Source-aware economic indicator API")
allowed_origins = [x.strip() for x in os.getenv("CORS_ORIGINS", "http://localhost:8000,http://127.0.0.1:8000").split(",") if x.strip()]
app.add_middleware(CORSMiddleware, allow_origins=allowed_origins, allow_credentials=False, allow_methods=["GET", "POST", "OPTIONS"], allow_headers=["Content-Type", "Authorization"])

class ResearchRecord(BaseModel):
    question: str = Field(min_length=5, max_length=1500)
    answer: str = Field(min_length=1, max_length=20000)
    sources: list[str] = Field(default_factory=list, max_length=30)

class ResearchQuestion(BaseModel):
    question: str = Field(min_length=5, max_length=1200)

_request_times = defaultdict(deque)

def _allow_research_request(client_ip: str) -> bool:
    now = time.monotonic()
    history = _request_times[client_ip]
    while history and now - history[0] > 60:
        history.popleft()
    if len(history) >= 5:
        return False
    history.append(now)
    return True

def _connect():
    if DATABASE_URL:
        try:
            import psycopg
            from psycopg.rows import dict_row
            conn = psycopg.connect(DATABASE_URL, row_factory=dict_row, connect_timeout=8)
            return conn, True
        except Exception as exc:
            raise RuntimeError("PostgreSQL connection failed. Check DATABASE_URL and network access.") from exc
    SQLITE_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(SQLITE_PATH, timeout=8)
    conn.row_factory = sqlite3.Row
    return conn, False

@contextmanager
def connection():
    conn, postgres = _connect()
    try:
        yield conn, postgres
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()

def _execute(conn: Any, postgres: bool, sql: str, params: tuple = ()):
    return conn.execute(sql.replace("?", "%s") if postgres else sql, params)

def init_db():
    with connection() as (conn, pg):
        if pg:
            conn.execute("""CREATE TABLE IF NOT EXISTS indicators (
                id BIGSERIAL PRIMARY KEY, period TEXT NOT NULL, indicator_key TEXT NOT NULL,
                indicator TEXT NOT NULL, value DOUBLE PRECISION NOT NULL, unit TEXT NOT NULL,
                category TEXT NOT NULL, source TEXT NOT NULL, source_url TEXT NOT NULL,
                status TEXT NOT NULL DEFAULT 'unverified', updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
                UNIQUE(period, indicator_key, source))""")
            conn.execute("""CREATE TABLE IF NOT EXISTS research_history (
                id BIGSERIAL PRIMARY KEY, question TEXT NOT NULL, answer TEXT NOT NULL,
                sources JSONB NOT NULL DEFAULT '[]'::jsonb, created_at TIMESTAMPTZ NOT NULL DEFAULT NOW())""")
        else:
            conn.execute("""CREATE TABLE IF NOT EXISTS indicators (
                id INTEGER PRIMARY KEY AUTOINCREMENT, period TEXT NOT NULL, indicator_key TEXT NOT NULL,
                indicator TEXT NOT NULL, value REAL NOT NULL, unit TEXT NOT NULL, category TEXT NOT NULL,
                source TEXT NOT NULL, source_url TEXT NOT NULL, status TEXT NOT NULL DEFAULT 'unverified',
                updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(period, indicator_key, source))""")
            conn.execute("""CREATE TABLE IF NOT EXISTS research_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT, question TEXT NOT NULL, answer TEXT NOT NULL,
                sources TEXT NOT NULL DEFAULT '[]', created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP)""")
        count = _execute(conn, pg, "SELECT COUNT(*) AS n FROM indicators").fetchone()
        if int(count["n"]) == 0:
            for row in DEMO_ROWS:
                _execute(conn, pg, """INSERT INTO indicators
                    (period,indicator_key,indicator,value,unit,category,source,source_url,status)
                    VALUES (?,?,?,?,?,?,?,?,?)""", row)

@app.on_event("startup")
def startup():
    init_db()

@app.get("/health")
def health():
    try:
        with connection() as (conn, pg):
            count = _execute(conn, pg, "SELECT COUNT(*) AS n FROM indicators").fetchone()["n"]
        return {"status": "ok", "database": "postgresql" if pg else "sqlite", "indicator_rows": int(count), "timestamp": datetime.now(timezone.utc).isoformat()}
    except Exception as exc:
        raise HTTPException(status_code=503, detail="Database unavailable or misconfigured") from exc

@app.get("/api/indicators")
def list_indicators(q: str = Query(default="", max_length=120), category: str = Query(default="", max_length=40), limit: int = Query(default=500, ge=1, le=2000)):
    clauses, params = [], []
    if q.strip():
        clauses.append("(LOWER(indicator) LIKE ? OR LOWER(source) LIKE ? OR LOWER(period) LIKE ?)")
        term = "%" + q.strip().lower() + "%"
        params.extend([term, term, term])
    if category.strip():
        clauses.append("LOWER(category) = ?")
        params.append(category.strip().lower())
    sql = "SELECT period,indicator_key,indicator,value,unit,category,source,source_url,status,updated_at FROM indicators"
    if clauses:
        sql += " WHERE " + " AND ".join(clauses)
    sql += " ORDER BY period, indicator LIMIT ?"
    params.append(limit)
    try:
        with connection() as (conn, pg):
            rows = _execute(conn, pg, sql, tuple(params)).fetchall()
        return {"data": [dict(row) for row in rows], "count": len(rows), "database": "postgresql" if DATABASE_URL else "sqlite"}
    except Exception as exc:
        raise HTTPException(status_code=503, detail="Unable to query indicator database") from exc

@app.post("/api/research/ask")
def ask_research(payload: ResearchQuestion, request: Request):
    """Run web-grounded AI research with the provider key kept on the server."""
    client_ip = request.client.host if request.client else "unknown"
    if not _allow_research_request(client_ip):
        raise HTTPException(status_code=429, detail="Research limit reached. Please wait a minute and try again.")
    api_key = os.getenv("OPENAI_API_KEY", "").strip()
    if not api_key:
        raise HTTPException(status_code=503, detail="AI research is not configured on the API server yet.")
    try:
        from openai import OpenAI
        response = OpenAI(api_key=api_key).responses.create(
            model=os.getenv("OPENAI_MODEL", "gpt-4.1-mini"),
            tools=[{"type": "web_search"}],
            instructions=("You are an evidence-led Sri Lankan economic research analyst. Prioritise official Sri Lankan government, Central Bank of Sri Lanka, Department of Census and Statistics, IMF, World Bank and ADB sources. Distinguish verified facts from analysis, state dates and units, never invent figures, and provide clickable source URLs. Note uncertainty."),
            input="Research this question about Sri Lanka using current web sources. Structure the answer as Summary; Verified facts; Implications; Risks and unknowns; Sources. Do not give personalised financial or legal advice.\n\nQuestion: " + payload.question.strip(),
        )
        answer = getattr(response, "output_text", "")
        if not answer or not answer.strip():
            raise RuntimeError("AI returned an empty answer")
        with connection() as (conn, pg):
            if pg:
                saved = conn.execute(
                    "INSERT INTO research_history (question,answer,sources) VALUES (%s,%s,%s::jsonb) RETURNING id",
                    (payload.question.strip(), answer.strip(), "[]"),
                ).fetchone()
            else:
                cur = conn.execute(
                    "INSERT INTO research_history (question,answer,sources) VALUES (?,?,?)",
                    (payload.question.strip(), answer.strip(), "[]"),
                )
                saved = {"id": cur.lastrowid}
        return {"answer": answer.strip(), "saved": True, "id": saved["id"] if saved else None}
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(status_code=502, detail="Research service failed. Check server logs and provider configuration.") from exc

@app.get("/api/research")
def list_research(limit: int = Query(default=20, ge=1, le=100)):
    try:
        with connection() as (conn, pg):
            rows = _execute(conn, pg, "SELECT id,question,answer,sources,created_at FROM research_history ORDER BY id DESC LIMIT ?", (limit,)).fetchall()
        import json
        data = []
        for row in rows:
            item = dict(row)
            if isinstance(item.get("sources"), str):
                item["sources"] = json.loads(item["sources"])
            data.append(item)
        return {"data": data, "count": len(data)}
    except Exception as exc:
        raise HTTPException(status_code=503, detail="Unable to load research history") from exc
