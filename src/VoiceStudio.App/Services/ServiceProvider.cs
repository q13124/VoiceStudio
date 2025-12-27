using System;
using System.Threading.Tasks;
using VoiceStudio.Core.Services;
using VoiceStudio.Core.Panels;

namespace VoiceStudio.App.Services
{
    /// <summary>
    /// Simple service provider for dependency injection.
    /// Can be upgraded to Microsoft.Extensions.DependencyInjection later.
    /// </summary>
    public static class ServiceProvider
    {
        private static IBackendClient? _backendClient;
        private static IAudioPlayerService? _audioPlayerService;
        private static IErrorDialogService? _errorDialogService;
        private static IErrorLoggingService? _errorLoggingService;
        private static OperationQueueService? _operationQueueService;
        private static StatePersistenceService? _statePersistenceService;
        private static StateCacheService? _stateCacheService;
        private static GracefulDegradationService? _gracefulDegradationService;
        private static IUpdateService? _updateService;
        private static ISettingsService? _settingsService;
        private static IHelpOverlayService? _helpOverlayService;
        private static PluginManager? _pluginManager;
        private static VoiceStudio.Core.Panels.PanelRegistry? _panelRegistry;
        private static RealTimeQualityService? _realTimeQualityService;
        private static PanelStateService? _panelStateService;
        private static ToastNotificationService? _toastNotificationService;
        private static MultiSelectService? _multiSelectService;
        private static DragDropVisualFeedbackService? _dragDropVisualFeedbackService;
        private static ContextMenuService? _contextMenuService;
        private static UndoRedoService? _undoRedoService;
        private static RecentProjectsService? _recentProjectsService;
        private static ToolbarConfigurationService? _toolbarConfigurationService;
        private static StatusBarActivityService? _statusBarActivityService;
        private static KeyboardShortcutService? _keyboardShortcutService;
        private static CollaborationService? _collaborationService;
        private static IFeatureFlagsService? _featureFlagsService;
        private static IErrorPresentationService? _errorPresentationService;
        private static INavigationService? _navigationService;
        private static ISecretsService? _secretsService;
        private static IAnalyticsService? _analyticsService;
        private static bool _initialized = false;

        /// <summary>
        /// Helper method to initialize a service with error handling and logging.
        /// Reduces code duplication in Initialize() method.
        /// </summary>
        private static void InitializeService<T>(
            Func<T> factory,
            Action<T> setter,
            string serviceName) where T : class
        {
            try
            {
                var service = factory();
                setter(service);
                _errorLoggingService?.LogInfo($"{serviceName} initialized", "ServiceProvider");
            }
            catch (Exception ex)
            {
                _errorLoggingService?.LogError(ex, $"Failed to initialize {serviceName}");
            }
        }

