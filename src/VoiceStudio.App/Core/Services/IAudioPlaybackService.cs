using System;
using System.IO;
using System.Threading;
using System.Threading.Tasks;

namespace VoiceStudio.Core.Services
{
    /// <summary>
    /// Service for audio playback in VoiceStudio.
    /// Supports playback of synthesized audio from voice cloning engines.
    /// </summary>
    public interface IAudioPlaybackService
    {
        /// <summary>
        /// Gets whether audio is currently playing.
        /// </summary>
        bool IsPlaying { get; }

        /// <summary>
        /// Gets the current playback position in seconds.
        /// </summary>
        double Position { get; }

        /// <summary>
        /// Gets the total duration of the current audio in seconds.
        /// </summary>
        double Duration { get; }

        /// <summary>
        /// Gets the current volume (0.0 to 1.0).
        /// </summary>
        double Volume { get; set; }

        /// <summary>
        /// Event raised when playback starts.
        /// </summary>
        event EventHandler? PlaybackStarted;

        /// <summary>
        /// Event raised when playback stops or completes.
        /// </summary>
        event EventHandler? PlaybackStopped;

        /// <summary>
        /// Event raised when playback position changes.
        /// </summary>
        event EventHandler<double>? PositionChanged;

        /// <summary>
        /// Plays audio from a file path.
        /// </summary>
        /// <param name="filePath">Path to audio file (WAV, MP3, FLAC supported)</param>
        /// <param name="cancellationToken">Cancellation token</param>
        Task PlayFileAsync(string filePath, CancellationToken cancellationToken = default);

        /// <summary>
        /// Plays audio from a stream (e.g., from backend API).
        /// </summary>
        /// <param name="audioStream">Stream containing audio data</param>
        /// <param name="format">Audio format (e.g., "wav", "mp3")</param>
        /// <param name="cancellationToken">Cancellation token</param>
        Task PlayStreamAsync(Stream audioStream, string format = "wav", CancellationToken cancellationToken = default);

        /// <summary>
        /// Plays audio from a URL (e.g., from backend API endpoint).
        /// </summary>
        /// <param name="audioUrl">URL to audio file</param>
        /// <param name="cancellationToken">Cancellation token</param>
        Task PlayUrlAsync(string audioUrl, CancellationToken cancellationToken = default);

        /// <summary>
        /// Pauses playback.
        /// </summary>
        void Pause();

        /// <summary>
        /// Resumes playback from paused position.
        /// </summary>
        void Resume();

        /// <summary>
        /// Stops playback and resets position.
        /// </summary>
        void Stop();

        /// <summary>
        /// Seeks to a specific position in seconds.
        /// </summary>
        /// <param name="position">Position in seconds</param>
        void Seek(double position);
    }
}
