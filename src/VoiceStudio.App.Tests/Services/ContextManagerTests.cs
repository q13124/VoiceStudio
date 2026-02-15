// VoiceStudio - Panel Architecture Phase E: Unit Tests
// ContextManager unit tests

using Microsoft.VisualStudio.TestTools.UnitTesting;
using System;
using System.Collections.Generic;
using System.Threading;
using VoiceStudio.App.Services;
using VoiceStudio.Core.Events;
using VoiceStudio.Core.Services;

namespace VoiceStudio.App.Tests.Services
{
    /// <summary>
    /// Unit tests for the ContextManager class.
    /// Tests state management, event publishing, and cross-panel coordination.
    /// </summary>
    [TestClass]
    public class ContextManagerTests
    {
        private MockEventAggregator _mockEventAggregator = null!;
        private ContextManager _contextManager = null!;

        [TestInitialize]
        public void TestInitialize()
        {
            _mockEventAggregator = new MockEventAggregator();
            _contextManager = new ContextManager(_mockEventAggregator);
        }

        [TestCleanup]
        public void TestCleanup()
        {
            _contextManager = null!;
            _mockEventAggregator = null!;
        }

        #region Initialization Tests

        [TestMethod]
        public void ContextManager_Initialization_Succeeds()
        {
            // Assert
            Assert.IsNotNull(_contextManager);
        }

        [TestMethod]
        [ExpectedException(typeof(ArgumentNullException))]
        public void ContextManager_NullEventAggregator_ThrowsArgumentNullException()
        {
            // Act
            _ = new ContextManager(null!);
        }

        [TestMethod]
        public void ContextManager_InitialState_IsNull()
        {
            // Assert
            Assert.IsNull(_contextManager.ActiveProfileId);
            Assert.IsNull(_contextManager.ActiveProfileName);
            Assert.IsNull(_contextManager.ActiveProjectId);
            Assert.IsNull(_contextManager.ActiveProjectName);
            Assert.IsNull(_contextManager.ActiveAssetId);
            Assert.IsNull(_contextManager.ActiveEngineId);
        }

        #endregion

        #region SetActiveProfile Tests

        [TestMethod]
        public void SetActiveProfile_WithValidProfile_UpdatesState()
        {
            // Arrange
            const string profileId = "profile-123";
            const string profileName = "Test Profile";

            // Act
            _contextManager.SetActiveProfile(profileId, profileName);

            // Assert
            Assert.AreEqual(profileId, _contextManager.ActiveProfileId);
            Assert.AreEqual(profileName, _contextManager.ActiveProfileName);
        }

        [TestMethod]
        public void SetActiveProfile_WithValidProfile_PublishesEvent()
        {
            // Arrange
            const string profileId = "profile-123";
            const string profileName = "Test Profile";

            // Act
            _contextManager.SetActiveProfile(profileId, profileName);

            // Assert
            Assert.IsTrue(_mockEventAggregator.PublishedEvents.Count > 0);
            var lastEvent = _mockEventAggregator.PublishedEvents[^1];
            Assert.IsInstanceOfType(lastEvent, typeof(ProfileSelectedEvent));
        }

        [TestMethod]
        public void SetActiveProfile_WithNull_ClearsState()
        {
            // Arrange
            _contextManager.SetActiveProfile("profile-123", "Test");

            // Act
            _contextManager.SetActiveProfile(null, null);

            // Assert
            Assert.IsNull(_contextManager.ActiveProfileId);
            Assert.IsNull(_contextManager.ActiveProfileName);
        }

        [TestMethod]
        public void SetActiveProfile_SameProfile_DoesNotPublishEvent()
        {
            // Arrange
            const string profileId = "profile-123";
            const string profileName = "Test Profile";
            _contextManager.SetActiveProfile(profileId, profileName);
            var eventCountBefore = _mockEventAggregator.PublishedEvents.Count;

            // Act
            _contextManager.SetActiveProfile(profileId, profileName);

            // Assert - should not publish duplicate event
            Assert.AreEqual(eventCountBefore, _mockEventAggregator.PublishedEvents.Count);
        }

