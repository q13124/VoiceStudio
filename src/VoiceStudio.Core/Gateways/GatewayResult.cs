using System;
using System.Text.Json;

namespace VoiceStudio.Core.Gateways
{
  /// <summary>
  /// Standard response envelope for all gateway operations.
  /// Provides consistent error handling and correlation tracking.
  /// </summary>
  /// <typeparam name="T">The type of the result data.</typeparam>
  public sealed class GatewayResult<T>
  {
    /// <summary>
    /// Gets a value indicating whether the operation succeeded.
    /// </summary>
    public bool Success { get; }

    /// <summary>
    /// Gets the result data when successful.
    /// </summary>
    public T? Data { get; }

    /// <summary>
    /// Gets the error details when failed.
    /// </summary>
    public GatewayError? Error { get; }

    /// <summary>
    /// Gets the correlation ID for tracing.
    /// </summary>
    public string CorrelationId { get; }

    private GatewayResult(bool success, T? data, GatewayError? error, string correlationId)
    {
      Success = success;
      Data = data;
      Error = error;
      CorrelationId = correlationId;
    }

    /// <summary>
    /// Creates a successful result with data.
    /// </summary>
    public static GatewayResult<T> Ok(T data, string? correlationId = null)
    {
      return new GatewayResult<T>(true, data, null, correlationId ?? Guid.NewGuid().ToString("N"));
    }

    /// <summary>
    /// Creates a failed result with error details.
    /// </summary>
    public static GatewayResult<T> Fail(GatewayError error, string? correlationId = null)
    {
      return new GatewayResult<T>(false, default, error, correlationId ?? Guid.NewGuid().ToString("N"));
    }

    /// <summary>
    /// Creates a failed result from an exception.
    /// </summary>
    public static GatewayResult<T> Fail(Exception exception, string? correlationId = null)
    {
      var error = GatewayError.FromException(exception);
      return new GatewayResult<T>(false, default, error, correlationId ?? Guid.NewGuid().ToString("N"));
    }

    /// <summary>
    /// Maps the result data to a new type.
    /// </summary>
    public GatewayResult<TNew> Map<TNew>(Func<T, TNew> mapper)
    {
      if (Success && Data is not null)
      {
        return GatewayResult<TNew>.Ok(mapper(Data), CorrelationId);
      }
      return GatewayResult<TNew>.Fail(Error!, CorrelationId);
    }
  }

  /// <summary>
  /// Error details for failed gateway operations.
  /// Aligns with backend StandardErrorResponse for unified error handling.
  /// </summary>
  public sealed class GatewayError
  {
    /// <summary>
    /// Gets the error code for programmatic handling.
    /// Maps to backend error_code field.
    /// </summary>
    public string Code { get; }

    /// <summary>
    /// Gets the human-readable error message.
    /// Maps to backend message field.
    /// </summary>
    public string Message { get; }

    /// <summary>
    /// Gets the HTTP status code if applicable.
    /// </summary>
    public int? StatusCode { get; }

    /// <summary>
    /// Gets a value indicating whether the operation can be retried.
    /// </summary>
    public bool IsRetryable { get; }

    /// <summary>
    /// Gets a suggestion for recovering from the error.
    /// Maps to backend recovery_suggestion field.
    /// </summary>
    public string? RecoverySuggestion { get; }

    /// <summary>
    /// Gets additional error details as JSON.
    /// Maps to backend details field.
    /// </summary>
    public JsonElement? Details { get; }

    /// <summary>
    /// Gets the request ID for correlation/tracing.
    /// Maps to backend request_id field.
    /// </summary>
    public string? RequestId { get; }

    /// <summary>
    /// Gets the timestamp when the error occurred.
    /// Maps to backend timestamp field (ISO 8601 format).
    /// </summary>
    public string? Timestamp { get; }

    /// <summary>
    /// Gets the API path where the error occurred.
    /// Maps to backend path field.
    /// </summary>
    public string? Path { get; }

    public GatewayError(
        string code,
        string message,
        int? statusCode = null,
        bool isRetryable = false,
        string? recoverySuggestion = null,
        JsonElement? details = null,
        string? requestId = null,
        string? timestamp = null,
        string? path = null)
    {
      Code = code;
      Message = message;
      StatusCode = statusCode;
      IsRetryable = isRetryable;
      RecoverySuggestion = recoverySuggestion;
      Details = details;
      RequestId = requestId;
      Timestamp = timestamp;
      Path = path;
    }

    /// <summary>
    /// Creates a GatewayError from an exception.
    /// </summary>
    public static GatewayError FromException(Exception exception)
    {
      // Check if it's a BackendException type via duck typing (avoid direct dependency)
      var exType = exception.GetType();
      var statusCodeProp = exType.GetProperty("StatusCode");
      var errorCodeProp = exType.GetProperty("ErrorCode");
      var isRetryableProp = exType.GetProperty("IsRetryable");
      var recoverySuggestionProp = exType.GetProperty("RecoverySuggestion");
      var detailsProp = exType.GetProperty("Details");

      var statusCode = statusCodeProp?.GetValue(exception) as int?;
      var errorCode = errorCodeProp?.GetValue(exception) as string ?? "UNKNOWN_ERROR";
      var isRetryable = isRetryableProp?.GetValue(exception) as bool? ?? false;
      var recoverySuggestion = recoverySuggestionProp?.GetValue(exception) as string;
      var details = detailsProp?.GetValue(exception) as JsonElement?;

      return new GatewayError(
          errorCode,
          exception.Message,
          statusCode,
          isRetryable,
          recoverySuggestion,
          details);
    }

    /// <summary>
    /// Creates a standard validation error.
    /// </summary>
    public static GatewayError Validation(string message, JsonElement? details = null)
    {
      return new GatewayError("VALIDATION_ERROR", message, 400, false, null, details);
    }

    /// <summary>
    /// Creates a standard not found error.
    /// </summary>
    public static GatewayError NotFound(string message)
    {
      return new GatewayError("NOT_FOUND", message, 404, false);
    }

    /// <summary>
    /// Creates a standard server error.
    /// </summary>
    public static GatewayError ServerError(string message, bool isRetryable = true)
    {
      return new GatewayError("SERVER_ERROR", message, 500, isRetryable);
    }

    /// <summary>
    /// Creates a standard unavailable error.
    /// </summary>
    public static GatewayError Unavailable(string message = "Service is temporarily unavailable")
    {
      return new GatewayError("UNAVAILABLE", message, 503, true, "Please try again in a moment.");
    }
  }
}
