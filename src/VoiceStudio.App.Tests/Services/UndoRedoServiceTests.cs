using Microsoft.VisualStudio.TestTools.UnitTesting;
using System;
using System.Collections.Generic;
using System.Linq;
using System.Threading.Tasks;
using VoiceStudio.App.Services;

namespace VoiceStudio.App.Tests.Services;

/// <summary>
/// Unit tests for UndoRedoService.
/// Tests undo/redo stack management, action registration, and property notifications.
/// </summary>
[TestClass]
public class UndoRedoServiceTests : TestBase
{
    private UndoRedoService _service = null!;

    [TestInitialize]
    public override void TestInitialize()
    {
        base.TestInitialize();
        _service = new UndoRedoService();
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
        // Assert
        Assert.IsFalse(_service.CanUndo);
    }

    [TestMethod]
    public void InitialState_CanRedo_IsFalse()
    {
        // Assert
        Assert.IsFalse(_service.CanRedo);
    }

    [TestMethod]
    public void InitialState_UndoCount_IsZero()
    {
        // Assert
        Assert.AreEqual(0, _service.UndoCount);
    }

    [TestMethod]
    public void InitialState_RedoCount_IsZero()
    {
        // Assert
        Assert.AreEqual(0, _service.RedoCount);
    }

    [TestMethod]
    public void InitialState_NextUndoActionName_IsNull()
    {
        // Assert
        Assert.IsNull(_service.NextUndoActionName);
    }

    [TestMethod]
    public void InitialState_NextRedoActionName_IsNull()
    {
        // Assert
        Assert.IsNull(_service.NextRedoActionName);
    }

    #endregion

    #region RegisterAction Tests

    [TestMethod]
    public void RegisterAction_Null_ThrowsArgumentNullException()
    {
        // Act & Assert
        Assert.ThrowsException<ArgumentNullException>(() => _service.RegisterAction(null!));
    }

    [TestMethod]
    public void RegisterAction_SingleAction_IncreasesUndoCount()
    {
        // Arrange
        var action = new MockUndoableAction("Action1");

        // Act
        _service.RegisterAction(action);

        // Assert
        Assert.AreEqual(1, _service.UndoCount);
        Assert.IsTrue(_service.CanUndo);
    }

    [TestMethod]
    public void RegisterAction_SingleAction_SetsNextUndoActionName()
    {
        // Arrange
        var action = new MockUndoableAction("MyAction");

        // Act
        _service.RegisterAction(action);

        // Assert
        Assert.AreEqual("MyAction", _service.NextUndoActionName);
    }

    [TestMethod]
    public void RegisterAction_ClearsRedoStack()
    {
        // Arrange
        _service.RegisterAction(new MockUndoableAction("Action1"));
        _service.Undo();
        Assert.IsTrue(_service.CanRedo);

        // Act
        _service.RegisterAction(new MockUndoableAction("Action2"));

        // Assert
        Assert.IsFalse(_service.CanRedo);
        Assert.AreEqual(0, _service.RedoCount);
    }

    [TestMethod]
    public void RegisterAction_MultipleActions_StacksCorrectly()
    {
        // Arrange & Act
        _service.RegisterAction(new MockUndoableAction("First"));
        _service.RegisterAction(new MockUndoableAction("Second"));
        _service.RegisterAction(new MockUndoableAction("Third"));

        // Assert
        Assert.AreEqual(3, _service.UndoCount);
        Assert.AreEqual("Third", _service.NextUndoActionName);
    }

    #endregion

    #region Undo Tests

    [TestMethod]
    public void Undo_EmptyStack_ReturnsFalse()
    {
        // Act
        var result = _service.Undo();

        // Assert
        Assert.IsFalse(result);
    }

    [TestMethod]
    public void Undo_SingleAction_DecreasesUndoCount()
    {
        // Arrange
        _service.RegisterAction(new MockUndoableAction("Action1"));
        Assert.AreEqual(1, _service.UndoCount);

        // Act
        _service.Undo();

        // Assert
        Assert.AreEqual(0, _service.UndoCount);
    }

    [TestMethod]
    public void Undo_SingleAction_IncreasesRedoCount()
    {
        // Arrange
        _service.RegisterAction(new MockUndoableAction("Action1"));

        // Act
        _service.Undo();

        // Assert
        Assert.AreEqual(1, _service.RedoCount);
        Assert.IsTrue(_service.CanRedo);
    }

    [TestMethod]
    public void Undo_CallsUndoOnAction()
    {
        // Arrange
        var action = new MockUndoableAction("Action1");
        _service.RegisterAction(action);

        // Act
        _service.Undo();

        // Assert
        Assert.IsTrue(action.UndoCalled);
        Assert.IsFalse(action.RedoCalled);
    }

