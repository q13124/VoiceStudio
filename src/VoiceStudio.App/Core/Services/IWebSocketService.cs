using System;
using System.Threading.Tasks;

namespace VoiceStudio.Core.Services
{
    /// <summary>
    /// WebSocket service interface for real-time communication with backend.
    /// Implements React/TypeScript WebSocket patterns in C#.
    /// </summary>
    public interface IWebSocketService : IDisposable
    {
        /// <summary>
        /// Event fired when WebSocket connection is established.
        /// </summary>
        event EventHandler? Connected;

        /// <summary>
        /// Event fired when WebSocket connection is closed.
        /// </summary>
        event EventHandler<string>? Disconnected;

        /// <summary>
        /// Event fired when an error occurs.
        /// </summary>
        event EventHandler<Exception>? Error;

        /// <summary>
        /// Event fired when a message is received.
        /// </summary>
        event EventHandler<WebSocketMessage>? MessageReceived;

        /// <summary>
        /// Gets the current connection state.
        /// </summary>
        WebSocketState State { get; }

        /// <summary>
        /// Gets whether the WebSocket is connected.
        /// </summary>
        bool IsConnected { get; }

        /// <summary>
        /// Connects to the WebSocket server with specified topics.
        /// </summary>
        /// <param name="topics">Topics to subscribe to (meters, training, batch, general, quality)</param>
        /// <param name="cancellationToken">Cancellation token</param>
        Task ConnectAsync(string[]? topics = null, System.Threading.CancellationToken cancellationToken = default);

        /// <summary>
        /// Disconnects from the WebSocket server.
        /// </summary>
        Task DisconnectAsync();

        /// <summary>
        /// Subscribes to a topic.
        /// </summary>
        /// <param name="topic">Topic to subscribe to</param>
        Task SubscribeAsync(string topic);

        /// <summary>
        /// Unsubscribes from a topic.
        /// </summary>
        /// <param name="topic">Topic to unsubscribe from</param>
        Task UnsubscribeAsync(string topic);

        /// <summary>
        /// Sends a ping message to keep connection alive.
        /// </summary>
        Task PingAsync();

        /// <summary>
        /// Sends a custom message.
        /// </summary>
        /// <param name="message">Message to send</param>
        Task SendMessageAsync(object message);
    }

    /// <summary>
    /// WebSocket connection state.
    /// </summary>
    public enum WebSocketState
    {
        Disconnected,
        Connecting,
        Connected,
        Disconnecting,
        Error
    }

    /// <summary>
    /// WebSocket message wrapper.
    /// </summary>
    public class WebSocketMessage
    {
        public string Topic { get; set; } = string.Empty;
        public string Type { get; set; } = string.Empty;
        public object? Payload { get; set; }
        public DateTime Timestamp { get; set; }
    }
}

