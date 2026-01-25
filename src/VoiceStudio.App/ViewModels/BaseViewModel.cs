using System;
using System.Threading.Tasks;
using Microsoft.Extensions.Logging;
using Microsoft.Extensions.Logging.Abstractions;
using Microsoft.UI.Dispatching;
using CommunityToolkit.Mvvm.ComponentModel;
using VoiceStudio.App.Services;
using VoiceStudio.App.Utilities;
using VoiceStudio.Core.Exceptions;

namespace VoiceStudio.App.ViewModels
{
    /// <summary>
    /// Base ViewModel class with standardized error handling and recovery mechanisms.
    /// Implements IDisposable for proper resource cleanup when panels are switched.
    /// </summary>
    public abstract class BaseViewModel : ObservableObject, IDisposable
    {
        protected ILogger Logger { get; }
        protected DispatcherQueue Dispatcher { get; }

        protected IErrorLoggingService? ErrorLoggingService { get; }
        protected IErrorDialogService? ErrorDialogService { get; }
        protected StatePersistenceService? StatePersistenceService { get; }
        protected OperationQueueService? OperationQueueService { get; }
        protected StateCacheService? StateCacheService { get; }
        protected GracefulDegradationService? GracefulDegradationService { get; }

        // Common UI state (many panels rely on these)
        private bool _isLoading;
        public bool IsLoading
        {
            get => _isLoading;
            set => SetProperty(ref _isLoading, value);
        }

        private string? _statusMessage;
        public string? StatusMessage
        {
            get => _statusMessage;
            set => SetProperty(ref _statusMessage, value);
        }

        private string? _errorMessage;
        public string? ErrorMessage
        {
            get => _errorMessage;
            set => SetProperty(ref _errorMessage, value);
        }

        protected BaseViewModel(
            IViewModelContext context,
            IErrorLoggingService? errorLoggingService = null,
            IErrorDialogService? errorDialogService = null,
            StatePersistenceService? statePersistenceService = null,
            OperationQueueService? operationQueueService = null,
            StateCacheService? stateCacheService = null,
            GracefulDegradationService? gracefulDegradationService = null)
        {
            if (context == null) throw new ArgumentNullException(nameof(context));

            Logger = context.Logger ?? throw new ArgumentNullException(nameof(context.Logger));
            Dispatcher = context.DispatcherQueue ?? throw new ArgumentNullException(nameof(context.DispatcherQueue));

            ErrorLoggingService = errorLoggingService;
            ErrorDialogService = errorDialogService;
            StatePersistenceService = statePersistenceService;
            OperationQueueService = operationQueueService;
            StateCacheService = stateCacheService;
            GracefulDegradationService = gracefulDegradationService;
        }

        /// <summary>
        /// Temporary legacy constructor to preserve existing call sites.
        /// TODO: remove once all ViewModels are migrated to DI constructors.
        /// </summary>
        [Obsolete("Use the DI-enabled constructor that accepts IViewModelContext and explicit services.")]
        protected BaseViewModel()
            : this(
                  ResolveContext(),
                  TryResolve<IErrorLoggingService>(),
                  TryResolve<IErrorDialogService>(),
                  TryResolve<StatePersistenceService>(),
                  TryResolve<OperationQueueService>(),
                  TryResolve<StateCacheService>(),
                  TryResolve<GracefulDegradationService>())
        {
        }

        private static IViewModelContext ResolveContext()
        {
            try
            {
                var context = AppServices.GetService<IViewModelContext>();
                if (context != null)
                {
                    return context;
                }
            }
            catch
            {
                // AppServices not initialized; fall back to minimal context
            }

            var dispatcher = DispatcherQueue.GetForCurrentThread()
                ?? Microsoft.UI.Dispatching.DispatcherQueueController.CreateOnDedicatedThread().DispatcherQueue;
            return new ViewModelContext(NullLogger.Instance, dispatcher);
        }

        private static T? TryResolve<T>() where T : class
        {
            try
            {
                return AppServices.GetService<T>();
            }
            catch
            {
                return null;
            }
        }

        /// <summary>
        /// Executes an operation with state persistence before critical operations.
        /// </summary>
        protected async Task<T?> ExecuteWithStatePersistenceAsync<T>(
            Func<Task<T>> operation,
            string operationId,
            object? stateToSave = null,
            string context = "",
            bool showDialog = true)
        {
            // Save state before operation
            string? savedStatePath = null;
            if (stateToSave != null && StatePersistenceService != null)
            {
                savedStatePath = await StatePersistenceService.SaveStateAsync(operationId, stateToSave);
            }

            try
            {
                return await operation();
            }
            catch (Exception ex)
            {
                // If operation fails and we have saved state, offer to restore
                if (!string.IsNullOrEmpty(savedStatePath) && ErrorDialogService != null)
                {
                    await ErrorDialogService.ShowErrorAsync(
                        ex,
                        title: "Operation Failed",
                        context: context);
                }
                else
                {
                    await HandleErrorAsync(ex, context, showDialog);
                }
                return default(T);
            }
        }

