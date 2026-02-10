// Phase 5: Drag and Drop System
// Task 5.7: Professional drag and drop support

using System;
using System.Collections.Generic;
using System.Threading.Tasks;
using Microsoft.UI.Xaml;
using Microsoft.UI.Xaml.Controls;
using Windows.ApplicationModel.DataTransfer;
using Windows.Storage;

namespace VoiceStudio.App.Features.DragDrop;

/// <summary>
/// Supported drag data types.
/// </summary>
public enum DragDataType
{
    AudioFile,
    VideoFile,
    Text,
    VoiceProfile,
    Project,
    Timeline,
    Effect,
    Custom,
}

/// <summary>
/// Drag operation data.
/// </summary>
public class DragData
{
    public DragDataType Type { get; set; }
    public object? Data { get; set; }
    public string? SourceId { get; set; }
    public Dictionary<string, object> Metadata { get; set; } = new();
}

/// <summary>
/// Drop result.
/// </summary>
public class DropResult
{
    public bool Success { get; set; }
    public string? Message { get; set; }
    public object? ResultData { get; set; }
}

/// <summary>
/// Service for managing drag and drop operations.
/// </summary>
public class DragDropService
{
    private DragData? _currentDrag;
    private readonly HashSet<string> _validDropTargets = new();
    
    // Supported file extensions
    private static readonly HashSet<string> AudioExtensions = new(StringComparer.OrdinalIgnoreCase)
    {
        ".wav", ".mp3", ".flac", ".ogg", ".m4a", ".aac", ".wma"
    };
    
    private static readonly HashSet<string> VideoExtensions = new(StringComparer.OrdinalIgnoreCase)
    {
        ".mp4", ".avi", ".mkv", ".mov", ".wmv", ".webm"
    };

    public event EventHandler<DragData>? DragStarted;
    public event EventHandler<DropResult>? DropCompleted;

    /// <summary>
    /// Start a drag operation.
    /// </summary>
    public void StartDrag(DragData data)
    {
        _currentDrag = data;
        DragStarted?.Invoke(this, data);
    }

    /// <summary>
    /// End the current drag operation.
    /// </summary>
    public void EndDrag()
    {
        _currentDrag = null;
    }

    /// <summary>
    /// Get the current drag data.
    /// </summary>
    public DragData? GetCurrentDrag() => _currentDrag;

    /// <summary>
    /// Register a drop target.
    /// </summary>
    public void RegisterDropTarget(string targetId, params DragDataType[] acceptedTypes)
    {
        _validDropTargets.Add(targetId);
    }

    /// <summary>
    /// Check if a drop is valid for a target.
    /// </summary>
    public bool CanDrop(string targetId, DragDataType dataType)
    {
        return _validDropTargets.Contains(targetId);
    }

    /// <summary>
    /// Handle drag enter on a UI element.
    /// </summary>
    public DataPackageOperation HandleDragEnter(
        UIElement element,
        DragEventArgs e,
        DragDataType[] acceptedTypes)
    {
        var view = e.DataView;
        
        // Check for files
        if (view.Contains(StandardDataFormats.StorageItems))
        {
            e.AcceptedOperation = DataPackageOperation.Copy;
            e.DragUIOverride.Caption = "Drop to import";
            e.DragUIOverride.IsCaptionVisible = true;
            e.DragUIOverride.IsGlyphVisible = true;
            return DataPackageOperation.Copy;
        }
        
        // Check for text
        if (view.Contains(StandardDataFormats.Text))
        {
            e.AcceptedOperation = DataPackageOperation.Copy;
            return DataPackageOperation.Copy;
        }
        
        // Check for internal drag
        if (_currentDrag != null)
        {
            foreach (var type in acceptedTypes)
            {
                if (_currentDrag.Type == type)
                {
                    e.AcceptedOperation = DataPackageOperation.Move;
                    return DataPackageOperation.Move;
                }
            }
        }
        
        e.AcceptedOperation = DataPackageOperation.None;
        return DataPackageOperation.None;
    }

