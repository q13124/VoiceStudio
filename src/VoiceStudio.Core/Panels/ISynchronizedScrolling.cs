// VoiceStudio - Panel Architecture Phase D: Synchronized Scrolling
// Interface for panels that support synchronized scrolling

using System;

namespace VoiceStudio.Core.Panels
{
    /// <summary>
    /// Interface for panels that can synchronize their scroll position with other panels.
    /// Typically used for timeline-based views where horizontal scroll represents time position.
    /// </summary>
    public interface ISynchronizedScrolling
    {
        /// <summary>
        /// Gets the unique identifier for this scrollable panel.
        /// </summary>
        string ScrollPanelId { get; }

        /// <summary>
        /// Gets or sets whether this panel is participating in synchronized scrolling.
        /// </summary>
        bool IsSynchronizedScrollEnabled { get; set; }

        /// <summary>
        /// Gets the current scroll position as a normalized value (0.0 to 1.0).
        /// </summary>
        double NormalizedScrollPosition { get; }

        /// <summary>
        /// Gets the current scroll position in time (for timeline-based views).
        /// </summary>
        TimeSpan? TimePosition { get; }

        /// <summary>
        /// Gets the scroll group this panel belongs to.
        /// Panels in the same group synchronize together.
        /// </summary>
        string ScrollGroup { get; }

        /// <summary>
        /// Sets the scroll position from an external sync source.
        /// </summary>
        /// <param name="normalizedPosition">Position between 0.0 and 1.0.</param>
        /// <param name="sourcePanelId">ID of the panel that originated the scroll.</param>
        void SetScrollPosition(double normalizedPosition, string sourcePanelId);

        /// <summary>
        /// Sets the scroll position based on time (for timeline views).
        /// </summary>
        /// <param name="timePosition">The time position to scroll to.</param>
        /// <param name="sourcePanelId">ID of the panel that originated the scroll.</param>
        void SetTimePosition(TimeSpan timePosition, string sourcePanelId);

        /// <summary>
        /// Raised when the scroll position changes within this panel.
        /// </summary>
        event EventHandler<ScrollPositionChangedEventArgs>? ScrollPositionChanged;
    }

    /// <summary>
    /// Event arguments for scroll position changes.
    /// </summary>
    public sealed class ScrollPositionChangedEventArgs : EventArgs
    {
        /// <summary>
        /// Gets the ID of the panel that changed scroll position.
        /// </summary>
        public string SourcePanelId { get; }

        /// <summary>
        /// Gets the scroll group this change applies to.
        /// </summary>
        public string ScrollGroup { get; }

        /// <summary>
        /// Gets the normalized scroll position (0.0 to 1.0).
        /// </summary>
        public double NormalizedPosition { get; }

        /// <summary>
        /// Gets the time position (for timeline views), or null if not applicable.
        /// </summary>
        public TimeSpan? TimePosition { get; }

        /// <summary>
        /// Gets the timestamp when the scroll occurred.
        /// </summary>
        public DateTime Timestamp { get; }

        public ScrollPositionChangedEventArgs(
            string sourcePanelId,
            string scrollGroup,
            double normalizedPosition,
            TimeSpan? timePosition = null)
        {
            SourcePanelId = sourcePanelId ?? string.Empty;
            ScrollGroup = scrollGroup ?? "default";
            NormalizedPosition = Math.Clamp(normalizedPosition, 0.0, 1.0);
            TimePosition = timePosition;
            Timestamp = DateTime.UtcNow;
        }
    }

    /// <summary>
    /// Predefined scroll groups for common panel synchronization scenarios.
    /// </summary>
    public static class ScrollGroups
    {
        /// <summary>
        /// Timeline-based panels (Timeline, Waveform, Video preview).
        /// </summary>
        public const string Timeline = "timeline";

        /// <summary>
        /// List-based panels (Library, Assets, Jobs queue).
        /// </summary>
        public const string List = "list";

        /// <summary>
        /// Editor panels (Text editor, Script editor).
        /// </summary>
        public const string Editor = "editor";

        /// <summary>
        /// Default group for panels without a specific group.
        /// </summary>
        public const string Default = "default";
    }
}
