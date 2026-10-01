# W2 · A1 — Build Your First CRUD API

A beginner-friendly **Task CRUD API** built with **Python + FastAPI** for the FlyRank Backend Track Week 2 assignment.

## What this project contains

- FastAPI server running on `localhost:8000`
- In-memory task storage — no database and no files
- Full CRUD:
  - `GET /tasks`
  - `GET /tasks/{id}`
  - `POST /tasks`
  - `PUT /tasks/{id}`
  - `DELETE /tasks/{id}`
- Root endpoint: `GET /`
- Health endpoint: `GET /health`
- Automatic Swagger UI at `/docs`
- Input validation and appropriate HTTP status codes

The assignment specifically requires in-memory storage and says data loss after a server restart is expected at this stage.

## Project structure

```text
W2_CRUD_API_Final_Submission/
├── main.py
├── requirements.txt
├── README.md
├── .gitignore
└── ai-version/
    └── PROMPT.md
```

## 1. Install

Create and activate a virtual environment:

### Windows PowerShell

```powershell
python -m venv venv
.env\Scripts\Activate.ps1
```

Install dependencies:

```powershell
pip install -r requirements.txt
```

## 2. Run

Start the server:

```powershell
uvicorn main:app --reload
```

Open:

- API: http://localhost:8000
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## 3. Endpoints

| Method | Endpoint | Purpose | Success |
|---|---|---|---|
| GET | `/` | API information | 200 |
| GET | `/health` | Health check | 200 |
| GET | `/tasks` | List all tasks | 200 |
| GET | `/tasks/{id}` | Get one task | 200 |
| POST | `/tasks` | Create task | 201 |
| PUT | `/tasks/{id}` | Update task | 200 |
| DELETE | `/tasks/{id}` | Delete task | 204 |

### Error handling

- Invalid/empty title → `400`
- Unknown task ID → `404`
- Successful delete → `204 No Content`

## 4. Test with curl

### List tasks

```powershell
curl.exe -i http://localhost:8000/tasks
```

Expected status:

```text
HTTP/1.1 200 OK
```

### Get one task

```powershell
curl.exe -i http://localhost:8000/tasks/1
```

### Unknown task

```powershell
curl.exe -i http://localhost:8000/tasks/99
```

Expected:

```text
HTTP/1.1 404 Not Found
```

### Create

```powershell
curl.exe -i -X POST http://localhost:8000/tasks `
  -H "Content-Type: application/json" `
  -d '{"title":"Buy milk"}'
```

Expected status:

```text
HTTP/1.1 201 Created
```

### Invalid create

```powershell
curl.exe -i -X POST http://localhost:8000/tasks `
  -H "Content-Type: application/json" `
  -d '{}'
```

Expected status:

```text
HTTP/1.1 400 Bad Request
```

The project includes a FastAPI validation exception handler so invalid request bodies use the assignment's required `400` status code.

### Update

```powershell
curl.exe -i -X PUT http://localhost:8000/tasks/1 `
  -H "Content-Type: application/json" `
  -d '{"title":"Learn FastAPI properly","done":true}'
```

Expected status:

```text
HTTP/1.1 200 OK
```

### Delete

```powershell
curl.exe -i -X DELETE http://localhost:8000/tasks/1
```

Expected status:

```text
HTTP/1.1 204 No Content
```

## 5. Swagger UI

Open:

```text
http://localhost:8000/docs
```

Use **Try it out** to perform the complete CRUD cycle:

1. Create a task.
2. List tasks.
3. Get the created task.
4. Update the task.
5. Delete the task.
6. Confirm the final task list.

### Screenshot

Add your actual Swagger UI screenshot here before submitting to GitHub:

```text
docs/swagger-screenshot.png
```

Recommended README image:

```markdown
![Swagger UI](docs/swagger-screenshot.png)
```

## 6. In-memory data experiment

The tasks are stored only in the Python `tasks` list.

If the server is restarted, newly created tasks disappear and the original three seed tasks return.

This is intentional for Week 2: the assignment asks for in-memory storage and introduces databases in a later week.

## 7. GitHub submission checklist

Before submitting:

- [ ] Public GitHub repository
- [ ] At least 6 meaningful commits
- [ ] Stage 0 commit
- [ ] Stage 1 commit
- [ ] Stage 2 commit
- [ ] Stage 3 commit
- [ ] Stage 4 commit
- [ ] Stage 5 commit
- [ ] Stage 6 commit
- [ ] README included
- [ ] Swagger screenshot added
- [ ] CRUD tested with curl
- [ ] CRUD tested through Swagger UI

Suggested commit messages:

```text
Stage 0: hello server
Stage 1: root and health endpoints
Stage 2: read endpoints with 404
Stage 3: create with validation
Stage 4: full CRUD
Stage 5: Swagger UI
Stage 6: publish and docs
```

## 8. Optional Stage 7 — AI vs me

The assignment's bonus stage asks you to create an AI version in a separate folder/branch, run it, compare it with your hand-built version, and document at least three concrete differences.

See `ai-version/PROMPT.md` for a starting prompt. Keep the hand-built submission untouched.

## Assignment reference

This project follows the uploaded FlyRank W2 · A1 assignment: build a small to-do API, use CRUD endpoints, test through Swagger UI, and publish the work to GitHub. The assignment requires a public repository, at least six meaningful commits, and a README with run instructions, an endpoint table, a curl output, and a Swagger screenshot.
