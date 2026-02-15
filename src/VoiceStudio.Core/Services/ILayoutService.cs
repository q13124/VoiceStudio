// VoiceStudio - Panel Architecture Phase 3: Workspace System
// ILayoutService provides low-level panel layout operations

using System;
using System.Collections.Generic;
using System.Threading.Tasks;
using VoiceStudio.Core.Panels;

namespace VoiceStudio.Core.Services;

/// <summary>
/// Event args for panel visibility changes.
/// </summary>
public class PanelVisibilityChangedEventArgs : EventArgs
{
    public string PanelId { get; }
    public bool IsVisible { get; }

    public PanelVisibilityChangedEventArgs(string panelId, bool isVisible)
    {
        PanelId = panelId;
        IsVisible = isVisible;
    }
}

/// <summary>
/// Event args for panel region changes.
/// </summary>
public class PanelRegionChangedEventArgs : EventArgs
{
    public string PanelId { get; }
    public PanelRegion OldRegion { get; }
    public PanelRegion NewRegion { get; }

    public PanelRegionChangedEventArgs(string panelId, PanelRegion oldRegion, PanelRegion newRegion)
    {
        PanelId = panelId;
        OldRegion = oldRegion;
        NewRegion = newRegion;
    }
}

/// <summary>
/// Service for low-level panel layout operations.
/// </summary>
public interface ILayoutService
{
    #region Panel Visibility

    /// <summary>
    /// Shows a panel by ID.
    /// </summary>
    void ShowPanel(string panelId);

    /// <summary>
    /// Hides a panel by ID.
    /// </summary>
    void HidePanel(string panelId);

    /// <summary>
    /// Toggles panel visibility.
    /// </summary>
    void TogglePanel(string panelId);

    /// <summary>
    /// Checks if a panel is visible.
    /// </summary>
    bool IsPanelVisible(string panelId);

    #endregion

    #region Panel Region Management

    /// <summary>
    /// Moves a panel to a different region.
    /// </summary>
    void MovePanel(string panelId, PanelRegion targetRegion);

    /// <summary>
    /// Gets the current region of a panel.
    /// </summary>
    PanelRegion? GetPanelRegion(string panelId);

    /// <summary>
    /// Reorders panels within a region.
    /// </summary>
    void ReorderPanels(PanelRegion region, IEnumerable<string> orderedPanelIds);

    #endregion

    #region Panel Size

    /// <summary>
    /// Sets the relative size of a panel.
    /// </summary>
    void SetPanelSize(string panelId, double relativeWidth, double relativeHeight);

    /// <summary>
    /// Collapses a panel (minimizes to header).
    /// </summary>
    void CollapsePanel(string panelId);

    /// <summary>
    /// Expands a collapsed panel.
    /// </summary>
    void ExpandPanel(string panelId);

    /// <summary>
    /// Checks if a panel is collapsed.
    /// </summary>
    bool IsPanelCollapsed(string panelId);

    #endregion

    #region Layout Capture

    /// <summary>
    /// Captures the current layout as a list of panel placements.
    /// </summary>
    IReadOnlyList<PanelPlacement> CaptureCurrentLayout();

    /// <summary>
    /// Applies a list of panel placements to restore a layout.
    /// </summary>
    Task ApplyLayoutAsync(IReadOnlyList<PanelPlacement> placements);

    #endregion

    #region Events

    /// <summary>
    /// Raised when a panel's visibility changes.
    /// </summary>
    event EventHandler<PanelVisibilityChangedEventArgs>? PanelVisibilityChanged;

    /// <summary>
    /// Raised when a panel is moved to a different region.
    /// </summary>
    event EventHandler<PanelRegionChangedEventArgs>? PanelRegionChanged;

    #endregion
}
