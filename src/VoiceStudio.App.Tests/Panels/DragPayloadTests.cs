using Microsoft.VisualStudio.TestTools.UnitTesting;
using System;
using System.Collections.Generic;
using VoiceStudio.Core.Panels;

namespace VoiceStudio.App.Tests.Panels;

[TestClass]
public class DragPayloadTests
{
    #region DragItem Tests

    [TestMethod]
    public void DragItem_RequiredProperties_AreSet()
    {
        var item = new DragItem
        {
            Id = "item-1",
            DisplayName = "Test Item"
        };

        Assert.AreEqual("item-1", item.Id);
        Assert.AreEqual("Test Item", item.DisplayName);
    }

    [TestMethod]
    public void DragItem_Metadata_IsNull_ByDefault()
    {
        var item = new DragItem
        {
            Id = "item-1",
            DisplayName = "Test Item"
        };

        Assert.IsNull(item.Metadata);
    }

    [TestMethod]
    public void DragItem_Metadata_CanBeSet()
    {
        var item = new DragItem
        {
            Id = "item-1",
            DisplayName = "Test Item",
            Metadata = new Dictionary<string, object>
            {
                ["Key1"] = "Value1",
                ["Key2"] = 42
            }
        };

        Assert.IsNotNull(item.Metadata);
        Assert.AreEqual("Value1", item.Metadata["Key1"]);
        Assert.AreEqual(42, item.Metadata["Key2"]);
    }

    #endregion

    #region DragPayload Constructor Tests

    [TestMethod]
    public void DragPayload_RequiredProperties_AreSet()
    {
        var items = new List<DragItem>
        {
            new DragItem { Id = "1", DisplayName = "Item 1" }
        };

        var payload = new DragPayload
        {
            PayloadType = DragPayloadType.Asset,
            SourcePanelId = "library-panel",
            Items = items
        };

        Assert.AreEqual(DragPayloadType.Asset, payload.PayloadType);
        Assert.AreEqual("library-panel", payload.SourcePanelId);
        Assert.AreEqual(1, payload.Items.Count);
    }

    [TestMethod]
    public void DragPayload_StartedAt_IsSetAutomatically()
    {
        var before = DateTimeOffset.UtcNow;
        var payload = new DragPayload
        {
            PayloadType = DragPayloadType.Profile,
            SourcePanelId = "panel",
            Items = new List<DragItem>()
        };
        var after = DateTimeOffset.UtcNow;

        Assert.IsTrue(payload.StartedAt >= before);
        Assert.IsTrue(payload.StartedAt <= after);
    }

    [TestMethod]
    public void DragPayload_IsCopy_DefaultsToTrue()
    {
        var payload = new DragPayload
        {
            PayloadType = DragPayloadType.TextBlock,
            SourcePanelId = "panel",
            Items = new List<DragItem>()
        };

        Assert.IsTrue(payload.IsCopy);
    }

    [TestMethod]
    public void DragPayload_IsCopy_CanBeFalse()
    {
        var payload = new DragPayload
        {
            PayloadType = DragPayloadType.TimelineClip,
            SourcePanelId = "panel",
            Items = new List<DragItem>(),
            IsCopy = false
        };

        Assert.IsFalse(payload.IsCopy);
    }

    [TestMethod]
    public void DragPayload_FilePaths_IsNull_ByDefault()
    {
        var payload = new DragPayload
        {
            PayloadType = DragPayloadType.Asset,
            SourcePanelId = "panel",
            Items = new List<DragItem>()
        };

        Assert.IsNull(payload.FilePaths);
    }

    #endregion

    #region FromAsset Factory Tests

    [TestMethod]
    public void FromAsset_CreatesAssetPayload()
    {
        var payload = DragPayload.FromAsset("library", "asset-1", "MyAudio.wav");

        Assert.AreEqual(DragPayloadType.Asset, payload.PayloadType);
    }

    [TestMethod]
    public void FromAsset_SetsSourcePanelId()
    {
        var payload = DragPayload.FromAsset("library-panel", "asset-1", "MyAudio.wav");

        Assert.AreEqual("library-panel", payload.SourcePanelId);
    }

    [TestMethod]
    public void FromAsset_CreatesSingleItem()
    {
        var payload = DragPayload.FromAsset("library", "asset-123", "Sound.mp3");

        Assert.AreEqual(1, payload.Items.Count);
        Assert.AreEqual("asset-123", payload.Items[0].Id);
        Assert.AreEqual("Sound.mp3", payload.Items[0].DisplayName);
    }

