using System;
using System.Collections.Generic;

namespace VoiceStudio.Core.Models
{
  /// <summary>
  /// Represents a navigation entry in the backstack.
  /// </summary>
  public class NavigationEntry
  {
    /// <summary>
    /// Gets or sets the panel ID.
    /// </summary>
    public string PanelId { get; set; } = string.Empty;

    /// <summary>
    /// Gets or sets the navigation parameters.
    /// </summary>
    public Dictionary<string, object> Parameters { get; set; } = new();

    /// <summary>
    /// Gets or sets the timestamp when navigation occurred.
    /// </summary>
    public DateTime Timestamp { get; set; } = DateTime.UtcNow;

    /// <summary>
    /// Gets or sets an optional title for display in breadcrumbs.
    /// </summary>
    public string? Title { get; set; }
  }

  /// <summary>
  /// Event arguments for navigation events.
  /// </summary>
  public class NavigationEventArgs : EventArgs
  {
    /// <summary>
    /// Gets or sets the previous panel ID (null if first navigation).
    /// </summary>
    public string? PreviousPanelId { get; set; }

    /// <summary>
    /// Gets or sets the new panel ID.
    /// </summary>
    public string NewPanelId { get; set; } = string.Empty;

    /// <summary>
    /// Gets or sets the navigation parameters.
    /// </summary>
    public Dictionary<string, object> Parameters { get; set; } = new();

    /// <summary>
    /// Gets or sets whether this navigation was a back navigation.
    /// </summary>
    public bool IsBackNavigation { get; set; }
  }
}