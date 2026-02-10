using Microsoft.VisualStudio.TestTools.UnitTesting;
using Moq;
using System;
using System.Threading.Tasks;
using VoiceStudio.App.ViewModels;
using VoiceStudio.App.Services;
using VoiceStudio.Core.Services;

namespace VoiceStudio.App.Tests.ViewModels
{
    /// <summary>
    /// Unit tests for RealTimeVoiceConverterViewModel and related model classes.
    /// Note: RealTimeVoiceConverterViewModel requires a WinUI DispatcherQueue that cannot be mocked in unit tests.
    /// These tests focus on the testable model classes used by the ViewModel.
    /// </summary>
    [TestClass]
    public class RealTimeVoiceConverterViewModelTests : ViewModelTestBase
    {
        #region ConverterSession Model Tests

        [TestMethod]
        public void ConverterSession_DefaultValues_AreEmpty()
        {
            // Arrange & Act
            var session = new ConverterSession();

            // Assert
            Assert.AreEqual(string.Empty, session.SessionId);
            Assert.AreEqual(string.Empty, session.SourceProfileId);
            Assert.AreEqual(string.Empty, session.TargetProfileId);
            Assert.AreEqual(string.Empty, session.Status);
            Assert.AreEqual(string.Empty, session.Created);
        }

        [TestMethod]
        public void ConverterSession_SetProperties_PersistsValues()
        {
            // Arrange & Act
            var session = new ConverterSession
            {
                SessionId = "session-001",
                SourceProfileId = "profile-source-1",
                TargetProfileId = "profile-target-1",
                Status = "active",
                Created = "2026-02-09T10:00:00Z"
            };

            // Assert
            Assert.AreEqual("session-001", session.SessionId);
            Assert.AreEqual("profile-source-1", session.SourceProfileId);
            Assert.AreEqual("profile-target-1", session.TargetProfileId);
            Assert.AreEqual("active", session.Status);
            Assert.AreEqual("2026-02-09T10:00:00Z", session.Created);
        }

        #endregion

        #region ConverterSessionItem Model Tests

        [TestMethod]
        public void ConverterSessionItem_Constructor_CopiesFromSession()
        {
            // Arrange
            var session = new ConverterSession
            {
                SessionId = "session-002",
                SourceProfileId = "source-2",
                TargetProfileId = "target-2",
                Status = "paused",
                Created = "2026-02-09T11:00:00Z"
            };

            // Act
            var item = new ConverterSessionItem(session);

            // Assert
            Assert.AreEqual("session-002", item.SessionId);
            Assert.AreEqual("source-2", item.SourceProfileId);
            Assert.AreEqual("target-2", item.TargetProfileId);
            Assert.AreEqual("paused", item.Status);
            Assert.AreEqual("2026-02-09T11:00:00Z", item.Created);
        }

        [TestMethod]
        public void ConverterSessionItem_UpdateFrom_UpdatesStatus()
        {
            // Arrange
            var originalSession = new ConverterSession
            {
                SessionId = "session-003",
                SourceProfileId = "source-3",
                TargetProfileId = "target-3",
                Status = "active",
                Created = "2026-02-09T12:00:00Z"
            };
            var item = new ConverterSessionItem(originalSession);

            var updatedSession = new ConverterSession
            {
                SessionId = "session-003",
                SourceProfileId = "source-3",
                TargetProfileId = "target-3",
                Status = "completed",
                Created = "2026-02-09T12:00:00Z"
            };

            // Act
            item.UpdateFrom(updatedSession);

            // Assert
            Assert.AreEqual("completed", item.Status);
        }

        [TestMethod]
        public void ConverterSessionItem_UpdateFrom_RaisesPropertyChanged()
        {
            // Arrange
            var session = new ConverterSession { Status = "active" };
            var item = new ConverterSessionItem(session);
            var propertyChangedRaised = false;
            string? changedProperty = null;

            item.PropertyChanged += (s, e) =>
            {
                propertyChangedRaised = true;
                changedProperty = e.PropertyName;
            };

            var updatedSession = new ConverterSession { Status = "stopped" };

            // Act
            item.UpdateFrom(updatedSession);

            // Assert
            Assert.IsTrue(propertyChangedRaised);
            Assert.AreEqual("Status", changedProperty);
        }

        [TestMethod]
        public void ConverterSessionItem_MultipleUpdates_TracksLatestStatus()
        {
            // Arrange
            var session = new ConverterSession { Status = "initializing" };
            var item = new ConverterSessionItem(session);

            // Act - simulate status progression
            item.UpdateFrom(new ConverterSession { Status = "active" });
            Assert.AreEqual("active", item.Status);

            item.UpdateFrom(new ConverterSession { Status = "paused" });
            Assert.AreEqual("paused", item.Status);

            item.UpdateFrom(new ConverterSession { Status = "completed" });

            // Assert
            Assert.AreEqual("completed", item.Status);
        }

        #endregion

        #region Edge Cases

        [TestMethod]
        public void ConverterSession_EmptySessionId_AllowsEmptyString()
        {
            // Arrange
            var session = new ConverterSession { SessionId = "" };

            // Assert - empty string is valid (no exception)
            Assert.AreEqual(string.Empty, session.SessionId);
        }

        [TestMethod]
        public void ConverterSessionItem_WithNullLikeSession_HandlesSafely()
        {
            // Arrange - session with default/empty values
            var session = new ConverterSession();
            
            // Act
            var item = new ConverterSessionItem(session);

            // Assert - should not throw, empty values are valid
            Assert.AreEqual(string.Empty, item.SessionId);
            Assert.AreEqual(string.Empty, item.Status);
        }

        #endregion
    }
}