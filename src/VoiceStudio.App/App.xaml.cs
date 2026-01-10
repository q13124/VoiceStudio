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
      this.UnhandledException += App_UnhandledException;
      _appStartTime = DateTime.UtcNow;
      _startupProfiler = PerformanceProfiler.Start("Application Startup");
      _startupProfiler.Checkpoint("App Constructor Start");

      this.InitializeComponent();
      _startupProfiler.Checkpoint("InitializeComponent");

      // Initialize service provider
      ServiceProvider.Initialize();
      _startupProfiler.Checkpoint("ServiceProvider.Initialize");
    }

    private void App_UnhandledException(object sender, Microsoft.UI.Xaml.UnhandledExceptionEventArgs e)
    {
      try
      {
        // Write to deterministic location: %LOCALAPPDATA%\VoiceStudio\crashes\
        var crashDir = System.IO.Path.Combine(
          Environment.GetFolderPath(Environment.SpecialFolder.LocalApplicationData),
          "VoiceStudio", "crashes");
        
        System.IO.Directory.CreateDirectory(crashDir);

        // Use timestamp + sequence to preserve crash history
        var timestamp = DateTime.UtcNow.ToString("yyyy-MM-dd_HH-mm-ss-fff");
        var logPath = System.IO.Path.Combine(crashDir, $"crash_{timestamp}.log");

        // Construct detailed crash log
        var sb = new System.Text.StringBuilder();
        sb.AppendLine("═══════════════════════════════════════════════════");
        sb.AppendLine("VoiceStudio Unhandled Exception Report");
        sb.AppendLine("═══════════════════════════════════════════════════");
        sb.AppendLine();
        sb.AppendLine($"Timestamp (UTC): {timestamp}");
        sb.AppendLine($"Process ID: {System.Diagnostics.Process.GetCurrentProcess().Id}");
        sb.AppendLine($"Thread ID: {System.Threading.Thread.CurrentThread.ManagedThreadId}");
        sb.AppendLine();
        
        // Startup stage indicator
        sb.AppendLine("--- Startup Stage ---");
        sb.AppendLine($"App Startup Time: {_appStartTime:yyyy-MM-dd_HH:mm:ss.fff}");
        sb.AppendLine($"Uptime at crash: {(DateTime.UtcNow - _appStartTime).TotalSeconds:F3}s");
        if (_startupProfiler != null)
        {
          sb.AppendLine($"Startup Profiler: Active (within startup phase)");
        }
        sb.AppendLine();

        // Environment
        sb.AppendLine("--- Environment ---");
        sb.AppendLine($"OS: {System.Runtime.InteropServices.RuntimeInformation.OSDescription}");
        sb.AppendLine($".NET Runtime: {System.Runtime.InteropServices.RuntimeInformation.FrameworkDescription}");
        sb.AppendLine($"Working Dir: {Environment.CurrentDirectory}");
        sb.AppendLine();

        // Exception details
        sb.AppendLine("--- Exception Details ---");
        sb.AppendLine($"Exception Type: {e.Exception?.GetType().FullName}");
        sb.AppendLine($"Message: {e.Message}");
        sb.AppendLine($"HResult: 0x{e.Exception?.HResult:X8}");
        sb.AppendLine();

        // Stack trace
        sb.AppendLine("--- Stack Trace ---");
        sb.AppendLine(e.Exception?.StackTrace ?? "(no stack trace)");
        sb.AppendLine();

        // Inner exception (if any)
        if (e.Exception?.InnerException != null)
        {
          sb.AppendLine("--- Inner Exception ---");
          sb.AppendLine($"Type: {e.Exception.InnerException.GetType().FullName}");
          sb.AppendLine($"Message: {e.Exception.InnerException.Message}");
          sb.AppendLine($"Stack Trace: {e.Exception.InnerException.StackTrace}");
          sb.AppendLine();
        }

        sb.AppendLine("═══════════════════════════════════════════════════");

        // Write to file
        System.IO.File.WriteAllText(logPath, sb.ToString());

        // Also write symbolic link to "latest crash" for easy access
        var latestLink = System.IO.Path.Combine(crashDir, "latest.log");
        try
        {
          if (System.IO.File.Exists(latestLink))
          {
            System.IO.File.Delete(latestLink);
          }
          System.IO.File.WriteAllText(latestLink, $"See: {logPath}");
        }
        catch { /* Best effort */ }

        // Debug output
        Debug.WriteLine($"💥 Unhandled exception logged to: {logPath}");
      }
      catch (Exception logEx)
      {
        // Fallback to debug output if file writing fails
        Debug.WriteLine($"⚠️ Failed to write crash log: {logEx.Message}");
      }
    }

    protected override async void OnLaunched(Microsoft.UI.Xaml.LaunchActivatedEventArgs args)
    {
      _startupProfiler?.Checkpoint("OnLaunched Start");

      var smokeExit = IsSmokeExit(args);

      // Load plugins in background (non-blocking)
      if (!smokeExit)
      {
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
      }

      m_window = new MainWindow();
      MainWindowInstance = m_window;
      _startupProfiler?.Checkpoint("MainWindow Created");

      m_window.Activate();
      _startupProfiler?.Checkpoint("MainWindow Activated");

      if (smokeExit)
      {
        _startupProfiler?.Checkpoint("SmokeExit Requested");

        // Give WinUI a moment to finish initial render and resource resolution.
        await Task.Delay(250);

        try
        {
          m_window.Close();
        }
        catch
        {
          try
          {
            Microsoft.UI.Xaml.Application.Current.Exit();
          }
          catch
          {
            // Best effort shutdown; process exit will end the smoke run.
          }
        }
      }

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

    private static bool IsSmokeExit(Microsoft.UI.Xaml.LaunchActivatedEventArgs args)
    {
      try
      {
        var arguments = args?.Arguments ?? string.Empty;
        if (arguments.IndexOf("--smoke-exit", StringComparison.OrdinalIgnoreCase) >= 0)
        {
          return true;
        }

        var env = Environment.GetEnvironmentVariable("VOICE_STUDIO_SMOKE_EXIT");
        if (string.IsNullOrWhiteSpace(env))
        {
          return false;
        }

        return env.Equals("1", StringComparison.OrdinalIgnoreCase)
            || env.Equals("true", StringComparison.OrdinalIgnoreCase);
      }
      catch
      {
        return false;
      }
    }

    // WinUI 3 doesn't have OnSuspending - cleanup happens on app exit
    // ServiceProvider cleanup should be handled elsewhere if needed

    private Window? m_window;
  }
}

