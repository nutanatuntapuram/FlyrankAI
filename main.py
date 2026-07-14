from fastapi import FastAPI
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import Optional
app = FastAPI()

tasks = [
    {"id": 1, "title": "Buy groceries", "done": False},
    {"id": 2, "title": "Finish assignment", "done": False},
    {"id": 3, "title": "Read a book", "done": True},
]

class TaskCreate(BaseModel):
    title: Optional[str] = None

@app.get("/")
def read_root():
    return {
        "name": "Task API",
        "version": "1.0",
        "endpoints": ["/tasks"]
    }

@app.get("/health")
def health_check():
    return {"status": "ok"}

@app.get("/tasks")
def get_tasks():
    return tasks

@app.get("/tasks/{task_id}")
def get_task(task_id: int):
    for task in tasks:
        if task["id"] == task_id:
            return task
    return JSONResponse(
        status_code=404,
        content={"error": f"Task {task_id} not found"}
    )

@app.post("/tasks")
def create_task(task: TaskCreate):
    # Validate: title must exist and not be empty/whitespace
    if not task.title or not task.title.strip():
        return JSONResponse(
            status_code=400,
            content={"error": "Title is required and cannot be empty"}
        )

    # Generate next available id
    next_id = max((t["id"] for t in tasks), default=0) + 1

    new_task = {
        "id": next_id,
        "title": task.title,
        "done": False
    }
    tasks.append(new_task)

    return JSONResponse(status_code=201, content=new_task)