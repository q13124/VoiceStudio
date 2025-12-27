# Original UI Script - VoiceStudio Quantum+
## Original ChatGPT + User Collaboration - Complete UI Specification

**Status:** ✅ PRESERVED - Original ChatGPT/User Collaboration  
**Date Created:** 2025 (Original collaboration with ChatGPT)  
**Purpose:** Original UI specification script that must never be lost  
**Critical:** This is the foundation document for all UI work

---

## 📋 IMPORTANCE

**This document contains the original UI specification script that was collaboratively created with ChatGPT. This is the source of truth for the exact UI design and must be preserved.**

**All UI work must reference this document to ensure consistency with the original vision.**

---

## 🎯 ORIGINAL UI VISION

This document preserves the original UI specification that was created through collaboration with ChatGPT. It defines:

1. **Complete MainWindow Structure** - Exact 3-row grid layout
2. **PanelHost System** - Mandatory panel container system
3. **6 Core Panels** - Profiles, Timeline, EffectsMixer, Analyzer, Macro, Diagnostics
4. **Design Tokens** - Complete VSQ.* design token system
5. **File Structure** - Canonical file organization
6. **Panel Registry** - Panel management system
7. **Complete XAML Code** - Full implementation code

---

## 📄 ORIGINAL SPECIFICATION DOCUMENT

**The complete original UI specification is preserved in:**
- **`docs/design/VOICESTUDIO_COMPLETE_IMPLEMENTATION_SPEC.md`** - Complete original specification with full XAML code
- **`docs/design/UI_IMPLEMENTATION_SPEC.md`** - Detailed UI implementation specification

**These documents contain:**
- ✅ Complete MainWindow.xaml structure (3-row grid, 4 PanelHosts, Nav rail, Command toolbar, Status bar)
- ✅ Complete PanelHost.xaml control specification
- ✅ Complete XAML code for all 6 core panels (ProfilesView, TimelineView, EffectsMixer, AnalyzerView, MacroView, DiagnosticsView)
- ✅ Complete DesignTokens.xaml specification (all VSQ.* resources)
- ✅ Complete Panel Registry system (PanelRegion enum, IPanelView interface, PanelDescriptor, PanelRegistry)
- ✅ Complete file structure specification
- ✅ Complete MCP integration hooks
- ✅ Complete plugin system architecture
- ✅ Complete backend client interface

---

## 🚨 CRITICAL RULES FROM ORIGINAL SCRIPT

**These rules were established in the original ChatGPT collaboration and must NEVER be violated:**

### 1. Layout Structure (NON-NEGOTIABLE)
```
✅ MUST maintain 3-row grid structure:
   - Row 0: Top Command Deck (MenuBar + 48px Toolbar)
   - Row 1: Main Workspace (4 Columns: Nav 64px + Left 20% + Center 55% + Right 25%)
            + 2 Rows: Main (*) + Bottom Deck (18%)
   - Row 2: Status Bar (26px)

✅ MUST have 4 PanelHosts:
   - LeftPanelHost (Row 0, Column 1)
   - CenterPanelHost (Row 0, Column 2)
   - RightPanelHost (Row 0, Column 3)
   - BottomPanelHost (Row 1, spans Columns 0-3)

✅ MUST have Nav Rail (64px width, 8 toggle buttons)
```

### 2. MVVM Separation (NON-NEGOTIABLE)
```
✅ MUST have separate files for every panel:
   - PanelNameView.xaml
   - PanelNameView.xaml.cs
   - PanelNameViewModel.cs (implements IPanelView)

❌ NEVER merge View and ViewModel files
❌ NEVER combine .xaml + .xaml.cs + ViewModel.cs into single file
```

### 3. PanelHost Control (NON-NEGOTIABLE)
```
✅ MUST use PanelHost UserControl for all panels
✅ MUST maintain PanelHost structure (header 32px + content area)

❌ NEVER replace PanelHost with raw Grid
❌ NEVER inline panel content directly in MainWindow
```

