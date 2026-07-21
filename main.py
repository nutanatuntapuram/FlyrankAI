import sqlite3
from fastapi import FastAPI
from fastapi.responses import JSONResponse, Response
from pydantic import BaseModel
from typing import Optional

app = FastAPI(
    title="Task API",
    description="A simple CRUD API for managing tasks.",
    version="1.0"
)

DB_FILE = "tasks.db"


def get_connection():
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row  # lets us access columns by name, like a dict
    return conn


def init_db():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS tasks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            done BOOLEAN NOT NULL DEFAULT 0
        )
    """)

    cursor.execute("SELECT COUNT(*) FROM tasks")
    count = cursor.fetchone()[0]

    if count == 0:
        cursor.executemany(
            "INSERT INTO tasks (title, done) VALUES (?, ?)",
            [
                ("Buy groceries", False),
                ("Finish assignment", False),
                ("Read a book", True),
            ]
        )

    conn.commit()
    conn.close()


init_db()  # runs once when the app starts


tasks = [
    {"id": 1, "title": "Buy groceries", "done": False},
    {"id": 2, "title": "Finish assignment", "done": False},
    {"id": 3, "title": "Read a book", "done": True},
]

class TaskCreate(BaseModel):
    title: Optional[str] = None

class TaskUpdate(BaseModel):
    title: Optional[str] = None
    done: Optional[bool] = None


@app.get("/", summary="API info", description="Returns basic information about this API.")
def read_root():
    return {
        "name": "Task API",
        "version": "1.0",
        "endpoints": ["/tasks"]
    }


@app.get("/health", summary="Health check", description="Returns OK if the server is running.")
def health_check():
    return {"status": "ok"}


@app.get("/tasks", summary="List all tasks", description="Returns the full list of tasks.")
def get_tasks():
    return tasks


@app.get("/tasks/{task_id}", summary="Get a single task", description="Returns one task by its id, or 404 if it doesn't exist.")
def get_task(task_id: int):
    for task in tasks:
        if task["id"] == task_id:
            return task
    return JSONResponse(
        status_code=404,
        content={"error": f"Task {task_id} not found"}
    )


@app.post("/tasks", summary="Create a task", description="Creates a new task. Requires a non-empty title.", status_code=201)
def create_task(task: TaskCreate):
    if not task.title or not task.title.strip():
        return JSONResponse(
            status_code=400,
            content={"error": "Title is required and cannot be empty"}
        )

    next_id = max((t["id"] for t in tasks), default=0) + 1
    new_task = {"id": next_id, "title": task.title, "done": False}
    tasks.append(new_task)

    return JSONResponse(status_code=201, content=new_task)


@app.put("/tasks/{task_id}", summary="Update a task", description="Updates a task's title and/or done status. Returns 404 if the task doesn't exist.")
def update_task(task_id: int, task: TaskUpdate):
    existing = None
    for t in tasks:
        if t["id"] == task_id:
            existing = t
            break

    if existing is None:
        return JSONResponse(
            status_code=404,
            content={"error": f"Task {task_id} not found"}
        )

    if task.title is not None and not task.title.strip():
        return JSONResponse(
            status_code=400,
            content={"error": "Title cannot be empty"}
        )

    if task.title is None and task.done is None:
        return JSONResponse(
            status_code=400,
            content={"error": "Provide at least a title or done field to update"}
        )

    if task.title is not None:
        existing["title"] = task.title
    if task.done is not None:
        existing["done"] = task.done

    return existing


@app.delete("/tasks/{task_id}", summary="Delete a task", description="Deletes a task by id. Returns 204 with no body on success, or 404 if not found.")
def delete_task(task_id: int):
    for i, t in enumerate(tasks):
        if t["id"] == task_id:
            tasks.pop(i)
            return Response(status_code=204)

    return JSONResponse(
        status_code=404,
        content={"error": f"Task {task_id} not found"}
    )