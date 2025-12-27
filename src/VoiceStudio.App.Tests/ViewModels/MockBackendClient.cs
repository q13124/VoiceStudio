using System;
using System.Collections.Generic;
using System.IO;
using System.Threading;
using System.Threading.Tasks;
using VoiceStudio.Core.Models;
using VoiceStudio.Core.Services;

namespace VoiceStudio.App.Tests.ViewModels
{
    /// <summary>
    /// Mock implementation of IBackendClient for testing GlobalSearchViewModel.
    /// Only SearchAsync is fully implemented; other methods throw NotImplementedException.
    /// </summary>
    public partial class MockBackendClient : IBackendClient
    {
        public SearchResponse? SearchResponse { get; set; }
        public Exception? SearchException { get; set; }
        public int SearchCallCount { get; private set; }
        public string? LastSearchQuery { get; private set; }

        public Task<SearchResponse> SearchAsync(string query, string? types = null, int limit = 50, CancellationToken cancellationToken = default)
        {
            SearchCallCount++;
            LastSearchQuery = query;

            if (SearchException != null)
            {
                throw SearchException;
            }

            return Task.FromResult(SearchResponse ?? new SearchResponse
            {
                Results = new List<SearchResultItem>(),
                TotalResults = 0,
                ResultsByType = new Dictionary<string, int>()
            });
        }

        // All other interface members are stubs that throw NotImplementedException
        // These are not used in GlobalSearchViewModel tests
        // Implemented in MockBackendClient.Stubs.cs for maintainability
    }

    /// <summary>
    /// Partial class containing all IBackendClient interface stub implementations.
    /// Separated for maintainability due to large number of interface members.
    /// </summary>
    public partial class MockBackendClient
    {
        public IWebSocketService? WebSocketService => null;

        public Task<TResponse> SendRequestAsync<TRequest, TResponse>(string endpoint, TRequest request, CancellationToken cancellationToken = default)
            => throw new NotImplementedException("Not used in GlobalSearchViewModel tests");

        public Task<TResponse> SendMcpOperationAsync<TRequest, TResponse>(string operation, TRequest payload, CancellationToken cancellationToken = default)
            => throw new NotImplementedException("Not used in GlobalSearchViewModel tests");

        public Task<bool> CheckHealthAsync(CancellationToken cancellationToken = default)
            => throw new NotImplementedException("Not used in GlobalSearchViewModel tests");

        // Voice cloning endpoints
        public Task<VoiceSynthesisResponse> SynthesizeVoiceAsync(VoiceSynthesisRequest request, CancellationToken cancellationToken = default)
            => throw new NotImplementedException("Not used in GlobalSearchViewModel tests");

        public Task<VoiceAnalysisResponse> AnalyzeVoiceAsync(Stream audioFile, string? metrics = null, CancellationToken cancellationToken = default)
            => throw new NotImplementedException("Not used in GlobalSearchViewModel tests");

        public Task<VoiceCloneResponse> CloneVoiceAsync(Stream referenceAudio, VoiceCloneRequest request, CancellationToken cancellationToken = default)
            => throw new NotImplementedException("Not used in GlobalSearchViewModel tests");

        // Profile management
        public Task<List<VoiceProfile>> GetProfilesAsync(CancellationToken cancellationToken = default)
            => throw new NotImplementedException("Not used in GlobalSearchViewModel tests");

        public Task<VoiceProfile> GetProfileAsync(string profileId, CancellationToken cancellationToken = default)
            => throw new NotImplementedException("Not used in GlobalSearchViewModel tests");

        public Task<VoiceProfile> CreateProfileAsync(string name, string language = "en", string? emotion = null, List<string>? tags = null, CancellationToken cancellationToken = default)
            => throw new NotImplementedException("Not used in GlobalSearchViewModel tests");

        public Task<VoiceProfile> UpdateProfileAsync(string profileId, string? name = null, string? language = null, string? emotion = null, List<string>? tags = null, CancellationToken cancellationToken = default)
            => throw new NotImplementedException("Not used in GlobalSearchViewModel tests");

        public Task<bool> DeleteProfileAsync(string profileId, CancellationToken cancellationToken = default)
            => throw new NotImplementedException("Not used in GlobalSearchViewModel tests");

        // Project management
        public Task<List<Project>> GetProjectsAsync(CancellationToken cancellationToken = default)
            => throw new NotImplementedException("Not used in GlobalSearchViewModel tests");

        public Task<Project> GetProjectAsync(string projectId, CancellationToken cancellationToken = default)
            => throw new NotImplementedException("Not used in GlobalSearchViewModel tests");

        public Task<Project> CreateProjectAsync(string name, string? description = null, CancellationToken cancellationToken = default)
            => throw new NotImplementedException("Not used in GlobalSearchViewModel tests");

        public Task<Project> UpdateProjectAsync(string projectId, string? name = null, string? description = null, List<string>? voiceProfileIds = null, CancellationToken cancellationToken = default)
            => throw new NotImplementedException("Not used in GlobalSearchViewModel tests");

        public Task<bool> DeleteProjectAsync(string projectId, CancellationToken cancellationToken = default)
            => throw new NotImplementedException("Not used in GlobalSearchViewModel tests");

        // Note: IBackendClient has 100+ methods. For GlobalSearchViewModel tests, only SearchAsync is needed.
        // Remaining methods can be added as stubs if compilation errors occur.
        // Pattern: public Task<ReturnType> MethodName(...) => throw new NotImplementedException("Not used in GlobalSearchViewModel tests");
    }
}
