using Microsoft.VisualStudio.TestTools.UnitTesting;
using VoiceStudio.App.Services;
using VoiceStudio.Core.Models;
using System.Linq;

namespace VoiceStudio.App.Tests.Services
{
    /// <summary>
    /// Integration tests for MultiSelectService (IDEA 12: Multi-Select System).
    /// Tests multi-select functionality across panels.
    /// </summary>
    [TestClass]
    public class MultiSelectServiceTests : TestBase
    {
        private MultiSelectService? _service;

        [TestInitialize]
        public override void TestInitialize()
        {
            base.TestInitialize();
            _service = new MultiSelectService();
        }

        [TestCleanup]
        public override void TestCleanup()
        {
            _service = null;
            base.TestCleanup();
        }

        [TestMethod]
        public void GetState_CreatesNewState_WhenNotExists()
        {
            // Arrange
            var panelId = "test-panel";

            // Act
            var state = _service!.GetState(panelId);

            // Assert
            Assert.IsNotNull(state);
            Assert.AreEqual(0, state.SelectedIds.Count);
        }

        [TestMethod]
        public void GetState_ReturnsExistingState_WhenExists()
        {
            // Arrange
            var panelId = "test-panel";
            var state1 = _service!.GetState(panelId);
            state1.Add("item1");

            // Act
            var state2 = _service.GetState(panelId);

            // Assert
            Assert.AreSame(state1, state2);
            Assert.AreEqual(1, state2.SelectedIds.Count);
            Assert.IsTrue(state2.SelectedIds.Contains("item1"));
        }

        [TestMethod]
        public void ClearSelection_ClearsItems_ForPanel()
        {
            // Arrange
            var panelId = "test-panel";
            var state = _service!.GetState(panelId);
            state.Add("item1");
            state.Add("item2");

            // Act
            _service.ClearSelection(panelId);

            // Assert
            Assert.AreEqual(0, state.SelectedIds.Count);
        }

        [TestMethod]
        public void ClearSelection_DoesNotAffect_OtherPanels()
        {
            // Arrange
            var panel1 = "panel1";
            var panel2 = "panel2";
            var state1 = _service!.GetState(panel1);
            var state2 = _service.GetState(panel2);
            state1.Add("item1");
            state2.Add("item2");

            // Act
            _service.ClearSelection(panel1);

            // Assert
            Assert.AreEqual(0, state1.SelectedIds.Count);
            Assert.AreEqual(1, state2.SelectedIds.Count);
            Assert.IsTrue(state2.SelectedIds.Contains("item2"));
        }

        [TestMethod]
        public void ClearAllSelections_ClearsAllPanels()
        {
            // Arrange
            var panel1 = "panel1";
            var panel2 = "panel2";
            var state1 = _service!.GetState(panel1);
            var state2 = _service.GetState(panel2);
            state1.Add("item1");
            state2.Add("item2");

            // Act
            _service.ClearAllSelections();

            // Assert
            Assert.AreEqual(0, state1.SelectedIds.Count);
            Assert.AreEqual(0, state2.SelectedIds.Count);
        }

        [TestMethod]
        public void RemoveState_RemovesPanelState()
        {
            // Arrange
            var panelId = "test-panel";
            var state1 = _service!.GetState(panelId);
            state1.Add("item1");

            // Act
            _service.RemoveState(panelId);
            var state2 = _service.GetState(panelId);

            // Assert
            Assert.AreNotSame(state1, state2);
            Assert.AreEqual(0, state2.SelectedIds.Count);
        }

        [TestMethod]
        public void SelectionChanged_Event_Raises_WhenSelectionChanges()
        {
            // Arrange
            var panelId = "test-panel";
            var eventRaised = false;
            string? eventPanelId = null;
            _service!.SelectionChanged += (s, e) =>
            {
                eventRaised = true;
                eventPanelId = e.PanelId;
            };

            var state = _service.GetState(panelId);

            // Act
            _service.OnSelectionChanged(panelId, state);

            // Assert
            Assert.IsTrue(eventRaised);
            Assert.AreEqual(panelId, eventPanelId);
        }

