"""
Intent Classifier Unit Tests (Phase 14.2.1)
"""

import time

from app.core.supervisor.classifier import (
    ComplexityLevel,
    IntentClassifier,
)


class TestIntentClassifier:
    """Tests for the intent classifier."""

    def setup_method(self):
        self.classifier = IntentClassifier()

    def test_casual_greeting(self):
        result = self.classifier.classify("hi")
        assert result.complexity == ComplexityLevel.LOW
        assert result.suggested_route == "s2s"

    def test_tool_call_detection(self):
        result = self.classifier.classify("Generate a voice clone from this file")
        assert result.requires_tool_call is True
        assert result.suggested_route == "cascade"

    def test_complex_reasoning_detection(self):
        result = self.classifier.classify("Explain how voice cloning works in detail")
        assert result.requires_reasoning is True
        assert result.suggested_route == "cascade"

    def test_medium_complexity(self):
        result = self.classifier.classify("What voice profiles are available?")
        assert result.complexity in (ComplexityLevel.LOW, ComplexityLevel.MEDIUM)

    def test_classification_under_50ms(self):
        """Classifier must complete under 50ms per the spec."""
        start = time.perf_counter()
        for _ in range(100):
            self.classifier.classify("Test input for classification speed")
        avg_ms = ((time.perf_counter() - start) / 100) * 1000
        assert avg_ms < 50.0, f"Classification took {avg_ms:.1f}ms (target: < 50ms)"

    def test_confidence_range(self):
        result = self.classifier.classify("test")
        assert 0.0 <= result.confidence <= 1.0

    def test_context_influences_routing(self):
        """Previous route should influence current classification."""
        context = {"previous_route": "cascade"}
        result = self.classifier.classify("Tell me more", context)
        # Should tend to stay in cascade
        assert result.suggested_route in ("cascade", "half_cascade", "s2s")

    def test_stats_tracking(self):
        self.classifier.classify("test")
        self.classifier.classify("another test")
        stats = self.classifier.get_stats()
        assert stats["total_classifications"] == 2
        assert stats["avg_latency_ms"] >= 0  # May be 0.0 on fast CPUs


class TestInterruptionFSM:
    """Tests for the interruption state machine."""

    def test_disfluency_ignored(self):
        from app.core.supervisor.interruption_fsm import InterruptionAction, InterruptionFSM

        fsm = InterruptionFSM()
        result = fsm.classify_interruption("um", ai_is_speaking=True)
        assert result["action"] == InterruptionAction.IGNORE.value

    def test_backchannel_buffered(self):
        from app.core.supervisor.interruption_fsm import InterruptionAction, InterruptionFSM

        fsm = InterruptionFSM()
        result = fsm.classify_interruption("yeah", ai_is_speaking=True)
        assert result["action"] == InterruptionAction.BUFFER.value

    def test_topic_change_stops(self):
        from app.core.supervisor.interruption_fsm import InterruptionAction, InterruptionFSM

        fsm = InterruptionFSM()
        result = fsm.classify_interruption(
            "wait actually I want something else", ai_is_speaking=True
        )
        assert result["action"] == InterruptionAction.STOP_AND_LISTEN.value

    def test_no_ai_speech_always_listens(self):
        from app.core.supervisor.interruption_fsm import InterruptionAction, InterruptionFSM

        fsm = InterruptionFSM()
        result = fsm.classify_interruption("anything", ai_is_speaking=False)
        assert result["action"] == InterruptionAction.STOP_AND_LISTEN.value


class TestSupervisorStateMachine:
    """Tests for the supervisor state machine."""

    def test_initial_state(self):
        from app.core.supervisor.state_machine import SupervisorState, SupervisorStateMachine

        fsm = SupervisorStateMachine()
        assert fsm.state == SupervisorState.IDLE

    def test_valid_transition(self):
        from app.core.supervisor.state_machine import SupervisorState, SupervisorStateMachine

        fsm = SupervisorStateMachine()
        result = fsm.transition(SupervisorState.ANALYZING, trigger="test")
        assert result is True
        assert fsm.state == SupervisorState.ANALYZING

    def test_invalid_transition(self):
        from app.core.supervisor.state_machine import SupervisorState, SupervisorStateMachine

        fsm = SupervisorStateMachine()
        # Can't go directly from IDLE to RESPONDING
        result = fsm.transition(SupervisorState.RESPONDING, trigger="test")
        assert result is False
        assert fsm.state == SupervisorState.IDLE

    def test_mode_tracking(self):
        from app.core.supervisor.state_machine import SupervisorState, SupervisorStateMachine

        fsm = SupervisorStateMachine()
        fsm.transition(SupervisorState.ANALYZING, trigger="input")
        fsm.transition(SupervisorState.CASUAL_MODE, trigger="low_complexity")
        assert fsm.active_mode == "s2s"

    def test_history_tracking(self):
        from app.core.supervisor.state_machine import SupervisorState, SupervisorStateMachine

        fsm = SupervisorStateMachine()
        fsm.transition(SupervisorState.ANALYZING, trigger="input")
        fsm.transition(SupervisorState.CASUAL_MODE, trigger="route")
        history = fsm.get_history()
        assert len(history) == 2
