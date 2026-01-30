using System;
using System.Collections.Generic;

namespace VoiceStudio.Core.Models
{
    /// <summary>
    /// Complete project data for serialization and persistence.
    /// Contains full project state including tracks, profiles, settings, and history.
    /// </summary>
    /// <remarks>
    /// Used by ProjectStore.MapDataToProject for full project hydration.
    /// Serialized to disk for project save/load (VS-0004, VS-0015).
    /// </remarks>
    public class ProjectData
    {
        /// <summary>
        /// Unique project identifier (GUID).
        /// </summary>
        public string Id { get; set; } = string.Empty;

        /// <summary>
        /// Project name.
        /// </summary>
        public string Name { get; set; } = string.Empty;

        /// <summary>
        /// Optional description.
        /// </summary>
        public string? Description { get; set; }

        /// <summary>
        /// Creation timestamp.
        /// </summary>
        public DateTime Created { get; set; }

        /// <summary>
        /// Last modification timestamp.
        /// </summary>
        public DateTime Modified { get; set; }

        /// <summary>
        /// Audio tracks in project.
        /// Serialized as list of track IDs or full track objects.
        /// </summary>
        public List<object>? Tracks { get; set; }

        /// <summary>
        /// Voice profile IDs used in project.
        /// </summary>
        public List<string>? ProfileIds { get; set; }

        /// <summary>
        /// Project-level settings (mixer config, export settings, etc.).
        /// </summary>
        public Dictionary<string, object>? Settings { get; set; }

        /// <summary>
        /// Additional metadata (custom fields, plugin data).
        /// </summary>
        public Dictionary<string, object>? Metadata { get; set; }

        /// <summary>
        /// Project author/creator.
        /// </summary>
        public string? Author { get; set; }

        /// <summary>
        /// Project format version for migration compatibility.
        /// </summary>
        public string? Version { get; set; }
    }
}
