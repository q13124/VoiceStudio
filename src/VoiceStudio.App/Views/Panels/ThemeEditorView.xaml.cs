using Microsoft.UI.Xaml;
using Microsoft.UI.Xaml.Controls;
using VoiceStudio.App.Services;

namespace VoiceStudio.App.Views.Panels;

/// <summary>
/// Theme Editor panel for customizing application appearance.
/// </summary>
public sealed partial class ThemeEditorView : UserControl
{
    private IUnifiedThemeService? _themeService;
    private bool _isInitializing = true;

    public ThemeEditorView()
    {
        this.InitializeComponent();
        this.Loaded += OnLoaded;
    }

    private void OnLoaded(object sender, RoutedEventArgs e)
    {
        _themeService = AppServices.TryGetThemeService();
        InitializeControls();
        _isInitializing = false;
    }

    private void InitializeControls()
    {
        if (_themeService == null) return;

        // Set current theme in ComboBox
        var currentTheme = _themeService.CurrentThemeName;
        foreach (ComboBoxItem item in ThemeComboBox.Items)
        {
            if (item.Tag?.ToString() == currentTheme)
            {
                ThemeComboBox.SelectedItem = item;
                break;
            }
        }

        // Set accent colors
        AccentColorGrid.ItemsSource = _themeService.GetPredefinedAccents();
        var currentAccent = _themeService.CurrentAccent;
        var accents = _themeService.GetPredefinedAccents();
        for (int i = 0; i < accents.Count; i++)
        {
            if (accents[i].Name == currentAccent.Name)
            {
                AccentColorGrid.SelectedIndex = i;
                break;
            }
        }

        // Set current density in ComboBox
        var currentDensity = _themeService.CurrentDensity.ToString();
        foreach (ComboBoxItem item in DensityComboBox.Items)
        {
            if (item.Tag?.ToString() == currentDensity)
            {
                DensityComboBox.SelectedItem = item;
                break;
            }
        }
    }

    private void ThemeComboBox_SelectionChanged(object sender, Microsoft.UI.Xaml.Controls.SelectionChangedEventArgs e)
    {
        if (_isInitializing || _themeService == null) return;

        if (ThemeComboBox.SelectedItem is ComboBoxItem selectedItem)
        {
            var themeName = selectedItem.Tag?.ToString();
            if (!string.IsNullOrEmpty(themeName))
            {
                _themeService.ApplyTheme(themeName);
            }
        }
    }

    private void AccentColorGrid_SelectionChanged(object sender, Microsoft.UI.Xaml.Controls.SelectionChangedEventArgs e)
    {
        if (_isInitializing || _themeService == null) return;

        if (AccentColorGrid.SelectedItem is ThemeAccent accent)
        {
            _themeService.SetAccent(accent);
        }
    }

    private void DensityComboBox_SelectionChanged(object sender, Microsoft.UI.Xaml.Controls.SelectionChangedEventArgs e)
    {
        if (_isInitializing || _themeService == null) return;

        if (DensityComboBox.SelectedItem is ComboBoxItem selectedItem)
        {
            var densityName = selectedItem.Tag?.ToString();
            if (!string.IsNullOrEmpty(densityName) && 
                System.Enum.TryParse<LayoutDensity>(densityName, out var density))
            {
                _themeService.SetDensity(density);
            }
        }
    }

    private void ResetButton_Click(object sender, RoutedEventArgs e)
    {
        if (_themeService == null) return;

        _isInitializing = true;
        
        // Reset to defaults
        _themeService.ApplyTheme("SciFi");
        _themeService.SetDensity(LayoutDensity.Compact);
        var accents = _themeService.GetPredefinedAccents();
        if (accents.Count > 0)
        {
            _themeService.SetAccent(accents[0]); // Blue
        }

        // Update UI
        InitializeControls();
        
        _isInitializing = false;
    }
}
