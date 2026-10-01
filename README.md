# W3 · A2 — Connecting Your CRUD to SQLite

A Week 3 continuation of the FlyRank Backend Track CRUD API.

The Week 2 API used an in-memory list. This version keeps the same CRUD endpoints and moves the storage layer to a real **SQLite** database. The database is stored in `tasks.db` and is created automatically when the application starts.

## Architecture

```text
Client → FastAPI API → SQLite (tasks.db)
```

The API contract stays the same. Only the storage layer changes.

## Requirements

- Python 3.10+
- FastAPI
- Uvicorn
- SQLite (provided by Python's standard library)
- Optional: DB Browser for SQLite for Stage 4

No separate database server is required.

## Install

From the project folder:

```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
```

## Run

```powershell
python -m uvicorn main:app --reload
```

Open Swagger UI:

```text
http://localhost:8000/docs
```

The first startup automatically:

1. Creates `tasks.db` if it does not exist.
2. Creates the `tasks` table if it does not exist.
3. Inserts three example tasks only when the table is empty.

## Database schema

```sql
CREATE TABLE tasks (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL,
    done INTEGER NOT NULL DEFAULT 0
);
```

SQLite stores boolean values as `0` and `1`; the API converts them back to JSON `false` and `true`.

## Endpoints

| Method | Endpoint | Purpose | Success |
|---|---|---|---|
| GET | `/` | API information | 200 |
| GET | `/health` | Health check | 200 |
| GET | `/tasks` | List all tasks | 200 |
| GET | `/tasks/{id}` | Get one task | 200 |
| POST | `/tasks` | Create a task | 201 |
| PUT | `/tasks/{id}` | Update a task | 200 |
| DELETE | `/tasks/{id}` | Delete a task | 204 |

### Error behavior

- Missing/empty title → `400`
- Empty PUT body → `400`
- Unknown task ID → `404`
- Successful delete → `204 No Content`

## Curl tests

### Read

```powershell
curl.exe -i http://localhost:8000/tasks
```

```powershell
curl.exe -i http://localhost:8000/tasks/1
```

Unknown ID:

```powershell
curl.exe -i http://localhost:8000/tasks/999
```

Expected:

```text
404 Not Found
```

### Create

```powershell
curl.exe -i -X POST http://localhost:8000/tasks `
  -H "Content-Type: application/json" `
  -d '{"title":"Buy milk"}'
```

Expected:

```text
201 Created
```

### Invalid create

```powershell
curl.exe -i -X POST http://localhost:8000/tasks `
  -H "Content-Type: application/json" `
  -d '{}'
```

Expected:

```text
400 Bad Request
```

### Update

```powershell
curl.exe -i -X PUT http://localhost:8000/tasks/1 `
  -H "Content-Type: application/json" `
  -d '{"title":"Learn SQLite","done":true}'
```

Expected:

```text
200 OK
```

### Delete

```powershell
curl.exe -i -X DELETE http://localhost:8000/tasks/1
```

Expected:

```text
204 No Content
```

## Persistence test

This is the key Week 3 test.

1. Start the API.
2. Create a new task.
3. Run `GET /tasks`.
4. Stop the server with `Ctrl+C`.
5. Start it again with the same command.
6. Run `GET /tasks` again.

The created task should still exist because it is stored in `tasks.db`.

The three seed tasks should **not** multiply after restarts.

## Stage 4 — SQL tested by hand

Open `tasks.db` in DB Browser for SQLite and use the **Execute SQL** tab.

### List every task

```sql
SELECT * FROM tasks;
```

### Completed tasks

```sql
SELECT * FROM tasks WHERE done = 1;
```

### Count tasks

```sql
SELECT COUNT(*) FROM tasks;
```

### Mark all tasks complete

```sql
UPDATE tasks SET done = 1;
```

### Delete completed tasks

```sql
DELETE FROM tasks WHERE done = 1;
```

After changing data in DB Browser, call:

```powershell
curl.exe -i http://localhost:8000/tasks
```

The API should immediately show the database changes.

### Example SQL query used

```sql
SELECT * FROM tasks WHERE done = 1;
```

This returns only tasks whose `done` value is `1`.

## Why SQLite?

SQLite is suitable for this assignment because it is a lightweight database stored in one file, requires no separate database server, and provides persistence across application restarts.

## Where is the database?

The application creates:

```text
tasks.db
```

in the project directory automatically.

`tasks.db` is included in `.gitignore` so every fresh clone creates its own local database and seed data.

## DB Browser screenshot

The assignment requires a screenshot showing `tasks.db` open in DB Browser for SQLite.

After opening the database and showing the `tasks` table, save the screenshot as:

```text
docs/db-browser-screenshot.png
```

Then this section can be updated with:

```markdown
![SQLite database in DB Browser](docs/db-browser-screenshot.png)
```

## Git commit plan

The assignment asks for one meaningful commit per stage:

```text
Stage 0: create SQLite database
Stage 1: database read endpoints
Stage 2: insert into database
Stage 3: update and delete with SQL
Stage 4: explored SQLite
Stage 5: database documentation
```

## Stage 6 — AI rematch

The optional AI stage belongs in a separate `ai-version/` folder or branch. See `ai-version/PROMPT.md`.

Do not replace the hand-built database version with AI-generated code.

## Final checklist

- [ ] Same CRUD endpoints as A1
- [ ] SQLite `tasks.db`
- [ ] Automatic database creation
- [ ] Automatic `tasks` table creation
- [ ] Three seeds only when the table is empty
- [ ] Parameterized SQL queries
- [ ] 200 / 201 / 204 / 400 / 404 behavior
- [ ] Data survives restart
- [ ] SQL queries tested in DB Browser
- [ ] DB Browser screenshot added
- [ ] Public GitHub repo updated
- [ ] Six meaningful stage commits
