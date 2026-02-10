// Phase 5: Settings UI
// Task 5.2: Comprehensive settings management

using System;
using System.Collections.ObjectModel;
using System.ComponentModel;
using System.Runtime.CompilerServices;
using System.Threading.Tasks;
using System.Windows.Input;
using VoiceStudio.App.Features.Accessibility;
using VoiceStudio.App.Features.Theming;

namespace VoiceStudio.App.Features.Settings;

/// <summary>
/// Settings categories.
/// </summary>
public enum SettingsCategory
{
    General,
    Appearance,
    Audio,
    Synthesis,
    Accessibility,
    Keyboard,
    Advanced,
    About,
}

/// <summary>
/// ViewModel for application settings.
/// </summary>
public class SettingsViewModel : INotifyPropertyChanged
{
    private readonly ThemeService _themeService;
    private readonly AccessibilityService _accessibilityService;
    
    private SettingsCategory _selectedCategory = SettingsCategory.General;
    private bool _isLoading;
    private bool _hasChanges;

    public event PropertyChangedEventHandler? PropertyChanged;

    public SettingsViewModel(
        ThemeService themeService,
        AccessibilityService accessibilityService)
    {
        _themeService = themeService;
        _accessibilityService = accessibilityService;
        
        SaveCommand = new RelayCommand(async () => await SaveAsync());
        ResetCommand = new RelayCommand(async () => await ResetAsync());
        ImportCommand = new RelayCommand(async () => await ImportSettingsAsync());
        ExportCommand = new RelayCommand(async () => await ExportSettingsAsync());
        
        Categories = new ObservableCollection<SettingsCategoryItem>
        {
            new() { Category = SettingsCategory.General, Name = "General", Icon = "\uE713" },
            new() { Category = SettingsCategory.Appearance, Name = "Appearance", Icon = "\uE771" },
            new() { Category = SettingsCategory.Audio, Name = "Audio", Icon = "\uE767" },
            new() { Category = SettingsCategory.Synthesis, Name = "Synthesis", Icon = "\uE8D6" },
            new() { Category = SettingsCategory.Accessibility, Name = "Accessibility", Icon = "\uE776" },
            new() { Category = SettingsCategory.Keyboard, Name = "Keyboard", Icon = "\uE92E" },
            new() { Category = SettingsCategory.Advanced, Name = "Advanced", Icon = "\uE90F" },
            new() { Category = SettingsCategory.About, Name = "About", Icon = "\uE946" },
        };
    }

    // Properties
    public ObservableCollection<SettingsCategoryItem> Categories { get; }

    public SettingsCategory SelectedCategory
    {
        get => _selectedCategory;
        set
        {
            if (_selectedCategory != value)
            {
                _selectedCategory = value;
                OnPropertyChanged();
                OnPropertyChanged(nameof(ShowGeneralSettings));
                OnPropertyChanged(nameof(ShowAppearanceSettings));
                OnPropertyChanged(nameof(ShowAudioSettings));
                OnPropertyChanged(nameof(ShowSynthesisSettings));
                OnPropertyChanged(nameof(ShowAccessibilitySettings));
                OnPropertyChanged(nameof(ShowKeyboardSettings));
                OnPropertyChanged(nameof(ShowAdvancedSettings));
                OnPropertyChanged(nameof(ShowAboutSettings));
            }
        }
    }

    public bool ShowGeneralSettings => SelectedCategory == SettingsCategory.General;
    public bool ShowAppearanceSettings => SelectedCategory == SettingsCategory.Appearance;
    public bool ShowAudioSettings => SelectedCategory == SettingsCategory.Audio;
    public bool ShowSynthesisSettings => SelectedCategory == SettingsCategory.Synthesis;
    public bool ShowAccessibilitySettings => SelectedCategory == SettingsCategory.Accessibility;
    public bool ShowKeyboardSettings => SelectedCategory == SettingsCategory.Keyboard;
    public bool ShowAdvancedSettings => SelectedCategory == SettingsCategory.Advanced;
    public bool ShowAboutSettings => SelectedCategory == SettingsCategory.About;

    public bool IsLoading
    {
        get => _isLoading;
        set { _isLoading = value; OnPropertyChanged(); }
    }

    public bool HasChanges
    {
        get => _hasChanges;
        set { _hasChanges = value; OnPropertyChanged(); }
    }

    // Commands
    public ICommand SaveCommand { get; }
    public ICommand ResetCommand { get; }
    public ICommand ImportCommand { get; }
    public ICommand ExportCommand { get; }

    // General Settings
    public string Language { get; set; } = "en-US";
    public bool AutoSaveEnabled { get; set; } = true;
    public int AutoSaveIntervalMinutes { get; set; } = 5;
    public bool CheckForUpdates { get; set; } = true;
    public bool ShowWelcomeOnStartup { get; set; } = true;
    public string DefaultProjectPath { get; set; } = "";

    // Appearance Settings
    public AppTheme SelectedTheme
    {
        get => _themeService.CurrentTheme;
        set
        {
            _themeService.SetTheme(value);
            OnPropertyChanged();
            HasChanges = true;
        }
    }