        /// <summary>
        /// Handles an exception with logging and user notification.
        /// </summary>
        protected async Task HandleErrorAsync(Exception exception, string context = "", bool showDialog = true)
        {
            if (exception == null)
                return;

            // Log the error
            ErrorLoggingService?.LogError(exception, context);

            // Show error dialog if requested
            if (showDialog && ErrorDialogService != null)
            {
                await ErrorDialogService.ShowErrorAsync(exception, context: context);
            }
        }

        /// <summary>
        /// Handles an error message with logging and user notification.
        /// </summary>
        protected async Task HandleErrorAsync(string message, string context = "", bool showDialog = true)
        {
            if (string.IsNullOrWhiteSpace(message))
                return;

            // Log the warning
            ErrorLoggingService?.LogWarning(message, context);

            // Show error dialog if requested
            if (showDialog && ErrorDialogService != null)
            {
                await ErrorDialogService.ShowErrorAsync(new Exception(message), title: null, context: context);
            }
        }

        /// <summary>
        /// Executes an async operation with error handling and optional retry logic.
        /// </summary>
        protected async Task<T?> ExecuteWithErrorHandlingAsync<T>(
            Func<Task<T>> operation,
            string context = "",
            int maxRetries = 0,
            bool showDialog = true,
            Func<Exception, bool>? shouldRetry = null)
        {
            int attempts = 0;
            Exception? lastException = null;

            while (attempts <= maxRetries)
            {
                try
                {
                    return await operation();
                }
                catch (Exception ex)
                {
                    lastException = ex;
                    attempts++;

                    // Check if we should retry
                    bool canRetry = attempts <= maxRetries;
                    if (canRetry && shouldRetry != null)
                    {
                        canRetry = shouldRetry(ex);
                    }

                    if (canRetry && IsRetryableException(ex))
                    {
                        // Wait before retrying (exponential backoff)
                        await Task.Delay(Math.Min(1000 * (int)Math.Pow(2, attempts - 1), 10000));
                        continue;
                    }

                    // Can't retry or max retries reached
                    await HandleErrorAsync(ex, context, showDialog);
                    return default(T);
                }
            }

            // If we get here, all retries failed
            if (lastException != null)
            {
                await HandleErrorAsync(lastException, context, showDialog);
            }

            return default(T);
        }

        /// <summary>
        /// Executes an async operation with error handling and optional retry logic (void return).
        /// </summary>
        protected async Task ExecuteWithErrorHandlingAsync(
            Func<Task> operation,
            string context = "",
            int maxRetries = 0,
            bool showDialog = true,
            Func<Exception, bool>? shouldRetry = null)
        {
            int attempts = 0;
            Exception? lastException = null;

            while (attempts <= maxRetries)
            {
                try
                {
                    await operation();
                    return;
                }
                catch (Exception ex)
                {
                    lastException = ex;
                    attempts++;

                    // Check if we should retry
                    bool canRetry = attempts <= maxRetries;
                    if (canRetry && shouldRetry != null)
                    {
                        canRetry = shouldRetry(ex);
                    }

                    if (canRetry && IsRetryableException(ex))
                    {
                        // Wait before retrying (exponential backoff)
                        await Task.Delay(Math.Min(1000 * (int)Math.Pow(2, attempts - 1), 10000));
                        continue;
                    }

                    // Can't retry or max retries reached
                    await HandleErrorAsync(ex, context, showDialog);
                    return;
                }
            }

            // If we get here, all retries failed
            if (lastException != null)
            {
                await HandleErrorAsync(lastException, context, showDialog);
            }
        }

        /// <summary>
        /// Determines if an exception is retryable.
        /// </summary>
        protected virtual bool IsRetryableException(Exception exception)
        {
            return exception switch
            {
                BackendTimeoutException => true,
                BackendUnavailableException => true,
                BackendServerException bex when bex.StatusCode >= 500 => true,
                System.Net.Http.HttpRequestException => true,
                TaskCanceledException => true,
                TimeoutException => true,
                BackendException bex when bex.IsRetryable => true,
                _ => false
            };
        }

        /// <summary>
        /// Logs an informational message.
        /// </summary>
        protected void LogInfo(string message, string context = "")
        {
            ErrorLoggingService?.LogInfo(message, context);
        }

        /// <summary>
        /// Logs a warning message.
        /// </summary>
        protected void LogWarning(string message, string context = "")
        {
            ErrorLoggingService?.LogWarning(message, context);
        }

        #region IDisposable Implementation

        private bool _disposed = false;

        /// <summary>
        /// Indicates whether this ViewModel has been disposed.
        /// </summary>
        protected bool IsDisposed => _disposed;

        /// <summary>
        /// Disposes the ViewModel and releases resources.
        /// </summary>
        public void Dispose()
        {
            Dispose(true);
            GC.SuppressFinalize(this);
        }

        /// <summary>
        /// Protected dispose method that can be overridden by derived classes.
        /// </summary>
        /// <param name="disposing">True if called from Dispose(), false if called from finalizer</param>
        protected virtual void Dispose(bool disposing)
        {
            if (!_disposed)
            {
                if (disposing)
                {
                    // Dispose managed resources here
                    // Derived classes should override this method to dispose their specific resources
                }
                _disposed = true;
            }
        }

        /// <summary>
        /// Finalizer - only called if Dispose() was not called
        /// </summary>
        ~BaseViewModel()
        {
            Dispose(false);
        }

        #endregion
    }
}

