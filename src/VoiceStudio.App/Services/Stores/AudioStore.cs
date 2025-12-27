using System;
using System.Collections.ObjectModel;
using System.Linq;
using System.Threading.Tasks;
using CommunityToolkit.Mvvm.ComponentModel;
using VoiceStudio.Core.Models;
using VoiceStudio.Core.Services;

namespace VoiceStudio.App.Services.Stores
{
    /// <summary>
    /// Centralized store for audio-related state.
    /// Implements React/TypeScript audioStore pattern in C#.
    /// </summary>
    public partial class AudioStore : ObservableObject
    {
        private readonly IBackendClient _backendClient;
        private readonly StateCacheService? _stateCacheService;

        [ObservableProperty]
        private ObservableCollection<AudioClip> audioClips = new();

        [ObservableProperty]
        private ObservableCollection<ProjectAudioFile> audioFiles = new();

        [ObservableProperty]
        private AudioClip? selectedClip;

        [ObservableProperty]
        private ProjectAudioFile? selectedFile;

        [ObservableProperty]
        private bool isLoading = false;

        [ObservableProperty]
        private string? errorMessage;

        [ObservableProperty]
        private DateTime? lastUpdated;

        public AudioStore(IBackendClient backendClient, StateCacheService? stateCacheService = null)
        {
            _backendClient = backendClient ?? throw new ArgumentNullException(nameof(backendClient));
            _stateCacheService = stateCacheService;
        }

        /// <summary>
        /// Loads all audio clips for a project.
        /// </summary>
        public async Task LoadAudioClipsAsync(string projectId)
        {
            try
            {
                IsLoading = true;
                ErrorMessage = null;

                // Try to load from cache first
                if (_stateCacheService != null)
                {
                    var cached = await _stateCacheService.GetCachedStateAsync<ObservableCollection<AudioClip>>($"audio_clips_{projectId}");
                    if (cached != null)
                    {
                        AudioClips = cached;
                        IsLoading = false;
                        // Still fetch from backend in background to update
                        _ = RefreshAudioClipsAsync(projectId);
                        return;
                    }
                }

                await RefreshAudioClipsAsync(projectId);
            }
            catch (Exception ex)
            {
                ErrorMessage = $"Failed to load audio clips: {ex.Message}";
            }
            finally
            {
                IsLoading = false;
            }
        }

        /// <summary>
        /// Refreshes audio clips from backend.
        /// </summary>
        public async Task RefreshAudioClipsAsync(string projectId)
        {
            try
            {
                // Get tracks for the project, then get clips from each track
                var tracks = await _backendClient.GetTracksAsync(projectId);
                
                AudioClips.Clear();
                foreach (var track in tracks)
                {
                    // Tracks contain clips, so add them
                    if (track.Clips != null)
                    {
                        foreach (var clip in track.Clips)
                        {
                            AudioClips.Add(clip);
                        }
                    }
                }

                LastUpdated = DateTime.UtcNow;

                // Cache the result
                if (_stateCacheService != null)
                {
                    await _stateCacheService.CacheStateAsync($"audio_clips_{projectId}", AudioClips);
                }
            }
            catch (Exception ex)
            {
                ErrorMessage = $"Failed to refresh audio clips: {ex.Message}";
            }
        }

        /// <summary>
        /// Loads audio files from library.
        /// </summary>
        public async Task LoadAudioFilesAsync()
        {
            try
            {
                IsLoading = true;
                ErrorMessage = null;

                // Try to load from cache first
                if (_stateCacheService != null)
                {
                    var cached = await _stateCacheService.GetCachedStateAsync<ObservableCollection<ProjectAudioFile>>("audio_files");
                    if (cached != null)
                    {
                        AudioFiles = cached;
                        IsLoading = false;
                        // Still fetch from backend in background to update
                        _ = RefreshAudioFilesAsync();
                        return;
                    }
                }

                await RefreshAudioFilesAsync();
            }
            catch (Exception ex)
            {
                ErrorMessage = $"Failed to load audio files: {ex.Message}";
            }
            finally
            {
                IsLoading = false;
            }
        }

        /// <summary>
        /// Refreshes audio files from backend.
        /// </summary>
        public async Task RefreshAudioFilesAsync()
        {
            try
            {
                // Use ListProjectAudioAsync or a similar method
                // For now, we'll use a generic approach - this may need to be adjusted based on actual API
                // Audio files might be retrieved from project audio persistence
                // This is a placeholder that can be updated when the actual library API is available
                
                AudioFiles.Clear();
                // Note: Library API not yet available.
                // Audio files are currently retrieved from project audio persistence (ListProjectAudioAsync).
                // This will be updated when the general library API is implemented.
                // For now, use ListProjectAudioAsync with a specific project ID to retrieve audio files.
                // See: IBackendClient.ListProjectAudioAsync() for current implementation.

                LastUpdated = DateTime.UtcNow;

                // Cache the result
                if (_stateCacheService != null)
                {
                    await _stateCacheService.CacheStateAsync("audio_files", AudioFiles);
                }
            }
            catch (Exception ex)
            {
                ErrorMessage = $"Failed to refresh audio files: {ex.Message}";
            }
        }

        /// <summary>
        /// Adds an audio clip to the store.
        /// </summary>
        public void AddAudioClip(AudioClip clip)
        {
            if (!AudioClips.Any(c => c.Id == clip.Id))
            {
                AudioClips.Add(clip);
                LastUpdated = DateTime.UtcNow;
            }
        }

        /// <summary>
        /// Removes an audio clip from the store.
        /// </summary>
        public void RemoveAudioClip(string clipId)
        {
            var clip = AudioClips.FirstOrDefault(c => c.Id == clipId);
            if (clip != null)
            {
                AudioClips.Remove(clip);
                LastUpdated = DateTime.UtcNow;
            }
        }

        /// <summary>
        /// Updates an audio clip in the store.
        /// </summary>
        public void UpdateAudioClip(AudioClip clip)
        {
            var existing = AudioClips.FirstOrDefault(c => c.Id == clip.Id);
            if (existing != null)
            {
                var index = AudioClips.IndexOf(existing);
                AudioClips[index] = clip;
                LastUpdated = DateTime.UtcNow;
            }
        }

        /// <summary>
        /// Clears all audio state.
        /// </summary>
        public void Clear()
        {
            AudioClips.Clear();
            AudioFiles.Clear();
            SelectedClip = null;
            SelectedFile = null;
            LastUpdated = null;
        }
    }
}

