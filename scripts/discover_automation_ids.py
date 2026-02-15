#!/usr/bin/env python3
"""
Automation ID Discovery Tool for VoiceStudio

This script systematically discovers and documents all UI automation IDs
in the VoiceStudio application by:
1. Launching the application via WinAppDriver
2. Traversing the UI element tree
3. Extracting AutomationId, Name, ClassName, and other attributes
4. Generating JSON and Markdown reference documentation

Usage:
    python scripts/discover_automation_ids.py [--extended] [--verbose] [--panels]

Arguments:
    --extended  Include additional element attributes (BoundingRectangle, etc.)
    --verbose   Print detailed progress information
    --panels    Generate per-panel breakdown in output
"""

import argparse
import contextlib
import json
import os
import subprocess
import sys
import time
from datetime import datetime
from pathlib import Path
from typing import Any

import requests

# Configuration
WINAPPDRIVER_URL = os.environ.get("WINAPPDRIVER_URL", "http://127.0.0.1:4723")
APP_PATH = os.environ.get(
    "VS_APP_PATH",
    r"E:\VoiceStudio\src\VoiceStudio.App\bin\x64\Debug\net8.0-windows10.0.22621.0\win-x64\VoiceStudio.App.exe"
)
OUTPUT_DIR = Path(__file__).parent.parent / "docs" / "developer"
JSON_OUTPUT = OUTPUT_DIR / "automation_ids.json"
MD_OUTPUT = OUTPUT_DIR / "AUTOMATION_ID_REFERENCE.md"

# Panel navigation IDs for systematic discovery
PANEL_NAV_IDS = [
    "NavProfiles",
    "NavTraining",
    "NavRealTime",
    "NavRecording",
    "NavSettings",
    "NavLibrary",
    "NavDiagnostics",
    "NavPresets",
    "NavDeepfakeCreator",
    "NavScriptEditor",
    "NavMultiSpeakerDubbing",
]


class WinAppDriverClient:
    """Simple WinAppDriver client using raw HTTP requests."""

    def __init__(self, url: str):
        self.url = url.rstrip("/")
        self.session_id = None

    def create_session(self, app_path: str) -> bool:
        """Create a new WinAppDriver session."""
        capabilities = {
            "desiredCapabilities": {
                "app": app_path,
                "platformName": "Windows",
                "deviceName": "WindowsPC",
                "ms:waitForAppLaunch": "25",
            }
        }
        try:
            response = requests.post(
                f"{self.url}/session",
                json=capabilities,
                timeout=60
            )
            if response.status_code == 200:
                data = response.json()
                self.session_id = data.get("sessionId") or data.get("value", {}).get("sessionId")
                return self.session_id is not None
            return False
        except requests.RequestException as e:
            print(f"Failed to create session: {e}")
            return False

    def close_session(self):
        """Close the WinAppDriver session."""
        if self.session_id:
            with contextlib.suppress(requests.RequestException):
                requests.delete(f"{self.url}/session/{self.session_id}", timeout=10)
            self.session_id = None

    def find_element(self, strategy: str, value: str) -> dict | None:
        """Find a single element."""
        if not self.session_id:
            return None
        try:
            response = requests.post(
                f"{self.url}/session/{self.session_id}/element",
                json={"using": strategy, "value": value},
                timeout=10
            )
            if response.status_code == 200:
                data = response.json()
                return data.get("value")
            return None
        except requests.RequestException:
            return None

    def find_elements(self, strategy: str, value: str) -> list:
        """Find multiple elements."""
        if not self.session_id:
            return []
        try:
            response = requests.post(
                f"{self.url}/session/{self.session_id}/elements",
                json={"using": strategy, "value": value},
                timeout=30
            )
            if response.status_code == 200:
                data = response.json()
                return data.get("value", [])
            return []
        except requests.RequestException:
            return []

    def get_element_attribute(self, element_id: str, attribute: str) -> str | None:
        """Get an attribute from an element."""
        if not self.session_id:
            return None
        try:
            # Extract the actual element ID from the element dict
            if isinstance(element_id, dict):
                element_id = element_id.get("ELEMENT") or next(iter(element_id.values()))

            response = requests.get(
                f"{self.url}/session/{self.session_id}/element/{element_id}/attribute/{attribute}",
                timeout=10
            )
            if response.status_code == 200:
                data = response.json()
                return data.get("value")
            return None
        except requests.RequestException:
            return None

    def click_element(self, element_id: str) -> bool:
        """Click an element."""
        if not self.session_id:
            return False
        try:
            if isinstance(element_id, dict):
                element_id = element_id.get("ELEMENT") or next(iter(element_id.values()))

            response = requests.post(
                f"{self.url}/session/{self.session_id}/element/{element_id}/click",
                timeout=10
            )
            return response.status_code == 200
        except requests.RequestException:
            return False

    def find_all_descendants(self) -> list:
        """Find all descendant elements using XPath."""
        return self.find_elements("xpath", "//*")


