using System;
using System.Text.Json;
using System.Threading;
using System.Threading.Tasks;
using VoiceStudio.Core.Models;
using VoiceStudio.Core.Services;

namespace VoiceStudio.App.Services
{
    /// <summary>
    /// Specialized WebSocket client for job progress updates.
    /// Implements React/TypeScript jobProgressClient pattern in C#.
    /// </summary>
    public class JobProgressWebSocketClient : IDisposable
    {
        private readonly IWebSocketService _webSocketService;
        private readonly JsonSerializerOptions _jsonOptions;
        private bool _isSubscribed = false;
        private bool _disposed = false;

        /// <summary>
        /// Event fired when job progress is updated.
        /// </summary>
        public event EventHandler<JobProgressUpdate>? ProgressUpdated;

        /// <summary>
        /// Event fired when a job status changes.
        /// </summary>
        public event EventHandler<JobStatusUpdate>? StatusChanged;

        /// <summary>
        /// Event fired when a job completes.
        /// </summary>
        public event EventHandler<JobCompletedUpdate>? JobCompleted;

        /// <summary>
        /// Event fired when a job fails.
        /// </summary>
        public event EventHandler<JobFailedUpdate>? JobFailed;

        public JobProgressWebSocketClient(IWebSocketService webSocketService)
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
        /// Connects and subscribes to job progress updates.
        /// </summary>
        public async Task ConnectAsync(CancellationToken cancellationToken = default)
        {
            if (_disposed)
                throw new ObjectDisposedException(nameof(JobProgressWebSocketClient));

            if (!_webSocketService.IsConnected)
            {
                await _webSocketService.ConnectAsync(new[] { "batch", "training" }, cancellationToken);
            }

            if (!_isSubscribed)
            {
                await _webSocketService.SubscribeAsync("batch");
                await _webSocketService.SubscribeAsync("training");
                _isSubscribed = true;
            }
        }

        /// <summary>
        /// Gets whether the WebSocket client is connected and subscribed.
        /// </summary>
        public bool IsConnected => _webSocketService.IsConnected && _isSubscribed;

        /// <summary>
        /// Unsubscribes from job progress updates.
        /// </summary>
        public async Task DisconnectAsync()
        {
            if (_isSubscribed)
            {
                try
                {
                    await _webSocketService.UnsubscribeAsync("batch");
                    await _webSocketService.UnsubscribeAsync("training");
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

            // Only process job-related topics
            if (message.Topic != "batch" && message.Topic != "training")
                return;

            try
            {
                var payloadJson = JsonSerializer.Serialize(message.Payload, _jsonOptions);
                using var doc = JsonDocument.Parse(payloadJson);
                var root = doc.RootElement;

                // Determine message type
                var messageType = root.TryGetProperty("type", out var typeProp) 
                    ? typeProp.GetString() 
                    : "progress";

                switch (messageType.ToLowerInvariant())
                {
                    case "progress":
                        HandleProgressUpdate(root);
                        break;
                    case "status":
                        HandleStatusUpdate(root);
                        break;
                    case "completed":
                        HandleJobCompleted(root);
                        break;
                    case "failed":
                        HandleJobFailed(root);
                        break;
                }
            }
            catch (Exception ex)
            {
                // Log error but don't throw
                System.Diagnostics.Debug.WriteLine($"Failed to process job progress message: {ex.Message}");
            }
        }

        private void HandleProgressUpdate(JsonElement root)
        {
            try
            {
                var update = JsonSerializer.Deserialize<JobProgressUpdate>(root.GetRawText(), _jsonOptions);
                if (update != null)
                {
                    ProgressUpdated?.Invoke(this, update);
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
                var update = JsonSerializer.Deserialize<JobStatusUpdate>(root.GetRawText(), _jsonOptions);
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

        private void HandleJobCompleted(JsonElement root)
        {
            try
            {
                var update = JsonSerializer.Deserialize<JobCompletedUpdate>(root.GetRawText(), _jsonOptions);
                if (update != null)
                {
                    JobCompleted?.Invoke(this, update);
                }
            }
            catch
            {
                // Ignore deserialization errors
            }
        }

        private void HandleJobFailed(JsonElement root)
        {
            try
            {
                var update = JsonSerializer.Deserialize<JobFailedUpdate>(root.GetRawText(), _jsonOptions);
                if (update != null)
                {
                    JobFailed?.Invoke(this, update);
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
    /// Job progress update message.
    /// </summary>
    public class JobProgressUpdate
    {
        public string JobId { get; set; } = string.Empty;
        public string JobType { get; set; } = string.Empty;
        public double Progress { get; set; } // 0.0 to 1.0
        public string? Status { get; set; }
        public string? Message { get; set; }
        public DateTime Timestamp { get; set; }
    }

    /// <summary>
    /// Job status update message.
    /// </summary>
    public class JobStatusUpdate
    {
        public string JobId { get; set; } = string.Empty;
        public string JobType { get; set; } = string.Empty;
        public string Status { get; set; } = string.Empty; // "pending", "running", "paused", "cancelled"
        public string? Message { get; set; }
        public DateTime Timestamp { get; set; }
    }

    /// <summary>
    /// Job completed update message.
    /// </summary>
    public class JobCompletedUpdate
    {
        public string JobId { get; set; } = string.Empty;
        public string JobType { get; set; } = string.Empty;
        public string? ResultId { get; set; }
        public string? Message { get; set; }
        public DateTime Timestamp { get; set; }
    }

    /// <summary>
    /// Job failed update message.
    /// </summary>
    public class JobFailedUpdate
    {
        public string JobId { get; set; } = string.Empty;
        public string JobType { get; set; } = string.Empty;
        public string Error { get; set; } = string.Empty;
        public string? Details { get; set; }
        public DateTime Timestamp { get; set; }
    }
}

