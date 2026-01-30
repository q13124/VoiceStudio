using System;
using System.Threading;
using System.Threading.Tasks;
using CommunityToolkit.Mvvm.Input;
using System.ComponentModel;

namespace VoiceStudio.App.Utilities
{
  /// <summary>
  /// Enhanced AsyncRelayCommand with in-flight guard, progress reporting, and cancellation support.
  /// Wraps CommunityToolkit.Mvvm.Input.AsyncRelayCommand with additional features.
  /// </summary>
  public class EnhancedAsyncRelayCommand : IAsyncRelayCommand, INotifyPropertyChanged
  {
    private readonly AsyncRelayCommand _innerCommand;
    private bool _isExecuting;
    private double _progress;
    private CancellationTokenSource? _cancellationTokenSource;

    public EnhancedAsyncRelayCommand(Func<Task> execute, Func<bool>? canExecute = null)
    {
      _innerCommand = new AsyncRelayCommand(
          async () =>
          {
            if (_isExecuting)
              return;

            _isExecuting = true;
            _progress = 0;
            OnPropertyChanged(nameof(IsExecuting));
            OnPropertyChanged(nameof(Progress));
            RaiseCanExecuteChanged();

            try
            {
              _cancellationTokenSource = new CancellationTokenSource();
              await execute();
            }
            finally
            {
              _isExecuting = false;
              _progress = 0;
              OnPropertyChanged(nameof(IsExecuting));
              OnPropertyChanged(nameof(Progress));
              RaiseCanExecuteChanged();
            }
          },
          canExecute ?? (() => true));

      _innerCommand.CanExecuteChanged += (_, _) => RaiseCanExecuteChanged();
    }

    public EnhancedAsyncRelayCommand(Func<CancellationToken, Task> execute, Func<bool>? canExecute = null)
    {
      _innerCommand = new AsyncRelayCommand(
          async () =>
          {
            if (_isExecuting)
              return;

            _isExecuting = true;
            _progress = 0;
            OnPropertyChanged(nameof(IsExecuting));
            OnPropertyChanged(nameof(Progress));
            RaiseCanExecuteChanged();

            try
            {
              _cancellationTokenSource = new CancellationTokenSource();
              await execute(_cancellationTokenSource.Token);
            }
            finally
            {
              _isExecuting = false;
              _progress = 0;
              OnPropertyChanged(nameof(IsExecuting));
              OnPropertyChanged(nameof(Progress));
              RaiseCanExecuteChanged();
            }
          },
          canExecute ?? (() => true));

      _innerCommand.CanExecuteChanged += (_, _) => RaiseCanExecuteChanged();
    }

    /// <summary>
    /// Gets whether the command is currently executing.
    /// </summary>
    public bool IsExecuting
    {
      get => _isExecuting;
      private set
      {
        if (_isExecuting != value)
        {
          _isExecuting = value;
          OnPropertyChanged(nameof(IsExecuting));
        }
      }
    }

    /// <summary>
    /// Gets the current progress (0-100).
    /// </summary>
    public double Progress
    {
      get => _progress;
      private set
      {
        if (Math.Abs(_progress - value) > 0.01)
        {
          _progress = Math.Max(0, Math.Min(100, value));
          OnPropertyChanged(nameof(Progress));
        }
      }
    }

    /// <summary>
    /// Reports progress (0-100).
    /// </summary>
    public void ReportProgress(double progress)
    {
      Progress = progress;
    }

    /// <summary>
    /// Cancels the command execution.
    /// </summary>
    public void Cancel()
    {
      _cancellationTokenSource?.Cancel();
    }

    /// <summary>
    /// Gets the cancellation token for the current execution.
    /// </summary>
    public CancellationToken? CancellationToken => _cancellationTokenSource?.Token;

    // Delegate to inner command
    public bool CanExecute(object? parameter) => !_isExecuting && _innerCommand.CanExecute(parameter);

    public void Execute(object? parameter) => _innerCommand.Execute(parameter);

    public Task ExecuteAsync(object? parameter) => _innerCommand.ExecuteAsync(parameter);

    public void NotifyCanExecuteChanged() => _innerCommand.NotifyCanExecuteChanged();

    // IAsyncRelayCommand members
    public Task? ExecutionTask => _innerCommand.ExecutionTask;
    public bool CanBeCanceled => _innerCommand.CanBeCanceled;
    public bool IsCancellationRequested => _innerCommand.IsCancellationRequested;
    public bool IsRunning => _innerCommand.IsRunning;

    public event EventHandler? CanExecuteChanged;

