using System;
using System.Collections.Generic;
using Microsoft.Extensions.DependencyInjection;
using Microsoft.Extensions.Logging.Abstractions;
using Microsoft.UI.Dispatching;
using VoiceStudio.Core.Panels;
using VoiceStudio.Core.Services;
using VoiceStudio.App.UseCases;
using VoiceStudio.App.ViewModels;

namespace VoiceStudio.App.Services
{
    /// <summary>
    /// Static DI facade used by ServiceProvider shim and Views/ViewModels.
    /// Initialize() must be called at app startup (e.g. from App constructor via ServiceProvider.Initialize()).
    /// </summary>
    public static class AppServices
    {
        private static IServiceProvider? _provider;
        private static ToastNotificationService? _toastOverride;

        /// <summary>
        /// Sets the root service provider (e.g. from a built ServiceCollection).
        /// </summary>
        public static void Initialize(IServiceProvider provider)
        {
            _provider = provider ?? throw new ArgumentNullException(nameof(provider));
        }

        /// <summary>
        /// Builds a minimal DI container and sets it as the provider.
        /// Called by ServiceProvider.Initialize() when no external provider is supplied.
        /// </summary>
        public static void Initialize()
        {
            var services = new ServiceCollection();

            // Config and backend
            services.AddSingleton(new BackendClientConfig { BaseUrl = "http://localhost:8001", WebSocketUrl = "ws://localhost:8001/ws" });
            services.AddSingleton<IBackendClient, BackendClient>();

            // Use cases
            services.AddSingleton<IProfilesUseCase, ProfilesUseCase>();

            // ViewModel context (factory: dispatcher may be null at startup; fallback when resolved)
            services.AddSingleton<IViewModelContext>(sp =>
            {
                var dispatcher = DispatcherQueue.GetForCurrentThread()
                    ?? Microsoft.UI.Dispatching.DispatcherQueueController.CreateOnDedicatedThread().DispatcherQueue;
                return new ViewModelContext(NullLogger.Instance, dispatcher);
            });

            // Core app services (register implementations; order may matter for dependencies)
            services.AddSingleton<ISettingsService, SettingsService>();
            services.AddSingleton<IUpdateService, UpdateService>();
            services.AddSingleton<IPanelRegistry, PanelRegistry>();
            services.AddSingleton<PanelStateService>();
            services.AddSingleton<INavigationService, NavigationService>();
            services.AddSingleton<IErrorDialogService, ErrorDialogService>();
            services.AddSingleton<IErrorLoggingService, ErrorLoggingService>();
            services.AddSingleton<IHelpOverlayService, HelpOverlayService>();
            services.AddSingleton<IAudioPlayerService, AudioPlayerService>();
            services.AddSingleton<OperationQueueService>();
            services.AddSingleton<StatePersistenceService>();
            services.AddSingleton<StateCacheService>();
            services.AddSingleton<GracefulDegradationService>();
            services.AddSingleton<PluginManager>();
            services.AddSingleton<RealTimeQualityService>();
            services.AddSingleton<ToastNotificationService>();
            services.AddSingleton<MultiSelectService>();
            services.AddSingleton<DragDropVisualFeedbackService>();
            services.AddSingleton<ContextMenuService>();
            services.AddSingleton<UndoRedoService>();
            services.AddSingleton<RecentProjectsService>();
            services.AddSingleton<ToolbarConfigurationService>();
            services.AddSingleton<StatusBarActivityService>();
            services.AddSingleton<KeyboardShortcutService>();
            services.AddSingleton<CollaborationService>();
            services.AddSingleton<IFeatureFlagsService, FeatureFlagsService>();
            services.AddSingleton<IErrorPresentationService, ErrorPresentationService>();
            services.AddSingleton<IAnalyticsService, AnalyticsService>();
            services.AddSingleton<EngineManager>();

            // ITelemetryService: stub when no dedicated implementation (GAP-003 follow-up can add real impl)
            services.AddSingleton<ITelemetryService, TelemetryServiceStub>();

            // IProjectRepository: JSON-based local storage (local-first, no cloud)
            services.AddSingleton<IProjectRepository, JsonProjectRepository>();

            // ISecretsService: use available implementation
            services.AddSingleton<ISecretsService, DevVaultSecretsService>();

            _provider = services.BuildServiceProvider();
        }

        public static T? GetService<T>() where T : class => (T?)_provider?.GetService(typeof(T));
        public static T GetRequiredService<T>() where T : class =>
            GetService<T>() ?? throw new InvalidOperationException($"Service not registered: {typeof(T).FullName}");

        public static IViewModelContext GetViewModelContext() => GetRequiredService<IViewModelContext>();

        public static void RegisterToastNotificationService(ToastNotificationService service) => _toastOverride = service;

