using System;
using System.Collections.ObjectModel;
using System.IO;
using System.Linq;
using System.Threading;
using System.Threading.Tasks;
using CommunityToolkit.Mvvm.ComponentModel;
using CommunityToolkit.Mvvm.Input;
using VoiceStudio.Core.Models;
using VoiceStudio.Core.Panels;
using VoiceStudio.Core.Services;
using VoiceStudio.App.Utilities;
using Windows.Storage;
using Windows.Storage.Pickers;

namespace VoiceStudio.App.ViewModels
{
  /// <summary>
  /// ViewModel for the BackupRestoreView panel - Backup and restore system.
  /// </summary>
  public partial class BackupRestoreViewModel : BaseViewModel, IPanelView
  {
    private readonly IBackendClient _backendClient;

    public string PanelId => "backup_restore";
    public string DisplayName => ResourceHelper.GetString("Panel.BackupRestore.DisplayName", "Backup & Restore");
    public PanelRegion Region => PanelRegion.Right;

    [ObservableProperty]
    private ObservableCollection<BackupItem> backups = new();

    [ObservableProperty]
    private BackupItem? selectedBackup;

    [ObservableProperty]
    private bool isCreatingBackup;

    [ObservableProperty]
    private string? backupName;

    [ObservableProperty]
    private bool includeProfiles = true;

    [ObservableProperty]
    private bool includeProjects = true;

    [ObservableProperty]
    private bool includeSettings = true;

    [ObservableProperty]
    private bool includeModels;

    [ObservableProperty]
    private string? backupDescription;

    [ObservableProperty]
    private bool isRestoring;

    [ObservableProperty]
    private bool restoreProfiles = true;

    [ObservableProperty]
    private bool restoreProjects = true;

    [ObservableProperty]
    private bool restoreSettings = true;

    [ObservableProperty]
    private bool restoreModels;

    public BackupRestoreViewModel(IViewModelContext context, IBackendClient backendClient)
        : base(context)
    {
      _backendClient = backendClient ?? throw new ArgumentNullException(nameof(backendClient));

      LoadBackupsCommand = new EnhancedAsyncRelayCommand(async (ct) =>
      {
        using var profiler = PerformanceProfiler.StartCommand("LoadBackups");
        await LoadBackupsAsync(ct);
      });
      CreateBackupCommand = new EnhancedAsyncRelayCommand(async (ct) =>
      {
        using var profiler = PerformanceProfiler.StartCommand("CreateBackup");
        await CreateBackupAsync(ct);
      });
      DownloadBackupCommand = new EnhancedAsyncRelayCommand<BackupItem>(async (backup, ct) =>
      {
        using var profiler = PerformanceProfiler.StartCommand("DownloadBackup");
        await DownloadBackupAsync(backup, ct);
      });
      RestoreBackupCommand = new EnhancedAsyncRelayCommand<BackupItem>(async (backup, ct) =>
      {
        using var profiler = PerformanceProfiler.StartCommand("RestoreBackup");
        await RestoreBackupAsync(backup, ct);
      });
      DeleteBackupCommand = new EnhancedAsyncRelayCommand<BackupItem>(async (backup, ct) =>
      {
        using var profiler = PerformanceProfiler.StartCommand("DeleteBackup");
        await DeleteBackupAsync(backup, ct);
      });
      UploadBackupCommand = new EnhancedAsyncRelayCommand(async (ct) =>
      {
        using var profiler = PerformanceProfiler.StartCommand("UploadBackup");
        await UploadBackupAsync(ct);
      });

      // Load initial data
      _ = LoadBackupsAsync(CancellationToken.None);
    }

    public IAsyncRelayCommand LoadBackupsCommand { get; }
    public IAsyncRelayCommand CreateBackupCommand { get; }
    public IAsyncRelayCommand<BackupItem> DownloadBackupCommand { get; }
    public IAsyncRelayCommand<BackupItem> RestoreBackupCommand { get; }
    public IAsyncRelayCommand<BackupItem> DeleteBackupCommand { get; }
    public IAsyncRelayCommand UploadBackupCommand { get; }

