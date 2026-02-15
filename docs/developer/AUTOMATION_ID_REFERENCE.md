# VoiceStudio Automation ID Reference

This document provides a reference for UI Automation IDs used in VoiceStudio for testing.

## Navigation Elements

The main navigation rail consists of 8 toggle buttons:

| AutomationId | Panel Name | Description |
|--------------|------------|-------------|
| `NavStudio` | Studio | Main voice synthesis workspace |
| `NavProfiles` | Profiles | Voice profile management |
| `NavLibrary` | Library | Audio library and files |
| `NavEffects` | Effects | Effects mixer and audio processing |
| `NavTrain` | Train | Voice model training |
| `NavAnalyze` | Analyze | Audio analysis tools |
| `NavSettings` | Settings | Application settings |
| `NavLogs` | Logs/Diagnostics | Logging and diagnostics |

## Panel Root Elements

Each panel has a root container element:

| AutomationId | Panel |
|--------------|-------|
| `VoiceSynthesisView_Root` | Studio |
| `ProfilesView_Root` | Profiles |
| `LibraryView_Root` | Library |
| `EffectsMixerView_Root` | Effects |
| `TrainingView_Root` | Train |
| `AnalyzeView_Root` | Analyze |
| `SettingsView_Root` | Settings |
| `DiagnosticsView_Root` | Logs/Diagnostics |

## Status Bar Elements

| AutomationId | Description |
|--------------|-------------|
| `StatusBar_ProcessingIndicator` | Processing status indicator |
| `StatusBar_StatusText` | Main status text |
| `StatusBar_JobStatusText` | Job status text |
| `StatusBar_JobProgressBar` | Job progress bar |

## Panel-Specific Elements

### Profiles Panel

| AutomationId | Type | Description |
|--------------|------|-------------|
| `ProfilesView_CreateButton` | Button | Create new profile |
| `ProfilesView_ProfileList` | List | Profile list container |
| `ProfilesView_FilterComboBox` | ComboBox | Filter dropdown |
| `ProfilesView_SearchBox` | TextBox | Search input |

### Voice Synthesis Panel (Studio)

| AutomationId | Type | Description |
|--------------|------|-------------|
| `VoiceSynthesisView_SynthesizeButton` | Button | Synthesize voice |
| `VoiceSynthesisView_TextInput` | TextBox | Text to synthesize |
| `VoiceSynthesisView_RefreshButton` | Button | Refresh profiles |

### Effects Panel

| AutomationId | Type | Description |
|--------------|------|-------------|
| `EffectsMixerView_MasterVolumeSlider` | Slider | Master volume control |
| `EffectsMixerView_ResetMixerButton` | Button | Reset mixer |

### Settings Panel

| AutomationId | Type | Description |
|--------------|------|-------------|
| `SettingsView_CategoriesList` | List | Settings categories |

### Library Panel

| AutomationId | Type | Description |
|--------------|------|-------------|
| `LibraryView_SearchBox` | TextBox | Search library |

## Using in Tests

### Python (WinAppDriverSession)

```python
# Find by automation ID
element = driver.find_element("accessibility id", "NavProfiles")
element.click()

# Find panel root
panel = driver.find_element("accessibility id", "ProfilesView_Root")
assert panel is not None
```

### C# (FlaUI or WinAppDriver)

```csharp
// Find by automation ID
var element = session.FindElementByAccessibilityId("NavProfiles");
element.Click();
```

## Discovery Tool

To discover all automation IDs in the running application:

```powershell
# Ensure WinAppDriver is running
python scripts/discover_automation_ids.py
```

This generates:
- `docs/developer/AUTOMATION_ID_MAP.json` - Machine-readable mapping
- `docs/developer/AUTOMATION_ID_REFERENCE.md` - This document (updated)

## Naming Conventions

| Pattern | Example | Description |
|---------|---------|-------------|
| `Nav{Panel}` | `NavStudio` | Navigation button |
| `{Panel}View_Root` | `ProfilesView_Root` | Panel container |
| `{Panel}View_{Element}` | `ProfilesView_CreateButton` | Panel element |
| `StatusBar_{Element}` | `StatusBar_StatusText` | Status bar element |

## Adding New Automation IDs

When adding new UI elements that need testing:

1. Add `AutomationProperties.AutomationId` in XAML:
   ```xml
   <Button x:Name="MyButton"
           AutomationProperties.AutomationId="PanelName_MyButton"
           ... />
   ```

2. Follow naming conventions above

3. Run discovery tool to update documentation

4. Add tests using the new ID

## Troubleshooting

### Element Not Found

1. Run discovery tool to verify ID exists
2. Check if element is off-screen or collapsed
3. Verify spelling matches XAML exactly
4. Use `driver.find_elements()` to check multiple matches

### WinAppDriver Connection Issues

1. Ensure WinAppDriver is running: `C:\Program Files (x86)\Windows Application Driver\WinAppDriver.exe`
2. Enable Developer Mode in Windows Settings
3. Check firewall isn't blocking port 4723

---

**Generated:** 2026-02-09
**Discovery Tool:** `scripts/discover_automation_ids.py`
