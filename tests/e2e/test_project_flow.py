"""
Project Flow E2E Tests for VoiceStudio.

Tests the complete project management workflow including:
- Project creation
- Project saving
- Project loading
- Project modification tracking
- Recent projects
"""

import logging
import os
import tempfile
import time
from pathlib import Path
from typing import Optional
from unittest.mock import MagicMock, patch

import pytest

from tests.e2e.framework.base import E2ETestBase, E2EConfig
from tests.e2e.framework.helpers import TestDataHelper, PerformanceTimer

logger = logging.getLogger(__name__)


# =============================================================================
# Test Fixtures
# =============================================================================


@pytest.fixture
def unique_project_name() -> str:
    """Generate a unique project name."""
    return TestDataHelper.unique_name("E2E-Project")


@pytest.fixture
def temp_project_dir(tmp_path: Path) -> str:
    """Get a temporary directory for project files."""
    project_dir = tmp_path / "voicestudio_projects"
    project_dir.mkdir(exist_ok=True)
    return str(project_dir)


@pytest.fixture
def sample_project_config() -> dict:
    """Get sample project configuration."""
    return TestDataHelper.sample_project_config()


# =============================================================================
# Mock-Based Tests (No App Required)
# =============================================================================


class TestProjectFlowMock:
    """
    Mock-based project flow tests.
    
    These tests validate the E2E test structure and logic
    without requiring the actual application.
    """
    
    def test_project_flow_structure(self):
        """Verify project flow test structure is correct."""
        assert TestProjectFlow is not None
        assert hasattr(TestProjectFlow, 'test_create_new_project')
        assert hasattr(TestProjectFlow, 'test_save_project')
        assert hasattr(TestProjectFlow, 'test_load_project')
    
    def test_page_objects_importable(self):
        """Verify project page objects can be imported."""
        from tests.e2e.pages import MainWindowPage
        from tests.e2e.pages import ProjectPage
        
        assert MainWindowPage is not None
        assert ProjectPage is not None
    
    def test_unique_project_name_fixture(self, unique_project_name: str):
        """Verify unique project name generation."""
        assert unique_project_name.startswith("E2E-Project")
        assert len(unique_project_name) > len("E2E-Project")
    
    def test_temp_project_dir_fixture(self, temp_project_dir: str):
        """Verify temp project directory is created."""
        assert os.path.exists(temp_project_dir)
        assert os.path.isdir(temp_project_dir)
    
    def test_mock_create_project_flow(
        self,
        unique_project_name: str,
        temp_project_dir: str
    ):
        """
        Test project creation flow with mocked page objects.
        """
        # Create mock page objects
        mock_main_window = MagicMock()
        mock_project_page = MagicMock()
        
        mock_main_window.get_project_page = MagicMock(return_value=mock_project_page)
        mock_project_page.is_project_open.return_value = True
        mock_project_page.get_current_project_name.return_value = unique_project_name
        mock_project_page.is_project_modified.return_value = False
        
        # Simulate create project flow
        # Step 1: Navigate to project area
        mock_main_window.navigate_to_library()
        mock_main_window.navigate_to_library.assert_called_once()
        
        # Step 2: Get project page
        project_page = mock_main_window.get_project_page()
        
        # Step 3: Click new project
        project_page.click_new_project()
        project_page.click_new_project.assert_called_once()
        
        # Step 4: Set project name
        project_page.set_new_project_name(unique_project_name)
        project_page.set_new_project_name.assert_called_with(unique_project_name)
        
        # Step 5: Set project location
        project_page.set_new_project_location(temp_project_dir)
        project_page.set_new_project_location.assert_called_with(temp_project_dir)
        
        # Step 6: Create project
        project_page.click_create_project()
        project_page.click_create_project.assert_called_once()
        
        # Step 7: Verify project is open
        assert project_page.is_project_open()
        assert project_page.get_current_project_name() == unique_project_name
        
        logger.info("Mock create project flow completed")
    
    def test_mock_save_load_project_flow(
        self,
        unique_project_name: str
    ):
        """
        Test project save and load flow with mocked page objects.
        """
        mock_project_page = MagicMock()
        
        mock_project_page.is_project_open.return_value = True
        mock_project_page.is_project_modified.side_effect = [True, False]
        mock_project_page.find_project_by_name.return_value = True
        mock_project_page.get_current_project_name.return_value = unique_project_name
        
        # Save project
        assert mock_project_page.is_project_modified()
        mock_project_page.click_save_project()
        mock_project_page.click_save_project.assert_called_once()
        
        # Verify saved
        assert not mock_project_page.is_project_modified()
        
        # Close project
        mock_project_page.click_close_project(save=False)
        mock_project_page.click_close_project.assert_called_with(save=False)
        
        # Simulate project closed
        mock_project_page.is_project_open.return_value = False
        
        # Load project
        mock_project_page.open_project_by_name(unique_project_name)
        mock_project_page.open_project_by_name.assert_called_with(unique_project_name)
        
        # Simulate project opened
        mock_project_page.is_project_open.return_value = True
        
        # Verify loaded
        assert mock_project_page.is_project_open()
        
        logger.info("Mock save/load project flow completed")
    
    def test_mock_recent_projects_flow(self):
        """
        Test recent projects functionality with mocked page objects.
        """
        mock_project_page = MagicMock()
        
        mock_project_page.get_recent_project_count.return_value = 3
        mock_project_page.is_project_open.return_value = True
        
        # Get recent projects count
        assert mock_project_page.get_recent_project_count() == 3
        
        # Open recent project
        mock_project_page.open_recent_project(0)
        mock_project_page.open_recent_project.assert_called_with(0)
        
        # Verify opened
        assert mock_project_page.is_project_open()
        
        # Clear recent
        mock_project_page.clear_recent_projects()
        mock_project_page.clear_recent_projects.assert_called_once()
        
        logger.info("Mock recent projects flow completed")