    private async Task LoadBackupsAsync(CancellationToken cancellationToken)
    {
      IsLoading = true;
      ErrorMessage = null;

      try
      {
        var backups = await _backendClient.GetBackupsAsync(cancellationToken);

        Backups.Clear();
        if (backups != null)
        {
          foreach (var backup in backups)
          {
            Backups.Add(new BackupItem(backup));
          }
        }
      }
      catch (OperationCanceledException)
      {
        return; // User cancelled
      }
      catch (Exception ex)
      {
        ErrorMessage = ResourceHelper.FormatString("BackupRestore.LoadBackupsFailed", ex.Message);
        await HandleErrorAsync(ex, "LoadBackups");
      }
      finally
      {
        IsLoading = false;
      }
    }

    private async Task CreateBackupAsync(CancellationToken cancellationToken)
    {
      if (string.IsNullOrWhiteSpace(BackupName))
      {
        ErrorMessage = ResourceHelper.GetString("BackupRestore.BackupNameRequired", "Backup name is required");
        return;
      }

      IsLoading = true;
      IsCreatingBackup = true;
      ErrorMessage = null;

      try
      {
        var createRequest = new BackupCreateRequest
        {
          Name = BackupName,
          IncludesProfiles = IncludeProfiles,
          IncludesProjects = IncludeProjects,
          IncludesSettings = IncludeSettings,
          IncludesModels = IncludeModels,
          Description = BackupDescription
        };

        var created = await _backendClient.CreateBackupAsync(createRequest, cancellationToken);

        if (created != null)
        {
          Backups.Insert(0, new BackupItem(created));
          StatusMessage = ResourceHelper.FormatString("BackupRestore.BackupCreatedSuccess", created.Name);
        }

        // Reset form
        BackupName = null;
        BackupDescription = null;
        IncludeProfiles = true;
        IncludeProjects = true;
        IncludeSettings = true;
        IncludeModels = false;
      }
      catch (OperationCanceledException)
      {
        return; // User cancelled
      }
      catch (Exception ex)
      {
        ErrorMessage = ResourceHelper.FormatString("BackupRestore.CreateBackupFailed", ex.Message);
        await HandleErrorAsync(ex, "CreateBackup");
      }
      finally
      {
        IsLoading = false;
        IsCreatingBackup = false;
      }
    }

    private async Task DownloadBackupAsync(BackupItem? backup, CancellationToken cancellationToken)
    {
      if (backup == null)
        return;

      IsLoading = true;
      ErrorMessage = null;
      StatusMessage = $"Downloading backup '{backup.Name}'...";

      try
      {
        // Get download stream from backend
        await using var stream = await _backendClient.DownloadBackupAsync(backup.Id, cancellationToken);

        // Show file save picker
        var savePicker = new FileSavePicker();
        savePicker.SuggestedStartLocation = PickerLocationId.DocumentsLibrary;
        savePicker.FileTypeChoices.Add("ZIP Archive", new[] { ".zip" });
        savePicker.SuggestedFileName = $"{backup.Name}.zip";

        var file = await savePicker.PickSaveFileAsync();
        cancellationToken.ThrowIfCancellationRequested();

        if (file != null)
        {
          // Write stream to file
          await using var fileStream = await file.OpenStreamForWriteAsync();
          await stream.CopyToAsync(fileStream, cancellationToken);
          await fileStream.FlushAsync(cancellationToken);

          StatusMessage = ResourceHelper.FormatString("BackupRestore.BackupDownloaded", backup.Name, file.Name);
        }
        else
        {
          StatusMessage = ResourceHelper.GetString("BackupRestore.DownloadCancelled", "Download cancelled");
        }
      }
      catch (OperationCanceledException)
      {
        StatusMessage = ResourceHelper.GetString("BackupRestore.DownloadCancelled", "Download cancelled");
        return; // User cancelled
      }
      catch (Exception ex)
      {
        ErrorMessage = ResourceHelper.FormatString("BackupRestore.DownloadBackupFailed", ex.Message);
        StatusMessage = null;
        await HandleErrorAsync(ex, "DownloadBackup");
      }
      finally
      {
        IsLoading = false;
      }
    }

    private async Task RestoreBackupAsync(BackupItem? backup, CancellationToken cancellationToken)
    {
      if (backup == null)
        return;

      IsLoading = true;
      IsRestoring = true;
      ErrorMessage = null;

      try
      {
        var request = new RestoreRequest
        {
          BackupId = backup.Id,
          RestoreProfiles = RestoreProfiles,
          RestoreProjects = RestoreProjects,
          RestoreSettings = RestoreSettings,
          RestoreModels = RestoreModels
        };

        await _backendClient.RestoreBackupAsync(backup.Id, request, cancellationToken);

        StatusMessage = ResourceHelper.FormatString("BackupRestore.BackupRestoredSuccess", backup.Name);
      }
      catch (OperationCanceledException)
      {
        return; // User cancelled
      }
      catch (Exception ex)
      {
        ErrorMessage = ResourceHelper.FormatString("BackupRestore.RestoreBackupFailed", ex.Message);
        await HandleErrorAsync(ex, "RestoreBackup");
      }
      finally
      {
        IsLoading = false;
        IsRestoring = false;
      }
    }

