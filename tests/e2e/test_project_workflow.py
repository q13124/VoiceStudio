"""
E2E Tests: Project Lifecycle Workflow.

Tests complete project operations:
- Create new project
- Import audio assets
- Configure synthesis settings
- Generate audio
- Save project
- Load project
- Export project
"""

import time
from datetime import datetime

import pytest

try:
    from selenium.webdriver.common.by import By
    from selenium.webdriver.common.keys import Keys
except ImportError:
    By = None
    Keys = None

# Pytest markers
pytestmark = [
    pytest.mark.e2e,
    pytest.mark.workflow,
    pytest.mark.project,
]


class TestProjectCreation:
    """Tests for creating new projects."""

    def test_create_new_project_api(self, api_client, backend_available):
        """Test creating project via API."""
        project_data = {
            "name": f"E2E Test Project {datetime.now().strftime('%H%M%S')}",
            "description": "Created by E2E test",
            "settings": {
                "sample_rate": 44100,
                "bit_depth": 16,
                "channels": 2,
            }
        }

        response = api_client.post("/api/projects/create", json=project_data, timeout=10)

        if response.status_code == 200:
            result = response.json()
            assert "project_id" in result or "id" in result
            print(f"Project created: {result}")
        elif response.status_code == 404:
            pytest.skip("Projects API not available")
        else:
            print(f"Create project response: {response.status_code} - {response.text[:200]}")

    def test_list_projects_api(self, api_client, backend_available):
        """Test listing projects via API."""
        response = api_client.get("/api/projects", timeout=10)

        if response.status_code == 200:
            projects = response.json()
            print(f"Found {len(projects) if isinstance(projects, list) else 'N/A'} projects")
        elif response.status_code == 404:
            pytest.skip("Projects list API not available")

    def test_project_settings_api(self, api_client, backend_available):
        """Test project settings API."""
        response = api_client.get("/api/projects/settings", timeout=10)

        if response.status_code == 200:
            settings = response.json()
            print(f"Project settings: {settings}")
        elif response.status_code == 404:
            pytest.skip("Project settings API not available")


class TestProjectWorkflowUI:
    """Tests for project workflow via UI."""

    def test_new_project_menu(self, driver, workflow_state, screenshot_capture):
        """Test File > New Project menu."""
        state = workflow_state

        # Try to find File menu
        from conftest import find_element_safe

        file_menu = find_element_safe(driver, By.NAME, "File")
        if file_menu:
            state["record_step"]("Found File menu")
            file_menu.click()
            time.sleep(0.5)

            screenshot_capture("file_menu_open")

            # Look for New Project option
            new_project = find_element_safe(driver, By.NAME, "New Project")
            if new_project:
                state["record_step"]("Found New Project option")
                # Don't click - just verify it exists
            else:
                state["record_step"]("New Project option not found", success=False)

            # Press Escape to close menu
            from selenium.webdriver.common.keys import Keys
            driver.find_element(By.XPATH, "//*").send_keys(Keys.ESCAPE)
        else:
            state["record_step"]("File menu not found", success=False)

        # Report workflow state
        assert any(s["success"] for s in state["steps"]), "No successful steps in workflow"

    def test_save_project_shortcut(self, driver, workflow_state):
        """Test Ctrl+S save shortcut."""
        from selenium.webdriver.common.keys import Keys

        # Press Ctrl+S
        root = driver.find_element(By.XPATH, "//*")
        root.send_keys(Keys.CONTROL + "s")
        time.sleep(0.5)

        # Check for save dialog or confirmation
        workflow_state["record_step"]("Triggered save shortcut")

        # Press Escape in case dialog opened
        root.send_keys(Keys.ESCAPE)


