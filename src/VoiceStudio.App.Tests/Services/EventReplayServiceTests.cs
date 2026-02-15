using Microsoft.VisualStudio.TestTools.UnitTesting;
using System;
using System.Threading;
using System.Threading.Tasks;
using VoiceStudio.App.Services;
using VoiceStudio.Core.Debugging;

namespace VoiceStudio.App.Tests.Services;

[TestClass]
public class EventReplayServiceTests
{
    private EventReplayService _service = null!;

    [TestInitialize]
    public void SetUp()
    {
        // Create service without dependencies for isolated testing
        _service = new EventReplayService();
    }

    #region Initial State Tests

    [TestMethod]
    public void InitialState_IsCapturing_IsFalse()
    {
        Assert.IsFalse(_service.IsCapturing);
    }

    [TestMethod]
    public void InitialState_CapturedEventCount_IsZero()
    {
        Assert.AreEqual(0, _service.CapturedEventCount);
    }

    [TestMethod]
    public void InitialState_GetRecentBundles_ReturnsEmpty()
    {
        var bundles = _service.GetRecentBundles();
        Assert.AreEqual(0, bundles.Count);
    }

    #endregion

    #region StartCapture Tests

    [TestMethod]
    public void StartCapture_SetsIsCapturingToTrue()
    {
        // Act
        _service.StartCapture();

        // Assert
        Assert.IsTrue(_service.IsCapturing);
    }

    [TestMethod]
    public void StartCapture_WithDescription_CreatesBundle()
    {
        // Act
        _service.StartCapture("Test capture");

        // Assert
        Assert.IsTrue(_service.IsCapturing);
        var bundle = _service.StopCapture();
        Assert.AreEqual("Test capture", bundle.Description);
    }

    [TestMethod]
    public void StartCapture_RaisesCaptureStartedEvent()
    {
        // Arrange
        var eventRaised = false;
        _service.CaptureStarted += (s, e) => eventRaised = true;

        // Act
        _service.StartCapture();

        // Assert
        Assert.IsTrue(eventRaised);
    }

    [TestMethod]
    public void StartCapture_WhenAlreadyCapturing_DoesNotRestart()
    {
        // Arrange
        _service.StartCapture("First");
        _service.RecordEvent("TestEvent", null);

        // Act - try to start another capture
        _service.StartCapture("Second");

        // Assert - original capture should still be active with the first event
        var bundle = _service.StopCapture();
        Assert.AreEqual("First", bundle.Description);
        Assert.AreEqual(1, bundle.Events.Count);
    }

    #endregion

    #region StopCapture Tests

    [TestMethod]
    public void StopCapture_SetsIsCapturingToFalse()
    {
        // Arrange
        _service.StartCapture();

        // Act
        _service.StopCapture();

        // Assert
        Assert.IsFalse(_service.IsCapturing);
    }

    [TestMethod]
    public void StopCapture_ReturnsBundle()
    {
        // Arrange
        _service.StartCapture("Test");

        // Act
        var bundle = _service.StopCapture();

        // Assert
        Assert.IsNotNull(bundle);
        Assert.AreEqual("Test", bundle.Description);
    }

    [TestMethod]
    public void StopCapture_RaisesCaptureStoppedEvent()
    {
        // Arrange
        EventReplayBundle? capturedBundle = null;
        _service.CaptureStopped += (s, e) => capturedBundle = e;
        _service.StartCapture();

        // Act
        _service.StopCapture();

        // Assert
        Assert.IsNotNull(capturedBundle);
    }

    [TestMethod]
    public void StopCapture_WhenNotCapturing_ReturnsEmptyBundle()
    {
        // Act
        var bundle = _service.StopCapture();

        // Assert
        Assert.IsNotNull(bundle);
        Assert.AreEqual(0, bundle.Events.Count);
    }

    [TestMethod]
    public void StopCapture_AddsBundleToCache()
    {
        // Arrange
        _service.StartCapture("Cached bundle");
        _service.StopCapture();

        // Act
        var bundles = _service.GetRecentBundles();

        // Assert
        Assert.AreEqual(1, bundles.Count);
        Assert.AreEqual("Cached bundle", bundles[0].Description);
    }

    #endregion

    #region RecordEvent Tests

