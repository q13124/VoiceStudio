using System;
using System.Threading.Tasks;
using VoiceStudio.App.Utilities;
using VoiceStudio.Core.Services;
using VoiceStudio.App.Logging;

namespace VoiceStudio.App.Services
{
  /// <summary>
  /// Centralized error coordination implementation.
  /// Consolidates error logging, dialog display, and state management.
  /// </summary>
  public class ErrorCoordinator : IErrorCoordinator
  {
    private readonly IErrorLoggingService? _loggingService;
    private readonly IErrorDialogService? _dialogService;
    private readonly object _lock = new();

    private string? _currentError;
    private bool _hasError;

    public ErrorCoordinator(
        IErrorLoggingService? loggingService = null,
        IErrorDialogService? dialogService = null)
    {
      _loggingService = loggingService;
      _dialogService = dialogService;
    }

    /// <inheritdoc />
    public string? CurrentError
    {
      get
      {
        lock (_lock) return _currentError;
      }
    }

    /// <inheritdoc />
    public bool HasError
    {
      get
      {
        lock (_lock) return _hasError;
      }
    }

    /// <inheritdoc />
    public event Action<ErrorInfo>? ErrorOccurred;

    /// <inheritdoc />
    public event Action? ErrorCleared;

    /// <inheritdoc />
    public async Task HandleErrorAsync(
        Exception ex,
        string context,
        ErrorSeverity severity = ErrorSeverity.Error,
        bool showDialog = true)
    {
      if (ex == null) return;

      // Generate user-friendly message
      var userMessage = ErrorHandler.GetUserFriendlyMessage(ex);
      var timestamp = DateTimeOffset.UtcNow;

      // Log the error
      try
      {
        _loggingService?.LogError(ex, context);
      }
      catch (Exception logEx)
      {
        ErrorLogger.LogWarning($"Best effort operation failed: {logEx.Message}", "ErrorCoordinator.HandleErrorAsync");
      }

      // Update state
      lock (_lock)
      {
        _currentError = userMessage;
        _hasError = true;
      }

      // Create error info for event
      var errorInfo = new ErrorInfo
      {
        Exception = ex,
        Context = context,
        Severity = severity,
        Timestamp = timestamp,
        UserMessage = userMessage,
        DialogShown = showDialog && _dialogService != null
      };

      // Raise event for subscribers
      try
      {
        ErrorOccurred?.Invoke(errorInfo);
      }
      catch (Exception eventEx)
      {
        ErrorLogger.LogWarning($"Best effort operation failed: {eventEx.Message}", "ErrorCoordinator.HandleErrorAsync");
      }

      // Show dialog if requested
      if (showDialog && _dialogService != null)
      {
        try
        {
          await _dialogService.ShowErrorAsync(ex, context);
        }
        catch (Exception dialogEx)
        {
          ErrorLogger.LogWarning($"Best effort operation failed: {dialogEx.Message}", "ErrorCoordinator.HandleErrorAsync");
        }
      }
    }

    /// <inheritdoc />
    public void ClearError()
    {
      lock (_lock)
      {
        _currentError = null;
        _hasError = false;
      }

      try
      {
        ErrorCleared?.Invoke();
      }
      catch (Exception ex)
      {
        ErrorLogger.LogWarning($"Best effort operation failed: {ex.Message}", "ErrorCoordinator.ClearError");
      }
    }
  }
}