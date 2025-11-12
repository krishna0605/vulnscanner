# Enhanced Vulnerability Scanner - Development Setup Script
# PowerShell equivalent of Makefile for Windows development

param(
    [Parameter(Position=0)]
    [string]$Command = "help",
    
    [Parameter(Position=1)]
    [string]$Environment = "development"
)

# Color output functions
function Write-Success { param($Message) Write-Host $Message -ForegroundColor Green }
function Write-Info { param($Message) Write-Host $Message -ForegroundColor Cyan }
function Write-Warning { param($Message) Write-Host $Message -ForegroundColor Yellow }
function Write-Error { param($Message) Write-Host $Message -ForegroundColor Red }

# Configuration
$PROJECT_NAME = "vulscanner"
$BACKEND_DIR = "backend"
$FRONTEND_DIR = "frontend"
$DOCKER_COMPOSE_DEV = "docker-compose.yml"
$DOCKER_COMPOSE_PROD = "docker-compose.prod.yml"
$DOCKER_COMPOSE_TEST = "docker-compose.test.yml"

function Show-Help {
    Write-Info "Enhanced Vulnerability Scanner - Development Commands"
    Write-Host ""
    Write-Host "SETUP COMMANDS:" -ForegroundColor Yellow
    Write-Host "  install-dev     Install development dependencies"
    Write-Host "  setup-env       Setup environment files"
    Write-Host "  dev-setup       Complete development setup"
    Write-Host ""
    Write-Host "DEVELOPMENT COMMANDS:" -ForegroundColor Yellow
    Write-Host "  run-dev         Start development environment"
    Write-Host "  run-prod        Start production environment"
    Write-Host "  stop            Stop all services"
    Write-Host "  restart         Restart all services"
    Write-Host "  logs            View application logs"
    Write-Host "  shell-backend   Open backend shell"
    Write-Host "  shell-frontend  Open frontend shell"
    Write-Host ""
    Write-Host "TESTING COMMANDS:" -ForegroundColor Yellow
    Write-Host "  test            Run all tests"
    Write-Host "  test-unit       Run unit tests only"
    Write-Host "  test-integration Run integration tests"
    Write-Host "  test-e2e        Run end-to-end tests"
    Write-Host "  test-performance Run performance tests"
    Write-Host "  coverage        Generate coverage report"
    Write-Host ""
    Write-Host "CODE QUALITY COMMANDS:" -ForegroundColor Yellow
    Write-Host "  lint            Run code linters"
    Write-Host "  format          Format code"
    Write-Host "  type-check      Run type checking"
    Write-Host "  security-check  Run security analysis"
    Write-Host ""
    Write-Host "BUILD COMMANDS:" -ForegroundColor Yellow
    Write-Host "  build           Build all Docker images"
    Write-Host "  build-backend   Build backend image"
    Write-Host "  build-frontend  Build frontend image"
    Write-Host "  docker-push     Push images to registry"
    Write-Host ""
    Write-Host "DATABASE COMMANDS:" -ForegroundColor Yellow
    Write-Host "  db-migrate      Create database migration"
    Write-Host "  db-upgrade      Apply database migrations"
    Write-Host "  db-seed         Seed database with sample data"
    Write-Host "  db-reset        Reset database"
    Write-Host ""
    Write-Host "DEPLOYMENT COMMANDS:" -ForegroundColor Yellow
    Write-Host "  deploy-staging  Deploy to staging"
    Write-Host "  deploy-prod     Deploy to production"
    Write-Host "  rollback        Rollback deployment"
    Write-Host ""
    Write-Host "MONITORING COMMANDS:" -ForegroundColor Yellow
    Write-Host "  monitoring-up   Start monitoring stack"
    Write-Host "  monitoring-down Stop monitoring stack"
    Write-Host "  health-check    Check service health"
    Write-Host "  status          Show service status"
    Write-Host ""
    Write-Host "UTILITY COMMANDS:" -ForegroundColor Yellow
    Write-Host "  clean           Clean build artifacts"
    Write-Host "  clean-docker    Clean Docker resources"
    Write-Host "  backup          Create backup"
    Write-Host "  restore         Restore from backup"
    Write-Host ""
    Write-Host "Usage: .\scripts\dev-setup.ps1 <command>"
    Write-Host "Example: .\scripts\dev-setup.ps1 run-dev"
}

