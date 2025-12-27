using System.Collections.Generic;
using VoiceStudio.App.Controls;

namespace VoiceStudio.App.Services
{
    /// <summary>
    /// Service interface for showing contextual help overlays in panels.
    /// </summary>
    public interface IHelpOverlayService
    {
        /// <summary>
        /// Shows a help overlay with the specified content.
        /// </summary>
        /// <param name="overlay">The HelpOverlay control to configure.</param>
        /// <param name="title">The title of the help overlay.</param>
        /// <param name="helpText">The main help text.</param>
        /// <param name="shortcuts">Optional keyboard shortcuts to display.</param>
        /// <param name="tips">Optional tips to display.</param>
        void ShowHelp(HelpOverlay overlay, string title, string helpText, 
            IEnumerable<KeyboardShortcut>? shortcuts = null, 
            IEnumerable<string>? tips = null);
    }
}

