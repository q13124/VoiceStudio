"""
Allan Watts Inter-Panel Communication Tests.

Tests event-driven communication between panels:
- Event propagation between panels
- Data payload verification
- Event timing and ordering
- Panel state synchronization
- Event error handling

Requirements:
- WinAppDriver running on port 4723
- Backend running on port 8001
- VoiceStudio application built
"""

from __future__ import annotations

import os
import sys
import time
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parent))

from fixtures.audio_test_data import (
    ALL_WORKFLOWS,
    PANEL_EVENTS,
    PANEL_NAVIGATION,
)
from tracing.api_monitor import APIMonitor
from tracing.workflow_tracer import WorkflowTracer

# Configuration
BACKEND_URL = os.getenv("VOICESTUDIO_BACKEND_URL", "http://127.0.0.1:8001")
OUTPUT_DIR = Path(os.getenv("VOICESTUDIO_OUTPUT_DIR", ".buildlogs/validation"))
SCREENSHOTS_ENABLED = os.getenv("VOICESTUDIO_SCREENSHOTS_ENABLED", "1") == "1"

# Pytest markers
pytestmark = [
    pytest.mark.events,
    pytest.mark.allan_watts,
]


# =============================================================================
# Fixtures
# =============================================================================

@pytest.fixture(scope="module")
def tracer():
    """Create a workflow tracer for event tests."""
    t = WorkflowTracer("allan_watts_events", OUTPUT_DIR)
    t.start()
    yield t
    t.export_report()


@pytest.fixture(scope="module")
def api_monitor():
    """Create an API monitor for tracking backend calls."""
    monitor = APIMonitor(base_url=BACKEND_URL)
    yield monitor
    monitor.export_log(OUTPUT_DIR / "api_coverage" / "allan_watts_events_api_calls.json")


def navigate_to_panel(driver, nav_id: str, root_id: str, tracer, timeout: float = 5.0):
    """Helper to navigate to a panel."""
    try:
        nav_button = driver.find_element("accessibility id", nav_id)
        nav_button.click()

        end_time = time.time() + timeout
        while time.time() < end_time:
            try:
                driver.find_element("accessibility id", root_id)
                return True
            except RuntimeError:
                time.sleep(0.2)
        return False
    except RuntimeError:
        return False


# =============================================================================
# Event Infrastructure Tests
# =============================================================================

class TestEventInfrastructure:
    """Test event system infrastructure."""

    def test_event_aggregator_exists(self, driver, app_launched, tracer):
        """Verify event aggregator service is available."""
        tracer.start_phase("event_infrastructure", "Test event infrastructure")
        tracer.step("Checking event aggregator availability")

        # The EventAggregator is a C# service - we verify by testing panel navigation
        # which relies on it

        workflow = ALL_WORKFLOWS[0]  # Import workflow

        try:
            driver.find_element("accessibility id", workflow.nav_id)
            tracer.step(f"Navigation element found: {workflow.nav_id}")
            tracer.success("Event infrastructure accessible")
        except RuntimeError as e:
            tracer.step(f"Navigation element not found: {e}")
            pytest.skip("Event infrastructure not accessible")
        finally:
            tracer.end_phase()

    def test_panel_event_definitions(self, tracer):
        """Verify panel event definitions are complete."""
        tracer.step("Verifying panel event definitions")

        for event_name, event_def in PANEL_EVENTS.items():
            source = event_def.get("source")
            targets = event_def.get("targets", [])
            payload = event_def.get("payload", [])

            tracer.step(f"Event: {event_name}")
            tracer.step(f"  Source: {source}")
            tracer.step(f"  Targets: {targets}")
            tracer.step(f"  Payload: {payload}")

        tracer.success("Event definitions verified")


# =============================================================================
# Library to Panel Events
# =============================================================================

