// Copyright (c) VoiceStudio. All rights reserved.
// Licensed under the MIT License.

using System;
using System.Text.Json;
using Microsoft.UI.Xaml;
using Microsoft.UI.Xaml.Controls;
using VoiceStudio.App.Services.AgentGovernance;

namespace VoiceStudio.App.Views;

/// <summary>
/// Dialog for approving or denying agent actions.
/// </summary>
public sealed partial class AgentApprovalDialog : Window
{
    private readonly ApprovalRequest _request;
    private readonly TaskCompletionSource<ApprovalResult> _resultTcs;

    /// <summary>
    /// Gets the tool name being requested.
    /// </summary>
    public string ToolName => _request.ToolName;

    /// <summary>
    /// Initializes a new instance of the <see cref="AgentApprovalDialog"/> class.
    /// </summary>
    /// <param name="request">The approval request to display.</param>
    public AgentApprovalDialog(ApprovalRequest request)
    {
        _request = request ?? throw new ArgumentNullException(nameof(request));
        _resultTcs = new TaskCompletionSource<ApprovalResult>();

        InitializeComponent();
        PopulateFields();
    }

    /// <summary>
    /// Gets a task that completes when the user makes a decision.
    /// </summary>
    public Task<ApprovalResult> ResultTask => _resultTcs.Task;

    private void PopulateFields()
    {
        ToolNameText.Text = _request.ToolName;
        RiskTierText.Text = _request.RiskTier.ToUpperInvariant();
        AgentIdText.Text = _request.AgentId;
        ReasonText.Text = _request.Reason;

        // Format expiration
        if (_request.ExpiresAt.HasValue)
        {
            var remaining = _request.ExpiresAt.Value - DateTime.Now;
            ExpiresText.Text = remaining.TotalMinutes > 1
                ? $"in {remaining.TotalMinutes:F0} minutes"
                : "soon";
        }
        else
        {
            ExpiresText.Text = "N/A";
        }

        // Format parameters as JSON
        try
        {
            var options = new JsonSerializerOptions
            {
                WriteIndented = true
            };
            ParametersText.Text = JsonSerializer.Serialize(_request.Parameters, options);
        }
        catch
        {
            ParametersText.Text = "(Unable to display parameters)";
        }
    }

    private void ApproveButton_Click(object sender, RoutedEventArgs e)
    {
        var result = new ApprovalResult
        {
            RequestId = _request.RequestId,
            IsApproved = true,
            DecidedBy = Environment.UserName,
            Reason = DecisionReasonInput.Text,
            DecidedAt = DateTime.Now
        };

        _resultTcs.TrySetResult(result);
        Close();
    }

    private void DenyButton_Click(object sender, RoutedEventArgs e)
    {
        var result = new ApprovalResult
        {
            RequestId = _request.RequestId,
            IsApproved = false,
            DecidedBy = Environment.UserName,
            Reason = DecisionReasonInput.Text,
            DecidedAt = DateTime.Now
        };

        _resultTcs.TrySetResult(result);
        Close();
    }
}
