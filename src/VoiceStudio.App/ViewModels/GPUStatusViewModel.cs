using System;
using System.Collections.ObjectModel;
using System.Linq;
using System.Threading;
using System.Threading.Tasks;
using System.Timers;
using CommunityToolkit.Mvvm.ComponentModel;
using CommunityToolkit.Mvvm.Input;
using VoiceStudio.Core.Panels;
using VoiceStudio.Core.Services;
using VoiceStudio.App.Utilities;
using GPUDeviceModel = VoiceStudio.App.ViewModels.GPUStatusViewModel.GPUDevice;

namespace VoiceStudio.App.ViewModels
{
  /// <summary>
  /// ViewModel for the GPUStatusView panel - GPU monitoring.
  /// </summary>
  public partial class GPUStatusViewModel : BaseViewModel, IPanelView
  {
    private readonly IBackendClient _backendClient;
    private System.Timers.Timer? _refreshTimer;

    public string PanelId => "gpu-status";
    public string DisplayName => ResourceHelper.GetString("Panel.GPUStatus.DisplayName", "GPU Status");
    public PanelRegion Region => PanelRegion.Right;

    [ObservableProperty]
    private ObservableCollection<GPUDeviceItem> devices = new();

    [ObservableProperty]
    private GPUDeviceItem? selectedDevice;

    [ObservableProperty]
    private int totalDevices;

    [ObservableProperty]
    private int availableDevices;

    [ObservableProperty]
    private string? primaryDeviceId;

    [ObservableProperty]
    private bool autoRefresh = true;

    [ObservableProperty]
    private int refreshIntervalSeconds = 5;

    public GPUStatusViewModel(IViewModelContext context, IBackendClient backendClient)
        : base(context)
    {
      _backendClient = backendClient ?? throw new ArgumentNullException(nameof(backendClient));

      LoadGPUStatusCommand = new EnhancedAsyncRelayCommand(async (ct) =>
      {
        using var profiler = PerformanceProfiler.StartCommand("LoadGPUStatus");
        await LoadGPUStatusAsync(ct);
      }, () => !IsLoading);
      RefreshCommand = new EnhancedAsyncRelayCommand(async (ct) =>
      {
        using var profiler = PerformanceProfiler.StartCommand("Refresh");
        await RefreshAsync(ct);
      }, () => !IsLoading);

      // Load initial data
      _ = LoadGPUStatusAsync(CancellationToken.None);

      // Setup auto-refresh
      SetupAutoRefresh();
    }

    public IAsyncRelayCommand LoadGPUStatusCommand { get; }
    public IAsyncRelayCommand RefreshCommand { get; }

    partial void OnAutoRefreshChanged(bool value)
    {
      if (value)
      {
        SetupAutoRefresh();
      }
      else
      {
        StopAutoRefresh();
      }
    }

    partial void OnRefreshIntervalSecondsChanged(int value)
    {
      if (AutoRefresh)
      {
        SetupAutoRefresh();
      }
    }

    private void SetupAutoRefresh()
    {
      StopAutoRefresh();

      if (AutoRefresh && RefreshIntervalSeconds > 0)
      {
        _refreshTimer = new System.Timers.Timer(RefreshIntervalSeconds * 1000);
        _refreshTimer.Elapsed += (_, e) =>
        {
          // Marshal to UI thread to avoid cross-thread ObservableCollection crash
          Microsoft.UI.Dispatching.DispatcherQueue.GetForCurrentThread()?.TryEnqueue(async () =>
          {
            try { await LoadGPUStatusAsync(CancellationToken.None); }
            catch (Exception ex) { System.Diagnostics.Debug.WriteLine($"GPU refresh error: {ex.Message}"); }
          });
        };
        _refreshTimer.AutoReset = true;
        _refreshTimer.Start();
      }
    }

    private void StopAutoRefresh()
    {
      if (_refreshTimer != null)
      {
        _refreshTimer.Stop();
        _refreshTimer.Dispose();
        _refreshTimer = null;
      }
    }

    protected override void Dispose(bool disposing)
    {
      if (disposing)
      {
        StopAutoRefresh();
      }
      base.Dispose(disposing);
    }

    private async Task LoadGPUStatusAsync(CancellationToken cancellationToken)
    {
      try
      {
        IsLoading = true;
        ErrorMessage = null;

        var status = await _backendClient.SendRequestAsync<object, GPUStatus>(
            "/api/gpu-status",
            null,
            System.Net.Http.HttpMethod.Get,
            cancellationToken
        );

        if (status != null)
        {
          Devices.Clear();
          foreach (var device in status.Devices)
          {
            Devices.Add(new GPUDeviceItem(device));
          }

          TotalDevices = status.TotalDevices;
          AvailableDevices = status.AvailableDevices;
          PrimaryDeviceId = status.PrimaryDevice;

          if (Devices.Count > 0 && SelectedDevice == null)
          {
            SelectedDevice = Devices.FirstOrDefault(d => d.DeviceId == PrimaryDeviceId) ?? Devices.First();
          }

          StatusMessage = ResourceHelper.FormatString("GPUStatus.Updated", DateTime.Now);
        }
      }
      catch (OperationCanceledException)
      {
        return; // User cancelled
      }
      catch (Exception ex)
      {
        await HandleErrorAsync(ex, "LoadGPUStatus");
      }
      finally
      {
        IsLoading = false;
      }
    }

