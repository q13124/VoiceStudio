# VoiceStudio Quantum+ UI Tests

UI automation tests for VoiceStudio Quantum+ using WinAppDriver.

## Overview

This directory contains UI automation tests that verify:
- Panel functionality and interactions
- User interface navigation
- User interactions (clicks, typing, selections)
- Panel state management
- Command palette functionality
- Keyboard shortcuts

## Prerequisites

### 1. WinAppDriver Installation

**Download and Install:**
1. Download WinAppDriver from: https://github.com/Microsoft/WinAppDriver/releases
2. Install WinAppDriver (requires Windows 10 version 1809 or later)
3. Start WinAppDriver service:
   ```powershell
   # Run as Administrator
   "C:\Program Files (x86)\Windows Application Driver\WinAppDriver.exe"
   ```

**Verify Installation:**
```powershell
# Check if WinAppDriver is running
Get-Process WinAppDriver
```

### 2. Application Build

Build the VoiceStudio application in Debug mode (automation IDs are only set in DEBUG builds):

```powershell
cd src/VoiceStudio.App
dotnet build --configuration Debug
```

### 3. Python Dependencies

```bash
pip install Appium-Python-Client selenium
```

## Test Structure

```
tests/ui/
├── README.md                    # This file
├── conftest.py                  # Pytest configuration and fixtures
├── test_panel_functionality.py  # Panel interaction tests
├── test_navigation.py           # Navigation and routing tests
├── test_user_interactions.py    # User interaction tests
├── test_command_palette.py      # Command palette tests
└── test_keyboard_shortcuts.py   # Keyboard shortcut tests
```

## Running Tests

### Start WinAppDriver

**Option 1: Manual Start**
```powershell
# Run as Administrator
"C:\Program Files (x86)\Windows Application Driver\WinAppDriver.exe"
```

**Option 2: Automated Start (included in test setup)**
Tests will attempt to start WinAppDriver automatically if not running.

### Run All UI Tests

```bash
# From project root
pytest tests/ui/ -v
```

### Run Specific Test File

```bash
pytest tests/ui/test_panel_functionality.py -v
```

### Run Specific Test

```bash
pytest tests/ui/test_panel_functionality.py::test_profiles_panel_loads -v
```

## Test Configuration

### Application Path

Update `conftest.py` with the correct path to your application executable:

```python
APP_PATH = r"C:\path\to\VoiceStudio.App.exe"
```

### Timeout Settings

Default timeouts can be adjusted in `conftest.py`:

```python
IMPLICIT_WAIT = 10  # seconds
EXPLICIT_WAIT = 30  # seconds
```

## Writing New Tests

### Example Test

```python
import pytest
from appium import webdriver
from appium.options.windows import WindowsOptions

def test_profiles_panel_loads(driver):
    """Test that Profiles panel loads correctly."""
    # Find and click Profiles panel button
    profiles_button = driver.find_element("accessibility id", "NavRail_ProfilesButton")
    profiles_button.click()
    
    # Wait for panel to load
    profiles_panel = driver.find_element("accessibility id", "ProfilesView_Root")
    assert profiles_panel is not None
    
    # Verify panel content
    profile_list = driver.find_element("accessibility id", "ProfilesView_ProfileList")
    assert profile_list is not None
```

### Automation IDs

All UI elements should have automation IDs set (see `docs/design/UI_TEST_HOOKS.md`).

Format: `[ComponentName]_[ElementType]_[Purpose]`

Examples:
- `ProfilesView_Root`
- `TimelineView_PlayButton`
- `CommandPalette_SearchBox`

## Test Categories

### Panel Functionality Tests
- Panel loading and initialization
- Panel content display
- Panel state management
- Panel interactions

### Navigation Tests
- Panel switching
- Panel routing
- Navigation rail functionality
- Tab navigation

### User Interaction Tests
- Button clicks
- Text input
- Dropdown selections
- Slider adjustments
- Checkbox toggles

### Command Palette Tests
- Command palette opening/closing
- Command search
- Command execution
- Keyboard navigation

### Keyboard Shortcut Tests
- Shortcut key combinations
- Shortcut functionality
- Shortcut help display

## Troubleshooting

### WinAppDriver Not Starting

**Error:** `Connection refused`

**Solution:**
1. Ensure WinAppDriver is running as Administrator
2. Check Windows Firewall settings
3. Verify WinAppDriver is listening on port 4723

### Application Not Found

**Error:** `Application not found`

**Solution:**
1. Verify application path in `conftest.py`
2. Ensure application is built in Debug mode
3. Check that executable exists at specified path

### Element Not Found

**Error:** `NoSuchElementException`

**Solution:**
1. Verify automation ID is set in application code
2. Check that element is visible (not hidden or collapsed)
3. Increase wait timeout if element loads slowly
4. Verify element exists in DEBUG build

### Tests Timing Out

**Solution:**
1. Increase timeout values in `conftest.py`
2. Add explicit waits for slow-loading elements
3. Check application performance

## Continuous Integration

### GitHub Actions Example

```yaml
- name: Start WinAppDriver
  run: |
    Start-Process -FilePath "C:\Program Files (x86)\Windows Application Driver\WinAppDriver.exe" -WindowStyle Hidden
    
- name: Run UI Tests
  run: pytest tests/ui/ -v
```

### Local CI Setup

1. Install WinAppDriver on CI machine
2. Configure WinAppDriver to start on boot
3. Update application path in test configuration
4. Run tests as part of CI pipeline

## Best Practices

1. **Use Explicit Waits:** Don't rely on fixed sleep times
2. **Clean Test Data:** Reset application state between tests
3. **Isolate Tests:** Each test should be independent
4. **Use Fixtures:** Share common setup/teardown code
5. **Verify State:** Assert expected outcomes, not just actions
6. **Handle Errors:** Gracefully handle expected errors

## Limitations

- Tests require application to be built in DEBUG mode (automation IDs)
- Tests require WinAppDriver service to be running
- Tests require Windows 10 version 1809 or later
- Some UI elements may not be accessible if not properly configured

## Future Enhancements

- [ ] Screenshot capture on test failure
- [ ] Video recording of test execution
- [ ] Performance metrics during UI tests
- [ ] Cross-browser testing (if web components added)
- [ ] Accessibility testing integration

---

**Last Updated:** 2025-01-28  
**Status:** Framework Ready - Requires Application Build and WinAppDriver

