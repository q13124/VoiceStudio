using System;
using System.Collections.Generic;
using System.Diagnostics;
using System.Linq;
using System.Text;

namespace VoiceStudio.App.Utilities
{
  /// <summary>
  /// Performance budgets for different operations.
  /// </summary>
  public static class PerformanceBudgets
  {
    /// <summary>
    /// Startup time budget: 3 seconds
    /// </summary>
    public const int StartupMs = 3000;

    /// <summary>
    /// Panel load time budget: 500 milliseconds
    /// </summary>
    public const int PanelLoadMs = 500;

    /// <summary>
    /// Render frame budget: 16.67 milliseconds (60fps)
    /// </summary>
    public const double RenderFrameMs = 16.67;

    /// <summary>
    /// API response budget: 1 second
    /// </summary>
    public const int ApiResponseMs = 1000;

    /// <summary>
    /// Command execution budget: 500 milliseconds
    /// </summary>
    public const int CommandExecutionMs = 500;
  }

  /// <summary>
  /// Performance budget violation event arguments.
  /// </summary>
  public class BudgetViolationEventArgs : EventArgs
  {
    public string OperationName { get; }
    public int BudgetMs { get; }
    public long ActualMs { get; }
    public double ViolationPercent { get; }
    public DateTime Timestamp { get; }

    public BudgetViolationEventArgs(string operationName, int budgetMs, long actualMs)
    {
      OperationName = operationName;
      BudgetMs = budgetMs;
      ActualMs = actualMs;
      Timestamp = DateTime.Now;
      ViolationPercent = (double)(actualMs - budgetMs) / budgetMs * 100.0;
    }
  }

  /// <summary>
  /// Simple performance profiler for measuring operation timings with budget enforcement.
  /// </summary>
  public class PerformanceProfiler : IDisposable
  {
    private readonly string _operationName;
    private readonly Stopwatch _stopwatch;
    private readonly Dictionary<string, TimeSpan> _checkpoints;
    private readonly int? _budgetMs;
    private bool _disposed;
    private bool _budgetViolated;

    /// <summary>
    /// Event raised when a performance budget is violated.
    /// </summary>
    public static event EventHandler<BudgetViolationEventArgs>? BudgetViolated;

    public PerformanceProfiler(string operationName, int? budgetMs = null)
    {
      _operationName = operationName;
      _budgetMs = budgetMs;
      _stopwatch = Stopwatch.StartNew();
      _checkpoints = new Dictionary<string, TimeSpan>();
    }

    /// <summary>
    /// Records a checkpoint with a name.
    /// </summary>
    public void Checkpoint(string name)
    {
      if (_disposed)
        return;

      _checkpoints[name] = _stopwatch.Elapsed;
    }

    /// <summary>
    /// Gets the elapsed time since the profiler started.
    /// </summary>
    public TimeSpan Elapsed => _stopwatch.Elapsed;

    /// <summary>
    /// Gets the elapsed time in milliseconds.
    /// </summary>
    public long ElapsedMilliseconds => _stopwatch.ElapsedMilliseconds;

    /// <summary>
    /// Gets all checkpoints.
    /// </summary>
    public IReadOnlyDictionary<string, TimeSpan> Checkpoints => _checkpoints;

    /// <summary>
    /// Gets a formatted report of all timings.
    /// </summary>
    public string GetReport()
    {
      var sb = new StringBuilder();
      sb.AppendLine($"=== Performance Report: {_operationName} ===")
        .AppendLine($"Total Time: {_stopwatch.Elapsed.TotalMilliseconds:F2} ms")
        .AppendLine();

      if (_checkpoints.Any())
      {
        sb.AppendLine("Checkpoints:");
        TimeSpan previous = TimeSpan.Zero;
        foreach (var checkpoint in _checkpoints.OrderBy(c => c.Value))
        {
          var elapsed = checkpoint.Value - previous;
          sb.AppendLine($"  {checkpoint.Key}: {checkpoint.Value.TotalMilliseconds:F2} ms (+{elapsed.TotalMilliseconds:F2} ms)");
          previous = checkpoint.Value;
        }
      }

      return sb.ToString();
    }

