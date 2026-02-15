using Microsoft.VisualStudio.TestTools.UnitTesting;
using System;
using System.Collections.Generic;
using System.Linq;
using System.Threading.Tasks;
using VoiceStudio.App.Services;
using VoiceStudio.Core.Panels;

namespace VoiceStudio.App.Tests.Services;

/// <summary>
/// Unit tests for SynchronizedScrollService.
/// Tests scroll synchronization, panel registration, and group management.
/// </summary>
[TestClass]
public class SynchronizedScrollServiceTests : TestBase
{
    private SynchronizedScrollService _service = null!;

    [TestInitialize]
    public override void TestInitialize()
    {
        base.TestInitialize();
        _service = new SynchronizedScrollService();
    }

    [TestCleanup]
    public override void TestCleanup()
    {
        _service = null!;
        base.TestCleanup();
    }

    #region IsEnabled Tests

    [TestMethod]
    public void IsEnabled_DefaultsToTrue()
    {
        // Assert
        Assert.IsTrue(_service.IsEnabled);
    }

    [TestMethod]
    public void IsEnabled_CanBeDisabled()
    {
        // Act
        _service.IsEnabled = false;

        // Assert
        Assert.IsFalse(_service.IsEnabled);
    }

    [TestMethod]
    public void IsEnabled_CanBeReEnabled()
    {
        // Arrange
        _service.IsEnabled = false;

        // Act
        _service.IsEnabled = true;

        // Assert
        Assert.IsTrue(_service.IsEnabled);
    }

    #endregion

    #region Registration Tests

    [TestMethod]
    public void Register_Null_DoesNotThrow()
    {
        // Act & Assert - should not throw
        _service.Register(null!);
    }

    [TestMethod]
    public void Register_AddsPanel()
    {
        // Arrange
        var panel = new MockScrollPanel("panel1", "timeline");

        // Act
        _service.Register(panel);

        // Assert
        var members = _service.GetGroupMembers("timeline");
        Assert.AreEqual(1, members.Count);
        Assert.IsTrue(members.Contains("panel1"));
    }

    [TestMethod]
    public void Register_SamePanelTwice_OnlyRegistersOnce()
    {
        // Arrange
        var panel = new MockScrollPanel("panel1", "timeline");

        // Act
        _service.Register(panel);
        _service.Register(panel);

        // Assert
        var members = _service.GetGroupMembers("timeline");
        Assert.AreEqual(1, members.Count);
    }

    [TestMethod]
    public void Register_MultiplePanels_AllRegistered()
    {
        // Arrange
        var panel1 = new MockScrollPanel("panel1", "timeline");
        var panel2 = new MockScrollPanel("panel2", "timeline");
        var panel3 = new MockScrollPanel("panel3", "waveform");

        // Act
        _service.Register(panel1);
        _service.Register(panel2);
        _service.Register(panel3);

        // Assert
        Assert.AreEqual(2, _service.GetGroupMembers("timeline").Count);
        Assert.AreEqual(1, _service.GetGroupMembers("waveform").Count);
    }

    [TestMethod]
    public void Unregister_Null_DoesNotThrow()
    {
        // Act & Assert - should not throw
        _service.Unregister(null!);
    }

    [TestMethod]
    public void Unregister_RemovesPanel()
    {
        // Arrange
        var panel = new MockScrollPanel("panel1", "timeline");
        _service.Register(panel);
        Assert.AreEqual(1, _service.GetGroupMembers("timeline").Count);

        // Act
        _service.Unregister(panel);

        // Assert
        Assert.AreEqual(0, _service.GetGroupMembers("timeline").Count);
    }

    [TestMethod]
    public void Unregister_NonRegisteredPanel_DoesNotThrow()
    {
        // Arrange
        var panel = new MockScrollPanel("panel1", "timeline");

        // Act & Assert - should not throw
        _service.Unregister(panel);
    }

    #endregion

    #region Group Management Tests

    [TestMethod]
    public void GetGroups_InitiallyEmpty()
    {
        // Assert
        Assert.AreEqual(0, _service.GetGroups().Count);
    }

    [TestMethod]
    public void GetGroups_ReturnsDistinctGroups()
    {
        // Arrange
        _service.Register(new MockScrollPanel("p1", "timeline"));
        _service.Register(new MockScrollPanel("p2", "timeline"));
        _service.Register(new MockScrollPanel("p3", "waveform"));
        _service.Register(new MockScrollPanel("p4", "effects"));

        // Act
        var groups = _service.GetGroups();

        // Assert
        Assert.AreEqual(3, groups.Count);
        Assert.IsTrue(groups.Contains("timeline"));
        Assert.IsTrue(groups.Contains("waveform"));
        Assert.IsTrue(groups.Contains("effects"));
    }

