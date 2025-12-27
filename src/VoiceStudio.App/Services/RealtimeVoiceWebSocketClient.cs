using System;
using System.Text.Json;
using System.Threading;
using System.Threading.Tasks;
using VoiceStudio.Core.Services;

namespace VoiceStudio.App.Services
{
    /// <summary>
    /// Specialized WebSocket client for real-time voice conversion.
    /// Implements React/TypeScript realtimeVoiceClient pattern in C#.
    /// </summary>
    public class RealtimeVoiceWebSocketClient : IDisposable
    {
        private readonly IWebSocketService _webSocketService;
        private readonly JsonSerializerOptions _jsonOptions;
        private bool _isSubscribed = false;
        private bool _disposed = false;

        /// <summary>
        /// Event fired when audio data is received for real-time conversion.
        /// </summary>
        public event EventHandler<RealtimeAudioData>? AudioDataReceived;

        /// <summary>
        /// Event fired when conversion status changes.
        /// </summary>
        public event EventHandler<RealtimeConversionStatus>? StatusChanged;

        /// <summary>
        /// Event fired when conversion quality metrics are updated.
        /// </summary>
        public event EventHandler<RealtimeQualityMetrics>? QualityMetricsUpdated;

        /// <summary>
        /// Event fired when latency information is received.
        /// </summary>
        public event EventHandler<RealtimeLatencyInfo>? LatencyInfoReceived;

        public RealtimeVoiceWebSocketClient(IWebSocketService webSocketService)
        {
            _webSocketService = webSocketService ?? throw new ArgumentNullException(nameof(webSocketService));
            _jsonOptions = new JsonSerializerOptions
            {
                PropertyNameCaseInsensitive = true,
                PropertyNamingPolicy = JsonNamingPolicy.CamelCase
            };

            // Subscribe to WebSocket messages
            _webSocketService.MessageReceived += OnWebSocketMessageReceived;
        }

        /// <summary>
        /// Connects and subscribes to real-time voice conversion updates.
        /// </summary>
        public async Task ConnectAsync(string? sessionId = null, CancellationToken cancellationToken = default)
        {
            if (_disposed)
                throw new ObjectDisposedException(nameof(RealtimeVoiceWebSocketClient));

            if (!_webSocketService.IsConnected)
            {
                await _webSocketService.ConnectAsync(new[] { "realtime_voice" }, cancellationToken);
            }

            if (!_isSubscribed)
            {
                await _webSocketService.SubscribeAsync("realtime_voice");
                _isSubscribed = true;
            }

            // Send session initialization if session ID provided
            if (!string.IsNullOrEmpty(sessionId))
            {
                await _webSocketService.SendMessageAsync(new
                {
                    type = "init_session",
                    session_id = sessionId
                });
            }
        }

        /// <summary>
        /// Sends audio data for real-time conversion.
        /// </summary>
        public async Task SendAudioDataAsync(byte[] audioData, CancellationToken cancellationToken = default)
        {
            if (_disposed || !_webSocketService.IsConnected)
                throw new InvalidOperationException("WebSocket is not connected");

            await _webSocketService.SendMessageAsync(new
            {
                type = "audio_data",
                data = Convert.ToBase64String(audioData),
                timestamp = DateTime.UtcNow
            });
        }

        /// <summary>
        /// Gets whether the WebSocket client is connected and subscribed.
        /// </summary>
        public bool IsConnected => _webSocketService.IsConnected && _isSubscribed;

        /// <summary>
        /// Unsubscribes from real-time voice conversion updates.
        /// </summary>
        public async Task DisconnectAsync()
        {
            if (_isSubscribed)
            {
                try
                {
                    await _webSocketService.UnsubscribeAsync("realtime_voice");
                }
                catch
                {
                    // Ignore errors during unsubscribe
                }
                _isSubscribed = false;
            }
        }