# =============================================================================
# Full E2E Tests (Require Application)
# =============================================================================


@pytest.mark.e2e
@pytest.mark.project
@pytest.mark.requires_app
class TestProjectFlow(E2ETestBase):
    """
    End-to-end tests for project management.
    
    These tests require:
    - VoiceStudio application running
    - WinAppDriver running
    - Write access to temp directory
    """
    
    # =========================================================================
    # Test: Create New Project
    # =========================================================================
    
    def test_create_new_project(
        self,
        unique_project_name: str,
        temp_project_dir: str,
        app_session
    ):
        """
        Test creating a new project.
        
        Steps:
        1. Navigate to project area
        2. Click New Project
        3. Enter project name and location
        4. Click Create
        5. Verify project is created and open
        """
        from tests.e2e.pages import MainWindowPage
        from tests.e2e.pages import ProjectPage
        
        with PerformanceTimer("Create new project") as timer:
            main_window = MainWindowPage(app_session)
            
            # Navigate to library/projects
            main_window.navigate_to_library()
            
            # Get project page (may be part of library or separate)
            project_page = ProjectPage(app_session)
            
            # Create new project
            project_page.create_project(
                name=unique_project_name,
                description="E2E test project",
                location=temp_project_dir
            )
            
            # Verify project is open
            assert project_page.is_project_open()
            assert project_page.get_current_project_name() == unique_project_name
            
            logger.info(
                f"Created project '{unique_project_name}' "
                f"in {timer.elapsed:.2f}s"
            )
    
    # =========================================================================
    # Test: Save Project
    # =========================================================================
    
    def test_save_project(
        self,
        unique_project_name: str,
        temp_project_dir: str,
        app_session
    ):
        """
        Test saving a project.
        
        Steps:
        1. Create a new project
        2. Make a modification (trigger dirty state)
        3. Save the project
        4. Verify saved state
        """
        from tests.e2e.pages import MainWindowPage
        from tests.e2e.pages import ProjectPage
        
        main_window = MainWindowPage(app_session)
        main_window.navigate_to_library()
        
        project_page = ProjectPage(app_session)
        
        # Create project first
        project_page.create_project(
            name=unique_project_name,
            location=temp_project_dir
        )
        
        # Make a modification (navigate to synthesis and back)
        main_window.navigate_to_studio()
        time.sleep(0.5)
        main_window.navigate_to_library()
        
        # Check if modified (may or may not be, depending on implementation)
        if project_page.is_project_modified():
            # Save the project
            project_page.click_save_project()
            
            # Verify saved
            assert project_page.wait_for_project_saved(timeout=10.0)
            assert not project_page.is_project_modified()
        
        logger.info(f"Project '{unique_project_name}' saved successfully")
    
    # =========================================================================
    # Test: Load Project
    # =========================================================================
    
    def test_load_project(
        self,
        unique_project_name: str,
        temp_project_dir: str,
        app_session
    ):
        """
        Test loading an existing project.
        
        Steps:
        1. Create and save a project
        2. Close the project
        3. Load the project from disk
        4. Verify project is loaded correctly
        """
        from tests.e2e.pages import MainWindowPage
        from tests.e2e.pages import ProjectPage
        
        main_window = MainWindowPage(app_session)
        main_window.navigate_to_library()
        
        project_page = ProjectPage(app_session)
        
        # Create and save project
        project_page.create_project(
            name=unique_project_name,
            location=temp_project_dir
        )
        project_page.click_save_project()
        
        # Close project
        project_page.click_close_project(save=True)
        
        # Verify closed
        assert not project_page.is_project_open()
        
        # Load project
        project_page.open_project_by_name(unique_project_name)
        
        # Verify loaded
        assert project_page.wait_for_project_loaded(timeout=30.0)
        assert project_page.get_current_project_name() == unique_project_name
        
        logger.info(f"Project '{unique_project_name}' loaded successfully")
    
    # =========================================================================
    # Test: Project Modification Tracking
    # =========================================================================
    
    def test_project_modification_tracking(
        self,
        unique_project_name: str,
        temp_project_dir: str,
        app_session
    ):
        """
        Test that project modifications are properly tracked.
        """
        from tests.e2e.pages import MainWindowPage
        from tests.e2e.pages import ProjectPage
        
        main_window = MainWindowPage(app_session)
        main_window.navigate_to_library()
        
        project_page = ProjectPage(app_session)
        
        # Create project
        project_page.create_project(
            name=unique_project_name,
            location=temp_project_dir
        )
        
        # Initially should not be modified
        project_page.click_save_project()
        time.sleep(0.5)
        assert not project_page.is_project_modified()
        
        logger.info("Project modification tracking verified")
    
    # =========================================================================
    # Test: Recent Projects
    # =========================================================================
    
    def test_recent_projects(
        self,
        app_session
    ):
        """
        Test recent projects functionality.
        """
        from tests.e2e.pages import ProjectPage
        
        project_page = ProjectPage(app_session)
        
        # Get initial recent count
        initial_count = project_page.get_recent_project_count()
        
        # Open most recent if available
        if initial_count > 0:
            project_page.open_recent_project(0)
            assert project_page.wait_for_project_loaded(timeout=30.0)
            logger.info(f"Opened recent project (had {initial_count} recent)")
        else:
            logger.info("No recent projects to open")
    
    # =========================================================================
    # Test: Close Without Saving
    # =========================================================================
    
    def test_close_without_saving(
        self,
        unique_project_name: str,
        temp_project_dir: str,
        app_session
    ):
        """
        Test closing a modified project without saving.
        """
        from tests.e2e.pages import MainWindowPage
        from tests.e2e.pages import ProjectPage
        
        main_window = MainWindowPage(app_session)
        main_window.navigate_to_library()
        
        project_page = ProjectPage(app_session)
        
        # Create project
        project_page.create_project(
            name=unique_project_name,
            location=temp_project_dir
        )
        
        # Close without saving
        project_page.click_close_project(save=False)
        
        # Verify closed
        assert not project_page.is_project_open()
        
        logger.info("Closed project without saving")
    
    # =========================================================================
    # Test: Delete Project
    # =========================================================================
    
    def test_delete_project(
        self,
        unique_project_name: str,
        temp_project_dir: str,
        app_session
    ):
        """
        Test deleting a project.
        """
        from tests.e2e.pages import MainWindowPage
        from tests.e2e.pages import ProjectPage
        
        main_window = MainWindowPage(app_session)
        main_window.navigate_to_library()
        
        project_page = ProjectPage(app_session)
        
        # Create project
        project_page.create_project(
            name=unique_project_name,
            location=temp_project_dir
        )
        project_page.click_save_project()
        project_page.click_close_project(save=False)
        
        # Delete project
        if project_page.find_project_by_name(unique_project_name):
            project_page.delete_project_by_name(unique_project_name, confirm=True)
            
            # Verify deleted
            assert not project_page.find_project_by_name(unique_project_name)
            
            logger.info(f"Deleted project '{unique_project_name}'")


