// ============================================================================
// FeedbackViewModel.cs - ViewModel for user feedback submission
//
// AI GUIDELINES:
// - This ViewModel handles user feedback collection and submission
// - Follows MVVM pattern with CommunityToolkit.Mvvm source generators
// - Feedback is stored locally and optionally sent to backend
// ============================================================================

using System;
using System.Collections.ObjectModel;
using System.Threading.Tasks;
using CommunityToolkit.Mvvm.ComponentModel;
using CommunityToolkit.Mvvm.Input;
using Microsoft.Extensions.Logging;
using VoiceStudio.App.Services;

namespace VoiceStudio.App.ViewModels;

/// <summary>
/// Feedback category options.
/// </summary>
public enum FeedbackCategory
{
    General,
    BugReport,
    FeatureRequest,
    Performance,
    UIExperience,
    Documentation,
    Other
}

/// <summary>
/// ViewModel for the feedback dialog.
/// </summary>
public partial class FeedbackViewModel : BaseViewModel
{
    private readonly ILogger<FeedbackViewModel>? _logger;

    [ObservableProperty]
    private FeedbackCategory _selectedCategory = FeedbackCategory.General;

    [ObservableProperty]
    private int _rating = 0;

    [ObservableProperty]
    private string _feedbackMessage = string.Empty;

    [ObservableProperty]
    private string _emailAddress = string.Empty;

    [ObservableProperty]
    private bool _includeSystemInfo = true;

    [ObservableProperty]
    private bool _isSubmitting;

    [ObservableProperty]
    private bool _isSubmitted;

    [ObservableProperty]
    private string _statusMessage = string.Empty;

    [ObservableProperty]
    private string _errorMessage = string.Empty;

    [ObservableProperty]
    private bool _hasError;

    /// <summary>
    /// Available feedback categories.
    /// </summary>
    public ObservableCollection<FeedbackCategory> Categories { get; } = new()
    {
        FeedbackCategory.General,
        FeedbackCategory.BugReport,
        FeedbackCategory.FeatureRequest,
        FeedbackCategory.Performance,
        FeedbackCategory.UIExperience,
        FeedbackCategory.Documentation,
        FeedbackCategory.Other
    };

    /// <summary>
    /// Event raised when the dialog should be dismissed.
    /// </summary>
    public event Action? Dismiss;

    /// <summary>
    /// Event raised when feedback is successfully submitted.
    /// </summary>
    public event Action? SubmitSuccess;

    public FeedbackViewModel(ILogger<FeedbackViewModel>? logger = null)
        : base(AppServices.GetViewModelContext())
    {
        _logger = logger;
    }

    /// <summary>
    /// Gets whether the form can be submitted.
    /// </summary>
    public bool CanSubmit => !IsSubmitting && !IsSubmitted && !string.IsNullOrWhiteSpace(FeedbackMessage);

    partial void OnFeedbackMessageChanged(string value)
    {
        OnPropertyChanged(nameof(CanSubmit));
    }

    partial void OnIsSubmittingChanged(bool value)
    {
        OnPropertyChanged(nameof(CanSubmit));
    }

    partial void OnIsSubmittedChanged(bool value)
    {
        OnPropertyChanged(nameof(CanSubmit));
    }

    /// <summary>
    /// Sets the rating value (1-5).
    /// </summary>
    [RelayCommand]
    private void SetRating(int rating)
    {
        Rating = Math.Clamp(rating, 0, 5);
    }

    /// <summary>
    /// Submits the feedback.
    /// </summary>
    [RelayCommand(CanExecute = nameof(CanSubmit))]
    private async Task SubmitFeedbackAsync()
    {
        if (string.IsNullOrWhiteSpace(FeedbackMessage))
        {
            ErrorMessage = "Please enter your feedback message.";
            HasError = true;
            return;
        }

        IsSubmitting = true;
        HasError = false;
        ErrorMessage = string.Empty;
        StatusMessage = "Submitting feedback...";

        try
        {
            // Collect feedback data
            var feedbackData = new
            {
                Category = SelectedCategory.ToString(),
                Rating,
                Message = FeedbackMessage,
                Email = EmailAddress,
                IncludeSystemInfo,
                Timestamp = DateTime.UtcNow,
                AppVersion = GetAppVersion(),
                SystemInfo = IncludeSystemInfo ? GetSystemInfo() : null
            };

            // Log feedback locally
            _logger?.LogInformation("Feedback submitted: Category={Category}, Rating={Rating}",
                feedbackData.Category, feedbackData.Rating);

            // Simulate async submission (replace with actual backend call)
            await Task.Delay(500);

            // Save to local feedback log
            await SaveFeedbackLocallyAsync(feedbackData);

            IsSubmitted = true;
            StatusMessage = "Thank you for your feedback!";
            SubmitSuccess?.Invoke();

            // Auto-dismiss after success
            await Task.Delay(1500);
            Dismiss?.Invoke();
        }
        catch (Exception ex)
        {
            _logger?.LogError(ex, "Failed to submit feedback");
            ErrorMessage = "Failed to submit feedback. Your feedback has been saved locally.";
            HasError = true;
        }
        finally
        {
            IsSubmitting = false;
        }
    }

    /// <summary>
    /// Cancels and closes the dialog.
    /// </summary>
    [RelayCommand]
    private void Cancel()
    {
        Dismiss?.Invoke();
    }

    /// <summary>
    /// Clears the form.
    /// </summary>
    [RelayCommand]
    private void ClearForm()
    {
        SelectedCategory = FeedbackCategory.General;
        Rating = 0;
        FeedbackMessage = string.Empty;
        EmailAddress = string.Empty;
        IncludeSystemInfo = true;
        HasError = false;
        ErrorMessage = string.Empty;
        StatusMessage = string.Empty;
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

    private static object? GetSystemInfo()
    {
        try
        {
            return new
            {
                OS = Environment.OSVersion.ToString(),
                Is64Bit = Environment.Is64BitOperatingSystem,
                ProcessorCount = Environment.ProcessorCount,
                DotNetVersion = Environment.Version.ToString(),
                MachineName = Environment.MachineName
            };
        }
        catch
        {
            return null;
        }
    }

    private async Task SaveFeedbackLocallyAsync(object feedbackData)
    {
        try
        {
            var feedbackDir = System.IO.Path.Combine(
                Environment.GetFolderPath(Environment.SpecialFolder.LocalApplicationData),
                "VoiceStudio", "Feedback");

            System.IO.Directory.CreateDirectory(feedbackDir);

            var fileName = $"feedback_{DateTime.Now:yyyyMMdd_HHmmss}.json";
            var filePath = System.IO.Path.Combine(feedbackDir, fileName);

            var json = System.Text.Json.JsonSerializer.Serialize(feedbackData, new System.Text.Json.JsonSerializerOptions
            {
                WriteIndented = true
            });

            await System.IO.File.WriteAllTextAsync(filePath, json);
            _logger?.LogInformation("Feedback saved locally: {FilePath}", filePath);
        }
        catch (Exception ex)
        {
            _logger?.LogWarning(ex, "Failed to save feedback locally");
        }
    }
}