    [TestMethod]
    public void Undo_UpdatesNextUndoActionName()
    {
        // Arrange
        _service.RegisterAction(new MockUndoableAction("First"));
        _service.RegisterAction(new MockUndoableAction("Second"));
        Assert.AreEqual("Second", _service.NextUndoActionName);

        // Act
        _service.Undo();

        // Assert
        Assert.AreEqual("First", _service.NextUndoActionName);
    }

    [TestMethod]
    public void Undo_UpdatesNextRedoActionName()
    {
        // Arrange
        _service.RegisterAction(new MockUndoableAction("MyAction"));
        Assert.IsNull(_service.NextRedoActionName);

        // Act
        _service.Undo();

        // Assert
        Assert.AreEqual("MyAction", _service.NextRedoActionName);
    }

    [TestMethod]
    public void Undo_ReturnsTrue_WhenSuccessful()
    {
        // Arrange
        _service.RegisterAction(new MockUndoableAction("Action1"));

        // Act
        var result = _service.Undo();

        // Assert
        Assert.IsTrue(result);
    }

    #endregion

    #region Redo Tests

    [TestMethod]
    public void Redo_EmptyStack_ReturnsFalse()
    {
        // Act
        var result = _service.Redo();

        // Assert
        Assert.IsFalse(result);
    }

    [TestMethod]
    public void Redo_AfterUndo_IncreasesUndoCount()
    {
        // Arrange
        _service.RegisterAction(new MockUndoableAction("Action1"));
        _service.Undo();
        Assert.AreEqual(0, _service.UndoCount);

        // Act
        _service.Redo();

        // Assert
        Assert.AreEqual(1, _service.UndoCount);
    }

    [TestMethod]
    public void Redo_AfterUndo_DecreasesRedoCount()
    {
        // Arrange
        _service.RegisterAction(new MockUndoableAction("Action1"));
        _service.Undo();
        Assert.AreEqual(1, _service.RedoCount);

        // Act
        _service.Redo();

        // Assert
        Assert.AreEqual(0, _service.RedoCount);
    }

    [TestMethod]
    public void Redo_CallsRedoOnAction()
    {
        // Arrange
        var action = new MockUndoableAction("Action1");
        _service.RegisterAction(action);
        _service.Undo();
        action.UndoCalled = false; // Reset for clarity

        // Act
        _service.Redo();

        // Assert
        Assert.IsTrue(action.RedoCalled);
    }

    [TestMethod]
    public void Redo_ReturnsTrue_WhenSuccessful()
    {
        // Arrange
        _service.RegisterAction(new MockUndoableAction("Action1"));
        _service.Undo();

        // Act
        var result = _service.Redo();

        // Assert
        Assert.IsTrue(result);
    }

    [TestMethod]
    public void Redo_UpdatesNextUndoActionName()
    {
        // Arrange
        _service.RegisterAction(new MockUndoableAction("MyAction"));
        _service.Undo();
        Assert.IsNull(_service.NextUndoActionName);

        // Act
        _service.Redo();

        // Assert
        Assert.AreEqual("MyAction", _service.NextUndoActionName);
    }

    #endregion

    #region Clear Tests

    [TestMethod]
    public void Clear_EmptiesBothStacks()
    {
        // Arrange
        _service.RegisterAction(new MockUndoableAction("Action1"));
        _service.RegisterAction(new MockUndoableAction("Action2"));
        _service.Undo();
        Assert.AreEqual(1, _service.UndoCount);
        Assert.AreEqual(1, _service.RedoCount);

        // Act
        _service.Clear();

        // Assert
        Assert.AreEqual(0, _service.UndoCount);
        Assert.AreEqual(0, _service.RedoCount);
        Assert.IsFalse(_service.CanUndo);
        Assert.IsFalse(_service.CanRedo);
    }

    [TestMethod]
    public void Clear_ResetsActionNames()
    {
        // Arrange
        _service.RegisterAction(new MockUndoableAction("Action1"));
        _service.Undo();
        Assert.IsNotNull(_service.NextRedoActionName);

        // Act
        _service.Clear();

        // Assert
        Assert.IsNull(_service.NextUndoActionName);
        Assert.IsNull(_service.NextRedoActionName);
    }

    #endregion

    #region History Tests

    [TestMethod]
    public void GetUndoHistory_Empty_ReturnsEmptyList()
    {
        // Act
        var history = _service.GetUndoHistory();

        // Assert
        Assert.AreEqual(0, history.Count);
    }

