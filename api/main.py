"""API backend for the Sri Lanka Economic Intelligence project.

Uses PostgreSQL when DATABASE_URL is set (recommended: free-tier Supabase Postgres).
Falls back to SQLite for local development. Never place database credentials in frontend code.
"""
from __future__ import annotations
import os
import sqlite3
from contextlib import contextmanager
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from fastapi import FastAPI, HTTPException, Query
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

@app.post("/api/research", status_code=201)
def save_research(record: ResearchRecord):
    """Store research produced by a trusted server-side AI workflow; this endpoint is not an AI proxy."""
    import json
    for source in record.sources:
        if not source.startswith(("https://", "http://")):
            raise HTTPException(status_code=422, detail="Every source must be an HTTP(S) URL")
    try:
        with connection() as (conn, pg):
            sql = "INSERT INTO research_history (question,answer,sources) VALUES (?,?,?)"
            source_value = json.dumps(record.sources) if not pg else json.dumps(record.sources)
            cur = _execute(conn, pg, sql, (record.question.strip(), record.answer.strip(), source_value))
            if pg:
                saved = cur.fetchone() if "RETURNING" in sql else None
            else:
                saved = {"id": cur.lastrowid}
        return {"saved": True, "id": saved["id"] if saved else None}
    except Exception as exc:
        raise HTTPException(status_code=503, detail="Unable to save research record") from exc

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
