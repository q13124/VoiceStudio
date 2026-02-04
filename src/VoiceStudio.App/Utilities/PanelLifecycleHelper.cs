using System;
using System.Collections.Generic;
using System.Reflection;
using System.Threading;
using System.Threading.Tasks;
using VoiceStudio.Core.Panels;

namespace VoiceStudio.App.Utilities
{
  /// <summary>
  /// Helper utility for managing panel lifecycle (initialize, activate, deactivate, persist, restore).
  /// </summary>
  public static class PanelLifecycleHelper
  {
    /// <summary>
    /// Checks if a panel implements lifecycle methods.
    /// </summary>
    /// <param name="panel">The panel to check.</param>
    /// <returns>True if the panel implements lifecycle methods.</returns>
    public static bool ImplementsLifecycle(object panel)
    {
      if (panel == null)
        return false;

      var type = panel.GetType();
      return HasMethod(type, "OnInitializeAsync") ||
             HasMethod(type, "OnActivateAsync") ||
             HasMethod(type, "OnDeactivateAsync") ||
             HasMethod(type, "OnPersistAsync") ||
             HasMethod(type, "OnRestoreAsync");
    }

    /// <summary>
    /// Invokes the OnInitializeAsync lifecycle method if it exists.
    /// </summary>
    /// <param name="panel">The panel to initialize.</param>
    /// <param name="cancellationToken">Cancellation token.</param>
    public static async Task InvokeInitializeAsync(object panel, CancellationToken cancellationToken = default)
    {
      await InvokeLifecycleMethodAsync(panel, "OnInitializeAsync", cancellationToken);
    }

    /// <summary>
    /// Invokes the OnActivateAsync lifecycle method if it exists.
    /// </summary>
    /// <param name="panel">The panel to activate.</param>
    /// <param name="cancellationToken">Cancellation token.</param>
    public static async Task InvokeActivateAsync(object panel, CancellationToken cancellationToken = default)
    {
      await InvokeLifecycleMethodAsync(panel, "OnActivateAsync", cancellationToken);
    }

    /// <summary>
    /// Invokes the OnDeactivateAsync lifecycle method if it exists.
    /// </summary>
    /// <param name="panel">The panel to deactivate.</param>
    /// <param name="cancellationToken">Cancellation token.</param>
    public static async Task InvokeDeactivateAsync(object panel, CancellationToken cancellationToken = default)
    {
      await InvokeLifecycleMethodAsync(panel, "OnDeactivateAsync", cancellationToken);
    }

    /// <summary>
    /// Invokes the OnPersistAsync lifecycle method if it exists.
    /// </summary>
    /// <param name="panel">The panel to persist.</param>
    /// <param name="cancellationToken">Cancellation token.</param>
    /// <returns>The persisted state dictionary, or null if not implemented.</returns>
    public static async Task<Dictionary<string, object>?> InvokePersistAsync(object panel, CancellationToken cancellationToken = default)
    {
      var method = FindMethod(panel?.GetType(), "OnPersistAsync", typeof(Task<Dictionary<string, object>>));
      if (method == null)
        return null;

      try
      {
        var task = (Task<Dictionary<string, object>>?)method.Invoke(panel, new object[] { cancellationToken });
        return task != null ? await task : null;
      }
      catch
      {
        return null;
      }
    }

    /// <summary>
    /// Invokes the OnRestoreAsync lifecycle method if it exists.
    /// </summary>
    /// <param name="panel">The panel to restore.</param>
    /// <param name="state">The state dictionary to restore.</param>
    /// <param name="cancellationToken">Cancellation token.</param>
    public static async Task InvokeRestoreAsync(object panel, Dictionary<string, object> state, CancellationToken cancellationToken = default)
    {
      var method = FindMethod(panel?.GetType(), "OnRestoreAsync", typeof(Task), typeof(Dictionary<string, object>), typeof(CancellationToken));
      if (method == null)
        return;

      try
      {
        var task = (Task?)method.Invoke(panel, new object[] { state, cancellationToken });
        if (task != null)
          await task;
      }
      catch
      {
        // Ignore errors during restore
      }
    }

    /// <summary>
    /// Invokes a lifecycle method by name if it exists.
    /// </summary>
    /// <param name="panel">The panel instance.</param>
    /// <param name="methodName">The method name to invoke.</param>
    /// <param name="cancellationToken">Cancellation token.</param>
    public static async Task InvokeLifecycleMethodAsync(object panel, string methodName, CancellationToken cancellationToken = default)
    {
      if (panel == null || string.IsNullOrWhiteSpace(methodName))
        return;

      var method = FindMethod(panel.GetType(), methodName, typeof(Task), typeof(CancellationToken));
      if (method == null)
        return;

      try
      {
        var task = (Task?)method.Invoke(panel, new object[] { cancellationToken });
        if (task != null)
          await task;
      }
      catch
      {
        // Ignore errors during lifecycle method invocation
      }
    }

    /// <summary>
    /// Gets recommended state to persist for a panel.
    /// </summary>
    /// <param name="panel">The panel to get state for.</param>
    /// <returns>A dictionary of recommended state keys and descriptions.</returns>
    public static Dictionary<string, string> GetRecommendedStateKeys(object _)
    {
      return new Dictionary<string, string>
            {
                { "SelectedItem", "Currently selected item ID" },
                { "FilterText", "Current filter/search text" },
                { "SortOrder", "Current sort order" },
                { "ViewMode", "Current view mode (list/grid/details)" },
                { "ScrollPosition", "Scroll position for lists" },
                { "ExpandedSections", "List of expanded section IDs" },
                { "ColumnWidths", "Column widths for table views" }
            };
    }

    /// <summary>
    /// Validates persisted state before restoration.
    /// </summary>
    /// <param name="state">The state dictionary to validate.</param>
    /// <returns>True if state is valid, false otherwise.</returns>
    public static bool ValidateState(Dictionary<string, object> state)
    {
      if (state == null)
        return false;

      // Basic validation - state should not be empty and should contain valid keys
      if (state.Count == 0)
        return false;

      // Check for common invalid values
      foreach (var kvp in state)
      {
        if (kvp.Value == null)
          continue; // Null values are okay

        // Reject extremely large values (potential memory issues)
        if (kvp.Value is string str && str.Length > 10000)
          return false;
      }

      return true;
    }

    private static MethodInfo? FindMethod(Type? type, string methodName, params Type[] parameterTypes)
    {
      if (type == null)
        return null;

      return type.GetMethod(
          methodName,
          BindingFlags.Public | BindingFlags.NonPublic | BindingFlags.Instance,
          null,
          parameterTypes,
          null);
    }

    private static bool HasMethod(Type type, string methodName)
    {
      return type.GetMethod(methodName, BindingFlags.Public | BindingFlags.NonPublic | BindingFlags.Instance) != null;
    }
  }
}