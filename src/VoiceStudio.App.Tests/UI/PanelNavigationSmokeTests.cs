using Microsoft.VisualStudio.TestTools.UnitTesting;
using System.Threading.Tasks;

namespace VoiceStudio.App.Tests.UI
{
  /// <summary>
  /// Smoke tests for panel navigation.
  /// Tests that all major panels can be loaded and displayed without errors.
  /// </summary>
  [TestClass]
  public class PanelNavigationSmokeTests : SmokeTestBase
  {
    #region Core Panels

    [TestMethod]
    [TestCategory("Smoke")]
    [TestCategory("UI")]
    public async Task Panel_VoiceSynthesis_CanNavigate()
    {
      // Arrange
      VerifyApplicationStarted();

      // Act
      var result = await NavigateToPanelAsync("VoiceSynthesis");

      // Assert
      Assert.IsTrue(result, "VoiceSynthesis panel should be visible");
      Assert.IsTrue(IsPanelVisible("VoiceSynthesisView_Root"));
    }

    [TestMethod]
    [TestCategory("Smoke")]
    [TestCategory("UI")]
    public async Task Panel_Profiles_CanNavigate()
    {
      VerifyApplicationStarted();
      var result = await NavigateToPanelAsync("Profiles");
      Assert.IsTrue(result, "Profiles panel should be visible");
    }

    [TestMethod]
    [TestCategory("Smoke")]
    [TestCategory("UI")]
    public async Task Panel_Library_CanNavigate()
    {
      VerifyApplicationStarted();
      var result = await NavigateToPanelAsync("Library");
      Assert.IsTrue(result, "Library panel should be visible");
    }

    [TestMethod]
    [TestCategory("Smoke")]
    [TestCategory("UI")]
    public async Task Panel_Timeline_CanNavigate()
    {
      VerifyApplicationStarted();
      var result = await NavigateToPanelAsync("Timeline");
      Assert.IsTrue(result, "Timeline panel should be visible");
    }

    [TestMethod]
    [TestCategory("Smoke")]
    [TestCategory("UI")]
    public async Task Panel_EffectsMixer_CanNavigate()
    {
      VerifyApplicationStarted();
      var result = await NavigateToPanelAsync("EffectsMixer");
      Assert.IsTrue(result, "EffectsMixer panel should be visible");
    }

    [TestMethod]
    [TestCategory("Smoke")]
    [TestCategory("UI")]
    public async Task Panel_Analyzer_CanNavigate()
    {
      VerifyApplicationStarted();
      var result = await NavigateToPanelAsync("Analyzer");
      Assert.IsTrue(result, "Analyzer panel should be visible");
    }

    [TestMethod]
    [TestCategory("Smoke")]
    [TestCategory("UI")]
    public async Task Panel_Diagnostics_CanNavigate()
    {
      VerifyApplicationStarted();
      var result = await NavigateToPanelAsync("Diagnostics");
      Assert.IsTrue(result, "Diagnostics panel should be visible");
    }

    [TestMethod]
    [TestCategory("Smoke")]
    [TestCategory("UI")]
    public async Task Panel_Macro_CanNavigate()
    {
      VerifyApplicationStarted();
      var result = await NavigateToPanelAsync("Macro");
      Assert.IsTrue(result, "Macro panel should be visible");
    }

    #endregion

    #region Synthesis Panels

    [TestMethod]
    [TestCategory("Smoke")]
    [TestCategory("UI")]
    public async Task Panel_EnsembleSynthesis_CanNavigate()
    {
      VerifyApplicationStarted();
      var result = await NavigateToPanelAsync("EnsembleSynthesis");
      Assert.IsTrue(result, "EnsembleSynthesis panel should be visible");
    }

    [TestMethod]
    [TestCategory("Smoke")]
    [TestCategory("UI")]
    public async Task Panel_BatchProcessing_CanNavigate()
    {
      VerifyApplicationStarted();
      var result = await NavigateToPanelAsync("BatchProcessing");
      Assert.IsTrue(result, "BatchProcessing panel should be visible");
    }

    [TestMethod]
    [TestCategory("Smoke")]
    [TestCategory("UI")]
    public async Task Panel_MultiVoiceGenerator_CanNavigate()
    {
      VerifyApplicationStarted();
      var result = await NavigateToPanelAsync("MultiVoiceGenerator");
      Assert.IsTrue(result, "MultiVoiceGenerator panel should be visible");
    }

