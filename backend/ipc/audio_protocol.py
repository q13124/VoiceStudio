"""
Binary Audio Protocol.

Task 1.4.2: Efficient audio streaming protocol.
Optimized binary protocol for real-time audio transfer.
"""

from __future__ import annotations

import asyncio
import logging
import struct
import zlib
from collections.abc import AsyncIterator, Awaitable, Callable
from dataclasses import dataclass
from datetime import datetime
from enum import IntEnum

logger = logging.getLogger(__name__)


class AudioFormat(IntEnum):
    """Audio sample formats."""
    PCM_S16LE = 0   # 16-bit signed little-endian
    PCM_S24LE = 1   # 24-bit signed little-endian
    PCM_S32LE = 2   # 32-bit signed little-endian
    PCM_F32LE = 3   # 32-bit float little-endian
    PCM_F64LE = 4   # 64-bit float little-endian


class FrameType(IntEnum):
    """Types of audio frames."""
    DATA = 0        # Audio data
    HEADER = 1      # Stream header
    END = 2         # End of stream
    ERROR = 3       # Error frame
    METADATA = 4    # Metadata frame


@dataclass
class AudioStreamConfig:
    """Configuration for an audio stream."""
    sample_rate: int = 44100
    channels: int = 2
    format: AudioFormat = AudioFormat.PCM_S16LE
    frame_size: int = 1024  # Samples per frame
    compression: bool = False
    buffer_frames: int = 10


@dataclass
class AudioFrame:
    """An audio frame in the protocol."""
    frame_type: FrameType
    sequence: int
    timestamp_ms: int
    data: bytes
    checksum: int = 0
    compressed: bool = False

    # Frame header: type(1) + seq(4) + timestamp(4) + data_len(4) + checksum(4) + flags(1) = 18 bytes
    HEADER_SIZE = 18

    def to_bytes(self) -> bytes:
        """Serialize frame to bytes."""
        flags = 0x01 if self.compressed else 0x00

        header = struct.pack(
            "<BIIIIB",
            self.frame_type.value,
            self.sequence,
            self.timestamp_ms,
            len(self.data),
            self.checksum,
            flags,
        )

        return header + self.data

    @classmethod
    def from_bytes(cls, data: bytes) -> AudioFrame:
        """Deserialize frame from bytes."""
        if len(data) < cls.HEADER_SIZE:
            raise ValueError("Frame too short")

        frame_type, sequence, timestamp_ms, data_len, checksum, flags = struct.unpack(
            "<BIIIIB", data[:cls.HEADER_SIZE]
        )

        frame_data = data[cls.HEADER_SIZE:cls.HEADER_SIZE + data_len]

        return cls(
            frame_type=FrameType(frame_type),
            sequence=sequence,
            timestamp_ms=timestamp_ms,
            data=frame_data,
            checksum=checksum,
            compressed=(flags & 0x01) != 0,
        )

    def compute_checksum(self) -> int:
        """Compute CRC32 checksum of data."""
        return zlib.crc32(self.data) & 0xFFFFFFFF

    def verify_checksum(self) -> bool:
        """Verify the frame checksum."""
        return self.checksum == self.compute_checksum()


