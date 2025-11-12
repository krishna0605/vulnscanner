# Enhanced Vulnerability Scanner - Backend Makefile
# Database migration and management commands

.PHONY: help install dev test lint format clean
.PHONY: db-status db-upgrade db-downgrade db-history db-create db-reset db-seed db-check
.PHONY: db-backup db-restore db-cleanup db-export db-validate db-repair db-analyze
.PHONY: run run-dev run-prod stop logs

# Default target
help:
	@echo "Enhanced Vulnerability Scanner - Backend Commands"
	@echo ""
	@echo "Development:"
	@echo "  install     Install dependencies"
	@echo "  dev         Run development server"
	@echo "  test        Run tests"
	@echo "  lint        Run linting"
	@echo "  format      Format code"
	@echo "  clean       Clean temporary files"
	@echo ""
	@echo "Database Migration:"
	@echo "  db-status   Show migration status"
	@echo "  db-upgrade  Upgrade to latest migration"
	@echo "  db-downgrade Downgrade one migration"
	@echo "  db-history  Show migration history"
	@echo "  db-create   Create new migration"
	@echo "  db-reset    Reset database (dev only)"
	@echo "  db-seed     Seed with test data"
	@echo "  db-check    Check database connectivity"
	@echo ""
	@echo "Database Backup:"
	@echo "  db-backup   Create database backup"
	@echo "  db-restore  Restore from backup"
	@echo "  db-cleanup  Cleanup old backups"
	@echo "  db-export   Export data to JSON/CSV"
	@echo ""
	@echo "Database Validation:"
	@echo "  db-validate Check data integrity"
	@echo "  db-repair   Repair database issues"
	@echo "  db-analyze  Analyze database statistics"
	@echo ""
	@echo "Server Management:"
	@echo "  run         Run production server"
	@echo "  run-dev     Run development server"
	@echo "  stop        Stop running servers"
	@echo "  logs        Show server logs"

# Development commands
install:
	pip install -r requirements.txt

# Testing commands
test:
	python -m pytest

test-unit:
	python -m pytest -m unit

test-integration:
	python -m pytest -m integration

test-coverage:
	python -m pytest --cov=. --cov-report=term-missing --cov-report=html:htmlcov --cov-report=xml:coverage.xml --cov-fail-under=80

test-parallel:
	python -m pytest -n auto

test-slow:
	python -m pytest -m slow

coverage-report:
	python -m coverage html
	@echo "Coverage report generated at htmlcov/index.html"

coverage-xml:
	python -m coverage xml
	pip install -e .

dev:
	python -m uvicorn main:app --reload --host 0.0.0.0 --port 8000

test:
	pytest tests/ -v --cov=. --cov-report=html

lint:
	ruff check .
	mypy .

format:
	black .
	isort .
	ruff format .

clean:
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -delete
	find . -type d -name "*.egg-info" -exec rm -rf {} +
	rm -rf .coverage htmlcov/ .pytest_cache/

# Database migration commands
db-status:
	python scripts/migrate.py status

db-upgrade:
	python scripts/migrate.py upgrade

db-downgrade:
	python scripts/migrate.py downgrade

db-history:
	python scripts/migrate.py history

db-create:
	@read -p "Migration name: " name; \
	python scripts/migrate.py create "$$name" --autogenerate

db-reset:
	python scripts/migrate.py reset

db-seed:
	python scripts/migrate.py seed

db-check:
	python scripts/migrate.py check

# Database backup commands
db-backup:
	python scripts/backup.py create

db-backup-named:
	@read -p "Backup name: " name; \
	python scripts/backup.py create --name "$$name"

db-restore:
	@echo "Available backups:"; \
	python scripts/backup.py list; \
	echo ""; \
	read -p "Backup name to restore: " name; \
	python scripts/backup.py restore "$$name"

db-list-backups:
	python scripts/backup.py list

db-cleanup:
	python scripts/backup.py cleanup

db-export-json:
	python scripts/backup.py export json

db-export-csv:
	python scripts/backup.py export csv

# Database validation commands
db-validate:
	python scripts/validate_schema.py check
	python scripts/validate_schema.py validate

db-repair:
	python scripts/validate_schema.py repair

db-analyze:
	python scripts/validate_schema.py analyze

# Server management
run:
	python -m uvicorn main:app --host 0.0.0.0 --port 8000

run-dev:
	python -m uvicorn main:app --reload --host 0.0.0.0 --port 8000

run-prod:
	python -m gunicorn main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000

stop:
	pkill -f "uvicorn main:app" || true
	pkill -f "gunicorn main:app" || true

logs:
	tail -f logs/app.log

# Docker commands
docker-build:
	docker build -t vulnscan-backend .

docker-run:
	docker run -p 8000:8000 -v $(PWD):/app vulnscan-backend

docker-dev:
	docker-compose up -d

docker-stop:
	docker-compose down

# Testing commands
test-unit:
	pytest tests/unit/ -v

test-integration:
	pytest tests/integration/ -v

test-api:
	pytest tests/api/ -v

test-coverage:
	pytest --cov=. --cov-report=html --cov-report=term

# Alembic direct commands (for advanced usage)
alembic-current:
	python -m alembic current

alembic-upgrade:
	python -m alembic upgrade head

alembic-downgrade:
	python -m alembic downgrade -1

alembic-history:
	python -m alembic history --verbose

alembic-revision:
	@read -p "Migration message: " msg; \
	python -m alembic revision --autogenerate -m "$$msg"

# Environment setup
setup-dev:
	cp .env.example .env
	make install
	make db-upgrade
	make db-seed
	@echo "Development environment setup complete!"

setup-prod:
	make install
	make db-upgrade
	@echo "Production environment setup complete!"

# Health checks
health:
	curl -f http://localhost:8000/api/v1/health || exit 1

health-detailed:
	curl -s http://localhost:8000/api/v1/health | python -m json.tool

# Security checks
security-check:
	bandit -r . -f json -o security-report.json
	safety check

# Performance testing
perf-test:
	locust -f tests/performance/locustfile.py --host=http://localhost:8000

# Celery tasks
.PHONY: worker beat queues

worker:
	celery -A tasks.celery_app worker --loglevel=info --concurrency=2

beat:
	celery -A tasks.celery_app beat --loglevel=info

# Optional: requires redis-cli installed and accessible
queues:
	redis-cli -n 1 keys "*" || echo "redis-cli not found or Redis not accessible; skipping"