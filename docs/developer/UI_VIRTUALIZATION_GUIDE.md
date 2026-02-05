# UI Virtualization Guide

> **Version**: 1.0.0  
> **Last Updated**: 2026-02-04  
> **Status**: Active

## Overview

VoiceStudio implements UI virtualization for large lists and collections to ensure smooth performance even with thousands of items. This guide documents the virtualization patterns used in WinUI 3.

## When to Use Virtualization

Use virtualization when:

- Lists contain 100+ items
- Items have complex templates
- Data is loaded incrementally
- Memory usage is a concern

Do NOT use virtualization when:

- Lists are small (< 50 items)
- Items have simple templates
- All data is available immediately

## WinUI 3 Virtualization Controls

### ItemsRepeater with Virtualization

The `ItemsRepeater` with a virtualizing layout is the recommended approach:

```xml
<ScrollViewer>
    <ItemsRepeater 
        ItemsSource="{x:Bind ViewModel.LargeCollection}"
        Layout="{StaticResource VirtualizingStackLayout}">
        <ItemsRepeater.ItemTemplate>
            <DataTemplate x:DataType="models:AudioClip">
                <local:AudioClipItem Clip="{x:Bind}" />
            </DataTemplate>
        </ItemsRepeater.ItemTemplate>
    </ItemsRepeater>
</ScrollViewer>
```

### Layout Definition

```xml
<Page.Resources>
    <StackLayout 
        x:Key="VirtualizingStackLayout" 
        Orientation="Vertical" 
        Spacing="4"/>
    
    <UniformGridLayout 
        x:Key="VirtualizingGridLayout"
        MinItemWidth="200"
        MinItemHeight="150"
        MinColumnSpacing="8"
        MinRowSpacing="8"/>
</Page.Resources>
```

## Implementation Patterns

### 1. Incremental Loading

For large datasets, load data incrementally:

```csharp
public class VirtualizedCollection : IncrementalLoadingCollection<AudioClipSource, AudioClip>
{
    public VirtualizedCollection() : base(new AudioClipSource()) { }
}

public class AudioClipSource : IIncrementalSource<AudioClip>
{
    private readonly IBackendClient _client;
    
    public async Task<IEnumerable<AudioClip>> GetPagedItemsAsync(
        int pageIndex, 
        int pageSize, 
        CancellationToken ct = default)
    {
        return await _client.GetAudioClipsAsync(pageIndex, pageSize, ct);
    }
}
```

### 2. Observable Range Collection

For efficient bulk updates:

```csharp
public class ObservableRangeCollection<T> : ObservableCollection<T>
{
    public void AddRange(IEnumerable<T> items)
    {
        CheckReentrancy();
        
        foreach (var item in items)
        {
            Items.Add(item);
        }
        
        OnCollectionChanged(new NotifyCollectionChangedEventArgs(
            NotifyCollectionChangedAction.Reset));
    }
    
    public void ReplaceRange(IEnumerable<T> items)
    {
        Items.Clear();
        AddRange(items);
    }
}
```

### 3. Virtualized Timeline

The Timeline panel uses virtualization for audio clips:

```csharp
public class TimelineVirtualizer
{
    private readonly double _viewportStart;
    private readonly double _viewportEnd;
    private readonly List<TimelineClip> _allClips;
    
    public IEnumerable<TimelineClip> GetVisibleClips()
    {
        return _allClips.Where(clip => 
            clip.EndTime > _viewportStart && 
            clip.StartTime < _viewportEnd);
    }
    
    public void OnViewportChanged(double start, double end)
    {
        _viewportStart = start;
        _viewportEnd = end;
        UpdateVisibleClips();
    }
}
```

## Data Template Optimization

### Lightweight Templates

Keep item templates simple to reduce rendering overhead:

