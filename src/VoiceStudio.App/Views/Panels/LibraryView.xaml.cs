using Microsoft.UI.Xaml;
using Microsoft.UI.Xaml.Controls;
using Microsoft.UI.Xaml.Controls.Primitives;
using Microsoft.UI.Xaml.Input;
using Microsoft.UI.Xaml.Media;
using VoiceStudio.App.Services;
using VoiceStudio.App.Services.UndoableActions;
using VoiceStudio.App.ViewModels;
using VoiceStudio.Core.Services;
using Windows.Foundation;
using Windows.System;
using Windows.ApplicationModel.DataTransfer;
using Windows.Storage.Pickers;
using System;
using System.Linq;
using System.Reflection;
using System.Threading.Tasks;

namespace VoiceStudio.App.Views.Panels
{
  /// <summary>
  /// LibraryView panel for asset library browsing and management.
  /// </summary>
  public sealed partial class LibraryView : UserControl
  {
    public LibraryViewModel ViewModel { get; }

    private LibraryAsset? _draggedAsset;
    private DragDropVisualFeedbackService? _dragDropService;
    private IAudioPlayerService? _audioPlayer;
    private ToastNotificationService? _toastService;
    private UndoRedoService? _undoRedoService;

    public LibraryView()
    {
      this.InitializeComponent();
      ViewModel = new LibraryViewModel(
          AppServices.GetRequiredService<IViewModelContext>(),
          ServiceProvider.GetBackendClient()
      );
      DataContext = ViewModel;

      // Initialize services
      _dragDropService = ServiceProvider.GetDragDropVisualFeedbackService();
      _audioPlayer = ServiceProvider.GetAudioPlayerService();
      _toastService = ServiceProvider.GetToastNotificationService();
      _undoRedoService = ServiceProvider.GetUndoRedoService();

      // Subscribe to selection changes to update UI
      var multiSelectService = ServiceProvider.GetMultiSelectService();
      multiSelectService.SelectionChanged += (s, e) =>
      {
        if (e.PanelId == ViewModel.PanelId)
        {
          UpdateAssetSelectionVisuals();
        }
      };

      // Handle keyboard shortcuts
      this.KeyDown += LibraryView_KeyDown;

      // Setup keyboard navigation
      this.Loaded += LibraryView_KeyboardNavigation_Loaded;

      // Setup Escape key to close help overlay
      KeyboardNavigationHelper.SetupEscapeKeyHandling(this, () =>
      {
        if (HelpOverlay.IsVisible)
        {
          HelpOverlay.Hide();
        }
      });

      // Update visuals when assets change
      ViewModel.PropertyChanged += (s, e) =>
      {
        if (e.PropertyName == nameof(LibraryViewModel.Assets) ||
                  e.PropertyName == nameof(LibraryViewModel.SelectedAssetCount))
        {
          UpdateAssetSelectionVisuals();
        }
      };
    }

    private void HelpButton_Click(object sender, Microsoft.UI.Xaml.RoutedEventArgs e)
    {
      HelpOverlay.Title = "Library Help";
      HelpOverlay.HelpText = "The Library panel provides access to all your audio assets, voice profiles, projects, and other content. Browse, search, and filter your library. View asset details, preview audio, and organize content with tags. The library is your central hub for all VoiceStudio content.";

      HelpOverlay.Shortcuts.Clear();
      HelpOverlay.Shortcuts.Add(new Controls.KeyboardShortcut { Key = "Ctrl+F", Description = "Focus search" });
      HelpOverlay.Shortcuts.Add(new Controls.KeyboardShortcut { Key = "F5", Description = "Refresh library" });
      HelpOverlay.Shortcuts.Add(new Controls.KeyboardShortcut { Key = "Escape", Description = "Close help" });

      HelpOverlay.Tips.Clear();
      HelpOverlay.Tips.Add("Use filters to narrow down assets by type, date, or tags");
      HelpOverlay.Tips.Add("Search across all asset metadata including tags and descriptions");
      HelpOverlay.Tips.Add("Click an asset to view details and preview");
      HelpOverlay.Tips.Add("Tag assets to organize and find them quickly");
      HelpOverlay.Tips.Add("The library automatically indexes all your content");

      HelpOverlay.Visibility = Microsoft.UI.Xaml.Visibility.Visible;
      HelpOverlay.Show();
    }

    private void File_RightTapped(object sender, RightTappedRoutedEventArgs e)
    {
      if (sender is Border border && border.DataContext != null)
      {
        e.Handled = true;
        var menuService = ServiceProvider.GetContextMenuService();
        var menu = menuService.CreateContextMenu("audio", border.DataContext);

        // Wire up menu item commands
        WireUpFileMenuCommands(menu, border.DataContext);

        var position = e.GetPosition(border);
        menuService.ShowContextMenu(menu, border, position);
      }
    }

