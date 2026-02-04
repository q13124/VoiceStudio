using System;
using System.Globalization;
using Microsoft.UI.Xaml.Data;
using VoiceStudio.App.Logging;

namespace VoiceStudio.App.Converters
{
  /// <summary>
  /// Converts a string (typically a name) to its initials.
  /// Takes the first letter of each word, up to 2 letters.
  /// </summary>
  public class InitialsConverter : IValueConverter
  {
    public object Convert(object value, Type targetType, object parameter, string language)
    {
      try
      {
        if (value is string name && !string.IsNullOrWhiteSpace(name))
        {
          var words = name.Trim().Split(new[] { ' ', '\t', '\n', '\r' }, StringSplitOptions.RemoveEmptyEntries);
          if (words.Length > 0)
          {
            if (words.Length == 1)
            {
              // Single word: take first letter (uppercase)
              if (words[0].Length > 0)
              {
                return words[0].Substring(0, Math.Min(1, words[0].Length)).ToUpperInvariant();
              }
            }
            else
            {
              // Multiple words: take first letter of first two words
              var first = words[0].Length > 0 ? words[0][0].ToString().ToUpperInvariant() : "";
              var second = words.Length > 1 && words[1].Length > 0 ? words[1][0].ToString().ToUpperInvariant() : "";
              return first + second;
            }
          }
        }
      }
      catch (Exception ex)
      {
        ErrorLogger.LogWarning($"Best effort operation failed: {ex.Message}", "InitialsConverter.Convert");
      }
      return "?";
    }

    public object ConvertBack(object value, Type targetType, object parameter, string language)
    {
      throw new NotSupportedException();
    }
  }
}