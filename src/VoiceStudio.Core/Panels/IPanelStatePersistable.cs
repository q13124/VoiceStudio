using System.Threading;
using System.Threading.Tasks;

namespace VoiceStudio.Core.Panels
{
    /// <summary>
    /// Interface for panels that support state persistence.
    /// Implement this to save and restore custom panel state (scroll position, 
    /// selection, filters, etc.) across sessions.
    /// 
    /// Backend-Frontend Integration Plan - Phase 2.
    /// </summary>
    public interface IPanelStatePersistable
    {
        /// <summary>
        /// Gets the current state of the panel for persistence.
        /// Called when the panel is deactivated or when explicitly saving state.
        /// </summary>
        /// <returns>
        /// A PanelStateData object containing the panel's current state.
        /// Return null if no state needs to be persisted.
        /// </returns>
        PanelStateData? GetCurrentState();

        /// <summary>
        /// Restores the panel to a previously saved state.
        /// Called when the panel is activated and saved state exists.
        /// </summary>
        /// <param name="state">The state data to restore.</param>
        /// <param name="cancellationToken">Cancellation token.</param>
        Task RestoreStateAsync(PanelStateData state, CancellationToken cancellationToken = default);
    }

    /// <summary>
    /// Data container for panel state persistence.
    /// Holds common state properties and a custom data dictionary
    /// for panel-specific state.
    /// </summary>
    public class PanelStateData
    {
        /// <summary>
        /// Gets or sets the panel ID this state belongs to.
        /// </summary>
        public string PanelId { get; set; } = string.Empty;

        /// <summary>
        /// Gets or sets the scroll position (for scrollable panels).
        /// </summary>
        public double? ScrollPosition { get; set; }

        /// <summary>
        /// Gets or sets the horizontal scroll position (for panels with horizontal scroll).
        /// </summary>
        public double? HorizontalScrollPosition { get; set; }

        /// <summary>
        /// Gets or sets the selected item ID (e.g., selected profile, audio file).
        /// </summary>
        public string? SelectedItemId { get; set; }

        /// <summary>
        /// Gets or sets the list of selected item IDs (for multi-select panels).
        /// </summary>
        public string[]? SelectedItemIds { get; set; }

        /// <summary>
        /// Gets or sets the current search/filter text.
        /// </summary>
        public string? SearchText { get; set; }

        /// <summary>
        /// Gets or sets the current sort column.
        /// </summary>
        public string? SortColumn { get; set; }

        /// <summary>
        /// Gets or sets whether sort is descending.
        /// </summary>
        public bool? SortDescending { get; set; }

        /// <summary>
        /// Gets or sets the expanded/collapsed state of sections.
        /// Key = section ID, Value = true if expanded.
        /// </summary>
        public System.Collections.Generic.Dictionary<string, bool>? ExpandedSections { get; set; }

        /// <summary>
        /// Gets or sets the active tab index (for tabbed panels).
        /// </summary>
        public int? ActiveTabIndex { get; set; }

        /// <summary>
        /// Gets or sets the zoom level (for zoomable panels like Timeline).
        /// </summary>
        public double? ZoomLevel { get; set; }

        /// <summary>
        /// Gets or sets custom panel-specific state data.
        /// Use this for any state not covered by the common properties.
        /// </summary>
        public System.Collections.Generic.Dictionary<string, object>? CustomData { get; set; }

        /// <summary>
        /// Gets or sets the timestamp when this state was captured.
        /// </summary>
        public System.DateTime? CapturedAt { get; set; }
    }
}
