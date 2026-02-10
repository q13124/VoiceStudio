"""
Streaming Audio Processor.

Task 4.4: Real-time audio streaming with low latency.
"""

from __future__ import annotations

import asyncio
import logging
import time
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, AsyncIterator, Callable, Dict, List, Optional

import numpy as np

from backend.voice.streaming.buffer import CircularBuffer

logger = logging.getLogger(__name__)


class StreamState(Enum):
    """Stream processing state."""
    IDLE = "idle"
    STARTING = "starting"
    ACTIVE = "active"
    PAUSED = "paused"
    STOPPING = "stopping"
    ERROR = "error"


@dataclass
class StreamConfig:
    """Configuration for streaming processor."""
    
    # Audio format
    sample_rate: int = 16000
    channels: int = 1
    chunk_size: int = 1024  # Samples per chunk
    
    # Buffering
    buffer_size: int = 10  # Chunks
    prefill_chunks: int = 2
    
    # Latency
    target_latency_ms: int = 100
    max_latency_ms: int = 500
    
    # Processing
    enable_vad: bool = True  # Voice Activity Detection
    enable_agc: bool = True  # Automatic Gain Control
    enable_noise_reduction: bool = False


@dataclass
class StreamStats:
    """Statistics for stream processing."""
    
    chunks_processed: int = 0
    bytes_processed: int = 0
    start_time: float = 0.0
    current_latency_ms: float = 0.0
    underruns: int = 0
    overruns: int = 0
    processing_time_avg_ms: float = 0.0
    
    def get_throughput(self) -> float:
        """Get throughput in samples per second."""
        elapsed = time.time() - self.start_time
        if elapsed > 0:
            return self.bytes_processed / elapsed
        return 0.0


