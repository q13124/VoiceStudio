using System;
using System.Threading;
using System.Threading.Tasks;
using VoiceStudio.Core.Exceptions;

namespace VoiceStudio.App.Utilities
{
  /// <summary>
  /// Helper class for retry logic with exponential backoff and circuit breaker pattern.
  /// </summary>
  public static class RetryHelper
  {
    /// <summary>
    /// Executes an operation with retry logic using exponential backoff.
    /// </summary>
    /// <typeparam name="T">Return type of the operation</typeparam>
    /// <param name="operation">The operation to execute</param>
    /// <param name="maxRetries">Maximum number of retry attempts (default: 3)</param>
    /// <param name="initialDelayMs">Initial delay in milliseconds (default: 1000)</param>
    /// <param name="maxDelayMs">Maximum delay in milliseconds (default: 10000)</param>
    /// <param name="cancellationToken">Cancellation token</param>
    /// <returns>Result of the operation</returns>
    public static async Task<T> ExecuteWithExponentialBackoffAsync<T>(
        Func<Task<T>> operation,
        int maxRetries = 3,
        int initialDelayMs = 1000,
        int maxDelayMs = 10000,
        CancellationToken cancellationToken = default)
    {
      Exception? lastException = null;

      for (int attempt = 0; attempt < maxRetries; attempt++)
      {
        try
        {
          return await operation();
        }
        catch (Exception ex) when (attempt < maxRetries - 1 && ShouldRetry(ex))
        {
          lastException = ex;

          // Calculate exponential backoff delay: initialDelay * 2^attempt
          var delayMs = Math.Min(
              initialDelayMs * (int)Math.Pow(2, attempt),
              maxDelayMs
          );

          // Add jitter to prevent thundering herd (random 0-20% of delay)
          var jitter = new Random().Next(0, (int)(delayMs * 0.2));
          delayMs += jitter;

          await Task.Delay(delayMs, cancellationToken);
        }
      }

      // All retries exhausted - throw the last exception
      if (lastException != null)
        throw lastException;

      throw new InvalidOperationException("Operation failed but no exception was captured.");
    }

    /// <summary>
    /// Determines if an exception should trigger a retry.
    /// </summary>
    private static bool ShouldRetry(Exception ex)
    {
      return ex switch
      {
        BackendException bex => bex.IsRetryable,
        System.Net.Http.HttpRequestException => true,
        TaskCanceledException tcex => !tcex.CancellationToken.IsCancellationRequested,
        TimeoutException => true,
        _ => false
      };
    }
  }

  /// <summary>
  /// Circuit breaker pattern implementation for preventing repeated failures.
  /// </summary>
  public class CircuitBreaker
  {
    private readonly int _failureThreshold;
    private readonly TimeSpan _timeout;
    private int _failureCount;
    private DateTime _lastFailureTime = DateTime.MinValue;
    private CircuitState _state = CircuitState.Closed;

    public CircuitBreaker(int failureThreshold = 5, TimeSpan? timeout = null)
    {
      _failureThreshold = failureThreshold;
      _timeout = timeout ?? TimeSpan.FromSeconds(30);
    }

    public CircuitState State => _state;

    /// <summary>
    /// Executes an operation through the circuit breaker.
    /// </summary>
    public async Task<T> ExecuteAsync<T>(Func<Task<T>> operation)
    {
      if (_state == CircuitState.Open)
      {
        // Check if timeout has passed - try half-open state
        if (DateTime.UtcNow - _lastFailureTime > _timeout)
        {
          _state = CircuitState.HalfOpen;
        }
        else
        {
          throw new BackendUnavailableException(
              "Service is temporarily unavailable. Please try again in a moment.");
        }
      }

      try
      {
        var result = await operation();

        // Success - reset circuit breaker
        if (_state == CircuitState.HalfOpen)
        {
          _state = CircuitState.Closed;
          _failureCount = 0;
        }
        else if (_state == CircuitState.Closed)
        {
          _failureCount = 0;
        }

        return result;
      }
      catch (Exception ex) when (ShouldCountAsFailure(ex))
      {
        _failureCount++;
        _lastFailureTime = DateTime.UtcNow;

        if (_failureCount >= _failureThreshold)
        {
          _state = CircuitState.Open;
        }

        throw;
      }
    }

    private bool ShouldCountAsFailure(Exception ex)
    {
      return ex switch
      {
        BackendException bex => bex.IsRetryable,
        System.Net.Http.HttpRequestException => true,
        TaskCanceledException => true,
        TimeoutException => true,
        _ => false
      };
    }

    public void Reset()
    {
      _state = CircuitState.Closed;
      _failureCount = 0;
      _lastFailureTime = DateTime.MinValue;
    }
  }

  /// <summary>
  /// Circuit breaker states.
  /// </summary>
  public enum CircuitState
  {
    Closed = 0,    // Normal operation
    Open = 1,      // Failing - reject requests
    HalfOpen = 2   // Testing if service recovered
  }
}