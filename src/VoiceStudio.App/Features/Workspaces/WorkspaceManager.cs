// Phase 5.1: Workspace Management System
// Task 5.1.1-5.1.5: Multi-workspace support with persistence
//
// DEPRECATED (Phase 5.0): This class is deprecated.
// Use VoiceStudio.App.Services.PanelStateService which implements IUnifiedWorkspaceService.
// This file is kept for reference and will be removed in a future version.

using System;
using System.Collections.Generic;
using System.Collections.ObjectModel;
using System.IO;
using System.Linq;
using System.Text.Json;
using System.Threading.Tasks;

namespace VoiceStudio.App.Features.Workspaces;

/// <summary>
/// Represents a workspace configuration.
/// </summary>
public class Workspace
{
    public string Id { get; set; } = Guid.NewGuid().ToString();
    public string Name { get; set; } = "Default";
    public DateTime CreatedAt { get; set; } = DateTime.Now;
    public DateTime LastAccessedAt { get; set; } = DateTime.Now;
    
    // Layout configuration
    public Dictionary<string, PanelState> PanelStates { get; set; } = new();
    public WindowState MainWindowState { get; set; } = new();
    
    // View preferences
    public string ActiveView { get; set; } = "Synthesis";
    public List<string> OpenTabs { get; set; } = new();
    public Dictionary<string, object> ViewSettings { get; set; } = new();
    
    // Theme override (null = use system)
    public string? ThemeOverride { get; set; }
}

/// <summary>
/// Panel state within a workspace.
/// </summary>
public class PanelState
{
    public string PanelId { get; set; } = "";
    public bool IsVisible { get; set; } = true;
    public bool IsPinned { get; set; } = false;
    public double Width { get; set; }
    public double Height { get; set; }
    public int DockPosition { get; set; } // 0=Left, 1=Right, 2=Bottom, 3=Float
    public double FloatX { get; set; }
    public double FloatY { get; set; }
}

/// <summary>
/// Main window state.
/// </summary>
public class WindowState
{
    public double Width { get; set; } = 1400;
    public double Height { get; set; } = 900;
    public double Left { get; set; } = 100;
    public double Top { get; set; } = 100;
    public bool IsMaximized { get; set; } = false;
}

/// <summary>
/// Manages workspaces for the application.
/// </summary>
public class WorkspaceManager
{
    private readonly string _workspacesPath;
    private readonly ObservableCollection<Workspace> _workspaces = new();
    private Workspace? _activeWorkspace;

    public event EventHandler<Workspace>? WorkspaceChanged;
    public event EventHandler<Workspace>? WorkspaceSaved;

    public WorkspaceManager(string? basePath = null)
    {
        _workspacesPath = Path.Combine(
            basePath ?? Environment.GetFolderPath(Environment.SpecialFolder.LocalApplicationData),
            "VoiceStudio",
            "Workspaces"
        );
        
        Directory.CreateDirectory(_workspacesPath);
    }

    public IReadOnlyCollection<Workspace> Workspaces => _workspaces;
    
    public Workspace? ActiveWorkspace => _activeWorkspace;

    /// <summary>
    /// Load all workspaces from disk.
    /// </summary>
    public async Task LoadWorkspacesAsync()
    {
        _workspaces.Clear();
        
        foreach (var file in Directory.GetFiles(_workspacesPath, "*.json"))
        {
            try
            {
                var json = await File.ReadAllTextAsync(file);
                var workspace = JsonSerializer.Deserialize<Workspace>(json);
                
                if (workspace != null)
                {
                    _workspaces.Add(workspace);
                }
            }
            // ALLOWED: empty catch - skip invalid workspace files, continue loading others
            catch (Exception)
            {
            }
        }
        
        // Ensure at least one workspace exists
        if (_workspaces.Count == 0)
        {
            var defaultWorkspace = new Workspace { Name = "Default" };
            _workspaces.Add(defaultWorkspace);
            await SaveWorkspaceAsync(defaultWorkspace);
        }
    }

    /// <summary>
    /// Save a workspace to disk.
    /// </summary>
    public async Task SaveWorkspaceAsync(Workspace workspace)
    {
        var filePath = Path.Combine(_workspacesPath, $"{workspace.Id}.json");
        
        var options = new JsonSerializerOptions { WriteIndented = true };
        var json = JsonSerializer.Serialize(workspace, options);
        
        await File.WriteAllTextAsync(filePath, json);
        
        WorkspaceSaved?.Invoke(this, workspace);
    }

    /// <summary>
    /// Create a new workspace.
    /// </summary>
    public async Task<Workspace> CreateWorkspaceAsync(string name)
    {
        var workspace = new Workspace
        {
            Name = name,
            CreatedAt = DateTime.Now,
            LastAccessedAt = DateTime.Now,
        };
        
        _workspaces.Add(workspace);
        await SaveWorkspaceAsync(workspace);
        
        return workspace;
    }

    /// <summary>
    /// Delete a workspace.
    /// </summary>
    public async Task DeleteWorkspaceAsync(string workspaceId)
    {
        var workspace = _workspaces.FirstOrDefault(w => w.Id == workspaceId);
        
        if (workspace != null)
        {
            _workspaces.Remove(workspace);
            
            var filePath = Path.Combine(_workspacesPath, $"{workspaceId}.json");
            if (File.Exists(filePath))
            {
                File.Delete(filePath);
            }
        }
        
        await Task.CompletedTask;
    }

    /// <summary>
    /// Switch to a different workspace.
    /// </summary>
    public async Task SwitchWorkspaceAsync(string workspaceId)
    {
        // Save current workspace first
        if (_activeWorkspace != null)
        {
            await SaveWorkspaceAsync(_activeWorkspace);
        }
        
        var workspace = _workspaces.FirstOrDefault(w => w.Id == workspaceId);
        
        if (workspace != null)
        {
            workspace.LastAccessedAt = DateTime.Now;
            _activeWorkspace = workspace;
            
            WorkspaceChanged?.Invoke(this, workspace);
        }
    }

    /// <summary>
    /// Duplicate a workspace.
    /// </summary>
    public async Task<Workspace> DuplicateWorkspaceAsync(string workspaceId, string newName)
    {
        var source = _workspaces.FirstOrDefault(w => w.Id == workspaceId);
        
        if (source == null)
        {
            throw new ArgumentException($"Workspace not found: {workspaceId}");
        }
        
        // Deep copy by serialization
        var json = JsonSerializer.Serialize(source);
        var duplicate = JsonSerializer.Deserialize<Workspace>(json)!;
        
        duplicate.Id = Guid.NewGuid().ToString();
        duplicate.Name = newName;
        duplicate.CreatedAt = DateTime.Now;
        duplicate.LastAccessedAt = DateTime.Now;
        
        _workspaces.Add(duplicate);
        await SaveWorkspaceAsync(duplicate);
        
        return duplicate;
    }

    /// <summary>
    /// Update panel state in active workspace.
    /// </summary>
    public void UpdatePanelState(string panelId, PanelState state)
    {
        if (_activeWorkspace != null)
        {
            _activeWorkspace.PanelStates[panelId] = state;
        }
    }

    /// <summary>
    /// Get panel state from active workspace.
    /// </summary>
    public PanelState? GetPanelState(string panelId)
    {
        return _activeWorkspace?.PanelStates.GetValueOrDefault(panelId);
    }

    /// <summary>
    /// Save active workspace.
    /// </summary>
    public async Task SaveActiveWorkspaceAsync()
    {
        if (_activeWorkspace != null)
        {
            await SaveWorkspaceAsync(_activeWorkspace);
        }
    }
}
