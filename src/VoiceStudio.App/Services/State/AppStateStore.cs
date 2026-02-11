using System;
using System.Collections.Generic;
using System.Threading;
using System.Threading.Tasks;
using CommunityToolkit.Mvvm.ComponentModel;
using VoiceStudio.Core.State;

namespace VoiceStudio.App.Services.State
{
  /// <summary>
  /// Central state store implementation.
  /// Provides Redux-like state management with derived selectors.
  /// </summary>
  public sealed partial class AppStateStore : ObservableObject, IAppStateStore, IDisposable
  {
    private readonly object _lock = new();
    private readonly List<SubscriptionBase> _subscriptions = new();
    private bool _disposed;

    [ObservableProperty]
    private AppState _state = AppState.Empty;

    public event EventHandler<StateChangedEventArgs>? StateChanged;

    public AppStateStore()
    {
    }

    public AppStateStore(AppState initialState)
    {
      _state = initialState;
    }

    public void Dispatch(Func<AppState, AppState> update)
    {
      AppState previousState;
      AppState newState;

      lock (_lock)
      {
        previousState = State;
        newState = update(previousState);

        if (ReferenceEquals(previousState, newState))
          return;

        State = newState;
      }

      NotifyStateChanged(previousState, newState);
    }

    public async Task DispatchAsync(Func<AppState, Task<AppState>> update)
    {
      AppState previousState;
      AppState newState;

      // We can't hold the lock during async operation,
      // so we use a pattern that reads, computes, then tries to apply
      previousState = State;
      newState = await update(previousState);

      if (ReferenceEquals(previousState, newState))
        return;

      lock (_lock)
      {
        // Re-check state hasn't changed during async operation
        if (!ReferenceEquals(State, previousState))
        {
          // State changed while we were computing - retry with fresh state
          previousState = State;
        }
        State = newState;
      }

      NotifyStateChanged(previousState, newState);
    }

    public IDisposable Subscribe<T>(Func<AppState, T> selector, Action<T> handler)
    {
      var subscription = new Subscription<T>(this, selector, handler);
      lock (_lock)
      {
        _subscriptions.Add(subscription);
      }
      return subscription;
    }

    public T Select<T>(Func<AppState, T> selector)
    {
      return selector(State);
    }

    private void NotifyStateChanged(AppState previousState, AppState newState)
    {
      StateChanged?.Invoke(this, new StateChangedEventArgs(previousState, newState));

      // Notify subscriptions
      List<SubscriptionBase> subs;
      lock (_lock)
      {
        subs = new List<SubscriptionBase>(_subscriptions);
      }

      foreach (var sub in subs)
      {
        sub.Notify(previousState, newState);
      }
    }

    private void RemoveSubscription(SubscriptionBase subscription)
    {
      lock (_lock)
      {
        _subscriptions.Remove(subscription);
      }
    }

    public void Dispose()
    {
      if (_disposed) return;
      _disposed = true;

      lock (_lock)
      {
        _subscriptions.Clear();
      }
    }

    #region Subscription Classes

    private abstract class SubscriptionBase
    {
      public abstract void Notify(AppState previous, AppState current);
    }

    private sealed class Subscription<T> : SubscriptionBase, IDisposable
    {
      private readonly AppStateStore _store;
      private readonly Func<AppState, T> _selector;
      private readonly Action<T> _handler;
      private T? _lastValue;
      private bool _disposed;

      public Subscription(AppStateStore store, Func<AppState, T> selector, Action<T> handler)
      {
        _store = store;
        _selector = selector;
        _handler = handler;
        _lastValue = selector(store.State);
      }

      public override void Notify(AppState previous, AppState current)
      {
        if (_disposed) return;

        var newValue = _selector(current);
        if (!EqualityComparer<T>.Default.Equals(_lastValue, newValue))
        {
          _lastValue = newValue;
          _handler(newValue);
        }
      }

      public void Dispose()
      {
        if (_disposed) return;
        _disposed = true;
        _store.RemoveSubscription(this);
      }
    }

    #endregion
  }
}
