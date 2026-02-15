# UI Automation Guide

This guide documents the UI automation framework for VoiceStudio, implementing Phase 3 of the Deterministic Sentinel Audio Workflow Implementation Plan.

## Overview

VoiceStudio uses **WinAppDriver** with a **Page Object Model** for UI automation testing. This approach provides:

- **Stable element identification** via AutomationIds
- **Maintainable tests** through page object abstraction
- **Reliable execution** with retry logic and wait utilities
- **CI integration** for nightly smoke testing

## Architecture

```
tests/ui/
├── conftest.py              # WinAppDriver session and fixtures
├── fixtures/
│   └── automation_ids.py    # Python-side ID registry
├── helpers/
│   └── navigation.py        # Navigation utilities
├── page_objects/
│   ├── __init__.py
│   ├── base_page.py         # Abstract base class
│   ├── studio_page.py       # Voice Synthesis panel
│   ├── clone_page.py        # Voice Cloning panel
│   ├── analyzer_page.py     # Audio Analysis panel
│   ├── effects_page.py      # Effects Mixer panel
│   └── library_page.py      # Library panel
└── test_smoke_workflows.py  # Smoke tests
```

## AutomationId Standards

### Naming Convention

All AutomationIds follow the pattern:

```
{ViewName}_{ElementType}_{Purpose}
```

Examples:
- `VoiceSynthesisView_Button_Synthesize`
- `LibraryView_ListView_Files`
- `DiagnosticsView_TabView_Main`

### Source of Truth

| Location | Purpose |
|----------|---------|
| `src/VoiceStudio.App/Constants/AutomationIds.cs` | C# constants for XAML binding |
| `tests/ui/fixtures/automation_ids.py` | Python registry for tests |

Keep these synchronized when adding new IDs.

### Adding New AutomationIds

1. **C# Side**: Add constant to `AutomationIds.cs`
   ```csharp
   public static class MyPanel
   {
       public const string Root = "MyPanelView_Root";
       public const string SaveButton = "MyPanelView_SaveButton";
   }
   ```

2. **XAML Side**: Reference in the view
   ```xml
   <UserControl
       AutomationProperties.AutomationId="MyPanelView_Root">
       <Button AutomationProperties.AutomationId="MyPanelView_SaveButton" />
   </UserControl>
   ```

3. **Python Side**: Add to `automation_ids.py` if needed for tests
   ```python
   "my_panel": {
       "root_id": "MyPanelView_Root",
       "key_elements": ["MyPanelView_SaveButton"],
   }
   ```

## Page Object Model

### Base Page Class

All page objects inherit from `BasePage`, which provides:

- **Element finding** with retry logic
- **Wait utilities** (wait for element, wait for enabled)
- **Actions** (click, type, select combobox)
- **Screenshot capture**
- **Navigation helpers**

### Creating a New Page Object

```python
from tests.ui.page_objects.base_page import BasePage

class MyPanelPage(BasePage):
    """Page object for MyPanel."""
    
    @property
    def root_automation_id(self) -> str:
        return "MyPanelView_Root"
    
    @property
    def nav_automation_id(self) -> str:
        return "NavMyPanel"
    
    # Element IDs
    SAVE_BUTTON = "MyPanelView_SaveButton"
    NAME_INPUT = "MyPanelView_NameInput"
    
    def enter_name(self, name: str) -> bool:
        """Enter a name."""
        return self.type_text(self.NAME_INPUT, name)
    
    def click_save(self) -> bool:
        """Click save button."""
        return self.click_with_retry(self.SAVE_BUTTON)
    
    def verify_elements_present(self) -> dict:
        """Verify critical elements."""
        return {
            "root": self.element_exists(self.root_automation_id),
            "save": self.element_exists(self.SAVE_BUTTON),
        }
```

### Using Page Objects in Tests

```python
import pytest
from tests.ui.page_objects import StudioPage

class TestMyFeature:
    
    @pytest.mark.smoke
    def test_panel_loads(self, driver):
        """Verify panel loads correctly."""
        page = StudioPage(driver)
        page.navigate()
        
        assert page.is_loaded()
        elements = page.verify_elements_present()
        assert all(elements.values())
```

