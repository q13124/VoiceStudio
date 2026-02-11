using System.Collections.Generic;
using System.IO;
using System.Threading;
using System.Threading.Tasks;

namespace VoiceStudio.Core.Gateways
{
  /// <summary>
  /// Gateway for voice synthesis, cloning, and analysis operations.
  /// </summary>
  public interface IVoiceGateway
  {
    /// <summary>
    /// Synthesizes text to speech.
    /// </summary>
    /// <param name="request">The synthesis request.</param>
    /// <param name="cancellationToken">Cancellation token.</param>
    /// <returns>Result containing the audio clip info or error.</returns>
    Task<GatewayResult<VoiceSynthesisResult>> SynthesizeAsync(
        VoiceSynthesisRequest request,
        CancellationToken cancellationToken = default);

    /// <summary>
    /// Synthesizes text to speech with streaming output.
    /// </summary>
    /// <param name="request">The synthesis request.</param>
    /// <param name="outputStream">The stream to write audio chunks to.</param>
    /// <param name="cancellationToken">Cancellation token.</param>
    /// <returns>Result indicating success or error.</returns>
    Task<GatewayResult<bool>> SynthesizeStreamAsync(
        VoiceSynthesisRequest request,
        Stream outputStream,
        CancellationToken cancellationToken = default);

    /// <summary>
    /// Clones a voice from audio samples.
    /// </summary>
    /// <param name="request">The cloning request.</param>
    /// <param name="cancellationToken">Cancellation token.</param>
    /// <returns>Result containing the cloned voice profile or error.</returns>
    Task<GatewayResult<VoiceCloneResult>> CloneVoiceAsync(
        VoiceCloneRequest request,
        CancellationToken cancellationToken = default);

    /// <summary>
    /// Analyzes audio for voice characteristics.
    /// </summary>
    /// <param name="audioPath">Path to the audio file.</param>
    /// <param name="cancellationToken">Cancellation token.</param>
    /// <returns>Result containing the analysis or error.</returns>
    Task<GatewayResult<VoiceAnalysisResult>> AnalyzeAsync(
        string audioPath,
        CancellationToken cancellationToken = default);

    /// <summary>
    /// Gets available voices for the specified engine.
    /// </summary>
    /// <param name="engineId">The engine identifier (optional, defaults to active engine).</param>
    /// <param name="cancellationToken">Cancellation token.</param>
    /// <returns>Result containing the available voices or error.</returns>
    Task<GatewayResult<IReadOnlyList<VoiceInfo>>> GetAvailableVoicesAsync(
        string? engineId = null,
        CancellationToken cancellationToken = default);
  }

  #region Request/Response Models

  /// <summary>
  /// Request for voice synthesis.
  /// </summary>
  public sealed class VoiceSynthesisRequest
  {
    public string Text { get; set; } = string.Empty;
    public string? VoiceId { get; set; }
    public string? ProfileId { get; set; }
    public string? EngineId { get; set; }
    public string Language { get; set; } = "en";
    public float Speed { get; set; } = 1.0f;
    public float Pitch { get; set; } = 1.0f;
    public Dictionary<string, object>? EngineParameters { get; set; }
  }

  /// <summary>
  /// Result of voice synthesis.
  /// </summary>
  public sealed class VoiceSynthesisResult
  {
    public string AudioPath { get; set; } = string.Empty;
    public string AudioId { get; set; } = string.Empty;
    public double DurationSeconds { get; set; }
    public int SampleRate { get; set; }
    public string Format { get; set; } = "wav";
  }

  /// <summary>
  /// Request for voice cloning.
  /// </summary>
  public sealed class VoiceCloneRequest
  {
    public string Name { get; set; } = string.Empty;
    public IReadOnlyList<string> AudioSamplePaths { get; set; } = new List<string>();
    public string? Description { get; set; }
    public string? EngineId { get; set; }
  }

  /// <summary>
  /// Result of voice cloning.
  /// </summary>
  public sealed class VoiceCloneResult
  {
    public string VoiceId { get; set; } = string.Empty;
    public string ProfileId { get; set; } = string.Empty;
    public string Name { get; set; } = string.Empty;
  }

  /// <summary>
  /// Result of voice analysis.
  /// </summary>
  public sealed class VoiceAnalysisResult
  {
    public double Pitch { get; set; }
    public double Energy { get; set; }
    public double SpeechRate { get; set; }
    public string? DetectedLanguage { get; set; }
    public string? DetectedGender { get; set; }
    public Dictionary<string, double>? Characteristics { get; set; }
  }

  /// <summary>
  /// Information about an available voice.
  /// </summary>
  public sealed class VoiceInfo
  {
    public string Id { get; set; } = string.Empty;
    public string Name { get; set; } = string.Empty;
    public string? Description { get; set; }
    public string? Language { get; set; }
    public string? Gender { get; set; }
    public string? EngineId { get; set; }
    public bool IsCloned { get; set; }
  }

  #endregion
}
