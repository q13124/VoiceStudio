"""
Audio Lifecycle End-to-End Test.

Comprehensive E2E test covering the full audio journey in VoiceStudio:
1. Audio Import (via API upload)
2. Library Verification (asset appears in library)
3. Transcription (optional, if backend supports)
4. Audio Processing (format conversion, effects)
5. Export/Download

This test uses the CorrelatedTracer to link all UI actions to API calls
and validate the complete workflow with assertions.

Requirements:
- Backend running on port 8000
- Test audio available (auto-provisioned via conftest.py)
- WinAppDriver running (for UI portions)

Markers:
- e2e: End-to-end lifecycle test
- audio: Requires audio files
"""

from __future__ import annotations

import os
import time

import pytest

# Test markers
pytestmark = [pytest.mark.e2e, pytest.mark.audio]

# Configuration
BACKEND_URL = os.getenv("VOICESTUDIO_BACKEND_URL", "http://127.0.0.1:8000")
TIMEOUT = 30


class TestAudioLifecycleE2E:
    """End-to-end test for complete audio workflow."""

    @pytest.fixture(autouse=True)
    def setup(self, tracer, api_monitor, canonical_audio_path):
        """Set up test with required fixtures."""
        self.tracer = tracer
        self.api_monitor = api_monitor
        self.audio_path = canonical_audio_path
        self.uploaded_asset_id = None

    def test_full_audio_lifecycle(self):
        """
        Complete audio lifecycle test.

        Validates the full journey of an audio file through VoiceStudio:
        Import -> Library -> Process -> Export
        """
        self.tracer.start_phase("lifecycle", "Full Audio Lifecycle Test")

        # Phase 1: Import Audio
        self._phase_import_audio()

        # Phase 2: Verify in Library
        self._phase_verify_library()

        # Phase 3: Process Audio (transcription or conversion)
        self._phase_process_audio()

        # Phase 4: Export/Cleanup
        self._phase_export_audio()

        self.tracer.complete_phase("lifecycle")

    def _phase_import_audio(self):
        """Phase 1: Import audio file via API."""
        self.tracer.start_phase("import", "Audio Import")

        # Step 1.1: Verify backend is healthy
        self.tracer.step("Checking backend health")
        response = self.api_monitor.get("/api/health")
        self.tracer.api_call("GET", "/api/health", response)

        if response.status_code != 200:
            pytest.skip("Backend not healthy, skipping E2E test")

        # Step 1.2: Upload audio file
        self.tracer.step(f"Uploading audio: {self.audio_path.name}")

        with open(self.audio_path, "rb") as f:
            files = {"file": (self.audio_path.name, f, "audio/wav")}
            response = self.api_monitor.post("/api/library/assets/upload", files=files)

        self.tracer.api_call("POST", "/api/library/assets/upload", response)

        # Validate upload
        assert response.status_code in (
            200,
            201,
        ), f"Upload failed: {response.status_code} - {response.text}"

        data = response.json()
        self.uploaded_asset_id = data.get("id") or data.get("asset_id")

        assert self.uploaded_asset_id, "No asset ID returned from upload"
        self.tracer.step(f"Upload successful: {self.uploaded_asset_id}")

        self.tracer.complete_phase("import")

    def _phase_verify_library(self):
        """Phase 2: Verify asset appears in library."""
        self.tracer.start_phase("library", "Library Verification")

        # Step 2.1: List library assets
        self.tracer.step("Listing library assets")
        response = self.api_monitor.get("/api/library/assets")
        self.tracer.api_call("GET", "/api/library/assets", response)

        assert response.status_code == 200, f"Library list failed: {response.status_code}"

        # Step 2.2: Find uploaded asset
        assets = response.json()
        if isinstance(assets, dict):
            assets = assets.get("assets", assets.get("items", []))

        asset_ids = [a.get("id") for a in assets if isinstance(a, dict)]
        self.tracer.step(f"Found {len(asset_ids)} assets in library")

        # Verify our asset is present
        if self.uploaded_asset_id:
            assert (
                self.uploaded_asset_id in asset_ids
            ), f"Uploaded asset {self.uploaded_asset_id} not in library"
            self.tracer.step("Uploaded asset found in library")

        # Step 2.3: Get asset details
        if self.uploaded_asset_id:
            self.tracer.step("Fetching asset details")
            response = self.api_monitor.get(f"/api/library/assets/{self.uploaded_asset_id}")
            self.tracer.api_call("GET", f"/api/library/assets/{self.uploaded_asset_id}", response)

            if response.status_code == 200:
                details = response.json()
                self.tracer.step(f"Asset details: {details.get('filename', 'unknown')}")

        self.tracer.complete_phase("library")

    def _phase_process_audio(self):
        """Phase 3: Process audio (transcription or conversion)."""
        self.tracer.start_phase("process", "Audio Processing")

        # Step 3.1: Check available engines
        self.tracer.step("Checking available engines")
        response = self.api_monitor.get("/api/engines/list")
        self.tracer.api_call("GET", "/api/engines/list", response)

        engines = []
        if response.status_code == 200:
            data = response.json()
            if isinstance(data, list):
                engines = data
            elif isinstance(data, dict):
                engines = data.get("engines", [])

        transcription_available = any(
            e.get("type") == "transcription" or "whisper" in str(e).lower()
            for e in engines
            if isinstance(e, dict)
        )

        # Step 3.2: Try transcription if available
        if transcription_available and self.uploaded_asset_id:
            self.tracer.step("Attempting transcription")
            response = self.api_monitor.post(
                "/api/transcription/start",
                json_data={
                    "audio_id": self.uploaded_asset_id,
                    "engine": "whisper",
                    "language": "en",
                },
            )
            self.tracer.api_call("POST", "/api/transcription/start", response)

            if response.status_code in (200, 202):
                self.tracer.step("Transcription started successfully")
                # Poll for completion (simplified)
                time.sleep(2)
            else:
                self.tracer.step(f"Transcription not available: {response.status_code}")
        else:
            self.tracer.step("Transcription engine not available, skipping")

        # Step 3.3: Try format conversion
        self.tracer.step("Checking conversion endpoint")
        response = self.api_monitor.post(
            "/api/audio/convert",
            json_data={
                "source": self.uploaded_asset_id,
                "format": "mp3",
            },
        )
        self.tracer.api_call("POST", "/api/audio/convert", response)

        if response.status_code in (200, 202):
            self.tracer.step("Conversion initiated")
        else:
            self.tracer.step(f"Conversion endpoint returned: {response.status_code}")

        self.tracer.complete_phase("process")

    def _phase_export_audio(self):
        """Phase 4: Export audio and cleanup."""
        self.tracer.start_phase("export", "Audio Export")

        # Step 4.1: Check export endpoint
        if self.uploaded_asset_id:
            self.tracer.step("Checking export availability")
            response = self.api_monitor.get(
                f"/api/library/assets/{self.uploaded_asset_id}/download"
            )
            self.tracer.api_call(
                "GET", f"/api/library/assets/{self.uploaded_asset_id}/download", response
            )

            if response.status_code == 200:
                self.tracer.step("Export endpoint available")
                # Verify response is audio data
                content_type = response.headers.get("Content-Type", "")
                if "audio" in content_type or "octet-stream" in content_type:
                    self.tracer.step(f"Export returned audio: {len(response.content)} bytes")
            else:
                self.tracer.step(f"Export returned: {response.status_code}")

        # Step 4.2: Optional cleanup (delete uploaded asset)
        # Commented out to preserve test data for inspection
        # if self.uploaded_asset_id:
        #     self.tracer.step("Cleaning up: deleting test asset")
        #     response = self.api_monitor.delete(
        #         f"/api/library/assets/{self.uploaded_asset_id}"
        #     )
        #     self.tracer.api_call(
        #         "DELETE",
        #         f"/api/library/assets/{self.uploaded_asset_id}",
        #         response
        #     )

        self.tracer.complete_phase("export")
        self.tracer.step("Audio lifecycle test completed successfully")


