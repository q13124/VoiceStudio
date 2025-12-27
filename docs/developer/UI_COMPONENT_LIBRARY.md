# VoiceStudio Quantum+ UI Component Library

Complete reference for all custom UI controls, reusable components, design tokens, and styling system.

**Version:** 1.0  
**Last Updated:** 2025-01-28  
**Status:** Ready for Use

---

## Table of Contents

1. [Overview](#overview)
2. [Custom Controls](#custom-controls)
3. [Design Tokens](#design-tokens)
4. [Styling System](#styling-system)
5. [Control Usage Examples](#control-usage-examples)
6. [Component Catalog](#component-catalog)
7. [Best Practices](#best-practices)

---

## Overview

VoiceStudio Quantum+ includes a comprehensive UI component library with:

- **32+ Custom Controls**: Specialized controls for audio visualization, mixer, panels, etc.
- **Design Token System**: Centralized design tokens for colors, typography, spacing
- **Styling System**: Reusable styles and themes
- **WinUI 3 Integration**: Built on WinUI 3 framework

### Component Categories

1. **Panel System Controls**: PanelHost, PanelStack, PanelResizeHandle
2. **Audio Visualization Controls**: WaveformControl, SpectrogramControl, VUMeterControl
3. **Mixer Controls**: FaderControl, PanFaderControl
4. **Feedback Controls**: LoadingOverlay, EmptyState, ErrorMessage, SkeletonScreen
5. **Navigation Controls**: CommandPalette, NavIconButton
6. **Quality Controls**: QualityBadgeControl
7. **Analysis Controls**: LoudnessChartControl, PhaseAnalysisControl, RadarChartControl
8. **Automation Controls**: AutomationCurveEditorControl
9. **Utility Controls**: UndoRedoIndicator, HelpOverlay, FloatingWindowHost

---

## Custom Controls

### Panel System Controls

#### PanelHost

**Location:** `src/VoiceStudio.App/Controls/PanelHost.xaml`

**Purpose:** Container control for hosting panel views with header, resize handles, and quality badge.

**Key Features:**
- Panel header with title and icon
- Context-sensitive action bar
- Quality badge display
- Resize handles (horizontal and vertical)
- Panel transitions

**Properties:**
```csharp
public string PanelTitle { get; set; }
public string PanelIcon { get; set; }
public bool ShowQualityBadge { get; set; }
public QualityMetrics QualityMetrics { get; set; }
public UIElement PanelContent { get; set; }
```

**Usage:**
```xml
<controls:PanelHost PanelTitle="Voice Synthesis"
                    PanelIcon="🎙️"
                    ShowQualityBadge="True">
    <controls:PanelHost.PanelContent>
        <views:VoiceSynthesisView />
    </controls:PanelHost.PanelContent>
</controls:PanelHost>
```

---

#### PanelResizeHandle

**Location:** `src/VoiceStudio.App/Controls/PanelResizeHandle.xaml`

**Purpose:** Resize handle for panel resizing (horizontal or vertical).

**Properties:**
```csharp
public string ResizeDirection { get; set; } // "Horizontal" or "Vertical"
```

**Usage:**
```xml
<controls:PanelResizeHandle ResizeDirection="Horizontal" />
```

---

#### PanelStack

**Location:** `src/VoiceStudio.App/Controls/PanelStack.xaml`

**Purpose:** Stack container for multiple panels with tab navigation.

**Features:**
- Tab navigation
- Panel switching
- Panel management

---

### Audio Visualization Controls

#### WaveformControl

**Location:** `src/VoiceStudio.App/Controls/WaveformControl.xaml`

**Purpose:** Custom control for rendering audio waveforms using Win2D.

**Properties:**
```csharp
public List<float> Samples { get; set; }  // Normalized -1.0 to 1.0
public string Mode { get; set; }          // "peak" or "rms"
public double ZoomLevel { get; set; }     // Zoom level
public double PanOffset { get; set; }     // Pan offset
public double PlaybackPosition { get; set; }  // Playback position (-1 = none)
```

**Features:**
- Peak and RMS waveform modes
- Zoom and pan support
- Playback position indicator
- Cached rendering for performance
- Win2D Canvas rendering

**Usage:**
```xml
<controls:WaveformControl Samples="{x:Bind ViewModel.WaveformSamples, Mode=OneWay}"
                          Mode="peak"
                          ZoomLevel="1.0"
                          PlaybackPosition="{x:Bind ViewModel.PlaybackPosition, Mode=OneWay}" />
```

---

#### SpectrogramControl

**Location:** `src/VoiceStudio.App/Controls/SpectrogramControl.xaml`

**Purpose:** Custom control for rendering audio spectrograms using Win2D.

**Properties:**
```csharp
public List<SpectrogramFrame> Frames { get; set; }
public double ZoomLevel { get; set; }
public double PanOffset { get; set; }
public double PlaybackPosition { get; set; }
public int SampleRate { get; set; }
public int FftSize { get; set; }
public int HopLength { get; set; }
```

**Features:**
- FFT-based frequency visualization
- Color mapping for frequency intensity
- Zoom and pan support
- Playback position indicator
- Cached rendering

**Usage:**
```xml
<controls:SpectrogramControl Frames="{x:Bind ViewModel.SpectrogramFrames, Mode=OneWay}"
                             SampleRate="44100"
                             PlaybackPosition="{x:Bind ViewModel.PlaybackPosition, Mode=OneWay}" />
```

---

#### VUMeterControl

**Location:** `src/VoiceStudio.App/Controls/VUMeterControl.xaml`

**Purpose:** Custom control for rendering VU (Volume Unit) meters.

**Properties:**
```csharp
public double PeakLevel { get; set; }  // 0.0 to 1.0 (1.0 = 0 dBFS)
public double RmsLevel { get; set; }   // 0.0 to 1.0
public double DecayRate { get; set; }  // Peak decay rate (default: 0.95)
```

**Features:**
- Peak and RMS level display
- Color-coded zones (safe, warning, danger)
- Peak hold indicator
- Automatic peak decay
- Win2D Canvas rendering

**Zones:**
- Safe: < 70% (-3 dB)
- Warning: 70-90% (-3 to -1 dB)
- Danger: > 90% (-1 to 0 dB)

**Usage:**
```xml
<controls:VUMeterControl PeakLevel="{x:Bind ViewModel.PeakLevel, Mode=OneWay}"
                         RmsLevel="{x:Bind ViewModel.RmsLevel, Mode=OneWay}" />
```

---

### Mixer Controls

#### FaderControl

**Location:** `src/VoiceStudio.App/Controls/FaderControl.xaml`

**Purpose:** Vertical fader control for mixer channels.

**Properties:**
```csharp
public double Volume { get; set; }  // 0.0 to 2.0 (0.0 = -∞ dB, 1.0 = 0 dB, 2.0 = +6 dB)
```

**Features:**
- Vertical fader with drag support
- Volume range: -96 dB to +6 dB
- Visual feedback
- Mouse and touch support

**Usage:**
```xml
<controls:FaderControl Volume="{x:Bind ViewModel.Volume, Mode=TwoWay}" />
```

---

#### PanFaderControl

**Location:** `src/VoiceStudio.App/Controls/PanFaderControl.xaml`

**Purpose:** Pan control for stereo positioning.

**Properties:**
```csharp
public double Pan { get; set; }  // -1.0 (left) to 1.0 (right), 0.0 = center
```

**Usage:**
```xml
<controls:PanFaderControl Pan="{x:Bind ViewModel.Pan, Mode=TwoWay}" />
```

---

### Feedback Controls

#### LoadingOverlay

**Location:** `src/VoiceStudio.App/Controls/LoadingOverlay.xaml`

**Purpose:** Overlay control for showing loading state.

**Properties:**
```csharp
public bool IsLoading { get; set; }
public string LoadingMessage { get; set; }
```

**Features:**
- Semi-transparent overlay
- Progress ring
- Loading message
- Fade-in animation

**Usage:**
```xml
<controls:LoadingOverlay IsLoading="{x:Bind ViewModel.IsLoading, Mode=OneWay}"
                         LoadingMessage="Loading profiles..." />
```

---

#### EmptyState

**Location:** `src/VoiceStudio.App/Controls/EmptyState.xaml`

**Purpose:** Empty state display for when no content is available.

**Properties:**
```csharp
public string Icon { get; set; }
public string Title { get; set; }
public string Message { get; set; }
public string ActionText { get; set; }
public ICommand ActionCommand { get; set; }
public Visibility HasAction { get; set; }
```

**Usage:**
```xml
<controls:EmptyState Icon="📁"
                     Title="No Profiles"
                     Message="Create your first voice profile to get started."
                     ActionText="Create Profile"
                     ActionCommand="{x:Bind ViewModel.CreateProfileCommand, Mode=OneWay}"
                     HasAction="Visible" />
```

---

#### ErrorMessage

**Location:** `src/VoiceStudio.App/Controls/ErrorMessage.xaml`

**Purpose:** Consistent error message display.

**Properties:**
```csharp
public string Title { get; set; }
public string Message { get; set; }
public string ActionText { get; set; }
public ICommand ActionCommand { get; set; }
public Visibility HasAction { get; set; }
```

**Usage:**
```xml
<controls:ErrorMessage Title="Connection Failed"
                       Message="Unable to connect to backend. Please check your connection."
                       ActionText="Retry"
                       ActionCommand="{x:Bind ViewModel.RetryCommand, Mode=OneWay}"
                       HasAction="Visible" />
```

---

#### SkeletonScreen

**Location:** `src/VoiceStudio.App/Controls/SkeletonScreen.xaml`

**Purpose:** Skeleton screen for loading state (content placeholders).

**Properties:**
```csharp
public bool IsLoading { get; set; }
```

**Features:**
- Animated placeholders
- Sliding animation
- Content structure preview

**Usage:**
```xml
<controls:SkeletonScreen IsLoading="{x:Bind ViewModel.IsLoading, Mode=OneWay}" />
```

---

### Navigation Controls

#### CommandPalette

**Location:** `src/VoiceStudio.App/Controls/CommandPalette.xaml`

**Purpose:** Command palette for quick command access (Ctrl+P).

**Features:**
- Search-based command discovery
- Keyboard navigation
- Command shortcuts display
- Fuzzy search support

**Usage:**
```xml
<controls:CommandPalette x:Name="CommandPalette"
                         Visibility="{x:Bind ShowCommandPalette, Mode=OneWay}" />
```

---

#### NavIconButton

**Location:** `src/VoiceStudio.App/Controls/NavIconButton.xaml`

**Purpose:** Icon button for navigation rail.

**Properties:**
```csharp
public string Icon { get; set; }
public string Label { get; set; }
public bool IsSelected { get; set; }
```

**Usage:**
```xml
<controls:NavIconButton Icon="📋"
                        Label="Profiles"
                        IsSelected="{x:Bind ViewModel.IsProfilesSelected, Mode=TwoWay}"
                        Command="{x:Bind ViewModel.NavigateToProfilesCommand, Mode=OneWay}" />
```

---

### Quality Controls

#### QualityBadgeControl

**Location:** `src/VoiceStudio.App/Controls/QualityBadgeControl.xaml`

**Purpose:** Quality badge display for panels.

**Properties:**
```csharp
public QualityMetrics QualityMetrics { get; set; }
```

**Features:**
- Quality score display
- Color-coded quality indicator
- Tooltip with detailed metrics

**Usage:**
```xml
<controls:QualityBadgeControl QualityMetrics="{x:Bind ViewModel.QualityMetrics, Mode=OneWay}" />
```

---

### Analysis Controls

#### LoudnessChartControl

**Location:** `src/VoiceStudio.App/Controls/LoudnessChartControl.xaml`

**Purpose:** Chart control for loudness analysis (LUFS over time).

**Properties:**
```csharp
public List<LoudnessData> Data { get; set; }
```

---

#### PhaseAnalysisControl

**Location:** `src/VoiceStudio.App/Controls/PhaseAnalysisControl.xaml`

**Purpose:** Control for phase analysis visualization.

**Properties:**
```csharp
public List<PhaseData> Data { get; set; }
```

---

#### RadarChartControl

**Location:** `src/VoiceStudio.App/Controls/RadarChartControl.xaml`

**Purpose:** Radar/spider chart for multi-dimensional analysis.

**Properties:**
```csharp
public RadarChartData Data { get; set; }
```

---

### Automation Controls

#### AutomationCurveEditorControl

**Location:** `src/VoiceStudio.App/Controls/AutomationCurveEditorControl.xaml`

**Purpose:** Editor for automation curves.

**Properties:**
```csharp
public AutomationCurve Curve { get; set; }
public double ZoomLevel { get; set; }
public double PanOffset { get; set; }
```

**Features:**
- Visual curve editing
- Point manipulation
- Bezier curve interpolation
- Time and value editing

---

### Utility Controls

#### UndoRedoIndicator

**Location:** `src/VoiceStudio.App/Controls/UndoRedoIndicator.xaml`

**Purpose:** Visual indicator for undo/redo state.

**Properties:**
```csharp
public bool CanUndo { get; set; }
public bool CanRedo { get; set; }
public int UndoCount { get; set; }
public int RedoCount { get; set; }
```

---

#### HelpOverlay

**Location:** `src/VoiceStudio.App/Controls/HelpOverlay.xaml`

**Purpose:** Contextual help overlay.

**Properties:**
```csharp
public string Title { get; set; }
public string Content { get; set; }
public bool IsVisible { get; set; }
```

---

#### FloatingWindowHost

**Location:** `src/VoiceStudio.App/Controls/FloatingWindowHost.xaml`

**Purpose:** Host for floating windows.

**Properties:**
```csharp
public UIElement Content { get; set; }
public bool IsVisible { get; set; }
```

---

## Design Tokens

### Color System

**Location:** `src/VoiceStudio.App/Resources/DesignTokens.xaml`

#### Base Colors

```xml
<!-- Background Colors -->
VSQ.Background.Darker      #FF0A0F15
VSQ.Background.Dark        #FF121A24
VSQ.Panel.Background.Dark  #FF151921
VSQ.Panel.Background.Darker #FF1E2329
VSQ.Panel.Background.Header #FF20252E
VSQ.Panel.Background.Master #FF252A34

<!-- Accent Colors -->
VSQ.Accent.Cyan            #FF00B7C2
VSQ.Accent.CyanGlow        #3030E0FF
VSQ.Accent.Lime            #FF9AFF33
VSQ.Accent.Magenta         #FFB040FF

<!-- Text Colors -->
VSQ.Text.Primary           #FFCDD9E5
VSQ.Text.Secondary         #FF8A9BB3

<!-- Semantic Colors -->
VSQ.Warn                   #FFFFB540
VSQ.Error                  #FFFF4060
VSQ.Success                #FF40FF80
```

#### Usage

```xml
<TextBlock Foreground="{StaticResource VSQ.Text.PrimaryBrush}" />
<Border Background="{StaticResource VSQ.Panel.Background.DarkBrush}" />
<Button Background="{StaticResource VSQ.Accent.CyanBrush}" />
```

---

### Typography

#### Font Sizes

```xml
VSQ.FontSize.Caption    10
VSQ.FontSize.Body       12
VSQ.FontSize.Title      16
VSQ.FontSize.Heading    20
```

#### Usage

```xml
<TextBlock FontSize="{StaticResource VSQ.FontSize.Body}" />
<TextBlock FontSize="{StaticResource VSQ.FontSize.Title}" FontWeight="SemiBold" />
```

---

### Spacing

#### Spacing Values

```xml
VSQ.Spacing.Value.XSmall   2
VSQ.Spacing.Value.Small    4
VSQ.Spacing.Value.Medium   8
VSQ.Spacing.Value.Large    16
VSQ.Spacing.Value.XLarge   24
```

#### Spacing Thickness

```xml
VSQ.Spacing.None        0
VSQ.Spacing.XSmall      2
VSQ.Spacing.Small       4
VSQ.Spacing.Medium      8
VSQ.Spacing.Large       16
VSQ.Spacing.XLarge      24
```

#### Usage

```xml
<StackPanel Margin="{StaticResource VSQ.Spacing.Medium}" />
<Border Padding="{StaticResource VSQ.Spacing.Large}" />
<Button Margin="0,0,{StaticResource VSQ.Spacing.Value.Medium},0" />
```

---

### Corner Radius

```xml
VSQ.CornerRadius.Panel     8
VSQ.CornerRadius.Button    4
VSQ.CornerRadius.Small     2
```

#### Usage

```xml
<Border CornerRadius="{StaticResource VSQ.CornerRadius.Panel}" />
<Button CornerRadius="{StaticResource VSQ.CornerRadius.Button}" />
```

---

### Animation Durations

```xml
VSQ.Animation.Duration.Fast             100ms
VSQ.Animation.Duration.Medium           150ms
VSQ.Animation.Duration.Slow             300ms
VSQ.Animation.Duration.PanelTransition  200ms
```

---

## Styling System

### Button Styles

#### VSQ.Button.FocusStyle

**Purpose:** Base button style with focus indicators.

**Usage:**
```xml
<Button Style="{StaticResource VSQ.Button.FocusStyle}" Content="Click Me" />
```

#### VSQ.Button.HoverStyle

**Purpose:** Button style with hover effects.

**Features:**
- Hover background change
- Scale transform on hover
- Smooth transitions

**Usage:**
```xml
<Button Style="{StaticResource VSQ.Button.HoverStyle}" Content="Hover Me" />
```

#### VSQ.Button.LoadingStyle

**Purpose:** Button style with loading state support.

**Features:**
- Loading spinner
- Disabled state during loading
- Opacity change during loading

**Usage:**
```xml
<Button Style="{StaticResource VSQ.Button.LoadingStyle}" 
        IsLoading="{x:Bind ViewModel.IsLoading, Mode=OneWay}" />
```

---

### List Item Styles

#### VSQ.ListItem.HoverStyle

**Purpose:** List item style with hover effects.

**Usage:**
```xml
<ListViewItem Style="{StaticResource VSQ.ListItem.HoverStyle}" />
```

#### VSQ.ListItem.SelectionStyle

**Purpose:** List item style with selection highlighting.

**Usage:**
```xml
<ListViewItem Style="{StaticResource VSQ.ListItem.SelectionStyle}" />
```

---

### Progress Styles

#### VSQ.LoadingSpinner.Style

**Purpose:** Loading spinner style.

**Usage:**
```xml
<ProgressRing Style="{StaticResource VSQ.LoadingSpinner.Style}" />
```

#### VSQ.ProgressBar.Style

**Purpose:** Progress bar style.

**Usage:**
```xml
<ProgressBar Style="{StaticResource VSQ.ProgressBar.Style}" 
             Value="{x:Bind ViewModel.Progress, Mode=OneWay}" />
```

---

### Animation Storyboards

#### VSQ.Panel.FadeIn

**Purpose:** Fade-in animation for panels.

**Usage:**
```xml
<Storyboard x:Name="FadeInStoryboard" Storyboard="{StaticResource VSQ.Panel.FadeIn}">
```

#### VSQ.Panel.FadeOut

**Purpose:** Fade-out animation for panels.

#### VSQ.Panel.SlideIn

**Purpose:** Slide-in animation for panels.

---

## Control Usage Examples

### Complete Panel Example

```xml
<UserControl x:Class="VoiceStudio.App.Views.Panels.ExamplePanel"
             xmlns:controls="using:VoiceStudio.App.Controls">
    <Grid>
        <controls:PanelHost PanelTitle="Example Panel"
                            PanelIcon="📋">
            <controls:PanelHost.PanelContent>
                <Grid>
                    <!-- Loading State -->
                    <controls:LoadingOverlay IsLoading="{x:Bind ViewModel.IsLoading, Mode=OneWay}"
                                             LoadingMessage="Loading data..." />
                    
                    <!-- Content -->
                    <StackPanel>
                        <!-- Empty State -->
                        <controls:EmptyState Visibility="{x:Bind ViewModel.ShowEmptyState, Mode=OneWay}"
                                             Icon="📁"
                                             Title="No Data"
                                             Message="Add some data to get started."
                                             ActionText="Add Data"
                                             ActionCommand="{x:Bind ViewModel.AddDataCommand, Mode=OneWay}" />
                        
                        <!-- Error State -->
                        <controls:ErrorMessage Visibility="{x:Bind ViewModel.ShowError, Mode=OneWay}"
                                              Title="Error"
                                              Message="{x:Bind ViewModel.ErrorMessage, Mode=OneWay}"
                                              ActionText="Retry"
                                              ActionCommand="{x:Bind ViewModel.RetryCommand, Mode=OneWay}" />
                        
                        <!-- Content -->
                        <ListView ItemsSource="{x:Bind ViewModel.Items, Mode=OneWay}"
                                  ItemTemplate="{StaticResource ItemTemplate}"
                                  Style="{StaticResource VSQ.ListItem.HoverStyle}" />
                    </StackPanel>
                </Grid>
            </controls:PanelHost.PanelContent>
        </controls:PanelHost>
    </Grid>
</UserControl>
```

### Waveform Visualization Example

```xml
<StackPanel>
    <controls:WaveformControl Samples="{x:Bind ViewModel.WaveformSamples, Mode=OneWay}"
                              Mode="peak"
                              ZoomLevel="{x:Bind ViewModel.ZoomLevel, Mode=TwoWay}"
                              PanOffset="{x:Bind ViewModel.PanOffset, Mode=TwoWay}"
                              PlaybackPosition="{x:Bind ViewModel.PlaybackPosition, Mode=OneWay}"
                              Height="200" />
    
    <controls:VUMeterControl PeakLevel="{x:Bind ViewModel.PeakLevel, Mode=OneWay}"
                             RmsLevel="{x:Bind ViewModel.RmsLevel, Mode=OneWay}"
                             Width="50"
                             Height="200" />
</StackPanel>
```

### Mixer Channel Example

```xml
<StackPanel Orientation="Horizontal" Spacing="{StaticResource VSQ.Spacing.Value.Medium}">
    <TextBlock Text="Channel 1" />
    
    <controls:FaderControl Volume="{x:Bind ViewModel.Volume, Mode=TwoWay}"
                           Width="30"
                           Height="200" />
    
    <controls:PanFaderControl Pan="{x:Bind ViewModel.Pan, Mode=TwoWay}"
                              Width="50"
                              Height="100" />
    
    <controls:VUMeterControl PeakLevel="{x:Bind ViewModel.PeakLevel, Mode=OneWay}"
                             RmsLevel="{x:Bind ViewModel.RmsLevel, Mode=OneWay}"
                             Width="30"
                             Height="200" />
</StackPanel>
```

---

## Component Catalog

### Complete Control Inventory

| Control | Location | Purpose | Properties |
|---------|----------|---------|------------|
| PanelHost | `Controls/PanelHost.xaml` | Panel container | PanelTitle, PanelIcon, QualityMetrics |
| PanelResizeHandle | `Controls/PanelResizeHandle.xaml` | Resize handle | ResizeDirection |
| PanelStack | `Controls/PanelStack.xaml` | Panel stack | - |
| WaveformControl | `Controls/WaveformControl.xaml` | Waveform visualization | Samples, Mode, ZoomLevel |
| SpectrogramControl | `Controls/SpectrogramControl.xaml` | Spectrogram visualization | Frames, SampleRate |
| VUMeterControl | `Controls/VUMeterControl.xaml` | VU meter | PeakLevel, RmsLevel |
| FaderControl | `Controls/FaderControl.xaml` | Volume fader | Volume |
| PanFaderControl | `Controls/PanFaderControl.xaml` | Pan control | Pan |
| LoadingOverlay | `Controls/LoadingOverlay.xaml` | Loading overlay | IsLoading, LoadingMessage |
| EmptyState | `Controls/EmptyState.xaml` | Empty state | Icon, Title, Message |
| ErrorMessage | `Controls/ErrorMessage.xaml` | Error message | Title, Message |
| SkeletonScreen | `Controls/SkeletonScreen.xaml` | Skeleton screen | IsLoading |
| CommandPalette | `Controls/CommandPalette.xaml` | Command palette | - |
| NavIconButton | `Controls/NavIconButton.xaml` | Navigation button | Icon, Label |
| QualityBadgeControl | `Controls/QualityBadgeControl.xaml` | Quality badge | QualityMetrics |
| LoudnessChartControl | `Controls/LoudnessChartControl.xaml` | Loudness chart | Data |
| PhaseAnalysisControl | `Controls/PhaseAnalysisControl.xaml` | Phase analysis | Data |
| RadarChartControl | `Controls/RadarChartControl.xaml` | Radar chart | Data |
| AutomationCurveEditorControl | `Controls/AutomationCurveEditorControl.xaml` | Automation editor | Curve |
| UndoRedoIndicator | `Controls/UndoRedoIndicator.xaml` | Undo/redo indicator | CanUndo, CanRedo |
| HelpOverlay | `Controls/HelpOverlay.xaml` | Help overlay | Title, Content |
| FloatingWindowHost | `Controls/FloatingWindowHost.xaml` | Floating window | Content |
| LoadingButton | `Controls/LoadingButton.xaml` | Button with loading | IsLoading |
| ErrorDialog | `Controls/ErrorDialog.xaml` | Error dialog | Title, Message |
| OnboardingHints | `Controls/OnboardingHints.xaml` | Onboarding hints | - |
| MacroNodeEditorControl | `Controls/MacroNodeEditorControl.xaml` | Macro node editor | Node |
| AnalyticsChartControl | `Controls/AnalyticsChartControl.xaml` | Analytics chart | Data |
| AutomationCurvesEditorControl | `Controls/AutomationCurvesEditorControl.xaml` | Automation curves editor | Curves |

**Total: 27+ Custom Controls**

---

## Best Practices

### Using Design Tokens

**✅ Do:**
```xml
<TextBlock Foreground="{StaticResource VSQ.Text.PrimaryBrush}" />
<Border Background="{StaticResource VSQ.Panel.Background.DarkBrush}" />
<Button Margin="0,0,{StaticResource VSQ.Spacing.Value.Medium},0" />
```

**❌ Don't:**
```xml
<TextBlock Foreground="#CDD9E5" />
<Border Background="#151921" />
<Button Margin="0,0,8,0" />
```

### Using Controls

**✅ Do:**
```xml
<controls:LoadingOverlay IsLoading="{x:Bind ViewModel.IsLoading, Mode=OneWay}" />
<controls:EmptyState Title="No Data" Message="Add data to continue." />
```

**❌ Don't:**
```xml
<ProgressRing Visibility="{x:Bind ViewModel.IsLoading, Mode=OneWay}" />
<TextBlock Text="No Data" />
```

### Performance

**Tips:**
- Use cached rendering for Win2D controls
- Limit waveform sample count for performance
- Use skeleton screens for long loading times
- Minimize control nesting

### Accessibility

**Requirements:**
- Add `AutomationProperties.Name` to all controls
- Provide `AutomationProperties.HelpText`
- Support keyboard navigation
- Ensure focus indicators visible

---

## Summary

This UI Component Library provides:

1. **27+ Custom Controls**: Specialized controls for all UI needs
2. **Design Token System**: Centralized design values
3. **Styling System**: Reusable styles and themes
4. **Usage Examples**: Complete examples for all controls
5. **Best Practices**: Guidelines for using components

**Key Features:**
- ✅ Comprehensive control library
- ✅ Design token system
- ✅ Consistent styling
- ✅ Accessibility support
- ✅ Performance optimized

---

**Document Version:** 1.0  
**Last Updated:** 2025-01-28  
**Next Review:** After new controls added or major changes