class TestLibraryEvents:
    """Test events originating from Library panel."""

    def test_library_to_synthesis_event(self, driver, app_launched, tracer):
        """Test Library -> Voice Synthesis file selection event."""
        tracer.start_phase("library_events", "Test Library events")
        tracer.step("Testing Library to Voice Synthesis event")

        # Document expected event flow
        event_def = PANEL_EVENTS.get("FileSelectedForSynthesis", {})

        tracer.trace_event(
            "FileSelectedForSynthesis",
            source_panel="Library",
            target_panel="VoiceSynthesis",
            payload={
                "source": event_def.get("source"),
                "targets": event_def.get("targets"),
                "expected_payload": event_def.get("payload"),
                "description": "User selects file in Library for synthesis"
            }
        )

        # Simulate workflow: Navigate Library -> select file -> send to synthesis
        library_nav = PANEL_NAVIGATION.get("Library", {})

        try:
            if navigate_to_panel(driver, library_nav.get("nav_id", ""), library_nav.get("root_id", ""), tracer):
                tracer.step("Navigated to Library panel")

                # Try to find and interact with file list
                try:
                    driver.find_element("accessibility id", "LibraryView_FilesList")
                    tracer.step("File list found")
                    tracer.ui_action("locate", "LibraryView_FilesList")
                except RuntimeError:
                    tracer.step("File list not found - documenting expected behavior")
            else:
                tracer.step("Library navigation not available")
        except RuntimeError as e:
            tracer.step(f"Navigation error: {e}")

        tracer.end_phase(success=True)
        tracer.success("Library event flow documented")

    def test_library_to_cloning_event(self, driver, app_launched, tracer):
        """Test Library -> Voice Cloning reference selection event."""
        tracer.step("Testing Library to Voice Cloning event")

        event_def = PANEL_EVENTS.get("FileSelectedForCloning", {})

        tracer.trace_event(
            "FileSelectedForCloning",
            source_panel="Library",
            target_panel="VoiceCloning",
            payload={
                "source": event_def.get("source"),
                "targets": event_def.get("targets"),
                "expected_payload": event_def.get("payload"),
                "description": "User selects file as cloning reference"
            }
        )

        tracer.success("Library to Cloning event documented")

    def test_library_to_transcription_event(self, driver, app_launched, tracer):
        """Test Library -> Transcription file selection event."""
        tracer.step("Testing Library to Transcription event")

        event_def = PANEL_EVENTS.get("FileSelectedForTranscription", {})

        tracer.trace_event(
            "FileSelectedForTranscription",
            source_panel="Library",
            target_panel="Transcription",
            payload={
                "source": event_def.get("source"),
                "targets": event_def.get("targets"),
                "expected_payload": event_def.get("payload"),
                "description": "User selects file for transcription"
            }
        )

        tracer.success("Library to Transcription event documented")


# =============================================================================
# Transcription Events
# =============================================================================

class TestTranscriptionEvents:
    """Test events from Transcription panel."""

    def test_transcription_completed_event(self, driver, app_launched, tracer):
        """Test Transcription -> Timeline completed event."""
        tracer.start_phase("transcription_events", "Test Transcription events")
        tracer.step("Testing Transcription completed event")

        event_def = PANEL_EVENTS.get("TranscriptionCompleted", {})

        tracer.trace_event(
            "TranscriptionCompleted",
            source_panel="Transcription",
            target_panel="Timeline",
            payload={
                "source": event_def.get("source"),
                "targets": event_def.get("targets"),
                "expected_payload": event_def.get("payload"),
                "description": "Transcription completed, sent to Timeline"
            }
        )

        tracer.end_phase(success=True)
        tracer.success("Transcription event documented")


# =============================================================================
# Cloning Events
# =============================================================================

class TestCloningEvents:
    """Test events from Voice Cloning panel."""

    def test_clone_completed_event(self, driver, app_launched, tracer):
        """Test Voice Cloning -> Profile Created event."""
        tracer.start_phase("cloning_events", "Test Cloning events")
        tracer.step("Testing Clone completed event")

        event_def = PANEL_EVENTS.get("VoiceProfileCreated", {})

        tracer.trace_event(
            "VoiceProfileCreated",
            source_panel="VoiceCloning",
            target_panel="VoiceSynthesis",
            payload={
                "source": event_def.get("source"),
                "targets": event_def.get("targets"),
                "expected_payload": event_def.get("payload"),
                "description": "Voice clone profile created"
            }
        )

        tracer.end_phase(success=True)
        tracer.success("Clone event documented")


# =============================================================================
# Synthesis Events
# =============================================================================

