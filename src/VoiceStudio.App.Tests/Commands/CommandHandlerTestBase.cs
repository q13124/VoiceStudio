using Microsoft.VisualStudio.TestTools.UnitTesting;
using Moq;
using System;
using System.Threading;
using System.Threading.Tasks;
using VoiceStudio.App.Core.Commands;
using VoiceStudio.App.Services;
using VoiceStudio.App.UseCases;
using VoiceStudio.Core.Services;

namespace VoiceStudio.App.Tests.Commands
{
    /// <summary>
    /// Base class for testing command handlers.
    /// Provides common mock setup and assertion helpers.
    /// </summary>
    public abstract class CommandHandlerTestBase
    {
        protected UnifiedCommandRegistry Registry { get; private set; } = null!;
        protected Mock<KeyboardShortcutService> MockShortcutService { get; private set; } = null!;
        protected Mock<IDialogService> MockDialogService { get; private set; } = null!;
        protected Mock<IProjectRepository> MockProjectRepository { get; private set; } = null!;
        protected Mock<IProfilesUseCase> MockProfilesUseCase { get; private set; } = null!;
        protected Mock<IAudioPlayerService> MockAudioPlayer { get; private set; } = null!;
        protected Mock<INavigationService> MockNavigationService { get; private set; } = null!;
        protected Mock<ISettingsService> MockSettingsService { get; private set; } = null!;

        [TestInitialize]
        public virtual void SetupBase()
        {
            MockShortcutService = new Mock<KeyboardShortcutService>();
            MockDialogService = new Mock<IDialogService>();
            MockProjectRepository = new Mock<IProjectRepository>();
            MockProfilesUseCase = new Mock<IProfilesUseCase>();
            MockAudioPlayer = new Mock<IAudioPlayerService>();
            MockNavigationService = new Mock<INavigationService>();
            MockSettingsService = new Mock<ISettingsService>();

            Registry = new UnifiedCommandRegistry(MockShortcutService.Object);

            // Setup common dialog defaults
            MockDialogService.Setup(d => d.ShowConfirmationAsync(
                It.IsAny<string>(), It.IsAny<string>(), It.IsAny<string>(), It.IsAny<string>()))
                .ReturnsAsync(true);

            MockDialogService.Setup(d => d.ShowInputAsync(
                It.IsAny<string>(), It.IsAny<string>(), It.IsAny<string>(), It.IsAny<string>()))
                .ReturnsAsync("Test Input");

            // Setup progress dialog mock
            var mockProgress = new Mock<IProgressDialog>();
            MockDialogService.Setup(d => d.ShowProgressAsync(
                It.IsAny<string>(), It.IsAny<string>(), It.IsAny<bool>()))
                .ReturnsAsync(mockProgress.Object);
        }

        #region Assertion Helpers

        /// <summary>
        /// Asserts that a command is registered in the registry.
        /// </summary>
        protected void AssertCommandRegistered(string commandId)
        {
            Assert.IsTrue(Registry.IsRegistered(commandId),
                $"Expected command '{commandId}' to be registered");
        }

        /// <summary>
        /// Asserts that multiple commands are registered.
        /// </summary>
        protected void AssertCommandsRegistered(params string[] commandIds)
        {
            foreach (var commandId in commandIds)
            {
                AssertCommandRegistered(commandId);
            }
        }

        /// <summary>
        /// Asserts that a command has the expected metadata.
        /// </summary>
        protected void AssertCommandMetadata(string commandId, string expectedTitle, string expectedCategory)
        {
            var descriptor = Registry.GetDescriptor(commandId);
            Assert.IsNotNull(descriptor, $"Command '{commandId}' not found");
            Assert.AreEqual(expectedTitle, descriptor.Title, $"Unexpected title for '{commandId}'");
            Assert.AreEqual(expectedCategory, descriptor.Category, $"Unexpected category for '{commandId}'");
        }

        /// <summary>
        /// Asserts that a command can execute.
        /// </summary>
        protected void AssertCanExecute(string commandId, object? parameter = null)
        {
            Assert.IsTrue(Registry.CanExecute(commandId, parameter),
                $"Expected command '{commandId}' to be executable");
        }

        /// <summary>
        /// Asserts that a command cannot execute.
        /// </summary>
        protected void AssertCannotExecute(string commandId, object? parameter = null)
        {
            Assert.IsFalse(Registry.CanExecute(commandId, parameter),
                $"Expected command '{commandId}' to not be executable");
        }

        /// <summary>
        /// Executes a command and asserts it completes successfully.
        /// </summary>
        protected async Task ExecuteAndAssertSuccess(string commandId, object? parameter = null)
        {
            await Registry.ExecuteAsync(commandId, parameter);
            var status = Registry.GetStatus(commandId);
            Assert.AreEqual(CommandStatus.Working, status,
                $"Expected command '{commandId}' to have Working status after execution");
        }

        /// <summary>
        /// Executes a command and asserts it throws an exception.
        /// </summary>
        protected async Task<TException> ExecuteAndAssertThrows<TException>(string commandId, object? parameter = null)
            where TException : Exception
        {
            try
            {
                await Registry.ExecuteAsync(commandId, parameter);
                Assert.Fail($"Expected command '{commandId}' to throw {typeof(TException).Name}");
                return null!; // Never reached
            }
            catch (TException ex)
            {
                return ex;
            }
        }

        #endregion

        #region Mock Setup Helpers

        /// <summary>
        /// Sets up the dialog service to return a specific input value.
        /// </summary>
        protected void SetupInputDialog(string? returnValue)
        {
            MockDialogService.Setup(d => d.ShowInputAsync(
                It.IsAny<string>(), It.IsAny<string>(), It.IsAny<string>(), It.IsAny<string>()))
                .ReturnsAsync(returnValue);
        }

        /// <summary>
        /// Sets up the dialog service to return a specific confirmation result.
        /// </summary>
        protected void SetupConfirmationDialog(bool returnValue)
        {
            MockDialogService.Setup(d => d.ShowConfirmationAsync(
                It.IsAny<string>(), It.IsAny<string>(), It.IsAny<string>(), It.IsAny<string>()))
                .ReturnsAsync(returnValue);
        }

        /// <summary>
        /// Sets up the dialog service to return a specific file path.
        /// </summary>
        protected void SetupFileDialog(string? returnValue)
        {
            MockDialogService.Setup(d => d.ShowOpenFileAsync(
                It.IsAny<string>(), It.IsAny<string[]>()))
                .ReturnsAsync(returnValue);

            MockDialogService.Setup(d => d.ShowSaveFileAsync(
                It.IsAny<string>(), It.IsAny<string>(), It.IsAny<string[]>()))
                .ReturnsAsync(returnValue);
        }

        /// <summary>
        /// Sets up the save file dialog to return a specific path.
        /// </summary>
        protected void SetupSaveFileDialog(string? returnValue)
        {
            MockDialogService.Setup(d => d.ShowSaveFileAsync(
                It.IsAny<string>(), It.IsAny<string>(), It.IsAny<string[]>()))
                .ReturnsAsync(returnValue);
        }

        #endregion
    }
}
