"""
Phase 6: Workflow Automation
Task 6.5: Batch processing for multiple files/tasks.
"""

import asyncio
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any, Callable, Optional
import logging

logger = logging.getLogger(__name__)


class BatchStatus(Enum):
    """Batch processing status."""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


@dataclass
class BatchItem:
    """A single item in a batch."""
    id: str
    input_data: Any
    output_data: Optional[Any] = None
    status: BatchStatus = BatchStatus.PENDING
    error: Optional[str] = None
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    progress: float = 0.0


@dataclass
class BatchJob:
    """A batch processing job."""
    id: str
    name: str
    items: list[BatchItem]
    status: BatchStatus = BatchStatus.PENDING
    concurrency: int = 2
    stop_on_error: bool = False
    created_at: datetime = field(default_factory=datetime.now)
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    
    @property
    def progress(self) -> float:
        """Calculate overall progress."""
        if not self.items:
            return 0.0
        
        completed = sum(1 for i in self.items
                       if i.status in (BatchStatus.COMPLETED, BatchStatus.FAILED))
        return completed / len(self.items) * 100
    
    @property
    def items_completed(self) -> int:
        """Count completed items."""
        return sum(1 for i in self.items if i.status == BatchStatus.COMPLETED)
    
    @property
    def items_failed(self) -> int:
        """Count failed items."""
        return sum(1 for i in self.items if i.status == BatchStatus.FAILED)


@dataclass
class BatchResult:
    """Result of batch processing."""
    job_id: str
    total_items: int
    completed: int
    failed: int
    duration_seconds: float
    errors: list[str] = field(default_factory=list)


class BatchProcessor:
    """Processor for batch operations."""
    
    def __init__(self, max_concurrency: int = 4):
        self._jobs: dict[str, BatchJob] = {}
        self._running: dict[str, asyncio.Task] = {}
        self._max_concurrency = max_concurrency
        self._progress_callbacks: dict[str, Callable[[BatchJob], None]] = {}
    
    def create_batch(
        self,
        job_id: str,
        name: str,
        items: list[Any],
        concurrency: int = 2,
        stop_on_error: bool = False
    ) -> BatchJob:
        """Create a new batch job."""
        batch_items = [
            BatchItem(id=f"{job_id}_{i}", input_data=item)
            for i, item in enumerate(items)
        ]
        
        job = BatchJob(
            id=job_id,
            name=name,
            items=batch_items,
            concurrency=min(concurrency, self._max_concurrency),
            stop_on_error=stop_on_error,
        )
        
        self._jobs[job_id] = job
        return job
    
    async def process_batch(
        self,
        job_id: str,
        processor: Callable[[Any], Any],
        progress_callback: Optional[Callable[[BatchJob], None]] = None
    ) -> BatchResult:
        """Process a batch job."""
        job = self._jobs.get(job_id)
        if not job:
            raise ValueError(f"Job not found: {job_id}")
        
        if progress_callback:
            self._progress_callbacks[job_id] = progress_callback
        
        job.status = BatchStatus.PROCESSING
        job.started_at = datetime.now()
        
        try:
            # Create semaphore for concurrency control
            semaphore = asyncio.Semaphore(job.concurrency)
            
            async def process_item(item: BatchItem) -> None:
                async with semaphore:
                    if job.status == BatchStatus.CANCELLED:
                        return
                    
                    item.status = BatchStatus.PROCESSING
                    item.started_at = datetime.now()
                    
                    try:
                        # Run processor (may be sync or async)
                        if asyncio.iscoroutinefunction(processor):
                            item.output_data = await processor(item.input_data)
                        else:
                            item.output_data = await asyncio.get_event_loop(). \
                                run_in_executor(None, processor, item.input_data)
                        
                        item.status = BatchStatus.COMPLETED
                        item.progress = 100.0
                        
                    except Exception as e:
                        item.status = BatchStatus.FAILED
                        item.error = str(e)
                        logger.error(f"Batch item error: {e}")
                        
                        if job.stop_on_error:
                            job.status = BatchStatus.FAILED
                    
                    finally:
                        item.completed_at = datetime.now()
                        
                        # Report progress
                        if job_id in self._progress_callbacks:
                            self._progress_callbacks[job_id](job)
            
            # Process all items
            tasks = [process_item(item) for item in job.items]
            await asyncio.gather(*tasks, return_exceptions=True)
            
            # Set final status
            if job.status != BatchStatus.CANCELLED:
                if job.items_failed > 0 and job.stop_on_error:
                    job.status = BatchStatus.FAILED
                else:
                    job.status = BatchStatus.COMPLETED
            
        except asyncio.CancelledError:
            job.status = BatchStatus.CANCELLED
        except Exception as e:
            job.status = BatchStatus.FAILED
            logger.error(f"Batch processing error: {e}")
        finally:
            job.completed_at = datetime.now()
            
            if job_id in self._progress_callbacks:
                del self._progress_callbacks[job_id]
        
        duration = (job.completed_at - job.started_at).total_seconds()
        
        return BatchResult(
            job_id=job_id,
            total_items=len(job.items),
            completed=job.items_completed,
            failed=job.items_failed,
            duration_seconds=duration,
            errors=[i.error for i in job.items if i.error],
        )
    
    async def cancel_batch(self, job_id: str) -> bool:
        """Cancel a batch job."""
        job = self._jobs.get(job_id)
        if job and job.status == BatchStatus.PROCESSING:
            job.status = BatchStatus.CANCELLED
            
            # Cancel pending items
            for item in job.items:
                if item.status == BatchStatus.PENDING:
                    item.status = BatchStatus.CANCELLED
            
            return True
        
        return False
    
    def get_job(self, job_id: str) -> Optional[BatchJob]:
        """Get a batch job by ID."""
        return self._jobs.get(job_id)
    
    def get_job_status(self, job_id: str) -> Optional[dict[str, Any]]:
        """Get batch job status."""
        job = self._jobs.get(job_id)
        if not job:
            return None
        
        return {
            "id": job.id,
            "name": job.name,
            "status": job.status.value,
            "progress": job.progress,
            "total_items": len(job.items),
            "completed": job.items_completed,
            "failed": job.items_failed,
            "started_at": job.started_at.isoformat() if job.started_at else None,
        }


