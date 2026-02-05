using System.Collections.Generic;

namespace VoiceStudio.App.Services
{
  /// <summary>
  /// Result of an API version compatibility check.
  /// </summary>
  public class ApiVersionCheckResult
  {
    /// <summary>
    /// Whether the client is compatible with the server API.
    /// </summary>
    public bool IsCompatible { get; set; }

    /// <summary>
    /// The server's current API version.
    /// </summary>
    public string ServerVersion { get; set; } = "unknown";

    /// <summary>
    /// The client's expected API version.
    /// </summary>
    public string ClientVersion { get; set; } = "unknown";

    /// <summary>
    /// List of API versions supported by the server.
    /// </summary>
    public List<string> SupportedVersions { get; set; } = new();

    /// <summary>
    /// Human-readable message about the compatibility status.
    /// </summary>
    public string Message { get; set; } = "";

    /// <summary>
    /// Recommendation for the client (e.g., "Upgrade to v2").
    /// </summary>
    public string? Recommendation { get; set; }

    /// <summary>
    /// Error message if the check failed.
    /// </summary>
    public string? Error { get; set; }
  }

  /// <summary>
  /// API version information from the server.
  /// </summary>
  public class ApiVersionInfo
  {
    /// <summary>
    /// The current (latest) API version.
    /// </summary>
    public string CurrentVersion { get; set; } = "unknown";

    /// <summary>
    /// The default API version for unversioned requests.
    /// </summary>
    public string DefaultVersion { get; set; } = "unknown";

    /// <summary>
    /// List of all supported API versions.
    /// </summary>
    public List<string> SupportedVersions { get; set; } = new();
  }
}
