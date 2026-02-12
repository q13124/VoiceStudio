// Copyright (c) VoiceStudio. All rights reserved.
// Licensed under the MIT license.

using System;

namespace VoiceStudio.Core.Services
{
    /// <summary>
    /// Factory interface for creating WebSocket clients.
    /// </summary>
    /// <remarks>
    /// <para>
    /// This factory enables dependency injection for WebSocket clients,
    /// allowing ViewModels to receive clients via DI rather than
    /// instantiating them directly with 'new'.
    /// </para>
    /// <para>
    /// Benefits:
    /// - Testability: Mock factories can provide test doubles
    /// - Loose coupling: ViewModels don't depend on concrete client types
    /// - Lifecycle management: Factory controls client creation
    /// </para>
    /// </remarks>
    public interface IWebSocketClientFactory
    {
        /// <summary>
        /// Creates a realtime voice WebSocket client.
        /// </summary>
        /// <returns>A new realtime voice client, or null if WebSocket service is unavailable.</returns>
        IRealtimeVoiceClient? CreateRealtimeVoiceClient();

        /// <summary>
        /// Creates a pipeline streaming WebSocket client.
        /// </summary>
        /// <returns>A new pipeline streaming client, or null if WebSocket service is unavailable.</returns>
        IPipelineStreamingClient? CreatePipelineStreamingClient();

        /// <summary>
        /// Creates a job progress WebSocket client.
        /// </summary>
        /// <returns>A new job progress client, or null if WebSocket service is unavailable.</returns>
        IJobProgressClient? CreateJobProgressClient();
    }

    /// <summary>
    /// Interface for realtime voice WebSocket clients.
    /// </summary>
    /// <remarks>
    /// Concrete implementations may use more specific event argument types.
    /// The interface uses object for maximum flexibility.
    /// </remarks>
    public interface IRealtimeVoiceClient : IDisposable
    {
        /// <summary>Whether the client is connected.</summary>
        bool IsConnected { get; }

        /// <summary>Connect to the WebSocket endpoint.</summary>
        System.Threading.Tasks.Task ConnectAsync(string? sessionId = null, System.Threading.CancellationToken cancellationToken = default);

        /// <summary>Send audio data for processing.</summary>
        System.Threading.Tasks.Task SendAudioDataAsync(byte[] audioData, System.Threading.CancellationToken cancellationToken = default);

        /// <summary>Disconnect from the WebSocket endpoint.</summary>
        System.Threading.Tasks.Task DisconnectAsync();
    }

    /// <summary>
    /// Interface for pipeline streaming WebSocket clients.
    /// </summary>
    /// <remarks>
    /// Concrete implementations may use more specific event argument types.
    /// </remarks>
    public interface IPipelineStreamingClient : IDisposable
    {
        /// <summary>Whether the client is connected.</summary>
        bool IsConnected { get; }

        /// <summary>Connect to the WebSocket endpoint.</summary>
        System.Threading.Tasks.Task ConnectAsync(string? sessionId = null, System.Threading.CancellationToken cancellationToken = default);

        /// <summary>Send audio data for processing.</summary>
        System.Threading.Tasks.Task SendAudioAsync(byte[] audioData, System.Threading.CancellationToken cancellationToken = default);

        /// <summary>Disconnect from the WebSocket endpoint.</summary>
        System.Threading.Tasks.Task DisconnectAsync();
    }

    /// <summary>
    /// Interface for job progress WebSocket clients.
    /// </summary>
    /// <remarks>
    /// Concrete implementations may use more specific event argument types.
    /// </remarks>
    public interface IJobProgressClient : IDisposable
    {
        /// <summary>Whether the client is connected.</summary>
        bool IsConnected { get; }

        /// <summary>Connect to the WebSocket endpoint.</summary>
        System.Threading.Tasks.Task ConnectAsync(System.Threading.CancellationToken cancellationToken = default);

        /// <summary>Disconnect from the WebSocket endpoint.</summary>
        System.Threading.Tasks.Task DisconnectAsync();
    }
}
