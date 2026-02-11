using System;
using System.Collections.Generic;
using System.IO;
using System.Threading;
using System.Threading.Tasks;

namespace VoiceStudio.Core.Gateways
{
  /// <summary>
  /// Gateway for audio file operations, streaming, and waveform analysis.
  /// </summary>
  public interface IAudioGateway
  {
    /// <summary>
    /// Uploads an audio file to the backend.
    /// </summary>
    /// <param name="fileStream">The audio file stream.</param>
    /// <param name="fileName">The file name.</param>
    /// <param name="progress">Optional progress callback.</param>
    /// <param name="cancellationToken">Cancellation token.</param>
    /// <returns>Result containing the uploaded audio info or error.</returns>
    Task<GatewayResult<AudioFileInfo>> UploadAsync(
        Stream fileStream,
        string fileName,
        Action<long, long>? progress = null,
        CancellationToken cancellationToken = default);

    /// <summary>
    /// Downloads an audio file from the backend.
    /// </summary>
    /// <param name="audioId">The audio identifier.</param>
    /// <param name="outputStream">The stream to write to.</param>
    /// <param name="progress">Optional progress callback.</param>
    /// <param name="cancellationToken">Cancellation token.</param>
    /// <returns>Result indicating success or error.</returns>
    Task<GatewayResult<bool>> DownloadAsync(
        string audioId,
        Stream outputStream,
        Action<long, long>? progress = null,
        CancellationToken cancellationToken = default);

    /// <summary>
    /// Gets audio file metadata.
    /// </summary>
    /// <param name="audioId">The audio identifier.</param>
    /// <param name="cancellationToken">Cancellation token.</param>
    /// <returns>Result containing the audio info or error.</returns>
    Task<GatewayResult<AudioFileInfo>> GetInfoAsync(
        string audioId,
        CancellationToken cancellationToken = default);

    /// <summary>
    /// Generates waveform data for visualization.
    /// </summary>
    /// <param name="audioId">The audio identifier.</param>
    /// <param name="samplesPerSecond">Number of samples per second for the waveform.</param>
    /// <param name="cancellationToken">Cancellation token.</param>
    /// <returns>Result containing the waveform data or error.</returns>
    Task<GatewayResult<WaveformData>> GetWaveformAsync(
        string audioId,
        int samplesPerSecond = 100,
        CancellationToken cancellationToken = default);

    /// <summary>
    /// Deletes an audio file.
    /// </summary>
    /// <param name="audioId">The audio identifier.</param>
    /// <param name="cancellationToken">Cancellation token.</param>
    /// <returns>Result indicating success or error.</returns>
    Task<GatewayResult<bool>> DeleteAsync(
        string audioId,
        CancellationToken cancellationToken = default);

    /// <summary>
    /// Converts audio to a different format.
    /// </summary>
    /// <param name="audioId">The audio identifier.</param>
    /// <param name="targetFormat">The target format (e.g., "wav", "mp3", "ogg").</param>
    /// <param name="cancellationToken">Cancellation token.</param>
    /// <returns>Result containing the converted audio info or error.</returns>
    Task<GatewayResult<AudioFileInfo>> ConvertAsync(
        string audioId,
        string targetFormat,
        CancellationToken cancellationToken = default);

    /// <summary>
    /// Streams audio for playback.
    /// </summary>
    /// <param name="audioId">The audio identifier.</param>
    /// <param name="cancellationToken">Cancellation token.</param>
    /// <returns>Result containing the audio stream or error.</returns>
    Task<GatewayResult<Stream>> StreamAsync(
        string audioId,
        CancellationToken cancellationToken = default);
  }

  #region Models

  /// <summary>
  /// Information about an audio file.
  /// </summary>
  public sealed class AudioFileInfo
  {
    public string Id { get; set; } = string.Empty;
    public string FileName { get; set; } = string.Empty;
    public string Format { get; set; } = string.Empty;
    public long SizeBytes { get; set; }
    public double DurationSeconds { get; set; }
    public int SampleRate { get; set; }
    public int Channels { get; set; }
    public int BitDepth { get; set; }
    public DateTime CreatedAt { get; set; }
    public string? Path { get; set; }
  }

  /// <summary>
  /// Waveform data for visualization.
  /// </summary>
  public sealed class WaveformData
  {
    public string AudioId { get; set; } = string.Empty;
    public int SamplesPerSecond { get; set; }
    public double DurationSeconds { get; set; }
    public IReadOnlyList<float> Samples { get; set; } = new List<float>();
    public float Min { get; set; }
    public float Max { get; set; }
  }

  #endregion
}
