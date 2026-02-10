// Phase 5: Panel Management System
// Task 5.10: Dockable and resizable panels

using System;
using System.Collections.Generic;
using System.Collections.ObjectModel;
using System.Linq;
using Microsoft.UI.Xaml;
using Microsoft.UI.Xaml.Controls;

namespace VoiceStudio.App.Features.Panels;

/// <summary>
/// Panel dock positions.
/// </summary>
public enum PanelDockPosition
{
    Left,
    Right,
    Top,
    Bottom,
    Center,
    Float,
}

/// <summary>
/// Panel visibility state.
/// </summary>
public enum PanelVisibility
{
    Visible,
    Hidden,
    Collapsed,
    AutoHide,
}

/// <summary>
/// Panel definition.
/// </summary>
public class PanelDefinition
{
    public string Id { get; set; } = "";
    public string Title { get; set; } = "";
    public string IconGlyph { get; set; } = "";
    public PanelDockPosition DefaultPosition { get; set; } = PanelDockPosition.Left;
    public double DefaultWidth { get; set; } = 300;
    public double DefaultHeight { get; set; } = 400;
    public double MinWidth { get; set; } = 200;
    public double MinHeight { get; set; } = 100;
    public bool CanClose { get; set; } = true;
    public bool CanFloat { get; set; } = true;
    public bool CanDock { get; set; } = true;
    public Type? ContentType { get; set; }
}

/// <summary>
/// Panel instance state.
/// </summary>
public class PanelState
{
    public string PanelId { get; set; } = "";
    public PanelDockPosition Position { get; set; }
    public PanelVisibility Visibility { get; set; } = PanelVisibility.Visible;
    public double Width { get; set; }
    public double Height { get; set; }
    public double X { get; set; }
    public double Y { get; set; }
    public int Order { get; set; }
    public bool IsActive { get; set; }
}

/// <summary>
/// Manages application panels.
/// </summary>
public class PanelManager
{
    private readonly Dictionary<string, PanelDefinition> _definitions = new();
    private readonly Dictionary<string, PanelState> _states = new();
    private readonly ObservableCollection<PanelState> _leftPanels = new();
    private readonly ObservableCollection<PanelState> _rightPanels = new();
    private readonly ObservableCollection<PanelState> _topPanels = new();
    private readonly ObservableCollection<PanelState> _bottomPanels = new();
    private readonly ObservableCollection<PanelState> _centerPanels = new();
    private readonly ObservableCollection<PanelState> _floatingPanels = new();
    private string? _activePanel;

    public event EventHandler<string>? PanelActivated;
    public event EventHandler<string>? PanelClosed;
    public event EventHandler<string>? PanelVisibilityChanged;
    public event EventHandler? LayoutChanged;

    public IReadOnlyCollection<PanelState> LeftPanels => _leftPanels;
    public IReadOnlyCollection<PanelState> RightPanels => _rightPanels;
    public IReadOnlyCollection<PanelState> TopPanels => _topPanels;
    public IReadOnlyCollection<PanelState> BottomPanels => _bottomPanels;
    public IReadOnlyCollection<PanelState> CenterPanels => _centerPanels;
    public IReadOnlyCollection<PanelState> FloatingPanels => _floatingPanels;
    public string? ActivePanelId => _activePanel;

    /// <summary>
    /// Register a panel definition.
    /// </summary>
    public void RegisterPanel(PanelDefinition definition)
    {
        _definitions[definition.Id] = definition;
        
        // Create initial state
        var state = new PanelState
        {
            PanelId = definition.Id,
            Position = definition.DefaultPosition,
            Width = definition.DefaultWidth,
            Height = definition.DefaultHeight,
        };
        
        _states[definition.Id] = state;
        AddToDockGroup(state);
    }

    /// <summary>
    /// Get a panel definition.
    /// </summary>
    public PanelDefinition? GetDefinition(string panelId)
    {
        return _definitions.TryGetValue(panelId, out var def) ? def : null;
    }

    /// <summary>
    /// Get a panel state.
    /// </summary>
    public PanelState? GetState(string panelId)
    {
        return _states.TryGetValue(panelId, out var state) ? state : null;
    }

    /// <summary>
    /// Show a panel.
    /// </summary>
    public void ShowPanel(string panelId)
    {
        if (_states.TryGetValue(panelId, out var state))
        {
            state.Visibility = PanelVisibility.Visible;
            PanelVisibilityChanged?.Invoke(this, panelId);
        }
    }

    /// <summary>
    /// Hide a panel.
    /// </summary>
    public void HidePanel(string panelId)
    {
        if (_states.TryGetValue(panelId, out var state))
        {
            state.Visibility = PanelVisibility.Hidden;
            PanelVisibilityChanged?.Invoke(this, panelId);
        }
    }

    /// <summary>
    /// Toggle a panel's visibility.
    /// </summary>
    public void TogglePanel(string panelId)
    {
        if (_states.TryGetValue(panelId, out var state))
        {
            state.Visibility = state.Visibility == PanelVisibility.Visible
                ? PanelVisibility.Hidden
                : PanelVisibility.Visible;
            
            PanelVisibilityChanged?.Invoke(this, panelId);
        }
    }

