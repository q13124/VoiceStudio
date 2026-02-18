# VoiceStudio Plugin Testing Guide

Comprehensive guide to testing VoiceStudio plugins.

## Overview

Testing is essential for plugin quality and reliability. This guide covers unit testing, integration testing, and best practices for testing VoiceStudio plugins.

## Testing Stack

VoiceStudio plugins use:

- **pytest** - Test framework
- **pytest-asyncio** - Async test support
- **pytest-cov** - Coverage reporting
- **voicestudio_sdk.testing** - SDK testing utilities

## Quick Start

### Setup

```bash
# Install development dependencies
pip install voicestudio-plugin-sdk[dev]

# Or install individually
pip install pytest pytest-asyncio pytest-cov
```

### Run Tests

```bash
# Using CLI tool
voicestudio-plugin test

# Using pytest directly
python -m pytest tests/ -v

# With coverage
python -m pytest tests/ --cov=my_plugin --cov-report=html
```

## Test Structure

### Directory Layout

```
my-plugin/
├── my_plugin/
│   ├── __init__.py
│   └── main.py
├── tests/
│   ├── __init__.py
│   ├── conftest.py          # Shared fixtures
│   ├── test_plugin.py       # Core plugin tests
│   ├── test_synthesis.py    # Feature-specific tests
│   └── test_integration.py  # Integration tests
└── pytest.ini               # Pytest configuration
```

### pytest.ini

```ini
[pytest]
asyncio_mode = auto
testpaths = tests
python_files = test_*.py
python_classes = Test*
python_functions = test_*
addopts = -v --tb=short
markers =
    slow: marks tests as slow
    integration: integration tests
    gpu: tests requiring GPU
```

## SDK Testing Utilities

### PluginTestCase

Base class that simplifies plugin testing:

```python
import pytest
from voicestudio_sdk.testing import PluginTestCase, MockHost
from my_plugin.main import MyPlugin

class TestMyPlugin(PluginTestCase):
    plugin_class = MyPlugin
    
    # setUp() is called before each test
    # tearDown() is called after each test
    # self.plugin - initialized plugin instance
    # self.host - MockHost instance
    
    async def test_basic_operation(self):
        """Test basic plugin operation."""
        result = await self.plugin.process(self.create_test_audio())
        self.assert_valid_audio(result)
```

### MockHost

Mock implementation of the Host API:

```python
from voicestudio_sdk.testing import MockHost

def test_with_mock_host():
    host = MockHost()
    
    # Pre-configure resources
    host.set_resource("models/config.json", b'{"key": "value"}')
    
    # Pre-configure settings
    host.set_setting("model_size", "large")
    
    # Pre-configure capabilities
    host.set_capability("gpu", True)
    
    # Set confirm response
    host.set_confirm_response(True)
    
    # Set version
    host.set_version("2.5.0")
    
    # Use with plugin...
    ctx = PluginContext(plugin_id="test", host_api=host)
    await plugin.initialize(ctx)
    
    # Verify interactions
    assert host.has_log("info", "initialized")
    assert len(host.progress_reports) > 0
```

### Test Helpers

```python
from voicestudio_sdk.testing import (
    create_test_manifest,
    create_test_plugin_directory,
)

def test_manifest_loading():
    """Test manifest creation."""
    manifest = create_test_manifest(
        plugin_id="com.test.my-plugin",
        name="My Plugin",
        version="1.0.0",
        plugin_type="synthesis",
        capabilities=["streaming"],
    )
    
    assert manifest["id"] == "com.test.my-plugin"
    assert manifest["version"] == "1.0.0"

def test_plugin_directory(tmp_path):
    """Test plugin directory creation."""
    plugin_dir = create_test_plugin_directory(
        base_dir=str(tmp_path),
        plugin_id="com.test.plugin",
        create_module=True,
    )
    
    assert (Path(plugin_dir) / "plugin.json").exists()
    assert (Path(plugin_dir) / "com_test_plugin").is_dir()
```