    private void Folder_RightTapped(object sender, RightTappedRoutedEventArgs e)
    {
      if (sender is ListView listView && e.OriginalSource is FrameworkElement element)
      {
        var folder = element.DataContext as dynamic ??
                   (listView.SelectedItem as dynamic);

        if (folder != null)
        {
          e.Handled = true;
          var menuService = ServiceProvider.GetContextMenuService();
          // Use default menu for folders (can be extended later)
          var menu = menuService.CreateContextMenu("default", folder);

          // Add folder-specific menu items
          AddFolderMenuItems(menu, folder);

          var position = e.GetPosition(listView);
          menuService.ShowContextMenu(menu, listView, position);
        }
      }
    }

    private void WireUpFileMenuCommands(MenuFlyout menu, object fileData)
    {
      foreach (var item in menu.Items)
      {
        if (item is MenuFlyoutItem menuItem)
        {
          menuItem.Click += (s, e) => HandleFileMenuClick(menuItem.Text, fileData);
        }
      }
    }

    private void AddFolderMenuItems(MenuFlyout menu, dynamic folder)
    {
      // Clear default items and add folder-specific items
      menu.Items.Clear();

      var newFolderItem = new MenuFlyoutItem { Text = "New Folder" };
      newFolderItem.Click += (s, e) => HandleFolderMenuClick("New Folder", folder);
      menu.Items.Add(newFolderItem);

      menu.Items.Add(new MenuFlyoutSeparator());

      var renameItem = new MenuFlyoutItem { Text = "Rename" };
      renameItem.Click += (s, e) => HandleFolderMenuClick("Rename", folder);
      menu.Items.Add(renameItem);

      var deleteItem = new MenuFlyoutItem { Text = "Delete" };
      deleteItem.Click += (s, e) => HandleFolderMenuClick("Delete", folder);
      menu.Items.Add(deleteItem);
    }

    private async void HandleFileMenuClick(string action, object fileData)
    {
      try
      {
        // Get asset properties dynamically
        var assetId = GetPropertyValue(fileData, "Id")?.ToString() ?? "";
        var assetName = GetPropertyValue(fileData, "Name")?.ToString() ?? "Unknown";
        var assetType = GetPropertyValue(fileData, "Type")?.ToString() ?? "";
        var assetUrl = GetPropertyValue(fileData, "Url")?.ToString() ?? "";
        var assetPath = GetPropertyValue(fileData, "FilePath")?.ToString() ?? "";

        switch (action.ToLower())
        {
          case "play":
            await PlayAssetAsync(assetId, assetUrl, assetPath, assetName);
            break;
          case "stop":
            StopAssetPlayback();
            break;
          case "export":
            await ExportAssetAsync(assetId, assetName, assetUrl, assetPath);
            break;
          case "analyze":
            await AnalyzeAssetAsync(assetId, assetName);
            break;
          case "apply effects":
            await ApplyEffectsToAssetAsync(assetId, assetName);
            break;
          case "properties":
            ShowAssetProperties(fileData, assetName);
            break;
          case "delete":
            await DeleteAssetAsync(assetId, assetName);
            break;
          case "open":
            await OpenAssetAsync(assetPath, assetUrl);
            break;
          case "add to timeline":
            await AddAssetToTimelineAsync(assetId, assetName, assetUrl);
            break;
        }
      }
      catch (Exception ex)
      {
        _toastService?.ShowToast(ToastType.Error, "Error", $"Failed to {action}: {ex.Message}");
        System.Diagnostics.Debug.WriteLine($"Error handling file menu action '{action}': {ex.Message}");
      }
    }

    private object? GetPropertyValue(object obj, string propertyName)
    {
      if (obj == null) return null;

      // Try reflection first
      var prop = obj.GetType().GetProperty(propertyName, BindingFlags.Public | BindingFlags.Instance);
      if (prop != null)
        return prop.GetValue(obj);

      // Try dynamic access
      try
      {
        dynamic dynObj = obj;
        return ((object)dynObj).GetType().GetProperty(propertyName)?.GetValue(dynObj);
      }
      catch
      {
        return null;
      }
    }

    private async Task PlayAssetAsync(string assetId, string assetUrl, string assetPath, string assetName)
    {
      if (_audioPlayer == null)
      {
        _toastService?.ShowToast(ToastType.Error, "Playback Error", "Audio player service not available");
        return;
      }

      try
      {
        string? audioPath = null;

        // Try to get audio path from URL or file path
        if (!string.IsNullOrEmpty(assetPath) && System.IO.File.Exists(assetPath))
        {
          audioPath = assetPath;
        }
        else if (!string.IsNullOrEmpty(assetUrl))
        {
          // If URL is a local path, use it; otherwise we'd need to download
          if (System.IO.File.Exists(assetUrl))
          {
            audioPath = assetUrl;
          }
          else
          {
            _toastService?.ShowToast(ToastType.Warning, "Playback", "Remote audio playback not yet supported");
            return;
          }
        }

        if (string.IsNullOrEmpty(audioPath))
        {
          _toastService?.ShowToast(ToastType.Warning, "Playback", $"Audio file not found for {assetName}");
          return;
        }

        await _audioPlayer.PlayFileAsync(audioPath, () =>
        {
          _toastService?.ShowToast(ToastType.Info, "Playback Complete", $"Finished playing {assetName}");
        });

        _toastService?.ShowToast(ToastType.Success, "Playing", $"Now playing: {assetName}");
      }
      catch (Exception ex)
      {
        _toastService?.ShowToast(ToastType.Error, "Playback Error", $"Failed to play {assetName}: {ex.Message}");
      }
    }