function Install-DevDependencies {
    Write-Info "Installing development dependencies..."
    
    # Check if Python is installed
    try {
        $pythonVersion = python --version 2>&1
        Write-Success "Python found: $pythonVersion"
    } catch {
        Write-Error "Python not found. Please install Python 3.11+"
        return
    }
    
    # Check if Node.js is installed
    try {
        $nodeVersion = node --version 2>&1
        Write-Success "Node.js found: $nodeVersion"
    } catch {
        Write-Error "Node.js not found. Please install Node.js 18+"
        return
    }
    
    # Install Python dependencies
    Write-Info "Installing Python dependencies..."
    Set-Location $BACKEND_DIR
    if (Test-Path "requirements.txt") {
        pip install -r requirements.txt
        pip install -r requirements-dev.txt
    } else {
        Write-Warning "requirements.txt not found in backend directory"
    }
    Set-Location ..
    
    # Install Node.js dependencies
    Write-Info "Installing Node.js dependencies..."
    Set-Location $FRONTEND_DIR
    if (Test-Path "package.json") {
        npm install
    } else {
        Write-Warning "package.json not found in frontend directory"
    }
    Set-Location ..
    
    # Install pre-commit hooks
    Write-Info "Installing pre-commit hooks..."
    if (Get-Command pre-commit -ErrorAction SilentlyContinue) {
        pre-commit install
    } else {
        Write-Warning "pre-commit not found. Install with: pip install pre-commit"
    }
    
    Write-Success "Development dependencies installed successfully!"
}

function Setup-Environment {
    Write-Info "Setting up environment files..."
    
    if (-not (Test-Path ".env")) {
        if (Test-Path ".env.example") {
            Copy-Item ".env.example" ".env"
            Write-Success "Created .env from .env.example"
            Write-Warning "Please edit .env file with your configuration"
        } else {
            Write-Error ".env.example not found"
        }
    } else {
        Write-Info ".env file already exists"
    }
}

function Complete-DevSetup {
    Write-Info "Running complete development setup..."
    Setup-Environment
    Install-DevDependencies
    Write-Success "Development setup completed!"
    Write-Info "Next steps:"
    Write-Host "  1. Edit .env file with your configuration"
    Write-Host "  2. Run: .\scripts\dev-setup.ps1 run-dev"
}

function Start-Development {
    Write-Info "Starting development environment..."
    
    if (-not (Test-Path ".env")) {
        Write-Error ".env file not found. Run 'setup-env' first."
        return
    }
    
    # Check if Docker is running
    try {
        docker version | Out-Null
        Write-Success "Docker is running"
    } catch {
        Write-Error "Docker is not running. Please start Docker Desktop."
        return
    }
    
    # Start services
    docker-compose -f $DOCKER_COMPOSE_DEV up -d
    
    Write-Success "Development environment started!"
    Write-Info "Services available at:"
    Write-Host "  Frontend: http://localhost:3000"
    Write-Host "  Backend API: http://localhost:8000"
    Write-Host "  API Docs: http://localhost:8000/docs"
    Write-Host "  Grafana: http://localhost:3001 (admin/admin)"
    Write-Host "  Prometheus: http://localhost:9090"
}

function Start-Production {
    Write-Info "Starting production environment..."
    docker-compose -f $DOCKER_COMPOSE_PROD up -d
    Write-Success "Production environment started!"
}

function Stop-Services {
    Write-Info "Stopping all services..."
    docker-compose -f $DOCKER_COMPOSE_DEV down
    docker-compose -f $DOCKER_COMPOSE_PROD down
    docker-compose -f $DOCKER_COMPOSE_TEST down
    Write-Success "All services stopped!"
}

function Restart-Services {
    Write-Info "Restarting services..."
    Stop-Services
    Start-Sleep -Seconds 2
    Start-Development
}

function Show-Logs {
    Write-Info "Showing application logs..."
    docker-compose -f $DOCKER_COMPOSE_DEV logs -f
}

function Open-BackendShell {
    Write-Info "Opening backend shell..."
    docker-compose -f $DOCKER_COMPOSE_DEV exec backend bash
}

function Open-FrontendShell {
    Write-Info "Opening frontend shell..."
    docker-compose -f $DOCKER_COMPOSE_DEV exec frontend sh
}

function Run-Tests {
    Write-Info "Running all tests..."
    
    # Backend tests
    Write-Info "Running backend tests..."
    Set-Location $BACKEND_DIR
    python -m pytest tests/ -v --cov=. --cov-report=html --cov-report=term
    Set-Location ..
    
    # Frontend tests
    Write-Info "Running frontend tests..."
    Set-Location $FRONTEND_DIR
    npm test
    Set-Location ..
    
    Write-Success "All tests completed!"
}

