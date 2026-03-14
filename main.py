
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import sqlite3

app = FastAPI()

# Database setup
def get_db_connection():
    conn = sqlite3.connect("todo.db")
    conn.row_factory = sqlite3.Row
    return conn

def create_table():
    conn = get_db_connection()
    conn.execute("CREATE TABLE IF NOT EXISTS todos (id INTEGER PRIMARY KEY AUTOINCREMENT, title TEXT NOT NULL, completed BOOLEAN NOT NULL DEFAULT 0)")
    conn.commit()
    conn.close()

create_table()

class TodoItem(BaseModel):
    title: str
    completed: bool = False

@app.get("/todos/")
async def read_todos():
    conn = get_db_connection()
    todos = conn.execute("SELECT * FROM todos").fetchall()
    conn.close()
    return [dict(todo) for todo in todos]

@app.post("/todos/")
async def create_todo(todo: TodoItem):
    conn = get_db_connection()
    cursor = conn.execute("INSERT INTO todos (title, completed) VALUES (?, ?)", (todo.title, todo.completed))
    conn.commit()
    new_todo_id = cursor.lastrowid
    new_todo = conn.execute("SELECT * FROM todos WHERE id = ?", (new_todo_id,)).fetchone()
    conn.close()
    return dict(new_todo)

@app.put("/todos/{todo_id}")
async def update_todo(todo_id: int, todo: TodoItem):
    conn = get_db_connection()
    cursor = conn.execute("UPDATE todos SET title = ?, completed = ? WHERE id = ?", (todo.title, todo.completed, todo_id))
    conn.commit()
    if cursor.rowcount == 0:
        raise HTTPException(status_code=404, detail="Todo not found")
    updated_todo = conn.execute("SELECT * FROM todos WHERE id = ?", (todo_id,)).fetchone()
    conn.close()
    return dict(updated_todo)

@app.delete("/todos/{todo_id}")
async def delete_todo(todo_id: int):
    conn = get_db_connection()
    cursor = conn.execute("DELETE FROM todos WHERE id = ?", (todo_id,))
    conn.commit()
    conn.close()
    if cursor.rowcount == 0:
        raise HTTPException(status_code=404, detail="Todo not found")
    return {"message": "Todo deleted successfully"}
