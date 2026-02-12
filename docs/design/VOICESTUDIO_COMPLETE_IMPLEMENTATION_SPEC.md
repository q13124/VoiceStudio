# VoiceStudio Quantum+ Complete Implementation Specification
## Professional DAW-Grade UI Implementation Guide

**Version:** 1.0  
**Date:** 2025  
**Target:** WinUI 3 (.NET 8) + Python FastAPI + MCP Integration

---

## 🚦 CRITICAL GUARDRAILS (Read First)

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

## 📁 Complete Project Structure

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
│   │   │   └── NavIconButton.xaml
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
│   │   │   ├── config.py
│   │   │   ├── plugin_manager.py
│   │   │   ├── schemas.py
│   │   │   └── audio_engine.py
│   ├── mcp_bridge/                      # MCP Integration (partial)
│   │   ├── pdf_unlocker_client.py       # Implemented
│   │   ├── mcp_client.py                # Future: unified MCP client
│   │   └── README.md
│   │   ├── api/
│   │   │   ├── profiles_api.py
│   │   │   ├── synthesis_api.py
│   │   │   ├── timeline_api.py
│   │   │   ├── effects_api.py
│   │   │   ├── analysis_api.py
│   │   │   ├── macros_api.py
│   │   │   └── diagnostics_api.py
│   │   ├── services/
│   │   │   ├── profile_service.py
│   │   │   ├── tts_service.py
│   │   │   ├── clone_service.py
│   │   │   ├── audio_service.py
│   │   │   ├── analysis_service.py
│   │   │   ├── macro_service.py
│   │   │   └── project_service.py
│   │   └── plugins/                  # Backend plugins
│   │       ├── carbon_voice/
│   │       │   ├── manifest.json
│   │       │   └── plugin.py
│   │       └── daisys_tts/
│   │           ├── manifest.json
│   │           └── plugin.py
├── shared/
│   └── contracts/                    # JSON schemas
│       ├── mcp_operation.schema.json
│       ├── analyze_voice_request.schema.json
│       └── layout_state.schema.json
└── docs/
    └── design/
```

---

## 🎨 Design Tokens (DesignTokens.xaml)

```xml
<ResourceDictionary
    xmlns="http://schemas.microsoft.com/winfx/2006/xaml/presentation"
    xmlns:x="http://schemas.microsoft.com/winfx/2006/xaml">

  <!-- Base colors -->
  <Color x:Key="VSQ.Background.Darker">#FF0A0F15</Color>
  <Color x:Key="VSQ.Background.Dark">#FF121A24</Color>
  <Color x:Key="VSQ.Accent.Cyan">#FF00B7C2</Color>
  <Color x:Key="VSQ.Accent.CyanGlow">#3030E0FF</Color>
  <Color x:Key="VSQ.Accent.Lime">#FF9AFF33</Color>
  <Color x:Key="VSQ.Accent.Magenta">#FFB040FF</Color>
  <Color x:Key="VSQ.Text.Primary">#FFCDD9E5</Color>
  <Color x:Key="VSQ.Text.Secondary">#FF8A9BB3</Color>
  <Color x:Key="VSQ.Border.Subtle">#26FFFFFF</Color>
  <Color x:Key="VSQ.Warn">#FFFFB540</Color>
  <Color x:Key="VSQ.Error">#FFFF4060</Color>

  <!-- Brushes -->
  <LinearGradientBrush x:Key="VSQ.Window.Background" StartPoint="0,0" EndPoint="0,1">
    <GradientStop Color="{StaticResource VSQ.Background.Darker}" Offset="0.0" />
    <GradientStop Color="{StaticResource VSQ.Background.Dark}" Offset="1.0" />
  </LinearGradientBrush>

  <SolidColorBrush x:Key="VSQ.Text.PrimaryBrush" Color="{StaticResource VSQ.Text.Primary}" />
  <SolidColorBrush x:Key="VSQ.Text.SecondaryBrush" Color="{StaticResource VSQ.Text.Secondary}" />
  <SolidColorBrush x:Key="VSQ.Accent.CyanBrush" Color="{StaticResource VSQ.Accent.Cyan}" />
  <SolidColorBrush x:Key="VSQ.Panel.BorderBrush" Color="{StaticResource VSQ.Border.Subtle}" />
  <SolidColorBrush x:Key="VSQ.Panel.BackgroundBrush" Color="#151921" />

  <!-- Typography sizes -->
  <x:Double x:Key="VSQ.FontSize.Caption">10</x:Double>
  <x:Double x:Key="VSQ.FontSize.Body">12</x:Double>
  <x:Double x:Key="VSQ.FontSize.Title">16</x:Double>
  <x:Double x:Key="VSQ.FontSize.Heading">20</x:Double>

  <!-- TextBlock styles -->
  <Style x:Key="VSQ.Text.Body" TargetType="TextBlock">
    <Setter Property="FontSize" Value="{StaticResource VSQ.FontSize.Body}"/>
    <Setter Property="Foreground" Value="{StaticResource VSQ.Text.PrimaryBrush}"/>
  </Style>
  <Style x:Key="VSQ.Text.Caption" TargetType="TextBlock">
    <Setter Property="FontSize" Value="{StaticResource VSQ.FontSize.Caption}"/>
    <Setter Property="Foreground" Value="{StaticResource VSQ.Text.SecondaryBrush}"/>
  </Style>
  <Style x:Key="VSQ.Text.Title" TargetType="TextBlock">
    <Setter Property="FontSize" Value="{StaticResource VSQ.FontSize.Title}"/>
    <Setter Property="Foreground" Value="{StaticResource VSQ.Text.PrimaryBrush}"/>
    <Setter Property="FontWeight" Value="SemiBold"/>
  </Style>
  <Style x:Key="VSQ.Text.Heading" TargetType="TextBlock">
    <Setter Property="FontSize" Value="{StaticResource VSQ.FontSize.Heading}"/>
    <Setter Property="Foreground" Value="{StaticResource VSQ.Text.PrimaryBrush}"/>
    <Setter Property="FontWeight" Value="Bold"/>
  </Style>

  <!-- Radius -->
  <x:Double x:Key="VSQ.CornerRadius.Panel">8</x:Double>
  <x:Double x:Key="VSQ.CornerRadius.Button">4</x:Double>

  <!-- Animation durations (ms) -->
  <x:Double x:Key="VSQ.Animation.Duration.Fast">100</x:Double>
  <x:Double x:Key="VSQ.Animation.Duration.Medium">150</x:Double>

