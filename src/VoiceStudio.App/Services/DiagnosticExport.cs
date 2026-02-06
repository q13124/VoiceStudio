// =============================================================================
// DiagnosticExport.cs — Phase 5.3.2
// Service for creating ZIP bundles of diagnostic data for support/debugging.
// =============================================================================

using System;
using System.Collections.Generic;
using System.Globalization;
using System.IO;
using System.IO.Compression;
using System.Text;
using System.Text.Json;
using System.Threading;
using System.Threading.Tasks;
using VoiceStudio.App.Logging;

namespace VoiceStudio.App.Services
{
    /// <summary>
    /// Provides functionality to export diagnostic data as a ZIP bundle.
    /// Includes logs, traces, system info, and configuration for support purposes.
    /// </summary>
    public sealed class DiagnosticExport : IDisposable
    {
        private readonly string _exportDirectory;
        private readonly JsonSerializerOptions _jsonOptions;
        private bool _disposed;

        /// <summary>
        /// Gets the default export directory for diagnostic bundles.
        /// </summary>
        public static string DefaultExportDirectory =>
            Path.Combine(
                Environment.GetFolderPath(Environment.SpecialFolder.LocalApplicationData),
                "VoiceStudio",
                "DiagnosticExports");

        /// <summary>
        /// Initializes a new instance of the <see cref="DiagnosticExport"/> class.
        /// </summary>
        /// <param name="exportDirectory">
        /// Directory to store exported bundles. Uses default if null.
        /// </param>
        public DiagnosticExport(string? exportDirectory = null)
        {
            _exportDirectory = exportDirectory ?? DefaultExportDirectory;
            _jsonOptions = new JsonSerializerOptions
            {
                WriteIndented = true,
                PropertyNamingPolicy = JsonNamingPolicy.CamelCase
            };

            // Ensure export directory exists
            Directory.CreateDirectory(_exportDirectory);
        }

        /// <summary>
        /// Creates a diagnostic ZIP bundle with all available data.
        /// </summary>
        /// <param name="options">Options controlling what to include.</param>
        /// <param name="cancellationToken">Cancellation token.</param>
        /// <returns>Path to the created ZIP file.</returns>
        public async Task<string> CreateBundleAsync(
            DiagnosticExportOptions options,
            CancellationToken cancellationToken = default)
        {
            var timestamp = DateTime.Now.ToString(
                "yyyyMMdd_HHmmss",
                CultureInfo.InvariantCulture);
            var filename = $"voicestudio_diagnostics_{timestamp}.zip";
            var zipPath = Path.Combine(_exportDirectory, filename);

            using var zipStream = new FileStream(
                zipPath,
                FileMode.Create,
                FileAccess.Write);
            using var archive = new ZipArchive(zipStream, ZipArchiveMode.Create);

            // Add manifest
            await AddManifestAsync(archive, options, cancellationToken);

            // Add system information
            if (options.IncludeSystemInfo)
            {
                await AddSystemInfoAsync(archive, cancellationToken);
            }

            // Add log files
            if (options.IncludeLogs)
            {
                await AddLogsAsync(archive, options, cancellationToken);
            }

            // Add trace files
            if (options.IncludeTraces)
            {
                await AddTracesAsync(archive, options, cancellationToken);
            }

            // Add configuration
            if (options.IncludeConfiguration)
            {
                await AddConfigurationAsync(archive, cancellationToken);
            }

            // Add error logs
            if (options.IncludeErrorLogs)
            {
                await AddErrorLogsAsync(archive, options, cancellationToken);
            }

            return zipPath;
        }

