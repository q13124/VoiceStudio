using System;
using System.Threading.Tasks;
using VoiceStudio.App.Utilities;
using VoiceStudio.Core.Services;

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
            catch
            {
                // Don't let logging failures propagate
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
            catch
            {
                // Don't let event handlers crash error handling
            }

            // Show dialog if requested
            if (showDialog && _dialogService != null)
            {
                try
                {
                    await _dialogService.ShowErrorAsync(ex, context);
                }
                catch
                {
                    // Dialog display failures shouldn't propagate
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
            catch
            {
                // Don't let event handlers crash
            }
        }
    }
}