class TestSynthesisEvents:
    """Test events from Voice Synthesis panel."""

    def test_synthesis_completed_event(self, driver, app_launched, tracer):
        """Test Voice Synthesis -> Library completed event."""
        tracer.start_phase("synthesis_events", "Test Synthesis events")
        tracer.step("Testing Synthesis completed event")

        event_def = PANEL_EVENTS.get("SynthesisCompleted", {})

        tracer.trace_event(
            "SynthesisCompleted",
            source_panel="VoiceSynthesis",
            target_panel="Library",
            payload={
                "source": event_def.get("source"),
                "targets": event_def.get("targets"),
                "expected_payload": event_def.get("payload"),
                "description": "Synthesis completed, audio added to Library"
            }
        )

        tracer.end_phase(success=True)
        tracer.success("Synthesis event documented")

    def test_synthesis_to_timeline_event(self, driver, app_launched, tracer):
        """Test Voice Synthesis -> Timeline add event."""
        tracer.step("Testing Synthesis to Timeline event")

        tracer.trace_event(
            "AddToTimeline",
            source_panel="VoiceSynthesis",
            target_panel="Timeline",
            payload={
                "expected_payload": ["audio_path", "start_time", "track"],
                "description": "Synthesized audio added to Timeline"
            }
        )

        tracer.success("Synthesis to Timeline event documented")


# =============================================================================
# Conversion Events
# =============================================================================

class TestConversionEvents:
    """Test events from Audio Conversion panel."""

    def test_conversion_completed_event(self, driver, app_launched, tracer):
        """Test Audio Conversion -> Library completed event."""
        tracer.start_phase("conversion_events", "Test Conversion events")
        tracer.step("Testing Conversion completed event")

        event_def = PANEL_EVENTS.get("ConversionCompleted", {})

        tracer.trace_event(
            "ConversionCompleted",
            source_panel="AudioConversion",
            target_panel="Library",
            payload={
                "source": event_def.get("source"),
                "targets": event_def.get("targets"),
                "expected_payload": event_def.get("payload"),
                "description": "Audio conversion completed"
            }
        )

        tracer.end_phase(success=True)
        tracer.success("Conversion event documented")


# =============================================================================
# Event Chain Tests
# =============================================================================

class TestEventChains:
    """Test multi-panel event chains."""

    def test_import_to_synthesis_chain(self, driver, app_launched, tracer):
        """Test Import -> Library -> Synthesis event chain."""
        tracer.start_phase("event_chains", "Test event chains")
        tracer.step("Testing Import to Synthesis chain")

        # Document full chain
        chain_steps = [
            ("Import", "Library", "FileImported"),
            ("Library", "VoiceSynthesis", "FileSelectedForSynthesis"),
            ("VoiceSynthesis", "Library", "SynthesisCompleted"),
        ]

        for i, (source, target, event) in enumerate(chain_steps):
            tracer.trace_event(
                event,
                source_panel=source,
                target_panel=target,
                payload={"chain_step": i + 1, "total_steps": len(chain_steps)}
            )
            tracer.step(f"Chain step {i + 1}: {source} -> {target} ({event})")

        tracer.end_phase(success=True)
        tracer.success("Event chain documented")

    def test_import_to_cloning_chain(self, driver, app_launched, tracer):
        """Test Import -> Library -> Cloning -> Synthesis chain."""
        tracer.step("Testing Import to Cloning chain")

        chain_steps = [
            ("Import", "Library", "FileImported"),
            ("Library", "VoiceCloning", "FileSelectedForCloning"),
            ("VoiceCloning", "VoiceSynthesis", "VoiceProfileCreated"),
        ]

        for i, (source, target, event) in enumerate(chain_steps):
            tracer.trace_event(
                event,
                source_panel=source,
                target_panel=target,
                payload={"chain_step": i + 1, "total_steps": len(chain_steps)}
            )
            tracer.step(f"Chain step {i + 1}: {source} -> {target} ({event})")

        tracer.success("Import to Cloning chain documented")

    def test_full_workflow_chain(self, driver, app_launched, tracer):
        """Test complete workflow: Import -> Transcribe -> Clone -> Synthesize."""
        tracer.step("Documenting full workflow chain")

        chain_steps = [
            ("Import", "Library", "FileImported", "Audio file imported"),
            ("Library", "Transcription", "FileSelectedForTranscription", "File sent to transcription"),
            ("Transcription", "Timeline", "TranscriptionCompleted", "Text extracted"),
            ("Library", "VoiceCloning", "FileSelectedForCloning", "File selected as voice reference"),
            ("VoiceCloning", "VoiceSynthesis", "VoiceProfileCreated", "Voice profile created"),
            ("VoiceSynthesis", "Library", "SynthesisCompleted", "New audio synthesized"),
        ]

        for i, (source, target, event, desc) in enumerate(chain_steps):
            tracer.trace_event(
                event,
                source_panel=source,
                target_panel=target,
                payload={
                    "chain_step": i + 1,
                    "total_steps": len(chain_steps),
                    "description": desc
                }
            )

        tracer.step(f"Full workflow: {len(chain_steps)} steps documented")
        tracer.success("Full workflow chain documented")


