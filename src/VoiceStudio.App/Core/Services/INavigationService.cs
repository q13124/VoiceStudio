using System;
using System.Collections.Generic;
using System.Threading;
using System.Threading.Tasks;
using VoiceStudio.Core.Models;

namespace VoiceStudio.Core.Services
{
    /// <summary>
    /// Service for managing panel navigation, deep-links, and backstack.
    /// </summary>
    public interface INavigationService
    {
        /// <summary>
        /// Navigates to a panel with optional parameters.
        /// </summary>
        /// <param name="panelId">The panel ID to navigate to.</param>
        /// <param name="parameters">Optional navigation parameters.</param>
        /// <param name="cancellationToken">Cancellation token.</param>
        Task NavigateToPanelAsync(string panelId, Dictionary<string, object>? parameters = null, CancellationToken cancellationToken = default);

        /// <summary>
        /// Navigates back to the previous panel.
        /// </summary>
        /// <param name="cancellationToken">Cancellation token.</param>
        Task NavigateBackAsync(CancellationToken cancellationToken = default);

        /// <summary>
        /// Checks if back navigation is possible.
        /// </summary>
        bool CanNavigateBack();

        /// <summary>
        /// Gets the current panel ID.
        /// </summary>
        string? GetCurrentPanelId();

        /// <summary>
        /// Gets the navigation backstack.
        /// </summary>
        IReadOnlyList<NavigationEntry> GetBackStack();

        /// <summary>
        /// Clears the navigation backstack.
        /// </summary>
        void ClearBackStack();

        /// <summary>
        /// Event raised when navigation occurs.
        /// </summary>
        event EventHandler<NavigationEventArgs> NavigationChanged;

        /// <summary>
        /// Event raised when the backstack changes.
        /// </summary>
        event EventHandler BackStackChanged;
    }
}