    /// <summary>
    /// Activate a panel.
    /// </summary>
    public void ActivatePanel(string panelId)
    {
        if (_states.TryGetValue(panelId, out var state))
        {
            // Deactivate current
            if (_activePanel != null && _states.TryGetValue(_activePanel, out var current))
            {
                current.IsActive = false;
            }
            
            state.IsActive = true;
            state.Visibility = PanelVisibility.Visible;
            _activePanel = panelId;
            
            PanelActivated?.Invoke(this, panelId);
        }
    }

    /// <summary>
    /// Close a panel.
    /// </summary>
    public void ClosePanel(string panelId)
    {
        if (_definitions.TryGetValue(panelId, out var def) && def.CanClose)
        {
            if (_states.TryGetValue(panelId, out var state))
            {
                state.Visibility = PanelVisibility.Collapsed;
                RemoveFromDockGroup(state);
                PanelClosed?.Invoke(this, panelId);
            }
        }
    }

    /// <summary>
    /// Dock a panel to a position.
    /// </summary>
    public void DockPanel(string panelId, PanelDockPosition position)
    {
        if (!_definitions.TryGetValue(panelId, out var def) || !def.CanDock)
        {
            return;
        }
        
        if (_states.TryGetValue(panelId, out var state))
        {
            RemoveFromDockGroup(state);
            state.Position = position;
            AddToDockGroup(state);
            
            LayoutChanged?.Invoke(this, EventArgs.Empty);
        }
    }

    /// <summary>
    /// Float a panel.
    /// </summary>
    public void FloatPanel(string panelId, double x, double y)
    {
        if (!_definitions.TryGetValue(panelId, out var def) || !def.CanFloat)
        {
            return;
        }
        
        if (_states.TryGetValue(panelId, out var state))
        {
            RemoveFromDockGroup(state);
            state.Position = PanelDockPosition.Float;
            state.X = x;
            state.Y = y;
            AddToDockGroup(state);
            
            LayoutChanged?.Invoke(this, EventArgs.Empty);
        }
    }

    /// <summary>
    /// Resize a panel.
    /// </summary>
    public void ResizePanel(string panelId, double width, double height)
    {
        if (_states.TryGetValue(panelId, out var state))
        {
            if (_definitions.TryGetValue(panelId, out var def))
            {
                state.Width = Math.Max(width, def.MinWidth);
                state.Height = Math.Max(height, def.MinHeight);
            }
            
            LayoutChanged?.Invoke(this, EventArgs.Empty);
        }
    }

    /// <summary>
    /// Get all visible panels.
    /// </summary>
    public IEnumerable<PanelState> GetVisiblePanels()
    {
        return _states.Values.Where(s =>
            s.Visibility == PanelVisibility.Visible);
    }

    /// <summary>
    /// Save the current layout.
    /// </summary>
    public Dictionary<string, PanelState> SaveLayout()
    {
        return new Dictionary<string, PanelState>(_states);
    }

    /// <summary>
    /// Restore a saved layout.
    /// </summary>
    public void RestoreLayout(Dictionary<string, PanelState> layout)
    {
        // Clear current dock groups
        _leftPanels.Clear();
        _rightPanels.Clear();
        _topPanels.Clear();
        _bottomPanels.Clear();
        _centerPanels.Clear();
        _floatingPanels.Clear();
        
        // Apply saved states
        foreach (var kvp in layout)
        {
            if (_states.ContainsKey(kvp.Key))
            {
                _states[kvp.Key] = kvp.Value;
                AddToDockGroup(kvp.Value);
            }
        }
        
        LayoutChanged?.Invoke(this, EventArgs.Empty);
    }

    /// <summary>
    /// Reset to default layout.
    /// </summary>
    public void ResetToDefault()
    {
        foreach (var def in _definitions.Values)
        {
            if (_states.TryGetValue(def.Id, out var state))
            {
                RemoveFromDockGroup(state);
                
                state.Position = def.DefaultPosition;
                state.Width = def.DefaultWidth;
                state.Height = def.DefaultHeight;
                state.Visibility = PanelVisibility.Visible;
                
                AddToDockGroup(state);
            }
        }
        
        LayoutChanged?.Invoke(this, EventArgs.Empty);
    }

    private void AddToDockGroup(PanelState state)
    {
        var collection = state.Position switch
        {
            PanelDockPosition.Left => _leftPanels,
            PanelDockPosition.Right => _rightPanels,
            PanelDockPosition.Top => _topPanels,
            PanelDockPosition.Bottom => _bottomPanels,
            PanelDockPosition.Center => _centerPanels,
            PanelDockPosition.Float => _floatingPanels,
            _ => _leftPanels,
        };
        
        collection.Add(state);
    }

    private void RemoveFromDockGroup(PanelState state)
    {
        _leftPanels.Remove(state);
        _rightPanels.Remove(state);
        _topPanels.Remove(state);
        _bottomPanels.Remove(state);
        _centerPanels.Remove(state);
        _floatingPanels.Remove(state);
    }
}