    [TestMethod]
    public void GetGroupMembers_UnknownGroup_ReturnsEmpty()
    {
        // Act
        var members = _service.GetGroupMembers("unknown");

        // Assert
        Assert.AreEqual(0, members.Count);
    }

    [TestMethod]
    public void GetGroupMembers_ReturnsOnlyGroupMembers()
    {
        // Arrange
        _service.Register(new MockScrollPanel("p1", "timeline"));
        _service.Register(new MockScrollPanel("p2", "timeline"));
        _service.Register(new MockScrollPanel("p3", "waveform"));

        // Act
        var timelineMembers = _service.GetGroupMembers("timeline");
        var waveformMembers = _service.GetGroupMembers("waveform");

        // Assert
        Assert.AreEqual(2, timelineMembers.Count);
        Assert.AreEqual(1, waveformMembers.Count);
        Assert.IsTrue(timelineMembers.Contains("p1"));
        Assert.IsTrue(timelineMembers.Contains("p2"));
        Assert.IsTrue(waveformMembers.Contains("p3"));
    }

    #endregion

    #region Scroll Broadcast Tests

    [TestMethod]
    public void BroadcastScroll_Null_DoesNotThrow()
    {
        // Act & Assert - should not throw
        _service.BroadcastScroll(null!);
    }

    [TestMethod]
    public void BroadcastScroll_WhenDisabled_DoesNotBroadcast()
    {
        // Arrange
        var sourcePanel = new MockScrollPanel("source", "timeline");
        var targetPanel = new MockScrollPanel("target", "timeline");
        _service.Register(sourcePanel);
        _service.Register(targetPanel);
        _service.IsEnabled = false;

        // Act
        _service.BroadcastScroll(new ScrollPositionChangedEventArgs("source", "timeline", 0.5));

        // Assert - target should not have received scroll
        Assert.AreEqual(0, targetPanel.ReceivedScrolls.Count);
    }

    [TestMethod]
    public void BroadcastScroll_NotifiePanelsInSameGroup()
    {
        // Arrange
        var sourcePanel = new MockScrollPanel("source", "timeline");
        var targetPanel1 = new MockScrollPanel("target1", "timeline");
        var targetPanel2 = new MockScrollPanel("target2", "timeline");
        var otherGroupPanel = new MockScrollPanel("other", "waveform");

        _service.Register(sourcePanel);
        _service.Register(targetPanel1);
        _service.Register(targetPanel2);
        _service.Register(otherGroupPanel);

        // Act
        _service.BroadcastScroll(new ScrollPositionChangedEventArgs("source", "timeline", 0.75));

        // Assert
        Assert.AreEqual(1, targetPanel1.ReceivedScrolls.Count);
        Assert.AreEqual(1, targetPanel2.ReceivedScrolls.Count);
        Assert.AreEqual(0, otherGroupPanel.ReceivedScrolls.Count);
        Assert.AreEqual(0.75, targetPanel1.ReceivedScrolls[0].position, 0.001);
    }

    [TestMethod]
    public void BroadcastScroll_DoesNotNotifySourcePanel()
    {
        // Arrange
        var sourcePanel = new MockScrollPanel("source", "timeline");
        var targetPanel = new MockScrollPanel("target", "timeline");
        _service.Register(sourcePanel);
        _service.Register(targetPanel);

        // Act
        _service.BroadcastScroll(new ScrollPositionChangedEventArgs("source", "timeline", 0.5));

        // Assert - source should NOT receive its own scroll
        Assert.AreEqual(0, sourcePanel.ReceivedScrolls.Count);
        Assert.AreEqual(1, targetPanel.ReceivedScrolls.Count);
    }

    [TestMethod]
    public void BroadcastScroll_WithTimePosition_SetsTimePosition()
    {
        // Arrange
        var sourcePanel = new MockScrollPanel("source", "timeline");
        var targetPanel = new MockScrollPanel("target", "timeline");
        _service.Register(sourcePanel);
        _service.Register(targetPanel);

        // Act
        _service.BroadcastScroll(new ScrollPositionChangedEventArgs("source", "timeline", 0.0, TimeSpan.FromSeconds(30)));

        // Assert
        Assert.AreEqual(1, targetPanel.ReceivedTimePositions.Count);
        Assert.AreEqual(TimeSpan.FromSeconds(30), targetPanel.ReceivedTimePositions[0].time);
    }