    [TestMethod]
    public void FromAsset_WithAssetType_SetsMetadata()
    {
        var payload = DragPayload.FromAsset("library", "asset-1", "Music.wav", "audio");

        Assert.IsNotNull(payload.Items[0].Metadata);
        Assert.AreEqual("audio", payload.Items[0].Metadata!["AssetType"]);
    }

    [TestMethod]
    public void FromAsset_WithoutAssetType_NoMetadata()
    {
        var payload = DragPayload.FromAsset("library", "asset-1", "Music.wav");

        Assert.IsNull(payload.Items[0].Metadata);
    }

    #endregion

    #region FromProfile Factory Tests

    [TestMethod]
    public void FromProfile_CreatesProfilePayload()
    {
        var payload = DragPayload.FromProfile("profiles", "profile-1", "English Voice");

        Assert.AreEqual(DragPayloadType.Profile, payload.PayloadType);
    }

    [TestMethod]
    public void FromProfile_SetsSourcePanelId()
    {
        var payload = DragPayload.FromProfile("profile-panel", "profile-1", "Voice");

        Assert.AreEqual("profile-panel", payload.SourcePanelId);
    }

    [TestMethod]
    public void FromProfile_CreatesSingleItem()
    {
        var payload = DragPayload.FromProfile("profiles", "prof-42", "French TTS");

        Assert.AreEqual(1, payload.Items.Count);
        Assert.AreEqual("prof-42", payload.Items[0].Id);
        Assert.AreEqual("French TTS", payload.Items[0].DisplayName);
    }

    [TestMethod]
    public void FromProfile_WithLanguage_SetsMetadata()
    {
        var payload = DragPayload.FromProfile("profiles", "profile-1", "German Voice", "de-DE");

        Assert.IsNotNull(payload.Items[0].Metadata);
        Assert.AreEqual("de-DE", payload.Items[0].Metadata!["Language"]);
    }

    [TestMethod]
    public void FromProfile_WithoutLanguage_NoMetadata()
    {
        var payload = DragPayload.FromProfile("profiles", "profile-1", "Voice");

        Assert.IsNull(payload.Items[0].Metadata);
    }

    #endregion

    #region FromExternalFiles Factory Tests

    [TestMethod]
    public void FromExternalFiles_CreatesExternalFilePayload()
    {
        var paths = new[] { @"C:\audio\file.wav" };
        var payload = DragPayload.FromExternalFiles(paths);

        Assert.AreEqual(DragPayloadType.ExternalFile, payload.PayloadType);
    }

    [TestMethod]
    public void FromExternalFiles_SetsSourcePanelIdToExternal()
    {
        var paths = new[] { @"C:\audio\file.wav" };
        var payload = DragPayload.FromExternalFiles(paths);

        Assert.AreEqual("external", payload.SourcePanelId);
    }

    [TestMethod]
    public void FromExternalFiles_CreatesItemsForEachFile()
    {
        var paths = new[]
        {
            @"C:\audio\file1.wav",
            @"D:\music\song.mp3",
            @"E:\sounds\effect.ogg"
        };
        var payload = DragPayload.FromExternalFiles(paths);

        Assert.AreEqual(3, payload.Items.Count);
    }

    [TestMethod]
    public void FromExternalFiles_UsesFilePathAsItemId()
    {
        var path = @"C:\folder\audio.wav";
        var payload = DragPayload.FromExternalFiles(new[] { path });

        Assert.AreEqual(path, payload.Items[0].Id);
    }

    [TestMethod]
    public void FromExternalFiles_ExtractsFileNameForDisplay()
    {
        var path = @"C:\folder\subdir\MyAudioFile.wav";
        var payload = DragPayload.FromExternalFiles(new[] { path });

        Assert.AreEqual("MyAudioFile.wav", payload.Items[0].DisplayName);
    }

    [TestMethod]
    public void FromExternalFiles_SetsFilePaths()
    {
        var paths = new[] { @"C:\a.wav", @"D:\b.wav" };
        var payload = DragPayload.FromExternalFiles(paths);

        Assert.IsNotNull(payload.FilePaths);
        Assert.AreEqual(2, payload.FilePaths.Count);
        Assert.AreEqual(@"C:\a.wav", payload.FilePaths[0]);
        Assert.AreEqual(@"D:\b.wav", payload.FilePaths[1]);
    }

