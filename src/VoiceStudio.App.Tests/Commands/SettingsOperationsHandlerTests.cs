using Microsoft.VisualStudio.TestTools.UnitTesting;
using Moq;
using System;
using System.Threading;
using System.Threading.Tasks;
using VoiceStudio.App.Commands;
using VoiceStudio.App.Core.Commands;
using VoiceStudio.Core.Models;

namespace VoiceStudio.App.Tests.Commands
{
    /// <summary>
    /// Unit tests for SettingsOperationsHandler.
    /// </summary>
    [TestClass]
    [TestCategory("Commands")]
    public class SettingsOperationsHandlerTests : CommandHandlerTestBase
    {
        private SettingsOperationsHandler _handler = null!;

        [TestInitialize]
        public override void SetupBase()
        {
            base.SetupBase();
            _handler = new SettingsOperationsHandler(
                Registry,
                MockSettingsService.Object,
                MockDialogService.Object,
                null);
        }

        #region Registration Tests

        [TestMethod]
        public void Constructor_RegistersAllSettingsCommands()
        {
            AssertCommandsRegistered(
                "settings.save",
                "settings.reset",
                "settings.export",
                "settings.import",
                "settings.theme"
            );
        }

        [TestMethod]
        public void Commands_HaveCorrectCategory()
        {
            AssertCommandMetadata("settings.save", "Save Settings", "Settings");
            AssertCommandMetadata("settings.reset", "Reset Settings", "Settings");
            AssertCommandMetadata("settings.theme", "Change Theme", "Settings");
        }

        #endregion

        #region Save Tests

        [TestMethod]
        public async Task SaveSettings_CallsSettingsService()
        {
            // Arrange
            var settings = new SettingsData();
            MockSettingsService.Setup(s => s.LoadSettingsAsync(It.IsAny<CancellationToken>()))
                .ReturnsAsync(settings);

            // Act
            await Registry.ExecuteAsync("settings.save");

            // Assert
            MockSettingsService.Verify(s => s.SaveSettingsAsync(
                It.IsAny<SettingsData>(), It.IsAny<CancellationToken>()), Times.Once);
        }

        #endregion

        #region Reset Tests

        [TestMethod]
        public async Task ResetSettings_WithConfirmation_ResetsSettings()
        {
            // Arrange
            SetupConfirmationDialog(true);

            // Act
            await Registry.ExecuteAsync("settings.reset");

            // Assert
            MockSettingsService.Verify(s => s.ResetSettingsAsync(
                It.IsAny<CancellationToken>()), Times.Once);
        }

        [TestMethod]
        public async Task ResetSettings_UserCancels_DoesNotReset()
        {
            // Arrange
            SetupConfirmationDialog(false);

            // Act
            await Registry.ExecuteAsync("settings.reset");

            // Assert
            MockSettingsService.Verify(s => s.ResetSettingsAsync(
                It.IsAny<CancellationToken>()), Times.Never);
        }

        #endregion

        #region Export Tests

        [TestMethod]
        public async Task ExportSettings_WithPath_ExportsToFile()
        {
            // Arrange
            var settings = new SettingsData();
            MockSettingsService.Setup(s => s.LoadSettingsAsync(It.IsAny<CancellationToken>()))
                .ReturnsAsync(settings);
            SetupSaveFileDialog(@"C:\settings.json");

            // Act
            await Registry.ExecuteAsync("settings.export");

            // Assert
            MockSettingsService.Verify(s => s.LoadSettingsAsync(
                It.IsAny<CancellationToken>()), Times.Once);
        }

        [TestMethod]
        public async Task ExportSettings_UserCancels_DoesNotExport()
        {
            // Arrange
            SetupSaveFileDialog(null);

            // Act
            await Registry.ExecuteAsync("settings.export");

            // Assert
            MockSettingsService.Verify(s => s.LoadSettingsAsync(
                It.IsAny<CancellationToken>()), Times.Never);
        }

        #endregion

        #region Import Tests

        [TestMethod]
        public async Task ImportSettings_UserCancels_DoesNotImport()
        {
            // Arrange
            SetupFileDialog(null);

            // Act
            await Registry.ExecuteAsync("settings.import");

            // Assert
            MockSettingsService.Verify(s => s.SaveSettingsAsync(
                It.IsAny<SettingsData>(), It.IsAny<CancellationToken>()), Times.Never);
        }

        #endregion

        #region Theme Toggle Tests

        [TestMethod]
        public async Task ToggleTheme_ExecutesWithoutError()
        {
            // Arrange
            var settings = new SettingsData();
            MockSettingsService.Setup(s => s.LoadSettingsAsync(It.IsAny<CancellationToken>()))
                .ReturnsAsync(settings);

            // Act & Assert - should not throw
            await Registry.ExecuteAsync("settings.theme");
        }

        #endregion

        #region Event Tests

        [TestMethod]
        public async Task SettingsChanged_RaisedAfterReset()
        {
            // Arrange
            SetupConfirmationDialog(true);

            bool eventRaised = false;
            _handler.SettingsChanged += (s, e) => eventRaised = true;

            // Act
            await Registry.ExecuteAsync("settings.reset");

            // Assert
            Assert.IsTrue(eventRaised);
        }

        [TestMethod]
        public async Task SettingsChanged_RaisedAfterThemeToggle()
        {
            // Arrange
            var settings = new SettingsData();
            MockSettingsService.Setup(s => s.LoadSettingsAsync(It.IsAny<CancellationToken>()))
                .ReturnsAsync(settings);

            bool eventRaised = false;
            _handler.SettingsChanged += (s, e) => eventRaised = true;

            // Act
            await Registry.ExecuteAsync("settings.theme");

            // Assert
            Assert.IsTrue(eventRaised);
        }

        #endregion
    }
}
