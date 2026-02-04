using System;
using System.Threading;
using System.Threading.Tasks;

namespace VoiceStudio.App.Services
{
  /// <summary>
  /// Service interface for checking and installing application updates.
  /// </summary>
  public interface IUpdateService
  {
    /// <summary>
    /// Gets the current application version.
    /// </summary>
    Version CurrentVersion { get; }

    /// <summary>
    /// Gets the latest available version from the update server.
    /// </summary>
    Version LatestVersion { get; }

    /// <summary>
    /// Gets whether an update is available.
    /// </summary>
    bool IsUpdateAvailable { get; }

    /// <summary>
    /// Gets whether an update check is in progress.
    /// </summary>
    bool IsCheckingForUpdates { get; }

    /// <summary>
    /// Gets whether an update download is in progress.
    /// </summary>
    bool IsDownloadingUpdate { get; }

    /// <summary>
    /// Gets the download progress (0.0 to 1.0).
    /// </summary>
    double DownloadProgress { get; }

    /// <summary>
    /// Gets the update download path.
    /// </summary>
    string UpdateDownloadPath { get; }

    /// <summary>
    /// Event raised when update check completes.
    /// </summary>
    event EventHandler<UpdateCheckCompletedEventArgs> UpdateCheckCompleted;

    /// <summary>
    /// Event raised when download progress changes.
    /// </summary>
    event EventHandler<DownloadProgressEventArgs> DownloadProgressChanged;

    /// <summary>
    /// Event raised when download completes.
    /// </summary>
    event EventHandler<DownloadCompletedEventArgs> DownloadCompleted;

    /// <summary>
    /// Checks for available updates.
    /// </summary>
    /// <param name="forceCheck">Whether to force a check even if recently checked.</param>
    /// <returns>True if an update is available, false otherwise.</returns>
    Task<bool> CheckForUpdatesAsync(bool forceCheck = false, CancellationToken cancellationToken = default);

    /// <summary>
    /// Downloads the latest update.
    /// </summary>
    /// <param name="progressCallback">Optional callback for download progress.</param>
    /// <returns>The path to the downloaded update file.</returns>
    Task<string> DownloadUpdateAsync(Action<double>? progressCallback = null);

    /// <summary>
    /// Verifies the downloaded update file integrity.
    /// </summary>
    /// <param name="updatePath">Path to the update file.</param>
    /// <param name="expectedChecksum">Expected SHA256 checksum.</param>
    /// <returns>True if verification succeeds, false otherwise.</returns>
    Task<bool> VerifyUpdateAsync(string updatePath, string expectedChecksum);

    /// <summary>
    /// Installs the downloaded update.
    /// </summary>
    /// <param name="updatePath">Path to the update installer.</param>
    /// <param name="restartAfterInstall">Whether to restart the application after installation.</param>
    /// <returns>True if installation started successfully, false otherwise.</returns>
    Task<bool> InstallUpdateAsync(string updatePath, bool restartAfterInstall = true);

    /// <summary>
    /// Gets update release notes for the specified version.
    /// </summary>
    /// <param name="version">Version to get release notes for.</param>
    /// <returns>Release notes HTML or markdown.</returns>
    Task<string> GetReleaseNotesAsync(Version version);
  }

  /// <summary>
  /// Event arguments for update check completion.
  /// </summary>
  public class UpdateCheckCompletedEventArgs : EventArgs
  {
    public bool UpdateAvailable { get; set; }
    public Version? LatestVersion { get; set; }
    public string? ErrorMessage { get; set; }
    public bool HasError => !string.IsNullOrEmpty(ErrorMessage);
  }

  /// <summary>
  /// Event arguments for download progress.
  /// </summary>
  public class DownloadProgressEventArgs : EventArgs
  {
    public double Progress { get; set; }
    public long BytesDownloaded { get; set; }
    public long TotalBytes { get; set; }
    public double DownloadSpeedMbps { get; set; }
  }

  /// <summary>
  /// Event arguments for download completion.
  /// </summary>
  public class DownloadCompletedEventArgs : EventArgs
  {
    public bool Success { get; set; }
    public string? FilePath { get; set; }
    public string? ErrorMessage { get; set; }
    public bool HasError => !string.IsNullOrEmpty(ErrorMessage);
  }
}