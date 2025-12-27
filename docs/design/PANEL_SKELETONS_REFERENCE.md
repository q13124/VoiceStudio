# Panel XAML Skeletons Reference

This document provides the exact XAML skeletons for all 6 core panels. These must be implemented exactly as specified.

## 7.1 ProfilesView.xaml

**Location:** `src/VoiceStudio.App/Views/Panels/ProfilesView.xaml`

**Structure:**
- 2-row grid: Tabs (32px) + Content (*)
- Tabs: ToggleButtons for Profiles/Library
- Content: 2-column grid
  - Left: ScrollViewer with WrapGrid (180×120 profile cards)
  - Right: Detail inspector (260px width)

**Key Elements:**
- WrapGrid with ItemWidth="180" ItemHeight="120"
- Profile card template with Rectangle (40px height), TextBlocks
- Detail panel with Rectangle (60px height) and info TextBlocks

## 7.2 TimelineView.xaml

**Location:** `src/VoiceStudio.App/Views/Panels/TimelineView.xaml`

**Structure:**
- 3-row grid: Toolbar (32px) + Tracks (*) + Visualizer (160px)
- Toolbar: Add Track, Zoom In, Zoom Out, Grid indicator
- Tracks: ItemsControl with track template
  - Track header (180px): Background #20252E
  - Timeline lane (48px height): Background #151921, waveform placeholder
- Visualizer: Border with placeholder text

**Key Elements:**
- Track template with 2-column grid
- Waveform placeholder in Border
- Spectrogram/visualizer placeholder at bottom

## 7.3 EffectsMixerView.xaml

**Location:** `src/VoiceStudio.App/Views/Panels/EffectsMixerView.xaml`

**Structure:**
- 2-row grid: Mixer (*) + FX Chain (0.4*)
- Mixer: Horizontal ScrollViewer with ItemsControl
  - Mixer strips (80px width)
  - Fader placeholder (140px height, 20×60 Rectangle)
  - FX inserts list (EQ, Comp, Reverb)
- FX Chain: Border with placeholder text

**Key Elements:**
- StackPanel Orientation="Horizontal" for mixer strips
- Fader uses VSQ.Accent.CyanBrush
- FX Chain placeholder at bottom

## 7.4 AnalyzerView.xaml

**Location:** `src/VoiceStudio.App/Views/Panels/AnalyzerView.xaml`

**Structure:**
- 2-row grid: Tabs (32px) + Chart area (*)
- Tabs: TabView with 5 tabs (Waveform, Spectral, Radar, Loudness, Phase)
- Chart: Border with placeholder text (opacity 0.6)

**Key Elements:**
- TabView (WinUI 3) - Note: Specification shows TabControl (WPF), but use TabView for WinUI 3
- Chart placeholder for each tab

## 7.5 MacroView.xaml

**Location:** `src/VoiceStudio.App/Views/Panels/MacroView.xaml`

**Structure:**
- 2-row grid: Tabs (32px) + Node graph (*)
- Tabs: ToggleButtons for Macros/Automation
- Node graph: Border with placeholder text (opacity 0.6)

**Key Elements:**
- ToggleButtons for mode switching
- Node graph canvas placeholder

## 7.6 DiagnosticsView.xaml

**Location:** `src/VoiceStudio.App/Views/Panels/DiagnosticsView.xaml`

**Structure:**
- 2-row grid: Logs (0.6*) + Metrics (0.4*)
- Logs: ListView with log entry template
  - StackPanel with [INFO] prefix and message
- Metrics: Horizontal StackPanel with 3 progress bars
  - CPU, GPU, RAM (160px width, 6px height)
  - Spacing: 24px between metrics

**Key Elements:**
- ListView with ItemTemplate for logs
- ProgressBar metrics (Width="160" Height="6")
- Horizontal layout with 24px spacing

## ViewModels

All ViewModels must:
- Implement `IPanelView` from `VoiceStudio.Core.Panels`
- Have `PanelId`, `DisplayName`, and `Region` properties
- Can start empty (properties added later)

**ViewModel Locations:**
- `ProfilesViewModel.cs` → PanelRegion.Left
- `TimelineViewModel.cs` → PanelRegion.Center
- `EffectsMixerViewModel.cs` → PanelRegion.Right
- `AnalyzerViewModel.cs` → PanelRegion.Right
- `MacroViewModel.cs` → PanelRegion.Bottom
- `DiagnosticsViewModel.cs` → PanelRegion.Bottom

## Code-Behind Files

All code-behind files should:
- Have basic InitializeComponent() call
- Include comment for DataContext wiring later
- Keep minimal implementation initially

## Verification

After implementation, verify:
- [ ] All 6 panels match XAML skeletons exactly
- [ ] All ViewModels implement IPanelView
- [ ] All code-behind files exist
- [ ] Placeholder regions are visible
- [ ] VSQ.* resources are used (not hardcoded colors)
- [ ] Structure matches specification (no simplifications)

