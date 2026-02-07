using System.Collections.Generic;
using VoiceStudio.App.Controls;

namespace VoiceStudio.App.Services
{
  /// <summary>
  /// Service for showing contextual help overlays in panels.
  /// </summary>
  public class HelpOverlayService : IHelpOverlayService
  {
    /// <summary>
    /// Shows a help overlay with the specified content.
    /// </summary>
    /// <param name="overlay">The HelpOverlay control to configure.</param>
    /// <param name="title">The title of the help overlay.</param>
    /// <param name="helpText">The main help text.</param>
    /// <param name="shortcuts">Optional keyboard shortcuts to display.</param>
    /// <param name="tips">Optional tips to display.</param>
    public void ShowHelp(HelpOverlay overlay, string title, string helpText,
        IEnumerable<Controls.KeyboardShortcut>? shortcuts = null,
        IEnumerable<string>? tips = null)
    {
      if (overlay == null)
        return;

      overlay.Title = title;
      overlay.HelpText = helpText;

      // Clear and set shortcuts
      overlay.Shortcuts.Clear();
      if (shortcuts != null)
      {
        foreach (var shortcut in shortcuts)
        {
          overlay.Shortcuts.Add(shortcut);
        }
      }

      // Clear and set tips
      overlay.Tips.Clear();
      if (tips != null)
      {
        foreach (var tip in tips)
        {
          overlay.Tips.Add(tip);
        }
      }

      // Show the overlay
      overlay.Visibility = Microsoft.UI.Xaml.Visibility.Visible;
      overlay.Show();
    }
  }
}