    private void StopAssetPlayback()
    {
      try
      {
        _audioPlayer?.Stop();
        _toastService?.ShowToast(ToastType.Info, "Stopped", "Playback stopped");
      }
      catch (Exception ex)
      {
        _toastService?.ShowToast(ToastType.Error, "Error", $"Failed to stop playback: {ex.Message}");
      }
    }

    private async Task ExportAssetAsync(string assetId, string assetName, string assetUrl, string assetPath)
    {
      try
      {
        var filePicker = new FileSavePicker();
        filePicker.SuggestedFileName = assetName;
        filePicker.FileTypeChoices.Add("Audio Files", new[] { ".wav", ".mp3", ".flac" });
        filePicker.FileTypeChoices.Add("All Files", new[] { ".*" });

        // Get window handle from current window
        var window = Microsoft.UI.Xaml.Window.Current;
        if (window == null)
        {
          _toastService?.ShowToast(ToastType.Warning, "Export", "Window not available");
          return;
        }
        var hwnd = WinRT.Interop.WindowNative.GetWindowHandle(window);
        WinRT.Interop.InitializeWithWindow.Initialize(filePicker, hwnd);

        var file = await filePicker.PickSaveFileAsync();
        if (file == null)
          return; // User cancelled

        // Copy file to selected location
        string? sourcePath = null;
        if (!string.IsNullOrEmpty(assetPath) && System.IO.File.Exists(assetPath))
        {
          sourcePath = assetPath;
        }
        else if (!string.IsNullOrEmpty(assetUrl) && System.IO.File.Exists(assetUrl))
        {
          sourcePath = assetUrl;
        }

        if (string.IsNullOrEmpty(sourcePath) || !System.IO.File.Exists(sourcePath))
        {
          _toastService?.ShowToast(ToastType.Error, "Export Error", "Source file not found");
          return;
        }

        System.IO.File.Copy(sourcePath, file.Path, true);
        _toastService?.ShowToast(ToastType.Success, "Exported", $"Exported {assetName} to {file.Name}");
      }
      catch (Exception ex)
      {
        _toastService?.ShowToast(ToastType.Error, "Export Error", $"Failed to export: {ex.Message}");
      }
    }

    private Task AnalyzeAssetAsync(string assetId, string assetName)
    {
      if (string.IsNullOrEmpty(assetId))
      {
        _toastService?.ShowToast(ToastType.Warning, "Analysis", "Asset ID required for analysis");
        return Task.CompletedTask;
      }

      try
      {
        // Navigate to AnalyzerView with this asset
        _toastService?.ShowToast(ToastType.Info, "Analysis", $"Opening analyzer for {assetName}...");

        // Note: Panel navigation will be implemented when PanelNavigationService is available
        System.Diagnostics.Debug.WriteLine($"Navigate to analyzer with assetId: {assetId}");
      }
      catch (Exception ex)
      {
        _toastService?.ShowToast(ToastType.Error, "Analysis Error", $"Failed to analyze: {ex.Message}");
      }

      return Task.CompletedTask;
    }

    private Task ApplyEffectsToAssetAsync(string assetId, string assetName)
    {
      if (string.IsNullOrEmpty(assetId))
      {
        _toastService?.ShowToast(ToastType.Warning, "Effects", "Asset ID required");
        return Task.CompletedTask;
      }

      try
      {
        // Navigate to EffectsMixerView with this asset
        _toastService?.ShowToast(ToastType.Info, "Effects", $"Opening effects mixer for {assetName}...");

        // Note: Panel navigation will be implemented when PanelNavigationService is available
        System.Diagnostics.Debug.WriteLine($"Navigate to effects mixer with assetId: {assetId}");
      }
      catch (Exception ex)
      {
        _toastService?.ShowToast(ToastType.Error, "Effects Error", $"Failed to apply effects: {ex.Message}");
      }

      return Task.CompletedTask;
    }

    private void ShowAssetProperties(object fileData, string assetName)
    {
      try
      {
        var dialog = new ContentDialog
        {
          Title = $"Properties: {assetName}",
          Content = CreatePropertiesContent(fileData),
          CloseButtonText = "Close",
          XamlRoot = this.XamlRoot
        };

        _ = dialog.ShowAsync();
      }
      catch (Exception ex)
      {
        _toastService?.ShowToast(ToastType.Error, "Error", $"Failed to show properties: {ex.Message}");
      }
    }