    [TestMethod]
    public void GetUndoHistory_ReturnsActionsInCorrectOrder()
    {
        // Arrange
        _service.RegisterAction(new MockUndoableAction("First"));
        _service.RegisterAction(new MockUndoableAction("Second"));
        _service.RegisterAction(new MockUndoableAction("Third"));

        // Act
        var history = _service.GetUndoHistory();

        // Assert - most recent first (stack order)
        Assert.AreEqual(3, history.Count);
        Assert.AreEqual("Third", history[0]);
        Assert.AreEqual("Second", history[1]);
        Assert.AreEqual("First", history[2]);
    }

    [TestMethod]
    public void GetUndoHistory_RespectsCountLimit()
    {
        // Arrange
        for (int i = 0; i < 20; i++)
        {
            _service.RegisterAction(new MockUndoableAction($"Action{i}"));
        }

        // Act
        var history = _service.GetUndoHistory(5);

        // Assert
        Assert.AreEqual(5, history.Count);
    }

    [TestMethod]
    public void GetRedoHistory_Empty_ReturnsEmptyList()
    {
        // Act
        var history = _service.GetRedoHistory();

        // Assert
        Assert.AreEqual(0, history.Count);
    }

    [TestMethod]
    public void GetRedoHistory_AfterUndo_ReturnsActionsInCorrectOrder()
    {
        // Arrange
        _service.RegisterAction(new MockUndoableAction("First"));
        _service.RegisterAction(new MockUndoableAction("Second"));
        _service.RegisterAction(new MockUndoableAction("Third"));
        _service.Undo();
        _service.Undo();

        // Act
        var history = _service.GetRedoHistory();

        // Assert - most recently undone first
        Assert.AreEqual(2, history.Count);
        Assert.AreEqual("Second", history[0]);
        Assert.AreEqual("Third", history[1]);
    }

    #endregion

    #region Stack Size Limit Tests

    [TestMethod]
    public void RegisterAction_ExceedsMaxSize_TrimsOldestActions()
    {
        // Arrange - register 101+ actions (max is 100)
        for (int i = 0; i < 105; i++)
        {
            _service.RegisterAction(new MockUndoableAction($"Action{i}"));
        }

        // Assert - should be capped at 100
        Assert.IsTrue(_service.UndoCount <= 100);
    }

    #endregion

    #region Property Notification Tests

    [TestMethod]
    public void RegisterAction_RaisesPropertyChangedForCanUndo()
    {
        // Arrange
        var propertyChangedRaised = false;
        _service.PropertyChanged += (s, e) =>
        {
            if (e.PropertyName == nameof(UndoRedoService.CanUndo))
                propertyChangedRaised = true;
        };

        // Act
        _service.RegisterAction(new MockUndoableAction("Action1"));

        // Assert
        Assert.IsTrue(propertyChangedRaised);
    }

    [TestMethod]
    public void Undo_RaisesPropertyChangedForCanRedo()
    {
        // Arrange
        _service.RegisterAction(new MockUndoableAction("Action1"));
        var propertyChangedRaised = false;
        _service.PropertyChanged += (s, e) =>
        {
            if (e.PropertyName == nameof(UndoRedoService.CanRedo))
                propertyChangedRaised = true;
        };

        // Act
        _service.Undo();

        // Assert
        Assert.IsTrue(propertyChangedRaised);
    }

    #endregion

    #region Undo/Redo Sequence Tests

    [TestMethod]
    public void UndoRedo_Sequence_WorksCorrectly()
    {
        // Arrange
        var action1 = new MockUndoableAction("Action1");
        var action2 = new MockUndoableAction("Action2");
        _service.RegisterAction(action1);
        _service.RegisterAction(action2);

        // Act & Assert - Undo Action2
        _service.Undo();
        Assert.IsTrue(action2.UndoCalled);
        Assert.AreEqual("Action1", _service.NextUndoActionName);
        Assert.AreEqual("Action2", _service.NextRedoActionName);

        // Act & Assert - Redo Action2
        _service.Redo();
        Assert.IsTrue(action2.RedoCalled);
        Assert.AreEqual("Action2", _service.NextUndoActionName);
        Assert.IsNull(_service.NextRedoActionName);

        // Act & Assert - Undo both
        _service.Undo();
        _service.Undo();
        Assert.AreEqual(0, _service.UndoCount);
        Assert.AreEqual(2, _service.RedoCount);
    }

    #endregion

    #region Mock Classes

    /// <summary>
    /// Mock implementation of IUndoableAction for testing.
    /// </summary>
    private class MockUndoableAction : IUndoableAction
    {
        public string ActionName { get; }
        public bool UndoCalled { get; set; }
        public bool RedoCalled { get; set; }

        public MockUndoableAction(string name)
        {
            ActionName = name;
        }

        public void Undo()
        {
            UndoCalled = true;
        }

        public void Redo()
        {
            RedoCalled = true;
        }
    }

    #endregion
}
