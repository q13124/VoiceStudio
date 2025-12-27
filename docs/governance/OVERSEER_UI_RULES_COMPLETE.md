# Overseer - Complete UI Rules & Windows Native Requirements
## VoiceStudio Quantum+ - Complete Reference for Overseer

**Last Updated:** 2025-01-27  
**Status:** Critical Reference - READ THIS FIRST  
**Purpose:** Complete consolidation of all UI details, rules, and Windows native requirements

---

## 🎯 CRITICAL CONFIRMATION

**✅ YES - This is a Windows Native Program:**
- **Framework:** WinUI 3 (Windows App SDK)
- **Language:** C# (.NET 8)
- **UI Markup:** XAML
- **Platform:** Windows Desktop Application
- **Target:** Windows 10 17763+ / Windows 11
- **Architecture:** Native Windows application, NOT web-based

**❌ NOT:**
- ❌ NOT a web app (no Electron, no browser)
- ❌ NOT a cross-platform framework (WinUI 3 is Windows-only)
- ❌ NOT a hybrid app (fully native Windows)

---

## 🚨 NON-NEGOTIABLE GUARDRAILS (ABSOLUTE RULES)

### Rule 1: Layout Complexity - DO NOT SIMPLIFY
```
❌ DO NOT reduce 3-column + nav + bottom deck layout
❌ DO NOT remove any PanelHost controls
❌ DO NOT collapse panels into single views
✅ MUST maintain MainWindow 3-Row Grid structure
✅ MUST have 4 PanelHosts: Left, Center, Right, Bottom
✅ MUST have 64px Nav Rail (8 toggle buttons)
✅ MUST have 48px Command Toolbar
✅ MUST have 26px Status Bar
```

### Rule 2: MVVM Separation - DO NOT MERGE
```
❌ DO NOT merge View and ViewModel files
❌ DO NOT combine .xaml + .xaml.cs + ViewModel.cs
✅ MUST have separate files for every panel:
   - PanelNameView.xaml
   - PanelNameView.xaml.cs
   - PanelNameViewModel.cs (implements IPanelView)
```

### Rule 3: PanelHost Control - DO NOT REPLACE
```
❌ DO NOT replace PanelHost with raw Grid
❌ DO NOT inline panel content in MainWindow
✅ MUST use PanelHost UserControl for all panels
✅ MUST maintain PanelHost structure (header + content)
```

### Rule 4: Design Tokens - DO NOT HARDCODE
```
❌ DO NOT use hardcoded colors, fonts, or spacing
❌ DO NOT create new color schemes
✅ MUST use VSQ.* resources from DesignTokens.xaml
✅ MUST reference design tokens for ALL styling
```

### Rule 5: Professional Complexity - REQUIRED
```
❌ DO NOT simplify "for clarity"
❌ DO NOT reduce panel count
❌ DO NOT remove placeholder areas
✅ MUST maintain Adobe/FL Studio level complexity
✅ MUST keep all 6 core panels
✅ MUST preserve all placeholder regions
```

---

## 🏗️ MAINWINDOW STRUCTURE (CANONICAL - NEVER CHANGE)

### Structure (3-Row Grid)

```
MainWindow.xaml
└── Grid (3 Rows)
    ├── Row 0: Top Command Deck (Auto height)
    │   ├── MenuBar
    │   │   └── MenuItems: File, Edit, View, Modules, Playback, Tools, AI, Help
    │   └── Command Toolbar (48px height)
    │       ├── Column 0: Transport (Play, Pause, Stop, Record, Loop)
    │       ├── Column 1: Project name + Engine selector
    │       ├── Column 2: Undo/Redo + Workspace dropdown
    │       └── Column 3: Performance HUD (CPU, GPU, Latency bars)
    │
    ├── Row 1: Main Workspace (*)
    │   └── Grid (4 Columns, 2 Rows)
    │       ├── Column 0: Nav Rail (64px width)
    │       │   └── Vertical Stack: 8 toggle buttons
    │       │       ├── Studio
    │       │       ├── Profiles
    │       │       ├── Library
    │       │       ├── Effects
    │       │       ├── Train
    │       │       ├── Analyze
    │       │       ├── Settings
    │       │       └── Logs
    │       │
    │       ├── Row 0, Column 1: LeftPanelHost (20% width)
    │       │   └── Default: ProfilesView
    │       │
    │       ├── Row 0, Column 2: CenterPanelHost (55% width)
    │       │   └── Default: TimelineView
    │       │
    │       ├── Row 0, Column 3: RightPanelHost (25% width)
    │       │   └── Default: EffectsMixerView
    │       │
    │       └── Row 1, Columns 0-3: BottomPanelHost (18% height, spans all)
    │           └── Default: MacroView
    │
    └── Row 2: Status Bar (26px height, Auto)
        └── Grid (3 Columns)
            ├── Column 0 (*): Status text ("Ready")
            ├── Column 1 (2*): Job progress (Job name + progress bar)
            └── Column 2 (*): Mini meters (CPU, GPU, RAM) + Clock
```

