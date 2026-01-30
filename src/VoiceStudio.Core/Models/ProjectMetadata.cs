using System;
using System.Collections.Generic;

namespace VoiceStudio.Core.Models
{
    /// <summary>
    /// Lightweight project metadata for list/index views.
    /// Contains summary information without loading full project data.
    /// </summary>
    /// <remarks>
    /// Used by ProjectStore.MapMetadataToProject for efficient project listing.
    /// Persistence layer (VS-0004) serializes this for project index files.
    /// </remarks>
    public class ProjectMetadata
    {
        /// <summary>
        /// Unique project identifier (GUID).
        /// </summary>
        public string Id { get; set; } = string.Empty;

        /// <summary>
        /// User-visible project name.
        /// </summary>
        public string Name { get; set; } = string.Empty;

        /// <summary>
        /// Optional project description.
        /// </summary>
        public string? Description { get; set; }

        /// <summary>
        /// Project creation timestamp.
        /// </summary>
        public DateTime Created { get; set; }

        /// <summary>
        /// Last modification timestamp.
        /// </summary>
        public DateTime Modified { get; set; }

        /// <summary>
        /// Optional thumbnail image path (relative to project root).
        /// </summary>
        public string? ThumbnailPath { get; set; }

        /// <summary>
        /// Project size in bytes (for storage metrics).
        /// </summary>
        public long SizeBytes { get; set; }

        /// <summary>
        /// Number of audio tracks in project.
        /// </summary>
        public int TrackCount { get; set; }

        /// <summary>
        /// Number of voice profiles associated with project.
        /// </summary>
        public int ProfileCount { get; set; }

        /// <summary>
        /// User-defined tags for categorization.
        /// </summary>
        public List<string>? Tags { get; set; }
    }
}
