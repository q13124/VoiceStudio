using Microsoft.VisualStudio.TestTools.UnitTesting;
using Moq;
using System.Threading;
using System.Threading.Tasks;
using VoiceStudio.App.Commands;
using VoiceStudio.App.Core.Commands;
using VoiceStudio.Core.Models;

namespace VoiceStudio.App.Tests.Commands
{
    /// <summary>
    /// Unit tests for FileOperationsHandler.
    /// </summary>
    [TestClass]
    [TestCategory("Commands")]
    public class FileOperationsHandlerTests : CommandHandlerTestBase
    {
        private FileOperationsHandler _handler = null!;

        [TestInitialize]
        public override void SetupBase()
        {
            base.SetupBase();
            _handler = new FileOperationsHandler(
                Registry,
                MockProjectRepository.Object,
                MockDialogService.Object,
                null);
        }

        #region Registration Tests

        [TestMethod]
        public void Constructor_RegistersAllFileCommands()
        {
            AssertCommandsRegistered(
                "file.new",
                "file.open",
                "file.save",
                "file.saveAs",
                "file.import",
                "file.export",
                "file.close"
            );
        }

        [TestMethod]
        public void Commands_HaveCorrectCategory()
        {
            AssertCommandMetadata("file.new", "New Project", "File");
            AssertCommandMetadata("file.open", "Open Project", "File");
            AssertCommandMetadata("file.save", "Save Project", "File");
        }

        #endregion

        #region New Project Tests

        [TestMethod]
        public async Task NewProject_WithValidName_CreatesProject()
        {
            // Arrange
            SetupInputDialog("My New Project");

            // Act
            await Registry.ExecuteAsync("file.new");

            // Assert
            Assert.IsNotNull(_handler.CurrentProject);
            Assert.AreEqual("My New Project", _handler.CurrentProject.Name);
        }

        [TestMethod]
        public async Task NewProject_UserCancels_DoesNotCreateProject()
        {
            // Arrange
            SetupInputDialog(null);

            // Act
            await Registry.ExecuteAsync("file.new");

            // Assert
            Assert.IsNull(_handler.CurrentProject);
        }

        [TestMethod]
        public async Task NewProject_EmptyName_DoesNotCreateProject()
        {
            // Arrange
            SetupInputDialog("");

            // Act
            await Registry.ExecuteAsync("file.new");

            // Assert
            Assert.IsNull(_handler.CurrentProject);
        }

        #endregion

        #region Open Project Tests

        [TestMethod]
        public async Task OpenProject_WithValidPath_LoadsProject()
        {
            // Arrange
            var testProject = new Project { Id = "test-id", Name = "Test Project" };
            SetupFileDialog("test-path");
            MockProjectRepository.Setup(r => r.OpenAsync(It.IsAny<string>(), It.IsAny<CancellationToken>()))
                .ReturnsAsync(testProject);

            // Act
            await Registry.ExecuteAsync("file.open");

            // Assert
            Assert.IsNotNull(_handler.CurrentProject);
            Assert.AreEqual("Test Project", _handler.CurrentProject.Name);
        }

        [TestMethod]
        public async Task OpenProject_UserCancels_DoesNotLoadProject()
        {
            // Arrange
            SetupFileDialog(null);

            // Act
            await Registry.ExecuteAsync("file.open");

            // Assert
            Assert.IsNull(_handler.CurrentProject);
        }

        #endregion

        #region Save Project Tests

        [TestMethod]
        public async Task SaveProject_WithCurrentProject_SavesSuccessfully()
        {
            // Arrange - First create a project
            SetupInputDialog("Project to Save");
            await Registry.ExecuteAsync("file.new");
            Assert.IsTrue(_handler.HasUnsavedChanges);

            // Act
            await Registry.ExecuteAsync("file.save");

            // Assert
            Assert.IsFalse(_handler.HasUnsavedChanges);
            MockProjectRepository.Verify(r => r.SaveAsync(
                It.Is<Project>(p => p.Name == "Project to Save"),
                It.IsAny<CancellationToken>()), Times.Once);
        }

        [TestMethod]
        public void SaveProject_NoCurrentProject_CannotExecute()
        {
            // Assert
            AssertCannotExecute("file.save");
        }

        #endregion

        #region Save As Tests

        [TestMethod]
        public async Task SaveAs_WithNewName_CreatesNewProject()
        {
            // Arrange - First create a project
            SetupInputDialog("Original Project");
            await Registry.ExecuteAsync("file.new");

            // Now set up for save as
            SetupInputDialog("Renamed Project");

            // Act
            await Registry.ExecuteAsync("file.saveAs");

            // Assert
            Assert.AreEqual("Renamed Project", _handler.CurrentProject?.Name);
        }

        #endregion

        #region Close Project Tests

        [TestMethod]
        public async Task CloseProject_ClosesCurrentProject()
        {
            // Arrange - First create a project
            SetupInputDialog("Project to Close");
            await Registry.ExecuteAsync("file.new");
            Assert.IsNotNull(_handler.CurrentProject);

            // Don't prompt to save
            SetupConfirmationDialog(false);

            // Act
            await Registry.ExecuteAsync("file.close");

            // Assert
            Assert.IsNull(_handler.CurrentProject);
        }

        #endregion

        #region Dirty State Tests

        [TestMethod]
        public void MarkDirty_SetsHasUnsavedChanges()
        {
            // Act
            _handler.MarkDirty();

            // Assert
            Assert.IsTrue(_handler.HasUnsavedChanges);
        }

        #endregion
    }
}
