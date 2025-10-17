# Project Management API (FastAPI)

Backend-only project management API built with FastAPI, async SQLAlchemy, PostgreSQL, JWT auth, and RBAC. Includes tests, CI, and containerized deploy.

## Features
- Users: register/login, JWT auth (access/refresh)
- Projects with memberships and roles: owner, admin, member, viewer
- Tasks with subtasks, tags, comments, attachments, sprints
- Activity log and WebSocket notifications
- Async-first, structured logging, error handlers

## Quickstart (Local Docker)
1. Copy env: `cp .env.example .env` and adjust values.
2. Start services: `docker compose -f infra/docker-compose.yml up --build`
3. API runs on http://localhost:8080 (Docs: http://localhost:8080/docs)

## Quickstart (Local Python)
- Python 3.12 recommended
- Install deps: `pip install -r requirements.txt`
- Create DB and set `DATABASE_URL` in `.env` or env vars
- Run migrations: `alembic -c app/db/migrations/alembic.ini upgrade head`
- Start server: `uvicorn app.main:app --reload`

## Testing
- `pytest -q`
- Tests use an in-memory SQLite DB via dependency override by default.

## Scripts (PowerShell)
- `scripts/dev_up.ps1` - run docker compose (dev)
- `scripts/format.ps1` - format via ruff+black
- `scripts/load_env.ps1` - load `.env` into current shell

## CI/CD
- GitHub Actions: lint, tests, image build
- CD workflow placeholder for Fly.io/ECS; add secrets and commands per platform

## Deployment
- Dockerfile (multi-stage)
- Fly.io config sample at `infra/fly.toml`

## Notes
- Real file storage for attachments is pluggable; current implementation stores files locally under `uploads/`.
- For production, configure object storage (S3 compatible) and update `services/notifications.py` or storage layer accordingly.
