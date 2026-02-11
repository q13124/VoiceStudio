// Phase 5.0: Service Unification
// Task 5.0.2: Unified Theme Service Interface
// This interface unifies ThemeManager and Features/Theming/ThemeService

using System;
using System.Collections.Generic;
using System.Threading.Tasks;
using Microsoft.UI.Xaml;

namespace VoiceStudio.App.Services;

/// <summary>
/// Application theme enumeration.
/// </summary>
public enum AppTheme
{
    System,
    Light,
    Dark,
    HighContrast,
    Custom
}

/// <summary>
/// Layout density options.
/// </summary>
public enum LayoutDensity
{
    Compact,
    Normal,
    Comfortable,
    Touch
}

/// <summary>
/// Theme accent color definition.
/// </summary>
public class ThemeAccent
{
    public string Name { get; set; } = string.Empty;
    public Windows.UI.Color Primary { get; set; }
    public Windows.UI.Color Secondary { get; set; }
    public Windows.UI.Color Tertiary { get; set; }
}

/// <summary>
/// Theme changed event arguments.
/// </summary>
public class ThemeChangedEventArgs : EventArgs
{
    public AppTheme Theme { get; set; }
    public string ThemeName { get; set; } = string.Empty;
    public ElementTheme EffectiveTheme { get; set; }
}

/// <summary>
/// Unified theme service interface that combines theme switching,
/// density control, and custom themes.
/// </summary>
public interface IUnifiedThemeService
{
    #region Properties

    /// <summary>
    /// Gets the current theme.
    /// </summary>
    AppTheme CurrentTheme { get; }

    /// <summary>
    /// Gets the current theme name (e.g., "SciFi", "Default").
    /// </summary>
    string CurrentThemeName { get; }

    /// <summary>
    /// Gets the current layout density.
    /// </summary>
    LayoutDensity CurrentDensity { get; }

    /// <summary>
    /// Gets the current accent color.
    /// </summary>
    ThemeAccent CurrentAccent { get; }

    /// <summary>
    /// Gets whether dark mode is currently active.
    /// </summary>
    bool IsDarkMode { get; }

    /// <summary>
    /// Gets the effective element theme.
    /// </summary>
    ElementTheme EffectiveTheme { get; }

    #endregion

    #region Theme Operations

    /// <summary>
    /// Initializes the theme service with the root element.
    /// </summary>
    Task InitializeAsync(FrameworkElement rootElement);

    /// <summary>
    /// Sets the application theme by name.
    /// </summary>
    void ApplyTheme(string themeName);

    /// <summary>
    /// Sets the application theme by enum.
    /// </summary>
    void SetTheme(AppTheme theme);

    /// <summary>
    /// Toggles between light and dark mode.
    /// </summary>
    void ToggleDarkMode();

    /// <summary>
    /// Sets the layout density.
    /// </summary>
    void SetDensity(LayoutDensity density);

    /// <summary>
    /// Sets the accent color.
    /// </summary>
    void SetAccent(ThemeAccent accent);

    /// <summary>
    /// Gets available theme names.
    /// </summary>
    IReadOnlyList<string> GetAvailableThemes();

    /// <summary>
    /// Gets predefined accent colors.
    /// </summary>
    IReadOnlyList<ThemeAccent> GetPredefinedAccents();

    #endregion

    #region Events

    /// <summary>
    /// Event raised when theme changes.
    /// </summary>
    event EventHandler<ThemeChangedEventArgs>? ThemeChanged;

    #endregion
}
