using System;
using System.Collections.Generic;
using VoiceStudio.Core.Models;
using Microsoft.UI.Xaml;

namespace VoiceStudio.App.Services
{
    /// <summary>
    /// Service for managing multi-select state across panels.
    /// Implements IDEA 12: Multi-Select with Visual Selection Indicators.
    /// </summary>
    public class MultiSelectService
    {
        private readonly Dictionary<string, MultiSelectState> _panelStates = new();

        /// <summary>
        /// Gets or creates the multi-select state for a panel.
        /// </summary>
        public MultiSelectState GetState(string panelId)
        {
            if (!_panelStates.TryGetValue(panelId, out var state))
            {
                state = new MultiSelectState();
                _panelStates[panelId] = state;
            }
            return state;
        }

        /// <summary>
        /// Clears the selection for a panel.
        /// </summary>
        public void ClearSelection(string panelId)
        {
            if (_panelStates.TryGetValue(panelId, out var state))
            {
                state.Clear();
            }
        }

        /// <summary>
        /// Clears all selections across all panels.
        /// </summary>
        public void ClearAllSelections()
        {
            foreach (var state in _panelStates.Values)
            {
                state.Clear();
            }
        }

        /// <summary>
        /// Removes the state for a panel (cleanup).
        /// </summary>
        public void RemoveState(string panelId)
        {
            _panelStates.Remove(panelId);
        }

        /// <summary>
        /// Event raised when selection changes in any panel.
        /// </summary>
        public event EventHandler<SelectionChangedEventArgs>? SelectionChanged;

        /// <summary>
        /// Raises the SelectionChanged event.
        /// </summary>
        public void OnSelectionChanged(string panelId, MultiSelectState state)
        {
            SelectionChanged?.Invoke(this, new SelectionChangedEventArgs(panelId, state));
        }
    }

    /// <summary>
    /// Event arguments for selection changed events.
    /// </summary>
    public class SelectionChangedEventArgs : EventArgs
    {
        public string PanelId { get; }
        public MultiSelectState State { get; }

        public SelectionChangedEventArgs(string panelId, MultiSelectState state)
        {
            PanelId = panelId;
            State = state;
        }
    }
}

