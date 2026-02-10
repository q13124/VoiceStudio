// Phase 5: Voice Profile UI
// Task 5.15: Voice profile management UI

using System;
using System.Collections.ObjectModel;
using System.ComponentModel;
using System.IO;
using System.Linq;
using System.Runtime.CompilerServices;
using System.Text.Json;
using System.Threading.Tasks;
using System.Windows.Input;
using CommunityToolkit.Mvvm.Input;
using VoiceStudio.App.Services;
using VoiceStudio.App.Logging;

namespace VoiceStudio.App.Features.VoiceProfile;

/// <summary>
/// Voice profile source.
/// </summary>
public enum VoiceSource
{
    Builtin,
    Cloned,
    Imported,
    Community,
}

/// <summary>
/// Voice profile data.
/// </summary>
public class VoiceProfileData : INotifyPropertyChanged
{
    private string _name = "";
    private string _description = "";
    private bool _isFavorite;
    private double _rating;
    private DateTime _lastUsed;

    public string Id { get; set; } = Guid.NewGuid().ToString();
    
    public string Name
    {
        get => _name;
        set { _name = value; OnPropertyChanged(); }
    }
    
    public string Description
    {
        get => _description;
        set { _description = value; OnPropertyChanged(); }
    }
    
    public VoiceSource Source { get; set; }
    public string Engine { get; set; } = "";
    public string Language { get; set; } = "en";
    public string Gender { get; set; } = "";
    public string? ThumbnailPath { get; set; }
    public string? SampleAudioPath { get; set; }
    public DateTime CreatedAt { get; set; } = DateTime.Now;
    
    public DateTime LastUsed
    {
        get => _lastUsed;
        set { _lastUsed = value; OnPropertyChanged(); }
    }
    
    public bool IsFavorite
    {
        get => _isFavorite;
        set { _isFavorite = value; OnPropertyChanged(); }
    }
    
    public double Rating
    {
        get => _rating;
        set { _rating = value; OnPropertyChanged(); }
    }
    
    public int UsageCount { get; set; }
    
    // Cloning specific
    public string? SourceAudioPath { get; set; }
    public TimeSpan? SourceDuration { get; set; }
    public double? CloningQuality { get; set; }
    
    public event PropertyChangedEventHandler? PropertyChanged;
    
    protected void OnPropertyChanged([CallerMemberName] string? name = null) =>
        PropertyChanged?.Invoke(this, new PropertyChangedEventArgs(name));
}

/// <summary>
/// ViewModel for voice profile management.
/// </summary>
public class VoiceProfileViewModel : INotifyPropertyChanged
{
    private VoiceProfileData? _selectedProfile;
    private string _searchQuery = "";
    private VoiceSource? _sourceFilter;
    private string? _languageFilter;
    private bool _showFavoritesOnly;
    private bool _isLoading;

    public VoiceProfileViewModel()
    {
        AllProfiles = new ObservableCollection<VoiceProfileData>();
        FilteredProfiles = new ObservableCollection<VoiceProfileData>();
        AvailableLanguages = new ObservableCollection<string>
        {
            "en", "es", "fr", "de", "it", "pt", "ja", "ko", "zh"
        };
        
        RefreshCommand = new AsyncRelayCommand(RefreshAsync);
        CloneVoiceCommand = new AsyncRelayCommand(CloneVoiceAsync, () => SelectedProfile != null);
        ImportVoiceCommand = new AsyncRelayCommand(ImportVoiceAsync);
        ExportVoiceCommand = new AsyncRelayCommand(ExportVoiceAsync, () => SelectedProfile != null);
        DeleteVoiceCommand = new AsyncRelayCommand(DeleteVoiceAsync, () => SelectedProfile != null && SelectedProfile.Source != VoiceSource.Builtin);
        PlaySampleCommand = new AsyncRelayCommand(PlaySampleAsync, () => !string.IsNullOrEmpty(SelectedProfile?.SampleAudioPath));
        ToggleFavoriteCommand = new RelayCommand(ToggleFavorite, () => SelectedProfile != null);
    }

