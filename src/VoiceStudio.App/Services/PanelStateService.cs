using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using System.Text.Json;
using System.Threading.Tasks;
using VoiceStudio.Core.Models;
using VoiceStudio.Core.Panels;
using VoiceStudio.Core.Services;
using VoiceStudio.App.Logging;

namespace VoiceStudio.App.Services
{
  /// <summary>
  /// Service for managing panel state persistence and workspace profiles.
  /// Implements IDEA 3: Panel State Persistence with Workspace Profiles.
  /// Phase 5.0: Now implements IUnifiedWorkspaceService for service unification.
  /// </summary>
  public class PanelStateService : IUnifiedWorkspaceService
  {
    // Built-in workspace templates
    private static readonly List<WorkspaceTemplate> _builtInTemplates = new()
    {
      new WorkspaceTemplate
      {
        Id = "recording",
        Name = "Recording Studio",
        Description = "Optimized for voice recording with waveform and input monitoring",
        Category = "Production",
        Layout = new WorkspaceLayout { ProfileName = "Recording", Version = "1.0" }
      },
      new WorkspaceTemplate
      {
        Id = "mixing",
        Name = "Mixing Console",
        Description = "Audio mixing with effects chain and analyzer panels",
        Category = "Production",
        Layout = new WorkspaceLayout { ProfileName = "Mixing", Version = "1.0" }
      },
      new WorkspaceTemplate
      {
        Id = "synthesis",
        Name = "Voice Synthesis",
        Description = "Text-to-speech synthesis with profile management",
        Category = "Synthesis",
        Layout = new WorkspaceLayout { ProfileName = "Synthesis", Version = "1.0" }
      },
      new WorkspaceTemplate
      {
        Id = "analysis",
        Name = "Audio Analysis",
        Description = "Detailed audio analysis with spectrogram and quality metrics",
        Category = "Analysis",
        Layout = new WorkspaceLayout { ProfileName = "Analysis", Version = "1.0" }
      },
      new WorkspaceTemplate
      {
        Id = "training",
        Name = "Model Training",
        Description = "Voice model training with dataset and progress panels",
        Category = "Training",
        Layout = new WorkspaceLayout { ProfileName = "Training", Version = "1.0" }
      }
    };

    private readonly ISettingsService _settingsService;
    private readonly string _workspaceProfilesDirectory;
    private readonly string _projectStatesDirectory;
    private readonly JsonSerializerOptions _jsonOptions;
    private WorkspaceLayout? _currentLayout;
    private string _currentWorkspaceProfile = "Default";
    private bool _disposed;

    public PanelStateService(ISettingsService settingsService)
    {
      _settingsService = settingsService ?? throw new ArgumentNullException(nameof(settingsService));

      // Set up directories
      var appDataPath = Environment.GetFolderPath(Environment.SpecialFolder.LocalApplicationData);
      _workspaceProfilesDirectory = Path.Combine(appDataPath, "VoiceStudio", "WorkspaceProfiles");
      _projectStatesDirectory = Path.Combine(appDataPath, "VoiceStudio", "ProjectStates");
      Directory.CreateDirectory(_workspaceProfilesDirectory);
      Directory.CreateDirectory(_projectStatesDirectory);

      _jsonOptions = new JsonSerializerOptions
      {
        WriteIndented = true,
        PropertyNamingPolicy = JsonNamingPolicy.CamelCase
      };

      // Load current workspace layout from settings (fire-and-forget with error handling)
      _ = LoadCurrentWorkspaceAsync();
    }

    /// <summary>
    /// Gets the current workspace layout.
    /// </summary>
    public WorkspaceLayout GetCurrentLayout()
    {
      if (_currentLayout == null)
      {
        _currentLayout = new WorkspaceLayout
        {
          ProfileName = _currentWorkspaceProfile,
          Version = "1.0",
          IsDefault = _currentWorkspaceProfile == "Default"
        };
      }
      return _currentLayout;
    }

    /// <summary>
    /// Gets the current workspace profile name.
    /// </summary>
    public string CurrentWorkspaceProfile => _currentWorkspaceProfile;

    /// <summary>
    /// Saves panel state for a specific region.
    /// </summary>
    public void SaveRegionState(PanelRegion region, string activePanelId, List<string> openedPanels)
    {
      var layout = GetCurrentLayout();
      var regionState = layout.Regions.FirstOrDefault(r => r.Region == region);

      if (regionState == null)
      {
        regionState = new RegionState
        {
          Region = region,
          ActivePanelId = activePanelId,
          OpenedPanels = openedPanels ?? new List<string>()
        };
        layout.Regions.Add(regionState);
      }
      else
      {
        regionState.ActivePanelId = activePanelId;
        regionState.OpenedPanels = openedPanels ?? new List<string>();
      }

      layout.ModifiedAt = DateTime.UtcNow;
      SaveCurrentWorkspace();
    }