class StreamingProcessor:
    """
    Real-time audio streaming processor.
    
    Features:
    - Low-latency processing pipeline
    - Input/output buffering
    - Voice activity detection
    - Dynamic latency management
    """
    
    def __init__(self, config: Optional[StreamConfig] = None):
        """
        Initialize streaming processor.
        
        Args:
            config: Stream configuration
        """
        self._config = config or StreamConfig()
        self._state = StreamState.IDLE
        self._stats = StreamStats()
        
        # Buffers
        buffer_samples = self._config.chunk_size * self._config.buffer_size
        self._input_buffer = CircularBuffer(buffer_samples)
        self._output_buffer = CircularBuffer(buffer_samples)
        
        # Processing pipeline
        self._processors: List[Callable] = []
        
        # Callbacks
        self._on_output: Optional[Callable] = None
        self._on_error: Optional[Callable] = None
        
        # Processing task
        self._process_task: Optional[asyncio.Task] = None
        self._running = False
    
    @property
    def state(self) -> StreamState:
        """Get current stream state."""
        return self._state
    
    @property
    def stats(self) -> StreamStats:
        """Get stream statistics."""
        return self._stats
    
    def add_processor(
        self,
        processor: Callable[[np.ndarray], np.ndarray],
    ) -> None:
        """
        Add a processing step to the pipeline.
        
        Args:
            processor: Function that takes audio chunk and returns processed chunk
        """
        self._processors.append(processor)
    
    def clear_processors(self) -> None:
        """Clear all processors from pipeline."""
        self._processors.clear()
    
    def set_output_callback(
        self,
        callback: Callable[[np.ndarray], None],
    ) -> None:
        """Set callback for processed output."""
        self._on_output = callback
    
    def set_error_callback(
        self,
        callback: Callable[[Exception], None],
    ) -> None:
        """Set callback for errors."""
        self._on_error = callback
    
    async def start(self) -> bool:
        """
        Start the streaming processor.
        
        Returns:
            True if started successfully
        """
        if self._state == StreamState.ACTIVE:
            return True
        
        try:
            self._state = StreamState.STARTING
            self._running = True
            self._stats = StreamStats(start_time=time.time())
            
            # Start processing loop
            self._process_task = asyncio.create_task(self._process_loop())
            
            self._state = StreamState.ACTIVE
            logger.info("Streaming processor started")
            return True
            
        except Exception as e:
            self._state = StreamState.ERROR
            logger.error(f"Failed to start streaming: {e}")
            return False
    
    async def stop(self) -> None:
        """Stop the streaming processor."""
        if self._state == StreamState.IDLE:
            return
        
        self._state = StreamState.STOPPING
        self._running = False
        
        if self._process_task:
            self._process_task.cancel()
            try:
                await self._process_task
            except asyncio.CancelledError:
                pass
        
        self._state = StreamState.IDLE
        logger.info("Streaming processor stopped")
    
    async def pause(self) -> None:
        """Pause processing."""
        if self._state == StreamState.ACTIVE:
            self._state = StreamState.PAUSED
    
    async def resume(self) -> None:
        """Resume processing."""
        if self._state == StreamState.PAUSED:
            self._state = StreamState.ACTIVE
    
    async def push_audio(self, audio_chunk: np.ndarray) -> bool:
        """
        Push audio data into the input buffer.
        
        Args:
            audio_chunk: Audio samples
            
        Returns:
            True if successfully buffered
        """
        if self._state not in (StreamState.ACTIVE, StreamState.PAUSED):
            return False
        
        written = self._input_buffer.write(audio_chunk)
        
        if written < len(audio_chunk):
            self._stats.overruns += 1
            return False
        
        return True
    
    async def pull_audio(self, num_samples: int) -> Optional[np.ndarray]:
        """
        Pull processed audio from the output buffer.
        
        Args:
            num_samples: Number of samples to pull
            
        Returns:
            Audio samples or None if not enough data
        """
        if self._output_buffer.available() < num_samples:
            self._stats.underruns += 1
            return None
        
        return self._output_buffer.read(num_samples)
    
    async def _process_loop(self) -> None:
        """Main processing loop."""
        chunk_size = self._config.chunk_size
        processing_times = []
        
        while self._running:
            try:
                if self._state == StreamState.PAUSED:
                    await asyncio.sleep(0.01)
                    continue
                
                # Check if we have enough input
                if self._input_buffer.available() < chunk_size:
                    await asyncio.sleep(0.001)
                    continue
                
                # Read chunk from input
                chunk = self._input_buffer.read(chunk_size)
                
                if chunk is None:
                    continue
                
                # Process through pipeline
                start = time.time()
                
                processed = chunk
                for processor in self._processors:
                    processed = processor(processed)
                
                processing_time = (time.time() - start) * 1000
                processing_times.append(processing_time)
                
                # Keep rolling average
                if len(processing_times) > 100:
                    processing_times.pop(0)
                
                self._stats.processing_time_avg_ms = sum(processing_times) / len(processing_times)
                
                # Write to output buffer
                self._output_buffer.write(processed)
                
                # Update stats
                self._stats.chunks_processed += 1
                self._stats.bytes_processed += len(processed) * 2  # 16-bit samples
                
                # Call output callback if set
                if self._on_output:
                    self._on_output(processed)
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Processing error: {e}")
                if self._on_error:
                    self._on_error(e)
    
    async def process_stream(
        self,
        input_stream: AsyncIterator[np.ndarray],
    ) -> AsyncIterator[np.ndarray]:
        """
        Process an async stream of audio.
        
        Args:
            input_stream: Async iterator of audio chunks
            
        Yields:
            Processed audio chunks
        """
        async for chunk in input_stream:
            # Process through pipeline
            processed = chunk
            for processor in self._processors:
                processed = processor(processed)
            
            self._stats.chunks_processed += 1
            yield processed
    
    def get_latency(self) -> float:
        """
        Get current end-to-end latency in milliseconds.
        """
        buffered_samples = (
            self._input_buffer.available() +
            self._output_buffer.available()
        )
        
        latency_samples = buffered_samples + self._config.chunk_size
        latency_ms = (latency_samples / self._config.sample_rate) * 1000
        
        self._stats.current_latency_ms = latency_ms
        return latency_ms
    
    def get_config(self) -> StreamConfig:
        """Get current configuration."""
        return self._config
    
    def get_stats_dict(self) -> Dict[str, Any]:
        """Get statistics as dictionary."""
        return {
            "state": self._state.value,
            "chunks_processed": self._stats.chunks_processed,
            "bytes_processed": self._stats.bytes_processed,
            "current_latency_ms": self.get_latency(),
            "underruns": self._stats.underruns,
            "overruns": self._stats.overruns,
            "processing_time_avg_ms": self._stats.processing_time_avg_ms,
            "throughput": self._stats.get_throughput(),
        }