    /// <summary>
    /// Checks if the operation exceeded its budget and raises an event if so.
    /// </summary>
    public void CheckBudget()
    {
      if (_budgetMs.HasValue && !_budgetViolated)
      {
        var elapsedMs = _stopwatch.ElapsedMilliseconds;
        if (elapsedMs > _budgetMs.Value)
        {
          _budgetViolated = true;
          BudgetViolated?.Invoke(this, new BudgetViolationEventArgs(_operationName, _budgetMs.Value, elapsedMs));
        }
      }
    }

    /// <summary>
    /// Gets whether the budget was violated.
    /// </summary>
    public bool IsBudgetViolated => _budgetViolated;

    public void Dispose()
    {
      if (_disposed)
        return;

      CheckBudget();
      _stopwatch.Stop();
      _disposed = true;
    }

    // Compatibility helpers: many ViewModels call PerformanceProfiler.StartXxx()
    public static PerformanceProfiler Start(string operationName, int? budgetMs = null) => Profiler.Start(operationName, budgetMs);
    public static PerformanceProfiler StartStartup() => Profiler.StartStartup();
    public static PerformanceProfiler StartPanelLoad(string panelName) => Profiler.StartPanelLoad(panelName);
    public static PerformanceProfiler StartApiCall(string endpoint) => Profiler.StartApiCall(endpoint);
    public static PerformanceProfiler StartCommand(string commandName) => Profiler.StartCommand(commandName);
  }

  /// <summary>
  /// Static helper for quick profiling with budget enforcement.
  /// </summary>
  public static class Profiler
  {
    private static readonly List<PerformanceProfiler> _activeProfilers = new();
    private static readonly object _lock = new();

    /// <summary>
    /// Starts profiling an operation.
    /// </summary>
    public static PerformanceProfiler Start(string operationName, int? budgetMs = null)
    {
      var profiler = new PerformanceProfiler(operationName, budgetMs);
      lock (_lock)
      {
        _activeProfilers.Add(profiler);
      }
      return profiler;
    }

    /// <summary>
    /// Starts profiling startup with budget enforcement.
    /// </summary>
    public static PerformanceProfiler StartStartup()
    {
      return Start("Application Startup", PerformanceBudgets.StartupMs);
    }

    /// <summary>
    /// Starts profiling panel load with budget enforcement.
    /// </summary>
    public static PerformanceProfiler StartPanelLoad(string panelName)
    {
      return Start($"Panel Load: {panelName}", PerformanceBudgets.PanelLoadMs);
    }

    /// <summary>
    /// Starts profiling API call with budget enforcement.
    /// </summary>
    public static PerformanceProfiler StartApiCall(string endpoint)
    {
      return Start($"API Call: {endpoint}", PerformanceBudgets.ApiResponseMs);
    }

    /// <summary>
    /// Starts profiling command execution with budget enforcement.
    /// </summary>
    public static PerformanceProfiler StartCommand(string commandName)
    {
      return Start($"Command: {commandName}", PerformanceBudgets.CommandExecutionMs);
    }

    /// <summary>
    /// Measures the execution time of an action.
    /// </summary>
    public static TimeSpan Measure(string operationName, Action action)
    {
      using var profiler = Start(operationName);
      action();
      return profiler.Elapsed;
    }

    /// <summary>
    /// Measures the execution time of a function.
    /// </summary>
    public static (T Result, TimeSpan Elapsed) Measure<T>(string operationName, Func<T> func)
    {
      using var profiler = Start(operationName);
      var result = func();
      return (result, profiler.Elapsed);
    }

    /// <summary>
    /// Measures the execution time of an async action.
    /// </summary>
    public static async System.Threading.Tasks.Task<TimeSpan> MeasureAsync(string operationName, Func<System.Threading.Tasks.Task> action)
    {
      using var profiler = Start(operationName);
      await action();
      return profiler.Elapsed;
    }

    /// <summary>
    /// Measures the execution time of an async function.
    /// </summary>
    public static async System.Threading.Tasks.Task<(T Result, TimeSpan Elapsed)> MeasureAsync<T>(string operationName, Func<System.Threading.Tasks.Task<T>> func)
    {
      using var profiler = Start(operationName);
      var result = await func();
      return (result, profiler.Elapsed);
    }
  }
}