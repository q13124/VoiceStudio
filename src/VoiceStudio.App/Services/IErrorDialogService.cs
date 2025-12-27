using System;
using System.Threading.Tasks;

namespace VoiceStudio.App.Services
{
    /// <summary>
    /// Service for displaying user-friendly error dialogs.
    /// </summary>
    public interface IErrorDialogService
    {
        /// <summary>
        /// Shows an error dialog with user-friendly message and recovery suggestions.
        /// </summary>
        Task ShowErrorAsync(Exception exception, string? title = null, string? context = null);

        /// <summary>
        /// Shows an error dialog with a custom message.
        /// </summary>
        Task ShowErrorAsync(string message, string? title = null, string? recoverySuggestion = null);

        /// <summary>
        /// Shows a warning dialog.
        /// </summary>
        Task ShowWarningAsync(string message, string? title = null);

        /// <summary>
        /// Shows an informational dialog.
        /// </summary>
        Task ShowInfoAsync(string message, string? title = null);
    }
}

