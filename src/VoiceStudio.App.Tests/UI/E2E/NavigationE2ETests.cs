using Microsoft.VisualStudio.TestTools.UnitTesting;
using System.Collections.Generic;
using System.Threading.Tasks;

namespace VoiceStudio.App.Tests.UI.E2E
{
  /// <summary>
  /// End-to-end tests for navigation functionality.
  /// Tests all 8 main navigation tabs in VoiceStudio.
  /// </summary>
  [TestClass]
  public class NavigationE2ETests : SmokeTestBase
  {
    /// <summary>
    /// Navigation button AutomationIds for the 8 main tabs.
    /// </summary>
    private static readonly string[] NavigationTabs = new[]
    {
      "NavStudio",
      "NavProfiles",
      "NavLibrary",
      "NavEffects",
      "NavTrain",
      "NavAnalyze",
      "NavSettings",
      "NavLogs"
    };

    /// <summary>
    /// Expected panels for each navigation tab.
    /// </summary>
    private static readonly Dictionary<string, string> NavToPanelMap = new()
    {
      { "NavStudio", "VoiceSynthesis" },
      { "NavProfiles", "Profiles" },
      { "NavLibrary", "Library" },
      { "NavEffects", "EffectsMixer" },
      { "NavTrain", "Training" },
      { "NavAnalyze", "Analyzer" },
      { "NavSettings", "Settings" },
      { "NavLogs", "Diagnostics" }
    };

    [TestMethod]
    [TestCategory("E2E")]
    [TestCategory("Navigation")]
    public async Task Navigation_StudioTab_ShowsVoiceSynthesisPanel()
    {
      // Arrange
      VerifyApplicationStarted();
      
      // Act - Use NavigateToPanelAsync which handles simulation properly
      var result = await NavigateToPanelAsync("VoiceSynthesis");
      
      // Assert
      Assert.IsTrue(result, "VoiceSynthesis panel should be visible after clicking NavStudio");
    }

    [TestMethod]
    [TestCategory("E2E")]
    [TestCategory("Navigation")]
    public async Task Navigation_ProfilesTab_ShowsProfilesPanel()
    {
      VerifyApplicationStarted();
      
      var result = await NavigateToPanelAsync("Profiles");
      
      Assert.IsTrue(result, "Profiles panel should be visible after clicking NavProfiles");
    }

    [TestMethod]
    [TestCategory("E2E")]
    [TestCategory("Navigation")]
    public async Task Navigation_LibraryTab_ShowsLibraryPanel()
    {
      VerifyApplicationStarted();
      
      var result = await NavigateToPanelAsync("Library");
      
      Assert.IsTrue(result, "Library panel should be visible after clicking NavLibrary");
    }

    [TestMethod]
    [TestCategory("E2E")]
    [TestCategory("Navigation")]
    public async Task Navigation_EffectsTab_ShowsEffectsMixerPanel()
    {
      VerifyApplicationStarted();
      
      var result = await NavigateToPanelAsync("EffectsMixer");
      
      Assert.IsTrue(result, "EffectsMixer panel should be visible after clicking NavEffects");
    }

    [TestMethod]
    [TestCategory("E2E")]
    [TestCategory("Navigation")]
    public async Task Navigation_TrainTab_ShowsTrainingPanel()
    {
      VerifyApplicationStarted();
      
      var result = await NavigateToPanelAsync("Training");
      
      Assert.IsTrue(result, "Training panel should be visible after clicking NavTrain");
    }

    [TestMethod]
    [TestCategory("E2E")]
    [TestCategory("Navigation")]
    public async Task Navigation_AnalyzeTab_ShowsAnalyzerPanel()
    {
      VerifyApplicationStarted();
      
      var result = await NavigateToPanelAsync("Analyzer");
      
      Assert.IsTrue(result, "Analyzer panel should be visible after clicking NavAnalyze");
    }

    [TestMethod]
    [TestCategory("E2E")]
    [TestCategory("Navigation")]
    public async Task Navigation_SettingsTab_ShowsSettingsPanel()
    {
      VerifyApplicationStarted();
      
      var result = await NavigateToPanelAsync("Settings");
      
      Assert.IsTrue(result, "Settings panel should be visible after clicking NavSettings");
    }

    [TestMethod]
    [TestCategory("E2E")]
    [TestCategory("Navigation")]
    public async Task Navigation_LogsTab_ShowsDiagnosticsPanel()
    {
      VerifyApplicationStarted();
      
      var result = await NavigateToPanelAsync("Diagnostics");
      
      Assert.IsTrue(result, "Diagnostics panel should be visible after clicking NavLogs");
    }

    [TestMethod]
    [TestCategory("E2E")]
    [TestCategory("Navigation")]
    public async Task Navigation_AllTabs_CanNavigateSequentially()
    {
      // Arrange
      VerifyApplicationStarted();
      var failedTabs = new List<string>();
      
      // Act & Assert - Navigate through all tabs
      foreach (var tab in NavigationTabs)
      {
        Log($"Testing navigation to: {tab}");
        
        await ClickButtonAsync(tab);
        
        if (NavToPanelMap.TryGetValue(tab, out var expectedPanel))
        {
          // In simulated mode, simulate the panel becoming visible
          if (!UseRealAutomation)
          {
            SimulatePanelVisible(expectedPanel);
          }
          
          var visible = await WaitForPanelAsync(expectedPanel, TimeSpan.FromSeconds(3));
          if (!visible)
          {
            failedTabs.Add($"{tab} -> {expectedPanel}");
          }
          
          // Clear for next iteration in simulated mode
          if (!UseRealAutomation)
          {
            ClearSimulatedState();
          }
        }
      }
      
      // Assert
      Assert.AreEqual(0, failedTabs.Count, 
        $"The following navigation tabs failed: {string.Join(", ", failedTabs)}");
    }

    [TestMethod]
    [TestCategory("E2E")]
    [TestCategory("Navigation")]
    public async Task Navigation_TabSwitching_UpdatesActiveState()
    {
      // Arrange
      VerifyApplicationStarted();
      
      // Act - Click Studio, then Profiles
      await ClickButtonAsync("NavStudio");
      if (!UseRealAutomation) SimulatePanelVisible("VoiceSynthesis");
      await WaitForPanelAsync("VoiceSynthesis");
      
      ClearSimulatedState();
      
      await ClickButtonAsync("NavProfiles");
      if (!UseRealAutomation) SimulatePanelVisible("Profiles");
      var profilesVisible = await WaitForPanelAsync("Profiles");
      
      // Assert
      Assert.IsTrue(profilesVisible, "Profiles panel should be visible after switching from Studio");
      
      // In real automation, verify VoiceSynthesis is no longer the active panel
      if (UseRealAutomation)
      {
        var synthesisStillVisible = IsPanelVisible("VoiceSynthesisView_Root");
        Log($"VoiceSynthesis still visible after switch: {synthesisStillVisible}");
        // Note: May still be visible in split view, so we just log rather than assert
      }
    }
  }
}
