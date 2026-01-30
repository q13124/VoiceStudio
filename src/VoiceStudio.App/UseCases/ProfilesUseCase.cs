using System.Collections.Generic;
using System.Threading;
using System.Threading.Tasks;
using VoiceStudio.Core.Models;
using VoiceStudio.Core.Services;

namespace VoiceStudio.App.UseCases
{
    /// <summary>
    /// Use case implementation that delegates profile operations to the backend via IBackendClient.
    /// </summary>
    public sealed class ProfilesUseCase : IProfilesUseCase
    {
        private readonly IBackendClient _backendClient;

        public ProfilesUseCase(IBackendClient backendClient)
        {
            _backendClient = backendClient ?? throw new System.ArgumentNullException(nameof(backendClient));
        }

        public async Task<IReadOnlyList<VoiceProfile>> ListAsync(CancellationToken cancellationToken = default)
        {
            var list = await _backendClient.GetProfilesAsync(cancellationToken).ConfigureAwait(false);
            return list ?? new List<VoiceProfile>();
        }

        public Task<VoiceProfile?> CreateAsync(string name, CancellationToken cancellationToken = default)
        {
            return _backendClient.CreateProfileAsync(name, "en", null, null, cancellationToken);
        }

        public Task<VoiceProfile?> CreateAsync(string name, string? language, string? emotion, List<string>? tags, CancellationToken cancellationToken = default)
        {
            return _backendClient.CreateProfileAsync(name, language ?? "en", emotion, tags, cancellationToken);
        }

        public Task<VoiceProfile?> UpdateAsync(string profileId, string? name, string? language, string? emotion, List<string>? tags, CancellationToken cancellationToken = default)
        {
            return _backendClient.UpdateProfileAsync(profileId, name, language, emotion, tags, cancellationToken);
        }

        public Task<bool> DeleteAsync(string profileId, CancellationToken cancellationToken = default)
        {
            return _backendClient.DeleteProfileAsync(profileId, cancellationToken);
        }
    }
}
