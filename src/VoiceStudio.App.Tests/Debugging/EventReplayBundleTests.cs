using Microsoft.VisualStudio.TestTools.UnitTesting;
using System;
using System.Collections.Generic;
using VoiceStudio.Core.Debugging;

namespace VoiceStudio.App.Tests.Debugging;

[TestClass]
public class EventReplayBundleTests
{
    #region EventReplayBundle Default Value Tests

    [TestMethod]
    public void EventReplayBundle_DefaultBundleId_IsNotEmpty()
    {
        var bundle = new EventReplayBundle();
        Assert.IsFalse(string.IsNullOrEmpty(bundle.BundleId));
        Assert.IsTrue(Guid.TryParse(bundle.BundleId, out _));
    }

    [TestMethod]
    public void EventReplayBundle_DefaultCreatedAt_IsSetToUtcNow()
    {
        var before = DateTime.UtcNow;
        var bundle = new EventReplayBundle();
        var after = DateTime.UtcNow;

        Assert.IsTrue(bundle.CreatedAt >= before);
        Assert.IsTrue(bundle.CreatedAt <= after);
    }

    [TestMethod]
    public void EventReplayBundle_DefaultEvents_IsEmptyList()
    {
        var bundle = new EventReplayBundle();
        Assert.IsNotNull(bundle.Events);
        Assert.AreEqual(0, bundle.Events.Count);
    }

    [TestMethod]
    public void EventReplayBundle_DefaultDescription_IsNull()
    {
        var bundle = new EventReplayBundle();
        Assert.IsNull(bundle.Description);
    }

    #endregion

    #region EventReplayBundle Serialization Tests

    [TestMethod]
    public void ToJson_EmptyBundle_ReturnsValidJson()
    {
        var bundle = new EventReplayBundle();
        var json = bundle.ToJson();

        Assert.IsFalse(string.IsNullOrEmpty(json));
        Assert.IsTrue(json.Contains("bundleId"));
        Assert.IsTrue(json.Contains("createdAt"));
    }

    [TestMethod]
    public void ToJson_WithDescription_IncludesDescription()
    {
        var bundle = new EventReplayBundle { Description = "Test Description" };
        var json = bundle.ToJson();

        Assert.IsTrue(json.Contains("description"));
        Assert.IsTrue(json.Contains("Test Description"));
    }

    [TestMethod]
    public void ToJson_WithEvents_IncludesEvents()
    {
        var bundle = new EventReplayBundle();
        bundle.Events.Add(new SerializedEvent
        {
            EventType = "TestEvent",
            PayloadJson = "{\"key\":\"value\"}"
        });

        var json = bundle.ToJson();

        Assert.IsTrue(json.Contains("events"));
        Assert.IsTrue(json.Contains("TestEvent"));
    }

    [TestMethod]
    public void ToJson_IndentedFalse_ReturnsCompactJson()
    {
        var bundle = new EventReplayBundle { Description = "Test" };
        var json = bundle.ToJson(indented: false);

        Assert.IsFalse(json.Contains("\n"));
    }

    [TestMethod]
    public void ToJson_IndentedTrue_ReturnsFormattedJson()
    {
        var bundle = new EventReplayBundle { Description = "Test" };
        var json = bundle.ToJson(indented: true);

        Assert.IsTrue(json.Contains("\n") || json.Contains(Environment.NewLine));
    }

    [TestMethod]
    public void ToJson_NullValues_AreOmitted()
    {
        var bundle = new EventReplayBundle();
        var json = bundle.ToJson();

        // Description is null and should be omitted with JsonIgnoreCondition.WhenWritingNull
        Assert.IsFalse(json.Contains("\"description\":null"));
    }

    #endregion

    #region EventReplayBundle Deserialization Tests

