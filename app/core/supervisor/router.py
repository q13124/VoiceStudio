"""
Supervisor Router for VoiceStudio (Phase 11.1.3)

Routes audio/text input to the appropriate pipeline (S2S, Cascade, or HalfCascade)
based on classifier output, cost constraints, and state machine state.

Integrates filler phrases for smooth transitions, context sync across modes,
barge-in handling for interruptions, and intent buffering for cooperative speech.
"""

import logging
import time
from typing import Any, Dict, Optional

logger = logging.getLogger(__name__)

from .classifier import ClassificationResult, ComplexityLevel, IntentClassifier
from .state_machine import SupervisorState, SupervisorStateMachine
from .filler_generator import FillerPhraseGenerator
from .context_sync import ContextSync
from .barge_in import BargeInHandler
from .intent_buffer import IntentBuffer
from .interruption_fsm import InterruptionFSM


class SupervisorRouter:
    """
    Routes input between S2S, Cascade, and Half-Cascade pipelines.

    Decision flow:
    1. Receive user input (audio or text)
    2. Classify intent and complexity
    3. Check cost constraints
    4. Route to appropriate pipeline
    5. Generate filler phrases during mode transitions
    6. Sync context across pipeline switches
    7. Handle interruptions via barge-in handler
    """

    def __init__(
        self,
        s2s_provider=None,
        cascade_pipeline=None,
        half_cascade_pipeline=None,
        classifier: Optional[IntentClassifier] = None,
        token_ceiling_manager=None,
        filler_generator: Optional[FillerPhraseGenerator] = None,
        context_sync: Optional[ContextSync] = None,
        barge_in_handler: Optional[BargeInHandler] = None,
        intent_buffer: Optional[IntentBuffer] = None,
    ):
        self._s2s = s2s_provider
        self._cascade = cascade_pipeline
        self._half_cascade = half_cascade_pipeline
        self._classifier = classifier or IntentClassifier()
        self._ceiling = token_ceiling_manager
        self._filler = filler_generator or FillerPhraseGenerator()
        self._context_sync = context_sync or ContextSync()
        self._barge_in = barge_in_handler or BargeInHandler(
            on_stop=self._on_barge_in_stop
        )
        self._intent_buffer = intent_buffer or IntentBuffer()
        self._fsm = SupervisorStateMachine()
        self._session_id: Optional[str] = None
        self._context: Dict[str, Any] = {}
        self._previous_mode: Optional[str] = None

    @property
    def state(self) -> SupervisorState:
        return self._fsm.state

    @property
    def active_mode(self) -> Optional[str]:
        return self._fsm.active_mode

    async def process_input(
        self,
        text: str,
        audio_data: Optional[bytes] = None,
    ) -> Dict[str, Any]:
        """
        Process user input through the supervisor routing logic.

        Args:
            text: User text (from STT or direct input).
            audio_data: Optional raw audio data.

        Returns:
            Dict with response text, audio, and routing metadata.
        """
        start_time = time.perf_counter()

        # Check for buffered input from cooperative interruptions
        buffered = self._intent_buffer.flush()
        if buffered:
            text = f"{buffered} {text}".strip()
            logger.debug(f"Including buffered input: {buffered[:50]}...")

        # Step 1: Analyze
        self._fsm.transition(SupervisorState.ANALYZING, trigger="user_input")

        classification = self._classifier.classify(text, self._context)

        # Step 2: Check cost ceiling
        if self._ceiling and self._session_id:
            ceiling_status = self._ceiling.get_session_status(self._session_id)
            if ceiling_status and ceiling_status.get("ceiling_reached"):
                # Force cascade mode (cheaper)
                classification = ClassificationResult(
                    complexity=classification.complexity,
                    confidence=1.0,
                    requires_tool_call=classification.requires_tool_call,
                    requires_reasoning=True,
                    suggested_route="cascade",
                    latency_ms=classification.latency_ms,
                    features={**classification.features, "ceiling_forced": True},
                )

        # Step 3: Route
        route = classification.suggested_route
        previous_route = self._context.get("previous_route")
        self._context["previous_route"] = route

        # Record context
        self._context_sync.add_turn("user", text, route)

        result: Dict[str, Any] = {
            "route": route,
            "classification": {
                "complexity": classification.complexity.value,
                "confidence": classification.confidence,
                "latency_ms": classification.latency_ms,
            },
        }

        # Step 4: Handle mode transition with filler phrase
        if previous_route and previous_route != route:
            filler = self._filler.get_filler_for_handoff(previous_route, route)
            result["transition_filler"] = filler
            # Inject context for the new mode
            context_injection = self._context_sync.generate_system_prompt_injection(
                route
            )
            result["context_injection"] = context_injection
            logger.info(f"Mode transition: {previous_route} → {route}")

        try:
            if route == "s2s" and self._s2s:
                response = await self._process_s2s(text, audio_data)
            elif route == "half_cascade" and self._half_cascade:
                response = await self._process_half_cascade(text, audio_data)
            else:
                response = await self._process_cascade(text)

            result.update(response)

            # Record assistant response in context
            if response.get("response_text"):
                self._context_sync.add_turn(
                    "assistant", response["response_text"], route
                )

        except Exception as exc:
            logger.error(f"Route processing failed: {exc}")
            self._fsm.transition(SupervisorState.ERROR, trigger=str(exc))
            # Fallback to cascade
            if route != "cascade":
                try:
                    fallback_response = await self._process_cascade(text)
                    result.update(fallback_response)
                    result["fallback"] = True
                    result["fallback_from"] = route
                except Exception as fallback_exc:
                    result["error"] = str(fallback_exc)
            else:
                result["error"] = str(exc)

        result["total_latency_ms"] = (time.perf_counter() - start_time) * 1000
        self._previous_mode = route
        self._fsm.transition(SupervisorState.IDLE, trigger="response_complete")
        return result

    async def _process_s2s(
        self,
        text: str,
        audio_data: Optional[bytes] = None,
    ) -> Dict[str, Any]:
        """Process through S2S pipeline."""
        self._fsm.transition(SupervisorState.CASUAL_MODE, trigger="s2s_route")

        if audio_data and self._s2s:
            response = await self._s2s.respond(audio_data, context=text)
            self._fsm.transition(SupervisorState.RESPONDING, trigger="s2s_response")
            return {
                "response_text": response.response_text or "",
                "audio_data": response.audio_data,
                "latency_ms": response.latency_ms,
                "mode": "s2s",
            }

        # Fallback: if no audio, use cascade
        return await self._process_cascade(text)

    async def _process_cascade(self, text: str) -> Dict[str, Any]:
        """Process through Cascade pipeline."""
        self._fsm.transition(SupervisorState.REASONING_MODE, trigger="cascade_route")

        if self._cascade:
            result = await self._cascade.process_text(text)
            self._fsm.transition(SupervisorState.RESPONDING, trigger="cascade_response")
            return {
                "response_text": result.get("response", ""),
                "audio_data": result.get("audio"),
                "metrics": result.get("metrics"),
                "mode": "cascade",
            }

        return {
            "response_text": "Pipeline not initialized",
            "mode": "cascade",
            "error": "No cascade pipeline available",
        }

    async def _process_half_cascade(
        self,
        text: str,
        audio_data: Optional[bytes] = None,
    ) -> Dict[str, Any]:
        """Process through Half-Cascade pipeline (S2S input + TTS output)."""
        self._fsm.transition(SupervisorState.REASONING_MODE, trigger="half_cascade")

        if self._half_cascade and audio_data:
            result = await self._half_cascade.process_audio(audio_data, context=text)
            self._fsm.transition(
                SupervisorState.RESPONDING, trigger="half_cascade_response"
            )
            return {
                "response_text": result.get("response_text", ""),
                "audio_data": result.get("audio"),
                "metrics": result.get("metrics"),
                "mode": "half_cascade",
            }

        # No audio data or no half-cascade, fall back to cascade
        return await self._process_cascade(text)

    async def handle_interruption(
        self,
        text: str = "",
        audio_energy: float = 0.0,
    ) -> Dict[str, Any]:
        """
        Handle user interruption (barge-in) using the barge-in handler.

        Args:
            text: Transcribed user speech during AI output.
            audio_energy: Audio energy level (0.0-1.0).

        Returns:
            Interruption handling result.
        """
        current = self._fsm.state

        # Set AI speaking state based on current FSM state
        is_speaking = current in (
            SupervisorState.RESPONDING,
            SupervisorState.CASUAL_MODE,
        )
        self._barge_in.set_ai_speaking(is_speaking)

        result = await self._barge_in.handle_user_speech(text, audio_energy)

        # If action is stop, transition to interrupted
        if result.get("action") == "stop":
            self._fsm.transition(SupervisorState.INTERRUPTED, trigger="barge_in")
            if self._s2s:
                try:
                    await self._s2s.interrupt()
                except Exception as exc:
                    logger.warning(f"S2S interrupt failed: {exc}")

        # If action is buffer, add to intent buffer for cooperative handling
        elif result.get("action") == "buffer" and text:
            self._intent_buffer.add(
                text=text,
                audio_energy=audio_energy,
                interruption_type=result.get("type", ""),
            )

        return result

    async def _on_barge_in_stop(self) -> None:
        """Callback when barge-in requires stopping AI output."""
        if self._s2s:
            try:
                await self._s2s.interrupt()
            except Exception as exc:
                logger.warning(f"Barge-in stop callback failed: {exc}")

    def set_session(self, session_id: str) -> None:
        """Set the current session for cost tracking."""
        self._session_id = session_id

    def get_context(self) -> Dict[str, Any]:
        """Get the current context including synopsis."""
        return self._context_sync.get_context_for_mode(
            self._previous_mode or "cascade"
        )

    def reset(self) -> None:
        """Reset supervisor state."""
        self._fsm.reset()
        self._context.clear()
        self._context_sync.reset()
        self._intent_buffer.clear()
        self._session_id = None
        self._previous_mode = None