def is_winappdriver_running() -> bool:
    """Check if WinAppDriver is running."""
    try:
        response = requests.get(f"{WINAPPDRIVER_URL}/status", timeout=5)
        return response.status_code == 200
    except requests.RequestException:
        return False


def start_winappdriver() -> subprocess.Popen | None:
    """Start WinAppDriver if not running."""
    winappdriver_path = r"C:\Program Files (x86)\Windows Application Driver\WinAppDriver.exe"
    if not Path(winappdriver_path).exists():
        winappdriver_path = r"C:\Program Files\Windows Application Driver\WinAppDriver.exe"

    if not Path(winappdriver_path).exists():
        print("ERROR: WinAppDriver not found. Please install from:")
        print("https://github.com/microsoft/WinAppDriver/releases")
        return None

    try:
        process = subprocess.Popen(
            [winappdriver_path],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            creationflags=subprocess.CREATE_NEW_CONSOLE
        )
        time.sleep(3)  # Wait for WinAppDriver to start
        return process
    except Exception as e:
        print(f"Failed to start WinAppDriver: {e}")
        return None


def discover_elements(
    client: WinAppDriverClient,
    include_extended: bool = False,
    verbose: bool = False
) -> list[dict[str, Any]]:
    """
    Discover all UI elements and extract their attributes.

    Args:
        client: WinAppDriver client instance
        include_extended: Include additional attributes like BoundingRectangle
        verbose: Print progress information

    Returns:
        List of element information dictionaries
    """
    elements = []
    seen_ids = set()

    if verbose:
        print("Discovering all UI elements...")

    all_elements = client.find_all_descendants()

    if verbose:
        print(f"Found {len(all_elements)} elements to process")

    for i, element in enumerate(all_elements):
        try:
            # Get element ID
            elem_id = element.get("ELEMENT") or next(iter(element.values())) if isinstance(element, dict) else element

            # Get basic attributes
            automation_id = client.get_element_attribute(elem_id, "AutomationId") or ""
            name = client.get_element_attribute(elem_id, "Name") or ""
            class_name = client.get_element_attribute(elem_id, "ClassName") or ""
            control_type = client.get_element_attribute(elem_id, "LocalizedControlType") or ""
            is_enabled = client.get_element_attribute(elem_id, "IsEnabled")
            is_offscreen = client.get_element_attribute(elem_id, "IsOffscreen")

            # Skip elements without useful identifiers
            if not automation_id and not name:
                continue

            # Create unique key for deduplication
            unique_key = f"{automation_id}|{name}|{class_name}"
            if unique_key in seen_ids:
                continue
            seen_ids.add(unique_key)

            element_info = {
                "AutomationId": automation_id,
                "Name": name,
                "ClassName": class_name,
                "LocalizedControlType": control_type,
                "IsEnabled": is_enabled == "True" if is_enabled else None,
                "IsOffscreen": is_offscreen == "True" if is_offscreen else None,
            }

            # Add extended attributes if requested
            if include_extended:
                framework_id = client.get_element_attribute(elem_id, "FrameworkId")
                bounding_rect = client.get_element_attribute(elem_id, "BoundingRectangle")
                element_info["FrameworkId"] = framework_id or ""
                element_info["BoundingRectangle"] = bounding_rect or ""

            elements.append(element_info)

            if verbose and (i + 1) % 50 == 0:
                print(f"Processed {i + 1}/{len(all_elements)} elements...")

        except Exception as e:
            if verbose:
                print(f"Error processing element {i}: {e}")
            continue

    if verbose:
        print(f"Discovered {len(elements)} unique elements with identifiers")

    return elements


