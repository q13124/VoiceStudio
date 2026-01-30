using System;
using System.Collections.ObjectModel;
using System.Linq;
using System.Threading.Tasks;
using CommunityToolkit.Mvvm.ComponentModel;
// using VoiceStudio.App.Services.Persistence;  // Commented - namespace missing
using VoiceStudio.Core.Models;
using VoiceStudio.Core.Services;

namespace VoiceStudio.App.Services.Stores
{
    /// <summary>
    /// Centralized store for project-related state.
    /// Implements React/TypeScript projectStore pattern in C#.
    /// </summary>
    public partial class ProjectStore : ObservableObject
    {
        private readonly IBackendClient _backendClient;
        private readonly StateCacheService? _stateCacheService;
        private readonly IProjectRepository? _projectRepository;

        [ObservableProperty]
        private ObservableCollection<Project> projects = new();

        [ObservableProperty]
        private Project? currentProject;

        [ObservableProperty]
        private Project? selectedProject;

        [ObservableProperty]
        private bool isLoading = false;

        [ObservableProperty]
        private string? errorMessage;

        [ObservableProperty]
        private DateTime? lastUpdated;

        public ProjectStore(
            IBackendClient backendClient,
            StateCacheService? stateCacheService = null,
            IProjectRepository? projectRepository = null)
        {
            _backendClient = backendClient ?? throw new ArgumentNullException(nameof(backendClient));
            _stateCacheService = stateCacheService;
            _projectRepository = projectRepository;
        }

        /// <summary>
        /// Loads all projects.
        /// </summary>
        public async Task LoadProjectsAsync()
        {
            try
            {
                IsLoading = true;
                ErrorMessage = null;

                // Try to load from cache first
                if (_stateCacheService != null)
                {
                    var cached = await _stateCacheService.GetCachedStateAsync<ObservableCollection<Project>>("projects");
                    if (cached != null)
                    {
                        Projects = cached;
                        IsLoading = false;
                        // Still fetch from backend in background to update
                        _ = RefreshProjectsAsync();
                        return;
                    }
                }

                await RefreshProjectsAsync();
            }
            catch (Exception ex)
            {
                ErrorMessage = $"Failed to load projects: {ex.Message}";
            }
            finally
            {
                IsLoading = false;
            }
        }

        /// <summary>
        /// Refreshes projects from backend.
        /// </summary>
        public async Task RefreshProjectsAsync()
        {
            try
            {
                if (_projectRepository != null)
                {
                    var localProjects = await _projectRepository.ListProjectsAsync();
                    Projects = new ObservableCollection<Project>(
                        localProjects.Select(MapMetadataToProject));

                    LastUpdated = DateTime.UtcNow;

                    if (_stateCacheService != null)
                    {
                        await _stateCacheService.CacheStateAsync("projects", Projects);
                    }

                    if (Projects.Count > 0)
                    {
                        return;
                    }
                }

                var projectsArray = await _backendClient.GetProjectsAsync();

                Projects.Clear();
                if (projectsArray != null)
                {
                    foreach (var project in projectsArray)
                    {
                        Projects.Add(project);
                    }
                }

                LastUpdated = DateTime.UtcNow;

                // Cache the result
                if (_stateCacheService != null)
                {
                    await _stateCacheService.CacheStateAsync("projects", Projects);
                }
            }
            catch (Exception ex)
            {
                ErrorMessage = $"Failed to refresh projects: {ex.Message}";
            }
        }

        /// <summary>
        /// Loads a specific project and sets it as current.
        /// </summary>
        public async Task LoadProjectAsync(string projectId)
        {
            try
            {
                IsLoading = true;
                ErrorMessage = null;

                Project? project = null;
                if (_projectRepository != null)
                {
                    try
                    {
                        var localProjects = await _projectRepository.ListProjectsAsync();
                        var localMatch = localProjects.FirstOrDefault(p => p.ProjectId == projectId);
                        if (localMatch != null)
                        {
                            var localProject = await _projectRepository.OpenAsync(localMatch.Path);
                            project = MapDataToProject(localProject);
                        }
                    }
                    catch (Exception)
                    {
                        // Fallback to backend
                    }
                }

                project ??= await _backendClient.GetProjectAsync(projectId);
                if (project != null)
                {
                    CurrentProject = project;
                    
                    // Update in projects list if it exists
                    var existing = Projects.FirstOrDefault(p => p.Id == projectId);
                    if (existing != null)
                    {
                        var index = Projects.IndexOf(existing);
                        Projects[index] = project;
                    }
                    else
                    {
                        Projects.Add(project);
                    }

                    LastUpdated = DateTime.UtcNow;
                }
            }
            catch (Exception ex)
            {
                ErrorMessage = $"Failed to load project: {ex.Message}";
            }
            finally
            {
                IsLoading = false;
            }
        }

        /// <summary>
        /// Adds a project to the store.
        /// </summary>
        public void AddProject(Project project)
        {
            if (!Projects.Any(p => p.Id == project.Id))
            {
                Projects.Add(project);
                LastUpdated = DateTime.UtcNow;
            }
        }

        /// <summary>
        /// Removes a project from the store.
        /// </summary>
        public void RemoveProject(string projectId)
        {
            var project = Projects.FirstOrDefault(p => p.Id == projectId);
            if (project != null)
            {
                Projects.Remove(project);
                
                // Clear current project if it was removed
                if (CurrentProject?.Id == projectId)
                {
                    CurrentProject = null;
                }
                
                LastUpdated = DateTime.UtcNow;
            }
        }

        /// <summary>
        /// Updates a project in the store.
        /// </summary>
        public void UpdateProject(Project project)
        {
            var existing = Projects.FirstOrDefault(p => p.Id == project.Id);
            if (existing != null)
            {
                var index = Projects.IndexOf(existing);
                Projects[index] = project;
                
                // Update current project if it's the same
                if (CurrentProject?.Id == project.Id)
                {
                    CurrentProject = project;
                }
                
                LastUpdated = DateTime.UtcNow;
            }
        }

        /// <summary>
        /// Sets the current project.
        /// </summary>
        public void SetCurrentProject(string projectId)
        {
            CurrentProject = Projects.FirstOrDefault(p => p.Id == projectId);
        }

        /// <summary>
        /// Clears all project state.
        /// </summary>
        public void Clear()
        {
            Projects.Clear();
            CurrentProject = null;
            SelectedProject = null;
            LastUpdated = null;
        }

        private static Project MapMetadataToProject(ProjectMetadata metadata)
        {
            return new Project
            {
                Id = metadata.ProjectId,
                Name = metadata.Name,
                Description = string.Empty,
                CreatedAt = metadata.CreatedAt.UtcDateTime.ToString("o"),
                UpdatedAt = metadata.ModifiedAt.UtcDateTime.ToString("o")
            };
        }

        private static Project MapDataToProject(ProjectData data)
        {
            return new Project
            {
                Id = data.ProjectId,
                Name = data.Name,
                Description = string.Empty,
                CreatedAt = data.CreatedAt.UtcDateTime.ToString("o"),
                UpdatedAt = data.ModifiedAt.UtcDateTime.ToString("o")
            };
        }
    }
}

