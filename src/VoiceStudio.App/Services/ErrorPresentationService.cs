using System;
using VoiceStudio.Core.Services;

namespace VoiceStudio.App.Services
{
  /// <summary>
  /// Implementation of error presentation service that decides the best way to present errors.
  /// </summary>
  public class ErrorPresentationService : IErrorPresentationService
  {
    private readonly IErrorDialogService? _errorDialogService;
    private readonly IErrorLoggingService? _errorLoggingService;

    // ToastNotificationService requires UI elements and is registered manually after UI creation.
    // Access it lazily via AppServices to avoid DI resolution failures at startup.
    private ToastNotificationService? ToastNotificationService => AppServices.TryGetToastNotificationService();

    public ErrorPresentationService(
        IErrorDialogService? errorDialogService = null,
        IErrorLoggingService? errorLoggingService = null)
    {
      _errorDialogService = errorDialogService;
      _errorLoggingService = errorLoggingService;
    }

    public void ShowError(Exception exception, string context, ErrorPresentationType type = ErrorPresentationType.Toast)
    {
      if (exception == null)
        return;

      // Log the error
      _errorLoggingService?.LogError(exception, context);

      // Determine presentation type if not explicitly specified
      if (type == ErrorPresentationType.Toast)
      {
        type = DeterminePresentationType(exception);
      }

      // Present error based on type
      switch (type)
      {
        case ErrorPresentationType.Toast:
          ShowErrorToast(exception, context);
          break;

        case ErrorPresentationType.Dialog:
          ShowErrorDialog(exception, context);
          break;

        case ErrorPresentationType.Inline:
          // Inline errors are typically handled by the ViewModel/View
          // This service can't directly set inline errors, so fall back to toast
          ShowErrorToast(exception, context);
          break;
      }
    }

    public void ShowError(string message, string context, ErrorPresentationType type = ErrorPresentationType.Toast)
    {
      if (string.IsNullOrWhiteSpace(message))
        return;

      // Log the error
      _errorLoggingService?.LogWarning(message, context);

      // Present error based on type
      switch (type)
      {
        case ErrorPresentationType.Toast:
          ToastNotificationService?.ShowError(message, "Error");
          break;

        case ErrorPresentationType.Dialog:
          _ = _errorDialogService?.ShowErrorAsync(message, "Error", context);
          break;

        case ErrorPresentationType.Inline:
          // Inline errors are typically handled by the ViewModel/View
          // This service can't directly set inline errors, so fall back to toast
          ToastNotificationService?.ShowError(message, "Error");
          break;
      }
    }

    private ErrorPresentationType DeterminePresentationType(Exception exception)
    {
      // Critical errors that require user action should use dialogs
      if (IsCriticalError(exception))
      {
        return ErrorPresentationType.Dialog;
      }

      // Transient errors can use toasts
      if (IsTransientError(exception))
      {
        return ErrorPresentationType.Toast;
      }

      // Default to toast for most errors
      return ErrorPresentationType.Toast;
    }

    private bool IsCriticalError(Exception exception)
    {
      // Critical errors that require user action
      return exception is
          System.Security.SecurityException or
          System.UnauthorizedAccessException or
          System.IO.IOException or
          OutOfMemoryException;
    }

    private bool IsTransientError(Exception exception)
    {
      // Transient errors that might resolve on retry
      return exception is
          System.Net.Http.HttpRequestException or
          System.TimeoutException or
          System.Threading.Tasks.TaskCanceledException or
          VoiceStudio.Core.Exceptions.BackendUnavailableException or
          VoiceStudio.Core.Exceptions.BackendTimeoutException;
    }

    private void ShowErrorToast(Exception exception, string _)
    {
      var userMessage = GetUserFriendlyMessage(exception);
      ToastNotificationService?.ShowError(userMessage, GetErrorTitle(exception));
    }

    private void ShowErrorDialog(Exception exception, string context)
    {
      _ = _errorDialogService?.ShowErrorAsync(exception, GetErrorTitle(exception), context);
    }

    private string GetUserFriendlyMessage(Exception exception)
    {
      return exception switch
      {
        VoiceStudio.Core.Exceptions.BackendUnavailableException => "Unable to connect to the backend. Please check your connection and try again.",
        VoiceStudio.Core.Exceptions.BackendTimeoutException => "The request timed out. Please try again.",
        VoiceStudio.Core.Exceptions.BackendAuthenticationException => "Authentication failed. Please check your credentials.",
        VoiceStudio.Core.Exceptions.BackendNotFoundException => "The requested resource was not found.",
        VoiceStudio.Core.Exceptions.BackendValidationException => "Validation failed. Please check your input.",
        System.Net.Http.HttpRequestException => "Network error occurred. Please check your connection.",
        System.TimeoutException => "The operation timed out. Please try again.",
        OutOfMemoryException => "Insufficient memory. Please close other applications and try again.",
        _ => exception.Message
      };
    }

    private string GetErrorTitle(Exception exception)
    {
      return exception switch
      {
        VoiceStudio.Core.Exceptions.BackendUnavailableException => "Connection Error",
        VoiceStudio.Core.Exceptions.BackendTimeoutException => "Timeout Error",
        VoiceStudio.Core.Exceptions.BackendAuthenticationException => "Authentication Error",
        VoiceStudio.Core.Exceptions.BackendNotFoundException => "Not Found",
        VoiceStudio.Core.Exceptions.BackendValidationException => "Validation Error",
        System.Net.Http.HttpRequestException => "Network Error",
        System.TimeoutException => "Timeout Error",
        OutOfMemoryException => "Memory Error",
        _ => "Error"
      };
    }
  }
}