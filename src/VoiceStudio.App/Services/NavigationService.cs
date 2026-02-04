using System;
using System.Collections.Generic;
using System.Linq;
using System.Threading;
using System.Threading.Tasks;
using Windows.Storage;
using VoiceStudio.Core.Models;
using VoiceStudio.Core.Services;

namespace VoiceStudio.App.Services
{
  /// <summary>
  /// Implementation of navigation service for panel navigation, deep-links, and backstack management.
  /// </summary>
  public class NavigationService : INavigationService
  {
    private readonly PanelStateService _panelStateService;
    private readonly List<NavigationEntry> _backstack = new();
    private string? _currentPanelId;
    private const int MaxBackstackSize = 50;
    private const string NavigationStateKey = "NavigationState";

    public NavigationService(PanelStateService panelStateService)
    {
      _panelStateService = panelStateService ?? throw new ArgumentNullException(nameof(panelStateService));
      LoadNavigationState();
    }

    public event EventHandler<NavigationEventArgs>? NavigationChanged;
    public event EventHandler? BackStackChanged;

    public Task NavigateToPanelAsync(string panelId, Dictionary<string, object>? parameters = null, CancellationToken cancellationToken = default)
    {
      if (string.IsNullOrWhiteSpace(panelId))
        throw new ArgumentException("Panel ID cannot be null or empty.", nameof(panelId));

      cancellationToken.ThrowIfCancellationRequested();

      var previousPanelId = _currentPanelId;
      var isBackNavigation = false;

      // Check if navigating back
      if (_backstack.Count > 0 && _backstack.Last().PanelId == panelId)
      {
        isBackNavigation = true;
        _backstack.RemoveAt(_backstack.Count - 1);
      }
      else
      {
        // Add current panel to backstack if it exists
        if (!string.IsNullOrEmpty(_currentPanelId))
        {
          _backstack.Add(new NavigationEntry
          {
            PanelId = _currentPanelId,
            Parameters = new Dictionary<string, object>(),
            Timestamp = DateTime.UtcNow
          });

          // Limit backstack size
          if (_backstack.Count > MaxBackstackSize)
          {
            _backstack.RemoveAt(0);
          }
        }
      }

      _currentPanelId = panelId;

      // Save navigation state
      SaveNavigationState();

      // Raise events
      var args = new NavigationEventArgs
      {
        PreviousPanelId = previousPanelId,
        NewPanelId = panelId,
        Parameters = parameters ?? new Dictionary<string, object>(),
        IsBackNavigation = isBackNavigation
      };

      NavigationChanged?.Invoke(this, args);
      BackStackChanged?.Invoke(this, EventArgs.Empty);

      return Task.CompletedTask;
    }

    public async Task NavigateBackAsync(CancellationToken cancellationToken = default)
    {
      if (!CanNavigateBack())
        return;

      cancellationToken.ThrowIfCancellationRequested();

      var previousEntry = _backstack.LastOrDefault();
      if (previousEntry != null)
      {
        _backstack.RemoveAt(_backstack.Count - 1);
        await NavigateToPanelAsync(previousEntry.PanelId, previousEntry.Parameters, cancellationToken);
      }
    }

    public bool CanNavigateBack()
    {
      return _backstack.Count > 0;
    }

    public string? GetCurrentPanelId()
    {
      return _currentPanelId;
    }

    public IReadOnlyList<NavigationEntry> GetBackStack()
    {
      return _backstack.AsReadOnly();
    }

    public void ClearBackStack()
    {
      _backstack.Clear();
      SaveNavigationState();
      BackStackChanged?.Invoke(this, EventArgs.Empty);
    }

    private void LoadNavigationState()
    {
      try
      {
        var localSettings = ApplicationData.Current.LocalSettings;
        if (localSettings.Values.TryGetValue(NavigationStateKey, out var value) && value is ApplicationDataCompositeValue composite && composite.TryGetValue("CurrentPanelId", out var panelId) && panelId is string panelIdStr)
        {
          _currentPanelId = panelIdStr;

          // Note: Backstack restoration would require more complex serialization
          // For now, we'll start fresh on app restart
        }
      }
      catch
      {
        // If loading fails, start fresh
      }
    }

    private void SaveNavigationState()
    {
      try
      {
        var localSettings = ApplicationData.Current.LocalSettings;
        var composite = new ApplicationDataCompositeValue();

        if (!string.IsNullOrEmpty(_currentPanelId))
        {
          composite["CurrentPanelId"] = _currentPanelId;
        }

        localSettings.Values[NavigationStateKey] = composite;
      }
      catch
      {
        // If saving fails, continue without persistence
      }
    }
  }
}