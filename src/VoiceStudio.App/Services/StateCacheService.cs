using System;
using System.Collections.Generic;
using System.IO;
using System.Text.Json;
using System.Threading.Tasks;

namespace VoiceStudio.App.Services
{
  /// <summary>
  /// Service for caching last known backend state when offline.
  /// </summary>
  public class StateCacheService
  {
    private readonly string _cacheDirectory;
    private readonly Dictionary<string, object> _memoryCache = new();
    private readonly JsonSerializerOptions _jsonOptions;

    public StateCacheService()
    {
      var appDataPath = Environment.GetFolderPath(Environment.SpecialFolder.LocalApplicationData);
      _cacheDirectory = Path.Combine(appDataPath, "VoiceStudio", "StateCache");
      Directory.CreateDirectory(_cacheDirectory);

      _jsonOptions = new JsonSerializerOptions
      {
        WriteIndented = true,
        PropertyNamingPolicy = JsonNamingPolicy.CamelCase
      };
    }

    /// <summary>
    /// Caches state for a specific key.
    /// </summary>
    public async Task CacheStateAsync<T>(string key, T state) where T : class
    {
      try
      {
        // Store in memory
        _memoryCache[key] = state;

        // Persist to disk
        var filePath = Path.Combine(_cacheDirectory, $"{key}.json");
        var json = JsonSerializer.Serialize(state, _jsonOptions);
        await File.WriteAllTextAsync(filePath, json);
      }
      catch
      {
        // Silently fail
      }
    }

    /// <summary>
    /// Gets cached state for a specific key.
    /// </summary>
    public async Task<T?> GetCachedStateAsync<T>(string key) where T : class
    {
      try
      {
        // Try memory cache first
        if (_memoryCache.TryGetValue(key, out var cached) && cached is T typedCached)
        {
          return typedCached;
        }

        // Try disk cache
        var filePath = Path.Combine(_cacheDirectory, $"{key}.json");
        if (File.Exists(filePath))
        {
          var json = await File.ReadAllTextAsync(filePath);
          var state = JsonSerializer.Deserialize<T>(json, _jsonOptions);

          if (state != null)
          {
            // Update memory cache
            _memoryCache[key] = state;
            return state;
          }
        }
      }
      catch
      {
        // Silently fail
      }

      return null;
    }

    /// <summary>
    /// Clears cached state for a specific key.
    /// </summary>
    public void ClearCachedState(string key)
    {
      try
      {
        _memoryCache.Remove(key);

        var filePath = Path.Combine(_cacheDirectory, $"{key}.json");
        if (File.Exists(filePath))
        {
          File.Delete(filePath);
        }
      }
      catch
      {
        // Silently fail
      }
    }

    /// <summary>
    /// Clears all cached state.
    /// </summary>
    public void ClearAllCachedState()
    {
      try
      {
        _memoryCache.Clear();

        foreach (var file in Directory.GetFiles(_cacheDirectory, "*.json"))
        {
          try
          {
            File.Delete(file);
          }
          catch
          {
            // Ignore individual file deletion errors
          }
        }
      }
      catch
      {
        // Silently fail
      }
    }

    /// <summary>
    /// Gets all cached state keys.
    /// </summary>
    public IEnumerable<string> GetCachedKeys()
    {
      try
      {
        var keys = new HashSet<string>(_memoryCache.Keys);

        foreach (var file in Directory.GetFiles(_cacheDirectory, "*.json"))
        {
          var fileName = Path.GetFileNameWithoutExtension(file);
          keys.Add(fileName);
        }

        return keys;
      }
      catch
      {
        return Array.Empty<string>();
      }
    }
  }
}