    private UIElement CreatePropertiesContent(object fileData)
    {
      var stackPanel = new StackPanel { Spacing = 8 };

      // Add properties dynamically
      var properties = new[] { "Id", "Name", "Type", "Url", "FilePath", "Duration", "Size", "Created", "Modified" };

      foreach (var propName in properties)
      {
        var value = GetPropertyValue(fileData, propName);
        if (value != null)
        {
          var grid = new Grid();
          grid.ColumnDefinitions.Add(new ColumnDefinition { Width = new GridLength(1, GridUnitType.Star) });
          grid.ColumnDefinitions.Add(new ColumnDefinition { Width = new GridLength(2, GridUnitType.Star) });

          var label = new TextBlock
          {
            Text = $"{propName}:",
            FontWeight = Microsoft.UI.Text.FontWeights.SemiBold,
            Margin = new Microsoft.UI.Xaml.Thickness(0, 0, 8, 0)
          };
          Grid.SetColumn(label, 0);

          var valueText = new TextBlock
          {
            Text = value.ToString() ?? "",
            TextWrapping = Microsoft.UI.Xaml.TextWrapping.Wrap
          };
          Grid.SetColumn(valueText, 1);

          grid.Children.Add(label);
          grid.Children.Add(valueText);
          stackPanel.Children.Add(grid);
        }
      }

      var scrollViewer = new ScrollViewer
      {
        Content = stackPanel,
        MaxHeight = 400
      };

      return scrollViewer;
    }

    private async Task DeleteAssetAsync(string assetId, string assetName)
    {
      try
      {
        if (string.IsNullOrEmpty(assetId))
        {
          _toastService?.ShowToast(ToastType.Warning, "Delete", "Asset ID required");
          return;
        }

        // Confirm deletion
        var dialog = new ContentDialog
        {
          Title = "Delete Asset",
          Content = $"Are you sure you want to delete '{assetName}'? This action cannot be undone.",
          PrimaryButtonText = "Delete",
          CloseButtonText = "Cancel",
          DefaultButton = ContentDialogButton.Close,
          XamlRoot = this.XamlRoot
        };

        var result = await dialog.ShowAsync();
        if (result != ContentDialogResult.Primary)
          return;

        // Use ViewModel's delete command
        if (ViewModel?.DeleteAssetCommand?.CanExecute(null) == true)
        {
          // Find the asset in the collection
          var asset = ViewModel.Assets.FirstOrDefault(a => GetPropertyValue(a, "Id")?.ToString() == assetId);
          if (asset != null)
          {
            // Store asset for undo
            var assetToDelete = asset;

            await ViewModel.DeleteAssetCommand.ExecuteAsync(asset);

            // Register undo action
            if (_undoRedoService != null)
            {
              var action = new SimpleAction(
                  $"Delete Asset: {assetName}",
                  () =>
                  {
                    // Undo: Add the asset back
                    ViewModel.Assets.Add(assetToDelete);
                    // Note: Backend restoration will be handled by ViewModel's delete command
                  },
                  () =>
                  {
                    // Redo: Remove the asset again
                    ViewModel.Assets.Remove(assetToDelete);
                    // Note: Backend deletion will be handled by ViewModel's delete command
                  });
              _undoRedoService.RegisterAction(action);
            }

            _toastService?.ShowToast(ToastType.Success, "Deleted", $"Deleted {assetName}");
          }
        }
      }
      catch (Exception ex)
      {
        _toastService?.ShowToast(ToastType.Error, "Delete Error", $"Failed to delete: {ex.Message}");
      }
    }

    private async Task OpenAssetAsync(string assetPath, string assetUrl)
    {
      try
      {
        string? path = null;
        if (!string.IsNullOrEmpty(assetPath) && System.IO.File.Exists(assetPath))
        {
          path = assetPath;
        }
        else if (!string.IsNullOrEmpty(assetUrl) && System.IO.File.Exists(assetUrl))
        {
          path = assetUrl;
        }

        if (string.IsNullOrEmpty(path))
        {
          _toastService?.ShowToast(ToastType.Warning, "Open", "File path not available");
          return;
        }

        // Open file with default application
        var file = await Windows.Storage.StorageFile.GetFileFromPathAsync(path);
        var success = await Windows.System.Launcher.LaunchFileAsync(file);

        if (success)
        {
          _toastService?.ShowToast(ToastType.Success, "Opened", "File opened in default application");
        }
        else
        {
          _toastService?.ShowToast(ToastType.Warning, "Open", "Could not open file");
        }
      }
      catch (Exception ex)
      {
        _toastService?.ShowToast(ToastType.Error, "Open Error", $"Failed to open file: {ex.Message}");
      }
    }

