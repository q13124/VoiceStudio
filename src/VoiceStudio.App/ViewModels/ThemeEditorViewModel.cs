using System;
using System.Collections.Generic;
using System.Collections.ObjectModel;
using System.IO;
using System.Linq;
using System.Text.Json;
using System.Threading.Tasks;
using CommunityToolkit.Mvvm.ComponentModel;
using CommunityToolkit.Mvvm.Input;
using VoiceStudio.App.Services;
using VoiceStudio.Core.Services;

namespace VoiceStudio.App.ViewModels;

/// <summary>
/// ViewModel for the Theme Editor panel.
/// Manages theme selection, accent colors, density settings, and custom theme persistence.
/// </summary>
public partial class ThemeEditorViewModel : BaseViewModel
{
    private readonly IUnifiedThemeService _themeService;
    private readonly string _customThemesPath;
    private bool _isInitializing;

    /// <summary>
    /// Available theme names.
    /// </summary>
    public IReadOnlyList<string> AvailableThemes { get; }

    /// <summary>
    /// Available accent colors.
    /// </summary>
    public IReadOnlyList<ThemeAccent> AvailableAccents { get; }

    /// <summary>
    /// Available density options.
    /// </summary>
    public IReadOnlyList<LayoutDensity> AvailableDensities { get; } = new List<LayoutDensity>
    {
        LayoutDensity.Compact,
        LayoutDensity.Normal,
        LayoutDensity.Comfortable,
        LayoutDensity.Touch
    };

    [ObservableProperty]
    private string _selectedTheme = "SciFi";

    [ObservableProperty]
    private ThemeAccent? _selectedAccent;

    [ObservableProperty]
    private LayoutDensity _selectedDensity = LayoutDensity.Compact;

    [ObservableProperty]
    private string _customThemeName = string.Empty;

    [ObservableProperty]
    private ObservableCollection<SavedThemeInfo> _savedThemes = new();

    [ObservableProperty]
    private SavedThemeInfo? _selectedSavedTheme;

    public ThemeEditorViewModel(IViewModelContext context, IUnifiedThemeService themeService)
        : base(context)
    {
        _themeService = themeService ?? throw new ArgumentNullException(nameof(themeService));
        
        AvailableThemes = _themeService.GetAvailableThemes();
        AvailableAccents = _themeService.GetPredefinedAccents();

        // Setup custom themes storage path
        var appData = Environment.GetFolderPath(Environment.SpecialFolder.LocalApplicationData);
        _customThemesPath = Path.Combine(appData, "VoiceStudio", "themes");
        Directory.CreateDirectory(_customThemesPath);
    }

    /// <summary>
    /// Initialize the ViewModel with current theme settings.
    /// </summary>
    public void Initialize()
    {
        _isInitializing = true;
        
        try
        {
            // Load current theme settings
            SelectedTheme = _themeService.CurrentThemeName;
            SelectedAccent = _themeService.CurrentAccent;
            SelectedDensity = _themeService.CurrentDensity;
            
            // Load saved themes
            LoadSavedThemes();
        }
        finally
        {
            _isInitializing = false;
        }
    }

    partial void OnSelectedThemeChanged(string value)
    {
        if (_isInitializing || string.IsNullOrEmpty(value)) return;
        
        _themeService.ApplyTheme(value);
        LogInfo($"Theme changed to: {value}", "ThemeEditor");
    }

    partial void OnSelectedAccentChanged(ThemeAccent? value)
    {
        if (_isInitializing || value == null) return;
        
        _themeService.SetAccent(value);
        LogInfo($"Accent changed to: {value.Name}", "ThemeEditor");
    }

    partial void OnSelectedDensityChanged(LayoutDensity value)
    {
        if (_isInitializing) return;
        
        _themeService.SetDensity(value);
        LogInfo($"Density changed to: {value}", "ThemeEditor");
    }

    /// <summary>
    /// Reset all theme settings to defaults.
    /// </summary>
    [RelayCommand]
    private void ResetToDefaults()
    {
        _isInitializing = true;
        
        try
        {
            _themeService.ApplyTheme("SciFi");
            _themeService.SetDensity(LayoutDensity.Compact);
            
            if (AvailableAccents.Count > 0)
            {
                _themeService.SetAccent(AvailableAccents[0]); // Blue
            }

            // Update VM state
            SelectedTheme = "SciFi";
            SelectedDensity = LayoutDensity.Compact;
            SelectedAccent = AvailableAccents.FirstOrDefault();
            
            LogInfo("Theme reset to defaults", "ThemeEditor");
        }
        finally
        {
            _isInitializing = false;
        }
    }

