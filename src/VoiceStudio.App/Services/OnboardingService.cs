using System;
using System.Collections.Generic;
using System.Linq;
using Windows.Storage;
using Microsoft.UI.Xaml;

namespace VoiceStudio.App.Services
{
  /// <summary>
  /// Service to manage onboarding hints for first-time users.
  /// </summary>
  public class OnboardingService
  {
    private static readonly string SettingsKey = "OnboardingHints";
    private static readonly ApplicationDataContainer _localSettings = ApplicationData.Current.LocalSettings;

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
      const string firstRunKey = "FirstRun";
      if (!_localSettings.Values.ContainsKey(firstRunKey))
      {
        _localSettings.Values[firstRunKey] = false;
        return true; // First run
      }

      return !_localSettings.Values.ContainsKey($"Hint_{hintId}_Dismissed");
    }

    /// <summary>
    /// Mark a hint as dismissed.
    /// </summary>
    public void DismissHint(string hintId, bool dontShowAgain = false)
    {
      _dismissedHints.Add(hintId);

      if (dontShowAgain)
      {
        _localSettings.Values[$"Hint_{hintId}_Dismissed"] = true;
      }

      SaveDismissedHints();
    }

    /// <summary>
    /// Reset all dismissed hints (for testing).
    /// </summary>
    public void ResetHints()
    {
      _dismissedHints.Clear();
      foreach (var key in (List<string>)_localSettings.Values.Keys.Where(k => k.StartsWith("Hint_")).ToList())
      {
        _localSettings.Values.Remove(key);
      }
      SaveDismissedHints();
    }

    private void LoadDismissedHints()
    {
      if (_localSettings.Values.ContainsKey(SettingsKey))
      {
        var hintsString = _localSettings.Values[SettingsKey] as string;
        if (!string.IsNullOrEmpty(hintsString))
        {
          foreach (var hint in hintsString.Split(','))
          {
            if (!string.IsNullOrWhiteSpace(hint))
              _dismissedHints.Add(hint.Trim());
          }
        }
      }
    }

    private void SaveDismissedHints()
    {
      _localSettings.Values[SettingsKey] = string.Join(",", _dismissedHints);
    }
  }
}