        public static void Initialize()
        {
            if (_initialized)
                return;

            // Create BackendClient with default configuration
            var config = new BackendClientConfig
            {
                BaseUrl = "http://localhost:8000",
                WebSocketUrl = "ws://localhost:8000/ws",
                RequestTimeout = TimeSpan.FromSeconds(30)
            };

            _backendClient = new BackendClientAdapter(config);
            _audioPlayerService = new AudioPlayerService();
            
            // Initialize error services first (needed for logging)
            _errorLoggingService = new ErrorLoggingService();
            _errorDialogService = new ErrorDialogService(_errorLoggingService);
            
            // Initialize AnalyticsService after error services (may use error logging)
            InitializeService(
                () => new AnalyticsService(),
                service => _analyticsService = service,
                "AnalyticsService");
            
            // Initialize new services with error handling and logging using helper method
            InitializeService(
                () => new OperationQueueService(),
                service => _operationQueueService = service,
                "OperationQueueService");

            InitializeService(
                () => new StatePersistenceService(),
                service => _statePersistenceService = service,
                "StatePersistenceService");

            InitializeService(
                () => new StateCacheService(),
                service => _stateCacheService = service,
                "StateCacheService");

            InitializeService(
                () => new GracefulDegradationService(),
                service => _gracefulDegradationService = service,
                "GracefulDegradationService");

            InitializeService(
                () => new UpdateService(),
                service => _updateService = service,
                "UpdateService");

            InitializeService(
                () => new SettingsService(_backendClient),
                service => _settingsService = service,
                "SettingsService");

            InitializeService(
                () => new HelpOverlayService(),
                service => _helpOverlayService = service,
                "HelpOverlayService");

            InitializeService(
                () => new RealTimeQualityService(_backendClient),
                service => _realTimeQualityService = service,
                "RealTimeQualityService");

            InitializeService(
                () => new PanelStateService(_settingsService),
                service => _panelStateService = service,
                "PanelStateService");

            InitializeService(
                () => new MultiSelectService(),
                service => _multiSelectService = service,
                "MultiSelectService");

            InitializeService(
                () => new DragDropVisualFeedbackService(),
                service => _dragDropVisualFeedbackService = service,
                "DragDropVisualFeedbackService");

            InitializeService(
                () => new ContextMenuService(),
                service => _contextMenuService = service,
                "ContextMenuService");

            InitializeService(
                () => new UndoRedoService(),
                service => _undoRedoService = service,
                "UndoRedoService");

            InitializeService(
                () => new RecentProjectsService(),
                service => _recentProjectsService = service,
                "RecentProjectsService");

            InitializeService(
                () => new ToolbarConfigurationService(),
                service => _toolbarConfigurationService = service,
                "ToolbarConfigurationService");

            // StatusBarActivityService needs special handling (calls StartMonitoring)
            try
            {
                _statusBarActivityService = new StatusBarActivityService(_backendClient, _operationQueueService);
                _statusBarActivityService.StartMonitoring();
                _errorLoggingService?.LogInfo("StatusBarActivityService initialized", "ServiceProvider");
            }
            catch (Exception ex)
            {
                _errorLoggingService?.LogError(ex, "Failed to initialize StatusBarActivityService");
            }

            InitializeService(
                () => new KeyboardShortcutService(),
                service => _keyboardShortcutService = service,
                "KeyboardShortcutService");

            InitializeService(
                () => new CollaborationService(),
                service => _collaborationService = service,
                "CollaborationService");

            InitializeService(
                () => new FeatureFlagsService(),
                service => _featureFlagsService = service,
                "FeatureFlagsService");

            InitializeService(
                () => new ErrorPresentationService(
                    _toastNotificationService,
                    _errorDialogService,
                    _errorLoggingService),
                service => _errorPresentationService = service,
                "ErrorPresentationService");

            try
            {
                if (_panelStateService != null)
                {
                    _navigationService = new NavigationService(_panelStateService);
                    _errorLoggingService?.LogInfo("NavigationService initialized", "ServiceProvider");
                }
            }
            catch (Exception ex)
            {
                _errorLoggingService?.LogError(ex, "Failed to initialize NavigationService");
            }

            try
            {
                // Use Windows Credential Manager in production, DevVault in development
                // Check if running in debug mode or if DEV_VAULT environment variable is set
                var useDevVault = System.Diagnostics.Debugger.IsAttached || 
                                 !string.IsNullOrEmpty(Environment.GetEnvironmentVariable("DEV_VAULT"));
                
                if (useDevVault)
                {
                    _secretsService = new DevVaultSecretsService();
                    _errorLoggingService?.LogInfo("DevVaultSecretsService initialized (development mode)", "ServiceProvider");
                }
                else
                {
                    _secretsService = new WindowsCredentialManagerSecretsService();
                    _errorLoggingService?.LogInfo("WindowsCredentialManagerSecretsService initialized (production mode)", "ServiceProvider");
                }
            }
            catch (Exception ex)
            {
                _errorLoggingService?.LogError(ex, "Failed to initialize SecretsService");
            }
            
            // Initialize panel registry and plugin manager
            _panelRegistry = new VoiceStudio.Core.Panels.PanelRegistry();
            
            // Register all 9 advanced panels
            AdvancedPanelRegistrationService.RegisterAdvancedPanels(_panelRegistry);
            
            _pluginManager = new PluginManager(_panelRegistry, _backendClient);
            
            // Set up operation queue processing when connection is restored
            _ = Task.Run(async () =>
            {
                bool wasConnected = true;
                while (true)
                {
                    try
                    {
                        await Task.Delay(TimeSpan.FromSeconds(5));
                        if (_backendClient == null) break;
                        
                        var isConnected = await _backendClient.CheckHealthAsync();
                        
                        // If connection restored, process queue
                        if (!wasConnected && isConnected && _operationQueueService != null)
                        {
                            await _operationQueueService.ProcessQueueAsync();
                            if (_gracefulDegradationService != null)
                            {
                                _gracefulDegradationService.ExitDegradedMode();
                            }
                        }
                        // If connection lost, enter degraded mode
                        else if (wasConnected && !isConnected && _gracefulDegradationService != null)
                        {
                            _gracefulDegradationService.EnterDegradedMode(
                                "Backend connection lost",
                                "VoiceSynthesis", "Training", "BatchProcessing", "Transcription");
                        }
                        
                        wasConnected = isConnected;
                    }
                    catch
                    {
                        // Silently continue monitoring
                    }
                }
            });
            
            _initialized = true;
        }

