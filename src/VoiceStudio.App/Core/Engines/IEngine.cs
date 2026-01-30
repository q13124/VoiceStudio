using System;
using System.Threading;
using System.Threading.Tasks;

namespace VoiceStudio.Core.Engines
{
    /// <summary>
    /// Base interface for all engine adapters.
    /// Engines wrap backend AI capabilities (TTS, ASR, etc.) into a consistent API.
    /// </summary>
    public interface IEngine
    {
        /// <summary>
        /// Unique identifier for the engine (e.g. "coqui-xtts-v2").
        /// </summary>
        string Id { get; }

        /// <summary>
        /// Display name of the engine.
        /// </summary>
        string Name { get; }

        /// <summary>
        /// Version string of the engine adapter/model.
        /// </summary>
        string Version { get; }

        /// <summary>
        /// Capabilities supported by this engine.
        /// </summary>
        EngineCapabilities Capabilities { get; }

        /// <summary>
        /// Initializes the engine (loads models, checks GPU, etc.).
        /// </summary>
        Task InitializeAsync(CancellationToken cancellationToken = default);

        /// <summary>
        /// Shuts down the engine and releases resources (VRAM).
        /// </summary>
        Task ShutdownAsync(CancellationToken cancellationToken = default);

        /// <summary>
        /// Checks if the engine is currently available and healthy.
        /// </summary>
        Task<bool> IsAvailableAsync(CancellationToken cancellationToken = default);
    }

    /// <summary>
    /// Capabilities flags for engine discovery.
    /// </summary>
    [Flags]
    public enum EngineCapabilities
    {
        None = 0,
        TextToSpeech = 1 << 0,
        Transcription = 1 << 1,
        VoiceCloning = 1 << 2,
        AudioEffects = 1 << 3,
        Training = 1 << 4
    }
}
