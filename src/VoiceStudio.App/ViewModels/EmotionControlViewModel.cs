using System;
using System.Collections.Generic;
using System.Collections.ObjectModel;
using System.Linq;
using System.Threading;
using System.Threading.Tasks;
using CommunityToolkit.Mvvm.ComponentModel;
using CommunityToolkit.Mvvm.Input;
using VoiceStudio.Core.Panels;
using VoiceStudio.Core.Services;
using VoiceStudio.App.Services;
using VoiceStudio.App.Services.UndoableActions;
using VoiceStudio.App.Utilities;

namespace VoiceStudio.App.ViewModels
{
  /// <summary>
  /// ViewModel for the EmotionControlView panel - Fine-grained emotion control for voice synthesis.
  /// </summary>
  public partial class EmotionControlViewModel : BaseViewModel, IPanelView
  {
    private readonly IBackendClient _backendClient;
    private readonly UndoRedoService? _undoRedoService;

    public string PanelId => "emotion-control";
    public string DisplayName => ResourceHelper.GetString("Panel.EmotionControl.DisplayName", "Emotion Control");
    public PanelRegion Region => PanelRegion.Right;

    [ObservableProperty]
    private ObservableCollection<string> availableEmotions = new();

    [ObservableProperty]
    private string? selectedPrimaryEmotion;

    [ObservableProperty]
    private double primaryIntensity = 50.0;

    [ObservableProperty]
    private string? selectedSecondaryEmotion;

    [ObservableProperty]
    private double secondaryIntensity;

    [ObservableProperty]
    private bool enableBlending;

    [ObservableProperty]
    private string? targetAudioId;

    [ObservableProperty]
    private ObservableCollection<EmotionControlPresetItem> presets = new();

    [ObservableProperty]
    private EmotionControlPresetItem? selectedPreset;

    [ObservableProperty]
    private string? newPresetName;

    [ObservableProperty]
    private string? newPresetDescription;

    [ObservableProperty]
    private bool isSavingPreset;

    [ObservableProperty]
    private string? previewAudioId;

    [ObservableProperty]
    private string? previewAudioUrl;

    [ObservableProperty]
    private bool isLoading;

    [ObservableProperty]
    private string? errorMessage;

    [ObservableProperty]
    private string? statusMessage;

    public EmotionControlViewModel(IViewModelContext context, IBackendClient backendClient)
        : base(context)
    {
      _backendClient = backendClient ?? throw new ArgumentNullException(nameof(backendClient));

      // Get undo/redo service (may be null if not initialized)
      try
      {
        _undoRedoService = AppServices.TryGetUndoRedoService();
      }
      catch
      {
        // Service may not be initialized yet - that's okay
        _undoRedoService = null;
      }

      LoadEmotionsCommand = new EnhancedAsyncRelayCommand(async (ct) =>
      {
        using var profiler = Profiler.StartCommand("LoadEmotions");
        await LoadEmotionsAsync(ct);
      }, () => !IsLoading);
      ApplyEmotionCommand = new EnhancedAsyncRelayCommand(async (ct) =>
      {
        using var profiler = Profiler.StartCommand("ApplyEmotion");
        await ApplyEmotionAsync(ct);
      }, () => !string.IsNullOrWhiteSpace(TargetAudioId) && !string.IsNullOrWhiteSpace(SelectedPrimaryEmotion) && !IsLoading);
      PreviewEmotionCommand = new EnhancedAsyncRelayCommand(async (ct) =>
      {
        using var profiler = Profiler.StartCommand("PreviewEmotion");
        await PreviewEmotionAsync(ct);
      }, () => !string.IsNullOrWhiteSpace(TargetAudioId) && !string.IsNullOrWhiteSpace(SelectedPrimaryEmotion) && !IsLoading);
      LoadPresetsCommand = new EnhancedAsyncRelayCommand(async (ct) =>
      {
        using var profiler = Profiler.StartCommand("LoadPresets");
        await LoadPresetsAsync(ct);
      }, () => !IsLoading);
      SavePresetCommand = new EnhancedAsyncRelayCommand(async (ct) =>
      {
        using var profiler = Profiler.StartCommand("SavePreset");
        await SavePresetAsync(ct);
      }, () => !IsSavingPreset && !string.IsNullOrWhiteSpace(NewPresetName) && !string.IsNullOrWhiteSpace(SelectedPrimaryEmotion) && !IsLoading);
      LoadPresetCommand = new EnhancedAsyncRelayCommand(async (ct) =>
      {
        using var profiler = Profiler.StartCommand("LoadPreset");
        await LoadPresetAsync(ct);
      }, () => SelectedPreset != null && !IsLoading);
      DeletePresetCommand = new EnhancedAsyncRelayCommand(async (ct) =>
      {
        using var profiler = Profiler.StartCommand("DeletePreset");
        await DeletePresetAsync(ct);
      }, () => SelectedPreset != null && !IsLoading);
      RefreshCommand = new EnhancedAsyncRelayCommand(async (ct) =>
      {
        using var profiler = Profiler.StartCommand("Refresh");
        await RefreshAsync(ct);
      }, () => !IsLoading);

      // Load initial data
      _ = LoadEmotionsAsync(CancellationToken.None);
      _ = LoadPresetsAsync(CancellationToken.None);
    }

