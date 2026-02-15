using Microsoft.VisualStudio.TestTools.UnitTesting;
using System;
using System.Linq;
using System.Threading.Tasks;
using VoiceStudio.Core.State;

namespace VoiceStudio.App.Tests.State;

[TestClass]
public class SelectionStackTests
{
    private SelectionStack _stack = null!;

    [TestInitialize]
    public void SetUp()
    {
        _stack = new SelectionStack();
    }

    private SelectionEntry CreateEntry(string id, string name = "Test", string type = "profile")
    {
        return new SelectionEntry
        {
            ItemId = id,
            DisplayName = name,
            ItemType = type
        };
    }

    #region Initial State Tests

    [TestMethod]
    public void InitialState_Current_IsNull()
    {
        Assert.IsNull(_stack.Current);
    }

    [TestMethod]
    public void InitialState_CanGoBack_IsFalse()
    {
        Assert.IsFalse(_stack.CanGoBack);
    }

    [TestMethod]
    public void InitialState_CanGoForward_IsFalse()
    {
        Assert.IsFalse(_stack.CanGoForward);
    }

    [TestMethod]
    public void InitialState_BackCount_IsZero()
    {
        Assert.AreEqual(0, _stack.BackCount);
    }

    [TestMethod]
    public void InitialState_ForwardCount_IsZero()
    {
        Assert.AreEqual(0, _stack.ForwardCount);
    }

    [TestMethod]
    public void InitialState_GetBackHistory_ReturnsEmpty()
    {
        Assert.AreEqual(0, _stack.GetBackHistory().Count);
    }

    [TestMethod]
    public void InitialState_GetForwardHistory_ReturnsEmpty()
    {
        Assert.AreEqual(0, _stack.GetForwardHistory().Count);
    }

    #endregion

    #region Push Tests

    [TestMethod]
    public void Push_FirstEntry_SetsCurrent()
    {
        // Arrange
        var entry = CreateEntry("1");

        // Act
        _stack.Push(entry);

        // Assert
        Assert.AreEqual(entry, _stack.Current);
    }

    [TestMethod]
    public void Push_SecondEntry_UpdatesCurrent()
    {
        // Arrange
        var entry1 = CreateEntry("1");
        var entry2 = CreateEntry("2");

        // Act
        _stack.Push(entry1);
        _stack.Push(entry2);

        // Assert
        Assert.AreEqual(entry2, _stack.Current);
    }

    [TestMethod]
    public void Push_SecondEntry_AddsFirstToBackStack()
    {
        // Arrange
        var entry1 = CreateEntry("1");
        var entry2 = CreateEntry("2");

        // Act
        _stack.Push(entry1);
        _stack.Push(entry2);

        // Assert
        Assert.AreEqual(1, _stack.BackCount);
        Assert.IsTrue(_stack.CanGoBack);
    }

    [TestMethod]
    public void Push_ClearsForwardStack()
    {
        // Arrange
        _stack.Push(CreateEntry("1"));
        _stack.Push(CreateEntry("2"));
        _stack.GoBack();
        Assert.IsTrue(_stack.CanGoForward);

        // Act
        _stack.Push(CreateEntry("3"));

        // Assert
        Assert.IsFalse(_stack.CanGoForward);
        Assert.AreEqual(0, _stack.ForwardCount);
    }

    [TestMethod]
    public void Push_SameItemId_DoesNothing()
    {
        // Arrange
        var entry1 = CreateEntry("1", "Name1");
        var entry2 = CreateEntry("1", "Name2"); // Same ID

        // Act
        _stack.Push(entry1);
        _stack.Push(entry2);

        // Assert - should still be entry1, no back history
        Assert.AreEqual("Name1", _stack.Current?.DisplayName);
        Assert.AreEqual(0, _stack.BackCount);
    }

    [TestMethod]
    public void Push_NullEntry_ThrowsArgumentNullException()
    {
        Assert.ThrowsException<ArgumentNullException>(() => _stack.Push(null!));
    }

