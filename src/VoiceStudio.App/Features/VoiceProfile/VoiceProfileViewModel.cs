// Phase 5: Voice Profile UI
// Task 5.15: Voice profile management UI
// GAP-FE-001: Integrated with ProfileGateway for backend connectivity

using System;
using System.Collections.ObjectModel;
using System.IO;
using System.Linq;
using System.Threading;
using System.Threading.Tasks;
using CommunityToolkit.Mvvm.ComponentModel;
using CommunityToolkit.Mvvm.Input;
using Microsoft.Extensions.Logging;
using VoiceStudio.App.ViewModels;
using VoiceStudio.Core.Gateways;
using VoiceStudio.Core.Services;

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
public partial class VoiceProfileData : ObservableObject
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
        set => SetProperty(ref _name, value);
    }
    
    public string Description
    {
        get => _description;
        set => SetProperty(ref _description, value);
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
        set => SetProperty(ref _lastUsed, value);
    }
    
    public bool IsFavorite
    {
        get => _isFavorite;
        set => SetProperty(ref _isFavorite, value);
    }
    
    public double Rating
    {
        get => _rating;
        set => SetProperty(ref _rating, value);
    }
    
    public int UsageCount { get; set; }
    
    // Cloning specific
    public string? SourceAudioPath { get; set; }
    public TimeSpan? SourceDuration { get; set; }
    public double? CloningQuality { get; set; }
}

/// <summary>
/// ViewModel for voice profile management.
/// GAP-FE-001: Refactored to inherit from BaseViewModel and integrate with ProfileGateway.
/// </summary>
public partial class VoiceProfileViewModel : BaseViewModel
{
    private readonly IProfileGateway _profileGateway;
    private readonly IVoiceGateway _voiceGateway;

    private VoiceProfileData? _selectedProfile;
    private string _searchQuery = "";
    private VoiceSource? _sourceFilter;
    private string? _languageFilter;
    private bool _showFavoritesOnly;

    public VoiceProfileViewModel(
        IViewModelContext context,
        IProfileGateway profileGateway,
        IVoiceGateway voiceGateway)
        : base(context)
    {
        _profileGateway = profileGateway ?? throw new ArgumentNullException(nameof(profileGateway));
        _voiceGateway = voiceGateway ?? throw new ArgumentNullException(nameof(voiceGateway));

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
        CreateProfileCommand = new AsyncRelayCommand(CreateProfileAsync);
        SaveProfileCommand = new AsyncRelayCommand(SaveProfileAsync, () => SelectedProfile != null);
    }

    public ObservableCollection<VoiceProfileData> AllProfiles { get; }
    public ObservableCollection<VoiceProfileData> FilteredProfiles { get; }
    public ObservableCollection<string> AvailableLanguages { get; }

    public VoiceProfileData? SelectedProfile
    {
        get => _selectedProfile;
        set 
        { 
            if (SetProperty(ref _selectedProfile, value))
            {
                // Notify commands that depend on selection
                CloneVoiceCommand.NotifyCanExecuteChanged();
                ExportVoiceCommand.NotifyCanExecuteChanged();
                DeleteVoiceCommand.NotifyCanExecuteChanged();
                PlaySampleCommand.NotifyCanExecuteChanged();
                ToggleFavoriteCommand.NotifyCanExecuteChanged();
                SaveProfileCommand.NotifyCanExecuteChanged();
            }
        }
    }

    public string SearchQuery
    {
        get => _searchQuery;
        set
        {
            if (SetProperty(ref _searchQuery, value))
            {
                ApplyFilters();
            }
        }
    }

    public VoiceSource? SourceFilter
    {
        get => _sourceFilter;
        set
        {
            if (SetProperty(ref _sourceFilter, value))
            {
                ApplyFilters();
            }
        }
    }

    public string? LanguageFilter
    {
        get => _languageFilter;
        set
        {
            if (SetProperty(ref _languageFilter, value))
            {
                ApplyFilters();
            }
        }
    }

    public bool ShowFavoritesOnly
    {
        get => _showFavoritesOnly;
        set
        {
            if (SetProperty(ref _showFavoritesOnly, value))
            {
                ApplyFilters();
            }
        }
    }

    // Commands
    public AsyncRelayCommand RefreshCommand { get; }
    public AsyncRelayCommand CloneVoiceCommand { get; }
    public AsyncRelayCommand ImportVoiceCommand { get; }
    public AsyncRelayCommand ExportVoiceCommand { get; }
    public AsyncRelayCommand DeleteVoiceCommand { get; }
    public AsyncRelayCommand PlaySampleCommand { get; }
    public RelayCommand ToggleFavoriteCommand { get; }
    public AsyncRelayCommand CreateProfileCommand { get; }
    public AsyncRelayCommand SaveProfileCommand { get; }