    public IAsyncRelayCommand LoadEmotionsCommand { get; }
    public IAsyncRelayCommand ApplyEmotionCommand { get; }
    public IAsyncRelayCommand PreviewEmotionCommand { get; }
    public IAsyncRelayCommand LoadPresetsCommand { get; }
    public IAsyncRelayCommand SavePresetCommand { get; }
    public IAsyncRelayCommand LoadPresetCommand { get; }
    public IAsyncRelayCommand DeletePresetCommand { get; }
    public IAsyncRelayCommand RefreshCommand { get; }

    partial void OnIsSavingPresetChanged(bool value)
    {
      SavePresetCommand.NotifyCanExecuteChanged();
    }

    partial void OnNewPresetNameChanged(string? value)
    {
      SavePresetCommand.NotifyCanExecuteChanged();
    }

    partial void OnSelectedPrimaryEmotionChanged(string? value)
    {
      ApplyEmotionCommand.NotifyCanExecuteChanged();
      PreviewEmotionCommand.NotifyCanExecuteChanged();
      SavePresetCommand.NotifyCanExecuteChanged();
    }

    partial void OnTargetAudioIdChanged(string? value)
    {
      ApplyEmotionCommand.NotifyCanExecuteChanged();
      PreviewEmotionCommand.NotifyCanExecuteChanged();
    }

    partial void OnSelectedPresetChanged(EmotionControlPresetItem? value)
    {
      LoadPresetCommand.NotifyCanExecuteChanged();
      DeletePresetCommand.NotifyCanExecuteChanged();
    }

    partial void OnEnableBlendingChanged(bool value)
    {
      if (!value)
      {
        SelectedSecondaryEmotion = null;
        SecondaryIntensity = 0.0;
      }
    }

    private async Task LoadEmotionsAsync(CancellationToken cancellationToken)
    {
      IsLoading = true;
      ErrorMessage = null;

      try
      {
        var emotions = await _backendClient.SendRequestAsync<object, string[]>(
            "/api/emotion/list",
            null,
            System.Net.Http.HttpMethod.Get,
            cancellationToken
        );

        cancellationToken.ThrowIfCancellationRequested();

        if (emotions != null)
        {
          AvailableEmotions.Clear();
          foreach (var emotion in emotions)
          {
            cancellationToken.ThrowIfCancellationRequested();
            AvailableEmotions.Add(emotion);
          }
        }
      }
      catch (OperationCanceledException)
      {
        return; // User cancelled
      }
      catch (Exception ex)
      {
        await HandleErrorAsync(ex, "LoadEmotions");
      }
      finally
      {
        IsLoading = false;
      }
    }

