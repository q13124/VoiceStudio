using System;
using System.Collections.ObjectModel;
using System.Linq;
using System.Threading;
using System.Threading.Tasks;
using CommunityToolkit.Mvvm.ComponentModel;
using CommunityToolkit.Mvvm.Input;
using VoiceStudio.Core.Panels;
using VoiceStudio.Core.Services;
using VoiceStudio.App.Services;
using VoiceStudio.App.Utilities;
using SupportedLanguagesResponseModel = VoiceStudio.App.ViewModels.MultilingualSupportViewModel.SupportedLanguagesResponse;

namespace VoiceStudio.App.ViewModels
{
  /// <summary>
  /// ViewModel for the MultilingualSupportView panel - Multi-language interface.
  /// </summary>
  public partial class MultilingualSupportViewModel : BaseViewModel, IPanelView
  {
    private readonly IBackendClient _backendClient;
    private readonly ToastNotificationService? _toastNotificationService;

    public string PanelId => "multilingual-support";
    public string DisplayName => ResourceHelper.GetString("Panel.MultilingualSupport.DisplayName", "Multilingual Support");
    public PanelRegion Region => PanelRegion.Center;

    [ObservableProperty]
    private ObservableCollection<LanguageItem> supportedLanguages = new();

    [ObservableProperty]
    private ObservableCollection<string> selectedTargetLanguages = new();

    [ObservableProperty]
    private string? sourceLanguage;

    [ObservableProperty]
    private string? detectedLanguage;

    [ObservableProperty]
    private string text = string.Empty;

    [ObservableProperty]
    private string translatedText = string.Empty;

    [ObservableProperty]
    private bool autoDetectLanguage = true;

    [ObservableProperty]
    private bool preserveEmotion = true;

    [ObservableProperty]
    private bool preserveStyle = true;

    [ObservableProperty]
    private ObservableCollection<string> availableProfiles = new();

    [ObservableProperty]
    private ObservableCollection<MultilingualAudioItem> synthesizedAudios = new();

    public MultilingualSupportViewModel(IViewModelContext context, IBackendClient backendClient)
        : base(context)
    {
      _backendClient = backendClient ?? throw new ArgumentNullException(nameof(backendClient));

      // Get services (may be null if not initialized)
      try
      {
        _toastNotificationService = ServiceProvider.GetToastNotificationService();
      }
      catch
      {
        // Services may not be initialized yet - that's okay
        _toastNotificationService = null;
      }

      LoadSupportedLanguagesCommand = new EnhancedAsyncRelayCommand(async (ct) =>
      {
        using var profiler = PerformanceProfiler.StartCommand("LoadSupportedLanguages");
        await LoadSupportedLanguagesAsync(ct);
      }, () => !IsLoading);
      TranslateCommand = new EnhancedAsyncRelayCommand(async (ct) =>
      {
        using var profiler = PerformanceProfiler.StartCommand("TranslateText");
        await TranslateTextAsync(ct);
      }, () => !IsLoading);
      SynthesizeCommand = new EnhancedAsyncRelayCommand(async (ct) =>
      {
        using var profiler = PerformanceProfiler.StartCommand("SynthesizeMultilingual");
        await SynthesizeMultilingualAsync(ct);
      }, () => !IsLoading);
      RefreshCommand = new EnhancedAsyncRelayCommand(async (ct) =>
      {
        using var profiler = PerformanceProfiler.StartCommand("Refresh");
        await RefreshAsync(ct);
      }, () => !IsLoading);

      // Load initial data
      _ = LoadSupportedLanguagesAsync(CancellationToken.None);
    }

    public IAsyncRelayCommand LoadSupportedLanguagesCommand { get; }
    public IAsyncRelayCommand TranslateCommand { get; }
    public IAsyncRelayCommand SynthesizeCommand { get; }
    public IAsyncRelayCommand RefreshCommand { get; }

    private async Task LoadSupportedLanguagesAsync(CancellationToken cancellationToken)
    {
      IsLoading = true;
      ErrorMessage = null;

      try
      {
        var response = await _backendClient.SendRequestAsync<object, SupportedLanguagesResponse>(
            "/api/multilingual/supported",
            null,
            System.Net.Http.HttpMethod.Get,
            cancellationToken
        );

        if (response?.Languages != null)
        {
          SupportedLanguages.Clear();
          foreach (var lang in response.Languages)
          {
            SupportedLanguages.Add(new LanguageItem(lang));
          }
          _toastNotificationService?.ShowSuccess(
              ResourceHelper.FormatString("MultilingualSupport.LanguagesLoadedDetail", response.Languages.Length),
              ResourceHelper.GetString("Toast.Title.LanguagesLoaded", "Languages Loaded"));
        }
      }
      catch (OperationCanceledException)
      {
        return; // User cancelled
      }
      catch (Exception ex)
      {
        await HandleErrorAsync(ex, "LoadSupportedLanguages");
      }
      finally
      {
        IsLoading = false;
      }
    }