## Writing Tests

### Basic Plugin Tests

```python
import pytest
from voicestudio_sdk import PluginContext, PluginMetadata
from voicestudio_sdk.testing import PluginTestCase, MockHost
from my_plugin.main import MySynthesisPlugin

class TestMySynthesisPlugin(PluginTestCase):
    plugin_class = MySynthesisPlugin
    
    async def test_initialize(self):
        """Test plugin initialization."""
        assert self.plugin.is_initialized
        assert self.host.has_log("info", "initialized")
    
    async def test_synthesize_simple(self):
        """Test simple text synthesis."""
        result = await self.plugin.synthesize("Hello world")
        
        self.assert_valid_audio(result)
        assert result.duration > 0
        assert result.sample_rate == 22050
    
    async def test_synthesize_with_options(self):
        """Test synthesis with options."""
        result = await self.plugin.synthesize(
            "Hello world",
            voice="female",
            speed=1.5,
        )
        
        self.assert_valid_audio(result)
    
    async def test_get_voices(self):
        """Test voice listing."""
        voices = await self.plugin.get_voices()
        
        assert isinstance(voices, list)
        assert len(voices) > 0
        assert "default" in voices
    
    async def test_shutdown(self):
        """Test graceful shutdown."""
        await self.plugin.shutdown()
        assert not self.plugin.is_initialized
```

### Testing with Configuration

```python
class TestPluginConfiguration(PluginTestCase):
    plugin_class = MyPlugin
    
    async def test_with_custom_config(self):
        """Test plugin with custom configuration."""
        ctx = self.create_context(
            config={
                "model_size": "large",
                "quality": "high",
                "enable_cache": True,
            }
        )
        
        await self.plugin.initialize(ctx)
        
        # Verify config was applied
        assert self.plugin._model_size == "large"
    
    async def test_missing_required_config(self):
        """Test error on missing required config."""
        ctx = self.create_context(config={})
        
        with pytest.raises(ValueError, match="api_key"):
            await self.plugin.initialize(ctx)
    
    async def test_invalid_config_value(self):
        """Test error on invalid config value."""
        ctx = self.create_context(
            config={"quality": "invalid"}
        )
        
        with pytest.raises(ValueError):
            await self.plugin.initialize(ctx)
```

### Testing Audio Operations

```python
import math
import struct
from voicestudio_sdk import AudioBuffer, AudioFormat

class TestAudioProcessing(PluginTestCase):
    plugin_class = MyProcessingPlugin
    
    async def test_audio_normalization(self):
        """Test audio normalization."""
        # Create quiet audio
        quiet_audio = self.create_test_audio(amplitude=0.1)
        
        result = await self.plugin.normalize(quiet_audio)
        
        # Verify normalization increased amplitude
        self.assert_valid_audio(result)
        # Check peak level is close to target
    
    async def test_audio_format_conversion(self):
        """Test format conversion."""
        wav_audio = self.create_test_audio()
        
        result = await self.plugin.convert(wav_audio, format="mp3")
        
        assert result.format == AudioFormat.MP3
        self.assert_valid_audio(result)
    
    async def test_stereo_processing(self):
        """Test stereo audio processing."""
        stereo_audio = AudioBuffer(
            data=self._create_stereo_samples(),
            sample_rate=44100,
            channels=2,
        )
        
        result = await self.plugin.process(stereo_audio)
        
        assert result.channels == 2
    
    def _create_stereo_samples(self) -> bytes:
        """Create stereo audio samples."""
        duration = 1.0
        sample_rate = 44100
        samples = []
        
        for i in range(int(duration * sample_rate)):
            t = i / sample_rate
            left = int(32767 * math.sin(2 * math.pi * 440 * t))
            right = int(32767 * math.sin(2 * math.pi * 880 * t))
            samples.extend([left, right])
        
        return struct.pack(f"<{len(samples)}h", *samples)
```

### Testing Host Interactions