    public ObservableCollection<VoiceProfileData> AllProfiles { get; }
    public ObservableCollection<VoiceProfileData> FilteredProfiles { get; }
    public ObservableCollection<string> AvailableLanguages { get; }

    public VoiceProfileData? SelectedProfile
    {
        get => _selectedProfile;
        set 
        { 
            _selectedProfile = value; 
            OnPropertyChanged();
            // Notify commands that depend on selection
            (CloneVoiceCommand as AsyncRelayCommand)?.NotifyCanExecuteChanged();
            (ExportVoiceCommand as AsyncRelayCommand)?.NotifyCanExecuteChanged();
            (DeleteVoiceCommand as AsyncRelayCommand)?.NotifyCanExecuteChanged();
            (PlaySampleCommand as AsyncRelayCommand)?.NotifyCanExecuteChanged();
            (ToggleFavoriteCommand as RelayCommand)?.NotifyCanExecuteChanged();
        }
    }

    public string SearchQuery
    {
        get => _searchQuery;
        set
        {
            _searchQuery = value;
            OnPropertyChanged();
            ApplyFilters();
        }
    }

    public VoiceSource? SourceFilter
    {
        get => _sourceFilter;
        set
        {
            _sourceFilter = value;
            OnPropertyChanged();
            ApplyFilters();
        }
    }

    public string? LanguageFilter
    {
        get => _languageFilter;
        set
        {
            _languageFilter = value;
            OnPropertyChanged();
            ApplyFilters();
        }
    }

    public bool ShowFavoritesOnly
    {
        get => _showFavoritesOnly;
        set
        {
            _showFavoritesOnly = value;
            OnPropertyChanged();
            ApplyFilters();
        }
    }

    public bool IsLoading
    {
        get => _isLoading;
        set { _isLoading = value; OnPropertyChanged(); }
    }

    // Commands
    public ICommand RefreshCommand { get; }
    public ICommand CloneVoiceCommand { get; }
    public ICommand ImportVoiceCommand { get; }
    public ICommand ExportVoiceCommand { get; }
    public ICommand DeleteVoiceCommand { get; }
    public ICommand PlaySampleCommand { get; }
    public ICommand ToggleFavoriteCommand { get; }

    public async Task LoadAsync()
    {
        IsLoading = true;
        
        try
        {
            await RefreshAsync();
        }
        finally
        {
            IsLoading = false;
        }
    }

    private async Task RefreshAsync()
    {
        // Load profiles from backend
        AllProfiles.Clear();
        
        // Add some sample profiles
        AllProfiles.Add(new VoiceProfileData
        {
            Name = "Default English",
            Description = "Standard English voice",
            Source = VoiceSource.Builtin,
            Engine = "xtts",
            Language = "en",
            Gender = "neutral",
        });
        
        AllProfiles.Add(new VoiceProfileData
        {
            Name = "My Clone",
            Description = "Cloned from sample recording",
            Source = VoiceSource.Cloned,
            Engine = "xtts",
            Language = "en",
            IsFavorite = true,
        });
        
        ApplyFilters();
        
        await Task.CompletedTask;
    }

