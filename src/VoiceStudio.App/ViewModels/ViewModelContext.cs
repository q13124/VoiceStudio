using Microsoft.Extensions.Logging;
using VoiceStudio.Core.Services;

namespace VoiceStudio.App.ViewModels
{
  /// <summary>
  /// Concrete implementation of IViewModelContext for ViewModel ambient context.
  /// Used when DI is not yet initialized (e.g. BaseViewModel fallback).
  /// </summary>
  public sealed class ViewModelContext : IViewModelContext
  {
    public ILogger Logger { get; }
    public object DispatcherQueue { get; }

    public ViewModelContext(ILogger logger, object dispatcherQueue)
    {
      Logger = logger ?? throw new System.ArgumentNullException(nameof(logger));
      DispatcherQueue = dispatcherQueue ?? throw new System.ArgumentNullException(nameof(dispatcherQueue));
    }
  }
}