        public static IBackendClient GetBackendClient()
        {
            if (!_initialized)
                Initialize();
            
            return _backendClient ?? throw new InvalidOperationException("BackendClient not initialized");
        }

        public static IAudioPlayerService GetAudioPlayerService()
        {
            if (!_initialized)
                Initialize();
            
            return _audioPlayerService ?? throw new InvalidOperationException("AudioPlayerService not initialized");
        }

        public static IErrorDialogService GetErrorDialogService()
        {
            if (!_initialized)
                Initialize();
            
            return _errorDialogService ?? throw new InvalidOperationException("ErrorDialogService not initialized");
        }

        public static IErrorLoggingService GetErrorLoggingService()
        {
            if (!_initialized)
                Initialize();
            
            return _errorLoggingService ?? throw new InvalidOperationException("ErrorLoggingService not initialized");
        }

        /// <summary>
        /// Gets the error logging service if available, returns null if not initialized.
        /// </summary>
        public static IErrorLoggingService? TryGetErrorLoggingService()
        {
            try
            {
                if (!_initialized)
                    Initialize();
                return _errorLoggingService;
            }
            catch
            {
                return null;
            }
        }

        public static OperationQueueService GetOperationQueueService()
        {
            if (!_initialized)
                Initialize();
            
            return _operationQueueService ?? throw new InvalidOperationException("OperationQueueService not initialized");
        }

        public static StatePersistenceService GetStatePersistenceService()
        {
            if (!_initialized)
                Initialize();
            
            return _statePersistenceService ?? throw new InvalidOperationException("StatePersistenceService not initialized");
        }

        public static StateCacheService GetStateCacheService()
        {
            if (!_initialized)
                Initialize();
            
            return _stateCacheService ?? throw new InvalidOperationException("StateCacheService not initialized");
        }

        public static GracefulDegradationService GetGracefulDegradationService()
        {
            if (!_initialized)
                Initialize();
            
            return _gracefulDegradationService ?? throw new InvalidOperationException("GracefulDegradationService not initialized");
        }

        public static IUpdateService GetUpdateService()
        {
            if (!_initialized)
                Initialize();
            
            return _updateService ?? throw new InvalidOperationException("UpdateService not initialized");
        }

        public static ISettingsService GetSettingsService()
        {
            if (!_initialized)
                Initialize();
            
            return _settingsService ?? throw new InvalidOperationException("SettingsService not initialized");
        }

        public static PluginManager GetPluginManager()
        {
            if (!_initialized)
                Initialize();
            
            return _pluginManager ?? throw new InvalidOperationException("PluginManager not initialized");
        }

        public static VoiceStudio.Core.Panels.PanelRegistry GetPanelRegistry()
        {
            if (!_initialized)
                Initialize();
            
            return _panelRegistry ?? throw new InvalidOperationException("PanelRegistry not initialized");
        }

        public static IHelpOverlayService GetHelpOverlayService()
        {
            if (!_initialized)
                Initialize();
            
            return _helpOverlayService ?? throw new InvalidOperationException("HelpOverlayService not initialized");
        }

        public static RealTimeQualityService GetRealTimeQualityService()
        {
            if (!_initialized)
                Initialize();
            
            return _realTimeQualityService ?? throw new InvalidOperationException("RealTimeQualityService not initialized");
        }

        public static PanelStateService GetPanelStateService()
        {
            if (!_initialized)
                Initialize();
            
            return _panelStateService ?? throw new InvalidOperationException("PanelStateService not initialized");
        }

        public static ToastNotificationService GetToastNotificationService()
        {
            return _toastNotificationService ?? throw new InvalidOperationException("ToastNotificationService not initialized. Call RegisterToastNotificationService first.");
        }

        /// <summary>
        /// Safely gets ToastNotificationService, returns null if not available.
        /// Use this for optional service usage.
        /// </summary>
        public static ToastNotificationService? TryGetToastNotificationService()
        {
            try
            {
                return _toastNotificationService;
            }
            catch
            {
                return null;
            }
        }

        public static void RegisterToastNotificationService(ToastNotificationService service)
        {
            _toastNotificationService = service;
            _errorLoggingService?.LogInfo("ToastNotificationService registered", "ServiceProvider");
        }