```xml
<!-- Good: Simple template -->
<DataTemplate x:DataType="models:AudioClip">
    <Grid Height="48" Padding="8">
        <TextBlock Text="{x:Bind Name}" />
        <TextBlock Text="{x:Bind DurationDisplay}" 
                   HorizontalAlignment="Right" />
    </Grid>
</DataTemplate>

<!-- Avoid: Complex nested template -->
<DataTemplate x:DataType="models:AudioClip">
    <Grid>
        <Grid.RowDefinitions>
            <RowDefinition />
            <RowDefinition />
            <RowDefinition />
        </Grid.RowDefinitions>
        <StackPanel>
            <Border>
                <!-- Multiple nested elements... -->
            </Border>
        </StackPanel>
    </Grid>
</DataTemplate>
```

### Deferred Loading

Use `x:Load` for conditional content:

```xml
<DataTemplate x:DataType="models:AudioClip">
    <Grid>
        <TextBlock Text="{x:Bind Name}" />
        
        <!-- Only load when expanded -->
        <StackPanel x:Load="{x:Bind IsExpanded}">
            <local:WaveformView Audio="{x:Bind}" />
            <local:MetadataPanel Metadata="{x:Bind Metadata}" />
        </StackPanel>
    </Grid>
</DataTemplate>
```

## Performance Guidelines

### 1. Avoid Synchronous Operations

```csharp
// Bad: Blocks UI thread
public void LoadData()
{
    Items = _service.GetItems(); // Synchronous
}

// Good: Async loading
public async Task LoadDataAsync()
{
    IsLoading = true;
    Items = await _service.GetItemsAsync();
    IsLoading = false;
}
```

### 2. Batch Updates

```csharp
// Bad: Multiple notifications
foreach (var item in newItems)
{
    Items.Add(item);  // Triggers notification each time
}

// Good: Single notification
Items.AddRange(newItems);  // Single notification
```

### 3. Image Virtualization

For lists with images:

```csharp
public class VirtualizedImageSource
{
    private readonly LruCache<string, BitmapImage> _cache;
    
    public async Task<ImageSource> GetImageAsync(string url)
    {
        if (_cache.TryGet(url, out var cached))
        {
            return cached;
        }
        
        var image = await LoadImageAsync(url);
        _cache.Put(url, image);
        return image;
    }
}
```

## Memory Management

### Item Recycling

ItemsRepeater recycles item containers automatically. Ensure proper cleanup:

```csharp
public class ClipItemControl : UserControl
{
    protected override void OnApplyTemplate()
    {
        base.OnApplyTemplate();
        // Initialize when recycled
    }
    
    public void OnRecycled()
    {
        // Clean up when item is recycled
        _waveformView?.Dispose();
        _cancellationTokenSource?.Cancel();
    }
}
```

### Weak References

Use weak references for large cached data:

```csharp
private readonly ConditionalWeakTable<string, BitmapImage> _imageCache;
```

## Testing Virtualization

```csharp
[TestMethod]
public async Task LargeCollection_LoadsIncrementally()
{
    // Arrange
    var viewModel = new LibraryViewModel();
    
    // Act
    await viewModel.LoadInitialPageAsync();
    
    // Assert
    Assert.IsTrue(viewModel.Items.Count <= PageSize);
    Assert.IsTrue(viewModel.HasMoreItems);
}

[TestMethod]
public void ViewportChange_UpdatesVisibleItems()
{
    // Arrange
    var virtualizer = new TimelineVirtualizer(clips);
    
    // Act
    virtualizer.OnViewportChanged(0, 10);
    
    // Assert
    Assert.IsTrue(virtualizer.VisibleClips
        .All(c => c.StartTime < 10 && c.EndTime > 0));
}
```

## Troubleshooting

### Symptoms of Missing Virtualization

- High memory usage with large lists
- Slow scrolling
- UI freezes during data updates

### Debugging

1. Enable performance profiling in Visual Studio
2. Check memory usage in Task Manager
3. Monitor frame rate during scrolling
4. Profile GC collections

## Related Documentation

- [Panel System Architecture](PANEL_SYSTEM_ARCHITECTURE.md)
- [Performance Baselines](PERFORMANCE_BASELINES.md)
- [WinUI 3 Migration Guide](WINUI_MIGRATION_GUIDE.md)
