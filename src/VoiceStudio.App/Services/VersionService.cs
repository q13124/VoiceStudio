using System;
using System.Diagnostics;
using System.Reflection;
using Windows.ApplicationModel;

namespace VoiceStudio.App.Services
{
  /// <summary>
  /// Service for retrieving application version information.
  /// </summary>
  public class VersionService
  {
    private static string? _version;
    private static string? _buildDate;

    /// <summary>
    /// Gets the application version (e.g., "1.0.0").
    /// </summary>
    public static string Version
    {
      get
      {
        if (_version == null)
        {
          try
          {
            // Try to get version from Package (MSIX)
            var package = Package.Current;
            var version = package.Id.Version;
            _version = $"{version.Major}.{version.Minor}.{version.Build}.{version.Revision}";
          }
          catch
          {
            // Fallback to assembly version
            var assembly = Assembly.GetExecutingAssembly();
            var version = assembly.GetName().Version;
            _version = version != null
                ? $"{version.Major}.{version.Minor}.{version.Build}"
                : "1.0.0";
          }
        }
        return _version;
      }
    }

    /// <summary>
    /// Gets the build date as a string.
    /// </summary>
    public static string BuildDate
    {
      get
      {
        if (_buildDate == null)
        {
          try
          {
            var assembly = Assembly.GetExecutingAssembly();
            var fileInfo = new System.IO.FileInfo(assembly.Location);
            _buildDate = fileInfo.LastWriteTime.ToString("yyyy-MM-dd");
          }
          catch
          {
            _buildDate = DateTime.Now.ToString("yyyy-MM-dd");
          }
        }
        return _buildDate;
      }
    }

    /// <summary>
    /// Gets the full version string including build date.
    /// </summary>
    public static string FullVersion => $"{Version} (Build {BuildDate})";

    /// <summary>
    /// Gets the application name.
    /// </summary>
    public static string ApplicationName => "VoiceStudio Quantum+";

    /// <summary>
    /// Gets copyright information.
    /// </summary>
    public static string Copyright
    {
      get
      {
        try
        {
          var assembly = Assembly.GetExecutingAssembly();
          var attribute = assembly.GetCustomAttribute<AssemblyCopyrightAttribute>();
          return attribute?.Copyright ?? "© 2025 VoiceStudio";
        }
        catch
        {
          return "© 2025 VoiceStudio";
        }
      }
    }

    /// <summary>
    /// Gets the .NET runtime version.
    /// </summary>
    public static string RuntimeVersion => Environment.Version.ToString();

    /// <summary>
    /// Gets the OS version.
    /// </summary>
    public static string OSVersion
    {
      get
      {
        try
        {
          var version = Environment.OSVersion;
          return $"{version.VersionString} ({version.Platform})";
        }
        catch
        {
          return "Unknown";
        }
      }
    }
  }
}
