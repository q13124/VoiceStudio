using System;
using System.Collections.Generic;
using System.Linq;
using VoiceStudio.App.Helpers;

namespace VoiceStudio.App.Services
{
  /// <summary>
  /// Service to manage onboarding hints for first-time users.
  /// Uses file-based settings storage for unpackaged app compatibility.
  /// </summary>
  public class OnboardingService
  {
    private const string SettingsKey = "OnboardingHints";
    private const string FirstRunKey = "OnboardingFirstRun";

    private readonly HashSet<string> _dismissedHints = new();

    public OnboardingService()
    {
      LoadDismissedHints();
    }

    /// <summary>
    /// Check if a hint should be shown (not dismissed and first-time use).
    /// </summary>
    public bool ShouldShowHint(string hintId)
    {
      if (_dismissedHints.Contains(hintId))
        return false;

      // Check if this is first-time use
      if (!UnpackagedSettingsHelper.ContainsKey(FirstRunKey))
      {
        UnpackagedSettingsHelper.SetValue(FirstRunKey, false);
        return true; // First run
      }

      return !UnpackagedSettingsHelper.ContainsKey($"Hint_{hintId}_Dismissed");
    }

    /// <summary>
    /// Mark a hint as dismissed.
    /// </summary>
    public void DismissHint(string hintId, bool dontShowAgain = false)
    {
      _dismissedHints.Add(hintId);

      if (dontShowAgain)
      {
        UnpackagedSettingsHelper.SetValue($"Hint_{hintId}_Dismissed", true);
      }

      SaveDismissedHints();
    }

    /// <summary>
    /// Reset all dismissed hints (for testing).
    /// </summary>
    public void ResetHints()
    {
      _dismissedHints.Clear();
      // Note: Full key enumeration is not supported with UnpackagedSettingsHelper.
      // For a full reset, clear the appsettings.json file manually or extend the helper.
      SaveDismissedHints();
    }

    private void LoadDismissedHints()
    {
      var hintsString = UnpackagedSettingsHelper.GetValue<string>(SettingsKey, string.Empty);
      if (!string.IsNullOrEmpty(hintsString))
      {
        foreach (var hint in hintsString.Split(','))
        {
          if (!string.IsNullOrWhiteSpace(hint))
            _dismissedHints.Add(hint.Trim());
        }
      }
    }

    private void SaveDismissedHints()
    {
      UnpackagedSettingsHelper.SetValue(SettingsKey, string.Join(",", _dismissedHints));
    }
  }
}