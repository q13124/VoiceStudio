// VoiceStudio - Panel Architecture Phase D: Event Serialization & Debug Replay
// Service interface for capturing and replaying events

using System;
using System.Collections.Generic;
using System.Threading;
using System.Threading.Tasks;
using VoiceStudio.Core.Debugging;

namespace VoiceStudio.Core.Services
{
    /// <summary>
    /// Service for capturing events and creating debug replay bundles.
    /// Useful for debugging complex event sequences and reproducing issues.
    /// </summary>
    public interface IEventReplayService
    {
        /// <summary>
        /// Gets whether capture is currently active.
        /// </summary>
        bool IsCapturing { get; }

        /// <summary>
        /// Gets the number of events captured in the current session.
        /// </summary>
        int CapturedEventCount { get; }

        /// <summary>
        /// Starts capturing events.
        /// </summary>
        /// <param name="description">Optional description for the capture session.</param>
        void StartCapture(string? description = null);

        /// <summary>
        /// Stops capturing events and returns the bundle.
        /// </summary>
        /// <returns>The completed replay bundle.</returns>
        EventReplayBundle StopCapture();

        /// <summary>
        /// Records an event to the current capture session.
        /// </summary>
        /// <param name="eventType">The type name of the event.</param>
        /// <param name="eventPayload">The event object to serialize.</param>
        /// <param name="sourcePanelId">Optional source panel ID.</param>
        /// <param name="targetPanelId">Optional target panel ID.</param>
        void RecordEvent(string eventType, object? eventPayload, string? sourcePanelId = null, string? targetPanelId = null);

        /// <summary>
        /// Captures a state snapshot.
        /// </summary>
        /// <returns>The current state snapshot.</returns>
        StateSnapshot CaptureStateSnapshot();

        /// <summary>
        /// Saves a bundle to a file.
        /// </summary>
        /// <param name="bundle">The bundle to save.</param>
        /// <param name="filePath">The file path.</param>
        /// <param name="cancellationToken">Cancellation token.</param>
        Task SaveBundleAsync(EventReplayBundle bundle, string filePath, CancellationToken cancellationToken = default);

        /// <summary>
        /// Loads a bundle from a file.
        /// </summary>
        /// <param name="filePath">The file path.</param>
        /// <param name="cancellationToken">Cancellation token.</param>
        /// <returns>The loaded bundle.</returns>
        Task<EventReplayBundle?> LoadBundleAsync(string filePath, CancellationToken cancellationToken = default);

        /// <summary>
        /// Gets recent bundles from the cache.
        /// </summary>
        /// <param name="maxCount">Maximum number of bundles to return.</param>
        /// <returns>Collection of recent bundles.</returns>
        IReadOnlyList<EventReplayBundle> GetRecentBundles(int maxCount = 10);

        /// <summary>
        /// Clears the recent bundles cache.
        /// </summary>
        void ClearBundleCache();

        /// <summary>
        /// Raised when an event is recorded.
        /// </summary>
        event EventHandler<SerializedEvent>? EventRecorded;

        /// <summary>
        /// Raised when capture starts.
        /// </summary>
        event EventHandler? CaptureStarted;

        /// <summary>
        /// Raised when capture stops.
        /// </summary>
        event EventHandler<EventReplayBundle>? CaptureStopped;
    }
}