    [TestMethod]
    public void FromExternalFiles_EmptyList_CreatesEmptyPayload()
    {
        var payload = DragPayload.FromExternalFiles(Array.Empty<string>());

        Assert.AreEqual(0, payload.Items.Count);
        Assert.IsNotNull(payload.FilePaths);
        Assert.AreEqual(0, payload.FilePaths.Count);
    }

    #endregion

    #region DragPayloadType Enum Tests

    [TestMethod]
    public void DragPayloadType_HasExpectedValues()
    {
        Assert.AreEqual(0, (int)DragPayloadType.Asset);
        Assert.AreEqual(1, (int)DragPayloadType.Profile);
        Assert.AreEqual(2, (int)DragPayloadType.TimelineClip);
        Assert.AreEqual(3, (int)DragPayloadType.TextBlock);
        Assert.AreEqual(4, (int)DragPayloadType.ReferenceAudio);
        Assert.AreEqual(5, (int)DragPayloadType.MultiSelect);
        Assert.AreEqual(6, (int)DragPayloadType.ExternalFile);
    }

    #endregion
}

[TestClass]
public class DropResultTests
{
    [TestMethod]
    public void DropResult_RequiredProperties_AreSet()
    {
        var result = new DropResult
        {
            Success = true,
            TargetPanelId = "timeline-panel"
        };

        Assert.IsTrue(result.Success);
        Assert.AreEqual("timeline-panel", result.TargetPanelId);
    }

    [TestMethod]
    public void DropResult_Action_IsNull_ByDefault()
    {
        var result = new DropResult
        {
            Success = true,
            TargetPanelId = "panel"
        };

        Assert.IsNull(result.Action);
    }

    [TestMethod]
    public void DropResult_Action_CanBeSet()
    {
        var result = new DropResult
        {
            Success = true,
            TargetPanelId = "panel",
            Action = "imported"
        };

        Assert.AreEqual("imported", result.Action);
    }

    [TestMethod]
    public void DropResult_ErrorMessage_IsNull_ByDefault()
    {
        var result = new DropResult
        {
            Success = false,
            TargetPanelId = "panel"
        };

        Assert.IsNull(result.ErrorMessage);
    }

    [TestMethod]
    public void DropResult_ErrorMessage_CanBeSet()
    {
        var result = new DropResult
        {
            Success = false,
            TargetPanelId = "panel",
            ErrorMessage = "Unsupported file type"
        };

        Assert.AreEqual("Unsupported file type", result.ErrorMessage);
    }

    [TestMethod]
    public void DropResult_AffectedItemIds_IsNull_ByDefault()
    {
        var result = new DropResult
        {
            Success = true,
            TargetPanelId = "panel"
        };

        Assert.IsNull(result.AffectedItemIds);
    }

    [TestMethod]
    public void DropResult_AffectedItemIds_CanBeSet()
    {
        var result = new DropResult
        {
            Success = true,
            TargetPanelId = "timeline",
            AffectedItemIds = new List<string> { "clip-1", "clip-2" }
        };

        Assert.IsNotNull(result.AffectedItemIds);
        Assert.AreEqual(2, result.AffectedItemIds.Count);
    }

    [TestMethod]
    public void DropResult_SuccessfulImport_TypicalUsage()
    {
        var result = new DropResult
        {
            Success = true,
            TargetPanelId = "library-panel",
            Action = "imported",
            AffectedItemIds = new[] { "asset-new-1", "asset-new-2" }
        };

        Assert.IsTrue(result.Success);
        Assert.AreEqual("imported", result.Action);
        Assert.IsNull(result.ErrorMessage);
        Assert.AreEqual(2, result.AffectedItemIds!.Count);
    }

    [TestMethod]
    public void DropResult_FailedDrop_TypicalUsage()
    {
        var result = new DropResult
        {
            Success = false,
            TargetPanelId = "timeline-panel",
            ErrorMessage = "Cannot drop profile onto timeline"
        };

        Assert.IsFalse(result.Success);
        Assert.AreEqual("Cannot drop profile onto timeline", result.ErrorMessage);
        Assert.IsNull(result.AffectedItemIds);
    }
}
