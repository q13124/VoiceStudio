using Microsoft.VisualStudio.TestTools.UnitTesting;
using System;
using System.Collections.Generic;
using System.Linq;
using VoiceStudio.App.Services;
using VoiceStudio.Core.Models;

namespace VoiceStudio.App.Tests.Services;

[TestClass]
public class WorkspaceHistoryServiceTests : TestBase
{
    private WorkspaceHistoryService _service = null!;

    [TestInitialize]
    public override void TestInitialize()
    {
        base.TestInitialize();
        _service = new WorkspaceHistoryService();
    }

    [TestCleanup]
    public override void TestCleanup()
    {
        _service = null!;
        base.TestCleanup();
    }

    #region Initial State Tests

    [TestMethod]
    public void InitialState_CanUndo_IsFalse()
    {
        Assert.IsFalse(_service.CanUndo);
    }

    [TestMethod]
    public void InitialState_CanRedo_IsFalse()
    {
        Assert.IsFalse(_service.CanRedo);
    }

    [TestMethod]
    public void InitialState_UndoCount_IsZero()
    {
        Assert.AreEqual(0, _service.UndoCount);
    }

    [TestMethod]
    public void InitialState_RedoCount_IsZero()
    {
        Assert.AreEqual(0, _service.RedoCount);
    }

    #endregion

    #region RecordChange Tests

    [TestMethod]
    public void RecordChange_FirstChange_NoUndoAvailable()
    {
        // Arrange
        var layout = CreateTestLayout("Layout1");

        // Act
        _service.RecordChange(layout, "First change");

        // Assert - first change becomes current state, undo stack is empty
        Assert.IsFalse(_service.CanUndo);
        Assert.AreEqual(0, _service.UndoCount);
    }

    [TestMethod]
    public void RecordChange_SecondChange_UndoBecomesAvailable()
    {
        // Arrange
        var layout1 = CreateTestLayout("Layout1");
        var layout2 = CreateTestLayout("Layout2");

        // Act
        _service.RecordChange(layout1, "First change");
        _service.RecordChange(layout2, "Second change");

        // Assert
        Assert.IsTrue(_service.CanUndo);
        Assert.AreEqual(1, _service.UndoCount);
    }

    [TestMethod]
    public void RecordChange_ClearsRedoStack()
    {
        // Arrange
        var layout1 = CreateTestLayout("Layout1");
        var layout2 = CreateTestLayout("Layout2");
        var layout3 = CreateTestLayout("Layout3");

        _service.RecordChange(layout1, "Change 1");
        _service.RecordChange(layout2, "Change 2");
        _service.Undo(); // Should have redo available

        Assert.IsTrue(_service.CanRedo);

        // Act - new change should clear redo
        _service.RecordChange(layout3, "Change 3");

        // Assert
        Assert.IsFalse(_service.CanRedo);
        Assert.AreEqual(0, _service.RedoCount);
    }

    [TestMethod]
    public void RecordChange_RaisesHistoryChangedEvent()
    {
        // Arrange
        var eventRaised = false;
        _service.HistoryChanged += (s, e) => eventRaised = true;
        var layout = CreateTestLayout("Layout1");

        // Act
        _service.RecordChange(layout, "Test change");

        // Assert
        Assert.IsTrue(eventRaised);
    }

    [TestMethod]
    public void RecordChange_MultipleChanges_IncreasesUndoCount()
    {
        // Act
        for (var i = 0; i < 5; i++)
        {
            _service.RecordChange(CreateTestLayout($"Layout{i}"), $"Change {i}");
        }

        // Assert - first becomes current, 4 are in undo stack
        Assert.AreEqual(4, _service.UndoCount);
    }

    #endregion

    #region Undo Tests

    [TestMethod]
    public void Undo_WhenEmpty_ReturnsNull()
    {
        // Act
        var result = _service.Undo();

        // Assert
        Assert.IsNull(result);
    }

    [TestMethod]
    public void Undo_ReturnsLayout()
    {
        // Arrange
        var layout1 = CreateTestLayout("Layout1");
        var layout2 = CreateTestLayout("Layout2");

        _service.RecordChange(layout1, "Change 1");
        _service.RecordChange(layout2, "Change 2");

        // Act
        var result = _service.Undo();

        // Assert
        Assert.IsNotNull(result);
        Assert.AreEqual("Layout1", result.ProfileName);
    }

    [TestMethod]
    public void Undo_DecreasesUndoCount()
    {
        // Arrange
        _service.RecordChange(CreateTestLayout("L1"), "Change 1");
        _service.RecordChange(CreateTestLayout("L2"), "Change 2");
        _service.RecordChange(CreateTestLayout("L3"), "Change 3");

        Assert.AreEqual(2, _service.UndoCount);

        // Act
        _service.Undo();

        // Assert
        Assert.AreEqual(1, _service.UndoCount);
    }