    #endregion

    #region Training Panels

    [TestMethod]
    [TestCategory("Smoke")]
    [TestCategory("UI")]
    public async Task Panel_Training_CanNavigate()
    {
      VerifyApplicationStarted();
      var result = await NavigateToPanelAsync("Training");
      Assert.IsTrue(result, "Training panel should be visible");
    }

    [TestMethod]
    [TestCategory("Smoke")]
    [TestCategory("UI")]
    public async Task Panel_TrainingDatasetEditor_CanNavigate()
    {
      VerifyApplicationStarted();
      var result = await NavigateToPanelAsync("TrainingDatasetEditor");
      Assert.IsTrue(result, "TrainingDatasetEditor panel should be visible");
    }

    [TestMethod]
    [TestCategory("Smoke")]
    [TestCategory("UI")]
    public async Task Panel_ModelManager_CanNavigate()
    {
      VerifyApplicationStarted();
      var result = await NavigateToPanelAsync("ModelManager");
      Assert.IsTrue(result, "ModelManager panel should be visible");
    }

    #endregion

    #region Audio Processing Panels

    [TestMethod]
    [TestCategory("Smoke")]
    [TestCategory("UI")]
    public async Task Panel_Transcribe_CanNavigate()
    {
      VerifyApplicationStarted();
      var result = await NavigateToPanelAsync("Transcribe");
      Assert.IsTrue(result, "Transcribe panel should be visible");
    }

    [TestMethod]
    [TestCategory("Smoke")]
    [TestCategory("UI")]
    public async Task Panel_Recording_CanNavigate()
    {
      VerifyApplicationStarted();
      var result = await NavigateToPanelAsync("Recording");
      Assert.IsTrue(result, "Recording panel should be visible");
    }

    [TestMethod]
    [TestCategory("Smoke")]
    [TestCategory("UI")]
    public async Task Panel_AudioAnalysis_CanNavigate()
    {
      VerifyApplicationStarted();
      var result = await NavigateToPanelAsync("AudioAnalysis");
      Assert.IsTrue(result, "AudioAnalysis panel should be visible");
    }

    [TestMethod]
    [TestCategory("Smoke")]
    [TestCategory("UI")]
    public async Task Panel_QualityControl_CanNavigate()
    {
      VerifyApplicationStarted();
      var result = await NavigateToPanelAsync("QualityControl");
      Assert.IsTrue(result, "QualityControl panel should be visible");
    }

    [TestMethod]
    [TestCategory("Smoke")]
    [TestCategory("UI")]
    public async Task Panel_QualityDashboard_CanNavigate()
    {
      VerifyApplicationStarted();
      var result = await NavigateToPanelAsync("QualityDashboard");
      Assert.IsTrue(result, "QualityDashboard panel should be visible");
    }

    #endregion

    #region Settings Panels

    [TestMethod]
    [TestCategory("Smoke")]
    [TestCategory("UI")]
    public async Task Panel_Settings_CanNavigate()
    {
      VerifyApplicationStarted();
      var result = await NavigateToPanelAsync("Settings");
      Assert.IsTrue(result, "Settings panel should be visible");
    }

    [TestMethod]
    [TestCategory("Smoke")]
    [TestCategory("UI")]
    public async Task Panel_AdvancedSettings_CanNavigate()
    {
      VerifyApplicationStarted();
      var result = await NavigateToPanelAsync("AdvancedSettings");
      Assert.IsTrue(result, "AdvancedSettings panel should be visible");
    }

    [TestMethod]
    [TestCategory("Smoke")]
    [TestCategory("UI")]
    public async Task Panel_KeyboardShortcuts_CanNavigate()
    {
      VerifyApplicationStarted();
      var result = await NavigateToPanelAsync("KeyboardShortcuts");
      Assert.IsTrue(result, "KeyboardShortcuts panel should be visible");
    }

    [TestMethod]
    [TestCategory("Smoke")]
    [TestCategory("UI")]
    public async Task Panel_PluginManagement_CanNavigate()
    {
      VerifyApplicationStarted();
      var result = await NavigateToPanelAsync("PluginManagement");
      Assert.IsTrue(result, "PluginManagement panel should be visible");
    }