    [TestMethod]
    public void FromJson_ValidJson_ReturnsBundle()
    {
        var original = new EventReplayBundle
        {
            Description = "Test",
            AppVersion = "1.0.0"
        };
        var json = original.ToJson();

        var deserialized = EventReplayBundle.FromJson(json);

        Assert.IsNotNull(deserialized);
        Assert.AreEqual("Test", deserialized.Description);
        Assert.AreEqual("1.0.0", deserialized.AppVersion);
    }

    [TestMethod]
    public void FromJson_WithEvents_DeserializesEvents()
    {
        var original = new EventReplayBundle();
        original.Events.Add(new SerializedEvent
        {
            EventType = "TestEvent",
            SequenceNumber = 1
        });

        var json = original.ToJson();
        var deserialized = EventReplayBundle.FromJson(json);

        Assert.AreEqual(1, deserialized?.Events.Count);
        Assert.AreEqual("TestEvent", deserialized?.Events[0].EventType);
        Assert.AreEqual(1, deserialized?.Events[0].SequenceNumber);
    }

    [TestMethod]
    public void FromJson_NullString_ReturnsNull()
    {
        var result = EventReplayBundle.FromJson(null!);
        Assert.IsNull(result);
    }

    [TestMethod]
    public void FromJson_EmptyString_ReturnsNull()
    {
        var result = EventReplayBundle.FromJson("");
        Assert.IsNull(result);
    }

    [TestMethod]
    public void FromJson_RoundTrip_PreservesAllData()
    {
        var original = new EventReplayBundle
        {
            Description = "Full Test",
            AppVersion = "2.0.0",
            InitialState = new StateSnapshot
            {
                ActiveWorkspaceId = "ws-1",
                SelectedProfileId = "profile-1"
            },
            FinalState = new StateSnapshot
            {
                ActiveWorkspaceId = "ws-1",
                SelectedProfileId = "profile-2"
            },
            Metadata = new Dictionary<string, string>
            {
                ["user"] = "test-user"
            }
        };
        original.Events.Add(new SerializedEvent
        {
            EventType = "ProfileChanged",
            SourcePanelId = "panel-1",
            PayloadJson = "{\"newProfile\":\"profile-2\"}"
        });

        var json = original.ToJson();
        var restored = EventReplayBundle.FromJson(json);

        Assert.IsNotNull(restored);
        Assert.AreEqual(original.Description, restored.Description);
        Assert.AreEqual(original.AppVersion, restored.AppVersion);
        Assert.AreEqual(original.InitialState?.ActiveWorkspaceId, restored.InitialState?.ActiveWorkspaceId);
        Assert.AreEqual(original.FinalState?.SelectedProfileId, restored.FinalState?.SelectedProfileId);
        Assert.AreEqual(1, restored.Events.Count);
        Assert.AreEqual("ProfileChanged", restored.Events[0].EventType);
        Assert.AreEqual("test-user", restored.Metadata?["user"]);
    }

    #endregion

    #region SerializedEvent Tests

    [TestMethod]
    public void SerializedEvent_DefaultEventId_IsNotEmpty()
    {
        var evt = new SerializedEvent();
        Assert.IsFalse(string.IsNullOrEmpty(evt.EventId));
        Assert.IsTrue(Guid.TryParse(evt.EventId, out _));
    }

    [TestMethod]
    public void SerializedEvent_DefaultTimestamp_IsSetToUtcNow()
    {
        var before = DateTime.UtcNow;
        var evt = new SerializedEvent();
        var after = DateTime.UtcNow;

        Assert.IsTrue(evt.Timestamp >= before);
        Assert.IsTrue(evt.Timestamp <= after);
    }

    [TestMethod]
    public void SerializedEvent_DefaultEventType_IsEmptyString()
    {
        var evt = new SerializedEvent();
        Assert.AreEqual(string.Empty, evt.EventType);
    }

    [TestMethod]
    public void SerializedEvent_DefaultSequenceNumber_IsZero()
    {
        var evt = new SerializedEvent();
        Assert.AreEqual(0, evt.SequenceNumber);
    }

