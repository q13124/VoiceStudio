using System;
using System.Threading.Tasks;

namespace VoiceStudio.Core.State
{
  /// <summary>
  /// Central state store interface.
  /// Provides access to application state and change notifications.
  /// </summary>
  public interface IAppStateStore
  {
    /// <summary>
    /// Gets the current application state.
    /// </summary>
    AppState State { get; }

    /// <summary>
    /// Occurs when any part of the state changes.
    /// </summary>
    event EventHandler<StateChangedEventArgs>? StateChanged;

    /// <summary>
    /// Updates the state using an update function.
    /// </summary>
    /// <param name="update">Function that takes current state and returns new state.</param>
    void Dispatch(Func<AppState, AppState> update);

    /// <summary>
    /// Updates the state using an async update function.
    /// </summary>
    /// <param name="update">Async function that takes current state and returns new state.</param>
    Task DispatchAsync(Func<AppState, Task<AppState>> update);

    /// <summary>
    /// Subscribes to changes in a specific part of the state.
    /// </summary>
    /// <typeparam name="T">The type of the selected state slice.</typeparam>
    /// <param name="selector">Function to select a slice of state.</param>
    /// <param name="handler">Handler called when the selected slice changes.</param>
    /// <returns>A disposable subscription.</returns>
    IDisposable Subscribe<T>(Func<AppState, T> selector, Action<T> handler);

    /// <summary>
    /// Gets a derived value from the state.
    /// </summary>
    /// <typeparam name="T">The type of the derived value.</typeparam>
    /// <param name="selector">Function to compute the derived value.</param>
    /// <returns>The computed value.</returns>
    T Select<T>(Func<AppState, T> selector);
  }

  /// <summary>
  /// Event arguments for state changes.
  /// </summary>
  public sealed class StateChangedEventArgs : EventArgs
  {
    /// <summary>
    /// Gets the previous state.
    /// </summary>
    public AppState PreviousState { get; }

    /// <summary>
    /// Gets the new state.
    /// </summary>
    public AppState NewState { get; }

    /// <summary>
    /// Gets the name of the action that caused the change (optional).
    /// </summary>
    public string? ActionName { get; }

    public StateChangedEventArgs(AppState previousState, AppState newState, string? actionName = null)
    {
      PreviousState = previousState;
      NewState = newState;
      ActionName = actionName;
    }
  }
}
