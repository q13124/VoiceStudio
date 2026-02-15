"""
Filler Phrase Generator for VoiceStudio (Phase 11.1.4)

Generates contextual filler phrases during handoffs between S2S
and Cascade pipelines to maintain conversational fluidity.
"""

from __future__ import annotations

import logging
import random

logger = logging.getLogger(__name__)


class FillerPhraseGenerator:
    """
    Generates natural filler phrases during pipeline handoffs.

    When transitioning from S2S to Cascade (1.5-3 second delay),
    the S2S engine generates these phrases to keep the user engaged.
    """

    # Default filler phrases by category
    THINKING_FILLERS = [
        "Let me think about that for a moment...",
        "That's a great question. Give me a second...",
        "Hmm, let me work through that...",
        "Let me pull up that information...",
        "One moment while I figure that out...",
    ]

    PROCESSING_FILLERS = [
        "I'm working on that right now...",
        "Just processing your request...",
        "Almost there, one moment...",
        "Let me handle that for you...",
        "Working on it...",
    ]

    TOOL_FILLERS = [
        "Let me run that for you...",
        "I'll generate that now...",
        "Processing your audio...",
        "Setting that up...",
        "Applying those changes...",
    ]

    ACKNOWLEDGMENT_FILLERS = [
        "Got it.",
        "Understood.",
        "Sure thing.",
        "I see what you mean.",
        "Right, I understand.",
    ]

    def __init__(self):
        self._used_recently: list[str] = []
        self._max_recent = 5

    def get_filler(
        self,
        category: str = "thinking",
        context: str | None = None,
    ) -> str:
        """
        Get a contextual filler phrase.

        Args:
            category: Type of filler ("thinking", "processing", "tool", "acknowledgment").
            context: Optional context to influence selection.

        Returns:
            A filler phrase string.
        """
        phrase_map = {
            "thinking": self.THINKING_FILLERS,
            "processing": self.PROCESSING_FILLERS,
            "tool": self.TOOL_FILLERS,
            "acknowledgment": self.ACKNOWLEDGMENT_FILLERS,
        }

        phrases = phrase_map.get(category, self.THINKING_FILLERS)

        # Avoid recently used phrases
        available = [p for p in phrases if p not in self._used_recently]
        if not available:
            self._used_recently.clear()
            available = phrases

        selected = random.choice(available)

        self._used_recently.append(selected)
        if len(self._used_recently) > self._max_recent:
            self._used_recently.pop(0)

        return selected

    def get_filler_for_handoff(self, from_mode: str, to_mode: str) -> str:
        """Get a filler phrase appropriate for a mode transition."""
        if to_mode == "cascade":
            return self.get_filler("thinking")
        elif from_mode == "cascade" and to_mode == "s2s":
            return self.get_filler("acknowledgment")
        return self.get_filler("processing")
