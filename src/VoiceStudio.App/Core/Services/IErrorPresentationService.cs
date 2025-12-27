using System;

namespace VoiceStudio.Core.Services
{
    /// <summary>
    /// Service for presenting errors to users in a consistent manner.
    /// </summary>
    public interface IErrorPresentationService
    {
        /// <summary>
        /// Shows an error to the user using the appropriate presentation method.
        /// </summary>
        /// <param name="exception">The exception to display.</param>
        /// <param name="context">Context information about where the error occurred.</param>
        /// <param name="type">The type of error presentation to use.</param>
        void ShowError(Exception exception, string context, ErrorPresentationType type = ErrorPresentationType.Toast);

        /// <summary>
        /// Shows an error message to the user.
        /// </summary>
        /// <param name="message">The error message.</param>
        /// <param name="context">Context information about where the error occurred.</param>
        /// <param name="type">The type of error presentation to use.</param>
        void ShowError(string message, string context, ErrorPresentationType type = ErrorPresentationType.Toast);
    }

    /// <summary>
    /// Types of error presentation methods.
    /// </summary>
    public enum ErrorPresentationType
    {
        /// <summary>
        /// Show error as a toast notification (transient, non-blocking).
        /// Use for non-critical errors that don't require user action.
        /// </summary>
        Toast,

        /// <summary>
        /// Show error inline (e.g., in a form field).
        /// Use for validation errors or field-specific errors.
        /// </summary>
        Inline,

        /// <summary>
        /// Show error in a dialog (blocking, requires user acknowledgment).
        /// Use for critical errors that require user action or acknowledgment.
        /// </summary>
        Dialog
    }
}
