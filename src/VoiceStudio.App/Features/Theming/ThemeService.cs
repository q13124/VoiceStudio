// Phase 5.5: Theme System
// Task 5.5.1-5.5.5: Comprehensive theming with dark mode
//
// DEPRECATED (Phase 5.0): This class is deprecated.
// Use VoiceStudio.App.Services.ThemeManager which implements IUnifiedThemeService.
// This file is kept for reference and will be removed in a future version.

using System;
using System.Collections.Generic;
using System.Threading.Tasks;
using Microsoft.UI.Xaml;
using Windows.Storage;

namespace VoiceStudio.App.Features.Theming;

/// <summary>
/// Available themes.
/// </summary>
public enum AppTheme
{
    System,
    Light,
    Dark,
    HighContrast,
    Custom,
}

/// <summary>
/// Theme accent colors.
/// </summary>
public class ThemeAccent
{
    public string Name { get; set; } = "";
    public Windows.UI.Color Primary { get; set; }
    public Windows.UI.Color Secondary { get; set; }
    public Windows.UI.Color Tertiary { get; set; }
}

/// <summary>
/// Custom theme definition.
/// </summary>
public class CustomTheme
{
    public string Id { get; set; } = Guid.NewGuid().ToString();
    public string Name { get; set; } = "";
    public bool IsDark { get; set; }
    
    // Background colors
    public Windows.UI.Color BackgroundPrimary { get; set; }
    public Windows.UI.Color BackgroundSecondary { get; set; }
    public Windows.UI.Color BackgroundTertiary { get; set; }
    
    // Text colors
    public Windows.UI.Color TextPrimary { get; set; }
    public Windows.UI.Color TextSecondary { get; set; }
    public Windows.UI.Color TextDisabled { get; set; }
    
    // Accent colors
    public Windows.UI.Color AccentPrimary { get; set; }
    public Windows.UI.Color AccentSecondary { get; set; }
    
    // Border colors
    public Windows.UI.Color BorderDefault { get; set; }
    public Windows.UI.Color BorderFocused { get; set; }
    
    // Semantic colors
    public Windows.UI.Color Success { get; set; }
    public Windows.UI.Color Warning { get; set; }
    public Windows.UI.Color Error { get; set; }
    public Windows.UI.Color Info { get; set; }
}

/// <summary>
/// Theme changed event args.
/// </summary>
public class ThemeChangedEventArgs : EventArgs
{
    public AppTheme NewTheme { get; set; }
    public ElementTheme EffectiveTheme { get; set; }
    public CustomTheme? CustomTheme { get; set; }
}

/// <summary>
/// Service for managing application theming.
/// </summary>
public class ThemeService
{
    private AppTheme _currentTheme = AppTheme.System;
    private CustomTheme? _customTheme;
    private ThemeAccent _currentAccent;
    private readonly List<CustomTheme> _customThemes = new();
    private FrameworkElement? _rootElement;

    public event EventHandler<ThemeChangedEventArgs>? ThemeChanged;

    public AppTheme CurrentTheme => _currentTheme;
    public CustomTheme? CustomTheme => _customTheme;
    public ThemeAccent CurrentAccent => _currentAccent;
    public IReadOnlyList<CustomTheme> CustomThemes => _customThemes;

    public ThemeService()
    {
        // Default accent
        _currentAccent = new ThemeAccent
        {
            Name = "Blue",
            Primary = Windows.UI.Color.FromArgb(255, 0, 120, 212),
            Secondary = Windows.UI.Color.FromArgb(255, 0, 90, 158),
            Tertiary = Windows.UI.Color.FromArgb(255, 0, 62, 110),
        };
    }

    /// <summary>
    /// Initialize theme service.
    /// </summary>
    public async Task InitializeAsync(FrameworkElement rootElement)
    {
        _rootElement = rootElement;
        
        // Load saved theme preference
        await LoadThemePreferenceAsync();
        
        // Apply initial theme
        ApplyTheme(_currentTheme);
        
        // Listen for system theme changes
        var uiSettings = new Windows.UI.ViewManagement.UISettings();
        uiSettings.ColorValuesChanged += OnSystemThemeChanged;
    }

    /// <summary>
    /// Set the application theme.
    /// </summary>
    public void SetTheme(AppTheme theme, CustomTheme? customTheme = null)
    {
        _currentTheme = theme;
        _customTheme = customTheme;
        
        ApplyTheme(theme);
        
        _ = SaveThemePreferenceAsync();
        
        ThemeChanged?.Invoke(this, new ThemeChangedEventArgs
        {
            NewTheme = theme,
            EffectiveTheme = GetEffectiveTheme(),
            CustomTheme = customTheme,
        });
    }

