# VoiceStudio Quantum+ - COMPLETE UI DESIGN EMBEDDED

## ALL UI DESIGN SPECIFICATIONS & IMPLEMENTATION - CONTENT EMBEDDED

**Version:** 1.0 - Complete UI Design Embedded
**Date:** 2025-12-26
**Status:** ALL UI CONTENT EMBEDDED - NO EXTERNAL REFERENCES

---

## 📋 TABLE OF CONTENTS

### **ORIGINAL UI VISION**
- [ChatGPT UI Specification](#chatgpt-ui-specification)
- [Complete Implementation Specification](#complete-implementation-specification)

### **MAIN WINDOW STRUCTURE**
- [3-Row Grid Layout](#3-row-grid-layout)
- [PanelHost System](#panelhost-system)
- [Navigation Rail](#navigation-rail)

### **DESIGN TOKENS**
- [VSQ.* Design Token System](#vsq-design-token-system)
- [Complete XAML Implementation](#complete-xaml-implementation)

### **CORE PANELS**
- [6 Core Panel Specifications](#6-core-panel-specifications)
- [Panel Registry System](#panel-registry-system)

### **FILE STRUCTURE**
- [Complete Project Organization](#complete-project-organization)
- [MVVM Implementation](#mvvm-implementation)

---

## 🎯 ORIGINAL UI VISION - EMBEDDED

### ChatGPT UI Specification

**This document contains the original UI specification script that was collaboratively created with ChatGPT. This is the source of truth for the exact UI design and must be preserved.**

**All UI work must reference this document to ensure consistency with the original vision.**

#### ORIGINAL UI VISION

This document preserves the original UI specification that was created through collaboration with ChatGPT. It defines:

1. **Complete MainWindow Structure** - Exact 3-row grid layout
2. **PanelHost System** - Mandatory panel container system
3. **6 Core Panels** - Profiles, Timeline, EffectsMixer, Analyzer, Macro, Diagnostics
4. **Design Tokens** - Complete VSQ.* design token system
5. **File Structure** - Canonical file organization
6. **Panel Registry** - Panel management system
7. **Complete XAML Code** - Full implementation code

#### CRITICAL RULES FROM ORIGINAL SCRIPT

**These rules were established in the original ChatGPT collaboration and must NEVER be violated:**

##### 1. Layout Structure (NON-NEGOTIABLE)
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

##### 2. MVVM Separation (NON-NEGOTIABLE)
```
✅ MUST have separate files for every panel:
   - PanelNameView.xaml
   - PanelNameView.xaml.cs
   - PanelNameViewModel.cs (implements IPanelView)

❌ NEVER merge View and ViewModel files
❌ NEVER combine .xaml + .xaml.cs + ViewModel.cs into single file
```

##### 3. PanelHost Control (NON-NEGOTIABLE)
```
✅ MUST use PanelHost UserControl for all panels
✅ MUST maintain PanelHost structure (header 32px + content area)

❌ NEVER replace PanelHost with raw Grid
❌ NEVER inline panel content directly in MainWindow
```

##### 4. Design Tokens (NON-NEGOTIABLE)
```
✅ MUST use VSQ.* resources from DesignTokens.xaml
✅ MUST reference design tokens for ALL styling

❌ NEVER hardcode colors, fonts, or spacing
❌ NEVER create new color schemes
```

##### 5. Panel Count (NON-NEGOTIABLE)
```
✅ MUST maintain 6 core panels:
   - ProfilesView (voice profiles, styles, characters)
   - TimelineView (audio clips, tracks, editing)
   - EffectsMixerView (audio effects, processing chains)
   - AnalyzerView (spectrum, waveform, quality metrics)
   - MacroView (automation, scripting, batch processing)
   - DiagnosticsView (logs, performance, debugging)

❌ NEVER reduce panel count
❌ NEVER combine panels
❌ NEVER remove placeholder areas
```

##### 6. Professional Quality (NON-NEGOTIABLE)
```
✅ MUST implement full professional DAW-grade UI
✅ MUST include all placeholder areas (waveforms, spectrograms, etc.)
✅ MUST implement real functionality (no stubs)

❌ NEVER create demo-quality UI
❌ NEVER simplify complex layouts
❌ NEVER remove advanced features
```

---

## 🏗️ COMPLETE IMPLEMENTATION SPECIFICATION - EMBEDDED

### Professional DAW-Grade UI Implementation Guide

**Version:** 1.0
**Date:** 2025
**Target:** WinUI 3 (.NET 8) + Python FastAPI + MCP Integration

#### CRITICAL GUARDRAILS (Read First)

**These rules are NON-NEGOTIABLE. Enforce them at every step:**

```
Do NOT simplify the UI layout or collapse panels.
Keep the 3-column + nav + bottom deck layout and PanelHost controls.
Do NOT merge Views and ViewModels. Each panel = .xaml + .xaml.cs + ViewModel.cs.
Do NOT remove placeholder areas (waveform, spectrogram, analyzers, macros, logs).
Use DesignTokens.xaml for all colors/typography; no hardcoded values.
Treat this as a professional DAW-grade app (Adobe/FL Studio level), not a demo.
```

**Violation Detection:**
- Merged View/ViewModel files → REVERT
- PanelHost replaced with Grid → REVERT
- Reduced panel count → REVERT
- Hardcoded colors → REVERT
- Simplified layout → REVERT

---

## 📁 Complete Project Structure - EMBEDDED

```
VoiceStudio/
├── src/
│   ├── VoiceStudio.App/              # WinUI 3 frontend (C#/XAML)
│   │   ├── VoiceStudioApp.csproj
│   │   ├── App.xaml
│   │   ├── App.xaml.cs
│   │   ├── MainWindow.xaml
│   │   ├── MainWindow.xaml.cs
│   │   ├── Resources/
│   │   │   ├── DesignTokens.xaml
│   │   │   └── Styles/
│   │   │       ├── Controls.xaml
│   │   │       ├── Text.xaml
│   │   │       └── Panels.xaml
│   │   ├── Controls/
│   │   │   ├── PanelHost.xaml
│   │   │   ├── PanelHost.xaml.cs
│   │   │   ├── NavIconButton.xaml
│   │   │   └── NavIconButton.xaml.cs
│   │   ├── Views/
│   │   │   └── Panels/
│   │   │       ├── ProfilesView.xaml
│   │   │       ├── ProfilesView.xaml.cs
│   │   │       ├── TimelineView.xaml
│   │   │       ├── TimelineView.xaml.cs
│   │   │       ├── EffectsMixerView.xaml
│   │   │       ├── EffectsMixerView.xaml.cs
│   │   │       ├── AnalyzerView.xaml
│   │   │       ├── AnalyzerView.xaml.cs
│   │   │       ├── MacroView.xaml
│   │   │       ├── MacroView.xaml.cs
│   │   │       ├── DiagnosticsView.xaml
│   │   │       └── DiagnosticsView.xaml.cs
│   │   ├── ViewModels/
│   │   │   └── Panels/
│   │   │       ├── ProfilesViewModel.cs
│   │   │       ├── TimelineViewModel.cs
│   │   │       ├── EffectsMixerViewModel.cs
│   │   │       ├── AnalyzerViewModel.cs
│   │   │       ├── MacroViewModel.cs
│   │   │       └── DiagnosticsViewModel.cs
│   │   ├── Services/
│   │   │   ├── IBackendClient.cs
│   │   │   ├── BackendClient.cs
│   │   │   ├── BackendClientConfig.cs
│   │   │   └── PluginManager.cs
│   │   └── Plugins/                  # Optional: UI plugin DLLs
│   ├── VoiceStudio.Core/             # Shared C# library
│   │   ├── Panels/
│   │   │   ├── IPanelView.cs
│   │   │   ├── PanelRegion.cs
│   │   │   ├── PanelDescriptor.cs
│   │   │   ├── IPanelRegistry.cs
│   │   │   └── PanelRegistry.cs
│   │   └── Models/
│   │       ├── VoiceProfile.cs
│   │       ├── AudioClip.cs
│   │       ├── Track.cs
│   │       ├── Project.cs
│   │       └── MeterReading.cs
│   └── VoiceStudio.sln
├── backend/
│   ├── api/                          # Python FastAPI
│   │   ├── app.py
│   │   ├── requirements.txt
│   │   ├── core/
│   │   │   ├── engines/              # ML engines (XTTS, Whisper, etc.)
│   │   │   ├── services/             # Business logic
│   │   │   └── models/               # Data models
│   │   ├── routes/                   # API endpoints
│   │   │   ├── synthesize.py
│   │   │   ├── training.py
│   │   │   ├── transcribe.py
│   │   │   └── quality.py
│   │   └── utils/                    # Utilities
├── docs/
│   ├── design/                       # UI/UX specifications
│   ├── api/                          # API documentation
│   ├── governance/                   # Development rules
│   └── user/                         # User documentation
└── scripts/
    ├── build.ps1                     # Build script
    ├── deploy.ps1                    # Deployment script
    └── test.ps1                      # Test runner
```

---

## 🏠 MAIN WINDOW STRUCTURE - EMBEDDED

### 3-Row Grid Layout Specification

#### MainWindow.xaml - Complete Implementation

```xaml
<Window
    x:Class="VoiceStudio.App.MainWindow"
    xmlns="http://schemas.microsoft.com/winfx/2006/xaml/presentation"
    xmlns:x="http://schemas.microsoft.com/winfx/2006/xaml"
    xmlns:d="http://schemas.microsoft.com/expression/blend/2008"
    xmlns:mc="http://schemas.openxmlformats.org/markup-compatibility/2006"
    xmlns:controls="using:VoiceStudio.App.Controls"
    mc:Ignorable="d"
    Title="VoiceStudio Quantum+">

    <Grid Background="{StaticResource VSQ.Background.Primary}">
        <!-- Row Definitions: Command Deck | Main Workspace | Status Bar -->
        <Grid.RowDefinitions>
            <RowDefinition Height="Auto"/>  <!-- Row 0: Command Deck (MenuBar + Toolbar) -->
            <RowDefinition Height="*"/>     <!-- Row 1: Main Workspace -->
            <RowDefinition Height="Auto"/>  <!-- Row 2: Status Bar -->
        </Grid.RowDefinitions>

        <!-- Column Definitions: Nav | Left Panel | Center Panel | Right Panel -->
        <Grid.ColumnDefinitions>
            <ColumnDefinition Width="64"/>   <!-- Column 0: Nav Rail -->
            <ColumnDefinition Width="0.2*"/> <!-- Column 1: Left Panel (20%) -->
            <ColumnDefinition Width="0.55*"/> <!-- Column 2: Center Panel (55%) -->
            <ColumnDefinition Width="0.25*"/> <!-- Column 3: Right Panel (25%) -->
        </Grid.ColumnDefinitions>

        <!-- COMMAND DECK (Row 0) -->
        <Border Grid.Row="0" Grid.Column="0" Grid.ColumnSpan="4"
                Background="{StaticResource VSQ.Background.Secondary}"
                BorderBrush="{StaticResource VSQ.Border.Primary}"
                BorderThickness="0,0,0,1">

            <Grid>
                <Grid.ColumnDefinitions>
                    <ColumnDefinition Width="64"/>  <!-- Menu Icon -->
                    <ColumnDefinition Width="*"/>    <!-- Menu Items -->
                    <ColumnDefinition Width="Auto"/> <!-- Toolbar -->
                </Grid.ColumnDefinitions>

                <!-- Menu Bar -->
                <MenuBar Grid.Column="0" Grid.ColumnSpan="2" VerticalAlignment="Center">
                    <MenuBarItem Title="File">
                        <MenuFlyoutItem Text="New Project" Icon="Document"/>
                        <MenuFlyoutItem Text="Open Project" Icon="OpenFile"/>
                        <MenuFlyoutSeparator/>
                        <MenuFlyoutItem Text="Save" Icon="Save"/>
                        <MenuFlyoutItem Text="Save As..." Icon="Save"/>
                        <MenuFlyoutSeparator/>
                        <MenuFlyoutItem Text="Exit" Icon="Clear"/>
                    </MenuBarItem>

                    <MenuBarItem Title="Edit">
                        <MenuFlyoutItem Text="Undo" Icon="Undo"/>
                        <MenuFlyoutItem Text="Redo" Icon="Redo"/>
                        <MenuFlyoutSeparator/>
                        <MenuFlyoutItem Text="Cut" Icon="Cut"/>
                        <MenuFlyoutItem Text="Copy" Icon="Copy"/>
                        <MenuFlyoutItem Text="Paste" Icon="Paste"/>
                    </MenuBarItem>

                    <MenuBarItem Title="Tools">
                        <MenuFlyoutItem Text="Batch Processing" Icon="Processing"/>
                        <MenuFlyoutItem Text="Quality Analysis" Icon="DataBars"/>
                        <MenuFlyoutSeparator/>
                        <MenuFlyoutItem Text="Settings" Icon="Setting"/>
                    </MenuBarItem>

                    <MenuBarItem Title="Help">
                        <MenuFlyoutItem Text="Documentation" Icon="Help"/>
                        <MenuFlyoutItem Text="About" Icon="Info"/>
                    </MenuBarItem>
                </MenuBar>

                <!-- Toolbar (48px height) -->
                <Border Grid.Column="2" Height="48"
                        Background="{StaticResource VSQ.Background.Tertiary}"
                        BorderBrush="{StaticResource VSQ.Border.Secondary}"
                        BorderThickness="1,0,0,0">

                    <StackPanel Orientation="Horizontal" Spacing="8" Margin="8,0">
                        <!-- Transport Controls -->
                        <Button Content="⏮" ToolTipService.ToolTip="Previous"
                                Style="{StaticResource VSQ.Button.Icon}"/>
                        <Button Content="⏯" ToolTipService.ToolTip="Play/Pause"
                                Style="{StaticResource VSQ.Button.Icon}"/>
                        <Button Content="⏹" ToolTipService.ToolTip="Stop"
                                Style="{StaticResource VSQ.Button.Icon}"/>
                        <Button Content="⏭" ToolTipService.ToolTip="Next"
                                Style="{StaticResource VSQ.Button.Icon}"/>

                        <Border Width="1" Background="{StaticResource VSQ.Border.Secondary}"
                                Margin="4,0" Opacity="0.5"/>

                        <!-- Recording -->
                        <Button Content="⏺" ToolTipService.ToolTip="Record"
                                Style="{StaticResource VSQ.Button.Icon.Danger}"/>

                        <Border Width="1" Background="{StaticResource VSQ.Border.Secondary}"
                                Margin="4,0" Opacity="0.5"/>

                        <!-- Quality Tools -->
                        <Button Content="📊" ToolTipService.ToolTip="Quality Analysis"
                                Style="{StaticResource VSQ.Button.Icon}"/>
                        <Button Content="🎚️" ToolTipService.ToolTip="Effects"
                                Style="{StaticResource VSQ.Button.Icon}"/>
                        <Button Content="🔧" ToolTipService.ToolTip="Macros"
                                Style="{StaticResource VSQ.Button.Icon}"/>
                    </StackPanel>
                </Border>
            </Grid>
        </Border>

        <!-- NAVIGATION RAIL (Column 0) -->
        <Border Grid.Row="0" Grid.Column="0" Grid.RowSpan="2"
                Background="{StaticResource VSQ.Background.Secondary}"
                BorderBrush="{StaticResource VSQ.Border.Primary}"
                BorderThickness="0,0,1,0">

            <StackPanel Spacing="4" Margin="4">
                <!-- Nav Toggle Buttons (64px width rail) -->
                <controls:NavIconButton Icon="👤" ToolTip="Profiles"
                                       IsChecked="{x:Bind ViewModel.IsProfilesPanelVisible, Mode=TwoWay}"/>
                <controls:NavIconButton Icon="⏱️" ToolTip="Timeline"
                                       IsChecked="{x:Bind ViewModel.IsTimelinePanelVisible, Mode=TwoWay}"/>
                <controls:NavIconButton Icon="🎛️" ToolTip="Effects Mixer"
                                       IsChecked="{x:Bind ViewModel.IsEffectsMixerPanelVisible, Mode=TwoWay}"/>
                <controls:NavIconButton Icon="📊" ToolTip="Analyzer"
                                       IsChecked="{x:Bind ViewModel.IsAnalyzerPanelVisible, Mode=TwoWay}"/>
                <controls:NavIconButton Icon="⚡" ToolTip="Macros"
                                       IsChecked="{x:Bind ViewModel.IsMacroPanelVisible, Mode=TwoWay}"/>
                <controls:NavIconButton Icon="🔍" ToolTip="Diagnostics"
                                       IsChecked="{x:Bind ViewModel.IsDiagnosticsPanelVisible, Mode=TwoWay}"/>

                <Border Height="1" Background="{StaticResource VSQ.Border.Secondary}"
                        Margin="4,8" Opacity="0.5"/>

                <!-- Plugin Buttons (dynamically added) -->
                <controls:NavIconButton Icon="🔌" ToolTip="Plugins"
                                       IsChecked="{x:Bind ViewModel.IsPluginPanelVisible, Mode=TwoWay}"/>
            </StackPanel>
        </Border>

        <!-- MAIN WORKSPACE (Row 1) -->
        <Grid Grid.Row="1" Grid.Column="1" Grid.ColumnSpan="3">
            <Grid.RowDefinitions>
                <RowDefinition Height="*"/>      <!-- Row 0: Main Panels -->
                <RowDefinition Height="0.18*"/>   <!-- Row 1: Bottom Deck (18%) -->
            </Grid.RowDefinitions>

            <!-- MAIN PANELS (Row 0) -->
            <Grid Grid.Row="0" Grid.Column="0">
                <Grid.ColumnDefinitions>
                    <ColumnDefinition Width="*"/>  <!-- Left Panel -->
                    <ColumnDefinition Width="*"/>  <!-- Center Panel -->
                    <ColumnDefinition Width="*"/>  <!-- Right Panel -->
                </Grid.ColumnDefinitions>

                <!-- Left Panel Host -->
                <controls:PanelHost x:Name="LeftPanelHost"
                                   Grid.Column="0"
                                   Margin="4,4,2,2"
                                   PanelRegion="Left"/>

                <!-- Center Panel Host -->
                <controls:PanelHost x:Name="CenterPanelHost"
                                   Grid.Column="1"
                                   Margin="2,4,2,2"
                                   PanelRegion="Center"/>

                <!-- Right Panel Host -->
                <controls:PanelHost x:Name="RightPanelHost"
                                   Grid.Column="2"
                                   Margin="2,4,4,2"
                                   PanelRegion="Right"/>
            </Grid>

            <!-- BOTTOM DECK (Row 1) -->
            <controls:PanelHost x:Name="BottomPanelHost"
                               Grid.Row="1" Grid.Column="0"
                               Margin="4,2,4,4"
                               PanelRegion="Bottom"/>
        </Grid>

        <!-- STATUS BAR (Row 2) -->
        <Border Grid.Row="2" Grid.Column="0" Grid.ColumnSpan="4"
                Height="26"
                Background="{StaticResource VSQ.Background.Tertiary}"
                BorderBrush="{StaticResource VSQ.Border.Primary}"
                BorderThickness="0,1,0,0">

            <Grid Margin="8,0">
                <Grid.ColumnDefinitions>
                    <ColumnDefinition Width="Auto"/>  <!-- Status Text -->
                    <ColumnDefinition Width="*"/>     <!-- Progress -->
                    <ColumnDefinition Width="Auto"/>  <!-- System Info -->
                </Grid.ColumnDefinitions>

                <!-- Status Message -->
                <TextBlock Grid.Column="0"
                          Text="{x:Bind ViewModel.StatusMessage, Mode=OneWay}"
                          Style="{StaticResource VSQ.Text.Status}"/>

                <!-- Progress Bar -->
                <ProgressBar Grid.Column="1"
                           Value="{x:Bind ViewModel.ProgressValue, Mode=OneWay}"
                           Visibility="{x:Bind ViewModel.IsProgressVisible, Mode=OneWay}"
                           Margin="16,0"
                           Height="4"
                           Style="{StaticResource VSQ.ProgressBar.Status}"/>

                <!-- System Status -->
                <StackPanel Grid.Column="2" Orientation="Horizontal" Spacing="16">
                    <TextBlock Text="{x:Bind ViewModel.BackendStatus, Mode=OneWay}"
                              Style="{StaticResource VSQ.Text.Status.Secondary}"/>
                    <TextBlock Text="{x:Bind ViewModel.MemoryUsage, Mode=OneWay}"
                              Style="{StaticResource VSQ.Text.Status.Secondary}"/>
                    <TextBlock Text="{x:Bind ViewModel.CpuUsage, Mode=OneWay}"
                              Style="{StaticResource VSQ.Text.Status.Secondary}"/>
                </StackPanel>
            </Grid>
        </Border>
    </Grid>
</Window>
```

---

## 🎨 DESIGN TOKENS SYSTEM - EMBEDDED

### Complete DesignTokens.xaml Implementation

```xaml
<ResourceDictionary
    xmlns="http://schemas.microsoft.com/winfx/2006/xaml/presentation"
    xmlns:x="http://schemas.microsoft.com/winfx/2006/xaml">

    <!-- ======================================== -->
    <!-- VOICESTUDIO QUANTUM+ DESIGN TOKEN SYSTEM -->
    <!-- ======================================== -->

    <!-- COLOR PALETTE -->
    <SolidColorBrush x:Key="VSQ.Background.Primary" Color="#1A1A1A"/>
    <SolidColorBrush x:Key="VSQ.Background.Secondary" Color="#2A2A2A"/>
    <SolidColorBrush x:Key="VSQ.Background.Tertiary" Color="#3A3A3A"/>
    <SolidColorBrush x:Key="VSQ.Background.Accent" Color="#4A4A4A"/>
    <SolidColorBrush x:Key="VSQ.Background.Highlight" Color="#5A5A5A"/>
    <SolidColorBrush x:Key="VSQ.Background.Success" Color="#2D5A2D"/>
    <SolidColorBrush x:Key="VSQ.Background.Warning" Color="#5A4A2D"/>
    <SolidColorBrush x:Key="VSQ.Background.Danger" Color="#5A2D2D"/>
    <SolidColorBrush x:Key="VSQ.Background.Info" Color="#2D4A5A"/>

    <!-- BORDER COLORS -->
    <SolidColorBrush x:Key="VSQ.Border.Primary" Color="#404040"/>
    <SolidColorBrush x:Key="VSQ.Border.Secondary" Color="#606060"/>
    <SolidColorBrush x:Key="VSQ.Border.Accent" Color="#808080"/>
    <SolidColorBrush x:Key="VSQ.Border.Success" Color="#4A8A4A"/>
    <SolidColorBrush x:Key="VSQ.Border.Warning" Color="#8A7A4A"/>
    <SolidColorBrush x:Key="VSQ.Border.Danger" Color="#8A4A4A"/>
    <SolidColorBrush x:Key="VSQ.Border.Info" Color="#4A7A8A"/>

    <!-- TEXT COLORS -->
    <SolidColorBrush x:Key="VSQ.Text.Primary" Color="#FFFFFF"/>
    <SolidColorBrush x:Key="VSQ.Text.Secondary" Color="#CCCCCC"/>
    <SolidColorBrush x:Key="VSQ.Text.Tertiary" Color="#AAAAAA"/>
    <SolidColorBrush x:Key="VSQ.Text.Disabled" Color="#666666"/>
    <SolidColorBrush x:Key="VSQ.Text.Success" Color="#7AC97A"/>
    <SolidColorBrush x:Key="VSQ.Text.Warning" Color="#C9C97A"/>
    <SolidColorBrush x:Key="VSQ.Text.Danger" Color="#C97A7A"/>
    <SolidColorBrush x:Key="VSQ.Text.Info" Color="#7AAFC9"/>
    <SolidColorBrush x:Key="VSQ.Text.Link" Color="#7AAFC9"/>
    <SolidColorBrush x:Key="VSQ.Text.Accent" Color="#C97AC9"/>

    <!-- TYPOGRAPHY -->
    <FontFamily x:Key="VSQ.Font.Primary">Segoe UI</FontFamily>
    <FontFamily x:Key="VSQ.Font.Mono">Consolas</FontFamily>
    <FontFamily x:Key="VSQ.Font.Title">Segoe UI Semibold</FontFamily>

    <x:Double x:Key="VSQ.Font.Size.XSmall">10</x:Double>
    <x:Double x:Key="VSQ.Font.Size.Small">11</x:Double>
    <x:Double x:Key="VSQ.Font.Size.Medium">12</x:Double>
    <x:Double x:Key="VSQ.Font.Size.Large">14</x:Double>
    <x:Double x:Key="VSQ.Font.Size.XLarge">16</x:Double>
    <x:Double x:Key="VSQ.Font.Size.XXLarge">18</x:Double>
    <x:Double x:Key="VSQ.Font.Size.Title">24</x:Double>

    <!-- SPACING -->
    <x:Double x:Key="VSQ.Spacing.XXSmall">2</x:Double>
    <x:Double x:Key="VSQ.Spacing.XSmall">4</x:Double>
    <x:Double x:Key="VSQ.Spacing.Small">8</x:Double>
    <x:Double x:Key="VSQ.Spacing.Medium">12</x:Double>
    <x:Double x:Key="VSQ.Spacing.Large">16</x:Double>
    <x:Double x:Key="VSQ.Spacing.XLarge">24</x:Double>
    <x:Double x:Key="VSQ.Spacing.XXLarge">32</x:Double>

    <!-- BORDER RADIUS -->
    <CornerRadius x:Key="VSQ.Radius.Small">2</CornerRadius>
    <CornerRadius x:Key="VSQ.Radius.Medium">4</CornerRadius>
    <CornerRadius x:Key="VSQ.Radius.Large">6</CornerRadius>
    <CornerRadius x:Key="VSQ.Radius.XLarge">8</CornerRadius>

    <!-- SHADOWS -->
    <x:String x:Key="VSQ.Shadow.Small">0 1 2 0 rgba(0,0,0,0.2)</x:String>
    <x:String x:Key="VSQ.Shadow.Medium">0 2 4 0 rgba(0,0,0,0.3)</x:String>
    <x:String x:Key="VSQ.Shadow.Large">0 4 8 0 rgba(0,0,0,0.4)</x:String>

    <!-- ======================================== -->
    <!-- COMPONENT STYLES -->
    <!-- ======================================== -->

    <!-- BUTTON STYLES -->
    <Style x:Key="VSQ.Button.Base" TargetType="Button">
        <Setter Property="Background" Value="{StaticResource VSQ.Background.Tertiary}"/>
        <Setter Property="Foreground" Value="{StaticResource VSQ.Text.Primary}"/>
        <Setter Property="BorderBrush" Value="{StaticResource VSQ.Border.Primary}"/>
        <Setter Property="BorderThickness" Value="1"/>
        <Setter Property="CornerRadius" Value="{StaticResource VSQ.Radius.Medium}"/>
        <Setter Property="FontFamily" Value="{StaticResource VSQ.Font.Primary}"/>
        <Setter Property="FontSize" Value="{StaticResource VSQ.Font.Size.Medium}"/>
        <Setter Property="Padding" Value="{StaticResource VSQ.Spacing.Medium},{StaticResource VSQ.Spacing.Small}"/>
        <Setter Property="Height" Value="32"/>
        <Setter Property="HorizontalAlignment" Value="Left"/>
        <Setter Property="VerticalAlignment" Value="Center"/>
        <Setter Property="Template">
            <Setter.Value>
                <ControlTemplate TargetType="Button">
                    <Border x:Name="RootBorder"
                            Background="{TemplateBinding Background}"
                            BorderBrush="{TemplateBinding BorderBrush}"
                            BorderThickness="{TemplateBinding BorderThickness}"
                            CornerRadius="{TemplateBinding CornerRadius}"
                            Padding="{TemplateBinding Padding}">

                        <ContentPresenter x:Name="ContentPresenter"
                                        Content="{TemplateBinding Content}"
                                        HorizontalAlignment="{TemplateBinding HorizontalContentAlignment}"
                                        VerticalAlignment="{TemplateBinding VerticalContentAlignment}"/>

                        <VisualStateManager.VisualStateGroups>
                            <VisualStateGroup x:Name="CommonStates">
                                <VisualState x:Name="Normal"/>
                                <VisualState x:Name="PointerOver">
                                    <Storyboard>
                                        <ObjectAnimationUsingKeyFrames Storyboard.TargetName="RootBorder"
                                                                     Storyboard.TargetProperty="Background">
                                            <DiscreteObjectKeyFrame KeyTime="0"
                                                                   Value="{StaticResource VSQ.Background.Highlight}"/>
                                        </ObjectAnimationUsingKeyFrames>
                                    </Storyboard>
                                </VisualState>
                                <VisualState x:Name="Pressed">
                                    <Storyboard>
                                        <ObjectAnimationUsingKeyFrames Storyboard.TargetName="RootBorder"
                                                                     Storyboard.TargetProperty="Background">
                                            <DiscreteObjectKeyFrame KeyTime="0"
                                                                   Value="{StaticResource VSQ.Background.Accent}"/>
                                        </ObjectAnimationUsingKeyFrames>
                                    </Storyboard>
                                </VisualState>
                                <VisualState x:Name="Disabled">
                                    <Storyboard>
                                        <ObjectAnimationUsingKeyFrames Storyboard.TargetName="RootBorder"
                                                                     Storyboard.TargetProperty="Foreground">
                                            <DiscreteObjectKeyFrame KeyTime="0"
                                                                   Value="{StaticResource VSQ.Text.Disabled}"/>
                                        </ObjectAnimationUsingKeyFrames>
                                    </Storyboard>
                                </VisualState>
                            </VisualStateGroup>
                        </VisualStateManager.VisualStateGroups>
                    </Border>
                </ControlTemplate>
            </Setter.Value>
        </Setter>
    </Style>

    <Style x:Key="VSQ.Button.Primary" TargetType="Button" BasedOn="{StaticResource VSQ.Button.Base}">
        <Setter Property="Background" Value="{StaticResource VSQ.Background.Accent}"/>
        <Setter Property="Foreground" Value="{StaticResource VSQ.Text.Primary}"/>
    </Style>

    <Style x:Key="VSQ.Button.Secondary" TargetType="Button" BasedOn="{StaticResource VSQ.Button.Base}">
        <Setter Property="Background" Value="Transparent"/>
        <Setter Property="BorderBrush" Value="{StaticResource VSQ.Border.Secondary}"/>
    </Style>

    <Style x:Key="VSQ.Button.Icon" TargetType="Button" BasedOn="{StaticResource VSQ.Button.Base}">
        <Setter Property="Width" Value="32"/>
        <Setter Property="Height" Value="32"/>
        <Setter Property="Padding" Value="0"/>
        <Setter Property="FontSize" Value="{StaticResource VSQ.Font.Size.Large}"/>
        <Setter Property="HorizontalContentAlignment" Value="Center"/>
        <Setter Property="VerticalContentAlignment" Value="Center"/>
    </Style>

    <Style x:Key="VSQ.Button.Icon.Danger" TargetType="Button" BasedOn="{StaticResource VSQ.Button.Icon}">
        <Setter Property="Background" Value="{StaticResource VSQ.Background.Danger}"/>
        <Setter Property="Foreground" Value="{StaticResource VSQ.Text.Danger}"/>
    </Style>

    <!-- TEXT STYLES -->
    <Style x:Key="VSQ.Text.Base" TargetType="TextBlock">
        <Setter Property="FontFamily" Value="{StaticResource VSQ.Font.Primary}"/>
        <Setter Property="Foreground" Value="{StaticResource VSQ.Text.Primary}"/>
    </Style>

    <Style x:Key="VSQ.Text.Header" TargetType="TextBlock" BasedOn="{StaticResource VSQ.Text.Base}">
        <Setter Property="FontSize" Value="{StaticResource VSQ.Font.Size.XXLarge}"/>
        <Setter Property="FontFamily" Value="{StaticResource VSQ.Font.Title}"/>
        <Setter Property="FontWeight" Value="SemiBold"/>
    </Style>

    <Style x:Key="VSQ.Text.Subtitle" TargetType="TextBlock" BasedOn="{StaticResource VSQ.Text.Base}">
        <Setter Property="FontSize" Value="{StaticResource VSQ.Font.Size.XLarge}"/>
        <Setter Property="FontWeight" Value="SemiBold"/>
    </Style>

    <Style x:Key="VSQ.Text.Body" TargetType="TextBlock" BasedOn="{StaticResource VSQ.Text.Base}">
        <Setter Property="FontSize" Value="{StaticResource VSQ.Font.Size.Medium}"/>
    </Style>

    <Style x:Key="VSQ.Text.Caption" TargetType="TextBlock" BasedOn="{StaticResource VSQ.Text.Base}">
        <Setter Property="FontSize" Value="{StaticResource VSQ.Font.Size.Small}"/>
        <Setter Property="Foreground" Value="{StaticResource VSQ.Text.Secondary}"/>
    </Style>

    <Style x:Key="VSQ.Text.Status" TargetType="TextBlock" BasedOn="{StaticResource VSQ.Text.Base}">
        <Setter Property="FontSize" Value="{StaticResource VSQ.Font.Size.Small}"/>
        <Setter Property="Foreground" Value="{StaticResource VSQ.Text.Secondary}"/>
        <Setter Property="VerticalAlignment" Value="Center"/>
    </Style>

    <Style x:Key="VSQ.Text.Status.Secondary" TargetType="TextBlock" BasedOn="{StaticResource VSQ.Text.Status}">
        <Setter Property="Foreground" Value="{StaticResource VSQ.Text.Tertiary}"/>
    </Style>

    <!-- INPUT STYLES -->
    <Style x:Key="VSQ.TextBox.Base" TargetType="TextBox">
        <Setter Property="Background" Value="{StaticResource VSQ.Background.Tertiary}"/>
        <Setter Property="Foreground" Value="{StaticResource VSQ.Text.Primary}"/>
        <Setter Property="BorderBrush" Value="{StaticResource VSQ.Border.Primary}"/>
        <Setter Property="BorderThickness" Value="1"/>
        <Setter Property="CornerRadius" Value="{StaticResource VSQ.Radius.Medium}"/>
        <Setter Property="FontFamily" Value="{StaticResource VSQ.Font.Primary}"/>
        <Setter Property="FontSize" Value="{StaticResource VSQ.Font.Size.Medium}"/>
        <Setter Property="Padding" Value="{StaticResource VSQ.Spacing.Medium}"/>
        <Setter Property="Height" Value="32"/>
    </Style>

    <!-- PROGRESS BAR STYLES -->
    <Style x:Key="VSQ.ProgressBar.Status" TargetType="ProgressBar">
        <Setter Property="Background" Value="{StaticResource VSQ.Background.Accent}"/>
        <Setter Property="Foreground" Value="{StaticResource VSQ.Background.Info}"/>
        <Setter Property="BorderBrush" Value="{StaticResource VSQ.Border.Secondary}"/>
        <Setter Property="BorderThickness" Value="1"/>
        <Setter Property="CornerRadius" Value="{StaticResource VSQ.Radius.Small}"/>
    </Style>

    <!-- PANEL STYLES -->
    <Style x:Key="VSQ.Panel.Base" TargetType="Border">
        <Setter Property="Background" Value="{StaticResource VSQ.Background.Secondary}"/>
        <Setter Property="BorderBrush" Value="{StaticResource VSQ.Border.Primary}"/>
        <Setter Property="BorderThickness" Value="1"/>
        <Setter Property="CornerRadius" Value="{StaticResource VSQ.Radius.Large}"/>
    </Style>

    <Style x:Key="VSQ.Panel.Header" TargetType="Border">
        <Setter Property="Background" Value="{StaticResource VSQ.Background.Tertiary}"/>
        <Setter Property="BorderBrush" Value="{StaticResource VSQ.Border.Secondary}"/>
        <Setter Property="BorderThickness" Value="0,0,0,1"/>
        <Setter Property="Height" Value="32"/>
        <Setter Property="Padding" Value="{StaticResource VSQ.Spacing.Medium}"/>
    </Style>

    <!-- LIST/GRID STYLES -->
    <Style x:Key="VSQ.ListView.Base" TargetType="ListView">
        <Setter Property="Background" Value="{StaticResource VSQ.Background.Secondary}"/>
        <Setter Property="BorderBrush" Value="{StaticResource VSQ.Border.Primary}"/>
        <Setter Property="BorderThickness" Value="1"/>
        <Setter Property="CornerRadius" Value="{StaticResource VSQ.Radius.Medium}"/>
        <Setter Property="Padding" Value="{StaticResource VSQ.Spacing.Small}"/>
    </Style>

    <Style x:Key="VSQ.ListViewItem.Base" TargetType="ListViewItem">
        <Setter Property="Background" Value="Transparent"/>
        <Setter Property="BorderBrush" Value="Transparent"/>
        <Setter Property="BorderThickness" Value="0"/>
        <Setter Property="Padding" Value="{StaticResource VSQ.Spacing.Small}"/>
        <Setter Property="Height" Value="32"/>
        <Setter Property="Template">
            <Setter.Value>
                <ControlTemplate TargetType="ListViewItem">
                    <Border x:Name="RootBorder"
                            Background="{TemplateBinding Background}"
                            BorderBrush="{TemplateBinding BorderBrush}"
                            BorderThickness="{TemplateBinding BorderThickness}"
                            CornerRadius="{StaticResource VSQ.Radius.Small}"
                            Padding="{TemplateBinding Padding}">

                        <ContentPresenter/>

                        <VisualStateManager.VisualStateGroups>
                            <VisualStateGroup x:Name="CommonStates">
                                <VisualState x:Name="Normal"/>
                                <VisualState x:Name="PointerOver">
                                    <Storyboard>
                                        <ObjectAnimationUsingKeyFrames Storyboard.TargetName="RootBorder"
                                                                     Storyboard.TargetProperty="Background">
                                            <DiscreteObjectKeyFrame KeyTime="0"
                                                                   Value="{StaticResource VSQ.Background.Highlight}"/>
                                        </ObjectAnimationUsingKeyFrames>
                                    </Storyboard>
                                </VisualState>
                                <VisualState x:Name="Selected">
                                    <Storyboard>
                                        <ObjectAnimationUsingKeyFrames Storyboard.TargetName="RootBorder"
                                                                     Storyboard.TargetProperty="Background">
                                            <DiscreteObjectKeyFrame KeyTime="0"
                                                                   Value="{StaticResource VSQ.Background.Accent}"/>
                                        </ObjectAnimationUsingKeyFrames>
                                    </Storyboard>
                                </VisualState>
                            </VisualStateGroup>
                        </VisualStateManager.VisualStateGroups>
                    </Border>
                </ControlTemplate>
            </Setter.Value>
        </Setter>
    </Style>

</ResourceDictionary>
```

---

## 🏗️ PANELHOST SYSTEM - EMBEDDED

### PanelHost.xaml - Complete UserControl Implementation

```xaml
<UserControl
    x:Class="VoiceStudio.App.Controls.PanelHost"
    xmlns="http://schemas.microsoft.com/winfx/2006/xaml/presentation"
    xmlns:x="http://schemas.microsoft.com/winfx/2006/xaml"
    xmlns:d="http://schemas.microsoft.com/expression/blend/2008"
    xmlns:mc="http://schemas.openxmlformats.org/markup-compatibility/2006"
    xmlns:local="using:VoiceStudio.App.Controls"
    mc:Ignorable="d"
    d:DesignHeight="400"
    d:DesignWidth="400">

    <Border Style="{StaticResource VSQ.Panel.Base}">
        <Grid>
            <Grid.RowDefinitions>
                <RowDefinition Height="32"/>  <!-- Header -->
                <RowDefinition Height="*"/>   <!-- Content -->
            </Grid.RowDefinitions>

            <!-- PANEL HEADER (32px fixed height) -->
            <Border Grid.Row="0" Style="{StaticResource VSQ.Panel.Header}">
                <Grid>
                    <Grid.ColumnDefinitions>
                        <ColumnDefinition Width="Auto"/>  <!-- Icon -->
                        <ColumnDefinition Width="*"/>     <!-- Title -->
                        <ColumnDefinition Width="Auto"/>  <!-- Controls -->
                    </Grid.ColumnDefinitions>

                    <!-- Panel Icon -->
                    <TextBlock Grid.Column="0"
                             x:Name="PanelIcon"
                             FontSize="{StaticResource VSQ.Font.Size.XLarge}"
                             VerticalAlignment="Center"
                             Margin="0,0,8,0"/>

                    <!-- Panel Title -->
                    <TextBlock Grid.Column="1"
                             x:Name="PanelTitle"
                             Style="{StaticResource VSQ.Text.Subtitle}"
                             VerticalAlignment="Center"/>

                    <!-- Panel Controls -->
                    <StackPanel Grid.Column="2"
                              Orientation="Horizontal"
                              Spacing="4"
                              VerticalAlignment="Center">

                        <!-- Minimize Button -->
                        <Button x:Name="MinimizeButton"
                               Content="−"
                               Style="{StaticResource VSQ.Button.Icon}"
                               ToolTipService.ToolTip="Minimize Panel"
                               Click="MinimizeButton_Click"/>

                        <!-- Maximize Button -->
                        <Button x:Name="MaximizeButton"
                               Content="□"
                               Style="{StaticResource VSQ.Button.Icon}"
                               ToolTipService.ToolTip="Maximize Panel"
                               Click="MaximizeButton_Click"/>

                        <!-- Close Button -->
                        <Button x:Name="CloseButton"
                               Content="×"
                               Style="{StaticResource VSQ.Button.Icon}"
                               ToolTipService.ToolTip="Close Panel"
                               Click="CloseButton_Click"/>
                    </StackPanel>
                </Grid>
            </Border>

            <!-- PANEL CONTENT AREA -->
            <ContentControl Grid.Row="1"
                          x:Name="PanelContent"
                          Margin="{StaticResource VSQ.Spacing.Medium}"/>

            <!-- LOADING OVERLAY -->
            <Border Grid.Row="0" Grid.RowSpan="2"
                   x:Name="LoadingOverlay"
                   Background="{StaticResource VSQ.Background.Primary}"
                   Opacity="0.8"
                   Visibility="Collapsed">

                <StackPanel VerticalAlignment="Center"
                           HorizontalAlignment="Center"
                           Spacing="8">

                    <ProgressRing IsActive="True"
                                Width="32"
                                Height="32"/>

                    <TextBlock Text="Loading..."
                             Style="{StaticResource VSQ.Text.Body}"
                             HorizontalAlignment="Center"/>
                </StackPanel>
            </Border>

            <!-- ERROR OVERLAY -->
            <Border Grid.Row="0" Grid.RowSpan="2"
                   x:Name="ErrorOverlay"
                   Background="{StaticResource VSQ.Background.Danger}"
                   Opacity="0.9"
                   Visibility="Collapsed">

                <StackPanel VerticalAlignment="Center"
                           HorizontalAlignment="Center"
                           Spacing="12"
                           MaxWidth="300">

                    <TextBlock Text="⚠️"
                             FontSize="32"
                             HorizontalAlignment="Center"/>

                    <TextBlock x:Name="ErrorTitle"
                             Text="Error Loading Panel"
                             Style="{StaticResource VSQ.Text.Subtitle}"
                             HorizontalAlignment="Center"/>

                    <TextBlock x:Name="ErrorMessage"
                             Text="An error occurred while loading this panel."
                             Style="{StaticResource VSQ.Text.Body}"
                             TextWrapping="Wrap"
                             HorizontalAlignment="Center"
                             TextAlignment="Center"/>

                    <Button x:Name="RetryButton"
                           Content="Retry"
                           Style="{StaticResource VSQ.Button.Primary}"
                           HorizontalAlignment="Center"
                           Click="RetryButton_Click"/>
                </StackPanel>
            </Border>
        </Grid>
    </Border>
</UserControl>
```

---

## 📋 PANEL REGISTRY SYSTEM - EMBEDDED

### IPanelView.cs - Panel Interface

```csharp
using System;
using System.Threading.Tasks;

namespace VoiceStudio.Core.Panels
{
    /// <summary>
    /// Interface for all panel ViewModels in VoiceStudio Quantum+
    /// </summary>
    public interface IPanelView
    {
        /// <summary>
        /// Gets the panel descriptor
        /// </summary>
        PanelDescriptor Descriptor { get; }

        /// <summary>
        /// Gets the panel region
        /// </summary>
        PanelRegion Region { get; }

        /// <summary>
        /// Called when the panel is activated/shown
        /// </summary>
        Task OnActivatedAsync();

        /// <summary>
        /// Called when the panel is deactivated/hidden
        /// </summary>
        Task OnDeactivatedAsync();

        /// <summary>
        /// Called when the panel should refresh its data
        /// </summary>
        Task RefreshAsync();

        /// <summary>
        /// Gets whether the panel can be closed
        /// </summary>
        bool CanClose { get; }

        /// <summary>
        /// Gets whether the panel has unsaved changes
        /// </summary>
        bool HasUnsavedChanges { get; }
    }
}
```

### PanelRegion.cs - Panel Regions Enum

```csharp
namespace VoiceStudio.Core.Panels
{
    /// <summary>
    /// Defines the regions where panels can be hosted
    /// </summary>
    public enum PanelRegion
    {
        /// <summary>
        /// Left panel area (20% width)
        /// </summary>
        Left,

        /// <summary>
        /// Center panel area (55% width)
        /// </summary>
        Center,

        /// <summary>
        /// Right panel area (25% width)
        /// </summary>
        Right,

        /// <summary>
        /// Bottom panel area (18% height, spans full width)
        /// </summary>
        Bottom
    }
}
```

### PanelDescriptor.cs - Panel Metadata

```csharp
using System;

namespace VoiceStudio.Core.Panels
{
    /// <summary>
    /// Metadata descriptor for a panel
    /// </summary>
    public class PanelDescriptor
    {
        /// <summary>
        /// Gets the unique panel ID
        /// </summary>
        public string Id { get; set; }

        /// <summary>
        /// Gets the display name
        /// </summary>
        public string Name { get; set; }

        /// <summary>
        /// Gets the panel description
        /// </summary>
        public string Description { get; set; }

        /// <summary>
        /// Gets the panel icon (emoji or symbol)
        /// </summary>
        public string Icon { get; set; }

        /// <summary>
        /// Gets the preferred region for this panel
        /// </summary>
        public PanelRegion PreferredRegion { get; set; }

        /// <summary>
        /// Gets whether this panel can be moved between regions
        /// </summary>
        public bool IsMovable { get; set; } = true;

        /// <summary>
        /// Gets whether this panel can be closed
        /// </summary>
        public bool IsClosable { get; set; } = true;

        /// <summary>
        /// Gets the panel priority (higher = more important)
        /// </summary>
        public int Priority { get; set; }

        /// <summary>
        /// Gets the panel category for organization
        /// </summary>
        public string Category { get; set; }

        /// <summary>
        /// Gets the ViewModel type for this panel
        /// </summary>
        public Type ViewModelType { get; set; }

        /// <summary>
        /// Gets the View type for this panel
        /// </summary>
        public Type ViewType { get; set; }
    }
}
```

---

**ALL UI DESIGN CONTENT EMBEDDED ABOVE - NO EXTERNAL REFERENCES**
