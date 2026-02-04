using System;
using System.Collections.ObjectModel;
using System.Collections.Generic;
using System.Linq;
using System.Threading;
using System.Threading.Tasks;
using CommunityToolkit.Mvvm.ComponentModel;
using CommunityToolkit.Mvvm.Input;
using VoiceStudio.Core.Panels;
using VoiceStudio.Core.Services;
using VoiceStudio.App.Utilities;
using ProsodyConfigModel = VoiceStudio.App.ViewModels.ProsodyViewModel.ProsodyConfig;

namespace VoiceStudio.App.ViewModels
{
  /// <summary>
  /// ViewModel for the ProsodyView panel - Prosody & phoneme control.
  /// </summary>
  public partial class ProsodyViewModel : BaseViewModel, IPanelView
  {
    private readonly IBackendClient _backendClient;

    public string PanelId => "prosody";
    public string DisplayName => ResourceHelper.GetString("Panel.Prosody.DisplayName", "Prosody & Phoneme Control");
    public PanelRegion Region => PanelRegion.Center;

    [ObservableProperty]
    private ObservableCollection<ProsodyConfigItem> configs = new();

    [ObservableProperty]
    private ProsodyConfigItem? selectedConfig;

    [ObservableProperty]
    private string configName = string.Empty;

    [ObservableProperty]
    private double pitch = 1.0;

    [ObservableProperty]
    private double rate = 1.0;

    [ObservableProperty]
    private double volume = 1.0;

    [ObservableProperty]
    private string? intonation;

    [ObservableProperty]
    private ObservableCollection<string> availableIntonations = new() { "flat", "rising", "falling", "rising-falling", "falling-rising" };

    [ObservableProperty]
    private string inputText = string.Empty;

    [ObservableProperty]
    private ObservableCollection<PhonemeItem> phonemes = new();

    [ObservableProperty]
    private string? selectedVoiceProfileId;

    [ObservableProperty]
    private ObservableCollection<string> availableVoiceProfiles = new();

    [ObservableProperty]
    private string? selectedEngine;

    [ObservableProperty]
    private ObservableCollection<string> availableEngines = new();

    public ProsodyViewModel(IViewModelContext context, IBackendClient backendClient)
        : base(context)
    {
      _backendClient = backendClient ?? throw new ArgumentNullException(nameof(backendClient));

      LoadConfigsCommand = new EnhancedAsyncRelayCommand(async (ct) =>
      {
        using var profiler = PerformanceProfiler.StartCommand("LoadConfigs");
        await LoadConfigsAsync(ct);
      }, () => !IsLoading);
      CreateConfigCommand = new EnhancedAsyncRelayCommand(async (ct) =>
      {
        using var profiler = PerformanceProfiler.StartCommand("CreateConfig");
        await CreateConfigAsync(ct);
      }, () => !IsLoading);
      UpdateConfigCommand = new EnhancedAsyncRelayCommand(async (ct) =>
      {
        using var profiler = PerformanceProfiler.StartCommand("UpdateConfig");
        await UpdateConfigAsync(ct);
      }, () => !IsLoading);
      DeleteConfigCommand = new EnhancedAsyncRelayCommand(async (ct) =>
      {
        using var profiler = PerformanceProfiler.StartCommand("DeleteConfig");
        await DeleteConfigAsync(ct);
      }, () => SelectedConfig != null && !IsLoading);
      AnalyzePhonemesCommand = new EnhancedAsyncRelayCommand(async (ct) =>
      {
        using var profiler = PerformanceProfiler.StartCommand("AnalyzePhonemes");
        await AnalyzePhonemesAsync(ct);
      }, () => !string.IsNullOrWhiteSpace(InputText) && !IsLoading);
      ApplyProsodyCommand = new EnhancedAsyncRelayCommand(async (ct) =>
      {
        using var profiler = PerformanceProfiler.StartCommand("ApplyProsody");
        await ApplyProsodyAsync(ct);
      }, () => SelectedConfig != null && !string.IsNullOrEmpty(SelectedVoiceProfileId) && !string.IsNullOrWhiteSpace(InputText) && !IsLoading);
      RefreshCommand = new EnhancedAsyncRelayCommand(async (ct) =>
      {
        using var profiler = PerformanceProfiler.StartCommand("Refresh");
        await RefreshAsync(ct);
      }, () => !IsLoading);

      // Load initial data
      _ = LoadConfigsAsync(CancellationToken.None);
    }

    public IAsyncRelayCommand LoadConfigsCommand { get; }
    public IAsyncRelayCommand CreateConfigCommand { get; }
    public IAsyncRelayCommand UpdateConfigCommand { get; }
    public IAsyncRelayCommand DeleteConfigCommand { get; }
    public IAsyncRelayCommand AnalyzePhonemesCommand { get; }
    public IAsyncRelayCommand ApplyProsodyCommand { get; }
    public IAsyncRelayCommand RefreshCommand { get; }

