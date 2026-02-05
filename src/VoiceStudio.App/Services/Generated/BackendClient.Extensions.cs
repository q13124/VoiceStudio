using VoiceStudio.App.Utilities;

namespace VoiceStudio.App.Services.Generated
{
  /// <summary>
  /// Partial class extensions for the NSwag-generated BackendClient.
  /// Provides snake_case JSON serialization to match the Python backend's conventions.
  /// </summary>
  public partial class GeneratedBackendClient
  {
    /// <summary>
    /// Configures JSON serializer settings for the generated client.
    /// This method is called by NSwag's CreateSerializerSettings.
    /// </summary>
    /// <remarks>
    /// The Python backend uses snake_case for all JSON properties and ISO 8601 datetimes.
    /// This method ensures the C# client serializes/deserializes using the same convention.
    /// </remarks>
    static partial void UpdateJsonSerializerSettings(System.Text.Json.JsonSerializerOptions settings)
    {
      // Use snake_case to match Python backend conventions
      settings.PropertyNamingPolicy = SnakeCaseJsonNamingPolicy.Instance;

      // Case-insensitive property matching for robustness
      settings.PropertyNameCaseInsensitive = true;

      // Handle enum values as strings
      settings.Converters.Add(new System.Text.Json.Serialization.JsonStringEnumConverter());

      // Handle ISO 8601 datetime format (with Z suffix)
      settings.Converters.Add(new Iso8601DateTimeConverter());
      settings.Converters.Add(new Iso8601NullableDateTimeConverter());

      // Allow reading numbers from strings (Python sometimes serializes as strings)
      settings.NumberHandling = System.Text.Json.Serialization.JsonNumberHandling.AllowReadingFromString;
    }
  }
}
