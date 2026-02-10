"""
Supervisor State Machine for VoiceStudio (Phase 11.1.2)

Manages state transitions between Idle, Casual (S2S), Complex (Cascade),
and Handoff states for the hybrid supervisor architecture.
"""

import logging
import time
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Callable, Dict, List, Optional

logger = logging.getLogger(__name__)


class SupervisorState(str, Enum):
    """States in the supervisor state machine."""
    IDLE = "idle"
    ANALYZING = "analyzing"
    CASUAL_MODE = "casual_mode"        # S2S engine active
    REASONING_MODE = "reasoning_mode"  # Cascade pipeline active
    HANDOFF = "handoff"                # Transitioning between modes
    GENERATING_FILLER = "generating_filler"
    RESPONDING = "responding"
    INTERRUPTED = "interrupted"
    ERROR = "error"


@dataclass
class StateTransition:
    """Record of a state transition."""
    from_state: SupervisorState
    to_state: SupervisorState
    trigger: str
    timestamp: float
    metadata: Dict[str, Any] = field(default_factory=dict)


class SupervisorStateMachine:
    """
    Finite State Machine for the hybrid supervisor.

    Manages transitions between conversation modes with
    validation and event callbacks.
    """

    # Valid transitions: from_state -> set of valid to_states
    VALID_TRANSITIONS = {
        SupervisorState.IDLE: {
            SupervisorState.ANALYZING,
        },
        SupervisorState.ANALYZING: {
            SupervisorState.CASUAL_MODE,
            SupervisorState.REASONING_MODE,
            SupervisorState.IDLE,
        },
        SupervisorState.CASUAL_MODE: {
            SupervisorState.RESPONDING,
            SupervisorState.HANDOFF,
            SupervisorState.INTERRUPTED,
            SupervisorState.IDLE,
        },
        SupervisorState.REASONING_MODE: {
            SupervisorState.GENERATING_FILLER,
            SupervisorState.RESPONDING,
            SupervisorState.INTERRUPTED,
            SupervisorState.IDLE,
        },
        SupervisorState.GENERATING_FILLER: {
            SupervisorState.REASONING_MODE,
            SupervisorState.RESPONDING,
            SupervisorState.INTERRUPTED,
        },
        SupervisorState.HANDOFF: {
            SupervisorState.CASUAL_MODE,
            SupervisorState.REASONING_MODE,
            SupervisorState.GENERATING_FILLER,
            SupervisorState.ERROR,
        },
        SupervisorState.RESPONDING: {
            SupervisorState.IDLE,
            SupervisorState.INTERRUPTED,
        },
        SupervisorState.INTERRUPTED: {
            SupervisorState.ANALYZING,
            SupervisorState.IDLE,
        },
        SupervisorState.ERROR: {
            SupervisorState.IDLE,
            SupervisorState.ANALYZING,
        },
    }

    def __init__(self):
        self._state = SupervisorState.IDLE
        self._history: List[StateTransition] = []
        self._callbacks: Dict[str, List[Callable]] = {}
        self._active_mode: Optional[str] = None  # "s2s" or "cascade"

    @property
    def state(self) -> SupervisorState:
        return self._state

    @property
    def active_mode(self) -> Optional[str]:
        return self._active_mode

    def transition(
        self,
        to_state: SupervisorState,
        trigger: str = "",
        metadata: Optional[Dict[str, Any]] = None,
    ) -> bool:
        """
        Attempt a state transition.

        Args:
            to_state: Target state.
            trigger: What caused the transition.
            metadata: Additional context.

        Returns:
            True if transition was valid and completed.
        """
        valid_targets = self.VALID_TRANSITIONS.get(self._state, set())
        if to_state not in valid_targets:
            logger.warning(
                f"Invalid transition: {self._state.value} → {to_state.value} "
                f"(trigger: {trigger})"
            )
            return False

        old_state = self._state
        self._state = to_state

        # Track active mode
        if to_state == SupervisorState.CASUAL_MODE:
            self._active_mode = "s2s"
        elif to_state == SupervisorState.REASONING_MODE:
            self._active_mode = "cascade"

        transition = StateTransition(
            from_state=old_state,
            to_state=to_state,
            trigger=trigger,
            timestamp=time.time(),
            metadata=metadata or {},
        )
        self._history.append(transition)

        logger.debug(
            f"Supervisor: {old_state.value} → {to_state.value} ({trigger})"
        )

        # Fire callbacks
        self._fire_callbacks(old_state, to_state)

        return True

    def on_transition(
        self,
        callback: Callable[[SupervisorState, SupervisorState], None],
        from_state: Optional[SupervisorState] = None,
    ) -> None:
        """Register a callback for state transitions."""
        key = from_state.value if from_state else "_any"
        self._callbacks.setdefault(key, []).append(callback)

    def _fire_callbacks(
        self, from_state: SupervisorState, to_state: SupervisorState
    ) -> None:
        """Fire registered callbacks for this transition."""
        # Specific callbacks
        for cb in self._callbacks.get(from_state.value, []):
            try:
                cb(from_state, to_state)
            except Exception as exc:
                logger.warning(f"State callback failed: {exc}")

        # General callbacks
        for cb in self._callbacks.get("_any", []):
            try:
                cb(from_state, to_state)
            except Exception as exc:
                logger.warning(f"State callback failed: {exc}")

    def reset(self) -> None:
        """Reset to idle state."""
        self._state = SupervisorState.IDLE
        self._active_mode = None

    def get_history(self, count: int = 20) -> List[Dict[str, Any]]:
        """Get recent transition history."""
        return [
            {
                "from": t.from_state.value,
                "to": t.to_state.value,
                "trigger": t.trigger,
                "timestamp": t.timestamp,
            }
            for t in self._history[-count:]
        ]
