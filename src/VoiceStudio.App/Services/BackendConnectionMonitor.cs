using System;
using System.Net.Http;
using System.Threading;
using System.Threading.Tasks;
using VoiceStudio.App.Logging;
using VoiceStudio.App.Utilities;
using VoiceStudio.Core.Services;

namespace VoiceStudio.App.Services;

/// <summary>
/// Monitors backend connection and handles automatic reconnection with exponential backoff.
/// </summary>
public sealed class BackendConnectionMonitor : IDisposable
{
  private readonly IBackendClient _backendClient;
  private readonly HttpClient _httpClient;
  private readonly CancellationTokenSource _cts = new();
  private readonly SemaphoreSlim _reconnectLock = new(1, 1);

  private bool _isMonitoring;
  private bool _isReconnecting;
  private int _consecutiveFailures;
  private DateTime _lastSuccessfulPing = DateTime.MinValue;

  // Configuration
  private const int HealthCheckIntervalMs = 10000;     // 10 seconds between health checks
  private const int InitialReconnectDelayMs = 1000;    // Start at 1 second
  private const int MaxReconnectDelayMs = 60000;       // Max 60 seconds
  private const int MaxConsecutiveFailures = 10;       // Before giving up

  /// <summary>
  /// Event raised when connection is established or restored.
  /// </summary>
  public event EventHandler? Connected;

  /// <summary>
  /// Event raised when connection is lost.
  /// </summary>
  public event EventHandler? Disconnected;

  /// <summary>
  /// Event raised when reconnection attempt starts.
  /// </summary>
  public event EventHandler<ReconnectEventArgs>? ReconnectAttempt;

  /// <summary>
  /// Event raised when all reconnection attempts have failed.
  /// </summary>
  public event EventHandler? ReconnectFailed;

  /// <summary>
  /// Gets whether the backend is currently connected.
  /// </summary>
  public bool IsConnected { get; private set; }

  /// <summary>
  /// Gets the number of consecutive connection failures.
  /// </summary>
  public int ConsecutiveFailures => _consecutiveFailures;

  /// <summary>
  /// Gets the time of the last successful health check.
  /// </summary>
  public DateTime LastSuccessfulPing => _lastSuccessfulPing;

  public BackendConnectionMonitor(IBackendClient backendClient)
  {
    _backendClient = backendClient ?? throw new ArgumentNullException(nameof(backendClient));

    _httpClient = new HttpClient
    {
      BaseAddress = backendClient.BaseAddress,
      Timeout = TimeSpan.FromSeconds(5)
    };
  }

  /// <summary>
  /// Starts monitoring the backend connection.
  /// </summary>
  public void StartMonitoring()
  {
    if (_isMonitoring) return;
    _isMonitoring = true;

    _ = MonitorLoopAsync(_cts.Token);
  }

  /// <summary>
  /// Stops monitoring the backend connection.
  /// </summary>
  public void StopMonitoring()
  {
    _isMonitoring = false;
    _cts.Cancel();
  }

  private async Task MonitorLoopAsync(CancellationToken cancellationToken)
  {
    while (!cancellationToken.IsCancellationRequested)
    {
      try
      {
        var healthy = await CheckHealthAsync(cancellationToken);

        if (healthy)
        {
          if (!IsConnected)
          {
            IsConnected = true;
            _consecutiveFailures = 0;
            Connected?.Invoke(this, EventArgs.Empty);
            ErrorLogger.LogInfo("Backend connection established");
          }
          _lastSuccessfulPing = DateTime.UtcNow;
        }
        else
        {
          await HandleConnectionFailureAsync(cancellationToken);
        }
      }
      catch (OperationCanceledException)
      {
        break;
      }
      catch (Exception ex)
      {
        ErrorLogger.LogWarning($"Connection monitor error: {ex.Message}");
        await HandleConnectionFailureAsync(cancellationToken);
      }

      try
      {
        await Task.Delay(HealthCheckIntervalMs, cancellationToken);
      }
      catch (OperationCanceledException)
      {
        break;
      }
    }
  }

