# Enhanced Vulnerability Scanner - Backend Management Script (PowerShell)
# Database migration and management commands for Windows

param(
    [Parameter(Position=0)]
    [string]$Command,
    
    [Parameter(Position=1)]
    [string]$Argument,
    
    [switch]$Force,
    [switch]$Help
)

# Color functions
function Write-Success { param($Message) Write-Host $Message -ForegroundColor Green }
function Write-Error { param($Message) Write-Host $Message -ForegroundColor Red }
function Write-Warning { param($Message) Write-Host $Message -ForegroundColor Yellow }
function Write-Info { param($Message) Write-Host $Message -ForegroundColor Cyan }

function Show-Help {
    Write-Host "Enhanced Vulnerability Scanner - Backend Management" -ForegroundColor Blue
    Write-Host ""
    Write-Host "Usage: .\scripts\manage.ps1 <command> [arguments] [options]" -ForegroundColor White
    Write-Host ""
    Write-Host "Development Commands:" -ForegroundColor Yellow
    Write-Host "  install          Install dependencies"
    Write-Host "  dev              Run development server"
    Write-Host "  test             Run tests"
    Write-Host "  lint             Run linting"
    Write-Host "  format           Format code"
    Write-Host "  clean            Clean temporary files"
    Write-Host ""
    Write-Host "Database Migration:" -ForegroundColor Yellow
    Write-Host "  db-status        Show migration status"
    Write-Host "  db-upgrade       Upgrade to latest migration"
    Write-Host "  db-downgrade     Downgrade one migration"
    Write-Host "  db-history       Show migration history"
    Write-Host "  db-create <name> Create new migration"
    Write-Host "  db-reset         Reset database (dev only)"
    Write-Host "  db-seed          Seed with test data"
    Write-Host "  db-check         Check database connectivity"
    Write-Host ""
    Write-Host "Database Backup:" -ForegroundColor Yellow
    Write-Host "  db-backup [name] Create database backup"
    Write-Host "  db-restore <name> Restore from backup"
    Write-Host "  db-list          List available backups"
    Write-Host "  db-cleanup       Cleanup old backups"
    Write-Host "  db-export <fmt>  Export data (json/csv)"
    Write-Host ""
    Write-Host "Database Validation:" -ForegroundColor Yellow
    Write-Host "  db-validate      Check data integrity"
    Write-Host "  db-repair        Repair database issues"
    Write-Host "  db-analyze       Analyze database statistics"
    Write-Host ""
    Write-Host "Server Management:" -ForegroundColor Yellow
    Write-Host "  run              Run production server"
    Write-Host "  run-dev          Run development server"
    Write-Host "  stop             Stop running servers"
    Write-Host "  health           Check server health"
    Write-Host ""
    Write-Host "Options:" -ForegroundColor Yellow
    Write-Host "  -Force           Skip confirmations"
    Write-Host "  -Help            Show this help"
    Write-Host ""
    Write-Host "Examples:" -ForegroundColor Green
    Write-Host "  .\scripts\manage.ps1 db-status"
    Write-Host "  .\scripts\manage.ps1 db-create 'add_new_field'"
    Write-Host "  .\scripts\manage.ps1 db-backup 'before_update'"
    Write-Host "  .\scripts\manage.ps1 db-restore 'backup_20241101'"
}

