// Copyright (c) VoiceStudio. All rights reserved.
// Licensed under the MIT License.

using System;
using System.Collections.Concurrent;
using System.Collections.Generic;
using System.Linq;
using System.Net.Http;
using System.Net.Http.Json;
using System.Text.Json;
using System.Threading;
using System.Threading.Tasks;
using Microsoft.Extensions.Logging;
using VoiceStudio.App.Logging;

namespace VoiceStudio.App.Services.AgentGovernance;

/// <summary>
/// Service for managing agent action approvals.
/// Communicates with the Python backend for approval management.
/// </summary>
public sealed class ApprovalService : IApprovalService, IDisposable
{
  private readonly HttpClient _httpClient;
  private readonly ILogger<ApprovalService>? _logger;
  private readonly ConcurrentDictionary<string, ApprovalRequest> _pendingRequests = new();
  private readonly string _currentUser;
  private CancellationTokenSource? _listenerCts;
  private Task? _listenerTask;
  private bool _disposed;

  /// <inheritdoc/>
  public event EventHandler<ApprovalRequest>? ApprovalRequested;

  /// <inheritdoc/>
  public event EventHandler<ApprovalResult>? ApprovalDecided;

  /// <summary>
  /// Initializes a new instance of the <see cref="ApprovalService"/> class.
  /// </summary>
  /// <param name="httpClient">HTTP client for backend communication.</param>
  /// <param name="logger">Optional logger.</param>
  public ApprovalService(HttpClient httpClient, ILogger<ApprovalService>? logger = null)
  {
    _httpClient = httpClient ?? throw new ArgumentNullException(nameof(httpClient));
    _logger = logger;
    _currentUser = Environment.UserName;
  }

  /// <inheritdoc/>
  public async Task<IReadOnlyList<ApprovalRequest>> GetPendingRequestsAsync(
      CancellationToken cancellationToken = default)
  {
    try
    {
      var response = await _httpClient.GetAsync(
          "api/governance/approvals/pending",
          cancellationToken).ConfigureAwait(false);

      if (response.IsSuccessStatusCode)
      {
        var requests = await response.Content.ReadFromJsonAsync<List<ApprovalRequest>>(
            cancellationToken: cancellationToken).ConfigureAwait(false);

        return requests ?? new List<ApprovalRequest>();
      }

      _logger?.LogWarning("Failed to get pending requests: {StatusCode}", response.StatusCode);
      return _pendingRequests.Values.Where(r => r.IsPending).ToList();
    }
    catch (Exception ex)
    {
      _logger?.LogError(ex, "Error getting pending requests");
      return _pendingRequests.Values.Where(r => r.IsPending).ToList();
    }
  }

  /// <inheritdoc/>
  public async Task<ApprovalRequest?> GetRequestAsync(
      string requestId,
      CancellationToken cancellationToken = default)
  {
    if (_pendingRequests.TryGetValue(requestId, out var cached))
    {
      return cached;
    }

    try
    {
      var response = await _httpClient.GetAsync(
          $"api/governance/approvals/{requestId}",
          cancellationToken).ConfigureAwait(false);

      if (response.IsSuccessStatusCode)
      {
        return await response.Content.ReadFromJsonAsync<ApprovalRequest>(
            cancellationToken: cancellationToken).ConfigureAwait(false);
      }
    }
    catch (Exception ex)
    {
      _logger?.LogError(ex, "Error getting request {RequestId}", requestId);
    }

    return null;
  }

  /// <inheritdoc/>
  public async Task<ApprovalResult> ApproveAsync(
      string requestId,
      string reason = "",
      CancellationToken cancellationToken = default)
  {
    return await DecideAsync(requestId, true, reason, cancellationToken).ConfigureAwait(false);
  }

  /// <inheritdoc/>
  public async Task<ApprovalResult> DenyAsync(
      string requestId,
      string reason = "",
      CancellationToken cancellationToken = default)
  {
    return await DecideAsync(requestId, false, reason, cancellationToken).ConfigureAwait(false);
  }

  private async Task<ApprovalResult> DecideAsync(
      string requestId,
      bool approve,
      string reason,
      CancellationToken cancellationToken)
  {
    var result = new ApprovalResult
    {
      RequestId = requestId,
      IsApproved = approve,
      DecidedBy = _currentUser,
      Reason = reason,
      DecidedAt = DateTime.Now
    };

    try
    {
      var endpoint = approve
          ? $"api/governance/approvals/{requestId}/approve"
          : $"api/governance/approvals/{requestId}/deny";

      var payload = new { decided_by = _currentUser, reason };
      var response = await _httpClient.PostAsJsonAsync(
          endpoint,
          payload,
          cancellationToken).ConfigureAwait(false);

      if (response.IsSuccessStatusCode)
      {
        _pendingRequests.TryRemove(requestId, out _);
        ApprovalDecided?.Invoke(this, result);
        _logger?.LogInformation(
            "Request {RequestId} {Decision} by {User}",
            requestId,
            approve ? "approved" : "denied",
            _currentUser);
      }
      else
      {
        _logger?.LogWarning(
            "Failed to {Decision} request {RequestId}: {StatusCode}",
            approve ? "approve" : "deny",
            requestId,
            response.StatusCode);
      }
    }
    catch (Exception ex)
    {
      _logger?.LogError(ex, "Error deciding on request {RequestId}", requestId);
    }

    return result;
  }