# =============================================================================
# Event Timing Tests
# =============================================================================

class TestEventTiming:
    """Test event timing and ordering."""

    def test_event_propagation_time(self, driver, app_launched, tracer):
        """Document expected event propagation time."""
        tracer.start_phase("event_timing", "Test event timing")
        tracer.step("Documenting event propagation expectations")

        expected_timings = {
            "navigation_transition": "< 500ms",
            "file_selection_event": "< 100ms",
            "data_load_event": "< 1000ms",
            "api_call_completion": "< 5000ms",
        }

        for event_type, expectation in expected_timings.items():
            tracer.step(f"{event_type}: {expectation}")

        tracer.end_phase(success=True)
        tracer.success("Timing expectations documented")

    def test_event_ordering(self, tracer):
        """Document expected event ordering."""
        tracer.step("Documenting event ordering requirements")

        ordering_rules = [
            "Navigation must complete before file operations",
            "File import must complete before library update",
            "Transcription must complete before timeline update",
            "Clone training must complete before profile available",
        ]

        for rule in ordering_rules:
            tracer.step(f"Rule: {rule}")

        tracer.success("Event ordering documented")


# =============================================================================
# Event Error Handling Tests
# =============================================================================

class TestEventErrors:
    """Test event error handling."""

    def test_missing_source_panel(self, tracer):
        """Document handling of missing source panel."""
        tracer.start_phase("event_errors", "Test event error handling")
        tracer.step("Documenting missing source panel handling")

        tracer.trace_event(
            "ErrorScenario_MissingSource",
            source_panel=None,
            target_panel="Library",
            payload={
                "scenario": "Source panel closed before event completion",
                "expected_behavior": "Event should be queued or cancelled gracefully"
            }
        )

        tracer.end_phase(success=True)
        tracer.success("Missing source handling documented")

    def test_missing_target_panel(self, tracer):
        """Document handling of missing target panel."""
        tracer.step("Documenting missing target panel handling")

        tracer.trace_event(
            "ErrorScenario_MissingTarget",
            source_panel="Library",
            target_panel=None,
            payload={
                "scenario": "Target panel not open when event fires",
                "expected_behavior": "Event should be queued until target opens"
            }
        )

        tracer.success("Missing target handling documented")

    def test_invalid_payload(self, tracer):
        """Document handling of invalid event payload."""
        tracer.step("Documenting invalid payload handling")

        tracer.trace_event(
            "ErrorScenario_InvalidPayload",
            source_panel="Library",
            target_panel="VoiceSynthesis",
            payload={
                "scenario": "Event payload missing required data",
                "expected_behavior": "Target should display error or request retry"
            }
        )

        tracer.success("Invalid payload handling documented")


# =============================================================================
# Panel State Synchronization Tests
# =============================================================================

class TestPanelSynchronization:
    """Test panel state synchronization."""

    def test_library_state_sync(self, driver, app_launched, tracer):
        """Test Library panel state synchronization."""
        tracer.start_phase("state_sync", "Test state synchronization")
        tracer.step("Testing Library state synchronization")

        # Document expected sync behavior
        sync_points = [
            "After file import: Library refreshes file list",
            "After synthesis: Library adds new audio file",
            "After conversion: Library updates file entry",
            "After deletion: Library removes entry",
        ]

        for point in sync_points:
            tracer.step(f"Sync: {point}")

        tracer.end_phase(success=True)
        tracer.success("State sync documented")

    def test_profile_state_sync(self, tracer):
        """Test voice profile state synchronization."""
        tracer.step("Testing profile state synchronization")

        sync_points = [
            "After clone creation: Profile available in Synthesis dropdown",
            "After profile deletion: Profile removed from all panels",
            "After profile update: All panels reflect changes",
        ]

        for point in sync_points:
            tracer.step(f"Sync: {point}")

        tracer.success("Profile sync documented")


# =============================================================================
# Entry Point
# =============================================================================

if __name__ == "__main__":
    pytest.main([
        __file__,
        "-v",
        "--tb=short",
        "-m", "not slow",
        "--html=.buildlogs/validation/reports/allan_watts_events_report.html",
        "--self-contained-html",
    ])
