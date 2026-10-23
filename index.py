"""Vercel entrypoint for the Sri Lanka Economic Intelligence API.

Vercel detects the exported ASGI application and routes requests through FastAPI.
The existing api.main module remains the source of truth for routes and database logic.
"""
from api.main import app
