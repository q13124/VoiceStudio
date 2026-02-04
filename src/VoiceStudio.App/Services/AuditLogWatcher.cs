using System;
using System.IO;

namespace VoiceStudio.App.Services
{
    /// <summary>
    /// Watches for changes to audit log files and notifies subscribers.
    /// Provides real-time streaming of audit log entries to UI components.
    /// </summary>
    public class AuditLogWatcher : IDisposable
    {
        private FileSystemWatcher? _watcher;
        private bool _disposed;
        private readonly string _auditDir;

        /// <summary>
        /// Event raised when a new audit entry is detected.
        /// </summary>
        public event EventHandler<AuditLogChangeEventArgs>? LogChanged;

        /// <summary>
        /// Initializes a new AuditLogWatcher.
        /// </summary>
        /// <param name="auditDir">Directory containing audit logs. If null, uses default.</param>
        public AuditLogWatcher(string? auditDir = null)
        {
            _auditDir = auditDir ?? GetDefaultAuditDir();
        }

        private static string GetDefaultAuditDir()
        {
            var appData = Environment.GetFolderPath(Environment.SpecialFolder.LocalApplicationData);
            return Path.Combine(appData, "VoiceStudio", "Audit");
        }

        /// <summary>
        /// Start watching the audit log directory for changes.
        /// </summary>
        public void StartWatching()
        {
            if (_watcher != null)
                return;

            if (!Directory.Exists(_auditDir))
            {
                Directory.CreateDirectory(_auditDir);
            }

            _watcher = new FileSystemWatcher(_auditDir)
            {
                Filter = "*.jsonl",
                NotifyFilter = NotifyFilters.LastWrite | NotifyFilters.Size | NotifyFilters.CreationTime,
                EnableRaisingEvents = true
            };

            _watcher.Changed += OnLogFileChanged;
            _watcher.Created += OnLogFileChanged;
        }

        /// <summary>
        /// Stop watching for changes.
        /// </summary>
        public void StopWatching()
        {
            if (_watcher != null)
            {
                _watcher.EnableRaisingEvents = false;
                _watcher.Changed -= OnLogFileChanged;
                _watcher.Created -= OnLogFileChanged;
                _watcher.Dispose();
                _watcher = null;
            }
        }

        private void OnLogFileChanged(object sender, FileSystemEventArgs e)
        {
            // Notify subscribers that the log file changed
            LogChanged?.Invoke(this, new AuditLogChangeEventArgs
            {
                FilePath = e.FullPath,
                ChangeType = e.ChangeType.ToString()
            });
        }

        /// <summary>
        /// Dispose of resources.
        /// </summary>
        public void Dispose()
        {
            Dispose(true);
            GC.SuppressFinalize(this);
        }

        /// <summary>
        /// Dispose of resources.
        /// </summary>
        protected virtual void Dispose(bool disposing)
        {
            if (!_disposed)
            {
                if (disposing)
                {
                    StopWatching();
                }
                _disposed = true;
            }
        }
    }

    /// <summary>
    /// Event arguments for audit log changes.
    /// </summary>
    public class AuditLogChangeEventArgs : EventArgs
    {
        /// <summary>
        /// Path to the changed log file.
        /// </summary>
        public string FilePath { get; set; } = string.Empty;

        /// <summary>
        /// Type of change (Created, Changed, etc.)
        /// </summary>
        public string ChangeType { get; set; } = string.Empty;
    }
}