    /// <summary>
    /// Set the accent color.
    /// </summary>
    public void SetAccent(ThemeAccent accent)
    {
        _currentAccent = accent;
        ApplyAccent(accent);
        
        _ = SaveThemePreferenceAsync();
    }

    /// <summary>
    /// Toggle between light and dark themes.
    /// </summary>
    public void ToggleDarkMode()
    {
        var newTheme = GetEffectiveTheme() == ElementTheme.Dark
            ? AppTheme.Light
            : AppTheme.Dark;
        
        SetTheme(newTheme);
    }

    /// <summary>
    /// Get the effective element theme.
    /// </summary>
    public ElementTheme GetEffectiveTheme()
    {
        if (_currentTheme == AppTheme.System)
        {
            return GetSystemTheme();
        }
        
        return _currentTheme switch
        {
            AppTheme.Light => ElementTheme.Light,
            AppTheme.Dark => ElementTheme.Dark,
            AppTheme.HighContrast => ElementTheme.Default,
            AppTheme.Custom => _customTheme?.IsDark == true
                ? ElementTheme.Dark
                : ElementTheme.Light,
            _ => ElementTheme.Default,
        };
    }

    /// <summary>
    /// Check if dark mode is active.
    /// </summary>
    public bool IsDarkMode()
    {
        return GetEffectiveTheme() == ElementTheme.Dark;
    }

    /// <summary>
    /// Create a new custom theme.
    /// </summary>
    public CustomTheme CreateCustomTheme(string name, bool basedOnDark = true)
    {
        var theme = new CustomTheme
        {
            Name = name,
            IsDark = basedOnDark,
        };
        
        if (basedOnDark)
        {
            ApplyDarkDefaults(theme);
        }
        else
        {
            ApplyLightDefaults(theme);
        }
        
        _customThemes.Add(theme);
        return theme;
    }

    /// <summary>
    /// Delete a custom theme.
    /// </summary>
    public bool DeleteCustomTheme(string themeId)
    {
        var theme = _customThemes.Find(t => t.Id == themeId);
        if (theme != null)
        {
            _customThemes.Remove(theme);
            
            if (_customTheme?.Id == themeId)
            {
                SetTheme(AppTheme.System);
            }
            
            return true;
        }
        
        return false;
    }

    /// <summary>
    /// Get predefined accent colors.
    /// </summary>
    public IReadOnlyList<ThemeAccent> GetPredefinedAccents()
    {
        return new List<ThemeAccent>
        {
            new() { Name = "Blue", Primary = Windows.UI.Color.FromArgb(255, 0, 120, 212) },
            new() { Name = "Purple", Primary = Windows.UI.Color.FromArgb(255, 128, 57, 123) },
            new() { Name = "Pink", Primary = Windows.UI.Color.FromArgb(255, 231, 72, 86) },
            new() { Name = "Red", Primary = Windows.UI.Color.FromArgb(255, 232, 17, 35) },
            new() { Name = "Orange", Primary = Windows.UI.Color.FromArgb(255, 247, 99, 12) },
            new() { Name = "Yellow", Primary = Windows.UI.Color.FromArgb(255, 255, 185, 0) },
            new() { Name = "Green", Primary = Windows.UI.Color.FromArgb(255, 16, 137, 62) },
            new() { Name = "Teal", Primary = Windows.UI.Color.FromArgb(255, 0, 178, 148) },
        };
    }

    private void ApplyTheme(AppTheme theme)
    {
        if (_rootElement == null)
        {
            return;
        }
        
        _rootElement.RequestedTheme = GetEffectiveTheme();
        
        if (theme == AppTheme.Custom && _customTheme != null)
        {
            ApplyCustomTheme(_customTheme);
        }
    }

    private void ApplyAccent(ThemeAccent accent)
    {
        // Apply accent colors to application resources
        if (Application.Current.Resources.TryGetValue("SystemAccentColor", out var _))
        {
            Application.Current.Resources["SystemAccentColor"] = accent.Primary;
        }
    }

    private void ApplyCustomTheme(CustomTheme theme)
    {
        var resources = Application.Current.Resources;
        
        // Apply custom colors to resources
        resources["CustomBackgroundPrimary"] = theme.BackgroundPrimary;
        resources["CustomBackgroundSecondary"] = theme.BackgroundSecondary;
        resources["CustomTextPrimary"] = theme.TextPrimary;
        resources["CustomAccentPrimary"] = theme.AccentPrimary;
    }

