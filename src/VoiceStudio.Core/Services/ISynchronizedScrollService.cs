// VoiceStudio - Panel Architecture Phase D: Synchronized Scrolling
// Service for coordinating scroll position across panels

using System;
using System.Collections.Generic;
using VoiceStudio.Core.Panels;

namespace VoiceStudio.Core.Services
{
    /// <summary>
    /// Service that coordinates scroll position synchronization across panels.
    /// Panels in the same scroll group will have their scroll positions synchronized.
    /// </summary>
    public interface ISynchronizedScrollService
    {
        /// <summary>
        /// Registers a panel for synchronized scrolling.
        /// </summary>
        /// <param name="panel">The panel to register.</param>
        void Register(ISynchronizedScrolling panel);

        /// <summary>
        /// Unregisters a panel from synchronized scrolling.
        /// </summary>
        /// <param name="panel">The panel to unregister.</param>
        void Unregister(ISynchronizedScrolling panel);

        /// <summary>
        /// Broadcasts a scroll position change to all panels in the same group.
        /// </summary>
        /// <param name="args">The scroll position change event args.</param>
        void BroadcastScroll(ScrollPositionChangedEventArgs args);

        /// <summary>
        /// Gets all panels in a specific scroll group.
        /// </summary>
        /// <param name="groupName">The name of the scroll group.</param>
        /// <returns>Collection of panel IDs in the group.</returns>
        IReadOnlyCollection<string> GetGroupMembers(string groupName);

        /// <summary>
        /// Gets all registered scroll groups.
        /// </summary>
        /// <returns>Collection of group names.</returns>
        IReadOnlyCollection<string> GetGroups();

        /// <summary>
        /// Sets whether synchronized scrolling is globally enabled.
        /// </summary>
        bool IsEnabled { get; set; }

        /// <summary>
        /// Raised when a scroll position is broadcast.
        /// </summary>
        event EventHandler<ScrollPositionChangedEventArgs>? ScrollBroadcast;
    }
}