        private void OnWebSocketMessageReceived(object? sender, WebSocketMessage message)
        {
            if (_disposed)
                return;

            // Only process real-time voice topic
            if (message.Topic != "realtime_voice")
                return;

            try
            {
                var payloadJson = JsonSerializer.Serialize(message.Payload, _jsonOptions);
                using var doc = JsonDocument.Parse(payloadJson);
                var root = doc.RootElement;

                // Determine message type
                var messageType = root.TryGetProperty("type", out var typeProp) 
                    ? typeProp.GetString() 
                    : "audio_data";

                switch (messageType.ToLowerInvariant())
                {
                    case "audio_data":
                        HandleAudioData(root);
                        break;
                    case "status":
                        HandleStatusUpdate(root);
                        break;
                    case "quality_metrics":
                        HandleQualityMetrics(root);
                        break;
                    case "latency":
                        HandleLatencyInfo(root);
                        break;
                }
            }
            catch (Exception ex)
            {
                // Log error but don't throw
                System.Diagnostics.Debug.WriteLine($"Failed to process real-time voice message: {ex.Message}");
            }
        }

        private void HandleAudioData(JsonElement root)
        {
            try
            {
                var update = JsonSerializer.Deserialize<RealtimeAudioData>(root.GetRawText(), _jsonOptions);
                if (update != null)
                {
                    AudioDataReceived?.Invoke(this, update);
                }
            }
            catch
            {
                // Ignore deserialization errors
            }
        }

        private void HandleStatusUpdate(JsonElement root)
        {
            try
            {
                var update = JsonSerializer.Deserialize<RealtimeConversionStatus>(root.GetRawText(), _jsonOptions);
                if (update != null)
                {
                    StatusChanged?.Invoke(this, update);
                }
            }
            catch
            {
                // Ignore deserialization errors
            }
        }

        private void HandleQualityMetrics(JsonElement root)
        {
            try
            {
                var update = JsonSerializer.Deserialize<RealtimeQualityMetrics>(root.GetRawText(), _jsonOptions);
                if (update != null)
                {
                    QualityMetricsUpdated?.Invoke(this, update);
                }
            }
            catch
            {
                // Ignore deserialization errors
            }
        }

        private void HandleLatencyInfo(JsonElement root)
        {
            try
            {
                var update = JsonSerializer.Deserialize<RealtimeLatencyInfo>(root.GetRawText(), _jsonOptions);
                if (update != null)
                {
                    LatencyInfoReceived?.Invoke(this, update);
                }
            }
            catch
            {
                // Ignore deserialization errors
            }
        }

        public void Dispose()
        {
            if (!_disposed)
            {
                _disposed = true;
                _webSocketService.MessageReceived -= OnWebSocketMessageReceived;
                DisconnectAsync().GetAwaiter().GetResult();
            }
        }
    }

    /// <summary>
    /// Real-time audio data message.
    /// </summary>
    public class RealtimeAudioData
    {
        public byte[] AudioData { get; set; } = Array.Empty<byte>();
        public int SampleRate { get; set; }
        public int Channels { get; set; }
        public DateTime Timestamp { get; set; }
    }

    /// <summary>
    /// Real-time conversion status message.
    /// </summary>
    public class RealtimeConversionStatus
    {
        public string Status { get; set; } = string.Empty; // "idle", "converting", "paused", "error"
        public string? Message { get; set; }
        public DateTime Timestamp { get; set; }
    }

    /// <summary>
    /// Real-time quality metrics message.
    /// </summary>
    public class RealtimeQualityMetrics
    {
        public double Similarity { get; set; }
        public double Naturalness { get; set; }
        public double Clarity { get; set; }
        public DateTime Timestamp { get; set; }
    }

    /// <summary>
    /// Real-time latency information message.
    /// </summary>
    public class RealtimeLatencyInfo
    {
        public double ProcessingLatency { get; set; } // milliseconds
        public double NetworkLatency { get; set; } // milliseconds
        public double TotalLatency { get; set; } // milliseconds
        public DateTime Timestamp { get; set; }
    }
}

