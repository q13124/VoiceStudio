"""
Context Preservation for VoiceStudio Supervisor (Phase 11.1.5)

Maintains conversation context across pipeline switches.
When transitioning from S2S to Cascade (or vice versa), the
context synopsis is injected into the new pipeline's system prompt.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from typing import Any

logger = logging.getLogger(__name__)


@dataclass
class ConversationTurn:
    """A single turn in the conversation."""

    role: str  # "user" or "assistant"
    content: str
    mode: str  # "s2s" or "cascade"
    timestamp: float = 0.0
    metadata: dict[str, Any] = field(default_factory=dict)


class ContextSync:
    """
    Maintains and synchronizes context across pipeline modes.

    When switching between S2S and Cascade, generates a synopsis
    of the conversation state that is injected into the new
    pipeline's system prompt.
    """

    MAX_HISTORY_TURNS = 50
    SYNOPSIS_MAX_LENGTH = 500

    def __init__(self):
        self._turns: list[ConversationTurn] = []
        self._synopsis: str = ""
        self._user_state: dict[str, Any] = {}

    def add_turn(
        self,
        role: str,
        content: str,
        mode: str,
        metadata: dict[str, Any] | None = None,
    ) -> None:
        """Record a conversation turn."""
        import time

        turn = ConversationTurn(
            role=role,
            content=content,
            mode=mode,
            timestamp=time.time(),
            metadata=metadata or {},
        )
        self._turns.append(turn)

        # Trim history
        if len(self._turns) > self.MAX_HISTORY_TURNS:
            self._turns = self._turns[-self.MAX_HISTORY_TURNS :]

        # Update synopsis
        self._update_synopsis()

    def get_synopsis(self) -> str:
        """
        Get a short synopsis of the conversation for context injection.

        The synopsis is designed to be injected as a system prompt
        when switching between pipeline modes.
        """
        return self._synopsis

    def get_context_for_mode(self, target_mode: str) -> dict[str, Any]:
        """
        Get context package for injecting into a pipeline mode.

        Args:
            target_mode: The mode being switched to ("s2s" or "cascade").

        Returns:
            Context dict with synopsis, recent turns, and user state.
        """
        recent = self._turns[-6:]  # Last 3 exchanges
        return {
            "synopsis": self._synopsis,
            "recent_turns": [{"role": t.role, "content": t.content[:200]} for t in recent],
            "user_state": self._user_state,
            "turn_count": len(self._turns),
            "previous_mode": self._turns[-1].mode if self._turns else None,
            "target_mode": target_mode,
        }

    def generate_system_prompt_injection(self, target_mode: str) -> str:
        """
        Generate a system prompt addition for the target pipeline.

        This is prepended to the LLM's system prompt during handoffs.
        """
        if not self._turns:
            return ""

        parts = [
            "Conversation context (continuing from previous mode):",
            f"Synopsis: {self._synopsis}",
        ]

        if self._user_state:
            state_str = ", ".join(f"{k}: {v}" for k, v in self._user_state.items())
            parts.append(f"User state: {state_str}")

        parts.append("Continue the conversation naturally.")
        return "\n".join(parts)

    def update_user_state(self, key: str, value: Any) -> None:
        """Update tracked user state (e.g., emotional state, topic)."""
        self._user_state[key] = value

    def _update_synopsis(self) -> None:
        """Update the conversation synopsis from recent history."""
        if not self._turns:
            self._synopsis = ""
            return

        # Build synopsis from last few turns
        recent = self._turns[-4:]
        parts = []
        for turn in recent:
            prefix = "User" if turn.role == "user" else "AI"
            short_content = turn.content[:100]
            if len(turn.content) > 100:
                short_content += "..."
            parts.append(f"{prefix}: {short_content}")

        synopsis = " | ".join(parts)
        if len(synopsis) > self.SYNOPSIS_MAX_LENGTH:
            synopsis = synopsis[: self.SYNOPSIS_MAX_LENGTH] + "..."

        self._synopsis = synopsis

    def reset(self) -> None:
        """Reset all context."""
        self._turns.clear()
        self._synopsis = ""
        self._user_state.clear()
