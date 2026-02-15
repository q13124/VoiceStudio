// VoiceStudio - Audio File Formats
// Centralized audio format definitions for UI components
// Mirrors backend/core/audio/formats.py for consistency

using System.Collections.Frozen;
using System.Collections.Immutable;

namespace VoiceStudio.App.Core.Audio;

/// <summary>
/// Supported audio formats in VoiceStudio.
/// </summary>
public enum AudioFormat
{
    Wav,
    Mp3,
    Flac,
    Ogg,
    Opus,
    M4A,
    Aac,
    Wma,
    Aiff
}

/// <summary>
/// Information about an audio format.
/// </summary>
public sealed record AudioFormatInfo(
    AudioFormat Format,
    string Name,
    string Description,
    ImmutableArray<string> Extensions,
    ImmutableArray<string> MimeTypes,
    bool IsLossy,
    bool SupportsMetadata,
    int? DefaultBitrateKbps = null
)
{
    /// <summary>
    /// Gets the primary (canonical) file extension with dot.
    /// </summary>
    public string PrimaryExtension => $".{Extensions[0]}";

    /// <summary>
    /// Gets the primary MIME type.
    /// </summary>
    public string PrimaryMimeType => MimeTypes[0];
}

/// <summary>
/// Centralized audio file format definitions.
/// Single source of truth for audio formats in the UI.
/// </summary>
public static class AudioFileFormats
{
    /// <summary>
    /// Standard audio format information catalog.
    /// </summary>
    public static readonly FrozenDictionary<AudioFormat, AudioFormatInfo> Formats = new Dictionary<AudioFormat, AudioFormatInfo>
    {
        [AudioFormat.Wav] = new(
            Format: AudioFormat.Wav,
            Name: "WAV",
            Description: "Waveform Audio File Format (uncompressed PCM)",
            Extensions: ["wav", "wave"],
            MimeTypes: ["audio/wav", "audio/x-wav", "audio/wave"],
            IsLossy: false,
            SupportsMetadata: false
        ),
        [AudioFormat.Mp3] = new(
            Format: AudioFormat.Mp3,
            Name: "MP3",
            Description: "MPEG Audio Layer III",
            Extensions: ["mp3"],
            MimeTypes: ["audio/mpeg", "audio/mp3"],
            IsLossy: true,
            SupportsMetadata: true,
            DefaultBitrateKbps: 192
        ),
        [AudioFormat.Flac] = new(
            Format: AudioFormat.Flac,
            Name: "FLAC",
            Description: "Free Lossless Audio Codec",
            Extensions: ["flac"],
            MimeTypes: ["audio/flac", "audio/x-flac"],
            IsLossy: false,
            SupportsMetadata: true
        ),
        [AudioFormat.Ogg] = new(
            Format: AudioFormat.Ogg,
            Name: "OGG Vorbis",
            Description: "OGG container with Vorbis audio",
            Extensions: ["ogg", "oga"],
            MimeTypes: ["audio/ogg", "audio/vorbis", "application/ogg"],
            IsLossy: true,
            SupportsMetadata: true,
            DefaultBitrateKbps: 192
        ),
        [AudioFormat.Opus] = new(
            Format: AudioFormat.Opus,
            Name: "Opus",
            Description: "Opus audio codec (OGG container)",
            Extensions: ["opus"],
            MimeTypes: ["audio/opus", "audio/ogg; codecs=opus"],
            IsLossy: true,
            SupportsMetadata: true,
            DefaultBitrateKbps: 128
        ),
        [AudioFormat.M4A] = new(
            Format: AudioFormat.M4A,
            Name: "M4A",
            Description: "MPEG-4 Audio (AAC in MP4 container)",
            Extensions: ["m4a"],
            MimeTypes: ["audio/mp4", "audio/x-m4a", "audio/m4a"],
            IsLossy: true,
            SupportsMetadata: true,
            DefaultBitrateKbps: 192
        ),
        [AudioFormat.Aac] = new(
            Format: AudioFormat.Aac,
            Name: "AAC",
            Description: "Advanced Audio Coding (raw AAC stream)",
            Extensions: ["aac"],
            MimeTypes: ["audio/aac", "audio/x-aac"],
            IsLossy: true,
            SupportsMetadata: false,
            DefaultBitrateKbps: 192
        ),
        [AudioFormat.Wma] = new(
            Format: AudioFormat.Wma,
            Name: "WMA",
            Description: "Windows Media Audio",
            Extensions: ["wma"],
            MimeTypes: ["audio/x-ms-wma", "audio/wma"],
            IsLossy: true,
            SupportsMetadata: true,
            DefaultBitrateKbps: 192
        ),
        [AudioFormat.Aiff] = new(
            Format: AudioFormat.Aiff,
            Name: "AIFF",
            Description: "Audio Interchange File Format",
            Extensions: ["aiff", "aif", "aifc"],
            MimeTypes: ["audio/aiff", "audio/x-aiff"],
            IsLossy: false,
            SupportsMetadata: true
        )
    }.ToFrozenDictionary();

    // Pre-computed extension lookup for performance
    private static readonly FrozenDictionary<string, AudioFormat> _extensionToFormat;

    // Pre-computed MIME type lookup
    private static readonly FrozenDictionary<string, AudioFormat> _mimeToFormat;

    // All supported extensions (frozen for thread safety)
    private static readonly FrozenSet<string> _allExtensions;

    // All extensions with dots (computed in static constructor to avoid null reference)
    private static readonly IReadOnlyList<string> _allExtensionsWithDots;

