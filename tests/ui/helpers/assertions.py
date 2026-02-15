"""
UI Assertion Helpers for UI Tests.

Provides reusable assertion utilities for WinAppDriver-based UI testing.
"""

from __future__ import annotations

import time
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from tests.ui.conftest import WinAppDriverElement, WinAppDriverSession


# =============================================================================
# Assertion Helper Class
# =============================================================================


class UIAssertions:
    """Helper class for UI assertions in tests."""

    def __init__(self, driver: WinAppDriverSession):
        """
        Initialize assertions helper.

        Args:
            driver: WinAppDriverSession instance.
        """
        self.driver = driver

    def element_exists(self, automation_id: str) -> bool:
        """
        Check if an element exists.

        Args:
            automation_id: Element's automation ID.

        Returns:
            True if element exists, False otherwise.
        """
        try:
            self.driver.find_element("accessibility id", automation_id)
            return True
        except RuntimeError:
            return False

    def element_is_enabled(self, automation_id: str) -> bool:
        """
        Check if an element is enabled.

        Args:
            automation_id: Element's automation ID.

        Returns:
            True if element is enabled, False if disabled or not found.
        """
        try:
            element = self.driver.find_element("accessibility id", automation_id)
            return element.is_enabled()
        except RuntimeError:
            return False

    def wait_for_element(
        self, automation_id: str, timeout: float = 10, poll_interval: float = 0.5
    ) -> WinAppDriverElement | None:
        """
        Wait for an element to appear.

        Args:
            automation_id: Element's automation ID.
            timeout: Maximum time to wait (seconds).
            poll_interval: Time between checks (seconds).

        Returns:
            Element if found, None if timeout.
        """
        start_time = time.time()
        while time.time() - start_time < timeout:
            try:
                return self.driver.find_element("accessibility id", automation_id)
            except RuntimeError:
                time.sleep(poll_interval)
        return None

    def wait_for_element_gone(
        self, automation_id: str, timeout: float = 10, poll_interval: float = 0.5
    ) -> bool:
        """
        Wait for an element to disappear.

        Args:
            automation_id: Element's automation ID.
            timeout: Maximum time to wait (seconds).
            poll_interval: Time between checks (seconds).

        Returns:
            True if element disappeared, False if still present.
        """
        start_time = time.time()
        while time.time() - start_time < timeout:
            try:
                self.driver.find_element("accessibility id", automation_id)
                time.sleep(poll_interval)
            except RuntimeError:
                return True
        return False

    def assert_element_exists(self, automation_id: str, message: str = "") -> None:
        """
        Assert that an element exists.

        Args:
            automation_id: Element's automation ID.
            message: Optional failure message.

        Raises:
            AssertionError: If element does not exist.
        """
        if not self.element_exists(automation_id):
            default_msg = f"Element with automation ID '{automation_id}' not found"
            raise AssertionError(message or default_msg)

    def assert_element_enabled(self, automation_id: str, message: str = "") -> None:
        """
        Assert that an element is enabled.

        Args:
            automation_id: Element's automation ID.
            message: Optional failure message.

        Raises:
            AssertionError: If element is not enabled or not found.
        """
        if not self.element_is_enabled(automation_id):
            default_msg = f"Element '{automation_id}' is not enabled or not found"
            raise AssertionError(message or default_msg)

    def assert_elements_exist(
        self, automation_ids: list[str], require_all: bool = True
    ) -> list[str]:
        """
        Assert that multiple elements exist.

        Args:
            automation_ids: List of automation IDs.
            require_all: If True, all must exist. If False, at least one must exist.

        Returns:
            List of IDs that were found.

        Raises:
            AssertionError: If condition not met.
        """
        found = []
        for aid in automation_ids:
            if self.element_exists(aid):
                found.append(aid)

        if require_all and len(found) != len(automation_ids):
            missing = set(automation_ids) - set(found)
            raise AssertionError(f"Elements not found: {missing}")

        if not require_all and len(found) == 0:
            raise AssertionError(f"None of the elements found: {automation_ids}")

        return found

    def count_elements(self, automation_id: str) -> int:
        """
        Count elements with a given automation ID.

        Args:
            automation_id: Element's automation ID.

        Returns:
            Number of elements found.
        """
        try:
            elements = self.driver.find_elements("accessibility id", automation_id)
            return len(elements)
        except RuntimeError:
            return 0


# =============================================================================
# Convenience Functions
# =============================================================================


def element_exists(driver: WinAppDriverSession, automation_id: str) -> bool:
    """
    Check if an element exists.

    Args:
        driver: WinAppDriverSession instance.
        automation_id: Element's automation ID.

    Returns:
        True if element exists.
    """
    helper = UIAssertions(driver)
    return helper.element_exists(automation_id)


def wait_for_element(
    driver: WinAppDriverSession,
    automation_id: str,
    timeout: float = 10,
) -> WinAppDriverElement | None:
    """
    Wait for an element to appear.

    Args:
        driver: WinAppDriverSession instance.
        automation_id: Element's automation ID.
        timeout: Maximum wait time.

    Returns:
        Element if found, None otherwise.
    """
    helper = UIAssertions(driver)
    return helper.wait_for_element(automation_id, timeout)


def assert_element_exists(
    driver: WinAppDriverSession, automation_id: str, message: str = ""
) -> None:
    """
    Assert that an element exists.

    Args:
        driver: WinAppDriverSession instance.
        automation_id: Element's automation ID.
        message: Optional failure message.

    Raises:
        AssertionError: If element not found.
    """
    helper = UIAssertions(driver)
    helper.assert_element_exists(automation_id, message)
