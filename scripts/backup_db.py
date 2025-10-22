#!/usr/bin/env python3
"""
VoiceStudio Database Backup Script

Supports both SQLite and PostgreSQL backups with compression and retention.
"""

import os
import sys
import subprocess
import argparse
import gzip
import shutil
from datetime import datetime, timedelta
from pathlib import Path
from urllib.parse import urlparse

def backup_sqlite(db_path: str, backup_dir: Path, compress: bool = True) -> str:
    """Backup SQLite database"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_name = f"voicestudio_sqlite_{timestamp}.db"
    backup_path = backup_dir / backup_name
    
    # Copy SQLite file
    shutil.copy2(db_path, backup_path)
    
    if compress:
        compressed_path = backup_path.with_suffix(".db.gz")
        with open(backup_path, 'rb') as f_in:
            with gzip.open(compressed_path, 'wb') as f_out:
                shutil.copyfileobj(f_in, f_out)
        backup_path.unlink()  # Remove uncompressed file
        backup_path = compressed_path
    
    return str(backup_path)

def backup_postgres(db_url: str, backup_dir: Path, compress: bool = True) -> str:
    """Backup PostgreSQL database using pg_dump"""
    parsed = urlparse(db_url)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_name = f"voicestudio_postgres_{timestamp}.sql"
    backup_path = backup_dir / backup_name
    
    # Build pg_dump command
    cmd = [
        "pg_dump",
        f"--host={parsed.hostname or 'localhost'}",
        f"--port={parsed.port or '5432'}",
        f"--username={parsed.username}",
        f"--dbname={parsed.path.lstrip('/')}",
        "--no-password",  # Use PGPASSWORD env var
        "--verbose",
        "--clean",
        "--if-exists",
        "--create",
    ]
    
    # Set password from URL if present
    env = os.environ.copy()
    if parsed.password:
        env["PGPASSWORD"] = parsed.password
    
    # Run pg_dump
    with open(backup_path, 'w') as f:
        result = subprocess.run(cmd, stdout=f, stderr=subprocess.PIPE, env=env)
        if result.returncode != 0:
            raise RuntimeError(f"pg_dump failed: {result.stderr.decode()}")
    
    if compress:
        compressed_path = backup_path.with_suffix(".sql.gz")
        with open(backup_path, 'rb') as f_in:
            with gzip.open(compressed_path, 'wb') as f_out:
                shutil.copyfileobj(f_in, f_out)
        backup_path.unlink()  # Remove uncompressed file
        backup_path = compressed_path
    
    return str(backup_path)

def cleanup_old_backups(backup_dir: Path, retention_days: int = 7):
    """Remove backup files older than retention_days"""
    cutoff_date = datetime.now() - timedelta(days=retention_days)
    
    for backup_file in backup_dir.glob("voicestudio_*"):
        if backup_file.stat().st_mtime < cutoff_date.timestamp():
            print(f"Removing old backup: {backup_file}")
            backup_file.unlink()

def main():
    parser = argparse.ArgumentParser(description="Backup VoiceStudio database")
    parser.add_argument("--db-url", help="Database URL (overrides DB_URL env var)")
    parser.add_argument("--backup-dir", default="./backups", help="Backup directory")
    parser.add_argument("--no-compress", action="store_true", help="Don't compress backups")
    parser.add_argument("--retention-days", type=int, default=7, help="Days to retain backups")
    parser.add_argument("--dry-run", action="store_true", help="Show what would be done")
    
    args = parser.parse_args()
    
    # Get database URL
    db_url = args.db_url or os.getenv("DB_URL")
    if not db_url:
        print("Error: No database URL provided. Set DB_URL env var or use --db-url")
        sys.exit(1)
    
    # Create backup directory
    backup_dir = Path(args.backup_dir)
    backup_dir.mkdir(parents=True, exist_ok=True)
    
    if args.dry_run:
        print(f"Would backup database: {db_url}")
        print(f"Would save to: {backup_dir}")
        print(f"Compression: {'disabled' if args.no_compress else 'enabled'}")
        print(f"Retention: {args.retention_days} days")
        return
    
    try:
        # Determine database type and backup
        if db_url.startswith(("postgresql://", "postgresql+psycopg://")):
            backup_path = backup_postgres(db_url, backup_dir, not args.no_compress)
            print(f"PostgreSQL backup completed: {backup_path}")
        elif db_url.startswith("sqlite:///"):
            db_path = db_url.replace("sqlite:///", "")
            backup_path = backup_sqlite(db_path, backup_dir, not args.no_compress)
            print(f"SQLite backup completed: {backup_path}")
        else:
            print(f"Error: Unsupported database URL format: {db_url}")
            sys.exit(1)
        
        # Cleanup old backups
        cleanup_old_backups(backup_dir, args.retention_days)
        
        print(f"Backup completed successfully: {backup_path}")
        
    except Exception as e:
        print(f"Backup failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
