using Microsoft.UI.Xaml;
using Microsoft.UI.Xaml.Data;
using System;

namespace VoiceStudio.App.Converters
{
  /// <summary>
  /// Converts a value to Visibility: Visible when non-null (and non-empty for strings), Collapsed otherwise.
  /// Can be inverted by setting ConverterParameter="Invert" (Visible when null, Collapsed when not null).
  /// </summary>
  public sealed class NullToVisibilityConverter : IValueConverter
  {
    public object? Convert(object value, Type targetType, object parameter, string language)
    {
      var isNullLike = value == null || (value is string s && string.IsNullOrWhiteSpace(s));
      var invert = parameter is string p && p.Equals("Invert", StringComparison.OrdinalIgnoreCase);

      var visible = invert ? isNullLike : !isNullLike;
      return visible ? Visibility.Visible : Visibility.Collapsed;
    }

    public object? ConvertBack(object value, Type targetType, object parameter, string language)
    {
      throw new NotSupportedException();
    }
  }
}