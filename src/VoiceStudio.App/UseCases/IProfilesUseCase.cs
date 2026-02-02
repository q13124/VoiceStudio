using System.Collections.Generic;
using System.Threading;
using System.Threading.Tasks;
using VoiceStudio.Core.Models;

namespace VoiceStudio.App.UseCases
{
    /// <summary>
    /// Use case for voice profile list, create, update, and delete operations.
    /// </summary>
    public interface IProfilesUseCase
    {
        Task<IReadOnlyList<VoiceProfile>> ListAsync(CancellationToken cancellationToken = default);
        Task<VoiceProfile> CreateAsync(string name, CancellationToken cancellationToken = default);
        Task<VoiceProfile> CreateAsync(string name, string? language, string? emotion, List<string>? tags, CancellationToken cancellationToken = default);
        Task<VoiceProfile> UpdateAsync(string profileId, string? name, string? language, string? emotion, List<string>? tags, CancellationToken cancellationToken = default);
        Task<bool> DeleteAsync(string profileId, CancellationToken cancellationToken = default);
    }
}
