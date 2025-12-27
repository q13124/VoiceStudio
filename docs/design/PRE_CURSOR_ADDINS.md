# Pre-Cursor Launch Optional Add-Ins (Recommended)

These are high-value, low-lift additions that significantly enhance scalability and usability.

---

## 1. 🧱 Modular PanelStack System

**Purpose:** Allow each PanelHost to support multiple panels per region, switchable via tabs or hotkeys.

**Benefits:**
- Macros + Logs can coexist in bottom panel
- Studio + Profiles can coexist in left panel
- Matches FL Studio's Channel Rack or DaVinci's tabbed scopes
- Themeable tab bar
- Adds scalability without clutter
- Cursor-friendly: drop-in control using `ObservableCollection<UserControl>`

**Files:**
- `Controls/PanelStack.xaml`
- `Controls/PanelStack.xaml.cs`
- `ViewModels/PanelStackViewModel.cs`

**Integration:**
- PanelHost can contain either a single panel OR a PanelStack
- PanelStack manages multiple panels with tabs
- Each tab represents a different panel view

---

## 2. 🧭 Command Palette (Ctrl+P)

**Purpose:** Searchable quick action UI like VSCode or Figma.

**Features:**
- Launch via `Ctrl+P`
- Supports actions like:
  - "Analyze Clip"
  - "Jump to Track 3"
  - "Insert Macro → Normalize"
  - "Switch to Profiles Panel"
  - "Open Settings"

**Files:**
- `Controls/CommandPalette.xaml`
- `Controls/CommandPalette.xaml.cs`
- `Services/ICommandRegistry.cs`
- `Services/CommandRegistry.cs`

**Integration:**
- Global keyboard shortcut handler
- Command registry for all actions
- Fuzzy search/filtering
- Category grouping

---

## 3. 🪟 Multi-Window Workspace Support

**Purpose:** Enable panels to pop out as independent windows (optional).

**Benefits:**
- Power users can run Analyzer or Logs on a second screen
- Floating panels for multi-monitor setups
- Maintains panel functionality when floating

**Files:**
- `Controls/FloatingWindowHost.xaml`
- `Services/WindowHostService.cs`

**Integration:**
- PanelHost can be "popped out" to floating window
- Reuses PanelView in floating context
- Window management service handles lifecycle

---

## 4. ⚙️ Per-Panel Settings Registry

**Purpose:** Each panel can optionally define its own right-click settings menu.

**Features:**
- Contextual settings per panel
- Toggles and configuration options
- Centralized settings store

**Files:**
- `Core/Panels/IPanelConfigurable.cs`
- `Services/PanelSettingsStore.cs`
- `Dialogs/PanelSettingsDialog.xaml`

**Integration:**
- Panels implement `IPanelConfigurable` if they have settings
- Right-click on panel header shows settings menu
- Settings persisted per panel type

---

## 5. 🧪 UI Test Coverage Hooks

**Purpose:** Add automation IDs for future testing frameworks.

**Implementation:**
```csharp
#if DEBUG
  AutomationProperties.SetAutomationId(control, "ProfilesView_Header");
#endif
```

**Benefits:**
- Enables Spectron, Appium, or WinAppDriver integration later
- No runtime overhead in release builds
- Makes UI testing feasible

**Files:**
- Add to all panel XAML files
- Add to MainWindow controls
- Document automation ID naming convention

---

## ✅ Minimum to Lock In Before Cursor Starts

**Required:**
- ✅ ThemeManager (already planned)
- ✅ PanelRegistry (already planned)
- ✅ PanelStack (recommended - high value, low effort)

**Optional but Recommended:**
- Command Palette (boosts usability at scale)
- Per-panel settings (very scalable)
- Multi-window support (power user feature)
- UI test hooks (future-proofing)

---

## Implementation Priority

1. **PanelStack** - Highest priority, enables multi-panel regions
2. **Command Palette** - High usability impact
3. **Per-Panel Settings** - Scalability feature
4. **Multi-Window Support** - Power user feature
5. **UI Test Hooks** - Future-proofing (can add incrementally)

