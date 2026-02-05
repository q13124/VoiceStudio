# XAML Design-Time Guide

## Overview

This guide documents the design-time patterns and practices for VoiceStudio's WinUI 3 XAML views. Following these patterns ensures that XAML designer previews work correctly, enabling developers to visualize UI changes without running the application.

## Prerequisites

- Visual Studio 2022 or later with WinUI 3 workload
- Windows App SDK
- VoiceStudio.App project properly configured

## Core Concepts

### 1. x:DataType Declaration

Every `UserControl` must declare its data type on the root element for compile-time binding validation:

```xml
<UserControl x:Class="VoiceStudio.App.Views.Panels.ExampleView"
    xmlns:local="using:VoiceStudio.App.Views.Panels"
    x:DataType="local:ExampleView">
```

**Benefits:**
- Compile-time binding error detection
- IntelliSense support for bindings
- Better performance with x:Bind

### 2. d:DataContext (Design-Time Data Context)

Add `d:DataContext` to provide design-time data for XAML preview:

```xml
<UserControl x:Class="VoiceStudio.App.Views.Panels.ExampleView"
    xmlns:d="http://schemas.microsoft.com/expression/blend/2008"
    xmlns:mc="http://schemas.openxmlformats.org/markup-compatibility/2006"
    xmlns:local="using:VoiceStudio.App.Views.Panels"
    mc:Ignorable="d"
    d:DataContext="{d:DesignInstance Type=local:ExampleViewModel, IsDesignTimeCreatable=False}"
    x:DataType="local:ExampleView">
```

**Key attributes:**
- `Type`: The ViewModel type to use for IntelliSense
- `IsDesignTimeCreatable`: Set to `False` if ViewModel requires DI or runtime initialization

### 3. d:Visibility Guards

Use `d:Visibility` to control element visibility during design-time:

| Pattern | Runtime Visibility | Design-Time | Use Case |
|---------|-------------------|-------------|----------|
| Loading overlays | Bound to IsLoading | `d:Visibility="Collapsed"` | Prevent overlay from hiding content |
| Error displays | Bound to HasError | `d:Visibility="Collapsed"` | Keep errors hidden during design |
| Help overlays | Usually Collapsed | `d:Visibility="Collapsed"` | Avoid overlay interference |
| Conditional panels | Bound to condition | `d:Visibility="Visible"` | Show hidden content for design |

**Example:**
```xml
<!-- Loading overlay - hidden at design time -->
<Grid Visibility="{x:Bind ViewModel.IsLoading, Mode=OneWay}"
      d:Visibility="Collapsed">
    <ProgressRing IsActive="True"/>
</Grid>

<!-- Multi-select actions - shown at design time for preview -->
<Border Visibility="{x:Bind ViewModel.HasSelection, Mode=OneWay}"
        d:Visibility="Visible">
    <Button Content="Batch Delete"/>
</Border>
```

## Design-Time Data Providers

### Location

Design-time data providers are located in `src/VoiceStudio.App/DesignTime/`.

### DesignTimeData.cs

Provides sample data collections for design-time preview:

```csharp
using System.Collections.ObjectModel;
using VoiceStudio.Core.Models;

namespace VoiceStudio.App.DesignTime;

public class DesignTimeData
{
    // Voice Profile samples
    public static ObservableCollection<VoiceProfile> SampleProfiles { get; } = new()
    {
        new VoiceProfile
        {
            Id = "profile-001",
            Name = "Professional Narrator",
            Language = "en-US",
            Emotion = "neutral",
            QualityScore = 4.5
        },
        // ... more samples
    };

    // Audio Track samples
    public static ObservableCollection<AudioTrack> SampleTracks { get; } = new()
    {
        new AudioTrack
        {
            Id = "track-001",
            Name = "Main Narration",
            IsMuted = false,
            TrackNumber = 1
        },
        // ... more samples
    };

    // Quality metrics
    public static double SampleMosScore => 4.2;
    public static double SampleSnrDb => 35.5;
    public static string SampleDuration => "00:03:45";
    public static bool IsProcessing => true;
}
```

### Using DesignTimeData in XAML

Reference design-time data in XAML with `d:` prefix bindings:

```xml
<UserControl 
    xmlns:designTime="using:VoiceStudio.App.DesignTime"
    d:DataContext="{d:DesignInstance Type=designTime:DesignTimeData, IsDesignTimeCreatable=True}">
    
    <ListView ItemsSource="{x:Bind ViewModel.Profiles, Mode=OneWay}"
              d:ItemsSource="{x:Bind designTime:DesignTimeData.SampleProfiles}"/>
</UserControl>
```

## Required Namespace Declarations

Every view should include these namespaces for design-time support:

```xml
xmlns:d="http://schemas.microsoft.com/expression/blend/2008"
xmlns:mc="http://schemas.openxmlformats.org/markup-compatibility/2006"
mc:Ignorable="d"
```

## Common Patterns

### Pattern 1: ViewModel in Views.Panels Namespace

VoiceStudio ViewModels are typically co-located with their Views:

```xml
<UserControl x:Class="VoiceStudio.App.Views.Panels.ProfilesView"
    xmlns:local="using:VoiceStudio.App.Views.Panels"
    d:DataContext="{d:DesignInstance Type=local:ProfilesViewModel, IsDesignTimeCreatable=False}"
    x:DataType="local:ProfilesViewModel">
```

### Pattern 2: DataTemplate with x:DataType

DataTemplates should declare their data type for compile-time validation:

```xml
<DataTemplate x:DataType="models:VoiceProfile">
    <TextBlock Text="{x:Bind Name, Mode=OneWay}"/>
</DataTemplate>
```

### Pattern 3: FallbackValue for Nullable Bindings

Use FallbackValue to prevent design-time errors for potentially null values:

```xml
<TextBlock Text="{x:Bind ViewModel.SelectedProfile.Name, 
                  Mode=OneWay, 
                  FallbackValue='No profile selected',
                  TargetNullValue='Unnamed profile'}"/>
```

## Checklist for New Views

When creating a new panel or view:

- [ ] Add `xmlns:d` and `xmlns:mc` namespaces
- [ ] Add `mc:Ignorable="d"`
- [ ] Add `x:DataType` to root UserControl
- [ ] Add `d:DataContext` with DesignInstance
- [ ] Add `d:Visibility="Collapsed"` to loading overlays
- [ ] Add `d:Visibility="Collapsed"` to error displays
- [ ] Add `d:Visibility="Visible"` to conditionally-shown panels
- [ ] Verify DataTemplates have `x:DataType`
- [ ] Add FallbackValue to nullable bindings

## Troubleshooting

### Designer Not Loading

1. Ensure `mc:Ignorable="d"` is present
2. Check that ViewModel exists and is accessible
3. Verify no runtime-only code in ViewModel constructor
4. Clean and rebuild the project

### Binding Errors in Designer

1. Add FallbackValue to bindings
2. Check x:DataType matches actual property types
3. Verify collection types match ItemsSource expectations

### Overlays Hiding Content

1. Add `d:Visibility="Collapsed"` to overlay elements
2. Ensure overlay Grid spans all rows/columns it should cover

## Related Documentation

- [XAML Change Protocol](./XAML_CHANGE_PROTOCOL.md)
- [UI Hardening Guidelines](./UI_HARDENING_GUIDELINES.md)
- [UI Component Library](./UI_COMPONENT_LIBRARY.md)

## Revision History

| Date | Author | Changes |
|------|--------|---------|
| 2026-02-05 | Phase 1 XAML Reliability | Initial creation |