    /// <summary>
    /// Saves panel-specific state (scroll position, selected items, etc.).
    /// </summary>
    public void SavePanelState(PanelRegion region, string panelId, PanelState state)
    {
      var layout = GetCurrentLayout();
      var regionState = layout.Regions.FirstOrDefault(r => r.Region == region);

      if (regionState == null)
      {
        regionState = new RegionState
        {
          Region = region,
          ActivePanelId = panelId
        };
        layout.Regions.Add(regionState);
      }

      state.PanelId = panelId;
      regionState.PanelStates[panelId] = state;
      layout.ModifiedAt = DateTime.UtcNow;
      SaveCurrentWorkspace();
    }

    /// <summary>
    /// Gets panel state for a specific panel.
    /// </summary>
    public PanelState? GetPanelState(PanelRegion region, string panelId)
    {
      var layout = GetCurrentLayout();
      var regionState = layout.Regions.FirstOrDefault(r => r.Region == region);
      return regionState?.PanelStates.GetValueOrDefault(panelId);
    }

    /// <summary>
    /// Gets region state for a specific region.
    /// </summary>
    public RegionState? GetRegionState(PanelRegion region)
    {
      var layout = GetCurrentLayout();
      return layout.Regions.FirstOrDefault(r => r.Region == region);
    }

    /// <summary>
    /// Saves panel state for a specific project.
    /// </summary>
    public async Task SaveProjectStateAsync(string projectId, WorkspaceLayout layout)
    {
      try
      {
        var filePath = Path.Combine(_projectStatesDirectory, $"{projectId}.json");
        var json = JsonSerializer.Serialize(layout, _jsonOptions);
        await File.WriteAllTextAsync(filePath, json);
      }
      catch (Exception ex)
      {
        // Log error but don't throw - state saving shouldn't break the app
        System.Diagnostics.Debug.WriteLine($"Failed to save project state: {ex.Message}");
      }
    }

    /// <summary>
    /// Loads panel state for a specific project.
    /// </summary>
    public async Task<WorkspaceLayout?> LoadProjectStateAsync(string projectId)
    {
      try
      {
        var filePath = Path.Combine(_projectStatesDirectory, $"{projectId}.json");
        if (!File.Exists(filePath))
          return null;

        var json = await File.ReadAllTextAsync(filePath);
        return JsonSerializer.Deserialize<WorkspaceLayout>(json, _jsonOptions);
      }
      catch (Exception ex)
      {
        System.Diagnostics.Debug.WriteLine($"Failed to load project state: {ex.Message}");
        return null;
      }
    }

    /// <summary>
    /// Saves a workspace profile.
    /// </summary>
    public async Task SaveWorkspaceProfileAsync(WorkspaceProfile profile)
    {
      try
      {
        var filePath = Path.Combine(_workspaceProfilesDirectory, $"{profile.Name}.json");
        profile.ModifiedAt = DateTime.UtcNow;
        var json = JsonSerializer.Serialize(profile, _jsonOptions);
        await File.WriteAllTextAsync(filePath, json);
      }
      catch (Exception ex)
      {
        System.Diagnostics.Debug.WriteLine($"Failed to save workspace profile: {ex.Message}");
      }
    }

    /// <summary>
    /// Loads a workspace profile by name.
    /// </summary>
    public async Task<WorkspaceProfile?> LoadWorkspaceProfileAsync(string profileName)
    {
      try
      {
        var filePath = Path.Combine(_workspaceProfilesDirectory, $"{profileName}.json");
        if (!File.Exists(filePath))
          return null;

        var json = await File.ReadAllTextAsync(filePath);
        return JsonSerializer.Deserialize<WorkspaceProfile>(json, _jsonOptions);
      }
      catch (Exception ex)
      {
        System.Diagnostics.Debug.WriteLine($"Failed to load workspace profile: {ex.Message}");
        return null;
      }
    }

