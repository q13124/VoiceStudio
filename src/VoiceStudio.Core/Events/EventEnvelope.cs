// VoiceStudio - Panel Architecture Phase 1: Event Enrichment
// EventEnvelope wraps events with metadata for tracing, correlation, and intent

using System;

namespace VoiceStudio.Core.Events;

/// <summary>
/// Wraps an event payload with metadata for tracing, sequencing, and correlation.
/// </summary>
/// <typeparam name="T">The event payload type.</typeparam>
public sealed class EventEnvelope<T> where T : class
{
    /// <summary>
    /// Unique identifier for this specific event instance.
    /// </summary>
    public Guid EventId { get; }

    /// <summary>
    /// Monotonically increasing sequence number assigned by the event bus.
    /// Used for ordering and deduplication.
    /// </summary>
    public long Sequence { get; internal set; }

    /// <summary>
    /// Correlation ID linking related events across a workflow.
    /// Events in the same workflow share this ID.
    /// </summary>
    public Guid CorrelationId { get; }

    /// <summary>
    /// When the event was created.
    /// </summary>
    public DateTimeOffset Timestamp { get; }

    /// <summary>
    /// The panel that originated this event.
    /// </summary>
    public string SourcePanelId { get; }

    /// <summary>
    /// True if this event was triggered by a user action.
    /// False for system-generated events (restore, background processing).
    /// </summary>
    public bool IsUserInitiated { get; }

    /// <summary>
    /// The user's intent when triggering this event.
    /// </summary>
    public InteractionIntent Intent { get; }

    /// <summary>
    /// The actual event payload.
    /// </summary>
    public T Payload { get; }

    /// <summary>
    /// Creates a new event envelope.
    /// </summary>
    public EventEnvelope(
        T payload,
        string sourcePanelId,
        InteractionIntent intent = InteractionIntent.Navigation,
        bool isUserInitiated = true,
        Guid? correlationId = null)
    {
        EventId = Guid.NewGuid();
        Timestamp = DateTimeOffset.UtcNow;
        SourcePanelId = sourcePanelId ?? string.Empty;
        Intent = intent;
        IsUserInitiated = isUserInitiated;
        CorrelationId = correlationId ?? Guid.NewGuid();
        Payload = payload;
    }

    /// <summary>
    /// Creates a continuation envelope that shares the correlation ID.
    /// </summary>
    public EventEnvelope<TNext> Continue<TNext>(
        TNext payload,
        string sourcePanelId,
        InteractionIntent? intent = null,
        bool? isUserInitiated = null) where TNext : class
    {
        return new EventEnvelope<TNext>(
            payload,
            sourcePanelId,
            intent ?? Intent,
            isUserInitiated ?? IsUserInitiated,
            CorrelationId);
    }
}

/// <summary>
/// Factory methods for creating event envelopes.
/// </summary>
public static class EventEnvelope
{
    /// <summary>
    /// Creates a new event envelope for a user-initiated navigation action.
    /// </summary>
    public static EventEnvelope<T> ForNavigation<T>(T payload, string sourcePanelId) where T : class
        => new(payload, sourcePanelId, InteractionIntent.Navigation, isUserInitiated: true);

    /// <summary>
    /// Creates a new event envelope for a preview action.
    /// </summary>
    public static EventEnvelope<T> ForPreview<T>(T payload, string sourcePanelId) where T : class
        => new(payload, sourcePanelId, InteractionIntent.Preview, isUserInitiated: true);

    /// <summary>
    /// Creates a new event envelope for an edit action.
    /// </summary>
    public static EventEnvelope<T> ForEdit<T>(T payload, string sourcePanelId) where T : class
        => new(payload, sourcePanelId, InteractionIntent.Edit, isUserInitiated: true);

    /// <summary>
    /// Creates a new event envelope for immediate use (drag-drop, double-click).
    /// </summary>
    public static EventEnvelope<T> ForImmediateUse<T>(T payload, string sourcePanelId) where T : class
        => new(payload, sourcePanelId, InteractionIntent.ImmediateUse, isUserInitiated: true);

    /// <summary>
    /// Creates a new event envelope for system restore (undo, session restore).
    /// </summary>
    public static EventEnvelope<T> ForSystemRestore<T>(T payload, string sourcePanelId) where T : class
        => new(payload, sourcePanelId, InteractionIntent.SystemRestore, isUserInitiated: false);

    /// <summary>
    /// Creates a new event envelope for background process notifications.
    /// </summary>
    public static EventEnvelope<T> ForBackgroundProcess<T>(T payload, string sourcePanelId) where T : class
        => new(payload, sourcePanelId, InteractionIntent.BackgroundProcess, isUserInitiated: false);
}