    [TestMethod]
    public void Undo_IncreasesRedoCount()
    {
        // Arrange
        _service.RecordChange(CreateTestLayout("L1"), "Change 1");
        _service.RecordChange(CreateTestLayout("L2"), "Change 2");

        Assert.AreEqual(0, _service.RedoCount);

        // Act
        _service.Undo();

        // Assert
        Assert.AreEqual(1, _service.RedoCount);
        Assert.IsTrue(_service.CanRedo);
    }

    [TestMethod]
    public void Undo_RaisesHistoryChangedEvent()
    {
        // Arrange
        _service.RecordChange(CreateTestLayout("L1"), "Change 1");
        _service.RecordChange(CreateTestLayout("L2"), "Change 2");

        var eventRaised = false;
        _service.HistoryChanged += (s, e) => eventRaised = true;

        // Act
        _service.Undo();

        // Assert
        Assert.IsTrue(eventRaised);
    }

    [TestMethod]
    public void Undo_MultipleUndos_ReturnCorrectLayouts()
    {
        // Arrange
        _service.RecordChange(CreateTestLayout("L1"), "Change 1");
        _service.RecordChange(CreateTestLayout("L2"), "Change 2");
        _service.RecordChange(CreateTestLayout("L3"), "Change 3");

        // Act & Assert
        var result1 = _service.Undo();
        Assert.AreEqual("L2", result1?.ProfileName);

        var result2 = _service.Undo();
        Assert.AreEqual("L1", result2?.ProfileName);

        // No more to undo
        Assert.IsFalse(_service.CanUndo);
    }

    #endregion

    #region Redo Tests

    [TestMethod]
    public void Redo_WhenEmpty_ReturnsNull()
    {
        // Act
        var result = _service.Redo();

        // Assert
        Assert.IsNull(result);
    }

    [TestMethod]
    public void Redo_AfterUndo_ReturnsLayout()
    {
        // Arrange
        _service.RecordChange(CreateTestLayout("L1"), "Change 1");
        _service.RecordChange(CreateTestLayout("L2"), "Change 2");
        _service.Undo();

        // Act
        var result = _service.Redo();

        // Assert
        Assert.IsNotNull(result);
        Assert.AreEqual("L2", result.ProfileName);
    }

    [TestMethod]
    public void Redo_DecreasesRedoCount()
    {
        // Arrange
        _service.RecordChange(CreateTestLayout("L1"), "Change 1");
        _service.RecordChange(CreateTestLayout("L2"), "Change 2");
        _service.RecordChange(CreateTestLayout("L3"), "Change 3");
        _service.Undo();
        _service.Undo();

        Assert.AreEqual(2, _service.RedoCount);

        // Act
        _service.Redo();

        // Assert
        Assert.AreEqual(1, _service.RedoCount);
    }

    [TestMethod]
    public void Redo_IncreasesUndoCount()
    {
        // Arrange
        _service.RecordChange(CreateTestLayout("L1"), "Change 1");
        _service.RecordChange(CreateTestLayout("L2"), "Change 2");
        _service.Undo(); // UndoCount = 0

        Assert.AreEqual(0, _service.UndoCount);

        // Act
        _service.Redo();

        // Assert
        Assert.AreEqual(1, _service.UndoCount);
    }

    [TestMethod]
    public void Redo_RaisesHistoryChangedEvent()
    {
        // Arrange
        _service.RecordChange(CreateTestLayout("L1"), "Change 1");
        _service.RecordChange(CreateTestLayout("L2"), "Change 2");
        _service.Undo();

        var eventRaised = false;
        _service.HistoryChanged += (s, e) => eventRaised = true;

        // Act
        _service.Redo();

        // Assert
        Assert.IsTrue(eventRaised);
    }

    #endregion

    #region GetUndoHistory/GetRedoHistory Tests

    [TestMethod]
    public void GetUndoHistory_ReturnsDescriptions()
    {
        // Arrange
        _service.RecordChange(CreateTestLayout("L1"), "First change");
        _service.RecordChange(CreateTestLayout("L2"), "Second change");
        _service.RecordChange(CreateTestLayout("L3"), "Third change");

        // Act
        var history = _service.GetUndoHistory().ToList();

        // Assert - most recent first (stack order)
        Assert.AreEqual(2, history.Count);
        Assert.AreEqual("Second change", history[0]);
        Assert.AreEqual("First change", history[1]);
    }

    [TestMethod]
    public void GetRedoHistory_ReturnsDescriptions()
    {
        // Arrange
        _service.RecordChange(CreateTestLayout("L1"), "First change");
        _service.RecordChange(CreateTestLayout("L2"), "Second change");
        _service.RecordChange(CreateTestLayout("L3"), "Third change");
        _service.Undo();
        _service.Undo();

        // Act
        var history = _service.GetRedoHistory().ToList();

        // Assert
        Assert.AreEqual(2, history.Count);
        Assert.AreEqual("Second change", history[0]);
        Assert.AreEqual("Third change", history[1]);
    }

    #endregion

    #region ClearHistory Tests