    private async Task ApplyEmotionAsync(CancellationToken cancellationToken)
    {
      if (string.IsNullOrWhiteSpace(TargetAudioId) || string.IsNullOrWhiteSpace(SelectedPrimaryEmotion))
      {
        return;
      }

      IsLoading = true;
      ErrorMessage = null;

      try
      {
        var request = new EmotionApplyExtendedRequest
        {
          AudioId = TargetAudioId,
          PrimaryEmotion = SelectedPrimaryEmotion,
          PrimaryIntensity = (float)PrimaryIntensity,
          SecondaryEmotion = EnableBlending ? SelectedSecondaryEmotion : null,
          SecondaryIntensity = EnableBlending ? (float)SecondaryIntensity : 0.0f
        };

        await _backendClient.SendRequestAsync<EmotionApplyExtendedRequest, object>(
            "/api/emotion/apply-extended",
            request,
            System.Net.Http.HttpMethod.Post,
            cancellationToken
        );

        StatusMessage = ResourceHelper.GetString("EmotionControl.EmotionApplied", "Emotion applied successfully");
      }
      catch (OperationCanceledException)
      {
        return; // User cancelled
      }
      catch (Exception ex)
      {
        await HandleErrorAsync(ex, "ApplyEmotion");
      }
      finally
      {
        IsLoading = false;
      }
    }

    private async Task PreviewEmotionAsync(CancellationToken cancellationToken)
    {
      if (string.IsNullOrWhiteSpace(TargetAudioId) || string.IsNullOrWhiteSpace(SelectedPrimaryEmotion))
      {
        return;
      }

      IsLoading = true;
      ErrorMessage = null;

      try
      {
        var request = new EmotionApplyExtendedRequest
        {
          AudioId = TargetAudioId,
          PrimaryEmotion = SelectedPrimaryEmotion,
          PrimaryIntensity = (float)PrimaryIntensity,
          SecondaryEmotion = EnableBlending ? SelectedSecondaryEmotion : null,
          SecondaryIntensity = EnableBlending ? (float)SecondaryIntensity : 0.0f
        };

        var response = await _backendClient.SendRequestAsync<EmotionApplyExtendedRequest, EmotionPreviewResponse>(
            "/api/emotion/preview",
            request,
            System.Net.Http.HttpMethod.Post,
            cancellationToken
        );

        if (response != null)
        {
          PreviewAudioId = response.AudioId;
          PreviewAudioUrl = $"/api/audio/{response.AudioId}";
          StatusMessage = ResourceHelper.GetString("EmotionControl.PreviewGenerated", "Preview generated successfully");
        }
      }
      catch (OperationCanceledException)
      {
        return; // User cancelled
      }
      catch (Exception ex)
      {
        await HandleErrorAsync(ex, "PreviewEmotion");
      }
      finally
      {
        IsLoading = false;
      }
    }

    private async Task LoadPresetsAsync(CancellationToken cancellationToken)
    {
      IsLoading = true;
      ErrorMessage = null;

      try
      {
        var presets = await _backendClient.SendRequestAsync<object, EmotionPreset[]>(
            "/api/emotion/preset/list",
            null,
            System.Net.Http.HttpMethod.Get,
            cancellationToken
        );

        cancellationToken.ThrowIfCancellationRequested();

        if (presets != null)
        {
          Presets.Clear();
          foreach (var preset in presets)
          {
            cancellationToken.ThrowIfCancellationRequested();
            Presets.Add(new EmotionControlPresetItem(preset));
          }
        }
      }
      catch (OperationCanceledException)
      {
        return; // User cancelled
      }
      catch (Exception ex)
      {
        await HandleErrorAsync(ex, "LoadPresets");
      }
      finally
      {
        IsLoading = false;
      }
    }