        [TestMethod]
        public void MultiSelectState_Add_AddsItem()
        {
            // Arrange
            var state = new MultiSelectState();
            var item = "test-item";

            // Act
            state.Add(item);

            // Assert
            Assert.AreEqual(1, state.SelectedIds.Count);
            Assert.IsTrue(state.SelectedIds.Contains(item));
        }

        [TestMethod]
        public void MultiSelectState_Remove_RemovesItem()
        {
            // Arrange
            var state = new MultiSelectState();
            var item = "test-item";
            state.Add(item);

            // Act
            state.Remove(item);

            // Assert
            Assert.AreEqual(0, state.SelectedIds.Count);
            Assert.IsFalse(state.SelectedIds.Contains(item));
        }

        [TestMethod]
        public void MultiSelectState_Toggle_TogglesSelection()
        {
            // Arrange
            var state = new MultiSelectState();
            var item = "test-item";

            // Act - First toggle (add)
            state.Toggle(item);

            // Assert
            Assert.AreEqual(1, state.SelectedIds.Count);
            Assert.IsTrue(state.SelectedIds.Contains(item));

            // Act - Second toggle (remove)
            state.Toggle(item);

            // Assert
            Assert.AreEqual(0, state.SelectedIds.Count);
            Assert.IsFalse(state.SelectedIds.Contains(item));
        }

        [TestMethod]
        public void MultiSelectState_Clear_ClearsAllItems()
        {
            // Arrange
            var state = new MultiSelectState();
            state.Add("item1");
            state.Add("item2");
            state.Add("item3");

            // Act
            state.Clear();

            // Assert
            Assert.AreEqual(0, state.SelectedIds.Count);
        }

        [TestMethod]
        public void MultiSelectState_SetRange_SetsRange()
        {
            // Arrange
            var state = new MultiSelectState();
            var items = new[] { "item1", "item2", "item3", "item4", "item5" };

            // Act
            state.SetRange("item2", "item4", items);

            // Assert
            Assert.AreEqual(3, state.SelectedIds.Count);
            Assert.IsTrue(state.SelectedIds.Contains("item2"));
            Assert.IsTrue(state.SelectedIds.Contains("item3"));
            Assert.IsTrue(state.SelectedIds.Contains("item4"));
            Assert.IsFalse(state.SelectedIds.Contains("item1"));
            Assert.IsFalse(state.SelectedIds.Contains("item5"));
            Assert.IsTrue(state.IsRangeSelection);
            Assert.AreEqual("item2", state.RangeAnchorId);
        }

        [TestMethod]
        public void MultiSelectState_SetSingle_SetsSingleSelection()
        {
            // Arrange
            var state = new MultiSelectState();
            state.Add("item1");
            state.Add("item2");

            // Act
            state.SetSingle("item3");

            // Assert
            Assert.AreEqual(1, state.SelectedIds.Count);
            Assert.IsTrue(state.SelectedIds.Contains("item3"));
            Assert.AreEqual("item3", state.RangeAnchorId);
        }

        [TestMethod]
        public void MultiSelectState_Properties_ReturnCorrectValues()
        {
            // Arrange
            var state = new MultiSelectState();

            // Act & Assert - Empty state
            Assert.AreEqual(0, state.Count);
            Assert.IsFalse(state.HasSelection);
            Assert.IsFalse(state.IsMultipleSelection);

            // Act - Add one item
            state.Add("item1");

            // Assert
            Assert.AreEqual(1, state.Count);
            Assert.IsTrue(state.HasSelection);
            Assert.IsFalse(state.IsMultipleSelection);

            // Act - Add second item
            state.Add("item2");

            // Assert
            Assert.AreEqual(2, state.Count);
            Assert.IsTrue(state.HasSelection);
            Assert.IsTrue(state.IsMultipleSelection);
        }
    }
}
