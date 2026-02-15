// VoiceStudio - Panel Architecture: Selection Stack
// Provides browser-like back/forward navigation for selections

using System;
using System.Collections.Generic;

namespace VoiceStudio.Core.State
{
    /// <summary>
    /// Represents a navigation entry in the selection history.
    /// </summary>
    public sealed record SelectionEntry
    {
        /// <summary>
        /// Gets the unique identifier for the selected item.
        /// </summary>
        public required string ItemId { get; init; }

        /// <summary>
        /// Gets the display name of the selected item.
        /// </summary>
        public required string DisplayName { get; init; }

        /// <summary>
        /// Gets the type of item (e.g., "profile", "asset", "job").
        /// </summary>
        public required string ItemType { get; init; }

        /// <summary>
        /// Gets the panel where the selection was made.
        /// </summary>
        public string? SourcePanelId { get; init; }

        /// <summary>
        /// Gets the timestamp when the selection was made.
        /// </summary>
        public DateTimeOffset Timestamp { get; init; } = DateTimeOffset.Now;

        /// <summary>
        /// Gets optional metadata about the selection.
        /// </summary>
        public IReadOnlyDictionary<string, object>? Metadata { get; init; }
    }

    /// <summary>
    /// Interface for selection navigation stack.
    /// </summary>
    public interface ISelectionStack
    {
        /// <summary>
        /// Gets the current selection entry, or null if none.
        /// </summary>
        SelectionEntry? Current { get; }

        /// <summary>
        /// Gets whether back navigation is available.
        /// </summary>
        bool CanGoBack { get; }

        /// <summary>
        /// Gets whether forward navigation is available.
        /// </summary>
        bool CanGoForward { get; }

        /// <summary>
        /// Gets the number of entries in the back history.
        /// </summary>
        int BackCount { get; }

        /// <summary>
        /// Gets the number of entries in the forward history.
        /// </summary>
        int ForwardCount { get; }

        /// <summary>
        /// Pushes a new selection onto the stack, clearing forward history.
        /// </summary>
        /// <param name="entry">The selection entry to push.</param>
        void Push(SelectionEntry entry);

        /// <summary>
        /// Navigates back to the previous selection.
        /// </summary>
        /// <returns>The previous selection entry, or null if none available.</returns>
        SelectionEntry? GoBack();

        /// <summary>
        /// Navigates forward to the next selection.
        /// </summary>
        /// <returns>The next selection entry, or null if none available.</returns>
        SelectionEntry? GoForward();

        /// <summary>
        /// Gets all entries in the back history (most recent first).
        /// </summary>
        IReadOnlyList<SelectionEntry> GetBackHistory();

        /// <summary>
        /// Gets all entries in the forward history (next first).
        /// </summary>
        IReadOnlyList<SelectionEntry> GetForwardHistory();

        /// <summary>
        /// Clears all navigation history.
        /// </summary>
        void Clear();

        /// <summary>
        /// Occurs when navigation happens (back, forward, or new push).
        /// </summary>
        event EventHandler<SelectionNavigationEventArgs>? Navigated;
    }

    /// <summary>
    /// Event arguments for selection navigation.
    /// </summary>
    public sealed class SelectionNavigationEventArgs : EventArgs
    {
        /// <summary>
        /// Gets the previous selection (before navigation).
        /// </summary>
        public SelectionEntry? Previous { get; init; }

        /// <summary>
        /// Gets the current selection (after navigation).
        /// </summary>
        public SelectionEntry? Current { get; init; }

        /// <summary>
        /// Gets the type of navigation that occurred.
        /// </summary>
        public NavigationType NavigationType { get; init; }
    }

    /// <summary>
    /// Type of navigation that occurred.
    /// </summary>
    public enum NavigationType
    {
        /// <summary>New selection was pushed.</summary>
        Push,
        /// <summary>Navigated back.</summary>
        Back,
        /// <summary>Navigated forward.</summary>
        Forward,
        /// <summary>History was cleared.</summary>
        Clear
    }

    /// <summary>
    /// Implementation of a selection navigation stack.
    /// Provides browser-like back/forward navigation for selections.
    /// </summary>
    public sealed class SelectionStack : ISelectionStack
    {
        private readonly Stack<SelectionEntry> _backStack = new();
        private readonly Stack<SelectionEntry> _forwardStack = new();
        private readonly int _maxHistorySize;
        private readonly object _lock = new();
        
        private SelectionEntry? _current;

