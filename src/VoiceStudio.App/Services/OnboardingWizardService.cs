using System;
using System.Collections.Generic;
using System.Linq;
using System.Threading.Tasks;
using Microsoft.UI.Xaml;
using Microsoft.UI.Xaml.Controls;

namespace VoiceStudio.App.Services;

/// <summary>
/// Onboarding wizard service for new users.
/// 
/// Phase 15.3: Smart Onboarding
/// Provides contextual tooltips, feature discovery, and progressive disclosure.
/// </summary>
public class OnboardingWizardService
{
    private readonly Dictionary<string, OnboardingStep> _steps;
    private readonly HashSet<string> _completedSteps;
    private readonly HashSet<string> _skippedFeatures;
    private OnboardingProgress _progress;
    private bool _isWizardActive;

    public event EventHandler<OnboardingStepEventArgs>? StepStarted;
    public event EventHandler<OnboardingStepEventArgs>? StepCompleted;
    public event EventHandler? WizardCompleted;
    public event EventHandler<TooltipEventArgs>? TooltipRequested;

    public OnboardingWizardService()
    {
        _steps = new Dictionary<string, OnboardingStep>();
        _completedSteps = new HashSet<string>();
        _skippedFeatures = new HashSet<string>();
        _progress = new OnboardingProgress();

        RegisterDefaultSteps();
    }

    #region Default Steps

    private void RegisterDefaultSteps()
    {
        // Welcome sequence
        RegisterStep(new OnboardingStep
        {
            StepId = "welcome",
            Title = "Welcome to VoiceStudio",
            Description = "Let's get you started with the basics of voice synthesis.",
            Category = OnboardingCategory.Welcome,
            Order = 1,
            IsRequired = true,
        });

        RegisterStep(new OnboardingStep
        {
            StepId = "select_voice",
            Title = "Choose Your First Voice",
            Description = "Browse our library of voices and select one to try.",
            Category = OnboardingCategory.GettingStarted,
            Order = 2,
            IsRequired = true,
            TargetElement = "VoiceSelector",
            HighlightType = HighlightType.Pulse,
        });

        RegisterStep(new OnboardingStep
        {
            StepId = "enter_text",
            Title = "Enter Your Text",
            Description = "Type or paste the text you want to convert to speech.",
            Category = OnboardingCategory.GettingStarted,
            Order = 3,
            IsRequired = true,
            TargetElement = "TextInput",
        });

        RegisterStep(new OnboardingStep
        {
            StepId = "generate_audio",
            Title = "Generate Audio",
            Description = "Click the Generate button to create your first audio!",
            Category = OnboardingCategory.GettingStarted,
            Order = 4,
            IsRequired = true,
            TargetElement = "GenerateButton",
            HighlightType = HighlightType.Spotlight,
        });

        // Feature discovery
        RegisterStep(new OnboardingStep
        {
            StepId = "discover_emotions",
            Title = "Add Emotions",
            Description = "Make your voice more expressive with emotion controls.",
            Category = OnboardingCategory.FeatureDiscovery,
            Order = 10,
            IsRequired = false,
            TargetElement = "EmotionPanel",
            TriggerCondition = "first_generation_complete",
        });

        RegisterStep(new OnboardingStep
        {
            StepId = "discover_cloning",
            Title = "Clone Your Voice",
            Description = "Create a custom voice from your own recordings.",
            Category = OnboardingCategory.FeatureDiscovery,
            Order = 11,
            IsRequired = false,
            TargetElement = "VoiceCloningButton",
        });

        RegisterStep(new OnboardingStep
        {
            StepId = "discover_effects",
            Title = "Audio Effects",
            Description = "Enhance your audio with professional effects.",
            Category = OnboardingCategory.FeatureDiscovery,
            Order = 12,
            IsRequired = false,
            TargetElement = "EffectsPanel",
        });

        RegisterStep(new OnboardingStep
        {
            StepId = "discover_batch",
            Title = "Batch Processing",
            Description = "Process multiple texts at once for efficiency.",
            Category = OnboardingCategory.FeatureDiscovery,
            Order = 13,
            IsRequired = false,
            TargetElement = "BatchButton",
        });

        // Pro tips
        RegisterStep(new OnboardingStep
        {
            StepId = "tip_shortcuts",
            Title = "Keyboard Shortcuts",
            Description = "Press Ctrl+Shift+P to open the command palette for quick access.",
            Category = OnboardingCategory.ProTips,
            Order = 20,
            IsRequired = false,
        });

        RegisterStep(new OnboardingStep
        {
            StepId = "tip_presets",
            Title = "Save Presets",
            Description = "Save your favorite voice settings as presets for quick reuse.",
            Category = OnboardingCategory.ProTips,
            Order = 21,
            IsRequired = false,
        });
    }

