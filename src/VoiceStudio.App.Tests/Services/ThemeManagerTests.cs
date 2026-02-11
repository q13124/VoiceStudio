using Microsoft.VisualStudio.TestTools.UnitTesting;
using System.Linq;
using System.Threading.Tasks;
using VoiceStudio.App.Services;

namespace VoiceStudio.App.Tests.Services;

/// <summary>
/// Unit tests for ThemeManager.
/// Tests theme switching, accent persistence, and density settings.
/// </summary>
[TestClass]
public class ThemeManagerTests : TestBase
{
    private ThemeManager? _themeManager;

    [TestInitialize]
    public override void TestInitialize()
    {
        base.TestInitialize();
        _themeManager = new ThemeManager();
    }

    [TestCleanup]
    public override void TestCleanup()
    {
        _themeManager = null;
        base.TestCleanup();
    }

    [TestMethod]
    public void ThemeManager_InitializesWithDefaultValues()
    {
        // Assert
        Assert.IsNotNull(_themeManager);
        Assert.AreEqual("SciFi", _themeManager.CurrentThemeName);
        Assert.AreEqual("Compact", _themeManager.Density);
        Assert.AreEqual(AppTheme.Dark, _themeManager.CurrentTheme);
        Assert.IsNotNull(_themeManager.CurrentAccent);
        Assert.AreEqual("Blue", _themeManager.CurrentAccent.Name);
    }

    [TestMethod]
    public void ThemeManager_GetAvailableThemes_ReturnsThemes()
    {
        // Act
        var themes = _themeManager!.GetAvailableThemes();

        // Assert
        Assert.IsNotNull(themes);
        Assert.IsTrue(themes.Count > 0);
        Assert.IsTrue(themes.Contains("SciFi"));
        Assert.IsTrue(themes.Contains("Dark"));
        Assert.IsTrue(themes.Contains("Light"));
        Assert.IsTrue(themes.Contains("HighContrast"));
    }

    [TestMethod]
    public void ThemeManager_GetPredefinedAccents_ReturnsAccents()
    {
        // Act
        var accents = _themeManager!.GetPredefinedAccents();

        // Assert
        Assert.IsNotNull(accents);
        Assert.IsTrue(accents.Count >= 8);
        Assert.IsTrue(accents.Any(a => a.Name == "Blue"));
        Assert.IsTrue(accents.Any(a => a.Name == "Purple"));
        Assert.IsTrue(accents.Any(a => a.Name == "Green"));
    }

    [TestMethod]
    public void ThemeManager_SetTheme_UpdatesCurrentTheme()
    {
        // Act
        _themeManager!.SetTheme(AppTheme.Light);

        // Assert
        Assert.AreEqual(AppTheme.Light, _themeManager.CurrentTheme);
        Assert.IsFalse(_themeManager.IsDarkMode);
    }

    [TestMethod]
    public void ThemeManager_SetDensity_UpdatesCurrentDensity()
    {
        // Act
        _themeManager!.SetDensity(LayoutDensity.Comfortable);

        // Assert
        Assert.AreEqual(LayoutDensity.Comfortable, _themeManager.CurrentDensity);
    }

    [TestMethod]
    public void ThemeManager_SetAccent_UpdatesCurrentAccent()
    {
        // Arrange
        var accents = _themeManager!.GetPredefinedAccents();
        var greenAccent = accents.FirstOrDefault(a => a.Name == "Green");
        Assert.IsNotNull(greenAccent);

        // Act
        _themeManager.SetAccent(greenAccent);

        // Assert
        Assert.AreEqual("Green", _themeManager.CurrentAccent.Name);
    }

    [TestMethod]
    public void ThemeManager_ToggleDarkMode_SwitchesTheme()
    {
        // Ensure we start in dark mode
        _themeManager!.SetTheme(AppTheme.Dark);
        Assert.IsTrue(_themeManager.IsDarkMode);

        // Act
        _themeManager.ToggleDarkMode();

        // Assert
        Assert.IsFalse(_themeManager.IsDarkMode);
        Assert.AreEqual(AppTheme.Light, _themeManager.CurrentTheme);

        // Act again
        _themeManager.ToggleDarkMode();

        // Assert
        Assert.IsTrue(_themeManager.IsDarkMode);
    }

    [TestMethod]
    public void ThemeManager_IsDarkMode_ReturnsCorrectValue()
    {
        // Assert default is dark
        Assert.IsTrue(_themeManager!.IsDarkMode);

        // SciFi should be dark
        _themeManager.ApplyTheme("SciFi");
        Assert.IsTrue(_themeManager.IsDarkMode);

        // Dark should be dark
        _themeManager.ApplyTheme("Dark");
        Assert.IsTrue(_themeManager.IsDarkMode);

        // Light should not be dark
        _themeManager.ApplyTheme("Light");
        Assert.IsFalse(_themeManager.IsDarkMode);
    }

    [TestMethod]
    public void ThemeManager_ThemeChanged_EventFires()
    {
        // Arrange
        var eventFired = false;
        ThemeChangedEventArgs? eventArgs = null;
        _themeManager!.ThemeChanged += (sender, args) =>
        {
            eventFired = true;
            eventArgs = args;
        };

        // Act
        _themeManager.SetTheme(AppTheme.Light);

        // Assert
        Assert.IsTrue(eventFired);
        Assert.IsNotNull(eventArgs);
        Assert.AreEqual(AppTheme.Light, eventArgs.Theme);
    }

    [TestMethod]
    public void ThemeManager_EffectiveTheme_ReturnsCorrectElementTheme()
    {
        // Dark theme
        _themeManager!.ApplyTheme("Dark");
        Assert.AreEqual(Microsoft.UI.Xaml.ElementTheme.Dark, _themeManager.EffectiveTheme);

        // Light theme
        _themeManager.ApplyTheme("Light");
        Assert.AreEqual(Microsoft.UI.Xaml.ElementTheme.Light, _themeManager.EffectiveTheme);
    }

    [TestMethod]
    public void ThemeManager_SetAccent_FiresThemeChangedEvent()
    {
        // Arrange
        var eventFired = false;
        _themeManager!.ThemeChanged += (_, _) => eventFired = true;

        var accents = _themeManager.GetPredefinedAccents();
        var purpleAccent = accents.FirstOrDefault(a => a.Name == "Purple");
        Assert.IsNotNull(purpleAccent);

        // Act
        _themeManager.SetAccent(purpleAccent);

        // Assert
        Assert.IsTrue(eventFired);
    }
}