        /// <summary>
        /// Initializes a new instance of SelectionStack.
        /// </summary>
        /// <param name="maxHistorySize">Maximum number of entries to keep in history.</param>
        public SelectionStack(int maxHistorySize = 50)
        {
            _maxHistorySize = maxHistorySize;
        }

        /// <inheritdoc />
        public SelectionEntry? Current
        {
            get
            {
                lock (_lock) return _current;
            }
        }

        /// <inheritdoc />
        public bool CanGoBack
        {
            get
            {
                lock (_lock) return _backStack.Count > 0;
            }
        }

        /// <inheritdoc />
        public bool CanGoForward
        {
            get
            {
                lock (_lock) return _forwardStack.Count > 0;
            }
        }

        /// <inheritdoc />
        public int BackCount
        {
            get
            {
                lock (_lock) return _backStack.Count;
            }
        }

        /// <inheritdoc />
        public int ForwardCount
        {
            get
            {
                lock (_lock) return _forwardStack.Count;
            }
        }

        /// <inheritdoc />
        public void Push(SelectionEntry entry)
        {
            if (entry == null)
                throw new ArgumentNullException(nameof(entry));

            SelectionEntry? previous;
            
            lock (_lock)
            {
                previous = _current;

                // Don't push if it's the same as current
                if (_current != null && _current.ItemId == entry.ItemId && _current.ItemType == entry.ItemType)
                {
                    return;
                }

                // Move current to back stack if exists
                if (_current != null)
                {
                    _backStack.Push(_current);
                    TrimBackStack();
                }

                // Clear forward history on new selection
                _forwardStack.Clear();

                _current = entry;
            }

            OnNavigated(new SelectionNavigationEventArgs
            {
                Previous = previous,
                Current = entry,
                NavigationType = NavigationType.Push
            });
        }

        /// <inheritdoc />
        public SelectionEntry? GoBack()
        {
            SelectionEntry? previous;
            SelectionEntry? newCurrent;

            lock (_lock)
            {
                if (_backStack.Count == 0)
                    return null;

                previous = _current;

                // Push current to forward stack if exists
                if (_current != null)
                {
                    _forwardStack.Push(_current);
                }

                // Pop from back stack
                newCurrent = _backStack.Pop();
                _current = newCurrent;
            }

            OnNavigated(new SelectionNavigationEventArgs
            {
                Previous = previous,
                Current = newCurrent,
                NavigationType = NavigationType.Back
            });

            return newCurrent;
        }

        /// <inheritdoc />
        public SelectionEntry? GoForward()
        {
            SelectionEntry? previous;
            SelectionEntry? newCurrent;

            lock (_lock)
            {
                if (_forwardStack.Count == 0)
                    return null;

                previous = _current;

                // Push current to back stack if exists
                if (_current != null)
                {
                    _backStack.Push(_current);
                    TrimBackStack();
                }

                // Pop from forward stack
                newCurrent = _forwardStack.Pop();
                _current = newCurrent;
            }

            OnNavigated(new SelectionNavigationEventArgs
            {
                Previous = previous,
                Current = newCurrent,
                NavigationType = NavigationType.Forward
            });

            return newCurrent;
        }

        /// <inheritdoc />
        public IReadOnlyList<SelectionEntry> GetBackHistory()
        {
            lock (_lock)
            {
                return _backStack.ToArray();
            }
        }

        /// <inheritdoc />
        public IReadOnlyList<SelectionEntry> GetForwardHistory()
        {
            lock (_lock)
            {
                return _forwardStack.ToArray();
            }
        }

        /// <inheritdoc />
        public void Clear()
        {
            SelectionEntry? previous;

            lock (_lock)
            {
                previous = _current;
                _backStack.Clear();
                _forwardStack.Clear();
                _current = null;
            }

            OnNavigated(new SelectionNavigationEventArgs
            {
                Previous = previous,
                Current = null,
                NavigationType = NavigationType.Clear
            });
        }

        /// <inheritdoc />
        public event EventHandler<SelectionNavigationEventArgs>? Navigated;

        private void OnNavigated(SelectionNavigationEventArgs args)
        {
            Navigated?.Invoke(this, args);
        }

        private void TrimBackStack()
        {
            // Already locked by caller
            while (_backStack.Count > _maxHistorySize)
            {
                // Remove oldest entries (bottom of stack)
                var items = _backStack.ToArray();
                _backStack.Clear();
                for (int i = items.Length - _maxHistorySize; i < items.Length; i++)
                {
                    _backStack.Push(items[i]);
                }
            }
        }
    }
}
