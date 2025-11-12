# Enhanced Vulnerability Scanner

A comprehensive, production-ready web application vulnerability scanner built with modern technologies and best practices.

[![CI/CD](https://github.com/your-org/vulscanner/workflows/CI/badge.svg)](https://github.com/your-org/vulscanner/actions)
[![Coverage](https://img.shields.io/badge/coverage-85%25-green.svg)](https://github.com/your-org/vulscanner)
[![Security](https://img.shields.io/badge/security-A+-green.svg)](https://github.com/your-org/vulscanner)
[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)

## 🚀 Features

### Core Functionality
- **Intelligent Web Crawling**: Advanced async crawler with rate limiting and scope management
- **Technology Detection**: Comprehensive fingerprinting of web technologies, frameworks, and CMS
- **Form Analysis**: Detailed extraction and analysis of web forms, including CSRF detection
- **Security Headers**: Analysis of security headers and best practices compliance
- **Real-time Monitoring**: Live scan progress with WebSocket updates
- **Comprehensive Reporting**: Multiple export formats (JSON, CSV, PDF, HTML)

### Technical Excellence
- **Async Architecture**: Built on FastAPI with async/await patterns for high performance
- **Scalable Design**: Microservices architecture with Celery for background processing
- **Modern Frontend**: React 18+ with TypeScript and Material-UI v5
- **Production Ready**: Docker containers, Kubernetes manifests, monitoring, and CI/CD
- **Security First**: OWASP compliance, input validation, rate limiting, and audit logging

### Enterprise Features
- **Multi-tenant**: User isolation with row-level security
- **API-First**: RESTful API with OpenAPI documentation
- **Monitoring**: Prometheus metrics, Grafana dashboards, structured logging
- **High Availability**: Load balancing, auto-scaling, health checks
- **Backup & Recovery**: Automated backups with point-in-time recovery

## 🏗️ Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Frontend      │    │   Load Balancer │    │   Monitoring    │
│   React + TS    │◄──►│   Nginx/HAProxy │◄──►│   Grafana       │
│   Material-UI   │    │                 │    │   Prometheus    │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         ▼                       ▼                       ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Backend API   │    │   Task Queue    │    │   Database      │
│   FastAPI       │◄──►│   Celery        │◄──►│   Supabase      │
│   Python 3.11+  │    │   Redis/RMQ     │    │   PostgreSQL    │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         ▼                       ▼                       ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Crawler       │    │   Storage       │    │   Security      │
│   aiohttp       │    │   Supabase      │    │   Auth & RBAC   │
│   BeautifulSoup │    │   File Storage  │    │   Rate Limiting │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

## 🛠️ Technology Stack

### Backend
- **Framework**: FastAPI 0.104+ with async/await
- **Language**: Python 3.11+
- **ORM**: SQLAlchemy 2.0 with async support
- **Task Queue**: Celery with Redis broker
- **HTTP Client**: aiohttp for async web requests
- **Parser**: BeautifulSoup4 for HTML parsing
- **Validation**: Pydantic v2 for data validation

### Frontend
- **Framework**: React 18+ with TypeScript
- **UI Library**: Material-UI v5 with custom theming
- **State Management**: Redux Toolkit + React Query
- **Build Tool**: Vite with hot module replacement
- **Testing**: Vitest + React Testing Library

### Database & Auth
- **Database**: Supabase (PostgreSQL + Auth + Realtime + Storage)
- **Authentication**: Supabase Auth with JWT tokens
- **Real-time**: Supabase Realtime subscriptions
- **File Storage**: Supabase Storage for reports and logs

### Infrastructure
- **Containerization**: Docker + Docker Compose
- **Orchestration**: Kubernetes with Helm charts
- **Monitoring**: Prometheus + Grafana + Loki
- **CI/CD**: GitHub Actions with automated testing
- **Load Balancing**: Nginx with SSL termination

## 🚀 Quick Start

### Prerequisites
- Python 3.11+
- Node.js 18+
- Docker & Docker Compose
- Git

### 1. Clone Repository
```bash
git clone https://github.com/your-org/vulscanner.git
cd vulscanner
```

### 2. Environment Setup
```bash
# Copy environment template
cp .env.example .env

# Edit environment variables
# Required: DATABASE_URL, SUPABASE_URL, SUPABASE_SERVICE_ROLE_KEY, REDIS_URL, SECRET_KEY
```

### 3. Development Setup
```bash
# Install dependencies and setup development environment
make dev-setup

# Start development services
make run-dev
```
 
#### Local SQLite Mode (No Supabase)
Use this when you want to run the backend entirely locally without Supabase.

```bash
# 1) Copy env and enable local mode
cp .env.example .env
sed -i 's/^SKIP_SUPABASE=.*/SKIP_SUPABASE=true/' .env
sed -i 's/^DEVELOPMENT_MODE=.*/DEVELOPMENT_MODE=true/' .env

# 2) Install backend dependencies
python -m pip install -r backend/requirements.txt

# 3) Initialize the local dev database (SQLite dev.db)
python backend/scripts/migrate.py upgrade

# 4) Start the API (FastAPI + Uvicorn)
cd backend
python -m uvicorn main:app --host 127.0.0.1 --port 8000 --reload
```

Windows (PowerShell):
```powershell
# 1) Copy env and enable local mode
Copy-Item .env.example .env
(Get-Content .env) -replace '^SKIP_SUPABASE=.*', 'SKIP_SUPABASE=true' | Set-Content .env
(Get-Content .env) -replace '^DEVELOPMENT_MODE=.*', 'DEVELOPMENT_MODE=true' | Set-Content .env

# 2) Install backend dependencies
python -m pip install -r backend\requirements.txt

# 3) Initialize the local dev database (SQLite dev.db)
python backend\scripts\migrate.py upgrade

# 4) Start the API (FastAPI + Uvicorn)
cd backend
python -m uvicorn main:app --host 127.0.0.1 --port 8000 --reload
```

Notes:
- With `SKIP_SUPABASE=true`, the backend uses `sqlite+aiosqlite:///./dev.db` and dynamically configures Alembic.
- Tables are auto-created on app startup; running `migrate.py upgrade` ensures Alembic versioning is initialized.
- You can seed sample data anytime with `python backend/scripts/migrate.py seed`.

#### Local PostgreSQL Mode (Recommended for backend development)
Use this when you want the backend to connect to a local PostgreSQL instead of Supabase.

Prerequisites:
- A local PostgreSQL instance listening on `localhost:5433`
- A database `vulscanner`, user `krishna` with a known password

Environment setup (bash):
```bash
cp .env.example .env
export DATABASE_URL_ASYNC="postgresql+asyncpg://krishna:<YOUR_PASSWORD>@localhost:5433/vulscanner"
export DATABASE_URL_SYNC="postgresql+psycopg://krishna:<YOUR_PASSWORD>@localhost:5433/vulscanner"
# Optional if you want to bypass Supabase entirely in dev
export SKIP_SUPABASE=true
```

Environment setup (PowerShell):
```powershell
Copy-Item .env.example .env
$env:DATABASE_URL_ASYNC = 'postgresql+asyncpg://krishna:<YOUR_PASSWORD>@localhost:5433/vulscanner'
$env:DATABASE_URL_SYNC  = 'postgresql+psycopg://krishna:<YOUR_PASSWORD>@localhost:5433/vulscanner'
$env:SKIP_SUPABASE = 'true'
```

Run migrations:
```bash
cd backend && python -m alembic upgrade head
```
```powershell
cd backend; python -m alembic upgrade head
```

Smoke tests:
```bash
# DB health
curl -s http://127.0.0.1:8000/api/v1/db/health | jq

# Create a scan job
curl -s -X POST http://127.0.0.1:8000/api/v1/scan-jobs \
  -H 'Content-Type: application/json' \
  -d '{"url": "https://example.com"}' | jq
```
```powershell
# DB health
Invoke-RestMethod -Uri 'http://127.0.0.1:8000/api/v1/db/health' -Method GET

# Create a scan job
Invoke-RestMethod -Uri 'http://127.0.0.1:8000/api/v1/scan-jobs' -Method POST \
  -ContentType 'application/json' -Body '{"url":"https://example.com"}'
```

Docker notes:
- If the API runs inside Docker but PostgreSQL is on the host, use `host.docker.internal` instead of `localhost` in URLs.
- Example:
  - `DATABASE_URL_ASYNC=postgresql+asyncpg://krishna:<YOUR_PASSWORD>@host.docker.internal:5433/vulscanner`
  - `DATABASE_URL_SYNC=postgresql+psycopg://krishna:<YOUR_PASSWORD>@host.docker.internal:5433/vulscanner`

Tip: If you run the API in Docker against a host PostgreSQL, you can set `USE_HOST_DOCKER_INTERNAL=true` in `.env` to automatically swap `localhost` with `host.docker.internal` at runtime.

### 4. Access Application
- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs
- **Grafana**: http://localhost:3001 (admin/admin)
- **Prometheus**: http://localhost:9090

## 📋 Development Guide

### Project Structure
```
vulscanner/
├── backend/                 # FastAPI backend application
│   ├── core/               # Core configuration and utilities
│   ├── models/             # Database models and schemas
│   ├── api/                # API endpoints and routes
│   ├── crawler/            # Web crawling engine
│   ├── tasks/              # Celery background tasks
│   ├── services/           # Business logic services
│   ├── tests/              # Test suites
│   └── monitoring/         # Logging and metrics
├── frontend/               # React frontend application
│   ├── src/
│   │   ├── components/     # Reusable UI components
│   │   ├── pages/          # Page components
│   │   ├── store/          # Redux store and slices
│   │   ├── services/       # API services
│   │   └── utils/          # Utility functions
│   └── public/
├── k8s/                    # Kubernetes manifests
├── deployment/             # Deployment configurations
├── scripts/                # Automation scripts
├── docs/                   # Documentation
└── infrastructure/         # Docker and infrastructure files
```

### Available Commands
```bash
# Development
make install-dev           # Install development dependencies
make run-dev              # Start development environment
make test                 # Run all tests
make lint                 # Run code linters
make format               # Format code

# Building
make build                # Build all Docker images
make docker-push          # Push images to registry

# Deployment
make deploy-staging       # Deploy to staging
make deploy-prod          # Deploy to production
make rollback             # Rollback deployment

# Database
make db-migrate           # Create migration
make db-upgrade           # Apply migrations
make db-seed              # Seed with sample data

# Monitoring
make monitoring-up        # Start monitoring stack
make logs                 # View application logs
make health-check         # Check service health

# See all commands
make help
```

### Running Tests
```bash
# All tests
make test

# Specific test types
make test-unit            # Unit tests only
make test-integration     # Integration tests
make test-e2e             # End-to-end tests
make test-performance     # Performance benchmarks

# Coverage report
make coverage
```

### Code Quality
```bash
# Linting and formatting
make lint                 # Check code style
make format               # Auto-format code
make type-check           # Type checking
make security-check       # Security analysis

# Pre-commit hooks (auto-installed with make install-dev)
pre-commit run --all-files
```

## 🔧 Configuration

### Environment Variables
```bash
# Database
DATABASE_URL=postgresql://user:pass@localhost:5432/vulscanner
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_SERVICE_ROLE_KEY=your-service-role-key

# Redis & Message Broker
REDIS_URL=redis://localhost:6379/0
RABBITMQ_URL=amqp://guest:guest@localhost:5672/

# Application
SECRET_KEY=your-secret-key-here
ENVIRONMENT=development
LOG_LEVEL=INFO

# External Services
SLACK_WEBHOOK_URL=https://hooks.slack.com/services/...
SMTP_HOST=smtp.gmail.com
SMTP_USER=your-email@gmail.com
SMTP_PASSWORD=your-app-password
```

### Celery & Broker Setup
Background scans are executed via Celery. In development you can either use Docker services or run workers locally.

Option A — Docker (recommended):
```bash
# Start only the queue-related services
docker compose up -d rabbitmq redis celery-worker celery-beat
```
```powershell
# Start only the queue-related services
docker compose up -d rabbitmq redis celery-worker celery-beat
```

Option B — Local (no Docker):
```bash
# Ensure Redis and/or RabbitMQ are running locally
python -m pip install "celery[redis]"
celery -A backend.tasks.celery_app.celery_app worker -l info -Q crawler
celery -A backend.tasks.celery_app.celery_app beat -l info
```
```powershell
# Ensure Redis and/or RabbitMQ are running locally
python -m pip install "celery[redis]"
celery -A backend.tasks.celery_app.celery_app worker -l info -Q crawler
celery -A backend.tasks.celery_app.celery_app beat -l info
```

Fallback behavior (dev only):
- If the Celery broker is unreachable, the API will start the crawl locally so your UI doesn’t fail.
- Response will include `{"status":"started_local"}` and logs will show the local start.
- For proper distributed execution and monitoring, run RabbitMQ/Redis and Celery workers.

### Crawler Configuration
```python
# Default crawler settings
CRAWLER_CONFIG = {
    "max_depth": 3,
    "max_pages": 1000,
    "requests_per_second": 10,
    "timeout": 30,
    "follow_redirects": True,
    "respect_robots": True,
    "user_agent": "Enhanced-Vulnerability-Scanner/1.0"
}
```

## 🚀 Deployment

### Docker Compose (Recommended for Development)
```bash
# Development
make run-dev

# Production
make run-prod
```

### Kubernetes (Production)
```bash
# Deploy to Kubernetes
make k8s-deploy

# Check deployment status
kubectl get pods -n vulscanner

# View logs
make k8s-logs
```

### Automated Deployment
```bash
# Deploy to staging
make deploy-staging

# Deploy to production (with confirmation)
make deploy-prod

# Rollback if needed
make rollback
```

## 📊 Monitoring & Observability

### Metrics & Dashboards
- **Prometheus**: Metrics collection and alerting
- **Grafana**: Visualization dashboards
- **Application Metrics**: API performance, crawler statistics, error rates
- **Infrastructure Metrics**: CPU, memory, disk, network usage

### Logging
- **Structured Logging**: JSON format with correlation IDs
- **Log Aggregation**: Loki for centralized log collection
- **Log Levels**: DEBUG, INFO, WARNING, ERROR, CRITICAL
- **Security Logging**: Authentication, authorization, and security events

### Health Checks
```bash
# Application health
curl http://localhost:8000/api/v1/health

# Service status
make status

# Comprehensive health check
make health-check
```

### Alerting
- **Slack Integration**: Real-time notifications for deployments and alerts
- **Email Notifications**: Critical alerts and reports
- **Custom Alerts**: Configurable thresholds for metrics

## 🔒 Security

### Authentication & Authorization
- **JWT Tokens**: Supabase Auth with automatic token refresh
- **Row Level Security**: Database-level access control
- **Role-Based Access**: User roles and permissions
- **API Rate Limiting**: Configurable rate limits per user/endpoint

### Security Headers
```http
Strict-Transport-Security: max-age=31536000; includeSubDomains
Content-Security-Policy: default-src 'self'; script-src 'self'
X-Frame-Options: DENY
X-Content-Type-Options: nosniff
Referrer-Policy: strict-origin-when-cross-origin
```

### Data Protection
- **Input Validation**: Pydantic schemas for all inputs
- **SQL Injection Prevention**: Parameterized queries
- **XSS Protection**: Content sanitization and CSP headers
- **Secrets Management**: Environment variables and secret stores

### Compliance
- **OWASP Guidelines**: Following OWASP security best practices
- **Privacy**: GDPR-compliant data handling
- **Audit Logging**: Comprehensive audit trail
- **Vulnerability Scanning**: Regular security scans

## 📈 Performance

### Optimization Features
- **Async Architecture**: Non-blocking I/O operations
- **Connection Pooling**: Database and Redis connection pools
- **Caching**: Redis caching for frequently accessed data
- **CDN Integration**: Static asset delivery optimization
- **Database Indexing**: Optimized database queries

### Performance Metrics
- **API Response Time**: <200ms for standard operations
- **Crawler Speed**: 10-50 URLs/second (configurable)
- **Concurrent Users**: 1000+ concurrent users supported
- **Database Performance**: <100ms for indexed queries

### Scaling
- **Horizontal Scaling**: Stateless API servers
- **Auto-scaling**: Kubernetes HPA based on CPU/memory
- **Load Balancing**: Nginx with health checks
- **Database Scaling**: Supabase automatic scaling

## 🧪 Testing

### Test Coverage
- **Unit Tests**: >85% code coverage
- **Integration Tests**: API endpoints and database operations
- **E2E Tests**: Complete user workflows
- **Performance Tests**: Load testing and benchmarks

### Test Types
```bash
# Unit tests - Fast, isolated tests
pytest tests/unit/

# Integration tests - Database and API tests
pytest tests/integration/

# Performance tests - Benchmarks and load tests
pytest tests/test_performance.py --benchmark-only

# E2E tests - Full application workflows
npm run test:e2e
```

### Continuous Testing
- **Pre-commit Hooks**: Automated code quality checks
- **CI Pipeline**: Automated testing on every commit
- **Coverage Reports**: Automatic coverage reporting
- **Security Testing**: Automated security scans

## 📚 API Documentation

### Interactive Documentation
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **OpenAPI Spec**: http://localhost:8000/openapi.json

### Key Endpoints
```http
# Authentication
POST /api/v1/auth/login
POST /api/v1/auth/logout
GET  /api/v1/auth/user

# Projects
GET    /api/v1/projects
POST   /api/v1/projects
GET    /api/v1/projects/{id}
PUT    /api/v1/projects/{id}
DELETE /api/v1/projects/{id}

# Scans
GET    /api/v1/projects/{project_id}/scans
POST   /api/v1/projects/{project_id}/scans
GET    /api/v1/scans/{scan_id}
PUT    /api/v1/scans/{scan_id}/stop
DELETE /api/v1/scans/{scan_id}

# Results
GET /api/v1/scans/{scan_id}/urls
GET /api/v1/scans/{scan_id}/forms
GET /api/v1/scans/{scan_id}/technologies
GET /api/v1/scans/{scan_id}/export
```

## 🤝 Contributing

### Development Workflow
1. Fork the repository
2. Create a feature branch: `git checkout -b feature/amazing-feature`
3. Make your changes and add tests
4. Run the test suite: `make test`
5. Commit your changes: `git commit -m 'Add amazing feature'`
6. Push to the branch: `git push origin feature/amazing-feature`
7. Open a Pull Request

### Code Standards
- **Python**: Follow PEP 8, use type hints, 85%+ test coverage
- **TypeScript**: Strict mode, ESLint configuration, comprehensive types
- **Documentation**: Update README and API docs for new features
- **Testing**: Add tests for all new functionality

### Pull Request Process
1. Ensure all tests pass and coverage is maintained
2. Update documentation as needed
3. Add a clear description of changes
4. Request review from maintainers
5. Address feedback and iterate

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🆘 Support

### Getting Help
- **Documentation**: Check this README and inline documentation
- **Issues**: Create a GitHub issue for bugs or feature requests
- **Discussions**: Use GitHub Discussions for questions
- **Security**: Email security@yourcompany.com for security issues

### Troubleshooting

#### Common Issues
1. **Database Connection**: Check DATABASE_URL and Supabase credentials
2. **Redis Connection**: Ensure Redis is running and accessible
3. **Port Conflicts**: Check if ports 3000, 8000 are available
4. **Docker Issues**: Ensure Docker daemon is running

#### Debug Mode
```bash
# Enable debug logging
export LOG_LEVEL=DEBUG

# Run with verbose output
make run-dev VERBOSE=1

# Check service health
make health-check
```

#### Performance Issues
```bash
# Run performance tests
make test-performance

# Check resource usage
docker stats

# Profile application
make profile
```

## 🗺️ Roadmap

### Current Version (v1.0)
- ✅ Core crawling engine
- ✅ Technology detection
- ✅ Form analysis
- ✅ Real-time monitoring
- ✅ Production deployment

### Upcoming Features (v1.1)
- 🔄 Advanced vulnerability detection
- 🔄 Machine learning integration
- 🔄 Custom scan rules
- 🔄 Enhanced reporting
- 🔄 API rate limiting improvements

### Future Enhancements (v2.0)
- 📋 AI-powered vulnerability analysis
- 📋 Integration with security tools
- 📋 Advanced compliance reporting
- 📋 Multi-cloud deployment
- 📋 Enterprise SSO integration

---

## 📞 Contact

- **Project Lead**: Your Name (your.email@company.com)
- **Team**: Security Engineering Team
- **Repository**: https://github.com/your-org/vulscanner
- **Documentation**: https://vulscanner.docs.company.com

---

**Built with ❤️ by the Security Engineering Team**