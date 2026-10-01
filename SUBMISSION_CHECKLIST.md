# W3 A2 Final Submission Checklist

1. Run `python -m uvicorn main:app --reload`.
2. Open `http://localhost:8000/docs`.
3. Confirm the `tasks.db` file is created automatically.
4. Confirm the `tasks` table exists.
5. Confirm exactly three seeds appear on the first run.
6. Restart the server and confirm the seeds do not duplicate.
7. Create a task and restart the server; confirm the task remains.
8. Test GET, POST, PUT, DELETE and the 400/404 cases.
9. Open `tasks.db` in DB Browser for SQLite.
10. Run the required Stage 4 SQL queries.
11. Take a DB Browser screenshot and save it as `docs/db-browser-screenshot.png`.
12. Update README with the screenshot.
13. Commit each stage.
14. Push to the same public GitHub repository used for A1.
