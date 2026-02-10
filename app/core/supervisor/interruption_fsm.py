"""
Pragmatic Interruption State Machine for VoiceStudio (Phase 11.2.1)

Distinguishes between different types of user interruptions:
- Cooperative: User completes AI's sentence
- Topic Change: User pivots the conversation
- Disfluency: User coughs, says "um", etc. (should be ignored)
"""

import logging
import time
from enum import Enum
from typing import Any, Dict, Optional

logger = logging.getLogger(__name__)


class InterruptionType(str, Enum):
    """Types of user interruption."""
    NONE = "none"
    COOPERATIVE = "cooperative"    # User supplies a missing word
    TOPIC_CHANGE = "topic_change"  # User asks a new question
    DISFLUENCY = "disfluency"      # Um, uh, cough, etc.
    BACKCHANNEL = "backchannel"    # "Yeah", "uh-huh", "right"
    URGENT = "urgent"              # Clear intent to take over


class InterruptionAction(str, Enum):
    """Action to take for an interruption."""
    IGNORE = "ignore"          # Continue AI output
    BUFFER = "buffer"          # Buffer user speech, continue AI
    STOP_AND_LISTEN = "stop"   # Stop AI output, process user input
    PAUSE = "pause"            # Pause AI output briefly


class InterruptionFSM:
    """
    Pragmatic interruption state machine.

    Analyzes overlapping speech to determine user intent and
    take the appropriate action (ignore, buffer, or stop).
    """

    # Disfluency patterns (should be ignored)
    DISFLUENCY_PATTERNS = frozenset({
        "um", "uh", "hmm", "ah", "er", "like",
        "you know", "i mean", "so", "well",
    })

    # Backchannel patterns (buffer, don't stop)
    BACKCHANNEL_PATTERNS = frozenset({
        "yeah", "yes", "yep", "uh-huh", "right",
        "okay", "ok", "sure", "got it", "i see",
        "mm-hmm", "mhm",
    })

    # Topic change indicators
    TOPIC_CHANGE_INDICATORS = frozenset({
        "but", "actually", "wait", "hold on", "no",
        "stop", "instead", "what about", "let me",
        "can you", "i want", "change",
    })

    def __init__(self):
        self._ai_is_speaking = False
        self._last_interruption_time: float = 0.0
        self._interruption_count: int = 0

    def classify_interruption(
        self,
        user_text: str,
        ai_is_speaking: bool = True,
        audio_energy: float = 0.0,
    ) -> Dict[str, Any]:
        """
        Classify an interruption and recommend an action.

        Args:
            user_text: Transcribed user speech during AI output.
            ai_is_speaking: Whether the AI is currently generating audio.
            audio_energy: RMS energy of user audio (0.0-1.0).

        Returns:
            Dict with interruption type and recommended action.
        """
        if not ai_is_speaking:
            return {
                "type": InterruptionType.NONE.value,
                "action": InterruptionAction.STOP_AND_LISTEN.value,
                "confidence": 1.0,
            }

        text_lower = user_text.lower().strip()
        words = text_lower.split()

        # Check for disfluency
        if text_lower in self.DISFLUENCY_PATTERNS or (
            len(words) == 1 and words[0] in self.DISFLUENCY_PATTERNS
        ):
            return {
                "type": InterruptionType.DISFLUENCY.value,
                "action": InterruptionAction.IGNORE.value,
                "confidence": 0.9,
            }

        # Check for backchannel
        if text_lower in self.BACKCHANNEL_PATTERNS:
            return {
                "type": InterruptionType.BACKCHANNEL.value,
                "action": InterruptionAction.BUFFER.value,
                "confidence": 0.85,
            }

        # Check for topic change
        for indicator in self.TOPIC_CHANGE_INDICATORS:
            if text_lower.startswith(indicator):
                self._interruption_count += 1
                self._last_interruption_time = time.time()
                return {
                    "type": InterruptionType.TOPIC_CHANGE.value,
                    "action": InterruptionAction.STOP_AND_LISTEN.value,
                    "confidence": 0.8,
                }

        # Check for cooperative completion (short, continues topic)
        if len(words) <= 3 and not any(
            text_lower.startswith(i) for i in self.TOPIC_CHANGE_INDICATORS
        ):
            return {
                "type": InterruptionType.COOPERATIVE.value,
                "action": InterruptionAction.BUFFER.value,
                "confidence": 0.6,
            }

        # Longer input during AI speech = likely topic change
        if len(words) > 5:
            self._interruption_count += 1
            return {
                "type": InterruptionType.TOPIC_CHANGE.value,
                "action": InterruptionAction.STOP_AND_LISTEN.value,
                "confidence": 0.7,
            }

        # Default: urgent interruption
        return {
            "type": InterruptionType.URGENT.value,
            "action": InterruptionAction.STOP_AND_LISTEN.value,
            "confidence": 0.5,
        }

    def get_stats(self) -> Dict[str, Any]:
        """Get interruption statistics."""
        return {
            "total_interruptions": self._interruption_count,
            "last_interruption_time": self._last_interruption_time,
        }
