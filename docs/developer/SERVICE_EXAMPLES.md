# VoiceStudio Service Usage Examples

Practical code examples for using VoiceStudio services in real-world scenarios.

**Last Updated:** 2025-01-28  
**Version:** 1.0

---

## Table of Contents

1. [MultiSelectService Examples](#multiselectservice-examples)
2. [ContextMenuService Examples](#contextmenuservice-examples)
3. [DragDropVisualFeedbackService Examples](#dragdropvisualfeedbackservice-examples)
4. [ToastNotificationService Examples](#toastnotificationservice-examples)
5. [UndoRedoService Examples](#undoredoservice-examples)
6. [RecentProjectsService Examples](#recentprojectsservice-examples)
7. [Error Handling Examples](#error-handling-examples)
8. [Audio Service Examples](#audio-service-examples)
9. [Complete Integration Examples](#complete-integration-examples)

---

## MultiSelectService Examples

### Example 1: Basic Multi-Select in ProfilesView

```csharp
public class ProfilesViewModel : BaseViewModel
{
    private readonly MultiSelectService _multiSelectService;
    private MultiSelectState _selectionState;

    public ProfilesViewModel()
    {
        _multiSelectService = ServiceProvider.GetMultiSelectService();
        _selectionState = _multiSelectService.GetState("ProfilesPanel");
        
        // Subscribe to selection changes
        _multiSelectService.SelectionChanged += OnSelectionChanged;
    }

    private void OnSelectionChanged(object? sender, SelectionChangedEventArgs e)
    {
        if (e.PanelId == "ProfilesPanel")
        {
            OnPropertyChanged(nameof(SelectedCount));
            OnPropertyChanged(nameof(HasSelection));
            OnPropertyChanged(nameof(CanDeleteSelected));
        }
    }

    public int SelectedCount => _selectionState.Count;
    public bool HasSelection => _selectionState.HasSelection;
    public bool CanDeleteSelected => _selectionState.HasSelection;

    public void SelectProfile(string profileId)
    {
        _selectionState.Add(profileId);
        _multiSelectService.OnSelectionChanged("ProfilesPanel", _selectionState);
    }

    public void ToggleProfileSelection(string profileId)
    {
        _selectionState.Toggle(profileId);
        _multiSelectService.OnSelectionChanged("ProfilesPanel", _selectionState);
    }

    public void SelectRange(string anchorId, string targetId)
    {
        var allIds = Profiles.Select(p => p.Id).ToList();
        _selectionState.SetRange(anchorId, targetId, allIds);
        _multiSelectService.OnSelectionChanged("ProfilesPanel", _selectionState);
    }

    public void ClearSelection()
    {
        _multiSelectService.ClearSelection("ProfilesPanel");
    }

    public async Task DeleteSelectedAsync()
    {
        if (!_selectionState.HasSelection)
            return;

        var selectedIds = _selectionState.SelectedIds.ToList();
        foreach (var id in selectedIds)
        {
            await DeleteProfileAsync(id);
        }

        ClearSelection();
    }
}
```

### Example 2: Range Selection with Shift+Click

```csharp
public partial class ProfilesView : UserControl
{
    private string? _rangeAnchorId;

    private void ProfileItem_PointerPressed(object sender, PointerPressedEventArgs e)
    {
        var profileId = GetProfileId(sender);
        
        if (e.KeyModifiers.HasFlag(KeyModifiers.Shift) && _rangeAnchorId != null)
        {
            // Range selection
            var viewModel = DataContext as ProfilesViewModel;
            viewModel?.SelectRange(_rangeAnchorId, profileId);
        }
        else if (e.KeyModifiers.HasFlag(KeyModifiers.Control))
        {
            // Toggle selection
            var viewModel = DataContext as ProfilesViewModel;
            viewModel?.ToggleProfileSelection(profileId);
        }
        else
        {
            // Single selection
            _rangeAnchorId = profileId;
            var viewModel = DataContext as ProfilesViewModel;
            viewModel?.SelectProfile(profileId);
        }
    }
}
```

---

## ContextMenuService Examples

### Example 1: Profile Context Menu

```csharp
public partial class ProfilesView : UserControl
{
    private readonly ContextMenuService _contextMenuService;

    public ProfilesView()
    {
        InitializeComponent();
        _contextMenuService = ServiceProvider.GetContextMenuService();
    }

    private void ProfileItem_RightTapped(object sender, RightTappedRoutedEventArgs e)
    {
        var profile = GetProfileFromElement(sender);
        if (profile == null) return;

        var menu = _contextMenuService.CreateContextMenu("profile", profile);
        
        // Add custom menu items
        menu.Items.Add(new MenuFlyoutSeparator());
        var customItem = new MenuFlyoutItem
        {
            Text = "Custom Action",
            Icon = new SymbolIcon(Symbol.Setting)
        };
        customItem.Click += (s, args) => HandleCustomAction(profile);
        menu.Items.Add(customItem);

        menu.ShowAt(sender as UIElement, e.GetPosition(sender as UIElement));
    }
}
```

### Example 2: Timeline Context Menu

```csharp
private void Timeline_RightTapped(object sender, RightTappedRoutedEventArgs e)
{
    var menu = _contextMenuService.CreateContextMenu("timeline", timelineData);
    
    // Modify menu items
    var addTrackItem = menu.Items.OfType<MenuFlyoutItem>()
        .FirstOrDefault(i => i.Text == "Add Track");
    if (addTrackItem != null)
    {
        addTrackItem.Click += (s, args) => AddTrack();
    }

    menu.ShowAt(sender as UIElement, e.GetPosition(sender as UIElement));
}
```

---

## DragDropVisualFeedbackService Examples

### Example 1: Marker Reordering

```csharp
public partial class MarkerManagerView : UserControl
{
    private readonly DragDropVisualFeedbackService _dragDropService;
    private UIElement? _dragPreview;

    public MarkerManagerView()
    {
        InitializeComponent();
        _dragDropService = ServiceProvider.GetDragDropVisualFeedbackService();
    }

    private void MarkerItem_DragStarting(UIElement sender, DragStartingEventArgs args)
    {
        var marker = GetMarkerFromElement(sender);
        _dragPreview = _dragDropService.CreateDragPreview(sender, marker.Name);
        args.DragUI.SetContentFromDataPackage();
    }

    private void MarkerItem_DragOver(object sender, DragEventArgs e)
    {
        e.AcceptedOperation = DataPackageOperation.Move;
        
        var targetElement = sender as UIElement;
        if (targetElement == null) return;

        // Determine drop position
        var position = GetDropPosition(e, targetElement);
        _dragDropService.ShowDropTargetIndicator(targetElement, position);
    }

    private void MarkerItem_Drop(object sender, DragEventArgs e)
    {
        _dragDropService.HideDropTargetIndicator();
        
        var sourceMarker = GetMarkerFromDataPackage(e.DataView);
        var targetMarker = GetMarkerFromElement(sender);
        var position = GetDropPosition(e, sender as UIElement);

        // Reorder markers
        ReorderMarker(sourceMarker, targetMarker, position);
    }

    private DropPosition GetDropPosition(DragEventArgs e, UIElement element)
    {
        var point = e.GetPosition(element);
        var height = element.ActualHeight;
        
        if (point.Y < height * 0.33)
            return DropPosition.Before;
        else if (point.Y > height * 0.67)
            return DropPosition.After;
        else
            return DropPosition.On;
    }
}
```

### Example 2: Script Segment Reordering

```csharp
private void ScriptSegment_DragOver(object sender, DragEventArgs e)
{
    e.AcceptedOperation = DataPackageOperation.Move;
    
    var targetElement = sender as UIElement;
    var position = CalculateDropPosition(e, targetElement);
    
    _dragDropService.ShowDropTargetIndicator(targetElement, position);
}

private DropPosition CalculateDropPosition(DragEventArgs e, UIElement element)
{
    var bounds = element.GetBoundingRect();
    var point = e.GetPosition(element);
    
    // Use horizontal position for script segments
    if (point.X < bounds.Width * 0.5)
        return DropPosition.Before;
    else
        return DropPosition.After;
}
```

---

## ToastNotificationService Examples

### Example 1: Operation Success/Error Notifications

```csharp
public class ProfilesViewModel : BaseViewModel
{
    private readonly ToastNotificationService _toastService;

    public ProfilesViewModel()
    {
        _toastService = ServiceProvider.GetToastNotificationService();
    }

    public async Task CreateProfileAsync(ProfileData data)
    {
        try
        {
            var profile = await BackendClient.CreateProfileAsync(
                data.Name, data.Language, data.Emotion, data.Tags);
            
            Profiles.Add(profile);
            _toastService.ShowSuccess($"Profile '{profile.Name}' created successfully!");
        }
        catch (Exception ex)
        {
            _toastService.ShowError(
                $"Failed to create profile: {ex.Message}",
                "Error",
                () => ShowErrorDetails(ex));
        }
    }

    public async Task DeleteProfileAsync(string profileId)
    {
        try
        {
            await BackendClient.DeleteProfileAsync(profileId);
            Profiles.Remove(Profiles.First(p => p.Id == profileId));
            _toastService.ShowSuccess("Profile deleted successfully");
        }
        catch (Exception ex)
        {
            _toastService.ShowError(
                $"Failed to delete profile: {ex.Message}",
                "Error");
        }
    }
}
```

### Example 2: Progress Notification

```csharp
public async Task UploadProfileAsync(string filePath)
{
    var progressToast = _toastService.ShowProgress("Uploading profile...");
    
    try
    {
        var progress = new Progress<double>(p => {
            progressToast.UpdateProgress(p);
            progressToast.UpdateMessage($"Uploading profile... {p:P0}");
        });

        await BackendClient.UploadProfileAsync(filePath, progress);
        
        progressToast.Dismiss();
        _toastService.ShowSuccess("Profile uploaded successfully!");
    }
    catch (Exception ex)
    {
        progressToast.Dismiss();
        _toastService.ShowError($"Upload failed: {ex.Message}", "Error");
    }
}
```

---

## UndoRedoService Examples

### Example 1: Profile Creation with Undo

```csharp
public class ProfilesViewModel : BaseViewModel
{
    private readonly UndoRedoService _undoRedoService;

    public ProfilesViewModel()
    {
        _undoRedoService = ServiceProvider.GetUndoRedoService();
    }

    public async Task CreateProfileAsync(ProfileData data)
    {
        var profile = await BackendClient.CreateProfileAsync(
            data.Name, data.Language, data.Emotion, data.Tags);
        
        Profiles.Add(profile);

        // Register undo action
        var action = new CreateProfileAction(profile.Id, profile);
        _undoRedoService.RegisterAction(action);
    }

    public void Undo()
    {
        if (_undoRedoService.CanUndo)
        {
            _undoRedoService.Undo();
        }
    }

    public void Redo()
    {
        if (_undoRedoService.CanRedo)
        {
            _undoRedoService.Redo();
        }
    }
}

// Action implementation
public class CreateProfileAction : IUndoableAction
{
    public string ActionName => "Create Profile";
    private readonly string _profileId;
    private readonly VoiceProfile _profile;
    private readonly ProfilesViewModel _viewModel;

    public CreateProfileAction(string profileId, VoiceProfile profile, ProfilesViewModel viewModel)
    {
        _profileId = profileId;
        _profile = profile;
        _viewModel = viewModel;
    }

    public void Undo()
    {
        _viewModel.Profiles.Remove(_viewModel.Profiles.First(p => p.Id == _profileId));
    }

    public void Redo()
    {
        _viewModel.Profiles.Add(_profile);
    }
}
```

### Example 2: Batch Operations with Undo

```csharp
public async Task DeleteSelectedProfilesAsync()
{
    var selectedIds = _selectionState.SelectedIds.ToList();
    var deletedProfiles = new List<VoiceProfile>();

    foreach (var id in selectedIds)
    {
        var profile = Profiles.First(p => p.Id == id);
        deletedProfiles.Add(profile);
        await BackendClient.DeleteProfileAsync(id);
        Profiles.Remove(profile);
    }

    // Register batch undo action
    var action = new BatchDeleteProfilesAction(selectedIds, deletedProfiles, this);
    _undoRedoService.RegisterAction(action);
}
```

---

## RecentProjectsService Examples

### Example 1: Adding Recent Project

```csharp
public class MainViewModel : BaseViewModel
{
    private readonly RecentProjectsService _recentProjectsService;

    public MainViewModel()
    {
        _recentProjectsService = ServiceProvider.GetRecentProjectsService();
    }

    public async Task OpenProjectAsync(string projectPath)
    {
        var projectName = Path.GetFileNameWithoutExtension(projectPath);
        
        // Add to recent projects
        await _recentProjectsService.AddRecentProjectAsync(projectPath, projectName);
        
        // Load project
        await LoadProjectAsync(projectPath);
    }

    public async Task PinProjectAsync(string projectPath)
    {
        await _recentProjectsService.PinProjectAsync(projectPath);
        OnPropertyChanged(nameof(PinnedProjects));
    }
}
```

### Example 2: Recent Projects Menu

```csharp
public void BuildRecentProjectsMenu(MenuFlyout menu)
{
    // Add pinned projects
    var pinned = _recentProjectsService.PinnedProjects;
    foreach (var project in pinned)
    {
        var item = new MenuFlyoutItem
        {
            Text = project.Name,
            Icon = new SymbolIcon(Symbol.Pin)
        };
        item.Click += (s, e) => OpenProjectAsync(project.Path);
        menu.Items.Add(item);
    }

    if (pinned.Count > 0)
    {
        menu.Items.Add(new MenuFlyoutSeparator());
    }

    // Add recent projects
    var recent = _recentProjectsService.RecentProjects;
    foreach (var project in recent)
    {
        var item = new MenuFlyoutItem
        {
            Text = project.Name
        };
        item.Click += (s, e) => OpenProjectAsync(project.Path);
        menu.Items.Add(item);
    }
}
```

---

## Error Handling Examples

### Example 1: BaseViewModel Error Handling

```csharp
public class ProfilesViewModel : BaseViewModel
{
    public async Task LoadProfilesAsync()
    {
        await ExecuteWithErrorHandlingAsync(async () =>
        {
            var profiles = await BackendClient.GetProfilesAsync();
            Profiles.Clear();
            foreach (var profile in profiles)
            {
                Profiles.Add(profile);
            }
        }, context: "Loading profiles", maxRetries: 3);
    }

    public async Task DeleteProfileAsync(string profileId)
    {
        await ExecuteWithStatePersistenceAsync(
            async () =>
            {
                await BackendClient.DeleteProfileAsync(profileId);
                Profiles.Remove(Profiles.First(p => p.Id == profileId));
            },
            operationId: $"delete-profile-{profileId}",
            stateToSave: Profiles.ToList(),
            context: "Deleting profile"
        );
    }
}
```

### Example 2: Custom Error Handling

```csharp
public async Task ProcessProfileAsync(string profileId)
{
    try
    {
        var profile = await BackendClient.GetProfileAsync(profileId);
        await ProcessProfileDataAsync(profile);
    }
    catch (ProfileNotFoundException ex)
    {
        await ErrorDialogService.ShowErrorAsync(
            ex,
            title: "Profile Not Found",
            context: "Processing profile",
            retryAction: async () => await ProcessProfileAsync(profileId)
        );
    }
    catch (Exception ex)
    {
        ErrorLoggingService.LogError(ex, "Processing profile");
        await ErrorDialogService.ShowErrorAsync(ex, context: "Processing profile");
    }
}
```

---

## Audio Service Examples

### Example 1: Playing Profile Audio

```csharp
public class ProfilesViewModel : BaseViewModel
{
    private readonly IAudioPlayerService _audioService;

    public ProfilesViewModel()
    {
        _audioService = ServiceProvider.GetAudioPlayerService();
        _audioService.PlaybackCompleted += OnPlaybackCompleted;
    }

    public async Task PlayProfileAsync(VoiceProfile profile)
    {
        if (string.IsNullOrEmpty(profile.ReferenceAudioUrl))
            return;

        try
        {
            await _audioService.PlayFileAsync(profile.ReferenceAudioUrl);
            IsPlaying = true;
        }
        catch (Exception ex)
        {
            await HandleErrorAsync(ex, "Playing profile audio");
        }
    }

    private void OnPlaybackCompleted(object? sender, EventArgs e)
    {
        IsPlaying = false;
    }

    public void StopPlayback()
    {
        _audioService.Stop();
        IsPlaying = false;
    }
}
```

### Example 2: Audio Position Tracking

```csharp
public class AudioPlayerViewModel : BaseViewModel
{
    private readonly IAudioPlayerService _audioService;
    private DispatcherTimer? _positionTimer;

    public AudioPlayerViewModel()
    {
        _audioService = ServiceProvider.GetAudioPlayerService();
        _audioService.PositionChanged += OnPositionChanged;
        
        _positionTimer = new DispatcherTimer
        {
            Interval = TimeSpan.FromMilliseconds(100)
        };
        _positionTimer.Tick += (s, e) => UpdatePosition();
        _positionTimer.Start();
    }

    private void UpdatePosition()
    {
        Position = _audioService.Position;
        Duration = _audioService.Duration;
        OnPropertyChanged(nameof(PositionText));
        OnPropertyChanged(nameof(Progress));
    }

    public double Progress => Duration > 0 ? Position / Duration : 0;
    public string PositionText => $"{Position:mm\\:ss} / {Duration:mm\\:ss}";
}
```

---

## Complete Integration Examples

### Example 1: Complete Profile Management with All Services

```csharp
public class ProfilesViewModel : BaseViewModel
{
    private readonly MultiSelectService _multiSelectService;
    private readonly UndoRedoService _undoRedoService;
    private readonly ToastNotificationService _toastService;
    private readonly IAudioPlayerService _audioService;
    private MultiSelectState _selectionState;

    public ProfilesViewModel()
    {
        _multiSelectService = ServiceProvider.GetMultiSelectService();
        _undoRedoService = ServiceProvider.GetUndoRedoService();
        _toastService = ServiceProvider.GetToastNotificationService();
        _audioService = ServiceProvider.GetAudioPlayerService();
        
        _selectionState = _multiSelectService.GetState("ProfilesPanel");
        _multiSelectService.SelectionChanged += OnSelectionChanged;
    }

    public async Task CreateProfileAsync(ProfileData data)
    {
        try
        {
            var profile = await BackendClient.CreateProfileAsync(
                data.Name, data.Language, data.Emotion, data.Tags);
            
            Profiles.Add(profile);

            // Register undo action
            var action = new CreateProfileAction(profile.Id, profile, this);
            _undoRedoService.RegisterAction(action);

            // Show success notification
            _toastService.ShowSuccess($"Profile '{profile.Name}' created successfully!");
        }
        catch (Exception ex)
        {
            await HandleErrorAsync(ex, "Creating profile");
        }
    }

    public async Task DeleteSelectedProfilesAsync()
    {
        if (!_selectionState.HasSelection)
            return;

        var selectedIds = _selectionState.SelectedIds.ToList();
        var deletedProfiles = new List<VoiceProfile>();

        foreach (var id in selectedIds)
        {
            var profile = Profiles.First(p => p.Id == id);
            deletedProfiles.Add(profile);
            await BackendClient.DeleteProfileAsync(id);
            Profiles.Remove(profile);
        }

        // Register batch undo action
        var action = new BatchDeleteProfilesAction(selectedIds, deletedProfiles, this);
        _undoRedoService.RegisterAction(action);

        // Clear selection
        _multiSelectService.ClearSelection("ProfilesPanel");

        // Show success notification
        _toastService.ShowSuccess($"{selectedIds.Count} profile(s) deleted");
    }

    public async Task PlayProfileAsync(VoiceProfile profile)
    {
        if (string.IsNullOrEmpty(profile.ReferenceAudioUrl))
        {
            _toastService.ShowWarning("No reference audio available");
            return;
        }

        try
        {
            await _audioService.PlayFileAsync(profile.ReferenceAudioUrl);
            _toastService.ShowInfo($"Playing '{profile.Name}'");
        }
        catch (Exception ex)
        {
            await HandleErrorAsync(ex, "Playing profile");
        }
    }

    private void OnSelectionChanged(object? sender, SelectionChangedEventArgs e)
    {
        if (e.PanelId == "ProfilesPanel")
        {
            OnPropertyChanged(nameof(SelectedCount));
            OnPropertyChanged(nameof(CanDeleteSelected));
        }
    }
}
```

### Example 2: View with Context Menu and Drag-Drop

```csharp
public partial class ProfilesView : UserControl
{
    private readonly ContextMenuService _contextMenuService;
    private readonly DragDropVisualFeedbackService _dragDropService;

    public ProfilesView()
    {
        InitializeComponent();
        _contextMenuService = ServiceProvider.GetContextMenuService();
        _dragDropService = ServiceProvider.GetDragDropVisualFeedbackService();
    }

    private void ProfileItem_RightTapped(object sender, RightTappedRoutedEventArgs e)
    {
        var profile = GetProfileFromElement(sender);
        if (profile == null) return;

        var menu = _contextMenuService.CreateContextMenu("profile", profile);
        menu.ShowAt(sender as UIElement, e.GetPosition(sender as UIElement));
    }

    private void ProfileItem_DragStarting(UIElement sender, DragStartingEventArgs args)
    {
        var profile = GetProfileFromElement(sender);
        _dragDropService.CreateDragPreview(sender, profile.Name);
    }

    private void ProfileItem_DragOver(object sender, DragEventArgs e)
    {
        e.AcceptedOperation = DataPackageOperation.Move;
        var position = GetDropPosition(e, sender as UIElement);
        _dragDropService.ShowDropTargetIndicator(sender as UIElement, position);
    }

    private void ProfileItem_Drop(object sender, DragEventArgs e)
    {
        _dragDropService.HideDropTargetIndicator();
        // Handle drop
    }
}
```

---

**Last Updated:** 2025-01-28  
**Version:** 1.0

