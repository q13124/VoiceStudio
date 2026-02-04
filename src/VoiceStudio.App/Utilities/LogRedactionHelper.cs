using System;
using System.Collections.Generic;
using System.Text.RegularExpressions;

namespace VoiceStudio.App.Utilities
{
  /// <summary>
  /// Helper for redacting sensitive data from log messages.
  /// </summary>
  public static class LogRedactionHelper
  {
    // Simple patterns; extend as needed
    private static readonly List<Regex> SensitivePatterns = new()
        {
            new Regex(@"(?i)(api[_-]?key|token|secret)\s*[:=]\s*([A-Za-z0-9-_]+)", RegexOptions.Compiled),
            new Regex(@"(?i)(password|passwd)\s*[:=]\s*([^\s]+)", RegexOptions.Compiled),
            new Regex(@"\b\d{3}[- ]?\d{2}[- ]?\d{4}\b", RegexOptions.Compiled), // SSN-like
            new Regex(@"\b\d{16}\b", RegexOptions.Compiled) // card-like
        };

    /// <summary>
    /// Redacts sensitive data in a message.
    /// </summary>
    public static string Redact(string? message)
    {
      if (string.IsNullOrEmpty(message))
        return message ?? string.Empty;

      var redacted = message;
      foreach (var regex in SensitivePatterns)
      {
        redacted = regex.Replace(redacted, "[REDACTED]");
      }
      return redacted;
    }

    /// <summary>
    /// Redacts values in a metadata dictionary.
    /// </summary>
    public static Dictionary<string, object>? RedactMetadata(Dictionary<string, object>? metadata)
    {
      if (metadata == null)
        return null;

      var result = new Dictionary<string, object>();
      foreach (var kvp in metadata)
      {
        if (kvp.Value is string s)
        {
          result[kvp.Key] = Redact(s);
        }
        else
        {
          result[kvp.Key] = kvp.Value;
        }
      }
      return result;
    }
  }
}