</ResourceDictionary>
```

---

## 🪟 MainWindow.xaml (Complete Shell)

```xml
<Window
    x:Class="VoiceStudio.App.MainWindow"
    xmlns="http://schemas.microsoft.com/winfx/2006/xaml/presentation"
    xmlns:x="http://schemas.microsoft.com/winfx/2006/xaml"
    xmlns:local="using:VoiceStudio.App"
    xmlns:controls="using:VoiceStudio.App.Controls"
    xmlns:d="http://schemas.microsoft.com/expression/blend/2008"
    xmlns:mc="http://schemas.openxmlformats.org/markup-compatibility/2006"
    mc:Ignorable="d"
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

    <!-- =============================================== -->
    <!-- TOP COMMAND DECK (MENU + TOOLBAR)               -->
    <!-- =============================================== -->
    <Grid Grid.Row="0">
      <Grid.RowDefinitions>
        <RowDefinition Height="Auto"/>   <!-- MenuBar -->
        <RowDefinition Height="48"/>     <!-- Command Toolbar -->
      </Grid.RowDefinitions>

      <!-- MenuBar -->
      <MenuBar Grid.Row="0">
        <MenuBarItem Title="File">
          <MenuFlyoutItem Text="New Project"/>
          <MenuFlyoutItem Text="Open Project..."/>
          <MenuFlyoutItem Text="Save"/>
          <MenuFlyoutItem Text="Save As..."/>
          <MenuFlyoutSeparator/>
          <MenuFlyoutItem Text="Exit"/>
        </MenuBarItem>
        <MenuBarItem Title="Edit">
          <MenuFlyoutItem Text="Undo"/>
          <MenuFlyoutItem Text="Redo"/>
          <MenuFlyoutSeparator/>
          <MenuFlyoutItem Text="Cut"/>
          <MenuFlyoutItem Text="Copy"/>
          <MenuFlyoutItem Text="Paste"/>
        </MenuBarItem>
        <MenuBarItem Title="View">
          <MenuFlyoutItem Text="Reset Layout"/>
          <MenuFlyoutItem Text="Toggle Fullscreen Timeline"/>
        </MenuBarItem>
        <MenuBarItem Title="Modules">
          <MenuFlyoutItem Text="Studio"/>
          <MenuFlyoutItem Text="Profiles"/>
          <MenuFlyoutItem Text="Library"/>
          <MenuFlyoutItem Text="Effects"/>
          <MenuFlyoutItem Text="Train"/>
          <MenuFlyoutItem Text="Analyze"/>
        </MenuBarItem>
        <MenuBarItem Title="Playback">
          <MenuFlyoutItem Text="Play"/>
          <MenuFlyoutItem Text="Stop"/>
          <MenuFlyoutItem Text="Record"/>
        </MenuBarItem>
        <MenuBarItem Title="Tools">
          <MenuFlyoutItem Text="Macros"/>
          <MenuFlyoutItem Text="Batch Processor"/>
        </MenuBarItem>
        <MenuBarItem Title="AI">
          <MenuFlyoutItem Text="Suggest Chain"/>
          <MenuFlyoutItem Text="Analyze Voice"/>
        </MenuBarItem>
        <MenuBarItem Title="Help">
          <MenuFlyoutItem Text="Documentation"/>
          <MenuFlyoutItem Text="About VoiceStudio Quantum+"/>
        </MenuBarItem>
      </MenuBar>

      <!-- Command Toolbar -->
      <Grid Grid.Row="1" Margin="8,0,8,4">
        <Grid.ColumnDefinitions>
          <ColumnDefinition Width="Auto"/>
          <ColumnDefinition Width="Auto"/>
          <ColumnDefinition Width="*"/>
          <ColumnDefinition Width="Auto"/>
        </Grid.ColumnDefinitions>

        <!-- Transport -->
        <StackPanel Grid.Column="0" Orientation="Horizontal"
                    VerticalAlignment="Center">
          <Button Content="▶" Margin="0,0,4,0"/>
          <Button Content="⏸" Margin="0,0,4,0"/>
          <Button Content="⏹" Margin="0,0,4,0"/>
          <Button Content="⏺" Margin="0,0,4,0"/>
          <ToggleButton Content="Loop" Margin="8,0,0,0"/>
        </StackPanel>

        <!-- Project & Engine -->
        <StackPanel Grid.Column="1" Orientation="Horizontal"
                    VerticalAlignment="Center" Margin="24,0,0,0">
          <TextBlock Text="Project:" Margin="0,0,4,0"/>
          <TextBox Width="200" Text="Untitled Project"/>
          <TextBlock Text="Engine:" Margin="16,0,4,0"/>
          <ComboBox Width="140">
            <ComboBoxItem Content="XTTS v2"/>
            <ComboBoxItem Content="OpenVoice"/>
            <ComboBoxItem Content="RVC"/>
          </ComboBox>
        </StackPanel>

        <!-- Undo/Redo & Workspace -->
        <StackPanel Grid.Column="2" Orientation="Horizontal"
                    VerticalAlignment="Center" HorizontalAlignment="Left"
                    Margin="32,0,0,0">
          <Button Content="Undo" Margin="0,0,4,0"/>
          <Button Content="Redo" Margin="0,0,12,0"/>
          <TextBlock Text="Workspace:" Margin="0,0,4,0"/>
          <ComboBox Width="150">
            <ComboBoxItem Content="Studio"/>
            <ComboBoxItem Content="Batch Lab"/>
            <ComboBoxItem Content="Training"/>
            <ComboBoxItem Content="Pro Mix"/>
          </ComboBox>
        </StackPanel>

        <!-- Performance HUD -->
        <StackPanel Grid.Column="3" Orientation="Horizontal"
                    HorizontalAlignment="Right" VerticalAlignment="Center">
          <StackPanel Margin="0,0,12,0">
            <TextBlock Text="CPU" FontSize="10"
                       HorizontalAlignment="Right"/>
            <ProgressBar Width="80" Height="6" Value="20"/>
          </StackPanel>
          <StackPanel Margin="0,0,12,0">
            <TextBlock Text="GPU" FontSize="10"
                       HorizontalAlignment="Right"/>
            <ProgressBar Width="80" Height="6" Value="10"/>
          </StackPanel>
          <StackPanel>
            <TextBlock Text="Latency" FontSize="10"
                       HorizontalAlignment="Right"/>
            <ProgressBar Width="80" Height="6" Value="5"/>
          </StackPanel>
        </StackPanel>
      </Grid>
    </Grid>

    <!-- =============================================== -->
    <!-- MAIN WORKSPACE (NAV + 3 HOSTS + BOTTOM HOST)   -->
    <!-- =============================================== -->
    <Grid Grid.Row="1" Margin="8,0,8,4">
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

      <!-- Nav rail -->
      <Border Grid.Row="0" Grid.Column="0"
              Grid.RowSpan="2"
              Background="#141820"
              CornerRadius="8"
              Padding="4">
        <StackPanel HorizontalAlignment="Center"
                    VerticalAlignment="Top"
                    Margin="0,8,0,8"
                    Spacing="8">
          <ToggleButton Content="🎛" ToolTipService.ToolTip="Studio"
                        Width="40" Height="40" Margin="0,0,0,4"/>
          <ToggleButton Content="👤" ToolTipService.ToolTip="Profiles"
                        Width="40" Height="40" Margin="0,0,0,4"/>
          <ToggleButton Content="📁" ToolTipService.ToolTip="Library"
                        Width="40" Height="40" Margin="0,0,0,4"/>
          <ToggleButton Content="🎚" ToolTipService.ToolTip="Effects"
                        Width="40" Height="40" Margin="0,0,0,4"/>
          <ToggleButton Content="🧠" ToolTipService.ToolTip="Train"
                        Width="40" Height="40" Margin="0,0,0,4"/>
          <ToggleButton Content="📊" ToolTipService.ToolTip="Analyze"
                        Width="40" Height="40" Margin="0,0,0,4"/>
          <ToggleButton Content="⚙" ToolTipService.ToolTip="Settings"
                        Width="40" Height="40" Margin="0,0,0,4"/>
          <ToggleButton Content="🧾" ToolTipService.ToolTip="Logs"
                        Width="40" Height="40" Margin="0,0,0,4"/>
        </StackPanel>
      </Border>

      <!-- Left PanelHost -->
      <controls:PanelHost Grid.Row="0"
                          Grid.Column="1"
                          Margin="4,0,4,4"
                          x:Name="LeftPanelHost"/>

      <!-- Center PanelHost -->
      <controls:PanelHost Grid.Row="0"
                          Grid.Column="2"
                          Margin="0,0,4,4"
                          x:Name="CenterPanelHost"/>

      <!-- Right PanelHost -->
      <controls:PanelHost Grid.Row="0"
                          Grid.Column="3"
                          Margin="0,0,0,4"
                          x:Name="RightPanelHost"/>

      <!-- Bottom PanelHost -->
      <controls:PanelHost Grid.Row="1"
                          Grid.Column="0"
                          Grid.ColumnSpan="4"
                          x:Name="BottomPanelHost"/>
    </Grid>

    <!-- =============================================== -->
    <!-- STATUS BAR                                      -->
    <!-- =============================================== -->
    <Border Grid.Row="2" Height="26"
            Background="#141820"
            BorderBrush="{StaticResource VSQ.Panel.BorderBrush}"
            BorderThickness="1,1,1,0">
      <Grid Margin="8,0,8,0">
        <Grid.ColumnDefinitions>
          <ColumnDefinition Width="*"/>
          <ColumnDefinition Width="2*"/>
          <ColumnDefinition Width="*"/>
        </Grid.ColumnDefinitions>

        <!-- Left -->
        <TextBlock Grid.Column="0"
                   Text="Ready"
                   VerticalAlignment="Center"/>

        <!-- Center -->
        <StackPanel Grid.Column="1" Orientation="Horizontal"
                    VerticalAlignment="Center" HorizontalAlignment="Center">
          <TextBlock Text="Job:" Margin="0,0,4,0"/>
          <TextBlock Text="Idle"/>
          <ProgressBar Width="200" Height="6"
                       Margin="12,0,0,0"
                       Value="0"/>
        </StackPanel>

        <!-- Right -->
        <StackPanel Grid.Column="2" Orientation="Horizontal"
                    HorizontalAlignment="Right" VerticalAlignment="Center">
          <TextBlock Text="CPU 12%" FontSize="10" Margin="0,0,12,0"/>
          <TextBlock Text="GPU 4%" FontSize="10" Margin="0,0,12,0"/>
          <TextBlock Text="RAM 26%" FontSize="10" Margin="0,0,12,0"/>
          <TextBlock Text="21:34" FontSize="10"/>
        </StackPanel>
      </Grid>
    </Border>
  </Grid>
