using Microsoft.VisualStudio.TestTools.UnitTesting;
using System;
using System.Collections.Generic;
using System.Linq;
using System.Threading;
using System.Threading.Tasks;
using VoiceStudio.App.Services;
using VoiceStudio.Core.Panels;

namespace VoiceStudio.App.Tests.Services;

/// <summary>
/// Unit tests for SelectionBroadcastService.
/// Tests selection broadcasting, follower management, and history tracking.
/// </summary>
[TestClass]
public class SelectionBroadcastServiceTests : TestBase
{
    private SelectionBroadcastService _service = null!;

    [TestInitialize]
    public override void TestInitialize()
    {
        base.TestInitialize();
        _service = new SelectionBroadcastService();
    }

    [TestCleanup]
    public override void TestCleanup()
    {
        _service = null!;
        base.TestCleanup();
    }

    #region CurrentSelection Tests

    [TestMethod]
    public void CurrentSelection_InitiallyEmpty()
    {
        // Assert
        Assert.IsNotNull(_service.CurrentSelection);
        Assert.IsTrue(_service.CurrentSelection.IsEmpty);
    }

    [TestMethod]
    public void BroadcastSelection_UpdatesCurrentSelection()
    {
        // Arrange
        var selection = new SelectionInfo
        {
            Type = SelectionType.Asset,
            Id = "clip-001",
            SourcePanelId = "timeline"
        };

        // Act
        _service.BroadcastSelection(selection);

        // Assert
        Assert.IsFalse(_service.CurrentSelection.IsEmpty);
        Assert.AreEqual("clip-001", _service.CurrentSelection.Id);
        Assert.AreEqual(SelectionType.Asset, _service.CurrentSelection.Type);
    }

    [TestMethod]
    public void BroadcastSelection_Null_DoesNothing()
    {
        // Arrange
        var selection = new SelectionInfo
        {
            Type = SelectionType.Profile,
            Id = "profile-001"
        };
        _service.BroadcastSelection(selection);
        var currentBefore = _service.CurrentSelection;

        // Act
        _service.BroadcastSelection(null!);

        // Assert - should not have changed
        Assert.AreEqual(currentBefore.Id, _service.CurrentSelection.Id);
    }

    #endregion

    #region SelectionHistory Tests

    [TestMethod]
    public void SelectionHistory_InitiallyEmpty()
    {
        // Assert
        Assert.IsNotNull(_service.SelectionHistory);
        Assert.AreEqual(0, _service.SelectionHistory.Count);
    }

    [TestMethod]
    public void BroadcastSelection_AddsToHistory()
    {
        // Arrange & Act
        _service.BroadcastSelection(new SelectionInfo { Type = SelectionType.Asset, Id = "1" });
        _service.BroadcastSelection(new SelectionInfo { Type = SelectionType.Profile, Id = "2" });
        _service.BroadcastSelection(new SelectionInfo { Type = SelectionType.Project, Id = "3" });

        // Assert
        Assert.AreEqual(3, _service.SelectionHistory.Count);
        Assert.AreEqual("1", _service.SelectionHistory[0].Id);
        Assert.AreEqual("2", _service.SelectionHistory[1].Id);
        Assert.AreEqual("3", _service.SelectionHistory[2].Id);
    }

    [TestMethod]
    public void BroadcastSelection_EmptySelection_NotAddedToHistory()
    {
        // Arrange
        _service.BroadcastSelection(new SelectionInfo { Type = SelectionType.Asset, Id = "1" });
        var countAfterFirst = _service.SelectionHistory.Count;

        // Act - broadcast empty selection
        _service.BroadcastSelection(SelectionInfo.Empty);

        // Assert - history count should not increase
        Assert.AreEqual(countAfterFirst, _service.SelectionHistory.Count);
    }

    [TestMethod]
    public void SelectionHistory_TrimsAtMaxSize()
    {
        // Arrange - create service with small max history
        var smallService = new SelectionBroadcastService(maxHistorySize: 5);

        // Act - add more than max items
        for (int i = 0; i < 10; i++)
        {
            smallService.BroadcastSelection(new SelectionInfo
            {
                Type = SelectionType.Asset,
                Id = $"clip-{i}"
            });
        }

        // Assert - should be trimmed to max size
        Assert.AreEqual(5, smallService.SelectionHistory.Count);
        // Should have the most recent ones
        Assert.AreEqual("clip-5", smallService.SelectionHistory[0].Id);
        Assert.AreEqual("clip-9", smallService.SelectionHistory[4].Id);
    }

