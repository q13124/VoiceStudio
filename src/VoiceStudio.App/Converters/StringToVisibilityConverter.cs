using System;
using Microsoft.UI.Xaml;
using Microsoft.UI.Xaml.Data;

namespace VoiceStudio.App.Converters;

/// <summary>
/// Converts a string to Visibility (Visible when non-empty).
/// </summary>
public sealed class StringToVisibilityConverter : IValueConverter
{
  public object Convert(object value, Type targetType, object parameter, string language)
  {
    return value is string s && !string.IsNullOrWhiteSpace(s)
        ? Visibility.Visible
        : Visibility.Collapsed;
  }

  public object ConvertBack(object value, Type targetType, object parameter, string language)
  {
    // One-way converter
    return string.Empty;
  }
}