</Window>
```

---

## 🎛️ PanelHost Control

**PanelHost.xaml:**
```xml
<UserControl x:Class="VoiceStudio.App.Controls.PanelHost"
             xmlns="http://schemas.microsoft.com/winfx/2006/xaml/presentation"
             xmlns:x="http://schemas.microsoft.com/winfx/2006/xaml">
  <Grid>
    <Grid.RowDefinitions>
      <RowDefinition Height="32"/> <!-- Header -->
      <RowDefinition Height="*"/>  <!-- Body -->
    </Grid.RowDefinitions>

    <!-- Header bar -->
    <Border Grid.Row="0"
            Background="#181D26"
            CornerRadius="8,8,0,0"
            Padding="8,0,8,0">
      <Grid>
        <Grid.ColumnDefinitions>
          <ColumnDefinition Width="Auto"/>
          <ColumnDefinition Width="*"/>
          <ColumnDefinition Width="Auto"/>
        </Grid.ColumnDefinitions>

        <TextBlock Grid.Column="0"
                   Text="Panel"
                   VerticalAlignment="Center"
                   Style="{StaticResource VSQ.Text.Body}"/>

        <TextBlock Grid.Column="1"
                   HorizontalAlignment="Center"
                   VerticalAlignment="Center"
                   Text="" />

        <!-- Actions -->
        <StackPanel Grid.Column="2"
                    Orientation="Horizontal"
                    VerticalAlignment="Center">
          <Button Content="▢" Width="24" Height="24" Margin="0,0,4,0"/>
          <Button Content="–" Width="24" Height="24"/>
        </StackPanel>
      </Grid>
    </Border>

    <!-- Body -->
    <Border Grid.Row="1"
            CornerRadius="0,0,8,8"
            Background="{StaticResource VSQ.Panel.BackgroundBrush}"
            BorderBrush="{StaticResource VSQ.Panel.BorderBrush}"
            BorderThickness="1">
      <ContentPresenter Content="{Binding Content, RelativeSource={RelativeSource Mode=TemplatedParent}}"/>
    </Border>
  </Grid>
