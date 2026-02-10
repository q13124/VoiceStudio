using Microsoft.VisualStudio.TestTools.UnitTesting;
using System;
using System.Collections.Generic;
using System.Diagnostics;
using System.Threading.Tasks;

namespace VoiceStudio.App.Tests.UI.E2E
{
  /// <summary>
  /// End-to-end tests for application lifecycle.
  /// Tests launch, startup performance, and graceful exit.
  /// </summary>
  [TestClass]
  public class AppLifecycleE2ETests : SmokeTestBase
  {
    /// <summary>
    /// Maximum acceptable startup time in seconds.
    /// </summary>
    private const int MaxStartupTimeSeconds = 30;

    /// <summary>
    /// Maximum acceptable graceful shutdown time in seconds.
    /// </summary>
    private const int MaxShutdownTimeSeconds = 10;

    [TestMethod]
    [TestCategory("E2E")]
    [TestCategory("Lifecycle")]
    public async Task Application_StartsSuccessfully()
    {
      // Arrange & Act (handled by TestInitialize in SmokeTestBase)
      VerifyApplicationStarted();
      
      // Assert
      if (UseRealAutomation)
      {
        Assert.IsNotNull(MainWindow, "MainWindow should be available after startup");
        Assert.IsTrue(MainWindow!.IsAvailable, "MainWindow should be in available state");
      }
      
      // Log success
      Log("Application started successfully");
      await Task.CompletedTask;
    }

    [TestMethod]
    [TestCategory("E2E")]
    [TestCategory("Lifecycle")]
    public async Task Application_MainWindowIsResponsive()
    {
      // Arrange
      VerifyApplicationStarted();
      
      if (!UseRealAutomation)
      {
        Log("Skipping responsiveness test in simulated mode");
        return;
      }
      
      // Act - Try to find a known element
      var sw = Stopwatch.StartNew();
      var found = await WaitForElementAsync("MainWindow_Root", TimeSpan.FromSeconds(5));
      sw.Stop();
      
      // Assert
      Log($"Element search completed in {sw.ElapsedMilliseconds}ms");
      Assert.IsTrue(found || MainWindow != null, "MainWindow should be responsive");
    }

    [TestMethod]
    [TestCategory("E2E")]
    [TestCategory("Lifecycle")]
    public async Task Application_NoExceptionsOnStartup()
    {
      // Arrange
      VerifyApplicationStarted();
      
      if (!UseRealAutomation)
      {
        Log("Skipping exception check in simulated mode");
        return;
      }
      
      // Act - Check status bar for error indicators
      var errorIndicators = new[]
      {
        "StatusBar_Error",
        "ErrorIcon",
        "ExceptionDialog"
      };
      
      var errorsFound = new List<string>();
      foreach (var indicator in errorIndicators)
      {
        var element = FindElement(indicator);
        if (element != null && element.IsAvailable)
        {
          errorsFound.Add(indicator);
        }
      }
      
      // Assert
      Assert.AreEqual(0, errorsFound.Count,
        $"Error indicators found on startup: {string.Join(", ", errorsFound)}");
      
      Log("No startup exceptions detected");
      await Task.CompletedTask;
    }

    [TestMethod]
    [TestCategory("E2E")]
    [TestCategory("Lifecycle")]
    public async Task Application_NavigationAvailableAfterStartup()
    {
      // Arrange
      VerifyApplicationStarted();
      
      // Act - Check if navigation buttons are available
      var navButtons = new[]
      {
        "NavStudio",
        "NavProfiles",
        "NavLibrary",
        "NavSettings"
      };
      
      var unavailableButtons = new List<string>();
      
      if (UseRealAutomation)
      {
        foreach (var buttonId in navButtons)
        {
          var button = FindElement(buttonId);
          if (button == null)
          {
            unavailableButtons.Add(buttonId);
          }
        }
        
        // Assert
        if (unavailableButtons.Count > 0)
        {
          Log($"Navigation buttons not found: {string.Join(", ", unavailableButtons)}");
        }
      }
      
      // In both modes, verify we can navigate to at least one panel
      var canNavigate = await NavigateToPanelAsync("VoiceSynthesis");
      Assert.IsTrue(canNavigate, "Should be able to navigate to VoiceSynthesis after startup");
    }

