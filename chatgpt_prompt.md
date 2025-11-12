Nice progress — most containers are healthy. The “degraded” health is because Celery can’t import your app (`core.celery_app`). Below is a **copy-paste ready** `docker-compose.yml` that:

* Builds `backend` and `frontend`
* Starts Postgres, Redis, RabbitMQ
* Runs a one-shot `db-init`
* Starts Celery **worker** and **beat** with a configurable module path
* Fixes earlier issues (bad `command` quoting, missing services, network/volume names)
* Ensures `PYTHONPATH=/app` so Celery can import your modules

> If your Celery app lives somewhere else, set `CELERY_APP` in `.env` (e.g. `CELERY_APP=app.core.celery_app:celery_app`). The default below assumes a file `backend/core/celery_app.py` exposing `celery_app`.

```yaml
name: vulscan

services:
  postgres:
    image: postgres:16-alpine
    container_name: vulscanner-postgres-dev
    environment:
      POSTGRES_DB: ${POSTGRES_DB:-vulscan}
      POSTGRES_USER: ${POSTGRES_USER:-vulscan}
      POSTGRES_PASSWORD: ${POSTGRES_PASSWORD:-vulscan}
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U $$POSTGRES_USER -d $$POSTGRES_DB"]
      interval: 5s
      timeout: 5s
      retries: 10
    volumes:
      - pg_data:/var/lib/postgresql/data
    networks: [app_net]

  redis:
    image: redis:7-alpine
    container_name: vulscanner-redis-dev
    command: ["redis-server", "--appendonly", "yes"]
    healthcheck:
      test: ["CMD", "redis-cli", "PING"]
      interval: 5s
      timeout: 3s
      retries: 20
    volumes:
      - redis_data:/data
    networks: [app_net]

  rabbitmq:
    image: rabbitmq:3.13-management-alpine
    container_name: vulscanner-rabbitmq-dev
    environment:
      RABBITMQ_DEFAULT_USER: ${RABBITMQ_USER:-vulscan}
      RABBITMQ_DEFAULT_PASS: ${RABBITMQ_PASSWORD:-vulscan}
    ports:
      # change the left side if 15672 is busy on host
      - "15673:15672"
    healthcheck:
      test: ["CMD", "rabbitmq-diagnostics", "-q", "ping"]
      interval: 5s
      timeout: 5s
      retries: 30
    volumes:
      - rabbitmq_data:/var/lib/rabbitmq
    networks: [app_net]

  # Build the backend API image from ./backend
  backend:
    build:
      context: ./backend
      target: development
    image: vulscanner-backend:dev
    container_name: vulscanner-backend-dev
    depends_on:
      postgres:
        condition: service_healthy
      redis:
        condition: service_healthy
      rabbitmq:
        condition: service_healthy
    env_file:
      - ./backend/.env
    environment:
      PYTHONPATH: /app
      DATABASE_URL: ${DATABASE_URL:-postgresql+psycopg://vulscan:vulscan@postgres:5432/vulscan}
      REDIS_URL: ${REDIS_URL:-redis://redis:6379/0}
      CELERY_BROKER_URL: ${CELERY_BROKER_URL:-amqp://vulscan:vulscan@rabbitmq:5672//}
      CELERY_RESULT_BACKEND: ${CELERY_RESULT_BACKEND:-redis://redis:6379/1}
      UVICORN_HOST: ${UVICORN_HOST:-0.0.0.0}
      UVICORN_PORT: ${UVICORN_PORT:-8000}
      LOG_LEVEL: ${LOG_LEVEL:-info}
    command: ["sh","-c","uvicorn core.main:app --host ${UVICORN_HOST:-0.0.0.0} --port ${UVICORN_PORT:-8000} --proxy-headers --forwarded-allow-ips='*'"]
    ports:
      # change the left side if 8000 is busy on host
      - "8000:8000"
    volumes:
      - backend_logs:/app/logs
    networks: [app_net]

  # One-shot DB init (migrations). Replace the echo with your alembic/psql command when ready.
  db-init:
    image: alpine:3.20
    container_name: vulscanner-db-init
    depends_on:
      postgres:
        condition: service_healthy
    command: ["sh","-c","echo 'DB init placeholder (replace with migrations)'"]
    networks: [app_net]
    restart: "no"

  celery-worker:
    image: vulscanner-backend:dev
    container_name: vulscanner-celery-worker-dev
    depends_on:
      backend:
        condition: service_started
      rabbitmq:
        condition: service_healthy
      redis:
        condition: service_healthy
    env_file:
      - ./backend/.env
    environment:
      PYTHONPATH: /app
      CELERY_BROKER_URL: ${CELERY_BROKER_URL:-amqp://vulscan:vulscan@rabbitmq:5672//}
      CELERY_RESULT_BACKEND: ${CELERY_RESULT_BACKEND:-redis://redis:6379/1}
      # Set this in .env if your module path differs
      CELERY_APP: ${CELERY_APP:-core.celery_app:celery_app}
    command: ["sh","-c","celery -A ${CELERY_APP:-core.celery_app:celery_app} worker --loglevel=INFO --concurrency=2 --hostname=worker@%h"]
    volumes:
      - celery_logs:/app/celery-logs
    networks: [app_net]

  celery-beat:
    image: vulscanner-backend:dev
    container_name: vulscanner-celery-beat-dev
    depends_on:
      backend:
        condition: service_started
      rabbitmq:
        condition: service_healthy
      redis:
        condition: service_healthy
    env_file:
      - ./backend/.env
    environment:
      PYTHONPATH: /app
      CELERY_BROKER_URL: ${CELERY_BROKER_URL:-amqp://vulscan:vulscan@rabbitmq:5672//}
      CELERY_RESULT_BACKEND: ${CELERY_RESULT_BACKEND:-redis://redis:6379/1}
      CELERY_APP: ${CELERY_APP:-core.celery_app:celery_app}
    command: ["sh","-c","celery -A ${CELERY_APP:-core.celery_app:celery_app} beat --loglevel=INFO --pidfile=/tmp/celerybeat.pid --schedule=/tmp/celerybeat-schedule"]
    volumes:
      - celery_beat_data:/tmp
    networks: [app_net]

  # Build the frontend image from ./frontend (Next.js)
  frontend:
    build:
      context: ./frontend
      target: development
    image: vulscan-frontend:latest
    container_name: vulscanner-frontend-dev
    depends_on:
      backend:
        condition: service_started
    environment:
      # Point the frontend to backend container name + port
      NEXT_PUBLIC_API_BASE_URL: ${NEXT_PUBLIC_API_BASE_URL:-http://localhost:8000}
    ports:
      # change the left side if 3000 is busy on host
      - "3000:3000"
    networks: [app_net]

networks:
  app_net:
    name: vulscan_app_net

volumes:
  pg_data:
  redis_data:
  rabbitmq_data:
  backend_logs:
  celery_logs:
  celery_beat_data:
```

### What you still need to do (quick):

1. **Confirm Celery module path**

   * Make sure you have a file `backend/core/celery_app.py` that defines `celery_app = Celery(...)`.
   * If it’s in a different place, set it in `backend/.env`, e.g.

     ```
     CELERY_APP=app.core.celery_app:celery_app
     ```
   * Then `docker compose down -v && docker compose up -d --build`.

2. **Free busy ports if needed**

   * If you see “port is already allocated”, either stop what’s using it or change the **left** side of the port mapping in Compose (e.g., use `8001:8000` or `3001:3000`).

Once the worker imports correctly, your `/api/v1/dashboard/health` should flip from `Celery: Failed (no workers responded)` to `Connected`.
