using System;
using System.Collections.Generic;
using System.Globalization;
using System.Reflection;
using Microsoft.UI.Xaml;
using Microsoft.UI.Xaml.Data;
using Microsoft.UI.Xaml.Media;
using Windows.UI;

namespace VoiceStudio.App.Converters
{
  /// <summary>
  /// Converter to convert a color string to a SolidColorBrush.
  /// Supports hex formats: #RGB, #ARGB, #RRGGBB, #AARRGGBB (prefix # optional).
  /// Also supports named colors matching Microsoft.UI.Colors (e.g., "Red").
  /// </summary>
  public sealed class StringToBrushConverter : IValueConverter
  {
    private readonly Dictionary<string, SolidColorBrush> _cache = new(StringComparer.OrdinalIgnoreCase);
    private static readonly Dictionary<string, Color> _namedColors = new(StringComparer.OrdinalIgnoreCase);

    public Brush? FallbackBrush { get; set; }

    public object Convert(object value, Type targetType, object parameter, string language)
    {
      if (value is not string input)
      {
        return ResolveFallbackBrush();
      }

      var key = input.Trim();
      if (key.Length == 0)
      {
        return ResolveFallbackBrush();
      }

      if (_cache.TryGetValue(key, out var cached))
      {
        return cached;
      }

      if (TryParseColorString(key, out var color))
      {
        var brush = new SolidColorBrush(color);
        _cache[key] = brush;
        return brush;
      }

      return ResolveFallbackBrush();
    }

    public object ConvertBack(object value, Type targetType, object parameter, string language)
    {
      throw new NotSupportedException();
    }

    private Brush ResolveFallbackBrush()
    {
      if (FallbackBrush != null)
      {
        return FallbackBrush;
      }

      try
      {
        var resources = Application.Current?.Resources;
        if (resources?.ContainsKey("VSQ.Accent.CyanBrush") == true && resources["VSQ.Accent.CyanBrush"] is Brush b)
        {
          return b;
        }
      }
      catch
      {
      }

      return new SolidColorBrush(Microsoft.UI.Colors.Transparent);
    }

    private static bool TryParseColorString(string input, out Color color)
    {
      if (TryGetNamedColor(input, out color))
      {
        return true;
      }

      var s = input;
      if (s.StartsWith("#", StringComparison.Ordinal))
      {
        s = s.Substring(1);
      }
      else if (s.StartsWith("0x", StringComparison.OrdinalIgnoreCase))
      {
        s = s.Substring(2);
      }

      if (s.Length == 3)
      {
        // RGB
        if (TryParseHexNibble(s[0], out var r) &&
            TryParseHexNibble(s[1], out var g) &&
            TryParseHexNibble(s[2], out var b))
        {
          color = Color.FromArgb(255, (byte)(r * 17), (byte)(g * 17), (byte)(b * 17));
          return true;
        }
      }
      else if (s.Length == 4)
      {
        // ARGB
        if (TryParseHexNibble(s[0], out var a) &&
            TryParseHexNibble(s[1], out var r) &&
            TryParseHexNibble(s[2], out var g) &&
            TryParseHexNibble(s[3], out var b))
        {
          color = Color.FromArgb((byte)(a * 17), (byte)(r * 17), (byte)(g * 17), (byte)(b * 17));
          return true;
        }
      }
      else if (s.Length == 6)
      {
        // RRGGBB
        if (TryParseHexByte(s, 0, out var r) &&
            TryParseHexByte(s, 2, out var g) &&
            TryParseHexByte(s, 4, out var b))
        {
          color = Color.FromArgb(255, r, g, b);
          return true;
        }
      }
      else if (s.Length == 8)
      {
        // AARRGGBB
        if (TryParseHexByte(s, 0, out var a) &&
            TryParseHexByte(s, 2, out var r) &&
            TryParseHexByte(s, 4, out var g) &&
            TryParseHexByte(s, 6, out var b))
        {
          color = Color.FromArgb(a, r, g, b);
          return true;
        }
      }

      color = default;
      return false;
    }

    private static bool TryGetNamedColor(string input, out Color color)
    {
      if (_namedColors.TryGetValue(input, out color))
      {
        return true;
      }

      try
      {
        var prop = typeof(Microsoft.UI.Colors).GetProperty(
            input,
            BindingFlags.Public | BindingFlags.Static | BindingFlags.IgnoreCase);

        if (prop != null && prop.PropertyType == typeof(Color) && prop.GetValue(null) is Color c)
        {
          _namedColors[input] = c;
          color = c;
          return true;
        }
      }
      catch
      {
      }

      color = default;
      return false;
    }

    private static bool TryParseHexByte(string s, int startIndex, out byte value)
    {
      if (startIndex < 0 || startIndex + 2 > s.Length)
      {
        value = 0;
        return false;
      }

      return byte.TryParse(
          s.Substring(startIndex, 2),
          NumberStyles.HexNumber,
          CultureInfo.InvariantCulture,
          out value);
    }

    private static bool TryParseHexNibble(char c, out int value)
    {
      if (c >= '0' && c <= '9')
      {
        value = c - '0';
        return true;
      }

      if (c >= 'a' && c <= 'f')
      {
        value = c - 'a' + 10;
        return true;
      }

      if (c >= 'A' && c <= 'F')
      {
        value = c - 'A' + 10;
        return true;
      }

      value = 0;
      return false;
    }
  }
}