    [TestMethod]
    public void Push_RaisesNavigatedEvent()
    {
        // Arrange
        SelectionNavigationEventArgs? eventArgs = null;
        _stack.Navigated += (s, e) => eventArgs = e;

        // Act
        var entry = CreateEntry("1");
        _stack.Push(entry);

        // Assert
        Assert.IsNotNull(eventArgs);
        Assert.AreEqual(NavigationType.Push, eventArgs.NavigationType);
        Assert.AreEqual(entry, eventArgs.Current);
        Assert.IsNull(eventArgs.Previous);
    }

    [TestMethod]
    public void Push_SecondEntry_EventContainsPrevious()
    {
        // Arrange
        var entry1 = CreateEntry("1");
        _stack.Push(entry1);

        SelectionNavigationEventArgs? eventArgs = null;
        _stack.Navigated += (s, e) => eventArgs = e;

        // Act
        var entry2 = CreateEntry("2");
        _stack.Push(entry2);

        // Assert
        Assert.IsNotNull(eventArgs);
        Assert.AreEqual(entry1, eventArgs.Previous);
        Assert.AreEqual(entry2, eventArgs.Current);
    }

    #endregion

    #region GoBack Tests

    [TestMethod]
    public void GoBack_WithHistory_ReturnsPreviousEntry()
    {
        // Arrange
        var entry1 = CreateEntry("1");
        var entry2 = CreateEntry("2");
        _stack.Push(entry1);
        _stack.Push(entry2);

        // Act
        var result = _stack.GoBack();

        // Assert
        Assert.AreEqual(entry1, result);
        Assert.AreEqual(entry1, _stack.Current);
    }

    [TestMethod]
    public void GoBack_WithoutHistory_ReturnsNull()
    {
        // Act
        var result = _stack.GoBack();

        // Assert
        Assert.IsNull(result);
    }

    [TestMethod]
    public void GoBack_AddsPreviousToForwardStack()
    {
        // Arrange
        var entry1 = CreateEntry("1");
        var entry2 = CreateEntry("2");
        _stack.Push(entry1);
        _stack.Push(entry2);

        // Act
        _stack.GoBack();

        // Assert
        Assert.IsTrue(_stack.CanGoForward);
        Assert.AreEqual(1, _stack.ForwardCount);
    }

    [TestMethod]
    public void GoBack_RaisesNavigatedEvent()
    {
        // Arrange
        var entry1 = CreateEntry("1");
        var entry2 = CreateEntry("2");
        _stack.Push(entry1);
        _stack.Push(entry2);

        SelectionNavigationEventArgs? eventArgs = null;
        _stack.Navigated += (s, e) => eventArgs = e;

        // Act
        _stack.GoBack();

        // Assert
        Assert.IsNotNull(eventArgs);
        Assert.AreEqual(NavigationType.Back, eventArgs.NavigationType);
        Assert.AreEqual(entry2, eventArgs.Previous);
        Assert.AreEqual(entry1, eventArgs.Current);
    }

    [TestMethod]
    public void GoBack_MultipleTimes_NavigatesEntireHistory()
    {
        // Arrange
        _stack.Push(CreateEntry("1"));
        _stack.Push(CreateEntry("2"));
        _stack.Push(CreateEntry("3"));

        // Act & Assert
        _stack.GoBack();
        Assert.AreEqual("2", _stack.Current?.ItemId);

        _stack.GoBack();
        Assert.AreEqual("1", _stack.Current?.ItemId);

        var result = _stack.GoBack();
        Assert.IsNull(result); // No more history
    }

    #endregion

    #region GoForward Tests

    [TestMethod]
    public void GoForward_WithHistory_ReturnsNextEntry()
    {
        // Arrange
        var entry1 = CreateEntry("1");
        var entry2 = CreateEntry("2");
        _stack.Push(entry1);
        _stack.Push(entry2);
        _stack.GoBack();

        // Act
        var result = _stack.GoForward();

        // Assert
        Assert.AreEqual(entry2, result);
        Assert.AreEqual(entry2, _stack.Current);
    }

    [TestMethod]
    public void GoForward_WithoutHistory_ReturnsNull()
    {
        // Act
        var result = _stack.GoForward();

        // Assert
        Assert.IsNull(result);
    }