function Invoke-PythonScript {
    param($ScriptPath, $Arguments)
    
    $fullPath = Join-Path $PSScriptRoot $ScriptPath
    if (-not (Test-Path $fullPath)) {
        Write-Error "Script not found: $fullPath"
        exit 1
    }
    
    $cmd = "python `"$fullPath`" $Arguments"
    Write-Info "Executing: $cmd"
    Invoke-Expression $cmd
}

function Test-PythonEnvironment {
    try {
        $pythonVersion = python --version 2>&1
        if ($LASTEXITCODE -ne 0) {
            Write-Error "Python not found. Please install Python 3.11+ and add it to PATH."
            exit 1
        }
        Write-Info "Using: $pythonVersion"
    }
    catch {
        Write-Error "Python not found. Please install Python 3.11+ and add it to PATH."
        exit 1
    }
}

# Main command processing
if ($Help -or $Command -eq "help" -or -not $Command) {
    Show-Help
    exit 0
}

# Test Python environment
Test-PythonEnvironment

# Change to backend directory
$backendDir = Split-Path $PSScriptRoot -Parent
Set-Location $backendDir

switch ($Command.ToLower()) {
    # Development commands
    "install" {
        Write-Info "Installing dependencies..."
        pip install -r requirements.txt
        if ($LASTEXITCODE -eq 0) {
            Write-Success "Dependencies installed successfully!"
        } else {
            Write-Error "Failed to install dependencies"
            exit 1
        }
    }
    
    "dev" {
        Write-Info "Starting development server..."
        python -m uvicorn main:app --reload --host 0.0.0.0 --port 8000
    }
    
    "test" {
        Write-Info "Running tests..."
        pytest tests/ -v --cov=. --cov-report=html
    }
    
    "lint" {
        Write-Info "Running linting..."
        ruff check .
        mypy .
    }
    
    "format" {
        Write-Info "Formatting code..."
        black .
        isort .
        ruff format .
        Write-Success "Code formatted successfully!"
    }
    
    "clean" {
        Write-Info "Cleaning temporary files..."
        Get-ChildItem -Recurse -Name "*.pyc" | Remove-Item -Force
        Get-ChildItem -Recurse -Directory -Name "__pycache__" | Remove-Item -Recurse -Force
        Get-ChildItem -Recurse -Directory -Name "*.egg-info" | Remove-Item -Recurse -Force
        if (Test-Path ".coverage") { Remove-Item ".coverage" -Force }
        if (Test-Path "htmlcov") { Remove-Item "htmlcov" -Recurse -Force }
        if (Test-Path ".pytest_cache") { Remove-Item ".pytest_cache" -Recurse -Force }
        Write-Success "Cleanup completed!"
    }
    
    # Database migration commands
    "db-status" {
        Invoke-PythonScript "migrate.py" "status"
    }
    
    "db-upgrade" {
        Invoke-PythonScript "migrate.py" "upgrade"
    }
    
    "db-downgrade" {
        Invoke-PythonScript "migrate.py" "downgrade"
    }
    
    "db-history" {
        Invoke-PythonScript "migrate.py" "history"
    }
    
    "db-create" {
        if (-not $Argument) {
            $Argument = Read-Host "Enter migration name"
        }
        Invoke-PythonScript "migrate.py" "create `"$Argument`" --autogenerate"
    }
    
    "db-reset" {
        if (-not $Force) {
            $confirm = Read-Host "This will DELETE ALL DATA. Type 'yes' to confirm"
            if ($confirm -ne "yes") {
                Write-Warning "Reset cancelled."
                exit 0
            }
        }
        Invoke-PythonScript "migrate.py" "reset"
    }
    
    "db-seed" {
        Invoke-PythonScript "migrate.py" "seed"
    }
    
    "db-check" {
        Invoke-PythonScript "migrate.py" "check"
    }
    
    # Database backup commands
    "db-backup" {
        if ($Argument) {
            Invoke-PythonScript "backup.py" "create --name `"$Argument`""
        } else {
            Invoke-PythonScript "backup.py" "create"
        }
    }
    
    "db-restore" {
        if (-not $Argument) {
            Write-Info "Available backups:"
            Invoke-PythonScript "backup.py" "list"
            $Argument = Read-Host "Enter backup name to restore"
        }
        
        if (-not $Force) {
            $confirm = Read-Host "This will overwrite the current database. Type 'yes' to confirm"
            if ($confirm -ne "yes") {
                Write-Warning "Restore cancelled."
                exit 0
            }
        }
        
        Invoke-PythonScript "backup.py" "restore `"$Argument`" --force"
    }
    
    "db-list" {
        Invoke-PythonScript "backup.py" "list"
    }
    
    "db-cleanup" {
        Invoke-PythonScript "backup.py" "cleanup"
    }
    
    "db-export" {
        if (-not $Argument) {
            $Argument = Read-Host "Enter export format (json/csv)"
        }
        Invoke-PythonScript "backup.py" "export $Argument"
    }
    
    # Database validation commands
    "db-validate" {
        Write-Info "Checking schema integrity..."
        Invoke-PythonScript "validate_schema.py" "check"
        Write-Info "Validating data integrity..."
        Invoke-PythonScript "validate_schema.py" "validate"
    }
    
    "db-repair" {
        if (-not $Force) {
            $confirm = Read-Host "This will modify the database. Type 'yes' to confirm"
            if ($confirm -ne "yes") {
                Write-Warning "Repair cancelled."
                exit 0
            }
        }
        Invoke-PythonScript "validate_schema.py" "repair"
    }
    
    "db-analyze" {
        Invoke-PythonScript "validate_schema.py" "analyze"
    }
    
    # Server management
    "run" {
        Write-Info "Starting production server..."
        python -m uvicorn main:app --host 0.0.0.0 --port 8000
    }
    
    "run-dev" {
        Write-Info "Starting development server..."
        python -m uvicorn main:app --reload --host 0.0.0.0 --port 8000
    }
    
    "stop" {
        Write-Info "Stopping servers..."
        Get-Process | Where-Object {$_.ProcessName -like "*python*" -and $_.CommandLine -like "*uvicorn*"} | Stop-Process -Force
        Write-Success "Servers stopped."
    }
    
    "health" {
        Write-Info "Checking server health..."
        try {
            $response = Invoke-RestMethod -Uri "http://localhost:8000/api/v1/health" -Method Get
            Write-Success "Server is healthy!"
            $response | ConvertTo-Json -Depth 3
        }
        catch {
            Write-Error "Server health check failed: $($_.Exception.Message)"
        }
    }
    
    # Setup commands
    "setup-dev" {
        Write-Info "Setting up development environment..."
        
        # Copy environment file
        if (-not (Test-Path ".env") -and (Test-Path ".env.example")) {
            Copy-Item ".env.example" ".env"
            Write-Success "Created .env file from template"
        }
        
        # Install dependencies
        Write-Info "Installing dependencies..."
        pip install -r requirements.txt
        
        # Run migrations
        Write-Info "Running database migrations..."
        Invoke-PythonScript "migrate.py" "upgrade"
        
        # Seed database
        Write-Info "Seeding database..."
        Invoke-PythonScript "migrate.py" "seed"
        
        Write-Success "Development environment setup complete!"
        Write-Info "You can now run: .\scripts\manage.ps1 dev"
    }
    
    "setup-prod" {
        Write-Info "Setting up production environment..."
        
        # Install dependencies
        pip install -r requirements.txt
        
        # Run migrations
        Invoke-PythonScript "migrate.py" "upgrade"
        
        Write-Success "Production environment setup complete!"
    }
    
    default {
        Write-Error "Unknown command: $Command"
        Write-Info "Use -Help to see available commands"
        exit 1
    }
}