using System;
using System.Globalization;
using System.Text.Json;
using System.Text.Json.Serialization;

namespace VoiceStudio.App.Utilities
{
  /// <summary>
  /// JSON converter for ISO 8601 datetime strings.
  /// Handles both "Z" suffix and "+00:00" timezone formats.
  /// </summary>
  /// <remarks>
  /// This converter is designed to parse datetime strings from the Python backend,
  /// which uses ISO 8601 format with UTC timezone.
  /// 
  /// Supported formats:
  /// - "2024-01-15T10:30:00Z"
  /// - "2024-01-15T10:30:00.123456Z"
  /// - "2024-01-15T10:30:00+00:00"
  /// - "2024-01-15T10:30:00.123456+00:00"
  /// </remarks>
  public class Iso8601DateTimeConverter : JsonConverter<DateTimeOffset>
  {
    private static readonly string[] Formats = new[]
    {
      "yyyy-MM-ddTHH:mm:ssZ",
      "yyyy-MM-ddTHH:mm:ss.FFFFFFFZ",
      "yyyy-MM-ddTHH:mm:sszzz",
      "yyyy-MM-ddTHH:mm:ss.FFFFFFFzzz",
      "yyyy-MM-ddTHH:mm:ss",
      "yyyy-MM-ddTHH:mm:ss.FFFFFFF",
    };

    public override DateTimeOffset Read(ref Utf8JsonReader reader, Type typeToConvert, JsonSerializerOptions options)
    {
      var value = reader.GetString();

      if (string.IsNullOrEmpty(value))
      {
        return default;
      }

      // Handle Z suffix
      if (value.EndsWith("Z", StringComparison.OrdinalIgnoreCase))
      {
        value = value.Substring(0, value.Length - 1) + "+00:00";
      }

      // Try parsing with exact formats first
      if (DateTimeOffset.TryParseExact(
        value,
        Formats,
        CultureInfo.InvariantCulture,
        DateTimeStyles.AssumeUniversal | DateTimeStyles.AllowWhiteSpaces,
        out var result))
      {
        return result;
      }

      // Fall back to general parsing
      if (DateTimeOffset.TryParse(value, CultureInfo.InvariantCulture, DateTimeStyles.AssumeUniversal, out result))
      {
        return result;
      }

      throw new JsonException($"Unable to parse datetime: {value}");
    }

    public override void Write(Utf8JsonWriter writer, DateTimeOffset value, JsonSerializerOptions options)
    {
      // Write in ISO 8601 format with Z suffix for UTC
      var utcValue = value.ToUniversalTime();
      writer.WriteStringValue(utcValue.ToString("yyyy-MM-ddTHH:mm:ss.FFFFFFFZ", CultureInfo.InvariantCulture));
    }
  }

  /// <summary>
  /// JSON converter for nullable ISO 8601 datetime strings.
  /// </summary>
  public class Iso8601NullableDateTimeConverter : JsonConverter<DateTimeOffset?>
  {
    private readonly Iso8601DateTimeConverter _innerConverter = new();

    public override DateTimeOffset? Read(ref Utf8JsonReader reader, Type typeToConvert, JsonSerializerOptions options)
    {
      if (reader.TokenType == JsonTokenType.Null)
      {
        return null;
      }

      return _innerConverter.Read(ref reader, typeof(DateTimeOffset), options);
    }

    public override void Write(Utf8JsonWriter writer, DateTimeOffset? value, JsonSerializerOptions options)
    {
      if (value == null)
      {
        writer.WriteNullValue();
        return;
      }

      _innerConverter.Write(writer, value.Value, options);
    }
  }

  /// <summary>
  /// JSON converter for DateTime (non-offset) ISO 8601 strings.
  /// </summary>
  public class Iso8601DateTimeNonOffsetConverter : JsonConverter<DateTime>
  {
    public override DateTime Read(ref Utf8JsonReader reader, Type typeToConvert, JsonSerializerOptions options)
    {
      var value = reader.GetString();

      if (string.IsNullOrEmpty(value))
      {
        return default;
      }

      // Handle Z suffix
      if (value.EndsWith("Z", StringComparison.OrdinalIgnoreCase))
      {
        value = value.Substring(0, value.Length - 1);
      }
      else if (value.Contains("+"))
      {
        // Strip timezone offset
        var plusIndex = value.LastIndexOf('+');
        if (plusIndex > 0)
        {
          value = value.Substring(0, plusIndex);
        }
      }

      if (DateTime.TryParse(value, CultureInfo.InvariantCulture, DateTimeStyles.AssumeUniversal, out var result))
      {
        return DateTime.SpecifyKind(result, DateTimeKind.Utc);
      }

      throw new JsonException($"Unable to parse datetime: {value}");
    }

    public override void Write(Utf8JsonWriter writer, DateTime value, JsonSerializerOptions options)
    {
      var utcValue = value.Kind == DateTimeKind.Utc ? value : value.ToUniversalTime();
      writer.WriteStringValue(utcValue.ToString("yyyy-MM-ddTHH:mm:ss.FFFFFFFZ", CultureInfo.InvariantCulture));
    }
  }
}