        // Typed accessors (forward to GetService / GetRequiredService)
        public static IBackendClient GetBackendClient() => GetRequiredService<IBackendClient>();
        public static IAudioPlayerService GetAudioPlayerService() => GetRequiredService<IAudioPlayerService>();
        public static IErrorDialogService GetErrorDialogService() => GetRequiredService<IErrorDialogService>();
        public static IErrorLoggingService GetErrorLoggingService() => GetRequiredService<IErrorLoggingService>();
        public static IErrorLoggingService? TryGetErrorLoggingService() => GetService<IErrorLoggingService>();
        public static OperationQueueService GetOperationQueueService() => GetRequiredService<OperationQueueService>();
        public static StatePersistenceService GetStatePersistenceService() => GetRequiredService<StatePersistenceService>();
        public static StateCacheService GetStateCacheService() => GetRequiredService<StateCacheService>();
        public static GracefulDegradationService GetGracefulDegradationService() => GetRequiredService<GracefulDegradationService>();
        public static IUpdateService GetUpdateService() => GetRequiredService<IUpdateService>();
        public static ISettingsService GetSettingsService() => GetRequiredService<ISettingsService>();
        public static PluginManager GetPluginManager() => GetRequiredService<PluginManager>();
        public static IPanelRegistry GetPanelRegistry() => GetRequiredService<IPanelRegistry>();
        public static IHelpOverlayService GetHelpOverlayService() => GetRequiredService<IHelpOverlayService>();
        public static RealTimeQualityService GetRealTimeQualityService() => GetRequiredService<RealTimeQualityService>();
        public static PanelStateService GetPanelStateService() => GetRequiredService<PanelStateService>();
        public static ToastNotificationService GetToastNotificationService() => _toastOverride ?? GetRequiredService<ToastNotificationService>();
        public static ToastNotificationService? TryGetToastNotificationService() => _toastOverride ?? GetService<ToastNotificationService>();
        public static MultiSelectService GetMultiSelectService() => GetRequiredService<MultiSelectService>();
        public static MultiSelectService? TryGetMultiSelectService() => GetService<MultiSelectService>();
        public static DragDropVisualFeedbackService GetDragDropVisualFeedbackService() => GetRequiredService<DragDropVisualFeedbackService>();
        public static DragDropVisualFeedbackService? TryGetDragDropVisualFeedbackService() => GetService<DragDropVisualFeedbackService>();
        public static ContextMenuService GetContextMenuService() => GetRequiredService<ContextMenuService>();
        public static ContextMenuService? TryGetContextMenuService() => GetService<ContextMenuService>();
        public static UndoRedoService GetUndoRedoService() => GetRequiredService<UndoRedoService>();
        public static UndoRedoService? TryGetUndoRedoService() => GetService<UndoRedoService>();
        public static RecentProjectsService GetRecentProjectsService() => GetRequiredService<RecentProjectsService>();
        public static RecentProjectsService? TryGetRecentProjectsService() => GetService<RecentProjectsService>();
        public static ToolbarConfigurationService GetToolbarConfigurationService() => GetRequiredService<ToolbarConfigurationService>();
        public static ToolbarConfigurationService? TryGetToolbarConfigurationService() => GetService<ToolbarConfigurationService>();
        public static StatusBarActivityService GetStatusBarActivityService() => GetRequiredService<StatusBarActivityService>();
        public static StatusBarActivityService? TryGetStatusBarActivityService() => GetService<StatusBarActivityService>();
        public static KeyboardShortcutService GetKeyboardShortcutService() => GetRequiredService<KeyboardShortcutService>();
        public static KeyboardShortcutService? TryGetKeyboardShortcutService() => GetService<KeyboardShortcutService>();
        public static CollaborationService GetCollaborationService() => GetRequiredService<CollaborationService>();
        public static CollaborationService? TryGetCollaborationService() => GetService<CollaborationService>();
        public static IFeatureFlagsService GetFeatureFlagsService() => GetRequiredService<IFeatureFlagsService>();
        public static IFeatureFlagsService? TryGetFeatureFlagsService() => GetService<IFeatureFlagsService>();
        public static IErrorPresentationService GetErrorPresentationService() => GetRequiredService<IErrorPresentationService>();
        public static IErrorPresentationService? TryGetErrorPresentationService() => GetService<IErrorPresentationService>();
        public static IAnalyticsService GetAnalyticsService() => GetRequiredService<IAnalyticsService>();
        public static IAnalyticsService? TryGetAnalyticsService() => GetService<IAnalyticsService>();
        public static ITelemetryService GetTelemetryService() => GetRequiredService<ITelemetryService>();
        public static ITelemetryService? TryGetTelemetryService() => GetService<ITelemetryService>();
        public static EngineManager GetEngineManager() => GetRequiredService<EngineManager>();
        public static INavigationService GetNavigationService() => GetRequiredService<INavigationService>();
        public static INavigationService? TryGetNavigationService() => GetService<INavigationService>();
        public static ISecretsService GetSecretsService() => GetRequiredService<ISecretsService>();
        public static ISecretsService? TryGetSecretsService() => GetService<ISecretsService>();
        public static IProfilesUseCase GetProfilesUseCase() => GetRequiredService<IProfilesUseCase>();
        public static IProfilesUseCase? TryGetProfilesUseCase() => GetService<IProfilesUseCase>();
        public static IProjectRepository GetProjectRepository() => GetRequiredService<IProjectRepository>();
        public static IProjectRepository? TryGetProjectRepository() => GetService<IProjectRepository>();
    }

    /// <summary>
    /// Stub for ITelemetryService when no dedicated implementation is registered.
    /// </summary>
    internal sealed class TelemetryServiceStub : ITelemetryService
    {
        public void TrackEvent(string eventName, IDictionary<string, object>? properties = null) { }
        public void TrackMetric(string metricName, double value, IDictionary<string, string>? dimensions = null) { }
        public void TrackException(Exception exception, IDictionary<string, string>? properties = null) { }
        public IDisposable TrackOperation(string operationName) => new TelemetryOperationStub();
        public void Flush() { }
    }

    internal sealed class TelemetryOperationStub : IDisposable
    {
        public void Dispose() { }
    }
}
