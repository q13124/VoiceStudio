using System;
using System.IO;
using System.Threading;
using System.Threading.Tasks;

namespace VoiceStudio.Core.Gateways
{
  /// <summary>
  /// Transport layer for backend HTTP communication.
  /// Provides retry, circuit breaker, and correlation tracking.
  /// </summary>
  public interface IBackendTransport
  {
    /// <summary>
    /// Gets the current connection status.
    /// </summary>
    bool IsConnected { get; }

    /// <summary>
    /// Occurs when the connection status changes.
    /// </summary>
    event EventHandler<bool>? ConnectionStatusChanged;

    /// <summary>
    /// Performs a GET request and deserializes the response.
    /// </summary>
    /// <typeparam name="T">The expected response type.</typeparam>
    /// <param name="path">The API path (e.g., "/api/profiles").</param>
    /// <param name="cancellationToken">Cancellation token.</param>
    /// <returns>Gateway result with deserialized data or error.</returns>
    Task<GatewayResult<T>> GetAsync<T>(string path, CancellationToken cancellationToken = default);

    /// <summary>
    /// Performs a POST request with a JSON body.
    /// </summary>
    /// <typeparam name="TRequest">The request body type.</typeparam>
    /// <typeparam name="TResponse">The expected response type.</typeparam>
    /// <param name="path">The API path.</param>
    /// <param name="body">The request body.</param>
    /// <param name="cancellationToken">Cancellation token.</param>
    /// <returns>Gateway result with deserialized data or error.</returns>
    Task<GatewayResult<TResponse>> PostAsync<TRequest, TResponse>(
        string path,
        TRequest body,
        CancellationToken cancellationToken = default);

    /// <summary>
    /// Performs a POST request with no response body.
    /// </summary>
    /// <typeparam name="TRequest">The request body type.</typeparam>
    /// <param name="path">The API path.</param>
    /// <param name="body">The request body.</param>
    /// <param name="cancellationToken">Cancellation token.</param>
    /// <returns>Gateway result indicating success or error.</returns>
    Task<GatewayResult<bool>> PostAsync<TRequest>(
        string path,
        TRequest body,
        CancellationToken cancellationToken = default);

    /// <summary>
    /// Performs a PUT request with a JSON body.
    /// </summary>
    /// <typeparam name="TRequest">The request body type.</typeparam>
    /// <typeparam name="TResponse">The expected response type.</typeparam>
    /// <param name="path">The API path.</param>
    /// <param name="body">The request body.</param>
    /// <param name="cancellationToken">Cancellation token.</param>
    /// <returns>Gateway result with deserialized data or error.</returns>
    Task<GatewayResult<TResponse>> PutAsync<TRequest, TResponse>(
        string path,
        TRequest body,
        CancellationToken cancellationToken = default);

    /// <summary>
    /// Performs a DELETE request.
    /// </summary>
    /// <param name="path">The API path.</param>
    /// <param name="cancellationToken">Cancellation token.</param>
    /// <returns>Gateway result indicating success or error.</returns>
    Task<GatewayResult<bool>> DeleteAsync(string path, CancellationToken cancellationToken = default);

    /// <summary>
    /// Performs a file upload using multipart form data.
    /// </summary>
    /// <typeparam name="TResponse">The expected response type.</typeparam>
    /// <param name="path">The API path.</param>
    /// <param name="fileStream">The file stream to upload.</param>
    /// <param name="fileName">The file name.</param>
    /// <param name="fieldName">The form field name (default: "file").</param>
    /// <param name="contentType">The content type (default: "application/octet-stream").</param>
    /// <param name="progress">Optional progress callback (bytesRead, totalBytes).</param>
    /// <param name="cancellationToken">Cancellation token.</param>
    /// <returns>Gateway result with deserialized data or error.</returns>
    Task<GatewayResult<TResponse>> UploadAsync<TResponse>(
        string path,
        Stream fileStream,
        string fileName,
        string fieldName = "file",
        string contentType = "application/octet-stream",
        Action<long, long>? progress = null,
        CancellationToken cancellationToken = default);

    /// <summary>
    /// Downloads a file from the backend.
    /// </summary>
    /// <param name="path">The API path.</param>
    /// <param name="destinationStream">The stream to write the downloaded content to.</param>
    /// <param name="progress">Optional progress callback (bytesRead, totalBytes).</param>
    /// <param name="cancellationToken">Cancellation token.</param>
    /// <returns>Gateway result indicating success or error.</returns>
    Task<GatewayResult<bool>> DownloadAsync(
        string path,
        Stream destinationStream,
        Action<long, long>? progress = null,
        CancellationToken cancellationToken = default);

    /// <summary>
    /// Gets the raw HTTP response for streaming scenarios.
    /// </summary>
    /// <param name="path">The API path.</param>
    /// <param name="cancellationToken">Cancellation token.</param>
    /// <returns>Gateway result with the response stream or error.</returns>
    Task<GatewayResult<Stream>> GetStreamAsync(string path, CancellationToken cancellationToken = default);

    /// <summary>
    /// Resets the circuit breaker state.
    /// </summary>
    void ResetCircuitBreaker();
  }
}