    /// <summary>
    /// Lists all available workspace profiles.
    /// </summary>
    public async Task<List<WorkspaceProfile>> ListWorkspaceProfilesAsync()
    {
      var profiles = new List<WorkspaceProfile>();

      try
      {
        if (!Directory.Exists(_workspaceProfilesDirectory))
          return profiles;

        foreach (var file in Directory.GetFiles(_workspaceProfilesDirectory, "*.json"))
        {
          try
          {
            var json = await File.ReadAllTextAsync(file);
            var profile = JsonSerializer.Deserialize<WorkspaceProfile>(json, _jsonOptions);
            if (profile != null)
              profiles.Add(profile);
          }
          catch (Exception ex)
      {
        ErrorLogger.LogWarning($"Best effort operation failed: {ex.Message}", "PanelStateService.Task");
      }
        }
      }
      catch (Exception ex)
      {
        System.Diagnostics.Debug.WriteLine($"Failed to list workspace profiles: {ex.Message}");
      }

      // Ensure Default profile exists
      if (!profiles.Any(p => p.Name == "Default"))
      {
        var defaultProfile = new WorkspaceProfile
        {
          Name = "Default",
          Description = "Default workspace layout",
          Layout = new WorkspaceLayout
          {
            ProfileName = "Default",
            IsDefault = true
          },
          CreatedAt = DateTime.UtcNow,
          ModifiedAt = DateTime.UtcNow
        };
        profiles.Insert(0, defaultProfile);
        await SaveWorkspaceProfileAsync(defaultProfile);
      }

      return profiles.OrderBy(p => p.Name).ToList();
    }

    /// <summary>
    /// Deletes a workspace profile.
    /// </summary>
    public Task<bool> DeleteWorkspaceProfileAsync(string profileName)
    {
      if (profileName == "Default")
        return Task.FromResult(false); // Cannot delete default profile

      try
      {
        var filePath = Path.Combine(_workspaceProfilesDirectory, $"{profileName}.json");
        if (File.Exists(filePath))
        {
          File.Delete(filePath);
          return Task.FromResult(true);
        }
      }
      catch (Exception ex)
      {
        System.Diagnostics.Debug.WriteLine($"Failed to delete workspace profile: {ex.Message}");
      }

      return Task.FromResult(false);
    }

    /// <summary>
    /// Switches to a different workspace profile.
    /// </summary>
    public async Task<bool> SwitchWorkspaceProfileAsync(string profileName)
    {
      try
      {
        // Save current layout before switching
        SaveCurrentWorkspace();

        // Load new profile
        var profile = await LoadWorkspaceProfileAsync(profileName);
        if (profile == null)
        {
          // Create new profile if it doesn't exist
          profile = new WorkspaceProfile
          {
            Name = profileName,
            Layout = new WorkspaceLayout
            {
              ProfileName = profileName,
              Version = "1.0"
            },
            CreatedAt = DateTime.UtcNow,
            ModifiedAt = DateTime.UtcNow
          };
          await SaveWorkspaceProfileAsync(profile);
        }

        _currentWorkspaceProfile = profileName;
        _currentLayout = profile.Layout;

        // Save to settings
        await SaveCurrentWorkspaceAsync();

        WorkspaceProfileChanged?.Invoke(this, new WorkspaceProfileChangedEventArgs
        {
          ProfileName = profileName,
          Layout = profile.Layout
        });

        return true;
      }
      catch (Exception ex)
      {
        System.Diagnostics.Debug.WriteLine($"Failed to switch workspace profile: {ex.Message}");
        return false;
      }
    }

    /// <summary>
    /// Saves current workspace layout to settings.
    /// </summary>
    private void SaveCurrentWorkspace()
    {
      try
      {
        // IMPORTANT: Do NOT block the UI thread here.
        // This method is called from UI panel switching (PanelHost.OnContentChanged).
        // Sync-over-async can deadlock or stall the UI thread (especially when the backend is unavailable),
        // which breaks Gate C UI smoke and can freeze the app in production.
        _ = Task.Run(async () => await SaveCurrentWorkspaceAsync().ConfigureAwait(false));
      }
      catch (Exception ex)
      {
        System.Diagnostics.Debug.WriteLine($"Failed to save workspace to settings: {ex.Message}");
      }
    }

    /// <summary>
    /// Saves current workspace layout to settings asynchronously.
    /// </summary>
    private async Task SaveCurrentWorkspaceAsync()
    {
      try
      {
        var layout = GetCurrentLayout();
        var settingsData = await _settingsService.LoadSettingsAsync();
        settingsData.WorkspaceLayout = layout;
        await _settingsService.SaveSettingsAsync(settingsData);
      }
      catch (Exception ex)
      {
        System.Diagnostics.Debug.WriteLine($"Failed to save workspace to settings: {ex.Message}");
      }
    }