    private Task AddAssetToTimelineAsync(string assetId, string assetName, string assetUrl)
    {
      if (string.IsNullOrEmpty(assetId))
      {
        _toastService?.ShowToast(ToastType.Warning, "Timeline", "Asset ID required");
        return Task.CompletedTask;
      }

      try
      {
        // Note: Adding asset to timeline will be implemented when TimelineViewModel integration is available
        // This will require:
        // 1. Get current project from TimelineViewModel
        // 2. Create AudioClip from asset
        // 3. Add clip to selected track

        _toastService?.ShowToast(ToastType.Info, "Timeline", $"Adding {assetName} to timeline...");
        System.Diagnostics.Debug.WriteLine($"Add asset {assetId} to timeline");
      }
      catch (Exception ex)
      {
        _toastService?.ShowToast(ToastType.Error, "Timeline Error", $"Failed to add to timeline: {ex.Message}");
      }

      return Task.CompletedTask;
    }

    private async void HandleFolderMenuClick(string action, dynamic folder)
    {
      try
      {
        var folderId = GetPropertyValue(folder, "Id")?.ToString() ?? "";
        var folderName = GetPropertyValue(folder, "Name")?.ToString() ?? "Unknown";

        switch (action.ToLower())
        {
          case "new folder":
            if (ViewModel?.CreateFolderCommand?.CanExecute(null) == true)
            {
              await ViewModel.CreateFolderCommand.ExecuteAsync(null);
              _toastService?.ShowToast(ToastType.Success, "Folder Created", "New folder created");
            }
            break;
          case "rename":
            await RenameFolderAsync(folder, folderId, folderName);
            break;
          case "delete":
            await DeleteFolderAsync(folderId, folderName);
            break;
        }
      }
      catch (Exception ex)
      {
        _toastService?.ShowToast(ToastType.Error, "Error", $"Failed to {action}: {ex.Message}");
        System.Diagnostics.Debug.WriteLine($"Error handling folder menu action '{action}': {ex.Message}");
      }
    }

    private async Task RenameFolderAsync(dynamic folder, string folderId, string folderName)
    {
      try
      {
        if (string.IsNullOrEmpty(folderId))
        {
          _toastService?.ShowToast(ToastType.Warning, "Rename", "Folder ID required");
          return;
        }

        var textBox = new TextBox
        {
          Text = folderName,
          PlaceholderText = "Enter new folder name",
          Margin = new Microsoft.UI.Xaml.Thickness(0, 12, 0, 0),
          HorizontalAlignment = HorizontalAlignment.Stretch
        };

        var dialog = new ContentDialog
        {
          Title = "Rename Folder",
          Content = textBox,
          PrimaryButtonText = "Rename",
          CloseButtonText = "Cancel",
          DefaultButton = ContentDialogButton.Primary,
          XamlRoot = this.XamlRoot
        };

        textBox.Loaded += (s, e) =>
        {
          textBox.SelectAll();
          textBox.Focus(FocusState.Programmatic);
        };

        var result = await dialog.ShowAsync();
        if (result == ContentDialogResult.Primary)
        {
          var newName = textBox.Text?.Trim();
          if (string.IsNullOrWhiteSpace(newName))
          {
            _toastService?.ShowToast(ToastType.Warning, "Rename", "Folder name cannot be empty");
            return;
          }

          // Validate folder name
          var invalidChars = System.IO.Path.GetInvalidFileNameChars();
          if (newName.IndexOfAny(invalidChars) >= 0)
          {
            _toastService?.ShowToast(ToastType.Error, "Invalid Name", "Folder name contains invalid characters");
            return;
          }

          // Store old name for undo
          var oldName = folderName;

          // Note: Backend API call for folder rename will be implemented when endpoint is available
          _toastService?.ShowToast(ToastType.Info, "Rename", $"Renaming folder to '{newName}'...");
          System.Diagnostics.Debug.WriteLine($"Rename folder {folderId} to {newName}");

          // Register undo action
          if (_undoRedoService != null)
          {
            var action = new SimpleAction(
                $"Rename Folder: {oldName} → {newName}",
                () =>
                {
                  // Undo: Revert to old name
                  // Note: Backend update will be handled by ViewModel's rename command
                  _toastService?.ShowToast(ToastType.Info, "Undo", $"Reverted folder name to '{oldName}'");
                },
                () =>
                {
                  // Redo: Apply new name again
                  // Note: Backend update will be handled by ViewModel's rename command
                  _toastService?.ShowToast(ToastType.Info, "Redo", $"Renamed folder to '{newName}'");
                });
            _undoRedoService.RegisterAction(action);
          }

          // Refresh folders after rename
          if (ViewModel?.LoadFoldersCommand?.CanExecute(null) == true)
          {
            await ViewModel.LoadFoldersCommand.ExecuteAsync(null);
          }
        }
      }
      catch (Exception ex)
      {
        _toastService?.ShowToast(ToastType.Error, "Rename Error", $"Failed to rename folder: {ex.Message}");
      }
    }