</UserControl>
```

**PanelHost.xaml.cs:**
```csharp
using Microsoft.UI.Xaml.Controls;
using Microsoft.UI.Xaml;

namespace VoiceStudio.App.Controls
{
    public sealed partial class PanelHost : UserControl
    {
        public static readonly DependencyProperty ContentProperty =
            DependencyProperty.Register(nameof(Content), typeof(object), typeof(PanelHost), new PropertyMetadata(null));

        public object Content
        {
            get => GetValue(ContentProperty);
            set => SetValue(ContentProperty, value);
        }

        public PanelHost()
        {
            this.InitializeComponent();
        }
    }
}
```

---

## 📊 Core Panel XAML Skeletons

### ProfilesView.xaml
```xml
<UserControl x:Class="VoiceStudio.App.Views.Panels.ProfilesView"
             xmlns="http://schemas.microsoft.com/winfx/2006/xaml/presentation"
             xmlns:x="http://schemas.microsoft.com/winfx/2006/xaml">
  <Grid>
    <Grid.RowDefinitions>
      <RowDefinition Height="32"/>
      <RowDefinition Height="*"/>
    </Grid.RowDefinitions>

    <StackPanel Grid.Row="0" Orientation="Horizontal" VerticalAlignment="Center" Margin="8,0">
      <ToggleButton Content="Profiles" Margin="0,0,8,0" IsChecked="True"/>
      <ToggleButton Content="Library"/>
    </StackPanel>

    <Grid Grid.Row="1">
      <Grid.ColumnDefinitions>
        <ColumnDefinition Width="*"/>
        <ColumnDefinition Width="260"/>
      </Grid.ColumnDefinitions>

      <ScrollViewer Grid.Column="0">
        <ItemsControl>
          <ItemsControl.ItemsPanel>
            <ItemsPanelTemplate>
              <WrapGrid Orientation="Horizontal" ItemWidth="180" ItemHeight="120"/>
            </ItemsPanelTemplate>
          </ItemsControl.ItemsPanel>
          <ItemsControl.ItemTemplate>
            <DataTemplate>
              <Border CornerRadius="8" Margin="8" BorderBrush="{StaticResource VSQ.Panel.BorderBrush}" BorderThickness="1">
                <StackPanel Margin="8">
                  <Rectangle Height="40" Fill="#333"/>
                  <TextBlock Text="Profile Name" Margin="0,6,0,0"/>
                  <TextBlock Text="Tags / Language" Foreground="{StaticResource VSQ.Text.SecondaryBrush}"/>
                </StackPanel>
              </Border>
            </DataTemplate>
          </ItemsControl.ItemTemplate>
        </ItemsControl>
      </ScrollViewer>

      <Border Grid.Column="1" Margin="8,0,0,0" CornerRadius="8" BorderBrush="{StaticResource VSQ.Panel.BorderBrush}" BorderThickness="1">
        <StackPanel Margin="8">
          <TextBlock Text="Profile Details" FontSize="16"/>
          <Rectangle Height="60" Margin="0,8,0,8" Fill="#222"/>
          <TextBlock Text="Language: "/>
          <TextBlock Text="Emotion: "/>
          <TextBlock Text="Quality Score: "/>
        </StackPanel>
      </Border>
    </Grid>
  </Grid>
</UserControl>
```

### TimelineView.xaml
```xml
<UserControl x:Class="VoiceStudio.App.Views.Panels.TimelineView"
             xmlns="http://schemas.microsoft.com/winfx/2006/xaml/presentation"
             xmlns:x="http://schemas.microsoft.com/winfx/2006/xaml">
  <Grid>
    <Grid.RowDefinitions>
      <RowDefinition Height="32"/>
      <RowDefinition Height="*"/>
      <RowDefinition Height="160"/>
    </Grid.RowDefinitions>

    <StackPanel Grid.Row="0" Orientation="Horizontal" VerticalAlignment="Center" Margin="8,0">
      <Button Content="Add Track" Margin="0,0,8,0"/>
      <Button Content="Zoom In" Margin="0,0,4,0"/>
      <Button Content="Zoom Out"/>
      <TextBlock Text="Grid: 1/16" Margin="16,0,0,0"/>
    </StackPanel>

    <ScrollViewer Grid.Row="1">
      <ItemsControl>
        <ItemsControl.ItemTemplate>
          <DataTemplate>
            <Grid Margin="4">
              <Grid.ColumnDefinitions>
                <ColumnDefinition Width="180"/>
                <ColumnDefinition Width="*"/>
              </Grid.ColumnDefinitions>
              <StackPanel Grid.Column="0" Margin="4" Background="#20252E" Padding="4">
                <TextBlock Text="Track 1"/>
                <TextBlock Text="Engine: XTTS" FontSize="10"/>
              </StackPanel>
              <Border Grid.Column="1" Height="48" CornerRadius="4" Background="#151921" BorderBrush="{StaticResource VSQ.Panel.BorderBrush}" BorderThickness="1">
                <!-- waveform placeholder -->
              </Border>
            </Grid>
          </DataTemplate>
        </ItemsControl.ItemTemplate>
      </ItemsControl>
    </ScrollViewer>

    <Border Grid.Row="2" Margin="0,4,0,0" CornerRadius="8" BorderBrush="{StaticResource VSQ.Panel.BorderBrush}" BorderThickness="1">
      <Grid>
        <TextBlock Text="Spectrogram / Orbs Visualizer" HorizontalAlignment="Center" VerticalAlignment="Center" Opacity="0.6"/>
      </Grid>
    </Border>
  </Grid>