def discover_by_panel(
    client: WinAppDriverClient,
    include_extended: bool = False,
    verbose: bool = False
) -> dict[str, list[dict[str, Any]]]:
    """
    Discover elements panel by panel for organized output.

    Args:
        client: WinAppDriver client instance
        include_extended: Include additional attributes
        verbose: Print progress information

    Returns:
        Dictionary mapping panel names to their elements
    """
    panel_data = {}

    # First, discover elements on the initial view
    if verbose:
        print("\nDiscovering elements on initial view...")
    panel_data["Initial"] = discover_elements(client, include_extended, verbose)

    # Navigate to each panel and discover its elements
    for nav_id in PANEL_NAV_IDS:
        panel_name = nav_id.replace("Nav", "")
        if verbose:
            print(f"\nNavigating to {panel_name} panel...")

        # Find and click the navigation item
        nav_element = client.find_element("accessibility id", nav_id)
        if nav_element:
            client.click_element(nav_element)
            time.sleep(1)  # Wait for panel to load

            # Discover elements on this panel
            panel_elements = discover_elements(client, include_extended, verbose=False)
            panel_data[panel_name] = panel_elements

            if verbose:
                print(f"  Found {len(panel_elements)} elements in {panel_name}")
        else:
            if verbose:
                print(f"  Warning: Could not find navigation item {nav_id}")
            panel_data[panel_name] = []

    return panel_data


def generate_json_output(
    elements: list[dict] | dict[str, list[dict]],
    output_path: Path,
    by_panel: bool = False
):
    """Generate JSON output file."""
    output_path.parent.mkdir(parents=True, exist_ok=True)

    output_data = {
        "generated_at": datetime.now().isoformat(),
        "total_elements": (
            sum(len(v) for v in elements.values()) if by_panel else len(elements)
        ),
        "by_panel": by_panel,
    }

    if by_panel:
        output_data["panels"] = elements
    else:
        output_data["elements"] = elements

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(output_data, f, indent=2, ensure_ascii=False)

    print(f"JSON output written to: {output_path}")