    partial void OnSelectedConfigChanged(ProsodyConfigItem? value)
    {
      if (value != null)
      {
        ConfigName = value.Name;
        Pitch = value.Pitch;
        Rate = value.Rate;
        Volume = value.Volume;
        Intonation = value.Intonation;
      }
    }

    private async Task LoadConfigsAsync(CancellationToken cancellationToken)
    {
      IsLoading = true;
      ErrorMessage = null;

      try
      {
        var configs = await _backendClient.SendRequestAsync<object, ProsodyConfig[]>(
            "/api/prosody/configs",
            null,
            System.Net.Http.HttpMethod.Get,
            cancellationToken
        );

        if (configs != null)
        {
          Configs.Clear();
          foreach (var config in configs)
          {
            Configs.Add(new ProsodyConfigItem(config));
          }
        }
      }
      catch (OperationCanceledException)
      {
        return; // User cancelled
      }
      catch (Exception ex)
      {
        await HandleErrorAsync(ex, "LoadConfigs");
      }
      finally
      {
        IsLoading = false;
      }
    }

    private async Task CreateConfigAsync(CancellationToken cancellationToken)
    {
      if (string.IsNullOrWhiteSpace(ConfigName))
      {
        ErrorMessage = ResourceHelper.GetString("Prosody.ConfigNameRequired", "Config name is required");
        return;
      }

      IsLoading = true;
      ErrorMessage = null;

      try
      {
        var request = new
        {
          name = ConfigName,
          pitch = Pitch,
          rate = Rate,
          volume = Volume,
          intonation = Intonation
        };

        var config = await _backendClient.SendRequestAsync<object, ProsodyConfig>(
            "/api/prosody/configs",
            request,
            System.Net.Http.HttpMethod.Post,
            cancellationToken
        );

        if (config != null)
        {
          var configItem = new ProsodyConfigItem(config);
          Configs.Add(configItem);
          SelectedConfig = configItem;
          StatusMessage = ResourceHelper.GetString("Prosody.ConfigCreated", "Config created");
        }
      }
      catch (OperationCanceledException)
      {
        return; // User cancelled
      }
      catch (Exception ex)
      {
        await HandleErrorAsync(ex, "CreateConfig");
      }
      finally
      {
        IsLoading = false;
      }
    }

    private async Task UpdateConfigAsync(CancellationToken cancellationToken = default)
    {
      if (SelectedConfig == null)
      {
        ErrorMessage = ResourceHelper.GetString("Prosody.NoConfigSelected", "No config selected");
        return;
      }

      try
      {
        IsLoading = true;
        ErrorMessage = null;

        var request = new
        {
          name = ConfigName,
          pitch = Pitch,
          rate = Rate,
          volume = Volume,
          intonation = Intonation
        };

        var config = await _backendClient.SendRequestAsync<object, ProsodyConfig>(
            $"/api/prosody/configs/{Uri.EscapeDataString(SelectedConfig.ConfigId)}",
            request,
            System.Net.Http.HttpMethod.Put,
            cancellationToken
        );

        if (config != null)
        {
          var index = Configs.IndexOf(SelectedConfig);
          var updatedItem = new ProsodyConfigItem(config);
          Configs[index] = updatedItem;
          SelectedConfig = updatedItem;
          StatusMessage = ResourceHelper.GetString("Prosody.ConfigUpdated", "Config updated");
        }
      }
      catch (Exception ex)
      {
        ErrorMessage = ResourceHelper.FormatString("Prosody.UpdateConfigFailed", ex.Message);
      }
      finally
      {
        IsLoading = false;
      }
    }

    private async Task DeleteConfigAsync(CancellationToken cancellationToken)
    {
      if (SelectedConfig == null)
      {
        ErrorMessage = ResourceHelper.GetString("Prosody.NoConfigSelected", "No config selected");
        return;
      }

      IsLoading = true;
      ErrorMessage = null;

      try
      {
        await _backendClient.SendRequestAsync<object, object>(
            $"/api/prosody/configs/{Uri.EscapeDataString(SelectedConfig.ConfigId)}",
            null,
            System.Net.Http.HttpMethod.Delete,
            cancellationToken
        );

        Configs.Remove(SelectedConfig);
        SelectedConfig = null;
        StatusMessage = ResourceHelper.GetString("Prosody.ConfigDeleted", "Config deleted");
      }
      catch (OperationCanceledException)
      {
        return; // User cancelled
      }
      catch (Exception ex)
      {
        await HandleErrorAsync(ex, "DeleteConfig");
      }
      finally
      {
        IsLoading = false;
      }
    }

