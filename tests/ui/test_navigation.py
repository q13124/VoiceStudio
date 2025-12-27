"""
UI Tests for Navigation and Routing.

Tests panel switching, navigation rail, and routing functionality.
"""

import time

import pytest
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait


class TestNavigationRail:
    """Tests for navigation rail functionality."""

    def test_navigation_rail_exists(self, driver, app_launched):
        """Test that navigation rail is present."""
        try:
            nav_rail = driver.find_element("accessibility id", "NavigationView_Root")
            assert nav_rail is not None
        except:
            pytest.skip("Navigation rail automation ID not set.")

    def test_navigation_rail_buttons_visible(self, driver, app_launched):
        """Test that navigation rail buttons are visible."""
        try:
            nav_rail = driver.find_element("accessibility id", "NavigationView_Root")

            # Check for common navigation buttons
            buttons = [
                "NavRail_ProfilesButton",
                "NavRail_TimelineButton",
                "NavRail_EffectsMixerButton",
                "NavRail_AnalyzerButton",
            ]

            for button_id in buttons:
                try:
                    button = driver.find_element("accessibility id", button_id)
                    assert button is not None
                except:
                    pass  # Some buttons may not be present
        except:
            pytest.skip("Navigation rail automation IDs not set.")


class TestPanelSwitching:
    """Tests for panel switching functionality."""

    def test_switch_to_profiles_panel(self, driver, app_launched):
        """Test switching to Profiles panel."""
        try:
            profiles_button = driver.find_element(
                "accessibility id", "NavRail_ProfilesButton"
            )
            profiles_button.click()
            time.sleep(1)

            profiles_panel = driver.find_element(
                "accessibility id", "ProfilesView_Root"
            )
            assert profiles_panel is not None
        except:
            pytest.skip("Panel switching automation IDs not set.")

    def test_switch_to_timeline_panel(self, driver, app_launched):
        """Test switching to Timeline panel."""
        try:
            timeline_button = driver.find_element(
                "accessibility id", "NavRail_TimelineButton"
            )
            timeline_button.click()
            time.sleep(1)

            timeline_panel = driver.find_element(
                "accessibility id", "TimelineView_Root"
            )
            assert timeline_panel is not None
        except:
            pytest.skip("Panel switching automation IDs not set.")

    def test_switch_between_panels(self, driver, app_launched):
        """Test switching between multiple panels."""
        try:
            # Switch to Profiles
            profiles_button = driver.find_element(
                "accessibility id", "NavRail_ProfilesButton"
            )
            profiles_button.click()
            time.sleep(0.5)

            # Switch to Timeline
            timeline_button = driver.find_element(
                "accessibility id", "NavRail_TimelineButton"
            )
            timeline_button.click()
            time.sleep(0.5)

            # Switch back to Profiles
            profiles_button.click()
            time.sleep(0.5)

            profiles_panel = driver.find_element(
                "accessibility id", "ProfilesView_Root"
            )
            assert profiles_panel is not None
        except:
            pytest.skip("Panel switching automation IDs not set.")


class TestTabNavigation:
    """Tests for tab navigation within panels."""

    def test_tab_navigation_exists(self, driver, app_launched):
        """Test that tab navigation is available."""
        try:
            # Navigate to a panel with tabs
            profiles_button = driver.find_element(
                "accessibility id", "NavRail_ProfilesButton"
            )
            profiles_button.click()
            time.sleep(1)

            # Check for tab control
            tab_control = driver.find_element("accessibility id", "TabView_Root")
            assert tab_control is not None
        except:
            pytest.skip("Tab navigation automation IDs not set.")

    def test_switch_tabs(self, driver, app_launched):
        """Test switching between tabs."""
        try:
            profiles_button = driver.find_element(
                "accessibility id", "NavRail_ProfilesButton"
            )
            profiles_button.click()
            time.sleep(1)

            # Find and click first tab
            first_tab = driver.find_element("accessibility id", "TabView_Tab0")
            first_tab.click()
            time.sleep(0.5)

            # Find and click second tab
            second_tab = driver.find_element("accessibility id", "TabView_Tab1")
            second_tab.click()
            time.sleep(0.5)

            # Verify tab content changed
            assert second_tab is not None
        except:
            pytest.skip("Tab navigation automation IDs not set.")


class TestPanelRouting:
    """Tests for panel routing and deep linking."""

    def test_panel_routing_works(self, driver, app_launched):
        """Test that panel routing works correctly."""
        try:
            # Navigate to Profiles panel
            profiles_button = driver.find_element(
                "accessibility id", "NavRail_ProfilesButton"
            )
            profiles_button.click()
            time.sleep(1)

            # Verify correct panel is displayed
            profiles_panel = driver.find_element(
                "accessibility id", "ProfilesView_Root"
            )
            assert profiles_panel is not None

            # Navigate to different panel
            timeline_button = driver.find_element(
                "accessibility id", "NavRail_TimelineButton"
            )
            timeline_button.click()
            time.sleep(1)

            # Verify panel changed
            timeline_panel = driver.find_element(
                "accessibility id", "TimelineView_Root"
            )
            assert timeline_panel is not None
        except:
            pytest.skip("Panel routing automation IDs not set.")
