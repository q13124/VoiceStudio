// VoiceStudio - Audio Export Request/Response Models

using System.Text.Json.Serialization;

namespace VoiceStudio.App.Core.Models;

/// <summary>
/// Request model for audio export API.
/// </summary>
public sealed class AudioExportRequest
{
    /// <summary>
    /// Source audio identifier (audio ID from upload or project).
    /// </summary>
    [JsonPropertyName("source")]
    public string Source { get; init; } = string.Empty;

    /// <summary>
    /// Target format (e.g., "mp3", "wav", "flac").
    /// </summary>
    [JsonPropertyName("format")]
    public string Format { get; init; } = "wav";

    /// <summary>
    /// Sample rate in Hz (optional, null uses source sample rate).
    /// </summary>
    [JsonPropertyName("sample_rate")]
    public int? SampleRate { get; init; }

    /// <summary>
    /// Number of audio channels (optional, null uses source channels).
    /// </summary>
    [JsonPropertyName("channels")]
    public int? Channels { get; init; }

    /// <summary>
    /// Bitrate in kbps for lossy formats (optional).
    /// </summary>
    [JsonPropertyName("bitrate_kbps")]
    public int? BitrateKbps { get; init; }

    /// <summary>
    /// Whether to normalize audio (optional, default false).
    /// </summary>
    [JsonPropertyName("normalize")]
    public bool? Normalize { get; init; }
}

/// <summary>
/// Response model for audio export API (metadata only, actual file is streamed).
/// </summary>
public sealed class AudioExportResponse
{
    /// <summary>
    /// Whether the export was successful.
    /// </summary>
    [JsonPropertyName("success")]
    public bool Success { get; init; }

    /// <summary>
    /// Suggested filename for the exported file.
    /// </summary>
    [JsonPropertyName("filename")]
    public string? Filename { get; init; }

    /// <summary>
    /// Format of the exported file.
    /// </summary>
    [JsonPropertyName("format")]
    public string? Format { get; init; }

    /// <summary>
    /// Size of the exported file in bytes.
    /// </summary>
    [JsonPropertyName("size_bytes")]
    public long? SizeBytes { get; init; }

    /// <summary>
    /// Error message if export failed.
    /// </summary>
    [JsonPropertyName("error")]
    public string? Error { get; init; }
}

/// <summary>
/// Information about a supported audio format (from /api/audio/formats).
/// </summary>
public sealed class AudioFormatInfo
{
    [JsonPropertyName("id")]
    public string Id { get; init; } = string.Empty;

    [JsonPropertyName("name")]
    public string Name { get; init; } = string.Empty;

    [JsonPropertyName("description")]
    public string Description { get; init; } = string.Empty;

    [JsonPropertyName("extensions")]
    public string[] Extensions { get; init; } = [];

    [JsonPropertyName("mime_types")]
    public string[] MimeTypes { get; init; } = [];

    [JsonPropertyName("is_lossy")]
    public bool IsLossy { get; init; }

    [JsonPropertyName("default_bitrate_kbps")]
    public int? DefaultBitrateKbps { get; init; }
}
