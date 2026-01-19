using System;
using System.Collections.Generic;
using System.Diagnostics;
using System.IO;
using System.Net.Http;
using System.Security.Cryptography;
using System.Text;
using System.Text.Json;
using System.Threading;
using System.Threading.Tasks;
using Microsoft.UI.Xaml;
using Windows.Storage;

namespace VoiceStudio.App.Services
{
    /// <summary>
    /// Service for checking and installing application updates.
    /// Uses GitHub Releases API for update checking.
    /// </summary>
    public class UpdateService : IUpdateService
    {
        private readonly HttpClient _httpClient;
        private readonly string _updateServerUrl;
        private readonly string _repositoryOwner;
        private readonly string _repositoryName;
        private Version? _latestVersion;
        private bool _isCheckingForUpdates;
        private bool _isDownloadingUpdate;
        private double _downloadProgress;
        private string? _updateDownloadPath;
        private DateTime _lastUpdateCheck = DateTime.MinValue;
        private const int UpdateCheckIntervalMinutes = 60;
        
        public Version CurrentVersion { get; }
        public Version LatestVersion => _latestVersion ?? CurrentVersion;
        public bool IsUpdateAvailable => _latestVersion != null && _latestVersion > CurrentVersion;
        public bool IsCheckingForUpdates => _isCheckingForUpdates;
        public bool IsDownloadingUpdate => _isDownloadingUpdate;
        public double DownloadProgress => _downloadProgress;
        public string UpdateDownloadPath => _updateDownloadPath ?? string.Empty;
        
        public event EventHandler<UpdateCheckCompletedEventArgs>? UpdateCheckCompleted;
        public event EventHandler<DownloadProgressEventArgs>? DownloadProgressChanged;
        public event EventHandler<DownloadCompletedEventArgs>? DownloadCompleted;
        
        public UpdateService()
        {
            _httpClient = new HttpClient
            {
                Timeout = TimeSpan.FromSeconds(30)
            };
            _httpClient.DefaultRequestHeaders.Add("User-Agent", "VoiceStudio-Quantum-Plus/1.0");
            
            // Repository information
            // Note: These values should be updated to match the actual GitHub repository at release time
            _updateServerUrl = "https://api.github.com";
            _repositoryOwner = "VoiceStudio"; // GitHub organization/username
            _repositoryName = "VoiceStudio-Quantum-Plus"; // Repository name
            
            // Get current version from assembly
            CurrentVersion = GetCurrentVersion();
        }
        
        /// <summary>
        /// Gets the current application version from the assembly.
        /// </summary>
        private Version GetCurrentVersion()
        {
            var assembly = System.Reflection.Assembly.GetExecutingAssembly();
            var version = assembly.GetName().Version;
            return version ?? new Version(1, 0, 0, 0);
        }
        
        public async Task<bool> CheckForUpdatesAsync(bool forceCheck = false, CancellationToken cancellationToken = default)
        {
            // Don't check if recently checked (unless forced)
            if (!forceCheck && _lastUpdateCheck.AddMinutes(UpdateCheckIntervalMinutes) > DateTime.UtcNow)
            {
                return IsUpdateAvailable;
            }
            
            if (_isCheckingForUpdates)
            {
                return IsUpdateAvailable;
            }
            
            _isCheckingForUpdates = true;
            _lastUpdateCheck = DateTime.UtcNow;
            
            try
            {
                // Check GitHub Releases API
                var apiUrl = $"{_updateServerUrl}/repos/{_repositoryOwner}/{_repositoryName}/releases/latest";
                var response = await _httpClient.GetAsync(apiUrl, cancellationToken).ConfigureAwait(false);
                
                if (!response.IsSuccessStatusCode)
                {
                    var errorMessage = $"Failed to check for updates: {response.StatusCode}";
                    OnUpdateCheckCompleted(false, null, errorMessage);
                    return false;
                }
                
                var jsonContent = await response.Content.ReadAsStringAsync(cancellationToken).ConfigureAwait(false);
                var release = JsonSerializer.Deserialize<GitHubRelease>(jsonContent, new JsonSerializerOptions
                {
                    PropertyNameCaseInsensitive = true
                });
                
                if (release == null || string.IsNullOrEmpty(release.TagName))
                {
                    OnUpdateCheckCompleted(false, null, "Invalid release information");
                    return false;
                }
                
                // Parse version from tag (e.g., "v1.2.3" -> Version(1, 2, 3))
                var versionString = release.TagName.TrimStart('v', 'V');
                if (Version.TryParse(versionString, out var latestVersion))
                {
                    _latestVersion = latestVersion;
                    var updateAvailable = latestVersion > CurrentVersion;
                    OnUpdateCheckCompleted(updateAvailable, latestVersion, null);
                    return updateAvailable;
                }
                else
                {
                    OnUpdateCheckCompleted(false, null, $"Invalid version format: {release.TagName}");
                    return false;
                }
            }
            catch (HttpRequestException ex)
            {
                var errorMessage = $"Network error while checking for updates: {ex.Message}";
                OnUpdateCheckCompleted(false, null, errorMessage);
                return false;
            }
            catch (Exception ex)
            {
                var errorMessage = $"Error checking for updates: {ex.Message}";
                OnUpdateCheckCompleted(false, null, errorMessage);
                return false;
            }
            finally
            {
                _isCheckingForUpdates = false;
            }
        }
        
