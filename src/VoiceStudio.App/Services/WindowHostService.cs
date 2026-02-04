using Microsoft.UI.Windowing;
using Microsoft.UI.Xaml;
using Microsoft.UI.Xaml.Controls;
using System;
using System.Collections.Generic;

namespace VoiceStudio.App.Services
{
  /// <summary>
  /// Service for managing floating windows that host panels.
  /// </summary>
  public class WindowHostService
  {
    private readonly Dictionary<string, Window> _floatingWindows = new();
    private readonly Dictionary<string, UIElement> _panelContent = new();

    /// <summary>
    /// Creates a floating window for a panel.
    /// </summary>
    public Window CreateFloatingWindow(string panelId, string title, UIElement content, double width = 800, double height = 600)
    {
      // Close existing window if present
      if (_floatingWindows.TryGetValue(panelId, out var existingWindow))
      {
        existingWindow.Close();
      }

      var host = new Controls.FloatingWindowHost
      {
        PanelId = panelId,
        Content = content
      };
      var window = new Window
      {
        Title = title,
        Content = host
      };

      // Set window size
      var appWindow = window.AppWindow;
      appWindow.Resize(new Windows.Graphics.SizeInt32((int)width, (int)height));

      // Center window
      var displayArea = DisplayArea.GetFromWindowId(appWindow.Id, DisplayAreaFallback.Nearest);
      if (displayArea != null)
      {
        var centerX = displayArea.WorkArea.X + ((displayArea.WorkArea.Width - (int)width) / 2);
        var centerY = displayArea.WorkArea.Y + ((displayArea.WorkArea.Height - (int)height) / 2);
        appWindow.Move(new Windows.Graphics.PointInt32(centerX, centerY));
      }

      _floatingWindows[panelId] = window;
      _panelContent[panelId] = content;

      window.Closed += (_, _) =>
      {
        _floatingWindows.Remove(panelId);
        _panelContent.Remove(panelId);
      };

      window.Activate();
      return window;
    }

    /// <summary>
    /// Closes a floating window by panel ID.
    /// </summary>
    public void CloseFloatingWindow(string panelId)
    {
      if (_floatingWindows.TryGetValue(panelId, out var window))
      {
        window.Close();
      }
    }

    /// <summary>
    /// Checks if a panel is currently in a floating window.
    /// </summary>
    public bool IsFloating(string panelId)
    {
      return _floatingWindows.ContainsKey(panelId);
    }

    /// <summary>
    /// Gets all floating windows.
    /// </summary>
    public IEnumerable<Window> GetFloatingWindows()
    {
      return _floatingWindows.Values;
    }
  }
}