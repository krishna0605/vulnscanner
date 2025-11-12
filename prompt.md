You are a senior backend engineer. Continue updating my Enhanced Vulnerability Scanner project to finalize PostgreSQL integration and smoke tests. Apply minimal changes, respect existing structure, and return unified diffs for each changed/created file plus the exact commands to run migrations and smoke-test.

Context / Constraints (must follow)

Stack: FastAPI + SQLAlchemy 2.0 (async runtime), Alembic (sync engine for migrations).

Repo layout (keep paths):

backend/core/config.py (Pydantic v2 settings)

backend/db/session.py (async engine & session)

backend/db/base.py (import all models; exposes metadata)

backend/models/scan_job.py (already exists)

backend/schemas/scan_job.py (added in previous step)

backend/api/v1/endpoints/scan_jobs.py (exists)

backend/api/v1/endpoints/health.py (create if missing)

backend/main.py (include routers)

backend/alembic/* (env.py already normalizes drivers; no new migration unless strictly required)

backend/requirements.txt (already updated to psycopg[binary] and asyncpg)

README.md, .env.example, Makefile (append non-breaking updates)

Postgres target (local):

HOST: localhost

PORT: 5433

USER: krishna

PASSWORD: Krishna@2003 (use examples only, never hardcode)

DB: vulscanner

Connection strings:

Async (runtime): postgresql+asyncpg://krishna:<PW>@localhost:5433/vulscanner

Sync (alembic): postgresql+psycopg://krishna:<PW>@localhost:5433/vulscanner

If API runs in Docker but DB stays on host: replace host with host.docker.internal in both URLs.

Do not change docker-compose services. Only document env overrides.

Deliverables
1) Settings

File: backend/core/config.py

Pydantic v2 BaseSettings reading:

DATABASE_URL_ASYNC and DATABASE_URL_SYNC

Optional USE_HOST_DOCKER_INTERNAL (bool, default False)

Expose settings.database_url_async / settings.database_url_sync.

Helper: get_runtime_db_url() returns async URL; if USE_HOST_DOCKER_INTERNAL is true and host is localhost, swap to host.docker.internal.

No secrets hardcoded.

2) Async engine & session

File: backend/db/session.py

Create async engine using SQLAlchemy 2.0 with postgresql+asyncpg:

pool: pool_size=10, max_overflow=20, pool_pre_ping=True, echo=False

Provide async_sessionmaker and FastAPI dependency:

async def get_async_session() -> AsyncIterator[AsyncSession]: ...


On startup/shutdown (via main.py), ensure engine is created once and disposed gracefully.

3) Base metadata aggregator

File: backend/db/base.py

Ensure it imports backend/models/scan_job.py and exposes:

from sqlalchemy.orm import DeclarativeBase
class Base(DeclarativeBase): pass
metadata = Base.metadata


If already present, just confirm scan_job import so Alembic autogenerate sees it.

4) Health endpoint

File: backend/api/v1/endpoints/health.py (create if missing)

Route: GET /api/v1/db/health

Use get_async_session and run:

SELECT version() AS version, current_database() AS db, inet_server_port() AS port;


Return JSON: { "ok": true, "info": { "version": "...", "db": "...", "port": <int> } }

Production-friendly error handling → respond {"ok": false, "error": "..."} with 500 on exceptions.

5) Wire routers

File: backend/main.py

Include both:

api.v1.endpoints.health (as v1_health_router)

api.v1.endpoints.scan_jobs (already added)

Add startup/shutdown events (or lifespan) to create/dispose engine (import from db.session).

6) Service stub (if missing)

File: backend/services/scan_job_service.py

Implement:

async def create_scan_job(session: AsyncSession, url: str) -> models.ScanJob:
    # insert ScanJob(url=url) with default status 'queued', return the ORM object

7) .env examples

File: .env.example
Append the two URLs (no secrets) and the Docker-host variants. Show URL-encoded password example for Krishna@2003 (Krishna%402003).

DATABASE_URL_ASYNC=postgresql+asyncpg://krishna:<YOUR_PASSWORD>@localhost:5433/vulscanner
DATABASE_URL_SYNC=postgresql+psycopg://krishna:<YOUR_PASSWORD>@localhost:5433/vulscanner
# If backend runs in Docker but DB is on host:
# DATABASE_URL_ASYNC=postgresql+asyncpg://krishna:<YOUR_PASSWORD>@host.docker.internal:5433/vulscanner
# DATABASE_URL_SYNC=postgresql+psycopg://krishna:<YOUR_PASSWORD>@host.docker.internal:5433/vulscanner
# USE_HOST_DOCKER_INTERNAL=true
# Example URL-encoding for '@': Krishna@2003 -> Krishna%402003

8) Makefile

File: Makefile (or backend/Makefile if that’s where DB targets live) – add non-breaking targets (keep existing ones):

db-rev:    ## alembic revision --autogenerate
	@cd backend && python -m alembic revision --autogenerate -m "$(m)"

db-upgrade: ## alembic upgrade head
	@cd backend && python -m alembic upgrade head

db-downgrade: ## alembic downgrade -1
	@cd backend && python -m alembic downgrade -1

9) README

File: README.md – append a “Connecting to Local PostgreSQL” block:

Env examples (localhost vs host.docker.internal)

Run steps (Windows + Bash):

install deps

set DATABASE_URL_SYNC

cd backend && python -m alembic upgrade head

uvicorn main:app --reload --port 8000

smoke test curl/Invoke-RestMethod for /api/v1/db/health and POST /api/v1/scan-jobs

Troubleshooting:

password auth failed → check role/port 5433 & URL-encoding (@ → %40)

Alembic URL mismatch (async vs sync)

Docker host connectivity note

Output format (strict)

Unified diffs for every created/changed file:

backend/core/config.py

backend/db/session.py

backend/db/base.py

backend/api/v1/endpoints/health.py (if created)

backend/services/scan_job_service.py (if created)

backend/main.py

.env.example (appended)

Makefile (or backend/Makefile)

README.md (appended)

Exact commands to run locally (Bash and PowerShell), including URL-encoded password examples:

set DATABASE_URL_SYNC and DATABASE_URL_ASYNC

run migrations

start API

smoke test both endpoints

No placeholders except <YOUR_PASSWORD> in .env.example. Never hardcode secrets in code.

Acceptance criteria

Alembic migrations run with postgresql+psycopg.

Runtime async engine uses postgresql+asyncpg.

/api/v1/db/health returns version, db, port.

POST /api/v1/scan-jobs creates and returns a row.

Swapping localhost ↔ host.docker.internal works by env only.