    private async Task AnalyzePhonemesAsync(CancellationToken cancellationToken)
    {
      if (string.IsNullOrWhiteSpace(InputText))
      {
        ErrorMessage = ResourceHelper.GetString("Prosody.TextRequired", "Text is required");
        return;
      }

      IsLoading = true;
      ErrorMessage = null;

      try
      {
        var response = await _backendClient.SendRequestAsync<object, PhonemeAnalysisResponse>(
            $"/api/prosody/phonemes/analyze?text={Uri.EscapeDataString(InputText)}&language=en",
            null,
            System.Net.Http.HttpMethod.Post,
            cancellationToken
        );

        if (response != null)
        {
          Phonemes.Clear();
          for (int i = 0; i < response.Phonemes.Length; i++)
          {
            Phonemes.Add(new PhonemeItem
            {
              Phoneme = response.Phonemes[i],
              Timing = i < response.Timings.Length ? response.Timings[i] : 0.1
            });
          }
          StatusMessage = ResourceHelper.FormatString("Prosody.PhonemesAnalyzed", Phonemes.Count);
        }
      }
      catch (OperationCanceledException)
      {
        return; // User cancelled
      }
      catch (Exception ex)
      {
        await HandleErrorAsync(ex, "AnalyzePhonemes");
      }
      finally
      {
        IsLoading = false;
      }
    }

    private async Task ApplyProsodyAsync(CancellationToken cancellationToken = default)
    {
      if (SelectedConfig == null)
      {
        ErrorMessage = ResourceHelper.GetString("Prosody.NoConfigSelected", "No config selected");
        return;
      }

      if (string.IsNullOrEmpty(SelectedVoiceProfileId))
      {
        ErrorMessage = ResourceHelper.GetString("Prosody.VoiceProfileRequired", "Voice profile must be selected");
        return;
      }

      if (string.IsNullOrWhiteSpace(InputText))
      {
        ErrorMessage = ResourceHelper.GetString("Prosody.TextRequired", "Text is required");
        return;
      }

      try
      {
        IsLoading = true;
        ErrorMessage = null;

        var request = new
        {
          config_id = SelectedConfig.ConfigId,
          text = InputText,
          voice_profile_id = SelectedVoiceProfileId,
          engine = SelectedEngine
        };

        var response = await _backendClient.SendRequestAsync<object, ProsodyApplyResponse>(
            "/api/prosody/apply",
            request,
            System.Net.Http.HttpMethod.Post,
            cancellationToken
        );

        if (response != null)
        {
          StatusMessage = ResourceHelper.FormatString("Prosody.ProsodyApplied", response.AudioId);
        }
      }
      catch (Exception ex)
      {
        ErrorMessage = ResourceHelper.FormatString("Prosody.ApplyProsodyFailed", ex.Message);
      }
      finally
      {
        IsLoading = false;
      }
    }

    private async Task RefreshAsync(CancellationToken cancellationToken)
    {
      await LoadConfigsAsync(cancellationToken);
      StatusMessage = ResourceHelper.GetString("Prosody.Refreshed", "Refreshed");
    }

    // Response models
    public class ProsodyConfig
    {
      public string ConfigId { get; set; } = string.Empty;
      public string Name { get; set; } = string.Empty;
      public double Pitch { get; set; }
      public double Rate { get; set; }
      public double Volume { get; set; }
      public Dictionary<string, object>? Emphasis { get; set; }
      public List<Dictionary<string, object>>? Pauses { get; set; }
      public string? Intonation { get; set; }
    }

    private class PhonemeAnalysisResponse
    {
      public string Text { get; set; } = string.Empty;
      public string[] Phonemes { get; set; } = Array.Empty<string>();
      public double[] Timings { get; set; } = Array.Empty<double>();
      public int[] WordBoundaries { get; set; } = Array.Empty<int>();
    }

    private class ProsodyApplyResponse
    {
      public string AudioId { get; set; } = string.Empty;
      public string ConfigApplied { get; set; } = string.Empty;
      public string Message { get; set; } = string.Empty;
    }
  }

  // Data models
  public class ProsodyConfigItem : ObservableObject
  {
    public string ConfigId { get; set; }
    public string Name { get; set; }
    public double Pitch { get; set; }
    public double Rate { get; set; }
    public double Volume { get; set; }
    public string? Intonation { get; set; }
    public string PitchDisplay => $"{Pitch:F2}x";
    public string RateDisplay => $"{Rate:F2}x";
    public string VolumeDisplay => $"{Volume:P0}";

    public ProsodyConfigItem(ProsodyConfigModel config)
    {
      ConfigId = config.ConfigId;
      Name = config.Name;
      Pitch = config.Pitch;
      Rate = config.Rate;
      Volume = config.Volume;
      Intonation = config.Intonation;
    }
  }

  public class PhonemeItem : ObservableObject
  {
    public string Phoneme { get; set; } = string.Empty;
    public double Timing { get; set; }
    public string TimingDisplay => $"{Timing:F2}s";
  }
}