// VoiceStudio - Panel Architecture Phase D: Event Serialization & Debug Replay
// Structures for capturing and replaying event sequences

using System;
using System.Collections.Generic;
using System.Text.Json;
using System.Text.Json.Serialization;

namespace VoiceStudio.Core.Debugging
{
    /// <summary>
    /// A bundle that captures a sequence of events for debugging and replay.
    /// Can be serialized to JSON for storage or sharing.
    /// </summary>
    public sealed class EventReplayBundle
    {
        /// <summary>
        /// Gets or sets the unique ID of this bundle.
        /// </summary>
        public string BundleId { get; set; } = Guid.NewGuid().ToString();

        /// <summary>
        /// Gets or sets the timestamp when the bundle was created.
        /// </summary>
        public DateTime CreatedAt { get; set; } = DateTime.UtcNow;

        /// <summary>
        /// Gets or sets a description of the bundle contents.
        /// </summary>
        public string? Description { get; set; }

        /// <summary>
        /// Gets or sets the application version that created this bundle.
        /// </summary>
        public string? AppVersion { get; set; }

        /// <summary>
        /// Gets or sets the initial state snapshot at the start of capture.
        /// </summary>
        public StateSnapshot? InitialState { get; set; }

        /// <summary>
        /// Gets or sets the final state snapshot at the end of capture.
        /// </summary>
        public StateSnapshot? FinalState { get; set; }

        /// <summary>
        /// Gets or sets the list of captured events in chronological order.
        /// </summary>
        public List<SerializedEvent> Events { get; set; } = new();

        /// <summary>
        /// Gets or sets any metadata associated with this bundle.
        /// </summary>
        public Dictionary<string, string>? Metadata { get; set; }

        /// <summary>
        /// Serializes this bundle to JSON.
        /// </summary>
        public string ToJson(bool indented = true)
        {
            var options = new JsonSerializerOptions
            {
                WriteIndented = indented,
                PropertyNamingPolicy = JsonNamingPolicy.CamelCase,
                DefaultIgnoreCondition = JsonIgnoreCondition.WhenWritingNull
            };
            return JsonSerializer.Serialize(this, options);
        }

        /// <summary>
        /// Deserializes a bundle from JSON.
        /// </summary>
        public static EventReplayBundle? FromJson(string json)
        {
            if (string.IsNullOrEmpty(json)) return null;

            var options = new JsonSerializerOptions
            {
                PropertyNamingPolicy = JsonNamingPolicy.CamelCase
            };
            return JsonSerializer.Deserialize<EventReplayBundle>(json, options);
        }
    }

    /// <summary>
    /// A serialized representation of an event.
    /// </summary>
    public sealed class SerializedEvent
    {
        /// <summary>
        /// Gets or sets the unique ID of this event instance.
        /// </summary>
        public string EventId { get; set; } = Guid.NewGuid().ToString();

        /// <summary>
        /// Gets or sets the type name of the event.
        /// </summary>
        public string EventType { get; set; } = string.Empty;

        /// <summary>
        /// Gets or sets the timestamp when the event occurred.
        /// </summary>
        public DateTime Timestamp { get; set; } = DateTime.UtcNow;

        /// <summary>
        /// Gets or sets the source panel ID (if applicable).
        /// </summary>
        public string? SourcePanelId { get; set; }

        /// <summary>
        /// Gets or sets the target panel ID (if applicable).
        /// </summary>
        public string? TargetPanelId { get; set; }

        /// <summary>
        /// Gets or sets the serialized event payload as JSON.
        /// </summary>
        public string? PayloadJson { get; set; }

        /// <summary>
        /// Gets or sets the sequence number within the bundle.
        /// </summary>
        public int SequenceNumber { get; set; }

        /// <summary>
        /// Gets or sets optional metadata about the event.
        /// </summary>
        public Dictionary<string, string>? Metadata { get; set; }
    }

    /// <summary>
    /// A snapshot of application state at a point in time.
    /// </summary>
    public sealed class StateSnapshot
    {
        /// <summary>
        /// Gets or sets the timestamp of this snapshot.
        /// </summary>
        public DateTime Timestamp { get; set; } = DateTime.UtcNow;

        /// <summary>
        /// Gets or sets the active workspace ID.
        /// </summary>
        public string? ActiveWorkspaceId { get; set; }

        /// <summary>
        /// Gets or sets the active panel ID.
        /// </summary>
        public string? ActivePanelId { get; set; }

        /// <summary>
        /// Gets or sets the selected asset ID.
        /// </summary>
        public string? SelectedAssetId { get; set; }

        /// <summary>
        /// Gets or sets the selected profile ID.
        /// </summary>
        public string? SelectedProfileId { get; set; }

        /// <summary>
        /// Gets or sets visible panel IDs.
        /// </summary>
        public List<string>? VisiblePanels { get; set; }

        /// <summary>
        /// Gets or sets the full state serialized as JSON.
        /// </summary>
        public string? FullStateJson { get; set; }

        /// <summary>
        /// Gets or sets custom state data.
        /// </summary>
        public Dictionary<string, string>? CustomData { get; set; }
    }
}
