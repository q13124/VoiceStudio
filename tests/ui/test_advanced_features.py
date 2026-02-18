"""
Advanced Feature Tests.

Tests for advanced VoiceStudio features:
- Multi-voice synthesis
- Emotion control
- Voice model training
- Batch processing
- Pipeline conversations
- Pronunciation lexicon

Requires:
- WinAppDriver running
- Backend running on port 8001
- VoiceStudio application built
"""

from __future__ import annotations

import os

# Import tracing infrastructure
import sys
import time
from pathlib import Path

import pytest
import requests

sys.path.insert(0, str(Path(__file__).parent))
from tracing.api_monitor import APIMonitor
from tracing.workflow_tracer import WorkflowTracer

from fixtures import get_test_audio_path, get_test_script

# Test configuration
BACKEND_URL = os.getenv("VOICESTUDIO_BACKEND_URL", "http://127.0.0.1:8001")
OUTPUT_DIR = Path(os.getenv("VOICESTUDIO_OUTPUT_DIR", ".buildlogs/validation"))
TRACE_ENABLED = os.getenv("VOICESTUDIO_TRACE_ENABLED", "1") == "1"
SCREENSHOTS_ENABLED = os.getenv("VOICESTUDIO_SCREENSHOTS_ENABLED", "1") == "1"

# Pytest markers
pytestmark = [
    pytest.mark.advanced,
    pytest.mark.features,
]


@pytest.fixture
def tracer():
    """Create a workflow tracer for this test."""
    tracer = WorkflowTracer("advanced_features", OUTPUT_DIR)
    tracer.start()
    yield tracer
    tracer.export_report()


@pytest.fixture
def api_monitor():
    """Create an API monitor for tracking backend calls."""
    monitor = APIMonitor(base_url=BACKEND_URL)
    yield monitor
    monitor.export_log(OUTPUT_DIR / "api_coverage" / "advanced_features_api_calls.json")


class TestMultiVoiceSynthesis:
    """Tests for multi-voice synthesis features."""

    @pytest.mark.smoke
    def test_multi_voice_endpoint_exists(self, api_monitor, tracer):
        """Test that multi-voice synthesis endpoint exists."""
        tracer.step("Testing multi-voice endpoint")

        try:
            # Try to get endpoint info
            response = api_monitor.get("/api/voice/multi-synthesize")
            tracer.api_call("GET", "/api/voice/multi-synthesize", response)

            # 405 means endpoint exists but method not allowed
            if response.status_code in [200, 405]:
                tracer.step("Multi-voice endpoint exists")
                tracer.success("Multi-voice endpoint available")
            elif response.status_code == 404:
                tracer.step("Multi-voice endpoint not found")
            else:
                tracer.step(f"Multi-voice: {response.status_code}")

        except Exception as e:
            tracer.error(e, "Multi-voice endpoint check failed")

    def test_multi_voice_synthesis(self, api_monitor, tracer):
        """Test multi-voice synthesis with multiple segments."""
        tracer.step("Testing multi-voice synthesis")

        payload = {
            "segments": [
                {
                    "text": "Hello, I am the first speaker.",
                    "voice_id": "default",
                    "speaker": "Speaker 1"
                },
                {
                    "text": "And I am the second speaker.",
                    "voice_id": "default",
                    "speaker": "Speaker 2"
                },
                {
                    "text": "Now I am speaking again.",
                    "voice_id": "default",
                    "speaker": "Speaker 1"
                },
            ],
            "output_format": "wav",
        }

        try:
            response = requests.post(
                f"{BACKEND_URL}/api/voice/multi-synthesize",
                json=payload,
                timeout=120
            )
            tracer.api_call("POST", "/api/voice/multi-synthesize", response)

            if response.status_code in [200, 201, 202]:
                tracer.step("Multi-voice synthesis successful")
                tracer.success("Multi-voice synthesis works")
            elif response.status_code == 404:
                tracer.step("Multi-voice endpoint not implemented")
            else:
                tracer.step(f"Multi-voice synthesis: {response.status_code}")

        except Exception as e:
            tracer.error(e, "Multi-voice synthesis failed")

    def test_multi_voice_ui_panel(self, driver, app_launched, tracer):
        """Test multi-voice panel in UI."""
        tracer.step("Looking for multi-voice panel", driver, SCREENSHOTS_ENABLED)

        try:
            nav_options = [
                ("accessibility id", "NavMultiVoice"),
                ("accessibility id", "NavMultiSpeaker"),
                ("xpath", "//*[contains(@Name, 'Multi')]"),
            ]

            for by, value in nav_options:
                try:
                    element = driver.find_element(by, value)
                    element.click()
                    time.sleep(1)
                    tracer.step(f"Found multi-voice nav: {value}", driver, SCREENSHOTS_ENABLED)
                    tracer.success("Multi-voice panel found")
                    return
                except Exception:
                    continue

            tracer.step("No multi-voice panel found")

        except Exception as e:
            tracer.error(e, "Multi-voice panel search failed")


