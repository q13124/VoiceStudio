# UI Test Matrix

This document defines the UI testing strategy for VoiceStudio, including test categories, automation frameworks, and coverage requirements.

## Test Categories

### 1. Smoke Tests (< 5 minutes)
Critical path verification run on every PR.

| Test | Description | Framework | AutomationIds Required |
|------|-------------|-----------|------------------------|
| App Launch | App starts without crash | FlaUI | MainWindow |
| Voice Synthesis Flow | Text → Voice synthesis works | FlaUI | VoiceSynthesisView.*, SynthesizeButton |
| Profile Management | Create/edit/delete profile | FlaUI | ProfilesView.*, NewProfileButton |
| Project Persistence | New project → Save → Load | FlaUI | MainMenu.*, SaveProjectButton |
| Settings Persistence | Change setting → Restart → Verify | FlaUI | SettingsView.* |
| Theme Switching | Switch themes without crash | FlaUI | ThemeEditorView.* |

### 2. E2E Tests (5-15 minutes)
Full workflow verification run on merge to main.

| Test | Description | Framework | Priority |
|------|-------------|-----------|----------|
| Voice Cloning Wizard | Full wizard flow with audio | WinAppDriver | HIGH |
| Multi-voice Project | Multiple voices in timeline | WinAppDriver | HIGH |
| Batch Processing | Process multiple files | WinAppDriver | MEDIUM |
| Real-time Converter | Live audio conversion | WinAppDriver | MEDIUM |
| Plugin Management | Install/enable/disable plugin | WinAppDriver | LOW |

### 3. Visual Regression Tests
Screenshot comparison for UI changes.

| Screen | Baseline | Tolerance |
|--------|----------|-----------|
| Main Window (Dark) | `baselines/main-dark.png` | 1% |
| Main Window (Light) | `baselines/main-light.png` | 1% |
| Settings Panel | `baselines/settings.png` | 2% |
| Theme Editor | `baselines/theme-editor.png` | 2% |

## Test Frameworks

### C# (FlaUI)
- **Location**: `src/VoiceStudio.App.Tests/UI/`
- **Usage**: Smoke tests, fast feedback
- **CI Integration**: MSTest on Windows runners

```csharp
// Example FlaUI test
[TestMethod]
public void VoiceSynthesis_CanSynthesizeText()
{
    using var app = Application.Launch("VoiceStudio.exe");
    var mainWindow = app.GetMainWindow(Automation);
    
    var textBox = mainWindow.FindFirstDescendant(
        cf => cf.ByAutomationId("VoiceSynthesis.TextInput"));
    textBox.AsTextBox().Enter("Hello world");
    
    var synthesizeBtn = mainWindow.FindFirstDescendant(
        cf => cf.ByAutomationId("VoiceSynthesis.SynthesizeButton"));
    synthesizeBtn.AsButton().Click();
    
    // Assert synthesis completed
    var status = mainWindow.FindFirstDescendant(
        cf => cf.ByAutomationId("VoiceSynthesis.StatusLabel"));
    Retry.WhileFalse(() => status.AsLabel().Text.Contains("Complete"));
}
```

### Python (WinAppDriver/Appium)
- **Location**: `tests/e2e/`
- **Usage**: Complex E2E flows, cross-platform potential
- **CI Integration**: pytest with WinAppDriver

```python
# Example WinAppDriver test
def test_voice_synthesis_flow(self, driver):
    text_input = driver.find_element(
        AppiumBy.ACCESSIBILITY_ID, "VoiceSynthesis.TextInput"
    )
    text_input.send_keys("Hello world")
    
    synthesize_btn = driver.find_element(
        AppiumBy.ACCESSIBILITY_ID, "VoiceSynthesis.SynthesizeButton"
    )
    synthesize_btn.click()
    
    # Wait for completion
    status = WebDriverWait(driver, 30).until(
        EC.text_to_be_present_in_element(
            (AppiumBy.ACCESSIBILITY_ID, "VoiceSynthesis.StatusLabel"),
            "Complete"
        )
    )
    assert status
```

## AutomationId Conventions

### Naming Pattern
`{PanelName}.{ElementType}.{Purpose}`

Examples:
- `VoiceSynthesis.TextInput.SourceText`
- `VoiceSynthesis.Button.Synthesize`
- `VoiceSynthesis.ComboBox.VoiceSelector`
- `Profiles.ListView.ProfileList`

### Required Coverage
| Category | Min Coverage | Current |
|----------|--------------|---------|
| Required (Buttons, TextBoxes) | 100% | ~80% |
| Recommended (Labels, Lists) | 80% | ~15% |
| Optional (Decorative) | 0% | N/A |

### Adding AutomationIds

```xml
<!-- In XAML -->
<Button Content="Synthesize"
        AutomationProperties.AutomationId="VoiceSynthesis.Button.Synthesize"
        AutomationProperties.Name="Synthesize voice" />
```

## CI Integration

### GitHub Actions Workflow

```yaml
# .github/workflows/ci.yml
ui-tests:
  runs-on: windows-latest
  steps:
    - uses: actions/checkout@v4
    
    - name: Build Application
      run: dotnet build -c Release
    
    - name: Run Smoke Tests
      run: |
        dotnet test src/VoiceStudio.App.Tests/VoiceStudio.App.Tests.csproj `
          --filter "Category=Smoke" `
          --logger "trx;LogFileName=smoke-results.trx"
    
    - name: Start WinAppDriver
      run: Start-Process "C:\Program Files\Windows Application Driver\WinAppDriver.exe"
    
    - name: Run E2E Tests
      run: pytest tests/e2e/ -v --screenshot=on-failure
    
    - name: Upload Screenshots
      if: failure()
      uses: actions/upload-artifact@v4
      with:
        name: test-screenshots
        path: tests/e2e/screenshots/
```

### Parallel Execution

```yaml
strategy:
  matrix:
    test-group: [smoke, synthesis, profiles, settings]
```

## Page Objects

### Location
- C#: `src/VoiceStudio.App.Tests/UI/PageObjects/`
- Python: `tests/e2e/pages/`

### Structure

```
tests/e2e/pages/
├── __init__.py
├── base_page.py
├── main_window.py
├── voice_synthesis.py
├── profiles.py
├── settings.py
├── theme_editor.py
└── profile_editor.py
```

## Running Tests

### Smoke Tests (Local)
```bash
# C# tests
dotnet test --filter "Category=Smoke"

# Python tests
pytest tests/e2e/ -m smoke -v
```

### E2E Tests (Local)
```bash
# Start WinAppDriver first
& "C:\Program Files\Windows Application Driver\WinAppDriver.exe"

# Run tests
pytest tests/e2e/ -v --screenshot=on-failure
```

### Coverage Report
```bash
python scripts/check_automation_coverage.py
```

## Troubleshooting

### WinAppDriver Not Starting
1. Ensure Developer Mode is enabled
2. Run WinAppDriver as Administrator
3. Check port 4723 is available

### Element Not Found
1. Verify AutomationId in UI with Inspect.exe
2. Check element is visible and enabled
3. Add explicit wait before interaction

### Flaky Tests
1. Add retry logic for state changes
2. Increase timeouts for slow operations
3. Use explicit waits instead of Thread.Sleep

## Related Documentation

- [AUTOMATION_ID_REGISTRY.md](AUTOMATION_ID_REGISTRY.md) - All AutomationIds
- [UI_AUTOMATION_SPEC.md](../design/UI_AUTOMATION_SPEC.md) - Technical specification
- [UI_TEST_HOOKS.md](../design/UI_TEST_HOOKS.md) - Test hook implementation