    [TestMethod]
    public void SerializedEvent_AllProperties_CanBeSet()
    {
        var evt = new SerializedEvent
        {
            EventId = "custom-id",
            EventType = "CustomEvent",
            Timestamp = new DateTime(2025, 1, 1, 0, 0, 0, DateTimeKind.Utc),
            SourcePanelId = "source",
            TargetPanelId = "target",
            PayloadJson = "{\"data\":123}",
            SequenceNumber = 42,
            Metadata = new Dictionary<string, string> { ["key"] = "value" }
        };

        Assert.AreEqual("custom-id", evt.EventId);
        Assert.AreEqual("CustomEvent", evt.EventType);
        Assert.AreEqual(2025, evt.Timestamp.Year);
        Assert.AreEqual("source", evt.SourcePanelId);
        Assert.AreEqual("target", evt.TargetPanelId);
        Assert.AreEqual("{\"data\":123}", evt.PayloadJson);
        Assert.AreEqual(42, evt.SequenceNumber);
        Assert.AreEqual("value", evt.Metadata?["key"]);
    }

    #endregion

    #region StateSnapshot Tests

    [TestMethod]
    public void StateSnapshot_DefaultTimestamp_IsSetToUtcNow()
    {
        var before = DateTime.UtcNow;
        var snapshot = new StateSnapshot();
        var after = DateTime.UtcNow;

        Assert.IsTrue(snapshot.Timestamp >= before);
        Assert.IsTrue(snapshot.Timestamp <= after);
    }

    [TestMethod]
    public void StateSnapshot_DefaultValues_AreNull()
    {
        var snapshot = new StateSnapshot();

        Assert.IsNull(snapshot.ActiveWorkspaceId);
        Assert.IsNull(snapshot.ActivePanelId);
        Assert.IsNull(snapshot.SelectedAssetId);
        Assert.IsNull(snapshot.SelectedProfileId);
        Assert.IsNull(snapshot.VisiblePanels);
        Assert.IsNull(snapshot.FullStateJson);
        Assert.IsNull(snapshot.CustomData);
    }

    [TestMethod]
    public void StateSnapshot_AllProperties_CanBeSet()
    {
        var snapshot = new StateSnapshot
        {
            Timestamp = new DateTime(2025, 6, 15, 12, 0, 0, DateTimeKind.Utc),
            ActiveWorkspaceId = "ws-1",
            ActivePanelId = "panel-1",
            SelectedAssetId = "asset-1",
            SelectedProfileId = "profile-1",
            VisiblePanels = new List<string> { "panel-1", "panel-2" },
            FullStateJson = "{\"state\":\"complete\"}",
            CustomData = new Dictionary<string, string> { ["custom"] = "data" }
        };

        Assert.AreEqual("ws-1", snapshot.ActiveWorkspaceId);
        Assert.AreEqual("panel-1", snapshot.ActivePanelId);
        Assert.AreEqual("asset-1", snapshot.SelectedAssetId);
        Assert.AreEqual("profile-1", snapshot.SelectedProfileId);
        Assert.AreEqual(2, snapshot.VisiblePanels?.Count);
        Assert.IsTrue(snapshot.FullStateJson?.Contains("complete"));
        Assert.AreEqual("data", snapshot.CustomData?["custom"]);
    }

    [TestMethod]
    public void StateSnapshot_SerializesCorrectly_InBundle()
    {
        var bundle = new EventReplayBundle
        {
            InitialState = new StateSnapshot
            {
                ActiveWorkspaceId = "initial-ws",
                VisiblePanels = new List<string> { "p1", "p2" }
            }
        };

        var json = bundle.ToJson();
        var restored = EventReplayBundle.FromJson(json);

        Assert.AreEqual("initial-ws", restored?.InitialState?.ActiveWorkspaceId);
        Assert.AreEqual(2, restored?.InitialState?.VisiblePanels?.Count);
    }

    #endregion
}
