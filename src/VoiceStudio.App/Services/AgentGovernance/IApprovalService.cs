// Copyright (c) VoiceStudio. All rights reserved.
// Licensed under the MIT License.

using System;
using System.Collections.Generic;
using System.Threading;
using System.Threading.Tasks;

namespace VoiceStudio.App.Services.AgentGovernance;

/// <summary>
/// Service interface for managing agent action approvals.
/// </summary>
public interface IApprovalService
{
  /// <summary>
  /// Raised when a new approval request is received.
  /// </summary>
  event EventHandler<ApprovalRequest>? ApprovalRequested;

  /// <summary>
  /// Raised when an approval decision is made.
  /// </summary>
  event EventHandler<ApprovalResult>? ApprovalDecided;

  /// <summary>
  /// Get all pending approval requests.
  /// </summary>
  /// <param name="cancellationToken">Cancellation token.</param>
  /// <returns>List of pending requests.</returns>
  Task<IReadOnlyList<ApprovalRequest>> GetPendingRequestsAsync(
      CancellationToken cancellationToken = default);

  /// <summary>
  /// Get a specific approval request by ID.
  /// </summary>
  /// <param name="requestId">The request ID.</param>
  /// <param name="cancellationToken">Cancellation token.</param>
  /// <returns>The request, or null if not found.</returns>
  Task<ApprovalRequest?> GetRequestAsync(
      string requestId,
      CancellationToken cancellationToken = default);

  /// <summary>
  /// Approve a request.
  /// </summary>
  /// <param name="requestId">The request ID to approve.</param>
  /// <param name="reason">Reason for approval.</param>
  /// <param name="cancellationToken">Cancellation token.</param>
  /// <returns>The approval result.</returns>
  Task<ApprovalResult> ApproveAsync(
      string requestId,
      string reason = "",
      CancellationToken cancellationToken = default);

  /// <summary>
  /// Deny a request.
  /// </summary>
  /// <param name="requestId">The request ID to deny.</param>
  /// <param name="reason">Reason for denial.</param>
  /// <param name="cancellationToken">Cancellation token.</param>
  /// <returns>The approval result.</returns>
  Task<ApprovalResult> DenyAsync(
      string requestId,
      string reason = "",
      CancellationToken cancellationToken = default);

  /// <summary>
  /// Show an approval dialog for a request.
  /// </summary>
  /// <param name="request">The approval request.</param>
  /// <param name="cancellationToken">Cancellation token.</param>
  /// <returns>The approval result from the dialog.</returns>
  Task<ApprovalResult> ShowApprovalDialogAsync(
      ApprovalRequest request,
      CancellationToken cancellationToken = default);

  /// <summary>
  /// Get approval history.
  /// </summary>
  /// <param name="startDate">Filter by start date.</param>
  /// <param name="endDate">Filter by end date.</param>
  /// <param name="limit">Maximum records to return.</param>
  /// <param name="cancellationToken">Cancellation token.</param>
  /// <returns>List of historical approval records.</returns>
  Task<IReadOnlyList<ApprovalRequest>> GetHistoryAsync(
      DateTime? startDate = null,
      DateTime? endDate = null,
      int limit = 100,
      CancellationToken cancellationToken = default);

  /// <summary>
  /// Start listening for approval requests from the backend.
  /// </summary>
  /// <param name="cancellationToken">Cancellation token.</param>
  Task StartListeningAsync(CancellationToken cancellationToken = default);

  /// <summary>
  /// Stop listening for approval requests.
  /// </summary>
  Task StopListeningAsync();
}