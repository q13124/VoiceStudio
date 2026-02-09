using Microsoft.VisualStudio.TestTools.UnitTesting;
using Moq;
using System.Collections.Generic;
using System.Threading;
using System.Threading.Tasks;
using VoiceStudio.App.Commands;
using VoiceStudio.App.Core.Commands;

namespace VoiceStudio.App.Tests.Commands
{
    /// <summary>
    /// Unit tests for NavigationHandler.
    /// </summary>
    [TestClass]
    [TestCategory("Commands")]
    public class NavigationHandlerTests : CommandHandlerTestBase
    {
        private NavigationHandler _handler = null!;

        [TestInitialize]
        public override void SetupBase()
        {
            base.SetupBase();
            _handler = new NavigationHandler(
                Registry,
                MockNavigationService.Object,
                null);
        }

        #region Registration Tests

        [TestMethod]
        public void Constructor_RegistersAllNavigationCommands()
        {
            AssertCommandsRegistered(
                "nav.studio",
                "nav.profiles",
                "nav.library",
                "nav.effects",
                "nav.train",
                "nav.analyze",
                "nav.settings",
                "nav.logs",
                "nav.synthesis",
                "nav.timeline",
                "nav.back",
                "nav.forward",
                "nav.home"
            );
        }

        [TestMethod]
        public void Commands_HaveCorrectCategory()
        {
            AssertCommandMetadata("nav.studio", "Studio", "Navigation");
            AssertCommandMetadata("nav.profiles", "Voice Profiles", "Navigation");
            AssertCommandMetadata("nav.settings", "Settings", "Navigation");
        }

        #endregion

        #region Navigation Tests

        [TestMethod]
        public async Task NavigateToStudio_CallsNavigationService()
        {
            // Act
            await Registry.ExecuteAsync("nav.studio");

            // Assert
            MockNavigationService.Verify(n => n.NavigateToPanelAsync(
                "studio", It.IsAny<Dictionary<string, object>?>(), It.IsAny<CancellationToken>()), Times.Once);
        }

        [TestMethod]
        public async Task NavigateToProfiles_CallsNavigationService()
        {
            // Act
            await Registry.ExecuteAsync("nav.profiles");

            // Assert
            MockNavigationService.Verify(n => n.NavigateToPanelAsync(
                "profiles", It.IsAny<Dictionary<string, object>?>(), It.IsAny<CancellationToken>()), Times.Once);
        }

        [TestMethod]
        public async Task NavigateToLibrary_CallsNavigationService()
        {
            // Act
            await Registry.ExecuteAsync("nav.library");

            // Assert
            MockNavigationService.Verify(n => n.NavigateToPanelAsync(
                "library", It.IsAny<Dictionary<string, object>?>(), It.IsAny<CancellationToken>()), Times.Once);
        }

        [TestMethod]
        public async Task NavigateToEffects_CallsNavigationService()
        {
            // Act
            await Registry.ExecuteAsync("nav.effects");

            // Assert
            MockNavigationService.Verify(n => n.NavigateToPanelAsync(
                "effects", It.IsAny<Dictionary<string, object>?>(), It.IsAny<CancellationToken>()), Times.Once);
        }

        [TestMethod]
        public async Task NavigateToTrain_CallsNavigationService()
        {
            // Act
            await Registry.ExecuteAsync("nav.train");

            // Assert
            MockNavigationService.Verify(n => n.NavigateToPanelAsync(
                "train", It.IsAny<Dictionary<string, object>?>(), It.IsAny<CancellationToken>()), Times.Once);
        }

        [TestMethod]
        public async Task NavigateToAnalyze_CallsNavigationService()
        {
            // Act
            await Registry.ExecuteAsync("nav.analyze");

            // Assert
            MockNavigationService.Verify(n => n.NavigateToPanelAsync(
                "analyze", It.IsAny<Dictionary<string, object>?>(), It.IsAny<CancellationToken>()), Times.Once);
        }

        [TestMethod]
        public async Task NavigateToSettings_CallsNavigationService()
        {
            // Act
            await Registry.ExecuteAsync("nav.settings");

            // Assert
            MockNavigationService.Verify(n => n.NavigateToPanelAsync(
                "settings", It.IsAny<Dictionary<string, object>?>(), It.IsAny<CancellationToken>()), Times.Once);
        }

        [TestMethod]
        public async Task NavigateToLogs_CallsNavigationService()
        {
            // Act
            await Registry.ExecuteAsync("nav.logs");

            // Assert
            MockNavigationService.Verify(n => n.NavigateToPanelAsync(
                "logs", It.IsAny<Dictionary<string, object>?>(), It.IsAny<CancellationToken>()), Times.Once);
        }

        [TestMethod]
        public async Task NavigateToSynthesis_CallsNavigationService()
        {
            // Act
            await Registry.ExecuteAsync("nav.synthesis");

            // Assert
            MockNavigationService.Verify(n => n.NavigateToPanelAsync(
                "synthesis", It.IsAny<Dictionary<string, object>?>(), It.IsAny<CancellationToken>()), Times.Once);
        }

        [TestMethod]
        public async Task NavigateToTimeline_CallsNavigationService()
        {
            // Act
            await Registry.ExecuteAsync("nav.timeline");

            // Assert
            MockNavigationService.Verify(n => n.NavigateToPanelAsync(
                "timeline", It.IsAny<Dictionary<string, object>?>(), It.IsAny<CancellationToken>()), Times.Once);
        }

        #endregion

        #region Back/Forward Tests

        [TestMethod]
        public async Task NavigateBack_CallsNavigationServiceNavigateBackAsync()
        {
            // Arrange
            MockNavigationService.Setup(n => n.CanNavigateBack()).Returns(true);

            // Act
            await Registry.ExecuteAsync("nav.back");

            // Assert
            MockNavigationService.Verify(n => n.NavigateBackAsync(It.IsAny<CancellationToken>()), Times.Once);
        }

        [TestMethod]
        public void NavigateBack_CannotExecute_WhenNoHistory()
        {
            // Arrange
            MockNavigationService.Setup(n => n.CanNavigateBack()).Returns(false);

            // Assert
            AssertCannotExecute("nav.back");
        }

        [TestMethod]
        public void NavigateForward_CannotExecute_AsNotImplemented()
        {
            // Forward navigation is not yet implemented in the handler
            // The canExecute returns false
            AssertCannotExecute("nav.forward");
        }

        #endregion

        #region Home Tests

        [TestMethod]
        public async Task NavigateHome_NavigatesToStudio()
        {
            // Act
            await Registry.ExecuteAsync("nav.home");

            // Assert - nav.home navigates to "studio" panel
            MockNavigationService.Verify(n => n.NavigateToPanelAsync(
                "studio", It.IsAny<Dictionary<string, object>?>(), It.IsAny<CancellationToken>()), Times.Once);
        }

        #endregion

        #region Event Tests

        [TestMethod]
        public async Task NavigationRequested_RaisedOnNavigation()
        {
            // Arrange
            string? receivedPanel = null;
            _handler.NavigationRequested += (s, panel) => receivedPanel = panel;

            // Act
            await Registry.ExecuteAsync("nav.studio");

            // Assert
            Assert.AreEqual("studio", receivedPanel);
        }

        #endregion
    }
}
