from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from fastapi import Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from repository import (
    initialize_database,
    get_all_tasks,
    get_task,
    create_task,
    update_task,
    delete_task,
)

from supabase_client import supabase


app = FastAPI(
    title="Task API",
    version="1.0",
)
security = HTTPBearer(auto_error=False)


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


class AuthRequest(BaseModel):
    email: str
    password: str


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

@app.get("/public/info")
def public_info():
    return {
        "message": "This is a public endpoint",
        "auth_required": False
    }

def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    if credentials is None:
        return JSONResponse(
            status_code=401,
            content={"error": "Access token required"}
        )

    token = credentials.credentials

    try:
        response = supabase.auth.get_user(token)

        if response.user is None:
            return JSONResponse(
                status_code=401,
                content={"error": "Invalid or expired token"}
            )

        return response.user

    except Exception:
        return JSONResponse(
            status_code=401,
            content={"error": "Invalid or expired token"}
        )
@app.get("/protected/profile")
def protected_profile(user=Depends(get_current_user)):
    return {
        "id": user.id,
        "email": user.email,
        "created_at": user.created_at
    }
@app.get("/protected/dashboard")
def protected_dashboard(user=Depends(get_current_user)):
    return {
        "message": "Welcome to your dashboard",
        "user_id": user.id,
        "email": user.email
    }
@app.post("/auth/logout", status_code=204)
def logout(user=Depends(get_current_user)):
    try:
        supabase.auth.sign_out()
    except Exception:
        pass

    return None
# ============================================================
# AUTHENTICATION
# ============================================================

# -----------------------------
# Signup
# -----------------------------

@app.post("/auth/signup", status_code=201)
def signup(data: AuthRequest):

    if not data.email or not data.password:
        return JSONResponse(
            status_code=400,
            content={
                "error": "Email and password are required"
            },
        )

    try:
        response = supabase.auth.sign_up({
            "email": data.email,
            "password": data.password,
        })

        return {
            "message": "Signup successful",
            "user_id": response.user.id if response.user else None,
            "email": response.user.email if response.user else data.email,
        }

    except Exception:
        return JSONResponse(
            status_code=400,
            content={
                "error": "Signup failed"
            },
        )


# -----------------------------
# Login
# -----------------------------

@app.post("/auth/login")
def login(data: AuthRequest):

    if not data.email or not data.password:
        return JSONResponse(
            status_code=400,
            content={
                "error": "Email and password are required"
            },
        )

    try:
        response = supabase.auth.sign_in_with_password({
            "email": data.email,
            "password": data.password,
        })

        return {
            "access_token": response.session.access_token,
            "refresh_token": response.session.refresh_token,
        }

    except Exception:
        return JSONResponse(
            status_code=401,
            content={
                "error": "Invalid login credentials"
            },
        )


# ============================================================
# TASK CRUD
# ============================================================

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
            content={
                "detail": "Task not found"
            },
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
            content={
                "detail": "Title cannot be empty"
            },
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
            content={
                "detail": "Title cannot be empty"
            },
        )

    row = update_task(
        task_id=task_id,
        title=task.title.strip(),
        done=task.done,
    )

    if row is None:
        return JSONResponse(
            status_code=404,
            content={
                "detail": "Task not found"
            },
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
            content={
                "detail": "Task not found"
            },
        )

    return None