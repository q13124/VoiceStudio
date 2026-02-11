using System.Threading;
using System.Threading.Tasks;

namespace VoiceStudio.Core.Panels
{
  /// <summary>
  /// Base interface for panel views.
  /// </summary>
  public interface IPanelView
  {
    /// <summary>
    /// Gets the unique panel identifier.
    /// </summary>
    string PanelId { get; }      // e.g. "Profiles", "Timeline", "Mixer"

    /// <summary>
    /// Gets the display name for the panel.
    /// </summary>
    string DisplayName { get; }

    /// <summary>
    /// Gets the region where this panel is displayed.
    /// </summary>
    PanelRegion Region { get; }   // Left, Center, Right, Bottom, Floating
  }

  /// <summary>
  /// Interface for panels that need lifecycle management.
  /// Implement this to receive activation/deactivation callbacks.
  /// </summary>
  public interface IPanelLifecycle
  {
    /// <summary>
    /// Called when the panel becomes the active panel.
    /// Use this to subscribe to events, start polling, or refresh data.
    /// </summary>
    /// <param name="cancellationToken">Cancellation token.</param>
    Task OnActivatedAsync(CancellationToken cancellationToken = default);

    /// <summary>
    /// Called when the panel is no longer active.
    /// Use this to unsubscribe from events, stop timers, and release resources.
    /// </summary>
    /// <param name="cancellationToken">Cancellation token.</param>
    Task OnDeactivatedAsync(CancellationToken cancellationToken = default);

    /// <summary>
    /// Called to refresh the panel's data.
    /// </summary>
    /// <param name="cancellationToken">Cancellation token.</param>
    Task RefreshAsync(CancellationToken cancellationToken = default);
  }

  /// <summary>
  /// Combined interface for panels with full lifecycle support.
  /// </summary>
  public interface ILifecyclePanelView : IPanelView, IPanelLifecycle
  {
  }
}