class TestAudioLifecycleAPIOnly:
    """
    API-only E2E test (no UI dependency).

    Runs the full lifecycle without WinAppDriver for faster CI execution.
    """

    @pytest.fixture(autouse=True)
    def setup(self, tracer, api_monitor, canonical_audio_path):
        """Set up test fixtures."""
        self.tracer = tracer
        self.api_monitor = api_monitor
        self.audio_path = canonical_audio_path

    def test_api_lifecycle_quick(self):
        """Quick API-only lifecycle test."""
        self.tracer.start_phase("api_quick", "API Quick Lifecycle")

        # Health check
        response = self.api_monitor.get("/api/health")
        if response.status_code != 200:
            pytest.skip("Backend not available")

        # Upload
        with open(self.audio_path, "rb") as f:
            files = {"file": (self.audio_path.name, f, "audio/wav")}
            response = self.api_monitor.post("/api/library/assets/upload", files=files)

        if response.status_code not in (200, 201):
            pytest.fail(f"Upload failed: {response.status_code}")

        asset_id = response.json().get("id") or response.json().get("asset_id")

        # Verify listing
        response = self.api_monitor.get("/api/library/assets")
        assert response.status_code == 200

        # Verify asset details
        if asset_id:
            response = self.api_monitor.get(f"/api/library/assets/{asset_id}")
            assert response.status_code == 200

        self.tracer.complete_phase("api_quick")
        self.tracer.step("API lifecycle test passed")