    /// <summary>
    /// Handle drop on a UI element.
    /// </summary>
    public async Task<DropResult> HandleDropAsync(
        UIElement element,
        DragEventArgs e,
        Func<DragData, Task<DropResult>>? processFunc = null)
    {
        var result = new DropResult();
        
        try
        {
            var view = e.DataView;
            DragData? dragData = null;
            
            // Handle file drops
            if (view.Contains(StandardDataFormats.StorageItems))
            {
                var items = await view.GetStorageItemsAsync();
                var files = new List<StorageFile>();
                
                foreach (var item in items)
                {
                    if (item is StorageFile file)
                    {
                        files.Add(file);
                    }
                }
                
                if (files.Count > 0)
                {
                    var type = DetermineFileType(files[0]);
                    dragData = new DragData
                    {
                        Type = type,
                        Data = files,
                    };
                }
            }
            // Handle text drops
            else if (view.Contains(StandardDataFormats.Text))
            {
                var text = await view.GetTextAsync();
                dragData = new DragData
                {
                    Type = DragDataType.Text,
                    Data = text,
                };
            }
            // Handle internal drags
            else if (_currentDrag != null)
            {
                dragData = _currentDrag;
            }
            
            if (dragData != null)
            {
                if (processFunc != null)
                {
                    result = await processFunc(dragData);
                }
                else
                {
                    result.Success = true;
                    result.ResultData = dragData.Data;
                }
            }
        }
        catch (Exception ex)
        {
            result.Success = false;
            result.Message = ex.Message;
        }
        finally
        {
            EndDrag();
            DropCompleted?.Invoke(this, result);
        }
        
        return result;
    }

    /// <summary>
    /// Create a data package for dragging.
    /// </summary>
    public DataPackage CreateDataPackage(DragData data)
    {
        var package = new DataPackage();
        package.RequestedOperation = DataPackageOperation.Move;
        
        switch (data.Type)
        {
            case DragDataType.Text:
                package.SetText(data.Data?.ToString() ?? "");
                break;
                
            case DragDataType.AudioFile:
            case DragDataType.VideoFile:
                if (data.Data is IEnumerable<StorageFile> files)
                {
                    package.SetStorageItems(files);
                }
                break;
                
            default:
                // Store as custom data
                package.SetText($"voicestudio:{data.Type}:{data.SourceId}");
                break;
        }
        
        return package;
    }

    /// <summary>
    /// Set up drag for a UI element.
    /// </summary>
    public void SetupDraggable(
        UIElement element,
        Func<DragData> getDragData)
    {
        element.CanDrag = true;
        
        element.DragStarting += (sender, args) =>
        {
            var data = getDragData();
            StartDrag(data);
            
            var package = CreateDataPackage(data);
            args.Data.SetDataProvider(
                StandardDataFormats.Text,
                async request =>
                {
                    var deferral = request.GetDeferral();
                    request.SetData(data.SourceId ?? "");
                    deferral.Complete();
                });
        };
    }

    /// <summary>
    /// Set up drop target for a UI element.
    /// </summary>
    public void SetupDropTarget(
        UIElement element,
        string targetId,
        DragDataType[] acceptedTypes,
        Func<DragData, Task<DropResult>>? processFunc = null)
    {
        RegisterDropTarget(targetId, acceptedTypes);
        
        element.AllowDrop = true;
        
        element.DragEnter += (sender, e) =>
        {
            HandleDragEnter(element, e, acceptedTypes);
        };
        
        element.DragOver += (sender, e) =>
        {
            // Update visual feedback
            e.AcceptedOperation = _currentDrag != null
                ? DataPackageOperation.Move
                : DataPackageOperation.Copy;
        };
        
        element.Drop += async (sender, e) =>
        {
            await HandleDropAsync(element, e, processFunc);
        };
    }

    private DragDataType DetermineFileType(StorageFile file)
    {
        var extension = file.FileType.ToLowerInvariant();
        
        if (AudioExtensions.Contains(extension))
        {
            return DragDataType.AudioFile;
        }
        
        if (VideoExtensions.Contains(extension))
        {
            return DragDataType.VideoFile;
        }
        
        return DragDataType.Custom;
    }
}
