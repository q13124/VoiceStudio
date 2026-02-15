// VoiceStudio - Panel Architecture Phase D: Selection Synchronization
// Service for broadcasting selection changes to follower panels

using System;
using System.Collections.Generic;
using VoiceStudio.Core.Panels;

namespace VoiceStudio.Core.Services
{
    /// <summary>
    /// Service that broadcasts selection changes to panels that follow selections.
    /// Allows panels to synchronize their view based on selections in other panels.
    /// </summary>
    public interface ISelectionBroadcastService
    {
        /// <summary>
        /// Gets the current selection.
        /// </summary>
        SelectionInfo CurrentSelection { get; }

        /// <summary>
        /// Gets the selection history (for back/forward navigation).
        /// </summary>
        IReadOnlyList<SelectionInfo> SelectionHistory { get; }

        /// <summary>
        /// Broadcasts a selection change to all registered followers.
        /// </summary>
        /// <param name="selection">The new selection.</param>
        void BroadcastSelection(SelectionInfo selection);

        /// <summary>
        /// Registers a panel as a selection follower.
        /// </summary>
        /// <param name="follower">The panel to register.</param>
        void RegisterFollower(ISelectionFollower follower);

        /// <summary>
        /// Unregisters a panel from receiving selection updates.
        /// </summary>
        /// <param name="follower">The panel to unregister.</param>
        void UnregisterFollower(ISelectionFollower follower);

        /// <summary>
        /// Gets whether a specific panel is currently following selections.
        /// </summary>
        /// <param name="panelId">The panel ID.</param>
        /// <returns>True if the panel is following, false otherwise.</returns>
        bool IsPanelFollowing(string panelId);

        /// <summary>
        /// Sets whether a specific panel should follow selections.
        /// </summary>
        /// <param name="panelId">The panel ID.</param>
        /// <param name="follow">True to enable following, false to disable.</param>
        void SetPanelFollowing(string panelId, bool follow);

        /// <summary>
        /// Gets all registered follower panel IDs.
        /// </summary>
        /// <returns>Collection of panel IDs.</returns>
        IReadOnlyCollection<string> GetFollowerPanelIds();

        /// <summary>
        /// Raised when a selection is broadcast.
        /// </summary>
        event EventHandler<PanelSelectionChangedEventArgs>? SelectionBroadcast;
    }
}
