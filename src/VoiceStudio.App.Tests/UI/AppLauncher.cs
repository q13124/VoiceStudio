using System;
using System.Diagnostics;
using System.IO;
using System.Threading.Tasks;
using FlaUI.Core;
using FlaUI.Core.AutomationElements;
using FlaUI.UIA3;

namespace VoiceStudio.App.Tests.UI
{
  /// <summary>
  /// Helper class for launching and managing the VoiceStudio application during UI automation tests.
  /// Provides methods to start the application, wait for the main window, and capture screenshots.
  /// </summary>
  public class AppLauncher : IDisposable
  {
    private Application? _application;
    private UIA3Automation? _automation;
    private Window? _mainWindow;
    private bool _disposed;

    /// <summary>
    /// Default timeout for waiting for the application to start.
    /// </summary>
    public static readonly TimeSpan DefaultStartupTimeout = TimeSpan.FromSeconds(30);

    /// <summary>
    /// Default polling interval when waiting for elements.
    /// </summary>
    public static readonly TimeSpan DefaultPollingInterval = TimeSpan.FromMilliseconds(500);

    /// <summary>
    /// Gets the main window of the application, if available.
    /// </summary>
    public Window? MainWindow => _mainWindow;

    /// <summary>
    /// Gets the FlaUI automation instance.
    /// </summary>
    public UIA3Automation? Automation => _automation;

    /// <summary>
    /// Gets whether the application is currently running.
    /// </summary>
    public bool IsRunning => _application != null && !_application.HasExited;

    /// <summary>
    /// Launches the VoiceStudio application and waits for the main window to appear.
    /// </summary>
    /// <param name="exePath">Path to the VoiceStudio executable. If null, uses GetApplicationPath().</param>
    /// <param name="timeout">Timeout for waiting for the main window. Defaults to 30 seconds.</param>
    /// <returns>The main window AutomationElement.</returns>
    /// <exception cref="FileNotFoundException">Thrown if the executable is not found.</exception>
    /// <exception cref="TimeoutException">Thrown if the main window doesn't appear within the timeout.</exception>
    public async Task<Window> LaunchAsync(string? exePath = null, TimeSpan? timeout = null)
    {
      var path = exePath ?? GetApplicationPath();
      
      if (!File.Exists(path))
      {
        throw new FileNotFoundException($"VoiceStudio executable not found at: {path}", path);
      }

      _automation = new UIA3Automation();
      _application = Application.Launch(path);
      
      _mainWindow = await WaitForMainWindowAsync(timeout);
      return _mainWindow;
    }

    /// <summary>
    /// Attaches to an already running VoiceStudio process.
    /// </summary>
    /// <param name="processId">The process ID to attach to.</param>
    /// <param name="timeout">Timeout for waiting for the main window.</param>
    /// <returns>The main window AutomationElement.</returns>
    public async Task<Window> AttachAsync(int processId, TimeSpan? timeout = null)
    {
      _automation = new UIA3Automation();
      _application = Application.Attach(processId);
      
      _mainWindow = await WaitForMainWindowAsync(timeout);
      return _mainWindow;
    }

    /// <summary>
    /// Waits for the main window to become available.
    /// </summary>
    /// <param name="timeout">Maximum time to wait. Defaults to 30 seconds.</param>
    /// <returns>The main window once available.</returns>
    /// <exception cref="TimeoutException">Thrown if the window doesn't appear within the timeout.</exception>
    public async Task<Window> WaitForMainWindowAsync(TimeSpan? timeout = null)
    {
      var effectiveTimeout = timeout ?? DefaultStartupTimeout;
      var sw = Stopwatch.StartNew();

      while (sw.Elapsed < effectiveTimeout)
      {
        try
        {
          var window = _application?.GetMainWindow(_automation);
          if (window != null && window.IsAvailable)
          {
            _mainWindow = window;
            return window;
          }
        }
        // ALLOWED: empty catch - polling pattern, window may not be ready yet
        catch
        {
          // Window not ready yet, continue waiting
        }

        await Task.Delay(DefaultPollingInterval);
      }

      throw new TimeoutException(
        $"Main window did not appear within {effectiveTimeout.TotalSeconds} seconds. " +
        $"Application running: {IsRunning}");
    }

    /// <summary>
    /// Captures a screenshot of the application window and saves it to the specified path.
    /// </summary>
    /// <param name="filePath">The path where the screenshot will be saved.</param>
    /// <returns>True if the screenshot was captured successfully, false otherwise.</returns>
    public bool CaptureScreenshot(string filePath)
    {
      try
      {
        if (_mainWindow == null || !_mainWindow.IsAvailable)
        {
          return false;
        }

        var capture = _mainWindow.Capture();
        if (capture == null)
        {
          return false;
        }

        // Ensure directory exists
        var directory = Path.GetDirectoryName(filePath);
        if (!string.IsNullOrEmpty(directory))
        {
          Directory.CreateDirectory(directory);
        }

        capture.Save(filePath);
        return true;
      }
      catch
      {
        return false;
      }
    }