</UserControl>
```

### EffectsMixerView.xaml
```xml
<UserControl x:Class="VoiceStudio.App.Views.Panels.EffectsMixerView"
             xmlns="http://schemas.microsoft.com/winfx/2006/xaml/presentation"
             xmlns:x="http://schemas.microsoft.com/winfx/2006/xaml">
  <Grid>
    <Grid.RowDefinitions>
      <RowDefinition Height="*"/>
      <RowDefinition Height="0.4*"/>
    </Grid.RowDefinitions>

    <ScrollViewer Grid.Row="0" HorizontalScrollBarVisibility="Auto">
      <ItemsControl>
        <ItemsControl.ItemsPanel>
          <ItemsPanelTemplate>
            <StackPanel Orientation="Horizontal"/>
          </ItemsPanelTemplate>
        </ItemsControl.ItemsPanel>
        <ItemsControl.ItemTemplate>
          <DataTemplate>
            <StackPanel Margin="4" Width="80">
              <TextBlock Text="Ch 1" HorizontalAlignment="Center"/>
              <Border Margin="0,4" Height="140" CornerRadius="8" Background="#151921" BorderBrush="{StaticResource VSQ.Panel.BorderBrush}" BorderThickness="1">
                <Rectangle Width="20" Height="60" Fill="{StaticResource VSQ.Accent.CyanBrush}" HorizontalAlignment="Center" VerticalAlignment="Center"/>
              </Border>
              <StackPanel Margin="0,4,0,0">
                <TextBlock Text="EQ" FontSize="10"/>
                <TextBlock Text="Comp" FontSize="10"/>
                <TextBlock Text="Reverb" FontSize="10"/>
              </StackPanel>
            </StackPanel>
          </DataTemplate>
        </ItemsControl.ItemTemplate>
      </ItemsControl>
    </ScrollViewer>

    <Border Grid.Row="1" Margin="0,4,0,0" CornerRadius="8" BorderBrush="{StaticResource VSQ.Panel.BorderBrush}" BorderThickness="1">
      <Grid>
        <TextBlock Text="FX Chain / Node View" HorizontalAlignment="Center" VerticalAlignment="Center" Opacity="0.6"/>
      </Grid>
    </Border>
  </Grid>
</UserControl>
```

### AnalyzerView.xaml
```xml
<UserControl x:Class="VoiceStudio.App.Views.Panels.AnalyzerView"
             xmlns="http://schemas.microsoft.com/winfx/2006/xaml/presentation"
             xmlns:x="http://schemas.microsoft.com/winfx/2006/xaml"
             xmlns:muxc="using:Microsoft.UI.Xaml.Controls">
  <Grid>
    <Grid.RowDefinitions>
      <RowDefinition Height="32"/>
      <RowDefinition Height="*"/>
    </Grid.RowDefinitions>

    <muxc:TabView Grid.Row="0">
      <muxc:TabViewItem Header="Waveform"/>
      <muxc:TabViewItem Header="Spectral"/>
      <muxc:TabViewItem Header="Radar"/>
      <muxc:TabViewItem Header="Loudness"/>
      <muxc:TabViewItem Header="Phase"/>
    </muxc:TabView>

    <Border Grid.Row="1" Margin="0,4,0,0" CornerRadius="8" BorderBrush="{StaticResource VSQ.Panel.BorderBrush}" BorderThickness="1">
      <Grid>
        <TextBlock Text="Analyzer Chart Placeholder" HorizontalAlignment="Center" VerticalAlignment="Center" Opacity="0.6"/>
      </Grid>
    </Border>
  </Grid>
</UserControl>
```

### MacroView.xaml
```xml
<UserControl x:Class="VoiceStudio.App.Views.Panels.MacroView"
             xmlns="http://schemas.microsoft.com/winfx/2006/xaml/presentation"
             xmlns:x="http://schemas.microsoft.com/winfx/2006/xaml">
  <Grid>
    <Grid.RowDefinitions>
      <RowDefinition Height="32"/>
      <RowDefinition Height="*"/>
    </Grid.RowDefinitions>

    <StackPanel Grid.Row="0" Orientation="Horizontal" VerticalAlignment="Center" Margin="8,0">
      <ToggleButton Content="Macros" IsChecked="True" Margin="0,0,8,0"/>
      <ToggleButton Content="Automation"/>
    </StackPanel>

    <Border Grid.Row="1" Margin="0,4,0,0" CornerRadius="8" BorderBrush="{StaticResource VSQ.Panel.BorderBrush}" BorderThickness="1">
      <Grid>
        <TextBlock Text="Macro / Automation Node Graph" HorizontalAlignment="Center" VerticalAlignment="Center" Opacity="0.6"/>
      </Grid>
    </Border>
  </Grid>