### 4. Design Tokens (NON-NEGOTIABLE)
```
✅ MUST use VSQ.* resources from DesignTokens.xaml
✅ MUST reference design tokens for ALL styling

❌ NEVER hardcode colors, fonts, or spacing
❌ NEVER create new color schemes
```

### 5. Professional Complexity (NON-NEGOTIABLE)
```
✅ MUST maintain professional DAW-grade complexity
✅ MUST keep all 6 core panels
✅ MUST preserve all placeholder regions
✅ MUST maintain file structure complexity

❌ NEVER simplify "for clarity"
❌ NEVER reduce panel count
❌ NEVER remove placeholder areas
```

---

## 📋 ORIGINAL MAINWINDOW STRUCTURE

**From the original ChatGPT specification:**

```xml
<Window
    x:Class="VoiceStudio.App.MainWindow"
    Width="1600"
    Height="900"
    Title="VoiceStudio Quantum+"
    Background="{StaticResource VSQ.Window.Background}">

  <Grid>
    <Grid.RowDefinitions>
      <RowDefinition Height="Auto"/>   <!-- Top Command Deck -->
      <RowDefinition Height="*"/>       <!-- Main Workspace -->
      <RowDefinition Height="Auto"/>   <!-- Status Bar -->
    </Grid.RowDefinitions>

    <!-- TOP COMMAND DECK (MENU + TOOLBAR) -->
    <Grid Grid.Row="0">
      <Grid.RowDefinitions>
        <RowDefinition Height="Auto"/>   <!-- MenuBar -->
        <RowDefinition Height="48"/>     <!-- Command Toolbar -->
      </Grid.RowDefinitions>

      <!-- MenuBar: File, Edit, View, Modules, Playback, Tools, AI, Help -->
      <!-- Command Toolbar: Transport, Project, Engine, Performance HUD -->
    </Grid>

    <!-- MAIN WORKSPACE (NAV + 3 HOSTS + BOTTOM HOST) -->
    <Grid Grid.Row="1">
      <Grid.RowDefinitions>
        <RowDefinition Height="*"/>        <!-- Top band -->
        <RowDefinition Height="0.18*"/>    <!-- Bottom deck -->
      </Grid.RowDefinitions>

      <Grid.ColumnDefinitions>
        <ColumnDefinition Width="64"/>     <!-- Nav rail -->
        <ColumnDefinition Width="0.20*"/>  <!-- Left dock -->
        <ColumnDefinition Width="0.55*"/>  <!-- Center -->
        <ColumnDefinition Width="0.25*"/>  <!-- Right dock -->
      </Grid.ColumnDefinitions>

      <!-- Nav rail: 8 toggle buttons (Studio, Profiles, Library, Effects, Train, Analyze, Settings, Logs) -->
      <!-- LeftPanelHost (Row 0, Column 1) -->
      <!-- CenterPanelHost (Row 0, Column 2) -->
      <!-- RightPanelHost (Row 0, Column 3) -->
      <!-- BottomPanelHost (Row 1, spans Columns 0-3) -->
    </Grid>

    <!-- STATUS BAR -->
    <Border Grid.Row="2" Height="26">
      <!-- Status text, Job progress, Mini meters (CPU, GPU, RAM) + Clock -->
    </Border>
  </Grid>
</Window>
```

**Full specification:** See `VOICESTUDIO_COMPLETE_IMPLEMENTATION_SPEC.md` for complete MainWindow.xaml code.

---

## 📋 ORIGINAL PANELHOST STRUCTURE

**From the original ChatGPT specification:**