class TestEmotionControl:
    """Tests for emotion control in synthesis."""

    def test_emotion_list(self, api_monitor, tracer):
        """Test getting list of available emotions."""
        tracer.step("Getting available emotions")

        try:
            response = api_monitor.get("/api/voice/emotions")
            tracer.api_call("GET", "/api/voice/emotions", response)

            if response.status_code == 200:
                emotions = response.json()
                tracer.step(f"Emotions: {emotions}")
                tracer.success("Emotion list retrieved")
            elif response.status_code == 404:
                tracer.step("Emotions endpoint not found")
            else:
                tracer.step(f"Emotions: {response.status_code}")

        except Exception as e:
            tracer.error(e, "Emotion list failed")

    @pytest.mark.parametrize("emotion", ["happy", "sad", "angry", "neutral", "excited"])
    def test_synthesis_with_emotion(self, emotion, api_monitor, tracer):
        """Test synthesis with different emotions."""
        tracer.step(f"Testing synthesis with emotion: {emotion}")

        payload = {
            "text": get_test_script("emotional"),
            "voice_id": "default",
            "emotion": emotion,
        }

        try:
            response = requests.post(
                f"{BACKEND_URL}/api/voice/synthesize",
                json=payload,
                timeout=60
            )
            tracer.api_call("POST", f"/api/voice/synthesize (emotion={emotion})", response)

            if response.status_code in [200, 201, 202]:
                tracer.step(f"Emotion {emotion}: OK")
            elif response.status_code == 422:
                # Emotion not supported
                tracer.step(f"Emotion {emotion}: not supported")
            else:
                tracer.step(f"Emotion {emotion}: {response.status_code}")

        except Exception as e:
            tracer.step(f"Emotion {emotion} failed: {e}")

    def test_emotion_intensity(self, api_monitor, tracer):
        """Test emotion intensity control."""
        tracer.step("Testing emotion intensity")

        payload = {
            "text": "This is an emotional test.",
            "voice_id": "default",
            "emotion": "happy",
            "emotion_intensity": 0.8,  # 80% intensity
        }

        try:
            response = requests.post(
                f"{BACKEND_URL}/api/voice/synthesize",
                json=payload,
                timeout=60
            )
            tracer.api_call("POST", "/api/voice/synthesize (intensity)", response)

            if response.status_code in [200, 201, 202]:
                tracer.step("Emotion intensity: OK")
                tracer.success("Emotion intensity works")
            else:
                tracer.step(f"Emotion intensity: {response.status_code}")

        except Exception as e:
            tracer.error(e, "Emotion intensity failed")


