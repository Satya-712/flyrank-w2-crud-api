# W3 A2 — AI Rematch Prompt

Build a Python FastAPI version of an existing CRUD Task API by replacing its in-memory storage with SQLite.

Use Python's built-in sqlite3 library.

Requirements:
- Keep the same API endpoints and request/response behavior:
  GET /tasks
  GET /tasks/{id}
  POST /tasks
  PUT /tasks/{id}
  DELETE /tasks/{id}
- Also keep GET / and GET /health.
- Use a SQLite database file named tasks.db.
- Create the database automatically if it is missing.
- Create a tasks table automatically if it is missing.
- The table must have id as an integer primary key, title as text, and done as a boolean-like integer.
- Insert exactly three example tasks only when the table is empty.
- Restarting the application must not duplicate the seed tasks.
- GET routes must use SELECT queries.
- POST must use INSERT.
- PUT must use UPDATE.
- DELETE must use DELETE.
- Use parameterized SQL placeholders for all user-supplied values. Never concatenate user input into SQL.
- Preserve the status-code behavior: 200 for reads/updates, 201 for create, 204 for delete, 400 for invalid request bodies, and 404 for unknown IDs.
- Keep FastAPI Swagger UI available at /docs.
- Include requirements.txt and a README explaining how to run the project and prove persistence.

Generate the code in a separate ai-version folder so the hand-built version remains untouched.