        public static MultiSelectService GetMultiSelectService()
        {
            if (!_initialized)
                Initialize();
            
            return _multiSelectService ?? throw new InvalidOperationException("MultiSelectService not initialized");
        }

        /// <summary>
        /// Safely gets MultiSelectService, returns null if not available.
        /// Use this for optional service usage.
        /// </summary>
        public static MultiSelectService? TryGetMultiSelectService()
        {
            try
            {
                if (!_initialized)
                    Initialize();
                return _multiSelectService;
            }
            catch
            {
                return null;
            }
        }

        public static DragDropVisualFeedbackService GetDragDropVisualFeedbackService()
        {
            if (!_initialized)
                Initialize();
            
            return _dragDropVisualFeedbackService ?? throw new InvalidOperationException("DragDropVisualFeedbackService not initialized");
        }

        /// <summary>
        /// Safely gets DragDropVisualFeedbackService, returns null if not available.
        /// Use this for optional service usage.
        /// </summary>
        public static DragDropVisualFeedbackService? TryGetDragDropVisualFeedbackService()
        {
            try
            {
                if (!_initialized)
                    Initialize();
                return _dragDropVisualFeedbackService;
            }
            catch
            {
                return null;
            }
        }

        public static ContextMenuService GetContextMenuService()
        {
            if (!_initialized)
                Initialize();
            
            return _contextMenuService ?? throw new InvalidOperationException("ContextMenuService not initialized");
        }

        /// <summary>
        /// Safely gets ContextMenuService, returns null if not available.
        /// Use this for optional service usage.
        /// </summary>
        public static ContextMenuService? TryGetContextMenuService()
        {
            try
            {
                if (!_initialized)
                    Initialize();
                return _contextMenuService;
            }
            catch
            {
                return null;
            }
        }

        public static UndoRedoService GetUndoRedoService()
        {
            if (!_initialized)
                Initialize();
            
            return _undoRedoService ?? throw new InvalidOperationException("UndoRedoService not initialized");
        }

        /// <summary>
        /// Safely gets UndoRedoService, returns null if not available.
        /// Use this for optional service usage.
        /// </summary>
        public static UndoRedoService? TryGetUndoRedoService()
        {
            try
            {
                if (!_initialized)
                    Initialize();
                return _undoRedoService;
            }
            catch
            {
                return null;
            }
        }

        public static RecentProjectsService GetRecentProjectsService()
        {
            if (!_initialized)
                Initialize();
            
            return _recentProjectsService ?? throw new InvalidOperationException("RecentProjectsService not initialized");
        }

        /// <summary>
        /// Safely gets RecentProjectsService, returns null if not available.
        /// Use this for optional service usage.
        /// </summary>
        public static RecentProjectsService? TryGetRecentProjectsService()
        {
            try
            {
                if (!_initialized)
                    Initialize();
                return _recentProjectsService;
            }
            catch
            {
                return null;
            }
        }

        public static ToolbarConfigurationService GetToolbarConfigurationService()
        {
            if (!_initialized)
                Initialize();
            
            return _toolbarConfigurationService ?? throw new InvalidOperationException("ToolbarConfigurationService not initialized");
        }

        /// <summary>
        /// Safely gets ToolbarConfigurationService, returns null if not available.
        /// Use this for optional service usage.
        /// </summary>
        public static ToolbarConfigurationService? TryGetToolbarConfigurationService()
        {
            try
            {
                if (!_initialized)
                    Initialize();
                return _toolbarConfigurationService;
            }
            catch
            {
                return null;
            }
        }

        public static StatusBarActivityService GetStatusBarActivityService()
        {
            if (!_initialized)
                Initialize();
            
            return _statusBarActivityService ?? throw new InvalidOperationException("StatusBarActivityService not initialized");
        }

        /// <summary>
        /// Safely gets StatusBarActivityService, returns null if not available.
        /// Use this for optional service usage.
        /// </summary>
        public static StatusBarActivityService? TryGetStatusBarActivityService()
        {
            try
            {
                if (!_initialized)
                    Initialize();
                return _statusBarActivityService;
            }
            catch
            {
                return null;
            }
        }

        public static KeyboardShortcutService GetKeyboardShortcutService()
        {
            if (!_initialized)
                Initialize();
            
            return _keyboardShortcutService ?? throw new InvalidOperationException("KeyboardShortcutService not initialized");
        }

