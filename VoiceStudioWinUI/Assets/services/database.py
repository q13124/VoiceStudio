#!/usr/bin/env python3
"""
VoiceStudio Database Integration
Handles persistent data storage with SQLite and optional PostgreSQL support.
Optimized with connection pooling, async operations, and caching.
"""

import json
import logging
import sqlite3
import threading
import asyncio
import aiofiles
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
from contextlib import contextmanager
import os
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
import queue
import time

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
    """Manages database operations with connection pooling and async support"""

    def __init__(self, db_path: str = "voicestudio.db", pool_size: int = 10):
        self.db_path = db_path
        self.pool_size = pool_size
        self._lock = threading.Lock()
        self._connection_pool = queue.Queue(maxsize=pool_size)
        self._executor = ThreadPoolExecutor(max_workers=pool_size)
        self._cache = {}  # Simple in-memory cache
        self._cache_ttl = 300  # 5 minutes
        self._init_database()
        self._init_connection_pool()

    def _init_connection_pool(self):
        """Initialize connection pool"""
        for _ in range(self.pool_size):
            conn = sqlite3.connect(self.db_path, check_same_thread=False)
            conn.row_factory = sqlite3.Row
            conn.execute("PRAGMA journal_mode=WAL")  # Enable WAL mode for better concurrency
            conn.execute("PRAGMA synchronous=NORMAL")  # Balance safety and performance
            conn.execute("PRAGMA cache_size=10000")  # Increase cache size
            conn.execute("PRAGMA temp_store=MEMORY")  # Use memory for temp tables
            self._connection_pool.put(conn)
        logger.info(f"Connection pool initialized with {self.pool_size} connections")

    def _init_database(self):
        """Initialize database tables with optimized indexes and performance settings"""
        with self._get_connection() as conn:
            cursor = conn.cursor()

            # Optimize SQLite settings for better performance
            cursor.execute("PRAGMA journal_mode=WAL")
            cursor.execute("PRAGMA synchronous=NORMAL")
            cursor.execute("PRAGMA cache_size=10000")
            cursor.execute("PRAGMA temp_store=MEMORY")
            cursor.execute("PRAGMA mmap_size=268435456")  # 256MB memory mapping
            cursor.execute("PRAGMA optimize")

            # Service logs table with optimized indexes
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

            # Create composite indexes for better query performance
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_logs_service_timestamp ON service_logs(service_id, timestamp DESC)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_logs_level_timestamp ON service_logs(level, timestamp DESC)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_logs_timestamp ON service_logs(timestamp DESC)")

            # Service metrics table with optimized indexes
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

            # Create composite indexes for metrics queries
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_metrics_service_timestamp ON service_metrics(service_id, timestamp DESC)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_metrics_name_timestamp ON service_metrics(metric_name, timestamp DESC)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_metrics_timestamp ON service_metrics(timestamp DESC)")

            # Configuration table with optimized structure
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

            # Service registry table with optimized indexes
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

            # Create composite indexes for service registry
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_registry_name_status ON service_registry(service_name, status)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_registry_status_heartbeat ON service_registry(status, last_heartbeat)")

            # Performance monitoring table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS performance_metrics (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    service_id TEXT NOT NULL,
                    metric_type TEXT NOT NULL,
                    metric_value REAL NOT NULL,
                    timestamp DATETIME NOT NULL,
                    tags TEXT
                )
            """)

            cursor.execute("CREATE INDEX IF NOT EXISTS idx_perf_service_type ON performance_metrics(service_id, metric_type, timestamp DESC)")

            # Voice cloning tables
            self._create_voice_cloning_tables(cursor)

            conn.commit()
            logger.info("Database initialized successfully with optimized indexes, performance settings, and voice cloning tables")

    def _create_voice_cloning_tables(self, cursor):
        """Create voice cloning related tables"""

        # Voice profiles table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS voice_profiles (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                speaker_id TEXT UNIQUE NOT NULL,
                voice_embedding BLOB,
                pitch_contour TEXT,
                formant_frequencies TEXT,
                speaking_rate REAL,
                breathing_patterns TEXT,
                emotion_patterns TEXT,
                audio_length REAL,
                sample_rate INTEGER,
                extracted_at DATETIME NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # Create indexes for voice profiles
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_voice_profiles_speaker_id ON voice_profiles(speaker_id)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_voice_profiles_extracted_at ON voice_profiles(extracted_at DESC)")

        # Voice cloning sessions table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS voice_cloning_sessions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id TEXT UNIQUE NOT NULL,
                speaker_id TEXT,
                reference_audio_path TEXT,
                target_text TEXT,
                cloned_audio_path TEXT,
                model_type TEXT DEFAULT 'gpt_sovits',
                processing_mode TEXT DEFAULT 'standard',
                status TEXT DEFAULT 'processing',
                progress INTEGER DEFAULT 0,
                quality_score REAL,
                processing_time REAL,
                error_message TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                started_at TIMESTAMP,
                completed_at TIMESTAMP,
                metadata TEXT
            )
        """)

        # Create indexes for voice cloning sessions
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_voice_sessions_session_id ON voice_cloning_sessions(session_id)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_voice_sessions_speaker_id ON voice_cloning_sessions(speaker_id)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_voice_sessions_status ON voice_cloning_sessions(status)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_voice_sessions_created_at ON voice_cloning_sessions(created_at DESC)")

        # Voice models table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS voice_models (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                model_name TEXT UNIQUE NOT NULL,
                model_type TEXT NOT NULL,
                model_path TEXT,
                is_loaded BOOLEAN DEFAULT FALSE,
                last_used TIMESTAMP,
                performance_metrics TEXT,
                model_size_mb REAL,
                load_time_seconds REAL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # Create indexes for voice models
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_voice_models_name ON voice_models(model_name)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_voice_models_type ON voice_models(model_type)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_voice_models_loaded ON voice_models(is_loaded)")

        # Voice cloning results table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS voice_cloning_results (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id TEXT NOT NULL,
                speaker_id TEXT,
                reference_audio_hash TEXT,
                target_text_hash TEXT,
                cloned_audio_path TEXT,
                model_type TEXT NOT NULL,
                processing_time REAL NOT NULL,
                quality_score REAL,
                similarity_score REAL,
                audio_length REAL,
                sample_rate INTEGER,
                file_size_bytes INTEGER,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                metadata TEXT,
                FOREIGN KEY (session_id) REFERENCES voice_cloning_sessions(session_id)
            )
        """)

        # Create indexes for voice cloning results
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_voice_results_session_id ON voice_cloning_results(session_id)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_voice_results_speaker_id ON voice_cloning_results(speaker_id)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_voice_results_model_type ON voice_cloning_results(model_type)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_voice_results_created_at ON voice_cloning_results(created_at DESC)")

        # Voice cloning metrics table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS voice_cloning_metrics (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                service_id TEXT NOT NULL,
                metric_name TEXT NOT NULL,
                metric_value REAL NOT NULL,
                metric_type TEXT NOT NULL,
                timestamp DATETIME NOT NULL,
                tags TEXT,
                session_id TEXT,
                speaker_id TEXT,
                model_type TEXT
            )
        """)

        # Create indexes for voice cloning metrics
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_voice_metrics_service_name ON voice_cloning_metrics(service_id, metric_name, timestamp DESC)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_voice_metrics_type ON voice_cloning_metrics(metric_type, timestamp DESC)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_voice_metrics_timestamp ON voice_cloning_metrics(timestamp DESC)")

        logger.info("Voice cloning tables created successfully")

    @contextmanager
    def _get_connection(self):
        """Get database connection from pool with context manager"""
        conn = None
        try:
            conn = self._connection_pool.get(timeout=5)
            yield conn
        except queue.Empty:
            # Fallback to new connection if pool is empty
            conn = sqlite3.connect(self.db_path, check_same_thread=False)
            conn.row_factory = sqlite3.Row
            conn.execute("PRAGMA journal_mode=WAL")
            conn.execute("PRAGMA synchronous=NORMAL")
            conn.execute("PRAGMA cache_size=10000")
            conn.execute("PRAGMA temp_store=MEMORY")
            yield conn
        finally:
            if conn:
                try:
                    self._connection_pool.put_nowait(conn)
                except queue.Full:
                    conn.close()

    def _get_cache_key(self, operation: str, *args) -> str:
        """Generate cache key for operation"""
        return f"{operation}:{':'.join(str(arg) for arg in args)}"

    def _is_cache_valid(self, cache_entry: dict) -> bool:
        """Check if cache entry is still valid"""
        return time.time() - cache_entry['timestamp'] < self._cache_ttl

    def _get_from_cache(self, cache_key: str) -> Optional[Any]:
        """Get value from cache if valid"""
        if cache_key in self._cache:
            entry = self._cache[cache_key]
            if self._is_cache_valid(entry):
                return entry['value']
            else:
                del self._cache[cache_key]
        return None

    def _set_cache(self, cache_key: str, value: Any):
        """Set value in cache"""
        self._cache[cache_key] = {
            'value': value,
            'timestamp': time.time()
        }

    def log_service_event(self, service_id: str, service_name: str,
                         level: str, message: str, metadata: Dict = None):
        """Log a service event asynchronously"""
        def _log():
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

        # Execute in thread pool for non-blocking operation
        self._executor.submit(_log)

    def record_service_metric(self, service_id: str, service_name: str,
                             metric_name: str, metric_value: float, tags: Dict = None):
        """Record a service metric asynchronously"""
        def _record():
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

        # Execute in thread pool for non-blocking operation
        self._executor.submit(_record)

    def get_service_logs(self, service_id: str = None, limit: int = 100) -> List[ServiceLog]:
        """Get service logs with caching"""
        cache_key = self._get_cache_key("logs", service_id, limit)
        cached_result = self._get_from_cache(cache_key)
        if cached_result:
            return cached_result

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

            # Cache the result
            self._set_cache(cache_key, logs)
            return logs

    def get_service_metrics(self, service_id: str = None, metric_name: str = None,
                           limit: int = 100) -> List[ServiceMetric]:
        """Get service metrics with caching"""
        cache_key = self._get_cache_key("metrics", service_id, metric_name, limit)
        cached_result = self._get_from_cache(cache_key)
        if cached_result:
            return cached_result

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

            # Cache the result
            self._set_cache(cache_key, metrics)
            return metrics

    def set_configuration(self, key: str, value: str, service_name: str = "system"):
        """Set configuration value"""
        def _set():
            with self._get_connection() as conn:
                cursor = conn.cursor()
                now = datetime.now()

                cursor.execute("""
                    INSERT OR REPLACE INTO configurations
                    (key, value, service_name, created_at, updated_at)
                    VALUES (?, ?, ?, ?, ?)
                """, (key, value, service_name, now, now))

                conn.commit()

                # Invalidate cache for this key
                cache_key = self._get_cache_key("config", key)
                if cache_key in self._cache:
                    del self._cache[cache_key]

        self._executor.submit(_set)

    def get_configuration(self, key: str) -> Optional[str]:
        """Get configuration value with caching"""
        cache_key = self._get_cache_key("config", key)
        cached_result = self._get_from_cache(cache_key)
        if cached_result:
            return cached_result

        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT value FROM configurations WHERE key = ?", (key,))
            row = cursor.fetchone()
            value = row['value'] if row else None

            # Cache the result
            self._set_cache(cache_key, value)
            return value

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

    def batch_log_events(self, events: List[Dict[str, Any]]):
        """Batch log multiple events for better performance"""
        def _batch_log():
            with self._get_connection() as conn:
                cursor = conn.cursor()

                # Prepare batch insert
                batch_data = []
                for event in events:
                    batch_data.append((
                        event.get('service_id', 'unknown'),
                        event.get('service_name', 'Unknown Service'),
                        event.get('level', 'INFO'),
                        event.get('message', ''),
                        datetime.now(),
                        json.dumps(event.get('metadata', {}))
                    ))

                # Execute batch insert
                cursor.executemany("""
                    INSERT INTO service_logs
                    (service_id, service_name, level, message, timestamp, metadata)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, batch_data)

                conn.commit()
                logger.info(f"Batch logged {len(events)} events")

        self._executor.submit(_batch_log)

    def batch_record_metrics(self, metrics: List[Dict[str, Any]]):
        """Batch record multiple metrics for better performance"""
        def _batch_record():
            with self._get_connection() as conn:
                cursor = conn.cursor()

                # Prepare batch insert
                batch_data = []
                for metric in metrics:
                    batch_data.append((
                        metric.get('service_id', 'unknown'),
                        metric.get('service_name', 'Unknown Service'),
                        metric.get('metric_name', 'unknown'),
                        metric.get('metric_value', 0.0),
                        datetime.now(),
                        json.dumps(metric.get('tags', {}))
                    ))

                # Execute batch insert
                cursor.executemany("""
                    INSERT INTO service_metrics
                    (service_id, service_name, metric_name, metric_value, timestamp, tags)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, batch_data)

                conn.commit()
                logger.info(f"Batch recorded {len(metrics)} metrics")

        self._executor.submit(_batch_record)

    def get_performance_summary(self, service_id: str = None, hours: int = 24) -> Dict[str, Any]:
        """Get performance summary with optimized queries"""
        cache_key = self._get_cache_key("perf_summary", service_id, hours)
        cached_result = self._get_from_cache(cache_key)
        if cached_result:
            return cached_result

        with self._get_connection() as conn:
            cursor = conn.cursor()
            cutoff_time = datetime.now() - timedelta(hours=hours)

            # Get performance metrics
            if service_id:
                cursor.execute("""
                    SELECT metric_name, AVG(metric_value) as avg_value,
                           MIN(metric_value) as min_value, MAX(metric_value) as max_value,
                           COUNT(*) as count
                    FROM service_metrics
                    WHERE service_id = ? AND timestamp > ?
                    GROUP BY metric_name
                """, (service_id, cutoff_time))
            else:
                cursor.execute("""
                    SELECT metric_name, AVG(metric_value) as avg_value,
                           MIN(metric_value) as min_value, MAX(metric_value) as max_value,
                           COUNT(*) as count
                    FROM service_metrics
                    WHERE timestamp > ?
                    GROUP BY metric_name
                """, (cutoff_time,))

            metrics_summary = {}
            for row in cursor.fetchall():
                metrics_summary[row['metric_name']] = {
                    'average': row['avg_value'],
                    'minimum': row['min_value'],
                    'maximum': row['max_value'],
                    'count': row['count']
                }

            # Get log level distribution
            if service_id:
                cursor.execute("""
                    SELECT level, COUNT(*) as count
                    FROM service_logs
                    WHERE service_id = ? AND timestamp > ?
                    GROUP BY level
                """, (service_id, cutoff_time))
            else:
                cursor.execute("""
                    SELECT level, COUNT(*) as count
                    FROM service_logs
                    WHERE timestamp > ?
                    GROUP BY level
                """, (cutoff_time,))

            log_distribution = {}
            for row in cursor.fetchall():
                log_distribution[row['level']] = row['count']

            summary = {
                'metrics_summary': metrics_summary,
                'log_distribution': log_distribution,
                'time_range_hours': hours,
                'generated_at': datetime.now().isoformat()
            }

            # Cache the result
            self._set_cache(cache_key, summary)
            return summary

    def cleanup_old_data(self, days: int = 30):
        """Clean up old logs and metrics asynchronously with optimized queries"""
        def _cleanup():
            cutoff_date = datetime.now() - timedelta(days=days)

            with self._get_connection() as conn:
                cursor = conn.cursor()

                # Clean up old logs with optimized query
                cursor.execute("""
                    DELETE FROM service_logs
                    WHERE timestamp < ?
                """, (cutoff_date,))
                logs_deleted = cursor.rowcount

                # Clean up old metrics with optimized query
                cursor.execute("""
                    DELETE FROM service_metrics
                    WHERE timestamp < ?
                """, (cutoff_date,))
                metrics_deleted = cursor.rowcount

                # Clean up old performance metrics
                cursor.execute("""
                    DELETE FROM performance_metrics
                    WHERE timestamp < ?
                """, (cutoff_date,))
                perf_deleted = cursor.rowcount

                conn.commit()
                logger.info(f"Cleaned up {logs_deleted} logs, {metrics_deleted} metrics, {perf_deleted} performance records older than {days} days")

                # Clear cache after cleanup
                self._cache.clear()

        self._executor.submit(_cleanup)

    # Voice Cloning Database Methods

    def save_voice_profile(self, speaker_id: str, voice_profile: Dict[str, Any]):
        """Save voice profile to database"""
        def _save():
            with self._get_connection() as conn:
                cursor = conn.cursor()

                # Convert voice profile to JSON for storage
                voice_embedding = json.dumps(voice_profile.get('speaker_embedding', []).tolist()) if 'speaker_embedding' in voice_profile else None
                pitch_contour = json.dumps(voice_profile.get('pitch_contour', {}))
                formant_frequencies = json.dumps(voice_profile.get('formant_frequencies', {}))
                breathing_patterns = json.dumps(voice_profile.get('breathing_patterns', {}))
                emotion_patterns = json.dumps(voice_profile.get('emotion_patterns', {}))

                cursor.execute("""
                    INSERT OR REPLACE INTO voice_profiles
                    (speaker_id, voice_embedding, pitch_contour, formant_frequencies,
                     speaking_rate, breathing_patterns, emotion_patterns, audio_length,
                     sample_rate, extracted_at, updated_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    speaker_id,
                    voice_embedding,
                    pitch_contour,
                    formant_frequencies,
                    voice_profile.get('speaking_rate', 0.0),
                    breathing_patterns,
                    emotion_patterns,
                    voice_profile.get('audio_length', 0.0),
                    voice_profile.get('sample_rate', 22050),
                    voice_profile.get('extracted_at', datetime.now().isoformat()),
                    datetime.now()
                ))

                conn.commit()
                logger.info(f"Voice profile saved for speaker {speaker_id}")

        self._executor.submit(_save)

    def get_voice_profile(self, speaker_id: str) -> Optional[Dict[str, Any]]:
        """Get voice profile from database"""
        cache_key = self._get_cache_key("voice_profile", speaker_id)
        cached_result = self._get_from_cache(cache_key)
        if cached_result:
            return cached_result

        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT * FROM voice_profiles WHERE speaker_id = ?
            """, (speaker_id,))

            row = cursor.fetchone()
            if row:
                profile = {
                    'speaker_id': row['speaker_id'],
                    'voice_embedding': json.loads(row['voice_embedding']) if row['voice_embedding'] else [],
                    'pitch_contour': json.loads(row['pitch_contour']) if row['pitch_contour'] else {},
                    'formant_frequencies': json.loads(row['formant_frequencies']) if row['formant_frequencies'] else {},
                    'speaking_rate': row['speaking_rate'],
                    'breathing_patterns': json.loads(row['breathing_patterns']) if row['breathing_patterns'] else {},
                    'emotion_patterns': json.loads(row['emotion_patterns']) if row['emotion_patterns'] else {},
                    'audio_length': row['audio_length'],
                    'sample_rate': row['sample_rate'],
                    'extracted_at': row['extracted_at']
                }

                # Cache the result
                self._set_cache(cache_key, profile)
                return profile

        return None

    def save_voice_cloning_session(self, session_id: str, speaker_id: str,
                                  reference_audio_path: str, target_text: str,
                                  model_type: str = "gpt_sovits",
                                  processing_mode: str = "standard"):
        """Save voice cloning session to database"""
        def _save():
            with self._get_connection() as conn:
                cursor = conn.cursor()

                cursor.execute("""
                    INSERT INTO voice_cloning_sessions
                    (session_id, speaker_id, reference_audio_path, target_text,
                     model_type, processing_mode, status, created_at, started_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    session_id,
                    speaker_id,
                    reference_audio_path,
                    target_text,
                    model_type,
                    processing_mode,
                    "processing",
                    datetime.now(),
                    datetime.now()
                ))

                conn.commit()
                logger.info(f"Voice cloning session saved: {session_id}")

        self._executor.submit(_save)

    def update_voice_cloning_session(self, session_id: str, status: str,
                                   progress: int = None, error_message: str = None,
                                   cloned_audio_path: str = None,
                                   processing_time: float = None,
                                   quality_score: float = None):
        """Update voice cloning session status"""
        def _update():
            with self._get_connection() as conn:
                cursor = conn.cursor()

                # Build update query dynamically
                updates = ["status = ?"]
                params = [status]

                if progress is not None:
                    updates.append("progress = ?")
                    params.append(progress)

                if error_message is not None:
                    updates.append("error_message = ?")
                    params.append(error_message)

                if cloned_audio_path is not None:
                    updates.append("cloned_audio_path = ?")
                    params.append(cloned_audio_path)

                if processing_time is not None:
                    updates.append("processing_time = ?")
                    params.append(processing_time)

                if quality_score is not None:
                    updates.append("quality_score = ?")
                    params.append(quality_score)

                # Set completion time if status is completed or failed
                if status in ["completed", "failed"]:
                    updates.append("completed_at = ?")
                    params.append(datetime.now())

                params.append(session_id)

                query = f"UPDATE voice_cloning_sessions SET {', '.join(updates)} WHERE session_id = ?"
                cursor.execute(query, params)

                conn.commit()
                logger.info(f"Voice cloning session updated: {session_id} -> {status}")

        self._executor.submit(_update)

    def get_voice_cloning_session(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Get voice cloning session from database"""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT * FROM voice_cloning_sessions WHERE session_id = ?
            """, (session_id,))

            row = cursor.fetchone()
            if row:
                return dict(row)

        return None

    def save_voice_cloning_result(self, session_id: str, speaker_id: str,
                                 cloned_audio_path: str, model_type: str,
                                 processing_time: float, quality_score: float = None,
                                 similarity_score: float = None, metadata: Dict = None):
        """Save voice cloning result to database"""
        def _save():
            with self._get_connection() as conn:
                cursor = conn.cursor()

                # Get audio file info
                try:
                    audio_path = Path(cloned_audio_path)
                    file_size = audio_path.stat().st_size if audio_path.exists() else 0
                except:
                    file_size = 0

                cursor.execute("""
                    INSERT INTO voice_cloning_results
                    (session_id, speaker_id, cloned_audio_path, model_type,
                     processing_time, quality_score, similarity_score,
                     file_size_bytes, metadata, created_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    session_id,
                    speaker_id,
                    cloned_audio_path,
                    model_type,
                    processing_time,
                    quality_score,
                    similarity_score,
                    file_size,
                    json.dumps(metadata or {}),
                    datetime.now()
                ))

                conn.commit()
                logger.info(f"Voice cloning result saved for session {session_id}")

        self._executor.submit(_save)

    def get_voice_cloning_results(self, speaker_id: str = None,
                                 model_type: str = None, limit: int = 100) -> List[Dict[str, Any]]:
        """Get voice cloning results from database"""
        with self._get_connection() as conn:
            cursor = conn.cursor()

            query = "SELECT * FROM voice_cloning_results WHERE 1=1"
            params = []

            if speaker_id:
                query += " AND speaker_id = ?"
                params.append(speaker_id)

            if model_type:
                query += " AND model_type = ?"
                params.append(model_type)

            query += " ORDER BY created_at DESC LIMIT ?"
            params.append(limit)

            cursor.execute(query, params)
            rows = cursor.fetchall()

            results = []
            for row in rows:
                result = dict(row)
                if result['metadata']:
                    result['metadata'] = json.loads(result['metadata'])
                results.append(result)

            return results

    def record_voice_cloning_metric(self, service_id: str, metric_name: str,
                                   metric_value: float, metric_type: str,
                                   session_id: str = None, speaker_id: str = None,
                                   model_type: str = None, tags: Dict = None):
        """Record voice cloning specific metric"""
        def _record():
            with self._get_connection() as conn:
                cursor = conn.cursor()

                cursor.execute("""
                    INSERT INTO voice_cloning_metrics
                    (service_id, metric_name, metric_value, metric_type,
                     timestamp, tags, session_id, speaker_id, model_type)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    service_id,
                    metric_name,
                    metric_value,
                    metric_type,
                    datetime.now(),
                    json.dumps(tags or {}),
                    session_id,
                    speaker_id,
                    model_type
                ))

                conn.commit()

        self._executor.submit(_record)

    def get_voice_cloning_metrics_summary(self, service_id: str = None,
                                        hours: int = 24) -> Dict[str, Any]:
        """Get voice cloning metrics summary"""
        cache_key = self._get_cache_key("voice_cloning_metrics", service_id, hours)
        cached_result = self._get_from_cache(cache_key)
        if cached_result:
            return cached_result

        with self._get_connection() as conn:
            cursor = conn.cursor()
            cutoff_time = datetime.now() - timedelta(hours=hours)

            # Get voice cloning metrics
            if service_id:
                cursor.execute("""
                    SELECT metric_name, AVG(metric_value) as avg_value,
                           MIN(metric_value) as min_value, MAX(metric_value) as max_value,
                           COUNT(*) as count
                    FROM voice_cloning_metrics
                    WHERE service_id = ? AND timestamp > ?
                    GROUP BY metric_name
                """, (service_id, cutoff_time))
            else:
                cursor.execute("""
                    SELECT metric_name, AVG(metric_value) as avg_value,
                           MIN(metric_value) as min_value, MAX(metric_value) as max_value,
                           COUNT(*) as count
                    FROM voice_cloning_metrics
                    WHERE timestamp > ?
                    GROUP BY metric_name
                """, (cutoff_time,))

            metrics_summary = {}
            for row in cursor.fetchall():
                metrics_summary[row['metric_name']] = {
                    'average': row['avg_value'],
                    'minimum': row['min_value'],
                    'maximum': row['max_value'],
                    'count': row['count']
                }

            # Get session statistics
            cursor.execute("""
                SELECT status, COUNT(*) as count
                FROM voice_cloning_sessions
                WHERE created_at > ?
                GROUP BY status
            """, (cutoff_time,))

            session_stats = {}
            for row in cursor.fetchall():
                session_stats[row['status']] = row['count']

            summary = {
                'metrics_summary': metrics_summary,
                'session_stats': session_stats,
                'time_range_hours': hours,
                'generated_at': datetime.now().isoformat()
            }

            # Cache the result
            self._set_cache(cache_key, summary)
            return summary

    def close(self):
        """Close database manager and cleanup resources"""
        self._executor.shutdown(wait=True)

        # Close all connections in pool
        while not self._connection_pool.empty():
            try:
                conn = self._connection_pool.get_nowait()
                conn.close()
            except queue.Empty:
                break

        logger.info("Database manager closed")

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

# Voice Cloning Database Convenience Functions

def save_voice_profile(speaker_id: str, voice_profile: Dict[str, Any]):
    """Save voice profile to database"""
    db_manager.save_voice_profile(speaker_id, voice_profile)

def get_voice_profile(speaker_id: str) -> Optional[Dict[str, Any]]:
    """Get voice profile from database"""
    return db_manager.get_voice_profile(speaker_id)

def save_voice_cloning_session(session_id: str, speaker_id: str,
                              reference_audio_path: str, target_text: str,
                              model_type: str = "gpt_sovits",
                              processing_mode: str = "standard"):
    """Save voice cloning session to database"""
    db_manager.save_voice_cloning_session(session_id, speaker_id, reference_audio_path,
                                         target_text, model_type, processing_mode)

def update_voice_cloning_session(session_id: str, status: str,
                                progress: int = None, error_message: str = None,
                                cloned_audio_path: str = None,
                                processing_time: float = None,
                                quality_score: float = None):
    """Update voice cloning session status"""
    db_manager.update_voice_cloning_session(session_id, status, progress, error_message,
                                           cloned_audio_path, processing_time, quality_score)

def get_voice_cloning_session(session_id: str) -> Optional[Dict[str, Any]]:
    """Get voice cloning session from database"""
    return db_manager.get_voice_cloning_session(session_id)

def save_voice_cloning_result(session_id: str, speaker_id: str,
                             cloned_audio_path: str, model_type: str,
                             processing_time: float, quality_score: float = None,
                             similarity_score: float = None, metadata: Dict = None):
    """Save voice cloning result to database"""
    db_manager.save_voice_cloning_result(session_id, speaker_id, cloned_audio_path,
                                        model_type, processing_time, quality_score,
                                        similarity_score, metadata)

def get_voice_cloning_results(speaker_id: str = None,
                             model_type: str = None, limit: int = 100) -> List[Dict[str, Any]]:
    """Get voice cloning results from database"""
    return db_manager.get_voice_cloning_results(speaker_id, model_type, limit)

def record_voice_cloning_metric(service_id: str, metric_name: str,
                               metric_value: float, metric_type: str,
                               session_id: str = None, speaker_id: str = None,
                               model_type: str = None, tags: Dict = None):
    """Record voice cloning specific metric"""
    db_manager.record_voice_cloning_metric(service_id, metric_name, metric_value, metric_type,
                                          session_id, speaker_id, model_type, tags)

def get_voice_cloning_metrics_summary(service_id: str = None,
                                     hours: int = 24) -> Dict[str, Any]:
    """Get voice cloning metrics summary"""
    return db_manager.get_voice_cloning_metrics_summary(service_id, hours)

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
