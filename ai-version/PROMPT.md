# Stage 7 — AI rematch prompt

Use this as the prompt for a separate AI-generated version. Do not replace the hand-built `main.py` with AI output.

Build a small to-do Task API using Python and FastAPI.

Requirements:
- Store tasks only in memory in a Python list. Do not use a database or files.
- Start with three example tasks. Every task has `id`, `title`, and `done`.
- Add `GET /` returning API name, version, and the `/tasks` endpoint.
- Add `GET /health` returning `{"status": "ok"}`.
- Add `GET /tasks` to list all tasks.
- Add `GET /tasks/{id}` to return one task. Unknown IDs must return 404 with a JSON error.
- Add `POST /tasks`. Accept a title, generate the next ID, set `done` to false, and return 201.
- Reject a missing or empty title.
- Add `PUT /tasks/{id}` to update title and/or done. Unknown IDs return 404. Empty/invalid update bodies return 400.
- Add `DELETE /tasks/{id}`. Successful deletion returns 204 with no body. Unknown IDs return 404.
- The API must expose Swagger UI at `/docs`.
- Add clear endpoint descriptions.
- Include a requirements file and simple run instructions.

After generating the code, test the CRUD flow and compare the result with the hand-built version.
