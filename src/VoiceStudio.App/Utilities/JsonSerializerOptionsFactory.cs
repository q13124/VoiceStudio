using System.Text.Json;
using System.Text.Json.Serialization;

namespace VoiceStudio.App.Utilities
{
  /// <summary>
  /// Factory for creating consistent JSON serialization options throughout the application.
  /// </summary>
  /// <remarks>
  /// This factory provides standardized options for:
  /// - Backend API communication (snake_case)
  /// - Local file storage (camelCase or snake_case)
  /// - Human-readable exports (indented formatting)
  /// </remarks>
  public static class JsonSerializerOptionsFactory
  {
    /// <summary>
    /// Options for communicating with the Python backend API.
    /// Uses snake_case property naming to match the backend convention.
    /// </summary>
    public static JsonSerializerOptions BackendApi => _backendApiOptions.Value;

    /// <summary>
    /// Options for local file storage and configuration.
    /// Uses camelCase for compatibility with common JSON conventions.
    /// </summary>
    public static JsonSerializerOptions LocalStorage => _localStorageOptions.Value;

    /// <summary>
    /// Options for human-readable exports (indented, snake_case).
    /// </summary>
    public static JsonSerializerOptions Export => _exportOptions.Value;

    /// <summary>
    /// Options for internal use (e.g., crash reports, diagnostics).
    /// Uses indented format for readability.
    /// </summary>
    public static JsonSerializerOptions Diagnostics => _diagnosticsOptions.Value;

    private static readonly System.Lazy<JsonSerializerOptions> _backendApiOptions = new(() =>
    {
      return new JsonSerializerOptions
      {
        PropertyNamingPolicy = SnakeCaseJsonNamingPolicy.Instance,
        PropertyNameCaseInsensitive = true,
        DefaultIgnoreCondition = JsonIgnoreCondition.WhenWritingNull,
        Converters =
        {
          new JsonStringEnumConverter(),
          new Iso8601DateTimeConverter(),
          new Iso8601NullableDateTimeConverter(),
        },
        NumberHandling = JsonNumberHandling.AllowReadingFromString,
      };
    });

    private static readonly System.Lazy<JsonSerializerOptions> _localStorageOptions = new(() =>
    {
      return new JsonSerializerOptions
      {
        PropertyNamingPolicy = JsonNamingPolicy.CamelCase,
        PropertyNameCaseInsensitive = true,
        WriteIndented = true,
        DefaultIgnoreCondition = JsonIgnoreCondition.WhenWritingNull,
        Converters = { new JsonStringEnumConverter() },
      };
    });

    private static readonly System.Lazy<JsonSerializerOptions> _exportOptions = new(() =>
    {
      return new JsonSerializerOptions
      {
        PropertyNamingPolicy = SnakeCaseJsonNamingPolicy.Instance,
        PropertyNameCaseInsensitive = true,
        WriteIndented = true,
        DefaultIgnoreCondition = JsonIgnoreCondition.WhenWritingNull,
        Converters = { new JsonStringEnumConverter() },
      };
    });

    private static readonly System.Lazy<JsonSerializerOptions> _diagnosticsOptions = new(() =>
    {
      return new JsonSerializerOptions
      {
        PropertyNamingPolicy = JsonNamingPolicy.CamelCase,
        WriteIndented = true,
        DefaultIgnoreCondition = JsonIgnoreCondition.Never,
        Converters = { new JsonStringEnumConverter() },
      };
    });

    /// <summary>
    /// Creates a copy of the specified options with WriteIndented set.
    /// Useful for one-off pretty-printed outputs.
    /// </summary>
    public static JsonSerializerOptions WithIndented(JsonSerializerOptions baseOptions, bool indented = true)
    {
      var copy = new JsonSerializerOptions(baseOptions)
      {
        WriteIndented = indented,
      };
      return copy;
    }
  }
}