    public async Task LoadAsync()
    {
        IsLoading = true;
        StatusMessage = "Loading profiles...";
        
        try
        {
            await RefreshAsync();
            StatusMessage = "Profiles loaded";
        }
        catch (Exception ex)
        {
            await HandleErrorAsync(ex, "Failed to load profiles");
        }
        finally
        {
            IsLoading = false;
        }
    }

    private async Task RefreshAsync()
    {
        IsLoading = true;
        ErrorMessage = null;
        
        try
        {
            // Load profiles from backend via ProfileGateway
            var result = await _profileGateway.GetAllAsync();
            
            AllProfiles.Clear();
            
            if (result.Success && result.Data != null)
            {
                foreach (var profileInfo in result.Data)
                {
                    AllProfiles.Add(new VoiceProfileData
                    {
                        Id = profileInfo.Id,
                        Name = profileInfo.Name,
                        Description = profileInfo.Description ?? "",
                        Engine = profileInfo.EngineId ?? "",
                        CreatedAt = profileInfo.CreatedAt,
                        Source = profileInfo.IsDefault ? VoiceSource.Builtin : VoiceSource.Cloned,
                    });
                }
                
                StatusMessage = $"Loaded {AllProfiles.Count} profiles";
            }
            else
            {
                // Backend unavailable - do NOT return fake sample data
                Logger.LogWarning("Failed to load profiles from backend: {Error}", result.Error);
                
                // Return empty list - UI should show "No profiles available. Check backend connection."
                // Do not add hardcoded sample profiles
                ErrorMessage = "No profiles available. Backend connection failed.";
            }
            
            ApplyFilters();
            
            if (FilteredProfiles.Count > 0 && SelectedProfile == null)
            {
                SelectedProfile = FilteredProfiles[0];
            }
        }
        catch (Exception ex)
        {
            await HandleErrorAsync(ex, "Failed to refresh profiles");
            
            // Do NOT add fake fallback profile - show empty list with error state
            // The UI should display "No profiles available" and prompt for backend connection
            ErrorMessage = "Failed to load profiles. Check backend connection.";
            ApplyFilters();
        }
        finally
        {
            IsLoading = false;
        }
    }

    private async Task CreateProfileAsync()
    {
        try
        {
            var request = new ProfileCreateRequest
            {
                Name = "New Profile",
                Description = "Created via VoiceStudio",
            };
            
            var result = await _profileGateway.CreateAsync(request);
            
            if (result.Success && result.Data != null)
            {
                var newProfile = new VoiceProfileData
                {
                    Id = result.Data.Id,
                    Name = result.Data.Name,
                    Description = result.Data.Description ?? "",
                    Engine = result.Data.EngineId ?? "",
                    CreatedAt = result.Data.CreatedAt,
                    Source = VoiceSource.Cloned,
                };
                
                AllProfiles.Add(newProfile);
                ApplyFilters();
                SelectedProfile = newProfile;
                
                StatusMessage = $"Created profile: {newProfile.Name}";
            }
            else
            {
                await HandleErrorAsync(result.Error?.Message ?? "Failed to create profile", "Profile error", showDialog: false);
            }
        }
        catch (Exception ex)
        {
            await HandleErrorAsync(ex, "Failed to create profile");
        }
    }

    private async Task SaveProfileAsync()
    {
        if (SelectedProfile == null)
        {
            return;
        }

        try
        {
            var request = new ProfileUpdateRequest
            {
                Name = SelectedProfile.Name,
                Description = SelectedProfile.Description,
            };
            
            var result = await _profileGateway.UpdateAsync(SelectedProfile.Id, request);
            
            if (result.Success)
            {
                StatusMessage = $"Saved profile: {SelectedProfile.Name}";
            }
            else
            {
                await HandleErrorAsync(result.Error?.Message ?? "Failed to save profile", "Profile error", showDialog: false);
            }
        }
        catch (Exception ex)
        {
            await HandleErrorAsync(ex, "Failed to save profile");
        }
    }

    private async Task CloneVoiceAsync()
    {
        if (SelectedProfile == null)
        {
            return;
        }
        
        try
        {
            // Create a clone of the selected profile via backend
            var request = new ProfileCreateRequest
            {
                Name = $"{SelectedProfile.Name} (Clone)",
                Description = SelectedProfile.Description,
                EngineId = SelectedProfile.Engine,
            };
            
            var result = await _profileGateway.CreateAsync(request);
            
            if (result.Success && result.Data != null)
            {
                var clonedProfile = new VoiceProfileData
                {
                    Id = result.Data.Id,
                    Name = result.Data.Name,
                    Description = result.Data.Description ?? "",
                    Source = VoiceSource.Cloned,
                    Engine = result.Data.EngineId ?? SelectedProfile.Engine,
                    Language = SelectedProfile.Language,
                    CreatedAt = DateTime.Now,
                };
                
                AllProfiles.Add(clonedProfile);
                ApplyFilters();
                SelectedProfile = clonedProfile;
                
                StatusMessage = $"Cloned profile: {clonedProfile.Name}";
            }
            else
            {
                await HandleErrorAsync(result.Error?.Message ?? "Failed to clone profile", "Clone error", showDialog: false);
            }
        }
        catch (Exception ex)
        {
            await HandleErrorAsync(ex, "Failed to clone voice profile");
        }
    }

