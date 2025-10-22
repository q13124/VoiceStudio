"""
VoiceStudio WebSocket Progress Updates
Implements real-time progress updates for async jobs via WebSocket
"""

import asyncio
import json
import time
import uuid
from datetime import datetime
from typing import Dict, List, Optional, Any, Set
from dataclasses import dataclass, asdict
from enum import Enum
import threading
from collections import defaultdict

try:
    from fastapi import WebSocket, WebSocketDisconnect
    from fastapi.websockets import WebSocketState

    FASTAPI_AVAILABLE = True
except ImportError:
    FASTAPI_AVAILABLE = False
    print("Warning: FastAPI not available, WebSocket support disabled")


class JobStatus(Enum):
    """Job status enumeration"""

    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


@dataclass
class JobProgress:
    """Job progress information"""

    job_id: str
    status: JobStatus
    progress_percent: float  # 0-100
    message: str
    engine_id: Optional[str] = None
    estimated_completion: Optional[datetime] = None
    error_message: Optional[str] = None
    result_data: Optional[Dict[str, Any]] = None
    timestamp: datetime = None

    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now()


class WebSocketManager:
    """Manages WebSocket connections and job progress updates"""

    def __init__(self):
        self.active_connections: Dict[str, WebSocket] = {}
        self.job_subscribers: Dict[str, Set[str]] = defaultdict(
            set
        )  # job_id -> connection_ids
        self.connection_jobs: Dict[str, Set[str]] = defaultdict(
            set
        )  # connection_id -> job_ids
        self.job_progress: Dict[str, JobProgress] = {}
        self._lock = threading.Lock()

    async def connect(self, websocket: WebSocket, connection_id: str):
        """Accept a WebSocket connection"""
        if not FASTAPI_AVAILABLE:
            return False

        try:
            await websocket.accept()
            with self._lock:
                self.active_connections[connection_id] = websocket
            return True
        except Exception as e:
            print(f"WebSocket connection failed: {e}")
            return False

    def disconnect(self, connection_id: str):
        """Remove a WebSocket connection"""
        with self._lock:
            if connection_id in self.active_connections:
                del self.active_connections[connection_id]

            # Clean up job subscriptions
            if connection_id in self.connection_jobs:
                for job_id in self.connection_jobs[connection_id]:
                    self.job_subscribers[job_id].discard(connection_id)
                    if not self.job_subscribers[job_id]:
                        del self.job_subscribers[job_id]
                del self.connection_jobs[connection_id]

    def subscribe_to_job(self, connection_id: str, job_id: str):
        """Subscribe a connection to job progress updates"""
        with self._lock:
            if connection_id in self.active_connections:
                self.job_subscribers[job_id].add(connection_id)
                self.connection_jobs[connection_id].add(job_id)
                return True
            return False

    def unsubscribe_from_job(self, connection_id: str, job_id: str):
        """Unsubscribe a connection from job progress updates"""
        with self._lock:
            self.job_subscribers[job_id].discard(connection_id)
            self.connection_jobs[connection_id].discard(job_id)

            if not self.job_subscribers[job_id]:
                del self.job_subscribers[job_id]

    async def send_progress_update(self, job_id: str, progress: JobProgress):
        """Send progress update to all subscribers of a job"""
        if not FASTAPI_AVAILABLE:
            return

        with self._lock:
            self.job_progress[job_id] = progress
            subscribers = self.job_subscribers.get(job_id, set()).copy()

        if not subscribers:
            return

        message = {
            "type": "job_progress",
            "job_id": job_id,
            "progress": asdict(progress),
            "timestamp": progress.timestamp.isoformat(),
        }

        # Send to all subscribers
        disconnected = []
        for connection_id in subscribers:
            try:
                websocket = self.active_connections.get(connection_id)
                if websocket and websocket.client_state == WebSocketState.CONNECTED:
                    await websocket.send_text(json.dumps(message))
                else:
                    disconnected.append(connection_id)
            except Exception as e:
                print(f"Failed to send progress update to {connection_id}: {e}")
                disconnected.append(connection_id)

        # Clean up disconnected connections
        if disconnected:
            with self._lock:
                for conn_id in disconnected:
                    self.disconnect(conn_id)

    async def send_broadcast_update(self, message: Dict[str, Any]):
        """Send a message to all connected clients"""
        if not FASTAPI_AVAILABLE:
            return

        with self._lock:
            connections = list(self.active_connections.keys())

        disconnected = []
        for connection_id in connections:
            try:
                websocket = self.active_connections.get(connection_id)
                if websocket and websocket.client_state == WebSocketState.CONNECTED:
                    await websocket.send_text(json.dumps(message))
                else:
                    disconnected.append(connection_id)
            except Exception as e:
                print(f"Failed to send broadcast to {connection_id}: {e}")
                disconnected.append(connection_id)

        # Clean up disconnected connections
        if disconnected:
            with self._lock:
                for conn_id in disconnected:
                    self.disconnect(conn_id)

    def get_job_progress(self, job_id: str) -> Optional[JobProgress]:
        """Get current progress for a job"""
        with self._lock:
            return self.job_progress.get(job_id)

    def get_active_jobs(self) -> List[str]:
        """Get list of active job IDs"""
        with self._lock:
            return [
                job_id
                for job_id, progress in self.job_progress.items()
                if progress.status in [JobStatus.PENDING, JobStatus.PROCESSING]
            ]

    def get_connection_count(self) -> int:
        """Get number of active connections"""
        with self._lock:
            return len(self.active_connections)