    private async Task CloneVoiceAsync()
    {
        if (SelectedProfile == null)
        {
            return;
        }
        
        try
        {
            // Create a clone of the selected profile with a new ID
            var clonedProfile = new VoiceProfileData
            {
                Id = Guid.NewGuid().ToString(),
                Name = $"{SelectedProfile.Name} (Clone)",
                Description = SelectedProfile.Description,
                Source = VoiceSource.Cloned,
                Engine = SelectedProfile.Engine,
                Language = SelectedProfile.Language,
                Rating = SelectedProfile.Rating,
                IsFavorite = false,
                SampleAudioPath = SelectedProfile.SampleAudioPath,
                CreatedAt = DateTime.Now,
                LastUsed = DateTime.MinValue
            };
            
            AllProfiles.Add(clonedProfile);
            ApplyFilters();
            SelectedProfile = clonedProfile;
            
            ErrorLogger.LogInfo($"Voice profile cloned: {clonedProfile.Name}", "VoiceProfileViewModel");
        }
        catch (Exception ex)
        {
            ErrorLogger.LogError($"Failed to clone voice profile: {ex.Message}", "VoiceProfileViewModel");
        }
        
        await Task.CompletedTask;
    }

    private async Task ImportVoiceAsync()
    {
        try
        {
            // Look for JSON files in the exported profiles directory
            var importDir = Path.Combine(
                Environment.GetFolderPath(Environment.SpecialFolder.MyDocuments),
                "VoiceStudio", "ExportedProfiles");
            
            if (!Directory.Exists(importDir))
            {
                ErrorLogger.LogWarning("No exported profiles directory found. Export a profile first.", "VoiceProfileViewModel");
                return;
            }
            
            // Get the most recent export file (simple implementation)
            var files = Directory.GetFiles(importDir, "*.json")
                .OrderByDescending(f => File.GetCreationTime(f))
                .ToArray();
            
            if (files.Length == 0)
            {
                ErrorLogger.LogWarning("No profile files found in export directory.", "VoiceProfileViewModel");
                return;
            }
            
            // Import the most recent file
            var filePath = files[0];
            var json = await File.ReadAllTextAsync(filePath);
            var importData = JsonSerializer.Deserialize<JsonElement>(json);
            
            var importedProfile = new VoiceProfileData
            {
                Id = Guid.NewGuid().ToString(), // Generate new ID for imported profile
                Name = importData.TryGetProperty("Name", out var nameProp) ? nameProp.GetString() ?? "Imported" : "Imported",
                Description = importData.TryGetProperty("Description", out var descProp) ? descProp.GetString() ?? "" : "",
                Source = VoiceSource.Imported,
                Engine = importData.TryGetProperty("Engine", out var engineProp) ? engineProp.GetString() ?? "" : "",
                Language = importData.TryGetProperty("Language", out var langProp) ? langProp.GetString() ?? "en" : "en",
                Rating = importData.TryGetProperty("Rating", out var ratingProp) ? ratingProp.GetDouble() : 0.8,
                IsFavorite = false,
                CreatedAt = DateTime.Now,
                LastUsed = DateTime.MinValue
            };
            
            AllProfiles.Add(importedProfile);
            ApplyFilters();
            SelectedProfile = importedProfile;
            
            ErrorLogger.LogInfo($"Voice profile imported: {importedProfile.Name} from {Path.GetFileName(filePath)}", "VoiceProfileViewModel");
        }
        catch (Exception ex)
        {
            ErrorLogger.LogError($"Failed to import voice profile: {ex.Message}", "VoiceProfileViewModel");
        }
    }

    private async Task ExportVoiceAsync()
    {
        if (SelectedProfile == null)
        {
            return;
        }
        
        try
        {
            // Export voice profile to JSON file
            var exportDir = Path.Combine(
                Environment.GetFolderPath(Environment.SpecialFolder.MyDocuments),
                "VoiceStudio", "ExportedProfiles");
            
            Directory.CreateDirectory(exportDir);
            
            var fileName = $"{SelectedProfile.Name.Replace(" ", "_")}_{DateTime.Now:yyyyMMdd_HHmmss}.json";
            var filePath = Path.Combine(exportDir, fileName);
            
            var exportData = new
            {
                SelectedProfile.Id,
                SelectedProfile.Name,
                SelectedProfile.Description,
                Source = SelectedProfile.Source.ToString(),
                SelectedProfile.Engine,
                SelectedProfile.Language,
                SelectedProfile.Gender,
                SelectedProfile.CreatedAt,
                SelectedProfile.Rating,
                SelectedProfile.UsageCount,
                SelectedProfile.CloningQuality,
                ExportedAt = DateTime.Now
            };
            
            var json = JsonSerializer.Serialize(exportData, new JsonSerializerOptions { WriteIndented = true });
            await File.WriteAllTextAsync(filePath, json);
            
            ErrorLogger.LogInfo($"Voice profile exported to: {filePath}", "VoiceProfileViewModel");
        }
        catch (Exception ex)
        {
            ErrorLogger.LogError($"Failed to export voice profile: {ex.Message}", "VoiceProfileViewModel");
        }
    }

