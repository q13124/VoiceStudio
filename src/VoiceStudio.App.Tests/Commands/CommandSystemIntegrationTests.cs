using Microsoft.VisualStudio.TestTools.UnitTesting;
using Moq;
using System;
using System.Linq;
using System.Threading;
using System.Threading.Tasks;
using VoiceStudio.App.Commands;
using VoiceStudio.App.Core.Commands;
using VoiceStudio.App.Services;
using VoiceStudio.Core.Services;

namespace VoiceStudio.App.Tests.Commands
{
    /// <summary>
    /// Integration tests for the complete command system.
    /// Tests that all registered commands can be retrieved and executed without exceptions.
    /// </summary>
    [TestClass]
    [TestCategory("Commands")]
    [TestCategory("Integration")]
    public class CommandSystemIntegrationTests
    {
        private UnifiedCommandRegistry _registry = null!;
        private CommandRouter _router = null!;

        [TestInitialize]
        public void Setup()
        {
            _registry = new UnifiedCommandRegistry();
            _router = new CommandRouter(_registry);
        }

        #region Navigation Command Tests

        [TestMethod]
        public async Task NavigationCommands_AllRegistered_CanExecute()
        {
            // Arrange
            var mockNavService = new Mock<INavigationService>();
            mockNavService.Setup(x => x.NavigateToPanelAsync(It.IsAny<string>(), It.IsAny<System.Collections.Generic.Dictionary<string, object>>(), It.IsAny<CancellationToken>()))
                .Returns(Task.CompletedTask);
            mockNavService.Setup(x => x.CanNavigateBack()).Returns(false);

            var handler = new NavigationHandler(_registry, mockNavService.Object);

            var navCommands = new[]
            {
                "nav.studio", "nav.profiles", "nav.library", "nav.effects",
                "nav.train", "nav.analyze", "nav.settings", "nav.logs",
                "nav.synthesis", "nav.timeline", "nav.home"
            };

            // Act & Assert
            foreach (var commandId in navCommands)
            {
                Assert.IsTrue(_registry.IsRegistered(commandId), $"Command '{commandId}' should be registered");
                Assert.IsTrue(_registry.CanExecute(commandId, null), $"Command '{commandId}' should be executable");

                // Execute should not throw
                await _registry.ExecuteAsync(commandId, null, CancellationToken.None);
            }
        }

        [TestMethod]
        public void NavigationHandler_RegistersExpectedCommandCount()
        {
            // Arrange
            var mockNavService = new Mock<INavigationService>();
            var handler = new NavigationHandler(_registry, mockNavService.Object);

            // Act
            var navCommands = _registry.GetAllCommands()
                .Where(d => d.Id.StartsWith("nav."))
                .ToList();

            // Assert - should have at least 10 navigation commands
            Assert.IsTrue(navCommands.Count >= 10, $"Expected at least 10 nav commands, found {navCommands.Count}");
        }

        #endregion

        #region File Command Tests

        [TestMethod]
        public void FileCommands_AllRegistered_HaveDescriptors()
        {
            // Arrange
            var mockProjectRepo = new Mock<IProjectRepository>();
            var mockDialogService = new Mock<IDialogService>();
            var handler = new FileOperationsHandler(_registry, mockProjectRepo.Object, mockDialogService.Object);

            var fileCommands = new[]
            {
                "file.new", "file.open", "file.save", "file.saveAs",
                "file.import", "file.export", "file.close"
            };

            // Act & Assert
            foreach (var commandId in fileCommands)
            {
                Assert.IsTrue(_registry.IsRegistered(commandId), $"Command '{commandId}' should be registered");

                var descriptor = _registry.GetDescriptor(commandId);
                Assert.IsNotNull(descriptor, $"Descriptor for '{commandId}' should not be null");
                Assert.IsFalse(string.IsNullOrEmpty(descriptor.Title), $"Title for '{commandId}' should not be empty");
            }
        }

        #endregion

        #region Playback Command Tests

        [TestMethod]
        public void PlaybackCommands_AllRegistered_HaveDescriptors()
        {
            // Arrange
            var mockAudioPlayer = new Mock<IAudioPlayerService>();
            var handler = new PlaybackOperationsHandler(_registry, mockAudioPlayer.Object);

            var playbackCommands = new[]
            {
                "playback.play", "playback.pause", "playback.toggle",
                "playback.stop", "playback.record"
            };

            // Act & Assert
            foreach (var commandId in playbackCommands)
            {
                Assert.IsTrue(_registry.IsRegistered(commandId), $"Command '{commandId}' should be registered");

                var descriptor = _registry.GetDescriptor(commandId);
                Assert.IsNotNull(descriptor, $"Descriptor for '{commandId}' should not be null");
            }
        }

        #endregion

        #region CommandRouter Tests

        [TestMethod]
        public async Task CommandRouter_ExecuteAsync_InvokesRegisteredCommand()
        {
            // Arrange
            var wasExecuted = false;
            _registry.Register(
                new CommandDescriptor { Id = "test.router", Title = "Test Router", Category = "Test" },
                async (param, ct) => { wasExecuted = true; await Task.CompletedTask; },
                _ => true
            );

            // Act
            await _router.ExecuteAsync("test.router");

            // Assert
            Assert.IsTrue(wasExecuted, "Command should have been executed via router");
        }