class AsyncJobManager:
    """Manages async job execution with progress updates"""

    def __init__(self, websocket_manager: WebSocketManager):
        self.websocket_manager = websocket_manager
        self.job_queue = asyncio.Queue()
        self.active_jobs: Dict[str, asyncio.Task] = {}
        self.max_concurrent_jobs = 5
        self._worker_tasks: List[asyncio.Task] = []
        self._shutdown = False

    async def start_workers(self):
        """Start background workers to process jobs"""
        for i in range(self.max_concurrent_jobs):
            task = asyncio.create_task(self._worker(f"worker-{i}"))
            self._worker_tasks.append(task)

    async def stop_workers(self):
        """Stop background workers"""
        self._shutdown = True

        # Cancel all active jobs
        for job_id, task in self.active_jobs.items():
            task.cancel()

        # Wait for workers to finish
        if self._worker_tasks:
            await asyncio.gather(*self._worker_tasks, return_exceptions=True)

    async def submit_job(self, job_id: str, job_data: Dict[str, Any]) -> str:
        """Submit a job for async processing"""
        job_info = {"job_id": job_id, "data": job_data, "submitted_at": datetime.now()}

        await self.job_queue.put(job_info)

        # Send initial progress update
        progress = JobProgress(
            job_id=job_id,
            status=JobStatus.PENDING,
            progress_percent=0.0,
            message="Job queued for processing",
        )
        await self.websocket_manager.send_progress_update(job_id, progress)

        return job_id

    async def _worker(self, worker_name: str):
        """Background worker to process jobs"""
        while not self._shutdown:
            try:
                # Get job from queue
                job_info = await asyncio.wait_for(self.job_queue.get(), timeout=1.0)
                job_id = job_info["job_id"]
                job_data = job_info["data"]

                # Create task for job processing
                task = asyncio.create_task(self._process_job(job_id, job_data))
                self.active_jobs[job_id] = task

                try:
                    await task
                except asyncio.CancelledError:
                    # Job was cancelled
                    progress = JobProgress(
                        job_id=job_id,
                        status=JobStatus.CANCELLED,
                        progress_percent=100.0,
                        message="Job cancelled",
                    )
                    await self.websocket_manager.send_progress_update(job_id, progress)
                except Exception as e:
                    # Job failed
                    progress = JobProgress(
                        job_id=job_id,
                        status=JobStatus.FAILED,
                        progress_percent=100.0,
                        message="Job failed",
                        error_message=str(e),
                    )
                    await self.websocket_manager.send_progress_update(job_id, progress)
                finally:
                    # Clean up
                    if job_id in self.active_jobs:
                        del self.active_jobs[job_id]

            except asyncio.TimeoutError:
                # No jobs available, continue
                continue
            except Exception as e:
                print(f"Worker {worker_name} error: {e}")

    async def _process_job(self, job_id: str, job_data: Dict[str, Any]):
        """Process a single job with progress updates"""
        try:
            # Update progress: Processing
            progress = JobProgress(
                job_id=job_id,
                status=JobStatus.PROCESSING,
                progress_percent=10.0,
                message="Starting job processing",
            )
            await self.websocket_manager.send_progress_update(job_id, progress)

            # Simulate job processing with progress updates
            engine_id = job_data.get("engine_id", "unknown")
            text = job_data.get("text", "")

            # Update progress: Engine selected
            progress = JobProgress(
                job_id=job_id,
                status=JobStatus.PROCESSING,
                progress_percent=25.0,
                message=f"Selected engine: {engine_id}",
                engine_id=engine_id,
            )
            await self.websocket_manager.send_progress_update(job_id, progress)

            # Simulate processing time based on text length
            processing_time = min(5.0, max(1.0, len(text) / 100.0))
            steps = 10
            step_time = processing_time / steps

            for i in range(steps):
                if self._shutdown:
                    raise asyncio.CancelledError()

                progress_percent = 25.0 + (i + 1) * 6.0  # 25% to 85%
                progress = JobProgress(
                    job_id=job_id,
                    status=JobStatus.PROCESSING,
                    progress_percent=progress_percent,
                    message=f"Processing... ({int(progress_percent)}%)",
                    engine_id=engine_id,
                )
                await self.websocket_manager.send_progress_update(job_id, progress)

                await asyncio.sleep(step_time)

            # Simulate final processing
            progress = JobProgress(
                job_id=job_id,
                status=JobStatus.PROCESSING,
                progress_percent=90.0,
                message="Finalizing output",
                engine_id=engine_id,
            )
            await self.websocket_manager.send_progress_update(job_id, progress)

            await asyncio.sleep(0.5)

            # Job completed
            result_data = {
                "engine_id": engine_id,
                "text_length": len(text),
                "processing_time": processing_time,
                "success": True,
            }

            progress = JobProgress(
                job_id=job_id,
                status=JobStatus.COMPLETED,
                progress_percent=100.0,
                message="Job completed successfully",
                engine_id=engine_id,
                result_data=result_data,
            )
            await self.websocket_manager.send_progress_update(job_id, progress)

        except Exception as e:
            # Job failed
            progress = JobProgress(
                job_id=job_id,
                status=JobStatus.FAILED,
                progress_percent=100.0,
                message="Job failed",
                error_message=str(e),
            )
            await self.websocket_manager.send_progress_update(job_id, progress)
            raise

    def cancel_job(self, job_id: str) -> bool:
        """Cancel a running job"""
        if job_id in self.active_jobs:
            self.active_jobs[job_id].cancel()
            return True
        return False

    def get_job_status(self, job_id: str) -> Optional[JobProgress]:
        """Get current status of a job"""
        return self.websocket_manager.get_job_progress(job_id)


