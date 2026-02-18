using Microsoft.VisualStudio.TestTools.UnitTesting;
using Moq;
using {{CLASS_NAME}}Plugin;
using VoiceStudio.Core.Panels;
using VoiceStudio.Core.Services;

namespace {{CLASS_NAME}}Plugin.Tests;

[TestClass]
public class PluginTests
{
    [TestMethod]
    public void Plugin_Name_ReturnsCorrectName()
    {
        // Arrange
        var plugin = new Plugin();

        // Act
        var name = plugin.Name;

        // Assert
        Assert.AreEqual("{{PLUGIN_NAME}}", name);
    }

    [TestMethod]
    public void Plugin_Version_ReturnsCorrectVersion()
    {
        // Arrange
        var plugin = new Plugin();

        // Act
        var version = plugin.Version;

        // Assert
        Assert.AreEqual("{{VERSION}}", version);
    }

    [TestMethod]
    public void Plugin_Author_ReturnsCorrectAuthor()
    {
        // Arrange
        var plugin = new Plugin();

        // Act
        var author = plugin.Author;

        // Assert
        Assert.AreEqual("{{AUTHOR}}", author);
    }

    [TestMethod]
    public void Plugin_RegisterPanels_RegistersSettingsPanel()
    {
        // Arrange
        var plugin = new Plugin();
        var mockRegistry = new Mock<IPanelRegistry>();

        // Act
        plugin.RegisterPanels(mockRegistry.Object);

        // Assert
        mockRegistry.Verify(r => r.Register(It.IsAny<PanelDescriptor>()), Times.Once);
    }

    [TestMethod]
    public void Plugin_Initialize_SetsInitializedFlag()
    {
        // Arrange
        var plugin = new Plugin();
        var mockBackend = new Mock<IBackendClient>();

        // Act
        plugin.Initialize(mockBackend.Object);

        // Assert
        Assert.IsTrue(plugin.IsInitialized);
    }

    [TestMethod]
    public void Plugin_Cleanup_ClearsInitializedFlag()
    {
        // Arrange
        var plugin = new Plugin();
        var mockBackend = new Mock<IBackendClient>();
        plugin.Initialize(mockBackend.Object);

        // Act
        plugin.Cleanup();

        // Assert
        Assert.IsFalse(plugin.IsInitialized);
    }

    [TestMethod]
    public void SettingsPanelViewModel_Message_BindsCorrectly()
    {
        // Arrange
        var viewModel = new SettingsPanelViewModel();

        // Act
        viewModel.Message = "Test Message";

        // Assert
        Assert.AreEqual("Test Message", viewModel.Message);
    }

    [TestMethod]
    public void SettingsPanelViewModel_Message_RaisesPropertyChanged()
    {
        // Arrange
        var viewModel = new SettingsPanelViewModel();
        var propertyChangedRaised = false;

        viewModel.PropertyChanged += (s, e) =>
        {
            if (e.PropertyName == nameof(SettingsPanelViewModel.Message))
            {
                propertyChangedRaised = true;
            }
        };

        // Act
        viewModel.Message = "New Message";

        // Assert
        Assert.IsTrue(propertyChangedRaised);
    }
}
