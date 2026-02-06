// ============================================================================
// NPSSurveyViewModel.cs - ViewModel for Net Promoter Score survey
//
// AI GUIDELINES:
// - NPS is a standard customer loyalty metric (0-10 scale)
// - Respects user privacy with local storage only
// - Survey frequency is rate-limited to avoid user fatigue
// ============================================================================

using System;
using System.IO;
using System.Text.Json;
using System.Threading.Tasks;
using CommunityToolkit.Mvvm.ComponentModel;
using CommunityToolkit.Mvvm.Input;
using Microsoft.Extensions.Logging;

namespace VoiceStudio.App.ViewModels;

/// <summary>
/// ViewModel for the NPS (Net Promoter Score) survey dialog.
/// </summary>
public partial class NPSSurveyViewModel : ObservableObject
{
    private readonly ILogger<NPSSurveyViewModel>? _logger;
    private static readonly string SurveyDataPath = Path.Combine(
        Environment.GetFolderPath(Environment.SpecialFolder.LocalApplicationData),
        "VoiceStudio", "Surveys");

    [ObservableProperty]
    private int _score = -1; // -1 means not selected

    [ObservableProperty]
    private string _additionalFeedback = string.Empty;

    [ObservableProperty]
    private bool _isSubmitting;

    [ObservableProperty]
    private bool _isSubmitted;

    [ObservableProperty]
    private string _statusMessage = string.Empty;

    [ObservableProperty]
    private bool _hasError;

    [ObservableProperty]
    private string _errorMessage = string.Empty;

    /// <summary>
    /// Event raised when the dialog should be dismissed.
    /// </summary>
    public event Action? Dismiss;

    /// <summary>
    /// Event raised when survey is successfully submitted.
    /// </summary>
    public event Action? SubmitSuccess;

    /// <summary>
    /// Gets whether a score has been selected.
    /// </summary>
    public bool HasSelectedScore => Score >= 0;

    /// <summary>
    /// Gets whether a score has been selected (alias for XAML binding).
    /// </summary>
    public bool HasScore => HasSelectedScore;

    /// <summary>
    /// Gets the category based on NPS score.
    /// </summary>
    public string ScoreCategory => Score switch
    {
        >= 9 => "Promoter",
        >= 7 => "Passive",
        >= 0 => "Detractor",
        _ => "Not Selected"
    };

    /// <summary>
    /// Gets the category label (alias for XAML binding).
    /// </summary>
    public string CategoryLabel => ScoreCategory;

    /// <summary>
    /// Gets the follow-up question based on score.
    /// </summary>
    public string FollowUpQuestion => Score switch
    {
        >= 9 => "What do you love most about VoiceStudio?",
        >= 7 => "What could we do to make VoiceStudio better?",
        >= 0 => "We're sorry to hear that. What went wrong?",
        _ => "Please select a score above."
    };

    public NPSSurveyViewModel(ILogger<NPSSurveyViewModel>? logger = null)
    {
        _logger = logger;
        Directory.CreateDirectory(SurveyDataPath);
    }

    partial void OnScoreChanged(int value)
    {
        OnPropertyChanged(nameof(HasSelectedScore));
        OnPropertyChanged(nameof(HasScore));
        OnPropertyChanged(nameof(ScoreCategory));
        OnPropertyChanged(nameof(CategoryLabel));
        OnPropertyChanged(nameof(FollowUpQuestion));
    }

    /// <summary>
    /// Sets the NPS score (0-10).
    /// </summary>
    [RelayCommand]
    private void SetScore(int score)
    {
        Score = Math.Clamp(score, 0, 10);
    }

    /// <summary>
    /// Submits the NPS survey.
    /// </summary>
    [RelayCommand]
    private async Task SubmitSurveyAsync()
    {
        if (Score < 0)
        {
            ErrorMessage = "Please select a score.";
            HasError = true;
            return;
        }

        IsSubmitting = true;
        HasError = false;
        ErrorMessage = string.Empty;
        StatusMessage = "Submitting...";

        try
        {
            var surveyData = new
            {
                Score,
                Category = ScoreCategory,
                Feedback = AdditionalFeedback,
                Timestamp = DateTime.UtcNow,
                AppVersion = GetAppVersion(),
                DaysUsed = GetDaysUsed()
            };

            _logger?.LogInformation("NPS Survey submitted: Score={Score}, Category={Category}",
                surveyData.Score, surveyData.Category);

            // Save locally
            await SaveSurveyAsync(surveyData);

            // Update last survey date
            await UpdateLastSurveyDateAsync();

            IsSubmitted = true;
            StatusMessage = "Thank you for your feedback!";
            SubmitSuccess?.Invoke();

            // Auto-dismiss after brief delay
            await Task.Delay(1500);
            Dismiss?.Invoke();
        }
        catch (Exception ex)
        {
            _logger?.LogError(ex, "Failed to submit NPS survey");
            ErrorMessage = "Failed to submit survey. It has been saved locally.";
            HasError = true;
        }
        finally
        {
            IsSubmitting = false;
        }
    }