</UserControl>
```

### DiagnosticsView.xaml
```xml
<UserControl x:Class="VoiceStudio.App.Views.Panels.DiagnosticsView"
             xmlns="http://schemas.microsoft.com/winfx/2006/xaml/presentation"
             xmlns:x="http://schemas.microsoft.com/winfx/2006/xaml">
  <Grid>
    <Grid.RowDefinitions>
      <RowDefinition Height="0.6*"/>
      <RowDefinition Height="0.4*"/>
    </Grid.RowDefinitions>

    <Border Grid.Row="0" CornerRadius="8" BorderBrush="{StaticResource VSQ.Panel.BorderBrush}" BorderThickness="1">
      <Grid>
        <ListView>
          <ListView.ItemTemplate>
            <DataTemplate>
              <StackPanel Orientation="Horizontal" Margin="2">
                <TextBlock Text="[INFO]" Margin="0,0,6,0"/>
                <TextBlock Text="Sample log line"/>
              </StackPanel>
            </DataTemplate>
          </ListView.ItemTemplate>
        </ListView>
      </Grid>
    </Border>

    <Border Grid.Row="1" Margin="0,4,0,0" CornerRadius="8" BorderBrush="{StaticResource VSQ.Panel.BorderBrush}" BorderThickness="1">
      <Grid>
        <StackPanel Orientation="Horizontal" HorizontalAlignment="Center" VerticalAlignment="Center">
          <StackPanel Margin="0,0,24,0">
            <TextBlock Text="CPU" HorizontalAlignment="Center"/>
            <ProgressBar Width="160" Height="6" Value="25"/>
          </StackPanel>
          <StackPanel Margin="0,0,24,0">
            <TextBlock Text="GPU" HorizontalAlignment="Center"/>
            <ProgressBar Width="160" Height="6" Value="10"/>
          </StackPanel>
          <StackPanel>
            <TextBlock Text="RAM" HorizontalAlignment="Center"/>
            <ProgressBar Width="160" Height="6" Value="40"/>
          </StackPanel>
        </StackPanel>
      </Grid>
    </Border>
  </Grid>
</UserControl>
```

---

## 🔌 Panel Registry System

### PanelRegion.cs
```csharp
namespace VoiceStudio.Core.Panels
{
    public enum PanelRegion
    {
        Left,
        Center,
        Right,
        Bottom,
        Floating
    }
}
```

### IPanelView.cs
```csharp
namespace VoiceStudio.Core.Panels
{
    public interface IPanelView
    {
        string PanelId { get; }
        string DisplayName { get; }
        PanelRegion Region { get; }
    }
}
```

### PanelDescriptor.cs
```csharp
namespace VoiceStudio.Core.Panels
{
    public sealed class PanelDescriptor
    {
        public string PanelId { get; init; } = string.Empty;
        public string DisplayName { get; init; } = string.Empty;
        public PanelRegion Region { get; init; }
        public Type ViewType { get; init; } = typeof(object);
        public Type ViewModelType { get; init; } = typeof(object);
    }
}
```

### IPanelRegistry.cs & PanelRegistry.cs
```csharp
namespace VoiceStudio.Core.Panels
{
    public interface IPanelRegistry
    {
        IEnumerable<PanelDescriptor> GetPanelsForRegion(PanelRegion region);
        PanelDescriptor? GetDefaultPanel(PanelRegion region);
    }

    public class PanelRegistry : IPanelRegistry
    {
        private readonly List<PanelDescriptor> _panels = new();

        public PanelRegistry()
        {
            // Register core panels
            _panels.Add(new PanelDescriptor
            {
                PanelId = "profiles",
                DisplayName = "Profiles",
                Region = PanelRegion.Left,
                ViewType = typeof(VoiceStudio.App.Views.Panels.ProfilesView),
                ViewModelType = typeof(VoiceStudio.App.ViewModels.Panels.ProfilesViewModel)
            });

            _panels.Add(new PanelDescriptor
            {
                PanelId = "timeline",
                DisplayName = "Timeline",
                Region = PanelRegion.Center,
                ViewType = typeof(VoiceStudio.App.Views.Panels.TimelineView),
                ViewModelType = typeof(VoiceStudio.App.ViewModels.Panels.TimelineViewModel)
            });

            _panels.Add(new PanelDescriptor
            {
                PanelId = "effectsmixer",
                DisplayName = "Effects Mixer",
                Region = PanelRegion.Right,
                ViewType = typeof(VoiceStudio.App.Views.Panels.EffectsMixerView),
                ViewModelType = typeof(VoiceStudio.App.ViewModels.Panels.EffectsMixerViewModel)
            });

            _panels.Add(new PanelDescriptor
            {
                PanelId = "analyzer",
                DisplayName = "Analyzer",
                Region = PanelRegion.Right,
                ViewType = typeof(VoiceStudio.App.Views.Panels.AnalyzerView),
                ViewModelType = typeof(VoiceStudio.App.ViewModels.Panels.AnalyzerViewModel)
            });

            _panels.Add(new PanelDescriptor
            {
                PanelId = "macro",
                DisplayName = "Macro",
                Region = PanelRegion.Bottom,
                ViewType = typeof(VoiceStudio.App.Views.Panels.MacroView),
                ViewModelType = typeof(VoiceStudio.App.ViewModels.Panels.MacroViewModel)
            });

            _panels.Add(new PanelDescriptor
            {
                PanelId = "diagnostics",
                DisplayName = "Diagnostics",
                Region = PanelRegion.Bottom,
                ViewType = typeof(VoiceStudio.App.Views.Panels.DiagnosticsView),
                ViewModelType = typeof(VoiceStudio.App.ViewModels.Panels.DiagnosticsViewModel)
            });
        }

        public IEnumerable<PanelDescriptor> GetPanelsForRegion(PanelRegion region)
        {
            return _panels.Where(p => p.Region == region);
        }