### Critical Dimensions

- **Window Default:** 1600×900
- **Nav Rail:** 64px width (fixed)
- **Command Toolbar:** 48px height (fixed)
- **Status Bar:** 26px height (fixed)
- **Left Panel:** 20% width (resizable)
- **Center Panel:** 55% width (resizable)
- **Right Panel:** 25% width (resizable)
- **Bottom Panel:** 18% height (resizable)

### PanelHost Structure (MANDATORY)

Each PanelHost MUST have:
- **Header Bar:** 32px height
  - Icon (Segoe MDL2 glyph)
  - Title text
  - Pop-out button (stub)
  - Collapse button
  - Options button (MenuFlyout)
- **Body:** ContentPresenter with Border
  - CornerRadius: 8px (VSQ.CornerRadius.Panel)
  - BorderBrush: VSQ.Panel.BorderBrush
  - BorderThickness: 1px

---

## 🎨 DESIGN TOKENS (DesignTokens.xaml)

### Critical Resources - MUST USE

#### Colors (VSQ.*)
```
VSQ.Background.Darker: #FF0A0F15
VSQ.Background.Dark: #FF121A24
VSQ.Accent.Cyan: #FF00B7C2
VSQ.Accent.Lime: #FF9AFF33
VSQ.Accent.Magenta: #FFB040FF
VSQ.Text.Primary: #FFCDD9E5
VSQ.Text.Secondary: #FF8A9BB3
VSQ.Border.Subtle: #26FFFFFF
VSQ.Warn: #FFFFB540
VSQ.Error: #FFFF4060
```

#### Brushes (VSQ.*Brush)
```
VSQ.Window.Background: LinearGradientBrush (Dark → Darker)
VSQ.Text.PrimaryBrush: SolidColorBrush
VSQ.Text.SecondaryBrush: SolidColorBrush
VSQ.Accent.CyanBrush: SolidColorBrush
VSQ.Panel.BackgroundBrush: SolidColorBrush
VSQ.Panel.BorderBrush: SolidColorBrush
```

#### Typography (VSQ.Font.*)
```
VSQ.Font.Caption: 10
VSQ.Font.Body: 12
VSQ.Font.Title: 16
VSQ.Font.Heading: 20
```

#### Styles (VSQ.Text.*)
```
VSQ.Text.Body: FontSize=12, Foreground=Primary
VSQ.Text.Caption: FontSize=10, Foreground=Secondary
VSQ.Text.Title: FontSize=16, Foreground=Primary, SemiBold
VSQ.Text.Heading: FontSize=20, Foreground=Primary, Bold
```

#### Constants (VSQ.*)
```
VSQ.CornerRadius.Panel: 8
VSQ.CornerRadius.Button: 4
VSQ.Animation.Duration.Fast: 100ms
VSQ.Animation.Duration.Medium: 150ms
```

#### Button Styles (VSQ.Button.*)
```
VSQ.Button.Style: Standard button
VSQ.Button.Icon: Icon button variant
VSQ.Button.NavToggle: Toggle button for navigation (active: cyan accent)
```

**Rule:** ALL styling MUST use these tokens. NO hardcoded values allowed.

---

## 📋 CORE PANELS (6 REQUIRED)

### 1. ProfilesView
- **Location:** `src/VoiceStudio.App/Views/Panels/ProfilesView.xaml`
- **ViewModel:** `ProfilesViewModel.cs` (implements IPanelView)
- **Default Region:** LeftPanelHost
- **Structure:**
  - Tabs: Profiles / Library (32px header)
  - Left: Profiles grid (WrapGrid, 180×120 cards)
  - Right: Detail inspector (260px width)

### 2. TimelineView
- **Location:** `src/VoiceStudio.App/Views/Panels/TimelineView.xaml`
- **ViewModel:** `TimelineViewModel.cs` (implements IPanelView)
- **Default Region:** CenterPanelHost
- **Structure:**
  - Toolbar (32px): Add Track, Zoom, Grid settings
  - Tracks area (*): ItemsControl with track templates
  - Visualizer (160px): Spectrogram/visualizer placeholder