  /// <inheritdoc/>
  public async Task<ApprovalResult> ShowApprovalDialogAsync(
      ApprovalRequest request,
      CancellationToken cancellationToken = default)
  {
    // This will be implemented by the View layer
    // For now, auto-deny for safety
    _logger?.LogWarning(
        "ShowApprovalDialogAsync not implemented, auto-denying request {RequestId}",
        request.RequestId);

    return await DenyAsync(
        request.RequestId,
        "Approval dialog not available",
        cancellationToken).ConfigureAwait(false);
  }

  /// <inheritdoc/>
  public async Task<IReadOnlyList<ApprovalRequest>> GetHistoryAsync(
      DateTime? startDate = null,
      DateTime? endDate = null,
      int limit = 100,
      CancellationToken cancellationToken = default)
  {
    try
    {
      var query = $"api/governance/approvals/history?limit={limit}";
      if (startDate.HasValue)
      {
        query += $"&start_date={startDate.Value:o}";
      }

      if (endDate.HasValue)
      {
        query += $"&end_date={endDate.Value:o}";
      }

      var response = await _httpClient.GetAsync(query, cancellationToken).ConfigureAwait(false);

      if (response.IsSuccessStatusCode)
      {
        var history = await response.Content.ReadFromJsonAsync<List<ApprovalRequest>>(
            cancellationToken: cancellationToken).ConfigureAwait(false);

        return history ?? new List<ApprovalRequest>();
      }
    }
    catch (Exception ex)
    {
      _logger?.LogError(ex, "Error getting approval history");
    }

    return new List<ApprovalRequest>();
  }

  /// <inheritdoc/>
  public async Task StartListeningAsync(CancellationToken cancellationToken = default)
  {
    if (_listenerTask != null)
    {
      return;
    }

    _listenerCts = CancellationTokenSource.CreateLinkedTokenSource(cancellationToken);
    _listenerTask = ListenForRequestsAsync(_listenerCts.Token);

    _logger?.LogInformation("Started listening for approval requests");
    await Task.CompletedTask.ConfigureAwait(false);
  }

  /// <inheritdoc/>
  public async Task StopListeningAsync()
  {
    if (_listenerCts != null)
    {
      await _listenerCts.CancelAsync().ConfigureAwait(false);
      _listenerCts.Dispose();
      _listenerCts = null;
    }

    if (_listenerTask != null)
    {
      try
      {
        await _listenerTask.ConfigureAwait(false);
      }
      catch (Exception ex)
      {
        ErrorLogger.LogWarning($"Best effort operation failed: {ex.Message}", "ApprovalService.StopListeningAsync");
      }

      _listenerTask = null;
    }

    _logger?.LogInformation("Stopped listening for approval requests");
  }

  private async Task ListenForRequestsAsync(CancellationToken cancellationToken)
  {
    while (!cancellationToken.IsCancellationRequested)
    {
      try
      {
        // Poll for new requests
        var requests = await GetPendingRequestsAsync(cancellationToken).ConfigureAwait(false);

        foreach (var request in requests)
        {
          if (_pendingRequests.TryAdd(request.RequestId, request))
          {
            _logger?.LogInformation(
                "New approval request: {RequestId} for {ToolName}",
                request.RequestId,
                request.ToolName);

            ApprovalRequested?.Invoke(this, request);
          }
        }

        // Clean up expired requests
        foreach (var request in _pendingRequests.Values.Where(r => r.IsExpired).ToList())
        {
          _pendingRequests.TryRemove(request.RequestId, out _);
        }

        await Task.Delay(TimeSpan.FromSeconds(2), cancellationToken).ConfigureAwait(false);
      }
      catch (OperationCanceledException)
      {
        break;
      }
      catch (Exception ex)
      {
        _logger?.LogError(ex, "Error in approval listener");
        await Task.Delay(TimeSpan.FromSeconds(5), cancellationToken).ConfigureAwait(false);
      }
    }
  }

  /// <inheritdoc/>
  public void Dispose()
  {
    if (_disposed)
    {
      return;
    }

    _listenerCts?.Cancel();
    _listenerCts?.Dispose();
    _disposed = true;
  }
}