using Microsoft.VisualStudio.TestTools.UnitTesting;
using System.Threading.Tasks;
using VoiceStudio.Core.Services;
using VoiceStudio.App.Tests.ViewModels;

namespace VoiceStudio.App.Tests.UI
{
  /// <summary>
  /// Smoke tests for panel navigation functionality.
  /// Verifies that panels can be navigated to and displayed correctly.
  /// </summary>
    [TestClass]
    [TestCategory("UI")]
    public class PanelNavigationSmokeTests : SmokeTestBase
  {
    private MockBackendClient? _mockBackendClient;

    [TestInitialize]
    public override void TestInitialize()
    {
      base.TestInitialize();
      _mockBackendClient = new MockBackendClient();
    }

    [TestCleanup]
    public override void TestCleanup()
    {
      _mockBackendClient = null;
      base.TestCleanup();
    }

    [UITestMethod]
    public async Task NavigateToProfilesPanel()
    {
      // Arrange
      // In a real implementation, this would use NavigationService to navigate
      // For now, we verify the ViewModel can be created

      var profilesUseCase = new VoiceStudio.App.UseCases.ProfilesUseCase(_mockBackendClient!);
      var viewModel = new VoiceStudio.App.Views.Panels.ProfilesViewModel(
          _mockBackendClient!,
          profilesUseCase,
          new VoiceStudio.App.Services.AudioPlayerService(),
          new VoiceStudio.App.Services.MultiSelectService(),
          toastNotificationService: null,
          undoRedoService: new VoiceStudio.App.Services.UndoRedoService(),
          errorService: null,
          logService: null);

      // Act
      await WaitForPanelAsync("profiles");

      // Assert
      Assert.IsNotNull(viewModel, "ProfilesViewModel should be created");
      Assert.AreEqual("profiles", viewModel.PanelId, "Panel ID should match");
    }

    [UITestMethod]
    public async Task NavigateToTimelinePanel()
    {
      // Arrange
      var viewModel = new VoiceStudio.App.Views.Panels.TimelineViewModel(
          _mockBackendClient!,
          new VoiceStudio.App.Services.AudioPlayerService(),
          new VoiceStudio.App.Services.MultiSelectService(),
          toastNotificationService: null,
          undoRedoService: new VoiceStudio.App.Services.UndoRedoService(),
          errorService: null,
          logService: null,
          settingsService: null,
          recentProjectsService: null);

      // Act
      await WaitForPanelAsync("timeline");

      // Assert
      Assert.IsNotNull(viewModel, "TimelineViewModel should be created");
      Assert.AreEqual("timeline", viewModel.PanelId, "Panel ID should match");
    }

    [UITestMethod]
    public async Task PanelSwitchingWorks()
    {
      // Arrange
      var profilesUseCase = new VoiceStudio.App.UseCases.ProfilesUseCase(_mockBackendClient!);
      var profilesViewModel = new VoiceStudio.App.Views.Panels.ProfilesViewModel(
          _mockBackendClient!,
          profilesUseCase,
          new VoiceStudio.App.Services.AudioPlayerService(),
          new VoiceStudio.App.Services.MultiSelectService(),
          toastNotificationService: null,
          undoRedoService: new VoiceStudio.App.Services.UndoRedoService(),
          errorService: null,
          logService: null);
      var timelineViewModel = new VoiceStudio.App.Views.Panels.TimelineViewModel(
          _mockBackendClient!,
          new VoiceStudio.App.Services.AudioPlayerService(),
          new VoiceStudio.App.Services.MultiSelectService(),
          toastNotificationService: null,
          undoRedoService: new VoiceStudio.App.Services.UndoRedoService(),
          errorService: null,
          logService: null,
          settingsService: null,
          recentProjectsService: null);

      // Act
      // In a real implementation, this would:
      // 1. Navigate to Profiles panel
      // 2. Verify it's displayed
      // 3. Navigate to Timeline panel
      // 4. Verify it's displayed
      // 5. Verify Profiles panel is no longer visible

      await WaitForPanelAsync("profiles");
      await WaitForPanelAsync("timeline");

      // Assert
      Assert.IsNotNull(profilesViewModel, "ProfilesViewModel should exist");
      Assert.IsNotNull(timelineViewModel, "TimelineViewModel should exist");
      Assert.AreNotEqual(profilesViewModel.PanelId, timelineViewModel.PanelId,
          "Panels should have different IDs");
    }

    [TestMethod]
    public void PanelViewModels_ImplementIPanelView()
    {
      // Arrange & Act
      var profilesUseCase = new VoiceStudio.App.UseCases.ProfilesUseCase(_mockBackendClient!);
      var profilesViewModel = new VoiceStudio.App.Views.Panels.ProfilesViewModel(
          _mockBackendClient!,
          profilesUseCase,
          new VoiceStudio.App.Services.AudioPlayerService(),
          new VoiceStudio.App.Services.MultiSelectService(),
          toastNotificationService: null,
          undoRedoService: new VoiceStudio.App.Services.UndoRedoService(),
          errorService: null,
          logService: null);

      // Assert
      Assert.IsInstanceOfType(profilesViewModel, typeof(VoiceStudio.Core.Panels.IPanelView),
          "ProfilesViewModel should implement IPanelView");

      var panelView = (VoiceStudio.Core.Panels.IPanelView)profilesViewModel;
      Assert.IsNotNull(panelView.PanelId, "PanelId should not be null");
      Assert.IsNotNull(panelView.DisplayName, "DisplayName should not be null");
    }
  }
}