```python
class TestHostInteractions(PluginTestCase):
    plugin_class = MyPlugin
    
    async def test_progress_reporting(self):
        """Test progress is reported correctly."""
        await self.plugin.process_large_file("test.wav")
        
        progress_reports = self.host.progress_reports
        
        assert len(progress_reports) > 0
        assert progress_reports[0].progress == 0.0
        assert progress_reports[-1].progress == 1.0
    
    async def test_logging(self):
        """Test logging behavior."""
        await self.plugin.process(self.create_test_audio())
        
        # Check specific log messages
        assert self.host.has_log("info", "Processing started")
        assert self.host.has_log("debug", "Processing complete")
        
        # Check no errors logged
        error_logs = self.host.get_logs(level="error")
        assert len(error_logs) == 0
    
    async def test_resource_access(self):
        """Test resource access."""
        # Pre-configure resource
        self.host.set_resource(
            "models/my-model.bin",
            b"model data..."
        )
        
        await self.plugin.load_model()
        
        # Verify resource was accessed
        # (implementation-specific verification)
    
    async def test_notification(self):
        """Test user notifications."""
        await self.plugin.complete_task()
        
        notifications = self.host.notifications
        assert any(n["message"] == "Task complete!" for n in notifications)
    
    async def test_confirmation_accepted(self):
        """Test confirmation when user accepts."""
        self.host.set_confirm_response(True)
        
        result = await self.plugin.delete_with_confirm()
        
        assert result is True
    
    async def test_confirmation_rejected(self):
        """Test confirmation when user rejects."""
        self.host.set_confirm_response(False)
        
        result = await self.plugin.delete_with_confirm()
        
        assert result is False
```

### Testing Error Handling

```python
class TestErrorHandling(PluginTestCase):
    plugin_class = MyPlugin
    
    async def test_invalid_input_error(self):
        """Test handling of invalid input."""
        with pytest.raises(ValueError, match="cannot be empty"):
            await self.plugin.synthesize("")
    
    async def test_file_not_found_error(self):
        """Test handling of missing file."""
        with pytest.raises(FileNotFoundError):
            await self.plugin.load_from_file("nonexistent.wav")
    
    async def test_network_error_handling(self):
        """Test graceful network error handling."""
        # Simulate network failure
        self.host.set_resource("network/api", None)
        
        with pytest.raises(RuntimeError, match="network"):
            await self.plugin.fetch_remote_data()
        
        # Verify error was logged
        assert self.host.has_log("error", "network")
    
    async def test_timeout_handling(self):
        """Test timeout handling."""
        with pytest.raises(TimeoutError):
            await self.plugin.slow_operation(timeout=0.1)
    
    async def test_graceful_degradation(self):
        """Test graceful degradation on non-critical failure."""
        # Disable optional feature
        self.host.set_capability("gpu", False)
        
        # Should still work, just slower
        result = await self.plugin.process(self.create_test_audio())
        
        self.assert_valid_audio(result)
        assert self.host.has_log("warning", "GPU not available")
```

## Fixtures

### conftest.py

```python
import pytest
from pathlib import Path
from voicestudio_sdk.testing import MockHost, create_test_manifest

@pytest.fixture
def mock_host():
    """Provide a clean MockHost for each test."""
    host = MockHost()
    host.set_version("2.5.0")
    host.set_capability("gpu", True)
    return host

@pytest.fixture
def sample_audio(tmp_path):
    """Provide sample audio file."""
    audio_path = tmp_path / "sample.wav"
    # Create sample WAV file
    create_sample_wav(audio_path)
    return audio_path

@pytest.fixture
def plugin_dir(tmp_path):
    """Create temporary plugin directory."""
    from voicestudio_sdk.testing import create_test_plugin_directory
    return create_test_plugin_directory(str(tmp_path))

@pytest.fixture
def manifest():
    """Provide test manifest."""
    return create_test_manifest(
        plugin_id="com.test.fixture-plugin",
        name="Fixture Plugin",
    )
```

## Integration Tests

### Testing with Real Audio

