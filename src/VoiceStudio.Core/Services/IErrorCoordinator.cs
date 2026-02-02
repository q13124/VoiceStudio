using System;
using System.Threading.Tasks;

namespace VoiceStudio.Core.Services
{
    /// <summary>
    /// Error severity levels for coordinated error handling.
    /// </summary>
    public enum ErrorSeverity
    {
        /// <summary>Informational message, not an error.</summary>
        Info,
        /// <summary>Warning that doesn't block operation.</summary>
        Warning,
        /// <summary>Error that may block operation.</summary>
        Error,
        /// <summary>Critical error requiring immediate attention.</summary>
        Critical
    }

    /// <summary>
    /// Information about an error occurrence for event subscribers.
    /// </summary>
    public class ErrorInfo
    {
        /// <summary>The exception that occurred.</summary>
        public Exception Exception { get; init; } = null!;
        
        /// <summary>Context describing where the error occurred.</summary>
        public string Context { get; init; } = string.Empty;
        
        /// <summary>Error severity level.</summary>
        public ErrorSeverity Severity { get; init; }
        
        /// <summary>Timestamp when the error occurred.</summary>
        public DateTimeOffset Timestamp { get; init; }
        
        /// <summary>User-friendly error message.</summary>
        public string UserMessage { get; init; } = string.Empty;
        
        /// <summary>Whether a dialog was shown to the user.</summary>
        public bool DialogShown { get; init; }
    }

    /// <summary>
    /// Centralized error coordination service.
    /// Consolidates error logging, user notification, and state management.
    /// </summary>
    /// <remarks>
    /// Replaces per-ViewModel error handling patterns with a single service.
    /// ViewModels can call HandleErrorAsync instead of duplicating try/catch patterns.
    /// Subscribers can react to ErrorOccurred for analytics or recovery.
    /// </remarks>
    public interface IErrorCoordinator
    {
        /// <summary>
        /// Handles an error with logging, optional dialog, and state update.
        /// </summary>
        /// <param name="ex">The exception to handle.</param>
        /// <param name="context">Context describing where the error occurred.</param>
        /// <param name="severity">Error severity level.</param>
        /// <param name="showDialog">Whether to show an error dialog to the user.</param>
        /// <returns>Task that completes when error handling is done.</returns>
        Task HandleErrorAsync(
            Exception ex, 
            string context, 
            ErrorSeverity severity = ErrorSeverity.Error,
            bool showDialog = true);

        /// <summary>
        /// Clears the current error state.
        /// </summary>
        void ClearError();

        /// <summary>
        /// Gets the current user-facing error message, or null if no error.
        /// </summary>
        string? CurrentError { get; }

        /// <summary>
        /// Gets whether there is an active error.
        /// </summary>
        bool HasError { get; }

        /// <summary>
        /// Event raised when an error occurs.
        /// Subscribe for analytics, recovery, or cross-cutting concerns.
        /// </summary>
        event Action<ErrorInfo>? ErrorOccurred;

        /// <summary>
        /// Event raised when the error state is cleared.
        /// </summary>
        event Action? ErrorCleared;
    }
}