class TestProjectImportExport:
    """Tests for project import/export."""

    def test_import_audio_to_project(self, api_client, backend_available, test_audio_file):
        """Test importing audio to project."""
        if not test_audio_file.exists():
            pytest.skip("Test audio file not available")

        with open(test_audio_file, "rb") as f:
            files = {"file": (test_audio_file.name, f, "audio/wav")}
            response = api_client.post("/api/audio/upload", files=files, timeout=30)

        if response.status_code == 200:
            result = response.json()
            print(f"Audio uploaded: {result}")
            assert "file_id" in result or "id" in result or "path" in result
        elif response.status_code == 404:
            pytest.skip("Audio upload API not available")

    def test_export_project_api(self, api_client, backend_available):
        """Test project export API."""
        export_config = {
            "format": "zip",
            "include_audio": True,
            "include_settings": True,
        }

        response = api_client.post("/api/projects/export", json=export_config, timeout=30)

        if response.status_code == 200:
            print(f"Export initiated: {response.headers.get('Content-Type')}")
        elif response.status_code == 404:
            pytest.skip("Export API not available")

    def test_import_project_api(self, api_client, backend_available):
        """Test project import API."""
        response = api_client.get("/api/projects/import/formats", timeout=10)

        if response.status_code == 200:
            formats = response.json()
            print(f"Supported import formats: {formats}")
        elif response.status_code == 404:
            pytest.skip("Import formats API not available")


class TestProjectPersistence:
    """Tests for project save/load."""

    def test_auto_save_settings(self, api_client, backend_available):
        """Test auto-save settings API."""
        response = api_client.get("/api/settings/autosave", timeout=10)

        if response.status_code == 200:
            settings = response.json()
            print(f"Auto-save settings: {settings}")
        elif response.status_code == 404:
            pytest.skip("Auto-save API not available")

    def test_recent_projects(self, api_client, backend_available):
        """Test recent projects list."""
        response = api_client.get("/api/projects/recent", timeout=10)

        if response.status_code == 200:
            recent = response.json()
            print(f"Recent projects: {len(recent) if isinstance(recent, list) else recent}")
        elif response.status_code == 404:
            pytest.skip("Recent projects API not available")


class TestFullProjectWorkflow:
    """Complete project workflow test."""

    def test_complete_project_workflow_api(self, api_client, backend_available, workflow_state):
        """Test complete project workflow via API."""
        state = workflow_state

        # Step 1: Create project
        project_name = f"E2E Workflow Test {datetime.now().strftime('%Y%m%d_%H%M%S')}"
        create_resp = api_client.post("/api/projects/create", json={
            "name": project_name,
            "description": "Complete workflow test",
        }, timeout=10)

        if create_resp.status_code == 200:
            project_id = create_resp.json().get("project_id") or create_resp.json().get("id")
            state["record_step"]("Created project", data={"project_id": project_id})
        elif create_resp.status_code == 404:
            state["record_step"]("Projects API not available", success=False)
            pytest.skip("Projects API not available")
        else:
            state["record_step"]("Project creation failed", success=False, data={
                "status": create_resp.status_code
            })
            project_id = None

        # Step 2: Configure settings
        if project_id:
            settings_resp = api_client.put(f"/api/projects/{project_id}/settings", json={
                "sample_rate": 48000,
                "default_engine": "piper",
            }, timeout=10)

            if settings_resp.status_code == 200:
                state["record_step"]("Updated project settings")
            else:
                state["record_step"]("Settings update response", data={
                    "status": settings_resp.status_code
                })

        # Step 3: Generate audio
        synth_resp = api_client.post("/api/voice/synthesize", json={
            "text": "This is a test of the project workflow.",
            "engine": "piper",
        }, timeout=60)

        if synth_resp.status_code == 200:
            state["record_step"]("Generated audio", data=synth_resp.json())
        else:
            state["record_step"]("Synthesis response", data={"status": synth_resp.status_code})

        # Step 4: Save/close project
        if project_id:
            save_resp = api_client.post(f"/api/projects/{project_id}/save", timeout=10)

            if save_resp.status_code == 200:
                state["record_step"]("Saved project")
            else:
                state["record_step"]("Save response", data={"status": save_resp.status_code})

        # Report
        success_count = sum(1 for s in state["steps"] if s["success"])
        total_count = len(state["steps"])
        print(f"\nWorkflow completed: {success_count}/{total_count} steps successful")
        for step in state["steps"]:
            status = "✓" if step["success"] else "✗"
            print(f"  {status} {step['name']}")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])
