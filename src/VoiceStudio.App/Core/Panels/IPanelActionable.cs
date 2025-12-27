using System.Collections.Generic;
using System.Windows.Input;

namespace VoiceStudio.Core.Panels
{
    /// <summary>
    /// Interface for panels that provide context-sensitive header actions.
    /// Implements IDEA 2: Context-Sensitive Action Bar in PanelHost Headers.
    /// </summary>
    public interface IPanelActionable
    {
        /// <summary>
        /// Gets the list of header actions for this panel.
        /// Maximum 4 actions recommended to maintain compactness.
        /// </summary>
        IEnumerable<PanelHeaderAction> GetHeaderActions();
    }

    /// <summary>
    /// Represents a header action button.
    /// </summary>
    public class PanelHeaderAction
    {
        /// <summary>
        /// Icon symbol or emoji for the action.
        /// </summary>
        public string Icon { get; set; } = string.Empty;

        /// <summary>
        /// Action name/tooltip text.
        /// </summary>
        public string Name { get; set; } = string.Empty;

        /// <summary>
        /// Keyboard shortcut hint (e.g., "Ctrl+N").
        /// </summary>
        public string? KeyboardShortcut { get; set; }

        /// <summary>
        /// Command to execute when action is clicked.
        /// </summary>
        public ICommand? Command { get; set; }

        /// <summary>
        /// Whether the action is enabled.
        /// </summary>
        public bool IsEnabled { get; set; } = true;

        /// <summary>
        /// Whether the action is visible.
        /// </summary>
        public bool IsVisible { get; set; } = true;

        /// <summary>
        /// Full tooltip text combining name and shortcut.
        /// </summary>
        public string Tooltip => string.IsNullOrEmpty(KeyboardShortcut)
            ? Name
            : $"{Name} ({KeyboardShortcut})";
    }
}

