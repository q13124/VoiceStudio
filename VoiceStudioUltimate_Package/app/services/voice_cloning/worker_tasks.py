#!/usr/bin/env python3
"""
VoiceStudio Voice Cloning Worker Tasks
Specialized worker tasks for voice cloning operations with parallel processing.
"""

import asyncio
import logging
import time
import threading
from typing import Dict, Any, Optional, List, Callable
from concurrent.futures import ThreadPoolExecutor, Future
from dataclasses import dataclass
from datetime import datetime
import uuid
import json
import os
from pathlib import Path

# Import our enhanced audio processor
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', 'VoiceStudio', 'workers', 'python', 'vsdml'))
from vsdml.services.audio_processor import EnhancedAudioProcessor

# Import database functions
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from database import (
    save_voice_profile, get_voice_profile, save_voice_cloning_session,
    update_voice_cloning_session, save_voice_cloning_result,
    record_voice_cloning_metric
)

logger = logging.getLogger(__name__)

@dataclass
class VoiceCloningTask:
    """Voice cloning task definition"""
    task_id: str
    task_type: str  # 'extract_profile', 'clone_voice', 'batch_clone'
    audio_path: str
    target_text: Optional[str] = None
    speaker_id: Optional[str] = None
    model_type: str = "gpt_sovits"
    processing_mode: str = "standard"
    priority: int = 1  # 1=high, 2=medium, 3=low
    callback: Optional[Callable] = None
    metadata: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}

@dataclass
class VoiceCloningResult:
    """Voice cloning task result"""
    task_id: str
    success: bool
    result: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    processing_time: float = 0.0
    timestamp: datetime = None
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now()