    #endregion

    #region Step Management

    public void RegisterStep(OnboardingStep step)
    {
        _steps[step.StepId] = step;
    }

    public OnboardingStep? GetStep(string stepId)
    {
        return _steps.TryGetValue(stepId, out var step) ? step : null;
    }

    public IEnumerable<OnboardingStep> GetStepsByCategory(OnboardingCategory category)
    {
        return _steps.Values
            .Where(s => s.Category == category)
            .OrderBy(s => s.Order);
    }

    public IEnumerable<OnboardingStep> GetPendingSteps()
    {
        return _steps.Values
            .Where(s => !_completedSteps.Contains(s.StepId) && !_skippedFeatures.Contains(s.StepId))
            .OrderBy(s => s.Order);
    }

    #endregion

    #region Wizard Flow

    public async Task StartWizardAsync()
    {
        if (_isWizardActive)
            return;

        _isWizardActive = true;
        _progress = new OnboardingProgress
        {
            StartedAt = DateTime.Now,
            TotalSteps = _steps.Values.Count(s => s.IsRequired),
        };

        var firstStep = GetPendingSteps().FirstOrDefault(s => s.IsRequired);
        if (firstStep != null)
        {
            await ShowStepAsync(firstStep.StepId);
        }
    }

    public Task ShowStepAsync(string stepId)
    {
        var step = GetStep(stepId);
        if (step == null)
            return Task.CompletedTask;

        _progress.CurrentStepId = stepId;
        StepStarted?.Invoke(this, new OnboardingStepEventArgs(step));

        // Request tooltip display
        TooltipRequested?.Invoke(this, new TooltipEventArgs
        {
            StepId = stepId,
            Title = step.Title,
            Description = step.Description,
            TargetElement = step.TargetElement,
            HighlightType = step.HighlightType,
            Position = step.TooltipPosition,
        });

        return Task.CompletedTask;
    }

    public async Task CompleteStepAsync(string stepId)
    {
        if (!_steps.ContainsKey(stepId))
            return;

        _completedSteps.Add(stepId);
        _progress.CompletedSteps++;

        var step = _steps[stepId];
        StepCompleted?.Invoke(this, new OnboardingStepEventArgs(step));

        // Move to next step
        var nextStep = GetPendingSteps()
            .FirstOrDefault(s => s.IsRequired || s.Category == OnboardingCategory.FeatureDiscovery);

        if (nextStep != null)
        {
            await ShowStepAsync(nextStep.StepId);
        }
        else if (_isWizardActive)
        {
            CompleteWizard();
        }
    }

    public void SkipStep(string stepId)
    {
        _skippedFeatures.Add(stepId);
    }

    public void CompleteWizard()
    {
        _isWizardActive = false;
        _progress.CompletedAt = DateTime.Now;
        WizardCompleted?.Invoke(this, EventArgs.Empty);
    }

    public void PauseWizard()
    {
        _isWizardActive = false;
    }

    public void ResumeWizard()
    {
        if (!_isWizardActive && _progress.CurrentStepId != null)
        {
            _isWizardActive = true;
            _ = ShowStepAsync(_progress.CurrentStepId);
        }
    }

    #endregion

    #region Contextual Tooltips

    public void ShowContextualTip(string featureId, string title, string description, string? targetElement = null)
    {
        if (_skippedFeatures.Contains(featureId))
            return;

        TooltipRequested?.Invoke(this, new TooltipEventArgs
        {
            StepId = featureId,
            Title = title,
            Description = description,
            TargetElement = targetElement,
            IsContextual = true,
        });
    }

