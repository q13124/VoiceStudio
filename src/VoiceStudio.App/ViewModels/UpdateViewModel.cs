using System;
using System.Threading.Tasks;
using System.Windows.Input;
using VoiceStudio.App.Services;
using VoiceStudio.App.ViewModels;
using VoiceStudio.App.Utilities;

using CommunityToolkit.Mvvm.Input;
namespace VoiceStudio.App.ViewModels
{
    /// <summary>
    /// ViewModel for the update dialog and update notifications.
    /// </summary>
    public class UpdateViewModel : BaseViewModel
    {
        private readonly IUpdateService _updateService;
        private bool _isUpdateAvailable;
        private bool _isCheckingForUpdates;
        private bool _isDownloadingUpdate;
        private double _downloadProgress;
        private string _downloadStatusText = string.Empty;
        private string _releaseNotes = string.Empty;
        private Version? _latestVersion;
        private string _errorMessage = string.Empty;

        public UpdateViewModel(IUpdateService updateService)
        {
            _updateService = updateService ?? throw new ArgumentNullException(nameof(updateService));

            // Subscribe to update service events
            _updateService.UpdateCheckCompleted += OnUpdateCheckCompleted;
            _updateService.DownloadProgressChanged += OnDownloadProgressChanged;
            _updateService.DownloadCompleted += OnDownloadCompleted;

            // Initialize commands
            CheckForUpdatesCommand = new UpdateRelayCommand(async () => await CheckForUpdatesAsync(), () => !IsCheckingForUpdates);
            DownloadUpdateCommand = new UpdateRelayCommand(async () => await DownloadUpdateAsync(), () => IsUpdateAvailable && !IsDownloadingUpdate);
            InstallUpdateCommand = new UpdateRelayCommand(async () => await InstallUpdateAsync(), () => !string.IsNullOrEmpty(UpdateDownloadPath));
            DismissCommand = new UpdateRelayCommand(() => Dismiss?.Invoke());
        }

        public bool IsUpdateAvailable
        {
            get => _isUpdateAvailable;
            set => SetProperty(ref _isUpdateAvailable, value);
        }

        public bool IsCheckingForUpdates
        {
            get => _isCheckingForUpdates;
            set
            {
                SetProperty(ref _isCheckingForUpdates, value);
                ((AsyncRelayCommand)CheckForUpdatesCommand).NotifyCanExecuteChanged();
            }
        }

        public bool IsDownloadingUpdate
        {
            get => _isDownloadingUpdate;
            set
            {
                SetProperty(ref _isDownloadingUpdate, value);
                ((AsyncRelayCommand)DownloadUpdateCommand).NotifyCanExecuteChanged();
            }
        }

        public double DownloadProgress
        {
            get => _downloadProgress;
            set => SetProperty(ref _downloadProgress, value);
        }

        public string DownloadStatusText
        {
            get => _downloadStatusText;
            set => SetProperty(ref _downloadStatusText, value);
        }

        public string ReleaseNotes
        {
            get => _releaseNotes;
            set => SetProperty(ref _releaseNotes, value);
        }

        public Version? LatestVersion
        {
            get => _latestVersion;
            set => SetProperty(ref _latestVersion, value);
        }

        public string ErrorMessage
        {
            get => _errorMessage;
            set => SetProperty(ref _errorMessage, value);
        }

        public string CurrentVersion => _updateService.CurrentVersion.ToString();
        public string UpdateDownloadPath => _updateService.UpdateDownloadPath;

        public ICommand CheckForUpdatesCommand { get; }
        public ICommand DownloadUpdateCommand { get; }
        public ICommand InstallUpdateCommand { get; }
        public ICommand DismissCommand { get; }

        public event Action? Dismiss;

        public async Task CheckForUpdatesAsync()
        {
            IsCheckingForUpdates = true;
            ErrorMessage = string.Empty;

            try
            {
                var updateAvailable = await _updateService.CheckForUpdatesAsync(forceCheck: true);
                IsUpdateAvailable = updateAvailable;

                if (updateAvailable && _updateService.LatestVersion != null)
                {
                    LatestVersion = _updateService.LatestVersion;
                    await LoadReleaseNotesAsync(_updateService.LatestVersion);
                }
            }
            catch (Exception ex)
            {
                ErrorMessage = ResourceHelper.FormatString("Update.CheckForUpdatesFailed", ex.Message);
            }
            finally
            {
                IsCheckingForUpdates = false;
            }
        }