    static AudioFileFormats()
    {
        var extDict = new Dictionary<string, AudioFormat>(StringComparer.OrdinalIgnoreCase);
        var mimeDict = new Dictionary<string, AudioFormat>(StringComparer.OrdinalIgnoreCase);
        var extSet = new HashSet<string>(StringComparer.OrdinalIgnoreCase);

        foreach (var info in Formats.Values)
        {
            foreach (var ext in info.Extensions)
            {
                extDict[ext] = info.Format;
                extSet.Add(ext);
            }
            foreach (var mime in info.MimeTypes)
            {
                mimeDict[mime] = info.Format;
            }
        }

        _extensionToFormat = extDict.ToFrozenDictionary(StringComparer.OrdinalIgnoreCase);
        _mimeToFormat = mimeDict.ToFrozenDictionary(StringComparer.OrdinalIgnoreCase);
        _allExtensions = extSet.ToFrozenSet(StringComparer.OrdinalIgnoreCase);
        _allExtensionsWithDots = _allExtensions.Select(e => $".{e}").ToImmutableArray();
    }

    /// <summary>
    /// Gets all supported file extensions (lowercase, without dots).
    /// </summary>
    public static FrozenSet<string> AllExtensions => _allExtensions;

    /// <summary>
    /// Gets all supported file extensions with dots for file picker filters.
    /// </summary>
    public static IReadOnlyList<string> AllExtensionsWithDots => _allExtensionsWithDots;

    /// <summary>
    /// Standard import extensions for file pickers.
    /// </summary>
    public static IReadOnlyList<string> ImportExtensions { get; } =
        [".wav", ".mp3", ".flac", ".ogg", ".opus", ".m4a", ".aac", ".wma", ".aiff", ".aif"];

    /// <summary>
    /// Standard export extensions for file pickers.
    /// </summary>
    public static IReadOnlyList<string> ExportExtensions { get; } =
        [".wav", ".mp3", ".flac", ".ogg", ".opus", ".m4a", ".aac", ".wma", ".aiff"];

    /// <summary>
    /// Gets format info by AudioFormat enum.
    /// </summary>
    public static AudioFormatInfo GetInfo(AudioFormat format) => Formats[format];

    /// <summary>
    /// Looks up AudioFormat by file extension.
    /// </summary>
    /// <param name="extension">File extension with or without leading dot.</param>
    /// <returns>AudioFormat if recognized, null otherwise.</returns>
    public static AudioFormat? GetFormatByExtension(string extension)
    {
        var normalized = NormalizeExtension(extension);
        return _extensionToFormat.TryGetValue(normalized, out var format) ? format : null;
    }

    /// <summary>
    /// Looks up AudioFormat by MIME type.
    /// </summary>
    public static AudioFormat? GetFormatByMimeType(string mimeType)
    {
        return _mimeToFormat.TryGetValue(mimeType, out var format) ? format : null;
    }

    /// <summary>
    /// Checks if an extension is supported.
    /// </summary>
    public static bool IsSupported(string extension)
    {
        return _extensionToFormat.ContainsKey(NormalizeExtension(extension));
    }

    /// <summary>
    /// Normalizes a file extension (removes dot, lowercases).
    /// </summary>
    public static string NormalizeExtension(string extension)
    {
        return extension.TrimStart('.').ToLowerInvariant();
    }

    /// <summary>
    /// Gets MIME type for a file extension.
    /// </summary>
    public static string GetMimeType(string extension)
    {
        var format = GetFormatByExtension(extension);
        return format.HasValue ? Formats[format.Value].PrimaryMimeType : "application/octet-stream";
    }

    /// <summary>
    /// Gets file picker filter spec for Windows file dialogs.
    /// Format: "Audio Files|*.wav;*.mp3;*.flac;..."
    /// </summary>
    public static string GetFilePickerFilter()
    {
        var extensions = string.Join(";", AllExtensionsWithDots.Select(e => $"*{e}"));
        return $"Audio Files|{extensions}";
    }

    /// <summary>
    /// Gets file type choices for WinRT FileOpenPicker/FileSavePicker.
    /// </summary>
    public static IReadOnlyList<string> GetFileTypeChoices()
    {
        return AllExtensionsWithDots;
    }

    /// <summary>
    /// Video formats that contain audio tracks (for audio extraction).
    /// </summary>
    private static readonly IReadOnlyList<string> _videoExtensionsWithDots = new[]
    {
        ".mp4", ".mov", ".mkv", ".avi", ".webm", ".wmv"
    }.ToImmutableArray();

    /// <summary>
    /// Gets file type choices for audio import that includes video formats.
    /// Use this for scenarios where video files can be imported and their audio extracted.
    /// </summary>
    public static IReadOnlyList<string> GetMediaFileTypeChoices()
    {
        return AllExtensionsWithDots.Concat(_videoExtensionsWithDots).ToImmutableArray();
    }

    /// <summary>
    /// Gets a file filter string for Win32 dialogs that includes video formats.
    /// Format: "Media Files|*.wav;*.mp3;...;*.mp4;*.mov;..."
    /// </summary>
    public static string GetMediaFileFilterString()
    {
        var audioExtensions = AllExtensionsWithDots.Select(e => $"*{e}");
        var videoExtensions = _videoExtensionsWithDots.Select(e => $"*{e}");
        var allExtensions = string.Join(";", audioExtensions.Concat(videoExtensions));
        return $"Media Files|{allExtensions}";
    }

    /// <summary>
    /// Gets export format options as display name / extension pairs.
    /// </summary>
    public static IReadOnlyList<(string DisplayName, string Extension)> GetExportOptions()
    {
        return Formats.Values
            .Select(f => (f.Name, f.PrimaryExtension))
            .ToImmutableArray();
    }
}