class TestVoiceModelTraining:
    """Tests for voice model training features."""

    def test_training_status(self, api_monitor, tracer):
        """Test training status endpoint."""
        tracer.step("Getting training status")

        try:
            response = api_monitor.get("/api/training/status")
            tracer.api_call("GET", "/api/training/status", response)

            if response.status_code == 200:
                status = response.json()
                tracer.step(f"Training status: {status}")
                tracer.success("Training status retrieved")
            elif response.status_code == 404:
                tracer.step("Training status endpoint not found")
            else:
                tracer.step(f"Training status: {response.status_code}")

        except Exception as e:
            tracer.error(e, "Training status failed")

    def test_list_datasets(self, api_monitor, tracer):
        """Test listing training datasets."""
        tracer.step("Getting training datasets")

        try:
            response = api_monitor.get("/api/training/datasets")
            tracer.api_call("GET", "/api/training/datasets", response)

            if response.status_code == 200:
                datasets = response.json()
                count = len(datasets) if isinstance(datasets, list) else "N/A"
                tracer.step(f"Datasets: {count}")
                tracer.success("Datasets retrieved")
            elif response.status_code == 404:
                tracer.step("Datasets endpoint not found")
            else:
                tracer.step(f"Datasets: {response.status_code}")

        except Exception as e:
            tracer.error(e, "Datasets failed")

    def test_training_config(self, api_monitor, tracer):
        """Test training configuration."""
        tracer.step("Getting training config")

        try:
            response = api_monitor.get("/api/training/config")
            tracer.api_call("GET", "/api/training/config", response)

            if response.status_code == 200:
                config = response.json()
                tracer.step(f"Training config: {config}")
                tracer.success("Training config retrieved")
            elif response.status_code == 404:
                tracer.step("Training config endpoint not found")
            else:
                tracer.step(f"Training config: {response.status_code}")

        except Exception as e:
            tracer.error(e, "Training config failed")

    def test_training_ui_panel(self, driver, app_launched, tracer):
        """Test training panel in UI."""
        tracer.step("Looking for training panel", driver, SCREENSHOTS_ENABLED)

        try:
            nav_options = [
                ("accessibility id", "NavTraining"),
                ("accessibility id", "NavTrain"),
                ("xpath", "//*[contains(@Name, 'Train')]"),
            ]

            for by, value in nav_options:
                try:
                    element = driver.find_element(by, value)
                    element.click()
                    time.sleep(1)
                    tracer.step(f"Found training nav: {value}", driver, SCREENSHOTS_ENABLED)
                    tracer.success("Training panel found")
                    return
                except Exception:
                    continue

            tracer.step("No training panel found")

        except Exception as e:
            tracer.error(e, "Training panel search failed")


class TestBatchProcessing:
    """Tests for batch processing features."""

    def test_batch_status(self, api_monitor, tracer):
        """Test batch processing status."""
        tracer.step("Getting batch status")

        try:
            response = api_monitor.get("/api/batch/status")
            tracer.api_call("GET", "/api/batch/status", response)

            if response.status_code == 200:
                status = response.json()
                tracer.step(f"Batch status: {status}")
                tracer.success("Batch status retrieved")
            elif response.status_code == 404:
                tracer.step("Batch status endpoint not found")
            else:
                tracer.step(f"Batch status: {response.status_code}")

        except Exception as e:
            tracer.error(e, "Batch status failed")

    def test_batch_synthesis(self, api_monitor, tracer):
        """Test batch synthesis."""
        tracer.step("Testing batch synthesis")

        payload = {
            "items": [
                {"text": "First item to synthesize.", "voice_id": "default"},
                {"text": "Second item to synthesize.", "voice_id": "default"},
                {"text": "Third item to synthesize.", "voice_id": "default"},
            ],
            "output_format": "wav",
        }

        try:
            response = requests.post(
                f"{BACKEND_URL}/api/batch/synthesize",
                json=payload,
                timeout=180
            )
            tracer.api_call("POST", "/api/batch/synthesize", response)

            if response.status_code in [200, 201, 202]:
                result = response.json()
                tracer.step(f"Batch result: {result}")
                tracer.success("Batch synthesis works")
            elif response.status_code == 404:
                tracer.step("Batch synthesis endpoint not found")
            else:
                tracer.step(f"Batch synthesis: {response.status_code}")

        except Exception as e:
            tracer.error(e, "Batch synthesis failed")

    def test_batch_transcription(self, api_monitor, tracer):
        """Test batch transcription."""
        tracer.step("Testing batch transcription")

        test_audio = get_test_audio_path("reference_clean")
        if not test_audio.exists():
            pytest.skip("Test audio not found")

        try:
            with open(test_audio, "rb") as f:
                files = {"files": (test_audio.name, f, "audio/wav")}
                response = requests.post(
                    f"{BACKEND_URL}/api/batch/transcribe",
                    files=files,
                    timeout=180
                )
                tracer.api_call("POST", "/api/batch/transcribe", response)

                if response.status_code in [200, 201, 202]:
                    tracer.step("Batch transcription successful")
                    tracer.success("Batch transcription works")
                elif response.status_code == 404:
                    tracer.step("Batch transcription endpoint not found")
                else:
                    tracer.step(f"Batch transcription: {response.status_code}")

        except Exception as e:
            tracer.error(e, "Batch transcription failed")