    [TestMethod]
    public void GoForward_AddsPreviousToBackStack()
    {
        // Arrange
        _stack.Push(CreateEntry("1"));
        _stack.Push(CreateEntry("2"));
        _stack.GoBack();

        var backCountBefore = _stack.BackCount;

        // Act
        _stack.GoForward();

        // Assert
        Assert.AreEqual(backCountBefore + 1, _stack.BackCount);
    }

    [TestMethod]
    public void GoForward_RaisesNavigatedEvent()
    {
        // Arrange
        var entry1 = CreateEntry("1");
        var entry2 = CreateEntry("2");
        _stack.Push(entry1);
        _stack.Push(entry2);
        _stack.GoBack();

        SelectionNavigationEventArgs? eventArgs = null;
        _stack.Navigated += (s, e) => eventArgs = e;

        // Act
        _stack.GoForward();

        // Assert
        Assert.IsNotNull(eventArgs);
        Assert.AreEqual(NavigationType.Forward, eventArgs.NavigationType);
        Assert.AreEqual(entry1, eventArgs.Previous);
        Assert.AreEqual(entry2, eventArgs.Current);
    }

    #endregion

    #region Clear Tests

    [TestMethod]
    public void Clear_RemovesAllHistory()
    {
        // Arrange
        _stack.Push(CreateEntry("1"));
        _stack.Push(CreateEntry("2"));
        _stack.Push(CreateEntry("3"));
        _stack.GoBack();

        // Act
        _stack.Clear();

        // Assert
        Assert.IsNull(_stack.Current);
        Assert.AreEqual(0, _stack.BackCount);
        Assert.AreEqual(0, _stack.ForwardCount);
        Assert.IsFalse(_stack.CanGoBack);
        Assert.IsFalse(_stack.CanGoForward);
    }

    [TestMethod]
    public void Clear_RaisesNavigatedEvent()
    {
        // Arrange
        var entry = CreateEntry("1");
        _stack.Push(entry);

        SelectionNavigationEventArgs? eventArgs = null;
        _stack.Navigated += (s, e) => eventArgs = e;

        // Act
        _stack.Clear();

        // Assert
        Assert.IsNotNull(eventArgs);
        Assert.AreEqual(NavigationType.Clear, eventArgs.NavigationType);
        Assert.AreEqual(entry, eventArgs.Previous);
        Assert.IsNull(eventArgs.Current);
    }

    #endregion

    #region History Retrieval Tests

    [TestMethod]
    public void GetBackHistory_ReturnsEntriesInCorrectOrder()
    {
        // Arrange
        _stack.Push(CreateEntry("1"));
        _stack.Push(CreateEntry("2"));
        _stack.Push(CreateEntry("3"));

        // Act
        var history = _stack.GetBackHistory();

        // Assert - most recent first (Stack order)
        Assert.AreEqual(2, history.Count);
        Assert.AreEqual("2", history[0].ItemId);
        Assert.AreEqual("1", history[1].ItemId);
    }

    [TestMethod]
    public void GetForwardHistory_ReturnsEntriesInCorrectOrder()
    {
        // Arrange
        _stack.Push(CreateEntry("1"));
        _stack.Push(CreateEntry("2"));
        _stack.Push(CreateEntry("3"));
        _stack.GoBack(); // current=2, forward=[3]
        _stack.GoBack(); // current=1, forward=[3,2]

        // Act
        var history = _stack.GetForwardHistory();

        // Assert - Stack.ToArray returns in LIFO order (most recently pushed first)
        // Forward stack has: first pushed 3, then pushed 2
        // So ToArray returns [2, 3] (2 was pushed most recently to forward stack)
        Assert.AreEqual(2, history.Count);
        Assert.AreEqual("2", history[0].ItemId);
        Assert.AreEqual("3", history[1].ItemId);
    }

    #endregion

    #region Max History Size Tests

