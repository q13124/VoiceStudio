"""
Token Ceiling Strategy for VoiceStudio (Phase 10.3.1)

Implements automatic switching from expensive S2S models to the cheaper
cascaded pipeline when token usage exceeds a configurable threshold.
This prevents runaway costs from context accumulation in S2S APIs.
"""

import logging
import time
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Callable, Dict, Optional

logger = logging.getLogger(__name__)


class CostTier(str, Enum):
    """Cost tier for different pipeline modes."""
    FREE = "free"        # Local models (Ollama, etc.)
    LOW = "low"          # Cascade with cloud STT/TTS
    MEDIUM = "medium"    # S2S with short conversations
    HIGH = "high"        # S2S with long context accumulation


@dataclass
class UsageRecord:
    """Record of token/audio usage for a session."""
    session_id: str
    provider: str
    input_tokens: int = 0
    output_tokens: int = 0
    audio_seconds_in: float = 0.0
    audio_seconds_out: float = 0.0
    turn_count: int = 0
    started_at: float = 0.0
    last_updated: float = 0.0


@dataclass
class CeilingConfig:
    """Configuration for token ceiling strategy."""
    # Token limits
    soft_ceiling_tokens: int = 50000   # Warn and suggest switching
    hard_ceiling_tokens: int = 100000  # Auto-switch to cascade
    # Time limits
    max_session_minutes: float = 15.0  # Auto-switch after this duration
    # Cost thresholds (approximate, in USD)
    max_estimated_cost: float = 1.0    # Max cost before auto-switch
    # Behavior
    auto_switch: bool = True
    notify_on_soft_ceiling: bool = True


class TokenCeilingManager:
    """
    Manages token ceiling and automatic pipeline switching.

    Monitors S2S session usage and triggers automatic transition
    to the cheaper cascaded pipeline when thresholds are exceeded.
    """

    # Approximate cost per token (varies by provider)
    COST_PER_INPUT_TOKEN = 0.000001    # ~$1/1M tokens
    COST_PER_OUTPUT_TOKEN = 0.000004   # ~$4/1M tokens
    COST_PER_AUDIO_SECOND = 0.0001     # ~$0.06/min

    def __init__(
        self,
        config: Optional[CeilingConfig] = None,
        on_switch: Optional[Callable] = None,
        on_warning: Optional[Callable] = None,
    ):
        self._config = config or CeilingConfig()
        self._on_switch = on_switch
        self._on_warning = on_warning
        self._sessions: Dict[str, UsageRecord] = {}
        self._switch_triggered: Dict[str, bool] = {}

    def start_session(self, session_id: str, provider: str) -> None:
        """Start tracking a new session."""
        self._sessions[session_id] = UsageRecord(
            session_id=session_id,
            provider=provider,
            started_at=time.time(),
            last_updated=time.time(),
        )
        self._switch_triggered[session_id] = False
        logger.info(f"Token ceiling tracking started: {session_id}")

    def record_usage(
        self,
        session_id: str,
        input_tokens: int = 0,
        output_tokens: int = 0,
        audio_seconds_in: float = 0.0,
        audio_seconds_out: float = 0.0,
    ) -> Dict[str, Any]:
        """
        Record usage and check ceiling.

        Returns:
            Status dict with ceiling check results.
        """
        if session_id not in self._sessions:
            return {"status": "unknown_session"}

        record = self._sessions[session_id]
        record.input_tokens += input_tokens
        record.output_tokens += output_tokens
        record.audio_seconds_in += audio_seconds_in
        record.audio_seconds_out += audio_seconds_out
        record.turn_count += 1
        record.last_updated = time.time()

        return self._check_ceiling(session_id)

    def _check_ceiling(self, session_id: str) -> Dict[str, Any]:
        """Check if any ceiling has been reached."""
        record = self._sessions[session_id]
        total_tokens = record.input_tokens + record.output_tokens
        elapsed_minutes = (time.time() - record.started_at) / 60.0
        estimated_cost = self._estimate_cost(record)

        result: Dict[str, Any] = {
            "session_id": session_id,
            "total_tokens": total_tokens,
            "elapsed_minutes": round(elapsed_minutes, 1),
            "estimated_cost_usd": round(estimated_cost, 4),
            "turn_count": record.turn_count,
            "should_switch": False,
            "reason": None,
        }

        # Hard ceiling: auto-switch
        if total_tokens >= self._config.hard_ceiling_tokens:
            result["should_switch"] = True
            result["reason"] = f"Hard token ceiling reached ({total_tokens}/{self._config.hard_ceiling_tokens})"

        elif elapsed_minutes >= self._config.max_session_minutes:
            result["should_switch"] = True
            result["reason"] = f"Session duration limit ({elapsed_minutes:.0f}/{self._config.max_session_minutes:.0f} min)"

        elif estimated_cost >= self._config.max_estimated_cost:
            result["should_switch"] = True
            result["reason"] = f"Cost ceiling reached (${estimated_cost:.4f}/${self._config.max_estimated_cost:.2f})"

        # Soft ceiling: warn
        elif total_tokens >= self._config.soft_ceiling_tokens:
            result["warning"] = f"Approaching token ceiling ({total_tokens}/{self._config.hard_ceiling_tokens})"
            if self._on_warning and self._config.notify_on_soft_ceiling:
                self._on_warning(result)

        # Trigger switch if needed
        if result["should_switch"] and self._config.auto_switch:
            if not self._switch_triggered.get(session_id, False):
                self._switch_triggered[session_id] = True
                logger.warning(f"Token ceiling reached for {session_id}: {result['reason']}")
                if self._on_switch:
                    self._on_switch(session_id, result)

        return result

    def _estimate_cost(self, record: UsageRecord) -> float:
        """Estimate the cost of a session's usage."""
        token_cost = (
            record.input_tokens * self.COST_PER_INPUT_TOKEN
            + record.output_tokens * self.COST_PER_OUTPUT_TOKEN
        )
        audio_cost = (
            (record.audio_seconds_in + record.audio_seconds_out)
            * self.COST_PER_AUDIO_SECOND
        )
        return token_cost + audio_cost

    def get_session_status(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Get usage status for a session."""
        if session_id not in self._sessions:
            return None
        record = self._sessions[session_id]
        return {
            "session_id": session_id,
            "provider": record.provider,
            "total_tokens": record.input_tokens + record.output_tokens,
            "turn_count": record.turn_count,
            "duration_minutes": round((time.time() - record.started_at) / 60.0, 1),
            "estimated_cost_usd": round(self._estimate_cost(record), 4),
            "ceiling_reached": self._switch_triggered.get(session_id, False),
        }

    def end_session(self, session_id: str) -> Optional[Dict[str, Any]]:
        """End a session and return final usage."""
        status = self.get_session_status(session_id)
        self._sessions.pop(session_id, None)
        self._switch_triggered.pop(session_id, None)
        return status
