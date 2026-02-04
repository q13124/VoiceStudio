using Microsoft.VisualStudio.TestTools.UnitTesting;
using Moq;
using VoiceStudio.App.Services;
using VoiceStudio.App.ViewModels;
using VoiceStudio.Core.Services;

namespace VoiceStudio.App.Tests.ViewModels
{
    [TestClass]
    public class SettingsViewModelTests
    {
        private Mock<IViewModelContext> _mockContext = null!;
        private Mock<ISettingsService> _mockSettingsService = null!;
        private Mock<IBackendClient> _mockBackendClient = null!;
        private SettingsViewModel _viewModel = null!;

        [TestInitialize]
        public void Setup()
        {
            _mockContext = new Mock<IViewModelContext>();
            _mockSettingsService = new Mock<ISettingsService>();
            _mockBackendClient = new Mock<IBackendClient>();
            _viewModel = new SettingsViewModel(
                _mockContext.Object,
                _mockSettingsService.Object,
                _mockBackendClient.Object);
        }

        [TestMethod]
        public void Constructor_InitializesWithDefaultValues()
        {
            Assert.IsNotNull(_viewModel);
            Assert.AreEqual("settings", _viewModel.PanelId);
            Assert.AreEqual("Settings", _viewModel.DisplayName);
        }

        [TestMethod]
        public void Theme_DefaultsToDark()
        {
            Assert.AreEqual("Dark", _viewModel.Theme);
        }

        [TestMethod]
        public void Language_DefaultsToEnUS()
        {
            Assert.AreEqual("en-US", _viewModel.Language);
        }

        [TestMethod]
        public void AutoSave_DefaultsToTrue()
        {
            Assert.IsTrue(_viewModel.AutoSave);
        }

        [TestMethod]
        public void AutoSaveInterval_DefaultsTo300()
        {
            Assert.AreEqual(300, _viewModel.AutoSaveInterval);
        }

        [TestMethod]
        public void DefaultAudioEngine_DefaultsToXtts()
        {
            Assert.AreEqual("xtts", _viewModel.DefaultAudioEngine);
        }

        [TestMethod]
        public void QualityLevel_DefaultsTo5()
        {
            Assert.AreEqual(5, _viewModel.QualityLevel);
        }

        [TestMethod]
        public void SampleRate_DefaultsTo44100()
        {
            Assert.AreEqual(44100, _viewModel.SampleRate);
        }

        [TestMethod]
        public void ApiUrl_DefaultsToLocalhost8001()
        {
            Assert.AreEqual("http://localhost:8001", _viewModel.ApiUrl);
        }

        [TestMethod]
        public void SnapEnabled_DefaultsToTrue()
        {
            Assert.IsTrue(_viewModel.SnapEnabled);
        }

        [TestMethod]
        public void CachingEnabled_DefaultsToTrue()
        {
            Assert.IsTrue(_viewModel.CachingEnabled);
        }
    }
}
