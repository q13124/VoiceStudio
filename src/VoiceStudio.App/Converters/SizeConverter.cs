using Microsoft.UI.Xaml.Data;
using System;

namespace VoiceStudio.App.Converters
{
  /// <summary>
  /// Converts file size in bytes to human-readable format (B, KB, MB, GB).
  /// </summary>
  public class SizeConverter : IValueConverter
  {
    public object? Convert(object value, Type targetType, object parameter, string language)
    {
      if (value is long bytes)
      {
        if (bytes < 1024)
          return $"{bytes} B";
        if (bytes < 1024 * 1024)
          return $"{bytes / 1024.0:F2} KB";
        if (bytes < 1024 * 1024 * 1024)
          return $"{bytes / (1024.0 * 1024.0):F2} MB";
        return $"{bytes / (1024.0 * 1024.0 * 1024.0):F2} GB";
      }
      return value?.ToString() ?? "0 B";
    }

    public object? ConvertBack(object value, Type targetType, object parameter, string language)
    {
      throw new NotSupportedException();
    }
  }
}