  private async Task<bool> CheckHealthAsync(CancellationToken cancellationToken)
  {
    try
    {
      var response = await _httpClient.GetAsync("/health", cancellationToken);
      return response.IsSuccessStatusCode;
    }
    catch (HttpRequestException)
    {
      return false;
    }
    catch (TaskCanceledException) when (!cancellationToken.IsCancellationRequested)
    {
      return false;
    }
  }

  private async Task HandleConnectionFailureAsync(CancellationToken cancellationToken)
  {
    var wasConnected = IsConnected;
    IsConnected = false;
    _consecutiveFailures++;

    if (wasConnected)
    {
      Disconnected?.Invoke(this, EventArgs.Empty);
      ErrorLogger.LogWarning("Backend connection lost");
    }

    // Start reconnection attempts
    await AttemptReconnectAsync(cancellationToken);
  }

  private async Task AttemptReconnectAsync(CancellationToken cancellationToken)
  {
    // Only one reconnection attempt at a time
    if (!await _reconnectLock.WaitAsync(0, cancellationToken))
    {
      return;
    }

    try
    {
      if (_isReconnecting) return;
      _isReconnecting = true;

      for (int attempt = 1; attempt <= MaxConsecutiveFailures; attempt++)
      {
        if (cancellationToken.IsCancellationRequested) break;

        // Calculate exponential backoff delay with jitter
        var delay = CalculateBackoffDelay(attempt);

        ReconnectAttempt?.Invoke(this, new ReconnectEventArgs
        {
          Attempt = attempt,
          MaxAttempts = MaxConsecutiveFailures,
          NextRetryDelayMs = delay
        });

        ErrorLogger.LogInfo($"Reconnection attempt {attempt}/{MaxConsecutiveFailures} in {delay}ms");

        await Task.Delay(delay, cancellationToken);

        if (await CheckHealthAsync(cancellationToken))
        {
          IsConnected = true;
          _consecutiveFailures = 0;
          _lastSuccessfulPing = DateTime.UtcNow;
          Connected?.Invoke(this, EventArgs.Empty);
          ErrorLogger.LogInfo("Backend connection restored");
          return;
        }
      }

      // All attempts failed
      ErrorLogger.LogError("All reconnection attempts failed");
      ReconnectFailed?.Invoke(this, EventArgs.Empty);
    }
    finally
    {
      _isReconnecting = false;
      _reconnectLock.Release();
    }
  }

  private int CalculateBackoffDelay(int attempt)
  {
    // Exponential backoff: delay = initial * 2^(attempt-1)
    var delay = InitialReconnectDelayMs * (int)Math.Pow(2, attempt - 1);
    delay = Math.Min(delay, MaxReconnectDelayMs);

    // Add jitter (0-20% of delay)
    var jitter = Random.Shared.Next(0, (int)(delay * 0.2));
    return delay + jitter;
  }

  /// <summary>
  /// Forces an immediate reconnection attempt.
  /// </summary>
  public async Task<bool> ForceReconnectAsync(CancellationToken cancellationToken = default)
  {
    _consecutiveFailures = 0;
    var healthy = await CheckHealthAsync(cancellationToken);

    if (healthy)
    {
      IsConnected = true;
      _lastSuccessfulPing = DateTime.UtcNow;
      Connected?.Invoke(this, EventArgs.Empty);
    }
    else
    {
      await AttemptReconnectAsync(cancellationToken);
    }

    return IsConnected;
  }

  public void Dispose()
  {
    StopMonitoring();
    _cts.Dispose();
    _httpClient.Dispose();
    _reconnectLock.Dispose();
  }
}

/// <summary>
/// Event arguments for reconnection attempts.
/// </summary>
public class ReconnectEventArgs : EventArgs
{
  /// <summary>
  /// Current attempt number.
  /// </summary>
  public int Attempt { get; init; }

  /// <summary>
  /// Maximum number of attempts before giving up.
  /// </summary>
  public int MaxAttempts { get; init; }

  /// <summary>
  /// Delay in milliseconds before the next retry.
  /// </summary>
  public int NextRetryDelayMs { get; init; }
}
