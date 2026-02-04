using System;
using System.Collections.Concurrent;
using System.Threading;
using System.Windows.Input;

namespace VoiceStudio.App.Utilities
{
  /// <summary>
  /// Helper utility for preventing duplicate command execution and tracking in-flight operations.
  /// </summary>
  public static class CommandGuard
  {
    private static readonly ConcurrentDictionary<ICommand, ExecutionState> _executionStates = new();

    /// <summary>
    /// Checks if a command is currently executing.
    /// </summary>
    /// <param name="command">The command to check.</param>
    /// <returns>True if the command is executing, false otherwise.</returns>
    public static bool IsCommandExecuting(ICommand command)
    {
      if (command == null)
        return false;

      return _executionStates.TryGetValue(command, out var state) && state.IsExecuting;
    }

    /// <summary>
    /// Prevents duplicate execution by checking if command is already executing.
    /// </summary>
    /// <param name="command">The command to guard.</param>
    /// <returns>True if execution should proceed, false if already executing.</returns>
    public static bool PreventDuplicateExecution(ICommand command)
    {
      if (command == null)
        return false;

      var state = _executionStates.GetOrAdd(command, _ => new ExecutionState());

      lock (state)
      {
        if (state.IsExecuting)
          return false;

        state.IsExecuting = true;
        state.ExecutionCount++;
        return true;
      }
    }

    /// <summary>
    /// Marks a command execution as complete.
    /// </summary>
    /// <param name="command">The command that completed.</param>
    public static void MarkExecutionComplete(ICommand command)
    {
      if (command == null)
        return;

      if (_executionStates.TryGetValue(command, out var state))
      {
        lock (state)
        {
          state.IsExecuting = false;
        }
      }
    }

    /// <summary>
    /// Creates an execution scope that automatically marks execution as complete on disposal.
    /// </summary>
    /// <param name="command">The command to create a scope for.</param>
    /// <returns>An IDisposable scope that marks execution complete on disposal.</returns>
    public static IDisposable CreateExecutionScope(ICommand command)
    {
      return new ExecutionScope(command);
    }

    /// <summary>
    /// Gets the execution count for a command (for debugging/monitoring).
    /// </summary>
    /// <param name="command">The command to check.</param>
    /// <returns>The number of times the command has been executed.</returns>
    public static int GetExecutionCount(ICommand command)
    {
      if (command == null)
        return 0;

      return _executionStates.TryGetValue(command, out var state) ? state.ExecutionCount : 0;
    }

    /// <summary>
    /// Clears all execution state (useful for testing or reset).
    /// </summary>
    public static void ClearAll()
    {
      _executionStates.Clear();
    }

    private class ExecutionState
    {
      public bool IsExecuting { get; set; }
      public int ExecutionCount { get; set; }
    }

    private class ExecutionScope : IDisposable
    {
      private readonly ICommand _command;
      private bool _disposed;

      public ExecutionScope(ICommand command)
      {
        _command = command;
      }

      public void Dispose()
      {
        if (!_disposed)
        {
          MarkExecutionComplete(_command);
          _disposed = true;
        }
      }
    }
  }
}