using VoiceStudio.Core.Panels;
using VoiceStudio.Core.Services;
using VoiceStudio.App.UseCases;

namespace VoiceStudio.App.Services
{
  /// <summary>
  /// Compatibility shim that forwards to the DI-backed AppServices.
  /// </summary>
  public static class ServiceProvider
  {
    /// <summary>
    /// Initializes the app service container. Called from App constructor.
    /// </summary>
    public static void Initialize() => AppServices.Initialize();

    public static IBackendClient GetBackendClient() => AppServices.GetBackendClient();
    public static IAudioPlayerService GetAudioPlayerService() => AppServices.GetAudioPlayerService();
    public static IErrorDialogService GetErrorDialogService() => AppServices.GetErrorDialogService();
    public static IErrorLoggingService GetErrorLoggingService() => AppServices.GetErrorLoggingService();
    public static IErrorLoggingService? TryGetErrorLoggingService() => AppServices.TryGetErrorLoggingService();
    public static OperationQueueService GetOperationQueueService() => AppServices.GetOperationQueueService();
    public static StatePersistenceService GetStatePersistenceService() => AppServices.GetStatePersistenceService();
    public static StateCacheService GetStateCacheService() => AppServices.GetStateCacheService();
    public static GracefulDegradationService GetGracefulDegradationService() => AppServices.GetGracefulDegradationService();
    public static IUpdateService GetUpdateService() => AppServices.GetUpdateService();
    public static ISettingsService GetSettingsService() => AppServices.GetSettingsService();
    public static PluginManager GetPluginManager() => AppServices.GetPluginManager();
    public static IPanelRegistry GetPanelRegistry() => AppServices.GetPanelRegistry();
    public static IHelpOverlayService GetHelpOverlayService() => AppServices.GetHelpOverlayService();
    public static RealTimeQualityService GetRealTimeQualityService() => AppServices.GetRealTimeQualityService();
    public static PanelStateService GetPanelStateService() => AppServices.GetPanelStateService();
    public static ToastNotificationService GetToastNotificationService() => AppServices.GetToastNotificationService();
    public static ToastNotificationService? TryGetToastNotificationService()
    {
      try { return AppServices.TryGetToastNotificationService(); }
      catch { return null; }
    }
    public static void RegisterToastNotificationService(ToastNotificationService service) =>
      AppServices.RegisterToastNotificationService(service);
    public static MultiSelectService GetMultiSelectService() => AppServices.GetMultiSelectService();
    public static MultiSelectService? TryGetMultiSelectService()
    {
      try { return AppServices.TryGetMultiSelectService(); }
      catch { return null; }
    }
    public static DragDropVisualFeedbackService GetDragDropVisualFeedbackService() =>
      AppServices.GetDragDropVisualFeedbackService();
    public static DragDropVisualFeedbackService? TryGetDragDropVisualFeedbackService()
    {
      try { return AppServices.TryGetDragDropVisualFeedbackService(); }
      catch { return null; }
    }
    public static ContextMenuService GetContextMenuService() => AppServices.GetContextMenuService();
    public static ContextMenuService? TryGetContextMenuService()
    {
      try { return AppServices.TryGetContextMenuService(); }
      catch { return null; }
    }
    public static UndoRedoService GetUndoRedoService() => AppServices.GetUndoRedoService();
    public static UndoRedoService? TryGetUndoRedoService()
    {
      try { return AppServices.TryGetUndoRedoService(); }
      catch { return null; }
    }
    public static RecentProjectsService GetRecentProjectsService() => AppServices.GetRecentProjectsService();
    public static RecentProjectsService? TryGetRecentProjectsService()
    {
      try { return AppServices.TryGetRecentProjectsService(); }
      catch { return null; }
    }
    public static ToolbarConfigurationService GetToolbarConfigurationService() =>
      AppServices.GetToolbarConfigurationService();
    public static ToolbarConfigurationService? TryGetToolbarConfigurationService() =>
      AppServices.TryGetToolbarConfigurationService();
    public static StatusBarActivityService GetStatusBarActivityService() => AppServices.GetStatusBarActivityService();
    public static StatusBarActivityService? TryGetStatusBarActivityService() =>
      AppServices.TryGetStatusBarActivityService();
    public static KeyboardShortcutService GetKeyboardShortcutService() => AppServices.GetKeyboardShortcutService();
    public static KeyboardShortcutService? TryGetKeyboardShortcutService() => AppServices.TryGetKeyboardShortcutService();
    public static CollaborationService GetCollaborationService() => AppServices.GetCollaborationService();
    public static CollaborationService? TryGetCollaborationService() => AppServices.TryGetCollaborationService();
    public static IFeatureFlagsService GetFeatureFlagsService() => AppServices.GetFeatureFlagsService();
    public static IFeatureFlagsService? TryGetFeatureFlagsService()
    {
      try { return AppServices.TryGetFeatureFlagsService(); }
      catch { return null; }
    }
    public static IErrorPresentationService GetErrorPresentationService() => AppServices.GetErrorPresentationService();
    public static IErrorPresentationService? TryGetErrorPresentationService()
    {
      try { return AppServices.TryGetErrorPresentationService(); }
      catch { return null; }
    }
    public static IAnalyticsService GetAnalyticsService() => AppServices.GetAnalyticsService();
    public static IAnalyticsService? TryGetAnalyticsService()
    {
      try { return AppServices.TryGetAnalyticsService(); }
      catch { return null; }
    }
    public static ITelemetryService GetTelemetryService() => AppServices.GetTelemetryService();
    public static ITelemetryService? TryGetTelemetryService()
    {
      try { return AppServices.TryGetTelemetryService(); }
      catch { return null; }
    }
    public static EngineManager GetEngineManager() => AppServices.GetEngineManager();
    public static INavigationService GetNavigationService() => AppServices.GetNavigationService();
    public static INavigationService? TryGetNavigationService() => AppServices.TryGetNavigationService();
    public static ISecretsService GetSecretsService() => AppServices.GetSecretsService();
    public static ISecretsService? TryGetSecretsService()
    {
      try { return AppServices.TryGetSecretsService(); }
      catch { return null; }
    }
    public static IProfilesUseCase GetProfilesUseCase() => AppServices.GetProfilesUseCase();
    public static IProfilesUseCase? TryGetProfilesUseCase()
    {
      try { return AppServices.TryGetProfilesUseCase(); }
      catch { return null; }
    }
  }
}