    /// <summary>
    /// Save current theme settings as a custom preset.
    /// </summary>
    [RelayCommand]
    private async Task SaveCustomThemeAsync()
    {
        var themeName = CustomThemeName?.Trim();
        if (string.IsNullOrEmpty(themeName))
        {
            themeName = $"Custom_{DateTime.Now:yyyyMMdd_HHmmss}";
        }

        await ExecuteWithErrorHandlingAsync(async () =>
        {
            var themeData = new Dictionary<string, string>
            {
                ["theme"] = SelectedTheme,
                ["density"] = SelectedDensity.ToString(),
                ["accentName"] = SelectedAccent?.Name ?? "Blue"
            };

            var json = JsonSerializer.Serialize(themeData, new JsonSerializerOptions { WriteIndented = true });
            var filePath = Path.Combine(_customThemesPath, $"{themeName}.json");
            
            await File.WriteAllTextAsync(filePath, json);

            CustomThemeName = string.Empty;
            LoadSavedThemes();

            LogInfo($"Saved custom theme: {themeName}", "ThemeEditor");
        }, "SaveCustomTheme");
    }

    /// <summary>
    /// Load a saved custom theme.
    /// </summary>
    [RelayCommand]
    private async Task LoadSelectedThemeAsync()
    {
        if (SelectedSavedTheme == null) return;

        await ExecuteWithErrorHandlingAsync(async () =>
        {
            var json = await File.ReadAllTextAsync(SelectedSavedTheme.FilePath);
            var themeData = JsonSerializer.Deserialize<Dictionary<string, string>>(json);

            if (themeData == null) return;

            _isInitializing = true;

            try
            {
                if (themeData.TryGetValue("theme", out var themeName))
                {
                    SelectedTheme = themeName;
                    _themeService.ApplyTheme(themeName);
                }

                if (themeData.TryGetValue("density", out var densityStr) &&
                    Enum.TryParse<LayoutDensity>(densityStr, out var density))
                {
                    SelectedDensity = density;
                    _themeService.SetDensity(density);
                }

                if (themeData.TryGetValue("accentName", out var accentName))
                {
                    var accent = AvailableAccents.FirstOrDefault(a => a.Name == accentName);
                    if (accent != null)
                    {
                        SelectedAccent = accent;
                        _themeService.SetAccent(accent);
                    }
                }

                LogInfo($"Loaded custom theme: {SelectedSavedTheme.Name}", "ThemeEditor");
            }
            finally
            {
                _isInitializing = false;
            }
        }, "LoadCustomTheme");
    }

    /// <summary>
    /// Delete a saved custom theme.
    /// </summary>
    [RelayCommand]
    private void DeleteSelectedTheme()
    {
        if (SelectedSavedTheme == null) return;

        try
        {
            if (File.Exists(SelectedSavedTheme.FilePath))
            {
                File.Delete(SelectedSavedTheme.FilePath);
                LogInfo($"Deleted custom theme: {SelectedSavedTheme.Name}", "ThemeEditor");
            }
            
            LoadSavedThemes();
        }
        catch (Exception ex)
        {
            LogWarning($"Failed to delete theme: {ex.Message}", "ThemeEditor");
        }
    }

    /// <summary>
    /// Load the list of saved custom themes.
    /// </summary>
    private void LoadSavedThemes()
    {
        try
        {
            SavedThemes.Clear();
            
            if (!Directory.Exists(_customThemesPath))
            {
                Directory.CreateDirectory(_customThemesPath);
                return;
            }

            var themeFiles = Directory.GetFiles(_customThemesPath, "*.json");
            foreach (var file in themeFiles)
            {
                var name = Path.GetFileNameWithoutExtension(file);
                SavedThemes.Add(new SavedThemeInfo
                {
                    Name = name,
                    FilePath = file
                });
            }
        }
        catch (Exception ex)
        {
            LogWarning($"Failed to load saved themes: {ex.Message}", "ThemeEditor");
        }
    }
}

/// <summary>
/// Information about a saved custom theme.
/// </summary>
public class SavedThemeInfo
{
    public string Name { get; set; } = string.Empty;
    public string FilePath { get; set; } = string.Empty;
}