    /// <summary>
    /// Loads current workspace layout from settings.
    /// </summary>
    private async Task LoadCurrentWorkspaceAsync()
    {
      try
      {
        var settingsData = await _settingsService.LoadSettingsAsync();
        if (settingsData?.WorkspaceLayout != null)
        {
          _currentLayout = settingsData.WorkspaceLayout;
          _currentWorkspaceProfile = _currentLayout.ProfileName;
        }
      }
      catch (Exception ex)
      {
        // Use default if loading fails, but log the error
        System.Diagnostics.Debug.WriteLine($"[PanelStateService] Failed to load workspace: {ex.Message}");
        _currentLayout = new WorkspaceLayout
        {
          ProfileName = "Default",
          Version = "1.0",
          IsDefault = true
        };
      }
    }

    /// <summary>
    /// Event raised when workspace profile changes.
    /// </summary>
    public event EventHandler<WorkspaceProfileChangedEventArgs>? WorkspaceProfileChanged;

    #region IUnifiedWorkspaceService Implementation

    /// <summary>
    /// Creates a new workspace profile from the current layout.
    /// </summary>
    public async Task<WorkspaceProfile> CreateWorkspaceProfileAsync(string name, string? description = null)
    {
      var profile = new WorkspaceProfile
      {
        Name = name,
        Description = description ?? $"Custom workspace: {name}",
        Layout = GetCurrentLayout(),
        CreatedAt = DateTime.UtcNow,
        ModifiedAt = DateTime.UtcNow
      };
      
      await SaveWorkspaceProfileAsync(profile);
      return profile;
    }

    /// <summary>
    /// Duplicates an existing workspace profile.
    /// </summary>
    public async Task<WorkspaceProfile?> DuplicateWorkspaceProfileAsync(string sourceName, string newName)
    {
      var source = await LoadWorkspaceProfileAsync(sourceName);
      if (source == null) return null;

      var duplicate = new WorkspaceProfile
      {
        Name = newName,
        Description = $"Copy of {sourceName}",
        Layout = source.Layout,
        CreatedAt = DateTime.UtcNow,
        ModifiedAt = DateTime.UtcNow
      };

      await SaveWorkspaceProfileAsync(duplicate);
      return duplicate;
    }

    /// <summary>
    /// Gets built-in workspace templates.
    /// </summary>
    public IReadOnlyList<WorkspaceTemplate> GetBuiltInTemplates() => _builtInTemplates;

    /// <summary>
    /// Applies a workspace template.
    /// </summary>
    public async Task ApplyTemplateAsync(string templateId)
    {
      var template = _builtInTemplates.FirstOrDefault(t => t.Id == templateId);
      if (template == null) return;

      // Create a profile from the template if it doesn't exist
      var existingProfile = await LoadWorkspaceProfileAsync(template.Name);
      if (existingProfile == null)
      {
        var profile = new WorkspaceProfile
        {
          Name = template.Name,
          Description = template.Description,
          Layout = template.Layout,
          CreatedAt = DateTime.UtcNow,
          ModifiedAt = DateTime.UtcNow
        };
        await SaveWorkspaceProfileAsync(profile);
      }

      await SwitchWorkspaceProfileAsync(template.Name);
    }

    /// <summary>
    /// Exports a workspace profile to JSON.
    /// </summary>
    public async Task<string> ExportWorkspaceAsync(string profileName)
    {
      var profile = await LoadWorkspaceProfileAsync(profileName);
      if (profile == null) return "{}";

      return JsonSerializer.Serialize(profile, _jsonOptions);
    }

    /// <summary>
    /// Imports a workspace profile from JSON.
    /// </summary>
    public async Task<WorkspaceProfile?> ImportWorkspaceAsync(string json)
    {
      try
      {
        var profile = JsonSerializer.Deserialize<WorkspaceProfile>(json, _jsonOptions);
        if (profile == null) return null;

        // Ensure unique name
        var existing = await LoadWorkspaceProfileAsync(profile.Name);
        if (existing != null)
        {
          profile.Name = $"{profile.Name} (Imported)";
        }

        profile.ModifiedAt = DateTime.UtcNow;
        await SaveWorkspaceProfileAsync(profile);
        return profile;
      }
      catch (Exception ex)
      {
        System.Diagnostics.Debug.WriteLine($"Failed to import workspace: {ex.Message}");
        return null;
      }
    }

    #endregion

    public void Dispose()
    {
      if (!_disposed)
      {
        // Save current workspace before disposing
        SaveCurrentWorkspace();
        _disposed = true;
      }
    }
  }

  /// <summary>
  /// Event args for workspace profile changes.
  /// </summary>
  public class WorkspaceProfileChangedEventArgs : EventArgs
  {
    public string ProfileName { get; set; } = string.Empty;
    public WorkspaceLayout Layout { get; set; } = null!;
  }
}