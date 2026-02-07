using System;
using Microsoft.UI.Xaml.Data;
using Microsoft.UI.Xaml.Media.Imaging;

namespace VoiceStudio.App.Converters
{
  /// <summary>
  /// Converter to convert a URL or file path string to a BitmapImage for display.
  /// Returns null if the string is null, empty, or cannot be converted, allowing
  /// controls like PersonPicture to fall back to their default behavior (initials).
  /// </summary>
  public sealed class StringToImageSourceConverter : IValueConverter
  {
    public object? Convert(object value, Type targetType, object parameter, string language)
    {
      if (value is not string path || string.IsNullOrWhiteSpace(path))
      {
        return null;
      }

      try
      {
        // Support both file paths and URIs
        Uri uri;
        if (path.StartsWith("http://", StringComparison.OrdinalIgnoreCase) ||
            path.StartsWith("https://", StringComparison.OrdinalIgnoreCase) ||
            path.StartsWith("ms-appx://", StringComparison.OrdinalIgnoreCase) ||
            path.StartsWith("ms-appdata://", StringComparison.OrdinalIgnoreCase))
        {
          uri = new Uri(path);
        }
        else if (System.IO.Path.IsPathRooted(path))
        {
          // Local file path
          uri = new Uri(path);
        }
        else
        {
          // Relative path - treat as ms-appx resource
          uri = new Uri($"ms-appx:///{path.TrimStart('/')}");
        }

        return new BitmapImage(uri)
        {
          DecodePixelWidth = 80,  // 2x the display size for crisp rendering
          DecodePixelHeight = 80
        };
      }
      catch (Exception)
      {
        // ALLOWED: Return null to let the control use its fallback (initials)
        return null;
      }
    }

    public object ConvertBack(object value, Type targetType, object parameter, string language)
    {
      throw new NotSupportedException("StringToImageSourceConverter does not support ConvertBack.");
    }
  }
}
