// Copyright (c) VoiceStudio. All rights reserved.
// Licensed under the MIT License.

using System;
using System.Collections.Generic;
using System.Text.Json.Serialization;

namespace VoiceStudio.App.Services.AgentGovernance;

/// <summary>
/// Status of an approval request.
/// </summary>
public enum ApprovalStatus
{
  Pending = 0,
  Approved = 1,
  Denied = 2,
  Expired = 3,
  Cancelled = 4
}

/// <summary>
/// An approval request for a high-risk agent action.
/// </summary>
public sealed class ApprovalRequest
{
  /// <summary>
  /// Unique identifier for this request.
  /// </summary>
  [JsonPropertyName("request_id")]
  public string RequestId { get; set; } = string.Empty;

  /// <summary>
  /// ID of the requesting agent.
  /// </summary>
  [JsonPropertyName("agent_id")]
  public string AgentId { get; set; } = string.Empty;

  /// <summary>
  /// ID of the user associated with the agent.
  /// </summary>
  [JsonPropertyName("user_id")]
  public string UserId { get; set; } = string.Empty;

  /// <summary>
  /// Cross-layer tracing ID.
  /// </summary>
  [JsonPropertyName("correlation_id")]
  public string CorrelationId { get; set; } = string.Empty;

  /// <summary>
  /// Name of the tool to execute.
  /// </summary>
  [JsonPropertyName("tool_name")]
  public string ToolName { get; set; } = string.Empty;

  /// <summary>
  /// Tool parameters.
  /// </summary>
  [JsonPropertyName("parameters")]
  public Dictionary<string, object?> Parameters { get; set; } = new();

  /// <summary>
  /// Risk tier of the action.
  /// </summary>
  [JsonPropertyName("risk_tier")]
  public string RiskTier { get; set; } = "medium";

  /// <summary>
  /// Why approval is required.
  /// </summary>
  [JsonPropertyName("reason")]
  public string Reason { get; set; } = string.Empty;

  /// <summary>
  /// When the request was created.
  /// </summary>
  [JsonPropertyName("created_at")]
  public DateTime CreatedAt { get; set; } = DateTime.Now;

  /// <summary>
  /// When the request expires.
  /// </summary>
  [JsonPropertyName("expires_at")]
  public DateTime? ExpiresAt { get; set; }

  /// <summary>
  /// Current status.
  /// </summary>
  [JsonPropertyName("status")]
  public ApprovalStatus Status { get; set; } = ApprovalStatus.Pending;

  /// <summary>
  /// Who made the approval decision.
  /// </summary>
  [JsonPropertyName("decided_by")]
  public string? DecidedBy { get; set; }

  /// <summary>
  /// When the decision was made.
  /// </summary>
  [JsonPropertyName("decided_at")]
  public DateTime? DecidedAt { get; set; }

  /// <summary>
  /// Reason for the decision.
  /// </summary>
  [JsonPropertyName("decision_reason")]
  public string DecisionReason { get; set; } = string.Empty;

  /// <summary>
  /// Check if the request has expired.
  /// </summary>
  public bool IsExpired => ExpiresAt.HasValue && DateTime.Now > ExpiresAt.Value;

  /// <summary>
  /// Check if the request is still pending.
  /// </summary>
  public bool IsPending => Status == ApprovalStatus.Pending && !IsExpired;

  /// <summary>
  /// Get a display-friendly summary of the action.
  /// </summary>
  public string ActionSummary => $"{ToolName} ({RiskTier} risk)";

  /// <summary>
  /// Get the time remaining before expiration.
  /// </summary>
  public TimeSpan? TimeRemaining => ExpiresAt.HasValue
      ? ExpiresAt.Value - DateTime.Now
      : null;
}

/// <summary>
/// Result of an approval decision.
/// </summary>
public sealed class ApprovalResult
{
  /// <summary>
  /// The request ID that was decided.
  /// </summary>
  public string RequestId { get; set; } = string.Empty;

  /// <summary>
  /// Whether the request was approved.
  /// </summary>
  public bool IsApproved { get; set; }

  /// <summary>
  /// Who made the decision.
  /// </summary>
  public string DecidedBy { get; set; } = string.Empty;

  /// <summary>
  /// Reason for the decision.
  /// </summary>
  public string Reason { get; set; } = string.Empty;

  /// <summary>
  /// When the decision was made.
  /// </summary>
  public DateTime DecidedAt { get; set; } = DateTime.Now;
}