### 3. EffectsMixerView
- **Location:** `src/VoiceStudio.App/Views/Panels/EffectsMixerView.xaml`
- **ViewModel:** `EffectsMixerViewModel.cs` (implements IPanelView)
- **Default Region:** RightPanelHost
- **Structure:**
  - Mixer (60%): Horizontal ItemsControl with mixer strips
  - FX Chain (40%): Node view / FX chain placeholder

### 4. AnalyzerView
- **Location:** `src/VoiceStudio.App/Views/Panels/AnalyzerView.xaml`
- **ViewModel:** `AnalyzerViewModel.cs` (implements IPanelView)
- **Alternative Region:** RightPanelHost
- **Structure:**
  - Tabs (32px): Waveform, Spectral, Radar, Loudness, Phase
  - Chart area (*): Placeholder for chart rendering

### 5. MacroView
- **Location:** `src/VoiceStudio.App/Views/Panels/MacroView.xaml`
- **ViewModel:** `MacroViewModel.cs` (implements IPanelView)
- **Default Region:** BottomPanelHost
- **Structure:**
  - Tabs (32px): Macros / Automation
  - Node graph canvas (*): Placeholder for node-based macro system

### 6. DiagnosticsView
- **Location:** `src/VoiceStudio.App/Views/Panels/DiagnosticsView.xaml`
- **ViewModel:** `DiagnosticsViewModel.cs` (implements IPanelView)
- **Alternative Region:** BottomPanelHost
- **Structure:**
  - Logs (60%): ListView with log entries
  - Metrics charts (40%): CPU, GPU, RAM progress bars

**Each panel MUST have:**
- Separate `.xaml` file
- Separate `.xaml.cs` file
- Separate `ViewModel.cs` file
- Implements `IPanelView` interface

---

## 📁 FILE STRUCTURE (CANONICAL - NEVER CHANGE)

```
src/
├── VoiceStudio.App/              # WinUI 3 frontend
│   ├── App.xaml                  # Merges DesignTokens.xaml
│   ├── App.xaml.cs               # Application entry point
│   ├── MainWindow.xaml           # 3-row grid with 4 PanelHosts
│   ├── MainWindow.xaml.cs        # Window code-behind
│   │
│   ├── Resources/
│   │   └── DesignTokens.xaml     # ALL VSQ.* resources
│   │
│   ├── Controls/
│   │   ├── PanelHost.xaml        # Reusable panel container
│   │   ├── PanelHost.xaml.cs     # PanelHost code-behind
│   │   ├── NavIconButton.xaml    # Navigation button control
│   │   └── NavIconButton.xaml.cs # NavIconButton code-behind
│   │
│   ├── Views/
│   │   ├── Shell/
│   │   │   ├── StatusBarView.xaml
│   │   │   ├── StatusBarView.xaml.cs
│   │   │   ├── StatusBarViewModel.cs
│   │   │   ├── NavigationView.xaml
│   │   │   ├── NavigationView.xaml.cs
│   │   │   └── NavigationViewModel.cs
│   │   │
│   │   └── Panels/
│   │       ├── ProfilesView.xaml
│   │       ├── ProfilesView.xaml.cs
│   │       ├── ProfilesViewModel.cs
│   │       ├── TimelineView.xaml
│   │       ├── TimelineView.xaml.cs
│   │       ├── TimelineViewModel.cs
│   │       ├── EffectsMixerView.xaml
│   │       ├── EffectsMixerView.xaml.cs
│   │       ├── EffectsMixerViewModel.cs
│   │       ├── AnalyzerView.xaml
│   │       ├── AnalyzerView.xaml.cs
│   │       ├── AnalyzerViewModel.cs
│   │       ├── MacroView.xaml
│   │       ├── MacroView.xaml.cs
│   │       ├── MacroViewModel.cs
│   │       ├── DiagnosticsView.xaml
│   │       ├── DiagnosticsView.xaml.cs
│   │       └── DiagnosticsViewModel.cs
│   │
│   ├── ViewModels/
│   │   └── BaseViewModel.cs      # Base view model class
│   │
│   └── Services/
│       ├── BackendClient.cs      # Backend API client
│       ├── AudioPlayerService.cs # Audio playback service
│       └── ServiceProvider.cs    # DI container
│
└── VoiceStudio.Core/             # Shared core library
    ├── Panels/
    │   ├── IPanelView.cs         # Panel interface
    │   ├── PanelRegion.cs        # Enum (Left, Center, Right, Bottom, Floating)
    │   ├── PanelDescriptor.cs    # Panel metadata
    │   ├── IPanelRegistry.cs     # Registry interface
    │   └── PanelRegistry.cs      # Registry implementation
    │
    ├── Models/
    │   ├── VoiceProfile.cs       # Voice profile model
    │   ├── AudioClip.cs          # Audio clip model
    │   └── MeterReading.cs       # Performance metrics model
    │
    └── Services/
        └── IBackendClient.cs     # Backend client interface
```