class TestPipelineConversation:
    """Tests for pipeline conversation features."""

    def test_pipeline_list(self, api_monitor, tracer):
        """Test listing pipelines."""
        tracer.step("Getting pipelines")

        try:
            response = api_monitor.get("/api/pipelines")
            tracer.api_call("GET", "/api/pipelines", response)

            if response.status_code == 200:
                pipelines = response.json()
                count = len(pipelines) if isinstance(pipelines, list) else "N/A"
                tracer.step(f"Pipelines: {count}")
                tracer.success("Pipelines retrieved")
            elif response.status_code == 404:
                tracer.step("Pipelines endpoint not found")
            else:
                tracer.step(f"Pipelines: {response.status_code}")

        except Exception as e:
            tracer.error(e, "Pipelines failed")

    def test_conversation_start(self, api_monitor, tracer):
        """Test starting a conversation."""
        tracer.step("Testing conversation start")

        payload = {
            "voice_id": "default",
            "context": "You are a helpful assistant.",
        }

        try:
            response = requests.post(
                f"{BACKEND_URL}/api/conversation/start",
                json=payload,
                timeout=30
            )
            tracer.api_call("POST", "/api/conversation/start", response)

            if response.status_code in [200, 201, 202]:
                result = response.json()
                tracer.step(f"Conversation started: {result}")
                tracer.success("Conversation start works")
            elif response.status_code == 404:
                tracer.step("Conversation start endpoint not found")
            else:
                tracer.step(f"Conversation start: {response.status_code}")

        except Exception as e:
            tracer.error(e, "Conversation start failed")


class TestPronunciationLexicon:
    """Tests for pronunciation lexicon features."""

    def test_lexicon_list(self, api_monitor, tracer):
        """Test listing lexicon entries."""
        tracer.step("Getting lexicon entries")

        try:
            response = api_monitor.get("/api/lexicon")
            tracer.api_call("GET", "/api/lexicon", response)

            if response.status_code == 200:
                entries = response.json()
                count = len(entries) if isinstance(entries, list) else "N/A"
                tracer.step(f"Lexicon entries: {count}")
                tracer.success("Lexicon retrieved")
            elif response.status_code == 404:
                tracer.step("Lexicon endpoint not found")
            else:
                tracer.step(f"Lexicon: {response.status_code}")

        except Exception as e:
            tracer.error(e, "Lexicon failed")

    def test_add_lexicon_entry(self, api_monitor, tracer):
        """Test adding a lexicon entry."""
        tracer.step("Testing add lexicon entry")

        payload = {
            "word": "VoiceStudio",
            "pronunciation": "voice studio",
            "phonemes": "v OY s s t UW d IY OW",
        }

        try:
            response = requests.post(
                f"{BACKEND_URL}/api/lexicon",
                json=payload,
                timeout=30
            )
            tracer.api_call("POST", "/api/lexicon", response)

            if response.status_code in [200, 201]:
                tracer.step("Lexicon entry added")
                tracer.success("Add lexicon entry works")
            elif response.status_code == 404:
                tracer.step("Lexicon endpoint not found")
            else:
                tracer.step(f"Add lexicon: {response.status_code}")

        except Exception as e:
            tracer.error(e, "Add lexicon failed")

    def test_synthesis_with_lexicon(self, api_monitor, tracer):
        """Test synthesis using custom pronunciation."""
        tracer.step("Testing synthesis with lexicon")

        payload = {
            "text": "Welcome to VoiceStudio.",
            "voice_id": "default",
            "use_lexicon": True,
        }

        try:
            response = requests.post(
                f"{BACKEND_URL}/api/voice/synthesize",
                json=payload,
                timeout=60
            )
            tracer.api_call("POST", "/api/voice/synthesize (lexicon)", response)

            if response.status_code in [200, 201, 202]:
                tracer.step("Synthesis with lexicon successful")
                tracer.success("Lexicon synthesis works")
            else:
                tracer.step(f"Lexicon synthesis: {response.status_code}")

        except Exception as e:
            tracer.error(e, "Lexicon synthesis failed")


