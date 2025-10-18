#!/usr/bin/env python3
"""
VoiceStudio Database Integration
Handles persistent data storage with SQLite and optional PostgreSQL support.
"""

import json
import logging
import sqlite3
import threading
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
from contextlib import contextmanager
import os

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class ServiceLog:
    """Service log entry"""
    id: Optional[int]
    service_id: str
    service_name: str
    level: str
    message: str
    timestamp: datetime
    metadata: Dict = None
    
    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}

@dataclass
class ServiceMetric:
    """Service performance metric"""
    id: Optional[int]
    service_id: str
    service_name: str
    metric_name: str
    metric_value: float
    timestamp: datetime
    tags: Dict = None
    
    def __post_init__(self):
        if self.tags is None:
            self.tags = {}

@dataclass
class Configuration:
    """Configuration entry"""
    id: Optional[int]
    key: str
    value: str
    service_name: str
    created_at: datetime
    updated_at: datetime

class DatabaseManager:
    """Manages database operations"""
    
    def __init__(self, db_path: str = "voicestudio.db"):
        self.db_path = db_path
        self._lock = threading.Lock()
        self._init_database()
    
    def _init_database(self):
        """Initialize database tables"""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            
            # Service logs table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS service_logs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    service_id TEXT NOT NULL,
                    service_name TEXT NOT NULL,
                    level TEXT NOT NULL,
                    message TEXT NOT NULL,
                    timestamp DATETIME NOT NULL,
                    metadata TEXT
                )
            """)
            
            # Service metrics table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS service_metrics (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    service_id TEXT NOT NULL,
                    service_name TEXT NOT NULL,
                    metric_name TEXT NOT NULL,
                    metric_value REAL NOT NULL,
                    timestamp DATETIME NOT NULL,
                    tags TEXT
                )
            """)
            
            # Configuration table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS configurations (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    key TEXT UNIQUE NOT NULL,
                    value TEXT NOT NULL,
                    service_name TEXT NOT NULL,
                    created_at DATETIME NOT NULL,
                    updated_at DATETIME NOT NULL
                )
            """)
            
            # Service registry table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS service_registry (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    service_id TEXT UNIQUE NOT NULL,
                    service_name TEXT NOT NULL,
                    host TEXT NOT NULL,
                    port INTEGER NOT NULL,
                    health_endpoint TEXT NOT NULL,
                    status TEXT NOT NULL,
                    last_heartbeat DATETIME,
                    metadata TEXT,
                    created_at DATETIME NOT NULL,
                    updated_at DATETIME NOT NULL
                )
            """)
            
            conn.commit()
            logger.info("Database initialized successfully")
    
    @contextmanager
    def _get_connection(self):
        """Get database connection with context manager"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        try:
            yield conn
        finally:
            conn.close()
    
    def log_service_event(self, service_id: str, service_name: str, 
                         level: str, message: str, metadata: Dict = None):
        """Log a service event"""
        with self._lock:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT INTO service_logs 
                    (service_id, service_name, level, message, timestamp, metadata)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, (
                    service_id, service_name, level, message, 
                    datetime.now(), json.dumps(metadata or {})
                ))
                conn.commit()
    
    def record_service_metric(self, service_id: str, service_name: str,
                             metric_name: str, metric_value: float, tags: Dict = None):
        """Record a service metric"""
        with self._lock:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT INTO service_metrics 
                    (service_id, service_name, metric_name, metric_value, timestamp, tags)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, (
                    service_id, service_name, metric_name, metric_value,
                    datetime.now(), json.dumps(tags or {})
                ))
                conn.commit()
    
    def get_service_logs(self, service_id: str = None, limit: int = 100) -> List[ServiceLog]:
        """Get service logs"""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            
            if service_id:
                cursor.execute("""
                    SELECT * FROM service_logs 
                    WHERE service_id = ? 
                    ORDER BY timestamp DESC 
                    LIMIT ?
                """, (service_id, limit))
            else:
                cursor.execute("""
                    SELECT * FROM service_logs 
                    ORDER BY timestamp DESC 
                    LIMIT ?
                """, (limit,))
            
            rows = cursor.fetchall()
            logs = []
            for row in rows:
                logs.append(ServiceLog(
                    id=row['id'],
                    service_id=row['service_id'],
                    service_name=row['service_name'],
                    level=row['level'],
                    message=row['message'],
                    timestamp=datetime.fromisoformat(row['timestamp']),
                    metadata=json.loads(row['metadata'] or '{}')
                ))
            
            return logs
    
    def get_service_metrics(self, service_id: str = None, metric_name: str = None,
                           limit: int = 100) -> List[ServiceMetric]:
        """Get service metrics"""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            
            query = "SELECT * FROM service_metrics WHERE 1=1"
            params = []
            
            if service_id:
                query += " AND service_id = ?"
                params.append(service_id)
            
            if metric_name:
                query += " AND metric_name = ?"
                params.append(metric_name)
            
            query += " ORDER BY timestamp DESC LIMIT ?"
            params.append(limit)
            
            cursor.execute(query, params)
            rows = cursor.fetchall()
            
            metrics = []
            for row in rows:
                metrics.append(ServiceMetric(
                    id=row['id'],
                    service_id=row['service_id'],
                    service_name=row['service_name'],
                    metric_name=row['metric_name'],
                    metric_value=row['metric_value'],
                    timestamp=datetime.fromisoformat(row['timestamp']),
                    tags=json.loads(row['tags'] or '{}')
                ))
            
            return metrics
    
    def set_configuration(self, key: str, value: str, service_name: str = "system"):
        """Set configuration value"""
        with self._lock:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                now = datetime.now()
                
                cursor.execute("""
                    INSERT OR REPLACE INTO configurations 
                    (key, value, service_name, created_at, updated_at)
                    VALUES (?, ?, ?, ?, ?)
                """, (key, value, service_name, now, now))
                
                conn.commit()
    
    def get_configuration(self, key: str) -> Optional[str]:
        """Get configuration value"""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT value FROM configurations WHERE key = ?", (key,))
            row = cursor.fetchone()
            return row['value'] if row else None
    
    def get_all_configurations(self) -> List[Configuration]:
        """Get all configurations"""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM configurations ORDER BY key")
            rows = cursor.fetchall()
            
            configs = []
            for row in rows:
                configs.append(Configuration(
                    id=row['id'],
                    key=row['key'],
                    value=row['value'],
                    service_name=row['service_name'],
                    created_at=datetime.fromisoformat(row['created_at']),
                    updated_at=datetime.fromisoformat(row['updated_at'])
                ))
            
            return configs
    
    def cleanup_old_data(self, days: int = 30):
        """Clean up old logs and metrics"""
        with self._lock:
            cutoff_date = datetime.now() - timedelta(days=days)
            
            with self._get_connection() as conn:
                cursor = conn.cursor()
                
                # Clean up old logs
                cursor.execute("""
                    DELETE FROM service_logs 
                    WHERE timestamp < ?
                """, (cutoff_date,))
                
                # Clean up old metrics
                cursor.execute("""
                    DELETE FROM service_metrics 
                    WHERE timestamp < ?
                """, (cutoff_date,))
                
                conn.commit()
                logger.info(f"Cleaned up data older than {days} days")

class DatabaseLogger:
    """Logger that writes to database"""
    
    def __init__(self, db_manager: DatabaseManager, service_id: str, service_name: str):
        self.db_manager = db_manager
        self.service_id = service_id
        self.service_name = service_name
    
    def log(self, level: str, message: str, metadata: Dict = None):
        """Log a message to database"""
        self.db_manager.log_service_event(
            self.service_id, self.service_name, level, message, metadata
        )
    
    def info(self, message: str, metadata: Dict = None):
        """Log info message"""
        self.log("INFO", message, metadata)
    
    def warning(self, message: str, metadata: Dict = None):
        """Log warning message"""
        self.log("WARNING", message, metadata)
    
    def error(self, message: str, metadata: Dict = None):
        """Log error message"""
        self.log("ERROR", message, metadata)

# Global database manager instance
db_manager = DatabaseManager()

def get_database_logger(service_id: str, service_name: str) -> DatabaseLogger:
    """Get database logger for service"""
    return DatabaseLogger(db_manager, service_id, service_name)

def record_metric(service_id: str, service_name: str, metric_name: str, 
                 metric_value: float, tags: Dict = None):
    """Record a service metric"""
    db_manager.record_service_metric(service_id, service_name, metric_name, metric_value, tags)

if __name__ == "__main__":
    # Example usage
    logger.info("Database system initialized")
    
    # Test logging
    db_logger = get_database_logger("test-service", "Test Service")
    db_logger.info("Test log message", {"test": True})
    
    # Test metrics
    record_metric("test-service", "Test Service", "response_time", 0.5, {"endpoint": "/health"})
    
    # Test configuration
    db_manager.set_configuration("test_key", "test_value", "test-service")
    value = db_manager.get_configuration("test_key")
    logger.info(f"Configuration value: {value}")
    
    # Test cleanup
    db_manager.cleanup_old_data(1)