```xml
<UserControl x:Class="VoiceStudio.App.Controls.PanelHost">
  <Grid>
    <Grid.RowDefinitions>
      <RowDefinition Height="32"/> <!-- Header -->
      <RowDefinition Height="*"/>   <!-- Body -->
    </Grid.RowDefinitions>

    <!-- Header bar: Icon + Title + Action Buttons -->
    <Border Grid.Row="0" Background="#181D26" CornerRadius="8,8,0,0">
      <!-- Icon, Title, Pop-out, Collapse, Options -->
    </Border>

    <!-- Body: ContentPresenter in Border -->
    <Border Grid.Row="1" CornerRadius="0,0,8,8" 
            Background="{StaticResource VSQ.Panel.BackgroundBrush}"
            BorderBrush="{StaticResource VSQ.Panel.BorderBrush}">
      <ContentPresenter Content="{Binding Content, ...}"/>
    </Border>
  </Grid>
</UserControl>
```

**Full specification:** See `VOICESTUDIO_COMPLETE_IMPLEMENTATION_SPEC.md` for complete PanelHost.xaml code.

---

## 📋 ORIGINAL DESIGN TOKENS

**From the original ChatGPT specification:**

```xml
<!-- Base colors -->
<Color x:Key="VSQ.Background.Darker">#FF0A0F15</Color>
<Color x:Key="VSQ.Background.Dark">#FF121A24</Color>
<Color x:Key="VSQ.Accent.Cyan">#FF00B7C2</Color>
<Color x:Key="VSQ.Accent.Lime">#FF9AFF33</Color>
<Color x:Key="VSQ.Accent.Magenta">#FFB040FF</Color>
<Color x:Key="VSQ.Text.Primary">#FFCDD9E5</Color>
<Color x:Key="VSQ.Text.Secondary">#FF8A9BB3</Color>

<!-- Brushes -->
<LinearGradientBrush x:Key="VSQ.Window.Background" .../>
<SolidColorBrush x:Key="VSQ.Text.PrimaryBrush" .../>
<SolidColorBrush x:Key="VSQ.Panel.BackgroundBrush" Color="#151921" />

<!-- Typography -->
<x:Double x:Key="VSQ.FontSize.Caption">10</x:Double>
<x:Double x:Key="VSQ.FontSize.Body">12</x:Double>
<x:Double x:Key="VSQ.FontSize.Title">16</x:Double>
<x:Double x:Key="VSQ.FontSize.Heading">20</x:Double>

<!-- Constants -->
<x:Double x:Key="VSQ.CornerRadius.Panel">8</x:Double>
<x:Double x:Key="VSQ.CornerRadius.Button">4</x:Double>
<x:Double x:Key="VSQ.Animation.Duration.Fast">100</x:Double>
<x:Double x:Key="VSQ.Animation.Duration.Medium">150</x:Double>
```

**Full specification:** See `VOICESTUDIO_COMPLETE_IMPLEMENTATION_SPEC.md` for complete DesignTokens.xaml code.

---

## 📋 ORIGINAL 6 CORE PANELS

**From the original ChatGPT specification:**

1. **ProfilesView** - LeftPanelHost default
   - Tabs: Profiles / Library (32px header)
   - Left: Profiles grid (WrapGrid, 180×120 cards)
   - Right: Detail inspector (260px width)

2. **TimelineView** - CenterPanelHost default
   - Toolbar (32px): Add Track, Zoom, Grid settings
   - Tracks area (*): ItemsControl with track templates
   - Visualizer (160px): Spectrogram/visualizer placeholder

3. **EffectsMixerView** - RightPanelHost default
   - Mixer (60%): Horizontal ItemsControl with mixer strips
   - FX Chain (40%): Node view / FX chain placeholder

4. **AnalyzerView** - RightPanelHost alternative
   - Tabs (32px): Waveform, Spectral, Radar, Loudness, Phase
   - Chart area (*): Placeholder for chart rendering

5. **MacroView** - BottomPanelHost default
   - Tabs (32px): Macros / Automation
   - Node graph canvas (*): Placeholder for node-based macro system

6. **DiagnosticsView** - BottomPanelHost alternative
   - Logs (60%): ListView with log entries
   - Metrics charts (40%): CPU, GPU, RAM progress bars