        /// <summary>
        /// Creates a minimal crash bundle for quick submission.
        /// </summary>
        /// <param name="crashInfo">Information about the crash.</param>
        /// <param name="cancellationToken">Cancellation token.</param>
        /// <returns>Path to the created ZIP file.</returns>
        public async Task<string> CreateCrashBundleAsync(
            CrashInfo crashInfo,
            CancellationToken cancellationToken = default)
        {
            var options = new DiagnosticExportOptions
            {
                IncludeSystemInfo = true,
                IncludeLogs = true,
                IncludeTraces = true,
                IncludeConfiguration = false,
                IncludeErrorLogs = true,
                LogHoursToInclude = 1,  // Last hour only for crash
                CorrelationIdFilter = crashInfo.CorrelationId
            };

            var timestamp = DateTime.Now.ToString(
                "yyyyMMdd_HHmmss",
                CultureInfo.InvariantCulture);
            var filename = $"voicestudio_crash_{timestamp}.zip";
            var zipPath = Path.Combine(_exportDirectory, filename);

            using var zipStream = new FileStream(
                zipPath,
                FileMode.Create,
                FileAccess.Write);
            using var archive = new ZipArchive(zipStream, ZipArchiveMode.Create);

            // Add crash-specific manifest
            await AddCrashManifestAsync(archive, crashInfo, cancellationToken);

            // Add crash details
            await AddCrashDetailsAsync(archive, crashInfo, cancellationToken);

            // Add standard diagnostic data
            await AddSystemInfoAsync(archive, cancellationToken);
            await AddLogsAsync(archive, options, cancellationToken);
            await AddTracesAsync(archive, options, cancellationToken);
            await AddErrorLogsAsync(archive, options, cancellationToken);

            return zipPath;
        }

        private async Task AddManifestAsync(
            ZipArchive archive,
            DiagnosticExportOptions options,
            CancellationToken cancellationToken)
        {
            var manifest = new Dictionary<string, object>
            {
                ["version"] = "1.0",
                ["created"] = DateTime.UtcNow.ToString("o", CultureInfo.InvariantCulture),
                ["applicationVersion"] = GetApplicationVersion(),
                ["options"] = new Dictionary<string, object>
                {
                    ["includeSystemInfo"] = options.IncludeSystemInfo,
                    ["includeLogs"] = options.IncludeLogs,
                    ["includeTraces"] = options.IncludeTraces,
                    ["includeConfiguration"] = options.IncludeConfiguration,
                    ["includeErrorLogs"] = options.IncludeErrorLogs,
                    ["logHoursToInclude"] = options.LogHoursToInclude,
                    ["correlationIdFilter"] = options.CorrelationIdFilter ?? string.Empty
                }
            };

            var json = JsonSerializer.Serialize(manifest, _jsonOptions);
            await AddTextEntryAsync(
                archive,
                "manifest.json",
                json,
                cancellationToken);
        }

        private async Task AddCrashManifestAsync(
            ZipArchive archive,
            CrashInfo crashInfo,
            CancellationToken cancellationToken)
        {
            var manifest = new Dictionary<string, object>
            {
                ["version"] = "1.0",
                ["type"] = "crash_bundle",
                ["created"] = DateTime.UtcNow.ToString("o", CultureInfo.InvariantCulture),
                ["applicationVersion"] = GetApplicationVersion(),
                ["crashId"] = crashInfo.CrashId ?? Guid.NewGuid().ToString(),
                ["crashTime"] = crashInfo.Timestamp.ToString(
                    "o",
                    CultureInfo.InvariantCulture),
                ["correlationId"] = crashInfo.CorrelationId ?? string.Empty
            };

            var json = JsonSerializer.Serialize(manifest, _jsonOptions);
            await AddTextEntryAsync(
                archive,
                "manifest.json",
                json,
                cancellationToken);
        }

        private async Task AddCrashDetailsAsync(
            ZipArchive archive,
            CrashInfo crashInfo,
            CancellationToken cancellationToken)
        {
            var details = new Dictionary<string, object?>
            {
                ["crashId"] = crashInfo.CrashId,
                ["timestamp"] = crashInfo.Timestamp.ToString(
                    "o",
                    CultureInfo.InvariantCulture),
                ["exceptionType"] = crashInfo.ExceptionType,
                ["message"] = crashInfo.Message,
                ["stackTrace"] = crashInfo.StackTrace,
                ["correlationId"] = crashInfo.CorrelationId,
                ["additionalData"] = crashInfo.AdditionalData
            };

            var json = JsonSerializer.Serialize(details, _jsonOptions);
            await AddTextEntryAsync(
                archive,
                "crash_details.json",
                json,
                cancellationToken);
        }