        /// <summary>
        /// Safely gets KeyboardShortcutService, returns null if not available.
        /// Use this for optional service usage.
        /// </summary>
        public static KeyboardShortcutService? TryGetKeyboardShortcutService()
        {
            try
            {
                if (!_initialized)
                    Initialize();
                return _keyboardShortcutService;
            }
            catch
            {
                return null;
            }
        }

        public static CollaborationService GetCollaborationService()
        {
            if (!_initialized)
                Initialize();
            
            return _collaborationService ?? throw new InvalidOperationException("CollaborationService not initialized");
        }

        /// <summary>
        /// Safely gets CollaborationService, returns null if not available.
        /// Use this for optional service usage.
        /// </summary>
        public static CollaborationService? TryGetCollaborationService()
        {
            try
            {
                if (!_initialized)
                    Initialize();
                return _collaborationService;
            }
            catch
            {
                return null;
            }
        }

        public static IFeatureFlagsService GetFeatureFlagsService()
        {
            if (!_initialized)
                Initialize();
            
            return _featureFlagsService ?? throw new InvalidOperationException("FeatureFlagsService not initialized");
        }

        /// <summary>
        /// Safely gets FeatureFlagsService, returns null if not available.
        /// Use this for optional service usage.
        /// </summary>
        public static IFeatureFlagsService? TryGetFeatureFlagsService()
        {
            try
            {
                if (!_initialized)
                    Initialize();
                return _featureFlagsService;
            }
            catch
            {
                return null;
            }
        }

        public static IErrorPresentationService GetErrorPresentationService()
        {
            if (!_initialized)
                Initialize();
            
            return _errorPresentationService ?? throw new InvalidOperationException("ErrorPresentationService not initialized");
        }

        /// <summary>
        /// Safely gets ErrorPresentationService, returns null if not available.
        /// Use this for optional service usage.
        /// </summary>
        public static IErrorPresentationService? TryGetErrorPresentationService()
        {
            try
            {
                if (!_initialized)
                    Initialize();
                return _errorPresentationService;
            }
            catch
            {
                return null;
            }
        }

        public static IAnalyticsService GetAnalyticsService()
        {
            if (!_initialized)
                Initialize();
            
            return _analyticsService ?? throw new InvalidOperationException("AnalyticsService not initialized");
        }

        /// <summary>
        /// Safely gets AnalyticsService, returns null if not available.
        /// Use this for optional service usage.
        /// </summary>
        public static IAnalyticsService? TryGetAnalyticsService()
        {
            try
            {
                if (!_initialized)
                    Initialize();
                return _analyticsService;
            }
            catch
            {
                return null;
            }
        }

        public static INavigationService GetNavigationService()
        {
            if (!_initialized)
                Initialize();
            
            return _navigationService ?? throw new InvalidOperationException("NavigationService not initialized");
        }

        /// <summary>
        /// Safely gets NavigationService, returns null if not available.
        /// Use this for optional service usage.
        /// </summary>
        public static INavigationService? TryGetNavigationService()
        {
            try
            {
                if (!_initialized)
                    Initialize();
                return _navigationService;
            }
            catch
            {
                return null;
            }
        }

        public static ISecretsService GetSecretsService()
        {
            if (!_initialized)
                Initialize();
            
            return _secretsService ?? throw new InvalidOperationException("SecretsService not initialized");
        }

        /// <summary>
        /// Safely gets SecretsService, returns null if not available.
        /// Use this for optional service usage.
        /// </summary>
        public static ISecretsService? TryGetSecretsService()
        {
            try
            {
                if (!_initialized)
                    Initialize();
                return _secretsService;
            }
            catch
            {
                return null;
            }
        }

        public static void Dispose()
        {
            if (_backendClient is IDisposable backendDisposable)
            {
                backendDisposable.Dispose();
            }
            if (_audioPlayerService is IDisposable audioDisposable)
            {
                audioDisposable.Dispose();
            }
            if (_errorLoggingService is IDisposable errorLoggingDisposable)
            {
                errorLoggingDisposable.Dispose();
            }
            
            _backendClient = null;
            _audioPlayerService = null;
            _errorDialogService = null;
            _errorLoggingService = null;
            _operationQueueService = null;
            _statePersistenceService = null;
            _stateCacheService = null;
            _gracefulDegradationService = null;
            if (_updateService is IDisposable updateDisposable)
            {
                updateDisposable.Dispose();
            }
            _updateService = null;
            _settingsService = null;
            _pluginManager?.UnloadPlugins();
            _pluginManager = null;
            _panelRegistry = null;
            _initialized = false;
        }
    }
}

