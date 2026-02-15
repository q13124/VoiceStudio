"""
Pipeline Orchestrator Unit Tests (Phase 14.1.1)
"""


from app.core.pipeline.orchestrator import (
    PipelineConfig,
    PipelineMode,
    PipelineOrchestrator,
    PipelineState,
)


class TestPipelineConfig:
    """Tests for PipelineConfig defaults."""

    def test_default_mode_is_streaming(self):
        config = PipelineConfig()
        assert config.mode == PipelineMode.STREAMING

    def test_default_engines(self):
        config = PipelineConfig()
        assert config.stt_engine == "whisper"
        assert config.llm_provider == "ollama"
        assert config.tts_engine == "xtts_v2"

    def test_custom_config(self):
        config = PipelineConfig(
            mode=PipelineMode.BATCH,
            llm_provider="openai",
            language="fr",
        )
        assert config.mode == PipelineMode.BATCH
        assert config.llm_provider == "openai"
        assert config.language == "fr"


class TestPipelineOrchestrator:
    """Tests for PipelineOrchestrator lifecycle."""

    def test_initial_state_is_idle(self):
        orchestrator = PipelineOrchestrator()
        assert orchestrator.state == PipelineState.IDLE

    def test_pipeline_id_is_unique(self):
        o1 = PipelineOrchestrator()
        o2 = PipelineOrchestrator()
        assert o1.pipeline_id != o2.pipeline_id

    def test_state_change_callback(self):
        states = []
        orchestrator = PipelineOrchestrator()
        orchestrator.on_state_change(lambda old, new: states.append((old, new)))

        orchestrator._set_state(PipelineState.TRANSCRIBING)
        assert len(states) == 1
        assert states[0] == (PipelineState.IDLE, PipelineState.TRANSCRIBING)

    def test_reset_clears_history(self):
        orchestrator = PipelineOrchestrator()
        orchestrator._conversation_history.append({"role": "user", "content": "test"})
        orchestrator._set_state(PipelineState.REASONING)

        orchestrator.reset()
        assert orchestrator.state == PipelineState.IDLE
        assert len(orchestrator._conversation_history) == 0


class TestPipelineMode:
    """Tests for pipeline mode enum."""

    def test_streaming_mode(self):
        assert PipelineMode.STREAMING.value == "streaming"

    def test_batch_mode(self):
        assert PipelineMode.BATCH.value == "batch"

    def test_half_cascade_mode(self):
        assert PipelineMode.HALF_CASCADE.value == "half_cascade"
