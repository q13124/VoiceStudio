using System;
using System.Collections.Generic;
using System.Linq;
using System.Threading;
using System.Threading.Tasks;
using VoiceStudio.Core.Models;
using VoiceStudio.Core.Services;
using VoiceStudio.App.Helpers;
using VoiceStudio.App.Logging;

namespace VoiceStudio.App.Services
{
  /// <summary>
  /// Implementation of navigation service for panel navigation, deep-links, and backstack management.
  /// Phase 5.2.6: Added forward navigation support.
  /// </summary>
  public class NavigationService : INavigationService
  {
    private readonly PanelStateService _panelStateService;
    private readonly List<NavigationEntry> _backstack = new();
    private readonly List<NavigationEntry> _forwardStack = new();
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

        // Clear forward stack on new navigation (not back/forward navigation)
        _forwardStack.Clear();
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
        // Push current panel to forward stack before navigating back
        if (!string.IsNullOrEmpty(_currentPanelId))
        {
          _forwardStack.Add(new NavigationEntry
          {
            PanelId = _currentPanelId,
            Parameters = new Dictionary<string, object>(),
            Timestamp = DateTime.UtcNow
          });
        }

        _backstack.RemoveAt(_backstack.Count - 1);
        _currentPanelId = previousEntry.PanelId;

        // Save navigation state
        SaveNavigationState();

        // Raise events
        var args = new NavigationEventArgs
        {
          PreviousPanelId = _currentPanelId,
          NewPanelId = previousEntry.PanelId,
          Parameters = previousEntry.Parameters ?? new Dictionary<string, object>(),
          IsBackNavigation = true
        };

        NavigationChanged?.Invoke(this, args);
        BackStackChanged?.Invoke(this, EventArgs.Empty);
      }
    }

    public async Task NavigateForwardAsync(CancellationToken cancellationToken = default)
    {
      if (!CanNavigateForward())
        return;

      cancellationToken.ThrowIfCancellationRequested();

      var nextEntry = _forwardStack.LastOrDefault();
      if (nextEntry != null)
      {
        // Push current panel to back stack before navigating forward
        if (!string.IsNullOrEmpty(_currentPanelId))
        {
          _backstack.Add(new NavigationEntry
          {
            PanelId = _currentPanelId,
            Parameters = new Dictionary<string, object>(),
            Timestamp = DateTime.UtcNow
          });
        }

        _forwardStack.RemoveAt(_forwardStack.Count - 1);
        _currentPanelId = nextEntry.PanelId;

        // Save navigation state
        SaveNavigationState();

        // Raise events
        var args = new NavigationEventArgs
        {
          PreviousPanelId = _currentPanelId,
          NewPanelId = nextEntry.PanelId,
          Parameters = nextEntry.Parameters ?? new Dictionary<string, object>(),
          IsBackNavigation = false
        };

        NavigationChanged?.Invoke(this, args);
        BackStackChanged?.Invoke(this, EventArgs.Empty);
      }

      await Task.CompletedTask;
    }

    public bool CanNavigateBack()
    {
      return _backstack.Count > 0;
    }

    public bool CanNavigateForward()
    {
      return _forwardStack.Count > 0;
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
        // Use UnpackagedSettingsHelper for file-based settings (works for both packaged and unpackaged apps)
        var savedPanelId = UnpackagedSettingsHelper.GetValue<string>(NavigationStateKey, null);
        if (!string.IsNullOrEmpty(savedPanelId))
        {
          _currentPanelId = savedPanelId;
        }
        // Note: Backstack restoration would require more complex serialization
        // For now, we'll start fresh on app restart
      }
      catch (Exception ex)
      {
        ErrorLogger.LogWarning($"Best effort operation failed: {ex.Message}", "NavigationService.LoadNavigationState");
      }
    }

    private void SaveNavigationState()
    {
      try
      {
        // Use UnpackagedSettingsHelper for file-based settings (works for both packaged and unpackaged apps)
        if (!string.IsNullOrEmpty(_currentPanelId))
        {
          UnpackagedSettingsHelper.SetValue(NavigationStateKey, _currentPanelId);
        }
      }
      catch (Exception ex)
      {
        ErrorLogger.LogWarning($"Best effort operation failed: {ex.Message}", "NavigationService.SaveNavigationState");
      }
    }
  }
}