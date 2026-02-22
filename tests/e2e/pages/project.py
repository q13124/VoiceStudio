"""
Project Page Object for VoiceStudio.

Provides access to project management functionality.
"""

from __future__ import annotations

import logging
import time

from tests.e2e.framework.page_objects import BasePage, ElementLocator

logger = logging.getLogger(__name__)


class ProjectPage(BasePage):
    """
    Page object for project management in VoiceStudio.

    Provides functionality for creating, saving, loading,
    and managing voice studio projects.
    """

    # ==========================================================================
    # Locators - Project List
    # ==========================================================================

    PROJECT_LIST = ElementLocator.by_automation_id("ProjectList", "Project list")
    PROJECT_LIST_ITEM = ElementLocator.by_automation_id("ProjectListItem", "Project list item")
    PROJECT_NAME = ElementLocator.by_automation_id("ProjectName", "Project name text")
    EMPTY_STATE = ElementLocator.by_automation_id("EmptyState", "No projects message")

    # ==========================================================================
    # Locators - Project Actions
    # ==========================================================================

    NEW_PROJECT_BUTTON = ElementLocator.by_automation_id("NewProjectButton", "New project button")
    OPEN_PROJECT_BUTTON = ElementLocator.by_automation_id(
        "OpenProjectButton", "Open project button"
    )
    SAVE_PROJECT_BUTTON = ElementLocator.by_automation_id(
        "SaveProjectButton", "Save project button"
    )
    SAVE_AS_BUTTON = ElementLocator.by_automation_id("SaveAsButton", "Save as button")
    DELETE_PROJECT_BUTTON = ElementLocator.by_automation_id(
        "DeleteProjectButton", "Delete project button"
    )
    CLOSE_PROJECT_BUTTON = ElementLocator.by_automation_id(
        "CloseProjectButton", "Close project button"
    )

    # ==========================================================================
    # Locators - New Project Dialog
    # ==========================================================================

    NEW_PROJECT_DIALOG = ElementLocator.by_automation_id("NewProjectDialog", "New project dialog")
    PROJECT_NAME_INPUT = ElementLocator.by_automation_id("ProjectNameInput", "Project name input")
    PROJECT_DESCRIPTION_INPUT = ElementLocator.by_automation_id(
        "ProjectDescriptionInput", "Project description input"
    )
    PROJECT_LOCATION_INPUT = ElementLocator.by_automation_id(
        "ProjectLocationInput", "Project location input"
    )
    BROWSE_LOCATION_BUTTON = ElementLocator.by_automation_id(
        "BrowseLocationButton", "Browse location button"
    )
    CREATE_BUTTON = ElementLocator.by_automation_id("CreateButton", "Create project button")
    CANCEL_BUTTON = ElementLocator.by_automation_id("CancelButton", "Cancel button")

    # ==========================================================================
    # Locators - Save Dialog
    # ==========================================================================

    SAVE_DIALOG = ElementLocator.by_automation_id("SaveDialog", "Save project dialog")
    SAVE_CONFIRM_BUTTON = ElementLocator.by_automation_id(
        "SaveConfirmButton", "Confirm save button"
    )
    DONT_SAVE_BUTTON = ElementLocator.by_automation_id("DontSaveButton", "Don't save button")

    # ==========================================================================
    # Locators - Current Project Info
    # ==========================================================================

    CURRENT_PROJECT_NAME = ElementLocator.by_automation_id(
        "CurrentProjectName", "Current project name display"
    )
    CURRENT_PROJECT_PATH = ElementLocator.by_automation_id(
        "CurrentProjectPath", "Current project path display"
    )
    PROJECT_MODIFIED_INDICATOR = ElementLocator.by_automation_id(
        "ProjectModifiedIndicator", "Unsaved changes indicator"
    )

    # ==========================================================================
    # Locators - Recent Projects
    # ==========================================================================

    RECENT_PROJECTS_LIST = ElementLocator.by_automation_id(
        "RecentProjectsList", "Recent projects list"
    )
    RECENT_PROJECT_ITEM = ElementLocator.by_automation_id(
        "RecentProjectItem", "Recent project item"
    )
    CLEAR_RECENT_BUTTON = ElementLocator.by_automation_id(
        "ClearRecentButton", "Clear recent projects button"
    )

    # ==========================================================================
    # Locators - Status
    # ==========================================================================

    LOADING_INDICATOR = ElementLocator.by_automation_id("LoadingIndicator", "Loading indicator")
    SUCCESS_MESSAGE = ElementLocator.by_automation_id("SuccessMessage", "Success message")
    ERROR_MESSAGE = ElementLocator.by_automation_id("ErrorMessage", "Error message")

    # ==========================================================================
    # Project List Operations
    # ==========================================================================

    def get_project_count(self) -> int:
        """Get number of projects in the list."""
        try:
            items = self.find_elements(self.PROJECT_LIST_ITEM)
            return len(items)
        except Exception:
            return 0

    def is_empty(self) -> bool:
        """Check if project list is empty."""
        return self.is_displayed(self.EMPTY_STATE) or self.get_project_count() == 0

    def get_project_names(self) -> list[str]:
        """Get all project names in the list."""
        names = []
        items = self.find_elements(self.PROJECT_LIST_ITEM)
        for item in items:
            try:
                name_element = item.find_element("accessibility id", "ProjectName")
                names.append(name_element.text)
            except Exception:
                continue
        return names

    def find_project_by_name(self, name: str) -> bool:
        """Check if a project with the given name exists."""
        names = self.get_project_names()
        return any(name.lower() in n.lower() for n in names)

    def select_project_by_name(self, name: str):
        """Select a project by name."""
        items = self.find_elements(self.PROJECT_LIST_ITEM)
        for item in items:
            try:
                name_element = item.find_element("accessibility id", "ProjectName")
                if name.lower() in name_element.text.lower():
                    item.click()
                    logger.info(f"Selected project: {name}")
                    return
            except Exception:
                continue
        raise ValueError(f"Project not found: {name}")

    def select_project_by_index(self, index: int):
        """Select a project by index."""
        items = self.find_elements(self.PROJECT_LIST_ITEM)
        if index >= len(items):
            raise IndexError(f"Project index {index} out of range")

        items[index].click()
        logger.info(f"Selected project at index: {index}")

    # ==========================================================================
    # Create New Project
    # ==========================================================================

    def click_new_project(self):
        """Click the New Project button."""
        self.click(self.NEW_PROJECT_BUTTON)
        self.wait_for_element(self.NEW_PROJECT_DIALOG, timeout=5.0)
        logger.info("Opened new project dialog")

    def is_new_project_dialog_visible(self) -> bool:
        """Check if new project dialog is visible."""
        return self.is_displayed(self.NEW_PROJECT_DIALOG)

    def set_new_project_name(self, name: str):
        """Set the name for the new project."""
        self.type_text(self.PROJECT_NAME_INPUT, name)
        logger.info(f"Set project name: {name}")

    def set_new_project_description(self, description: str):
        """Set the description for the new project."""
        self.type_text(self.PROJECT_DESCRIPTION_INPUT, description)
        logger.info("Set project description")

    def set_new_project_location(self, path: str):
        """Set the location for the new project."""
        self.type_text(self.PROJECT_LOCATION_INPUT, path)
        logger.info(f"Set project location: {path}")

    def click_create_project(self):
        """Click the Create button in the new project dialog."""
        self.click(self.CREATE_BUTTON)
        self.wait_for_loading()
        logger.info("Created new project")

    def cancel_new_project(self):
        """Cancel the new project dialog."""
        self.click(self.CANCEL_BUTTON)
        logger.info("Cancelled new project dialog")

    def create_project(
        self, name: str, description: str | None = None, location: str | None = None
    ):
        """
        Create a new project with the given settings.

        Args:
            name: Project name
            description: Optional project description
            location: Optional project save location
        """
        self.click_new_project()

        self.set_new_project_name(name)

        if description:
            self.set_new_project_description(description)

        if location:
            self.set_new_project_location(location)

        self.click_create_project()

        # Wait for project to be created
        time.sleep(1.0)

        if self.is_displayed(self.ERROR_MESSAGE):
            error = self.get_text(self.ERROR_MESSAGE)
            raise RuntimeError(f"Failed to create project: {error}")

        logger.info(f"Project '{name}' created successfully")

    # ==========================================================================
    # Open/Load Project
    # ==========================================================================

    def click_open_project(self):
        """Click the Open Project button."""
        self.click(self.OPEN_PROJECT_BUTTON)
        logger.info("Clicked open project")

    def open_project_by_name(self, name: str):
        """Open a project by selecting from the list."""
        self.select_project_by_name(name)
        # Double-click or click open button
        if self.is_displayed(self.OPEN_PROJECT_BUTTON):
            self.click(self.OPEN_PROJECT_BUTTON)
        else:
            self.double_click(self.PROJECT_LIST_ITEM)

        self.wait_for_loading()
        logger.info(f"Opened project: {name}")

    def open_recent_project(self, index: int = 0):
        """Open a recent project by index."""
        items = self.find_elements(self.RECENT_PROJECT_ITEM)
        if index >= len(items):
            raise IndexError(f"Recent project index {index} out of range")

        items[index].click()
        self.wait_for_loading()
        logger.info(f"Opened recent project at index: {index}")

    # ==========================================================================
    # Save Project
    # ==========================================================================

    def click_save_project(self):
        """Save the current project."""
        self.click(self.SAVE_PROJECT_BUTTON)
        self.wait_for_loading()
        logger.info("Saved project")

    def click_save_as(self):
        """Open Save As dialog."""
        self.click(self.SAVE_AS_BUTTON)
        logger.info("Clicked save as")

    def is_project_modified(self) -> bool:
        """Check if project has unsaved changes."""
        return self.is_displayed(self.PROJECT_MODIFIED_INDICATOR)

    def save_with_confirmation(self):
        """Save project with confirmation if needed."""
        if self.is_displayed(self.SAVE_DIALOG):
            self.click(self.SAVE_CONFIRM_BUTTON)
            self.wait_for_loading()

    # ==========================================================================
    # Close/Delete Project
    # ==========================================================================

    def click_close_project(self, save: bool = True):
        """
        Close the current project.

        Args:
            save: Whether to save changes before closing
        """
        self.click(self.CLOSE_PROJECT_BUTTON)

        # Handle save prompt if it appears
        if self.is_displayed(self.SAVE_DIALOG):
            if save:
                self.click(self.SAVE_CONFIRM_BUTTON)
            else:
                self.click(self.DONT_SAVE_BUTTON)

        self.wait_for_loading()
        logger.info("Closed project")

    def delete_project_by_name(self, name: str, confirm: bool = True):
        """Delete a project by name."""
        self.select_project_by_name(name)
        self.click(self.DELETE_PROJECT_BUTTON)

        if confirm:
            confirm_button = ElementLocator.by_name("Delete", "Confirm delete")
            try:
                self.click(confirm_button)
            except Exception:
                ok_button = ElementLocator.by_name("OK", "OK button")
                self.click(ok_button)

        logger.info(f"Deleted project: {name}")

    # ==========================================================================
    # Current Project Info
    # ==========================================================================

    def get_current_project_name(self) -> str:
        """Get the name of the currently open project."""
        try:
            return self.get_text(self.CURRENT_PROJECT_NAME)
        except Exception:
            return ""

    def get_current_project_path(self) -> str:
        """Get the path of the currently open project."""
        try:
            return self.get_text(self.CURRENT_PROJECT_PATH)
        except Exception:
            return ""

    def is_project_open(self) -> bool:
        """Check if a project is currently open."""
        name = self.get_current_project_name()
        return bool(name and name.strip())

    # ==========================================================================
    # Recent Projects
    # ==========================================================================

    def get_recent_project_count(self) -> int:
        """Get number of recent projects."""
        try:
            items = self.find_elements(self.RECENT_PROJECT_ITEM)
            return len(items)
        except Exception:
            return 0

    def clear_recent_projects(self):
        """Clear recent projects list."""
        if self.is_displayed(self.CLEAR_RECENT_BUTTON):
            self.click(self.CLEAR_RECENT_BUTTON)
            logger.info("Cleared recent projects")

    # ==========================================================================
    # Wait Helpers
    # ==========================================================================

    def wait_for_project_loaded(self, timeout: float = 30.0) -> bool:
        """Wait for project to finish loading."""
        start = time.time()
        while time.time() - start < timeout:
            if self.is_project_open() and not self.is_displayed(self.LOADING_INDICATOR):
                return True
            time.sleep(0.5)
        return False

    def wait_for_project_saved(self, timeout: float = 30.0) -> bool:
        """Wait for project save to complete."""
        start = time.time()
        while time.time() - start < timeout:
            if not self.is_project_modified():
                return True
            time.sleep(0.5)
        return False
