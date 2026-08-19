from fastapi import FastAPI
from fastapi.responses import JSONResponse, Response
from pydantic import BaseModel
from typing import Optional

from postgres_repository import PostgresTaskRepository
from supabase_client import supabase

print("Server running and connected to Supabase")

app = FastAPI(
    title="Task API",
    description="A simple CRUD API for managing tasks.",
    version="1.0"
)

# The ONE place that decides which storage backend is in use.
repo = PostgresTaskRepository()


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
    return repo.get_all()


@app.get("/tasks/{task_id}", summary="Get a single task", description="Returns one task by its id, or 404 if it doesn't exist.")
def get_task(task_id: int):
    task = repo.get_by_id(task_id)
    if task is None:
        return JSONResponse(
            status_code=404,
            content={"error": f"Task {task_id} not found"}
        )
    return task


@app.post("/tasks", summary="Create a task", description="Creates a new task. Requires a non-empty title.", status_code=201)
def create_task(task: TaskCreate):
    if not task.title or not task.title.strip():
        return JSONResponse(
            status_code=400,
            content={"error": "Title is required and cannot be empty"}
        )

    new_task = repo.create(task.title)
    return JSONResponse(status_code=201, content=new_task)


@app.put("/tasks/{task_id}", summary="Update a task", description="Updates a task's title and/or done status. Returns 404 if the task doesn't exist.")
def update_task(task_id: int, task: TaskUpdate):
    existing = repo.get_by_id(task_id)
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

    updated = repo.update(task_id, task.title, task.done)
    return updated


@app.delete("/tasks/{task_id}", summary="Delete a task", description="Deletes a task by id. Returns 204 with no body on success, or 404 if not found.")
def delete_task(task_id: int):
    deleted = repo.delete(task_id)
    if not deleted:
        return JSONResponse(
            status_code=404,
            content={"error": f"Task {task_id} not found"}
        )
    return Response(status_code=204)