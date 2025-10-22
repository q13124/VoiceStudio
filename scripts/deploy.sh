#!/bin/bash
set -euo pipefail

# VoiceStudio Production Deployment Script
# Handles database migrations, health checks, and graceful startup

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

# Configuration
DB_URL="${DB_URL:-postgresql+psycopg://voicestudio:secret@localhost:5432/voicestudio}"
MAX_RETRIES=30
RETRY_INTERVAL=2

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

log() {
    echo -e "${GREEN}[$(date +'%Y-%m-%d %H:%M:%S')]${NC} $1"
}

warn() {
    echo -e "${YELLOW}[$(date +'%Y-%m-%d %H:%M:%S')] WARNING:${NC} $1"
}

error() {
    echo -e "${RED}[$(date +'%Y-%m-%d %H:%M:%S')] ERROR:${NC} $1"
}

# Wait for database to be ready
wait_for_db() {
    log "Waiting for database to be ready..."
    
    local retries=0
    while [ $retries -lt $MAX_RETRIES ]; do
        if python -c "
import os
import psycopg2
from urllib.parse import urlparse

url = os.getenv('DB_URL', '$DB_URL')
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
" 2>/dev/null; then
            log "Database is ready!"
            return 0
        fi
        
        retries=$((retries + 1))
        log "Database not ready, retrying in ${RETRY_INTERVAL}s... (${retries}/${MAX_RETRIES})"
        sleep $RETRY_INTERVAL
    done
    
    error "Database failed to become ready after ${MAX_RETRIES} retries"
    return 1
}

# Run database migrations
run_migrations() {
    log "Running database migrations..."
    
    cd "$PROJECT_ROOT"
    
    # Check if alembic is available
    if ! command -v alembic &> /dev/null; then
        error "Alembic not found. Please install it first."
        return 1
    fi
    
    # Run migrations
    if alembic upgrade head; then
        log "Database migrations completed successfully"
    else
        error "Database migrations failed"
        return 1
    fi
}

# Health check for the API
health_check() {
    local api_url="${1:-http://localhost:8000}"
    local max_retries="${2:-30}"
    
    log "Performing health check on $api_url..."
    
    local retries=0
    while [ $retries -lt $max_retries ]; do
        if curl -f -s "$api_url/v1/health/metrics" > /dev/null 2>&1; then
            log "Health check passed!"
            return 0
        fi
        
        retries=$((retries + 1))
        log "Health check failed, retrying in ${RETRY_INTERVAL}s... (${retries}/${max_retries})"
        sleep $RETRY_INTERVAL
    done
    
    error "Health check failed after ${max_retries} retries"
    return 1
}

# Backup database before migration
backup_db() {
    if [ "${BACKUP_BEFORE_MIGRATION:-true}" = "true" ]; then
        log "Creating database backup before migration..."
        
        if [ -f "$PROJECT_ROOT/scripts/backup_db.py" ]; then
            python "$PROJECT_ROOT/scripts/backup_db.py" --backup-dir "$PROJECT_ROOT/backups" || {
                warn "Database backup failed, but continuing..."
            }
        else
            warn "Backup script not found, skipping backup"
        fi
    fi
}

# Main deployment function
deploy() {
    log "Starting VoiceStudio deployment..."
    
    # Set environment variables
    export DB_URL="$DB_URL"
    
    # Wait for database
    wait_for_db || exit 1
    
    # Backup database
    backup_db
    
    # Run migrations
    run_migrations || exit 1
    
    # Start the application
    log "Starting VoiceStudio API..."
    
    cd "$PROJECT_ROOT"
    
    # Start with uvicorn
    if command -v uvicorn &> /dev/null; then
        uvicorn services.main:app --host 0.0.0.0 --port 8000 --workers 4 &
        API_PID=$!
        
        # Wait for API to start
        sleep 5
        
        # Health check
        health_check "http://localhost:8000" || {
            error "API failed health check"
            kill $API_PID 2>/dev/null || true
            exit 1
        }
        
        log "VoiceStudio API started successfully (PID: $API_PID)"
        log "API is available at: http://localhost:8000"
        log "API docs available at: http://localhost:8000/docs"
        
        # Wait for the process
        wait $API_PID
    else
        error "uvicorn not found. Please install it first."
        exit 1
    fi
}

# Show usage
usage() {
    echo "Usage: $0 [COMMAND]"
    echo ""
    echo "Commands:"
    echo "  deploy     - Full deployment (default)"
    echo "  migrate    - Run database migrations only"
    echo "  health     - Perform health check"
    echo "  backup     - Create database backup"
    echo ""
    echo "Environment variables:"
    echo "  DB_URL     - Database connection URL (default: postgresql+psycopg://voicestudio:secret@localhost:5432/voicestudio)"
    echo "  BACKUP_BEFORE_MIGRATION - Create backup before migration (default: true)"
    echo ""
}

# Main script logic
main() {
    local command="${1:-deploy}"
    
    case "$command" in
        deploy)
            deploy
            ;;
        migrate)
            export DB_URL="$DB_URL"
            wait_for_db || exit 1
            run_migrations || exit 1
            ;;
        health)
            health_check "${2:-http://localhost:8000}" "${3:-30}"
            ;;
        backup)
            export DB_URL="$DB_URL"
            python "$PROJECT_ROOT/scripts/backup_db.py" --backup-dir "$PROJECT_ROOT/backups"
            ;;
        *)
            usage
            exit 1
            ;;
    esac
}

# Run main function with all arguments
main "$@"