    private async Task TranslateTextAsync(CancellationToken cancellationToken)
    {
      if (string.IsNullOrWhiteSpace(Text))
      {
        ErrorMessage = ResourceHelper.GetString("MultilingualSupport.TextRequired", "Text is required");
        return;
      }

      if (string.IsNullOrEmpty(SourceLanguage) || SelectedTargetLanguages.Count == 0)
      {
        ErrorMessage = ResourceHelper.GetString("MultilingualSupport.SourceAndTargetRequired", "Source and target languages must be selected");
        return;
      }

      IsLoading = true;
      ErrorMessage = null;

      try
      {
        // Translate to the first selected target language
        var targetLang = SelectedTargetLanguages.FirstOrDefault();
        if (string.IsNullOrEmpty(targetLang))
        {
          ErrorMessage = ResourceHelper.GetString("MultilingualSupport.TargetLanguageRequired", "Target language must be selected");
          return;
        }

        var request = new
        {
          text = Text,
          source_language = SourceLanguage,
          target_language = targetLang
        };

        var response = await _backendClient.SendRequestAsync<object, TranslationResponse>(
            "/api/multilingual/translate",
            request,
            System.Net.Http.HttpMethod.Post,
            cancellationToken
        );

        if (response != null)
        {
          TranslatedText = response.TranslatedText;
          StatusMessage = ResourceHelper.FormatString("MultilingualSupport.TranslationComplete", response.SourceLanguage, response.TargetLanguage);
          _toastNotificationService?.ShowSuccess(
              ResourceHelper.FormatString("MultilingualSupport.TranslationCompleteDetail", response.SourceLanguage, response.TargetLanguage),
              ResourceHelper.GetString("Toast.Title.TranslationComplete", "Translation Complete"));
        }
      }
      catch (OperationCanceledException)
      {
        return; // User cancelled
      }
      catch (Exception ex)
      {
        await HandleErrorAsync(ex, "TranslateText");
      }
      finally
      {
        IsLoading = false;
      }
    }

    private async Task SynthesizeMultilingualAsync(CancellationToken cancellationToken)
    {
      if (string.IsNullOrWhiteSpace(Text))
      {
        ErrorMessage = ResourceHelper.GetString("MultilingualSupport.TextRequired", "Text is required");
        return;
      }

      if (SelectedTargetLanguages.Count == 0)
      {
        ErrorMessage = ResourceHelper.GetString("MultilingualSupport.AtLeastOneTargetRequired", "At least one target language must be selected");
        return;
      }

      try
      {
        IsLoading = true;
        ErrorMessage = null;

        var request = new
        {
          text = Text,
          source_language = AutoDetectLanguage ? null : SourceLanguage,
          target_languages = SelectedTargetLanguages.ToArray(),
          profile_ids = new System.Collections.Generic.Dictionary<string, string>(),
          preserve_emotion = PreserveEmotion,
          preserve_style = PreserveStyle
        };

        var response = await _backendClient.SendRequestAsync<object, MultilingualSynthesisResponse>(
            "/api/multilingual/synthesize",
            request,
            System.Net.Http.HttpMethod.Post,
            cancellationToken
        );

        if (response != null)
        {
          DetectedLanguage = response.DetectedLanguage;
          SynthesizedAudios.Clear();

          foreach (var kvp in response.AudioIds)
          {
            SynthesizedAudios.Add(new MultilingualAudioItem
            {
              LanguageCode = kvp.Key,
              LanguageName = SupportedLanguages.FirstOrDefault(l => l.Code == kvp.Key)?.Name ?? kvp.Key,
              AudioId = kvp.Value
            });
          }

          StatusMessage = response.Message;
          _toastNotificationService?.ShowSuccess(
              ResourceHelper.FormatString("MultilingualSupport.SynthesisCompleteDetail", SynthesizedAudios.Count),
              ResourceHelper.GetString("Toast.Title.SynthesisComplete", "Synthesis Complete"));
        }
      }
      catch (OperationCanceledException)
      {
        return; // User cancelled
      }
      catch (Exception ex)
      {
        await HandleErrorAsync(ex, "SynthesizeMultilingual");
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
        await LoadSupportedLanguagesAsync(cancellationToken);
        StatusMessage = ResourceHelper.GetString("MultilingualSupport.LanguagesRefreshed", "Languages refreshed");
        _toastNotificationService?.ShowSuccess(
            ResourceHelper.GetString("MultilingualSupport.LanguagesRefreshedSuccessfully", "Languages refreshed successfully"),
            ResourceHelper.GetString("Toast.Title.Refreshed", "Refreshed"));
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
    public class SupportedLanguagesResponse
    {
      public LanguageInfo[] Languages { get; set; } = Array.Empty<LanguageInfo>();

      public class LanguageInfo
      {
        public string Code { get; set; } = string.Empty;
        public string Name { get; set; } = string.Empty;
      }
    }

    private class TranslationResponse
    {
      public string TranslatedText { get; set; } = string.Empty;
      public string SourceLanguage { get; set; } = string.Empty;
      public string TargetLanguage { get; set; } = string.Empty;
      public double Confidence { get; set; }
    }

    private class MultilingualSynthesisResponse
    {
      public System.Collections.Generic.Dictionary<string, string> AudioIds { get; set; } = new();
      public string? DetectedLanguage { get; set; }
      public string Message { get; set; } = string.Empty;
    }
  }

  // Data models
  public class LanguageItem : ObservableObject
  {
    public string Code { get; set; }
    public string Name { get; set; }

    public LanguageItem(SupportedLanguagesResponseModel.LanguageInfo info)
    {
      Code = info.Code;
      Name = info.Name;
    }
  }

  public class MultilingualAudioItem : ObservableObject
  {
    public string LanguageCode { get; set; } = string.Empty;
    public string LanguageName { get; set; } = string.Empty;
    public string AudioId { get; set; } = string.Empty;
  }
}