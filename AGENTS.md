# AGENTS.md

Flask 2.3.3 task-manager web app. Python 3.13 (`.venv/`). UI and code comments are in Spanish — keep new user-facing strings in Spanish.

## Run / setup

- Run app: `python run.py` → http://localhost:8082 (`debug=True`, host `0.0.0.0`)
- Install deps: `pip install -r requirements.txt` (venv is `.venv/`)
- DB schema: `table.sql` (single table `tasks`)
- No tests, linter, CI, or git repo are configured.

## Config / environment gotchas

- `config.py` calls `load_dotenv()` — it reads **only `.env`**. DB credentials (MYSQL_*) are NOT in `.env`, so the app falls back to `localhost` / `root` / `task_manager` unless you add them.
- Live PythonAnywhere DB credentials are duplicated in `env` and `static/.env`, but neither file is loaded by the app. Don't rely on them; don't introduce new secret files.
- SMTP uses Gmail SSL on port 465 (`MAIL_USE_SSL=True`, `MAIL_USE_TLS=False`).

## Architecture

- App factory `create_app()` in `app/__init__.py`; entrypoint `run.py`.
- MVC-ish layout: `app/models/task.py` (raw SQL via `mysql-connector-python`, **no ORM/migrations**), `app/controllers/task_controller.py` (view functions + email side-effects), `app/templates/` (Jinja2).
- Routes are registered **inline in `create_app()`** with `app.route()` — no blueprints. New endpoints must be registered there.
- Any `Task.save()` also sends an email synchronously via `send_notification()` to a hardcoded Gmail address (`task_controller.py:8`).

## Domain invariants (easy to break)

- Task statuses are Spanish **MySQL ENUM** values and must be used verbatim: `creada`, `en proceso`, `en espera`, `cancelado`, `terminado`. They double as dict keys in `summary` (`task_controller.py:44`) and are matched in templates — changing a string breaks filtering/counts.
- Task IDs are generated manually as `TSK-{N:04d}` from `COUNT(*)` in `Task.save()` (`task.py:27`); not auto-increment and race-prone.
- `closed_at` is set only when status becomes `cancelado`/`terminado`.

## Frontend

- Tailwind v4 via CDN script in `app/templates/base.html` — no build step; the UI depends on the CDN.
- `base.html` links `css/custom.css`, but that file does **not** exist in `app/static/css/` → 404. Root `static/` is not served by Flask (static folder is `app/static`) and `static/custom.css` is an uncompiled Tailwind source file. `app/static/css/{input,output,styles}.css` are stale leftovers.
