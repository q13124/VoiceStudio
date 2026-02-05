using Microsoft.VisualStudio.TestTools.UnitTesting;
using System;
using System.Linq;
using VoiceStudio.App.Services;

namespace VoiceStudio.App.Tests.Services
{
    /// <summary>
    /// Unit tests for CommandRegistry service.
    /// Tests command registration, retrieval, and execution.
    /// </summary>
    [TestClass]
    public class CommandRegistryTests
    {
        private CommandRegistry _sut = null!;

        [TestInitialize]
        public void Setup()
        {
            _sut = new CommandRegistry();
        }

        #region Initial State Tests

        [TestMethod]
        public void Constructor_GetAllCommands_ReturnsEmptyList()
        {
            // Act
            var commands = _sut.GetAllCommands();

            // Assert
            Assert.IsNotNull(commands);
            Assert.AreEqual(0, commands.Count());
        }

        #endregion

        #region RegisterCommand Tests

        [TestMethod]
        public void RegisterCommand_AddsCommandToRegistry()
        {
            // Arrange
            Action action = () => { };

            // Act
            _sut.RegisterCommand("test.command", "Test Command", "A test command", "Testing", action);
            var commands = _sut.GetAllCommands().ToList();

            // Assert
            Assert.AreEqual(1, commands.Count);
            Assert.AreEqual("test.command", commands[0].CommandId);
        }

        [TestMethod]
        public void RegisterCommand_SetsAllProperties()
        {
            // Arrange
            Action action = () => { };

            // Act
            _sut.RegisterCommand(
                commandId: "file.new",
                title: "New File",
                description: "Creates a new file",
                category: "File",
                action: action,
                shortcut: "Ctrl+N");

            var command = _sut.GetAllCommands().First();

            // Assert
            Assert.AreEqual("file.new", command.CommandId);
            Assert.AreEqual("New File", command.Title);
            Assert.AreEqual("Creates a new file", command.Description);
            Assert.AreEqual("File", command.Category);
            Assert.AreEqual("Ctrl+N", command.Shortcut);
        }

        [TestMethod]
        public void RegisterCommand_WithNullShortcut_SetsEmptyString()
        {
            // Arrange
            Action action = () => { };

            // Act
            _sut.RegisterCommand("no.shortcut", "No Shortcut", "Command without shortcut", "General", action, null);

            var command = _sut.GetAllCommands().First();

            // Assert
            Assert.AreEqual(string.Empty, command.Shortcut);
        }

        [TestMethod]
        public void RegisterCommand_MultipleTimes_AddsAllCommands()
        {
            // Arrange
            Action action = () => { };

            // Act
            _sut.RegisterCommand("cmd1", "Command 1", "First", "Cat1", action);
            _sut.RegisterCommand("cmd2", "Command 2", "Second", "Cat1", action);
            _sut.RegisterCommand("cmd3", "Command 3", "Third", "Cat2", action);

            var commands = _sut.GetAllCommands().ToList();

            // Assert
            Assert.AreEqual(3, commands.Count);
        }

        [TestMethod]
        public void RegisterCommand_SameIdTwice_ReplacesExisting()
        {
            // Arrange
            int callCount = 0;
            Action action1 = () => callCount = 1;
            Action action2 = () => callCount = 2;

            // Act
            _sut.RegisterCommand("same.id", "First", "First version", "Cat", action1);
            _sut.RegisterCommand("same.id", "Second", "Second version", "Cat", action2);

            var commands = _sut.GetAllCommands().ToList();

            // Assert - Should have only one command with updated properties
            Assert.AreEqual(1, commands.Count);
            Assert.AreEqual("Second", commands[0].Title);

            // Execute and verify second action is used
            _sut.ExecuteCommand("same.id");
            Assert.AreEqual(2, callCount);
        }

        #endregion

        #region GetAllCommands Tests

        [TestMethod]
        public void GetAllCommands_ReturnsAllRegisteredCommands()
        {
            // Arrange
            Action action = () => { };
            _sut.RegisterCommand("a", "A", "Desc A", "Cat", action);
            _sut.RegisterCommand("b", "B", "Desc B", "Cat", action);
            _sut.RegisterCommand("c", "C", "Desc C", "Cat", action);

            // Act
            var commands = _sut.GetAllCommands().ToList();

            // Assert
            Assert.AreEqual(3, commands.Count);
            Assert.IsTrue(commands.Any(c => c.CommandId == "a"));
            Assert.IsTrue(commands.Any(c => c.CommandId == "b"));
            Assert.IsTrue(commands.Any(c => c.CommandId == "c"));
        }

