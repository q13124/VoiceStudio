// Copyright (c) VoiceStudio. All rights reserved.
// Licensed under the MIT license.

using System;
using VoiceStudio.Core.Services;

namespace VoiceStudio.App.Services
{
    /// <summary>
    /// Factory for creating WebSocket clients.
    /// </summary>
    /// <remarks>
    /// <para>
    /// This factory centralizes WebSocket client creation, enabling:
    /// - Dependency injection in ViewModels
    /// - Testability via mock factories
    /// - Centralized WebSocket service access
    /// </para>
    /// <para>
    /// GAP-009: Replaces direct instantiation with factory pattern.
    /// </para>
    /// </remarks>
    public class WebSocketClientFactory : IWebSocketClientFactory
    {
        private readonly IWebSocketService? _webSocketService;

        /// <summary>
        /// Initializes a new instance of the <see cref="WebSocketClientFactory"/> class.
        /// </summary>
        /// <param name="webSocketService">The WebSocket service to use for client creation.</param>
        public WebSocketClientFactory(IWebSocketService? webSocketService)
        {
            _webSocketService = webSocketService;
        }

        /// <inheritdoc/>
        public IRealtimeVoiceClient? CreateRealtimeVoiceClient()
        {
            if (_webSocketService == null)
                return null;

            return new RealtimeVoiceWebSocketClient(_webSocketService);
        }

        /// <inheritdoc/>
        public IPipelineStreamingClient? CreatePipelineStreamingClient()
        {
            if (_webSocketService == null)
                return null;

            return new PipelineStreamingWebSocketClient(_webSocketService);
        }

        /// <inheritdoc/>
        public IJobProgressClient? CreateJobProgressClient()
        {
            if (_webSocketService == null)
                return null;

            return new JobProgressWebSocketClient(_webSocketService);
        }
    }
}
