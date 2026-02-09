using Microsoft.VisualStudio.TestTools.UnitTesting;
using Moq;
using System.Collections.Generic;
using System.Threading;
using System.Threading.Tasks;
using VoiceStudio.App.Commands;
using VoiceStudio.App.Core.Commands;
using VoiceStudio.Core.Models;

namespace VoiceStudio.App.Tests.Commands
{
    /// <summary>
    /// Unit tests for ProfileOperationsHandler.
    /// </summary>
    [TestClass]
    [TestCategory("Commands")]
    public class ProfileOperationsHandlerTests : CommandHandlerTestBase
    {
        private ProfileOperationsHandler _handler = null!;

        [TestInitialize]
        public override void SetupBase()
        {
            base.SetupBase();
            _handler = new ProfileOperationsHandler(
                Registry,
                MockProfilesUseCase.Object,
                MockDialogService.Object,
                null);
        }

        #region Registration Tests

        [TestMethod]
        public void Constructor_RegistersAllProfileCommands()
        {
            AssertCommandsRegistered(
                "profile.create",
                "profile.edit",
                "profile.delete",
                "profile.save",
                "profile.load",
                "profile.clone",
                "profile.select"
            );
        }

        [TestMethod]
        public void Commands_HaveCorrectCategory()
        {
            AssertCommandMetadata("profile.create", "Create Profile", "Profile");
            AssertCommandMetadata("profile.edit", "Edit Profile", "Profile");
            AssertCommandMetadata("profile.delete", "Delete Profile", "Profile");
        }

        #endregion

        #region Create Profile Tests

        [TestMethod]
        public async Task CreateProfile_WithValidName_CreatesProfile()
        {
            // Arrange
            var testProfile = new VoiceProfile { Id = "new-id", Name = "New Voice" };
            SetupInputDialog("New Voice");
            MockProfilesUseCase.Setup(u => u.CreateAsync(
                It.IsAny<string>(), It.IsAny<CancellationToken>()))
                .ReturnsAsync(testProfile);

            // Act
            await Registry.ExecuteAsync("profile.create");

            // Assert
            Assert.IsNotNull(_handler.SelectedProfile);
            Assert.AreEqual("New Voice", _handler.SelectedProfile.Name);
        }

        [TestMethod]
        public async Task CreateProfile_UserCancels_DoesNotCreateProfile()
        {
            // Arrange
            SetupInputDialog(null);

            // Act
            await Registry.ExecuteAsync("profile.create");

            // Assert
            Assert.IsNull(_handler.SelectedProfile);
            MockProfilesUseCase.Verify(u => u.CreateAsync(
                It.IsAny<string>(), It.IsAny<CancellationToken>()), Times.Never);
        }

        #endregion

        #region Delete Profile Tests

        [TestMethod]
        public async Task DeleteProfile_WithConfirmation_DeletesProfile()
        {
            // Arrange
            var profiles = new List<VoiceProfile>
            {
                new VoiceProfile { Id = "profile-1", Name = "Test Profile" }
            };
            MockProfilesUseCase.Setup(u => u.ListAsync(It.IsAny<CancellationToken>()))
                .ReturnsAsync(profiles);
            MockProfilesUseCase.Setup(u => u.DeleteAsync(
                "profile-1", It.IsAny<CancellationToken>()))
                .ReturnsAsync(true);
            SetupConfirmationDialog(true);

            // Select the profile first
            _handler.SelectProfile(profiles[0]);

            // Act
            await Registry.ExecuteAsync("profile.delete", "profile-1");

            // Assert
            MockProfilesUseCase.Verify(u => u.DeleteAsync(
                "profile-1", It.IsAny<CancellationToken>()), Times.Once);
        }

        [TestMethod]
        public async Task DeleteProfile_UserDeclinesConfirmation_DoesNotDelete()
        {
            // Arrange
            var profiles = new List<VoiceProfile>
            {
                new VoiceProfile { Id = "profile-1", Name = "Test Profile" }
            };
            MockProfilesUseCase.Setup(u => u.ListAsync(It.IsAny<CancellationToken>()))
                .ReturnsAsync(profiles);
            SetupConfirmationDialog(false);

            _handler.SelectProfile(profiles[0]);

            // Act
            await Registry.ExecuteAsync("profile.delete", "profile-1");

            // Assert
            MockProfilesUseCase.Verify(u => u.DeleteAsync(
                It.IsAny<string>(), It.IsAny<CancellationToken>()), Times.Never);
        }