    [TestMethod]
    public void BroadcastScroll_DisabledPanel_NotNotified()
    {
        // Arrange
        var sourcePanel = new MockScrollPanel("source", "timeline");
        var enabledPanel = new MockScrollPanel("enabled", "timeline") { IsSynchronizedScrollEnabled = true };
        var disabledPanel = new MockScrollPanel("disabled", "timeline") { IsSynchronizedScrollEnabled = false };

        _service.Register(sourcePanel);
        _service.Register(enabledPanel);
        _service.Register(disabledPanel);

        // Act
        _service.BroadcastScroll(new ScrollPositionChangedEventArgs("source", "timeline", 0.5));

        // Assert
        Assert.AreEqual(1, enabledPanel.ReceivedScrolls.Count);
        Assert.AreEqual(0, disabledPanel.ReceivedScrolls.Count);
    }

    [TestMethod]
    public void BroadcastScroll_RaisesScrollBroadcastEvent()
    {
        // Arrange
        ScrollPositionChangedEventArgs? receivedArgs = null;
        _service.ScrollBroadcast += (sender, args) => receivedArgs = args;

        _service.Register(new MockScrollPanel("panel1", "timeline"));

        // Act
        _service.BroadcastScroll(new ScrollPositionChangedEventArgs("external", "timeline", 0.25));

        // Assert
        Assert.IsNotNull(receivedArgs);
        Assert.AreEqual("timeline", receivedArgs.ScrollGroup);
        Assert.AreEqual(0.25, receivedArgs.NormalizedPosition, 0.001);
    }

    #endregion

    #region Thread Safety Tests

    [TestMethod]
    public async Task ConcurrentRegistration_DoesNotThrow()
    {
        // Arrange
        var tasks = new List<Task>();
        var panels = Enumerable.Range(0, 50).Select(i =>
            new MockScrollPanel($"panel{i}", "timeline")).ToList();

        // Act - register concurrently
        foreach (var panel in panels)
        {
            tasks.Add(Task.Run(() => _service.Register(panel)));
        }

        await Task.WhenAll(tasks);

        // Assert - all should be registered
        var members = _service.GetGroupMembers("timeline");
        Assert.AreEqual(50, members.Count);
    }

    [TestMethod]
    public async Task ConcurrentBroadcast_DoesNotThrow()
    {
        // Arrange
        var panels = Enumerable.Range(0, 10).Select(i =>
            new MockScrollPanel($"panel{i}", "timeline")).ToList();

        foreach (var panel in panels)
        {
            _service.Register(panel);
        }

        var tasks = new List<Task>();

        // Act - broadcast concurrently
        for (int i = 0; i < 100; i++)
        {
            var pos = i / 100.0;
            tasks.Add(Task.Run(() =>
            {
                _service.BroadcastScroll(new ScrollPositionChangedEventArgs("external", "timeline", pos));
            }));
        }

        await Task.WhenAll(tasks);

        // Assert - no exception is success
        Assert.IsTrue(true);
    }

    #endregion

    #region Mock Classes

    /// <summary>
    /// Mock implementation of ISynchronizedScrolling for testing.
    /// </summary>
    private class MockScrollPanel : ISynchronizedScrolling
    {
        public string ScrollPanelId { get; }
        public string ScrollGroup { get; }
        public bool IsSynchronizedScrollEnabled { get; set; } = true;
        public double NormalizedScrollPosition { get; private set; }
        public TimeSpan? TimePosition { get; private set; }

        public List<(double position, string? source)> ReceivedScrolls { get; } = new();
        public List<(TimeSpan time, string? source)> ReceivedTimePositions { get; } = new();

        public event EventHandler<ScrollPositionChangedEventArgs>? ScrollPositionChanged;

        public MockScrollPanel(string panelId, string group)
        {
            ScrollPanelId = panelId;
            ScrollGroup = group;
        }

        public void SetScrollPosition(double normalizedPosition, string? sourcePanelId = null)
        {
            NormalizedScrollPosition = normalizedPosition;
            ReceivedScrolls.Add((normalizedPosition, sourcePanelId));
        }

        public void SetTimePosition(TimeSpan position, string? sourcePanelId = null)
        {
            TimePosition = position;
            ReceivedTimePositions.Add((position, sourcePanelId));
        }

        public void RaiseScrollChanged(double position)
        {
            ScrollPositionChanged?.Invoke(this, new ScrollPositionChangedEventArgs(
                ScrollPanelId,
                ScrollGroup,
                position));
        }
    }

    #endregion
}