        public async Task<string> DownloadUpdateAsync(Action<double>? progressCallback = null)
        {
            if (!IsUpdateAvailable || _latestVersion == null)
            {
                throw new InvalidOperationException("No update available to download");
            }
            
            if (_isDownloadingUpdate)
            {
                throw new InvalidOperationException("Update download already in progress");
            }
            
            _isDownloadingUpdate = true;
            _downloadProgress = 0.0;
            
            try
            {
                // Get release information
                var apiUrl = $"{_updateServerUrl}/repos/{_repositoryOwner}/{_repositoryName}/releases/latest";
                var response = await _httpClient.GetAsync(apiUrl, CancellationToken.None).ConfigureAwait(false);
                response.EnsureSuccessStatusCode();
                
                var jsonContent = await response.Content.ReadAsStringAsync(CancellationToken.None).ConfigureAwait(false);
                var release = JsonSerializer.Deserialize<GitHubRelease>(jsonContent, new JsonSerializerOptions
                {
                    PropertyNameCaseInsensitive = true
                });
                
                if (release?.Assets == null || release.Assets.Count == 0)
                {
                    throw new Exception("No update assets found in release");
                }
                
                // Find Windows installer asset
                var installerAsset = release.Assets.Find(a =>
                {
                    var name = a.Name;
                    if (string.IsNullOrWhiteSpace(name))
                    {
                        return false;
                    }

                    return name.Contains("Setup", StringComparison.OrdinalIgnoreCase) ||
                           name.Contains("Installer", StringComparison.OrdinalIgnoreCase) ||
                           name.EndsWith(".exe", StringComparison.OrdinalIgnoreCase) ||
                           name.EndsWith(".msi", StringComparison.OrdinalIgnoreCase);
                });
                
                if (installerAsset == null)
                {
                    throw new Exception("No installer asset found in release");
                }
                
                // Create download directory
                var localAppData = ApplicationData.Current.LocalFolder.Path;
                var downloadDir = Path.Combine(localAppData, "Updates");
                Directory.CreateDirectory(downloadDir);
                
                var assetFileName = installerAsset.Name;
                if (string.IsNullOrWhiteSpace(assetFileName))
                {
                    throw new Exception("Installer asset name is missing");
                }

                var downloadPath = Path.Combine(downloadDir, assetFileName);
                _updateDownloadPath = downloadPath;
                
                // Download file with progress tracking
                using (var fileStream = new FileStream(downloadPath, FileMode.Create, FileAccess.Write, FileShare.None))
                {
                    var downloadResponse = await _httpClient.GetAsync(installerAsset.BrowserDownloadUrl, HttpCompletionOption.ResponseHeadersRead, CancellationToken.None).ConfigureAwait(false);
                    downloadResponse.EnsureSuccessStatusCode();
                    
                    var totalBytes = downloadResponse.Content.Headers.ContentLength ?? 0L;
                    var bytesDownloaded = 0L;
                    var stopwatch = Stopwatch.StartNew();
                    
                    using (var contentStream = await downloadResponse.Content.ReadAsStreamAsync(CancellationToken.None).ConfigureAwait(false))
                    {
                        var buffer = new byte[8192];
                        int bytesRead;
                        
                        while ((bytesRead = await contentStream.ReadAsync(buffer, 0, buffer.Length, CancellationToken.None).ConfigureAwait(false)) > 0)
                        {
                            await fileStream.WriteAsync(buffer, 0, bytesRead, CancellationToken.None).ConfigureAwait(false);
                            bytesDownloaded += bytesRead;
                            
                            if (totalBytes > 0)
                            {
                                _downloadProgress = (double)bytesDownloaded / totalBytes;
                                var elapsedSeconds = stopwatch.Elapsed.TotalSeconds;
                                var speedMbps = elapsedSeconds > 0 ? bytesDownloaded * 8 / (elapsedSeconds * 1_000_000) : 0;
                                
                                progressCallback?.Invoke(_downloadProgress);
                                OnDownloadProgressChanged(_downloadProgress, bytesDownloaded, totalBytes, speedMbps);
                            }
                        }
                    }
                }
                
                OnDownloadCompleted(true, downloadPath, null);
                return downloadPath;
            }
            catch (Exception ex)
            {
                var errorMessage = $"Failed to download update: {ex.Message}";
                OnDownloadCompleted(false, null, errorMessage);
                throw new Exception(errorMessage, ex);
            }
            finally
            {
                _isDownloadingUpdate = false;
            }
        }
        