        private async Task AddSystemInfoAsync(
            ZipArchive archive,
            CancellationToken cancellationToken)
        {
            var systemInfo = new Dictionary<string, object>
            {
                ["machineName"] = Environment.MachineName,
                ["osVersion"] = Environment.OSVersion.ToString(),
                ["is64BitOperatingSystem"] = Environment.Is64BitOperatingSystem,
                ["is64BitProcess"] = Environment.Is64BitProcess,
                ["processorCount"] = Environment.ProcessorCount,
                ["systemPageSize"] = Environment.SystemPageSize,
                ["clrVersion"] = Environment.Version.ToString(),
                ["workingSet"] = Environment.WorkingSet,
                ["currentDirectory"] = Environment.CurrentDirectory,
                ["systemDirectory"] = Environment.SystemDirectory,
                ["userDomainName"] = Environment.UserDomainName,
                ["userName"] = "[REDACTED]",  // Privacy
                ["environmentVariables"] = GetSafeEnvironmentVariables()
            };

            var json = JsonSerializer.Serialize(systemInfo, _jsonOptions);
            await AddTextEntryAsync(
                archive,
                "system_info.json",
                json,
                cancellationToken);
        }

        private async Task AddLogsAsync(
            ZipArchive archive,
            DiagnosticExportOptions options,
            CancellationToken cancellationToken)
        {
            var logsDir = Path.Combine(
                Environment.GetFolderPath(Environment.SpecialFolder.LocalApplicationData),
                "VoiceStudio",
                "Logs");

            if (!Directory.Exists(logsDir))
            {
                return;
            }

            var cutoff = DateTime.Now.AddHours(-options.LogHoursToInclude);
            var logFiles = Directory.GetFiles(logsDir, "*.log");

            foreach (var logFile in logFiles)
            {
                cancellationToken.ThrowIfCancellationRequested();

                var fileInfo = new FileInfo(logFile);
                if (fileInfo.LastWriteTime < cutoff)
                {
                    continue;
                }

                var entryName = $"logs/{Path.GetFileName(logFile)}";
                await AddFileEntryAsync(archive, entryName, logFile, cancellationToken);
            }
        }

        private async Task AddTracesAsync(
            ZipArchive archive,
            DiagnosticExportOptions options,
            CancellationToken cancellationToken)
        {
            var tracesDir = Path.Combine(
                Environment.CurrentDirectory,
                ".voicestudio",
                "traces");

            if (!Directory.Exists(tracesDir))
            {
                return;
            }

            var cutoff = DateTime.Now.AddHours(-options.LogHoursToInclude);
            var traceFiles = Directory.GetFiles(tracesDir, "*.jsonl");

            foreach (var traceFile in traceFiles)
            {
                cancellationToken.ThrowIfCancellationRequested();

                var fileInfo = new FileInfo(traceFile);
                if (fileInfo.LastWriteTime < cutoff)
                {
                    continue;
                }

                // Filter by correlation ID if specified
                if (!string.IsNullOrEmpty(options.CorrelationIdFilter))
                {
                    var filteredContent = await FilterTracesByCorrelationIdAsync(
                        traceFile,
                        options.CorrelationIdFilter,
                        cancellationToken);

                    if (!string.IsNullOrEmpty(filteredContent))
                    {
                        var entryName = $"traces/{Path.GetFileName(traceFile)}";
                        await AddTextEntryAsync(
                            archive,
                            entryName,
                            filteredContent,
                            cancellationToken);
                    }
                }
                else
                {
                    var entryName = $"traces/{Path.GetFileName(traceFile)}";
                    await AddFileEntryAsync(archive, entryName, traceFile, cancellationToken);
                }
            }
        }

