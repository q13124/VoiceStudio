// VoiceStudio - Panel Architecture Phase 1: Event Enrichment
// Intent-aware events enable panels to respond contextually based on user intent

namespace VoiceStudio.Core.Events;

/// <summary>
/// Describes the user's intent when triggering an event.
/// Panels can respond differently based on this intent.
/// </summary>
public enum InteractionIntent
{
    /// <summary>
    /// Default intent for navigation actions (clicking, selecting).
    /// Panels may load lightweight previews.
    /// </summary>
    Navigation = 0,

    /// <summary>
    /// User wants to preview content without committing.
    /// Panels should show preview UI, not modify state.
    /// </summary>
    Preview,

    /// <summary>
    /// User intends to edit the selected item.
    /// Panels should prepare edit UI and lock resources if needed.
    /// </summary>
    Edit,

    /// <summary>
    /// User wants to use the item immediately (e.g., drag-drop, double-click).
    /// Panels should apply the item directly.
    /// </summary>
    ImmediateUse,

    /// <summary>
    /// User wants to compare items (multi-select for comparison).
    /// Panels should enable side-by-side view.
    /// </summary>
    Compare,

    /// <summary>
    /// Background process started (synthesis, training).
    /// Panels should not interrupt current workflow.
    /// </summary>
    BackgroundProcess,

    /// <summary>
    /// System-initiated restore (e.g., session restore, undo).
    /// Panels should restore state silently without user-facing effects.
    /// </summary>
    SystemRestore,

    /// <summary>
    /// User initiated a batch operation.
    /// Panels may queue updates instead of immediate processing.
    /// </summary>
    BatchOperation,

    /// <summary>
    /// User performed a context menu action.
    /// </summary>
    ContextAction,

    /// <summary>
    /// Keyboard shortcut triggered the action.
    /// </summary>
    KeyboardShortcut
}