        public async Task DownloadUpdateAsync()
        {
            if (!IsUpdateAvailable)
            {
                return;
            }

            IsDownloadingUpdate = true;
            DownloadProgress = 0.0;
            ErrorMessage = string.Empty;
            DownloadStatusText = ResourceHelper.GetString("Update.PreparingDownload", "Preparing download...");

            try
            {
                await _updateService.DownloadUpdateAsync(progress =>
                {
                    DownloadProgress = progress;
                    DownloadStatusText = ResourceHelper.FormatString("Update.Downloading", progress.ToString("P0"));
                });

                DownloadStatusText = ResourceHelper.GetString("Update.DownloadComplete", "Download complete!");
            }
            catch (Exception ex)
            {
                ErrorMessage = ResourceHelper.FormatString("Update.DownloadUpdateFailed", ex.Message);
                DownloadStatusText = ResourceHelper.GetString("Update.DownloadFailed", "Download failed");
            }
            finally
            {
                IsDownloadingUpdate = false;
                ((AsyncRelayCommand)InstallUpdateCommand).NotifyCanExecuteChanged();
            }
        }

        public async Task InstallUpdateAsync()
        {
            if (string.IsNullOrEmpty(UpdateDownloadPath))
            {
                ErrorMessage = ResourceHelper.GetString("Update.NoUpdateFileAvailable", "No update file available");
                return;
            }

            try
            {
                var success = await _updateService.InstallUpdateAsync(UpdateDownloadPath, restartAfterInstall: true);
                if (!success)
                {
                    ErrorMessage = ResourceHelper.GetString("Update.FailedToStartInstaller", "Failed to start update installer");
                }
            }
            catch (Exception ex)
            {
                ErrorMessage = ResourceHelper.FormatString("Update.InstallUpdateFailed", ex.Message);
            }
        }

        private async Task LoadReleaseNotesAsync(Version version)
        {
            try
            {
                ReleaseNotes = await _updateService.GetReleaseNotesAsync(version);
            }
            catch
            {
                ReleaseNotes = ResourceHelper.GetString("Update.ReleaseNotesNotAvailable", "Release notes not available");
            }
        }

        private void OnUpdateCheckCompleted(object? sender, UpdateCheckCompletedEventArgs e)
        {
            IsUpdateAvailable = e.UpdateAvailable;
            LatestVersion = e.LatestVersion;

            if (e.HasError)
            {
                ErrorMessage = e.ErrorMessage ?? ResourceHelper.GetString("Update.UnknownError", "Unknown error");
            }

            if (e.UpdateAvailable && e.LatestVersion != null)
            {
                _ = LoadReleaseNotesAsync(e.LatestVersion);
            }
        }

        private void OnDownloadProgressChanged(object? sender, DownloadProgressEventArgs e)
        {
            DownloadProgress = e.Progress;
            var speedText = e.DownloadSpeedMbps > 0 ? ResourceHelper.FormatString("Update.DownloadSpeed", e.DownloadSpeedMbps.ToString("F2")) : "";
            DownloadStatusText = ResourceHelper.FormatString("Update.DownloadingWithProgress", e.Progress.ToString("P0"), speedText);
        }

        private void OnDownloadCompleted(object? sender, DownloadCompletedEventArgs e)
        {
            if (e.Success)
            {
                DownloadStatusText = ResourceHelper.GetString("Update.DownloadComplete", "Download complete!");
                ((AsyncRelayCommand)InstallUpdateCommand).NotifyCanExecuteChanged();
            }
            else
            {
                ErrorMessage = e.ErrorMessage ?? ResourceHelper.GetString("Update.DownloadFailed", "Download failed");
                DownloadStatusText = ResourceHelper.GetString("Update.DownloadFailed", "Download failed");
            }
        }
    }

    /// <summary>
    /// Simple relay command implementation (local to UpdateViewModel to avoid toolkit ambiguity).
    /// /// </summary>
    internal class UpdateRelayCommand : ICommand
    {
        private readonly Action _execute;
        private readonly Func<bool>? _canExecute;

        public UpdateRelayCommand(Action execute, Func<bool>? canExecute = null)
        {
            _execute = execute ?? throw new ArgumentNullException(nameof(execute));
            _canExecute = canExecute;
        }

        public event EventHandler? CanExecuteChanged;

        public bool CanExecute(object? parameter) => _canExecute?.Invoke() ?? true;

        public void Execute(object? parameter) => _execute();

        public void RaiseCanExecuteChanged() => CanExecuteChanged?.Invoke(this, EventArgs.Empty);
    }
}