function Run-UnitTests {
    Write-Info "Running unit tests..."
    Set-Location $BACKEND_DIR
    python -m pytest tests/unit/ -v
    Set-Location ..
}

function Run-IntegrationTests {
    Write-Info "Running integration tests..."
    Set-Location $BACKEND_DIR
    python -m pytest tests/integration/ -v
    Set-Location ..
}

function Run-E2ETests {
    Write-Info "Running end-to-end tests..."
    Set-Location $FRONTEND_DIR
    npm run test:e2e
    Set-Location ..
}

function Run-PerformanceTests {
    Write-Info "Running performance tests..."
    Set-Location $BACKEND_DIR
    python -m pytest tests/test_performance.py --benchmark-only
    Set-Location ..
}

function Generate-Coverage {
    Write-Info "Generating coverage report..."
    Set-Location $BACKEND_DIR
    python -m pytest tests/ --cov=. --cov-report=html --cov-report=term
    Write-Success "Coverage report generated in backend/htmlcov/"
    Set-Location ..
}

function Run-Linting {
    Write-Info "Running code linters..."
    
    # Backend linting
    Set-Location $BACKEND_DIR
    Write-Info "Linting Python code..."
    ruff check .
    flake8 .
    Set-Location ..
    
    # Frontend linting
    Set-Location $FRONTEND_DIR
    Write-Info "Linting TypeScript code..."
    npm run lint
    Set-Location ..
    
    Write-Success "Linting completed!"
}

function Format-Code {
    Write-Info "Formatting code..."
    
    # Backend formatting
    Set-Location $BACKEND_DIR
    Write-Info "Formatting Python code..."
    black .
    isort .
    Set-Location ..
    
    # Frontend formatting
    Set-Location $FRONTEND_DIR
    Write-Info "Formatting TypeScript code..."
    npm run format
    Set-Location ..
    
    Write-Success "Code formatting completed!"
}

function Run-TypeCheck {
    Write-Info "Running type checking..."
    
    # Backend type checking
    Set-Location $BACKEND_DIR
    Write-Info "Type checking Python code..."
    mypy .
    Set-Location ..
    
    # Frontend type checking
    Set-Location $FRONTEND_DIR
    Write-Info "Type checking TypeScript code..."
    npm run type-check
    Set-Location ..
    
    Write-Success "Type checking completed!"
}

function Run-SecurityCheck {
    Write-Info "Running security analysis..."
    
    Set-Location $BACKEND_DIR
    Write-Info "Scanning Python dependencies..."
    bandit -r .
    safety check
    Set-Location ..
    
    Write-Success "Security analysis completed!"
}

function Build-All {
    Write-Info "Building all Docker images..."
    docker-compose -f $DOCKER_COMPOSE_PROD build
    Write-Success "All images built successfully!"
}

function Build-Backend {
    Write-Info "Building backend image..."
    docker-compose -f $DOCKER_COMPOSE_PROD build backend
    Write-Success "Backend image built successfully!"
}

function Build-Frontend {
    Write-Info "Building frontend image..."
    docker-compose -f $DOCKER_COMPOSE_PROD build frontend
    Write-Success "Frontend image built successfully!"
}

function Push-Images {
    Write-Info "Pushing images to registry..."
    docker-compose -f $DOCKER_COMPOSE_PROD push
    Write-Success "Images pushed successfully!"
}

function Create-Migration {
    Write-Info "Creating database migration..."
    Set-Location $BACKEND_DIR
    alembic revision --autogenerate -m "Auto migration"
    Set-Location ..
    Write-Success "Migration created!"
}

function Apply-Migrations {
    Write-Info "Applying database migrations..."
    Set-Location $BACKEND_DIR
    alembic upgrade head
    Set-Location ..
    Write-Success "Migrations applied!"
}

function Seed-Database {
    Write-Info "Seeding database with sample data..."
    Set-Location $BACKEND_DIR
    python scripts/seed_data.py
    Set-Location ..
    Write-Success "Database seeded!"
}

function Reset-Database {
    Write-Info "Resetting database..."
    Write-Warning "This will delete all data. Are you sure? (y/N)"
    $confirmation = Read-Host
    if ($confirmation -eq 'y' -or $confirmation -eq 'Y') {
        Set-Location $BACKEND_DIR
        alembic downgrade base
        alembic upgrade head
        python scripts/seed_data.py
        Set-Location ..
        Write-Success "Database reset completed!"
    } else {
        Write-Info "Database reset cancelled."
    }
}