        #endregion

        #region SetActiveProject Tests

        [TestMethod]
        public void SetActiveProject_WithValidProject_UpdatesState()
        {
            // Arrange
            const string projectId = "project-456";
            const string projectName = "Test Project";

            // Act
            _contextManager.SetActiveProject(projectId, projectName);

            // Assert
            Assert.AreEqual(projectId, _contextManager.ActiveProjectId);
            Assert.AreEqual(projectName, _contextManager.ActiveProjectName);
        }

        [TestMethod]
        public void SetActiveProject_WithNull_ClearsState()
        {
            // Arrange
            _contextManager.SetActiveProject("project-456", "Test");

            // Act
            _contextManager.SetActiveProject(null, null);

            // Assert
            Assert.IsNull(_contextManager.ActiveProjectId);
            Assert.IsNull(_contextManager.ActiveProjectName);
        }

        #endregion

        #region SetActiveAsset Tests

        [TestMethod]
        public void SetActiveAsset_WithValidAsset_UpdatesState()
        {
            // Arrange
            const string assetId = "asset-789";
            const string assetType = "audio";

            // Act
            _contextManager.SetActiveAsset(assetId, assetType);

            // Assert
            Assert.AreEqual(assetId, _contextManager.ActiveAssetId);
            Assert.AreEqual(assetType, _contextManager.ActiveAssetType);
        }

        [TestMethod]
        public void SetActiveAsset_PublishesAssetSelectedEvent()
        {
            // Arrange
            const string assetId = "asset-789";
            const string assetType = "audio";

            // Act
            _contextManager.SetActiveAsset(assetId, assetType);

            // Assert
            Assert.IsTrue(_mockEventAggregator.PublishedEvents.Count > 0);
            var lastEvent = _mockEventAggregator.PublishedEvents[^1];
            Assert.IsInstanceOfType(lastEvent, typeof(AssetSelectedEvent));
        }

        #endregion

        #region SetActiveEngine Tests

        [TestMethod]
        public void SetActiveEngine_WithValidEngine_UpdatesState()
        {
            // Arrange
            const string engineId = "xtts";

            // Act
            _contextManager.SetActiveEngine(engineId);

            // Assert
            Assert.AreEqual(engineId, _contextManager.ActiveEngineId);
        }

        [TestMethod]
        public void SetActiveEngine_PublishesEngineChangedEvent()
        {
            // Arrange
            const string engineId = "xtts";

            // Act
            _contextManager.SetActiveEngine(engineId);

            // Assert
            Assert.IsTrue(_mockEventAggregator.PublishedEvents.Count > 0);
            var lastEvent = _mockEventAggregator.PublishedEvents[^1];
            Assert.IsInstanceOfType(lastEvent, typeof(EngineChangedEvent));
        }

        #endregion

        #region ContextChanged Event Tests

        [TestMethod]
        public void SetActiveProfile_RaisesContextChangedEvent()
        {
            // Arrange
            var eventRaised = false;
            ContextChangedEventArgs? args = null;
            _contextManager.ContextChanged += (s, e) =>
            {
                eventRaised = true;
                args = e;
            };

            // Act
            _contextManager.SetActiveProfile("profile-123", "Test Profile");

            // Assert
            Assert.IsTrue(eventRaised);
            Assert.IsNotNull(args);
            Assert.AreEqual("ActiveProfileId", args.PropertyName);
            Assert.AreEqual("profile-123", args.NewValue);
        }

        [TestMethod]
        public void ContextChanged_EventArgs_ContainsCorrectIntent()
        {
            // Arrange
            ContextChangedEventArgs? args = null;
            _contextManager.ContextChanged += (s, e) => args = e;

            // Act - Using Navigation which is a valid InteractionIntent
            _contextManager.SetActiveProfile("profile-123", "Test Profile", InteractionIntent.Navigation);

            // Assert
            Assert.IsNotNull(args);
            Assert.AreEqual(InteractionIntent.Navigation, args.Intent);
        }