**Rule:** This structure is CANONICAL. Do NOT merge, collapse, or reorganize files.

---

## 🖥️ WINDOWS NATIVE REQUIREMENTS

### Technology Stack (CONFIRMED)
- **Framework:** WinUI 3 (Windows App SDK 1.5.0)
- **Language:** C# (.NET 8.0)
- **UI Markup:** XAML
- **Platform:** Windows Desktop (Windows 10 17763+ / Windows 11)
- **Architecture:** Native Windows application

### Dependencies (NATIVE WINDOWS ONLY)

#### .NET / WinUI 3 Packages
```xml
<PackageReference Include="Microsoft.WindowsAppSDK" Version="1.5.240627000" />
<PackageReference Include="Microsoft.Windows.SDK.BuildTools" Version="10.0.26100.0" />
<PackageReference Include="CommunityToolkit.WinUI.UI.Controls" Version="8.1.2409" />
<PackageReference Include="CommunityToolkit.Mvvm" Version="8.3.2" />
<PackageReference Include="NAudio" Version="2.2.1" />
<PackageReference Include="Win2D.WinUI" Version="1.1.0" />
```

#### Windows-Specific Features
- **Win2D:** Native Windows 2D graphics (waveforms, spectrograms)
- **NAudio:** Native Windows audio I/O (WASAPI)
- **WinUI 3 Controls:** Native Windows controls (MenuBar, Grid, etc.)
- **Windows App SDK:** Native Windows APIs

### Native Windows Features Used
- ✅ Native Windows windowing system
- ✅ Native Windows controls (Button, Grid, MenuBar, etc.)
- ✅ Native Windows audio (WASAPI via NAudio)
- ✅ Native Windows 2D graphics (Win2D)
- ✅ Native Windows file system access
- ✅ Native Windows notification system

### NOT Web-Based
- ❌ NO Electron
- ❌ NO web views
- ❌ NO browser engines
- ❌ NO JavaScript/HTML
- ❌ NO cross-platform frameworks

---

## 🚨 VIOLATION DETECTION PATTERNS

### Detection Patterns
```
If you see ANY of these, STOP and REVERT immediately:

1. ❌ Merged View/ViewModel files
   → REVERT: Must be separate files

2. ❌ PanelHost replaced with Grid
   → REVERT: PanelHost is mandatory

3. ❌ Reduced panel count
   → REVERT: All 6 panels required

4. ❌ Hardcoded colors (Background="#FF0000")
   → REVERT: Use VSQ.* design tokens

5. ❌ Simplified layout (removed columns/rows)
   → REVERT: Maintain 3-column + nav + bottom deck

6. ❌ Removed placeholder areas
   → REVERT: Placeholders are required

7. ❌ Web-based technologies mentioned
   → REVERT: This is Windows native only
```

### Remediation Command
```
STOP. Detected violation: [specific violation]

This is a Windows native WinUI 3 application. Requirements:
1. Must use WinUI 3 controls (NOT web controls)
2. Must maintain MainWindow 3-row grid structure
3. Must use PanelHost for all panels
4. Must use VSQ.* design tokens only
5. Must maintain MVVM separation (separate files)

Revert changes immediately and restore:
- [List specific files to restore]
- [List specific structures to restore]

Then proceed according to specifications in:
- MEMORY_BANK.md
- UI_IMPLEMENTATION_SPEC.md
- MAINWINDOW_STRUCTURE.md
```

---

## ✅ VERIFICATION CHECKLIST

### Before Approving Any Work

#### Windows Native Verification
- [ ] Uses WinUI 3 controls (NOT web controls)
- [ ] Uses C# / XAML (NOT JavaScript/HTML)
- [ ] Targets Windows platform (NOT cross-platform)
- [ ] Uses Windows-native packages only

#### Layout Verification
- [ ] MainWindow uses 3-row grid
- [ ] Workspace has 4 columns (nav + left + center + right)
- [ ] Workspace has 2 rows (main + bottom)
- [ ] All 4 PanelHosts exist and are used
- [ ] Nav Rail is 64px width
- [ ] Command Toolbar is 48px height
- [ ] Status Bar is 26px height

