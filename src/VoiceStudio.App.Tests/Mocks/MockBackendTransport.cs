using System;
using System.Collections.Generic;
using System.IO;
using System.Threading;
using System.Threading.Tasks;
using VoiceStudio.Core.Gateways;

namespace VoiceStudio.App.Tests.Mocks
{
  /// <summary>
  /// Mock implementation of <see cref="IBackendTransport"/> for testing.
  /// </summary>
  public class MockBackendTransport : IBackendTransport
  {
    private bool _isConnected = true;
    private readonly Dictionary<string, Func<object?>> _getResponses = new();
    private readonly Dictionary<string, Func<object?, object?>> _postResponses = new();
    private readonly Dictionary<string, Func<object?, object?>> _putResponses = new();
    private readonly Dictionary<string, bool> _deleteResponses = new();
    private readonly List<(string Method, string Path, object? Body)> _requests = new();

    /// <summary>
    /// Gets whether the transport is connected.
    /// </summary>
    public bool IsConnected
    {
      get => _isConnected;
      set
      {
        if (_isConnected != value)
        {
          _isConnected = value;
          ConnectionStatusChanged?.Invoke(this, value);
        }
      }
    }

    /// <inheritdoc />
    public event EventHandler<bool>? ConnectionStatusChanged;

    /// <summary>
    /// Gets the list of requests made to this mock.
    /// </summary>
    public IReadOnlyList<(string Method, string Path, object? Body)> Requests => _requests;

    /// <summary>
    /// Clears all recorded requests.
    /// </summary>
    public void ClearRequests()
    {
      _requests.Clear();
    }

    /// <summary>
    /// Sets up a response for a GET request.
    /// </summary>
    public void SetupGet<T>(string path, T response)
    {
      _getResponses[path] = () => response;
    }

    /// <summary>
    /// Sets up a response for a GET request using a factory function.
    /// </summary>
    public void SetupGet<T>(string path, Func<T> responseFactory)
    {
      _getResponses[path] = () => responseFactory();
    }

    /// <summary>
    /// Sets up a response for a POST request.
    /// </summary>
    public void SetupPost<TRequest, TResponse>(string path, Func<TRequest, TResponse> handler)
    {
      _postResponses[path] = body => handler((TRequest)body!);
    }

    /// <summary>
    /// Sets up a static response for a POST request.
    /// </summary>
    public void SetupPost<TResponse>(string path, TResponse response)
    {
      _postResponses[path] = _ => response;
    }

    /// <summary>
    /// Sets up a response for a PUT request.
    /// </summary>
    public void SetupPut<TRequest, TResponse>(string path, Func<TRequest, TResponse> handler)
    {
      _putResponses[path] = body => handler((TRequest)body!);
    }

    /// <summary>
    /// Sets up a static response for a PUT request.
    /// </summary>
    public void SetupPut<TResponse>(string path, TResponse response)
    {
      _putResponses[path] = _ => response;
    }

    /// <summary>
    /// Sets up a response for a DELETE request.
    /// </summary>
    public void SetupDelete(string path, bool response = true)
    {
      _deleteResponses[path] = response;
    }

    /// <summary>
    /// Simulates a network error.
    /// </summary>
    public GatewayError? SimulatedError { get; set; }

    /// <summary>
    /// Delay to simulate network latency.
    /// </summary>
    public TimeSpan SimulatedLatency { get; set; } = TimeSpan.Zero;

    /// <inheritdoc />
    public async Task<GatewayResult<T>> GetAsync<T>(string path, CancellationToken cancellationToken = default)
    {
      _requests.Add(("GET", path, null));

      if (SimulatedLatency > TimeSpan.Zero)
        await Task.Delay(SimulatedLatency, cancellationToken);

      if (SimulatedError != null)
        return GatewayResult<T>.Fail(SimulatedError);

      if (!IsConnected)
        return GatewayResult<T>.Fail(new GatewayError("NETWORK_ERROR", "Not connected", isRetryable: true));

      if (_getResponses.TryGetValue(path, out var factory))
      {
        var response = factory();
        if (response is T typedResponse)
          return GatewayResult<T>.Ok(typedResponse);
      }

      return GatewayResult<T>.Fail(new GatewayError("NOT_FOUND", $"No mock set up for GET {path}"));
    }

    /// <inheritdoc />
    public async Task<GatewayResult<TResponse>> PostAsync<TRequest, TResponse>(
        string path,
        TRequest body,
        CancellationToken cancellationToken = default)
    {
      _requests.Add(("POST", path, body));

      if (SimulatedLatency > TimeSpan.Zero)
        await Task.Delay(SimulatedLatency, cancellationToken);

      if (SimulatedError != null)
        return GatewayResult<TResponse>.Fail(SimulatedError);

      if (!IsConnected)
        return GatewayResult<TResponse>.Fail(new GatewayError("NETWORK_ERROR", "Not connected", isRetryable: true));

      if (_postResponses.TryGetValue(path, out var handler))
      {
        var response = handler(body);
        if (response is TResponse typedResponse)
          return GatewayResult<TResponse>.Ok(typedResponse);
      }

      return GatewayResult<TResponse>.Fail(new GatewayError("NOT_FOUND", $"No mock set up for POST {path}"));
    }