        public async Task<bool> VerifyUpdateAsync(string updatePath, string expectedChecksum)
        {
            if (!File.Exists(updatePath))
            {
                return false;
            }
            
            try
            {
                using (var sha256 = SHA256.Create())
                using (var fileStream = File.OpenRead(updatePath))
                {
                    var hashBytes = await sha256.ComputeHashAsync(fileStream);
                    var actualChecksum = BitConverter.ToString(hashBytes).Replace("-", "").ToLowerInvariant();
                    var expectedChecksumLower = expectedChecksum.Replace("-", "").Replace(" ", "").ToLowerInvariant();
                    
                    return actualChecksum == expectedChecksumLower;
                }
            }
            catch
            {
                return false;
            }
        }
        
        public async Task<bool> InstallUpdateAsync(string updatePath, bool restartAfterInstall = true)
        {
            if (!File.Exists(updatePath))
            {
                throw new FileNotFoundException("Update file not found", updatePath);
            }
            
            try
            {
                // Launch installer
                var processStartInfo = new ProcessStartInfo
                {
                    FileName = updatePath,
                    UseShellExecute = true,
                    Verb = "runas" // Run as administrator
                };
                
                var process = Process.Start(processStartInfo);
                if (process == null)
                {
                    return false;
                }
                
                // Wait a moment to ensure installer started
                await Task.Delay(1000);
                
                // If restart requested, close application after installer starts
                if (restartAfterInstall)
                {
                    // Give installer time to start, then close application
                    await Task.Delay(2000);
                    Application.Current.Exit();
                }
                
                return true;
            }
            catch (Exception ex)
            {
                throw new Exception($"Failed to install update: {ex.Message}", ex);
            }
        }
        
        public async Task<string> GetReleaseNotesAsync(Version version)
        {
            try
            {
                var apiUrl = $"{_updateServerUrl}/repos/{_repositoryOwner}/{_repositoryName}/releases/tags/v{version}";
                var response = await _httpClient.GetAsync(apiUrl, CancellationToken.None).ConfigureAwait(false);
                
                if (!response.IsSuccessStatusCode)
                {
                    return $"Release notes not available for version {version}";
                }
                
                var jsonContent = await response.Content.ReadAsStringAsync(CancellationToken.None).ConfigureAwait(false);
                var release = JsonSerializer.Deserialize<GitHubRelease>(jsonContent, new JsonSerializerOptions
                {
                    PropertyNameCaseInsensitive = true
                });
                
                return release?.Body ?? $"Release notes not available for version {version}";
            }
            catch
            {
                return $"Release notes not available for version {version}";
            }
        }
        
        private void OnUpdateCheckCompleted(bool updateAvailable, Version? latestVersion, string? errorMessage)
        {
            UpdateCheckCompleted?.Invoke(this, new UpdateCheckCompletedEventArgs
            {
                UpdateAvailable = updateAvailable,
                LatestVersion = latestVersion,
                ErrorMessage = errorMessage
            });
        }
        
        private void OnDownloadProgressChanged(double progress, long bytesDownloaded, long totalBytes, double speedMbps)
        {
            DownloadProgressChanged?.Invoke(this, new DownloadProgressEventArgs
            {
                Progress = progress,
                BytesDownloaded = bytesDownloaded,
                TotalBytes = totalBytes,
                DownloadSpeedMbps = speedMbps
            });
        }
        
        private void OnDownloadCompleted(bool success, string? filePath, string? errorMessage)
        {
            DownloadCompleted?.Invoke(this, new DownloadCompletedEventArgs
            {
                Success = success,
                FilePath = filePath,
                ErrorMessage = errorMessage
            });
        }
        
        public void Dispose()
        {
            _httpClient?.Dispose();
        }
    }
    
    /// <summary>
    /// GitHub Release API response model.
    /// </summary>
    internal class GitHubRelease
    {
        public string? TagName { get; set; }
        public string? Name { get; set; }
        public string? Body { get; set; }
        public bool Prerelease { get; set; }
        public List<GitHubAsset>? Assets { get; set; }
    }
    
    /// <summary>
    /// GitHub Release Asset model.
    /// </summary>
    internal class GitHubAsset
    {
        public string? Name { get; set; }
        public string? BrowserDownloadUrl { get; set; }
        public long Size { get; set; }
    }
}

