// VoiceStudio - Panel Architecture Phase D: Selection Synchronization
// ISelectionFollower interface for panels that can follow selections

using System;
using System.Threading;
using System.Threading.Tasks;

namespace VoiceStudio.Core.Panels
{
    /// <summary>
    /// Interface for panels that can follow a selection from another panel.
    /// When enabled, the panel will update its view based on the current selection.
    /// </summary>
    public interface ISelectionFollower
    {
        /// <summary>
        /// Gets or sets whether the panel is following selections from other panels.
        /// </summary>
        bool IsFollowingSelection { get; set; }

        /// <summary>
        /// Gets the types of selections this panel can follow.
        /// </summary>
        SelectionType[] SupportedSelectionTypes { get; }

        /// <summary>
        /// Called when a selection changes in a linked panel.
        /// </summary>
        /// <param name="selection">The new selection details.</param>
        /// <param name="cancellationToken">Cancellation token.</param>
        Task OnSelectionChangedAsync(SelectionInfo selection, CancellationToken cancellationToken = default);
    }

    /// <summary>
    /// Types of selectable items that can be followed.
    /// </summary>
    public enum SelectionType
    {
        /// <summary>
        /// Voice profile selection.
        /// </summary>
        Profile,

        /// <summary>
        /// Audio asset selection.
        /// </summary>
        Asset,

        /// <summary>
        /// Timeline clip selection.
        /// </summary>
        TimelineClip,

        /// <summary>
        /// Job selection.
        /// </summary>
        Job,

        /// <summary>
        /// Text block selection.
        /// </summary>
        TextBlock,

        /// <summary>
        /// Project selection.
        /// </summary>
        Project,

        /// <summary>
        /// Any selection type (for panels that can follow all).
        /// </summary>
        Any
    }

    /// <summary>
    /// Information about a selection that can be shared across panels.
    /// </summary>
    public sealed record SelectionInfo
    {
        /// <summary>
        /// Gets the type of item selected.
        /// </summary>
        public SelectionType Type { get; init; }

        /// <summary>
        /// Gets the unique identifier of the selected item.
        /// </summary>
        public string Id { get; init; } = string.Empty;

        /// <summary>
        /// Gets the display name of the selected item.
        /// </summary>
        public string? DisplayName { get; init; }

        /// <summary>
        /// Gets the ID of the panel that originated this selection.
        /// </summary>
        public string SourcePanelId { get; init; } = string.Empty;

        /// <summary>
        /// Gets the timestamp when the selection was made.
        /// </summary>
        public DateTime Timestamp { get; init; } = DateTime.UtcNow;

        /// <summary>
        /// Gets additional metadata about the selection.
        /// </summary>
        public System.Collections.Generic.IReadOnlyDictionary<string, object>? Metadata { get; init; }

        /// <summary>
        /// Creates an empty (no selection) info.
        /// </summary>
        public static SelectionInfo Empty => new() { Type = SelectionType.Any, Id = string.Empty };

        /// <summary>
        /// Returns true if this represents a valid selection.
        /// </summary>
        public bool IsEmpty => string.IsNullOrEmpty(Id);
    }

    /// <summary>
    /// Event arguments for panel selection broadcast changes.
    /// Named distinctly to avoid conflict with MultiSelectService.SelectionChangedEventArgs.
    /// </summary>
    public sealed class PanelSelectionChangedEventArgs : EventArgs
    {
        /// <summary>
        /// Gets the previous selection (may be empty).
        /// </summary>
        public SelectionInfo Previous { get; }

        /// <summary>
        /// Gets the new selection.
        /// </summary>
        public SelectionInfo Current { get; }

        public PanelSelectionChangedEventArgs(SelectionInfo previous, SelectionInfo current)
        {
            Previous = previous ?? SelectionInfo.Empty;
            Current = current ?? SelectionInfo.Empty;
        }
    }
}