        public PanelDescriptor? GetDefaultPanel(PanelRegion region)
        {
            return _panels.FirstOrDefault(p => p.Region == region);
        }
    }
}
```

---

## 🔗 MCP Integration Hooks

> **Note:** MCP integration is currently limited to PDF unlock functionality. Full MCP integration
> for design tokens, AI model calls, and voice engines is planned for future releases. The
> structure below represents the target architecture.

### Current MCP Structure (Implemented)

**backend/mcp_bridge/** (actual location):
- `pdf_unlocker_client.py` - PDF unlock MCP client (implemented)
- `README.md` - MCP bridge documentation

### Target MCP Client Structure (Future)

**backend/mcp_bridge/mcp_client.py** (target path for future implementation):
```python
from typing import Dict, Any, Optional
import httpx
import asyncio

class MCPClient:
    """Unified MCP server client for VoiceStudio (Future Implementation)"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.clients = {}
    
    async def call_mcp_operation(
        self,
        operation: str,
        payload: Dict[str, Any],
        server: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Route MCP operation to appropriate server
        
        Target Operations:
        - analyze_voice -> TTS/analysis MCP
        - synthesize -> Voice cloning MCP (carbon-voice, daisys-tts)
        - transcribe -> Whisper MCP
        - suggest_chain -> AI suggestion MCP
        """
        # Route based on operation type
        if operation == "analyze_voice":
            return await self._call_analysis_mcp(payload)
        elif operation == "synthesize":
            return await self._call_synthesis_mcp(payload, server)
        elif operation == "transcribe":
            return await self._call_transcribe_mcp(payload)
        elif operation == "suggest_chain":
            return await self._call_ai_mcp(payload)
        else:
            raise ValueError(f"Unknown operation: {operation}")
    
    async def _call_analysis_mcp(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        # Implementation for voice analysis
        pass
    
    async def _call_synthesis_mcp(self, payload: Dict[str, Any], server: str) -> Dict[str, Any]:
        # Implementation for voice synthesis
        pass
    
    async def _call_transcribe_mcp(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        # Implementation for transcription
        pass
    
    async def _call_ai_mcp(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        # Implementation for AI suggestions
        pass
```

### MCP Message Schemas

**shared/contracts/mcp_operation.schema.json:**
```json
{
  "title": "McpOperationRequest",
  "type": "object",
  "properties": {
    "requestId": {
      "type": "string"
    },
    "operation": {
      "type": "string",
      "enum": ["analyze_voice", "synthesize", "transcribe", "suggest_chain"]
    },
    "source": {
      "type": "string",
      "enum": ["ui", "batch", "training"]
    },
    "payload": {
      "type": "object"
    }
  },
  "required": ["requestId", "operation", "payload"]
}
```

**shared/contracts/analyze_voice_request.schema.json:**
```json
{
  "title": "AnalyzeVoiceRequest",
  "type": "object",
  "properties": {
    "profileId": {
      "type": "string"
    },
    "clipId": {
      "type": "string"
    },
    "analysisModes": {
      "type": "array",
      "items": {
        "type": "string",
        "enum": ["lufs", "timbre", "similarity", "pitch", "spectral"]
      }
    }
  },
  "required": ["profileId", "clipId"]
}
```

### Backend API Endpoints (MCP Integration - Target)

> **Note:** The following shows the target API structure for full MCP integration (future work).

**backend/api/routes/analysis.py** (target structure):
```python
from fastapi import APIRouter, HTTPException
from backend.mcp_bridge.mcp_client import MCPClient  # Target import path
from backend.api.models import AnalyzeVoiceRequest, AnalyzeVoiceResponse

router = APIRouter()

@router.post("/api/voices/analyze")
async def analyze_voice(request: AnalyzeVoiceRequest):
    """
    Analyze voice using MCP analysis server (future implementation)
    """
    mcp_client = MCPClient(config)
    result = await mcp_client.call_mcp_operation(
        operation="analyze_voice",
        payload={
            "profileId": request.profileId,
            "clipId": request.clipId,
            "modes": request.analysisModes
        }
    )
    return AnalyzeVoiceResponse(**result)
```

---

## 🔌 Plugin System Architecture

### Plugin Manifest Format

**backend/plugins/{plugin_name}/manifest.json:**
```json
{
  "name": "CarbonVoice",
  "version": "1.0.0",
  "author": "VoiceStudio Team",
  "description": "High-quality voice cloning via Carbon AI",
  "backend": {
    "module": "carbon_voice.plugin",
    "requires": ["@carbon-voice/mcp-server"],
    "routes": ["/api/carbon/*"]
  },
  "frontend": {
    "panel": {
      "name": "Carbon Voice",
      "userControl": "CarbonVoice.Views.CarbonPanel",
      "icon": "VoiceIcon"
    },
    "navSection": "Voice Engines"
  }
}
```

### Plugin Registration (Backend)

**backend/api/core/plugin_manager.py:**
```python
import importlib
import json
from pathlib import Path
from fastapi import FastAPI

class PluginManager:
    def __init__(self, app: FastAPI, plugins_dir: Path):
        self.app = app
        self.plugins_dir = plugins_dir
        self.loaded_plugins = []
    
    def discover_and_load_plugins(self):
        """Scan plugins directory and load all plugins"""
        for plugin_dir in self.plugins_dir.iterdir():
            if plugin_dir.is_dir():
                manifest_path = plugin_dir / "manifest.json"
                if manifest_path.exists():
                    self._load_plugin(plugin_dir, manifest_path)
    
    def _load_plugin(self, plugin_dir: Path, manifest_path: Path):
        """Load a single plugin"""
        with open(manifest_path) as f:
            manifest = json.load(f)
        
        # Import plugin module
        module_name = manifest["backend"]["module"]
        plugin_module = importlib.import_module(module_name)
        
        # Call register function
        if hasattr(plugin_module, "register"):
            plugin_module.register(self.app)
            self.loaded_plugins.append(manifest)
```

### Plugin UI Loading (Frontend)

**VoiceStudio.App/Services/PluginManager.cs:**
```csharp
using System;
using System.IO;
using System.Reflection;
using VoiceStudio.Core.Panels;

namespace VoiceStudio.App.Services
{
    public class PluginManager
    {
        private readonly IPanelRegistry _panelRegistry;
        private readonly string _pluginsPath;

        public PluginManager(IPanelRegistry panelRegistry, string pluginsPath)
        {
            _panelRegistry = panelRegistry;
            _pluginsPath = pluginsPath;
        }

        public void LoadPlugins()
        {
            if (!Directory.Exists(_pluginsPath))
                return;

            foreach (var dll in Directory.GetFiles(_pluginsPath, "*.dll"))
            {
                try
                {
                    var assembly = Assembly.LoadFrom(dll);
                    // Scan for UserControl classes implementing IPanelView
                    // Register with panel registry
                }
                catch (Exception ex)
                {
                    // Log error, continue with other plugins
                }
            }
        }
    }
}
```

---

## 📡 Backend Client Interface

### IBackendClient.cs
```csharp
using System.Threading.Tasks;
using VoiceStudio.Core.Models;

namespace VoiceStudio.App.Services
{
    public interface IBackendClient
    {
        Task<bool> CheckHealthAsync();
        Task<AnalyzeVoiceResult> AnalyzeVoiceAsync(AnalyzeVoiceRequest request);
        Task<SynthesisJob> StartSynthesisAsync(SynthesisRequest request);
        Task<WaveformData> GetWaveformAsync(string filePath, int resolution);
        Task<SystemStats> GetSystemStatsAsync();
    }
}
```

### BackendClient.cs
```csharp
using System;
using System.Net.Http;
using System.Text.Json;
using System.Threading.Tasks;
using VoiceStudio.App.Services;

namespace VoiceStudio.App.Services
{
    public class BackendClient : IBackendClient
    {
        private readonly HttpClient _httpClient;
        private readonly BackendClientConfig _config;

        public BackendClient(BackendClientConfig config)
        {
            _config = config;
            _httpClient = new HttpClient
            {
                BaseAddress = new Uri(config.BaseUrl)
            };
        }

        public async Task<bool> CheckHealthAsync()
        {
            try
            {
                var response = await _httpClient.GetAsync("/api/health");
                return response.IsSuccessStatusCode;
            }
            catch
            {
                return false;
            }
        }

        public async Task<AnalyzeVoiceResult> AnalyzeVoiceAsync(AnalyzeVoiceRequest request)
        {
            var json = JsonSerializer.Serialize(request);
            var content = new StringContent(json, System.Text.Encoding.UTF8, "application/json");
            var response = await _httpClient.PostAsync("/api/voices/analyze", content);
            response.EnsureSuccessStatusCode();
            var resultJson = await response.Content.ReadAsStringAsync();
            return JsonSerializer.Deserialize<AnalyzeVoiceResult>(resultJson);
        }

        // Additional methods...
    }
}
```

---

## 🎯 Implementation Phases

### Phase 1: Shell & Layout ✅
- [x] Create WinUI 3 project
- [x] DesignTokens.xaml
- [x] MainWindow.xaml shell
- [x] PanelHost control
- [x] 6 core panel skeletons
- [x] Panel registry system

### Phase 2: Styling & Navigation
- [ ] Centralized styles (Controls.xaml, Text.xaml, Panels.xaml)
- [ ] NavIconButton control
- [ ] Panel swapping on nav click
- [ ] Micro-interactions (hover, focus states)

### Phase 3: Layout Persistence
- [ ] PanelRegistry with all panels registered
- [ ] LayoutState model
- [ ] Save/restore layout to JSON
- [ ] Nav integration with PanelRegistry

### Phase 4: Data Models
- [ ] Core models (Project, Track, Clip, VoiceProfile, LibraryAsset)
- [ ] Project serialization (.voiceproj)
- [ ] Bind panels to real data

### Phase 5: Backend API Skeleton
- [ ] FastAPI app structure
- [ ] Basic endpoints (/api/health, /api/profiles, etc.)
- [ ] IBackendClient implementation
- [ ] Wire DiagnosticsView to backend health

### Phase 6: MCP Bridge Layer
- [ ] MCP client implementation
- [ ] Map MCP operations to API endpoints
- [ ] Wire AnalyzerView to real analysis data

### Phase 7: Audio Engines & I/O
- [ ] Audio synthesis endpoints
- [ ] Playback integration
- [ ] Timeline play/stop hooks

### Phase 8: Visuals (Waveforms, Spectrograms)
- [ ] WaveformControl (Win2D)
- [ ] SpectrogramControl
- [ ] VU meters
- [ ] Backend visualization data endpoints

### Phase 9: Macros & Automation
- [ ] Macro data model
- [ ] Node editor UI
- [ ] Macro execution backend
- [ ] Automation curves

### Phase 10: Advanced Modules & Packaging
- [ ] Training module
- [ ] Batch processor
- [ ] Transcribe panel
- [ ] Settings & Logs
- [ ] Installer & packaging

---

## ✅ Success Criteria

### Phase 1 Complete
- [x] Solution builds without errors
- [x] All VSQ.* resources resolve
- [x] MainWindow displays with correct layout
- [x] All 6 panels exist as separate files
- [x] PanelHost used for all panels
- [x] PanelRegistry functional

### Ready for Phase 2
- All Phase 1 deliverables complete
- No simplifications detected
- File structure matches spec
- Design tokens in use

---

## 📚 Reference Documents

- **PHASE_ROADMAP_COMPLETE.md** - Complete 10-phase roadmap
- **GLOBAL_GUARDRAILS.md** - Anti-simplification rules
- **UI_IMPLEMENTATION_SPEC.md** - Detailed UI spec
- **ARCHITECTURE_DATA_FLOW.md** - Data flow and contracts
- **EXECUTION_PLAN.md** - Legacy plan (archived: [legacy_worker_system/design/](../archive/legacy_worker_system/design/EXECUTION_PLAN.md))

---

**This specification provides the complete foundation for implementing VoiceStudio Quantum+ as a professional DAW-grade application with Adobe-style complexity and functionality.**

