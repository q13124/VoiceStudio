using System;

namespace VoiceStudio.Core.Models
{
    /// <summary>
    /// Information about a backup.
    /// </summary>
    public class BackupInfo
    {
        public string Id { get; set; } = string.Empty;
        public string Name { get; set; } = string.Empty;
        public string Created { get; set; } = string.Empty; // ISO datetime string
        public long SizeBytes { get; set; }
        public bool IncludesProfiles { get; set; }
        public bool IncludesProjects { get; set; }
        public bool IncludesSettings { get; set; }
        public bool IncludesModels { get; set; }
        public string? Description { get; set; }
    }

    /// <summary>
    /// Request to create a backup.
    /// </summary>
    public class BackupCreateRequest
    {
        public string Name { get; set; } = string.Empty;
        public bool IncludesProfiles { get; set; } = true;
        public bool IncludesProjects { get; set; } = true;
        public bool IncludesSettings { get; set; } = true;
        public bool IncludesModels { get; set; } = false;
        public string? Description { get; set; }
    }

    /// <summary>
    /// Request to restore from a backup.
    /// </summary>
    public class RestoreRequest
    {
        public string BackupId { get; set; } = string.Empty;
        public bool RestoreProfiles { get; set; } = true;
        public bool RestoreProjects { get; set; } = true;
        public bool RestoreSettings { get; set; } = true;
        public bool RestoreModels { get; set; } = false;
    }

    /// <summary>
    /// Response from restore operation.
    /// </summary>
    public class RestoreResponse
    {
        public bool Success { get; set; }
        public string Message { get; set; } = string.Empty;
    }
}

