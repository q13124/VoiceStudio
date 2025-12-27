using System;
using System.Diagnostics;
using System.Threading.Tasks;
using Microsoft.UI.Xaml;
using VoiceStudio.App.Services;
using VoiceStudio.App.Utilities;

namespace VoiceStudio.App
{
    public partial class App : Application
    {
        private static PerformanceProfiler? _startupProfiler;
        private static DateTime _appStartTime;
        public static Window? MainWindowInstance { get; private set; }

        public App()
        {
            _appStartTime = DateTime.UtcNow;
            _startupProfiler = PerformanceProfiler.Start("Application Startup");
            _startupProfiler.Checkpoint("App Constructor Start");
            
            this.InitializeComponent();
            _startupProfiler.Checkpoint("InitializeComponent");
            
            // Initialize service provider
            ServiceProvider.Initialize();
            _startupProfiler.Checkpoint("ServiceProvider.Initialize");
        }

        protected override async void OnLaunched(Microsoft.UI.Xaml.LaunchActivatedEventArgs args)
        {
            _startupProfiler?.Checkpoint("OnLaunched Start");
            
            // Load plugins in background (non-blocking)
            _ = Task.Run(async () =>
            {
                try
                {
                    var pluginManager = ServiceProvider.GetPluginManager();
                    await pluginManager.LoadPluginsAsync();
                }
                catch
                {
                    // Silently fail - plugins are optional
                }
            });
            
            m_window = new MainWindow();
            MainWindowInstance = m_window;
            _startupProfiler?.Checkpoint("MainWindow Created");
            
            m_window.Activate();
            _startupProfiler?.Checkpoint("MainWindow Activated");
            
            // Log startup performance
            if (_startupProfiler != null)
            {
                var totalTime = _startupProfiler.ElapsedMilliseconds;
                Debug.WriteLine(_startupProfiler.GetReport());
                
                // Target: < 3 seconds
                if (totalTime > 3000)
                {
                    Debug.WriteLine($"⚠️ WARNING: Startup time ({totalTime}ms) exceeds target (3000ms)");
                }
                else
                {
                    Debug.WriteLine($"✅ Startup time: {totalTime}ms (target: <3000ms)");
                }
                
                _startupProfiler.Dispose();
                _startupProfiler = null;
            }
        }

        // WinUI 3 doesn't have OnSuspending - cleanup happens on app exit
        // ServiceProvider cleanup should be handled elsewhere if needed

        private Window? m_window;
    }
}