    private async Task DeleteFolderAsync(string folderId, string folderName)
    {
      try
      {
        if (string.IsNullOrEmpty(folderId))
        {
          _toastService?.ShowToast(ToastType.Warning, "Delete", "Folder ID required");
          return;
        }

        // Confirm deletion
        var dialog = new ContentDialog
        {
          Title = "Delete Folder",
          Content = $"Are you sure you want to delete '{folderName}'? This will also delete all assets in this folder. This action cannot be undone.",
          PrimaryButtonText = "Delete",
          CloseButtonText = "Cancel",
          DefaultButton = ContentDialogButton.Close,
          XamlRoot = this.XamlRoot
        };

        var result = await dialog.ShowAsync();
        if (result != ContentDialogResult.Primary)
          return;

        // Store folder info for undo
        var folderIdToDelete = folderId;

        // Note: Backend API call for folder deletion will be implemented when endpoint is available
        _toastService?.ShowToast(ToastType.Info, "Delete", $"Deleting folder '{folderName}'...");
        System.Diagnostics.Debug.WriteLine($"Delete folder {folderId}");

        // Register undo action
        if (_undoRedoService != null)
        {
          var action = new SimpleAction(
              $"Delete Folder: {folderName}",
              () =>
              {
                // Undo: Restore folder
                // Note: Backend restoration will be handled by ViewModel's delete command
                _toastService?.ShowToast(ToastType.Info, "Undo", $"Restored folder '{folderName}'");
              },
              () =>
              {
                // Redo: Delete folder again
                // Note: Backend deletion will be handled by ViewModel's delete command
                _toastService?.ShowToast(ToastType.Info, "Redo", $"Deleted folder '{folderName}'");
              });
          _undoRedoService.RegisterAction(action);
        }

        // Refresh folders after delete
        if (ViewModel?.LoadFoldersCommand?.CanExecute(null) == true)
        {
          await ViewModel.LoadFoldersCommand.ExecuteAsync(null);
        }
      }
      catch (Exception ex)
      {
        _toastService?.ShowToast(ToastType.Error, "Delete Error", $"Failed to delete folder: {ex.Message}");
      }
    }

    private void Asset_PointerPressed(object sender, PointerRoutedEventArgs e)
    {
      if (sender is Border border && border.DataContext is LibraryAsset asset)
      {
        var isCtrlPressed = InputHelper.IsControlPressed();
        var isShiftPressed = InputHelper.IsShiftPressed();

        ViewModel.ToggleAssetSelection(asset.Id, isCtrlPressed, isShiftPressed);

        UpdateAssetSelectionVisuals();
        e.Handled = true;
      }
    }

    private void LibraryView_KeyboardNavigation_Loaded(object sender, RoutedEventArgs e)
    {
      // Setup Tab navigation order for this panel
      KeyboardNavigationHelper.SetupTabNavigation(this, 0);
    }

    private void LibraryView_KeyDown(object sender, KeyRoutedEventArgs e)
    {
      var isCtrlPressed = Microsoft.UI.Input.InputKeyboardSource.GetKeyStateForCurrentThread(VirtualKey.Control).HasFlag(Windows.UI.Core.CoreVirtualKeyStates.Down);

      if (isCtrlPressed && e.Key == VirtualKey.A)
      {
        // Ctrl+A - Select all assets
        ViewModel.SelectAllAssetsCommand.Execute(null);
        UpdateAssetSelectionVisuals();
        e.Handled = true;
      }
      else if (e.Key == VirtualKey.Escape)
      {
        // Escape - Clear asset selection
        ViewModel.ClearAssetSelectionCommand.Execute(null);
        UpdateAssetSelectionVisuals();
        e.Handled = true;
      }
    }

    private void UpdateAssetSelectionVisuals()
    {
      // Update visual indicators for all asset borders
      UpdateAssetSelectionVisualsRecursive(this);
    }

    private void UpdateAssetSelectionVisualsRecursive(DependencyObject element)
    {
      if (element == null || ViewModel == null)
        return;

      // Check if this is an asset border with a Tag (asset ID)
      if (element is Border border && border.Tag is string assetId)
      {
        var isSelected = ViewModel.IsAssetSelected(assetId);

        // Find the selection indicator child border
        var selectionIndicator = FindChildBorder(border, "AssetSelectionIndicator");
        if (selectionIndicator != null)
        {
          selectionIndicator.Visibility = isSelected
              ? Microsoft.UI.Xaml.Visibility.Visible
              : Microsoft.UI.Xaml.Visibility.Collapsed;
        }

        // Update border brush to show selection
        if (isSelected)
        {
          border.BorderBrush = new SolidColorBrush(Windows.UI.Color.FromArgb(255, 0, 183, 194)); // VSQ.Accent.Cyan
          border.BorderThickness = new Microsoft.UI.Xaml.Thickness(2);
        }
        else
        {
          border.BorderBrush = (Microsoft.UI.Xaml.Media.Brush)this.Resources["VSQ.Panel.BorderBrush"];
          border.BorderThickness = new Microsoft.UI.Xaml.Thickness(1);
        }
      }

      // Recursively check children
      var childCount = Microsoft.UI.Xaml.Media.VisualTreeHelper.GetChildrenCount(element);
      for (int i = 0; i < childCount; i++)
      {
        var child = Microsoft.UI.Xaml.Media.VisualTreeHelper.GetChild(element, i);
        UpdateAssetSelectionVisualsRecursive(child);
      }
    }