    public void ShowFeatureDiscovery(string featureId)
    {
        var step = GetStep(featureId);
        if (step != null && !_completedSteps.Contains(featureId))
        {
            _ = ShowStepAsync(featureId);
        }
    }

    public void DismissTooltip(string stepId, bool dontShowAgain = false)
    {
        if (dontShowAgain)
        {
            _skippedFeatures.Add(stepId);
        }
    }

    #endregion

    #region Progress Tracking

    public OnboardingProgress GetProgress() => _progress;

    public bool IsStepCompleted(string stepId) => _completedSteps.Contains(stepId);

    public bool IsFeatureSkipped(string featureId) => _skippedFeatures.Contains(featureId);

    public double GetCompletionPercentage()
    {
        var requiredSteps = _steps.Values.Count(s => s.IsRequired);
        if (requiredSteps == 0) return 100;

        var completedRequired = _completedSteps.Count(id => _steps.TryGetValue(id, out var step) && step.IsRequired);
        return (double)completedRequired / requiredSteps * 100;
    }

    public bool IsOnboardingComplete()
    {
        return _steps.Values
            .Where(s => s.IsRequired)
            .All(s => _completedSteps.Contains(s.StepId));
    }

    #endregion

    #region Persistence

    public OnboardingState GetState()
    {
        return new OnboardingState
        {
            CompletedSteps = _completedSteps.ToList(),
            SkippedFeatures = _skippedFeatures.ToList(),
            Progress = _progress,
            IsComplete = IsOnboardingComplete(),
        };
    }

    public void RestoreState(OnboardingState state)
    {
        _completedSteps.Clear();
        _skippedFeatures.Clear();

        foreach (var stepId in state.CompletedSteps)
            _completedSteps.Add(stepId);

        foreach (var featureId in state.SkippedFeatures)
            _skippedFeatures.Add(featureId);

        _progress = state.Progress;
    }

    #endregion
}

#region Data Classes

public enum OnboardingCategory
{
    Welcome,
    GettingStarted,
    FeatureDiscovery,
    ProTips,
    Advanced,
}

public enum HighlightType
{
    None,
    Outline,
    Pulse,
    Spotlight,
    Arrow,
}

public enum TooltipPosition
{
    Auto,
    Top,
    Bottom,
    Left,
    Right,
}

public class OnboardingStep
{
    public string StepId { get; set; } = string.Empty;
    public string Title { get; set; } = string.Empty;
    public string Description { get; set; } = string.Empty;
    public OnboardingCategory Category { get; set; }
    public int Order { get; set; }
    public bool IsRequired { get; set; }
    public string? TargetElement { get; set; }
    public HighlightType HighlightType { get; set; } = HighlightType.Outline;
    public TooltipPosition TooltipPosition { get; set; } = TooltipPosition.Auto;
    public string? TriggerCondition { get; set; }
    public string? ActionButtonText { get; set; }
}

public class OnboardingProgress
{
    public string? CurrentStepId { get; set; }
    public int TotalSteps { get; set; }
    public int CompletedSteps { get; set; }
    public DateTime? StartedAt { get; set; }
    public DateTime? CompletedAt { get; set; }
}

public class OnboardingState
{
    public List<string> CompletedSteps { get; set; } = new();
    public List<string> SkippedFeatures { get; set; } = new();
    public OnboardingProgress Progress { get; set; } = new();
    public bool IsComplete { get; set; }
}

public class OnboardingStepEventArgs : EventArgs
{
    public OnboardingStep Step { get; }

    public OnboardingStepEventArgs(OnboardingStep step)
    {
        Step = step;
    }
}

public class TooltipEventArgs : EventArgs
{
    public string StepId { get; set; } = string.Empty;
    public string Title { get; set; } = string.Empty;
    public string Description { get; set; } = string.Empty;
    public string? TargetElement { get; set; }
    public HighlightType HighlightType { get; set; }
    public TooltipPosition Position { get; set; }
    public bool IsContextual { get; set; }
}

#endregion