def generate_markdown_output(
    elements: list[dict] | dict[str, list[dict]],
    output_path: Path,
    by_panel: bool = False
):
    """Generate Markdown reference documentation."""
    output_path.parent.mkdir(parents=True, exist_ok=True)

    lines = [
        "# VoiceStudio Automation ID Reference",
        "",
        f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
        "",
        "This document lists all discoverable UI automation IDs in VoiceStudio.",
        "Use these IDs with WinAppDriver for UI testing.",
        "",
        "## Quick Reference",
        "",
    ]

    if by_panel:
        total = sum(len(v) for v in elements.values())
        lines.append(f"**Total Elements:** {total}")
        lines.append(f"**Panels Scanned:** {len(elements)}")
        lines.append("")

        # Table of contents
        lines.append("## Table of Contents")
        lines.append("")
        for panel_name in elements:
            anchor = panel_name.lower().replace(" ", "-")
            lines.append(f"- [{panel_name}](#{anchor})")
        lines.append("")

        # Per-panel sections
        for panel_name, panel_elements in elements.items():
            lines.append(f"## {panel_name}")
            lines.append("")
            lines.append(f"**Elements:** {len(panel_elements)}")
            lines.append("")

            # Group by control type
            by_type: dict[str, list[dict]] = {}
            for elem in panel_elements:
                ctrl_type = elem.get("LocalizedControlType", "unknown") or "unknown"
                if ctrl_type not in by_type:
                    by_type[ctrl_type] = []
                by_type[ctrl_type].append(elem)

            for ctrl_type in sorted(by_type.keys()):
                type_elements = by_type[ctrl_type]
                lines.append(f"### {ctrl_type.title()} ({len(type_elements)})")
                lines.append("")
                lines.append("| AutomationId | Name | ClassName |")
                lines.append("|---|---|---|")

                for elem in sorted(type_elements, key=lambda x: x.get("AutomationId", "")):
                    auto_id = elem.get("AutomationId", "") or "-"
                    name = elem.get("Name", "") or "-"
                    class_name = elem.get("ClassName", "") or "-"
                    # Escape pipe characters
                    name = name.replace("|", "\\|")[:50]
                    lines.append(f"| `{auto_id}` | {name} | {class_name} |")

                lines.append("")
    else:
        lines.append(f"**Total Elements:** {len(elements)}")
        lines.append("")

        # Group by control type
        by_type: dict[str, list[dict]] = {}
        for elem in elements:
            ctrl_type = elem.get("LocalizedControlType", "unknown") or "unknown"
            if ctrl_type not in by_type:
                by_type[ctrl_type] = []
            by_type[ctrl_type].append(elem)

        lines.append("## Elements by Type")
        lines.append("")

        for ctrl_type in sorted(by_type.keys()):
            type_elements = by_type[ctrl_type]
            lines.append(f"### {ctrl_type.title()} ({len(type_elements)})")
            lines.append("")
            lines.append("| AutomationId | Name | ClassName | Enabled |")
            lines.append("|---|---|---|---|")

            for elem in sorted(type_elements, key=lambda x: x.get("AutomationId", "")):
                auto_id = elem.get("AutomationId", "") or "-"
                name = elem.get("Name", "") or "-"
                class_name = elem.get("ClassName", "") or "-"
                is_enabled = "Yes" if elem.get("IsEnabled") else "No" if elem.get("IsEnabled") is False else "-"
                # Escape pipe characters and truncate long names
                name = name.replace("|", "\\|")[:50]
                lines.append(f"| `{auto_id}` | {name} | {class_name} | {is_enabled} |")

            lines.append("")

    # Usage section
    lines.extend([
        "## Usage in Tests",
        "",
        "```python",
        "# Find element by AutomationId",
        'element = driver.find_element("accessibility id", "NavProfiles")',
        "",
        "# Find element by Name",
        'element = driver.find_element("name", "Profiles")',
        "",
        "# Find element by ClassName",
        'elements = driver.find_elements("class name", "Button")',
        "```",
        "",
        "## Regenerating This Document",
        "",
        "```bash",
        "python scripts/discover_automation_ids.py --panels --extended",
        "```",
    ])

    with open(output_path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))

    print(f"Markdown output written to: {output_path}")


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Discover and document VoiceStudio automation IDs"
    )
    parser.add_argument(
        "--extended",
        action="store_true",
        help="Include extended attributes (BoundingRectangle, FrameworkId)"
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Print detailed progress information"
    )
    parser.add_argument(
        "--panels",
        action="store_true",
        help="Generate per-panel breakdown (navigates through all panels)"
    )
    args = parser.parse_args()

    print("=" * 60)
    print("VoiceStudio Automation ID Discovery Tool")
    print("=" * 60)

    # Check if app exists
    if not Path(APP_PATH).exists():
        print(f"ERROR: Application not found at: {APP_PATH}")
        print("Set VS_APP_PATH environment variable to the correct path.")
        sys.exit(1)

    # Start WinAppDriver if needed
    winappdriver_process = None
    if not is_winappdriver_running():
        print("Starting WinAppDriver...")
        winappdriver_process = start_winappdriver()
        if not winappdriver_process:
            sys.exit(1)
    else:
        print("WinAppDriver is already running")

    client = WinAppDriverClient(WINAPPDRIVER_URL)

    try:
        # Create session (launches app)
        print(f"Launching application: {APP_PATH}")
        if not client.create_session(APP_PATH):
            print("ERROR: Failed to create WinAppDriver session")
            sys.exit(1)

        print("Application launched successfully")
        time.sleep(3)  # Wait for app to fully load

        # Discover elements
        if args.panels:
            elements = discover_by_panel(client, args.extended, args.verbose)
        else:
            elements = discover_elements(client, args.extended, args.verbose)

        # Generate outputs
        generate_json_output(elements, JSON_OUTPUT, by_panel=args.panels)
        generate_markdown_output(elements, MD_OUTPUT, by_panel=args.panels)

        print("")
        print("=" * 60)
        print("Discovery complete!")
        if args.panels:
            total = sum(len(v) for v in elements.values())
            print(f"Total elements discovered: {total}")
            print(f"Panels scanned: {len(elements)}")
        else:
            print(f"Total elements discovered: {len(elements)}")
        print("=" * 60)

    finally:
        # Clean up
        print("Closing session...")
        client.close_session()

        if winappdriver_process:
            print("Stopping WinAppDriver...")
            winappdriver_process.terminate()


if __name__ == "__main__":
    main()