        private async Task AddConfigurationAsync(
            ZipArchive archive,
            CancellationToken cancellationToken)
        {
            var configDir = Path.Combine(
                Environment.GetFolderPath(Environment.SpecialFolder.LocalApplicationData),
                "VoiceStudio",
                "Config");

            if (!Directory.Exists(configDir))
            {
                return;
            }

            var configFiles = Directory.GetFiles(configDir, "*.json");

            foreach (var configFile in configFiles)
            {
                cancellationToken.ThrowIfCancellationRequested();

                // Redact sensitive fields from config
                var content = await File.ReadAllTextAsync(configFile, cancellationToken);
                var redacted = RedactSensitiveConfig(content);

                var entryName = $"config/{Path.GetFileName(configFile)}";
                await AddTextEntryAsync(archive, entryName, redacted, cancellationToken);
            }
        }

        private async Task AddErrorLogsAsync(
            ZipArchive archive,
            DiagnosticExportOptions options,
            CancellationToken cancellationToken)
        {
            // Get error logs from the error tracker
            try
            {
                var errorLogs = await GetRecentErrorLogsAsync(
                    options.LogHoursToInclude,
                    options.CorrelationIdFilter,
                    cancellationToken);

                if (errorLogs.Count > 0)
                {
                    var json = JsonSerializer.Serialize(errorLogs, _jsonOptions);
                    await AddTextEntryAsync(
                        archive,
                        "error_logs.json",
                        json,
                        cancellationToken);
                }
            }
            catch (InvalidOperationException)
            {
                // Error tracker not available, skip
            }
        }

        private static async Task<string> FilterTracesByCorrelationIdAsync(
            string filePath,
            string correlationId,
            CancellationToken cancellationToken)
        {
            var lines = await File.ReadAllLinesAsync(filePath, cancellationToken);
            var filtered = new StringBuilder();

            foreach (var line in lines)
            {
                if (line.Contains(correlationId, StringComparison.OrdinalIgnoreCase))
                {
                    filtered.AppendLine(line);
                }
            }

            return filtered.ToString();
        }

        private static async Task AddTextEntryAsync(
            ZipArchive archive,
            string entryName,
            string content,
            CancellationToken cancellationToken)
        {
            var entry = archive.CreateEntry(entryName, CompressionLevel.Optimal);
            using var stream = entry.Open();
            using var writer = new StreamWriter(stream, Encoding.UTF8);
            await writer.WriteAsync(content.AsMemory(), cancellationToken);
        }

        private static async Task AddFileEntryAsync(
            ZipArchive archive,
            string entryName,
            string filePath,
            CancellationToken cancellationToken)
        {
            var entry = archive.CreateEntry(entryName, CompressionLevel.Optimal);
            using var entryStream = entry.Open();
            using var fileStream = new FileStream(
                filePath,
                FileMode.Open,
                FileAccess.Read,
                FileShare.ReadWrite);
            await fileStream.CopyToAsync(entryStream, cancellationToken);
        }

        private static string GetApplicationVersion()
        {
            var assembly = typeof(DiagnosticExport).Assembly;
            var version = assembly.GetName().Version;
            return version?.ToString() ?? "1.0.0.0";
        }

        private static Dictionary<string, string> GetSafeEnvironmentVariables()
        {
            var safeVars = new Dictionary<string, string>();
            var sensitivePatterns = new[]
            {
                "API", "KEY", "SECRET", "PASSWORD", "TOKEN", "CREDENTIAL"
            };

            foreach (System.Collections.DictionaryEntry entry in Environment.GetEnvironmentVariables())
            {
                var key = entry.Key?.ToString() ?? string.Empty;
                var isSensitive = false;

                foreach (var pattern in sensitivePatterns)
                {
                    if (key.Contains(pattern, StringComparison.OrdinalIgnoreCase))
                    {
                        isSensitive = true;
                        break;
                    }
                }

                safeVars[key] = isSensitive ? "[REDACTED]" : entry.Value?.ToString() ?? string.Empty;
            }

            return safeVars;
        }

