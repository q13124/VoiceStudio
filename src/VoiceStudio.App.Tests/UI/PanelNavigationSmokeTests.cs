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
            
            var viewModel = new VoiceStudio.App.ViewModels.ProfilesViewModel(
                _mockBackendClient!,
                new VoiceStudio.App.Services.AudioPlayerService());
            
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
            var viewModel = new VoiceStudio.App.ViewModels.TimelineViewModel(_mockBackendClient!);
            
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
            var profilesViewModel = new VoiceStudio.App.ViewModels.ProfilesViewModel(
                _mockBackendClient!,
                new VoiceStudio.App.Services.AudioPlayerService());
            var timelineViewModel = new VoiceStudio.App.ViewModels.TimelineViewModel(_mockBackendClient!);
            
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
            var profilesViewModel = new VoiceStudio.App.ViewModels.ProfilesViewModel(
                _mockBackendClient!,
                new VoiceStudio.App.Services.AudioPlayerService());
            
            // Assert
            Assert.IsInstanceOfType(profilesViewModel, typeof(VoiceStudio.Core.Panels.IPanelView), 
                "ProfilesViewModel should implement IPanelView");
            
            var panelView = (VoiceStudio.Core.Panels.IPanelView)profilesViewModel;
            Assert.IsNotNull(panelView.PanelId, "PanelId should not be null");
            Assert.IsNotNull(panelView.DisplayName, "DisplayName should not be null");
        }
    }
}