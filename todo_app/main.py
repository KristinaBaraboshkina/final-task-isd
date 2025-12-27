from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional
import sqlite3
import os
from contextlib import contextmanager

app = FastAPI(title="ToDo Service", version="1.0.0")

DB_PATH = "/app/data/todo.db"


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
            CREATE TABLE IF NOT EXISTS items (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                description TEXT,
                completed BOOLEAN NOT NULL DEFAULT 0
            )
        """)
        conn.commit()


class ItemCreate(BaseModel):
    title: str
    description: Optional[str] = None
    completed: bool = False


class ItemUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    completed: Optional[bool] = None


class Item(BaseModel):
    id: int
    title: str
    description: Optional[str] = None
    completed: bool


@app.on_event("startup")
async def startup_event():
    init_db()


@app.post("/items", response_model=Item, status_code=201)
async def create_item(item: ItemCreate):
    with get_db() as conn:
        cursor = conn.execute(
            "INSERT INTO items (title, description, completed) VALUES (?, ?, ?)",
            (item.title, item.description, item.completed)
        )
        conn.commit()
        item_id = cursor.lastrowid

        row = conn.execute("SELECT * FROM items WHERE id = ?", (item_id,)).fetchone()
        return dict(row)


@app.get("/items", response_model=list[Item])
async def get_items():
    with get_db() as conn:
        rows = conn.execute("SELECT * FROM items").fetchall()
        return [dict(row) for row in rows]


@app.get("/items/{item_id}", response_model=Item)
async def get_item(item_id: int):
    with get_db() as conn:
        row = conn.execute("SELECT * FROM items WHERE id = ?", (item_id,)).fetchone()
        if not row:
            raise HTTPException(status_code=404, detail="Item not found")
        return dict(row)


@app.put("/items/{item_id}", response_model=Item)
async def update_item(item_id: int, item: ItemUpdate):
    with get_db() as conn:
        row = conn.execute("SELECT * FROM items WHERE id = ?", (item_id,)).fetchone()
        if not row:
            raise HTTPException(status_code=404, detail="Item not found")

        update_fields = []
        params = []

        if item.title is not None:
            update_fields.append("title = ?")
            params.append(item.title)
        if item.description is not None:
            update_fields.append("description = ?")
            params.append(item.description)
        if item.completed is not None:
            update_fields.append("completed = ?")
            params.append(item.completed)

        if update_fields:
            params.append(item_id)
            query = f"UPDATE items SET {', '.join(update_fields)} WHERE id = ?"
            conn.execute(query, params)
            conn.commit()

        row = conn.execute("SELECT * FROM items WHERE id = ?", (item_id,)).fetchone()
        return dict(row)


@app.delete("/items/{item_id}", status_code=204)
async def delete_item(item_id: int):
    with get_db() as conn:
        cursor = conn.execute("DELETE FROM items WHERE id = ?", (item_id,))
        conn.commit()
        if cursor.rowcount == 0:
            raise HTTPException(status_code=404, detail="Item not found")


@app.get("/")
async def root():
    return {"message": "ToDo Service API", "docs": "/docs"}
