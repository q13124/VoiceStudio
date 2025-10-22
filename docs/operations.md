# VoiceStudio Operations Guide

This guide covers the operational aspects of VoiceStudio, including database management, monitoring, and deployment.

## Quick Start

### Development (SQLite)
```bash
# Copy environment template
cp env.example .env

# Install dependencies
pip install -r requirements.lock.txt

# Run migrations
alembic upgrade head

# Start the API
uvicorn services.main:app --reload
```

### Production (PostgreSQL + Docker)
```bash
# Start all services
docker-compose up -d

# Run migrations
docker-compose exec voicestudio-api alembic upgrade head

# Check health
curl http://localhost:8000/v1/health/metrics
```

## Database Management

### Alembic Migrations

VoiceStudio uses Alembic for database schema management. All database changes should be made through migrations.

```bash
# Create a new migration
alembic revision --autogenerate -m "Description of changes"

# Apply migrations
alembic upgrade head

# Rollback to previous version
alembic downgrade -1

# Check current version
alembic current

# Show migration history
alembic history
```

### Database URLs

- **SQLite (Development)**: `sqlite:///./app.db`
- **PostgreSQL (Production)**: `postgresql+psycopg://user:pass@host:port/dbname`

### Backup and Restore

#### Automated Backups
```bash
# Manual backup
python scripts/backup_db.py --backup-dir ./backups

# With compression
python scripts/backup_db.py --backup-dir ./backups --retention-days 7

# Dry run
python scripts/backup_db.py --dry-run
```

#### PostgreSQL Backup
```bash
# Full backup
pg_dump -h localhost -U voicestudio voicestudio > backup.sql

# Restore
psql -h localhost -U voicestudio voicestudio < backup.sql
```

#### SQLite Backup
```bash
# Simple copy
cp app.db backup_$(date +%Y%m%d).db

# With compression
gzip -c app.db > backup_$(date +%Y%m%d).db.gz
```

## Monitoring and Observability

### Prometheus Metrics

VoiceStudio exposes metrics at `/metrics` when `PROM_ENABLED=true`.

Key metrics:
- `voicestudio_tts_requests_total` - Total TTS requests by engine
- `voicestudio_tts_request_duration_seconds` - Request duration histogram
- `voicestudio_engine_load_ratio` - Engine load ratio
- `voicestudio_engine_health` - Engine health status

### Grafana Dashboards

Import the dashboard from `ops/grafana/voicestudio_dashboard.json`:

1. Go to Grafana → Dashboards → Import
2. Upload `ops/grafana/voicestudio_dashboard.json`
3. Configure PostgreSQL datasource

### Health Checks

```bash
# API health
curl http://localhost:8000/v1/health/metrics

# Database connectivity
python -c "from app.core.db import engine; print('DB OK' if engine.connect() else 'DB FAIL')"
```

## Deployment

### Using Deployment Scripts

#### Linux/macOS
```bash
# Full deployment
./scripts/deploy.sh

# Migrations only
./scripts/deploy.sh migrate

# Health check
./scripts/deploy.sh health
```

#### Windows PowerShell
```powershell
# Full deployment
.\scripts\deploy.ps1

# Migrations only
.\scripts\deploy.ps1 migrate

# Health check
.\scripts\deploy.ps1 health
```

### Docker Compose

```bash
# Start all services
docker-compose up -d

# View logs
docker-compose logs -f voicestudio-api

# Run migrations
docker-compose exec voicestudio-api alembic upgrade head

# Stop services
docker-compose down
```

### Manual Deployment

```bash
# 1. Install dependencies
pip install -r requirements.lock.txt

# 2. Set environment variables
export DB_URL="postgresql+psycopg://user:pass@host:port/db"
export AB_PERSIST_ENABLED=true
export EVALS_INGEST_ENABLED=true

# 3. Run migrations
alembic upgrade head

# 4. Start application
uvicorn services.main:app --host 0.0.0.0 --port 8000 --workers 4
```

## Configuration

### Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `DB_URL` | `sqlite:///./app.db` | Database connection URL |
| `AB_PERSIST_ENABLED` | `false` | Enable A/B summary persistence |
| `EVALS_INGEST_ENABLED` | `false` | Enable evaluation ingest endpoint |
| `EVALS_INGEST_TOKEN` | `null` | Bearer token for ingest endpoint |
| `PROM_ENABLED` | `false` | Enable Prometheus metrics |
| `METRICS_ENABLED` | `false` | Enable audio metrics |
| `FFMPEG_PATH` | `null` | Custom FFmpeg path |
| `FFPROBE_PATH` | `null` | Custom FFprobe path |

### Database Configuration

#### PostgreSQL Setup
```sql
-- Create database and user
CREATE DATABASE voicestudio;
CREATE USER voicestudio WITH PASSWORD 'secret';
GRANT ALL PRIVILEGES ON DATABASE voicestudio TO voicestudio;
```

#### Connection Pool Settings
The application uses SQLAlchemy connection pooling. For production:

```python
# In app/core/db.py
engine = create_engine(
    db_url,
    pool_size=20,
    max_overflow=30,
    pool_pre_ping=True,
    pool_recycle=3600
)
```

## Troubleshooting

### Common Issues

#### Migration Errors
```bash
# Reset migration state (DANGER: Data loss)
alembic stamp head
alembic upgrade head
```

#### Database Connection Issues
```bash
# Test connection
python -c "
from sqlalchemy import create_engine
engine = create_engine('$DB_URL')
with engine.connect() as conn:
    print('Connection OK')
"
```

#### Performance Issues
- Check database indexes: `\di` in PostgreSQL
- Monitor connection pool usage
- Review slow query logs
- Check disk space and I/O

### Logs and Debugging

```bash
# Enable debug logging
export LOG_LEVEL=DEBUG

# View application logs
tail -f logs/voicestudio.log

# Database query logs
export SQLALCHEMY_ECHO=true
```

## Security Considerations

### Database Security
- Use strong passwords
- Enable SSL/TLS for PostgreSQL
- Restrict network access
- Regular security updates

### API Security
- Use HTTPS in production
- Implement rate limiting
- Validate all inputs
- Use environment variables for secrets

### Backup Security
- Encrypt backup files
- Store backups securely
- Test restore procedures
- Monitor backup success

## Maintenance

### Regular Tasks

#### Daily
- Monitor application health
- Check backup success
- Review error logs

#### Weekly
- Review performance metrics
- Update dependencies
- Clean old logs

#### Monthly
- Security updates
- Database maintenance
- Capacity planning

### Scaling Considerations

#### Horizontal Scaling
- Use load balancer
- Session affinity for WebSocket
- Shared database
- Redis for caching

#### Vertical Scaling
- Increase worker processes
- Optimize database queries
- Add more memory
- Use faster storage

## Support

For operational issues:
1. Check logs and metrics
2. Review this documentation
3. Test with minimal configuration
4. Contact development team

### Useful Commands

```bash
# Check system resources
htop
df -h
free -h

# Database size
psql -c "SELECT pg_size_pretty(pg_database_size('voicestudio'));"

# Active connections
psql -c "SELECT count(*) FROM pg_stat_activity WHERE datname='voicestudio';"

# Application status
curl -s http://localhost:8000/v1/health/metrics | jq
```
