# Enhanced Vulnerability Scanner - Makefile
# Comprehensive build, test, and deployment automation

.PHONY: help install install-dev test test-unit test-integration test-e2e test-performance
.PHONY: lint format type-check security-check coverage
.PHONY: build build-backend build-frontend build-all
.PHONY: run run-dev run-prod stop clean
.PHONY: deploy deploy-staging deploy-prod rollback
.PHONY: docker-build docker-push docker-clean
.PHONY: k8s-deploy k8s-delete k8s-logs
.PHONY: db-rev db-migrate db-upgrade db-downgrade db-reset db-seed
.PHONY: monitoring-up monitoring-down logs
.PHONY: backup restore health-check

# Configuration
PROJECT_NAME := vulscanner
BACKEND_DIR := backend
FRONTEND_DIR := frontend
DOCKER_REGISTRY := your-registry.com
VERSION := $(shell git describe --tags --always --dirty)
ENVIRONMENT := development

# Colors for output
RED := \033[0;31m
GREEN := \033[0;32m
YELLOW := \033[1;33m
BLUE := \033[0;34m
NC := \033[0m # No Color

# Default target
help: ## Show this help message
	@echo "$(BLUE)Enhanced Vulnerability Scanner - Available Commands$(NC)"
	@echo ""
	@awk 'BEGIN {FS = ":.*?## "} /^[a-zA-Z_-]+:.*?## / {printf "$(GREEN)%-20s$(NC) %s\n", $$1, $$2}' $(MAKEFILE_LIST)
	@echo ""
	@echo "$(YELLOW)Examples:$(NC)"
	@echo "  make install-dev     # Install development dependencies"
	@echo "  make test           # Run all tests"
	@echo "  make run-dev        # Start development environment"
	@echo "  make deploy-staging # Deploy to staging"

# Installation targets
install: ## Install production dependencies
	@echo "$(BLUE)Installing production dependencies...$(NC)"
	cd $(BACKEND_DIR) && pip install -r requirements.txt
	cd $(FRONTEND_DIR) && npm ci --only=production

install-dev: ## Install development dependencies
	@echo "$(BLUE)Installing development dependencies...$(NC)"
	cd $(BACKEND_DIR) && pip install -r requirements-dev.txt
	cd $(FRONTEND_DIR) && npm ci
	pre-commit install

# Testing targets
test: test-unit test-integration ## Run all tests
	@echo "$(GREEN)All tests completed!$(NC)"

test-unit: ## Run unit tests
	@echo "$(BLUE)Running unit tests...$(NC)"
	cd $(BACKEND_DIR) && python -m pytest tests/unit/ -v --tb=short
	cd $(FRONTEND_DIR) && npm run test:unit

test-integration: ## Run integration tests
	@echo "$(BLUE)Running integration tests...$(NC)"
	cd $(BACKEND_DIR) && python -m pytest tests/integration/ -v --tb=short
	cd $(FRONTEND_DIR) && npm run test:integration

test-e2e: ## Run end-to-end tests
	@echo "$(BLUE)Running E2E tests...$(NC)"
	cd $(FRONTEND_DIR) && npm run test:e2e

test-performance: ## Run performance tests
	@echo "$(BLUE)Running performance tests...$(NC)"
	cd $(BACKEND_DIR) && python -m pytest tests/test_performance.py -v --benchmark-only

# Code quality targets
lint: ## Run linters
	@echo "$(BLUE)Running linters...$(NC)"
	cd $(BACKEND_DIR) && ruff check .
	cd $(BACKEND_DIR) && flake8 .
	cd $(FRONTEND_DIR) && npm run lint

format: ## Format code
	@echo "$(BLUE)Formatting code...$(NC)"
	cd $(BACKEND_DIR) && black .
	cd $(BACKEND_DIR) && isort .
	cd $(FRONTEND_DIR) && npm run format

type-check: ## Run type checking
	@echo "$(BLUE)Running type checks...$(NC)"
	cd $(BACKEND_DIR) && mypy .
	cd $(FRONTEND_DIR) && npm run type-check

security-check: ## Run security checks
	@echo "$(BLUE)Running security checks...$(NC)"
	cd $(BACKEND_DIR) && bandit -r . -f json -o security-report.json || true
	cd $(BACKEND_DIR) && safety check
	cd $(FRONTEND_DIR) && npm audit

coverage: ## Generate test coverage report
	@echo "$(BLUE)Generating coverage report...$(NC)"
	cd $(BACKEND_DIR) && python scripts/coverage_report.py --format html
	@echo "$(GREEN)Coverage report generated in backend/htmlcov/$(NC)"

# Build targets
build: build-backend build-frontend ## Build all components

build-backend: ## Build backend Docker image
	@echo "$(BLUE)Building backend image...$(NC)"
	docker build -t $(PROJECT_NAME)/backend:$(VERSION) -f $(BACKEND_DIR)/Dockerfile $(BACKEND_DIR)/
	docker tag $(PROJECT_NAME)/backend:$(VERSION) $(PROJECT_NAME)/backend:latest

build-frontend: ## Build frontend Docker image
	@echo "$(BLUE)Building frontend image...$(NC)"
	docker build -t $(PROJECT_NAME)/frontend:$(VERSION) -f $(FRONTEND_DIR)/Dockerfile $(FRONTEND_DIR)/
	docker tag $(PROJECT_NAME)/frontend:$(VERSION) $(PROJECT_NAME)/frontend:latest

build-all: build ## Build and tag all images
	@echo "$(GREEN)All images built successfully!$(NC)"

# Development environment targets
run-dev: ## Start development environment
	@echo "$(BLUE)Starting development environment...$(NC)"
	docker-compose -f docker-compose.yml up -d
	@echo "$(GREEN)Development environment started!$(NC)"
	@echo "Backend API: http://localhost:8000"
	@echo "Frontend: http://localhost:3000"
	@echo "Grafana: http://localhost:3001"
	@echo "Prometheus: http://localhost:9090"

run-prod: ## Start production environment
	@echo "$(BLUE)Starting production environment...$(NC)"
	docker-compose -f docker-compose.prod.yml up -d
	@echo "$(GREEN)Production environment started!$(NC)"

stop: ## Stop all services
	@echo "$(BLUE)Stopping services...$(NC)"
	docker-compose down
	docker-compose -f docker-compose.prod.yml down
	docker-compose -f docker-compose.test.yml down

clean: ## Clean up containers, images, and volumes
	@echo "$(BLUE)Cleaning up...$(NC)"
	docker-compose down -v --remove-orphans
	docker system prune -f
	docker volume prune -f

# Deployment targets
deploy: ## Deploy to specified environment (default: staging)
	@echo "$(BLUE)Deploying to $(ENVIRONMENT)...$(NC)"
	python scripts/deploy.py --environment $(ENVIRONMENT)

deploy-staging: ## Deploy to staging environment
	@echo "$(BLUE)Deploying to staging...$(NC)"
	python scripts/deploy.py --environment staging

deploy-prod: ## Deploy to production environment
	@echo "$(YELLOW)Deploying to production...$(NC)"
	@read -p "Are you sure you want to deploy to production? [y/N] " -n 1 -r; \
	echo; \
	if [[ $$REPLY =~ ^[Yy]$$ ]]; then \
		python scripts/deploy.py --environment production; \
	else \
		echo "$(RED)Deployment cancelled$(NC)"; \
	fi

rollback: ## Rollback deployment
	@echo "$(YELLOW)Rolling back deployment...$(NC)"
	python scripts/deploy.py --rollback --environment $(ENVIRONMENT)

# Docker registry targets
docker-build: build ## Build and tag images for registry
	@echo "$(BLUE)Tagging images for registry...$(NC)"
	docker tag $(PROJECT_NAME)/backend:$(VERSION) $(DOCKER_REGISTRY)/$(PROJECT_NAME)/backend:$(VERSION)
	docker tag $(PROJECT_NAME)/frontend:$(VERSION) $(DOCKER_REGISTRY)/$(PROJECT_NAME)/frontend:$(VERSION)

docker-push: docker-build ## Push images to registry
	@echo "$(BLUE)Pushing images to registry...$(NC)"
	docker push $(DOCKER_REGISTRY)/$(PROJECT_NAME)/backend:$(VERSION)
	docker push $(DOCKER_REGISTRY)/$(PROJECT_NAME)/frontend:$(VERSION)
	docker push $(DOCKER_REGISTRY)/$(PROJECT_NAME)/backend:latest
	docker push $(DOCKER_REGISTRY)/$(PROJECT_NAME)/frontend:latest

docker-clean: ## Clean Docker images and containers
	@echo "$(BLUE)Cleaning Docker resources...$(NC)"
	docker container prune -f
	docker image prune -f
	docker network prune -f
	docker volume prune -f

# Kubernetes targets
k8s-deploy: ## Deploy to Kubernetes
	@echo "$(BLUE)Deploying to Kubernetes...$(NC)"
	kubectl apply -f k8s/namespace.yaml
	kubectl apply -f k8s/configmap.yaml
	kubectl apply -f k8s/secrets.yaml
	kubectl apply -f k8s/backend-deployment.yaml
	kubectl apply -f k8s/frontend-deployment.yaml
	kubectl apply -f k8s/celery-deployment.yaml

k8s-delete: ## Delete Kubernetes resources
	@echo "$(BLUE)Deleting Kubernetes resources...$(NC)"
	kubectl delete -f k8s/ --ignore-not-found=true

k8s-logs: ## View Kubernetes logs
	@echo "$(BLUE)Viewing Kubernetes logs...$(NC)"
	kubectl logs -f deployment/vulscanner-backend -n vulscanner

# Database targets
db-rev: ## Create autogenerate init migration
	@echo "$(BLUE)Creating initial autogenerate migration...$(NC)"
	cd $(BACKEND_DIR) && alembic revision --autogenerate -m "init"

db-migrate: ## Create new database migration
	@echo "$(BLUE)Creating database migration...$(NC)"
	cd $(BACKEND_DIR) && alembic revision --autogenerate -m "$(MESSAGE)"

db-upgrade: ## Upgrade database to latest migration
	@echo "$(BLUE)Upgrading database...$(NC)"
	cd $(BACKEND_DIR) && alembic upgrade head

db-downgrade: ## Downgrade database by one migration
	@echo "$(BLUE)Downgrading database...$(NC)"
	cd $(BACKEND_DIR) && alembic downgrade -1

db-reset: ## Reset database (WARNING: destructive)
	@echo "$(RED)WARNING: This will destroy all data!$(NC)"
	@read -p "Are you sure? [y/N] " -n 1 -r; \
	echo; \
	if [[ $$REPLY =~ ^[Yy]$$ ]]; then \
		cd $(BACKEND_DIR) && alembic downgrade base && alembic upgrade head; \
	else \
		echo "$(GREEN)Database reset cancelled$(NC)"; \
	fi

db-seed: ## Seed database with sample data
	@echo "$(BLUE)Seeding database...$(NC)"
	cd $(BACKEND_DIR) && python scripts/seed_database.py

# Monitoring targets
monitoring-up: ## Start monitoring stack
	@echo "$(BLUE)Starting monitoring stack...$(NC)"
	docker-compose -f docker-compose.monitoring.yml up -d
	@echo "$(GREEN)Monitoring stack started!$(NC)"
	@echo "Grafana: http://localhost:3001 (admin/admin)"
	@echo "Prometheus: http://localhost:9090"

monitoring-down: ## Stop monitoring stack
	@echo "$(BLUE)Stopping monitoring stack...$(NC)"
	docker-compose -f docker-compose.monitoring.yml down

logs: ## View application logs
	@echo "$(BLUE)Viewing application logs...$(NC)"
	docker-compose logs -f backend frontend celery-worker

# Backup and restore targets
backup: ## Create database backup
	@echo "$(BLUE)Creating database backup...$(NC)"
	mkdir -p backups
	docker-compose exec postgres pg_dump -U postgres vulscanner > backups/backup-$(shell date +%Y%m%d-%H%M%S).sql
	@echo "$(GREEN)Backup created in backups/ directory$(NC)"

restore: ## Restore database from backup
	@echo "$(BLUE)Available backups:$(NC)"
	@ls -la backups/
	@read -p "Enter backup filename: " backup_file; \
	if [ -f "backups/$$backup_file" ]; then \
		docker-compose exec -T postgres psql -U postgres -d vulscanner < "backups/$$backup_file"; \
		echo "$(GREEN)Database restored from $$backup_file$(NC)"; \
	else \
		echo "$(RED)Backup file not found$(NC)"; \
	fi

health-check: ## Check application health
	@echo "$(BLUE)Checking application health...$(NC)"
	@curl -s http://localhost:8000/api/v1/health | jq . || echo "$(RED)Backend health check failed$(NC)"
	@curl -s http://localhost:3000 > /dev/null && echo "$(GREEN)Frontend is healthy$(NC)" || echo "$(RED)Frontend health check failed$(NC)"

# CI/CD targets
ci-test: install-dev lint type-check security-check test coverage ## Run full CI test suite
	@echo "$(GREEN)CI test suite completed!$(NC)"

ci-build: build ## Build for CI/CD
	@echo "$(GREEN)CI build completed!$(NC)"

ci-deploy: docker-push deploy ## Deploy from CI/CD
	@echo "$(GREEN)CI deployment completed!$(NC)"

# Development helpers
dev-setup: install-dev db-upgrade db-seed ## Complete development setup
	@echo "$(GREEN)Development environment setup completed!$(NC)"
	@echo "Run 'make run-dev' to start the development server"

quick-test: ## Run quick tests (unit tests only)
	@echo "$(BLUE)Running quick tests...$(NC)"
	cd $(BACKEND_DIR) && python -m pytest tests/unit/ -x --tb=short
	cd $(FRONTEND_DIR) && npm run test:unit -- --watchAll=false

watch-test: ## Run tests in watch mode
	@echo "$(BLUE)Running tests in watch mode...$(NC)"
	cd $(BACKEND_DIR) && python -m pytest tests/ --tb=short -f

# Documentation targets
docs-build: ## Build documentation
	@echo "$(BLUE)Building documentation...$(NC)"
	cd docs && mkdocs build

docs-serve: ## Serve documentation locally
	@echo "$(BLUE)Serving documentation...$(NC)"
	cd docs && mkdocs serve

# Performance and profiling
profile: ## Run performance profiling
	@echo "$(BLUE)Running performance profiling...$(NC)"
	cd $(BACKEND_DIR) && python -m cProfile -o profile.stats scripts/profile_app.py
	cd $(BACKEND_DIR) && python -c "import pstats; pstats.Stats('profile.stats').sort_stats('cumulative').print_stats(20)"

benchmark: ## Run benchmarks
	@echo "$(BLUE)Running benchmarks...$(NC)"
	cd $(BACKEND_DIR) && python -m pytest tests/test_performance.py --benchmark-only --benchmark-sort=mean

# Utility targets
version: ## Show current version
	@echo "$(BLUE)Current version: $(GREEN)$(VERSION)$(NC)"

status: ## Show service status
	@echo "$(BLUE)Service Status:$(NC)"
	@docker-compose ps

env-check: ## Check environment variables
	@echo "$(BLUE)Checking environment variables...$(NC)"
	@python scripts/check_env.py

# Security and compliance
security-scan: ## Run comprehensive security scan
	@echo "$(BLUE)Running security scan...$(NC)"
	cd $(BACKEND_DIR) && bandit -r . -f json -o security-report.json
	cd $(BACKEND_DIR) && safety check --json --output safety-report.json
	cd $(FRONTEND_DIR) && npm audit --json > audit-report.json
	@echo "$(GREEN)Security scan completed. Check *-report.json files$(NC)"

compliance-check: ## Check compliance requirements
	@echo "$(BLUE)Checking compliance...$(NC)"
	@echo "TODO: Implement compliance checks (GDPR, SOC2, etc.)"

# Cleanup targets
clean-all: clean docker-clean ## Clean everything
	@echo "$(BLUE)Cleaning all resources...$(NC)"
	rm -rf $(BACKEND_DIR)/__pycache__
	rm -rf $(BACKEND_DIR)/.pytest_cache
	rm -rf $(BACKEND_DIR)/htmlcov
	rm -rf $(FRONTEND_DIR)/node_modules/.cache
	rm -rf $(FRONTEND_DIR)/dist
	rm -rf $(FRONTEND_DIR)/build
	@echo "$(GREEN)Cleanup completed!$(NC)"

# Help for specific categories
help-dev: ## Show development commands
	@echo "$(BLUE)Development Commands:$(NC)"
	@awk 'BEGIN {FS = ":.*?## "} /^(install|run|test|lint|format|type-check|dev-).*:.*?## / {printf "$(GREEN)%-20s$(NC) %s\n", $$1, $$2}' $(MAKEFILE_LIST)

help-deploy: ## Show deployment commands
	@echo "$(BLUE)Deployment Commands:$(NC)"
	@awk 'BEGIN {FS = ":.*?## "} /^(build|deploy|docker|k8s).*:.*?## / {printf "$(GREEN)%-20s$(NC) %s\n", $$1, $$2}' $(MAKEFILE_LIST)

help-db: ## Show database commands
	@echo "$(BLUE)Database Commands:$(NC)"
	@awk 'BEGIN {FS = ":.*?## "} /^(db-).*:.*?## / {printf "$(GREEN)%-20s$(NC) %s\n", $$1, $$2}' $(MAKEFILE_LIST)