from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from pydantic import BaseModel

from repository import (
    initialize_database,
    get_all_tasks,
    get_task,
    create_task,
    update_task,
    delete_task,
)


app = FastAPI(
    title="Task API",
    version="1.0",
)


# -----------------------------
# Pydantic Models
# -----------------------------

class Task(BaseModel):
    id: int
    title: str
    done: bool


class TaskCreate(BaseModel):
    title: str
    done: bool = False


class TaskUpdate(BaseModel):
    title: str
    done: bool


# -----------------------------
# Validation Error Handler
# -----------------------------

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(
    request: Request,
    exc: RequestValidationError
):
    return JSONResponse(
        status_code=400,
        content={"error": "Invalid request body"},
    )


# -----------------------------
# Database Startup
# -----------------------------

@app.on_event("startup")
def startup():
    initialize_database()


# -----------------------------
# Helper
# -----------------------------

def row_to_task(row):
    return Task(
        id=row[0],
        title=row[1],
        done=bool(row[2]),
    )


# -----------------------------
# Root
# -----------------------------

@app.get("/")
def root():
    return {
        "message": "Task API is running"
    }


# -----------------------------
# Health Check
# -----------------------------

@app.get("/health")
def health():
    return {
        "status": "ok"
    }


# -----------------------------
# GET all tasks
# -----------------------------

@app.get("/tasks", response_model=list[Task])
def get_tasks():
    rows = get_all_tasks()

    return [
        row_to_task(row)
        for row in rows
    ]


# -----------------------------
# GET one task
# -----------------------------

@app.get("/tasks/{task_id}", response_model=Task)
def get_single_task(task_id: int):
    row = get_task(task_id)

    if row is None:
        return JSONResponse(
            status_code=404,
            content={"detail": "Task not found"},
        )

    return row_to_task(row)


# -----------------------------
# CREATE task
# -----------------------------

@app.post("/tasks", response_model=Task, status_code=201)
def add_task(task: TaskCreate):

    if not task.title.strip():
        return JSONResponse(
            status_code=400,
            content={"detail": "Title cannot be empty"},
        )

    row = create_task(
        title=task.title.strip(),
        done=task.done,
    )

    return row_to_task(row)


# -----------------------------
# UPDATE task
# -----------------------------

@app.put("/tasks/{task_id}", response_model=Task)
def edit_task(
    task_id: int,
    task: TaskUpdate
):

    if not task.title.strip():
        return JSONResponse(
            status_code=400,
            content={"detail": "Title cannot be empty"},
        )

    row = update_task(
        task_id=task_id,
        title=task.title.strip(),
        done=task.done,
    )

    if row is None:
        return JSONResponse(
            status_code=404,
            content={"detail": "Task not found"},
        )

    return row_to_task(row)


# -----------------------------
# DELETE task
# -----------------------------

@app.delete("/tasks/{task_id}", status_code=204)
def remove_task(task_id: int):

    deleted = delete_task(task_id)

    if deleted == 0:
        return JSONResponse(
            status_code=404,
            content={"detail": "Task not found"},
        )

    return None