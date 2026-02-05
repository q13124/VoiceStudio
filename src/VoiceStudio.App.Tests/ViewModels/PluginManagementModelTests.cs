using Microsoft.VisualStudio.TestTools.UnitTesting;
using VoiceStudio.App.ViewModels;

namespace VoiceStudio.App.Tests.ViewModels
{
    [TestClass]
    public class PluginManagementModelTests
    {
        #region PluginInfo Model Tests

        [TestMethod]
        public void PluginInfo_DefaultValues()
        {
            var plugin = new PluginInfo();

            Assert.AreEqual(string.Empty, plugin.Name);
            Assert.AreEqual(string.Empty, plugin.Version);
            Assert.AreEqual(string.Empty, plugin.Author);
            Assert.AreEqual(string.Empty, plugin.Description);
            Assert.IsTrue(plugin.IsEnabled);
            Assert.IsFalse(plugin.IsInitialized);
            Assert.IsNotNull(plugin.Status);
            Assert.IsNull(plugin.ErrorMessage);
        }

        [TestMethod]
        public void PluginInfo_PropertiesSetCorrectly()
        {
            var plugin = new PluginInfo
            {
                Name = "Audio Enhancer",
                Version = "2.0.0",
                Author = "VoiceStudio Team",
                Description = "Enhances audio quality",
                IsEnabled = true,
                IsInitialized = true,
                Status = "Active",
                ErrorMessage = null
            };

            Assert.AreEqual("Audio Enhancer", plugin.Name);
            Assert.AreEqual("2.0.0", plugin.Version);
            Assert.AreEqual("VoiceStudio Team", plugin.Author);
            Assert.AreEqual("Enhances audio quality", plugin.Description);
            Assert.IsTrue(plugin.IsEnabled);
            Assert.IsTrue(plugin.IsInitialized);
            Assert.AreEqual("Active", plugin.Status);
            Assert.IsNull(plugin.ErrorMessage);
        }

        [TestMethod]
        public void PluginInfo_CanBeDisabled()
        {
            var plugin = new PluginInfo { IsEnabled = false };
            Assert.IsFalse(plugin.IsEnabled);
        }

        [TestMethod]
        public void PluginInfo_CanHaveErrorMessage()
        {
            var plugin = new PluginInfo
            {
                IsEnabled = true,
                IsInitialized = false,
                Status = "Error",
                ErrorMessage = "Failed to load plugin assembly"
            };

            Assert.IsFalse(plugin.IsInitialized);
            Assert.AreEqual("Error", plugin.Status);
            Assert.AreEqual("Failed to load plugin assembly", plugin.ErrorMessage);
        }

        [TestMethod]
        public void PluginInfo_InitializedFlag()
        {
            var plugin = new PluginInfo { IsInitialized = false };
            Assert.IsFalse(plugin.IsInitialized);

            plugin.IsInitialized = true;
            Assert.IsTrue(plugin.IsInitialized);
        }

        #endregion
    }
}