    [TestMethod]
    [TestCategory("Smoke")]
    [TestCategory("UI")]
    public async Task Panel_APIKeyManager_CanNavigate()
    {
      VerifyApplicationStarted();
      var result = await NavigateToPanelAsync("APIKeyManager");
      Assert.IsTrue(result, "APIKeyManager panel should be visible");
    }

    #endregion

    #region Utility Panels

    [TestMethod]
    [TestCategory("Smoke")]
    [TestCategory("UI")]
    public async Task Panel_Help_CanNavigate()
    {
      VerifyApplicationStarted();
      var result = await NavigateToPanelAsync("Help");
      Assert.IsTrue(result, "Help panel should be visible");
    }

    [TestMethod]
    [TestCategory("Smoke")]
    [TestCategory("UI")]
    public async Task Panel_GPUStatus_CanNavigate()
    {
      VerifyApplicationStarted();
      var result = await NavigateToPanelAsync("GPUStatus");
      Assert.IsTrue(result, "GPUStatus panel should be visible");
    }

    #endregion

    #region Voice Control Panels

    [TestMethod]
    [TestCategory("Smoke")]
    [TestCategory("UI")]
    public async Task Panel_VoiceMorph_CanNavigate()
    {
      VerifyApplicationStarted();
      var result = await NavigateToPanelAsync("VoiceMorph");
      Assert.IsTrue(result, "VoiceMorph panel should be visible");
    }

    [TestMethod]
    [TestCategory("Smoke")]
    [TestCategory("UI")]
    public async Task Panel_StyleTransfer_CanNavigate()
    {
      VerifyApplicationStarted();
      var result = await NavigateToPanelAsync("StyleTransfer");
      Assert.IsTrue(result, "StyleTransfer panel should be visible");
    }

    [TestMethod]
    [TestCategory("Smoke")]
    [TestCategory("UI")]
    public async Task Panel_EmotionControl_CanNavigate()
    {
      VerifyApplicationStarted();
      var result = await NavigateToPanelAsync("EmotionControl");
      Assert.IsTrue(result, "EmotionControl panel should be visible");
    }

    [TestMethod]
    [TestCategory("Smoke")]
    [TestCategory("UI")]
    public async Task Panel_Prosody_CanNavigate()
    {
      VerifyApplicationStarted();
      var result = await NavigateToPanelAsync("Prosody");
      Assert.IsTrue(result, "Prosody panel should be visible");
    }

    [TestMethod]
    [TestCategory("Smoke")]
    [TestCategory("UI")]
    public async Task Panel_SSML_CanNavigate()
    {
      VerifyApplicationStarted();
      var result = await NavigateToPanelAsync("SSML");
      Assert.IsTrue(result, "SSML panel should be visible");
    }

    [TestMethod]
    [TestCategory("Smoke")]
    [TestCategory("UI")]
    public async Task Panel_Spectrogram_CanNavigate()
    {
      VerifyApplicationStarted();
      var result = await NavigateToPanelAsync("Spectrogram");
      Assert.IsTrue(result, "Spectrogram panel should be visible");
    }

    #endregion

    #region Multi-Panel Navigation Tests

    [TestMethod]
    [TestCategory("Smoke")]
    [TestCategory("UI")]
    public async Task Navigation_CorePanels_AllLoad()
    {
      VerifyApplicationStarted();

      var corePanels = new[] { "VoiceSynthesis", "Profiles", "Library", "Timeline", "EffectsMixer", "Analyzer" };
      
      foreach (var panel in corePanels)
      {
        ClearSimulatedState();
        var result = await NavigateToPanelAsync(panel);
        Assert.IsTrue(result, $"{panel} panel should be visible");
      }
    }

    [TestMethod]
    [TestCategory("Smoke")]
    [TestCategory("UI")]
    public async Task Navigation_SynthesisPanels_AllLoad()
    {
      VerifyApplicationStarted();

      var synthesisPanels = new[] { "VoiceSynthesis", "EnsembleSynthesis", "BatchProcessing" };
      
      foreach (var panel in synthesisPanels)
      {
        ClearSimulatedState();
        var result = await NavigateToPanelAsync(panel);
        Assert.IsTrue(result, $"{panel} panel should be visible");
      }
    }

    #endregion
  }
}