    private async Task RefreshAsync(CancellationToken cancellationToken)
    {
      try
      {
        await LoadGPUStatusAsync(cancellationToken);
        StatusMessage = ResourceHelper.GetString("GPUStatus.Refreshed", "Refreshed");
      }
      catch (OperationCanceledException)
      {
        return; // User cancelled
      }
      catch (Exception ex)
      {
        await HandleErrorAsync(ex, "Refresh");
      }
    }

    // Response models
    private class GPUStatus
    {
      public GPUDevice[] Devices { get; set; } = Array.Empty<GPUDevice>();
      public int TotalDevices { get; set; }
      public int AvailableDevices { get; set; }
      public string? PrimaryDevice { get; set; }
    }

    public class GPUDevice
    {
      public string DeviceId { get; set; } = string.Empty;
      public string Name { get; set; } = string.Empty;
      public string Vendor { get; set; } = string.Empty;
      public int MemoryTotalMb { get; set; }
      public int MemoryUsedMb { get; set; }
      public int MemoryFreeMb { get; set; }
      public double UtilizationPercent { get; set; }
      public double? TemperatureCelsius { get; set; }
      public double? PowerUsageWatts { get; set; }
      public string? DriverVersion { get; set; }
      public string? ComputeCapability { get; set; }
      public bool IsAvailable { get; set; }
    }
  }

  // Data models
  public class GPUDeviceItem : ObservableObject
  {
    public string DeviceId { get; set; }
    public string Name { get; set; }
    public string Vendor { get; set; }

    private int _memoryTotalMb;
    public int MemoryTotalMb { get => _memoryTotalMb; set { SetProperty(ref _memoryTotalMb, value); OnPropertyChanged(nameof(MemoryTotalDisplay)); OnPropertyChanged(nameof(MemoryUsagePercent)); } }

    private int _memoryUsedMb;
    public int MemoryUsedMb { get => _memoryUsedMb; set { SetProperty(ref _memoryUsedMb, value); OnPropertyChanged(nameof(MemoryUsedDisplay)); OnPropertyChanged(nameof(MemoryUsagePercent)); } }

    private int _memoryFreeMb;
    public int MemoryFreeMb { get => _memoryFreeMb; set { SetProperty(ref _memoryFreeMb, value); OnPropertyChanged(nameof(MemoryFreeDisplay)); } }

    private double _utilizationPercent;
    public double UtilizationPercent { get => _utilizationPercent; set { SetProperty(ref _utilizationPercent, value); OnPropertyChanged(nameof(UtilizationDisplay)); } }

    private double? _temperatureCelsius;
    public double? TemperatureCelsius { get => _temperatureCelsius; set { SetProperty(ref _temperatureCelsius, value); OnPropertyChanged(nameof(TemperatureDisplay)); } }

    private double? _powerUsageWatts;
    public double? PowerUsageWatts { get => _powerUsageWatts; set { SetProperty(ref _powerUsageWatts, value); OnPropertyChanged(nameof(PowerDisplay)); } }

    public string? DriverVersion { get; set; }
    public string? ComputeCapability { get; set; }
    public bool IsAvailable { get; set; }

    public string MemoryTotalDisplay => $"{MemoryTotalMb / 1024.0:F1} GB";
    public string MemoryUsedDisplay => $"{MemoryUsedMb / 1024.0:F1} GB";
    public string MemoryFreeDisplay => $"{MemoryFreeMb / 1024.0:F1} GB";
    public string MemoryUsagePercent => MemoryTotalMb > 0 ? $"{MemoryUsedMb * 100.0 / MemoryTotalMb:F1}%" : "0.0%";
    public string UtilizationDisplay => $"{UtilizationPercent:F1}%";
    public string TemperatureDisplay => TemperatureCelsius.HasValue ? $"{TemperatureCelsius:F1}°C" : "N/A";
    public string PowerDisplay => PowerUsageWatts.HasValue ? $"{PowerUsageWatts:F1}W" : "N/A";
    public string StatusDisplay => IsAvailable ? "Available" : "Unavailable";

    public GPUDeviceItem(GPUDeviceModel device)
    {
      DeviceId = device.DeviceId;
      Name = device.Name;
      Vendor = device.Vendor;
      MemoryTotalMb = device.MemoryTotalMb;
      MemoryUsedMb = device.MemoryUsedMb;
      MemoryFreeMb = device.MemoryFreeMb;
      UtilizationPercent = device.UtilizationPercent;
      TemperatureCelsius = device.TemperatureCelsius;
      PowerUsageWatts = device.PowerUsageWatts;
      DriverVersion = device.DriverVersion;
      ComputeCapability = device.ComputeCapability;
      IsAvailable = device.IsAvailable;
    }
  }
}