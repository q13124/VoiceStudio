using Microsoft.VisualStudio.TestTools.UnitTesting;
using Moq;
using VoiceStudio.App.Views.Panels;
using VoiceStudio.Core.Services;

namespace VoiceStudio.App.Tests.ViewModels
{
    [TestClass]
    public class MacroViewModelTests
    {
        private Mock<IViewModelContext> _mockContext = null!;
        private Mock<IBackendClient> _mockBackendClient = null!;
        private MacroViewModel _viewModel = null!;

        [TestInitialize]
        public void Setup()
        {
            _mockContext = new Mock<IViewModelContext>();
            _mockBackendClient = new Mock<IBackendClient>();
            _viewModel = new MacroViewModel(_mockContext.Object, _mockBackendClient.Object);
        }

        [TestMethod]
        public void Constructor_InitializesWithDefaultValues()
        {
            Assert.IsNotNull(_viewModel);
            Assert.AreEqual("macro", _viewModel.PanelId);
            Assert.AreEqual("Macros", _viewModel.DisplayName);
            Assert.IsFalse(_viewModel.IsLoading);
        }

        [TestMethod]
        public void Macros_InitializesAsEmptyCollection()
        {
            Assert.IsNotNull(_viewModel.Macros);
            Assert.AreEqual(0, _viewModel.Macros.Count);
        }

        [TestMethod]
        public void SelectedMacro_DefaultsToNull()
        {
            Assert.IsNull(_viewModel.SelectedMacro);
        }

        [TestMethod]
        public void ShowMacrosView_DefaultsToTrue()
        {
            Assert.IsTrue(_viewModel.ShowMacrosView);
        }

        [TestMethod]
        public void AutomationCurves_InitializesAsEmptyCollection()
        {
            Assert.IsNotNull(_viewModel.AutomationCurves);
            Assert.AreEqual(0, _viewModel.AutomationCurves.Count);
        }

        [TestMethod]
        public void SelectedMacroCount_DefaultsToZero()
        {
            Assert.AreEqual(0, _viewModel.SelectedMacroCount);
        }

        [TestMethod]
        public void HasMultipleMacroSelection_DefaultsToFalse()
        {
            Assert.IsFalse(_viewModel.HasMultipleMacroSelection);
        }
    }
}