#### MVVM Verification
- [ ] All panels have separate .xaml files
- [ ] All panels have separate .xaml.cs files
- [ ] All panels have separate ViewModel.cs files
- [ ] No View/ViewModel files merged
- [ ] All ViewModels implement IPanelView

#### Design Token Verification
- [ ] All colors use VSQ.* resources
- [ ] All typography uses VSQ.Text.* styles
- [ ] All buttons use VSQ.Button.* styles
- [ ] No hardcoded values
- [ ] DesignTokens.xaml is referenced in App.xaml

#### PanelHost Verification
- [ ] PanelHost used for all panels (NOT raw Grid)
- [ ] PanelHost has header bar (32px)
- [ ] PanelHost has content area
- [ ] PanelHost uses design tokens

#### Complexity Verification
- [ ] Layout complexity maintained
- [ ] All 6 panels exist
- [ ] All placeholder regions visible
- [ ] No simplifications detected

---

## 📚 KEY DOCUMENT REFERENCES

### Original UI Specification (CRITICAL - SOURCE OF TRUTH)
1. **[ORIGINAL_UI_SCRIPT_CHATGPT.md](../design/ORIGINAL_UI_SCRIPT_CHATGPT.md)** - **CRITICAL** - Original ChatGPT/User UI script - **THIS IS THE SOURCE OF TRUTH**
2. **[VOICESTUDIO_COMPLETE_IMPLEMENTATION_SPEC.md](../design/VOICESTUDIO_COMPLETE_IMPLEMENTATION_SPEC.md)** - **CRITICAL** - Complete original specification with full XAML code (source document)

### Critical Documents (MUST READ)
3. **[MEMORY_BANK.md](../design/MEMORY_BANK.md)** - Core specifications (references original script)
4. **[UI_IMPLEMENTATION_SPEC.md](../design/UI_IMPLEMENTATION_SPEC.md)** - Complete UI spec
5. **[MAINWINDOW_STRUCTURE.md](../design/MAINWINDOW_STRUCTURE.md)** - MainWindow structure (based on original spec)
6. **[GUARDRAILS.md](../design/GUARDRAILS.md)** - Critical guardrails (enforces original rules)
7. **[GLOBAL_GUARDRAILS.md](../design/GLOBAL_GUARDRAILS.md)** - Global guardrails
8. **[TECHNICAL_STACK_SPECIFICATION.md](../design/TECHNICAL_STACK_SPECIFICATION.md)** - Tech stack (Windows native)

### Architecture Documents
7. **[VoiceStudio-Architecture.md](../design/VoiceStudio-Architecture.md)** - Architecture reference
8. **[TECHNICAL_STACK_SPECIFICATION.md](../design/TECHNICAL_STACK_SPECIFICATION.md)** - Windows native stack

---

## 🎯 OVERSEER PRIORITIES

### Priority 1: Preserve Windows Native Architecture
- ✅ Ensure WinUI 3 is used (NOT web technologies)
- ✅ Ensure Windows-native packages only
- ✅ Ensure native Windows controls
- ✅ Reject any web-based solutions

### Priority 2: Enforce UI Guardrails
- ✅ Prevent layout simplification
- ✅ Prevent file merging
- ✅ Prevent PanelHost replacement
- ✅ Prevent hardcoded values

### Priority 3: Maintain Professional Complexity
- ✅ Preserve all 6 panels
- ✅ Preserve all placeholder regions
- ✅ Maintain layout structure
- ✅ Maintain file structure

---

## ✅ CONFIRMATION

**As Overseer, I confirm:**

✅ **Windows Native Program:** Yes - WinUI 3 (.NET 8, C#/XAML)  
✅ **All UI Details:** Yes - Complete specifications in UI_IMPLEMENTATION_SPEC.md  
✅ **All Rules & Demands:** Yes - Complete guardrails in MEMORY_BANK.md, GUARDRAILS.md, GLOBAL_GUARDRAILS.md  
✅ **MainWindow Structure:** Yes - Complete structure in MAINWINDOW_STRUCTURE.md  
✅ **Design Tokens:** Yes - Complete tokens in DesignTokens.xaml  
✅ **File Structure:** Yes - Complete structure defined in multiple docs  
✅ **Panel System:** Yes - Complete panel specifications  
✅ **Windows Requirements:** Yes - Complete Windows native requirements  

**All specifications, rules, and Windows native requirements are documented and will be enforced.**

---

**Last Updated:** 2025-01-27  
**Status:** Complete Reference  
**Overseer:** Confirmed