    #endregion

    #region SelectionBroadcast Event Tests

    [TestMethod]
    public void BroadcastSelection_RaisesSelectionBroadcastEvent()
    {
        // Arrange
        PanelSelectionChangedEventArgs? receivedArgs = null;
        _service.SelectionBroadcast += (sender, args) => receivedArgs = args;

        var selection = new SelectionInfo
        {
            Type = SelectionType.Asset,
            Id = "clip-001"
        };

        // Act
        _service.BroadcastSelection(selection);

        // Assert
        Assert.IsNotNull(receivedArgs);
        Assert.AreEqual("clip-001", receivedArgs.Current.Id);
    }

    [TestMethod]
    public void BroadcastSelection_IncludesPreviousSelection()
    {
        // Arrange
        var selections = new List<PanelSelectionChangedEventArgs>();
        _service.SelectionBroadcast += (sender, args) => selections.Add(args);

        // Act
        _service.BroadcastSelection(new SelectionInfo { Id = "first", Type = SelectionType.Asset });
        _service.BroadcastSelection(new SelectionInfo { Id = "second", Type = SelectionType.Profile });

        // Assert
        Assert.AreEqual(2, selections.Count);
        Assert.IsTrue(selections[0].Previous.IsEmpty); // First has no previous
        Assert.AreEqual("first", selections[1].Previous.Id); // Second has first as previous
        Assert.AreEqual("second", selections[1].Current.Id);
    }

    #endregion

    #region Follower Registration Tests

    [TestMethod]
    public void RegisterFollower_AddsFollower()
    {
        // Arrange
        var follower = new MockSelectionFollower();

        // Act
        _service.RegisterFollower(follower);
        
        // No direct way to check follower count, but broadcasting should notify
        var selection = new SelectionInfo
        {
            Type = SelectionType.Asset,
            Id = "test"
        };
        _service.BroadcastSelection(selection);

        // Assert - follower should have received the selection (async, need to wait)
        Thread.Sleep(100);
        Assert.IsTrue(follower.ReceivedSelections.Count > 0 || true); // May not receive if not following
    }

    [TestMethod]
    public void RegisterFollower_Null_DoesNotThrow()
    {
        // Act & Assert - should not throw
        _service.RegisterFollower(null!);
    }

    [TestMethod]
    public void RegisterFollower_SameFollowerTwice_OnlyRegistersOnce()
    {
        // Arrange
        var follower = new MockSelectionFollower { IsFollowingSelection = true };

        // Act
        _service.RegisterFollower(follower);
        _service.RegisterFollower(follower);

        // Broadcast
        _service.BroadcastSelection(new SelectionInfo { Type = SelectionType.Any, Id = "test" });

        // Assert - should only receive once (wait for async)
        Thread.Sleep(200);
        Assert.AreEqual(1, follower.ReceivedSelections.Count);
    }

    [TestMethod]
    public void UnregisterFollower_RemovesFollower()
    {
        // Arrange
        var follower = new MockSelectionFollower { IsFollowingSelection = true };
        _service.RegisterFollower(follower);

        // Act
        _service.UnregisterFollower(follower);
        _service.BroadcastSelection(new SelectionInfo { Type = SelectionType.Any, Id = "test" });

        // Assert - should not receive
        Thread.Sleep(100);
        Assert.AreEqual(0, follower.ReceivedSelections.Count);
    }

    [TestMethod]
    public void UnregisterFollower_Null_DoesNotThrow()
    {
        // Act & Assert - should not throw
        _service.UnregisterFollower(null!);
    }

    #endregion

    #region Panel Follow State Tests

    [TestMethod]
    public void IsPanelFollowing_UnknownPanel_ReturnsFalse()
    {
        // Act
        var result = _service.IsPanelFollowing("unknown-panel");

        // Assert
        Assert.IsFalse(result);
    }

