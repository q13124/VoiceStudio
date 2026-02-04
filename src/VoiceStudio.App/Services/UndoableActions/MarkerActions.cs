using System;
using System.Collections.ObjectModel;
using System.Linq;
using VoiceStudio.Core.Services;
using VoiceStudio.App.ViewModels;

namespace VoiceStudio.App.Services.UndoableActions
{
  /// <summary>
  /// Undoable action for creating a marker.
  /// </summary>
  public class CreateMarkerAction : IUndoableAction
  {
    private readonly ObservableCollection<MarkerItem> _markers;
    private readonly IBackendClient _backendClient;
    private readonly MarkerItem _marker;
    private readonly Action<MarkerItem>? _onUndo;
    private readonly Action<MarkerItem>? _onRedo;

    public string ActionName => $"Create Marker '{_marker.Name ?? "Unnamed"}'";

    public CreateMarkerAction(
        ObservableCollection<MarkerItem> markers,
        IBackendClient backendClient,
        MarkerItem marker,
        Action<MarkerItem>? onUndo = null,
        Action<MarkerItem>? onRedo = null)
    {
      _markers = markers ?? throw new ArgumentNullException(nameof(markers));
      _backendClient = backendClient ?? throw new ArgumentNullException(nameof(backendClient));
      _marker = marker ?? throw new ArgumentNullException(nameof(marker));
      _onUndo = onUndo;
      _onRedo = onRedo;
    }

    public void Undo()
    {
      var markerToRemove = _markers.FirstOrDefault(m => m.Id == _marker.Id);
      if (markerToRemove != null)
      {
        _markers.Remove(markerToRemove);
        _onUndo?.Invoke(markerToRemove);
      }
    }

    public void Redo()
    {
      if (!_markers.Any(m => m.Id == _marker.Id))
      {
        _markers.Add(_marker);
        _onRedo?.Invoke(_marker);
      }
    }
  }

  /// <summary>
  /// Undoable action for deleting a marker.
  /// </summary>
  public class DeleteMarkerAction : IUndoableAction
  {
    private readonly ObservableCollection<MarkerItem> _markers;
    private readonly IBackendClient _backendClient;
    private readonly MarkerItem _marker;
    private readonly int _originalIndex;
    private readonly Action<MarkerItem>? _onUndo;
    private readonly Action<MarkerItem>? _onRedo;

    public string ActionName => $"Delete Marker '{_marker.Name ?? "Unnamed"}'";

    public DeleteMarkerAction(
        ObservableCollection<MarkerItem> markers,
        IBackendClient backendClient,
        MarkerItem marker,
        int originalIndex,
        Action<MarkerItem>? onUndo = null,
        Action<MarkerItem>? onRedo = null)
    {
      _markers = markers ?? throw new ArgumentNullException(nameof(markers));
      _backendClient = backendClient ?? throw new ArgumentNullException(nameof(backendClient));
      _marker = marker ?? throw new ArgumentNullException(nameof(marker));
      _originalIndex = originalIndex;
      _onUndo = onUndo;
      _onRedo = onRedo;
    }

    public void Undo()
    {
      if (!_markers.Any(m => m.Id == _marker.Id))
      {
        if (_originalIndex >= 0 && _originalIndex <= _markers.Count)
        {
          _markers.Insert(_originalIndex, _marker);
        }
        else
        {
          _markers.Add(_marker);
        }
        _onUndo?.Invoke(_marker);
      }
    }

    public void Redo()
    {
      var markerToRemove = _markers.FirstOrDefault(m => m.Id == _marker.Id);
      if (markerToRemove != null)
      {
        _markers.Remove(markerToRemove);
        _onRedo?.Invoke(markerToRemove);
      }
    }
  }
}