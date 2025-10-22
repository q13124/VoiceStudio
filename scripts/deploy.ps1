# VoiceStudio Production Deployment Script (PowerShell)
# Handles database migrations, health checks, and graceful startup

param(
    [string]$Command = "deploy",
    [string]$DbUrl = $env:DB_URL ?? "postgresql+psycopg://voicestudio:secret@localhost:5432/voicestudio",
    [string]$ApiUrl = "http://localhost:8000",
    [int]$MaxRetries = 30,
    [int]$RetryInterval = 2,
    [switch]$BackupBeforeMigration = $true
)

$ErrorActionPreference = "Stop"

# Configuration
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$ProjectRoot = Split-Path -Parent $ScriptDir

function Write-Log {
    param([string]$Message)
    Write-Host "[$(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')] $Message" -ForegroundColor Green
}

function Write-Warning {
    param([string]$Message)
    Write-Host "[$(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')] WARNING: $Message" -ForegroundColor Yellow
}

function Write-Error {
    param([string]$Message)
    Write-Host "[$(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')] ERROR: $Message" -ForegroundColor Red
}

# Wait for database to be ready
function Wait-ForDatabase {
    Write-Log "Waiting for database to be ready..."

    $retries = 0
    while ($retries -lt $MaxRetries) {
        try {
            $pythonScript = @"
import os
import psycopg2
from urllib.parse import urlparse

url = os.getenv('DB_URL', '$DbUrl')
parsed = urlparse(url)
try:
    conn = psycopg2.connect(
        host=parsed.hostname or 'localhost',
        port=parsed.port or 5432,
        user=parsed.username,
        password=parsed.password,
        dbname=parsed.path.lstrip('/')
    )
    conn.close()
    print('Database is ready')
    exit(0)
except Exception as e:
    print(f'Database not ready: {e}')
    exit(1)
"@

            $result = python -c $pythonScript 2>$null
            if ($LASTEXITCODE -eq 0) {
                Write-Log "Database is ready!"
                return $true
            }
        }
        catch {
            # Continue to retry
        }

        $retries++
        Write-Log "Database not ready, retrying in ${RetryInterval}s... ($retries/$MaxRetries)"
        Start-Sleep -Seconds $RetryInterval
    }

    Write-Error "Database failed to become ready after $MaxRetries retries"
    return $false
}

# Run database migrations
function Invoke-Migrations {
    Write-Log "Running database migrations..."

    Set-Location $ProjectRoot

    # Check if alembic is available
    try {
        alembic --version | Out-Null
    }
    catch {
        Write-Error "Alembic not found. Please install it first."
        return $false
    }

    # Run migrations
    try {
        $env:DB_URL = $DbUrl
        alembic upgrade head
        Write-Log "Database migrations completed successfully"
        return $true
    }
    catch {
        Write-Error "Database migrations failed: $_"
        return $false
    }
}

# Health check for the API
function Test-ApiHealth {
    param(
        [string]$Url = $ApiUrl,
        [int]$MaxRetries = $MaxRetries
    )

    Write-Log "Performing health check on $Url..."

    $retries = 0
    while ($retries -lt $MaxRetries) {
        try {
            $response = Invoke-WebRequest -Uri "$Url/v1/health/metrics" -Method GET -TimeoutSec 10
            if ($response.StatusCode -eq 200) {
                Write-Log "Health check passed!"
                return $true
            }
        }
        catch {
            # Continue to retry
        }

        $retries++
        Write-Log "Health check failed, retrying in ${RetryInterval}s... ($retries/$MaxRetries)"
        Start-Sleep -Seconds $RetryInterval
    }

    Write-Error "Health check failed after $MaxRetries retries"
    return $false
}

# Backup database before migration
function Backup-Database {
    if ($BackupBeforeMigration) {
        Write-Log "Creating database backup before migration..."

        $backupScript = Join-Path $ProjectRoot "scripts\backup_db.py"
        if (Test-Path $backupScript) {
            try {
                $env:DB_URL = $DbUrl
                python $backupScript --backup-dir (Join-Path $ProjectRoot "backups")
            }
            catch {
                Write-Warning "Database backup failed, but continuing..."
            }
        }
        else {
            Write-Warning "Backup script not found, skipping backup"
        }
    }
}

# Main deployment function
function Start-Deployment {
    Write-Log "Starting VoiceStudio deployment..."

    # Set environment variables
    $env:DB_URL = $DbUrl

    # Wait for database
    if (-not (Wait-ForDatabase)) {
        exit 1
    }

    # Backup database
    Backup-Database

    # Run migrations
    if (-not (Invoke-Migrations)) {
        exit 1
    }

    # Start the application
    Write-Log "Starting VoiceStudio API..."

    Set-Location $ProjectRoot

    # Start with uvicorn
    try {
        uvicorn --version | Out-Null
    }
    catch {
        Write-Error "uvicorn not found. Please install it first."
        exit 1
    }

    # Start uvicorn in background
    $job = Start-Job -ScriptBlock {
        param($ProjectRoot, $DbUrl)
        Set-Location $ProjectRoot
        $env:DB_URL = $DbUrl
        uvicorn services.main:app --host 0.0.0.0 --port 8000 --workers 4
    } -ArgumentList $ProjectRoot, $DbUrl

    # Wait for API to start
    Start-Sleep -Seconds 5

    # Health check
    if (-not (Test-ApiHealth)) {
        Write-Error "API failed health check"
        Stop-Job $job
        Remove-Job $job
        exit 1
    }

    Write-Log "VoiceStudio API started successfully"
    Write-Log "API is available at: http://localhost:8000"
    Write-Log "API docs available at: http://localhost:8000/docs"

    # Wait for the job
    Wait-Job $job
    Receive-Job $job
    Remove-Job $job
}

# Show usage
function Show-Usage {
    Write-Host "Usage: .\deploy.ps1 [COMMAND] [OPTIONS]"
    Write-Host ""
    Write-Host "Commands:"
    Write-Host "  deploy     - Full deployment (default)"
    Write-Host "  migrate    - Run database migrations only"
    Write-Host "  health     - Perform health check"
    Write-Host "  backup     - Create database backup"
    Write-Host ""
    Write-Host "Options:"
    Write-Host "  -DbUrl     - Database connection URL"
    Write-Host "  -ApiUrl    - API URL for health checks"
    Write-Host "  -MaxRetries - Maximum retry attempts"
    Write-Host "  -RetryInterval - Seconds between retries"
    Write-Host "  -BackupBeforeMigration - Create backup before migration"
    Write-Host ""
    Write-Host "Environment variables:"
    Write-Host "  DB_URL     - Database connection URL"
    Write-Host ""
}

# Main script logic
switch ($Command.ToLower()) {
    "deploy" {
        Start-Deployment
    }
    "migrate" {
        $env:DB_URL = $DbUrl
        if (-not (Wait-ForDatabase)) { exit 1 }
        if (-not (Invoke-Migrations)) { exit 1 }
    }
    "health" {
        Test-ApiHealth
    }
    "backup" {
        $env:DB_URL = $DbUrl
        $backupScript = Join-Path $ProjectRoot "scripts\backup_db.py"
        python $backupScript --backup-dir (Join-Path $ProjectRoot "backups")
    }
    default {
        Show-Usage
        exit 1
    }
}
