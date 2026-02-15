"""
Intent Buffer for VoiceStudio Supervisor (Phase 11.2.4)

Buffers user speech during AI audio output for processing
after the current AI turn completes. Used for cooperative
interruptions and backchannel signals.
"""

import logging
import time
from collections import deque
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class BufferedUtterance:
    """A buffered user utterance during AI output."""
    text: str
    timestamp: float
    audio_energy: float = 0.0
    interruption_type: str = ""


class IntentBuffer:
    """
    Buffers user speech during AI audio output.

    Cooperative interruptions and backchannels are buffered
    and processed after the AI finishes its current turn.
    """

    MAX_BUFFER_SIZE = 20
    MAX_BUFFER_AGE_SECONDS = 30.0

    def __init__(self):
        self._buffer: deque[BufferedUtterance] = deque(maxlen=self.MAX_BUFFER_SIZE)

    def add(
        self,
        text: str,
        audio_energy: float = 0.0,
        interruption_type: str = "",
    ) -> None:
        """Add a buffered utterance."""
        utterance = BufferedUtterance(
            text=text,
            timestamp=time.time(),
            audio_energy=audio_energy,
            interruption_type=interruption_type,
        )
        self._buffer.append(utterance)

    def flush(self) -> str:
        """Get all buffered text and clear the buffer."""
        now = time.time()
        # Filter out stale entries
        valid = [
            u for u in self._buffer
            if (now - u.timestamp) < self.MAX_BUFFER_AGE_SECONDS
        ]
        self._buffer.clear()

        if not valid:
            return ""

        return " ".join(u.text for u in valid)

    def peek(self) -> list[str]:
        """View buffered text without clearing."""
        return [u.text for u in self._buffer]

    def has_content(self) -> bool:
        """Check if there's meaningful content in the buffer."""
        return len(self._buffer) > 0

    @property
    def size(self) -> int:
        return len(self._buffer)

    def clear(self) -> None:
        """Clear all buffered content."""
        self._buffer.clear()