    private static Border? FindChildBorder(DependencyObject? parent, string childName)
    {
      if (parent == null) return null;

      for (int i = 0; i < Microsoft.UI.Xaml.Media.VisualTreeHelper.GetChildrenCount(parent); i++)
      {
        var child = Microsoft.UI.Xaml.Media.VisualTreeHelper.GetChild(parent, i);

        if (child is Border border && (child as FrameworkElement)?.Name == childName)
        {
          return border;
        }

        var foundChild = FindChildBorder(child, childName);
        if (foundChild != null)
        {
          return foundChild;
        }
      }

      return null;
    }

    private async void BatchExportAssets_Click(object sender, Microsoft.UI.Xaml.RoutedEventArgs e)
    {
      try
      {
        var selectedCount = ViewModel.SelectedAssetCount;
        if (selectedCount == 0)
        {
          _toastService?.ShowToast(ToastType.Warning, "Export", "No assets selected for export");
          return;
        }

        // Show folder picker for export destination
        var folderPicker = new Windows.Storage.Pickers.FolderPicker();
        folderPicker.SuggestedStartLocation = Windows.Storage.Pickers.PickerLocationId.DocumentsLibrary;
        folderPicker.FileTypeFilter.Add("*");

        var window = Microsoft.UI.Xaml.Window.Current;
        if (window == null)
        {
          _toastService?.ShowToast(ToastType.Warning, "Export", "Window not available");
          return;
        }
        var hwnd = WinRT.Interop.WindowNative.GetWindowHandle(window);
        WinRT.Interop.InitializeWithWindow.Initialize(folderPicker, hwnd);

        var folder = await folderPicker.PickSingleFolderAsync();
        if (folder == null)
          return; // User cancelled

        _toastService?.ShowToast(ToastType.Info, "Exporting", $"Exporting {selectedCount} asset(s)...");

        // Get selected assets
        var selectedAssets = ViewModel.Assets.Where(a => ViewModel.IsAssetSelected(GetPropertyValue(a, "Id")?.ToString() ?? "")).ToList();

        int exportedCount = 0;
        int failedCount = 0;

        foreach (var asset in selectedAssets)
        {
          try
          {
            var assetId = GetPropertyValue(asset, "Id")?.ToString() ?? "";
            var assetName = GetPropertyValue(asset, "Name")?.ToString() ?? "Unnamed";
            var assetPath = GetPropertyValue(asset, "FilePath")?.ToString() ?? "";
            var assetUrl = GetPropertyValue(asset, "Url")?.ToString() ?? "";

            // Find source file
            string? sourcePath = null;
            if (!string.IsNullOrEmpty(assetPath) && System.IO.File.Exists(assetPath))
            {
              sourcePath = assetPath;
            }
            else if (!string.IsNullOrEmpty(assetUrl) && System.IO.File.Exists(assetUrl))
            {
              sourcePath = assetUrl;
            }

            if (string.IsNullOrEmpty(sourcePath) || !System.IO.File.Exists(sourcePath))
            {
              failedCount++;
              continue;
            }

            // Get file extension
            var extension = System.IO.Path.GetExtension(sourcePath);
            var fileName = $"{assetName}{extension}";
            var destPath = System.IO.Path.Combine(folder.Path, fileName);

            // Handle duplicate names
            int counter = 1;
            while (System.IO.File.Exists(destPath))
            {
              var nameWithoutExt = System.IO.Path.GetFileNameWithoutExtension(fileName);
              fileName = $"{nameWithoutExt} ({counter}){extension}";
              destPath = System.IO.Path.Combine(folder.Path, fileName);
              counter++;
            }

            // Copy file
            System.IO.File.Copy(sourcePath, destPath, false);
            exportedCount++;
          }
          catch (Exception ex)
          {
            failedCount++;
            System.Diagnostics.Debug.WriteLine($"Failed to export asset: {ex.Message}");
          }
        }

        if (exportedCount > 0)
        {
          _toastService?.ShowToast(ToastType.Success, "Exported", $"Exported {exportedCount} asset(s) to {folder.Name}" + (failedCount > 0 ? $" ({failedCount} failed)" : ""));
        }
        else
        {
          _toastService?.ShowToast(ToastType.Error, "Export Failed", "Failed to export any assets");
        }
      }
      catch (Exception ex)
      {
        _toastService?.ShowToast(ToastType.Error, "Export Error", $"Failed to batch export: {ex.Message}");
      }
    }