    /// <inheritdoc />
    public async Task<GatewayResult<bool>> PostAsync<TRequest>(
        string path,
        TRequest body,
        CancellationToken cancellationToken = default)
    {
      _requests.Add(("POST", path, body));

      if (SimulatedLatency > TimeSpan.Zero)
        await Task.Delay(SimulatedLatency, cancellationToken);

      if (SimulatedError != null)
        return GatewayResult<bool>.Fail(SimulatedError);

      if (!IsConnected)
        return GatewayResult<bool>.Fail(new GatewayError("NETWORK_ERROR", "Not connected", isRetryable: true));

      return GatewayResult<bool>.Ok(true);
    }

    /// <inheritdoc />
    public async Task<GatewayResult<TResponse>> PutAsync<TRequest, TResponse>(
        string path,
        TRequest body,
        CancellationToken cancellationToken = default)
    {
      _requests.Add(("PUT", path, body));

      if (SimulatedLatency > TimeSpan.Zero)
        await Task.Delay(SimulatedLatency, cancellationToken);

      if (SimulatedError != null)
        return GatewayResult<TResponse>.Fail(SimulatedError);

      if (!IsConnected)
        return GatewayResult<TResponse>.Fail(new GatewayError("NETWORK_ERROR", "Not connected", isRetryable: true));

      if (_putResponses.TryGetValue(path, out var handler))
      {
        var response = handler(body);
        if (response is TResponse typedResponse)
          return GatewayResult<TResponse>.Ok(typedResponse);
      }

      return GatewayResult<TResponse>.Fail(new GatewayError("NOT_FOUND", $"No mock set up for PUT {path}"));
    }

    /// <inheritdoc />
    public async Task<GatewayResult<bool>> DeleteAsync(string path, CancellationToken cancellationToken = default)
    {
      _requests.Add(("DELETE", path, null));

      if (SimulatedLatency > TimeSpan.Zero)
        await Task.Delay(SimulatedLatency, cancellationToken);

      if (SimulatedError != null)
        return GatewayResult<bool>.Fail(SimulatedError);

      if (!IsConnected)
        return GatewayResult<bool>.Fail(new GatewayError("NETWORK_ERROR", "Not connected", isRetryable: true));

      var success = _deleteResponses.GetValueOrDefault(path, true);
      return GatewayResult<bool>.Ok(success);
    }

    /// <inheritdoc />
    public Task<GatewayResult<TResponse>> UploadAsync<TResponse>(
        string path,
        Stream fileStream,
        string fileName,
        string fieldName = "file",
        string contentType = "application/octet-stream",
        Action<long, long>? progress = null,
        CancellationToken cancellationToken = default)
    {
      _requests.Add(("UPLOAD", path, fileName));

      if (SimulatedError != null)
        return Task.FromResult(GatewayResult<TResponse>.Fail(SimulatedError));

      if (!IsConnected)
        return Task.FromResult(GatewayResult<TResponse>.Fail(
            new GatewayError("NETWORK_ERROR", "Not connected", isRetryable: true)));

      progress?.Invoke(fileStream.Length, fileStream.Length);

      // Return default response - caller should set up mock if specific response needed
      return Task.FromResult(GatewayResult<TResponse>.Fail(
          new GatewayError("NOT_CONFIGURED", $"No mock set up for UPLOAD {path}")));
    }

    /// <inheritdoc />
    public Task<GatewayResult<bool>> DownloadAsync(
        string path,
        Stream destinationStream,
        Action<long, long>? progress = null,
        CancellationToken cancellationToken = default)
    {
      _requests.Add(("DOWNLOAD", path, null));

      if (SimulatedError != null)
        return Task.FromResult(GatewayResult<bool>.Fail(SimulatedError));

      if (!IsConnected)
        return Task.FromResult(GatewayResult<bool>.Fail(
            new GatewayError("NETWORK_ERROR", "Not connected", isRetryable: true)));

      // Write some dummy data
      var dummyData = new byte[1024];
      destinationStream.Write(dummyData, 0, dummyData.Length);
      progress?.Invoke(dummyData.Length, dummyData.Length);

      return Task.FromResult(GatewayResult<bool>.Ok(true));
    }

    /// <inheritdoc />
    public Task<GatewayResult<Stream>> GetStreamAsync(string path, CancellationToken cancellationToken = default)
    {
      _requests.Add(("STREAM", path, null));

      if (SimulatedError != null)
        return Task.FromResult(GatewayResult<Stream>.Fail(SimulatedError));

      if (!IsConnected)
        return Task.FromResult(GatewayResult<Stream>.Fail(
            new GatewayError("NETWORK_ERROR", "Not connected", isRetryable: true)));

      var stream = new MemoryStream(Array.Empty<byte>());
      return Task.FromResult(GatewayResult<Stream>.Ok(stream));
    }

    /// <inheritdoc />
    public void ResetCircuitBreaker()
    {
      // No-op for mock
    }
  }
}