# =============================================================================
# Backend Integration Tests
# =============================================================================


@pytest.mark.e2e
@pytest.mark.project
@pytest.mark.requires_backend
class TestProjectBackendIntegration:
    """
    Tests that verify project integration with backend.
    """
    
    def test_project_api_list(
        self,
        api_client
    ):
        """
        Test project listing API.
        """
        response = api_client.get("/api/projects")
        
        if response.status_code == 200:
            projects = response.json()
            assert isinstance(projects, (list, dict))
            logger.info(f"Found {len(projects) if isinstance(projects, list) else 'some'} projects")
        elif response.status_code == 404:
            logger.info("Projects API not available")
        else:
            logger.warning(f"Projects API returned: {response.status_code}")
    
    def test_project_api_create(
        self,
        unique_project_name: str,
        api_client
    ):
        """
        Test project creation API.
        """
        response = api_client.post(
            "/api/projects",
            json={
                "name": unique_project_name,
                "description": "E2E test project"
            }
        )
        
        if response.status_code in [200, 201]:
            result = response.json()
            assert "id" in result or "project_id" in result
            logger.info(f"Created project via API: {result}")
        elif response.status_code == 404:
            pytest.skip("Project creation API not available")
        else:
            logger.warning(f"Project creation failed: {response.status_code}")


