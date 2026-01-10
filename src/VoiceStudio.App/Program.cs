using Microsoft.UI.Dispatching;
using Microsoft.UI.Xaml;
using Microsoft.Windows.ApplicationModel.DynamicDependency;
using System;
using System.Runtime.InteropServices;
using System.Threading;
using Windows.ApplicationModel;

namespace VoiceStudio.App
{
  public static class Program
  {
    [DllImport("Microsoft.ui.xaml.dll")]
    private static extern void XamlCheckProcessRequirements();

    private const uint WindowsAppSdkMajorMinorVersion = 0x00010008; // Windows App SDK 1.8

    [STAThread]
    static void Main(string[] args)
    {
      var bootstrapInitialized = false;

      try
      {
        // Force the Windows App SDK bootstrapper to load the bundled (self-contained) runtime
        // instead of the system-installed framework to avoid version mismatches (0xc000027b).
        Environment.SetEnvironmentVariable("WINDOWSAPPSDK_SELFCONTAINED", "1");
        Environment.SetEnvironmentVariable("WINDOWSAPPSDK_RUNTIME_ID", "windows.x64");

        // For unpackaged apps, initialize the Windows App SDK runtime before any WinUI types are activated.
        // This prevents COM "Class not registered" failures in environments where the runtime isn't loaded yet.
        if (!IsPackaged())
        {
          Bootstrap.Initialize(WindowsAppSdkMajorMinorVersion);
          bootstrapInitialized = true;
        }

        XamlCheckProcessRequirements();

        WinRT.ComWrappersSupport.InitializeComWrappers();

        Application.Start((p) =>
        {
          var context = new DispatcherQueueSynchronizationContext(DispatcherQueue.GetForCurrentThread());
          SynchronizationContext.SetSynchronizationContext(context);
          new App();
        });
      }
      catch (Exception ex)
      {
        string logPath = System.IO.Path.Combine(System.AppDomain.CurrentDomain.BaseDirectory, "startup_native_crash.log");
        System.IO.File.WriteAllText(logPath, $"Startup Exception: {ex}\nMessage: {ex.Message}\nStack: {ex.StackTrace}");
        // Re-throw to ensure process exit code reflects failure
        throw;
      }
      finally
      {
        if (bootstrapInitialized)
        {
          Bootstrap.Shutdown();
        }
      }
    }

    private static bool IsPackaged()
    {
      try
      {
        _ = Package.Current;
        return true;
      }
      catch
      {
        return false;
      }
    }
  }
}