        [TestMethod]
        public void GetAllCommands_ReturnedItems_HaveCorrectProperties()
        {
            // Arrange
            Action action = () => { };
            _sut.RegisterCommand("edit.copy", "Copy", "Copy selection", "Edit", action, "Ctrl+C");

            // Act
            var command = _sut.GetAllCommands().First();

            // Assert
            Assert.AreEqual("edit.copy", command.CommandId);
            Assert.AreEqual("Copy", command.Title);
            Assert.AreEqual("Copy selection", command.Description);
            Assert.AreEqual("Edit", command.Category);
            Assert.AreEqual("Ctrl+C", command.Shortcut);
        }

        #endregion

        #region ExecuteCommand Tests

        [TestMethod]
        public void ExecuteCommand_WithValidId_InvokesAction()
        {
            // Arrange
            bool executed = false;
            Action action = () => executed = true;
            _sut.RegisterCommand("exec.test", "Test", "Test", "Test", action);

            // Act
            _sut.ExecuteCommand("exec.test");

            // Assert
            Assert.IsTrue(executed);
        }

        [TestMethod]
        public void ExecuteCommand_WithInvalidId_DoesNotThrow()
        {
            // Act - should not throw
            _sut.ExecuteCommand("nonexistent.command");

            // Assert - no exception
            Assert.IsTrue(true);
        }

        [TestMethod]
        public void ExecuteCommand_MultipleTimes_InvokesActionEachTime()
        {
            // Arrange
            int count = 0;
            Action action = () => count++;
            _sut.RegisterCommand("counter", "Counter", "Count", "Test", action);

            // Act
            _sut.ExecuteCommand("counter");
            _sut.ExecuteCommand("counter");
            _sut.ExecuteCommand("counter");

            // Assert
            Assert.AreEqual(3, count);
        }

        [TestMethod]
        public void ExecuteCommand_ActionThrows_ExceptionPropagates()
        {
            // Arrange
            Action action = () => throw new InvalidOperationException("Test exception");
            _sut.RegisterCommand("throwing", "Throwing", "Throws", "Test", action);

            // Act & Assert
            Assert.ThrowsException<InvalidOperationException>(() => _sut.ExecuteCommand("throwing"));
        }

        [TestMethod]
        public void ExecuteCommand_AfterReregistration_ExecutesNewAction()
        {
            // Arrange
            string result = "";
            Action action1 = () => result = "first";
            Action action2 = () => result = "second";

            _sut.RegisterCommand("dynamic", "Dynamic", "Dynamic", "Test", action1);
            _sut.ExecuteCommand("dynamic");
            Assert.AreEqual("first", result);

            // Act
            _sut.RegisterCommand("dynamic", "Dynamic", "Dynamic", "Test", action2);
            _sut.ExecuteCommand("dynamic");

            // Assert
            Assert.AreEqual("second", result);
        }

        #endregion

        #region Category Tests

        [TestMethod]
        public void RegisterCommand_DifferentCategories_ArePreserved()
        {
            // Arrange
            Action action = () => { };
            _sut.RegisterCommand("file.open", "Open", "Open file", "File", action);
            _sut.RegisterCommand("edit.cut", "Cut", "Cut selection", "Edit", action);
            _sut.RegisterCommand("view.zoom", "Zoom", "Zoom view", "View", action);

            // Act
            var commands = _sut.GetAllCommands().ToList();
            var categories = commands.Select(c => c.Category).Distinct().ToList();

            // Assert
            Assert.AreEqual(3, categories.Count);
            Assert.IsTrue(categories.Contains("File"));
            Assert.IsTrue(categories.Contains("Edit"));
            Assert.IsTrue(categories.Contains("View"));
        }

        [TestMethod]
        public void RegisterCommand_SameCategory_CanHaveMultipleCommands()
        {
            // Arrange
            Action action = () => { };
            _sut.RegisterCommand("edit.cut", "Cut", "Cut", "Edit", action);
            _sut.RegisterCommand("edit.copy", "Copy", "Copy", "Edit", action);
            _sut.RegisterCommand("edit.paste", "Paste", "Paste", "Edit", action);

            // Act
            var editCommands = _sut.GetAllCommands().Where(c => c.Category == "Edit").ToList();

            // Assert
            Assert.AreEqual(3, editCommands.Count);
        }

        #endregion

        #region Edge Cases

        [TestMethod]
        public void RegisterCommand_EmptyStrings_AreAllowed()
        {
            // Arrange
            Action action = () => { };

            // Act
            _sut.RegisterCommand("", "", "", "", action);

            // Assert
            var commands = _sut.GetAllCommands().ToList();
            Assert.AreEqual(1, commands.Count);
            Assert.AreEqual("", commands[0].CommandId);
        }

        [TestMethod]
        public void ExecuteCommand_EmptyId_ExecutesIfRegistered()
        {
            // Arrange
            bool executed = false;
            Action action = () => executed = true;
            _sut.RegisterCommand("", "", "", "", action);

            // Act
            _sut.ExecuteCommand("");

            // Assert
            Assert.IsTrue(executed);
        }

        #endregion
    }
}
