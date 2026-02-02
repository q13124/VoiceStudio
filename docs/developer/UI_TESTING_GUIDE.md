# UI Testing Guide

This guide covers UI testing strategies and frameworks for VoiceStudio.

## Table of Contents

1. [Framework Overview](#framework-overview)
2. [Primary Framework: MSTest with UITestMethod](#primary-framework-mstest-with-uitestmethod)
3. [Secondary Framework: WinAppDriver/Appium](#secondary-framework-winappdriver-appium)
4. [When to Use Each Framework](#when-to-use-each-framework)
5. [Running Tests Locally](#running-tests-locally)
6. [Writing New Tests](#writing-new-tests)
7. [CI/CD Integration](#cicd-integration)

---

## Framework Overview

VoiceStudio uses a **dual UI testing framework**:

| Framework | Location | Use Case | External Dependencies |
|-----------|----------|----------|----------------------|
| MSTest + `[UITestMethod]` | `src/VoiceStudio.App.Tests/UI/` | Component tests, ViewModel tests, UI unit tests | None (integrated) |
| WinAppDriver/Appium | `tests/ui/` | E2E workflows, full app automation, accessibility | WinAppDriver service |

### Framework Selection Decision

**Primary: MSTest with `[UITestMethod]`**
- Official WinUI 3 support via Windows App SDK
- No external service dependencies
- Runs with standard `dotnet test`
- Best for: Component tests, isolated UI behavior

**Secondary: WinAppDriver/Appium (Python)**
- Full application automation
- Cross-panel navigation testing
- Accessibility verification
- Best for: E2E scenarios, regression testing

---

## Primary Framework: MSTest with UITestMethod

### Location

```
src/VoiceStudio.App.Tests/UI/
├── UITestMethodAttribute.cs    # Custom attribute for WinUI 3 tests
├── SmokeTestBase.cs            # Base class with helper methods
├── LaunchSmokeTests.cs         # App launch tests
├── PanelNavigationSmokeTests.cs # Panel navigation tests
├── CommonActionsSmokeTests.cs   # Common action tests
├── CriticalPathSmokeTests.cs    # Critical path tests
├── SettingsPanelTests.cs        # Settings panel tests
├── WizardFlowTests.cs           # Wizard flow tests
└── KeyboardShortcutTests.cs     # Keyboard shortcut tests
```

### How It Works

The `[UITestMethod]` attribute:
1. Creates an STA thread (required for WinUI 3)
2. Initializes Windows App SDK bootstrap
3. Creates a DispatcherQueue
4. Initializes WindowsXamlManager
5. Executes the test method

### Example Test

```csharp
using Microsoft.VisualStudio.TestTools.UnitTesting;
using VoiceStudio.App.Tests.UI;

[TestClass]
public class MyUITests : SmokeTestBase
{
    [UITestMethod]
    public void MyControl_ShouldRender()
    {
        // Arrange
        VerifyApplicationStarted();
        
        // Act
        await WaitForPanelAsync("SettingsPanel");
        
        // Assert
        // Verify expected state
    }
}
```

### Running MSTest UI Tests

```powershell
# Run all UI tests
dotnet test src/VoiceStudio.App.Tests -c Debug --filter "Category=UI"

# Run specific test class
dotnet test src/VoiceStudio.App.Tests -c Debug --filter "FullyQualifiedName~LaunchSmokeTests"

# Run with verbose output
dotnet test src/VoiceStudio.App.Tests -c Debug --filter "Category=UI" -v detailed
```

---

## Secondary Framework: WinAppDriver/Appium

### Location

```
tests/ui/
├── conftest.py                     # Pytest fixtures, WinAppDriver setup
├── test_navigation.py              # Navigation tests
├── test_panel_functionality.py     # Panel tests (20+ panels)
├── test_user_interactions.py       # User interaction tests
├── test_command_palette.py         # Command palette tests
├── test_keyboard_shortcuts.py      # Keyboard shortcut tests
├── PANEL_TESTING_SPECIFICATION.md  # Test specification
└── README.md                       # Setup instructions
```

### Prerequisites

1. **Install WinAppDriver**
   ```powershell
   choco install winappdriver -y
   # OR download from: https://github.com/microsoft/WinAppDriver/releases
   ```

2. **Enable Developer Mode** (Windows Settings > Privacy & Security > For Developers)

3. **Install Python dependencies**
   ```powershell
   cd tests/ui
   pip install -r requirements.txt
   ```

### Running WinAppDriver Tests

```powershell
# 1. Start WinAppDriver (in separate terminal)
Start-Process "C:\Program Files (x86)\Windows Application Driver\WinAppDriver.exe"

# 2. Build the app
dotnet publish src/VoiceStudio.App -c Debug -r win-x64

# 3. Set environment variable
$env:VS_APP_PATH = "$(Get-Location)\.buildlogs\x64\Debug\net8.0-windows10.0.19041.0\win-x64\publish\VoiceStudio.App.exe"

# 4. Run tests
cd tests/ui
pytest test_navigation.py -v
```

### Example Test

```python
import pytest
from appium import webdriver

def test_panel_navigation(driver):
    """Test navigating to Settings panel."""
    # Find and click Settings in navigation
    settings_btn = driver.find_element_by_accessibility_id("Settings_NavButton")
    settings_btn.click()
    
    # Verify panel loaded
    settings_panel = driver.find_element_by_accessibility_id("SettingsPanel")
    assert settings_panel.is_displayed()
```

---

## When to Use Each Framework

| Scenario | Framework | Reason |
|----------|-----------|--------|
| ViewModel logic with UI binding | MSTest `[UITestMethod]` | Isolated, no app launch needed |
| Single control behavior | MSTest `[UITestMethod]` | Fast, focused |
| Panel navigation flow | WinAppDriver | Full app context |
| Wizard multi-step flow | WinAppDriver | Requires app state |
| Keyboard shortcuts | Either | MSTest for logic, WinAppDriver for actual keys |
| Accessibility (screen reader) | WinAppDriver | Requires full UI tree |
| CI/CD smoke test | Gate C script | Fastest, built-in |

### Decision Flowchart

```
Need to test UI?
├── Is it a single component/control?
│   └── YES → MSTest [UITestMethod]
├── Does it require app launch?
│   └── NO → MSTest [UITestMethod]
├── Does it span multiple panels?
│   └── YES → WinAppDriver
├── Is it accessibility testing?
│   └── YES → WinAppDriver
└── Default → MSTest [UITestMethod]
```

---

## Running Tests Locally

### Quick Smoke Test (Recommended)

```powershell
# Gate C UI smoke test - fastest verification
.\scripts\gatec-publish-launch.ps1 -Configuration Release -RuntimeIdentifier win-x64 -UiSmoke
```

This runs the built-in smoke test that:
- Launches the app with `--smoke-ui` flag
- Navigates to all 11 core panels
- Detects binding failures
- Generates `ui_smoke_summary.json`

### Full Test Suite

```powershell
# 1. C# UI tests
dotnet test src/VoiceStudio.App.Tests -c Debug --filter "Category=UI"

# 2. Python WinAppDriver tests (requires WinAppDriver running)
cd tests/ui && pytest -v
```

---

## Writing New Tests

### MSTest UI Test

1. Create file in `src/VoiceStudio.App.Tests/UI/`
2. Inherit from `SmokeTestBase`
3. Use `[UITestMethod]` attribute
4. Use `[TestCategory("UI")]` for filtering

```csharp
[TestClass]
public class MyFeatureTests : SmokeTestBase
{
    [UITestMethod]
    [TestCategory("UI")]
    public void Feature_ShouldWork()
    {
        VerifyApplicationStarted();
        // Test implementation
    }
}
```

### WinAppDriver Test

1. Create file in `tests/ui/`
2. Use pytest fixtures from `conftest.py`
3. Find elements by `AccessibilityId` (from `AutomationProperties.AutomationId`)

```python
def test_my_feature(driver):
    """Test description."""
    element = driver.find_element_by_accessibility_id("MyControl_AutomationId")
    element.click()
    assert driver.find_element_by_accessibility_id("ExpectedResult").is_displayed()
```

---

## CI/CD Integration

### Current CI Workflow

The `.github/workflows/test.yml` includes:
- `test-frontend`: Runs C# tests (includes `[UITestMethod]` tests)
- Gate C smoke test via `gatec-publish-launch.ps1`

### WinAppDriver CI (Manual Trigger)

WinAppDriver tests require a Windows desktop session. Use `workflow_dispatch` for manual triggering:

```yaml
ui-automation:
  runs-on: windows-latest
  if: github.event_name == 'workflow_dispatch'
  steps:
    - uses: actions/checkout@v4
    - name: Install WinAppDriver
      run: choco install winappdriver -y
    - name: Start WinAppDriver
      run: Start-Process "C:\Program Files (x86)\Windows Application Driver\WinAppDriver.exe"
    - name: Build App
      run: dotnet publish src/VoiceStudio.App -c Release -r win-x64
    - name: Run UI Tests
      run: |
        cd tests/ui
        pip install -r requirements.txt
        pytest test_navigation.py -v
```

---

## Troubleshooting

### MSTest UI Tests

| Issue | Solution |
|-------|----------|
| "Bootstrap.Initialize failed" | Ensure Windows App SDK 1.8+ is installed |
| "DispatcherQueue is null" | Test must use `[UITestMethod]`, not `[TestMethod]` |
| Tests hang | Check for deadlocks in async code |

### WinAppDriver Tests

| Issue | Solution |
|-------|----------|
| "Failed to create session" | Start WinAppDriver service first |
| "Element not found" | Check AutomationId in XAML, use Inspect.exe |
| "Access denied" | Enable Developer Mode in Windows |

---

## References

- [WinUI 3 Testing Guide](../testing/WINUI3_TEST_SETUP_GUIDE.md)
- [Panel Testing Specification](../../tests/ui/PANEL_TESTING_SPECIFICATION.md)
- [Accessibility Testing Guide](../testing/ACCESSIBILITY_TESTING_GUIDE.md)
- [WinAppDriver GitHub](https://github.com/microsoft/WinAppDriver)

---

**Last Updated:** 2026-02-02  
**Framework Versions:** MSTest 3.6+, Appium.WebDriver 5.0, WinAppDriver 1.2