class TestJobQueue:
    """Tests for job queue features."""

    def test_job_list(self, api_monitor, tracer):
        """Test listing jobs."""
        tracer.step("Getting job list")

        try:
            response = api_monitor.get("/api/jobs")
            tracer.api_call("GET", "/api/jobs", response)

            if response.status_code == 200:
                jobs = response.json()
                count = len(jobs) if isinstance(jobs, list) else "N/A"
                tracer.step(f"Jobs: {count}")
                tracer.success("Jobs retrieved")
            elif response.status_code == 404:
                tracer.step("Jobs endpoint not found")
            else:
                tracer.step(f"Jobs: {response.status_code}")

        except Exception as e:
            tracer.error(e, "Jobs failed")

    def test_job_status(self, api_monitor, tracer):
        """Test getting job status by ID."""
        tracer.step("Testing job status")

        # First try to get a job ID from the list
        try:
            response = api_monitor.get("/api/jobs")
            job_id = None

            if response.status_code == 200:
                jobs = response.json()
                if isinstance(jobs, list) and len(jobs) > 0:
                    job = jobs[0]
                    if isinstance(job, dict):
                        job_id = job.get("id") or job.get("job_id")

            if job_id:
                response = api_monitor.get(f"/api/jobs/{job_id}")
                tracer.api_call("GET", f"/api/jobs/{job_id}", response)

                if response.status_code == 200:
                    status = response.json()
                    tracer.step(f"Job {job_id} status: {status}")
                    tracer.success("Job status works")
                else:
                    tracer.step(f"Job status: {response.status_code}")
            else:
                tracer.step("No jobs available for status test")

        except Exception as e:
            tracer.error(e, "Job status failed")


class TestAdvancedFeaturesReport:
    """Generate advanced features report."""

    @pytest.mark.smoke
    def test_generate_advanced_report(self, api_monitor, tracer):
        """Generate comprehensive advanced features report."""
        tracer.step("Generating advanced features report")

        features = {
            "Multi-voice": "/api/voice/multi-synthesize",
            "Emotions": "/api/voice/emotions",
            "Training Status": "/api/training/status",
            "Datasets": "/api/training/datasets",
            "Batch Status": "/api/batch/status",
            "Pipelines": "/api/pipelines",
            "Lexicon": "/api/lexicon",
            "Jobs": "/api/jobs",
        }

        available = []
        unavailable = []

        for feature, endpoint in features.items():
            try:
                response = api_monitor.get(endpoint)
                if response.status_code in [200, 405]:  # 405 = method exists
                    available.append(feature)
                    tracer.step(f"✓ {feature}")
                else:
                    unavailable.append(feature)
                    tracer.step(f"✗ {feature}")
            except Exception:
                unavailable.append(feature)
                tracer.step(f"✗ {feature} (error)")

        # Summary
        total = len(features)
        avail_count = len(available)
        coverage = (avail_count / total * 100) if total > 0 else 0

        tracer.step("\n=== Advanced Features Summary ===")
        tracer.step(f"Total features: {total}")
        tracer.step(f"Available: {avail_count}")
        tracer.step(f"Coverage: {coverage:.1f}%")

        # Write report
        report_path = OUTPUT_DIR / "advanced_features_report.txt"
        report_path.parent.mkdir(parents=True, exist_ok=True)

        with open(report_path, "w", encoding="utf-8") as f:
            f.write("VoiceStudio Advanced Features Report\n")
            f.write("=" * 40 + "\n\n")
            f.write(f"Total features: {total}\n")
            f.write(f"Available: {avail_count}\n")
            f.write(f"Coverage: {coverage:.1f}%\n\n")
            f.write("Available:\n")
            for feat in available:
                f.write(f"  ✓ {feat}\n")
            f.write("\nUnavailable:\n")
            for feat in unavailable:
                f.write(f"  ✗ {feat}\n")

        tracer.step(f"Report written to: {report_path}")
        tracer.success("Advanced features report generated")


# Run tests directly if executed as script
if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
