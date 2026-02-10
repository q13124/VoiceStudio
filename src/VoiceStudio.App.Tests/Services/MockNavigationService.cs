using System;
using System.Collections.Generic;
using System.Collections.ObjectModel;
using System.Linq;
using System.Threading;
using System.Threading.Tasks;
using VoiceStudio.Core.Models;
using VoiceStudio.Core.Services;

namespace VoiceStudio.App.Tests.Services
{
  /// <summary>
  /// Mock implementation of INavigationService for testing.
  /// Tracks navigation calls and maintains a navigation history.
  /// </summary>
  public class MockNavigationService : INavigationService
  {
    private readonly List<NavigationEntry> _backStack = new();
    private readonly List<NavigationEntry> _forwardStack = new();
    private string? _currentPanelId;
    private readonly object _lock = new();

    public event EventHandler<NavigationEventArgs>? NavigationChanged;
    public event EventHandler? BackStackChanged;

    /// <summary>
    /// Gets the navigation history (all panels navigated to).
    /// </summary>
    public IReadOnlyList<NavigationEntry> NavigationHistory =>
        new ReadOnlyCollection<NavigationEntry>(_backStack.ToList());

    /// <summary>
    /// Gets the current panel ID.
    /// </summary>
    public string? CurrentPanelId => _currentPanelId;

    /// <summary>
    /// Gets the count of navigation calls.
    /// </summary>
    public int NavigationCallCount { get; private set; }

    /// <summary>
    /// Gets the count of back navigation calls.
    /// </summary>
    public int BackNavigationCallCount { get; private set; }

    /// <summary>
    /// Gets the count of forward navigation calls.
    /// </summary>
    public int ForwardNavigationCallCount { get; private set; }

    /// <summary>
    /// Gets the last navigated panel ID.
    /// </summary>
    public string? LastNavigatedPanelId { get; private set; }

    /// <summary>
    /// Gets the last navigation parameters.
    /// </summary>
    public Dictionary<string, object>? LastNavigationParameters { get; private set; }

    /// <summary>
    /// Clears navigation history and resets state.
    /// </summary>
    public void Clear()
    {
      lock (_lock)
      {
        _backStack.Clear();
        _forwardStack.Clear();
        _currentPanelId = null;
        NavigationCallCount = 0;
        BackNavigationCallCount = 0;
        ForwardNavigationCallCount = 0;
        LastNavigatedPanelId = null;
        LastNavigationParameters = null;
      }
    }

    public Task NavigateToPanelAsync(string panelId, Dictionary<string, object>? parameters = null, CancellationToken cancellationToken = default)
    {
      var previousPanelId = _currentPanelId;
      lock (_lock)
      {
        if (_currentPanelId != null)
        {
          _backStack.Add(new NavigationEntry
          {
            PanelId = _currentPanelId,
            Parameters = parameters ?? new Dictionary<string, object>()
          });
        }

        // Clear forward stack on new navigation (standard navigation behavior)
        _forwardStack.Clear();

        _currentPanelId = panelId;
        LastNavigatedPanelId = panelId;
        LastNavigationParameters = parameters;
        NavigationCallCount++;
      }

      var args = new NavigationEventArgs
      {
        PreviousPanelId = previousPanelId,
        NewPanelId = panelId,
        Parameters = parameters ?? new Dictionary<string, object>(),
        IsBackNavigation = false
      };
      NavigationChanged?.Invoke(this, args);

      return Task.CompletedTask;
    }

    public Task NavigateBackAsync(CancellationToken cancellationToken = default)
    {
      NavigationEntry? previous = null;
      string? newPanelId = null;
      lock (_lock)
      {
        if (_backStack.Count > 0)
        {
          previous = _backStack[_backStack.Count - 1];
          _backStack.RemoveAt(_backStack.Count - 1);
          newPanelId = previous.PanelId;
          var oldPanelId = _currentPanelId;
          
          // Push current to forward stack before navigating back
          if (oldPanelId != null)
          {
            _forwardStack.Add(new NavigationEntry
            {
              PanelId = oldPanelId,
              Parameters = new Dictionary<string, object>()
            });
          }
          
          _currentPanelId = newPanelId;
          BackNavigationCallCount++;
        }
      }

      if (previous != null && newPanelId != null)
      {
        var args = new NavigationEventArgs
        {
          PreviousPanelId = _currentPanelId,
          NewPanelId = newPanelId,
          Parameters = previous.Parameters,
          IsBackNavigation = true
        };
        NavigationChanged?.Invoke(this, args);
      }

      return Task.CompletedTask;
    }

    public bool CanNavigateBack()
    {
      lock (_lock)
      {
        return _backStack.Count > 0;
      }
    }

    public Task NavigateForwardAsync(CancellationToken cancellationToken = default)
    {
      NavigationEntry? next = null;
      string? newPanelId = null;
      lock (_lock)
      {
        if (_forwardStack.Count > 0)
        {
          next = _forwardStack[_forwardStack.Count - 1];
          _forwardStack.RemoveAt(_forwardStack.Count - 1);
          newPanelId = next.PanelId;
          
          // Push current to back stack
          if (_currentPanelId != null)
          {
            _backStack.Add(new NavigationEntry
            {
              PanelId = _currentPanelId,
              Parameters = new Dictionary<string, object>()
            });
          }
          
          _currentPanelId = newPanelId;
          ForwardNavigationCallCount++;
        }
      }

      if (next != null && newPanelId != null)
      {
        var args = new NavigationEventArgs
        {
          PreviousPanelId = _currentPanelId,
          NewPanelId = newPanelId,
          Parameters = next.Parameters,
          IsBackNavigation = false
        };
        NavigationChanged?.Invoke(this, args);
      }

      return Task.CompletedTask;
    }

    public bool CanNavigateForward()
    {
      lock (_lock)
      {
        return _forwardStack.Count > 0;
      }
    }

    public string? GetCurrentPanelId()
    {
      return _currentPanelId;
    }

    public IReadOnlyList<NavigationEntry> GetBackStack()
    {
      lock (_lock)
      {
        return new ReadOnlyCollection<NavigationEntry>(_backStack.ToList());
      }
    }

    public void ClearBackStack()
    {
      lock (_lock)
      {
        _backStack.Clear();
      }

      BackStackChanged?.Invoke(this, EventArgs.Empty);
    }
  }
}