    [TestMethod]
    public void RecordEvent_WhenCapturing_AddsEvent()
    {
        // Arrange
        _service.StartCapture();

        // Act
        _service.RecordEvent("TestEvent", new { Value = 42 });

        // Assert
        Assert.AreEqual(1, _service.CapturedEventCount);
        var bundle = _service.StopCapture();
        Assert.AreEqual(1, bundle.Events.Count);
        Assert.AreEqual("TestEvent", bundle.Events[0].EventType);
    }

    [TestMethod]
    public void RecordEvent_WhenNotCapturing_DoesNothing()
    {
        // Act
        _service.RecordEvent("TestEvent", null);

        // Assert
        Assert.AreEqual(0, _service.CapturedEventCount);
    }

    [TestMethod]
    public void RecordEvent_WithPayload_SerializesPayload()
    {
        // Arrange
        _service.StartCapture();

        // Act
        _service.RecordEvent("TestEvent", new { Name = "Test", Value = 123 });

        // Assert
        var bundle = _service.StopCapture();
        Assert.IsNotNull(bundle.Events[0].PayloadJson);
        Assert.IsTrue(bundle.Events[0].PayloadJson!.Contains("\"name\":\"Test\""));
        Assert.IsTrue(bundle.Events[0].PayloadJson!.Contains("\"value\":123"));
    }

    [TestMethod]
    public void RecordEvent_WithNullPayload_SetsPayloadJsonToNull()
    {
        // Arrange
        _service.StartCapture();

        // Act
        _service.RecordEvent("TestEvent", null);

        // Assert
        var bundle = _service.StopCapture();
        Assert.IsNull(bundle.Events[0].PayloadJson);
    }

    [TestMethod]
    public void RecordEvent_WithSourcePanel_SetsSourcePanelId()
    {
        // Arrange
        _service.StartCapture();

        // Act
        _service.RecordEvent("TestEvent", null, "SourcePanel");

        // Assert
        var bundle = _service.StopCapture();
        Assert.AreEqual("SourcePanel", bundle.Events[0].SourcePanelId);
    }

    [TestMethod]
    public void RecordEvent_WithTargetPanel_SetsTargetPanelId()
    {
        // Arrange
        _service.StartCapture();

        // Act
        _service.RecordEvent("TestEvent", null, null, "TargetPanel");

        // Assert
        var bundle = _service.StopCapture();
        Assert.AreEqual("TargetPanel", bundle.Events[0].TargetPanelId);
    }

    [TestMethod]
    public void RecordEvent_RaisesEventRecordedEvent()
    {
        // Arrange
        SerializedEvent? recordedEvent = null;
        _service.EventRecorded += (s, e) => recordedEvent = e;
        _service.StartCapture();

        // Act
        _service.RecordEvent("TestEvent", null);

        // Assert
        Assert.IsNotNull(recordedEvent);
        Assert.AreEqual("TestEvent", recordedEvent.EventType);
    }

    [TestMethod]
    public void RecordEvent_MultipleEvents_IncrementsSequenceNumber()
    {
        // Arrange
        _service.StartCapture();

        // Act
        _service.RecordEvent("Event1", null);
        _service.RecordEvent("Event2", null);
        _service.RecordEvent("Event3", null);

        // Assert
        var bundle = _service.StopCapture();
        Assert.AreEqual(3, bundle.Events.Count);
        Assert.AreEqual(0, bundle.Events[0].SequenceNumber);
        Assert.AreEqual(1, bundle.Events[1].SequenceNumber);
        Assert.AreEqual(2, bundle.Events[2].SequenceNumber);
    }

    [TestMethod]
    public void RecordEvent_SetsTimestamp()
    {
        // Arrange
        _service.StartCapture();
        var before = DateTime.UtcNow;

        // Act
        _service.RecordEvent("TestEvent", null);
        var after = DateTime.UtcNow;

        // Assert
        var bundle = _service.StopCapture();
        Assert.IsTrue(bundle.Events[0].Timestamp >= before);
        Assert.IsTrue(bundle.Events[0].Timestamp <= after);
    }

    #endregion

    #region CaptureStateSnapshot Tests

    [TestMethod]
    public void CaptureStateSnapshot_ReturnsSnapshot()
    {
        // Act
        var snapshot = _service.CaptureStateSnapshot();

        // Assert
        Assert.IsNotNull(snapshot);
    }