    /// <summary>
    /// Gets the path to the VoiceStudio executable.
    /// Searches in common build output locations relative to the test assembly.
    /// </summary>
    /// <returns>The path to VoiceStudio.exe.</returns>
    public static string GetApplicationPath()
    {
      // Get the directory of the test assembly
      var testAssemblyPath = typeof(AppLauncher).Assembly.Location;
      var testDir = Path.GetDirectoryName(testAssemblyPath) ?? ".";

      // Try common build output paths
      var searchPaths = new[]
      {
        // Debug/Release builds relative to test project
        Path.Combine(testDir, "..", "..", "..", "..", "VoiceStudio.App", "bin", "x64", "Debug", "net8.0-windows10.0.19041.0", "VoiceStudio.exe"),
        Path.Combine(testDir, "..", "..", "..", "..", "VoiceStudio.App", "bin", "x64", "Release", "net8.0-windows10.0.19041.0", "VoiceStudio.exe"),
        // Direct sibling path
        Path.Combine(testDir, "VoiceStudio.exe"),
        // From solution root
        Path.Combine(testDir, "..", "..", "..", "..", "..", "src", "VoiceStudio.App", "bin", "x64", "Debug", "net8.0-windows10.0.19041.0", "VoiceStudio.exe"),
        Path.Combine(testDir, "..", "..", "..", "..", "..", "src", "VoiceStudio.App", "bin", "x64", "Release", "net8.0-windows10.0.19041.0", "VoiceStudio.exe"),
      };

      foreach (var path in searchPaths)
      {
        var normalizedPath = Path.GetFullPath(path);
        if (File.Exists(normalizedPath))
        {
          return normalizedPath;
        }
      }

      // Environment variable override
      var envPath = Environment.GetEnvironmentVariable("VOICESTUDIO_EXE_PATH");
      if (!string.IsNullOrEmpty(envPath) && File.Exists(envPath))
      {
        return envPath;
      }

      // Return default path (will throw FileNotFoundException when launching)
      return Path.Combine(testDir, "VoiceStudio.exe");
    }

    /// <summary>
    /// Closes the application gracefully.
    /// </summary>
    /// <param name="timeout">Maximum time to wait for the application to close.</param>
    /// <returns>True if the application closed successfully, false if it had to be killed.</returns>
    public async Task<bool> CloseAsync(TimeSpan? timeout = null)
    {
      if (_application == null || _application.HasExited)
      {
        return true;
      }

      var effectiveTimeout = timeout ?? TimeSpan.FromSeconds(10);

      try
      {
        // Try to close the main window gracefully
        _mainWindow?.Close();

        // Wait for the process to exit
        var sw = Stopwatch.StartNew();
        while (sw.Elapsed < effectiveTimeout && !_application.HasExited)
        {
          await Task.Delay(100);
        }

        if (!_application.HasExited)
        {
          // Force kill if it didn't close gracefully
          _application.Kill();
          return false;
        }

        return true;
      }
      // ALLOWED: empty catch - test cleanup must not throw
      catch
      {
        // If anything goes wrong, try to kill the process
        try
        {
          _application?.Kill();
        }
        // ALLOWED: empty catch - kill errors during cleanup are acceptable
        catch
        {
          // Ignore kill errors
        }
        return false;
      }
    }

    /// <summary>
    /// Disposes of the AppLauncher, closing the application if it's still running.
    /// </summary>
    public void Dispose()
    {
      Dispose(true);
      GC.SuppressFinalize(this);
    }

    /// <summary>
    /// Disposes of managed and unmanaged resources.
    /// </summary>
    protected virtual void Dispose(bool disposing)
    {
      if (_disposed)
      {
        return;
      }

      if (disposing)
      {
        // Close application synchronously during dispose
        if (_application != null && !_application.HasExited)
        {
          try
          {
            _mainWindow?.Close();
            
            // Give it a moment to close
            var timeout = DateTime.UtcNow.AddSeconds(5);
            while (DateTime.UtcNow < timeout && !_application.HasExited)
            {
              System.Threading.Thread.Sleep(100);
            }

            if (!_application.HasExited)
            {
              _application.Kill();
            }
          }
          // ALLOWED: empty catch - best effort cleanup during test teardown
          catch
          {
            // Best effort cleanup
            // ALLOWED: empty catch - nested cleanup
            try { _application?.Kill(); } catch { }
          }
        }

        _application?.Dispose();
        _automation?.Dispose();
      }

      _application = null;
      _automation = null;
      _mainWindow = null;
      _disposed = true;
    }

    /// <summary>
    /// Finalizer to ensure cleanup.
    /// </summary>
    ~AppLauncher()
    {
      Dispose(false);
    }
  }
}