        #endregion

        #region Thread Safety Tests

        [TestMethod]
        public void ContextManager_ConcurrentAccess_IsThreadSafe()
        {
            // Arrange
            var exceptions = new List<Exception>();
            var threads = new List<Thread>();

            // Act - Multiple threads setting different values
            for (int i = 0; i < 10; i++)
            {
                var index = i;
                var thread = new Thread(() =>
                {
                    try
                    {
                        for (int j = 0; j < 100; j++)
                        {
                            _contextManager.SetActiveProfile($"profile-{index}-{j}", $"Profile {index}-{j}");
                            _contextManager.SetActiveEngine($"engine-{index}-{j}");
                            _ = _contextManager.ActiveProfileId;
                            _ = _contextManager.ActiveEngineId;
                        }
                    }
                    catch (Exception ex)
                    {
                        lock (exceptions)
                        {
                            exceptions.Add(ex);
                        }
                    }
                });
                threads.Add(thread);
            }

            foreach (var thread in threads)
            {
                thread.Start();
            }

            foreach (var thread in threads)
            {
                thread.Join();
            }

            // Assert - No exceptions during concurrent access
            Assert.AreEqual(0, exceptions.Count, $"Thread safety violation: {string.Join(", ", exceptions)}");
        }

        #endregion

        #region State Persistence Tests

        [TestMethod]
        public void ContextManager_MultipleUpdates_RetainsLatestValues()
        {
            // Arrange & Act
            _contextManager.SetActiveProfile("profile-1", "Profile 1");
            _contextManager.SetActiveProfile("profile-2", "Profile 2");
            _contextManager.SetActiveProfile("profile-3", "Profile 3");

            // Assert - only the latest value is retained
            Assert.AreEqual("profile-3", _contextManager.ActiveProfileId);
            Assert.AreEqual("Profile 3", _contextManager.ActiveProfileName);
        }

        [TestMethod]
        public void ContextManager_ClearProfile_DoesNotAffectOtherState()
        {
            // Arrange
            _contextManager.SetActiveProfile("profile-123", "Test Profile");
            _contextManager.SetActiveEngine("xtts");
            _contextManager.SetActiveAsset("asset-456", "audio");

            // Act
            _contextManager.SetActiveProfile(null, null);

            // Assert - profile cleared but engine and asset remain
            Assert.IsNull(_contextManager.ActiveProfileId);
            Assert.AreEqual("xtts", _contextManager.ActiveEngineId);
            Assert.AreEqual("asset-456", _contextManager.ActiveAssetId);
        }

        #endregion
    }

    /// <summary>
    /// Mock implementation of IEventAggregator for testing.
    /// </summary>
    internal class MockEventAggregator : IEventAggregator
    {
        public List<object> PublishedEvents { get; } = new();

        public void Publish<TEvent>(TEvent eventData) where TEvent : class
        {
            PublishedEvents.Add(eventData);
        }

        public System.Threading.Tasks.Task PublishAsync<TEvent>(TEvent eventMessage) where TEvent : class
        {
            PublishedEvents.Add(eventMessage);
            return System.Threading.Tasks.Task.CompletedTask;
        }

        public ISubscriptionToken Subscribe<TEvent>(Action<TEvent> handler) where TEvent : class
        {
            return new MockSubscriptionToken(typeof(TEvent));
        }

        public ISubscriptionToken Subscribe<TEvent>(Func<TEvent, System.Threading.Tasks.Task> handler) where TEvent : class
        {
            return new MockSubscriptionToken(typeof(TEvent));
        }

        public void Unsubscribe(ISubscriptionToken token)
        {
            // No-op for testing
        }

        public void UnsubscribeAll(object subscriber)
        {
            // No-op for testing
        }

        private class MockSubscriptionToken : ISubscriptionToken
        {
            public bool IsActive { get; private set; } = true;
            public Type EventType { get; }

            public MockSubscriptionToken(Type eventType)
            {
                EventType = eventType;
            }

            public void Dispose()
            {
                IsActive = false;
            }
        }
    }
}