class AudioProtocol:
    """
    Binary protocol for efficient audio streaming.

    Features:
    - Low-latency frame transfer
    - Optional compression
    - Sequence tracking
    - Checksum validation
    - Stream header negotiation
    """

    def __init__(self, config: AudioStreamConfig | None = None):
        self.config = config or AudioStreamConfig()

        self._sequence = 0
        self._start_time: datetime | None = None
        self._frames_sent = 0
        self._frames_received = 0
        self._bytes_sent = 0
        self._bytes_received = 0
        self._lock = asyncio.Lock()

    def create_header_frame(self) -> AudioFrame:
        """Create a stream header frame."""
        # Pack stream configuration
        header_data = struct.pack(
            "<IIBIB",
            self.config.sample_rate,
            self.config.channels,
            self.config.format.value,
            self.config.frame_size,
            0x01 if self.config.compression else 0x00,
        )

        frame = AudioFrame(
            frame_type=FrameType.HEADER,
            sequence=0,
            timestamp_ms=0,
            data=header_data,
        )
        frame.checksum = frame.compute_checksum()

        return frame

    def parse_header_frame(self, frame: AudioFrame) -> AudioStreamConfig:
        """Parse a stream header frame."""
        if frame.frame_type != FrameType.HEADER:
            raise ValueError("Not a header frame")

        sample_rate, channels, format_val, frame_size, compression = struct.unpack(
            "<IIBIB", frame.data
        )

        return AudioStreamConfig(
            sample_rate=sample_rate,
            channels=channels,
            format=AudioFormat(format_val),
            frame_size=frame_size,
            compression=compression != 0,
        )

    async def create_data_frame(
        self,
        audio_data: bytes,
        timestamp_ms: int | None = None,
    ) -> AudioFrame:
        """Create a data frame from audio samples."""
        async with self._lock:
            self._sequence += 1
            sequence = self._sequence

        if timestamp_ms is None:
            if self._start_time is None:
                self._start_time = datetime.now()
            timestamp_ms = int((datetime.now() - self._start_time).total_seconds() * 1000)

        # Compress if enabled
        data = audio_data
        compressed = False
        if self.config.compression:
            compressed_data = zlib.compress(audio_data, level=1)  # Fast compression
            if len(compressed_data) < len(audio_data) * 0.9:  # Only use if 10%+ smaller
                data = compressed_data
                compressed = True

        frame = AudioFrame(
            frame_type=FrameType.DATA,
            sequence=sequence,
            timestamp_ms=timestamp_ms,
            data=data,
            compressed=compressed,
        )
        frame.checksum = frame.compute_checksum()

        self._frames_sent += 1
        self._bytes_sent += len(frame.to_bytes())

        return frame

    async def extract_audio(self, frame: AudioFrame) -> bytes:
        """Extract audio data from a frame."""
        if frame.frame_type != FrameType.DATA:
            raise ValueError("Not a data frame")

        if not frame.verify_checksum():
            raise ValueError("Checksum verification failed")

        data = frame.data
        if frame.compressed:
            data = zlib.decompress(data)

        self._frames_received += 1
        self._bytes_received += len(frame.to_bytes())

        return data

    def create_end_frame(self) -> AudioFrame:
        """Create an end-of-stream frame."""
        frame = AudioFrame(
            frame_type=FrameType.END,
            sequence=self._sequence + 1,
            timestamp_ms=0,
            data=b"",
        )
        return frame

    def create_error_frame(self, error_message: str) -> AudioFrame:
        """Create an error frame."""
        frame = AudioFrame(
            frame_type=FrameType.ERROR,
            sequence=self._sequence + 1,
            timestamp_ms=0,
            data=error_message.encode("utf-8"),
        )
        return frame

    async def stream_audio(
        self,
        audio_source: AsyncIterator[bytes],
        send_func: Callable[[bytes], Awaitable[None]],
    ) -> int:
        """
        Stream audio from a source.

        Args:
            audio_source: Async iterator yielding audio chunks
            send_func: Function to send frame bytes

        Returns:
            Total frames sent
        """
        # Send header
        header = self.create_header_frame()
        await send_func(header.to_bytes())

        frames_sent = 0

        try:
            async for chunk in audio_source:
                frame = await self.create_data_frame(chunk)
                await send_func(frame.to_bytes())
                frames_sent += 1

            # Send end frame
            end_frame = self.create_end_frame()
            await send_func(end_frame.to_bytes())

        except Exception as e:
            error_frame = self.create_error_frame(str(e))
            await send_func(error_frame.to_bytes())
            raise

        return frames_sent

    async def receive_audio(
        self,
        receive_func: Callable[[], Awaitable[bytes]],
    ) -> AsyncIterator[bytes]:
        """
        Receive audio frames.

        Args:
            receive_func: Function to receive frame bytes

        Yields:
            Audio data chunks
        """
        # Receive header
        header_data = await receive_func()
        header_frame = AudioFrame.from_bytes(header_data)

        if header_frame.frame_type != FrameType.HEADER:
            raise ValueError("Expected header frame")

        # Update config from header
        self.config = self.parse_header_frame(header_frame)

        # Receive data frames
        expected_sequence = 1

        while True:
            frame_data = await receive_func()
            frame = AudioFrame.from_bytes(frame_data)

            if frame.frame_type == FrameType.END:
                break

            if frame.frame_type == FrameType.ERROR:
                raise RuntimeError(frame.data.decode("utf-8"))

            if frame.frame_type != FrameType.DATA:
                continue

            # Check sequence
            if frame.sequence != expected_sequence:
                logger.warning(f"Sequence gap: expected {expected_sequence}, got {frame.sequence}")
            expected_sequence = frame.sequence + 1

            # Extract audio
            audio_data = await self.extract_audio(frame)
            yield audio_data

    def get_stats(self) -> dict:
        """Get protocol statistics."""
        return {
            "frames_sent": self._frames_sent,
            "frames_received": self._frames_received,
            "bytes_sent": self._bytes_sent,
            "bytes_received": self._bytes_received,
            "current_sequence": self._sequence,
            "config": {
                "sample_rate": self.config.sample_rate,
                "channels": self.config.channels,
                "format": self.config.format.name,
                "compression": self.config.compression,
            },
        }