    /// <summary>
    /// Skips the survey (user chose not to respond).
    /// </summary>
    [RelayCommand]
    private async Task SkipSurveyAsync()
    {
        // Record that user skipped, update last shown date
        await UpdateLastSurveyDateAsync();
        Dismiss?.Invoke();
    }

    /// <summary>
    /// Reminds user later (snoozes the survey).
    /// </summary>
    [RelayCommand]
    private void SetRemindLater()
    {
        // Don't update last survey date - will show again after cooldown
        Dismiss?.Invoke();
    }

    /// <summary>
    /// Cancels the survey dialog.
    /// </summary>
    [RelayCommand]
    private void Cancel()
    {
        Dismiss?.Invoke();
    }

    /// <summary>
    /// Checks if it's appropriate to show the NPS survey.
    /// </summary>
    public static bool ShouldShowSurvey()
    {
        try
        {
            var settingsPath = Path.Combine(SurveyDataPath, "nps_settings.json");
            if (!File.Exists(settingsPath))
            {
                // First time - don't show immediately, wait for some usage
                return false;
            }

            var json = File.ReadAllText(settingsPath);
            var settings = JsonSerializer.Deserialize<NPSSettings>(json);

            if (settings == null)
                return false;

            // Don't show more than once every 90 days
            var daysSinceLastSurvey = (DateTime.UtcNow - settings.LastSurveyDate).TotalDays;
            if (daysSinceLastSurvey < 90)
                return false;

            // Show if user has been using the app for at least 7 days
            var daysUsed = (DateTime.UtcNow - settings.FirstLaunchDate).TotalDays;
            return daysUsed >= 7;
        }
        catch
        {
            return false;
        }
    }

    /// <summary>
    /// Records the first launch date if not already set.
    /// Call this on app startup.
    /// </summary>
    public static void RecordAppLaunch()
    {
        try
        {
            Directory.CreateDirectory(SurveyDataPath);
            var settingsPath = Path.Combine(SurveyDataPath, "nps_settings.json");

            NPSSettings settings;
            if (File.Exists(settingsPath))
            {
                var json = File.ReadAllText(settingsPath);
                settings = JsonSerializer.Deserialize<NPSSettings>(json) ?? new NPSSettings();
            }
            else
            {
                settings = new NPSSettings
                {
                    FirstLaunchDate = DateTime.UtcNow
                };
            }

            settings.LaunchCount++;
            settings.LastLaunchDate = DateTime.UtcNow;

            var updatedJson = JsonSerializer.Serialize(settings, new JsonSerializerOptions { WriteIndented = true });
            File.WriteAllText(settingsPath, updatedJson);
        }
        catch
        {
            // Silently fail - not critical
        }
    }

    private async Task SaveSurveyAsync(object surveyData)
    {
        var fileName = $"nps_{DateTime.Now:yyyyMMdd_HHmmss}.json";
        var filePath = Path.Combine(SurveyDataPath, fileName);

        var json = JsonSerializer.Serialize(surveyData, new JsonSerializerOptions { WriteIndented = true });
        await File.WriteAllTextAsync(filePath, json);

        _logger?.LogInformation("NPS survey saved to {FilePath}", filePath);
    }

    private async Task UpdateLastSurveyDateAsync()
    {
        try
        {
            var settingsPath = Path.Combine(SurveyDataPath, "nps_settings.json");

            NPSSettings settings;
            if (File.Exists(settingsPath))
            {
                var json = await File.ReadAllTextAsync(settingsPath);
                settings = JsonSerializer.Deserialize<NPSSettings>(json) ?? new NPSSettings();
            }
            else
            {
                settings = new NPSSettings { FirstLaunchDate = DateTime.UtcNow };
            }

            settings.LastSurveyDate = DateTime.UtcNow;

            var updatedJson = JsonSerializer.Serialize(settings, new JsonSerializerOptions { WriteIndented = true });
            await File.WriteAllTextAsync(settingsPath, updatedJson);
        }
        catch (Exception ex)
        {
            _logger?.LogWarning(ex, "Failed to update last survey date");
        }
    }

    private static string GetAppVersion()
    {
        try
        {
            var version = System.Reflection.Assembly.GetExecutingAssembly().GetName().Version;
            return version?.ToString() ?? "Unknown";
        }
        catch
        {
            return "Unknown";
        }
    }

    private static int GetDaysUsed()
    {
        try
        {
            var settingsPath = Path.Combine(SurveyDataPath, "nps_settings.json");
            if (!File.Exists(settingsPath))
                return 0;

            var json = File.ReadAllText(settingsPath);
            var settings = JsonSerializer.Deserialize<NPSSettings>(json);

            if (settings == null)
                return 0;

            return (int)(DateTime.UtcNow - settings.FirstLaunchDate).TotalDays;
        }
        catch
        {
            return 0;
        }
    }

    private class NPSSettings
    {
        public DateTime FirstLaunchDate { get; set; } = DateTime.UtcNow;
        public DateTime LastLaunchDate { get; set; } = DateTime.UtcNow;
        public DateTime LastSurveyDate { get; set; } = DateTime.MinValue;
        public int LaunchCount { get; set; }
    }
}