    public event PropertyChangedEventHandler? PropertyChanged;

    private void RaiseCanExecuteChanged()
    {
      CanExecuteChanged?.Invoke(this, EventArgs.Empty);
    }

    protected virtual void OnPropertyChanged(string propertyName)
    {
      PropertyChanged?.Invoke(this, new PropertyChangedEventArgs(propertyName));
    }
  }

  /// <summary>
  /// Enhanced AsyncRelayCommand with parameter support.
  /// </summary>
  public class EnhancedAsyncRelayCommand<T> : IAsyncRelayCommand<T>, INotifyPropertyChanged
  {
    private readonly AsyncRelayCommand<T> _innerCommand;
    private readonly Func<T?, bool>? _canExecute;
    private bool _isExecuting;
    private double _progress;
    private CancellationTokenSource? _cancellationTokenSource;

    public EnhancedAsyncRelayCommand(Func<T?, Task> execute, Func<T?, bool>? canExecute = null)
    {
      _canExecute = canExecute;
      _innerCommand = new AsyncRelayCommand<T>(
          async (param) =>
          {
            if (_isExecuting)
              return;

            _isExecuting = true;
            _progress = 0;
            OnPropertyChanged(nameof(IsExecuting));
            OnPropertyChanged(nameof(Progress));

            try
            {
              _cancellationTokenSource = new CancellationTokenSource();
              await execute(param);
            }
            finally
            {
              _isExecuting = false;
              _progress = 0;
              OnPropertyChanged(nameof(IsExecuting));
              OnPropertyChanged(nameof(Progress));
            }
          });
    }

    public EnhancedAsyncRelayCommand(Func<T?, CancellationToken, Task> execute, Func<T?, bool>? canExecute = null)
    {
      _canExecute = canExecute;
      _innerCommand = new AsyncRelayCommand<T>(
          async (param) =>
          {
            if (_isExecuting)
              return;

            _isExecuting = true;
            _progress = 0;
            OnPropertyChanged(nameof(IsExecuting));
            OnPropertyChanged(nameof(Progress));

            try
            {
              _cancellationTokenSource = new CancellationTokenSource();
              await execute(param, _cancellationTokenSource.Token);
            }
            finally
            {
              _isExecuting = false;
              _progress = 0;
              OnPropertyChanged(nameof(IsExecuting));
              OnPropertyChanged(nameof(Progress));
            }
          });
    }

    public bool IsExecuting
    {
      get => _isExecuting;
      private set
      {
        if (_isExecuting != value)
        {
          _isExecuting = value;
          OnPropertyChanged(nameof(IsExecuting));
        }
      }
    }

    public double Progress
    {
      get => _progress;
      private set
      {
        if (Math.Abs(_progress - value) > 0.01)
        {
          _progress = Math.Max(0, Math.Min(100, value));
          OnPropertyChanged(nameof(Progress));
        }
      }
    }

    public void ReportProgress(double progress)
    {
      Progress = progress;
    }

    public void Cancel()
    {
      _cancellationTokenSource?.Cancel();
    }

    public CancellationToken? CancellationToken => _cancellationTokenSource?.Token;

    public bool CanExecute(object? parameter) => !_isExecuting && _innerCommand.CanExecute(parameter);

    public void Execute(object? parameter) => _innerCommand.Execute(parameter);

    public Task ExecuteAsync(object? parameter) => _innerCommand.ExecuteAsync(parameter);

    public void NotifyCanExecuteChanged() => _innerCommand.NotifyCanExecuteChanged();

    // IAsyncRelayCommand<T> members
    public Task? ExecutionTask => _innerCommand.ExecutionTask;
    public bool CanBeCanceled => _innerCommand.CanBeCanceled;
    public bool IsCancellationRequested => _innerCommand.IsCancellationRequested;
    public bool IsRunning => _innerCommand.IsRunning;

    // IRelayCommand<T> members
    public bool CanExecute(T? parameter) => !_isExecuting && _innerCommand.CanExecute(parameter);
    public void Execute(T? parameter) => _innerCommand.Execute(parameter);
    public Task ExecuteAsync(T? parameter) => _innerCommand.ExecuteAsync(parameter);

    public event EventHandler? CanExecuteChanged
    {
      add => _innerCommand.CanExecuteChanged += value;
      remove => _innerCommand.CanExecuteChanged -= value;
    }

    public event PropertyChangedEventHandler? PropertyChanged;

    protected virtual void OnPropertyChanged(string propertyName)
    {
      PropertyChanged?.Invoke(this, new PropertyChangedEventArgs(propertyName));
    }
  }
}
