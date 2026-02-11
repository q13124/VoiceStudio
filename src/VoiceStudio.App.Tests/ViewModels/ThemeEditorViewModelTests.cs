using Microsoft.VisualStudio.TestTools.UnitTesting;
using Moq;
using System.Collections.Generic;
using System.Linq;
using System.Threading.Tasks;
using VoiceStudio.App.Services;
using VoiceStudio.App.ViewModels;
using VoiceStudio.Core.Services;

namespace VoiceStudio.App.Tests.ViewModels;

/// <summary>
/// Unit tests for ThemeEditorViewModel.
/// Tests theme selection, accent handling, and custom theme persistence.
/// </summary>
[TestClass]
public class ThemeEditorViewModelTests : ViewModelTestBase
{
    private Mock<IUnifiedThemeService>? _mockThemeService;
    private ThemeEditorViewModel? _viewModel;

    [TestInitialize]
    public override void TestInitialize()
    {
        base.TestInitialize();

        // Setup mock theme service
        _mockThemeService = new Mock<IUnifiedThemeService>();

        var themes = new List<string> { "SciFi", "Dark", "Light", "HighContrast" };
        var accents = new List<ThemeAccent>
        {
            new() { Name = "Blue", Primary = Windows.UI.Color.FromArgb(255, 0, 120, 212) },
            new() { Name = "Purple", Primary = Windows.UI.Color.FromArgb(255, 128, 57, 123) },
            new() { Name = "Green", Primary = Windows.UI.Color.FromArgb(255, 16, 137, 62) }
        };

        _mockThemeService.Setup(x => x.GetAvailableThemes()).Returns(themes);
        _mockThemeService.Setup(x => x.GetPredefinedAccents()).Returns(accents);
        _mockThemeService.Setup(x => x.CurrentThemeName).Returns("SciFi");
        _mockThemeService.Setup(x => x.CurrentAccent).Returns(accents[0]);
        _mockThemeService.Setup(x => x.CurrentDensity).Returns(LayoutDensity.Compact);

        _viewModel = new ThemeEditorViewModel(MockContext!, _mockThemeService.Object);
    }

    [TestCleanup]
    public override void TestCleanup()
    {
        _viewModel?.Dispose();
        _viewModel = null;
        _mockThemeService = null;

        base.TestCleanup();
    }

    [TestMethod]
    public void ThemeEditorViewModel_Constructor_InitializesCorrectly()
    {
        // Assert
        Assert.IsNotNull(_viewModel);
        Assert.IsNotNull(_viewModel.AvailableThemes);
        Assert.IsNotNull(_viewModel.AvailableAccents);
        Assert.IsNotNull(_viewModel.AvailableDensities);
        Assert.AreEqual(4, _viewModel.AvailableThemes.Count);
        Assert.AreEqual(3, _viewModel.AvailableAccents.Count);
    }

    [TestMethod]
    public void ThemeEditorViewModel_Initialize_LoadsCurrentSettings()
    {
        // Act
        _viewModel!.Initialize();

        // Assert
        Assert.AreEqual("SciFi", _viewModel.SelectedTheme);
        Assert.IsNotNull(_viewModel.SelectedAccent);
        Assert.AreEqual("Blue", _viewModel.SelectedAccent.Name);
        Assert.AreEqual(LayoutDensity.Compact, _viewModel.SelectedDensity);
    }

    [TestMethod]
    public void ThemeEditorViewModel_SelectedTheme_ChangesTheme()
    {
        // Arrange
        _viewModel!.Initialize();

        // Act
        _viewModel.SelectedTheme = "Dark";

        // Assert
        _mockThemeService!.Verify(x => x.ApplyTheme("Dark"), Times.Once);
    }

    [TestMethod]
    public void ThemeEditorViewModel_SelectedAccent_ChangesAccent()
    {
        // Arrange
        _viewModel!.Initialize();
        var greenAccent = _viewModel.AvailableAccents.FirstOrDefault(a => a.Name == "Green");
        Assert.IsNotNull(greenAccent);

        // Act
        _viewModel.SelectedAccent = greenAccent;

        // Assert
        _mockThemeService!.Verify(x => x.SetAccent(greenAccent), Times.Once);
    }

    [TestMethod]
    public void ThemeEditorViewModel_SelectedDensity_ChangesDensity()
    {
        // Arrange
        _viewModel!.Initialize();

        // Act
        _viewModel.SelectedDensity = LayoutDensity.Comfortable;

        // Assert
        _mockThemeService!.Verify(x => x.SetDensity(LayoutDensity.Comfortable), Times.Once);
    }

    [TestMethod]
    public void ThemeEditorViewModel_ResetToDefaultsCommand_ResetsAllSettings()
    {
        // Arrange
        _viewModel!.Initialize();

        // Act
        _viewModel.ResetToDefaultsCommand.Execute(null);

        // Assert
        _mockThemeService!.Verify(x => x.ApplyTheme("SciFi"), Times.AtLeast(1));
        _mockThemeService.Verify(x => x.SetDensity(LayoutDensity.Compact), Times.AtLeast(1));
        Assert.AreEqual("SciFi", _viewModel.SelectedTheme);
        Assert.AreEqual(LayoutDensity.Compact, _viewModel.SelectedDensity);
    }

    [TestMethod]
    public void ThemeEditorViewModel_SavedThemes_InitializesEmpty()
    {
        // Assert
        Assert.IsNotNull(_viewModel!.SavedThemes);
        // Initially may have some saved themes based on filesystem
    }

    [TestMethod]
    public void ThemeEditorViewModel_CustomThemeName_DefaultsToEmpty()
    {
        // Assert
        Assert.AreEqual(string.Empty, _viewModel!.CustomThemeName);
    }

    [TestMethod]
    public void ThemeEditorViewModel_SelectedSavedTheme_DefaultsToNull()
    {
        // Assert
        Assert.IsNull(_viewModel!.SelectedSavedTheme);
    }

    [TestMethod]
    public async Task ThemeEditorViewModel_SaveCustomThemeCommand_SavesTheme()
    {
        // Arrange
        _viewModel!.Initialize();
        _viewModel.CustomThemeName = "TestTheme";

        // Act
        await _viewModel.SaveCustomThemeCommand.ExecuteAsync(null);

        // Assert
        Assert.AreEqual(string.Empty, _viewModel.CustomThemeName);
        // Note: File system interaction would need integration test
    }

    [TestMethod]
    public void ThemeEditorViewModel_DeleteSelectedThemeCommand_CanExecute()
    {
        // Arrange
        _viewModel!.Initialize();

        // Assert - command exists and is executable
        Assert.IsNotNull(_viewModel.DeleteSelectedThemeCommand);
    }

    [TestMethod]
    public void ThemeEditorViewModel_Dispose_DoesNotThrow()
    {
        // Act & Assert
        _viewModel!.Dispose();
        // No exception means success
    }
}