    [TestMethod]
    public void CaptureStateSnapshot_WithoutDependencies_ReturnsEmptySnapshot()
    {
        // Act
        var snapshot = _service.CaptureStateSnapshot();

        // Assert
        Assert.IsNull(snapshot.ActiveWorkspaceId);
        Assert.IsNull(snapshot.SelectedProfileId);
        Assert.IsNull(snapshot.SelectedAssetId);
    }

    #endregion

    #region Bundle Cache Tests

    [TestMethod]
    public void GetRecentBundles_ReturnsRequestedCount()
    {
        // Arrange
        for (int i = 0; i < 5; i++)
        {
            _service.StartCapture($"Bundle {i}");
            _service.StopCapture();
        }

        // Act
        var bundles = _service.GetRecentBundles(3);

        // Assert
        Assert.AreEqual(3, bundles.Count);
    }

    [TestMethod]
    public void GetRecentBundles_ReturnsLatestBundles()
    {
        // Arrange
        for (int i = 0; i < 5; i++)
        {
            _service.StartCapture($"Bundle {i}");
            _service.StopCapture();
        }

        // Act
        var bundles = _service.GetRecentBundles(3);

        // Assert - should get the last 3 (indices 2, 3, 4)
        Assert.AreEqual("Bundle 2", bundles[0].Description);
        Assert.AreEqual("Bundle 3", bundles[1].Description);
        Assert.AreEqual("Bundle 4", bundles[2].Description);
    }

    [TestMethod]
    public void ClearBundleCache_RemovesAllBundles()
    {
        // Arrange
        _service.StartCapture();
        _service.StopCapture();
        _service.StartCapture();
        _service.StopCapture();

        // Act
        _service.ClearBundleCache();

        // Assert
        Assert.AreEqual(0, _service.GetRecentBundles().Count);
    }

    [TestMethod]
    public void BundleCache_RespectsMaxCacheSize()
    {
        // Arrange - default max cache size is 5
        for (int i = 0; i < 10; i++)
        {
            _service.StartCapture($"Bundle {i}");
            _service.StopCapture();
        }

        // Act
        var bundles = _service.GetRecentBundles();

        // Assert - should only keep the last 5
        Assert.AreEqual(5, bundles.Count);
        Assert.AreEqual("Bundle 5", bundles[0].Description);
    }

    #endregion

    #region Thread Safety Tests

    [TestMethod]
    public void RecordEvent_IsThreadSafe()
    {
        // Arrange
        _service.StartCapture();
        var tasks = new Task[10];

        // Act - record events from multiple threads
        for (int i = 0; i < 10; i++)
        {
            var eventName = $"Event{i}";
            tasks[i] = Task.Run(() =>
            {
                for (int j = 0; j < 100; j++)
                {
                    _service.RecordEvent(eventName, new { Iteration = j });
                }
            });
        }

        Task.WaitAll(tasks);

        // Assert
        var bundle = _service.StopCapture();
        Assert.AreEqual(1000, bundle.Events.Count);
    }

    #endregion

    #region Full Workflow Tests

    [TestMethod]
    public void FullWorkflow_CaptureRecordStop_ProducesBundleWithAllData()
    {
        // Arrange & Act
        _service.StartCapture("Full workflow test");
        _service.RecordEvent("UserAction", new { Action = "Click" }, "Panel1");
        _service.RecordEvent("StateChange", new { NewState = "Active" }, "Panel1", "Panel2");
        _service.RecordEvent("NetworkRequest", new { Url = "/api/data" });
        var bundle = _service.StopCapture();

        // Assert
        Assert.AreEqual("Full workflow test", bundle.Description);
        Assert.AreEqual(3, bundle.Events.Count);
        
        // Initial and final state snapshots should be set
        Assert.IsNotNull(bundle.InitialState);
        Assert.IsNotNull(bundle.FinalState);
        
        // Events should be in order
        Assert.AreEqual("UserAction", bundle.Events[0].EventType);
        Assert.AreEqual("StateChange", bundle.Events[1].EventType);
        Assert.AreEqual("NetworkRequest", bundle.Events[2].EventType);
    }

    #endregion
}