    private ElementTheme GetSystemTheme()
    {
        var uiSettings = new Windows.UI.ViewManagement.UISettings();
        var foreground = uiSettings.GetColorValue(
            Windows.UI.ViewManagement.UIColorType.Foreground);
        
        // If foreground is light, system is in dark mode
        return foreground.R > 128 ? ElementTheme.Dark : ElementTheme.Light;
    }

    private void OnSystemThemeChanged(
        Windows.UI.ViewManagement.UISettings sender,
        object args)
    {
        if (_currentTheme == AppTheme.System && _rootElement != null)
        {
            _rootElement.DispatcherQueue.TryEnqueue(() =>
            {
                ApplyTheme(_currentTheme);
                
                ThemeChanged?.Invoke(this, new ThemeChangedEventArgs
                {
                    NewTheme = _currentTheme,
                    EffectiveTheme = GetEffectiveTheme(),
                });
            });
        }
    }

    private async Task LoadThemePreferenceAsync()
    {
        try
        {
            var settings = ApplicationData.Current.LocalSettings;
            
            if (settings.Values.TryGetValue("AppTheme", out var themeValue))
            {
                if (Enum.TryParse<AppTheme>(themeValue.ToString(), out var theme))
                {
                    _currentTheme = theme;
                }
            }
        }
        // ALLOWED: empty catch - using default theme is acceptable fallback
        catch
        {
        }
        
        await Task.CompletedTask;
    }

    private async Task SaveThemePreferenceAsync()
    {
        try
        {
            var settings = ApplicationData.Current.LocalSettings;
            settings.Values["AppTheme"] = _currentTheme.ToString();
        }
        // ALLOWED: empty catch - theme save is non-critical
        catch
        {
        }
        
        await Task.CompletedTask;
    }

    private void ApplyDarkDefaults(CustomTheme theme)
    {
        theme.BackgroundPrimary = Windows.UI.Color.FromArgb(255, 32, 32, 32);
        theme.BackgroundSecondary = Windows.UI.Color.FromArgb(255, 45, 45, 45);
        theme.BackgroundTertiary = Windows.UI.Color.FromArgb(255, 58, 58, 58);
        theme.TextPrimary = Windows.UI.Color.FromArgb(255, 255, 255, 255);
        theme.TextSecondary = Windows.UI.Color.FromArgb(255, 180, 180, 180);
        theme.TextDisabled = Windows.UI.Color.FromArgb(255, 100, 100, 100);
        theme.AccentPrimary = _currentAccent.Primary;
        theme.AccentSecondary = _currentAccent.Secondary;
        theme.BorderDefault = Windows.UI.Color.FromArgb(255, 60, 60, 60);
        theme.BorderFocused = _currentAccent.Primary;
        theme.Success = Windows.UI.Color.FromArgb(255, 16, 185, 129);
        theme.Warning = Windows.UI.Color.FromArgb(255, 245, 158, 11);
        theme.Error = Windows.UI.Color.FromArgb(255, 239, 68, 68);
        theme.Info = Windows.UI.Color.FromArgb(255, 59, 130, 246);
    }

    private void ApplyLightDefaults(CustomTheme theme)
    {
        theme.BackgroundPrimary = Windows.UI.Color.FromArgb(255, 255, 255, 255);
        theme.BackgroundSecondary = Windows.UI.Color.FromArgb(255, 245, 245, 245);
        theme.BackgroundTertiary = Windows.UI.Color.FromArgb(255, 235, 235, 235);
        theme.TextPrimary = Windows.UI.Color.FromArgb(255, 0, 0, 0);
        theme.TextSecondary = Windows.UI.Color.FromArgb(255, 80, 80, 80);
        theme.TextDisabled = Windows.UI.Color.FromArgb(255, 160, 160, 160);
        theme.AccentPrimary = _currentAccent.Primary;
        theme.AccentSecondary = _currentAccent.Secondary;
        theme.BorderDefault = Windows.UI.Color.FromArgb(255, 200, 200, 200);
        theme.BorderFocused = _currentAccent.Primary;
        theme.Success = Windows.UI.Color.FromArgb(255, 16, 185, 129);
        theme.Warning = Windows.UI.Color.FromArgb(255, 217, 119, 6);
        theme.Error = Windows.UI.Color.FromArgb(255, 220, 38, 38);
        theme.Info = Windows.UI.Color.FromArgb(255, 37, 99, 235);
    }
}
