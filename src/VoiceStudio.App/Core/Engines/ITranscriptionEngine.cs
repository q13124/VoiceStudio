using System.Threading;
using System.Threading.Tasks;
using VoiceStudio.Core.Models;

namespace VoiceStudio.Core.Engines
{
  /// <summary>
  /// Interface for Speech-to-Text (Transcription) engines.
  /// </summary>
  public interface ITranscriptionEngine : IEngine
  {
    /// <summary>
    /// Transcribes an audio clip.
    /// </summary>
    /// <param name="audioClipId">ID of the audio clip to transcribe.</param>
    /// <param name="language">Optional language code (e.g. "en").</param>
    /// <param name="cancellationToken">Cancellation token.</param>
    /// <returns>The transcription result.</returns>
    Task<TranscriptionResponse> TranscribeAsync(string audioClipId, string? language = null, CancellationToken cancellationToken = default);
  }
}