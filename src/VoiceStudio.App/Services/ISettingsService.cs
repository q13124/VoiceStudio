using System.Threading;
using System.Threading.Tasks;
using VoiceStudio.Core.Models;

namespace VoiceStudio.App.Services
{
  /// <summary>
  /// Interface for managing application settings.
  /// </summary>
  public interface ISettingsService
  {
    /// <summary>
    /// Loads all settings from backend or local storage.
    /// </summary>
    Task<SettingsData> LoadSettingsAsync(CancellationToken cancellationToken = default);

    /// <summary>
    /// Loads settings for a specific category.
    /// </summary>
    Task<T?> LoadCategoryAsync<T>(string category, CancellationToken cancellationToken = default) where T : class;

    /// <summary>
    /// Saves all settings to backend and local storage.
    /// </summary>
    Task SaveSettingsAsync(SettingsData settings, CancellationToken cancellationToken = default);

    /// <summary>
    /// Updates settings for a specific category.
    /// </summary>
    Task<T> UpdateCategoryAsync<T>(string category, T categorySettings, CancellationToken cancellationToken = default) where T : class;

    /// <summary>
    /// Resets all settings to defaults.
    /// </summary>
    Task<SettingsData> ResetSettingsAsync(CancellationToken cancellationToken = default);

    /// <summary>
    /// Validates settings data.
    /// </summary>
    bool ValidateSettings(SettingsData settings, out string? errorMessage);

    /// <summary>
    /// Gets default settings.
    /// </summary>
    SettingsData GetDefaultSettings();
  }
}