class BatchSynthesizer:
    """Batch synthesizer for processing multiple texts."""
    
    def __init__(self, processor: BatchProcessor):
        self._processor = processor
    
    async def synthesize_batch(
        self,
        texts: list[str],
        voice: str,
        engine: str = "xtts",
        output_dir: Optional[Path] = None,
        progress_callback: Optional[Callable[[BatchJob], None]] = None
    ) -> BatchResult:
        """Synthesize multiple texts in batch."""
        import uuid
        
        job_id = str(uuid.uuid4())
        
        # Create batch items with text and config
        items = [
            {"text": text, "voice": voice, "engine": engine, "index": i}
            for i, text in enumerate(texts)
        ]
        
        self._processor.create_batch(
            job_id=job_id,
            name="Batch Synthesis",
            items=items,
            concurrency=2,
        )
        
        async def synthesize_item(item: dict) -> dict:
            """Synthesize a single item."""
            # Simulate synthesis
            await asyncio.sleep(0.5)
            
            output_path = output_dir or Path("temp")
            audio_path = output_path / f"synthesis_{item['index']}.wav"
            
            return {
                "audio_path": str(audio_path),
                "text": item["text"],
                "duration": len(item["text"]) * 0.05,
            }
        
        return await self._processor.process_batch(
            job_id,
            synthesize_item,
            progress_callback
        )


class BatchExporter:
    """Batch exporter for converting multiple files."""
    
    def __init__(self, processor: BatchProcessor):
        self._processor = processor
    
    async def export_batch(
        self,
        audio_files: list[Path],
        output_format: str = "mp3",
        output_dir: Optional[Path] = None,
        progress_callback: Optional[Callable[[BatchJob], None]] = None
    ) -> BatchResult:
        """Export multiple audio files in batch."""
        import uuid
        
        job_id = str(uuid.uuid4())
        
        items = [
            {"input_path": path, "format": output_format, "index": i}
            for i, path in enumerate(audio_files)
        ]
        
        self._processor.create_batch(
            job_id=job_id,
            name="Batch Export",
            items=items,
            concurrency=4,
        )
        
        async def export_item(item: dict) -> dict:
            """Export a single item."""
            # Simulate export
            await asyncio.sleep(0.2)
            
            output_path = output_dir or Path("output")
            output_file = output_path / f"export_{item['index']}.{item['format']}"
            
            return {
                "output_path": str(output_file),
                "format": item["format"],
            }
        
        return await self._processor.process_batch(
            job_id,
            export_item,
            progress_callback
        )