class VoiceCloningWorkerPool:
    """Worker pool for voice cloning tasks with specialized workers"""
    
    def __init__(self, max_workers: int = 8, cache_size: int = 2000):
        self.max_workers = max_workers
        self.cache_size = cache_size
        
        # Initialize audio processor
        self.audio_processor = EnhancedAudioProcessor(
            max_workers=max_workers, 
            cache_size=cache_size
        )
        
        # Worker pools for different task types
        self.profile_extraction_pool = ThreadPoolExecutor(max_workers=max_workers//2)
        self.voice_cloning_pool = ThreadPoolExecutor(max_workers=max_workers//2)
        self.batch_processing_pool = ThreadPoolExecutor(max_workers=2)
        
        # Task queues with priority
        self.task_queue = []
        self.queue_lock = threading.Lock()
        
        # Active tasks tracking
        self.active_tasks = {}
        self.active_lock = threading.Lock()
        
        # Results storage
        self.results = {}
        self.results_lock = threading.Lock()
        
        # Performance metrics
        self.metrics = {
            "tasks_completed": 0,
            "tasks_failed": 0,
            "total_processing_time": 0.0,
            "average_processing_time": 0.0,
            "queue_size": 0,
            "active_tasks": 0
        }
        
        # Start worker threads
        self.running = True
        self.worker_threads = []
        self._start_worker_threads()
        
        logger.info(f"Voice cloning worker pool initialized with {max_workers} workers")
    
    def _start_worker_threads(self):
        """Start worker threads for different task types"""
        
        # Profile extraction workers
        for i in range(self.max_workers // 2):
            thread = threading.Thread(
                target=self._profile_extraction_worker,
                name=f"ProfileWorker-{i}",
                daemon=True
            )
            thread.start()
            self.worker_threads.append(thread)
        
        # Voice cloning workers
        for i in range(self.max_workers // 2):
            thread = threading.Thread(
                target=self._voice_cloning_worker,
                name=f"CloningWorker-{i}",
                daemon=True
            )
            thread.start()
            self.worker_threads.append(thread)
        
        # Batch processing worker
        batch_thread = threading.Thread(
            target=self._batch_processing_worker,
            name="BatchWorker",
            daemon=True
        )
        batch_thread.start()
        self.worker_threads.append(batch_thread)
        
        logger.info(f"Started {len(self.worker_threads)} worker threads")
    
    def submit_task(self, task: VoiceCloningTask) -> str:
        """Submit a voice cloning task"""
        with self.queue_lock:
            # Add task to queue with priority
            self.task_queue.append(task)
            self.task_queue.sort(key=lambda t: t.priority)
            self.metrics["queue_size"] = len(self.task_queue)
        
        logger.info(f"Submitted task {task.task_id} of type {task.task_type}")
        return task.task_id
    
    def get_task_result(self, task_id: str) -> Optional[VoiceCloningResult]:
        """Get result for a completed task"""
        with self.results_lock:
            return self.results.get(task_id)
    
    def get_active_tasks(self) -> List[str]:
        """Get list of active task IDs"""
        with self.active_lock:
            return list(self.active_tasks.keys())
    
    def get_queue_status(self) -> Dict[str, Any]:
        """Get current queue and worker status"""
        with self.queue_lock:
            queue_size = len(self.task_queue)
        
        with self.active_lock:
            active_count = len(self.active_tasks)
        
        return {
            "queue_size": queue_size,
            "active_tasks": active_count,
            "metrics": self.metrics.copy(),
            "worker_pools": {
                "profile_extraction": self.profile_extraction_pool._max_workers,
                "voice_cloning": self.voice_cloning_pool._max_workers,
                "batch_processing": self.batch_processing_pool._max_workers
            }
        }
    
    def _profile_extraction_worker(self):
        """Worker thread for voice profile extraction"""
        while self.running:
            try:
                task = self._get_next_task("extract_profile")
                if task is None:
                    time.sleep(0.1)
                    continue
                
                self._process_profile_extraction_task(task)
                
            except Exception as e:
                logger.error(f"Profile extraction worker error: {e}")
                time.sleep(1)
    
    def _voice_cloning_worker(self):
        """Worker thread for voice cloning"""
        while self.running:
            try:
                task = self._get_next_task("clone_voice")
                if task is None:
                    time.sleep(0.1)
                    continue
                
                self._process_voice_cloning_task(task)
                
            except Exception as e:
                logger.error(f"Voice cloning worker error: {e}")
                time.sleep(1)
    
    def _batch_processing_worker(self):
        """Worker thread for batch processing"""
        while self.running:
            try:
                task = self._get_next_task("batch_clone")
                if task is None:
                    time.sleep(0.1)
                    continue
                
                self._process_batch_cloning_task(task)
                
            except Exception as e:
                logger.error(f"Batch processing worker error: {e}")
                time.sleep(1)
    
    def _get_next_task(self, task_type: str) -> Optional[VoiceCloningTask]:
        """Get next task of specified type from queue"""
        with self.queue_lock:
            for i, task in enumerate(self.task_queue):
                if task.task_type == task_type:
                    # Move task to active
                    task = self.task_queue.pop(i)
                    self.metrics["queue_size"] = len(self.task_queue)
                    
                    with self.active_lock:
                        self.active_tasks[task.task_id] = task
                        self.metrics["active_tasks"] = len(self.active_tasks)
                    
                    return task
        
        return None
    
    def _process_profile_extraction_task(self, task: VoiceCloningTask):
        """Process voice profile extraction task"""
        start_time = time.time()
        result = VoiceCloningResult(task_id=task.task_id, success=False)
        
        try:
            logger.info(f"Processing profile extraction task {task.task_id}")
            
            # Extract voice profile
            profile = asyncio.run(
                self.audio_processor.extract_voice_profile(task.audio_path)
            )
            
            # Save to database if speaker_id provided
            if task.speaker_id:
                save_voice_profile(task.speaker_id, profile)
            
            result.success = True
            result.result = profile
            
            # Record metrics
            record_voice_cloning_metric(
                "voice_cloning_workers",
                "profile_extraction_time",
                time.time() - start_time,
                "processing_time",
                task_id=task.task_id,
                speaker_id=task.speaker_id
            )
            
        except Exception as e:
            logger.error(f"Profile extraction failed for task {task.task_id}: {e}")
            result.error = str(e)
            
            # Record error metrics
            record_voice_cloning_metric(
                "voice_cloning_workers",
                "profile_extraction_error",
                1.0,
                "error_count",
                task_id=task.task_id,
                speaker_id=task.speaker_id
            )
        
        finally:
            # Update metrics
            processing_time = time.time() - start_time
            result.processing_time = processing_time
            self._update_metrics(result)
            
            # Store result
            with self.results_lock:
                self.results[task.task_id] = result
            
            # Remove from active tasks
            with self.active_lock:
                self.active_tasks.pop(task.task_id, None)
                self.metrics["active_tasks"] = len(self.active_tasks)
            
            # Call callback if provided
            if task.callback:
                try:
                    task.callback(result)
                except Exception as e:
                    logger.error(f"Callback error for task {task.task_id}: {e}")
    
    def _process_voice_cloning_task(self, task: VoiceCloningTask):
        """Process voice cloning task"""
        start_time = time.time()
        result = VoiceCloningResult(task_id=task.task_id, success=False)
        
        try:
            logger.info(f"Processing voice cloning task {task.task_id}")
            
            # Create session in database
            session_id = f"session_{task.task_id}"
            save_voice_cloning_session(
                session_id, task.speaker_id, task.audio_path,
                task.target_text, task.model_type, task.processing_mode
            )
            
            # Clone voice
            clone_result = asyncio.run(
                self.audio_processor.clone_voice(
                    task.audio_path, task.target_text, 
                    task.speaker_id, task.model_type
                )
            )
            
            # Update session status
            update_voice_cloning_session(
                session_id, "completed",
                cloned_audio_path=clone_result.get("cloned_audio"),
                processing_time=clone_result.get("processing_time"),
                quality_score=clone_result.get("quality_score")
            )
            
            # Save result to database
            save_voice_cloning_result(
                session_id, task.speaker_id,
                clone_result.get("cloned_audio", ""),
                task.model_type,
                clone_result.get("processing_time", 0.0),
                clone_result.get("quality_score"),
                clone_result.get("similarity_score")
            )
            
            result.success = True
            result.result = clone_result
            
            # Record metrics
            record_voice_cloning_metric(
                "voice_cloning_workers",
                "voice_cloning_time",
                time.time() - start_time,
                "processing_time",
                session_id=session_id,
                speaker_id=task.speaker_id,
                model_type=task.model_type
            )
            
        except Exception as e:
            logger.error(f"Voice cloning failed for task {task.task_id}: {e}")
            result.error = str(e)
            
            # Update session status
            if 'session_id' in locals():
                update_voice_cloning_session(session_id, "failed", error_message=str(e))
            
            # Record error metrics
            record_voice_cloning_metric(
                "voice_cloning_workers",
                "voice_cloning_error",
                1.0,
                "error_count",
                task_id=task.task_id,
                speaker_id=task.speaker_id,
                model_type=task.model_type
            )
        
        finally:
            # Update metrics
            processing_time = time.time() - start_time
            result.processing_time = processing_time
            self._update_metrics(result)
            
            # Store result
            with self.results_lock:
                self.results[task.task_id] = result
            
            # Remove from active tasks
            with self.active_lock:
                self.active_tasks.pop(task.task_id, None)
                self.metrics["active_tasks"] = len(self.active_tasks)
            
            # Call callback if provided
            if task.callback:
                try:
                    task.callback(result)
                except Exception as e:
                    logger.error(f"Callback error for task {task.task_id}: {e}")
    
    def _process_batch_cloning_task(self, task: VoiceCloningTask):
        """Process batch voice cloning task"""
        start_time = time.time()
        result = VoiceCloningResult(task_id=task.task_id, success=False)
        
        try:
            logger.info(f"Processing batch cloning task {task.task_id}")
            
            # Extract batch data from metadata
            batch_data = task.metadata.get("batch_data", [])
            results = []
            
            for i, batch_item in enumerate(batch_data):
                try:
                    # Process each item in batch
                    item_result = asyncio.run(
                        self.audio_processor.clone_voice(
                            batch_item["audio_path"],
                            batch_item["target_text"],
                            batch_item.get("speaker_id"),
                            task.model_type
                        )
                    )
                    
                    results.append({
                        "batch_index": i,
                        "success": True,
                        "result": item_result
                    })
                    
                except Exception as e:
                    logger.error(f"Batch item {i} failed: {e}")
                    results.append({
                        "batch_index": i,
                        "success": False,
                        "error": str(e)
                    })
            
            result.success = True
            result.result = {
                "batch_results": results,
                "total_items": len(batch_data),
                "successful_items": sum(1 for r in results if r["success"]),
                "failed_items": sum(1 for r in results if not r["success"])
            }
            
            # Record batch metrics
            record_voice_cloning_metric(
                "voice_cloning_workers",
                "batch_cloning_time",
                time.time() - start_time,
                "processing_time",
                task_id=task.task_id,
                tags={"batch_size": len(batch_data)}
            )
            
        except Exception as e:
            logger.error(f"Batch cloning failed for task {task.task_id}: {e}")
            result.error = str(e)
            
            # Record error metrics
            record_voice_cloning_metric(
                "voice_cloning_workers",
                "batch_cloning_error",
                1.0,
                "error_count",
                task_id=task.task_id
            )
        
        finally:
            # Update metrics
            processing_time = time.time() - start_time
            result.processing_time = processing_time
            self._update_metrics(result)
            
            # Store result
            with self.results_lock:
                self.results[task.task_id] = result
            
            # Remove from active tasks
            with self.active_lock:
                self.active_tasks.pop(task.task_id, None)
                self.metrics["active_tasks"] = len(self.active_tasks)
            
            # Call callback if provided
            if task.callback:
                try:
                    task.callback(result)
                except Exception as e:
                    logger.error(f"Callback error for task {task.task_id}: {e}")
    
    def _update_metrics(self, result: VoiceCloningResult):
        """Update performance metrics"""
        if result.success:
            self.metrics["tasks_completed"] += 1
        else:
            self.metrics["tasks_failed"] += 1
        
        self.metrics["total_processing_time"] += result.processing_time
        
        total_tasks = self.metrics["tasks_completed"] + self.metrics["tasks_failed"]
        if total_tasks > 0:
            self.metrics["average_processing_time"] = (
                self.metrics["total_processing_time"] / total_tasks
            )
    
    def submit_profile_extraction(self, audio_path: str, speaker_id: str = None,
                                 priority: int = 1, callback: Callable = None) -> str:
        """Submit voice profile extraction task"""
        task_id = str(uuid.uuid4())
        task = VoiceCloningTask(
            task_id=task_id,
            task_type="extract_profile",
            audio_path=audio_path,
            speaker_id=speaker_id,
            priority=priority,
            callback=callback
        )
        
        return self.submit_task(task)
    
    def submit_voice_cloning(self, audio_path: str, target_text: str,
                            speaker_id: str = None, model_type: str = "gpt_sovits",
                            priority: int = 1, callback: Callable = None) -> str:
        """Submit voice cloning task"""
        task_id = str(uuid.uuid4())
        task = VoiceCloningTask(
            task_id=task_id,
            task_type="clone_voice",
            audio_path=audio_path,
            target_text=target_text,
            speaker_id=speaker_id,
            model_type=model_type,
            priority=priority,
            callback=callback
        )
        
        return self.submit_task(task)
    
    def submit_batch_cloning(self, batch_data: List[Dict[str, Any]],
                            model_type: str = "gpt_sovits", priority: int = 2,
                            callback: Callable = None) -> str:
        """Submit batch voice cloning task"""
        task_id = str(uuid.uuid4())
        task = VoiceCloningTask(
            task_id=task_id,
            task_type="batch_clone",
            audio_path="",  # Not used for batch
            target_text="",  # Not used for batch
            model_type=model_type,
            priority=priority,
            callback=callback,
            metadata={"batch_data": batch_data}
        )
        
        return self.submit_task(task)
    
    def shutdown(self):
        """Shutdown worker pool"""
        logger.info("Shutting down voice cloning worker pool...")
        
        self.running = False
        
        # Wait for active tasks to complete
        while True:
            with self.active_lock:
                if not self.active_tasks:
                    break
            time.sleep(0.1)
        
        # Shutdown thread pools
        self.profile_extraction_pool.shutdown(wait=True)
        self.voice_cloning_pool.shutdown(wait=True)
        self.batch_processing_pool.shutdown(wait=True)
        
        # Close audio processor
        self.audio_processor.close()
        
        logger.info("Voice cloning worker pool shutdown complete")

# Global worker pool instance
worker_pool = VoiceCloningWorkerPool()

def get_voice_cloning_worker_pool() -> VoiceCloningWorkerPool:
    """Get the global voice cloning worker pool"""
    return worker_pool

def submit_profile_extraction(audio_path: str, speaker_id: str = None,
                             priority: int = 1, callback: Callable = None) -> str:
    """Submit voice profile extraction task"""
    return worker_pool.submit_profile_extraction(audio_path, speaker_id, priority, callback)

def submit_voice_cloning(audio_path: str, target_text: str,
                        speaker_id: str = None, model_type: str = "gpt_sovits",
                        priority: int = 1, callback: Callable = None) -> str:
    """Submit voice cloning task"""
    return worker_pool.submit_voice_cloning(audio_path, target_text, speaker_id, model_type, priority, callback)

def submit_batch_cloning(batch_data: List[Dict[str, Any]],
                        model_type: str = "gpt_sovits", priority: int = 2,
                        callback: Callable = None) -> str:
    """Submit batch voice cloning task"""
    return worker_pool.submit_batch_cloning(batch_data, model_type, priority, callback)

def get_task_result(task_id: str) -> Optional[VoiceCloningResult]:
    """Get result for a completed task"""
    return worker_pool.get_task_result(task_id)

def get_worker_status() -> Dict[str, Any]:
    """Get worker pool status"""
    return worker_pool.get_queue_status()

if __name__ == "__main__":
    # Example usage
    logger.info("Voice cloning worker tasks initialized")
    
    # Example: Submit a voice cloning task
    def task_callback(result: VoiceCloningResult):
        if result.success:
            logger.info(f"Task {result.task_id} completed successfully")
        else:
            logger.error(f"Task {result.task_id} failed: {result.error}")
    
    # Submit profile extraction
    task_id = submit_profile_extraction(
        "test_audio.wav",
        speaker_id="speaker_001",
        callback=task_callback
    )
    
    logger.info(f"Submitted profile extraction task: {task_id}")
    
    # Submit voice cloning
    task_id = submit_voice_cloning(
        "reference_audio.wav",
        "Hello, this is a cloned voice.",
        speaker_id="speaker_001",
        model_type="gpt_sovits",
        callback=task_callback
    )
    
    logger.info(f"Submitted voice cloning task: {task_id}")
    
    # Keep running to process tasks
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        worker_pool.shutdown()
