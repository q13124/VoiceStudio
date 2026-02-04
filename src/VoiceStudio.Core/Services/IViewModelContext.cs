using Microsoft.Extensions.Logging;

namespace VoiceStudio.Core.Services
{
  /// <summary>
  /// Ambient context for ViewModels providing logger and UI dispatcher.
  /// Part of TD-004 ViewModel DI migration to eliminate parameterless BaseViewModel().
  /// </summary>
  /// <remarks>
  /// Registered as singleton in DI container.
  /// Provides access to UI thread dispatcher and scoped logging.
  /// </remarks>
  public interface IViewModelContext
  {
    /// <summary>
    /// Logger for ViewModel diagnostic output.
    /// Used by BaseViewModel for error logging and trace output.
    /// </summary>
    ILogger Logger { get; }

    /// <summary>
    /// UI thread dispatcher for marshalling async results to UI.
    /// Required for any ViewModel that updates observable properties from background tasks.
    /// </summary>
    /// <remarks>
    /// Type: Microsoft.UI.Dispatching.DispatcherQueue from WinUI (declared as object here for Core portability)
    /// </remarks>
    object DispatcherQueue { get; }
  }
}