    [TestMethod]
    public void Push_ExceedsMaxHistorySize_TrimsEntries()
    {
        // Arrange
        var smallStack = new SelectionStack(maxHistorySize: 3);

        // Act - push 5 entries (max is 3)
        smallStack.Push(CreateEntry("1"));
        smallStack.Push(CreateEntry("2"));
        smallStack.Push(CreateEntry("3"));
        smallStack.Push(CreateEntry("4"));
        smallStack.Push(CreateEntry("5"));

        // Assert - only 3 entries in back stack, current is "5"
        Assert.AreEqual(3, smallStack.BackCount);
        Assert.AreEqual("5", smallStack.Current?.ItemId);
        
        // The implementation trims entries to keep backstack at maxHistorySize
        var history = smallStack.GetBackHistory();
        Assert.AreEqual(3, history.Count);
    }

    #endregion

    #region Thread Safety Tests

    [TestMethod]
    public void ConcurrentPush_IsThreadSafe()
    {
        // Arrange
        var tasks = new Task[10];

        // Act
        for (int i = 0; i < 10; i++)
        {
            var id = i.ToString();
            tasks[i] = Task.Run(() =>
            {
                for (int j = 0; j < 100; j++)
                {
                    _stack.Push(CreateEntry($"{id}-{j}"));
                }
            });
        }

        Task.WaitAll(tasks);

        // Assert - no exception occurred and stack is in valid state
        Assert.IsNotNull(_stack.Current);
        Assert.IsTrue(_stack.BackCount > 0);
    }

    [TestMethod]
    public void ConcurrentNavigation_IsThreadSafe()
    {
        // Arrange - fill the stack
        for (int i = 0; i < 100; i++)
        {
            _stack.Push(CreateEntry(i.ToString()));
        }

        var tasks = new Task[4];

        // Act - concurrent back/forward navigation
        tasks[0] = Task.Run(() =>
        {
            for (int i = 0; i < 50; i++) _stack.GoBack();
        });
        tasks[1] = Task.Run(() =>
        {
            for (int i = 0; i < 50; i++) _stack.GoForward();
        });
        tasks[2] = Task.Run(() =>
        {
            for (int i = 0; i < 10; i++) _stack.Push(CreateEntry($"new-{i}"));
        });
        tasks[3] = Task.Run(() =>
        {
            for (int i = 0; i < 20; i++)
            {
                _ = _stack.GetBackHistory();
                _ = _stack.GetForwardHistory();
            }
        });

        Task.WaitAll(tasks);

        // Assert - no exception, stack is valid
        Assert.IsTrue(_stack.BackCount >= 0);
        Assert.IsTrue(_stack.ForwardCount >= 0);
    }

    #endregion

    #region SelectionEntry Tests

    [TestMethod]
    public void SelectionEntry_RequiredProperties_AreSet()
    {
        // Arrange & Act
        var entry = new SelectionEntry
        {
            ItemId = "test-id",
            DisplayName = "Test Name",
            ItemType = "profile"
        };

        // Assert
        Assert.AreEqual("test-id", entry.ItemId);
        Assert.AreEqual("Test Name", entry.DisplayName);
        Assert.AreEqual("profile", entry.ItemType);
    }

    [TestMethod]
    public void SelectionEntry_OptionalProperties_HaveDefaults()
    {
        // Arrange & Act
        var entry = new SelectionEntry
        {
            ItemId = "id",
            DisplayName = "name",
            ItemType = "type"
        };

        // Assert
        Assert.IsNull(entry.SourcePanelId);
        Assert.IsNull(entry.Metadata);
        Assert.IsTrue(entry.Timestamp <= DateTimeOffset.Now);
    }

    [TestMethod]
    public void SelectionEntry_WithAllProperties_SetsCorrectly()
    {
        // Arrange
        var metadata = new System.Collections.Generic.Dictionary<string, object>
        {
            ["key"] = "value"
        };

        // Act
        var entry = new SelectionEntry
        {
            ItemId = "id",
            DisplayName = "name",
            ItemType = "type",
            SourcePanelId = "panel1",
            Metadata = metadata
        };

        // Assert
        Assert.AreEqual("panel1", entry.SourcePanelId);
        Assert.AreEqual("value", entry.Metadata?["key"]);
    }

    #endregion
}