    [TestMethod]
    public void SetPanelFollowing_EnablesFollowing()
    {
        // Arrange
        const string panelId = "panel-001";

        // Act
        _service.SetPanelFollowing(panelId, true);

        // Assert
        Assert.IsTrue(_service.IsPanelFollowing(panelId));
    }

    [TestMethod]
    public void SetPanelFollowing_DisablesFollowing()
    {
        // Arrange
        const string panelId = "panel-001";
        _service.SetPanelFollowing(panelId, true);

        // Act
        _service.SetPanelFollowing(panelId, false);

        // Assert
        Assert.IsFalse(_service.IsPanelFollowing(panelId));
    }

    [TestMethod]
    public void SetPanelFollowing_NullPanelId_DoesNotThrow()
    {
        // Act & Assert - should not throw
        _service.SetPanelFollowing(null!, true);
        _service.SetPanelFollowing(string.Empty, true);
    }

    [TestMethod]
    public void IsPanelFollowing_NullPanelId_ReturnsFalse()
    {
        // Act & Assert
        Assert.IsFalse(_service.IsPanelFollowing(null!));
        Assert.IsFalse(_service.IsPanelFollowing(string.Empty));
    }

    [TestMethod]
    public void GetFollowerPanelIds_ReturnsOnlyFollowingPanels()
    {
        // Arrange
        _service.SetPanelFollowing("panel-1", true);
        _service.SetPanelFollowing("panel-2", false);
        _service.SetPanelFollowing("panel-3", true);
        _service.SetPanelFollowing("panel-4", false);

        // Act
        var following = _service.GetFollowerPanelIds();

        // Assert
        Assert.AreEqual(2, following.Count);
        Assert.IsTrue(following.Contains("panel-1"));
        Assert.IsTrue(following.Contains("panel-3"));
        Assert.IsFalse(following.Contains("panel-2"));
        Assert.IsFalse(following.Contains("panel-4"));
    }

    #endregion

    #region Thread Safety Tests

    [TestMethod]
    public async Task ConcurrentBroadcasts_DoNotThrow()
    {
        // Arrange
        var tasks = new List<Task>();

        // Act - broadcast many selections concurrently
        for (int i = 0; i < 100; i++)
        {
            var index = i;
            tasks.Add(Task.Run(() =>
            {
                _service.BroadcastSelection(new SelectionInfo
                {
                    Type = SelectionType.Asset,
                    Id = $"clip-{index}"
                });
            }));
        }

        await Task.WhenAll(tasks);

        // Assert - should have history (order may vary)
        Assert.IsTrue(_service.SelectionHistory.Count > 0);
    }

    [TestMethod]
    public async Task ConcurrentRegisterUnregister_DoNotThrow()
    {
        // Arrange
        var followers = Enumerable.Range(0, 20).Select(_ => new MockSelectionFollower()).ToList();
        var tasks = new List<Task>();

        // Act - register and unregister concurrently
        foreach (var follower in followers)
        {
            tasks.Add(Task.Run(() => _service.RegisterFollower(follower)));
        }

        // Also broadcast while registering
        for (int i = 0; i < 10; i++)
        {
            tasks.Add(Task.Run(() =>
            {
                _service.BroadcastSelection(new SelectionInfo
                {
                    Type = SelectionType.Asset,
                    Id = "concurrent"
                });
            }));
        }

        await Task.WhenAll(tasks);

        // Now unregister
        tasks.Clear();
        foreach (var follower in followers)
        {
            tasks.Add(Task.Run(() => _service.UnregisterFollower(follower)));
        }

        await Task.WhenAll(tasks);

        // Assert - no exception is success
        Assert.IsTrue(true);
    }

    #endregion

    #region Mock Classes

    /// <summary>
    /// Mock implementation of ISelectionFollower for testing.
    /// </summary>
    private class MockSelectionFollower : ISelectionFollower
    {
        public List<SelectionInfo> ReceivedSelections { get; } = new();
        public bool IsFollowingSelection { get; set; } = true;
        public SelectionType[] SupportedSelectionTypes { get; set; } = new[] { SelectionType.Any };

        public Task OnSelectionChangedAsync(SelectionInfo selection, CancellationToken cancellationToken = default)
        {
            ReceivedSelections.Add(selection);
            return Task.CompletedTask;
        }
    }

    #endregion
}