        #endregion

        #region Edit Profile Tests

        [TestMethod]
        public async Task EditProfile_WithNewName_UpdatesProfile()
        {
            // Arrange
            var profiles = new List<VoiceProfile>
            {
                new VoiceProfile { Id = "profile-1", Name = "Old Name" }
            };
            var updatedProfile = new VoiceProfile { Id = "profile-1", Name = "New Name" };

            MockProfilesUseCase.Setup(u => u.ListAsync(It.IsAny<CancellationToken>()))
                .ReturnsAsync(profiles);
            MockProfilesUseCase.Setup(u => u.UpdateAsync(
                "profile-1", "New Name", null, null, null, It.IsAny<CancellationToken>()))
                .ReturnsAsync(updatedProfile);

            SetupInputDialog("New Name");
            _handler.SelectProfile(profiles[0]);

            // Act
            await Registry.ExecuteAsync("profile.edit", "profile-1");

            // Assert
            MockProfilesUseCase.Verify(u => u.UpdateAsync(
                "profile-1", "New Name", null, null, null, It.IsAny<CancellationToken>()), Times.Once);
        }

        #endregion

        #region Clone Profile Tests

        [TestMethod]
        public async Task CloneProfile_CreatesNewProfileWithCopySuffix()
        {
            // Arrange
            var originalProfile = new VoiceProfile { Id = "orig-id", Name = "Original", Language = "en" };
            var clonedProfile = new VoiceProfile { Id = "clone-id", Name = "Original (Copy)", Language = "en" };

            var profiles = new List<VoiceProfile> { originalProfile };
            MockProfilesUseCase.Setup(u => u.ListAsync(It.IsAny<CancellationToken>()))
                .ReturnsAsync(profiles);
            // Use flexible matchers for CreateAsync
            MockProfilesUseCase.Setup(u => u.CreateAsync(
                It.IsAny<string>(),
                It.IsAny<string?>(),
                It.IsAny<string?>(),
                It.IsAny<List<string>?>(),
                It.IsAny<CancellationToken>()))
                .ReturnsAsync(clonedProfile);

            SetupInputDialog("Original (Copy)");
            _handler.SelectProfile(originalProfile);

            // Act
            await Registry.ExecuteAsync("profile.clone", "orig-id");

            // Assert
            Assert.AreEqual("Original (Copy)", _handler.SelectedProfile?.Name);
            MockProfilesUseCase.Verify(u => u.CreateAsync(
                "Original (Copy)",
                "en",
                It.IsAny<string?>(),
                It.IsAny<List<string>?>(),
                It.IsAny<CancellationToken>()), Times.Once);
        }

        #endregion

        #region Select Profile Tests

        [TestMethod]
        public void SelectProfile_SetsSelectedProfile()
        {
            // Arrange
            var profile = new VoiceProfile { Id = "select-id", Name = "Selected" };

            // Act
            _handler.SelectProfile(profile);

            // Assert
            Assert.AreEqual(profile, _handler.SelectedProfile);
        }

        [TestMethod]
        public async Task SelectProfile_ViaCommand_SetsSelectedProfile()
        {
            // Arrange
            var profile = new VoiceProfile { Id = "select-id", Name = "Selected" };

            // Act
            await Registry.ExecuteAsync("profile.select", profile);

            // Assert
            Assert.AreEqual(profile, _handler.SelectedProfile);
        }

        #endregion

        #region Event Tests

        [TestMethod]
        public void SelectProfile_RaisesEvent()
        {
            // Arrange
            var profile = new VoiceProfile { Id = "event-id", Name = "Event Test" };
            VoiceProfile? receivedProfile = null;
            _handler.SelectedProfileChanged += (s, p) => receivedProfile = p;

            // Act
            _handler.SelectProfile(profile);

            // Assert
            Assert.AreEqual(profile, receivedProfile);
        }

        #endregion
    }
}