function Start-Monitoring {
    Write-Info "Starting monitoring stack..."
    docker-compose -f $DOCKER_COMPOSE_PROD up -d prometheus grafana loki promtail
    Write-Success "Monitoring stack started!"
    Write-Info "Grafana: http://localhost:3001 (admin/admin)"
    Write-Info "Prometheus: http://localhost:9090"
}

function Stop-Monitoring {
    Write-Info "Stopping monitoring stack..."
    docker-compose -f $DOCKER_COMPOSE_PROD stop prometheus grafana loki promtail
    Write-Success "Monitoring stack stopped!"
}

function Check-Health {
    Write-Info "Checking service health..."
    
    $services = @(
        @{Name="Backend API"; Url="http://localhost:8000/api/v1/health"},
        @{Name="Frontend"; Url="http://localhost:3000"},
        @{Name="Prometheus"; Url="http://localhost:9090/-/healthy"},
        @{Name="Grafana"; Url="http://localhost:3001/api/health"}
    )
    
    foreach ($service in $services) {
        try {
            $response = Invoke-WebRequest -Uri $service.Url -TimeoutSec 5 -UseBasicParsing
            if ($response.StatusCode -eq 200) {
                Write-Success "$($service.Name): Healthy"
            } else {
                Write-Warning "$($service.Name): Unhealthy (Status: $($response.StatusCode))"
            }
        } catch {
            Write-Error "$($service.Name): Unreachable"
        }
    }
}

function Show-Status {
    Write-Info "Service Status:"
    docker-compose -f $DOCKER_COMPOSE_DEV ps
}

function Clean-Artifacts {
    Write-Info "Cleaning build artifacts..."
    
    # Python artifacts
    Get-ChildItem -Path . -Recurse -Name "__pycache__" | Remove-Item -Recurse -Force
    Get-ChildItem -Path . -Recurse -Name "*.pyc" | Remove-Item -Force
    Get-ChildItem -Path . -Recurse -Name ".pytest_cache" | Remove-Item -Recurse -Force
    
    # Node.js artifacts
    if (Test-Path "$FRONTEND_DIR/node_modules") {
        Remove-Item "$FRONTEND_DIR/node_modules" -Recurse -Force
    }
    if (Test-Path "$FRONTEND_DIR/dist") {
        Remove-Item "$FRONTEND_DIR/dist" -Recurse -Force
    }
    
    Write-Success "Build artifacts cleaned!"
}

function Clean-Docker {
    Write-Info "Cleaning Docker resources..."
    docker system prune -f
    docker volume prune -f
    Write-Success "Docker resources cleaned!"
}

# Main command dispatcher
switch ($Command.ToLower()) {
    "help" { Show-Help }
    "install-dev" { Install-DevDependencies }
    "setup-env" { Setup-Environment }
    "dev-setup" { Complete-DevSetup }
    "run-dev" { Start-Development }
    "run-prod" { Start-Production }
    "stop" { Stop-Services }
    "restart" { Restart-Services }
    "logs" { Show-Logs }
    "shell-backend" { Open-BackendShell }
    "shell-frontend" { Open-FrontendShell }
    "test" { Run-Tests }
    "test-unit" { Run-UnitTests }
    "test-integration" { Run-IntegrationTests }
    "test-e2e" { Run-E2ETests }
    "test-performance" { Run-PerformanceTests }
    "coverage" { Generate-Coverage }
    "lint" { Run-Linting }
    "format" { Format-Code }
    "type-check" { Run-TypeCheck }
    "security-check" { Run-SecurityCheck }
    "build" { Build-All }
    "build-backend" { Build-Backend }
    "build-frontend" { Build-Frontend }
    "docker-push" { Push-Images }
    "db-migrate" { Create-Migration }
    "db-upgrade" { Apply-Migrations }
    "db-seed" { Seed-Database }
    "db-reset" { Reset-Database }
    "monitoring-up" { Start-Monitoring }
    "monitoring-down" { Stop-Monitoring }
    "health-check" { Check-Health }
    "status" { Show-Status }
    "clean" { Clean-Artifacts }
    "clean-docker" { Clean-Docker }
    default {
        Write-Error "Unknown command: $Command"
        Write-Info "Run '.\scripts\dev-setup.ps1 help' to see available commands"
    }
}