    private async Task ImportVoiceAsync()
    {
        try
        {
            // Look for export files in the standard directory
            var importDir = Path.Combine(
                Environment.GetFolderPath(Environment.SpecialFolder.MyDocuments),
                "VoiceStudio", "ExportedProfiles");
            
            if (!Directory.Exists(importDir))
            {
                StatusMessage = "No exported profiles directory found";
                return;
            }
            
            var files = Directory.GetFiles(importDir, "*.vsprofile")
                .OrderByDescending(f => File.GetCreationTime(f))
                .ToArray();
            
            if (files.Length == 0)
            {
                StatusMessage = "No profile files found in export directory";
                return;
            }
            
            // Import the most recent file
            var filePath = files[0];
            
            await using var fileStream = File.OpenRead(filePath);
            var result = await _profileGateway.ImportAsync(fileStream, Path.GetFileName(filePath));
            
            if (result.Success && result.Data != null)
            {
                var importedProfile = new VoiceProfileData
                {
                    Id = result.Data.Id,
                    Name = result.Data.Name,
                    Description = result.Data.Description ?? "",
                    Source = VoiceSource.Imported,
                    Engine = result.Data.EngineId ?? "",
                    CreatedAt = DateTime.Now,
                };
                
                AllProfiles.Add(importedProfile);
                ApplyFilters();
                SelectedProfile = importedProfile;
                
                StatusMessage = $"Imported profile: {importedProfile.Name}";
            }
            else
            {
                await HandleErrorAsync(result.Error?.Message ?? "Failed to import profile", "Import error", showDialog: false);
            }
        }
        catch (Exception ex)
        {
            await HandleErrorAsync(ex, "Failed to import voice profile");
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
            var exportDir = Path.Combine(
                Environment.GetFolderPath(Environment.SpecialFolder.MyDocuments),
                "VoiceStudio", "ExportedProfiles");
            
            Directory.CreateDirectory(exportDir);
            
            var fileName = $"{SelectedProfile.Name.Replace(" ", "_")}_{DateTime.Now:yyyyMMdd_HHmmss}.vsprofile";
            var filePath = Path.Combine(exportDir, fileName);
            
            await using var fileStream = File.Create(filePath);
            var result = await _profileGateway.ExportAsync(SelectedProfile.Id, fileStream);
            
            if (result.Success)
            {
                StatusMessage = $"Exported profile to: {filePath}";
            }
            else
            {
                await HandleErrorAsync(result.Error?.Message ?? "Failed to export profile", "Export error", showDialog: false);
            }
        }
        catch (Exception ex)
        {
            await HandleErrorAsync(ex, "Failed to export voice profile");
        }
    }

    private async Task DeleteVoiceAsync()
    {
        if (SelectedProfile == null || SelectedProfile.Source == VoiceSource.Builtin)
        {
            return;
        }
        
        try
        {
            var result = await _profileGateway.DeleteAsync(SelectedProfile.Id);
            
            if (result.Success)
            {
                var deletedName = SelectedProfile.Name;
                AllProfiles.Remove(SelectedProfile);
                SelectedProfile = null;
                ApplyFilters();
                
                StatusMessage = $"Deleted profile: {deletedName}";
            }
            else
            {
                await HandleErrorAsync(result.Error?.Message ?? "Failed to delete profile", "Delete error", showDialog: false);
            }
        }
        catch (Exception ex)
        {
            await HandleErrorAsync(ex, "Failed to delete voice profile");
        }
    }

    private async Task PlaySampleAsync()
    {
        if (SelectedProfile?.SampleAudioPath == null)
        {
            return;
        }
        
        try
        {
            StatusMessage = "Playing sample...";
            
            // In a real implementation, use IAudioPlayerService
            await Task.Delay(1000);
            
            SelectedProfile.LastUsed = DateTime.Now;
            StatusMessage = "Ready";
        }
        catch (Exception ex)
        {
            await HandleErrorAsync(ex, "Failed to play voice sample");
        }
    }

    private void ToggleFavorite()
    {
        if (SelectedProfile != null)
        {
            SelectedProfile.IsFavorite = !SelectedProfile.IsFavorite;
            
            if (ShowFavoritesOnly)
            {
                ApplyFilters();
            }
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
}
