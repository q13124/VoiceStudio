using System;
using System.Collections.Generic;

namespace VoiceStudio.Core.Models
{
    /// <summary>
    /// Represents a backend job with progress and status details.
    /// </summary>
    public class Job
    {
        public string Id { get; set; } = string.Empty;
        public string Name { get; set; } = string.Empty;
        public string Type { get; set; } = string.Empty;
        public string Status { get; set; } = string.Empty;
        public double Progress { get; set; }
        public string? CurrentStep { get; set; }
        public int? CurrentStepIndex { get; set; }
        public int? TotalSteps { get; set; }
        public string Created { get; set; } = string.Empty;
        public string? Started { get; set; }
        public string? Completed { get; set; }
        public string? EstimatedTimeRemaining { get; set; }
        public string? ErrorMessage { get; set; }
        public string? ResultId { get; set; }
        public Dictionary<string, object>? Metadata { get; set; }
    }
}