    private async Task DeleteVoiceAsync()
    {
        if (SelectedProfile == null || SelectedProfile.Source == VoiceSource.Builtin)
        {
            return;
        }
        
        AllProfiles.Remove(SelectedProfile);
        SelectedProfile = null;
        ApplyFilters();
        
        await Task.CompletedTask;
    }

    private async Task PlaySampleAsync()
    {
        if (SelectedProfile?.SampleAudioPath == null)
        {
            return;
        }
        
        try
        {
            // Get the audio player service and play the sample
            var audioPlayer = AppServices.GetAudioPlayerService();
            
            if (File.Exists(SelectedProfile.SampleAudioPath))
            {
                await audioPlayer.PlayFileAsync(SelectedProfile.SampleAudioPath);
                
                // Update last used timestamp
                SelectedProfile.LastUsed = DateTime.Now;
            }
            else
            {
                ErrorLogger.LogWarning(
                    $"Sample audio file not found: {SelectedProfile.SampleAudioPath}",
                    "VoiceProfileViewModel");
            }
        }
        catch (Exception ex)
        {
            ErrorLogger.LogError($"Failed to play voice sample: {ex.Message}", "VoiceProfileViewModel");
        }
    }

    private void ToggleFavorite()
    {
        if (SelectedProfile != null)
        {
            SelectedProfile.IsFavorite = !SelectedProfile.IsFavorite;
        }
    }

    private void ApplyFilters()
    {
        FilteredProfiles.Clear();
        
        foreach (var profile in AllProfiles)
        {
            if (!MatchesFilters(profile))
            {
                continue;
            }
            
            FilteredProfiles.Add(profile);
        }
    }

    private bool MatchesFilters(VoiceProfileData profile)
    {
        // Search query
        if (!string.IsNullOrEmpty(SearchQuery))
        {
            var query = SearchQuery.ToLowerInvariant();
            if (!profile.Name.ToLowerInvariant().Contains(query) &&
                !profile.Description.ToLowerInvariant().Contains(query))
            {
                return false;
            }
        }
        
        // Source filter
        if (SourceFilter.HasValue && profile.Source != SourceFilter.Value)
        {
            return false;
        }
        
        // Language filter
        if (!string.IsNullOrEmpty(LanguageFilter) && profile.Language != LanguageFilter)
        {
            return false;
        }
        
        // Favorites only
        if (ShowFavoritesOnly && !profile.IsFavorite)
        {
            return false;
        }
        
        return true;
    }

    public event PropertyChangedEventHandler? PropertyChanged;
    
    protected void OnPropertyChanged([CallerMemberName] string? name = null) =>
        PropertyChanged?.Invoke(this, new PropertyChangedEventArgs(name));
}

/// <summary>
/// Simple relay command.
/// </summary>
file class RelayCommand : ICommand
{
    private readonly Action _execute;
    private readonly Func<bool>? _canExecute;

    public RelayCommand(Action execute, Func<bool>? canExecute = null)
    {
        _execute = execute;
        _canExecute = canExecute;
    }

    public event EventHandler? CanExecuteChanged;
    public bool CanExecute(object? parameter) => _canExecute?.Invoke() ?? true;
    public void Execute(object? parameter) => _execute();
}
