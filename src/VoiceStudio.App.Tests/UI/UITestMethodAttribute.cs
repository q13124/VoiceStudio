using System;
using System.Runtime.InteropServices;
using System.Threading;
using Microsoft.Windows.ApplicationModel.DynamicDependency;
using Microsoft.UI.Dispatching;
using Microsoft.UI.Xaml.Hosting;
using Microsoft.VisualStudio.TestTools.UnitTesting;
using WinRT;

namespace VoiceStudio.App.Tests.UI
{
  /// <summary>
  /// Executes the test method on an STA thread for WinUI/XAML component creation.
  /// </summary>
  [AttributeUsage(AttributeTargets.Method, AllowMultiple = false)]
  public sealed class UITestMethodAttribute : TestMethodAttribute
  {
    private const uint WindowsAppSdkMajorMinorVersion = 0x00010008; // Windows App SDK 1.8

    private static readonly object BootstrapLock = new();
    private static bool BootstrapInitialized;

    public override TestResult[] Execute(ITestMethod testMethod)
    {
      if (testMethod == null)
      {
        throw new ArgumentNullException(nameof(testMethod));
      }

      TestResult[]? results = null;
      Exception? exception = null;

      var thread = new Thread(() =>
      {
        object? dispatcherQueueController = null;
        WindowsXamlManager? xamlManager = null;

        try
        {
          ComWrappersSupport.InitializeComWrappers();
          EnsureWindowsAppSdkBootstrap();
          dispatcherQueueController = EnsureDispatcherQueue();
          xamlManager = WindowsXamlManager.InitializeForCurrentThread();
          results = base.Execute(testMethod);
        }
        catch (Exception ex)
        {
          exception = ex;
        }
        finally
        {
          xamlManager?.Dispose();

          if (dispatcherQueueController != null && Marshal.IsComObject(dispatcherQueueController))
          {
            try
            {
              Marshal.FinalReleaseComObject(dispatcherQueueController);
            }
            catch
            {
              // Best-effort cleanup; tests must not fail due to COM release issues.
            }
          }
        }
      })
      {
        IsBackground = true
      };

      thread.SetApartmentState(ApartmentState.STA);
      thread.Start();
      thread.Join();

      if (exception != null)
      {
        throw new AssertFailedException($"UI test execution failed: {exception}", exception);
      }

      return results ?? Array.Empty<TestResult>();
    }

    private static object? EnsureDispatcherQueue()
    {
      // WinUI 3 objects require a DispatcherQueue on the creating thread.
      if (DispatcherQueue.GetForCurrentThread() != null)
      {
        return null;
      }

      // Use the WinUI 3 API to create the DispatcherQueueController.
      return DispatcherQueueController.CreateOnCurrentThread();
    }

    private static void EnsureWindowsAppSdkBootstrap()
    {
      if (BootstrapInitialized)
      {
        return;
      }

      lock (BootstrapLock)
      {
        if (BootstrapInitialized)
        {
          return;
        }

        Bootstrap.Initialize(WindowsAppSdkMajorMinorVersion);
        BootstrapInitialized = true;
      }
    }
  }
}