    [TestMethod]
    public void ClearHistory_ResetsAllState()
    {
        // Arrange
        _service.RecordChange(CreateTestLayout("L1"), "Change 1");
        _service.RecordChange(CreateTestLayout("L2"), "Change 2");
        _service.RecordChange(CreateTestLayout("L3"), "Change 3");
        _service.Undo();

        Assert.IsTrue(_service.CanUndo);
        Assert.IsTrue(_service.CanRedo);

        // Act
        _service.ClearHistory();

        // Assert
        Assert.IsFalse(_service.CanUndo);
        Assert.IsFalse(_service.CanRedo);
        Assert.AreEqual(0, _service.UndoCount);
        Assert.AreEqual(0, _service.RedoCount);
    }

    [TestMethod]
    public void ClearHistory_RaisesHistoryChangedEvent()
    {
        // Arrange
        _service.RecordChange(CreateTestLayout("L1"), "Change 1");

        var eventRaised = false;
        _service.HistoryChanged += (s, e) => eventRaised = true;

        // Act
        _service.ClearHistory();

        // Assert
        Assert.IsTrue(eventRaised);
    }

    #endregion

    #region SetInitialState Tests

    [TestMethod]
    public void SetInitialState_DoesNotAffectHistory()
    {
        // Act
        _service.SetInitialState(CreateTestLayout("Initial"));

        // Assert - setting initial state doesn't create history
        Assert.IsFalse(_service.CanUndo);
        Assert.IsFalse(_service.CanRedo);
    }

    [TestMethod]
    public void SetInitialState_BecomesUndoTarget()
    {
        // Arrange
        _service.SetInitialState(CreateTestLayout("Initial"));
        _service.RecordChange(CreateTestLayout("Changed"), "User change");

        // Act
        var result = _service.Undo();

        // Assert - undo returns the initial state
        Assert.IsNotNull(result);
        Assert.AreEqual("Initial", result.ProfileName);
    }

    #endregion

    #region MaxHistorySize Tests

    [TestMethod]
    public void RecordChange_ExceedsMaxHistorySize_TrimsOldest()
    {
        // Arrange
        var service = new WorkspaceHistoryService(maxHistorySize: 5);

        // Act - record 10 changes
        for (var i = 0; i < 10; i++)
        {
            service.RecordChange(CreateTestLayout($"L{i}"), $"Change {i}");
        }

        // Assert - undo stack should be trimmed to max size
        // First change becomes current, then 9 changes pushed, but max is 5
        Assert.IsTrue(service.UndoCount <= 5);
    }

    #endregion

    #region HistoryChanged Event Tests

    [TestMethod]
    public void HistoryChangedEvent_ContainsCorrectState()
    {
        // Arrange
        WorkspaceHistoryChangedEventArgs? eventArgs = null;
        _service.HistoryChanged += (s, e) => eventArgs = e;

        _service.RecordChange(CreateTestLayout("L1"), "Change 1");
        _service.RecordChange(CreateTestLayout("L2"), "Change 2");
        _service.RecordChange(CreateTestLayout("L3"), "Change 3");

        // Act
        _service.Undo();

        // Assert
        Assert.IsNotNull(eventArgs);
        Assert.IsTrue(eventArgs.CanUndo);
        Assert.IsTrue(eventArgs.CanRedo);
        Assert.AreEqual(1, eventArgs.UndoCount);
        Assert.AreEqual(1, eventArgs.RedoCount);
    }

    #endregion

    #region Edge Cases

    [TestMethod]
    public void UndoRedo_ComplexSequence_MaintainsCorrectState()
    {
        // Arrange
        _service.SetInitialState(CreateTestLayout("Initial"));
        _service.RecordChange(CreateTestLayout("A"), "Change A");
        _service.RecordChange(CreateTestLayout("B"), "Change B");
        _service.RecordChange(CreateTestLayout("C"), "Change C");

        // Act & Assert
        Assert.AreEqual("B", _service.Undo()?.ProfileName);
        Assert.AreEqual("A", _service.Undo()?.ProfileName);
        Assert.AreEqual("B", _service.Redo()?.ProfileName);
        Assert.AreEqual("C", _service.Redo()?.ProfileName);
        Assert.IsFalse(_service.CanRedo);

        // New change after undo/redo
        _service.RecordChange(CreateTestLayout("D"), "Change D");
        Assert.IsFalse(_service.CanRedo);
        Assert.IsTrue(_service.CanUndo);
    }

    [TestMethod]
    public void RecordChange_DeepClonesLayout()
    {
        // Arrange
        var layout = CreateTestLayout("Original");

        // Act
        _service.RecordChange(layout, "Record");
        layout.ProfileName = "Modified"; // Modify after recording

        _service.RecordChange(CreateTestLayout("Another"), "Another");
        var undoneLayout = _service.Undo();

        // Assert - should return "Original", not "Modified"
        Assert.AreEqual("Original", undoneLayout?.ProfileName);
    }

    #endregion

    #region Helper Methods

    private static WorkspaceLayout CreateTestLayout(string name)
    {
        return new WorkspaceLayout
        {
            ProfileName = name
        };
    }

    #endregion
}