    public bool IsDarkMode
    {
        get => _themeService.IsDarkMode();
        set
        {
            _themeService.SetTheme(value ? AppTheme.Dark : AppTheme.Light);
            OnPropertyChanged();
        }
    }

    public double UIScale { get; set; } = 1.0;
    public bool CompactMode { get; set; } = false;
    public bool ShowStatusBar { get; set; } = true;
    public bool ShowToolbar { get; set; } = true;

    // Audio Settings
    public string DefaultInputDevice { get; set; } = "";
    public string DefaultOutputDevice { get; set; } = "";
    public int SampleRate { get; set; } = 44100;
    public int BitDepth { get; set; } = 16;
    public int BufferSize { get; set; } = 512;
    public bool AudioMonitoring { get; set; } = true;
    public double MasterVolume { get; set; } = 1.0;

    // Synthesis Settings
    public string DefaultEngine { get; set; } = "xtts";
    public string DefaultVoice { get; set; } = "";
    public double DefaultSpeed { get; set; } = 1.0;
    public double DefaultPitch { get; set; } = 1.0;
    public bool UseGPU { get; set; } = true;
    public int MaxConcurrentSynthesis { get; set; } = 2;

    // Accessibility Settings
    public AccessibilitySettings AccessibilitySettings => _accessibilityService.Settings;

    public bool ScreenReaderSupport
    {
        get => _accessibilityService.Settings.ScreenReaderAnnouncements;
        set
        {
            _accessibilityService.UpdateSettings(s =>
                s.ScreenReaderAnnouncements = value);
            OnPropertyChanged();
        }
    }

    public bool ReduceMotion
    {
        get => _accessibilityService.Settings.ReduceMotion;
        set
        {
            _accessibilityService.UpdateSettings(s => s.ReduceMotion = value);
            OnPropertyChanged();
        }
    }

    public bool HighContrast
    {
        get => _accessibilityService.Settings.HighContrastMode;
        set
        {
            _accessibilityService.UpdateSettings(s =>
                s.HighContrastMode = value);
            OnPropertyChanged();
        }
    }

    public double TextScaling
    {
        get => _accessibilityService.Settings.TextScaling;
        set
        {
            _accessibilityService.UpdateSettings(s => s.TextScaling = value);
            OnPropertyChanged();
        }
    }

    // Advanced Settings
    public bool DebugMode { get; set; } = false;
    public bool VerboseLogging { get; set; } = false;
    public string LogLevel { get; set; } = "Information";
    public int MaxLogFiles { get; set; } = 10;
    public bool EnableTelemetry { get; set; } = false;
    public string BackendUrl { get; set; } = "http://localhost:8000";
    public int BackendTimeout { get; set; } = 30;
    public bool EnableExperimentalFeatures { get; set; } = false;

    // About
    public string Version => "1.0.0";
    public string BuildDate => DateTime.Now.ToString("yyyy-MM-dd");
    public string Copyright => "© 2026 VoiceStudio";

    // Methods
    public async Task LoadAsync()
    {
        IsLoading = true;
        
        try
        {
            // Load settings from storage
            await Task.Delay(100); // Simulate loading
        }
        finally
        {
            IsLoading = false;
        }
    }

    public async Task SaveAsync()
    {
        IsLoading = true;
        
        try
        {
            // Save settings to storage
            await Task.Delay(100); // Simulate saving
            HasChanges = false;
        }
        finally
        {
            IsLoading = false;
        }
    }

    private async Task ResetAsync()
    {
        // Reset to defaults
        Language = "en-US";
        AutoSaveEnabled = true;
        AutoSaveIntervalMinutes = 5;
        SelectedTheme = AppTheme.System;
        UIScale = 1.0;
        
        HasChanges = true;
        await Task.CompletedTask;
    }

    private async Task ImportSettingsAsync()
    {
        // Import settings from file
        await Task.CompletedTask;
    }

    private async Task ExportSettingsAsync()
    {
        // Export settings to file
        await Task.CompletedTask;
    }

    protected void OnPropertyChanged([CallerMemberName] string? propertyName = null)
    {
        PropertyChanged?.Invoke(this, new PropertyChangedEventArgs(propertyName));
        
        if (propertyName != nameof(IsLoading) &&
            propertyName != nameof(HasChanges))
        {
            HasChanges = true;
        }
    }
}

/// <summary>
/// Settings category item for navigation.
/// </summary>
public class SettingsCategoryItem
{
    public SettingsCategory Category { get; set; }
    public string Name { get; set; } = "";
    public string Icon { get; set; } = "";
}

/// <summary>
/// Simple relay command implementation.
/// </summary>
public class RelayCommand : ICommand
{
    private readonly Func<Task> _execute;
    private readonly Func<bool>? _canExecute;

    public RelayCommand(Func<Task> execute, Func<bool>? canExecute = null)
    {
        _execute = execute;
        _canExecute = canExecute;
    }

    public event EventHandler? CanExecuteChanged;

    public bool CanExecute(object? parameter) => _canExecute?.Invoke() ?? true;

    public async void Execute(object? parameter) => await _execute();

    public void RaiseCanExecuteChanged() =>
        CanExecuteChanged?.Invoke(this, EventArgs.Empty);
}
