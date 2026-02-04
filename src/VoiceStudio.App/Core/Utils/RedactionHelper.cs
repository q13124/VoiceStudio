using System;
using System.Collections.Generic;
using System.Text;
using System.Text.RegularExpressions;

namespace VoiceStudio.Core.Utils
{
  /// <summary>
  /// PII and Secret Redaction Helper
  /// Redacts PII and secrets from logs and test data.
  /// </summary>
  public static class RedactionHelper
  {
    private static readonly List<(Regex Pattern, string Replacement)> PiiPatterns = new()
        {
            (new Regex(@"\b\d{3}-\d{2}-\d{4}\b"), "[SSN]"), // SSN
            (new Regex(@"\b\d{3}\.\d{2}\.\d{4}\b"), "[SSN]"), // SSN with dots
            (new Regex(@"\b\d{16}\b"), "[CARD]"), // Credit card
            (new Regex(@"\b\d{4}[\s-]?\d{4}[\s-]?\d{4}[\s-]?\d{4}\b"), "[CARD]"), // Credit card with spaces/dashes
            (new Regex(@"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b"), "[EMAIL]"), // Email
            (new Regex(@"\b\d{3}-\d{3}-\d{4}\b"), "[PHONE]"), // Phone
            (new Regex(@"\b\(\d{3}\)\s?\d{3}-\d{4}\b"), "[PHONE]"), // Phone with parentheses
        };

    private static readonly List<(Regex Pattern, string Replacement)> SecretPatterns = new()
        {
            (new Regex(@"password[""']?\s*[:=]\s*[""']?([^""'\s]+)", RegexOptions.IgnoreCase), "password\"\": \"\"[REDACTED]"),
            (new Regex(@"api[_-]?key[""']?\s*[:=]\s*[""']?([^""'\s]+)", RegexOptions.IgnoreCase), "api_key\"\": \"\"[REDACTED]"),
            (new Regex(@"secret[""']?\s*[:=]\s*[""']?([^""'\s]+)", RegexOptions.IgnoreCase), "secret\"\": \"\"[REDACTED]"),
            (new Regex(@"token[""']?\s*[:=]\s*[""']?([^""'\s]+)", RegexOptions.IgnoreCase), "token\"\": \"\"[REDACTED]"),
            (new Regex(@"authorization[""']?\s*[:=]\s*[""']?([^""'\s]+)", RegexOptions.IgnoreCase), "authorization\"\": \"\"[REDACTED]"),
            (new Regex(@"bearer\s+([A-Za-z0-9._-]+)", RegexOptions.IgnoreCase), "bearer [REDACTED]"),
            (new Regex(@"aws[_-]?access[_-]?key[_-]?id[""']?\s*[:=]\s*[""']?([^""'\s]+)", RegexOptions.IgnoreCase), "aws_access_key_id\"\": \"\"[REDACTED]"),
            (new Regex(@"aws[_-]?secret[_-]?access[_-]?key[""']?\s*[:=]\s*[""']?([^""'\s]+)", RegexOptions.IgnoreCase), "aws_secret_access_key\"\": \"\"[REDACTED]"),
        };

    private static readonly HashSet<string> DefaultKeysToRedact = new(StringComparer.OrdinalIgnoreCase)
        {
            "password", "api_key", "secret", "token", "authorization", "access_key", "secret_key"
        };

    /// <summary>
    /// Redact PII and secrets from text.
    /// </summary>
    public static string RedactText(string text, bool redactPii = true, bool redactSecrets = true)
    {
      if (string.IsNullOrEmpty(text))
        return text;

      var result = text;

      // Redact PII
      if (redactPii)
      {
        foreach (var (pattern, replacement) in PiiPatterns)
        {
          result = pattern.Replace(result, replacement);
        }
      }

      // Redact secrets
      if (redactSecrets)
      {
        foreach (var (pattern, replacement) in SecretPatterns)
        {
          result = pattern.Replace(result, replacement);
        }
      }

      return result;
    }

    /// <summary>
    /// Redact PII and secrets from dictionary.
    /// </summary>
    public static Dictionary<string, object?> RedactDictionary(
        Dictionary<string, object?> data,
        HashSet<string>? keysToRedact = null,
        bool redactPii = true,
        bool redactSecrets = true)
    {
      if (data == null)
        return new Dictionary<string, object?>();

      keysToRedact ??= DefaultKeysToRedact;
      var result = new Dictionary<string, object?>();

      foreach (var kvp in data)
      {
        // Always redact specific keys
        if (keysToRedact.Contains(kvp.Key))
        {
          result[kvp.Key] = "[REDACTED]";
        }
        else if (kvp.Value is string strValue)
        {
          result[kvp.Key] = RedactText(strValue, redactPii, redactSecrets);
        }
        else if (kvp.Value is Dictionary<string, object?> dictValue)
        {
          result[kvp.Key] = RedactDictionary(dictValue, keysToRedact, redactPii, redactSecrets);
        }
        else if (kvp.Value is IEnumerable<object> listValue)
        {
          var redactedList = new List<object?>();
          foreach (var item in listValue)
          {
            if (item is string strItem)
            {
              redactedList.Add(RedactText(strItem, redactPii, redactSecrets));
            }
            else if (item is Dictionary<string, object?> dictItem)
            {
              redactedList.Add(RedactDictionary(dictItem, keysToRedact, redactPii, redactSecrets));
            }
            else
            {
              redactedList.Add(item);
            }
          }
          result[kvp.Key] = redactedList;
        }
        else
        {
          result[kvp.Key] = kvp.Value;
        }
      }

      return result;
    }

    /// <summary>
    /// Redact PII and secrets from data.
    /// </summary>
    public static T Redact<T>(T data, HashSet<string>? keysToRedact = null, bool redactPii = true, bool redactSecrets = true)
    {
      if (data == null)
        return data!;

      if (data is string str)
      {
        return (T)(object)RedactText(str, redactPii, redactSecrets);
      }

      if (data is Dictionary<string, object?> dict)
      {
        return (T)(object)RedactDictionary(dict, keysToRedact, redactPii, redactSecrets);
      }

      // For other types, return as-is
      return data;
    }
  }
}