```python
import pytest
from pathlib import Path

@pytest.mark.integration
class TestRealAudioProcessing:
    """Integration tests with real audio files."""
    
    @pytest.fixture
    def audio_samples(self):
        """Load real audio samples."""
        samples_dir = Path(__file__).parent / "samples"
        return {
            "speech": samples_dir / "speech.wav",
            "music": samples_dir / "music.wav",
            "noise": samples_dir / "noise.wav",
        }
    
    async def test_real_speech_synthesis(self, initialized_plugin):
        """Test synthesis with realistic text."""
        text = """
        Welcome to VoiceStudio. This is a test of the text-to-speech
        system with realistic content including punctuation, numbers
        like 123, and various sentence structures.
        """
        
        result = await initialized_plugin.synthesize(text)
        
        assert result.duration > 5.0  # Should be several seconds
        assert result.sample_rate == 22050
    
    async def test_real_transcription(self, initialized_plugin, audio_samples):
        """Test transcription of real audio."""
        audio = AudioBuffer.from_file(str(audio_samples["speech"]))
        
        result = await initialized_plugin.transcribe(audio)
        
        assert len(result) > 0
        assert "hello" in result.lower()  # Expected word
```

### Testing End-to-End Workflows

```python
@pytest.mark.integration
class TestEndToEndWorkflows:
    """Test complete user workflows."""
    
    async def test_synthesis_transcription_roundtrip(self):
        """Test TTS followed by STT produces similar text."""
        original_text = "Hello, this is a test."
        
        # Synthesize
        tts_plugin = MySynthesisPlugin()
        await tts_plugin.initialize(ctx)
        audio = await tts_plugin.synthesize(original_text)
        
        # Transcribe
        stt_plugin = MyTranscriptionPlugin()
        await stt_plugin.initialize(ctx)
        transcribed = await stt_plugin.transcribe(audio)
        
        # Compare (fuzzy match)
        assert similarity(original_text, transcribed) > 0.8
    
    async def test_audio_processing_pipeline(self):
        """Test multi-step processing pipeline."""
        # Load -> Enhance -> Process -> Save
        audio = AudioBuffer.from_file("input.wav")
        
        enhanced = await enhancement_plugin.enhance(audio)
        processed = await processing_plugin.process(enhanced)
        
        processed.save("output.wav")
        
        # Verify output
        output = AudioBuffer.from_file("output.wav")
        assert output.duration == audio.duration
```

## Performance Testing

```python
import pytest
import time

@pytest.mark.slow
class TestPerformance:
    """Performance and stress tests."""
    
    async def test_synthesis_performance(self, initialized_plugin):
        """Test synthesis meets performance requirements."""
        text = "Hello world, this is a performance test."
        
        start = time.perf_counter()
        result = await initialized_plugin.synthesize(text)
        elapsed = time.perf_counter() - start
        
        # Should complete within 2 seconds
        assert elapsed < 2.0
        # Real-time factor should be reasonable
        rtf = elapsed / result.duration
        assert rtf < 1.0  # Faster than real-time
    
    async def test_batch_processing(self, initialized_plugin):
        """Test batch processing efficiency."""
        texts = [f"Text number {i}" for i in range(10)]
        
        start = time.perf_counter()
        results = await initialized_plugin.synthesize_batch(texts)
        elapsed = time.perf_counter() - start
        
        assert len(results) == 10
        # Batch should be faster than sequential
        assert elapsed < 10.0
    
    async def test_memory_usage(self, initialized_plugin):
        """Test memory doesn't grow unbounded."""
        import tracemalloc
        
        tracemalloc.start()
        
        for _ in range(100):
            await initialized_plugin.synthesize("Test text")
        
        current, peak = tracemalloc.get_traced_memory()
        tracemalloc.stop()
        
        # Peak memory should be reasonable (< 500MB)
        assert peak < 500 * 1024 * 1024
```

## Coverage

### Coverage Configuration