    private async Task SavePresetAsync(CancellationToken cancellationToken)
    {
      if (string.IsNullOrWhiteSpace(NewPresetName) || string.IsNullOrWhiteSpace(SelectedPrimaryEmotion))
      {
        return;
      }

      IsSavingPreset = true;
      ErrorMessage = null;

      try
      {
        var request = new EmotionPresetCreateRequest
        {
          Name = NewPresetName,
          Description = NewPresetDescription,
          PrimaryEmotion = SelectedPrimaryEmotion,
          PrimaryIntensity = (float)PrimaryIntensity,
          SecondaryEmotion = EnableBlending ? SelectedSecondaryEmotion : null,
          SecondaryIntensity = EnableBlending ? (float)SecondaryIntensity : 0.0f
        };

        var preset = await _backendClient.SendRequestAsync<EmotionPresetCreateRequest, EmotionPreset>(
            "/api/emotion/preset/save",
            request,
            System.Net.Http.HttpMethod.Post,
            cancellationToken
        );

        cancellationToken.ThrowIfCancellationRequested();

        if (preset != null)
        {
          var presetItem = new EmotionControlPresetItem(preset);
          Presets.Add(presetItem);

          // Register undo action
          if (_undoRedoService != null)
          {
            var action = new CreateEmotionPresetAction(
                Presets,
                _backendClient,
                presetItem,
                onUndo: (p) =>
                {
                  if (SelectedPreset?.PresetId == p.PresetId)
                  {
                    SelectedPreset = Presets.FirstOrDefault();
                  }
                },
                onRedo: (p) => SelectedPreset = p);
            _undoRedoService.RegisterAction(action);
          }

          // Clear form
          NewPresetName = null;
          NewPresetDescription = null;

          StatusMessage = ResourceHelper.GetString("EmotionControl.PresetSaved", "Preset saved successfully");
        }
      }
      catch (OperationCanceledException)
      {
        return; // User cancelled
      }
      catch (Exception ex)
      {
        await HandleErrorAsync(ex, "SavePreset");
      }
      finally
      {
        IsSavingPreset = false;
      }
    }

    private async Task LoadPresetAsync(CancellationToken cancellationToken)
    {
      if (SelectedPreset == null)
      {
        return;
      }

      try
      {
        cancellationToken.ThrowIfCancellationRequested();

        SelectedPrimaryEmotion = SelectedPreset.PrimaryEmotion;
        PrimaryIntensity = SelectedPreset.PrimaryIntensity;

        if (!string.IsNullOrWhiteSpace(SelectedPreset.SecondaryEmotion))
        {
          EnableBlending = true;
          SelectedSecondaryEmotion = SelectedPreset.SecondaryEmotion;
          SecondaryIntensity = SelectedPreset.SecondaryIntensity;
        }
        else
        {
          EnableBlending = false;
          SelectedSecondaryEmotion = null;
          SecondaryIntensity = 0.0;
        }

        StatusMessage = ResourceHelper.GetString("EmotionControl.PresetLoaded", "Preset loaded");
      }
      catch (OperationCanceledException)
      {
        return; // User cancelled
      }
      catch (Exception ex)
      {
        await HandleErrorAsync(ex, "LoadPreset");
      }
    }