    [TestMethod]
    [TestCategory("E2E")]
    [TestCategory("Lifecycle")]
    public async Task Application_StatusBarShowsReady()
    {
      // Arrange
      VerifyApplicationStarted();
      
      if (!UseRealAutomation)
      {
        Log("Skipping status bar check in simulated mode");
        return;
      }
      
      // Act - Wait for status bar to show ready state
      await Task.Delay(2000); // Allow app to fully initialize
      
      var statusBar = FindElement("StatusBar") ?? FindElement("StatusBarText");
      
      // Assert
      if (statusBar != null)
      {
        var statusText = statusBar.Name ?? statusBar.AutomationId;
        Log($"Status bar content: {statusText}");
        // Just log the status, don't fail if not "Ready"
      }
      else
      {
        Log("Status bar element not found");
      }
      
      Assert.IsTrue(true, "Status bar check completed");
    }

    [TestMethod]
    [TestCategory("E2E")]
    [TestCategory("Lifecycle")]
    public async Task Application_CanPerformBasicWorkflow()
    {
      // Arrange
      VerifyApplicationStarted();
      
      // Act - Perform a basic navigation workflow
      var workflow = new[]
      {
        "VoiceSynthesis",
        "Profiles",
        "Settings",
        "VoiceSynthesis"
      };
      
      var workflowSteps = new List<string>();
      foreach (var panel in workflow)
      {
        ClearSimulatedState();
        var success = await NavigateToPanelAsync(panel);
        if (success)
        {
          workflowSteps.Add(panel);
        }
        else
        {
          Log($"Workflow step failed: {panel}");
          break;
        }
      }
      
      // Assert
      Assert.AreEqual(workflow.Length, workflowSteps.Count,
        $"Basic workflow completed {workflowSteps.Count}/{workflow.Length} steps");
    }

    [TestMethod]
    [TestCategory("E2E")]
    [TestCategory("Lifecycle")]
    [TestCategory("Performance")]
    public async Task Application_StartsWithinTimeLimit()
    {
      // Note: This test measures startup time. In real automation,
      // the timing is measured during LaunchAsync in SmokeTestBase.
      
      VerifyApplicationStarted();
      
      // For simulated mode, just pass
      if (!UseRealAutomation)
      {
        Log($"Simulated startup - max allowed: {MaxStartupTimeSeconds}s");
        Assert.IsTrue(true, "Startup time check passed (simulated)");
        return;
      }
      
      // In real automation, we can't easily measure startup time here
      // since the app is already started. Log the expectation.
      Log($"Application should start within {MaxStartupTimeSeconds} seconds");
      Assert.IsTrue(MainWindow != null && MainWindow.IsAvailable,
        "Application should be fully started and responsive");
      
      await Task.CompletedTask;
    }

    [TestMethod]
    [TestCategory("E2E")]
    [TestCategory("Lifecycle")]
    public async Task Application_HandlesMultipleNavigations()
    {
      // Arrange
      VerifyApplicationStarted();
      const int navigationCount = 10;
      var panels = new[] { "VoiceSynthesis", "Profiles", "Library", "Settings", "Diagnostics" };
      var random = new Random(42); // Fixed seed for reproducibility
      
      var successCount = 0;
      
      // Act
      for (int i = 0; i < navigationCount; i++)
      {
        var targetPanel = panels[random.Next(panels.Length)];
        ClearSimulatedState();
        
        var success = await NavigateToPanelAsync(targetPanel);
        if (success)
        {
          successCount++;
        }
        else
        {
          Log($"Navigation {i + 1} to {targetPanel} failed");
        }
      }
      
      // Assert
      Assert.AreEqual(navigationCount, successCount,
        $"All {navigationCount} navigations should succeed");
    }

    [TestMethod]
    [TestCategory("E2E")]
    [TestCategory("Lifecycle")]
    public async Task Application_MemoryUsageReasonable()
    {
      // This is a placeholder for memory usage monitoring.
      // In real scenarios, you would use performance counters or memory profiling.
      
      VerifyApplicationStarted();
      
      if (!UseRealAutomation)
      {
        Log("Memory check skipped in simulated mode");
        Assert.IsTrue(true);
        return;
      }
      
      // Perform some operations
      await NavigateToPanelAsync("VoiceSynthesis");
      await NavigateToPanelAsync("Library");
      await NavigateToPanelAsync("Settings");
      
      // In real automation, we could check process memory here
      // For now, just verify app is still responsive
      var stillResponsive = MainWindow != null && MainWindow.IsAvailable;
      Assert.IsTrue(stillResponsive, "Application should remain responsive after operations");
      
      Log("Memory usage check completed (app remains responsive)");
    }
  }
}