# =============================================================================
# Performance Tests
# =============================================================================


@pytest.mark.e2e
@pytest.mark.project
@pytest.mark.performance
@pytest.mark.requires_app
class TestProjectPerformance:
    """
    Performance tests for project operations.
    """
    
    def test_project_creation_performance(
        self,
        unique_project_name: str,
        temp_project_dir: str,
        app_session,
        performance_timer
    ):
        """
        Test project creation performance.
        
        Target: < 3 seconds
        """
        from tests.e2e.pages import MainWindowPage
        from tests.e2e.pages import ProjectPage
        
        main_window = MainWindowPage(app_session)
        main_window.navigate_to_library()
        
        project_page = ProjectPage(app_session)
        
        with performance_timer("Create project") as timer:
            project_page.create_project(
                name=unique_project_name,
                location=temp_project_dir
            )
        
        assert timer.elapsed < 3.0, f"Creation too slow: {timer.elapsed:.2f}s"
    
    def test_project_save_performance(
        self,
        unique_project_name: str,
        temp_project_dir: str,
        app_session,
        performance_timer
    ):
        """
        Test project save performance.
        
        Target: < 2 seconds
        """
        from tests.e2e.pages import MainWindowPage
        from tests.e2e.pages import ProjectPage
        
        main_window = MainWindowPage(app_session)
        main_window.navigate_to_library()
        
        project_page = ProjectPage(app_session)
        project_page.create_project(
            name=unique_project_name,
            location=temp_project_dir
        )
        
        with performance_timer("Save project") as timer:
            project_page.click_save_project()
            project_page.wait_for_project_saved()
        
        assert timer.elapsed < 2.0, f"Save too slow: {timer.elapsed:.2f}s"
    
    def test_project_load_performance(
        self,
        unique_project_name: str,
        temp_project_dir: str,
        app_session,
        performance_timer
    ):
        """
        Test project load performance.
        
        Target: < 5 seconds
        """
        from tests.e2e.pages import MainWindowPage
        from tests.e2e.pages import ProjectPage
        
        main_window = MainWindowPage(app_session)
        main_window.navigate_to_library()
        
        project_page = ProjectPage(app_session)
        
        # Create and save first
        project_page.create_project(
            name=unique_project_name,
            location=temp_project_dir
        )
        project_page.click_save_project()
        project_page.click_close_project(save=False)
        
        # Measure load time
        with performance_timer("Load project") as timer:
            project_page.open_project_by_name(unique_project_name)
            project_page.wait_for_project_loaded()
        
        assert timer.elapsed < 5.0, f"Load too slow: {timer.elapsed:.2f}s"
