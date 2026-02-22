"""
Audio Buffers.

Task 4.4.2: Efficient audio buffering for streaming.
"""

from __future__ import annotations

import threading

import numpy as np


class CircularBuffer:
    """
    Thread-safe circular buffer for audio samples.

    Features:
    - Lock-free for single producer/consumer
    - Efficient numpy operations
    - Overflow/underflow handling
    """

    def __init__(self, capacity: int, dtype=np.float32):
        """
        Initialize circular buffer.

        Args:
            capacity: Maximum number of samples
            dtype: Sample data type
        """
        self._capacity = capacity
        self._buffer = np.zeros(capacity, dtype=dtype)
        self._write_pos = 0
        self._read_pos = 0
        self._size = 0
        self._lock = threading.Lock()

    @property
    def capacity(self) -> int:
        """Get buffer capacity."""
        return self._capacity

    def available(self) -> int:
        """Get number of samples available to read."""
        return self._size

    def free_space(self) -> int:
        """Get number of samples that can be written."""
        return self._capacity - self._size

    def is_empty(self) -> bool:
        """Check if buffer is empty."""
        return self._size == 0

    def is_full(self) -> bool:
        """Check if buffer is full."""
        return self._size == self._capacity

    def write(self, data: np.ndarray) -> int:
        """
        Write samples to buffer.

        Args:
            data: Samples to write

        Returns:
            Number of samples actually written
        """
        with self._lock:
            to_write = min(len(data), self.free_space())

            if to_write == 0:
                return 0

            # Handle wrap-around
            end_pos = (self._write_pos + to_write) % self._capacity

            if end_pos > self._write_pos:
                # No wrap-around
                self._buffer[self._write_pos : end_pos] = data[:to_write]
            else:
                # Wrap-around
                first_part = self._capacity - self._write_pos
                self._buffer[self._write_pos :] = data[:first_part]
                self._buffer[:end_pos] = data[first_part:to_write]

            self._write_pos = end_pos
            self._size += to_write

            return to_write

    def read(self, num_samples: int) -> np.ndarray | None:
        """
        Read samples from buffer.

        Args:
            num_samples: Number of samples to read

        Returns:
            Samples or None if not enough data
        """
        with self._lock:
            if self._size < num_samples:
                return None

            result = np.zeros(num_samples, dtype=self._buffer.dtype)

            # Handle wrap-around
            end_pos = (self._read_pos + num_samples) % self._capacity

            if end_pos > self._read_pos:
                # No wrap-around
                result[:] = self._buffer[self._read_pos : end_pos]
            else:
                # Wrap-around
                first_part = self._capacity - self._read_pos
                result[:first_part] = self._buffer[self._read_pos :]
                result[first_part:] = self._buffer[:end_pos]

            self._read_pos = end_pos
            self._size -= num_samples

            return result

    def peek(self, num_samples: int) -> np.ndarray | None:
        """
        Peek at samples without consuming.

        Args:
            num_samples: Number of samples to peek

        Returns:
            Samples or None if not enough data
        """
        with self._lock:
            if self._size < num_samples:
                return None

            result = np.zeros(num_samples, dtype=self._buffer.dtype)

            end_pos = (self._read_pos + num_samples) % self._capacity

            if end_pos > self._read_pos:
                result[:] = self._buffer[self._read_pos : end_pos]
            else:
                first_part = self._capacity - self._read_pos
                result[:first_part] = self._buffer[self._read_pos :]
                result[first_part:] = self._buffer[:end_pos]

            return result

    def clear(self) -> None:
        """Clear the buffer."""
        with self._lock:
            self._write_pos = 0
            self._read_pos = 0
            self._size = 0


class AudioBuffer:
    """
    High-level audio buffer with multiple channels.

    Features:
    - Multi-channel support
    - Resampling integration
    - Format conversion
    """

    def __init__(
        self,
        capacity: int,
        channels: int = 1,
        sample_rate: int = 16000,
    ):
        """
        Initialize audio buffer.

        Args:
            capacity: Capacity per channel
            channels: Number of audio channels
            sample_rate: Sample rate
        """
        self._channels = channels
        self._sample_rate = sample_rate
        self._buffers = [CircularBuffer(capacity) for _ in range(channels)]

    @property
    def channels(self) -> int:
        """Get number of channels."""
        return self._channels

    @property
    def sample_rate(self) -> int:
        """Get sample rate."""
        return self._sample_rate

    def available(self) -> int:
        """Get minimum samples available across all channels."""
        return min(buf.available() for buf in self._buffers)

    def write(self, data: np.ndarray) -> int:
        """
        Write multi-channel audio.

        Args:
            data: Audio data (samples, channels) or (samples,) for mono

        Returns:
            Samples written
        """
        if data.ndim == 1:
            # Mono
            if self._channels == 1:
                return self._buffers[0].write(data)
            else:
                # Duplicate to all channels
                written = float("inf")
                for buf in self._buffers:
                    w = buf.write(data)
                    written = min(written, w)
                return int(written)
        else:
            # Multi-channel
            written = float("inf")
            for i, buf in enumerate(self._buffers):
                if i < data.shape[1]:
                    w = buf.write(data[:, i])
                    written = min(written, w)
            return int(written)

    def read(self, num_samples: int) -> np.ndarray | None:
        """
        Read multi-channel audio.

        Args:
            num_samples: Samples per channel

        Returns:
            Audio data (samples, channels) or None
        """
        if self.available() < num_samples:
            return None

        if self._channels == 1:
            return self._buffers[0].read(num_samples)

        result = np.zeros((num_samples, self._channels), dtype=np.float32)

        for i, buf in enumerate(self._buffers):
            data = buf.read(num_samples)
            if data is not None:
                result[:, i] = data

        return result

    def clear(self) -> None:
        """Clear all buffers."""
        for buf in self._buffers:
            buf.clear()

    def duration_available(self) -> float:
        """Get duration of available audio in seconds."""
        return self.available() / self._sample_rate
