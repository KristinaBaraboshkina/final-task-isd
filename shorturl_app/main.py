from fastapi import FastAPI, HTTPException
from fastapi.responses import RedirectResponse
from pydantic import BaseModel, HttpUrl
import sqlite3
import os
import random
import string
from contextlib import contextmanager
from datetime import datetime

app = FastAPI(title="URL Shortener Service", version="1.0.0")

DB_PATH = "/app/data/shorturl.db"


@contextmanager
def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
    finally:
        conn.close()


def init_db():
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    with get_db() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS urls (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                short_id TEXT UNIQUE NOT NULL,
                full_url TEXT NOT NULL,
                created_at TEXT NOT NULL
            )
        """)
        conn.commit()


def generate_short_id(length: int = 6) -> str:
    characters = string.ascii_letters + string.digits
    return ''.join(random.choice(characters) for _ in range(length))


class URLCreate(BaseModel):
    url: str


class URLInfo(BaseModel):
    short_id: str
    full_url: str
    created_at: str


@app.on_event("startup")
async def startup_event():
    init_db()


@app.post("/shorten", response_model=dict, status_code=201)
async def shorten_url(url_data: URLCreate):
    with get_db() as conn:
        short_id = generate_short_id()

        while True:
            existing = conn.execute(
                "SELECT short_id FROM urls WHERE short_id = ?",
                (short_id,)
            ).fetchone()
            if not existing:
                break
            short_id = generate_short_id()

        created_at = datetime.utcnow().isoformat()

        conn.execute(
            "INSERT INTO urls (short_id, full_url, created_at) VALUES (?, ?, ?)",
            (short_id, url_data.url, created_at)
        )
        conn.commit()

        return {
            "short_id": short_id,
            "short_url": f"/{short_id}",
            "full_url": url_data.url
        }


@app.get("/{short_id}")
async def redirect_to_url(short_id: str):
    with get_db() as conn:
        row = conn.execute(
            "SELECT full_url FROM urls WHERE short_id = ?",
            (short_id,)
        ).fetchone()

        if not row:
            raise HTTPException(status_code=404, detail="Short URL not found")

        return RedirectResponse(url=row["full_url"], status_code=302)


@app.get("/stats/{short_id}", response_model=URLInfo)
async def get_url_stats(short_id: str):
    with get_db() as conn:
        row = conn.execute(
            "SELECT short_id, full_url, created_at FROM urls WHERE short_id = ?",
            (short_id,)
        ).fetchone()

        if not row:
            raise HTTPException(status_code=404, detail="Short URL not found")

        return dict(row)


@app.get("/")
async def root():
    return {"message": "URL Shortener Service API", "docs": "/docs"}
