"""
Barge-In Handler for VoiceStudio (Phase 11.2.3)

Handles immediate AI audio stop when the user begins speaking.
Coordinates with the interruption FSM to determine the appropriate response.
"""

import asyncio
import logging
import time
from typing import Any, Callable, Dict, Optional

logger = logging.getLogger(__name__)

from .interruption_fsm import InterruptionAction, InterruptionFSM


class BargeInHandler:
    """
    Handles barge-in (user interrupts AI speech).

    When user speech is detected during AI output:
    1. Classify the interruption type
    2. Take appropriate action (ignore, buffer, stop)
    3. Manage the transition smoothly
    """

    def __init__(
        self,
        interruption_fsm: Optional[InterruptionFSM] = None,
        on_stop: Optional[Callable] = None,
        on_buffer: Optional[Callable] = None,
    ):
        self._fsm = interruption_fsm or InterruptionFSM()
        self._on_stop = on_stop
        self._on_buffer = on_buffer
        self._ai_speaking = False
        self._buffered_input: list = []
        self._last_barge_in: float = 0.0

    def set_ai_speaking(self, speaking: bool) -> None:
        """Set whether the AI is currently producing audio."""
        self._ai_speaking = speaking
        if not speaking:
            self._buffered_input.clear()

    async def handle_user_speech(
        self,
        text: str,
        audio_energy: float = 0.0,
    ) -> Dict[str, Any]:
        """
        Handle detected user speech.

        Args:
            text: Transcribed user speech.
            audio_energy: Audio energy level (0.0-1.0).

        Returns:
            Action result dict.
        """
        result = self._fsm.classify_interruption(
            user_text=text,
            ai_is_speaking=self._ai_speaking,
            audio_energy=audio_energy,
        )

        action = result["action"]

        if action == InterruptionAction.STOP_AND_LISTEN.value:
            self._last_barge_in = time.time()
            if self._on_stop:
                await self._execute_callback(self._on_stop)
            result["buffered_input"] = self._flush_buffer()
            result["buffered_input"].append(text)
            logger.info(f"Barge-in: stop ({result['type']})")

        elif action == InterruptionAction.BUFFER.value:
            self._buffered_input.append(text)
            if self._on_buffer:
                await self._execute_callback(self._on_buffer, text)
            logger.debug(f"Barge-in: buffered ({result['type']})")

        elif action == InterruptionAction.IGNORE.value:
            logger.debug(f"Barge-in: ignored ({result['type']})")

        return result

    def flush_buffer(self) -> str:
        """Get and clear all buffered user input."""
        combined = " ".join(self._buffered_input)
        self._buffered_input.clear()
        return combined

    def _flush_buffer(self) -> list:
        """Internal flush that returns the list."""
        items = list(self._buffered_input)
        self._buffered_input.clear()
        return items

    async def _execute_callback(self, callback: Callable, *args) -> None:
        """Execute a callback safely."""
        try:
            if asyncio.iscoroutinefunction(callback):
                await callback(*args)
            else:
                callback(*args)
        except Exception as exc:
            logger.warning(f"Barge-in callback failed: {exc}")