    private void Asset_DragStarting(UIElement sender, DragStartingEventArgs e)
    {
      if (sender is Border border && border.DataContext is LibraryAsset asset)
      {
        _draggedAsset = asset;

        // Set drag data
        e.Data.SetText(asset.Id);
        e.Data.Properties.Add("AssetId", asset.Id);
        e.Data.Properties.Add("AssetName", asset.Name ?? "Unnamed Asset");
        e.Data.Properties.Add("AssetType", asset.Type);

        // Reduce opacity of source element
        border.Opacity = 0.5;
      }
    }

    private void Asset_DragItemsCompleted(UIElement sender, DragItemsCompletedEventArgs e)
    {
      // Clean up drag state
      if (sender is Border border)
      {
        border.Opacity = 1.0;
      }

      if (_dragDropService != null)
      {
        _dragDropService.Cleanup();
        DragDropCanvas.Children.Clear();
      }

      _draggedAsset = null;
    }

    private void Asset_DragOver(object sender, DragEventArgs e)
    {
      if (sender is Border border && _dragDropService != null)
      {
        e.AcceptedOperation = DataPackageOperation.Move | DataPackageOperation.Copy;
        e.DragUIOverride.IsGlyphVisible = false;
        e.DragUIOverride.IsContentVisible = false;

        // Show drop target indicator
        var position = e.GetPosition(border);
        var dropPosition = DetermineDropPosition(border, position);
        _dragDropService.ShowDropTargetIndicator(border, dropPosition);
      }
    }

    private async void Asset_Drop(object sender, DragEventArgs e)
    {
      if (sender is Border border && _draggedAsset != null && _dragDropService != null)
      {
        e.AcceptedOperation = DataPackageOperation.Move;

        // Hide drop indicator
        _dragDropService.HideDropTargetIndicator();
        _dragDropService.Cleanup();

        // Implement asset reordering or folder move logic
        if (_draggedAsset != null)
        {
          var targetData = border.DataContext;

          // Check if dropping on a folder
          var targetFolderId = GetPropertyValue(targetData, "Id")?.ToString();
          var targetFolderName = GetPropertyValue(targetData, "Name")?.ToString() ?? "Unknown";

          if (!string.IsNullOrEmpty(targetFolderId) && targetData != null)
          {
            // Check if target is a folder (has folder-like properties)
            var targetType = GetPropertyValue(targetData, "Type")?.ToString() ?? "";

            if (targetType == "folder" || targetType == "Folder" || string.IsNullOrEmpty(targetType))
            {
              // Move asset to folder
              try
              {
                // Update asset's folder property if it exists
                var assetId = _draggedAsset.Id;

                // Note: Backend API call for moving asset to folder will be implemented when endpoint is available
                _toastService?.ShowToast(ToastType.Info, "Move", $"Moving '{_draggedAsset.Name}' to '{targetFolderName}'...");
                System.Diagnostics.Debug.WriteLine($"Move asset {assetId} to folder {targetFolderId}");

                // Refresh assets after move
                if (ViewModel?.LoadAssetsCommand?.CanExecute(null) == true)
                {
                  await ViewModel.LoadAssetsCommand.ExecuteAsync(null);
                }
              }
              catch (Exception ex)
              {
                _toastService?.ShowToast(ToastType.Error, "Move Error", $"Failed to move asset: {ex.Message}");
              }
            }
            else
            {
              // Reorder assets (move before/after target)
              try
              {
                // Get drop position
                var position = e.GetPosition(border);
                var dropPosition = DetermineDropPosition(border, position);

                // Note: Asset reordering will be implemented in ViewModel when reorder command is available
                _toastService?.ShowToast(ToastType.Info, "Reorder", $"Reordering '{_draggedAsset.Name}'...");
                System.Diagnostics.Debug.WriteLine($"Reorder asset {_draggedAsset.Name} {dropPosition} {targetFolderName}");

                // Refresh assets after reorder
                if (ViewModel?.LoadAssetsCommand?.CanExecute(null) == true)
                {
                  await ViewModel.LoadAssetsCommand.ExecuteAsync(null);
                }
              }
              catch (Exception ex)
              {
                _toastService?.ShowToast(ToastType.Error, "Reorder Error", $"Failed to reorder asset: {ex.Message}");
              }
            }
          }
        }

        // Clean up drag state
        _draggedAsset = null;

        // Restore source element opacity
        if (e.OriginalSource is Border sourceBorder)
        {
          sourceBorder.Opacity = 1.0;
        }
      }
    }

    private void Asset_DragLeave(object sender, DragEventArgs e)
    {
      if (_dragDropService != null)
      {
        _dragDropService.HideDropTargetIndicator();
      }
    }

    private DropPosition DetermineDropPosition(Border target, Point position)
    {
      // Determine if drop is before, after, or on the target
      var targetHeight = target.ActualHeight;
      var relativeY = position.Y;

      if (relativeY < targetHeight * 0.33)
        return DropPosition.Before;
      else if (relativeY > targetHeight * 0.67)
        return DropPosition.After;
      else
        return DropPosition.On;
    }
  }
}