        [TestMethod]
        public async Task CommandRouter_ExecuteSafeAsync_ReturnsFalseOnError()
        {
            // Arrange
            _registry.Register(
                new CommandDescriptor { Id = "test.error", Title = "Error Command", Category = "Test" },
                async (param, ct) => { await Task.CompletedTask; throw new InvalidOperationException("Test error"); },
                _ => true
            );

            // Act
            var result = await _router.ExecuteSafeAsync("test.error");

            // Assert
            Assert.IsFalse(result, "ExecuteSafeAsync should return false when command throws");
        }

        [TestMethod]
        public void CommandRouter_CanExecute_DelegatestoRegistry()
        {
            // Arrange
            _registry.Register(
                new CommandDescriptor { Id = "test.canexec", Title = "CanExecute Test", Category = "Test" },
                _ => { },
                param => param is string s && s == "allowed"
            );

            // Act & Assert
            Assert.IsTrue(_router.CanExecute("test.canexec", "allowed"));
            Assert.IsFalse(_router.CanExecute("test.canexec", "denied"));
        }

        #endregion

        #region Full System Integration Tests

        [TestMethod]
        public void FullSystem_AllHandlersRegistered_HaveUniqueCommandIds()
        {
            // Arrange - Register all handlers
            var mockNavService = new Mock<INavigationService>();
            var mockProjectRepo = new Mock<IProjectRepository>();
            var mockDialogService = new Mock<IDialogService>();
            var mockAudioPlayer = new Mock<IAudioPlayerService>();

            var navHandler = new NavigationHandler(_registry, mockNavService.Object);
            var fileHandler = new FileOperationsHandler(_registry, mockProjectRepo.Object, mockDialogService.Object);
            var playbackHandler = new PlaybackOperationsHandler(_registry, mockAudioPlayer.Object);

            // Act
            var allDescriptors = _registry.GetAllCommands().ToList();
            var duplicateIds = allDescriptors
                .GroupBy(d => d.Id)
                .Where(g => g.Count() > 1)
                .Select(g => g.Key)
                .ToList();

            // Assert
            Assert.AreEqual(0, duplicateIds.Count,
                $"Found duplicate command IDs: {string.Join(", ", duplicateIds)}");
        }

        [TestMethod]
        public void FullSystem_AllCommands_HaveCategory()
        {
            // Arrange - Register all handlers
            var mockNavService = new Mock<INavigationService>();
            var mockProjectRepo = new Mock<IProjectRepository>();
            var mockDialogService = new Mock<IDialogService>();
            var mockAudioPlayer = new Mock<IAudioPlayerService>();

            var navHandler = new NavigationHandler(_registry, mockNavService.Object);
            var fileHandler = new FileOperationsHandler(_registry, mockProjectRepo.Object, mockDialogService.Object);
            var playbackHandler = new PlaybackOperationsHandler(_registry, mockAudioPlayer.Object);

            // Act
            var allDescriptors = _registry.GetAllCommands().ToList();
            var missingCategory = allDescriptors
                .Where(d => string.IsNullOrEmpty(d.Category))
                .Select(d => d.Id)
                .ToList();

            // Assert
            Assert.AreEqual(0, missingCategory.Count,
                $"Commands missing category: {string.Join(", ", missingCategory)}");
        }

        [TestMethod]
        public void FullSystem_CommandsWithShortcuts_HaveValidFormat()
        {
            // Arrange - Register navigation handler (has shortcuts)
            var mockNavService = new Mock<INavigationService>();
            var handler = new NavigationHandler(_registry, mockNavService.Object);

            // Act
            var commandsWithShortcuts = _registry.GetAllCommands()
                .Where(d => !string.IsNullOrEmpty(d.KeyboardShortcut))
                .ToList();

            // Assert
            Assert.IsTrue(commandsWithShortcuts.Count > 0, "Should have commands with keyboard shortcuts");

            foreach (var cmd in commandsWithShortcuts)
            {
                // Shortcuts should contain modifier keys or be single keys
                var shortcut = cmd.KeyboardShortcut!;
                var isValid = shortcut.Contains("Ctrl") ||
                              shortcut.Contains("Alt") ||
                              shortcut.Contains("Shift") ||
                              shortcut.Length <= 10; // Single keys like "Space", "Home"

                Assert.IsTrue(isValid,
                    $"Command '{cmd.Id}' has invalid shortcut format: '{shortcut}'");
            }
        }

        #endregion

        #region Health and Status Tests

        [TestMethod]
        public void Registry_GetHealthReport_ReturnsValidData()
        {
            // Arrange
            _registry.Register(
                new CommandDescriptor { Id = "health.test", Title = "Health Test", Category = "Test" },
                _ => { },
                null
            );

            // Act
            var report = _registry.GetHealthReport();

            // Assert
            Assert.IsNotNull(report);
            Assert.IsTrue(report.Count > 0);
        }

        [TestMethod]
        public async Task Registry_AfterExecution_TracksStatus()
        {
            // Arrange
            _registry.Register(
                new CommandDescriptor { Id = "status.test", Title = "Status Test", Category = "Test" },
                async (param, ct) => await Task.Delay(1, ct),
                null
            );

            // Act
            await _registry.ExecuteAsync("status.test");
            var status = _registry.GetStatus("status.test");

            // Assert
            // After successful execution, status should be Working
            Assert.AreEqual(CommandStatus.Working, status);
        }

        #endregion
    }
}