# Global instances
_websocket_manager: Optional[WebSocketManager] = None
_async_job_manager: Optional[AsyncJobManager] = None


def get_websocket_manager() -> WebSocketManager:
    """Get the global WebSocket manager instance"""
    global _websocket_manager

    if _websocket_manager is None:
        _websocket_manager = WebSocketManager()

    return _websocket_manager


def get_async_job_manager() -> AsyncJobManager:
    """Get the global async job manager instance"""
    global _async_job_manager

    if _async_job_manager is None:
        _async_job_manager = AsyncJobManager(get_websocket_manager())

    return _async_job_manager


async def start_async_job_processing():
    """Start the async job processing system"""
    job_manager = get_async_job_manager()
    await job_manager.start_workers()


async def stop_async_job_processing():
    """Stop the async job processing system"""
    job_manager = get_async_job_manager()
    await job_manager.stop_workers()


def create_async_job(
    engine_id: str,
    text: str,
    language: str,
    quality: str,
    voice_profile: Dict[str, Any],
    params: Dict[str, Any],
) -> str:
    """Create a new async job"""
    job_id = str(uuid.uuid4())
    job_data = {
        "engine_id": engine_id,
        "text": text,
        "language": language,
        "quality": quality,
        "voice_profile": voice_profile,
        "params": params,
    }

    # Submit job asynchronously
    job_manager = get_async_job_manager()
    asyncio.create_task(job_manager.submit_job(job_id, job_data))

    return job_id


if __name__ == "__main__":
    # Test WebSocket manager
    async def test_websocket_manager():
        manager = get_websocket_manager()

        # Simulate job progress
        job_id = "test_job_1"
        progress = JobProgress(
            job_id=job_id,
            status=JobStatus.PROCESSING,
            progress_percent=50.0,
            message="Processing...",
            engine_id="xtts",
        )

        await manager.send_progress_update(job_id, progress)
        print(f"Sent progress update for {job_id}")

    # Run test
    asyncio.run(test_websocket_manager())
