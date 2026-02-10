using Microsoft.VisualStudio.TestTools.UnitTesting;
using Moq;
using System;
using System.Collections.Generic;
using VoiceStudio.App.Services;
using VoiceStudio.App.Tests.Fixtures;
using VoiceStudio.App.ViewModels;
using VoiceStudio.App.Core.Commands;
using CommandExecutedEventArgs = VoiceStudio.App.ViewModels.CommandExecutedEventArgs;
using VoiceStudio.Core.Panels;
using VoiceStudio.Core.Services;

namespace VoiceStudio.App.Tests.ViewModels
{
  /// <summary>
  /// Unit tests for CommandPaletteViewModel.
  /// Tests initialization, filtering, command execution, and property changes.
  /// </summary>
  [TestClass]
  public class CommandPaletteViewModelTests : ViewModelTestBase
  {
    private Mock<IPanelRegistry>? _mockPanelRegistry;
    private Mock<IUnifiedCommandRegistry>? _mockCommandRegistry;
    private CommandPaletteViewModel? _viewModel;

    [TestInitialize]
    public override void TestInitialize()
    {
      base.TestInitialize();
      TestAppServicesHelper.EnsureInitialized();
      _mockPanelRegistry = new Mock<IPanelRegistry>();
      _mockCommandRegistry = new Mock<IUnifiedCommandRegistry>();
    }

    [TestCleanup]
    public override void TestCleanup()
    {
      _viewModel = null;
      _mockPanelRegistry = null;
      _mockCommandRegistry = null;
      base.TestCleanup();
    }

    private CommandPaletteViewModel CreateViewModel(bool withCommandRegistry = false)
    {
      _mockPanelRegistry!.Setup(x => x.GetPanelsForRegion(It.IsAny<PanelRegion>()))
          .Returns(Array.Empty<IPanelView>());

      if (withCommandRegistry)
      {
        _mockCommandRegistry!.Setup(x => x.GetAllCommands())
            .Returns(new List<CommandDescriptor>());
        return new CommandPaletteViewModel(_mockPanelRegistry.Object, _mockCommandRegistry.Object);
      }

      return new CommandPaletteViewModel(_mockPanelRegistry.Object, null);
    }

    #region Initialization Tests

    [TestMethod]
    public void Constructor_WithValidDependencies_CreatesInstance()
    {
      // Arrange & Act
      _viewModel = CreateViewModel();

      // Assert
      Assert.IsNotNull(_viewModel);
      Assert.IsNotNull(_viewModel.Items);
      Assert.IsNotNull(_viewModel.FilteredItems);
      Assert.IsNotNull(_viewModel.RunSelectedCmd);
      Assert.IsNotNull(_viewModel.RunByIdCmd);
    }

    [TestMethod]
    public void Constructor_LoadsDefaultItems_IncludingThemeAndHelp()
    {
      // Arrange & Act
      _viewModel = CreateViewModel();

      // Assert - LoadDefaultItems adds theme:, density:, help: items
      Assert.IsTrue(_viewModel!.Items.Count > 0);
      var hasTheme = false;
      var hasHelp = false;
      foreach (var item in _viewModel.Items)
      {
        if (item.Id.StartsWith("theme:", StringComparison.Ordinal)) hasTheme = true;
        if (item.Id.StartsWith("help:", StringComparison.Ordinal)) hasHelp = true;
      }
      Assert.IsTrue(hasTheme, "Should contain theme commands");
      Assert.IsTrue(hasHelp, "Should contain help command");
    }

    [TestMethod]
    public void Constructor_ApplyFilter_SetsFilteredItemsAndSelectedItem()
    {
      // Arrange & Act
      _viewModel = CreateViewModel();

      // Assert
      Assert.IsTrue(_viewModel!.FilteredItems.Count > 0);
      Assert.IsNotNull(_viewModel.SelectedItem);
      Assert.AreEqual(_viewModel.FilteredItems[0], _viewModel.SelectedItem);
    }

    #endregion

    #region Property Tests

    [TestMethod]
    public void FilterText_WhenSet_RaisesPropertyChanged()
    {
      // Arrange
      _viewModel = CreateViewModel();
      var propertyChanged = false;
      _viewModel.PropertyChanged += (_, e) =>
      {
        if (e.PropertyName == nameof(CommandPaletteViewModel.FilterText))
          propertyChanged = true;
      };

      // Act
      _viewModel.FilterText = "theme";

      // Assert
      Assert.IsTrue(propertyChanged);
      Assert.AreEqual("theme", _viewModel.FilterText);
    }