    private async Task DeletePresetAsync(CancellationToken cancellationToken)
    {
      if (SelectedPreset == null)
      {
        return;
      }

      IsLoading = true;
      ErrorMessage = null;

      try
      {
        await _backendClient.SendRequestAsync<object, object>(
            $"/api/emotion/preset/{Uri.EscapeDataString(SelectedPreset.PresetId)}",
            null,
            System.Net.Http.HttpMethod.Delete,
            cancellationToken
        );

        cancellationToken.ThrowIfCancellationRequested();

        var presetToDelete = SelectedPreset;
        var originalIndex = Presets.IndexOf(presetToDelete);
        Presets.Remove(presetToDelete);
        SelectedPreset = null;

        // Register undo action
        if (_undoRedoService != null && presetToDelete != null)
        {
          var action = new DeleteEmotionPresetAction(
              Presets,
              _backendClient,
              presetToDelete,
              originalIndex,
              onUndo: (p) => SelectedPreset = p,
              onRedo: (p) =>
              {
                if (SelectedPreset?.PresetId == p.PresetId)
                {
                  SelectedPreset = null;
                }
              });
          _undoRedoService.RegisterAction(action);
        }

        StatusMessage = ResourceHelper.GetString("EmotionControl.PresetDeleted", "Preset deleted successfully");
      }
      catch (OperationCanceledException)
      {
        return; // User cancelled
      }
      catch (Exception ex)
      {
        await HandleErrorAsync(ex, "DeletePreset");
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
        await LoadEmotionsAsync(cancellationToken);
        await LoadPresetsAsync(cancellationToken);
        StatusMessage = ResourceHelper.GetString("EmotionControl.Refreshed", "Refreshed");
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

    // Request/Response models
    private class EmotionApplyExtendedRequest
    {
      public string AudioId { get; set; } = string.Empty;
      public string PrimaryEmotion { get; set; } = string.Empty;
      public float PrimaryIntensity { get; set; }
      public string? SecondaryEmotion { get; set; }
      public float SecondaryIntensity { get; set; }
    }

    public class EmotionPresetCreateRequest
    {
      public string Name { get; set; } = string.Empty;
      public string? Description { get; set; }
      public string PrimaryEmotion { get; set; } = string.Empty;
      public float PrimaryIntensity { get; set; }
      public string? SecondaryEmotion { get; set; }
      public float SecondaryIntensity { get; set; }
    }

    public class EmotionPreset
    {
      public string PresetId { get; set; } = string.Empty;
      public string Name { get; set; } = string.Empty;
      public string? Description { get; set; }
      public string PrimaryEmotion { get; set; } = string.Empty;
      public float PrimaryIntensity { get; set; }
      public string? SecondaryEmotion { get; set; }
      public float SecondaryIntensity { get; set; }
      public string CreatedAt { get; set; } = string.Empty;
      public string UpdatedAt { get; set; } = string.Empty;
    }

    private class EmotionPreviewResponse
    {
      public string AudioId { get; set; } = string.Empty;
      public string Message { get; set; } = string.Empty;
    }
  }

  // Data models
  public class EmotionControlPresetItem : ObservableObject
  {
    public string PresetId { get; set; }
    public string Name { get; set; }
    public string? Description { get; set; }
    public string PrimaryEmotion { get; set; }
    public float PrimaryIntensity { get; set; }
    public string? SecondaryEmotion { get; set; }
    public float SecondaryIntensity { get; set; }
    public string CreatedAt { get; set; }
    public string UpdatedAt { get; set; }

    public string PrimaryEmotionDisplay => PrimaryEmotion.ToUpper();
    public string PrimaryIntensityDisplay => $"{PrimaryIntensity:F0}%";
    public string SecondaryEmotionDisplay => SecondaryEmotion != null ? SecondaryEmotion.ToUpper() : "None";
    public string SecondaryIntensityDisplay => SecondaryIntensity > 0 ? $"{SecondaryIntensity:F0}%" : "0%";
    public string BlendingDisplay => SecondaryEmotion != null ? $"{PrimaryEmotionDisplay} + {SecondaryEmotionDisplay}" : PrimaryEmotionDisplay;

    public EmotionControlPresetItem(EmotionControlViewModel.EmotionPreset preset)
    {
      PresetId = preset.PresetId;
      Name = preset.Name;
      Description = preset.Description;
      PrimaryEmotion = preset.PrimaryEmotion;
      PrimaryIntensity = preset.PrimaryIntensity;
      SecondaryEmotion = preset.SecondaryEmotion;
      SecondaryIntensity = preset.SecondaryIntensity;
      CreatedAt = preset.CreatedAt;
      UpdatedAt = preset.UpdatedAt;
    }
  }
}