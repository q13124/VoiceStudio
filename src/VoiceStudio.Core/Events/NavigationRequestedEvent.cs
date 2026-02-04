namespace VoiceStudio.Core.Events
{
  /// <summary>
  /// Event raised when navigation to a panel is requested.
  /// Used for cross-module navigation via the Messenger pattern.
  /// </summary>
  public sealed class NavigationRequestedEvent
  {
    /// <summary>
    /// The panel identifier to navigate to (e.g., "VoiceSynthesis", "Timeline").
    /// </summary>
    public string PanelId { get; init; } = string.Empty;

    /// <summary>
    /// Optional parameter to pass to the target panel.
    /// </summary>
    public object? Parameter { get; init; }

    /// <summary>
    /// Optional region hint for where to display the panel.
    /// If null, the panel's default region is used.
    /// </summary>
    public Panels.PanelRegion? TargetRegion { get; init; }
  }
}