## Writing Tests

### Test Markers

| Marker | Purpose |
|--------|---------|
| `@pytest.mark.smoke` | Quick verification tests (< 30s) |
| `@pytest.mark.slow` | Longer integration tests |
| `@pytest.mark.ui` | All UI tests |

### Test Structure

```python
class TestFeatureWorkflow:
    """Tests for feature workflow."""
    
    @pytest.mark.smoke
    def test_panel_loads(self, page_fixture):
        """Quick load verification."""
        assert page_fixture.is_loaded()
    
    @pytest.mark.smoke
    def test_critical_elements(self, page_fixture):
        """Verify critical elements exist."""
        elements = page_fixture.verify_elements_present()
        assert elements["root"]
    
    @pytest.mark.slow
    def test_full_workflow(self, page_fixture):
        """Complete workflow test."""
        # This test takes longer
        pass
```

### Fixtures

```python
@pytest.fixture
def studio_page(driver):
    """Get Studio page, navigated and loaded."""
    page = StudioPage(driver)
    page.navigate()
    assert page.is_loaded()
    return page
```

## Running Tests

### Local Execution

```powershell
# Start WinAppDriver
& "C:\Program Files (x86)\Windows Application Driver\WinAppDriver.exe"

# Run smoke tests
python -m pytest tests/ui/test_smoke_workflows.py -v -m smoke

# Run all UI tests
python -m pytest tests/ui/ -v

# Run specific test
python -m pytest tests/ui/test_smoke_workflows.py::TestVoiceSynthesisWorkflow -v
```

### CI Execution

The nightly workflow (`.github/workflows/sentinel_ui_smoke_nightly.yml`) runs:
- Build application
- Start WinAppDriver
- Execute smoke tests
- Capture screenshots on failure
- Upload artifacts

## Troubleshooting

### Element Not Found

1. **Verify AutomationId exists** in XAML
2. **Check element is visible** (not collapsed/hidden)
3. **Increase timeout** for slow-loading elements
4. **Use `capture_screenshot()`** to see UI state

### WinAppDriver Issues

```powershell
# Check WinAppDriver is running
Get-Process -Name "WinAppDriver"

# Restart WinAppDriver
Stop-Process -Name "WinAppDriver" -Force
Start-Process "C:\Program Files (x86)\Windows Application Driver\WinAppDriver.exe"
```

### Session Failures

The `WinAppDriverSession` class in `conftest.py` handles Selenium 4.x compatibility issues. If sessions fail:

1. Check app path is correct
2. Verify app builds and runs manually
3. Check WinAppDriver console for errors

## Best Practices

### DO

- ✅ Use descriptive AutomationIds
- ✅ Add retry logic for flaky elements
- ✅ Capture screenshots on failure
- ✅ Keep tests independent
- ✅ Use page objects for all interactions

### DON'T

- ❌ Use positional locators (XPath indices)
- ❌ Hard-code wait times without retry
- ❌ Share state between tests
- ❌ Skip AutomationIds for important elements

## CI Integration

### Nightly Workflow

The `sentinel_ui_smoke_nightly.yml` workflow runs at 3:00 AM UTC daily:

1. Builds the application
2. Validates page objects (lint, type check)
3. Runs UI smoke tests
4. Reports results

### Manual Trigger

```bash
gh workflow run sentinel_ui_smoke_nightly.yml
```

### Artifacts

Test artifacts are uploaded for 7 days:
- Test results XML
- Screenshots (on failure)
- Console logs

## Related Documents

- [DETERMINISTIC_SENTINEL_IMPLEMENTATION_PLAN.md](../design/DETERMINISTIC_SENTINEL_IMPLEMENTATION_PLAN.md)
- [AutomationIds.cs](../../src/VoiceStudio.App/Constants/AutomationIds.cs)
- [automation_ids.py](../../tests/ui/fixtures/automation_ids.py)