        private static string RedactSensitiveConfig(string configContent)
        {
            // Simple redaction of common sensitive patterns
            var sensitivePatterns = new[]
            {
                ("apiKey", "[REDACTED]"),
                ("api_key", "[REDACTED]"),
                ("secret", "[REDACTED]"),
                ("password", "[REDACTED]"),
                ("token", "[REDACTED]"),
                ("credential", "[REDACTED]")
            };

            var result = configContent;
            foreach (var (pattern, replacement) in sensitivePatterns)
            {
                // Simple pattern: "key": "value" -> "key": "[REDACTED]"
                var regex = $"\"{pattern}\"\\s*:\\s*\"[^\"]*\"";
                result = System.Text.RegularExpressions.Regex.Replace(
                    result,
                    regex,
                    $"\"{pattern}\": \"{replacement}\"",
                    System.Text.RegularExpressions.RegexOptions.IgnoreCase);
            }

            return result;
        }

        private static Task<List<Dictionary<string, object>>> GetRecentErrorLogsAsync(
            int hoursToInclude,
            string? correlationIdFilter,
            CancellationToken cancellationToken)
        {
            // This would integrate with the error tracker service
            // For now, return empty list - actual implementation would query ErrorTracker
            _ = hoursToInclude;
            _ = correlationIdFilter;
            _ = cancellationToken;
            return Task.FromResult(new List<Dictionary<string, object>>());
        }

        /// <summary>
        /// Disposes resources used by the export service.
        /// </summary>
        public void Dispose()
        {
            if (!_disposed)
            {
                _disposed = true;
            }
        }
    }

    /// <summary>
    /// Options for controlling diagnostic export content.
    /// </summary>
    public sealed class DiagnosticExportOptions
    {
        /// <summary>
        /// Gets or sets whether to include system information.
        /// </summary>
        public bool IncludeSystemInfo { get; set; } = true;

        /// <summary>
        /// Gets or sets whether to include log files.
        /// </summary>
        public bool IncludeLogs { get; set; } = true;

        /// <summary>
        /// Gets or sets whether to include trace files.
        /// </summary>
        public bool IncludeTraces { get; set; } = true;

        /// <summary>
        /// Gets or sets whether to include configuration files.
        /// </summary>
        public bool IncludeConfiguration { get; set; } = false;

        /// <summary>
        /// Gets or sets whether to include error logs.
        /// </summary>
        public bool IncludeErrorLogs { get; set; } = true;

        /// <summary>
        /// Gets or sets the number of hours of logs to include.
        /// </summary>
        public int LogHoursToInclude { get; set; } = 24;

        /// <summary>
        /// Gets or sets correlation ID to filter by.
        /// </summary>
        public string? CorrelationIdFilter { get; set; }
    }

    /// <summary>
    /// Information about a crash for crash bundle creation.
    /// </summary>
    public sealed class CrashInfo
    {
        /// <summary>
        /// Gets or sets the unique crash identifier.
        /// </summary>
        public string? CrashId { get; set; }

        /// <summary>
        /// Gets or sets the timestamp of the crash.
        /// </summary>
        public DateTime Timestamp { get; set; } = DateTime.UtcNow;

        /// <summary>
        /// Gets or sets the exception type.
        /// </summary>
        public string? ExceptionType { get; set; }

        /// <summary>
        /// Gets or sets the error message.
        /// </summary>
        public string? Message { get; set; }

        /// <summary>
        /// Gets or sets the stack trace.
        /// </summary>
        public string? StackTrace { get; set; }

        /// <summary>
        /// Gets or sets the correlation ID associated with the crash.
        /// </summary>
        public string? CorrelationId { get; set; }

        /// <summary>
        /// Gets or sets additional data to include.
        /// </summary>
        public Dictionary<string, object>? AdditionalData { get; set; }
    }
}
