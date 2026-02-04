using System;
using System.Collections.Generic;
using System.IO;
using System.Text.Json;
using System.Threading.Tasks;
using VoiceStudio.App.Logging;

namespace VoiceStudio.App.Services
{
  /// <summary>
  /// Service for persisting application state before critical operations.
  /// </summary>
  public class StatePersistenceService
  {
    private readonly string _stateDirectory;
    private readonly JsonSerializerOptions _jsonOptions;

    public StatePersistenceService()
    {
      var appDataPath = Environment.GetFolderPath(Environment.SpecialFolder.LocalApplicationData);
      _stateDirectory = Path.Combine(appDataPath, "VoiceStudio", "StateBackups");
      Directory.CreateDirectory(_stateDirectory);

      _jsonOptions = new JsonSerializerOptions
      {
        WriteIndented = true,
        PropertyNamingPolicy = JsonNamingPolicy.CamelCase
      };
    }

    /// <summary>
    /// Saves state before a critical operation.
    /// </summary>
    public async Task<string> SaveStateAsync<T>(string operationId, T state) where T : class
    {
      try
      {
        var timestamp = DateTime.UtcNow.ToString("yyyyMMdd_HHmmss");
        var fileName = $"{operationId}_{timestamp}.json";
        var filePath = Path.Combine(_stateDirectory, fileName);

        var json = JsonSerializer.Serialize(state, _jsonOptions);
        await File.WriteAllTextAsync(filePath, json);

        return filePath;
      }
      catch
      {
        // Silently fail - don't break application if state saving fails
        return string.Empty;
      }
    }

    /// <summary>
    /// Restores state from a saved file.
    /// </summary>
    public async Task<T?> RestoreStateAsync<T>(string filePath) where T : class
    {
      try
      {
        if (!File.Exists(filePath))
          return null;

        var json = await File.ReadAllTextAsync(filePath);
        return JsonSerializer.Deserialize<T>(json, _jsonOptions);
      }
      catch
      {
        return null;
      }
    }

    /// <summary>
    /// Gets the most recent state backup for an operation.
    /// </summary>
    public string? GetLatestStateFile(string operationId)
    {
      try
      {
        var pattern = $"{operationId}_*.json";
        var files = Directory.GetFiles(_stateDirectory, pattern);

        if (files.Length == 0)
          return null;

        // Return the most recent file
        Array.Sort(files);
        return files[files.Length - 1];
      }
      catch
      {
        return null;
      }
    }

    /// <summary>
    /// Cleans up old state backups (keeps only the most recent N backups per operation).
    /// </summary>
    public void CleanupOldBackups(int keepCount = 5)
    {
      try
      {
        var operationGroups = new Dictionary<string, List<string>>();

        foreach (var file in Directory.GetFiles(_stateDirectory, "*.json"))
        {
          var fileName = Path.GetFileName(file);
          var parts = fileName.Split('_');
          if (parts.Length >= 2)
          {
            var operationId = parts[0];
            if (!operationGroups.ContainsKey(operationId))
              operationGroups[operationId] = new List<string>();
            operationGroups[operationId].Add(file);
          }
        }

        foreach (var group in operationGroups.Values)
        {
          if (group.Count > keepCount)
          {
            group.Sort();
            var toDelete = group.Count - keepCount;
            for (int i = 0; i < toDelete; i++)
            {
              try
              {
                File.Delete(group[i]);
              }
              catch (Exception ex)
      {
        ErrorLogger.LogWarning($"Best effort operation failed: {ex.Message}", "StatePersistenceService.CleanupOldBackups");
      }
            }
          }
        }
      }
      catch (Exception ex)
      {
        ErrorLogger.LogWarning($"Best effort operation failed: {ex.Message}", "StatePersistenceService.CleanupOldBackups");
      }
    }
  }
}