    [TestMethod]
    public void FilterText_WhenSet_AppliesFilterToFilteredItems()
    {
      // Arrange
      _viewModel = CreateViewModel();

      // Act
      _viewModel.FilterText = "theme";

      // Assert - Filtered items should match filter
      foreach (var item in _viewModel!.FilteredItems)
      {
        Assert.IsTrue(
            (item.Title ?? "").Contains("theme", StringComparison.OrdinalIgnoreCase),
            $"Filtered item '{item.Title}' should contain 'theme'");
      }
    }

    [TestMethod]
    public void FilterText_Empty_ShowsAllItems()
    {
      // Arrange
      _viewModel = CreateViewModel();
      var itemCount = _viewModel!.Items.Count;

      // Act
      _viewModel.FilterText = "";
      _viewModel.FilterText = "  "; // Trim to empty

      // Assert
      Assert.AreEqual(itemCount, _viewModel.FilteredItems.Count);
    }

    #endregion

    #region Command Execution Tests

    [TestMethod]
    public void RunByIdCmd_WithThemeCommand_RaisesCommandExecuted()
    {
      // Arrange
      _viewModel = CreateViewModel();
      CommandExecutedEventArgs? capturedArgs = null;
      _viewModel!.CommandExecuted += (_, e) => capturedArgs = e;

      // Act
      _viewModel.RunByIdCmd.Execute("theme:Dark");

      // Assert
      Assert.IsNotNull(capturedArgs);
      Assert.AreEqual("theme", capturedArgs.Action);
      Assert.AreEqual("Dark", capturedArgs.Value);
      Assert.AreEqual("theme:Dark", capturedArgs.CommandId);
    }

    [TestMethod]
    public void RunByIdCmd_WithHelpCommand_RaisesCommandExecuted()
    {
      // Arrange
      _viewModel = CreateViewModel();
      CommandExecutedEventArgs? capturedArgs = null;
      _viewModel!.CommandExecuted += (_, e) => capturedArgs = e;

      // Act
      _viewModel.RunByIdCmd.Execute("help:keymap");

      // Assert
      Assert.IsNotNull(capturedArgs);
      Assert.AreEqual("help", capturedArgs.Action);
      Assert.AreEqual("keymap", capturedArgs.Value);
    }

    [TestMethod]
    public void RunByIdCmd_WithNullOrEmpty_DoesNotRaiseEvent()
    {
      // Arrange
      _viewModel = CreateViewModel();
      var raised = false;
      _viewModel!.CommandExecuted += (_, _) => raised = true;

      // Act
      _viewModel.RunByIdCmd.Execute(null);
      _viewModel.RunByIdCmd.Execute("");

      // Assert
      Assert.IsFalse(raised);
    }

    [TestMethod]
    public void RunByIdCmd_WithInvalidFormat_DoesNotRaiseEvent()
    {
      // Arrange
      _viewModel = CreateViewModel();
      var raised = false;
      _viewModel!.CommandExecuted += (_, _) => raised = true;

      // Act - ID without colon (invalid format)
      _viewModel.RunByIdCmd.Execute("invalidformat");

      // Assert
      Assert.IsFalse(raised);
    }

    [TestMethod]
    public void RunSelectedCmd_WithSelectedItem_RaisesCommandExecuted()
    {
      // Arrange
      _viewModel = CreateViewModel();
      CommandExecutedEventArgs? capturedArgs = null;
      _viewModel!.CommandExecuted += (_, e) => capturedArgs = e;
      _viewModel.SelectedItem = _viewModel.Items[0]; // First item (e.g., "open:..." or "help:keymap")

      // Act
      _viewModel.RunSelectedCmd.Execute(null);

      // Assert
      Assert.IsNotNull(capturedArgs);
      Assert.IsNotNull(capturedArgs.CommandId);
    }

    [TestMethod]
    public void RunSelectedCmd_WithNullSelectedItem_DoesNotRaiseEvent()
    {
      // Arrange
      _viewModel = CreateViewModel();
      var raised = false;
      _viewModel!.CommandExecuted += (_, _) => raised = true;
      _viewModel.SelectedItem = null;

      // Act
      _viewModel.RunSelectedCmd.Execute(null);

      // Assert
      Assert.IsFalse(raised);
    }

    #endregion
  }
}