**Full XAML code:** See `VOICESTUDIO_COMPLETE_IMPLEMENTATION_SPEC.md` for complete XAML code for all 6 panels.

---

## 📋 ORIGINAL FILE STRUCTURE

**From the original ChatGPT specification:**

```
VoiceStudio/
├── src/
│   ├── VoiceStudio.App/              # WinUI 3 frontend
│   │   ├── App.xaml                  # Merges DesignTokens.xaml
│   │   ├── MainWindow.xaml          # 3-row grid with 4 PanelHosts
│   │   ├── Resources/
│   │   │   └── DesignTokens.xaml    # All VSQ.* resources
│   │   ├── Controls/
│   │   │   └── PanelHost.xaml        # Reusable panel container
│   │   └── Views/Panels/
│   │       └── [6 core panels, each with .xaml, .xaml.cs, ViewModel.cs]
│   │
│   └── VoiceStudio.Core/             # Shared library
│       └── Panels/
│           └── [Panel registry types]
```

**Full specification:** See `VOICESTUDIO_COMPLETE_IMPLEMENTATION_SPEC.md` for complete file structure.

---

## 📚 REFERENCE DOCUMENTS

### Original Specification Documents
1. **`VOICESTUDIO_COMPLETE_IMPLEMENTATION_SPEC.md`** - **CRITICAL** - Complete original specification with full XAML code (THIS IS THE SOURCE)
2. **`UI_IMPLEMENTATION_SPEC.md`** - Detailed UI implementation specification
3. **`EXECUTION_PLAN.md`** - Original execution plan with Overseer + 8 Workers

### Current Implementation Documents
4. **`MEMORY_BANK.md`** - Memory bank (references original spec)
5. **`OVERSEER_UI_RULES_COMPLETE.md`** - Complete UI rules (enforces original spec)
6. **`MAINWINDOW_STRUCTURE.md`** - MainWindow structure (based on original spec)
7. **`GUARDRAILS.md`** - Guardrails (enforces original rules)

### Worker Documents
8. **`OVERSEER_3_WORKER_PLAN.md`** - 3-worker plan (references original spec)
9. **`WORKER_2_PROMPT_UIUX.md`** - Worker 2 prompt (references original spec)
10. **`OVERSEER_SYSTEM_PROMPT_3_WORKERS.md`** - Overseer prompt (references original spec)

---

## ✅ PRESERVATION STATUS

**✅ ORIGINAL UI SCRIPT PRESERVED:**
- ✅ Complete MainWindow structure preserved in `VOICESTUDIO_COMPLETE_IMPLEMENTATION_SPEC.md`
- ✅ Complete PanelHost structure preserved
- ✅ Complete 6 core panels XAML code preserved
- ✅ Complete DesignTokens.xaml preserved
- ✅ Complete file structure preserved
- ✅ Complete Panel Registry system preserved
- ✅ Original rules and guardrails preserved
- ✅ This document created to ensure original script is never lost

**✅ ACCESSIBILITY:**
- ✅ Referenced in MEMORY_BANK.md
- ✅ Referenced in OVERSEER_UI_RULES_COMPLETE.md
- ✅ Referenced in all worker prompts
- ✅ Referenced in Overseer prompt

---

## 🎯 USAGE

**When working on UI:**
1. **ALWAYS** reference `VOICESTUDIO_COMPLETE_IMPLEMENTATION_SPEC.md` for exact specifications
2. **ALWAYS** reference this document (`ORIGINAL_UI_SCRIPT_CHATGPT.md`) to understand the original vision
3. **ALWAYS** follow the original rules and guardrails established in the original ChatGPT collaboration
4. **NEVER** deviate from the original specification without explicit approval

---

**Last Updated:** 2025-01-27  
**Status:** ✅ PRESERVED - Original UI Script  
**Source:** Original ChatGPT + User Collaboration  
**Critical:** This is the foundation document - must never be lost

