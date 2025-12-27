using System.Collections.Generic;
using System.Linq;
using System;

namespace VoiceStudio.Core.Models
{
    /// <summary>
    /// Represents the multi-select state for a panel or view.
    /// Implements IDEA 12: Multi-Select with Visual Selection Indicators.
    /// </summary>
    public class MultiSelectState
    {
        /// <summary>
        /// List of selected item IDs.
        /// </summary>
        public List<string> SelectedIds { get; set; } = new();

        /// <summary>
        /// Whether multi-select mode is active.
        /// </summary>
        public bool IsMultiSelectMode { get; set; }

        /// <summary>
        /// Whether the last selection was a range selection (Shift+Click).
        /// </summary>
        public bool IsRangeSelection { get; set; }

        /// <summary>
        /// The anchor item ID for range selection.
        /// </summary>
        public string? RangeAnchorId { get; set; }

        /// <summary>
        /// Gets the count of selected items.
        /// </summary>
        public int Count => SelectedIds.Count;

        /// <summary>
        /// Gets whether any items are selected.
        /// </summary>
        public bool HasSelection => SelectedIds.Count > 0;

        /// <summary>
        /// Gets whether multiple items are selected.
        /// </summary>
        public bool IsMultipleSelection => SelectedIds.Count > 1;

        /// <summary>
        /// Clears the selection.
        /// </summary>
        public void Clear()
        {
            SelectedIds.Clear();
            IsRangeSelection = false;
            RangeAnchorId = null;
        }

        /// <summary>
        /// Adds an item to the selection.
        /// </summary>
        public void Add(string id)
        {
            if (!SelectedIds.Contains(id))
            {
                SelectedIds.Add(id);
            }
        }

        /// <summary>
        /// Removes an item from the selection.
        /// </summary>
        public void Remove(string id)
        {
            SelectedIds.Remove(id);
            if (SelectedIds.Count == 0)
            {
                RangeAnchorId = null;
            }
        }

        /// <summary>
        /// Toggles an item's selection state.
        /// </summary>
        public void Toggle(string id)
        {
            if (SelectedIds.Contains(id))
            {
                Remove(id);
            }
            else
            {
                Add(id);
            }
        }

        /// <summary>
        /// Sets the selection to a single item.
        /// </summary>
        public void SetSingle(string id)
        {
            Clear();
            Add(id);
            RangeAnchorId = id;
        }

        /// <summary>
        /// Sets a range selection from anchor to target.
        /// </summary>
        public void SetRange(string anchorId, string targetId, IEnumerable<string> allIds)
        {
            var allIdsList = allIds.ToList();
            var anchorIndex = allIdsList.IndexOf(anchorId);
            var targetIndex = allIdsList.IndexOf(targetId);

            if (anchorIndex == -1 || targetIndex == -1)
                return;

            Clear();
            RangeAnchorId = anchorId;
            IsRangeSelection = true;

            var start = Math.Min(anchorIndex, targetIndex);
            var end = Math.Max(anchorIndex, targetIndex);

            for (int i = start; i <= end; i++)
            {
                if (i < allIdsList.Count)
                {
                    Add(allIdsList[i]);
                }
            }
        }
    }
}