```ini
# pytest.ini or pyproject.toml
[tool.coverage.run]
source = ["my_plugin"]
branch = true
omit = ["tests/*"]

[tool.coverage.report]
exclude_lines = [
    "pragma: no cover",
    "if TYPE_CHECKING:",
    "raise NotImplementedError",
]
fail_under = 80
```

### Running with Coverage

```bash
# Generate coverage report
pytest --cov=my_plugin --cov-report=html

# Check coverage threshold
pytest --cov=my_plugin --cov-fail-under=80
```

## Markers

### Using Test Markers

```python
import pytest

@pytest.mark.slow
async def test_large_file_processing():
    """Slow test for large files."""
    pass

@pytest.mark.integration
async def test_external_api():
    """Requires external API."""
    pass

@pytest.mark.gpu
async def test_gpu_acceleration():
    """Requires GPU."""
    pass

@pytest.mark.skip(reason="Not implemented yet")
async def test_future_feature():
    pass

@pytest.mark.skipif(
    not has_gpu(),
    reason="GPU not available"
)
async def test_gpu_specific():
    pass
```

### Running Specific Markers

```bash
# Run only fast tests
pytest -m "not slow"

# Run only unit tests
pytest -m "not integration"

# Run GPU tests
pytest -m "gpu"
```

## Best Practices

### 1. Test Independence

Each test should be independent:

```python
# ❌ BAD: Tests depend on order
class TestBad:
    shared_state = None
    
    def test_setup(self):
        self.shared_state = "initialized"
    
    def test_use(self):
        assert self.shared_state == "initialized"  # Fails if run alone

# ✅ GOOD: Tests are independent
class TestGood:
    @pytest.fixture
    def state(self):
        return "initialized"
    
    def test_use(self, state):
        assert state == "initialized"
```

### 2. Descriptive Names

```python
# ❌ BAD
def test_1():
    pass

# ✅ GOOD
def test_synthesize_returns_audio_for_valid_text():
    pass

def test_synthesize_raises_error_for_empty_text():
    pass
```

### 3. AAA Pattern

Arrange-Act-Assert:

```python
async def test_synthesis_with_custom_voice():
    # Arrange
    plugin = MySynthesisPlugin()
    await plugin.initialize(ctx)
    text = "Hello world"
    voice = "female"
    
    # Act
    result = await plugin.synthesize(text, voice=voice)
    
    # Assert
    assert result.duration > 0
    assert result.sample_rate == 22050
```

### 4. Test Edge Cases

```python
class TestEdgeCases:
    async def test_empty_input(self):
        """Test empty input handling."""
        with pytest.raises(ValueError):
            await plugin.synthesize("")
    
    async def test_very_long_input(self):
        """Test maximum input length."""
        long_text = "a" * 100000
        with pytest.raises(ValueError, match="too long"):
            await plugin.synthesize(long_text)
    
    async def test_special_characters(self):
        """Test special character handling."""
        result = await plugin.synthesize("Hello <world> & \"friends\"!")
        assert result.duration > 0
    
    async def test_unicode_input(self):
        """Test unicode handling."""
        result = await plugin.synthesize("こんにちは世界 🌍")
        assert result.duration > 0
```

## Troubleshooting

### Common Issues

**Tests hang on async operations:**
```python
# Use timeout
@pytest.mark.timeout(30)
async def test_with_timeout():
    await plugin.slow_operation()
```

**Flaky tests:**
```python
# Use retry for flaky tests (last resort)
@pytest.mark.flaky(reruns=3)
async def test_network_dependent():
    pass
```

**Resource leaks:**
```python
# Always clean up
@pytest.fixture
async def plugin():
    p = MyPlugin()
    await p.initialize(ctx)
    yield p
    await p.shutdown()  # Cleanup
```

## See Also

- [SDK Reference](./PLUGIN_SDK_REFERENCE.md)
- [Development Guide](./PLUGIN_DEVELOPMENT_GUIDE.md)
- [pytest Documentation](https://docs.pytest.org/)
