using System;
using System.Collections.Generic;
using System.Threading.Tasks;

namespace VoiceStudio.App.Services
{
    /// <summary>
    /// Service for centralized error logging and tracking with correlation IDs and breadcrumbs.
    /// </summary>
    public interface IErrorLoggingService
    {
        /// <summary>
        /// Logs an error with context information.
        /// </summary>
        void LogError(Exception exception, string context = "", Dictionary<string, object>? metadata = null);

        /// <summary>
        /// Logs a warning message.
        /// </summary>
        void LogWarning(string message, string context = "", Dictionary<string, object>? metadata = null);

        /// <summary>
        /// Logs an informational message.
        /// </summary>
        void LogInfo(string message, string context = "", Dictionary<string, object>? metadata = null);

        /// <summary>
        /// Gets recent error log entries.
        /// </summary>
        IReadOnlyList<ErrorLogEntry> GetRecentErrors(int count = 100);

        /// <summary>
        /// Clears all error logs.
        /// </summary>
        void ClearLogs();

        /// <summary>
        /// Event raised when a new error is logged.
        /// </summary>
        event EventHandler<ErrorLogEntry>? ErrorLogged;

        /// <summary>
        /// Exports logs in structured JSON format.
        /// </summary>
        string ExportLogsAsJson(int count = 1000);

        /// <summary>
        /// Exports logs in key-value format for easy parsing.
        /// </summary>
        string ExportLogsAsKeyValue(int count = 1000);

        /// <summary>
        /// Starts a new correlation context for tracking user actions.
        /// Returns a correlation ID that should be used for all related log entries.
        /// </summary>
        string StartCorrelation(string action, Dictionary<string, object>? metadata = null);

        /// <summary>
        /// Ends a correlation context and logs completion.
        /// </summary>
        void EndCorrelation(string correlationId, bool success = true, string? message = null);

        /// <summary>
        /// Adds a breadcrumb for tracking critical flows (recording, editing, export, etc.).
        /// </summary>
        void AddBreadcrumb(string message, string category = "UserAction", Dictionary<string, object>? metadata = null);

        /// <summary>
        /// Gets breadcrumbs for a correlation ID.
        /// </summary>
        IReadOnlyList<Breadcrumb> GetBreadcrumbs(string correlationId);
    }

    /// <summary>
    /// Represents a single error log entry.
    /// </summary>
    public class ErrorLogEntry
    {
        public DateTime Timestamp { get; set; }
        public string Level { get; set; } = "Error"; // Error, Warning, Info
        public string Message { get; set; } = string.Empty;
        public string? Context { get; set; }
        public string? ExceptionType { get; set; }
        public string? StackTrace { get; set; }
        public Dictionary<string, object>? Metadata { get; set; }
        public string? CorrelationId { get; set; }
    }

    /// <summary>
    /// Represents a breadcrumb for tracking user actions and critical flows.
    /// </summary>
    public class Breadcrumb
    {
        public DateTime Timestamp { get; set; }
        public string Message { get; set; } = string.Empty;
        public string Category { get; set; } = "UserAction";
        public string? CorrelationId { get; set; }
        public Dictionary<string, object>? Metadata { get; set; }
    }
}