    private async Task DeleteBackupAsync(BackupItem? backup, CancellationToken cancellationToken)
    {
      if (backup == null)
        return;

      IsLoading = true;
      ErrorMessage = null;

      try
      {
        await _backendClient.DeleteBackupAsync(backup.Id, cancellationToken);

        Backups.Remove(backup);
        StatusMessage = ResourceHelper.FormatString("BackupRestore.BackupDeleted", backup.Name);
      }
      catch (OperationCanceledException)
      {
        return; // User cancelled
      }
      catch (Exception ex)
      {
        ErrorMessage = ResourceHelper.FormatString("BackupRestore.DeleteBackupFailed", ex.Message);
        await HandleErrorAsync(ex, "DeleteBackup");
      }
      finally
      {
        IsLoading = false;
      }
    }

    private async Task UploadBackupAsync(CancellationToken cancellationToken)
    {
      IsLoading = true;
      ErrorMessage = null;
      StatusMessage = ResourceHelper.GetString("BackupRestore.SelectingBackupFile", "Selecting backup file...");

      try
      {
        // Show file open picker
        var openPicker = new FileOpenPicker();
        openPicker.SuggestedStartLocation = PickerLocationId.DocumentsLibrary;
        openPicker.FileTypeFilter.Add(".zip");

        var file = await openPicker.PickSingleFileAsync();
        cancellationToken.ThrowIfCancellationRequested();

        if (file != null)
        {
          StatusMessage = ResourceHelper.FormatString("BackupRestore.UploadingBackup", file.Name);

          // Read file stream
          await using var fileStream = await file.OpenStreamForReadAsync();

          // Upload backup
          var uploadedBackup = await _backendClient.UploadBackupAsync(fileStream, file.Name, cancellationToken);

          // Refresh backups list
          await LoadBackupsAsync(cancellationToken);

          StatusMessage = ResourceHelper.FormatString("BackupRestore.BackupUploadedSuccess", uploadedBackup.Name);
        }
        else
        {
          StatusMessage = ResourceHelper.GetString("BackupRestore.UploadCancelled", "Upload cancelled");
        }
      }
      catch (OperationCanceledException)
      {
        StatusMessage = ResourceHelper.GetString("BackupRestore.UploadCancelled", "Upload cancelled");
        return; // User cancelled
      }
      catch (Exception ex)
      {
        ErrorMessage = ResourceHelper.FormatString("BackupRestore.UploadBackupFailed", ex.Message);
        await HandleErrorAsync(ex, "UploadBackup");
      }
      finally
      {
        IsLoading = false;
      }
    }

    // Data models
    public class BackupItem : ObservableObject
    {
      public string Id { get; set; }
      public string Name { get; set; }
      public string Created { get; set; }
      public long SizeBytes { get; set; }
      public string SizeDisplay { get; set; }
      public bool IncludesProfiles { get; set; }
      public bool IncludesProjects { get; set; }
      public bool IncludesSettings { get; set; }
      public bool IncludesModels { get; set; }
      public string? Description { get; set; }

      public BackupItem(BackupInfo backup)
      {
        Id = backup.Id;
        Name = backup.Name;
        Created = backup.Created;
        SizeBytes = backup.SizeBytes;
        SizeDisplay = FormatBytes(backup.SizeBytes);
        IncludesProfiles = backup.IncludesProfiles;
        IncludesProjects = backup.IncludesProjects;
        IncludesSettings = backup.IncludesSettings;
        IncludesModels = backup.IncludesModels;
        Description = backup.Description;
      }

      private static string FormatBytes(long bytes)
      {
        string[] sizes = { "B", "KB", "MB", "GB", "TB" };
        double len = bytes;
        int order = 0;
        while (len >= 1024 && order < sizes.Length - 1)
        {
          order++;
          len /= 1024;
        }
        return $"{len:0.##} {sizes[order]}";
      }
    }
  }
}